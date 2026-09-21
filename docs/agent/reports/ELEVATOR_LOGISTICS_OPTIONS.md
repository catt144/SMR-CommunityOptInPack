# Elevator cargo logistics — options report (design, no build)

**Origin (owner, 2026-09-21).** The surface↔underground Elevator's cargo pain is an Opt-In
Modules matter, not a fix-pack defect. This report designs options; it does not re-argue the
placement and nothing here is built. Player report (Reddit, 2026-09-20): *"You can't push lots
of stuff up or down. You can trickle stuff through the elevator but not any serious amount of
produce. You will have to move stuff manually with a rover to/from the elevator."*

**Method.** Desk only, 2026-09-21. Installed build read from
`A:\SteamLibrary\steamapps\appmanifest_3215050.acf`: `buildid 24995074`, `TargetBuildID 0` — the
brief's build, so stop (3) did not fire. Every citation is `<path>:<lines>` inside
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908\Src\`; `1.0.7.396349` is cited only where a
difference is stated. **The game was not launched.** Every behavioural statement about the
elevator is *predicted from source; engine rule unmeasured*. §6 is the sitting that measures it.

⚠️ Reports are not authority. No module exists; building any option needs an owner ruling
recorded for this mod and an `agent/bugs/` entry (`FIX_POLICY.md` §4).

---

## 1 · What the source says, beyond the fix-pack pass

The fix-pack pass holds on re-read (`Lua/Buildings/Elevator.lua:10-32`, `:124-127`, `:177-230`,
`:260-316`, `:1047-1068`). Its falsifier was re-run:
`rg -n "SetDesiredAmount|desired_amount" …/Lua/Buildings/Elevator.lua` → 3 hits, `:17`, `:124`,
`:126`. Four findings change the design space.

**1.1 · The "desired level" is two numbers, and only the slider ties them.** Every depot
resource has a demand request and a supply request, each carrying its own desired amount.
`StorageDepot:SetDesiredAmount` (`Lua/Buildings/StorageDepot.lua:84-97`) always writes the
complement: supply gets `D`, demand gets `max − D`. `MultiResourceDepotBase:UpdateRequestCapacity`
(`Lua/Buildings/MultiResourceDepot.lua:217-223`) and `RecalculateAfterResourceListChange`
(`:379-407`) rewrite the same complement.

**1.2 · The Station pattern is that complement at its two ends, per resource.**
`Station:SetDesiredAmount` (`Lua/Buildings/Station.lua:964-995`): "accept" writes demand `max`,
supply `0`, which is exactly `D = 0`; "send" writes demand `0`, supply `max`, exactly `D = max`.
The authors' comments give the drone-side meaning: `D = 0` — *"only take the resource away from
here by other means"*; `D = max` — *"only bring the resource here by other means"*. A Station
needs only one end because the train is the other leg. **The elevator needs both ends at once**
— bring here on the giving map, take away on the receiving map — and a single `D` cannot say
that. This is the brief's "one desired level serves both sides", restated in the authors' words.

**1.3 · The one-way states already split the two requests across the two maps.**
`ShouldAddRequestToCommandCenter` (`Elevator.lua:201-230`): in `to_surface` the underground hubs
see *only the demand* request and the surface hubs see *only the supply* request
(`to_underground` mirrors it). So in a one-way state the two desired amounts can be set
independently and no hub ever sees a contradictory pair: **demand desired `0`** (the "send" end:
drones bring stock here) **and supply desired `0`** (the "accept" end: drones take all of it
away). The slider cannot reach that pair; two `SetDesiredAmount` calls on the request userdata
can. That is option A.

**1.4 · The shuttle pairing rule is now readable from the developers' own test.**
`GameTests.ShuttleTaskFillOrder` (`Lua/Dev/GameTests.lua:452-554`) pins `Request_FindShuttleTask`:
a storage→storage transfer is admitted when the source's *fill index* (stock ÷ its supply
request's desired amount) is higher than the destination's; *"a keep-0 destination has no fill
ratio, so the order must not be compared at all"* (`:532-533`, expected 1 task); a mechanized
destination with no deficit absorbs surplus (`:534-535`). The test does not exist in 1.0.7
(`rg -c ShuttleTaskFillOrder 1.0.7.396349/Src/Lua/Dev/GameTests.lua` → no hits): the guard is
new in 1.1.0. It agrees with the slider tooltip, *"storages with higher Desired Amount will be
filled first … stored resources will still be used when needed"*
(`Data/XDef/sectionMultiResourceStorage.lua:13`).

**What stays unverified.** The *drone* matcher (`Request_FindTask`, C side, reached only through
`Lua/_TaskRequest.lua:73-85`) is unread. Whether it uses the same fill-index ordering as the
shuttle finder or a plain above/below-desired rule is unknown; both predict a stall near `D`
for depot-sourced stock and both predict option A flows. A source with supply desired `0` is not
covered by the developers' test either. The fix pack's measured facts cover only the consumer
side: desired withholds nothing from consumers (C48, `StorageSeeds#14612` reading) and depot
supply is the matcher's last resort (EF-059). RC Transport routes were not read beyond the
elevator's `RoverLoadResource` pass-through (`Elevator.lua:524-528`).

**The pre-rework carrier cannot be traced.** Only stubs survive (`Elevator.lua:1322-1326`:
`Load`, `UpdateInstantTransferCargo`, `UpdateCargoRequestToMinimumFor`; fields `cargo`,
`cargo_minimum`, `departures`, `boarding` cleared at `:1380-1393`). 1.0.7 already has the shared
depot (`rg -c MapSharedDepot` → 25) and the same stubs, so the rework predates both archived
trees. The names say it was a manifest carrier with a per-resource minimum on each side — which
is a two-level design, the thing §1.2 says the shared depot lost. "It used to be great" is
consistent with that and not provable from disk.

**Developer activity on these lines.** `diff` of `Elevator.lua` 1.0.7 → 1.1.0 changes 432 lines
(`diff … | grep -cE "^[<>]"`), concentrated in `SetAcceptResourceState`, lock-state handling and
fixups. Collision ratings below are set against that.

**Predicted vanilla behaviour, for the record.** In `to_surface` at the default `D = 10`:
underground drones pull depot stock in only until the elevator holds 10; producer overflow can
fill it to 50; surface drones move only the stock above 10 into surface depots, and only into
depots whose own desired amount is above zero; consumers draw from it last (EF-059). Stop (1)
did not fire: nothing read makes the one-way modes pump already.

---

## 2 · Options

Ratings: **save** uses `FIX_POLICY.md` §3a tiers; **collision** is against a developer patch
to `Elevator.lua` / `MultiResourceDepot.lua`.

### A · One-way pump — split the desired pair in the one-way states (minimal)

- **Mechanism.** For each resource whose state is `to_surface` or `to_underground`:
  `demand[res]:SetDesiredAmount(0)` and `supply[res]:SetDesiredAmount(0)`. For `bidirectional`
  and `disabled`, the vanilla complement from `depot.desired_amount`.
- **Hook points.** A post-hook on `MapSharedDepot.SetAcceptResourceState` (state changes), plus
  a re-apply after the three vanilla writers of the complement: `SetDesiredAmount` (inherited
  from `StorageDepot`; the slider), `UpdateRequestCapacity` and
  `RecalculateAfterResourceListChange`. `MapSharedDepot:CreateResourceRequests`
  (`Elevator.lua:111-122`) already funnels new requests through `SetAcceptResourceState`. One
  sweep over `city.labels.Elevator` (the label `Elevator.lua:262` uses) on `PostLoadGame`,
  `CityStart` and `ApplyModOptions` reconciles to the current option, including back to vanilla
  when it is off. All synchronous; no thread, no stored function (§3a layer 3/2 by construction).
- **Player-facing.** No new control: the direction toggle the player already uses starts to
  mean it. The resource rollover (`ResourceRolloverText`, `:197-199`) gains a line in one-way
  states: *"Pumping: drones fill the elevator from this side's depots and empty it on the other.
  The Desired Amount slider applies to ON resources only."* Receiving depots still need a
  desired amount above zero to be restocked from it — ordinary depot play, worth one sentence in
  the option description.
- **Balance.** No free movement: every unit still rides a drone or shuttle on each side, and
  the 50 buffer still bounds a burst. It removes a dead end rather than adding capacity.
  The pump drains the giving map's *surplus* only — stock above each depot's own desired amount
  — so a player protects underground reserves the normal way. Risk to watch: a `to_surface`
  pump competes with underground depots for producer output as an equal storage demand.
- **Save / uninstall.** Request desired amounts persist in the save. After removal one-way
  resources keep pumping until the player moves the slider to a *different* value
  (`StorageDepot:SetDesiredAmount` early-returns on an equal one, `:85`). Tier 2: inert, bounded,
  player-reversible, disclosed. Turning the option off while installed restores the complement
  in the sweep, so off is clean.
- **Collision.** Low–medium. It reads one table (`resource_storage_states`) and calls one
  request method the developers use themselves. If a patch ships the same split, the module
  writes the same values and becomes a no-op; if a patch adds per-side levels, the module's
  require-check on the state table should stand it down.
- **Reachability.** R1: the direction toggle is on the stock elevator panel
  (`Lua/XDef/customElevator.generated.lua:74-75`), on every platform.

### B · Buffer dial — raise the 50-per-resource cap

- **Mechanism.** `max_storage_per_resource` is a modifiable property
  (`StorageDepot.lua:332`), and `MultiResourceDepotBase:OnModifiableValueChanged`
  (`MultiResourceDepot.lua:225-240`) already re-derives slider range, clamps the desired amount
  and resizes every request; shrinking below current stock is handled by
  `Max(0, new_cap − stored)` (`:220`). A `ModItemOptionChoice` dial — base 50, steps 100 / 200 /
  400 — applied as a modifier under one string id on each `shared_depot`, reconciled on the same
  three messages as D09 `DroneStatDials` and on `SetupSharedDepot` (`Elevator.lua:448-459`) for
  new links. The depot is not in an elevator-only label (it sits in `AllStorageDepots` with
  every depot), so the D09 label route does not transfer unchanged; the per-object modifier call
  is the one API detail to confirm at build.
- **Player-facing.** One dial in Mod Options; the panel's capacity figures follow by themselves.
- **Balance.** Free storage: the shared depot has no footprint and no cubes
  (`Elevator.lua:23-31`). 400 × every transportable resource per elevator is a large invisible
  warehouse; 100–200 is a buffer. By itself B does **not** fix flow — a bigger tank that parks
  at `D` is still parked. It matters only beside A, where it smooths bursts between two drone
  fleets working at different rates.
- **Save / uninstall.** Same shape as D09: a vanilla `Modifier` under our string id persists; a
  save loaded without the mod keeps the larger cap until cleaned (tier 2, benign; the id becomes
  a persisted name and joins the `FIX_POLICY.md` inventory). Base position removes it.
- **Collision.** Low: a documented modifiable property with the developers' own change handler.

### C · Freight run — the elevator moves stock itself (bold)

- **Mechanism.** A post-hook on the elevator's building update (`building_update_time = 1000`,
  `Elevator.lua:575`), throttled to once per game hour: for each one-way resource, take up to
  *N* units from giving-side depots connected to the elevator's command centers — limited to
  each supply request's unassigned surplus above its desired amount (`GetTargetAmount`, never
  `GetActualAmount`, so stock a drone is already walking toward is not taken) — into the shared
  depot, and push shared-depot stock out to receiving-side depots below their desired amount,
  through the depots' own `AddResource` paths. No thread of ours; the vanilla update calls us.
- **Player-facing.** Genuinely "bulk movement without rovers or drones". Needs a rate dial
  (say 10 / 25 / 50 per hour per resource) and honest wording that cargo is teleported within
  the elevator's service range.
- **Balance.** Heavy. It deletes the drone cost of the busiest haul in an underground colony.
  The coherent price is electricity per unit moved, but the elevator's consumption is 0 with a
  lowered-power fixup in its history (`:582`, `:1496`), so any figure is ours, without sibling
  evidence — a §4 "arbitrary constant" concern.
- **Save / uninstall.** Clean in principle (synchronous, moves real stock through vanilla
  paths). The risk is request bookkeeping: every transfer must leave each depot's request
  amounts consistent, across two maps.
- **Collision.** High. It depends on depot internals the developers changed in 1.1.0
  (`MultiResourceDepotBase` is new-shaped there) and on cross-map object handling.

### D · Rejected after reading: make the elevator a first-class source

Clearing `rfStorageDepot` from the elevator's supply would lift it out of the matcher's
last-resort class (EF-059) so consumers draw from it first. **Do not:**
`SetAcceptResourceState` derives "enabled" from that exact flag (`Elevator.lua:278-280`), and
`SetAcceptResource` toggles it (`MultiResourceDepot.lua:271-281`); clearing it makes the game
read the resource as disabled. The sanctioned route to the same end is a class-constrained
re-query at `TaskRequestHub:FindTask` (EF-060) — a matchmaker wrapper carrying every drone
assignment in the colony, far out of proportion to this pain.

### E · Not offered: rebuild the pre-rework carrier

No code survives to restore (§1); it would be a new transport system on the most-churned file in
this area.

---

## 3 · Pain points against options

| pain | A pump | B dial | C freight |
|---|---|---|---|
| one-way pumping | **yes** — the core of it | no | yes |
| stranded underground depot stock | **yes**, for surplus above each depot's desired amount | no | yes |
| the 50 buffer | softened: it stops mattering once stock moves through | **yes** | partly |
| bulk movement without rovers | drone- and shuttle-limited; scales with fleets and with D09's carry dial | no | **yes** |

## 4 · Recommendation

**Build A, with B as a dial in the same module; hold C until a sitting says A's throughput is
still a trickle.** A is the smallest change that addresses the mechanism the source names, uses
a call the developers use for the same purpose, gives the existing UI its evident intent, and
degrades to a no-op if the developers ship the same fix. B costs little and is only meaningful
beside A. Ship both off/base. Working name `ElevatorPump`: one toggle (A), one choice dial (B).

C is the only option that answers "serious amounts without drones", but it is a balance opinion
with an invented price and the highest patch exposure. The owner's prototype-first practice
points the same way: measure A in play before designing C's numbers.

Owner decisions this would need, none asked yet: whether to build at all; whether B's top step
is 200 or 400; whether A's residual (pump levels stay in a save after removal until the slider
moves) is accepted as tier 2.

## 5 · Stops

1. Engine rule makes one-way modes flow already — **not fired** on the source reading (§1);
   §6 step 2 is where it would fire in play.
2. A state Steam/console players cannot reach — **not fired**: A and B hang off the stock panel
   and Mod Options. Step 3's console paste is the owner's probe, not the product.
3. Developer patch moved the lines — **not fired**: installed `buildid 24995074`.

## 6 · One sitting: settles the drone rule and prototypes A, no build

Needs a save with an elevator, drones on both sides, and one spare resource (Concrete below).
The console is the owner's probe only.

1. **Set up.** Underground: a depot holding ≥ 30 Concrete, its desired amount 0. Surface: a
   Concrete depot with desired amount 30, currently short. Elevator: Concrete `to_surface`,
   slider at the default 10. Note the three stock figures.
2. **Vanilla leg, ~2 sols at speed.** Prediction from source: the elevator rises to about 10 and
   stays; the surface depot gains little or nothing from underground depot stock. *If the surface
   depot fills instead, stop (1) has fired in play: A is unnecessary and this report's premise
   is wrong.*
3. **Apply the split** (console, once):
   ```lua
   for _, e in ipairs(UICity.labels.Elevator or {}) do local d = e.shared_depot
     if d then for res, st in pairs(d.resource_storage_states or {}) do
       if st == "to_surface" or st == "to_underground" then
         d.demand[res]:SetDesiredAmount(0) d.supply[res]:SetDesiredAmount(0)
   end end end end
   ```
4. **Pump leg, ~2 sols.** Prediction: underground stock drains through the elevator and the
   surface depot fills to its 30. That result settles the drone rule in the direction that
   matters (split levels flow, tied levels stall) and is option A working.
5. **Read three more things while it runs:** whether producer output underground starts
   favouring the elevator over local depots (A's balance risk); whether shuttles join in (the
   untested source-desired-0 case of §1.4); and that moving the slider to a new value puts the
   vanilla complement back (the uninstall remedy in A).

If step 4 stalls too, neither reading of the engine rule holds and the next instrument is the
fix pack's log-only `FindTask` wrapper (EF-060) pointed at the elevator's two requests.
