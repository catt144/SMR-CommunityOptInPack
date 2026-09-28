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
   - **WHERE THE PROJECT STANDS, orchestrator close-out 2026-09-28** (Opus 5.5 `claude-opus-5-5`).
     **How sittings run** (owner, 2026-09-26: *"we are going to do each sitting together and you
     will relay a message to them"*): the orchestrator guides the owner through a build's attended
     smoke from the build's own predictions, reads the log on "flushed" (re-read the file: the owner
     keeps playing after a flush), records the result, archives the closed log with a receipt line,
     and relays fixes. A build session on another model family (GPT-6 via Codex) cannot be messaged:
     hand the owner paste-ready text, and say which earlier message it replaces. Console lines are
     acceptable where no slot fits (owner, 2026-09-27).
     **Sittings are stream-first** (owner, 2026-09-28): TestKit slot 6 streams every train and
     station change to the log, on/off, and must be re-pressed after an autosave. Write steps as
     "stream on, play, flushed" and read units from the stream; do not have the owner select them.
     Other slots: Scratch balances every non-hub station to its row target, 1 empties them, 2 fills
     a selected station's Metals, 3 is brief 13's bay read (TestKit `a4b122b`), 4-5 are brief 10's.
     The fixture is **`build6_capacity_covered_pass3`** (a Drone Hub and Metals depot beside 2007).
     Scratch, then half a sol at top speed, reliably leaves train 2000001844 empty and parked on the hub.
     **Bay cut (ruling 10, 2026-09-28).** Briefs 13-15 are deleted: the bay's first sitting misplaced
     spawns, brief 15's gated rerun never deployed an extra, and the owner cut the extras to an
     archive and asked for a Train Cargo Upgrade (+100% cargo, +25% speed, 40 Metals + 20 Polymers;
     spec §4.10). The capacity salvage/rebuild change is merged (`7dcef3e`). Brief `16` archives and
     cuts the extras and builds the upgrade; its sitting is next. Archive the 2026-09-28 sitting logs (`14.27.05` and
     brief 15's run) with a receipt once the owner has closed the game. The owner's frame-flash
     sighting (spec §4.10, grep `flashes unpainted`) is recorded, not briefed.
     Eight game logs 2026-09-28 12.06.47 to 13.25.51 are unread; ask the owner what they were.
     **Where things stand:**
     - 5d (brief `10`, live): stranded-cargo repair PASSED live, and ruling 6's hub-first dump was
       seen on 2000001844 (cargo confirmed Metals). **Held:** its chained Export/Import legs, until
       the bay (`13`) has passed its smoke (ruling 7's sequencing).
     - Stations do not spoil food, and the hub does (ruling 8, live PASS). A minimum shipment is
       held unless covered stations' drone demand makes trips too frequent.
     - Dispatch is a train bay (ruling 9). The probes proved the reassignment holds and that a
       train stored and redeployed at the hub departs and serves its line. **Open:** whether the
       spawn sits exactly on the arm's siding (the owner saw it "off center").
     - **§4.9, whether the hub places the trains it builds, is not authorised.** Ruling 9 may
       answer it (a new train goes into the bay and deploys by need). This was said to the owner
       but not ruled; ask before treating it as settled.
     **Pending proposals for the owner, when they have room:**
     - Two capacity findings, neither briefed (`reports/TRAIN_HUB_CAPACITY_20260926.md`): drones
       will not build an upgrade from a station's own storage, and a salvaged hub's ruins wait for
       outside drones, so its bonus can stay on indefinitely. Both are fix-or-describe.
     - doccheck passed `README.md` collapsed onto one line (`7d7d0c2`, repaired in `04513e7`). It
       was offered to the owner as a tooling fix for an agent; no decision yet.
     - The owner's heated-track candidate (spec §10, grep `a heated`): not briefed, not a ruling.
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
   - **The audit sweep, only when the owner says builds 3, 4 and 5 are done** (owner,
     2026-09-19; the owner changes the model themselves). Treat every build report as a claim and
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
