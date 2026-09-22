"""Mocked visual lifecycle only: absent/present imports, replacement, SI and FX.
No claim about native rendering, importer UI, game attachment or save serialization.
"""
import json
from pathlib import Path
import subprocess

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'tools/devmods/train_hub/Code/20_TrainHub.lua'
code = SOURCE.read_text(encoding='utf8')
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
SMROptInTrainHubBase={}; empty_table={}
const={efCollision=1,efApplyToGrids=2,efWalkable=4,efSelectable=8}
local P={}; P.__index=P
function P:x() return self._x end
function P:y() return self._y end
function P:z() return self._z end
function P:Len() return math.floor(math.sqrt(self._x*self._x+self._y*self._y)+.5) end
P.__add=function(a,b) return point(a._x+b._x,a._y+b._y) end
function point(x,y,z) return setmetatable({_x=x,_y=y,_z=z},P) end
function Rotate(p,a) local r=math.rad(a/60); local c,s=math.cos(r),math.sin(r)
 return point(math.floor(p._x*c-p._y*s+.5), math.floor(p._x*s+p._y*c+.5)) end
weak_keys_meta={__mode='k'}; Floor={}; abs=math.abs; Min=math.min; Max=math.max
OnMsg={}
-- The map object the hub reports; vanilla publishes day/night on it as the MapVar
-- NightLightsState (Lua/NightLightObjects.lua:22,:337,:388, build 1.1.0.403908). Start by DAY.
MAP={NightLightsState=false}
function IsValidThread(t) return t and true or false end
threads=0; function CreateRealTimeThread() threads=threads+1; return {} end
function AllMapsForEach(_,_,f) f(h) end
guim=100; axis_y='axis_y'
function RGB(r,g,b) return r*65536+g*256+b end
function GetRGB(c) return math.floor(c/65536)%256, math.floor(c/256)%256, c%256 end
function Clamp(v,a,b) return math.max(a,math.min(b,v)) end
function MulDivRound(a,b,c) return math.floor(a*b/c+.5) end
function HexRotate(q,r,d) for _=1,d do q,r=-r,q+r end return q,r end
function HexToWorld(q,r) return math.floor(1000*(q+r/2)+.5), math.floor(866*r+.5) end
function CalcOrientation(a,b) return math.floor(math.deg(math.atan(b._y-a._y,b._x-a._x))*60+.5) end
function train_deck_height() return 800 end
function IsValid(o) return o and not o.deleted end
function IsKindOf(o,c) return o.class==c end
available={FusionReactor=true}
function IsValidEntity(e) return available[e] or false end
function DoneObject(o) o.deleted=true end
function DeleteOnLoadGame(o) o.delete_on_load=true end
function PlayFX(_,state,o) o.fx_state=state end
function top_up_hub_drones() end
local V={}; V.__index=V
function V:GetEntity() return self.entity end
function V:ChangeEntity(e) self.entity=e end
function V:ClearEnumFlags(f) self.cleared=f end
function V:HasState(s) return s=='idle' or self.entity=='FusionReactor' end
function V:SetState(s) self.state=s end
function V:SetAttachOffset(p) self.offset=p end
function V:SetAttachAngle(a) self.angle=a end
function V:SetScale(s) self.scale=s end
function V:SetSIModulation(s) self.si=s end
function V:SetDetailClass(d) self.detail=d end
function V:SetColor(c) self.color=c end
function V:SetIntensity(i) self.intensity=i end
function V:SetAttenuationRadius(r) self.radius=r end
function V:SetConeInnerAngle(a) self.inner=a end
function V:SetConeOuterAngle(a) self.outer=a end
function V:SetAttachAxis(a) self.axis=a end
local B={}; B.__index=B
function B:Center() return point((self[1]+self[3])/2,(self[2]+self[4])/2) end
function B:minx() return self[1] end; function B:miny() return self[2] end
function B:maxx() return self[3] end; function B:maxy() return self[4] end
function B:sizex() return self[3]-self[1] end; function B:sizey() return self[4]-self[2] end
function box(...) return setmetatable({...},B) end
function V:GetEntityBBox() return box(0,-200,200,240) end -- closed centre (100, 20)
function V:Open() self.opens=(self.opens or 0)+1 end
function V:Close() self.closes=(self.closes or 0)+1 end
function PlaceObjectIn(c,map) return setmetatable({class=c,map=map},V) end
h=setmetatable({attached={},working=true},{__index=SMROptInTrainHubBase})
function h:GetAttaches(c)
 local out={} for _,v in ipairs(self.attached) do
  if IsValid(v) and v.class==c then out[#out+1]=v end
 end return out
end
function h:GetMap() return MAP end
function h:GetAngle() return 0 end
function h:GetPosXYZ() return 0,0,0 end
h.city={labels={Train={}}}
print=function() end
function lights()
 local list={} for _,c in ipairs({'PointLight','SpotLight'}) do
  for _,v in ipairs(h:GetAttaches(c)) do list[#list+1]=v end
 end return list
end
function h:GetSpotBeginIndex(s) assert(s=='Origin' or s=='Pitrim', s); return s=='Pitrim' and 27 or 0 end
function h:HasSpot(s) return s=='Pitrim' end
function h:Attach(v,spot) v.spot=spot; self.attached[#self.attached+1]=v end
function h:GatherOrphanedDrones() end
function h:SetWaitingDronesIdle() end
function h:NotifyWorkingChanged() end
function living(entity)
 local list={} for _,v in ipairs(h:GetAttaches('ShapeshifterAutoAttach')) do
  if v.entity==entity then list[#list+1]=v end
 end return list
end
''')
visuals = code[code.index('local reactor_entity ='):code.index('-- A train station is normally')]
working = code[code.index('function SMROptInTrainHubBase:OnSetWorking('):code.index('-- Done is combined.')]
lua.execute(visuals + '\n' + working)
lua.execute(r'''
-- Before editor import, the existing visual survives and no missing entity is made.
h:InitHubReactorVisual(); h:InitHubSidingGlass()
assert(#living('FusionReactor')==1 and #living('SMROptInTrainHub6Glass')==0)
old=living('FusionReactor')[1]
assert(old.scale==75 and old.angle==210*60)
assert(old.offset:x()==3897 and old.offset:y()==2250 and old.offset:z()==0)
foreign=PlaceObjectIn('ShapeshifterAutoAttach',1); foreign:ChangeEntity('ForeignVisual'); h:Attach(foreign,0)
-- Imported replacements, then repeated initialization: no duplicates or unrelated deletion.
available.SMROptInTrainHubReactor=true; available.SMROptInTrainHub6Glass=true
for i=1,2 do h:InitHubReactorVisual(); h:InitHubSidingGlass() end
assert(old.deleted and IsValid(foreign))
assert(#living('FusionReactor')==0)
assert(#living('SMROptInTrainHubReactor')==1 and #living('SMROptInTrainHub6Glass')==1)
reactor=living('SMROptInTrainHubReactor')[1]; glass=living('SMROptInTrainHub6Glass')[1]
assert(reactor.scale==75 and reactor.angle==210*60 and reactor.fx_actor_class=='FusionReactor')
assert(glass.offset:x()==0 and glass.offset:y()==0 and glass.offset:z()==0)
for _,v in ipairs({reactor,glass}) do assert(v.delete_on_load and v.cleared==15 and v.spot==0) end
h:OnSetWorking(false)
assert(reactor.si==0 and glass.si==0 and reactor.fx_state=='end')
h:OnSetWorking(true)
assert(reactor.si==200 and glass.si==200 and reactor.fx_state=='start')
-- DeleteOnLoadGame's engine removal is mocked, then run the exact init path again.
DoneObject(reactor); DoneObject(glass); h:InitHubReactorVisual(); h:InitHubSidingGlass()
assert(#living('SMROptInTrainHubReactor')==1 and #living('SMROptInTrainHub6Glass')==1)
assert(IsValid(foreign))
-- Arm lights: 6*12 on (the owner's pick, B2 spots, on every arm), along the painted line's path, destroyed (not dimmed) off, no duplicates on repeat, others untouched.
h:OnSetWorking(true); h:OnSetWorking(true)
function set(k) return Floor.HubLightSet(h)[k] end
function n(k) return #set(k) end
assert(n('arm')==72, n('arm'))
local spots=0
for _,v in ipairs(set('arm')) do
 assert(v.delete_on_load and v.spot==0 and v.detail=='Essential' and v.intensity==50 and v.radius==500 and v.offset:z()>800)
 if v.class=='SpotLight' then spots=spots+1; assert(v.axis=='axis_y' and v.angle==90*60 and v.outer==100) end
 local d=math.sqrt(v.offset:x()^2+v.offset:y()^2); assert(d>=800 and d<=8100, d)
end
assert(spots==72)
-- Structure lights: portal and pit on, the ring rim and the floor edge off by default (owner, 2026-09-22).
assert(n('portal')==30 and n('pit')==0 and n('rim')==0 and n('floor')==0)
assert(#lights()==102, #lights())
Floor.SetHubStructureLights{rim={on=true},pit={on=true}}; assert(n('rim')==36 and n('pit')==6 and #lights()==144)
for _,v in ipairs(set('portal')) do
 assert(v.class=='PointLight' and v.delete_on_load and v.spot==0 and v.detail=='Essential' and v.intensity==4)
 local d=math.sqrt(v.offset:x()^2+v.offset:y()^2)
 assert(d>=2868 and d<=3353, d)                      -- on the flush rim's radial span
 assert(v.offset:z()>=860 and v.offset:z()<=1272)    -- inside the mouth, 0.40 m under the crown
end
for _,v in ipairs(set('rim')) do
 assert(v.intensity==12 and v.offset:z()==690)
 assert(math.abs(math.sqrt(v.offset:x()^2+v.offset:y()^2)-3610)<=1)
end
local pc=point(0,0) -- hung on the Pitrim spot, so the kerb circle is about the spot itself
for _,v in ipairs(set('pit')) do
 assert(v.intensity==15 and v.offset:z()==30 and v.spot==27)
 assert(math.abs(math.sqrt((v.offset:x()-pc:x())^2+(v.offset:y()-pc:y())^2)-590)<=1)
end
-- The live arm tune: same count, re-init, and every light moved by `side` and recoloured.
local was={} for i,v in ipairs(set('arm')) do was[i]={v.offset:x(),v.offset:y()} end
Floor.SetHubLightTune{side=300,intensity=80,radius=7*guim,color=RGB(0,0,200)}
assert(n('arm')==72 and #lights()==144)
local moved=0
for i,v in ipairs(set('arm')) do
 assert(v.intensity==80 and v.radius==700 and v.color==RGB(0,0,200) and v.outer==100)
 if v.offset:x()~=was[i][1] or v.offset:y()~=was[i][2] then moved=moved+1 end
end
assert(moved==72, moved)
Floor.SetHubLightTune('side',150); Floor.SetHubLightTune{intensity=50,radius=5*guim,color=RGB(0,40,255)}
for i,v in ipairs(set('arm')) do assert(v.offset:x()==was[i][1] and v.offset:y()==was[i][2] and v.intensity==50) end
-- Every structure family is off-able, and the floor edge strip is on-able, without an import.
Floor.SetHubStructureLights{portal={on=false},pit={on=false},rim={on=false}}
assert(n('portal')==0 and n('pit')==0 and n('rim')==0 and #lights()==72)
Floor.SetHubStructureLights{floor={on=true}}
assert(n('floor')==24 and #lights()==96)
for _,v in ipairs(set('floor')) do assert(v.intensity==30 and v.offset:z()==45) end
Floor.SetHubStructureLights{portal={on=true},pit={on=true},rim={on=true},floor={on=false}}
assert(#lights()==144 and n('floor')==0)
-- Destroyed (not dimmed) when the hub stops, recreated on, idempotent, nothing else touched.
h:OnSetWorking(false)
assert(#lights()==0 and Floor.HubLightSet(h)==nil and IsValid(foreign) and #living('SMROptInTrainHubReactor')==1)
h.working=false; h:InitHubLights(); assert(#lights()==0)
h.working=true; h:InitHubLights(); h:InitHubLights(); assert(#lights()==144, #lights())
assert(n('arm')==72 and n('portal')==30 and n('pit')==6 and n('rim')==36)
assert(IsValid(foreign))
-- The crown floor light rides the VANILLA night schedule: our OnMsg.LightmodelChange handler sits
-- beside the game's own (Lua/NightLightObjects.lua:250-259, build 1.1.0.403908) and compares the
-- same two booleans. Everything above ran by DAY, so the crown was absent throughout.
assert(n('crown')==0, n('crown'))
OnMsg.LightmodelChange(MAP,false,{night=false},0,{night=false}) -- no transition: no rebuild
assert(n('crown')==0 and #lights()==144)
-- Dusk, fired the vanilla way.
MAP.NightLightsState=true
OnMsg.LightmodelChange(MAP,false,{night=true},0,{night=false})
assert(n('crown')==1, n('crown'))
assert(#lights()==145 and n('arm')==72 and n('portal')==30 and n('pit')==6 and n('rim')==36)
crown=set('crown')[1]
assert(crown.class=='SpotLight' and crown.delete_on_load and crown.spot==0 and crown.detail=='Essential')
assert(crown.color==RGB(255,214,170) and crown.intensity==60 and crown.radius==35*guim)
assert(crown.inner==50 and crown.outer==90)
assert(crown.axis=='axis_y' and crown.angle==90*60)          -- the arm spots' aim, reused: straight down
assert(crown.offset:x()==0 and crown.offset:y()==0 and crown.offset:z()==1900) -- the dome axis, 19.00 m
-- Idempotent at night, and tunable/off-able through the existing console entry point.
h:InitHubLights(); h:InitHubLights(); assert(n('crown')==1 and #lights()==145)
Floor.SetHubStructureLights{crown={intensity=90,height=1850,color=RGB(255,200,150),outer=120}}
assert(n('crown')==1)
crown=set('crown')[1]
assert(crown.intensity==90 and crown.offset:z()==1850 and crown.color==RGB(255,200,150) and crown.outer==120)
Floor.SetHubStructureLights{crown={on=false}}; assert(n('crown')==0 and #lights()==144)
Floor.SetHubStructureLights{crown={on=true,intensity=60,height=1900,color=RGB(255,214,170),outer=90}}
assert(n('crown')==1 and #lights()==145)
-- A stopped hub destroys it with the rest; running again rebuilds it.
h:OnSetWorking(false); assert(#lights()==0 and Floor.HubLightSet(h)==nil)
h:OnSetWorking(true); assert(n('crown')==1 and #lights()==145)
night_counts={crown=n('crown'),total=#lights()}
-- Dawn, the same Msg the other way: the crown goes, nothing else moves.
MAP.NightLightsState=false
OnMsg.LightmodelChange(MAP,false,{night=false},0,{night=true})
assert(n('crown')==0 and #lights()==144 and n('arm')==72 and n('portal')==30 and n('rim')==36)
-- Another map's dusk/dawn does not switch this hub: the override is keyed by map, and a hub
-- elsewhere falls back to its own MapVar.
MAP.NightLightsState=true; h:InitHubLights(); assert(n('crown')==1)
OnMsg.LightmodelChange({},false,{night=false},0,{night=true})
assert(n('crown')==1, n('crown'))
MAP.NightLightsState=false; h:InitHubLights(); assert(n('crown')==0 and #lights()==144)
counts={arm=n('arm'),portal=n('portal'),pit=n('pit'),rim=n('rim'),floor=n('floor'),
        crown_day=n('crown'),crown_night=night_counts.crown,
        total_day=#lights(),total_night=night_counts.total,total=#lights()}
''')
counts = {k: v for k, v in dict(lua.globals().counts).items()}
print(json.dumps({'command':'python tools/devmods/train_hub/tests/look_smoke.py',
    'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'status':'PASS: mocked visual lifecycle; native game behavior untested',
    'counts':counts,
    'cases':['missing imports','fallback replacement','idempotent init','foreign attachment preserved',
             'offset/scale/FX preserved','working on/off SI','recreate after mocked load deletion',
             'arm lights: 72 on, destroyed off, idempotent, foreign attachment preserved',
             'arm tune: defaults, re-init keeps 72, side moves all 72, intensity/radius/colour applied, reset restores offsets',
             'structure lights: portal 30 on by default; pit 6 (on the Pitrim spot), rim 36 and floor 24 off by default; 102 default, 144 with rim and pit',
             'structure lights: on the rim span, the kerb circle and the ring radius, at their z',
             'structure lights: every family off-able to 0, floor edge on-able to 24, destroyed off and recreated on',
             'crown floor light: absent all through the day pass; 1 at night on the dome axis (0,0,1900), SpotLight aimed down like the arm spots, RGB(255,214,170), intensity 60, radius 3500 cm, cone 50/90',
             'crown floor light: the vanilla night hook fired both ways -- Msg LightmodelChange day->night places it, night->day destroys it, a no-transition fire rebuilds nothing',
             "crown floor light: another map's LightmodelChange does not switch this hub",
             'crown floor light: idempotent at night, tunable and off-able via SetHubStructureLights, destroyed by OnSetWorking(false) and recreated by (true)']}))
