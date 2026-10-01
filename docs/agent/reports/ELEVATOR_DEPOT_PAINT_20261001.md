# Elevator Depot, the paint pass (brief 28), 2026-10-01

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
