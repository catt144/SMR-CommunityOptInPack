# Train hub build 2: the owner's drone rulings, then the asset

## Authority

- **Owner, 2026-09-19, in the hub's smoke test** (spec §10, "Owner rulings, 2026-09-19, from the
  sitting", `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`):
  - **Drone radius defaults to 10.** A slider up to **20** is *"maybe"*: build it unless it costs
    a new persisted field you cannot justify, and say which you did.
  - **The infopanel gets the vanilla drone hub's section:** drone count, load and service area.
  - **Testing depth:** *"bare minimum testing before we do the real model"*. This build gets a
    smoke test, not the prediction battery.
- The rest of spec §10's 2026-09-18 rulings stand as built (`886926b`). MODULE FREEZE is lifted
  (`CLAUDE.md`). Both bans in `FIX_POLICY.md` bind; so does spec §8.
- **The owner's asset** is approved in shape (spec §9, "The owner's asset"). The owner imports
  it through the Relaunched Mod Editor. That import, not you, answers §9's unverified list.

## Start

`git log --oneline -5`, `git pull`. This brief landed at the commit that
`git log -1 --format=%h -- docs/agent/prompts/TRAIN_HUB_BUILD2_high.md` names; if
`git diff --stat <that sha>..HEAD -- tools/devmods/train_hub docs/agent/reports/TRAIN_HUB_BUILD_20260918.md`
is empty, the facts below hold. Put the end state in the todo tool before any write.

## Where things stand

- The hub is the dev mod `tools/devmods/train_hub/` (mod id `SMR_TrainHubDev_20260918`). Its
  design record and the 2026-09-19 smoke-test result are `TRAIN_HUB_BUILD_20260918.md`; read its
  §"Sitting result" first. The hub passed boot, placement, six connectors, drones, cubes, reload
  and salvage with 0 Lua errors.
- The radius is `longest_line + hub_drone_reach` in `20_TrainHub.lua` `GameInit`, with no slider
  and no drone section (`customDroneHub` is conditioned on `DroneHubBase`). Its drones' reach
  mattered in the sitting: end stations 10+ hexes out got no maintenance and wore out in about
  seven sols at ultra speed.
- The asset pipeline and its outputs are outside both repos, at `C:\Dev\SMR-TrainHubAssets\blender\`
  (`README.md`). `export_prep.py` wrote `export\SMROptInTrainHub6.fbx` on 2026-09-19 for the
  owner to import. Checked by re-importing it into Blender: `Origin` > mesh `SMROptInTrainHub6` >
  25 spots and 3 surfaces, spot positions equal to the work file's. What the import carries:
  - **Entity `SMROptInTrainHub6`**, the template's id. Treat it as permanent once a kept save
    sees a hub.
  - Spots: `Trackconnector1..6`, `Trackdirection1..6`, `Top`, six `Box1` (one range, as
    `own_pallets` reads it) and six `WorkDrone`. Surfaces: `hex_shape`, `Collision`, `Selection`.
  - **Not carried:** `Ramparrive`, `Stop`, `Spawn`, `Rampdepart`, `Sign`. Once the body has
    `Trackconnector1`, `uses_body_spots` turns off every synthetic spot in `code_kind`, including
    these. Your call: keep computing them on the asset, or have the owner add them to
    `hub_skeleton.py`.
  - No UVs anywhere, so the default material; the glass is left out, because an opaque dome
    would hide the cargo. Texturing is a later pass.
  - **The hub stores 21 resource types**, not the ~15 the cube display was sized for: the
    sitting's CheatFill on a station filled `resources=21` (log id 172), and the source agrees
    (13 physical in `Data/Resource.lua` plus the Norman DLC's eight `ResourceIngredient` foods,
    `DLC/norman/Presets/Resource.lua`). Six beds share out 360 columns, which gives about 17
    columns per resource. `max_z` then comes to about 15, against the 10 the beds' placement
    assumed. In the smoke test, fill one hub with every resource and check the stacks against
    the ring and hoods. Also worth a look: whether food spoils in station storage (`Spoilage.lua`).

## End state

1. **Radius and slider.** Default 10 on a fresh hub. Your call how a hub built at 8 reads after
   the change; it must not need a migration of a persisted name (ban 1).
2. **Drone section** on the hub's infopanel: count, load, service area, and the slider if built.
   Vanilla's own section is the target look; your call whether to reuse its XTemplate or build one.
3. **Asset swap, only if the owner's import has landed** (an entity folder or ArtSpec item in the
   dev mod, or the owner says so). Set the template's `entity`, drop the stand-in's computed spots
   where the body supplies them, and run the body's `Box` branch of the cube display, which has
   never run. If the import has not landed, skip this item and say so in the report.
4. **Smoke test with the owner**, about five steps at a time, one colony (the owner's choice):
   boot, place, attach six lines, trains stop at the hub, the drone section reads right at 10 and
   at the slider's ends, save and reload, salvage, 0 Lua errors. Two open questions from the last
   sitting ride along: whether drones near the hub say "Controlled by: Train Hub", and whether
   salvaging a **vanilla** station with trains docked also removes them (the hub's did).
5. **Record** the result in `TRAIN_HUB_BUILD_20260918.md` (or a new report, your call) and spec
   §10; put anything owed by the owner on `docs/PLAYTEST_CHECKLIST.md`.

**Done means:** a hub placed after this build commands drones at radius 10, shows the drone
section, and smoke-tests clean in one colony. If time runs out, drop the slider first, then the
asset swap. Never drop reload and salvage.

## Scope

In: the hub's classes and template in the dev mod, TestKit slots in `80_AgentSlots.lua` (standing
permission, `tools/SMRTK.md`), the sitting, the records.
Out: the crossing-witness fix (a separate brief), OI-18's packaging tool, Module A, routing, the
four-connector hub, and the art itself.

## Stops

- **The import landed but the axis mapping or track height is wrong** (lines off the hex axes, or
  stub ends not meeting the track): report the measurement and stop the swap; the fix is in the
  owner's Blender pipeline, not in Lua.
- **The drone section cannot be shown on a `Station` without replacing a vanilla XTemplate
  wholesale**: report the options and ship the radius change alone.

## Do not claim

- "The asset works" from placement alone. The narrower claim is what the smoke test showed:
  lines attach, trains stop, cubes stack on the beds.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` once its smoke test is
recorded.
