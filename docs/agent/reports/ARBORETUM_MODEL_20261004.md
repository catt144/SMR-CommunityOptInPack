# Arboretum model — 2026-10-04

**Execution draft; independent audit pending.** This is the review package for
[ARBORETUM_MODEL_high.md](../prompts/ARBORETUM_MODEL_high.md), not an accepted findings
record. The owner imported on 2026-10-05, before the audit, by their choice; readback, activation
and menu loads are in §"Import, readback and menu loads" below. No owner look has run. Do not
consume the brief.
Input OptInPack `7b472d8`, Assets `2b9f196`; both working trees were clean on entry.
Pass 3 resumed this uncommitted tree at OptInPack `90969be`, Assets `2b9f196`. Pass 2's walkway
layout was scrapped by the owner and its builder is gone. Pass 4 resumed the same uncommitted
tree at OptInPack `e88d559`, Assets `7d3275c`; the pass 4 section below is the current geometry,
pass 3's holds where pass 4 does not change it, and the pass 1 text is kept where it still holds.
The owner replied **"I'll run the audit separately"** in this execution session.
The brief says execution and audit use different owner-selected models and nothing
enters the record unaudited; findings/checkpoint commits await that separate audit.

## Authority and live work

The 2026-10-04 ruling is recorded in [D19](../bugs/D19.md): custom glass pavilion from the
owner's concept, borrowed game assets, visible native Seeds supply, prototype first and
flat materials. Pad versus loose stock is delegated by space. The prepared choice is a
small exterior pad with native Seeds boxes/groups; its dimensions are an initial proposal.
The Large Garden reservation surface remains the baseline. OI-47/OI-48 are unsettled;
no balance, category, one-per-dome, icon, production package or promotion change is made.

No todo tool is available; this is the live list, with one item in progress.

- [ ] **In progress:** investigation and its independent audit/committed findings.
- [ ] Rough model checkpoint. Builder, exported files and desk verifier are prepared;
  execution checks ran, but independent audit is pending.
- [x] Owner import into workbench; compiled readback, template activation, both-configuration
  new-entity menu checks, complete logs archived. Unaudited; two findings open (below).
- [ ] Owner look: fresh placement, native drone stocking, visible Seeds and visitors;
  screenshots and the owner's words, adjustments and a checked checkpoint.

## Investigation for review

SOURCE below refers only to archived build **1.1.1.406343**, under
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/`. Read with `rg -n` on the named
symbols and bounded `Get-Content -Encoding UTF8` sections, at input HEAD `7b472d8`.
`python tools/doccheck.py --emit-fingerprint` read installed Steam build **25579348**.

| kind / question | evidence | proposed consequence / control |
|---|---|---|
| SOURCE — native visual stock | `Lua/HasConsumption.lua:51-52,76-88,223-250`: a named existing spot creates `ConsumptionResourceStockpile` with resource `Seeds`, no requests and no overview count. `:283-288,331-336,388-394` update it on drone delivery and debit. | Set only `consumption_resource_stockpile_spot_name="Resourcepile"` and supply that spot. The building keeps the demand request. Empty/missing visual stock or a visual `stockpiled_amount` different from stored Seeds refutes success. No vanilla method replacement. |
| SOURCE — boxes and grouping | `Lua/Buildings/ResourceStockpile.lua:127-136,549-632`: default grid, resource-specific boxes/groups, `SetCount` scaled by ResourceScale. Local decoded `ResourceSeeds` and `ResourceSeeds10` bound the pad. | Native art determines loose units versus a full group; fractional stock is not a precise visual counter. Infopanel/native milli-resource value remains authoritative. No decorative fake Seeds are built. |
| SOURCE — Grocer | `Data/BuildingTemplate/ShopsFood.lua` names `Resourcepile` in `food_stockpile_spots`; `Lua/Buildings/FoodServiceBuilding.lua:84-103` creates a native food stockpile controller. | D19 consumes Seeds through HasConsumption, so it does not inherit the Grocer's food-controller path. A modeled pad may support the native consumption pile without adopting food-service methods. |
| SOURCE / unresolved comparison — Art Store | `Data/BuildingTemplate/ShopsJewelry.lua` consumes Polymers per visit but leaves stock spot at HasConsumption's `Resourcepile2` default. The binary reader returns `Resourcepile` for its base entity. | The owner's screenshot is the appearance target; the exact relation between those loose cubes and runtime stored Polymers is not established by these reads. During the menu probe read the actual class default and native `HasSpot`/spot ranges for base and alternate art. Do not file a vanilla defect from this discrepancy. D19 explicitly names its own real spot. |
| SOURCE — footprint | `Lua/hex.lua:67-80,184-244`: Outline comes from HexShape; Build is separately optional and falls back empty. | Copy the GardenLargeCP3 HexShape triangles exactly; do not invent a nonempty Build surface. After import compare actual outline/interior/build member sets to vanilla, not just counts. A difference refutes inherited placement evidence. |
| SOURCE — building surfaces | `Lua/Mod.lua:117-178`: validator requires HexShape/Selection/Collision and Top/Workdrone; Walk and utility/door spots are optional. | Pavilion supplies reservation, selection, two small collision posts, Top and Workdrone. The entry aisle remains open. Engine collision/pathfinding is not desk-certified. |
| SOURCE — drone approach | `Lua/Units/DroneBase.lua:9-10` names Workdrone for task and deposit work; `Lua/Buildings/Building.lua:364` adds it to resource spots. | Workdrone is outside the glazing beside the Seeds pad. Delivery still uses D19's native request and callback; the owner must witness reachable drones stocking it. |
| SOURCE — entrance and visitors | `Lua/Buildings/BuildingWayPoints.lua:259-278` uses Yard before waypoint/fallback routes. `Lua/Units/Colonist.lua:2978-2984` selects the program by `prg_class` or falls back to VisitDefault. `CommonLua/X/XPrgAmbientLife.lua:428-440,727-741` detaches default visitors from the map. | Supply Yard/Door and use `prg_class="GardenNatural_Large"`; its native program (`Lua/AmbientLife/VisitGardenNatural_Large.lua:3-39`) reads Visitwarmup plus Visitbench on attached DecorInt_03. Preserve service/visit/consumption methods. Owner must still witness visitors. |
| SOURCE — borrowed art and glass | `Lua/Decor.lua:7-12` makes BuildingEntityClass auto-attach capable. `CommonLua/Classes/AutoAttach.lua:673-707,727-762,795-815` turns `att,<class>,show` annotations into native attachments. `CommonLua/Libs/DevToolsPublic/SceneImport.lua:3486-3490,3748-3749,3788-3796,4318-4319` carries annotations from import selectors. | Use vanilla tree/shrub/flower/rock/bench entity names and one separately imported glass entity. No custom object field, class method or persisted callback. Verify Attaches data and visible results after import. |
| SOURCE — workbench boundary | `tools/workbench.py` admits SourceData/entities/material/mesh/texture ownership; `tools/promote_module.py:50-54` refuses custom models. | Import directly into staging's own ArtSpec. Production remains untouched. If editor import needs production ArtSpec, stop under the brief. |

The binary reference was freshly decoded from installed `Packs/BinAssets.fpk`, not taken
from the older scratch extraction. Command: `python ../SMR-Assets/arboretum/blender/reference.py`.
The reader is `SMR-Assets/_shared/geometry/entities_dat.py`; decoded SHA-256 is
`64b682061315fab9e9bb1c21be6f29f5953ef90451b43c1574bbb0b0a05a434d`. `reference.py`
fails if that fingerprint changes. Its ignored `reference/contract.json` contains all
selected entities and the actual surface members. The reader does not decode every
native entity fully; missing tree bounds and the Art Store discrepancy are not absence proofs.

## Prepared artifact and checks

Assets: `arboretum/blender/reference.py`, `arboretum_build.py`, `verify_arboretum.py`,
`Arboretum_work.blend`, and the [import instructions](../../../../SMR-Assets/arboretum/blender/README.md).
Flat materials and FBX are rebuilt locally in its ignored `textures/` and `export/` folders.
The verifier reimports the FBX independently of the builder, checking hierarchy, one
visible mesh/material per entity, spot position/angle export, exact reservation triangles,
UVs, work-blend/export geometry and face lists, outward dome winding, glass alpha/settings
and native Seeds-pad clearance.
Its source oracle is the separately decoded vanilla contract, not just builder constants.
Native tree size, attachment rendering and dome fit still require the engine/owner.

MEASURED execution-only: the following commands ran on Assets `2b9f196` plus this working
diff, using `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`:

```text
blender --background --factory-startup --python-exit-code 1 --python arboretum/blender/arboretum_build.py
blender --background --factory-startup --python-exit-code 1 --python arboretum/blender/verify_arboretum.py
```

Both exited successfully. Local receipts `export/model_proof.json` and
`export/verify_arboretum.json` record input HEAD, game fingerprint, FBX hashes, parameters,
spot/node member lists and measured geometry counts. No geometry totals are inferred
from the concept image. The verifier checks that the full Seeds group clears the glass
line and stays within the actual exported pad top.
Blender emitted its Material.use_nodes deprecation and factory brush-path warnings;
neither is an engine import result.

Pass 1's diagnostic view was `SMR-Assets/arboretum/blender/preview_scaffold.png`; the owner's
first feedback is on that picture.

The prepared SourceData files belong to the workbench. `activate_model.py` refuses absent
imports; after disk/readback review, its `--activate` switch sets only entity, stock spot
and native visitor program in `template.json`, regenerates the class/template and updates
owned paths. It does not make the imports or edit production. The current runtime
template remains on GardenLargeCP3 until that step.

Save contract: FIX_POLICY inventory reserves `SMROptInArboretumPavilion` and
`SMROptInArboretumGlass` before any placed-content save. Ordinary native stock/auto-attaches
can persist native objects/references; this is not a clean-removal claim. D19's demolition
instruction still applies. No new Arboretum object field or persisted callback is proposed.

## Pass 3 — the concept's building (2026-10-04)

The owner's words on passes 1 and 2 are quoted in D19 and the brief. Pass 2 built separate
glass walkways; the owner called it *"a complete scrap"*. Nothing of its layout remains.

What `arboretum_build.py` now builds, every figure an owner-movable constant at its top:

- One enclosed plan inside the Large Garden reservation: the hull of a dome circle on the rear
  axis (`DOME_Y`, `DOME_R`) and two wing-end circles at the front corners (`WING_END`, `WING_R`).
  The builder refuses a plan or Seeds pad that leaves the copied reservation triangles.
- Glass: a low base wall and glass wall to the eave (`BASE_H`, `WALL_H`), two rounded wing vaults
  from the dome to the wing ends (`WING_H`), flatter glass between them falling to the entrance
  (`CENTRE_TOP`, `CENTRE_DROP`), a drum up to the ring and a bare dome (`RING_Z`, `DOME_Z`).
- Frame, cut to main members: the ring, `DOME_RIBS` 6 meridians, four heavy spokes (ring to each
  wing end, ring to each side of the entrance), the eave rail, a thin wall post every
  `WALL_POST_EVERY` 520. No roof mullions.
- Floor: planted ground wall to wall. Paving is the footpaths only: a winding centre path from the
  door to the dome, a loop through each wing, a walk round the dome's tree. `PLANTED_SHARE` .84
  sets their width.
- Attached vanilla entities, by spot annotation: trees only where the glass clears their measured
  height and canopy, shrubs on a `PLANT_SPACING` grid over the rest, one rock, benches and path
  lamps beside the footpaths. Every name already appears as an `att,<name>,show` annotation in
  the game's own entities.dat. `Flowers_01..03` were dropped after decoding: their meshes are
  4 m coloured strips, not flowers. `RockInDome_*` has no mesh of its own in entities.dat.
- Visitor spots: ten `Visitwarmup` on the footpaths, six `DecorInt_03` benches beside the wing loops.
- Kept from pass 1: native Seeds pile on `Resourcepile` on the exterior pad, Workdrone beside it,
  the copied GardenLargeCP3 HexShape, the entrance portal with leaf panels, the two entrance-post
  collision boxes. No collision on glass; whether colonists keep to the footpaths is a witness
  for the owner's look.

MEASURED execution-only, Assets `2b9f196` plus working diff, Blender 5.2:

- `python arboretum/blender/reference_meshes.py` decoded the top-LOD `.hgrm` parts and base-colour
  maps of the attachable entities from the installed packs into ignored `arboretum/reference/meshes/`.
  Heights it printed, cm: Tree_01 905, Tree_04 779, Tree_02 750, Tree_05 723, Tree_03 639; bench
  110; LampInt_02 92. The wings were raised to `WING_H` 900 because of these.
- `arboretum_build.py`: floor 5,949,577 cm2, footpaths 9,367 cm long and 101.6 cm wide (from
  `model_proof.json` `floor`). 123 vanilla attachments plus the glass (`attached`): Tree_01 1,
  Tree_02 5, Tree_03 3, Tree_04 3, Tree_05 5, Bush_01 11, Bush_02 11, Bush_03 11, Bush_04 21,
  Bush_05 11, Bush_06 23, RocksLightSmall_05 1, DecorInt_03 6, LampInt_02 11.
- `verify_arboretum.py`: PASS. Body 12,920 vertices / 3,232 faces / 139 spots / 144 nodes, glass
  6,386 vertices / 1,942 faces. Its glass check is now: roof sheets face up, wall sheets face away
  from the plan's middle, drum and dome away from the dome's axis.
- `python arboretum/blender/verify_arboretum_negative.py`: mutation refused, blend restored,
  positive recheck passed.
- `preview_arboretum.py` wrote `SMR-Assets/arboretum/blender/preview_pavilion.png`: the decoded
  vanilla meshes at the exported attach spots and angles, glass back faces culled, camera high
  three-quarter from the entrance side like the concept, picture mirrored to the game's handedness.
  Not drawn: Seeds pile, colonists, the dome's grass and light. The glass tint is a stand-in.
- OptInPack at `90969be` plus working diff: `deskcheck.py`, `generate.py --check`, `parsecheck.py`
  and `workbench.py` pass; `activate_model.py` still refuses the absent imports.

NOT MEASURED: how blendGlass looks in the game; whether 123 auto-attachments on one building cost
anything; whether a 14.6 m dome top fits every dome; the attached entities' in-game scale against
the decoded meshes.

Pass 3 executed model: **claude-fable-5-1**, from this session's system prompt; no subagent ran.
Pass 3 is unaudited like pass 1; the audit stays with the owner's separate run.

## Pass 4 — a miniature Surviving Mars dome (2026-10-04)

The owner's words are quoted in D19 and the brief. Pass 3's plan, footpaths, visitor spots, Seeds
pad, Workdrone and copied HexShape are unchanged. What changed in `arboretum_build.py`, every
figure an owner-movable constant at its top:

- **Top bubble cut.** The drum, ring and raised dome are gone, with the wing vaults, glass wall,
  eave rail, wall posts and spokes. The glass is one smooth shell over the plan: a rounded
  shoulder rising from the base ring (`SHOULDER` 400 in, `RISE` 760 up) and a low crown
  (`CROWN` 200 over `CROWN_RUN` 400). Top 1,005 cm; the 14.6 m question is gone. The shell's
  vertices are shared and shaded smooth.
- **Dome look.** A dark base ring (`BASE_H` 45) with seven feet (`FEET_AT`, `FOOT`) and two slim
  dark ribs from beside the door to the rear (`RIB_FRONT`, `RIB_REAR`, `RIB_R` 9) are the whole
  frame. Colours are read by eye off `look_ref_vanilla_dome.jpg`: MEASURED, the decoded
  `DomeTrigon` and `Dome_Entrance` base-colour maps are near white (the game tints them), so
  there is no dark palette in the meshes to copy.
- **Door.** The custom portal and leaf panels are gone. The vanilla dome's own door leaves,
  `DomeDoorEntrance_01` and `_02` (decoded: 408 wide, 272 tall, arched, three portholes), attach
  on `Doorleaf` spots and stand slid open either side of a clear 400 doorway under a slim dark
  frame and track. Their meshes sit off their origins, so each spot is offset to land its leaf.
  The other vanilla `*Door` entities decode with garbage bounds (animated) and were not used.
- **Planting.** 9 tree types (the 5 dome trees plus `TreeArm_01..04`, conifers and a birch), 6
  bushes, big ferns `BushArm_01..03`, 3 rock types. Trees only where the shell clears their
  measured height and reach; shrubs on a `PLANT_SPACING` 165 grid, up to `UNDERSTOREY` 70 from a
  trunk, a wide one kept off the glass. Not used after decoding: `TerrainGrass_*` are plain
  cubes; `GrassArm_*` and the `Crop*` fields are 9-14 m patches that would bury the footpaths;
  six `Crop*`/`ResourceFruitTree` meshes are not in the installed packs.
- **Night lighting, the native route.** SOURCE `Lua/NightLightObjects.lua:430-541,544-570`: at
  `EntitiesLoaded` the game reads every entity's `Autolight` and `L` spots and parses the
  annotation into a point or spot light, or `emissive` into the entity's self-illumination;
  `:201-226` switches them at night and recurses into attached `NightLightObject`s;
  `CommonLua/Modding/ModItem.lua:695` fires `EntitiesLoaded` again after mod entities load.
  `Lua/Buildings/Building.lua:1391-1429`: lights follow the building's working state.
  `Lua/_EntityData.generated.lua`: the `Lamp*` entities are `NightLightObject`s. So the body
  carries 32 `Autolight` spots in vanilla's annotation form, and a light strip (base ring inside,
  door lintel) that is the only lit part of its SI map. No script.

MEASURED execution-only, Assets `7d3275c` plus working diff, Blender 5.2, from `model_proof.json`:

- 220 attachments (`attached`, glass included; pass 3 had 124): trees 26 (Tree_01 2, Tree_02 5,
  Tree_03 3, Tree_04 4, Tree_05 3, TreeArm_02 2, TreeArm_03 5, TreeArm_04 2), bushes 140
  (Bush_01 11, Bush_02 13, Bush_03 33, Bush_04 38, Bush_05 12, Bush_06 33), ferns 2 (BushArm_01,
  BushArm_03), rocks 2 (RocksLightSmall_02, _05), benches 6, lamps 41 (LampInt_03 11, LampInt_02
  10, LampGroundInner_01 20), door leaves 2, glass 1. `TreeArm_01` (954 cm) found no site.
- 32 lights (`lights`): 13 `color:neutral,radius:9,intensity:60` over the footpaths and door, 14
  `color:cool,radius:6,intensity:40` inside the base ring, 4 `color:warm,radius:16,intensity:50`
  in the canopy, 1 `emissive,intensity:200`.
- `verify_arboretum.py`: PASS. Body 6,532 vertices / 1,664 faces / 267 spots / 272 nodes, glass
  1,460 vertices / 1,797 faces. New checks: glass top equals the stated shell top and nothing of
  the frame stands above it, all glass wound outward and smooth, light annotations in the parsed
  form with exactly one emissive, both door leaves, only the light swatch lit in the SI map.
- `verify_arboretum_negative.py`: mutation refused, blend restored, positive recheck passed.
- `preview_arboretum.py -- day` and `-- night` wrote `preview_dome_day.png` and
  `preview_dome_night.png`; `preview_dome_board.png` sets them beside the concept and the dome
  reference. Night draws a light at each exported `Autolight` spot and a stand-in light at each lamp.
- OptInPack at `e88d559` plus working diff: `deskcheck.py`, `generate.py --check`, `parsecheck.py`
  and `workbench.py` pass; `activate_model.py` still refuses the absent imports.

NOT MEASURED: brightness and reach of these lights in the game (intensities are first guesses
inside vanilla's range); whether attached lamps bring their own light (the reader does not decode
their spots); whether the door leaves land on the track and keep their idle pose as attachments
(`DoorWithFX`); their and the frame's tint; cost of 220 attachments and 31 lights on one building;
blendGlass on a smooth shell. The leaves never close; colonists walk the open doorway.

Pass 4 executed model: **claude-fable-5-1**, from this session's system prompt; no subagent ran.
Unaudited like passes 1 and 3; the audit stays with the owner's separate run.

## Owner steps and continuation

After the different-model audit and checkpoint, hand over the five import steps in the
Assets README. Save and close the editor before agent writes. Read compiled mesh/material/
entity paths, spot annotations and geometry against the exported proof, then activate.
Run the native-consumption desk check, generator parity, parsecheck and workbench gate.
Adapt the build report's fresh-process menu matrix to require the new entity and glass,
all native attachment classes, stock spot, visitor program, exact vanilla reservation
member sets and native consumption method identity. Check with the fix pack present and
absent, restore the actual captured enabled-mod order, archive full logs. This is still owed.
The owner's audit/import handoff is OI-52 on this mod's checklist. The live gameplay
continuation stays with the existing ck223 sitting; the fix pack was not edited here.

The sitting source retains ck223's slots. Added **slot 9** reads entity, native visual stock,
stored Seeds, visual count, visitor program and direct attachments, and refuses a placeholder
or missing/mismatched stock. Source prepared; not installed or run. Preload before the look.
`python staging/tools/arboretum/preload.py` ran without `--install`; generated slot source
and its receipt are prepared in staging, and the TestKit working tree remains clean.
First owner batch after menu checks: load the disposable inhabited-dome save; enable D19;
place a fresh pavilion; let drones build and deliver Seeds; pin with slot 2 and read slot 9.
Owner views the building/dome panels and takes normal-camera screenshots. Then slots 4/5
run the organic visit window at top speed, followed by forced depletion/refill if needed.
No seeds-per-sol figure is claimed here; that measurement remains ck223's.

Owner screenshots: **NOT RUN**. Owner look words: **NOT YET SUPPLIED**.
Both-configuration new-model menu-load evidence: **NOT RUN**. No claim of all-dome fit,
Arboretum completion or readiness to ship. Existing placeholder Arboretums are not migrated
by this preparation; use fresh placement for the look sitting.

## Review package handoff

Executed model: **gpt-6-astra, xhigh**, read from the `model`/`effort` fields of this session's
`turn_context` record in
`C:/Users/stkot/.codex/sessions/2026/10/04/rollout-2026-10-04T15-23-59-01a1085f-8211-7200-a886-74ab2ca463ae.jsonl`.
No subagent or independent audit has run. The `_high` suffix is not the executed effort.
Probe sweep: `rg -l TEMPORARY Code staging/Code ../SMR-BugFixPack-TestKit/Code` returned
no paths at input HEAD `7b472d8`; no temporary runtime probe was installed by this preparation.
The execution draft and source changes remain uncommitted pending the brief's audit requirement.

Execution checks at OptInPack `7b472d8` / Assets `2b9f196`, plus this working diff:

- `python staging/tools/arboretum/deskcheck.py`: native debit/empty/restart and build-lock
  controls pass; the new slot refuses placeholder, missing and stale visual stock, and
  accepts matching stock. These are synthetic objects, not drone/colonist evidence.
- `python staging/tools/arboretum/generate.py --check`, `python tools/parsecheck.py`, and
  parsecheck's Lua loader over the prepared SourceData and composed slots pass.
- `python tools/workbench.py`: ownership/package isolation passes. `git diff --exit-code --
  staging/Code staging/Data metadata.lua items.lua SourceData/ArtSpec-mod.lua` confirms
  runtime/template and production editor surfaces have not been switched by this preparation.
- `python staging/tools/arboretum/activate_model.py` intentionally refuses the absent
  imports with `Both entities must be registered by the Mod Editor`; no activation ran.
- `python ../SMR-Assets/arboretum/blender/verify_arboretum_negative.py` moves a source vertex
  without changing topology, requires a geometry-drift refusal, restores the work blend
  byte-for-byte and requires the positive check again. Local `export/verify_negative.json`
  retains the refusal. This tests the export gate, not the native importer.
- `python tools/doccheck.py --regen` and `python tools/doccheck.py`: GREEN. Existing
  frozen-row warnings remain D16/D17/D18. No generated output changed in this preparation.
- The diagnostic Blender view, receipts and generated maps are local rebuildable artifacts;
  all borrowed game data stays under ignored Assets `arboretum/reference/`.

| finding/block | evidence/home | next action | disposition |
|---|---|---|---|
| Owner's custom-model decision | D19 and prompt | obey during model/import | recorded authority, not an agent verdict |
| Native stock/visitor/attachment route | investigation above, archived source and local contract | different-model audit; runtime controls | draft, not accepted evidence |
| Rough model and flat export | Assets builder/verifier and receipts | audit/checkpoint, owner import | prepared; uncommitted |
| Art Store spot discrepancy | investigation above | menu inspection of native class/entity values | unresolved; no fix commissioned |
| Imported entity names and native residuals | FIX_POLICY/D19 | inspect saves only in the commissioned sitting scope | reserved contract; no removal proof |
| Menu checks and owner look | continuation above | import then fresh-process matrix; preload slots | not run; prompt stays live |

## Import, readback and menu loads (2026-10-05)

Execution-only, unaudited, uncommitted. OptInPack `0de88e6` plus working diff, Assets `7d3275c`
plus working diff, game **1.1.1.406343**. The owner ran the five import steps, saved and closed
the editor, and chose to import before the different-model audit, which covers all of this
before any commit. Statements above that say the import, activation, menu checks or slot
install have not run predate this section.

**Editor-save diff.** The save rewrote `staging/metadata.lua`, `items.lua` and both template
files. Dropped fields, each equal to its source default: ModDependency `version_minor` 0 and
`required` true (`CommonLua/Modding/Mod.lua:2821-2822`), ModDef `version_minor` 0 and
`optional_mod` false (`:267,272`), ModItemOptionToggle `DefaultValue` false (`:2730`), template
`maintenance_resource_amount` 1000 (`Lua/RequiresMaintenance.lua:23`) and `same_category_as` ""
(`Lua/ServiceBase.lua:18`). Added: `entities`, `Code/_EntityData.generated.lua`, ModItemRefs,
`version` 3, `saved`, `code_hash`, `affected_resources`; template handle 12 became 1. As
`c704955` did for production, the hand `metadata.lua`/`items.lua` were restored from git and
given only the `entities` list and the entity-data code line; the template files are
regenerated from `template.json`, whose handle now follows the editor's (1). The editor moved
the dependency's `id` above the ModDef's, which made `generate.py` write production's id into
`SaveIn`; it now reads the one-tab `id`.

**Readback.** `python staging/tools/arboretum/readback.py <fbx dump>`; receipt
`docs/archive/arboretum_model_20261005/readback_receipt.json`. The FBX files on disk carry the
proof's hashes and are the import items' ScenePath. Compiled pavilion: 267 spots equal the
proof's in name, position, angle and annotation; 220 attach annotations in 25 classes and 32
light annotations equal the proof's; surfaces 4 HexShape (the proof's triangles), 132
Selection, 24 Collision, no Build. Compiled meshes: pavilion 3,204 triangles, glass 2,849, equal
to the triangulated FBX; every compiled position within 0.039 cm of an FBX position and the
reverse, under one axis map that also carries the 267 FBX spot empties onto the compiled spots.
Glass material: blendGlass, DepthWrite off, TwoSidedShading on, CastShadow off. Seen, not
judged: the glass compiled to 6,402 vertices from 1,460, so the importer split most of the
smooth shell's vertices; whether it shades faceted is for the owner's look.

**Activation.** `activate_model.py --activate` set entity, stock spot `Resourcepile` and
`prg_class`; it now also lists the entity-data file as the module's code. `generate.py --check`,
`deskcheck.py`, `parsecheck.py`, `workbench.py`, `workbench_selftest.py` and `doccheck.py` pass.

**Menu loads.** `python staging/tools/arboretum/read_model_boots.py`; logs and
`boot_receipt.json` in `docs/archive/arboretum_model_20261005/`. Each leg is a fresh retail
process armed through the fix pack's `arm_leg.ps1`. Captured enabled order: fix pack, TestKit,
Opt-In; the workbench was not enabled. `setup` enabled it, four check legs ran (fix pack
present/absent, option off/on), `restored.log` confirms the captured order is back and
production alone has no Arboretum. In all four legs: template on `SMROptInArboretumPavilion`
with `Resourcepile` and `GardenNatural_Large`; both entities valid; spot counts as proved; 220
attachments, every class known to the game; 32 lights parsed, one emissive, 32 in the game's
night-light registry; 41 consumption methods identical to the native class's; live off/on
reconciles. Art Store, informational: class default spot `Resourcepile2`; `ShopsJewelry` has one
`Resourcepile` and no `Resourcepile2`; `ArtGalleryCCP2` has neither.

Findings, both open:

1. **The reservation is not the Large Garden's.** MEASURED: pavilion outline 19 hexes, Large
   Garden 10; the 19 are those 10 plus the 9 hexes around them. Interior, Build and inverse
   Build are empty for both. The copied triangles follow the outer edge of the 10 hexes and the
   game counts the neighbours they touch. Placement evidence from the Large Garden does not
   carry. The fix is in `arboretum_build.py` (pull the HexShape in from the edge) and needs a
   re-import; not done, so the first look runs on 19 hexes.
2. **One Lua error at every start with the workbench loaded:** `CommonLua/Editor/ArtSpecEditor.lua:573:
   attempt to call a nil value (global 'EntitySpecPathToEntity')`, raised for
   `SMROptInArboretumGlass` while mod items load. The entities still load and every check after
   it passes. Production's five EntitySpecs do not raise it (`restored.log`, `setup.log`). Cause
   not established.

Two engine behaviours found on the way, both SOURCE plus MEASURED:

- A first load only queues a mod's entities (`CommonLua/Modding/Mod.lua:2150-2154`); they load
  with a map's assets (`CommonLua/Core/map.lua:245`). At the menu they are not valid until
  `WaitDelayedLoadEntities()` runs; the probe calls it.
- `Attaches[entity]` is built from annotations only on DataChanged
  (`CommonLua/Classes/AutoAttach.lua:799-821,851-853`), which a first load posts before mod
  entities exist. MEASURED in `attempt4_present_off.log`: after the entity load the pavilion had
  no attach table. `staging/Code/Opt_Arboretum.lua` now builds that one entity's table on
  `AdditionalEntitiesLoaded` with the game's `GetEntityAutoAttachTable`; with it the table holds
  the 220. This is module code the pass 3 and 4 text above did not foresee ("No script"). It
  writes no save data and replaces no method. Whether the attachments then appear on a placed
  building is the owner's look.

Retained failed attempts: `attempt1` (the exe restarts itself through Steam; the runner
disarmed before the second process read the kit), `attempt2` (workbench not enabled),
`attempt3` (editor-saved items; entities not loaded at the menu), `attempt4` (no attach table).

Slots: `preload.py --install` RAN; the kit's `Code/80_AgentSlots.lua` is modified and
uncommitted, receipt `staging/tools/arboretum/preload_receipt.json`. The workbench is not in the
enabled list; the owner enables it for the look.

First look, attempt 1 (owner, 2026-10-05): *"found nothing in the build list"*. The owner had set
Arboretum to On on the workbench's own Mod Options page; both cold starts logged `Arboretum:
inactive`. SOURCE: the list shows a page for any mod whose options object has properties
(`Lua/XDef/OptionsContentWindow.generated.lua:472`) and never asks `HasOptions`, which is all
the bridge overrode; a value applied there is stored under the workbench id
(`CommonLua/Modding/Mod.lua:753-768`), not production's. `staging/Code/00_Workbench.lua` now
caches an empty property list on the workbench's options object; `workbench_selftest.py` passes.
The hidden page is unverified in the game. The 2026-10-03 workbench boots checked `HasOptions`
only, so this was not caught there.

First look, attempt 2 (owner, 2026-10-05, two cursor screenshots; words in D19): the cursor shows
the base, ribs, footpaths, benches and planting, so the attach table reaches a real placement
cursor. Footprint too big, as measured; the owner judges the asset fits the corrected footprint.
Glass, lamps lit, doors and Seeds stock not yet judged.

Changes after it, execution-only: `arboretum_build.py` writes the reservation as one inset
hexagon (`HEX_SHRINK` .8) on each of the 10 hexes the game reads for the Large Garden
(`HEX_CELLS`, from `present_off.log`), IMPORTER_FACTS's method; `verify_arboretum.py` requires
one face per cell, every corner inside its hex's inscribed circle and every cell centre inside
the decoded GardenLargeCP3 triangles; build, verify and the negative control pass. `readback.py`
compares the compiled HexShape corners with the proof's faces. `template.json` gains
`interest4 = interestSocial`. Both FBX files were rewritten, so **the compiled assets in
`staging/` are stale until the owner re-imports both**; the readback, the menu loads and
`read_model_boots.py`'s expected reservation lines must be redone after that. NOT MEASURED: that
the game reads 10 hexes from the new surface.

First placed building (owner, 2026-10-05, night screenshot; words in D19). The owner re-imported
the pavilion (compiled 14:11, FBX 14:04) but not the glass, and played on the editor-saved mod
files; no readback or menu load ran on that import. Seen in the screenshot: glass shell, ribs,
trees, shrubs, benches, lamps, both door leaves and a native Seeds pile of ten boxes. The scene
is blown out white, and the pile sits about centred on its spot along x (spot 670, pile about
362 to 941, read off the screenshot), so it overhung the pad towards the door.

Changes after it, execution-only, in `arboretum_build.py`: all lights warm; path 60 to 15 and
radius 9 to 6, ring 40 to 10 and radius 6 to 4, canopy 50 to 15 and radius 16 to 12, glow 200 to
80; ring bollards halved (`RING_LAMP_EVERY` 840; 20 to 10, 210 attachments); `STOCK_SPOT` x 670
to 950. The verifier's stock-extent check follows the screenshot reading. Build, verify and the
negative control pass. NOT MEASURED: how much of the glare is the attached lamps' own light,
which no annotation here controls. **Both compiled entities are stale again** until the owner
re-imports both. `staging/metadata.lua` and `items.lua` are the editor's form again and want the
hand restore after that import.

Second placed building (owner, 2026-10-05, two screenshots; words in D19), on the owner's own
re-import of both entities, again without a readback or menu load. Seen: the Seeds pile sits on
its pad; infopanel reads Servicing 40/40, Stored Seeds 10/10, interests Social, Relaxation,
Exercise, Playing; a colonist sits on a bench inside; the interest popout lists Party Animal
only. Lights still too strong. Changed in `arboretum_build.py`: path and canopy 15 to 8, ring 10
to 6 and orange, glow 80 to 40; build, verify and negative control pass; compiled assets stale
again. The trait request is an open owner decision: the popout lists only effects the game
applies (`Code/Opt_ServiceInterestTags.lua:220-246`), so more tags means more real effects.

Crop survey (owner, 2026-10-05: *"Can we borrow assets from the farm planets ... alot of them look
like flowers"*, then *"start with the flowering / colorful ones, see what we can do"*). Desk only,
Assets `7d3275c` plus working diff. `python arboretum/blender/crop_survey.py` MEASURED: 57 `Crop*`
entities are named in the base entities.dat; 49 have a mesh, 34 in `Packs/Meshes.fpk` and 15 in
`DLC/norman.fpk`; 8 have none in any pack (Cabbage, HerbGiant, Pea, PumpkinArm, SoybeansGiant,
Spinach, Tomato, Zucchini). Every crop carries 3 to 5 growth-stage meshes (`mesh`, `mesh2` ...).
Bed-sized ones are 6 to 10 m across (`_SmallFarm` and hydroponic variants); field ones 22 to 31 m.
`preview_crops.py -- beds|large|stages` wrote three contact sheets beside it from the decoded
meshes and base-colour maps. Read off the sheets: Herb's last stage is a red, purple and blue
flower bed; Rapeseed and Quinoa bloom yellow and pink at stage 3 of 4 and dry out at 4; Cucumber
flowers yellow at 3 of 5; Pumpkin ends on orange fruit; Coffee (DLC) on red berries; Potatoes and
Soybeans flower faintly. NOT MEASURED: any of them attached to the pavilion or scaled in the game,
and how the game steps a crop through its stages. Nothing is built from this.

Staffing, upgrades and display beds (owner go-ahead 2026-10-05; design in the brief §"Agreed
design"). Built by two subagents on disjoint files, both **claude-opus** at the session's effort
(general-purpose type, `model: opus`), unaudited, nothing imported or run in the game.

- Model (`SMR-Assets/arboretum/blender/`): three `Cropbed` spots with clear 800 circles at
  (0,-360), (770,290), (-770,290) and two `Specimen` spots with clear 500 circles at (0,480),
  (0,-1250); the footpaths are now a ring round each, joined along the centre line; 10 trees, 75
  shrubs, 6 benches, 20 lamps, 115 attachments, 26 lights, 161 spots. Build, verify (new circle
  checks) and the negative control pass; `preview_dome_day.png` shows it. The night preview fails
  on the orange ring light and is stale. Compiled assets in `staging/` are stale.
- Code (`staging/Code/Opt_Arboretum.lua`, `template.json`): parents `ElectricityConsumer`,
  `LifeSupportConsumer`, `ServiceWorkplace`; 2 workers, no specialization, automation floor 100;
  own `GetWorkshiftPerformance` (100 / 125 / 150 or the workers' own; 100 without Seeds), own
  `Consume_Workshift` (1 Seed per staffed shift, +1 per upgrade) and a `CanConsume` that keeps an
  empty building open; three upgrades; visit bonus under Seasonal Blooms; crop attach and state
  stepping after the farm's. `generate.py --check`, `deskcheck.py` (8 PASS) and the parse check
  pass here; the agent reports 14 single mutations each failing the desk check.
- Departures the agent made, for the owner to see: capacity 14 per shift (42 over three shifts,
  60 with Rare Specimens) because a staffed service multiplies capacity by open shifts
  (`Lua/Buildings/Service.lua:294-302`); Rare Specimens alone costs 2 Seeds a shift; beds stop
  growing as well as replanting while untended; Rare Specimens shows `CropApples` on both spots;
  upgrade costs chosen (bots 10 Electronics, the others 5 and 10 Polymers); Blooms and Specimens
  need no tech.
- Stale because of it: `staging/items.lua` option help and the description's Seeds wording there,
  slot 6's forced-empty expectation, `read_model_boots.py`'s expected counts.
- NOT MEASURED, all of it in the game: the class builds; workers take the jobs with
  `automation` above 0 (`Lua/Buildings/Workplace.lua:1387`); upgrades appear and modify; Seeds
  per shift; crop state names against mesh stages (inferred, the mapping is in the binary entity
  data); crop scale and selection; the two fields through a save and load.

Default shrubs on the `Specimen` spots (owner, 2026-10-05; words in D19): the code agent added a
four-shrub group per spot that Rare Specimens replaces and switching it off restores; no new
saved name (`SMROptInSpecimens` changed shape before any save held it). Desk check 9 PASS here.

Third import and its checks, 2026-10-05 evening, execution-only. The owner re-imported both
entities (compiled 17:44, FBX 17:10). Hand `metadata.lua`/`items.lua` restored again with the
`entities` list and entity-data code line; `activate_model.py --activate`, `generate.py --check`,
`deskcheck.py` and `tools/workbench.py` pass. `readback.py` passes on the new proof (stdout kept
in `scratch/arboretum_boot/readback2.json`, not archived). Menu loads, logs in
`docs/archive/arboretum_model_20261005staffed/`, captured order fix pack, TestKit, Opt-In,
`qL8sA2m`, workbench:

- `present_on_nochange.log` (fix pack present) and `absent_on.log` (absent; it put the captured
  order back, `next_order` line): every section ok. MEASURED: reservation 10 hexes against the
  Large Garden's 10, all six shape kinds equal, so the 19-hex finding is closed; spots `Cropbed`
  3, `Specimen` 2, `Visitwarmup` 10, `Autolight` 26; 115 attachments, every class known; 26
  lights in the registry; the class is a `ServiceWorkplace` with `max_workers` 2, `automation` 1,
  `auto_performance` 100, capacity 14, store 30, consumption type 5; its only consumption
  overrides are `CanConsume` and `Consume_Workshift`; three upgrade ids present; the seven crop
  entities used are valid classes whose states are `idle`, `idle2` ... one per mesh stage, which
  is the naming the code assumes.
- `attempt1_present_on.log` is retained: it failed two probe assumptions, not the module (the
  leg expected the option off while the owner's account now has it on, and a check that the
  Diner uses HasConsumption's own `CanConsume`, which was never established and was removed).
- The one startup Lua error (`ArtSpecEditor.lua:573`) is still in every workbench boot; cause
  not established.
- `read_model_boots.py` was not updated and does not read these logs; no receipt was written.
- No option-off leg and no `restored` leg ran this round.

Still NOT MEASURED: everything in a loaded colony after the first two looks. The handoff is the
rewritten [brief](../prompts/ARBORETUM_MODEL_high.md).

Executed model: **claude-fable-5-1**, from this session's system prompt; two subagents ran, named above.

## Owner look, door and blooms (2026-10-05 evening)

Execution-only, unaudited, uncommitted; OptInPack `0de88e6` plus working diff, Assets `7d3275c`
plus working diff. The owner's words are in D19. Four subagents ran, all **claude-opus** at the
session's effort (general-purpose type, `model: opus`), on disjoint files; one earlier
**claude-sonnet** agent updated `read_model_boots.py` (receipt
`docs/archive/arboretum_model_20261005staffed/boot_receipt.json`; it notes that the logs carry hex
counts, not hex lists, that `ServiceWorkplace` shows only as the consumption section passing, and
that "order restored" rests on the staged `next_order` line). `preview_arboretum.py -- night`
renders again: its colour table lacked the game's `orange` (`Lua/NightLightObjects.lua:18`, build
1.1.1.406343).

**Door.** SOURCE: a building with a `Yard` spot gets no door route (`Lua/Buildings/BuildingWayPoints.lua:264-266,
297-299`); `GardenNatural_Large` pathfinds to the visit spot and walks the last leg straight
(`Lua/AmbientLife/VisitGardenNatural_Large.lua:8,13,24`; `CommonLua/X/XPrgAmbientLife.lua:800-806`);
leaving is a state change with no movement (`Lua/Units/Unit.lua:441-452`). MEASURED (`entjson`): the
compiled pavilion's only Collision was the two door posts (24 triangles). Built in
`arboretum_build.py`: a collision ring (`WALL_T` 20, `WALL_Z` -16..320) along the glass line with
the one door gap; 684 triangles; verifier checks one gap of door width, all 21 interior spots
inside, Yard and stock pad outside, straight walks from the door clear; five collision mutations
refused. The pavilion FBX changed in Collision only; the glass FBX differs in 109 bytes but
re-imports identically. Pavilion re-import owed. NOT MEASURED: that the pathfinder honours a 20 cm
ring. Correction: `ShopsFood`'s collision is a closed solid with its visit spots outside it, so
vanilla shops are not evidence that a gap routes visitors. The builder and verifier take
`ARBORETUM_STAGING` so a build need not overwrite the editor-saved `staging/SourceData` files; the
verifier's SIE line check fails against editor-written files (pre-existing, format only).

**Beds.** INFERRED from `Opt_Arboretum.lua` and the crop sheets: under Seasonal Blooms a bed
was in bloom a quarter to a third of its sol and only Herb reads as flowers. SOURCE: giant crops
are separate taller entities (`Data/CropPreset.lua:25,67,151,252,294,355`); the smooth growth is
terraforming vegetation's scale-up from 20% in a saved thread (`Lua/Vegetation.lua:15,362-404`),
not copied. Built (owner ruling "do a plus our own"): beds always at a bloom state; with the
upgrade scale 20 → 120 by hour 10 of the bed's sol on the quarter-hour update, then held;
`BED_VARIETIES` of six Herb tints then the three custom blooms, tint by `SetColorModifier`; a
missing entity is skipped with one log line; custom entities are placed as `CropEntityClass` with
`ChangeEntity`; no new saved name, bed record unchanged. Desk check 9 PASS, 16 single mutations
caught. Models (`SMR-Assets/arboretum/blooms/`): Spike 2.5 m 2,710 tris, Round 1.5 m 2,484,
Low 0.6 m 3,364; one mesh, one material, 64 px maps; verifier and 18-case negative control pass;
`preview_blooms.png`. Their SIE and GFXMaterial sources are in `staging/SourceData/`;
`activate_model.py --activate` registered them and the workbench is GREEN. NOT MEASURED: the
importer accepting them, tint on Herb, scale steps, any of it in a colony. Agent decisions for
the owner: tint values, full at hour 10, straight-line growth, variety order.

Import owed: pavilion, then Spike, Round, Low; after it the hand `metadata.lua`/`items.lua`
restore, `activate_model.py --activate`, readback (blooms not yet covered), menu loads.
