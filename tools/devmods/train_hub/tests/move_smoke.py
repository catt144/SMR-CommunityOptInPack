"""Small mocked contract smoke for the centre/transition prototype; no oracle.

This checks Lua control flow, reservations and power gating, not the look,
native interpolation, loading cargo or serialization. The owner smoke is owed.
"""
import subprocess

from lupa import LuaRuntime
from traffic_smoke import ARCHIVE, ROOT, SOURCE, STUBS, between

lua = LuaRuntime(unpack_returned_tuples=True)
# Reuse the existing mocked engine with the longer-stub six-hex connector.
lua.execute(STUBS.replace("for k=1,4 do", "for k=1,6 do")
            .replace("s<200 and 4 or 5", "s<200 and 6 or 7"))
lua.execute("sqrt=math.sqrt; Min=math.min")
code = SOURCE.read_text(encoding="utf-8")
lua.execute(code[:code.index("-- Vanilla creates only indices 0..4")])
lua.execute(between(code, "DefineClass.SMROptInTrainHub6Base =", "-- The BuildingTemplate companion"))
train = (ARCHIVE / "Lua/Units/Train.lua").read_text(encoding="utf-8")
station = (ARCHIVE / "Lua/Buildings/Station.lua").read_text(encoding="utf-8")
base = (ARCHIVE / "Lua/Buildings/BaseBuilding.lua").read_text(encoding="utf-8")
lua.execute("Train={}; BaseBuilding={}")
lua.execute(between(train, "function Train:GotoSpot(", "function Train:WaitTraverseElement("))
lua.execute(between(station, "function Station:RemoveOccupyingTrain(", "function Station:GetOccupyingTrain("))
lua.execute(between(base, "function BaseBuilding:SetWorking(", "function BaseBuilding:Setexceptional_circumstances("))
lua.execute(between(code, "function SMROptInTrainHubBase:CreateElectricityElement(", "function SMROptInTrainHubBase:InitHubLaunchPad("))
lua.execute(between(train, "function Train:WaitTraverseElement(", "function Train:GetNominalMoveSpeed("))
lua.execute(between(train, "function Train:Traverse(", "function Train:GetNextStationName("))
lua.execute(r'''
-- Extend the old fixture with real track ordering beyond each connector.
local oldhub,oldtrain=newhub,newtrain
function newhub(rotation,is_start)
 local h=oldhub(rotation,is_start)
 for i,tr in ipairs(h.tracks) do
  local connector=h.elements[i]
  connector.direction=0; connector.traverse_pitch=0
  function connector:GetAngle() return CalcOrientation(h:GetPos(),self.pos) end
  local radial=MulDivRound(connector.pos-h:GetPos(),1,6)
  radial=point(radial:x(),radial:y(),0)
  local function outside(n)
   local e={valid=true,direction=0,traverse_pitch=0,pos=connector.pos+MulDivRound(radial,n,1)}
   function e:GetPos() return self.pos end
   function e:GetAngle() return connector:GetAngle() end
   e.GetSpotBeginIndex=connector.GetSpotBeginIndex
   function e:GetSpotPos(spot) return connector:GetSpotPos(spot)+MulDivRound(radial,n,1) end
   return e
  end
  local near,far=outside(1),outside(2)
  tr.elements=is_start and {connector,near,far} or {far,near,connector}
  tr.first_outside=near
 end
 return h
end
function newtrain(h,k)
 local t=oldtrain(h,k)
 t.WaitTraverseElement=Train.WaitTraverseElement; t.Traverse=Train.Traverse
 function t:GetDepartedStation() return self.current_station end
 function t:CheckValidDest() return true end
 function t:ShouldStopOnTrack() return false end
 function t:SetMoveSpeed(speed) self.speed=speed end
 function t:GetRollPitchYaw() return 0,0,self.yaw end
 function t:SetRollPitchYaw(_,_,yaw) self.yaw=yaw end
 function t:SetState() end
 function t:DestroySilent() self.valid=false end
 return t
end
function HandleTrainOnBrokenTrack() return false end
local world_to_hex=WorldToHex
function WorldToHex(p) return world_to_hex(p.pos or p) end
function ResolveMap() return {object_hex_grid={}} end
function IsPointStationTrackConnection() return nil end
local h=newhub(1,false)
assertclose(h:GetDist2D(h:GetSpotPos(h:GetSpotBeginIndex('Trackconnector1'))),60*guim)
for _,distance in ipairs({SMROptInTrainFloor.HubSidingEntryDistance,
 SMROptInTrainFloor.HubSidingRejoinDistance,SMROptInTrainFloor.HubSidingReverseRejoinDistance}) do
 assertclose(h:GetDist2D(h:HubCentrePosition(1,distance)),distance)
end
local t=newtrain(h,1)
local movement={}
local move=h.HubMoveTrain
function h:HubMoveTrain(train,pos,speed,yaw)
 movement[#movement+1]={speed=speed,pos=pos}
 return move(self,train,pos,speed,yaw)
end
h:AddOccupyingTrain(t,h.tracks[1],true)
local watched=false
on_sleep=function()
 assert(h:GetOccupyingTrain(h.tracks[2],true)==t,'second arrival must wait outside')
 watched=true
end
h:TrainArrive(t,h.tracks[1]); on_sleep=nil
assert(watched and t.at_station and t.current_station==h)
assert(not h:HubCrossingTrain())
-- Entry speed is fixed, while the lateral move exactly matches the outer
-- slide's eight 150 ms samples and reaches the parked point without a stop.
assert(movement[#movement].speed==t:GetNominalMoveSpeed()/3,
 'siding approach speed depends on run length')
local slide_start=point(t.segments[#t.segments-7].from[1],t.segments[#t.segments-7].from[2],
 t.segments[#t.segments-7].from[3])
local stop=h:GetSpotPos(h:GetSpotBeginIndex('Stop1'))
local hub_centre=point(h.pos.xx,h.pos.yy,slide_start.zz)
local axis=h:HubCentrePosition(1,guim)-hub_centre
local total=stop-slide_start
local lateral_total=MulDivRound(total.xx,axis.yy,guim)-MulDivRound(total.yy,axis.xx,guim)
for i=#t.segments-7,#t.segments do
 local segment=t.segments[i]
 local n=i-(#t.segments-7)+1
 local f=MulDivRound(n*n*(24-2*n),1000,512)
 local p=point(segment.to[1],segment.to[2],segment.to[3])-slide_start
 local lateral=MulDivRound(p.xx,axis.yy,guim)-MulDivRound(p.yy,axis.xx,guim)
 assert(segment.time==150,'siding slide rate differs from outer slide')
 assertclose(lateral,MulDivRound(lateral_total,f,1000),3)
end
assertclose(t.pos.xx,stop.xx); assertclose(t.pos.yy,stop.yy)
local centre=h:HubCentrePosition(1,SMROptInTrainFloor.HubParkDistance)
assertclose(t:GetDist2D(centre),SMROptInTrainFloor.HubSidingOffset)
local ramp=h:GetSpotPos(h:GetSpotBeginIndex('Ramparrive1'))
assertclose(t.segments[1].to[1],ramp.xx); assertclose(t.segments[1].to[2],ramp.yy)
for _,segment in ipairs(t.segments) do assert(segment.time>0,'arrival teleported') end
assert(h:GetOccupyingTrain(h.tracks[1],true)==t,'park reservation lost')
t.command='LoadTrain'; active_thread=t.command_thread
assert(not h:GetOccupyingTrain(h.tracks[1],false),'own load must be allowed')
active_thread={}
assert(h:GetOccupyingTrain(h.tracks[1],false)==t,'spawn must remain excluded')
-- Reverse departure rejoins the track's own outgoing lane and releases.
local slide=h.HubSlideTrain
local exit_checked=false
function h:HubSlideTrain(train,destination)
 local expected=self:HubCentrePosition(1,SMROptInTrainFloor.HubExitSlideDistance)
 assertclose(train.pos.xx,expected.xx); assertclose(train.pos.yy,expected.yy)
 exit_checked=true
 return slide(self,train,destination)
end
t.command='GotoStation'; t:AssignToTrack(h.tracks[1]); t.at_station=false
local acceleration=t.GetAccelerationAndTime
local handoff_start,handoff_final
function t:GetAccelerationAndTime(pos,final,start)
 handoff_start,handoff_final=start,final
 return acceleration(self,pos,final,start)
end
h:TrainDepart(t,h.tracks[1])
assert(exit_checked,'departure missed outward slide')
assert(handoff_start==t:GetNominalMoveSpeed(h.elements[1]) and handoff_final==handoff_start,
 'post-slide handoff must start and finish at outgoing nominal speed')
h.HubSlideTrain=nil
local unchanged_arrival=h:GetSpotPos(h:GetSpotBeginIndex('Ramparrive1'))
assertclose(unchanged_arrival.xx,ramp.xx); assertclose(unchanged_arrival.yy,ramp.yy)
local dest=h.tracks[1].first_outside:GetSpotPos(2)
assertclose(t.pos.xx,dest.xx); assertclose(t.pos.yy,dest.yy)
assert(not h:HubCrossingTrain() and not h:GetOccupyingTrain(h.tracks[1],false))
-- One other-line through movement exercises entry, centre pivot, and exit.
local through=newtrain(h,1)
h:TrainPassThrough(through,h.tracks[1],h.tracks[3])
assert(through.speed==through:GetNominalMoveSpeed(h.elements[3]),'through exit retains crawl speed')
dest=h.tracks[3].first_outside:GetSpotPos(2)
assertclose(through.pos.xx,dest.xx); assertclose(through.pos.yy,dest.yy)
assert(not h:HubCrossingTrain())
assert(#through.turns>0,'other-line path missed its pivot')

-- Exit-contact regression: vanilla permits this track because its train is
-- parked. The hub must reject both through admission and crossing acquisition.
-- A same-line reverse by the blocker must remain possible, then the follower
-- waits until that departing train also clears vanilla's outgoing track.
local qh=newhub(0,true)
local blocker=atstop(qh,3)
blocker.command='LoadTrain'
local follower=newtrain(qh,1)
assert(qh.tracks[3]:IsTrackFreeFor(follower,qh),'fixture must reproduce vanilla parked exemption')
assert(not qh:HubExitClear(follower,qh.tracks[3]),'parked exit train ignored')
assert(not qh:CanTrainTraverse(follower,qh.tracks[1],qh.tracks[3]),'through train admitted into parked exit')
assert(qh:HubExitClear(blocker,qh.tracks[3]),'own-line reverse incorrectly blocked')
local start=follower:GetPos()
local waits=0
function WaitMsg()
 waits=waits+1; assert(waits==1,'crossing failed to wake after exit cleared')
 assert(not qh:HubCrossingTrain(),'waiting follower owns crossing')
 assertclose(follower.pos.xx,start.xx); assertclose(follower.pos.yy,start.yy)
 blocker.command='GotoStation'; blocker:AssignToTrack(qh.tracks[3])
 qh:TrainDepart(blocker,qh.tracks[3])
 assert(not qh:HubExitClear(follower,qh.tracks[3]),'departing train lost vanilla track exclusion')
 -- Simulate completion of vanilla Traverse/arrival at the far station.
 blocker.current_station=false; blocker.at_station=true
 table.remove_value(qh.tracks[3].assigned_vehicles,blocker)
 assert(qh:HubExitClear(follower,qh.tracks[3]))
end
assert(qh:HubAcquireCrossing(follower,qh.tracks[3]))
assert(waits==1 and qh:HubCrossingTrain()==follower)
qh:RemoveOccupyingTrain(follower)
-- A loaded departure must stay on its siding until the exit guard clears.
local parked=atstop(qh,1)
local occupied=atstop(qh,3)
parked.command='GotoStation'; parked:AssignToTrack(qh.tracks[3])
local siding=parked:GetPos()
local held=false
function WaitMsg()
 assert(parked.at_station and not qh:HubCrossingTrain())
 assertclose(parked.pos.xx,siding.xx); assertclose(parked.pos.yy,siding.yy)
 held=true
 qh:RemoveOccupyingTrain(occupied)
end
qh:TrainDepart(parked,qh.tracks[3])
assert(held and not qh:HubCrossingTrain(),'loaded departure did not wait/release')
-- Load migration keeps a parked train at the siding and reservations intact.
local restored=atstop(qh,2)
qh.city={labels={Train={restored}}}
restored.pos=point(0,0,0)
qh:HubRestoreParkedTrains()
local restored_stop=qh:GetSpotPos(qh:GetSpotBeginIndex('Stop2'))
assertclose(restored.pos.xx,restored_stop.xx); assertclose(restored.pos.yy,restored_stop.yy)
assert(qh:GetOccupyingTrain(qh.tracks[2],false)==restored)

-- Reproduce the former native handoff snap, then check corrected departures
-- and through paths in both track orders against the archived Traverse body.
for _,is_start in ipairs({true,false}) do
 local j=newhub(0,is_start)
 local legacy=newtrain(j,1)
 legacy.current_station=j
 local spot=is_start and 1 or 2
 legacy.pos=j.elements[1]:GetSpotPos(spot)
 legacy:Traverse(j.tracks[1],true)
 local first=legacy.segments[1]
 assert(first.time==0 and (first.from[1]~=first.to[1] or first.from[2]~=first.to[2]),
  'fixture failed to reproduce connector-to-next-element teleport')
 for _,passing in ipairs({false,true}) do
  local moving=passing and newtrain(j,1) or atstop(j,1)
  if passing then j:TrainPassThrough(moving,j.tracks[1],j.tracks[3])
  else j:TrainDepart(moving,j.tracks[1]) end
  local track=j.tracks[passing and 3 or 1]
  local before=#moving.segments
  moving:Traverse(track,true)
  for n=before+1,#moving.segments do
   local segment=moving.segments[n]
   if segment.time==0 then
    assertclose(segment.from[1],segment.to[1]); assertclose(segment.from[2],segment.to[2])
    assertclose(segment.from[3],segment.to[3])
   end
  end
 end
end

SupplyGridElement={new=function(_,element)
 function element:SetProduction(value) self.production=value end
 function element:SetConsumption(value) self.consumption=value end
 return element
end}
function h:GetPerformanceModifiedElectricityProduction() return 70000 end
function h:DoesHaveConsumption() return false end
function h:DoesHaveUpgradeConsumption() return false end
function h:UpdateNotWorkingBuildingsNotification() end
-- Model the producer callback that the combined vanilla method invokes.
function h:OnSetWorking(work) self.electricity:SetProduction(work and 70000 or 0) end
h.working=false; h.ui_working=true; h.is_malfunctioned=false
h:CreateElectricityElement()
assert(h.electricity.production==70000 and h.electricity.consumption==10000)
h:SetWorking(false); assert(h.electricity.production==70000)
h.ui_working=false; h:SetWorking(false); assert(h.electricity.production==0)
h.ui_working=true; h:SetWorking(false); assert(h.electricity.production==70000)
h.is_malfunctioned=true; h:SetWorking(false); assert(h.electricity.production==0)
h.is_malfunctioned=false; h:SetWorking(false); assert(h.electricity.production==70000)
h.electricity.production=0; h:OnModifiableValueChanged('electricity_production')
assert(h.electricity.production==70000)
''')
# Exercise the archived command bodies, including time consumed before their wait.
lua.execute("local Floor=SMROptInTrainFloor\n" + between(code, "local function hub_dwell_train(", "local hub_work_radius") + "\nInstallHubDwell=install_hub_dwell")
lua.execute(between(train, "function Train:LoadTrain()", "function Train:WaitForTrack("))
lua.execute(between(train, "function Train:UnloadTrain()", "function Train:IsStoppingOn("))
lua.execute(r'''
const.HourDuration=60000
local clock=0
function GameTime() return clock end
function PlayFX() end
function IsBeingDestructed() return false end
function ripairs(t) local i=#t+1; return function() i=i-1; if i>0 then return i,t[i] end end end
local original_waits={}
function WaitWakeup(timeout,...)
 original_waits[#original_waits+1]=timeout
 clock=clock+timeout
 return 'delegated',42
end
local hub=newhub(0,true)
local train=newtrain(hub,1)
hub.city={labels={Train={train}}}
function AllMapsForEach(_,class,fn,...) assert(class=='SMROptInTrainHubBase'); fn(hub,...) end
InstallHubDwell()
local installed=WaitWakeup
InstallHubDwell(); assert(WaitWakeup==installed,'double installation')
train.at_station=true; train.at_spawn_track=true; train.units={}
train.current_station=hub; active_thread=train.command_thread
local transfer_time=0
function train:TransferCargo() clock=clock+transfer_time; return true,{},{} end
function train:SetCommand(command) self.command=command end
function train:PushDestructor(fn) self.destructor=fn end
function train:PopAndCallDestructor() self.destructor(self); clock=clock+transfer_time end
function train:QueueCommand(command) self.queued=command end
for _,elapsed in ipairs({0,4000,7000,13000}) do
 for _,command in ipairs({'LoadTrain','UnloadTrain'}) do
  clock=0; transfer_time=elapsed; train.command=command
  Train[command](train)
  assert(clock==math.max(6000,elapsed+100),'hub deadline/floor changed')
 end
end
-- Foreign station, foreign command and another thread retain vanilla wait.
local foreign={valid=true}
train.track.GetStartStation=function() return foreign end
train.current_station=foreign
clock=0; transfer_time=0; train.command='LoadTrain'
Train.LoadTrain(train); assert(clock==12000,'vanilla station dwell changed')
train.current_station=hub; train.command='Idle'; clock=0
local a,b=WaitWakeup(12000); assert(clock==12000 and a=='delegated' and b==42)
train.command='LoadTrain'; active_thread={}; clock=0
WaitWakeup(12000); assert(clock==12000,'foreign thread changed')
active_thread=train.command_thread; clock=0; SMROptInTrainFloor.HubDwellTime=5000
WaitWakeup(12000); assert(clock==5000,'live dwell tuning ignored')
SMROptInTrainFloor.HubDwellTime=6000
''')
print("HEAD", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip())
print("PASS: mocked movement/reservations, exit handoff without displacement on vanilla teleport, occupied-exit exclusion, same-line reverse/release, power gating, archived dwell commands and vanilla control.")
print("Owner visual smoke and native cold-start/save-load checks remain pending; no oracle run.")
