# Train hub texture: our own textures, built in Blender

## Authority

- **Owner, 2026-09-19:** the Tripo texture pass was tried and dropped; texture the hub in Blender
  ourselves. This is spec §9's "Our own textures: the fallback"
  (`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`). Settled; do not re-argue Tripo.
- **The look (owner, 2026-09-19, spec §9):** the vanilla station's colour scheme, clean white and
  red, with the hex-pattern floor, but *"more clean / modern / high tech"*. **Not** the brushed
  metal or the slatted look of the station's older parts. No entrances, no decorative door.
- **Testing depth (owner):** a smoke test only. You are judged on renders and on a clean
  re-import; the owner's one look in the game is the check that counts.
- The geometry is settled and must not move: the owner approved the shape (OI-15, OI-16), the spots
  and footprint are measured on the hex grid, and the mesh, entity and spot names are permanent.

## Start

`git log --oneline -5`, `git pull`. Everything you build lives **outside this repo**, in
`C:\Dev\SMR-TrainHubAssets\blender\` (`README.md` there is the pipeline). Put the end state in the
todo tool before any write. Facts, each with the command that could falsify it:

- **The export body is one joined mesh** `SMROptInTrainHub6` (12,886 verts, 11,666 polys) under
  `Origin`, with one material and the spots and surfaces parented to it. `export_prep.py` writes
  `export\SMROptInTrainHub6.fbx`. Glass is left out (`INCLUDE_GLASS = False`). Measured with
  `blender --background export\TrainHub_export.blend --python <probe>` printing meshes, polys and
  UV layers, using `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`.
- **Its UVs are unusable.** It has a `UVMap` layer, but 10,586 of 11,666 faces have zero UV area.
  The layer is Blender's leftover primitive default. Unwrap it fresh.
- **The importer takes one material per mesh node** (`SceneImport.lua:1877-1885`, `:4018-4024`;
  "Contains multi-materials. Not supported yet."). Splitting the body into more nodes, each with
  its own material, is allowed. The Importer's Material dropdown lists only `Default` and **mod
  materials**, so the game needs a GFXMaterial item in the mod. **The owner makes it in the Mod
  Editor**; you do not.
- **Reference for what a game building material carries:** the vanilla station uses
  `TrainStationBig_T1` with an atlas `Station_BC.dds` and a colour-mask `Station_CM.dds` (3
  colours), in `Materials.fpk` and `Textures3.fpk`. `tools/flpk_extract.py` reads `.fpk`. The
  game install path is volatile; read it with a command (Steam `libraryfolders.vdf`). The
  worked mod sample is under the game's `ModTools\Samples\Mods\`.
- **`C:\Dev\SMR-TrainHubAssets\tripo_textured\` does not exist.** Nothing from Tripo is coming.

## End state

1. **A textured export.** Unwrap the body (your call: one atlas on one node, or two nodes with a
   material each). Generate the textures procedurally in Blender and bake them to images: white
   glossy panels, thin red accent stripes, a light-grey **hex-pattern floor** on the platforms
   with relief, and dark slate-blue storage pads. **All six sides must match** (the hub is
   six-fold symmetric; sharing one sector's UVs is a lever, your call).
2. **The maps the game's material takes**, written as image files the Mod Editor's GFXMaterial
   accepts. Find out from the ModTools docs, the sample mod and the Mod Editor source which
   formats and channels those are. Base colour first; then the normal or relief map and any
   roughness or shine map; then a colorization mask **only if it is cheap**. Files go in
   `blender\textures\`.
3. **`export_prep.py` rerunnable headlessly**, keeping the new UVs and writing the FBX. Keep the
   current untextured FBX as `export\SMROptInTrainHub6_untextured.fbx` first. Prove the geometry
   did not move: the spot empties and the `hex_shape`, `Collision` and `Selection` surfaces read
   the same transforms before and after, and the mesh's own vertex positions are unchanged apart
   from splitting seams.
4. **Previews:** `preview_textured_*.png` renders from the views `render_previews.py` already
   uses, plus a close-up of the floor and of one portal.
5. **The owner's steps**, at most five, written into `blender\README.md`: the GFXMaterial item, its
   texture slots, assigning it in the Importer, the re-import and the save. Verify each against
   the docs, the sample mod and the editor source. The orchestrator walks the owner through
   them; you do not drive the Mod Editor.

**Done means:** the previews match the look direction, the FBX carries UVs and one material per
node, the geometry is proved unmoved, and the README carries the owner's steps. If time runs out,
drop the colorization mask first, then the relief map, then the floor's detail; never drop the
geometry proof.

## Scope

In: `C:\Dev\SMR-TrainHubAssets\blender\` and its `textures\` and `export\` folders.
Out: this repo, entirely. Build 2 is editing the dev mod, the spec and the checklist in the
shared tree right now. Do not write the mod, the entity files or the Mod Editor's save. Your
report is your final message; the orchestrator folds it into the spec.

## Stops

- **The game's material cannot take what the pipeline produces** (an unsupported format or channel
  layout, or a texture size the importer refuses): report the exact message and the formats
  found, and stop.
- **The unwrap moves geometry or a spot:** stop and report the measurement.
- **The procedural look stays flat or muddy** after a real attempt: report the renders and what
  you tried, and stop; the owner decides the next route.

## Do not claim

- "It looks right in the game" or "the texture works". The narrower claim is what you showed:
  the renders, the FBX and the geometry proof. The re-import and the owner's look settle the rest.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` once the owner's re-import
is done and recorded in the spec.
