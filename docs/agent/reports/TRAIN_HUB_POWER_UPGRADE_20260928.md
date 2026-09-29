# Hub Power Upgrade — 2026-09-28

Brief 21, owner ruling in train design §4.10. **The first sitting failed at 145 power. The
saved-base repair and slot 6 effective-speed reader are desk-tested; full rerun owed.**
Template generation passed after the owner's `5128fec` save. No live repair PASS is claimed.
Executed model: GPT-6 (Codex, identified in this transcript); no subagents.

## Repair after the failed sitting

Owner findings are retained in brief 21. The log
[`Mars.exe-20260928-22.20.16-6aad2d75.log`](../../archive/power_upgrade_20260928/Mars.exe-20260928-22.20.16-6aad2d75.log)
records `145 255 255 255` before cold (line 344), then `75 0 0 0` on the other hub and
`145 255 255 0` on the upgraded hub (3382/3386). The warm ring reached its service edge and
left the outside cold. The owner stopped; the whole sitting is to be rerun.

SOURCE cause: vanilla `Modifiable:InitBaseProperties` saves the placement-time property in
`base_electricity_production`. Changing the class to 75000 does not rebase existing hubs.
`UpdateModifier` computes from that saved base, so old 70000 + Power's 75000 = 145000.
The old desk fixture incorrectly always supplied a fresh 75000 base. Archived build
1.1.1.405907 `Lua/Modifiers.lua:30-37,41-86,120-128` supplies all three methods.
The revised fixture runs vanilla `UpdateModifier`, `ModifyValue` and `SetBase`, reproduces
145, and repairs it to 150; turning Power off gives 75. It also checks no-upgrade/off hubs,
ruins, repeated loads, modifier identity and preservation of unrelated modifiers/bases.

INFERRED attribution to the sitting's hub: its load log identifies `Double Hub Build.savegame.sav`
at game time 20344961, mod version 54. Read-only BPUL fragment assembly and ZSTD decoding
of that save (`python docs/archive/power_upgrade_20260928/read_save.py`, at `1d93090` plus this diff) found its
persisted base-property symbol and old 70000 values, but did not fully decode the native
object graph to assign the field to handle 6430. Save SHA256:
`901147f3e7e56dcb2cf410cb6969524263f6569bdfe83cefce0acde1417e0399`.
The load repair therefore logs the actual hub handle and pre/post property values as it
rebases; the rerun must confirm `base 70000>75000`, with output 145000>150000 if Power was
saved on (70000>75000 if saved off). The original save was not modified.

`rebase_hub_power` runs on load only for this hub class and **only when the saved base equals
70000**, through vanilla `SetBase`. It neither clears modifiers nor toggles the upgrade and
needs no saved marker. Other bases are untouched; ruins still produce zero. There is no
copied vanilla body or new persisted name.

TestKit **slot 6 (stream every train and station)** now emits each train's `effective_speed`
from native `GetVelocity()` (archived 1.1.1.405907
`CommonLua/LuaExportedDocs/Game/GameObject.lua:141-150,646`). It measures actual movement,
including acceleration and stops, in world units per second. The existing change detector
also emits speed-only changes. Slot 3 is unchanged. The brief's claim that nominal speed
cannot reflect cold is too broad: `Units/Train.lua:593-613` does read heat, at its supplied
track element or the train. Its unchanged sitting readings do not prove actual motion;
the new stream supplies the requested independent reading. Compare steady movement on
the same open, cold track, away from stations/turns, not a standing train's zero velocity.

Repair validation at `1d93090` plus this diff, TestKit `e09efa0` plus its diff:
the TestKit change is committed as `4a31982`.
`python tools/devmods/train_hub/tests/cargo_heater_smoke.py` and
`python tools/devmods/train_hub/tests/distribution_slots_smoke.py`: PASS. Removing the
migration, widening its old-base guard, or replacing slot 6's actual reader with nominal
speed fails their regression checks. Slot 6 tests exercise speed-only transitions and stops.
`cargo_upgrade_smoke.py --require-generated`: PASS. Running every sorted `*_smoke.py` under
`tools/devmods/train_hub/tests` with Python, scoring exit code, again gives **22 members =
22 passing + 0 failing**, the same member list below. `python tools/doccheck.py` is GREEN;
Lua `load()` parses both changed Lua files and both trees pass `git diff --check`.
Native velocity, repair on the actual
loaded save, and post-repair cold-wave behaviour remain attended checks.

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

## Desk evidence — initial build

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

## Mod Editor step before the rerun

Open the Train Hub dev mod and save it in Mod Editor. Slot **2, Train Cargo**, should mention
only cargo/speed. Slot **3, Power Upgrade**, should show the local power/heat and colony train
protection, costing 30 Metals and 20 Electronics. Restart the game after the save.
The agent then runs `python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated`.
It now PASSES after the owner's `5128fec` template save. This repair changes Lua only;
save once more to refresh the editor-owned `code_hash`, then restart. Generated class and
hash were not hand-edited. The check compares authored slot 2/3 fields and effective base
power, allowing omitted vanilla defaults. The runtime template is ready; live repair is owed.

## Combined attended cold-wave check — full rerun owed

Use a copy of a save with two intact hubs away from other heaters, Cargo built, both mods
and TestKit loaded. Use the same moving train on open track outside both hubs' drone ranges
for the speed comparisons. Enable **slot 6 (stream every train and station)**; re-enable it
after every save/load because those stop the stream. Confirm the load repair diagnostic above.
With a hub selected, this console read reports gross power, center, edge and outside heat:
`local h=SelectedObj; local x,y=h:GetVisualPosXYZ(); local r=h.work_radius*const.GridSpacing; print(h:GetUIPowerProduction()/1000,GetHeatAt(h),GetHeatAtXY(x+r,y),GetHeatAtXY(x+r+const.GridSpacing,y))`
[RAN 2026-09-28, log Mars.exe-20260928-22.20.16-6aad2d75.log, lines 344/3382/3386].
Allow heat/cooling to settle before comparing; use the panel as a second power read.

1. **Baseline, Cargo only.** Leave Power absent/off everywhere. Record a warm train reading
   in **slot 6 (stream every train and station)**. Start a cold wave through TestKit World
   (the prior sitting used `ColdWave_GameRule`); unpause about half a sol, then read.
   Hub production must be 75; center/edge/outside heat must be at most 90. The stream must
   show the same train's effective speed lower on comparable straight track despite Cargo's
   bonus. Exclude stops, acceleration and hub manoeuvres; if the ground is still warm, wait.
2. **Buy Power locally.** Buy Power on the first hub, allow heat to settle, repeat the reads:
   150 production, center and service edge above 90, outside still at most 90; the outside
   train returns to its warm Cargo speed. The second hub stays at 75 without local heat.
   Switch Cargo off/on: cargo and the 25% bonus change, but Power, ground heat and cold
   immunity stay. **Slot 3 (read upgrades, train capacities and nominal speed)** checks the
   cargo capacity; **slot 6 (stream every train and station)** checks actual warm speed with
   Cargo off and on. If Power is already bought, its on/off switch replaces the purchase.
3. **Second owner and off/on.** Buy Power on the second hub: it must be available and give
   that hub 150 and its own heat. Turn the first hub's Power off: first returns to 75 and
   cools, second stays at 150, trains stay warm. Turn the second off: both cool, train cold
   speed returns. Turn first Power back on and confirm its effects return.
4. **Salvage with another buyer.** Leave only first Power on; salvage it. Ruins produce zero,
   its ground cools, outside train slows. Second hub can turn its own Power on while those
   ruins remain; production, heat and warm train speed return. No rebuild action is required.
5. **Save and close.** Save/reload the copy with second Power on and first in ruins. Confirm
   the surviving effects and ruins' inactivity, restart **slot 6 (stream every train and
   station)**, then use TestKit **Stop disaster**. Review new Lua errors and the stream with
   the agent. Restore the desired upgrade settings and stop the stream.

The orchestrator routes this sitting to the fix pack's owner list, superseding the old
briefs 19/20 check. Brief 21 remains until the whole rerun passes; editor hash refresh and live
acceptance are the remaining work. Hub movement, distribution and reactor appearance are outside
this change.
