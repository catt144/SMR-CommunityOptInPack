"""The hub refuses add-train at the one vanilla spawn and on its card (brief 34b, Fix 2).

Archived 1.1.1.406343 bodies of TrackBase:AssignTrain / GetSpawnPoint and
StationsLink:AddTransportLink run against engine doubles, then the real bay file.
A hub as the station argument must spawn nothing and spend no prefab; a plain
station must still spawn exactly as vanilla does. The four hub card methods are
exercised on a button double. Engine rendering remains an attended check.
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
for required in ['function TrackBase:AssignTrain(', 'DefineClass.HubTrain', 'persist_baseclass = "Train"',
                 'function SMROptInTrainHubBase:ConstructTrain_Update(',
                 'function SMROptInTrainHubBase:ToggleCreateRouteMode_Update(',
                 'function SMROptInTrainHubBase:ConstructTrain()',
                 'function SMROptInTrainHubBase:ToggleCreateRouteMode()']:
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
function Station:ToggleCreateRouteMode_Update(button) button:SetEnabled(true) end
function Station:ConstructTrain(change) self.trains_in_construction=(self.trains_in_construction or 0)+change end
function Station:ToggleCreateRouteMode() self.interaction_mode='assign_train' end
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
local line
for _,l in ipairs(printed) do if l:find('[TrainBay] refused hub=6430',1,true) then line=l end end
assert(line,'the refusal line names the hub')

-- A plain station: vanilla's archived body spawns exactly as before.
track:AssignTrain(plain)
assert(#city.labels.Train==1,'one train placed at the station')
local t=city.labels.Train[1]
assert(t.current_station==plain and t.at_spawn_track==true and t.started,'born at the station, at_spawn_track, started')
assert(t.pos=='pos:spot:Spawn1' and t.angle=='angle:spot:Spawn1','placed on the station\'s own Spawn spot')
assert(ColonyGetPrefabs('Train',city)==2 and track.assigned_vehicles[1]==t and plain.track_busy[1]==t)
assert(B.stats.refused==1,'the station path is not counted as a refusal')

-- The card: both buttons disabled with the reason; both presses do nothing on a hub.
local function button()
    local b={calls={}}
    function b:SetEnabled(v) self.enabled=v end
    function b:SetRolloverTitle(v) self.title=v end
    function b:SetRolloverText(v) self.text=v end
    function b:SetRolloverDisabledText(v) self.disabled_text=v end
    return b
end
local b1,b2=button(),button()
hub:ConstructTrain_Update(b1); hub:ToggleCreateRouteMode_Update(b2)
for _,b in ipairs({b1,b2}) do
    assert(b.enabled==false,'button disabled on the hub')
    assert(b.text:find('Train Station',1,true) and b.disabled_text==b.text,'the reason names the station')
end
assert(b1.title=='T14474:Construct Train' and b2.title=='T14381:Send out Train')
hub:ConstructTrain(1); hub:ToggleCreateRouteMode()
assert(hub.trains_in_construction==0 and hub.interaction_mode==nil,'presses do nothing on the hub')
-- A plain station keeps vanilla's behaviour for the same calls.
local b3=button(); plain:ToggleCreateRouteMode_Update(b3); assert(b3.enabled==true)
plain:ConstructTrain(1); plain:ToggleCreateRouteMode()
assert(plain.trains_in_construction==1 and plain.interaction_mode=='assign_train')
''')
print('PASS hub refusal: AssignTrain(hub) spawns nothing and spends nothing; AssignTrain(station) spawns on the '
      'station\'s own Spawn spot; both hub card buttons disabled with the reason; presses inert on the hub only', flush=True)
print('NOT RUN: engine rendering of the disabled buttons, the Transportation overview row, and a live spawn', flush=True)
