# Train hub build 5 — pass 2 implemented, acceptance smoke pending

The original implementation receipt below describes pass 1. Pass 2's diagnosis, changes and
current attended predictions follow it; the stopped pass-1 sitting is in spec §10.

Authority: owner `d230bd4`, "1 is fine": a line uses native construction-group accounting
and completion. Element-by-element completion and pricing are not authorised. Pulled with
`git pull --ff-only` (already current); distribution prototype commit `d2609dd` landed in the
shared tree during implementation. Its metadata edit is excluded from this build commit.

Implemented in the dev hub only. No native game was launched for this build; no line timings,
save-file result, visual acceptance or shipping status are claimed. Brief 04 remains live.

## Behavior

- New construction groups on unfinished tracks incident to the hub's physical network become
  `kind = "build"` jobs in `SMROptIn_track_work`. Unfinished tracks do not extend that network.
  A disconnected line waits until its end station becomes reachable. Queued jobs recheck reach
  before dispatch. Native groups remain intact; if vanilla splits a line into groups, each
  native group is serviced separately, never by splitting or repricing its members ourselves.
- The existing toggle is labelled **Track work** and gates new build and repair dispatches.
  Its persisted `repair` key and callable methods keep their names. Jobs already dispatched
  finish after switch-off. Ordinary drones are unrestricted.
- Builders use the group's full outstanding native demand, with no repair discount. At work
  end they deliver as much free hub stock as possible through the native `AddResource` path.
  The maintenance reserve and supply claims remain protected. Native target demand excludes
  ordinary drones' reservations; the builder waits for those deliveries instead of paying
  them twice. A shortage signs the hub and keeps the builder at the site; replenishment resumes
  payment and the group's native `Complete()`. Nanite-deferred completion is retried without
  charging supplied resources again. Repairs retain their existing claim and discount path.
- `BuildTimePerElement` defaults to 1000 game ms per live member counted when the group is
  queued, added to the flight's ordinary work time. This is a tuning choice, not a measured
  game balance result. The per-flight duration is restored on adoption. Flight death or a
  save during scripted work can restart the trip/work pose; supplied resources remain native
  state and are not paid again. No new top-level persisted field or mod-owned job thread.
- Dispatch/completion logs carry job kind, group element count, and game-time duration.
  Completion elapsed time is the latest trip, reset by a relaunch; retain dispatch/relaunch
  timestamps when measuring a whole line across a save or lost Wasp.
- D14(g) is corrected: counting hub A's rising drones no longer deletes hub B's live records.
  Source comments about deadline authority and deadline-based adoption were brought into line
  with the already recorded flight-authoritative rulings.

**SOURCE:** archived build **1.1.1.405907 / installed 25390750**, matching the executed
`python tools/doccheck.py --emit-fingerprint`. Under
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua/`:
`Tracks.lua:329-383,419-474` creates/groups new sites and sets native pricing;
`TrainTransport.lua:57-66` exposes connector elements;
`Buildings/ConstructionSite.lua:1560-1575` supplies native resource requests and
`:2671-2718` completes group members (or defers to nanites). The original stop's source
audit is `TRAIN_HUB_BUILDTRACK_BLOCKER_20260925.md`; its decision is settled.

## Desk verification

Command-bearing outputs, HEAD and runtime source hashes are preserved under
`docs/archive/train_hub_build5_20260925/`. All readings are against the implementation diff
on `d2609dd`; they are mocked execution or static checks, not attended game evidence.

| Command / evidence | Result and limit |
|---|---|
| `python tools/devmods/train_hub/tests/buildtrack_smoke.py` | PASS. Includes the existing repair smoke, then connected/isolated/delayed lines, partial payment, ordinary-drone reservations, reserve protection, group-time scaling, mocked load adoption, toggle directions, native-completion retry, drones finishing first, lost connection and alternating hub launches. `buildtrack.txt` carries the output and hashes. |
| `python tools/devmods/train_hub/tests/flight_smoke.py` | PASS. New control exercises per-flight work duration and callback refusal until stock returns; existing stock-command/save-stage controls also pass. `flight.txt`. This does not execute the native flight solver or save-file serialization. |
| `python tools/devmods/train_hub/tests/move_smoke.py` | PASS existing movement/reservation controls. `move.txt`; no movement implementation was edited. |
| `LuaRuntime.compile` over `tools/devmods/train_hub/Code/**/*.lua` | PASS, exact file membership and SHA-256 values in `devparse.json`. Also ran the repository `python tools/parsecheck.py`. |
| `flight_smoke.py --clearance-output scratch/build5-motion.json`, then Blender `exit_clearance.py --motion ... --receipt ...` | Regenerated `tests/motion_clearance_receipt.json` from the generator and current flight source; full command, geometry/source hashes and members are in that receipt. Tagged scripted-route mesh measurement only, not native engine clearance. `clearance.txt` preserves the executed generator result. |

## Next attended smoke and inherited QA

Use the standing `train_hub_base` fixture, preserving it; do not reconstruct its trains and
network. The implementation has not preloaded or changed shared TestKit sitting slots.
The sitting worker preloads them under `tools/SMRTK.md` before launch. Build 5's new-line
cases need disposable construction branches on that fixture, with existing stations reused
where possible. Record resource scarcity, fleet, layout, element counts, actual game-time
dispatch/completion timestamps and any relaunches; judge the pop-in with the owner.

1. Hub-served station to a far station with no ordinary drone coverage; compare a longer line.
2. A line from an unreachable station stays waiting, then starts after a connecting line finishes.
3. A middle section covered by an ordinary Drone Hub remains serviceable by its drones; reconcile
   delivered resources with the builder's outstanding payment. Force a stock-out at work end,
   observe the sign and waiting Wasp, replenish and observe completion.
4. Save/reload in flight and while waiting on stock, including a full process restart. Toggle
   Track work off/on mid-session: new launches stop/resume while dispatched work continues.

| Inherited work | Disposition / trigger |
|---|---|
| C1 / D14(g) | Desk correction and paired-hub regression done; simultaneous native launches remain at the next attended run, shared Fix Pack checklist ck217. |
| C2 / D14(h) | Still owed: fresh-process load with active repair notification and ordinary preset control, before selecting a fix. No notification-permanent correction was inferred from the historical warning. |
| C3 | `traffic_smoke.py` retains the previously reported stale arrival-heading failure; no traffic/movement expectations changed here. Next movement owner reconciles it against the settled geometry. Passing `move_smoke.py` does not turn traffic green. |
| C4 | This build's code comments, brief status and group done-condition reconciled. Earlier owner rulings remain historical authority, with spec §10 Drones L5 taking precedence as recorded. |
| C5 | Missing L3 integer-control/editor-round-trip evidence remains unverified; capture those controls when their surfaces next change. No historical result manufactured. |
| C6 | ck217 retains reassign/rocket refusal, far-station return/no balancing, long-run Lost and long hold, dead-grid repair, storage cap, door/work-pose observation and the separate shipping matrix. Those are not claimed by this desk smoke. |
| D14(a–f), cross-map, nanite, split and old-save cases | Existing homes and triggers remain. This build's mocked nanite retry is not a native nanite test or closure of the wider audit. OI-27's map ruling is still open. |

The brief closes only after the owner's smoke is recorded. Ship still requires packed import,
the named Fix Pack release present/absent matrix, module toggles, old/new save controls and
the content-removal disclosure. The build does not settle those gates.

Executed model: Codex / GPT-6 as identified in this transcript; no more specific model variant
was exposed. Scope reviewed: build diff, brief 04, spec §10, D14(g,h), L6 C1–C6 and the named
desk receipts. Unrelated distribution-prototype and metadata work is excluded.

## Pass 2: live topology inspection

Started on `3f46c8d`, game fingerprint command `python tools/doccheck.py --emit-fingerprint`
reports installed 25390750 / archived source 1.1.1.405907. Owner has no saved failed layout and
will recreate it from `train_hub_base` (2026-09-25). Preserve that save. No runtime fix chosen
before this read; the previous smoke proves failure, not its full topology.

Read-only TestKit slots replace sitting `hubset07b` at kit parent `c8b1646`; that binding is
recoverable in git. Slot calls do not change the fixture, launch work, arm callbacks, or change
speed. Select the hub and pause before each snapshot. Native game actions used to recreate the
case (cutting/extending track and the Track work toggle) remain explicit owner actions.

Predictions, written before boot:

1. Scratch: `SMRTK_ACTION action=slot_scratch status=OK`, plus `SMRTK_TAINT_READ` and
   `SMRTK_ELIGIBILITY reason=UNAVAILABLE:sandbox`. Read the actual taint and error count;
   no clean-achievement claim. First-screen witness: "Read taint and eligibility".
2. Slots 1–6: `SMRTK_ACTION action=slot_N status=OK`, phase respectively BASE, CUT, EXTENDED,
   WAITED, REJOINED, FOLLOWUP. Each emits bounded map membership via `SMRTK_DUMP` rows for
   stations/connectors, tracks/endpoints/member lists, elements/hex links/neighbours, repair
   groups and pending jobs, bracketed by numeric MARKs. Handles and counts are live variables.
   Expected witness: "Read topology: BASE (select hub, paused)" on slot 1. Normal runtime is
   immediate while paused; stop if no result within 10 seconds, abort at 30 seconds, or on any
   engine error/unexpected mutation. Wrong selection or running time must return REFUSED.
3. Capture BASE before cutting, CUT after cutting, EXTENDED after placing the new section.
   Keep Track work off during setup; turn it on, run briefly, pause and capture WAITED.
   REJOINED/FOLLOWUP are reserved for explicit subsequent shapes; no silent slot rebinding.
   Flush the full file log. A missing endpoint does not decide the fix: compare the exact
   connector membership, element connections and neighbouring occupied hexes across stages.

Source reads motivating those fields: archived `Buildings/Track.lua:194-200,564-571`
reads endpoint station ownership and resets endpoints from the built-element array;
`Buildings/TrackElement.lua:815-856` expands across neighbouring hexes and can move elements
between track objects; `TrainTransport.lua:57-66` supplies station connectors. Both build and
repair discovery currently depend on the same station-endpoint graph. These are investigation
leads, not a live diagnosis or a claim that all neighbouring track must be serviced.

The four acceptance cases and every inherited QA trigger above remain owed. This inspection
does not run those cases. Unrelated TestKit UI/depot/field-watch/overlay, world actions, grouped
selection, pipe/cable/dome Quick build and Verbose checks in `tools/SMRTK.md`: NOT RUN.

## Pass 2: diagnosis and desk result

Owner correction: the failed-layout save **did** exist and was loaded instead of rebuilding the
fixture. The log's live fingerprint calls it `Autosave Sol 46.savegame.sav`. BASE and EXTENDED
are two paused reads of that same saved layout at game time 32762717, not a before/after cut.
Slot 1 and slot 3 returned `status=OK errors=0`; Scratch/taint/eligibility was not recorded.
The read-only snapshot is archived byte-for-byte as
`docs/archive/train_hub_build5_20260925/topology_snapshot_Mars.exe-20260925-23.08.46-6aad2d75.log`.
Its SHA-256 is `4b2fb494810d497e6ddcd43587d9ac1bf4cd2997c82b6f807a058c5a5a271163`.
The final closed-process log is also archived under its original basename
`Mars.exe-20260925-23.08.46-6aad2d75.log`; `pass2_evidence.json` records its complete hash,
byte count, the receipt/source comparison and both negative TestKit scans with a positive control.

**Worked cause.** The hub's built track 6517 ends at element 6941, beside construction element
7361 on track 7360. Their occupied hexes touch, but neither their stored `connections` arrays
nor TrackBase endpoint-station fields join the objects. The unfinished corridor continues on
another track object, 7504, to station 7042's connector 7044. A separate unfinished line, 7134,
leaves that station toward 7353. Thus 7042 being outside the *built* network is correct in this
snapshot; failing to discover the attached construction corridor is the hub defect. The old
endpoint walk cannot see the seam at all. Merely reading `connections` would also miss it.

Vanilla resolves this shape through occupied neighbouring hexes: archived 1.1.1.405907
`Buildings/TrackElement.lua:815-856` (`process_alien_elements`/`ExpandTrackFromElement`) explains
the placement constraint and absorbs adjacent elements, and `:912-933` invokes that merge on
completion. Pass 2 uses the same hex adjacency for discovery, without changing native objects.
Built/broken elements extend physical service. A second walk finds build groups along attached
unfinished corridors, stopping at their far station; those corridors do not grant remote station
service. Repair groups are discovered from reached members too, so an unfinished member on a
mixed track no longer hides its physically reachable repair. Queued targets refresh from the
live group member after native reassignment, and a real missing hex still blocks dispatch.

**Changes.** Default `MaxDrones=60`; fleet chunks remain 5/15/25. Repairs get the tick's launch
before builds. Builders cannot occupy the unconsumed repair reserve; active repairs may use it.
Native group pricing/completion, payment, flight and persisted field names are unchanged.
Dispatch/completion logging now includes the group handle and game time so separate lines and
reload attempts can be reconciled. This is developer evidence, not a player-facing control.

**Desk evidence.** The executed commands are the four required
`python tools/devmods/train_hub/tests/{buildtrack,repair,flight,move}_smoke.py` invocations.
Each passed; exact commands, parent HEAD `86c7a9e`, source SHA-256s, output and exit code are
`pass2_buildtrack.txt`, `pass2_repair.txt`, `pass2_flight.txt`, `pass2_move.txt` in the archive
directory above. They measure the recorded implementation diff, not a clean parent checkout.
The build smoke replays the owner's archived EXTENDED rows through real Lua: **20 native groups**
on 7360/7504 are discovered, while the same fixture through `86c7a9e`'s graph discovers none.
It reconciles the candidate group identities against all captured member rows on those tracks;
7134 remains excluded until 7042 joins. Synthetic controls cover missing station endpoints,
mixed track, hanging construction, true gaps, reassignment, repair-first launch and the shared
ceiling (25 fleet + 30 builders + 5 repairs). Existing payment/load/toggle controls pass too.
This proves these desk shapes and the captured topology, not native play or all reworked networks.

## Pass 2: attended smoke predictions

Replaces the diagnostic slot meanings above for the next boot. Select the hub and pause before
any slot. Scratch reads taint and sandbox eligibility; slot 1's first-screen label is **Read track
work (select hub, paused)**. Every action returns `SMRTK_ACTION action=slot_N status=OK`; its MARK
and DUMP rows carry live game time, group identities/member counts, actual/target demands, stock,
pending jobs and drones. Wrong selection or running time returns REFUSED. Normal duration is
immediate, stop at 10 seconds without a result and abort at 30 seconds or on error/mutation outside
the named action. These are predictions, not witnessed outcomes.

| Slot | Action and expected fields |
|---|---|
| 1 | Read only: `max_drones=60`, current `candidate_groups`, `candidate_elements`, `active`, `waiting`, `fleet`, toggle and `errors`. |
| 2 | Explicit `SetHubTrackRepair(false)`, then read: `track_work=false`; existing flights may finish, new jobs do not launch. |
| 3 | Explicit `SetHubTrackRepair(true)`, then read: `track_work=true`; dispatch resumes with game time. |
| 4 | Drain only free stock of resources requested by this hub's live builds. `stock_change` carries before/delta/after/target; maintenance, repair and ordinary-drone reservations remain held. Expect a build to wait/sign when its work ends with unmet demand. Deliveries can replenish stock; inspect rather than assume a shortage persisted. |
| 5 | Refill those resources up to available storage/demand, then read. Expect waiting work to resume and native groups to complete. |
| 6 | Full read-only topology snapshot, FOLLOWUP phase. |

Stock mutations use the hub's existing `AddResource` path, archived 1.1.1.405907
`Buildings/MultiResourceCubeVisuals.lua:422-435`; capacity is `:571-589`. Each mutation validates
all requests before writing and logs its actual amount. They intentionally alter the resource
scarcity under test and touch only the selected hub. No detached mutation threads, probes or
load-time arms. No resource provisioning is required for the diagnosis; provision the test line
from the fixture's actual stock and record any refill. Preserve both `train_hub_base` and the
failed-layout save; use a separate named save for mid-job reload.

Run the original four acceptance cases from the beginning: fresh uncovered line plus a longer
one; delayed connection plus the saved cut-and-extend layout; covered middle plus stock-out and
refill; mid-job save/reload/full restart plus toggle off/on. Obtain the owner's judgment of the
chunked appearance and whole-line time. Results follow below; the inherited QA triggers remain
in the original table. Executed model for pass 2: Codex / GPT-6, as exposed in this transcript.

## Pass 2 attended results — in progress

**Case 2 PASS in the saved cut-and-extend layout and its following line.** Owner asked to exercise
the failing shape first; fresh-line regression remains owed. Runtime `3e8176b`, TestKit `357bccc`,
game 405907, named save `track test(2).savegame.sav`, sol 46; both mods loaded. The sitting's live
Fix Pack registry reports version 21 and 41/41 active, whereas the earlier diagnostic boot was
42/42. No present/absent shipping matrix is claimed. Initial hub fleet was 5, cap 60, Track work
off, Metals 70600 actual/target (native units, ON dump `:725`). Ordinary drone coverage was not mapped in this
case. No stock injection was used for this leg.

| Line, matched by native leader handles | Groups / members | First dispatch → last done (game ms) | Elapsed |
|---|---|---|---|
| Reworked corridor, original tracks 7360/7504 | 20 / 96 = 19 × 5 + 1 × 1 | 32766195 → 32864770 | 98575 ms |
| Following line, original track 7134 | 14 / 69 = 13 × 5 + 1 × 4 | 32866195 → 32958533 | 92338 ms |

Every dispatched leader has one matching done line with the same element count. Vanilla moved
members between TrackBase objects during completion; reconciliation uses leader identity, not
the changing track id. The following line was absent from the initial candidates and began only
after the reworked corridor finished. Final paused read (`:1130`) reports no active/waiting jobs,
no candidate groups/elements, `errors=0`, cap 60; stations 7042 and 7353 both read `on_graph=true`
(`:1087`, `:1075`). The first final-read attempt was REFUSED because time was running (`:1041`);
the paused retry is the evidence. Scratch recorded `used=false` and eligibility
`UNAVAILABLE:sandbox`; these remain distinct observations.

**Owner acceptance, 2026-09-25:** asked whether the chunked construction looked acceptable and
the total time felt right, the owner replied **"done and yes"**. Keep `BuildTimePerElement=1000`;
no timing adjustment requested. This accepts this colony's observed lines, not every layout.

The file was flushed while the process was still running. Its byte-preserved checkpoint is
`docs/archive/train_hub_build5_20260925/case2_snapshot_Mars.exe-20260925-23.29.29-6aad2d75.log`.
`pass2_case2.json` carries the exact command/filter, HEAD, hash, complete leader membership and
timing reconciliation. The full closed-process log will be appended after this sitting ends.
Cases 1, 3 and 4, repair-priority/reserve in native play, and inherited QA remain unclaimed.

The closed case-2 log has now been appended under its original basename
`Mars.exe-20260925-23.29.29-6aad2d75.log`: 98706 bytes, SHA-256
`adbec278d35fe80ce8af42ad771022ca0cdf94ede567a2144bc0484c2842e320`.
Measured by `python scratch/build5_case3_attempt1_receipt.py` at HEAD `a2c9ce4` using
the complete source bytes; the earlier checkpoint remains unchanged.

**Case 3 first attempt: completion observed; shortage not held (2026-09-26).**
Boot `Mars.exe-20260925-23.49.03-6aad2d75.log`, same runtime and TestKit as case 2.
Slot 4 removed 70600 Metals at t=32762717 (`:607`); the ON read still showed zero
(`:883`). Construction completed before a material wait was captured. The first
final read was refused because time was running (`:1233`); the paused retry
at t=33072446 shows Metals 42100 actual/target (`:1272`) and no active, waiting or
candidate work, `errors=0` (`:1305`). Stock was replenished during the attempt;
these reads do not identify the delivery source. No slot-5 refill was exercised.
Asked whether the ordinary Drone Hub's drones built the middle, the owner replied
"yes everything appeared normal flushed". This supports the covered-middle
observation; a sustained shortage/refill remains unwitnessed.

**Owner ruling, 2026-09-26: case 3 accepted as PASS; no shortage/refill retry owed.**
"Its going to be near impossible to get shortage refill it has 5 other trains all
constantly balancing the hub. I think we are close enough to call this a pass".
The train count and balancing explanation are the owner's fixture description,
not a measured count. This acceptance waives the remaining attended shortage/refill
step for this sitting. Keep the observed evidence and desk controls distinct from
native verification of a sustained material wait. Cases 1 and 4 remain owed.

Byte checkpoint `case3_attempt1_snapshot_Mars.exe-20260925-23.49.03-6aad2d75.log`
and `pass2_case3_attempt1.json` in the same archive preserve this unsuccessful
shortage attempt. The JSON records HEAD, command/filter, hash and selected raw rows.

**Case 4 pre-shutdown checkpoint, 2026-09-26; outcome pending.** The owner completed
the mid-job save and full exit, and warned that earlier sessions share this process log.
`Mars.exe-20260926-10.33.35-6aad2d75.log` is archived complete, including that noise.
The relevant load starts at line 7035. Its ON read is at t=32762717 (`:7278`);
OFF and READ are at t=32779613 (`:7477`, `:7667`). Both report 3 active jobs and
17 queued, Track work false, fleet 5, cap 60. The READ job rows reconcile to
20 groups / 96 members: active leaders 7420, 7510, 7522 each have 5 members;
the queued leaders have 16 groups of 5 and one of 1. Site 7420 relaunched at
t=32781195 (`:7670`), after this read; the saved state needs a native reload check.

The process-wide error field stays 112 from ON to the final read. Filtering raw
`[LUA ERROR]` rows around the last `Load Game:` boundary finds 112 before it and
none after it. The last preceding error is `:6897`, in SupplyGrid; these earlier
errors are retained without attributing them to this test or investigating them here.
The owner-named `train_hub_build5_midjob.savegame.sav` exists and Mars is no longer
running. This proves the checkpoint, not successful recovery or OFF behavior over time.

`pass2_case4_presave.json` records command/filter, HEAD `cf5194d`, full leader
membership, log/save hashes and the unchanged runtime hash. It also records the
appended closed case-3 log `Mars.exe-20260925-23.49.03-6aad2d75.log`; all earlier
snapshots remain intact. Next: reload in a fresh process, read paused, let existing
jobs finish with Track work OFF, read again, then turn ON and verify queued work.

**Case 4 fresh-process reload and OFF hold PASS, 2026-09-26.** The owner loaded the
named mid-job save in a new Mars process. Paused slot-1 reads at t=32793440 and
t=32988754 show Track work false, fleet 5, cap 60, errors 0. The three active
five-member leaders 7420, 7510 and 7522 each completed during that interval;
all 17 queued groups, 81 members, retained their leader identities and did not
dispatch. No raw Lua errors appear in this process snapshot. This verifies
recovery and OFF behavior. ON continuation is still owed before case 4 passes.
`case4_off_snapshot_Mars.exe-20260926-13.24.29-6aad2d75.log` is a byte-preserved
running-process checkpoint; `pass2_case4_off.json` gives the command/filter, HEAD
`719f174`, hash and reconciled member identities. The full closed log will be
appended after the process exits.
