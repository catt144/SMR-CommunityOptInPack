# D06 rebuild — the DESIGN SPEC (2026-09-01)

**Job:** one-off `prompts/DRONE_BUILD_DESIGN.md` (consumed by this commit; recover with
`git show 870c3e0:docs/agent/prompts/DRONE_BUILD_DESIGN.md`). Written at opt-in `870c3e0` /
fix pack `3e224a7` / TestKit `832568e`, Src build `1.0.7.396349` (`EF-014`). **Desk only —
no module built or changed, no experiment run, no save loaded** (`PROBE SWEEP: clean`).
Its companion is the build brief `prompts/DRONE_REBUILD_BUILD.md`, which the BUILD session
runs from. **Nothing is built until the owner ratifies §9 ask 1** (fix-pack checklist 91).

**Provenance words on every claim:** **SOURCE** = read at Src `file:line` this session ·
**MEASURED** = a recorded log/console reading with its date · **INFERRED** = follows from
SOURCE/MEASURED by an argument written out here · **IDEA** = unproven. Every rubric cell and
every table cell below carries one.

> ⚖️ **The owner's directive this spec is built to (2026-09-01):** the best build-out of the
> D06 rebuild **in a way that does not require the Save Rescue or any uninstall mod**. That
> makes rubric rows **R3** (uninstall-clean) and **R7** (nothing for the Rescue to do) HARD
> CONSTRAINTS, not trade-offs. Every candidate that fails either one is out regardless of what
> it wins elsewhere; the two that were rejected on exactly that ground are named in §2.

> ⛔ **E-4 and E-8 HAVE NOT RUN** (fix-pack checklist 92 is OPEN, verified at `3e224a7`
> 2026-09-01). Per the job's §0.4 branch this spec designs **V-a as primary**, records **P**
> as the fallback and **2-S** as the floor, and the build brief's FIRST GATE is running E-4 /
> E-8 / the `EF-074`-guard assertion before a line of module code is written. **No outcome of
> either experiment is claimed anywhere in this document.**

---

## 1 · What is being built, in one paragraph

`Opt_DroneOverhaul` v1's closest-fleet claim gate measured inert (B2, 2026-07-29: one veto in
25 malfunctions, its leg moved one minute) because **hauling is 88 % of repair elapsed time and
v1 exempts hauling by design** (D06 entry). The owner ruled a rebuild 2026-07-31 shaped as
**urgency tiers** — broken life-support first, then broken anything, both above the player's
supply arrows — and the 2026-09-01 bands report established that bands 4–5 **as persisted data**
cannot revert cleanly, while the same ordering **held in transient structures the matcher is
shown** can. This spec builds that: **the tiers are a VIEW, the filing stays vanilla's.** The
claim gate is deleted (settled 07-31). Repair moonlighting is kept unchanged (§6, with the
reasoning). `DroneReport()` is kept and extended.

---

## 2 · THE TIER × DEMAND LAYOUT TABLE

**The single answer to "who is served first, on which leg, fed from where, and what does turning
it off leave."** Every cell cites Src or an `EF-`; cells that need a running game name their
experiment. Read the prose rules under the table with it — the table alone is not the design.

**Reading the "tier" column:** T5 and T4 are **passes**, not keys. Nothing is ever filed at 4 or
5. Rows 3 / 2 / 1 / 0 / −1 are the real vanilla bands and are listed so the whole ordering is on
one page; the rebuild does not touch them except where the row says so.

| tier | contents — the predicate, as a Src-citable test | legs elevated | supply side | `EF-074` guard | revert: toggle OFF / uninstall |
|---|---|---|---|---|---|
| **T5** | (a) **malfunctioned life-support producers**: `IsKindOf(b,"AirProducer") or IsKindOf(b,"WaterProducer")` AND `b.is_malfunctioned` — the game's own test (`LifeSupportGrid.lua:272-276`), completeness claimed by the class docstrings (`LifeSupportProducer.lua:21-23`, `:125-127`), exactly **5** templates via 4 derived classes (SOURCE, re-verified 2026-09-01: `Electrolyzer.lua:3`, `MOXIE.lua:3`, `MoistureVaporator.lua:3`, `WaterExtractor.lua:3`; Q3a, D06 entry). **plus** (b) **vanilla's own band-3 grid/dome repair legs** — requests in the hub's REAL `priority_queue[3]` / `demand_queues[3]` whose `GetSource()` `IsKindOf` `BreakableSupplyGridElement` or `PassageGridElement`, with `GetTargetAmount() > 0` and `CanAssignUnit()`. Their band is 3 unconditionally by class override (`SupplyGridBreakable.lua:48-56`; `Passage.lua:485-491` — SOURCE) so the amount test is what selects a genuinely broken one. **Co-equal with (a) by design**, so the rebuild never outranks a dome breach with a broken Mall | maintenance **demand** (`b.maintenance_resource_request` — the haul IS the repair, the 88 %) **and** maintenance **work** (`b.maintenance_work_request`); for (b), vanilla's `repair_resource_request` + `repair_work_request` / `fracture_*_request` | the **REAL** `supply_queues` of that hub, passed by reference into the proxy — so the C matcher pairs an urgent demand with any real supply exactly as it does today. **`EF-059`'s depot-last-resort law is untouched and is NOT overridden**: a tier demand is still fed from loose piles / producer output before a depot, however near the depot is. Stated because it is a player-visible consequence, not a footnote — see §2b rule 3 | **guarded, on the demand leg only** (a): the pre-wrapper on `Drone:ImproveDemandRequest` declines improvement for `b.maintenance_resource_request` while `b.is_malfunctioned` and `must_change` is false (§2b rule 5). (b): **no guard needed and none installed** — a grid/dome demand's real band is already 3, so `ImproveDemandRequest`'s `min_priority = 3 + 1 = 4` and C loops `4..3` = nothing (SOURCE, `Drone.lua:766`; `EF-071`) | **nothing / nothing.** The tier is a view (`EF-072`); the real filing is vanilla's and was never altered. OFF = the wrapper passes through on the next call. Uninstall = the save has no key 4/5, no mod closure on any object, no captured frame |
| **T4** | every other `RequiresMaintenance` with `is_malfunctioned` — the `:41` *"no work possible"* split: elevate **broken**, not degrading. `is_malfunctioned` is written in exactly four places tree-wide (SOURCE, swept 2026-09-01): the classdef default `RequiresMaintenance.lua:41`, then `SetMalfunction :252`, `Repair :271`, `DisableMaintenance :324` — which is why the lifecycle wrapper set in §3 is provably complete | demand + work, same two requests | same real `supply_queues` | guarded, same rule | same |
| **3** | the player's **High**; vanilla's pipes / dome fractures (their own class override, `:48-56` / `:485-491`); **⚖ the food-service default-3 data patch** — `IsKindOf("ServiceWorkplace")` AND a Food demand = exactly **4** buildings (Diner, Mega Mall, Grocer, Small Grocer; the Food test alone also catches two habitats, which are residences — Q3b, D06 entry). Q4: `priority` is a class member (`TaskRequest.lua:53-59`), no template sets it, instances carry it only after a real change (`SetPriority :170-179` early-outs on equality) ⇒ omitted from saves, clean revert. **Its own decision row — §9 ask 2 — and buildable independently of everything else here** | vanilla | vanilla | n/a (a real band; `ImproveDemandRequest` behaves exactly as it does today) | data patch: the class default returns to 2 and the four re-register on `on_deactivate`; the save never carried it (Q4). Everything else on this row: nothing to revert |
| **2** | the player's default arrows; **routine maintenance top-up stays here** — `is_need_maintenance` without `is_malfunctioned` (`RequiresMaintenance.lua:42`, `SetNeedsMaintenanceState :230`) is a supply question and keeps the player's answer (the owner's split, 07-31) | vanilla | vanilla | n/a | n/a |
| **1** | the player's **Low**; vegetation seed offers (class `priority = 1` — `EF-060` queue census, MEASURED 2026-08-16) | vanilla | vanilla | n/a | n/a |
| **0 / −1** | 0: storage-depot requests (`TaskRequester:GetPriorityForRequest :181-187`, `rfStorageDepot` → 0 — SOURCE). −1: `RCTransport`'s own supplies (`RCTransport.lua:217-223` — SOURCE, the fourth override; the count "three" in `DRONE_PRIORITY_SYSTEM.md` §4 was corrected 09-01) | untouched | untouched | n/a | n/a |
| **construction** | `under_construction` is a separate structure `FindTask` hands C (`_TaskRequest.lua:75` — SOURCE). **DECISION, not an omission: it is passed REAL into every tier proxy and is never filtered.** A tier pass that returns a construction task is DISCARDED and the next pass runs (§3 step 4) — so construction is neither promoted into a tier nor removed from any pass, and its relationship to everything else is decided by the final vanilla call exactly as today. Swarming on a build site stays desirable and stays possible | untouched | untouched | n/a | n/a |

### 2b · The demand-side rules, as prose (each its own row)

1. **Which demand is elevated.** Exactly one per tiered building: `b.maintenance_resource_request`,
   and **only while `b.is_malfunctioned`** (SOURCE, `RequiresMaintenance.lua:75-97` creates it once
   at construction; `:41` is the flag). Not the routine top-up, not any other demand the building
   posts. For grid/dome the pair is vanilla's own two requests, already at 3.
2. **Which work is elevated.** `b.maintenance_work_request` (`max_units = 1`,
   `RequiresMaintenance.lua:82` via `AddWorkRequest("repair",0,0,1)` — SOURCE). Because
   `max_units = 1`, a request appearing both in the real tables and in a view is safe: a claim
   through either route flips `CanAssignUnit()` for both. **Duplicates are by design, not a leak.**
3. **What feeds it, and the honest consequence.** Any real supply. The proxy carries the hub's
   REAL `supply_queues` by reference, so the pairing arithmetic — distance, reachability,
   restrictors, claims — stays engine-side (`EF-060`). **`EF-059` still rules the supply side:
   depots are a strict last resort and a p1 bush beats a fully-stocked nearer depot (MEASURED
   2026-08-16, 479/479).** The tiers change *which job is served first*, never *which pile feeds
   it*. ⇒ **A broken Water Extractor can still wait on parts scavenged from the landscape while a
   full depot sits beside it.** That sentence belongs in the disclaimer (§7) and in the playtest's
   expectations (§8); this design does not fix it and must not be read as fixing it.
4. **Hub self-repair precedence is kept, for free.** `Drone:Idle` repairs its own malfunctioned
   command centre at `:593-606` — **before** the `FindTask` call at `:621` (SOURCE). The rebuild
   installs nothing above that, so a broken hub is still served by its own drones first.
5. **The `EF-074` guard — the mechanism, chosen and reasoned.**
   `Drone:Deliver` re-opens every PickUp-chained delivery through
   `self:ImproveDemandRequest(...)` (`Drone.lua:1164-1175`, and again in the retry loop at
   `:1252-1253`), which asks for a strictly better destination at
   `min_priority = d_building:GetPriorityForRequest(d_request) + 1` (`:766`). A T5/T4 demand's
   REAL band is the building's arrow (default 2), so its parts can be traded up mid-flight to any
   band-3 demand — the exact inversion the tiers exist to prevent (`EF-074`).
   **Chosen: a chained PRE-wrapper on `Drone.ImproveDemandRequest` that returns `d_request`
   unchanged when `must_change` is false and `d_request` is a tier demand.**
   ```lua
   -- shape only; the build writes the real thing
   function Drone:ImproveDemandRequest(s_request, d_request, resource, amount, must_change, ...)
       if not must_change and module_active() and is_tier_demand(self, d_request) then
           return d_request
       end
       return orig(self, s_request, d_request, resource, amount, must_change, ...)
   end
   ```
   Four properties, each cited:
   * **It returns exactly what vanilla returns on its own "nothing better found" path.** With
     `must_change` false and `assigned` still true, vanilla falls to `:807-812` and
     `return d_request` with the drone still assigned (SOURCE, `Drone.lua:802-813`). So the
     wrapper is a *narrowing* of an existing result, not a new outcome — the §1.4b shape
     `FIX_POLICY` prefers.
   * **The `must_change` carve-out is load-bearing, and `EF-074`'s first-named route is unsafe
     without it.** `Deliver`'s retry loop sets `must_change` when the destination is unreachable,
     when a fulfill retry failed, or when the request was suspended (`Drone.lua:1246-1250`).
     A guard that declined *unconditionally* would leave the drone looping on an unreachable
     building at `Sleep(1000)` per pass forever. Handing `must_change` calls straight to `orig`
     keeps vanilla's own escape hatch. **This sharpens `EF-074`, which named the naive decline
     first; the fact is amended in the same commit as this spec.**
   * **`is_tier_demand` needs NO mod state.** It is computed from vanilla fields:
     `local b = d_request:GetSource(self); return IsValid(b) and b.is_malfunctioned and
     d_request == b.maintenance_resource_request`. Nothing is looked up in a mod table, so the
     guard adds nothing to the savegame footprint argument in §4.
   * **The body is synchronous** — no `Sleep`/`WaitMsg`/`WaitWakeup` in `Drone:ImproveDemandRequest`
     (SOURCE, `:760-813`; `tools/blocking_analysis.py` verdict `clear`, run 2026-09-01, §5). Its
     frame can never be captured (`EF-023` route (a) closed by construction).
   ⛔ **This IS a behaviour change and is priced, not hidden:** while a tier delivery is in flight,
   band-3 demands can no longer poach its parts. The player-visible shape is "a delivery heading
   to a broken oxygen plant is not re-routed to a High-priority factory en route". §7 says so.
6. **Rockets and rovers — DEFAULT, not a ruling.** Fix-pack checklist **93 is OPEN** (verified at
   `3e224a7`). Every `DroneControl` carrier shares `FindTask` (`DroneHub.lua:1-2`,
   `RocketBase.lua:1-2`, `RCRover.lua:4-6` — SOURCE), so the default here is **hubs only**: the
   wrapper's first statement is `if not IsKindOf(self, "DroneHubBase") then return orig(...) end`,
   which is v1's own gate (`Opt_DroneOverhaul.lua:185`). **This is a default the build inherits
   because the ruling has not been made — it is not a recommendation dressed as one.** If the
   owner says "all carriers", the gate is deleted and nothing else changes.
7. **Shuttles are untouched, structurally.** `LRManager` keys its queues by RESOURCE, not priority
   (`LRManager.lua:12-41, :51-88`; `EF-073` corollary), so no band or tier design reaches shuttle
   logistics. Shuttles read hub `deficit_table` through `Request_UpdateDeficits`
   (`DroneControl.lua:121-123`) — a fourth C consumer of the REAL tables, which this design never
   reshapes. ⚠️ Carried forward, not fixed: a shuttle-delivered maintenance resource MISFIRES the
   deliverer handoff (`ShuttleHub.lua:1014` → `StartWorkPhase(shuttle)`, and `CargoShuttle` has no
   `Work` method), dropping the repair back into the hub queues — where the tiers now serve it.
   That makes the tiers *more* relevant on shuttle colonies, and it is a vanilla defect candidate
   in its own right (D06 entry, 07-29). Not this build's scope.
8. **A dust storm — the per-call budget, priced.** A storm puts many buildings into T4 at once.
   Cost per non-empty `FindTask` call = one integer version compare, then O(|T5| + |T4|) validity
   filtering, then up to three C calls. Scale from the only measurement available: **25,184
   `FindTask` calls in 10 game-hours at 3×** on a 9-hub colony (`EF-060`, MEASURED 2026-08-16) ≈
   0.7 calls/second wall-clock. At 50 simultaneous malfunctions that is ≈ 35 request-validity
   checks per second across the whole colony plus ≤ 2 extra C calls per call. **INFERRED, and the
   inference is the arithmetic above — it is not a measurement; the playtest's dust-storm step
   (§8 step 4) is what turns it into one.** Two structural brakes already exist and are not ours:
   `Drone:Idle` only calls `FindTask` when `GameTime() - command_center.no_requests_time > 1000`
   (`Drone.lua:620` — SOURCE), and the empty-tier fast path below never reaches C more than once.
9. **The empty fast path.** `if tier_count == 0 then return orig(self, agent, flags) end` — one
   integer read. The tiers are empty in the overwhelming majority of colony-seconds, so the hot
   seam's normal cost is that compare and nothing else.

---

## 3 · Mechanism — candidate V-a, its rubric re-checked cell by cell

### 3.1 What runs

**One chained wrapper on `TaskRequestHub.FindTask`, installed at FILE SCOPE** (classdef time, so
it propagates through flattening to all 48 carriers — `EF-058` scope clause; the module already
installs there, `Opt_DroneOverhaul.lua:180-212`). On a call:

1. `if not module_active() or not IsKindOf(self, "DroneHubBase") then return orig(self, agent, flags) end`
   — inert for a foreign object before it touches one (`FIX_POLICY` §2).
2. `if tier_count == 0 then return orig(self, agent, flags) end` — the fast path.
3. **Build the T5 pass list** (fresh per call, from the version-stamped membership sets): every
   tiered building `b` with `IsValid(b)` and `table.find(b.command_centers, self)`, contributing
   its demand request when `b.maintenance_phase == "demand"` and its work request when
   `== "work"`, each filtered by `CanAssignUnit()` and `GetTargetAmount() > 0`; plus the
   grid/dome scan of the hub's real `priority_queue[3]` described in the T5 row.
   Build a **proxy** — a plain table carrying
   `priority_queue = {[-1..3] = {}}` with the T5 requests at `[3]`,
   `demand_queues = {[-1..3] = {}}` with `[3][res] = {T5 demands}`,
   `supply_queues = self.supply_queues` (REAL, by reference),
   `under_construction = self.under_construction` (REAL, by reference),
   `restrictor_tables = self.restrictor_tables` (REAL, by reference),
   `lap_start = self.lap_start`, `lap_time = self.lap_time`.
   `FindTask` reads **nothing else of `self`** and never hands `self` to C — re-read at
   `_TaskRequest.lua:71-83` this session, SOURCE, `EF-072`. The proxy is therefore complete and
   the lap write-back lands on the proxy harmlessly.
4. `local r, pr, res, amt, p = orig(proxy, agent, flags)`. **If `r` (or `pr`) is not one of the
   requests we put in the proxy, DISCARD the result and continue** — see §3.2, this is the one
   place this spec departs from the bands report's §4.2 V.
5. Repeat 3–4 for T4. Then `return orig(self, agent, flags)`.
6. Return in vanilla shape `(request, pair_request, resource, amount, priority)`; the drone uses
   four of the five (`Drone.lua:621-629` — SOURCE).

**The tier membership sets** are two weak-keyed tables of buildings plus an integer
`tier_version`, held as upvalues of the class-table functions. Maintained by chained wrappers on
**`RequiresMaintenance.SetMalfunction`** (add), **`RequiresMaintenance.Repair`** (remove) and
**`RequiresMaintenance.DisableMaintenance`** (remove), and rebuilt on **`OnMsg.LoadGame`** by a
synchronous walk of the `RequiresMaintenance` label testing `is_malfunctioned`.

> ⭐ **The wrapper set is provably complete, and this is the strongest structural claim in the
> spec.** `is_malfunctioned` is written in exactly four places in the entire tree (SOURCE, swept
> 2026-09-01 over `Lua/` + `CommonLua/`): the classdef default `RequiresMaintenance.lua:41`, and
> `:252` / `:271` / `:324` — the three methods above. There is no other entry to or exit from the
> malfunctioned state. `ElevatorBase:SetMalfunction` (`Elevator.lua:1003-1006`) forwards to
> `RequiresMaintenance.SetMalfunction(self)` by dotted call, so the base wrapper catches it too.
> `BaseRover:Repair` is a **name collision, not a carrier**: `BaseRover`'s `__parents` are
> `{Demolishable, DroneBase, PinnableObject, SkinChangeable, TaskRequester, DepositRevealer,
> SpecialOrientation}` — no `RequiresMaintenance` anywhere (SOURCE, `BaseRover.lua:2-12`), so a
> wrapper on `RequiresMaintenance.Repair` never reaches it.

**`OnMsg.LoadGame` is early enough and must run inline.** No game-time thread runs before
`PostLoadGame`: the load screen is `game_blocking` (`Savegame.lua:1098`; `LoadingScreen.lua:57-60`,
released at `:184` after `LoadGame` returns) and `UnpersistGame :801-818` orders
`PersistLoad → PersistPostLoad → LoadGame → fixups → PostLoadGame` (SOURCE, bands report §3).
The walk must **not** be spawned in a thread — `CreateGameTimeThread` defers (`EF-029`).

**`AllMapsForEach(true, "DroneControl", …)` is the walk shape for anything hub-side** (`EF-053`:
19 objects vs 13 from the three concrete classes; a rocket leg must never be named `RocketBase`).
This design needs no hub walk at all — recorded so the build does not add one out of habit.

### 3.2 The one departure from the bands report's §4.2 V, and why

The report's V hands the proxy the real `under_construction` and returns whatever C returns. This
spec adds step 4's **discard-and-continue**. The reason is a hazard the report did not name:

- If the proxy carries an **empty** `under_construction`, construction is excluded from the tier
  passes and demoted below every open tier — a starvation shape `DRONE_PRIORITY_SYSTEM.md` §6
  landmine 6 explicitly warns about — and it makes the proxy depend on C tolerating an empty
  table, which nothing measures.
- If it carries the **real** one and the result is returned blindly, C may choose a construction
  task during the T5 pass, and the wrapper would return it as if it were T5 — which **promotes**
  construction above both tiers. Whether that happens depends on C's internal scan order, which is
  unread (`DRONE_PRIORITY_SYSTEM.md` §6 landmine 7).
- **Discard-and-continue removes the dependency entirely.** The proxy carries the real table (so
  C sees exactly what it always sees, and no empty-table tolerance is assumed); a non-tier result
  is dropped and the next pass runs; the final `orig(self, …)` re-decides over the full real
  tables and will return that same construction task if it is genuinely the best. Cost: one extra
  C call in the rare case. **No assumption about C's ordering is made anywhere.**

This is a design decision derived from SOURCE, not a measurement, and it is INFERRED. It also
narrows E-4(iii): the card must now assert *which* request comes back, not merely that one does.

### 3.3 The 11-row rubric, re-checked — every citation re-read this session, none inherited

| row | question | V-a verdict | evidence, re-verified 2026-09-01 |
|---|---|---|---|
| R1 | Mod Options toggle OFF | **PASS, instant** (SOURCE) | the real tables were never touched; the per-call `module_active()` gate makes the next call byte-vanilla. Nothing to put back, so no `on_deactivate` state work at all (the food patch of §2 row 3 is the sole exception and has its own restore) |
| R2 | `SMROptInPack_Disabled` veto | **PASS** (SOURCE + `EF-002`) | file-scope installers hook before `Register`; the gate reads the registry status AND the veto per call (`FIX_POLICY` §2, the A1 lesson). No const is written — ever, in V-a |
| R3 | Mod-Manager disable / uninstall of a save made with tiers ACTIVE | **PASS by construction** (SOURCE) | no key 4/5 in any real table (nothing is filed); no closure on any game object (every wrapper lives in a class table = a persist permanent, `persist.lua:157-165`); no captured frame (all five wrapped bodies are synchronous — §5); nothing stranded (the filing is vanilla's own); nothing widened, so no nil-index on any vanilla loop |
| R4 | existing saves — hubs, rockets, rovers built under vanilla | **PASS by construction** | no table shape changes, so no top-up exists to get wrong. Works on any save, no new game |
| R5 | persisted footprint | **PASS** (SOURCE, `EF-072`) | ZERO new persisted names; `l3_save_footprint.py` §3 still reads exactly the five `SMRFixPack_*`. The membership sets are reachable ONLY as upvalues of class-table functions, and the persist walk does not descend into class tables, `_G` or a mod env. The `EF-072` caveat is honoured: no persisted thread frame, no game-object field and no `GameVar` references them — the frame half is what §5 proves |
| R6 | the §10 duplicate leak | **n/a** | nothing enters the real tables at 4/5, so `DroneControl:RemoveBuilding`'s file-local `-1..3` loop (`:735`, `DroneControl.lua:8`) covers everything this module can produce. E-3 is not owed |
| R7 | Save Rescue | **PASS** | nothing for it to do. The Rescue detects by a fixed name table only (`D13_EXPOSED_SET.md` §10.2) and would have had to learn a queue shape for any persisted-band design |
| R8 | patch-rot exposure | chained wrappers ×5 + one message handler; hot cost one integer compare | **No C signature knowledge anywhere** — the proxy goes through `orig`, so a C ABI change breaks vanilla before it breaks us. The rot surface is one sentence: *"`FindTask` reads only `priority_queue`, `supply_queues`, `demand_queues`, `under_construction`, `restrictor_tables`, `lap_start`, `lap_time` of `self`"* (`_TaskRequest.lua:71-83`), checkable by the fpk extraction diff at every game update (`WORKFLOW.md` release gate). Prior art for the alternative: "Smarter Drones" re-implemented the finders in Lua and rotted into a 150 GB log; V re-implements nothing |
| R9 | flattening | **PASS + identity proof owed at build** | one classdef write on `TaskRequestHub` pre-`Autorun` reaches the 48 carriers (`EF-058` scope clause); `EF-066` makes an identity check on a live instance a sound witness. The build's desk gate runs `harvest_wrap_targets.py --check` and the A/B's conditions header prints the wiring proof |
| R10 | the DISTINCTION — 5 vs 4 vs player-3 still visible to the matcher | **PASS in mechanism, UNMEASURED in behaviour** | strict between tiers because a pass returns before the next runs; C's own order within a tier. ⚠️ **Strict *per hub poll*, not colony-global** — a far hub's drone can take T4 while a near hub's T5 waits for that hub's next poll (bands report §8; persisted bands share this property). The behavioural claim is **E-9 territory and is not made here** |
| R11 | interactions | **PASS** on every enumerated seam | **F77**: none — no registration change. **D09**: none — it writes two label modifiers by id, disjoint props. **Fix pack**: nothing wraps `FindTask`; `Fix_DroneUnreachableForever` sits on `CleanUnreachables` and chains in either order (`EF-054`). **Hub self-repair** (`Drone.lua:593-606`) still runs first. **`ImproveDemandRequest`** — the gap the review found, now guarded (§2b rule 5). **Deficits** are computed over the real tables only, so shuttles are unchanged. **Commander profiles**: `Inventor` ramps repair *throughput*, never claim order — orthogonal, but it makes cross-sitting comparisons invalid (D06 entry) and the playtest must record the profile |

**The two UNKNOWN cells, restated as the build's first gate:** **E-4(iii)** — a mod-built table
set is honoured by `Request_FindTask`, and specifically *which* request comes back given the real
`under_construction` alongside a one-entry tier queue (§3.2 sharpens this). **E-8** — a
wrapper-substituted pairing is claimed via `RequestAssignUnit` (`Drone.lua:901`/`:941`) and
executed through `MaintenanceDroneUnload :418-426` like a matcher-chosen one, **and the tier
delivery ARRIVES at the tier building** (the `EF-074` guard assertion the review added).
**E-4(ii)** decides V-b vs V-a only and changes nothing else in this spec.

### 3.4 The recorded fallbacks

| if | then | what changes in this spec |
|---|---|---|
| E-4(ii) reads **call-time** | **V-b** is permitted: real keys 4/5 in the proxy with `const.TaskRequest.MaxBuildingPriority` flipped `3 → 5 → 3` around the single C call | one C call instead of up to three; a literal 4/5 for the matcher's eyes only. **No real table is widened either way**, so the module locals stay at 3 and nothing nil-indexes. The tier table, the guard, the footprint statement and the playtest are unchanged |
| **E-4(iii) fails** (C does not honour a mod-built set) | **P — finder pre-emption.** Same tier sets; instead of a proxy the wrapper iterates T5 then T4 itself: `demand` phase → `self:FindSupplyRequest(agent, req:GetResource(), req:GetTargetAmount())` and return `(supply, demand, res, amount)` — the precedent is vanilla's own hub self-repair (`Drone.lua:593-606`); `work` phase → return `(work_req, nil, "repair", Min(DroneResourceUnits.repair, target))` — the precedent is `Drone.lua:604` and v1's moonlighting (`:259-260`). Reachability via `agent.unreachable_buildings`, which the finder takes | R1–R9 and R11 identical. **R10 changes owner**: order within a tier becomes the mod's policy (life-support first, then nearest) instead of C's. R8 grows: the wrapper reconstructs pairings for work requests. Still needs E-8; does not need E-4 |
| **E-8 also fails** | **2-S — table surgery at band 3.** No view, no substitution: on `SetMalfunction` move the building's two maintenance requests from `queue[p]` to `queue[3]` in every covering hub's three tables (`remove_entry` + append — the exact ops `DroneControl:AddBuilding :694-706` and `RemoveBuilding :739-744` perform); on `Repair`/`DisableMaintenance` move them back to `b:GetPriorityForRequest(req)`; post-wrap `DroneControl:AddBuilding` to re-apply after any re-registration; `OnMsg.LoadGame` sweep re-applies. No `UpdateDeficits` churn — deficits sum over all bands (`:133-161`), so a move changes no total | **R10 FAILS by definition**: one band, 5/4/player-3 collapse. R1–R9/R11 pass from citations with no experiment at all. The residue is *"a broken building's requests filed one band above its arrow until its next re-registration"* — **the exact shape vanilla gives a broken pipe** (`SupplyGridBreakable.lua:48-56`). This is the **citation-complete floor**: it ships without any running game |
| the owner rules the 5/4/3 distinction a **preference** | **D** — 2-S restricted to the five `AirProducer`/`WaterProducer` templates: the devs' own tier, on the buildings they never extended it to | the narrowest honest form. Its disclaimer writes itself (§7) |

---

## 4 · Savegame footprint statement (`FIX_POLICY` §3 / §3a shape)

**Expected footprint: ZERO new persisted names and zero new persisted values.**
`tools/l3_save_footprint.py` §3 must still read **exactly five** — the `SMRFixPack_*` fields and
modifier ids this mod already writes, which are save contract and unrenameable (ban 1).

**The argument, per structure, via `EF-072`'s only-route rule:**

| structure | route to a save | verdict |
|---|---|---|
| the two tier membership sets + `tier_version` | reachable only as upvalues of functions stored in class tables. `_G` (`persist.lua:61`, `:104`), `g_Classes` and every class table by name (`:157-165`) and each mod env (`Mod.lua:1642-1644`) are PERMANENTS — substituted by label, never walked | **no route exists** |
| the per-call proxy table | allocated inside a synchronous call and dropped on return; never stored anywhere | **no route exists** |
| the wrapper functions themselves | live in class tables. Class tables are permanents; the functions *inside* them are not individually registered, but nothing copies one onto an instance — and that copy is the whole of `EF-069`, which is why **no class-level `GetPriorityForRequest` override appears anywhere in this design** | **no route exists** |
| any wrapper's stack frame | all five wrapped bodies are synchronous (§5), so no frame can sit below a `Sleep`/`WaitMsg`/`WaitWakeup` on a game-time thread — `EF-023` route (a) is closed by construction, and with it route (b) for the tier sets | **no route exists** |
| the food-service default patch (§2 row 3, if built) | a NUMBER written on four class tables. Class tables are permanents restored by name; no template sets `priority`; an instance carries the key only after a real change (Q4, live-confirmed 2026-07-31) | **no route exists**; reverts by Q4 |

**What remains owed to a measurement, stated plainly:** **E-4(iii) must also witness whether C
writes into the proxy** — specifically the `p_queue.index` cursor the 2018 Lua mirror reads
(`local index = requests.index or 1`). If it does, the write lands on our transient table and is
dropped on return, which changes nothing above; the card inspects it so the answer is on record
rather than assumed. And `EF-072`'s guard word — *ONLY* — is what §5 exists to hold.

⛔ **What this section does NOT claim.** "Clean revert" beyond the bands report's **YES-IF** form.
The footprint argument is complete from citations; the *verification* is the build's own
Mod-Manager-disable leg and the `FIX_POLICY` §8 both-config test (§8 steps 6–7). Until those run,
the honest sentence is *"designed to leave nothing, argued from source, not yet witnessed."*

---

## 5 · Blocking analysis — every wrapped body, run this session

`python tools/blocking_analysis.py` over the design's wrap targets, 2026-09-01
(15,106 names; 633 yield directly somewhere; 711 block on every definition):

| target | tool verdict | adjudication |
|---|---|---|
| `TaskRequestHub.FindTask` | `clear` | ✅ synchronous — a C call plus lap arithmetic (`_TaskRequest.lua:71-83`) |
| `RequiresMaintenance.SetMalfunction` | `clear` | ✅ |
| `RequiresMaintenance.DisableMaintenance` | `clear` | ✅ |
| `Drone.ImproveDemandRequest` | `clear` | ✅ synchronous — finders, claim arithmetic, no yield (`:760-813`) |
| `TaskRequestHub.FindSupplyRequest` / `FindDemandRequest` | `clear` | ✅ (needed only by fallback **P**) |
| `Drone.CleanUnreachables` | `clear` | ✅ (v1's moonlight seam, kept — §6) |
| `RequiresMaintenance.Repair` | **AMBIGUOUS** — *1 of 6 defs yields directly: BaseRover* | ✅ **false alarm, hand-adjudicated.** The yielding definition is `BaseRover:Repair` (`BaseRover.lua:271`, `PlayState`), and `BaseRover` does not inherit `RequiresMaintenance` (`:2-12` — SOURCE). `RequiresMaintenance:Repair` (`:265-297`) contains no `Sleep`/`WaitMsg`/`WaitWakeup`/`PlayState`. A file-scope wrapper on `RequiresMaintenance.Repair` never reaches the rover method |
| `DroneControl.AddBuilding` / `RemoveBuilding` | **BLOCKS** — *via unambiguous `UpdateDeficits`, `UpdateDumps`* | ✅ **false positive of the tool, hand-adjudicated.** Both `DroneControl:UpdateDeficits` (`:105-117`) and `UpdateDumps :581-584` → `UpdateRestrictors :551-560` only `Wakeup(t)` an existing thread or `CreateGameTimeThread(...)`; the `WaitWakeup()` lives **inside the spawned closure**, not in the caller's flow. The tool's propagation rule cannot see a blocking call that sits inside a function passed to a thread constructor. Both methods are synchronous for the caller. *(Wrapped only by fallback **2-S**; V-a wraps neither.)* |

⚠️ **Recorded for the tool, not fixed here (out of scope, filed):** `blocking_analysis.py`'s
propagation marks a caller blocking when a callee's *text* contains a yield, including yields that
live inside a closure handed to `CreateGameTimeThread` / `CreateRealTimeThread`. That is a
systematic false-positive class, it will recur on any `DroneControl` method, and it is a tooling
change, not a drone change.

---

## 6 · What replaces v1, file by file — the rebuild lands as ONE piece

Target: `Code/Opt_DroneOverhaul.lua`, rewritten in one commit. **ONE toggle, all or nothing**
(settled 07-31); no sub-toggles; D09's dials stay a separate module.

| part | v1 today | the rebuild |
|---|---|---|
| **1 · closest-fleet claim gate** | `Opt_DroneOverhaul.lua:180-212` + `closest_covering_hub` (`:130-152`) + the `strikes` / `cover_cache` / `STRIKES_MAX` / `STRIKE_TTL` / `COVER_CACHE_TTL` machinery | **DELETED** (settled 07-31, not re-litigated). It arbitrates a 12 % slice already decided by the deliverer handoff, and B2 measured it firing once in 25 malfunctions for a one-minute effect |
| **2 · repair moonlighting** | chained POST-wrapper on `Drone:CleanUnreachables` gated to the Idle tail (`:214-278`), F86 Site 2's repaired call position | ⭐ **KEEP, mechanism UNCHANGED — recommendation, §9 ask 3.** See the reasoning box below |
| **3 · telemetry** | `SMROptInPack.DroneReport()` (`:283-330`), registered unconditionally, read-only | **KEEP and EXTEND**: add per-hub `T5=<n> T4=<n>` depths and the counters `tier5_served / tier4_served / improve_declined / moonlighted`. Still unconditional and read-only so an OFF leg can be measured (the ListFixes lesson) |
| **4 · the tiers** | — | **NEW**: the `FindTask` wrapper, the three lifecycle wrappers, the `OnMsg.LoadGame` rebuild, the `ImproveDemandRequest` guard (§3.1, §2b rule 5) |
| **5 · the food default** | — | **NEW, conditional on §9 ask 2**: a class-default write on the four `ServiceWorkplace`+Food templates plus a **targeted** re-registration of those four (`DisconnectFromCommandCenters()` + `ConnectToCommandCenters()` — the vanilla protocol, `RequiresMaintenance.lua:289-291`) on activate / `LoadGame`, and the reverse on deactivate |

> **Moonlighting — KEEP, and why.** It is the one part of v1 that serves ground the tiers do not:
> the tiers reorder work **within a hub's poll**, and R10's per-hub caveat is exactly the gap a
> workless drone helping a saturated neighbour closes. Three supporting facts: (a) it was never
> measured inert — the B2 table records `vetoed`, not `moonlighted`, so "it did nothing" is a
> claim nobody has evidence for either way; (b) its F86 Site 2 leak was repaired 2026-08-01 and
> verified by PT-58, and `Drone.CleanUnreachables` is `clear` (§5); (c) it reads the FLAT
> `const.MaxBuildingPriority` (`:239`), which this design never touches, so there is **no
> interaction between it and the tiers** to reason about. **Not extended with tier awareness in
> this build** — that would put two new variables in one A/B, which is how v1 got here. The
> counter-argument, recorded honestly: it is one more hot-path scan over `city.labels.DroneControl`
> whose value is unproven, and dropping it would make the rebuild a strictly smaller product.
> **The owner's call.**

### 6.1 The `Require` block — F107, and the checklist-84 interplay

The module calls **no `Require` at all** today; its three capture-and-install sites are
allowlisted in `tools/harvest_wrap_targets.py` with Src citations, and the allowlist entry is
*"a receipt for an open case, never a permanent waiver"* (`FIX_POLICY` §2). **This build is the
"next planned edit of the file"** that checklist item 84 option (a) was waiting for. So:

**The rebuild declares every `(class, method)` pair it installs on or captures from:**

```
{ class = "TaskRequestHub",      method = "FindTask" },
{ class = "RequiresMaintenance", method = "SetMalfunction" },
{ class = "RequiresMaintenance", method = "Repair" },
{ class = "RequiresMaintenance", method = "DisableMaintenance" },
{ class = "Drone",               method = "ImproveDemandRequest" },
{ class = "Drone",               method = "CleanUnreachables" },   -- moonlighting, if kept
{ class = "DroneHubBase" },                                        -- the hubs-only gate's class
{ global = "DroneResourceUnits", kind = "table" },
{ path = { "const", "rfWork" }, kind = "number" },
```
⛔ **`Drone.Idle` is NOT in the list** — the rebuild neither wraps nor captures it. v1's
`install_error` checks it only as the moonlight precondition; the F107 rule is about pairs
*installed on or captured from*, and an existence check is neither. Keep the check as an inline
guard, out of `Require`.
⛔ **No per-game runtime global in `Require`** (the F110 rule): `UIColony`, `Cities`, `LoadedMaps`
are read with `rawget` inside handlers, never declared.

**Consequence, and it must land in the same commit:** the two `Opt_DroneOverhaul` rows retire from
`tools/harvest_wrap_targets.py`'s allowlist (`Drone.CleanUnreachables`, `TaskRequestHub.FindTask`).
`Opt_MultipleSuns`'s `SolarPanelBase.GameInit` row stays — untouched by this build. The build's
desk gate is `python tools/harvest_wrap_targets.py --check` GREEN with two fewer allowlist rows.
**Checklist 84 is answered by construction, not by a separate decision** — say so when it lands.

---

## 7 · The disclaimer draft (research-brief spec — player wording is the owner's, §9 ask 5)

The research brief requires a design-drift disclaimer in `MOD_DESCRIPTION.md` on the rebuild:
*what was done, the limits without hedging, the off-ramp*, and **not legal cover**. It could not be
written honestly until the footprint was known; §4 is now its substance.

> **Drone repair urgency — what this changes, and what it does not.**
>
> This is a **design change, not a bug fix.** Surviving Mars decides how urgently a repair is
> served from the same arrows you use to decide who gets scarce resources first — a question about
> supply, answering a question about urgency. This module separates them: a **broken** building is
> served ahead of routine traffic, and a broken oxygen or water producer is served ahead of that,
> at the same urgency the game already gives a broken pipe or a cracked dome. Nothing else moves.
> Your arrows keep meaning what they show.
>
> **What was actually done to keep your save safe.** The new ordering is never written into your
> colony. The game's own queues are left exactly as they are; the module builds the ordering
> fresh, in memory, each time a drone asks for work, and throws it away again. So a save made with
> this on contains **nothing from this module** — no new fields, no changed priorities, no
> leftover work parked somewhere the game will not look. Turn the toggle off and the very next
> drone behaves like vanilla; remove the mod entirely and your colony loads with nothing to clean
> up and nothing for a repair tool to find. That is a design property, not a promise about your
> particular save — see the limits.
>
> **The limits, without hedging.** It touches the deepest shared queues in the game — drone hubs,
> rovers and the rocket cargo path all run through them — and it is the part of this mod where we
> can least claim every interaction has been found. Two specific effects you should expect and we
> are not hiding: **(1)** while parts are flying to a broken building, they can no longer be
> diverted to a higher-priority delivery en route. That is deliberate — it is what stops the
> urgent repair from being robbed — but it is a real change to how deliveries behave.
> **(2)** This changes *which job is served first*, never *which pile of resources feeds it*.
> The game strongly prefers loose resources on the ground over your storage depots, and this
> module does not change that: a broken water extractor can still wait on parts scavenged from
> across the map while a full depot sits next to it. If that is your complaint, this is not the
> fix for it.
>
> **The off-ramp.** It is off until you turn it on, it is one switch, and everything else in this
> mod works normally with it off. If you want the rest without the redesign, leave it off.

⚠️ **Two sentences in the draft above cannot ship until they are witnessed**, and the build brief
gates them: *"a save made with this on contains nothing from this module"* and *"your colony loads
with nothing to clean up"* are the §8 steps 6–7 outcome, not desk output. If either leg does not
run clean, the wording narrows to what was measured before the module ships.

**PT-52's archival, as an edit for the owner to apply (not applied here):** the frozen PT-52
Triggers A / B / B2 block in the fix pack's `docs/archive/PLAYTEST_ARCHIVE.md` is marked
**deprecated-by-redesign** — obsolete, *not* un-run, and never reported as outstanding coverage —
and replaced by the single item in §8. Its B2 protocol and CAN/CANNOT lists stay as reference
material; §8 step 5 is derived from them.

---

## 8 · The ONE playtest that replaces PT-52

**One item, numbered steps, one sitting, attended.** Matches how the module ships: a single
product, one toggle. **Do NOT create a family of drone PTs — that is the failure mode the freeze
existed to end.** Setup: a colony with ≥ 2 drone hubs with overlapping coverage, extenders
present, work happening; **record the commander profile** (Inventor's ramps drift repair
throughput over sols — D06 entry); `ListFixes` shows `DroneOverhaul [active]`;
`SMROptInPack.DroneReport()` once as the baseline.

1. **Tier precedence, n ≥ 3.** Break a life-support producer and an ordinary building of the same
   class-of-work simultaneously and equidistant from one hub; repeat three times with the pair
   swapped left/right. **EXPECTED:** the producer reaches `phase=work` first on every repeat.
   **BROKEN:** the ordinary building wins, or the order is random. *(This is E-9's question asked
   as a playtest; the claim is not made anywhere until this step passes.)*
2. **T4 above the arrows.** Set an ordinary building's arrow to **High** and break a *different*
   ordinary building at default. **EXPECTED:** the broken one is served first. **BROKEN:** the
   High one wins — the tiers are not reaching the matcher.
3. **The `EF-074` guard, live.** With a maintenance delivery in flight to a broken building, set a
   third building of the same resource to **High**. **EXPECTED:** the delivery still arrives at
   the broken building; `DroneReport` shows `improve_declined` climbing. **BROKEN:** the drone
   re-routes. Then repeat with the *destination* made unreachable — **EXPECTED:** the drone drops
   it the vanilla way and does not loop (the `must_change` carve-out, §2b rule 5).
4. **Dust-storm surge.** Let (or cheat) a storm break many buildings at once. **EXPECTED:** no
   frame-rate change attributable to the module; producers still first; **construction sites still
   progress** (landmine 6 — this is the starvation check); `DroneReport` T4 depth matches the
   wrench count. **BROKEN:** construction stalls colony-wide while tiers are open.
5. **A/B, the real verdict** — the `91_Stress.lua` v2 lifecycle harness, B2 protocol, under
   **REPRESENTATIVE** conditions (see §8a). Same quicksave both legs, same `scope`/`n`/`seed`,
   normal-to-3× speed. Read the lifecycle decomposition (`haul queue` / `haul exec` / `claim wait`
   / `travel` / `repair`), **not** total clearance time.
6. **OFF-flip mid-session.** Toggle the module off with tiers non-empty. **EXPECTED:** the next
   drone poll is vanilla; nothing is stuck; `DroneReport` still prints (it is unconditional).
7. **Mod-Manager disable + restart + load-clean.** Save with tiers ACTIVE and work outstanding →
   **disable the OPT-IN MOD in the Mod Manager** → restart → load. **EXPECTED:** 0 `[LUA ERROR]`
   naming this mod, no stranded work, the colony runs. ⛔ **A toggle cannot answer this** — with
   the module merely off the env is present and any captured frame reads inactive and no-ops, so
   it reads clean by construction (`EF-002`; `Opt_DroneOverhaul` leaked at 98 errors/session with
   its own toggle OFF — that is how F86 Site 2 was found). Mod-Manager-disable is the measured
   equivalent of a real uninstall (PT-20: 98 vs 98 on the same save).
8. **Both-configuration ship test** (`FIX_POLICY` §8): the whole of steps 1–7's headline checks
   re-run **with the fix pack installed** and **with it absent**, naming the version. The
   standalone invariant is this mod's product claim.

### 8a · The A/B and probe plan

**The A/B must be representative, and that is the B2 lesson, not a nicety.** The 07-29 run was
internally valid and externally invalid: depots deliberately pre-filled, hubs carrying 14–24 idle
drones each, layout optimised for drone access. *"This run may have engineered away the very
phenomenon it was built to measure"* (D06 entry). So the rebuild's A/B:
- **right-size fleets** toward the D08 advisory's suggestion, raising contention;
- **do NOT pre-fill depots** — scarcity is the deployment condition;
- run against real industrial density during a genuine demand surge;
- **log the commander profile and the drone stats** with the numbers (the v2 conditions header
  does this; `Compare()` flags condition mismatches itself);
- **≥ 3 seeds per leg** before believing any delta — one pair is not a verdict at n = 25.

**A D06 `RunAll` probe — designed here, NOT built (checklist 83 item 4; the kit is SHARED and
editing it needs the owner's go).** D06 is the only module of the eight with no probe
(`STATE.md` build state: this mod owns 9 of the shared 100, D06 owns none).

- **Registration:** `SMRTest.Register("DroneOverhaul", { title = …, kind = "behavior",
  fix = "DroneOverhaul", run = … })` behind the shared `opt_gate("DroneOverhaul")` (`60_Probes_Opt.lua:26-39`),
  so a fix-pack-only run SKIPs cleanly.
- **What it asserts, with stand-ins** (the D04/D07/D12 pattern — plain tables, `IsValid`/`IsKindOf`
  stubbed via `SMRTest.WithGlobals`): build a stand-in hub carrying the five queue fields plus the
  two lap fields; a stand-in malfunctioned `AirProducer` and a stand-in ordinary building; drive
  `TaskRequestHub.FindTask` and assert the T5 request is offered before the T4 one and before the
  real band-3 contents. Drive `Drone.ImproveDemandRequest` with a tier demand and assert it
  returns unchanged when `must_change` is false **and delegates when it is true**.
- ⭐ **The vanilla-control clause is mandatory — D12's is the model** (`60_Probes_Opt.lua:490-494`,
  the 08-24 probe rule). Before asserting the module's behaviour, the probe drives the SAME
  fixture with the module gate closed and asserts vanilla's answer stands. If the control ever
  fails, the probe reports *"the game changed the thing this module exists to change — re-derive
  D06 before trusting any result below"* rather than silently passing.
- **What it cannot reach and must not pretend to:** anything the C matcher decides. The probe
  scores the module's Lua contract; the matcher's behaviour is steps 1–5 above.

**Desk instruments — the build's exit gate, all GREEN before the commit:**
`python tools/doccheck.py` (both repos) · `python tools/l2_reload_sim.py --strict` ·
`python tools/l3_save_footprint.py` (must still read exactly five) ·
`python tools/harvest_wrap_targets.py --check` (two fewer allowlist rows — §6.1) ·
`python tools/blocking_analysis.py` over the wrap set (the §5 verdicts reproduced, with the two
hand-adjudications restated) · a Lua parse sweep of `Code/`.

---

## 9 · Owner asks — one line + pointer each, filed on the fix pack's checklist

1. **Ratify the spec — the mechanism (§3, V-a with P/2-S recorded) and the tier table (§2).**
   This supersedes and answers item 91. **Nothing is built until this line.**
2. **Food-service default 3 (§2 row 3, §6 part 5):** in the rebuild under the same toggle,
   separate, or dropped.
3. **Moonlighting (§6 part 2):** keep or drop — the spec recommends **keep, unchanged**, with the
   counter-argument recorded.
4. **Items 92 and 93, if still open:** run E-4 / E-8 (the build's first gate cannot pass without
   them, and the build's own fallback ladder is written for either answer); tiers on
   rockets/rovers or hubs only (the spec defaults to **hubs only** and says so).
5. **The disclaimer's final player-facing wording (§7).**

---

## 10 · What this spec does NOT claim

- **Any E-4 or E-8 outcome.** Neither has run; the build brief gates on them.
- **Any tier-precedence ORDERING as fact** — that is E-9 / playtest step 1 territory. §3.3 R10 is
  a claim about the *mechanism* (a pass returns before the next runs), not about observed
  behaviour, and it is strict per hub poll rather than colony-global.
- **"Clean revert"** beyond the bands report's YES-IF form, until the build's own A/B and the §8
  step 7–8 legs both run.
- **"No behaviour change" for the `EF-074` guard.** It IS one — deliveries stop being traded up —
  and §2b rule 5 and §7 both price it.
- **Anything desk-derived as "verified."** The blocking-analysis verdicts of §5 are a static tool's
  output plus two hand adjudications, not a running game.
- Counts not emitted by `doccheck --emit-counts`.

---

## 11 · Corrections and filings made with this spec

- ⚠️ **`DRONE_PRIORITY_SYSTEM.md` §6 landmine 8 was announced in fix-pack commit `3e224a7`'s
  message and never written.** The commit touched only `docs/agent/facts/` (verified by
  `git show --stat 3e224a7`), yet its subject line, the bands report §8 and this repo's
  `STATE.md` all say the landmine landed. **Written for real in this commit** as landmine 8 (the
  `ImproveDemandRequest` hijack, `EF-074`), fix pack first.
- ⚠️ **`EF-074` is amended.** It names two guard routes and lists the "decline in
  `ImproveDemandRequest`" one first; without a `must_change` carve-out that route hangs `Deliver`'s
  retry loop on an unreachable destination (`Drone.lua:1246-1264` — SOURCE). The amendment records
  the carve-out and marks the vanilla `do_not_improve_req` seam as unreachable without replacing a
  command body. Fix pack first, mirrored here.
- **No fact was contradicted by Src today.** Every `EF-` cited above was re-read at its cited
  lines and held. `EF-072`'s `FindTask` input list, `EF-073`'s "the band lives in the queue key",
  `EF-071`'s bound rule and `EF-069`'s `:94` route all re-verified.
- **Out of scope, filed by pointer only:** `tools/blocking_analysis.py`'s closure-blind
  propagation (§5) — a tooling defect, not drone work.
