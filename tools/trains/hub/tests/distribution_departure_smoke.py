"""Loaded-cargo departure watchdog on archived LoadTrain and track traversal.

Movement and request objects are doubles; a departure must come from LoadTrain's
actual SetCommand result, never from a test choosing the delivery destination.
"""
import hashlib
import subprocess
import sys
from distribution_smoke import ROOT, ARCHIVE, runtime


def main():
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), flush=True)
    lua = runtime()
    train = (ARCHIVE/'Units/Train.lua').read_text(encoding='utf8')
    transport = (ARCHIVE/'TrainTransport.lua').read_text(encoding='utf8')
    print('TrainTransport.lua sha256:', hashlib.sha256((ARCHIVE/'TrainTransport.lua').read_bytes()).hexdigest(), flush=True)
    lua.execute('''
-- Engine permits #nil; keep that behavior without rewriting the train bodies.
debug.setmetatable(nil, {__len=function() return 0 end})
table.clear=function(t) for k in pairs(t) do t[k]=nil end end
Msg=function() end; PlayFX=function() end
const.HourDuration=60000
WaitWakeup=function() end
engine_assertions=0
''')
    lua.execute(transport[transport.index('const.trfInclusive ='):transport.index('function ForEachTrackInRoute(')])
    # Retail assertions do not provide a departure. Observe their invariant and
    # let the watchdog judge the command instead of treating assert as a stop.
    lua.execute('local assert=function(ok) if not ok then engine_assertions=engine_assertions+1 end end\n'
                + train[train.index('function Train:LoadTrain()'):train.index('function Train:WaitForTrack(')])
    print('archived LoadTrain + ForEachStationAlongTrack; nil length=0; engine assert observed; waits/movement doubled', flush=True)
    lua.execute(r'''
local D=SMROptInTrainDistribution
local function setup(t)
    local track=t.track
    track.city=t.city;track.assigned_vehicles={t};track.elements_under_construction={}
    track.transport_mode='cargo'
    function track:GetStartStation() return self.members[1] end
    function track:GetEndStation() return self.members[#self.members] end
    track.members.edges={{start=track.members[1],dest=track.members[2],tracks={track}}}
    for _,st in ipairs(track.members) do
        st.working=true
        function st:GetConnectedTrack() end
        function st:GetOccupyingTrain() end
        if not st.supply.Butter then
            st.storable_resources[#st.storable_resources+1]='Butter';st.storable_resources.Butter=true
            st.supply.Butter=request(0,10000)
            st.demand.Butter=request(st:GetMaxStorage('Butter'),st:GetMaxStorage('Butter')-10000)
        end
    end
    t.at_station=true;t.at_spawn_track=false;t.departures=0
    function t:GetEmptyStorage()
        local stored=0
        for _,n in pairs(self.stockpiled_amount) do stored=stored+n end
        return 105000-stored
    end
    function t:SetCommand(command,dest)
        self.command=command;self.next_stop=dest
        if command=='GotoStation' and IsValid(dest) and dest~=self.current_station then
            self.departures=self.departures+1
        end
    end
end
local function depart(t,label)
    local before=t.departures
    for attempt=1,3 do
        t:LoadTrain()
        assert(not D.error and not SMROptInTrainFloor.stats.last_error)
        if t.departures>before then
            assert(engine_assertions==0,'native has_work/next_stop invariant failed')
            local dest=t.next_stop
            t.current_station=dest -- movement double follows only the native command
            return dest
        end
    end
    error(label..': watchdog: three LoadTrain calls at one station without departure; command='
        ..tostring(t.command)..' calls='..D.CallsFor(t.current_station)
        ..' engine_assertions='..engine_assertions)
end
local function load_old(t,a,b,res,left,right)
    t.stockpiled_amount[res]=left+right
    t.assigned_resources={[a]={[res]=left},[b]={[res]=right}}
    assert(a.demand[res]:AssignUnit(left) and b.demand[res]:AssignUnit(right))
    OnMsg.LoadGame()
end

for _,case in ipairs({'Butter','ButterLoose','Metals','empty'}) do
    local res=case=='ButterLoose' and 'Butter' or case
    local t,s,h=fixture(0,220,120,480);setup(t)
    if res~='empty' then
        load_old(t,s,h,res,49000,res=='Butter' and 20000 or 49000)
        if case=='ButterLoose' then
            t.assigned_resources[h]=nil;h.demand.Butter:UnassignUnit(20000,false)
            OnMsg.LoadGame()
        end
    else OnMsg.LoadGame() end
    print('LOAD '..case..' parent='..tostring(D.Parent(s) and D.Parent(s).handle)
        ..' colony_routes='..tostring(UIColony.train_track_routes))
    assert(depart(t,res)==h)
    assert(depart(t,res..' hub')==s)
    t:UnloadAll()
    assert(stock(s)==10000 and stock(h)==(res=='Metals' and 308000 or 210000))
    if res=='Butter' then assert(stock(s,'Butter')==10000 and stock(h,'Butter')==59000) end
    assert(engine_assertions==0)
end
print('PASS load + native departure watchdog: Butter 69, Metals 98, train capacity 105, and empty train fetch; hub starts at Metals 220')

do
    local t,s,h=fixture(10,220,120,480);setup(t);OnMsg.LoadGame()
    t:LoadTrain()
    assert(t.command=='Idle' and t.departures==0 and engine_assertions==0)
    local t,s,h=fixture(60,480,120,480);setup(t)
    assert(D.Set(s,'Metals','export',20));t:LoadTrain()
    assert(stock(s)==60000 and t.command=='Idle' and t.departures==0 and engine_assertions==0)
    print('PASS quiet controls: satisfied pin and full-hub refusal create no phantom departure')
end

local trunk,middle,hub=fixture(0,220,120,480);setup(trunk)
local child=station(0,120);child.handle=6243;child.city=middle.city;middle.handle=2012
middle.city.labels.Station={middle,hub,child};hub.nodes[child]=true
local spur={members={child,middle},trains={}}
function spur:GetDestStation(st) return st==child and middle or child end
middle.city.train_track_routes[spur]=spur.members
local t=setmetatable({current_station=child,track=spur,city=middle.city,
    stockpiled_amount={},assigned_resources={},units={},is_stopping=false,
    GetEmptyStorage=trunk.GetEmptyStorage,AddResource=trunk.AddResource,
    LogCargo=trunk.LogCargo,PushDestructor=trunk.PushDestructor,
    PopDestructor=trunk.PopDestructor},{__index=Train})
spur.trains={t};setup(t)
load_old(t,child,middle,'Butter',49000,20000)
assert(D.Parent(child)==middle and D.Parent(middle)==hub)
assert(depart(t,'chained old Butter')==middle)
t:UnloadAll();assert(stock(middle,'Butter')==69000)
assert(depart(trunk,'intermediate fetch')==hub)
assert(depart(trunk,'hub fills empty chain')==middle)
trunk:UnloadAll()
assert(stock(middle)==20000)
assert(depart(t,'intermediate forwards')==child)
t:UnloadAll()
assert(stock(child)==10000 and stock(middle)==10000 and stock(hub)==200000)
assert(stock(child,'Butter')==10000 and stock(middle,'Butter')==10000 and stock(hub,'Butter')==49000)
assert(engine_assertions==0 and rawget(child,D.FIELD)==nil and rawget(middle,D.FIELD)==nil)
for _,st in ipairs({child,middle,hub}) do
    for _,res in ipairs(st.storable_resources) do
        assert(st.supply[res]:GetActualAmount()==st.supply[res]:GetTargetAmount())
        assert(st.demand[res]:GetActualAmount()==st.demand[res]:GetTargetAmount())
    end
end
print('PASS empty chain at load: native commands fetch Metals and return old Butter via intermediate; both pins 10; claims released')

-- Departure alone misses cargo which circles forever. Count native unloads,
-- independently for every resource present at load; fresh loads cannot satisfy
-- the watchdog. No manual delivery destination is used.
local function watch_old(t)
    local left=table.copy(t.stockpiled_amount)
    local add=t.AddResource
    t.landings={};t.visits={}
    function t:AddResource(n,res)
        if n<0 and (left[res] or 0)>0 then
            local delivered=math.min(-n,left[res])
            left[res]=left[res]-delivered
            self.landings[#self.landings+1]={station=self.current_station,res=res,amount=delivered,call=#self.visits}
        end
        add(self,n,res)
    end
    return function(label)
        for call=1,6 do
            -- Unload can satisfy the final call even if no further trip is needed.
            t.visits[#t.visits+1]=t.current_station
            t:LoadTrain()
            assert(not D.error and not SMROptInTrainFloor.stats.last_error)
            local complete=true
            for _,n in pairs(left) do if n>0 then complete=false end end
            if complete then
                print('PASS delivery watchdog '..label..' calls='..call)
                assert(engine_assertions==0)
                return
            end
            assert(t.command=='GotoStation' and t.next_stop~=t.current_station,
                label..': retained cargo without departure')
            t.current_station=t.next_stop
        end
        error(label..': delivery watchdog: old cargo remains after six LoadTrain calls')
    end
end

for _,loose in ipairs({false,true}) do
    for _,full in ipairs({false,true}) do
        local t,s,h=fixture(10,full and 480 or 220,120,480);setup(t)
        -- Off-line reservations survive load; native UnloadAll must release them.
        local off=station(0,120);off.handle=2008
        off.supply.Butter=request(0,10000);off.demand.Butter=request(120000,110000)
        h:AddResource(full and 480000 or 200000,'Butter')
        t.stockpiled_amount={Metals=98000,Butter=7000}
        if not loose then
            t.assigned_resources={[off]={Metals=98000,Butter=7000}}
            assert(off.demand.Metals:AssignUnit(98000) and off.demand.Butter:AssignUnit(7000))
        end
        -- Keep both pins already satisfied, including untouched Butter.
        s:AddResource(10000,'Butter')
        OnMsg.LoadGame()
        local run=watch_old(t)
        run((loose and 'unassigned' or 'off-line')..(full and ' full hub' or ' hub room'))
        for _,event in ipairs(t.landings) do
            assert(event.station==(full and s or h),'hub must be attempted before over-pin dumping')
            if full then assert(t.visits[event.call-1]==h,'overflow preceded actual hub attempt') end
        end
        if full then assert(stock(s)==108000 and stock(s,'Butter')==17000) end
        assert(off.demand.Metals.actual==off.demand.Metals.target)
        assert(off.demand.Butter.actual==off.demand.Butter.target)
    end
end

-- A reservation for this line can also become unreachable when its pin shrinks.
-- Hub refusal evidence must be reconsidered if room opens or a save is loaded.
for _,change in ipairs({'none','room','load'}) do
    local t,s,h=fixture(10,480,120,480);setup(t)
    t.stockpiled_amount={Metals=98000};t.assigned_resources={[s]={Metals=98000}}
    assert(s.demand.Metals:AssignUnit(98000));OnMsg.LoadGame()
    assert(depart(t,'shrunken pin to hub')==h)
    assert(depart(t,'hub refused shrunken pin')==s)
    if change=='room' then h:AddResource(-98000,'Metals') end
    if change=='load' then OnMsg.LoadGame() end
    local run=watch_old(t)
    run('shrunken pin '..change)
    if change=='room' then
        assert(t.landings[1].station==h and stock(s)==10000,'new hub room takes precedence')
    else
        assert(t.landings[1].station==s and stock(s)==108000)
        if change=='load' then assert(t.visits[2]==h and t.landings[1].call==3) end
    end
    assert(s.demand.Metals.actual==s.demand.Metals.target)
end

-- Both endpoints have independent hub lines: neither is the other's parent.
-- Cargo from an obsolete off-line assignment needs a deterministic handoff.
for _,full in ipairs({false,true}) do
    local trunk,gateway,hub=fixture(10,full and 480 or 220,120,480);setup(trunk)
    local peer=station(10,120);peer.handle=2012;peer.city=gateway.city
    local off=station(0,120);off.handle=2008
    local side={members={peer,gateway},trains={}}
    function side:GetDestStation(st) return st==peer and gateway or peer end
    local peer_hub={members={peer,hub},trains={}}
    gateway.city.train_track_routes[side]=side.members
    gateway.city.train_track_routes[peer_hub]=peer_hub.members
    gateway.city.labels.Station={gateway,hub,peer};hub.nodes[peer]=true
    local t=setmetatable({current_station=peer,track=side,city=gateway.city,
        stockpiled_amount={Metals=98000},assigned_resources={[off]={Metals=98000}},
        units={},is_stopping=false,AddResource=trunk.AddResource,LogCargo=trunk.LogCargo,
        PushDestructor=trunk.PushDestructor,PopDestructor=trunk.PopDestructor},{__index=Train})
    side.trains={t};setup(t);assert(off.demand.Metals:AssignUnit(98000));OnMsg.LoadGame()
    assert(D.Parent(peer)==hub and D.Parent(gateway)==hub)
    watch_old(t)('sideways off-line '..(full and 'full hub' or 'hub room'))
    assert(t.landings[1].station==gateway and stock(gateway)==108000)
    assert(off.demand.Metals.actual==off.demand.Metals.target)
    if not full then
        assert(depart(trunk,'gateway forwards dump')==hub)
        trunk:UnloadAll()
        assert(stock(gateway)==10000 and stock(hub)==318000)
    else
        trunk:LoadTrain()
        assert(trunk.command=='Idle' and stock(gateway)==108000,'full hub must refuse new export')
    end
    print('PASS sideways gateway '..(full and 'holds overflow after full hub refusal' or 'forwards excess to hub'))
end
''')


if __name__ == '__main__':
    main()
