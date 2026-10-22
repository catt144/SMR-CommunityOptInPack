# Station rows relay: the unattended in-game leg — 2026-10-22

**Verdict: smoke clean within its reach.** Ran unattended in the game at `e49a4e4` (shipping
`Code/` identical to `3aa5402`: `git diff --stat 3aa5402 e49a4e4 -- Code items.lua metadata.lua`
prints nothing) on `SMRTK_A.sav`, log `Mars.exe-20261022-12.23.59-6aba6e65.log`: errors 0,
depot targets as ruled, rows as saved, icons present, refresh 11.10 ms mean on 19 stations and
2 hubs; the owner glanced and said "everything looks clean to me". The first run fell short in
two parts: the main run reached 2 of 3 sols, and the hubless set row was never called on
(`CallsFor` stayed 0). **A second run the same day (§15, owner: "you can proceed with that")
closed both:** set rows on the hubless junction `StationBig(9702)` (Metals Import 100, Concrete
Export 0) ran three full sols with errors 0, the hubless view read them (`CallsFor` 1 → 45) and
Metals rose 45157 → 131157, against a fall of 1000 on default rows in the first run.

This is a smoke, not `tested-attended`; that word is the owner's. Brief:
`STATION_ROWS_RELAY_LEG_medium.md` (consumed by this commit). Executed model, from the
transcript: Claude Opus 5.5 (`claude-opus-5-5`).

## 1 · The run

| item | value |
|---|---|
| rig | retail (`rig_switch.ps1 status`: install BetaKey `public`; Mods junctions to `B:\Dev\SMR\SMR-BugFixPack` and this repo; saves to `SMR-Saves\retail`; Steam Cloud OFF) |
| harness | fix pack `tools/arm_leg.ps1`, manifest `tools/trains/relay_leg/relay_leg.json`, payload `98_RelayLeg.lua.txt`; `-Mode verify` every gate passed before launch and after disarm |
| launch | `Start-Process` 12:21:53; handoff log 539 B; Steam relaunched the real process at 12:23:59; it exited 12:54:37 (the owner closed it, before the payload's 30-minute timeout, so no `END` line was logged) |
| log | archived complete after exit: `docs/archive/station_rows_leg_20261022/Mars.exe-20261022-12.23.59-6aba6e65.log`, 671 lines; as the game wrote it (CRLF) 50,906 B, sha256 `95974c3b1b8e427bb0c8bb64d3aaefa01ec14c7c5d6ef9449973c0038a90a017`; as committed (git normalises to LF) 50,449 B, sha256 `5a295c252a1da5ee27ab5e8d664818cfa40ad74880a1070ca4999cdffb20a5cc`; 314 `[RELAYLEG]` lines (`grep -c "\[RELAYLEG\]"`) |
| save | `SMRTK_A.sav` loaded natively, day 50; its mtime stays 2026-10-03 12:57:01. `find <saves> -newermt "2026-10-22 12:00"` lists only `account.dat`, `account.dat.bak`, `steam_autocloud.vdf`: no save written |
| kit | disarmed, verified; the harness had also dropped the two commented-out `mustNotBeListed` lines from the kit's `metadata.lua`, restored with `git checkout -- metadata.lua`; kit `git status` clean |

The first arm failed its own symbol gate (`RelayLeg.count, hubs, surface, underground`, set only
by multi-assignment); the payload was given single assignments and re-armed before any launch.

## 2 · ERRORS

| check (on the archived log) | result |
|---|---|
| `[RELAYLEG] ERRORS smrtk_error_count=` | 0 |
| `grep -c "Lua error"` | 0 |
| `grep -c "SMRTK_ERROR"` | 0 |
| `[RELAYLEG] ERROR <stage>` (caught stage failures), `LOADERR`, `TIMEOUT` | none |
| `[TrainDistribution]` lines | 2, both at load: `station rows loaded (brief 30: hub + hubless)`, `native storage-row UI registered` |

## 3 · BOOT: identity

| witness | logged |
|---|---|
| build | `BuildVersion` 1.1.1.406343, `LuaRevision` 406343 |
| engine's loaded mods (log lines 63–68) | Relaunched Fix Pack v1.00-026; Test Kit; DEV ONLY - Opt-In Modules Workbench (never upload) v1.00-000; Relaunched Fix Pack: Opt-In Modules v1.00-003; Save Buffer Fix; TEMPORARY - Linux NVIDIA 580 Crash Workaround |
| modules | `StationRows`, `TrainHub`, `ElevatorDepot`: `active=true` each |
| relay witnesses | `SMROptInTrainDistribution.WaterFill`, `.IsJunction`, `.Clear`: `function` each; `D.error=nil` |
| autosave | `config.AutosaveSuspended=true` |

## 4 · CENSUS

19 stations, 2 hubs (`SMROptInTrainHub6` 6430 and 6495), 17 trains, one Elevator Depot pair
(surface 9036, owned by hub 6430; underground 9041, no hub). Row stations: 15, of which 12
hub-owned (8 under 6430, 4 under 6495) and 3 with no hub — `StationSmall(7861)`,
`StationBig(9702)` (a junction, `IsJunction=true`) and `StationSmall(10531)`; 12 + 3 + 2 hubs +
2 depot halves = 19. Hub-owned junctions: `StationBig(2009)`, `StationBig(7873)`. Trains at load:
9 `LoadTrain`, 8 `GotoStation`, cargo as printed in the log.

## 5 · DEPOT (R5)

21 storable resources per half (16 + 1 + 2 + 2 below). Surface half 9036 (the setting's owner):

| row | State | Target | set | HubEntry | reading |
|---|---|---|---|---|---|
| 16 untouched Import rows (BlackCube … WasteRock) | `to_underground` | 100 | false | `import/100` | untouched Import reads 100 |
| PreciousMetals, untouched Export | `to_surface` | 0 | false | `export/0` | untouched Export reads 0 |
| Metals, Concrete (Import) | `to_underground` | 21 | true | `import/21` | saved slider keeps its number |
| Food, Sugar (Export) | `to_surface` | 0 | true | `export/0` | saved 0 kept |

Underground half 9041 reads its surface twin's state and target; its `HubEntry` is the inverse
flow at the fixed ends (`export/0` where the surface imports, `import/100` where it exports), as
`D.HubEntry` defines.

## 6 · ROWS

No ordinary station holds a saved `SMROptIn_station_rows` table (`saved=nil` on all 15). Hub
tables: 6430 holds Metals rows for 8 stations (`StationSmall(2007)` export 9, the rest import
100, the depot 9036 among them), 6495 holds Metals import 100 for its 4. **No Balanced pin is
saved anywhere in this fixture.** `D.RowState` agrees with the hub tables for Metals; Concrete is
`default` everywhere, its percent the live dial (8 on a small station, 4 on a large).

## 7 · RUN

Speed `const.GameSpeeds.fastest`, `GetTimeFactor()` 20000 throughout.

| boundary | real time (log stamp) | `D.calls` |
|---|---|---|
| load, day 50 | 0:00:42 | — |
| sol 1, day 51 | 0:00:43 | 15 |
| sol 2, day 52 | ≈ 0:01:20 | 465 |
| cap | 0:06:42 | `RUN done sols=2 capped=true` |

**Shortfall: 2 of 3 sols.** No sol boundary arrived between 0:01:20 and the six-minute cap, though a
sol otherwise took about 36 s at this factor (the hubless run's second sol: 0:09:19 to 0:09:55). The
story bit `UndergroundDeepScanning_Water` triggered at 0:01:19.96, just before the stall began; that it paused the
game is an inference, not logged. Trains served both hub networks and the depot under the new
code throughout: depot 9036 `CallsFor` 1 → 7 → 13 → 18; hubless junction `StationBig(9702)`
`CallsFor` 1 → 15 → 29 → 43 on default rows, its Metals 45157 → 44157 and Concrete
9404 → 3570 with trains unloading there.

## 8 · HUBLESS

`D.Set(StationSmall(7861), "Metals", "import", 100)` → `ok=true`; two sols ran (`capped=false`,
days 53–54); `D.Clear` → `ok=true`, `saved=nil` afterwards. **`CallsFor` stayed 0 before, during
and after, and its Metals stayed 11300:** no train called on 7861 in this window, so the set row
was never read by the hubless view. What step 7 shows is that the set and clear calls ran on a
live colony without an error; it does not witness the hubless view on a set row. The hubless
view on default rows is witnessed at 9702 (§7).

## 9 · ICON

| image | w × h |
|---|---|
| `resource_accept.tga` | 72 × 62 |
| `resource_storing.tga` | 72 × 62 |
| `elevator_resource_up.png` | 72 × 62 |
| `elevator_resource_down.png` | 72 × 62 |
| `resource_no_accept.png` | 72 × 62 |

All non-zero: every row icon is present on this build.

## 10 · TOOLTIP

`ResourceRolloverText("Metals")`, first 300 characters as printed:

- `StationSmall(2007)` (hub-owned, Export 9), length 220: `Export: trains take stock above the
  selected minimum to the hub. Local drones bring in what nearby storage holds above its Desired
  Amount. A full hub refuses exports.<newline><newline>Slider: 9% of current capacity (10).`
- Depot surface 9036, length 352: `Import: this half gathers it for the cabin: trains (and drones,
  with Drone Access on) bring it here, and each down leg carries it to the underground
  half.<newline>The underground half shows the same word, read-only.<newline>Vanilla elevator's
  word: Underground.<newline><newline>Slider: 21% of curren` (cut at 300).

The ordinary station read is the hub text; the hubless (`local_help`) text and the joining-station
line were not read by this leg.

## 11 · REFRESH

`D.Refresh()` × 100 under `GetPreciseTicks(1000000)`: total 1,109,771 µs, mean **11.10 ms**
(computed outside the game, EF-116), on 19 stations and 2 hubs, game paused. A station-row click
calls it at least once (the A3 snapshot) and `D.Set`/`D.Clear` once more; the per-click figure is
bounded by this colony's size and was not measured as a click.

## 12 · READY: the owner's glance

The game paused with the depot surface half selected (`READY handle=9036`). The push-notification
tool answered "Mobile push not sent (Remote Control inactive)"; the glance steps were given in
the session's chat. The owner's words, verbatim: **"everything looks clean to me"**. Nothing they
did in the game was recorded by the leg.

## 13 · NOT RUN and limits

- Third sol of the first run's main stage (capped, §7); the second run ran three (§15).
- The hubless view on a set row in the first run (§8); covered by the second run at 9702 (§15).
- The hubless tooltip text and the joining-station line in the first run (§10); read in §15.
- Saved Balanced pins: none in the fixture, so none could be shown (§6).
- No figure here speaks to drones, throughput or pixels beyond the owner's sentence.

## 14 · Outside findings (reported, not edited)

- Hub 6430's saved table holds a Metals row for the Elevator Depot surface half (9036). `D.Get`
  reads the depot's own `HubEntry` first, so the row is dormant; the comment in
  `StationRows_40_TrainDistribution.lua` says the hub never stores a depot row, so this is
  data from before that rule or from another path. Not investigated.
- The station tooltip prints `(10)` for a target of 10800: `target / const.ResourceScale` is
  integer division in the engine (EF-116). Display only; not a regression of this change set.
- The DEV-ONLY Workbench mod (`SMR_CommunityOptInPack_Workbench`) was loaded in the standing
  config during this run.

## 15 · Second run: set rows on the hubless junction

Asked by the owner after §§1–14 ("are we good to deploy or should we do a second run?"; the agent
recommended one targeted run; owner: "you can proceed with that"). Same rig, build and save;
manifest `relay_leg2.json`, payload `98_RelayLeg2.lua.txt`, every gate passed before launch and after
disarm; kit `metadata.lua` again restored to HEAD and clean. Launched 16:45:15, log
`Mars.exe-20261022-16.45.52-6aba6e65.log`, the payload quit itself after `END`. Archived complete
after exit: 386 lines; as written (CRLF) 23,949 B, sha256
`17e596e781f51d584ea062ac1a6b2872a6845a93924164301006bd07c34f4790`; LF-normalised 23,735 B,
sha256 `c16bfab3a67f85fe36d02c7e74c0428298b008ff0e1613094903fd7d6c590ce8`; 72 `[RELAYLEG2]` lines.
No save written (the same `find -newermt` lists only `account.dat`, its `.bak`, `steam_autocloud.vdf`).

The stall fix: a popup holds an `XPauseLayer` in `PauseReasons` that game speed cannot lift
(`CommonLua/X/XLayers.lua`, `Lua/UI/PopupNotification.lua`, build 1.1.1.406343). The payload
resumed that layer only, leaving the popup open and choosing nothing: `UNSTALL ... PopupNotification
n=1`. Every 10-second tick read `time_factor=20000` with no pause reason (8 ticks).

| check | logged |
|---|---|
| errors | `smrtk_error_count=0`; `Lua error` 0; `SMRTK_ERROR` 0; no `ERROR <stage>` |
| modules, witnesses | all three active; `WaterFill`, `IsJunction`, `Clear` functions; autosave suspended |
| pick | `StationBig(9702) junction=true`, `HubFor=nil` throughout |
| set | `D.Set` Metals import 100 `ok=true`; Concrete export 0 `ok=true`; `saved=true` |

| | day | `D.calls` | `CallsFor(9702)` | Metals | Concrete |
|---|---|---|---|---|---|
| before set (default/4 each) | 50 | 0 | 0 | 45157 | 9404 |
| sol 1 | 51 | 15 | 1 | 45157 | 9404 |
| sol 2 | 52 | 473 | 23 | 116157 | 5404 |
| sol 3 | 53 | 949 | 45 | 131157 | 4404 |
| after `D.Clear` both (default/4, `saved=false`) | 53 | 949 | 45 | 131157 | 4404 |

`RUN done sols=3 capped=false unstalls=1`. Against the first run's default rows at the same days
(§7: Metals 45157 → 44157, Concrete 9404 → 3570), Import 100 pulled Metals in; Concrete left the
station in both runs, so the Concrete figures show Export 0 does not block outflow but do not
distinguish Export 0 from Default. Trains unloaded at 9702 during the run (ticks show
`Train(2000003078)` `UnloadTrain` there with Metals 3000 aboard).

Tooltips at 9702 after the set, verbatim apart from `<newline><newline>` shown as ` / `:
- Metals (len 740): `Import: trains bring stock from other stations up to the selected amount, a
  share of this station's own store, and take none of that amount away. From a station left at
  Default they bring what the base game would share; set Export there to send everything. Local
  drones may drain this station to zero. / Slider: 100% of current capacity (240). / No hub: these
  settings are kept at this station. Connecting a hub uses its separate settings; disconnecting
  restores these. / This station joins lines: cargo for its other lines passes through the room
  above its number, so its stock reads above the number on the way. At 100 nothing can pass
  between its lines; lower the number to let cargo through.`
- Concrete (len 581): `Export: trains take what this station holds above the selected amount, a
  share of its own store, to accepting stations, and bring nothing for its own use. Local drones
  bring in what nearby storage holds above its Desired Amount. / Slider: 0% of current capacity
  (0). / No hub: ... restores these. / This station joins lines: cargo for its other lines passes
  through the room above its number, so its stock reads above the number on the way.`

Limits: one junction, two resources, three sols; no relay-through figure (cargo passing between
9702's lines) was measured, and at Import 100 the help itself says none can pass. Nothing here
speaks to drones, throughput or pixels.
