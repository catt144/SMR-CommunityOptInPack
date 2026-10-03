# Train final battery — 2026-10-02

Authority: [brief 35](../prompts/Train_Hub_Project/35_FINAL_BATTERY_high.md).
Starting shipping code: `eb36cff`; `git log --oneline -5` and `git pull` ran first,
pull already up to date. Scope: testing and recording, with failures returned to
the train orchestrator for a fix brief. **No final-battery gameplay verdict yet.**
Executed model: GPT-6 (Codex; no more specific runtime model identifier is exposed
in this transcript). No subagents.

## Work list

| Unit | State |
|---|---|
| Reconcile predictions, prepare slots, verify and commit preparation | COMPLETE; TestKit `783a24d` |
| Attended complete battery with the released fix pack | IN PROGRESS: waiting for fixture/release identity; no boot yet |
| Attended complete battery without the fix pack, fresh process | PENDING |
| Archive closed logs, reconcile verdicts/failures and cleanup | PENDING |

The save-copy choice has been asked of the owner; no save has been loaded or
changed. Autosaves must be byte-copied and inventoried before loading the copy
(CO_RUNS). Initial process check found Mars.exe closed. Initial TestKit checkout
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

Released fix-pack identity is **UNVERIFIED**. The installed junction targets
`B:/Dev/SMR/SMR-BugFixPack`; its metadata currently says 1.0.26. The command
`git -C ../SMR-BugFixPack tag --list 'fixpack*'` returns `fixpack-v1.0.0` only.
Neither a development version nor that historical tag proves the current portal
release. Resolve the released artifact before calling the with-pack leg shipping
acceptance. Keep any development-head run distinctly labeled.

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
flush, taint and eligibility; no owner console typing is planned.

## Attended batches (predictions, all NOT RUN)

Run every batch in **P = released fix pack present** and **A = fix pack absent**.
Each configuration starts in a new process; capture native mod-load lines and
slot 11. A mismatch stops that configuration before measurement. Default/off,
independent modules, combinations, first enable, disable and re-enable are
distinct cells below; a historical smoke fills none of them.

### B0 — identity, quiet baseline and real toggles

1. Boot with train options OFF; load the named copy, pause, slot 11. Expect the
   recorded pack configuration, TrainTrace false, and known hub/depot identities.
   Inspect build menu: no new hub/depot. Placed content remains operational.
2. Enable StationRows only through Mod Options and Apply. Inspect a hubless
   Small and Big Station; four states and sliders appear, on each applicable map.
   Slot 11 and Rows slot 4 record requests/settings. Toggle OFF: vanilla hubless
   behavior returns; ON restores settings. An existing hub network is not the
   negative control—use the disconnected stations.
3. StationRows OFF, TrainHub ON: hub menu appears, all ordinary station rows are
   effective. TrainHub OFF: menu disappears, existing hub/network works, hubless
   rows revert. Re-enable. Observe actual transport, not just registry booleans.
4. Both previous modules OFF, ElevatorDepot ON: placement and existing pair work
   independently; OFF hides new halves while the pair runs; ON restores placement.
5. With diagnostics still OFF, use the bounded run for active trains/cabin and
   flush. At process exit archive the complete log; repeating train trace lines
   in this quiet interval refute quiet shipping logging. Require cargo/cabin
   activity as a liveness witness. No absence verdict from a live partial log.

Also test a cold boot with each independent option state, and main-menu enable
of the mod before loading. Record actual UI and behavior for both live directions.

### B1 — hub and map crossings; OI-38

1. Crossings slot 7 starts the ledger. Expect `wiring_ok=true`, every live train
   and watched station wired, real pair/cabin wired. Incomplete wiring refuses.
2. Slot 8 runs hub route crossing at Ultra and pauses. Require `verdict=proved`,
   `bound=strict|net`, positive excess and live transfer events. Route reloading
   its own cargo, drawdown and drone-only delivery must not prove a crossing.
3. Slot 9 runs depot crossing. Require positive origin AND destination link
   excess with a direction, not merely a cabin arrival. Exercise both directions
   by setting surface Import/Export and real train supplies/destination take-away.
4. Save A during a run, re-press the watch, then slot 10 reads the ledger. Require
   retained books/rearm evidence; a load deliberately resets the ledger. Record
   every mismatch, tainted resource and open bracket. No tainted row earns PASS.
5. For OI-38 use the Upgrades train stream, then Depot departure and arrival reads
   with an Export row: record actual `cabin=up`, aboard cargo, surface/underground
   stock and next arrival. These are scripted observations on final loading.
   The controlled Depot Export fixture is a separate reservation/priority test.

Expected crossings usually within two game hours; witness deadline is twelve
game hours. `deadline` with visits is NO PROOF; without visits is a fixture gap.
Cabin departure/arrival runs have three-game-hour deadlines. Wrong direction,
missing cargo or nonconservation refutes the corresponding prediction.

### B2 — station row behavior, with and without a hub

1. On Small/Big stations on each applicable map cycle Balanced → Export → Import
   → Not accepted → Balanced. Mouse and gamepad sliders, mode tooltip, long
   titles and minimum panel scale remain usable. Ctrl-click copies current mode
   AND percentage without advancing the clicked row; depots are excluded.
2. Record untouched Balanced at its native absolute dial. Change capacity:
   untouched absolute target stays fixed; configured percentage scales. Use
   Rows slot 4 before/after and slot 5 for actual delivery to the target.
3. Export preserves its floor, Import stops at cap, Not accepted takes none;
   actual trains visit, with and without local drones. Include fractional room:
   no divide-by-zero, whole-unit loading does not overfill a sub-unit deficit.
4. Join/leave hub network; disconnect/reconnect; multiple hubs; chained
   Export/Import/Balanced with a witnessed intermediate hop. Hub and hubless
   settings stay separate. Name serving hub and route, not just a handle.
5. Unlock/relock resource requests and run NoTerraforming control. Membership
   follows available requests; do not assume the historical fixture's resource
   count. Save/load with settings, then full mod disable/restart on a content-free
   copy: no dangling claims or nonvanilla hubless desired values.

### B3 — Export floor, hub refusal and routing boundaries

1. 34b slot 1 reads a selected Export station and its controller queue stores;
   slot 2 enables pairing witness, slot 9 Food STREAM. Sample both hubless and
   hub-served stations. Use storage above, at and below Desired, plus producers.
2. Run the bounded sol. Require real storage-to-Export hauls above Desired and
   none taking below Desired; also real reverse replenishment to Desired.
   Merely zero violations without qualifying hauls is NOT PROOF.
3. Set diagnostics ON before refusal reading. On selected hub, slot 4 baseline,
   slot 5 native AssignTrain control. It refuses without spending a prefab or
   creating a train. With an available prefab add at an ordinary station and
   each depot half; owner sees it spawn there and depart. No hub auto-fill.
4. Full-hub refusal on an uncovered Export spoke: require a live train call,
   stock unchanged, hub full and held request intact. Cancellation/save releases
   the test hold. A deadline, broken hold or no train call is not a PASS.
5. Stranded cargo returns to hub first, then overflow behavior accounts for every
   unit. Cargo trap and train stream attribute the writer; distinguish vanilla
   food shortfall/over-credit from this mod (34b's routed bug). Any mismatch gets
   a verdict and orchestrator route; never rerun merely for a preferred result.

### B4 — hub economy, visuals, spoilage and upgrades

1. Fresh isolated hub with fixture Stirlings removed: cold start at 75 production,
   10 consumption. Maintenance takes 2 Electronics from own stock; reserve 4
   survives competing train exports and ordinary construction demand.
2. Cargo appears on every appropriate bed at low/high stock and after load;
   Small/Big station cubes survive capacity changes. Time/speed changes preserve
   accepted movement/art. No additional art or motion gate is introduced.
3. Actual spoilage interval with stocked controls: TrainHub ON protects ordinary
   stations, hub still spoils, other depots unchanged. OFF restores vanilla
   station spoilage. Keep incoming/outgoing Food flows out of this measurement
   or account for them explicitly with the stream.
4. Buy each upgrade once and toggle from either hub, including Ctrl-click and
   both maps/future objects. Capacity arithmetic uses additive native modifiers;
   hub storage combinations 1,000/2,000/4,000, draw 10/29, output 75/150.
   Cargo gives +25% speed; Power heats drone range and removes train cold penalty.
   Record actual purchase charges, tech and native warehousing state.
5. Save/restart, salvage buyer, remove all hubs, replace: receipts and shared
   state persist without duplicate purchase/modifiers. OFF retains over-capacity
   stock. Depot remains 250/500, outside network storage bonus. Read all four
   upgrades, current/future train capacities, power/heat and physical effects.

### B5 — hub drone and track-work matrix

1. Repair-first dispatch at fleet ceiling 60; simultaneous paired-hub launches
   retain ownership/accounting. Ordinary service inside radius; only maintenance
   at far stations. No orphan adoption; reassignment/rocket requests refuse.
2. Connected cut/reworked construction, isolated negative control, native group
   accounting and competing deliveries. Observe reachability before crediting
   completion; every dispatched group has a terminal or routed identity.
3. Hold sustained stock-out, then refill. Log actual waiting and subsequent
   dispatch; historical owner acceptance did not witness this state. Long hold,
   Lost/return paths and no-grid repair each get a named live fixture.
4. Save while drones fly/work, restart, reload. Track work OFF holds NEW jobs;
   in-flight work finishes. ON resumes queued work. Separately sample autosave
   timing. This switch is distinct from TrainHub's content module switch.
5. Active repair-notification save plus ordinary-notification control, then cold
   load: check permanent and displayed notification (D14(h)). Record old marked
   and unmarked dev-save paths and retained legacy HubTrain cargo/passengers/pool
   where fixtures exist. Missing fixtures remain NOT RUN, not inferred passes.

Carry L6 C5's historical integer/control evidence limits without rerunning an
obsolete sitting to manufacture history; capture those controls when their
surfaces next change. C6 also includes actual door clearance/work pose, far
station go-home bounce/no balancing, a hold beyond 60 seconds, packed import
and old→new→save→reload. A desk smoke proves no native save.

### B6 — depot independence, loading, survivor and save boundaries

1. With hub/rows modules OFF, test underground locked, unlocked and used. Place
   each half manually; one pair limit, paid construction, default rows/access,
   native train construction/assignment on both maps. Trains stay on their map.
2. Read-only underground row word/arrow/tooltip matches surface; only surface
   writes. Per-half Drone Access OFF/ON/OFF changes real local hauling while
   maintenance/train building remain possible; Shuttle Access stays independent.
   Observe an actual passenger train → walk → vanilla elevator → next train chain.
3. Save B, run controlled Import and Export needs (Depot slots 1/4), then slot 3
   and arrivals. Compare logged expected load against actual aboard cargo in
   consistent units. Empty destination row wins; reservations/free room limit it.
   Add competing delivery in flight, full destination and returning leftovers;
   account stock+cabin+train cargo, including every deliberate fixture write.
4. Base 250 cabin/stores; either half buys Expanded Depot for 10 Metals and 10
   Concrete → 500/500. Save during construction/travel; no concurrent duplicate,
   refund or loss. Survivor adopts the receipt; only both halves gone lose it.
5. Salvage each half while cargo travels, separately. Survivor rests with FX off,
   missing-twin notice is correct, pair recreation adopts rows/targets and resumes.
   Account cargo on BOTH salvage paths. Inspect full mod removal separately on a
   copy after demolishing all content; content residuals follow FIX_POLICY §0.

## Verdict ledger

| Batch | P | A | Evidence / failure route |
|---|---|---|---|
| B0 configuration, quiet and toggles | NOT RUN | NOT RUN | — |
| B1 crossings / OI-38 | NOT RUN | NOT RUN | — |
| B2 row matrix | NOT RUN | NOT RUN | — |
| B3 floor / refusal / cargo | NOT RUN | NOT RUN | — |
| B4 economy / upgrades | NOT RUN | NOT RUN | — |
| B5 drones / track / native save | NOT RUN | NOT RUN | — |
| B6 depot matrix | NOT RUN | NOT RUN | — |

Each result adds exact step/configuration, trigger, prediction, owner observation,
log boundary and control. FAIL, fixture gap, NOT RUN and owner PARK/CUT remain
different. Archive complete post-exit logs for negatives and preserve every
unexplained error for review. End each boot with toolkit taint and eligibility
reads. Restore baseline fix-pack enablement after A. No project-folder retirement
until every retained module satisfies the brief or the owner parks/cuts it.

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

Next: obtain the test-save filename, stage its byte copy and autosave backups,
settle released fix-pack provenance, then issue B0 as a short attended batch.
No gameplay PASS, save-copy creation or release-version acceptance is implied
by this preparation commit. Brief 35 and the project folder remain live.
