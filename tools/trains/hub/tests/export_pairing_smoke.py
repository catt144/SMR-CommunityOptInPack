"""34b: archived FindTask/FindSupplyRequest shells with a deterministic C double.

Proves Lua filtering and engine-call arguments, not C matching or live throughput.
"""
import hashlib
import subprocess
import sys

from distribution_smoke import ROOT, runtime


def matcher(lua):
    path = ROOT.parent / 'SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/Lua/_TaskRequest.lua'
    source = path.read_text(encoding='utf8')
    print('source:', path, 'sha256:', hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
    lua.execute(r'''
const.rfSupply=8; const.rfDemand=16; const.rfWaitToFill=32
const.rfSpecialSupplyPairing=64; const.rfSpecialDemandPairing=128
ResourceUnits={Metals=5000}; original_calls=0; retry_calls=0
agent={unreachable_buildings={}}
controller=setmetatable({supply_queues={}, demand_queues={}, priority_queue={},
    under_construction={}, restrictor_tables={}}, {__index=TaskRequestHub})
function Request_FindTask(pq,sq,dq,construction,restrictors,units,unreachable,flags,a)
    assert(pq==controller.priority_queue and sq==controller.supply_queues)
    assert(dq==controller.demand_queues and construction==controller.under_construction)
    assert(restrictors==controller.restrictor_tables and units==ResourceUnits)
    assert(a==agent and unreachable==agent.unreachable_buildings and flags==73)
    original_calls=original_calls+1
    return false, table.unpack(candidate,1,5)
end
function Request_FindSupply(a,queues,res,n,min_priority,ignore,required,exclude,unreachable,measure,max_dist)
    retry_calls=retry_calls+1
    assert(a==agent and queues==controller.supply_queues and res=='Metals' and n==candidate[4])
    assert(min_priority==nil and required==nil and measure==nil and max_dist==nil)
    assert(ignore==const.rfSpecialDemandPairing, 'special pairing compatibility')
    assert(exclude==candidate[1].source and unreachable==agent.unreachable_buildings)
    if alternative then return alternative, offered end
end
''')
    start = source.index('local Request_FindSupply_C =')
    end = source.index('--[[@@@', start)
    lua.execute(source[start:end])


def main():
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print('HEAD:', subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), flush=True)
    lua = runtime(matcher)
    lua.execute(r'''
local D=SMROptInTrainDistribution
local _,st,hub=fixture(0,0,120,480)
assert(D.Set(st,'Metals','export',50))
function req(source,n,want,flags)
    local r=request(n,want); r.source=source; r.flags=flags
    function r:GetSource(a) assert(a==agent) return self.source end
    function r:GetFlags() return self.flags end
    return r
end
local depot={class='StorageDepot',desired_amount=50000}
local supply=req(depot,52000,50000, const.rfSupply|const.rfStorageDepot)
local demand=st.demand.Metals
demand.source=st; demand.flags=const.rfDemand|const.rfStorageDepot|const.rfSpecialSupplyPairing
demand.GetSource=supply.GetSource; demand.GetFlags=supply.GetFlags
local function choose(s,d,n,res)
    candidate={s,d,res or 'Metals',n,0}
    return controller:FindTask(agent,73)
end
local function unchanged(s,d,n,res)
    local r,p,rres,take,prio=choose(s,d,n,res)
    assert(r==s and p==d and rres==(res or 'Metals') and take==n and prio==0)
end
-- Below/at floor: one excluded-source retry, then no assignment.
for _,n in ipairs({0,49000,50000}) do
    supply.actual=n; supply.target=n
    local retries=retry_calls
    assert(not choose(supply,demand,5000))
    assert(retry_calls==retries+1)
end
-- Partial surplus and existing bookings both limit the haul.
supply.actual=56000; supply.target=52000
local r,p,res,take,prio=choose(supply,demand,5000)
assert(r==supply and p==demand and take==2000 and prio==0)
assert(supply:AssignUnit(take))
assert(not choose(supply,demand,5000),'a second drone cannot book the same surplus')
assert(supply.actual==56000 and supply.target==50000)
-- Positive fractional excess is permitted unless a native wait-to-fill flag forbids it.
supply.actual=50900; supply.target=50900
assert(select(4,choose(supply,demand,5000))==900)
supply.flags=supply.flags|const.rfWaitToFill
assert(not choose(supply,demand,5000))
supply.flags=supply.flags&~const.rfWaitToFill
supply.actual=60000; supply.target=60000
unchanged(supply,demand,5000)
print('PASS storage floors, outstanding bookings, fractional excess, native wait guard')

-- Re-query can rescue the drone with another depot or a producer; never the rejected source.
supply.actual=50000; supply.target=50000
alternative=req({class='StorageDepot'},58000,50000,const.rfSupply|const.rfStorageDepot); offered=5000
r,p,res,take=choose(supply,demand,5000)
assert(r==alternative and p==demand and take==5000)
alternative.target=51500
assert(select(4,choose(supply,demand,5000))==1500)
alternative.target=50000
assert(not choose(supply,demand,5000))
alternative=supply
assert(not choose(supply,demand,5000))
alternative=req(st,120000,0,const.rfSupply|const.rfStorageDepot)
assert(not choose(supply,demand,5000),'supply finder cannot create a self-haul')
alternative.source=depot
assert(not choose(supply,demand,5000),'a second request on the excluded building is still excluded')
alternative.source={invalid=true}
assert(not choose(supply,demand,5000))
alternative=req({class='ProducerStockpile'},60000,60000,const.rfSupply); offered=4000
r,p,res,take=choose(supply,demand,5000)
assert(r==alternative and p==demand and take==4000)
alternative.target=0
assert(not choose(supply,demand,5000))
alternative.target=60000
demand.target=1000
assert(select(4,choose(supply,demand,5000))==1000)
demand.target=120000
alternative=nil
-- Repeated rejected matches have bounded work; the next unrelated vanilla result survives.
local before,retries=original_calls,retry_calls
for i=1,100 do assert(not choose(supply,demand,5000)) end
assert(original_calls-before==100 and retry_calls-retries==100)
local work=req({},10000,0,256)
unchanged(work,nil,5000,'repair')
print('PASS one excluded-source retry, substitute cap/assignability, repeated refusals, next work result')

-- Pass-throughs: no pair, producers, loose piles, other destinations, modes and reverse direction.
unchanged(nil,nil,nil)
local output=req({class='ProducerStockpile'},5000,5000,const.rfSupply)
unchanged(output,demand,5000)
local foreign=req({class='StorageDepot'},10000,0,const.rfDemand|const.rfStorageDepot)
unchanged(supply,foreign,5000)
for _,mode in ipairs({'import','balanced'}) do
    assert(D.Set(st,'Metals',mode,40)); unchanged(supply,demand,5000)
end
assert(D.Set(st,'Metals','export',50))
st:SetAcceptResourceState('Metals','disabled'); unchanged(supply,demand,5000)
st:SetAcceptResourceState('Metals','store')
local station_supply=req(st,10000,120000,const.rfSupply|const.rfStorageDepot)
unchanged(station_supply,foreign,5000)
-- Hubless module gating, hub-owned rows, save-time pass-through and inherited controllers.
hub.hub=false; D.Refresh()
assert(D.Set(st,'Metals','export',50))
SMROptInPack={IsActive=function() return false end}
unchanged(supply,demand,5000)
SMROptInPack.IsActive=function(id) return id=='StationRows' end
assert(not choose(supply,demand,5000))
SMROptInPack.IsActive=function(id) return id=='TrainHub' end
assert(not choose(supply,demand,5000))
hub.hub=true; D.Refresh(); SMROptInPack.IsActive=function() return false end
assert(not choose(supply,demand,5000))
OnMsg.SaveGameStart(); unchanged(supply,demand,5000); OnMsg.SaveGameDone()
assert(not choose(supply,demand,5000))
local DroneHub={FindTask=TaskRequestHub.FindTask,FindSupplyRequest=TaskRequestHub.FindSupplyRequest}
setmetatable(controller,{__index=DroneHub})
assert(not choose(supply,demand,5000))
assert(st.demand.Metals:GetDesiredAmount()==0 and st.supply.Metals:GetDesiredAmount()==120000)
assert(D.ExportPairingStats.capped>0 and D.ExportPairingStats.substituted>0 and D.ExportPairingStats.refused>0)
print('PASS work/producer/reverse/foreign/mode gates, hubless toggles, hub ownership, save, flattening')
''')


if __name__ == '__main__':
    main()
