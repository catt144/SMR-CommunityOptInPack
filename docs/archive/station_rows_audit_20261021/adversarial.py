"""Independent checks of shipping relay code. Run from repo root; no shipping writes.

Uses native bodies and request/window doubles from the existing harness, with
archived native route walking and connected-track iteration, plus new witnesses.
Debug upvalue access observes the unmodified local view; it is not a game claim.
"""
from pathlib import Path
import hashlib
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf8')

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools/trains/hub/tests'))
import distribution_smoke as h
import distribution_ui_smoke as ui

print('COMMAND:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), flush=True)
archive = ROOT.parent / 'SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/Lua'
for name in ['Units/Train.lua', 'Buildings/Station.lua', 'Buildings/MultiResourceDepot.lua', 'Buildings/MultiResourceCubeVisuals.lua']:
    assert (h.ARCHIVE / name).read_bytes() == (archive / name).read_bytes(), name
    print('PASS archived body parity 405907 -> 406343:', name, hashlib.sha256((archive/name).read_bytes()).hexdigest())

lua = h.runtime()
route = (archive/'TrainTransport.lua').read_text(encoding='utf8')
print('NATIVE route build 1.1.1.406343 SHA256:', hashlib.sha256((archive/'TrainTransport.lua').read_bytes()).hexdigest())
lua.execute('TrackConnectedObjBase={}; IsBeingDestructed=function() return false end; const.trfInclusive=1; const.trfPassengerTransport=2; const.trfBidirectional=4; const.trfRunnableOnly=8; table.clear=function(t) for k in pairs(t) do t[k]=nil end end')
for start, end in [('function TrackConnectedObjBase:ForEachConnectedTrack(', 'function TrackConnectedObjBase:OrientConnectorElements('), ('local stations_visited = false', 'function GetTrainsOnRoute(')]:
    lua.execute(route[route.index(start):route.index(end)])
lua.execute(r'''
debug.setmetatable(nil, {__len=function() return 0 end})
D=SMROptInTrainDistribution
function network(stocks,caps,edges)
    SMRElevatorDepot=nil; SMROptInPack=nil
    local nodes,tracks,trains={},{},{}
    local city={train_track_routes={},labels={Station=nodes}}
    for i,n in ipairs(stocks) do
        local s=station(n,caps[i]); nodes[i]=s; s.handle=i; s.city=city; s.working=true
        s.connectors={}; s.first_connector_idx=1; s.last_connector_idx=0
        s.ForEachConnectedTrack=TrackConnectedObjBase.ForEachConnectedTrack
        function s:GetConnectorElement(i) return self.connectors[i] end
    end
    UIColony={labels=city.labels}
    for i,edge in ipairs(edges) do
        local members={}; for _,idx in ipairs(edge) do members[#members+1]=nodes[idx] end
        local segments={}
        members.edges={}
        for j=1,#members-1 do
            local a,b=members[j],members[j+1]
            local seg={members=members,city=city,elements_under_construction={},transport_mode='all',assigned_vehicles={}}
            function seg:GetDestStation(s) return s==a and b or a end
            function seg:CanTrainsRun() return true end
            members.edges[#members.edges+1]={start=a,dest=b,tracks={seg}}
            city.train_track_routes[seg]=members; segments[#segments+1]=seg
            for _,s in ipairs({a,b}) do s.connectors[#s.connectors+1]={track_obj=seg}; s.last_connector_idx=#s.connectors end
        end
        local track=segments[1]
        local t=setmetatable({current_station=members[1],track=track,city=city,
            stockpiled_amount={},assigned_resources={},units={},is_stopping=false},{__index=Train})
        function t:GetEmptyStorage() local n=0; for _,v in pairs(self.stockpiled_amount) do n=n+v end; return 42000-n end
        function t:AddResource(n,r) self.stockpiled_amount[r]=(self.stockpiled_amount[r] or 0)+n end
        function t:LogCargo() end; function t:PushDestructor() end; function t:PopDestructor() end
        track.assigned_vehicles={t}; tracks[i]=track; trains[i]=t
    end
    D.Refresh()
    return nodes,tracks,trains,city
end
function move(t,src,dst) t.current_station=src; checked_transfer(t); deliver(t,dst) end
for i=1,30 do local k,v=debug.getupvalue(Train.TransferCargo,i); if k=='local_train_view' then local_view=v end end
assert(local_view)

-- Junction topology: actual connected-track method, native modes/construction/working filter.
local ns,ts,vs,city=network({0,60,0,0},{60,60,60,60},{{1,2},{2,3},{2,4}})
assert(D.IsJunction(ns[2]) and not D.IsJunction(ns[1]))
ts[2].transport_mode='people'; ts[3].elements_under_construction={true}
assert(D.IsJunction(ns[2]), 'cache retains old classification until invalidated')
D.Refresh(); assert(not D.IsJunction(ns[2]))
assert(D.Set(ns[2],'Metals','import',50)); move(vs[1],ns[2],ns[1]); assert(stock(ns[1])==0)
ts[3].elements_under_construction={}; OnMsg.TrainRoutesRebuilt(); assert(D.IsJunction(ns[2]))
ns[4].working=false; D.Refresh(); assert(not D.IsJunction(ns[2]))
ns[4].working=true; now=1001; GameTime=function() return now end; D.HubFor(ns[2]); assert(D.IsJunction(ns[2]))
print('PASS native junction: three routes; people/construction/nonworking exclusion; Refresh, rebuild and HubFor at 1001ms invalidate')
ns,ts,vs,city=network({0,0,0},{60,60,60},{{1,2,1},{1,3}})
ts[1].members.loop=true; assert(D.IsJunction(ns[1]) and not D.IsJunction(ns[2]))
city.train_track_routes[{}]=ts[1].members; ts[2].transport_mode='people'; D.Refresh()
assert(not D.IsJunction(ns[1]))
city.train_track_routes=false; D.Refresh(); assert(not D.IsJunction(ns[1]))
print('PASS native loop repeats/segment aliases count once; false route index returns false')

-- Cargo is counted once even when one train is indexed on two route segments.
ns,ts,vs=network({60,0,0},{60,60,60},{{1,2,3}})
assert(D.Set(ns[2],'Metals','import',100)); assert(D.Set(ns[3],'Metals','export',100))
local other={stockpiled_amount={Metals=20000},assigned_resources={[ns[2]]={Metals=20000}}}
ts[1].assigned_vehicles[#ts[1].assigned_vehicles+1]=other
ts[1].members.edges[2].tracks[1].assigned_vehicles={other}
assert(ns[2].demand.Metals:AssignUnit(20000))
local answers=local_view(vs[1],ts[1]); assert(answers[ns[2]].Metals.capacity==40000)
checked_transfer(vs[1]); local booked=vs[1].stockpiled_amount.Metals or 0
print('OBSERVE other train inbound20, source60, Import100: new booked='..booked..'; receiver total reserved='..(ns[2].demand.Metals.actual-ns[2].demand.Metals.target))
assert(booked==20000) -- native allocator shares further; view room is 40, not 20 or 60
assert(ns[2].demand.Metals.actual-ns[2].demand.Metals.target==40000)
print('PASS all-train pool/alias dedup/reservation: view40, native new booking20, total bookings40')

-- Competing incoming lines: reserve first, relay remainder; conservation at delivery.
ns,ts,vs=network({60,0,60},{60,60,60},{{1,2},{3,2}})
assert(D.Set(ns[2],'Metals','balanced',20))
checked_transfer(vs[1]); checked_transfer(vs[2])
local booked=ns[2].demand.Metals.actual-ns[2].demand.Metals.target
assert(booked<=60000)
deliver(vs[2],ns[2]); deliver(vs[1],ns[2])
assert(stock(ns[2])==booked and stock(ns[1])+stock(ns[2])+stock(ns[3])==120000)
print('PASS competing lines reserved/delivered='..booked..'; total stock=120000')

-- Sub-resource rounding: independent rounded shares need not add to the pool.
ns,ts,vs=network({60,0,0},{60,60,60},{{1,2,3}})
ts[1].members.edges[2].tracks[1].transport_mode='people'
assert(D.Set(ns[1],'Metals','export',0))
for i=1,3 do move(vs[1],ns[1],ns[2]) end
assert(stock(ns[1])==30000 and stock(ns[2])==30000 and stock(ns[3])==0)
print('COUNTEREXAMPLE people-only tail on same route: Export0 source60 -> cargo receiver0 -> people-only receiver0; after 3 trips stock=30000,30000,0; 30000 stranded despite cargo receiver room30000')
ts[1].members.edges[2].tracks[1].transport_mode='all'; D.Refresh()
move(vs[1],ns[1],ns[3]); assert(stock(ns[1])==0 and stock(ns[3])==30000)
print('CONTROL all-cargo tail: remaining30000 is booked and delivered, source reaches Export0')
ns,ts,vs=network({60,0,60},{60,60,60},{{1,2,3}})
ts[1].members.edges[2].tracks[1].transport_mode='people'
assert(D.Set(ns[2],'Metals','import',100))
move(vs[1],ns[1],ns[2]); assert(stock(ns[1])==40000 and stock(ns[2])==20000)
print('COUNTEREXAMPLE inaccessible stock: Default source60 -> Import100 empty -> people-only stock60; cargo load=20000 instead of the reachable pair share30000')

-- Sub-resource rounding: independent rounded shares need not add to the pool.
ns,ts,vs=network({0.002,0,0,0},{60,60,60,60},{{1,2,3,4}})
assert(D.Set(ns[4],'Metals','export',0))
local a,c=local_view(vs[1],ts[1]); local demands={}
for _,claim in ipairs(c) do for i=2,3 do if claim[1]==ns[i].demand.Metals then demands[i]=ns[i].demand.Metals.target-claim[2] end end end
assert(c[1][2]==1 and demands[2]==1 and demands[3]==1)
print('COUNTEREXAMPLE rounding: pool=2 internal units; source floor=1; orders=1+1; total allocation=3; handle sorting does not apportion remainder')
checked_transfer(vs[1]); assert(stock(ns[1])+(vs[1].stockpiled_amount.Metals or 0)==2)
print('LIMIT rounding witness: native transfer conserves physical cargo; 1 internal unit = 0.001 resource; not a duplication claim')

-- The deliberately retained whole-assignment rule can occupy an entire train.
ns,ts,vs=network({0,0},{60,250},{{1,2}})
local depot=ns[2]
SMRElevatorDepot={IsDepot=function(o) return o==depot end,
    HubEntry=function(o) if o==depot then return {mode='import',percent=4} end end}
assert(D.Set(ns[1],'Metals','export',0))
local t=vs[1]; t.stockpiled_amount.Metals=42000; t.assigned_resources[depot]={Metals=42000}
assert(depot.demand.Metals:AssignUnit(42000))
for i=1,3 do deliver(t,depot); deliver(t,ns[1]) end
assert(t.stockpiled_amount.Metals==42000 and stock(depot)==0 and stock(ns[1])==0)
print('OBSERVE ruled whole-assignment limit: old42000 assignment vs depot cap10000, Export0 other stop; 3 unload visit-pairs leave all42000 aboard; scheduling/cabin NOT RUN')
SMRElevatorDepot=nil

-- Continued relay under explicit service schedules, with capacity and conservation guards.
for _,cyclic in ipairs({false,true}) do
    local edges=cyclic and {{1,2},{2,3},{3,1},{3,4}} or {{1,2},{2,3},{3,4}}
    ns,ts,vs=network({60,0,0,0},{60,60,60,60},edges)
    assert(D.Set(ns[2],'Metals','balanced',20)); assert(D.Set(ns[3],'Metals','balanced',20))
    if cyclic then assert(D.Set(ns[1],'Metals','export',0)) end
    local got,added,last=0,0,0
    for round=1,12 do
        local n=60000-stock(ns[1]); ns[1]:AddResource(n,'Metals'); added=added+n
        for i,e in ipairs(edges) do move(vs[i],ns[e[1]],ns[e[2]]) end
        last=stock(ns[4]); got=got+last; ns[4]:AddResource(-last,'Metals')
        for _,s in ipairs(ns) do assert(stock(s)>=0 and stock(s)<=60000) end
    end
    local held=0; for _,s in ipairs(ns) do held=held+stock(s) end
    for _,t in ipairs(vs) do held=held+(t.stockpiled_amount.Metals or 0) end
    assert(last>0 and held+got==60000+added)
    print('PASS relay cyclic='..tostring(cyclic)..' received='..got..' last='..last..'; conservation/capacity hold')
end
assert(not D.error and not SMROptInTrainFloor.stats.last_error)
''')

# Independent rational oracle: saturated slots are sorted by room/weight, then
# solved by a continuous water level. It does not implement the production loop.
from fractions import Fraction
import random
rng = random.Random(20261021)
lua.execute(r'''
function allocation_case(capacities, room_percents, pool)
    local stocks,caps,edge={pool},{math.max(pool,1)},{1}
    for i=1,#capacities do stocks[i+1]=0; caps[i+1]=capacities[i]; edge[i+1]=i+1 end
    local ns,ts,vs=network(stocks,caps,{edge})
    assert(D.Set(ns[1],'Metals','export',0))
    for i=1,#capacities do assert(D.Set(ns[i+1],'Metals','import',room_percents[i])) end
    local iterations=0
    debug.sethook(function() iterations=iterations+1; assert(iterations<10000,'allocation instruction limit') end,'',1000)
    local answers,claims=local_view(vs[1],ts[1]); debug.sethook()
    local orders={}
    for i=2,#ns do
        for _,claim in ipairs(claims) do
            if claim[1]==ns[i].demand.Metals then orders[i-1]=ns[i].demand.Metals.target-claim[2] end
        end
    end
    return orders
end
''')
worst = Fraction(0)
max_sum_error = 0
samples = 1200
for _ in range(samples):
    n = rng.randrange(3, 9)
    caps = [rng.randrange(1, 101) for _ in range(n)]
    percents = [rng.choice([0, 1, 20, 50, 80, 99, 100]) for _ in range(n)]
    rooms = [c * 10 * p for c,p in zip(caps,percents)]
    weights = [c * 1000 for c in caps]
    pool = rng.randrange(0, 301)
    left = pool * 1000
    remaining = sum(w for w,r in zip(weights,rooms) if r > 0)
    expected = [Fraction(0) for _ in caps]
    active = sorted((i for i,r in enumerate(rooms) if r > 0), key=lambda i: Fraction(rooms[i],weights[i]))
    for index,i in enumerate(active):
        if Fraction(left * weights[i], remaining) >= rooms[i]:
            expected[i]=Fraction(rooms[i]); left-=rooms[i]; remaining-=weights[i]
        else:
            for j in active[index:]: expected[j]=Fraction(left*weights[j],remaining)
            break
    got = lua.globals().allocation_case(lua.table_from(caps), lua.table_from(percents), pool)
    values = [int(got[i+1]) for i in range(n)]
    for v,e,r in zip(values,expected,rooms):
        assert 0 <= v <= r
        worst=max(worst,abs(v-e))
        assert abs(v-e) <= 1, (caps,percents,pool,values,expected)
    max_sum_error=max(max_sum_error,abs(sum(values)-min(pool*1000,sum(rooms))))
print(f'PASS water-fill search seed20261021: {samples} cases, 3..8 Import parts, zero/partial/full rooms; instruction guard held; max deviation from rational oracle={float(worst):.6f} internal unit; max pool-sum error={max_sum_error}', flush=True)

u = ui.ui_runtime()
u.execute(r'''
local D=SMROptInTrainDistribution
local t,s,h=fixture(0,0,60,250)
local dlg,row=dialog(s); OnMsg.DialogOpen(dlg)
-- A cached hub ownership read followed by a fresh write chooses from different sets.
assert(D.Set(s,'Metals','export',0))
rawset(s,D.LOCAL_FIELD,{Metals={mode='import',percent=70}})
h.nodes[s]=nil -- route ownership changes inside the one-second cache interval
assert(D.HubFor(s)==h)
s:ToggleAcceptResource('Metals',false)
assert(not D.HubFor(s))
local e=D.Get(s,'Metals')
assert(e.mode=='import' and e.percent==100)
assert(rawget(h,D.FIELD)[s].Metals.mode=='export')
print('COUNTEREXAMPLE UI leave-hub seam: cached Export0 click writes Import100 into local Import70; current local cycle would disable and retain70')

-- Default follows the same stale read/fresh write seam on joining a hub.
local t,s,h=fixture(0,0,60,250)
assert(D.Set(s,'Metals','import',77)); h.nodes[s]=nil; D.Refresh()
assert(D.Get(s,'Metals')==nil)
h.nodes[s]=true
s:ToggleAcceptResource('Metals',false)
assert(D.HubFor(s)==h and D.Get(s,'Metals').mode=='export' and D.Get(s,'Metals').percent==0)
print('COUNTEREXAMPLE UI join-hub seam: cached local Default click overwrites saved hub Import77 with Export0; current hub cycle would disable and retain77')

-- Clear active row and table only, preserve other resource and dormant local data.
assert(D.Set(s,'Food','balanced',31)); rawset(s,D.LOCAL_FIELD,{Metals={mode='balanced',percent=23}})
assert(D.Clear(s,'Metals')); assert(rawget(h,D.FIELD)[s].Food.percent==31)
assert(D.Clear(s,'Food')); assert(rawget(h,D.FIELD)[s]==nil and rawget(s,D.LOCAL_FIELD).Metals.percent==23)
assert(rawget(h,D.FIELD) and next(rawget(h,D.FIELD))==nil)
print('OBSERVE Clear: active station entry removed, dormant local kept; empty hub root table remains {}')
h.nodes[s]=nil; D.Refresh(); assert(D.Clear(s,'Metals')); assert(rawget(s,D.LOCAL_FIELD)==nil)
print('PASS Clear local empty table removed; hub active per-station table removed; dormant set preserved')

-- Broadcast disabled with no saved source row must clear target remembered row.
local t,s,h=fixture(0,0,60,250)
h.hub=false; h.GetTrainExportFloor=nil; h.HubTrackGraph=nil; h.nodes=nil; D.Refresh()
assert(D.Set(h,'Metals','import',64)); s:SetAcceptResourceState('Metals','disabled')
s:ToggleAcceptResource('Metals',true)
assert(not h:IsResourceEnabled('Metals') and not rawget(h,D.LOCAL_FIELD))
s:ToggleAcceptResource('Metals',false); assert(s:IsResourceEnabled('Metals') and D.RowState(s,'Metals')=='default')
s:ToggleAcceptResource('Metals',true); assert(h:IsResourceEnabled('Metals') and D.RowState(h,'Metals')=='default')
s.city.train_track_routes=false; D.Refresh()
s:ToggleAcceptResource('Metals',false); s:ToggleAcceptResource('Metals',false)
assert(D.RowState(s,'Metals')=='import' and D.Get(s,'Metals').percent==100)
print('PASS disabled/Default broadcast clears destination row; false route index click defaults Import100')
local t,s,h=fixture(0,0,60,250)
h.hub=false; h.GetTrainExportFloor=nil; h.HubTrackGraph=nil; h.nodes=nil
local far=station(0,60); far.handle=3; far.city=s.city
local right={members={s,far},trains={}}
s.city.train_track_routes[right]=right.members; s.city.labels.Station={s,h,far}; UIColony.labels=s.city.labels; D.Refresh()
assert(D.IsJunction(s))
for _,mode in ipairs({'import','export'}) do
    assert(D.Set(s,'Metals',mode,20))
    local tip=s:ResourceRolloverText('Metals')
    assert(tip:find('passes through',1,true))
    assert(tip:find(mode=='import' and 'never take it away' or 'never deliver here',1,true))
    print('COUNTEREXAMPLE joining '..mode..' help combines terminal never-clause with passes-through clause')
end
assert(not D.error and not D.ui_error)
''')
print('NOT RUN: engine scheduling, actual route rebuilding, cabin/drone operation, real UI pixels, save serialization, player saves.', flush=True)
