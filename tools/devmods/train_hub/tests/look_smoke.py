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
function IsValidThread(t) return t and true or false end
threads=0; function CreateRealTimeThread() threads=threads+1; return {} end
function AllMapsForEach(_,_,f) f(h) end
guim=100; axis_y='axis_y'
function RGB(r,g,b) return r*65536+g*256+b end
function Clamp(v,a,b) return math.max(a,math.min(b,v)) end
function MulDivRound(a,b,c) return math.floor(a*b/c+.5) end
function HexRotate(q,r,d) for _=1,d do q,r=-r,q+r end return q,r end
function HexToWorld(q,r) return math.floor(1000*(q+r/2)+.5), math.floor(866*r+.5) end
function CalcOrientation(a,b) return math.floor(math.deg(math.atan(b._y-a._y,b._x-a._x))*60+.5) end
function train_deck_height() return 800 end
function IsValid(o) return o and not o.deleted end
function IsKindOf(o,c) return o.class==c end
available={FusionReactor=true,MarsAssembly_Door_01=true,TunnelEntranceDoor=true}
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
function h:GetMap() return 1 end
function h:GetAngle() return 0 end
function h:GetPosXYZ() return 0,0,0 end
h.city={labels={Train={}}}
print=function() end
function lights()
 local list={} for _,c in ipairs({'PointLight','SpotLight'}) do
  for _,v in ipairs(h:GetAttaches(c)) do list[#list+1]=v end
 end return list
end
function h:GetSpotBeginIndex(s) assert(s=='Origin'); return 0 end
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
assert(#lights()==72, #lights())
local spots,far=0,0
for _,v in ipairs(lights()) do
 assert(v.delete_on_load and v.spot==0 and v.detail=='Essential' and v.intensity==130 and v.offset:z()>800)
 if v.class=='SpotLight' then spots=spots+1; assert(v.axis=='axis_y' and v.angle==90*60 and v.outer==100) end
 local d=math.sqrt(v.offset:x()^2+v.offset:y()^2); assert(d>=800 and d<=8100, d)
 if d>6000 then far=far+1 end
end
assert(spots==72)
h:OnSetWorking(false)
assert(#lights()==0 and IsValid(foreign) and #living('SMROptInTrainHubReactor')==1)
h.working=false; h:InitHubLights(); assert(#lights()==0)
h.working=true; h:InitHubLights(); assert(#lights()==72)
-- Portal doors: 6 on, 0 off, idempotent, foreign attachment untouched, placed on the plane turned round.
function doors() return h:GetAttaches('MarsAssembly_Door_01') end
h:OnSetWorking(true); h:OnSetWorking(true)
assert(#doors()==6, #doors())
assert(threads>=1)
for _,d in ipairs(doors()) do
 assert(d.delete_on_load and d.spot==0 and d.detail=='Essential' and d.scale==184 and d.cleared==15 and d.offset:z()==800)
 assert(not d.opens and not d.closes)
end
local d0 -- direction 0 is +X: angle 0, turned to 180 deg; leaf centre (100,20)*1.84 -> (184,37) turned -> (-184,-37)
for _,d in ipairs(doors()) do if d.angle==180*60 then d0=d end end
assert(d0 and d0.offset:x()==3475+184 and d0.offset:y()==37, d0 and d0.offset:x())
for _,d in ipairs(doors()) do local r=math.sqrt(d.offset:x()^2+d.offset:y()^2); assert(r>3600 and r<3700, r) end
h:OnSetWorking(false); assert(#doors()==0 and IsValid(foreign))
h:OnSetWorking(true); assert(#doors()==6)
-- A 30 m train on line 0, heading in: the body reaches the band, only door 0 opens, once.
local T={}; T.__index=T
function T:GetEntityBBox() return box(-1500,-200,1500,200) end
function T:GetVisualPos2D() return point(self.at,self.side or 0) end
function T:GetVisualAngle() return 180*60 end
train=setmetatable({at=6000},T); h.city.labels.Train={train}
for _,d in ipairs(doors()) do if d.angle==180*60 then d0=d end end
Floor.UpdateHubDoors(h,1000); Floor.UpdateHubDoors(h,1100)
assert(d0.opens==1 and not d0.closes)
for _,d in ipairs(doors()) do if d~=d0 then assert(not d.opens) end end
-- Through the door to the centre: held for HubDoorHoldTime, then closed exactly once.
train.at=0; Floor.UpdateHubDoors(h,2000); assert(not d0.closes)
Floor.UpdateHubDoors(h,1100+Floor.HubDoorHoldTime); assert(d0.closes==1)
Floor.UpdateHubDoors(h,9000); assert(d0.closes==1)
-- A train on a track beside line 0 (15 m off it) opens nothing.
train.at=5000; train.side=1500; Floor.UpdateHubDoors(h,10000); assert(d0.opens==1)
for _,d in ipairs(doors()) do if d~=d0 then assert(not d.opens) end end
-- Opened again, then the train is destroyed mid-transit: the door closes after the hold.
train.side=0; train.at=4000; Floor.UpdateHubDoors(h,20000); assert(d0.opens==2 and d0.closes==1)
train.deleted=true; Floor.UpdateHubDoors(h,20100); assert(d0.closes==1)
Floor.UpdateHubDoors(h,20000+Floor.HubDoorHoldTime); assert(d0.closes==2)
-- Save/load mid-open: the engine removes the doors, the init path recreates them closed.
train.deleted=false; Floor.UpdateHubDoors(h,30000); assert(d0.opens==3)
for _,d in ipairs(doors()) do DoneObject(d) end
h:InitHubDoors(); assert(#doors()==6)
for _,d in ipairs(doors()) do assert(not d.opens and not d.closes) end
-- The second style switches from the console with no import; the first is removed.
Floor.SetHubDoorStyle('shutter'); assert(#doors()==0 and #h:GetAttaches('TunnelEntranceDoor')==6)
for _,d in ipairs(h:GetAttaches('TunnelEntranceDoor')) do assert(d.scale==81 and d.angle%(60*60)==0) end
Floor.SetHubDoorStyle('glass'); assert(#doors()==6 and #h:GetAttaches('TunnelEntranceDoor')==0 and IsValid(foreign))
''')
print(json.dumps({'command':'python tools/devmods/train_hub/tests/look_smoke.py',
    'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'status':'PASS: mocked visual lifecycle; native game behavior untested',
    'cases':['missing imports','fallback replacement','idempotent init','foreign attachment preserved',
             'offset/scale/FX preserved','working on/off SI','recreate after mocked load deletion',
             'arm lights: 72 on, destroyed off, idempotent, foreign attachment preserved',
             'doors: 6 on, 0 off, idempotent, foreign preserved, on the 34.75 m plane turned round',
             'doors: mocked passing train opens its portal only, once; closes once after the hold',
             'doors: train off the line opens nothing; destroyed mid-transit closes; recreated closed after mocked load',
             'doors: second style by console knob, no import']}))
