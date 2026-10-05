"""Brief 30: native train bodies with request doubles, without a hub class.

Desk smoke only: no engine request, save serialization, drone or pixel claim.
"""
import subprocess
import sys

from distribution_smoke import ROOT, ARCHIVE, runtime


def main():
    print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print("HEAD:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), flush=True)
    # The existing harness pins 405907. Check its consumed files against the
    # installed build's archived tree before inheriting those native bodies.
    current = ARCHIVE.parents[2] / "1.1.1.406343/Src/Lua"
    for name in ["Units/Train.lua", "Buildings/Station.lua",
                 "Buildings/MultiResourceDepot.lua", "Buildings/MultiResourceCubeVisuals.lua"]:
        assert (ARCHIVE / name).read_bytes() == (current / name).read_bytes(), name
    print("PASS native-body archive parity: 1.1.1.405907 -> 1.1.1.406343", flush=True)
    lua = runtime()
    lua.execute(r'''
local D, F = SMROptInTrainDistribution, SMROptInTrainFloor
-- The engine permits #nil; match the existing native-departure harness.
debug.setmetatable(nil, {__len=function() return 0 end})
assert(SMROptInTrainHubBase == nil)
function plain_fixture(a, b, cap)
    local t, s, other = fixture(a, b, cap, cap)
    other.hub = false
    other.GetTrainExportFloor, other.HubTrackGraph, other.nodes = nil, nil, nil
    D.Refresh()
    assert(not D.HubFor(s) and not D.HubFor(other))
    return t, s, other
end
local t, s, other = plain_fixture(80, 0, 100)
assert(D.Set(s, 'Metals', 'export', 20))
assert(D.Set(other, 'Metals', 'import', 50))
checked_transfer(t)
assert(stock(s)==30000 and t.stockpiled_amount.Metals==50000)
deliver(t, other); checked_transfer(t)
assert(stock(other)==50000 and t.stockpiled_amount.Metals==0)
t.current_station=s; checked_transfer(t)
assert(stock(s)==30000 and t.stockpiled_amount.Metals==0)
assert(s.transport_policy.Metals==nil and other.transport_policy.Metals==nil)
assert(s.supply.Metals.desired==100000 and s.demand.Metals.desired==0 and other.supply.Metals.desired==0)
assert(rawget(s,D.LOCAL_FIELD).Metals.percent==20 and rawget(s,D.FIELD)==nil)
assert(D.Status(other,'Metals').hub==nil)
print('PASS no hub implementation: native export floor, import cap/refusal, drone baselines, separate saved row')

-- A real incoming reservation reduces the order; the floor must survive
-- transfer and all temporary claims must return, leaving that reservation.
t,s,other=plain_fixture(80,0,100)
assert(D.Set(s,'Metals','export',20)); assert(D.Set(other,'Metals','balanced',80))
assert(other.demand.Metals:AssignUnit(10000))
checked_transfer(t)
assert(stock(s)==20000 and t.stockpiled_amount.Metals==60000)
deliver(t,other)
assert(stock(other)==60000 and other.demand.Metals.target==30000)
assert(s.supply.Metals.target==stock(s))
assert(other.supply.Metals.target==stock(other))
print('PASS Balanced pin, real reservation preserved, exact export floor and transient release')

-- Owner 2026-10-05: an untouched hubless row keeps the game's balancing (an
-- even split between equal stations, whatever the dial says), with no view.
t,s,other=plain_fixture(80,0,100)
local calls=D.calls
checked_transfer(t); deliver(t,other)
assert(stock(s)==40000 and stock(other)==40000 and not D.Get(other,'Metals'))
assert(D.calls==calls,'an untouched line must take the native path')
-- The reporter's line: a drone-fed source sitting at its 10-unit dial, untouched,
-- and an Import at the other end. The source shares as the game would.
t,s,other=plain_fixture(10,0,100)
assert(D.Set(other,'Metals','import',50))
checked_transfer(t); deliver(t,other)
assert(stock(s)==5000 and stock(other)==5000)
t.current_station=other; checked_transfer(t)
assert(stock(other)==5000 and t.stockpiled_amount.Metals==0,'an Import never becomes a source')
-- A set Balanced pin sends its surplus to an untouched neighbour, up to that
-- neighbour's share, and the neighbour does not send it back.
t,s,other=plain_fixture(80,0,100)
assert(D.Set(s,'Metals','balanced',50))
checked_transfer(t); deliver(t,other)
assert(stock(s)==50000 and stock(other)==30000)
t.current_station=other; checked_transfer(t)
assert(stock(other)==30000 and t.stockpiled_amount.Metals==0)
-- A depot line keeps the dial pin on an untouched row.
t,s,other=plain_fixture(80,0,100)
SMRElevatorDepot={IsDepot=function(o) return o==other end, HubEntry=function() end}
checked_transfer(t); deliver(t,other)
assert(stock(s)==10000 and stock(other)==70000)
SMRElevatorDepot=nil
-- A hub elsewhere on the map does not own a line it has no track to: remote
-- untouched stations still take the native path.
t,s,other=plain_fixture(80,0,100)
local far=station(0,400,true); far.handle=43; far.city=s.city; far.nodes={[far]=true}
-- the fixture's colony label is the line's own member list; give the hub a list of its own
local line_label=UIColony.labels.Station
UIColony.labels.Station={s,other,far}
D.Refresh()
assert(not D.HubFor(s) and not D.HubFor(other))
calls=D.calls
checked_transfer(t); deliver(t,other)
assert(stock(s)==40000 and stock(other)==40000 and D.calls==calls)
UIColony.labels.Station=line_label; D.Refresh()
print('PASS untouched hubless rows: native balance, share against a set row, depot line pinned')
-- The first slider edit selects a percent that follows capacity changes and
-- native request rewrites.
t,s,other=plain_fixture(80,0,100)
assert(D.Set(s,'Metals','export',20)); assert(D.Set(s,'Food','balanced',35))
local function baselines(cap)
    assert(s.supply.Metals.desired==cap and s.demand.Metals.desired==0,'Export retains vanilla send baseline; pairing filter enforces source floor (34b)')
    assert(s.supply.Food.desired==cap*35//100)
end
s:SetDesiredAmount(3000); baselines(100000)
s:SetAcceptResourceState('Metals','disabled')
s:SetAcceptResourceState('Metals','store'); baselines(100000)
s:UpdateRequestCapacity('Food'); baselines(100000)
s.max_storage_per_resource=200000; s:OnModifiableValueChanged('max_storage_per_resource'); baselines(200000)
s.supply.Food=nil; s.demand.Food=nil; s:RecalculateAfterResourceListChange(); baselines(200000)
SavegameFixups.RevertStationDesiredAmount(); baselines(200000)
print('PASS edited percentage, native rewrite paths and replacement requests')

-- Save snapshot is vanilla even with the mod removed: no custom policy,
-- no standing claims, and native desired values instead of our runtime baseline.
OnMsg.SaveGameStart()
for _,res in ipairs({'Metals','Food'}) do
    assert(s.supply[res].desired==s.desired_amount)
    assert(s.demand[res].desired==s:GetMaxStorage(res)-s.desired_amount)
    assert(s.supply[res].target==s.supply[res].actual)
    assert(s.transport_policy[res]==nil)
end
assert(rawget(s,D.LOCAL_FIELD).Metals.mode=='export')
OnMsg.SaveGameDone(); baselines(200000)
OnMsg.LoadGame(); baselines(200000)
print('PASS simulated save snapshot: native baseline and no claims/policy; save-done/load restore rows')

-- Independent settings on the seam. Resources present only in the old set
-- must not keep its baseline; an untouched hub row retains the old hub default.
local hub=station(0,400,true); hub.handle=42; hub.city=s.city; hub.nodes={[s]=true,[hub]=true}
table.insert(UIColony.labels.Station,hub)
D.Refresh(); D.Apply(s)
assert(D.HubFor(s)==hub and not D.Get(s,'Metals'))
assert(s.supply.Metals.desired==s.desired_amount and s.supply.Food.desired==s.desired_amount)
assert(D.Set(s,'Metals','import',70))
assert(s.supply.Metals.desired==0 and rawget(s,D.LOCAL_FIELD).Metals.percent==20)
hub.nodes[s]=nil; D.Refresh(); D.Apply(s); baselines(200000)
assert(D.Get(s,'Metals').mode=='export')
hub.nodes[s]=true; D.Refresh(); D.Apply(s)
assert(D.Get(s,'Metals').percent==70 and s.supply.Food.desired==s.desired_amount)
hub.nodes[s]=nil; D.Refresh(); D.Apply(s)
D.Reset(s,'Metals'); assert(not D.Get(s,'Metals') and s.supply.Metals.desired==s.desired_amount)
assert(D.Get(s,'Food').percent==35)
print('PASS hub join/leave/rejoin isolates settings, clears stale baselines, and resets individual rows')

-- Late cargo honors a reduced cap and the entire assignment stays aboard;
-- an accepting native endpoint can receive it with vanilla's own unload.
t,s,other=plain_fixture(10,0,100)
t.stockpiled_amount.Metals=30000; t.assigned_resources[s]={Metals=30000}
assert(s.demand.Metals:AssignUnit(30000)); assert(D.Set(s,'Metals','import',20))
t:UnloadAll()
assert(stock(s)==10000 and t.stockpiled_amount.Metals==30000)
assert(D.Set(other,'Metals','import',50)); deliver(t,other)
assert(stock(other)==30000 and t.stockpiled_amount.Metals==0)
assert(s.demand.Metals.target==s.demand.Metals.actual)
-- Empty importer must visit a supplier; a satisfied line must stay quiet.
t,s,other=plain_fixture(0,80,100)
assert(D.Set(s,'Metals','import',50)); assert(D.Set(other,'Metals','export',20))
local work,stop=t:TransferCargo(nil,false)
assert(work and stop==other)
t.current_station=other; checked_transfer(t); deliver(t,s)
assert(stock(s)==50000)
local _,stop=t:TransferCargo(nil,false); assert(not stop)
assert(not D.error and not F.stats.last_error)
print('PASS old cargo cap, native reassignment, empty pickup and satisfied-line stop')

-- The live underground fixture's other endpoint is a depot, which owns its
-- own rows. Its native storage can exchange with the ordinary station without
-- calling HubEntry, migrating settings, or adding a station-row field to it.
t,s,other=plain_fixture(80,0,100)
SMRElevatorDepot={IsDepot=function(o) return o==other end,
    HubEntry=function() error('hubless loading must not consume depot hub settings') end}
assert(D.Set(s,'Metals','export',20)); checked_transfer(t); deliver(t,other)
assert(stock(s)==20000 and stock(other)==60000 and not rawget(other,D.LOCAL_FIELD))
assert(D.Set(s,'Metals','import',50)); checked_transfer(t); deliver(t,s)
assert(stock(s)==50000 and stock(other)==30000)
assert(other.transport_policy.Metals==nil)
SMRElevatorDepot=nil
-- Disabled remains vanilla-removable stock, including when it was an Import.
assert(D.Set(s,'Metals','import',100)); s:SetAcceptResourceState('Metals','disabled')
assert(D.Set(other,'Metals','import',100)); checked_transfer(t); deliver(t,other)
assert(stock(s)==0 and not s:IsResourceEnabled('Metals'))
print('PASS native depot endpoint without hub settings, and disabled-resource drain')
''')
    print("NOT RUN: native engine/save removal, drone scheduling and attended UI", flush=True)


if __name__ == "__main__":
    main()
