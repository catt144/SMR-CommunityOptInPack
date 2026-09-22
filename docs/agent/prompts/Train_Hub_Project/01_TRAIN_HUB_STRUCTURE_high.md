# Train hub: look step 2 — the structure, its lighting, then the whole hub's GPU cost

**LIVE, one-off.** The owner fires it; the orchestrator parks or deletes it once done (owner,
2026-09-21). Authoring
state: tag `hub-lines-b2-lights-20260921` in both repos (restore point 3; its `RESTORE.md` is in
`B:\Dev\SMR\SMR-Shared\SMR-HubBackups\`). Empty `git diff --stat hub-lines-b2-lights-20260921..HEAD
-- trainhub/` (SMR-Assets) and `-- tools/devmods/train_hub/` (here) mean this brief's facts hold.
Start with `git log`, `git pull` in both repos.

**Where the lights brief left it (fired and closed, spec §9 "Lights step" to "Restore point 3"):**
the owner's hold "for the moment" is road finish B, thin deep blue (0,40,255) lines at SI 0.7 on
every arm, the structure's glow lines recoloured and levelled to match (`STRUCTURE_LINES`,
`ARM_LINE_WINNER = 5`, baked by `bake_thinlines.py`, delivered as `textures/thinlines_all/`), and
72 Lua spots along the arm lines (`20_TrainHub.lua`, `hub_light_*`). Restore points 1 and 2
(`hub-road-b-20260921`, `hub-road-b-nostrips-20260921`) stay the fallbacks.

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
- **The road is done: variant B, held,** with its deep blue lines and their lights as restore
  point 3 holds them.
- **Order (owner, 2026-09-21): "finish the model update and get its lighting done to test the gpu
  part because right now we would just be testing the tracks."** The hub off/on cost is measured
  once, on the whole hub, after the structure and its lights are in. No cost reading before that.
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
   the owner screenshotted (a ring seam, blue rim strip beside it). **Measure the blur's cause
   first, cheaply, before the heavy bake:** texels per metre on the ring and ribs (the UVs are
   frozen, so density is a ceiling supersampling cannot lift), and the compiled DDS against its
   source PNG at that close-up (block compression softens thin lines). Say which limits the look;
   it may change the per-map sizes. **Clarity at the sector overview:** seams and rib bands must
   still read once mipped down, so "restrained contrast" is judged there too, not only close up.
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

6. **The structure's lighting, after the owner keeps the maps:** real lights for the structure in
   the owner's deep blue, following the arm lights' pattern in `20_TrainHub.lua` (vanilla
   `PointLight`/`SpotLight` attached at Origin, positions computed in code, `DeleteOnLoadGame`,
   recreated from `GameInit`, `heal_after_load` and `OnSetWorking`; **a stopped hub destroys
   them, never dims them**; no spot, persisted class or saved field). Your call on where they sit
   (ring, portals, ribs, supports) and how many; small and dim beside the painted lines is what
   the owner chose on the arms, after rejecting lights that washed a platform. Extend
   `tests/look_smoke.py` with the count.
7. **The whole hub's cost, then and only then:** the owner's reading, same save, fixed camera, hub
   on screen, no trains in view, hub on against off (a stopped hub also stops its trains).
   `SMR-Assets\trainhub\blender\gpu_sample.ps1 -Label <on|off label> -Note '<save, camera>'` logs
   GPU memory and 3D utilisation; the owner's 120 fps cap hides cost in the frame rate, so uncap
   or read utilisation. Report the light count with it, and fill spec §9's `<<PENDING-RUN>>`.

Done means: the owner looks at the hub and says it feels premium, or names what stops it, and the
whole hub's off/on cost is recorded.

## Pass 2 — the owner's look at pass 1 (2026-09-21)

Pass 1 (assets `a2b9727`, imported in dev mod checkpoint `5f7ee27`) is in the game. The owner
looked close up at the pillars, a rib, a portal and the ring, and said **yes to all four fixes
below**. Pass 1 is not kept yet: take `snapshot_hub.py hub-structure-pass1-20260921` before you
change anything, so it is one step to undo. The palette is right and stays; the road, the deep blue
lines and their level stay held by value, as before.

1. **Rib glow bands are still stair-stepped.** The glow is the SI map, still at 2048 on a thin tube
   island, so the 4096 BC could not help. Take SI to 4096 and antialias the band's edge.
2. **Ring seams are soft and read as a doubled hairline** (a light line beside a dark one). Take NM
   to 4096 (the brief already allowed it) and make the groove one clean line. Lead, from the
   owner's close-up: the blue line steps where it crosses a seam, so check whether a painted seam
   sits on a UV island boundary and bleeds differently on each side.
   **The owner's fallback, in their words:** *"can we design over them to make it less noticeable
   if that doesn't work, put something there thats not a hairline seem."* If a crisp groove does
   not hold at this density, stop fighting the hairline and **design a feature at each ring seam
   position** that is readable at 7-14 texels per metre: your call among, for example, a wider
   silver joint band, a raised trim strip with a bevel, or a recessed channel. It must sit on the
   seam positions and read as deliberate. Keep the palette; a blue accent there is the owner's call,
   so offer it, do not ship it.
3. **Silver reads as a blurry chrome blob** (metalness .90, roughness .22 mirroring the terrain).
   Make it brushed metal: rougher (about .35-.45) and/or less metallic, your call by eye.
4. **Portal insert edge is ragged and hairy** against the white shell. Hard-edge it or widen the band
   so it covers the fringe; check the island bleed there. The dark sawtooth shading along the arch's
   facets may be the geometry, which is frozen: say so if it is, do not chase it with the maps.

Same close-ups again for the owner's second look. Report per point what changed and the raw sizes.

## Leads, not the route

- `BODY_SIZE = 2048` (`paint_concept.py:24`) sizes every map; you need it per map.
- Seams: `paint_concept.py:111` (track), `:131` (platform), `:139` (ring, about every 10 degrees
  around the ring, 25% darkening and a shallow `height` groove). They are drawn per texel from 3D
  position, so a higher resolution or supersample sharpens them without changing the UVs.
- The island bleed `dilate(..., steps=4)` is in pixels: at 4096 it covers half the distance.
- The painted seams' jaggedness is a diagnosis from the script, not measured. Confirm the seam
  positions in the screenshot match the script's spacing before you change anything.
- **The owner's night screenshot (2026-09-21, after the strips-off import):** the dome ribs' glow bands
  (`Rib_*`, `paint_concept.py`, `glow = .75*band(remainder(r,7)-3.5,.19,aa)`, one band every 7 units)
  show as jagged white splotches that the owner remembers as blue. The maps did not change there:
  the band's base colour is the same blue (about RGB 46,121,244) in the old and new BaseColor, and the
  lights agent proved the glow is byte-identical off the road. Read, untested: a saturated blue at a
  high SI modulation clips toward white at night, and the band is about 4 texels wide on a thin tube
  island, hence the jags. Since then the owner confirmed the clipping on the arm lines (SI 1.0 on
  the cyan-leaning `BLUE` "to white"; saturated deep blue at 0.7 held its colour), and the ribs now
  carry deep blue at 0.7 too; whether their jags survive is not yet looked at. Make the bands crisp.
  This is inside this step: the ribs are structure.
- The structure's glow colour and level are the owner's hold (deep blue, SI 0.7): keep them by
  value unless the owner rules. Your resolution change re-bakes them; prove they did not move.
- The spot light's aim in the arm lights assumes a spot shines along its own +X, turned a quarter
  about Y to face down; the owner liked the result in game, which is the only evidence for it.

## Scope

**File ownership (owner, 2026-09-21).** The maps work is in SMR-Assets and needs no Lua. Step 6
edits `20_TrainHub.lua`: do not start it while another brief that edits that file is in flight
(`02_TRAIN_HUB_LOADERRORS_low.md`); recheck `git log -- tools/devmods/train_hub/` first. Movement is
finished (parked), and the drone builds come after the hub look.

In: the structure's maps, the resolution change, the structure's lights block in
`20_TrainHub.lua` with its mocked smoke, and the whole-hub cost reading. Out: the road and its
lines and arm lights as held, glass, reactor, dome, geometry, UVs, spots, routing and movement
code. Out-of-scope findings go in the report.

## Stops (report instead of pushing on)

1. One material will not carry maps of different sizes, and all four at 4096 is not acceptable.
2. The structure cannot be separated from the road and glow by an existing face test without a
   geometry or UV change.
3. The importer or the game rejects the new sizes, or the cost reading shows the lights visibly
   cost frame rate on the owner's rig: report the count and the reading, and stop at the largest
   count that holds.

## Do not claim

Do not claim it looks premium, or performs, from a Blender render. Claim the maps you built, the
per-map raw sizes, the proofs, and what the owner's smoke showed.

## Deliver

1. Todo list first, one item per commit-and-verify unit.
2. Design smoke only. About five steps at a time.
3. Record in spec §9 with `doc-editing`, commit both repos with pathspecs.
4. **The B run (owner, 2026-09-21).** This is a long build, and the owner watches your context. If
   they tell you to split off into a B run, stop starting new work and finish only the
   commit-and-verify unit in progress, so both trees are committed and no bake or import is half
   done. Take a restore point if the owner has kept anything. Then write the B run's brief yourself,
   with `prompt-authoring`, as a one-off in `Train_Hub_Project/` with its row in that folder's README: the todo list
   as it stands (done, in progress, not started), the commits and tags that hold the state, what the
   owner has kept or ruled since this brief, and any decision you have made that the next worker
   would otherwise re-derive. Record the same state in spec §9. Do not restate this brief in it:
   point at it and at the spec. The B run starts from that brief's authoring sha, not from memory.
