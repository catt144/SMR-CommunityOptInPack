"""Build 5 desk smoke. Executes real hub Lua over repair_smoke's mocked engine.

No native game, save-file, timing or visual claim. Command and source hashes in the receipt.
"""
import hashlib
import json
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
''')
print(json.dumps({
    "command": "python tools/devmods/train_hub/tests/buildtrack_smoke.py",
    "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "sources": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        HERE.parent / "Code/20_TrainHub.lua", HERE.parent / "Code/30_TrainHubDrones.lua")},
    "scope": "mocked Lua: build gate, native partial payment, drone reservations, group timing, adoption, toggle, nanite retry, multi-hub launches; no game/save-file evidence",
    "result": "PASS",
}, indent=2))
