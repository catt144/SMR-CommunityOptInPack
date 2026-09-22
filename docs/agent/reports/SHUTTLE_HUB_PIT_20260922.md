# The Shuttle Hub's pit as the train hub's drone hangar — survey (desk, 2026-09-22)

**Question (owner).** Use the Shuttle Hub's **pit** — the round shaft the shuttles rise out of, with
its white rim and posts — as the train hub's repair-drone hangar, so Wasps launch from and land into
a pit instead of appearing beside a recoloured drone recharger. **The tower is far too big and
unwanted.** Which route is possible?

**Method.** Desk only. **The game was not launched; every console line below is `[NEVER RUN]`.**

- Lua citations are `<path>:<lines>` under `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908\Src\`.
- Game data is the Steam app **"Project Spark"** at `A:\SteamLibrary\steamapps\common\Project Spark`.
- ⭐ Sizes are **MEASURED** from `Packs\BinAssets.fpk` → `entities.dat` by the method of
  `VANILLA_DOOR_ENTITIES_20260922.md` §5, decompressed in memory with `tools/flpk_extract.py`'s
  `parse_table`. **Nothing was extracted to disk.** The decoder was re-validated here before use:
  it re-derives `ElevatorSurfaceDoor` as **19.46 × 0.63 × 12.93 m**, the door survey's published
  figure, `SpaceElevator` as **86.48 × 77.44 m**, and `WayPointBig` exactly against its shipped
  `.entjson` twin. §7 states the layout and the falsifier.
- **No writes anywhere but this file.**

⚠️ A report is not authority. Changing the train hub needs an owner ruling recorded for this mod
(`CLAUDE.md` header, `FIX_POLICY.md` §4).

---

## 0. The one-paragraph answer

**There is no pit entity.** `ShuttleHub`, `ShuttleHubCP3` and `JumperShuttleHub` are the only three
shuttle-hub entities in the game, and each is **one entity, one mesh** (3 LODs × 2 sub-meshes, no
animation files at all). The pit and the tower are the same mesh, so "attach the pit, hide the
tower" has nothing to attach. But the mesh **does** reach **40.22 m below its own origin**
(`ShuttleHub`, measured), which is the shaft, and the tower is the 38.80 m above it.

The mechanism that lets that shaft be seen is an **`eTerrainHole` surface authored into the
entity** — one of the engine's surface types, present by name in `Mars.exe` in the same enum as
`eHexShape`, `eCollision` and `eSelection`, which **this mod's own entity already declares 796 of**
in `tools/devmods/train_hub/Entities/SMROptInTrainHub6.entjson`. So **route 1 — our own pit,
modelled into the hub's floor plate, with `eTerrainHole` triangles over its mouth — is the route
that is actually open to us**, and it needs no vanilla asset at all.

Two more things the owner will want: the vanilla shuttle's rise is **the shuttle's own animation**
(`Shuttle_takeOff`), not the hub's — so a pit launch is animated by the *thing that launches*; and
the Wasp drone **already ships three unused shaft states** — `metalMineEnter`, `metalMineExit`,
`metalMineIdle`, with a swept box reaching **26.73 m below the drone's origin** and no Lua anywhere
in the game driving them. That is a drone rising out of a shaft, already authored, free.

---

## 1. How the ShuttleHub is assembled

### 1.1 The entities — three, and only three

`grep ShuttleHub Lua/_EntityData.generated.lua` returns exactly three records:

| entity | line | `class_parent` | template using it |
|---|---|---|---|
| `JumperShuttleHub` | `_EntityData.generated.lua:13099` | `BuildingEntityClass` | `Data/BuildingTemplate/JumperShuttleHub.lua:25` |
| `ShuttleHub` | `:19470` | `BuildingEntityClass` | `Data/BuildingTemplate/ShuttleHub.lua:32` |
| `ShuttleHubCP3` | `:19481` | `BuildingEntityClass` | `entity2` of **both** templates (`ShuttleHub.lua:33`, `JumperShuttleHub.lua:26`) |

⭐ **No `ShuttleHubPit`, `_Base`, `_Hangar` or any other part entity exists.** `Meshes.fpk` carries
exactly 6 files per hub — `<entity>_mesh.sub_0/1.hgrm` for LOD 0, `.1.` for LOD 1, `.2.` for
LOD 2 — and `Animations.fpk` carries **zero** files whose name contains `ShuttleHub`. The hub is a
static mesh; nothing about it moves.

### 1.2 Measured bounding boxes ⭐

Entity-local, metres (1 m = 100 engine units; `const.GridSpacing = const.HexWidth = 10*guim = 1000`
→ `guim = 100`, `Lua/_GameConst.lua:26`). One box block decodes per hub entity, and since these
entities have no animation states, that block **is** the static mesh box.

| entity | footprint X × Y | z range | total height |
|---|---|---|---|
| **`ShuttleHub`** | **28.15 × 23.33 m** | **−40.22 … +38.80 m** | 79.02 m |
| **`ShuttleHubCP3`** | **24.40 × 24.39 m** (round) | **−39.05 … +38.94 m** | 77.99 m |
| **`JumperShuttleHub`** | **28.15 × 22.75 m** | **−39.06 … +38.80 m** | 77.86 m |

So roughly **half the asset is below the origin.** The tower is the +38.8 m the owner does not want;
the pit is the −40.2 m.

For scale, the same sweep over all 1 507 entities whose box decodes puts the shuttle hubs in a clear
family of buildings with real below-ground geometry:

| entity | min z | max z |
|---|---|---|
| `ElevatorSurface` (Below & Beyond) | **−124.49 m** | +26.59 m |
| `MoholeMineLights` | −119.66 m | +3.87 m |
| `CoreHeatConvector` | −73.87 m | +8.00 m |
| `Sinkhole` | −70.24 m | +1.67 m |
| `MagneticFieldGenerator` | −69.37 m | +17.13 m |
| `WaterExtractor` | −50.00 m | +7.42 m |
| **`ShuttleHub`** | **−40.22 m** | +38.80 m |
| `MetalsExtractor` / `MetalsExtractorElevator` | −26.80 / −26.60 m | +6.81 / +2.47 m |
| `SolarPanel`, `DroneHub` (ordinary buildings) | **0.00 m** | — |

⚠️ In that sweep, an **animated** entity's extreme is the swept box of some state, not static
geometry (`Drone` reads −26.72 m because of its `metalMine*` states, §5.3). The shuttle hubs have no
animations, so their −40 m is the mesh.

### 1.3 Spots — decoded, with one open discrepancy

The spot table decodes as 20-byte records against a global name table also in `entities.dat`
(§7). The decoder is confirmed by `TrainStationCCP3`, which yields exactly the spot names this mod
already uses in game (`Trackconnector1/2`, `Trackdirection1/2`, `Ramparrive2/3`, `Rampdepart1/2`,
`Stop1/2`, `Spawn1/2`, `Sign1/2`, `Box10`), and by spot name id 190 = `Out`, which occurs on
**exactly** the three shuttle-hub entities and nowhere else in the file.

| entity | decoded spots |
|---|---|
| `ShuttleHub` | `Autolight`, `Construction`, **`Out`**, `Dronein`, `Resourcepile2`, `Resourcepile3`, `Top`, `Workdrone` × 6, `Lifesupportgrid` × 4, `Terminal` |
| `JumperShuttleHub` | the same 18 |
| `ShuttleHubCP3` | the above plus `Petlay` × 2, **`Out2`**, `Workdrone002`, minus `Autolight` |

⛔ **Unresolved, and it must be settled in game before anyone builds on the spot names.** The decode
finds **`Out` but no `In`**, while `ShuttleHubBase.landing_spot_name = "In"` (`ShuttleHub.lua:1543`)
and `skin_to_landing_info` names `land_spot = "In"` / `"In2"` (`:1578-1605`). Two readings:

- the decode is right — and that is exactly the case Relaunched's own added guard describes:
  *"Buildings whose entity is missing landing spots would otherwise make shuttles wait forever for a
  free spot"* (`ShuttleHub.lua:99-108`, `GetFallbackLandingSpot`, whose slot is `self:GetPos()`), with
  the same guard again at `:581`; or
- the decode misses a record — and the falsifier is `ShuttleHub.lua:1700`,
  `local to_spot = self.landing_slots[1].pos - self:GetPos()`, which is **unguarded** and would
  error on a hub with no landing slots.

§6 line **P1** settles it in one paste. Nothing in this report's verdicts depends on it.

### 1.4 What actually moves — the shuttle, not the hub

There are no `attaches` or `PlaceObj` calls in `Init`/`GameInit` that build the hub out of parts, and
no `attaches` field in either building template. The hub is inert. The motion the owner is looking
at belongs to the **shuttle**:

```
ShuttleHubBase:ShuttleLeadIn   ShuttleHub.lua:1609-1639
  spot_idx = self:GetSpotBeginIndex(data.land_spot)   -- "In" / "In2"
  … fly to the spot with SetPos(pos, t) + SetAcceleration …
  self:Attach(shuttle, spot_idx)
  shuttle:SetAnim(1, data.land_anim, 0, 0)            -- "landing" / "landing2"
  Sleep(shuttle:TimeToAnimEnd())

ShuttleHubBase:ShuttleLeadOut  ShuttleHub.lua:1641-1656
  spot_idx = self:GetSpotBeginIndex(data.take_off_spot)  -- "Out" / "Out2"
  self:Attach(shuttle, spot_idx)
  shuttle:SetAnim(1, data.take_off_anim)              -- "takeOff" / "takeOff2"
  Sleep(shuttle:TimeToAnimEnd())
  shuttle:Detach()
  shuttle:SetPos(self:GetSpotPos(spot_idx))
```

The skin table that picks those names is `skin_to_landing_info` (`ShuttleHub.lua:1578-1605`), keyed
by shuttle class then by the hub's **current entity**. `Animations.fpk` ships exactly the clips it
names: `Shuttle_landing`, `Shuttle_landing2`, `Shuttle_takeOff`, `Shuttle_takeOff2`,
`Shuttle_fly`, `Shuttle_idle` — and nothing for the hub.

⭐ **So the rise out of the pit is authored into the shuttle's own clip**, played while the shuttle
is attached to a hub spot. The pattern for a pit launch is therefore: *the launching unit carries
the vertical move*, either as an animation or, as the generic `ShuttleLanding:ShuttleLeadIn` /
`ShuttleLeadOut` do it (`ShuttleHub.lua:267-330`), as scripted `SetPos(pos, 1000)` +
`SetAcceleration(±1500)` over two 1-second legs.

---

## 2. How the pit renders below ground

### 2.1 What the terrain does under a building: it is FLATTENED, never holed

`Building:RestoreTerrain` (`Building.lua:1522-1545`) flattens under the build shape
(`FlattenTerrainInBuildShape` → `terrain.SetHeightCircle`, `Lua/Construction/Construction.lua:2474-2488`,
shape from `Building:GetFlattenShape` → `GetBuildShape`, `Building.lua:648-650`), and
`PlaceConstructionSite` flattens again at placement (`ConstructionSite.lua:2221-2222`). The shuttle
hub feels this from the other side: `ShuttleHubBase:GameInit` carries the comment *"hack, move
landing pos a bit away, so that shuttles don't fly vry high when returning due to **shuttle hub's
imprint on the height grid**"* (`ShuttleHub.lua:1699-1701`).

**No Lua anywhere in the tree punches a terrain hole from an object.** The only `TerrainHole` writes
are the editor's cave brush (`terrain.SetTerrainHolesBaseGridRect` / `ClearTerrainHolesBaseGrid`,
`CommonLua/Editor/XEditor/XCaveBrush.lua:28-30`, `:122`), which is a map-authoring tool, not a
building.

### 2.2 The mechanism: an `eTerrainHole` surface on the entity ⭐

`EntitySurfaces.TerrainHole` is read in exactly three places, all of them consequences rather than
the cause:

| site | what it decides |
|---|---|
| `Building.lua:1598` | a building with a `TerrainHole` **or** `Height` surface is **not sunk and tilted** on demolish |
| `ConstructionSite.lua:947-950` | `progress_below_terrain` — the construction clip plane starts **below** terrain instead of at the object's own z (`SetClipPlaneByProgress`, `CommonLua/gamelib.lua:779-808`) |
| `ConstructionSite.lua:1163` | such a site gets **no resource stockpile** (there is no ground to put it on) |

The carving itself is C-side. The name is in the engine: `Mars.exe` (and `MarsDebug.exe`) contain
the literal string **`eTerrainHole`** in one block with the rest of the surface enum —

```
eCollision  eHeight  eWalk  eBuild  eHexShape  eTerrainHole  eSelection  eRoad  eTerrain
ePassageForbid  ePassageEntrance  eService  eNumUsed  eBlockPass  eFree1  eFlat  eFree3
eMinHeight  eClearRoad  eNumAll  eMaxHeight
```

— and those are the same tokens an entity's `.entjson` uses as its surface `type` (§3). The terrain
renderer independently supports holes (the cave brush above writes a *terrain holes base grid*).

**Verdict on mechanism (INFERRED, one probe settles it):** the pit is a hole in the terrain grid
carved from an `eTerrainHole` surface authored into the `ShuttleHub` mesh, over the pit mouth, with
the shaft modelled below z = 0. The behaviour of the whole family in §1.2 — Mohole, Sinkhole, the
extractors, the Below & Beyond `ElevatorSurface` — is the same shape of asset.

### 2.3 The probe that turns the inference into a fact

`HasAnySurfaces` accepts an **entity name string** (`CommonLua/Editor/editor.lua:435-436` calls it
that way), and `GetEntitySurfacesBBox(entity, request_surfaces, fallback_surfaces, state_idx)` is
exported (`CommonLua/LuaExportedDocs/Game/LuaExports.lua:221-228`) — so the second line also hands
back **the pit mouth's exact size and depth**, which no desk method here can reach. See §6 **P2**.

---

## 3. Can a mod entity use the same mechanism? — YES, and we already use the pipeline

⭐ **This mod hand-authors its entity as an `.entjson`, and that file already carries 796 surfaces.**
`tools/devmods/train_hub/Entities/SMROptInTrainHub6.entjson` (152 870 bytes) has, under
`$value.meshDescriptions[1]`:

| field | value |
|---|---|
| `lods[1].boxMin` | `[-8000.0, -7186.35, 0.0]` — **the hub currently stops dead at z = 0** |
| `lods[1].boxMax` | `[8000.0, 7186.35, 2074.99]` — 160 × 143.7 × 20.7 m |
| `attaches` | 25 spots (`Box1` × 6, `Top`, `Trackconnector1‑6`, `Trackdirection1‑6`, …) |
| `surfaces` | **796 triangles**: `eHexShape` × 504, `eCollision` × 258, `eSelection` × 34 |

A surface record is literally three points and a type:

```json
{"points": [[-2911.44, -1189.33, 100.0], [-3314.14, -1353.83, 100.0], [-3214.66, -1575.54, 100.0]],
 "type": "eCollision"}
```

`eTerrainHole` is a peer of `eHexShape` in the same engine enum (§2.2). So adding a pit is, in file
terms: **model the shaft below z = 0 in the mesh, and add `eTerrainHole` triangles covering the pit
mouth.** No new Lua class, no new persisted name, no vanilla asset.

What already follows for free once the surface is there:

- our template's `demolish_sinking = range(5, 15)` stops applying — `Building:Destroy` skips the
  sink-and-tilt for any entity with a `TerrainHole` or `Height` surface (`Building.lua:1598`);
- the construction animation builds the hub **from below the terrain up** instead of from its own
  base (`ConstructionSite.lua:947-950`), which is the correct look for a building with a shaft;
- no construction resource stockpile is placed (`ConstructionSite.lua:1163`).

The mod-entity checker only *requires* `HexShape`, `Selection` and `Collision`, and only *suggests*
`Walk` (`Lua/Mod.lua:111-135`) — it neither demands nor forbids `TerrainHole`, so nothing in the mod
verification path blocks it. The importer side is the same story: the Scene Importer assigns a
`SurfaceType` per mesh node, its choice list being `table.keys(const.SurfaceTypes)`, auto-matched
from the node's name (`CommonLua/Libs/DevToolsPublic/SceneImport.lua:2172-2211`, `:3545`, `:4364`).

Two cautions, both for the asset pass, neither a blocker:

1. **Keep the `eHexShape` triangles as they are.** The footprint, the connector line radii and this
   mod's own `line_radii` computation all read the hex outline
   (`20_TrainHub.lua:172` uses `GetEntityOutlineShape`), and a hole in the middle of the footprint
   must not become a hole in the hex shape.
2. **The hole triangles must cover only the pit mouth.** The rest of the footprint still wants the
   terrain flattened under it (`Building.lua:1539-1541`).

**INFERRED, not measured:** that the engine honours a `TerrainHole` surface supplied by a *mod*
entity exactly as by a shipped one. The evidence that it honours mod surfaces at all is this mod's
own `eHexShape` set, which already drives `GetEntityOutlineShape` in game (proven in the hub's
sitting 2). §6 **P3** checks `TerrainHole` specifically.

---

## 4. Wasp launch and landing — what the source carries

### 4.1 The class

`FlyingDrone` (`Lua/Units/FlyingDrone.lua:11-51`) — display name "Wasp Drone" (`:20`), entity
`DroneJapanFlying` (`:16`), `__parents = { "Drone", "FlyingObject", "FlyingDroneAutoresolve" }`.
`hover_height = 7*guim`, `min_hover_height = 1*guim`, `move_speed = 16*guim`, `auto_landing = true`.

| call | body | line |
|---|---|---|
| `FlyingDrone:TakeOff` | `SetState("fly")`; `ClearGameFlags(gofSpecialOrientMode)` | `:114-117` |
| `FlyingDrone:LandingEnd` | `SetState("idle")`; `SetGameFlags(gofSpecialOrientMode)`; `SetAcceleration(0)` | `:124-132` |
| `FlyingDrone:IsLanded` | `GetGameFlags(gofSpecialOrientMode) ~= 0` | `:91-93` |
| `FlyingDrone:Land` | drops to **`self:GetMap():GetHeight(pos)`** then `LandingEnd` | `:181-201` |

⛔ **Vanilla landing always ends at the terrain height**, and free flight is planned over a clone of
the terrain height grid (`Lua/Flight.lua:285-318`, `terrain.GetHeightGrid`). So the drone AI will
never, of its own accord, put a Wasp below ground — a pit descent has to be driven by us, the way
the shuttle's is (§1.4). It also means a Wasp released at a pit-bottom spot and then handed to
`Goto` will be pulled back to terrain level; the hand-over has to happen **at the rim**, not at the
bottom.

### 4.2 ⭐ The Wasp already has shaft states, and nothing uses them

The `DroneJapanFlying` entity ships **47** animation states. Three of them are a shaft sequence:

| state | clip | measured |
|---|---|---|
| `metalMineEnter` | `DroneJapanFlying_metalMineEnter.hgacl` (3 729 B) | — |
| `metalMineExit` | `DroneJapanFlying_metalMineExit.hgacl` (2 489 B) | — |
| **`metalMineIdle`** | `DroneJapanFlying_metalMineIdle.hgacl` (1 309 B) | **2 000 ms, box z −26.73 … +2.89 m**, footprint 2.43 × 2.16 m |

By comparison `fly` and `idle` both sit at z +0.24 … +1.83 m. So the `metalMine*` family's swept box
reaches **26.73 m below the drone's origin**: a drone descending into, hovering in, and rising out of
a shaft. `Drone` (the ordinary one) carries the same three states.

⭐ **`grep -rn "metalMine\|MetalMine" --include=*.lua` over the whole tree returns nothing.** No Lua
drives them; they are shipped, unused assets. They are settable by name the way this mod already
sets states on attached visuals (`20_TrainHub.lua:1046-1054`, `visual:SetState(state)` guarded by
`HasState`). §6 **P4** looks at all three.

### 4.3 What this mod has today

`SMROptInTrainHubBase:SpawnDrone` (`20_TrainHub.lua:997-1012`) drops the drone at
`GetRandomPassableAroundOnMap` between the longest connector line and the 15-hex work radius — it
does not use the pad. The pad itself is `InitHubLaunchPad` (`:1270-1298`): one
`RechargeStationPlatform` attached at hex (1,1) with `launch_pad_offset()` (`:1022-1026`),
deliberately with no `NotBuildingRechargeStation` behind it so it cannot charge, recoloured with
`Building.SetPalette`. The brief that owns this is
`docs/agent/prompts/Train_Hub_Project/03_TRAIN_HUB_DRONES_high.md` — owner, 2026-09-19: *"They
launch from and return to a pad, never from nothing"*, the pad being the vanilla recharge platform
model. **A pit replaces that pad; it does not change any other line of that brief.**

---

## 5. Attaching a vanilla hub entity under ours — the facts

Carried forward from `VANILLA_DOOR_ENTITIES_20260922.md` §4, still the governing facts:

1. **Scale is uniform.** `SetScale(scale)` takes one integer, 100 = native
   (`CommonLua/LuaExportedDocs/Game/GameObject.lua:1007-1012`); no non-uniform export exists.
   A `ShuttleHub` scaled to make its 38.8 m tower acceptable also shrinks its 40.2 m pit by the same
   factor. **Scale cannot separate the tower from the pit.**
2. **Scale composes down the attach chain** (`GetWorldScale`, `:1015-1019`), and this mod already
   sets `SetScale` on an attached child (`20_TrainHub.lua:1071`, `reactor_scale = 75`).
3. **`GetEntityBBox` excludes scale** (`:403-407`); world size = bbox × scale ÷ 100.

### 5.1 Attaching as a decoration avoids the footprint and the class — PROVEN HERE

This mod already attaches a **vanilla building entity** as a pure decoration:
`InitHubReactorVisual` (`20_TrainHub.lua:1058-1074`) places a `ShapeshifterAutoAttach`,
`ChangeEntity("FusionReactor")` (with `SMROptInTrainHubReactor` preferred when present), clears
`efCollision + efApplyToGrids + efWalkable + efSelectable`, attaches at `Origin`, offsets, angles and
scales it, and `DeleteOnLoadGame`s it. With `efApplyToGrids` cleared it imprints **no hex footprint
and no height grid**, and being a `Shapeshifter` rather than a `Building` it carries **none** of
`ShuttleHubBase`'s behaviour — no shuttles, no fuel consumption, no landing slots, no infopanel.
No new persisted class or field is introduced, because `ShapeshifterAutoAttach` is the engine's own.

The `ShuttleHub` template's own footprint claim (`is_tall = true`, `dome_forbidden = true`,
`build_pos = 2` — a build-menu index, `Building.lua:194`, not a placement rule) never applies to a
decoration: templates are read by the construction controller, not by an attached object. The hex
shape itself is not in the template at all; it is computed at runtime from the entity's `eHexShape`
surface (`RebuildHexShapes` → `GetSurfaceHexShapes`, `Lua/hex.lua:183-215`), so §6 **P5** is the
only way to learn it.

### 5.2 ⭐ The tower can be cut off without touching the model

`SetClipPlane` is a real `CObject` method — `CommonLua/Classes/_cobject.lua:326-349` wraps it
(`GetClipPlaneBase/Norm/Local`, `SetClipPlaneBase/Norm/Local`, `DecodePlane`/`EncodePlane`),
`CommonLua/Classes/BaseObjects.lua:410` sets it, and `CommonLua/gamelib.lua:779-808` builds a
**horizontal** plane at a chosen height and applies it:

```lua
local plane = invert and PlaneFromPoints(0, 0, z, 1, 0, z, 0, 1, z)
                     or  PlaneFromPoints(0, 0, z, 0, 1, z, 1, 0, z)
object:SetClipPlane(plane)
```

`PlaneFromPoints` is exported (`CommonLua/LuaExportedDocs/Global/LuaSharedLib.lua:566`), and
`SetClipPlane(0)` clears it (`gamelib.lua:781`). The non-inverted winding is the one vanilla gives
to the **real building** as construction progresses from the ground up, i.e. it keeps what is
**below** the plane. So a horizontal clip plane at the rim height keeps the pit and discards the
tower, with no model work at all.

⚠️ **UNMEASURED:** whether the clip plane also applies to the object's own attaches (vanilla applies
it separately to the building and to its construction proxy, `ConstructionSite.lua:949-950`,
suggesting it does **not** cascade), and — the important one — **whether the entity's `eTerrainHole`
surface still carves when the object is an attached decoration rather than a placed building.**
§6 **P6** answers both in one look.

---

## 6. Console probes `[NEVER RUN]`

Paste-safe, one line each, `*r` where the line is multi-statement, no `--` comments. Every global
used is verified present in the 1.1.0.403908 tree at the citation given; `SelectedObj` and
`MapForEach` are reachable from the sandbox (`EF-096`). Keep prints short.

**P1 — the spot question of §1.3 (run this first; it is one line and costs nothing):**
```
*r local t = {} for n, ids in pairs(GetEntitySpots("ShuttleHub")) do t[#t+1] = n .. "x" .. #ids end table.sort(t) print(table.concat(t, " "))
```
`GetEntitySpots(entity)` is used this way at `CommonLua/Classes/_cobject.lua:97`. Expect `Out` and
`Workdrone x6`; the question is whether `In` is in the list.

**P2 — does the ShuttleHub carve a terrain hole, and how big is the pit mouth?**
```
*r local m = EntitySurfaces.TerrainHole print("hole", HasAnySurfaces("ShuttleHub", m), HasAnySurfaces("ShuttleHubCP3", m), HasAnySurfaces("MetalsExtractor", m), HasAnySurfaces("SolarPanel", m))
```
```
*r print(GetEntitySurfacesBBox("ShuttleHub", EntitySurfaces.TerrainHole), GetEntitySurfacesBBox("ShuttleHubCP3", EntitySurfaces.TerrainHole))
```
`SolarPanel` is the control: it must come back **false**, or the call is not measuring what we think.
The second line's box is **the pit mouth and its depth**, the number §1.2 cannot separate from the
whole building.

**P3 — can our entity declare one? (the surface-type vocabulary the loader accepts)**
```
*r local t = table.keys(const.SurfaceTypes) table.sort(t) print(table.concat(t, " "))
```
```
*r local t = {} for k, v in pairs(EntitySurfaces) do t[#t+1] = k .. "=" .. v end table.sort(t) print(table.concat(t, " "))
```
Expect `TerrainHole` in both. `const.SurfaceTypes` is read this way at
`SceneImport.lua:3545`; `EntitySurfaces` is iterated at `_cobject.lua:88`.

**P4 — the Wasp's unused shaft states, on a live drone:**
```
*r local d = SelectedObj print(d.class, d:GetEntity(), d:HasState("metalMineExit"), d:HasState("metalMineEnter"), d:HasState("metalMineIdle"), d:GetAnimDuration(GetStateIdx("metalMineExit")))
```
```
*r SelectedObj:SetStateText("metalMineExit") print(SelectedObj:GetStateText(), SelectedObj:GetEntityBBox())
```
Select a Wasp first (Japan sponsor, or a hub drone). Expect the box to open downward to about
−26.7 m. Put it back with `SelectedObj:SetStateText("idle")`.

**P5 — the ShuttleHub's hex footprint (nothing in the data carries it):**
```
*r print("outline", #GetEntityOutlineShape("ShuttleHub"), "combined", #(HexCombinedShapes.ShuttleHub or ""), "ours", #GetEntityOutlineShape("SMROptInTrainHub6"))
```
`GetEntityOutlineShape` is already used by this mod (`20_TrainHub.lua:172`); `HexCombinedShapes` is
built at `Lua/hex.lua:200-215`.

**P6 — the decoration test: does an attached ShuttleHub carve, and does clipping cut the tower?**
Place it 30 m east of the selected object, tower clipped off at 2 m above its origin:
```
*r o = PlaceObjectIn("ShapeshifterAutoAttach", GetMap()) o:ChangeEntity("ShuttleHub") o:ClearEnumFlags(const.efCollision + const.efApplyToGrids + const.efWalkable + const.efSelectable) o:SetPos(SelectedObj:GetPos() + point(3000, 0, 0)) print(o:GetEntity(), o:GetEntityBBox(), o:GetPos())
```
```
*r local z = o:GetPos():z() + 200 o:SetClipPlane(PlaneFromPoints(0, 0, z, 0, 1, z, 1, 0, z)) print("clipped at", z)
```
If the tower is still there, try the other winding:
```
*r local z = o:GetPos():z() + 200 o:SetClipPlane(PlaneFromPoints(0, 0, z, 1, 0, z, 0, 1, z)) print("inverted at", z)
```
Then read whether the ground opened under it:
```
*r local p = o:GetPos() print("h at obj", GetMap():GetHeight(p), "h 12m out", GetMap():GetHeight(p + point(1200, 0, 0)), "obj z", p:z())
```
Clean up:
```
*r o:SetClipPlane(0) DoneObject(o) o = nil
```
⚠️ Expect the hole test to be **negative**: a terrain hole is very likely applied through the grid
path this object has just been stripped of (`efApplyToGrids`). If so, route 2 loses its pit and only
route 1 remains — which is the recommendation anyway.

**P7 — a placed vanilla hub for comparison, if the owner wants to see the pit up close.** Build a
Shuttle Hub in a sandbox game, select it, and read the terrain around it:
```
*r local b = SelectedObj local p = b:GetPos() print(b.class, b:GetEntity(), "z", p:z(), "h", GetMap():GetHeight(p), "h 15m out", GetMap():GetHeight(p + point(1500, 0, 0)), b:GetEntityBBox())
```

---

## 7. How the numbers were measured (so they can be falsified)

`Packs\BinAssets.fpk` → `entities.dat` (FLPK entry, zstd-wrapped, **14 168 326 B** decompressed) is
the compiled entity-spec database. It is the only entity store in the pack set (`BinAssets.fpk`
holds five files: `AssetsRevision.lua`, `entities.dat`, `resources.meta`, `sndlen.dat`,
`sndmeta.dat`).

**Record boundaries.** Every entity's record ends with the literal string
`Entities/<Name>.entjson`; **3 445** such markers exist, and the span between consecutive markers is
one entity's record. That is the index used throughout.

**Box block** (int32 little-endian, the door survey's layout minus its leading `duration_ms` for an
entity with no animation):

```
bsCenter.x, bsCenter.y, bsCenter.z, bsRadius,
boxMin.x, boxMin.y, boxMin.z, boxMax.x, boxMax.y, boxMax.z,
sizeX (= maxX-minX), sizeY (= maxY-minY)
```

Accepted only when `bsCenter == (boxMin+boxMax)/2` within 1 unit on all three axes,
`sizeX == maxX−minX`, `sizeY == maxY−minY`, all three extents positive, and `0 < bsRadius < 400000`.
For an animated entity the same block is preceded by `duration_ms` and sits after that state's
`Animations/<entity>_<state>.hgacl` path string; a block belongs to the **last** such string before
it (checked against `Shuttle`: the block before the `idle` string carries `dur = 3333`, which is
`Shuttle_fly`'s loop, and the next carries `166`, which is `Shuttle_idle`'s).

**Calibration, three independent points.**

| entity | this decoder | independent source |
|---|---|---|
| `WayPointBig` | min (−383,−131,−345) max (121,119,1305) r 857 | `CommonAssets.fpk` → `Entities/WayPointBig.entjson`: y, z, centre, radius and both derived sizes match exactly; only x differs, as the door survey also recorded |
| `ElevatorSurfaceDoor` | 19.46 × 0.63 × 12.93 m | `VANILLA_DOOR_ENTITIES_20260922.md` §3, same figure |
| `SpaceElevator` | 86.48 × 77.44 m | the same survey §1.4, same figure |

**Spot table.** 20-byte records, `u16 name_id | 0xFFFF | u16 angle (1/60°) | …`, run-detected by the
`0xFFFF` at +2 and a stride of 20. `name_id` indexes a global name table earlier in the same file,
records of `0x02 | u32 len | name | u32 id` (376 ids recovered; `0 = Origin`, `1 = Autoattach`,
`189 = In`, `190 = Out`, `280 = In2`, `281 = Out2`). Cross-checks: `TrainStationCCP3` decodes to the
exact spot names this mod uses in game; name id 190 (`Out`) occurs on exactly the three shuttle-hub
entities and nowhere else in 14 MB. Known limit: the open discrepancy of §1.3.

**Surfaces are NOT in `entities.dat`.** At ~4 KB per entity the file is far too small to hold surface
triangles (this mod's own 796 triangles are 153 KB of JSON), and no surface-type string occurs in
it. That is why §2 ends in an inference and a probe rather than a measurement. Surface **type names**
were read from `Mars.exe` / `MarsDebug.exe` (§2.2) and the surface **format** from this repo's own
`Entities/SMROptInTrainHub6.entjson` (§3).

**Falsifier for the headline number.** `GetEntityBBox()` on a placed Shuttle Hub must return
`z` reaching about **−4022** engine units with the box about `2815 × 2333` wide (§6 **P7**).

---

## 8. Verdicts

### Route 1 — our own pit, modelled into the hub's floor plate, same mechanism — **POSSIBLE** ⭐

Everything it needs is already in our hands. The entity is ours and hand-authored
(`Entities/SMROptInTrainHub6.entjson`), it already declares 796 surfaces in three types, and
`eTerrainHole` is a peer type in the same engine enum. The work is: **model the shaft below z = 0**
(the file's `boxMin.z` is `0.0` today) and **add `eTerrainHole` triangles over the mouth**. No new
Lua class, no new persisted name, no vanilla asset, no dependency on the Shuttle Hub at all — and
the pit can be exactly the diameter the owner wants, in the mod's own material, with its own rim.
Three vanilla side effects come free and all three are wanted (no demolish sink, build-from-below
construction, no stockpile — §3).
**Cost:** one asset pass in SMR-Assets plus a rebake. **Open:** probe **P3** (the loader's
vocabulary) and **P2**'s control, both one line.

### Route 2 — the vanilla pit entity alone, attached and scaled, tower hidden — **NOT POSSIBLE as stated**

No pit entity exists (§1.1): three shuttle-hub entities, each one mesh, three LODs, two sub-meshes,
no `*Pit` / `*Base` / `*Hangar` anywhere in `_EntityData.generated.lua`. An entity attaches whole;
half a mesh cannot be attached. And uniform scale cannot shrink the 38.8 m tower without shrinking
the 40.2 m pit by the same factor (§5).

**The near variant — the whole entity attached as a decoration with the tower cut off by a
horizontal `SetClipPlane` at the rim — is NEEDS THE PROBE.** The clipping half is source-backed and
cheap (§5.2). The doubt is the half that matters: a decoration is placed with `efApplyToGrids`
cleared (which is what keeps it from imprinting a footprint on our hub), and the terrain hole is very
likely carved through exactly that grid path — so the attached hub would most likely render its
shaft **behind solid ground**. Probe **P6** settles it. Even if it works, it costs us the Shuttle
Hub's own material, rim and posts, which do not match the hub's look pass (owner, 2026-09-21,
spec §9: *our own themed entity; never restyle vanilla's material*).

### Route 3 — the whole ShuttleHub sunk — **NOT POSSIBLE**

Sinking the object buries the rim first, since the rim is at the origin and the shaft is already
below it; the 38.8 m tower is unaffected by z and still stands. Scaling to hide the tower shrinks the
pit equally (uniform scale, §5). Without the clip plane of route 2 there is no mechanism here at all;
with it, this is route 2.

### Wasp launch and land — **POSSIBLE**, and better than expected

The rise is driven by the launching unit, not the building (§1.4), and vanilla's own generic form is
two `SetPos(pos, 1000)` + `SetAcceleration(±1500)` legs while the unit is attached to a building
spot (`ShuttleHub.lua:267-330`). The Wasp additionally ships **`metalMineEnter` / `metalMineIdle` /
`metalMineExit`**, real states with real clips, reaching **26.73 m below the drone's origin**, which
no Lua in the game drives (§4.2). ⛔ The one hard constraint: vanilla landing and flight are pinned
to the terrain height grid (`FlyingDrone:Land`, `:181-201`; `Lua/Flight.lua:285-318`), so the
hand-over between our pit sequence and the drone AI must happen **at the rim**, never at the bottom.

---

## 9. Recommendation

**Build route 1 — our own pit — and drive it with the Wasp's own `metalMine*` states.**

It is the only route that does not depend on a vanilla asset, it is the only one whose look the owner
controls, it reuses a pipeline this mod has already proven with 796 surfaces, and it retires the
recoloured recharger pad that `03_TRAIN_HUB_DRONES_high.md` only ever adopted as a stand-in — without
changing any other line of that brief. The shape of the change:

1. **Asset (SMR-Assets, owner's model).** Sink a shaft into the hub's floor plate at the launch-pad
   hex (1,1) where `launch_pad_offset()` already puts the pad (`20_TrainHub.lua:1022-1026`), deep
   enough to swallow a drone — vanilla's own shaft states use **26.7 m**, and much less will read
   fine since a drone is 2.4 m; a rim and posts in our material. Add the `eTerrainHole` triangles
   over the mouth **and nothing else**; leave `eHexShape` untouched.
2. **Code.** Launch: place the drone at a pit-bottom spot with `efVisible` set,
   `SetStateText("metalMineExit")`, `Sleep(TimeToAnimEnd())` or a scripted rise to the rim, then hand
   to the normal drone AI. Land: fly to the rim, `SetStateText("metalMineEnter")`, then remove. This
   replaces `SpawnDrone`'s `GetRandomPassableAroundOnMap` (`20_TrainHub.lua:997-1012`) and
   `InitHubLaunchPad`'s platform (`:1270-1298`); nothing else in the drone brief moves.
3. **Order.** Run **P2**, **P3** and **P4** first — three pastes, under a minute — before any model
   work. P3 confirms the vocabulary, P2 confirms the mechanism against a control, P4 confirms the
   drone states are usable. If P3 comes back without `TerrainHole`, stop and re-plan: the fallback is
   a pit whose floor is at ground level with a raised rim around it, which needs no hole at all and
   still reads as a hangar mouth from the game's camera angle.

**Do not pursue** the vanilla Shuttle Hub entity in any form: no pit entity exists, its material is
not ours, and attaching the whole 79 m building to hide 95 % of it is a large object in every frame
for a 5 m hole.

---

## 10. Owed

- ⛔ **[NEVER RUN] — nothing here has been seen in game.** §6 P1–P5 is one sitting of a few minutes
  and answers every open question in this report except P6's.
- **The open discrepancy of §1.3** (`Out` decoded, `In` not) is the one place where a decoded fact
  and the Lua disagree. P1 settles it. No verdict here rests on it.
- **Three inferences, marked in place:** that the pit is an `eTerrainHole` surface (§2.2); that a mod
  entity's `TerrainHole` surface is honoured like a shipped one (§3); that a decoration with
  `efApplyToGrids` cleared does **not** carve (§5.2, §8 route 2).
- **`metalMineEnter` / `metalMineExit` have no decoded box** — only `metalMineIdle` does. Their
  travel is assumed to match it; P4's second line measures them.
- A behaviour change on the train hub needs an owner ruling recorded for this mod before any of this
  is built (`CLAUDE.md` header, `FIX_POLICY.md` §4).
