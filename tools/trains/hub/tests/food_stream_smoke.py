"""34b v4: real TestKit dispatch/Agent, Lua request shell, simulated clock/UI.

No retail pixel, C matching or pathfinding claim. No live mutation.
"""
from pathlib import Path
import hashlib
import subprocess
import sys

from distribution_smoke import ROOT, runtime
from export_pairing_smoke import matcher

KIT = ROOT.parent / 'SMR-BugFixPack-TestKit'
SRC = ROOT.parent / 'SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src'


def main():
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    for path in [ROOT, KIT]:
        print(path.name, 'HEAD:', subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip(), flush=True)
    lua = runtime(matcher)
    ui = (ROOT/'Code/StationRows_45_TrainDistributionUI.lua').read_text(encoding='utf8')
    lua.execute('local D=SMROptInTrainDistribution\n' +
                ui[ui.index('function D.RowState('):ui.index('local station_installed, row_installed')])
    lua.execute(r'''
-- Real dispatcher lifecycle; engine additive message delivery.
messages={}
OnMsg=setmetatable({}, {__newindex=function(_,key,fn)
    messages[key]=messages[key] or {}; table.insert(messages[key],fn)
end})
function message(key) for _,fn in ipairs(messages[key] or {}) do fn() end end
game_time=0; time_factor=0; current_thread=false; threads={}; log_lines={}
GameTime=function() return game_time end
GetTimeFactor=function() return time_factor end
CurrentMap=1
IsValid=function(o) return type(o)=='table' and not o.invalid end
Sleep=function(ms) return coroutine.yield(ms) end
function spawn(fn)
    local co=coroutine.create(fn); threads[co]=true
    local before=current_thread; current_thread=co
    local ok,err=coroutine.resume(co); current_thread=before; assert(ok,err)
    return co
end
CreateGameTimeThread=spawn; CreateRealTimeThread=spawn
IsValidThread=function(co) return threads[co] and coroutine.status(co)~='dead' end
DeleteThread=function(co) threads[co]=nil end
CurrentThread=function() return current_thread end
function tick(ms)
    game_time=game_time+ms
    local copy={} for co in pairs(threads) do copy[#copy+1]=co end
    for _,co in ipairs(copy) do
        if IsValidThread(co) then
            current_thread=co; local ok,err=coroutine.resume(co); current_thread=false; assert(ok,err)
        end
    end
end
ModLog=function(line) log_lines[#log_lines+1]=line end
FlushLogFile=function() end
AreCheatsUsed=function() return false end
Platform={debug=false}; const.HourDuration=30000
FoodResources={Food=true,Bread=true}; guim=1000
RGBA=function(r,g,b,a) return string.format('%d,%d,%d,%d',r,g,b,a) end
RGB=function(r,g,b) return RGBA(r,g,b,255) end
box=function(...) return {...} end
function widget(props,parent)
    local o=props or {}; o.window_state='open'; o.threads={}
    function o:SetText(v) self.Text=v end
    function o:GetText() return self.Text or '' end
    function o:SetEnabled(v) self.enabled=v end
    function o:SetBackground(v) self.Background=v end
    function o:SetRolloverBackground(v) self.RolloverBackground=v end
    function o:SetPressedBackground(v) self.PressedBackground=v end
    function o:CreateThread(name,fn) self.threads[name]=spawn(fn) end
    if parent then table.insert(parent,o) end
    return o
end
XText={new=function(_,props,parent) return widget(props,parent) end}
XTextEditor=XText
''')
    for name in ['70_SMRTK_Core.lua','74_SMRTK_Agent.lua']:
        if name.startswith('74'):
            lua.execute(r'''
SMRTK.pages={}
function SMRTK.Page(id,label,build) SMRTK.pages[id]={build=build} end
function SMRTK.PreloadProbeSweep(e) SMRTK.sweep=e end
function SMRTK.ControlRow(parent) return widget({},parent) end
function SMRTK.Button(parent,label,action,props)
    local o=widget(props,parent); o.caption=widget({Text=label},o); return o
end
''')
        path = KIT/'Code'/name
        print('source:', name, 'sha256:', hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
        lua.execute(path.read_text(encoding='utf8'))
    source = (SRC/'Lua/_TaskRequest.lua').read_text(encoding='utf8')
    lua.execute(source[source.index('function RequestUnitFulfill('):source.index('function Request_OnGameObjReplaced(')])
    lua.execute(r'''
local T=SMRTK
T.Action{id='speed_ultra',run=function() time_factor=5000; return {} end}
local _,station,hub=fixture(0,0,120,480)
station.GetMap=function() return 1 end
assert(SMROptInTrainDistribution.Set(station,'Food','export',50))
station.supply.Food.actual=10000; station.supply.Food.target=10000
station.handle=101; SelectedObj=station; watched=station
g_Classes.TaskRequestHub=TaskRequestHub
local function object(class,handle,map)
    local o={class=class,handle=handle}
    function o:GetMap() return map or 1 end
    function o:GetDist2D() error('fixed radius must never be consulted') end
    return o
end
function food_req(src,n,want,res,flags)
    local r=request(n,want); r.source=src; r.resource=res or 'Food'; r.flags=flags or (const.rfSupply|const.rfStorageDepot)
    function r:GetSource() return self.source end
    function r:GetResource() return self.resource end
    function r:Fulfill(amount)
        if self.reject then return false end
        self.actual=self.actual-amount; return true
    end
    return r
end
far=object('StorageDepot',201); other=object('StorageDepot',202)
remote=object('StorageDepot',203,2); consumer=object('Diner',301)
s=food_req(far,52000,50000); s2=food_req(other,12000,15000,'Bread')
far.supply={Food=s}; other.supply={Bread=s2}
d=food_req(station,110000,0,'Food',const.rfDemand|const.rfStorageDepot)
station.demand.Food=d
local station_s=station.supply.Food
station_s.source=station; station_s.GetSource=s.GetSource; station_s.GetResource=function() return 'Food' end
controller.supply_queues={[0]={Food={s,s2,station_s},Bread={s2},Metals={food_req(far,2000,0,'Metals')}},[1]={Food={s}}}
second_controller={supply_queues={[0]={Food={s,food_req(remote,99999,0)}}}}
controller.CanCommandDrones=function() return true end
second_controller.CanCommandDrones=controller.CanCommandDrones
controller.IsInWorkRange=controller.CanCommandDrones
second_controller.IsInWorkRange=controller.CanCommandDrones
station.command_centers={controller,second_controller}
agent.class='Drone'; agent.handle=401; agent.command_center=controller; agent.d_request=d
base_fulfill=RequestUnitFulfill
''')
    path=ROOT/'tools/trains/hub/tests/80_AgentSlots_34b.lua.txt'
    lua.execute(path.read_text(encoding='utf8'))
    lua.execute(r'''
local T=SMRTK
local ok,read=T.Run('slot_1')
if not ok then error(read.reason) end
assert(ok and read.stores==3 and read.controllers==2,'queue union includes far stores, dedupes aliases/controllers, excludes other map')
local function button_state(id,armed)
    local b=widget({}); b.caption=widget({})
    T.UpdateSlotIndicator(b,id)
    assert(b.Background==(armed and '45,114,76,255' or '55,68,82,255'))
    assert(b.RolloverBackground==(armed and '58,140,94,255' or '85,105,124,255'))
    assert(b.PressedBackground==(armed and '35,92,60,255' or '36,46,56,255'))
    assert((b.caption.Text:find('ARMED',1,true)~=nil)==armed)
end
button_state('slot_9',false); button_state('slot_3',false)
assert(T.Arm('slot_9')); assert(T.armed.slot_9 and not T.armed.sol_34b)
assert(RequestUnitFulfill~=base_fulfill)
button_state('slot_9',true); button_state('slot_3',false)
local wrapper=RequestUnitFulfill
local function rows(kind)
    local out={}
    for _,line in ipairs(log_lines) do
        if line:find('SMRTK_STREAM',1,true) and line:find('row='..kind..' ',1,true) then out[#out+1]=line end
    end
    return out
end
assert(#rows('snapshot')==3)
assert(RequestUnitFulfill(s,agent,2000))
local hauls=rows('haul'); assert(#hauls==1)
local line=hauls[1]
for _,field in ipairs({'source_before=52','source_after=50','source_desired=50','amount=2',
    'destination_stock=10','destination_desired=120','destination_is_export_station=true'}) do
    assert(line:find(field,1,true),field..' missing from '..line)
end
-- Failed fulfill, wrong controller, non-food and demand fulfillment cannot look like a pickup.
s.reject=true; assert(not RequestUnitFulfill(s,agent,1000)); s.reject=false
agent.command_center={}; RequestUnitFulfill(s,agent,1000); agent.command_center=controller
RequestUnitFulfill(food_req(far,10000,0,'Metals'),agent,1000)
RequestUnitFulfill(d,agent,1000)
assert(#rows('haul')==1)
-- A consumer receives real physical-stock information and explicitly has no Desired slider.
local cd=food_req(consumer,20000,0,'Food',const.rfDemand)
consumer.consumption_resource_request=cd
consumer.GetConsumptionStoredResources=function() return 1234 end
agent.d_request=cd
RequestUnitFulfill(s,agent,1000)
hauls=rows('haul'); assert(#hauls==2)
assert(hauls[2]:find('destination_stock=1.234',1,true) and hauls[2]:find('destination_desired=n/a',1,true))
assert(hauls[2]:find('destination_is_export_station=false',1,true))
agent.d_request=d
tick(const.HourDuration); assert(#rows('snapshot')==6,'each store emitted at hourly boundary')
-- Build the actual Agent page and its periodic indicator/readout refresh.
local parent=widget({}); T.pages.Agent.build(parent)
assert(parent[1].Text:find('snapshot complete',1,true))
assert(parent.threads.SMRTKAgentRefresh and parent.threads.FoodStreamReadout34b)
assert(T.Run('slot_3')); assert(not T.armed.slot_3 and T.armed.sol_34b)
button_state('slot_3',true); button_state('slot_9',true)
message('SaveGameStart')
button_state('slot_3',false); button_state('slot_9',false)
local snapshots,hauls_before=#rows('snapshot'),#rows('haul')
RequestUnitFulfill(s,agent,1000); tick(const.HourDuration)
assert(#rows('haul')==hauls_before and #rows('snapshot')==snapshots)
assert(parent[1].Text:find('STREAM OFF: SaveGameStart',1,true))
-- No startup/reload auto-arm. Re-arming does not stack the fulfillment wrapper.
time_factor=0; assert(T.Arm('slot_9')); assert(RequestUnitFulfill==wrapper)
assert(T.Run('slot_3')); message('LoadGame')
button_state('slot_3',false); button_state('slot_9',false)
time_factor=0; assert(T.Arm('slot_9')); assert(T.Run('slot_3'))
message('CurrentMapChange'); button_state('slot_3',false); button_state('slot_9',false)
-- The run's own completion clears only its indicator; STREAM remains green until stopped.
time_factor=0; assert(T.Arm('slot_9')); assert(T.Run('slot_3'))
SetGameSpeed=function(n) time_factor=n end; PlayFX=function() end
tick(const.HourDuration*24)
button_state('slot_3',false); button_state('slot_9',true)
assert(T.Disarm('slot_9','manual')); button_state('slot_9',false)
-- Stream's own invalid-fixture stop must clear its indicator too.
assert(T.Arm('slot_9')); watched.invalid=true; tick(500)
button_state('slot_9',false); watched.invalid=false
-- Existing true armed slots keep their behavior; metadata does not create dummy armed entries.
assert(T.Bind(10,'legacy',function() return {} end,{arm=function() return {} end,disarm=function() return {} end}))
assert(T.Arm('slot_10')); button_state('slot_10',true)
assert(T.Disarm('slot_10','manual')); button_state('slot_10',false)
assert(not T.Bind(11,'bad',function() end,{armed_id=true}))
assert(T.error_count==0, 'dispatcher must record no instrumentation errors')
print('PASS connected queue scope, actual pickups, failed/out-of-scope controls, hourly snapshots and notes readout')
print('PASS actual dispatcher: green normal/hover/pressed, autosave/load/map stop, run completion, stream stop, legacy slot')
''')


if __name__ == '__main__':
    main()
