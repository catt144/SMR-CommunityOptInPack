# Release outbox — player-facing changes staged for the NEXT upload

## Must_Read_Header
<!-- RULES -->
Rule: Append a filled `### Pending` entry whenever a shipping module, a player-facing surface or a store claim is added, retired or materially respecified. [A3: pass]
Rule: Do not append a pending entry for an internal change that never reached a player. [A3: pass]
Rule: Move a batch's pinned pending entries to `docs/archive/RELEASE_HISTORY.md` only with `python tools/release_batch.py drain`, after the owner confirms that batch's upload on both stores. [A3: pass]
Rule: Do not delete a pending entry except through a release or with an explicit withdrawal reason. [A3: pass]
<!-- /RULES -->

This ledger tracks every player-facing tree change since the last upload.
`docs/agent/prompts/perma/release_prompt.md` derives the change note and the surface
updates from it and pins the entries one release carries as a batch
(`docs/agent/support/RELEASE_BATCH.json`). After the owner's confirmed upload only that
batch's entries move to `docs/archive/RELEASE_HISTORY.md`; an entry added later, or held
out of the batch, stays here. `docs/agent/support/RELEASE_SURFACES.md` defines
which changes have a player surface.

**Live tree version:** `metadata.lua` `version` — read it, never hand-set it
(`release_prompt.md` § Release rails). **No count word:** this mod's store body carries
no module count on purpose (the Mod Options page is the checkable list), so no release
bumps one.

## Pending — goes out with the next upload

## Last released

**v1.0.2, 2026-10-04** — batch `2026-10-04-01`, base `03dfda8`. Its entries are in `docs/archive/RELEASE_HISTORY.md`.
