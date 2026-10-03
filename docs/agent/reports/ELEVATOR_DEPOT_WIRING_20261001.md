# Elevator Depot, the wiring (brief 27), 2026-10-01

Build **25579348**: Steam `appmanifest_3215050.acf` `buildid` read this session. The orchestrator ran
`python tools/doccheck.py --emit-fingerprint`; this session did not run doccheck, by the division of
labour. Source: the archived tree
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.406343\Src`, cited below as `406343`. The session started
at OptInPack `48b4e63` and SMR-Assets `642943a`. OptInPack moved to `1972103` during the session; that
commit adds brief 28, which leaves `10_ElevatorDepotDev.lua` to this brief. `tasklist` found no
`Mars.exe` before the first `Code/` write. Executed model: Claude Opus 5.5 (`claude-opus-5-5[1m]`), the
brief's build agent. No writing git command was run; the orchestrator commits the units listed at the end.
Orchestrator session that ran the sitting and committed: Claude Fable 5.1 (`claude-fable-5-1`).

**State: built; the attended sitting ran 2026-10-01 (batches A-E, results under each batch). The done-when
items passed in game: Import crosses on the hourly cabin; one word on both panels; Drone Access off keeps hub
drones away (registered 0) and on lets them in (registered 64); the passenger chain was watched end to end.**
Open: the long-title fix's in-game look (a desk fix, cause found), the hub's latent copy of the same fault (reported), and the NOT RUN steps listed under each batch.

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
| **One state per resource for the pair, three settings** (owner, 2026-10-01, sitting C: *"maybe we should cut balanced from this. Make it so the elevator only brings down or sends up"*). The settings are vanilla's elevator vocabulary without its `bidirectional` (`Elevator.lua:192-197` on 406343): `to_underground` (Import: goes down), `to_surface` (Export: comes up), `disabled` (Not accepted). **A row with no stored value is Import** (owner, 2026-10-01, sitting C: *"default them to import since thats how most peoples first build out will be"*), so vanilla storage stays on and Not accepted is stored explicitly. This supersedes the same sitting's first reading, unset = Not accepted. | Balanced is gone, and the cabin only brings down or sends up. An old save's unset rows, which used to mean Balanced, load as Import. |
| **One writer: the surface half's rows** (owner, 2026-10-01). `D.SetRow` refuses an underground half. A paired underground half reads the setting from its surface twin, and its own `SMROptIn_depot_rows` is a read-only copy that only the surface's write path rewrites (whole table, every change). A lone underground half reads its copy, which a new surface twin adopts. | The owner: *"to change you must use the surface elevator"*. The copy is what survives a surface demolition (recommendation 2). |
| **The underground rows show; they do not act.** A click there writes nothing and logs `underground rows are read-only; change <res> on the surface Elevator Depot`. A row hook, chained at run time on `sectionStorageRow.OnContextUpdate` as the hub's `45_TrainDistributionUI.lua` does, replaces the row's click hint with "Read-only here: change it on the surface Elevator Depot." and makes its `OnActivate` a no-op. The row still shows vanilla's stock/capacity figures and mark (`Data/XDef/sectionStorageRow.lua:16-32`): **down** = it goes down (Import), **up** = it comes up (Export), or the no-accept X. | The owner's design. The hover highlight of an active section may remain; only the click and its hint are taken away. |
| **The rows take the hub's station-row shape** (owner, 2026-10-01, sitting B: *"We still need the sliders for target values, and I would like the text to resemble our station ones"*; clarified: the hub's own wording and sliders, verbatim). The title is `T{Untranslated("<resource(res)> · " .. word), context}`, using the hub's words without Balanced: Import / Export / Not accepted (`45_TrainDistributionUI.lua:33-34`, `:206`). The surface rows also carry the hub's slider (Min 0, Max 100, StepSize 1, docked between the left title and vanilla's stock/capacity on the right; `:133-181`), the hub's title fit (`:118-131`), the hub's next-word click hint (`:209-212`, without its Ctrl line, which does nothing on a depot row) and **the hub's panel-scale floor** (`:239-269`, copied after the sitting C defect, in which a long title wrapped, doubled its row and pushed the slider down). The infotip ends with the hub's line "Slider: N% of current capacity (X)." (`:101-102`). Not accepted keeps vanilla's red X and red text (`Data/XDef/sectionStorageRow.lua:16-32`); the slider is disabled there, as the hub does (`:213`). **One word for the pair, the surface's, on both panels** (owner, 2026-10-01, sitting C: *"underground it makes it seem like I am importing rare metals and food to the underground even though thats not what it is"*): Import = goes down, Export = comes up. Underground rows show that word and arrow unchanged, vanilla's stock/capacity, no slider and no click. | The hub's row code is `local` to `45_TrainDistributionUI.lua`, so the depot cannot call it without depending on the hub. It is copied into the depot, with the source lines cited in the code. The only changes are the title fit and the infotip amount, which use integer `MulDivRound` (EF-116) where the hub divides. The scale floor uses its own window marker, so it chains with a hub wrap on the same panel. The applied hub patch keeps the hub's own slider and title off depot rows, so nothing is drawn twice. |
| **The target, and how the depot honours it.** One target per resource, in percent of the surface half's capacity, set by the surface slider. Unset, it is the hub's untouched-row default: the live dial as a percentage (`45_TrainDistributionUI.lua:46-51`). It is the surface half's station target, read as at a hub station: **on Import the surface gathers up to it** (a hub fills the surface half to it), **on Export the surface hands out down to it** (a hub takes only the stock above it). The cabin plays the station's local drones: on an Import row it takes everything gathered on the down leg; on an Export row it delivers all that fits on the up leg, for trains to hand out above the target. The underground half has no slider. Where the cabin loads (Export) it gathers to full; where the cabin delivers (Import) it hands out everything (`D.HubEntry`: a gathering half is an "import" station to the hub, a handing-out half an "export" one). | The hub semantics apply unchanged. Without a hub, vanilla trains ignore every target (they balance by capacity, `Train.lua:862-1043`). |
| **One arrow meaning on both panels: the cabin's direction.** Down for `to_underground` (Import: it goes down), up for `to_surface` (Export: it comes up). That is vanilla's elevator icons and the hub's Import/Export icons at once, so `row_words` now changes only the words in the infotips and the surface click order. | The arrows the owner asked for equal vanilla's elevator marks (recommendation 3). The switch cost nothing to keep. |
| **The underground infotip** leads with the surface's word and says where it is set ("Import (set on the surface Elevator Depot)."). It then gives the flow in words ("Arrives here: each down leg brings it from the surface half; trains … take it away from here.", or "Leaves this half…", "The cabin never carries it…") and ends "Read-only here: to change it, use the surface Elevator Depot." No inverted word anywhere. The surface infotip leads with the same word and says the underground shows it read-only. | Owner: *"have its infotip say its current info"*; one word for the pair. |
| A surface click cycles the hub's order without Balanced: Export → Import → Not accepted → Export. `row_words = "elevator"` uses vanilla's order, which is the same three. | Ruling 2, "as at every station". |
| **Vanilla follows the row, from the one write path.** Not accepted is vanilla's disabled storage on both halves, so trains drain it (`Station.lua:1021-1051`). Drone desires follow the half's word: Import fills like `send` and Export drains like `accept` (`transport_policy`, `Station.lua:964-995`, a vanilla field). **No reconcile pass.** Vanilla's own "apply to all stations" reaches the depot as a method call and only puts vanilla back to the surface row; it never writes the setting. | One writer. A hub Ctrl+click calls vanilla's setter directly and would bypass this; the hub patch below now skips depots in that loop. |
| **The witness replaces `mirror=ok`.** `D.UndergroundPanel(u, s, res)` takes the mark the underground row will draw (vanilla's no-accept X when storage is off, else `GetResAcceptIcon`) and its infotip, and checks both against the surface half's own stored row. `Pair()` prints `u_panel=<shown>(surface says <expected>)` per row and `underground panel: N rows match the surface setting, M differ; read-only copy current/STALE`. Scratch and slot 3 carry it into the sitting. | It can fail: the smoke turns an underground vanilla flag off behind the depot and gets `DIFFERENT`. |
| **Per-trip loads (ruling 1).** At departure the cabin takes stock off the origin half with `AddResource(-n)`. At arrival it gives everything that fits, measured by the destination's demand target, with `AddResource(+n)`. These are the train's own writes (`Train.lua:744-831`), including the BlackCube count. What does not fit stays aboard and rides back to where it came from. | Nothing is on either half while the cabin travels, and nothing is ever lost. |
| Loading on a leg: only the rows that send that way. Import rows load on the down leg, Export rows on the up leg, Not accepted never. **Capacity is 42 units a leg, shared by all resources.** | 42 is one vanilla train load (`Train.lua:22`, `max_shared_storage`), a rough start. The owner tunes it live with `Set("cabin_capacity", n)`. |
| **The timer (ruling 5).** A state machine (`at_top`, `down`, `at_bottom`, `up`) runs on `OnMsg.NewMinute` (`DayTime.lua:69`), timed by `GameTime`. The first leg leaves on the hour. Leg 60 game minutes, pause 0, both live (`cabin_leg_minutes`, `cabin_pause_minutes`); a changed value applies from the next leg. While either half is switched off, the cabin waits at the end it reached. | No thread of ours rides a save; the record holds plain numbers. Vanilla's own legs are a game hour (`SpaceElevator.lua:7` `travel_time`, `:194` `SpaceElevatorTripInterval` one sol, `:318-322` `NewHour`). |
| **The cabin art follows the real legs** (`cabin_follows_schedule = true`). The surface cabin rests at its base and sinks through the well on the down leg; the underground cabin waits in the ceiling and comes down to the receiver on the same leg. An unpaired depot keeps the old show cycle. | The owner can see the hourly cabin at a glance. The look itself is brief 28's. |
| **Drone Access (ruling 6)** works through `ShouldAddRequestToCommandCenter`, the hook every drone controller asks (`DroneControl.lua:741-757`). Off, the half's storage requests are refused to any `DroneControl`; maintenance and train-construction requests keep vanilla service. Shuttles pass a map (`LRManager.lua:74`) and are untouched. On, the filter is MapSharedDepot's direction filter (`Elevator.lua:214-243`): an Import half registers demand only, an Export half supply only. A toggle resets the drones on the half's storage requests and re-registers, as vanilla's elevator does (`Elevator.lua:322-325`). | Off, hub drones never service the depot's storage. The train hub is itself a `DroneControl` (`20_TrainHub.lua:209`), so its drones are covered. RC Commanders are drone controllers too and are also kept off. |
| The **Drone Access button** is an `InfopanelButton` added on `DialogOpen` (`InfopanelButton.generated.lua:34-39`). It is placed right of `ToggleLRTServiceButton` by ZOrder (`XWindow.lua:324`, `:722`). **Its look is vanilla's toggle look** (B1 defect, owner, 2026-10-01): a filled red hex when off and a filled green hex when on. Vanilla bakes the fill into the icon image and swaps it per state, with the rollover colour (`StorageDepot.lua:306-314`, `ToggleLRTService_Update`, archived build 25579348). The plain `drone.png` carries its own dark hex and cannot be filled, so the button uses vanilla's unreferenced filled drone pair `drone_balacing_on` / `drone_balacing_off` (UI.fpk `IconsRemaster/IPButtons`, extracted and viewed). That is a drone glyph inside two arrows, not the full-colour drone picture. **Each half has its own switch; Ctrl+click is a plain click.** | "Beside the existing Shuttle Access one." Drone hubs are per map, so each half's switch is its own. Vanilla's Shuttle Access Ctrl+click covers the same map's depots (`BroadcastAction`), which is this one depot, so a both-halves Ctrl was dropped. If the ordering does not take in game, the button lands at the row's end and still works. |
| **Old saves:** on the first tick after a load, every half re-registers once, so a fixture placed before this brief picks up Drone Access off. | The default is off (ruling 6). |
| **The pair** is the first live depot by handle on each map. Further depots are unpaired extras: no cabin, a plain station to a hub, rows kept. | The owner's fixture may hold more than one depot per map from earlier sittings. |
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

**2. A surviving half keeps its stock, works as a plain station, and the setting survives in the copy
(built this way; recommended).** On demolition or destruction of either half, the cabin's cargo goes to the
survivor up to its room. The rest becomes a resource stockpile beside it, as vanilla's
`MapSharedDepot:ReturnStockpiledResources` does (`Elevator.lua:89-110`). The cabin resets at the
surface. While unpaired, the survivor tells a hub and drones that it is a plain station (the hub's
default row), so an Import row does not fill a store that nothing empties, and its infotip says there
is no twin. Its Not accepted rows stay vanilla-disabled.
- **Surface demolished:** the underground survivor keeps its read-only copy and still shows it,
  unclickable. A new surface depot, which has no setting of its own, adopts the copy; the copy is then
  rewritten from it.
- **Underground demolished:** the surface keeps its rows and stays the writer. A new underground depot
  receives a copy at pairing.
*Alternatives:* (b) demolishing one half demolishes both. Vanilla's elevator cannot be demolished at
all (`can_demolish = false`), so there is no vanilla shape to copy. (c) The survivor resets every row
to Not accepted, which loses the player's setup on a rebuild.

**3. The vanilla elevator's marks are MODES, not stock state; match the depot's vocabulary to them
(switch built, default left at ruling 2's words).** `MapSharedDepot.resource_storage_states` holds one
of four modes per resource: `bidirectional` (green tick, "ON"), `to_surface` (green up arrow,
"Surface"), `to_underground` (green down arrow, "Underground") and `disabled` (red X, "OFF")
(`Elevator.lua:186-243`). The encyclopedia text says the same: storage on or off, and usage Surface,
Underground or both (`Elevator.generated.lua`). The depot already stores its pair state in exactly
these four; since the sitting C ruling it uses three of them, dropping `bidirectional`.
Under the 2026-10-01 amendment, the underground's fixed arrows (up = leaves this half, down = arrives
here) are vanilla's elevator marks exactly. The depot now draws them, and the matching arrows on the
surface, in both vocabularies. The owner has since ruled the row titles to the stations' words
(sitting B). What is left is the infotips: I recommend `row_words = "elevator"`, with "Status:
Underground/Surface/OFF" leading both infotips and the station word kept after it. The click order
is the same in both vocabularies. One `Set("row_words", "elevator")` shows it in the sitting; making it the
default is the owner's call.

## Persisted names (ban 1)

All are fields on the dev mod's own depot objects (class `SMROptInElevatorDepotDev`). Each tolerates its
absence: an old save loads every unset row as Import, Drone Access off, the dial default for
every target and a fresh cabin at the surface. These rows are ready for `FIX_POLICY.md`'s inventory, which I did not edit; the
orchestrator decides.

| # | exact bytes | kind | written at | read at |
|---|---|---|---|---|
| 20 | `SMROptIn_depot_rows` | table on a depot half: resource id to a setting. **Values since the sitting C rulings:** absent = Import (goes down), the default; `"to_underground"` = Import too; `"to_surface"` = Export (comes up); `"disabled"` = Not accepted; any other value reads as the default, Import. A new write stores `"to_surface"` and `"disabled"` and leaves Import absent. Old saves wrote Balanced as absence, so it now reads Import; an old explicit `"disabled"` (the one-writer build's vanilla seed) still reads Not accepted. On the surface half, the setting; on the underground half, a read-only copy, written only by the surface's write path (and at pairing), which a new surface twin adopts | `10_ElevatorDepotDev.lua` WIRING: `D.SetRow` (surface only), `D.OnPairChanged` | same file: `D.State` (a paired underground reads its surface), the panel methods, the cabin, `D.HubEntry`, `D.UndergroundPanel`; `tests/wiring_smoke.py` |
| 21 | `SMROptIn_depot_drones` | `true` on a half whose Drone Access is on; absent when off (the default) | same file, `D.SetDroneAccess` | same file, `ShouldAddRequestToCommandCenter`, the button, `D.Pair` |
| 23 | `SMROptIn_depot_targets` | table on a depot half: resource id to an integer percent 0–100 of the surface half's capacity (absent means the dial default). On the surface half, the slider's targets; on the underground half, a read-only copy written by the surface's write path and at pairing, which a new surface twin adopts | `10_ElevatorDepotDev.lua` WIRING: `D.SetTarget` (surface only, from the slider), `D.OnPairChanged` | same file: `D.Target`, `D.HubEntry`, the row slider and infotip, `D.Pair`; the staged slots (slot 3) |
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

`D.HubEntry(st, res)` answers `nil` for anything that is not a depot. For a lone half or a Not
accepted row it answers `false` (the hub's own default; Not accepted is vanilla-disabled anyway).
Otherwise it answers the hub's entry shape by the half's flow. A half the cabin loads from is
`{mode = "import"}` (the surface at its slider target, the underground at 100), so the hub fills it
for the cabin. A half the cabin delivers to is `{mode = "export"}` (the surface at its slider target,
the underground at 0), so the hub takes what the cabin brings.

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
| `python tools/devmods/elevator_station/tests/wiring_smoke.py` (after the sitting C rulings, Import default) | exit 0, `wiring_smoke: PASS; HEAD=497a7263... + working tree; Lua 5.5` |
| the same smoke against source mutations (scratch copies), each round on the source of its day | sitting C round: an inverted underground word (`one word on both panels: Import = goes down`), the unset default (now: unset not Import, `an unset row is Import, vanilla storage on`; Not accepted stored as absence, `explicit Not accepted, copied, vanilla off`), no scale floor (`the floor clamps a depot panel to 800`); sitting B round: a slider underground, the hub ignoring the target, the underground writing a target; one-writer round: no underground copy, underground writable, underground reading its own copy, cargo crossing mid-leg, drones on by default, float division, build-once colony-wide, a witness ignoring vanilla's flag. Each exits 1 on its own assertion. |
| `python tools/devmods/elevator_station/tests/props_smoke.py` | exit 0, `props_smoke: PASS; HEAD=497a7263... + working tree; Lua 5.5` |
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

*Results, batch A* (orchestrator's notes; log `Mars.exe-20261001-14.22.48-6aba6e65.log`; slots swapped into the
kit at 14:21 with the game closed):
- A1 **PASS.** The `SMR_TrainHubDev` editor save landed: generated template plus metadata version 61 → 62,
  commit `47f2fc6`.
- A2 **PASS.** `cargo_upgrade_smoke.py --require-generated` exit 0, "Generated upgrade slots 1/2/3/4,
  base storage and power match source".
- A3 **PASS.** Log line 419: `pair surface=9036 underground=9041 cabin=up legs=3` (the owner had run past
  an hour). "LUA ERROR" over the log: 0 hits.
- A4 **DEFECT, fixed at the desk.** Each text is one line, in shape, but the ⚡ glyph rendered as a broken box
  in the Power Upgrade and Storage Hub tooltips (owner screenshots 1.png, 2.png). The fix is in `Data/`
  only (vanilla's inline `<icon_Power>`), and its own editor save is still owed (see the risks below).
- A5 **PASS.** Scratch, log 449: `cabin=up`, `drone_access=off` on both halves, `registered=0`,
  `underground_panel=matches`, "19 rows match the surface setting, 0 differ; read-only copy current".
  The cabin was not `at_top` because legs had already run.
- Observation, now moot: every row was Balanced then and carried toward the target (aboard WasteRock 18 units).
  The sitting C ruling cut Balanced.

**B. The panel: station-shaped rows, one word for the pair, set on the surface (paused)**
- B1 Select the surface depot. *Prediction:* the drone button stands right of Shuttle Access as a filled
  red hex (vanilla's off look); hovering it shows "Drone Access", status OFF. Every resource row reads
  `<Resource> · <word>`. An unset row reads "· Import" with the down arrow and an enabled slider, its
  vanilla storage on. A row an earlier build stored as `"disabled"` reads "· Not accepted" in red with
  the red X and a greyed slider. Rows lay out at one height, with no title cut to "...", like a hub
  station panel (the scale floor).
- B2 The surface Metals row already reads "Metals · Import" (the default; if an earlier build stored it
  Not accepted, click twice, passing "Metals · Export"). Drag its slider to about 60 %. *Prediction:*
  `target Metals = <n>% (set on the surface half <S>; underground <U> copy updated)` lines while
  dragging (a click first also logs `row Metals = to_underground word=import ...`). The hover starts "Import: this half gathers it for the
  cabin" and ends "Slider: <n>% of current capacity (<amount>)."
- B3 Select the underground depot and hover its Metals row. *Prediction:* the row reads **"Metals ·
  Import"**, the same word, with the down arrow, its own stock/capacity and no slider. The infotip
  starts "Import (set on the surface Elevator Depot). Arrives here: each down leg brings it from the
  surface half" and ends "Read-only here: to change it, use the surface Elevator Depot." The click
  hint reads "Read-only here: change it on the surface Elevator Depot."
- B4 Click the underground Metals row once, then press slot 3 with the underground depot selected.
  *Prediction:* nothing changes, and the log has `underground rows are read-only; change Metals on the
  surface Elevator Depot`. Slot 3: `word=import title_word=import panel_shows=down surface_says=down
  title_ok=true infotip_ok=true copy_current=true target_percent=<n>`, with no twin word.
- B5 Console `SMRElevatorDepotDev.Set("row_words", "elevator")`. No slot sets a layout key, which is
  why this is a console line. Hover the Metals row on each panel, then `Set("row_words", "station")`.
  *Prediction:* the titles keep the station words; in elevator words both infotips lead with "Status:
  Underground."

*Results, batch B* (first instance, log `Mars.exe-20261001-14.22.48-6aba6e65.log`; then a restart at 15:40 after
`62ca05f`, log `Mars.exe-20261001-15.40.40-6aba6e65.log`, with the station-row build, the filled toggle and an
older staged copy of the slots):
- B1 **DEFECT ×2, fixed.** The drone button stood right of Shuttle Access with hover "Drone Access" OFF, but
  showed a grey hex with a rim only: look rejected, ruling `8b41ece`, fix `730188f`. The rows were bare
  (arrow, name, stock only): ruling `624955f`, fix `34a4ee6` (the station-row shape). The final look was
  checked in batch E.
- B2 **PASS.** Rows set on the surface logged "set on the surface half 9036; underground 9041 copy
  updated" (lines 675-679: MachineParts, Electronics; Metals set earlier).
- B3/B4 **PASS** for the witness: slot 3 on the underground half (line 857) read `panel_shows=down
  surface_says=down infotip_ok=true copy_current=true word=export twin_word=import`. That was the build
  before the one-word ruling; the inverted twin word in it is what ruling `57bac5d` removed. **NOT
  CONFIRMED:** the underground row click itself left no log line.
- B5 **dropped.** Recommendation 3 was settled by the station-words ruling (titles take the stations'
  words).

**C. The hourly cabin, down**
- C1 Select the surface depot; press slot 1. *Prediction:* `added_tenths=200`, and `after_tenths` is
  `before_tenths` + 200.
- C2 Slot 6 (run until the cabin departs). *Prediction:* it pauses at the next down departure within 1
  game hour. `cabin=down`; `aboard_Metals` covers the surface's Metals up to 420 tenths; `s_Metals`
  dropped by that amount and `u_Metals` is unchanged. Every surface row still at the default (Import) loads
  too, sharing the 42-unit capacity; a Not accepted row shows nothing aboard.
  Nothing crosses while the cabin travels.
- C3 Slot 2 (run until the next arrival). *Prediction:* it pauses within 1 game hour: `verdict=arrived`,
  `legs` up by one, `u_Metals` up by C2's aboard amount, `aboard_Metals=0`, `cabin=up`. Log: `cabin
  arrived underground (leg n) delivered ...Metals=...`.
- C4 Normal speed for one leg (about 30 s real): watch both depots' cores. *Prediction:* the underground
  cabin rises from the receiver into the ceiling; the surface cabin rises out of the well and rests in
  the ring at the arrival.
- C5 Slot 4 with the drone-covered half selected (one game hour). *Prediction:* `drone_access=off`,
  `max_registered=0`, `max_drones_busy=0`. Off keeps hub drones away.

*Results, batch C* (log `Mars.exe-20261001-15.40.40-6aba6e65.log`):
- C1 **PASS.** Slot 1 on the surface (line 826): added 200, 250 → 450. The owner also pressed slot 1 on the
  underground half (849): 222 → 422.
- C2 **PASS.** Slot 6 (867-872): `departed down` leg 27, `loaded Metals=42000`, which is the 42-unit
  capacity.
- C3 **PASS.** Slot 2 (888-891): `arrived underground` leg 27, `delivered Metals=42000`, aboard none.
- C4 **NOT RUN.** The owner did not report on the cabin art at normal speed.
- C5 **PASS, run in batch E.** Slot 4 with Drone Access off (log `Mars.exe-20261001-16.20.31-6aba6e65.log`
  line 383): `drone_access=off registered=0`.
- Observation, now moot: up legs carried Food, PreciousMetals and Sugar on Balanced rows below target.
  Balanced was later cut. "LUA ERROR" count: 0.
- The owner's screenshots of the station-row panel led to rulings `57bac5d` (one word for the pair on
  both panels, Balanced cut) and `497a726` (unset rows default to Import); fixes `2471213` and
  `941632e`.

**D. The hourly cabin, up, and Drone Access on**
- D1 On the surface panel, click Metals twice ("Metals · Not accepted", then "Metals · Export"); the
  slider keeps B2's target. *Prediction:* the log ends `row Metals = to_surface word=export`. Both rows
  read **"Metals · Export"** with the up arrow: the surface one with an enabled slider, the underground
  one without. The underground infotip starts "Export (set on the surface Elevator Depot). Leaves this
  half". Slot 3 on the underground half reads `word=export title_word=export panel_shows=up
  surface_says=up title_ok=true`.
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

*Results, batch D* (restart at 16:20, after the last commit `941632e` at 16:17; log
`Mars.exe-20261001-16.20.31-6aba6e65.log`):
- The owner: *"Drones work, import export works"*.
- D1 **PASS** (screenshots `depot_rows_05/06`, SMR-Assets `250d0bf`). The surface sets Export rows ("Food ·
  Export", "Rare Metals · Export") and both halves read the surface's word. Not run as the scripted click
  sequence.
- D2/D3 **NOT RUN as scripted.** No slot 6 up-departure read is in the logs; the up direction rests on the
  owner's words above.
- D4 **PASS.** Slot 4 off (line 383): `drone_access=off registered=0`. Slot 4 on (line 408):
  `drone_access=on registered=64`. "drone access underground 9041 on" (line 344) and "off" (346); the toggle
  was also logged for surface 9036. (The notes' batch D entry says slot 4 was not found in that log; their
  batch E entry gives lines 383 and 408, and this report follows the later entry.)
- D5 **NOT RUN as scripted.** The toggle is logged per half, but nobody read whether the twin was
  unaffected. "LUA ERROR" count: 0.

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
  shows its read-only marks, and its infotip adds "No surface twin: the cabin is idle and this half works
  as a plain station; the setting is kept for the next surface depot." Then `pair formed: surface <new>
  underground <U> rows Metals=to_surface,...`: the new surface adopted the copy, and Scratch reads
  `underground_panel=matches copy=current`. Finish with Load A.

*Results, batch E* (final build `941632e`, log `Mars.exe-20261001-16.20.31-6aba6e65.log`):
- Panels **PASS** (`depot_rows_05/06`): both halves read the surface's word, there is no Balanced, and Drone
  Access shows filled red when off.
- **DEFECT (open, not blocking):** the surface row "Exotic Minerals · Not accepted" truncates to
  "Exotic Minerals · N…" in red, and the row grows to double height with the slider pushed down
  (`depot_rows_06`). The underground's "Exotic Minerals · Import" fits (`depot_rows_05`). Cause and fix
  below, under "The long-title defect".
- E1 **PASS** (`depot_build_once_01.png`): the item is greyed with "You can build this building only once."
  The template description still says "no cargo crosses maps yet"; that needs a depot editor session,
  and brief 28 owns the editor import.
- E2 **PASS.** The owner: *"on 5 I watched the entire process end to end"*. Passengers were re-verified by
  the owner's eye on the final build.
- E3-E5 **NOT RUN** (the survivor steps). "LUA ERROR" count: 0.

**The long-title defect, found and fixed at the desk.** The hub check is done (owner, `depot_rows_07`): on a
hub station, "Exotic Minerals · Not accepted" wraps cleanly to "Exotic Minerals · Not" / "accepted". The
two copies of the row code are line-for-line the same: hub `45_TrainDistributionUI.lua:114-130` (`fit_title`),
`:133-181` (`make_slider`), `:183-217` (`update_row`) against the depot's `fit_title` (`:1116`), `make_slider`
(`:1133`) and `D.DecorateRow` (`:1171`) in `10_ElevatorDepotDev.lua`. They share the same shorten flag, the same 154 width with a
fit, the same two-line height cap, the same docking and margins, and the same text control
(`sectionStorageRow.idSectionTitle`). The title string's bytes are identical (hub `:206`, depot `:1175`
and `:1184`). What differs at run time is the panel's scale. In the screenshots the depot panel renders
about 15 % larger than the hub station's: "Basic Resources" is 222 px against 190 px, and the title boxes
are about 277 px against 240 px. That scale exposes an arithmetic fault in the shared code. The hub writes
`math.ceil(2 * title.font_height * 1000 / sy)` (`:129`, and the same for the width at `:124`), but in
the engine int/int truncates (EF-116), so `math.ceil` gets an already-floored integer. XWindow then turns
`MaxHeight` and the padding into pixels separately through `ScaleXY` (`CommonLua/X/XWindow.lua:766-784`,
archived build 25579348). At scale 1000 every step is exact and two lines fit. At other scales the box
can come out a pixel short, and the shortening label shows one line with "…".
**Fix (depot only):** the ceiling the hub's author intended (`mul_div_ceil`), plus a 2-unit guard for the
native `ScaleXY` rounding, which cannot be read and which the mock emulates as truncation. The guard is
not needed under that emulation, but a third line would need about 35 units. `wiring_smoke.py` runs the
hub's own `fit_title`, read from the hub file with the engine's integer division, beside the depot's on
116 cases (four titles at scales 800-2200), and scales both boxes to pixels by truncation. The depot's box
holds two lines and the widest word at every scale. The hub's fits at 1000, which matches
`depot_rows_07`, and falls short in 44 cases. Restoring the hub's floor in the depot makes the smoke fail
at scale 1050 ("the depot box loses a line or a word").
**Reported, not fixed:** the hub has the same latent fault. A hub station panel drawn at a scale other than
1000 would shorten long titles the same way. The fix is the same `mul_div_ceil` in `45_TrainDistributionUI.lua`.
Owed in game: one look at the depot's surface "Exotic Minerals · Not accepted" row after a restart.

## What I did not do, and the risks the sitting carries

- **Sitting A defect, fixed in `Data/` only:** the Power Upgrade and Storage Hub texts' U+26A1 rendered as a broken glyph; they now use vanilla's inline `<icon_Power>` (archived 1.1.1.406343 `Lua/Resources.lua:527-531`, `Lua/Buildings/Dome.lua:2177-2179`). That owes one more `SMR_TrainHubDev` Mod Editor save; until then `cargo_upgrade_smoke.py --require-generated` fails.
- **Every unset row is now Import:** vanilla storage stays on, and from the first hour the cabin carries
  every unset resource down. A vanilla refusal on a never-wired depot is not kept (only an earlier
  build's explicit `"disabled"` is); the owner sets Not accepted per row.
- **The slider's look in the real panel is unproven:** the mock checks construction, docking and
  values, not pixels. The hub's panel-scale floor is now copied (sitting C defect); its effect on
  the real panel is the sitting's.
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

## OI-38 sitting, 2026-10-02 (the owner's words; no log read)

On the depot's final build (brief 28 closed):
- C4 **PASS.** *"Cable looks smooth and natural at all speed."*
- D5 **PASS.** *"drone access works as expected when on one is on and the other is off"*
- The hub tooltips' power icon **PASS.** *"power icon looks correct."*

Still owed on OI-38: E3-E5 (the survivor steps), the scripted up-leg read, and the long-title
fix's glance (`1122115`).

Batch E, same sitting (log `Mars.exe-20261002-00.07.14-6aba6e65.log`, read after the game closed;
"LUA ERROR" count 0):
- The long-title fix (`1122115`) **PASS** in the owner's word ("1 is correct").
- E3 **PASS**: `SMRTK_SAVE ... slot=A status=OK`.
- E4 **PASS** (owner: "3. was correct"): `half gone: underground 9041 survivor 9036 cargo delivered
  PreciousMetals=16000,Sugar=26000 stockpiled none`, then `no pair: surface 9036 underground none`.
- E5 **FAIL, stopped at its first check.** After Load A and the surface half's salvage the log has
  `half gone: surface 9036 survivor 9041 cargo delivered Food=1000,PreciousMetals=4000,Sugar=2000
  stockpiled none` and `no pair: surface none underground 9041`, as predicted, and the underground
  half kept working as a plain station, which the owner read as *"it just continues opperating
  normally"*. **DEFECT (open):** the underground panel's infotip never showed the predicted "No
  surface twin: the cabin is idle and this half works as a plain station; the setting is kept for
  the next surface depot." (owner: *"This messaged didn't come up so I stoped testing at that
  point"*). The new surface depot's placement and adoption of the copy were not run.

## OI-38 final up-leg read - PASS, 2026-10-03

Owner sitting, orchestrator ruling `ac634ca`: final B1 reads UP departure,
62166 raw Metals aboard, then arrival and the same 62166 on the surface; the
622 trigger fields use rounded tenths. Trace was ON before reads. The stock
setup used underground storage CheatFill before arming, not a retry. OI-38 is
closed. The archived live-log prefix, exact lines, controls and map-change stream
cleanup are in [the final battery report](TRAIN_FINAL_BATTERY_20261002.md#b1-in-p---pass-2026-10-03).
