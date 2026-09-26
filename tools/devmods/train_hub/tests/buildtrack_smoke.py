"""Build 5 desk smoke. Executes real hub Lua over repair_smoke's mocked engine.

No native game, save-file, timing or visual claim. Command and source hashes in the receipt.
"""
import hashlib
import json
import re
import runpy
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
env = runpy.run_path(str(HERE / "repair_smoke.py"))
lua = env["lua"]
lua.execute(r'''
-- New sites, native group delivery and completion. Endpoints remain station connectors;
-- the group moves its members out of elements_under_construction together on completion.
function new_line(a, b, n, cost)
  local t = track(a, b, n)
  local leader = { valid = true, construction_resources = { Metals = request(cost) } }
  local cg = { leader }; leader.construction_group = cg
  for _, el in ipairs(t.elements) do
    el.is_construction_site = true; el.construction_group = cg
    cg[#cg + 1] = el; t.elements_under_construction[#t.elements_under_construction + 1] = el
  end
  function leader:AddResource(amount, res) self.construction_resources[res]:AddAmount(-amount) end
  function leader:Complete()
    if self.nanite_wait then return end
    self.completed = true; self.deleted = true; t.elements_under_construction = {}
    for _, el in ipairs(t.elements) do el.is_construction_site = false; el.construction_group = false end
  end
  return t, leader
end
function build_job(h, leader)
  for _, j in ipairs(h.SMROptIn_track_work.jobs) do if j.site == leader then return j end end
end
Tune.Visual = true; Tune.FlightGrace = 100; Tune.ForceFleet = 0
Tune.LaunchTime = 4000; Tune.WorkTime = false; Tune.BuildTimePerElement = 1000
local h = hub(0, 0); local a = station('A'); local b = station('B'); local c = station('C')
local t1, l1 = new_line(h, a, 4, 10000)
local t2, l2 = new_line(a, b, 8, 6000)
local isolated, li = new_line(station('isolated'), c, 5, 2000)
h:HubTrackWorkTick()
local j1 = assert(build_job(h, l1))
assert(j1.kind == 'build' and j1.elements == 4 and j1.deadline and not build_job(h, l2))
assert(not build_job(h, li), 'isolated line not queued')
assert(F.last.work_time == 9000, 'flight receives base 5000 + 4 x 1000')
assert(j1.deadline - j1.started == 15000, 'same-position launch 4000 + work 7000 + 4000')
assert(h.supply.Metals.actual == 20000 and not j1.held, 'build does not reserve discounted repair cost')
-- Stock-out at work end. Another drone reserves 1000 of demand and supplies 2000;
-- only 4000 hub stock is free (1000 kept as a standing reserve).
l1.construction_resources.Metals:AssignUnit(1000)
l1:AddResource(2000, 'Metals')
h.supply.Metals = request(5000); h.supply.Metals:AssignUnit(1000)
clock = j1.deadline
assert(F.OnWorkDone(h, j1.drone, clock) == false, 'builder stays at site while short')
assert(not l1.completed and l1.construction_resources.Metals.actual == 4000)
assert(h.supply.Metals.actual == 1000 and h.supply.Metals.target == 0 and j1.waiting == 'Metals')
assert(h.signs.SignNoConsumptionResource, 'stock-out sign')
-- A load keeps delivered resources and adopts the saved stock command. It repeats the
-- work pose, never the paid cost; this simulates the hub hook, not engine serialization.
j1.drone.command = 'WaitUninterruptable'; OnMsg.LoadGame(); clock = clock + 1; h:HubTrackWorkTick()
assert(F.adopted[#F.adopted].work_time == 9000 and l1.construction_resources.Metals.actual == 4000)
h:AddResource(8000, 'Metals'); clock = j1.deadline + 1
assert(F.OnWorkDone(h, j1.drone, clock) == false, 'reserved drone delivery is not paid twice')
assert(l1.construction_resources.Metals.actual == 1000 and h.supply.Metals.actual == 6000)
-- Native reservation delivery releases its reservation and consumes the actual demand.
l1.construction_resources.Metals:UnassignUnit(1000); l1:AddResource(1000, 'Metals')
F.OnWorkDone(h, j1.drone, clock + 1)
assert(l1.completed and h.supply.Metals.actual == 6000, '7000 hub + 3000 drone = 10000, no repair discount')
clock = clock + 5000; h:HubTrackWorkTick()
local j2 = assert(build_job(h, l2)); assert(j2.deadline and j2.elements == 8)
assert(j2.deadline - j2.started == 19000, 'longer group adds 8000, not 4000 work ms')
assert(F.last.work_time == 13000, 'per-flight time, no global flight dial mutation')
-- Toggle stops new launches, including a subsequently connected line, but a dispatched
-- group still finishes. Nanite deferral retains the paid job until native Complete succeeds.
local t3, l3 = new_line(h, c, 3, 1000)
h:SetHubTrackRepair(false); clock = clock + 1; h:HubTrackWorkTick()
assert(not build_job(h, l3).deadline)
l2.nanite_wait = true; clock = j2.deadline; F.OnWorkDone(h, j2.drone, clock)
assert(not l2.completed and l2.construction_resources.Metals.actual == 1000, 'reserve still protected')
h:AddResource(1000, 'Metals'); F.OnWorkDone(h, j2.drone, clock + 1)
assert(not l2.completed and l2.construction_resources.Metals.actual == 0 and build_job(h, l2))
local paid = h.supply.Metals.actual
l2.nanite_wait = false; F.OnWorkDone(h, j2.drone, clock + 2)
assert(l2.completed and h.supply.Metals.actual == paid and not build_job(h, l3).deadline)
h:SetHubTrackRepair(true); clock = clock + 5000; h:HubTrackWorkTick()
local j3 = build_job(h, l3); assert(j3.deadline)
-- Ordinary drones win the race: the hub drops the job without charging anything.
l3:Complete(); clock = clock + 5000; h:HubTrackWorkTick()
assert(not build_job(h, l3) and h.supply.Metals.actual == paid)
-- An unlaunched job loses its connection and waits; its old graph entry is not authority.
local far = station('far'); local bridge = track(h, far, 3)
local t4, l4 = new_line(far, station('last'), 4, 2000)
h.ui_working = false; h:HubTrackWorkTick(); assert(build_job(h, l4))
bridge.deleted = true; h.ui_working = true; h:HubTrackWorkTick(); assert(not build_job(h, l4).deadline)
bridge.deleted = false; h:HubTrackWorkTick(); assert(build_job(h, l4).deadline)
-- C1 / D14(g): counting another hub must retain this hub's live launches.
local made = {}; local original_create = F.Create
F.Create = function(hub, started) local r = original_create(hub); made[#made + 1] = r; return r end
F.Release = function(r) r.release = true return r end
Tune.ForceFleet = 5
local ha, hb = hub(0,0), hub(1000,0)
ha:HubTrackWorkTick(); hb:HubTrackWorkTick(); ha:HubTrackWorkTick(); hb:HubTrackWorkTick()
assert(#made == 10, 'five launches per hub, no foreign records evicted and no duplicate fleet')
local counts = {}; for _, r in ipairs(made) do counts[r.hub] = (counts[r.hub] or 0) + 1 end
assert(counts[ha] == 5 and counts[hb] == 5)
F.Create = original_create; F.Release = nil

-- Reworked shape: neither TrackBase endpoint names a station, a new line hangs off
-- its finished end on a separate object, and one new member shares the old object.
Tune.ForceFleet = 0; Tune.MaxDrones = 60; Tune.FlightGrace = 100
local hr = hub(0, 0); local far = station('reworked far')
local old = track(hr, station('removed station'), 4)
old.end_el.deleted = true
testmap.object_hex_grid[old.end_el.q .. ':' .. old.end_el.r] = nil
old.start_el = old.elements[2]; old.end_el = old.elements[4]
local added, lb = new_line(station('unused'), far, 4, 2000)
testmap.object_hex_grid[added.start_el.q .. ':' .. added.start_el.r] = nil
added.start_el.deleted = true
local function move_hex(el, q, r)
  testmap.object_hex_grid[el.q .. ':' .. el.r] = nil
  el.q, el.r = q, r; testmap.object_hex_grid[q .. ':' .. r] = el
end
for i, el in ipairs(added.elements) do move_hex(el, 4+i, old.elements[1].r) end
move_hex(added.end_el, 9, old.elements[1].r)
added.elements[1].track_obj = old
old.elements_under_construction = {added.elements[1]}
local nextline, ln = new_line(far, station('beyond far'), 3, 1000)
hr.ui_working = false; hr:HubTrackWorkTick()
assert(build_job(hr, lb) and not build_job(hr, ln), 'hanging build found, far station remains a boundary')
local lr = break_track(old, 2, 1000)
hr:HubTrackWorkTick()
local nodes, _, sites = hr:HubTrackGraph()
assert(sites[lr] and sites[lb] and not nodes[far], 'repair on mixed track and connected build both found')
-- Put the builder last: reverse iteration used to give it the only launch.
local repair, builder = build_job(hr, lr), build_job(hr, lb)
hr.SMROptIn_track_work.jobs = {repair, builder}
hr.ui_working = true; hr:HubTrackWorkTick()
assert(repair.deadline and not builder.deadline, 'repair dispatch precedes queued build')
clock = clock + 1; hr:HubTrackWorkTick(); assert(builder.deadline)
-- Completing the native group opens far-station service and its next line.
lb:Complete(); nodes = hr:HubTrackGraph(); assert(nodes[far])
hr:HubTrackWorkTick(); assert(build_job(hr, ln))

-- A physical gap cannot be bridged by shared TrackBase membership. Moving a queued
-- target to another native object does not strand it if its element is still reachable.
local hg = hub(0,0); local gapline, lg = new_line(hg, station('gap far'), 4, 1000)
hg.ui_working = false; hg:HubTrackWorkTick(); local gj = assert(build_job(hg, lg))
gapline.elements[1].deleted = true
hg.ui_working = true; hg:HubTrackWorkTick(); assert(not gj.deadline, 'real gap stops dispatch')
gapline.elements[1].deleted = false
local replacement = {valid=true, elements={}, elements_under_construction=gapline.elements, repair_cgs={}}
for _, el in ipairs(gapline.elements) do el.track_obj = replacement end
hg:HubTrackWorkTick(); assert(gj.deadline and gj.track == replacement, 'live target survives native reassignment')

-- Builders fill the non-reserved capacity; repairs can still use all five reserved
-- slots, and later builds can replace completed repairs only above that reserve.
Tune.MaxDrones = 60; Tune.RepairReserve = 5; Tune.ForceFleet = 25; Tune.WorkTime = 10000000
local hc = hub(0,0)
for i=1,25 do local d=FlyingDrone:new({}, testmap); d:SetCommandCenter(hc); d.command='Work' end
local capleaders = {}
for i=1,36 do local _, l = new_line(hc, station('cap '..i), 1, 0); capleaders[i]=l end
for i=1,40 do clock=clock+1; hc:HubTrackWorkTick() end
local builders=0
for _, j in ipairs(hc.SMROptIn_track_work.jobs) do if j.kind=='build' and j.deadline then builders=builders+1 end end
assert(builders==30 and #hc.drones==25, '25 fleet + 30 builders leaves five repair slots')
local rt=track(hc,station('repairs at cap'),7)
for i=1,5 do break_track(rt,i,0) end
for i=1,6 do clock=clock+1; hc:HubTrackWorkTick() end
local active, repairs=0,0
for _, j in ipairs(hc.SMROptIn_track_work.jobs) do
  if j.deadline then active=active+1; if j.kind=='repair' then repairs=repairs+1 end end
end
assert(active==35 and repairs==5 and #hc.drones==25, 'repairs fill reserve, total never exceeds sixty')
Tune.WorkTime=false; Tune.ForceFleet=0
''')

# Replay the owner's full paused topology through the actual Lua graph. This is
# archived input, not a hand-authored graph that assumes the desired connection.
snapshot = ROOT / "docs/archive/train_hub_build5_20260925/topology_snapshot_Mars.exe-20260925-23.08.46-6aad2d75.log"
rows = []
for line in snapshot.read_text(encoding="utf-8").splitlines():
    if line.startswith("[mod] [SMRTK] SMRTK_DUMP ") and "leg=EXTENDED " in line:
        rows.append({k: v.strip('"') for k, v in re.findall(r'(\w+)=("[^"]*"|\S+)', line)})
lua.globals().snapshot_rows = lua.table_from([lua.table_from(r) for r in rows])
lua.execute(r'''
local objects, station_rows, element_rows = {}, {}, {}
local function object(id)
  if not id or id=='false' then return false end
  if not objects[id] then
    objects[id]={valid=true,handle=id,connectors={},construction_group={},elements_under_construction={}}
    objects[id].GetStartStation=function(self) return self.start_el and self.start_el.station end
    objects[id].GetEndStation=function(self) return self.end_el and self.end_el.station end
  end
  return objects[id]
end
local replay_map = {object_hex_grid={}}
for _, row in ipairs(snapshot_rows) do
  local o=object(row.object)
  if row.row=='element' then
    o.q,o.r=tonumber(row.q),tonumber(row.r)
    o.track_obj,o.station,o.broken=object(row.track),object(row.station),object(row.broken)
    o.is_construction_site=row.site=='true'; o.GetMap=function() return replay_map end
    local leader=object(row.leader)
    if leader then
      o.construction_group=leader.construction_group
      if #o.construction_group==0 then o.construction_group[1]=leader end
      table.insert(o.construction_group,o)
    end
    replay_map.object_hex_grid[o.q..':'..o.r]=o
    element_rows[#element_rows+1]=row
  elseif row.row=='station' then
    station_rows[#station_rows+1]=row
    o.ForEachConnectorElement=function(self,fn) for _,el in ipairs(self.connectors) do fn(el) end end
  elseif row.row=='track' then
    o.start_el,o.end_el=object(row.start_el),object(row.end_el)
    for id in row.unfinished:gmatch('[^,]+') do table.insert(o.elements_under_construction,object(id)) end
  end
end
for _,row in ipairs(station_rows) do
  for entry in row.connectors:gmatch('[^,]+') do
    local id=entry:match('^[^:]+:([^:]+):')
    table.insert(objects[row.object].connectors,object(id))
  end
end
local h=objects['6430']; h.HubTrackGraph=SMROptInTrainHubBase.HubTrackGraph
replay_hub=h
local nodes,_,sites=h:HubTrackGraph()
local expected,actual={},{}
for _,r in ipairs(element_rows) do
  if r.track=='7360' or r.track=='7504' then expected[r.leader]=true end
end
for leader,target in pairs(sites) do
  assert(target.kind=='build'); actual[leader.handle]=true
  assert(expected[leader.handle], 'no next line beyond unbuilt station, no disconnected work')
end
for leader in pairs(expected) do assert(actual[leader], 'captured hanging-line group missing: '..leader) end
replay_groups=0; for _ in pairs(actual) do replay_groups=replay_groups+1 end
assert(not nodes[objects['7042']] and not nodes[objects['7353']], 'unbuilt route grants no station service')
-- Native completion changes these members to built track. Leave stale endpoints and
-- separate TrackBase objects in place to check that they cannot suppress reach.
for _,r in ipairs(element_rows) do
  if r.track=='7360' or r.track=='7504' then objects[r.object].is_construction_site=false end
end
nodes,_,sites=h:HubTrackGraph()
assert(nodes[objects['7042']] and not nodes[objects['7353']], 'station joins when its line finishes')
local following=false
for _,target in pairs(sites) do if target.track==objects['7134'] then following=true end end
assert(following, 'the next line starts after its station joins')
-- Restore snapshot state for the pre-fix control below.
for _,r in ipairs(element_rows) do objects[r.object].is_construction_site=r.site=='true' end
''')

before = subprocess.check_output(
    ["git", "show", "86c7a9e:tools/devmods/train_hub/Code/20_TrainHub.lua"], cwd=ROOT, text=True)
graph = before[before.index("local function physical_track("):before.index("-- Every Station on the graph")]
lua.execute(graph)
lua.execute(r'''
local _, tracks = SMROptInTrainHubBase.HubTrackGraph(replay_hub)
local candidates = {}
for t, physical in pairs(tracks) do
  if not physical then
    for _,el in ipairs(t.elements_under_construction) do
      if el.is_construction_site and not IsValid(el.broken) then candidates[el.construction_group[1]]=true end
    end
  end
end
assert(next(candidates)==nil and replay_groups>0, 'pre-fix body must reproduce missing builds in the same snapshot')
''')
print(json.dumps({
    "command": "python tools/devmods/train_hub/tests/buildtrack_smoke.py",
    "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "sources": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        HERE.parent / "Code/20_TrainHub.lua", HERE.parent / "Code/30_TrainHubDrones.lua")},
    "snapshot_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
    "captured_line_groups": lua.globals().replay_groups,
    "pre_fix_control": "86c7a9e graph finds zero build groups in the identical snapshot",
    "scope": "mocked Lua plus captured-topology replay: reworked/mixed/hanging tracks, real gaps, repair priority/reserve, build payment/timing, adoption, toggle, multi-hub launches; no game/save-file evidence",
    "result": "PASS",
}, indent=2))
