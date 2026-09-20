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
- The 2026-09-19 sitting, its measurements, source facts and the owner's rulings behind builds 3 to 5:
  `docs/agent/reports/TRAIN_HUB_SITTING_20260919.md`.
- The owner's asset: the shape was approved on 2026-09-18 and imported into the dev mod on
  2026-09-19, on the hex grid (`06b5a62`). Spec §9 holds the pipeline, the measured axis mapping,
  the owner's look direction and what only the game can answer. The Blender and Mod Editor
  steps are in `C:\Dev\SMR-Assets\trainhub\blender\README.md`.

## Each run

1. `git log`, `git status`, `git pull`. Find what build agents have committed or reported since
   the last orchestrator commit that touched the spec.
2. Treat each report as a claim. Confirm each result against its log and commits with one check
   before believing it.
   **Take the cheap direct measurement before anything rests on a derived one** (owner,
   2026-09-20). In this game that is a **superimposed build cursor, which makes the 10 m hex grid
   visible** — the owner sized a train that way in seconds. It cost a gated build, an owner
   checklist item and about six hours of costed redesign options to learn: all of it stood on a
   41.5 m train length from one `GetEntityBBox()` call on an entity with no mesh of its own
   (report §13). Distrust any dimension read off an entity whose `mesh_bbox` is null or that
   auto-attaches parts, and when an owner observation disagrees with an agent-derived figure, the
   observation governs.
3. Fold confirmed results into the spec, then propose the next step to the owner. The current
   order:
   - **On launch, stand by** (owner, 2026-09-19). The owner may bring design questions, rulings or
     sitting help first. Do not start the audit or assume it is due. Orient from
     `docs/agent/reports/TRAIN_HUB_SITTING_20260919.md` §6-7, then from the three live holds below;
   - **The geometry oracle ran the night of 2026-09-19** (`GEOMETRY_ORACLE_high.md`; its report is
     `docs/agent/reports/GEOMETRY_ORACLE_20260919.md`, the instrument
     `C:\Dev\SMR-Assets\_shared\geometry\hub_oracle.py`, its measured rules
     `_shared/IMPORTER_FACTS.md`, its game reads TestKit slot 6 `geometry_reads`). Read it before
     any hub geometry or train work: it found `hub_connector_directions` wrong for indices 1-4
     against the imported body, which puts four of six lines' train spots on another line and past
     `Station.lua:1105`'s 50 m teleport. Its run B (report §10) measured a whole train at 41.5 m by
     4.16 m, four times the length and twice the width every earlier clearance figure assumed, and
     found that a track element's `Enter1`/`Enter2` side depends on the track's angle and the
     train's direction of travel. The paths run (report §11, 2026-09-20) folded that into the
     oracle and re-ran it under the corrected table: §11's numbered list is what 3b still has to
     solve and it lifted §10's "not to be used" from the three path verdicts. ⛔ **But its item 6
     (a stopped train is longer than a half-line) rested on a train length the owner has since
     DISPUTED** (report §13, owner 2026-09-20): a hex-grid measurement gives about two hexes
     (~20 m) against §10's 41.5 m, and `TrainCCP3` has no mesh of its own, so the `GetEntityBBox`
     read was taken on an assembly. R-TRAIN is disputed, §12's gate verdict is set aside and OI-22
     was withdrawn from the owner's list. **The resolution: park position is a tunable in our own
     Lua**, tuned by eye and judged in the smoke — no asset change. 3b is re-scoped on that, is
     live, and owes the clean length measurement. ⛔ Do not revive the withdrawn options
     (`SetScale`, alternating lines, a tunnel hood, `FOOTPRINT_R = 5`, resizing the dome): every
     one was generated downstream of the disputed figure. The oracle stays the check instrument for
     spot changes, but its `--train-length-m` default inherits the doubt;
   - **⛔ `C:\Dev\SMR-TrainHubAssets` is a STALE COPY, not a junction** — make it one before any
     Mod Editor re-import, or the editor writes into a dead folder. Steps in
     `C:\Dev\SMR-Assets\README.md` §"The old path";
   - **The hub's ship size** (OI-18, and spec §9): `upload_preflight.py` admits no asset file types
     at all, and the hub is 44 MB against a 5 MB `PACK_MAX_BYTES`. MEASURED 2026-09-20: **that 5 MB
     is our own constant, not a platform limit** — vanilla buildings use 2048 maps where ours are
     4096, packs are zstd-compressed and our three maps compress to about 3.3 MB, and Steam carries
     Surviving Mars mods at 103 MB. Spec §9 holds the decode and what is still undetermined. The
     owner was researching this on 2026-09-20; it is their ruling, not an agent's;
   - **the audit sweep, only when the owner says builds 3, 4 and 5 are done** (owner, 2026-09-19;
     the owner changes the model themselves): treat every build
     report as a claim and check it against its commits and logs. Cover: the persisted-name
     inventory (ban 1: the repair list's name and kind field are the new ones); `FIX_POLICY` §8's
     both-configuration ship test and the toggle test as §0 defines it for content, which the
     smokes do not cover; the
     spec §10 and hub report agreeing with the code; the settled 19 request-backed resources
     against 21 nominal candidates; and that each fired brief and its map row were deleted at its
     lifecycle; build 3's sitting-report §6 audit records how every mid-run ruling landed;
   - the Blender texture pass is done (owner, 2026-09-19: Tripo dropped); its brief is retired.
     The owner's GFXMaterial item and re-import ride build 3's footprint fix, from the steps in
     `C:\Dev\SMR-Assets\trainhub\blender\README.md`. Spec §9 records the result and what was
     not checked (§5 of the sitting report);
   - OI-18 and OI-19 on the owner's list;
   - builds 3b, 4 and 5 (`TRAIN_HUB_TRAINS_high.md`, `TRAIN_HUB_REPAIR_high.md`,
     `TRAIN_HUB_BUILDTRACK_high.md`; briefs written 2026-09-19): the owner fires them in order, each
     after the previous smoke is recorded, and plays each smoke with you when asked. A brief still
     in the map has not finished. Build 3's footprint/texture re-import and smoke are recorded and
     its one-off brief is deleted. **Build 3b was re-scoped and FIRED on 2026-09-20 and is working
     in this tree — it owns `tools/devmods/train_hub/Code/20_TrainHub.lua`, so do not touch that
     file and commit with a pathspec.** The owner plays its smoke on 2026-09-21 and will bring the
     results; read them as a claim like any other;
   - the look pass, unbriefed: a floor plate modelled on the vanilla station's, the stub narrowed
     to vanilla's profile with a red centre strip, the glass, and the night lighting — all in spec
     §9, all waiting on 3b's lane number and one Mod Editor re-import (so: the junction first).
     Texture resolution rides it, because of the ship-size bar above;
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
