# Distribution second pass — desk build and attended predictions

Authority: `prompts/Train_Hub_Project/09_TRAIN_HUB_DISTRIBUTION_high.md`, pass 2;
spec §4.8's owner delegation, recorded in `e1daef6`. Tested base:
`e1daef62f8546b93beb0671e49056712f40216ec` plus this commit's diff.
Executed model: GPT-6 as exposed by session instructions; no more specific model
identifier was exposed in the transcript. No subagents.

**Desk implemented; attended smoke pending.** The owner has not seen these rows
or played these modes yet. This is not a ship test or a claim about native save/load.

## Result and mechanism

**MEASURED, archived-body harness:** pass 1's controls reproduce: initial stock 80,
floor 20 retains 60 with an equal sink and 36 with a four-times-larger sink. The
new view drains to the slider and stops on the return trip, with source/hub capacities
60/240, 60/480 and 100/100, at sliders 0/1/20/50/99/100 percent.

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

**MEASURED, UI doubles:** the boxes exclude one another; unchecking returns to
balanced; the slider writes a percentage; disabled resources disable controls;
the coverage note appears; the native stored/max readout remains; the hub gets no
controls. Native layout, mouse hits, readability and gamepad focus are untested.
Controls are children of each existing resource row, below its original title and
readout. Basic / Advanced / Delicacies / Other grouping is untouched.

## Save ladder and residuals

| Part | Rung | Basis for this rung and why the lower one is insufficient |
|---|---|---|
| Train allocation and old-cargo unload limits | 0 | Archived-body tests above achieve the floor and import target with temporary getter answers and claims; no higher rung needed. SaveGameStart injection observes original enabled/capacity answers and released claims. |
| Drone desired amounts | 1 | The owner's 2026-09-25 sitting measured drone hauling from installed native desired amounts; pass 1's transient sample restored them and supplied no standing drone behavior. This build calls vanilla's writer for each configured resource. |
| Player settings | 2 | Pass 1's session-local configuration could not represent a loaded game's choices. The one hub field holds station/resource mode and percentage; a desk load event rebuilds desired amounts from it. Native serialization remains to be witnessed. |
| Resource-row UI and counters | 0 | Widgets, callbacks and diagnostic counts are runtime-only; no saved building field or new persisted class. |

The mod description discloses the rung-1 residual: without the mod, desired amounts
can remain as last set until a vanilla dial, resource toggle or capacity rewrite.
Hub removal retains the hub's already accepted content-removal limitations. No
custom station field, standing distribution claim, request-flag write or custom
persisted class was introduced. `SaveGameStart` clears active view state and releases
transient scopes exactly once; `SaveGameDone` / load reapply baselines. Request
doubles and a simulated message are not proof of native save serialization.

## Verification and scope

Commands and complete captured output are in
`docs/archive/train_distribution_20260926/pass2/`. `verification.txt` records the
input hashes; `final_verification.txt` reconciles the explicit `tests/*smoke.py`
list (including sitting callbacks) plus parsecheck and the wrap-target check:
**13 passes, 1 failure, 14 commands**. It also checks the fenced files against HEAD
and verifies that adding distribution bindings preserved capacity's slots exactly.

The failure remains `traffic_smoke.py`, `-10800 != 0` at its arrival assertion,
as pass 1 recorded. It is not silently repaired. Capacity smoke passes, but that
does not discharge brief 08's attended sitting. The shipping wrap-target command
scans shipping `Code/`; the standalone dev distribution file additionally checks
its own declaring/alias target list before installing. The distribution harness
executes those captured aliases and compiles the owned dev Lua and registrations.

The ModItemCode source registration in `items.lua` and regenerated metadata code
list add `45_TrainDistributionUI.lua`. No editor-owned generated asset or template
was changed. `20_TrainHub.lua` and `30_TrainHubDrones.lua` remain outside this diff.

Exact hub-header inventory line owed to the orchestrator after brief 08 closes:

```lua
--   SMROptIn_distribution   per-station/resource mode + percent on hubs (40_TrainDistribution.lua)
```

## Attended predictions — not results

TestKit bindings are committed locally at `a8352dc`; its standing no-remote rule
applies. `prelaunch_gates.log` records doccheck GREEN, kit parse, forbidden-writer
searches and their positive source control. The installed fingerprint is build
25390750 (1.1.1.405907). Existing doccheck warnings, verbatim:

```text
WARN docs/archive/drones_l6_20260925/.gitattributes
WARN tools/devmods/train_hub/tests/motion_clearance_receipt.json
```

**<<PENDING-RUN>> All predictions below.** Use `train_hub_base`; build the hub as in
spec §10. Do not overwrite that save. The rig's standing setup has both mods and
cheats enabled. Selected station's Metals is the first resource. The original
fixture lacks drone hubs, so the covered legs need the local controller/depot
setup used in the 2026-09-25 sitting. No setting is automatically selected for the
player. Slots 1–3 and Scratch preserve brief 08's capacity bindings.

| Slot | Exact label | Expected result |
|---|---|---|
| 4 | Distribution read: selected station | `SMRTK_ACTION action=slot_4 status=OK`; DUMP rows carry live handles, mode, percent, target, stock, request targets/desired amounts, coverage, hub stock/room and train cargo. Also samples taint and eligibility. |
| 5 | Run until selected station's Metals reaches slider | `SMRTK_ARM action=distribution_target status=OK`, then `SMRTK_TRIGGER ... verdict=at_target`, with exact stock/target equality and a station or hub transfer-call witness; pauses automatically. Re-press after autosave. |
| 6 | Toggle hub Metals full / empty (paused) | Explicit fixture mutation: less than full becomes full, already full becomes empty, through vanilla AddResource. DUMP reports before/after. No resource other than Metals is changed. |

Slot 5 samples every 100 game milliseconds. Prediction: target reached within
100000 game ticks; the 300000-tick deadline pauses with `verdict=deadline` instead
of treating a stalled train as a pass. The slot starts the kit's highest speed;
no real-minute wait or owner-polled stock reading is required. A changed setting,
missing fixture or error is a stop/read, not a rerun for a preferred result.

First batch, from the owner's seat:

1. Start the updated dev mod, load `train_hub_base`, build/connect the hub, and
   pause. For the first UI look, use a station covered by a working local Drone
   Controller with a Metals depot in range. Open its Basic resource group.
2. In the Metals row, check Export and set the slider to 20%. Confirm Import
   clears; press slot 4. The read should show supply desired = live capacity,
   demand desired = 0 and the player percentage. Judge the row's visual weight.
3. Use slot 2 to fill that selected station's Metals. Use slot 6 to give its hub
   room (if the first press fills it, the second empties it). Slot 4 records setup.
4. Press slot 5; it runs and pauses at the target or deadline. Press slot 4 and
   Screenshot + Mark. Local drone deliveries can refill a covered exporter, so
   the train-only stopping witness is repeated on the uncovered spoke next.
5. Flush + copy and say "flushed". The attending agent reads the newest Mars log
   and inspects the screenshot; the owner says whether the row reads right.

Next batches: import at the selected percentage with stocked hub (slot 6), native
drone drain/fill with a wanting/supplying local depot, uncovered train-only export
and import with the warning visible, full-hub refusal, then a save to a separate
kit slot and reload with modes and cargo outstanding. To confirm an uncovered
exporter stays at its floor, re-arm slot 5 there: require a further transfer call
and unchanged stock. Native readouts, not the desk checks, decide these legs.

## Attended smoke

<<PENDING-RUN>> No game was launched for this build. No new game-session log exists
yet. On the owner's "flushed", archive that log byte-for-byte, record each measured
mode/station/coverage, fold the results into spec §4.8 and hand back. The brief stays
live; the orchestrator owns retirement. The live Capacity Network Upgrade pairing
and the both-configuration ship test remain separate obligations.
