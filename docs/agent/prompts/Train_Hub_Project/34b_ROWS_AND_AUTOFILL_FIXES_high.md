# 34b — Export rows keep each depot's Desired Amount: build the pairing filter (fix build, fresh session)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/34b_ROWS_AND_AUTOFILL_FIXES_high.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`, now. A previous session did phases 1 and 2 and
ran sitting 1. Its record is `docs/agent/reports/TRAIN_34B_PLAN_20261002.md`; read §"Sitting 1"
and §"The next build" first.

Reasoning: high, because this changes the drones' busiest code path (the pairing seam).

## Where things stand (claims; one check each)

- **Fix 2 is built (`d6dbca0`, cleanup `e120c83`).** Auto-fill is cut, the guard on the hub's
  `AssignTrain` refuses a train there, and `HubTrain` is kept (ban 1). The owner says the hub never
  showed Construct Train or Send out Train, so the button-greying methods were removed. **Owed:**
  its in-game check, smoke steps 4-7 in the report's §"The one smoke, preloaded".
- **Fix 3 is closed here.** The cause is vanilla: train food cargo shrinks about 4% at a game-hour
  boundary while the unload hands over the booked amount. The fix-pack bug report is
  `docs/agent/reports/TRAIN_CARGO_SPOILAGE_BUGREPORT_20261002.md`. The owner ruled no clamp here.
  Do not touch it.
- **Fix 1 is the open work.** The first build (`b4106ce`) raised the Export row's demand desired to
  capacity. It applied in game (`demand_desired=120`) and the depot still drained, so that write is
  dead code.
  - Sitting 1's witness: 151 food storage-to-storage pairings, of which 149 fit "the destination is
    below its own Desired Amount, or ranks above the source", and no source ever has a floor.
  - The station at 120 outranks a depot at 50 and drains it.
  - Evidence: log `Mars.exe-20261002-17.41.30-6aba6e65.log`, report §"Fix 1: the build applied, and
    the theory is refuted".
- **The code lives in this mod since brief 34.** It is in `Code/StationRows_*` and `Code/TrainHub_*`,
  with tests in `tools/trains/hub/tests/`. The map is `reports/TRAIN_MOVE_20261002.md` §"Handoff".
  The TestKit slots are at `aeaf496`: slot v2, with slot 1's `MapGet` fixed.

## Authority and outcome

The owner, 2026-10-02, after sitting 1. Spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`
§4.8, grep `The lever, owner 2026-10-02`. Settled; do not reopen it.

- **Build option 1, the FindTask pairing filter.** A pairing from a storage into an Export row
  takes only the source's stock above its own Desired Amount. If no source has stock above its
  Desired Amount, re-ask once with that building excluded, and otherwise return no pairing.
  Producer output passes untouched.
- **No reverse block.** In the owner's words: *"blocking is the wrong call if the desired amount on
  local storage depots should win anything above that leaves."* A depot below its Desired Amount
  may still refill from the Export station up to it. Stock settles at each depot's Desired Amount.

Outcome:

- Drones never take a depot below its Desired Amount to fill an Export row.
- The depot's stock above Desired still reaches the row, as does producers' output.
- Import, Balanced, Not accepted and the trains behave as before.

Done when:

1. the dead `b4106ce` write is reverted;
2. the filter is built with its harness leg and desk-checked;
3. one smoke covering Fix 1 and Fix 2's steps is preloaded;
4. the owner has run it and both pass.

## Your judgment

The filter's shape, where it hooks, and its guard against starving drones when it keeps refusing
the best pairing are yours. Record each call, and the vanilla source lines with the build they were
read on, in the commit message. Sitting 1 ran a log-only wrapper on this seam: 931 pairings over
11.5 game hours at Ultra, with no errors.

## Testing

Smoke only (spec §10). Preload SMRTK slots (`tools/SMRTK.md`): the owner clicks and does not type.
Name each slot's function beside its number, call hubs by role, and write predictions before boot.
Advance time with Run until at top speed. Re-press the watch slots after a load, and the run slot
after an autosave.

The predictions:

- slot 1 reads the Export row and the Food depots;
- over one sol, **no pairing into the Export station leaves a source below its Desired Amount**,
  while pairings overall stay above 0 (the control);
- a depot that starts above its Desired Amount settles at it, and a depot below Desired may
  receive from the station, but never above its Desired Amount;
- Fix 2's steps 4-7 run as already written.

`FIX_POLICY` §8's both-configuration run belongs to brief `35`.

## Scope

In: the Export row's drone-side sourcing; reverting `b4106ce`'s write; the smoke.

Out: Fix 3 (closed), trains' loading and routing, Import and Balanced, the depot's rows, train
movement, and anything brief 35 owns. Report outside findings without editing them.

## Stops (report instead of continuing)

1. The filter needs a persisted-name change or crosses a ban in `FIX_POLICY`'s header.
2. The filter starves drones (repeated refusals of the same best pairing) and no cheap guard fixes
   it. Report the measured behaviour and the options.

## Claim limits

A desk check proves the code path: say "desk-verified", not "fixed", until the owner's smoke passes.

## Work list, start, references, lifecycle

- Keep a work list, one item per commit-and-verify unit: in the todo tool if the session has one,
  otherwise in the report.
- Start with `git log --oneline -5` and `git pull` in both repos. This brief was rewritten at
  `a5869cf`.
- Append to the existing report; do not start a new one.
- House rules: `CLAUDE.md`, `docs/agent/WORKFLOW.md`, `docs/agent/FIX_POLICY.md` (§8 includes the
  player-text rule for any tooltip). Skills: `smr-bug-library` for engine facts, and `doc-editing`.
- Tell the orchestrator when the smoke is preloaded. The orchestrator owns this brief's lifecycle;
  do not move or delete it.
