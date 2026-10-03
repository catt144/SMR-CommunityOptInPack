# Mechanized depot throughput — 2026-10-03

**Verdict: feasible as a bulk transfer at crane landing, with the vanilla look and
motion code preserved. A literal larger load held in flight is a different, more
expensive design. Recommend post-launch, with a fixed ×5 boost first.** Desk
investigation only; no module built, no throughput measured in play.

The owner's observation is authority: the vanilla depot drains into the Export
station, slowly. This investigation accepts that and does not diagnose a mod block.
The proposed distinction matters: the economical route leaves five units on the
moving crane and transfers the extra stock synchronously at its destination. If
the owner specifically requires all boosted stock to leave the source at pickup,
this report does **not** certify that stricter design.

## Work list and evidence boundary

- [x] Pull and identify the input revision; read policy and task skills.
- [x] Pin current archived source; trace pad requests, visuals and crane accounting.
- [x] Identify wrapper seams and OFF/save hazards; compare StationRows and shuttles.
- [x] File the source finding in the fix pack first and mirror EF-121 here.
- [x] Present the design choice and size; route the remaining owner decision to OI-46.
- [x] Documentation checks GREEN; report and one-off retirement delivered in this commit.

Input: Opt-In `666980332e3a4a7016b990df1985fe37312e4d95`; `git log --oneline -3`
and `git pull` ran, reporting already up to date. Fix Pack source census:
`56d725791b04f628b028c2ea5400d4aeef33185c`. Executed model identity exposed by
the transcript: GPT-6 / Codex; an exact deployment/model suffix was not exposed.

**Every game citation below means game 1.1.1.406343, Steam build 25579348,
archived tree `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src`.** Build
identity was read with `python tools/doccheck.py --emit-fingerprint`. Scoped
archive/manifest/live-Src hashes agree; this is source evidence, not a new FPK
parity claim or a runtime test.

Reproducible desk evidence:

```powershell
python docs/archive/mechanized_depot_20261003/evidence.py docs/archive/mechanized_depot_20261003/receipt.json
```

[RAN 2026-10-03, desk receipt; no game log]. [Receipt](../../archive/mechanized_depot_20261003/receipt.json)
contains hashes, regexes, file members, caller sites and the derived capacity table;
[script](../../archive/mechanized_depot_20261003/evidence.py) asserts the load-bearing
source shapes. It searches decoded archived Lua, including DLC and CommonLua.
All totals reconcile against their member arrays. Matched source files: 18 =
7 machinery files + 11 generated depot templates. The manifest SHA-256 is
`d753f949af92e2b753f44163a2e47229e371f810ef3c2752d30a98953af2663c`.
For a later rerun, use a new output path under `scratch/`; the original archived
receipt is historical evidence. Fact allocation landed in Fix Pack commit
`30dacada`; the mirrored EF-121 SHA-256 is
`4227c7498e1a7d288c57f82ee120fd41551217da3689be5e759b748d479ff62c`.

## Where the bottleneck lives

| Claim | Evidence and consequence |
|---|---|
| SOURCE: this is a separate depot family | `Lua/Buildings/StorageDepot.lua:834-835`: parents are `Building`, `StockpileController`, `ResourceStockpileBase`, `ElectricityConsumer`; it is not `StorageDepot`. EF-102's historical class distinction still holds on this build. |
| SOURCE: one shared input/output pad | `StorageDepot.lua:858-867`, `:1009-1019`: `ResourceStockpileLR`, both supply and demand, reciprocal requests. These are not separately sized input and output buffers. |
| SOURCE: pad capacity is 50 units | Its dimensions are 5 × 2 × 5; `ResourceStockpile.lua:746-747` implements `GetMax()` as that product. The requests use `GetMax() * const.ResourceScale` at `:320-336`. |
| SOURCE: main storage is 3,950 units for Machine Parts | `Lua/BuildingTemplate/MechanizedDepotMachineParts.generated.lua:31-36`: Desired defaults to 3 units, main capacity is 3,950,000 raw units. The owner's Desired 100 is a player setting. Base UI total is 4,000, including the pad (`StorageDepot.lua:1068-1070`). |
| SOURCE: each crane cycle transfers five units | `StorageDepot.lua:1160-1185`: file-local `store_step = 5 * const.ResourceScale`, passed with either sign to `Store`. It is not a modifiable class property. |
| SOURCE: output refills in small pulses | `:1170-1180`: expected pad stock, including booked arrivals/pickups, must be at most five; room for five and at least five in main storage are also required. |
| SOURCE: intake uses different thresholds | `:1181-1185`: expected pad stock at least 20, actual at least 10, main storage room at least five. Enlarging the buffer alone does not enlarge the batch or change these thresholds. |
| SOURCE: crane work requires power and serializes | `:1161-1168`: one `is_storing` thread at a time, with a power check before scheduling. |

The template census reconciles **11 resource templates**: Concrete, Electronics,
Food, Fuel, MachineParts, Metals, MysteryResource, Polymers, RareMetals,
RareMinerals, Seeds. Ten directly inherit `MechanizedDepot`; MysteryResource
inherits `MechanizedMysteryDepot`, whose parent is `MechanizedDepot`
(`StorageDepot.lua:2050-2052`). `MechanizedDepotStockLane` is a helper with parent
`Object` (`:1799-1800`), not a twelfth shipping resource depot. The script's
`families` array records every member and its 3,950,000 raw main capacity.

**SOURCE: cycle timing varies with the selected lane and current crane position.**
`StorageDepot.lua:1189-1270` uses 200 ms motion pauses and 300 ms pickup/drop
pauses. `:1436-1545` uses 150 ms per coordinate step, with horizontal travel
`(abs(start_x-x)+abs(start_y-y))*150` and vertical travel
`abs(11-z)*150`. `CenterHoist` can add another movement and pause
(`:1548-1574`). These are game-time milliseconds, not a measured resources/sol rate.
An exact cycle is the two `CraneGoTo…` durations, both retractions, pickup/drop
pauses, the final pause and any centering. Observe it in the owner's actual depot
rather than infer one rate for every lane and fill level.

**SOURCE: drones see requests on the pad, not the 3,950-unit main inventory.**
`ResourceStockpile.lua:320-336` constructs them; `StorageDepot.lua:1011-1019`
adds the resource maps and reciprocal link. `:972-979` translates the depot's
Desired Amount into pad request desires using total stored stock. At total stock
well above Desired, the pad supply can have Desired zero; that permits its stock
to leave while the main storage refills it five at a time. `Lua/_TaskRequest.lua:65-86`
returns an unassigned native match; `Lua/Units/Drone.lua:1130-1139` reserves the
requests before travelling. Actual and Target therefore both matter.

## Keeping the look

**SOURCE: the pad drawing already caps itself independently of request stock.**
`ResourceStockpile.lua:597-604` converts raw stock to cube units and clamps drawing
to `max_x * max_y * max_z`. `:549-594` draws individual/grouped resource entities.
The normal geometry therefore accommodates 50 unit positions; some resources use
grouped entities, so this is not necessarily 50 separate visible objects.

**INFERRED: wrap the declaring `ResourceStockpileBase:GetMax`, scoped to a vanilla
mechanized depot's actual attached pad, and multiply its returned logical capacity.**
Leave `max_x`, `max_y`, `max_z`, entity, footprint, attachments and placement code
alone. Stock above 50 then remains in requests and native `stockpiled_amount` while
the existing draw clamp shows a normally full pad. No custom drawing code or
asset is indicated. `CraneGoToIO` also already caps its stock-height coordinate
(`StorageDepot.lua:1577-1582`).

Changing dimensions instead would change both the draw cap and cube placement;
that is the wrong mechanism for this requirement. Leave main capacity and lane
dimensions unchanged too: lane stock is coupled to its geometry
(`StorageDepot.lua:1971-2006`). The proposal enlarges working buffers and transfer
pulses, not the whole warehouse.

**INFERRED: the native crane model, carried cube attachments, motion routines and
speeds can remain unchanged.** `GameInit` creates the carried cube attachments once
(`:1054-1064`); `SetHoistCubesVisible` toggles those existing objects (`:1430-1433`).
Stock lanes will empty/fill in larger increments, and the next selected lane can
differ. “Same animation” here means the existing motion/attachment code and look,
not identical frames over an entire colony's history. Visual preservation still
needs an attended A/B.

## Mechanism and policy fit

**INFERRED: a bounded landing bonus is the smallest credible route.** Keep native
`TryStore` and `Store` intact, including their ±five argument and their in-flight
`carrying` boolean. At the destination, transfer up to the additional batch amount
between the native pad and main storage in the same synchronous operation.

The seams are `MechanizedDepot:SetCount` and the declaring
`StockpileController:UpdateStockpileAmounts`. Native `Store` calls the former for
main storage and the latter for the pad (`StorageDepot.lua:1193-1198`). Distinguish
its landing from pickup and other work with all of: eligible vanilla depot,
`CurrentThread() == self.is_storing`, `self.carrying`, the right resource and the
expected positive five-unit destination delta. At pickup, `carrying` has not yet
been set; at landing it is still true (`:1205-1218`, `:1232-1245`).

| Direction | Synchronous input adjustment, before calling the captured original |
|---|---|
| INFERRED: pad → main | In the positive `SetCount` landing, take extra **unbooked** pad supply, then increase the original's requested main count by exactly the amount taken. Limit extra to the boost ceiling, `Min(supply Actual, supply Target)` and main room after the vanilla five. |
| INFERRED: main → pad | In the positive `UpdateStockpileAmounts` landing, take extra main stock, then increase the original's requested pad amount by exactly that debit. Limit extra to main stock, the boost ceiling and `Min(demand Actual, demand Target)` room after the vanilla five. |

Round extra down to native five-unit lane increments; never consume drone/shuttle
reservations. The inverse leg has a negative delta, so it does not satisfy the
positive landing predicate. Keep source debit and destination credit together with
no yield, and pass every original return through. Base/off adds no bonus.

The outer operation explicitly uses the adjusted amount: this is not a post-hook
that independently spends capacity its caller just freed. The receipt enumerates
tree-wide `SetCount`, `UpdateStockpileAmounts` and `GetMax` sites. Relevant competing
main setters in `StorageDepot.lua` are direct resource changes (`:1277-1325`), daily
spoilage (`:1328-1332`), clear/fill cheats (`:1741-1785`) and crane pickup/landing.
The pad updater also appears in the save fixup (`:2109-2123`). Other controllers,
cheats and fixups cannot opt in merely by passing the same numeric delta; the
thread and object predicates are essential. `Store`'s search reconciles three
rows: two thread starts (`:1180`, `:1185`) plus its declaration (`:1190`), with no
other textual call in the decoded tree.

**INFERRED: per-object application is possible without a per-object saved setting.**
A global Mod Options multiplier can apply independently to each eligible depot and
its pad. Shared-class wrappers delegate immediately for foreign objects. No class
dimension mutation or per-pad function assignment is needed. Restrict eligibility
to the enumerated shipped class names and pad ownership, rather than including
arbitrary third-party subclasses. A separate saved multiplier for each depot
would require a new setting field and is outside this proposed shape.

The reconciler must resize existing pad requests when the choice changes and on
load, not merely wrap `GetMax` for new request creation. Preserve the supply amount
and outstanding bookings; add the capacity delta to demand in place, then refresh
`UpdateStockpileDesire`. Do not recreate requests under travelling drones/shuttles.
Also cover UI capacity: `GetUIMaxStorageAmount` reads the geometry directly
(`:1068-1070`), while `GetMaxStorageForAnyOneResource` reads the request sum
(`:990-993`). `GetEmptyStorage` has a separate hardcoded +5,000 raw allowance
(`:956-958`), and `AddResourceAmount` clamps/reroutes against pad `GetMax`
(`:1277-1306`). These require explicit capacity/overflow treatment, not an
assumption that one wrapper updates every capacity reader.

**Policy assessment:** this follows §1's chained wrappers and §3a layer 3:
synchronous input changes, native blocking crane body. File-scope hooks before
flattening, declaring-class `Require` checks, foreign-object delegation, per-call
status/veto gates and idempotent reconciliation follow §2/§5. A dial would use the
D09 lifecycle (ApplyModOptions, CityStart, PostLoadGame); a toggle can use the core's
activation/deactivation callbacks. No wholesale replacement is indicated for this
landing design. Its correctness remains a design inference, not an implementation
or an engine-level proof of native request resizing.

## OFF, reduced capacity and saves

**Recommendation: retain stock above the reduced pad capacity and let it drain.**
Do not truncate it, and do not automatically push the excess into main storage.
Main storage may be full; drones and shuttles may already have reservations.
If intake is naturally active and there is main room, native five-unit cycles can
move stock inward. Otherwise it remains on the pad until consumers/exports collect
it. Drainage requires available work and, for crane movement, power; it has no
unconditional completion deadline.

This is consistent with the owner-accepted train B4 retention result in
[TRAIN_FINAL_BATTERY_20261002.md](TRAIN_FINAL_BATTERY_20261002.md), “B4: capacity and
stock”: reducing capacity retained the stock above it. That result supports the
product choice; it does not prove the mechanized pad uses the same request machinery.
Here decreasing capacity while holding supply constant can produce negative demand
room (`ResourceStockpile.lua:439-450`, `:861-863`). Preserve booked deliveries and
stop **new** intake while over capacity; native negative request behavior must be
tested, including whether a zero-advertised-demand transition is needed.

**SOURCE hazard: direct depot `AddResourceAmount` is not simply a drain path.**
With an oversized pad, even a small subtraction can still leave `new_a > stock_max`;
`:1288-1306` then removes the excess from the pad and sends it toward main storage,
clamping against main capacity. A base/OFF transition therefore needs a bounded
overflow guard for these existing over-capacity objects until they drain, so a
rover/direct resource change cannot lose stock. It adds no new persisted marker:
over-capacity is detectable from native stock and capacity. Settled base objects
delegate exactly to vanilla. This transitional retention behavior needs the owner
choice in OI-46; it is not silently declared byte-vanilla.

**INFERRED: an OFF switch can leave a crane cycle running safely in this design.**
Only the native five units are in flight. The future landing sees base and adds no
bonus; if the bonus already landed, it is native stored stock. There is no enlarged
crane cargo to refund. A true multiplied `Store(amount)` is unsafe as a lone wrapper:
`GetStoredAmount` counts carrying as five (`:1137-1146`), direct removal also assumes
five (`:1309-1316`), and `MechanizedDepotResetInFlightStoreThread` returns only five
to IO on fixup (`:2109-2123`). The schedule checks also guarantee room/stock for five,
not for a multiplied payload. Tracking a literal enlarged payload through saves
would need additional reliable state and separate recovery design. This report
stops short of that design; a required new persisted name or wholesale body copy
returns to the owner under the brief's stop 2.

| Save surface | Assessment |
|---|---|
| SOURCE: existing stock fields and request objects | Main/lane and pad `stockpiled_amount`, supply/demand actual/target/desired amounts, drawn cube objects, and native crane state already exist. The proposed boost changes their values, not their identities. |
| INFERRED: new saved depot fields/classes/GameVars/modifier ids | None needed by the landing design. Do not borrow an unrelated existing field to hide a cargo ledger. |
| INFERRED: new settings contract | A new module option/registration key, and any dial choice strings, are required for the new feature. §3's inventory includes these too. Their exact names require the owner-authorized build specification; no name is minted here. This is distinct from needing a new saved cargo field. |
| INFERRED: saved executable code | Synchronous wrappers create no suspended mod frame or new thread. Keep native `Store` and its local helpers; install no per-object method closures. Verify this shape in save/removal testing. |
| UNTESTED: removal with an oversized pad | Persisted native requests may retain boosted capacity even though vanilla `GetMax` reads 50; direct changes have the clamp hazard above. Native object types alone do not prove clean removal. |

A possible save-time normalization could remove boosted request capacity from the
snapshot without discarding stock, but it must coordinate with reservations and
other save handlers. It is additional §3a layer-1 work, not assumed necessary or
proven here. The inexpensive initial exit is: set base, let every oversized pad
drain to its vanilla capacity, save, then disable in Mod Manager and restart.
That procedure needs testing before it becomes player-facing advice. Base/save
alone cannot promise safety if stock is still oversized. No current uninstall
documentation is changed by this investigation.

## Size, settings and interactions

| Setting | Logical pad capacity | Maximum transfer per eligible landing | Total depot capacity | Visible pad unit positions |
|---|---:|---:|---:|---:|
| SOURCE/DERIVED: base | 50 | 5 | 4,000 | 50 |
| DERIVED: ×2 | 100 | 10 | 4,050 | 50 |
| DERIVED: ×5 | 250 | 25 | 4,200 | 50 |
| DERIVED: ×10 | 500 | 50 | 4,450 | 50 |

These arithmetic figures come from the executed evidence script. “Maximum transfer”
includes the native five plus bounded extra, not a measured rate. Main capacity
stays 3,950. For an observed cycle duration T, the vanilla pulse is 5/T and the
boost ceiling is 5m/T. Cycle positions, partial batches, reservations, travel time,
power, demand and station/train capacity prevent promising an m-fold end-to-end
speedup. Leaving the native 5/20/10 thresholds means output still refills at the
low-water trigger; changing refill timing is a separate scope choice.

**GUESS, session estimate:** fixed ×5 toggle: **2–3 working sessions**, including
implementation/desk checks, save and reservation checks, and an attended visual
A/B with the fix pack present and absent. A base/×2/×5/×10 dial: **3–4 sessions**,
because every decrease and reload boundary adds cases. These estimates assume the
landing seam behaves as read and the owner can attend the required checks. Session
counts are effort estimates, not measurements or scheduled sittings.

**Recommendation:** fixed ×5, off by default, post-launch. It provides a substantial
candidate pulse without committing to another dial before its trade-offs are seen.
A dial offers useful colony tuning and matches D09's familiar control, but its
benefit should be established before multiplying boundary tests. Risks that enlarge
the job: negative native demand behavior, reservation preservation, direct/rover
overflow, snapshot normalization, spoilage on oversized food pads, and visually
large lane jumps. A literal enlarged in-flight payload would also reopen stock
accounting and save recovery; the estimate above does not cover it.

**SOURCE + INFERRED: StationRows Export.** At input HEAD,
`Code/StationRows_40_TrainDistribution.lua:223-272` caps an `rfStorageDepot` source
to `Min(Actual, Target) - Desired`, with one alternate-source retry. Mechanized pad
requests carry `rfStorageDepot` and `rfMechanizedStorage`
(`StorageDepot.lua:861-865`). Larger pad supply is therefore eligible under the
same surplus filter; it does not bypass Desired or allow a drone to lift directly
from main storage. Native depot unload mode clears `rfStorageDepot`
(`:1717-1729`), so that mode takes the existing producer-style path in the filter.
Preserve those flags, desires and reciprocal requests. The new module works with
StationRows off and with an ordinary destination too; no cross-module dependency.

**SOURCE + INFERRED: shuttles.** The pad is `ResourceStockpileLR`; its registration
and shuttle toggle are in `ResourceStockpile.lua:1275-1302` and
`StorageDepot.lua:914-938`. `Lua/LRManager.lua:195-199` uses the native shuttle
matcher, not the StationRows `TaskRequestHub.FindTask` wrapper. Larger buffers can
support shuttle cargo, but do not enlarge shuttle capacity or impose StationRows'
Export floor on shuttle selections. Shared drone/shuttle reservations constrain
the landing bonus and request resize. Keep Shuttle Access and queue registration
unchanged.

**Desk census: no explicit mechanized/stockpile-base target in this fix-pack Code.**
The executed script and independent `rg -n --no-ignore` used
`MechanizedDepot|rfMechanizedStorage|StockpileController|ResourceStockpileBase|ResourceStockpileLR`
against decoded `Code/**/*.lua`: Fix Pack **47 files, zero hits**; Opt-In **19
files, zero hits**. Both file lists are in the receipt. This bounds the absence
claim to those targets in current source; it does not rule out generic/shared
methods or indirect traffic effects. The broader manual search found fix-pack
shuttle availability/cache and track-refund work, not a crane/buffer patch.
Compatibility still requires the both-configuration check; this census is not a
compatibility PASS.

## Cheap owner read and remaining decision

This console line only reads the selected mechanized depot. **[NEVER RUN]**; it is
optional information for a later authorized build/check, not an owed playtest.
Stock/requests print in raw resource units (divide by `const.ResourceScale`).

```lua
local d=SelectedObj; if IsValid(d) and IsKindOf(d,"MechanizedDepot") then local p=d.stockpiles and d.stockpiles[1]; if p and p.supply_request and p.demand_request then local s=p.supply_request; local r=p.demand_request; print("mech",GameTime(),d.class,d.handle,"scale",const.ResourceScale,"main",d.stockpiled_amount,"total",d:GetStoredAmount(),"desired",d.desired_amount,"pad-max",p:GetMax()*const.ResourceScale,"pad",p:GetStoredAmount(),"supply",s:GetActualAmount(),s:GetTargetAmount(),s:GetDesiredAmount(),"demand",r:GetActualAmount(),r:GetTargetAmount(),r:GetDesiredAmount(),"carrying",d.carrying,"thread",IsValidThread(d.is_storing),"visible-count",p.count) end end
```

For timing, two idle snapshots around one observed full native crane cycle provide
a game-time interval; console input delay makes it an approximate observation,
not a precise benchmark. A build can add a read-only TestKit pickup/landing witness
if exact cycle timing is needed. No save inspection or runtime probe was performed
in this investigation.

OI-46 asks the owner to choose the landing-bonus interpretation, a stricter in-flight
cargo design, or parking, and whether to authorize a post-launch fixed boost versus
a dial, including its new option contract and retained-overflow transition.
Evidence is filed in [EF-121](../facts/EF-121.md), allocated in the Fix Pack first
and mirrored here. Source mechanics are settled to the cited build; live visual,
conservation, toggle, save and removal behavior remains untested.

Documentation validation: `python tools/doccheck.py --regen` and
`python tools/doccheck.py` GREEN in the respective filing trees; `git diff --check`
clean. Doccheck's stale-probe sweep was clean; no retail test started. The report,
OI-46 and fact preserve the remaining decision; the consumed prompt and map row
are deleted together. No kernel status or shipping behavior changes arise from
this source investigation.
