# Elevator Depot, the paint pass (brief 28), 2026-10-01

> **Run B (2026-10-01) is the current state: its section is at the end of this file.** Run A's state
> below is history, kept as written; the owner's verdict on it is the last run-A section.

Build **25579348** (`python tools/doccheck.py --emit-fingerprint` at the start, GREEN; 1.1.1.406343).
Executed model: Claude Fable 5.1 (`claude-fable-5-1`), the brief's `_high` session, with two
subagents (Sonnet for vanilla's texture read, Opus for the AO bake; both at the session's `high`).
Start: OptInPack `1972103`, SMR-Assets `642943a`; `git pull` current in OptInPack, Assets has no
remote. `tasklist`: no `Mars.exe` at the start; nothing under the dev mod's `Code/` was written.
Brief 27 went live beside this one and committed `3131ad2`..`ad01179`; its `10_ElevatorDepotDev.lua`,
its smoke and its staged slots are untouched here, and the depot's Mod Editor import was NOT run.

**State: maps built, desk-verified, rendered by day and by night from the owner's angles. Owed:
the owner's yes on the renders (`SMR-Assets/elevatorstation/blender/review_paint/index.html`), then
the import (after brief 27), then the sitting on both maps.** The brief's done-when (the owner sees
the painted depot in their normal game, both maps, day and night, and says it is production ready)
is not reached, and nothing below claims the look: Blender renders on a proxy elevator are what the
owner has to judge first; the game decides after.

## Commits

| repo | commit | what |
|---|---|---|
| SMR-Assets | `c660d60` | the UV pass: world-scale islands, one atlas for both entities, the verifier compared by position with UV checks, the depot's own material name |
| SMR-Assets | `f059a97` | the painter, the AO bake, the paint and compose render scripts, the maps' proofs, the README, the review renders and sheets |
| SMR-OptInPack | `cffb57a` | the dev mod's GFXMaterial `SMROptInElevatorDepot` (handle 6), its `items.lua` ref, both import items pointing at it |
| SMR-OptInPack | the commit after `cffb57a` | this report, brief 28's row |

## The owner's words

Firing the brief, 2026-10-01: *"update the design prompt to fire paint work, get it production
ready. Probably match the general them of the train hub that we made while blending it in with the
vanilla elevator look."* Nothing further from the owner this session; the renders are their first
look.

## What the facts turned out to be

- **The depot's maps were a swatch atlas.** `depot_geometry.assign_uvs` squeezed every face into
  the middle 60 % of one 128-px cell of a 1024 atlas: flat colour, no texel density, no room for a
  seam. Finished maps needed a real unwrap first; brief 28 puts UV work in scope.
- **Vanilla's Space Elevator base colour is neutral grey, not ivory** (read 2026-10-01 from the
  installed packs with `tools/flpk_extract.py`: `Materials.fpk` binds `SpaceElevator_mesh.sub_1` to
  BaseColor `1321000` (Textures7, BC1 sRGB 2048), RM `1321002`, Normal `1321001`, Colorization
  `1321009`; the light panels cluster at RGB (206,207,206), 64 % of texels, roughness byte 41,
  metal 0; the dark band (57,56,57) at roughness 137; seam lines (112,112,112); an accent
  (2,36,49)). The warm ivory the owner sees is the game's colourisation and light. Our material has
  no colourisation map, so the hub's off-white `#D9D4CA`, accepted by eye beside those pads in the
  design pass (owner screenshots `designpass_01`, `passengers_01`), stays the match. The decoded
  PNGs are in `SMR-Assets/trainhub/reference/raw/SpaceElevator__*` (game art, git-ignored).
- **UVs are float32.** The first pack separated islands by offsets of a kilometre per island; at
  378 km two 1 cm slivers of the trough rounded to zero width. One metre apart is enough
  (`depot_geometry.ISLAND_OFFSET`), and the verifier now derives islands from UV connectivity on its
  own and would catch a merge.
- **The subagents skill's tier agent types are not installed on this rig** (`.claude/agents/` holds
  only `doc-surgeon`); `general-purpose` with an explicit model was used. Filed in memory.

## Design calls

| call | why |
|---|---|
| The depot gets its **own material** `SMROptInElevatorDepot` (GFXMaterial handle 6); the dome's `SMROptInElevatorStation` is not touched | the dome entities are on hold (D4) and share that material; repainting it would repaint them |
| **One island per primitive at world scale**, u along a loft's ring and v along its rows, planar for free faces; **both entities in one atlas**, quarter-turn rotations only, uniform scale, 10 texels apart at 2048 | a line around the shell is a texel row and a line along it a texel column (the hub's UV lesson); the receiver shares the material, so it shares the atlas |
| **Sizes: BC, NM, SI at 4096, RM at 2048** | the hub's structure set and its reasons (density makes a seam crisp; RM carries nothing finer than a face). Density 15.5 texels/m at 2048, so **31 at 4096** against the hub's 19.15. Raw DDS about 47.5 MB (the owner's 2026-09-21 ruling: the 5 MB guard does not bind this mod; resolution is a look decision). `-- --size 2048` bakes the 14 MB fallback from the same UVs |
| **Palette by value from the hub's reactor paint**: navy `#162248` .38/.10, polished off-white `#D9D4CA` .30/.60 on the mouth collar, gunmetal `#14181E` .30/.70, brushed silver `#AEB9BE` .40/.75, the deep blue line (0,40,255) at `THIN_SI` .4 (SI byte 102) on every glow stroke | "match the general theme of the train hub"; the levels are the ones the owner kept on the hub (SI .4: "navy, just brighter") |
| **The shell's skin in the off-white at roughness .24 / metal .05**, between vanilla's panels (.16) and the hub's shell (.31), in **plates**: courses of 2.6 m up the walls from the floor, plates radiating from the crown over the arch, a belt seam at the shoulder, station seams under each rib and one mid-gap; one-sided step seams .12 m wide, 18 % darker, 15 mm of relief; plate tone +-2.5 % | "blending it in with the vanilla elevator look": the pads beside it are coursed horizontally and panelled; the hub's seam treatment keeps the family resemblance. The first cut measured the walls from the crown and every wall seam ran diagonally (the shoulder drops toward the rear); coursing from the floor fixed it |
| The liner, trough walls, well, ceiling, lip, rear cap inside and channel in gunmetal; the liner plated like the skin, the well coursed every 1.5 m; the pit floor and the receiver's landing `#26282E` with 1 m plates along the descent and 12 radial plates on the landing | a dark interior that reads as a lined shaft, as the design pass asked; the receiver reads as a platform, not a hole |
| **The hub's AO / bevel / cavity layer** baked on this atlas (`depot_bake_ao.py`, each entity occluding only itself, 30 s on the RTX 4080, tangent residual 0.001) and composited as the hub does (AO .55, edge light .10, cavity roughness .20, bevel reoriented), never on a lit texel | the hub's premium read came from this layer; same knobs by value |
| `verify_depot.py` compares the approved shell **by vertex position alone** and gains UV checks (islands by connectivity, 0 texels claimed twice, 0 bleed collisions, density floors) and map checks (the proof names this atlas by `uv_sha256`, the four TGAs at the proof's sizes and hashes, SI 0 or 102 only, every lit texel the deep blue, RM's roughness written twice, the material source and its ref present) | the key used to carry the swatch-cell UVs; brief 28 relays every UV |

Not changed: geometry, footprint, spots (the FBX sha is the design pass's successor only through the
UVs), vanilla's elevator, cabin, rope and track art, the dev Lua, the dome build.

## The maps

| file | size | bytes | sha256 |
|---|---|---|---|
| `SMROptInElevatorDepot_BC.tga` | 4096 | 67,109,403 | `dbe4969bcbb2ac4054cb81efb42ace8c2c5082fa500e1b082b3ea87522a33df4` |
| `SMROptInElevatorDepot_NM.tga` | 4096 | 67,109,403 | `dec87dc385a9d7588214cb5880dca149d86a0f5a2de01f9b3e19112acdc3f65b` |
| `SMROptInElevatorDepot_RM.tga` | 2048 | 16,777,755 | `e29ce7970d3b1943c54abe2ab449c3ac0159f947be2774287457c8461942d624` |
| `SMROptInElevatorDepot_SI.tga` | 4096 | 67,109,403 | `dc0bbab7fecac6ccca00d4211a482e8fc0eebb16a92ad6e38ba98d3d99900cf5` |

`blender --background ElevatorDepot_work.blend --python-exit-code 1 --python depot_paint.py` at Assets
`c660d60`: 8,611,627 covered texels at 4096, 138,522 lit, bleed 8 texels, 42.8 s of raster and
theme, 64.7 s in all; the AO layer applied on 9,932,046 eligible texels (mean AO .7425). Atlas
`uv_sha256` `f2dd0167d4753aae160bf10b9b122e52a8c8449503e6b2e58906233c6833df39`. The TGAs are
git-ignored (`**/textures/`) like the hub's; `export/paint_proof.json` carries the knobs, the
per-piece texel counts and these hashes.

`blender --background --factory-startup --python-exit-code 1 --python verify_depot.py` →
`export/verify_depot.json`, **PASS** (`failures: []`): 7,758 approved shell faces preserved, 3,555
added (unchanged from the design pass), 30 footprint hexes, 14 spots, 41 rays, UV 0 outside / 0 zero
area, 476 + 24 islands by connectivity = the builder's, 0 two-island texels, 0 bleed conflicts,
density min 14.0 / p1 14.67 / median 15.53 / max 17.44 texels/m at 2048, the four maps at the
proof's sizes and hashes, 138,522 lit texels at SI 102 and none elsewhere.

## Per piece: the render

`SMR-Assets/elevatorstation/blender/review_paint/index.html` (`compose_paint.py`): the owner's
screenshot beside the painted render from that angle, day and night where it matters. Blender
lighting on a proxy elevator; the night glow is scaled x8 for the eye and says nothing about the
game's level.

| piece | sheet | what to look at |
|---|---|---|
| the shell's skin, skirts, apron | `sheet_1_behind`, `sheet_5_side`, `sheet_7_closeups` | the plated ivory hull: courses on the walls, plates over the crown, the belt at the shoulder; the navy skirting and the apron's stripe; the silver ribs |
| the mouth: collar, gasket, glow edge | `sheet_2_track`, `sheet_7_closeups`, `sheet_8_night` | the polished collar, the navy gasket, the blue edge lit at night |
| the deck and pillar | `sheet_3_join` | brushed silver at vanilla's profile, the dark channel, navy edge lines |
| the interior and the pit | `sheet_9_interior`, `sheet_6_front` | the plated gunmetal liner, the 1 m floor plates down the descent, the black rear cap, the guide lines |
| the well and the core | `sheet_4_core` | the coursed gunmetal well, its two blue rings, the apron diving into the ring |
| the receiver (underground) | `sheet_9_interior`, `sheet_8_night` | the landing's 12 plates and ring seam, the blue ring, the silver cradles |

What the owner said: nothing yet. The renders are theirs to judge before the import.

## The import (owner), when brief 27 allows

`SMR-Assets/elevatorstation/blender/README.md`, "The owner's import for the paint pass". In short:
checkpoint committed (`cffb57a`), game closed; Mod Editor, the depot mod; the GFXMaterial
`SMROptInElevatorDepot` is already in the mod with its four map paths; EntitySpec
`SMROptInElevatorDepot` → `mesh` → Open in Importer, Material **SMROptInElevatorDepot**, Import (this
compiles the four DDS); the same for `SMROptInElevatorDepotReceiver`; save the mod; quit. Then the
agent checks `Materials/SMROptInElevatorDepot.mtljson`, both `.entjson` files, the DDS sizes (about 11
MB BC1, 22 MB BC5, 11 MB BC4, 2.8 MB) and `metadata.lua`, and commits. The old
`SMROptInElevatorStation_*.dds` stay as the dome's unless the owner says otherwise.

## The sitting, after the import: about five steps a batch, one prediction each

Fresh placements on both maps; console lines where no SMRTK slot fits (brief 27's staged slots are
its own). The owner clicks and reads; the orchestrator reads the log on flush.

**P1, surface by day.** Place; the owner's four design-pass angles. Prediction: the hull reads as
plated ivory with crisp seams at the owner's inspection zoom, the collar polished, the skirting and
gasket navy, the deck silver like vanilla's; no blurred or jagged seam; no sand texture on the
depot; `SMRElevatorDepotDev.Report()` prints no Lua error and `entity imported`.
**P2, surface at night.** Prediction: every glow stroke (mouth edge, skirting lines, apron stripes,
pit guides, well rings) reads deep blue and does not bloom to white (the hub's .4 level); the
building dims when it stops working (vanilla `WorkLightsOff`).
**P3, underground.** Place, connect, `Measure()` then `Report()`. Prediction: `Measure()` completes
with a native ceiling reading (the nil-Z repair `493f518`, never read natively); the receiver shows
in the well with its plates, ring and cradles; the cabin at rest sits in it.
**P4, `receiver_z` by eye.** `SMRElevatorDepotDev.Set("receiver_z", -250)` / `-350` until the cabin's
underside meets the landing. Prediction: one value satisfies the owner; it is baked into the dev
Lua's default by brief 27's owner (its file) or recorded here for them.
**P5, the core's frame.** Against the painted well, ask the owner whether vanilla's frame inside the
core stays. It is baked into vanilla's `SpaceElevator` mesh (brief 26, B1): removing it is a change
to vanilla's elevator, stop 1 of this brief. Record the ruling; do nothing else.

## What I did not do, and the risks

- **No import, no game look**: brief 27 is live, so the owner's Mod Editor session waits, and the
  owner's yes on the renders comes before it anyway. The game's lighting, mip chain and BC1/BC5/BC4
  compression are untested on these maps; the hub's experience says 4096 survives them.
- **`receiver_z`, `Measure()` underground and the core's frame** are the sitting's (P3-P5).
- **The AO bake is not bit-reproducible on the GPU** (the hub's own note); its proof carries this
  run's hashes. The bake took 31,577 covered texels as failed rays and wrote them flat (0.37 %), and
  a few texels at AO 0.0 on both entities suggest inward-facing or enclosed faces the agent did not
  trace; nothing visible in the renders.
- **The hub's `uv_fingerprint` check between paint and bake is by the blend**, not the FBX: a
  re-run of `depot_build.py` re-lays the UVs and invalidates both the layer and the maps (the
  verifier says so), so the order is build → bake → paint → verify.
- **No colourisation map**: the depot's colours are fixed; vanilla's elevator takes the colony's
  palette through its CM. If the owner's colony palette shifts the pads away from `#D9D4CA`, the
  shell will not follow. A CM map is a later decision, not this pass.
- The plate pitch (2.6 m), the seam strength and the skin's gloss are by eye against the renders;
  each is one constant in `depot_paint.py` for the owner's next round.
- Brief 27 owns `10_ElevatorDepotDev.lua`; the one Lua-side item this pass may want (a
  `receiver_z` default once settled) is reported, not written.

## The owner's first look, 2026-10-01: another pass, handed to run B

Owner, verbatim, with three screenshots of vanilla's elevator in their colony: *"Ours looks
significantly more plain that the vanilla elevator compared to your renders. So I think we need
another pass, but you are also short on context, so I need your to hand the next run off to another
session."* Screenshots: SMR-Assets `owner_feedback/paint_01..03_*` (`ad93c4f`). They show the
elevator white with broad deep-blue bands (pad-top rings, two wall bands, blue plinths, blue hatch
trim) and our depot plain behind it. The cause, read on the 406343 tree after the verdict: vanilla's
texture is neutral and the colony scheme colours it through a colourisation mask and the template's
three palette names; our template names one. The handoff, with the colourisation route first and
painted bands as the fallback, is brief 28's "Run B" section. OI-35 is closed by this verdict; no
yes was given, and the import stays unrun.

## Run B (2026-10-01): the colony's colours, not ours

Build **25579348** (`python tools/doccheck.py --emit-fingerprint` at the start, GREEN; 1.1.1.406343).
Executed model: Claude Fable 5.1 (`claude-fable-5-1`), the brief's `_high` session, with two
subagents (Opus, `general-purpose` at the session's `high`, within the tier-2 cap: one decoded
vanilla's masks from the packs, one read the engine and importer chain on the 406343 archive).
Start: OptInPack `730188f`, SMR-Assets `1bbd34e`; `git pull` current in OptInPack, Assets has no
remote. `tasklist`: no `Mars.exe` at the start. Brief 27 committed `34a4ee6`..`62ca05f` beside
this run; its Lua, smoke and staged slots are untouched, the editor's uncommitted save of
`items.lua` and `metadata.lua` (mod version 12) is left as it stands, and the import was NOT run.

**State: the maps are rebuilt with a colourisation mask, desk-verified, and rendered by day and by
night from the owner's angles with the colony scheme simulated on the depot and on the proxy
elevator. Owed: the owner's yes on the renders (`review_paint/index.html`, sheets 0, 0b and 10
first), the two items below for the orchestrator (the template's three palette names; one Lua line
so the depot's own attached elevator takes the palette too), then the import after brief 27, then
the sitting on both maps.** Nothing here claims the look: the game decides.

### Commits

| repo | commit | what |
|---|---|---|
| SMR-Assets | `635022e` | the colourisation map in the painter, the verifier's CM gates, the material writer in the editor's format, the render material's palette mixes, the work blend |
| SMR-Assets | `8b53ab3` | the service frame keyed to its station; the renders in Space_Y and the default scheme, the proxy pads banded like vanilla's, the sheets; the README's run-B section and import steps |
| SMR-OptInPack | the commit after `62ca05f` | the material source with `Colorization` and `Colors = 3`; this section; OI-36; brief 28's row |

### Why route A, in one paragraph

The owner's three screenshots show vanilla's elevator white with broad deep-blue bands. Their
design-pass screenshots of 2026-09-30 show the same elevator plain, with no band at all. Vanilla's
texture carries no colour: its BaseColor `1321000` is flat grey and the colony scheme paints it
through a colourisation mask. A navy painted by value (route B) would be wrong in every save but
one; a mask marked the elevator's way follows the scheme in all of them, exactly as the elevator
does. So the hull, the collar, the skirt, the bands and the trims now carry no colour of their own.

### What the facts turned out to be (the route-A fact-find, 2026-10-01)

- **Vanilla's mask.** `Materials.fpk` binds `SpaceElevator_mesh.sub_1` to `Colorization
  Textures/1321009.dds` (Textures3, BC3 2048, 12 mips) with `Colors 4`, beside BC `1321000`, NM
  `1321001`, RM `1321002` and `Special 1321006` (`SpecialChannel 1`). The mask is four
  **exclusive one-hot** channels (no pair overlaps; A is strictly binary): R 22.1 %, G 52.7 %,
  B 15.3 %, A 1.8 % of texels above 128; 8.2 % in no channel (the dark discs, BC about 60, and the
  dark-teal window slots), which keep their painted colour. The BC under R, G and B is flat grey
  (means 196, 189, 200). Decoded copies: `SMR-Assets/trainhub/reference/raw/SpaceElevator__1321009_CM*.png`
  and `SpaceElevator__CM_sheet.png` (game art, git-ignored).
- **Which channel is which, on the elevator.** R = the pad tops' wide ring, the two six-spoke
  centre caps, the long top bands, the hatch and door frames; G = the panels; B = the two wall
  stripes, the plinth, the thin rim round the dark disc; A = small rectangles (unused by this
  building's template). The channels are slots 1..4 (ModTools `Docs/ModItemColonyColorScheme.md.html:18-25`:
  "red is part 1, green part 2, blue part 3, alpha part 4; black is ignored; edges must not blend;
  BaseColor greyscale at about 190-220 where tinted").
- **The names.** `Data/BuildingTemplate/SpaceElevator.lua:30-32` (406343): `palette_color1 =
  "outside_accent_1"`, `palette_color2 = "outside_base"`, `palette_color3 = "electro_accent_2"`.
  In Space_Y (`Data/ColonyColorScheme.lua:370, :373, :337`) those are mid blue (80,117,172), white,
  cornflower (105,144,208): the owner's screenshots. In the default scheme (`:422, :425, :392`)
  crimson, light grey, teal. Our template names one, `outside_TrainStation` (grey 100 in Space_Y).
- **How the colour combines.** `DL_Mesh_Colorize.h` (`Shaders.fpk`): `base_color *= 1 + Σ
  mask_i (C_i - 1)` with `C_i = (byte/255)^2` (`PROJ_COLORIZATION_GAMMA 2.0`): a multiply, so the
  BC under a mark must be the grey the colour is meant to come out at. Roughness and metal take
  the scheme's signed offsets per channel (`:22-27, :41-47`).
- **The material and the importer.** The GFXMaterial's property is `Colorization` with the count
  `Colors` (both C++ `MaterialData` members, `GFXMaterial.lua:561-563`); `ImportMap` refuses a mask
  whose count is 0 (`:1067-1068`), compiles 1..3 colours to BC1 and 4 to BC3, linear, Kaiser mips
  (`:1098, :1138-1142`), and clears the channels above the count (`:1046-1047`). The entity import
  compiles every non-empty map (`SceneImport.lua:1913-1925`) and the mtljson carries
  `Colorization`, `ColorizationChannel` and `Colors` (vanilla's `ElevatorSurface_mesh.sub_0.mtljson`
  as the example). "Secondary colours" are a different mechanism (the `Special` slot, a render-global
  palette, used by no shipped material): not needed.
- **The palette chain.** `PlaceBuildingIn` → `OnPlace` → `GetBuildingColors(GetCurrentColonyColorScheme(),
  self)` → `SetPalette` → `SetObjectPaletteRecursive` → `SetColorizationMaterials`
  (`Building.lua:2660-2664, :761-772, :747-749`; `Colorization.lua:846-858, :889-896`), gated by
  `CanBeColorized` = `ColorizationMaterialsCount(entity) > 0` (`:832-838`), i.e. the compiled
  `Colors`. `ReapplyPalettes` repaints on a scheme change (`ColonyColorScheme.lua:95-103`). A
  template's `palette_color1..4` are `template = true` properties the Mod Editor's template item
  shows and the generated class carries (`Building.lua:233-236`; `Composite.lua:182-187, :496-519`);
  `Station` and `10_ElevatorDepotDev.lua` override nothing (0 hits for `palette`, `coloriz`). So
  the depot's own template fields are honoured once set.
- **The depot's attached elevator misses the palette.** `D.Dress` attaches the 75 % SpaceElevator
  visual in `GameInit` (`10_ElevatorDepotDev.lua:140-143, :283-284`), which runs in a game-time
  thread after `OnPlace`'s synchronous `SetPalette`, and `OnMsg.LoadGame` (`:521-526`) re-dresses
  after a load; the recursion never reaches it. The owner's `paint_03` shows exactly that: the
  depot's pads plain behind vanilla's banded elevator in one colony. Painting the shell does not
  fix the pads; one Lua line does (below, for the orchestrator).
- **The Special map** `1321006` is one-channel BC4 on UV set 1: unrelated to the band layout.

### Design calls

| call | why |
|---|---|
| **Route A, the colourisation mask**; route B not built | the elevator is banded in one save and plain in another: only a mask follows that |
| **The depot names the elevator's three colours** (`palette_color1..3` = `outside_accent_1`, `outside_base`, `electro_accent_2`) and marks its pieces the elevator's way: whole pieces by `cm_channel()`: hull, apron, collar, rear cap, pillar foot → G; skirt → B (the pads' plinth); the hub's navy trims (gasket, skirting, apron stripe, deck edge lines, pad-side blocks) → R | the depot and the elevator then take the same colours from any scheme, by construction; the trims read as the elevator's frames and rings |
| **The pads' bands carried onto the shell** (`theme()`): the wall's second course above the floor (2.6..5.2 m, `WALL_BAND`) → B, the service panels sitting in it as vanilla's hatches sit in their stripe; two ring bands over the arch → R, the collar's back face (-33.15 m) to the first rib (-30.49 m) and the last rib (-16.51 m) to the rear (-13.5 m), each edge on a rib's painted seam (`RING_BANDS`); the service frames → R and their slats silver (`FRAME_LIP` .265 m beyond the half-width at the panel's station, `SERVICE_T`); the receiver landing's outer annulus 3.0..4.15 m → R | the brief's run-B list: plinth, lower wall band, a ring behind the collar and one before the rear cap, trim on the panels, the pad-top blue on the receiver's ring. The band heights are the pads' proportions read from `paint_03` (plinth, white course, broad band with the hatches in it) |
| **BC `NEUTRAL` (206,206,206)** under every marked texel, vanilla's panel grey; the plate tone, the seams and the AO layer still multiply | the shader multiplies, so this is the grey the elevator's colours come out at |
| **Unmarked, keeping their paint**: every glow stroke, the gunmetal interior, the floors, the silver ribs, deck, pillar, cradles and slats | as vanilla's hatch louvres and dark discs keep theirs; the hub's silver and glow are the hub's theme |
| **Hard mask edges per sub-texel sample** (`within()`), no antialias | the ModTools rule; the four samples still soften the single edge texel, as the compiler's mips would |
| **CM at 2048** (BC1 for three colours, about 2.8 MB compiled); BC, NM, SI stay 4096, RM 2048 | vanilla's own size; every colour edge lies on a painted seam or a piece boundary, which the 4096 maps keep crisp |
| The hub's ivory `#D9D4CA` and navy `#162248` are no longer bytes in the maps | they are what the renders' schemes stand in for; the roughness and metal knobs stay |
| **The renders simulate a scheme** (`depot_paint_render.py --scheme`): Space_Y by default, the default "Surviving Mars" scheme for sheet 10; the proxy pads carry vanilla's band layout in the scheme's colours; roughness and metal offsets are not simulated | the owner judges the depot beside what their elevator looks like, and sees it follow a scheme rather than a paint |

Not changed: geometry, footprint, spots, UVs (`uv_sha256` `f2dd0167…` as run A), the AO layer, NM,
RM and SI (same hashes as run A), vanilla's art, the dev Lua, the dome build.

### The maps

| file | size | bytes | sha256 |
|---|---|---|---|
| `SMROptInElevatorDepot_BC.tga` | 4096 | 67,109,403 | `7a1240d264030d24595fd06c89b99b0303d7d4f88a9ef0bbc64d5d10a1a2e57b` |
| `SMROptInElevatorDepot_NM.tga` | 4096 | 67,109,403 | `dec87dc385a9d7588214cb5880dca149d86a0f5a2de01f9b3e19112acdc3f65b` (run A's) |
| `SMROptInElevatorDepot_RM.tga` | 2048 | 16,777,755 | `e29ce7970d3b1943c54abe2ab449c3ac0159f947be2774287457c8461942d624` (run A's) |
| `SMROptInElevatorDepot_SI.tga` | 4096 | 67,109,403 | `dc0bbab7fecac6ccca00d4211a482e8fc0eebb16a92ad6e38ba98d3d99900cf5` (run A's) |
| `SMROptInElevatorDepot_CM.tga` | 2048 | 16,777,755 | `63fb86a0cf267ffa2717b75f8e9eaa62f88e0a5fec4d6651b3af9679d50a13c2` |

`blender --background ElevatorDepot_work.blend --python-exit-code 1 --python depot_paint.py` at
Assets `635022e`: 81.5 s; 8,611,627 covered texels at 4096; the CM census by strongest channel
(`cm_census_at_raster_size`): accent R 372,435, base G 1,096,958, stripe B 213,420, fourth A 0,
unmarked 6,928,814, which sum to the covered count; 138,522 lit; the AO layer applied as before.
Raw DDS estimate 50.3 MB (run A's 47.5 plus the CM). `export/paint_proof.json` carries the knobs,
the census and the three palette names the template needs.

`blender --background --factory-startup --python-exit-code 1 --python verify_depot.py` →
`export/verify_depot.json`, **PASS** (`failures: []`): the geometry, UV and run-A map gates as
before, plus the run-B gates: five maps at the proof's sizes and hashes; the CM one-hot or nothing
(0 texels with R+G+B > 1, 0 with A written); 0 lit texels marked; 0 fully marked texels with a
tinted BC; no channel empty (at 2048: R 157,968, G 324,508, B 59,600, unmarked or edge 3,652,228,
summing to 4,194,304); the material source carries `Colorization` and `Colors = 3`.

### The material source

`tools/devmods/elevator_station/SourceData/GFXMaterial/SMROptInElevatorDepot.lua`: the painter now
writes the editor's own format (the editor's 2026-10-01 re-save of this file was the model: the
comment line gone, non-default properties in byte order), plus two lines after `BaseColor`:
`Colorization = "…\SMROptInElevatorDepot_CM.tga"` and `Colors = 3`. The editor's uncommitted
`items.lua` and `metadata.lua` are not touched (the `{6}` ref is present, so the painter leaves
`items.lua` alone).

### Per piece: the render

`review_paint/index.html` (`compose_paint.py`), Space_Y unless said; Blender lighting on a proxy
elevator banded like vanilla's; the night glow scaled x8 for the eye.

| piece | sheet | what to look at |
|---|---|---|
| the owner's angles | `sheet_0_owner_above` (their `paint_02` beside `paint_02_above`), `sheet_0b_owner_beside` (their `paint_03` beside the side view) | the depot in their elevator's colours: the rings on the arch, the wall band, the skirt |
| the shell's skin, skirt, apron | `sheet_1_behind`, `sheet_5_side`, `sheet_7_closeups` | the hull in the base colour, plated; the ring band behind the collar and the one before the rear cap in colour 1; the wall band in colour 3 with the service frames in colour 1 and the slats silver; the skirt in colour 3 |
| the mouth: collar, gasket, glow edge | `sheet_2_track`, `sheet_7_closeups`, `sheet_8_night` | the polished collar in the base colour, the gasket in colour 1, the blue edge lit at night |
| the deck and pillar | `sheet_3_join` | silver, the edge lines in colour 1 |
| the interior and the pit | `sheet_9_interior`, `sheet_6_front` | unchanged gunmetal and plates |
| the well and the core | `sheet_4_core` | the well gunmetal; the proxy core banded |
| the receiver | `sheet_9_interior`, `sheet_8_night` | the landing's outer annulus in colour 1 round the plates |
| two schemes | `sheet_10_schemes` | Space_Y beside the default scheme: the depot follows the scheme; the glow, silver and gunmetal do not |

What the owner said about run B: nothing yet. The renders are theirs to judge before the import.

### For the orchestrator (brief 27's files; reported, not written)

1. **The template's palette names.** `SMROptInElevatorDepotDev` needs `palette_color1 =
   "outside_accent_1"`, `palette_color2 = "outside_base"`, `palette_color3 = "electro_accent_2"`
   (today only `palette_color1 = "outside_TrainStation"`). Either brief 27's owner sets them in the
   editor's `Data/BuildingTemplate/SMROptInElevatorDepotDev.lua` and the generated file, or the
   owner sets them in the Mod Editor's template item at the import (the item shows the four fields).
   Without them the shell takes grey 100 on channel 1 and white on the rest in Space_Y.
2. **The attached elevator.** After the attach in `D.Dress` and after the `LoadGame` re-dress,
   apply the building's palette to the visual: `SetObjectPaletteRecursive(visual,
   GetBuildingColors(GetCurrentColonyColorScheme(), self))` (`Colorization.lua:846`,
   `ColonyColorScheme.lua:20`), or simply `self:SetPalette(GetBuildingColors(…))` once the attach
   exists. With item 1 in place the attach then takes exactly vanilla's colours. Evidence: the
   owner's `paint_03`; the chain above. The train hub's `20_TrainHub.lua:1150-1177` does the
   per-object variant on its own attaches.
3. **The import steps** below, once brief 27 releases the editor.

### The import (owner), when brief 27 allows

`SMR-Assets/elevatorstation/blender/README.md`, "The owner's import for the paint pass". The run-A
steps stand, with three changes: in the GFXMaterial check that **five** slots are set (BaseColor,
Colorization, Normal, RM, SI) and **Colors = 3**; in the template item set the three palette names
(item 1 above) unless brief 27 did; after the Import, `Textures/` carries
`SMROptInElevatorDepot_CM.dds` (BC1 2048, about 2.8 MB) beside the four, and
`Materials/SMROptInElevatorDepot.mtljson` carries `"Colorization"`, `"ColorizationChannel": 0` and
`"Colors": 3`. The stop in the brief: if the editor refuses the slot or the colony palette does not
reach the entity in game, report it with the evidence and fall back to route B.

### The sitting, after the import: about five steps a batch, one prediction each

**P1, surface by day.** Place; the owner's four design-pass angles. Prediction: the hull is the
colony's base colour and the bands the scheme's colours 1 and 3, the same bytes as the vanilla
elevator beside it; the service frames and the gasket in colour 1; seams crisp at inspection zoom;
`SMRElevatorDepotDev.Report()` prints no Lua error and `entity imported`. The depot's own attached
pads stay plain until item 2 lands: say so, do not read it as a map defect.
**P1b, a scheme change.** Command Center → colony colour scheme → another scheme. Prediction: the
depot repaints with the elevator (`ReapplyPalettes`); the glow, the silver and the gunmetal do not.
**P2, surface at night.** As run A: every glow stroke deep blue at the hub's level; the building
dims when it stops working.
**P3, underground.** As run A: `Measure()` with a native ceiling reading; the receiver's landing
with its colour-1 annulus.
**P4, `receiver_z` by eye.** As run A.
**P5, the core's frame.** As run A.

### What I did not do, and the risks

- **No import, no game look**: the compile of a one-hot mask to BC1 and its mips, the scheme's
  roughness and metal offsets on our RM, and the colour under the game's light are untested;
  vanilla ships the same mask format at the same size.
- **The owner's scheme is not known**: Space_Y matches their screenshots by eye; the renders would
  differ in hue under another blue scheme, the mechanism would not.
- **The attached pads** stay plain until the Lua item lands (brief 27's file).
- **The fourth colour** is unused, as on the elevator; `Colors = 3`.
- `receiver_z`, `Measure()` underground and the core's frame are the sitting's (P3-P5).
- The render proxy's bands are placed by eye from the owner's night screenshots; the proxy is
  not vanilla's mesh.

### Run B, continued (2026-10-01): the two handed-over items landed

The orchestrator, `063a10d`: with brief 27 closed, items 1 and 2 of "For the orchestrator" are brief
28's. Both are in the OptInPack commit after `3bed14d`. Executed model as above (Claude Fable 5.1,
`claude-fable-5-1`, the `_high` session; no subagent in this part).

- **Item 1, the template.** `Data/BuildingTemplate/SMROptInElevatorDepotDev.lua` now names
  `palette_color1 = "outside_accent_1"`, `palette_color2 = "outside_base"`, `palette_color3 =
  "electro_accent_2"`; the fourth is unset, as on the elevator. The generated class file
  (`Code/BuildingTemplate/*.generated.lua`) is the editor's output and was not hand-edited: the
  owner's Mod Editor save at the import regenerates it, and until that save the game's class still
  carries `outside_TrainStation`. Desk check after the save: `grep -n palette_color
  tools/devmods/elevator_station/Code/BuildingTemplate/SMROptInElevatorDepotDev.generated.lua`
  prints the three names. In the same source the description's "Its cabin runs for show only; no
  cargo crosses maps yet." became "Its cabin carries cargo between the maps once an hour; set each
  resource's rows on the surface half." (the brief carried this into the editor session; the source
  is what the editor reads, so it is set there and the editor step is a check).
- **Item 2, the Lua.** `10_ElevatorDepotDev.lua`: `paint_rig(bld, rig)` runs at the end of `D.Dress`:
  `GetBuildingColors(GetCurrentColonyColorScheme(), bld)`, then `SetObjectPaletteRecursive` on the
  elevator, the tunnel, the receiver, the cabin and each rope tile; the dressed log line gains
  `palette=N`, the pieces painted. `SMROptInElevatorDepotDevBase:SetPalette` calls
  `Building.SetPalette` and then paints the free cabin, so a scheme change (`ReapplyPalettes`,
  `ColonyColorScheme.lua:95-103`) reaches it too; the attached pieces are reached by vanilla's
  recursion. Both are guarded with `rawget(_G, …)`, so the smoke's mock world runs them as no-ops.
  Nothing else of brief 27's behaviour was touched: the diff is two functions, one call and one
  format string.
- **Smokes.** `props_smoke.py`: PASS on the live tree. `wiring_smoke.py` on the live tree FAILS at
  its §10b hub cross-check (`the hub fit_title has two divisions`) before and after this change:
  brief 29's `b551930` rewrote the hub's `fit_title`, and 29's report (`3bed14d`) records the
  depot smoke's §10b as 29's owed item. In a scratch mirror holding this Lua, the smoke, its slots
  file and the hub file at `063a10d` (pre-29): `wiring_smoke: PASS`, every section including the
  LoadGame re-dress, so the change itself breaks nothing the smoke covers.
- **What changes above.** The import's step 1 is a check, not typing; after the save, the
  generated-file check; the sitting's P1 prediction: the attached pads take the colony's colours
  at the dress (`palette=` at least 3 on the surface: elevator, cabin, ropes; the receiver adds one
  underground), no longer plain. Before the import, the shell's own entity has no mask and stays
  as it is; the pads paint regardless.
- **Still owed.** The owner's yes on the renders, re-asked as OI-39: OI-36 left the owner's list
  with brief 27's close (`d0a46ce`) before the owner had acted on it. Then the import, then the
  sitting.
