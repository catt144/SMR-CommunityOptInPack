# Hub dispatch — can the hub choose which line a train serves?

**LIVE, investigation** (2026-09-27), for a fresh session. It runs alongside brief `10` (5d routing,
fixing stranded cargo), which owns the distribution files.

⚖️ **Owner, 2026-09-27 (spec §4.8 ruling 7):** the hub should be able to assign trains to its lines
by need. A quiet station gets topped up by an occasional train; a busy one is served by several. The
owner's sequencing: **settle whether dispatch is possible before 5d's remaining live legs**, so
chained routing is not tested twice under two dispatchers. This brief answers the question. It does
not build the dispatcher.

Read first:
- spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`: §4.8 (every ruling, including 6 and
  7), §4.9 (train construction at the hub), §5.2–§5.3 (the linear route model, and
  `Train:AssignToTrack`), §6 OPTION 5 (5c versus 5d), and §10 (the hub, its movement record and the
  finished-movement ruling);
- `docs/agent/reports/TRAIN_ROUTING_5D_20260927.md`.

## The question

**Can a train standing at the hub be put onto another of the hub's lines, and then serve that line
through vanilla's own loading and travel?** If yes: what is the smallest dispatcher that decides
which line gets which train by need, and what does it cost in patch exposure and save rung?

## What is already there — claims to confirm with one check each

- **The movement already crosses arms.** In `tools/devmods/train_hub/Code/20_TrainHub.lua`:
  - `TrainDepart` routes a train from its arrival arm (`station_arrival_track`) to the departure arm
    of the `departure_track` vanilla hands it;
  - `HubRouteTrain` turns it at `HubTurnPoint` and slides it out, or flips it on the same arm;
  - `TrainPassThrough` already calls `train:AssignToTrack(departure_track)` before moving.

  The owner accepted this movement (spec §10, finished 2026-09-21). Re-derive the lines with
  `grep -n`.
- **Vanilla's primitive:** `Train:AssignToTrack(track)` (archived 1.1.1.405907 `Units/Train.lua`,
  near `:220`) only moves the train between tracks' `assigned_vehicles`.
- **`Train:LoadTrain` rejects a source station that is not an end of `self.track`.** The hub is an
  end of every hub line, so a train reassigned while at the hub may pass that check. That is the
  lead, not a finding.
- **Where vanilla picks a train's next track**, and whether anything re-assigns it (`GotoStation`,
  `RebuildTrainRoutes`, route rebuilds on construction, save/load of `self.track`): find these.
  They decide whether a reassignment sticks.

## What to produce

1. **A feasibility answer with evidence:**
   - source reads with the build and line (from the archived tree, per `CLAUDE.md`);
   - a desk run on archived bodies where it helps;
   - if the desk cannot settle it, **one small in-game prototype**. Method: rough and in the game
     fast (owner, 2026-09-20). It is a throwaway: a console-driven or single-slot reassignment of one
     train at the hub to another hub line, and a check that it departs on that arm and serves it.
     Put its sitting steps for the orchestrator in your report: five steps at most, slots preferred,
     console acceptable (owner, 2026-09-27), from `build6_capacity_covered_pass3`.
2. **If feasible, a design sketch, not a build:**
   - **the need signal:** which line is short, and by how much (the distribution module's orders
     are the obvious input; read `40_TrainDistribution.lua`, do not edit it);
   - when a train at the hub is released to which line;
   - how many trains a line may hold;
   - what happens to chained lines that never touch the hub (they keep their own trains);
   - the interaction with brief 10's forwarding and with §4.9 (the hub placing trains it builds);
   - the save rung (§4.8's ladder) and the patch exposure;
   - what the owner would see and control.
3. **If not feasible, the wall:** the exact line that defeats it, and whether 5c (trains driving
   through hubs, §5.2's rewrite) is the only road.
4. **A report**, `docs/agent/reports/TRAIN_HUB_DISPATCH_<date>.md`, with the answer, the evidence
   (each claim with its measurement or source line), the sketch or the wall, and a cost the owner
   can weigh: what it would take to build, and what it would force re-testing in 5d. Spec §4.8 gets
   a one-line pointer. Hand back with the commit and a short relay the orchestrator can read in one
   pass.

## Start

`git log --oneline -5`, `git status`, `git pull --ff-only`. Authored on the commit that adds this
brief. Put the work in the todo tool before the first write, one item per commit-and-verify unit.
Brief `10` commits to this tree at the same time: `git pull --ff-only` before every commit, and
commit with a pathspec.

## Scope

**In:**
- reading anything;
- a new throwaway prototype file of your own under `tools/devmods/train_hub/Code/` (register it in
  `metadata.lua`; re-read that file immediately before each write, since brief 10 may touch it) or a
  console line;
- TestKit slots for your prototype;
- your report and spec §4.8's pointer.

**Out:**
- ⛔ **Editing** `20_TrainHub.lua`, `30_TrainHubDrones.lua`, `10_TrainFloor.lua`,
  `40_TrainDistribution.lua` or `45_TrainDistributionUI.lua`. Read them freely. Brief 10 owns the
  last three, and the movement is finished (spec §10). If feasibility needs a movement change,
  that is a finding to report.
- Building the dispatcher; the route model (5c); the shipping `Code/` tree; `FIX_POLICY` §8's ship
  test.

Report anything outside this fence without editing it.

## Stops

- The prototype needs an edit to a fenced file: report the change it needs, with the evidence.
- A reassigned train reaches a state vanilla cannot recover from (stuck, teleporting, or a lost
  train) in the prototype: stop, keep the log, report.

## Do not claim

- ⛔ Not "the hub can dispatch". Claim what was shown: source, desk or one prototype, on which arms,
  in which colony.
- ⛔ Not a cost as a measurement unless you measured it; an estimate is labelled as one.

## Lifecycle

A one-off. Done when the report is committed and handed back. The orchestrator then parks or deletes
this brief and moves its row in `README.md` in one commit (owner, 2026-09-21). Build agents do not
delete or move their own brief.
