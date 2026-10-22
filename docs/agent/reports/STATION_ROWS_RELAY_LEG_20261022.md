# Station rows relay: the unattended in-game leg — 2026-10-22

**Verdict: smoke clean within its reach.** Ran unattended in the game at `e49a4e4` (shipping
`Code/` identical to `3aa5402`: `git diff --stat 3aa5402 e49a4e4 -- Code items.lua metadata.lua`
prints nothing) on `SMRTK_A.sav`, log `Mars.exe-20261022-12.23.59-6aba6e65.log`: errors 0,
depot targets as ruled, rows as saved, icons present, refresh 11.10 ms mean on 19 stations and
2 hubs; the owner glanced and said "everything looks clean to me". Two parts fell short of the
brief and are stated below: the main run reached 2 of 3 sols, and the hubless set row was never
called on (`CallsFor` stayed 0), so the hubless view is witnessed only on default rows.

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

- Third sol of the main run (capped, §7).
- The hubless view on a set row (§8). No claim about a hubless junction with a set row; 9702
  ran on default rows only.
- The hubless tooltip text and the joining-station line (§10).
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
