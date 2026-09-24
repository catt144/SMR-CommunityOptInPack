# TRAIN ORCHESTRATOR — the train logistics project's standing lead

> ⛔ **PURGE WHEN THE TRAINS PROJECT IS COMPLETE AND TESTED** (owner, 2026-09-18). Complete
> means every train module the owner keeps is built and has passed its ship test (`FIX_POLICY`
> §8: both configurations, both toggle directions), or the owner has parked or killed the rest.
> Then delete the whole `Train_Hub_Project/` folder and its row in `docs/agent/prompts/README.md`
> in one commit.

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/00_TRAIN_ORCHESTRATOR.md` in a fresh session rooted at
`B:\Dev\SMR\SMR-OptInPack`. Re-runnable for as long as the project lives.

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
  steps are in `B:\Dev\SMR\SMR-Assets\trainhub\blender\README.md`.

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
     sitting help first. Do not start the audit or assume it is due.
   - **WHERE THE PROJECT STANDS, close of the 2026-09-24 orchestrator session.** The fire order is
     this folder's [`README.md`](README.md) and the drones chain's own
     [`03_Drones/README.md`](03_Drones/README.md) — keep both current; they are what the owner reads
     to pick the next thing. The look pass is DONE and accepted (brief `01` parked, body paint kept,
     restore point 6); spec §9 holds every step, its measurements and the restore tags, and `05` is
     live for its last step alone, the whole-hub GPU cost reading that is still `<<PENDING-RUN>>`.
     The drones are built: chain links 1-4 are consumed, the hub half landed in `b556035` with the
     one persisted name `SMROptIn_track_work` inventoried, and **link 5's attended smoke is in
     flight and paused on a save defect another agent is fixing**; link 6's QA is last and the owner
     runs it on a different model. `04` (build 5, the hub builds track) stays held until that smoke
     is recorded. The owner's open asks live on [`docs/PLAYTEST_CHECKLIST.md`](../../../PLAYTEST_CHECKLIST.md)
     — read it there rather than trusting a list here.
   - **The next design, not authorised: the distribution centre, spec §4.8** (owner, 2026-09-24).
     Read §4.8 and §4.9 before briefing anything in this area; they carry the mechanism (baseline
     numbers are the drones' view, a transient claim during the train's evaluation is the trains'),
     the decisions already taken (per resource not per station, state on the hub, controls in the
     station card's existing rows, claims kept out of saves), and the three unproven things its
     console prototype settles in one sitting.
   - **Live, fire when the owner wants an agent spent:** `02_TRAIN_HUB_LOADERRORS_low.md`, two errors
     the owner found in their session log on the dev hub's load path.
   - **The geometry oracle ran the night of 2026-09-19** (`GEOMETRY_ORACLE_high.md`; its report is
     `docs/agent/reports/GEOMETRY_ORACLE_20260919.md`, the instrument
     `B:\Dev\SMR\SMR-Assets\_shared\geometry\hub_oracle.py`, its measured rules
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
     (`SetScale`, alternating lines, a tunnel hood, resizing the dome): every one was generated
     downstream of the disputed figure. **The longer stub is not one of them**: the owner measured
     the stub at one hex on 2026-09-20 and directed one more (spec §9), which moves the connectors
     to radius 5 on the owner's own measurement. The oracle stays the check instrument for
     spot changes, but its `--train-length-m` default inherits the doubt;
   - **The hub's ship size** (OI-18, and spec §9): `upload_preflight.py` admits no asset file types
     at all. ⭐ MEASURED 2026-09-21, the bar fell on its own: the concept maps are 2048 where the old
     ones were 4096, and the dev mod's compiled textures are **14 MB, not 44** (three dead 4096 maps
     were deleted with them unreferenced). The glass and reactor will add a little. MEASURED 2026-09-20: **that 5 MB
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
     `B:\Dev\SMR\SMR-Assets\trainhub\blender\README.md`. Spec §9 records the result and what was
     not checked (§5 of the sitting report);
   - OI-18 and OI-19 on the owner's list;
   - **the movement work is FINISHED** (owner, 2026-09-21, restated 2026-09-21): centreline entry
     and mirrored exit, the six-siding transition and rejoin, the exit slide and vanilla handoff,
     the cold-start power fix (working for a long time) and the 6 s dwell. It may reopen once, at the
     final pre-launch test, if the owner wants some moves slightly tweaked.
     `Parked/TRAIN_HUB_MOVE_high.md` is PARKED for that and is not fired before it; never treat it as a
     gate on anything. Do not re-derive a movement fault from an old report.
   - **Build 4** (`03_TRAIN_HUB_DRONES_high.md`) is unblocked but NOT next (owner, 2026-09-21): the
     hub look comes first, and the drone system (deploy, movement, retextured storage) is unbuilt
     beyond a few test drones. **Build 5**
     (`04_TRAIN_HUB_BUILDTRACK_high.md`) stays HELD until build 4's smoke is recorded. A brief still
     in the map has not finished.
   - **Loading policy and full queueing** are the owner's own next pass, deferred 2026-09-20.
   - **Speed is NOT the trains' problem (MEASURED 2026-09-20; spec §10).** A train and a shuttle
     cruise at the same units per game second, and the train's best samples beat the shuttle's.
     ⛔ **Never compare `move_speed` constants across unit types** — a shuttle is a `FlyingObject`
     with no `Movable` and no `GetSpeed`, so its constant feeds another system; reading the
     constants alone produced two wrong orchestrator tables that the owner's eye overturned. What
     costs a train time is stops, track path and braking, which is what Module B is for. The cold
     x1/3 fires **only in a cold wave**. Not measured: door-to-door trip time, the number a player
     feels;
   - **Candidate, the owner's (2026-09-20, thinking about it, not briefed): a heated track
     upgrade** — hub-connected track gets a heated bonus so a network keeps moving through a cold
     wave. Spec §10 holds the open questions. Decide after the movement prototype;
   - **the look pass RESUMED, staged** (`Parked/TRAIN_HUB_LOOK_high.md`, the briefs named above). Settled, with citations in
     spec §9: the SI glow map is a ONE-CHANNEL BC4 mask, so glow colour lives in the base colour;
     the hub's glow follows its working state and goes to **zero**, not dim, when it stops
     (`SetSIModulation` 200 / 0), ours to drive per siding later; glass CANNOT live in the hub's
     mesh (one material per node) and goes as a separate attached entity, the way every vanilla
     dome's glass does. Still owed: the resumed look, the owner's night look, the glass and
     reactor imports.
   - before the final build's full battery, brief a TestKit fix for the crossing witness
     (the hub report's §"Sitting result");
   - **The distribution centre (spec 4.8), the owner's design of 2026-09-24 — DESIGN ONLY, not
     authorised.** Per-resource export / import / balanced on every station, the hub as the sink,
     state on the hub, controls in the station card's existing resource rows. Place it AFTER the
     drones chain and build 5: it is Module A's A1+A2 and wants the hub's own mechanics finished
     first. **One exception worth jumping the queue:** its console-only prototype (no UI, two
     stations and the hub) settles the three unproven things at once — the transient claim path
     that has never run, whether drones respond to the baseline numbers, and the unmeasured
     `accept` half. Cheap, and everything else rests on it. Train construction at the hub is
     spec 4.9: the hub can already build trains; the work worth doing is having it PLACE them.
   - Module A phase A1, whose `accept` half needs a retest with a Metals consumer in drone
     range (§4.3);
   - routing 5d or 5c, once the owner has played the 5a network.
   - **"Follow the track" no longer binds on its own (owner, 2026-09-23).** The 2026-09-19 ruling
     -- *"never drone pathing, so it cannot cut across open ground"* -- is not by itself a reason to
     take the flight back from the engine: *"Not unless we have another reason to go back to our
     flight path, it would have to be that plus something else. Right now that reason is the only
     reason for our own flight path."* So engine mode stands and the drones cross open ground.
     Reachability moves to dispatch, which is the only thing still enforcing it.
   - **`OI-26` is PARKED (owner, 2026-09-23)** until the hub is built and running: *"Lets park
     that until we get everything else built and running thats alot of poking and proding for
     something that might basically be unnoticible under real conditions and i am leaning towards
     not worth changing its state"*. Engine mode ships as built meanwhile; the Wasp's 7 m ride on
     engine-flown legs is unchanged. Judge it under real play in link 5's smoke, not by staging a
     train. If it ever does read wrong, the choice is three-way, not two: accept it, take the
     flight back (scripted, the tag), or give the drone our own `FlyingDrone` subclass with a
     higher `hover_height` — which keeps the engine flying but ends "it is just a vanilla Wasp",
     the standing protection for a save loaded without the mod.
4. Brief each new build with the `prompt-authoring` skill. Record owner rulings in the brief and
   the spec the obeying agent reads, never only in chat.
5. **You own every brief's lifecycle** (owner, 2026-09-21). Once a fired brief's work is done,
   decide: **park it** in `Parked/` if it is worth keeping for possible touch-up work, or **delete
   it**. Move or delete its row in this folder's `README.md` in the same commit, and say which and
   why in the commit message. Build agents do not delete or move their own brief.

**Method (owner, 2026-09-20): quick and iterative, never "try to be perfect".** *"Right now we are
doing extremely heavy builds each pass and then having to rewrite all the steps, and then do another
heavy try-to-be-perfect build, and we just keep repeating every time we learn something new."* Brief
small: get the model done, the owner inspects it, a quick prototype of the actions, then dial in by
eye. No gate, battery or analysis run stands between the owner and a rough thing they can look at.

In live in-game sittings, give the owner about five steps at a time. **Testing depth** (owner,
2026-09-19): a design pass gets a smoke test only; the full prediction battery runs once, on the
final build (spec §10). Brief build agents to write their sitting scripts that way. The game
cannot turn autosave off: after one, the owner re-presses the armed slot.
