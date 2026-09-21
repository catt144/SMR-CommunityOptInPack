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
function P:Len() return math.floor(math.sqrt(self.x*self.x+self.y*self.y)+.5) end
function point(x,y,z) return setmetatable({x=x,y=y,z=z},P) end
guim=100; axis_y='axis_y'
function RGB(r,g,b) return r*65536+g*256+b end
function MulDivRound(a,b,c) return math.floor(a*b/c+.5) end
function HexRotate(q,r,d) for _=1,d do q,r=-r,q+r end return q,r end
function HexToWorld(q,r) return math.floor(1000*(q+r/2)+.5), math.floor(866*r+.5) end
function CalcOrientation(a,b) return math.floor(math.deg(math.atan(b.y-a.y,b.x-a.x))*60+.5) end
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
function PlaceObjectIn(c,map) return setmetatable({class=c,map=map},V) end
h=setmetatable({attached={},working=true},{__index=SMROptInTrainHubBase})
function h:GetAttaches(c)
 local out={} for _,v in ipairs(self.attached) do
  if IsValid(v) and v.class==c then out[#out+1]=v end
 end return out
end
function h:GetMap() return 1 end
function h:GetAngle() return 0 end
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
assert(old.offset.x==3897 and old.offset.y==2250 and old.offset.z==0)
foreign=PlaceObjectIn('ShapeshifterAutoAttach',1); foreign:ChangeEntity('ForeignVisual'); h:Attach(foreign,0)
-- Imported replacements, then repeated initialization: no duplicates or unrelated deletion.
available.SMROptInTrainHubReactor=true; available.SMROptInTrainHub6Glass=true
for i=1,2 do h:InitHubReactorVisual(); h:InitHubSidingGlass() end
assert(old.deleted and IsValid(foreign))
assert(#living('FusionReactor')==0)
assert(#living('SMROptInTrainHubReactor')==1 and #living('SMROptInTrainHub6Glass')==1)
reactor=living('SMROptInTrainHubReactor')[1]; glass=living('SMROptInTrainHub6Glass')[1]
assert(reactor.scale==75 and reactor.angle==210*60 and reactor.fx_actor_class=='FusionReactor')
assert(glass.offset.x==0 and glass.offset.y==0 and glass.offset.z==0)
for _,v in ipairs({reactor,glass}) do assert(v.delete_on_load and v.cleared==15 and v.spot==0) end
h:OnSetWorking(false)
assert(reactor.si==0 and glass.si==0 and reactor.fx_state=='end')
h:OnSetWorking(true)
assert(reactor.si==200 and glass.si==200 and reactor.fx_state=='start')
-- DeleteOnLoadGame's engine removal is mocked, then run the exact init path again.
DoneObject(reactor); DoneObject(glass); h:InitHubReactorVisual(); h:InitHubSidingGlass()
assert(#living('SMROptInTrainHubReactor')==1 and #living('SMROptInTrainHub6Glass')==1)
assert(IsValid(foreign))
-- Arm lights: 2*(28+14+42) on, destroyed (not dimmed) off, no duplicates on repeat, others untouched.
h:OnSetWorking(true); h:OnSetWorking(true)
assert(#lights()==168, #lights())
local spots,far=0,0
for _,v in ipairs(lights()) do
 assert(v.delete_on_load and v.spot==0 and v.detail=='Essential' and v.intensity>0 and v.offset.z>800)
 if v.class=='SpotLight' then spots=spots+1; assert(v.axis=='axis_y' and v.angle==90*60 and v.outer==120) end
 local d=math.sqrt(v.offset.x^2+v.offset.y^2); assert(d>=800 and d<=8100, d)
end
assert(spots==28)
h:OnSetWorking(false)
assert(#lights()==0 and IsValid(foreign) and #living('SMROptInTrainHubReactor')==1)
h.working=false; h:InitHubLights(); assert(#lights()==0)
h.working=true; h:InitHubLights(); assert(#lights()==168)
''')
print(json.dumps({'command':'python tools/devmods/train_hub/tests/look_smoke.py',
    'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'status':'PASS: mocked visual lifecycle; native game behavior untested',
    'cases':['missing imports','fallback replacement','idempotent init','foreign attachment preserved',
             'offset/scale/FX preserved','working on/off SI','recreate after mocked load deletion',
             'arm lights: 168 on, destroyed off, idempotent, foreign attachment preserved']}))
