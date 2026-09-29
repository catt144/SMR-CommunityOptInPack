# TRAIN ORCHESTRATOR — the train logistics project's standing lead

> ⛔ **PURGE WHEN THE TRAINS PROJECT IS COMPLETE AND TESTED** (owner, 2026-09-18). Complete
> means every train module the owner keeps is built and has passed its ship test (`FIX_POLICY`
> §8: both configurations, both toggle directions), or the owner has parked or killed the rest, and the rail shaft's F vs G is ruled with any module
> it gets briefed or shipped.
> Then delete the whole `Train_Hub_Project/` folder and its row in `docs/agent/prompts/README.md`
> in one commit.

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/00_TRAIN_ORCHESTRATOR.md` in a fresh session rooted at
`B:\Dev\SMR\SMR-OptInPack`. Re-runnable for as long as the project lives.

## Authority

The owner, 2026-09-18: this session is the project's **orchestrator**. Build work goes to other
agents through briefs; the orchestrator holds the big picture. The trains are Module A
(per-resource station import/export) and Module B (the train hub). The owner, 2026-09-28: a simple
change the owner asks for, the orchestrator may make itself or give to a subagent; **a big change
is delegated to another agent through a brief.** The owner, 2026-09-29: **the rail shaft project
is the orchestrator's too**, since it touches the hub; its live handoff is this folder's
`RAIL_SHAFT_PROTOTYPE_high.md`. Plan hub and shaft together: check each brief on either side
against the other before it fires.

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
   - **WHERE THE PROJECT STANDS, orchestrator close-out 2026-09-29** (Opus 5.5 `claude-opus-5-5`).
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
     **Next, in order:**
     1. **Brief `22` (hub storage fixes)**, built. Check its handback once, have the
        owner do the Mod Editor save for slot 4 (`cargo_upgrade_smoke.py --require-generated`),
        Brief `23` (OI-27's drone map guard), fired by the owner.
        **Owner, 2026-09-29:** the hub is nearly done; `SMR_RailShaftDev` stays enabled; the
        crossing is built next, `22`'s and `23`'s smokes and the hub's remaining minor tests fold
        into the crossing's sittings, and one full battery runs at the end. Brief `24` (the
        crossing's shape investigation) comes before any crossing build.
     2. **The audit**, below; then **"remove its dev tags"**, still undefined. The orchestrator's
        guess, not yet answered by the owner: moving the hub out of `SMR_TrainHubDev_20260918` into
        the shipping Opt-In Pack as modules. The recommendation given was to audit the dev layout
        first, then brief the move. The owner picks the audit's model. Then the final full battery
        on the shipping layout.
     **Owner questions still open:** whether auto-fill stays; the hub-economy candidate (OI-19,
     spec grep `hub's economy becomes an upgrade`); accepting the look (`Parked/TRAIN_HUB_LOOK_high.md`).
     **Housekeeping, owed:** archive the closed sitting logs with a receipt, the game being closed.
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
