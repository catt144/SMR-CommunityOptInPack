# D06 — drone assignment overhaul, feasibility study (2026-07-28, game-free)

> **BUILD STATUS (2026-07-28, same day):** the user greenlit the core — **core v1
> is BUILT**: `Code/Opt_DroneOverhaul.lua` (closest-fleet-first claim gate on
> `TaskRequestHub:FindTask` — the veto variant of H, chosen over registration-H
> for v1 because it is instantly and completely reversible via the toggle and
> cannot orphan a request — plus option A repair moonlighting and the G
> telemetry `SMRFixPack.DroneReport()`), and `Code/Fix_ExtenderFlapChurn.lua`
> (F77, default-on). See the D06 entry in BUGS.md. Registration-H, H-v2
> (demand), B, C, E remain future iterations per the plan below.

Commissioned by the user after the 2026-07-28 static investigation verdict (BUGS
DroneControl bullet + F77): *"what is even feasible if we want an optional overhaul
toggle — load balancing? handoff? distance/idle priority?"* Everything below is
static-analysis-verified against Src; **nothing is built**. The module would ship as
`Opt_*` behind a Mod Options toggle (D05 surface), off by default, per the D02-D05
convention.

## Ground rules — what is patchable and what is not (each verified)

These constraints shape every option:

1. **The C matcher cannot be reordered.** `Request_FindTask` / `Request_FindDemand` /
   `Request_FindSupply` are engine exports; their internal scan order is invisible and
   untouchable. Their **Lua callers** (`TaskRequestHub:FindTask` and friends,
   `_TaskRequest.lua:54-83`) are plain methods — wrappable, and callable BY US against
   any hub with any agent.
2. **Work requests (repair/clean/construct) live ONLY in `priority_queue`** — a plain
   per-hub Lua array of request userdata (`_TaskRequest.lua:118-121` adds
   `rfPostInQueue`; supply/demand queues only hold `rfSupplyDemand` requests). A Lua
   scan over them is legal and cheap; the userdata API we need (`IsAnyFlagSet`,
   `CanAssignUnit`, `GetTargetAmount`, `GetSource`, `GetResource`) is used from Lua
   game code everywhere.
3. **Claims are atomic and Lua-visible.** `RequestAssignUnit` is a global Lua function
   (`_TaskRequest.lua:352`); `Drone.lua` holds **no file-local alias** (grep-verified),
   so a wrapper installed from mod code IS seen by every drone claim. Claim happens
   inside `Drone:Work`/`PickUp` at command start (`Drone.lua:901,941`) with a benign
   failure path (Sleep + return to Idle).
4. **`Drone:Idle` falls through exactly when it found nothing** — the body ends with
   `Sleep(2000)` + `CleanUnreachables()` and returns; the command loop re-runs it. So a
   **chained post-wrapper runs precisely in the "idle with no work" case** (every ~2s
   per idle drone) — the natural dispatch hook. (When Idle DOES find work it
   SetCommands and the thread dies before our code — which is correct: vanilla own-hub
   priority is preserved for free.) The F73 "pre-wrap only" fact applies to command
   methods that always end in SetCommand (Colonist:Idle); Drone:Idle's fall-through is
   the exception that makes the post position usable.
5. **`Drone:Work` and `ApproachWrapper` never consult `command_center`**
   (`Drone.lua:898-938`, `:819-849` — only an optional `UpdateConstructions` ping).
   Requests are hub-agnostic C objects. **A drone can execute another hub's request
   with zero bookkeeping surgery.** Movement stays bounded by the engine's own
   RestrictArea (100 hexes-worth around the drone's OWN hub, `Drone.lua:227-230`).
6. **Drone migration between hubs is vanilla-blessed**: the player's reassign
   interaction is `Drone:SetCommandCenterUser(obj)` → `SetCommandCenter` + Idle/Reset
   (`Drone.lua:2687-2694`); orphan gathering and refab use the same primitives. Caps
   via `CanHaveMoreDrones()` (`g_Consts.CommandCenterMaxDrones`).
7. **The load signal already exists**: `CalcLapTime()` vs `const.DroneLoadLow/
   MediumThreshold` is the game's own heavy-workload metric (`DroneControl.lua:
   955-971`), and `GetIdleDronesCount()` is cheap. No new bookkeeping needed to know
   who is starved and who is slack.
8. **Coverage checks must be extender-aware.** A hub's effective area = own circle +
   every WORKING linked extender's circle, recursively (`FindTaskRequesters`,
   `DroneControl.lua:315-325`). Any option that asks "does hub H cover point P" must
   recurse `linked_extenders` the same way — a naive `HexAxialDistance(hub, P) ≤
   work_radius` silently ignores exactly the extender geometry this whole
   investigation is about.
9. **Savegame discipline is easy here**: every option below keeps only transient
   module-state (memos, ledgers) — nothing persisted, toggle-safe both directions via
   the D05 `IsActive`-per-call pattern.

## The options

### A. Repair-work moonlighting — idle drones serve neighboring saturated hubs' WORK queues
**What:** post-chain `Drone:Idle` (ground rule 4). When vanilla found nothing: skip if
the drone's controller is an RCRover/rocket (player-zoned fleets) or hub not working.
Otherwise iterate the city's `DroneHubBase`s (labels filter), take those that are
working, not own, **saturated** (`GetIdleDronesCount() == 0` — if the owner has idle
drones they'd take the work themselves), and scan their `priority_queue` high→low
priority for `rfWork` requests with `CanAssignUnit()` and target > 0 whose SOURCE is
(i) within a modest radius of the DRONE (25-35 hexes — near work only), (ii) inside
the drone's own RestrictArea with margin, and (iii) not in the drone's unreachable
cache. First hit → `SetCommand("Work", req, req:GetResource(),
Min(DroneResourceUnits[res], target))` — byte-parallel to vanilla's own maintenance
branch (`Drone.lua:602-605`).
**Feasibility: HIGH** — every piece verified above; no pairing logic, no C
reimplementation; the claim stays vanilla-atomic inside Work.
**Risk: LOW.** Worst case the claim fails (race) or approach fails (feeds the
unreachable cache exactly as vanilla does; F55's fix already retires those). Perf:
scan runs only in drones with literally nothing to do, ~every 2s, gated by the
saturation check + a per-hub last-miss memo (mirror of vanilla `no_requests_time`).
Accounting: forign work never touches the foreign hub's `lap_time` (we bypass its
FindTask), and our drone's own hub keeps its idle count until the command flips —
cosmetic at worst.
**Reward: HIGH for hypothesis (a) and for general idle-fleet utilization** — the four
observed drones would have picked up the PolymerPlant repair within ~2s. **Does NOT
help (b)** (a request already claimed by a far drone reads `CanAssignUnit() == false`
— see D/E).
**Effort:** small module (~100 lines + option toggle).

### B. Full moonlighting — delegate to the foreign hub's own matcher (haulage included)
**What:** same hook as A, but instead of a Lua queue scan, call
`foreignhub:FindTask(self)` — the C matcher does priority + supply/demand pairing,
so idle drones also *haul* for saturated neighbors, not just repair.
**Feasibility: HIGH** (one call), with two warts A doesn't have: it perturbs the
foreign hub's `lap_time` bookkeeping (`_TaskRequest.lua:77-81` — feeds the
heavy-workload notification), and the returned request can target the FAR END of the
foreign hub's territory (no max_dist parameter on FindTask), so a post-return distance
check + skip-memo is mandatory to avoid claim-then-unreachable churn (skip BEFORE
SetCommand — the claim only happens inside Work, so a skip is free).
**Risk: MEDIUM** — same class as A plus the two warts; the skip-memo must be
per-drone with TTL or the same far request is returned every poll.
**Reward: HIGH** if live data shows starved *haulage* (deliveries), not just repair.
**Recommendation:** ship A first; A's hook and gates are a strict subset — B is a
drop-in upgrade of the "find" step if the R1-R7 reads or the playtest show starved
supply/demand requests too.

### C. Idle-drone migration balancer — the "load balancing poll" (user's suggestion)
**What:** a slow periodic sweep (game-time thread, every 1/2 sol, or on the existing
`BuildingUpdate` cadence): for each pair (overloaded hub H, slack hub S) where H's
`CalcLapTime() ≥ DroneLoadMediumThreshold`, S has ≥ N idle drones, H
`CanHaveMoreDrones()`, and the hubs are within a distance budget — migrate
`min(idle-1, deficit)` idle drones S→H via the vanilla `SetCommandCenter` path with
hysteresis (max one move per pair per sol; never drain S below a floor; never touch
rover/rocket fleets or disabled drones).
**Feasibility: HIGH** — all vanilla primitives (ground rules 6-7); this is literally
automating what the player does by hand today.
**Risk: MEDIUM, but of a different kind — intent, not mechanism.** It *permanently*
rewrites the player's fleet distribution; a player who deliberately parked 12 drones
at a quiet hub will watch them walk away. Mitigations: opt-in toggle (given),
conservative thresholds (only act on the game's own "Medium/Heavy load" signal),
migrate only genuinely-Idle drones, and a Mod Options aggressiveness knob if wanted.
No sync/savegame risk (SetCommandCenter is save-clean).
**Reward: MEDIUM-HIGH and hypothesis-independent** — it fixes chronic imbalance at
the FLEET level, which neither A nor D can (they redistribute work, not workers), and
it reduces the far fleet's average haul length, which is the performance complaint.
Weakness: reacts on lap-time scale (slow), useless for acute single-building
starvation — that's A's job. A and C compose cleanly: A = fast/tactical,
C = slow/strategic.
**Effort:** small-medium (~150 lines; the care is all in hysteresis tuning).

### D. Near-idle claim veto — "distance/idle priority" at the only injectable point
**What:** the match order is C-side (ground rule 1), so preference can only be
injected at claim time: chain-wrap `Drone:Work`/`Drone:PickUp` (or `RequestAssignUnit`
itself) — before claiming, if the request's source building has a DIFFERENT covering
command center (extender-aware, rule 8) that is meaningfully closer AND has idle
drones, yield once (the shipped miss path: Sleep + return) and memo the request so the
second encounter claims normally (starvation-proof by construction).
**Feasibility: HIGH** mechanically.
**Risk: MEDIUM.** It inserts a delay into EVERY claim decision colony-wide (the memo
bounds it to one 1-2s yield per request per drone, but the code path is the hottest
in the domain); "closer hub's idle drone will take it" is a *prediction* — if that
drone's Idle poll misses (its own hub's C-scan picks a different request first —
order unknowable, rule 1), the yield bought nothing; and it perturbs F50/F68/F71
adjacent machinery (rocket cargo claims) unless class-filtered to repair work.
**Reward: targeted at hypothesis (b) ONLY — and (b) is unproven.** If R1/R3 show (a)
(registration gap), this option is dead weight.
**Recommendation:** do NOT build until the live reads confirm (b). If (b) is
confirmed, build it repair-work-only first.

### E. True handoff — reassign already-claimed work to a closer idle drone
**What:** wrap `RequestAssignUnit`/`RequestUnassignUnit` to keep a claim ledger
(request → holder, claim time). A watchdog (every ~10s) looks for `rfWork` claims
where the holder is still en route, far (say > 40 hexes from target), and an idle
drone of ANY covering hub sits within ~10 hexes of the target. Then:
`holder:SetCommand("Reset")` (vanilla interrupt — the Work destructor unassigns,
`Drone.lua:905-911`; `InterruptDrones` precedent `_TaskRequest.lua:290-314`) and
immediately `neardrone:SetCommand("Work", req, ...)` — whose own claim is atomic; if
it loses a race, both drones just re-idle.
**Feasibility: MEDIUM-HIGH** — all public primitives, but the most moving parts of
any option: ledger correctness across savegame load (ledger is transient — rebuild
lazily), holder state edge cases (restrict to `rfWork` claims only — NEVER touch
PickUp/Deliver claims, a resource-carrying drone must not be Reset), ping-pong
control (distance-ratio gate ≥ 3-4× + never hand off the same request twice per
X hours).
**Risk: MEDIUM-HIGH.** Reset mid-command is the F50 churn primitive — used
surgically it's fine, used wrongly it IS the bug we fixed. Player-visible U-turns.
**Reward:** the only option that rescues work already locked by a far claim — i.e.
the definitive (b)-killer, and the observed `target:0` reads suggest (b) moments
exist even if (a) is the root.
**Recommendation:** tier 3 — only after A (+D if (b)) prove insufficient, and only
with C's telemetry in place.

### F. Rewrite the matcher in Lua with distance-weighted scoring — REJECTED
Replacing `TaskRequestHub:FindTask` with a Lua matcher that scores
priority × distance × idle-time is the "real" overhaul — and the wrong move:
the C matcher's semantics (supply↔demand pairing, `rfWaitToFill`, restrictor tables,
`under_construction` gating, deficit interplay, `supply_dist_modifier`) are only
partially visible from Lua; a reimplementation guesses at engine behavior the
investigation explicitly recorded as unverifiable, runs in Lua at the hottest
call site (every idle drone × 2s × whole queue set — the exact loop the user already
reports as a perf problem), and rots on every game patch. All of A-E get the
locality wins without owning the matcher. Rejected on FIX_POLICY grounds
(full replacement of engine-opaque machinery, maximum rot surface).

### H. Closest-hub-first registration with overload escalation — the proximity cascade (added 2026-07-28 after user design review)
**What the user asked for:** "request tries the closest hub; if it's overloaded, try
the next closest." Requests are passive so they cannot poll — but the same result is
achievable by INVERTING it: control which hubs a request is VISIBLE to. The hook
exists and is Lua-owned: `building:ShouldAddRequestToCommandCenter(request, hub,
resource)` is consulted per-request per-hub at every connect
(`DroneControl.lua:692`), default `return_true` (`_TaskRequest.lua:192`), replaceable
at the declaring class (F64 apply-check lesson applies).
**Mechanism:**
* **Tier 0:** the filter answers true only for the CLOSEST covering `DroneHubBase`
  (rank by `HexAxialDistance(hub, building)` among working hubs with usable drones —
  an extender-carried far hub correctly ranks FAR, because the fleet lives at the
  hub). Far fleets never see the request, so the "far drone claimed first and hauls
  across the map" scene — the user's stated biggest issue — is structurally
  impossible in tier 0, at any load level, with no saturation precondition and no
  race to lose.
* **Escalation:** a slow watchdog (~30s cadence) spots requests still unclaimed after
  a threshold (near fleet overloaded / broken / drained) and re-runs the building's
  registration (`DisconnectFromCommandCenters` + `ConnectToCommandCenters` — vanilla
  primitives) with the filter widened for that building (next-closest, then all
  covering hubs) for a bounded window. Transient ledger only; savegame-clean.
**Scope control (the important caveats, found in this pass):**
* **v1 filters repair/clean WORK requests only.** Demand-request filtering ripples
  into the per-hub `deficit_table` that shuttle logic reads (`Request_UpdateDeficits`,
  `DroneControl.lua:107-123`) — spatially arguably MORE accurate, but it needs its
  own assessment; v2 behind its own consideration. Supply/storage requests are NEVER
  filtered (FindTask pairs demand+supply within ONE hub's queues — filtering supply
  would break deliveries outright). Construction work stays unfiltered on purpose:
  multi-fleet swarming on a build site is desirable; repair can't swarm anyway
  (max_units=1).
* The class gate (`IsKindOf(hub, "DroneHubBase")`) confines the filter: the OTHER
  consumer of the same hook (`LRManager.lua:58`, shuttle side) and the elevator
  override (`MapSharedDepot`, `Elevator.lua:178`) pass different center classes and
  are untouched; rover/rocket fleets untouched.
* Delivery legs: with v1 (work-only), the maintenance DEMAND phase (fetch Electronics
  from a depot → deliver) is still claimable by far fleets. Note the locality prize
  there is double — a claiming drone pairs the supply from ITS OWN hub's queues, so a
  far claim often means a far DEPOT too (two long legs). If live data shows the
  delivery leg dominates, that's the v2 demand filter or a PickUp-scoped claim veto.
**Registration-guards audit (2026-07-28, user question — what vanilla does and
doesn't guarantee, and what H hardens):**
* Vanilla's out-of-range guard is geometry at CONNECT TIME ONLY, and it lives in the
  two search paths (`FindTaskRequesters` hub-side, `FindDroneNodes` building-side) —
  NOT in the API: `TaskRequester:AddCommandCenter` accepts any center
  (`CommonLua\TaskRequest.lua:147-160`, only `accept_requester_connects` checked).
* **Dome-inherit hole:** an in-dome building copies the DOME's `command_centers`
  wholesale with no per-building distance check
  (`ConnectToBuildingCommandCenters`, `_TaskRequest.lua:263-271`) — a hub clipping
  one edge of a large dome holds requests for EVERY building in it, including ones
  outside its circle. H's rank measures hub distance to the BUILDING itself, so for
  filtered requests H quietly repairs this.
* **Reach hole:** nothing aligns registration with `DroneRestrictRadius` (100 hexes
  around the hub) — a post-SignalBoosters extender CHAIN can register buildings the
  hub's drones cannot legally reach. H tier-0/escalation additionally EXCLUDES any
  hub farther than DroneRestrictRadius (with margin) from the building, neutralizing
  the registered-but-unreachable pathology for filtered requests as a side effect.
* **Battery:** no battery-vs-trip-length guard exists anywhere in vanilla — Idle
  checks only the emergency threshold BEFORE seeking work (`Drone.lua:608-610`); a
  claim by a dying drone is recovered (not prevented) when the battery command
  switch runs the destructors and releases the request. H/A do not change this;
  their distance bounds merely correlate claims with feasible trips.
* **Extenders hold nothing** (re-confirmed for this audit): an extender is a
  `DroneNode`, not a `TaskRequestHub` — no queues, no drones, absent from every
  request structure; both connect directions resolve to the uplink HUB. It is a
  registration-footprint booster plus attached recharge stations
  (`Drone.lua:2341-2345`), nothing more — so every option in this document
  correctly targets hubs only.
**Feasibility: HIGH** — one class-method replacement + a watchdog + a coverage-rank
helper (extender-aware per ground rule 8, cached per building with TTL; connect-time
code, not a hot path).
**Risk: LOW-MEDIUM.** Redundancy shrinks by design in tier 0 (a request waits out the
escalation threshold before other fleets may help — bounded, tunable, and exactly the
trade the user described wanting); reconnect storms re-run the filter idempotently;
no persisted state.
**Reward: HIGH — this is the structural fix for hypothesis (b)** and the closest
implementation of the user's intended behavior; it also makes option D (claim veto)
largely obsolete: D *predicts* a nearer drone will claim, H *guarantees* only nearer
drones can.

### G. Supporting acts (cheap, mostly independent of the toggle)
* **F77 debounce** (extender flap churn) — a plain repair, ships as `Fix_*` regardless
  of the overhaul decision; sketch on the F77 entry. Without it, any overhaul fights
  periodic whole-fleet Idle-kicks whenever an extender blips.
* **`SMRFixPack.DroneReport()`** — console/TestKit telemetry: per hub — handle, class,
  working, drones idle/broken/total, `CalcLapTime` vs thresholds, per-priority queue
  depths, extender chains. Zero risk, ~40 lines, makes the next playtest *measure*
  instead of eyeball, and is the tuning instrument every option above needs. Build
  first whatever else is decided.
* **`no_requests_time` nudge** — wrap `TaskRequester:AddRequest` to clear covering
  hubs' empty-queue throttle when a new request posts: shaves up to ~1s off reaction
  time. Trivial, marginal, fold into the module if built.

## Recommended shape (user decision; revised 2026-07-28 after user design review added H)

**Build order for an `Opt_DroneOverhaul` module (each independently toggleable in
spirit, one Mod Options switch in practice):**
1. **G-telemetry (`DroneReport`)** — before anything, so the next sitting quantifies
   the problem and every later change has a before/after.
2. **H (closest-first registration + escalation, repair/clean work only)** — the
   centerpiece: structural fix for far-fleet capture, the user's intended cascade
   semantics, no saturation precondition, no race.
3. **A (repair moonlighting)** — the complement H cannot cover: hypothesis (a)
   ground (building covered ONLY by the far hub — H then ranks the far hub closest
   covering, unchanged from vanilla) and the escalation window. A's saturation gate
   is fine THERE because that scenario is precisely "owner fleet has no idle drones".
   H and A compose: tier-0 work is only in the near queue, which is where the near
   idle drones already look.
4. **C (migration balancer)** — the strategic half; conservative thresholds,
   sol-scale cadence; automates the drone-count balancing the user otherwise does by
   hand (H's escalation makes imbalance survivable; C makes it self-correcting).
5. **H-v2 (demand filter) or B (full moonlighting)** — only if live data shows the
   DELIVERY leg (depot → building) still dominating; H-v2 needs the shuttle
   deficit-table ripple assessed first.
6. **D / E** — largely superseded by H (D predicted what H guarantees); E stays the
   last resort for claims that predate escalation.
7. **F77 fix** — separate `Fix_`, ships with the next wave independent of all above.

**What still gates this:** the R1/R3 reads at a live starvation moment remain
worthwhile (they tune H's escalation threshold and decide whether v2/B are needed),
but H + A no longer DEPEND on the (a)-vs-(b) answer — the pair covers both.

**Global risk statement (unchanged from the verdict):** this is the deepest shared
machinery in the game — hubs, rovers, and the rocket cargo path (F50/F68/F70/F71) all
run through these queues. Whatever subset is approved must re-pass the F50
rocket-churn and F55 unreachable scenarios, plus a new probe set (moonlight
claim/execute, migration hysteresis) in the A/B harness before it ships.

---

# MANDATE CHANGE — 2026-07-29, read before D06 options A–H or D08 below

**The user widened the brief after the first measured A/B**, verbatim: *"The
overall goal of this opt-in is not to be 100% true to the base game, it's to
make this issue that is highly frustrating to end-game players workable. So if
that means we also need to tweak drone speed instead of just logic, I am open to
that."*

Everything below was written under the older, tighter assumption that only
**dispatch logic** was in scope. That is no longer the constraint. **Stat
changes are admissible** in an `Opt_*` module:
- `Drone.move_speed = 1440` (`Lua\Units\Drone.lua:26`), applied via
  `SetMoveSpeed` (`:85`).
- `g_Consts.DroneResourceCarryAmount` (`Lua\__const.lua:639`) feeds
  `UpdateDroneResourceUnits` (`Drone.lua:707-723`), rebuilt on
  `OnMsg.ConstValueChanged` / `NewMap` / `PostLoadGame` — a clean hook, and the
  AncientArtifactInterface upgrade already modifies this property, so there is
  in-game precedent.
- Repair/work chunk sizes via `DroneResourceUnits`.

**What still binds:** opt-in only; toggling off restores vanilla completely;
save-safety per FIX_POLICY §3 and the D08 risk table. FIX_POLICY §4's "no
balance changes" governs `Fix_*` modules — it never governed `Opt_*` D-items,
which are behavioural overhauls by definition.

**Empirical caution to weigh, not to obey:** the save that produced the A/B has
**all techs researched plus a drone-carry breakthrough**, and hauling was still
**88% of elapsed repair time**. That is evidence throughput buffs may hit
diminishing returns and the real bottleneck is structural — trip count, trip
distance, depot choice, drone assignment. Stat levers are nonetheless simple,
robust, and immune to the scheduler quirks that made the claim gate inert.

**Also note the A/B verdict itself (D06 entry, BUGS.md): the shipped claim gate
fired ONCE across 25 simultaneous malfunctions and moved its own leg by one
minute.** Options A–H and the D08 layers below were all designed before that
was known. Re-read them as hypotheses, not as a plan.

# DECISION — 2026-07-29 (post-QA review): the overhaul ships with player-facing STAT DIALS — **BUILT 2026-07-29 late (D09, `Code/Opt_DroneStatDials.lua`)**

**User decision, made after the fresh-context QA review reported:** stop
treating speed as a diagnosis question. The overhaul module will EXPOSE the two
stat levers as Mod Options dials and move on; the structural work stays gated
on instrumentation (below).

**BUILD NOTE (2026-07-29 late):** shipped as D09 — see the BUGS.md entry for
the build facts. **Speed dial range AMENDED by user the same day, pre-build,
after the no-clamp probe below: 1x (base)/2x/3x/5x (percent +0/+100/+200/+400,
additive with techs; worst case 1440 × 5.6 = 8064, under the proven 10000
headroom), superseding this section's original 1.0x/1.5x/2.0x. Carry unchanged
(+0/+1/+2).** PT-56 owed.

**The UI capability is verified** (QA session, `CommonLua\Classes\Mod.lua`):
Mod Options is NOT toggle-only. Three widget types exist —
`ModItemOptionToggle` (bool), `ModItemOptionNumber` (integer slider,
min/max/step, `:2728-2750`), `ModItemOptionChoice` (dropdown over a string
list, `:2752-2771`). Planned surface:

- **Drone speed** — choice `1.0x (base) / 1.5x / 2.0x` → module-owned modifier
  (own id) on `move_speed`, percent +0/+50/+100 on top of whatever techs the
  save has. Choice values arrive as STRINGS (the choice text IS the value,
  `:2767-2769`) — map them in code.
- **Drone carry** — choice `+0 (base) / +1 / +2` → module-owned modifier on
  `g_Consts.DroneResourceCarryAmount` (base 1; Artificial Muscles +1 and the
  Artifact Interface upgrade's `upgrade1_add_value_1 = 1` stack the same way —
  plain addition on one global; consumed at `Drone.lua:719`, auto-rebuilt via
  `OnMsg.ConstValueChanged`). There is no per-tier "recorded ability" anywhere.
- Reads via `CurrentModOptions` (already used, `00_Core.lua:48-52`); live
  re-apply in the existing `OnMsg.ApplyModOptions` handler (`00_Core.lua:106`).

**Facts recorded with the decision (all source- or live-verified in the QA
session):**
- The user's colony was already AT the vanilla stat ceiling during the first
  A/B: live read `GetMoveSpeed() = 2304` = 1440 × 1.6 — Low-G Drive (+20%)
  **plus the Advanced Drone Drive breakthrough (+40%)**, percents stacking
  additively on base (`Modifiers.lua:100,112-113`); carry 2× via Artificial
  Muscles. **This corrects the mandate note below: the user has BOTH
  breakthroughs; the carry breakthrough has no speed component.**
- Hauling was 88% of elapsed repair time AT that ceiling — so the dials are
  player-facing relief and breakthrough-lottery insurance (most saves never
  draw either breakthrough), NOT the fix for the structural problem. Set
  expectations accordingly in the mod description.
- **No drone speed cap exists in the game's Lua** — no clamp constant, no
  min/max metadata on the property; the modifier pipeline clamps only to int64
  (`Modifiers.lua:100-101`); the game itself runs units at 2× through passages
  via raw `SetMoveSpeed` (`Passage.lua:1046-1056`). **The queued C-side check
  RAN 2026-07-29 (user, live, screenshot on file): `SelectedObj:SetMoveSpeed(10000)`
  → `GetMoveSpeed()` = 10000 — NO C-side clamp; and at 10000 on ultra sim
  speed movement stayed clean (no frame skips, clipping, tripping or stuck
  states). Probe drone restored to 2304 afterwards.**
- Save-safety (FIX_POLICY §3): modifiers persist on objects/save. Toggle-off or
  selecting "base" must remove the module's modifiers **by id**; uninstalling
  the mod with a dial active leaves a benign vanilla `Modifier` residue
  (documented, loads clean without the mod).

**What stays data-gated:** the structural choice — maintenance priority
escalation (vanilla precedent: cables/passages repair at forced priority 3,
`SupplyGridBreakable.lua:48-56`) vs the D08 layer-1 dispatcher — waits on the
request-lifecycle decomposition (queue-latency vs travel). That instrument is
**BUILT (2026-07-29, stress harness v2 in the TestKit — per-request lifecycle
tracing; `HARNESS_REVIEW_PROMPT.md` executed and deleted)**; the decomposition
is now measurable and the next PT-52 B2 run supplies the data. Note from the
rebuild: shuttle deliveries misfire the deliverer handoff (no
`CargoShuttle:Work`), so on shuttle-served colonies the claim gate sees more
of the repair traffic than the v1 null result implied — see the D06 entry.

# D08 — Drone Hub Extender overhaul + Command Center (2026-07-29 design session, game-free)

Origin: the user observed live that **Drone Hub Extenders make the D06 problem
worse, not better** — a large base ends up with overlapping-upon-overlapping
unadjustable coverage blobs. This section is the full design record of that
session. **Nothing here is built. Every layer is a user decision.**

## The foundational constraint — the leash

**Drone service is a DISTANCE relation, not a connectivity relation.**
`Drone:RestrictArea(const.DroneRestrictRadius, command_center_pos)`
(`Lua\Units\Drone.lua:227-231`) is a hard engine-level movement restriction: a
drone physically cannot leave a circle centred on its own hub. Jobs therefore
**cannot be relayed** — you can pass a job's *description* any distance, but the
worker that must fly there is chained to its hub.

Consequence, and the single most important thing in this section: **any scheme
that propagates work along a topology (a "mesh"/relay of extenders and hubs) can
manufacture registrations that no drone can legally serve.** The correct
candidate set for "which hubs could serve this building" is a one-line geometric
test, not a graph walk:

```
GetDist2D(hub, building) <= const.DroneRestrictRadius
```

A graph walk is strictly worse: it produces false positives (candidates too far
to serve — the exact blind spot described below) and false negatives (hubs
geometrically in range but not "connected"). **Do not re-propose job relaying.**

## Verified facts this design rests on (all read 2026-07-29)

| Fact | Source |
|---|---|
| `work_radius` is a **modifiable** property on `DroneNode`, default `CommandCenterDefaultRadius` | `DroneControl.lua:40` |
| Hub range slider is UI-only, `min=CommandCenterMinRadius`, **`max=CommandCenterDefaultRadius`** — you can only ever SHRINK below default | `DroneControl.lua:76` |
| `CommandCenterDefaultRadius = 35`, `CommandCenterMaxRadius = 50`, `CommandCenterMinRadius = 5`, `SignalBoostersBuff = 15` (35+15 = exactly the 50 ceiling) | `_GameConst.lua:62-64,72` |
| `DroneRestrictRadius = CommandCenterMaxRadius * 2 * GridSpacing` — travel cap is *derived* as 2× the coverage ceiling | `_GameConst.lua:71` |
| Extender inherits the same default radius (template overrides nothing) | `BuildingTemplate\DroneHubExtender.generated.lua` |
| `FindTaskRequesters(node)` = requesters in the node's radius **plus recursively** every working linked extender's | `DroneControl.lua:315-324` |
| An extender must be placed **inside its uplink's radius** — coverage is already contiguous | `DroneHubExtender.lua:66` |
| `extender:GetCommandCenter()` hard-returns **the uplink's** hub | `DroneHubExtender.lua:156-160` |
| `TaskRequester.command_centers` is a **LIST** — buildings already register to every covering node's centre | `_TaskRequest.lua:266-278` |
| Buildings inside a dome inherit the dome's centres and **return early** — no own node search | `_TaskRequest.lua:266-271` |
| `DroneControl:ReconnectTaskRequesters` exists — vanilla rebuilds registrations routinely | `DroneControl.lua:779-785` |
| `CalcLapTime()` = time for one pass over the hub's queue; vanilla classifies it against `DroneLoadLowThreshold` (h/3), `DroneLoadMediumThreshold` (3h), and warns via `UpdateHeavyLoadNotification` after `DroneLoadMediumThresholdNotification` (6h) sustained | `DroneControl.lua:955-971`, `_GameConst.lua:83-85` |
| `UseDronePrefab(bulk)` / `ConvertDroneToPrefab(bulk)` are the +/- actions; `bulk` truthy = 5. UI calls them **DIRECTLY — no NetSyncEvent, no cheat gate** | `DroneControl.lua:825,861`; `Data\XDef\CommandCenterTransportationOverviewRow.lua:159,167,225,233` |
| A vanilla **Command Center → Transportation** overview already lists hubs as rows **with the +/- buttons wired in** | `Data\XDef\CommandCenterTransportationOverview(Row).lua` |
| Command Center graph sections are a plain **Lua table built by a function** (ids `colonists`/`transportation`/`buildings`) — wrappable in pure Lua | `Lua\X\ColonyControlCenter.lua:10-65` |

## The defect being fixed

Every building under an extender is registered to **exactly one hub, arbitrarily
far away** (`GetCommandCenter` → uplink). That is precisely the pathology D06
exists to fight, manufactured by design.

Worse: D06's `closest_covering_hub` excludes hubs beyond `DroneRestrictRadius`
of the building, so a building covered only via a long extender chain can have
**no legal covering hub at all** in the module's view — the claim gate abstains
entirely and vanilla's race decides. Extenders don't merely cause far-fleet
claims; they create a blind spot in the existing fix.

**And the claim gate can only WITHHOLD work from a far hub — it cannot GIVE it to
a near hub that isn't registered.** Under an extender the near hub usually isn't
registered, so vetoing accomplishes nothing and the job just waits. Moonlighting
is the only escape and only fires when the neighbour is fully saturated — which
is why live reports keep showing `moonlighted=0`. **Awareness and eligibility
must widen together, or a wider veto starves the building.**

## Layer 1 — Dispatcher (recommended first)

Extender-covered requesters register to **every hub within legal drone reach**,
not just the uplink. Then D06's existing claim gate arbitrates by distance and
idle state — no new scoring system.

- **Implementation:** chained wrapper on `TaskRequester:ConnectTaskRequesters`;
  when a covering node is an extender, add the geometric candidate set instead
  of only `node:GetCommandCenter()`.
- **Why it's small:** many-to-many registration is already stock vanilla; the
  extender is the *only* node type that collapses to one hub.
- **Save risk: none.** Every added entry references an existing vanilla hub
  object. No new class, no new GameVar, no new persisted property. Worst case
  after uninstall is over-registration, which self-heals on the next
  `ReconnectTaskRequesters` (hub toggle, extender flap, radius change,
  nearby placement).
- **Risks to test:** queue bloat (live hubs already show `p2:261`) and the
  per-`FindTask` polling cost; the dome early-return path; `auto_connect` and
  `ConstructionSite` special-casing in `DroneControl:ConnectTaskRequesters`;
  `are_requesters_connected` guard semantics. Debounce rebuilds using the F77
  pattern.

## Layer 2 — Cluster scoping (the user's "mesh", correctly scoped)

The mesh is **wrong for transporting jobs** (see the leash) but **right as a
player-authored grouping**: candidate set = `within drone reach AND in the same
extender-linked cluster`. Strictly a subset of the geometric set, so it can never
create an unservable assignment, and it gives the player a scope control the base
game has no concept of — "these hubs are one logistics zone, those are another."
This is the "cross-dispatch without cross-contamination" half of the idea.
Save risk: none (runtime only).

## Layer 3 — Adjustable extender radius (the user's original proposal)

Extenders stop projecting their own fixed blob; an extender in range of a hub
raises that hub's **user-assignable maximum** instead. Player regains control,
overlap becomes chosen rather than forced, and multiple hubs can benefit from one
extender (gated by having to be in its range).

- **Numbers:** hub 50 (with SignalBoosters) + extender 35 = 85 combined. That is
  **inside** the 100-hex travel cap, so nothing breaks structurally — but it is
  70% past the engine's own coverage ceiling of 50, and the cost lands as **lap
  time**, which `DroneReport` already measures. Consider capping the combined max
  (50? 65?) once lap data exists. User's stated intent: mostly ~75%, occasional
  temporary max for a niche corner during terraforming.
- **Counter-argument on record:** today's extender gives *directional* reach; a
  concentric boost must cover everything at that distance in all directions, so
  raw overlap could rise. The rebuttal is that overlap becomes *chosen*.
- **Costs:** the slider max is class-level property metadata → patch at
  `ClassesPostprocess` and clamp per-hub. **This is the only layer with save
  residue:** modifiers are stored on the object, so an uninstall leaves hubs
  permanently boosted. Must clear on toggle-off. Radius changes also trigger
  re-registration → F77 debounce.

## Layer 4 — Command Center drone tab (recommended second; zero save risk)

A **dedicated tab**, not columns bolted onto Transportation — that tab already
carries rockets, trains, rovers and shuttle hubs, and a robust drone view would
swamp it. A separate tab is also **safer**: editing the vanilla row means a game
patch or another UI mod can break us inside a screen used for other things,
whereas our own template fails in isolation and deactivates via the standard
apply-time self-check.

Contents: per-hub rows (fleet size, avg lap over the last sol, idle %, suggested
range, unclaimed, bottleneck rank), extender/cluster topology, the module
counters (`vetoed / veto_expired / moonlighted`), colony prefab pool, and the
+/- actions inline so advice is one click from action.

### 4a — Drone-count advisory (high value, cheap)

**Vanilla already tells you when you need MORE drones (`UpdateHeavyLoadNotification`)
and has NO signal for having too many.** Fill the other half of a comparison the
game already makes — so this reports against the game's own thresholds rather
than inventing balance opinions (FIX_POLICY §4).

- Sample per hub hourly: lap time, fleet size, idle count, unclaimed. Rolling
  24-sample (one sol) window, **module-local and weak-keyed — runtime only, like
  the existing counters**, so zero save impact. Show "sampling… N/24h" before it
  is meaningful.
- Mean lap far below `DroneLoadLowThreshold` + high idle → over-provisioned.
  Mean at/above medium → under-provisioned, quantified. **Peak** lap over the
  window drives build-out padding (construction is exempt from the claim gate =
  pure extra demand).
- `target ≈ current × (current_lap / target_lap)` is an approximation (travel
  time doesn't scale linearly, there's a floor) → present a **range with the
  inputs visible**, never a single authoritative number, never auto-act.
- **Strategic value:** over-provisioning is how players *hide* dispatch problems.
  This turns the overhaul into a bankable saving in prefabs and power — and is
  the honest self-check: if nobody's suggested count ever drops after the
  dispatcher ships, the dispatcher didn't work.

## Layer 5 — "Drone Command Center" building (optional, last, gated on PT-20)

User idea: a unique building that owns dispatch. **Feasible** — `items.lua`
already ships `PlaceObj` mod items, a vanilla entity can be reused, no custom
art. It would add a power cost, a real failure mode (malfunction/power loss
degrades dispatch to vanilla — free, since hooks already gate per call on
`IsActive`), and an in-world home.

**It is the only layer with genuine save risk**: a placed object of a
mod-defined class. On uninstall the class is gone — outcome unknown, ranging
from "object dropped with log errors" to a load failure. **This is measurable,
not arguable: PT-20 is exactly that test.** Mitigations: keep it a **leaf in the
object graph** (nothing else stores a reference; look it up on demand), minimal
persisted members, and graceful degradation while installed.

**It adds no capability** — the module already has total global awareness
(`DroneReport` walks every map, city, hub, extender and queue). The building is a
*gate* and a *cost*, not an enabler. Note also that layer 4 delivers the "one
place that shows everything, with bottlenecks and controls" experience with zero
save risk, which is most of what the building was wanted for.

## Risk table

| Layer | Save risk | Notes |
|---|---|---|
| 1 Dispatcher | **none** | references to vanilla hubs only; self-heals |
| 2 Cluster scoping | **none** | runtime only |
| 4 Command Center tab + advisory | **none** | UI templates are not persisted; own template = isolated failure |
| 3 Adjustable radius | **mild residue** | modifiers persist on the object; clear on toggle-off |
| 5 Building | **real, testable** | mod-defined persisted class; PT-20 verdict decides |

## Open questions — resolve BEFORE building

1. **Is `command_centers` persisted, or rebuilt on load?** If rebuilt, layer 1's
   residue is zero rather than merely harmless. Not verified — do not assume.
2. Queue-size/perf impact of many-to-many registration on a 9-hub, 437-building
   colony. Measure with the stress harness (`SMRTest.Stress`).
3. Does the dome early-return path (`_TaskRequest.lua:266-271`) need the same
   treatment, or is dome-inherited registration already correct?
4. Combined-radius cap for layer 3 — pick from live lap data, not from theory.
5. ~~**Src vs shipped `Lua.fpk` divergence** — proven real this session
   (`GetCameraLookAtPassable` exists in Src, does not exist at runtime).~~
   **[WITHDRAWN 2026-07-29 — misreading: that function is a Cheats.lua
   file-local, console-invisible by design; the full extraction diff proved
   the shipped build IS Src (2,250/2,256 byte-identical, divergences
   engine/tooling only) — see ENGINE_FACTS.md.]** Apply-time self-checks stay
   for every layer regardless: they guard future game updates.

## Recommended order

1. **Dispatcher** — the actual behaviour win, near-zero risk, measurable with the
   stress harness.
2. **Command Center tab + advisory** — zero risk, delivers the framing the user
   wants, and quantifies whether step 1 worked.
3. **Cluster scoping** — once dispatch is proven and grouping is wanted.
4. **Adjustable radius** — after dispatch stops being the bottleneck; the
   pressure to grow radii should be lower by then.
5. **Building** — only behind a PT-20 verdict, purely as gate + cost + failure
   mode. Nothing from 1-4 is wasted if it is rejected.

# I + J — seed-supply routing pair (added 2026-08-15 out of the fix pack's C47/C48 measurement chain)

⚖️ **OWNER RULING, 2026-08-15, recorded verbatim: "I am not going to manipulate
drone behavior on a bug fix mod."** ⇒ Every behavioral remedy for the
`C47`/`C48` seed-routing family lives HERE, in this house, behind this pack's
default-OFF convention — the fix pack gets, at most, data-shaped repairs, and
only after `C48` is ruled. This section is the standing record of that boundary.

**Provenance.** The fix pack's `C48` leg (2026-08-15, `archive/c48veg_*` in that
repo) measured the routing signature on the owner's own colony: **134 deliveries
to two farms at 200 ms sampling, not one a full drone trip (3,000 on the rig),
83.6% exactly 280 = one bush's yield at soil 100, while 12.4M stored Seeds
across 34 depots did not fall.** Mechanism source-verified there:
`VegetationTaskRequester` posts ONE request per PLANT for
`GetVegOutputAmount(preset)` (Bush 200 × soil bonus ⇒ 280 ceiling,
`Vegetation.lua:1848-1851`), inherits `supply_dist_modifier = 100` (no distance
brake; the tree's only override is `SurfaceDeposit = 150`), and carries
`priority = 1`. The drone side is NOT seeds-specific: one trip serves exactly
one supply request and takes `min(capacity, what that request holds)`
(`Drone:PickUp`, `Drone.lua:940-1014`; `FindTask` pairing is C-side). A bush
outbidding a depot therefore wastes ~90% of the trip's capacity on a +2-carry
rig, every time.

## I. Cargo top-up on the way to deliver — the "gleaner"

**What.** After a drone completes its assigned pickup with cargo below
capacity, let it claim additional same-resource supply requests within a
bounded radius of where it stands (or roughly on the corridor to its
destination), topping up before it delivers. Converts 280-per-trip seed crumbs
into up-to-capacity loads — on the owner's rig, roughly **10× fewer trips for
the same seed flow**.

**Why it is legal (each point rests on a verified ground rule above or a fresh
2026-08-15 source read):**
* The C matcher's CHOICE is untouchable (ground rule 1) — this option does not
  touch it. It extends what the drone does AFTER assignment, which is all Lua.
* ⭐ **Vanilla precedent for post-assignment second-guessing already exists on
  the demand side**: `Drone:Deliver` calls `ImproveDemandRequest` — *"req,
  coming from PickUp, find a better dest"* (`Drone.lua:1172-1175`). The gleaner
  is the mirror image on the supply side.
* ⭐ **The seam is vanilla-provided**: `Drone:PickUp(s_request, d_request,
  resource, amount, dont_chain_deliver)` — a pre-wrapper calls the vanilla body
  with `dont_chain_deliver = true`, runs the top-up loop, then
  `SetCommand("Deliver", d_request)` exactly as vanilla would have
  (`Drone.lua:940,1013-1014`).
* Claims are atomic and Lua-visible (`RequestAssignUnit` /
  `RequestUnitFulfill`, ground rule 3); each extra hop must replicate the
  vanilla Push/PopDestructor discipline (`Drone.lua:956-995`) so an interrupted
  drone releases every reservation.
* **Over-carry is a handled state, not a new failure mode**: `Deliver` clamps
  to the destination's remaining need (`Min(amount,
  d_request:GetTargetAmount())`, `Drone.lua:1183`), leftover cargo goes through
  the idle-with-cargo path (find another demand), and the terminal fallback is
  vanilla `CreateDumpingStockpile` (`Drone.lua:1195`).
* **Save/uninstall shape**: commands are restartable — `SetCommand` persists
  name + args and the command re-runs from scratch on load (why `PickUp`
  re-asserts its claims at the top). The wrapper passes only vanilla-shaped
  args, so a save taken mid-glean loads without the mod as a plain vanilla
  `PickUp` retry. Same safety class as the built D06 core; still owes the
  standard save-contract proof before shipping.

**Guards it must ship with** (the failure mode is not a crash, it is a drone
wasting its life hopping bushes): hard cap on extra stops · hard radius ·
a gate on when gleaning is allowed — lowest-priority resources only (seeds are
already `priority = 1`, so a seeds-only v1 is self-selecting) or hub load
reading Low via `CalcLapTime` (ground rule 7, free to read).

**v1 scoping: SEEDS-ONLY GLEANER.** Smallest blast radius, biggest measured
win, self-selecting priority gate. Generalising to all resources touches every
logistics flow in the game and is a separate decision.

## J. Scattered-source distance brake — the devs' own number

**What.** `VegetationTaskRequester.supply_dist_modifier = 150` — the exact
value and rationale the developers applied to the only comparable scattered
source (*"surface deposits are considered 50% further than storages"*,
`SurfaceDeposit.lua:84`). One field, class-level, no wrapper.

* ⭐ **Propagation is self-healing**: the modifier is baked into each request at
  creation (`Request_New`, `_TaskRequest.lua:154`), BUT the requester
  population churns fast — the C48 ladder watched it move 3,583 → 3,457 →
  3,304 → 3,637 within 14 game hours (every harvest destroys one, every
  cooldown expiry spawns one) — so a class-level change reaches most of the
  live population in hours of game time with zero teardown surgery.
* ⚠️ **Known limit, stated up front**: the brake multiplies DISTANCE. On a
  carpeted map where bushes stand beside the farm, a 150 brake may barely move
  the routing — the fix pack's planned intervention leg tests exactly this
  before anyone trusts the knob. If that leg refutes it, option J dies and
  option I (which attacks trip EFFICIENCY, not source choice) is the survivor.
* ⛔⛔ **REFUTED 2026-08-15, the same evening, by that leg** (fix pack
  `archive/c48brake_*`, owner-authorized): the brake was applied at 100% — all
  3,390 live requests rebuilt and provably rebaked at 150 — and **the routing
  did not move**: the 280-crumb wall stood in the braked window (86–88%/68%),
  zero bulk arrivals appeared, and the farms went on eating the landscape.
  Exactly the known limit above, now measured. **Option J is DEAD. Option I
  (the gleaner) is the surviving remedy, strengthened** — it works regardless
  of why drones pick the landscape. ⭐ The propagation-churn claim below was
  incidentally confirmed live (3,580 → 3,702 requesters across 10.5 game
  hours).

**Relationship.** I and J are complementary, not alternatives: J tries to send
drones to depots more often; I makes the landscape trips that still happen cost
what they should. Either could ship alone.

⛔ **Parked per the FUTURE_IDEAS hard rule** — nothing here is built, and
un-parking is an owner decision after launch. Cross-reference: fix pack
`agent/bugs/C47.md` + `C48.md` (the measurements), this repo's `D02.md` (the
flapping boundary the same sitting found), FUTURE_IDEAS item 7.
