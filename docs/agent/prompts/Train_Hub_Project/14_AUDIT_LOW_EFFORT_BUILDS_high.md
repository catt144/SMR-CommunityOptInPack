# Audit two builds made below build tier (2026-09-28)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/14_AUDIT_LOW_EFFORT_BUILDS_high.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`. Authored at `f893336`. Start with
`git log --oneline -5`, `git status` and `git pull`.

## Authority

The owner, 2026-09-28: the orchestrator launched two builds from a session run at low effort on
purpose (authoring and recording only), and the subagents inherited that effort. **Both are
audited at build tier before either is trusted.** The rulings they implement are settled; do not
reopen them:
- **Capacity bonus, salvage and rebuild.** Spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`
  §4.10, grep `amending the 2026-09-26 one`: (a) salvage or destruction switches the bonus off,
  and the ruins keep the claim; (b) a rebuild of the ruins restores it without re-buying, keeping
  an off toggle off; (c) clearing the ruins releases it.
- **Doc-checker collapse guard.** The owner approved a gate so a Markdown file collapsed onto one
  line fails doccheck (incident `7d7d0c2`, repaired `04513e7`).

Execution and audit run on different owner-selected models. The capacity change was built on
Opus, the guard on Sonnet.

## The two items

1. **Capacity salvage/rebuild: uncommitted, not merged.** It is in worktree
   `.claude/worktrees/agent-af033497203ef0c8a` (branch `worktree-agent-af033497203ef0c8a`, based on
   `a0768c5`, 20+ commits behind `main`). Two files: `tools/devmods/train_hub/Code/20_TrainHub.lua`
   (section "The Capacity Network Upgrade") and `tools/devmods/train_hub/tests/capacity_smoke.py`.
   The builder's claims, each to be cleared by one check:
   - The desk test passes: `python tools/devmods/train_hub/tests/capacity_smoke.py` exits 0, and
     each of six mutations (salvage stop, rebuild transfer, off-state carry, ruins guard, position
     match, load fixup) makes it fail.
   - No new persisted name, and no vanilla body copied. The hooks used are
     `OnMsg.BuildingDemolished`, a hub-class `ApplyCopyParams` (a call-all method) and
     `OnMsg.LoadGame`. It says `OnDestroyed` was avoided because defining it would replace
     DroneControl's.
   - Between `a0768c5` and `main`, `capacity_smoke.py` is unchanged, and `20_TrainHub.lua`
     changed only in `HealCargoColumns`, so the patch applies cleanly.
   - Its source citations on 1.1.1.405907 (archive `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src`):
     `Building.lua` `:910-919` (OnDemolish → Destroy → Msg), `:1788-1810` Rebuild;
     `ConstructionSite.lua:1724-1745` (ApplyCopyParams before the ruins are removed);
     `BaseBuilding.lua:2` (call-all).
   - Not tested by the builder: anything live; the new hub's own 480 capacity; ruins without
     `orig_state`; a rebuild cancelled mid-construction.
2. **Doc-checker COLLAPSE gate: merged as `e830024`.** `tools/doccheck.py` gains `check_collapse` and
   `collapse_guard_selftest` (a tracked `*.md` over 500 B with under 8 lines is RED).
   `tools/counts_selftest.py` stubs the two gates. The orchestrator checked it once: GREEN at
   HEAD, and RED with `git show 7d7d0c2:docs/agent/prompts/Train_Hub_Project/README.md` in place.

## What done looks like

For each item, a verdict (**PASS**, **PASS WITH FIXES** or **FAIL**) that rests on your own
commands, not the builder's report. Judge correctness against the ruling, `FIX_POLICY` (read its
header; both bans; §2 wrapping), and edge cases the desk test misses. For the capacity change, at
least weigh: ownership during the rebuild window, when ruins and the new hub both exist; the
once-per-colony gate; a second hub's refusal while ruins stand; save/load in each state; toggle
broadcasts; and a destroyed rather than salvaged hub.

- **Fix within the ruling.** Fix the capacity change in its worktree and the guard on `main`; one
  commit per verified unit. Record your judgment calls in the commit messages.
- **Merge the capacity change into `main` only after the owner says no sitting is running.** The
  game reads the dev mod straight from this repo through a junction, so an edit on `main` changes
  the next boot. Until then, leave it verified in the worktree and say so.
- **File the builder's in-game steps**, corrected by your audit, as an addendum to
  `docs/agent/reports/TRAIN_HUB_CAPACITY_20260926.md`. They exist only in the orchestrator's
  session:
  1. Load a save where hub A owns the upgrade and it is on; slot 6 on. Predict: small station 120,
     trains 84/24. Any pre-ruling ruins that still hold it turn off on load.
  2. Salvage A. Predict log `capacity upgrade: hub <A> ruined, bonus off, claim held`; stations 60,
     trains 42/12, over-cap stock kept; hub B reads "Upgrade already constructed" and logs
     `refused on hub <B>` if tried.
  3. Ctrl+click toggle from B. Predict capacities stay 60/42.
  4. Rebuild A's ruins. Predict `carried from ruins <A> to rebuilt hub <new>, on`; 120 and 84/24
     (not 180); no upgrade cost charged.
  5. Toggle off on the new hub, salvage, rebuild. Predict `..., off` and 60; toggle on gives 120.
     Salvage again, clear the ruins with a Drone Hub. Predict B can build it.
  The builder assumed slot 6's stream shows capacities. Check that. Where it doesn't, say which
  slot read is needed; do not add one (TestKit edits are out of scope).
- Hand-back: a short report under `docs/agent/reports/` with each verdict, the commands and their
  exits, your fixes, what you did not verify, and a one-line pointer under the capacity ruling in
  spec §4.10. Run `python tools/doccheck.py` before each doc commit.

Keep a live todo list, one item per commit-and-verify unit, before any write.

## Scope and stops

**In:** the two items above, their tests, the capacity report's addendum, your audit report and
its spec pointer. **Out:** the train bay (`70_TrainBay.lua`, brief `13`), the TestKit, and any
other behaviour change. Report outside findings without editing them.

Stop and report instead of continuing if:
- the capacity ruling cannot be met without a new persisted name or a copied vanilla body;
- the worktree's changes cannot be carried onto `main` without redoing the change;
- fixing the guard would require loosening a threshold that current tracked files need.

Claim limits: desk PASS means "the mocked vanilla bodies agree". It does not mean "works in the
game". The live claim waits for the filed steps.

References: `CLAUDE.md`, `docs/agent/FIX_POLICY.md`, `docs/agent/WORKFLOW.md`, skills
`doc-editing` and `smr-bug-library`.

## Lifecycle

One-off. The orchestrator deletes this brief and its row in this folder's `README.md` once the
audit report lands, and removes the worktree after the merge.
