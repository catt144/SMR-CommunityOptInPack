# 13 — build the hub's train bay (dispatch by need), dev mod

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/13_TRAIN_HUB_BAY_BUILD_high.md` in a fresh
session rooted at `B:\Dev\SMR\SMR-OptInPack`. Authored by the train orchestrator, 2026-09-28, at
the HEAD named in its commit. Start with `git log --oneline -8`, `git status`, `git pull`.

## Authority and outcome

The owner's direction is **spec §4.8 ruling 9** (`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`,
grep `9. **Hub dispatch is a train bay**`). Read it whole; it is settled and not reopened here. In
short:
- the bay is the colony's stored-train pool;
- the player sees the vanilla cap;
- hub extras go up to **5 per hub route** by need and are **recalled to the bay as soon as idle**;
- at save, empty hub trains are put on the engine's delete-on-load list and counted into the pool,
  and `SaveGameDone` undoes both;
- loaded hub trains persist as a `HubTrain` class with `persist_baseclass = "Train"`;
- when a station joins a hub route, one train from the pool fills the new vanilla slot.
The owner asked for this build to go to another agent (2026-09-28).

**Done when** the dev mod (`tools/devmods/train_hub/`) does all of ruling 9, with:
- a desk smoke over the archived 1.1.1.405907 bodies, in the style of the existing `tests/*smoke.py`;
- sitting steps for the orchestrator, a smoke only, about five steps (see Sitting);
- a short report, `docs/agent/reports/TRAIN_HUB_BAY_<date>.md`, with one pointer line under ruling 9.
The orchestrator runs the sitting; you claim no live result.

## What is already measured (claims to check once, not re-derive)

- **Store and deploy work** (bay probe, 2026-09-28, log
  `Mars.exe-20260928-11.52.17-6aad2d75.log`, archived by the orchestrator under
  `docs/archive/train_routing_5d_20260927/sittings/`):
  - `P.Bay` in `Code/50_TrainHubDispatchProbe.lua` called vanilla `Train:DestroySilent` on train
    2000001844: pool 6 → 7.
  - It then called `TrackBase:AssignTrain(hub)` on hub arm 1 (the 2008 line): a new train,
    2000001890, spawned on the hub in `LoadTrain`.
  - The owner saw it appear "right in the middle of the hub kind off center onto another loading
    platform". Code reading says `Spawn` and `Stop` share the park distance and siding offset
    (`20_TrainHub.lua`, grep `kind == "Stop" or kind == "Spawn"`), so it should sit on arm 1's
    siding. **Not settled:** whether it sits where a parked train sits. **Not seen:** a spawned
    train departing.
- **Reassignment holds but is not the design:** the move probe `P.Run` kept a train on `2009-6430`
  through eight hourly re-checks. Brief 11's report `reports/TRAIN_HUB_DISPATCH_20260927.md` holds
  that source chain and its **need signal** sketch (branch_need / child_need per hub line). Reuse
  the need signal. The move mechanics are superseded by ruling 9.
- **Every route but one was at the vanilla cap** on the owner's fixture (probe refusal,
  `Mars.exe-20260928-11.11.49`). The extras above the cap are what make dispatch useful at all.
- Stream reads: TestKit slot 6 logs every train's command, station, line, cargo and assignments,
  and every station stock change (`SMRTK_STREAM`). Idle trains read `command=false` and re-check
  once per game hour (vanilla `Train.lua:63`).

Further records: `docs/agent/facts/INDEX.md`, `docs/agent/bugs/INDEX.md`. Cite every game line
from the archived tree (`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src`) and re-derive
line numbers with `grep -n` when you use them.

## Judgment delegated to you

- The file layout. A new dev file for the bay is the expected shape; register it in both
  `metadata.lua` and `items.lua` (WORKFLOW.md).
- How a hub train leaves the player-visible count, and how hub extras still get past the cap
  gate. Vanilla gates in `AddTransportLink` / `CanAddVehicle` / `GetTrainsOnRoute`.
- The need-to-trains rule, the "idle" threshold for recall, and hysteresis.
- The exact save-time sequence.
Record each call in your commit message.

## Scope and fences

**In:**
- the bay, extras, recall, `HubTrain`, save-time storing and auto-fill, in the dev mod;
- read-only accessor exports added to `40_TrainDistribution.lua` for the need signal (brief 10's
  file: add exports only, change no behaviour);
- the spawn position in `20_TrainHub.lua`, **only** if the desk or the sitting shows a spawned train
  off its siding;
- retiring the throwaway probe (`50_TrainHubDispatchProbe.lua` and its registration) once your
  build replaces it;
- TestKit slot 3 (`B:\Dev\SMR\SMR-BugFixPack-TestKit\Code\80_AgentSlots.lua`), rebound to whatever
  your sitting needs. Keep `tests/distribution_slots_smoke.py` passing.

**Out:**
- train movement in `20_TrainHub.lua` (owner: finished, 2026-09-21);
- `10_TrainFloor.lua`;
- distribution behaviour;
- the minimum shipment (held, ruling 8);
- the shipping mod `Code/`;
- TestKit Scratch and slots 1, 2, 4–6.
Report findings outside the fence without editing.

## Rules that apply

- `CLAUDE.md`.
- `docs/agent/FIX_POLICY.md`: read its header before any code. `HubTrain` is a new persisted
  class name, so record it in the persisted-name inventory the way that section asks.
- `docs/agent/WORKFLOW.md` for tests.
- The `doc-editing` skill before the report or the spec pointer.
- The save ladder in spec §4.8 (grep `"Minimally" is this ladder`): name each rung you use.
- `python tools/doccheck.py` and `python tools/parsecheck.py --dir tools/devmods/train_hub/Code`
  before each commit. Commit with a pathspec.
- Keep a live todo list from before your first write: one item per commit-and-verify unit, one in
  progress at a time.

## Sitting (for the orchestrator to run, attended)

Write about five steps from `build6_capacity_covered_pass3`, preloaded into slots, with slot 6's
stream on so no unit needs selecting. The smoke must show:
1. a hub train spawns on the siding of the arm it is deployed to;
2. it departs and serves the line when there is work;
3. it returns to the bay when idle;
4. the player-visible route count stays vanilla;
5. a save and reload with the hub brings hub trains back through the pool, with 0 `LUA ERROR`.

Give each step a named prediction written before boot. Loading **without** the mod is the ship
test's, not this smoke's.

## Stops (report instead of continuing)

1. Extras past the cap need a copied vanilla body rather than a wrapper.
2. A spawned hub train cannot reach a siding without a movement change.
3. The save-time storing cannot avoid rung 4: a destination booking or cargo left behind by a
   deleted train.

## Claim limits

Write "desk-verified; live smoke owed" for anything not run in the game. Do not claim that the
without-mod load degrades cleanly: that is SOURCE until the ship test.

## Close-out

Record the executed model from your transcript. Do not delete or move this brief: the orchestrator
owns its lifecycle.
