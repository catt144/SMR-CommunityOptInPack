# Train final battery — 2026-10-02

Authority: [brief 35](../prompts/Train_Hub_Project/35_FINAL_BATTERY_high.md).
Starting shipping code: `eb36cff`; `git log --oneline -5` and `git pull` ran first,
pull already up to date. Scope: testing and recording, with failures returned to
the train orchestrator for a fix brief. **B0 in P: PASS, owner 2026-10-03.**
The final scope is ruled at `076e655`: B1 is issued below; one combined B2/B4
batch follows its result. No other B2-B6 checks remain in this battery.
Executed model: GPT-6 (Codex; no more specific runtime model identifier is exposed
in this transcript). No subagents.

## Work list

| Unit | State |
|---|---|
| Reconcile predictions, prepare slots, verify and commit preparation | COMPLETE; TestKit `783a24d` |
| P: released fix pack installed | B0 PASS; B1 issued, awaiting owner result |
| A: fix pack absent | WAIVED by owner 2026-10-03; not a runtime PASS |
| Archive B0, explain forced rows, reconcile remaining checks | COMPLETE in this update |
| Final scope | APPROVED `076e655`: B1, then B2 removal + B4 zero-hub persistence / over-capacity OFF |

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
| B1 | APPROVED: OI-38's five-step streamed up-leg read below; awaiting result. |
| B2 | Retain only content-free full-mod removal/restart restoring vanilla requests. Other review items STRUCK by owner. |
| B3 | CLEARED on owner witness during hub design, also for the elevator. |
| B4 | Retain only upgrade persistence through zero hubs and replacement, plus over-capacity stock after OFF. Other review items STRUCK, including spoilage OFF. |
| B5 | SKIPPED by owner; not a native PASS. |
| B6 | CLEARED on owner witness during hub design. |

After B1 is read, issue **one combined batch** for the retained B2/B4 cases.
Their predictions remain: a replacement hub inherits paid colony upgrades and
shared state without repurchase; reducing capacity by switching the storage
upgrade OFF retains stock above the new cap; full mod removal on a content-free
copy restores vanilla station requests after a fresh process. Work on fixture
copies. The passed B0 and prior accepted evidence are not repeated. No stronger
UP crossing-ledger proof or other cleared/skipped/struck edge is added as a gate.

## Issued B1 owner batch - OI-38; awaiting result

Issued 2026-10-03 under the approved final battery. Current TestKit `783a24d`:
`Get-FileHash` on installed `Code/80_AgentSlots.lua` and the retained composed
source both returned SHA-256
`0c991302949b6c206cd784775412e359645ac7e2a3df8bfa9c119cb71fcbaa65`;
the live group bindings were read before issuance. No slot edit or restart is
needed for new code. Use the battery copy with fix pack 1.0.26 installed and
ElevatorDepot ON. No hub is selected: targets are the **surface depot** and its
**underground twin**; route references use the serving hub's role.

1. **Slot 12 - next labeled group**, paused with watches disarmed, until **Depot**.
   **Scratch - train diagnostics switch**: set `SMROptInPack.TrainTrace = true`
   and confirm `trace=true` before any diagnostic read. **Slot 11 - configuration
   snapshot**: predict P / `1.0.26`, Depot group and the actual pair identities.
2. Select the **surface depot**. In its native row UI choose **Metals Export**,
   with Metals stocked underground and room at the surface; retain normal train
   service. **Depot slot 7 - halves/rows read**, then **slot 3 - capacities/cargo
   read**. Predict a working pair, the shared Export word, origin stock and
   destination room. No controlled stock-writing slot is part of this batch.
3. **Depot slot 10 - train/station STREAM ON**, then **slot 6 - next departure**.
   It runs Ultra and pauses. Predict `verdict=departed cabin=up` and nonzero cargo
   for the Export resource. A first DOWN departure is recorded as the intervening
   leg; wait for its arrival, then arm the next departure once. A deadline or
   empty UP is a recorded fixture/result gap, not permission to provision and retry.
   Each departure/arrival watch has a three-game-hour deadline.
4. At the UP pause, **Depot slot 7 - halves/rows read** and **slot 3 - capacities/
   cargo read**, then **slot 2 - next arrival**. Predict `arrived`, top phase,
   reduced underground stock, cleared/delivered cabin cargo and corresponding
   surface stock/train movement. Reconcile units across readers and stream;
   report competing flows instead of assuming an unchanged destination.
5. **Depot slot 3 - final capacities/cargo read**, **slot 10 - STREAM OFF**,
   **Scratch - trace OFF**, then **Sitting - Flush + copy**. Orchestrator reads
   the result before anything else is issued. A save disarms stream/watch;
   re-press the named controls if that occurs. OI-38 stays open until a usable
   UP departure/arrival reading is actually obtained.

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
