# Train hub — why the pallets drew empty while the hub was stocked

Brief `prompts/Train_Hub_Project/12_TRAIN_HUB_PALLET_VISUALS_high.md` (owner ask 2026-09-27,
worked 2026-09-28). A dev-mod investigation and repair record, not a shipping claim. Desk
result only: **desk-reproduced and repaired; live look owed.** Whether the healed look matches
the owner's intent is the owner's judgement in the sitting, not a claim here.

## The cause

Vanilla stores a multi-resource depot's visual column split — `capacity_columns` and
`visual_col_start` — on the object, and it rides in the save. It is recomputed in exactly two
places: at placement (`CreateResourceRequests`, `MultiResourceDepot.lua:156-182` on
1.1.1.405907) and on a storable-list change (`RecalculateAfterResourceListChange`, `:380-408`).
**Nothing recomputes it when the column count under it moves.** The hub's column count has
moved across the fixture's life: `GetTotalStorageColumns()` is `attached depots × 60` on the
stand-in body (`Station.lua:1215-1218`) and `own pallets × 60` on the owner's asset
(`20_TrainHub.lua`). A hub whose split was derived in an earlier epoch draws with that stale
split forever: its resources take too few columns, land on a fraction of the beds, and the
rest of every bed stays bare while the panel shows the stock.

`max_z` is different: the Capacity Network Upgrade's modifier fires
`OnModifiableValueChanged`, which re-derives it live. That is why the height was right (9)
while the split was stale — the receipts below pin both.

The reconstruction that fits every receipt: the split was derived when the hub read **240
columns** (four stand-in sub-depots), the asset's six pallets (360 columns) arrived without a
re-derive, and the upgrade later re-derived only `max_z`. The desk smoke reproduces the
reported picture from exactly that state. The live save's actual epoch is owed to the log:
the heal (below) prints the old split once before repairing it, so the first load of
`build6_capacity_covered_pass3` on the fixed build records it even if nobody presses a slot.

## Evidence

| claim | source | tag |
|---|---|---|
| Every group stocked, many beds bare (Metals 251/480, Basic 902/2,400, Advanced 700/1,920, Delicacies 1,318/3,840, Other 360/960) | owner screenshot, `docs/archive/train_hub_pallets_20260927/` | MEASURED (owner) |
| Live `max_z` = 9, before and after the upgrade | capacity sitting log 2026-09-26 (`TRAIN_HUB_CAPACITY_20260926.md` step 2); boot dump `Mars.exe-20260927-23.52.42-6aad2d75.log:336` | MEASURED |
| Six pallets, own `Box1` spots, r = 2492 | console dump 2026-09-23, `drones_chain/L3_FLIGHTLOOK_ENGINE_20260923.md`; no spot-touching asset export since (SMR-Assets log) | MEASURED |
| Hub 6430 persists across the save lineage since ≤ 2026-09-23 | same handle in `TRAIN_HUB_AUDIT_111_20260923` inventory and the 2026-09-26 capacity log | MEASURED |
| The split is recomputed only at placement / storable-list change | `MultiResourceDepot.lua:156-182`, `:380-408`; `MultiResourceCubeVisuals.lua:224-257` (1.1.1.405907) | SOURCE |
| A fresh 360-column split cannot produce the screenshot | falsifying check below | SOURCE |
| The stale 240-column split reproduces it | `tests/pallet_visuals_smoke.py` | MEASURED (desk) |
| Per-leaf stocks inside Advanced/Delicacies | smoke fixture splits group totals evenly/plausibly | INFERRED |

**The falsifying check.** With the current code and six pallets, 360 columns over 19 visible
resources give 19 columns each (18 to the last), allocated contiguously in
`TransportableResourceIds` order. The five basics (Metals, Concrete, Food, Rare Metals, Exotic
Minerals — panel 150–251 each) are adjacent in that order, so a fresh split must draw them as
one solid ~95-column wall at up to 9 high: bed 1 fully covered and a third of bed 2. The
screenshot shows no fully covered bed anywhere — isolated 12-15-column clusters. A fresh
split is falsified; the live split is inherited from the save. The stale-240 state, run at
desk with the panel's stocks, yields the observed shape: 13/12-column slabs, ~1,600 cubes, on
four of six beds, two beds bare, none taller than 9.

## The fix — `SMROptInTrainHubBase:HealCargoColumns()`

In `20_TrainHub.lua`'s cargo-on-show block; `heal_after_load` calls it on every load. It
re-derives the split and `max_z` and repositions (`RecalculateCapacityColumns`,
`RecalculateDerivedMaxZ`, `ReallocateVisualColumns`) — the same shape as vanilla's own
savegame fixup for these visuals (`ZZMultiResourceCubeVisualsFillOrder`,
`MultiResourceCubeVisuals.lua:604-611`, which re-runs `ReallocateVisualColumns` on load).
When something moved it logs one `[TrainHubDev] hub <handle> cargo columns re-derived` line
carrying the **old** split, so a stale save's epoch reaches the log before the repair erases
it; when the split is already right it logs nothing and repositioning is a no-op. Every field
written is vanilla's own; no new persisted name (FIX_POLICY ban 1 untouched). The restored
look is spec §10's standing ruling: 18/19-column slabs, stacks capped at the height 150000
drew (`max_z` 9), stock past the cap stored and not drawn.

**Residual, for the owner's eye in the sitting:** vanilla's scheme reserves columns per
resource. Leaves with zero stock (Seeds, unstocked delicacies) keep their columns bare even
after the heal — with the panel's stocks roughly a third of the ring stays empty by design.
If the owner wants beds to pack densely regardless of which leaf holds the stock (the
shared-pool look of `MixedPoolStockpile`), that is a behaviour change wanting its own ruling
and brief; the cargo-draw override is the place, cost about a session.

## Desk receipts, HEAD `5a42508` plus the working tree that becomes this commit

| command | result |
|---|---|
| `python tools/devmods/train_hub/tests/pallet_visuals_smoke.py` | exit 0, PASS; archived vanilla bodies by hash; stale 240 split: max_z 13 then 9 after the upgrade's own re-derive, 1,611 cubes on beds 0-3, two beds bare; healed: 19/18 columns contiguous over all 360, 2,352 cubes over six beds, per-leaf drawn = min(stock, cols×9); heal logs once, silent and idempotent when clean |
| `python tools/devmods/train_hub/tests/capacity_smoke.py` | exit 0 |
| `python tools/devmods/train_hub/tests/distribution_slots_smoke.py` | exit 0 (slot 2 untouched in the kit for now, see below) |
| `look/buildtrack/repair/flight/move/distribution/distribution_ui/distribution_departure/dwell/art_spec` smokes | exit 0 each |
| `python tools/devmods/train_hub/tests/traffic_smoke.py` | **FAIL, pre-existing**: fails identically with this change stashed (`-10800 != 0`, a z-height assert). Not this brief's fence; owed to the orchestrator |
| `python tools/parsecheck.py --dir tools/devmods/train_hub/Code` | 0 errors |
| `python tools/doccheck.py` | exit 0 |

## TestKit: slot 2 staged, not rebound

The orchestrator's amendment (`5a42508`) makes slot 2 mine only after the owner's probe
sitting ends, and the deployed kit is a junction to the working tree, so the rebind is
**staged** at `tools/devmods/train_hub/tests/81_PalletColumnsSlot.lua.txt` and the kit is
untouched. The staged slot is a pure read of the selected hub: per-resource
`cols`/`col_start`/`stored`/`drawn` rows plus `max_z`, `total_cols`, depot attaches, the
`Box1` spot range and totals. Note for brief 10's ledger: slot 6's refusal message still says
"fill the spoke above its floor with slot 2 first"; after the rebind that hint names a slot
that no longer fills (out of this brief's fence, reported not edited).

## Sitting steps for the orchestrator (a smoke, after the probe sitting ends)

1. Apply the staged rebind: replace the kit's `T.Bind(2, "Fill selected station's Metals to
   its cap", ...)` block and its header line with `81_PalletColumnsSlot.lua.txt`'s block;
   commit the kit. `distribution_slots_smoke` stays green (it asserts slot 2 is bound).
2. Launch, load `build6_capacity_covered_pass3`, pause. Expect one
   `[TrainHubDev] hub 6430 cargo columns re-derived (total_cols=360): ...` line — archive it;
   its old values are the live epoch record this report owes.
3. Select the hub, press slot 2. Expect `max_z=9 total_cols=360 depot_attaches=0
   spot_first/last` spanning six spots, per-resource `cols` 19 (18 on the last visible),
   contiguous `col_start`, `drawn = min(stored/1000, cols*9)` per row, `errors=0`.
4. Owner looks at the pallets: stocked resources as wide slabs (4 files of 5) up to 9 high,
   every bed carrying some resource's columns, excess invisible. The owner's word on whether
   this is the intended look — including the bare columns of unstocked leaves (Residual
   above) — closes or reopens the brief.
5. Reload the same save once: no re-derive line (the heal is silent when clean), the look
   unchanged. Save over no fixture.

Normal time about ten minutes; a console error, a second re-derive line, or any slot figure
off these stops the smoke for a read.

## Close-out

Executed model: claude-fable-5 (Claude Fable 5). The brief stays in place; the orchestrator
owns its lifecycle.
