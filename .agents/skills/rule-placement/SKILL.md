---
name: rule-placement
description: Decide whether something should be a rule at all, and where it lives if it should. The owner's rule-placement test, authored 2026-09-14, carrying the owner's authority to purge. Use before writing, moving, keeping or cutting a rule in any repo.
---

# The rule-placement test

The owner's, derived in a 2026-09-14 design session while tearing down a monolith's
"Ground rules". It is the same test in every repo; only the document names differ.

## The authority this carries

Owner ruling, 2026-09-17: *"before we run into an issue with a rule cannot be purged by
an agent, I authored the rules test so it carries my authority."*

Applying it is **executing the owner's decision, not making one**. A rule the test
disposes of is purged, and purged means deleted rather than re-archived — content
already recorded elsewhere does not need a second home.

The delegation is to the **test**, not to your judgement. A rule goes because the test
disposes of it, never because it reads as unnecessary, and the evidence goes in the
commit message. **Where the test does not decide, keep the rule and ask.** An
undecidable rule is never purged on the balance of probability.

## The question

Ask it of every rule — not "is this important?", which is why the document grew:

> **What actually stops this, if not the reader's memory?**

| answer | disposition |
|---|---|
| Structure — the reader cannot perform the action at all | delete the rule |
| A guard — a machine already catches it | a one-line pointer to the gate |
| Nothing, and it has been violated in practice | it was never a rule; it is a wish |
| Nothing, and it binds exactly one job | that job's skill or brief |
| Already a recorded fact with a canonical home | delete the prose, keep the fact |
| Nothing, binds every session, no guard is possible | the always-loaded set, kept very short |

## Four shapes that should not be rules at all

| shape | meaning | disposition |
|---|---|---|
| **CANNOT** | structurally impossible for the reader | delete |
| **WOULD NOT** | possible, but contrary to how an agent operates | **an incident check is required before cutting** — this branch can delete an earned rule |
| **WRONG READER** | the actor is not this document's audience | move it, do not delete |
| **NOT A RULE** | information written in the imperative | an engine fact or a pull-only lesson; never the always-loaded set |

## Placement, once it survives

Tiered by **when a rule loads**, not by topic: the always-loaded entry file for duties
binding every session · a document's own `Must_Read_Header` for duties binding only that
document · a skill or brief for a named task.

A canonical rule reads `Rule: <one imperative sentence>.` — no bold, no emoji, none of
MUST / NEVER / ALWAYS — and is unique repo-wide.

## Two things that catch people

**Find duplicates by meaning, not by string.** Two rules that share no words can be the
same rule.

**A rule you are about to keep because it is "important" has failed the test.** Importance
is the reason the document grew in the first place.

---

Scope: this skill is repo-agnostic and lives at the user level, so it loads in every
project. Each repo's own doc-editing skill holds that repo's specifics — which document is
the owner's list, which documents are agent-facing, which gate enforces the header format.
In the Relaunched Fix Pack the worked reasoning, the owner's verbatim wording and the
calibration warning are in `docs/agent/reports/RULE_PLACEMENT_TEST.md`.
