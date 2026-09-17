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
- When trimming or retiring a passage, separate settled evidence from remaining obligations. Verify
  the full obligation survives at its home before cutting. A matching heading is not proof.
- To shrink a document, make deletion the default: each surviving line needs a reason, a home, or a
  slot under a stated cap. Do not defend cuts line by line.
- If the question requires historical evidence, use smr-orientation's archive search route. A
  default search excludes `docs/archive/` deliberately.

## The things this repo will not let you rewrite

- **Persisted names** (`SMRFixPack_*` fields and modifier ids) are save contract even inside prose
  that merely quotes them — a doc edit that "fixes the naming" teaches the next session to rename
  the real thing. `docs/agent/PROVENANCE.md` §2.
- **Pre-split and pre-rename records** cite `Code/Opt_*.lua` paths in the fix pack, the `SMRFixPack`
  namespace, and older family names. Translate mentally; **do not edit the records**.
- **`docs/archive/`** is append-only. Never rewrite or delete what is archived there.

## Keep regeneration within the edit

`python tools/doccheck.py --regen` reads every entry on disk, including peers' unfinished work.
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

Run `python tools/doccheck.py` before committing; red blocks.

This skill supplies judgment checks. It does not verify that an agent invoked it.
