# TRAIN ORCHESTRATOR — the train logistics project's standing lead

> ⛔ **PURGE WHEN THE TRAINS PROJECT IS COMPLETE AND TESTED** (owner, 2026-09-18). Complete
> means every train module the owner keeps is built and has passed its ship test (`FIX_POLICY`
> §8: both configurations, both toggle directions), or the owner has parked or killed the rest; the Elevator Depot
> (spec §11) is one of those modules.
> Then delete the whole `Train_Hub_Project/` folder and its row in `docs/agent/prompts/README.md`
> in one commit.

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/00_TRAIN_ORCHESTRATOR.md` in a fresh session rooted at
`B:\Dev\SMR\SMR-OptInPack`. Re-runnable for as long as the project lives.

## Authority

The owner, 2026-09-18: this session is the project's **orchestrator**. Build work goes to other
agents through briefs; the orchestrator holds the big picture. The trains are three
modules: station rows (Module A, per-resource import/export), the train hub (Module B) and the
Elevator Depot (spec §11). The owner, 2026-09-28: a simple
change the owner asks for, the orchestrator may make itself or give to a subagent; **a big change
is delegated to another agent through a brief.** The owner, 2026-09-29: **the crossing between the
surface and the underground is the orchestrator's too**, since it touches the hub. It is now the
Elevator Depot (spec §11); the rail shaft's handoff is `Parked/RAIL_SHAFT_PROTOTYPE_high.md`.
Plan the hub and the crossing together: check each brief on either side against the other
before it fires.

## Read first

- The spec, `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`. §4.7 and §4.8 hold the
  distribution and dispatch rulings (4.8 numbers them, 1 to 10, and carries the save-boundary ladder).
  §4.9 is train construction (record only: the hub builds no
  trains, owner 2026-09-28), §4.10 capacity, §6 the options and the owner's routing direction
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
   - **On launch: open with an overall status** (owner, 2026-10-01): run step 1, check the live
     brief's latest commits and the working tree once, then give the owner, briefly: where the
     project stands, what is live, what passed since the last close-out, and **what the owner needs
     to do next**, in order. Then stand by (owner, 2026-09-19): the owner may bring design
     questions, rulings or sitting help first.
   - **How sittings run** (owner, 2026-09-26): the orchestrator guides the owner through a build's
     attended smoke from the build's own predictions, reads the log on "flushed" (re-read the file:
     the owner keeps playing after a flush), records the result in the brief, and folds it into
     the spec when the brief passes. A Codex build session cannot be messaged: hand the owner
     paste-ready text. Console lines are acceptable where no slot fits (owner, 2026-09-27); the
     console read is pasted into the TestKit **command box**, not a slot. Name each slot's function
     beside its number, and call hubs by role, never by number (owner, 2026-09-28). Slot bindings change each
     sitting (`tools/SMRTK.md`): read the current `80_AgentSlots.lua` before naming a slot. An
     autosave disarms an armed watch; the owner re-presses it.
   - **WHERE THE PROJECT STANDS, orchestrator close-out 2026-10-02** (Opus 5.5
     `claude-opus-5-5`). Closed briefs are in this folder's
     `README.md`; their rulings are spec §4.7 and §11's last blocks. Passengers need no code: vanilla's elevator carries them, train to train.
     **Next, in order** (every remaining brief is authored; the owner tests and fires):
     1. **`33`, the crossing witness**: desk done (`c06349e`, report
        `TRAIN_CROSSING_WITNESS_20261002.md` at `0b8225b`); its attended check is owed. Guide it
        from that report's predictions, then close the brief.
     2. **`34`, the move into this mod**: checkpoint answered (OI-41, 2026-10-02; spec §10 grep
        `Brief 34's checkpoint`); preflight widened (`5aa529d`). The owner's veto on the player-text
        drafts is owed (`TRAIN_MOVE_CHECKPOINT_20261002.md` §"Player text drafts"). Code moves
        after 33 closes: both touch the hub's tests.
     2b. **`34b`, two owner fixes (2026-10-02)**: Export rows take only stock above a storage's
        Desired Amount (spec §4.8 grep `Export takes only the excess`), and auto-fill's train enters
        at the joining station, not the hub (grep `enters at the joining station`). Phase 1 (plan)
        may fire now; phase 2 lands after 33 and 34 close.
     3. **`35`, the final full battery**, after 33, 34 and 34b; it carries OI-38's up-leg read and
        auto-fill's watch (the train enters at the joining station). Its pass completes the project: purge this folder.
     **Sitting logs:** no further archiving is owed; the project is near its end (owner,
     2026-10-01).
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
     - **The hub's ship size** is the owner's ruling (spec §9, grep `OUR OWN GUARD`); OI-18's widened preflight
       landed at `5aa529d` (brief 34).
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
