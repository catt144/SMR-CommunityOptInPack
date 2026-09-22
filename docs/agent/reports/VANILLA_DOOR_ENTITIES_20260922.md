# Vanilla door entities for the train-hub portals — survey (desk, 2026-09-22)

**Question (owner).** Reuse a vanilla door entity that already has an open/close animation on the
six tunnel portals of the train hub, scaled to an arched mouth ≈ **6.5 m wide × 13 m high at the
crown** (train ≈ 4 m wide), opening as a train approaches and closing behind it. We cannot author
animations; we can attach vanilla entities and drive `SetState` / `SetStateText` / `SetScale`.

**Mid-task owner input (2026-09-22).** *The only single door found in game is the Space Elevator's
roll-up shutter — horizontal slats, orange seams, chevrons painted on the threshold in front of it;
the dome doors are double and cannot be split.* §1 answers the Space Elevator question first; §2
corrects two parts of that premise from the data.

**Method.** Desk only. **The game was not launched; every console line below is `[NEVER RUN]`.**

- Lua citations are `<path>:<lines>` under
  `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908\Src\`. The brief named
  `C:\Dev\SMR-SrcArchive\...`; that path no longer exists — the tree is at
  `C:\Dev\SMR-SrcArchive__MOVED_20260921\1.1.0.403908\Src`. Both were read and the 14 files cited
  here are **byte-identical** across the two copies (`sha256sum`, 14/14 SAME), so the canonical
  `SMR-Shared` root is cited.
- The game is installed as Steam app **"Project Spark"** at
  `A:\SteamLibrary\steamapps\common\Project Spark` (`WORKFLOW.md:11`). No `.ent` files ship; entity
  specs are compiled into `Packs\BinAssets.fpk` → `entities.dat` (14,168,326 B decompressed).
- ⭐ **Sizes below are MEASURED from that file**, not guessed — see §5 for the record layout, the
  calibration against a known spec, and the falsifier. Nothing was extracted to disk: `entities.dat`
  was decompressed in memory with `tools/flpk_extract.py`'s `parse_table`. **No writes anywhere but
  this file.**

⚠️ A report is not authority. Attaching anything to a shipping module needs an owner ruling recorded
for this mod (`CLAUDE.md` header, `FIX_POLICY.md` §4).

---

## 0. The one-paragraph answer

Every animated vanilla door is **wider than it is tall**; `SetScale` is a **single integer, uniform
only** (`CommonLua/LuaExportedDocs/Game/GameObject.lua:1007-1012`; no non-uniform scale export
exists in the tree — grep for `ScaleX`, `SetScaleXYZ`, `NonUniform`, `SetMirrored` in
`LuaExportedDocs` returns nothing). So **no vanilla door can fill a 6.5 × 13 m arch**: the aspect the
portal wants is 0.50 (tall), the best vanilla aspect is 0.75 and the usable ones are 1.5–5.0 (wide).
The portal shape has to move toward the door, or the door sits in the lower part of the arch.

The two doors worth building on are **`ElevatorSurfaceDoor`** (19.46 m × **12.93 m**, single slab,
rolls straight down into the ground, 600 ms) and **`TunnelEntranceDoor`** (20.00 m × 6.66 m, rolls
straight down, 500 ms, and it is *literally the rover tunnel mouth's door*). The Space Elevator's
door is 4.54 × 2.85 m — a person-sized service hatch, ~1/4.5 of the height wanted.

---

## 1. The Space Elevator door (asked first)

### 1.1 Console test line — run this one first `[NEVER RUN]`

`SpaceElevatorDoor_02` is the cleanest of the three (its panel is axis-aligned; `_01` is rotated, so
its bounding box is a diagonal). Its mesh is authored **40.6 m out in −X and 15.8 m in +Y** from its
own entity origin, so a bare `SetPos` puts the visible panel 43 m away from where you aimed. The
line below cancels that with the entity bbox centre:

```
*r local o = PlaceObjectIn("SpaceElevatorDoor_02", SelectedObj) local c = o:GetEntityBBox():Center() o:SetPos(SelectedObj:GetPos() + point(1500,0,0) - point(c:x(), c:y(), 0)) o:SetScale(100) o:Open() print(o.class, o:GetEntity(), o:GetStateText(), o:GetAnimDuration(), o:GetEntityBBox())
```

Close it again, then clean up:

```
*r o:Close()
```
```
*r DoneObject(o)
```

Every name in that line is verified present in the 1.1.0.403908 tree: `PlaceObjectIn`
(`Lua/_fixup.lua:31-34`, resolves its 2nd arg through `ResolveMap`, which accepts a game object —
`CommonLua/LuaExportedDocs/Game/realm.lua:92`), `PlaceObject` (`CommonLua/Core/classes.lua:1589`),
`box:Center` (`CommonLua/LuaExportedDocs/Global/box.lua:168`), `GetEntityBBox` (`GameObject.lua:404-407`),
`SetScale` (`:1007-1012`), `GetAnimDuration` (`:1023-1027`), `Open`/`Close`/`GetStateText`
(`CommonLua/Classes/Door.lua:15-36`), `DoneObject` (`classes.lua:1622`). `SelectedObj` is reachable
(`EF-096` lists it OPEN). Keep prints short — no `ConsolePrint` length fact exists in
`docs/agent/facts/`; I looked and found none, so this is untested headroom, not a cleared limit.

### 1.2 What carries it — an entity of its own, not a sub-part

⭐ **The door is its own entity.** `SpaceElevatorDoor_01`, `_02` and `_03` are three separate
entities (`Lua/_EntityData.generated.lua:20614`, `:20623`, `:20632`), each with
`entity.class_parent = "Door"`, each with its own mesh (`Meshes.fpk` →
`SpaceElevatorDoor_0N_mesh.sub_0.hgrm`) and its own animation pair
(`Animations.fpk` → `SpaceElevatorDoor_0N_idle.hgacl`, `SpaceElevatorDoor_0N_opening.hgacl`). It is
**not** a sub-part of the `SpaceElevator` mesh, so the "attach the whole elevator scaled and hidden"
fallback is not needed.

**There is no `DefineClass` for them anywhere in the tree** — and none is needed.
`CommonLua/Classes/EntityClass.lua:46-84` generates a Lua class named exactly after every entity in
`EntityData` that no hand-written class claims, with `__parents = { class_parent }`. So
`g_Classes.SpaceElevatorDoor_02` exists at runtime and inherits `Door`. Same mechanism gives us
`ElevatorSurfaceDoor`, `TunnelEntranceDoor`, `TrainTunnelUniversalDoor`, etc.

**How vanilla attaches and triggers it.** Not from `SpaceElevator.lua` — that file never mentions a
door. The chain is generic:

1. The **parent entity's spot annotations** carry `chain=`, `waypoint=` and `door=<class>` keys,
   parsed by `GetEntityWaypointChains` (`Lua/Buildings/BuildingWayPoints.lua:21-99`, the `door` key
   at `:63-69`; `ChainTypes` maps the spot names — `Door`, `Doorentrance1/2`, `Doorexit1/2`,
   `Dronedoor`, `Pathpassage` — at `:7-19`).
2. `WaypointsObj:BuildWaypointChains` places the named door class and attaches it to the building:
   `PlaceObjectIn(chain.door, map)` → `CopyColorizationMaterial(self, door)` → `self:Attach(door)`
   (`BuildingWayPoints.lua:179-188`; the re-attach path is `:546-552`).
3. A unit walking the chain opens and closes it: `door:Open()` … `unit:WaitDoorOpening(door)` …
   `door:Close()` (`BuildingWayPoints.lua:450-476`). `Unit:WaitDoorOpening` sleeps
   `door:TimeToOpen()` (`Lua/Units/Unit.lua:279-280`); the unit's destructor also closes a door it
   left open (`Unit.lua:113-115`).

So the trigger is **a colonist traversing the entrance**, not any elevator-specific code. For us that
is good news: the door object is fully driveable on its own.

### 1.3 States

`Door` (`CommonLua/Classes/Door.lua:1-46`):

| member / call | value | line |
|---|---|---|
| `closedState` | `"idle"` | `Door.lua:7` |
| `openingState` | `"opening"` | `Door.lua:6` |
| `Door:Init` | `SetState(closedState, 0, 0)` | `Door.lua:11-13` |
| `Door:Open` | `SetStateText("opening", 0, 0)`; if already reversing, `+ const.eKeepPhase` | `Door.lua:15-24` |
| `Door:Close` | `SetStateText("opening", const.eReverse + const.eKeepPhase, 0)` | `Door.lua:26-36` |
| `Door:TimeToOpen` | `TimeToAnimEnd() - 1`, or 0 | `Door.lua:38-46` |

⭐ **There is no `closing` state.** Closing is the **same `opening` clip played backwards** with
`eReverse + eKeepPhase`, which is why the pack ships only `_idle` and `_opening` `.hgacl` per door.
`Open`/`Close` are **ref-counted** (`open_counter`), so a close only fires when the last holder lets
go — our code must pair them exactly once each.

`DoorWithFX` (`Door.lua:51-136`) is the same thing plus `PlayFX("DoorOpen"/"DoorClose", …)` and an
optional command-thread variant that sleeps `TimeToAnimEnd()` (`:106-126`). Only two vanilla
subclasses use it: `DomeDoorWithFX` (`Lua/Buildings/Dome.lua:4122-4128`) and `TunnelDoorWithFX`
(`Lua/Buildings/Tunnel.lua:272-274`). **The Space Elevator and Elevator doors inherit plain `Door` —
they are silent.** If the owner wants a hiss/clang, we declare our own class with
`__parents = {"DoorWithFX"}, entity = "<vanilla entity>"` and an `ActionFXSound` of our own; borrowing
a vanilla door's sound would require its `Actor`, which is set per actor class
(`Data/FXPreset/ActionFXSound.lua:5496`, `:5524` for `TunnelEntranceDoor`).

### 1.4 Size — and why it does not fit

Closed (`idle`) bounding box, entity-local, metres (1 m = 100 engine units; `const.GridSpacing =
const.HexWidth = 10*guim = 1000` → `guim = 100`, `Lua/_GameConst.lua:26`):

| entity | panel W | thickness | H (closed) | opening dur | travel |
|---|---|---|---|---|---|
| `SpaceElevatorDoor_01` | 4.54 (bbox 4.13 × 2.42 — panel is rotated ≈62°) | ~0.3 | **2.85** | 500 ms | down 2.81 m |
| `SpaceElevatorDoor_02` | **4.54** | 0.29 | **2.85** | 500 ms | down 2.81 m |
| `SpaceElevatorDoor_03` | **4.54** | 0.35 | **2.84** | 500 ms | down 2.82 m |

It **rolls downward into the threshold** (closed `z 0.30 … 3.15`; during `opening` the box grows to
`z −2.51 … 3.15`, i.e. the leaf sinks 2.81 m — its own height). That is consistent with the owner's
"roll-up shutter with horizontal slats", except the direction is down, not up.

**Verdict for a 6.5 × 13 m arch: NO.** Native aspect 4.54 : 2.85 = **1.59 : 1**; the arch wants
**0.50 : 1**. Uniform scale only, so:

- scale to 6.5 m wide → `SetScale(143)` → **4.1 m** tall (fills 31 % of the arch height);
- scale to 13 m tall → `SetScale(456)` → **20.7 m** wide (3.2× too wide), and the 43 m authoring
  offset scales too, putting the panel ~196 m from the anchor.

Secondary problem already noted: all three panels are authored 40–44 m from their entity origin (they
are modelled in the `SpaceElevator`'s frame — that entity's own box is 86.5 × 77.4 m,
`_EntityData.generated.lua:20583`), so every placement needs the bbox-centre correction of §1.1.

---

## 2. Two corrections to the premise

1. **The dome doors *can* be split.** `DomeDoorEntrance_01`, `DomeDoorEntrance_02`, `DomeDoorExit_01`
   and `DomeDoorExit_02` are **four separate entities**, each `class_parent = "DomeDoorWithFX"`
   (`_EntityData.generated.lua:6303`, `:6321` and neighbours), each with its own mesh and its own
   `_opening.hgacl`. `DomeDoorEntrance_01` occupies `y −4.30 … −0.22`, `DomeDoorExit_01` the mirror
   `y 0.22 … 4.30` — they are the entrance and the exit leaf of the dome service airlock, and either
   can be placed alone. Each leaf: **4.08 m wide × 0.37 m thick**, `z −2.04 … 3.29` while opening
   (500 ms). Still far too small for the arch, and they carry the red/green lamp geometry the owner
   saw, so they read as "dome airlock" wherever you put them.
2. **The Space Elevator's is not the only single-leaf shutter.** Ten vanilla entities are single
   `Door`-class leaves with a working `opening` clip that are bigger than it; four are listed in §3.

---

## 3. The candidate table

Only entities whose `opening` animation was found and whose box decoded consistently are listed;
the full sweep covered all **282** `class_parent = "Door"` entities plus the four `DomeDoorWithFX`,
the one `TunnelDoorWithFX` and the 16 hand-written `Door` subclasses (`Lua/Buildings/MedicalCenter.lua:80-90`,
`Residence.lua:558-572`, `SchoolSpire.lua:1-2`, `SecurityPost.lua:1-2`, `TVStudioWorkshop.lua:1-3`,
`Station.lua:14-27`); 132 decoded, the rest are colonist doors under 3 m and were dropped.

W = clear width, H = closed height, T = thickness, all metres, entity-local, MEASURED (§5).

| class / entity | states | how vanilla triggers it | W × H × T | travel | dur | aspect W:H | fit for 6.5 × 13 m |
|---|---|---|---|---|---|---|---|
| **`ElevatorSurfaceDoor`** (`:10457`) | `idle` / `opening` | waypoint chain on `ElevatorSurface`; `ElevatorBase` re-runs `BuildWaypointChains()` "to attach door" after `ChangeEntity` (`Lua/Buildings/Elevator.lua:699-715`) | **19.46 × 12.93 × 0.63** | straight **down 11.05 m** | 600 ms | 1.51 | ⭐ **best height.** `SetScale(100)` gives exactly the 12.93 m crown; 3× too wide. `SetScale(33)` → 6.42 × 4.27 m |
| `ElevatorUndergroundDoor` (`:10486`) | `idle` / `opening` | same, on `ElevatorUnderground` | 19.46 × 12.93 × 0.63 | down 10.46 m | 600 ms | 1.51 | identical twin; use whichever skins better |
| **`TunnelEntranceDoor`** (`:23796`) | `idle` / `opening` | `class_parent = "TunnelDoorWithFX"` (`Tunnel.lua:272-274`); waypoint chain `Dronedoor` → `tunnel_entrance` (`BuildingWayPoints.lua:17`) on `TunnelEntrance` | **20.00 × 6.66 × 0.80** | straight **down 6.26 m** | 500 ms | 3.00 | ⭐ **the actual tunnel-mouth door**, and the only candidate with its own open/close **sound** (`ActionFXSound.lua:5496`, `:5524`). `SetScale(33)` → 6.6 × 2.2 m |
| `TrainTunnelUniversalDoor` (`:23466`) | `idle` / `opening` | auto-attach on `TrainTunnelUniversal` (`Data/BuildingTemplate/UniversalTunnel.lua:20`) | **28.78 × 5.79 × 0.31** | down 5.74 m | 625 ms | 4.97 | thematically perfect (it *is* a train tunnel door) but the flattest of the set; authored 31.9 m off-origin |
| `MarsAssembly_Door_01`…`_06` (`:14351`+) | `idle` / `opening` | waypoint chain on `MarsAssembly` | 4.02 × 5.38 × 0.26 | slides sideways, box grows to 7.56 m in Y | 500 ms | **0.75** | ⭐ **the only taller-than-wide door in the game.** `SetScale(162)` → 6.5 × 8.7 m. Sideways travel suggests a parting pair — verify in game |
| `DomeDoorEntrance_01` / `DomeDoorExit_01` (`:6303`, `:6321`) | `opening` only | `DomeDoorWithFX`, chain `Doorentrance1/2`, `Doorexit1/2` | 4.08 × ≈2.7 × 0.37 | down ~2.7 m | 500 ms | 1.51 | too small; reads as "dome airlock" |
| `SpaceElevatorDoor_01/02/03` (`:20614`+) | `idle` / `opening` | waypoint chain on `SpaceElevator` | 4.54 × 2.85 × ~0.3 | down 2.81 m | 500 ms | 1.59 | §1.4 — no |
| `DroneHubCP3Door` (near `:10015`) | `idle` / `opening` | chain on `DroneHubCP3` | 4.15 × 2.96 × 0.23 | down 2.84 m | 500 ms | 1.40 | too small |
| `FusionReactorDoor_01/_02` | `idle` / `opening` | chain on `FusionReactor` | 5.82 × 2.72 × 0.20 | down 2.56 m | 500 ms | 2.14 | too small |
| `TrainStationDoorCCP3`, `…_02`, `TrainStationLargeDoor1-4CCP3` (`Station.lua:14-27`, `_EntityData…:23398`+) | `idle` / `opening` | hand-written `Door` subclasses, auto-attached to `TrainStationCCP3` / `…Large` | 3.9 × 3.3 × 0.15 | **swings** (box grows in the second axis) | 625 ms | 1.18 | too small; swing not slide |
| `PeakNodeCCP2Door` | `idle` / `opening` | chain | 4.04 × 2.37 × 0.14 | in place (box unchanged) | 625 ms | 1.70 | too small |

**Not doors, checked and excluded.** Shuttle hub — `JumperShuttleHub.lua`, `ShuttleHub.lua` have no
door entity and no `opening` state; the hangar reads as a static mesh plus the shuttle's own
`Shuttle_landing`/`takeOff` clips. Rockets — `Rocket_disembarkStart/Idle/End` are disembark
sequences on the whole rocket, and `UniversalPod.lua:6` exposes `HasDoorAnim` as a **template flag**,
not an attachable door entity. Space Elevator cabin — `SpaceElevatorCabin` has no door states.
Garage / rover door — `Cardoor` exists only as a `ChainTypes` spot name for the drone factory exit
(`BuildingWayPoints.lua:14`), with no door entity behind it. `SpaceportDoor` exists as an entity
(`class_parent = "Door"`) but ships **no animation file at all** — it is a static prop; do not use it.
`Blinds` / `SolarPanel` / `StirlingGenerator` have `opening`/`closing` states but are panels, not doors.

---

## 4. Attach, scale and animation — what the engine guarantees

**1. `SetState` on an attached object plays. SOURCE, and this mod already relies on it.** An
attached door is an ordinary `Object` with `ComponentAnim`; vanilla places it and attaches it
(`BuildingWayPoints.lua:179-188`) and then drives its state from outside
(`door:Open()` → `SetStateText`, `Door.lua:15-24`), which is `SetState` by name. This mod's own dev
mod does the same on attached visuals: `PlaceObjectIn(...)` → `self:Attach(visual,
self:GetSpotBeginIndex("Origin"))` → `visual:SetState(state)` guarded by `HasState`
(`tools/devmods/train_hub/Code/20_TrainHub.lua:1046-1071`, `:1281`).

**2. Scale composes down the attach chain, and the child can carry its own. SOURCE.**
`GetWorldScale` is documented as "the final scaling of an object, that take into account **parent
object scale and spot's scale to which the object is attached**" (`GameObject.lua:1015-1019`). The
dev mod already sets `SetScale` on an attached child (`20_TrainHub.lua:1071`,
`reactor_scale = 75`). So attaching a door to a portal and scaling the door alone is the supported
shape.

**3. Scale is uniform. SOURCE (absence proved).** `SetScale(scale)` takes one integer
(`GameObject.lua:1007-1012`), 100 = native. `grep -rn "ScaleX\|SetScaleXYZ\|NonUniform\|SetMirrored"`
over `CommonLua/LuaExportedDocs` returns **zero** hits, against 2 hits for `SetScale`/`GetScale` in
the same file — the presence side is non-empty, so the absence is real for the exported API. **A
6.5 × 13 arch cannot be filled by scaling a 1.5:1 door.**

**4. Scale does not change animation timing. INFERRED, worth one in-game check.** Every timing
export is in units of time and names only speed modifiers as inputs: `GetAnimDuration`
(`:1023-1027`), `TimeToAnimEnd` "Modified by animation speed modifier!" (`:1038-1041`),
`SetAnimSpeedModifier` (`:205-210`), `SetAnimSpeed(channel, speed, time)` (`:1249-1255`). No scale
term appears in any of them. The **travel** does scale — the animation is authored in mesh space, so
a `SetScale(200)` `ElevatorSurfaceDoor` retracts 22.1 m instead of 11.05 m, which matters because it
sinks below the terrain.

**5. `GetEntityBBox` excludes scale — multiply it yourself.** "the bounding box of the current state
of the object with mirroring applied, but **without applying object's position, scale and
orientation**" (`GameObject.lua:403-407`). World size = bbox × scale ÷ 100. It is also **per state**,
so reading it during `opening` returns the swept box, not the closed panel — read it in `idle`.

**6. Waiting for the animation to end from a game-time thread.** Vanilla's exact form is
`Sleep(self:TimeToAnimEnd())` (`Door.lua:113`, `:124`, inside `DoorWithFX:DoOpen`/`DoClose`, which
run as commands). For a caller that is not the door, vanilla uses
`unit:WaitDoorOpening(door)` → `Sleep(door:TimeToOpen())`, where `TimeToOpen` is
`TimeToAnimEnd() - 1` while the door is held open (`Door.lua:38-46`, `Unit.lua:279-280`). Our
train-approach hook should be:

```lua
CreateGameTimeThread(function(door)
    door:Open()
    Sleep(door:TimeToOpen())
    -- train passes
    door:Close()
end, door)
```

⛔ `CreateGameTimeThread` **defers** — the body does not run before the creating statement continues
(`EF-029`, MEASURED). Do not read the door's state on the next line.
`PlayState(state, count)` (`GameObject.lua:971-977`) also sleeps the calling thread, but it takes a
loop count and the door API is the safer match. `IsAnimLooping(channel)` (`:1345-1349`) can confirm
`opening` is one-shot; that is **UNMEASURED** — check it in the §1.1 paste.

**7. Ref-counting.** `open_counter` (`Door.lua:8`, `:16`, `:27`) means N opens need N closes. Six
portals each holding their own door object avoids the issue; one shared door driven by six trains
does not.

---

## 5. How the sizes were measured (so they can be falsified)

`Packs\BinAssets.fpk` → `entities.dat` (FLPK entry, zstd-wrapped, 14,168,326 B decompressed) is the
compiled entity-spec database. Its schema is readable because `Packs\CommonAssets.fpk` ships 32
uncompiled `.entjson` twins of the same structure — e.g. `Entities/WayPointBig.entjson` gives
`boxMin`, `boxMax`, `bsCenter`, `bsRadius` as named fields.

**Record layout** (int32 little-endian, immediately after each state's `Animations/<entity>_<state>.hgacl`
path string and a short zero/flag preamble):

```
duration_ms, bsCenter.x, bsCenter.y, bsCenter.z, bsRadius,
boxMin.x, boxMin.y, boxMin.z, boxMax.x, boxMax.y, boxMax.z,
sizeX (= maxX-minX), sizeY (= maxY-minY)
```

**Calibration.** Decoded against `WayPointBig`, whose `.entjson` states
`boxMin [-129,-131,-345] / boxMax [375,119,1305] / bsCenter [123,-6,480] / bsRadius 857`. The
binary yields `min (-383,-131,-345) / max (121,119,1305) / center (-131,-6,480) / radius 857` and
`sizeX 504 = 121-(-383)`, `sizeY 250 = 119-(-131)` — y, z, centre, radius and both derived sizes
match the JSON exactly; only x is offset (the shipped mesh differs from the dev-tools twin).

**Self-checks applied to every row.** The decoder accepted a block only when
`bsCenter == (boxMin+boxMax)/2` within 1 unit on all three axes, `sizeX == maxX-minX`,
`sizeY == maxY-minY`, and `0 < duration < 20000 ms`. Rows that failed are reported as "no box"
rather than guessed — the first pass without the duration check produced obvious nonsense
(`TrainStationDoorCCP3` at 204 m) by running into a neighbouring record, and the check kills it.
Independent corroboration per entity: the durations recovered (33/41/66 ms for `idle`, 500/600/625 ms
for `opening`) line up with the `Animations.fpk` file list, which contains exactly one `_idle` and
one `_opening` clip per door and no `_closing` clip — matching `Door:Close`'s reverse-play
(`Door.lua:26-36`) with no assumption.

**Falsifier.** `GetEntityBBox()` in game on a placed instance must return the same numbers
(§1.1's print does this for `SpaceElevatorDoor_02`: expect roughly
`box(-4074, 1351, 30, -4045, 1805, 315)`).

---

## 6. Console lines for the top candidates `[NEVER RUN]`

One line each, paste-safe, `*r` prefix because each is multi-statement. `point(1500,0,0)` = 15 m east
of the selected object. Each leaves the object in `o` so the follow-up lines work.

**A — `ElevatorSurfaceDoor` at native scale (the 12.93 m crown):**
```
*r local o = PlaceObjectIn("ElevatorSurfaceDoor", SelectedObj) local c = o:GetEntityBBox():Center() o:SetPos(SelectedObj:GetPos() + point(1500,0,0) - point(c:x(), c:y(), 0)) o:SetScale(100) o:Open() print(o.class, o:GetStateText(), o:GetAnimDuration(), o:IsAnimLooping(), o:GetEntityBBox())
```

**B — `ElevatorSurfaceDoor` scaled to 6.5 m wide (`SetScale(33)` → 6.42 × 4.27 m):**
```
*r local o = PlaceObjectIn("ElevatorSurfaceDoor", SelectedObj) local c = o:GetEntityBBox():Center() o:SetPos(SelectedObj:GetPos() + point(3000,0,0) - point(c:x()*33/100, c:y()*33/100, 0)) o:SetScale(33) o:Open() print(o.class, o:GetScale(), o:GetWorldScale(), o:GetAnimDuration())
```

**C — `TunnelEntranceDoor` (the rover tunnel mouth, has sound):**
```
*r local o = PlaceObjectIn("TunnelEntranceDoor", SelectedObj) local c = o:GetEntityBBox():Center() o:SetPos(SelectedObj:GetPos() + point(4500,0,0) - point(c:x(), c:y(), 0)) o:SetScale(100) o:Open() print(o.class, o:GetStateText(), o:GetAnimDuration(), o:GetEntityBBox())
```

**D — `MarsAssembly_Door_01` (the only tall-aspect door, scaled to 6.5 m wide):**
```
*r local o = PlaceObjectIn("MarsAssembly_Door_01", SelectedObj) local c = o:GetEntityBBox():Center() o:SetPos(SelectedObj:GetPos() + point(6000,0,0) - point(c:x()*162/100, c:y()*162/100, 0)) o:SetScale(162) o:Open() print(o.class, o:GetScale(), o:GetAnimDuration(), o:GetEntityBBox())
```

**E — `TrainTunnelUniversalDoor` (the vanilla train-tunnel door):**
```
*r local o = PlaceObjectIn("TrainTunnelUniversalDoor", SelectedObj) local c = o:GetEntityBBox():Center() o:SetPos(SelectedObj:GetPos() + point(7500,0,0) - point(c:x(), c:y(), 0)) o:SetScale(100) o:Open() print(o.class, o:GetStateText(), o:GetAnimDuration(), o:GetEntityBBox())
```

**Close / re-open the last one placed:**
```
*r o:Close()
```

**Cleanup — sweep every loose door on the map:**
```
*r local n = 0 MapForEach("map", "Door", function(d) if not d:GetParent() then DoneObject(d) n = n + 1 end end) print("removed", n)
```

`MapForEach` is reachable from the sandbox (`EF-096` lists it OPEN); the `GetParent()`
(`GameObject.lua:283`) guard spares
every door that is attached to a real building. If that guard is not trusted, delete by name instead
and check the count.

---

## 7. Recommendation — the top two

**1. `ElevatorSurfaceDoor` — take it, and move the portal to it.** It is the only vanilla door whose
**height already is the owner's number**: 12.93 m closed, against a 13 m crown, at `SetScale(100)`.
It is a single slab, it retracts **straight down into the ground** (11.05 m in 600 ms) which is
exactly "opens as the train approaches, closes behind it", it is only 0.63 m thick so it sits flush
in an arch face, and its geometry is **centred on its own entity origin in X** (`−9.72 … +9.74`) with
only a 3 m offset in Y — alone among the large doors, it needs almost no placement correction. The
one cost is width: 19.46 m against 6.5 m. Two ways out, both for the owner to judge by eye:
(a) **widen the portal mouth to ~19.5 m** and keep 13 m of height — the train is 4 m wide, so a
19.5 m mouth reads as a freight portal rather than a doorway; or (b) keep 6.5 m and let the door's
outer thirds be **buried inside the arch masonry**, which works because the panel is flat and the
travel is vertical — nothing swings out into the rock. ⚠️ At scale ≠ 100 the retraction scales with
it: at `SetScale(33)` the door drops only 3.6 m, so the mouth must be no taller than that or the
"open" pose still shows a closed slab. Silent (plain `Door`); a `DoorWithFX` subclass of our own can
add sound.

**2. `TunnelEntranceDoor` — take it if the arch must stay 6.5 m wide.** It is the rover tunnel's own
door, so it already *belongs* on a tunnel mouth: same downward roll, 20.00 × 6.66 m, 500 ms, and it
is the **only** candidate that ships its own `DoorOpen`/`DoorClose` sounds (`TunnelDoorWithFX`,
`Tunnel.lua:272-274`; `ActionFXSound.lua:5496`, `:5524`) — free audio, no FX preset of ours. At
`SetScale(33)` it is 6.6 m wide × 2.2 m tall, which fits the 6.5 m width exactly and fills the bottom
sixth of a 13 m arch: read that as **a door in a gateway**, not as a door filling the gateway, and it
is arguably the better look for a 13 m arch anyway. Cost: authored 27.7 m off-origin in Y, so every
placement needs the bbox-centre correction.

**Third, only if the arch shape is negotiable toward tall-and-narrow:**
`MarsAssembly_Door_01`, the one vanilla door taller than it is wide (4.02 × 5.38, aspect 0.75).
`SetScale(162)` gives 6.5 × 8.7 m — the right width and two-thirds of the height, the closest any
vanilla asset gets to the requested proportion. Its opening motion is **sideways**, and the swept box
grows in both Y directions (`−2.04…1.98` closed → `−3.70…3.86` open), which most likely means a
**parting pair**, not a single leaf — line D of §6 settles that in one look.

**Do not pursue:** the Space Elevator doors (4.54 × 2.85, §1.4), `SpaceportDoor` (no animation ships),
shuttle hub / rocket / garage (no door entity exists, §3).

---

## 8. Owed

- ⛔ **[NEVER RUN] — nothing here has been seen in game.** §6 A–E is one sitting, ~5 minutes: place
  five doors in a row 15 m apart in front of the selected object, screenshot, pick one.
- The five reads that only the game can answer: (a) is `ElevatorSurfaceDoor` one slab or two halves;
  (b) is `MarsAssembly_Door_01` a single leaf or a pair; (c) does `IsAnimLooping()` return false for
  `opening`; (d) does the panel z-fight or clip the terrain when scaled; (e) which of these is the
  shutter the owner actually photographed — §6's five lines answer all five at once.
- A behaviour change on the train hub needs an owner ruling recorded for this mod before any of this
  is built (`CLAUDE.md` header).
