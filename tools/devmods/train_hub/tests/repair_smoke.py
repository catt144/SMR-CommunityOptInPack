"""Execute the hub's TRACK WORK section (20_TrainHub.lua, drones chain L4) against a mocked
engine and a deterministic track graph. Requires lupa, as the adjacent smokes do.

No game, render, import, save-file or clearance evidence. What this holds: the hub-rooted graph
(the far side of a break reachable, an isolated network excluded, a tunnel pair crossed, a cycle
terminating, unfinished new track excluded); dispatch under the switch, the toggle, the ceiling
and the stock (the claim taken all-or-nothing, the maintenance reserve never touched, short stock
signed and retried); completion at the deadline through the live group leader at the OUTSTANDING
cost at the hub's rate (50 % without SafeTransport, 100 % with it), nothing paid twice; a site the
drones finished first dropped silently; a malfunctioned or unpowered hub still dispatching and
completing; the fleet tiers, the recall rules and the ceiling shared with repair flights; a
destroyed hub despawning every drone with its cube dropped first; the load sweep and adoption;
the control wrap's scope; the persisted shape (plain data and object references only, one field);
and static gates on the section's source. Native behaviour is link 5's sitting.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "tools/devmods/train_hub/Code/20_TrainHub.lua"
code = SOURCE.read_text(encoding="utf8")
section = code[code.index("-- TRACK WORK (build 4"):code.index("-- The sizes. Thin by design")]
section = section[:section.rindex("-- =====")]

# Static gates on the section's source.
plain = "\n".join(line.split("--", 1)[0] for line in section.split("\n"))
assert not re.search(r"CreateGameTimeThread|CreateRealTimeThread|\bSleep\(|WaitMsg\(|WaitWakeup\(", plain), "the section owns no thread and never yields"
assert re.findall(r"rawset\(\s*self\s*,\s*(\w+)", plain) == ["TRACK_WORK"], "one persisted field, written by name"
assert 'local TRACK_WORK = "SMROptIn_track_work"' in plain
assert "SMRFixPack" not in plain, "executable code carries no fix-pack reference (ban 2)"
cmds = re.findall(r":SetCommand\(\s*\"(\w+)\"", plain)
assert set(cmds) == {"GoHome", "Idle"}, "only stock command names are written onto a drone (Idle hands a pit-launched Wasp to vanilla, L5): %r" % cmds
assert "IsWorking" not in plain and "self.working" not in plain, "dispatch reads the switch, never IsWorking (owner, 2026-09-22)"
assert "ForEachConnectedTrack" not in plain, "the one-hop helper hides broken edges (EF-114)"
assert "FlyingDrone.CanBeControlled" in plain and "local vanilla_wasp_can_be_controlled = FlyingDrone.CanBeControlled" in plain
assert plain.count("function FlyingDrone:CanBeControlled") == 1

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
clock = 0; OnMsg = {}; empty_table = {}; SelectedObj = false
function SelectObj(o) SelectedObj = o or false end
function GameTime() return clock end
function Max(a, b) return a > b and a or b end
function Min(a, b) return a < b and a or b end
function MulDivRound(a, b, c) return math.floor(a * b / c + .5) end
function DivRound(a, b) return math.floor(a / b + .5) end
const = { HourDuration = 60000, MinuteDuration = 1000, GridSpacing = 1000, DroneBatteryMax = 80000 }
weak_keys_meta = { __mode = "k" }
function IsValid(o) return type(o) == "table" and o.valid == true and not o.deleted end
function IsBeingDestructed(o) return type(o) == "table" and o.destructing or false end
function IsKindOf(o, c) return type(o) == "table" and o.classes ~= nil and o.classes[c] == true end
function table.find(t, v) for i, x in ipairs(t) do if x == v then return i end end end
function table.keys(t) local r = {} for k in pairs(t) do r[#r + 1] = tostring(k) end table.sort(r) return r end
function table.remove_entry(t, v) local i = table.find(t, v) if i then table.remove(t, i) return i end end
function T(id, text, ...) if type(id) == "table" then local s = id[2] for k, v in pairs(id) do if type(k) == "string" then s = s:gsub("<" .. k .. ">", tostring(v)) end end return s end return text end
function Untranslated(s) return s end
function RebuildInfopanel() rebuilt = (rebuilt or 0) + 1 end
function ResolvePropObj(c) return c end
function DoneObject(o) assert(IsValid(o), "DoneObject on a dead object") o.deleted = true; removed = (removed or 0) + 1 end
notifications = {}
function AddOnScreenNotification(id, cb, params, objs, map) notifications[#notifications + 1] = { id = id, text = params.override_text, objs = objs } end
NotificationPresets = {}; XTemplates = {}
created_ui = {}
local function ui_class(name) local c = {} function c.new(cls, props, parent, ctx) local o = { class = name, props = props, parent = parent, ctx = ctx } created_ui[#created_ui + 1] = o return o end return c end
InfopanelSection = ui_class("InfopanelSection"); InfopanelActiveSection = ui_class("InfopanelActiveSection"); InfopanelText = ui_class("InfopanelText")
function InfopanelSection.__content(o) return o end
sectionCustom = {}; function sectionCustom.Init(self, parent, context) self.vanilla_init = true end
placed = {}
function PlaceObj(class, props, children) local o = { class = class, props = props, children = children } placed[#placed + 1] = o return o end
UIColony = { safe = false, IsTechResearched = function(self, id) return id == "SafeTransport" and self.safe end }
hubs, drones_all = {}, {}
function AllMapsForEach(mode, class, fn)
  if class == "SMROptInTrainHubBase" then for _, h in ipairs(hubs) do fn(h) end
  elseif class == "FlyingDrone" then for _, d in ipairs(drones_all) do fn(d) end end
end
function GetRandomPassableAroundOnMap(map, centre, outer, inner) return { x = centre.x + (inner or 0), y = centre.y } end
function longest_line() return 4 end
hub_drone_battery_max = 100 * const.DroneBatteryMax
hub_reactor_channels = 4
hub_reactor_palettes = { P4 = { channels = { { color = 1 }, { color = 2 }, { color = 3 }, { color = 4 } } } }
SMROptInTrainFloor = {}
TaskRequester = { ShouldAddRequestToCommandCenter = function() return true end }
Station = {}
DroneControl = {}
function DroneControl.KillDrone(self, d) assert(table.remove_entry(self.drones, d), "KillDrone asserts fleet membership") DoneObject(d) end
function DroneControl.Finalize(self) self.finalized = (self.finalized or 0) + 1 for _, d in ipairs(self.drones) do d.orphaned = true end end
-- vanilla's drone-coverage verdict for a construction site
ConstructionSite = {}
function ConstructionSite.IsOutsideCommandRange(self) return true end
-- vanilla's building destruction and the meteor FX
destroyed_log = {}
function DestroyBuildingImmediate(bld, params) destroyed_log[#destroyed_log + 1] = { bld = bld, reason = params and params.reason } bld.destroyed = true return true end
function PlayFX() end
-- vanilla's panel lines, declared on Drone
Drone = {}
function Drone.Getui_command(self) return "vanilla status" end
function Drone.GetDestName(self) return "vanilla dest" end
-- the Wasp
FlyingDrone = { classes = { FlyingDrone = true } }
function FlyingDrone.CanBeControlled(self) return not self.disabled end
function FlyingDrone.new(cls, params, map)
  local d = { valid = true, classes = { FlyingDrone = true }, command = "Idle", commands = {}, name = "" }
  for k, v in pairs(params or empty_table) do d[k] = v end
  function d:SetCommandCenter(cc) if self.command_center and self.command_center.drones then table.remove_entry(self.command_center.drones, self) end self.command_center = cc; if cc then cc.drones[#cc.drones + 1] = self end end
  function d:SetPos(p) self.pos = p end
  function d:GetPos() return self.pos or { x = 0, y = 0 } end
  function d:DropCarriedResource() if self.resource then self.dropped = self.resource; self.resource = false end end
  function d:StopFX() end
  function d:SetCommand(cmd, ...) self.commands[#self.commands + 1] = { cmd, ... }; self.command = cmd end
  function d:GetCarriedResource() return self.resource or false end
  function d:SetColorizationMaterial(i, color) self.painted = (self.painted or 0) + 1 end
  drones_all[#drones_all + 1] = d
  return d
end
-- the flight API (30_TrainHubDrones.lua), mocked: records made, targets sent, adoption by command
SMROptInHubFlight = { Speed = 16000, WorkTime = 5000, save_gate = false, created = 0, adopted = {} }
local F = SMROptInHubFlight
function F.Create(hub) if F.save_gate then return nil, "Save in progress" end local d = FlyingDrone:new({ command_center = hub, city = hub.city, name = "Repair Drone" }, 1) d.command = false; F.created = F.created + 1 F.last = { hub = hub, drone = d } return F.last end
function F.Send(record, target) if not IsValid(target) or not IsValid(target.track_obj) then return nil, "bad target" end record.target = target return record end
function F.Remove(record) if IsValid(record.drone) then DoneObject(record.drone) end record.removed = true end
function F.Adopt(hub, drone, target, stage)
  if drone.command ~= "FlightGoto" and drone.command ~= "WaitUninterruptable" then return nil, "Not under a stock leg or hold" end
  local r = { hub = hub, drone = drone, target = target, stage = stage } F.adopted[#F.adopted + 1] = r return r
end
-- requests, the engine's reservation shape (10_TrainFloor.lua header)
function request(amount) local r = { actual = amount, target = amount, valid = true } -- an engine object, a leaf for the shape walk
  function r:GetActualAmount() return self.actual end
  function r:GetTargetAmount() return self.target end
  function r:AssignUnit(n) if n > self.target then return false end self.target = self.target - n return true end
  function r:UnassignUnit(n) self.target = self.target + n end
  function r:AddAmount(n) self.actual = self.actual + n; self.target = self.target + n end
  return r end
-- graph objects
function station(name, near) local s = { valid = true, name = name, classes = { Station = true }, auto_connect = true, command_centers = {}, connectors = {}, near = near or false, pos = { x = 0, y = 0 } }
  function s:ForEachConnectorElement(fn) for _, el in ipairs(self.connectors) do fn(el) end end
  s.maintenance_resource_request = { valid = true, kind = 'maintenance material' }; s.maintenance_work_request = { valid = true, kind = 'maintenance work' }
  s.task_requests = { { valid = true, kind = 'supply Metals' }, { valid = true, kind = 'demand Concrete' }, s.maintenance_resource_request, s.maintenance_work_request }
  s.filed = {}
  -- DroneControl:AddBuilding files each request the building admits (DroneControl.lua:742)
  function s:AddCommandCenter(c) if table.find(self.command_centers, c) then return false end self.command_centers[#self.command_centers + 1] = c; c.connected_task_requesters[#c.connected_task_requesters + 1] = self
    self.filed[c] = {} for _, r in ipairs(self.task_requests) do if Station.ShouldAddRequestToCommandCenter(self, r, c, 'res') then self.filed[c][#self.filed[c] + 1] = r.kind end end return true end
  function s:RemoveCommandCenter(c) table.remove_entry(self.command_centers, c); table.remove_entry(c.connected_task_requesters, self); self.filed[c] = nil end
  return s end
function tunnel(name) local t = station(name) t.classes = { TrackTunnelBase = true } t.linked_obj = false return t end
function track(a, b, n) local t = { valid = true, elements = {}, elements_under_construction = {}, repair_cgs = {}, GetMap = function() return 1 end }
  for i = 1, n do t.elements[i] = { valid = true, track_obj = t, node_idx = i, pos = { x = a.pos.x + (b.pos.x - a.pos.x) * i / n, y = a.pos.y + (b.pos.y - a.pos.y) * i / n }, GetPos = function(self) return self.pos end } end
  t.elements[1].station = a; t.elements[n].station = b
  function t:GetStartStation() return self.elements[1].station end
  function t:GetEndStation() return self.elements[#self.elements].station end
  a.connectors[#a.connectors + 1] = t.elements[1]; b.connectors[#b.connectors + 1] = t.elements[n]
  return t end
-- a break: the repair group of Track.lua:628-663 and Meteors.lua:713-727, with its cost
function break_track(t, idx, cost)
  local el = t.elements[idx]
  local leader = { valid = true, classes = { ConstructionGroupLeader = true }, construction_resources = { Metals = request(cost) } }
  local site = { valid = true, is_construction_site = true, track_obj = t, broken = el }
  local cg = { leader, site }
  leader.construction_group = cg; site.construction_group = cg; el.broken = site
  t.elements_under_construction[#t.elements_under_construction + 1] = site
  t.repair_cgs[#t.repair_cgs + 1] = cg
  function leader:Complete()
    self.completed = true; el.broken = nil; table.remove_entry(t.elements_under_construction, site)
    -- 1.1.1.405907 TrackElement.lua:915-933: old groups stay until EVERY site is done.
    if #t.elements_under_construction == 0 then t.repair_cgs = {} end
    DoneObject(site); DoneObject(self)
  end
  -- drones finished it first: the same teardown, nothing paid by the hub
  function leader:DronesFinish() self:Complete() end
  return leader, el
end
function hub(x, y) local h = { valid = true, classes = { SMROptInTrainHubBase = true, Station = true }, pos = { x = x, y = y }, city = {}, drones = {},
    connected_task_requesters = {}, are_requesters_connected = true, ui_working = true, working = true, work_radius = 15, load = "low", connectors = {},
    supply = { Metals = request(20000), Concrete = request(10000) }, signs = {}, resources_added = {} }
  function h:ForEachConnectorElement(fn) for _, el in ipairs(self.connectors) do fn(el) end end
  function h:GetMap() return 1 end
  function h:GetPos() return self.pos end
  function h:GetDist2D(p) return math.floor(math.sqrt((self.pos.x - p.x) ^ 2 + (self.pos.y - p.y) ^ 2) + .5) end
  function h:GetDroneLoad() return self.load end
  function h:GetFreeDronesCount() return self.free or #self.drones end
  function h:CanCommandDrones() return self.ui_working and not self.destroyed end
  function h:IsInWorkRange(o) return o.near == true end
  function h:AttachSign(on, name) self.signs[name] = on or nil end
  function h:AddResource(amount, res) self.supply[res]:AddAmount(amount); self.resources_added[#self.resources_added + 1] = { res, amount } end
  h.KillDrone = DroneControl.KillDrone
  hubs[#hubs + 1] = h
  return setmetatable(h, { __index = SMROptInTrainHubBase })
end
''')
lua.execute("SMROptInTrainHubBase = {}\nlocal Floor = SMROptInTrainFloor\n" + section.replace("local Floor = SMROptInTrainFloor", ""))

lua.execute(r'''
F = SMROptInHubFlight; Tune = SMROptInTrainFloor.HubRepairTune
Tune.FlightGrace = 0 -- the deadline cases below complete at the deadline; the live-Wasp wait has its own case
-- The fixture: H -T1- S1(near) -T2- S2 -T3- N]tunnel[F -T4- S3 -T5- H (a cycle); I -T6- J isolated;
-- S3 -X- (unfinished new track). T2 breaks at element 3 (past S1, so the far side is beyond a break).
H = hub(0, 0)
S1 = station("S1", true); S1.pos = { x = 10000, y = 0 }
S2 = station("S2"); S2.pos = { x = 40000, y = 0 }
N = tunnel("N"); N.pos = { x = 60000, y = 0 }
Fm = tunnel("Fm"); Fm.pos = { x = 80000, y = 0 }
N.linked_obj = Fm; Fm.linked_obj = N
S3 = station("S3"); S3.pos = { x = 100000, y = 0 }
I = station("I"); I.pos = { x = 0, y = 90000 }
J = station("J"); J.pos = { x = 0, y = 100000 }
T1 = track(H, S1, 3); T2 = track(S1, S2, 6); T3 = track(S2, N, 3); T4 = track(Fm, S3, 3); T5 = track(S3, H, 8); T6 = track(I, J, 3)
X = track(S3, station("X"), 3); X.elements_under_construction = { { valid = true, is_construction_site = true, broken = false } }
keys_before = table.keys(H)
nodes, tracks = H:HubTrackGraph()
assert(nodes[S1] and nodes[S2] and nodes[N] and nodes[Fm] and nodes[S3] and not nodes[I] and not nodes[J], "graph: stations, tunnel pair, cycle; not the isolated pair")
assert(tracks[T1] and tracks[T2] and tracks[T5] and tracks[X] == false and tracks[T6] == nil, "edges: physical tracks; unfinished new track excluded")
-- a break beyond S1 keeps the far side reachable: the broken track stays a physical edge
L1, E1 = break_track(T2, 3, 4000)
nodes = H:HubTrackGraph(); assert(nodes[S2] and nodes[S3], "the far side of a break is reachable for repair")
-- an isolated break is never a job
Li = break_track(T6, 2, 4000)
''')

lua.execute(r'''
-- Dispatch: the job is recorded, the claim taken at the hub's rate, the deadline set, a Wasp sent.
clock = 1000; H:HubTrackWorkTick()
jobs = H.SMROptIn_track_work.jobs
assert(#jobs == 1 and jobs[1].site == L1 and jobs[1].el == E1 and jobs[1].track == T2 and jobs[1].kind == "repair", "one job, the on-graph break; the isolated one ignored")
local job = jobs[1]
assert(job.deadline and job.started == 1000 and not job.waiting, "dispatched on the first tick")
assert(job.held.Metals.amount == 2000 and H.supply.Metals.target == 18000 and H.supply.Metals.actual == 20000, "claimed 50 % of the 4000 outstanding, stock untouched")
assert(#notifications == 1 and notifications[1].text == "Repair drone dispatched" and notifications[1].objs[1] == E1, notifications[1].text)
-- deadline = LaunchTime + dist/Speed + WorkTime (owner option A, 2026-09-24): E1 is at x 25000; Speed is
-- a hub Wasp's live move_speed x 80 %, or the class base 1600 with none: 4000 + 25000*1000/1280 + 7000
assert(job.deadline == 1000 + 4000 + 19531 + 7000, "deadline arithmetic: " .. job.deadline)
assert(F.created == 1 and IsValid(job.drone) and job.drone.command_center == H, "one Wasp flies")
-- the panel lines on the repair flight (owner, 2026-09-24): ours by stage; every other drone vanilla's
assert(Drone.Getui_command(job.drone) == "Flying to a track repair" and Drone.GetDestName(job.drone) == "Going to<right><em>Broken track</em>")
F.last.stage = "work"; assert(Drone.Getui_command(job.drone) == "Repairing track")
F.last.stage = "back"; assert(Drone.Getui_command(job.drone) == "Returning to the Train Hub" and Drone.GetDestName(job.drone) == "Going to<right><em>Train Hub</em>")
F.last.stage = "rise"; assert(Drone.Getui_command(job.drone) == "Launching for a track repair")
F.last.stage = "out"
-- coverage (owner, 2026-09-24): a site the hub is repairing reads as covered, and its sign is refreshed
assert(ConstructionSite.IsOutsideCommandRange(job.site) == false, "the hub's job site is covered")
assert(ConstructionSite.IsOutsideCommandRange({ valid = true }) == true, "any other site is vanilla's")
-- a meteor malfunctions the hub instead of destroying it (owner, 2026-09-24); nothing else changes
H.SetMalfunction = function(self) self.meteor_malfunction = true end
assert(DestroyBuildingImmediate(H, { reason = "meteor", insurance = true }) == false and H.meteor_malfunction and not H.destroyed and #destroyed_log == 0, "the hub is damaged, not destroyed")
local shed = { valid = true, classes = { Building = true } }
assert(DestroyBuildingImmediate(shed, { reason = "meteor" }) == true and shed.destroyed, "another building still goes")
assert(#destroyed_log == 1 and destroyed_log[1].bld == shed)
H.meteor_malfunction = nil; H.SetMalfunction = nil
assert(Drone.Getui_command(H.drones[1]) == "vanilla status" and Drone.GetDestName(H.drones[1]) == "vanilla dest", "a fleet Wasp keeps vanilla's lines")
local foreign_wasp = FlyingDrone:new({ command_center = S1 }, 1)
assert(Drone.Getui_command(foreign_wasp) == "vanilla status" and Drone.GetDestName(foreign_wasp) == "vanilla dest", "a foreign Wasp keeps vanilla's lines")
-- the remote stations got the hub as a command centre; the isolated one did not
assert(table.find(S2.command_centers, H) and table.find(S3.command_centers, H) and table.find(S1.command_centers, H) and not table.find(I.command_centers, H))
assert(not table.find(N.command_centers or empty_table, H), "tunnel mouths are not stations")
-- out of range, only the two maintenance requests join the hub (owner, 2026-09-23: no resource balancing); in range, everything does
assert(#S2.filed[H] == 2 and S2.filed[H][1] == "maintenance material" and S2.filed[H][2] == "maintenance work", table.concat(S2.filed[H], ","))
assert(#S1.filed[H] == 4, "a station inside the radius keeps vanilla's full service")
assert(Station.ShouldAddRequestToCommandCenter(S2, S2.task_requests[1], S1, "res") == true, "another controller passes through to the original")
-- the panel line and the toggle read without creating anything
assert(H:GetHubRepairLine() == "Repair drones: 6 out / 30, 1 track job under way", H:GetHubRepairLine())
-- (five fleet Wasps stood up on the same tick, load low)
assert(#H.drones == 5 and H.drones[1].name == "Repair Drone" and H.drones[1].battery == hub_drone_battery_max, "the standing fleet")
-- Completion at the deadline: the leader's Complete, the outstanding cost paid once at 50 %.
clock = job.deadline - 1; H:HubTrackWorkTick(); assert(not L1.completed and #jobs == 1, "not before the deadline")
clock = job.deadline; H:HubTrackWorkTick()
assert(L1.completed and #jobs == 0, "completed at the deadline")
assert(H.supply.Metals.actual == 18000 and H.supply.Metals.target == 18000, "paid 2000 once; the claim released before paying: " .. H.supply.Metals.actual .. "/" .. H.supply.Metals.target)
assert(#H.resources_added == 1 and H.resources_added[1][1] == "Metals" and H.resources_added[1][2] == -2000)
-- Drones delivered part of it before the deadline: only the remainder is paid.
-- a site whose requests are not built yet (TrackBroken's own tick) waits a tick instead of dispatching unclaimed
local pending_site, pending_el = break_track(T2, 5, 4000); local built = pending_site.construction_resources; pending_site.construction_resources = false
clock = clock + 5000; H:HubTrackWorkTick()
local seen = false; for _, j in ipairs(jobs) do if j.site == pending_site then seen = true; assert(not j.deadline and not j.held, "no dispatch before the site's requests exist") end end; assert(seen, "the pending site is a job")
pending_site.construction_resources = built; clock = clock + 5000; H:HubTrackWorkTick()
seen = false; for _, j in ipairs(jobs) do if j.site == pending_site then seen = true; assert(j.deadline and j.held and j.held.Metals, "dispatched with its claim once they do") end end; assert(seen, "still a job")
pending_site.construction_resources.Metals.actual = 0; clock = clock + 100000; H:HubTrackWorkTick(); clock = clock + 5000; H:HubTrackWorkTick()
-- the live speed: a hub Wasp at move_speed 8960 (the owner's 5x dial and techs) sets the travel at 80 % of it
H.drones[1].move_speed = 8960
L2, E2 = break_track(T2, 4, 4000); clock = clock + 5000; H:HubTrackWorkTick()
local job2 = jobs[1]; assert(job2.site == L2 and job2.held.Metals.amount == 2000)
local d2 = H:GetDist2D(E2:GetPos())
assert(job2.deadline - job2.started == 4000 + MulDivRound(d2, 1000, 7168) + 7000, "travel at the live speed: " .. (job2.deadline - job2.started) .. " for " .. d2)
H.drones[1].move_speed = nil
L2.construction_resources.Metals.actual = 1000; L2.construction_resources.Metals.target = 1000 -- drones brought 3000
clock = job2.deadline; H:HubTrackWorkTick()
assert(L2.completed and H.supply.Metals.actual == 17500, "paid half of the 1000 still outstanding: " .. H.supply.Metals.actual)
assert(H.supply.Metals.target == 17500, "the unused claim went back")
-- SafeTransport researched: the site already costs half, the hub pays the outstanding as is.
UIColony.safe = true
L3 = break_track(T2, 5, 2000); clock = clock + 5000; H:HubTrackWorkTick()
assert(jobs[1].held.Metals.amount == 2000); clock = jobs[1].deadline; H:HubTrackWorkTick()
assert(L3.completed and H.supply.Metals.actual == 15500); UIColony.safe = false
-- Drones finished the site first: the job is dropped silently and the claim released.
L4 = break_track(T2, 2, 4000); clock = clock + 5000; H:HubTrackWorkTick()
assert(jobs[1].site == L4 and H.supply.Metals.target == 13500)
L4:DronesFinish(); clock = clock + 5000; H:HubTrackWorkTick()
assert(#jobs == 0 and H.supply.Metals.target == 15500 and H.supply.Metals.actual == 15500, "dropped, nothing paid, claim released")
''')

lua.execute(r'''
-- Short stock: the job waits, the hub is signed, and it dispatches when stock lands.
H.supply.Metals.actual = 1000; H.supply.Metals.target = 1000
L5 = break_track(T2, 3, 4000); clock = clock + 5000; H:HubTrackWorkTick()
local job = jobs[1]; assert(not job.deadline and job.waiting == "Metals" and H.signs.SignNoConsumptionResource == true, "waiting for Metals, signed")
assert(H:GetHubRepairLine():find("waiting") and H:GetHubRepairLine():find("short of Metals"))
H:AddResource(5000, "Metals"); clock = clock + 5000; H:HubTrackWorkTick()
assert(job.deadline and not job.waiting and H.signs.SignNoConsumptionResource == nil and H.supply.Metals.target == 4000, "dispatched once stock landed")
-- The reserve is never touched: a standing claim on the request (10_TrainFloor's shape) counts as taken.
clock = job.deadline; H:HubTrackWorkTick(); assert(L5.completed and #jobs == 0)
H.supply.Metals.actual = 3000; H.supply.Metals.target = 1000 -- 2000 held by the maintenance reserve
L6 = break_track(T2, 3, 4000); clock = clock + 5000; H:HubTrackWorkTick()
assert(jobs[1].waiting == "Metals", "3000 in stock but only 1000 free: the reserve stands")
H.supply.Metals.actual = 20000; H.supply.Metals.target = 18000
clock = clock + 5000; H:HubTrackWorkTick(); assert(jobs[1].deadline); clock = jobs[1].deadline; H:HubTrackWorkTick(); assert(L6.completed)
-- The toggle off: a new break is recorded but not dispatched; a repair under way still completes.
L7 = break_track(T2, 3, 4000); clock = clock + 5000; H:HubTrackWorkTick(); assert(jobs[1].deadline)
H:SetHubTrackRepair(false); assert(H.SMROptIn_track_work.repair == false and rebuilt == 1)
L8 = break_track(T2, 4, 4000); clock = clock + 5000; H:HubTrackWorkTick()
assert(#jobs == 2 and not jobs[2].deadline and jobs[2].site == L8, "recorded, not dispatched, toggle off")
assert(ConstructionSite.IsOutsideCommandRange(L8) == true, "toggle off: the hub covers nothing, vanilla's warning returns")
assert(H:GetHubRepairLine():find("track work off"))
clock = jobs[1].deadline; H:HubTrackWorkTick(); assert(L7.completed, "the repair under way completed with the toggle off")
assert(#T2.repair_cgs == 2 and #T2.elements_under_construction == 1,
  "partially repaired track remains blocked while another group is unfinished")
local refreshed = 0; L8.UpdateNoCCSign = function() refreshed = refreshed + 1 end
H:SetHubTrackRepair(true); clock = clock + 5000; H:HubTrackWorkTick(); assert(jobs[1].deadline, "dispatched once the toggle is back on")
assert(ConstructionSite.IsOutsideCommandRange(L8) == false and refreshed >= 1, "toggle on: covered again, and the sign refreshed"); L8.UpdateNoCCSign = nil
clock = jobs[1].deadline; H:HubTrackWorkTick(); assert(L8.completed and #jobs == 0)
assert(#T2.repair_cgs == 0 and #T2.elements_under_construction == 0,
  "last break clears the track; a dead earlier group is not rediscovered as a job")
-- The player's switch off stops NEW dispatches; malfunction and no power do not (owner, 2026-09-22).
H.ui_working = false
L9 = break_track(T2, 3, 4000); clock = clock + 5000; H:HubTrackWorkTick(); assert(not jobs[1].deadline, "switch off: no dispatch")
H.ui_working = true; H.working = false; H.is_malfunctioned = true
clock = clock + 5000; H:HubTrackWorkTick(); assert(jobs[1].deadline, "malfunctioned and unpowered: still dispatches")
clock = jobs[1].deadline; H:HubTrackWorkTick(); assert(L9.completed, "and still completes")
H.working = true; H.is_malfunctioned = nil
''')

lua.execute(r'''
-- The ceiling: fleet and repair flights share MaxDrones; the fleet makes room for a waiting repair.
Tune.MaxDrones = 8; Tune.Standing = 5; Tune.LaunchTime = 200000 -- long deadlines, so no slot frees during the scenario
Tune.RepairReserve = 0 -- the bare shared ceiling here; the reserve has its own case below
-- five fleet Wasps stand; three breaks: two dispatch (one per tick), the third waits at 5 + 3 > 8
local Ls = {}
for i = 1, 3 do Ls[i] = break_track(T5, i + 1, 2000) end
for i = 1, 4 do clock = clock + 5000; H:HubTrackWorkTick() end
local dispatched, waiting = 0, 0
for _, j in ipairs(jobs) do if j.deadline then dispatched = dispatched + 1 else waiting = waiting + 1 end end
assert(dispatched == 3 and waiting == 0 and #H.drones <= 5, "8 - 3 flights leaves 5; three dispatched over three ticks: " .. dispatched .. "/" .. waiting .. " fleet " .. #H.drones)
-- a fourth waits, and the waiting job recalls an idle fleet drone without the delay
Ls[4] = break_track(T5, 5, 2000); clock = clock + 5000; H:HubTrackWorkTick()
waiting = 0; for _, j in ipairs(jobs) do if not j.deadline then waiting = waiting + 1 end end
assert(waiting == 1 and #H.drones == 4, "the fourth waits at the ceiling, and one idle fleet drone is recalled at once to make room: " .. #H.drones)
clock = clock + 5000; H:HubTrackWorkTick()
waiting = 0; for _, j in ipairs(jobs) do if not j.deadline then waiting = waiting + 1 end end
assert(waiting == 0 and #H.drones == 4, "dispatched once the fleet made room; the fleet holds at the ceiling's remainder: waiting " .. waiting .. " fleet " .. #H.drones)
for _, j in ipairs(jobs) do clock = math.max(clock, j.deadline) end
H:HubTrackWorkTick(); assert(#jobs == 0)
Tune.MaxDrones = 30; Tune.LaunchTime = 12000; Tune.RepairReserve = 5
''')

lua.execute(r'''
-- The fleet tiers: low 5, medium 10, high 20; a recall only of an idle, empty-handed drone,
-- removed when near, sent home when far; never a busy one.
for i = #H.drones, 1, -1 do DroneControl.KillDrone(H, H.drones[i]) end
Tune.ForceFleet = 5; clock = clock + 5000; H:HubTrackWorkTick(); assert(#H.drones == 5, "low: 5")
Tune.ForceFleet = 10; clock = clock + 5000; H:HubTrackWorkTick(); assert(#H.drones == 10, "medium: 10")
Tune.ForceFleet = 20; clock = clock + 5000; H:HubTrackWorkTick(); assert(#H.drones == 20, "high: 20")
for _, d in ipairs(H.drones) do assert(d.painted == nil, "no palette by default") end
Tune.ForceFleet = 5
clock = clock + 5000; H:HubTrackWorkTick(); assert(#H.drones == 20, "no recall before RecallDelay")
clock = clock + Tune.RecallDelay; H:HubTrackWorkTick(); assert(#H.drones == 19, "one recalled after the delay")
clock = clock + 1000; H:HubTrackWorkTick(); assert(#H.drones == 19, "one per RecallStep")
-- the next idle drone is far: it is sent home first, not removed
H.drones[1].pos = { x = 50000, y = 0 }
for _, d in ipairs(H.drones) do if d ~= H.drones[1] then d.command = "Work" end end
clock = clock + Tune.RecallStep; H:HubTrackWorkTick()
assert(#H.drones == 19 and H.drones[1].command == "GoHome" and H.drones[1].commands[#H.drones[1].commands][5] == "ReturningToController", "far idle drone sent home")
-- back near and idle: removed next step; a busy drone is never touched; one carrying a cube is skipped
H.drones[1].pos = { x = 100, y = 0 }; H.drones[1].command = "Idle"
clock = clock + Tune.RecallStep; H:HubTrackWorkTick(); assert(#H.drones == 18)
for _, d in ipairs(H.drones) do d.command = "Idle"; d.resource = "Metals" end
clock = clock + Tune.RecallStep; H:HubTrackWorkTick(); assert(#H.drones == 18, "a drone carrying a cube is not recalled")
for _, d in ipairs(H.drones) do d.resource = false end
-- the palette dial paints new Wasps with the reactor's variant
Tune.WaspPalette = "P4"; Tune.ForceFleet = 20; clock = clock + 5000; H:HubTrackWorkTick()
assert(#H.drones == 20 and H.drones[20].painted == 4, "painted through per-object colorization"); Tune.WaspPalette = false
-- the switch off freezes the fleet where it is
H.ui_working = false; Tune.ForceFleet = 5; clock = clock + Tune.RecallDelay * 2; H:HubTrackWorkTick(); assert(#H.drones == 20); H.ui_working = true
-- the fleet's own meter (owner, 2026-09-24): idle drones averaged over LoadWindow, vanilla's thresholds
Tune.ForceFleet = false
for i = #H.drones, 1, -1 do DroneControl.KillDrone(H, H.drones[i]) end
H.free = 5; for _ = 1, 12 do clock = clock + 5000; H:HubTrackWorkTick() end
assert(#H.drones == 5, "idle fleet: low, 5: " .. #H.drones)
-- chunks (owner, 2026-09-25): all busy grows 5 -> 15 -> 25, one jump per LoadWindow, and stops
-- there: the last 5 of 30 are the repairs'
H.free = 0; local seen, ticks = {}, 0
while ticks < 60 do clock = clock + 5000; H:HubTrackWorkTick(); ticks = ticks + 1; seen[#H.drones] = seen[#H.drones] or ticks end
assert(seen[15] and seen[25] and not seen[10] and not seen[20] and #H.drones == 25 and seen[25] <= 30,
  "5 -> 15 -> 25 in chunks and no further: " .. #H.drones)
assert(H:GetDronesStatusText():find("Heavy"), "the panel's load line shows the fleet meter: " .. tostring(H:GetDronesStatusText()))
-- 25 out keeps 10 idle: 12 idle recalls down to the buffer, not to the standing 5
for _, d in ipairs(H.drones) do d.command = "Idle" end
H.free = 12; for _ = 1, 12 do clock = clock + 5000; H:HubTrackWorkTick() end
clock = clock + Tune.RecallDelay; H:HubTrackWorkTick(); assert(#H.drones == 24, "above the buffer: one recalled: " .. #H.drones)
H.free = 10; for _ = 1, 8 do clock = clock + Tune.RecallStep; H:HubTrackWorkTick() end
assert(#H.drones == 24, "at the buffer: the fleet holds: " .. #H.drones)
-- 15 out keeps 5 idle: a busy fleet with 3 idle is never recalled; it grows to 25
for i = #H.drones, 16, -1 do DroneControl.KillDrone(H, H.drones[i]) end
local lowest = #H.drones
H.free = 3; for _ = 1, 24 do clock = clock + 5000; H:HubTrackWorkTick(); lowest = Min(lowest, #H.drones) end
assert(lowest == 15 and #H.drones == 25, "3 idle of 15: never below 15, grows to 25: lowest " .. lowest .. " now " .. #H.drones)
-- the repairs' reserve: even pinned at 30 the fleet stops at 25
Tune.ForceFleet = 30; clock = clock + 5000; H:HubTrackWorkTick(); assert(#H.drones == 25, "the repairs' 5 are never the fleet's: " .. #H.drones)
Tune.ForceFleet = false
-- no work at all: back down to the standing 5, never below
H.free = 30; for _ = 1, 200 do clock = clock + Tune.RecallStep; H:HubTrackWorkTick() end
assert(#H.drones == 5, "idle: down to Standing: " .. #H.drones)
-- through the pit (owner, 2026-09-24): with the flight's Release, a launch rises before it joins the
-- fleet, counting as out meanwhile; a recall leaves the list at once and flies home
local made, recalled = {}, {}
F.Release = function(r) r.release = true made[#made + 1] = r return r end
F.Recall = function(hub, d) recalled[#recalled + 1] = d return {} end
F.PitPoints = function() return {} end
Tune.ForceFleet = 8; clock = clock + 5000; H:HubTrackWorkTick()
assert(#made == 3 and #H.drones == 5, "three launches rising, not yet in the fleet: " .. #made .. " / " .. #H.drones)
assert(made[1].hub == H and made[2].drone ~= made[1].drone)
clock = clock + 5000; H:HubTrackWorkTick(); assert(#made == 3, "rising Wasps count as out: no second launch")
for _, r in ipairs(made) do r.released = true; F.OnReleased(H, r.drone) end
assert(#H.drones == 8 and H.drones[8].command == "Idle" and H.drones[8].name == "Repair Drone", "released into the fleet")
Tune.ForceFleet = 5; H.free = 8; for _, d in ipairs(H.drones) do d.command = "Idle" end
clock = clock + 5000; H:HubTrackWorkTick(); clock = clock + Tune.RecallDelay; H:HubTrackWorkTick()
assert(#recalled >= 1 and #H.drones == 8 - #recalled and not recalled[1].deleted, "recalled through the pit: off the list, flying home")
F.Release, F.Recall, F.PitPoints, F.OnReleased = nil, nil, nil, nil; Tune.ForceFleet = false; H.free = nil
H.free = nil
''')

lua.execute(r'''
-- The control wrap: false only for a Wasp whose live controller is a train hub.
local mine = H.drones[1]; local theirs = FlyingDrone:new({ command_center = S1 }, 1); local loose = FlyingDrone:new({}, 1)
assert(FlyingDrone.CanBeControlled(mine) == false and FlyingDrone.CanBeControlled(theirs) == true and FlyingDrone.CanBeControlled(loose) == true)
theirs.disabled = true; assert(FlyingDrone.CanBeControlled(theirs) == false, "the original's verdict passes through")
-- Destroyed hub: every drone gone, fleet and flight, a carried cube dropped first, jobs cleared,
-- claims released, then vanilla's Finalize with nothing left to orphan.
L10, E10 = break_track(T2, 3, 4000); clock = clock + 5000; H:HubTrackWorkTick()
local job = jobs[1]; assert(job.deadline and IsValid(job.drone))
local flight = job.drone; local carrier = H.drones[1]; carrier.resource = "Concrete"
local target_before = H.supply.Metals.target
H.destroyed = true; H:Finalize()
assert(flight.deleted and carrier.deleted and carrier.dropped == "Concrete", "flight and fleet removed, the cube dropped first")
for _, d in ipairs(drones_all) do if d.command_center == H then assert(d.deleted, "no repair drone of a destroyed hub survives") end end
assert(#H.drones == 0 and #H.SMROptIn_track_work.jobs == 0 and H.finalized == 1, "jobs cleared, vanilla Finalize ran once")
assert(H.supply.Metals.target == target_before + 2000, "the claim released")
H.destroyed = false; jobs = H.SMROptIn_track_work.jobs -- Finalize replaced the list
L10:DronesFinish() -- the site outlived the hub; ordinary drones finish it
''')

lua.execute(r'''
-- Load: the first tick adopts each job's surviving Wasp at the deadline's stage, then sweeps strays.
H2 = hub(0, 200000); H2.city = {}
local SA = station("SA"); SA.pos = { x = 30000, y = 200000 }
local TA = track(H2, SA, 4)
local La, Ea = break_track(TA, 2, 4000)
clock = clock + 5000; H2:HubTrackWorkTick()
local job = H2.SMROptIn_track_work.jobs[1]; assert(job.deadline and IsValid(job.drone))
-- simulate the save/load: the flight's records are gone, the Wasp rode the save under a stock leg
job.drone.command = "FlightGoto"
local fleet = H2.drones[1]
local stray = FlyingDrone:new({ command_center = H2, command = "FlightGoto" }, 1)          -- the console prototype's leftover
local dead_hub = { valid = true, destroyed = true, classes = { SMROptInTrainHubBase = true }, drones = {}, supply = {} }
local orphan_of_dead = FlyingDrone:new({ command_center = dead_hub, command = "Idle", resource = "Metals" }, 1)
local foreign = FlyingDrone:new({ command_center = SA, command = "Idle" }, 1)
SA.filed[H2] = { "supply Metals", "demand Concrete", "maintenance material", "maintenance work" } -- registered before the filter existed
OnMsg.LoadGame()
clock = clock + 5000; H2:HubTrackWorkTick()
assert(#SA.filed[H2] == 2, "an out-of-range station is re-filed once per load")
assert(#F.adopted == 1 and F.adopted[1].drone == job.drone and F.adopted[1].stage == "out" and F.adopted[1].target == Ea, "adopted at 'out': adoptions " .. #F.adopted .. " stage " .. tostring(F.adopted[1] and F.adopted[1].stage) .. " same drone " .. tostring(F.adopted[1] and F.adopted[1].drone == job.drone) .. " deadline " .. tostring(job.deadline) .. " clock " .. clock)
assert(not job.drone.deleted and not fleet.deleted and not foreign.deleted, "adopted, fleet and foreign Wasps stay")
assert(stray.deleted and orphan_of_dead.deleted and orphan_of_dead.dropped == "Metals", "strays and a dead hub's drone go, cubes dropped")
-- a later load near the deadline: still adopted 'out' (a standing job's work is not done); a refused
-- adoption (foreign command) is swept and the job relaunches a fresh Wasp
local job2 = job; job2.drone.command = "WaitUninterruptable"
OnMsg.LoadGame(); clock = job2.deadline - 1000; H2:HubTrackWorkTick()
assert(F.adopted[2].stage == "out", "a standing job resumes outbound")
local idle_wasp = job2.drone; idle_wasp.command = "Idle"; OnMsg.LoadGame(); clock = clock + 1; H2:HubTrackWorkTick()
assert(#F.adopted == 2 and idle_wasp.deleted == true and IsValid(job2.drone) and job2.drone ~= idle_wasp, "a Wasp under a foreign command is refused and swept; a fresh one relaunches")
assert(La.completed or job2.deadline > clock)
-- no flight while saving: Create refuses, the deadline stands, the next tick tries again
clock = job2.deadline; H2:HubTrackWorkTick(); assert(La.completed)
local Lb = break_track(TA, 3, 4000); F.save_gate = true; clock = clock + 5000; H2:HubTrackWorkTick()
local jb = H2.SMROptIn_track_work.jobs[1]; assert(jb.deadline and not IsValid(jb.drone), "dispatched, no Wasp under the save gate")
F.save_gate = false; clock = clock + 5000; H2:HubTrackWorkTick(); assert(IsValid(jb.drone), "a Wasp once the gate lifts")
-- a Wasp destroyed on the way (owner, 2026-09-24: a meteor storm) is replaced and its trip restarts
local lost_wasp, d0 = jb.drone, jb.deadline; DoneObject(lost_wasp); clock = clock + 1000; H2:HubTrackWorkTick()
assert(IsValid(jb.drone) and jb.drone ~= lost_wasp and jb.deadline > d0 and not Lb.completed, "relaunched, the trip restarted, nothing repaired")
jb.drone.command = "Dead"; local dead_wasp = jb.drone; clock = clock + 1000; H2:HubTrackWorkTick()
assert(IsValid(jb.drone) and jb.drone ~= dead_wasp and not Lb.completed, "a dead Wasp is replaced too")
assert(F.OnWorkDone, "the hub registers its work-done hook on the flight")
jb.drone = FlyingDrone:new({ command_center = H2 }, 1); clock = clock + 1; local early = clock; assert(early < jb.deadline)
F.OnWorkDone(H2, jb.drone, early)
assert(Lb.completed and not table.find(H2.SMROptIn_track_work.jobs, jb), "completed at the work's end, the job cleared")
F.OnWorkDone(H2, FlyingDrone:new({ command_center = H2 }, 1), early); F.OnWorkDone(H, jb.drone, early) -- unknown drones and other hubs: no-ops
-- a live Wasp holds the completion past its deadline until its work ends, within FlightGrace (owner, 2026-09-24)
Tune.FlightGrace = 100
local Lc = break_track(TA, 4, 4000); clock = clock + 5000; H2:HubTrackWorkTick()
local jc; for _, j in ipairs(H2.SMROptIn_track_work.jobs) do if j.site == Lc then jc = j end end
assert(jc and jc.deadline and IsValid(jc.drone), "dispatched with a Wasp")
clock = jc.deadline; H2:HubTrackWorkTick(); assert(not Lc.completed, "the Wasp is still out: the deadline waits for it")
F.OnWorkDone(H2, jc.drone, clock); assert(Lc.completed, "its work's end completes it")
-- a stuck Wasp: past the grace the deadline completes anyway
local Ld = break_track(TA, 4, 4000); clock = clock + 5000; H2:HubTrackWorkTick()
local jd; for _, j in ipairs(H2.SMROptIn_track_work.jobs) do if j.site == Ld then jd = j end end
assert(jd and IsValid(jd.drone), "stuck case dispatch: job " .. tostring(jd) .. " deadline " .. tostring(jd and jd.deadline) .. " left " .. tostring(jd and jd.deadline and jd.deadline - clock) .. " jobs " .. #H2.SMROptIn_track_work.jobs); local trip = jd.deadline - jd.started
clock = jd.deadline + trip - 1; H2:HubTrackWorkTick(); assert(not Ld.completed, "inside the grace")
clock = jd.deadline + trip; H2:HubTrackWorkTick(); assert(Ld.completed, "past the grace: the fallback completes a stuck flight")
-- no Wasps at all (the Visual probe dial off): the deadline alone completes it
Tune.Visual = false
local Le = break_track(TA, 4, 4000); clock = clock + 5000; H2:HubTrackWorkTick()
local je; for _, j in ipairs(H2.SMROptIn_track_work.jobs) do if j.site == Le then je = j end end
assert(je and je.deadline and not IsValid(je.drone)); clock = je.deadline; H2:HubTrackWorkTick(); assert(Le.completed, "Visual off: completed at the deadline")
Tune.Visual = true
Tune.FlightGrace = 0
''')

lua.execute(r'''
-- The persisted shape: one new field on the hub, plain data and object references, no functions.
local keys_after = table.keys(H)
local new = {}
for _, k in ipairs(keys_after) do if not table.find(keys_before, k) and k ~= "destroyed" and k ~= "finalized" then new[#new + 1] = k end end -- the two are this test's own writes in the destruction scenario
assert(#new == 1 and new[1] == "SMROptIn_track_work", "exactly one new field: " .. table.concat(new, ","))
local function plain(v, depth)
  if type(v) == "function" or type(v) == "thread" then return false end
  if type(v) == "table" and v.valid ~= nil then return true end -- an object reference (the mock's methods sit on the instance; the engine's on the class)
  if type(v) == "table" and depth < 4 then for k, x in pairs(v) do if not plain(k, depth + 1) or not plain(x, depth + 1) then return false end end end
  return true
end
local count0 = #jobs; L11 = break_track(T2, 3, 4000); clock = clock + 5000; H:HubTrackWorkTick()
assert(#jobs == count0 + 1 and plain(H.SMROptIn_track_work, 0), "no function reaches the persisted record: jobs " .. #jobs .. " before " .. count0 .. " plain " .. tostring(plain(H.SMROptIn_track_work, 0)))
for _, key in ipairs({ "kind", "site", "el", "track", "found", "started", "deadline", "drone", "held", "waiting" }) do assert(jobs[1][key] ~= nil, key) end
-- Console: the dials and the status line.
assert(SetHubRepairTune("Standing", 3) and Tune.Standing == 3)
assert(SetHubRepairTune{ Buffer20 = 4, RecallDelay = 1000 } and Tune.Buffer20 == 4)
assert(not SetHubRepairTune("Nope", 1) and not SetHubRepairTune("Standing", -1) and not SetHubRepairTune("Standing", 1.5))
assert(SetHubRepairTune("Speed", false), "Speed false"); assert(SetHubRepairTune("Speed", 9000), "Speed 9000"); assert(not SetHubRepairTune("Speed", 0), "Speed 0 refused")
assert(SetHubRepairTune("WaspPalette", "P4"), "P4"); assert(not SetHubRepairTune("WaspPalette", "P9"), "P9 refused"); assert(SetHubRepairTune("WaspPalette", false), "palette off")
assert(HubRepairStatus(H) == jobs)
-- the message handler pokes the hubs of the track's map immediately
local before = #jobs; L12 = break_track(T5, 3, 2000); OnMsg.TrackBroken(T5, true); assert(#jobs == before + 1, "TrackBroken ticks the hub at once")
OnMsg.TrackBroken(T5, false); assert(#jobs == before + 1)
-- the panel template registers once, with the section, the line and the toggle
OnMsg.CityStart(); assert(NotificationPresets.SMROptInTrackRepair)
local n = #placed; OnMsg.LoadGame(); assert(#placed == n, "idempotent")
-- the hub's sections are built in sectionCustom:Init (L5, 2026-09-24): vanilla's Init first, then
-- the status section with its two lines and the toggle; any other building gets vanilla's alone
local sec = {}; local before_ui = #created_ui; sectionCustom.Init(sec, nil, H)
assert(sec.vanilla_init and #created_ui == before_ui + 4, "four elements for a hub: " .. (#created_ui - before_ui))
assert(created_ui[before_ui + 1].class == "InfopanelSection" and created_ui[before_ui + 1].parent == sec)
assert(created_ui[before_ui + 3].props.Text == "<HubRepairLine>" and created_ui[before_ui + 4].class == "InfopanelActiveSection" and created_ui[before_ui + 4].parent == sec)
local other = {}; before_ui = #created_ui; sectionCustom.Init(other, nil, S1); assert(other.vanilla_init and #created_ui == before_ui, "other buildings: vanilla only")
''')

result = {
    "command": "python tools/devmods/train_hub/tests/repair_smoke.py",
    "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "scope": "mocked Lua / source contract over the TRACK WORK section; no native run, no save file, no clearance claim",
    "result": "PASS",
    "flight_records_created": lua.globals().SMROptInHubFlight.created,
    "adoptions": len(lua.globals().SMROptInHubFlight.adopted),
    "notifications": len(lua.globals().notifications),
}
print(json.dumps(result, indent=2))
