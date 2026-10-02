# Bug report for the Relaunched Fix Pack: a train's food cargo spoils in transit, but its unload hands over the booked amount

Written for the fix pack's owner and its triage. Source: Opt-In Modules brief 34b, Fix 3 (owner
ruling 2026-10-02, `9f217b5`: if the cause is vanilla, no clamp in this mod and a full report
here). Executed model: Fable 5.1 (`claude-fable-5-1`).

**The defect in one line.** A train carrying Food or a delicacy loses a few percent of it in
transit, but the cargo it booked for its destination is not reduced, so the station it unloads
at is credited the booked amount while the train gives up only what it still carries: one or more
units of food appear from nothing at every affected unload.

**Build.** Surviving Mars: Relaunched 1.1.1.406343 (the newest log says `Build version:
1.1.1.406343`, Lua revision 406343), installed build fingerprint 25579348. Source lines below were
read on the archived 1.1.1.406343 tree (`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src`).

**How to reproduce.**

1. Any colony with trains hauling Food (or Sugar, Herbs, Bread) between stations. Let a train
   load food and travel or wait at a station for long enough to cross its once-per-sol update
   (in the witnessed sitting the drop landed on two trains in the same game hour, 18:00).
2. Read the train's `stockpiled_amount[res]` and the sum of its `assigned_resources[*][res]`
   after that hour: the carried amount is a few percent below the booked amount, rounded to whole
   units (4 percent, `g_Consts.FoodDecay`).
3. Let the train unload. The station's supply request rises by the booked amount; the train's
   carried amount floors at zero. Station gain minus train loss is the spoiled units.

**Evidence, log `Mars.exe-20261002-15.30.19-6aba6e65.log`** (brief 33's crossing witness, which
brackets every `UnloadAll` and compares the train's cargo change with the station's stock change):

```
[SMRTK] SMRTK_DUMP call=UnloadAll ... resource=Food  route=R1 size=1 station=SMROptInTrainHub6(6430) station_delta=13 station_stock=815 train=Train(2000002659) train_delta=-12 game_time=35860002
[SMRTK] SMRTK_DUMP call=UnloadAll ... resource=Sugar route=R1 size=1 station=SMROptInTrainHub6(6430) station_delta=17 station_stock=826 train=Train(2000002659) train_delta=-16 game_time=35860002
```

The same witness bracketed every `LoadResourceForStation` of that train and logged no load
mismatch, so the train had received exactly what its source gave.

**Evidence, log `Mars.exe-20261002-17.41.30-6aba6e65.log`** (brief 34b's train cargo trap: log-only
wrappers on `Train:UnloadAll`, `Train:LoadResourceForStation` and every Lua writer of a train's
cargo table (`MultiResourceCubeVisuals.AddResource`, `SetStoredAmount`, `ClearAllResources`,
`ReturnStockpiledResources`, `DroneLoadResource`, `DroneUnloadResource`), plus a poll every 500
game ms comparing each train's cargo with the writes attributed since the last poll):

```
[SMRTK] SMRTK_ACTION action=slot_8 ... bracketed_writes=293 unbracketed_writes=0 unattributed_changes=3 polls=693 ...
[SMRTK] SMRTK_DUMP after=101 at_station=false attributed=0 before=105 command=GotoStation delta=-4 game_time=35820404 ledger=trap leg=unattributed_change resource=Food  station=StationSmall(10650) train=Train(2000001850)
[SMRTK] SMRTK_DUMP after=16  at_station=true  attributed=0 before=17  command=LoadTrain   delta=-1 game_time=35820404 ledger=trap leg=unattributed_change resource=Sugar station=StationBig(7873)    train=Train(2000002659)
[SMRTK] SMRTK_DUMP after=12  at_station=true  attributed=0 before=13  command=LoadTrain   delta=-1 game_time=35820404 ledger=trap leg=unattributed_change resource=Food  station=StationBig(7873)    train=Train(2000002659)
```

What these three lines establish:

- No Lua writer touched the cargo (0 unbracketed writes over 693 polls, with 293 bracketed writes
  as the control that the wrappers were live), yet three trains' amounts dropped in one poll
  window. The window [35819904, 35820404] contains the game-hour boundary 35820000 (hour 18 of
  sol 49). One drop set in about 11.5 game hours of watching 17 trains: a once-per-sol event at a
  train-specific hour, not an hourly one.
- The drops are `CalcResourceSpoilage` arithmetic (`Lua/Spoilage.lua:17-34`): 4 percent of the
  stored amount, the fraction rounded to a whole unit at random. 105 Food gives 4.2, dropped 4;
  13 Food gives 0.52, dropped 1; 17 Sugar gives 0.68, dropped 1. Train 2000002659 carried exactly
  13 Food and 17 Sugar in both logs, and the first log's unload gain was exactly 1 and 1.
- The spoilage reaches trains from outside the Lua tree. Every Lua caller of
  `CalcResourceSpoilage` or `FoodDecay` is a building path (`StorageDepot.lua:126`, `:1329`,
  `HasConsumption.lua:132`, `RecipeProductionBuilding.lua:60`, and `Spoilage.lua:66-91`'s daily
  pass over the `ResourceStockpile` label and map `ResourcePile`s); a Train joins only the `Train`
  label (`Units/Train.lua:113`), is not a `ResourceStockpile` (`ResourceStockpile.lua:74` is the
  only adder) and has no supply requests. The Opt-In Modules' own spoilage file replaces
  `Station:SpoilStoredResources` with a no-op and never touches a train; the fix pack has no
  spoilage code (grep: none). Whatever spoils train cargo is engine-side or in a Lua file the
  archived tree does not carry.

**Why the unload then duplicates.** `Train:UnloadAll` (`Units/Train.lua:787-831`) walks
`assigned_resources` and hands each booked entry over whole: `unload_cargo` (`:779-785`) does
`station:AddResource(amount)` then `train:AddResource(-amount)` with the same booked `amount`. The
train's writer, `MultiResourceCubeVisuals.AddResource` (`Buildings/MultiResourceCubeVisuals.lua:
422-435`), floors at zero and never checks the booking, so a train that carries 12 with 13 booked
loses 12 and the station gains 13. Nothing in the spoilage path reduces `assigned_resources` or the
destination demand's reservation (`RequestAssignUnit` at `:774`).

**Mods present.** The sitting ran with the Relaunched Fix Pack (45/45 fixes), its TestKit and the
Opt-In Modules (Station Rows, Train Hub, Elevator Depot) loaded, on the owner's save "Double
Hub+elev Built Under2". **Not tested with the Opt-In Modules off.** Nothing in either mod writes a
train's cargo or spoils one; the Opt-In hub receives the unload through vanilla's `UnloadAll`
unchanged (its wrapper takes the plain path at a hub).

**Impact.** Small but unbounded: every unload of food cargo that spent a sol boundary aboard
creates spoilage's worth of resource from nothing (one to several units per resource per unload).
Resource totals drift upward; the station's request reservation for the missing units is
released by the unload, so no request is left dangling.

**Candidate fix (for the fix pack).** At the top of `Train:UnloadAll`, before the booked entries
are walked, reconcile each resource's bookings to what the train carries: while the sum of
`assigned_resources[*][res]` exceeds `stockpiled_amount[res]`, reduce the largest booking by the
difference and `RequestUnassignUnit(dest.demand[res], train, difference, false)` for it (the same
call vanilla makes when it re-books at `:764`). The station then receives exactly what leaves the
train, and the spoiled units become a short delivery instead of a gain. A narrower alternative is
to apply the same spoilage to `assigned_resources` wherever the engine spoils the cargo, but that
site is not in the Lua tree, so the unload-side reconcile is the one a mod can reach.

**Reproduction aids.** The trap and witness slots are in the Opt-In TestKit staging file
`tools/trains/hub/tests/80_AgentSlots_34b.lua.txt` (slots 7 and 8) and brief 33's
`80_AgentSlots_crossing.lua.txt`; both are log-only.
