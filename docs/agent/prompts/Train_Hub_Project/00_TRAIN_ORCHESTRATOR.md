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
agents through briefs; the orchestrator holds the big picture. The trains are Module A
(per-resource station import/export) and Module B (the train hub). The owner, 2026-09-28: a simple
change the owner asks for, the orchestrator may make itself or give to a subagent; **a big change
is delegated to another agent through a brief.**

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
   - **WHERE THE PROJECT STANDS, orchestrator close-out 2026-09-28 (evening)** (Opus 5.5
     `claude-opus-5-5`). Rulings of the day are in the spec: §4.8 ruling 10 (hub extras cut to
     `docs/archive/train_bay_extras_20260928/`; auto-fill and siding placement kept), §4.9 (the hub
     builds no trains), §4.10 (Train Cargo Upgrade; Power Upgrade; salvage off, no normal rebuild).
     **How sittings run** (owner, 2026-09-26): the orchestrator guides the owner through a build's
     attended smoke from the build's own predictions, reads the log on "flushed" (re-read the file:
     the owner keeps playing after a flush), records the result in the spec, archives the closed log
     with a receipt line, and relays fixes. A Codex build session cannot be messaged: hand the owner
     paste-ready text. Console lines are acceptable where no slot fits (owner, 2026-09-27).
     **Stream-first** (owner, 2026-09-28): TestKit slot 6 streams trains and stations and must be
     re-pressed after an autosave or load. **Name each slot's function beside its number** in every
     step (a sitting was lost to slot 2 pressed for slot 3). Slots at TestKit `e09efa0`: Scratch
     balances non-hub stations; 1 empties them; 2 is brief 17's reactor dust reference (2 s); 3 reads
     upgrades, train capacities and speed; 4 reads a selected station's distribution rows; 5 runs
     until a selected station's Metals reaches its slider; 6 streams. Fixture
     **`build6_capacity_covered_pass3`**; the owner also has a two-hub save (hubs 6430 and 6495).
     **Next, in order** (owner, 2026-09-28: *"get all our sittings done now and then fire the audit,
     remove its dev tags and then do our final full test"*):
     1. **Brief `21` (Power Upgrade) has handed back, unchecked**: `57ee0f7`, report
        `reports/TRAIN_HUB_POWER_UPGRADE_20260928.md`. Check it once, have the owner do the Mod
        Editor save (`cargo_upgrade_smoke.py --require-generated`), then run its combined
        cold-wave sitting (it supersedes briefs 19/20's, deleted).
     2. **Brief `10`'s chained Export/Import legs** plus one sol at top speed, on the fixture:
        slot 4 baselines on 6243, 2012, 2009 and the small station; Metals Export on 6243 and Import on
        the small station; slot 5; then the sol. Its report's "Initial sitting predictions" hold the
        predictions. No longer held: dispatch is vanilla since ruling 10.
     3. **Brief `17`'s reactor check** in the same boot: slot 2 on the hub, compare with the owner's
        flash; then change game speeds while watching. Delete `17` on the owner's acceptance.
     4. **The audit**, below; then **"remove its dev tags"**, which is not yet defined. Ask the
        owner whether it means moving the hub out of `SMR_TrainHubDev_20260918` into the shipping
        Opt-In Pack as modules, and brief it before the final full battery, which runs on the
        shipping layout.
     **Owner questions still open:** whether auto-fill stays (kept until answered; placement at the
     hub needs the siding correction either way); the hub-economy candidate (OI-19, spec grep
     `hub's economy becomes an upgrade`); accepting the look (`Parked/TRAIN_HUB_LOOK_high.md`).
     **Housekeeping:** archive the 2026-09-28 sitting logs with a receipt, the game being closed:
     `14.27.05` (bay sitting), brief 15's run, `17.13.10` (cargo upgrade PASS) and the evening
     cold-wave logs (`19.07.48`, `20.00.03`, `20.45.30`, `20.48.36`; ask the owner which were
     sittings). Logs `12.06.47` to `13.25.51` were never read; ask before treating any as a sitting.
     The spawn-on-siding correction has not been seen live; watch the next hub spawn.
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
