# Release history — every upload's player-facing changes

Append-only. `docs/agent/prompts/perma/release_prompt.md` appends one
`### Released in v<major.minor.version> (date)` section here when it closes a confirmed
upload, so the newest release is LAST. The outbox (`prompts/perma/RELEASE_OUTBOX.md`)
keeps only what has not shipped.

Created 2026-10-03 with the release system (the root `RELEASE_SYSTEM_high.md` brief,
consumed). **No release has happened yet**; this file gains its first section with the
first confirmed upload and never earlier. An empty ledger is the honest state, not a
gap.

### Released in v1.0.2 (2026-10-04) · batch `2026-10-04-01`, base `03dfda8`

#### FIRST PUBLICATION (staged 2026-10-03, Launch_Prep/03)
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

#### Launch exit disclosure and warning (2026-10-03, Launch_Prep/01)
- OI-43: newly written saves identify this mod as nonoptional for the native missing-mod warning;
  older saves can retain their optional flag until resaved with the mod enabled.
- Both maintained store bodies now disclose retained Train Hub upgrade receipts and possible
  ordinary bonuses after removal. The ChoGGi/LukeH acknowledgement is on the public README
  and the site, not the store bodies (owner's store template, 2026-10-04).
- Both store bodies, the public README and the site also carry the class-reference disclosure
  from `reports/SHIP_RESIDUAL_20261003.md` (`37aff24`, site `9d490ce`); the residual owners stay
  UNKNOWN by the owner's choice, and no clean removal or train recovery is claimed.
