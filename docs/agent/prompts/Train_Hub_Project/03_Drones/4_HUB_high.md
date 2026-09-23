# Drones chain, link 4 — the hub half: dispatch, the pending list, the save guard

**Link 4 of the `03_Drones` chain** (`README.md`). ⛔ **HELD until the structure pass is out of
`tools/devmods/train_hub/Code/20_TrainHub.lua`** — check `git log` on that file and the structure
brief (`../01_TRAIN_HUB_STRUCTURE_high.md`) before you start; only one brief edits it at a time.

Read `DESIGN.md` — it is the whole design and it is settled — and your `## Notes from upstream`,
which links 1, 2 and 3 wrote. `git log`, `git pull` both repos first.

## Authority

`DESIGN.md`'s owner rulings, unchanged. The flight already exists and is tuned
(`Code/30_TrainHubDrones.lua`): **you call it, you do not rebuild it.** This link is the hub's half —
everything in `DESIGN.md` §§1, 2, 4 and the save guard — plus the persisted name.

**Both bans bind** (`FIX_POLICY.md`). This build adds persisted state: name the pending-repair list
once, permanently, with the kind field build 5 needs, and add it to the persisted-name inventory in
the same commit.

## End state

`DESIGN.md` §1 (dispatch and reachability), §2 (completion at the deadline, the outstanding cost
only), §4 (the infopanel line and the track-repair toggle), the save guard, the `CanBeControlled`
wrap and the no-free-drone-leak backstop — built on the flight link's calls, with the smoke left to
link 5.

**Reachability is yours alone now (owner, 2026-09-23).** `DESIGN.md` End state 1 defined what a
repair drone can reach as "anything a repair drone following the track could reach" -- the flight
itself enforced it. Engine mode flies straight over the terrain, so the path no longer constrains
anything: a drone can physically reach an isolated network. **Dispatch must refuse a target off the
hub's connected graph**, because nothing downstream will. The graph and the "track work" definition
(owner, 2026-09-19) are unchanged; only their enforcement point moved.

**The standing fleet (owner, 2026-09-23).** *"since the are acting as normal drones we should have
maybe 5 out standying by at idle? And then dispatch can deploy and return more as needed?"* Five is
the baseline idle count, superseding the "like 2" low tier below. With `work_radius` fixed at 15
hexes and little but the hub inside it, vanilla `Idle` leaves them effectively parked; if the owner
builds within the radius they pitch in, which the owner accepts. Keep them genuinely vanilla --
`TryTakeTask` draws only from their own `command_center` (`Drone.lua:708`), so they cannot be taken
by other work, and past `distance_to_provoke_go_home_cmd` `Idle` sends them home rather than astray.

**Plus fleet scaling by load (owner, 2026-09-23).** `DESIGN.md`'s "constant 30, launched on demand"
is refined: the hub launches only what the work needs and brings the surplus home. The owner's
words: *"since we are allowing up to 30 drones, but won't need them all in flight, if drone load is
at low maybe we only have like 2 out there and if it goes to medium we launch X more drones, high
we launch X more drones. And as it dials back down we bring X drones back into the bay?"* The
tiers, their thresholds and the step size are **your call** — record them in the commit message and
give the owner a console dial per number, the way the flight link's tuner works, because these are
feel values link 5's sitting will want to move. Scaling down recalls and removes; it never strands
a drone mid-job. The hub is already a `DroneControl` (`20_TrainHub.lua:95`), so `drones`,
`SpawnDrone`, `KillDrone` and `GetIdleDronesCount()` (`Lua/Buildings/DroneControl.lua:99, 725, 729,
992`, build 25390750) are inherited rather than built; prefer `DespawnNow`'s `KillDrone` route over
a bare `DoneObject`, which skips the controller's bookkeeping.

`FIX_POLICY` §0 sets the disable direction for content. The toggle is tested in both directions in
link 5, not here.

**Flight has two modes, and you serve whichever one ships** (2026-09-23): the engine paths between
our pit ends (`9a540dd`), or the scripted flight at tag `drones-scripted-flight-20260923`. Link 3's
sitting picks one. Build dispatch against the flight file's API, never a mode's internals, and keep
**`DESIGN.md` section 2's persisted deadline as the only authority**: an engine leg's arrival is
solver-owned and is not knowable at dispatch, so the ETA you notify and the cost you charge come
from your deadline, and the visual is advisory.

**Save, corrected by L2E (`L2E_ENGINEFLIGHT_20260923.md`):** engine-driven legs and queued holds
**need no save guard** — a drone under a stock command carries no mod thread, so it persists as an
ordinary Wasp, which is what `DESIGN.md` already allows. The guard exists for **our own game-time
driver thread** (EF-023), so it covers the scripted mode and our pit ends. L2E removes its own
prototype visuals at save; **you replace that removal with adoption from the persisted deadline**, so
a reload continues the job instead of blinking it away. Its hold has a 60 s game-time timeout, after
which vanilla's `Idle` takes the drone — that timeout is exactly the window a save loaded without
our code falls into, so re-arm inside it.

⚠️ **Version.** The engine facts in these notes and in `DESIGN.md` were read on **1.1.0.403908**
except where a note says 1.1.1; the installed game is now **1.1.1.405907** (build 25390750), and
`doccheck --emit-fingerprint` reports every fact group MOVED. Re-read each line number you build on;
the sweep is queued at `prompts/perma/gamepatch/`.

## Live work list

One todo item per commit-and-verify unit, before any write.

## Scope

In: `20_TrainHub.lua`, the persisted name and its inventory row, the panel, the toggle, the tests
that run offline. Out: the flight file's internals, art, the entity, the model, build 5's track
construction (design the list for it; ship only the repair kind).

## Stops

1. The structure pass is still in `20_TrainHub.lua`: wait or report, never edit alongside it.
2. A second persisted name turns out to be unavoidable: stop and route the name to the owner.
3. The completion path cannot charge the outstanding cost without double-paying: report the
   measurement rather than shipping a guess.

## Do not claim

Do not claim the repair works from an offline run. Claim the code path, the persisted shape, and
what link 5's sitting still has to show.

## Notes from upstream

- **Link-1 evidence:** `docs/agent/reports/drones_chain/L1_SURVEY_20260922.md`; engine facts
  `EF-112`–`EF-115`; verbatim lenses under `docs/agent/reports/drones_chain/agents/`.
- **Reachability:** `ForEachConnectedTrack` is one-hop and calls `GetDestStation`, which rejects a
  track while `elements_under_construction` is nonempty. A break creates exactly such a site, so
  that helper can hide the broken edge and everything beyond it. Build an explicit hub-rooted BFS
  with visited station/tunnel nodes and visited tracks, using physical `GetStartStation` /
  `GetEndStation` owners across existing broken tracks plus reciprocal tunnel `linked_obj` edges.
  Cached routes, `CanTrainsRun` and a nil helper result are not repair reachability.
- **Graph smoke owed:** component before/after a connecting break, far side still reachable for
  repair, independent remote component excluded, then a tunnel and a station cycle. Log endpoint
  owners, repair group, `elements_under_construction` and visited sets.
- **Completion:** use the live repair construction-group leader's dynamic `Complete()` after
  validating the site and outstanding cost. It dispatches to each `TrackConstructionSite:Complete`,
  which restores/reconnects the broken element. `DESIGN.md`'s generic
  `ConstructionSite:Complete()` citation is an imprecise body reference; do not call that base body
  directly or synthesize a drone work request.
- **Work/accounting boundary:** controller radius governs automatic request discovery; track graph
  membership does not. Station maintenance material can self-fill, but the `repair` work request
  still needs a worker; dust is cleared by maintenance and has no separate clean request. Ship only
  the work kinds `DESIGN.md` authorizes and keep each material/work/completion path explicit.
- **Save guard:** `EF-023`/`EF-027` establish by-value command-thread persistence;
  `EF-024`/`EF-030` establish start/done hooks including autosave; `EF-070` establishes that game
  time can run before the persist walk. Persist only pending data plus absolute deadline. Raise a
  save gate, synchronously remove track visuals/commands, make every spawner honor the gate until
  `SaveGameDone`, then re-arm from remaining deadline even after a failed save. Load validates and
  does the same; never restart a full trip. Manual-save, autosave, reload, failed-save and long-soak
  A/B remain owed.
- **Control:** chain `Drone:CanBeControlled`; after calling the captured original, return false only
  when the live `command_center` is a train hub and otherwise return the original result. That one
  gate greys both reassign buttons. Keep the no-free-drone backstop separate.
- L2 API/report: `docs/agent/reports/drones_chain/L2_FLIGHT_20260922.md` and
  `SMROptInHubFlight` in `Code/30_TrainHubDrones.lua`. `Create(hub, started)` returns an ephemeral
  record; `Send(record, target, true)` retains that absolute start; `Update(record, now)` samples
  it without economy; `Remove(record)` cleans it. Multiple independent records are supported.
  `Route(hub,target)` uses physical connectors across broken tracks and reciprocal tunnels.
- Persist no flight record or plan. You own pending data and the authoritative deadline; derive
  the visual start from that deadline/plan offsets, sample elapsed time after rearm, and keep
  that authority if tunables changed. `work_done` includes end animation, not just work dwell.
  L2 clears every registered visual at save start and blocks creation until save done; it
  deliberately does not reconstruct jobs. Native save/race/soak checks remain yours and L5's.
- L2 never registers a prototype in the hub's drone dispatch list or invokes a work request.
  You own the fleet integration, control wrapper, dispatch and completion. The console driver
  samples only its own selected visual; drive your records through `Update` independently.
- OI-25 approved 2026-09-22; the column is settled. L3 still owes owner-tuned constants and
  actual clearance/import persistence; L2's mocked success is not a native verdict.

- **Owner ruling, 2026-09-22 — malfunction and power loss never stop the repair work.** The owner
  asked what happens when the maintenance gauge fills and the hub needs maintenance, and what
  happens in a network power outage. Build 3 already answers both and this link keeps them:
  `SMROptInTrainHubBase:CanCommandDrones` (`20_TrainHub.lua:972`) deliberately drops vanilla's
  malfunction gate (`DroneHub.lua:150-153`) because the hub's drones exist to repair it and it may
  stand far from any other controller; the hub is its own producer and the cold-start ruling keeps
  its source alive without a grid. **So `DESIGN.md` §1's "if the hub is working" means the player's
  switch (`ui_working`) and not destroyed — never `IsWorking`, which a malfunction or an unpowered
  grid clears.** A malfunctioned or unpowered hub still dispatches and still completes; only the
  player's switch stops NEW dispatches, and a repair already in flight always completes on its
  deadline. Prove both in an offline check, and hand link 5 the two sitting cases: dispatch with the
  maintenance gauge full, and dispatch with the grid dead.

- **Owner ruling, 2026-09-22 — a destroyed hub despawns its drones.** The owner asked whether we
  have a despawn mechanism for drones that are out when the hub is destroyed, since vanilla would
  leave them abandoned and ours are not reassignable while the hub lives. `DESIGN.md`'s backstop
  line is the design and it is unbuilt; **build it here**: any repair drone whose hub is gone, or
  whose controller is not a train hub, is **removed — in flight or idle** — and one carrying a
  resource **drops its cube on the ground first**, so nothing is destroyed with it. Kill the
  drone's command before removing it: nothing may go on executing a route owned by a building that
  no longer exists. The hub's own destruction path is not enough on its own — **sweep on load too**,
  so a save made between the two states self-heals. This closes the free-drone exploit (destroy the
  hub, keep 30 Wasps): orphans are never handed to the colony. Link 5's sitting tests it: drones
  out, hub destroyed, then save and reload.

- **L2M2 API note, 2026-09-22.** `Create`, `Send(record, target, true)`, `Update(record, now)`,
  `Remove`, `Route` and `Position(plan, t)` keep their shapes. Two changes: every record made by
  `Create` is registered with the module's own game-time driver, which services all records, so
  you may leave sampling to it, and calling `Update` yourself remains safe (a repeated `now`
  issues nothing; a sparse or late `now` snaps to the absolute position and flies on). And the
  plan offsets `arrival - started`, `work_done - started`, `removed - started` now follow the
  motion dials (`Accel`, `TurnRadius`, `Speed`, `ClimbRate`, heights), not a fixed budget: derive
  the visual start from your persisted deadline and the plan's offsets at rearm time, as before.
  `LandingEnd` fires only at `removed`. Nothing here is persisted.

### L2E handoff, 2026-09-23

Engine mode (`9a540dd`, report `L2E_ENGINEFLIGHT_20260923.md`) changes two things this link builds
on. **Save guard:** a drone under a stock `FlightGoto` or the stock `WaitUninterruptable` hold has
no mod thread and stays in the save; only scripted motion (rise, exit, work pose, descent) is
removed at `SaveGameStart`, and re-arming from the deadline is owed only for those. **Load:** the
prototype's `OnMsg.LoadGame` sweeps any `FlyingDrone` whose controller is a train hub and that
`hub.drones` does not hold — replace that sweep with adoption once the fleet enters `hub.drones`,
or fleet Wasps in a loaded save are safe only because they are in the list. `DespawnNow` was not
adopted by the prototype: `DroneControl:KillDrone` asserts `hub.drones` membership
(`DroneControl.lua:729-733`), so it is the fleet's route, not a loose visual's. The infopanel
during an engine leg shows `Getui_command`'s fallback for `"FlightGoto"`/`"WaitUninterruptable"`;
the panel line this link builds should not rely on `command` for the repair drone's status.

## Lifecycle

Append what the smoke must cover into link 5's notes, then **delete this file and strike its row in
`README.md` in the same commit**.
