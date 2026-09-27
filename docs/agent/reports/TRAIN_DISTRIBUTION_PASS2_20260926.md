# Distribution — native storage rows and next sitting

Authority: `prompts/Train_Hub_Project/09_TRAIN_HUB_DISTRIBUTION_high.md`, pass 2;
spec §4.8's owner delegation (`e1daef6`), §4.7's final UI ruling (`79c0ec9`),
and the owner's orchestrator relays of 2026-09-26/27. UI refinements follow
`817b778` (remove bubble, wrap between words), `a55fba4` (Ctrl copies current state),
and `7f10c96` (Ctrl also copies the slider percentage).
Pass 2's allocation is `c90a670`; the nil-cargo fix is `0a41767`. The separate
section (`969c7c3`, load-order repair `057320e`) is removed by the final ruling.
Executed model: GPT-6 as exposed by session instructions; no more specific model
identifier was exposed in the transcript. No subagents.

**Export floor PASSED live on `67bbf45`**, per the orchestrator's 2026-09-27 relay
recorded at `a55fba4`: from `build6_capacity`, the uncovered spoke went from 120
to 24, and another spoke visit left 24. The relay reports zero log errors. The
owner accepted the four-state cycle, titles, icons, inline slider and tooltips,
and confirmed off-network stations stay vanilla. This pairs distribution with
the already-active capacity upgrade; it does not witness toggling that upgrade.
The first three sittings stopped before the floor test, as recorded below.

**Current handback: pass 3, covered-station crash repair, desk only.** The second
2026-09-27 sitting on `fef640a` passed full-hub refusal, uncovered Import and
Balanced, save/reload with cargo, disable/re-enable, new trains and the UI
refinements (spec §4.8; `sittings/receipt.txt`). It exposed the fractional-order
division by zero. The reproduction, fix and covered-leg predictions are appended
below. Earlier sitting predictions remain historical, not a list of tests still owed.

## First sitting and crash repair

The first sitting's log is
[`Mars.exe-20260926-19.29.34-6aad2d75.log`](../../archive/train_hub_capacity_20260926/Mars.exe-20260926-19.29.34-6aad2d75.log).
Its receipt is beside it; no duplicate was archived. Line 818 is the
`assigned_resources` nil error at `40_TrainDistribution.lua:271`, reached through
`UnloadAll` and `TransferCargo` when a newly placed train arrived at the configured
Concrete row on StationSmall(1994). The read precedes `with_view`, so this crash
acquired no distribution claim.

**SOURCE, archived 1.1.1.405907:** `Lua/Units/Train.lua:798,823` permits a nil
assignment map through `table.keys`, then initializes it in vanilla's `UnloadAll`.
`CommonLua/LuaExportedDocs/Global/table.lua:215-226` documents the nil-tolerant helper.
The wrapper now treats a missing map as empty without initializing or writing cargo.
The desk double now accepts nil too, instead of masking this new-train state.

**MEASURED, desk:** a nil-map, empty-cargo train arriving at a Concrete exporter
reproduces the exact failure before the guard, then drains capacity 120 to the 20%
floor of 24 and holds it on return after the guard. Native code creates the map;
claims release. Before/after receipts: `repair/crash_regression_before.txt` and
`repair/crash_fix_suite.txt` under `docs/archive/train_distribution_20260926/`.

## Second sitting — section load order, no mode test ran

The owner stopped at step 1. The closed-process log is archived once at
[`ui_load_order/Mars.exe-20260926-20.43.45-6aad2d75.log`](../../archive/train_distribution_20260926/ui_load_order/Mars.exe-20260926-20.43.45-6aad2d75.log),
with its byte/hash/filter receipt beside it. Line 141 reports the distribution core
loaded; the section-loaded marker is absent, with no Lua error. The file-level
`InfopanelSection` guard silently returned before registering `DialogOpen` because
XDef classes are not built at mod-code load. The earlier harness created them too early.

**MEASURED, desk:** the corrected harness loads the UI file without its XDef classes,
then defines them before opening the station card. It fails against `969c7c3` and
passes with the check inside `D.AttachStationSection`. Missing class/constructor
or contained host now prints once per reason per module load; retry succeeds after
the class becomes available and clears `D.ui_error`. The startup marker confirms
callback registration, not native rendering. Before/after outputs are
`ui_load_order/regression_before.txt` and `ui_load_order/final_suite.txt` under
`docs/archive/train_distribution_20260926/`.

The orchestrator's later sitting evidence is in
[`sittings/receipt.txt`](../../archive/train_distribution_20260926/sittings/receipt.txt).
The third log, `sittings/Mars.exe-20260926-21.21.51-6aad2d75.log:178`, records section
registration, but the owner saw invisible `label()` text and rejected that UI.
No slot read or floor test followed. Existing logs were not archived again.

## Result and mechanism

**MEASURED, archived-body harness:** pass 1's controls reproduce: initial stock 80,
floor 20 retains 60 with an equal sink and 36 with a four-times-larger sink. The
new view drains to the slider and stops on the return trip, with source/hub capacities
60/240, 60/480, 100/100 and 120/480, at sliders 0/1/20/50/99/100 percent.

**MEASURED:** vanilla import with stock 80 at an equal-capacity source allocated 40.
The new view allocates 80 to a target of 80, and the destination receives it.
Balanced fills to its number and exports its excess. A full hub accepts nothing
and does not refill an exporter. The existing standing maintenance reserve still
holds. Several receivers get separate orders; an already reserved delivery reduces
the new order. Cargo reserved before changing a station to export stays aboard and
can unload at the hub through vanilla's own `UnloadAll`.

**SOURCE:** `40_TrainDistribution.lua` wraps the existing transfer path, leaving the
archived train body and loader intact. For a managed resource, the source answers
disabled only inside evaluation, removing its capacity entitlement. Receiving
stations answer a capacity equal to their remaining order. Claims hide their
already stored supply and cap demand at that order. Actual stock still contributes
to vanilla's line total. With stock sufficient for the orders, vanilla's capped
shares fill them; with a shortage, its allocator divides the stock. The native
loader owns cargo, stock and destination reservations. No copied train body and no
amount-only replacement were needed.

**SOURCE:** orders travel between configured spokes and their hub on vanilla's
current reachable track walk. No routing junction was added. A station connected
only through another route needs vanilla trains to reach the hub on their route;
graph membership alone is not a new cargo route. Unconfigured resources retain
vanilla behavior. Moving an untouched Balanced slider configures its pinned
amount; merely opening the card does not create settings. The displayed default
percentage is derived from the current native dial and live capacity.

**MEASURED, desk:** the six rewrite paths reapply drone baselines through archived
`Station:SetDesiredAmount`, including a recreated request reached through the
captured `RegisterResourceRequest` alias. The capacity getter also has a captured
depot alias; both it and the declaring method receive the transient wrapper.
Network-wide doubling changes the tested export floor 12 to 24 and the hub max
240 to 480. These rewrite measurements are from the harness. The later live floor
pass above uses the already-enabled upgrade; it does not witness a rewrite.

## Native row UI — desk rework after `79c0ec9`

`45_TrainDistributionUI.lua` now extends vanilla's `sectionStorageRow`. There is
no separate section, tab bar, help button, checkbox or handmade text widget.
Vanilla still creates the groups, rows, hex, title and `stored/max`. Its compiled
row context callback is chained after XDefs exist, and its constructor and click
callbacks are retained. This is a small patch to the compiled template, not a
replacement row. **SOURCE, archived 1.1.1.405907:**
`CommonLua/X/XTemplate.lua:1496` spawns the generated XDef class before considering
an XTemplate tree; `Lua/XDef/sectionResourceGroupStorage.generated.lua:85` constructs
`sectionStorageRow` directly. Editing preset data alone would not change that call.

For a hub-network station, the hex cycles Balanced → Export → Import → Not accepted
→ Balanced. The existing title changes with it, e.g. **Metals · Export**. Icons are
vanilla's storage crate, elevator resource up, elevator resource down, and native
red X respectively; the owner accepted those icons on `67bbf45`. The disabled
leg calls vanilla `SetAcceptResourceState("disabled")`, including its native flags.
Ctrl-click copies the clicked station's **current state and percentage** across
vanilla's city-wide Station list without advancing or rewriting the source. A
disabled network destination receives the remembered setting through `D.Set`
before finishing in vanilla's disabled path; no yielding occurs between those
steps. Plain clicks still cycle only the clicked station. Other stations receive the native enabled
or disabled state and acquire no hub setting. Their own clicks remain two-state.

The native `InfopanelSlider` shares `idSectionTitles` with the original titles;
the right title stays at the right edge. Its vertical margins are zero, its native
bar/track minima are released. The left title reserves at least 154 layout units,
expanding to fit its longest translated word using native font measurements.
Its maximum height is two native font lines plus native padding. This prevents
the native wrapper's last-resort character split when a word exceeds the entire
line (`CommonLua/X/XTextParser.lua:1057-1107`, build 1.1.1.405907), while bounding
row height. Native shortening handles text that exceeds those two lines.
The slider contributes zero measured height and uses native stretch layout to take the
title line's height (`CommonLua/X/XWindow.lua:623-665,744-794`, build 1.1.1.405907).
No additional line is created. Balanced has an active slider; Not accepted leaves
it visible but disabled. The owner's rejected drag bubble and its fade timer are
deleted without replacement. The row's per-mode hover tooltip is the percent and
amount readout, including **No drones in range — trains only** when applicable.

The panel's existing per-instance `AdjustConstrainedScale` callback still snaps
the scale, then clamps a connected station to **800/1000 (80%)**. This is a starting
value retained after the owner's acceptance of the native rows. Disconnection
restores the native row and removes the scale floor; the hub and unrelated panels
keep native scale behavior. Very tall panels may run offscreen at the floor.

**MEASURED, desk:** the harness loads the mod before XDefs, then executes archived
native row and slider constructors/callbacks with engine window doubles.
It checks the four states and distinct icons/titles, native disabled flags, late
class retry/log-once, current-state/percentage Ctrl-copy without source mutation, Balanced
slider, row-tooltip readout without a bubble or timer, live capacity/coverage
changes, and disconnect/reconnect restoration. Native word splitting reproduces
as a control, then whole words fit across font-size/scale doubles with a two-line
height cap. Actual rendering still needs the owner's eye. Slot 4
reads an Export setting made by the native row's click, then the train fixture keeps
24 on both visits at capacity 120. No direct `D.Set` substitutes for that UI action.
Native row appearance was accepted live on `67bbf45`. The new title bounds,
bubble removal and Ctrl behavior have desk evidence only; controller focus has
not been witnessed in the engine.

## Save ladder and residuals

| Part | Rung | Basis for this rung and why the lower one is insufficient |
|---|---|---|
| Train allocation and old-cargo unload limits | 0 | Archived-body tests above achieve the floor and import target with temporary getter answers and claims; no higher rung needed. SaveGameStart injection observes original enabled/capacity answers and released claims. |
| Drone desired amounts | 1 | The owner's 2026-09-25 sitting measured drone hauling from installed native desired amounts; pass 1's transient sample restored them and supplied no standing drone behavior. This build calls vanilla's writer for each configured resource. |
| Player settings | 2 | Pass 1's session-local configuration could not represent a loaded game's choices. The one hub field holds station/resource mode and percentage; a desk load event rebuilds desired amounts from it. Native serialization remains to be witnessed. |
| Row UI and counters | 0 | Native widgets and diagnostic counts are runtime-only; no saved building field, new persisted class or UI timer. |

The mod description discloses the rung-1 residual: without the mod, desired amounts
can remain as last set until a vanilla dial, resource toggle or capacity rewrite.
Hub removal retains the hub's already accepted content-removal limitations. No
custom station field, standing distribution claim, custom request-flag write or custom
persisted class was introduced. `SaveGameStart` clears active view state and releases
transient scopes exactly once; `SaveGameDone` / load reapply baselines. Request
doubles and a simulated message are not proof of native save serialization.

## Verification and scope

Commands, HEAD, hashes and captured output for the UI refinements:
[`ui_refinement_20260927/final_suite.txt`](../../archive/train_distribution_20260926/ui_refinement_20260927/final_suite.txt).
The explicit `tests/*smoke.py` list (including UI and sitting callbacks), parsechecks
for dev/shipping/TestKit code, and wrap-target check reconcile to **15 passes,
1 failure, 16 commands**. This is the full suite after the UI refinements and held
fixture. The sitting smoke executes the kit's own trigger and dispatcher bodies
with thread/ledger doubles: competing claims and hub visits cannot drain the
held stock; a source visit witnesses refusal; completion, save, cancellation and
deadline release the claim. Existing incoming/outgoing reservations refuse setup;
fixture corruption cannot pass. This does not measure the engine's ledger.
The percentage-copy follow-up has its own receipt,
[`ctrl_percent_20260927.txt`](../../archive/train_distribution_20260926/ui_refinement_20260927/ctrl_percent_20260927.txt),
including the four-state percentage assertions, unchanged plain click, and a
different-capacity destination. TestKit's preloaded refusal slots are unchanged.
Historical pass-2 measurements remain
in `docs/archive/train_distribution_20260926/pass2/`.

The failure remains `traffic_smoke.py`, `-10800 != 0` at its arrival assertion,
as pass 1 recorded. It is not silently repaired. Capacity smoke passes; capacity's
own attended result is in `TRAIN_HUB_CAPACITY_20260926.md`. The live export-floor
pairing is recorded above. The shipping wrap-target command
scans shipping `Code/`; the standalone dev distribution file additionally checks
its own declaring/alias target list before installing. The distribution harness
executes those captured aliases and compiles the owned dev Lua and registrations.

Existing doccheck warnings remain:

```text
WARN docs/archive/drones_l6_20260925/.gitattributes
WARN tools/devmods/train_hub/tests/motion_clearance_receipt.json
```

The existing ModItemCode registration and metadata list still load the UI file.
This refinement does not change metadata or the owner's editor-save fields.
No editor-owned generated asset or template was changed. `20_TrainHub.lua` and
`30_TrainHubDrones.lua` remain outside this repair.

Exact hub-header inventory line owed to the orchestrator after brief 08 closes:

```lua
--   SMROptIn_distribution   per-station/resource mode + percent on hubs (40_TrainDistribution.lua)
```

## Attended predictions - not results

TestKit slot definitions and their hash are in the current suite receipt above;
the local commit is recorded in `ui_refinement_20260927/handoff_receipt.txt`.
Scratch and capacity slots 1-3 stay unchanged. Slot 4 reads settings and ledgers;
slot 5 remains available for later import/Balanced target checks. **Slot 6 no
longer toggles full/empty.** It fills and reserves hub Metals until the export
refusal has a spoke-visit witness, then pauses and releases the reservation.

The orchestrator runs the next sitting from **`build6_capacity`**, without
saving over it. Restart to load the new Lua. These predictions are
**<<PENDING-RUN>>**; the floor pass above is already measured live. Both mods
and cheats remain the rig's setup. The active capacity upgrade gives the intended
spoke capacity 120 and hub capacity 480. Stop on a different fixture, unexpected
engine error, taint or mutation; do not rerun to obtain a preferred verdict.

| Slot | Exact label | Expected result |
|---|---|---|
| 4 | Distribution read: selected station | `SMRTK_ACTION action=slot_4 status=OK`; DUMP includes mode, enabled, percent, target, stock, capacity, coverage and hub stock/room, using live handles. |
| 5 | Run until selected station's Metals reaches slider | Existing `distribution_target` watch; export requires another spoke call. Not used during the held-hub leg. |
| 6 | Hold hub full and run export refusal (paused) | `SMRTK_ARM action=distribution_full_hub status=OK`; fixture DUMP shows `stock=480000`, `held=480000`, `available=0`, `room=0`. After a spoke visit: `SMRTK_TRIGGER ... verdict=full_refused`, unchanged spoke stock, full hub, followed by `SMRTK_DISARM ... released=480000`. |

First batch, orchestrator-guided:

1. Restart, load `build6_capacity`, pause and select the uncovered spoke. Inspect
   Electronics, Machine Parts and Rare Metals titles: breaks only between words,
   no title taller than two lines. Drag a slider: **no bubble or empty dark box**.
   Hover its row for the percent and amount. Existing native icons and layout stay
   as accepted. Screenshot + Mark any failure.
2. Put Metals in Export at 20%. **Slot 4 is the mode proof:** `mode=export`,
   `enabled=true`, `cap=120000`, `percent=20`, `target=24000`, `covered=false`.
   Ctrl-click once: the clicked row must remain Export. Slot 4 on that station
   and another network station must show Export and **20%**, even if the other
   station previously had a different percentage. The copied amount uses that
   station's own capacity. The same state-and-percentage copy applies to the
   other modes; a plain click still changes only the clicked station.
3. Still paused, select the uncovered Export spoke and use slot 2 to fill Metals
   to 120 (skip if already full). Slot 4 records the setup. Slot 6 validates that
   hub Metals has no existing supply or delivery reservation, fills its stock to
   480, reserves it and starts top speed. A `REFUSED` reservation check means the
   fixture is not quiet: stop/read that result. No run has started and no claim
   was stolen. Provisioning adds only the hub's missing Metals; slot 2 adds only
   the spoke's missing Metals. These mutations prepare this sacrificial leg.
4. Slot 6's watch samples every 100 game milliseconds. A hub visit alone cannot
   pass. After a new spoke transfer call, expect spoke **120**, hub **480**,
   `available=0`, `room=0`, `verdict=full_refused`. Normal prediction: within
   100000 game ticks; at 300000 it pauses with `verdict=deadline`, not a pass.
   The trigger pauses before releasing its native claim. Its cleanup releases
   once on completion, cancellation, save/load or map change; a save interrupts
   the leg, so no result from that interrupted run counts. Filled stock remains.
   Cancel via the kit's armed `distribution_full_hub` action if needed.
5. At the automatic pause, slot 4 and Screenshot + Mark record the station and
   hub; Flush + copy supplies the orchestrator's evidence. The live log belongs
   to the orchestrator's sitting archive. This desk work neither edits nor
   re-archives it. The refusal fixture's reservation has been released, so normal
   traffic resumes when time resumes.

The full-hub fixture uses native `AddResource` and `AssignUnit`/`UnassignUnit`,
not a stock getter override or periodic refill. It rejects pre-existing incoming
and outgoing reservations so an already-assigned hauler cannot drain the held
stock. Its own claim exists only in the kit's armed action state and is released
before saving. A replaced/reset request is not credited with an obsolete claim.
Changing the mode, network, coverage, capacity or ledger during the run ends the
leg as an invalid fixture. The test demonstrates refusal while hub stock and
room remain full/zero; it does not witness ordinary hub draining while unreserved.

## Remaining live checks

Covered drone drain/fill with a wanting/supplying local depot remains owed, now
with the pass-3 repair and predictions below. The uncovered modes and other
second-sitting results are recorded in spec §4.8. Native group expansion and
controller focus have only the coverage actually witnessed; resource-policy and
capacity rewrites still need their live witnesses. The uncovered tooltip warning
has desk coverage; the relay does not supply a separate live witness for its text.
The whole hub's both-configuration ship test remains owed to its own lane.

## Pass 3 — fractional-order crash repair, 2026-09-27

**MEASURED, desk:** the unchanged distribution code at `f989887` fails with
`Division by zero` when a covered Import spoke at 59.6 requests 60 from a hub
holding 113.5. The order is 400 milliresources. The harness now translates every
`/ scale` in its extracted archived train bodies to `// scale`, asserting that
these are all their division sites, and its `MulDivRound` double rejects a zero
denominator. This models the nonnegative integer resource arithmetic; it is not
a general engine emulator. Before/after commands, HEAD and source hashes are in
[`covered_20260927/regression_before.txt`](../../archive/train_distribution_20260926/covered_20260927/regression_before.txt)
and [`regression_after.txt`](../../archive/train_distribution_20260926/covered_20260927/regression_after.txt).

**SOURCE, archived game 1.1.1.405907:** `Lua/Units/Train.lua:894-897` sums each
enabled station's desire and capacity after dividing by scale. At `:946`, positive
aggregate desire reaches `MulDivRound` with aggregate storage as denominator.
The old answer contributes desire 1 and storage 0 for a sub-unit order.
**MEASURED, desk fix:** positive transient capacities now answer at least
`const.ResourceScale`; disabled answered rows report zero desire. The existing
demand claim keeps the exact order, so the larger capacity answer does not permit
an oversized delivery. A zero order stays disabled, preserving full-hub refusal.

**SOURCE / MEASURED, desk:** `Train:UnloadAll` (`:787-831`, same archive) uses
unscaled demand amounts and enabled answers; its distribution wrapper does not
substitute capacity. It has no matching divided-capacity failure. Fractional old
cargo unloads when it fits an Import/Balanced target, remains assigned when it
would exceed that target or the row is Export, and can unload at the hub later.
The added smoke cases verify these paths and released temporary claims.

**Corrected measurement limit:** earlier exact fractional-floor assertions used
standard Lua floating division. Vanilla's positive-desire loading lane moves
whole resource units (`Train.lua:935,943-952,1027-1028`, same archive). Under the
corrected harness, the capacity-60 Export fixture with a 1% floor of 0.6 retains
1.0; the return trip leaves it there. Integer floors retain their earlier results.
Fractional import deficits below one unit likewise wait for more demand; this fix
does not invent fractional loading or round the requested delivery upward.
Covered drones can keep changing the stock, so an exact instantaneous slider
reading is not the live acceptance criterion while they are hauling.

**MEASURED:** the explicit `tests/*smoke.py` glob plus dev/shipping/TestKit
parsechecks and the wrap-target check reconcile to **15 passes, 1 failure,
16 commands**. The failure is still `traffic_smoke.py`, `-10800 != 0`.
[`covered_20260927/final_suite.txt`](../../archive/train_distribution_20260926/covered_20260927/final_suite.txt)
lists every command, exit status and the summed result, with HEAD and file hashes.
It includes the integer-arithmetic Import/Balanced/Export boundary cases, the
existing allocation controls, full-hub refusal, aliases, UI and sitting callbacks.

The repair itself is rung 0. Overall distribution remains **rung 2**, with only
`SMROptIn_distribution` on the hub. The rung-1 native drone desired amounts can
linger after removal until vanilla rewrites them; the hub retains its accepted
content-removal residual. No new persisted name or copied runtime train body.
No game was launched. Executed model: GPT-6, as exposed by the session
instructions; no finer executed-model identifier was available. No subagents.

## Next sitting — covered drain/fill predictions, not results

**<<PENDING-RUN>>**, orchestrator-attended. Restart for the committed Lua. Load
`build6_capacity`, which has no drone coverage at its stations. Quick-build a
Drone Hub and a Metals depot beside a connected spoke, with both in the working
hub's range and drones available. Save this fixture once as
**`build6_capacity_covered_distribution_pass3`**; keep `build6_capacity` intact.
The new save is a requested future fixture name, not a claim that it exists.
Record actual handles, coverage, stock and capacity; the original fixture predicts
spoke capacity 120 and hub capacity 480. Both mods and cheats stay as configured.

The preloaded TestKit is unchanged, at `fed769c`; its slot source hash is in the
suite receipt. Slot 4, **Distribution read: selected station**, predicts
`SMRTK_ACTION action=slot_4 status=OK` and DUMP fields `res=Metals`, `mode`,
`percent`, `target`, `stock`, `supply_desired`, `demand_desired`, `cap`,
`covered=true`, `hub_stock` and `hub_room`. Contrary to the brief's shorthand,
the installed reader also emits other configured resources: use the Metals row.
Slot 2, **Fill selected station's Metals to its cap**, can provision the selected
hub while paused; its DUMP records the exact amount added. Use it only if the
hub lacks stock for the Import leg. Slots 1–3 and Scratch retain their capacity
bindings. Slot 5's exact-target watch is unsuitable while drones are changing
stock; slot 6's refusal fixture deliberately rejects covered stations.

For each leg: MARK, make the setup, run, pause for slot 4 plus Screenshot + Mark,
then end MARK and Flush + copy. The expected mode behavior follows the build's
own row tooltip:

| Leg | Setup and first witness | Prediction |
|---|---|---|
| Import | Metals Import 50%; local depot wants Metals and has room; hub has supply. Slot 4: target 60000, supply desired 0, demand desired 120000. | Trains bring Metals toward 60; local drones carry it from the station to the depot, potentially toward zero between arrivals. The row has no no-drones warning. A dip below 60 while drones haul is expected. Record station-to-depot drone work and train delivery separately. |
| Export | Use the Metals accumulated at the depot in the Import leg; lower the depot's desired amount to zero. Set station Metals Export 20%; hub has room. Slot 4: target 24000, supply desired 120000, demand desired 0. | Drones haul depot-to-station; trains take stock above the 24 floor to the hub and do not replenish the exporter. Stock can rise again after a train visit. No train departure crosses below the floor; less than one unit of fractional excess may remain. |
| Balanced | Set Metals Balanced 20%. Vary the local depot's desired amount to provide a wanting or supplying counterpart. Slot 4: target 24000, supply desired 24000, demand desired 96000. | The slider is the local drones' desired amount; trains fill a shortage or remove excess toward 24. Drones use ordinary desired-amount balancing, not Import's drain-to-zero or Export's fill-to-capacity baseline. |

Expected first useful witness: a train visit and a local drone delivery during
the first sol with a working, supplied fixture. If either is missing after three
sols, pause and return that missing witness; an unchanged stock read alone is not
a result. Provisioning cost is the quick-built Drone Hub/depot and any slot-2
Metals addition; these are intentional fixture mutations, recorded by the sitting.

The crash check runs **at least one full sol at top speed with fractional Metals
stock in play**, using the toolkit Run page's target-sol control. Start/end MARKs
record the sol/time; intermediate slot-4 DUMPs must show a stock not divisible by
1000. At least one active train route and local drone haul remain necessary.
Predict **zero `LUA ERROR` lines** across the run and no transient-claim failure
or distribution error. The orchestrator counts the complete closed-process log
with its exact error filter and reconciles matches, rather than treating a clean
screen or a truncated ring copy as evidence. Stop on the first unexpected engine
error, taint or fixture change; archive the result without rerunning for a pass.

The brief's console fallback is unnecessary for these Metals reads because slot
4 fits them. The orchestrator records measured results in spec §4.8, then handles
brief 09's retirement and prompt-map row. This handback claims the desk
reproduction and repair only; covered drone drain/fill remains unwitnessed.
