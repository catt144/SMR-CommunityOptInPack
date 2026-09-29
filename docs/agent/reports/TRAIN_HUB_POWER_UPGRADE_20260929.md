# Hub upgrades: one colony state - 2026-09-29

Brief 21 repair 3 implements the owner's 2026-09-29 ruling in train design section 4.10.
**Desk PASS; Mod Editor save and the attended rerun below remain owed.** Every bought
upgrade has one on/off state. Any hub can switch it; every hub displays that state.
Salvaging or clearing any hub, including the buyer and the last hub, preserves it.
Executed model: GPT-6 (Codex, as identified in this transcript); no subagents.

## Change and save contract

Vanilla still builds and charges for each upgrade. Its existing Capacity and Cargo
LabelModifiers move from city to colony, retaining their objects, amounts and generated
ids. Native label membership covers future stations and trains on every map. Power's
old local ObjectModifier is removed; every intact hub derives the extra 75 output from
the colony switch. Base output stays 75, upgraded output 150 at normal performance.
Ground heat and train cold immunity read that same switch; Cargo remains +100% cargo
and +25% speed, without heat or cold immunity of its own.

`UIColony.SMROptIn_hub_upgrades` holds the existing upgrade ids mapped to `{on, modifiers}`.
It is necessary because a purchase must survive removal of all buildings; vanilla's
research unlock does not record purchase or switch state. FIX_POLICY inventory row 18
records the name, shape and reason, as brief 21 permits. It holds plain data and native
modifier references, no custom object, function, thread or hub reference. Existing
upgrade ids and generated modifier ids keep their bytes.

Load adopts old paid receipts, including ruins, preserving saved switches (ON wins if
old duplicate receipts disagree). It removes old city registrations before applying the
colony effects. Every hub mirrors the vanilla purchase and switch tables,
including the raw switch table read by Ctrl+click. Local modifier arrays are empty so
native building cleanup and modifier scans cannot replay a colony modifier per hub.
Publishing every mirror synchronously prevents a broadcast from toggling the colony once per hub. Native bulk
modifier callbacks reconcile to the colony switch; salvage is no longer an off command.

SOURCE, archived **1.1.1.405907** under
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src`:
`Lua/XDef/sectionUpgrades.generated.lua:41-55,69-92` explains the old lit spent row and
raw broadcast reads; `Lua/Buildings/Building.lua:1151-1250,1261-1389` provides native
purchase, modifier lifecycle, leaked-modifier cleanup and panel getters;
`Lua/LabelContainer.lua:17-90`, `Lua/Modifiers.lua:284-328` and `Lua/City.lua:82-88`
provide colony label effects. The old-save leak fixup can unregister generated-id
modifiers when no hubs remain; load restores them from the colony receipt.
No copied vanilla production body or incompatible vanilla storage change was needed.

The receipt and native capacity effects may survive mod removal if vanilla's once-per-save
cleanup already ran. This remains content-mod residual, not a clean-uninstall claim;
see FIX_POLICY row 18. Desk tests do not prove native serialization or save removal.

TestKit slot **3 (read upgrades, train capacities and nominal speed)** now reads colony
and city modifiers plus saved modifier references, deduplicating shared objects and
including OFF modifiers with no hubs present. It remains read-only. Slot **6 (stream
every train and station)** retains its existing effective-speed reader.

## Evidence

At OptInPack HEAD `28223954f90fe1a15a980f6172813cc4b2441b5d` plus this diff and TestKit
`4a31982` plus its slot-3 diff: execute `python <file>` for every sorted
`Path('tools/devmods/train_hub/tests').glob('*_smoke.py')`, score process exit code.
**23 members = 23 passing + 0 failing**:
art_spec, buildtrack, capacity, cargo_heater, cargo_slots, cargo_upgrade, cargo_view,
distribution_departure, distribution_slots, distribution, distribution_ui, dwell, flight,
global_upgrade, look, move, pallet_visuals, reactor_dust_slot, repair, spoilage, traffic,
train_fill, train_spawn (each with suffix `_smoke.py`). Full local output:
`scratch/power_global_smokes.json`. The tested slot-3 change is committed as TestKit
`587f474`. `python tools/doccheck.py` is GREEN; Lua `load()` parses the dev mod
`Code/**/*.lua`, authored hub template and TestKit slot file. Both trees pass
`git diff --check`.

Mutations reject per-hub display, refused receiver switching, stale raw panel state,
lost future-hub heat, salvage revocation, lost zero-hub receipts, changed old-save OFF
state, local-only modifiers and failed native leak-fixup recovery. Slot 3 rejects duplicate
modifier rows and omission of OFF modifiers when no hubs remain. Prior Cargo numeric,
Power heat/radius, cold-speed and legacy 145-output regressions remain exercised.
Fixtures execute archived vanilla bodies over mocked objects, grids and lifecycle;
restoring a plain receipt table is a desk check, not a real save/load claim.

The owner's earlier repair-2 readings remain in brief 21 and the
[prior report](TRAIN_HUB_POWER_UPGRADE_20260928.md). They do not establish repair-3 controls
or salvage persistence. Consumption 10 versus 20 was vanilla's cold penalty, explained
there; expected warmed consumption is still 10, with no added Power upkeep.

## Editor and combined attended check

Save the Train Hub dev mod in Mod Editor and restart. All three descriptions now say
any hub can switch the colony state and salvage does not change it. The editor owns the
generated template and code hash; neither was hand-edited. Then run
`python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated`.
It currently fails only on the three changed descriptions; numeric fields agree.

Use a disposable copy with two hubs, both mods and TestKit loaded. For each hub this
console read shows production, center, edge and outside heat:
`local h=SelectedObj; local x,y=h:GetVisualPosXYZ(); local r=h.work_radius*const.GridSpacing; print(h:GetUIPowerProduction()/1000,GetHeatAt(h),GetHeatAtXY(x+r,y),GetHeatAtXY(x+r+const.GridSpacing,y))`
[RAN 2026-09-28, log Mars.exe-20260928-22.20.16-6aad2d75.log, lines 344/3382/3386].
Allow heat to settle. Compare the same cruising train on straight open track away from
hubs, excluding acceleration and stops. Restart slot 6 after every save, including autosaves.

1. **Cold baseline.** Turn Power off from either hub. Both rows must show OFF and both
   panels read 75. Start a cold wave through TestKit World. Use **slot 6 (stream every
   train and station)** to record cold effective speed; center/edge/outside ground cools.
2. **Switch from the other hub.** Buy Power once if needed, then switch it from the
   non-buying hub. Both rows show ON, both panels read 150, centers/service edges warm
   (normally 255), and outside ground stays cold. Consumption settles to 10 and the
   train regains warm speed. Off and back on from either hub must change both together.
3. **All three controls.** For each bought Capacity Network and Train Cargo upgrade,
   switch it from the non-buying hub, checking both panels match. Include one Ctrl+click:
   it changes state once. **Slot 3 (read upgrades, train capacities and nominal speed)**
   checks capacity; **slot 6 (stream every train and station)** checks Cargo's speed.
   Cargo changes neither Power output nor heat. Leave a mix of ON and OFF for the next step.
4. **Salvage and reload.** Salvage the original buyer, then save/reload. Remaining hub
   displays, capacities, Power output/heat and train speed retain the chosen states.
   A destroyed hub itself produces zero and stops heating. Clear its ruins, build a new
   hub and verify inherited states, switches and no purchase cost.
5. **Last hub removed.** On the disposable copy, clear every hub while retaining at least
   one ON and one OFF upgrade. Save/reload, build another hub and check the same purchases
   and states, with no re-buy; its switches still work. Stop the disaster and stream,
   review the log with the agent, and return to the intended play save.

The orchestrator routes this revised sitting to the fix pack's owner list. Brief 21
remains until it passes. Movement, distribution and reactor appearance are unchanged.
