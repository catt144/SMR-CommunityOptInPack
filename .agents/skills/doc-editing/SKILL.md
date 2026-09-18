---
name: doc-editing
description: Edit Opt-In Modules documentation while preserving owner decisions, obligations and meaning across source documents, maps and generated views. Use before a documentation edit here.
---

# Documentation edits

Check the meaning that doccheck cannot check. Work from the document's existing purpose and its
actual destination passages, not a topic match or a fresh GREEN.

## Before changing the text

- Identify the reader and the action this passage supports. Use `docs/README.md` for placement; do
  not move a rule to a new home without existing authority.
- Identify any owner decision the edit creates, settles or changes. Preserve its wording and the
  condition under which it was made. An item in `docs/DECISIONS_OWED.md` still there must still be
  owed by the owner; delete it once the owner has acted.
- When trimming or retiring a passage, separate settled evidence from remaining obligations. Follow
  the destination's local retirement rule; verify the full obligation survives at its home before
  cutting. A matching heading is not proof.
- To shrink a document, make deletion the default: each surviving line needs a reason, a home, or a
  slot under a stated cap. Do not defend cuts line by line.
- ⚖️ **Owner ruling 2026-09-17 (OI-09): agent-facing documents MAY be machine-tuned hard; the
  owner's may not.** Agent-facing is `docs/agent/**` (including `WORKFLOW.md`, `FIX_POLICY.md`,
  `prompts/**`, `reports/**`), `CLAUDE.md` / `AGENTS.md`, and `tools/README.md`.
  The owner's are `docs/DECISIONS_OWED.md` and `docs/FUTURE_IDEAS.md`; `docs/README.md` is read by
  both and is cut only with a line from the owner. ⚠️ The two PLAYTEST files are not in this repo —
  the fix pack's ruling governs them.
  ⛔ **Content already recorded elsewhere is DELETED, not re-archived.** Archiving it is the failure
  mode this ruling exists to prevent: under hard triage the temptation is to archive everything
  rather than cut, which satisfies the letter and misses the point, and an overhaul that files its
  own output into the tree it is shrinking can come out net negative. `git log -S` holds deleted
  text; the reasoning goes in the commit message. Retire silently — no dated note, no
  strikethrough, no "superseded by", no pointer.
  ⛔ **Protected regardless of this licence:** the two bans; `FIX_POLICY` §4 **inverted** for a mod
  whose product IS opinionated modules, with the donor's §4 kept verbatim as §4-donor; the §5 dial
  addendum for D09; and the both-configuration ship test.
  ⚠️ **Re-derive every line citation after a prune.** The donor found six worklist items and a whole
  authored brief already executed, because citations die the moment the text around them moves. It
  costs one grep.
- If the question requires historical evidence, use smr-orientation's archive search route. A
  default search excludes `docs/archive/` deliberately.

## When the edit writes, moves or keeps a rule

One question decides it — not "is this important?", which is why the docs grew:

**What actually stops this, if not the reader's memory?**

| answer | disposition |
|---|---|
| Structure — the reader cannot perform the action at all | delete the rule |
| A guard — a machine already catches it | a one-line pointer to the gate |
| Nothing, and it has been violated in practice | it was never a rule; it is a wish |
| Nothing, and it binds exactly one job | that job's skill or brief |
| Already a recorded fact with a canonical home | delete the prose, keep the fact |
| Nothing, binds every session, no guard is possible | the always-loaded set, which stays very short |

Four shapes that should not be rules at all: **CANNOT**, structurally impossible for the reader,
delete · **WOULD NOT**, possible but contrary to how an agent operates — an incident check is
required before cutting, because this branch can delete an earned rule · **WRONG READER**, the actor
is not this doc's audience, move it rather than delete · **NOT A RULE**, information written in the
imperative, which becomes an engine fact or a pull-only lesson and never joins the always-loaded set.

Find duplicates by meaning, not by string. The worked reasoning, the owner's wording and the
calibration warning are in the FIX PACK's `docs/agent/reports/RULE_PLACEMENT_TEST.md` — ⚠️ that file
is not in this repo; read it at `C:\Dev\SMR-BugFixPack`.

⚖️ **Owner ruling 2026-09-17: the test carries the owner's authority.** *"before we run into an
issue with a rule cannot be purged by an agent, I authored the rules test so it carries my
authority."* ⇒ Applying it is executing a decision, not making one: a rule the test disposes of is
purged without coming back, and purged means DELETED under OI-09. ⛔ The delegation is to the TEST,
not to your judgement — a rule goes because the test disposes of it, never because it reads as
unnecessary, and the evidence goes in the commit message. Where the test does not decide, KEEP the
rule and ask; an undecidable rule is never purged on the balance of probability.

⛔ **Placement is tiered by when a rule LOADS**, not by topic: `CLAUDE.md` for duties binding every
session, a document's own `Must_Read_Header` for duties binding only it, a skill for a named task.
Adding a document to `RULE_HEADER_DOCS` forces it to carry a block. A canonical rule reads
`Rule: <one imperative sentence>.` — no bold, no emoji, none of MUST / NEVER / ALWAYS — and is
unique repo-wide; `doccheck`'s RULES HEADERS gate reds on the rest.

## The things this repo will not let you rewrite

The persisted-name, donor-name and archive duties are canonical in `CLAUDE.md`'s
`Must_Read_Header`. They cover names quoted in prose as well as code: a cosmetic rename in a doc
can teach a later session to rename the save contract. Pre-split records retain their old paths,
namespace and family names.

## Keep regeneration within the edit

The kernel's generated-source rule applies. `python tools/doccheck.py --regen` reads every entry on
disk, including peers' unfinished work.
Before choosing it, inspect changes under both `docs/agent/bugs/` and `docs/agent/facts/` and
compare them with your edit's inputs. Review the resulting diff: fresh generated output can still
contain work outside your change. The same applies to `AGENTS.md`, regenerated from `CLAUDE.md`.

## Review meaning after the edit

- For a revised prompt, compare the description that routes readers to it with the resulting
  purpose, scope and lifecycle. Filename agreement does not establish that the pointer still
  describes the job.
- For an owner ruling, check its condition and body together, and that it lands where the role that
  obeys it reads it. `docs/DECISIONS_OWED.md` holds the *ask*; the ruling goes where it binds.
- For a move or a cut, inspect the destination passage and the source diff together. Preserve open
  work and conditions; remove the moved instruction from its source in the same change. Do not
  substitute a size target for this check, or restore temporarily suspended caps without the
  owner's ruling.

This skill supplies judgment checks. It does not verify that an agent invoked it.
