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
`WORKFLOW.md` or `FIX_POLICY.md`, those win. The owner asks are `PLAYTEST_CHECKLIST.md`
**OI-10**.

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
through the export branch in normal play today. See §7.1.

### 4.3 Design → mechanism

| Element | Vanilla status | Work |
|---|---|---|
| import/export per resource | `transport_policy[res]` exists, consumed, no UI | **UI only** |
| import: drones drain to zero | `supply desired = 0` — the `accept` branch | **none** |
| export: drones fill to max | `supply desired = max` — the `send` branch | **none** |
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

### 4.5 Five vanilla paths that rewrite per-resource desired amounts

Our values must survive all of them:

| Site | Fires when |
|---|---|
| `Station:SetDesiredAmount` (`:964`) | the flatten loop |
| `Station:SetAcceptResourceState` (`:1038-1045`) | **every accept/export/disable click** |
| `MultiResourceDepotBase:UpdateRequestCapacity` (`MultiResourceDepot.lua:221-222`) | capacity change |
| `MultiResourceDepotBase:OnModifiableValueChanged` (`MultiResourceDepot.lua:397`) | the `max_storage_per_resource` upgrade — live via `upgrade1_mod_prop_id_1` |
| `SavegameFixups.RevertStationDesiredAmount` (`Station.lua:1744`) | once, on old saves |

### 4.6 ⛔ The alias trap

`MultiResourceDepot.lua:63` does
`RegisterResourceRequest = MultiResourceCubeVisuals.RegisterResourceRequest` — a reference
**captured at class-definition time**. Wrapping the declaring class later will **not**
affect the alias `Station` resolves through. Declaring class is
`MultiResourceCubeVisuals:RegisterResourceRequest` (`MultiResourceCubeVisuals.lua:372`).
This is the F64/F107 shape; `FIX_POLICY` §2 governs it and
`tools/harvest_wrap_targets.py --check` gates it via doccheck. Design around it.

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

A `Station` using all four connectors is already two crossing lines on two routes sharing
one member — a 2-way interchange with today's art and today's code. Whether cargo actually
flows through it is **untested** (§7.2). Six connectors would be three crossing lines.

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
recommended. ⛔ None is an owner ruling; the asks are `PLAYTEST_CHECKLIST.md` **OI-10**.

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

### OPTION 5 — How module B is scoped

| | |
|---|---|
| **5a** | Interchange only — multiple straight-through lines crossing at one building, cargo transferring through its storage. No route-model change |
| **5b** | 5a plus colonist interchange — a two-hop `work_route` through a shared station |
| **5c** | Full route-switching — trains driving through the junction. Requires a graph layer |

⭐ **Recommended: 5a first, then reassess.** It is the `PassageHub` pattern applied
faithfully and it needs no graph. 5b is the most defensible *feature* of the three — the
single-route restriction on colonists is a real, verifiable gap — but it should follow 5a.
5c is large and grows; hold it in reserve.

---

## 7 · Falsifiers — what must be tested before any of this is believed

Every claim in this spec is desk-read. These are the checks that would prove it wrong, in
the order they should be run. ⛔ None has been run: `<<PENDING-RUN>>`.

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
   the geometry comes from the entity art and has not been seen. *Fail:* Module B needs more
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
   `*r SelectedObj:SetDesiredAmount(20 * const.ResourceScale)` with a few multipliers and compare
   drone filling against
   a second station. This only matters to the parity-restore route, which §2 recommends against.
5. **What breaks when `GetMaxStorage(res)` stops being uniform?** It also drives visual cube
   columns, `GetEmptyStorage` (`MultiResourceCubeVisuals.lua:506`) and load caps — so
   overriding it changes *real* capacity, not only a balance weight.
6. **Can native `CObject` methods be overridden on a Lua class?** The assumption under
   OPTION 3a. A hello-world test settles it without any design commitment.
7. **Paradox patch notes / dev diaries** on the 1.1.0 station change — external, not checked.
   Would settle §1's intent inference.

---

## 8 · Binding constraints for whoever builds this

- ⛔ **Both modules are NEW.** The 2026-08-31 drone unfreeze does not cover them, and the
  2026-09-17 ruling unfroze only D06/D07/D12 — all three now retired. MODULE FREEZE applies.
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

**Unknowns this pipeline leaves open, each decisive for OPTION 3:**
- Can a mod's `.ent` reference a mesh that exists only inside `Packs\Meshes.hpk`? This decides
  whether 3b is possible.
- What does `<surf_hash>` gate? If it is an integrity check, hand-edited surfaces may be
  rejected.
- Can a Lua class override native `CObject` spot methods? This is §7 item 6, and 3a depends
  on it.

---

## 10 · The prototype, the next build (not yet authorised)

**Owner direction, 2026-09-18:** run §7's T1–T3 **before** the prototype build, and the owner
runs the in-game checks. ⛔ The build itself needs **OI-10** ruled, at least to the extent of
"prototype Module B via option 3a". MODULE FREEZE applies until then.

**Shape (recommended; re-scope from T2's result first).** Module B only, option 3a, interchange
only (5a). A `Station` subclass whose template references `entity = "PassageHub"` by name, with
the palette moved to the train family and connector positions computed in Lua. It must be a
`Station`: interchange needs storage and the balancer, and a bare `TrackConnectedObjBase`, like
the tunnel, only passes trains through. If T2 passes, the prototype's question narrows to "does
a PassageHub-shaped hub with more than four connectors work". If T2 fails, re-scope OPTION 5
before building anything. PassageHub's hex footprint, including how many edge hexes it has, is
not readable from Lua and is discovered during the prototype.

**Step 0 is a spike:** override `GetSpotBeginIndex` and `GetSpotPos` on the class (§7 item 6).
If that fails, override the six `TrackConnectedObjBase` spot methods and wrap the two external
readers, `TrackElement.lua:345` and `Train.lua:660`. §5.4 lists all twelve sites.

**Done means:** the hub is buildable; tracks attach to its computed connectors; trains on two
routes both stop at it; cargo moves from route A through the hub to route B; and it demolishes
cleanly. `PassageHub.lua:50-55` warns that teardown is where hubs assert.

⛔ **Disposable saves only** (recommended; the owner confirms it with the OI-10 ruling). The
prototype's class and field names are not save contract until they touch a kept save; after
that, ban 1 makes them permanent.

**The build prompt** is authored with the `prompt-authoring` skill as a root one-off, only after
T1–T3 results are recorded in §7.
