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
  at `B:\Dev\SMR\SMR-Assets\trainhub\reference\` (game art, local only).

**The owner's asset: shape approved by the owner 2026-09-18 (OI-15 = six, OI-16 = 4b).** The
owner, after the rebuild: "I actually think that turned out perfect", and the rest waits on the
game. The concept art was iterated with an image AI and meshed in Tripo (Smart Mesh, quad
topology, about 15,000 polygons, untextured, FBX with the Blender preset). Its output is
`C:\Dev\SMR-Optin-Assets\circular industrial platform 3d model.fbx`: binary FBX 7400, 15,229
vertices and 281 loose parts. The Blender 5.2 pipeline lives outside both repos in
`B:\Dev\SMR\SMR-Assets\trainhub\blender\`, and its `README.md` gives the steps:
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
  `B:\Dev\SMR\SMR-Assets\trainhub\blender\textures\`: `TrainHub_BC` (sRGB base colour), `TrainHub_NM`
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

  ⚖️ **Owner ruling, 2026-09-21: the 5 MB guard does not bind this mod.** It exists for the fix
  pack, which is Lua only, has never carried assets and never will; the opt-in ships assets. So
  `PACK_MAX_BYTES` is no ceiling on the hub's maps, and texture resolution is a **look decision**
  (raw DDS sizes: BC 2.8 MB at 2048 and 11.2 MB at 4096; BC5 normal 5.6 and 22.4; the four maps
  14 MB and 45 MB). The tool itself is not yet adapted: `upload_preflight.py:47` still applies it
  and `:188-196` still admits no asset files (OI-18's remaining question). VRAM and download cost
  stay unmeasured.

  **Owner, 2026-09-21: the hub is wonder-sized and must feel premium.** Vanilla spends 4096 on
  wonders (55 of 5,087), and the hub's model is about 144 x 160 m against about 90 m for the large
  station. **Plan for the structure step:** BaseColor at 4096 supersampled, Normal, RM and SI at
  2048, Normal up to 4096 only if the seam relief stays soft, panel seams kept and made crisp
  (`Train_Hub_Project/01_TRAIN_HUB_STRUCTURE_high.md`). Going to 4096 later is one constant per map in
  `paint_concept.py` (`BODY_SIZE`, line 24) because the maps are drawn per texel from 3D position;
  pixel-based constants (the bleed `steps=4`) and `validate_pad.py`'s 2048 pins need updating.

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
  `INCLUDE_GLASS = False` because the default material is opaque; a second mesh node is not a route
  (the importer keeps one, MEASURED 2026-09-20, "six loading sidings" below); (3) **the stub looks nothing like the vanilla track**: it is a slab with a hex
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
- **A clean glass deck with a metal border** (owner), no panel seams. **Real glass is a texture-pass
  question, gated; the owner accepted opaque panels until then (2026-09-20).** A second mesh node is
  not a route to it: the importer keeps one mesh node and silently discards any other (MEASURED
  2026-09-20, below; `_shared/IMPORTER_FACTS.md`), which also closes that route for the hub's dome.
- **Movement:** the slide onto the siding folds into the braking and the rejoin into the
  acceleration — one curved motion, never stop-then-slide-then-stop, because the hub already adds
  transitions to every trip (owner). **Loading policy and full queueing are a later owner pass,
  deferred 2026-09-20.**
- **Method (owner):** *"not extreme effort in getting it exact... the focus is getting the models in,
  I do the fine adjustments."* The owner eyes the gaps in game and supplies the movement parameters.
- **Built 2026-09-20** (`hub_skeleton.py`, constants `SIDING_*`; `build_workfile.py` then
  `export_prep_untextured.py`, verifier `LOOK_PASS_PROOF` PASS with `sidings: 6`,
  `siding_panels_in_body: 6`, `separate_mesh_nodes: 0`). Each deck runs along its beam's edge to
  `SIDING_TO = 23.0` m before the along-spur shift below, `SIDING_W = 4.0` m wide, top at 8 m, its
  inner end cut parallel to the neighbouring spur (`SIDING_CLEAR = 2.0` m from that centreline before
  the shift): 19.7 m along the beam, 17.4 m along the outer edge. Three gussets under each, no
  pillar. Border (`SIDING_BORDER = 0.35`), gussets and a flat panel flush with the deck top
  (`SidingPanel_*`, from the border's inner outline) all join the body in the body's material.
  **Handedness:** `SIDING_SIDE = 1` is counter-clockwise of the spur in Blender; the importer's map
  is a reflection (`_shared/IMPORTER_FACTS.md`), so it is predicted clockwise in game.
- **MEASURED 2026-09-20 (owner's import, seen in game; `SMROptInTrainHub6.entjson` after it holds 1
  `"mesh"` and 1 `"material"`, `grep -c`): the importer takes one mesh node only.** The first export
  carried the glass as a second mesh node, `SidingGlass`, a child of the body with its own material.
  The importer discarded it silently and the sidings came in as open frames. The reading that
  `SceneImport.lua:4023` ("Contains multi-materials. Not supported yet.") means a second look is a
  second node was an inference and is wrong for this importer: `:4023` rejects several materials on
  one mesh, and nothing offers a second mesh.
- **The arms' hand shift is now in the generator.** The work file that was imported as pass 1 had all
  twelve arms moved 0.573 m outward as object offsets, which the generator did not carry
  (`Platform_1` lateral 1.76 to 5.16 m in the `.blend`, 1.19 to 4.59 m from the script), so a rebuild
  would have undone it. It is `PLATFORM_DECK_SHIFT = 0.573`; the arm centre is 3.463 m off the line.
  **Owner, 2026-09-20: the shift was intended** — an agent made it by hand to take the arms out of
  the beam — *"Keep 0.573."*
- **The sidings' along-spur shift is the owner's and is kept (owner, 2026-09-20).** In Blender the
  owner moved `Siding_1` by -0.28 m on object X, along spur 1 toward the hub centre (no height or
  lateral change wanted), and after the import a further -0.02 m to bury a hairline crease seen in
  game where the siding's inner end face was coplanar with the beam's side wall. It is
  `SIDING_ALONG_SHIFT = -0.30`, applied through each siding's own turn to all six frames, gussets and
  panels; every object offset stays 0 and the verifier asserts both. The decks end 22.70 m out. For
  the owner's eye, not a blocker: each inner corner is 0.26 m closer to the neighbouring spur's
  centreline, 2.0 m down to about 1.74 m.
- **Uniform sink (owner, 2026-09-20: *"a uniform pass of making sure both sides are slightly sunk into
  the tracks to avoid another pass of blender work"*).** Where the crease came from, from the
  geometry: the -0.28 m shift put each siding's cut inner end 1.76 m from the NEIGHBOURING spur's
  centreline, a hair off that beam's side wall at 1.75 m; the long side was exactly on its own
  beam's wall. Both faces now sit `SIDING_SINK = 0.05` m inside the beam wall they meet (1.70 m from
  each centreline, which replaces the 1.74 above), and the deck top is `SIDING_TOP_DROP = 0.005` m
  under the beam top so the sunk strip cannot z-fight it once textured. The outer end and the -0.30
  shift are untouched. The verifier asserts both sinks and the drop. The transition arms were NOT
  touched: their inner edge is 1.763 m out, 13 mm clear of the beam, by the owner's 0.573 ruling.
  Imported by the owner 2026-09-20: no crease at either beam (owner's screenshot).
- **Flush panels vanish into the track (owner's two screenshots, 2026-09-20).** With the panel flush
  and in the body's one untextured material, a siding read as a wider piece of track; the import
  before it, where the glass node had been discarded, read clearly as a frame because it was open.
  Agent's response, the owner's ruling on it still owed: `SIDING_PANEL_RECESS = 0.10` m puts the
  panel under the border so the border reads as a rim (0 restores flush, which the owner had asked
  for). Rebuilt and re-exported; that export is not yet imported.

✅ **THE TEXTURE GATE IS LIFTED (owner, 2026-09-21).** Two rulings on the same day close it.
The transitions: *"transitions are 99%, we might have some very slight tweaking before launch but
they have convinced me."* The model: *"all of the model changes are done unless something truly
unexpected comes up, everything fits and nothing clips."* The final model is committed
(`d1beaba` here, SMR-Assets `54eb84d`) and a bake is baked against that.
⚠️ **What the gate actually protected, so the remaining tweaks do not re-arm it:** a re-import
throws away the bake, and only a MODEL change forces a re-import. The owner's "very slight tweaking"
is movement tuning — pause, park, onset, slide rate, dwell — all constants in `20_TrainHub.lua`,
which can move freely for as long as they like at no cost to a bake. If geometry or UVs move, the
bake is spent and the gate is back; that is the one condition to watch.

**The look pass's engine facts, read 2026-09-21 from the archived 1.1.0.403908 tree.** Settled
before the pass is briefed, because each one decides how the art is authored.
- **Self-illumination is a supported map** (`GFXMaterial.lua:137`, `MatMapToMatProps.SI`), alongside
  base colour, normal, RM, AO, colorization and the rest. ⚠️ **It compresses to BC4, one channel**
  (`:1100`), so it is a greyscale MASK of where a surface glows; the colour comes from the base
  colour beneath it. Blue strips = blue in BC, white in SI along the same shapes.
- **The game already drives that glow as a gameplay signal.** `Building:WorkLightsOn/Off` are
  `SetSIModulation(200)` and `SetSIModulation(0)` (`Lua/Buildings/Building.lua:1413-1419`), run from
  `OnSetWorking`, so a hub with an SI map goes dark when it stops working with no code from us. The
  call is ours to drive too (a siding lit while a train loads on it, an inbound line lit). The engine
  keeps `NightLightEmissiveEntites` for entities that glow only at night, so day-or-night is a choice.
- **Glass cannot live in the hub's own mesh.** One material per mesh node — the importer's own words
  are *"Contains multi-materials. Not supported yet."* (`SceneImport.lua:4023`) — and MEASURED
  2026-09-20, a second mesh node is discarded silently (`_shared/IMPORTER_FACTS.md`).
  ⭐ **The route is a separate attached entity, which is exactly how vanilla does every dome:**
  `DomeBasic_Glass`, `DomeOval_Glass`, `DomeMega_Glass` are their own entities attached at the dome's
  `Origin` (`Lua/Buildings/Dome.lua:501`, `:3042-3075`). A glass entity carries its own material, so
  its own blending (`BlendType`) and its own SI, modulated independently of the body.
- **Owner, 2026-09-21: the sidings keep their glass.** *"I still want the glass for the loading
  platforms, the concept art is wrong about that part, but I like the border and if we can add any of
  that blue glow into the glass or around it that would be nice."* So: border and its glow in the body
  maps, glass as the attached entity, blue glow available in both and tunable against each other.
- **Adding the glow later is cheap; changing the model later is not.** The entity points at a
  material and the material at its maps, so an SI map can be added to an existing material without
  re-importing the mesh (reasoned from the file structure, confirmed by one check the first time).
  What is NOT cheap is moving geometry or UVs after a bake. Author the glow strips as clean shapes in
  the base colour so the mask can be cut from them later, and freeze the UVs at the bake.

**Concept preflight, 2026-09-21 — stopped before asset changes (OI-23).** The owner's
`reference/Concept.png` and `reference/overall.png` were viewed and match the brief's blue-lit
maglev direction. At assets HEAD `54eb84d448bc6f5d74f6335711504e04fe4697a7`, run from
`B:\Dev\SMR\SMR-Assets\trainhub\blender`:
`blender --background export/TrainHub_export.blend --python-exit-code 1 --python preflight_concept.py`.
The read-only command exited 1 on its UV gate. Filter: every polygon in `SMROptInTrainHub6`,
first UV layer, absolute shoelace double-area below `1e-12`. It reconciled **11,678 faces =
10,598 zero-area + 1,080 nonzero-area**; the former each have one distinct UV corner, the latter
four. Loaded file SHA256: `d6967283887bce0c78bca7735d28e50e0261c88d577a690cf817685360aa5657`.
The exported UV layer exists but cannot carry distinct surface detail on the collapsed faces.
The old `texture_hub.py` would unwrap again; invoking it would violate the brief's UV freeze.

The same HEAD's `hub_skeleton.py` siding block generates `SidingPanel_*` prisms and explicitly
joins panels, borders and gussets into the body. Source inspection found the panel generator
in place of the brief's claimed separate `SidingGlass`. Thus a transparent overlay leaves opaque
panels underneath. Proposed exception: move those existing panel faces into the attached glass
entity without reshaping or moving them, and create then freeze a usable body UV layout before
the first concept bake. At that preflight stop no model, UV, texture, runtime code or imported
entity was changed; no concept render or in-game look was produced.

**OI-23 APPROVED, owner 2026-09-21: both changes, with three conditions.** Unwrap the body and
separate the siding panels into the glass entity. The ban protected a bake that does not yet
exist; collapsed UVs cannot carry textures, and the already-ruled glass needs a separate material.
Preserve every piece's shape and position exactly: **"everything fits and nothing clips"** must
survive. (1) The unwrap is scripted into the pipeline and deterministic: same input, same UVs,
every run, never a downstream hand edit. (2) The verifier gains a UV fingerprint so layout drift
fails loudly instead of scrambling the art. (3) The existing geometry proof passes and the report
states it. After these proofs pass and the work lands, the model is frozen again and the ban
resumes in full: from the first bake onward, a geometry or UV change spends the bake and is a
stop, not a decision. The orchestrator tags this state in both repos before any paint is baked.

**OI-23 preparation proof (Blender 5.2.2 LTS, build `d13f752e3b9c`).** Assets
`export_prep.py` now calls `prepare_concept.py`, with no bake. The unchanged
`verify_look_pass.py` passed on the approved workfile and the full generator rebuild. The new
proof compares exact world-space face-boundary multisets through the panel split and geometry
hashes through the unwrap: **shape and position unchanged**, including spots and surfaces.
The evaluated source also fingerprints the converted ribs, which the older MESH/EMPTY proof
alone did not cover. `concept_freeze.json` holds the source/export geometry and exact float32
per-face/per-loop UV fingerprints, including topology. Normal exports reject any mismatch before
writing deliverables; the legacy re-unwrapping baker and combined-panel exporter now stop.

Executed from `C:\Dev\SMR-Assets\trainhub\blender`, against assets base `0717592` plus this
implementation (the paired `hub-prepaint-uv-frozen-20260921` tags identify the landed source):
`blender --background TrainHub_work.blend --python-exit-code 1 --python export_prep.py -- --freeze-candidate`,
then `blender --background --factory-startup --python-exit-code 1 --python build_workfile.py -- --check-rebuild`,
then `blender --background export/concept/TrainHub_rebuilt.blend --python-exit-code 1 --python export_prep.py`.
The approved workfile and regenerated workfile produced identical fingerprints. Candidate mode
closes once the baseline exists; no rebuild can silently replace it. Filter: every evaluated
source face routed into body or glass. Reconciled **11,678 = 11,642 body + 36 glass faces**, with
the panel source members listed in `concept_freeze.json`. Dome glass is excluded.

`blender --background export/concept/TrainHub_prepaint.blend --python-exit-code 1 --python verify_concept.py`
passed separate FBX round trips and deliberate UV-coordinate/vertex mutations for each entity.
Filter: all exported nodes, parent links, transforms, ordered polygon boundaries and UV corners;
results in `export/concept/verification.json`. Maximum UV delta was **0** for each entity;
maximum geometry/transform component delta was **1.1920928955078125e-07** for the body and **0**
for glass, below the verifier's `1e-4` FBX tolerance. These are Blender checks, not an in-game
glass/material acceptance. The prepaint exports are `export/concept/SMROptInTrainHub6.fbx` and
`SMROptInTrainHub6Glass.fbx`; no paint was baked before the restore point. Executed model from
the developer transcript: GPT-6; no more specific runtime identifier was supplied.

**First concept paint prepared, 2026-09-21 (owner: "As long as we have backup up your work you
can proceed").** Both `hub-prepaint-uv-frozen-20260921` tags were checked before painting:
assets `69b23fc`, OptInPack `5657136`. `paint_concept.py` now regenerates BC/NM/RM/SI directly
on the frozen body and glass UVs, with before/after fingerprint checks. The owner's reference
direction is expressed as off-white shells, near-black decks, blue centre dashes, flowing lines
on the transition arms and glass, lit portal rims and body borders. Dome glass remains excluded.
The Blender day/night and detail previews were inspected; the deck's initial excessive gloss
was reduced in RM. This is a first cut for the owner's game view, not acceptance of the concept.

The body uses **2048-square** maps and the platform glass **1024-square** maps. These are the
first-pass choices for the visible line detail; no 4096 default. From the assets blender folder,
`python validate_concept_maps.py` at base `69b23fc` plus this pass emitted **63,967,448 bytes** of
TGA sources and **18,176,648 bytes** estimated DDS including mip chains. Its
`export/concept/map_validation.json` lists each map and reconciles both sums. The DDS estimate
uses the formats in archived 1.1.0.403908 `CommonLua/Libs/DevToolsPublic/GFXMaterial.lua:1098-1138`;
it is not a measured import or a packed-mod size. OI-18 remains the owner's ship-size decision.
`paint_source/README.md` explains a hand-editable RGBA BC overlay that survives regeneration;
all glow geometry and palette knobs remain in the script so BC and SI can change together.

`build_concept_reactor.py` produces `SMROptInTrainHubReactor`, a simple white housing around a
dark core with blue rings, sampling the body's material. **Material sharing works in Blender
and survives its FBX round trip; sharing in the Mod Editor remains untested.** It adds no map
set and never edits a vanilla material. `20_TrainHub.lua` selects this new entity after import,
otherwise retaining FusionReactor. It preserves the existing offset, scale and Working FX
actor. `SMROptInTrainHub6Glass` is attached at Origin and follows the reactor's existing
DeleteOnLoadGame/recreate lifecycle; both new visuals receive SI modulation from working state.
No movement code/tunable, economy, persisted class or persisted field changed.

Executed asset commands (Blender 5.2.2 LTS) are listed in `blender/README.md`: `paint_concept.py`
on `export/concept/TrainHub_prepaint.blend`, `build_concept_reactor.py` and
`verify_concept.py -- --with-reactor` on `TrainHub_look.blend`, then `validate_concept_maps.py`
and `render_concept.py`. The paint and verification reports carry commands, HEADs and filters.
The frozen body/glass checks and deliberate drift-rejection controls pass. The FBX verifier
passes each exported node/parent/transform/face boundary/UV corner for body, glass and reactor;
reactor material assignment survives. Source maps pass dimensions, raw TGA channels, RM R/G
agreement, greyscale SI, blue BC alignment under lit SI, and transparent glass alpha.
`python tools/devmods/train_hub/tests/look_smoke.py` at OptInPack base `5657136` plus this pass
passes mocked missing-import fallback, replacement, repeat initialization, preservation of a
foreign attachment, offset/scale/FX, working on/off SI and recreation after mocked load deletion.
`python tools/parsecheck.py --dir tools/devmods/train_hub/Code --quiet` passes. Neither test is
evidence of native rendering, importer acceptance or serialization.

**Iteration 1, owner 2026-09-21: centre fix and relaid lights alone.** The owner imported the body
with BC, Normal, RM and SI and saw centre z-fighting. The owner approved a geometry exception:
replace the overlapping crossing with a single centre plate, preserving shape and position
everywhere else, then re-run the geometry/UV proofs, re-bake and re-freeze. Dashes belong on the
outer transition arms; inward they converge into one line ending in the portal. Inside the ring
the floor carries continuous radiating curves. Glass and the themed reactor are deferred to a
later session. Bare siding frames and the vanilla FusionReactor visual are expected until those
entities exist. The owner receives ONE import round, the rebuilt body, with no glass steps.

**Centre preparation proof, before rebaking.** Assets base `97eaeeb` plus this implementation,
Blender 5.2.2 LTS `d13f752e3b9c`: `build_workfile.py -- --check-rebuild`, then
`export_prep.py -- --centre-candidate --body-only` on that rebuilt blend produced the candidate.
After explicit promotion to `concept_freeze.json`, a fresh `build_workfile.py` and
`export_prep.py -- --body-only` on `TrainHub_work.blend` reproduced the exact contract. The
previous manifest is preserved as `concept_freeze_first_cut.json`; the centre candidate switch
now rejects reuse. The paired `hub-centre-uv-frozen-20260921` tags preserve this state before paint.

The existing `verify_look_pass.py` passes with only CentrePlate added to its allowed object set.
`verify_centre.py`, called during preparation, compares every evaluated source mesh/empty against
the first-cut manifest: **all 100 other objects retain exact shape and position** (members in
`centre_proof.unchanged_members`). The replacement preserves the original track union outline and
deck levels. Seven top faces reconcile as two per Track_A/B/C plus one CentrePlate. Across all
21 pairs the largest intersection is `3.436146623982385e-07` square metres, below the `1e-5`
roundoff tolerance; the original overlapping boxes give `14.145081595145864` square metres in
the negative control. Original/new top union areas are `1333.1735664109221` /
`1333.173662046942` square metres, within the `0.001` comparison tolerance. No new top polygon
extends beyond the old union. Preparation preserves exact face boundaries through assembly,
all spot/surface transforms, and geometry through the scripted unwrap.

`verify_concept.py -- --body-only` on `TrainHub_prepaint.blend` passes all exported node/parent/
transform/face/UV comparisons and rejects deliberate UV and vertex mutations. Maximum UV delta
is zero; maximum geometry/transform component delta is `1.1920928955078125e-07`. Prepared faces
reconcile as **11,692 = 11,656 body + 36 retained glass**; only the body FBX is written this pass.
The new body UV fingerprint is `7cec91ae0c8e2a13189f7c848b9c9bd382deb1485fd339ed71db72ec108ddce4`;
glass retains `45ec462e67b7073ca83ddbba8326c5a8572b925e90f274d8463b94b197597620`.
The model is frozen again; another geometry/UV edit needs a new owner ruling. These proofs do
not replace the owner's in-game centre and day/night lighting check. Commands, HEAD, filters and
member lists are recorded in `export/concept/preparation_proof.json` and `verification.json`.

**Body-only relighting baked, 2026-09-21.** Both prepaint tags were read back before this bake:
assets `381fb1c`, OptInPack `df6ef4c`. From the assets blender folder,
`blender --background export/concept/TrainHub_prepaint.blend --python-exit-code 1 --python paint_concept.py`
at assets `381fb1c` plus the relighting implementation passed frozen geometry/UV guards before
and after painting. The prepared scene's body-only flag restricts output to the body's maps;
old glass maps/FBX and reactor output are not part of this delivery. The later reactor session
must regenerate its material-sampling UVs against the changed body atlas before import.

The same physical-coordinate approach path crosses both arms and the body track: paired outer
dashes become continuous converging strips, merge into one, and end at the portal. The floor
uses continuous radiating curves shared across the centre plate and adjoining tracks, with no
interior floor dashes. Centre lines were widened and antialiasing increased after inspecting
the first close preview. `render_concept.py` on `TrainHub_look.blend` produced day/night,
approach and centre views; the final centre and night images were inspected. Deferred entities
are hidden in these previews; there is no Blender stand-in for the vanilla reactor.

`python validate_concept_maps.py --body-only` passed raw TGA dimensions/channels, RM R/G agreement,
grey SI, blue BC alignment under lit SI and normal directions. Filter: body BC/NM/RM/SI only,
each 2048 square, **50,333,804 = 4 × 12,583,451 source bytes**. Full-mip DDS estimate:
**13,981,672 = 2,796,364 BC + 5,592,580 NM + 2,796,364 RM + 2,796,364 SI bytes**; this is not
an imported-file or packed-mod measurement. Map hashes are in `paint_proof.json`, reconciled
costs in `map_validation.json`. Re-running `export_prep.py -- --centre-candidate --body-only`
on the tracked workfile at assets `381fb1c` was rejected with "centre exception already consumed"
before export (`centre_closed_gate.log`). The earlier first-cut restore tags remain intact.

The editor-generated `SourceData/GFXMaterial/SMROptInTrainHub6.lua`, read at OptInPack `48d2cea`
plus the owner's pending import output, confirms BaseColor, Normal, RM and SI all point to the
canonical concept TGA files. This confirms SI slot availability, recorded in assets
`_shared/IMPORTER_FACTS.md`; it does not establish night-time glow acceptance. The owner next
reloads these map inputs and re-imports only the body using `blender/README.md`, then checks the
centre and lighting in their existing fixture. Their pending editor-generated files are
preserved and excluded from these source/documentation commits. No movement Lua changed.
Before the next import, the pending tracked dev-mod outputs plus every file under its Textures
folder were copied to `.git/session-backups/hub-first-import-20260921/` in OptInPack. Every copy
was SHA256-compared with its source; `manifest.json` records the source HEAD, filter, members,
sizes and hashes. This preserves the first imported appearance as well as the source restore
tags. The completed source/hand-off restore point is paired tag `hub-centre-lights-20260921`.
Executed model from the developer transcript: GPT-6; no more specific identifier supplied.

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

### The first concept import in game, MEASURED 2026-09-21

The owner's import of the rebuilt body and the first concept maps, read in a live session.

**The footprint is at radius 6, and that is the accepted state.** The game printed
`[TrainHubDev] SMROptInTrainHub6 line radii d0..d5 = 6 6 6 6 6 6`, and the connector spots in
`Entities/SMROptInTrainHub6.entjson` measure 6,000 units from centre on all six lines, z 800 —
consistent at 1,000 units per hex with the 4,000 units at radius 4 recorded on 2026-09-19. Tracing
the entity file: the connectors moved 4,000 → 6,000 at `d1beaba`, *the owner's import of the final
hub model*, which the owner accepted in game the same day (*"everything fits and nothing clips"*).
**So the stub direction above, which priced one more hex to radius 5, is superseded by the owner's
own acceptance of the final model at radius 6.** It is history, not an open item, and no ruling is
owed. Nothing in our Lua needs to change with it: `line_radii` (`20_TrainHub.lua:168-188`) reads
each line's radius from the model's own outline at runtime and `line_hex` places from that, so no
radius literal exists to update. `Station.lua:1105`'s 50 m teleport check is comfortable: it
measures the train against `Ramparrive`, not the connector.

⛔ **But the movement tunables were dialled in BEFORE the connectors moved, and were not re-judged
after.** `Floor.HubParkDistance` (11 m), `HubTransitionPauseDistance` (48 m) and
`HubExitSlideDistance` (50 m) are absolute distances from the hub's centre
(`20_TrainHub.lua:38-43,243-254`), so they did **not** follow the radius outward. `3722283`, the
last movement tuning, is an ancestor of `d1beaba`. The consequence is concrete: `Ramparrive` at
48 m used to sit **8 m outside** the connector at 40 m; it now sits **12 m inside** the connector at
60 m, so the approach the owner called *"99%, slight tuning before launch"* was judged on a
20 m-shorter run than the one that ships today. The movement smoke that `TRAIN_HUB_MOVE_high.md`
still owes must therefore be played at radius 6, and those three distances are the first things to
watch. MEASURED 2026-09-21; falsify with `git merge-base --is-ancestor 3722283 d1beaba` and the
connector radius at each revision of the entity file.

**The glow works, and it goes to zero rather than dimming.** `Building:OnSetWorking` calls
`WorkLightsOn()` → `SetSIModulation(200)` when working and `WorkLightsOff()` → `SetSIModulation(0)`
when not (`Lua/Buildings/Building.lua:1395-1420`, build 1.1.0.403908). Only entities carrying an
attach spot annotated `emissive` bypass this (`NightLightObjects.lua:512-518`), and the hub has
none, so its glow follows the working state exactly. Confirmed in game: powered and serving a train,
the SI lines are lit. This closes the open question of whether the hub's glow darkens when it stops
working — it does not darken, it extinguishes.

**The maps are correctly compiled and almost entirely unpainted.** The four DDS in the dev mod are
2048², 12 mips: BC `BC1_UNORM_SRGB`, NM `BC5_UNORM`, RM `BC1_UNORM`, SI `BC4_UNORM` — the
one-channel mask §9 already records. Vanilla's own `Station_BC`, `Station_CM` and `NewDomes_BC` in
`trainhub/reference/raw/` are the same 2048² BC1_UNORM_SRGB at 2.80 MB, so **format and resolution
match vanilla exactly and are not a limiter**. The content does not: sampling 42,025 points per
source TGA, BaseColor is **84.2% a single colour** RGB(176,194,209) with 563 distinct values,
Normal is **97.9% neutral** (128,128,255), RM holds **5 distinct values** with metalness 0
everywhere, and SI is 95.9% black. By compressed-block endpoints, 77.5% of our base colour is one
pair against 48.6% for vanilla's Station and 9% for NewDomes. The owner's read — *"this just looks
like blue paint"*, *"blurry … more like the first rough draft of a design step"* (2026-09-21) — is
what those numbers describe: a flat normal gives the lighting no surface to catch. The look pass's
next iteration is DEFERRED by the owner, 2026-09-21; the order when it resumes is the normal bake
first and alone, then RM metalness and roughness variation, then base-colour break-up, and texel
density measured only if blur survives all three.

**Restore points: five paired tags, and none carries a texture.** Both repos hold the same five,
all 2026-09-21, in this order by SMR-Assets commit: `hub-model-final-untextured` (`54eb84d`, final
geometry, before any look work) → `hub-prepaint-uv-frozen-20260921` (`69b23fc`, first UV freeze,
no paint) → `hub-look-first-cut-20260921` (`35cda1a`) → `hub-centre-uv-frozen-20260921`
(`381fb1c`, centre overlap removed, UVs refrozen) → `hub-centre-lights-20260921` (`09bd145`,
the imported state). **The UV base for any repaint is `hub-centre-uv-frozen-20260921`**;
`hub-prepaint-uv-frozen` says "no paint" but predates the centre fix and would bring the z-fight
back. `git ls-files trainhub/blender/textures/` is empty in SMR-Assets, so a rollback restores
geometry and UVs only: the TGAs in `textures/concept/` and the dev mod's DDS stay put and would
then be painted against UVs that no longer exist, with no error.

**Restore points now carry the textures (2026-09-21).** `snapshot_hub.py` (SMR-Assets
`trainhub/blender`, `python snapshot_hub.py <name>`) makes the paired tags and also copies the
git-ignored maps and the dev mod's compiled DDS, with a sha256 `MANIFEST.json` and a `RESTORE.md`,
into `B:\Dev\SMR\SMR-Shared\SMR-HubBackups\<name>`. Restore point 1 is `hub-road-b-20260921`
(road finish B, painted strips still on; 50 files, 153.6 MB, all 50 hashes re-verified). Restore
point 2, `hub-road-b-nostrips-20260921`, is taken by the lights agent after it strips the road
paint and the owner's importer run is verified. Commit before a snapshot: a tag on a dirty tree
holds nothing the owner meant to keep.

**GPU cost, sampled 2026-09-21 (`gpu_sample.ps1`, SMR-Assets `trainhub/blender`; log
`B:\Dev\SMR\SMR-Shared\SMR-HubBackups\vram_samples.jsonl`).** RTX 4080, the owner's monitor is
capped at 120 fps in the NVIDIA panel, so frame rate hides small costs and the game's 3D-engine
utilisation is logged too. Unconditioned readings (colony, camera and hub visibility not
confirmed): game dedicated 5,755 MB and 466 MB shared, stable to the megabyte over 20 s, and 3D
utilisation 87-88% at that view. **No real baseline exists yet.** The owner deferred it; the plan is
before the lights, `lights-off` against `lights-on` (hub off against on, same save and camera;
the lights brief makes off remove the lights), and again after the structure import, all from one
fixed save and camera, ideally uncapped for the runs. Expected, not measured: BaseColor 2048 to
4096 adds about 8 MB of raw DDS (2.8 to 11.2) against 5.7 GB, and lights cost frame time, not
VRAM.

**The AI texturing trial is CLOSED (owner, 2026-09-21).** The owner tried Tripo on the bare export
(`blender/export_for_texturing.py`, SMR-Assets `df9bb50`; GLB, OBJ and FBX in the gitignored
`export/for_texturing/`, with `MODEL_FACTS.json`) and it "gets confused and nothing useable comes
out of it" — the model is too big. That is the mesh-generating category already dropped on
2026-09-19; no tool was found. **The look goes by a scripted bake onto our own frozen UVs**
(`texture_hub.py` and the concept bake in SMR-Assets), never a painted or generated mesh. The
production source stays the tested `.blend` (`hub-centre-uv-frozen-20260921` for UVs); nothing
from the handoff below is a production export.

**The owner's visual handoff, 2026-09-21:** `C:\Users\stkot\Downloads\TrainHub_Visual_Handoff_v1\TrainHub_Visual_Handoff_v1`
(five images, `MATERIAL_SPEC.md`, `STYLE_PARAMETERS.json`, `ROUTE_GEOMETRY_SPEC.json`, an
implementation brief). The owner: it is *"better quality than the original ref concept"*.
**Reference only.** Usable: the warm off-white shell, the dark portal insert with a cyan ring, the
Y-merge route-light topology (two platform lines merge to one centred line at the portal),
`01_HUB_LOOK_TARGET.png` as the target. Not usable as written: its Blender Principled-BSDF
materials and clearcoat (the game takes BaseColor, Normal, RM and a one-channel SI mask on one
material, with no clearcoat channel) and its `Hub_VisualOverlay` geometry (the model is final and
frozen; the lights are painted into base colour and SI on the existing UVs). Its GLB is our own
export flattened (26,266 vertices against our 12,778 is the same 24,094 triangles split at UV
seams).

**Pad direction (owner, 2026-09-21):** the transport surfaces are to be *"a highly polished
metallic black, that's almost glass looking"*, not the package's gunmetal grey. The package's own
`maglev_pad` (#111A21, metallic 0.82, roughness 0.16) is what reads as gunmetal. UNTESTED proposal
for two variants to judge by eye: base about #05080B, roughness 0.04-0.08, and metalness 0-0.3
(dielectric, Fresnel sheen at the oblique camera) against near 1.0 (mirror). Whether the game's
shader reflects strongly enough for glass is not measured.

**Staged (owner, 2026-09-21), the owner inspects in game after each step:** 1. every road surface
(platforms, portal approaches, radial paths, centre) and nothing else; 2. the structure (shell,
rails, trim); 3. the cyan lights (portal ring, then route lines); 4. fine normal detail.

**Step 1 delivery, 2026-09-21 — assets `ea82ef4`, desk-verified; game look UNTESTED.**
Executed agent: Codex, GPT-6 as identified by the session instruction; an exact model variant
was not exposed in the transcript. No game launch or import was performed by this agent.

The current source is `paint_concept.py`, not the older `texture_hub.py`. Its imported-paint
selection is upward `Track_A/B/C` and `CentrePlate`, plus upward `Platform_*` above z=7.
That last predicate includes the support-post caps at z=7.4, so it is broader than the roads.
The new finish additionally requires `abs(z-8)<0.0001`. The face-set check reconciles **19 road
faces = 6 track tops + 12 outer platform tops + 1 centre top**; the track tops cover the portal
approaches and radial paths. Trim and light weights are preserved, including their antialias
blends; pure trim/lights, platform undersides, post caps and every other face are unchanged.
The first broad candidate failed the expected-face-set check and was not delivered. The
restriction uses existing face provenance, normals and elevation; no geometry/UV change.

`bake_pad.py` regenerates the old paint and both variants; `concept_guard.verify_scene()` runs
before and after each bake. UV SHA-256 remains
`7cec91ae0c8e2a13189f7c848b9c9bd382deb1485fd339ed71db72ec108ddce4`.
`validate_pad.py` compares the regenerated baseline against pinned pre-task hashes and the
original concept maps, then checks every output texel before publishing `textures/pad/`.
The pad influence mask has **129,815 texels = 127,955 covered + 1,860 island-padding texels**.
The padding follows the painter's existing four-pixel bleed; it never crosses a covered face.

Command: `python validate_pad.py`, run from `SMR-Assets/trainhub/blender` at `ea82ef4`.
Filter: BC/NM/RM/SI of the body only; selected road pigment and its existing bleed, excluding
pure trim/light coverage. Each row sums to the **4,194,304 texels** in its 2048-square map:

| Map | A changed | A unchanged | B changed | B unchanged | Changed outside pad, A / B |
|---|---:|---:|---:|---:|---:|
| BC | 128,001 | 4,066,303 | 128,001 | 4,066,303 | 0 / 0 |
| NM | 0 | 4,194,304 | 0 | 4,194,304 | 0 / 0 |
| RM | 129,708 | 4,064,596 | 129,721 | 4,064,583 | 0 / 0 |
| SI | 0 | 4,194,304 | 0 | 4,194,304 | 0 / 0 |

The named knobs in `paint_concept.py` are `PAD_BASE` (#05080B), `PAD_ROUGHNESS` (0.06),
`PAD_VARIANTS` (A_BlackGlass metalness 0.15; B_BlackMirror 0.95) and `PAD_DECK_Z` (8.0).
Unmixed RM bytes are (15,15,38) for A and (15,15,242) for B; unmixed BC is (5,8,11), with the
existing seam shading retained. Normal and SI are byte-identical to the pre-task originals.
The variants share BC/NM/SI, so switching costs one RM map. Names describe intent, not acceptance.

Compared both `export/pad/{A_BlackGlass,B_BlackMirror}/deck_day.png` and `deck_night.png`,
rendered with `render_concept.py -- --pad-preview <variant>` on each variant's `preview.blend`.
In this Blender lighting A has broader, lighter sheen; B stays darker with sharper surface
breaks; the distinction is smaller at night. These previews do not establish game reflections.
PowerShell reported Blender deprecation warnings as stderr errors; both renders wrote their
day/night outputs and completed normally. No geometry, lights, shell or runtime code was changed.

Owner handoff: `SMR-Assets/trainhub/blender/README.md`, **Owner import and comparison**, gives
five steps. Open existing material `SMROptInTrainHub6`; from `textures/pad/` choose
`SMROptInTrainHub6_BC.tga` in **BaseColor**, `_NM.tga` in **Normal**, `_SI.tga` in **SI**,
and `SMROptInTrainHub6_A_BlackGlass_RM.tga` in **RM**. Save material/mod and reload the existing
colony for day/night looks. Then change RM alone to `SMROptInTrainHub6_B_BlackMirror_RM.tga`
and compare the same views. ⛔ The importer run compiles the DDS, so each variant needs one (the
handoff's first text said no re-import; the owner's 16:07 import proved otherwise,
`_shared/IMPORTER_FACTS.md`, "Mod Editor pipeline"). The source maps and proof JSON are local,
ignored, reproducible outputs; `bake_pad.py` then `validate_pad.py` regenerates the delivery.
**Owner ruling, 2026-09-21 (OI-24): B (`B_BlackMirror`, metalness 0.95) is better than A**, whose
reflections were "very high". PROVISIONAL: the owner will revisit the road surface if the painted
glow lights make the reflections act up. What is locked is little: the finish is two maps
regenerated from `PAD_VARIANTS` in `paint_concept.py`, and a revisit costs one importer run.
Predicted, not measured, from the values: with base `#05080B` a metal takes its reflection colour
from a near-black base (about 0.2-0.3% head-on) where A's dielectric floor is 4%, so B is dimmer
head-on, which fits what the owner saw. Lead for the lights step, untested: the light strips keep
the deck's blends, so a bright base colour on metalness 0.95 would reflect that colour strongly;
give the strips their own RM texels and judge with the glow lit at night. Structure, lights and
fine normal remain later stages, and the full final-build battery remains owed.

**Lighting direction (owner, 2026-09-21):** the owner does not like the painted glow strips on the
tracks and platforms and wants **real lighting effects** there, in red or blue; the paint may be
revisited on the hub structure later. Read 2026-09-21, not yet run on a hub: the annotation route
takes only `warm`, `neutral`, `cool` (pale cyan), `orange` and `red` (`NightLightObjects.lua:14-20`)
and only at night, gated on the hub's working state (`Building.lua:1371-1394`); lights placed from
our own Lua take any colour with `SetColor` (`Mysteries/Fireflies.lua:85,109`;
`UI/PlanetScene.lua:178`) and are not tied to night. The painted strips' colour is one constant,
`BLUE` at `paint_concept.py:36`, and the SI mask carries no colour. The test: three reds and three
blues, one variant per arm, the owner choosing in game (`TRAIN_HUB_LIGHTS_medium.md`).

**Lights step, paint half, 2026-09-21 — assets `5dda4b6`, desk-verified; game look UNTESTED, the
owner's import is owed.** Executed agent: Claude Fable 5.1 (`claude-fable-5-1`). The knob is
`DECK_STRIPS` in `paint_concept.py`; `False` zeroes the glow on four face groups and nothing else:
the upward `Track_*`/`CentrePlate` tops (approach lines and floor curves), the upward `Platform_*`
tops (approach dashes), and the `Track_*` and `Platform_*` side rims (z 7.24 and 7.64). The brief
names the platform rims; the track side rim is removed with them as a painted strip on the tracks
(the owner's words), and is one line to bring back. Ring, portals, hoods, sidings, ribs and the
base line keep their glow. On the road the freed texels take finish B, so the road is plain
polished black. With the knob at `True`, `bake_pad.py` then `validate_pad.py` passed against the
pinned hashes, and all 5 files of `textures/pad/` match restore point 1's `MANIFEST.json` by
sha256 (0 of 5 differ), so the edit changes nothing that was delivered before.

Command: `python validate_nostrips.py`, from `SMR-Assets/trainhub/blender`, run on `451e5d7` plus
the working-tree edit committed unchanged as `5dda4b6`. Filter: BC/NM/RM/SI of the body against
the delivered `textures/pad/` set with the B RM; strip mask = removed glow > 0 plus its four-pixel
bleed, **66,653 texels** on **85 faces = 1 centre + 3 tracks × 8 + 12 platforms × 5**. Each row
sums to the 4,194,304 texels of its map:

| Map | Changed | Unchanged | Changed outside the strips |
|---|---:|---:|---:|
| BC | 66,627 | 4,127,677 | 0 |
| NM | 0 | 4,194,304 | 0 |
| RM | 25,421 | 4,168,883 | 0 |
| SI | 66,627 | 4,127,677 | 0 |

SI lit texels: 182,736 before = 116,109 kept + 66,627 removed; the validator also asserts no glow
on any road or strip texel and byte-equal SI everywhere else. The 26 mask texels that did not
change carried a glow too faint to move a byte. Delivery is `textures/nostrips/` (four maps,
standard names); the owner's five steps are `SMR-Assets/trainhub/blender/README.md`, "Owner
import". Out-of-scope finding: the reactor's `blue` sampling swatch is the median lit SI texel
and moves with this set; the deferred reactor pass already has to regenerate its UVs.

**Restore point 2: `hub-road-b-nostrips-20260921`** — paired tags at OptInPack `d0e5a37` (the
owner's editor output from the 17:25 import, BC/NM/RM/SI DDS all stamped 17:25:32, the material
pointing at `textures/nostrips/`) and assets `5dda4b6`; 54 files, 203.9 MB, in
`B:\Dev\SMR\SMR-Shared\SMR-HubBackups\hub-road-b-nostrips-20260921`. Strips off, no lights.

**Lights step, Lua half, 2026-09-21 — OptInPack `4e13ecb`; mocked lifecycle only, NOTHING SEEN IN
GAME YET.** Executed agent: Claude Fable 5.1 (`claude-fable-5-1`). In `20_TrainHub.lua`, one
block before `CreateElectricityElement`: `hub_light_variants` (the six looks),
`hub_light_arms` (local hex direction → variant, the one line per arm to reassign) and
`hub_light_rows` (the model's own edges from `hub_skeleton.py`: beam edge 1.75 m out from 8 to
64 m, platform outer border 5.16 m out from 40 to 80 m, both sides). Vanilla `PointLight` /
`SpotLight` (`CommonLua/Classes/Light.lua:11-120,278-304,456-476`, build 1.1.0.403908) attached
at the hub's Origin with computed offsets; no spot, persisted class, saved field or thread;
`DeleteOnLoadGame` and recreation from `GameInit`, `heal_after_load` and `OnSetWorking`, like the
reactor. **A stopped hub destroys every light** (`DoneObject`), it does not dim them. Lights are
set to detail class `Essential`, because a light's default, Eye Candy (`Light.lua:13-21`), can
drop out at low detail.

| Arm (local direction), found from the reactor | Variant | Class | RGB | Intensity | Radius | Spacing | Height | Lights |
|---|---|---|---|---:|---:|---:|---:|---:|
| 0, flanks the reactor, red flank | R1 Ember rail | point | 255,40,20 | 120 | 6 m | 8 m | 0.6 m | 28 |
| 1, flanks the reactor, blue flank | B1 Ice rail | point | 40,160,255 | 120 | 6 m | 8 m | 0.6 m | 28 |
| 2, next to the blue flank | R2 Crimson wash | spot 60/120 | 220,0,30 | 200 | 14 m | 16 m | 5 m | 14 |
| 3, opposite the red flank | B3 Cobalt beads | point | 90,110,255 | 255 | 3 m | 5 m | 0.3 m | 42 |
| 4, opposite the blue flank | R3 Rose beads | point | 255,60,90 | 255 | 3 m | 5 m | 0.3 m | 42 |
| 5, next to the red flank | B2 Deep blue wash | spot 60/120 | 0,40,255 | 200 | 14 m | 16 m | 5 m | 14 |

Total **168 = 2 × (28 + 14 + 42)**, asserted by `python tools/devmods/train_hub/tests/look_smoke.py`
(PASS at `d0e5a37` plus the working tree committed as `4e13ecb`; filter: the mocked visual
lifecycle, which also asserts 0 lights after hub off, no duplicates on repeat and the reactor and
foreign attachments untouched). The arms are named from the reactor, which stands between arms 0
and 1, because no source line fixes which world axis is north; the game log prints one
`[TrainHubDev] lights:` line per arm with the variant, count and engine bearing. UNVERIFIED and
owed to the design smoke: that a mod-placed light renders at all, that blue saturates, the spot's
aim (the code assumes a spot shines along its own +X and turns it a quarter about Y to face
down), daylight visibility, and frame cost.

**Owner direction after the first look, 2026-09-21: "my painted lines back, but acting as light
sources. Keep the six variants."** Thin emissive line paint restored on the tracks and platforms,
one colour per arm to match its variant, at a lower SI level "so it doesn't burn to white at
night"; the Lua lights small, low-intensity and spaced along the same line paths, "so the glow
spills onto the road around the line and does not wash the whole platform"; working-state gating
and hub-off removal kept; restore point 2 stays the clean fallback. The table above is the first
cut the owner judged, superseded by this one. Assets `ac600ba`, OptInPack `134bedd`; desk
and mock only, the owner's import and look are owed.

Paint: `DECK_STRIPS = 'thin'` in `paint_concept.py` — tops only (approach lines and dashes, one
pair of floor curves; side rims stay off), `THIN_WIDTH_SCALE` 0.65 of the old half-widths (0.5
left almost no full-strength core at this atlas's texel size), `THIN_SI` 0.35, `ARM_LINE_COLOUR`
keyed by the arm's game direction. Generator sector s is game arm (4 − s) mod 6, read off the
`Trackconnector1..6` spots in `Entities/SMROptInTrainHub6.entjson` (entity angle = 240° − generator
angle) with `hub_connector_directions`; the same spots put arm d at 60·d° in the hub's own frame,
which is what places the reactor (30°) between arms 0 and 1. Command: `python
validate_thinlines.py` from `SMR-Assets/trainhub/blender`, run on `5dda4b6` plus the working tree
committed as `ac600ba`; filter: BC/NM/RM/SI against `textures/nostrips/`, line mask = thin glow
> 0 plus bleed, **16,985 texels on the 19 road faces**, required inside the old strips' 66,653.
Changed / unchanged / outside the lines, each row summing to 4,194,304: BC 16,961 / 4,177,343 / 0;
NM 0 / 4,194,304 / 0; RM 15,155 / 4,179,149 / 0; SI 16,925 / 4,177,379 / 0. Core SI byte 89;
core texels by arm colour 572 + 662 + 570 + 578 + 622 + 678 = 3,682, all six present. Before it,
`validate_pad.py` and `validate_nostrips.py` passed again and the four `textures/nostrips/` hashes
did not move, so `True` and `False` still reproduce. Delivery `textures/thinlines/`; the owner's
five steps are the README's "Owner import".

Lua: the lights follow the painted path (`hub_line_v`, the painter's own smoothstep): one on the
arm's centre from 8 to 40 m, then a pair easing apart to 3.46 m by 60 m and straight to 80 m.

| Variant (arms as above) | Class | Intensity | Radius | Spacing | Height | Lights per arm |
|---|---|---:|---:|---:|---:|---:|
| R1 Ember rail / B1 Ice rail | point | 60 | 3 m | 6 m | 0.4 m | 20 |
| R2 Crimson wash / B2 Deep blue wash | spot 50/100 | 100 | 5 m | 10 m | 2 m | 12 |
| R3 Rose beads / B3 Cobalt beads | point | 120 | 1.5 m | 3 m | 0.3 m | 39 |

Total **142 = 2 × (20 + 12 + 39)**, asserted by `look_smoke.py` with the same lifecycle cases.
A variant's colour now lives in two places (the Lua table and `ARM_LINE_COLOUR`); reassigning an
arm's colour costs a rebake and an importer run, reassigning only its light style does not.
**Owner's look at the thin lines, 2026-09-21 (two screenshots, a blue arm):** the old paint's
"intensity is about right but its to white"; the thin set's "color it better but its intensity
isn't quite there". Read: the old line was SI 1.0 on `BLUE` (2,97,255), whose green burns toward
cyan-white; the thin line was SI 0.35 on a saturated arm colour. `THIN_SI` 0.35 → **0.7**, assets
`abd9684`; only the SI map moves (BC, NM and RM byte-identical to `ac600ba`'s delivery, core SI
byte 179, `validate_thinlines.py` PASS, 0 texels outside the lines). UNTESTED in game; whether the
less saturated arms (B1, B3, R3) whiten at 0.7 is the owner's look. Lua unchanged.
**Owner, 2026-09-21, after importing SI 0.7 (SI DDS 18:05): "I think that might be the winner can
you do that for all lines and let me take a look."** PROVISIONAL pick, not a ruling. Which arm:
INFERRED as **B3 Cobalt beads** from the second screenshot — saturated line pixels (b > 220,
r < 100, g < 110; 5,684 of them) have median RGB (58,77,225), r/g 0.75, against B3's 0.82, B1's
0.25 and B2's 0; the shot shows no reactor beside the arm, which also rules out B1. If that read
is wrong, `ARM_LINE_WINNER` and the six `hub_light_arms` lines are the fix. Assets `43eafe4`:
`ARM_LINE_WINNER = 3` puts cobalt (90,110,255) at SI 0.7 on every arm (`validate_thinlines.py`
PASS, 3,595 core texels, one colour, 0 outside the lines). Because "all lines" can stop at the
arms or take in the structure, a second set `textures/thinlines_all/` also recolours and levels
the ring, portal, hood, siding, rib and base glow (`STRUCTURE_LINES`; BC and SI only, same
shapes): `python validate_thinlines_all.py` against `textures/thinlines/`, mask = lit texels grown
one texel outside the arm lines, 171,516 texels; BC changed 115,966, SI 115,872, NM and RM 0, 0
outside the mask, SI ceiling 179. That set edits structure glow, which
`Train_Hub_Project/01_TRAIN_HUB_STRUCTURE_high.md` also owns: whoever fires it starts from the owner's choice here.
OptInPack `29101e8`: all six arms carry B3's light style, **234 lights = 6 × 39**, up from 142
(the beads are the densest style). The pad and strips-off sets rebake unchanged.
**Correction, owner, 2026-09-21: B3 "was the wrong blue, it was the other blue that i wanted",
with its "lighting intensity slightly bumped".** The inference above failed: the pixel test split
B1 from the rest but could not split B2 from B3 once bloom and ambient lift a saturated line's
red and green together; read the pick from the owner, not from a screenshot. "The other blue" is
taken as **B2 Deep blue wash** (0,40,255), the only other blue the same pixels allow. Assets
`a93a143`: `ARM_LINE_WINNER = 5`; both validators PASS again (arms: 3,595 core texels, one
colour, 0 outside the lines; structure set: BC 115,783 and SI 115,872 changed, NM and RM 0, 0
outside the mask, SI ceiling 179). OptInPack `bbfec1a`: all six arms carry B2's spots, intensity
100 → 130 (R2 keeps 100), **72 lights = 6 × 12**, down from 234. The spot's aim is still the
unverified +X assumption; the owner's look at B2's arm is the only evidence it lands on the deck.
**Owner, 2026-09-21: "we are good here for the moment". Restore point 3:
`hub-lines-b2-lights-20260921`** — paired tags at OptInPack `ea68b2c` (the owner's editor output,
material pointing at `textures/thinlines_all/`; BC DDS 18:38, after the 18:35 B2 bake; NM, RM and
SI DDS 18:32, from the cobalt import, whose NM, RM and SI do not depend on line colour) and assets
`a93a143`; 62 files, 304.6 MB, in
`B:\Dev\SMR\SMR-Shared\SMR-HubBackups\hub-lines-b2-lights-20260921`. State held: road finish B,
thin deep blue (0,40,255) lines at SI 0.7 on every arm, the structure's glow lines matched, 72 B2
spots at intensity 130 along the lines. "Good for the moment" is the owner's hold, not a final
acceptance; restore point 2 remains the clean fallback. Still owed: the hub off/on cost, a
daylight look, and the both-configuration and toggle ship tests on the final build.
**Owner, 2026-09-21, on the cost reading: "we should finish the model update and get its lighting
done to test the gpu part because right now we would just be testing the tracks."** The hub off
against on reading is DEFERRED to the whole hub: structure maps, then the structure's own lights,
then one reading. `Train_Hub_Project/01_TRAIN_HUB_STRUCTURE_high.md` carries all three and starts from restore point 3.
**Hub off against on cost: <<PENDING-RUN>>** — the owner's reading, same save and fixed camera,
no trains in view; frame rate first, `gpu_sample.ps1` for GPU memory and 3D utilisation.

**Structure step, the blur measured before the bake, 2026-09-21 — assets `3be561d`.** Executed
agent: Claude Fable 5.1 (`claude-fable-5-1`). Two read-only scripts in SMR-Assets
`trainhub/blender`. `measure_density.py` (Blender, on `TrainHub_prepaint.blend`; filter: body loop
triangles by provenance group, road tops split from sides) finds every group at **6.7-7.3 texels
per metre** at 2048 (Ring 6.91, Rib 6.70, Hub_Portals 6.88, Hood 6.80, Track_top 7.34; worst-axis
medians 6.5-7.3), so a texel is about 13.6 cm and the frozen atlas is **25.48% covered**
(1,067,453 texels). `measure_dds.py` (Pillow, the DDS relabelled from DXGI 72 to 71 in memory)
compares the dev mod's compiled DDS with `textures/thinlines_all/`: BC mean error on the ring
0.99/255 with 6.2% of texels moved by more than 4; NM byte-equal in R and G to a mean 0.03; SI
mean 0.22. **The ring seam, per image row inside the ring island with the lit strip excluded, is a
4-texel-wide dip of median depth 33 on a hull luma of 193 (17%) in the source and 4 texels, depth
32, in the compiled copy.** The script draws it 2 × 0.05/33.5 rad wide, about 0.09 m at the ring,
under one texel, and the antialias term (0.55 of a texel's world size) spreads it into that soft
band; the 25% core darkening is never reached. **Density limits the look, not block
compression**; supersampling sharpens a seam's edge but cannot add texels to a face, so BaseColor
goes to 4096 as the owner planned. The owner's seam screenshots are not on disk (they were pasted
in chat), so the seam-spacing check against the script (the ring's period is 6/33.5 rad, 10.26°)
is not done; the profile stands without it.

**Structure step, maps delivered, 2026-09-21 — assets `a2b9727`, desk-verified; game look
UNTESTED, the owner's import is owed.** Built by an Opus agent (`claude-opus-5`) on a brief from
the orchestrator (Claude Fable 5.1), who reran every validator and compared the hashes.
`paint_concept.py`: `MAP_SIZE` per map, `SUPERSAMPLE = 2` (four sub-texel samples per texel, the
antialias term .55 → .30 of a texel), seam knobs in metres, `STRUCTURE_LOOK` (the handoff palette:
shell `#D9D4CA` .31/.05 on ring, ribs, portals, hoods and hull sides; silver `#AEB9BE` .22/.90 on
pillars, ring pillars, clamps and siding frames; insert `#071016` .20/.55 in the portal trim band;
±2.5% per-panel tone, ring panel lines at z 7.40 and 8.30, ±.03 brushed roughness on the silver,
no grime). Every knob defaults to legacy: `bake_pad.py`, `bake_thinlines.py` and their validators
PASS and all 13 held TGAs are sha256-identical. `bake_structure.py` (57.8 s) bakes **BC 4096, NM,
RM and SI 2048** into `export/structure/`; ring seam 0.20 m wide, 18% deep, groove 0.02 m; road
seams keep their widths. `python validate_structure.py` PASS, 0 failures, publishes
`textures/structure/`. Filter: the painter's own road mask (full pad and pigment weight). Road:
at 4096, pad 516,184 = 450,348 finish + 12,860 seam + 52,976 partial, **0 finish texels off
`PAD_BASE`**, 0 seam texels off the formula; at 2048, 135,162 = 107,384 + 4,212 + 23,566, **0 RM
texels off (15,15,242)**, 0 lit. Against the held set the finish is 110,312 → 107,384, the 2,928
lost all on its own one-texel boundary, none gained; on the common 107,384: BC 0, RM 0, SI 0, NM
229 changed (a groove's slope reaching one texel). Glow: SI ceiling 179 held, 104,268 texels
exactly (0,40,255), road lit 15,496 → 15,716; per-group SI sums within ±1% on ring, portals,
hoods, sidings and road, +10% pillars, **Rib +33%** (`RIB_GLOW_LEVEL` .75 → 1.0 so the bands
reach the line level: 0 → 370 core runs, median 4 texels). Crispness: ring seam dark run 4 texels
at 2048 → 2 at 4096. Changed against the held set at 2048: BC 1,829,430, RM 1,596,139, SI
90,832, NM 86,493 of 4,194,304; `Bay_*` re-antialiases (BC 28,177, NM 32,317) without redesign.
Owner's five steps: `SMR-Assets/trainhub/blender/README.md`, "Current handoff: structure set";
the compiled BC DDS grows to about 11 MB. Previews `export/structure/{day,night,deck_day,deck_night}.png`
are Blender only.

**Structure pass 1 in game, the owner's look, 2026-09-21.** The owner imported `a2b9727`
(dev mod checkpoint `5f7ee27`: all four slots on `textures/structure/`, BC 4096 BC1 with 13 mips
at 11,184,972 B, NM/RM/SI 2048, import log OK) and sent close-ups of the pillars, a rib, a portal and
the ring. The palette reads as materials, not blue paint; the deep blue line is clean. **Owner
ruling: yes to all four fixes** — SI to 4096 with antialiased rib bands, NM to 4096 for one clean
ring groove, brushed rather than chrome silver, a hard portal insert edge — and on the ring seams:
*"can we design over them to make it less noticeable if that doesn't work, put something there
thats not a hairline seem"*, then *"Or just make it solid no seem?"* — solid is the default if a
crisp groove does not hold, the designed feature offered beside it. Pass 1 is not kept; it is snapshotted as `hub-structure-pass1-20260921`
before pass 2. The pass 2 brief is `prompts/Train_Hub_Project/01_TRAIN_HUB_STRUCTURE_high.md`
§"Pass 2". Read from screenshots by the orchestrator, not measured.

**Restore point pass 1: `hub-structure-pass1-20260921`** — paired tags at OptInPack `5f7ee27`
and assets `c8f1847` (`snapshot_hub.py` now carries `textures/structure/`); 66 files, 401.0 MB.
The material carried BC 4096 with NM/RM/SI 2048, so stop 1 (one material, mixed sizes) did not
fire.

**Structure pass 2, maps delivered, 2026-09-21 — assets `cb60471`, desk-verified; game look
UNTESTED, the owner's import is owed.** Built by the same Opus agent; validators rerun and hashes
compared by the orchestrator (`python validate_structure.py` PASS, 0 failures; the 13 held TGAs
byte-identical). **BC, NM and SI at 4096, RM at 2048** (TGA 3 × 50,332,187 + 12,583,451 B; DDS
expected about 11 + 22 + 11 + 2.8 MB). Per fix: (1) rib bands: `RIB_GLOW_SHARP` 2.0, edge ramp
1.2 texels; on the Rib island 744 core runs, median 7 texels, 1,154 edge-ramp runs, median 4
(pass 1: 370 / 4 and a 0.24-texel step). (2) Ring seams: relief is a one-sided 0.02 m plate step
inside the 0.20 m seam (`SEAM_RELIEF_RING = 'step'`; `RING_SEAM_SECTORS = 36`, was 35.08, so
plate parity closes on the branch cut; spacing 5.85 m); at 4096, ring texels with lit ones and two
around excluded: 10,665 dark colour runs, median 2 texels, p90 depth 26 of hull 209; **0 light
runs; 526 slope runs, 0 paired with an opposite slope, 525 on a dark run** — the one-line seam
holds by the stated measure and ships as the default; a solid candidate (0 dark, 0 slope runs) is
baked at `export/structure_solid/` for one import if the owner wants it. The owner's lead
measured: 4,755 of 34,517 dark-line texels lie within 2 texels of a ring UV-island boundary and
1,827 of the ring's 42,808 padding texels carry the seam's dark into the bleed, a real mechanism
for the blue line's step at a seam under bilinear filtering; unchanged by this pass. The designed
seam feature (a 0.45 m silver joint strap with a 0.20 m channel and the step at its leading edge,
one `band()` per ring texel) is described, not built, for the owner's pick. (3) Silver roughness
.22 → .40, metalness .90 → .75, brush ±.03 kept. (4) Portal insert edge one 4096 texel
(`INSERT_EDGE` .0224 arch units), widened 0.15 m: fringe runs touching the insert median 1 texel,
p90 2 (pass 1: 2 / 9); the insert and shell share an island, so no cross-island bleed. **The arch
sawtooth is the frozen geometry**: Hood arches are 15-facet polylines (11.9° a facet), Hub_Portals'
arch band is 201 Tripo faces at 159 distinct angles; the maps cannot remove it; left alone. Road:
450,348 finish texels at 4096, 0 off `PAD_BASE`, 0 lit; 0 RM texels off (15,15,242); NM 298 road
texels changed by a seam's slope. Line colour exact on 67,525 core texels, SI ceiling 179. Glow
assert now checks each group's peak SI level (179; 71 base line) and its total within 15% (30% on
the base-line groups, whose 0.15 m band lies along texel rows and converges with sampling: Pillar
164,695 → 180,858 → 204,707 across held, pass 1, pass 2 at peak 71 throughout). Owner's steps:
README "Current handoff: structure set"; one import, four slots.

**Structure pass 2 in game, the owner's look, 2026-09-21, and the UV ruling.** Three close-ups: the
portal insert edge and arch line jagged, blurry and asymmetric; rib and pillar bands torn; the
black-glass road and its borders "seamless, nearly perfect", the quality wanted over the whole
model. Read by the orchestrator (not measured in game): the road's borders are mesh edges and its
lines run along the track island's texel rows; the structure's features are painted curves across
the grid at 14 texels/m, about 14 px a texel at that zoom, on a 25.48%-covered atlas over a
faceted Tripo surface (the analytic arch wanders against it). **Owner ruling, 2026-09-21: the UV
freeze is lifted for one full, comprehensive pass — uniform quality over every bit of the model,
"so we can texture, paint, light and zoom and it looks clean with no jagged edges or blurred
pixels."** Geometry and spots stay frozen; the UV contract is re-frozen after the pass. Bounded for
the owner: the target is the road's quality at the inspection zoom everywhere, not any zoom. The
2048 held sets become historical at their tags. Brief: `01_TRAIN_HUB_STRUCTURE_high.md` §"Pass 3".
**Owner, same sitting: the floor plate goes in before the UV freeze** — the 2026-09-20 floor
decision above was never built (`hub_skeleton.py` has no plate; the model freeze came after it).
One geometry change: `FloorPlate`, the beds and `Box1` spots rising by its thickness, every
other object's digest unchanged. Restore point `hub-structure-pass2-20260921` (OptInPack
`d6d1a1f`, the pass 2 import checkpoint, assets `cb60471`; 66 files, 501.7 MB) holds
the state before the floor and the UV pass.

**Floor plate built, 2026-09-21 — assets `e9e6f3c`, desk-verified; game look UNTESTED.** Built by
an Opus agent; guards and validator rerun by the orchestrator. `FloorPlate` in `hub_skeleton.py`:
144-gon, radius 31.35 m (ring wall inner 31.65 less 0.30), thickness `FLOOR_T` 0.30 m (the beds'
own kerb height), top and rim only, no collider (`Collision`, `hex_shape`, `Selection` FBX nodes
byte-identical). `Bay_1..6` and their `-Box` spots rise 0.30 m (FBX `-Box` z 0.5 → 0.8). Proof
`verify_floor_pass.py` against `floor_pass_baseline.json` (the work file at
`hub-structure-pass2-20260921`): 98 objects, 86 byte-identical, 1 added, 12 risen by exactly
0.30; source digests 92 of 92 untouched equal; old freeze kept as `concept_freeze_pass2.json`.
Clearances (BVH, both directions): ring wall 5.66 m, portal legs 4.88, hoods 7.93, ring-pillar
feet 0.155; the seven centre pillars pass through, the six beds stand on it; each bed's outer
corner overhangs the edge by ≤ 0.083 m (reported, not fixed: covering it eats the pillar
clearance). Paint: `#E4E0D8` (.35/.05), per-hex tone ±1.2%, hex relief on the game's pointy-top
lattice at 2.0 m pitch (a fifth of a hex), 0.60 m `#071016` trim, a 0.15 m (0,40,255) strip at
`THIN_SI` just inside it — **offered; the owner picks the strip's colour**. The Bay cube grid is
removed (no beam or stub ever carried a hex pattern). `validate_structure.py` PASS on the new
atlas by value (0 road-finish texels off, ceiling 179, 64,305 core texels exactly the line
colour; FloorPlate 635,340 texels at 4096, shell luma median 222 against the beds' 14). Adopted
for the pass, owner's latitude 2026-09-21 ("anything else … feel free to adopt"): smooth shading
by angle on the curved parts (normals only; the owner's look says whether the engine takes
them), a baked AO/bevel layer in the structure rebake, and a two-atlas deck/structure split held
back until the repack's density is seen.

**UV pass delivered, 2026-09-22 — assets `3d5c11e`, desk-verified; game look UNTESTED, the
owner's mesh-and-maps import is owed.** Built by an Opus agent; guards, validator and proofs
rerun by the orchestrator. `reunwrap_hub.py`: per-group unwrap (ring and every tube unrolled
straight, lids axis-aligned, floor top planar with a polar rim so the rim strip is one texel row,
portals creased at 20°, the knee of a 60→12° sweep), a deterministic skyline packer replacing
`uv.pack_islands` (which filled 22% and is not build-stable): one uniform scale, 90° turns only,
2 texels between a part's own islands, 18 between blocks (an 8-texel bleed each side + 2), 128
strip cuts, 155 blocks. Body atlas at 4096 (`measure_uv_quality.py`, `export/uv/before.json` →
`after.json`): **density 13.76 → 19.17 texels/m**, spread 9.0% → **4.2%** (19.04-19.85),
**coverage 27.68% → 53.66%**, overlap 0, islands 2,018 → 2,603; straightness within 2° of a UV
axis: tracks, sidings, centre plate 100%, pillars/ring pillars 92 → 100%, clamps 84 → 100%, hoods
60 → 81%, ring 37 → 74% (median 5.32° → 0.64°, max 6.56°, the lathe's own step), floor rim 0.00°;
portals' worst-axis p01 1.21 → 18.85/m. Glass: own atlas, 65% covered, 100% straight. Two
targets not met, measured: coverage < 75% (islands fill boxes 83%, boxes fill padded blocks 69%
— the 18-texel margin — blocks fill the square 93.65%; the margin is the only lever and stays);
ribs 9.9% straight because a band is a level set of world radius on an inclined tube (2.2-41.1°
at the five band radii), unfixable by unwrapping. No face boundary exists at the portal opening
(`probe_portal_opening.py`), so the arch line stays analytic. Smooth-by-angle 35° on portals,
hoods, ring, ribs, pillars, clamps and the floor rim (10,256 of 12,970 faces); the painter's
tangent frame uses face normals, so the bake is unaffected. Proofs: geometry digests 32 of 32
unchanged (`verify_uv_pass.py`), FBX reimport 30 objects with zero vertex and transform drift,
UVs and normals the only difference (`verify_fbx_reimport.py`, glass too), fingerprint
`9eb1dc9a…` reproduced by a plain run and by a from-scratch rebuild, `validate_structure.py` PASS
with no check weakened. `textures/pad|nostrips|thinlines*` are historical at
`hub-structure-pass2-20260921`. Owner's steps: README "Current handoff: the comprehensive UV pass"
— the material is unchanged; run the Body import procedure in full (the Importer re-reads the
FBX and recompiles all four DDS), save, reload.

**The owner's look at the UV pass, 2026-09-22: "the hub's quality is much better now, the only
thing that still doesn't look up to spec is the paint."** Restore point
`hub-uv-refrozen-20260922` — paired tags at OptInPack `543504f`, the checkpoint of the 00:44
mesh-and-maps import (entjson, `Meshes/*.hgrm`, metadata) and assets `3d5c11e`; 66 files,
501.8 MB. The paint pass is next (AO/bevel bake, panelisation, decals, roughness variety, small
emissives — proposed, the owner's screenshot and decal call awaited). A trim-sheet material for
the metal parts is possible (the importer assigns a material per mesh object, as the glass
shows) and unmeasured on this pipeline; proposed as the paint pass's first unit behind a test
import. **Then, with four close-ups: the portals.** Owner: *"we need our train tunnels / portals
… some of the rims are broken. I mostly want them to look clean, have a nice transition /
entrance, and look clean."* Read by the orchestrator: every defect is the Tripo mesh (the collar
strap splits at the crown, the hood is a separate piece inside the arch, the side silhouette is a
keyhole), not paint. **Ruling, owner, 2026-09-22: the portals are open to redesign.** Route: a
generated portal in `hub_skeleton.py` (flared collar from one continuous profile, recessed
throat with a hard-edged dark band, lip bevel, blue line on the lip, buttresses into the ring,
hood merged into the liner), opening size and position unchanged, spots untouched; two
candidates (arch mouth / rounded-rect mouth) rendered from the owner's four angles for the pick
before any export; then unwrap, one more re-freeze, bake, one import.
Candidates delivered, assets `74efbad` (`PORTAL_STYLE` None by default; renders
`export/portal_candidates/{A,B}_view1..4.png`, `NOTES.md`): one profile swept round the opening
(throat, `PortalFrame_*` door rebate, collar with a 0.15 m lip bevel for the line, sill,
buttresses); changed object `Hub_Portals` only (six Tripo collars and twelve straps removed, track
beds and stub pylons kept), 104 others byte-identical. **Today's Tripo portal is 118 mm inside
the measured 4.16 × 4.36 m train's roof corner**; both candidates clear it; only B clears a
5 m tall train (+0.125 m). Door plane at 34.75 m from the centre, clear 6.50 × 5.125 m over the
deck, rebate 7.10 m wide, 0.40 m deep, 0.30 m lip overlap. Hoods untouched, so the hood's
arched bore is the tightest point behind B (+0.023 m); on a B pick the hood takes the same bore.
The orchestrator recommends B. The owner's pick is owed.
**Portal doors (owner, 2026-09-22):** reuse a vanilla animated door, scaled — brief
`Train_Hub_Project/05_TRAIN_HUB_DOORS_high.md`, survey `VANILLA_DOOR_ENTITIES_20260922.md`
(every Door-class entity measured from `entities.dat`; none fills a 6.5 × 13 m arch, scale is
uniform; `ElevatorSurfaceDoor` 19.46 × 12.93 m and `TunnelEntranceDoor` 20.0 × 6.66 m at 33% are
the two to look at; the owner's screenshot is the Elevator's surface door, not the Space
Elevator's 2.85 m hatch). The door plane follows the owner's pick.
**Repair-drone hangar (owner, 2026-09-22):** a pit like the Shuttle Hub's, for the Wasps to
launch from and land into, instead of a recoloured recharger; the tower unwanted. **Ruling: route
1, a pit modelled into the hub's own floor plate**, built now so it lands in the same re-freeze
and bake as the portal. Feasibility read owed: `SHUTTLE_HUB_PIT_20260922.md` (how the pit renders
below ground, whether a mod entity can do the same, the Wasps' launch and land states).
**Pit survey delivered (`bf468f3`) and probed in game, 2026-09-22 (owner's console, read from
`Mars.exe-20260922-00.44.52` log lines 683-730):** no pit entity exists — `ShuttleHub`,
`ShuttleHubCP3`, `JumperShuttleHub` are one mesh each (measured z −40.22 to +38.80 m, no
animation files); the shaft renders because the entity carries an `eTerrainHole` surface. MEASURED:
`const.SurfaceTypes` lists `terrain_hole`; `EntitySurfaces.TerrainHole = 64`; `HasAnySurfaces`
with it is true for `ShuttleHub`, `ShuttleHubCP3`, `MetalsExtractor` and **false for `SolarPanel`**
(the control). So our own pit, modelled into the floor plate with a `TerrainHole` surface node
over the mouth, is the route (the entity already declares 796 surfaces in three types through the
same importer). The survey's "Wasp shaft states 26.7 m down" is WRONG: in game `DroneMaintenance`
and `DroneJapanFlying` both carry `metalMineEnter/Idle/Exit` (exit 2,533 ms) but the box is a
15 m *sideways* run at ground level (`(-138,-121,25)-(1342,118,301)` for the Wasp) — a mine-mouth
exit, not a descent. The drone's rise and descent are therefore scripted lifts (`SetPos` with a
duration, as the generic shuttle lead-in does); vanilla flight and landing are pinned to the
terrain height grid, so the hand-over to the drone AI is at the rim. Owner's pit spec: circular,
about 11-12 m across ("fit in 3 hexes"), oversized to the Wasp for depth, in a clear wedge of the
floor; built into the floor plate before the final re-freeze.
**Portal doors built (brief 05, OptInPack `1a7381f`, by a peer session; mocked only):** the
owner's five-minute look picked `MarsAssembly_Door_01`, a parting glass pair, at scale 184 on
the rebuilt portal's door plane (34.75 m), reversed to read solid from outside; second style
`shutter` (`TunnelEntranceDoor` at 81) by console. A door opens while a train body is within
20 m outside / 5 m inside the plane on that portal's line and closes 1.5 s after the doorway
empties; `look_smoke.py` PASS. The portal's mouth is being shaped to that pair by agreement
between the two sessions for the owner's morning review.
**Owner ruling, 2026-09-22 (via session 1d, the doors brief): "I would like the portals opening
to not move, and the track … I would prefer it not get taller but it could get wider … it
absolutely cannot get shorter (the opening)."** Agreement between sessions 2e (portal) and 1d
(doors), 02:30: the clear opening stays 6.50 × 5.125 m over the deck; the glass pair (closed 7.40
wide × 9.90 tall × 0.48 thick at scale 184; each leaf slides 3.1-3.4 m sideways and up to 1.67 m
inward, no rise) hides inside the collar as a pocket door. Numbers, hub frame: **sink 1.85 m**
(leaf z 6.15-16.18; collar top 16.50 unchanged), **leaf outer face x 35.10** (centre 34.86;
`PORTAL_DOOR_X` 34.75 stays the plane's name), **pocket cavity** x 33.10-35.15, y ±7.50, z
5.90-16.25 open to the mouth only behind the 0.30 lip, **collar shoulders** full height to |y| =
8.00 (a ~16 m gatehouse block round the rounded-rect mouth, the bell only above and outside it),
**sill** thickened to z 5.90 across the collar so the sunk leaves and the track beam are inside
it. The shutter style (16.2 m wide, drops 5.07 m) is not designed for; it stays a dev-only
console style. Leaves hidden in the pockets is both sessions' recommendation; **the owner's
morning call: hidden or visible.** Constants to share by name: `PORTAL_DOOR_FACE_X`,
`PORTAL_DOOR_SINK`, `PORTAL_POCKET_*`; a door rescale re-runs the portal parametrically.
The doors' side landed at OptInPack `8aef5de` (`Floor.HubDoorFaceX = 3510`, `HubDoorSink = 185`).
**Pit built as a candidate, 2026-09-22 — assets `4f86f1a`, `PIT_ON` default off; desk-verified.**
Built by an Opus agent. `PIT_R` 5.75 m (11.50 across, `HEX/√3`), `PIT_D` 11.547 m on the 30°
midline (the three-hex corner of generator hexes (1,0)/(0,1)/(1,1), and the one radius where the
centre pillar and the two 20 m line pillars are equidistant: 3.70 m at the mouth, 3.10 at the
kerb — the ≥3.5 m asked for is met at the mouth, not the kerb, and 3.10 is the maximum for this
size), `PIT_DEPTH` 20 m, kerb 0.30 × 0.60, three ledge bands, six posts, `terrain_hole` node r
6.05 m at z 0, spots `-Pitfloor` (z −20) and `-Pitrim` (z 0.30). `FloorPlate` the only existing
object changed (top area 2983.0757 m² = 144-gon minus mouth), 104 of 105 byte-identical; the
importer needs one selector (`'name', "terrain_hole", 'SurfaceType', "terrain_hole"`), and
`prepare_concept.py` `SURFACES` gains `'terrain_hole'` at export. **Finding for the owner: the
deck roofs 73.6% of the mouth** (1,254 rays up: `SidingPanel_1` 532, `Siding_1` 142, `Track_A`
132, `Track_B` 117; lowest roof 6.19 m over the kerb), and the wedge is six-fold symmetric, so no
radius on a midline escapes: an 11.5 m mouth cannot fit the ~2.7 m gap between two siding decks
at any radius inside the beds. The shaft reads from above only from bearings 20-90°
(`export/pit_candidates/pit_top.png` against `pit_top_floor.png`). **Owner's morning call:**
accept a hangar under the deck (drones fly out under 6 m of headroom; the mouth shows at a
slant), or shorten a siding's inner end to open the wedge (siding geometry, parking length), or
a smaller pit.
**AO and bevel layer built, 2026-09-22 — assets `2fb01e7`, desk-verified.** Built by an Opus
agent; validator rerun by the orchestrator (PASS, 0 failures). `bake_ao.py` (47 s on OPTIX):
AO at 2.5 m / 192 rays, a 0.08 m bevel normal, a curvature map, to the atlas at 4096, 16-bit
PNGs hashed with the UV fingerprint in `export/ao/ao_proof.json` (three runs give three sha256
— OPTIX reduction order — so the layer is a recorded input, and the painter refuses one whose
fingerprint does not match the blend). Composited on non-road, non-lit texels only: AO × .35 in
linear light, edge light .06 (held off the portal inserts and floor trim by the painter's own
trim weight), cavity roughness +.08 / edge −.04, bevel normal blended reoriented at 1.0; the
tangent frame measured against an object-space control (mean error 0.0001, no flip). Proofs:
with `AO_LAYER` off all eight structure TGAs reproduce their pre-change sha256; with it on SI is
byte-identical (`30853f0966db0cca`) and 0 road or lit texels are reached; 9,972,166 eligible
texels, mean AO 0.679, 3,650,654 darkened > 10%, 3,094,496 lightened by the edge. The ring
one-line seam check subtracts the solid variant's bevel slopes (14,218) as its baseline: 1,957
seam runs, 0 paired, still holds. Whether it reads as premium in game is untested.
**Portal B finalised, 2026-09-22 — assets `2ef2bfb`, desk-verified.** Built by an Opus agent.
Constants from the door at 184 (`PORTAL_DOOR_FACE_X` 35.10, `PORTAL_DOOR_SINK` 1.85, leaf 7.40 ×
9.90 × 0.48, slide 3.40; `pocket_box`/`shoulder_box`/`leaf_boxes` derive every plane, so a
rescale re-runs the pocket). `PORTAL_SHOULDERS`: a 16.00 × 16.50 × 2.50 m gatehouse block round
the rounded-rect mouth with a 0.20 m front chamfer (the bell is inside it and is not built),
pocket cavity x 33.10-35.15 / y ±7.50 / z 5.90-16.25, sill underside 5.80 (the ring's own),
crown 16.50 asserted; `HOOD_BORE = 'portal'` rebores the hoods; the twelve buttresses go (the
block subsumes them; the ring's rim dies on its flat wall). Changed: `Hub_Portals`, `Hood_1..6`,
`FloorPlate`; 97 byte-identical; knobs off reproduce 104 of 104. Clearance through the whole
tunnel: the measured 4.16 × 4.36 m train +0.748 m (was −0.118), a 4.0 × 5.0 m train +0.104 —
the first build that clears it. Pocket containment measured by BVH: closed pair ≥ 0.05 m, open
pair ≥ 0.05 m. The doors session corrected its inward figure: the open leaf's innermost x is
33.19 (1.43 m inward of the closed inner face 34.62, measured in game from the opening-state
box), 0.09 m inside the 33.10 back wall, so the pocket holds the whole envelope. **Finding for
the owner: the ring wall stands inside the pocket's lowest 1.10 m** (26 vertices, up to z 9.10,
|y| 7.01) — invisible from the mouth, possibly visible through the see-through glass from the
hub side; a notch in the ring's outer shoulder is the fix and needs a ruling. `prepare_concept`
`SURFACES` gains `terrain_hole`; `reunwrap_hub.SMOOTH_PARTS` gains the pit and portal sweeps.
Renders `export/portal_candidates/B_view1..5.png`, `B_doors_closed.png`, `B_doors_open.png`.
**Production pipeline run, 2026-09-22 04:06 — assets `2f4b782` (+ `1020b65`), desk-verified;
the owner's mesh-and-maps import is owed.** Built by an Opus agent; the guard, validator and
proofs rerun by the orchestrator. Production knobs are the skeleton's defaults (`PORTAL_STYLE
'B'`, `PORTAL_SHOULDERS`, `HOOD_BORE 'portal'`, `PIT_ON`), legacy reachable by `--legacy` and
proved (99 of 99 byte-identical; `TrainHub_work_before_portal_pit.blend` kept). Work file 99 →
135 objects: 8 changed (`Hub_Portals` 4,434 → 630 faces, `Hood_1..6`, `FloorPlate`), 36 added,
91 identical, spots 25 → 27 with 0 moved (`verify_portal_pit_pass.py`, `portal_pit_baseline.json`).
UVs re-frozen once more (`concept_freeze_uv1.json` kept; plain rerun passes `require_frozen`):
density 18.00 texels/m (was 19.17: the same atlas now carries the 16 m portal blocks and the
pit), spread 8.5% over 24 groups, coverage 53.69%, overlap 0, every new group within ±0.9% of
the mean, `Hub_Portals` straightness 38.9 → 85.2%, glass atlas unchanged. FBX 30 → 33 nodes
(`terrain_hole` as its own 48-face mesh, `-Pitfloor`, `-Pitrim`), body 14,976 faces,
`Collision`/`hex_shape`/`Selection` byte-identical. AO rebaked on the new fingerprint (23 s);
`bake_structure.py` 176 s; `validate_structure.py` PASS, 0 failures: every group's SI peak at its
knob level (Portal 179 — the collar gained a paint branch with the line on its 0.15 m chamfer;
PitShaft 89), the insert-edge test extended to the portal family (fringe median 1 texel), road
0 and lit 0 texels reached by the layer. **The ring one-line check's light half misfired and
published `solid`**: 0 of its 54,840 "light" texels were brightened by the seam step (all within
1 byte of the no-relief variant; 21,755 of them the AO edge light), the seams' own darkening
having pulled the ring's median from 205.3 to 200.7 under the 6%-over-median rule. The
orchestrator gave the light half the same no-relief baseline the slope half already had (a
light texel is one the seam brightened over the `solid` variant by 6% of the hull): 0 seam
light runs, 1,835 seam slope runs, 0 paired, `seams` published to `textures/structure/`.
Previews `export/final/previews/` (14 views incl. `portal_front`, `pit_close`, night pairs).
Owner's steps: README "Current handoff: the portal collar and the drone pit" and
`export/final/IMPORTER_STEPS.md` — the material is unchanged; **add one importer selector**
(`'name', "terrain_hole", 'SurfaceType', "terrain_hole"`) beside `Collision`/`hex_shape`/
`Selection`, run the Body import procedure, save, reload. **The owner decides in the morning:**
portal B confirmed (A one knob away), leaves hidden in the pockets (recommended) or visible,
the pit's roofing (accept the hangar under the deck / shorten a siding / smaller pit), the ring
notch if the ring shows in a pocket, and the doors driven by trains (`8aef5de`, mocked only).
Still owed after the look: the structure's own lights (step 6, held while the doors brief has
`20_TrainHub.lua`), the whole-hub cost reading (step 7), a restore point on keep.

**The owner's look at the portal/pit import, 2026-09-22 11:02 — KEPT; restore point
`hub-portal-pit-20260922`** (paired tags at OptInPack `8cbe3f2`, the import checkpoint with the
`terrain_hole` selector, and assets `1020b65`; 66 files, 501.9 MB). The import: entity gains
`Pitfloor`, `Pitrim` and the `eTerrainHole` surface, mesh re-read, four DDS recompiled; the
selector was added in the editor as a sibling of `Collision`/`hex_shape`/`Selection` (a first
try nested it under `Collision`, which would not match). Owner: the pit reads as a hole with depth
from every angle, better at night, **the hangar under the deck is accepted**; the whole hub holds
up close and far, *"I am fully happy with it."* **Owner ruling: the door operation is cut** —
*"The doors I love, but I think we are going to have to cut them because of what we had to do to
get them."* Reasoning given by the orchestrator first: the doors cannot slow the train network
(positions only, a 100 ms watch, no train reads a door), but at six busy stations they sit open
or flutter, a fast train outruns the 0.5 s opening, and they are invisible at the overview.
**Owner ruling: the portals must fit the dome** — the 16 m squared gatehouse blocks *"give the
opposite feel of dome"* and will look worse once the glass is in; *"I want the portals to
seemlessly fit into the dome in general."* The owner's wish, thought impossible: no portal at
all, a sliding glass door opening a "portal" in the glass. Read on the skeleton: the dome seats in
the ring's channel at r 32.95, z 8.40 (`DOME_R`, `DOME_BASE_Z`), the mouth's crown 13.125 m sits
4 m above the ring top (9.10), so every opening is already a cut in the glass with the hood as
its frame; the gatehouse and pocket are `PORTAL_SHOULDERS` and the door constants, and the clear
opening does not depend on them. The portal fit is the next design unit; the pending decisions
(leaves hidden or visible, the ring notch) lapse with the doors. Brief 05 is done as far as it
goes: its Lua block stays until the portal ruling says what replaces it.

**Owner ruling, 2026-09-22, the jagged paint: hard-edged features go on geometry** — *"Then we
need to implement this as well."* The owner's five close-ups: the road's curved blue lines and the
centre-plate crossings stepped and soft, the ring's rim strip a sawtooth, a rib band a sawtooth,
and, clean, the beam-edge strips. Read by the orchestrator (not measured in game): the clean strips
are their own faces and islands, so their edges are mesh edges; every jagged feature is painted
from 3D position across the texel grid (5.5 cm a texel at 4096 and 18 texels/m, 6-10 px at the
owner's zoom): a curve stairs, the ring strip crosses the ring island's 0.64° median row tilt,
the rib band is a level set of world radius on an inclined tube (spec §9 "UV pass delivered":
ribs 9.9% straight, unfixable by unwrapping). The fix is the road's own technique: the ring rim
strip and the rib bands become their own face loops and islands; the road arcs and the centre
crossings become thin ribbon meshes on the deck, each a flat island, so the line's edge is a mesh
edge and no texel size limits it. Cost stated: a few hundred faces, ribbons a few millimetres
proud of the deck. Bundled with the portal fit into ONE re-freeze, bake and import; the current
build stays reachable by knob. Portal option 1 ("flush rim": a rib-section collar bent round the
mouth, flush with the glass, gatehouse and pocket gone, clear opening unchanged) is being built
as a candidate with renders beside the current build, glass shown, for the owner's pick.

**Portal candidate C, the flush rim, 2026-09-22 — assets `559e478`, desk-verified; owner's pick
owed.** Built by an Opus agent; `--check-rebuild` rerun by the orchestrator (WORKFILE_PROOF PASS,
135 objects, 91 identical against the pre-portal baseline, i.e. production byte for byte).
`PORTAL_COLLAR` knob (`'shoulders'` production | `'bell'` | `'rim'`): the gatehouse, pocket,
rebate and buttresses go; a 0.60 m tube (the ribs' `bevel_depth`, asserted equal) bends round the
mouth laid on the dome so its centreline is the glass edge, the dome's cut read back off the same
polyline; the hood stays as the hidden liner; the throat is two cheeks through the ring's gap;
the thin sill. `C_rim_proof.json` (export/, gitignored): +6 `PortalRim_*`, −12 (`Portal_*`,
`PortalShoulder_*`), 19 changed (`Glass`, `Hood_*`, `PortalThroat_*`, `PortalSill_*`), 110
identical, 0 spots moved, floor untouched; rim radial extent 28.68-33.53 m (collar was
33.0-35.5), z 7.30-14.32; glass edge buried everywhere (least 0.239 m, gap 0); clearance
4.16 × 4.36 train +0.7475 (unchanged), 4.0 × 5.0 +0.125 (was +0.104); new portal faces 3,144
against B's 4,938. Consequence for the owner: outboard of the dome nothing stands over the
track (the ring's gap is cheeked to 9.10 m, open sky to the dome); `NOTES_C.md` §5 offers a
second hoop on the ring's outer lip at 35.5 m and rim radii 0.45 / 0.80. Renders
`export/portal_candidates/C_view1..5`, `C_portal_{front,close}{,_night}`, `B_glass_*` beside.

**Edges onto geometry, 2026-09-22 — assets `332548e`, desk-verified.** Built
by an Opus agent; `--check-rebuild` and `validate_edges.py` rerun by the orchestrator.
`EDGE_GEOMETRY` knob, default legacy in `hub_skeleton.py` and `paint_concept.py`. On: arm lines
(approach path, merge curve, dashes) `Line_Arm_1..6` ribbons 1,140 faces; floor curves
`Line_Curve_1..6` + `Line_Centre_1` 847; rib bands `RibBand_1..30` sleeves 960 (12 mm proud,
32 steps, inradius clearance 3.34 mm over the rib's 12-gon after a first render showed the
ridges poking through at 6 mm); ring rim strip its own face loop (`RING_PROFILE` 14 → 18: four
points, the inner wall is lit too); siding frame line a face loop; floor trim circle and edge
strip concentric loops at r 30.75 / 30.60. Ribbon lift 8 mm, MEASURED (`zfight_proof.json`,
Eevee, deck-wins fraction of 93,101 interior pixels: 3 mm 1.174%, 8 mm 0.0032%, the knee).
`edges_proof.json`: 135 → 178 objects, 43 added, 8 changed (`Ring`, `FloorPlate`,
`Siding_1..6`), 127 identical, 0 spots moved, plate rim 144 faces; identical under both
`PORTAL_COLLAR` values; body 14,976 → 18,883 faces. Legacy reproduces: check-rebuild PASS, 135
of 135 digests identical; 4 of 4 maps byte-identical between the HEAD painter and the new one
with the knob off. UV (`uv_edges.json`): density 18.00 → 17.63 /m, spread 8.4%, coverage 53.69
→ 51.94%, islands 2,021, overlap 0, `Line_Arm`/`Line_Curve` 100% straight, `RibBand` 96.8%.
Bake at 2048 (AO off), `validate_edges.py` PASS: road lit texels 0/0/0, `Line_Arm` 7,607,
`Line_Curve` 5,958, `RibBand` 4,026 texels every one at SI 179 and BC (0,40,255);
`validate_structure.py`'s `EXPECTED_PEAK` re-pinned by value, gated on the mask carrying the new
groups so held bakes still validate. Renders `export/edges/renders/{before,after}_{road_arc,
ring_rim,rib_band,centre_cross,beam_strip}_{day,night}`. Open for the owner: the rib band stands
12 mm proud (flush needs the ribs as meshes, a different pass); the road line now reads its full
0.247 m width; the arm ribbon runs across a 13 mm slot between beam edge and platform edge near
u 50 m. Incident: an early candidate run overwrote `TrainHub_work.blend` and two proofs; restored
from git, regenerated, verified 135/135. Next: the owner's picks, then the production run
(knobs on, one re-freeze, AO + structure bake at 4096, export, one import).

**Owner rulings, 2026-09-22, on the two candidates: "the first is good for me, all look good",
then "Approved".** Portal C, the PLAIN rim at the ribs' 0.60 m, no second hoop (the hoop render
was stopped unbuilt, nothing left in the tree); the edges unit as rendered: the rib sleeves 12 mm
proud accepted, the road line at its full 0.247 m width kept. Production run authorised:
`PORTAL_COLLAR='rim'` and `EDGE_GEOMETRY` on become the skeleton's defaults, legacy by knob; one
UV re-freeze; AO + structure bake at the production sizes; export; one import (same FBX path,
same material, no new selector or spot). The brief-05 door block comes out of `20_TrainHub.lua`
in the same step; the structure lights follow.

**Production run, the flush rim and the hard-edged lines, 2026-09-22 13:11 — assets
`24a98b7`, desk-verified; the owner's mesh-and-maps import is owed.** Built by an Opus
agent; the orchestrator reran `--check-rebuild` (172 of 172 digests), `prove_previous_production.py`
(135 of 135 identical to `TrainHub_work_before_rim_edges.blend` by knob), `--legacy
--check-rebuild` (99 of 99) and `validate_structure.py` (PASS, 0 failures). Defaults:
`PORTAL_COLLAR='rim'`, `EDGE_GEOMETRY` on; `PORTAL_SHOULDERS` is now derived from the collar.
Work file 135 → 172 objects: 49 added (`PortalRim_1..6`, `Line_Arm_1..6`, `Line_Curve_1..6`,
`Line_Centre_1`, `RibBand_1..30`), 27 changed, 12 removed (`Portal_*`, `PortalShoulder_*`), 96
identical, spots 27 → 27, 0 moved; body 17,689 faces / 22,541 verts. The rim's blue line is the
generator's glow faces carried through the merge (`lit` per face, 41 a mouth, 246), painted by
that mark. UV re-frozen once (`concept_freeze_uv2.json` kept): density 18.00 → 19.33 /m, spread
5.1%, worst group 4.45%, coverage 51.35%, overlap 0; `Hood` straightness 68.1 → 56.8% (the hoods
now die on the dome: a change of subject). FBX 33 nodes, only the body changed. AO rebaked;
`bake_structure.py` 191 s; published `seams` as the validator's first choice (0 ring light runs —
the last pass's flip has no symptom now): road lit 0, `Line_Arm` 37,196 / `Line_Curve` 28,700 /
`RibBand` 20,340 / `PortalRim` 6,504 lit texels all core at SI 179, 180,977 core texels exactly
(0,40,255). Clearance unchanged (+0.7475 / +0.125 m). TGA sha256 BC `0a598e77…`, NM `09db59d5…`,
RM `38724e48…`, SI `f572b12e…`; DDS expected ~11 + 22 + 11 + 2.8 MB. **Flagged: a published check
changed** — the rib-band edge-ramp test moves to the `RibBand` sleeves and inverts to 0 ramp
texels, gated on the mask (wants a ruling, as the light-half change did). `textures/structure_seams/`
is a dead-atlas leftover (03:58), deletion the owner's call. Owner's steps: README "Current
handoff: the flush rim and the hard-edged lines" and `IMPORTER_STEPS.md` — same FBX path, same
material, no new selector or spot; Fill selectors, Body import procedure in full, save, reload.
The doors' Lua came out at OptInPack `c1a8a50` (look_smoke 8 cases PASS); brief 05 deleted at
`b3c1bba`. Next after the look: restore point on keep, then the structure lights (step 6).

**The owner's look at the rim + edges import, 2026-09-22 13:21 — KEPT ("It all look great");
restore point `hub-rim-edges-20260922`** (paired tags at OptInPack `62bd798`, the import
checkpoint, and assets `24a98b7`; 66 files, 502.5 MB). Owner's open questions, answered in
chat and recorded: the exterior colouring is a paint-only decision now (every hard edge is
geometry and the UVs are frozen), so it never gates geometry, the lights or the cost reading;
a track colour change is a knob (`PAD_BASE`/`PAD_VARIANT`, the line colour), a ~3-minute bake,
a validator re-pin of the held road value under a ruling, and a texture-only import; the arm
lights' colour is one Lua constant. Next: the structure lights (step 6), then the cost reading.

**Floor strip islands and the portal junction, 2026-09-22 — assets `5cbedc6`, desk-verified; the
owner's mesh-and-maps import is owed.** Owner's look after the rim + edges import: the floor
plate's blue edge strip still a sawtooth; at every portal mouth the throat cheeks strobing
("textures breaking") and a thin black line at the ring's cut end. Causes measured: the floor
loops sat inside the one planar top island and were painted by radius (lit 13,192 vs core
8,423 — the only edge group where the two differed); the cheeks were trimmed flush to the ring's
envelope (204 coplanar overlapping face pairs, 16.08 m², with Ring underside/tops and the hood
bore) and the cut end was uncovered. Fix, one Opus run, proofs rerun by the orchestrator
(check-rebuild 172/172, previous production 135/135 by knob, legacy 99/99, validate_structure
PASS 0 failures): strip (144 faces) and trim (288) are their own polar islands (0 off-axis UV
edges, density −0.03% of the mean), painted by face membership — lit 10,736 = core 10,736;
`build_throat_cheeks()` sweeps the ring's own section inboard with `PORTAL_THROAT_INSET` 30 mm
on every shared face (inner wall 3.25 → 3.28 m): 0 coplanar pairs, cut-face exposure 4,077 →
603 samples, the residual the inset's own band, not a hole (`junction_{before,after}_*.png`).
Digests: only `PortalThroat_1..6` changed, `FloorPlate` identical, 0 spots moved; body 19,321
faces; UV re-frozen once (`concept_freeze_rim_edges.json` kept), density 19.59 /m, spread 5.4%,
overlap 0. Published TGA sha256 BC `62f01310…`, NM `99de6443…`, RM `626bb85d…`, SI `462fa59f…`.
Also this sitting: the structure lights (OptInPack `ba1e0d7`: portal 30, pit 6, rim 36, floor 24
off by default, 144 total with the arms; `SetHubLightTune` / `SetHubStructureLights` console
tuners for the owner's lavender-when-lit, read as overexposure) and the recharger platform
removed (`51b89a5`). Owner's asks pending: storage bay restyle (gunmetal, yellow border, a decal
the owner will supply) — paint only, after this import.

**Correction to the earlier sampled RM claim.** The validator's full baseline histogram at
`ea82ef4` finds RGB (71,71,0): 91,421; (74,74,0): 432,288; (82,82,0): 3,254,698;
(110,110,31): 95,577; (122,122,0): 320,320, summing to 4,194,304 texels.
The five-value count holds, but "metalness 0 everywhere" does not: 95,577 texels carry 31/255.
The old platform predicate's hidden-cap painting is also an out-of-scope baseline finding;
those texels retain their original values in this delivery. The earlier normal-first order is
historical and is superseded by the owner's staged order above.

---

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
**BUILT in `3ec2f0b`, not yet checked in game** (`TRAIN_HUB_MOVE_high.md`): `HubUpdateProduction`
now keys production off `ui_working`, malfunction and destruction rather than `working`, so a lone
hub should start on its own output. The in-game check needs the seven Stirlings removed (below). Open, not yet ruled: what else must work with no drones and no grid, such
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

**A vanilla stop costs 12 game seconds each way, and nothing can end it early** (read 2026-09-20
from the archived 1.1.0.403908 tree). `Train:LoadTrain` ends on
`WaitWakeup(Max(const.HourDuration / 5 - GameTime() + time_stamp, 100))` (`Lua/Units/Train.lua:281`)
and `Train:UnloadTrain` carries the identical line (`:450`). `const.HourDuration` is
`const.Scale.h` (`Lua/_GameConst.lua:5`); a Sol is 1,440,000 ms over 24 hours (`EF-062`), so a game
hour is 60,000 ms and a fifth of one is **12,000 ms of game time**. Three properties matter:
- It is a **deadline, not an added delay** — `time_stamp` is taken at the top of the command and the
  cargo transfer runs before the wait, so a stop is a flat 12 s whatever the transfer costs, with a
  100 ms floor when the transfer has already spent the window.
- **Unloading costs its own 12 s** and queues `LoadTrain` on the way out, so a train that both
  unloads and loads stands for about **24 s**.
- **Vanilla never wakes a train early.** `WaitWakeup` returns early only on a matching
  `Wakeup(thread)`, and a grep of the whole `Lua/` tree finds no such call for a train — the
  elevator's `Wakeup(queue[idx + 1].command_thread)` (`Lua/Buildings/BaseElevator.lua:62`) is the
  game's own demonstration of the move on another class.
⇒ **The dwell is ours to shorten without touching vanilla's code**: `command_thread` is a public
field of every `CommandObject` (`CommonLua/Classes/CommandObject.lua:90`), so a `Wakeup` on it ends
the stop at whatever moment we choose. The lever is one-directional — it can only make a stop
shorter than 12 s, never longer, since a longer dwell would mean replacing the command.

**Owner ruling, 2026-09-20: halve the dwell, hub trains only.** *"Can we cut each in half and see how
that looks. 6s / 6s so the whole transfer can take a max of 12s if it has to do both."* Scope, the
owner's, same exchange: **only trains in our hub**, NOT vanilla stations — *"I would rather not over
ride it for all stations unless we can't find other ways to make it 'feel' good."* Whether it should
ever apply colony-wide is a later question at the scale of the whole project, not this build's. The
6 s is a named constant the owner dials by eye; it is a deadline like vanilla's, so it is measured
from the start of the command, keeps the 100 ms floor, and must be timed in **game time** so it
scales with the speed slider exactly as vanilla's wait does.

**What our own transition costs today, for comparison** (read 2026-09-20 from
`tools/devmods/train_hub/Code/20_TrainHub.lua`, as the MOVE prototype left it). `HubSlideTrain`
(`:471-483`) is **1.2 s flat** — eight steps of 150 ms on a smoothstep curve, a fixed duration
whatever the lateral distance — and it runs twice a visit, in and out, so **2.4 s**. A reversal that
is not straight-through adds `SetAngle(outward, 1000)` with a matching `Sleep`, **1 s**
(`:524-525`). The approach and park moves are distance-based through `GetAccelerationAndTime`
(`:451`), governed by the owner's pause and park tunables, not by a timer. Halving the slide costs
nothing in smoothness if the step shortens rather than the step count dropping (8 × 75 ms keeps all
eight samples); below about six steps the easing reads as a stutter. **Owner, 2026-09-20: not yet.**
They want the halved dwell in front of their eye first and will decide the slide and the turn after
— *"at least I know it's an option."* Do not change either without that ruling.

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


**MOVE implementation update, 2026-09-20 (SOURCE, visual smoke owed).** The dev hub now curves
from the running centreline onto its loading siding while braking and rejoins while accelerating,
only after the existing exit/crossing guard clears. Stop/Spawn move together onto the siding;
reservation identity remains the connector. Pause, park, lateral offset, entry and both rejoin
positions are live tunables, never solved from train length. Outer-slide and turn timing is
unchanged. The hub-only dwell is implemented as a synchronous adjustment of the remaining
`WaitWakeup` deadline, scoped to the parked hub train's LoadTrain/UnloadTrain command thread:
6000 game ms from command start, preserving the 100 ms floor after long transfers. Vanilla
stations retain their original input; no wakeup helper or Train command replacement is needed.
The mocked smoke passes, including archived loading commands and vanilla control. Native
appearance, timing, save/load and cold start remain owed; see the build report's
"Siding movement and hub dwell prototype" for the prepared sitting. Loading policy/full
queueing, textures and build 4 remain deferred under their existing gates.

**Pass 3 movement trials, owner handoff 2026-09-20 (computed, not measured in game):**
park 14.5 m, clockwise siding offset 4.5 m, entry and reverse rejoin 26.5 m; inward rejoin
stays 5 m. These defaults require the Pass 3 model, whose owner import is pending in the
handoff. Try 5.0 m lateral next if needed and judge park within 13–15 m. No width/length fit
is established; R-TRAIN remains DISPUTED. The model's reported cargo-bed corner overhang
is still an owner asset question. The build report carries the current sitting.

**Longer-stub movement trial, owner handoff 2026-09-20 (import pending):** set pause to
48 m, with 47–49 m for the owner's eye. The model session reports connector 60 m and arms
40–80 m; generator `STUB_R = FOOTPRINT_R + 2` and `PLATFORM_ARM_HEXES = 4` were checked
from `hub_skeleton.py` at Opt-In HEAD `15d6e19`. Siding tunables stay unchanged.
The proposed 46–50 m clearance window assumes a centred, roughly 20 m train from screenshots;
it is not a measurement or a resolution of R-TRAIN. Verify mirrored exit clearance too.
Until the owner trims old tracks and saves a new fixture, use a freshly placed hub after
import; confirm its 60 m connector and native track attachment. If no pause in the window
looks right, report the overlap in metres to the model pass instead of compensating in Lua.
The same FBX reportedly shifts the cargo beds and their Box spots together; the movement
code continues reading those spots and makes no cargo-layout adjustment.

**Owner visual ruling, 2026-09-20:** entrance was "very good"; exit slides too early.
Keep arrival at its 48 m source setting and separate the exit slide distance. The implemented
first outward trial is `HubExitSlideDistance = 50 * guim`, read only by Rampdepart and exposed
in the live tuning slots. Siding geometry and centreline positions are unchanged. This is an
eye-tuning trial; exit acceptance and the remaining native smoke are still owed.
The owner then clarified that the first screenshot's "pull up a little more" concerns the
interior move onto the loading platform. Its curve now starts at 25.5 m instead of 26.5 m,
a 1 m farther-in trial with the parking point and both rejoins unchanged. This is independent
of the entrance transition and exit slide; the owner must still judge both adjusted movements.

**Owner exit-speed ruling, 2026-09-20:** after the exit slide, go immediately to normal travel
speed. The hub now passes outgoing-element nominal speed as both start and finish of its
final GotoSpot, replacing the one-third-speed acceleration leg. Vanilla's tech/heat/law speed
calculation remains authoritative; slide timing and interior movement are unchanged. This
also applies to through departures. The post-slide launch needs the owner's visual check.

**Owner siding follow-up, 2026-09-20:** pull another quarter hex inward before starting the
loading-platform transition. `HubSidingEntryDistance` changes from 25.5 to 23 m (2.5 m inward);
park and every other movement setting remain fixed. Visual acceptance of this trial is owed.

**Owner correction, 2026-09-20:** entry-only changes made the transition sharper/jerky and
left parked overhang unchanged. Correct the implementation by translating the entire siding
movement 3.5 m inward from the Pass 3 trial: entry 23 m, park 11 m, inward rejoin 1.5 m,
reverse rejoin 23 m. This restores the original approach/rejoin lengths instead of shortening
the curves against a fixed parking point. The fixed-park trials above are rejected. Lateral
offset and outer transitions stay unchanged. Parked fit, inner clearance and smoothness need
the owner's next visual check; the arithmetic does not settle train dimensions or clearance.

**Owner exit-handoff report and repair, 2026-09-20:** visible jump at the stub/vanilla joint.
SOURCE: archived 1.1.0.403908 Train.lua's LoadTrain/GotoStation requests a teleport on the
first outgoing segment, which the previous hub handoff had not traversed. The hub now calls
vanilla CheckValidDest and WaitTraverseElement with teleport disabled to travel that segment
before returning control. Vanilla's subsequent teleport destination is already reached.
No Train replacement or new persisted state; slide positions/timing and normal-speed launch
remain. The mocked archived-body smoke reproduces the old jump and passes the corrected
handoff for stopping/through departures in both track directions. Native visual acceptance
at the arrowed joint is still owed; details and source lines are in the build report.

**Owner siding fine-tune, 2026-09-20:** alignment is right and the transition nearly perfect;
onset is a little early. Preserve park 11 m and lateral offset 4.5 m; trial entry 22.5 m
instead of 23 m, delaying lateral onset by 0.5 m while retaining the same easing function.
Rejoins and outer transitions stay fixed. Judge the slightly shorter curve's smoothness
in the next sitting; the owner's alignment feedback does not close the remaining smoke.

**Owner onset follow-up, 2026-09-21:** half-metre delay made no visible difference. Trial
entry 20 m (another 2.5 m inward) with park 11 m and offset 4.5 m fixed. Scale the braking
entry speed with its remaining run relative to the original 12 m approach to avoid
compressing the lateral easing time as onset moves inward. Rejoins and outer transitions
stay fixed. This is a new visual trial, not a measured clearance or accepted movement.

**Owner next trial, 2026-09-21:** 20 m onset is close but still early. Set entry to 19 m
for another metre of straight travel, retaining the fixed parking alignment and existing
entry-speed compensation. Other settings stay fixed; the owner still judges the result.

**Owner siding-entry correction, 2026-09-21 (implemented; visual acceptance owed):** remove
the run-length entry-speed compensation: it changed speed when the requested change was position.
The approach is fixed at one-third nominal speed. The siding entry now keeps moving forward while
using the accepted outer slide's exact eight-step, 150 ms smoothstep for the lateral component;
a longitudinal Hermite component carries the incoming speed to zero at the parked point. Thus the
lateral rate and 1.2 s duration do not depend on the live onset setting. The first trial is 17 m,
with park 11 m and offset 4.5 m unchanged. Rejoins, outer transitions, dwell and vanilla handoff
remain as accepted. The mocked movement smoke checks the fixed approach speed and all eight
lateral samples; only the owner's eye at normal, fast and fastest speed can close smoothness and
rate matching. The build report carries the five-step sitting and live 1 m onset control.
