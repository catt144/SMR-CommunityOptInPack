"""Execute the flight Lua against a deterministic physical graph and clock.

No game/render/import/clearance evidence. Requires lupa, as the adjacent smokes do.
Only opens the flight source; the hub implementation belongs to L4.

L2M2: the mocks record every engine call so the smoke can hold the contract the owner's eye
cannot check from code: one timed SetPos per chord, chained end to end at exact game-time
wakes, speed continuous across chord joins, acceleration bounded, zero speed and zero roll at
every rest pose before any state change, concealment seams exact, recall retracing the flown
lane. Fluidity itself is the owner's verdict in game.
"""
import json
import argparse
import hashlib
import math
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
-- The engine's Min/Max/Clamp are INTEGER helpers and its `/` divides integers as integers
-- (shipped idiom `a * 1.0 / b`). They are deliberately absent here so the flight source cannot
-- lean on them; MulDivRound is the engine's integer function and keeps its integer contract.
Min=nil; Max=nil; Clamp=nil
function MulDivRound(a,b,c)
  assert(math.type(a)=='integer' and math.type(b)=='integer' and math.type(c)=='integer','MulDivRound takes integers')
  return math.floor(a*b/c+.5)
end
local function isint(v) return math.type(v)=='integer' end
local P={}; P.__index=P
function point(x,y,z) assert(isint(x) and isint(y) and isint(z),'engine points take integers'); return setmetatable({X=x,Y=y,Z=z},P) end
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
function CreateRealTimeThread(fn) error('The driver must be a GAME-time thread') end
function CreateGameTimeThread(fn) return {fn=fn} end
function Sleep() error('yield outside a thread') end
function IsValidThread(t) return t and not t.deleted end
function DeleteThread(t) if t then t.deleted=true end end
function DoneObject(o) assert(not o.deleted); o.deleted=true; removed=removed+1 end
function GetEntitySpotPos(_,idx) return idx==0 and point(-1000,-577,-2000) or point(-1000,-577,30) end
local O={}; O.__index=O
function obj(x,y,z) return setmetatable({valid=true,pos=point(x,y,z or 0),connectors={},calls={},states={}},O) end
function O:GetPos() return self.pos end
function O:GetVisualPos() return self.pos end
function O:GetEntity() return self.entity or 'rail' end
function O:GetMap() return 1 end
function O:GetRelativePoint(p)
  local angle=(self.angle or 0)*math.pi/180
  local scale=(self.scale or 100)/100
  return self.pos+point(math.floor((p.X*math.cos(angle)-p.Y*math.sin(angle))*scale+.5),
    math.floor((p.X*math.sin(angle)+p.Y*math.cos(angle))*scale+.5),math.floor(p.Z*scale+.5))
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
-- Engine mocks record the call contract. A timed SetPos starts where the object IS.
function O:SetPos(p,time)
  assert(time==nil or isint(time),'SetPos time is an integer')
  self.calls[#self.calls+1]={from=self.pos,to=p,time=time or 0,clock=clock,visible=self.visible,state=self.state}
  self.pos=p; self.pos_time=time or 0
end
function O:SetAngle(a) self.angle=a end
function O:GetAngle() return self.angle or 0 end
function O:SetCurvature(value) assert(value==false); self.curvature=value end
function O:SetAcceleration(value)
  assert(isint(value),'HGE::l_SetAcceleration: Expected integer')
  local c=self.calls[#self.calls]
  if c and c.clock==clock and c.acc==nil then c.acc=value else self.rest_acc=value end
end
function O:SetRollPitchYaw(roll,pitch,yaw,time)
  assert(time>0 and pitch==0 and math.abs(roll)<=math.abs(SMROptInHubFlight.BankAngle))
  assert(isint(roll) and isint(pitch) and isint(yaw) and isint(time),'SetRollPitchYaw takes integers')
  local c=self.calls[#self.calls]
  if c and c.clock==clock then c.roll=roll; c.yaw=yaw; c.rot_time=time end
  self.angle=yaw; self.roll=roll; self.turn_time=time
end
function O:SetState(s) self.states[#self.states+1]={s,clock}; self.state=s end
function O:SetVisible(v) self.visible=v end
function O:TakeOff() self:SetState('fly') end
function O:LandingEnd() self:SetState('idle') end
function O:GetAnimDuration(s) return s=='constructStart' and 400 or 600 end
function O:StartFX(f,t) self.fx=f; self.fx_target=t; self.fx_first=self.fx_first or clock end
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
function tick(t) clock=t; return SMROptInHubFlight.Sample() end
-- The game-time driver, simulated: wake exactly when the current chord ends.
function drive(limit)
  local wakes=0
  while true do
    local w=SMROptInHubFlight.Sample()
    if not w then return wakes,false end
    assert(isint(w),'Sleep takes an integer')
    if limit and clock+w>limit then clock=limit; SMROptInHubFlight.Sample(); return wakes,true end
    clock=clock+w; wakes=wakes+1
  end
end
''')
source_text = SOURCE.read_text(encoding="utf8")
# Static gate: this engine's `/` divides integers as integers, so the flight source may divide
# only inside div() (which coerces to float first) and may not call the engine's integer helpers.
import re
_code = "\n".join(line.split("--", 1)[0] for line in source_text.split("\n"))
_bare = [line.strip() for line in _code.split("\n") if re.search(r"(?<!/)/(?!/)", line)]
assert _bare == ["local function div(a, b) return (a * 1.0) / b end"], "bare division outside div(): %r" % _bare
assert not re.search(r"\b(Min|Max|Clamp)\(", _code), "engine integer helper used on flight numbers"
lua.execute(source_text)
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
''')

lua.execute(r'''
-- The console sequence: spawn, rise to the crest, hover until sent, fly, work, return, land.
clock=10000; drone=assert(SpawnHubDrone(h)); assert(created==1)
assert(SpawnHubDrone(h)==drone and created==1)
assert(#drone.calls==1 and drone.calls[1].time==0, 'exactly one instant placement, at the pit floor')
assert(not drone.curvature, 'SetCurvature(false): every chord is a straight engine move')
local rise_wakes=drive(18000)
assert(F.Status().phase=='hover' and drone.pos.Z==F.PitExitZ, 'holds at the crest until sent')
local crest_calls=#drone.calls
assert(rise_wakes>=8 and rise_wakes<=16, 'the 30 m rise is a dozen chords, not a write per tick: '..rise_wakes)
clock=18000; local d2,status=SendHubDroneTo(cs,h); assert(d2==drone)
arrival,completed,finished=status.arrival,status.work_done,status.removed
assert(completed-arrival==6000)
trip_wakes=drive()
assert(clock==finished and drone.deleted and not F.Status(), 'removed exactly at its deadline')
-- The call contract: one timed move per chord, chained at exact wakes.
chords=0; instant=0; joins=0; breaks=0; max_chord=0; min_chord=1e9
for i,c in ipairs(drone.calls) do
  if c.time==0 then instant=instant+1 else
    chords=chords+1; max_chord=math.max(max_chord,c.time); min_chord=math.min(min_chord,c.time)
    assert(c.rot_time==c.time, 'heading/bank interpolate over the same chord time')
    local p=drone.calls[i-1]
    if p and p.time>0 then
      joins=joins+1
      local continuous=p.to.X==c.from.X and p.to.Y==c.from.Y and p.to.Z==c.from.Z and p.clock+p.time==c.clock
      if not continuous then
        breaks=breaks+1
        -- only a rest (the crest hover, the work) may separate two chords in time
        assert(p.to.X==c.from.X and p.to.Y==c.from.Y and p.to.Z==c.from.Z, 'a chord starts where the last ended')
        assert(c.clock==18000 or c.clock==completed, 'a gap between chords is a planned rest: '..c.clock)
      end
    end
  end
end
assert(instant==1, 'no snap after placement: '..instant)
assert(breaks==2, 'the only time gaps are the crest hover and the work: '..breaks)
assert(max_chord<=F.ChordTime and min_chord>=1, 'chords fit the Wasp cadence: '..min_chord..'..'..max_chord)
assert(trip_wakes<=chords+8, 'the driver sleeps through each chord: '..trip_wakes..' wakes for '..chords..' chords')
assert(chords<400, 'chords per trip: '..chords)
-- State changes only at rest, exactly on the deadlines, and never into an unfinished move.
local seq={}
for _,st in ipairs(drone.states) do seq[#seq+1]=st[1]..'@'..st[2] end
assert(seq[1]=='fly@10000' and seq[2]=='constructStart@'..arrival and seq[3]=='constructIdle@'..(arrival+400)
  and seq[4]=='constructEnd@'..(arrival+5400) and seq[5]=='fly@'..completed and seq[6]=='idle@'..finished,
  table.concat(seq,' '))
assert(#seq==6, 'no state is re-issued along the flight')
assert(drone.fx_first==arrival and drone.fx_target==cs, 'work FX start at arrival, on the target')
''')
lua.execute(r'''
-- Kinematics of the committed plan: continuous speed, bounded acceleration, rest before work.
clock=100000; r=assert(F.Create(h,clock)); assert(F.Send(r,cs,true))
measured_arrival,measured_work,measured_total=r.arrival-clock,r.work_done-clock,r.removed-clock
-- Regression pins for the fixture at the committed defaults; a planner change moves them on purpose.
assert(measured_arrival==25524 and measured_work==31524 and measured_total==57051,
  'fixture offsets moved: '..measured_arrival..' '..measured_work..' '..measured_total)
local steps=r.plan.steps
local prev; worst_join=0; max_acc=0; max_roll=0
for i,s in ipairs(steps) do
  if s.state=='fly' then
    assert(s.finish-s.start>=1 and s.finish-s.start<=F.ChordTime)
    assert(s.v0>=-1 and s.v1>=-1 and s.len>0)
    if not s.curved then max_acc=math.max(max_acc,math.abs(s.acc)) end
    max_roll=math.max(max_roll,math.abs(s.roll))
    if prev and prev.state=='fly' and prev.finish==s.start then worst_join=math.max(worst_join,math.abs(prev.v1-s.v0)) end
    local nxt=steps[i+1]
    if nxt and nxt.state~='fly' then
      assert(math.abs(s.v1)<1 and s.roll==0, 'arrives at rest, level: v1='..s.v1..' roll='..s.roll)
      assert(s.finish==nxt.start)
    end
  end
  prev=s
end
assert(worst_join<1, 'speed is continuous across chord joins: '..worst_join)
assert(max_acc<=F.Accel*1.1, 'straight-line acceleration stays under Accel: '..max_acc)
assert(max_roll>0 and max_roll<=math.abs(F.BankAngle), 'banks through the track approach: '..max_roll)
-- The work pose is exact; the return mirrors the outward trip in time and space.
local at=F.Position(r.plan,measured_arrival)
assert(at.X==cs.pos.X and at.Y==cs.pos.Y and at.Z==F.FixHeight)
assert(math.abs((measured_total-measured_work)-measured_arrival)<=10, 'return takes the outward time, to chord rounding')
for t=0,measured_arrival,97 do
  local out=F.Position(r.plan,t); local back=F.Position(r.plan,r.plan.total-t)
  assert(out:Dist(back)<=40, 'return retraces the outward chords within rounding drift: '..t)
end
-- The pit column: rises through the rim, reverses at the crest through rest with the same
-- acceleration on both sides (a parabola, not a stall), then lowers to the lane.
local crest_i
for i,s in ipairs(steps) do if s.state=='fly' and s.b[3]==F.PitExitZ and s.a[3]<F.PitExitZ then crest_i=i; break end end
local up,down=steps[crest_i],steps[crest_i+1]
assert(math.abs(up.v1)<1 and down.a[3]==F.PitExitZ and down.b[3]<F.PitExitZ)
assert(up.acc<0 and down.acc>0 and math.abs(math.abs(up.acc)-math.abs(down.acc))<F.Accel*.1, 'C2 through the crest')
for i=1,crest_i do assert(steps[i].a[1]==steps[1].a[1] and steps[i].a[2]==steps[1].a[2], 'no sideways motion in the shaft') end
-- Corners are rounded inside their own legs and taken at the speed their radius allows.
local lane_z=F.UnderDeckHeight
local in_lane=false
for i,s in ipairs(steps) do
  if s.state=='fly' and s.start<measured_arrival then
    if s.a[3]==lane_z and s.b[3]==lane_z then in_lane=true end
    if s.curved then
      assert(math.abs(s.v1-s.v0)<=s.v0*.01+1 and s.v0<=F.Speed, 'a corner is flown at constant speed, to ms rounding: '..s.v0..'->'..s.v1)
      -- a right angle rounded within TurnRadius cannot exceed the speed that radius allows
      if s.turn>=4800 then assert(s.v0<=math.sqrt(F.Accel*F.TurnRadius)*1.01, 'right angle at radius-bound speed: '..s.v0) end
    end
  end
end
assert(in_lane)
''')

lua.execute(r'''
-- Pure geometry: a corner is genuinely curved, C1 at its seams and inside its legs' hull.
corner,corner_total=F.Trajectory({{p={0,0,0},stop=true},{p={6000,0,0}},{p={6000,6000,0},stop=true}},0,0)
local plan={steps=corner,total=corner_total}; for i,s in ipairs(corner) do s.index=i end
local curved=0
for _,s in ipairs(corner) do
  assert(s.a[1]>=-1 and s.a[1]<=6001 and s.a[2]>=-1 and s.a[2]<=6001, 'inside the corner hull')
  assert(s.a[1]-1<=6000 and s.a[2]+1>=0 and s.a[2]<=s.a[1]+1, 'never outside the L of its two legs')
  if s.curved then curved=curved+1 end
end
assert(curved>=6, 'a right angle is at least six chords: '..curved)
local mid=F.Position(plan,math.floor(corner_total/2))
assert(mid.X<6000 and mid.Y>0 and mid.X>3000, 'genuinely curved, not an axis lerp')
-- A reversal reaches its mark at rest; nothing overshoots.
rev,rev_total=F.Trajectory({{p={0,0,0},stop=true},{p={0,0,1000}},{p={0,0,0},stop=true}},0,0)
local rplan={steps=rev,total=rev_total}; for i,s in ipairs(rev) do s.index=i end
local top=0
for t=0,rev_total do local p=F.Position(rplan,t); assert(p.X==0 and p.Y==0 and p.Z>=0 and p.Z<=1000); top=math.max(top,p.Z) end
assert(top==1000)
-- A concealment seam is exact: the chord ends on it, the corner there is not rounded.
seam,_=F.Trajectory({{p={0,0,0},stop=true},{p={5000,0,0}},{p={10000,3000,0},hidden=true},{p={15000,3000,0}},{p={20000,3000,0},stop=true}},0,0)
local hidden_start,visible_again
for _,s in ipairs(seam) do
  if s.hidden and not hidden_start then hidden_start=s.a end
  if hidden_start and not visible_again and not s.hidden then visible_again=s.a end
  if s.hidden then assert(s.a[1]>=4999 and s.b[1]<=10001) end
end
assert(hidden_start[1]==5000 and hidden_start[2]==0 and visible_again[1]==10000 and visible_again[2]==3000)
''')

lua.execute(r'''
-- Recall while accelerating along the under-deck lane: brake, stop, retrace the lane, land.
clock=200000; drone,status=SendHubDroneTo(cs,h)
local low_at
while F.Status() and not (drone.pos.Z==F.UnderDeckHeight and drone.pos.X<-2500) do local w=F.Sample(); clock=clock+w end
low_at=clock; local at_recall=drone.pos
ReturnHubDrone(); local recalled=F.Status().removed
assert(ReturnHubDrone()==drone and F.Status().removed==recalled)
local n0=#drone.calls; local farthest=at_recall.X
while F.Status() do local w=F.Sample(); if not w then break end; clock=clock+w
  if drone.pos.X<farthest then farthest=drone.pos.X end end
assert(clock==recalled and drone.deleted)
assert(farthest<at_recall.X-500, 'brakes forward along the lane before turning back')
for i=n0+1,#drone.calls do
  local c=drone.calls[i]
  assert(c.time>0, 'recall never snaps')
  if c.to.X<-2000 and c.to.X>-7000 then assert(math.abs(c.to.Z-F.UnderDeckHeight)<=1, 'retrace stays in the lane') end
end
assert(drone.calls[#drone.calls].to.Z==-2000, 'lands on the pit floor')
-- Recall from the crest hover descends and lands; recall mid-rise never passes the crest.
clock=300000; drone=SpawnHubDrone(h); drive(clock+6000); assert(F.Status().phase=='hover')
ReturnHubDrone(); drive(); assert(drone.deleted and drone.calls[#drone.calls].to.Z==-2000)
clock=400000; drone=SpawnHubDrone(h); drive(clock+1200); local z0=drone.pos.Z
ReturnHubDrone(); local zmax=z0
while F.Status() do local w=F.Sample(); if not w then break end; clock=clock+w; zmax=math.max(zmax,drone.pos.Z) end
assert(zmax<F.PitExitZ and zmax>z0 and drone.deleted, 'brakes upward then returns: '..z0..' -> '..zmax)
''')

lua.execute(r'''
-- Reciprocal tunnel: hidden only between the inner spots, in both directions, seams exact.
h2=hub(0,100000); near=obj(20000,100000); far=obj(70000,100000); dest=obj(90000,100000)
near.class='TrackTunnelBase'; far.class='TrackTunnelBase'; near.linked_obj=far; far.linked_obj=near
near.inner=obj(21000,100000); far.inner=obj(69000,100000)
a=track(h2,near,{{0,100000},{20000,100000}})
b=track(far,dest,{{70000,100000},{80000,100000},{90000,100000}})
tp=assert(F.Route(h2,b.elements[2])); hidden=0
for _,p in ipairs(tp) do if p.hidden then hidden=hidden+1 end end
assert(hidden==1)
far.linked_obj=false; assert(F.Route(h2,b.elements[2])==nil); far.linked_obj=near
clock=500000; drone,status=SendHubDroneTo(b.elements[2],h2)
local outbound_hidden,inbound_hidden=false,false
while F.Status() do
  local w=F.Sample(); if not w then break end; clock=clock+w
  if F.Status() and drone.visible==false then
    if clock<status.arrival then outbound_hidden=true else inbound_hidden=true end
    assert(drone.pos.X>=21000 and drone.pos.X<=69000, 'hidden only past the inner spot')
  end
end
assert(outbound_hidden and inbound_hidden and clock==status.removed and not F.Status())
-- Interruption inside the tunnel stays hidden, then emerges on the same route.
clock=600000; drone,status=SendHubDroneTo(b.elements[2],h2)
while F.Status() and drone.visible~=false do clock=clock+F.Sample() end
clock=clock+700; F.Sample(); ReturnHubDrone(); assert(drone.visible==false)
local reappeared=false
while F.Status() do local w=F.Sample(); if not w then break end; clock=clock+w; if drone.visible~=false and drone.pos.X<21000 then reappeared=true end end
assert(reappeared and drone.deleted)
''')

lua.execute(r'''
-- Save race gate: even clock advancement cannot respawn; failed save Done releases it.
clock=700000; drone=SpawnHubDrone(h); OnMsg.SaveGameStart()
assert(drone.deleted and not F.Status()); assert(SpawnHubDrone(h)==nil)
tick(clock+10000); assert(SendHubDroneTo(cs,h)==nil)
OnMsg.SaveGameDone(); drone=assert(SpawnHubDrone(h))
OnMsg.LoadGame(); assert(drone.deleted and not F.Status())
-- Controller loss, death and removal are scoped to the prototype object.
drone=SpawnHubDrone(h); drone.command_center=s; tick(clock+1); assert(drone.deleted)
drone=SpawnHubDrone(h); drone.command='GoHome'; tick(clock+1); assert(drone.deleted)
drone=SpawnHubDrone(h); h.destroyed=true; tick(clock+1); assert(drone.deleted); h.destroyed=false
drone=SpawnHubDrone(h); drone.run_cmd_on_land='Malfunction'; tick(clock+1); assert(drone.deleted)
-- Tuner: the owner's dials, and the retired names refused.
assert(SetHubDroneTune('Speed',9000)); assert(not SetHubDroneTune('Speed',0)); F.Speed=6000
for _,name in ipairs({'UnderDeckHeight','OutwardDistance','ClimbRate','OverTrackHeight','FixHeight','TransferHeight','HoverHeight','WorkTime','TurnRadius','Accel','BankAngle'}) do
  assert(SetHubDroneTune(name,F[name]))
end
for _,name in ipairs({'PitOffsetX','LaunchTime','LandingTime','BlendTime','AccelTime','HeadingTime','SampleTime','ChordTime'}) do
  assert(not SetHubDroneTune(name,400), name..' is not a dial')
end
assert(SetHubDroneTune('BankAngle',0)); assert(not SetHubDroneTune('BankAngle',2701)); assert(SetHubDroneTune('BankAngle',-900)); assert(SetHubDroneTune('BankAngle',900))
drone=SpawnHubDrone(h); assert(not SetHubDroneTune('Speed',6000))
OnMsg.DoneGame(); assert(drone.deleted and not F.Status())
-- No AI/path entry point is needed. Throw if a new implementation hands over control.
local forbidden=function() error('Vanilla command/pathing entered') end
FlyingDrone.Goto=forbidden; FlyingDrone.FlightGoto=forbidden
clock=800000; r=assert(F.Create(h,clock)); r.drone.SetCommand=forbidden
r.drone.Goto=forbidden; r.drone.FlightGoto=forbidden; r.drone.UseBattery=forbidden
assert(F.Send(r,cs,true)); r.drone.battery=1
local prev_yaw=r.drone:GetAngle(); max_yaw_step=0
while F.Update(r,clock) do
  local yaw=r.drone:GetAngle(); local dt=r.drone.turn_time or 1
  local jump=math.abs((yaw-prev_yaw+10800)%21600-10800)
  assert(jump<=F.YawRate*dt/1000+1, 'yaw turns no faster than the Wasp turns')
  max_yaw_step=math.max(max_yaw_step,jump); prev_yaw=yaw
  assert(r.drone.battery==F.BatteryMax and not r.drone.command and not r.drone.curvature)
  clock=clock+F.Update(r,clock)
end
assert(r.drone.deleted)
''')
lua.execute(r'''
-- L4's independent records: absolute start, sparse sampling, idempotence, no deadline drift.
clock=900000
r1=assert(F.Create(h,clock-4000)); r2=assert(F.Create(h,clock-4000))
assert(F.Send(r1,cs,true)); assert(F.Send(r2,cs,true))
assert(r1.arrival==clock-4000+measured_arrival and r2.arrival==r1.arrival)
assert(F.Update(r1,clock) and F.Update(r2,clock)); assert(r1.drone.pos:Dist(r2.drone.pos)==0)
-- An absolute start in the past: one catch-up snap, then the current chord; a repeat issues nothing.
assert(#r1.drone.calls==3 and r1.drone.calls[2].time==0 and r1.drone.calls[3].time>0, 'rearm: snap then chord')
local n=#r1.drone.calls
assert(F.Update(r1,clock)==F.Update(r1,clock) and #r1.drone.calls==n, 'a repeated now issues nothing')
-- A single late sample lands exactly on the work pose in the work state.
assert(F.Update(r2,r2.arrival+100)); assert(r2.drone.state=='constructStart' and r2.drone.pos.Z==F.FixHeight)
assert(not F.Update(r2,r2.removed+10000) and r2.drone.deleted)
-- Smoothing dials move the visual's own duration and therefore its offsets; the record's
-- absolute deadlines are whatever the plan says at Send, never extended by sampling.
F.TurnRadius=300; F.Accel=2400
q=F.Create(h,clock); F.Send(q,cs,true)
assert(q.arrival<r1.arrival+4000, 'a nimbler drone arrives sooner')
assert(q.removed-q.started==q.plan.total)
F.TurnRadius=1500; F.Accel=1200
OnMsg.SaveGameStart(); assert(r1.drone.deleted and q.drone.deleted)
assert(F.Create(h)==nil); OnMsg.SaveGameDone()
assert(created==removed)
''')

# Actual archived FlightGoto, with a solver spy: the destination is a solver request, not a
# waypoint-constrained interpolator. Source contract only; it names the call path the build
# does not take.
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
assert 'per-instance overrides are ignored by design' in flight, 'flight class params are class-static (Flight.lua)'

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
      local p=idx==0 and spot_floor or spot_rim
      return point(math.floor(p[1]+.5),math.floor(p[2]+.5),math.floor(p[3]+.5)) end''')
    routes={}
    for name,spot in spots.items():
        if not name.startswith('Trackconnector'): continue
        lua.globals().connector=lua.table_from(spot)
        lua.execute('''mh=hub(); ms=obj(20000,0); local c=connector
        local function r(v) return math.floor(v+.5) end -- spot positions are engine integers
        mt=track(mh,ms,{{r(c[1]),r(c[2]),r(c[3])},{r(c[1]*4),r(c[2]*4),r(c[3])}})
        mr=F.Create(mh,0); F.Send(mr,mt.elements[2],true)
        export={}
        for _,p in ipairs(mr.plan.prims) do
          if p.start and p.finish<=mr.arrival then
            local bank=0
            for _,s in ipairs(mr.plan.steps) do
              if s.state=='fly' and s.start>=p.start and s.finish<=p.finish then bank=math.max(bank,math.abs(s.roll)) end
            end
            export[#export+1]={start=p.start,finish=p.finish,bank=math.ceil(bank),pts=p.pts}
          end
        end
        F.Remove(mr)''')
        export=lua.globals().export
        spans=[{'start':e.start,'finish':e.finish,'bank_minutes':e.bank,
                'points':[[v for v in p.values()] for p in e.pts.values()]} for e in export.values()]
        assert spans and all(len(sp['points']) in (2,3) for sp in spans)
        for a_,b_ in zip(spans,spans[1:]):
            assert a_['finish']==b_['start'] and a_['points'][-1]==b_['points'][0], 'spans tile the outward route'
        routes[name]=spans
    args.clearance_output.write_text(json.dumps({
        'command':'python tools/devmods/train_hub/tests/flight_smoke.py --clearance-output '+str(args.clearance_output),
        'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'entity_sha256':hashlib.sha256(entity_path.read_bytes()).hexdigest(),
        'bank_angle_minutes':abs(lua.globals().F.BankAngle),
        'chord_horizon_ms':0,
        'chords_are':'straight engine moves cut at every span boundary; each lies in its span control hull',
        'routes':routes},indent=2)+'\n')
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
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "scope": "mocked Lua / source contract; ordinary run also verifies mesh receipt; no native flight, import or serialization claim",
    "result": "PASS",
    "fixture_game_ms": {"arrival": g.measured_arrival, "work_done": g.measured_work, "removed": g.measured_total},
    "visuals_created": g.created,
    "visuals_removed": g.removed,
    "console_trip": {"timed_position_calls": g.chords, "instant_position_calls": g.instant,
                     "driver_wakes_incl_hover": g.trip_wakes, "chord_ms_min_max": [g.min_chord, g.max_chord]},
    "worst_chord_join_speed_step_units_per_s": g.worst_join,
    "max_straight_accel_units_per_s2": g.max_acc,
    "max_yaw_step_minutes_per_chord": g.max_yaw_step,
    "native_solver_contract": "archived FlightGoto executed with solver spy; solver owns path; not taken",
}
print(json.dumps(result, indent=2))
