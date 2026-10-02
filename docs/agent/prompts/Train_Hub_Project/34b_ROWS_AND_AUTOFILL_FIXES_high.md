# 34b — Three owner fixes after the move: Export keeps Desired; no train in the hub; no cargo gain on unload (fix build)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/34b_ROWS_AND_AUTOFILL_FIXES_high.md` in
a fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`, **in two phases** (owner, 2026-10-02):
**phase 1 may fire now** (investigate and plan, no code edits); **phase 2 lands after brief `34`
closes** (33 closed 2026-10-02) (both fixes then edit the moved modules; editing now would collide with the move).
Reasoning: high (vanilla drone request priorities; vanilla train assignment and spawn).

## Authority and outcome

Three owner rulings, 2026-10-02. Both are settled; do not reopen them.

**Fix 1, Export rows.** After a live test, the owner said that with a resource's station row on
Export, drones *"drain everything ... including resource pads that have a desired amount set. ... I
expect drones to fill the station of all the excess up to the desired amount."* Spec
`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §4.8's mode table already says Export
drones haul *"the area's excess in"*. The ruling under it (grep `Export takes only the excess`)
defines excess as **stock above that storage's own Desired Amount.**

**Fix 2, auto-fill.** The owner: *"the station gets a train auto added to its line, the station
itself handles the spawn in from the station, not spawned in from the hub."* Spec §4.8 ruling 10
(grep `enters at the joining station`). Auto-fill stays. The train joins the joining station's
line and enters at that station, the way vanilla spawns one. It does not enter at the hub, and it
is not placed on the hub's arm siding. The owner, same day: *"If the add train is something the
player needs to do that is also fine. I don't want it to be a complicated thing, and I don't want
them spawned in the hub."* So cutting auto-fill, leaving the player vanilla's add-train at the
station, is acceptable if it is simpler. Either way, **no train ever appears in the hub**,
auto-filled or player-assigned.

**Fix 3, a one-unit food gain on unload** (owner, 2026-10-02, routed from brief 33's finding):
brief 33's witness saw one train's unload at the hub take 12 Food and 16 Sugar off the train while
the hub gained 13 and 17 (`docs/agent/reports/TRAIN_CROSSING_WITNESS_20261002.md`, grep
`appears from nothing`; log `Mars.exe-20261002-15.30.19`). Its hypothesis, unconfirmed: spoilage in
transit lowers the carried amount but not the booked one, and the unload hands over the booked
amount. Station spoilage is this project's own code (`60_StationSpoilage.lua`, which ships with the
hub). Find the cause; if it is ours and the fix is simple, fix it so an unload never adds more than
the train gave up. If it is vanilla or the fix is not simple, report the options instead.
**Owner ruling on Fix 3, 2026-10-02** (after the phase-1 plan at `bb736af`): find the writer first
(the log-only trap). **If the cause is ours, fix it at the source.** **If it is vanilla, add no
clamp here** (the station-rows rule against writing the cargo ledger stands) and **write a full
bug report the owner can send to the Relaunched Fix Pack**: the defect in one line; build id;
how to reproduce it; the log lines (with file name) and trap output that prove it; the vanilla
source lines with the build they were read on; whether it reproduces with this mod's modules off
(or that this was not tested); impact; and a candidate fix. Put it in `docs/agent/reports/`; the
owner carries it over. Either way, the report says what the cause is.

Outcome:

- **Fix 1:** an Export row's drones fill the station only from stock above each source storage's
  Desired Amount. A storage at or under its Desired Amount loses nothing to the row. Import,
  Balanced, Not accepted and the trains' loading behave as before.
- **Fix 2:** when a station joins a hub route and auto-fill adds a train, the train appears at that
  station. The hub stays a pass-through. Trains that already exist and pass through the hub move as
  before (movement is finished, owner 2026-09-21).

- **Fix 3:** the cause is named. If ours, an unload adds to the station exactly what left the
  train. If vanilla, a full bug report for the fix pack exists and nothing here clamps.

Done when all three are committed with desk checks, a preloaded smoke covers both, and the owner has
run it and seen each one.

## Evidence

**Fix 1:** the owner's screenshots, 2026-10-02, at build `e223b25` or later.

- `StationSmall(10650)`: row `Food · Export` at 16.5/120, Trains 0.
- `StorageFood(1067)`: Desired Amount 50, holding **8.2/180**. It was drained below 50 while the
  Export row was still filling.
- Balanced rows filled only once every other storage was full. The owner reads that as intended
  (vanilla); it is out of scope.

**Fix 2:** an orchestrator audit's reading of the dev mod at `4433c2f`. It is a claim: confirm it
before building on it.

- `tools/devmods/train_hub/Code/70_TrainBay.lua:109` `arm.track:AssignTrain(hub)` assigns the
  auto-fill train at the hub.
- `:76-91` places a spawned train on the arm's siding through `Floor.HubSpawnLocation`
  (`20_TrainHub.lua:402`). The placement fix is `9b58888`.
- After brief 34 these live in this mod; find them by those names.
- The `HubTrain` class is persisted name #15 (`FIX_POLICY.md` §"The persisted-name inventory").
  Keep it so old saves load (ban 1).

## Your judgment

**Fix 1:** the approach is yours. Find where the drain comes from (the row's demand priority, the
request amounts, or how vanilla moves stock depot-to-depot) and make the narrowest change that
honours the ruling. For stores with no Desired Amount of their own (producers' output, any depot
without the slider), match what vanilla's depot-to-depot moves do with them.

**Fix 2:** decide how the train comes to enter at the station, and what to do with the hub-side
siding placement once auto-fill no longer uses it. Remove it if nothing else needs it. If a
player-assigned train can still appear at a hub, report that path and keep what it needs.

For both fixes, record each call and its vanilla source lines, with the build they were read on,
in the commit message. The owner checks the results by eye at the smoke.

## Work list and start

Keep a work list, one item per commit-and-verify unit, one in progress: in the todo tool if the
session has one, otherwise in the report.

1. Run `git log --oneline -5` and `git pull`. This brief was authored after `9cff16d`.
2. **Phase 1, now:** investigate both fixes on the dev copies (`tools/devmods/train_hub/`) and the
   vanilla source, and write the plan to `docs/agent/reports/`: what you confirmed or refuted in
   the Evidence, where each fix goes, the change, and the smoke with its predictions. Edit no code
   and no TestKit slots (33's attended check holds slots 7-10; 34 is moving the code). Then stop
   and tell the orchestrator the plan is ready.
3. **Phase 2, after 33 and 34 close** (the orchestrator says so): re-read the moved files, apply
   the plan where 34 put them, desk-check, and preload the smoke. 34 closed 2026-10-02
   (`4edf446`): `tools/devmods/train_hub/Code/<NN>_<name>.lua` is now `Code/StationRows_<NN>_…`
   (10, 40, 45) or `Code/TrainHub_<NN>_…` (20, 30, 60, 70), and its tests are in
   `tools/trains/hub/tests/`. The whole map is in `reports/TRAIN_MOVE_20261002.md`, "Handoff".

## Scope

In: the Export row's drone-side sourcing, on stations with and without a hub; where auto-fill's
train enters; the unload's cargo accounting at stations and the hub.

Out: trains' loading and routing, Import and Balanced behaviour, the depot's rows, train movement
through the hub, and anything brief 34 or 35 owns. Report outside findings without editing them.

## Testing

This is a design pass, so a smoke test only (spec §10). Preload it into SMRTK slots
(`tools/SMRTK.md`): the owner clicks and does not type. Name each slot's function beside its
number, call hubs by role, and write predictions before boot. Advance time with Run until at top
speed rather than owner minutes of watching. An autosave disarms a slot; say to re-press it.

The smoke shows:

- one storage with a Desired Amount set, holding at or above it beside an Export row that keeps
  filling from storage above Desired;
- a station joining a hub route and its auto-filled train appearing at that station.

`FIX_POLICY` §8's both-configuration run belongs to brief `35`.

## Stops (report instead of continuing)

1. Phase 2 is reached and briefs 33 and 34 have not both closed.
2. Honouring either ruling needs a persisted-name change or crosses a ban in `FIX_POLICY`'s header.
3. Vanilla offers no way to honour a ruling without rewriting its request or train-assignment
   system. Report the options and their costs.

## Claim limits

A desk check proves the code path, not the behaviour. Say "desk-verified", not "fixed", until the
owner's smoke passes.

## References and lifecycle

- House rules and process: `CLAUDE.md`, `docs/agent/WORKFLOW.md`, `docs/agent/FIX_POLICY.md`.
- Use `smr-bug-library` for any engine fact you file (`docs/agent/facts/INDEX.md`,
  `docs/agent/bugs/INDEX.md`), and `doc-editing` for any doc.
- Report to `docs/agent/reports/` and tell the orchestrator.
- The orchestrator owns this brief's lifecycle. Do not move or delete it.
