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
''')


if __name__ == '__main__':
    main()
