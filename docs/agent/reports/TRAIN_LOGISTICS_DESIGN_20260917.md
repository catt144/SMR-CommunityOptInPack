# Train logistics — design spec for two new modules against game 1.1.0.403908

**Origin (owner, 2026-09-17).** The 1.1.0 train overhaul removed the station resource
request sliders. The owner asked what it would take to restore control, then set the
target higher: a per-resource import/export design of our own rather than a restoration,
and — separately — whether a train junction hub is reachable. This spec answers both and
is written **to be implemented**. It is a decent-size lift and is not a session's work.

**Method.** Desk only. Every claim is read off the archived tree
`C:\Dev\SMR-SrcArchive\1.1.0.403908\Src`, which matches installed build `24995074`
(`python tools/doccheck.py --emit-fingerprint`, 2026-09-17), with
`C:\Dev\SMR-SrcArchive\1.0.7.396349\Src` cited only where a difference is stated.
Citations are `<path>:<lines>` within that tree. **The game was not launched and no
playtest was run.** Every behavioural claim here is static-read; §7 lists what must be
tested before any of it is believed.

**No code was changed.** MODULE FREEZE holds. Nothing here is built, and neither module
exists yet.

⚠️ Reports are not authority. Where this disagrees with `agent/bugs/`, `agent/facts/`,
`WORKFLOW.md` or `FIX_POLICY.md`, those win. OI-10 was ruled on 2026-09-18 (§10) and has left the
checklist. The §6 calls the ruling did not settle return there when their next action is the
owner's.

---

## 1 · What 1.1.0 did, and what it did not

`Station` was re-parented from `UniversalStorageDepotBase` to `MultiResourceDepotBase`
(1.0.7 `Station.lua:46-56` → `Station.lua:48-57`); the file went 1432 → 1746 lines with
787 changed. `Data/XDef/sectionStorage.lua` was deleted and replaced by
`sectionMultiResourceStorage` + `contextResourceAcceptToggles` + `sectionResourceGroupStorage`.

**The slider was not removed. It was gated off for stations alone.** The whole "Desired
Amount" section survives verbatim, `InfopanelSlider BindTo "DesiredAmountSlider"` included,
behind one condition — `Lua/XDef/sectionMultiResourceStorage.generated.lua:18`:

    local cond = not IsKindOf(context, "Station")

Source XDef: `Data/XDef/sectionMultiResourceStorage.lua:11`. Every other depot keeps it.

**The mechanism behind it is live, not vestigial.** `Station:SetDesiredAmount`
(`Station.lua:964-994`) still walks demand/supply per resource;
`Station:SetAcceptResourceState` still reads `self.desired_amount` (`:1038-1039`);
`desire_slider_max` / `desired_amount` still ship on the station templates; and the
station's inheritance still reaches the slider API — `Station` → `MultiResourceDepotBase`
→ `StorageDepot` → `ResourceStockpileBase`, which declares `GetDesiredAmountSlider` /
`SetDesiredAmountSlider` / `GetDesiredAmountUI` (`ResourceStockpile.lua:119,202,217,231`).

**Two one-way savegame fixups shipped with it:** `StationsToMultiResourceDepot` and
`RevertStationDesiredAmount` (`Station.lua:1741-1745`), the latter force-resetting every
station to its class default. Fixups run alphabetically, not in definition order
(`CommonLua/SavegameFixup.lua:33`), so `Revert…` lands first.

**Why it was gated — inference, not fact.** No comment states intent, no changelog ships
in the tree, no VCS history is available. The weight of evidence is deliberate design
removal: no TODO/WIP/HACK markers anywhere near it; the section was re-authored with
all-new string ids rather than commented out; a fixup that *flushes* the player's value
is what you write when a value should stop varying, not when you intend to restore it;
and the arithmetic is consistent, so they were not hiding a broken path
(`MultiResourceDepot.lua:161` recomputes `desire_slider_max` from
`GetMaxStorageForAnyOneResource()`, and both writers then agree). The one loose end
pointing the other way is `Train:UpdateTransportedResourceRow` (`Train.lua:1054`), now
orphaned with no callers.

⇒ **Consequence for design.** `station.desired_amount` is the layer the developers are
walking away from. Anything we build should bind lower — see §2.

---

## 2 · The stability ranking that drives both designs

Ranked by what survived the 787-line rewrite, most stable first:

| # | Layer | Fate |
|---|---|---|
| 1 | `req:SetDesiredAmount` / `GetDesiredAmount` on request objects | **Native C++** — absent from Lua in both trees. Untouched |
| 2 | `TaskRequester:AddDemandRequest` / `AddSupplyRequest` | Thin Lua over native bindings (`_TaskRequest.lua:128-151`). Unchanged |
| 3 | `station.demand[res]` / `station.supply[res]` | Same shape in both builds |
| 4 | `Station:SetDesiredAmount` / `station.desired_amount` | Survives, unreachable by the player, flushed by a fixup |
| 5 | `sectionMultiResourceStorage:Init` | XDef-generated, rebuilt, carries the carve-out |

**Build on 1–3. Do not build on 4–5.** Restoring the vanilla slider would bind us to
exactly the two decaying layers.

---

## 3 · What the train balancer actually reads

All in `Train:TransferCargo` (`Lua/Units/Train.lua:836-1020`), per resource per route:

    res_data.desired[res] += st:GetResDesiredAmount(res)   -- summed route-wide
    res_data.storage[res] += st:GetMaxStorage(res)         -- summed route-wide
    ...
    if res_data.desired[res] > 0 then                      -- GATE: balance this res at all?
        target = MulDivRound(res_data.total[res], storage, res_data.storage[res])  -- WEIGHT

**Desired amount is a gate, not a weight.** Distribution is proportional to per-resource
storage capacity. The per-resource rollover — byte-identical in both builds — says as
much: trains balance *"regardless of the desired amount in the Stations"*.

Task priorities are `ttPrioBalance = 0`, `ttPrioForbidden = 1`, `ttPrioShortage = 2`
(`Train.lua:729-731`). **`ttPrioShortage` is never passed to `add_transport_task` in
either build** — a dead priority lane the sorter already honours. Train capacity is a
shared pool (`max_shared_storage`), not per-resource.

**Measured 2026-09-18 (§7.2 T2):** per-route balancing composes through a shared station, and
a two-route network settled at network-wide capacity shares.

**Ceiling without owning the scheduler:** per resource × per station × per route. Out of
reach: per-train, per-direction, inter-resource priority, time-based rules.

---

## 4 · Module A — per-resource station import/export

### 4.1 The design (owner, 2026-09-17)

Per resource at a station, two states plus neutral:

- **Import**: trains bring it in up to a set amount; **drones may still drain it to zero**.
- **Export**: trains take everything above a set minimum; **drones fill it to max**.

### 4.2 ⭐ The design is already in the game, unwired

`Station:SetDesiredAmount` (`Station.lua:974-991`) — the game's own comments:

    local policy = self:GetTrainTransportPolicy(res)
    if policy == "accept" then
        -- we accept by train, we want to only take the resource away from here by other means, set as if desired is 0
        req:SetDesiredAmount(max);  supply[res]:SetDesiredAmount(0)
    elseif policy == "send" then
        -- we send by train, we want to only bring the resource here by other means, set as if desired is max
        req:SetDesiredAmount(0);    supply[res]:SetDesiredAmount(max)

"Accept by train, take it away by other means" is import. "Send by train, bring it here by
other means" is export. Per resource. That is the owner's design in vanilla's words.

**It is dead code, verified in both builds.** `Station:ToggleTransportResource`
(`Station.lua:1061-1076`) cycles `transport_policy[res]` default → send → accept with
ctrl-click broadcast already written, and **has no callers** — the cycler is the only
writer of `transport_policy` anywhere in either tree. Separately,
`Station:SetAcceptResourceState` (`:1021-1053`) accepts `"store"` / `"export"` /
`"disabled"` and **`"export"` is never passed**; live callers pass only the other two
(`:1058`, `:1491`). The surviving per-resource row `sectionStorageRow` calls only the
two-state `ToggleAcceptResource`.

**But it is consumed by live code.** `Station:GetTrainTransportPolicy` (`:1078-1082`)
returns `"send"` for any disabled resource — so disabling a resource already routes
through the export branch in normal play today. A disabled resource is emptied by the
*forbidden* branch, whatever the policy says (§7's correction; T1 measured it, §7.2).

**Measured 2026-09-18 (§7.2 T3):** the unwired `send` works when driven by hand, making the
station a drone-fed export pump. `accept` showed no drone effect in a fixture with no
Metals consumer in range, and is unconfirmed.

### 4.3 Design → mechanism

| Element | Vanilla status | Work |
|---|---|---|
| import/export per resource | `transport_policy[res]` exists, consumed, no UI | **UI only** |
| import: drones drain to zero | `supply desired = 0` — the `accept` branch; **UNCONFIRMED** 2026-09-18 (§7.2) | **none**, if a later fixture with a Metals consumer confirms it |
| export: drones fill to max | `supply desired = max` — the `send` branch; **MEASURED** 2026-09-18 (§7.2) | **none** |
| import **up to N** | amount hardcoded to 0/max in both branches; the slider reaches only the `default` branch | small — make `SetDesiredAmount` per-resource-aware; the absolute cap falls out of per-resource capacity, since `load_amount` is already clamped by `dest.demand[res]:GetTargetAmount()` |
| export **down to floor N** | **MISSING** — the train reads `available = Min(supply:GetTargetAmount(), supply:GetActualAmount())` and never subtracts a floor; only `needed`, a proportional share, is held back | **the one genuinely new thing** — requires intervening in `Train:TransferCargo` |

### 4.4 Phasing

- **Phase A1 — import.** Per-resource policy UI + per-resource amounts + per-resource
  capacity allocation via `GetMaxStorage(res)`. Rides existing mechanism; no scheduler
  contact. Delivers half the design.
- **Phase A2 — export floor.** Intervene in `TransferCargo` so `available` subtracts a
  player floor. Rule on this **separately**, after A1 has been played.
- **Reserve — own the scheduler.** Populate the dead `ttPrioShortage` lane for
  demand-driven hauling instead of proportional parity. Deepest patch exposure.

### 4.5 Six vanilla paths that rewrite per-resource desired amounts

Our values must survive all of them:

| Site | Fires when |
|---|---|
| `Station:SetDesiredAmount` (`:964`) | the flatten loop |
| `Station:SetAcceptResourceState` (`:1038-1045`) | **every accept/export/disable click**; the re-enable click MEASURED 2026-09-18 (§7.2) |
| `MultiResourceDepotBase:UpdateRequestCapacity` (`MultiResourceDepot.lua:221-222`) | capacity change |
| `MultiResourceDepotBase:OnModifiableValueChanged` (`MultiResourceDepot.lua:225-240`), through `UpdateRequestCapacity` | the **Expanded Warehousing** upgrade, which doubles `max_storage_per_resource` (`upgrade1_mul_value_1 = 100`, `Data/BuildingTemplate/StationSmall.lua`, and likewise `StationBig`; tech `StationsStorage`) and then rewrites every resource from the dial, whatever the policy; MEASURED 2026-09-18 (§7.2 P3b) |
| `MultiResourceDepotBase:RecalculateAfterResourceListChange` (`MultiResourceDepot.lua:379-397`) | a storable resource is added, removed or unlocked (`:322`, `:376`, `:459`) |
| `SavegameFixups.RevertStationDesiredAmount` (`Station.lua:1744`) | once, on old saves |

### 4.6 ⛔ The alias trap

`MultiResourceDepot.lua:63` does
`RegisterResourceRequest = MultiResourceCubeVisuals.RegisterResourceRequest` — a reference
**captured at class-definition time**. Wrapping the declaring class later will **not**
affect the alias `Station` resolves through. Declaring class is
`MultiResourceCubeVisuals:RegisterResourceRequest` (`MultiResourceCubeVisuals.lua:372`).
This is the F64/F107 shape; `FIX_POLICY` §2 governs it and
`tools/harvest_wrap_targets.py --check` gates it via doccheck. Design around it.

### 4.7 UI direction (owner, 2026-09-18)

1.1.0's station infopanel is cleaner, and Module A must blend with it rather than add a section
of its own. The panel groups resources into collapsible **Basic / Advanced / Delicacies /
Other** headers, each carrying a `stored/max` total. Under each header, every resource is one row
with an icon button at the left and `stored/max` plus the resource glyph at the right. The
per-resource control belongs **in that row**, with the same visual weight as the existing
parts: a state the row already has room for, not a new panel. How it does that (the row's
button, a glyph beside the amount, or a ctrl-click the way the row's broadcast already works) is
open, and the prototype decides it.

**Capacity is not fixed.** Expanded Warehousing doubles the per-resource max (60 → 120 on a
`StationSmall`), and §4.5's upgrade path rewrites every resource's desired amounts when it lands.
Any floor or amount the module shows or stores must therefore be relative to the live
`GetMaxStorage(res)`, and the module must re-apply its values after that rewrite.

---

## 5 · Module B — train junction hub

### 5.1 What is closed, and what is not

**Closed: a junction on open track.** `TrackGridElement.connections` is capped at two —
`TrackElement.lua:333` (`if #self.connections > 1 then return end`) and `:355`
(`#el.connections < 2`). Every track hex is degree-≤2. You cannot draw a T or + with track.

**Not closed: a junction at a building.** Tracks terminate at buildings
(`GetStartStation` / `GetEndStation` / `GetDestStation`), and `TrackConnectedObjBase`
already exists as that abstraction with two shipping instances — `Station` (4 connectors,
`Station.lua:61-62`) and `TrackTunnelBase`. **The degree-2 cap never applied to buildings.**

⭐ **1.1.0 shipped the precedent.** `PassageHub` is new in 1.1.0 and solves exactly this
class of problem for passages, by star topology rather than by changing the grid —
`Lua/PassageHub.lua:50-55`:

> Connect the hub radially: every edge hex links (internally) only to the central hex,
> never to a neighbouring edge hex. […] so several passages on one small hub never create
> the overlapping edge↔edge connections that would leave asymmetric bits and assert when a
> passage is removed.

Its template says *"Passages must start and end at a Dome or a Passage Hub"* — a hub is a
**terminus**, not a branch. That is the shape a track hub would take.

### 5.2 What still blocks a *routing* junction

1. `Station:GetConnectedTrack` (`Station.lua:931`) is a choice function that does not
   choose — it pairs connectors by collinearity and `return "break"`s on the first match.
2. The route model is linear. `RebuildTrainRoutes` builds a path-or-loop array, one route
   per track segment, guarded by a literal `assert(not routes[connected_track])`. Every
   consumer does `table.find(route, station)` on that array.
3. Colonists are explicitly single-route: `RebuildTrainRoutes` clears `work_route` unless
   both stations are found in the **same** route.

### 5.3 ⭐ A useful hub does not need a routing graph

`PassageHub` is not a pathfinding graph either — it is a place where several connections
meet and join. The train equivalent is a building where multiple **straight-through lines
cross**, with cargo interchanging through its storage. Each connector pair remains its own
ordinary linear route, so **no route-model rewrite is required.**

A `Station` using all four connectors is two lines on two routes sharing one member, a 2-way
interchange with today's art and today's code. **Measured 2026-09-18 (§7.2 T2), one colony:**
cargo flows through it. On a large station the two lines are **parallel**, not crossing (owner
screenshot). A track straight through one line's two ends makes a single through-route, so each
route must use its own line. Six connectors would be three lines.

`Train:AssignToTrack` (`Train.lua:220-228`) is a clean existing primitive that moves a
train between tracks, should a later phase want route-switching.

### 5.4 Connector geometry does not require entity spots

Twelve sites read connector spots (`TrainTransport.lua:18,84,85,121,122,165,178,186`;
`Station.lua:446,620`; `TrackElement.lua:345`; `Tracks.lua:29`; `Train.lua:660`). Every one
does the same two steps:

    local conspot = self:GetSpotBeginIndex("Trackconnector" .. i)
    local dirspot = self:GetSpotBeginIndex("Trackdirection" .. i)
    local conpos = self:GetSpotPos(conspot)   -- which hex the connector occupies
    local dirpos = self:GetSpotPos(dirspot)   -- which way it points outward
    local q, r = WorldToHex(conpos)

**Two world positions per connector, immediately collapsed to hex coordinates.** There is
no mesh dependency in the track system; the spots merely store numbers that can be
computed. This is what makes a code-only hub plausible — see OPTION 3.

---

## 6 · Open questions, as options with a recommendation

Nothing in this section is settled. Each states the options considered and the one
recommended. ⛔ None is an owner ruling, except where one is marked: the 2026-09-18 ruling (§10)
settled 1b for the prototype, 3a and 5a first.

### OPTION 1 — Which module is built first

| | |
|---|---|
| **1a** | Module A (per-resource import/export) first |
| **1b** | Module B (junction hub) first |
| **1c** | Neither — park both until the seven surviving modules are re-verified on 1.1.0 |

⭐ **Recommended: 1a, phase A1 only.** It rides mechanism the developers already wrote and
already consume, needs no new assets, and its riskiest part (the export floor) is deferred
by construction. Module B's cheapest step is a *test*, not a build (§7.2), and that test
may change its scope — so B should not start first.
⚠️ **1c is the honest counter-argument and should not be dismissed:** nothing in this repo
is re-verified on 1.1.0, D01 is overtaken with OI-01 still open, and the shared TestKit
carries orphaned probes. Building new modules grows an untested set. That tension is the
owner's to resolve, not this spec's.

### OPTION 2 — Where module A stores its per-resource values

| | |
|---|---|
| **2a** | Write vanilla `transport_policy[res]` — already an ordinary `Station` member, already in the save format, so **no new persisted name is minted** |
| **2b** | Our own persisted field, fully owned |
| **2c** | 2a for direction + one new field for the per-resource amounts |

⭐ **Recommended: 2c.** Direction has a vanilla home that costs nothing and is already
consumed by live code; amounts have no vanilla home and need one field of our own.
⚠️ **Ban 1 applies:** any new field name is permanent from the first save that sees it.
Name it once, deliberately, at design time — not during the build.
⚠️ Risk accepted with 2a: if the developers later wire `transport_policy` up themselves, we
collide with them on a field we do not own.

### OPTION 3 — The hub's model ⛔ UNKNOWN, DELIBERATELY UNRESOLVED

The owner has left the hub's model open. The options, cheapest first:

| | |
|---|---|
| **3a** | **Copy nothing.** New building template with `entity = "PassageHub"`, referencing vanilla art by name as every template does. New Lua class off `TrackConnectedObjBase`. Connector positions **computed in Lua** rather than read from spots (§5.4). Palette swapped to the train family. **Pure code mod — no asset work at all** |
| **3b** | **New `.ent`, vanilla mesh.** Author our own entity XML with real `Trackconnector`/`Trackdirection` spots pointing at PassageHub's existing mesh file |
| **3c** | **Extract and ship the mesh.** Pull the mesh out of `Packs\Meshes.hpk` into the mod |
| **3d** | **Commission or author new art.** A purpose-built junction model |

⭐ **Recommended: 3a**, with 3b as the fallback if its one assumption fails.

**Why PassageHub is the right reference regardless of option.** Its radial hex footprint
was designed for exactly this job — edge hexes around a shared centre — which is the shape
a multi-connector junction needs. Its palette is `dome_base` / `mining_base` /
`pipes_metal` (`Data/BuildingTemplate/PassageHub.lua`), against `outside_TrainStation` on
both station templates and `train_track_base` on `TrackTunnel`. Palette is a template
string and is settable at runtime (`Building:SetPalette`, `Building.lua:736`), so
recolouring it into the train family costs nothing and uses the game's own colour language.
Vanilla track props can be attached at the connector hexes to reinforce the read.

⛔ **The assumption 3a rests on, untested:** that `GetSpotBeginIndex` / `GetSpotPos` can be
reliably overridden on a Lua class so all twelve call sites are covered — including
`TrackElement.lua:345` and `Train.lua:660`, which reach in from outside and would not be
covered by overriding the `TrackConnectedObjBase` methods alone. If that fails, the
fallback is overriding the six `TrackConnectedObjBase` methods and wrapping the two
external readers — messier, more `Require` pairs under F107, but bounded and enumerated.

⚠️ **3c redistributes Paradox art** rather than referencing it. Common in the scene, but a
posture decision the owner makes deliberately, not by default — and it is at odds with this
mod being a runtime patch.
⚠️ **Cosmetic cost of 3a/3b, accepted knowingly:** PassageHub's art shows passage
attachment points, not rails. Palette and attached props narrow the gap; it will read as
deliberate rather than bespoke.

### OPTION 4 — Asset posture, if any option needs an asset

| | |
|---|---|
| **4a** | Stay a pure runtime patch. Any option requiring a shipped asset is refused |
| **4b** | Allow assets in **this** mod, ending "no game files are modified" as its identity |
| **4c** | Allow assets, but in a **separate** mod, keeping this one pure |

⭐ **Recommended: 4a for now, 4c if 3a and 3b both fail.** The mod's standalone,
no-files-modified identity is load-bearing in its own description and is not worth spending
on a first version. 4c preserves it while leaving a route open.

**Owner ruling, 2026-09-18 (OI-16): 4b.** The hub asset ships in this mod. The owner's reasoning:
the module is opt-in, so an asset is fine. The case for 4b over 4c: a second mod can be
unsubscribed while a save still holds hubs, and that leaves hubs without their model. Its
costs: the description drops "code only"; the building stays out of the build menu while the
module is off; and the packaging checks must admit an entity folder.

### OPTION 5 — How module B is scoped

| | |
|---|---|
| **5a** | Interchange only — multiple straight-through lines crossing at one building, cargo transferring through its storage. No route-model change |
| **5b** | 5a plus colonist interchange — a two-hop `work_route` through a shared station |
| **5c** | Full route-switching — trains driving through the junction. Requires a graph layer |
| **5d** | Cargo routing, not train routing — every hub-to-hub segment stays its own linear route with its own trains, and a routing layer sends each load toward the hub next on the path to where it is wanted (per-hop forwarding in `TransferCargo`, through the dead `ttPrioShortage` lane, §3/§4.4). No route-model change |

⭐ **Recommended: 5a first, then reassess.** It is the `PassageHub` pattern applied
faithfully and it needs no graph. 5b is the most defensible *feature* of the three — the
single-route restriction on colonists is a real, verifiable gap — but it should follow 5a.
5c is large and grows; hold it in reserve.

**Owner direction, 2026-09-18:** the hub is for **player usability and routing**. The target is
a network like the owner's diagram: six hubs, four around a loop and two on a spur, with end
stations hanging off them, and every hub meeting three or four lines. Read against that target:

- **It fits the track rules.** Branches happen only at hubs, never on open track (§5.1).
- **Vanilla cannot build it.** A station hub carries two routes, one per line (§7.2 T2), and these
  hubs need three or four. That is the more-than-four-connector hub (§10), 6–8 connectors each.
- **5a** makes it buildable, and cargo then spreads hop by hop to capacity shares across the
  whole network (§7.2 T2). But nothing is *sent* from A to F, every hub holds stock, every
  segment needs its own train, and colonists cannot cross a hub.
- **5d** adds the "routing" to 5a without touching the route model: loads move toward where
  they are wanted. It is a scheduler change, the spec's deepest patch exposure (§4.4 Reserve).
- **5c** is literal trains running A → H1 → H3 → H4 → C. It needs the route model rewritten
  (§5.2's three blockers), pathfinding over a graph with a loop, and reservation at hubs so
  trains on shared segments do not deadlock. It is the largest option by far.

INFERRED sequencing, not a ruling: 5a with the more-than-four-connector hub is step 1 for every
variant, so the §10 prototype stays the first build. 5d or 5c is chosen after that network has
been played.

---

## 7 · Falsifiers — what must be tested before any of this is believed

Every claim in this spec is desk-read. These are the checks that would prove it wrong, in
the order they should be run. **T1–T3 and P3b RAN 2026-09-18** (§7.2); T4 and items 5–7 have
not, and stay `<<PENDING-RUN>>`.

**Correction, 2026-09-18.** Item 1 below used to say that disabling a resource tests the
`transport_policy` export branch. It does not. A disabled resource is evacuated by
`TransferCargo`'s *forbidden* branch (`Train.lua:873`, `:910-941`, priority `ttPrioForbidden`),
whatever `transport_policy` says. Test T3 is the one that exercises the policy.

**Common setup for T1–T4.** Use a **disposable save**, never a campaign save: a campaign copy
still runs its autosave rotation (`EF-055`/`EF-056`), and T3 writes the vanilla
`transport_policy` field into whatever save it runs on. Cheats are fine (`WORKFLOW.md`, cheats on
playtest saves). Place the stations far enough apart that drones and shuttles cannot carry
between them, or they will fake a pass on T1 and T2. The owner runs these in the game
(owner, 2026-09-18). Every console line below is `<<PENDING-RUN>>`: it has not been run, and it
needs `[RAN <date>, log <name>]` (`WORKFLOW.md`) before it goes into any human doc.

1. **T1: does "export everything" already exist?** Two stations X and Y on one track with a
   train. Stock Metals at X, then switch Metals off at X in its per-resource row.
   *Pass:* trains carry X's Metals to Y. That is export with a floor of zero, already shipping
   in vanilla, which narrows Module A's new work to the non-zero floor. Also note whether
   drones stop delivering Metals to X. *Fail:* the forbidden branch does not behave as read;
   re-read `Train.lua:903-944` before designing further.
2. **T2: does station interchange already work?** Station H with track on **both** connector
   pairs, forming route A (X–H–Y) and route B (P–H–Q). Put Metals only at X, with Metals
   enabled everywhere. *Pass:* Metals reach P or Q, which only route B serves, so they must
   have passed through H. That is a working 2-way interchange in vanilla, and Module B's first
   question narrows to "more connectors". *Record either way:* do H's two connector pairs make a
   cross or two parallel through-lines? The pairing is `(1,2)`/`(3,4)` (`Station.lua:620`), but
   the geometry comes from the entity art. **Seen 2026-09-18 (owner screenshot, top-down, large
   station, no DUMP):** two **parallel** through-lines, each with its own rail and two end
   connectors. A track through one line's two ends makes one through-route (the owner's X–H–P
   read `3/3` everywhere), so a hub needs the second route on the **other** line. *Fail:* Module B needs more
   than interchange, so re-scope OPTION 5 before any prototype.
3. **T3: does the dead `transport_policy` work when driven by hand?** This tests Module A's
   mechanism with no mod code. Select a station holding Metals, then type these into the
   in-game Lua console one line at a time. Reads are bare expressions and writes run under
   `*r`, following the house console form (`prompt-authoring`). `SelectedObj` is open in the mod
   sandbox (`EF-096`); `const` is not on that fact's checked list, so if the first line fails,
   that is why.

        const.ResourceScale
        *r SelectedObj:ToggleTransportResource("Metals")
        SelectedObj:GetTrainTransportPolicy("Metals")
        *r SelectedObj:SetDesiredAmount(SelectedObj.desired_amount + const.ResourceScale)

   `[NEVER RUN]` as typed lines: slot 5 made the same calls (§7.1), `[RAN 2026-09-18, log
   train_tests_Mars.exe-20260918-12.27.51]`.

   The first toggle moves the policy from `"default"` to `"send"`, and the third line should
   then read `send`. The fourth line is required: `ToggleTransportResource` only writes the policy, and
   `SetDesiredAmount` returns early on an unchanged value (`Station.lua:964-965`), so it must be
   called with a different value to re-apply. `SelectedObj` is set in
   `CommonLua/Selection.lua:17`. Toggle a second time to reach `"accept"`, then re-apply.
   *Pass:* on `"send"`, drones fill Metals toward max and stop taking from it; on `"accept"`,
   drones drain it to zero. Watch the trains too: they read supply desired as a route-wide gate
   (§3), so no direct directional change is expected. *Clobber check:* click the station's
   per-resource row once. `SetAcceptResourceState` rewrites desired amounts from
   `self.desired_amount` and ignores the policy (`:1038-1045`), so the policy effect should
   vanish. Seeing that confirms §4.5's second path.
4. **T4 (optional): does the station-wide dial still bite?** With the policy at `"default"`, run
   `*r SelectedObj:SetDesiredAmount(20 * const.ResourceScale)` `[NEVER RUN]` with a few multipliers and compare
   drone filling against
   a second station. This only matters to the parity-restore route, which §2 recommends against.
5. **What breaks when `GetMaxStorage(res)` stops being uniform?** It also drives visual cube
   columns, `GetEmptyStorage` (`MultiResourceCubeVisuals.lua:506`) and load caps — so
   overriding it changes *real* capacity, not only a balance weight.
6. **Can native `CObject` methods be overridden on a Lua class?** The assumption under
   OPTION 3a. A hello-world test settles it without any design commitment.
7. **Paradox patch notes / dev diaries** on the 1.1.0 station change — external, not checked.
   Would settle §1's intent inference.

### 7.1 The SMRTK sitting for T1–T4 (predictions written before boot, 2026-09-18)

The slots are preloaded in the TestKit's `Code/80_AgentSlots.lua` (owner ruling 2026-09-18,
that file only), on TestKit `382c667` plus that rewrite and pack `56a77e8`. Every leaf was read on
1.1.0.403908 (`C:\Dev\SMR-SrcArchive\1.1.0.403908\Src`). Each press is MARK → act → DUMP → MARK
in the log, so a slot replaces the typed T3 console lines above. Those lines stay as the fallback.
The slots are **1** Read stations + trains (read-only, every `Station` and `Train` on the map);
**2** Setup: +20 Metals here; **3** Setup: clear Metals here; **4** Act: click Metals row
(`ToggleAcceptResource`, what the row calls, `sectionStorageRow.lua:42`); **5** Act: policy step
+ reapply; **6** Run: 2 arrivals here (the watch); and **Scratch** Boot status (console, taint,
eligibility). T4 has no slot. It uses item 4's console line.
Pin X as A, H as B and P as C, so the DUMP lines tag them.

**Procedure correction.** T3's clobber check needs **two** row clicks, not one. From enabled, a
click takes `SetAcceptResourceState`'s `"disabled"` branch, which only suspends the request
(`Station.lua:1046-1050`). The `"store"` branch that rewrites both desired amounts from the dial
(`:1034-1039`) is the second click.

Predictions. `sdes` is the supply request's desired amount, `ddes` the demand's, and `max` is
`GetMaxStorageForAnyOneResource`. Every figure comes from slot 1's DUMP.

**The watch unit is train arrivals, not human timing** (owner, 2026-09-18). Slot 6 arms a
read-only Run trigger on the selected **end** station (X or P, never H) together with
`run_until`, which runs the game fast and pauses when the trigger fires. Every 500 game-ms it
polls every train and logs each arrival (`at_station` false → true, `Station.lua:1119`) and
departure (true → false, `Train.lua:358`), with game-ms since arming and the Metals carried. It
fires on the **second arrival at that station**, which is two round trips of a two-station
route. The fired record also carries the pinned stations' state lines. One press is one
window. Abort after three presses with no movement. Drones cannot be watched at that speed, so
the drone half of T1 and T3 is read from `stored` in the DUMP.

- **P0 (first screen):** the log carries `SMRTK_SLOTS sitting=train_tests_20260918`, and
  Scratch returns `taint` and `eligibility` read as separate dispatches.
- **Fixture (owner, 2026-09-18):** the owner's colony has a regular station connected to a
  large one. That pair is route A: X is the regular station and H the large one, so T1's Y is H.
  One new regular station P, on H's **other** track pair, makes route B, and T2 needs no Q.
  Every station has track points 1–4 (`Station.lua:61-62`, no template override). The regular
  station holds 60 per resource and the large one 120 (`StationBig.lua:33`), and Expanded
  Warehousing doubles both. ⛔ **Balancing alone moves Metals.** Trains share a resource by
  capacity (§3), so with Metals enabled X settles near its capacity share: about ⅓ of the
  total on a two-station X–H route, and about ¼ on the owner's as-built X–H–P through-route
  (60 / (60+120+60)), with nothing upgraded. T1 therefore runs a **control phase first**:
  X stocked, Metals enabled, two watch windows, the settled share read.
- **Route check before the base save.** A route is a linear chain. A train continues through a
  station only when the next track leaves from the connector directly opposite the one it came in
  on (`Station.lua:931-960`, used by `EnumRouteTracks`, `TrainTransport.lua:251-300`). The
  Trains rollover's cap counts each distinct station **once** across all of a station's
  routes: `GetTrainsOnRoute` shares one `seen` table, and a route left with fewer than two unseen
  stations adds 0 (`TrainTransport.lua:492-536`). So separate A and B read `…/2` at X, H and P,
  and one through-route reads `…/3` everywhere, in which case T2 tests nothing. Corrected
  2026-09-18: this line first predicted `…/4` at H. The owner's H read `3/3`, and they pointed
  out that a fourth station would be needed. Slot 1 now also DUMPs every route's station path,
  which settles the question from the log.
- **P1 (T1, slot 4 on X, after the control):** `en=false`, `pol=send` (`Station.lua:1079-1081`).
  X's `stored` then goes to **zero**, below its settled share, which is the forbidden branch
  and not balancing. H gains the difference plus or minus `in_trains`, and `colony_total` does
  not change. No drone delivers Metals to X.
- **P2 (T2, slot 3 on H and P, slot 2 on X):** P's `stored > 0` within the window. Only route B
  serves P. The cross-or-parallel layout of H's connectors is a screenshot, not a DUMP.
- **P3 (T3, slot 5 on a station on `default`):** the 1st press gives `pol=send sdes=max ddes=0`,
  the 2nd `pol=accept sdes=0 ddes=max`, and the 3rd `pol=default sdes=dial ddes=max−dial`
  (`Station.lua:964-994`). Behaviour is as in item 3. **Clobber:** slot 4 twice leaves `raw`
  unchanged but resets `sdes=dial ddes=max−dial`.
- **P3b (upgrade clobber, T3 continued):** on a station that is **not yet upgraded**, set the
  policy to `send` with slot 5, then apply Expanded Warehousing with the Selected page's
  **Upgrade 1**. Predicted: `max` doubles, and `sdes=dial ddes=max−dial` returns while `raw`
  stays `send` (`MultiResourceDepot.lua:217-240`). This is §4.5's upgrade path.
- **P4 (T4, console, optional):** after item 4's `SetDesiredAmount`, `sdes=dial ddes=max−dial`.

Stop on unexpected taint, a Lua error, or a DUMP read of `read=FAILED`. Do not rerun a test to get
a preferred verdict.

### 7.2 Results, 2026-09-18 (MEASURED; one colony; tests of vanilla behaviour)

Log `docs/archive/train_tests_Mars.exe-20260918-12.27.51-6a91a190.log`, retail 1.1.0.403908, save `train1` at sol 71, 0 Lua errors in 2,888 lines. The
standing rig had both mods and the TestKit loaded. Neither mod touches trains, so the rig
does not intersect these tests. Ids are the log's `id=`. **Fixture:** X =
`StationSmall(2360)`, H = `StationBig(2281)` and P = `StationSmall(2843)`, none upgraded.
Route A is X > H on one of H's two parallel lines and route B is P > H on the other (slot 1
route DUMP, ids 68–69), with two trains each. X is inside a drone controller's range; P is
outside every one (the game's "Too far from working Drone controller"). Station distance was
not measured. Base save: Metals 0 at all three stations.

- **T1: PASS** (ids 300–476). Control on `default`: X 15, H 30, P 15, holding across two
  windows. Then Metals was switched off at X. The act was the owner's hand click on the row,
  not slot 4, so the act itself is unlogged; the reads either side show `en` on (id 344) and
  then off with `pol=send` (id 355). In the next window X went to **0**: train
  `2000000933` carried 11 to H, and drones took 4 to a depot (the stations lost 4 while
  `colony_total` held at 556). X stayed at 0 for about two sols with no drone deliveries
  back (ids 401, 467). ⇒ Vanilla already exports down to zero, and Module A's new work is
  the non-zero floor (§4.3).
- **T2: PASS** (ids 225–283). Seen during T1's control phase, which was T2's exact setup:
  Metals only at X, enabled everywhere. Train `2000002696` on route B carried 10 from H to P,
  which only route B serves, and P went 0 → 14. ⇒ A large station whose two lines carry two
  routes is a working two-way interchange in vanilla, in this colony. **Also measured:**
  balancing composes across the interchange to network-wide capacity shares. X : H : P
  settled at 14 : 29 : 14 = ¼ : ½ : ¼ of 60 : 120 : 60 (ids 267–269).
- **T3 acts: all as predicted** (ids 582, 641, 718, 749). The toggle alone changes no
  request amount (`after_toggle`), and the re-apply is what sets them.
- **T3 `send`: PASS** (ids 597–633). X filled to max (60) within one window. Over two windows
  trains carried 127 out of it, and the stations' total rose 40 → 143 as drones fed X from the
  depots. ⇒ `send` makes a station a drone-fed export pump. T1's `default` control is the
  contrast: the stations' total never moved off 60.
- **T3 `accept`: NOT CONFIRMED in this fixture.** In the clean leg (ids 1013–1142), set with
  no game time on `send`, X went 40 → 4 → 10 → 10. The stations' total held at 40 and
  `colony_total` at 536, so drones did nothing either way, and X sat at its capacity share.
  INFERRED: drones haul only toward a demand, and nothing in X's drone range wants Metals.
  This fixture cannot discriminate. The first `accept` window (ids 641–707) followed `send`
  and is confounded by deliveries still in flight.
- **Clobber: CONFIRMED** (ids 749–791). On `send` (`sdes=60 ddes=0`), the 1st row click
  disabled Metals and left the amounts alone. The 2nd click rewrote them to `sdes=14 ddes=46`
  (dial, and max minus dial) while `raw=send` stayed. §4.5 row 2.
- **P3b upgrade: CONFIRMED** (ids 867–914). On `send`, Expanded Warehousing took `max` 60 → 120
  and reset to `sdes=11 ddes=109` (dial, and max minus dial) with `raw=send` kept. §4.5 row 4.

The slot DUMP printed `en=unavailable` for a disabled resource. That was an and/or slip in the
slot code, and `pol=send` beside it confirms the resource was off.

---

## 8 · Binding constraints for whoever builds this

- **Both modules are NEW.** The owner lifted MODULE FREEZE on every module on 2026-09-18
  (`CLAUDE.md`). A behaviour still needs an owner ruling recorded for this mod, and §10 holds
  Module B's.
- ⛔ **Ban 1** — a new persisted field name is permanent from the first save that sees it.
- ⛔ **Ban 2** — zero `SMRFixPack` references in executable code.
- **F107** — every `(class, method)` pair installed on or captured from must appear in the
  module's own `Require` block; `tools/harvest_wrap_targets.py --check` gates it.
- **F64** — self-check on the **declaring** class, not the subclass. See §4.6.
- **F87** — `apply()` runs at the menu with classes not yet built and presets already
  loaded. An XDef-generated class override must install after flattening and survive an
  in-place `ReloadLua`.
- **F110** — no per-game runtime global in a `Require` block.
- **FIX_POLICY §8** — the both-configuration ship test is owed at ship for every module.
- ⚠️ The shared TestKit follows the fix pack's permissions (`tools/TESTKIT.md`, `tools/SMRTK.md`)
  and already carries orphaned probes from the 09-17 retirement.

---

## 9 · The asset pipeline, as read on disk 2026-09-17

Read from the installed game, not the source archive. The install path is volatile, so
re-read it with a command (Steam's `libraryfolders.vdf` lists libraries on C:, A: and B:). On
2026-09-17 the game was at `A:\SteamLibrary\steamapps\common\Surviving Mars`. This section
supports OPTION 3 and OPTION 4.

**ModTools contents.** `BlenderExport.py` (1423 lines), `HGBlenderExporter.zip`,
`AssetsProcessor\AssetsProcessor.exe`, `hgimgcvt.exe`, `Docs\ModItemEntity.md.html` (the
entity authoring doc), and two worked samples: `Samples\Mods\Cemetery\` (a complete building
mod) and `Samples\Assets\ModTerrainIcon\ExportedEntities\`.

**What an export produces:**

| File | Format | Holds |
|---|---|---|
| `.ent` | XML, text | spots, surfaces, bounds, and the mesh and material file names |
| `.mtl` | XML, text | texture and material bindings |
| `.m.hgm` | **binary**, header magic `hsmh`, version 4, undocumented | the visible mesh |
| `.dds` | binary | textures |
| `.map`, `.md5` | text | texture id mapping |

**Spots and surfaces are text in the `.ent`**, as in `Samples\Mods\Cemetery\Entities\Cemetery.ent`:

    <attach name="Top" spot_pos="-4,561,937"/>
    <attach name="Workdrone" spot_pos="-404,1502,0" spot_rot="-0.000000,0.000000,-0.704864,89.6371"/>
    <surf type="hex_shape" points="-582,861,0;716,874,0;-77,-79,0"/>
    <surf type="collision" points="829,570,107;1000,866,0;829,570,0"/>
    <surf_hash type="collision" value="1739606373"/>

`spot_rot` is `axis·sin(θ/2)` followed by `θ` in degrees. This was checked against three sample
values: `0,0,0.5,60` → sin 30° = 0.5; `0,0,-0.707107,90` → sin 45°; `0,0,0.999905,178.4237` →
sin 89.2°. In Blender, spots are Empty objects whose names start with `-`; `Origin`,
`hex_shape`, `Selection` and `Collision` are named objects (`ModItemEntity.md.html`).
`_EntityData.generated.lua` holds editor metadata only, with no spots. PassageHub's entry is at
`:16336`, and its template sets `entity = "PassageHub"`, `object_class = "PassageHubBase"`.

**Environment on 2026-09-17:** Blender is not installed (`C:\Program Files\Blender Foundation`
is absent); Python 3.13.5 is.

**Capability, as judged on 2026-09-17: inference, not tested.** An agent can author the text
side reliably: `.ent` spots and surfaces computed from hex math, `.mtl`, templates and Lua. It
cannot reliably edit or produce `.m.hgm` or texture art. A third route sits between those two:
if Blender were installed, generating simple parametric geometry by `bpy` script and exporting
headless with the shipped exporter looks feasible. That is programming, not modelling, and it
has not been tried. A capability comparison with Codex was drafted for the owner to run. Its
discriminating questions are scripted Blender and whether a mod can reference a packed mesh.

**Relaunched correction, read 2026-09-18.** Everything above describes the classic install. The
game the owner plays is Relaunched, at `A:\SteamLibrary\steamapps\common\Project Spark`.
- Its packs are `.fpk`, which `tools/flpk_extract.py` reads.
- Its meshes are `.hgrm`.
- Its `ModTools\Docs\ModItemEntity.md.html` imports **FBX from Blender** through the Mod
  Editor's ArtSpec item.
- The station textures are `Station_*`. The passage hub body uses `NewDomes_*` and its glass
  `DomeGlass_*` (`Materials.fpk`).
- The spot and footprint data sit in the binary `BinAssets.fpk:entities.dat`, which has not
  been decoded.
- Reference images and the asset's layout requirements for the owner are outside both repos,
  at `C:\Dev\SMR-Assets\trainhub\reference\` (game art, local only).

**The owner's asset: shape approved by the owner 2026-09-18 (OI-15 = six, OI-16 = 4b).** The
owner, after the rebuild: "I actually think that turned out perfect", and the rest waits on the
game. The concept art was iterated with an image AI and meshed in Tripo (Smart Mesh, quad
topology, about 15,000 polygons, untextured, FBX with the Blender preset). Its output is
`C:\Dev\SMR-Optin-Assets\circular industrial platform 3d model.fbx`: binary FBX 7400, 15,229
vertices and 281 loose parts. The Blender 5.2 pipeline lives outside both repos in
`C:\Dev\SMR-Assets\trainhub\blender\`, and its `README.md` gives the steps:
- `hub_skeleton.py` builds everything that must be exact: `Origin`, the `hex_shape` footprint
  (61 hexes, 4 hexes of radius) and the free ring beyond it, `Collision`, `Selection`, three beams
  60° apart, every pillar with its foot on the ground, the platforms on posts, the ring wall as a
  true circle with a glazing channel, the glass dome seated in that channel, a hood joining the
  glass to each portal, the ribs and their clamps, six storage beds on the ground, and the spots
  `-Trackconnector1..6`, `-Trackdirection1..6`, `-Box1..6`, `-Top` and `-WorkDrone1..6`.
- `tripo_cleanup.py` takes one piece from Tripo, the portal on +X with its collar, clamp and stub
  pylon. It copies that piece to all six positions and deletes the rest.
- `build_workfile.py` runs the chain and saves `TrainHub_work.blend`; `render_previews.py` writes
  eight preview renders.

**Why only the portal comes from Tripo (measured 2026-09-18, mesh scaled to 90 m end to end).**
Its portals stand at 0°, 55.5° and 123°, and no two are the same size. Its ring is 0.7 m out of
round, its supports float 0.4 to 1.6 m above the ground, and its pallet decks are tilted.
- The ring's cross-section was read off Tripo's ring beside the good portal. It runs 31.65 to
  35.6 m out, and its channel floor is at 8.4 m.
- The dome's rim is at 32.95 m, and its apex at 20 m.
- `DECK_Z` is 8 m. All six portals measure centred on their beams to the millimetre.
- **The storage beds are on the ground** because the build stacks cubes ten high (`max_z` 10,
  `TRAIN_HUB_BUILD_20260918.md`); from the Tripo decks 6 m up, the stacks would reach the glass.
  Each bed takes the 12 × 5 grid. Its `-Box` spot is the centre of the first cube, with columns
  along the spot's +X and rows along its +Y, as `GetCubePosRelative` reads it.

**Imported 2026-09-19** (owner, Mod Editor, into the dev mod; `export_prep.py` makes the FBX).
- **The axis mapping, MEASURED:** the importer maps Blender (x, y) m to game (−y, −x) × 100.
  This was read from the first import's `Entities/SMROptInTrainHub6.entjson`. It put the lines
  at 30°, 90° and 150°, 30° off the game's hex rows, which run along world X (`MapGrids.lua:67`).
  `export_prep.py` turns the model 30° (`TURN_DEG`). On the re-import, the six connectors read
  0°, 60°, … 300° at 4,000 units and z 800, and all 61 footprint hexes fall on the lattice. The
  lattice check found 60 of 61 off for the unturned model.
- **What the importer needs:** Origin > one mesh > spots and surfaces; **one material per mesh**
  ("Contains multi-materials. Not supported yet."); spots that share a name via `.001`
  suffixes. The entity file is written only when the Art Spec is saved
  (`ArtSpecEditor.lua:1006-1028`), so saving comes before a successful import.

**Owner direction for the look, 2026-09-19:** the vanilla station's colour scheme (clean white
and red, the hex-pattern floor), but *"more clean / modern / high tech"*; **not** the brushed
metal or the slatted look of the station's older parts. No colonist entrances and no station
building: *"its meant to be a hub not a true station"*. Owner, same day: it must not block
colonists who use it as a station, but without the door look. INFERRED from source, not run: no
door is needed. A station boards passengers through the domes whose entrances lie within its
outside-work radius (`Station.lua:320-337`, `LinkToStation`), and the hub's drones work from its
`WorkDrone` spots and never enter. The next smoke test checks a dome in range. **No decorative
door either** (owner, 2026-09-19: *"we can always revisit later as a v2"*). The charger stays the game's own pad,
placed by the code (no charger spot in the model).

**The look: our own Blender textures (owner, 2026-09-19: Tripo texturing dropped).** The untextured import
used `Default`; the textured model is UV-unwrapped and baked by `export_prep.py` calling `texture_hub.py`.
- **Vanilla material: ruled out as a pick.** The Importer's Material dropdown lists only
  `Default` and mod materials (owner, 2026-09-19). The station's material is `TrainStationBig_T1`
  (atlas `Station_BC.dds`, colorization `Station_CM.dds`, 3 colours, in `Materials.fpk` /
  `Textures3.fpk`). Patching its path into the entjson after import probably resolves, since
  `Materials/Default.mtljson` is itself a game path. But every re-import overwrites the patch,
  and the atlas carries the aged look the owner rejected. Fallback only.
- **Chosen: procedural textures, made in Blender.** `texture_hub.py` bakes white enamel, red trim rings,
  a light-grey hex floor with relief and slate-blue pads into three 4096² uncompressed TGAs in
  `C:\Dev\SMR-Assets\trainhub\blender\textures\`: `TrainHub_BC` (sRGB base colour), `TrainHub_NM`
  (tangent-space normal) and `TrainHub_RM` (roughness R/G, metal B). The body is one mesh with one
  material, as the importer requires (`SceneImport.lua:3548`, `:4023`); no colorization mask was
  made, so the colours are fixed. **Size, MEASURED 2026-09-19:** the imported DDS come to 44 MB
  (43 MB of it textures), against `PACK_MAX_BYTES = 5 MB` at `upload_preflight.py:47`. The maps are
  baked by `texture_hub.py`, so re-baking at 2048 lands near 11 MB and at 1024 near 2.7 MB; whether
  the hub still reads right at those is a look-pass judgement and is untested.

  **The 5 MB is OUR OWN GUARD, not a platform limit** (MEASURED 2026-09-20; an earlier draft of this
  passage said the hub "cannot ship at this resolution whatever OI-18 rules", which overstated it).
  `upload_preflight.py:44-47`'s own comment gives its reason — the shipped pack is about 0.6 MB and
  the constant exists to catch a pack "carrying something that is not the mod". Read-only decode of
  the installed packs (build `24995074`; `flpk_extract.py` + DDS headers; `TrainStationLargeCCP3`
  decodes at 89.94 x 90.95 m, confirming 100 units = 1 m):

  - **Vanilla's own resolution is 2048.** Of 5087 texture DDS, 3024 are 2048² and only 55 are 4096²
    — wonders, terrain, decals, and one building exception, `StationBig T1_DM`. Every ordinary
    building checked (MachinePartsFactory, DomeMediumConstruction, ApartmentsCP3, PassageHub) is
    2048². The train station binds `Station_BC/CM/NM/RM/EM` at 2048² plus that 4096² DM.
  - **Our three maps are 4096², above vanilla's norm**, at 44.7 MB raw: BC1_SRGB 11.18 MB, BC5
    22.37 MB, BC1 11.18 MB. The **format** choices match vanilla exactly; only resolution differs.
  - **Packs are zstd-compressed**, so raw size is not shipped size: vanilla stores `Station_BC` at
    418 KB against 2.80 MB raw. Our three compress to **4.52 MB** (deflate-6) or **3.31 MB**
    (zstd-19) — the maps are largely flat procedural surfaces.
  - **The importer picks the DDS format and does not resize** (`GFXMaterial:ImportMap`,
    `CommonLua/Libs/DevToolsPublic/GFXMaterial.lua:1098`, `:1101-1139`, called from
    `SceneImport.lua:1922`): BC1 sRGB for BaseColor, BC5 for Normal, BC1 for RM. Source resolution
    is the modder's choice; output size follows it.
  - **Steam accepts far larger Surviving Mars mods** (owner, 2026-09-20): the Red Horizon Buildings
    & Techs Pack listing shows 103.5 MB, about 2.4x our unpacked hub.

  **Not determined:** whether the shipped mod is compressed in transit; any Paradox Mods or Steam
  Workshop total-size cap; whether the hub maps were authored at 4096 or upscaled; and the VRAM or
  performance cost of 4096 against 2048. A test pack built from the dev mod would settle the first,
  and nothing packed has ever been loaded (OI-18). Checked 2026-09-19 by the orchestrator: geometry exactly equal to the
  untextured baseline, 0 zero-UV faces, the previews match the look direction. The owner's steps
  (a GFXMaterial item, the three maps, the Material choice on the body mesh, re-import) are in that folder's
  `README.md`; they ride build 3's footprint fix so one re-import carries both.
  Not checked: the look in game, the Mod Editor steps run, the normal map's handedness. Blender
  renders a black patch at the central beam crossing even with every map disconnected: a geometry
  question, to be compared in the game view.
- **In game, the textured import (owner, 2026-09-19 evening):** the white and red and the hex tiles read.
  Three things owed, as one look pass and one re-import: (1) **night lighting like the vanilla
  station**: light spots (`-L;` names, ModItemEntity "Metadata in Scenes"); the vanilla station's
  night look is pole lights pooling on its floor and the ground. A glow map for the red trim (the
  GFXMaterial has an `SI` slot) is the orchestrator's option, not ruled; (2) **the glass**, out of the export while
  `INCLUDE_GLASS = False` because the default material is opaque; it needs its own mesh and a blended
  material, untested; (3) **the stub looks nothing like the vanilla track**: it is a slab with a hex
  top where vanilla is a narrow deck with side rails. **MEASURED, build 3's smoke, 2026-09-19:
  there is no height error.** The probe reads the vanilla element's own `Enter1` spot, so the
  comparison is the game's train level against ours: all six read `stub=10800:running=10800`,
  exactly equal (`Mars.exe-20260919-20.33.45`, slot 1 `track_height_rows`). The owner's
  2026-09-19 "the fault is the asset's" was by eye and holds only for the **width**: the vanilla
  element measures `bbox_xy=1000x204`, so 2.04 m across (10 m along, one hex), against our 3.5 m
  `BEAM_W` — about 1.7 times. The restyle therefore narrows the stub and gives it vanilla's side
  rails; it does not move it vertically. The bbox covers the whole `TrackPillarCCP3` entity,
  pillar included, so 2.04 m is an upper bound on the visible deck's width. **Owner, same evening:** keep our red; the stub carries a **red centre
  stripe where the vanilla track has its blue one**, so the hand-over from hub to vanilla track
  is visible (vanilla's blue strip is dark conveyor segments between white rails; it does not
  glow, and the blue dots seen on a selected station are its selection outline). **Floor (owner, same evening):**
  a floor plate under the ring interior, modelled on the vanilla station's platform (near-white,
  faint hex relief, a dark trim border, a coloured edge strip). The hex pattern moves onto it, off
  the beams and the stub. Colour adjustments are fine, but never so dark that the slate storage
  plates blend in. No collider on the plate; the cargo beds rise by its thickness.
  **Lights and pillars (owner, same evening):** the night lighting is a flood light facing down into
  the hub from the top, where the dome ribs meet, plus subtle lighting around the six tunnel
  entrances. The pillars are thinned: cut the inner ring of six (10 m out on each line, set by
  `PILLAR_AT` in `hub_skeleton.py`) and keep the centre pillar, the middle ring (20 m) and the outer
  ring supports, so the hub reads open and less cluttered.

**Unverified:**
- the vanilla track deck height, which the stub ends must match (the spots sit at z 800);
- the textured look in game, and whether the crossing's black patch shows (see the look paragraph above);

**Cargo grid, MEASURED 2026-09-19 (console dump of one filled hub, then confirmed by the owner in game).**
The importer writes a Blender spot's `rot_z` as the game angle `330 - rot_z`; the hub's
`GetCubePosRelative` lays a bed's columns along that angle and its rows 90 degrees on. Spot positions
map exactly (`(x, y)` Blender m to `(-y, -x)` x 100 after the 30 degree turn). So each `-Box` spot
is turned 90 degrees from its bed's long axis and starts on the bed's inner long edge; under that
rule all 60 cubes of a bed land on it. A bed holds 12 x 5 = 60 columns, as a vanilla depot does
(`Station.lua:99-100`); layers are 1.01 m, so 9 layers is about 9.1 m.

**Lessons:**
- Image AIs and Tripo do not hold three lines exactly 60° apart, so build the geometry in the
  Blender skeleton and use Tripo for pieces only.
- FBX is loaded with File → Import, not File → Open.

**Unknowns this pipeline leaves open, each decisive for OPTION 3:**
- Can a mod's `.ent` reference a mesh that exists only inside `Packs\Meshes.hpk`? This decides
  whether 3b is possible.
- What does `<surf_hash>` gate? If it is an integrity check, hand-edited surfaces may be
  rejected.
- Can a Lua class override native `CObject` spot methods? This is §7 item 6, and 3a depends
  on it.


**Deck under the lanes (owner direction, 2026-09-20, from build 3b's sitting; a candidate, not
briefed).** By eye, with a train parked at 13 m: trains ride 289 units off the connector centreline
(`lane_offset`, `20_TrainHub.lua:171`, read from the vanilla element's own `Enter1`/`Enter2`), but
the hub's hex deck and stub sit on the centreline, so the train hangs mostly off the strip. At the
portal the deck ends square beside the first vanilla element and the two never join. The owner's
direction: build a deck **on either side of the stub**, one under each lane, matching the transition
of the train coming off the vanilla track onto ours, so the hand-over reads as intended. **The
owner's constraint:** the stub is too short for a whole train to be on it before it enters the
tunnel. **The owner then measured it with the build cursor (2026-09-20): the stub is exactly one hex,
and the direction is to bring the stubs out exactly one more hex, two in all, matching a train of
about two hexes.** This overrides the earlier "not proposed: lengthening the stub" reasoning, which
took a longer stub for the withdrawn `FOOTPRINT_R = 5` family; the withdrawal rested on the disputed
41.5 m, this rests on the owner's measurement. The mechanism as read from the code, not run: the hub
takes each line's radius from the model's own outline (`line_radii`, `20_TrainHub.lua:115`) and a
connector must be the last footprint hex on its line (`Tracks.lua:19-24`), so the change is six
more outline hexes, one per line, and connectors moved out by one hex, then re-imported with the
lane decks. `Floor.HubParkDistance` is a distance from the hub's centre, so the 13 m does not move
with it. What it costs, for the look-pass brief to price: the Mod Editor re-import, the ramp spots (5/7 of the radius) and the oracle's
tables and the desktop traffic check re-run at the new radius, and the fixture saves. On
`train_hub_base`, `train_hub_base_agent` and `SpaceY Sol 21` the six laid tracks end at today's
connectors, so each line's end element must be shortened by a hex, and a hub already built at the
old radius (`SpaceY Sol 21`, the agent fixture) would have to be replaced (inferred, not tested). Untested: whether a decorative deck may
instead extend past the connector over the first vanilla element. This is the look pass (above); it
follows build 3b's smoke and the junction fix, and needs the owner's go before it is briefed.
**Owner design, 2026-09-20: six loading sidings, one per internal spur.** The problem it solves came
out of the movement pass: vanilla picks a loading train's exit only **after** it has entered and
loaded (`Station.lua`), so a blocked exit leaves only bad options — sit on the running line and block
its own line and the crossing, or reverse out into the lane the next arrival needs. With a siding the
train loads and waits **off** the running line and a through train passes while it does. The owner's
words: *"a platform off to one side of each internal track... the train slides onto it while loading
and waits for its track clearance to rejoin the track."*
- **Six, not twelve** (orchestrator recommendation, owner accepted): vanilla enforces one train per
  platform and queues the rest on their track outside (`Train:CanEnter`, `GetOccupyingTrain`), so a
  second siding per spur would have nothing to hold. The overflow case — a loaded train waiting on the
  siding while another arrives on that line — already has a home on the transition arm outside.
- **Same rotational handedness** on all six, so a through line's two sidings fall on opposite sides of
  it and the Lua is one sign flipped by connector index.
- **Cantilevered off the track beam, no pillar** (owner), deck top at 8 m, long enough for a whole
  train, and **inside about 23 m radius** so the cargo stacks do not grow through it (beds are centred
  26.75 m out and span about 23.5 to 30 m radially).
- **A clean glass deck with a metal border** (owner), no panel seams. It needs **its own mesh node**,
  because one material per mesh is measured (`_shared/IMPORTER_FACTS.md`; `SceneImport.lua:4023`) and
  that is why `INCLUDE_GLASS = False`. Vanilla's `DomeGlass_*` is tried first at import; if it works,
  the hub's own dome can stop being opaque too.
- **Movement:** the slide onto the siding folds into the braking and the rejoin into the
  acceleration — one curved motion, never stop-then-slide-then-stop, because the hub already adds
  transitions to every trip (owner). **Loading policy and full queueing are a later owner pass,
  deferred 2026-09-20.**
- **Method (owner):** *"not extreme effort in getting it exact... the focus is getting the models in,
  I do the fine adjustments."* The owner eyes the gaps in game and supplies the movement parameters.

⛔ **Texture gate (owner, 2026-09-20):** *"Just function, no textures until I fully green the function from transition, enter, load, exit and transition back on the vanilla track."* The model was imported UNTEXTURED on 2026-09-20 and the owner accepted it in game as a prototype; a track attached down the path between two arms and a train parked on the deck at the right height. **No texture or material pass until the owner greens the whole cycle**, because a re-import throws away the bake and the movement prototype (`TRAIN_HUB_MOVE_high.md`) is what proves the geometry. The arm may need a fourth hex; that is one constant and the owner judges it by eye.
**Owner direction, same sitting: the transition platform.** Two platforms, one each side, three
hexes long as in the owner's screenshots, with the track linking between them to meet our stub
(*"can we still link the train up in between the platform to meet our stub in between them. So we
will need to carefully setup the exclusion zone"*). **Three hexes is the minimum and the starting
length; four may be needed, judged by eye.** The deck is authored asset geometry (`10_TrainFloor.lua`
is the storage floor, not the deck), so each length tried costs a re-import. The screenshot's translucent pieces are
vanilla train tracks the owner placed as stand-ins, to show how the platform would be laid out and
its length in hexes (owner, 2026-09-20). Open: whether the lanes (289 units either side of the line)
sit inside the centre hex row or the rows beside it, since the stand-ins sit a row apart. Also
open: the exclusion zone is the footprint's hex set, and the centre row past the connector must stay
outside it while the stub hexes and the platform hexes are inside; a trial import, with a track laid
to it on a scratch save, is the test the mock cannot replace.
**Owner direction, same sitting: what the transition is (this corrects the orchestrator's two earlier
readings, "the train stays on its lane throughout" and "the platform is a ramp to ground level").**
Trains never go to ground level. On vanilla track a train rides along the **side** of the rail; on
our track it rides **on top, down the centre**, and the visuals must look correct and designed. The
vanilla track brings the arriving train to a platform that sits right under it, beside the rail; the
train moves forward and then **over onto the centre of our track in one smooth move, which must look
right at various speeds**; it rides the centre through the hub; on exit it leaves the tunnel on the
centre, moves over onto the platform beside the vanilla track, and rides the vanilla track as normal.
So there is one platform each side of the line: arrivals use one, departures the other. **No lift is
needed** (owner: *"our platform height already is very close to the bottom of the train"*).
Consequences, read from the code and not run. (1) **This re-scopes build 3b's lanes:** inside the hub
the train rides the centreline, not the 289-unit lanes of brief item 3, so the park position, the
turn point and the reverse's lane join are judged again on the centre; 3b's smoke of the lane build
is not an acceptance of this. It needs the owner's go as a change to 3b or as a build after it. (2)
The move exists already in kind: the reverse's lane join (`HubRouteTrain`, `20_TrainHub.lua:462-479`)
is an eight-step smoothstep in **distance**, with the yaw following the path, so its shape does not
change with speed; the transition would be the same construction over 289 units, not 578, run
outside the portal. (3) A platform under a train that rides 289 units off the line lies inside the
**centre hex row**, the row the vanilla track's own elements occupy, not the rows beside it where
the stand-ins were placed. The footprint cannot take those hexes (the connector is the last footprint
hex on that row), so the platform would be mesh overhanging hexes outside the footprint, above or
beside vanilla track pillars. Untested: whether that is allowed and how it looks against the pillars.
**The layout, as the owner then fixed it (2026-09-20, two screenshots of a train beside the rail at
the stub).** Our stub goes out one more hex, two in all. The platform **wraps round the stub's two
side hexes and runs two hexes further out past the stub's end**, one arm each side, **leaving a
one-hex path between the arms for the vanilla track to reach the stub**. The stub's height is already
very close to the train's underside. The owner's look idea, not yet a ruling: a futuristic maglev
feel, the train passing from the vanilla monorail onto our track, with our track's top retextured to
suit (this would replace §9's red centre stripe if ruled). **Where the merge runs (orchestrator, from
source, not run):** the hub controls a train only from `TrainArrive` (`Train.lua:390`); outside the
connector vanilla's `WaitTraverseElement` moves it, and changing that means wrapping `Train.lua`. So
the train rides over the platform arms under vanilla's control, beside the rail as always, and the
sideways move onto the centre happens **on the two-hex stub**, about 12 degrees of yaw at most for
289 units over 20 m, on a rigid body (vanilla bends the train with a `turnLeft`/`turnRight` animation
on its curves, `Train.lua:539-553`; ours cannot). What the arms give for free: their footprint hexes
flank the centre row, so a player cannot curve the track inside the last two hexes and every train
arrives straight; and a train queueing outside waits over a deck. Geometry to settle by eye on a
render: a train 289 units off the line straddles the zig-zag edge between the centre row and the
flank hexes, so the arms' inner edge overhangs the track's own hexes and must clear the vanilla
pillar under the rail. **Gate before any of this is briefed (owner asked for a straight verdict,
2026-09-20):** watch build 3b's existing reverse lane join, the same smoothstep at 578 units, at
normal, fast and fastest speed; then a code-only trial of centre riding and the merge on today's
one-hex stub. The asset is touched only after the motion passes by eye.

---

## 10 · The prototype, the next build (authorised 2026-09-18)

**Owner ruling, 2026-09-18 (OI-10):** "prototype B via 3a". Appearance does not matter, and the
vanilla body may be reused. The owner wants a go/no-go before investing in an asset. The brief,
now retired, had the done-condition **three lines** (six
connectors), matching the owner's routing target (§6 OPTION 5).

**Round 1 (`dfb8052`, sitting 1, 2026-09-18): the spot overrides held on the placed object;
the sitting stopped before attachment.** Slot 2 read six connectors and six valid track-grid
elements. Placement raised a Lua error because vanilla `CanBuildOver` reads spots from the
construction cursor, and the owner could not see where to attach track. Evidence:
`TRAIN_HUB_PROTOTYPE_20260918.md` §Result. **Owner, 2026-09-18:** rebuild round 2 with both fixed,
then rerun the sitting (the same brief, rewritten). No go/no-go yet.

**Round 2 (`625053c`, sitting 2, 2026-09-18): QUALIFIED GO (owner).** One colony, `Japan Sol
490`. The results:
- Six connectors on the footprint edge, all attached.
- Three routes through the hub, with trains stopping at it.
- Placement over open ground and vanilla salvage both raised 0 Lua errors.
- A save of the colony with the hub removed reloads cleanly.

Cargo crossing was not directly witnessed: drones confounded it, and the case rests on §7.2 T2's
shared station storage. The five must-pass checks for the next hub build are listed in
`TRAIN_HUB_PROTOTYPE_20260918.md` §"Sitting 2 teardown and reload, and the verdict".

**Owner ruling, 2026-09-18 (OI-15): the asset has six connectors (three lines).** Eventually
the owner would also like to offer a **four-connector (two-line) asset** "if it's easy". Design
consequences for the real hub build:
- Connector count and line geometry live in one shared base, and each size is a thin subclass
  with its own template. A four-connector hub is then additive. It needs no migration and no
  change to the six's names.
- Class and template names become save contract once a kept save sees them (ban 1). Name both
  sizes up front, even if only the six ships first.
- Each asset's footprint must reach the last hex along each of its lines, because a connector
  must sit inside the footprint (`Tracks.lua:19-24`). On a hex grid, two lines cross at 60°.
- The four differs from vanilla's large station, whose two lines run parallel, by being a
  crossing. Each size owes its own sitting and its own ship test (`FIX_POLICY` §8).
- ⛔ **The four cannot be much smaller than the six** (owner, 2026-09-20). Footprint radius is
  driven by **where a train has to park**, not by how many lines cross: a two-line hub parks the
  same train on the same length of arm as a three-line one. Fewer connectors buys fewer *stops*,
  not a shorter arm. The principle holds whatever the train's parking length settles at, so it is
  independent of the R-TRAIN dispute (`GEOMETRY_ORACLE_20260919.md` §13) — but the four's arm
  length must be set from the *measured* figure, not scaled down from the six's because it looks
  like a smaller building. Expect a similar footprint with two arms fewer, and price the asset work
  accordingly rather than assuming "the small one is easy".

**Owner rulings, 2026-09-18, for the real hub build.** The brief is
`docs/agent/prompts/TRAIN_HUB_BUILD_high.md`.
- **Build the real six-connector hub** on the prototype body as a stand-in until the owner's
  asset lands. Reserve the four-connector's name.
- **A built-in drone controller with a small work radius**, so the hub maintains itself. Its
  drones serve **anything** inside that radius (owner: *"keep it simple plus people might find
  other use cases like if they have a bunch of waste rock to dump by it and then have it
  transport out"*).
- **A maintenance reserve.** The hub *"holds a minimal stock back for its own maintenance"*.
  Neither trains nor its own drones take Metals below the reserve. This is §4.3's missing
  export floor in its smallest form (Metals only, one fixed amount), so build it so that Module
  A can generalise it. The large station's maintenance is 5 Metals
  (1.1.0.403908 `StationBig.generated.lua:29-30`).
- **Storage is vanilla in mechanism but bigger** (owner, 2026-09-18: *"I think we need bigger
  storage hubs"*). It is a per-resource pool balanced network-wide by capacity share (§7.2 T2),
  which matches the owner's reading, "overflow and distribution". The large station holds 120
  per resource (`StationBig.generated.lua:52`, `max_storage_per_resource = 120000`). The hub
  starts at **240, proposed and the owner may change it**, as one template value. Because the
  balancer settles at capacity shares, a hub with twice the capacity holds twice the share of
  network stock. That fits a distribution buffer, but a player will see it. Per-resource control
  is Module A's.
- **Players watch the storage build up and draw down inside the hub** (owner, 2026-09-18: *"I
  would love the concept of them seeing the storage build up and draw down inside"*). Vanilla
  already draws a station's stock as cube stacks on its pallet sub-models from a `Box1` spot,
  on a grid set in code (1.1.0.403908 `Station.lua:1240-1260`). So the asset models empty
  pallet beds inside the dome with no baked cargo, and the code sizes the grid to show 240 per
  resource. Separate storage depots cannot replace this storage, because trains load and unload
  only a station's own storage.
- **INFERRED, not tested: trains can carry Waste Rock.** `Resource.lua:417-434` sets no
  `transportable = false` on it, unlike the grid and player resources (`:343-413`), and a
  station stores every transportable resource except Seeds (`Station.lua:110-114`).

**The build, 2026-09-18 (pack `886926b`): smoke-tested 2026-09-19, one colony (`SpaceY Sol
20`, 1.1.0.403908).** Design record, predictions and the per-step result are in
`TRAIN_HUB_BUILD_20260918.md` §"Sitting result". Boot, placement, six attached connectors, the
built-in controller, the cube display, reload and salvage passed with 0 Lua errors; Metals left
the hub on a route that delivered none, and the hub paid one maintenance from its own stock. The
export floor turned out not to need an edit inside `Train:TransferCargo`: a claim the station
holds on its own supply request lowers the target every hauler reads, so §4.3's "MISSING" row is
a wrapper.

**Owner rulings, 2026-09-19, from the sitting.**
- **Testing depth:** *"we just need to be doing the bare minimum testing before we do the real
  model we can do in-depth testing when we have a final build and revise around that, I don't
  want to do multi hour battery of test each design pass."* A design pass gets a smoke test
  (boot, place, attach, trains through it, reload, salvage, 0 errors); the full prediction
  battery runs once, on the final build with the asset.
- **Drone radius:** default **10**, and *"maybe"* a slider up to **20** (the slider is
  tentative). The infopanel needs the vanilla drone hub's section: drone count, load and service
  area. The build shipped a fixed radius of 8 and no drone section. Reason seen in the sitting:
  end stations placed 10+ hexes out get no maintenance from a radius-8 hub, and at ultra speed
  they wear out within about seven sols.

**Build 2, 2026-09-19 (pre-boot).** The tentative slider was built because vanilla's persisted
`work_radius` and non-saving `UIWorkRadius` supply the whole mechanism: no new persisted name. Its
range is 10–20; fresh hubs start at 10 and build-1 radius-8 hubs rise to 10 on load. The infopanel
uses vanilla's service-area section and a small custom section with the vanilla Drone Hub count/load
presentation. The imported `SMROptInTrainHub6` entity is selected by the editable template source;
its connector, direction and `Box1` spots win, while its missing train operating spots remain
computed. Build record, desktop gates and the three-batch smoke are in
`TRAIN_HUB_BUILD_20260918.md` §"Build 2". Status is PRE-BOOT; no asset or UI pass is claimed.

**Build 3, 2026-09-19: SMOKE PASS.** The owner replaced build 2's tentative controls with a fixed
15-hex drone radius, no slider and no prefab buttons. The working charger was removed; its pad
model remains inside the ring for build 4, while the hub tops its two current drones up to a large
battery maximum. The hub is the single +70/-10 power-grid object and carries a 75% Fusion Reactor
as a visual. The final import has 66 outline hexes (61 ring plus the five-hex reactor lobe), radius
4 on each of six lines, the inner pillars cut and six cargo beds correctly aimed. Six tracks and
six station grids attached with zero grid mismatches.

Measured z/width values, game units: running surface `10800`; connector `10800`; stub top `10800`;
track x width `1000`; track y width `204`. These measurements caused no Lua change; `6123ae7` was
the separate, already-committed synthetic train-spot deck correction.

Storage is 150000 per live resource and produces `max_z=9`. A fill-all made 2850 cubes: 19 current
request-backed resources at 150 each, with no clipping by the owner's inspection. The nominal
station/transportable list has 21 entries; `BlackCube` and `MysteryResource` were the two absent
request types. Vanilla creates requests only for enabled presets (`MultiResourceDepot.lua:409-412`,
game build 1.1.0.403908), so 19 is this colony's request-backed set and 21 is its candidate list.
Save/load preserved the full storage, six connections, power, radius/overlay, drones, launch-pad
model and absence of a charger. Details and the log fingerprint are in
`TRAIN_HUB_BUILD_20260918.md` §"Build 3".

Train movement across the hub is not a build-3 claim. The owner ruled the observed floor drop and
floating as a separate full rework; `TRAIN_HUB_TRAINS_high.md` is build 3b. Its implementation
and unattended smoke are recorded in `TRAIN_HUB_BUILD_20260918.md` §"Build 3b"; the owner's
visual acceptance is still pending.

**Owner correction, 2026-09-20: the train-length figure is DISPUTED and the redesign is off.**
The owner measured a train against the game's hex grid at about two hexes (~20 m) with three hexes
of margin, against the 41.5 m that §11 and the build-3b gate rested on; the hex measurement governs
and R-TRAIN is disputed (oracle report §13). `TrainCCP3` has no mesh of its own and `Train` is an
`AutoAttachObject`, so the `GetEntityBBox` read was taken on an assembly and its span is not
established. The step-0 gate verdict is set aside and OI-22 is withdrawn from the owner's list, where the gate
run had filed it. **The resolution is that park position is a tunable in our own Lua** — Stop, Spawn and the
ramps are synthetic spots this mod computes, so the distance is tuned by eye and judged in the
smoke. The asset options costed the same day (runtime `SetScale`, three alternating lines, a new
tunnel hood, `FOOTPRINT_R = 5`, resizing the dome) are withdrawn. The look standard stands: an
unnoticeable result is required, and it is met by tuning the number, not by changing the body.

**Build 3b implementation, 2026-09-20:** park distance is the live
`SMROptInTrainFloor.HubParkDistance` control, provisionally **20 m** after the 17/20/23 m visual
comparison. Own-line reservations survive retuning; the saved crossing lock serialises movements
through the centre.
Other-line departures follow their lanes to a timed centre turn; a same-line reverse retains
Stop's position and then joins the outward lane on a curve. TestKit controls and native smoke
evidence are in the build report: straight, 60°, 120°, reverse and a parked-plus-crossing reload
passed unattended; turn/portal appearance and queue clearance still need the owner. The body,
train scale and economy are untouched. The withdrawn gate's calculations remain in oracle
report §12 and do not gate this implementation.
Build 4 remains held until build 3b's smoke is recorded.

**Owner requirement, 2026-09-20: the hub must start in a remote, droneless area with little except
what a person brought to build it.** Found in the sitting on `train_hub_base` (no power, no drone
hubs): a fresh hub read production 0, consumption 10 and "Not enough Power". The code cause, read
statically and not yet run: `20_TrainHub.lua:877` (`CreateElectricityElement`) sets production to
the 70000 only while `self.working`, and a hub with no other supply is never working, so it cannot
start itself. Build 3's smoke passed only because seven Stirling generators were already on the
merged grid, and the build report's placement step tells testers to use `NoConsumption` to get
round it. The "powers itself" line in §10 and in the hub's description is therefore untrue on a
cold start. Last night's commit `b02db74` changed no power line; the values are still +70/-10.
Owed, before build 4 (it touches `20_TrainHub.lua`, which build 3b owns until its smoke): production
must count while the hub is unpowered and stop only for malfunction or switched off, so a lone hub
starts on its own output. Open, not yet ruled: what else must work with no drones and no grid, such
as the maintenance the hub pays from its own stock, the crew that only exists at a working hub, and
where the start-up stock comes from. The 20-power base direction above depends on this fix.
**A cold-start test runs with the seven Stirling Generators removed from the fixture**, or the
hub's own production is never the only supply.

**Centre/transition implementation, 2026-09-20 (owner acceptance pending):**
`TRAIN_HUB_MOVE_high.md` now has a hub-local arrival and mirrored exit: stop on the arm,
smoothstep sideways, then run on the centre. The live pause distance starts provisionally
at 45 m from centre after the owner reported the initial 30 m stop about 1.5-2 hexes too late;
45 m is the next visual trial. Parking starts at the owner's previous 13 m for a new judgement.
Neither uses the disputed train length. The cold-start gate is implemented at creation,
load, working-state updates and production-modifier changes; it no longer depends on receiving
grid power. A small mocked contract smoke and Lua parsing passed, not a native or visual test.
The current TestKit controls and first owner batch are in `TRAIN_HUB_BUILD_20260918.md`
§"Centre/transition prototype". Remaining: the owner-view cycle at every speed, turns, queue,
parked-plus-crossing reload and the isolated-power check above. Build 4 and texture work stay held.

**Owner close-out direction, 2026-09-20, after exit contact:** finish the movement pass; the
owner will change loading/queueing in the next pass. The movement guard now checks for a
parked train on the intended exit line, which vanilla's track-free test excludes. Own-line
reversal remains permitted; through trains wait outside at vanilla's endpoint, while loaded
departures wait at their park. No ordered platform queue or loading-policy change is included.
The mocked regression passes; native acceptance and mutually blocked departure policy remain
open. The owner witness, partial flushed log and precise limits are in the build report's
"Exit contact and scope ruling" passage. The log's last pause tuning was 37 m, not 45 m.

**MEASURED 2026-09-20: a train and a shuttle cruise at the same speed. Trains are not slow.**
Log `docs/archive/train_speed_Mars.exe-20260920-18.39.01-6a91a190.log`, save `train_hub_base` sol 28,
game 1.1.0.403908, both packs + TestKit + the dev hub. Method: one game-time console line sampled
every `CargoShuttle` and every `Train` in `UICity.labels`, slept 1000 ms of game time, and reported
the furthest each type moved; 15 samples. Game-time sleep, so the speed slider does not affect it.

| | per game second |
|---|---|
| Shuttle | 3,939 - 4,898, steady (typically ~4,800) |
| Train, cruising | 2,682 - 5,409 |
| Train, stopped at a station | 0 |

The train's best samples (5,409 and 5,215) **beat** the shuttle's best (4,898). ⛔ **The template
constants are not the currency anything moves in and must not be compared across unit types**:
`Train.move_speed = 1000` (`Train.lua:28`) against `CargoShuttle` `move_speed = 30*guim`
(`ShuttleHub.lua:476`) predicts a 30x gap that does not exist. `Shuttle.__parents` is
`{ "FlyingObject", ... }` (`ShuttleHub.lua:459`) with no `Movable`, so a shuttle has no `GetSpeed`
at all and its constant feeds a different flight system; `Train` reaches `Movable` through
`Vehicle`, and even there the live `GetSpeed` read 4502 against a computed nominal ceiling of 1995.
An orchestrator read of the constants alone produced two wrong tables before the owner's eye and
this measurement overturned them (owner, 2026-09-20: shuttles are visibly faster but nowhere near
that much). **Bias to state with the numbers:** the line takes the fastest unit of each type, so
with several shuttles it always catches one cruising and never one hovering, landing or loading,
while the single train's profile includes its stops. The shuttle figure is a best case.

**So the trains problem is not speed.** At equal cruise speed what costs a train its time is
stopping at every station on the route, following track where a shuttle flies straight, and
braking and accelerating between elements (the 0 and 2,682 samples). That is routing and stops,
which is what Module B is for. Not yet measured: door-to-door trip time for the same cargo by each
method, which is the number a player actually feels.

**The train speed chain, for reference** (`Train:GetNominalMoveSpeed`, `Train.lua:592-613`): without
Faster Trains x0.70, with it x1.00; Vacuum Rail Systems x1.50; the Train Track Standards law x1.33;
and **during a cold wave only** x1/3, or x2/3 with Safe Transport. The cold branch reads
`GetHeatAt(...) <= 90`, and the heat grid is created filled with `MaxHeat` (`Heat.lua:39`), so it
does not fire in normal weather (owner confirmed in play, 2026-09-20; `Drone.lua:286` shows the same
`HasColdWave` gate). An earlier orchestrator claim that trains always run at a third speed was wrong.

**Candidate, the owner's, 2026-09-20 (thinking about it; not briefed and not a ruling): a heated
track upgrade.** Cold waves cut the speed of everything, and the train branch above is a x1/3 during
one. Track connected to our hub would get a heated bonus, so a hub network keeps moving through a
cold wave. Open: whether it warms the heat grid (the hub would act as a `heater`, `Heat.lua`
`heaters`) or wraps the speed for trains on our network; what it costs; and whether it also helps
drones and rovers in range, which take their own cold penalties. Decide it after the movement
prototype, not before.

**Owner direction, 2026-09-20: the hub's economy becomes an upgrade (candidate, not briefed; the
Electronics amount is pending the owner's OI-19 research).** Base hub: **20 power** generated,
**5 Metals** maintenance as the large station's (`StationBig.lua:31-32`), and it draws 10. Mini-reactor
upgrade: **+80 power, 100 in all** (half a fusion reactor's 200, `FusionReactor.lua:19`), still 5 Metals,
plus **1 Electronics** upkeep. Owner reasoning: 2 Electronics for 70 power and a two-drone crew is
dearer per unit of power than a fusion reactor (3 Electronics for 200), in the scarcest early
resource, and a drone hub's 1 Electronics is often researched away early. The owner's Polymers idea
(1 Polymers, as half an Advanced Stirling's 2 Polymers for 40 power, `AdvancedStirlingGenerator.lua:16-25`)
is dropped: `maintenance_resource_type` is one string per building (`RequiresMaintenance.lua:22`, one
demand request at `:80`), so 5 Metals + Polymers would need a code-side second request, which is
unverified and adds persisted state (ban 1). Mechanism, read from `Building.lua:1131-1235`
(1.1.0.403908), not run: an upgrade's modifiers change numbers only, so the +80 `electricity_production`
is a modifier, and the Electronics is the upgrade's own upkeep (`CreateUpgradeUpkeepObject`;
`AutomaticMetalsExtractor.lua:40-42` is the vanilla precedent). Consequence: the base hub powers itself
and one large station (20 - 10 = 10), and the other five need grid power; upgraded, 100 covers the hub
and six stations (70) with 30 spare. Build 3's smoke tested the old +70/-10. Open, the owner's: the
Electronics upkeep amount; what unlocks the upgrade (a tech, or always available; whether a mod can
add either is untested). It touches `20_TrainHub.lua`, so it would follow build 3b's smoke and
precede build 4.

**Owner direction, 2026-09-18:** run §7's T1–T3 **before** the prototype build, and the owner
runs the in-game checks. Done (§7.2), and the build is ruled (above).

**Shape (recommended; re-scope from T2's result first).** Module B only, option 3a, interchange
only (5a). A `Station` subclass whose template references `entity = "PassageHub"` by name, with
the palette moved to the train family and connector positions computed in Lua. It must be a
`Station`: interchange needs storage and the balancer, and a bare `TrackConnectedObjBase`, like
the tunnel, only passes trains through. **T2 passed 2026-09-18 (§7.2), one colony:** vanilla's
large station already carries two-route interchange. The prototype's question therefore narrows
to "does a PassageHub-shaped hub with **more than four** connectors (three or more routes)
work". OPTION 5 stays at 5a. PassageHub's hex footprint, including how many edge hexes it has, is
not readable from Lua and is discovered during the prototype.

**Step 0 is a spike:** override `GetSpotBeginIndex` and `GetSpotPos` on the class (§7 item 6).
If that fails, override the six `TrackConnectedObjBase` spot methods and wrap the two external
readers, `TrackElement.lua:345` and `Train.lua:660`. §5.4 lists all twelve sites.

**Done means:** the hub is buildable; tracks attach to its computed connectors; trains on two
routes both stop at it; cargo moves from route A through the hub to route B; and it demolishes
cleanly. `PassageHub.lua:50-55` warns that teardown is where hubs assert.

⛔ **Disposable saves only** (the brief binds it). The
prototype's class and field names are not save contract until they touch a kept save; after
that, ban 1 makes them permanent.

**The build prompt** is authored with the `prompt-authoring` skill as a root one-off, only after
T1–T3 results are recorded in §7.

**The standing test save, `train_hub_base` (owner, 2026-09-20).** The save the owner loads every
round. Recorded from the owner's account; the save file and the build it was made on have not been
read. Its content as described:
- Seven stations prebuilt, all with empty bays and no drone hubs, and **prebuilt trains** (owner,
  2026-09-20). Both this save and `train_hub_base_agent` carry **seven Stirling Generators**, which
  mask the cold start below; they must be removed to test it. Neither save is a cold-start
  fixture as it stands.
- Six lines already set, their tracks laid, to connect to a hub at the centre. **Only the hub is
  built each round.** The centre site is bare ground with the six track ends stopping short of it,
  one from each direction: two diagonals from the upper left and upper right, two horizontals from
  the left and right, and two diagonals from the lower left and lower right (owner's screenshot,
  2026-09-20, read by eye; no gap was measured). Dropping a fresh hub on it is the whole setup.
- The lines are joined in a mix. Some stations connect to each other and to the hub; one station
  is reached only through a station that is connected to the hub. The map's large station has one
  line to the hub and its other line to a station that is connected to the hub.
- The large station is one of the seven (owner, 2026-09-20), and every "connected" above means
  stations connected.
- `train_hub_base` is the only save the owner has used for testing lately. The exception is a test
  that needs stations actually connected and running inside a large, complex colony, for which
  `train1` (sol 71, §7.2) remains the save.

`SpaceY Sol 21` (file dated 2026-09-20 03:27, the save build 3b's agent ran on) is the same base with a hub
built and powered, saved by the owner before bed; it is not a separate fixture (owner, 2026-09-20).
Its hub predates the agent fixture, which was built later that day.

The owner's 2026-09-20 setup work (several trains built at each station from filled train-yard
pads, so trains need not be built each sitting) is what put the prebuilt trains into the saves.

**The agent fixture, `train_hub_base_agent` (owner, 2026-09-20).** For unattended work, when an
agent launches the game and tests on its own. "The exact same setup" as `train_hub_base` except:
the hub is prebuilt and full of resources, `StationSmall(2008)` is full of resources, and every
other station is empty. **The hub is powered off**, to keep trains from firing at once, so an
unattended leg must switch it on itself. Both saves are otherwise identical: the same stations,
trains and Stirlings (owner, 2026-09-20). Not yet recorded: the saves' build and mods.

**Owner observation, 2026-09-20, from building that variant.** With train construction as the only
task, drones do haul the materials from the train yard's storage pad to the train under
construction. The owner had missed it earlier because of high game speed and how close the drones
fly to the track. It shows a construction site supplied from a building's own pad. **It does not
show** that drones draw a hub's or ordinary station's stock for a nearby site; build 1's
prediction 9 (the Metals reserve against a construction site in the hub's radius) is still
untested. For §4.3's owed `accept` retest, a train-yard site in drone range is a Metals consumer
whose supply may be the yard pad and not the station, so the fixture must keep the two apart.
