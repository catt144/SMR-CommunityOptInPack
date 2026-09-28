# Train bay fixes — 2026-09-28

Brief: `prompts/Train_Hub_Project/15_TRAIN_BAY_FIXES_high.md`. Authority: design spec
§4.8 ruling 9 and its 2026-09-28 vanilla-first amendment. Started at `d0f2b8a`;
`git pull` reported up to date. Executed model: GPT-6 (Codex), as identified in the
session instructions; no more specific model id or effort was exposed. No subagents.

**Desk changes implemented; attended smoke owed.** Dispatch and cargo-display defects have
regressions against their actual call paths. Spawn placement now explicitly uses the parked
siding, but the native cause of the original live discrepancy is **unresolved**. The old
spot-only desk proof did not establish it, and neither does a mocked native boundary here.
The complete smoke suite is **not green**: its traffic test fails identically on the starting
revision. Movement remains outside this brief.

## Changes and evidence

### Vanilla first — `989bd56`

`70_TrainBay.lua` keeps the existing need arithmetic, pool, hidden count and recall semantics.
Extra dispatch now requires every vanilla train on the route to be demonstrably working,
continuous excess need for `B.shortfall_delay` (one game hour), expiry of `B.settle_delay`
(three game hours), and the existing pool, platform and cooldown checks.

Delegated calls, recorded in the commit:

- Working means `GotoStation` off-platform, or `LoadTrain`/`UnloadTrain` with cargo, assigned
  resources or passengers. Empty loading reevaluation, idle, unknown states and a route with
  no vanilla train fail closed. Enumeration must agree with the vanilla route count.
- Shortfall means wanted extras exceed deployed extras. The timer resets when that ceases,
  vanilla stops working, the hub stops working, routes rebuild, or the session loads/starts.
  Need may mature during the settle interval; a qualifying line can deploy when it ends.
  Conditions are observed at the existing ten-game-minute checks, not continuously between them.
- A successful request closes that route for the rest of the check, including another hub on
  the same route. The no-work recall cooldown remains two game hours. Vanilla auto-fill for a
  newly joined station remains independent of the extra-only gate.
- `B.Read()` adds `working`, `shortfall` and `settle` to each line. Reading never advances a timer.
  New timing state is file-local runtime data, discarded on load; no persisted name was added.

**MEASURED at desk:** `bay_gates_smoke.py` covers the settle boundary, renewed need, idle and
empty-loading controls, load/new-game resets, zero vanilla, and separate hub arms on a shared
route. Mutations removing settle, working, persistence, reset and the per-route guard each fail
the intended assertion. `bay_smoke.py` retains pool, hidden-count, recall, save and auto-fill tests.

### Spawn placement — `9b58888`

The exported `SMROptInTrainFloor.HubSpawnLocation` calls the existing computed Spawn geometry,
which shares the parked Stop position and faces outward. `70_TrainBay.lua` applies it to a newly
spawned hub train in `TransportLinkChanged`, **after** extra class conversion and **before**
vanilla assigns the track and calls `Train:Start`. This also covers auto-fill/player spawns.
Travelling trains, arrivals and remove events are untouched. No movement method changed.

**SOURCE:** archived **1.1.1.405907**, under
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/`:
`Lua/Buildings/Track.lua:428-457` places the Train, publishes its spawn state, adds the link,
assigns its track, reserves the platform and starts it in that order.
`CommonLua/Classes/_object.lua:233-240` changes the metatable and calls `OnClassChanged`.

**MEASURED at desk:** `bay_spawn_smoke.py` checks the real helper across arms, rotations and
track ends, then archived `AssignTrain` through the real bay handler with deliberately wrong
native lookup and class-change poses. The final object must have the computed position and
outward angle. Removing the final `SetPos` fails. These corrupt poses are boundary controls,
**not a reproduction of what the native engine did**.

**Rejected hypothesis:** the checked-in entity supplies no baked Spawn/Stop spots. The test
parses `SMROptInTrainHub6.entjson`, reports its hash and reconciles its connector presence and
Spawn/Stop absence. The earlier session message suggesting baked Spawn spots was withdrawn.
The brief-13 test only exercised the lookup with geometry doubles; it did not observe a native
spawned object. Its PASS wording now states that narrower scope.

**Live reading still needed:** `[TrainBay] spawn` records train, hub, arm, pre-correction pose,
target pose and actual pose after the setters. While that train is still in `LoadTrain`, the
owner must see it on that arm's siding, facing out. Target/actual agreement in Lua alone does
not prove the rendered placement. A before/target mismatch localizes a placement discrepancy;
if they already agree but the train subsequently appears wrong, inspect the first streamed
command transition. A repair that requires movement changes stops under this brief's fence.

### Stocked stacks disappearing — `9ed5f4f`

**MEASURED reproduction:** a hub holding 220 resource units sends 10 to an empty spoke under
the real distribution code and archived train/depot/cube bodies. Stock remains 210, but all
its displayed cubes disappear. This fails on the pre-fix code and with the fix removed.
Fixture arithmetic and expectations are executable in `cargo_view_smoke.py`; the receipt
records the archived body hashes.

**SOURCE cause:** distribution gives a source hub temporary capacity zero while allocating
cargo. Archived **1.1.1.405907** `Lua/Units/Train.lua:769-770` updates station stock inside that
call; `Lua/Buildings/MultiResourceCubeVisuals.lua:422-435` calls the visual update, and
`:165-199` clamps its cube count by `GetMaxStorage`. That getter still sees the allocation
view. The old load heal redraws the stacks correctly until another transfer erases them.
This explains why the previous sitting could improve without a changed-column diagnostic.
It does not establish the unrecorded native state of the owner's earlier screenshot.

The hub's `SetCount` now scopes **only cube drawing** to physical per-resource capacity, using
the physical formula from the same archived file's `:571-589`. Outside that non-yielding draw,
`GetMaxStorage` delegates to the live depot getter and distribution sees its existing answers.
The scope unwinds on failure and is runtime-only. It does not capture a getter that editor
load-order changes could already have wrapped. Existing column allocation and height caps stay.

`cargo_view_smoke.py` verifies the same cargo transfer, surviving cubes, drain/refill, the
visual ceiling at base/expanded storage, error cleanup and the removed-fix mutation.
`pallet_visuals_smoke.py` still verifies load healing. The capacity-upgrade section and
`40_TrainDistribution.lua` are unchanged against `d0f2b8a`, checked by exact section comparison
and `git diff`; the comparison also held for the traffic-to-cargo region of `20_TrainHub.lua`.

## Verification receipts

**RAN 2026-09-28**, Opt-In HEAD `378bd39`, TestKit HEAD `63c94ba`:

```text
python tools/devmods/train_hub/tests/bay_fixes_suite.py --output docs/archive/train_bay_fixes_20260928
```

Exit **1**, intentionally retaining any smoke failure. The filter is
`tools/devmods/train_hub/tests/*_smoke.py`: **19 members = 18 passing + 1 failing**, reconciled
against the explicit member list in
[results.json](../../archive/train_bay_fixes_20260928/results.json). Each sibling receipt
contains its command, revisions, exit and full output. The output destination is append-only;
a repeat run needs a fresh path.

The failure is `traffic_smoke.py`, `-10800 != 0`, in its arrival-orientation assertion. The
runner separately extracts `20_TrainHub.lua` from **starting `d0f2b8a`** and repeats that exact
failure; [baseline receipt](../../archive/train_bay_fixes_20260928/traffic_baseline.txt).
No traffic-test assertion was weakened and no movement code was edited. `move_smoke.py`,
`bay_smoke.py`, the new regressions, distribution, capacity, pallet and other discovered
smokes pass. This is a reported outside-scope limitation, not an all-green claim.

Also RAN: `python tools/parsecheck.py --dir tools/devmods/train_hub/Code` and
`python tools/parsecheck.py --dir ../SMR-BugFixPack-TestKit/Code`, both PASS. Documentation is
gated by `python tools/doccheck.py` before its commit. No game launch or attended test occurred.

## Attended smoke — predictions, NEVER RUN

For the orchestrator's next sitting: fresh restart with both mods and the TestKit, using
`build6_capacity_covered_pass3`. Slot **6 (stream every train and station)** remains read-only.
Its TestKit change at `63c94ba` adds `cubes` and `expected_cubes` for hub resource rows and emits
a row if cubes change without stock changing. `distribution_slots_smoke.py` exercises that case.

1. **Stream and settle.** Load, pause, press slot **6 (stream every train and station)**, then
   slot **3 (bay read: pool, extras and need)**. Read the initial stock/cube rows and remaining
   `settle`. Unpause. Predict no new extra deploys before the three-game-hour settle expires.
   Existing loaded extras may be present; compare deploy events, not just the total extras.
2. **Vanilla first, then siding.** Pause and press slot **1 (empty every non-hub station)**,
   then slot **3 (bay read)**; resume normal speed. An idle vanilla train must block that line.
   After `settle=0` and qualifying shortfall for an hour, predict at most one extra on that line
   per check. On its deploy, pause promptly and inspect the named arm while the train is in
   `LoadTrain`: it must stand on the siding facing out. Compare the spawn pose log. If no line
   qualifies, retain the no-deploy result and mark spawn unexercised; do not lower the timers.
3. **Service and stacks.** Resume and follow that train in slot **6 (stream every train and
   station)** output through `GotoStation` and unloading. Its cargo and station stocks should
   change. After hub transfers, positive stock must retain the expected visible cubes, capped
   by column height. Observe the beds too. Stop on stocked resources showing empty stacks or
   `cubes` disagreeing with `expected_cubes`; preserve the resource, time and train handle.
4. **Recall and count.** Pause and press **Scratch (balance non-hub stations to target)**,
   then resume. Empty extras should recall when idle and return to the pool. Slot
   **3 (bay read)** records that change. While extras are present, the station's Trains panel
   should still agree with the line's vanilla count/cap. A no-work recall pauses redeployment
   on its line for two game hours.
5. **Save/reload.** Save to a new slot. Compare the save stored/kept log and slot **3 (bay read)**
   before and after; the in-session snapshot undo must preserve the pool. Reload, press slot
   **6 (stream every train and station)** again, then slot **3 (bay read)**. Empty extras stored
   by the snapshot return to the pool; retained loaded trains remain. Predict a fresh settle
   interval and correct cube rows. Save/load/autosave stop the stream, so re-press slot
   **6 (stream every train and station)** after each. Archive the log and check `LUA ERROR`.

## Close-out and remaining work

The live todo was kept in session messages: dispatch, placement, stack cause, then receipts and
report. Code commits: `989bd56`, `9b58888`, `9ed5f4f`; receipt/test harness commit `378bd39`;
shared local-only TestKit `63c94ba`. The spec receives one pointer under ruling 9. The report
and archived receipts hold the source, controls, rejected hypothesis and untested boundaries.

The orchestrator owns the attended smoke and the unresolved native spawn diagnosis. The
pre-existing traffic failure is filed here for a movement-authorized task, not repaired by this
brief. No new owner ruling was needed, no new persisted name was added, and no capacity-worktree
change was merged. Keep brief 15 and its map entry until the orchestrator accepts its sitting.
