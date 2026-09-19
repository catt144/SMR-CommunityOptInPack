# Train hub build 2 sitting and the 2026-09-19 design rulings — orchestrator's record

**Authority.** The owner's sitting and rulings of 2026-09-19 (spec §10,
`TRAIN_LOGISTICS_DESIGN_20260917.md`). This is the durable home for what the orchestrator
measured and read that day, so it survives the briefs it fed: `TRAIN_HUB_BUILD3_high.md`,
`TRAIN_HUB_REPAIR_high.md` and `TRAIN_HUB_BUILDTRACK_high.md` (deleted at their lifecycles).
Labels: **observed** (a log or capture), **measured** (a command), **read** (source), **inferred**,
**untested**, **owner-ruled**. Game build 1.1.0.403908, Steam 24995074.

## 1. The sitting (Batch 1 of build 2's script only; the owner played it)

Log `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-20260919-13.47.41-6a91a190.log`;
captures `C:\Dev\SMR-ScreenCaptures\SMRTK_0017.png` and `_0018.png`; `SMRTK_ACTION slot_1` id 119.

| Item | Result |
|---|---|
| Boot | Both dev-mod load lines present; observed. One Lua error at 0:00:18: `CommonLua/Editor/ArtSpecEditor.lua:573 attempt to call a nil value (global 'EntitySpecPathToEntity')`, its trace beside our `EntitySpec 'SMROptInTrainHub6'`. Observed; game editor code, cause **not investigated**. |
| Slot 1 | `hub=SMROptInTrainHub6(2010)`, 6 real connectors and directions, 24 synthetic spots, 6 `Box1`, `work_radius=10`, `service_min=10 service_max=20`, 2 drones, `controlled_by_hub=2`, `errors=0`, **`connected_tracks=0`**, **`custom_section=missing`**, `resource_types=19`, `max_z=14`. Observed. |
| Slot 2 (slider ends) | Not in the log read. **Untested.** The owner's capture shows the slider at 20. |
| Owner, by eye | Stub and track heights do not line up (direction not given). Four of six lines cannot attach, "off by one hex"; two attach. No service-area map overlay. No drone count and no prefab plus or minus, so a lost drone is never replaced. The charger pad sits a hex outside the hub and can be built over. |
| Batches 2 and 3 | Not run. Build 3 takes them over. |

## 2. The footprint: asset right, game reading wrong

- **Measured (asset).** Parsing `tools/devmods/train_hub/Entities/SMROptInTrainHub6.entjson`
  (`surfaces`, type `eHexShape`, 244 triangles) onto the lattice (pitch 1,000, row 866.03): 61
  hexes, 4 on each of the six lines, connectors at exactly 4.0 hexes, z 800. Every triangle vertex
  is 577.3 to 577.4 from its nearest hex centre, the circumradius: the boundary sits exactly on
  shared hex corners.
- **Observed (game).** Boot log `[TrainHubDev] SMROptInTrainHub6 line radii d0..d5 = 5 5 5 5 4 4`
  (`line_radii`, `20_TrainHub.lua`); the owner's console read
  `#GetEntityOutlineShape("SMROptInTrainHub6")` = **85** (61 plus 24). The four length-5 lines show
  a red "Blocking objects" at the first track element; the two length-4 lines attach.
- **Inferred, untested.** The game rounds some boundary hexes outward when the triangle corners lie
  on shared hex corners; an inset of about 10% should read 61. Falsify: script the shrink, reload,
  read the count and radii (build 3, end state 1).
- **Excluded.** The texture worker's mesh has real UVs (`zero_uv_faces` 0); the pre-texture UV layer
  was default primitive data (10,586 of 11,666 faces zero-area). Neither touches the footprint.

## 3. Source facts read for the design (each falsifiable at its line)

- A break is a construction site: `TrackBase:BreakTrackElement`, `Track.lua:623-655`; cost halved by
  the `SafeTransport` tech; trains cannot run while `#repair_cgs > 0` (`Track.lua:372-384`). A train
  on a broken element is destroyed and passengers roll 80% death, 20% with SafeTransport
  (`TrainDisasterHandling.lua:1-28`). Completion path: `ConstructionSite:Complete()`,
  `ConstructionSite.lua:1675`.
- New track is the same class of site: `PlaceTrackLine` creates a `TrackGridElement` construction
  group (`Tracks.lua:100-122`); both ends must already be station connectors (`Tracks.lua:240`).
  Element cost `construction_cost_Metals = 200`, `build_points = 1000`
  (`Data/BuildingTemplate/Track.lua:5-8`); the resource scale is **not confirmed**.
- A track merges its two stations' power grids (`TrackBase:ConnectToGrids`, `Track.lua:97-122`).
  A hub that produces power therefore feeds every connected station, and any colony cable one of
  them touches.
- Template numbers (`Data/BuildingTemplate/`): FusionReactor +200 with 8 workers, cost 60 Concrete,
  30 Metals, 15 Electronics, 15 Polymers, upkeep 3 Electronics; StirlingGenerator +10, no workers;
  StationBig draws 10 (cost 50 Concrete, 30 Metals, 10 MachineParts), StationSmall 5; the hub's
  own draw is 10 (owner's infopanel capture).
- Vanilla scales attached objects, not buildings (`SetScale` on attaches, `ConstructionSite.lua:873`);
  a footprint comes from the model's `hex_shape`, so a scaled vanilla building has no smaller
  footprint of its own. Vanilla charger placement: `AttachedRechargeStations.lua:2-29`. No `.hgrm`
  exporter exists in ModTools; only `flpk_extract.py` opens the packs.

## 4. Owner rulings, 2026-09-19 (homes: the briefs, then spec §10 when the builds record them)

- Tripo texturing tried and dropped; texture in Blender (reason not recorded).
- Build 3: drone replacement from prefabs; a service-area overlay; the hub generates its own
  power for itself plus six stations, no workers, higher build cost and upkeep; a scaled fusion
  reactor if it looks good at about 3 to 5 hexes, extending the footprint under it (Stirling model
  the fallback); the charger moves inside the footprint. The +70, cost and upkeep figures are the
  orchestrator's starting values, not rulings.
- Build 4 (repair train), the cheap version: hub pays from stock at the cheaper SafeTransport rate
  always; reach is everything on the network connected to the hub, never an isolated network;
  faster than a normal train, but the speed must not become its own pain point; a cosmetic vehicle
  with a repair livery as a nice-to-have; drones are never limited and the hub pays only the
  outstanding cost. Build 5: the hub builds new track, and a line does not start until it is
  connected to the hub.
- The audit sweep of builds 3 to 5 runs after all three smokes, when the owner calls for it.

## 5. The texture pass, as the orchestrator checked it

Read: `geometry_proof.json` (geometry exactly equal, 0 zero-UV faces), `asset_validation.json`
(three 4096² TGAs, base colour, normal, roughness/metal), `preview_textured_overall.png` and
`preview_textured_floor_closeup.png`, and `blender\README.md`'s owner steps. Matches the look
direction: white, hex floor, slate pads. Red accents are thin rings, not stripes. A black patch
renders at the central beam crossing in Blender even with every map disconnected (README, its own
diagnosis): a geometry question, not a texture one. **Not checked:** the look in game, the Mod
Editor steps run, the normal map's handedness (the worker says unvalidated). The owner's
GFXMaterial item and re-import ride build 3's footprint fix so one re-import carries both.

## 6. Build 3's sitting, later the same day (orchestrator's reading)

Logs `Mars.exe-20260919-15.48.44-6a91a190.log` (slot 1 id 52) and `Mars.exe-20260919-16.22.23-6a91a190.log`
(slot 1 id 60), both on build 3's working tree after `8230d6f`.

- **Observed, id 52:** `outline_hexes=61`, radii `4,4,4,4,4,4`, `connected_tracks=6` on build 3's
  `entjson` shrink probe (uncommitted); the owner saw all six lines attach. Power `70000` produced,
  `10000` consumed, all six station grids `merged=true`; the network grid read `grid_production=140000`,
  `grid_consumption=55000`, `grid_waste=85000` (the source of the rest is build 3's to explain). 4
  drones, 7 prefabs available, `range_overlays=1`, `custom_section=missing`, `fusion_outline_hexes=7`.
  Height row: stub `10800`, vanilla `TrackPillarCCP3` element at `10000` with bbox z `-1726..1069`,
  which is consistent with the owner's eye (track higher than our 8 m stub) only if the bbox top is
  the running surface: **inferred, unconfirmed**.
- **Observed, id 60:** slot 1 `status=ERROR` from the TestKit's own readout, `80_AgentSlots.lua:224`
  `track_height_fields`, a nil at connector 1 on `train_hub_base.save` with `connected_tracks=2`. Two
  `SelectedObj` errors before it were the owner's console lines run with nothing selected.
- **Corrected by the owner:** the orchestrator first claimed every footprint hex blocks pathing. The
  owner pointed to domes. Source: `hex_shape` blocks building; units treat the `Collision` surface as
  solid (`BuildableGrid.lua:12`); enterable buildings set `efWalkable` (`Dome.lua:476`). The Importer
  has per-node `ColliderKind` and `ColliderMask` with `PassabilityMask` (`SceneImport.lua:3495-3515`,
  `:2008-2011`), and the ModTools doc's 1 m disc exists "to block pathfinding units". A drained drone
  would not reach the charger inside the ring: observed.
- **Not ours:** the ring on a selected vanilla station is vanilla's 20-hex passenger range
  (`show_range_all`, `StationSmall`/`StationBig` templates; `DefaultOutsideWorkplacesRadius = 20`,
  `__const.lua:1921-1923`). The hub replaced its own ring with the drone ring
  (`GetSelectionRadiusScale`, `20_TrainHub.lua:545`), so a player cannot see the hub's passenger
  range; offered to the owner as a note, **not ruled**.
- **Observed by the owner:** a vanilla train vanishes when its nose reaches the black backdrop inside
  a tunnel mouth; the arch clears the rail with room above.

**Owner rulings in this stretch, each written into the brief that obeys it (commit in brackets).**
Build 3: the underside passable like a dome, charger stays inside the ring (`cef8e93`, `62b3f5c`);
cut the raised platforms (`cae7604`); reactor at 75% at the current offset, footprint extended only
by the hexes it covers, with the same inset (`51a8e06`); prefab buttons still missing, and drop the
Power grid section from the hub's panel only (`3dfb3b5`). Builds 4 and 5: the vehicle is never a
train (`c251fb1`); tunnels in scope by hide and show (`650d0c9`); the vehicle is the vanilla Wasp
model, recoloured, hovering over the track, moved along track elements with no drone pathing or
battery, playing vanilla repair work (`b1a1ecd`). Policy: `FIX_POLICY` §0, this mod's risk standard
as a content mod, never the fix pack's (`c251fb1`). **Then the owner replaced the hub's drones**
(`91dc2c1`, `024bdcd`, `102db53`, `6eb8903`, `c4bb738`): build 3 dropped the prefab-button chase and
cut the slider to a fixed 15; build 4's repair drones are vanilla Wasps under the hub, identified by
their controller, a constant 30 launched from a recoloured recharge-pad model inside the ring,
never charging (per-drone battery topped up in every hub state, held full in track mode), anything
a drone does within 15 hexes and track work beyond it, with a track-mode save guard and a scoped
`Drone:CanBeControlled` wrap against reassignment. Then ruled: "track work" is any upkeep of
anything on the track or joined to it by a connector, on the connected network (build 4's brief). **Build 3 was mid-run for most of these**; the
owner pasted each to it, but whether it acted on them is the audit's to check.

## 7. State at close

HEAD `c4bb738` at this update. The owner **paused build 3** to discuss the drone redesign; its
`20_TrainHub.lua`, `entjson`, `shrink_footprint_probe.py` and the TestKit's `80_AgentSlots.lua` are
uncommitted and are its. On resuming, the owner pastes build 3 the paused rulings (brief at
`6eb8903`). Builds 4 and 5 stay held. Unfiled: the hub's passenger-range
ring note awaits an owner call. Executed models, from the transcript: Sonnet 5, Opus 5 (1M),
Fable 5.1, Sonnet 5, then Opus 5 (1M).
