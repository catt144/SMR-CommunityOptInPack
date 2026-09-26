---
name: prompt-authoring
description: Write or revise a Relaunched Fix Pack prompt or job brief with settled authority, delegated judgment, a live work list, scope, stops and lifecycle.
---

# Author a prompt or job brief

Write for a capable worker familiar with the repo. State the decision and
outcome; delegate judgment. Reference skills and policies instead of
repeating them.

## Choose the mode

- Investigation or fix build: supply evidence, the question or done-condition,
  and applicable constraints from `docs/agent/FIX_POLICY.md` and owner-approved
  designs. Apply FIX_POLICY's header stop before authoring a build brief.
  Leave approach, read path, step order and exploration open; leads are not
  prescribed hypotheses.
- Repeatable job: give numbered steps, named files, scope, checks and focus.
  If time or budget is limited, say what drops first.
- An unknown answer makes the work an investigation.
- Work exceeding about two sessions is a chain; read
  `docs/agent/support/CHAIN_METHOD.md` before splitting it.

## Every brief

- Authority and outcome: open with the owner's settled decision, without
  reopening it; state the end state and completion evidence.
- Judgment: delegate choices within that authority. Record calls in the
  commit message instead of asking the owner what the worker can decide.
- Live work list: require the todo tool before any write, one item per
  commit-and-verify unit, one in progress, updated as units land.
- Starting state: authoring SHA and startup `git log` / `git pull`.
- Evidence: include facts the worker would otherwise re-derive, each with
  its measurement method and a falsifying command. Point to
  `docs/agent/bugs/INDEX.md` and `docs/agent/facts/INDEX.md` for further records.
- Scope: one in-scope and one out-of-scope line. Investigation scope bounds
  the question, not exploration. Report outside findings without editing.
  Define fences by behavior, not line counts.
- Stops: at most three conditions permitting a report instead of continued
  execution.
- Claim limits: name the unsupported claim and its supported replacement.
- Lifecycle: delete one-offs when fired; retain permanent prompts.
- Routing: filename tags are `_low`, `_medium`, `_high` or
  `_fanout_level_<x>` (1–10, subagent control). `_low` includes settled plans
  and simple investigations needing light-to-moderate reasoning with good
  instructions. State reasoning needs; never name, check or prescribe the
  worker's model or effort. Tags guide the owner, not execution.
- Unattended work: require execution and audit on different owner-selected
  models, for individual items and chains. No unattended result enters the
  record unaudited.
- References: name applicable skills, including `doc-editing` and
  `smr-bug-library`. House rules: `CLAUDE.md`; process:
  `docs/agent/WORKFLOW.md`; code: `docs/agent/FIX_POLICY.md`.

## Prevent stale instructions

Prefer content anchors. Require cited line numbers to be re-derived with
`grep -n` when used; an empty `git diff --stat <sha>..HEAD -- <paths>`
does not validate them.

Re-run `git log --oneline -3` before publishing and after owner waits.
The context's gitStatus block is a staleable snapshot.

## Job-specific safeguards

- Shrinking: default to deletion within authority; survivors earn a home
  or capped slot. Include concrete examples of gaming the cap.
- Triage: delete already-homed content instead of re-archiving it; verify
  the destination body.
- Subagents: output remains a claim until a command confirms the evidence
  supporting each cut or verdict.
- Rule rewrites: inventory requirements first, then require an independent
  blind check given only that inventory and the new text.
- Tests and playtests: apply `docs/agent/WORKFLOW.md`'s test-design and
  execution requirements; include applicable fixture constraints, controls
  and completion evidence in the brief.
- Attended sittings: preload the work into SMRTK slots and triggers
  (`tools/SMRTK.md`) and advance time with Run until at top speed. The owner
  clicks; they do not type. A hand-typed console line, a wait measured in
  owner minutes, or a watch for an on-screen state each needs a stated reason
  no slot can do it. Owner time is the cost being minimised.
- Sitting scope: minor means shippable desk-verified. An item needing a reading
  is not minor; an item called minor gets no reading and is not reported as an
  owed gap. Scope a sitting to the defects the work was created for, and do not
  price an addition in owner minutes — that estimate is not yours to make.

Before handoff, read as the worker: decision, outcome, scope, stops and
completion evidence must stand without this conversation. Read an attended
brief again from the owner's seat: where they see each reading, what they
click, how long it takes. A step resting on one unit's infopanel among
hundreds, or on real minutes of watching, fails that read.
