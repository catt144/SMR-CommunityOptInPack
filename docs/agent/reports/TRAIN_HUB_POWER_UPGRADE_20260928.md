# Hub Power Upgrade — 2026-09-28

Brief 21, owner ruling in train design §4.10. Implemented and desk-tested; **owner Mod Editor
save and combined cold-wave sitting owed**. No game launch, native heat or save/load claim.
Executed model: GPT-6 (Codex, identified in this transcript); no subagents.

## Change and save contract

- Train Cargo now gives only +100% cargo and +25% speed. Its existing purchase, claim,
  toggle and salvage behaviour remains; cold uses vanilla's penalty before the speed bonus.
- Power is slot 3: 30 Metals + 20 Electronics, no tech, independently bought and switched
  on each hub. Base `electricity_production` was 70000 (70) at `ad636f0`; class, postprocess
  overrides and authored template now give 75000 (75). A vanilla self `ObjectModifier` adds
  75000: **75 off / 150 on**, gross production at normal performance. The existing production
  callback refreshes the grid. Ruins produce zero and lose the modifier's extra 75.
- Ground heat reads only that hub's applied Power modifier and uses vanilla `BaseHeater`,
  `work_radius * const.GridSpacing` (configured 15 hexes), no fading border or added upkeep.
  Load reconciliation also removes heat left by the previous Cargo implementation.
- Delegated decision: **any intact hub with Power applied protects all trains in its colony**,
  including another city/map. This is appropriate for the brief's network effect: extra hubs
  buy local production and ground heat, while their overlapping train protection does not
  stack. Switching the last Power off restores vanilla cold; Cargo's bonus remains independent.
- Toggle, bulk removal, salvage, ruins and load cleanup remove the applied effects. Power
  never enters the colony claim or rebuild-carry mechanism. Other hubs can buy it while one
  builds, holds it, or stands in ruins. The owner's normal-rebuild limitation remains.
- New saved ID `SMROptInTrainHub6_Power` is inventoried in FIX_POLICY row 17 with its reason:
  a separately saved vanilla upgrade needs its own id. No custom modifier id, saved field,
  mod object or thread. Existing heat-grid state and the hub content residual remain; no
  clean-uninstall claim. No copied vanilla production body or ownership conflict: no stop hit.

SOURCE, archived `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua`:
`Buildings/Building.lua:1151-1250,1299-1321` (self modifier and bulk paths),
`Modifiers.lua:340-378` (ObjectModifier), `ElectricityProducer.lua:9,56-72`
(modifiable property without a scale, performance and UI reading), `City.lua:43,83`
(colony labels), and `Heater.lua:31-81` (existing heater machinery).

## Desk evidence

Commands run at HEAD `ad636f05a014c0d806accb69c3bb524229d48040` plus this diff:
`python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py` and
`python tools/devmods/train_hub/tests/cargo_heater_smoke.py`: PASS, including their mutation
checks. Tested `20_TrainHub.lua` SHA256:
`d6115604bbdfdddcc4d1b8ae09fa798128b69d14fc9b64f458540de2ca40b6dd`.

Coverage: Cargo-only cold, Power-only cold, both, neither; prior speed returns and heat
restoration after error; independent hub construction and switching; 75/150 property and
grid updates; radius, edge/outside heat, power loss, bulk cleanup, salvage, old ruins,
old Cargo heat, load idempotence, no Power carry, deletion and colony boundaries.
Mutations cover wrong gating, lost warming/restoration, wrong base/addition or notification,
shared ownership, wrong radius, missing cleanup/unlock, ruins reactivation and Power carry.
Fixtures execute archived vanilla upgrade, ObjectModifier, heater and train-speed bodies.
Modifier arithmetic, grid output and heat rasterization are doubles; native behaviour is owed.

Command/filter: run `python <file>` for every sorted
`Path('tools/devmods/train_hub/tests').glob('*_smoke.py')`, score process exit code.
**22 members = 22 passing + 0 failing**:
art_spec, buildtrack, capacity, cargo_heater, cargo_slots, cargo_upgrade, cargo_view,
distribution_departure, distribution_slots, distribution, distribution_ui, dwell, flight,
look, move, pallet_visuals, reactor_dust_slot, repair, spoilage, traffic, train_fill, train_spawn
(each with suffix `_smoke.py`). Detailed local output: `scratch/power_upgrade_smokes.json`.
The subsequently added unlock/output mutations also pass in the targeted heater run.
`python tools/doccheck.py`: GREEN; `python tools/parsecheck.py` and Lua `load()` over the
dev mod's `Code/**/*.lua` plus its authored hub template: PASS. `git diff --check`: clean.

## Mod Editor step

Open the Train Hub dev mod and save it in Mod Editor. Slot **2, Train Cargo**, should mention
only cargo/speed. Slot **3, Power Upgrade**, should show the local power/heat and colony train
protection, costing 30 Metals and 20 Electronics. Restart the game after the save.
The agent then runs `python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated`.
It was run here and FAILS on the old Cargo description and missing Power fields, as expected
before regeneration. It now compares every authored slot 2/3 field and effective base power,
allowing the editor to omit the vanilla self-target default or inherited class output.
Generated class and editor-owned `code_hash` were not hand-edited; the editor
save must refresh them. Desk PASS does not mean the generated runtime template is ready.

## Combined attended cold-wave check — NEVER RUN

Use a copy of a save with two intact hubs away from other heaters, Cargo built, both mods
and TestKit loaded. Keep one standing train outside both hubs' drone ranges for all reads.
With a hub selected, this console read reports gross power, center, edge and outside heat:
`local h=SelectedObj; local x,y=h:GetVisualPosXYZ(); local r=h.work_radius*const.GridSpacing; print(h:GetUIPowerProduction()/1000,GetHeatAt(h),GetHeatAtXY(x+r,y),GetHeatAtXY(x+r+const.GridSpacing,y))`
[NEVER RUN]. Allow heat/cooling to settle before comparing; use the panel as a second power read.

1. **Baseline, Cargo only.** Leave Power absent/off everywhere. Record a warm train reading
   with **slot 3 (read upgrades, train capacities and nominal speed)**. Run
   `CheatColdWave("ColdWave_High")` [NEVER RUN], unpause about half a sol, then pause.
   Hub production must be 75; center/edge/outside heat must be at most 90. Slot 3 must show
   the same train slowed by cold despite Cargo's bonus. If the ground is still warm, wait.
2. **Buy Power locally.** Buy Power on the first hub, allow heat to settle, repeat the reads:
   150 production, center and service edge above 90, outside still at most 90; the outside
   train returns to its warm Cargo speed. The second hub stays at 75 without local heat.
   Switch Cargo off/on: cargo and the 25% bonus change, but Power, ground heat and cold
   immunity stay. Slot 3 without Cargo must show the warm pre-Cargo speed.
3. **Second owner and off/on.** Buy Power on the second hub: it must be available and give
   that hub 150 and its own heat. Turn the first hub's Power off: first returns to 75 and
   cools, second stays at 150, trains stay warm. Turn the second off: both cool, train cold
   speed returns. Turn first Power back on and confirm its effects return.
4. **Salvage with another buyer.** Leave only first Power on; salvage it. Ruins produce zero,
   its ground cools, outside train slows. Second hub can turn its own Power on while those
   ruins remain; production, heat and warm train speed return. No rebuild action is required.
5. **Save and close.** Save/reload the copy with second Power on and first in ruins. Confirm
   the surviving effects and ruins' inactivity, run `CheatStopDisaster()` [NEVER RUN], and
   review new Lua errors with the agent. Restore the desired upgrade settings.

The orchestrator routes this sitting to the fix pack's owner list, superseding the old
briefs 19/20 check. Brief 21 remains until that sitting passes; Mod Editor and live acceptance
are the remaining work. Hub movement, distribution and reactor appearance are outside this change.
