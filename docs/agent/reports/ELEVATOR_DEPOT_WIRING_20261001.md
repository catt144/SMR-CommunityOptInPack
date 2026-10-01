# Elevator Depot, the wiring (brief 27), 2026-10-01

Build **25579348**: Steam `appmanifest_3215050.acf` `buildid` read this session. The orchestrator ran
`python tools/doccheck.py --emit-fingerprint`; this session did not run doccheck, by the division of
labour. Source: the archived tree
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.406343\Src`, cited below as `406343`. The session started
at OptInPack `48b4e63` and SMR-Assets `642943a`. OptInPack moved to `1972103` during the session; that
commit adds brief 28, which leaves `10_ElevatorDepotDev.lua` to this brief. `tasklist` found no
`Mars.exe` before the first `Code/` write. Executed model: Claude Opus 5.5 (`claude-opus-5-5[1m]`), the
brief's build agent. No writing git command was run; the orchestrator commits the units listed at the end.

**State: built, desk PASS, attended sitting pending.** Nothing below is observed in game.

**Amended the same day (owner ruling, `6dbf705`, spec §11 and brief 27 ruling 3): the surface half owns
the row settings; the underground half's rows are read-only.** The first build landed as `3131ad2`,
`6fa354d`, `0763b2a` with a two-way mirror. This report and the code now describe the one-writer
design: one write path, no reconcile pass, and a panel witness in place of `mirror=ok`. The fixture is
named (`ad01179`): `double hub+elev Built+underground setup`, on the hub network.

## What was built

| file | what |
|---|---|
| `tools/devmods/elevator_station/Code/10_ElevatorDepotDev.lua` | The WIRING section is new: surface-owned rows with the underground's read-only marks, the hourly cabin, Drone Access, the one-pair limit, a half's demolition, the hub's read and the reads. Small hooks were added to the existing look code: `GameInit`/`Done`/`OnDestroyed`, `start_cycle`'s follow branch, `rig.bld`, `LoadGame` and `Report()`. |
| `tools/devmods/elevator_station/tests/wiring_smoke.py` | New desk smoke. It runs the whole dev Lua against a mock world, with integer-only `Min`/`Max`/`Clamp`/`MulDivRound` (EF-116) and a bare-`/` gate on the WIRING section. It also exercises the staged slots. |
| `tools/devmods/elevator_station/tests/80_AgentSlots_depot.lua.txt` | Staged, not loaded: the sitting's SMRTK slots (Scratch and slots 1-6). |
| this report | |

There is no Mod Editor change to the depot mod. Its template, items and `metadata.lua` are untouched
and the code lives in the one existing code file, so the depot needs only a restart. The template's
description still says "no cargo crosses maps yet". That text is `Data/`, it can change only in the
editor, and it was left for the next depot editor session.

## Design calls

| call | why |
|---|---|
| **One state per resource for the pair**, held in vanilla's elevator vocabulary (`bidirectional` / `to_surface` / `to_underground` / `disabled`, `Elevator.lua:192-197` on 406343). Each half derives its station word from the state and its own map: `to_underground` is surface Import and underground Export. | Ruling 3: surface Import = underground Export. A missing row means Balanced, as a missing state means `bidirectional` in vanilla. |
| **One writer: the surface half's rows** (owner, 2026-10-01). `D.SetRow` refuses an underground half. A paired underground half reads the setting from its surface twin, and its own `SMROptIn_depot_rows` is a read-only copy that only the surface's write path rewrites (whole table, every change). A lone underground half reads its copy, which a new surface twin adopts. | The owner: *"to change you must use the surface elevator"*. The copy is what survives a surface demolition (recommendation 2). |
| **The underground rows show; they do not act.** A click there writes nothing and logs `underground rows are read-only; change <res> on the surface Elevator Depot`. A row hook, chained at run time on `sectionStorageRow.OnContextUpdate` as the hub's `45_TrainDistributionUI.lua` does, replaces the row's click hint with "Read-only here: change it on the surface Elevator Depot." and makes its `OnActivate` a no-op. The row still shows vanilla's stock/capacity figures and mark (`Data/XDef/sectionStorageRow.lua:16-32`): **up** = it leaves this half on the cabin, **down** = it arrives here, the Balanced mark, or the no-accept X. | The owner's design. The hover highlight of an active section may remain; only the click and its hint are taken away. |
| **One arrow meaning on both panels: the cabin's direction.** Down for `to_underground` (surface Import: it leaves the surface), up for `to_surface`. That is vanilla's elevator icons and the hub's Import/Export icons at once, so `row_words` now changes only the Balanced mark (the stations' storing mark or vanilla's tick), the words in the infotips and the surface click order. | The underground arrows the owner asked for equal vanilla's elevator marks (recommendation 3). The switch cost nothing to keep. |
| **The underground infotip** states the setting in words ("Arrives here: each down leg brings it from the surface half; trains … take it away from here.", or "Leaves this half…", "Balanced…", "Not accepted…"), both halves' words and vanilla's word, then "Read-only here: to change it, use the surface Elevator Depot." The surface infotip leads with its word and says how the underground shows it. | Owner: *"have its infotip say its current info"*. |
| A surface click cycles the surface word in the hub's order (Balanced, Export, Import, Not accepted); `row_words = "elevator"` uses vanilla's order. | Ruling 2, "as at every station". |
| **Vanilla follows the row, from the one write path.** Not accepted is vanilla's disabled storage on both halves, so trains drain it (`Station.lua:1021-1051`). Drone desires follow the half's word: Import fills like `send` and Export drains like `accept` (`transport_policy`, `Station.lua:964-995`, a vanilla field). **No reconcile pass.** Vanilla's own "apply to all stations" reaches the depot as a method call and only puts vanilla back to the surface row; it never writes the setting. | One writer. A hub Ctrl+click calls vanilla's setter directly and would bypass this; the hub patch below now skips depots in that loop. |
| **The witness replaces `mirror=ok`.** `D.UndergroundPanel(u, s, res)` takes the mark the underground row will draw (vanilla's no-accept X when storage is off, else `GetResAcceptIcon`) and its infotip, and checks both against the surface half's own stored row. `Pair()` prints `u_panel=<shown>(surface says <expected>)` per row and `underground panel: N rows match the surface setting, M differ; read-only copy current/STALE`. Scratch and slot 3 carry it into the sitting. | It can fail: the smoke turns an underground vanilla flag off behind the depot and gets `DIFFERENT`. |
| **First wiring of an old surface half seeds from vanilla.** A resource it had Not accepted stays so; the rest start Balanced. The underground never seeds: its refusals are overwritten by the surface's setting. | The surface owns it. |
| **Per-trip loads (ruling 1).** At departure the cabin takes stock off the origin half with `AddResource(-n)`. At arrival it gives everything that fits, measured by the destination's demand target, with `AddResource(+n)`. These are the train's own writes (`Train.lua:744-831`), including the BlackCube count. What does not fit stays aboard and rides back to where it came from. | Nothing is on either half while the cabin travels, and nothing is ever lost. |
| Loading order on a leg: the carried direction first (`to_underground` going down, `to_surface` going up), then Balanced rows, which move half the stock difference. **Capacity is 42 units a leg, shared by all resources.** | 42 is one vanilla train load (`Train.lua:22`, `max_shared_storage`), a rough start. The owner tunes it live with `Set("cabin_capacity", n)`. |
| **The timer (ruling 5).** A state machine (`at_top`, `down`, `at_bottom`, `up`) runs on `OnMsg.NewMinute` (`DayTime.lua:69`), timed by `GameTime`. The first leg leaves on the hour. Leg 60 game minutes, pause 0, both live (`cabin_leg_minutes`, `cabin_pause_minutes`); a changed value applies from the next leg. While either half is switched off, the cabin waits at the end it reached. | No thread of ours rides a save; the record holds plain numbers. Vanilla's own legs are a game hour (`SpaceElevator.lua:7` `travel_time`, `:194` `SpaceElevatorTripInterval` one sol, `:318-322` `NewHour`). |
| **The cabin art follows the real legs** (`cabin_follows_schedule = true`). The surface cabin rests at its base and sinks through the well on the down leg; the underground cabin waits in the ceiling and comes down to the receiver on the same leg. An unpaired depot keeps the old show cycle. | The owner can see the hourly cabin at a glance. The look itself is brief 28's. |
| **Drone Access (ruling 6)** works through `ShouldAddRequestToCommandCenter`, the hook every drone controller asks (`DroneControl.lua:741-757`). Off, the half's storage requests are refused to any `DroneControl`; maintenance and train-construction requests keep vanilla service. Shuttles pass a map (`LRManager.lua:74`) and are untouched. On, the filter is MapSharedDepot's direction filter (`Elevator.lua:214-243`): an Import half registers demand only, an Export half supply only. A toggle resets the drones on the half's storage requests and re-registers, as vanilla's elevator does (`Elevator.lua:322-325`). | Off, hub drones never service the depot's storage. The train hub is itself a `DroneControl` (`20_TrainHub.lua:209`), so its drones are covered. RC Commanders are drone controllers too and are also kept off. |
| The **Drone Access button** is an `InfopanelButton` added on `DialogOpen` (`InfopanelButton.generated.lua:34-39`). It is placed right of `ToggleLRTServiceButton` by ZOrder (`XWindow.lua:324`, `:722`). Red when off, green when on. **Each half has its own switch; Ctrl+click is a plain click.** | "Beside the existing Shuttle Access one." Drone hubs are per map, so each half's switch is its own. Vanilla's Shuttle Access Ctrl+click covers the same map's depots (`BroadcastAction`), which is this one depot, so a both-halves Ctrl was dropped. If the ordering does not take in game, the button lands at the row's end and still works. |
| **Old saves:** on the first tick after a load, every half re-registers once, so a fixture placed before this brief picks up Drone Access off. | The default is off (ruling 6). |
| **The pair** is the first live depot by handle on each map. Further depots are unpaired extras: no cabin, Balanced to a hub, rows kept. | The owner's fixture may hold more than one depot per map from earlier sittings. |
| **Passengers (rule 7):** no code touches colonists; the depot stays a `Station`. | `LabelsConnectedToStations.Elevator = "all"` (`Building.lua:3843-3850` on 406343, re-derived). |
| **Independence (rule 8):** vanilla's elevator is not read or written. The depot reads nothing of the hub, and the hub reads the depot only through `rawget(_G, "SMRElevatorDepotDev")` (the patch below). With the underground locked or absent, the depot is hidden from the menu. | Stop 1 did not fire. |

## The three recommendations (the owner rules)

**1. The one-pair limit: build-once per map, by code (built this way; recommended).** The depot answers
vanilla's `CanBuildOnlyOnce()` with true once a live depot stands on the map in view. Vanilla then
greys the menu item with its own "You can build this building only once." (`BuildMenu.lua:735-751`)
and closes placement after the first depot (`Construction.lua:210-216`). That gives one depot per map,
which is one pair, with no template change. A `GetAdditionalBuildingLocks` entry hides the depot until
`UIColony.underground_map_unlocked` (`Colony.lua:655-661`); that is vanilla's lock path, and it hides
rather than greys (`BuildMenu.lua:400-408`, `:731`).
*Alternatives:* (b) two templates, surface-only and underground-only, each with `build_once`. This is
vanilla's flag, but it needs a Mod Editor change, a second persisted class name and two menu entries.
(c) Lock-and-hide only, with no greyed message. A placement path that skips the menu, if any exists,
is caught only as a logged unpaired extra. Cost balancing is not built: the template is still instant
and free, and numbers want the owner. Vanilla's Elevator (10 Concrete, 5 Metals, 2 Machine Parts,
`Elevator.generated.lua`) is an obvious first reference.

**2. A surviving half keeps its stock, acts Balanced, and the setting survives in the copy (built
this way; recommended).** On demolition or destruction of either half, the cabin's cargo goes to the
survivor up to its room. The rest becomes a resource stockpile beside it, as vanilla's
`MapSharedDepot:ReturnStockpiledResources` does (`Elevator.lua:89-110`). The cabin resets at the
surface. While unpaired, the survivor tells a hub and drones that its rows are Balanced, so an Import
row does not fill a store that nothing empties, and its infotip says there is no twin.
- **Surface demolished:** the underground survivor keeps its read-only copy and still shows it,
  unclickable. A new surface depot, which has no setting of its own, adopts the copy; the copy is then
  rewritten from it.
- **Underground demolished:** the surface keeps its rows and stays the writer. A new underground depot
  receives a copy at pairing.
*Alternatives:* (b) demolishing one half demolishes both. Vanilla's elevator cannot be demolished at
all (`can_demolish = false`), so there is no vanilla shape to copy. (c) The survivor resets every row
to Balanced, which loses the player's setup on a rebuild.

**3. The vanilla elevator's marks are MODES, not stock state; match the depot's vocabulary to them
(switch built, default left at ruling 2's words).** `MapSharedDepot.resource_storage_states` holds one
of four modes per resource: `bidirectional` (green tick, "ON"), `to_surface` (green up arrow,
"Surface"), `to_underground` (green down arrow, "Underground") and `disabled` (red X, "OFF")
(`Elevator.lua:186-243`). The encyclopedia text says the same: storage on or off, and usage Surface,
Underground or both (`Elevator.generated.lua`). The depot already stores its pair state in exactly
these four.
Under the 2026-10-01 amendment, the underground's fixed arrows (up = leaves this half, down = arrives
here) are vanilla's elevator marks exactly. The depot now draws them, and the matching arrows on the
surface, in both vocabularies. What is left for the owner to rule is words and one mark. I recommend
`row_words = "elevator"`: vanilla's tick for Balanced, "Status: Underground/Surface/ON/OFF" leading
both infotips, and vanilla's click order on the surface, with the station word (Import or Export)
kept in each infotip. One `Set("row_words", "elevator")` shows it in the sitting; making it the
default is the owner's call.

## Persisted names (ban 1)

All are fields on the dev mod's own depot objects (class `SMROptInElevatorDepotDev`). Each tolerates its
absence: an old save loads with Balanced rows seeded from vanilla, Drone Access off and a fresh cabin
at the surface. These rows are ready for `FIX_POLICY.md`'s inventory, which I did not edit; the
orchestrator decides.

| # | exact bytes | kind | written at | read at |
|---|---|---|---|---|
| 20 | `SMROptIn_depot_rows` | table on a depot half: resource id to one of `"to_surface"`, `"to_underground"`, `"disabled"` (`"bidirectional"` is stored as absence). On the surface half, the setting; on the underground half, a read-only copy, written only by the surface's write path (and at pairing), which a new surface twin adopts | `10_ElevatorDepotDev.lua` WIRING: `D.SetRow` (surface only), `seed_rows` (surface only), `D.OnPairChanged` | same file: `D.State` (a paired underground reads its surface), the panel methods, the cabin, `D.HubEntry`, `D.UndergroundPanel`; `tests/wiring_smoke.py` |
| 21 | `SMROptIn_depot_drones` | `true` on a half whose Drone Access is on; absent when off (the default) | same file, `D.SetDroneAccess` | same file, `ShouldAddRequestToCommandCenter`, the button, `D.Pair` |
| 22 | `SMROptIn_depot_cabin` | table on the pair's surface half. Keys: `phase` (`"at_top"`, `"down"`, `"at_bottom"`, `"up"`), `ends` and `leg_ms` (game ms), `cargo` (resource id to amount ×1000), `legs` (count), `started` (boolean) | same file, `cabin_of`, `D.Tick`, `D.HalfGone` | same file, `D.Tick`, `D.FollowTarget`, `D.Pair`; the staged slots |

The state strings and key names inside rows 20 and 22 are contract with their fields. Vanilla writes
of the dev mod's own making (`transport_policy[res]`, vanilla accept flags) are vanilla fields, not new
names. They follow `FIX_POLICY` §3, and the dev mod's description already says to demolish every depot
before removing the mod.

## The hub change the depot needs (APPLIED)

**Applied in `tools/devmods/train_hub/Code/40_TrainDistribution.lua` and
`tools/devmods/train_hub/Code/45_TrainDistributionUI.lua`, under brief 27 (`ad01179` lifts the hub-code
bar for this one change).** The two files carry exactly the diff below. No other hub file changed:
upgrade texts, `Data/`, templates, items and metadata are untouched.

Rule 2 needs the hub to read the depot's rows and never write one. Without this patch, a depot on a
hub network:
- shows the hub's slider and a hub "· Balanced" title on its rows;
- writes a hub row if that slider is dragged;
- is treated as Balanced at its dial by the hub's trains;
- (since the one-writer amendment) has its vanilla storage flag rewritten by a hub Ctrl+click from
  another station, with no reconcile pass left to undo it.

The depot itself still works. Its icon, click and rollover win, because the depot's class methods
override the hub's `Station` wrappers. The cabin and vanilla balancing still move cargo. The fixture
is on the hub network (`ad01179`), so the change had to be in place before batch B. It adds no field
and no persisted name. An old hub row stored for a depot is ignored and is cleared by the
hub's own `D.Reset`. The second `45` hunk is new with the amendment.

Run in the repo after applying, at `fdd54b0` + working tree: `distribution_smoke.py` (22 PASS),
`distribution_ui_smoke.py` (4 PASS) and `station_visuals_smoke.py` (3 PASS) each exit 0, the same PASS
counts as unpatched HEAD. `parsecheck` over the hub's `Code/` reads 8 files with 0 errors, and
`cargo_upgrade_smoke.py` is unchanged (11 PASS, then the owed editor step). These smokes run without the depot
mod, so they cover the hub-alone half of rule 8. The depot-present read is covered on the depot side
(`D.HubEntry` in `wiring_smoke.py`), not inside the hub.

```diff
--- tools/devmods/train_hub/Code/45_TrainDistributionUI.lua
@@ -26,6 +26,8 @@
 local function network(st)
+	-- an Elevator Depot draws its own rows (brief 27); the hub leaves them alone
+	if D.IsDepotStation and D.IsDepotStation(st) then return false end
 	return IsValid(st) and IsKindOf(st, "Station") and D.HubFor(st)
 end
@@ -71,7 +73,9 @@
 		if not broadcast then mode = following[mode] end
 		-- Preserve vanilla's city-wide scope and its own disabled/request-flag path.
 		for _, target in ipairs(broadcast and st.city.labels.Station or { st }) do
-			if not broadcast or target ~= st then
+			-- an Elevator Depot's setting is written only on its surface panel (brief 27)
+			local depot = D.IsDepotStation and D.IsDepotStation(target)
+			if (not broadcast or target ~= st) and not depot then
 				if broadcast and mode == "disabled" and network(target) then
--- tools/devmods/train_hub/Code/40_TrainDistribution.lua
@@ -61,6 +61,19 @@
 	return IsValid(o) and IsKindOf(o, "SMROptInTrainHubBase")
 end
 
+-- Elevator Depot (brief 27, spec section 11 ruling 2): the depot owns its rows and the
+-- hub reads them through its HubEntry; the hub never stores a row for a depot. Absent
+-- depot mod: both answer nil and the hub behaves as before.
+local function is_depot(st)
+	local depot = rawget(_G, "SMRElevatorDepotDev")
+	return depot and type(depot.IsDepot) == "function" and depot.IsDepot(st) or false
+end
+local function depot_entry(st, res)
+	local depot = rawget(_G, "SMRElevatorDepotDev")
+	if depot and type(depot.HubEntry) == "function" then return depot.HubEntry(st, res) end
+end
+D.IsDepotStation = is_depot
+
@@ -126,6 +139,8 @@
 function D.Get(st, res)
 	local hub = D.HubFor(st)
+	local own = depot_entry(st, res)
+	if own ~= nil then return own or nil, hub end
 	local rows = hub and rawget(hub, FIELD)
@@ -146,7 +161,9 @@
 local function effective(st, res, hub)
 	if not hub or is_hub(st) then return end
-	local rows = rawget(hub, FIELD)
+	local own = depot_entry(st, res)
+	if own then return own end
+	local rows = own == nil and rawget(hub, FIELD)
 	local entry = rows and rows[st] and rows[st][res]
@@ -246,7 +263,7 @@
 function D.Apply(st)
-	if saving or baseline or view or not IsValid(st) or is_hub(st) then return end
+	if saving or baseline or view or not IsValid(st) or is_hub(st) or is_depot(st) then return end
@@ -282,6 +299,7 @@
 	if not ready(st, res) or is_hub(st) then return false, "enable this resource at a station" end
+	if is_depot(st) then return false, "the Elevator Depot owns this row" end
@@ -412,6 +430,7 @@
 	rows = rows and rows[st]
+	if is_depot(st) then rows = nil end
 	local defaults = line_managed(self, self.track, st, hub)
```

`D.HubEntry(st, res)` answers `nil` for anything that is not a depot. For a depot it answers `false`
(the hub's own default, Balanced at the dial) or the hub's entry shape: Import is
`{mode = "import", percent = 100}`, so the hub fills it for the cabin; Export is
`{mode = "export", percent = 0}`, so the hub takes everything the cabin brings.

## Evidence re-derived (406343, `rg -n`)

- The brief's `SpaceElevatorTripInterval` and `travel_time`: `SpaceElevator.lua:194` (`DefineConstInt
  ... 1, "sols"`) and `:7` (`default = 1*const.HourDuration`); the leg loop is `:397-401`. Confirmed.
- `LabelsConnectedToStations` is `Building.lua:3843-3850`, with `Elevator = "all"` at `:3848`.
  Confirmed. The brief's "406343" is the right tree.
- `MapSharedDepot` is `Elevator.lua:10-36`, a cross-map store whose four modes are listed at `:192-197`.
  Used for mechanism (the direction filter and stockpile overflow), not storage. Ruling 1 stands.
- The four modes in the hub (`40_TrainDistribution.lua` `D.Set` at `:279-295`;
  `45_TrainDistributionUI.lua:31-43`). Confirmed. The depot carries its own copy of the words and
  icons and needs no hub.
- The depot's Shuttle Access toggle is vanilla's: `Station` is a `StorageDepot` through
  `MultiResourceDepotBase` (`MultiResourceDepot.lua:9`), and `ipBuilding.generated.lua:348` shows the
  button for every `StorageDepot`. This matches SMR-Assets `drone_access_01_shuttle_access_toggle.png`.

## Verification (desk; commands and what they printed)

| command | result |
|---|---|
| `python tools/devmods/elevator_station/tests/wiring_smoke.py` (after the amendment) | exit 0, `wiring_smoke: PASS; HEAD=ad01179e... + working tree; Lua 5.5` |
| the same smoke against nine source mutations (scratch copies) | each exits 1 on its own assertion: no underground copy (`its read-only copy follows`), underground writable (`SetRow on the underground refused`), underground reading its own copy (`stale copy reported`), cargo crossing while travelling (`down leg loads all Import Metals`), Drone Access default on (`off: storage supply refused`), float division (`bare / in the WIRING section`), no vanilla seed (`the surface vanilla Not accepted survives the first wiring`), build-once colony-wide (`none underground yet: buildable`), a witness that ignores vanilla's flag (`the witness can fail`) |
| `python tools/devmods/elevator_station/tests/props_smoke.py` | exit 0, `props_smoke: PASS; HEAD=ad01179e... + working tree; Lua 5.5` |
| `python tools/parsecheck.py --dir tools/devmods/elevator_station/Code` | exit 0, `PARSE: 2 file(s) ..., 0 error(s) [Lua 5.5]` |
| `lupa` `load()` of `tests/80_AgentSlots_depot.lua.txt` | `ok`; 6 `Bind`, 1 `BindScratch`, 3 `Trigger` |
| `python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py` | exit 0, 11 PASS lines, then `OWNER STEP OWED: Mod Editor save for slot 4 and base storage; code_hash remains editor-owned` |
| `python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated` | **exit 1 (FAILED, expected):** `AssertionError: ('Mod Editor regeneration owed', ...)`. The four generated descriptions still hold the long texts, and the carried-in editor save (A1) is what clears this. |
| hub patch applied in the repo: `distribution_smoke.py`, `distribution_ui_smoke.py`, `station_visuals_smoke.py` | exit 0 each; PASS counts 22 / 4 / 3, the same as unpatched HEAD; `HEAD: fdd54b0...` |
| `python tools/parsecheck.py --dir tools/devmods/train_hub/Code` (after the patch) | exit 0, `PARSE: 8 file(s) ..., 0 error(s) [Lua 5.5]` |
| `python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py` (after the patch) | exit 0, 11 PASS, then `OWNER STEP OWED: Mod Editor save for slot 4 and base storage; code_hash remains editor-owned` |
| byte check of the three written files | CR 0 in each (LF only) |

What the mock does not prove: real drone queues and `InterruptDrones`; the panel's look and the
button's position; the underground rows' hint and dead click in the real panel; vanilla trains around the depot; the cabin art's motion; the save file;
`CanBuildOnlyOnce` in the real build menu; and any passenger. All of these are the sitting's.

## The sitting

Smoke depth (spec §10). The owner clicks; the orchestrator reads the log on flush. About five steps a
batch, one prediction a step. Times are game time; abort at 3×. Slots: load the staged file per its
header (it replaces the kit's `Code/80_AgentSlots.lua` for this sitting, so keep the 2026-09-26 file
to restore). Slots 2, 4 and 6 run at Ultra and pause themselves; re-press one after an autosave.
**Fixture (named, `ad01179`):** `double hub+elev Built+underground setup`, on the hub network. The hub
patch is applied before batch B.

**A. Editor save, desk gate, restart, the hub texts**
- A1 Game running at the main menu: **Mod Editor**, open **DEV ONLY - Train Hub (Module B build)**
  (`SMR_TrainHubDev_20260918`), change nothing, **Save the mod**, quit the game. The depot mod needs
  no editor save. *Prediction:* `tools/devmods/train_hub/Code/BuildingTemplate/SMROptInTrainHub6.generated.lua`
  changes, its four `upgradeN_description` lines matching `Data/`.
- A2 Orchestrator: `python tools/devmods/train_hub/tests/cargo_upgrade_smoke.py --require-generated`.
  *Prediction:* exit 0, no `OWNER STEP OWED` line. This must PASS before the restart.
- A3 Load the staged slots, start the game, load the fixture, unpause for one game minute.
  *Prediction:* the log has `[ElevatorDepotDev] pair formed: surface <S> underground <U> rows ...`
  and no `[LUA ERROR]`.
- A4 Select a train hub and hover each of its four upgrades. *Prediction:* the texts read, one line each:
  "+100% Station storage; +100% Train cargo and passenger capacity. Colony upgrade: any hub can switch it." /
  "+100% Train cargo capacity; +25% Train speed. Colony upgrade: any hub can switch it." /
  "+75 ⚡ Production per hub; heats the ground in drone range; trains lose the cold penalty. Colony upgrade: any hub can switch it." /
  "+100% storage in every Train Hub; +19 ⚡ Consumption per hub. Colony upgrade: any hub can switch it."
- A5 Pause; press Scratch (pair read). *Prediction:* `surface=<S> underground=<U>`, `cabin=at_top` (or
  a moving leg if an hour has passed), both halves `drone_access=off registered=0`, `underground_panel=matches`, `copy=current`.

<<SITTING PENDING>>

**B. The panel: surface rows set, underground rows shown read-only (paused)**
- B1 Select the surface depot. *Prediction:* a drone button with a red rim stands right of Shuttle
  Access. Hovering it shows "Drone Access", status OFF.
- B2 On the surface panel, click the Metals row until its icon is the down arrow (from Balanced: two
  clicks, passing Export with the up arrow). *Prediction:* log `row Metals = to_underground
  surface=import underground=export (set on the surface half <S>; underground <U> copy updated)`. The
  hover starts "Import: this half gathers it for the cabin".
- B3 Select the underground depot and hover its Metals row. *Prediction:* the row shows its stock and
  capacity and a down arrow. The infotip starts "Arrives here: each down leg brings it from the surface
  half" and ends "Read-only here: to change it, use the surface Elevator Depot." The click hint line
  reads "Read-only here: change it on the surface Elevator Depot."
- B4 Click the underground Metals row once. *Prediction:* nothing changes on either panel, and the log
  has `underground rows are read-only; change Metals on the surface Elevator Depot`. Then, with the
  underground depot selected, press slot 3: `panel_shows=down surface_says=down infotip_ok=true
  copy_current=true`. The underground panel shows what the surface setting says.
- B5 Console `SMRElevatorDepotDev.Set("row_words", "elevator")`. No slot sets a layout key, which is
  why this is a console line. Hover a Metals row and a Balanced row on each panel, then
  `Set("row_words", "station")`. *Prediction:* in elevator words the infotips lead with "Status:
  Underground."; the arrows are unchanged; Balanced rows show vanilla's tick instead of the storing
  mark. The owner's verdict here settles recommendation 3.

<<SITTING PENDING>>

**C. The hourly cabin, down**
- C1 Select the surface depot; press slot 1. *Prediction:* `added_tenths=200`, and `after_tenths` is
  `before_tenths` + 200.
- C2 Slot 6 (run until the cabin departs). *Prediction:* it pauses at the next down departure within 1
  game hour. `cabin=down`; `aboard_Metals` covers the surface's Metals up to 420 tenths; `s_Metals`
  dropped by that amount and `u_Metals` is unchanged. Nothing crosses while the cabin travels.
- C3 Slot 2 (run until the next arrival). *Prediction:* it pauses within 1 game hour: `verdict=arrived`,
  `legs` up by one, `u_Metals` up by C2's aboard amount, `aboard_Metals=0`, `cabin=up`. Log: `cabin
  arrived underground (leg n) delivered ...Metals=...`.
- C4 Normal speed for one leg (about 30 s real): watch both depots' cores. *Prediction:* the underground
  cabin rises from the receiver into the ceiling; the surface cabin rises out of the well and rests in
  the ring at the arrival.
- C5 Slot 4 with the drone-covered half selected (one game hour). *Prediction:* `drone_access=off`,
  `max_registered=0`, `max_drones_busy=0`. Off keeps hub drones away.

<<SITTING PENDING>>

**D. The hourly cabin, up, and Drone Access on**
- D1 On the surface panel, click Metals three times (Import to Not accepted, Balanced, Export).
  *Prediction:* the log ends `row Metals = to_surface surface=export underground=import`.
  The surface Metals shows the up arrow. On the underground panel Metals shows the up arrow, and its
  infotip starts "Leaves this half". Slot 3 on the underground half reads `panel_shows=up
  surface_says=up`.
- D2 Underground selected: slot 1. *Prediction:* `added_tenths=200` on the underground half.
- D3 Slot 6, then slot 6 again if the first stop is a down departure. *Prediction:* the up departure
  shows `cabin=up`, `aboard_Metals` of at least 200 tenths, and `u_Metals` lowered by it.
- D4 On the drone-covered half, click the Drone Access button, then press slot 4. *Prediction:* the log
  has `drone access <map> <handle> on`, the button turns green with status ON, and slot 4 reports
  `max_registered` > 0. `max_drones_busy` > 0 only if drones have work for that half; registration is
  the deterministic witness. On lets them in.
- D5 Click Drone Access on the other half, then on both halves again to finish off. *Prediction:*
  each click logs one `drone access <map> <handle>` line for that half only; the twin's button is
  unchanged. Ctrl+click behaves as a plain click. Both end off.

<<SITTING PENDING>>

**E. Limits and passengers**
- E1 On each map, open Stations in the build menu. *Prediction:* the Elevator Depot item is greyed with
  "You can build this building only once."
- E2 Owner's eye, Fast speed: a colonist travels by train to the surface depot, walks to vanilla's
  elevator, goes down and boards an underground station, as on 2026-10-01. Slot 5 before and after.
  *Prediction:* the chain runs as before; slot 5 reports `halves=2` and its waiting/riding counts.
  Passengers count as re-verified only if this step was watched.
- E3 SMRTK Saves: Save A. *Prediction:* `SMRTK_SAVE status=OK`.
- E4 Slot 6 to a departure with cargo aboard, then salvage the half the cabin is heading to.
  *Prediction:* log `half gone: <map> <handle> survivor <handle> cargo delivered ... stockpiled ...`.
  The survivor's stock rises; overflow lies as a pile beside it.
- E5 Load A. Salvage the **surface** half, press Scratch, then place a new surface depot and unpause
  one minute. *Prediction:* first `no pair: surface none underground <U>`. The underground panel still
  shows its read-only marks, and its infotip adds "No surface twin: the cabin is idle and this half acts
  Balanced; the setting is kept for the next surface depot." Then `pair formed: surface <new>
  underground <U> rows Metals=to_surface,...`: the new surface adopted the copy, and Scratch reads
  `underground_panel=matches copy=current`. Finish with Load A.

<<SITTING PENDING>>

## What I did not do, and the risks the sitting carries

- **Sitting A defect, fixed in `Data/` only:** the Power Upgrade and Storage Hub texts' U+26A1 rendered as a broken glyph; they now use vanilla's inline `<icon_Power>` (archived 1.1.1.406343 `Lua/Resources.lua:527-531`, `Lua/Buildings/Dome.lua:2177-2179`). That owes one more `SMR_TrainHubDev` Mod Editor save; until then `cargo_upgrade_smoke.py --require-generated` fails.
- **No hub test with the depot loaded.** The hub smokes run without the depot mod; `D.HubEntry` is
  tested on the depot side. The hub reading a live depot's rows is the sitting's (batch B onwards).
- **No `FIX_POLICY.md` inventory edit, no README row, no STATE or checklist edit, no doccheck, no
  commit.** The orchestrator does these by the division of labour.
- **No construction cost or tech gate** beyond the underground unlock (recommendation 1's last line).
- **The template description** still says "no cargo crosses maps yet": a `Data/` change for the next
  depot editor session.
- Unproven in game: `CanBuildOnlyOnce` with the real menu; the button's ZOrder placement; real drone
  queues; vanilla trains balancing around a depot whose stock the cabin drains and fills (without the
  hub, trains treat the depot as any station); the cabin art's motion.
- At the first wiring of an old pair, the surface's vanilla refusals become the setting and any
  underground-only refusal is re-enabled: the surface owns it.
- Batch A is unchanged except A5's witness word (`mirror=ok` no longer exists); D5 was rewritten because
  the both-halves Ctrl+click was dropped.
- A destroyed half that vanilla later rebuilds in place re-pairs on the next minute. That rule is
  derived from the code and not exercised.

## Commit units (for the orchestrator, in order)

First build (landed): `3131ad2` (dev Lua and smoke), `6fa354d` (staged slots), `0763b2a` (this report).
The one-writer amendment:
1. `tools/devmods/elevator_station/Code/10_ElevatorDepotDev.lua tools/devmods/elevator_station/tests/wiring_smoke.py`
   "Elevator Depot dev mod: the surface half owns the rows, the underground rows are read-only marks with a surface-pointing infotip (owner, 2026-10-01); one write path, no reconcile, panel witness; per-half Drone Access; wiring_smoke PASS"
2. `tools/devmods/elevator_station/tests/80_AgentSlots_depot.lua.txt`
   "Brief 27 staged slots: Scratch and slot 3 carry the underground panel witness"
3. `docs/agent/reports/ELEVATOR_DEPOT_WIRING_20261001.md`
   "Brief 27 report: the one-writer amendment (design calls, recommendations 2 and 3, row 20, hub patch's broadcast hunk, batches B, D1, D5, E5)"

Those three landed as `8ba7ad4`, `f682872`, `fdd54b0`. The hub patch:
1. `tools/devmods/train_hub/Code/40_TrainDistribution.lua tools/devmods/train_hub/Code/45_TrainDistributionUI.lua`
   "Train hub dev mod: the hub reads the Elevator Depot's rows and never writes one, and its Ctrl+click broadcast skips depots (brief 27, ad01179); distribution smokes 22/4/3 PASS"
2. `docs/agent/reports/ELEVATOR_DEPOT_WIRING_20261001.md`
   "Brief 27 report: the hub patch is applied (40/45), with its verification"
