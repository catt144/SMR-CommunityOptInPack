"""The hub refuses add-train at the one vanilla spawn and on its card (brief 34b, Fix 2).

Archived 1.1.1.406343 bodies of TrackBase:AssignTrain / GetSpawnPoint and
StationsLink:AddTransportLink run against engine doubles, then the real bay file.
A hub as the station argument must spawn nothing and spend no prefab; a plain
station must still spawn exactly as vanilla does. A live spawn remains an attended check.
"""
import hashlib
import subprocess
import sys
from pathlib import Path
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
ARCHIVE = ROOT.parent / "SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src"
CODE = ROOT / "Code/TrainHub_70_TrainBay.lua"

print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), flush=True)


def text(rel):
    path = ARCHIVE / rel
    print("source:", rel, "sha256:", hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
    return path.read_text(encoding="utf8")


def body(src, start, end="\nend\n"):
    i = src.index(start)
    return src[i:src.index(end, i) + len(end)]


code = CODE.read_text(encoding="utf8")
print("70_TrainBay.lua sha256:", hashlib.sha256(CODE.read_bytes()).hexdigest(), flush=True)

# The cut is real: none of auto-fill's names survive; the guard and the class do.
for forbidden in ['TrainRoutesRebuilt', 'try_fill', 'HubSpawnLocation', 'TransportLinkChanged',
                  'AssignTrain(hub)', 'NewMinute', 'fill_window']:
    assert forbidden not in code, forbidden
for forbidden in ['ConstructTrain', 'ToggleCreateRouteMode', 'Untranslated']:
    assert forbidden not in code, forbidden + ' (the hub card never shows the buttons; owner 2026-10-02)'
for required in ['function TrackBase:AssignTrain(', 'DefineClass.HubTrain', 'persist_baseclass = "Train"']:
    assert required in code, required
print('PASS cut and guard present by text', flush=True)

STUBS = r'''
now=12345; GameTime=function() return now end
empty_table={}; Min=math.min; Max=math.max
table.find=function(t,v) for i,x in ipairs(t) do if x==v then return i end end end
table.insert_unique=function(t,v) if not table.find(t,v) then t[#t+1]=v end end
table.remove_entry=function(t,v) for i=#t,1,-1 do if t[i]==v then table.remove(t,i) return end end end
printed={}
local raw_print=print
print=function(...) local parts={} for i=1,select('#',...) do parts[#parts+1]=tostring((select(i,...))) end
    printed[#printed+1]=table.concat(parts,' ') end
Untranslated=function(s) return 'U:'..tostring(s) end
T=function(id,s) return 'T'..tostring(id)..':'..tostring(s) end
Msg=function() end
SelectedObj=false; RebuildInfopanel=function() end
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
DefineClass.TrackBase={}
StationsLink=TrackBase
DefineClass.Train={}
function Train:GetAttach() end
function Train:SetPos(p) self.pos=p end
function Train:SetAngle(a) self.angle=a end
function Train:AssignToTrack(track) self.track=track; table.insert_unique(track.assigned_vehicles,self) end
function Train:Start() self.started=true end
function Train:DestroySilent() self.invalid=true end
DefineClass.Station={}
DefineClass.SMROptInTrainHubBase={__parents={'Station'}}
CreateGameTimeThread=function(fn,...) fn(...) end
city={available_prefabs={Train=3},labels={Train={}}}
ColonyGetPrefabs=function(p,c) return c.available_prefabs[p] or 0 end
ColonyAddPrefabs=function(p,n,_,c) c.available_prefabs[p]=c.available_prefabs[p]+n end
local handle=100
function PlaceObjectIn(class,station)
    handle=handle+1
    local o=setmetatable({city=station.city,handle=handle,stockpiled_amount={},assigned_resources={}},g_Classes[class])
    table.insert(city.labels.Train,o)
    return o
end
function station(name,handle,hub)
    local st=setmetatable({name=name,handle=handle,city=city,track_busy={},trains_in_construction=0,construction_queue={}},
        hub and SMROptInTrainHubBase or Station)
    function st:GetConnectionSpot(track) return 1 end
    function st:GetSpotBeginIndex(spot) return 'spot:'..spot end
    function st:GetSpotLoc(spot) return 'pos:'..tostring(spot),'angle:'..tostring(spot) end
    function st:GetOccupyingTrain(track) return self.track_busy[1] end
    function st:AddOccupyingTrain(t) self.track_busy[1]=t end
    return st
end
hub=station('the hub',6430,true)
plain=station('a station',10650,false)
track=setmetatable({handle=77,assigned_vehicles={}},TrackBase)
function track:CanAddVehicle() return true end
function track:GetMaxVehicles() return 2 end
'''

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(STUBS)
trk = text("Lua/Buildings/Track.lua")
for start in ("function TrackBase:AssignTrain(", "function TrackBase:GetSpawnPoint("):
    lua.execute(body(trk, start))
lua.execute(body(text("Lua/Buildings/StationsLink.lua"), "function StationsLink:AddTransportLink("))
lua.execute(body(text("Lua/Buildings/StationsLink.lua"), "function StationsLink:CanAddVehicle("))
lua.execute(code)
lua.execute(r'''
local B=SMROptInTrainBay
assert(B.active, tostring(B.error))
assert(IsKindOf(HubTrain,'Train') and HubTrain.persist_baseclass=='Train','HubTrain stays, inheriting Train')

-- A hub as the spawn host: refused before vanilla's thread, nothing placed, no prefab spent.
assert(ColonyGetPrefabs('Train',city)==3)
track:AssignTrain(hub)
assert(#city.labels.Train==0,'no train placed at a hub')
assert(ColonyGetPrefabs('Train',city)==3,'no prefab spent on a refusal')
assert(#track.assigned_vehicles==0 and hub.track_busy[1]==nil)
assert(B.stats.refused==1)
local function refusal_line()
  for _,l in ipairs(printed) do if l:find('[TrainBay] refused hub=6430',1,true) then return l end end
end
-- FIX_POLICY §8 (owner 2026-10-02): the line is a dev trace, silent until SMROptInPack.TrainTrace.
assert(rawget(_G,'SMROptInPack')==nil and not refusal_line(),'the refusal is silent with the switch off')
SMROptInPack={TrainTrace=true}
track:AssignTrain(hub)
assert(B.stats.refused==2 and #city.labels.Train==0 and ColonyGetPrefabs('Train',city)==3,'a second refusal, still nothing spent')
assert(refusal_line(),'the refusal line names the hub (switch on)')

-- A plain station: vanilla's archived body spawns exactly as before.
track:AssignTrain(plain)
assert(#city.labels.Train==1,'one train placed at the station')
local t=city.labels.Train[1]
assert(t.current_station==plain and t.at_spawn_track==true and t.started,'born at the station, at_spawn_track, started')
assert(t.pos=='pos:spot:Spawn1' and t.angle=='angle:spot:Spawn1','placed on the station\'s own Spawn spot')
assert(ColonyGetPrefabs('Train',city)==2 and track.assigned_vehicles[1]==t and plain.track_busy[1]==t)
assert(B.stats.refused==2,'the station path is not counted as a refusal')

''')
print('PASS hub refusal: AssignTrain(hub) spawns nothing and spends nothing; AssignTrain(station) spawns on the '
      'station\'s own Spawn spot; no card methods remain (the hub never showed the buttons)', flush=True)
print('NOT RUN: a live spawn and the Transportation overview row', flush=True)
