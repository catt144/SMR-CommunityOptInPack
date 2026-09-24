# Train hub / rail shaft audit — 1.1.1.405907

Executed 2026-09-24; owner request and incident 2026-09-23. **Siding deadlock fixed;
owner confirms trains unstuck (§9). The guarded autosave cycle, new manual save
and fresh-process reload pass in the owner fixture (§§11–12). Wider audit residue remains.**
**Correction after owner testing: `3a0faff` is withdrawn.** Old autosave and
known-good template loads asserted and crashed with that change. The legacy
dwell closure is restored; the owner's template and stalled autosave load again.
Autosaves before the snapshot guard still reported the C-function persist error;
the later closed run and fresh-load prefix do not (§§11–12). Start with §§8–12 before using
the initial audit evidence below.
No game ran during the initial audit. The game was closed when checked; the availability
question received no answer during the source work. The later owner sitting
supplied the stalled state and native fix result. Link 5 resumes with §6; save
compatibility and wider audit gaps remain. This is not certification of either dev mod on 1.1.1.

## 1. Evidence boundary and reproduction

Started at Opt-In `d73d7016eaaf60c0fa54bbdb8f7d4ac1646564d0`, fix pack
`fa96a47`; `git log` and `git pull --ff-only` in both repos, already current.
`git diff --stat 1b32bc8..HEAD -- tools/devmods/` was empty at start. The existing
template icon edit and untracked `train_hub/UI/` were left outside all commits.

Installed Steam build read from `A:/SteamLibrary/steamapps/appmanifest_3215050.acf`:
**25390750**. Source citations below are to the archived trees at
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/{1.1.0.403908,1.1.1.405907}/Src`;
unqualified new lines mean **1.1.1.405907**. Old/new column order is fixed.

The complete executed patchcheck command, HEAD, archive digest, FPK parity,
members and totals are in [patchcheck.txt](train_hub_audit_111_20260923/patchcheck.txt).
It accepted both dev `Code/` directories. Its verdict was SCOPED, not a pass.
The new archive matched installed Lua/Data FPK bytes in that command.

The wider inventory command was:

```powershell
python tools/devmods/train_hub/tests/audit_111.py --output docs/agent/reports/train_hub_audit_111_20260923/inventory.json
```

[inventory.json](train_hub_audit_111_20260923/inventory.json) records input hashes,
calls, member and assignment names, handlers, citations, candidate declarations,
body diffs and logs. Output is exclusive-create; reproduce to a NEW path.
At `3a0faff` plus the recorded comment changes, its recursive filter selected
**11 Lua files** from both dev mods, excluding `SourceData`; the members are its
`files` array. **2698 declaration candidates = 2647 identical + 46 body-changed +
5 added**, reconciled against `declarations` and `candidate_status_counts` by
the script. These are lexical candidates, not 2698 reviewed dependencies: names
such as `Init` match unrelated classes. No semantic coverage count is claimed.

Patchcheck limitations, checked in `tools/patchcheck.py` at fix-pack `fa96a47`:
`module_files` scans only the immediate directory, so the generated building
companion and Data template are omitted. `harvest` pins declarations/captures and
parses citations; `analyse` checks called names for vanished signatures, not all
callee body changes. String commands, fields and actual receiver classes are not
resolved. Its D3 list comes from the shipping save-exposure inventory; **D3=0
does not mean the dev mods have no saved threads**. In particular it missed the
changed `Train:UnloadAll` behind the floor wrapper and the waiter permanent issue.

## 2. Save error: ours, not an attribution to the last vanilla thread

The old global `WaitWakeup` wrapper called its captured native function.
`CommonLua/Core/cthreads.lua:466-478` gathers `cthread.WaitWakeup` from the CURRENT
global. The wrapper therefore took the native waiter's permanent key, while native
C frames remained suspended in it. The whole `cthreads.lua` file is byte-identical
between the archived builds; this is not a changed 1.1.1 permanent API.

`DroneControl:UpdateDeficits` (`Lua/Buildings/DroneControl.lua:129-141`) and the
`MarkFlight` repeat (`Lua/Flight.lua:835-840`) both call that waiter. Which saved
object graph reaches it first explains the different stack tails; a stack through
`FlightSystem.marked_objects` does not make the flight driver its cause. The
21:19 and 23:38 stacks end in `deficit_thread`. The earlier shaft report's
MarkFlight attribution is insufficient as ownership evidence. Both are victims
of the same displaced mapping. The old hook was introduced in `99a8cd9`.

**Initial repair `3a0faff`, later withdrawn (§8):** preserve global `WaitWakeup`; shorten only the hub's
`Train:LoadTrain` / `Train:UnloadTrain` waits. The command copies are pinned to
archived 1.1.1, with ownership guards delegating foreign stations to their originals.
`dwell_smoke.py` executes the archived permanent collector with a native C waiter;
it rejects the old file and accepts the new one. Its copy gate checks every other
body byte against the archive. `move_smoke.py` uses 1.1.1 and checks elapsed work,
the minimum wait, tuning and foreign controls. Save policy is layer 2 for the
copied blocking commands; no persisted key changed. Native save/reload is owed.
The fix also removes the map query responsible for brief 02's startup assert;
brief 02's native absence check and separate inheritance issue remain open.

This does not repair already damaged saves or prove that every persist error has
gone. The logged C address is not a symbolic function identity. The source and
regression identify a real defect; the fresh-process native save control in §6
must confirm the error attribution in the actual game.

## 3. Engine audit table

`Holds` below means the stated Lua contract; `moved` means a line moved with an
identical body. Neither is native evidence. Other fields and ambiguous receiver
matches remain inventoried but unadjudicated; see §7.

| surface | old → new archived line | verdict and consequence |
|---|---|---|
| `Train.LoadTrain` / `UnloadTrain` | `Lua/Units/Train.lua:230 → 230`, `424 → 424` | Holds. Native waits still follow transfer/boarding. The new copies change the timeout alone. |
| Floor wrap, `Train.TransferCargo` | `Train.lua:836 → 862` | Moved, body holds. The wrapper still delegates; requests retain actual/target and claim semantics. |
| `Train.UnloadAll` | `Train.lua:779 → 787` | **Changed.** Keeps cargo assignments that cannot fit or whose resource is disabled, and unloads whole assigned entries. The floor's early call remains followed by vanilla's call; no yield occurs between them. Its old comment claiming an empty assignment list was false and is corrected. A native cargo/full-storage control is owed. |
| Train routing, station through-connector choice | `Lua/TrainTransport.lua:302 → 302`; `Station.lua:931 → 931` | Holds. The entire TrainTransport and TrackTunnel files are byte-identical. Route overwrite / linear-chain constraint is not new in 1.1.1; the shaft report's branch hypothesis still needs `Routes()`. |
| Hub movement, reservations, crossing lock | `Station.lua:1097 → 1097`, `1184 → 1184`; dev `HubCrossingTrain`, `HubAcquireCrossing` | Arrival/departure bodies hold. Valid interrupted trains retain the saved crossing lock by existing policy; a dead command is not automatically clearance. No lock reset was added. Read the lock/thread in the stalled save. |
| `TrackBase.ProcessAllElements` | `Track.lua:466` in both | **Changed.** Repair sites with a valid `broken` original are excluded from duplicate processing. Physical originals remain the graph edges. |
| Track split/removal and repair-site ownership | `TrackElement.lua:483`, `513`, `593` old; new `483`, `515`, `594` | **Changed.** Repair sites stay in `elements_under_construction`; splits retarget each repair site's `track_obj` and rebuild `repair_cgs`. Pending jobs cache `job.track`; split-after-discovery is an untested stale-reference risk, not established as tonight's cause. |
| Breaking track / meteor emission | `Track.lua:623 → 628`; `Meteors.lua:713` new | Break body moved, holds. `BreakTracks` appends the repair group before `TrackBroken(track,true)`; the hub's immediate discovery sees it. A toolkit FIRE record only proves dispatch of a meteor, not a hit or a break. |
| Group and element completion | `ConstructionSite.lua:2659 → 2671`; `TrackElement.lua:841 → 860` | Moved, bodies hold. Group leader completes members. New `915-933` clears groups only when all unfinished elements are gone, as before. Corrected the smoke's eager-group-removal mock; two breaks on one track now retain the dead first group until the second completes. Hub logic passes that case. |
| Completion early exit | `ConstructionSite.lua:2673-2675` new | Holds, **unresolved interaction**: a queued nanite completion can make `Complete()` return early. Hub pays before the call and assumes success. Test this conditional path before claiming all completions are safe; no runtime evidence of nanites in tonight's case. |
| Physical graph / reciprocal tunnels | dev `HubTrackGraph`; `TrackTunnel.lua:40` both | Same-map tunnel contract holds. **Design gap:** graph traversal accepts a cross-map `linked_obj`, while the Wasp leg targets XY on its own map. Far stations can be registered across maps. OI-27 asks the map policy; no silent map restriction was built. |
| Remote station request filter | `DroneControl.lua:742,754` new; `Lua/_TaskRequest.lua:209-210` | Holds at the per-request seam. Only the two maintenance requests pass out of range; in-radius requests delegate. Controller membership is not proof of physical service or a successful repair. |
| Maintenance recovery | `RequiresMaintenance.lua:101` both | **Changed.** When demand is already satisfied, BuildingUpdate starts the work phase. Helpful to remote station maintenance; does not supply missing material or prove a Wasp can reach it. |
| `FlyingDrone.CanBeControlled` | `FlyingDrone.lua:141 → 144` | Moved, body holds and chains Drone. Hub's wrap captures the declaring Wasp method; foreigners reach it. |
| `Drone.CanBeControlled` / DroneBase | `Drone.lua:2171 → 2207`; `DroneBase.lua:156 → 160` | **Changed.** Uses operational state and uninterruptible-code guard. Preserved through the chained Wasp wrap. |
| `Drone.Done`, carried resource cleanup | `Drone.lua:122` both | **Changed.** Records dropped-resource state before delayed catch-all drop. Hub explicitly drops before deletion, so destruction/cube survival still needs the native L5 control. |
| Fleet/orphan/finalize/load | `DroneControl.lua:292`, `315` both; `1088 → 1092` load word | Orphan gathering and Finalize bodies hold; load-word body moved. `cafcaea` deliberately overrides gathering with no adoption; scaling remains source/mock evidence. |
| Engine flight / Wasp height | `Lua/Flight.lua:1182` new; `FlyingDrone.lua` flight class data | **Changed underneath us.** New obstacle grid, height ceilings, surface marking and landing filters; stock FlightGoto retains its interface but removes the non-debug trajectory-error assert. Therefore a quiet log cannot prove arrival. The class-static Wasp ride and OI-26 remain the design; native clearance remains owed. |
| `FlyingDrone.Land` | `181 → 184` | **Changed.** Uses XYZ and terrain-height APIs; scripted ends retain their own movement and engine legs use stock commands. Prior source citations do not prove the engine flew our intended path. |
| Stock command/hold machinery | `CommonLua/Classes/CommandObject.lua:341,346,552,170` | Holds for SetCommand, DoSetCommand, QueueCommand, InterruptWait. Literal FlightGoto/WaitUninterruptable dispatch is outside patchcheck's call-name resolution; the flight smoke's solver spy is still only a source-contract check. |
| Save/load driver hooks | dev `30_TrainHubDrones.lua:1172-1187`; `CommonLua/Savegame.lua:1041,1059` new | Hooks remain present. Driver and scripted visuals are torn down; stock flights/holds may survive. Existing autosave-yield and alternate-save-path limits remain; no new native save proof. |
| Station train construction | `Station.lua:462,503,520,541` both | Holds: demand requests, SelfService, resource/working-state gate, timed construction. No drone-count gate in these bodies. DESIGN §6 remains a request-state observation, not permission to add an acknowledgement launch speculatively. |
| Power, Building update and class combination | `Building.lua:810` new; `SupplyGrid.lua`; dev combined parents | Update still runs for valid buildings regardless of working state. New `Building:OnModifiableValueChanged` at 736 updates parent-dome stats; hub's callback only updates its production. Parent callback combination still applies. Startup diamond in brief 02 remains a separate open native issue. |
| Template / generated companion / panel | dev Data template, Code/BuildingTemplate companion; runtime `customSMROptInTrainHub6Base` | Included in recursive inventory, omitted by patchcheck's shallow scan. Custom XTemplate is created in `20_TrainHub.lua`, not a separate file. Its section/toggle creation passes repair smoke. Entity, object_class, label and persist-baseclass names were not changed. Existing peer icon differs from generated companion and is outside this audit. |
| Visual helpers / night message | `Lua/NightLightObjects.lua:250` both | LightmodelChange parameters and night transition contract hold; look smoke passes mocked lifecycle. Native art, GPU cost, dynamic collision/clearance and Mod Editor round-trip are outside this result. |
| Shaft guards / map transfer | `Tunnel.lua:193 → 193`, `160 → 160`; `TrackTunnel.lua:40` both | AddPFTunnel **changed** to reject destroyed ends; our same-map branch chains that body. MergeGrids and TrainTraverse hold. Cross-map transfer still uses the prototype's destructor and map transfer. Earlier measured hops remain that fixture's evidence, not evidence about tonight's stalled save. |
| EntitySpec load error | `CommonLua/Editor/ArtSpecEditor.lua:565-612` both | Body holds. Calls unavailable runtime `EntitySpecPathToEntity` at 573; definition is in `CommonLua/Libs/DevToolsPublic/SceneImport.lua:5905`. Vanilla editor/mod-load path, reached by the hub's imported EntitySpec source data. Not a train command failure; art/import fix remains outside this audit. |

## 4. Logs and the silent gap

Logs are under `%APPDATA%/Surviving Mars Relaunched/logs/`; all names below end
`-6aad2d75.log`. Inventory `logs` preserves the warning/error matches and exact
lines, hashes, FIREs, repair status and shaft prints. Filter is the script's
`warning` regex; FIREs count only `[mod] [SMRTK]` lines so the duplicated plain
console echo is not counted twice.

| log | error / warning attribution | missing observation |
|---|---|---|
| `Mars.exe-20260923-21.19.58` | ArtSpec nil at 201: vanilla editor path triggered by imported hub data. Persist error 806: D14(a), tail is a DroneHub deficit thread. Braze DNS/init failures 227-237: vanilla telemetry. PdxSDK ModAlreadyInstalled 239: platform installer. Mod-version notices 259-260,323-324,422-423: expected older-save/current-mod mismatch, not proof of compatibility. | No completed-repair/train-resumption or route diagnosis is established by this log. |
| `Mars.exe-20260923-22.13.30` | ArtSpec nil 166; Braze failures 194-204. No persist error in this closed log, **but it is not a successful-save control**. | No FIRE events, only load-side hub prints. |
| `Mars.exe-20260923-23.38.53` | ArtSpec nil 196; Braze failures 224-235; version notices 255-256 and later 1322-1323. Persist error 566: D14(a), tail is a rocket deficit thread. SMRTK SAVE_A subsequently reports OK: toolkit operation success did not certify serializer cleanliness; no TestKit code defect is established. | No train command/route/crossing-lock snapshot at the stall, and no post-deadline repair snapshot. |

The script counted each evening log's hub-positive side as **221 / 2 / 290**
lines respectively; its complete matching event arrays have **15 / 7 / 12**
members. Its daily glob records **7 affected logs**, with member lines:
10:45 `[513]`, 12:05 `[1007,1485]`, 16:09 `[578]`, 17:27 `[373]`,
17:45 `[703,753]`, 21:19 `[806]`, 23:38 `[566]` — **9 errors total**.
The 2026-09-23 old-hash log in that same glob has none. This does not prove
absence across every historical 1.1.0 log or isolate a patch-caused regression.

In 23:38, the pre-save FIRE ids are **31,39,43,46,49** (5 members); after the
reload they are **71,85** (2), reconciling the log's **7** unique FIRE records.
The brief omitted the later id 85. A click position is not evidence of a track
break. At line 724 the hub reports no jobs. Lines 745-746 and 922-923 report one
job for id 71's interval, still BEFORE its deadline, with FlightGoto active.
No later status proves whether it completed. The owner report establishes the
stall, not which track or command blocked it.

The shaft was enabled, but lines 261 and 676 say the underground was locked on
the relevant loads. Later at 1328 another save enables the underground; that is
after the repair observations. This makes the earlier cross-map branch story a
poor default explanation here. Only Status/Routes/Sweep on the actual stalled
save can exclude it. No routing mutation or `Unlink()` was run by this audit.

## 5. Tests, design obligations and limits

Initial pre-rollback commands from this repo: `python tools/devmods/train_hub/tests/` followed by
`dwell_smoke.py`, `move_smoke.py`, `repair_smoke.py`, `flight_smoke.py`,
`look_smoke.py` — **PASS** for their stated mocked/source scopes. `traffic_smoke.py`
— **FAIL**, `-10800 != 0` at its old geometry assertion, already recorded by brief
02 before the audit. It was not repaired by weakening that expectation. Both dev
Code directories passed `python tools/parsecheck.py --dir <directory>`.
`python tools/doccheck.py` — GREEN before the fix commit.

The old hub was obtained with `git show d73d701:tools/devmods/train_hub/Code/20_TrainHub.lua`;
`dwell_smoke.py --source <that file>` failed at the missing native permanent.
The fixed command passes. The corrected repair fixture also rejects its old
eager-group-removal body at the partial-repair assertion. Vanilla trailing
whitespace in the command copies is intentional under the byte-copy policy.
Initial move smoke failed because its fixture lacked IsKindOf; that stub was
added, not a production workaround. The flight source was unchanged, so its
passing receipt check stands and no clearance receipt was re-pinned.

DESIGN/L4 obligations remain reachable as tests on 1.1.1, with these qualifications:

- Far-break discovery, cost claims, shortage, toggle and switch, no-power and
  malfunction cases: source paths and mock controls hold. First measure a real
  completed repair AND both unfinished-element and repair-group counts AND train
  motion. Multiple breaks on one track must finish before the line clears.
- Mid-trip save/load and autosave: repeat on a fresh process after D14(a). Keep
  the old failed save as evidence. Observe outbound and return legs separately;
  a completed job no longer supplies adoption metadata for a returning visual.
- Remote station maintenance and no resource balancing: filter is scoped in
  source, but request membership alone is insufficient. Watch arrival/work and
  idle go-home behavior. Cross-map ownership is OI-27, not cleared.
- Fleet load tiers, capacity/waiting jobs, a destroyed drone, no charging,
  greyed reassignment, dead hub and carried-cube drop: still owed in the game.
  A mocked ceiling test is not the requested real maximum-load case.
- Train construction: inspect material requests and working state on hub and
  far station. The conditional acknowledgement-launch ruling remains conditional.
- OI-26's real train-under-drone look, fleet pit-launch question, settled-lane
  clearance caveat and palette response remain with link 5. The engine leg's
  changed obstacle behavior needs eyes, including actual arrival on quiet logs.
- `cafcaea`, `5ec8048`, `1b32bc8` remain as recorded: no orphan adoption, notice
  has no ETA, and engine handoff defaults outside. No owner ruling was reversed.
  Both shipping configurations and toggle directions remain the eventual ship gate.

## 6. Resume after the native siding fix

The owner completed the template and autosave rollback controls and the train
departure test. Their evidence is in §§8–9; do not ask for those same reads again.
The snapshot guard now passes the native autosave cycle, manual save and
fresh-process reload controls (§§11–12); ck215 is consumed. Keep the protected
inputs and the stated compatibility bounds. A successful toolkit SAVE line alone
is not a clean serializer result.

L5 still owes a measured repair to completion, including multiple breaks on a
track, train motion afterwards, and its remaining DESIGN scenarios (§5). Read
HubRepairStatus before and after the deadline; measure the Wasp's actual arrival.
If another stall occurs, use §9's connector/lock reads and Sweep first. Routes and
Status remain available if route membership or map ownership becomes suspect;
those extra probes were unnecessary for the measured siding deadlock. Do not
clear locks or unlink tracks to diagnose an unexplained stall.

## 7. Remaining work / close-out inventory

| finding or request | home / next action | disposition |
|---|---|---|
| Save permanent defect | D14(a), §§8–12 | `3a0faff` withdrawn; guard `102f5f0` passes the observed native autosave/manual-save/fresh-process controls; historical fixture and ship-matrix bounds remain |
| Stall classification | D14(f), §9; link 5 upstream notes | Siding guard corrected; owner confirms trains unstuck; visual clearance not explicitly confirmed |
| Exhaustive engine-field/class/message audit | inventory file/member/assignment/citation arrays; manually resolve remaining candidates and literal commands on the relevant archive | **Incomplete**. The table above names adjudicated groups; inventory is not a substitute for reviewing every receiver and field. Citation-only and lower-priority semantic rows remain. |
| Cross-map drone ownership | D14(b), this mod OI-27 | Owner design ruling; no map guard built |
| Nanite early completion / pending job after a track split | D14(c,d); reproduce conditional paths before fixes | Source risks, not tonight's measured cause |
| ArtSpec load error | D14(e), §3-4; art/import follow-up | Attributed, unresolved; do not ship a global stub for editor APIs |
| Over-eager repair mock | corrected repair_smoke partial/last-break controls | Fixed fixture; no proof of native track repair |
| Traffic smoke | existing stale geometry failure | Open; movement smoke is narrower and is not a replacement clearance proof |
| Full log scope | warning regex and all matched events in inventory | Attributed matches only; silent progress gaps explicitly unresolved |
| Earlier read errors | nonexistent local patchcheck/L4-report paths, PowerShell wildcard rg, one wrong appmanifest id, one wrong CommandObject path, exact-selector miss | Resolved using donor tool, drones_chain report, directory-glob searches, actual appmanifest and Classes path; no conclusions from failed commands |
| Workflow tool | no todo tool exposed | Work list stated in commentary before edits; no subagents |
| Checklist allocation | ck208 was already used in older records; full explicit live/archive search found ids through ck211 | New ask uses ck212; no old ask was overwritten |
| Doccheck before staging lifecycle deletion / cross-repo Home | unstaged deleted brief was still enumerated by rule placement; donor checklist rejected an absolute Home and a long line | Stage the deletion; donor pull-only handoff holds the external report link and ck212 points there |

`smr-session-close` applied. The report consumes the one-off audit brief and its
map row, but does not retire the pending L5 work. No STATE or archived text was
edited. Executed model from this transcript: **GPT-6 (Codex)**; no more specific
model/effort identifier was exposed. No native game, upload or publication occurred.

## 8. Owner load crashes and rollback, 2026-09-24

**Observed:** the owner attempted the stalled autosave, received assertions in
`luaSPersist.cpp(1272)`, chose Ignore All, and crashed to desktop. The owner then
reported the same failure in older known-good templates. The screenshots and
native logs supersede the earlier source-only confidence in `3a0faff`.

The preserved logs are in
[`docs/archive/train_hub_load_crash_20260924/`](../../archive/train_hub_load_crash_20260924/).
Read with `rg -n 'Load Game:|last saved|ASSERT|Game Loaded|Access violation|Details:'`
over those named files [RAN 2026-09-24, HEAD `1b6f28e`]:

| log suffix (all `Mars.exe-20260924-`, build `6aad2d75`, game 1.1.1.405907) | last saved on | assertion / crash lines |
|---|---|---|
| `10.28.59-6aad2d75.log` | 405907 | 222, 226 / 305-306 |
| `10.33.26-6aad2d75.log` | 403908 | 221 / 275-276 |
| `10.36.16-6aad2d75.log` | 403908 | 225 / 305-306 |

Each reaches a `Game Loaded` line after an assertion, then the Lua thread has
an access violation reading `00000001BA5175D3`. That line is not a successful
load verdict. The first two screenshots test `ci->func`'s type; the third tests
its GC object's type. Ignoring the assertions did not restore a usable colony.

A later log, `10.42.33-6aad2d75.log`, is also preserved. It asserts at 113 and
crashes at 158-159, but lines 119-122 explicitly say the opt-in pack, TestKit,
fix pack and hub are present **but not loaded**. This launch followed the rollback
write at 10:41:01, but did not execute it. It is not the rollback control. The
owner was told to re-enable the original mod set and restart before that check.

**Source-supported regression hypothesis:** the old hook occupied the engine's
`cthread.WaitWakeup` permanent with a Lua closure. `3a0faff` made the same label
resolve to a C function. The existing test exercised the new collector at save
and load; it never restored a save made with the old mapping. A Lupa probe at
`1b6f28e` confirms `debug.getinfo(...).what` changes from `Lua` to `C` across
those implementations. This is a type-mapping demonstration, not native
deserialization. The native C++ serializer source was unavailable; the precise
failing saved frame remains unproved. The later rollback restores loading below.

**Containment:** restored the dwell helper and wrapper byte-for-byte from
`d73d701`, removed the copied train commands, and restored the corresponding
movement smoke while retaining its 1.1.1 source pin. The restored section from
`local function hub_dwell_train(` to `local hub_work_radius` has SHA256
`2d64e75720a577aaa56d53fd7e2dc2812fcaa520513d77908c5537225c95dd23`.
An equality assertion against `git show d73d701:tools/devmods/train_hub/Code/20_TrainHub.lua`
passed [RAN 2026-09-24, HEAD `1b6f28e` plus rollback diff]. This is a rollback,
not a new serialization fix. No save bytes or installed game files were changed.

Backups outside the game's autosave rotation are in
`scratch/train_hub_load_20260924/saves/`, with full-file hash equality recorded in
`scratch/train_hub_load_20260924/backup_receipt.json`. Members: `Autosave Sol 31(3)`,
`train_hub_base`, `train_hub_base_agent`, `tunnel test`, and `SMRTK_A` (original
extensions retained). Their plaintext metadata records hub versions 49, 15, 9,
27, and 49 respectively. The first 200000 bytes were read for metadata; compressed
persist bodies were **not decoded**. An initial FLPK extraction assumption failed
on the BPUL header, before changing any input. The original source defect still
does not establish that every old save is damaged.

Checks [RAN 2026-09-24, HEAD `1b6f28e` plus rollback diff]:
`python tools/parsecheck.py --dir tools/devmods/train_hub/Code` and
`python tools/devmods/train_hub/tests/move_smoke.py` pass.
`python tools/devmods/train_hub/tests/dwell_smoke.py` deliberately remains RED
at the missing native permanent assertion: the original defect is still present.
Do not reinterpret that failure as a clean save result or weaken the test.

**Rollback control passed:** the owner re-enabled mods, loaded, and restarted.
Preserved `10.45.34-6aad2d75.log` shows all template-required mods loaded at 183,
saved hub version 15 at 224, `Game Loaded` at 246, the map ready at 259, a track
selection at 261, and normal exit code 0 at 265. At HEAD `2035dbb`,
`rg -n 'ASSERT|\[ CRASH \]|Access violation|Persist error:' <that-log>` returned
1; the verification throws on any other result. The loaded-mod list, `Game Loaded`,
map-ready and exit-code markers each occurred once (counted and asserted in the
same command). This supports rollback of the template-load regression, not save
recovery, a new-save pass, or train movement. The existing ArtSpec startup error
is still present. Rail Shaft was not loaded and is not listed in this template's
saved mod set; the autosave requires it.

**Autosave rollback control passed:** the owner answered "Loaded without assertions"
for `Autosave Sol 31(3)` with Train Hub and Rail Shaft enabled. The preserved,
closed `10.49.56-6aad2d75.log` has `Game Loaded` at 270, map-ready at 283 and
normal exit at 431. A Python assertion and
`rg -n 'ASSERT|\[ CRASH \]|Access violation' <that-log>` found no such markers
(rg exit 1 required, HEAD `2035dbb`). The C-function persist error is still at
286, this time through the hub's restrictor thread. This is successful loading,
not repaired saving. §9 records the subsequent stall diagnosis and departure fix.
Agent work remains: diagnose the old/new permanent transition and test a migration
before reintroducing the save repair. That repair
must distinguish legacy and newly written saves, and cover old→new→save→reload,
ordinary native saves and suspended waits. A version-only guess is insufficient:
`3a0faff` retained dev version 49, and the wrapper was introduced during version 9.
L5's remaining smoke resumes through §6. No clean new-save verification has been observed.

Executed model: GPT-6 (Codex), as exposed by the transcript; no subagents.

## 9. Native siding deadlock and correction, 2026-09-24

Owner: all but one line remained stuck after rollback. The closed archived
`Mars.exe-20260924-10.49.56-6aad2d75.log` records these read-only console commands
(Sweep refreshes its diagnostic cache):

```lua
*r SMRRailShaft.Sweep(); FlushLogFile()
*r local h=SelectedObj; print("[TrainAudit] hub",h.handle,"crossing",h.SMROptIn_hub_crossing); for k,t in pairs(h.track_busy or empty_table) do print("[TrainAudit] slot",k,"train",t.handle,"cmd",t.command,"thread",IsValidThread(t.command_thread),"station",t.current_station and t.current_station.handle,"arrival",t.station_arrival_track,"parked",t.at_station) end; FlushLogFile()
*r local h=SelectedObj; print("[TrainAudit] hub",h.handle,"old_crossers",table.count(h.trains_traversing or empty_table)); h:ForEachConnectorElement(function(el,i) local tr=el.track_obj; print("[TrainAudit] track",tr.handle,"spot",i,"can_run",tr:CanTrainsRun(),"repairs",#tr.repair_cgs,"unfinished",#tr.elements_under_construction) end); FlushLogFile()
```

An intervening probe iterated `h.tracks`, a mock-only field, and printed nothing.
That was an instrumentation mistake, not evidence of absent tracks; the connector
probe replaced it. Archived 1.1.1.405907 `Lua/TrainTransport.lua:57` visits actual
connectors, including tracks whose destination is unavailable. Its connected-track
iterator at 68 would filter those out. No trains, routes, locks or repairs were reset.

Measurement at HEAD `2035dbb`, before the guard diff: Python `re.findall(..., re.M)`
on the closed log used `^\[RailShaftDev\]   \[\d+\].*$`,
`^\[TrainAudit\] slot .*$` and `^\[TrainAudit\] track .*$`, asserted totals
**8 / 4 / 6**, and asserted every row's positive state. Reproduce the member read
with `rg -n '^\[RailShaftDev\]   \[|^\[TrainAudit\]' <that-log>`.
Sweep members at 323–330: train handles 2000001652, 2000001837, 2000001838,
2000001839, 2000001840, 2000001841, 2000001842, 2000001843. All had
`route_ok true`; 1652 was LoadTrain, the remaining seven were GotoStation.
Hub 6430's crossing was false (341), legacy crossers zero (386). Its parked
members (342–345), joined to their assigned outgoing tracks, were:

| parked slot | train handle | requested track | exit slot | exit siding held by |
|---|---|---|---|---|
| 1 | 2000001841 | 6410 | 2 | 2000001837 |
| 2 | 2000001837 | 6402 | 1 | 2000001841 |
| 3 | 2000001843 | 6413 | 4 | 2000001839 |
| 4 | 2000001839 | 6406 | 3 | 2000001843 |

Each had a live GotoStation thread, `current_station=6430`, the matching
`station_arrival_track`, and `at_station=true`. Track members at 388–393, in
connector order 1–6: **6402, 6410, 6406, 6413, 6378, 6417**. Every one reported
CanTrainsRun true, zero repair groups, zero unfinished elements. Archived
1.1.1.405907 `Lua/Buildings/Track.lua:371` gates on those two lists. Thus the
observed pairs were waiting on each other's siding reservation, with no occupied
crossing or unfinished track repair to clear. Slots 5/6 had no such parked pair,
consistent with the owner's working line; the screenshot alone could not prove it.

The exit-contact guard in `2606719` predates the off-line sidings in `99a8cd9`
(`git merge-base --is-ancestor 2606719 99a8cd9` passed). The earlier build/spec
records already noted mutually blocked departures as a limitation. The later
owner ruling, spec §9 at the six-loading-sidings passage, explicitly permits
through movement beside a parked loading train. The implementation retained
the earlier whole-exit reservation guard, contradicting that later design.

**Correction:** HubExitClear permits an exit with a train fully parked on that
exit's siding: this hub is its current station, at_station is true, arrival slot
matches and it does not own the crossing. Arrival publishes that state only after
siding motion. Incoming, moving and unknown/legacy reservations still block.
The existing crossing lock and vanilla IsTrackFreeFor check continue to govern
actual movement; no queue priorities, routes or persisted fields were added.
The legacy dwell closure remains byte-identical to the rollback.

**Controls run** on `2035dbb` plus the guard/test diff:
`python tools/devmods/train_hub/tests/move_smoke.py` PASS and
`python tools/parsecheck.py --dir tools/devmods/train_hub/Code` PASS.
The same movement smoke with `--source scratch/train_hub_before_siding_guard.lua`
(exact `git show 2035dbb:tools/devmods/train_hub/Code/20_TrainHub.lua`) FAILS at
"opposite siding reservation deadlocks first departure". Positive controls allow
both opposite departures and a through train beside the parked train, retaining
its position/reservation; negative controls retain moving/incoming/unknown and
crossing-owner exclusions. Both departures release their reservations and lock.
The old contact fixtures needed explicit absent arrival metadata: `atstop` had
inherited a completed-siding slot, so its original expectation described the old
inline geometry. No production workaround was added for that fixture failure.

**Native result:** asked the owner to fully restart, reload the same autosave and
unpause without overwriting it. Owner: **"They are now unstuck."** This is the
train resumption result for that colony; physical contact/clearance was not
explicitly answered. Partial post-fix log
`Mars.exe-20260924-11.01.15-6aad2d75.partial-after-guard.log` preserves loading and
the still-present save error (284, 299), now through VoiceQueuePlay. Its partial
status precludes a whole-process absence claim. The error is independent of the
departure guard, and the owner was told that new autosaves remain unreliable.

Archive bytes were captured with exclusive-create and readback equality. SHA256:
closed pre-guard `10.49.56`: `9b9e497846e83d293227ef20c4427f4fc951621dfa73f2fe76abe6f5ef2a36e1`;
partial post-guard `11.01.15`: `195f7ae224897d5cb1c7e14adfd7f6f7c861c17ada512a2d6b2560d2e6aee74d`.
The archive's local `*.log -text -diff` preserves the native bytes on commit.

Completed owner asks ck213 (template rollback), ck214 (autosave rollback), and
the subsequent departure test are recorded here and removed from the donor list.
No new owner ask substitutes for the agent's pending save-compatibility work.
L5 retains the broader drone smoke; D14 retains save, cross-map, conditional
nanite/split and import findings. Executed model: GPT-6 (Codex), no subagents.

## 10. Owner's save-boundary proposal and snapshot-guard candidate

Owner: "Can't we guard our changes from saves by unloading them right at the
on save point, and then applying them at the onload point ?" The narrower
implementation applies that idea to the global wait-function replacement;
it does not unload content, strip saved state or erase suspended command frames.
Those frames are why simply removing the wrapper previously broke old loads.

On archived **1.1.1.405907**, `CommonLua/Savegame.lua:1041` sends SaveGameStart,
then yields on the route to the snapshot; `_Wrap:337`, `_InternalSave:346` and
`SaveMetadata:784` retain that gap. EF-070's earlier-build warning therefore still
applies to a general teardown scheme. InMemSaveGame (1117) and bug-report PStr
(1141) skip the Start/Done messages. The checked Lua save paths reach PersistGame
(853), which calls EngineSaveGame (860). Commands:
`rg -n -F 'PersistGame(' <1.1.1-archive>/Src` and
`rg -n -F 'EngineSaveGame(' <1.1.1-archive>/Src` [RAN at HEAD `f556ee8`].
This scopes the check to Lua source callers, not unknown native entry points.

**Candidate built after `f556ee8`:** chain PersistGame with a native-waiter
scope and restore the runtime wrapper after success, a returned error, or a
thrown error. Preserve returned values and rethrow after cleanup. If another
replacement has changed the expected waiter, return a save error before the
snapshot rather than writing a save with the wrong marker. The guarded function
still performs the engine's CanSaveGame, snapshot and persist-error handling.

GatherGameMetadata marks `SMROptIn_hub_native_waiter=1` only when the guard is
installed. SavegameMetadata.lua:50–82 supplies metadata for normal and in-memory
saves; uiXBugReportDlg.lua:390 gathers the bug-report metadata through it too.
PreLoadGame selects the captured native waiter for marked saves or saves with no
hub mod record; unmarked existing hub saves select the exact legacy Lua wrapper.
UnpersistEnd restores runtime behavior even when EngineLoadGame returns an error.
This runs before/after the engine at Savegame.lua:798–815. The new marker is in
FIX_POLICY's persisted-name inventory. No original permanent label is renamed.

**Compatibility boundary:** the unmarked version-15 template and version-49
autosave retain their successful rollback mapping. The older pre-wrapper hub
version-9 fixture remains ambiguous: the wrapper appeared during that same
version, so a version-only choice is unsafe. This candidate preserves the
rollback behavior for such unmarked hub saves; it does not claim to repair all
historical fixtures or to recover frames already lost by an earlier bad save.

**Local controls** [RAN at `f556ee8` plus candidate diff]: updated
`python tools/devmods/train_hub/tests/dwell_smoke.py` runs the actual archived
PersistGame and permanent collector with a mocked engine snapshot. It checks
native mapping during the snapshot, legacy/new/native load selection, a suspended
native waiter, success/error cleanup, and a conflicting global waiter. It also
asserts that the legacy wrapper's body is byte-identical to `d73d701`. This is
not C++ serialization. The earlier test's global-always-native/command-copy
requirements described the withdrawn repair and were replaced with the new
snapshot-boundary contract; a passing collector alone still cannot prove reload.

Failing controls use `dwell_smoke.py --source <file>`: the `f556ee8` body lacks
the guard and fails; changing only the guard's native assignment to retain the
wrapper fails at "native waiter missing at actual snapshot"; forcing all loads
to native fails the legacy mapping equality. Reproduction files are
`scratch/train_hub_before_save_guard.lua`, `train_hub_guard_no_native_snapshot.lua`,
and `train_hub_guard_wrong_legacy_mapping.lua`. The initial standalone candidate
in `scratch/train_hub_save_guard.lua` is inert, not an additional loaded mod.
Movement smoke and dev Lua parse pass. Its shared mock needed the normal OnMsg
table because handlers now occur earlier in the source; its first failure was
missing mock setup, not a runtime game failure. No clearance claim was added.

**Native control, ck215:** §§11–12 record the subsequent legacy-load, autosave
cycle, manual save and fresh-process reload result; the ask is consumed.
The explicit metadata marker and closed-run error sweep accompany positive load
evidence. This verifies the owner fixture, not full historical save compatibility.

During preparation the active autosave entry had rotated out. The agent restored
`Autosave Sol 31(3).savegame.sav` using exclusive-create from the protected backup;
SHA256 remained `36e32972717e2177ede90a66e11ba7558a82ebeaef22c4c869d081eb02d2192e`.
No existing save was overwritten. Active directory:
`C:/Users/stkot/Saved Games/Surviving Mars Relaunched/76561198020568696/`.
The owner's `trainhub post stuck test.savegame.sav` was also copied to the protected
backup directory; SHA256 `f1aeae7d526268e857d0c4c08e24ca7362cbfbed9af50f49a7ea70298d171ce8`.
Copy/readback equality was asserted. Earlier read attempts used a nonexistent
donor saves path and omitted the Steam-id subdirectory; no absence conclusion
was taken until the real directory was listed. A quoted PowerShell rg pattern
also misrouted a search; the literal source searches above replaced it.

## 11. Native 128× autosave cycle, 2026-09-24

Owner loaded the original autosave, ran at 128×, let a new autosave generate,
continued, reloaded that autosave, continued again and flushed the log. This
fulfills the legacy-load and same-process autosave/reload portion of ck215.
No code changed for this read. HEAD was `29c3666`; `git diff 102f5f0..HEAD --
tools/devmods/train_hub/Code/20_TrainHub.lua tools/devmods/train_hub/tests/dwell_smoke.py`
was empty. The intervening `29c3666` is design-only, outside this test.

Preserved evidence in `docs/archive/train_hub_load_crash_20260924/`:
`Mars.exe-20260924-12.06.00-6aad2d75.partial-autosave-validation.log` and its
`.receipt.json`. The receipt records input hash, bytes, line count, HEAD, regexes,
counts and exact matching members. Exclusive-create/readback equality preserved
the captured bytes. The game was still open, so this is a flushed prefix through
RT **0:24:47.809**, not a closed-process absence claim. The first Python print
failed on a console encoding character; rerunning with UTF-8 stdout succeeded.

Evidence on **1.1.1.405907**, executable **6aad2d75** (log header):

| observation | members in preserved log | measured result |
|---|---|---|
| save guard installed | 136 | one positive guard marker |
| game load completed | 270, 580 | two `Game Loaded in` markers |
| map ready after load | 283, 593 | two map-ready markers |
| 128× actions, counting `[mod]` only | 341, 493, 597, 743 | four positive speed records |
| explicit flush actions, counting `[mod]` only | 740, 746 | two `flushed=true` records |
| persistence/load/assert/crash filter below | empty member list | zero matches in this prefix |
| Lua error | 165 | one: existing ArtSpecEditor.lua:573 / EntitySpecPathToEntity, D14(e) |
| Braze failures | 193, 195, 197, 199, 202, 204 | six lines: DNS/session/launcher/init failures, same startup telemetry issue as earlier logs |

Counts were measured by Python `re.search` per decoded line, with each pattern
and matching line stored in the receipt. The negative check was also executed:

```powershell
rg -n 'Persist error:|Attempt to persist|ASSERT|\[ CRASH \]|Access violation|Unpersisted function|Unpersist missing permanent|snapshot cancelled|LoadGame error:|Savegame error:' docs/archive/train_hub_load_crash_20260924/Mars.exe-20260924-12.06.00-6aad2d75.partial-autosave-validation.log
if ($LASTEXITCODE -ne 1) { throw 'snapshot contains a failure or grep failed' }
```

This passed at `29c3666`. Positive guard/load/map markers were asserted beside
it. No compressed save body was searched for absence. The broader
`error|exception|assert|crash|warning|fail|invalid` and
`lost|stuck|leak|fatal|problem|timeout|cannot|unable|missing|not found|unavailable|bad|dropped`
reads found no additional runtime fault in this prefix. The ArtificialSun
startup availability warning at 156 resolves at 161. The console copy reports
`truncated=true` because its display buffer holds a limited tail; this review
read the entire flushed disk file, not just that copied tail.

The active autosaves were copied outside rotation to
`scratch/train_hub_load_20260924/saves/autosave_guard_128x/`. Both copies were
byte-checked. Metadata-only reads of their first 200000 bytes each found exactly
one `SMROptIn_hub_native_waiter = 1` and `autosave = true`:

| file | GameTime | os_timestamp | SHA256 |
|---|---|---|---|
| `Autosave Sol 36(2).savegame.sav` | 25460094 | 1790267378 | `9739eeb5dacf3f89854207bf37d0c29e1ea53ae9acec12410e6a3f887dbbf28b` |
| `Autosave Sol 41.savegame.sav` | 29143934 | 1790267458 | `cb7463bc93302df43d49bb5281b3f532ddea70fe8fe328f127c7beee6f2eee41` |

These are subsequent saved artifacts, not a proved filename for the loaded
autosave: the reload resumes at game time 25361662 (581–591), before either
artifact's metadata GameTime. The owner identifies the reloaded input as the
new autosave. Sol 41's timestamp is also later than the captured log's last
flush, so its metadata proves the new mapping was written, not that this log
already covers every event of that later save. Retain those evidence boundaries.

**Verdict:** positive native legacy-load→autosave→same-process reload with no
matching save/load failures in the flushed prefix. The existing startup art
error and telemetry failures remain concerns in their recorded scopes. Do not
call the entire log error-free, certify every historical save, or infer drone
repair completion from this accelerated run. At this capture, the fresh-process
reload, named manual-save leg and closed-log check were still ck215; the owner's
next report and §12 complete those controls. L5 keeps its broader smoke.
Executed model: GPT-6 (Codex), no subagents.

## 12. Named manual save and full restart verified, 2026-09-24

The owner then reported making a new hard save, fully restarting, loading that
save and flushing the new log. The completed `12.06.00-6aad2d75.log`, the new
`12.35.05-6aad2d75.partial-manual-restart.log`, and
`manual_restart_20260924.receipt.json` are preserved beside §11's earlier prefix.
No archived file was replaced. Capture HEAD `69f7cc5` only adds design/prompt
work since `29c3666`; `git diff 102f5f0..HEAD --` over the hub code and dwell
smoke is still empty. Runtime remains the guard from `102f5f0`.

The receipt's per-line regex measurement and the same failure `rg` command from
§11, now over these two named files, passed with zero failure matches and the
positive controls below. Each total is reconciled against its member lines:

| check | closed 12.06.00 run | new 12.35.05 flushed prefix |
|---|---|---|
| guard active | 136 (one) | 136 (one) |
| completed loads | 270, 580, 1009 (three) | 268 (one) |
| map ready | 283, 593, 1022 (three) | 284 (one) |
| persist/load/assert/crash failures | zero | zero in the captured prefix |
| normal exit | 1033 (one), followed by WM_QUIT | none; process still open |
| existing ArtSpec Lua error | 165 (one) | 165 (one) |
| Braze failures | 193,195,197,199,202,204 (six) | same line members (six) |

The named file is `trainhub post stuck test.savegame.sav`, written at metadata
`os_timestamp=1790267683`, with `SMROptIn_hub_native_waiter=1` and
`GameTime=31329512`. The fresh-process load's toolkit readouts at 269–280 report
that exact game time. This independently ties the marked manual save to the
owner's successful cold load; the prior process also loaded it at 1009 before
exiting. The restored colony advances to game time 31345537 at the new flush
(288), so this is not merely a load-banner observation.

A byte-identical copy lives at
`scratch/train_hub_load_20260924/saves/manual_guard_123443/trainhub post stuck test.savegame.sav`.
Its SHA256 is `d1c0c1647fb524ec45191316cb1999ac94a4a0f656f73ca876d5782268a87797`.
This is separate from the earlier protected file with the same display name;
no backup was overwritten. Metadata inspection was limited to plaintext header
fields in the first 200000 bytes; no compressed-body absence claim was made.

**Result:** the reported native save defect passes the owner fixture's legacy
load, generated-autosave/reload, new manual save and fresh-process reload controls.
The completed writer process has no persistence failures. The new process has
none in its flushed prefix. Existing D14(e) art-import and Braze network startup
errors remain; the logs are not globally error-free. No code change was needed
after the guard for this run.

ck215 is consumed. Test-shape clarification: autosave was reloaded in the writer
process; the independent fresh-process leg used the new manual save. Both carry
the same explicit marker and use the same guarded snapshot/load mapping, so this
covers the regression mechanisms without another blocking rerun. An autosave-only
cold reload was not separately performed. Ambiguous pre-wrapper hub saves and
the both-configuration/toggle ship matrix remain outside this result; D14's
other audit findings and L5's drone smoke remain open.
Executed model: GPT-6 (Codex), no subagents.
