# Train hub build 3: footprint, drones, overlay, power and charger

## Authority

- **Owner, 2026-09-19, in the build 2 sitting** (screenshots `C:\Dev\SMR-ScreenCaptures\SMRTK_0017.png`
  and `SMRTK_0018.png`; the log's `SMRTK_ACTION slot_1` line): four of the six lines cannot attach,
  *"the four are off by one hex"*, and the stub and track heights do not line up. The infopanel has
  the service-area slider but no map overlay, so *"a player has no idea what the service area can
  actually do"*; the vanilla drone hub shows its hex range and a Drones section (count, load).
  **Owner, same sitting:** the hub shows no drone count and has no prefab plus or minus, so a
  destroyed drone can never be replaced. Drone replacement from prefabs is wanted, as the vanilla
  drone hub does it. **Owner, later the same day: reversed.** The hub's drones will become
  on-demand repair drones in build 4 (`TRAIN_HUB_REPAIR_high.md`), so there are no prefab controls;
  see end-state item 3.
- **Owner, same day, design:** the hub **generates its own power**, enough for itself plus its
  maximum six stations (tracks merge station grids, `TrackBase:ConnectToGrids`, `Track.lua:97-122`),
  with **no workers**, and its **build cost and maintenance go up** to match. **The look,
  preferred: a scaled-down vanilla fusion reactor** (owner: it fits the theme better), covering
  about 3 to 5 hexes, **if it still looks good at that scale**; the owner then accepts
  **extending the hub's footprint** under it. **Fallback:** the vanilla advanced Stirling model
  inside the ring, unscaled (about one hex, from the owner's screenshot), with no footprint
  change. Either model is only the look; the hub's class makes the power. The
  **charger moves inside the hub's footprint**: today it sits on the first hex outside
  (`charger_offset`), about a hex out, and players can build over it.
  **Owner, same day, mid-sitting:** a drained drone will not path to the pad at
  `HexToWorld(1, 1)` inside the ring. **The owner's model: the underside is open and should be
  passable, like a dome** — its footprint blocks building but units move inside it. Reserving
  and passability are separate in this engine: `hex_shape` blocks building; the entity's
  `Collision` surface is what units treat as solid (`EntitySurfaces.Collision`,
  `BuildableGrid.lua:12`), and domes and other enterable buildings set `efWalkable = true`
  (`Dome.lua:476`, `Residence.lua:525`). INFERRED, not tested: our `Collision` is one solid disc
  over almost the whole footprint (`hub_skeleton.py`, `foot_radius - 1.0`, 1 m up), which blocks
  the underside. Required: shrink `Collision` to the parts that are really solid (ring wall,
  pillars) so the ground between opens, and add `efWalkable` if that alone is not enough. The
  owner recalls pathing options in the Importer, and the source has them: each mesh node has a
  Collider section, `ColliderKind` (none, box, sphere, convex up to 16 pieces) and `ColliderMask`,
  whose layers include `PassabilityMask`, `ObstructionMask`, `TerrainMask` and `VisibilityMask`
  ("controls which systems — passability, selection, placement — interact with it";
  `SceneImport.lua:3495-3515`, `:2008-2011`). The ModTools doc's `Collision` advice (a disc 1 m up
  "to block pathfinding units") is why the disc exists. Your call: shape the surface, or drop
  `PassabilityMask` where drones should pass; either rides the same re-import, and the owner's
  Importer steps must name the setting; keep
  `hex_shape` whole so nothing can be built over. The charger stops charging (item 3: the hub's drones
  never charge); its pad model stays, as build 4's launch pad. The passable underside still stands; note whether outside rovers or colonists now
  path through the hub. **And cut the raised platforms** (`PLATFORMS = False` in
  `hub_skeleton.py`; cosmetic, and they read as the station look the owner ruled out); it rides
  the same re-import.
  Settled: fix all of it. Nothing here is frozen (`CLAUDE.md`); both bans in `FIX_POLICY.md` bind,
  and so does spec §8 (`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`).
- **Testing depth (owner):** a smoke test only, never the prediction battery before the final build.
- **The owner does the Mod Editor steps** (one re-import); you do not drive it.

## Start

`git log --oneline -5`, `git pull`, `git status`. **No session is active.** The working tree holds
**build 2's uncommitted work** (`tools/devmods/train_hub/` Lua, template and `metadata.lua`,
`TRAIN_HUB_BUILD_20260918.md` §"Build 2", a spec §10 paragraph, and an edit to
`docs/PLAYTEST_CHECKLIST.md`). Read `git diff`, commit what is build 2's first, by pathspec, saying
it was smoke-tested in part on 2026-09-19 (Batch 1 only). Then put the end state in the todo tool
before any other write. This brief takes over build 2's unrun Batches 2 and 3.
Facts, each with a command that could falsify it:

- **The asset is right and the game reads it wrong.** Parse the `eHexShape` triangles in the dev
  mod's `Entities/SMROptInTrainHub6.entjson`, mapping centroids to the lattice (pitch 1,000 units,
  row 866.03): 61 hexes, 4 hexes on each of the six lines, six connectors at exactly 4.0 hexes,
  z 800. Every triangle vertex sits 577.3 to 577.4 from its nearest hex centre, which is the
  circumradius: **the footprint boundary lies exactly on shared hex corners.**
- **The game's footprint is bigger.** The boot log line `[TrainHubDev] ... line radii d0..d5 =
  5 5 5 5 4 4` and the owner's console read `#GetEntityOutlineShape("SMROptInTrainHub6")` = **85**
  (61 plus 24). The tracks on the four length-5 lines show the red "Blocking objects" at their first
  element; the two length-4 lines attach. Slot 1: `connected_tracks=0`.
- **Slot 1 also showed:** `custom_section=missing` (no drone count or load on the panel),
  `show_service_area=true` (the slider is present), `resource_types=19` where the notes say 21.
- **Vanilla's reference look:** the DroneHub panel reads "Drones 8/120", "Drones load", "Available
  Prefabs" with prefab plus and minus, and draws the service hexes on the map when selected.

## End state

1. **The footprint reads 61 hexes and 4 on all six lines.** Cheapest test first: script a shrink
   of each `eHexShape` triangle about its own hex centre (about 90% of the circumradius) in the dev
   mod's `entjson`, reload, and read the count and the radii. If they hold, make the durable fix
   in `C:\Dev\SMR-Assets\trainhub\blender\hub_skeleton.py` (`add_hex_face` takes a `shrink`; the
   `hex_shape` call passes none and welds with `remove_doubles`), then re-run the pipeline so the
   FBX carries **both** the footprint and the finished texture (the texture pass is done there;
   its README has the owner's steps). Prove the spots and geometry did not move, as that pass did.
   Your call how, and whether the importer needs anything different for un-welded faces.
2. **The service-area overlay** on the map when the hub is selected. **Owner, 2026-09-19: cut the
   slider; the radius is fixed at 15.** Remove the slider; a hub saved at any other radius reads 15
   on load through vanilla `work_radius`, with no new persisted name; the overlay shows 15.
3. **Drones: stop the prefab chase (owner, 2026-09-19).** Build 4 replaces the hub's drones with
   on-demand repair drones (a constant 30, no charging, no prefab controls). Here: remove the
   prefab section attempts (your call whether any drone count stays), keep the current drones as
   a stopgap, and stop them needing a charger: give each drone the hub controls a large per-drone
   `battery_max` and top it up (`Drone.lua:10`; no change to vanilla's battery code); then
   remove the working charger but **keep its pad model where it is**, inside the ring: build 4
   uses it as the drones' launch pad (owner, 2026-09-19).
   **Also remove the "Power grid" section from the
   hub's infopanel** (owner: the UI is getting tight, and Module A's per-resource controls will need
   the room); keep the hub's own Production and Consumption rows. Do it with a condition scoped to
   the hub's class; if it needs a vanilla XTemplate replaced wholesale, that is the brief's stop.
4. **Power, cost and the charger.** Starting values, proposed by the orchestrator and tunable by
   the owner in the smoke: **+70** (the hub's 10 plus six big stations at 10; vanilla
   `StationBig` draws 10, `StationSmall` 5, `FusionReactor` makes 200 with 8 workers); build
   cost about 60 Concrete, 40 Metals, 10 MachineParts, 15 Electronics; upkeep about 2
   Electronics. **The reactor, in this order, so there is one re-import:** (a) measure the vanilla
   `FusionReactor` footprint (`#GetEntityOutlineShape`) and pick a `SetScale` that brings it to
   about 3 to 5 hexes; (b) attach it in Lua, outside the ring between two arms, and have the owner
   judge the look in game, including its working FX; (c) if the owner approves, add a lobe to
   `hex_shape` in `hub_skeleton.py` under it, keeping every line's approach and the hexes beyond
   the connectors free, and let it ride the same re-import as the footprint fix and the texture.
   **Owner, 2026-09-19, after trying 50% and 60% in game: keep 75% at the current offset
   (`point(3897, 2250, 0)`), and extend the footprint only by the whole hexes the reactor sits over
   outside it** (estimated 3 to 5; compute the exact set). The lobe's hexes get the same inset as
   the rest of `hex_shape`, or the 85-hex rounding comes back; re-read the outline count and the six
   line radii after the re-import;
   (d) if not, attach the advanced Stirling model inside the ring (likely `StirlingGeneratorCP3`,
   the `StirlingGenerator` template's sponsor entity; check `IsValidEntity`). Prove the lines merge
   grids with one end station on a separate grid, and say in the report where the surplus goes
   when stations also touch the colony's cables.
5. **The height.** Measure the vanilla track element's z against the connector's z 800 (spec §9's
   unverified item) with a slot dump. **Owner, 2026-09-19, from two screenshots (stub beam against
   the vanilla track, and top-down at a portal): the fault is the asset's** (the stub sits off the
   track's level, and its slab is wider than the track). So **measure and report only**: the
   vanilla track's running-surface z (not its bbox top), the connector's z as the game reads it,
   and the stub's top z, as numbers. Change no Lua for it; the orchestrator corrects the stub in
   Blender (`hub_skeleton.py` `DECK_Z`, now 10.69 m, the bbox top) and it rides the re-import. If
   the numbers show the Lua places the track wrongly, report that instead of fixing it.
6. **Smoke with the owner**, about five steps at a time, one colony: attach six lines, trains stop
   at the hub, the power reading and a station fed through a line, the overlay at 15, a hub drone
   working with no charger and its battery staying up, then the three-batch
   script's Batches 2 and 3 from `TRAIN_HUB_BUILD_20260918.md` §"Build 2". Also settle
   `resource_types` 19 against 21.
   **Storage (owner, 2026-09-19, after a fill-all test where the stacks clipped the beams and the
   trains):** set `max_storage_per_resource` to **150000** (was 240000) in the template source
   `Data/BuildingTemplate/SMROptInTrainHub6.lua`, and regenerate the `.generated.lua`, never edit it.
   With 360 columns, 19 types gives 18 columns and `max_z` 9 (17 columns for 21 types, also 9),
   under the ten the beams and the trains' clearance were designed for. Confirm `max_z=9` from a
   slot readout and that a fill-all no longer clips the beams or a train at a portal.
7. **Record** it in that report and spec §10; put the owner's re-import and anything else owed on
   `docs/PLAYTEST_CHECKLIST.md`.

**Done means:** a hub placed after the owner's re-import reads 61 hexes and radius 4 on all six
lines, attaches all six tracks without "Blocking objects", shows the overlay at a fixed 15, powers
itself and its stations, and smoke-tests clean with its drones working without a charger. If time runs out, drop the
`resource_types` check, then the height (report the measurement only), then the overlay, then the
generator model (keep the power). Never drop the footprint, or reload and
salvage.

## Scope

In: the dev mod, the Blender pipeline in `C:\Dev\SMR-Assets\trainhub\blender\`, TestKit slots in
`80_AgentSlots.lua` (standing permission, `tools/SMRTK.md`), the sitting, the records.
Out: Module A, routing, the four-connector hub, OI-18's packaging tool, and the art itself.

## Stops

- **The shrink leaves the game's count at 85:** dump the outline's hex coordinates and report the
  rule the game seems to use; do not guess a second fix.
- **The overlay needs replacing a vanilla XTemplate wholesale:** report the options; ship the
  footprint and the drone section.
- **The re-export moves a spot or a surface:** stop and report the measurement.

## Do not claim

- "The footprint is fixed" from the `entjson` edit. The owner's re-import overwrites it. The
  narrower claim is the game's count and radii on a fresh hub after that re-import.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` once the smoke test is
recorded.
