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
   - **start here: the Tripo texture pass** (owner, 2026-09-19, on their Tripo trial). The
     owner textures `C:\Dev\SMR-TrainHubAssets\blender\export\SMROptInTrainHub6_body_for_tripo.glb`
     in Tripo Studio. That's texture only, with no remesh, using the prompt in spec §9. They export
     it to `C:\Dev\SMR-TrainHubAssets\tripo_textured\`. Check that folder first. Then, in Blender,
     give the export mesh `SMROptInTrainHub6` a UV map, bake Tripo's maps onto it
     (selected-to-active, so Tripo's geometry never ships), write TGA maps, and walk the owner
     through one GFXMaterial item plus a re-import. Judge the result against the owner's look
     direction. If it is muddy or inconsistent, fall back to our own procedural textures (spec
     §9, "The look");
   - OI-18 and OI-19 on the owner's list;
   - fire `TRAIN_HUB_BUILD2_high.md` (the radius and drone-section rulings, and the swap to the
     imported asset) and play its smoke test with the owner;
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
