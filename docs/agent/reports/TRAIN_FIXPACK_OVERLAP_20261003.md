# The train modules against the shipped fix pack — overlap check, 2026-10-03

An orchestrator subagent did this read-only check, on Opus 5.5. It is the evidence behind the
owner's 2026-10-03 waiver of the fix-pack-absent run for the train modules (`FIX_POLICY` §8).

## What was read

- **The shipped fix pack:** the Steam Workshop copy
  (`A:\SteamLibrary\steamapps\workshop\content\3215050\3787202810\ModContent.fpk`), decoded.
  - Its 46 `Code/*.lua` files match fix-pack repo commit `be06b4d5` ("Close v18"), with line
    endings ignored.
  - Its metadata says `version 25`. The release was 1.0.26, which fits the version bump the upload
    save makes (EF-068).
  - The game itself loads the fix-pack repo through a link. That copy adds one unreleased fix,
    C121 `Fix_UniversalDepotSeedsToggle.lua` (universal depots only), which does not touch trains.
- **The train modules:** `Code/StationRows_*`, `Code/TrainHub_*`, `Code/ElevatorDepot_*`, the
  three `Opt_*` files and `00_Core.lua`.
- **Game source:** the archived 1.1.1.406343 tree, for vanilla lines.

## Result

**No hidden dependency in either direction.**

- The train code makes no reference to the fix pack:
  `grep -nE "SMRFixPack|CommunityFixPack|SMR_CommunityFixPack"` over the 14 train files gives 0
  hits, comments included. As a control, the same grep over all of `Code/` finds 3 persisted-name
  strings in non-train modules.
- The fix pack makes no reference to the train code:
  `grep -rcE "SMROptIn|OptInPack|SMRElevatorDepot|HubTrain|TrainHub"` over the decoded fpk gives
  0 hits. The control `SMRFixPack` gives 278.
- `metadata.lua` declares no dependency.

**No method or Msg is patched by both mods.**

- The train modules have 35 engine patch points; the fix pack has 56 patch targets across 44
  modules.
- None of the train modules' wrap targets appears in the fix pack. That includes `FindTask`,
  `SpoilStoredResources`, `AssignTrain`, `TransferCargo`, `UnloadAll`, `SetDesiredAmount`,
  `WaitWakeup` and `PersistGame`.
- The Msg handlers add up rather than replace one another.
- So load order does not matter.

**Where behaviour differs without the fix pack.** In each case the cause is a vanilla bug that the
fix pack repairs. None is a defect in this mod.

| Fix | Without the fix pack | Risk |
|---|---|---|
| F65 `Fix_TrackTunnelPowerBridge.lua:150-176` | Vanilla merges power grids only across tracks longer than 2 pieces (Track.lua:672-680). A station joined to a hub connector-to-connector does not share the hub's power. The bridge is saved, so it survives into a later load without the fix pack. | REAL, layout-specific |
| F44/F91 `Fix_TrackSalvageWipe.lua:47-237` | Salvaging a piece can cut more track, and can destroy trains on a short remainder (TrackElement.lua:508-511, :529-530, :543-544). | REAL when a piece is salvaged |
| F66 `Fix_TrackConnectorPingPong.lua:144-196, :222-247` | Coincident connector hexes are taken back and forth forever. The hub's own override is at `TrainHub_20:873-909`. | LOW, only with coincident hexes |
| F47, F48, C119, F57a, F50, F51 | A Metals refund, a one-time track pass, ghost power cells, a rocket non-Fuel edge case, hub drones idled near an auto rocket, and colonist route-cache freshness. | LOW |

## Owner rulings, 2026-10-03

- The fix-pack-absent run is **waived** for the train modules. In the owner's words: *"The fix pack
  cannot interfere in anyway with this mod ... I will not make a mod a dependancy. And we cannot
  force people to install the fix pack."* Recorded in `FIX_POLICY` §8.
- The F65 case is **accepted as vanilla behaviour**. Without the fix pack, a station on 1-2 pieces
  of track from a hub does not share the hub's power, and the hub does not compensate for it.

## Not checked

- Anything at runtime, or the battery fixture's layout.
- Whether the hub's power cells match its footprint.
- Whether a drone hub extender can link to a train hub.
- The non-train opt-in modules.
- The Paradox copy of the fix pack.
