# Drone priority bands 4–5 with a clean revert — the research-and-design report (2026-09-01)

**Job:** one-off `prompts/BANDS_CLEAN_REVERT.md` (consumed by this commit; recover with
`git show ba6c3b7:docs/agent/prompts/BANDS_CLEAN_REVERT.md`). Written at opt-in `ba6c3b7` /
fix pack `c337e5c` / TestKit `832568e`, Src build `1.0.7.396349` (`EF-014`), desk only —
**no module built or changed, no persisted string touched, no save loaded, no probe run**
(`PROBE SWEEP: clean`). The D06 design decision stays the owner's (fix pack
`prompts/DRONE_PROJECT_PROMPT.md` §3); this report changes its inputs and recommends in §7.

**Provenance words, used on every claim:** **SOURCE** = read at Src `file:line` (or a
public Haemimont drop, named as such) · **MEASURED** = a recorded log/console reading with
its date · **INFERRED** = follows from SOURCE/MEASURED by an argument written out here ·
**IDEA** = unproven. **FINDING** and **IDEA** are kept apart in every sentence.

> ⚖️ **Verdict, in the prompt's required form (§7 has the reasoning):**
> **YES IF — mechanism V ("view tiers": the elevated requests are handed to the C matcher
> in transient mod-built view tables, in tier order, before the hub's real tables) passes
> every rubric row from citations except two cells that need a running game: E-4 (a
> mod-built view is honoured by `Request_FindTask`) and E-8 (a wrapper-substituted pairing
> is claimed and executed like a matcher-chosen one).** Bands 4–5 **as persisted data in the
> real hub tables** (option 1) fail R3 and R7 by measurement (§9 stranding) and only the
> layer-1 tear-down the owner declined would rescue them — and Src now shows even that
> cannot hold its invariant on the autosave path (§4.1.2, delta 15). Option 2 reverts clean but is
> not bands 4–5 (R10), and its natural implementation — a class-level
> `GetPriorityForRequest` — fails R3 through a route the record did not have (EF-069).

---

## 1 · The problem, compressed

`Opt_DroneOverhaul` (D06) v1 was measured inert (hauling = 88 % of repair time, v1 exempts
hauling); the owner ruled a rebuild 2026-07-31 as a priority-band scheme: **5** = malfunctioned
life-support producers + the grid/dome tier vanilla already elevates, **4** = every other
malfunctioned building, **3/2/1** = the player's supply arrows (default 2), **0** = depots.
Q1 (07-31) MEASURED the C matcher consuming band-4 work and haul legs on a NEW game. Three
constraints stand (`DRONE_PRIORITY_SYSTEM.md` §8–§10): **Q2** hub queue tables are persisted
and allocated once at construction, so a widened bound over an un-topped-up save nil-indexes
in every `FindTask`; **§9** a widened save loads into vanilla silently but strands anything
filed at 4/5 and the heal path (`DepositsSpawned`) expires on a fully-scanned map; **§10**
`DroneControl:RemoveBuilding` loops a file-local pinned at 3, so a routine re-registration
duplicates band-4 entries (measured `4 → 6`, n=1). The owner wants the bands **and** a
module that cleans up after itself: toggle OFF = vanilla instantly; disable/uninstall = a
save that loads in vanilla with no errors, no stranded work, no orphaned data, no captured
frame, no closure, nothing a second mod has to fix; no new game required.

---

## 2 · Part A — the evidence delta since 2026-07-31

One line each: the fact, its source, what it changes for options 1 / 2 / 3.

1. **EF-023 (07-31, amended 08-13) — capture is value-reachability (a/b/c), and the tail-call
   question is CANCELLED as unfalsifiable** (`FIX_POLICY` §3a layer 2). ⇒ E-2 of the brief is
   REFUSED, not designed (§5). Equal for 1/2/3: every candidate must sit on synchronous seams.
2. **F86 Site 2 repaired + PT-58 (08-01): the module has no capturable frame** — `FindTask`
   and `CleanUnreachables` are both synchronous. ⇒ the CODE half of uninstall is already clean
   for any design that stays on those seams; only DATA residue is at issue. Equal for 1/2/3.
3. **EF-024/028/030 (07-31, 08-01): `SaveGameStart`/`SaveGameDone` reach mods, cover autosaves.**
   ⇒ tear-down-on-save is implementable — **but** `SAVE_SAFETY_REDESIGN.md` §6.3 / `FIX_POLICY`
   §3a: *"LAYER 1 IS NOT TO BE BUILT. The owner declined it explicitly … Do not propose it again
   without new evidence that Tier 3 causes real harm."* ⇒ option 1's uninstall remedy by
   tear-down is an owner question (§6, ask B), not a design choice; and **new SOURCE today
   weakens it further** (delta 15).
4. **EF-029 (08-01): `CreateGameTimeThread` defers.** ⇒ a load-time top-up must run inline in
   the `OnMsg`, never in a spawned thread. Option 1 only.
5. **EF-053 (08-12): `AllMapsForEach(true, "DroneControl", …)` reaches every hub, rocket and
   rover (19 vs 13 concrete); `RocketBase` walked 0 on a colony with 6 rockets.** ⇒ option 1's
   top-up and any OFF/uninstall sweep is one walk; a rocket leg must not be named `RocketBase`.
6. **EF-054 (08-12/24): inter-mod order is the user's enable order.** ⇒ R11 — any wrapper on
   `FindTask` must chain and be order-independent (the v1 wrapper already is). Equal.
7. **EF-058 scope clause (08-19): a patch installed at file scope propagates through flattening.**
   ⇒ one classdef write on `TaskRequestHub` reaches the 48 `FindTask` carriers (the c48
   instrument needed 48 runtime patches because it was installed after `Autorun`). It does
   **not** retire §6 landmine 4 — it makes it worse (delta 14).
8. **EF-059 (08-16): the matcher's supply pairing honours class flags (`rfStorageDepot`) over
   distance, and C48 shows over bucket** (a p1 bush beats a p2/p3 depot, 479/479). ⇒ bands act
   on the demand/work side only (which job is served first), never on which supply feeds it.
   Bounds what any band design may claim. Equal.
9. **EF-060 (08-16): `FindSupplyRequest`/`FindDemandRequest` hand `ignore_flags`/`required_flags`
   straight to C; 25,184 `FindTask` calls per 10 game-hours at 3×; substituted pairings must be
   vanilla-legal requests.** ⇒ candidates V and P (§4.2) have a sanctioned engine finder for the
   haul leg; the per-call budget is "one table read on the empty path".
10. **The standalone split (08-12) and 09-01 ruling: this mod is its own product.** ⇒ the 07-31
    "relocate to a standalone" consequence is spent; "requires a new game" is a shipping shape
    the owner accepted, but this job's R4 forbids it, and no candidate here needs it.
11. **Save Rescue (D13, tested 08-14) exists and detects by a fixed name table only — no queue
    shape is catalogued** (`D13_EXPOSED_SET.md` §10.2, 6b/6c "never by pattern"). ⇒ any
    residue in a hub's queue tables would require the Rescue to learn a new detection KIND ⇒
    fails R7 by construction. Option 1 only.
12. **L3/L2/L8 (08-31): L3 is lexical; a write at an integer key of a vanilla table has no name
    to census** (`L3_SAVE_FOOTPRINT.md` §3, §7 "a persisted name survives iff its carrier is
    vanilla's"). ⇒ R5's "l3 still reads exactly the five" is necessary, never sufficient, for
    any key-4/5 design; adjudication is by hand. Option 1 and 3-with-top-up.
13. **EF-066 (08-24): identity checks are valid on plain methods.** ⇒ the harness wiring proof
    for a `FindTask` wrapper is a sound R9 witness. Equal.
14. ⭐ **NEW today, SOURCE — vanilla writes a class's `GetPriorityForRequest` onto every
    no-maintenance building instance, and class-table functions are not permanents**
    (`RequiresMaintenance.lua:94`; `persist.lua:157-165`; filed as **EF-069**). ⇒ option 2's
    natural shape (class-level override) is copied INTO SAVES BY VALUE by vanilla itself —
    route (c) of EF-023 — for every no-maintenance building built while the mod is installed.
    §6 landmine 4 said "not a hazard for maintenance work"; it is the R3 hazard for the whole
    override family. Options 2 and 8 must re-file by table surgery instead.
15. ⭐ **NEW today, SOURCE — autosave and quicksave do NOT pause game time, and there are at
    least four yields between `Msg("SaveGameStart")` and `EngineSaveGame`**
    (`Savegame.lua:1043` → `:337-344` two `WaitThread`s → `:368` `AsyncStringToFile` →
    `:1010-1023` `WaitRenderMode` → `:862`; `SilentSaveScreen.game_blocking = false`,
    `CommonLua/Classes/XDef/SilentSaveScreen.generated.lua:20`; only the manual non-silent
    `SaveGame` opens a `game_blocking` screen, `LoadingScreen.lua:57-60`). ⇒ a tear-down
    invariant set in `SaveGameStart` can be violated by a drone thread before the walk. Kills
    the tear-down candidate on its own terms (§4.2 T).
16. ⭐ **NEW today, MEASURED-then-INFERRED — the C matcher reads the `const.TaskRequest`
    group bound; it does not walk the keys it is handed.** The recovered v1 experiment
    (TestKit `f617576:Code/97_Q1Q2_PriorityBands.lua:88-93, :104-110`) widened ONLY
    `const.TaskRequest.MaxBuildingPriority` and left `const.MaxBuildingPriority` at 3, and
    `Request_FindTask_C` threw `attempt to index a nil value` at `[C](-1)` on `-1..3` tables
    (MEASURED 07-31, §8). A walk over existing keys (`lua_next`) or over `1..#t` cannot index a
    key that is absent; therefore C iterates an explicit range whose upper bound came from
    outside the tables, and the only external value that changed was the group. Corroboration
    (SOURCE, historical): Haemimont's own Lua mirror of the matcher in the 2018 public drop
    (`HaemimontGames/SurvivingMars` Spirit, `Lua/Buildings/DroneHub.lua:441-621`,
    `for j = MaxBuildingPriority, -1, -1 do … local index = requests.index or 1 …`, with a
    debug assert that C and Lua agreed). Open: **at call time or cached at `ClassesPreprocess`**
    — E-4(ii). ⇒ option 3's "shadow view at keys 4/5 with the const at 3" is dead (C would
    never look at 4/5); option 3 survives as V-a (keys ≤ 3, tier order by pass) or V-b (keys
    4/5 under a per-call bound flip, if call-time).
17. **NEW today, SOURCE — the request userdata's priority field is never written by Lua for
    hub-filed maintenance requests.** `_InternalAddRequest` calls `request:SetPriority(p)`
    (`TaskRequest.lua:313`) but `DroneControl:AddBuilding` never does (`DroneControl.lua:685-718`);
    maintenance requests are created before connection (`TaskRequester:GameInit :61-66` creates,
    then connects) so `AddRequest :133` loops an empty `command_centers` and `_InternalAddRequest`
    never runs for them. ⇒ C derives a request's band from the queue key it is found under, not
    from the userdata (consistent with 16); and a design that re-files through
    `_InternalAddRequest` writes a value into persisted C-side userdata that vanilla's path
    never touches — avoid it or use only vanilla-legal values.
18. **NEW today, SOURCE — the persist walk does not descend into class tables, `_G`, or the
    mod env** (`persist.lua:61, :157-165`; `Mod.lua:1643`): a table held only in a mod file's
    local upvalue of a function stored in a class table is unreachable. ⇒ R5 for the view
    tables of candidate V fills from source: no route to the save exists.
19. **NEW today, SOURCE — `LRManager` (shuttles) keys its queues by resource, not priority**
    (`LRManager.lua:12-41, :51-88`). ⇒ no band design touches shuttle queues; shuttles read hub
    `deficit_table` via the C `Request_UpdateDeficits` (`DroneControl.lua:121-123`), which is a
    fourth C consumer of the hub tables (R4/R11 for option 1).
20. **NEW today, SOURCE — a fourth `GetPriorityForRequest` override exists**:
    `RCTransport.lua:217-223` returns `-1` for the transport's own supplies. §4 of
    `DRONE_PRIORITY_SYSTEM.md` counts three; corrected in the fix-pack commit. No design impact.
21. **NEW today, SOURCE — `RCRover.lua:702` carries a second file-local `MaxBuildingPriority`,
    used only by `DebugCheckIfAllQueuesAreEmpty :714-731`, whose callers at `:733-741` are
    inside a `--[[` block.** Inert; recorded so §10's "the one file-local" stays true in effect.
22. **Prior art (web, 2026-09-01):** no published mod widens the range or overrides
    `GetPriorityForRequest`; ChoGGi's "Drones Use Nearest Waste Dump" wraps `FindDemandRequest`
    (freeze reports); "Smarter Drones" replaced the finders in Lua and rotted into a 150 GB log.
    **The devs themselves shipped and removed an urgency mechanism**: 2018 `RequiresMaintenance`
    had `maintenance_request_is_highest_prio` → `GetPriorityForRequest` = max +
    disconnect/reconnect (Spirit drop `:45, :81-87, :382-388`), removed 2018-05 with a
    `SavegameFixups` pass that `rawset` the method on every object (public
    `SavegameTempCompatibilityFixes.lua:595-601`) — the field survives in our Src as
    `RequiresMaintenance.lua:53` "save compat with rev 225026 saves". ⇒ precedent for option
    2/8's SHAPE and for delta 14's hazard, in the devs' own history.
23. **Unfreeze (owner 08-31, checklist 87):** design + playtest work may resume, A/B per change.

**Is there a delta? Yes, and it points one way.** Nothing since 07-31 opened a route to
*bands 4–5 as persisted data* with a clean revert — deltas 11, 12, 15 and 16 closed the last
ones. What opened is the **transient-view** route (16 + 18 + 9 + 17 together), which delivers
the ordering the bands are for without a 4 or a 5 ever entering a save.

---

## 3 · The rubric (from the brief §2), and the routes every table cites

| row | question | pass condition |
|---|---|---|
| R1 | Mod Options toggle OFF | byte-vanilla on the next call; nothing left elevated |
| R2 | `SMROptInPack_Disabled` veto | as R1 (file-scope installers hook before `Register`, `EF-002`) |
| R3 | Mod-Manager disable / uninstall, save made with bands ACTIVE | vanilla load: 0 `[LUA ERROR]`, no missing-permanent that matters, no captured frame, no closure on an object, no request stranded in a key vanilla never iterates, no widened table vanilla could index-nil on |
| R4 | existing saves (hubs, rockets, rovers built under vanilla) | works without a new game; any top-up is safe and precedes the first `FindTask` |
| R5 | persisted footprint | ZERO new persisted names (ban 1); `l3_save_footprint.py` still reads five; a marker fails |
| R6 | duplicate leak (§10) | closed, and by what |
| R7 | Save Rescue | nothing for it to do |
| R8 | patch-rot exposure | wrapped vs replaced; hot-path cost |
| R9 | flattening | file-scope install, proven on live instances |
| R10 | the design's DISTINCTION | 5 vs 4 vs player-3 still distinguishable to the matcher |
| R11 | interactions | F77, D09, fix-pack wrappers, rockets/rovers/shuttles on the same seams |

**Routes cited below, re-derived at Src today (SOURCE unless marked):**

- **Bounds.** `CommonLua/TaskRequest.lua:16-18` module locals; `:21-32` `OnMsg.ClassesPreprocess`
  re-reads `const.TaskRequest.{Min,Def,Max}BuildingPriority` (the group EXISTS at runtime and
  carries 3 — MEASURED 07-31, `DRONE_PRIORITY_SYSTEM.md` §1 correction; a Src-only sweep finds
  no definer, so it lives in `Data.fpk` or C). `:242-256` `Init` allocates `Min..Max` once.
  `Lua/_GameConst.lua:56` is the separate flat `const.MaxBuildingPriority = 3`, read by the
  player scrollbar (`Building.lua:199`), `TogglePriority` (`_TaskRequest.lua:209-218`), the three
  `Clamp` overrides, `Colonist.lua:1466`, and captured into `DroneControl.lua:8` and
  `RCRover.lua:702`. **Two consts: the group feeds the Lua loops and (INFERRED, delta 16) the C
  matcher; the flat one feeds the UI and the file-locals.** Widening the flat one would put
  bands 4/5 on the player's arrows — no candidate may touch it.
- **Filing.** `_InternalAddRequest :309-335` bakes priority (`:312-313`) and files into
  `supply_queues[p][res]`/`demand_queues[p][res]` (`:315-321`) and, when `ShouldPostRequestInQueue`
  (Mars: `rfPostInQueueFlags`, `_TaskRequest.lua:30-32`), into `priority_queue[p]` with the cursor
  insert `p_queue.index` (`:323-334`; hook `ShouldAddRequestAtCurrentIndex :189-190`, overridden
  nowhere in the tree). `DroneControl:AddBuilding :685-718` is the override every hub, rocket and
  rover uses (`DroneHub.lua:1-2`, `RocketBase.lua:1-2`, `RCRover.lua:4-6`): same tables, no
  `SetPriority`, no cursor insert, `UpdateDeficits` after (`:711`).
- **Removal.** `DroneControl:RemoveBuilding :731-757`: `OnRemoveBuilding :720-729` first (kicks
  drones whose `goto_target` is the building to `Idle` unless `newp > oldp`), then the loop
  `for priority = -1, MaxBuildingPriority` (`:735`, file-local = 3) over the three tables with
  `remove_entry` on plain Lua arrays (`:739-744`), then `UpdateDeficits` (`:749`).
  `TaskRequestHub:_InternalRemoveRequest :364-374` and the base `RemoveBuilding :344-362` loop
  the widened module locals. `SetPriority` (`_TaskRequest.lua:157-181`) = `RemoveBuilding(self,
  oldp, newp)` per centre, set, `AddBuilding` per centre. Re-registration of ONE building is a
  vanilla protocol: `DisconnectFromCommandCenters()` + `ConnectToCommandCenters()`
  (`RequiresMaintenance.lua:289-291, :395-412`; `TaskRequest.lua:204-217`).
- **The matcher seam.** `_TaskRequest.lua:71-83`: `Request_FindTask` is a GLOBAL captured into
  a file-local; `FindTask` hands C `self.priority_queue, self.supply_queues, self.demand_queues,
  self.under_construction, self.restrictor_tables, ResourceUnits, agent.unreachable_buildings,
  flags, agent` — **no bounds, and `self` is never handed to C**; the only other reads of `self`
  are the lap bookkeeping `:77-81`. Sole caller `Drone.lua:621` (uses four of the five returns).
  The finders `:53-69` take `min_priority` and both flag filters and pass the REAL
  `supply_queues`/`demand_queues`; their callers are `Drone.lua:598` (hub self-repair, in Idle
  BEFORE `FindTask`), `:772` (`ImproveDemandRequest`, `min_priority = GetPriorityForRequest + 1`),
  `:1181` (Deliver). Fourth C consumer: `Request_UpdateDeficits(self, …)` (`DroneControl.lua:122`)
  from the persisted deficit thread (`:112-117`, `WaitWakeup`).
- **Malfunction state machine.** Requests are created ONCE at construction
  (`RequiresMaintenance.lua:82` work `max_units=1`, `:86` demand) before connection;
  `SetMalfunction :247-262` (sync; sets `is_malfunctioned` `:252`; no `Msg`; no re-registration),
  `StartDemandPhase :182-188` / `StartWorkPhase :190-205` only `AddAmount`; `Repair :265-298`
  (sync; `Msg("Repaired")` `:295`; re-registers only on the exceptional-circumstances branch
  `:289-291`); `ResetMaintenanceRequests :300-320` → `InterruptDrones` (`_TaskRequest.lua:290-314`,
  `SetCommand("Reset")`); `DisableMaintenance :322-328`. **`GetPriorityForRequest` is consulted
  only at registration** (`TaskRequest.lua:312`, `DroneControl.lua:693`) plus one advisory read
  (`Drone.lua:766`) — changing its return does nothing until a re-registration.
- **Drone side.** `Idle :564-641`: `Sleep` at `:570`, `:577`, `:639`; hub self-repair
  `:594-606` (the vanilla precedent for constructing a pairing outside the matcher:
  `FindSupplyRequest` → `SetCommand("PickUp", supply, demand, res, amount)`); `FindTask :621`
  → `SetCommand("Work"/"PickUp")` `:625-629`; `CleanUnreachables :640` last statement (sync,
  `:879-896`). `Work :898-938`: claim = `RequestAssignUnit :901`, failure → `Sleep(1000)` and
  back to Idle; destructors unassign (`:905-912`, `:928-935`); no `CanAssignUnit` in `Work`.
  `PickUp :940-1016` same shape with two claims (`:941`, `:946`).
- **Save/load.** `DoSaveGame` `Savegame.lua:1037-1063` fires `SaveGameStart :1043` on a
  REAL-TIME thread; `EngineSaveGame :862` is the one persist call; `SaveGameDone :1061`.
  Autosave `:1484-1546` → `SaveAutosaveGame :1450-1452` → `DoSaveGame`; quicksave `:1342-1405`
  → `DoSaveGame :1383`. Two paths skip both messages: `SaveGameBugReportPStr :1143` (the
  in-game bug reporter) and `InMemSaveGame :1119` (no Lua caller). Load: `UnpersistGame :801-818`
  — `PersistLoad` (threads re-materialised, `cthreads.lua:506-542`) → `PersistPostLoad` →
  `LoadGame :810` → fixups `:811` → `PostLoadGame :813`; game time stays paused by the
  `game_blocking` load screen (`Savegame.lua:1098`; `LoadingScreen.lua:57-60`, released at `:184`
  after `LoadGame` returns) ⇒ **no game-time thread can run before `PostLoadGame`** — the R4
  hook is `OnMsg.LoadGame` (`EF-028`; `CityStart`/`NewMapLoaded` fire BEFORE unpersist on a load).
- **Persist.** Permanents: `g_Classes` and each class TABLE by name (`persist.lua:157-165`),
  `_G` (`:61, :104`), each mod env (`Mod.lua:1642-1644`); the walk substitutes the label and
  does not descend. Roots: `PersistableGlobals` (`GameVar`, `lib.lua:1040-1055`;
  `persist.lua:119-134`) and the thread set (`cthreads.lua:466-504`). A Lua closure that is not
  a permanent is serialised by value with its upvalues (EF-022 MEASURED; the shipped instance
  of it is `RequiresMaintenance.lua:94`). Mods cannot register permanents (`ModMsgBlacklist`
  `Mod.lua:1430-1440`, enforced `:1586, :1593`). `Msg` runs static handlers inline through
  `procall` (`cthreads.lua:15-31`) — a throwing handler is swallowed, the save proceeds.
- **Flattening.** `classes.lua:652-733`: members COPIED into subclass tables at `Autorun`
  (`:685, :703, :726`) except under a `__hierarchy_cache` root (`Building.lua:157` is one —
  `Building` stays a live `__index` link, `:708`); mod code runs before `Autorun` (`EF-058`).

---

## 4 · Part B — the candidates

### 4.1 B1 — the three options, re-examined with the delta applied

The four checks the brief asks for, answered first; the tables follow.

**4.1.1 Is the duplicate leak really unreachable by a wrapper? — No. A chained PRE-wrapper
closes it without replacing anything (FINDING, SOURCE; magnitude still owed to E-3).**
`DroneControl:RemoveBuilding :731-757` is `OnRemoveBuilding` + a loop of `remove_entry` calls
over `self.supply_queues[p][res]`, `self.demand_queues[p][res]`, `self.priority_queue[p]` for
each of `building.task_requests`, + `UpdateDeficits`. The constant is unreachable; the TABLES
are not — they are the hub's own plain Lua arrays, and the request values are the same
userdata. A wrapper that runs the identical three `remove_entry`s for
`p = 4 .. const.TaskRequest.MaxBuildingPriority` **before** `orig(self, building, oldp, newp)`
leaves the file-local loop to do `-1..3`, and `orig`'s `UpdateDeficits` then sees clean tables.
Pre, not post, for that reason and for layer-2 shape. Every removal path reaches it:
`DisconnectTaskRequesters :441-450` → `RemoveCommandCenter` → `center:RemoveBuilding`;
`SetPriority` → `center:RemoveBuilding`; `_InternalRemoveRequest` already loops the widened
locals. `TaskRequestHub:RemoveBuilding` (base) is never used by a `DroneControl`. ⇒
**`DRONE_PRIORITY_SYSTEM.md` §10's conclusion "requires replacing `DroneControl:RemoveBuilding`
outright" is corrected in the fix-pack commit**; its mechanism paragraph stands.

**4.1.2 Tear-down-on-save. — Implementable, owner-declined, and Src now shows it cannot hold
its invariant on the autosave path (FINDING, SOURCE).** Delta 15: on autosave/quicksave game
time is not paused and there are ≥ 4 yields between the handler and the walk. A drone thread
can call `FindTask`, `AddBuilding` or `_InternalAddRequest` in that window. If the handler
removed keys 4/5 while the widened module locals still loop to 5, `_InternalRemoveRequest :369`
nil-indexes — the §8 crash from our own hand; if it only re-filed entries, a malfunction in the
window files at 4/5 again and is written. Additionally every autosave (≈ once a sol) would
re-file downward through `RemoveBuilding(b, 5, 3)`, whose `OnRemoveBuilding` kicks every drone
approaching an elevated building to `Idle` (`:721-727`, `newp < oldp`); avoiding that means table
surgery, which then leaves EMPTY keys 4/5 in the save (nothing vanilla index-nils on, but
orphaned data). Cost per save: one three-table sweep per `DroneControl` — small; the problem is
correctness, not cost. Drones mid-command keep their claim (the userdata is unchanged by a
re-file). Save paths without the hook: the bug-report save and `InMemSaveGame` — negligible for
players. **Retired (§4.2 T).**

**4.1.3 The top-up on load (R4 for option 1). — `OnMsg.LoadGame` is early enough, and the
v2 pattern is the right shape (FINDING, SOURCE; E-5 owed for the measurement).** No game-time
thread runs before `PostLoadGame` (routes §3 "Save/load"). The v2 experiment's `TopUp` pre-wrap
on every Lua entry that indexes the tables plus a `LoadGame` sweep
(`6d05136:Code/97_Q1Q2_PriorityBands.lua:133-170, :174-208`) is the backstop-plus-belt shape;
today it walks `AllMapsForEach(true, "DroneControl", TopUp)` (EF-053) and must also pre-wrap
`FindSupplyRequest`, `FindDemandRequest` and `DroneControl:UpdateDeficitsInternal` (`:121-123`,
called from the persisted deficit thread on resume) because those hand the REAL tables to C
too (delta 19). An empty widened table in a later vanilla load is silent (§9 asymmetry,
MEASURED) — and is orphaned data (R3 note). v2 ran on a new game only ("0 topped up"), so the
loaded-save top-up is UNMEASURED → E-5.

**4.1.4 Option 3's real cost. — Settled by delta 16: C reads the group bound.** A shadow view
with keys 4/5 under a const of 3 is never looked at. Two survivors: **V-a**, keys ≤ 3 with
tier order by pass (no bound involved at all); **V-b**, keys 4/5 with the group flipped
`3 → 5 → 3` around the single C call, valid only if C reads the group at call time (E-4(ii)).
Neither widens a real table, so the top-up disappears. Because `FindTask` never hands `self`
to C, the "proxy hub" of seed 3 is five fields on a plain table, and `orig_findtask(proxy, …)`
keeps the C arity vanilla's problem (R8). Full treatment: §4.2 V.

#### Option 1 — bands 4–5 in the real hub tables (+ top-up, + leak wrapper, Rescue as remedy)

| row | verdict | evidence |
|---|---|---|
| R1 | PASS IF `on_deactivate` re-files every elevated building (INFERRED) | entries are baked (`TaskRequest.lua:312-313`); OFF must walk `is_malfunctioned` requesters and `SetPriority`-style re-file; hot wrappers pass through on `IsActive` |
| R2 | PASS on behaviour, NOTE on shape (SOURCE) | the group widening is file-scope and unconditional (`ClassesPreprocess` runs once) — a vetoed install still allocates/top-ups keys 4/5 on every hub; behaviour stays vanilla |
| R3 | **FAIL** (MEASURED §9) | 0 errors ✓, no frame ✓ (sync seams), but requests at 4/5 are STRANDED and the heal expires; keys 4/5 remain in every hub (orphaned data). Only tear-down (4.1.2, retired) would change this |
| R4 | PASS IF E-5 (INFERRED from 4.1.3) | top-up in `LoadGame` + pre-wraps on `FindTask`/finders/`UpdateDeficitsInternal`/`AddBuilding`/`RemoveBuilding`/`_Internal*` |
| R5 | PASS on the letter, blind on the spirit | no new NAME; keys 4/5 and any `_InternalAddRequest`-written userdata priority are unnamed persisted deltas L3 cannot census (delta 12) |
| R6 | PASS (4.1.1; E-3 for the number) | pre-wrapper on `DroneControl:RemoveBuilding` sweeping `4..max` |
| R7 | **FAIL** (delta 11) | stranded 4/5 entries = a new detection kind the Rescue must learn |
| R8 | chained wrappers ×8 + one const write; hot cost one compare | rot: C's bound-read is undocumented; a game update that changes it is undetectable by `install_error` |
| R9 | PASS by construction + identity proof | file-scope install (EF-058 scope clause) |
| R10 | PASS | real keys |
| R11 | F77 flap → `Reconnect` = the leak trigger (closed by R6); the module's own moonlight scan reads the FLAT const (`Opt_DroneOverhaul.lua:239`) and would not see 4/5; `Drone.lua:766` `+1` lets a band-4 delivery be redirected to a band-5 demand (vanilla semantics extended); rockets/rovers widened by the same walk; shuttles untouched (delta 19) | |

**Verdict: NO** on the job's question — R3 and R7 fail by measurement, and the one remedy is
the layer the owner declined and Src now undercuts.

#### Option 2 — inside `-1..3`: "urgent while broken" at 3

Two shapes, because delta 14 splits them:

- **2-M (method override)**: chained `TaskRequester.GetPriorityForRequest` at file scope returning
  3 for a malfunctioned building's maintenance requests + re-registration on the flip.
  **FAILS R3** — `RequiresMaintenance.lua:94` copies the wrapper onto every no-maintenance building
  built under the mod; vanilla serialises it by value (EF-069). An orphan gate makes it inert,
  not absent.
- **2-S (table surgery)**: no method override. On `SetMalfunction` (pre/post wrapper, sync) move
  the building's two maintenance requests from `queue[p]` to `queue[3]` in every covering hub's
  three tables (`remove_entry` + append; the exact ops `DroneControl:AddBuilding :694-706` and
  `RemoveBuilding :739-744` perform); on `Repair`/`DisableMaintenance` move them back to
  `building:GetPriorityForRequest(req)`; post-wrap `DroneControl:AddBuilding` to re-apply after
  any re-registration; `OnMsg.LoadGame` sweep re-applies for every currently-malfunctioned
  requester. No `UpdateDeficits` churn: deficits sum over all bands (`:133-161`), so a move
  changes no total.

| row | 2-S verdict | evidence |
|---|---|---|
| R1 | PASS (INFERRED) | `on_deactivate` moves every elevated pair back; nothing else exists |
| R2 | PASS | wrappers gate on `IsActive`; no const, no allocation |
| R3 | PASS (SOURCE) | requests sit at 3 — a key vanilla iterates (`:735`); no closure (no method on any object); no frame; no widened table; the residue is "a broken building's requests filed one band above its arrow until its next re-registration", **the exact shape vanilla gives a broken pipe** (`SupplyGridBreakable.lua:49-50`: `priority` field unchanged, repair legs at 3) |
| R4 | PASS by construction | no table shape change |
| R5 | PASS | zero names; urgency is `is_malfunctioned`, vanilla's own field |
| R6 | n/a | vanilla's loop covers 3 |
| R7 | PASS | nothing |
| R8 | chained: `SetMalfunction`, `Repair`, `DisableMaintenance`, `DroneControl:AddBuilding`; not hot | `SetMalfunction` is overridden+forwarded by `Elevator.lua:1003-1006` — wrap the base, the forward reaches it |
| R9 | PASS + identity proof | file scope |
| R10 | **FAIL by definition** | one band; 5/4/player-3 collapse — unless E-7 (cursor insert) buys within-band order |
| R11 | pipes/passages already at 3 (tie, cursor order); `Drone.lua:766` `+1` = 4 → C loops `4..3` = nothing (no redirect); rockets/rovers get the same move; fix pack: none on these seams | |

**Verdict: clean revert YES (from citations) — but it is not bands 4–5.** The honest one-line
disclaimer it can carry is written in §4.2 D.

#### Option 3 — merged-view overlay → candidate V (§4.2)

Re-scoped by 4.1.4; its full table is under V, which is the same mechanism made concrete.

### 4.2 B2 — the brainstorm: fourteen mechanisms, each with its table and a kill-or-keep

The end is "broken life-support first, broken things before routine hauling, the arrows go
back to meaning supply allocation". Seeds 1–9 of the brief are extended; killed ideas keep
their table so the kill is auditable.

#### V — "view tiers": transient mod-built tables handed to the matcher in tier order ⭐ KEEP

**Mechanism [IDEA, on SOURCE seams].** A chained `TaskRequestHub:FindTask` wrapper (file
scope; the module already has one at `Opt_DroneOverhaul.lua:180-212`) keeps, per hub, two
transient tier sets — **T5** = malfunctioned `AirProducer`/`WaterProducer` (Q3 class test) plus
the grid/dome repair requests vanilla files at 3, **T4** = every other malfunctioned
`RequiresMaintenance` — restricted to requesters connected to this hub
(`table.find(bld.command_centers, hub)`), each holding only requests with `CanAssignUnit()` and
`GetTargetAmount() > 0`. On a call: if both sets are empty → `return orig(self, agent, flags)`
(the fast path — one table read). Else build a **proxy** — a plain table with
`priority_queue = {[-1..2] = empty, [3] = T5 work+demand}`, `demand_queues = {[-1..2] = empty,
[3] = {[res] = T5 demands}}`, `supply_queues = self.supply_queues` (REAL, so C pairs an urgent
demand with any real supply exactly as it does today), `under_construction`, `restrictor_tables`,
`lap_start`, `lap_time` — and call `orig(proxy, agent, flags)`: `FindTask` reads nothing else
of `self` (`_TaskRequest.lua:73-81`), so the proxy is complete and the lap writes land on it
harmlessly. A result → return it in vanilla shape (`request, pair_request, resource, amount,
priority`; the drone uses four, `Drone.lua:621-629`). Nothing → same with T4. Nothing →
`orig(self, …)`. The sets are maintained by chained wrappers on `SetMalfunction`, `Repair`,
`DisableMaintenance` (all sync) and rebuilt on `OnMsg.LoadGame` from `is_malfunctioned` over the
`RequiresMaintenance` label (sync walk); pipe/passage repair requests join T5 at
`FindTask` time by a scan of the real `priority_queue[3]` for `BreakableSupplyGridElement` /
`PassageGridElement` sources (cost ∝ band-3 depth) or by a wrapper at their request creation
(`SupplyGridBreakable.lua:33-36`) — a design detail, not a rubric row. Duplicates are by
design: an urgent request stays in the real tables at its real band and appears again in a
view; it is the same userdata, so a claim through either path flips `CanAssignUnit` for both
(`max_units = 1` on work requests, `RequiresMaintenance.lua:82`).

**V-b (variant):** the same, with real keys 4/5 in the proxy and
`const.TaskRequest.MaxBuildingPriority` flipped `3 → 5` before the single C call and back
after — one C call instead of up to three, a literal 4 and 5 for the matcher. Valid only if C
reads the group at call time (E-4(ii)); otherwise identical to V-a. No real table is widened
either way, so the module locals stay at 3 and nothing nil-indexes.

| row | verdict | evidence |
|---|---|---|
| R1 | **PASS, instant** (SOURCE) | the real tables are never touched; OFF = the wrapper passes through on the next call; nothing to put back |
| R2 | PASS (SOURCE + L8) | file-scope wrapper, status `disabled` → pass-through; no const written outside a synchronous call (V-b) or ever (V-a) |
| R3 | **PASS by construction** (SOURCE) | no key 4/5 in any real table; no closure on any object (the wrapper lives in class tables = permanents, `persist.lua:157-165`); no frame (`FindTask` is sync — `SaveGameStart` can never land inside it); nothing stranded (real filing is vanilla's); nothing widened |
| R4 | PASS by construction | no top-up; works on any save |
| R5 | **PASS** (SOURCE, delta 18) | the tier sets and proxies are upvalues of a class-table function — the walk does not descend into class tables, `_G` or the mod env; weak-keyed like the module's existing caches (`:115-118`) |
| R6 | n/a | nothing enters the real tables at 4/5 |
| R7 | PASS | nothing |
| R8 | chained: `FindTask` (hot: one read on the empty path; up to three C calls when a tier is non-empty), `SetMalfunction`, `Repair`, `DisableMaintenance`, `LoadGame`. **No C signature knowledge** (proxy goes through `orig`). Rot surface: "`FindTask` reads only those fields of `self`" (`:73-81`) — checkable by the fpk diff at every update | prior art: "Smarter Drones" rotted by re-implementing the finders in Lua; V re-implements nothing |
| R9 | PASS + identity proof on live hubs (EF-066) | one classdef write on `TaskRequestHub` pre-`Autorun` reaches all 48 carriers (EF-058 scope clause) |
| R10 | **PASS** — strict between tiers (a pass returns before the next runs), C's own order within a tier | the distinction is pass order, not a stored number (V-a) or a literal 4/5 (V-b) |
| R11 | F77: none (no registration change); D09: none; fix pack: none on `FindTask`, and `Fix_DroneUnreachableForever` on `CleanUnreachables` chains either order (EF-054); hub self-repair (`Drone.lua:594-606`) still runs before `FindTask` — vanilla precedence kept; `ImproveDemandRequest` sees the real tables only (no redirect to a tier — acceptable, and it cannot crash: bound 3, keys 3); deficits over real tables — shuttles unchanged; rockets/rovers: the wrapper is on `TaskRequestHub`, so they serve tiers first too unless gated on `DroneHubBase` as v1 does (`:185`) — an owner design question (§6 ask C) | |

**UNKNOWN cells → E-4(iii) (a mod-built table set is honoured by `Request_FindTask`, incl.
the `.index` cursor it may write into the proxy) and E-8 (a wrapper-substituted pairing is
claimed via `RequestAssignUnit :901`/`:941` and executed to `MaintenanceDroneUnload :418-426`
like a matcher-chosen one). E-4(ii) decides V-b vs V-a only.**

**Kill-or-keep: KEEP — first.** It is the only mechanism that delivers the full 5/4/3 ordering
with every R-row filled from citations except the two matcher cells.

#### P — pre-emption at `FindTask` via the engine's own finders (seed 1) ⭐ KEEP as V's sibling

**Mechanism [IDEA].** Same tier sets; instead of a proxy, the wrapper iterates T5 then T4
itself: for a building in `maintenance_phase == "demand"` it calls
`self:FindSupplyRequest(agent, req:GetResource(), req:GetTargetAmount())` and returns
`(supply, demand, res, amount)` — the precedent is vanilla's hub self-repair (`Drone.lua:598-600`);
for `"work"` it returns `(work_req, nil, "repair", Min(DroneResourceUnits.repair, target))` —
the precedent is `Drone.lua:604` and the module's own moonlighting (`:259-260`). Reachability
via `agent.unreachable_buildings` (the finder takes it; work requests checked as moonlighting
does, `:247-248`). Order within a tier is the mod's (life-support first, then nearest) rather
than C's.

Rubric: identical to V in every row except **R10** (order within a tier is policy, not C —
the same distinction, differently owned) and **R8** (the wrapper reconstructs pairings for work
requests; the finders do the haul leg). **UNKNOWN → E-8** (E-4 not needed).
**Kill-or-keep: KEEP** — the fallback if E-4 fails; slightly more logic in the mod than V.

#### D — the devs' own mechanism, exactly (seed 8), and the question it raises — KEEP as the minimum

**Mechanism [FINDING for the shape, IDEA for the build].** `BreakableSupplyGridElement` and
`PassageGridElement` return 3 for their repair legs via the class override. The 2018 drop did
the same for maintenance behind `maintenance_request_is_highest_prio` + disconnect/reconnect
(delta 22) and the devs removed it. Applying it to the five producers + the malfunction
predicate = **option 2-S restricted to `AirProducer`/`WaterProducer`** — implemented by table
surgery, not by the class override (EF-069). Its honest disclaimer: *"broken oxygen and water
producers are repaired at the same urgency the game already gives broken pipes and dome
cracks; nothing else changes; a save made with this on loads in vanilla with those requests at
'urgent' until the building is next re-registered."* Rubric = 2-S (R10 fails).
**The question, written as a question (§6 ask A):** is *5 vs 4 vs player-3* a requirement or
a preference, given that the devs' own tier is exactly one band, the player's maximum
coincides with it by design (`Building.lua:199`), and the devs shipped and withdrew a
one-band urgency themselves? **Kill-or-keep: KEEP** as the no-experiment floor.

#### C — cursor insert: within-band "serve next" without changing the band (seed 9) — IDEA, E-7

**Mechanism [IDEA on a SOURCE hook].** `TaskRequester:ShouldAddRequestAtCurrentIndex(req)`
(`TaskRequest.lua:189-190`, overridden nowhere) makes `_InternalAddRequest` insert at
`p_queue.index` (`:325-330`) — the round-robin cursor the 2018 Lua mirror reads
(`local index = requests.index or 1`). A mod re-filing an urgent request via
`hub:_InternalRemoveRequest(req)` + `hub:_InternalAddRequest(req, bld)` with the hook true
would make it the next examined in its band. Caveats: only the base path honours the hook
(`DroneControl:AddBuilding` appends, `:704-705`), `_InternalAddRequest` writes
`request:SetPriority` into the userdata (delta 17 — a vanilla-legal value, but a write vanilla's
own path never makes), and whether the Relaunched C serves from the cursor is UNKNOWN. Rubric:
R1–R9 as 2-S plus the userdata write (R5 note); R10: within-band only — combined with 2-S it
gives "urgent first within 3", still one band vs pipes. **Kill-or-keep: KEEP as a refinement,
E-7.** (Vanilla's own `OnAddedToTaskRequestHub` hook, `:192-193`, is the natural place to trigger
it.)

#### E — event-driven push dispatch (extends seed 4, the moonlighting pattern) — KEEP as an adjunct

**Mechanism [IDEA].** On the `SetMalfunction` wrapper (sync), if a covering hub has an IDLE
drone (`command == "Idle"`), hand it the job directly the way vanilla hands the repair to the
deliverer (`StartWorkPhase :196-198` → `SetCommandKeepQueue`): `FindSupplyRequest` → `SetCommand
("PickUp", supply, demand, …)` or `SetCommand("Work", …)`. Zero latency instead of the 2 s +
1 s Idle cadence (`Drone.lua:620, :639`). Rubric: as P (sync, no data), R10: event order, not a
queue — simultaneous breakdowns get first-come service, so it is an ADJUNCT to V/P, not a
replacement; R11: must take only `Idle` drones (a `SetCommand` on a working drone kills its
command, `CommandObject.lua:372`). **Kill-or-keep: KEEP as adjunct, E-8 covers it.**

#### 2-S — option 2 by table surgery — KEEP (documented above)

#### 2-M — option 2 by class-level override — KILL (R3, EF-069)

Table: R1/R2/R4–R9/R11 as 2-S; **R3 FAIL** — vanilla copies the override onto every
no-maintenance building built under the mod and serialises it by value; **R10 FAIL**.

#### T — widen + tear-down-on-save (seed 5) — KILL (owner-declined layer 1; SOURCE 4.1.2)

Table: as option 1 with R3 "PASS-ish (empty keys) IF the window closes" — and the window does
not close on autosave/quicksave (delta 15); R7 conditional on accepting empty keys; R8 highest
(a handler on every save incl. ≈ once-a-sol autosaves, `EF-030`). **Kill.** Every save path
enumerated: manual (paused, hook), autosave (unpaused, hook), quicksave (unpaused, hook),
bug-report save (no hook), `InMemSaveGame` (no hook, no Lua caller), cloud (uploads a written
file after `SaveGameDone`, `Lua/Savegame.lua:24-29`), crash (no save). Recorded for the owner
as ask B — the ruling is theirs to reopen, and this report gives no new evidence FOR it.

#### W — widen per hub on demand, un-widen on exit (seed 6) — KILL (SOURCE)

`_InternalRemoveRequest :369` and the base `RemoveBuilding :349` loop the widened module
locals unconditionally — a hub without keys 4/5 while the group says 5 nil-indexes (§8). The
group cannot be 5 while any hub lacks the keys, so per-hub widening is impossible; with the
group at 3 there are no bands. It collapses into V-b's per-call flip, which never widens a hub.

#### N — demote routine traffic instead of promoting urgent (seed 7) — KILL (SOURCE)

Filing the player's 1..3 one band lower puts "Low" at 0 with depot requests
(`GetPriorityForRequest :182-183`) and would need −1, the floor `RCTransport` uses for its own
supplies (`:217-219`); every building re-registers; the arrows stop meaning what they show
(`GetUIPriority`, `_TaskRequest.lua:225-227`). R10 preserved, R11 broken, and it is the player's
scale inverted. Kill.

#### S — a drone-side pre-hook on `Idle` (seed 4 as written) — KILL

A pre-wrapper on a command body is layer 2 by policy and needs no tail-call measurement
(E-2 refused), but it fires before vanilla's hub self-repair (`:594-606`) and gains nothing
over P, which sits inside the same `Idle` at `:621` on a synchronous seam. Kill.

#### B — set the building's own `priority` to 3 while broken (the "what a player would do") — KILL

`SetPriority` writes the persisted vanilla field; after uninstall the arrow stays High
forever with no way to know it was ours (R3 "nothing a second mod has to fix" fails in the
worst way — it cannot be fixed); restoring the player's value needs a marker (R5 fail). Kill.

#### Q — brand requests at `Request_New` with a new flag (seed 9) — KILL

`Request_New = MarsRequest_New` (`_TaskRequest.lua:23`) is a replaceable global, but a flag is
a C-defined bit inside persisted userdata created at construction (`:153-155`) — residue in a
carrier the mod cannot re-open, with C semantics nobody can read. Kill.

#### M — `supply_dist_modifier` as urgency (seed 9) — KILL

It is a SUPPLY-side distance multiplier baked into the userdata at `Request_New :154`, measured
NULL as a brake (C48 `c48-brake`, 3,390/3,390 requesters rebuilt at 150, share unchanged), and
it persists. Not an ordering lever for demands or work. Kill.

#### H — `ShouldAddRequestToCommandCenter` per-class registration policy (seed 9) — OUT OF SCOPE

The `MapSharedDepot` precedent (`Elevator.lua:178-195`) decides WHICH hubs hold a request —
D08 layer 1 territory (`DRONE_OVERHAUL_OPTIONS.md` H). Not urgency. Filed, not designed.

### 4.3 Ranked shortlist — trade-offs measured where a number exists

| rank | candidate | rows from citations | rows owed to a run | what it costs |
|---|---|---|---|---|
| 1 | **V** view tiers (V-a; V-b if E-4(ii)) | R1–R9, R11 | R10 as behaviour (E-4(iii), E-8) | up to 3 C calls per `FindTask` while a tier is non-empty (25,184 calls / 10 game-h measured at 3×; tiers are empty most of the time) |
| 2 | **P** finder pre-emption | R1–R9, R11 | E-8 | mod-side iteration of the tier sets per call; pairing logic for work requests |
| 3 | **2-S** table surgery at 3 (+ C if E-7) | R1–R9, R11 | none for revert; R10 fails | one band; the pipe/passage tie |
| 4 | **D** the devs' tier on five producers | as 2-S | none | narrowest; the owner's distinction question |
| — | option 1 | R6, R9, R10 | R4 (E-5) | R3/R7 fail by measurement; the Rescue learns a kind; a const write; 8 wrappers |
| — | T, W, N, S, B, Q, M, 2-M | — | — | killed by SOURCE or by the owner's ruling |

What V and P give up against option 1: a literal 4/5 stored anywhere (V-b keeps the literal
for the matcher's eyes only), `ImproveDemandRequest`'s redirect toward an elevated demand, and
the "bands are data other code could read" property — no vanilla code reads a request's band
except C (delta 17), so the last is a property nobody uses.

---

## 5 · Experiment cards — designed and priced, NOT run

Every card: NEW GAME only (`EF-055/056`; the 07-31 incident broke a live colony), a TEMPORARY
TestKit module marked `TEMPORARY` and deleted in the result commit (`WORKFLOW.md` probe
hygiene), `tasklist | findstr Mars.exe` as its own step, predictions committed before the run,
polled reads paired with an event witness (`EF-057`), `PROBE SWEEP:` line on the result commit.

**E-4 — what `Request_FindTask` reads, three questions in one sitting (≈ 30 min attended).**
Fixture: new game, one hub, one Stirling Generator in range, group at default 3.
(i) *bound vs keys* — already INFERRED (delta 16); the run re-reads it: set
`const.TaskRequest.MaxBuildingPriority = 5` from the console on the NARROW hub, call
`hub:FindTask(drone)` in a `pcall` → **prediction: throws "attempt to index a nil value"**
(bound) / returns (keys). Restore 3. (ii) *call-time vs cached* — the same read IS the answer:
a throw after a runtime write means C read the group at call time; no throw with (i) already
measured true on 07-31 (file-scope write) means it cached at `ClassesPreprocess` →
**prediction: call-time** (the flat const was untouched on 07-31, so nothing else could have
carried the 5 to C). (iii) *a mod-built view is honoured* — build a proxy with
`priority_queue[3] = {work_req}`, `demand_queues[3][res] = {demand_req}`, real
`supply_queues`, real `under_construction`/`restrictor_tables`; break the generator; call
`TaskRequestHub.FindTask(proxy, drone)` → **prediction: returns the demand paired with a real
supply (phase demand) / the work request (phase work)**; inspect `proxy.priority_queue[3].index`
after the call (does C write the cursor into our table?). Settles: V-a (iii), V-b (ii), and
the design of the fast path.

**E-8 — a wrapper-substituted pairing executes like a matcher-chosen one (≈ 40 min).**
Fixture: new game, Polymers stocked, one generator. TEMPORARY wrapper returns, for one call,
the generator's demand paired by `FindSupplyRequest`; log `RequestAssignUnit` (`_TaskRequest.lua:352`)
and `MaintenanceDroneUnload :418` for that request. **Prediction:** claim succeeds, PickUp →
Deliver → unload → `StartWorkPhase(drone)` hands the repair to the deliverer; `malfunctioned →
false`. Falsifier: the claim fails and the drone takes the shipped miss path (`Sleep(1000)`,
`Work :902`). Settles: V, P, E.

**E-3 — the leak wrapper (≈ 25 min).** Fixture: new game under a TEMPORARY group-5 widening
(hubs allocate `-1..5` natively — the v2 shape), two buildings armed at 4 (v2 `Arm`),
`ReconnectTaskRequesters()` ×3 on the hub; read `#demand_queues[4][res]` before/after each.
**Prediction without the pre-wrapper: 2 → 4 → 6 → 8** (re-measures §10's `4 → 6`); **with the
pre-wrapper of 4.1.1: 2 → 2 → 2 → 2.** Settles R6 for option 1 and corrects §10's number to n=2.

**E-5 — top-up on a loaded save before the first `FindTask` (≈ 30 min).** Fixture: new game
saved with NO widening (narrow hubs), then loaded with a TEMPORARY module = group 5 +
`OnMsg.LoadGame` `AllMapsForEach(true,"DroneControl",TopUp)` + the pre-wrap set of 4.1.3.
**Prediction:** `topped_up == 19-ish (the walk's count)`, 0 `[LUA ERROR]` across 5 game-min,
`Q1.Status()` reads keys `-1..5` on a hub built before the load. Only owed if option 1 is
chosen.

**E-6 — the `:94` capture (≈ 35 min; a SOURCE finding, this measures it).** Fixture: new game
under a TEMPORARY chained `TaskRequester.GetPriorityForRequest` wrapper (file scope, gated
open); build one no-maintenance building (any template with `maintenance_resource_type =
"no_maintenance"`); save; **load WITHOUT the module** (Mod-Manager disable + restart, PT-20
method). **Prediction:** `rawget(bld, "GetPriorityForRequest")` returns a function, and a
`ReconnectTaskRequesters()` on its hub logs `attempt to index a nil value` naming the mod (or
runs silently if the wrapper opened with an orphan gate — both outcomes confirm the capture).
Turns EF-069 from SOURCE to MEASURED.

**E-7 — the cursor insert (≈ 40 min).** Fixture: new game, three same-class buildings at the
same band broken in sequence; re-file the third via `_InternalRemoveRequest` +
`_InternalAddRequest` with `ShouldAddRequestAtCurrentIndex` true on its instance; watch which
work request the next idle drone claims. **Prediction:** the third. n ≥ 3 repeats.

**E-9 — tier precedence at n ≥ 3 (≈ 45 min; only after E-4/E-8 pass).** The Q1 pair
re-run through V: T5 generator vs real band-3 generator, equidistant. **Prediction:** the T5
building reaches `phase=work` first on every repeat. This is the claim §9 of the brief forbids
until measured.

**E-1 (save-hook synchronicity) — written, NOT owed:** answered from SOURCE (delta 15) and
the candidate it served is retired. **E-2 (tail call) — REFUSED:** `EF-023` and `FIX_POLICY`
§3a say do not measure it and do not rely on it.

Running any card is an owner call — checklist item 92.

---

## 6 · Corrections and filings

**Owner asks — bodies on the fix pack's `docs/PLAYTEST_CHECKLIST.md` "Decisions waiting on you":**
ask A (is the 5/4/3 distinction a requirement or a preference?) and ask B (tear-down-on-save is
layer 1, owner-declined; this report gives no new evidence FOR reopening it) are folded into
**item 91**, the restated design decision; the experiments to run are **item 92**; ask C
(tiers on rockets/rovers or hubs only) is **item 93**.

- **Fix pack `DRONE_PRIORITY_SYSTEM.md`** (same commit as this report, fix-pack side): §4
  gains the fourth override (`RCTransport.lua:217-223`); §6 landmine 4 gains the EF-069
  consequence; §10's cost line is corrected — a pre-wrapper closes the leak, no replacement
  needed (4.1.1). Its mechanism and the `4 → 6` reading stand.
- **New fact EF-069** (allocated in the fix pack, mirrored here): the `:94` capture route.
- **No fact file was contradicted by Src today.** `EF-024/028` line cites verified
  (`Savegame.lua:1043`, `:1061`; `Mod.lua:1430-1440`).
- **Out of scope, filed by pointer only:** the deleted v1 experiment header's claim that
  `priority_queue` is always empty was wrong (Mars overrides `ShouldPostRequestInQueue`,
  `_TaskRequest.lua:30-32`) — no live doc carries it; H (registration policy) belongs to D08.

---

## 7 · Verdict and recommendation

**YES IF — V passes pending E-4 and E-8.** Every rubric row for V fills from citations except
the two that only a matcher can answer: that it honours a mod-built table set (E-4(iii)) and
that a substituted pairing runs to completion (E-8). If E-4 fails, **P** carries the same
verdict on E-8 alone. Bands 4–5 **as persisted data** are a **NO** — R3 and R7 fail by the
07-31 measurements, and the only remedy is the layer the owner declined, which Src now shows
cannot hold on the autosave path.

**Recommendation (ranked, not decided — the pick is checklist item 91):** build the rebuild on
V (V-a; adopt V-b if E-4(ii) reads call-time), with E as an adjunct, and carry 2-S as the
documented fallback if both matcher experiments fail. Run E-4 and E-8 first (one sitting,
≈ 70 min), E-9 after they pass. Do not run E-5 or E-3 unless option 1 is chosen. Whether the
5/4/3 distinction is a requirement (V/P) or a preference (D suffices) is the owner's question
to answer before the build brief is written.

**What this report does not claim:** band ordering inside or between bands (E-9 owed); the
leak's magnitude (n=1 until E-3); that V "has no behaviour change" (desk-derived); which option
the owner should pick (the checklist item asks it).
