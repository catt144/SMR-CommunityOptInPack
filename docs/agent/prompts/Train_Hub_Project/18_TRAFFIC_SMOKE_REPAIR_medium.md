# Repair the failing `traffic_smoke.py` without changing train movement

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/18_TRAFFIC_SMOKE_REPAIR_medium.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`. Start with `git log --oneline -5`,
`git status` and `git pull`.

## Authority

The owner, 2026-09-28: *"lets get this done"*: make the train hub's desk suite green again.
Movement through the hub is **finished and owner-accepted** (2026-09-21; the orchestrator prompt,
"Movement is FINISHED"). The owner has watched it live many times since, most recently the cargo
upgrade's faster trains on 2026-09-28 ("looked fine, not stuttering"). The accepted live
behaviour is the reference. The test serves it, not the other way round.

## The failure

`python tools/devmods/train_hub/tests/traffic_smoke.py` exits 1 with `-10800 != 0` at its
arrival-orientation assertion. It has failed since at least the 2026-09-23 audit
(`docs/agent/reports/TRAIN_HUB_AUDIT_111_20260923.md`, grep `traffic_smoke`). Brief 15 also showed
it fails identically on its starting revision
(`docs/archive/train_bay_fixes_20260928/traffic_baseline.txt`). -10800 is -180° in the engine's
arcminutes, so a train is facing the opposite way from the test's expectation.

## The question and done

Is the test's expectation stale, for example written against a geometry or orientation convention
the accepted movement later changed? Or does the code really turn an arriving train the wrong way
in a case the owner has not seen live? Find out which, with evidence: git history of the assertion
and the code it checks, the spec's movement rulings (§10), and the move reports.
- **If the test is stale:** correct it to the accepted behaviour. Keep the assertion strong,
  not deleted or loosened to "any angle". Add a mutation that still fails it.
- **If the code is wrong:** do not change it. Report the case, how to reach it live, and what
  the owner would see, then stop. Movement changes need an owner ruling.

Then run every `tools/devmods/train_hub/tests/*_smoke.py`, report members = passing + failing,
and add a short report, `docs/agent/reports/TRAIN_TRAFFIC_SMOKE_<date>.md`. Run
`python tools/doccheck.py` before the doc commit. Keep a live todo list before any write.

## Scope and stops

**In:** `traffic_smoke.py` and its fixtures. **Out:** every file under
`tools/devmods/train_hub/Code/`. Stop and report if the fix needs a code change, or if other
smokes depend on the same stale expectation in a way you cannot fix without weakening them.

References: `CLAUDE.md`, `docs/agent/FIX_POLICY.md`, `docs/agent/WORKFLOW.md`, skill `doc-editing`.

## Lifecycle

One-off. The orchestrator deletes it, with its README row, once the report lands.
