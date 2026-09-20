"""Small mocked contract smoke for the centre/transition prototype; no oracle.

This checks Lua control flow, reservations and power gating, not the look,
native interpolation, loading cargo or serialization. The owner smoke is owed.
"""
import subprocess

from lupa import LuaRuntime
from traffic_smoke import ARCHIVE, ROOT, SOURCE, STUBS, between

lua = LuaRuntime(unpack_returned_tuples=True)
# Reuse the existing mocked engine, with this model's five-hex connector.
lua.execute(STUBS.replace("for k=1,4 do", "for k=1,5 do")
            .replace("s<200 and 4 or 5", "s<200 and 5 or 6"))
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
lua.execute(r'''
local h=newhub(1,false)
local t=newtrain(h,1)
h:AddOccupyingTrain(t,h.tracks[1],true)
local watched=false
on_sleep=function()
 assert(h:GetOccupyingTrain(h.tracks[2],true)==t,'second arrival must wait outside')
 watched=true
end
h:TrainArrive(t,h.tracks[1]); on_sleep=nil
assert(watched and t.at_station and t.current_station==h)
assert(not h:HubCrossingTrain())
local stop=h:GetSpotPos(h:GetSpotBeginIndex('Stop1'))
assertclose(t.pos.xx,stop.xx); assertclose(t.pos.yy,stop.yy)
assertclose(h:GetDist2D(stop),SMROptInTrainFloor.HubParkDistance)
local ramp=h:GetSpotPos(h:GetSpotBeginIndex('Ramparrive1'))
assertclose(t.segments[1].to[1],ramp.xx); assertclose(t.segments[1].to[2],ramp.yy)
for _,segment in ipairs(t.segments) do assert(segment.time>0,'arrival teleported') end
assert(h:GetOccupyingTrain(h.tracks[1],true)==t,'park reservation lost')
t.command='LoadTrain'; active_thread=t.command_thread
assert(not h:GetOccupyingTrain(h.tracks[1],false),'own load must be allowed')
active_thread={}
assert(h:GetOccupyingTrain(h.tracks[1],false)==t,'spawn must remain excluded')
-- Reverse departure rejoins the track's own outgoing lane and releases.
t.command='GotoStation'; t:AssignToTrack(h.tracks[1]); t.at_station=false
h:TrainDepart(t,h.tracks[1])
local dest=h.elements[1]:GetSpotPos(2)
assertclose(t.pos.xx,dest.xx); assertclose(t.pos.yy,dest.yy)
assert(not h:HubCrossingTrain() and not h:GetOccupyingTrain(h.tracks[1],false))
-- One other-line through movement exercises entry, centre pivot, and exit.
local through=newtrain(h,1)
h:TrainPassThrough(through,h.tracks[1],h.tracks[3])
dest=h.elements[3]:GetSpotPos(2)
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
print("HEAD", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip())
print("PASS: mocked movement/reservations, occupied-exit exclusion, same-line reverse/release, power gating.")
print("Owner visual smoke and native cold-start/save-load checks remain pending; no oracle run.")
