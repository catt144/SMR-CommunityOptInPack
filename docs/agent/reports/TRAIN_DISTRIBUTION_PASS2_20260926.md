# Distribution — crash repair, section UI and next sitting

Authority: `prompts/Train_Hub_Project/09_TRAIN_HUB_DISTRIBUTION_high.md`, pass 2;
spec §4.8's owner delegation (`e1daef6`), §4.7's UI ruling (`94bb535`),
and the owner's orchestrator relay of 2026-09-26. Pass 2 landed in `c90a670`;
this desk repair starts after the pull to `813b0ea`. The nil-cargo fix is
`0a41767`; the section UI is `969c7c3`. This follow-up moves its XDef check to
runtime after the second sitting's load-order failure.
Executed model: GPT-6 as exposed by session instructions; no more specific model
identifier was exposed in the transcript. No subagents.

**Desk repair complete; hand back to the orchestrator. Export to the floor has
NOT RUN live.** The first sitting exposed the crash below and rejected the row UI;
the second stopped at step 1 because the section never registered. Neither sitting
ran the floor test. The late-class guard now passes the corrected desk harness.
The next sitting starts from the owner's `build6_capacity` save, hub standing and
capacity upgrade on, with uncovered-spoke export as its headline. Native section
appearance, mode acceptance and save/load remain owed; this is not a ship test.

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
`docs/archive/train_distribution_20260926/`. The same sitting plan below stands.

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
vanilla behavior. Both unchecked after setting the slider means a configured
balanced row; an untouched row retains vanilla's current dial until adjusted.

**MEASURED, desk:** the six rewrite paths reapply drone baselines through archived
`Station:SetDesiredAmount`, including a recreated request reached through the
captured `RegisterResourceRequest` alias. The capacity getter also has a captured
depot alias; both it and the declaring method receive the transient wrapper.
Network-wide doubling changes the tested export floor 12 to 24 and the hub max
240 to 480. This is the harness-driven rewrite, not the live upgrade pairing.

**SOURCE / MEASURED with UI doubles and archived grouping:** `45_TrainDistributionUI.lua`
attaches one `InfopanelSection` to the station's contained `ipBuilding.idContent`,
using TestKit's `section_attach` / `DialogOpen` pattern. Vanilla row methods and
children are untouched. The section owns Basic / Advanced / Delicacies / Other
tabs, independently of vanilla expansion. A lone resource stays in its named tab;
hidden resources stay hidden until unlocked. The no-drones line precedes the tabs.
Each resource shows its name, `stored/max`, mutually exclusive Import / Export,
and a slider with a changing amount/percentage label, e.g. `Keep 24 (20%)`.
Neither checked is Balanced. Disabled resources cannot change settings; full hubs
are identified on export rows. A mouse-only `?` on the header owns all help text.
No standing popup or new update thread is created; native context updates refresh
the section. The hub has no controls. Native rendering, hit boxes, hover dismissal,
scrolling and gamepad focus still need the attended check.

## Save ladder and residuals

| Part | Rung | Basis for this rung and why the lower one is insufficient |
|---|---|---|
| Train allocation and old-cargo unload limits | 0 | Archived-body tests above achieve the floor and import target with temporary getter answers and claims; no higher rung needed. SaveGameStart injection observes original enabled/capacity answers and released claims. |
| Drone desired amounts | 1 | The owner's 2026-09-25 sitting measured drone hauling from installed native desired amounts; pass 1's transient sample restored them and supplied no standing drone behavior. This build calls vanilla's writer for each configured resource. |
| Player settings | 2 | Pass 1's session-local configuration could not represent a loaded game's choices. The one hub field holds station/resource mode and percentage; a desk load event rebuilds desired amounts from it. Native serialization remains to be witnessed. |
| Section UI and counters | 0 | Widgets, callbacks, selected tab and diagnostic counts are runtime-only; no saved building field or new persisted class. |

The mod description discloses the rung-1 residual: without the mod, desired amounts
can remain as last set until a vanilla dial, resource toggle or capacity rewrite.
Hub removal retains the hub's already accepted content-removal limitations. No
custom station field, standing distribution claim, request-flag write or custom
persisted class was introduced. `SaveGameStart` clears active view state and releases
transient scopes exactly once; `SaveGameDone` / load reapply baselines. Request
doubles and a simulated message are not proof of native save serialization.

## Verification and scope

Current commands, HEAD, hashes and captured output:
[`ui_load_order/final_suite.txt`](../../archive/train_distribution_20260926/ui_load_order/final_suite.txt).
The explicit `tests/*smoke.py` list (including UI and sitting callbacks), dev parsecheck
and wrap-target check reconcile to **13 passes, 1 failure, 14 commands**. The full
suite also ran immediately after the crash fix and after the section rewrite.
`repair/scope_receipt.txt` checks
fenced paths and unchanged capacity bindings. Historical pass-2 measurements remain
in `docs/archive/train_distribution_20260926/pass2/`.

The failure remains `traffic_smoke.py`, `-10800 != 0` at its arrival assertion,
as pass 1 recorded. It is not silently repaired. Capacity smoke passes; capacity's
own attended result is in `TRAIN_HUB_CAPACITY_20260926.md`. Distribution's live
pairing with it is still owed. The shipping wrap-target command
scans shipping `Code/`; the standalone dev distribution file additionally checks
its own declaring/alias target list before installing. The distribution harness
executes those captured aliases and compiles the owned dev Lua and registrations.

The existing ModItemCode registration and metadata list still load the UI file.
Only the description changes in metadata; the owner's editor-save fields remain.
No editor-owned generated asset or template was changed. `20_TrainHub.lua` and
`30_TrainHubDrones.lua` remain outside this repair.

Exact hub-header inventory line owed to the orchestrator after brief 08 closes:

```lua
--   SMROptIn_distribution   per-station/resource mode + percent on hubs (40_TrainDistribution.lua)
```

## Attended predictions — not results

TestKit bindings are local at `bf75983` (on `a8352dc`), with no remote. Slot 5 now
requires a new **spoke** transfer call for export; a hub-only call cannot pass a
floor recheck. The desk case exercises that rejection and the subsequent spoke
visit. Scratch and capacity slots 1–3 are unchanged. Current fingerprint and
pre-sitting checks are in `ui_load_order/prelaunch_gates.txt`; read them for the installed
build rather than carrying forward an old fingerprint. Existing doccheck warnings:

```text
WARN docs/archive/drones_l6_20260925/.gitattributes
WARN tools/devmods/train_hub/tests/motion_clearance_receipt.json
```

**<<PENDING-RUN>> All live predictions below.** The orchestrator attends with the
owner from **`build6_capacity`**, without overwriting it. Restart the game for the
updated Lua, so the former row wrapper is not retained by a hot reload. The hub is
already standing with the capacity upgrade on. Both mods and cheats are the rig's
standing setup. Use an uncovered small spoke connected to the hub on its train
route, with Metals enabled. No setting is chosen automatically. Confirm live
capacity **120**, hub capacity **480**, coverage false, and space at the hub before
running; investigate mismatched fixture readings before applying these predictions.

| Slot | Exact label | Expected result |
|---|---|---|
| 4 | Distribution read: selected station | `SMRTK_ACTION action=slot_4 status=OK`; DUMP rows carry live handles, mode, percent, target, stock, request targets/desired amounts, coverage, hub stock/room and train cargo. Also samples taint and eligibility. |
| 5 | Run until selected station's Metals reaches slider | `SMRTK_ARM action=distribution_target status=OK`, then `SMRTK_TRIGGER ... verdict=at_target`; exact stock/target equality and a new spoke call for export (spoke or hub for other modes); pauses automatically. Re-press after autosave. |
| 6 | Toggle hub Metals full / empty (paused) | Explicit fixture mutation: less than full becomes full, already full becomes empty, through vanilla AddResource. DUMP reports before/after. No resource other than Metals is changed. |

Slot 5 samples every 100 game milliseconds. Prediction: target reached within
100000 game ticks; the 300000-tick deadline pauses with `verdict=deadline` instead
of treating a stalled train as a pass. The slot starts the kit's highest speed;
no real-minute wait or owner-polled stock reading is required. A changed setting,
missing fixture or error is a stop/read, not a rerun for a preferred result.

First batch, orchestrator-guided:

1. Load `build6_capacity` and pause. Select the uncovered spoke and open its own
   **Import / Export → Basic** tab. Vanilla resource rows should retain their old
   appearance. The no-drones line should be above the tabs. Check the header `?`:
   hover shows help, moving away dismisses it; no explanation stays over controls.
2. Set Metals to Export, **20%**. Import clears and the label reads **Keep 24 (20%)**.
   Slot 4 should report `cap=120000`, `percent=20`, `target=24000`,
   `supply_desired=120000`, `demand_desired=0`, `covered=false` (ledger units).
3. Slot 2 fills the selected station to **120**. Slot 6 makes hub room (if a press
   fills it, the next empties it). Slot 4 records setup; the section reads `120/120`.
4. Slot 5 runs to the target or deadline. Prediction: trains remove **96**, leaving
   **24**, with the section reading `24/120`. At pause, use slot 4 and Screenshot +
   Mark. Re-arm slot 5: it must see another call at that spoke, with stock still
   **24**, before reporting the return-trip pass. A hub call alone is insufficient.
5. Flush + copy. The orchestrator reads the newest log and inspects the screenshot.
   Any crash, floor overshoot, deadline or UI failure is recorded as observed.

The 120 × 20% = 24 and 120 − 24 = 96 arithmetic was emitted in
`repair/scope_receipt.txt`; those are still live predictions. This sitting is also
the required pairing of distribution with the already-active capacity upgrade.

## Remaining live checks

After the headline floor leg: new-train arrival at a configured Concrete row;
import at its percentage with stock at the hub; Balanced; full-hub refusal; covered
drone drain/fill with a wanting/supplying local depot as in the 2026-09-25 fixture;
uncovered import with its warning; resource disable/re-enable; and a separate test
save/reload with modes and cargo outstanding. Observe native UI fit and tab/slider
operation, not just the desk callbacks. Resource-policy and capacity rewrites have
desk coverage; native baselines and serialization still need their live witnesses.

No game was launched during this repair. The first sitting's log above stays its
single archive copy. The orchestrator records the next sitting's measured
mode/station/coverage and folds it into spec §4.8. Brief 09 stays live; its retirement
belongs to the orchestrator. The whole hub's both-configuration ship test remains owed.
