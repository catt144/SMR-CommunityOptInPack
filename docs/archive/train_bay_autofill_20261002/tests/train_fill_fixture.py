"""Archived vanilla bodies and engine doubles for auto-fill/save compatibility checks."""
import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
ARCHIVE = ROOT.parent / "SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src"
CODE = ROOT / "Code/TrainHub_70_TrainBay.lua"
HERE = Path(__file__).resolve().parent


def text(rel):
    path = ARCHIVE / rel
    print("source:", rel, "sha256:", hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
    return path.read_text(encoding="utf8")


def body(src, start, end="\nend\n"):
    i = src.index(start)
    return src[i:src.index(end, i) + len(end)]


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(HERE))
    spec.loader.exec_module(mod)
    return mod


def need_exports():
    lua = module("distribution_smoke").runtime()
    lua.execute(r'''
local D=SMROptInTrainDistribution
local t,s,h=fixture(0,220,120,480)
assert(D.Parent(s)==h and D.HubFor(s)==h)
assert(D.BranchNeed(s,'Metals')==10000,'empty spoke wants its dial')
assert(D.ChildNeed(h,'Metals')==10000)
local t2,s2,h2=fixture(40,220,120,480)
assert(D.BranchNeed(s2,'Metals')==-30000,'40 held against a dial of 10 offers 30 back')
''')
    print("PASS need exports: BranchNeed/ChildNeed read brief 10's stop arithmetic (+10 empty, -30 over its dial)", flush=True)


def spawn_spot():
    traffic = module("traffic_smoke")
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(traffic.STUBS)
    code = traffic.SOURCE.read_text(encoding="utf-8")
    print("20_TrainHub.lua sha256:", hashlib.sha256(traffic.SOURCE.read_bytes()).hexdigest(), flush=True)
    lua.execute(code[:code.index("-- Vanilla creates only indices 0..4")])
    lua.execute(traffic.between(code, "DefineClass.SMROptInTrainHub6Base =", "-- The BuildingTemplate companion"))
    lua.execute("TrackBase={}\n" + body(text("Lua/Buildings/Track.lua"), "function TrackBase:GetSpawnPoint("))
    n = lua.execute(r'''
local n=0
for rotation=0,5 do for _,start in ipairs({true,false}) do for k=1,6 do
 local h=newhub(rotation,start)
 local spot=TrackBase.GetSpawnPoint(h.tracks[k],h)
 local pos,angle=h:GetSpotLoc(spot)
 local stop=h:GetSpotLoc(h:GetSpotBeginIndex('Stop'..k))
 assert(pos.xx==stop.xx and pos.yy==stop.yy and pos.zz==stop.zz,'spawn is off the parked siding')
 local _,out=h:GetSpotAxisAngle(h:GetSpotBeginIndex('Rampdepart'..k))
 assert(angle==out,'spawn does not face out along its arm')
 n=n+1
end end end
return n''')
    print(f"PASS spawn spot math: archived GetSpawnPoint with mocked native spot lookup agrees with Stop "
          f"and outward facing ({n} arm/rotation/end cases); not engine placement proof. "
          "Final object placement is tested in bay_spawn_smoke.py", flush=True)


STUBS = r'''
now=0; GameTime=function() return now end
const={HourDuration=60000,ResourceScale=1000}
empty_table={}; Min=math.min; Max=math.max
Cities={}; SelectedObj=false
table.find=function(t,v) for i,x in ipairs(t) do if x==v then return i end end end
table.remove_value=function(t,v) for i=#t,1,-1 do if t[i]==v then table.remove(t,i) return end end end
table.remove_entry=table.remove_value
table.insert_unique=function(t,v) if not table.find(t,v) then t[#t+1]=v end end
table.clear=function(t) for k in pairs(t) do t[k]=nil end end
string.concat=function(sep,...) return table.concat({...},sep) end
local handlers={}
OnMsg=setmetatable({}, {__newindex=function(_,k,fn) handlers[k]=handlers[k] or {}; table.insert(handlers[k],fn) end})
Msg=function(name,...) for _,fn in ipairs(handlers[name] or {}) do fn(...) end end
g_Classes={}
DefineClass=setmetatable({}, {__newindex=function(_,name,def)
    def.class=name; def.__index=def
    local parent=def.__parents and g_Classes[def.__parents[1]]
    setmetatable(def,{__index=parent})
    g_Classes[name]=def; rawset(_G,name,def)
end})
function IsKindOf(o,name)
    if type(o)~='table' then return false end
    local c=rawget(o,'class') and o or getmetatable(o)
    while c do
        if rawget(c,'class')==name then return true end
        local mt=getmetatable(c); c=mt and mt.__index
    end
    return false
end
IsValid=function(o) return type(o)=='table' and not o.invalid end
DefineClass.MapObject={}
function MapObject:ChangeClass(name) ChangeClassMeta(self,name) end -- the engine's C entry
function MapObject:OnClassChanged() end
DefineClass.TrackBase={}
StationsLink=TrackBase
DefineClass.Train={__parents={'MapObject'}}
Demolishable=Train
function Train:KickUnitsFromHolder() end
function Train:SetCommand(c) self.command=c end
function Train:Idle() self.idled=true end -- CommandObject:Idle stands here
function Train:SetPos(p) self.pos=p end
function Train:SetAngle(a) self.angle=a end
function Train:GetPos() return self.pos end
function Train:GetAttach() end
function Train:GetVisualPos() end; function Train:GetMap() end; function Train:GetAngle() return self.angle end
function Train:SetStoredAmount(res,n) self.stockpiled_amount[res]=n end
dropped=0
PlaceResourceStockpile_Delayed=function(_,_,_,qty) dropped=dropped+qty end
DefineClass.SMROptInTrainHubBase={}
CreateGameTimeThread=function(fn,...) fn(...) end
PlayFX=function() end; PlayFXAroundBuilding=function() end; RefreshXBuildMenu=function() end
RebuildInfopanel=function() end; AddObjectToNotification=function() end; IsT=function() return false end
GetNextConnectedStation=function(st) return st end
weak_keys_meta={__mode='k'}
GameVar=function(name,v,meta) rawset(_G,name,setmetatable(v,meta)) end
City={}
ColonyGetPrefabs=function(p,city) return city.available_prefabs[p] or 0 end
function DoneObject(o)
    o:Done()
    table.remove_value(o.city.labels.Train,o)
    o.invalid=true
end
function PlaceObjectIn(class,station)
    local o=setmetatable({city=station.city,stockpiled_amount={},assigned_resources={},units={},
        track=false,at_station=true,handle=next_handle()},g_Classes[class])
    table.insert(o.city.labels.Train,o)
    return o
end
local handle=2000
function next_handle() handle=handle+1 return handle end
persist_impl=function() return nil end
PersistGame=function(...) return persist_impl(...) end
'''

FIXTURE = r'''
city=setmetatable({available_prefabs={Train=10},labels={Train={},Station={}},train_track_routes={}},{__index=City})
Cities={city}
function station(handle)
    local st={handle=handle,city=city,track_busy={},storable_resources={'Metals'},working=true}
    function st:RemoveOccupyingTrain(t) for k,v in pairs(self.track_busy) do if v==t then self.track_busy[k]=nil end end end
    function st:RemoveNoDestPassengers() end
    table.insert(city.labels.Station,st)
    return st
end
hub=setmetatable(station(1),SMROptInTrainHubBase)
hub.first_connector_idx,hub.last_connector_idx=1,1
hub.supply={Metals={GetActualAmount=function() return 400000 end}}
hub.demand={Metals={GetTargetAmount=function() return 0 end}}
s1=station(2)
track=setmetatable({idx=1,city=city,assigned_vehicles={}},TrackBase)
function track:GetStartStation() return hub end
function track:GetEndStation() return s1 end
local el={track_obj=track}
function hub:GetConnectorElement(i) return i==1 and el or nil end
function hub:GetConnectionSpot(t) return t.idx end
function hub:GetOccupyingTrain(t) return self.track_busy[t.idx] end
function hub:AddOccupyingTrain(t) self.track_busy[t.track.idx]=t end
function hub:GetSpotBeginIndex(name) return name end
function hub:GetSpotLoc(spot) return 'pos:'..spot, 'out:'..spot end
SMROptInTrainFloor={HubSpawnLocation=function(h,idx) return 'pos:Spawn'..idx,'out:Spawn'..idx end}
function set_route(...)
    local r={...}; r.edges={{tracks={track}}}
    city.train_track_routes={[track]=r}
    return r
end
route=set_route(hub,s1)
need=6*42000
SMROptInTrainDistribution={active=true,
    HubFor=function(st) return hub end, Parent=function(st) return hub end,
    BranchNeed=function(st,res) return st==s1 and need or 0 end}
for i=1,2 do -- two vanilla trains, both out on the line
    local t=PlaceObjectIn('Train',hub); t:AssignToTrack(track); t.at_station=false; t.current_station=s1; t.command='GotoStation'
end
function extras() local n=0 for _,t in ipairs(city.labels.Train) do if IsKindOf(t,'HubTrain') then n=n+1 end end return n end
function leave(t) hub:RemoveOccupyingTrain(t); t.at_spawn_track=false; t.at_station=false; t.current_station=s1 end
function newest() return city.labels.Train[#city.labels.Train] end
pool=function() return city.available_prefabs.Train or 0 end
'''


def runtime(code=None):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(STUBS)
    transport = text("Lua/TrainTransport.lua")
    lua.execute("local seen_table\n" + body(transport, "function GetTrainsOnRoute("))
    track = text("Lua/Buildings/Track.lua")
    for start in ("function TrackBase:CanAddVehicle(", "function TrackBase:AssignTrain(", "function TrackBase:GetSpawnPoint("):
        lua.execute(body(track, start))
    link = text("Lua/Buildings/StationsLink.lua")
    for start in ("function StationsLink:AddTransportLink(", "function StationsLink:RemoveTransportLink("):
        lua.execute(body(link, start))
    train = text("Lua/Units/Train.lua")
    for start in ("function Train:Done(", "function Train:Start(", "function Train:DestroySilent(",
                  "function Train:OnDemolish(", "function Train:AssignToTrack("):
        lua.execute(body(train, start))
    demolish = text("Lua/Demolishable.lua")
    lua.execute(body(demolish, "function Demolishable:DoDemolish(") + body(demolish, "function Demolishable:UseDemolishedState("))
    lua.execute(body(text("Lua/City.lua"), "function City:AddPrefabs("))
    colony = text("Lua/Colony.lua")
    lua.execute(colony[colony.index("local function ColonyAddPrefabsSingleCity("):colony.index("function ColonyAddPrefabs(")]
                + body(colony, "function ColonyAddPrefabs("))
    lua.execute(body(text("CommonLua/Classes/_object.lua"), "function ChangeClassMeta("))
    persist = text("CommonLua/Core/persist.lua")
    lua.execute(persist[persist.index('GameVar("ObjsToDeleteOnLoadGame"'):persist.index("function CancelDeleteOnLoadGameList(")])
    lua.execute(persist[persist.index("PersistResolvePermanent = {"):persist.index("function LoadMissingPermanent(")])
    loop = persist[persist.index("\tlocal concat = string.concat"):persist.index("\nend\n\nDefineClass.UnpersistedMissingClass")]
    lua.execute("function register(permanents, direction)\n" + loop + "\nend")
    lua.execute(body(text("CommonLua/Classes/_cobject.lua"), "function MapObject:UnpersistMissingClass("))
    lua.execute(FIXTURE)
    lua.execute(code if code is not None else CODE.read_text(encoding="utf8"))
    print("70_TrainBay.lua sha256:", hashlib.sha256(CODE.read_bytes()).hexdigest(), flush=True)
    lua.execute("assert(SMROptInTrainBay.active, SMROptInTrainBay.error); Msg('LoadGame')")
    return lua

