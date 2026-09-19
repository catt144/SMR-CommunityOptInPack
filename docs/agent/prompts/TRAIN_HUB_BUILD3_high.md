# Train hub build 3: the footprint, the drone section and the service-area overlay

## Authority

- **Owner, 2026-09-19, in the build 2 sitting** (screenshots `C:\Dev\SMR-ScreenCaptures\SMRTK_0017.png`
  and `SMRTK_0018.png`; the log's `SMRTK_ACTION slot_1` line): four of the six lines cannot attach,
  *"the four are off by one hex"*, and the stub and track heights do not line up. The infopanel has
  the service-area slider but no map overlay, so *"a player has no idea what the service area can
  actually do"*; the vanilla drone hub shows its hex range and a Drones section (count, load).
  **Owner, same sitting:** the hub shows no drone count and has no prefab plus or minus, so a
  destroyed drone can never be replaced. Drone replacement from prefabs is wanted, as the vanilla
  drone hub does it; this **reverses build 2's omission** of the prefab controls. Settled: fix all
  four. Nothing here is frozen (`CLAUDE.md`); both bans in `FIX_POLICY.md` bind,
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
  Prefabs" (this hub has no prefabs; omit) and draws the service hexes on the map when selected.

## End state

1. **The footprint reads 61 hexes and 4 on all six lines.** Cheapest test first: script a shrink
   of each `eHexShape` triangle about its own hex centre (about 90% of the circumradius) in the dev
   mod's `entjson`, reload, and read the count and the radii. If they hold, make the durable fix
   in `C:\Dev\SMR-TrainHubAssets\blender\hub_skeleton.py` (`add_hex_face` takes a `shrink`; the
   `hex_shape` call passes none and welds with `remove_doubles`), then re-run the pipeline so the
   FBX carries **both** the footprint and the finished texture (the texture pass is done there;
   its README has the owner's steps). Prove the spots and geometry did not move, as that pass did.
   Your call how, and whether the importer needs anything different for un-welded faces.
2. **The service-area overlay** on the map when the hub is selected, at the slider's radius and
   following the slider. Your call: reuse vanilla's or build our own.
3. **The drone section** on the infopanel at the vanilla look: drone count against the hub's
   capacity, load, available prefabs, and the prefab plus and minus that order a replacement, so a
   destroyed drone can be replaced from the colony's prefab stock. Your call whether to reuse the
   vanilla Drone Hub's machinery or build the smallest equivalent; it must not need a new persisted
   name (ban 1), and if it does, report that instead.
4. **The height.** Measure the vanilla track element's z against the connector's z 800 (spec §9's
   unverified item) with a slot dump. Fix in Lua if the code is wrong, in Blender if the asset is.
5. **Smoke with the owner**, about five steps at a time, one colony: attach six lines, trains stop
   at the hub, overlay and drone section read right at the slider's ends, destroy one drone and
   order a replacement from prefabs (the count returns and the stock drops), then the three-batch
   script's Batches 2 and 3 from `TRAIN_HUB_BUILD_20260918.md` §"Build 2". Also settle
   `resource_types` 19 against 21.
6. **Record** it in that report and spec §10; put the owner's re-import and anything else owed on
   `docs/PLAYTEST_CHECKLIST.md`.

**Done means:** a hub placed after the owner's re-import reads 61 hexes and radius 4 on all six
lines, attaches all six tracks without "Blocking objects", shows the overlay and the drone section,
and smoke-tests clean, and a destroyed drone can be replaced from prefabs. If time runs out, drop
the `resource_types` check, then the height (report the measurement only), then the overlay. Never
drop the footprint, drone replacement, or reload and salvage.

## Scope

In: the dev mod, the Blender pipeline in `C:\Dev\SMR-TrainHubAssets\blender\`, TestKit slots in
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

One-off. Delete this file, `TRAIN_HUB_BUILD2_high.md` and their rows in
`docs/agent/prompts/README.md` once the smoke test is recorded, and delete
`TRAIN_HUB_TEXTURE_high.md` and its row once the owner's re-import is done.
