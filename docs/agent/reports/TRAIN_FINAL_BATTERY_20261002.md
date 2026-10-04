# Train final battery — 2026-10-02

Authority: owner rulings through `ddf14cc`; brief 35 is recoverable with
`git show ddf14cc:docs/agent/prompts/Train_Hub_Project/35_FINAL_BATTERY_high.md`.
Starting shipping code: `eb36cff`; `git log --oneline -5` and `git pull` ran first,
pull already up to date. Scope: testing and recording, with failures returned to
the train orchestrator for a fix brief. **FINAL BATTERY: PASS within the owner's
retained scope, 2026-10-03.** P tested against released fix pack **1.0.26**
(release status by owner); A waived. B0/B1/B2 and retained B4 checks passed;
B3/B6 owner-cleared, B5 skipped, remaining B2/B4 struck. Non-gating findings
are routed below. The orchestrator owns project-folder retirement; no more
battery work is required.
Executed model: GPT-6 (Codex; no more specific runtime model identifier is exposed
in this transcript). No subagents.

## Work list

| Unit | State |
|---|---|
| Reconcile predictions, prepare slots, verify and commit preparation | COMPLETE; TestKit `783a24d` |
| P: released fix pack installed | FINAL PASS in retained scope; native and owner evidence below |
| A: fix pack absent | WAIVED by owner 2026-10-03; not a runtime PASS |
| Archives, forced-row explanation, final verdict and finding routes | COMPLETE |
| Project retirement | ORCHESTRATOR: final evidence ready; launch-prep follow-ups are non-gating |

Owner, 2026-10-02: copy **Double Hub+elev Built Under2** as the battery fixture.
The copy's exact filename is `FINAL35_P_20261002.savegame.sav`; use filename-based
loading because its menu title duplicates the source. The staging receipt is
`docs/archive/train_final_fixture_20261002/staging.json`, including the original
save-directory inventory, source/copy hash and every protected autosave/toolkit
save by name. Backups are in `local/train-final-battery-20261002/`.
The owner accepted B0 on the fixture. The native log does not print the loaded
filename, so it is not independent proof of the exact copy's load-back. Initial TestKit checkout
`8408566` was clean and its pull was already up to date.

## Current contract and evidence boundary

SOURCE: `Code/Opt_StationRows.lua`, `Opt_TrainHub.lua`, `Opt_ElevatorDepot.lua`,
and the current parts loaded beside them. Owner decisions in spec §§4.7, 4.8,
4.10, 10, 11 and brief 34/34b reports govern over historical predictions.

- StationRows alone changes ordinary stations on either map, without a hub.
  OFF restores hubless vanilla rows/desired amounts and retains inert settings.
  TrainHub ON forces rows on; built hubs retain network rows when both switches
  are off. Station spoilage protection follows TrainHub's module switch.
- Hub/depot OFF hides new construction; placed content keeps working. A module
  toggle is distinct from full Mod Manager removal and process restart.
- Auto-fill and hub-side train spawning were cut in 34b. Audit §2's siding-spawn
  prediction is withdrawn under that ruling. Add a train at an ordinary station
  or depot; the hub must refuse without consuming a prefab. §4.9 remains rejected
  design. Movement stays accepted unless the owner reopens its parked brief.
- Hub base storage 1,000; Capacity Network and Storage Hub produce 2,000 alone
  or 4,000 together. Draw 10/29; production 75/150. Shared upgrade receipts and
  switches survive every buyer/hub removal. Depot stores/cabin remain 250/500.
- Depot: surface writes Import/Export/Not accepted, default Import; underground
  shows the same word and arrow read-only. Import goes down; Export goes up.
  Both legs load destination need, emptiest stock first, respecting reservations.
  Drone Access is independent per half, initially OFF; no own drone crew.

`python tools/doccheck.py --emit-fingerprint` ran successfully: installed Steam
build **25579348**. Game source routing is the archived **1.1.1.406343** tree.
Old fact groups marked MOVED are not current source evidence.

**OWNER, 2026-10-02: fix pack 1.0.26 IS released.** The owner explicitly instructs
this battery to cite their word because the fix-pack repo has no 1.0.26 release
record, only `fixpack-v1.0.0`. Configuration P is therefore **released Relaunched
Fix Pack 1.0.26 installed**, release status by owner testimony. The installed
junction targets `B:/Dev/SMR/SMR-BugFixPack`; read its loaded `PackVersion()` and
archive the native startup lines to confirm what this process actually tests.
The B0 native snapshot confirms loaded version `1.0.26` below. No new tag or
portal receipt is inferred.

Owner rulings 2026-10-03, read after `git pull` at `9c58d1c`: configuration A is
waived under [FIX_POLICY §8](../FIX_POLICY.md), on the evidence in
[TRAIN_FIXPACK_OVERLAP_20261003.md](TRAIN_FIXPACK_OVERLAP_20261003.md).
F65's short-track case is accepted vanilla: without the fix pack a station
one or two track pieces from a hub need not share its power. P is trimmed to
checks never witnessed live. Existing owner passes remain passes.

## Battery script and slot groups

The sitting source and reproducible loader live in `tools/trains/final_battery/`.
Slot 12 selects the next explicitly labeled group while paused and disarmed;
slot 11 reads configuration, object identities and state. Scratch switches train
diagnostics explicitly. Every boot starts with trace OFF and the Crossings group.
Only an explicit click may arm or mutate a fixture. Labels, not historical slot
numbers, determine the active group. A save disarms watches; re-press after it.

The shared script retains the crossing witness, depot readers and departure/
arrival runs, upgrade/train stream, station-row reader and 34b Food/trap tools.
Fixture writers are labeled as such and run only on the designated test copy.
Direct stock provisioning cannot prove organic train-to-cabin crossing.

| Group | Clicks used in this battery |
|---|---|
| Crossings (initial) | 1 bounded hour; 2 cabin arrival; 3 depot revision read; 4 half/row read; 5 passenger read; 6 train/station STREAM; 7 start ledger; 8 hub proof; 9 depot proof; 10 ledger read |
| Depot | 1 controlled Import setup/departure; 2 arrival; 3 capacities/cargo/upgrade/trains; 4 controlled Export setup/departure; 5 upgrade/train/rest watch; 6 departure; 7 half/row read; 8 drone hour; 9 passenger read; 10 train/station STREAM |
| Rows | 1 selected Metals fixture; 2 bounded hour; 4 rows/trains read; 5 target watch; 6 STREAM |
| Upgrades | 2 bounded hour; 3 capacities/modifiers; 4 distribution read; 5 target watch; 6 STREAM; 7 full-hub refusal fixture |
| 34b | 1 Food stores/rows; 2 pairing witness toggle; 3 bounded sol/trap polling; 4 trains/pool; 5 hub refusal control; 6 empty-pool prefab provision; 7 cargo trap toggle; 8 ledgers; 9 Food STREAM; 10 bounded hour |

Slot 11 supplements the historical upgrade read with all current upgrades,
power, requests and track-job identities. Hub roles are assigned by sorted live
handle on each read and logged with map and handle; retain that mapping across
each batch. Changing groups refuses until paused, watches canceled and 34b's
pairing/cargo recorders switched off. An absent selected fixture refuses rather
than returning a success-shaped no-op. Toolkit controls handle save/load, note,
flush, taint and eligibility. Exception for initial load: the panel requires
`GetInGameInterface()` (`71_SMRTK_Panel.lua`); it cannot provide a slot at the
main menu. The owner also confirms the console is unavailable there: first load
any save, then use the clipboard-provisioned
`*r LoadGame("FINAL35_P_20261002.savegame.sav")` inside that game. This console
exception selects the duplicate-title fixture by filename; normal checks use slots.
Owner 2026-10-02: before reading a `[TrainBay]`, pair or cabin diagnostic line,
set `SMROptInPack.TrainTrace = true`; Scratch supplies that explicit switch.

## B0 in P - PASS, 2026-10-03

**OWNER:** cold OFF snapshot; build-menu entries absent; StationRows, TrainHub and
ElevatorDepot toggled each way and behaved as expected; Rows slot 4 restored
station **10531, Metals Export**. Configuration tested: **released fix pack
1.0.26 installed**, release status on the owner's word of 2026-10-02.

**MEASURED:** the complete closed
[`Mars.exe-20261003-01.04.09-6aba6e65.log`](../../archive/train_b0_20261003/Mars.exe-20261003-01.04.09-6aba6e65.log)
is archived byte-for-byte. Reproduce the filters, counts and every member with
`python docs/archive/train_b0_20261003/read_log.py`; the executed output is
[`receipt.json`](../../archive/train_b0_20261003/receipt.json), read at `896dfc7`,
TestKit `783a24d`, game build **1.1.1.406343**. The native log reports version,
not a source commit. Current read HEAD is not claimed as its boot SHA.

| Observation | Evidence and boundary |
|---|---|
| Cold OFF | Lines 340/347/351: TrainHub, ElevatorDepot, StationRows inactive with their options false. Line 1181: `fixpack=present fixpack_version=1.0.26 trace=false errors=0`. Build-menu absence is OWNER. |
| Hub identity | Lines 597/646: **Hub 1 = 6430**, **Hub 2 = 6495**, both Surface. Those are snapshot labels, not geographic roles. Earlier row read identifies 6430 as the hub serving surface station 2007; use that role when targeting its network. No unverified role is assigned to 6495. |
| Quiet-hour activity | Canonical `[SMRTK]` records at 1196 and 3087: `hour_done`, live trains 17 in each, state changes 39 and 42; cabin-leg counters advance 25->26 and 31->32. These toolkit counters are the quiet control, with train diagnostics OFF. |
| Export restored | Rows slot 4 at 2155: station 10531, `hub=none mode=export percent=8 resource=Metals target=9600 supply_desired=120000 demand_desired=0`. Final OFF snapshot at 3824 restores native desired demand/supply 110000/10000. |
| Both toggle directions | OWNER for each module. The snapshots bracket states; they do not independently log every observed click or panel change. |
| Quiet complete log | Six train logging lines at 140/141/143/146/148/151, all startup registration/load announcements; zero repeating lines under the receipt's train-prefix filter. Zero `LUA ERROR`; normal `Debug::Done()` at 3957. B0 quiet PASS. |

⚖️ **Owner 2026-10-04 (OI-51): "seperate is fine."** The six train startup notices stay as
separate lines, as shipped, so no code action follows.

The brief's owner record says three bounded hours. The closed log contains two
canonical `hour_done` records (excluding duplicated `[mod]` echoes); a third is
not independently recoverable from this file. Keep the owner's B0 pass and the
measured boundary separately; no repeat is requested.

The broad diagnostic filter has 20 members: six Braze launcher DNS/init errors,
two retired dev-mod `Mod/SMR_TrainHubDev_20260918` permanent fallbacks, four missing
retired hub/depot mod references, and eight toolkit label/echo lines containing
"stop on error". These reconcile to the receipt's full list. None is a new Lua
error or a repair-notification warning. The old-dev references are preserved,
not erased as a "clean load"; this B0 did not contain the active repair-notice
fixture required by D14(h). No unexplained remainder in that filter.

### Why StationRows says inactive while rows work

SOURCE at `896dfc7`: `Code/00_Core.lua`'s `IsActive` reads the named module's
registry status. `Opt_StationRows.lua` therefore remains inactive when its own
option is OFF. In `Code/StationRows_40_TrainDistribution.lua:95`, `hubless_on()`
returns `IsActive("StationRows") or IsActive("TrainHub")`. Its `RowsOn()` at
839 also accepts a station served by an existing hub; the row UI delegates to
that predicate (`StationRows_45_TrainDistributionUI.lua:30`). TrainHub's toggle
callbacks call `StationRowsReapply` to refresh the effective rows.

Thus TrainHub ON forces the **row behavior** on without changing StationRows'
option or registry status. With both options OFF, a built hub still keeps its
network's rows. Slot 11's inactive status is accurate and is not a failed toggle.

## B1-B6: final owner disposition - 2026-10-03

Authority: brief 35's owner rulings, `c5db1f4` / `076e655`, and the owner's
instruction to issue B1 now. This replaces the proposed witness-review list.

| Battery | Final disposition |
|---|---|
| B1 | PASS on owner sitting/orchestrator read at `ac634ca`; archived below. OI-38 closed. |
| B2 | PASS: content-free full-mod removal restores vanilla requests. Other review items STRUCK by owner. |
| B3 | CLEARED on owner witness during hub design, also for the elevator. |
| B4 | PASS: capacity drop and unchanged stock measured; zero-hub inheritance owner-witnessed. Other review items STRUCK, including spoilage OFF. |
| B5 | SKIPPED by owner; not a native PASS. |
| B6 | CLEARED on owner witness during hub design. |

Owner scope and result rulings: `076e655`, `ac634ca`, `ddf14cc`. A skip, strike,
or waiver is not a native test pass. No stronger UP crossing-ledger proof or
cleared/skipped/struck edge is added as a gate. Placed-content removal and the
residual class warnings are bounded separately below.

## B1 in P - PASS, 2026-10-03

Owner/orchestrator ruling `ac634ca`, checked once against the named native log.
Archive: [`train_b1_20261003`](../../archive/train_b1_20261003/receipt.json), command
`python docs/archive/train_b1_20261003/capture.py`, read HEAD `ac634ca`, TestKit
`783a24d`. This is the **flushed prefix of a still-running process**, preserved
byte-for-byte. Its complete post-exit continuation is now in
`docs/archive/train_final_result_20261003/`; the capture asserts the original
archived prefix is unchanged. The closed continuation has no Lua errors.

| Witness | Native evidence |
|---|---|
| Configuration | Line 3279: P, `fixpack_version=1.0.26`, `trace=true`, errors 0. Released status remains the owner's 2026-10-02 authority. |
| Setup | Canonical `selected_fill` at 3354/3361/3366: `CheatFill` on underground Metals storages 10920, 10921, 10573 before the first arm. Fixture setup, not a retry. |
| UP departure | 3849: `departed cabin=up aboard_Metals=622`; underground depot stock 62166 raw before, zero afterward. Raw cabin read 3871/3899: `aboard_metals=62166`. The trigger's 622 is rounded tenths, not 622 whole resource units. |
| Arrival | 4258: `arrived`, legs 35 to 36, `s_Metals=622`, cabin empty. Sampling already sees the next `down` phase; it does not disprove arrival. Final surface read 4311: `metals=62166`, aboard zero. |
| Closing state | Map change disarmed the stream at 4269; closing slot 10 **re-armed** it at 4713. Trace OFF at 4720. Cancel the armed stream before changing groups. |

Receipt filters reconcile one departure, one arrival, three setup writes, and
zero `LUA ERROR` in the archived prefix to their full member lists. Its broad
error/warning filter has nine members: six Braze DNS/init errors, one retired
dev-mod permanent fallback and two old-mod reference notices. No unexplained
remainder in that filter. This is the accepted scripted up-leg read; no extra
organic crossing-ledger claim is awarded. OI-38's remaining owner action is done.

## B2/B4 final results - PASS, 2026-10-03

Owner/orchestrator ruling `ddf14cc`; confirmation command:
`python docs/archive/train_final_result_20261003/capture.py`. The
[receipt](../../archive/train_final_result_20261003/receipt.json) records read HEAD,
SHA-256, byte/line counts, filters and complete member lists. All logs are
strictly decoded UTF-8 and copied byte-for-byte. Game build: **1.1.1.406343**.

| Archive log suffix | Boundary |
|---|---|
| `20261003-12.28.41-6aba6e65.log` | Complete closed B1 log; immutable earlier prefix verified. |
| `20261003-12.55.31-6aba6e65.log` | Complete closed B4/setup log; normal shutdown, no Lua errors. |
| `20261003-13.05.06-6aba6e65.log` | Flushed removal result through line 481, process still running at capture; no closed-process claim. |

All are under `docs/archive/train_final_result_20261003/`. The error-free B2
window starts at the second `Load Game:` (line 404), not at process startup.
The first loaded save still contained custom buildings and failed as recorded
below. The owner loaded the intended content-free `SMRTK_B.sav` using
`*r LoadGame("SMRTK_B.sav")`; its provenance matches Save B.

### B4: capacity and stock

In `12.55.31`, compare the last ON snapshot (canonical hub request rows within
1122-1976) with the OFF snapshot (1977-2828). `capture.py` requires the same
nonempty object/resource keys, equal stock and game time, and each capacity
changing from 4000000 to 2000000. **38 comparisons = 19 resources on each of
2 hubs; all 38 unchanged.** The receipt contains every paired member.

| Hub / Metals | Before OFF | After OFF |
|---|---|---|
| Hub serving surface station 2007, handle 6430 | Line 1395: stock **3974400**, capacity 4000000 | Line 2247: stock **3974400**, capacity 2000000 |
| Other existing hub, handle 6495 | Line 1444: stock **1516000**, capacity 4000000 | Line 2296: stock **1516000**, capacity 2000000 |

All readings are raw resource units, at paused game time **35790404**. Thus the
serving hub retains **3974.4 Metals** against its reduced **2000** capacity;
no truncation at the OFF switch. Its post-OFF request reports `room=-25000`;
that request field is not a negative stock reading. Capacity/drop/retention PASS.

### B4: zero-hub inheritance

PASS on the owner's witness: both quick-built replacement hubs retained bought
upgrades and Storage Hub OFF. Native evidence corroborates deletion of original
hubs (2831/2836), zero-hub snapshots, replacement completion (4325/4337), and
subsequent deletion (4351/4356). The zero-hub window has no hub objects among
34 ordinary/depot object rows; the exact members/filter are in the receipt.
**No slot 11 ran while the replacements stood**, so upgrade inheritance and
no repurchase are owner-observed, not independently measured in that log.

### B2: content-free full-mod removal

Before save: both replacement hubs and depot halves were deleted; the final
snapshot has no hub/depot among 15 object rows. At 5135, Rows slot 4 reads
station **10531, underground**, `hub=none`, Metals Export. The issued script's
surface label was wrong; the actual object/map governs. Save B succeeds at 5140.

After native filename load in `13.05.06`, line 478 records
`optin_present=false fixpack_present=true native_match=true policy=default`,
capacity 120000, dial 10000, desired supply/demand **10000/110000**. This is the
pre-control-change read, matching archived **1.1.1.406343**
`Src/Lua/Buildings/Station.lua:964`'s native formula. Zero `[LUA ERROR]` from
load boundary 404 through captured end 481. **Removal/request restoration PASS**;
missing-class warnings remain a separately routed finding, not a clean-save claim.

## Non-gating findings and launch-prep routes

Owner `ddf14cc`: route all three; none gates this battery or its final verdict.

| Finding | Evidence / bounded conclusion | Owning destination and next action |
|---|---|---|
| Shared TestKit save discoverability | Native `SMRTK_SAVE` writes `SMRTK_A.sav` / `SMRTK_B.sav`; owner reports the native menu does not list them. `load_B` refuses the foreign process at 399/402. Native `*r LoadGame("SMRTK_B.sav")` succeeds. The issued native-menu instruction was wrong. | Launch-prep 01 holds an exact shared-TestKit handoff: reconcile slot extension/menu discovery and cross-process UI instructions in `75_SMRTK_Saves.lua` / SMRTK docs under that repo's authority. Keep the filename workaround; do not rewrite slots or rename saved files in this result task. |
| Class references survive deleting content | Content-free SMRTK_B still warns at 424 and 426 for **SMROptInElevatorDepotDevBase:SMROptInElevatorDepotDev** AND **SMROptInTrainHub6Base:SMROptInTrainHub6**, falling back to `UnpersistedMissingClass`. No later Lua error in the captured B2 window. A retained reference is observed; its owner/path and harm are unproved. | D17/D18 removal-residue passages and launch-prep 01's exit/rescue investigation. Trace remaining references in this exact Save B before proposing cleanup; a control removes the references without placed content and checks both warning keys on cold load. No train-battery rerun or speculative fix. |
| Full-mod removal with buildings standing | First load in `13.05.06` still had hubs/depot and raised **5 native Lua errors** at 213/265/286/336/372; the receipt lists every member. Missing methods include `GetPriorityForRequest` under `FixupHubGroupRequests`, `UpdateRevealObject`, `GetShapePoints`, `CanCommandDrones`, plus a Colony.lua call. This is outside content-free B2. | **OI-45**, launch-prep 01: owner chooses existing demolish-first limitation/disclosure or additional exit/recovery work. OI-43 remains the separate missing-mod warning choice. No corruption/crash claim and no rescue capability assumed. |

The same handoff reaches launch-prep 04 for independent review. All findings
have evidence and an owning action; no code changes or sibling writes are made.
Train battery complete; launch readiness and the owner's save-exit choices are
separate. The game remained in the mod-disabled B2 process at capture; no claim
is made that its configuration or Save A was restored by the agent.

## Preparation verification

MEASURED desk only, `f3d6c78`: enumerate
`sorted(Path('tools/trains').glob('*/tests/*_smoke.py'))`, run each with the
current Python and score its exit code. **34 enumerated = 34 exit 0 + 0 nonzero**;
the exact member list/commands and full output are preserved in
`docs/archive/train_final_battery_prep_20261002/smokes.json` and `smokes.txt`.
This does not award an attended verdict. The later `b9ec090` touches none of
`Code/` or `tools/trains/` (`git diff eb36cff..b9ec090 --stat -- Code/ tools/trains/`
is empty); its owner rulings concern D02/D04/D09, outside this train battery.

`python tools/trains/final_battery/assembly_smoke.py`: PASS. Executes the actual
current SMRTK Bind implementation with the composed script and controlled
fixtures; covers every group binding, wrong-configuration refusal on slots and
trigger preparation, missing crossing ledger, paused/armed group guards, quiet
load, explicit trace ON/OFF and quiet-hour liveness/error controls. Both present
and absent configuration guards are exercised. Engine dispatch, rendering, threads and live
save serialization remain attended work.

PROBE SWEEP: clean. Exact `grep -rln "TEMPORARY" Code/
../SMR-BugFixPack-TestKit/Code/` ran through Git's `usr/bin/grep.exe`, exit 1,
empty stdout/stderr, no hits. `preload_receipt.json` records the timestamp,
both HEADs, exact source hashes and generated-script hash. The literal command
is split only in its Lua string representation so it is not itself a sweep hit.
The first rg-equivalent draft was corrected before handoff because SMRTK's native
probe preflight requires the exact grep command; no probe ran on the draft.

Installed TestKit `783a24d` is committed and pushed; its slots match the composed
source byte for byte. `python tools/parsecheck.py --dir
B:/Dev/SMR/SMR-BugFixPack-TestKit/Code --quiet` passes. The required forbidden-call
and bare-print `rg` gates both exit 1 without diagnostics; positive control reads
the nonempty decoded `70`–`76` toolkit sources and `80_AgentSlots.lua`.

`python tools/doccheck.py`: GREEN. Remaining whole-CRLF warnings (archive bytes
retained; no mixed endings) are quoted verbatim for the attending handoff:

```text
  WARN docs/archive/train_34b_sitting2_20261002/log_receipt.json
  WARN docs/archive/train_audit_20261002/lifecycle.json
  WARN docs/archive/train_audit_20261002/log_receipts.json
  WARN docs/archive/train_audit_20261002/smokes.json
  WARN docs/archive/train_final_battery_prep_20261002/smokes.json
  WARN docs/archive/train_final_battery_prep_20261002/smokes.txt
```

Brief 35 and the project folder remain live; the preparation commit grants no
gameplay verdict.

## B0 recording verification - 2026-10-03

`python docs/archive/train_b0_20261003/read_log.py` passed its closed-log,
version, quiet-prefix and activity assertions at `896dfc7`. Full native bytes
match the source SHA-256 in the receipt. `python tools/doccheck.py`: GREEN;
`git diff --check`: clean. The whole-CRLF archive warnings remain the same
members quoted in Preparation verification; those archived bytes were not edited.
Exact `grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/` through Git's
`usr/bin/grep.exe`: exit 1, empty stdout/stderr. **PROBE SWEEP: clean.**
Shipping code, installed slots and saves were unchanged in this recording turn.
Concurrent `d1d1fc1` / `896dfc7` only changed prompt/launch handoffs; their B0
quiet-pass and fix-pack-owned cargo-defect rulings were incorporated above.

B1 recording checks at `ac634ca`: archive capture assertions and reader syntax
pass; `python tools/doccheck.py` GREEN; `git diff --check` clean. Exact Git grep
`-rln TEMPORARY Code/ ../SMR-BugFixPack-TestKit/Code/` returned exit 1 without
output: **PROBE SWEEP: clean**. The reader is an inert clipboard artifact;
shipping and installed TestKit code are unchanged. The open-log boundary is
explicit above; its closed continuation is preserved in the final-result archive.

Final close-out verification: capture assertions PASS at `ddf14cc`; all paired
stock members retained; final removal error window separated from the first
load. Executed model remains GPT-6 (Codex); no subagents. No runtime edits.

`python tools/doccheck.py`: GREEN after regeneration from D16-D18. Expected
frozen `row_status` warnings retain their historical built cells; live status
and generated index now say tested-attended. Existing archive EOL warnings
remain unchanged. `git diff --check`: clean. Exact Git grep
`-rln TEMPORARY Code/ ../SMR-BugFixPack-TestKit/Code/`: exit 1, no output.
**PROBE SWEEP: clean.** No shipping or installed TestKit code changed.
