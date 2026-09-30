# Elevator Station — the look, built for the owner's first view (brief 25)

Brief: [25_ELEVATOR_STATION_LOOK_high.md](../prompts/Train_Hub_Project/25_ELEVATOR_STATION_LOOK_high.md).
Spec §11 (owner ruling 2026-09-29). Built 2026-09-29, starting at OptInPack `36adc5a`: `git pull`
reported **Already up to date**. Installed game build **25390750**, read with
`python tools/doccheck.py --emit-fingerprint` (GREEN), so stop 3 did not fire. Source citations are from the archived tree
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src` (build 25390750). Executed model:
**Claude Fable 5.1** (`claude-fable-5-1`), no subagents.

**State: built and export-verified at the desk; nothing is imported or placed yet.** The owner's
Mod Editor import (§4, batch A) comes first, then the viewing sitting. Nothing here says the look is
accepted: the owner has seen no render and no in-game view yet.

## Commits and files

| repo | commit | what |
|---|---|---|
| SMR-Assets | `0b381b6` | `elevatorstation/blender/`: `station_build.py` (generator), `verify_station.py` (export proof), `station_render.py` (previews), `README.md` (pipeline and the owner's import); the top README's layout row; `.gitignore` whitelists the two proofs |
| SMR-Assets | `07d67b1` | `ElevatorStation_work.blend`, `export/station_proof.json`, `export/verify_station.json`, built at `0b381b6` |
| OptInPack | `e169746` | the dev mod `tools/devmods/elevator_station/` (`SMR_ElevatorStationDev_20260929`); `.gitignore` for its compiled textures. This is the checkpoint before the owner's Mod Editor session |
| OptInPack | this commit | this report; brief 25's row in `prompts/Train_Hub_Project/README.md` |

The dev mod is junctioned into the game as
`%APPDATA%\Surviving Mars Relaunched\Mods\SMR-ElevatorStationDev`, the rail shaft's pattern.

## 1. What was built, and the design calls

Three entities, because the importer keeps one mesh node and one material per entity
(`SMR-Assets/_shared/IMPORTER_FACTS.md`):

| entity | faces | contents |
|---|---:|---|
| `SMROptInElevatorStation` | 4,052 | ring, ribs, collar, floor, the store, the column to its headframe, the rail run, 14 spots, `hex_shape` / `Selection` / `Collision` |
| `SMROptInElevatorStationGlass` | 1,296 | the dome glass, its own blending material (the hub dome glass's flat maps and flags) |
| `SMROptInElevatorStationShaft` | 1,116 | the column from 28 m to 300 m; attached on the underground map only; shares the body's material |

1. **Beside the rail, never over it.** The rail line and all 14 of `TrainStationCCP3`'s train spots
   (`Trackconnector1/2`, `Trackdirection1/2`, `Ramparrive1/2`, `Rampdepart1/2`, `Spawn1/2`,
   `Stop1/2`, `Sign1/2`) are copied verbatim. The wiring brief's station class can then run vanilla
   `Station` code on vanilla's names at vanilla's positions (`Station.lua:620,1101-1103,1162,1188,1202`).
2. **The small dome is the hub's own, derived at build time.** `station_build.py` imports
   `trainhub/blender/hub_skeleton.py` and reads `RING_PROFILE`, `DOME_R`, `DOME_BASE_Z`, `DOME_H`,
   `RIB_TUBE_R`, `RIM_STRIP_*` and `FLOOR_T` from it; the hub's asset is not edited.
   - The ring section is scaled 0.6 about its glazing channel and kept at the hub's heights: ring
     6.84–8.82 m, glass from 8.40 m, level with a vanilla train's floor at 8.00 m.
   - Outer radius is 11.4 m. The glass has a 9.81 m radius and rises at the hub's own proportion
     (0.352) to an apex at 11.85 m.
   - Six ribs carry white sleeves. The ring's blue strip and the floor's edge line are the hub's blue
     line.
   - Knobs: `RING_OUT`, `RING_SECTION`, `DOME_RISE_RATIO`.
3. **The store** is a 5 × 5 m core to 6.5 m, with six racks under the ribs, each holding
   2 × 2 × 3 crates of 1 m in amber and grey. It is decoration: whether real cube stacks replace it
   is the store brief's call.
4. **The cargo-lift column** is a 3.55 m square lattice: navy posts, off-white frames every 3 m and
   two blue guide rails. A lift car sits at 15 m. The headframe box is at 26–28 m with a red beacon
   on top, so the surface top is 28.5 m.
5. **The underground shaft** is a separate entity: the same lattice, 28–300 m. Underground the
   headframe reads as a landing on it.
6. **Paint** is the hub's reactor palette (`paint_concept.py:51,132-140`): navy, off-white band,
   dark fittings, the blue line. It is flat swatches on a 1024² atlas, with no texture pass
   (owner's method, 2026-09-20).
7. **The rail beam** copies vanilla `TrackCCP3`'s profile (2.06 m wide, 8.53–10.69 m) and spans
   ±44.9 m as vanilla's station rail does. Four pillars at ±10 and ±30 m leave the connector hexes
   (±40) free for the element a track places there. No line is painted on the beam's faces: a
   train's clamp wraps them (lane 2.89 m, width 4.16 m).
8. **The building** is template `SMROptInElevatorStationDev`:
   - plain vanilla `Building`, so no custom class enters a save;
   - instant build, no cost, in the Stations menu;
   - `disabled_in_environment = set("Asteroid")`, the value vanilla's stations and the hub use.
     The template default is `set("Underground","Asteroid")` (`Building.lua:253`), and
     `IsBuildingAllowedIn` reads only the template's own set (`:56-104`), so **stop 2 did not fire**:
     no global setting and no vanilla elevator is touched.
   - The glass and the shaft are `ShapeshifterAutoAttach` visuals on the train hub glass's lifecycle
     (`DeleteOnLoadGame`, re-dressed on `LoadGame`), gated on `IsValidEntity`.
   - A plain `Building` switches its self-illumination off when not working (`Building.lua:1422-1439`),
     so the dev code keeps the body's glow at 200.

## 2. Measured

**Footprint — stop 1 did not fire.** Ours is **16 hexes**, 7 under the dome and 9 on the rail row;
`verify_station.py` read them back from the FBX, corners inset 57.7 units. The vanilla station the
connectors are copied from is larger. Counted on its decoded `hex_shape` (8 triangles, game hex
lattice rows 866 / pitch 1000):

| entity | centre rule (inclusive barycentric) | touch union (any polygon overlap) |
|---|---:|---:|
| `TrainStationCCP3` (Train Station) | 24 | 41 |
| `TrainStationLargeCCP3` — positive control | 85 | 95 |

The control reproduces `IMPORTER_FACTS`' recorded band for the large station (85..95; the game reads
95), so the counter is sound. Data: `Packs/BinAssets.fpk:entities.dat`, sha256 `64b682061315fab9…`,
extracted with `CROSSING_SHAPE_20260929.md` §9's `members`/`unpack` and read with `entities_dat.py`;
lattice scanned over rows ±10 and columns ±12.

**Connector positions.** Game units in the entity's frame. Blender (x, y) maps to game (−y, −x) ×100.

| spot | game (x, y, z) | game angle | vanilla `TrainStationCCP3` |
|---|---|---:|---|
| `Trackconnector1` | (−3997, −1731, 0) | 180 | identical |
| `Trackconnector2` | (3997, −1731, 0) | 180 | identical |
| `Trackdirection1` | (−4996, −1731, 0) | 180 | identical |
| `Trackdirection2` | (4996, −1731, 0) | 180 | identical |

`verify_station.py` re-imports the FBX; its worst error over all 14 spots is **0.0001 units**, with
angles exact (`export/verify_station.json`). The connectors sit on hex row −2 at columns ±4: one at
each end of the 9-hex rail row. Trains stay outside: the building-side lane (Blender x 12.34–16.28 m,
z 8.04–12.36 m) holds **0 body vertices**, and the dome clears it by **0.955 m**
(`export/station_proof.json`, `train_lane_check`). In game, `SMRElevatorStationDev.Report()` prints
each placed stand-in's connector positions against vanilla's and says MATCH or DIFFERENT HEX.

**Column height and the cave ceiling — desk readings; the in-game read is owed.**

| reading | value | where |
|---|---|---|
| vanilla underground elevator's game bbox top | 12,861 units (128.6 m), mesh only 12.9 m, so the shaft is an attach | `entities.dat`, `ElevatorUnderground` |
| vanilla surface elevator's shaft, downward | −12,449 units | `ElevatorSurface` bbox |
| space elevator tether | 1.14 m wide, −22 to 277.5 m | `SpaceElevatorRope` bbox |
| the underground flight roof | terrain + 100 m, `hard_ceiling = true`, "the cave roof" | `Flight.lua:82-83` |
| stalactites | hang 2.0–4.0 m from their origin (mesh z −401..0) | `Underground_Stalactite_01..06` |
| RTS camera defaults | pitch 3–60°, zoom-out look-at distance 600 m; underground minimum height from map data | `Config/camera.lua:92-115` |

No ceiling object or ceiling class exists in the Lua. The column is sized at **300 m underground**:
2.3× vanilla's own shaft and 3× the flight roof. It is one constant (`SHAFT_TOP`) and one live offset
(`SMRElevatorStationDev.ShaftZ(m)`). Whether it ever shows its top depends on how high the
underground camera can rise. That is **NOT MEASURED**; `SMRElevatorStationDev.Measure()` reads it in
batch C, with every object standing above 20 m within 150 m of each elevator, grouped by entity.

## 3. Renders

`B:\Dev\SMR\SMR-Assets\elevatorstation\blender\preview_*.png` (git-ignored; `station_render.py`
rebuilds them in about 13 s):
- `overall`
- `top_grid`: the 10 m hex grid and the 16 footprint hexes in green
- `track_level`
- `store`
- `night`
- `underground`: the shaft into the dark
- `underground_high`

Stand-ins drawn in the renders only:
- a 20 m train box at `Stop2`, sized to the owner's "about two hexes" and not the disputed 41.5 m;
- vanilla-like track three hexes past each connector;
- red connector markers.

The glass is drawn more opaque than the game's 6 % so it shows. Blender lighting cannot show the
game's glow or acceptance.

## 4. The viewing sitting

**Console lines, not SMRTK slots.** At TestKit `587f474`, `80_AgentSlots.lua` has all six slots and
Scratch bound to the live train-hub sittings: capacity reads, the fixture setters, and slot 6's
stream. Rewriting it would break them. The owner accepts console lines where no slot is free
(2026-09-27). Batches, about five steps each:

- **A — import (Mod Editor).** Follow `SMR-Assets/elevatorstation/blender/README.md`, "The owner's
  import": three new EntitySpecs, `Open in Importer` on each `mesh`, Import, then save the mod. The
  materials and import items are pre-written. Afterwards the agent checks on disk:
  - three `Entities/*.entjson` files;
  - the body's 14 spots against vanilla;
  - `metadata.lua` still listing both code files (an editor save has dropped code lines before).
- **B — surface.** Enable *DEV ONLY - Elevator Station* in the mod manager and load the normal game.
  Build menu → Stations → **Elevator Station (look only)**; place it beside a line; look by day and
  at night. Console: `SMRElevatorStationDev.Report()`.
- **C — underground.** Switch maps and place one near an elevator. Zoom fully out at the lowest
  pitch and compare the column with the vanilla elevator's shaft. Console:
  `SMRElevatorStationDev.Measure()` there, then `Report()`.
- **D — adjust by eye.** The owner names what to move: size, heights, colours, the column. The agent
  regenerates, and the owner re-imports only the changed entity.

**Predictions** (written before any import):
1. `Report()` prints two `MATCH` lines per stand-in, `valid=true`, and
   `visuals=SMROptInElevatorStationGlass`. Underground it also lists `SMROptInElevatorStationShaft`.
2. The stand-in places instantly on both maps. Its footprint takes 16 hexes: the dome's 7 and the
   rail row's 9.
3. `Measure()` prints `env=Underground` and each vanilla elevator's shaft top at about 12,861 cm.
   The camera and ceiling numbers are unknowns, not predictions.
4. No `[ElevatorStationDev]` line reports an error.

A save made with a stand-in needs this dev mod to load it; **demolish every stand-in before
removing the mod**.

## 5. Not done

- **Not done here:** no import, no placement and no in-game view; the Mod Editor is the owner's.
  The in-game ceiling and camera read: **NOT RUN**.
- **Out of scope:**
  - the store, the elevator range rule, the twin and the station class (next brief);
  - vanilla's elevator;
  - hub code and the hub's asset;
  - the rail shaft.
- **Unverified until batch A:** that the Mod Editor picks up the pre-written import items and
  materials. The README gives the manual fallback.
- **Unverified until the sitting:**
  - that "Stations" shows the building underground;
  - the SI glow in game;
  - instant placement on uneven ground.
- **For the wiring brief:**
  - `Building:GameInit` calls `UpdateMapMaxObjRadius` before `BuildingInit`, so today's 300 m attach
    does not enter the map's object radius. A real station attaching it elsewhere should keep that
    order.
  - The rack crates are mesh, not cube spots.

## 6. Owner direction after the build (2026-09-29, evening) — the design turns

The owner, having seen vanilla's Space Elevator in play: *"Make a mini space elevator, and underground
to surface cargo elevator. It already handles the cargo internally, we don't have to show it or have
plates. Drones service it and when it comes back down drone come in and get the cargo out. Then
playes can decide if they want a train station there. Drone hub there, handle it how they want to."*
This session answered with source evidence:
- The cabin is a separate `SpaceElevatorCabin` moved by Lua `SetPos`, and the rope is stacked
  `SpaceElevatorRope` tiles every 100 m (`SpaceElevator.lua:56-73, 391-410`).
- The sound is the `ElevatorMoving` FX on the building and the cabin (`:395-407, 652-659`).
- A scaled vanilla visual keeps its auto-attaches (`AutoAttach.lua:2606-2619`; the hub's reactor
  runs at 75 %).
- The footprint does not scale with the art. Vanilla's SpaceElevator `hex_shape`, counted as in §2:

| scale | centre rule | touch union | extent |
|---|---:|---:|---|
| 100 % | 38 | 61 | 85 × 79 m |
| 75 % | 19 | 40 | 64 × 59 m |
| 50 % | 9 | 22 | 42 × 40 m |

The Train Station is 24 / 41 (82 × 47 m).
`SMRElevatorStationDev.Preview(scale, mode, rope_m)` (OptInPack `c49f3a4`) shows the scaled art
with its cabin cycle and sound in game. It is visual only.

**Owner ruling, 2026-09-29: *"lets try the 75% one."*** The crossing's look becomes vanilla's Space
Elevator at 75 %, on a footprint of our own drawn to cover it. The dome model of §1 is **on hold,
not imported**; this report's §4 batch A is suspended.

The owner's follow-up questions, not yet ruled:
- the elevator's own internal drones;
- a **companion station** "designed to play by our elevator rules", so that a station on either
  side is loaded or unloaded by its Import / Export / Balanced settings.

Facts for that answer:
- The four modes live today in the hub dev mod's `40_TrainDistribution.lua`.
- The hub itself is `{ "Station", "DroneControl", "ElectricityProducer" }` (`20_TrainHub.lua:209`):
  a station with its own drone crew, already running in game.

Still open from this session's list:
- which way the surface cabin travels, up or down;
- per-trip cargo versus a shared store;
- placement: beside a vanilla elevator, or anywhere.

**Owner, 2026-09-29, later the same evening — the train mouth.** In place of a companion
station: *"we borrow the asset of a tunnel make it smaller, and blend it into the elevator. So its
already train ready. Traints can deliver into or out of it. Drones can as well. Depending on player
setup. Gives players the most agency. Then with the tunnels design we still don't have to deal
with internal cargo visuals, the train just goes "inside" and comes out"*. Clarified: *"More of a
depot. Trains still dont goto new maps it enters the elevator, and the cargo transfers from the
elvator"*. §11's rule that trains never change maps stands.

Desk facts, `entities.dat` at 25390750:
- `TrainTunnel` and `TrainTunnelUniversal` measure 110 × 43 m, with a 49-hex footprint (centre
  rule).
- Their one connector is `Trackconnector0` at (5000, 0, 0).
- At 75 % the tunnel takes 25 hexes. Butted into the 75 % elevator, the pair takes about 35–44.

What does not scale:
- Vanilla track runs 8 m up. A 75 % tunnel's rail stub lands at 6 m, and its connector at 37.5 m,
  off the hex lattice.
- The train keeps its full size.

`SMRElevatorStationDev.PreviewTunnel(scale, lift_m, angle_deg, entity)` (OptInPack `45e19ff`)
shows the scaled tunnel art in game.
