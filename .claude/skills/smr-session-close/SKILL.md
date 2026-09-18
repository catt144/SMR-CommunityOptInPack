---
name: smr-session-close
description: Preserve findings and unfinished work in the Opt-In Modules repo. Use for session close-out, unfiled-finding lookbacks, or handoff to fresh context.
---

# Session close

Preserve evidence and next steps within the session's scope.

## Recover

Record HEAD and `git status --short`. Review the conversation, diffs, working files and
relevant report sections in full. Identify commits by sha and diff, not the shared author.
If context is partial, start from the task and STATE's live pointers; state that limit.

Before polishing prose, inventory findings and every block of the handoff being updated:

`finding/block | evidence | home passage | next action/trigger | disposition`

Include unfiled decisions, request departures, unfinished or deferred work, and new
evidence affecting existing decisions. Use scratch if needed to survive context loss.

## Route

Read each destination's actual passage, including subitems. Match the finding, not just
its topic or an "already filed" pointer. Search by meaning and identifier; check archive
and ignored paths explicitly before concluding an expected record is missing.

- Owner calls about THIS mod: `docs/DECISIONS_OWED.md`. Add the question to the
  matching item, or create one; keep independently answerable parts, ruling conditions and
  pull-only scope. Evidence goes to a pull-only home first, linked from the item.
- Owner calls that bind the FIX PACK (the shared TestKit, `EF-` id allocation, a fix-pack
  feature): the fix pack's `docs/PLAYTEST_CHECKLIST.md`, through its entrance gate.
- Defects/facts: the appropriate entry in `docs/agent/bugs/` or `facts/`. A new `EF-` is
  filed in the FIX PACK first and mirrored here at the same id.
- Agent work: the responsible live prompt/report, with next action and takeable condition.
  Situation-dependent playtests go on the owner list as riders.
- Lessons: a durable task-specific document with evidence and limits; do not promote them
  to standing policy or create skills merely to close a session.

Preserve observed/inferred/untested/owner-ruled distinctions. Keep owner conditions,
withdrawn claims and dead ends with their basis. Preserve runnable checks and acceptance
conditions, stable file/symbol names, and answers costly to discover but cheap to confirm.
Distinguish current values from historical baselines and tested revisions; retain the
latter with measurement commands/builds. Do not invent evidence for incomplete searches.

## Handoff, if needed

The handoff is temporary: remaining work, blockers and minimal orientation with links.
Facts need durable homes even if the handoff's filename persists. For this session's
handoff or a requested successor launch, assign each old block and new finding:

1. **Keep:** name the successor action or live constraint that needs it here.
2. **Route:** name what a cut would lose; open the proposed home's actual passage and
   confirm it preserves the finding, procedure and conditions. Topic overlap is insufficient.
   If missing, file it first where someone working that task would look, then re-read it.
   Record the verified home before removing the block.
3. **Unresolved:** preserve findings and sources in a task report if their final home
   is uncertain. Hand off the remaining filing decision and link, not the findings.

File dormant mechanisms with their reopening conditions; once homed, remove them from
the handoff. Do not keep reminders solely to prevent rediscovery. Use the gated
`docs/agent/prompts/README.md` map instead of a hand-kept prompt list, and existing fact
and owner sources instead of repeating their summaries. Link only what the next action
needs. Remove duplicate tellings and settled split/absence notices once existing routes
suffice; preserve any live obligation or owner-required notice.

Use plain headings, short paragraphs and clickable Markdown links. Avoid decorative
emojis and emphasis; reserve emphasis for live holds or vetoes. Measure before and after
with the same byte-count method; never meet a size target by dropping unhomed content.
Read the actual handoff's launch instruction.

## Verify

Reconcile each row: filed, verified present, resolved with basis, or unresolved with a
home. Re-read changed destinations and links for usable evidence and next steps.
Review the diff for lost obligations and unintended changes.

Run `python tools/doccheck.py` for doc changes. Report destinations, unresolved routing,
uncommitted work and any handoff launch/byte delta. For handoff removals report traced/total
and unhomed content dropped (must be zero). Bound completeness to sources reviewed.
If nothing needs filing, say so briefly; no new document is needed.
