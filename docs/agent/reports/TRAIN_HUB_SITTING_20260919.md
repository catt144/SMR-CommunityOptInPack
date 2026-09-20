# Train hub build 2 sitting and the 2026-09-19 design rulings — orchestrator's record

**Authority.** The owner's sitting and rulings of 2026-09-19 (spec §10,
`TRAIN_LOGISTICS_DESIGN_20260917.md`). This is the durable home for what the orchestrator
measured and read that day, so it survives the now-consumed build-3 brief,
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

## 6. Build 3's sitting, later the same day (build agent's audit)

The early probe logs remain useful history, but the closing evidence is
`Mars.exe-20260919-20.33.45-6a91a190.log`, game 403908, save `SpaceY Sol 23`. Slot 1 ids 116/121
and slot 2 ids 124/127 were run after the save/load at lines 504-554. This is what I did about
each ruling from the sitting:

- **Footprint and lines:** I verified the durable shrink from `d07a457` and final re-import
  `5002a49`, rather than relying on the temporary `entjson` probe. They produced 66 outline hexes:
  the 61-hex ring plus the reactor's five-hex lobe, all with the 0.9 inset. The six line radii read
  `4,4,4,4,4,4`. One track piece was physically incomplete; after the owner reconnected it, the
  post-reload read was six tracks, six merged station grids and zero grid mismatches. I deleted the
  obsolete untracked `shrink_footprint_probe.py`.
- **Open underside, platforms and collision:** the final collision/passability pass and inner-pillar
  cut left the underside usable for the owner's drone-work check. The raised platforms were cut
  (`PLATFORMS = False`). The owner cleared the final work and visual checks. I do **not** claim the
  original drained-drone-to-charger proof: the later charger ruling made that leg obsolete before
  it passed.
- **Reactor and UI:** I kept the reactor at 75% and offset `(3897,2250,0)`; only its five covered
  hexes extend the footprint. I stopped the missing-prefab-button chase, removed its section
  attempts, hid only this hub's Power grid section, removed the slider and fixed work/UI/selection
  radius at 15. After reload the probe read one overlay and all four radius values at 15; the owner
  accepted the overlay visually.
- **Current drones and pad:** the later ruling superseded "charger stays inside". I removed the
  functional charger and kept one non-selectable `RechargeStationPlatform` two hexes from the hub
  centre as build 4's launch-pad model. The hub tops its current stopgap drones up instead: two
  controlled drones survived reload at `battery=battery_max=8000000`, and the owner saw them work.
  None of build 4's 30-Wasp, track-mode or reassignment design was implemented here.
- **Power:** after the Mod Editor save removed the template's duplicate electricity declarations
  (`f71a3c2`), `20_TrainHub.lua` still supplied +70000/-10000. The merged fixture grid was
  +140000/-55000 with 85000 waste. Seven Stirling Generators supplied the other 70000. This colony
  had zero cable elements, so the hub's surplus reached the six merged station grids but not colony
  cables; it reaches cables only when that connected grid actually includes them.
- **Height and width:** the track/stub measurements caused no Lua change. Game units: running
  surface `10800`; connector `10800`; stub top `10800`; vanilla element x width `1000`; y width
  `204`. The nil-safe TestKit readout replaced the earlier formatter failure. `6123ae7` was the
  separate, already-committed synthetic train-spot deck correction; I did not re-derive or edit it.
- **Storage and resources:** the source cap is 150000 (`3b4f73b`) and the editor-generated file
  matches (`c35f58b`). Fill-all ended at 2850 cubes, 19 live resource requests times 150, with
  `max_z=9`; the owner saw no beam or portal-train clipping, and the full state survived reload.
  The apparent 19/21 discrepancy is two different sets: 21 nominal candidate ids, versus 19
  enabled request-backed resources in this colony. `BlackCube` and `MysteryResource` were the two
  without requests. The shared TestKit was updated in `e838d4f` to classify this as an expected
  enabled subset; that classifier was not rerun in this sitting.
- **Texture, beds and load order:** I used the already-imported textured body (`d07a457`) and the
  final pillar/cargo pass (`5002a49`); the owner accepted the in-game look and full-bed clearance.
  I did not rerun or edit the now-external Blender pipeline at
  `C:\Dev\SMR-Assets\trainhub\blender`. `266191d` makes `20_TrainHub.lua` create the shared Floor
  table itself, so the Mod Editor's item reorder cannot leave it nil.
- **Mod Editor procedure:** no further owner pass was needed. The completed pass confirmed that
  saving regenerates the generated template. Ctrl+Alt+B creates a new BuildingTemplate item; it is
  never a regeneration instruction.
- **Train movement:** I changed no train spot, `TrainDepart`, occupancy or `synthetic_spot_pos`
  logic after the owner's stop. Arrival/departure behaviour and the known floor-drop/floating cases
  moved intact to `TRAIN_HUB_TRAINS_high.md` (build 3b, `9b3ddda`).
- **Later builds:** the Wasp vehicle, tunnel hide/show, constant 30 repair drones, connected-network
  track work and track construction remain rulings for builds 4 and 5, not build-3 work.

The selected vanilla station's 20-hex passenger ring remains a separate vanilla presentation fact;
build 3 claims only the hub's fixed 15-hex drone overlay.

## 7. State at close

Build 3's smoke passed. After reload the hub retained 66 outline hexes, all six connections, all six
merged station grids, +70/-10 hub power, 2850 cubes at `max_z=9`, two full stopgap drones, no
charger, the launch-pad model, fixed radius 15 and one overlay. The only Lua error in the process
was the known `ArtSpecEditor.lua:573` Mod Editor boot error; the hub slots reported zero errors.
`Textures/` and `Fallbacks/` are intentionally gitignored and were not committed. Build 3b is now
the live train-movement task; build 4 stays held behind its smoke. Executed models, from the
transcript: Sonnet 5, Opus 5 (1M), Fable 5.1, Sonnet 5, Opus 5 (1M), GPT-5.
