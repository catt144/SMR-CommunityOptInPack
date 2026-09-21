# Train hub: look step 2 — the structure, premium at wonder scale

**LIVE, one-off. FIRE IT, THEN DELETE THIS FILE AND ITS MAP ROW in the fire commit.** Authoring
shas: SMR-OptInPack `03bfd59`, SMR-Assets `8e2e380` (tag `hub-road-b-20260921` is restore point 1).
An empty `git diff --stat hub-road-b-20260921..HEAD -- trainhub/` means the assets facts hold, or
the lights agent's paint half has landed (see Order). Start with `git log`, `git pull` in both repos.

**Order:** `TRAIN_HUB_LIGHTS_medium.md`'s paint half edits `paint_concept.py` and the same maps.
Fire this **after** that agent has committed it and taken `hub-road-b-nostrips-20260921`
(`snapshot_hub.py`). Its Lua half may run alongside: it owns `tools/devmods/train_hub/Code/`, you
never touch it. If the tag is absent, stop and tell the owner.

## Authority

The owner, 2026-09-21, settled all of this (spec §9):

- **The bar is premium.** *"I don't want to do all this work and have a product that doesn't feel
  like a wow to a view"*; the hub is wonder-sized and likely one per colony, taking a large part of
  a sector. It has to read at the sector-level overview, where the tracks are thin lines, and
  close up, where the surface is judged.
- **The 5 MB guard does not bind this mod.** Resolution is a look decision. **The plan: BaseColor at
  4096 supersampled; Normal, RM and SI at 2048; Normal up to 4096 only if the seam relief is still
  soft.** Your call on any per-map change with a stated raw size. Vanilla spends 4096 on wonders.
- **Keep the panel seams, and make them crisp.** The owner is fine with visible seams; the current
  ones are "jagged and blurry" everywhere.
- **The road is done: variant B, held.** The strips and lights on it belong to the lights brief.
- The model is FINAL and frozen at radius 6: no geometry, UV or spot change.
  `concept_guard.verify_scene()` before every bake.
- The owner's handoff package (`C:\Users\stkot\Downloads\TrainHub_Visual_Handoff_v1\TrainHub_Visual_Handoff_v1`,
  spec §9) is **reference only**. Its target: warm off-white shell (`#D9D4CA`, metallic 0.05,
  roughness 0.31), cool brushed-silver rails and trim (`#AEB9BE`, metallic 0.9, roughness 0.22),
  dark portal inserts (`#071016`, metallic 0.55, roughness 0.2), restrained surface detail, no
  grime. There is no clearcoat channel in the game. The owner said they *may* want a paint on the
  structure: this is a look for them to judge, so the restore points must make it easy to undo.

## End state

1. **The structure's maps** (ring, portal housings and hoods, ribs, supports, rails, trim, the
   deck's non-road surfaces): base colour, normal and RM built from the script, with real surface
   variety, not one flat colour. The blue-grey `HULL` that reads as paint is replaced.
2. **Crisp seams:** supersample the bake (4x, downsample) and set seam widths to at least 2-3
   texels at the map's density with restrained contrast. Compare before and after at the close-up
   the owner screenshotted (a ring seam, blue rim strip beside it).
3. **The road untouched by value:** the deck's base colour and RM equal the road finish (`PAD_BASE`,
   B's metalness and roughness) at every road texel, proven per texel by value. A byte-hash proof
   cannot hold once BaseColor changes size: re-pin `validate_pad.py`'s baselines at the new size,
   say so, and keep the proof.
4. **One owner import** (about five steps, the importer run compiles the DDS, `_shared/IMPORTER_FACTS.md`
   "Mod Editor pipeline"). The first import must confirm one material can carry BaseColor at 4096
   and the other maps at 2048; if it cannot, all four at 4096 is the fallback and you say what it
   costs. Report stale DDS as orphans; delete none without the owner's word.
5. **The owner looks in game**, at sector overview and close, day and night, and says what to change.
   Take a restore point (`snapshot_hub.py hub-structure-<step>-20260921`) when they say keep it.

Done means: the owner looks at the hub and says it feels premium, or names what stops it.

## Leads, not the route

- `BODY_SIZE = 2048` (`paint_concept.py:24`) sizes every map; you need it per map.
- Seams: `paint_concept.py:111` (track), `:131` (platform), `:139` (ring, about every 10 degrees
  around the ring, 25% darkening and a shallow `height` groove). They are drawn per texel from 3D
  position, so a higher resolution or supersample sharpens them without changing the UVs.
- The island bleed `dilate(..., steps=4)` is in pixels: at 4096 it covers half the distance.
- The painted seams' jaggedness is a diagnosis from the script, not measured. Confirm the seam
  positions in the screenshot match the script's spacing before you change anything.
- Leave the ring and portal glows exactly as they are unless the owner rules; their look is the
  owner's call after they see the shell.

## Scope

In: the structure's maps and the resolution change. Out: the road, the lights (Lua and the road
paint), glass, reactor, dome, geometry, UVs, spots, the dev mod's Code. Out-of-scope findings go
in the report.

## Stops (report instead of pushing on)

1. One material will not carry maps of different sizes, and all four at 4096 is not acceptable.
2. The structure cannot be separated from the road and glow by an existing face test without a
   geometry or UV change.
3. The importer or the game rejects the new sizes, or the frame rate visibly drops.

## Do not claim

Do not claim it looks premium, or performs, from a Blender render. Claim the maps you built, the
per-map raw sizes, the proofs, and what the owner's smoke showed.

## Deliver

1. Todo list first, one item per commit-and-verify unit.
2. Design smoke only. About five steps at a time.
3. Record in spec §9 with `doc-editing`, commit both repos with pathspecs.
