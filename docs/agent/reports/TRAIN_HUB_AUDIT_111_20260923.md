# Train hub / rail shaft audit — 1.1.1.405907

Executed 2026-09-24; owner request and incident 2026-09-23. **Stall cause OPEN.**
**Correction after owner testing: `3a0faff` is withdrawn.** Old autosave and
known-good template loads asserted and crashed with that change. The legacy
dwell closure is restored; its original save defect remains OPEN. Start with
the load-crash follow-up below before using the older audit instructions.
No game ran during the initial audit. The game was closed when checked; the availability
question received no answer during the source work. Brief stop 1 applies: the
stalled save must be read with the owner. Link 5 resumes with §6, before its next
meteor or mid-trip save. This is not certification of either dev mod on 1.1.1.

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

**Fixed in `3a0faff`:** preserve global `WaitWakeup`; shorten only the hub's
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

Commands run from this repo: `python tools/devmods/train_hub/tests/` followed by
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

## 6. Resume: one console read at a time

Owner-only live run is routed to the fix pack's checklist **ck212**, per this mod's kernel.
Keep the stalled save. Restart the process to load the corrected dev code, then
load that save without adding trains, firing meteors or unlinking anything.
Give only the next line; the agent reads its output in the newest file log.

1. `SMRRailShaft.Sweep()` — commands, route membership, map and station for each
   train. If there are no trains, first establish the correct fixture.
2. `SMRRailShaft.Routes()` — broken route membership vs an intact linear chain.
3. `SMRRailShaft.Status()` — actual cross-map mouths; enabled mod alone is not a shaft.
4. Select the built hub, then `HubRepairStatus()` — jobs, deadlines and stock waits.
5. Read track repair state with this single paste-safe line:

```lua
*r for _, c in ipairs(Cities or empty_table) do for _, t in ipairs(c.labels.TrackBase or empty_table) do if IsValid(t) then print(string.format("[TrainAudit] track=%s groups=%s unfinished=%s", tostring(t.handle), tostring(#(t.repair_cgs or empty_table)), tostring(#(t.elements_under_construction or empty_table)))) end end end
```

6. With the hub selected, read its lock and each train's live command thread:

```lua
*r local h=SelectedObj; print("[TrainAudit] crossing="..tostring(h and h.SMROptIn_hub_crossing)); for _, c in ipairs(Cities or empty_table) do for _, t in ipairs(c.labels.Train or empty_table) do if IsValid(t) then print(string.format("[TrainAudit] train=%s cmd=%s thread=%s station=%s track=%s",tostring(t.handle),tostring(t.command),tostring(IsValidThread(t.command_thread)),tostring(t.current_station and t.current_station.handle),tostring(t.track and t.track.handle))) end end end
```

If repairs remain, inspect those sites before making more damage. If route membership
is broken, follow the shaft report's reversible fixture procedure after preserving
the readout. If routes and tracks are sound, investigate the command/crossing lock;
do not clear a valid lock on assumption. Run a fresh fixed-process save and reload
on a throwaway copy, then exit and grep `Persist error` with positive SAVE/load/hub
lines. A negative log requires process exit. Only that control can close D14(a)'s
native result; only observed resumption can close the stall cause.

## 7. Remaining work / close-out inventory

| finding or request | home / next action | disposition |
|---|---|---|
| Save permanent defect | D14(a); load-crash follow-up below | `3a0faff` withdrawn; legacy hook restored, original save defect OPEN |
| Stall classification | §6; link 5 upstream notes | Open under brief stop 1 |
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
failing saved frame and recovery of the autosave remain unproved.

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

**Next owner check:** enable the original mod set, fully restart, load `train_hub_base`, do not overwrite it,
and exit rather than ignore an assertion. The agent reads the new log. A load
without assertions or CTD is the rollback control; if it still fails, the mapping
hypothesis alone is insufficient. If it loads, diagnose the old/new permanent
transition and test a migration before reintroducing the save repair. That repair
must distinguish legacy and newly written saves, and cover old→new→save→reload,
ordinary native saves and suspended waits. A version-only guess is insufficient:
`3a0faff` retained dev version 49, and the wrapper was introduced during version 9.
Then resume §6's stall reads and L5's remaining smoke. Neither native rollback
success nor save recovery has been observed yet.

Executed model: GPT-6 (Codex), as exposed by the transcript; no subagents.
