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

### Released in v1.0.3 (2026-10-05) · batch `2026-10-05-02`, base `c3eb22f`

#### Station rows: untouched rows keep the game's balancing without a hub (2026-10-05, D16)
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

### Released in v1.0.4 (2026-10-24) · batch `2026-10-22-03`, base `62d3e41`

#### Station rows without a hub: rows relay, Import/Export defaults, a Default state; the Elevator Depot's rows reach trains without a hub (2026-10-21, D16, D18)
- Targets mechanisms described in three Workshop reports (Erion, Xeryx, TheGodUncle; the report's
  §1): on a line with no Train Hub a set row made its station a dead end, so a Large Station joining two lines stopped
  passing a resource between them, Import at a low number brought a trickle, and the Elevator
  Depot's Export half kept its stock because its rows were invisible to trains without a hub.
- Now, on a line with no hub, a row keeps its amount for its own station and the rest balances
  by the ruled weights among cargo-reachable members (R1, R7), so a station that joins lines
  passes cargo through below full reserve. A click to
  Export sets 0, a click to Import sets 100, or 50 on a hubless station that joins lines. The row
  can return to Default: base-game balancing off a hub, the hub's untouched setting on its network
  (R4). The depot's rows work without a hub, loading and unloading, and its unset sliders mean
  Import 100 / Export 0 on every depot,
  hub-managed ones included, instead of the dial percentage (R2, R5): an existing depot with
  untouched sliders changes on load.
- Player surfaces touched: the station row cycle (Default, Export, Import, Not accepted), its
  icons for Default and Balanced, the Import/Export/Default tooltips and a joining-station line
  (`Code/StationRows_45_TrainDistributionUI.lua`); the depot's Export tooltip and unset slider
  (`Code/ElevatorDepot_10_ElevatorDepot.lua`). The Mod Options help line still names the four
  words "Import, Export, Balanced or Not accepted" (`items.lua`); the release decides its wording.
- Rulings, build and limits: `docs/agent/bugs/D16.md` (owner 2026-10-21, R1–R7), `D18.md`;
  `docs/agent/reports/STATION_ROWS_RELAY_20261021.md` §§15–18. The first independent audit's
  corrections (cargo-inaccessible allocation, now R7; rounding; the inherited hub-click seam;
  junction help; an emptied hub table) are built at `3aa5402` and confirmed as desk-verified
  by the second audit. The audit gate for v1.0.4 is cleared; release proceeds through
  `docs/agent/prompts/perma/release_prompt.md`. No named player's save is verified fixed;
  this revision is not tested in game. Refresh latency on a large colony is unmeasured.
  Two unattended in-game smokes on `SMRTK_A.sav` (2026-10-22) logged no error, the depot targets as
  ruled and set rows on a hubless junction pulling stock in, with `D.Refresh()` at 11.10 ms on 19
  stations, and the owner's glance found it clean
  (`docs/agent/reports/STATION_ROWS_RELAY_LEG_20261022.md`).

### Released in v1.0.6 (2026-10-25) · batch `2026-10-25-04`, base `8ddf8e2`

#### The Train Hub no longer replaces the game's WaitWakeup (2026-10-23, D14)
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
