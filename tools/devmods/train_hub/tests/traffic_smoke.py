"""Offline contract smoke: execute hub Lua + archived vanilla arrival in lupa.

Native geometry/interpolation/saving are mocked, so this is NOT a game smoke.
Feed the executed paths to the unchanged oracle's width-only TWO-TRAIN method;
its CLI still models the old single-slide station and cannot model this build.
Run from the repo root. --output writes a NEW evidence file (never overwrites).
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "tools/devmods/train_hub/Code/20_TrainHub.lua"
ARCHIVE = Path(os.environ.get("SMR_SRCARCHIVE",
                              r"B:\Dev\SMR\SMR-Shared\SMR-SrcArchive")) / "1.1.0.403908" / "Src"
# The oracle sits beside the train assets, in the same SMR-Assets repo.
ASSETS = Path(os.environ.get("SMR_TRAINASSETS",
                             r"B:\Dev\SMR\SMR-Assets\trainhub")).parent
ORACLE = ASSETS / "_shared" / "geometry" / "hub_oracle.py"

STUBS = r'''
guim=100; empty_table={}; axis_z={}; const={DroneBatteryMax=100}; OnMsg={}
function round(n) return math.floor(n+0.5) end
local P={}; P.__index=P
function point(x,y,z) return setmetatable({xx=x,yy=y,zz=z or 0},P) end
function P:x() return self.xx end
function P:y() return self.yy end
function P:z() return self.zz end
function P:xy() return self.xx,self.yy end
function P.__add(a,b) return point(a.xx+b.xx,a.yy+b.yy,a.zz+b.zz) end
function P.__sub(a,b) return point(a.xx-b.xx,a.yy-b.yy,a.zz-b.zz) end
function MulDivRound(a,b,c)
 if type(a)=='table' then return point(round(a.xx*b/c),round(a.yy*b/c),round(a.zz*b/c)) end
 return round(a*b/c)
end
Max=math.max
function IsValid(o) return type(o)=='table' and o.valid==true end
function CurrentThread() return active_thread end
function Msg(...) end
function Sleep(t) if on_sleep then on_sleep(t) end end
function WaitMsg(_,t) Sleep(t) end
function CalcOrientation(a,b) return (round(math.deg(math.atan(b.yy-a.yy,b.xx-a.xx))*60))%21600 end
function WorldToHex(p)
 local r=round(p.yy/(500*math.sqrt(3))); return round(p.xx/1000-r/2),r
end
function HexToWorld(q,r) return round(1000*q+500*r),round(500*math.sqrt(3)*r) end
function HexRotate(q,r,d) for i=1,d%6 do q,r=-r,q+r end return q,r end
function HexAngleToDirection(a) return round(a/3600)%6 end
function GetEntityOutlineShape()
 local t={point(0,0)}
 for d=0,5 do for k=1,4 do local q,r=HexRotate(k,0,d); t[#t+1]=point(q,r) end end
 return t
end
DroneControl={OnPinClicked=function() end}; Station={}; CObject={}; pf={}
DefineClass=setmetatable({}, {__newindex=function(t,k,v) rawset(t,k,v); _G[k]=v end})
function CObject.HasSpot(_,n) return n:match('^Trackconnector') or n:match('^Trackdirection') end
function CObject.GetSpotBeginIndex(_,n) local k,i=n:match('^(%a+)(%d+)$'); return (k=='Trackconnector' and 100 or 200)+tonumber(i) end
function CObject.GetSpotPos(h,s)
 local i=s%100; local d=({4,1,3,0,2,5})[i]+HexAngleToDirection(h.angle)
 local q,r=HexRotate(s<200 and 4 or 5,0,d); local x,y=HexToWorld(q,r)
 return point(x+h.pos.xx,y+h.pos.yy,h.pos.zz+800)
end
function table.remove_value(t,v) for i=#t,1,-1 do if t[i]==v then table.remove(t,i) end end end
function pf.GetSpeed(t) return t.speed or 0 end
function GetPitchYaw() return 0 end
function newhub(rotation, is_start)
 local h=setmetatable({valid=true,pos=point(13000,17320,10000),angle=rotation*3600,
   track_busy={},last_connector_idx=6,hub_connector_directions=SMROptInTrainHub6Base.hub_connector_directions},
   {__index=SMROptInTrainHubBase})
 function h:GetEntity() return 'SMROptInTrainHub6' end
 function h:GetAngle() return self.angle end
 function h:GetPos() return self.pos end
 function h:GetPosXYZ() return self.pos.xx,self.pos.yy,self.pos.zz end
 function h:GetDist2D(p) return round(math.sqrt((self.pos.xx-p.xx)^2+(self.pos.yy-p.yy)^2)) end
 function h:GetConnectorElement(i) return self.elements and self.elements[i] end
 function h:GetConnectionSpot(t) return t and t.idx end
 h.elements={}; h.tracks={}
 for i=1,6 do
  local tr={valid=true,idx=i,assigned_vehicles={}}
  function tr:GetStartStation() return is_start and h or false end
  function tr:IsTrackFreeFor(train,start_station)
   for _,other in ipairs(self.assigned_vehicles) do
    if other~=train and not other.at_station and other.current_station==(start_station or train.current_station) then return false end
   end
   return true
  end
  h.tracks[i]=tr
  local el={valid=true,track_obj=tr,pos=CObject.GetSpotPos(h,100+i)}
  local d=({4,1,3,0,2,5})[i]+rotation+(is_start and 3 or 0)
  local a=math.rad(d*60)
  function el:GetPos() return self.pos-point(0,0,800) end
  function el:GetSpotBeginIndex(s) return s=='Enter1' and 1 or 2 end
  function el:GetSpotPos(s)
   local off=s==1 and 289 or -289
   return self.pos+point(round(-math.sin(a)*off),round(math.cos(a)*off),0)
  end
  h.elements[i]=el
 end
 return h
end
function newtrain(h,k)
 local t={valid=true,track=h.tracks[k],current_station=false,station_arrival_track=k,
   at_station=false,command='GotoStation',command_thread={},segments={},turns={},speed=500}
 t.pos=h.elements[k]:GetSpotPos(t.track:GetStartStation()==h and 2 or 1)
 t.yaw=(h.hub_connector_directions[k]*3600+h.angle+10800)%21600
 function t:GetPos() return self.pos end
 function t:GetDist2D(p) return round(math.sqrt((self.pos.xx-p.xx)^2+(self.pos.yy-p.yy)^2)) end
 function t:GetNominalMoveSpeed() return 1500 end
 function t:AssignToTrack(track)
  table.remove_value(self.track.assigned_vehicles,self); self.track=track
  track.assigned_vehicles[#track.assigned_vehicles+1]=self
 end
 function t:GetAccelerationAndTime(p,final,start) self.speed=final; return 0,math.max(1,self:GetDist2D(p)) end
 function t:SetPos(p,time)
  self.segments[#self.segments+1]={from={self.pos.xx,self.pos.yy,self.pos.zz},to={p.xx,p.yy,p.zz},time=time or 0,yaw=self.yaw}
  self.pos=p
 end
 function t:SetAngle(a,time) self.turns[#self.turns+1]={yaw=a,time=time or 0}; self.yaw=a%21600 end
 function t:SetAcceleration(a) end
 function t:StopInterpolation() end
 function t:WaitChangeDir(_,_,_,time) Sleep(time) end
 t.GotoSpot=Train.GotoSpot
 return t
end
function atstop(h,k)
 local t=newtrain(h,k); t.pos=h:GetSpotPos(h:GetSpotBeginIndex('Stop'..k)); t.current_station=h; t.at_station=true
 h:AddOccupyingTrain(t,k,true); return t
end
function assertclose(a,b,epsilon) assert(math.abs(a-b)<=(epsilon or 2), tostring(a)..' != '..tostring(b)) end
'''


def between(text, start, end):
    return text[text.index(start):text.index(end)]


def plain(value):
    if not hasattr(value, "items"):
        return value
    items = list(value.items())
    if items and all(isinstance(k, int) for k, _ in items):
        return [plain(value[i]) for i in range(1, len(items) + 1)]
    return {str(k): plain(v) for k, v in items}


def run():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(STUBS)
    code = SOURCE.read_text(encoding="utf-8")
    lua.execute(code[:code.index("-- Vanilla creates only indices 0..4")])
    lua.execute(between(code, "DefineClass.SMROptInTrainHub6Base =", "-- The BuildingTemplate companion"))
    station = (ARCHIVE / "Lua/Buildings/Station.lua").read_text(encoding="utf-8")
    train = (ARCHIVE / "Lua/Units/Train.lua").read_text(encoding="utf-8")
    lua.execute("Train={}")
    lua.execute(between(train, "function Train:GotoSpot(", "function Train:WaitTraverseElement("))
    lua.execute(between(station, "function Station:TrainArrive(", "function Station:AddOccupyingTrain("))
    lua.execute(between(station, "function Station:RemoveOccupyingTrain(", "function Station:GetOccupyingTrain("))
    lua.execute("TEST_DEFAULT_PARK=SMROptInTrainFloor.HubParkDistance")
    # All rotations, connector directions, and both track start/end states.
    checks = lua.execute(r'''
local results={}
for rotation=0,5 do for _,start in ipairs({true,false}) do for k=1,6 do
 local h=newhub(rotation,start); local t=newtrain(h,k)
 h:AddOccupyingTrain(t,h.tracks[k],true)
 local arriving=t.pos
 Station.TrainArrive(h,t,h.tracks[k])
 local stop=h:GetSpotPos(h:GetSpotBeginIndex('Stop'..k))
 local spawn=h:GetSpotPos(h:GetSpotBeginIndex('Spawn'..k))
 assertclose(stop.xx,spawn.xx,0); assertclose(stop.yy,spawn.yy,0)
 local _,angle=h:GetSpotAxisAngle(h:GetSpotBeginIndex('Spawn'..k))
 assertclose(angle%21600,(h.hub_connector_directions[k]*3600+h.angle)%21600,2)
 assert(t.at_station and t.current_station==h)
 for _,s in ipairs(t.segments) do
  assert(s.time>0,'arrival teleported')
  assertclose(s.to[3],h.pos.zz+800,0)
  local yaw=CalcOrientation(point(s.from[1],s.from[2]),point(s.to[1],s.to[2]))
  local delta=(yaw-t.yaw+10800)%21600-10800
  assertclose(delta,0,5)
 end
 assert(h:GetOccupyingTrain(h.tracks[k],true)==t)
 -- The old opposite-key save normalizes to its actual arrival connector.
 h.track_busy={[k%2==1 and k+1 or k-1]=t}
 assert(h:GetOccupyingTrain(h.tracks[k],true)==t)
 -- Changing the park control cannot invalidate a stopped reservation.
 SMROptInTrainFloor.HubParkDistance=2300
 assert(h:GetOccupyingTrain(h.tracks[k],true)==t)
 SMROptInTrainFloor.HubParkDistance=TEST_DEFAULT_PARK
 -- Reverse can see its own lane free, while a spawning thread cannot.
 t.command='LoadTrain'; active_thread=t.command_thread
 assert(h:GetOccupyingTrain(h.tracks[k])==nil)
 active_thread={}; assert(h:GetOccupyingTrain(h.tracks[k])==t)
 results[#results+1]={rotation=rotation,hub_is_start=start,connector=k,pass=true}
end end end
return results
''')
    paths = {}
    for mode in ("stop", "pass"):
        for k in range(1, 7):
            for j in range(1, 7):
                if mode == "pass" and k == j:
                    continue
                lua.globals().k, lua.globals().j = k, j
                lua.globals().mode = mode
                row = plain(lua.execute(r'''
local h=newhub(0,true); local t=newtrain(h,k)
if mode=='stop' then
 h:AddOccupyingTrain(t,k,true); Station.TrainArrive(h,t,h.tracks[k])
 t.track=h.tracks[j]; h:TrainDepart(t,h.tracks[j])
else h:TrainPassThrough(t,h.tracks[k],h.tracks[j]) end
assert(not h:HubCrossingTrain(),'lock leaked')
assert(next(h.track_busy)==nil,'reservation leaked')
local target=h.elements[j]:GetSpotPos(1)
assertclose(t.pos.xx,target.xx,0); assertclose(t.pos.yy,target.yy,0)
assertclose(t.yaw,(h.hub_connector_directions[j]*3600)%21600,3)
for _,s in ipairs(t.segments) do assert(s.time>0,'position teleport'); assertclose(s.to[3],10800,0) end
for _,turn in ipairs(t.turns) do assert(turn.time>0 or (mode=='stop' and k==j),'untimed centre turn') end
return {segments=t.segments,turns=t.turns}
'''))
                paths[(mode, k, j)] = row
    concurrency = plain(lua.execute(r'''
local h=newhub(0,true); local first=atstop(h,1); local second=atstop(h,3)
active_thread=first.command_thread; assert(h:HubAcquireCrossing(first))
assert(h:GetOccupyingTrain(h.tracks[5],true)==first)
assert(not h:CanTrainTraverse(second,h.tracks[3],h.tracks[4]))
-- A simulated restored object keeps the saved owner, not an unsaved table.
local restored=newhub(0,true); restored.SMROptIn_hub_crossing=first
assert(restored:HubCrossingTrain()==first)
-- Interruption is not clearance: the train remains physically in the crossing.
first.command_thread={}; assert(h:HubCrossingTrain()==first)
local waited=0
on_sleep=function()
 waited=waited+1; assert(h:HubCrossingTrain()==first); h:RemoveOccupyingTrain(first)
end
active_thread=second.command_thread; assert(h:HubAcquireCrossing(second)); on_sleep=nil
assert(waited==1 and h:HubCrossingTrain()==second)
second.valid=false; assert(not h:HubCrossingTrain())
assert(next(h:HubReservations())==nil)
local inbound=newtrain(h,5); h:AddOccupyingTrain(inbound,5,true)
assert(not h:CanTrainTraverse(first,h.tracks[1],h.tracks[2]))
on_sleep=function() inbound.current_station=h; inbound.at_station=true end
local other=newtrain(h,2); assert(h:HubAcquireCrossing(other)); on_sleep=nil
local oldhub=newhub(0,true); local legacy=newtrain(oldhub,1); local parked=atstop(oldhub,2)
oldhub.trains_traversing={[oldhub.tracks[1]]=legacy}
assert(oldhub:HubCrossingTrain()==legacy)
oldhub.city={labels={Train={legacy,parked}}}
local oldpos=legacy.pos; parked.pos=point(0,0,0)
oldhub:HubRestoreParkedTrains()
assert(legacy.pos==oldpos,'migration touched moving train')
assertclose(parked.pos.xx,oldhub:GetSpotPos(oldhub:GetSpotBeginIndex('Stop2')).xx,0)
local waited_legacy=0
on_sleep=function() waited_legacy=waited_legacy+1; oldhub.trains_traversing={} end
assert(oldhub:HubAcquireCrossing(parked)); on_sleep=nil
assert(waited_legacy==1)
local outboundhub=newhub(0,true); local through=newtrain(outboundhub,1); local departing=atstop(outboundhub,3)
departing.current_station=outboundhub; departing.at_station=false; departing:AssignToTrack(outboundhub.tracks[2])
assert(not outboundhub:CanTrainTraverse(through,outboundhub.tracks[1],outboundhub.tracks[2]))
departing.at_station=true
assert(outboundhub:CanTrainTraverse(through,outboundhub.tracks[1],outboundhub.tracks[2]))
local first_yield=true
on_sleep=function()
 if first_yield then
  first_yield=false
  assert(through.track==outboundhub.tracks[2] and through.current_station==outboundhub)
  assert(not outboundhub.tracks[2]:IsTrackFreeFor(departing,outboundhub))
 end
end
outboundhub:TrainPassThrough(through,outboundhub.tracks[1],outboundhub.tracks[2]); on_sleep=nil
assert(not first_yield)
return {exclusive=true,restore_field_retained=true,interruption_blocks=true,wait_then_release=true,invalid_removed=true,inbound_blocks=true,legacy_crossing_wait=true,parked_migration=true,outgoing_reserved_before_yield=true}
'''))
    # Use the oracle as a library, supplying actual executed paths, not its
    # old Lua regex model. No instrument source or global is modified.
    spec = importlib.util.spec_from_file_location("hub_oracle", ORACLE)
    oracle = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = oracle
    spec.loader.exec_module(oracle)
    model = object.__new__(oracle.Oracle)
    model.paths, model.train_w, model.verdicts = paths, 416, []
    model._two_train()
    compared = []
    keys = sorted(paths)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if a[:2] == b[:2]:
                continue
            distance = min(oracle.seg_seg_dist(sa["from"][:2], sa["to"][:2], sb["from"][:2], sb["to"][:2])
                           for sa in paths[a]["segments"] for sb in paths[b]["segments"])
            compared.append({"a": list(a), "b": list(b), "distance": distance, "conflict": distance < 416})
    assert len(compared) == model.two_train["pairs"]
    assert sum(x["conflict"] for x in compared) == model.two_train["within_a_train_width"]
    result = {
        "command": subprocess.list2cmdline(["python", *sys.argv]),
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "oracle_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ORACLE.parent, text=True).strip(),
        "inputs": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                   (SOURCE, Path(__file__), ORACLE, ARCHIVE / "Lua/Buildings/Station.lua", ARCHIVE / "Lua/Units/Train.lua")},
        "limitations": "Mocked engine; width-only spatial conflicts, not time simulation, length, mesh clearance or observed motion. R-TRAIN remains disputed.",
        "lane_reservation_checks": plain(checks), "concurrency": concurrency,
        "paths": {str(k): v for k, v in paths.items()}, "two_train": model.two_train,
        "compared_pairs": compared,
    }
    print(f"PASS: {len(checks)} lane/reservation cases; {len(paths)} executed routes; concurrency assertions passed.")
    print("TWO-TRAIN (unlocked spatial prediction):", model.two_train)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
