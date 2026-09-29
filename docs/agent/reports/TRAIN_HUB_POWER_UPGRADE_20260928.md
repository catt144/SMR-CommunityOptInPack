# Hub Power Upgrade — 2026-09-28

Brief 21, owner ruling in train design section 4.10. **Repair 2 makes Power a single colony
purchase: all present and future hubs receive output and heat. Desk PASS; Mod Editor save
and the combined attended rerun below remain owed.** The owner's prior rerun confirmed
150/75 and the heat footprint after `9bffa5c`; its evidence and train slowdown correction
remain in brief 21. That sitting predates this colony-sharing change.
Executed model: GPT-6 (Codex, identified in this transcript); no subagents.

## Colony purchase repair

The buyer keeps its existing vanilla self `ObjectModifier` and upgrade ID. Power now uses
the same construction claim, spent display, switch guard, ruins claim and carry path as
Capacity Network and Train Cargo. The production reader chains vanilla and adds a
performance-scaled 75 on other intact hubs while any valid buyer's modifier is applied.
The buyer already gets that 75 from its modifier, so it never receives it twice.
Grid production and `GetUIPowerProduction()` are 75 off / 150 on at normal performance.
The receiving hub's raw `electricity_production` property stays 75000; its effective output
is 150000. No copied vanilla body, new persisted name, modifier, field or thread.

Heat and train immunity read the same colony state. Purchase, toggle, bulk cleanup,
salvage and load refresh all hubs; `GameInit`'s existing upgrade initializer heats and
refreshes each later-built hub. Destroyed receivers produce zero and lose heat; deleting
a receiver leaves the buyer's effects intact. Destroying the buyer removes all effects,
while its ruins retain the spent claim. Normal hub rebuild remains outside the sitting;
the existing carry path is kept symmetric and desk-tested.

Old per-hub saves can have duplicate purchases. Load keeps the first active buyer, or the
first saved buyer if all are off; it stops and clears only redundant Power bookkeeping.
No resources are refunded. This converts the existing receipts to the owner's single
colony claim, preserving on/off behavior and other upgrades. Repeated load is inert.
The old 70000-base repair still runs before sharing, preserving unrelated modifiers.

SOURCE for the reported consumption difference, archived build **1.1.1.405907**:
`Lua/Buildings/ColdSensitive.lua:58-60` checks ground heat against `penalty_heat`;
`Lua/_GameConst.lua:208-209` supplies threshold 210 and penalty 100%;
`Lua/ElectricityConsumer.lua:71-82` applies that percent to consumption. Thus a base-10 hub
on cold ground consumes 20, while a heated hub consumes 10. INFERRED attribution to the
owner's 10/20 panels: the readings agree with that path, not an upgrade upkeep charge.
The Winter Is Coming rule can double the penalty; the next sitting records consumption
alongside actual heat rather than assuming every cold-wave setting has the same penalty.
SOURCE output/panel path: `Lua/ElectricityProducer.lua:56-72`; colony membership:
`Lua/City.lua:82-88`. All paths above are within
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src`.

Repair 2 validation at `2226e949fbcb8f44ac422e034db7a1259004e657` plus this diff:
`python tools/devmods/train_hub/tests/cargo_heater_smoke.py` PASS, including mutations for
per-hub output, per-hub heat, missed later-built hub, duplicate claims, shared ownership,
salvage, cleanup, prior saved-base repair and Cargo isolation.
`cargo_upgrade_smoke.py` PASS. Command/filter: run `python <file>` for every sorted
`Path('tools/devmods/train_hub/tests').glob('*_smoke.py')`, score exit code:
**22 members = 22 passing + 0 failing**, same members listed under initial desk evidence.
Local complete output: `scratch/power_colony_smokes.json`.
`cargo_upgrade_smoke.py --require-generated` currently FAILS solely on slot 3's revised
description: the owner must save the authored template in Mod Editor. This is separate
from the passing desk suite. Native heat, grid and attended behavior remain live checks.

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

Train Cargo gives only +100% cargo and +25% speed, with its prior purchase and switching
behavior. Power is slot 3, costs 30 Metals + 20 Electronics, requires no tech and is bought
once per colony. Its existing saved ID `SMROptInTrainHub6_Power` stays inventoried in
FIX_POLICY row 17. Ground heat uses vanilla `BaseHeater`, `work_radius * const.GridSpacing`
(configured 15 hexes), no fading border and no extra upkeep. Existing heat-grid persistence
and the hub content residual remain; no clean-uninstall claim.

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

Open the Train Hub dev mod and save it in Mod Editor, then restart the game. Slot **2,
Train Cargo** mentions only cargo/speed. Slot **3, Power Upgrade** must say buy once per
colony, benefits every present and future hub, and is switched by the purchasing hub.
The save regenerates the class and editor-owned `code_hash`; neither was hand-edited.
Then run `python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated`.
The pending mismatch is the slot 3 description only; the existing cost and modifier fields
stay unchanged. The earlier `5128fec` save predates this new description.

## Combined attended cold-wave check - full rerun owed

Use a copy with two intact hubs away from other heaters, Cargo built, both mods and TestKit
loaded. Compare the same moving train on open track outside the hubs' drone ranges.
Enable **slot 6 (stream every train and station)**; re-enable after every save/load,
including autosaves. Compare steady motion, excluding stops, acceleration and hub turns.
With a hub selected, read gross output, center, edge and outside heat:
`local h=SelectedObj; local x,y=h:GetVisualPosXYZ(); local r=h.work_radius*const.GridSpacing; print(h:GetUIPowerProduction()/1000,GetHeatAt(h),GetHeatAtXY(x+r,y),GetHeatAtXY(x+r+const.GridSpacing,y))`
[RAN 2026-09-28, log Mars.exe-20260928-22.20.16-6aad2d75.log, lines 344/3382/3386].
Allow heat/cooling to settle and record panel consumption alongside these readings.

1. **Baseline, Cargo only.** Leave Power absent/off everywhere. Record warm effective train
   speed using **slot 6 (stream every train and station)**. Start a cold wave through TestKit
   World, as in the previous sitting. After the ground cools, both hubs produce 75,
   center/edge/outside are at most 90, and that train slows despite Cargo's bonus. Record
   consumption; ordinary cold predicts 20 from base 10, subject to the cold rule noted above.
2. **Buy once.** Buy or enable Power on its owning hub. Both hubs now produce 150, both
   centers/service edges warm above 210 (normally 255), and ground just outside stays cold.
   Both consumers return to 10 after heat settles; the train returns to warm speed.
   The other hub shows Power spent with no independent switch or purchase. Build a later hub:
   it also receives 150 and heat without buying Power, and shows the spent claim.
3. **Independent controls.** Turn Cargo off/on: **slot 3 (read upgrades, train capacities and
   nominal speed)** confirms cargo capacity, and **slot 6 (stream every train and station)**
   confirms its speed bonus; power/heat/cold immunity stay. Turn the owning hub's Power off:
   all intact hubs return to 75, ground cools and trains slow. Turn it on: all effects return.
4. **Save and salvage.** Save/reload with Power on and check all hubs still receive it;
   restart **slot 6 (stream every train and station)**. Salvage the owning hub. Its ruins
   produce zero; surviving hubs return to 75 and cool, trains slow, and other hubs still
   show Power spent while the ruins stand. No normal rebuild is required.
5. **Ruins reload and close.** Save/reload the copy with the buyer in ruins. Check effects
   remain off and the spent claim remains. Restart **slot 6 (stream every train and station)**,
   use TestKit **Stop disaster**, and review the log with the agent. Restore the desired
   play save/settings and stop the stream.

The orchestrator routes this sitting to the fix pack's owner list. Brief 21 remains until
this whole rerun passes. Hub movement, distribution and reactor appearance are outside
this change. Remaining work: Mod Editor save, strict generated check, attended rerun.
