# Elevator Depot — the look, built for the owner's first view (brief 25, second build)

Brief: [25_ELEVATOR_STATION_LOOK_high.md](../prompts/Train_Hub_Project/25_ELEVATOR_STATION_LOOK_high.md)
(the Elevator Depot handoff, owner rulings D1–D4 of 2026-09-29). The first build's record, the dome
model now on hold, is [ELEVATOR_STATION_LOOK_20260929.md](ELEVATOR_STATION_LOOK_20260929.md).
Built 2026-09-29 on OptInPack `c6eb586` (`git log --oneline -3`; `git pull` reported **Already up
to date**; the brief names `8408f9a` as its authoring base and the tree had moved past it). Installed
game build **25390750**, read with `python tools/doccheck.py --emit-fingerprint` (HOLDS, GREEN), so
stop 3 did not fire. `Mars.exe` was not running (`tasklist /FI "IMAGENAME eq Mars.exe"`: no tasks).
Source citations are from the archived tree `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src`
(build 25390750). Executed model: **Claude Fable 5.1** (`claude-fable-5-1`); one tier-2 subagent
(Opus, `general-purpose`, at this session's effort) read `Station.lua`, `TrainTransport.lua`,
`TrackElement.lua`, `Train.lua`, `SpaceElevator.lua` and `Building.lua`; its two load-bearing
findings (the slot pairing and the label gap) were re-read here before the design used them.

**State: the owner imported and placed the first depot, rejected its look, and the shape was
rebuilt the same evening as a tube on one of the elevator's pads (§6); that rebuild is
export-verified at the desk and waits for the owner's one-step re-import.** Nothing here says the
look is accepted, and nothing here moves cargo. §1–§5 record the first depot as built.

## Commits and files

| repo | commit | what |
|---|---|---|
| SMR-Assets | `533791c` | `elevatorstation/blender/depot_build.py` (the base entity's generator), `verify_depot.py` (the export proof), `ElevatorDepot_work.blend`, `export/depot_proof.json`, `export/verify_depot.json`, the owner's import in `README.md`; `.gitignore` whitelists the two proofs; the top README's row |
| OptInPack | `bfd748c` | the dev mod `tools/devmods/elevator_station/`: `Code/10_ElevatorDepotDev.lua`, the template `SMROptInElevatorDepotDev` and its generated class, `SourceData/SIE_ImportItem/SMROptInElevatorDepot.lua`; `metadata.lua` and `items.lua` follow. The dome-era template, generated class and code file are removed; the dome entities' import items and materials stay (D4) |
| OptInPack | this commit | this report; brief 25's row in `prompts/Train_Hub_Project/README.md` |

The dev mod is still junctioned into the game as
`%APPDATA%\Surviving Mars Relaunched\Mods\SMR-ElevatorStationDev` (mod id
`SMR_ElevatorStationDev_20260929`, title now *DEV ONLY - Elevator Depot (look prototype)*). No renders
were made: the deliverable is the in-game view, and Blender cannot show scaled vanilla art.

## 1. Design calls

1. **Two vanilla visuals on one base entity of ours.** The look is `SpaceElevator` and
   `TrainTunnelUniversal` (D2) attached at run time as `ShapeshifterAutoAttach` visuals at 75 %, the
   hub's reactor pattern (`20_TrainHub.lua:1271-1285`), so vanilla's elevator is untouched and the
   art keeps its auto-attaches. Footprints do not scale with art, so the base entity
   `SMROptInElevatorDepot` carries what the game reads from the building: the footprint, the 14
   train spots and a plinth. It reuses the dome body's material and atlas (`SMROptInElevatorStation`,
   already in the dev mod), so the owner imports **one** EntitySpec.
2. **Layout (building frame, game units; the tunnel's axis on hex row −3).** Vanilla's elevator
   platform is a tripod: along its own x axis the core is only ±15.5 m wide at 75 %, with lobes out
   to ±32 m and a narrow south pier to −35 m. The tunnel (62 m of visible mound at 75 %, 30 m wide)
   therefore runs west–east along y = −2598, south of the origin: its mound swallows the pier and
   stops 2.5 m short of the cabin's footprint, and the cabin and rope run through the origin clear
   of it. The mouth faces −x (angle 180, vanilla's own `Trackconnector1` sense) on hex (−5, −3), so
   the tunnel art sits at (−750, −2598): its own connector, 50 m from its centre, lands exactly on
   our `Trackconnector1` at (−4500, −2598).
3. **Podium, not full-size mouth.** At 75 % the tunnel's rail stub is 6 m up; the art is lifted
   200 units so the stub meets vanilla's 8 m track, and a 2 m plinth of 18 hex prisms under the mound
   (`depot_build.py`, `PLINTH_H`) hides the floating skirt. The scale and lift are live tunables.
4. **Spots at track height.** Every train spot is at z 800: the hub's proven entity puts its
   connectors and synthetic stop spots there (`20_TrainHub.lua:424-432`,
   `corpus/current_5002a49.entjson`, `Trackconnector1 ... 800.0`), and trains slide to a spot's full
   position (`Train:GotoSpot`, `Train.lua:507-512`). Vanilla's station spots sit at z 0 in
   `entities.dat`; the hub's z 800 is the one measured in play, so it is used.
5. **Slot pairing and the buried connector.** `Station` pairs slots 1↔2: a train parked at
   `Stop1` is counted at `Spawn2` within 1 m (`Station.lua:1162-1164`, re-read), so `Spawn2` is on
   `Stop1` and `Stop2` on `Spawn1`, as vanilla's are. Trains keep to the right of their heading:
   arriving (+x) on the −y lane, departing (−x) on the +y lane, at ±335 off the axis (vanilla's
   `Stop1` offset). `Trackconnector2` is buried at (1500, −2598) with `Trackdirection2` at
   (500, −2598), both inside the footprint: a station connector accepts a track only on its
   `Trackdirection` hex (`TrackElement.lua:345-348`) and a building hex takes track only at a
   connector (`Tracks.lua:240`), so no track can ever reach it; `ForEachConnectedTrack` skips a
   lone element (`TrainTransport.lua:73`).
6. **A working station (D3).** `SMROptInElevatorDepotDevBase` is `{ "Station" }` and adds itself to
   the `Station` city label in code, as the hub does (`Building.lua:436-442, 458-463` add only the
   class and `object_class`; `Train.lua:94, :134` walk that label). `disabled_in_environment =
   set("Asteroid")`, `build_category = "Stations"`, instant build, `electricity_consumption = 0`
   so the stand-in needs no grid. Vanilla keeps stations 10 hexes apart (`Station.lua:59`,
   `TooCloseToAnotherStation`), so the owner places it at least 100 m from other stations.
7. **Cabin and rope (D1).** A free `SpaceElevatorCabin` and `SpaceElevatorRope` tiles every 75 m at
   the elevator's world position, as vanilla's `GameInit` lays them (`SpaceElevator.lua:56-74`),
   with `ElevatorMoving` start/end FX on the visual (`fx_actor_class = "SpaceElevator"`) and the
   cabin (`:391-410`; actors `:652-655`). Surface: down 60 m into the ground, no rope above.
   Underground: up the rope's height, 300 m by default. Nothing of it is saved: the props are
   `DeleteOnLoadGame`, re-dressed on load, and the cycle thread stops at each save.
8. **Live tunables.** `SMRElevatorDepotDev.Set(key, value)` moves scale, either visual's offset and
   angle, the tunnel entity and lift, rope heights, travel, leg and dwell times, then re-dresses
   every depot; `Show()` prints the table. A move the owner keeps goes back into `depot_build.py`
   for a regenerate and a one-step re-import, so the spots follow the art.

## 2. Measured

**Footprint — stop 2 did not fire.** Command: `blender --background --factory-startup
--python-exit-code 1 --python depot_build.py` (Blender 5.2.2 LTS), then `verify_depot.py`.

| count | rule | result |
|---|---|---|
| footprint hexes | centre rule over both scaled `hex_shape`s, one inset hex face per cell | **37** (15 elevator only, 18 tunnel only, 4 both) |
| the same, re-derived by `verify_depot.py` with a half-plane test | independent derivation | **37**, identical cell set |
| plinth cells | footprint cells within 15 m of the tunnel axis under the visible mound | 18 |
| hex corner inset | `INSET = 0.9` | 57.73 units |
| extent of the cells | x −4500..3000, y −3464..1732 | 75 × 52 m of cell centres |

The elevator's visible art at 75 % spans x ±32.4 m, y −34.9..+23.1 m, z −13.8..+6.7 m; the mound
spans x −34.0..+27.9 m, y ±14.85 about its axis, z 2..17.5 m. Both reach a little past the cell
centres, as vanilla's own art does past its footprint. Data: `entities.dat` sha256 `64b68206…`,
decoded with `entities_dat.py` (the desk probe is in the scratchpad, its triangle tables are
restated in both scripts).

**Spots** (game units in the entity's frame; `verify_depot.py`: worst position error **0.0001
units**, angles exact, all 12 train spots at z 800, pairing holds):

| spot | position | angle | spot | position | angle |
|---|---|---:|---|---|---:|
| `Trackconnector1` | (−4500, −2598, 800) | 180 | `Trackdirection1` | (−5500, −2598, 800) | 180 |
| `Trackconnector2` | (1500, −2598, 800) | 180 | `Trackdirection2` | (500, −2598, 800) | 180 |
| `Ramparrive1` | (−2600, −2933, 800) | 180 | `Rampdepart1` | (−1800, −2263, 800) | 180 |
| `Stop1` = `Spawn2` | (−700, −2933, 800) | 0 | `Spawn1` = `Stop2` | (200, −2263, 800) | 180 |
| `Ramparrive2` | (−400, −2263, 800) | 180 | `Rampdepart2` | (−1000, −2933, 800) | 0 |
| `Sign1` | (−4500, −2598, 0) | 0 | `Sign2` | (1500, −2598, 0) | 180 |

`Ramparrive1` is 19 m in from the connector, so the arrival slides (the 50 m teleport test,
`Station.lua:1105`). A 41.5 m train parked at `Stop1` spans x −20.3..+21.2 (its box is
−13.3..+28.2 about its origin), inside the mound's −34..+28; at `Spawn1` facing −x it spans
−26.2..+15.3, its nose 3 m inside the mouth face at −29.5. The owner's two-hex train fits with room.

**Rope height and the cave ceiling — NOT MEASURED.** The underground rope defaults to 300 m
(`rope_underground_m`), 2.3× vanilla's own shaft (128.6 m) and 3× the flight roof (terrain +
100 m, `Flight.lua:82-83`); the tiles' art reaches 208 m past the last tile, so the top is at
433 m. `SMRElevatorDepotDev.Measure()` reads the camera and the ceiling objects in batch D, and the
number is moved with `Set("rope_underground_m", n)`.

**Predictions, written before any import:**
1. `Report()` prints 14 `MATCH` lines per depot, `valid=true`, `label.Station=yes`, `working=true`,
   and `connector 1 element=TrackGridElement` at the hex of (−4500, −2598) in the building's frame.
2. The depot places instantly on both maps and takes 37 hexes.
3. A track dragged to the mouth connects; a vanilla train slides in, stops inside the mound out of
   sight, and leaves by the same mouth.
4. The cabin cycles with vanilla's elevator sound; on the surface it sinks into the ground.
5. No `[ElevatorDepotDev]` line reports an error and the log carries no Lua error from
   `10_ElevatorDepotDev.lua`.

## 3. What the owner saw and said

Nothing yet: the owner has not imported, placed or seen the depot.

## 4. Not done

- **Not done here:** the Mod Editor import (the editor keeps no mesh spec until an entity file
  exists, `ArtSpecEditor.lua:565-603`; Ctrl-Alt-A is the owner's); placement; the in-game view;
  the train drive-through; the camera and ceiling read; the owner's adjustments. **The three "done
  when" items are all owed to the sitting.**
- **Not verified until the sitting:** that the Mod Editor picks up the pre-written import item;
  that the tunnel art's own auto-attaches (its doors and rail pieces) come through on a
  `ShapeshifterAutoAttach`; the mound's mouth clearance for a train at 75 %; that an empty vanilla
  train with no work drives to a line end (`Train.lua:256-261, :453-467`); that
  `electricity_consumption = 0` reads as working.
- **Out of scope, per the brief:** cargo between maps, store modes and the drone crew (next
  brief); the twin and its placement rule; vanilla's elevator; hub code and the hub's asset; the
  rail shaft.
- **The dome model (D4):** on hold, not imported; its assets and dev-mod sources stay in place.

## 5. The sitting

**Console lines, not SMRTK slots.** TestKit `587f474`'s six slots and Scratch are bound to the live
train-hub sittings; none is rebound. Slot 6's train/station stream serves batch C as it is. Output
lands in `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-*.log` as `[ElevatorDepotDev]`.

- **A — import (Mod Editor, about five steps).** Follow
  `SMR-Assets/elevatorstation/blender/README.md`, "The Elevator Depot": one new EntitySpec
  `SMROptInElevatorDepot`, `Open in Importer` on `mesh`, Import, save the mod. Afterwards the agent
  checks on disk: `Entities/SMROptInElevatorDepot.entjson` exists with 14 spots; `metadata.lua`
  still lists both code files (an editor save has dropped code lines before).
- **B — surface.** Enable *DEV ONLY - Elevator Depot (look prototype)* in the mod manager and load
  the normal game. Build menu → Stations → **Elevator Depot (dev)**; place it at least 100 m from
  any station, with the tunnel's mouth toward where the track will come from. Look by day: the
  elevator, the mound rising out of its south side, the cabin sinking and rising with its sound.
  Console: `SMRElevatorDepotDev.Report()`, then flush. Send back the `[ElevatorDepotDev]` lines
  and a screenshot.
- **C — the train.** Drag a track from an existing line's end to the mouth (the tool snaps to the
  connector as at any station). Set one of the depot's resource rows to Import so trains have work.
  Press slot 6's stream on, play, and watch one train enter, vanish, and come back out. Flush.
- **D — underground.** Switch maps and place one. Zoom fully out at the lowest pitch: the rope
  should vanish into the ceiling. Console: `SMRElevatorDepotDev.Measure()` then `Report()`. Flush.
- **E — by eye.** `SMRElevatorDepotDev.Set("scale", 80)`, `Set("tunnel_lift", 250)`,
  `Set("tunnel_x", -1000)`, `Set("rope_underground_m", 400)`, and so on; `Show()` lists the keys.
  The owner names what stays; the agent bakes it into `depot_build.py`, regenerates, and the owner
  re-imports in one step.

A save made with a depot needs this dev mod to load it; **demolish every depot before removing the
mod**.

## 6. The first view, and the turn (2026-09-29, later)

**Batch A** went through on the owner's rig: the Art Spec step had been skipped at first (the
Importer said *ArtSpec Entity SMROptInElevatorDepot not found*), then Ctrl-Alt-A, save, Import.
On disk: `Entities/SMROptInElevatorDepot.entjson` with the 14 spots at the designed positions and
the three surfaces, the shared material compiled; the editor's save renumbered the mod handles and
regenerated the template (OptInPack `0793c9a`).

**The first placement showed the plinth and the outline alone.** Cause, from the source: a placed
building carries no `template_name` field (`Building.lua:2701` sets it only on the
`BuildingTemplates` registry wrapper), so the dressing hook's check was false and no visual was
attached. Fixed to a class check, with a `dressed` log line (`815b6f1`); the log then read
`elevator=true tunnel=true cabin=true ropes=0 scale=75` and the owner saw the depot.

**What the owner saw and said.** The 75 % elevator and the 75 % vanilla tunnel side by side, the
tunnel as long as the elevator is wide, its mound swallowing one pad: *"still has graphic errors,
and not a fan of this look at all i wanted a much smaller tunnel that gets out in one of the three
corners of the elevator basically making the tunnel the tunnel just big enough to fit the train
into and still look clean"*. The graphic errors were not itemised; the plinth's hexes showing
round the mound's skirt is the one this session can name.

**The turn (this session's design, the owner's words as the rule).** The vanilla tunnel art is out.
The elevator's platform is a tripod: three round pads of radius 12.2 m at 75 %, centred 23.1 m
out at 30.3°, 150.2° and 269.8° (circles fitted to the `hex_shape` arcs), and nothing on it stands
above 6.7 m while a train rides at 8 m, so only a tube can hide a train. The elevator visual is
turned 30° (`elevator_angle`), which puts one pad's centre at (−2313, −8): on the track axis,
8 units off. The mouth is the base entity's own tube on that pad: 11.6 m wide outside, floor at
6.6 m on the pad's top, apex 14.4 m, from the pad's rim at x −36 m to x −8 m short of the cabin,
with a portal rim carrying the blue line and TrackCCP3's beam profile inside. The connector is on
the axis at (−4000, 0), so the track's own element ends at the mouth and no stub is needed; the
buried second connector is at (1000, 0) with its direction at the origin. A positive attach angle
turns counter-clockwise in the game's (x, y): the hub's reactor at offset (3897, 2250) faces the
centre with attach angle 210 (`20_TrainHub.lua:1144, :1283`).

Measured (`depot_build.py`, then `verify_depot.py` PASS with its own turn and membership tests):

| count | rule | result |
|---|---|---|
| footprint hexes | centre rule over the turned elevator, plus the tube rectangle and the connector hex | **21** (17 elevator only, 1 connector hex, 3 both) |
| the same, re-derived independently | complex-number turn, half-plane test | **21**, identical cell set |
| spot error | 14 spots | 0.0 units, angles exact |
| tube z range | the rim included | 6.4..14.8 m |

| spot | position | angle | spot | position | angle |
|---|---|---:|---|---|---:|
| `Trackconnector1` | (−4000, 0, 800) | 180 | `Trackdirection1` | (−5000, 0, 800) | 180 |
| `Trackconnector2` | (1000, 0, 800) | 180 | `Trackdirection2` | (0, 0, 800) | 180 |
| `Ramparrive1` | (−3200, −335, 800) | 180 | `Rampdepart1` | (−3100, 335, 800) | 180 |
| `Stop1` = `Spawn2` | (−2200, −335, 800) | 0 | `Spawn1` = `Stop2` | (−2000, 335, 800) | 180 |
| `Ramparrive2` | (−1200, 335, 800) | 180 | `Rampdepart2` | (−1400, −335, 800) | 0 |

The train's length now decides the look: the tube hides 28 m. The owner's two-hex train fits; the
disputed 41.5 m would show 13 m of tail. The sitting reads it.

**Owed:** the owner's re-import (Open in Importer on `mesh`, Import, save), a restart for the
Lua, then batches B–E of §5 on the new shape.
