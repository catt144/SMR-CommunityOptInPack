# TRAIN ORCHESTRATOR — the train logistics project's standing lead

> ⛔ **PURGE WHEN THE TRAINS PROJECT IS COMPLETE AND TESTED** (owner, 2026-09-18). Complete
> means every train module the owner keeps is built and has passed its ship test (`FIX_POLICY`
> §8: both configurations, both toggle directions), or the owner has parked or killed the rest; the Elevator Station
> (spec §11) is one of those modules.
> Then delete the whole `Train_Hub_Project/` folder and its row in `docs/agent/prompts/README.md`
> in one commit.

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/00_TRAIN_ORCHESTRATOR.md` in a fresh session rooted at
`B:\Dev\SMR\SMR-OptInPack`. Re-runnable for as long as the project lives.

## Authority

The owner, 2026-09-18: this session is the project's **orchestrator**. Build work goes to other
agents through briefs; the orchestrator holds the big picture. The trains are Module A
(per-resource station import/export) and Module B (the train hub). The owner, 2026-09-28: a simple
change the owner asks for, the orchestrator may make itself or give to a subagent; **a big change
is delegated to another agent through a brief.** The owner, 2026-09-29: **the crossing between the
surface and the underground is the orchestrator's too**, since it touches the hub. It is now the
Elevator Station (spec §11); the rail shaft's handoff is `Parked/RAIL_SHAFT_PROTOTYPE_high.md`.
Plan the hub and the crossing together: check each brief on either side against the other
before it fires.

## Read first

- The spec, `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`. §4.7 and §4.8 hold the
  distribution and dispatch rulings (4.8 numbers them, 1 to 9, and carries the save-boundary ladder).
  §4.9 is train construction, §4.10 capacity, §6 the options and the owner's routing direction
  (OPTION 5), §7.2 the measured results, §9 the asset and ship size, §10 the hub prototype and its
  standing rulings. Read the relevant sections before briefing anything in their area.
- The fire order: this folder's [`README.md`](README.md). The owner's open asks:
  [`docs/PLAYTEST_CHECKLIST.md`](../../../PLAYTEST_CHECKLIST.md).

## Each run

1. `git log`, `git status`, `git pull`. Find what build agents have committed or reported since
   the last orchestrator commit that touched the spec.
2. Treat each report as a claim. Confirm each result against its log and commits with one check
   before believing it. **Take the cheap direct measurement before anything rests on a derived
   one** (owner, 2026-09-20): in this game, a superimposed build cursor shows the 10 m hex grid.
   A 41.5 m train length read with `GetEntityBBox()` on an assembly with no mesh of its own cost a
   gated build and hours of redesign (`GEOMETRY_ORACLE_20260919.md` §13). When an owner
   observation disagrees with an agent-derived figure, the observation governs.
3. Fold confirmed results into the spec, then propose the next step to the owner. The current
   order:
   - **On launch, stand by** (owner, 2026-09-19). The owner may bring design questions, rulings or
     sitting help first. Do not start the audit or assume it is due.
   - **WHERE THE PROJECT STANDS, orchestrator close-outs 2026-09-29 and 2026-09-30** (09-29: Opus 5.5
     `claude-opus-5-5`; 09-29 evening to 09-30: Fable 5.1 `claude-fable-5-1`, switched by the owner
     mid-session). The 2026-09-30 block is inside item 1 below.
     All the sittings from the 2026-09-28 order have passed, and their briefs are deleted: `21`
     (Power, once per colony, one shared state, salvage changes nothing; spec §4.10), `10` (chained
     legs; §4.8 ruling 10) and `17` (reactor flash, no flash at any speed). New rulings are in
     spec §4.10: all hub upgrades are one colony purchase with one shared switch, and the owner's
     **pre-audit fix list** (grep `Owner's fix list before the audit`).
     **How sittings run** (owner, 2026-09-26): the orchestrator guides the owner through a build's
     attended smoke from the build's own predictions, reads the log on "flushed" (re-read the file:
     the owner keeps playing after a flush), records the result in the brief, and folds it into
     the spec when the brief passes. A Codex build session cannot be messaged: hand the owner
     paste-ready text. Console lines are acceptable where no slot fits (owner, 2026-09-27); the
     console read is pasted into the TestKit **command box**, not a slot. Name each slot's function
     beside its number, and call hubs by role, never by number (owner, 2026-09-28). Slot 6 streams
     trains with `effective_speed` (TestKit `4a31982`); an autosave disarms it.
     **WHERE THE PROJECT STANDS, orchestrator close-out 2026-10-01** (Fable 5.1 `claude-fable-5-1`;
     the build ran as an Opus 5.5 subagent). **Brief `27` is done:** the Elevator Depot pair is
     wired in the dev mod and its attended sitting passed on the final build (report
     `reports/ELEVATOR_DEPOT_WIRING_20261001.md`). Rulings taken that day are in spec §11: the surface
     half owns the rows, the underground shows them read-only with a surface-pointing infotip; rows
     take the hub's station shape with a target slider; one word for the pair on both panels
     (Import = goes down, Export = comes up); Balanced cut, unset rows Import; Drone Access on both
     halves in vanilla's filled on/off look; the hub reads the depot's rows and never writes one
     (`c54dfeb`). Open: OI-37 (one-pair limit and survivor rule), OI-38 (unrun sitting steps); the
     `SMR_TrainHubDev` editor save and the depot template text are carried into `28`; the hub's own
     `fit_title` carries the floored-ceiling fault the depot fixed at `1122115` (report §"long title")
     and belongs on the hub's next brief; four persisted names (`SMROptIn_depot_rows`, `_drones`,
     `_cabin`, `_targets`) go into FIX_POLICY's inventory when the depot ships.
     **Next, in order:**
     1. **Brief `22` (hub storage fixes)**, built. Check its handback once, have the
        owner do the Mod Editor save for slot 4 (`cargo_upgrade_smoke.py --require-generated`),
        **Owner, 2026-09-29:** the hub is nearly done; the crossing is built next; `22`'s smoke
        and the hub's remaining minor tests fold into the crossing's sittings, and one full
        battery runs at the end. The crossing is the **Elevator Station** (spec §11; the shape
        investigation behind it is `reports/CROSSING_SHAPE_20260929.md`). **Design before
        wiring** (owner): brief `25` (the look, placeable for visual sign-off), then a wiring
        brief (the shared store, the elevator range rule, the underground twin). The rail shaft
        and brief `23` are parked. `SMR_RailShaftDev` and the 09-18 `SMR_TrainHubPrototype` junctions were removed from
        the game's Mods folder on 2026-09-30 (owner: clean up unused mods); the repo folders
        stay. Do not load the old shaft save with the hub.
        **2026-09-30, where it stands:** the crossing is the **Elevator Depot** (a 75 % space
        elevator; the train drives into a portal between the pads and down under it; spec §11 and
        `reports/ELEVATOR_DEPOT_LOOK_20260929.md` §7 hold the owner's picture). Brief `25`'s
        portal is imported and **HELD for another design pass** (owner): good enough to test, not
        complete. The game moved to hotfix build **25579348** (owner: content unchanged). The
        combined sitting is next, guided by the orchestrator: (1) the owner's Mod Editor save of
        the train hub dev mod, which brief `22`'s
        `tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated` still fails
        without; (2) the depot's surface look, cabin and sound on a fresh placement; (3) a vanilla
        train in, down and out (slot 6 streams); (4) underground `Measure()`, `Report()` and the
        rope at the lowest pitch; (5) brief `22`'s five smoke steps
        (`reports/TRAIN_HUB_STORAGE_20260929.md`). Then the wiring brief, then the next design
        pass (deferred: the core's bare ground and frame, plus what the sitting shows).
        **Sitting 2026-09-30 done** (`reports/ELEVATOR_DEPOT_LOOK_20260930.md`, "Sitting"): look,
        cabin, sound, rope and trains PASS as a test model; brief `22`'s smoke NOT RUN (owner):
        its `SMR_TrainHubDev` Mod Editor save and its five steps fold into the **next design
        pass's** editor-and-import session. The design pass is **brief `26`** (eight items, the owner's words), fired by the owner;
        the orchestrator guides its sitting, which ends with brief `22`'s five steps.
        **2026-10-01: both PASSED live** (brief 26's design accepted until the paint pass; brief
        22's five steps): 22 and 26 deleted, 25 parked; spec §4.10 and §11 hold it. Brief `28`, the depot's paint
        pass, may run beside `27`; its Mod Editor import waits for `27`. **Next: brief
        `27`, the wiring**, authored 2026-10-01 for the owner to fire (passengers passed live on
        vanilla's elevator, no code; spec §11). The hub upgrade texts are rewritten at `6c53b46`;
        the owner's next `SMR_TrainHubDev` Mod Editor save makes them live (then
        `cargo_upgrade_smoke.py --require-generated` PASS).
     2. **The audit**, below; then **"remove its dev tags"**, still undefined. The orchestrator's
        guess, not yet answered by the owner: moving the hub out of `SMR_TrainHubDev_20260918` into
        the shipping Opt-In Pack as modules. The recommendation given was to audit the dev layout
        first, then brief the move. The owner picks the audit's model. Then the final full battery
        on the shipping layout.
     **Owner questions still open:** whether auto-fill stays; the hub-economy candidate (OI-19,
     spec grep `hub's economy becomes an upgrade`); accepting the look (`Parked/TRAIN_HUB_LOOK_high.md`).
     **Housekeeping, owed:** archive the closed sitting logs with a receipt, the game being closed.
     From 2026-10-01: `00.06.49` (sitting B's B1) and `11.16.04` (batch D); from 2026-09-30 also
     `21.43.16` (sitting B, stopped). From 2026-09-30: `12.23.04` (the depot sitting: look, train stream, underground Measure) and
     `11.47.37` (its first placement); the `13.xx` logs are brief 26's agent, ask.
     From 2026-09-28: `14.27.05`, `17.13.10`, `19.07.48`, `20.00.03`, `20.45.30`, `20.48.36`
     (ask which were sittings; `12.06.47` to `13.25.51` never read), `22.20.16` (brief 21's first
     sitting, already archived by `9bffa5c` under `docs/archive/power_upgrade_20260928/`) and
     `22.57.28`. From 2026-09-29: `12.03.53`, `12.55.28` (brief 21's reruns) and `13.36.00`
     (brief 10). The spawn-on-siding correction has not been seen live; watch the next hub spawn.
     Brief 10's old report predictions were written before ruling 10; treat any report's
     predictions from before 2026-09-28 as possibly stale.
   - **Standing constraints:**
     - **Movement is FINISHED** (owner, 2026-09-21). It may reopen once, at the final pre-launch
       test, if the owner wants moves tweaked; `Parked/TRAIN_HUB_MOVE_high.md` waits for that and
       is never a gate. Do not re-derive a movement fault from an old report.
     - **Loading policy and full queueing** are the owner's own later pass (deferred 2026-09-20).
     - **Speed is not the trains' problem**, and `move_speed` constants must never be compared
       across unit types (spec §10, grep `must not be compared across unit types`).
     - **Geometry:** the oracle `B:\Dev\SMR\SMR-Assets\_shared\geometry\hub_oracle.py` stays the
       check instrument for spot changes, but its `--train-length-m` default inherits the disputed
       41.5 m. Do not revive the options withdrawn with that figure (`GEOMETRY_ORACLE_20260919.md`
       §13 and the list at grep `SetScale`).
     - **The hub's ship size** is the owner's ruling (OI-18; spec §9, grep `OUR OWN GUARD`).
   - **The audit sweep, authorised to follow the sittings above** (owner, 2026-09-28; the owner
     changes the model themselves). Treat every build report as a claim and
     check it against its commits and logs. Cover:
     - the persisted-name inventory (ban 1);
     - `FIX_POLICY` §8's both-configuration ship test and the toggle test as §0 defines it for
       content, which the smokes do not cover;
     - spec §10 and the hub report agreeing with the code;
     - the settled 19 request-backed resources against the 21 nominal candidates;
     - that each fired brief and its map row were deleted at its lifecycle;
     - build 3's sitting-report §6 audit of how every mid-run ruling landed.
     Before the final build's full battery, brief a TestKit fix for the crossing witness
     (`TRAIN_HUB_BUILD_20260918.md`, grep `crossing witness cannot prove`).
4. Brief each new build with the `prompt-authoring` skill. Record owner rulings in the brief and
   the spec the obeying agent reads, never only in chat.
5. **You own every brief's lifecycle** (owner, 2026-09-21). Once a fired brief's work is done,
   decide: **park it** in `Parked/` if it is worth keeping for possible touch-up work, or **delete
   it**. Move or delete its row in this folder's `README.md` in the same commit, and say which and
   why in the commit message. Build agents do not delete or move their own brief.

**The orchestrator does not investigate or build** (owner, 2026-09-28, after a session spent its
cheap context on source reads, feasibility checks and merges while the sitting waited). Source
reads, feasibility questions, desk checks and merges go to a subagent; the orchestrator answers
the owner from what it already holds, and says "an agent will check" rather than checking. Keep
the orchestrator's own context under about 30%. The owner runs this session at **low effort on
purpose** (authoring and recording) and switches it to high only for a task they name; builds run
at high Opus or medium/high Fable/Astra. A subagent launched from here without a pinned effort
inherits low, which is below build tier: build through a brief the owner fires, not from here. When the owner is ready to play, the sitting comes
first and background work runs beside it, not before it.

**Method (owner, 2026-09-20): quick and iterative, never "try to be perfect".** *"Right now we are
doing extremely heavy builds each pass and then having to rewrite all the steps, and then do another
heavy try-to-be-perfect build, and we just keep repeating every time we learn something new."* Brief
small: get the model done, the owner inspects it, a quick prototype of the actions, then dial in by
eye. No gate, battery or analysis run stands between the owner and a rough thing they can look at.

In live in-game sittings, give the owner about five steps at a time. **Testing depth** (owner,
2026-09-19): a design pass gets a smoke test only; the full prediction battery runs once, on the
final build (spec §10). Brief build agents to write their sitting scripts that way. The game
cannot turn autosave off: after one, the owner re-presses the armed slot.
