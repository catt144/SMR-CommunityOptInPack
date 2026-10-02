# Train project audit — 2026-10-02

**Pre-move verdict: findings remain; this is not shipping acceptance.** The current
behavior passes the desk tests except the two installed-slot tests below. A historical
building-name discontinuity, incomplete live coverage, inventory omissions and stale
documentation need to travel into the move and final battery.

Authority: [brief 31](../prompts/Train_Hub_Project/31_TRAIN_AUDIT_high.md).
Behavior/test snapshot: **`000b498aefef4385bf36d9f741a60d1d5c9f4d02`**. `git log --oneline -5`
and `git pull` ran first; pull reported already up to date. The tree was initially clean.
The snapshot includes brief 30's hubless rows and depot follow-up. **Brief 30 closed
during this audit at `f8584b7`; its closing commit and log were checked.** The audited
Lua and tests are byte-unchanged from `000b498` through that close, so the run below
also covers the required closing code snapshot. Its final acceptance is bounded:
A/B/C have native readings; D is the owner's observation, without a `train_complete`
log witness. This distinction does not override the owner's PASS.

Concurrent commits `463b027` and `6485695` add/accept icon variant A; `2ba63d7` records
depot smokes A/B. `git diff --name-only 000b498 f8584b7 -- tools/devmods/train_hub/Code
tools/devmods/elevator_station/Code tools/devmods/train_hub/tests
tools/devmods/elevator_station/tests` is empty. Those commits do not invalidate the
behavioral run. The icon's template/editor/glance work remains separate.
Concurrent tooling mirrors landed in `b9257f5`, outside this report. At the final
working-tree check on that HEAD, peer edits only wire the accepted icon in the depot's
source/generated template and update its metadata version/hash. They are outside
this audit commit; the tested gameplay code is unchanged.

Executed model: **Codex, based on GPT-6**, as identified in the session instructions;
no more specific backend model identifier was exposed. No subagents. No todo tool was
available; a seven-item tool-side checklist tracked the required verdicts before writes.
No game was launched, save changed, or shared TestKit file written by this audit.

## Verdicts

| Brief item | Verdict | Evidence / consequence |
|---|---|---|
| 1. Persisted names | **Historical discontinuity; current inventory incomplete** | §1, commit `bfd748c`, current writers and native persistence keys. Reported to the owner immediately when found. Retained-save impact is unverified. |
| 2. Ship tests beyond smokes | **Owed** | §2; FIX_POLICY §§0, 8; current dev metadata has no shipping module toggles. Existing logs show the fix pack present, not the required absent configuration. |
| 3. Spec/build reports against code | **Current behavior substantially agrees with later rulings; drift and residuals remain** | §3; current Lua, archived logs and the full exit-code run. Historical proposals and superseded designs are distinguished from current faults. |
| 4. Resources | **19/21 holds in the sampled colony; membership is conditional** | §4 reconciles every member across hub, hub-served/hubless stations and depot halves. No fixed universal 19-resource contract. |
| 5. Brief lifecycle | **Historical failures; brief 30 closes correctly** | §5; deletion/rename commits and their actual map diffs. No lifecycle edit made here. |
| 6. Rulings landed | **Implemented, superseded explicitly, or carried by live work** | §6; source locations and destination briefs. Depot follow-up accepted at `f8584b7`, with evidence limits retained. |
| 7. Smokes | **28 exit 0 + 2 exit 1 = 30 files** | §7; exact glob and complete member list. The failures remain failures. |

Evidence labels below are SOURCE, MEASURED, OWNER or UNVERIFIED. A desk pass establishes
only the exercised Lua/fixture contract. It does not establish native serialization,
pixels, controller usability, engine flight clearance or an attended result.

## 1. Save contract

SOURCE commands, run from this repository:

```powershell
git log --reverse --format="%h %s" -p -- tools/devmods/train_hub/Code tools/devmods/train_hub/Data tools/devmods/elevator_station/Code tools/devmods/elevator_station/Data
rg -n 'rawset|GameVar|DefineClass|persist_baseclass|upgrade[1-4]_id|SMROptIn_|hub_notification_id' tools/devmods/train_hub/Code tools/devmods/elevator_station/Code -g '*.lua'
git show e169746:tools/devmods/elevator_station/Code/BuildingTemplate/SMROptInElevatorStationDev.generated.lua
git show bfd748c -- tools/devmods/elevator_station/Code/BuildingTemplate tools/devmods/elevator_station/Data/BuildingTemplate
rg -n 'SMROptInElevatorStationDev' tools/devmods/elevator_station/Code
```

The last grep exits **1**, with no diagnostic: the old class is absent. Positive
control over the same loaded-Code scope: `SMROptInElevatorDepotDev` occurs **8 times
in 3 Lua inputs** (Python `Path.rglob('*.lua')`, word-boundary token count). All were
decoded as UTF-8 text before searching. `bfd748c` removed the old generated class and
source template, replacing them with the depot template and custom base. The former
key is `Building:SMROptInElevatorStationDev`; the new key is
`SMROptInElevatorDepotDevBase:SMROptInElevatorDepotDev`. This is a committed-name
discontinuity, not merely a changed display title. Native fallback to `Building`
does not preserve the old template's behavior.

**Stop notification given during the sweep.** Whether the old look-only stand-in ever
entered a *retained* save is UNVERIFIED. The look report's statement that plain
`Building` meant no custom class entered a save conflicts with its generated class.
This audit neither diagnoses a corrupt retained save nor authorizes a compatibility
implementation. Brief 34's owner checkpoint needs to disposition the historical name
as well as the current ones. Other scanned prefixed removals were retired code or
runtime helper references; the legacy `HubTrain` class remains defined.

### Current names and retained legacy names

Paths in this table are relative to `tools/devmods/`. Schemas are part of the contract;
resource ids and object references are keys, not new field names to rename.

| Exact name / key | Save writer and meaning | Move impact |
|---|---|---|
| `SMROptInTrainHub6` | Hub source/generated template; placed class, `template_name`, labels and entity id. | Keep through a file move. |
| `SMROptInTrainHub6Base`, `SMROptInTrainHub6Base:SMROptInTrainHub6` | Generated `object_class` / `persist_baseclass` and native persist key. `SMROptInTrainHubBase` is the required shared class ancestry. | Keep class ancestry and exact persist base. |
| `SMROptIn_floor_hold` | `train_hub/Code/10_TrainFloor.lua`, `ReconcileRes`: `{resource={req,amount}}` on the hub. | Missing from central inventory; retain and inventory. |
| `SMROptIn_hub_crossing` | `20_TrainHub.lua`, crossing acquisition/cleanup: train reference or false. | Already inventoried; retain. |
| `SMROptIn_track_work` | `20_TrainHub.lua`, `track_work`: `{repair,jobs}`. Each job uses `kind,site,el,track,found,started,deadline,drone,held,waiting`; build jobs also `elements`; `held` contains `{req,amount}` by resource. | Already inventoried; retain schema and `repair` key even though the UI says Track work. |
| `SMROptIn_hub_native_waiter` | `20_TrainHub.lua`, `OnMsg.GatherGameMetadata` / `PreLoadGame`: metadata marker `1`, distinguishing snapshot waiter mappings. | Retain marker and legacy unmarked-save selection. |
| `SMROptIn_distribution` | `40_TrainDistribution.lua`, `Set`: hub table → station object → resource → `{mode,percent}`. Mode values `balanced,export,import`. | Retain; hub and hubless settings stay separate. |
| `SMROptIn_station_rows` | Same file, `Set/Reset`: inert station table → resource → `{mode,percent}`; dormant on a hub network. | Already inventoried by 30; retain. |
| `SMROptInTrainHub6_CapacityNetwork` | Hub upgrade slot 1 and vanilla receipts/unlocks; storage, cargo and passenger label modifiers. | Retain. |
| `SMROptInTrainHub6_TrainCargo` | Hub slot 2; cargo modifier and code-side speed gate. | Retain. |
| `SMROptInTrainHub6_Power` | Hub slot 3; purchase/state gates output, heat and cold immunity. | Retain; retired local power modifiers are migrated. |
| `SMROptInTrainHub6_StorageHub` | Hub slot 4; purchase/state gates native storage/consumption bases. | Retain. |
| `SMROptIn_hub_upgrades` | `20_TrainHub.lua`, adoption: colony table keyed by those upgrade ids, values `{on,modifiers}`; native `LabelModifier` references. | Retain even with no hubs left. |
| `<handle>_upgrade<tier>_mod_<i>` | Vanilla-generated modifier ids; `upgrade_id` stores the exact upgrade id. Capacity uses its native slots; Cargo uses its cargo slot. Migration keeps these ids and moves ownership to the colony. | No cosmetic recreation under new ids. |
| `SMROptInTrackRepair`, `Preset:NotificationPreset.SMROptInTrackRepair` | Hub notification preset id / saved permanent, `ensure_hub_notification` and `AddOnScreenNotification`. Native notification state can capture the preset. | Central inventory omission; D14(h)'s cold-load warning is still unresolved. |
| `HubTrain`, `Train:HubTrain` | Retired bay writer; bare class in `70_TrainBay.lua` preserves existing objects with native `Train` fallback. | Keep compatibility despite no new extras. |
| `SMROptInElevatorDepotDev` | Depot source/generated template, placed class, `template_name` and labels. | Contains `Dev` **inside a save name**; removing display dev tags does not authorize renaming it. |
| `SMROptInElevatorDepotDevBase`, `SMROptInElevatorDepotDevBase:SMROptInElevatorDepotDev` | Depot class ancestry, generated persist base and persist key. | Same restriction. |
| `SMROptInElevatorDepot` | Main depot entity on the placed building. Receiver/cabin/rope visuals are reconstructed separately. | Retain entity resolution for existing objects. |
| `SMROptIn_depot_rows` | `elevator_station/Code/10_ElevatorDepotDev.lua`, `SetState/OnPairChanged`: resource → `to_underground,to_surface,disabled`; underground cached copy. | Central inventory omission; retain states, surface authority and survivor adoption. |
| `SMROptIn_depot_targets` | Same file, `SetTarget/OnPairChanged`: resource → percentage; underground cached copy. | Central inventory omission; retain. |
| `SMROptIn_depot_drones` | Same file, `SetDroneAccess`: per-half boolean, absent means off. | Central inventory omission; retain independently on each half. |
| `SMROptIn_depot_cabin` | Same file, `cabin_of/Tick/HalfGone`: surface record `{phase,ends,cargo,legs,started,leg_ms}`; cargo amounts by resource; phases `at_top,down,at_bottom,up`. | Central inventory omission; retain in-flight timing and cargo. |
| `SMROptInElevatorDepotDev_Capacity` | Native slot 1 receipts/unlocks, `D.CAPACITY_UPGRADE`, `SyncCapacity`. Pair-owned purchase, no new modifier object. | New in `000b498`; central inventory omission; `Dev` is contract here too. |
| `SMR_TrainHubDev_20260918`, `SMR_ElevatorStationDev_20260929` | Dev metadata ids recorded in saved `active_mods`; the hub's `PreLoadGame` explicitly examines the former. Source templates also name their `SaveIn` mod. | Packaging changes to this mod's id need an explicit old-save path; not a blind string substitution. |
| `SMROptInElevatorStationDev`, `Building:SMROptInElevatorStationDev` | Historical look template at `e169746`, removed by `bfd748c`. | Owner disposition before claiming old-dev-save compatibility. |

The four-connector names `SMROptInTrainHub4` / `SMROptInTrainHub4Base` remain
reserved commentary, not implemented writers. Runtime tables such as
`SMROptInTrainFloor`, `SMROptInTrainDistribution`, `SMROptInHubFlight`, the bay's
`owed/snapshot`, the depot's `rigs/pair_cache` and UI widget fields are not additional
GameVars. Depot `smr_depot_prop` marks disposable art; current props clear
`gofPermanent`. Earlier saved ropes are a documented legacy cleanup issue, not a
reason to rename their marker or drop the cleanup during packaging.

SOURCE native save effects also remain: request actual/target/desired amounts and
flags; stock/visual allocation and station `transport_policy/desired_amount`;
train assignments, cargo and passenger bookings; drone battery/controller/command
state; hub work radius; native `base_max_storage_per_resource`,
`base_electricity_consumption`, `base_electricity_production`; `upgrades_built`,
`upgrade_on_off_state`, `upgrade_modifiers`, `upgrade_id_to_modifiers`,
`upgrades_under_construction`, `unlocked_upgrades`, label registrations and heat-grid
heater entries. The wrappers temporarily alter getter answers and claims, not the
names of these engine fields. Hub movement can leave bounded captured frames;
hubless saving restores native desired baselines, while hub-served baselines can
linger. These are effects to test, not extra renamable mod fields.

No current save name **has to** change to remove visible dev branding. Only the
packaging identity/path changes necessarily need review. Brief 34 owns its recorded
owner checkpoint; this report makes no rename decision.

## 2. What brief 35 still needs in game

SOURCE check: `Get-Content docs/agent/FIX_POLICY.md` §§0, 5, 8 and
`Get-Content docs/agent/prompts/Train_Hub_Project/35_FINAL_BATTERY_high.md`.
`rg -n 'Register|optional|default_options|ModItemOption'` over both dev mods'
metadata/items/Code does not establish any shipping opt-in implementation. The
current files load dev behavior directly. The move has to supply the options first.

Run the *complete* shipping battery with the Relaunched Fix Pack installed and
absent, naming the **released fix-pack version** in the report. Test each retained
module independently, the intended combinations, a cold boot, and main-menu enable.
A historical `pack_version` fingerprint alone is not the requested release-version
record. These are per-module acceptance checks, not repetitions of each design smoke:

| Shipping module / surface | In-game checks carried to 35 |
|---|---|
| Station rows alone | Hub never built and hub module disabled: Small/Big station on each applicable map; native row cycle, gamepad/mouse slider, tooltip, Ctrl broadcast and long titles at the shrink floor. Balanced uses the native absolute dial when untouched; configured percentages follow capacity changes. Export floor, Import cap and Not accepted with actual trains and with/without local drones. No divide-by-zero on fractional needs. |
| Station rows transitions | Both live module-toggle directions, including first mid-session enable. OFF returns the promised vanilla row/transport behavior; save/load preserves inert settings without leaving claims or nonvanilla hubless desired amounts after full mod disable + process restart. Join/leave a hub network, disconnected/reconnected track, multiple hubs and separate stored settings. Unlock/relock resource requests. |
| Hub content toggle | OFF removes new-building availability; existing hubs continue working under the accepted content semantics. ON offers construction again. Registry/veto and late-load behavior follow the shipping framework. This is distinct from removing the whole mod with placed hubs. |
| Hub logistics | Build and attach all connectors; auto-fill from the pool; **watch a newly spawned train on its arm's siding**. The hub does not offer train construction (§4.9's 09-28 rejection); ordinary stations and the depot supply trains. Cross-route cargo with 33's liveness/negative controls; chained Export/Import/Balanced with an actual intermediate hop; full-hub refusal and stranded-cargo return/overflow. Preserve accepted movement; reopen its parked brief only at the owner's request. |
| Hub economy/display | Isolated cold start with fixture Stirlings removed; maintenance from its own stock while trains and ordinary construction compete against the Electronics reserve. Cargo visible on every bed at low/high stock and after load; small/big station cubes with capacity upgrades. Actual spoilage: ordinary stations retain food, hub still spoils, other depots unchanged. |
| Hub upgrades | Each purchase and shared ON/OFF from either hub, Ctrl-click, cross-map trains/stations and future objects. Costs and additive stacking with native tech/warehousing; 1,000/2,000/4,000 hub storage combinations; 10/29 consumption; 75/150 output; Cargo +25% speed and Power cold immunity/ground heat. Save/restart, buyer salvage, zero hubs then replacement, no duplicate purchase/modifiers, over-capacity stock retained on OFF. Depot remains 250/500, excluded from Capacity Network's storage bonus. |
| Hub drones/track work | Repair-first dispatch at the 60 ceiling; paired-hub launch accounting; only maintenance at far stations, ordinary service inside radius; no orphan adoption, reassign/rocket refusal, return behavior, long hold/Lost and no-grid repair. Connected cut/reworked construction, isolated negative control, native group accounting and competing deliveries. Sustained stock-out/refill remains uninstrumented despite the owner's accepted build-5 sitting. Save/restart during flight/work and autosave-only timing; OFF holds new jobs while in-flight work completes; ON resumes. |
| Hub residual save checks | Marked and unmarked old dev saves, current save→restart→load, old bay `HubTrain` cargo/passengers/pool, active repair-notification cold load with ordinary-preset control (D14(h)). Keep the distinctions in D14 and L6 C5/C6; no historical integer-control or editor round-trip result is invented. |
| Elevator Depot alone | Hub and station-row modules disabled, with underground locked/unlocked/used. Each manually placed half, one-pair limit, native train controls on both maps, trains stay on their map and cargo crosses. Existing vanilla passenger walk/elevator/next-station chain remains intact. Surface-only writes; underground read-only titles/arrows/tooltip; default Import; no Balanced; no own drone crew. Per-half Drone Access default off, actual local haulers, maintenance/train construction still possible; native Shuttle Access unchanged. |
| Depot loading/upgrade | Both legs: lowest destination stock first, demand reservations and physical room bound the load; in-flight competing delivery, full destination, returning leftovers, no duplication/loss. Base 250 shared cabin/250 per-resource stores, paid 500/500 upgrade, costs 10 Metals + 10 Concrete, either buyer, no concurrent duplicate/refund, survivor adoption and loss only after both halves go. Save during travel and while constructing the upgrade. OI-38's scripted **up-leg** reading belongs here even if a short revision smoke passes. |
| Depot survivor/content toggle | Orphan rests with FX off, pair recreation resumes, retained row/target copy adopted, cargo accounted on either salvage path, both missing-twin notices. OFF stops new placement while existing pairs keep the settled content behavior; ON restores placement. The exact depot module-off implementation is 34's checkpoint, not something these dev smokes have exercised. |
| Packaging and appearance | Real packed assets/templates and fresh-install paths; editor regeneration retains authored code registration and correct icons. Blueprint/default-off visibility, player descriptions and removal disclosures; depot icon after editor save. Owner judges panel fit, cabin/rope motion, palette/day/night, door flight/work pose and clearance. |

The crossing witness in 33 needs to distinguish **hub route-to-route** transport and
**depot map-to-map** transport; they are different transfers. Autosave/drone stock
changes cannot count as train unloads. A timeout without a train visit is no refusal
proof. The accepted design-pass smokes are not grounds to drop this final matrix.

## 3. Spec and build-report reconciliation

SOURCE comparisons used the complete requested spec ranges, current dev Lua and
generated/source templates. Evidence commands:

```powershell
rg -n '^### 4\.[7-9]|^### 4\.10|^## 10|^## 11|2026-10-0[12]' docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md
git log --oneline -- tools/devmods/train_hub/Code tools/devmods/elevator_station/Code
rg -n 'HubTrackGraph|hub_visual_storage|MaxDrones|RepairReserve|BuildTimePerElement|ensure_hub_notification|sync_hub_storage|adopt_colony_upgrades' tools/devmods/train_hub/Code/20_TrainHub.lua
rg -n 'LOCAL_FIELD|function D.Set|vanilla_baseline|SaveGame|PersistGame|IsRowStation' tools/devmods/train_hub/Code/40_TrainDistribution.lua
rg -n 'CAPACITY_UPGRADE|SyncCapacity|load_cabin|destination_room|OnPairChanged|FollowTarget|InstallStationPanel' tools/devmods/elevator_station/Code/10_ElevatorDepotDev.lua
```

| Passage / report claim | Current finding and disposition |
|---|---|
| §4.7 rows require a hub in older prose | Overtaken by the 10-02 ruling and `3ff3ae4`; `D.IsRowStation`, `LOCAL_FIELD`, hubless train view and UI are present. Hubless smoke and sitting reads hold. The stale “awaiting smoke” sentence was corrected in concurrent close `f8584b7`. |
| §4.8 early checkboxes, separate section, hub-only direct routes, untouched vanilla spread | Overtaken: native four-state rows and sliders, graph ownership/chained parent routing, untouched Balanced absolute target. `distribution_smoke.py`, `distribution_ui_smoke.py`, `distribution_departure_smoke.py` and both `hubless_*` tests pass; `distribution_slots_smoke.py` fails as recorded in §7. The depot owns its rows and rejects hub writes/broadcasts. |
| §4.8 extras/need dispatcher/save-time storing | Explicitly cut by ruling 10. `70_TrainBay.lua` contains native auto-fill/siding placement and legacy `HubTrain`, not the old extras mechanism. Auto-fill remains accepted on 10-01. Spawn placement still lacks attended acceptance. |
| §4.8 “Still open” whether the hub places trains; §4.9 DESIGN ONLY | The open placement sketch is superseded by auto-fill/spawn. **§4.9 explicitly rejects hub train construction on 09-28**; its inherited-method discussion is historical design, not authority to expose a build queue. Current hub custom sections add drone status/Track work, not the depot's native train buttons. Preserve that rejection. The promised chained-hop tooltip was never built, as the later §4.8 sitting explicitly records; do not silently claim it exists. |
| §4.10 240/480 storage, city ownership, buyer-only controls, salvage removes bonus/re-buy | Historical values/rulings, explicitly overtaken. Code has 1,000 base, Storage Hub doubles its base, native Capacity Network doubles again; colony receipt and shared switch survive any/all hub removal. A native `city` target in the template is the creation route; adoption changes each retained modifier's container to the colony. It is not evidence of a current city-only scope bug. |
| §4.10 Cargo warmth and local Power | Superseded by independent global Power. Current Cargo grants cargo/speed only; Power handles +75 output, range heat and train cold protection. `global_upgrade`, `cargo_upgrade`, `cargo_heater`, `storage_upgrade` pass. Late “Power smoke owed” prose conflicts with the earlier recorded 09-29 acceptance; it is stale history. |
| §4.10 one consumption per stored resource | Implemented as the explicitly ruled **+19**, not a dynamic request-count calculation. `sync_hub_storage` selects 29,000 or 10,000. This matches the sampled 19-resource colony; if “one per resource” is intended to change after mystery unlocks, that is a further owner decision, not current behavior. |
| §10 / original hub report radius 8 or 10–20, two drones, charger/pad, +70, Metals reserve, 150 storage | Overtaken by later rulings: fixed radius 15, no functional charger/launch pad, pit/door Wasps with fleet 5/15/25 and total cap 60, +75/+150, maintenance 2 Electronics and reserve 4, base storage 1,000 while visual cap remains 150. These are deliberate evolution, not regressions. |
| §10 under-deck/scripted flight, deadline as completion authority, 30 drones | Overtaken by door/engine flight, Wasp work-end authority with persisted fallback deadline, 60 ceiling and repair-first dispatch. Current repair/buildtrack/flight smokes pass. Mesh receipts for the retired scripted route do not prove native door clearance. |
| §10 L6 corrections | C1/D14(g) desk repair remains present; C3 traffic is now exit 0. D14(h) notification registration is still dispatch/CityStart/LoadGame/InitHubTrackWork, without demonstrated pre-unpersist registration. C5 missing historical controls and C6 native matrix remain open. No broad L6 “all corrected” claim is supported. |
| §10 cross-map drone guard | OI-27 has a live **parked** owner, `Parked/23_OI27_DRONE_MAP_GUARD_high.md`, conditioned on a shaft returning/old shaft save. `HubTrackGraph` still follows reciprocal tunnel links without that guard. Do not convert the parked scope into an implemented guard; ordinary depot cargo transfer does not create a track edge between maps. |
| §11 original shared store, elevator range/autotwin, two accessible ends, drone crew, mirrored writable rows/Balanced | Later depot design supersedes these: manually placed halves, separate station stores plus scheduled cargo, one accessible train mouth, no crew, one surface writer, same Import/Export word on both panels, no Balanced. Current wiring/props tests pass. The abandoned look's no-custom-class assertion is wrong as described in §1. |
| §11 42-unit cabin and 120-unit stores | Retired by 10-02 ruling; current code reconciles 250/500 cabin and each store. Native generated template still inherits base station defaults at class creation; `SyncCapacity` applies the ruled native base on placement/load. The effective behavior is covered by revision smoke. |
| §11 destination need and twinless rest | Present at `000b498`: `destination_room`, stable lowest-stock-first sort with incoming/aboard amounts, resting orphan follower. `2ba63d7` records live A/B; `f8584b7` closes C/D without changing that code. |
| §11 missing train buttons | `InstallStationPanel` aliases native `customStation` for the exact depot base; revision smoke executes native actions. Owner accepted construction/assignment on both maps in D; no `train_complete` log reading was taken. Final shipping battery remains separate. |
| Display descriptions | Depot source/generated description still says DEV ONLY, “look” and “once an hour”, with no capacity upgrade explanation; surface→underground is one leg of the alternating schedule. Hub description promises itself plus six large stations even when Storage Hub raises its draw. Brief 34 already owns player text; distinguish base conditions and upgrade consumption. |
| Ship structure | No shipping registry/option split yet. `60_StationSpoilage.lua` directly assigns `SMROptInTrainHubBase.SpoilStoredResources`; `40` needs the floor helper. 34 must place shared helpers and spoilage deliberately so station rows and depot work with the hub module absent. The hubless harness alone does not prove all dev files can load without that class. |

### Build-report evidence ledger

All names below resolve in this reports directory. `git cat-file -e <sha>^{commit}`
checked report-cited commit ids; source claims were checked against current writers
and the corresponding smoke, not accepted from report status headings. Log receipt
hashes and bounded scans are in the archived `log_receipts.json` linked in §7.
“Historical” retains the report's tested revision and does not promote it to HEAD.

| Report(s) | Primary check and verdict |
|---|---|
| `TRAIN_HUB_PROTOTYPE_20260918`, `TRAIN_HUB_BUILD_20260918`, `TRAIN_HUB_SITTING_20260919` | Commits `dfb8052`, `625053c`, `886926b`, `5002a49`, `6123ae7`; current move/look/dwell/repair tests. Build-3b prefixed archived log exists and records native stages. Original build-1/2/3 closing log files were not recovered in the searched stores; those exact live results remain unverified here. Build 3's owner rulings are reconciled in §6. |
| `TRAIN_HUB_AUDIT_111_20260923` | `3a0faff` was withdrawn; `102f5f0` snapshot marker/legacy selection is current and dwell smoke passes. Archived crash/partial-success logs and D14 retain the limits. Old source-version statements are not current parity proof. |
| `drones_chain/L1_SURVEY_20260922` through `L6_QA_20260925` and its intermediate motion/flight reports | L6's command-bearing `docs/archive/drones_l6_20260925/audit.json` and recovered logs delimit the historical chain. Current flight/repair/buildtrack tests verify the retained mechanisms; `git show` retirement/map checks independently confirm the L2M2 lifecycle exception. Notification warning re-read in its archived native log. C5/C6 remain unverified, not re-created history. |
| `TRAIN_HUB_BUILDTRACK_BLOCKER_20260925`, `TRAIN_HUB_BUILDTRACK_20260925` | Native group mechanism and pass-2 physical graph remain; buildtrack smoke exit 0. Archived `20260926-13.24.29` ends with no active/candidate/waiting work and max 60. Owner accepted the bounded sitting; sustained shortage and one unmatched historical completion are still limitations. |
| `TRAIN_DISTRIBUTION_PROTOTYPE_20260925`, `TRAIN_DISTRIBUTION_BUILD_20260926`, `TRAIN_DISTRIBUTION_PASS2_20260926` | Prototype/pass-1 claims are superseded by allocation views, native rows and later fixes. Current behavioral/UI/departure tests pass; old installed-slot test fails. Archived `20260927-18.40.16` reads 19 station rows; earlier failed distribution frames are preserved in the capacity log. No blanket all-smokes-green inheritance. |
| `TRAIN_ROUTING_5D_20260927` | `6e187dd`, `cad784f`, `9a2d470`; current routing/departure/cargo-view tests pass. Archived routing sittings support scoped native cargo/spoilage observations; final actual chained-hop witness still owed. |
| `TRAIN_HUB_DISPATCH_20260927`, `TRAIN_HUB_BAY_20260928`, `TRAIN_BAY_FIXES_20260928` | `9947552` extra mechanism is archived; `4614075` retains vanilla auto-fill/compatibility. Train-fill and spawn smokes pass. Probe reassignment is not proof of a departure, and desk spawn geometry is not an owner visual result. |
| `TRAIN_HUB_PALLETS_20260927` | `5a42508`/later visual fixes; pallet/cargo-view tests pass. Historical stale-split diagnosis was not demonstrated live; unconditional reallocation/owner acceptance does not retroactively prove it. |
| `TRAIN_HUB_CAPACITY_20260926`, `TRAIN_HUB_CAPACITY_AUDIT_20260928` | `c6108c9`, `8a3c921`, `7dcef3e`; native capacity log confirms modifiers/storage, current capacity/global tests pass. Salvage/buyer policies were subsequently superseded, so those old assertions are not final expectations. |
| `TRAIN_CARGO_UPGRADE_20260928`, `TRAIN_CARGO_WARM_20260928`, `TRAIN_CARGO_HEATER_20260928` | `4614075`, `22f83ec`, `81c3fbe`; cargo/heater tests pass. Warmth's later transfer to Power is authoritative; earlier Cargo-warm claims are historical. |
| `TRAIN_HUB_POWER_UPGRADE_20260928`, `TRAIN_HUB_POWER_UPGRADE_20260929` | Current global/heater tests pass and native power sittings are retained under `sittings_20260929_20261001`. Their early “rerun owed” headers are not the final owner status in §4.10. |
| `TRAIN_HUB_STORAGE_20260929` | Current storage and station-visual tests pass; archived `20261001-11.16.04` carries upgraded hub readings and save actions. Owner visual acceptance remains an owner observation; no absent-fix-pack test. |
| `TRAIN_HUB_REACTOR_FLASH_20260928`, `TRAIN_TRAFFIC_SMOKE_20260928` | Reactor dust slot/look and traffic tests now exit 0. Dust-write correction and traffic-model correction are verified at desk; the owner's no-flash verdict is not a render trace. |
| `ELEVATOR_STATION_LOOK_20260929`, `ELEVATOR_DEPOT_LOOK_20260929`, `ELEVATOR_DEPOT_LOOK_20260930`, `ELEVATOR_DEPOT_DESIGN_PASS_20260930` | `e169746`→`bfd748c` template change and later rope repair commits verified. Current props smoke passes; archived rope/design logs preserve real failures. No-custom-class/no-saved-props early generalizations cannot survive the generated class and saved-rope evidence. |
| `ELEVATOR_DEPOT_WIRING_20261001`, `ELEVATOR_DEPOT_PAINT_20261001`, `HUB_TITLE_AND_DEPOT_COST_20261001` | Current wiring/props/title cases, generated costs and palette/cursor code hold. Commits `3131ad2`, `b551930`, `1122115`, `e280cda`, `9d6fd8c`, `6de571d`. Passenger/palette appearance is owner evidence; native wiring/survivor logs are distinct from mock results. |
| `STATION_ROWS_WITHOUT_HUB_20261002`, `ELEVATOR_DEPOT_REVISION_20261002` | `3ff3ae4`, `63d72d4`, `000b498`; hubless/slots and depot revision tests pass. Archived audit copy of `20261002-10.43.08` confirms rows/settings and survivor-copy events. Closing commit `f8584b7` accepts A–D: `12.28.11` has orphan-rest, upgraded-capacity and both-leg load readings; D rests on the owner's word. Earlier pending-smoke paragraphs inside the revision report are historical, not its final status. |

Historical log scope matters: the inspected capacity process contains a distribution
Lua error at line 818; the movement and notification processes contain their earlier
ArtSpecEditor error. These do not invalidate a later scoped reading, but they refute
an unqualified claim that those whole processes were error-free. The archived scans
record both positive markers and all literal `LUA ERROR` matches.

## 4. Resource membership

**MEASURED:** 21 current nominal physical leaf candidates reconcile as the following
19 request-backed ids **plus** `BlackCube` and `MysteryResource`:

`Bread, Butter, Cheese, Coffee, Concrete, Electronics, Food, Fuel, Herbs,
MachineParts, Meat, Metals, Polymers, PreciousMetals, PreciousMinerals, Seeds,
Spices, Sugar, WasteRock`.

Reproduction, Python from the repo root (build **25579348 / 1.1.1.406343**):

```python
from pathlib import Path
import re
s = Path('../SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src')
names = set()
for p in (s/'Data/Resource.lua', s/'DLC/norman/Presets/Resource.lua'):
    for block in re.split(r"PlaceObj\('Resource\w*',", p.read_text(encoding='utf8'))[1:]:
        match = re.search(r'\bid\s*=\s*"([^"]+)"', block)
        if match and not any(x in block for x in
                ('Obsolete = true', 'is_group = true', 'transportable = false')):
            names.add(match[1])
print(len(names), sorted(names))
```

This explicitly includes `ResourceIngredient` presets and excludes groups/obsolete
presets; counting only `Resource` declarations loses the delicacies. The source set
equals the depot's logged nominal row set, providing an independent control on that
static enumeration.

| Native reading | Filter / members | Result |
|---|---|---|
| `sittings_20260929_20261001/Mars.exe-20261001-11.16.04-6aba6e65.log` | Lines beginning `[SMRTK]`, `row=stock class=hub`; extract `res` grouped by `object`. | Hubs `6430` and `6495`: each the exact 19 above. |
| Audit's copied `Mars.exe-20261002-10.43.08-6aba6e65.log` | `[SMRTK]` lines with `row=resource sitting=station_rows_30`; extract `resource` grouped by `station`. | Hubless `9702`, `10531` and hub-served `2007`: each the same 19. |
| Same copied log | `[ElevatorDepotDev]   row `; nominal ids, then `stock_s>=0` / `stock_u>=0` for request-backed membership. | Each half: same 19; nominal 21; the two missing requests print `-1`. |

SOURCE parity at the audited code snapshot: all inherit native `Station:Init`
(`1.1.1.406343/Src/Lua/Buildings/Station.lua:109`), and native requests require an
enabled preset (`Buildings/MultiResourceDepot.lua:411`). Hubless/distribution `ready`
and depot `has_rows`/`destination_room` require actual demand/supply requests; none
installs a separate 19-id allowlist. **Seeds is conditional on `NoTerraforming`**, as
`Station.lua:112` shows; it is present in these readings. Mysteries can acquire
requests after unlock. Thus 19/21 is still correct for this fixture, not a promise
for every colony/DLC/rule state. Brief 35 carries lock/unlock and rule controls.

Original build-3 resource observations cannot be revalidated from its missing
`20260919-20.33.45` log. The newer source and native rows independently establish the
current answer. The original 2,850-cube figure is not a current storage prediction.

## 5. Brief lifecycle

Evidence commands:

```powershell
git log --reverse --format="%h %s" --name-status -- docs/agent/prompts/Train_Hub_Project
git show <retirement-commit> -- docs/agent/prompts/Train_Hub_Project/README.md docs/agent/prompts/Train_Hub_Project/03_Drones/README.md
git ls-tree -r --name-only HEAD docs/agent/prompts/Train_Hub_Project
```

The initial event census is retained in `lifecycle.json`: **42 deletion/parking
events**, including the design-pass brief's park and subsequent deletion as separate
events. The appended `lifecycle_close30.txt` supplies **1 more = 43 events** through
`f8584b7`; this is not a claim of 43 different briefs. The `03`→`DESIGN.md` conversion is
separate (`d8a5ca8`), not a deleted build. Root retirements:

| Brief | Retirement / disposition |
|---|---|
| Earlier portal `05` | `b3c1bba`, deleted with row after owner cut. |
| `01` | `ec51c6f`, parked with row. |
| Earlier audit `07`, `06`, `02`, body-paint `05` | `1b6f28e`, `c8a006f`, `43e3f7f`, `f447e11`: deleted with rows. |
| Distribution prototype `07`, `04`, `08`, `09` | `0976be9`, `d2e3a78`, `813b0ea`, `526496e`: deleted with rows. |
| `12` | **Exception:** `7d7d0c2` deleted the brief but collapsed the README into one line retaining its live row, contrary to the commit's claim. `04513e7` later repairs the map/removes it. |
| `11`, `13`, `14`, `15` | `04513e7`; then `389ae1e` for 13–15, deleted with rows. |
| `16`, `18`, `19`, `20` | `56e37fb`, `8786752`, `45ef933` (19/20), deleted with rows. |
| `21`, `10`, `17`, `24` | `d830519`, `0cf61f8`, `c94ac54`, `ec52ac0`, deleted with rows. |
| `23`, rail shaft | `36adc5a`, parked with rows; 23 was unfired, not a completed test. |
| `22`, `25`, `26` | `6e212af`: 22 deleted, 25/26 parked with rows; `1972103` deletes parked 26 with its row. |
| `27`, `29`, `28` | `9ba0cd9`, `eee364a`, `a60af5b`, deleted with rows. Open survivor work was transferred rather than erased. |
| `30` | `f8584b7`, deleted with row and final results/spec update. |
| Model / look / movement | Present only in `Parked/` with corresponding map entries; retained reference/touch-up scope, not live build slots. |

Nested drone retirements are `b8ab545` (L1), `0edc0c9` (L2), `0ad2e3d` (L2R),
`6a56be0` (L2M), `6d89b1a` (L2M2), `bbcd8ad` (L2E), `6cd20f3` (L3), `0fbaeae`
(L4), `d6135b8` (L5), `1c18eeb` (L6). Their own README is the applicable nested map.
**L2M2 is another confirmed timing exception:** deletion at `6d89b1a`, map/handoff
at `1e146a6`. L2E/L4 retain historical mentions in their changed map, which is not
alone evidence of a live row; the surviving `DESIGN.md`/README reference is deliberate.

At the closing snapshot no closed numbered root brief is left live. `31` is this
audit; `32` is live and `33` ready, then 34/35. The initial map's stale “30 Ready to
fire” and spec's pre-smoke state were corrected by `f8584b7`. Icon work began before
the written 30-close hold cleared; the owner accepted variant A in `6485695` and
the final map now reflects the live work. No behavior/test conclusion rests on
that timing. The orchestrator owns 31's retirement; this report edits no brief/map.

## 6. Owner rulings traced

This is a landing check, not a replacement specification. SOURCE evidence is the
symbols/commits below (`git show <sha> -- <path>` plus current source), with desk
coverage from §7. OWNER observations remain authority for visual acceptance.

### Build 3 sitting §6

| Ruling / action | Landing at the current snapshot |
|---|---|
| Footprint/lines; underside/pillars/platforms | Historical `d07a457`/`5002a49` import; current geometry deliberately advanced with the accepted radius-6 model. Move/look tests cover current structure. Do not reapply old radius-4/66-hex geometry. |
| Reactor and UI | Reactor visual kept with later palette/light refinements; `ShowUISectionElectricityGrid` suppresses only the shared grid summary; fixed radius 15, no radius slider/prefab-control design resurrected. |
| Drones/charger/pad | Working charger retired; subsequent owner pit/door fleet replaces the temporary pad and battery stopgaps. Current flight/repair code implements it. |
| Power/grid connections | Self-powered cold-start logic in `HubUpdateProduction`; later +75/+150 supersedes +70. Track/native grids remain the transmission path; no unsupported assertion that disconnected cables receive power. |
| Height/width and synthetic deck spots | `6123ae7` and later movement tuning; source/move tests retain computed geometry, with accepted owner movement controlling the final positions. |
| Storage/resources | Historical 150 storage superseded economically, retained as visual cap; §4 establishes current resource membership. |
| Texture/beds/load order | Existing imported assets and current visual tests; `20` can initialize the shared floor table. Packed assets/editor-order survival remains 34/35, not an assumption from an import. |
| Editor procedure | Source template and generated twin still distinct; no generated file edited in this audit. Current editor saves are separately evidenced by their commits. |
| Train movement stop | Movement remains untouched; only the owner's final-battery reopening is permitted by the parked brief. |
| Wasp/network construction later builds | Implemented by the later accepted flight/repair/group-construction work, with subsequent fleet and route rulings taking precedence. |

### 2026-10-01 / 2026-10-02 rulings in §§4.7, 11 (and the move rulings at §10's end)

| Ruling | Source landing / remaining live owner |
|---|---|
| Rows on every vanilla station, hub optional | `3ff3ae4`, `40`/`45`, local saved settings; A/B/C report and native log. Shipping module independence belongs to 34. |
| Accepted depot shape; production paint; core frame/receiver kept | `e280cda` material/palette, `6de571d` cursor and props; design/paint owner acceptance. Final icon is distinct. |
| Passengers use vanilla elevator after leaving train | Depot remains a Station without a new cross-map passenger implementation; recorded owner end-to-end pass. 35 preserves that path. |
| Drone Access default off on both halves, independent of Shuttle Access | `DRONES`, `ToggleDroneAccess`, request filter and native filled icon pair (`730188f`); station drone service not replaced. |
| Initially mirrored writable rows | Superseded explicitly by surface ownership/read-only underground (`8ba7ad4`). Copy/adoption remains. |
| Row shape: mode words, slider, stock/capacity; underground read-only | `34a4ee6`, `DecorateRow/InstallRowHook`; hub excludes depot rows (`c54dfeb`). Title arithmetic fixed in `1122115`/`b551930`. |
| Same word/arrow on both halves; no Balanced; unset Import | `2471213`, `941632e`, `normal_state`, `word_of`; modes and default match, old Balanced loads as Import. |
| No depot-owned drone crew | Base inherits Station, not DroneControl; no crew creation in wiring. Drone Access retained. |
| One pair and survivor behavior stand as built | `CanBuildOnlyOnce`, pair selection, `HalfGone`, `OnPairChanged`; 30's native survivor-copy read supplies the previously missing adoption observation. Both cargo-loss boundaries remain final-battery checks. |
| Half cost 5 Concrete / 2 Metals / 1 Machine Parts, 10,000 build points, no instant build | `9d6fd8c` generated/source costs; inherited native build-points default, not a missing required override. |
| Placement cursor carries complete painted art | `6de571d`, `OnMsg.CursorBuildingInit`; props smoke and recorded owner paint close. |
| Cabin loads destination need, emptiest first, both directions | `000b498`, `destination_room/load_cabin`; revision smoke and `2ba63d7` A/B live readings. |
| Cabin 250→500, both stores 250→500, upgrade 10 Metals + 10 Concrete | `000b498`, native slot 1, runtime published costs and `SyncCapacity`; revision smoke and native C at close `f8584b7`. The owner confirms charged once. |
| Both halves need native train buttons | `InstallStationPanel` / native `customStation`; revision smoke. D passed by owner observation at `f8584b7`, without a logged completion watch. |
| Orphan cabin must rest with no twin | `FollowTarget/start_cycle` path in `000b498`; revision smoke and native A. |
| Depot icon matches painted building | **Live 32**; concurrent `463b027`/`6485695` provide/accept variant A. Source/template editor save and glance are still owed, not a code-complete icon claim. |
| Auto-fill stays | `70_TrainBay.lua`; train-fill smoke. Native siding spawn still owed. |
| Hub economic and module-off defaults accepted | Generated costs and Electronics reserve hold. Content toggle is specified for 34, not implemented in the dev package. |
| Hub look accepted for now; finish deferred | Preserved by parked look/model briefs; no unsolicited art change in audit. |
| Audit → move → final battery; widen upload preflight | Live 31/34/35, with 34 explicitly carrying preflight widening and its owner checkpoint. Neither packing nor publication occurs in this audit. |

## 7. Desk run, receipts and handoff

MEASURED run at `000b498`: enumerate `sorted(Path.cwd().glob('tools/devmods/*/tests/*_smoke.py'))`,
then execute each as `[sys.executable, str(path)]` from the repository root with
`subprocess.run`. Score **returncode**, not printed “PASS”. Assert the recorded list
equals the enumerated files and group by mod and exit code. Result: **3 elevator +
27 hub = 30; 28 exit 0 + 2 exit 1 = 30**. No matching smoke was omitted.

| Smoke (under `tools/devmods/`) | Exit |
|---|---|
| `elevator_station/tests/props_smoke.py` | 0 |
| `elevator_station/tests/revision_smoke.py` | 0 |
| `elevator_station/tests/wiring_smoke.py` | 0 |
| `train_hub/tests/art_spec_smoke.py` | 0 |
| `train_hub/tests/buildtrack_smoke.py` | 0 |
| `train_hub/tests/capacity_smoke.py` | 0 |
| `train_hub/tests/cargo_heater_smoke.py` | 0 |
| `train_hub/tests/cargo_slots_smoke.py` | 1 |
| `train_hub/tests/cargo_upgrade_smoke.py` | 0 |
| `train_hub/tests/cargo_view_smoke.py` | 0 |
| `train_hub/tests/distribution_departure_smoke.py` | 0 |
| `train_hub/tests/distribution_slots_smoke.py` | 1 |
| `train_hub/tests/distribution_smoke.py` | 0 |
| `train_hub/tests/distribution_ui_smoke.py` | 0 |
| `train_hub/tests/dwell_smoke.py` | 0 |
| `train_hub/tests/flight_smoke.py` | 0 |
| `train_hub/tests/global_upgrade_smoke.py` | 0 |
| `train_hub/tests/hubless_slots_smoke.py` | 0 |
| `train_hub/tests/hubless_smoke.py` | 0 |
| `train_hub/tests/look_smoke.py` | 0 |
| `train_hub/tests/move_smoke.py` | 0 |
| `train_hub/tests/pallet_visuals_smoke.py` | 0 |
| `train_hub/tests/reactor_dust_slot_smoke.py` | 0 |
| `train_hub/tests/repair_smoke.py` | 0 |
| `train_hub/tests/spoilage_smoke.py` | 0 |
| `train_hub/tests/station_visuals_smoke.py` | 0 |
| `train_hub/tests/storage_upgrade_smoke.py` | 0 |
| `train_hub/tests/traffic_smoke.py` | 0 |
| `train_hub/tests/train_fill_smoke.py` | 0 |
| `train_hub/tests/train_spawn_smoke.py` | 0 |

Both failures read the **installed**, mutable
`B:/Dev/SMR/SMR-BugFixPack-TestKit/Code/80_AgentSlots.lua`, not an immutable sitting
fixture. TestKit HEAD was `7c3781bf566685b229c0b47f0c446d3807f4e567`; slot SHA-256
`96e51d423e8f9961ce5b1ec1f2bd48553a16bc38872c18ab47791fdcd7d6aaff`.
Cargo expects old slot 3's upgrade snapshot, and distribution expects old slot 4's
row snapshot. The installed depot slots return a refusal boolean for those unrelated
fixtures, producing `attempt to index a boolean value`. This diagnoses a sitting/test
contract mismatch; it does not turn either test green or establish a production
transport regression. **No TestKit checkout/restore was attempted.** The current
hubless/depot staged-slot tests pass. The historical traffic failure is now exit 0.

Evidence files (append-only):

- [smokes.json](../../archive/train_audit_20261002/smokes.json): exact command, HEAD,
  member and exit-code reconciliation.
- [smokes.txt](../../archive/train_audit_20261002/smokes.txt): full stdout/stderr,
  including both tracebacks and harness limitations.
- [lifecycle.json](../../archive/train_audit_20261002/lifecycle.json): deletion/parking
  census; root-map token presence is an initial locator, with disputed destination
  passages inspected explicitly in §5.
- [brief 30 retirement](../../archive/train_audit_20261002/lifecycle_close30.txt):
  final additional lifecycle event and its map/spec/report changes.
- [log_receipts.json](../../archive/train_audit_20261002/log_receipts.json): existing
  archived-log hashes, exact marker filter and literal error counts.
- [station-row sitting log](../../archive/train_audit_20261002/Mars.exe-20261002-10.43.08-6aba6e65.log):
  byte copy; SHA-256 `3677c7945f7677fd56f42ebb3f0b4f18418fa020a194dcf940a28cf53bf993b7`.
  Strict UTF-8 decode succeeds; literal `LUA ERROR` has no hits, while
  `sitting=station_rows_30` has **354 matching lines**, including the log's duplicate
  mod/plain emissions. Resource counts above deduplicate ids and select plain lines.
- [brief 30 closing log snapshot](../../archive/train_audit_20261002/Mars.exe-20261002-12.28.11-6aba6e65.log)
  and [receipt](../../archive/train_audit_20261002/close30_log_receipt.json):
  SHA-256 `9e536b773e52389cefbdbb0baf161da149e0f842892596a37db6a9d8859942f4`.
  Orphan-rest reading at 435; upgrade completion at 1125; underground's 500/500
  reading at 1134; 500-unit departures at 1279 and 1375. Literal `train_complete`
  and `LUA ERROR` each have zero hits after strict decoding; the same file has
  **34 `cabin_capacity=500` lines** as a positive control (including duplicate
  emissions). It is a finite audit snapshot, not a claim the still-running process
  ended cleanly. D remains OWNER evidence.

The missing build-3 log search enumerated both repositories' `docs/archive/` and
the live game log directory, including ignored files. Exact timestamp searches
found neither `20260919-13.47.41` nor `20260919-20.33.45`. The inspected suffix
inventories contained no `.gz/.zip/.zst/.zstd/.xz/.7z/.bz2` candidates to decode.
This is a bounded availability result, not proof that no external backup exists.

Ban-2 check: `rg -n SMRFixPack tools/devmods/train_hub tools/devmods/elevator_station -g '*.lua'`
exits 1 without error; Python enumerated **34 decoded Lua inputs, all 34 containing
`SMROptIn`** as the positive control. No executable fix-pack reference was found in
that scope. This source result does not replace the absent-fix-pack game run.

`python tools/doccheck.py --emit-fingerprint` read installed Steam build **25579348**.
Older fact groups report MOVED; game-source citations in the current analysis use
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src`. Historical log claims retain
their own game revision. The pre-test temporary-probe sweep was clean in pack
`Code/` and shared TestKit `Code/`.

### Takeable work

| Reader / trigger | Work carried by this report |
|---|---|
| Orchestrator, audit report committed | Brief 30's closing diff and C/D are checked here. Retire 31/map row through its declared lifecycle; route historical-name disposition and evidence gaps to 34/35. The final up-leg/shipping matrix remains independent of the accepted smoke. |
| Brief 32 | Complete the accepted icon's template/editor/glance path; the PNG alone does not wire its build-menu use. |
| Brief 33, after 30 frees the shared slots | Resolve the installed-slot test dependency as part of making a reproducible final witness; retain failing/pass controls and distinguish both kinds of cargo crossing. Do not restore another sitting's TestKit. |
| Brief 34, owner checkpoint | Use §1's complete name/schema inventory, including the removed stand-in and notification permanent. Record keep/rename consequences and legacy-save disposition. Put names in FIX_POLICY at implementation, split helpers/spoilage without a hub dependency, implement real OFF/ON gates, rewrite player text and widen actual-pack preflight. Explicitly disposition every remaining finding. |
| Brief 35, shipping layout ready | Carry all §2 controls, D14(h), remaining C5/C6 boundaries, actual siding spawn, real serialization, old dev saves and the named released fix-pack two-configuration matrix. Record failures and owner deferrals as such. |

No shipping code, spec, brief or checklist was edited for these findings. They remain
in this report for the orchestrator, as the audit's scope requires.

Documentation verification: `python tools/doccheck.py` ran at `b9257f5` on 2026-10-02,
exit 0, **GREEN**, including its required selftests. The archive's `.gitattributes`
keeps both copied native logs as exact binary bytes; their recorded hashes are the
integrity check, independently of line-ending settings.
The staged-file run remains GREEN and reports whole-CRLF warnings for `lifecycle.json`,
`log_receipts.json` and `smokes.json`; none has mixed endings. Their working copies
are retained under the append-only archive rule, while Git stores normalized text.
