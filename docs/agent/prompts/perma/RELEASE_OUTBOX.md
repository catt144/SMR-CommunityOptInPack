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

### Pending · FIRST PUBLICATION (staged 2026-10-03, Launch_Prep/03)
- **The whole shipping set, first time on a store:** Acknowledged warnings (D02),
  Multiple Artificial Suns (D04), Drone speed and carry dials (D09), Service interest
  tags (D15), Station import/export rows (D16), Train Hub (D17), Elevator Depot (D18).
  Every one off, or at base, until the player turns it on.
- Change note: the "First release" block in `docs/UPLOAD_WORKFLOW.md` §3, already in
  `metadata.lua` `last_changes`.
- Surfaces prepared: both store bodies (`UPLOAD_WORKFLOW.md` §3, `metadata.lua`), the
  public `README.md`, the site's `content/opt-in/` section and nav (site `9d490ce`,
  undeployed). Owed at upload: the owner's platform choice and approval step (OI-44).
- Not in this entry, by rule: the development history before first publication (the
  2026-09-22 widenings, the train rebuilds, retired D01/D06/D07/D12 and parked D03)
  never shipped, so none of it is a player-facing change.

### Pending · Launch exit disclosure and warning (2026-10-03, Launch_Prep/01)
- OI-43: newly written saves identify this mod as nonoptional for the native missing-mod warning;
  older saves can retain their optional flag until resaved with the mod enabled.
- Both maintained store bodies now disclose retained Train Hub upgrade receipts and possible
  ordinary bonuses after removal. The ChoGGi/LukeH acknowledgement is on the public README
  and the site, not the store bodies (owner's store template, 2026-10-04).
- Both store bodies, the public README and the site also carry the class-reference disclosure
  from `reports/SHIP_RESIDUAL_20261003.md` (`37aff24`, site `9d490ce`); the residual owners stay
  UNKNOWN by the owner's choice, and no clean removal or train recovery is claimed.

## Last released

**Nothing yet.** This mod has never been uploaded; `docs/archive/RELEASE_HISTORY.md`
holds no release section by design. The first `### Released in v…` line arrives with the
first confirmed upload, through `release_prompt.md` §5. The drain rewrites this section.
