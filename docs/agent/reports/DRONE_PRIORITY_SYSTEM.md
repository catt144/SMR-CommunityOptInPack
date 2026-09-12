# The drone task-priority system — full breakdown

Research 2026-07-31, requested by the owner before any priority work is
attempted: *"I know the game has a player toggled priority system and a hidden
priority system… If there is a life risk drones rapidly repair it… A crack in
the dome, a leak in an O2 pipe, all super fast."*

Every claim below was read from
`A:\SteamLibrary\steamapps\common\Project Spark\ModTools\Src` at build
`1.0.7.396349`. Reference material for the drone rebuild — **not a spec, and
nothing here authorises a change.**

---

## Headline — the observation is correct, but there is NO hidden band

The fast-repair behaviour is real and you identified both instances of it. But
it is not a separate hidden priority tier. **It is two classes auto-assigning
themselves the top of the player's own scale.**

The entire priority system is **five integer bands, `-1` to `3`**, and the
player's scrollbar already reaches the top one.

| Band | Set by | What lives there |
|---|---|---|
| **3** | player (max) **and auto** for broken pipes/cables + dome fractures | "urgent" |
| **2** | player — **the default** | everything else, **including all building maintenance** |
| **1** | player (min) | deprioritised |
| **0** | engine only | storage-depot requests |
| **-1** | engine floor (`Clamp` argument) | reserved; nothing observed assigning it |

Higher is served first — the game says so itself in a code comment: *"we use our
priority to force our consumer element to be serviced first"*
(`SupplyGridBreakable.lua:52-53`).

---

## §1 The bands, and where they are defined

`CommonLua/TaskRequest.lua:15-18` (module locals, overridable from the Consts
editor group `const.TaskRequest`):

```lua
local MinBuildingPriority        = -1
local DefBuildingPriority        =  2
local MaxBuildingPriority        =  3
```

~~**The game does not override them** — a sweep for a `const.TaskRequest`
settings group found no hits, so the CommonLua defaults stand.~~ Separately
`Lua/_GameConst.lua:56` sets `const.MaxBuildingPriority = 3`, with the shipped
comment `-- 1 normal, 2 - high, 3 - urgent`.

> ⚠️ **CORRECTION 2026-07-31, measured live — the struck sentence is WRONG.**
> The experiment module read the group at mod-load time and reported
> `const.TaskRequest.MaxBuildingPriority = 5 (was 3)`. **The group EXISTS and
> already carries 3** before any mod runs, so `ClassesPreprocess` really does
> apply it and the CommonLua defaults are being re-asserted rather than left
> alone. Where it is defined is **not determined**: it is in neither the Src Lua
> tree nor Src's `Data/` (both swept). The likely home is a Consts/`ConstDef`
> preset inside `Data.fpk`, which the 2026-07-29 parity extraction did not cover
> — that job diffed `Lua.fpk` only. **Do not re-assert "the game does not define
> that group" without extracting `Data.fpk` first.**
>
> This matters beyond bookkeeping: the group being live is what makes a
> file-scope `const.TaskRequest` write take effect at all — and therefore what
> made the §8 incident possible.

⚠️ **That comment is misleading and should not be trusted as the band map.** The
actual player default is **2**, not 1 — see §2.

> ⚠️ **CORRECTION 2026-07-31 — the function named below does not exist.** This
> section originally cited `TaskRequestHub:InitRequestQueues`; there is no such
> function anywhere in the tree. **The allocation loop lives in
> `TaskRequestHub:Init()` (`TaskRequest.lua:242-256`)** — i.e. it runs when a hub
> is **constructed**, and *never again*. It does **not** run on load. The wrong
> name carried a wrong implication (that queues get initialised at some
> re-triggerable moment), and that implication broke a live save — see §8.

**The queues exist only for those five values.**
`TaskRequestHub:Init()` (`TaskRequest.lua:242-256`):

```lua
for priority = MinBuildingPriority, MaxBuildingPriority do
    self.priority_queue[priority] = {}
    self.supply_queues[priority]  = {}
    self.demand_queues[priority]  = {}
end
```

**A priority outside `-1..3` has no queue at all.** `_InternalAddRequest`
(`:310-320`) indexes `supply_queues[priority]` / `demand_queues[priority]`
directly — an out-of-range value yields nil and the subsequent index errors.
Because `error()` in this engine **reports and continues** (ENGINE_FACTS), the
practical outcome is a log line and a **silently lost request**, not a crash.
`SupplyGridBreakable.lua:51-52` carries the shipped warning in its own comment:
*"asserts will happen if we go above or below known priorities in DroneHub.lua
code."*

> **Hard constraint for any future work: every priority must be an integer in
> `[-1, 3]`. There is no room to invent a band above urgent.**

---

## §2 The player-facing control

`Lua/Buildings/Building.lua:199` — the property behind the infopanel arrows:

```lua
{ name = T(172, "Priority"), id = "priority", category = "General",
  editor = "number", default = 2, ui = "scrollbar",
  min = 1, max = const.MaxBuildingPriority }
```

So the player gets **three positions — 1, 2, 3 — defaulting to 2**, and band 3
("urgent") is **already reachable by hand**. Bands 0 and -1 are engine-only and
not exposed.

---

## §3 The one function that decides everything

`TaskRequester:GetPriorityForRequest(req)` — `CommonLua/TaskRequest.lua:181-187`:

```lua
function TaskRequester:GetPriorityForRequest(req)
    if req:IsAnyFlagSet(rfStorageDepot) then
        return 0
    else
        return self.priority
    end
end
```

That is the whole base policy: **storage-depot requests sink to 0; everything
else inherits the building's own player-set priority.**

Note the shape — a request-class special case, hardcoded, one branch. **That is
the precedent** any future request-class rule would follow, not a new mechanism.

**Where it is called:** `TaskRequestHub:_InternalAddRequest`
(`TaskRequest.lua:310-312`) and `DroneControl:AddBuilding`
(`DroneControl.lua:693`) — both at the moment a request **enters a hub's
queue**.

> ⚠️ **Priority is baked at queue-insert time.** `_InternalAddRequest` calls
> `GetPriorityForRequest`, then `request:SetPriority(priority)`, then files the
> request into `queue[priority]`. Calling `SetPriority` later does **not** move
> it between queues. Changing a live building's effective priority requires a
> **re-registration** — remove and re-add, which is what
> `DroneControl:ReconnectTaskRequesters` (`DroneControl.lua:779-785`) does and
> which vanilla already performs routinely (hub toggle, extender flap, radius
> change, nearby placement).

---

## §4 The "hidden" system — three overrides, and that is all of them

A whole-tree sweep for `GetPriorityForRequest` found exactly four definitions
(one base + three overrides) and two aliases.

> ⚠️ **CORRECTION 2026-09-01 (BANDS_CLEAN_REVERT, Src re-read): there is a FOURTH
> override — `RCTransport:GetPriorityForRequest` (`Lua/Units/RCTransport.lua:217-223`)
> returns `-1` for the transport's own `resource_requests` supplies and `self.priority`
> otherwise.** It is a unit, not a building, and grants no urgency, so nothing in §5–§7
> changes; the count "three overrides" in this heading is wrong as a count. The two
> `ConstructionSite` aliases (`:2082`, `:2199`) read `RequiresMaintenance.GetPriorityForRequest`
> off a bare classdef, and `RequiresMaintenance` defines no such method — they evaluate
> to `nil` and add nothing.

### 4a. Broken pipes and cables → **3** — *your O2 leak*

`Lua/SupplyGridBreakable.lua:48-56`:

```lua
function BreakableSupplyGridElement:GetPriorityForRequest(req)
    if req == self.repair_resource_request or req == self.repair_work_request then
        return 3 --Drones automatically repair cables with the priority of cable construction.
    else
        return Clamp(TaskRequester.GetPriorityForRequest(self, req), -1, const.MaxBuildingPriority)
    end
end
```

Both legs — the **resource haul** and the **repair work** — jump to 3.

### 4b. Dome fractures → **3** — *your crack in the dome*

`Lua/Passage.lua:485-491`: identical shape, for `fracture_demand_request` and
`fracture_work_request`.

### 4c. Track elements → **no bump**

`Lua/Buildings/TrackElement.lua:172-174` overrides the method but only to apply
the `Clamp`; it grants no urgency. Tracks are **not** in the fast-repair club.

### 4d. Aliases

`Lua/Buildings/ConstructionSite.lua:2082` and `:2199` set
`GetPriorityForRequest = RequiresMaintenance.GetPriorityForRequest` — an
inherited reference, not a distinct policy.

---

## §5 THE GAP — ordinary building maintenance has no override at all

`Lua/RequiresMaintenance.lua` **defines no `GetPriorityForRequest`.** Its two
requests therefore fall through to the base function and inherit `self.priority`
— the player's arrows, default **2**:

- `maintenance_resource_request` — the **demand/haul** leg (`StartDemandPhase`);
- `maintenance_work_request` — the **repair** leg (`StartWorkPhase`).

**Consequence:** a malfunctioned Oxygen Factory's parts delivery is filed at
priority 2, competing on exactly equal footing with routine resource shuffling
from every other default-priority building on the map. A cracked pipe beside it
is at 3 and jumps the whole queue.

**This is the mechanism behind the measured 3h03m hauling leg** (PT-52 B2 — see
the D06 entry): the delivery is not slow because hauling is slow, it is slow
because **nothing marks it as more important than routine traffic.**

### The developers' actual rule, read off their own code

The pattern in §4 is **not** "repairs are urgent". Tracks are repairs and get
nothing. The rule they implemented is narrower and more specific:

> **Life-support-critical repairs are urgent.**

They applied it to the **grid** (pipes and cables carrying air and water) and to
the **dome shell** (fractures venting atmosphere) — and never extended it to the
**buildings that produce** the air and water. A broken Oxygen Factory is exactly
as life-threatening as the pipe leading out of it, and sits a full band lower.

**That framing matters for policy.** Extending the rule to life-critical
producers is *completing a policy the developers started*, not inventing one —
a materially different argument from "we think repairs should be faster", and
the difference is the one FIX_POLICY §4 cares about.

---

## §6 Landmines for anyone implementing against this

1. **The `-1..3` ceiling.** No new band. Any bump is *into* an existing band,
   and the only headroom above the default is **one step: 2 → 3**.
2. **Band 3 is not exclusive.** Putting maintenance at 3 makes it
   indistinguishable from a dome breach *and* from any building the player set
   to max by hand. A flat bump therefore flattens two distinctions at once.
3. **Priority is baked at insert.** A dynamic "urgent while broken" needs a
   re-registration to take effect (§3), not a `SetPriority` call.
4. **Instance-level method flattening.** `RequiresMaintenance.lua:94` does
   `self.GetPriorityForRequest = g_Classes[self.class].GetPriorityForRequest or
   TaskRequester.GetPriorityForRequest` — but **only in the `else` branch**, for
   buildings that do *not* accumulate maintenance. Maintenance buildings keep
   normal method lookup, so a class-level override reaches them. Non-maintenance
   buildings that took that branch hold a direct function reference and would
   **not** see a later class patch. Not a hazard for maintenance work; record it
   before touching anything else through this method.
   > ⛔ **AMENDED 2026-09-01 — this IS the hazard, and it is a save-safety one, not a
   > reach one (EF-069).** Class-table functions are not persist permanents
   > (`CommonLua/Core/persist.lua:157-165`), so the value `:94` writes onto every
   > no-maintenance building at construction is serialised BY VALUE. With a class-level
   > override installed at file scope, that value is the MOD's closure: vanilla itself
   > copies it into the save of every no-maintenance building built while the mod is
   > installed (the EF-022 route, executed by shipped code). Any "urgent while broken"
   > design must therefore re-file requests in the hub's own tables (or substitute at
   > `FindTask`), never override this method on a class a no-maintenance building
   > inherits. Full route and the falsifier: opt-in mod
   > `reports/DRONE_BANDS_CLEAN_REVERT_20260901.md` §4.1, E-6.
5. **Overriding the player.** `self.priority` is the arrows the player set. Any
   automatic bump overrides an explicit player choice. Deciding whether a bump
   is *absolute* (always 3) or *relative* (preserves the player's ordering among
   affected buildings) is a design decision with real UX consequences, not an
   implementation detail.
6. **Starvation, mirrored.** Whatever is promoted, something else is demoted.
   Promoting maintenance colony-wide can starve food delivery and construction
   in a colony with many simultaneous breakdowns — the same failure D06's
   claim gate already carries a strike/TTL valve for, one layer up.
7. **The matcher is C-side.** The per-priority queue *structures* are Lua and
   readable; the matching pass that consumes them is not. Ordering claims beyond
   "higher is served first" (evidenced by the shipped comment at
   `SupplyGridBreakable.lua:52`) should be **measured, not asserted.**
8. ⚠️ **A DELIVERY IN FLIGHT IS RE-OPENED AGAINST THE REAL BANDS — any urgency
   scheme that elevates a demand OUTSIDE the real queues must guard
   `Drone:ImproveDemandRequest` (added 2026-09-01, `EF-074`).** `Drone:Deliver`
   (`Lua/Units/Drone.lua:1164-1175`) improves every PickUp-chained delivery unless
   `do_not_improve_req` is passed, and the shipped `PickUp` tail chains
   `SetCommand("Deliver", d_request)` **without** it (`:1013-1014`).
   `ImproveDemandRequest` (`:760-813`) asks for a strictly better destination at
   `min_priority = d_building:GetPriorityForRequest(d_request) + 1` (`:766`) **in
   the REAL demand queues**. So a demand that is urgent only in a mod-side view
   still carries its real band here, and the parts flown for a tier-5 repair can
   be traded up mid-flight to routine player-High traffic — the exact inversion
   such a scheme exists to prevent. Vanilla baseline for scale: band-2 deliveries
   are ALREADY hijackable by band-3 demands today; the trap is only that a tier
   design thinks it outranks 3 and this seam does not know it.
   ⚠️ **And the guard needs a carve-out or it hangs the drone** (added 2026-09-01,
   opt-in `reports/DRONE_REBUILD_DESIGN_20260901.md` §2b rule 5): `Deliver`'s
   retry loop sets `must_change` when the destination is unreachable, when a
   fulfill retry failed, or when the request was suspended (`:1246-1250`), and a
   guard that declined unconditionally would loop the drone on an unreachable
   building at `Sleep(1000)` per pass forever. Decline only while `must_change` is
   false; hand `must_change` calls straight to the original.

> ⚠️ **RECORD CORRECTION, 2026-09-01.** This landmine was announced in commit
> `3e224a7`'s subject line ("DRONE_PRIORITY_SYSTEM gains landmine 8") and in the
> opt-in bands report's §8 addendum, but the commit touched only
> `docs/agent/facts/` (`git show --stat 3e224a7`) — **the landmine was never
> written.** Written for real here by the opt-in mod's rebuild-design session.

---

## §7 What this does and does not settle

**Settled, from source:** the band range and its hard ceiling; the player's
control and its default; the single function that assigns priority; every
override that exists; that building maintenance has none; that priority is baked
at insert; that the developers' rule is life-support-criticality rather than
repair-ness.

**Settled 2026-07-31 by the research brief's Q3/Q4 (source, game-free)** — moved
out of the unsettled list below; full evidence on the D06 entry:

- **Property defaults are omitted from saves.** `TaskRequester` carries
  `priority = 2` as a **class member** (`TaskRequest.lua:53-59`); the instance
  member is written only by a real change (`SetPriority` `:170-179` early-outs on
  equality); `ConstructionSite:Complete` (`:1484-1521`) does not pass one; and
  savegames persist the instance table only, with class tables restored as
  permanents by name (`Core/persist.lua:157-165`). **No template in the game sets
  `priority`** — all 288 swept. So a class-default change reaches every existing
  building the player never re-prioritised, and reverts on uninstall.
- ⚠️ **`const.TaskRequest.DefBuildingPriority` is dead.** The classdef captures
  the module local at file-load time (`:57`); `ClassesPreprocess` reassigns it
  afterwards (`:21-32`). A default change must be written on the class.
  `Min`/`MaxBuildingPriority` are read at call time and are unaffected.
- **Life-support producers = a shipped class test**, not a property test:
  `IsKindOf("AirProducer")` / `IsKindOf("WaterProducer")`, which the game itself
  uses at `LifeSupportGrid.lua:272-276` and whose docstrings claim completeness
  (`LifeSupportProducer.lua:21-23`, `:125-127`). It catches exactly five —
  MOXIE, Electrolyzer, Water Extractor, Micro-G Water Extractor, Moisture
  Vaporator. Air/water **storage** is a separate family and is not caught.
- **Food service = `ServiceWorkplace` AND a Food demand**, exactly four: Diner,
  Mega Mall, Grocer, Small Grocer. The Food test **alone** also catches Micro-G
  Habitat and Naturalist Habitat, which are residences (`MicroGHabitat.lua:3-4`)
  — an owner call, recorded and not made.

**NOT settled, and not to be assumed:** whether the C matcher honours a widened
priority range at all (**research brief Q1 — decisive, still owed, needs a
running game**); whether hub queues persist across a save (**Q2, still owed**);
the C matcher's exact ordering within a band; whether a bump to 3 measurably
shortens the 3h03m haul leg in play (that is a measurement, and PT-52's harness
must be re-pointed first — the current metric measures *which hub delivered*, not
which won a claim); and how much routine traffic a colony-wide promotion would
displace.

---

## §8 The live widening incident, 2026-07-31 — read this before touching the range

The Q1/Q2 experiment module widened `const.TaskRequest.MaxBuildingPriority` to 5
at file scope and the owner loaded an existing save. **Every `FindTask` call in
the colony threw immediately**, drones froze in place while the UI reported
"heavy load", and the log filled with tens of millions of lines. Nothing had been
armed yet — the widening **alone** did it. Stack:

```
[LUA ERROR] attempt to index a nil value
  [C](-1):                   upvalue Request_FindTask_C
  Lua/_TaskRequest.lua(73):  upvalue orig_findtask
```

**Mechanism, and it is the important part.** `Init()` allocates the queue tables
at construction time and never runs again (see the correction in §1). A hub
restored from a save therefore comes back with the tables it was **built** with —
`-1..3`. The widened const makes vanilla's own loops (`_InternalRemoveRequest`
`:364-374`, `TaskRequestHub:RemoveBuilding` `:344-358`, both reading the module
locals) iterate `-1..5` and index `supply_queues[4]`, which is nil.

### What this settles

1. **Q2 IS ANSWERED: hub queues are PERSISTED, not rebuilt on load.** They are
   plain instance members and they come back through the save exactly as they
   were. This was the branch the research brief flagged as needing mitigation,
   and it now has a live demonstration rather than an assumption.
2. **The hub population is bigger than "drone hubs".** `DroneControl` subclasses
   are **`DroneHubBase`, `RocketBase` and `RCRover`** (`DroneHub.lua:2`,
   `RocketBase.lua:2`, `RCRover.lua:6`) — every rocket and every RC Rover carries
   its own queue set. Any range change has to reach all of them.
3. **Strong signal on Q1, not yet proof.** If the C matcher had `-1..3` baked in,
   widening a const it ignores could not have made it index a missing key.
   `Request_FindTask_C` throwing is most simply explained by the C side *reading*
   the bound — which points toward "honoured". **Not recorded as the answer**;
   it needs the clean run.
4. **`DroneControl` caches the maximum in a FILE-LOCAL** — `local MaxBuildingPriority
   = const.MaxBuildingPriority` (`DroneControl.lua:8`), evaluated when the game's
   own Lua loads, **before any mod runs**, and used by the live
   `DroneControl:RemoveBuilding` loop at `:735`. Mod code cannot reach a file-local
   upvalue. So even a fully honoured widening leaves that removal path stopping at
   3, and band 4-5 entries would not be cleared by it. (The similar loop at `:133`
   is inside a `--[[ ]]` comment — a dead Lua version of a C function — and does
   not count.)

### The design consequence — this is the part that bites the rebuild

Bands 4-5 cannot simply be switched on. **Every hub in every existing save has
narrow tables**, and the moment the range widens, vanilla's own removal loops
index keys those hubs do not have. Any real deployment needs to top up (or
rebuild) the queue tables of every already-constructed `DroneControl` — hubs,
rockets and rovers, across every loaded map — before anything calls `FindTask`.
That is a savegame-compatibility burden the band design did not previously know
it had, and it belongs in the design-drift disclaimer if the scheme survives.

**Safe re-run:** do it on a **new game**, where every hub is constructed after the
const change and allocates the full range natively.

---

## §9 The uninstall picture — safe, lossy, and the heal path expires

Measured 2026-07-31 immediately after §8, on a purpose-built save (`Q1orphan`):
a band-4 demand request left **outstanding**, the closure stripped from the
building first (priority is baked at insert, so the request stays at 4), saved
while paused, then loaded with the experiment module **disarmed**.

### What a vanilla load does with a widened save

- **Zero Lua errors.** The colony loads and runs clean.
- **The widened structure is IN THE SAVE.** With the module gone, a hub still
  reports `demand keys: -1,0,1,2,3,4,5`. Queue key range is savegame state, not
  mod state.
- **`band4 entries on this hub: 4`** — and note four, not one: *every* building
  ever armed at band 4 left its request parked there, including ones that were
  successfully repaired (those sit at amount 0, harmless but unreachable).
- A mod-written plain number on a building (`SMRTest_Q1_band = 4`) persisted into
  the vanilla load without issue.

**The asymmetry is the whole finding:**

| | loops | tables | result |
|---|---|---|---|
| §8 — widen an existing save | `-1..5` | `-1..3` | **nil index, total drone failure** |
| §9 — load a widened save vanilla | `-1..3` | `-1..5` | **silent; keys 4-5 never visited** |

Wide loops over narrow tables crash. Narrow loops over wide tables are safe and
quiet — vanilla asks only for `-1..3`, finds every key, and never looks higher.
**So uninstall does not break a colony. It strands work in it.**

### The heal path exists — and then it expires

Re-registration re-files requests through `GetPriorityForRequest`, which without
the mod returns `1..3`, so an orphan clears the moment its hub re-registers.
Every trigger, swept:

- `OnMsg.DepositsSpawned` → re-registers **every drone hub in the city**
  (`DroneHub.lua:188-198`). Fired from a completed sector scan, and **only when
  that sector actually placed deposits** (`Exploration.lua:265`, `if placed > 0`).
- Work-radius change → `DelayedCall(300, ReconnectTaskRequesters)`
  (`DroneControl.lua:776`).
- Extender flap → `DroneHubExtender.lua:110-111`.
- Rocket takeoff/landing (`RocketBase.lua:1577/1583`); RC Rover movement
  (`RCRover.lua:425/439`) — these two are not in `labels.DroneHub` and heal
  themselves.

**There is NO timer, NO lap sweep and NO on-unpause pass.** Nothing is gated to a
sol.

⚠️ **And the main path expires.** Sector status is a one-way ladder —
`unexplored → scanned → deep scanned` (`Exploration.lua:123`, `:40`) — deposits
are revealed only on those transitions, and `UnexploredSectorsExist` reports
`fully_scanned` once every sector is deep scanned (`:47-68`). **There is no
re-scan, so `DepositsSpawned` never fires again on a fully-explored map.**

**Owner's observation, and it is the right one:** clearing the map is one of the
first things players do, while removing a mod from an established colony is a
late act. **The heal dries up exactly when it would be needed.** (Sensor towers
are disaster warning, a different system; the in-range revealer at
`DepositRevealer.lua:21` does not fire `DepositsSpawned`.) What is left late-game
is incidental — a hub toggle, a radius change, an extender flap.

> 🔗 **Uncomfortable interaction, recorded not actioned:** **F77
> (`ExtenderFlapChurn`) exists to REDUCE extender flap**, and extender flap is
> one of the few recurring reconnect sources still alive in a late colony. Our
> own fix therefore reduces the frequency of this heal path. That is not a reason
> to change F77 — but do not design a mitigation around "it will reconnect
> eventually" without accounting for it.

### What this obliges the disclaimer to say

Not *"savegame footprint: none"* — that is D06 v1's claim and the rebuild cannot
inherit it. The honest version: uninstalling **does not break the colony and does
not error**, but any work filed in the extra bands at that moment is **stranded**
until that hub happens to re-register, which on a fully-scanned map may not
happen on its own. A deliberate mitigation (a shutdown sweep that re-registers
every hub, or a one-shot fixup) would be worth more than any wording.

---

## §10 The duplicate-entry leak — a defect of the band design ITSELF, not of uninstall

Measured 2026-07-31, and it is the finding that most constrains the band scheme.

**What was seen.** On the `Q1orphan` save, with the experiment module removed,
`demand_queues[4]` on the sampled hub held **4** entries. A
`ReconnectTaskRequesters()` was then run. It **repaired the target building** —
its request re-filed into band 1 and a drone serviced it — but the band-4 count
went **4 → 6**. The re-registration *healed the building and grew the garbage.*

**Mechanism.** `ReconnectTaskRequesters` is `DisconnectTaskRequesters()` +
`ConnectTaskRequesters()` (`DroneControl.lua:779-785`). The disconnect runs
`DroneControl:RemoveBuilding`, whose loop is

```lua
for priority = -1, MaxBuildingPriority do   -- DroneControl.lua:735
```

where `MaxBuildingPriority` is the **file-local captured at game-Lua load time**
(`DroneControl.lua:8`, `local MaxBuildingPriority = const.MaxBuildingPriority`)
— i.e. **3**, before any mod runs, and unreachable from mod code because a
file-local upvalue is not addressable. So the disconnect **cannot remove a
band-4/5 entry**. The connect then re-files each request at its current
priority. Any building still resolving to 4 gets a **new** entry while its old
one is never cleared. Two such buildings were still armed at band 4 in that save;
`4 + 2 = 6`, and the arithmetic matches exactly.

> ⛔ **This is NOT an uninstall problem. It happens with the mod fully
> installed and working.** Re-registration is routine in normal play — extender
> flap, work-radius change, deposits spawning. **Every one of them duplicates
> the elevated entries of every elevated building, permanently.** A long game
> would accumulate dead request references in bands 4-5 without bound.

**Corollary — the base class is not the problem.** `TaskRequestHub:RemoveBuilding`
(`TaskRequest.lua:344-358`) and `_InternalRemoveRequest` (`:364-374`) loop the
**module locals**, which the `const.TaskRequest` group *does* widen. It is
specifically `DroneControl`'s override, with its own baked constant, that traps
the entries — and `DroneControl` is the class every drone hub, rocket and RC
Rover inherits.

### What this costs each design option

- **Bands 4-5 inside `-1..3`-shaped vanilla structures require replacing
  `DroneControl:RemoveBuilding` outright** — a FIX_POLICY §1.5 full replacement
  in the most shared queue code in the game, and one of the highest patch-rot
  exposures available. Nothing smaller reaches the constant.
  > ⚠️ **CORRECTED 2026-09-01 (BANDS_CLEAN_REVERT §4.1.1): the constant is unreachable,
  > the TABLES are not.** `DroneControl:RemoveBuilding` (`:731-757`) is `OnRemoveBuilding` +
  > `remove_entry` calls over the hub's own plain Lua arrays + `UpdateDeficits`; a chained
  > PRE-wrapper that runs the same three `remove_entry`s for `4..const.TaskRequest.
  > MaxBuildingPriority` before `orig` closes the leak with no replacement — every removal
  > path (`DisconnectTaskRequesters`, `SetPriority`) reaches it, and `_InternalRemoveRequest`
  > already loops the widened locals. The mechanism above and the `4 → 6` reading stand;
  > the "requires replacing outright" conclusion does not. Re-measure = E-3 there.
- **Working inside `-1..3` avoids this entirely.** Vanilla's own removal loop
  already covers the whole range, so no entry can ever be stranded and no
  duplicate can accumulate. (This is now a *second* independent argument for the
  `-1..3` design, alongside uninstall-cleanliness — and neither was known when
  the band table was drafted.)
- **A merged-view overlay** (band 4-5 held in non-persisted mod-side tables,
  merged into the view handed to `Request_FindTask`) would sidestep both,
  because nothing outside `-1..3` would ever enter a hub's real queues.
  **Unproven and unscoped** — `FindTask` is hot, and every other queue path
  would have to agree with the overlay.

**Do not design against this section without re-measuring it.** The count read
`4 → 6` once, on one hub, in one save. The mechanism is source-backed and the
arithmetic fits, but a second observation on a clean fixture would make it solid.
