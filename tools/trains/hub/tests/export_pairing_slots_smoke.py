"""Desk-check the 34b slot witness with real distribution code and matcher shells."""
import subprocess
import sys

from distribution_smoke import ROOT, runtime
from export_pairing_smoke import matcher


def main():
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print('HEAD:', subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), flush=True)
    lua = runtime(matcher)
    lua.execute(r'''
SMRTK={slots={},triggers={},error_count=0,armed={}}
function SMRTK.PreloadProbeSweep(e) SMRTK.sweep=e end
function SMRTK.Bind(n,label,fn,opts) SMRTK.slots[n]=fn end
function SMRTK.Trigger(t) SMRTK.triggers[t.id]=t end
guim=1000; FoodResources={Metals=true}; GetTimeFactor=function() return 0 end
g_Classes.TaskRequestHub=TaskRequestHub
ctx={state={},mark=function() return 1 end,log=function() end}
local _,st,hub=fixture(0,0,120,480)
test_station=st
assert(SMROptInTrainDistribution.Set(st,'Metals','export',50))
function make_request(source,actual,want,flags)
    local r=request(actual,want); r.source=source; r.flags=flags
    function r:GetSource(a) assert(a==agent) return self.source end
    function r:GetFlags() return self.flags end
    return r
end
test_supply=make_request({class='StorageDepot'},52000,50000,const.rfSupply|const.rfStorageDepot)
test_demand=st.demand.Metals
test_demand.source=st; test_demand.flags=const.rfDemand|const.rfStorageDepot|const.rfSpecialSupplyPairing
test_demand.GetSource=test_supply.GetSource; test_demand.GetFlags=test_supply.GetFlags
''')
    path = ROOT/'tools/trains/hub/tests/80_AgentSlots_34b.lua.txt'
    lua.execute(path.read_text(encoding='utf8'))
    lua.execute(r'''
local T=SMRTK
assert(T.slots[2](ctx).witness=='on')
candidate={test_supply,test_demand,'Metals',5000,0}
assert(select(4,controller:FindTask(agent,73))==2000)
local read=T.slots[8](ctx)
assert(read.pairings==1 and read.export_from_storage==1 and read.export_below_floor==0 and read.filter_capped==1)
test_supply.target=50000
assert(not controller:FindTask(agent,73))
read=T.slots[8](ctx)
assert(read.calls==2 and read.pairings==1 and read.filter_retried==1 and read.filter_refused==1)
-- A below-floor storage haul to an ordinary consumer is allowed and must not fail Export.
local ordinary=make_request({class='StorageDepot'},50000,0,const.rfDemand|const.rfStorageDepot)
candidate={test_supply,ordinary,'Metals',5000,0}
controller:FindTask(agent,73)
read=T.slots[8](ctx)
assert(read.food_storage_pairings==2 and read.export_below_floor==0)
local producer=make_request({class='Stockpile'},5000,5000,const.rfSupply)
candidate={producer,test_demand,'Metals',5000,0}; controller:FindTask(agent,73)
read=T.slots[8](ctx); assert(read.export_from_producer==1)
local station_supply=make_request(test_station,10000,120000,const.rfSupply|const.rfStorageDepot)
candidate={station_supply,ordinary,'Metals',5000,0}; controller:FindTask(agent,73)
read=T.slots[8](ctx)
assert(read.refill_from_export==1 and read.refill_above_desired==0 and read.export_below_floor==0)
ordinary.target=1000
controller:FindTask(agent,73)
read=T.slots[8](ctx); assert(read.refill_above_desired==1)
-- Falsifier: a runtime carrier returning an unsafe pair must increment the violation counter.
g_Classes.UnfilteredHub={__ancestors={TaskRequestHub=true},FindTask=function() return table.unpack(candidate,1,5) end}
T.slots[2](ctx); T.slots[2](ctx)
candidate={test_supply,test_demand,'Metals',5000,0}
g_Classes.UnfilteredHub:FindTask(agent,73)
read=T.slots[8](ctx); assert(read.export_below_floor==1)
OnMsg.LoadGame()
g_Classes.UnfilteredHub:FindTask(agent,73)
assert(T.slots[8](ctx).calls==read.calls,'load disarms witness')
assert(T.slots[2](ctx).witness=='on')
assert(T.slots[8](ctx).pairings==0,'re-arm starts fresh counters')
print('PASS witness scope, reservation-aware floor, producer/refill counts, unsafe-pair falsifier, load/re-arm')
''')


if __name__ == '__main__':
    main()
