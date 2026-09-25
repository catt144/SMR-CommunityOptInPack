# Train hub build 5: the hub builds track

**LIVE: implemented, attended smoke remains** (2026-09-25). Build receipt and remaining
checks: `reports/TRAIN_HUB_BUILDTRACK_20260925.md`. Build 4's smoke is recorded
(`reports/drones_chain/L5_SMOKE_20260925.md`), and build 4 itself is
`03_Drones/DESIGN.md` with the hub half in `20_TrainHub.lua`. It is build 4's mechanism with a
second trigger and native group completion, on the pending list `SMROptIn_track_work` that build 4 shipped
with a kind field for exactly this. ⚠️ Read that build before designing: the pending list, the
completion path and the fleet all exist now, and the drones chain's link 6 (QA) may still be
auditing them — check `git log` on `20_TrainHub.lua` and do not edit it alongside another brief.

## Authority

- **Owner, 2026-09-19.** The other pain point of a big network is building it: slow-driving a
  commander or chaining drone hubs along the line. The hub **builds new track** from its own stock
  by dispatching its repair drones to the construction sites. **The gate: a line does not start until it
  is connected to the hub**, meaning one of its end stations is on the hub's network. A line placed
  from a station the hub cannot reach waits, and starts the moment the network grows to touch that
  station. Cost is the normal element cost; there is no vanilla cheaper rate to match.
- Build 4's rulings carry over: cheap version, emergency speed, the principle that the feature
  must not replace one pain point with another, and the repair drones themselves (vanilla Wasps
  under the hub, a constant 30, launched from the pad, never charging, track mode with its save
  guard; build 4's brief). Both bans bind; no new
  persisted name if build 4's list carries the kind, and if it does not, stop and report.
- Testing depth (owner): a smoke test only.
- ⚖️ **Owner ruling 2026-09-25, on this brief's construction-group stop: "1 is fine" — the whole
  line is one job, the game's own way.** New track is one `construction_group`: only its leader
  holds the cost and work requests, and the leader's `Complete()` finishes every element at once
  (`ConstructionSite.lua:32,2671`, `Tracks.lua:460-474`, 1.1.1.405907;
  `reports/TRAIN_HUB_BUILDTRACK_BLOCKER_20260925.md`). So the hub pays the group's **outstanding**
  cost from stock and completes the leader after a build time scaled to the line's length, which is
  build 4's repair path. Element-by-element order and per-element payment are dropped; End state 2-5
  below read with that. If the whole line appearing at once reads wrong in the smoke, the next
  step is feeding the cost in over the build time (pause the line on a stock-out), still
  completing at once. Taking over the group's accounting to finish single elements is not
  authorised.
- ⚖️ **Owner ruling 2026-09-25, in the attended smoke: repairs take priority, and the drone cap goes
  to 60.** *"I think repairs take priority and we just increase the drone cap to 60 that should be
  plenty."* Seen in the sitting: vanilla splits a placed line into 5-element construction groups
  (23 on one line), each became its own build job and Wasp, and one line had 21 of 30 Wasps out.
  Keep one job per native group. Raise `Floor.HubRepairTune.MaxDrones` to 60 (it counts the fleet
  and track flights together); the fleet chunks 5 / 15 / 25 are the owner's earlier ruling and stay,
  so the added slots go to track work. A queued or broken-track **repair dispatches before any
  queued build**, and builds never take the repair reserve. No frame-rate check: a vanilla Drone
  Hub runs 120 drones fully teched (owner, in the sitting, from its own panel reading 20/120).

## Read first

**Current inheritance:** spec §10 “Drones L5” overtakes the pad/constant-fleet/scripted-route wording below; take `reports/drones_chain/L6_QA_20260925.md` C1–C6 and D14(g,h) into the active build's work list, preserving each test's stated trigger.

Build 4's brief and report. Facts from the 1.1.0.403908 source, with the line that could falsify each:

- **New track is the same site class as a break.** `PlaceTrackLine` places a `TrackGridElement`
  construction group (`Tracks.lua:108`), so build 4's completion path completes it unchanged.
  Vanilla notes whether the line has a drone hub in reach (`has_group_with_no_hub`, `Tracks.lua:122`).
- **Both ends must already be station connectors** (`Tracks.lua:240`). The hub builds the line,
  never the stations.
- **Cost per element:** `construction_cost_Metals = 200`, `build_points = 1000`
  (`Data/BuildingTemplate/Track.lua:5-8`); confirm the resource scale before quoting a per-line
  total.

## End state

1. **Trigger and gate.** A track construction group with an end station on the hub's network is
   queued as build work; one without waits, and is picked up when it becomes connected. A player
   toggle on the hub, separate from repair, your call.
2. **One job per line** (owner ruling above). Pay the group leader's outstanding cost from stock and
   complete the leader; the whole line finishes at once. If stock runs out, pay what is there, sign
   the hub, and wait; resume when stock lands.
   **Drones are never limited** (owner, 2026-09-19): any section in a drone's range is built by
   drones exactly as today, at the same time as the hub's job runs. The hub pays only the
   group's **outstanding** cost, so a line drones have part-supplied is never paid twice. The smoke has one line with a drone hub covering its middle.
3. **Time.** Flight at the emergency speed plus a build time scaled to the line's element count, a dial: a long line
   visibly takes longer than a repair, but never long enough to be the pain point again. Report
   the smoke's measured times per line, with each line's element count.
4. **The repair drone** flies out as build 4's do (engine mode, spec §10 "Drones L5") and works
   the line until it completes.
5. **Smoke with the owner:** a line from a hub-served station to a new far station with no drone
   in reach; a line placed from an unreachable station that starts when a second line connects it;
   stock running out mid-job; save and reload mid-job; toggle off.
6. **Record** in the hub report and spec §10.

**Done means:** a line with no drone coverage is built by the hub from stock as a native group,
survives a reload mid-job, and a line placed before connection starts on connection.

## Scope

**Test save (owner, 2026-09-20):** sittings load `train_hub_base`, which has the stations, tracks and lines prebuilt; only the hub is built each round. Spec §10, "The standing test save". Do not build trains or lines each sitting. Unattended legs load `train_hub_base_agent` (hub prebuilt, full and switched off; spec §10).

In: the dev mod, TestKit slots (`tools/SMRTK.md`), the sitting, the records.
Out: building stations, drone logic, Module A, routing. Tunnels follow build 4's hide-and-show rule.

## Stops

- **Build 4's list has no kind field** and adding one needs a second persisted name: report.

## Do not claim

"Building works" from one line. The claim is the smoke's lines, element counts, times and reload,
in that colony.

## Lifecycle

Done when its smoke is recorded. Lifecycle: the orchestrator decides, once this is fired and done: park it in `Parked/` if it is kept for touch-up work, or delete it; either way its row in `README.md` follows (owner, 2026-09-21).
