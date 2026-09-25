# Train hub build 5: the hub builds track

**LIVE, fire when ready. Its hold is lifted** (2026-09-25): build 4's smoke is recorded
(`reports/drones_chain/L5_SMOKE_20260925.md`), and build 4 itself is
`03_Drones/DESIGN.md` with the hub half in `20_TrainHub.lua`. It is build 4's mechanism with a
second trigger and a fixed order, on the pending list `SMROptIn_track_work` that build 4 shipped
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
2. **Order.** Elements complete sequentially from the connected end outward, so the drone always
   rides built track to the next site; pay each element from stock as it completes, at the normal
   cost. If stock runs out, pause at the last built element, sign the hub, resume when stock lands.
   **Drones are never limited** (owner, 2026-09-19): any section in a drone's range is built by
   drones exactly as today, at the same time as the hub works the line from its end, and an
   element other drones finish is skipped. The hub pays only an element's
   **outstanding** cost when it completes it, so a site drones have part-supplied is never paid
   twice. The smoke has one line with a drone hub covering its middle.
3. **Time.** Per element at the emergency speed plus a build time per element, a dial: a long line
   visibly takes longer than a repair, but never long enough to be the pain point again. Report
   the smoke's measured times per element and per line.
4. **The repair drone** rides out in track mode and lays track as it goes, under build 4's save guard.
5. **Smoke with the owner:** a line from a hub-served station to a new far station with no drone
   in reach; a line placed from an unreachable station that starts when a second line connects it;
   stock running out mid-line; save and reload mid-line; toggle off.
6. **Record** in the hub report and spec §10.

**Done means:** a line with no drone coverage is built by the hub from stock, in order from the
connected end, survives a reload mid-line, and a line placed before connection starts on connection.

## Scope

**Test save (owner, 2026-09-20):** sittings load `train_hub_base`, which has the stations, tracks and lines prebuilt; only the hub is built each round. Spec §10, "The standing test save". Do not build trains or lines each sitting. Unattended legs load `train_hub_base_agent` (hub prebuilt, full and switched off; spec §10).

In: the dev mod, TestKit slots (`tools/SMRTK.md`), the sitting, the records.
Out: building stations, drone logic, Module A, routing. Tunnels follow build 4's hide-and-show rule.

## Stops

- **Build 4's list has no kind field** and adding one needs a second persisted name: report.
- **Sequential completion fights the construction group's own leader logic** (the group's first
  site carries the cost multiplier, `Track.lua:646`): report the fields and stop.

## Do not claim

"Building works" from one line. The claim is the smoke's lines, element counts, times and reload,
in that colony.

## Lifecycle

Done when its smoke is recorded. Lifecycle: the orchestrator decides, once this is fired and done: park it in `Parked/` if it is kept for touch-up work, or delete it; either way its row in `README.md` follows (owner, 2026-09-21).
