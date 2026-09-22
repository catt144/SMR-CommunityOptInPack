"""Execute the flight Lua against a deterministic physical graph and clock.

No game/render/import/clearance evidence. Requires lupa, as the adjacent smokes do.
Only opens L2's own source; the hub implementation belongs to L4.
"""
import json
from pathlib import Path
import subprocess

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "tools/devmods/train_hub/Code/30_TrainHubDrones.lua"
metadata = (ROOT / "tools/devmods/train_hub/metadata.lua").read_text(encoding="utf8")
assert metadata.count('"Code/30_TrainHubDrones.lua"') == 1, "Flight code registration missing or duplicated"
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
OnMsg = {}; empty_table = {}; clock = 0; created = 0; removed = 0
Min=math.min; Max=math.max
function Clamp(v,a,b) return Max(a,Min(b,v)) end
function MulDivRound(a,b,c) return math.floor(a*b/c+.5) end
local P={}; P.__index=P
function point(x,y,z) return setmetatable({X=x,Y=y,Z=z},P) end
function P:x() return self.X end; function P:y() return self.Y end; function P:z() return self.Z end
P.__add=function(a,b) return point(a.X+b.X,a.Y+b.Y,a.Z+b.Z) end
P.__sub=function(a,b) return point(a.X-b.X,a.Y-b.Y,a.Z-b.Z) end
function P:Dist(b) return math.floor(math.sqrt((self.X-b.X)^2+(self.Y-b.Y)^2+(self.Z-b.Z)^2)+.5) end
function GameTime() return clock end
function IsValid(o) return type(o)=='table' and o.valid and not o.deleted end
function IsBeingDestructed(o) return o and o.destructing end
function IsKindOf(o,c) return o and o.class==c end
function Untranslated(s) return s end
function CalcOrientation(a,b) return math.deg(math.atan(b.Y-a.Y,b.X-a.X))*60 end
function CreateRealTimeThread(fn) return {fn=fn} end
function IsValidThread(t) return t and not t.deleted end
function DeleteThread(t) if t then t.deleted=true end end
function DoneObject(o) assert(not o.deleted); o.deleted=true; removed=removed+1 end
function GetEntitySpotPos(_,idx) return idx==0 and point(-1000,-577,-2000) or point(-1000,-577,30) end
local O={}; O.__index=O
function obj(x,y,z) return setmetatable({valid=true,pos=point(x,y,z or 0),connectors={}},O) end
function O:GetPos() return self.pos end
function O:GetVisualPos() return self.pos end
function O:GetEntity() return self.entity or 'rail' end
function O:GetMap() return 1 end
function O:GetRelativePoint(p)
  local angle=(self.angle or 0)*math.pi/180
  local scale=(self.scale or 100)/100
  return self.pos+point(math.floor((p.X*math.cos(angle)-p.Y*math.sin(angle))*scale+.5),
    math.floor((p.X*math.sin(angle)+p.Y*math.cos(angle))*scale+.5),p.Z*scale)
end
function O:GetSpotBeginIndex(name)
  if self.missing then return -1 end
  return (name=='Pitfloor' or name=='Enter1') and 0 or 1
end
function O:GetSpotPos(idx)
  if self.entity=='SMROptInTrainHub6' then return self:GetRelativePoint(GetEntitySpotPos(self.entity,idx)) end
  return self.pos+point(idx*100,0,0)
end
function O:ForEachConnectorElement(fn) for _,el in ipairs(self.connectors) do fn(el) end end
function O:GetConnectorElement() return self.connectors[1] end
function O:GetInnerTrackElement() return self.inner end
function O:GetStartStation() return self.start_el.station end
function O:GetEndStation() return self.end_el.station end
function O:SetPos(p) self.pos=p end
function O:SetAngle(a) self.angle=a end
function O:SetState(s) self.state=s end
function O:SetVisible(v) self.visible=v end
function O:TakeOff() self:SetState('fly') end
function O:LandingEnd() self:SetState('idle') end
function O:GetAnimDuration(s) return s=='constructStart' and 400 or 600 end
function O:StartFX(f,t) self.fx=f; self.fx_target=t end
function O:StopFX() self.fx=false end
FlyingDrone={}
function FlyingDrone:new(params,map)
  assert(params.init_with_command==false and map==1)
  local d=obj(0,0)
  for k,v in pairs(params) do d[k]=v end
  created=created+1
  return d
end
Building={SetPalette=function(d,...) d.palette={...} end}
function hub(x,y)
  local h=obj(x or 0,y or 0); h.city={}; h.entity='SMROptInTrainHub6'; return h
end
function track(a,b,points)
  local t=obj(0,0); t.elements={}; t.elements_under_construction={}
  for i,p in ipairs(points) do
    local el=obj(p[1],p[2],p[3]); el.node_idx=i; el.track_obj=t; t.elements[i]=el
  end
  t.start_el=t.elements[1]; t.end_el=t.elements[#t.elements]
  t.start_el.station=a; t.end_el.station=b
  a.connectors[#a.connectors+1]=t.start_el; b.connectors[#b.connectors+1]=t.end_el
  return t
end
function tick(t) clock=t; SMROptInHubFlight.Sample() end
''')
lua.execute(SOURCE.read_text(encoding="utf8"))
lua.execute(r'''
F=SMROptInHubFlight
h=hub(); s=obj(20000,0); f=obj(40000,0)
t1=track(h,s,{{0,0},{10000,0},{20000,0}})
t2=track(s,f,{{20000,0},{30000,0},{40000,0}})
-- Breaks retain their originals. The site has no ordered node index.
cs=obj(10000,0); cs.is_construction_site=true; cs.track_obj=t1
cs.broken=t1.elements[2]; t1.elements[2].broken=cs; t1.elements_under_construction={cs}
path=assert(F.Route(h,t2.elements[2])); assert(#path==6)
assert(F.Route(h,cs)[3].owner==t1.elements[2])
-- A cycle terminates; an isolated component cannot be reached.
loop=track(f,h,{{40000,0},{20000,20000},{0,0}})
outside=obj(60000,0); other=obj(80000,0)
isolated=track(outside,other,{{60000,0},{80000,0}})
assert(F.Route(h,isolated.elements[1])==nil)
-- Missing/unfinished inputs fail safely, without mutating the track arrays.
local order=t1.elements[1]; t1.elements_under_construction={obj(3,4)}
assert(F.Route(h,cs)==nil); assert(t1.elements[1]==order)
t1.elements_under_construction={cs}
h.missing=true; assert(SpawnHubDrone(h)==nil); h.missing=false
-- Live spot transforms honour scale and rotation.
h.angle=90; h.scale=150
pit=assert(F.PitPoints(h)); assert(pit[1].Z==-3000 and pit[3].Z==1500)
assert(math.abs(pit[1].X-595.5)<=.5 and pit[1].Y==-1965)
h.angle=0; h.scale=100
drone=assert(SpawnHubDrone(h)); assert(created==1)
assert(SpawnHubDrone(h)==drone and created==1)
tick(1500); assert(drone.pos.Z>-2000 and drone.pos.Z<1000)
assert(ReturnHubDrone()==drone); deadline=F.Status().removed
assert(deadline==3000); assert(ReturnHubDrone()==drone)
tick(deadline); assert(not F.Status() and drone.deleted)
-- Fresh full trip: exact deadline, direct work visuals, full battery, return cleanup.
clock=10000; drone,status=SendHubDroneTo(cs,h)
assert(drone and status.arrival>clock+F.LaunchTime)
assert(SendHubDroneTo(cs,h)==drone)
arrival=status.arrival; completed=status.work_done; finished=status.removed
assert(completed-arrival==6000)
drone.battery=1; tick(arrival); assert(drone.battery==F.BatteryMax)
assert(drone.state=='constructStart' and drone.fx=='Construct')
tick(arrival+400); assert(drone.state=='constructIdle')
tick(arrival+5400); assert(drone.state=='constructEnd' and not drone.fx)
tick(completed); assert(drone.state=='fly')
assert(ReturnHubDrone()==drone and F.Status().removed==finished)
tick(finished); assert(drone.deleted and not F.Status())
measured_arrival=arrival-10000; measured_work=completed-10000; measured_total=finished-10000
-- Reciprocal tunnel path is timed and hidden in both directions.
h2=hub(0,100000); near=obj(20000,100000); far=obj(70000,100000); dest=obj(90000,100000)
near.class='TrackTunnelBase'; far.class='TrackTunnelBase'; near.linked_obj=far; far.linked_obj=near
near.inner=obj(21000,100000); far.inner=obj(69000,100000)
a=track(h2,near,{{0,100000},{20000,100000}})
b=track(far,dest,{{70000,100000},{80000,100000},{90000,100000}})
tp=assert(F.Route(h2,b.elements[2])); hidden=0
for _,p in ipairs(tp) do if p.hidden then hidden=hidden+1 end end
assert(hidden==1)
far.linked_obj=false; assert(F.Route(h2,b.elements[2])==nil); far.linked_obj=near
clock=100000; drone,status=SendHubDroneTo(b.elements[2],h2)
local outbound_hidden,inbound_hidden=false,false
for tm=clock,status.removed,50 do
  tick(tm)
  if F.Status() and drone.visible==false then
    if tm<status.arrival then outbound_hidden=true else inbound_hidden=true end
  end
end
assert(outbound_hidden and inbound_hidden)
tick(status.removed); assert(not F.Status())
-- Manual interruption inside a tunnel remains hidden, then emerges onto the same route.
clock=200000; drone,status=SendHubDroneTo(b.elements[2],h2)
local hidden_at
for tm=clock,status.arrival,20 do tick(tm); if drone.visible==false then hidden_at=tm; break end end
assert(hidden_at); tick(hidden_at+1000); ReturnHubDrone(); tick(hidden_at+1020); assert(drone.visible==false)
tick(F.Status().removed); assert(not F.Status())
-- Save race gate: even clock advancement cannot respawn; failed save Done releases it.
clock=300000; drone=SpawnHubDrone(h); OnMsg.SaveGameStart()
assert(drone.deleted and not F.Status()); assert(SpawnHubDrone(h)==nil)
tick(clock+10000); assert(SendHubDroneTo(cs,h)==nil)
OnMsg.SaveGameDone(); drone=assert(SpawnHubDrone(h))
OnMsg.LoadGame(); assert(drone.deleted and not F.Status())
-- Controller loss, death and removal are scoped to the prototype object.
drone=SpawnHubDrone(h); drone.command_center=s; tick(clock+1); assert(drone.deleted)
drone=SpawnHubDrone(h); drone.command='GoHome'; tick(clock+1); assert(drone.deleted)
drone=SpawnHubDrone(h); h.destroyed=true; tick(clock+1); assert(drone.deleted); h.destroyed=false
assert(SetHubDroneTune('Speed',9000)); assert(not SetHubDroneTune('Speed',0))
assert(not SetHubDroneTune('PitOffsetX',1))
drone=SpawnHubDrone(h); assert(not SetHubDroneTune('Speed',6000))
OnMsg.DoneGame(); assert(drone.deleted and not F.Status())
-- L4's independent records can be sampled from an absolute start without restarting.
clock=400000; F.Speed=6000
r1=assert(F.Create(h,clock-4000)); r2=assert(F.Create(h,clock-4000))
assert(F.Send(r1,cs,true)); assert(F.Send(r2,cs,true))
assert(r1.arrival==clock+923 and r2.arrival==r1.arrival)
assert(F.Update(r1,clock) and F.Update(r2,clock)); assert(r1.drone.pos:Dist(r2.drone.pos)==0)
OnMsg.SaveGameStart(); assert(r1.drone.deleted and r2.drone.deleted)
assert(F.Create(h)==nil); OnMsg.SaveGameDone()
assert(created==removed)
''')
g = lua.globals()
result = {
    "command": "python tools/devmods/train_hub/tests/flight_smoke.py",
    "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "source_sha256": __import__("hashlib").sha256(SOURCE.read_bytes()).hexdigest(),
    "scope": "mocked Lua only; no native flight, clearance, import or save serialization claim",
    "result": "PASS",
    "fixture_game_ms": {"arrival": g.measured_arrival, "work_done": g.measured_work, "removed": g.measured_total},
    "visuals_created": g.created,
    "visuals_removed": g.removed,
}
print(json.dumps(result, indent=2))
