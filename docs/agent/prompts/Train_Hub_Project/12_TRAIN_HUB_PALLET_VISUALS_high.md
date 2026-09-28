# 12 — why do the hub's pallets draw empty while it is stocked? (investigation, fix if it is small)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/12_TRAIN_HUB_PALLET_VISUALS_high.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`. Authored at `9ef387b` by the train orchestrator,
2026-09-27. Start with `git log --oneline -5`, `git status`, `git pull`.

## Authority and outcome

The owner, 2026-09-27, on the look this must produce: *"the plan was is for them to fill up and then
any exceess me invisiblly stored which is how vanilla handles expansions"*. The standing ruling is
spec §10's storage-cap bullet (grep `the cargo stacks are capped at the height 150000 drew`):
storage 240000 per resource, stacks capped at the height 150000 drew, and stock past the cap is
stored and not drawn. The owner asked for this investigation on 2026-09-27, to run while they play
brief 11's probe sitting.

**Done when** you have the cause, with a desk or source reproduction and a falsifying check, and
either:
- a fix in the hub's cargo-display code that restores the intended look, with a desk smoke and
  sitting steps for the orchestrator (a smoke only, about five steps); or
- a report of why the fix is not small, with its cost and options for the owner.

Your report goes in `docs/agent/reports/TRAIN_HUB_PALLETS_20260927.md`, with one pointer line
under the spec §10 finding (see Evidence). The orchestrator runs the sitting; you do not claim a
live result.

## Evidence

- **The owner's screenshot:** `docs/archive/train_hub_pallets_20260927/owner_hub_pallets_20260927.png`.
  Save `build6_capacity_covered_pass3`, the hub SMROptInTrainHub6 (handle 6430), the Capacity
  Network Upgrade on. The panel shows every resource stocked (Metals 251/480; Basic 902/2,400,
  Advanced 700/1,920, Delicacies 1,318/3,840, Other 360/960). Several pallets show stacks and many
  beds draw empty. The owner had not looked for some time, so when it started is unknown.
- **The last good look:** spec §10 (grep `A fill-all made 2850 cubes`). At 150000 storage, 19
  request-backed resources at 150 each drew 2850 cubes with no clipping. That was before the
  storage went back to 240000 with the visual cap (`ca586d1`) and before the capacity upgrade
  (spec §4.10: the hub goes 240 → 480, through vanilla's resize).
- **The code:** `tools/devmods/train_hub/Code/20_TrainHub.lua`, from the comment block
  `Cargo on show` through `SMROptInTrainHubBase:GetCubePosRelative` (`own_pallets`,
  `GetTotalStorageColumns`, `hub_visual_storage`, `RecalculateDerivedMaxZ`). Its comments cite
  vanilla `MultiResourceDepot.lua` and `MultiResourceCubeVisuals.lua`; re-derive every line number
  with `grep -n` on the archived 1.1.1.405907 tree before you cite it.
- **Measurements of the pallets' spots:** `reports/drones_chain/L3_FLIGHTLOOK_ENGINE_20260923.md`
  (six pallets on r = 2492).
- Other records: `docs/agent/facts/INDEX.md`, `docs/agent/bugs/INDEX.md`.

Leads, not hypotheses to prove: the capacity upgrade's resize path and whether the cap still
applies after it; how columns are allotted per resource against the six pallets; the "stops at the
first nil position" behaviour the code comments cite.

## Scope and fences

**In:** the cause, and a fix confined to the hub's cargo-display code in `20_TrainHub.lua`. No
other brief is editing `20_TrainHub.lua` now.
**Out:** `10_TrainFloor.lua`, `40_TrainDistribution.lua`, `45_TrainDistributionUI.lua` (brief
10's), `50_TrainHubDispatchProbe.lua` (brief 11's), the model and asset, and storage amounts (the
owner's ruling). Report findings outside the fence without editing.

**The owner is in a sitting while you work.** Editing files on disk does not change the running
game, but do not ask the owner for anything mid-sitting; hand the orchestrator what you need.
**TestKit** (`B:\Dev\SMR\SMR-BugFixPack-TestKit`, shared): only **slots 1 and 2** are free
(capacity's, finished). Slot 3 is brief 11's probe, slots 4–6 are brief 10's, and Scratch is
read-only and in use: leave them. Keep `tools/devmods/train_hub/tests/distribution_slots_smoke.py`
passing, and update its capacity-slot assertion if you rebind 1 or 2. For sitting steps, follow
`tools/SMRTK.md` and the prompt-authoring skill's attended-sitting rules: slots, not console lines.

## Rules that apply

`CLAUDE.md`; `docs/agent/FIX_POLICY.md` (read its header before any code change; no new
persisted name); `docs/agent/WORKFLOW.md` for tests and the `items.lua`/`metadata.lua` pairing
if you add a file; the `doc-editing` skill before the report or spec edit;
`smr-bug-library` if you file anything. Run `python tools/doccheck.py` and `tools/parsecheck.py`
on the dev tree before committing. Commit with a pathspec.

Keep a live todo list from before your first write: one item per commit-and-verify unit, one in
progress at a time.

## Stops (report instead of continuing)

1. The cause is in vanilla's cube code in a way that only a body copy could fix.
2. The fix needs a change to storage amounts, the model, or any file outside the fence.
3. A reproduction needs a live read you cannot get at the desk. Write the slot and sitting steps
   instead, and stop there.

## Claim limits

Do not write "fixed" for a desk result. Write "desk-reproduced and repaired; live look owed".
Do not claim the look matches the owner's intent: that is the owner's judgement in the sitting.

## Close-out

Record the executed model from your transcript. Do not delete or move this brief: the orchestrator
owns its lifecycle.
