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

## 6. State at close

HEAD at this section's writing: `b6a8587` ("Train hub build 2: imported body and service-area smoke"),
committed by another session after `98a362a`; its message says Batches 2 and 3 remain for Build 3.
That is build 3's first step, so **build 3 has started** (`git log`, 15:11 on 2026-09-19; the session's
identity is not recorded). The tree was clean after that commit. Unfiled: spec §9's Tripo paragraph still
needs replacing (build 3 may be editing the spec; leave it to the audit or a quiet tree); which vanilla building the owner's
"that's it scale in game" screenshots show was assumed, not verified, and build 3 must confirm the
entity name. Executed models, from the transcript: Sonnet 5, then Opus 5 (1M), then Fable 5.1,
then Sonnet 5.
