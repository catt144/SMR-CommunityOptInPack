# Station rows relay: the unattended in-game leg, with a one-minute glance

One-off. Authored 2026-10-22 at `b5e76b4` by Claude Fable 5.1 for the owner to fire. Delete this
file and its row in `docs/agent/prompts/README.md` in the commit that files the result. Start with
`git log --oneline -3` and `git pull`; the gitStatus block in your context is a snapshot.

## Authority and outcome

The relay change set (`optin-v1.0.3` → `3aa5402`, D16/D18, rulings R1–R7) is desk-verified and
audited twice (report `docs/agent/reports/STATION_ROWS_RELAY_20261021.md` §§15–18). The owner
chose to release without an attended A/B and asked for the checks an unattended session can
run instead, plus one glance at the panel by their own eye. This leg is a smoke, not an audit:
it runs the shipping code in the real game against a save on the rig and reports what the log
and the owner's glance show. It changes no shipping code, no save on disk and no module setting.

End state: a report `docs/agent/reports/STATION_ROWS_RELAY_LEG_20261022.md` with the log's
verdict lines, the complete game log copied after the process exited under
`docs/archive/station_rows_leg_20261022/`, one `Unattended run` line appended to the build status
lines in `docs/agent/bugs/D16.md` and `D18.md`, one sentence in the outbox's station rows entry,
the kit disarmed, doccheck GREEN, one commit with a pathspec. The owner's glance result, if they
gave one, recorded verbatim; if they did not glance, say so and nothing is inferred from it.

## What the leg checks, in the owner's words

From the risk assessment the owner accepted (2026-10-22):

1. **A Lua error in the train code** on the paths the save exercises: the hub network, the
   hub-managed depot, and a hubless line with a set row if the save has a station off every hub.
2. **Existing depots changing on load (R5):** an untouched Import row on the depot reads 100 and
   an Export 0; a saved slider keeps its number.
3. **Saved rows from the old cycle:** every station's rows printed, so Balanced pins are visible.
4. **The panel, as far as Lua reaches:** the new icon asset measures non-zero; the rollover texts
   read as built. Pixels and layout are the owner's glance.
5. **Click latency:** `D.Refresh()` timed on this colony, with its hub and station counts, so the
   figure is bounded by what it was measured on.

## The rig, and the rules that bind an armed run

- The harness is the fix pack's `B:\Dev\SMR\SMR-BugFixPack\tools\arm_leg.ps1` with a JSON manifest;
  its rules and the failure behind each are `B:\Dev\SMR\SMR-BugFixPack\tools\arming\README.md`.
  Read it before writing the manifest. In short: arming is a file, never an inline one-liner;
  every payload carries a `TEMPORARY` marker and lands in the shared kit
  (`B:\Dev\SMR\SMR-BugFixPack-TestKit`), never in a mod; ASCII-only bodies; the driver calls its
  boot symbol at file scope and calls `quit()`; `-Mode verify` reads the gates back.
- `Mars.exe` must not be running when you arm or disarm; the owner and other sessions share one
  game. `tasklist | grep Mars.exe` before each. An armed kit makes this repo's doccheck RED
  (`TESTKIT TREE`), so nothing is committed while armed.
- Launch: `Start-Process "A:\SteamLibrary\steamapps\common\Project Spark\Mars.exe"` with that
  working directory while Steam is running; the first process hands off and exits in about 30 ms,
  Steam relaunches the real one a few seconds later with no dialog. Wait on `tasklist` until the
  process is gone before reading a count from the log; a log read while the game runs is partial,
  which is fine for a marker and wrong for a count. Logs:
  `%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-*.log`, newest without `GED` in the name.
- Only `ModLog` reaches the log file; `print` does not. Prefix every line `[RELAYLEG]` and flush
  (`FlushLogFile`) after each block.
- The save: `C:\Users\stkot\Saved Games\Surviving Mars Relaunched\<steamid>\SMRTK_A.sav`, the
  final train battery's fixture (a hub, an Elevator Depot pair, stations; 1.1.x). Load it natively
  from the driver, `LoadGame("SMRTK_A.sav", {})`, as the c95 payloads do; the kit's own loader
  refuses a foreign session. Set `config.AutosaveSuspended = true` at boot, before the load: the
  game cannot disable autosave from its options and this run must write no save. Never call
  `SaveGame`.
- Modules: the owner's standing config has both mods loaded and the train modules on. The
  payload reads `SMROptInPack.IsActive` for `StationRows`, `TrainHub`, `ElevatorDepot` and logs
  them; it never writes `CurrentModOptions`. A module found off makes that part NOT RUN.
- Mod code runs sandboxed: no file access. The code's identity is witnessed from inside:
  `SMROptInTrainDistribution.WaterFill`, `.IsJunction` and `.Clear` exist only since the relay
  commits; log their presence, the engine's own loaded-mods lines, and `BuildVersion`.

## The payload, in order

Manifest and payload live in this repo under `tools/trains/relay_leg/` (`relay_leg.json`,
`98_RelayLeg.lua.txt`), with the manifest's `park` pointing there and `kit` at the shared kit;
the harness installs the payload as the kit's `Code/98_RelayLeg.lua`. Markers in the log:
`[RELAYLEG] BOOT`, `CENSUS`, `DEPOT`, `ROWS`, `SOL n`, `HUBLESS`, `ICON`, `TOOLTIP`, `REFRESH`,
`ERRORS`, `READY`, `END`, and `ERROR <stage>` on any caught failure. Every stage under `pcall`;
a failure logs and moves on, so the glance still happens.

1. **BOOT:** build, loaded mods, the three module states, the three identity witnesses,
   autosave suspended.
2. **LOAD** `SMRTK_A.sav`; wait for the city and let the handlers settle (the autorun harness's
   pattern in the kit's `95_AutoRun.lua` is the reference for waiting on a map). Pause.
3. **CENSUS:** every `Station`: handle, class, `D.HubFor`, `D.IsJunction`, depot or not; every
   `Train`: handle, command, current station, cargo. Hub count, station count.
4. **DEPOT (R5):** for the surface half and the underground half, every storable resource:
   `SMRElevatorDepot.State`, `SMRElevatorDepot.Target` with its `set` flag, `SMRElevatorDepot.HubEntry`.
5. **ROWS:** every ordinary station's saved rows (`SMROptIn_station_rows`) and the hub's table
   (`SMROptIn_distribution`), mode and percent per resource; `D.RowState` for Metals and Concrete.
6. **RUN:** resume at the game's top speed for three sols by `UIColony.day`, capped at six real
   minutes; at each sol boundary log `D.calls`, `D.CallsFor` per station, every station's Metals
   and Concrete stock and every train's cargo and command. This is the error exposure: trains
   serve the hub network and the depot under the new code.
7. **HUBLESS (only if the census found a station with no hub):** `D.Set(st, "Metals", "import", 100)`
   on it, in memory only; run two more sols as above; log that station's `CallsFor` rising
   (the hubless view ran) and the stock readings. Then `D.Clear(st, "Metals")`. Skip with a line
   if every station is hub-owned; do not build one.
8. **ICON:** `UIL.MeasureImage` for `UI/IconsRemaster/Sections/resource_accept.tga`,
   `resource_storing.tga`, `elevator_resource_up.png`, `elevator_resource_down.png`,
   `resource_no_accept.png`: width and height each; zero means missing.
9. **TOOLTIP:** `ResourceRolloverText("Metals")` on one ordinary station and on the depot's
   surface half, first 300 characters each, markup included.
10. **REFRESH:** `D.Refresh()` one hundred times under `GetPreciseTicks()`; log total and mean
    with the hub and station counts beside it.
11. **ERRORS:** the kit's error counter (`SMRTK.error_count`) and any Lua error text the
    kit captured; the agent also greps the finished log for `Lua error` and `[TrainDistribution]`.
12. **READY (the glance):** pause; `SelectObj(<the depot's surface half>)` so its infopanel is
    open; log `READY handle=<n>` and flush; then a real-time thread waits up to thirty minutes
    for the owner to close the game and calls `quit()` if they do not. `END` is logged either way
    just before `quit()`.

## The agent, around the run

1. Arm with the harness, verify, confirm `Mars.exe` is not running, launch.
2. Watch the newest log for `[RELAYLEG] READY` (poll the file; a marker read is fine while the
   game runs). On `READY`, send the owner one notification with the session's push notification
   tool, one line under 200 characters, in this shape: `Relay leg ready: game paused on the
   Elevator Depot panel. One-minute glance, then close the game (no save).` If the tool reports
   it did not send, say so in the report and leave the game to its own timeout.
3. The glance, written for the owner in the report and repeated in the notification's reply
   if they ask: on the depot panel, an untouched Import row's slider sits at 100 and an Export
   at 0; click any ordinary station: its rows read `<resource> · Default` with the crate icon;
   one click on a row gives `Export` with the up arrow, a second `Import` with the down arrow,
   a third `Not accepted`, a fourth `Default` again; hover shows the tooltip. Then close the game
   from its menu without saving. Nothing they do in that minute is recorded by the leg; what they
   saw is theirs to tell you.
4. Wait on `tasklist` until `Mars.exe` is gone (the owner closed it, or the payload's timeout
   did), then disarm, verify, and copy the complete log into the archive folder.
5. Write the report: one table per marker block with the figures as the log printed them,
   `ERRORS` first; the identity witnesses; what was NOT RUN and why (a module off, no hubless
   station, the owner did not glance). Then the records, doccheck, one commit.

## Scope

In: the leg, its manifest and payload under this repo, the report, the archive copy, the three
record lines. Out: any shipping code or test, any save written, Mod Options, the release itself
(`release_prompt.md` is the owner's), the hub tree, §8. Report outside findings; do not edit them.

## Stops

- `Mars.exe` is running when you would arm, or the harness's `-Mode verify` fails: report, do not
  launch.
- `SMRTK_A.sav` is missing or fails to load (`LOADERR` in the log): report; do not substitute an
  owner's play save.
- The run shows a Lua error from `Code/StationRows_*` or `Code/ElevatorDepot_*`: disarm, copy the
  log, report the traceback verbatim with the stage, and stop; a fix is the owner's next brief.

## Claim limits

Supported: "ran unattended in the game at `<sha>` on `SMRTK_A.sav`, log `<name>`: errors 0,
depot targets as ruled, rows as saved, icons present, refresh `<mean>` ms on `<n>` stations and
`<h>` hubs; the owner glanced and said `<verbatim>`". Not supported: tested in game in the
record's sense (`tested-attended` is the owner's word), any claim about a hubless junction unless
step 7 ran, any figure about drones or throughput, anything about pixels the owner did not say.

## Routing

Moderate reasoning with these instructions; the hazards are the rig's, not the problem's. Any
model; a different one from the build's only if the owner wants the leg to double as a check of
its author. Record the executed model from the transcript in the report.

## References

Skills: `smr-orientation`, `smr-bug-library`, `doc-editing`, `smr-session-close`. Rig notes:
`tools/TESTKIT.md` (Unattended legs), `tools/SMRTK.md`, the fix pack's `tools/arming/README.md`
and its `payloads/98_C95Save.lua.txt` as the load-a-save driver shape. House rules `CLAUDE.md`;
process `docs/agent/WORKFLOW.md`; code `docs/agent/FIX_POLICY.md`.
