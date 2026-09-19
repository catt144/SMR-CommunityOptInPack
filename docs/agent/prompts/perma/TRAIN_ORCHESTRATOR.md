# TRAIN ORCHESTRATOR — the train logistics project's standing lead

> ⛔ **PURGE WHEN THE TRAINS PROJECT IS COMPLETE AND TESTED** (owner, 2026-09-18). Complete
> means every train module the owner keeps is built and has passed its ship test (`FIX_POLICY`
> §8: both configurations, both toggle directions), or the owner has parked or killed the rest.
> Then delete this file and its row in `docs/agent/prompts/README.md` in one commit. Unlike the
> other perma prompts, it is temporary.

**Fire with:** `task docs/agent/prompts/perma/TRAIN_ORCHESTRATOR.md` in a fresh session rooted at
`C:\Dev\SMR-OptInPack`. Re-runnable for as long as the project lives.

## Authority

The owner, 2026-09-18: this session is the project's **orchestrator**. Build work goes to other
agents through briefs; the orchestrator holds the big picture. It does not build modules itself.
The trains are Module A (per-resource station import/export) and Module B (the train hub).

## Read first

- The spec, `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`: §7.2 holds the measured
  results, §6 the options and the owner's direction (the routing target in OPTION 5), and §10 the
  prototype.
- The live briefs in `docs/agent/prompts/README.md`. The hub prototype returned a **qualified
  GO** (owner, 2026-09-18). The real hub build (fired and retired) committed its dev mod
  and design record (`886926b`, `d9be297`, `docs/agent/reports/TRAIN_HUB_BUILD_20260918.md`).
  Its smoke test was played with the owner on 2026-09-19 (the report's §"Sitting result").
  Its owner decisions are OI-18 and OI-19 in `docs/PLAYTEST_CHECKLIST.md`; the radius was ruled
  in the sitting (spec §10).
- The owner's asset: the shape was approved on 2026-09-18 and imported into the dev mod on
  2026-09-19, on the hex grid (`06b5a62`). Spec §9 holds the pipeline, the measured axis mapping,
  the owner's look direction and what only the game can answer. The Blender and Mod Editor
  steps are in `C:\Dev\SMR-TrainHubAssets\blender\README.md`.

## Each run

1. `git log`, `git status`, `git pull`. Find what build agents have committed or reported since
   the last orchestrator commit that touched the spec.
2. Treat each report as a claim. Confirm each result against its log and commits with one check
   before believing it.
3. Fold confirmed results into the spec, then propose the next step to the owner. The current
   order:
   - **start here: the Blender texture pass** (owner, 2026-09-19: the Tripo pass was tried and
     dropped). Its worker has returned (the brief is retired; outputs in
     `C:\Dev\SMR-TrainHubAssets\blender\`). Treat its report as a claim: check the previews against
     the owner's look direction and the geometry proof against the FBX. The owner's
     GFXMaterial item and re-import wait for build 3's footprint fix so that one re-import carries
     both, from the steps in that folder's `README.md`. Fold the result into spec §9, replacing its
     Tripo route paragraph;
   - OI-18 and OI-19 on the owner's list;
   - fire `TRAIN_HUB_BUILD3_high.md` (the footprint the game reads as 85 hexes, the overlay, drone
     replacement from prefabs, the track height; it also takes over build 2's uncommitted work) and
     play its smoke test with the owner. The footprint fix and the texture ride one Mod Editor
     re-import;
   - fire `TRAIN_HUB_REPAIR_high.md` (build 4, the repair train; owner, 2026-09-19) once build 3's
     smoke is recorded, and play its smoke with the owner;
   - fire `TRAIN_HUB_BUILDTRACK_high.md` (build 5, the hub builds track; owner, 2026-09-19) once
     build 4's smoke is recorded, and play its smoke with the owner;
   - **audit sweep of builds 3, 4 and 5** (owner, 2026-09-19), once all three smokes are recorded
     and when the owner asks for it (they will change the model themselves): treat every build
     report as a claim and check it against its commits and logs. Cover: the persisted-name
     inventory (ban 1: the repair list's name and kind field are the new ones); `FIX_POLICY` §8's
     both-configuration and both-toggle-direction ship test, which the smokes do not cover; the
     spec §10 and hub report agreeing with the code; the `resource_types` 19 against 21 question;
     and that each fired brief and its map row were deleted at its lifecycle;
   - before the final build's full battery, brief a TestKit fix for the crossing witness
     (the hub report's §"Sitting result");
   - Module A phase A1, whose `accept` half needs a retest with a Metals consumer in drone
     range (§4.3);
   - routing 5d or 5c, once the owner has played the 5a network.
4. Brief each new build with the `prompt-authoring` skill. Record owner rulings in the brief and
   the spec the obeying agent reads, never only in chat.

In live in-game sittings, give the owner about five steps at a time. **Testing depth** (owner,
2026-09-19): a design pass gets a smoke test only; the full prediction battery runs once, on the
final build (spec §10). Brief build agents to write their sitting scripts that way. The game
cannot turn autosave off: after one, the owner re-presses the armed slot.
