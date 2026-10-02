# 35 — The final full battery on the shipping layout (attended test)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/35_FINAL_BATTERY_high.md` in a fresh
session rooted at `B:\Dev\SMR\SMR-OptInPack`, **after briefs `33`, `34` and `34b` close**. Reasoning: high
(a full prediction battery across modules and configurations).

## Authority and outcome

The owner, 2026-09-19: a design pass gets a smoke; **the full prediction battery runs once, on the
final build** (spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §10). `FIX_POLICY` §8:
the complete shipping test runs **with the Relaunched Fix Pack installed and with it absent**, and
§0 defines the toggle test for content; both toggle directions. Outcome: one battery script, run
with the owner, whose verdicts decide whether the train project is complete. Done when every
module the owner keeps has passed in both configurations and both toggle directions, or the owner
has parked or cut it; the report names the released fix-pack version tested.

## What the battery carries

- Each module's predictions from its spec sections (§4.7-§4.10, §10, §11) and its build reports,
  restated for the shipping layout from brief `34`. Treat predictions written before 2026-09-28 as
  possibly stale: re-derive them.
- Every in-game check the audit (`docs/agent/reports/TRAIN_AUDIT_20261002.md` §2) says the smokes miss.
- The crossing verdicts on brief `33`'s witness.
- OI-38's last step on `docs/PLAYTEST_CHECKLIST.md`: the scripted up-leg read (slot 6, the train
  stream, then slot 2 with an Export row), on the final up-leg loading.
- The hub's spawn-on-siding correction, never seen live: watch a hub spawn.
- **Movement is finished** (owner, 2026-09-21). It may reopen once, here, if the owner wants moves
  tweaked; that goes to `Parked/TRAIN_HUB_MOVE_high.md`, never as a gate.

## Method

`git log --oneline -5` and `git pull` first; authored at `58ebf7e`+. Use the todo tool before any
write. Preload SMRTK slots (`tools/SMRTK.md`): the owner clicks, they do not type, and each
hand-typed console line needs a stated reason no slot covers it. About five steps a batch,
predictions beside each, hubs named by role. Slot 6 streams trains with `effective_speed`; an
autosave disarms a watch, and the owner re-presses the slot. The orchestrator guides the owner and
reads the log on each "flushed". Apply `docs/agent/WORKFLOW.md`'s test-design rules. A failure is a
recorded verdict and a routed fix, not a retry for a preferred result. References: `CLAUDE.md`,
`docs/agent/FIX_POLICY.md`; skills `doc-editing`, `smr-bug-library`.

## Scope

In: testing and recording. Out: fixes (each failure goes to the orchestrator for a brief).

## Stops

1. A module cannot be tested in one configuration (for example, the fix pack will not load): report
   which, and what the owner must decide.

## Lifecycle

One-off. When the battery passes, the orchestrator deletes the whole `Train_Hub_Project/` folder and
its row in `docs/agent/prompts/README.md` in one commit (owner, 2026-09-18).
