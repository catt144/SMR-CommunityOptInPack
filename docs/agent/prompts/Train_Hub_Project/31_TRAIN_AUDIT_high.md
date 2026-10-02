# 31 — The train project's audit sweep (investigation, report only)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/31_TRAIN_AUDIT_high.md` in a fresh session
rooted at `B:\Dev\SMR\SMR-OptInPack`. Reasoning: high (cross-checking many claims against code,
commits and logs). The owner picks the model (owner, 2026-09-28).

## Authority and outcome

The owner authorised this sweep on 2026-09-28, to run before the train project's code moves out of
its dev mods into this mod (spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §11, grep
`Remove its dev tags`). Every build report is a **claim**: check each against its commits and logs.
The outcome is one report, `docs/agent/reports/TRAIN_AUDIT_<date>.md`, that the move brief (`34`)
and the final battery (`35`) read: what holds, what does not, and what each later brief must carry.
Done when every item below has a verdict with its evidence command, and the report is committed.

## The items

1. **Persisted names (ban 1, `docs/agent/FIX_POLICY.md` header and §"The persisted-name
   inventory").** List every name the train hub, the station rows, the Elevator Depot and their
   upgrades write into a save, in `tools/devmods/train_hub/` and `tools/devmods/elevator_station/`:
   fields, modifier ids, class and template names. Known: the depot's `SMROptIn_depot_rows`,
   `_drones`, `_cabin`, `_targets` (brief 27). Brief `30` may add more (hubless station settings,
   the depot upgrade): read its report and code at its close. Mark which names the move would change.
2. **The ship tests the smokes do not cover:** `FIX_POLICY` §8's run with the Relaunched Fix Pack
   installed and absent, and the toggle test as §0 defines it for content. Say which in-game checks
   brief `35` must carry, per module.
3. **The spec against the code:** spec §4.7-§4.10, §10 and §11, and the hub report
   (`TRAIN_HUB_BUILD_20260918.md`), against the dev mods' code at HEAD. Name every disagreement.
4. **The 19 request-backed resources against the 21 nominal candidates**
   (`TRAIN_HUB_SITTING_20260919.md`, grep `19/21`): is the set still right, and is it the same set
   on the hub, the hubless station rows and the depot?
5. **Brief lifecycle:** every fired brief and its map row in `Train_Hub_Project/README.md` were
   deleted or parked at its close (git history of the folder).
6. **Rulings landed:** build 3's sitting report §6 (`TRAIN_HUB_SITTING_20260919.md`) and every
   owner ruling dated 2026-10-01 and 2026-10-02 in spec §4.7 and §11: each is in the code or in a
   live brief.
7. **Smokes:** run every `tools/devmods/*/tests/*_smoke.py`, scored by exit code, with the count
   reconciled against the file list.

## Scope and method

In: reading, running desk smokes and decoding logs and saves read-only. Out: any edit to code,
specs, briefs or the checklist; findings go in the report, and the orchestrator routes them. Brief
`30` may still be live: audit its areas (the depot's cabin, loading, storage, upgrade and train
buttons; the hubless station rows) at its closing commit, and say which commit you read.
`git log --oneline -5` and `git pull` first; authored at `58ebf7e`+. Use the todo tool before any
write, one item per verdict. The shared TestKit (`B:\Dev\SMR\SMR-BugFixPack-TestKit`) has other
sessions' uncommitted work: never `git restore` it. References: `CLAUDE.md`,
`docs/agent/WORKFLOW.md`, `docs/agent/FIX_POLICY.md`; skills `smr-bug-library` (engine facts,
`docs/agent/facts/INDEX.md`) and `doc-editing` for the report.

## Stops

1. A persisted name has already changed between a committed build and HEAD (a save-contract break):
   report it at once, before finishing the sweep.

## Claim limits

"Holds" means checked by a command or a log line you cite, not that a report says so.

## Lifecycle

One-off; the orchestrator deletes it when done.
