"""Independent adversarial review of the archived proposal; no shipping edits."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools/trains/hub/tests'))
import distribution_smoke as h

print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
print('HEAD:', subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(), flush=True)
prototype = ROOT / 'docs/archive/station_rows_proposal_20261021/StationRows_40_TrainDistribution.proposal.lua'
print('prototype sha256:', hashlib.sha256(prototype.read_bytes()).hexdigest(), flush=True)
for name in ['Units/Train.lua','Buildings/Station.lua','Buildings/MultiResourceDepot.lua','Buildings/MultiResourceCubeVisuals.lua']:
    assert (h.ARCHIVE / name).read_bytes() == (h.ARCHIVE.parents[2] / '1.1.1.406343/Src/Lua' / name).read_bytes(), name
work = ROOT / 'scratch/station_rows_second_review_mod'
(work / 'Code').mkdir(parents=True, exist_ok=True)
shutil.copyfile(ROOT / 'Code/StationRows_10_TrainFloor.lua', work / 'Code/StationRows_10_TrainFloor.lua')
shutil.copyfile(prototype, work / 'Code/StationRows_40_TrainDistribution.lua')
h.MOD = work
lua = h.runtime()
lua.execute(r'''
debug.setmetatable(nil, {__len=function() return 0 end})
local D=SMROptInTrainDistribution
function network(stocks,caps,edges)
    SMRElevatorDepot=nil; SMROptInPack=nil
    local nodes,tracks,trains={},{},{}
    local city={train_track_routes={},labels={Station=nodes}}
    for i,n in ipairs(stocks) do
        nodes[i]=station(n,caps[i]); nodes[i].handle=i; nodes[i].city=city; nodes[i].working=true
    end
    UIColony={labels=city.labels}
    for i,edge in ipairs(edges) do
        local members={}; for _,idx in ipairs(edge) do members[#members+1]=nodes[idx] end
        local track={members=members,trains={},city=city}
        function track:GetDestStation(st) return members[1]==st and members[2] or members[1] end
        city.train_track_routes[track]=members
        local t=setmetatable({current_station=members[1],track=track,city=city,
            stockpiled_amount={},assigned_resources={},units={},is_stopping=false},{__index=Train})
        function t:GetEmptyStorage() local n=0; for _,v in pairs(self.stockpiled_amount) do n=n+v end; return 42000-n end
        function t:AddResource(n,r) self.stockpiled_amount[r]=(self.stockpiled_amount[r] or 0)+n end
        function t:LogCargo() end
        function t:PushDestructor() end
        function t:PopDestructor() end
        track.trains={t}; tracks[i]=track; trains[i]=t
    end
    D.Refresh()
    return nodes,tracks,trains,city
end
local function units(st) return stock(st)/1000 end
local function move(t,src,dst) t.current_station=src; checked_transfer(t); deliver(t,dst) end

-- An empty Export leaf has no receiving weight in the prose contract.
local ns,ts,vs=network({60,0,0},{60,60,60},{{1,2,3}})
assert(D.Set(ns[3],'Metals','export',100))
move(vs[1],ns[1],ns[2])
assert(stock(ns[1])==40000 and stock(ns[2])==20000 and stock(ns[3])==0)
print('COUNTEREXAMPLE empty Export100 leaf: untouched source='..units(ns[1])..' untouched receiver='..units(ns[2])..' exporter='..units(ns[3])..'; zero-weight contract would deliver 30')

-- A satisfied Import consumes weight even though it contributes no releasable stock and orders zero.
ns,ts,vs=network({60,0,60},{60,60,60},{{1,2,3}})
assert(D.Set(ns[1],'Metals','export',0)); assert(D.Set(ns[3],'Metals','import',100))
move(vs[1],ns[1],ns[2]); move(vs[1],ns[1],ns[2])
assert(stock(ns[1])==30000 and stock(ns[2])==30000 and stock(ns[3])==60000)
print('COUNTEREXAMPLE satisfied Import100: Export0 source='..units(ns[1])..' untouched receiver='..units(ns[2])..' full Import='..units(ns[3])..'; second trip transfers zero despite receiver room')

-- Native unloading admits both loose and assigned old cargo above a depot Import cap.
for _,assigned in ipairs({false,true}) do
    ns,ts,vs=network({0,0},{250,60},{{1,2}})
    local depot,other,t=ns[1],ns[2],vs[1]
    SMROptInPack={IsActive=function() return false end}
    SMRElevatorDepot={IsDepot=function(o) return o==depot end,
        HubEntry=function(o) if o==depot then return {mode='import',percent=4} end end}
    depot.transport_policy.Metals='send'; depot.desired_amount=false; depot:SetDesiredAmount(10000)
    t.stockpiled_amount.Metals=42000
    if assigned then t.assigned_resources[depot]={Metals=42000}; assert(depot.demand.Metals:AssignUnit(42000)) end
    t:UnloadAll()
    assert(stock(depot)==42000 and t.stockpiled_amount.Metals==0)
    print('COUNTEREXAMPLE depot Import4 target10 native unload assigned='..tostring(assigned)..' received='..units(depot))
end

-- Two distinct lines book one shared station before either arrives.
ns,ts,vs=network({60,0,60},{60,60,60},{{1,2},{3,2}})
assert(D.Set(ns[2],'Metals','balanced',20))
checked_transfer(vs[1]); checked_transfer(vs[2])
local reserved=ns[2].demand.Metals.actual-ns[2].demand.Metals.target
assert(reserved<=60000 and reserved==36000)
deliver(vs[2],ns[2]); deliver(vs[1],ns[2])
assert(stock(ns[2])==36000 and ns[2].demand.Metals.target==24000)
assert(stock(ns[1])+stock(ns[2])+stock(ns[3])==120000)
print('PASS competing lines: reserved='..(reserved/1000)..' delivered='..units(ns[2])..'; no overfill or lost reservation')

-- All train cargo contributes, not just the currently loading train.
ns,ts,vs=network({60,0},{60,60},{{1,2}})
assert(D.Set(ns[2],'Metals','import',100))
local other={stockpiled_amount={Metals=20000},assigned_resources={[ns[2]]={Metals=20000}}}
ts[1].trains[#ts[1].trains+1]=other; assert(ns[2].demand.Metals:AssignUnit(20000))
checked_transfer(vs[1])
assert(vs[1].stockpiled_amount.Metals==20000 and ns[2].demand.Metals.target==20000)
print('PASS other train cargo: 20 already inbound; current load=20; receiver free unreserved=20')

-- Aliases, duplicate route members, and rebuild invalidation.
ns,ts,vs,city=network({0,0,0,0},{60,60,60,60},{{1,2},{1,3},{1,4}})
assert(D.IsJunction(ns[1]) and not D.IsJunction(ns[2]))
city.train_track_routes[{}]=ts[1].members
ts[1].members[#ts[1].members+1]=ns[2]
OnMsg.TrainRoutesRebuilt(); assert(not D.IsJunction(ns[2]))
city.train_track_routes[ts[2]]=nil; city.train_track_routes[ts[3]]=nil
OnMsg.TrainRoutesRebuilt(); assert(not D.IsJunction(ns[1]))
print('PASS route identity: three routes, aliases, repeated member and rebuild invalidation')

-- Disabled source drains through the proposal view; a missing destination request gets no booking.
ns,ts,vs=network({30,0},{60,60},{{1,2}})
assert(D.Set(ns[2],'Metals','import',100)); ns[1]:SetAcceptResourceState('Metals','disabled')
move(vs[1],ns[1],ns[2]); assert(stock(ns[1])==0 and stock(ns[2])==30000)
ns,ts,vs=network({30,0},{60,60},{{1,2}})
assert(D.Set(ns[1],'Metals','export',0)); ns[2].demand.Metals=nil
checked_transfer(vs[1]); assert((vs[1].stockpiled_amount.Metals or 0)==0)
print('PASS disabled source drained; missing destination demand booked nothing')

-- Empty line / no inventory does not divide by zero or manufacture cargo.
ns,ts,vs=network({0,0},{60,60},{{1,2}})
assert(D.Set(ns[1],'Metals','export',0)); assert(D.Set(ns[2],'Metals','import',100))
local work,stop=vs[1]:TransferCargo(nil,false)
assert(not stop and (vs[1].stockpiled_amount.Metals or 0)==0)
print('PASS empty stock line: no cargo and no pickup stop')

-- Consecutive junctions with source replenishment and consumer drainage, no forced new stock mid-line.
ns,ts,vs=network({60,0,0,0},{60,60,60,60},{{1,2},{2,3},{3,4}})
assert(D.Set(ns[2],'Metals','balanced',20)); assert(D.Set(ns[3],'Metals','balanced',20))
local received,total_added=0,0
local arrivals={}
for round=1,12 do
    local add=60000-stock(ns[1]); ns[1]:AddResource(add,'Metals'); total_added=total_added+add
    for i=1,3 do move(vs[i],ns[i],ns[i+1]) end
    arrivals[round]=stock(ns[4]); received=received+arrivals[round]
    ns[4]:AddResource(-arrivals[round],'Metals')
end
assert(arrivals[12]>0 and received>0)
assert(stock(ns[1])+stock(ns[2])+stock(ns[3])+received==60000+total_added)
print('PASS consecutive junctions: total_received='..(received/1000)..' last_round='..(arrivals[12]/1000)..'; conservation reconciled against replenishment')

assert(not D.error and not SMROptInTrainFloor.stats.last_error)
''')
print('Review witnesses completed. COUNTEREXAMPLE lines are failures of proposal claims, not release passes.', flush=True)

# Exercise actual route-mode filtering as well as the actual transfer bodies.
route_path=h.ARCHIVE.parents[2] / '1.1.1.406343/Src/Lua/TrainTransport.lua'
route_source=route_path.read_text(encoding='utf-8')
print('native route source: 1.1.1.406343/Src/Lua/TrainTransport.lua sha256:', hashlib.sha256(route_path.read_bytes()).hexdigest(), flush=True)
start=route_source.index('function ForEachStationAlongTrack(')
end=route_source.index('\nfunction ', start+1)
lua.execute('const.trfPassengerTransport=4; const.trfRunnableOnly=8; table.clear=function(t) for k in pairs(t) do t[k]=nil end end')
lua.execute(route_source[start:end])
lua.execute(r'''
local D=SMROptInTrainDistribution
local function native_edges(ns,ts)
    for _,track in ipairs(ts) do
        track.elements_under_construction={}; track.transport_mode='all'
        function track:CanTrainsRun() return true end
        track.members.edges={{start=track.members[1],dest=track.members[2],tracks={track}}}
    end
end
local ns,ts,vs=network({0,60,0},{60,60,60},{{1,2},{2,3}})
native_edges(ns,ts); ts[2].transport_mode='people'
assert(D.Set(ns[2],'Metals','import',50)); assert(D.IsJunction(ns[2]))
vs[1].current_station=ns[2]; checked_transfer(vs[1]); deliver(vs[1],ns[1])
assert(stock(ns[1])==15000 and stock(ns[2])==45000)
vs[2].current_station=ns[2]; checked_transfer(vs[2]); assert((vs[2].stockpiled_amount.Metals or 0)==0)
print('DESIGN EDGE native route walk: Import50 returns 15 on cargo line when its only other line is people-only; people leg loads zero')

ns,ts,vs=network({0,60,0},{60,60,60},{{1,2},{2,3}})
native_edges(ns,ts); ts[2].elements_under_construction={true}
assert(D.Set(ns[2],'Metals','import',50)); assert(D.IsJunction(ns[2]))
vs[1].current_station=ns[2]; checked_transfer(vs[1]); deliver(vs[1],ns[1])
vs[2].current_station=ns[2]; checked_transfer(vs[2])
assert(stock(ns[1])==15000 and (vs[2].stockpiled_amount.Metals or 0)==0)
print('DESIGN EDGE native route walk: retained construction-route membership permits Import surplus to leave the working line; blocked leg loads zero')

-- A cycle plus a drained branch, using real route traversal and transfer with request doubles.
ns,ts,vs=network({60,0,0,0},{60,60,60,60},{{1,2},{2,3},{3,1},{3,4}})
native_edges(ns,ts)
assert(D.Set(ns[1],'Metals','export',0)); assert(D.Set(ns[2],'Metals','balanced',20)); assert(D.Set(ns[3],'Metals','balanced',20))
local received,added,last=0,0,0
for round=1,12 do
    local n=60000-stock(ns[1]); ns[1]:AddResource(n,'Metals'); added=added+n
    for i,track in ipairs(ts) do
        vs[i].current_station=track.members[1]; checked_transfer(vs[i]); deliver(vs[i],track.members[2])
    end
    last=stock(ns[4]); received=received+last; ns[4]:AddResource(-last,'Metals')
    for _,st in ipairs(ns) do assert(stock(st)>=0 and stock(st)<=60000) end
end
assert(last>0 and received>0)
local stored=0; for _,st in ipairs(ns) do stored=stored+stock(st) end
local carried=0; for _,t in ipairs(vs) do carried=carried+(t.stockpiled_amount.Metals or 0) end
assert(stored+carried+received==60000+added)
assert(not D.error and not SMROptInTrainFloor.stats.last_error)
print('PASS cycle with consumer: received='..(received/1000)..' last_round='..(last/1000)..'; conserved, capacities bounded')
''')
print('NOT RUN: actual route rebuilding, engine request scheduling, real depot cabin, saves, UI or player saves.', flush=True)
