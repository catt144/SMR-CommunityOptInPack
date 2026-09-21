# Train hub: real lights on the tracks and borders — six variants, one per arm

**LIVE, one-off. FIRE IT, THEN DELETE THIS FILE AND ITS MAP ROW in the fire commit.** Authoring
shas: SMR-OptInPack `57acb33`, SMR-Assets after `snapshot_hub.py` (tag `hub-road-b-20260921`). An empty
`git diff --stat 57acb33..HEAD -- tools/devmods/train_hub/Code/` and `git diff --stat
hub-road-b-20260921..HEAD -- trainhub/` mean this brief's facts hold.
**Restore point 1 exists**: tags `hub-road-b-20260921` in both repos and the copy of the ignored
maps and DDS in `B:\Dev\SMR\SMR-Shared\SMR-HubBackups\hub-road-b-20260921` (its `RESTORE.md`). Start with `git log`, `git pull` in both repos. The dev mod's `Materials/`,
`SourceData/` and `metadata.lua` carry the owner's uncommitted Mod Editor output: never revert or
stage them for them.

## Authority

The owner, 2026-09-21, settled all of this (spec §9, "Owner ruling ... (OI-24)" and the lighting
paragraph after it):

- **The road is settled: variant B** (`B_BlackMirror`, metalness 0.95), held. Do not touch the
  road's base colour or RM.
- **The owner dislikes the painted glow strips on the tracks and platforms and wants real lighting
  effects instead**, in red or blue, day and night. The paint may be revisited on the hub structure
  later; that is out of scope.
- **The owner will choose from a comparison: three reds and three blues, one variant on each of
  the hub's six arms.** They look in game and pick.
- The model is FINAL and frozen at radius 6: no geometry, UV or spot change. The lights come from
  our own Lua, not from `-L;` spot annotations.

## End state

1. **Paint half (SMR-Assets):** the road and platform glow strips, rim strips and floor curves
   removed from the deck and platforms so they cannot clash with the lights; the road stays plain
   polished black; every other texel unchanged, proven the way `validate_pad.py` proves it. The
   owner does one importer run (`_shared/IMPORTER_FACTS.md`, "Mod Editor pipeline": the importer
   compiles the DDS, saving the material does not). Give them about five steps.
   **Then, before any light code, take restore point 2** (owner, 2026-09-21): commit, have the
   owner's import verified by the `Textures/` timestamps, and run `python snapshot_hub.py
   hub-road-b-nostrips-20260921` from `SMR-Assets	rainhublender`. Report the tag and folder.
2. **Lua half (the dev mod, `Code/20_TrainHub.lua`):** real `PointLight`/`SpotLight` objects
   attached to the hub and placed along each arm's track edges and platform borders, six variants
   in one table keyed by arm so the owner can reassign by editing one line. Your call on
   the three reds and three blues: vary the things that change how it reads (hue and saturation,
   intensity and radius, spacing and height, point against spot), so the owner is choosing between
   looks, not near-duplicates.
3. **Lights follow the hub's working state and are on in the day as well as at night.** Off when
   the hub is off. Use the hub's own attach, recreate-after-load pattern
   (`20_TrainHub.lua` reactor visual, `set_hub_reactor_working`); the lights are visuals, not
   saved state.
4. **Tell the owner which arm carries which variant** in a way they can read in game (a log line
   naming each arm's compass direction and variant is enough), and how to reassign.

Done means: the owner can load the hub, see six arms with six different lighting looks, day and
night, and say which they prefer.

## Leads, not the route

- Vanilla places lights from Lua with `AttachToObject(obj, "PointLight", spot)` and colours them
  with `light:SetColor(...)` (`Mysteries/Fireflies.lua:85,109`; `UI/PlanetScene.lua:178` takes an
  arbitrary RGB), in the archived 1.1.0.403908 tree under `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive`.
  The annotation route's five names (`NightLightObjects.lua:14`) do not bind our own lights. Read,
  not yet run on a hub: confirm blue works before building six of them.
- The annotation system's night gate does not apply to lights we place ourselves. Whether a light
  is visible against full daylight is NOT measured; that is the owner's look to give.
- Positions: `line_hex`, `line_radii` and the connector geometry are already in the hub Lua. The
  spot set is off limits; compute positions in code.
- A real light lights the surface; it does not draw a fixture. If the borders read as nothing
  without one, say so and propose the smallest emissive dot as an option; do not paint strips.

## Scope

In: the paint removal above and the lights' Lua. Out: the hub structure paint, the road finish,
glass, the reactor, geometry, spots, routing and movement code, the annotation route.
Out-of-scope findings go in the report.

## Stops (report instead of pushing on)

1. A light cannot be placed from mod Lua, or does not take a saturated blue.
2. The lights need a persisted class, a new saved field or a change to the frozen model.
3. The light count needed for the look visibly costs frame rate on the owner's rig: report the
   count and what you measured, and stop at the largest count that holds.

## Do not claim

Do not claim a look works in daylight, or performs, from code or a Blender render. Claim what
you placed, what the code and logs show, and the smoke you ran. Both-configuration and toggle
ship tests are owed later, on the final build; this is a design smoke.

## Deliver

1. Todo list first, one item per commit-and-verify unit.
2. The paint half, proven, then the Lua half.
3. Design smoke only (the owner's call in the sitting): load, day, night, hub powered off. About
   five steps at a time (memory: short step batches).
4. Record in spec §9 with `doc-editing`, commit both repos with pathspecs.
