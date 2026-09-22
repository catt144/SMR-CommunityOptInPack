"""Execute the flight Lua against a deterministic physical graph and clock.

No game/render/import/clearance evidence. Requires lupa, as the adjacent smokes do.
Only opens L2's own source; the hub implementation belongs to L4.
"""
import json
import argparse
import hashlib
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
function O:SetPos(p,time) self.pos=p; self.pos_time=time or 0 end
function O:SetAngle(a) self.angle=a end
function O:GetAngle() return self.angle or 0 end
function O:SetCurvature(value) assert(value==false); self.curvature=value end
function O:SetAcceleration(value) assert(value==0) end
function O:SetRollPitchYaw(roll,pitch,yaw,time)
  assert(time>0 and pitch==0 and math.abs(roll)<=SMROptInHubFlight.BankAngle)
  self.angle=yaw; self.roll=roll; self.turn_time=time
end
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
path=assert(F.Route(h,t2.elements[2]))
local rails={}
for _,node in ipairs(path) do
  if node.owner and node.owner.node_idx and node.pos.Z==F.OverTrackHeight+F.HoverHeight then
    rails[#rails+1]=node.owner
  end
end
assert(#rails==5 and rails[1]==t1.elements[1] and rails[5]==t2.elements[2])
local repair_path=assert(F.Route(h,cs))
assert(repair_path[#repair_path].owner==t1.elements[2])
assert(repair_path[#repair_path].pos.Z==F.FixHeight)
-- No portal shortcut: fixed column -> low outward leg -> outside vertical climb,
-- then high transfer to the first rail, centreline cruise, and site-only descent.
assert(path[1].pos.Z==F.PitExitZ and path[2].pos.Z==F.UnderDeckHeight)
assert(path[3].pos.Z==F.UnderDeckHeight and path[4].pos.Z==F.TransferHeight)
assert(path[3].pos.X==path[4].pos.X and path[3].pos.Y==path[4].pos.Y)
assert(math.sqrt(path[3].pos.X^2+path[3].pos.Y^2)>8900)
assert(path[1].pos.X==path[2].pos.X and path[1].pos.Y==path[2].pos.Y)
assert(path[6].pos.Z>=F.TransferHeight)
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
assert(pit[4].Z==450 and pit[5].Z==450 and pit[6].Z==3750)
assert(pit[5].X==6750 and pit[5].Y==-11691)
h.angle=0; h.scale=100
drone=assert(SpawnHubDrone(h)); assert(created==1)
assert(SpawnHubDrone(h)==drone and created==1)
tick(1500); assert(drone.pos.Z>-2000 and drone.pos.Z<1000)
assert(ReturnHubDrone()==drone); deadline=F.Status().removed
assert(deadline>3000); assert(ReturnHubDrone()==drone)
tick(deadline); assert(not F.Status() and drone.deleted)
-- Fresh full trip: exact deadline, direct work visuals, full battery, return cleanup.
clock=10000; drone,status=SendHubDroneTo(cs,h)
assert(drone and status.arrival>clock+F.LaunchTime)
assert(SendHubDroneTo(cs,h)==drone)
arrival=status.arrival; completed=status.work_done; finished=status.removed
assert(completed-arrival==6000)
drone.battery=1; tick(arrival); assert(drone.battery==F.BatteryMax)
assert(drone.state=='constructStart' and drone.fx=='Construct')
assert(drone.pos.X==cs.pos.X and drone.pos.Y==cs.pos.Y and drone.pos.Z==F.FixHeight)
tick(arrival+400); assert(drone.state=='constructIdle')
tick(arrival+5400); assert(drone.state=='constructEnd' and not drone.fx)
tick(completed); assert(drone.state=='fly')
assert(ReturnHubDrone()==drone and F.Status().removed==finished)
tick(finished); assert(drone.deleted and not F.Status())
measured_arrival=arrival-10000; measured_work=completed-10000; measured_total=finished-10000
assert(measured_arrival==10981 and measured_work==16981 and measured_total==27962)
-- Recall while beneath the deck must retrace the low lane before the pit column.
clock=50000; drone,status=SendHubDroneTo(cs,h)
local low_at
for tm=clock,status.arrival,20 do
  tick(tm)
  if drone.pos.Z==F.UnderDeckHeight and drone.pos.X < -2000 then low_at=tm; break end
end
assert(low_at); local farthest=drone.pos.X
ReturnHubDrone(); local recalled=F.Status().removed
for tm=low_at+20,recalled,20 do
  tick(tm)
  if F.Status() then
    -- Recall may first brake along the curve; its full path is the flown lane.
    assert(drone.pos.X>=farthest-F.Speed*F.AccelTime/1000)
    if drone.pos.X < -1310-F.TurnRadius then assert(drone.pos.Z==F.UnderDeckHeight) end
  end
end
tick(recalled); assert(drone.deleted and not F.Status())
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
for _,name in ipairs({'UnderDeckHeight','OutwardDistance','ClimbRate','OverTrackHeight','FixHeight','TransferHeight','HoverHeight'}) do
  assert(SetHubDroneTune(name,F[name]))
end
assert(not SetHubDroneTune('PitOffsetX',1))
drone=SpawnHubDrone(h); assert(not SetHubDroneTune('Speed',6000))
OnMsg.DoneGame(); assert(drone.deleted and not F.Status())
-- L4's independent records can be sampled from an absolute start without restarting.
clock=400000; F.Speed=6000
r1=assert(F.Create(h,clock-4000)); r2=assert(F.Create(h,clock-4000))
assert(F.Send(r1,cs,true)); assert(F.Send(r2,cs,true))
assert(r1.arrival==clock-4000+measured_arrival and r2.arrival==r1.arrival)
-- Full return reverses every movement, including the site climb and the low exit.
local movements={}
for _,s in ipairs(r1.plan) do if s.state=='fly' then movements[#movements+1]=s end end
assert(#movements%2==0)
for i=1,#movements/2 do
  local a,b=movements[i],movements[#movements+1-i]
  assert(a.a:Dist(b.b)==0 and a.b:Dist(b.a)==0)
  if not a.pit then assert(a.finish-a.start>=MulDivRound(math.abs(a.b.Z-a.a.Z),1000,F.ClimbRate)) end
end
assert(F.Update(r1,clock) and F.Update(r2,clock)); assert(r1.drone.pos:Dist(r2.drone.pos)==0)
OnMsg.SaveGameStart(); assert(r1.drone.deleted and r2.drone.deleted)
assert(F.Create(h)==nil); OnMsg.SaveGameDone()
assert(created==removed)
''')
lua.execute(r'''
-- A real corner has a continuous nonzero velocity; a reversal reaches its mark.
function motion_plan(points,span)
  local p={total=(#points-1)*span}
  for i=2,#points do p[#p+1]={a=points[i-1],b=points[i],start=(i-2)*span,
    finish=(i-1)*span,state='fly',hidden=false} end
  return p
end
corner=motion_plan({point(0,0,0),point(6000,0,0),point(6000,6000,0)},1000)
local mid=F.Position(corner,1000)
assert(mid.X<6000 and mid.Y>0) -- genuinely curved, not an axis lerp
local before,after=F.Position(corner,999),F.Position(corner,1001)
assert(after.X>before.X and after.Y>before.Y)
reverse=motion_plan({point(0,0,0),point(0,0,1000),point(0,0,0)},1000)
assert(F.Position(reverse,1000).Z==1000)
for t=0,2000 do local p=F.Position(reverse,t); assert(p.X==0 and p.Y==0 and p.Z<=1000 and p.Z>=0) end
-- No AI/path entry point is needed. Throw if a new implementation hands over control.
local forbidden=function() error('Vanilla command/pathing entered') end
FlyingDrone.Goto=forbidden; FlyingDrone.FlightGoto=forbidden
local base=clock+10000
r=assert(F.Create(h,base)); r.drone.SetCommand=forbidden
r.drone.Goto=forbidden; r.drone.FlightGoto=forbidden; r.drone.UseBattery=forbidden
assert(F.Send(r,cs,true)); local previous_yaw=r.drone:GetAngle()
max_yaw_step=0; timed_positions=0
for now=base,r.removed-1,20 do
  clock=now; assert(F.Update(r,now))
  local yaw=r.drone:GetAngle()
  local jump=math.abs((yaw-previous_yaw+10800)%21600-10800)
  assert(jump<=515,'20-ms yaw jump exceeds filtered half-turn bound')
  max_yaw_step=math.max(max_yaw_step,jump); previous_yaw=yaw
  if r.drone.pos_time>0 then timed_positions=timed_positions+1 end
  assert(not r.drone.curvature and not r.drone.command)
  local pos=r.drone.pos; F.Update(r,now); assert(pos==r.drone.pos) -- pause
end
assert(timed_positions>0); F.Update(r,r.removed); assert(r.drone.deleted)
-- Smoothness tuners cannot change authoritative arrival/work/removal offsets.
r=F.Create(h,base); F.Send(r,cs,true)
local expected={r.arrival,r.work_done,r.removed}
for _,name in ipairs({'TurnRadius','BlendTime','AccelTime','HeadingTime','BankAngle'}) do
  assert(SetHubDroneTune(name,F[name]))
end
F.TurnRadius=150; F.AccelTime=200; F.BlendTime=200
q=F.Create(h,base); F.Send(q,cs,true)
assert(q.arrival==expected[1] and q.work_done==expected[2] and q.removed==expected[3])
F.TurnRadius=300; F.AccelTime=400; F.BlendTime=400
-- Sparse/late sampling catches up instead of extending an economic deadline.
assert(F.Update(q,q.arrival+100)); assert(q.drone.state=='constructStart')
assert(q.drone.pos.Z==F.FixHeight)
assert(not F.Update(q,q.removed+10000))
r.drone.run_cmd_on_land='Malfunction'; assert(not F.Update(r,base+1))
-- Recalling within a corner retraces the original curve, including the braking arc.
clock=base+50000; drone,status=SendHubDroneTo(cs,h)
tick(clock+F.LaunchTime+480); local recall_start=clock
ReturnHubDrone(); local stop=F.Status().removed
assert(ReturnHubDrone()==drone and F.Status().removed==stop)
for now=recall_start,stop-1,20 do tick(now); assert(F.Status()) end
tick(stop); assert(not F.Status())
assert(SetHubDroneTune('BankAngle',0)); assert(not SetHubDroneTune('BankAngle',301))
assert(SetHubDroneTune('BankAngle',180)); assert(created==removed)
''')

# Check C1 at every compiled seam, including unequal speeds and exact stops.
def check_curves(curves):
    previous = None
    for c in curves.values():
        p = [list(v.values()) for v in c.points.values()]
        span = c.finish-c.start
        first = [(p[1][k]-p[0][k])*(len(p)-1)/span for k in range(3)]
        last = [(p[-1][k]-p[-2][k])*(len(p)-1)/span for k in range(3)]
        if previous:
            assert abs(previous[0]-c.start)<1e-7
            assert max(abs(a-b) for a,b in zip(previous[1],p[0]))<1e-7
            assert max(abs(a-b) for a,b in zip(previous[2],first))<1e-7
        previous = (c.finish,p[-1],last)

for plan in (lua.globals().corner, lua.globals().reverse, lua.globals().r.plan):
    check_curves(lua.globals().F.PrepareMotion(plan))
lua.execute('''
local plan=r.plan
for t=0,measured_arrival,37 do
  local out=F.Position(plan,t); local back=F.Position(plan,plan.total-t)
  assert(out:Dist(back)<=1,'Return must share the measured outward envelope')
end
''')

# Actual archived FlightGoto, with a solver spy: the destination is a solver
# request, not a waypoint-constrained interpolator. This is a source contract test.
archive = Path('B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.0.403908/Src')
flight = (archive/'Lua/Flight.lua').read_text(encoding='utf8')
body = flight.split('function FlyingObject:FlightGoto(dest, dest_vector)',1)[1].split('\nfunction FlyingObject:FlightStop()',1)[0]
native = LuaRuntime()
native.execute('''FlyingObject={}; calls=0; Sleep=function() error('yield') end
function Flight_Step(self,dest,vector) calls=calls+1; self.solver_dest=dest; self.pos='solver-owned'; return -1 end
function IsValid() return true end
''')
native.execute('local fssFinished=-1; local fssRequestFailed=-9; local debug=false\nfunction FlyingObject:FlightGoto(dest,dest_vector)'+body)
native.execute('''o=setmetatable({sync_path=true},{__index=FlyingObject})
function o:GetFlying() return false end; function o:FlightStop() self.stopped=true end
assert(o:FlightGoto('requested-waypoint')); assert(calls==1 and o.solver_dest=='requested-waypoint')
assert(o.pos=='solver-owned' and o.stopped)
''')

parser = argparse.ArgumentParser()
parser.add_argument('--clearance-output',type=Path)
args = parser.parse_args()
if args.clearance_output:
    entity_path=ROOT/'tools/devmods/train_hub/Entities/SMROptInTrainHub6.entjson'
    entity=json.loads(entity_path.read_text())
    spots={s['name']:s['spotPos'] for s in entity['$value']['meshDescriptions'][0]['attaches']}
    lua.globals().spot_floor=lua.table_from(spots['Pitfloor'])
    lua.globals().spot_rim=lua.table_from(spots['Pitrim'])
    lua.execute('''function GetEntitySpotPos(_,idx)
      local p=idx==0 and spot_floor or spot_rim; return point(p[1],p[2],p[3]) end''')
    routes={}
    for name,spot in spots.items():
        if not name.startswith('Trackconnector'): continue
        lua.globals().connector=lua.table_from(spot)
        lua.execute('''mh=hub(); ms=obj(20000,0); local c=connector
        mt=track(mh,ms,{{c[1],c[2],c[3]},{c[1]*4,c[2]*4,c[3]}})
        mr=F.Create(mh,0); F.Send(mr,mt.elements[2],true)
        export_plan={total=0}
        for _,s in ipairs(mr.plan) do
          if s.state~='fly' then break end
          export_plan[#export_plan+1]=s; export_plan.total=s.finish
        end
        F.PrepareMotion(export_plan); F.Remove(mr)''')
        plan=lua.globals().export_plan
        check_curves(plan.motion)
        routes[name]=[{'start':c.start,'finish':c.finish,
                      'points':[list(p.values()) for p in c.points.values()]}
                     for c in plan.motion.values()]
    args.clearance_output.write_text(json.dumps({
        'command':'python tools/devmods/train_hub/tests/flight_smoke.py --clearance-output '+str(args.clearance_output),
        'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'entity_sha256':hashlib.sha256(entity_path.read_bytes()).hexdigest(),
        'bank_angle_minutes':lua.globals().F.BankAngle,'routes':routes},indent=2)+'\n')
g = lua.globals()
assert g.created==g.removed
if not args.clearance_output:
    receipt=json.loads((ROOT/'tools/devmods/train_hub/tests/motion_clearance_receipt.json').read_text())
    assert receipt['source_sha256']==receipt['motion']['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert receipt['entity_sha256']==hashlib.sha256((ROOT/'tools/devmods/train_hub/Entities/SMROptInTrainHub6.entjson').read_bytes()).hexdigest()
    assert receipt['blend_sha256']==hashlib.sha256(Path(receipt['blend']).read_bytes()).hexdigest()
    assert receipt['leg_count']==len(receipt['legs'])==sum(len(v) for v in receipt['motion']['routes'].values())>0
    assert receipt['triangle_total']==sum(receipt['object_triangles'].values())>0
    assert all(v['margin_m']>0 for v in receipt['legs'].values())
result = {
    "command": "python tools/devmods/train_hub/tests/flight_smoke.py"+(" --clearance-output "+str(args.clearance_output) if args.clearance_output else ""),
    "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "source_sha256": __import__("hashlib").sha256(SOURCE.read_bytes()).hexdigest(),
    "scope": "mocked Lua / source contract; ordinary run also verifies mesh receipt; no native flight, import or serialization claim",
    "result": "PASS",
    "fixture_game_ms": {"arrival": g.measured_arrival, "work_done": g.measured_work, "removed": g.measured_total},
    "visuals_created": g.created,
    "visuals_removed": g.removed,
    "max_20ms_heading_step_minutes": g.max_yaw_step,
    "timed_position_calls": g.timed_positions,
    "native_solver_contract": "archived FlightGoto executed with solver spy; solver owns path",
}
print(json.dumps(result, indent=2))
