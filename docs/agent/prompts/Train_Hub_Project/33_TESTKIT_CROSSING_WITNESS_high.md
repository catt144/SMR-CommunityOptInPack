# 33 — The TestKit's crossing witness (fix, before the final battery)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/33_TESTKIT_CROSSING_WITNESS_high.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`, **after brief `30` closes** (30 may touch the
shared TestKit's slots). Reasoning: high (stock accounting across trains, drones and autosaves).

## Authority and outcome

The orchestrator brief's standing order (owner-authorised sweep, 2026-09-28): *"Before the final
build's full battery, brief a TestKit fix for the crossing witness"*. The defect, from the hub's
build report `docs/agent/reports/TRAIN_HUB_BUILD_20260918.md` (grep `crossing witness cannot
prove`): in a gap-free run (`blind_ms=0`) the witness booked `other_in=74` Metals against
`train_in R1=71`, so R2's 4 out never exceeded it; it appears to miss train unloads at ultra speed,
and autosaves add unexplained stock. Outcome: a witness the final battery (`35`) can rest a crossing
verdict on, or a report that the battery needs a different witness. Done when a desk smoke proves
it can fail and pass, and a short attended check passes.

## What is known

- The TestKit is `B:\Dev\SMR\SMR-BugFixPack-TestKit`, **shared with the fix pack**. Other sessions
  leave uncommitted work there: never `git restore` it; commit only your paths. Its slot conventions
  are `tools/SMRTK.md`. An autosave disarms watches (the game cannot turn autosave off).
- What "a crossing" means has moved since 2026-09-18: the Elevator Depot now carries cargo between
  maps (spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §11). Decide what the battery's
  crossing verdict must prove now (the hub's route-to-route cargo, the depot's cross-map cargo, or
  both), from the spec and the audit report if brief `31` has finished, and record the call.

## Also carried (the audit, `docs/agent/reports/TRAIN_AUDIT_20261002.md` §7)

- `tools/devmods/train_hub/tests/cargo_slots_smoke.py` and `distribution_slots_smoke.py` exit 1
  at `000b498` ("attempt to index a boolean value"): they expect an earlier sitting's installed
  `80_AgentSlots.lua`. Make the slot smokes independent of whichever sitting's slots are
  installed, or point them at their staged files; the battery needs every smoke green.
- Brief 30's papercut: the depot's fixture slots 1/4 refuse while the line's trains hold
  reservations (the owner switched an underground station off to run them). Give the battery's
  fixture slots a way through that does not need the owner to edit the colony.

## Scope and method

In: the witness and its slots. Out: hub, depot and station-row code. `git log --oneline -5` and
`git pull` first in both repos; authored at `58ebf7e`+. Use the todo tool before any write. Apply
`docs/agent/WORKFLOW.md`'s test-design rules: controls, a counterexample that fails, and the
completion evidence. Preload SMRTK slots for the owner's check, about five steps, predictions from
your build; the orchestrator guides it. References: `CLAUDE.md`, `docs/agent/FIX_POLICY.md`; skill
`smr-bug-library` for engine facts (`docs/agent/facts/INDEX.md`).

## Stops

1. The witness cannot separate train unloads from drone and autosave stock changes at all: report
   the alternative (for example, a per-train cargo ledger) instead of tuning thresholds.
2. A change would alter the fix pack's own TestKit behaviour beyond these slots.

## Lifecycle

One-off; the orchestrator deletes it when done.
