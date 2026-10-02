# Station rows without a hub — brief 30, 2026-10-02

**Attended batches A, B and C passed** (sitting records below, including `9b05edc`).
The subsequent depot work and next smoke are in
[Elevator Depot follow-up](ELEVATOR_DEPOT_REVISION_20261002.md).
This is the design pass authorized by the owner's
2026-10-02 ruling in the train spec §4.7. Station build: `3ff3ae4`; depot tooltip:
`63d72d4`. Both are pushed. Brief 30 remains live for the depot follow-up.

Started at `ea6d43fb93ea2bf669be564229c414c713476455`; `git log --oneline -5` and
`git pull` ran first (already current). Executed model: Codex (GPT-6 per session
instructions; an exact backend model id is not exposed in this transcript).
`python tools/doccheck.py --emit-fingerprint` read installed build **25579348**.
Source tree: `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src`.

## Design calls delegated by the brief

Every ordinary `Station` gets the existing native row and inline slider. The hub and
Elevator Depot keep their own panels. The states are Balanced → Export → Import →
Not accepted → Balanced. Ctrl+click copies the current mode and percentage to other
ordinary stations in the same city, including hubless stations, without advancing
the source. Not accepted still uses vanilla's flags and remembers the slider.

| Hubless state | Trains | Local drones |
|---|---|---|
| Balanced | Supply excess above the selected amount; receive up to it | Use it as the desired amount |
| Export | Supply stock above the minimum; refuse deliveries | Fill to capacity |
| Import | Receive up to the cap; never supply | May drain to zero |
| Not accepted | Vanilla disabled-resource drain | Vanilla disabled storage |

These are targets and bounds, not promises that stock exists elsewhere. Untouched
Balanced rows use the live absolute vanilla dial; an edited slider is a percentage
of live capacity and follows upgrades. The hubless tooltip describes other stations
as suppliers/receivers, without promising a hub or a central surplus sink.

Joining a hub switches to that hub's existing settings and default Balanced pin.
The station's independent settings remain dormant. Leaving resumes them; a station
never configured outside a hub resumes the vanilla dial as its Balanced target.
Rejoining restores the hub's table. Neither set is copied into the other. Baselines
from resources present only in the old set are cleared at this change of ownership.

## Mechanism and save footprint

SOURCE: `40_TrainDistribution.lua` keeps the existing hub allocation function and adds
a separate line-local allocation view. No hub object or hub implementation is needed
for this path. It wraps native `Train:TransferCargo` / `UnloadAll`, uses the existing
temporary-claim helper and synchronous capacity/enabled answers, and leaves native
code to write cargo and reservations. It uses the native should-move input to find
an empty pickup trip, as the hub path already does; no scheduler or movement changes.

SOURCE: native cargo bodies are `Lua/Units/Train.lua:744-831,862-1043` on archived
**1.1.1.406343 / build 25579348**. The hubless smoke checks byte parity of that file,
Station, MultiResourceDepot and MultiResourceCubeVisuals against the older archive
consumed by the existing harness. Late assignments exceeding a changed cap stay aboard
whole; vanilla may unload them at another accepting stop. No hub overflow exception
applies to a hubless row. A depot endpoint retains its own row writers and native
storage; its exchange is bounded by the ordinary station's row.

New persisted name, also in FIX_POLICY's inventory: **`SMROptIn_station_rows`**, on a
vanilla station, containing only resource keys and `{mode, percent}` data. This is
the inert-field rung: settings must survive a save in a colony with no mod-owned hub,
while vanilla has no field that represents per-resource percentages without changing
its removal behavior. It contains no object references, callbacks, custom classes or
threads. The old hub field `SMROptIn_distribution` is unchanged.

SOURCE / desk-checked: `transport_policy` is never written. Claims are synchronous and
released after evaluation, on genuine errors, and at SaveGameStart. At SaveGameStart,
hubless stations with applied settings regain vanilla's own desired amounts before
the snapshot; SaveGameDone and LoadGame reapply the saved inert rows. Native disabled
flags remain player-reversible through vanilla's controls. The hub's existing save
behavior stays as before. **Actual serialization and mod-removal loading are NOT RUN**;
the desk snapshot check does not claim either.

## Desk verification

Commands run on the working change based on `ea6d43f` (2026-10-02):

| Command | Evidence and limit |
|---|---|
| `python tools/devmods/train_hub/tests/hubless_smoke.py` | Archived native bodies with request doubles: caps/floors, Balanced pin, reservations, native rewrites, simulated save baseline and hub transitions; no hub class loaded. Engine behavior remains unobserved. |
| `python tools/devmods/train_hub/tests/distribution_smoke.py` | Existing hub allocation smoke passes, including chain routing, full-hub refusal and save hooks. |
| `python tools/devmods/train_hub/tests/distribution_departure_smoke.py` | Existing native departure/watchdog smoke passes. |
| `python tools/devmods/train_hub/tests/station_visuals_smoke.py` | Existing physical-capacity drawing smoke passes. |
| `python tools/devmods/train_hub/tests/distribution_ui_smoke.py` | Compiled native row/slider callbacks with window doubles: hubless cycle, slider, Ctrl copy and tooltip; existing hub layout checks pass. No pixels or hit-testing claim. |

PROBE SWEEP: `rg -n 'TEMPORARY' Code/ ../SMR-BugFixPack-TestKit/Code/` and doccheck's
matching sweep found no markers before testing. `tasklist /FI "IMAGENAME eq Mars.exe"`
found the game closed before Code writes. TestKit has unrelated working changes in
`Code/72_SMRTK_World.lua` and `README.md`; they are outside this task.

## Attended smoke

**NOT RUN.** The owner must see the hubless row draw and act, and the repaired twinless
infotip in game. Full shipping tests, removal testing and the shipping split stay outside
this design pass. No screen result is promoted by a slot's arithmetic.

The newest log was re-read on 2026-10-02:
`Mars.exe-20261002-00.07.14-6aba6e65.log`. Filter
`rg -n '9702|no pair: surface|pair formed:|SMRTK_(ACTION|SAVE|LOAD).*slot' <newest-log>`
shows underground station 9702 on lines to depot 9041 and ordinary station 10531,
with `target=none` before this change. The last Load A succeeded. These handles are
fixture leads, not guards: the new slots read the selected object's real map and hub.

Preload composition: the existing staged depot slots
`tools/devmods/elevator_station/tests/80_AgentSlots_depot.lua.txt`, followed by
`tools/devmods/train_hub/tests/80_AgentSlots_station_rows.lua.txt`, installed as the
shared TestKit's `Code/80_AgentSlots.lua` in pushed commit `2f5f8f8`. The old committed capacity bindings remain
recoverable at TestKit `f30ba1b`; the unrelated World/README edits are untouched.
`python tools/devmods/train_hub/tests/hubless_slots_smoke.py` passed at `63d72d4` plus
the sitting change: real native loader bodies with doubles, refusal guards, reservation
preservation and independent floor/cap/error/edit/deadline counterexamples.
The owner-run obligation is also on the fix pack's ck221 (`1b93f04`, pushed). Its existing
asks and OI-38's separate scripted up-leg reading remain. GitHub accepted the TestKit's
normal push with a notice that the account bypassed its pull-request rule.

| SMRTK Slots & notes | Binding for this sitting |
|---|---|
| Scratch | Read depot pair; reports `underground_panel` and `copy` |
| 1 | Set selected station/depot Metals to 80% while paused, using free requests only |
| 2 | Run to the cabin's next arrival, Ultra, automatic pause |
| 3 | Read selected depot half, row and copy witness |
| 4 | Read ordinary station rows and line cargo; `hub=none` or its **serving hub** |
| 5 | Run selected station's Metals toward its row target, Ultra, automatic pause |
| 6 | Run to the cabin's next departure, Ultra, automatic pause |

Predictions written before boot: slots 1/4/5 report `SMRTK_ACTION action=slot_N status=OK`
on valid paused selections. The stock setter reports actual `before`, `added`, `stock`,
`target` and `reserved_shortfall`; it refuses a disabled row or a fully reserved change.
It can add at most 80% of that station's current Metals capacity, or remove unreserved
stock down to it. This is fixture provisioning, not production evidence. It touches no
other resource or train cargo. Keep the existing Load A as the recovery fixture.

Slot 5 polls every 250 game ms; paused time makes no progress. Its normal budget is
six game hours with a working supplied line, its abort is eighteen game hours (3×),
and it pauses on `SMRTK_TRIGGER trigger=station_rows_30 verdict=target_sampled`, a changed
row/network, a new Lua error, crossed floor/cap, or deadline. `target_sampled` requires
both stock movement and a native allocation evaluation, within the loader's resource-unit
rounding; it is evidence to inspect, not PASS. Drones can confound stock movement: slot 4
reports coverage and train assignments. Use an uncovered station where possible; otherwise
the agent reads the cargo evidence before attributing a stock change to trains.
Save/load/map changes disarm watches; re-arm explicitly. No automatic arm at boot.

**Batch A — hubless UI and Export** (all steps NEVER RUN):
1. Restart into the existing depot fixture / Load A, pause, select the ordinary underground
   station beside the depot, and open Slots & notes. First-screen witness: native resource
   titles and inline sliders are present without adding a row underneath.
2. Press slot 4. Prediction: `hub=none`, Metals has a numeric target, and no UI/allocation
   error. Note the capacity; it determines every following amount.
3. Click Metals to Export, slide to 20%, and hover the row. Prediction: Export arrow/title,
   20% minimum, and the no-hub explanation. Press slot 1 to provision 80%, then slot 4.
4. Press slot 5. On its pause, press slot 4. Prediction: native cargo moved away; Metals
   reaches the 20% floor within one resource unit and never goes below it through train loading.
   A deadline, engine error or crossed bound is a report, not a retry for a preferred result.
5. Flush + copy and report whether the row fits and the control acts. The agent reads the
   newest complete log before moving on; screenshots are only needed for a visual defect.

**Batch B — Import, persistence, existing hub** (NEVER RUN):
1. On the same underground line, select the other ordinary station (10531 in the old log),
   set Metals Export 0%, and press slot 1. This is the **supplier station**.
2. Return to the first ordinary station (the **receiving station**), choose Import 50%,
   and press slot 4. Prediction: local drone supply desired is zero, target is half capacity.
3. Press slot 5, then slot 4 after the pause. Prediction: trains deliver up to the cap and
   do not take the import stock away. Inspect cargo evidence and reported drone coverage.
4. Save B and Load B through SMRTK, pause and read the receiving station again with slot 4.
   Prediction: Import 50% and its baseline survive, and the slider remains in its native row.
5. On the surface, select an existing ordinary station served by a hub and press slot 4.
   Prediction: its existing hub settings and tooltip remain, and `hub` names its **serving hub**.
   Judge the hubless Balanced/Export/Import choices and independent settings by eye, then flush.

**Batch C — OI-38 E5, both missing-twin notices** (NEVER RUN):
1. Load A, pause and press Scratch to capture the pair's current settings/copy witness.
2. Salvage the surface depot. Underground, hover a resource row on its surviving half,
   then press slot 3 and Scratch. Prediction: tooltip starts with the exact **No surface twin**
   sentence; Scratch reports no pair. The survivor keeps operating as a plain station.
3. Place and finish a new surface depot. Let pairing run (slot 6 can advance to departure),
   pause and press Scratch. Prediction: `pair formed: surface <new> underground <old>`,
   `underground_panel=matches copy=current`; the new surface adopts the old row settings.
4. Reopen/hover the underground row. Prediction: the missing-twin notice is gone and its
   read-only settings still match the new surface half. This completes E5 only when witnessed.
5. Load A; salvage the underground half and hover a surface resource row. Prediction: **No
   underground twin** leads the tooltip. Finish with Load A and Flush + copy.

End the boot with SMRTK Read taint and Read eligibility. The latter is sandbox-unavailable,
not an achievement verdict. The pre-existing OI-38 scripted up-leg read remains separately
owed; its original slots 6 and 2 are available, but it is not silently counted as run here.

## Depot twinless infotip repair

SOURCE: the existing `D.RowText` already contained both missing-twin sentences, and
the existing row decorator did not set the actual control's rollover text. Vanilla's
compiled `sectionStorageRow` stores the translated `<ResourceRolloverText(res)>`
formatter (`Lua/XDef/sectionStorageRow.generated.lua:8`, archived 1.1.1.406343).
The old desk witness read the object's method, not the row control.

The decorator now writes the current `D.RowText` directly to each resource row's
`RolloverText`, on both maps. Missing-twin text leads the tooltip, before the longer
flow explanation. Refreshing the row after re-pairing removes that notice. Pairing,
settings adoption, storage and plain-station behavior are unchanged. This repairs
the presentation path; the exact cause of the owner's missing display is **not
isolated live**, and the in-game tooltip remains the acceptance check.

`python tools/devmods/elevator_station/tests/wiring_smoke.py` PASS at `3ff3ae4` plus
this working change (2026-10-02). It now checks the actual decorated controls for
both missing twins and their refreshed paired state, alongside its existing pairing,
demolition and adoption checks. The brief's known stale title test was updated: it
now loads the hub's current integer-ceiling helper and requires both title helpers
to fit, instead of expecting the hub's already-repaired rounding defect.

OI-38 E5's in-game new-surface adoption remains NOT RUN. No new persisted field.

## Handoff at the first sitting batch

Next action: owner restarts and runs Batch A above. Then the agent reads the newest
complete boot log and guides B/C, preserving the log if a result is recorded. No live
acceptance has been inferred from the desk suite; the task brief is retained.

Unrelated working paths left untouched: TestKit `Code/72_SMRTK_World.lua`, `README.md`;
fix pack `docs/agent/reports/RULE_PLACEMENT_TEST.md`, `tools/SMRTK.md`. The local task
introduced no changes to either pack's shipping `Code/` or to train movement.

## Sitting, batches A and B (2026-10-02, guided by the orchestrator)

Log `Mars.exe-20261002-10.43.08-6aba6e65.log`, read on each "flushed"; "LUA ERROR" count 0.

- **A, Export 20% hubless: PASS on the log.** Slot 4 on StationBig 9702: `hub=none mode=export
  percent=20 capacity=240000 stock=192000 target=48000`. Slot 5's first watch was disarmed by an
  autosave (`reason=SaveGameStart`); at its re-press the stock stood at `before=48059`, the floor
  within one unit, 144 Metals carried off by trains. The look passed in the owner's word (below).
- **B, Import 50% hubless: PASS on the log.** Supplier StationSmall 10531 at Export 0%, stock 96000
  of 120000. Slot 5 on 9702: `before=44059` to `stock=119059 target=120000 supply_desired=0`,
  `verdict=target_sampled`.
- **B, persistence: PASS.** The owner pressed **Save A / Load A** (not B), so Load A is now this
  later state; the depot pair is intact in it. After the load, slot 4 on 9702 reads `mode=import
  percent=50 target=120000`.
- **B, a hub's own station unchanged: PASS on the log.** Slot 4 on surface station 2007:
  `hub=6430 hub_role="serving hub" mode=export percent=9 target=10800`.
- **TestKit papercut:** slot 5 refused five presses with `reason="cancel the current run first"`
  while batch A's re-armed run was still live; it cleared only when the owner unpaused and the old
  watch fired `verdict=row_changed`. Slot 5 then refused once with `reason="pause first"` and armed
  on the next press. A slot that cancels its own stale run, or says how, would save the owner this.
- **The look: PASS.** Asked whether the rows and tooltips looked right underground and on the hub's
  surface station, the owner: *"Yes"*.

## Sitting, batch C (same log, read on "flushed"; "LUA ERROR" count 0)

- **C1-C2, "No surface twin": PASS.** Owner's screenshot: the tooltip leads with the exact sentence
  on the surviving underground half's Metals row. Log: `half gone: surface 9036 survivor 9041`,
  `no pair: surface none underground 9041`; slot 3 `twin=none flow=plain working=true`; Scratch
  `underground_panel="no pair"`.
- **DEFECT (open): the cabin keeps moving with no twin.** Owner: *"So we get the message now, but
  the cabine continues to move up and down."* The log logs no leg after `no pair` (`pair
  surface=none underground=9041 ... cabin=none legs=0`), so the cargo logic is idle as designed
  while the cabin's art keeps cycling, against the notice's own "the cabin is idle".
- **C3-C4, the new surface adopts the copy (OI-38 E5's rest): PASS.** `pair formed: surface 10915
  underground 9041 rows ...` with the same rows; slot 6 `verdict=departed`; Scratch
  `underground_panel=matches copy=current`. The owner: *"everything else worked as expected"*.
- **C5, "No underground twin": PASS on the owner's word.** The log holds no `half gone:
  underground` line before the closing Load A, so the salvage may not have completed in game time;
  the desk smoke covers this branch (`wiring_smoke.py`).
