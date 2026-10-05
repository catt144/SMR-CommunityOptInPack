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

### Pending · Arboretum test build (2026-10-03, D19)
- Adds an off-by-default in-dome service consuming Seeds, using vanilla Large Garden art.
- Test content only: gameplay acceptance, balance, category and footprint decisions remain open.
- Before inclusion in an upload, reconcile its store description and uninstall disclosure with
  D19 and the measured save-exit residual. The existing first-publication copy does not describe it.
- Evidence and sitting: `docs/agent/reports/ARBORETUM_BUILD_20261003.md`.

### Pending · Station rows: untouched rows keep the game's balancing without a hub (2026-10-05, D16)
- Fixes a player report: with Station rows or the Train Hub on, trains on a line with no hub
  stopped carrying cargo between stations left at their default settings, and worked again
  with the modules off.
- Now, on a line with no Train Hub, a resource row nobody has changed is balanced between
  stations as in the base game. A row the player sets (Balanced amount, Export, Import) still
  behaves as described. Lines on a hub's network, and lines ending at an Elevator Depot, are
  unchanged.
- Player surfaces touched: the row tooltip for an unchanged Balanced row on a no-hub line
  (`Code/StationRows_45_TrainDistributionUI.lua`). The README and store bodies never described
  the old pin behaviour, so only the change note is owed.
- Ruling, build and limits: `docs/agent/bugs/D16.md` (owner 2026-10-05). Seen live once on the
  reporter's save; the depot-line exception and sharing against a set row are desk-tested only.

## Last released

**v1.0.2, 2026-10-04** — batch `2026-10-04-01`, base `03dfda8`. Its entries are in `docs/archive/RELEASE_HISTORY.md`.
