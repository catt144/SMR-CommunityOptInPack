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

### Pending · The Train Hub no longer replaces the game's WaitWakeup (2026-10-23, D14)
- Targets a field crash report received privately (its source is not named in release notes,
  owner 2026-10-24). With the mod installed, hub module on or off, the game's C `WaitWakeup`
  was replaced by a Lua wrapper. Paused threads therefore carried that wrapper into saves, and
  a load after the wrapper was gone could crash.
- Now nothing in this mod replaces a C function: the wrapper, its map-change swaps, the save
  guard and the load mapping are removed. Train stops do not change: the wrapper's 6000 game ms
  equalled vanilla's, measured at 6000. Saves from earlier versions can keep old frames in
  indefinitely waiting threads; measured, those saves load with and without the mod.
- Player surfaces touched: none. No option, tooltip, store or README claim changes. The change
  note's wording is the release's: one line that the Train Hub no longer replaces a game
  function, with no reporter named.
- Rulings, build and limits: `docs/agent/bugs/D14.md` (a), owner 2026-10-23 (option 1; unmarked
  pre-guard dev-hub saves unsupported) and 2026-10-24 (reporter unnamed). Unattended native leg
  on 1.1.1.406343 (`tools/trains/hub/tests/ww_leg.json`): old→new load, manual save, autosave
  and cold reloads clean; mod-absent loads clean. No leftover frame was seen resuming, and the
  reported failing saves were not reproduced.

### Pending · Arboretum test build (2026-10-03, D19)
- Adds an off-by-default in-dome service consuming Seeds, using vanilla Large Garden art.
- Test content only: gameplay acceptance, balance, category and footprint decisions remain open.
- Before inclusion in an upload, reconcile its store description and uninstall disclosure with
  D19 and the measured save-exit residual. The existing first-publication copy does not describe it.
- Evidence and sitting: `docs/agent/reports/ARBORETUM_BUILD_20261003.md`.

## Last released

**v1.0.4, 2026-10-24** — batch `2026-10-22-03`, base `62d3e41`. Its entries are in `docs/archive/RELEASE_HISTORY.md`.
