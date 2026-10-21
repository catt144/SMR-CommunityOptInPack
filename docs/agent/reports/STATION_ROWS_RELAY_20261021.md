# Station rows without a hub: terminal, not relay — 2026-10-21

> §11 is the independent check (Codex, 2026-10-21). §12 is the revised proposal that answers it (Claude Fable 5.1, second session, the same day), with its prototype and desk check under `docs/archive/station_rows_proposal_20261021/`. §13 is the second check of that proposal (Codex); §14 is revision b, answering §13, with its own prototype and check under `docs/archive/station_rows_proposal_20261021b/`.

> §13 is the second independent check (Codex, same day): diffusion is supported in the exercised
> networks, but reproduced allocation and unload failures require another correction.

**Latest independent verdict in §13: the revised prototype needs corrections.** This is the package the owner
hands to a second model family (Codex) to confirm or refute before anything is authored as a fix.
Nothing here is a ruling and no module behaviour has changed. The claims register in §9 is the
checklist for that leg: every claim carries where it was read and how far it was verified.

Inputs: OptInPack HEAD `80766e7`; `git diff --stat optin-v1.0.3 -- Code/` prints nothing, so every
`Code/` citation is the live v1.0.3. Game lines are from the archived tree
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.406343\Src` (installed build 25579348 =
1.1.1.406343 per `python tools/doccheck.py --emit-fingerprint`). Investigation: five read-only
Opus 5.5 (`claude-opus-5-5`, effort high) subagents, each cleared by one spot-check of the line its
verdict rested on; the depot and junction findings were then re-derived in the session itself. This
write-up: Claude Fable 5.1. No game was launched during that investigation; §§1–10 are its original
claims, retained for comparison. §11 records the independent source review and desk checks and
qualifies or corrects those claims. No game was launched during the independent check either.

## 1 · The player reports (Steam Workshop, verbatim)

| date | player | report | module |
|---|---|---|---|
| Oct 7 | Erion | "I use train stations to make sure certain ressources are available everywhere and to shift citizens. I use big stations to interconnect lines. Now with your mod active concrete does not get shifted from one line of the big station to the second one (the one further from the building). Other ressources seem to work as exspected. When I disable the mod, concrete gets distributed again." | D16 |
| Oct 10 | TheGodUncle | "How does the elevator depot work? I've set multiple resources to export and they get moved to the surface but then they stay in the depot and don't get moved away. Do I have to set the slider to a certain value for the resources to get moved from the depot into the connected train station?" | D18 (+D16) |
| Oct 15 | Xeryx | "I have tried importing items to the station, like food when starting a new colony and the trains coming to that station seem to rarely bring me enough items. After much frustration I disabled Train stations. When I did that trains started bringing all sorts of items. I did find I had one large food storage set to a high capacity. And that is what I am wondering about importing. Should the value be low? because I think I had it set to a 20?" | D16 |
| Oct 15 | Xeryx | "The drone carry capacity, if I set it to +1. Every time I load a game it adds +1 to the previous setting. After five game reloads, I am now at a +6 carry capacity." (runs an unnamed "increased capacity mod") | D09 — separate, §8 |
| Oct 10 | Brad Thundercock | "the trains are getting stuck and not moving between the tunnels after a little bit of time" | none found — §8 |

## 2 · The owner's design intent (this session, verbatim)

> "we have to assume people will want the sliders to fully function without a hub."
> "What are your recommendations to get this working as expected?"
> "my desire of this working the way players expect this to work"

Read as: a station row (Import / Export / Balanced, with its slider) must do what its word says on
any line, hub or no hub, and a station that joins lines must keep passing cargo between them the way
the base game does.

## 3 · What the three train reports share

**The hubless rows treat every station as a terminal; the base game treats every station as a
relay.** Vanilla balances each line separately by storage share (`Lua/Units/Train.lua:884-950`):
a station that joins two lines holds a *different* share on each line, so stock flows from the
richer line to the poorer one through it. The hubless rows path replaces that share with a hard
target and floor that apply on **every** line touching the station
([StationRows_40_TrainDistribution.lua:832-853](../../../Code/StationRows_40_TrainDistribution.lua#L832-L853)).
The instant a row exists on a station that is not the end consumer of its line — a junction, a
depot's neighbour, a small store with a low target — the station is worse than vanilla. The hub path
has a relay concept (a tree with forwarding, §6); the hubless path has none.

## 4 · Findings per report

### 4.1 Erion — concrete stops crossing a Large Train Station

- Nothing in `Code/` singles out Concrete. Stations sort resources by SortKey
  (`Lua/Buildings/Station.lua:110`, `Lua/Resources.lua:357-363,386`; Metals 1000, Concrete 2000,
  Food 3000 in `Data/Resource.lua`), Concrete lands fourth; every loop of ours over
  `storable_resources` is a full `ipairs` (`StationRows_40:577,615,681,754,855`;
  `StationRows_10:185,226`). Multi-track mix-ups were ruled out: the view is built on
  `next_track or self.track` ([:891](../../../Code/StationRows_40_TrainDistribution.lua#L891)),
  the same track vanilla balances (`Train.lua:863`). The Fix Pack hooks no train transfer code.
- **Surviving cause: a saved Concrete row on the big station.** With Station rows on and no hub,
  a saved row makes the hubless view hold a floor of the row amount (the whole stock for Import,
  [:852](../../../Code/StationRows_40_TrainDistribution.lua#L852)) and order only up to the row
  amount (nothing for Export, [:838-846](../../../Code/StationRows_40_TrainDistribution.lua#L838-L846)),
  on both lines. Balanced at p%: line 1 fills the station to p, line 2 may take only what is above
  p — nothing crosses. Import: nothing leaves. Export: nothing arrives.
- **Why only Concrete:** it is the one row the player touched. Every click on a row writes one —
  the cycle is Balanced → Export → Import → Not accepted → Balanced
  ([StationRows_45_TrainDistributionUI.lua:34](../../../Code/StationRows_45_TrainDistributionUI.lua#L34),
  [:80-93](../../../Code/StationRows_45_TrainDistributionUI.lua#L80-L93)); one click on the slider
  writes Balanced at that percent ([:184-189](../../../Code/StationRows_45_TrainDistributionUI.lua#L184-L189));
  Ctrl+click copies the row to every station in the city ([:82-95](../../../Code/StationRows_45_TrainDistributionUI.lua#L82-L95)).
  **No panel action returns a row to untouched**; only the console
  `SMROptInTrainDistribution.Reset(st, res)` does ([:429](../../../Code/StationRows_40_TrainDistribution.lua#L429)).
  A saved Balanced row at the dial is indistinguishable from an untouched one in the panel. A
  vanilla-habit "click off, click on" lands on Import.
- "Disable the mod" cures it because with the modules off the rows are hidden and vanilla amounts
  are restored ([:107](../../../Code/StationRows_40_TrainDistribution.lua#L107),
  [:933-942](../../../Code/StationRows_40_TrainDistribution.lua#L933-L942)).
- Confidence: ~75% a Concrete row on the `StationBig` itself; ~15% rows only on the far line's
  stations (Ctrl+click usually lands on the big station too); ~5% an Elevator Depot on a line (it
  would pin every resource, a poor fit); ~5% undiscovered.

### 4.2 Xeryx — Import at 20 brings almost nothing

- The slider is a percent of **that station's own storage**: target =
  `MulDivRound(st:GetMaxStorage(res), percent, 100)`
  ([:188-191](../../../Code/StationRows_40_TrainDistribution.lua#L188-L191)); a vanilla station
  holds 60 per resource (`Station.lua:74`, `max_storage_per_resource = 60000`). Import 20 = 12 food
  per visit at most, and nothing while the station already holds 12. The storage building plays no
  part in the train maths; it only receives what drones carry off the station.
- An Import row **replaces** vanilla's share with the slider cap
  ([:839,846](../../../Code/StationRows_40_TrainDistribution.lua#L839-L846)). Two equal stations and
  60 food at the source: vanilla would send about 30; Import 20 sends at most 12. A low Import is
  worse than leaving the row untouched.
- A row cycled to Import **inherits the station's dial as a percent**
  ([StationRows_45:56-57](../../../Code/StationRows_45_TrainDistributionUI.lua#L56-L57)); the vanilla
  dial default is 10 units ≈ 17% of 60. "Import" therefore silently means "bring a trickle".
- Verdict: not a defect, a usability gap. The help text ([:49](../../../Code/StationRows_45_TrainDistributionUI.lua#L49))
  is accurate but does not warn. A third-party storage-capacity mod touches none of this.

### 4.3 TheGodUncle — exported cargo sits in the surface depot

The depot's Export word only reaches the trains through a Train Hub. Three configurations:

- **Hub on the line (D17):** works as designed. `D.HubEntry` presents the Export half as an export
  row at its slider ([ElevatorDepot_10_ElevatorDepot.lua:1390-1397](../../../Code/ElevatorDepot_10_ElevatorDepot.lua#L1390-L1397));
  the hub takes the stock above it. This is the owner's own configuration, cleared by play.
- **Depot only (D16 and D17 off):** pure vanilla balancing. The Export half (`hand_out`) is mapped
  to vanilla policy **"accept"** ([:883](../../../Code/ElevatorDepot_10_ElevatorDepot.lua#L883),
  applied at [:1090-1113](../../../Code/ElevatorDepot_10_ElevatorDepot.lua#L1090-L1113)), which sets
  its supply-desired to 0 (`Station.lua:975-980`). Vanilla moves a resource on a line **only if the
  sum of supply-desired along the line is above 0** (`Train.lua:896-897, 927, 933`;
  [TRAIN_LOGISTICS_DESIGN_20260917.md](TRAIN_LOGISTICS_DESIGN_20260917.md) line 99 names it the
  GATE), then splits by storage share. So the depot (250, `:137`) keeps ~81% against a 60-unit
  station, and the receiver's default dial (10) is the only thing holding the gate open. If the
  player sets the receiver's resource to vanilla "accept" (the one-click cycle at
  `Station.lua:1062-1067`), both ends read 0 and **nothing moves at all**. The "accept" mapping was
  chosen for its drone meaning ([ELEVATOR_DEPOT_WIRING_20261001.md](ELEVATOR_DEPOT_WIRING_20261001.md)
  row 50), but the depot's own filter already decides what drones see
  ([:1403-1409](../../../Code/ElevatorDepot_10_ElevatorDepot.lua#L1403-L1409)), so the policy's only
  surviving effect is on the trains.
- **Station rows on, no hub (D16):** the hubless view excludes depots from `IsRowStation`
  ([StationRows_40:88](../../../Code/StationRows_40_TrainDistribution.lua#L88)) and `effective()`
  returns nil for them ([:197-199](../../../Code/StationRows_40_TrainDistribution.lua#L197-L199)),
  so the depot's word and slider are **invisible**. The depot becomes a wordless member with floor 0
  ([:851](../../../Code/StationRows_40_TrainDistribution.lua#L851)) *and* an order equal to its full
  vanilla room ([:841-842](../../../Code/StationRows_40_TrainDistribution.lua#L841-L842)) — trains
  may also bring cargo *into* the Export half. Receivers on a depot line are pinned to their dial
  (~10 units) by the owner ruling of 2026-10-05
  ([:553-556](../../../Code/StationRows_40_TrainDistribution.lua#L553-L556),
  [:806-809](../../../Code/StationRows_40_TrainDistribution.lua#L806-L809)): each visit tops them up
  to 10. A trickle unless the player sets Import.
- The surface tooltip promises "trains (and drones, with Drone Access on) take it away from here"
  unconditionally ([:1209](../../../Code/ElevatorDepot_10_ElevatorDepot.lua#L1209)). The wiring
  report knew half of this (row 46: "Without a hub, vanilla trains ignore every target"). The
  record's "needs neither D16 nor D17" ([D18](../bugs/D18.md)) is true of the building and cabin,
  not of the train semantics. The final battery fixture was "Double Hub+elev", so the hubless cases
  were never attended.
- Drone Access is off by default (ruling 6), so drones never serve the depot unless turned on
  ([:1405](../../../Code/ElevatorDepot_10_ElevatorDepot.lua#L1405)).

## 5 · Can it happen with a hub?

- **Junction inside one hub network — no.** The hub path models the network as a tree
  (`owners/parents/children`, built from `train_track_routes` in `D.Refresh`,
  [:111-133](../../../Code/StationRows_40_TrainDistribution.lua#L111-L133)). An intermediate
  station's order includes its children's need (`child_need`,
  [:510-516](../../../Code/StationRows_40_TrainDistribution.lua#L510-L516)); "a leaf Import never
  becomes a train source, an intermediate Import may forward stock above its own pin"
  ([:701-704](../../../Code/StationRows_40_TrainDistribution.lua#L701-L704)); an Export station still
  accepts deliveries when its children need them
  ([:622-623](../../../Code/StationRows_40_TrainDistribution.lua#L622-L623)).
- **Xeryx's problem — yes.** Import N is N% of a 60-unit store with or without a hub, and the
  inherited-dial default is the same.
- **Seam between a hub's network and a line it does not own — partly.** No view is built for the
  other track ([:628-640](../../../Code/StationRows_40_TrainDistribution.lua#L628-L640)) but the
  hub-side row still caps unloads from it
  ([:593-628](../../../Code/StationRows_40_TrainDistribution.lua#L593-L628)). Asymmetric, untested.

## 6 · Recommendations (each a behaviour change needing an owner ruling unless marked text)

1. **A relay rule for the hubless path — the hub's `child_need` without a root.** For a station
   with a saved row that sits on more than one route (the city's `train_track_routes`; the hub tree
   is built from the same table, and vanilla exposes `Station:GetConnectedTrack` at
   `Station.lua:931`), its order on track A includes the net need of the stations on its *other*
   tracks, and its floor on track B is its own target. One hop with a visited set. Semantics that
   fall out, mirroring the hub:

   | row | leaf station | junction station |
   |---|---|---|
   | untouched | vanilla share | vanilla share (already relays) |
   | Balanced N | hold N; give above, take below | same, plus forward other lines' need |
   | Import N | take up to N; never give | take up to N + other lines' need; give above N |
   | Export N | give down to N; never take | give down to N; take only what other lines need |

   Scope: `local_train_view` ([:782-878](../../../Code/StationRows_40_TrainDistribution.lua#L782-L878))
   and the hubless branch of `Train:UnloadAll`
   ([:571-591](../../../Code/StationRows_40_TrainDistribution.lua#L571-L591)). Fixes Erion outright
   and the depot-neighbour trickle in the common case.
2. **Defaults that match the words.** A row cycled to Import starts at **100%**, Export at **0%**,
   Balanced inherits the dial ([StationRows_45:56-57](../../../Code/StationRows_45_TrainDistributionUI.lua#L56-L57)).
   Xeryx's fix.
3. **A visible way back to untouched.** Add "Default" (vanilla balancing) to the click cycle and
   title it as such; put it right after Not accepted so a vanilla-habit "click off, click on" lands
   on Default, not Import. Closes the trap that caught Erion.
4. **Route the depot's words through the hubless view.** The hub branch of `effective()` already
   tries `depot_entry` first ([:200-202](../../../Code/StationRows_40_TrainDistribution.lua#L200-L202));
   do the same in the `not hub` branch. Export half → export row at its slider, Import half →
   import at 100. The depot slider then works without a hub, as its tooltip says.
5. **Drop the dial pin on depot lines** (reverses part of the 2026-10-05 ruling). With 1 and 4 the
   pin only chokes receivers at 10 units. The pin existed because the depot was tested against it,
   so this costs a depot re-test, not a design.
6. **Map the Export half to "send" on the train side**
   ([ElevatorDepot_10:883](../../../Code/ElevatorDepot_10_ElevatorDepot.lua#L883)). Vanilla's gate
   then counts it and an "accept" receiver cannot freeze the line. The drone filter is unaffected.
   Does not fix the 81% share, which vanilla cannot express.
7. **Text.** Import/Export help says "percent of this station's N-unit store"; the depot tooltip
   stops promising trains unconditionally. (Text only.)

Relative size: 1 is the build; 2, 3, 4, 6, 7 are small; 5 is a re-test. Proposed vehicle: v1.0.4,
replies to the four players after the fix is live.

## 7 · Controls — what would falsify each finding

- **Erion**, in the player's save or any copy (a game loaded):
  ```lua
  for _,s in ipairs(UIColony.labels.Station) do for r,e in pairs(rawget(s,"SMROptIn_station_rows") or {}) do print(s.handle, s.template_name, r, e.mode, e.percent) end end
  ```
  A Concrete row on the `StationBig` handle confirms 4.1; none at all refutes it.
  `SMROptInTrainDistribution.Reset(nil, "Concrete")` clears every Concrete row and doubles as the
  workaround. Owner fixture: two lines joined by a Large Station, no hub, Balanced at the dial on
  Concrete — line 2 must starve on v1.0.3 and receive after recommendation 1.
- **Xeryx**, hubless fixture (`tools/trains/hub/tests/hubless_smoke.py`): food Import 100, then 20,
  then untouched; deliveries per visit predicted ≈60-cap, ≈12, vanilla share. Low deliveries at 100
  refute 4.2.
- **TheGodUncle**, one sitting, Export one resource with the receiver untouched: (a) D16 and D17
  off → depot ≈81% of the line total; then receiver set to vanilla "accept" → nothing moves;
  (b) D16 on → receiver sits near 10 per visit; receiver Import 100 → depot drains to the
  receiver's free capacity. Full depot with room free refutes 4.3.
- **Hub junction (§5):** same Large-Station fixture inside a hub network — line 2 must receive on
  v1.0.3 already.

## 8 · The two reports outside this fix

- **Xeryx, carry +1 per reload (D09).** Our code is symmetric on load: `ReapplyDials` runs on
  `PostLoadGame` ([Opt_DroneStatDials.lua:149](../../../Code/Opt_DroneStatDials.lua#L149)) and the
  engine's `SetLabelModifier` subtracts exactly the saved modifier before adding the new one
  (`Lua/LabelContainer.lua:59-78`). [D09](../bugs/D09.md) rows 30-33 record one reload at +1
  reading carry 2, not 3 (1.0.7, no third-party mod), and the owner's 1.1.x play showed no growth.
  Likely an interaction with the player's capacity mod (it bakes the current value into the base,
  or drops our `label_modifiers` entry while leaving our contribution in the running total).
  Affected saves would not self-heal. Control: save at +1, reload five times, print after each
  `g_Consts.DroneResourceCarryAmount, g_Consts.base_DroneResourceCarryAmount,
  g_Consts.modifications.DroneResourceCarryAmount.amount,
  #g_Consts.modifications.DroneResourceCarryAmount,
  UIColony.label_modifiers.Consts.SMRFixPack_DroneCarryDial` — our mod alone, then with the other
  mod. Ask the player which mod.
- **Brad, trains stuck at Universal Tunnels.** Nothing we ship can hold a train at a tunnel unless
  a Train Hub is on that line. Vanilla tunnels cannot be built underground (no
  `disabled_in_environment` override, `Building.lua:253` default), so the pair is two surface
  mouths and no map change happens (`TrackTunnel.lua:70` moves the train with `SetPos`). Candidate
  vanilla cause, unreproduced: `TrainPassThrough` marks the mouth busy before the traverse and
  clears it only after (`TrainTransport.lua:43-51`); a train interrupted mid-hop leaves the mark,
  and every later train from that side waits at `Train.lua:313-321`. `CanTrainTraverse` checks only
  that a mark exists (`:39-41`). If it holds up, it is the Fix Pack's, not this mod's. Ask: modules
  on, hub on the stuck line, other mods, a save and the newest log.

## 9 · Claims register for the independent check

Status key: **S** read in the session itself from the cited line; **A** subagent-derived, the
anchoring line spot-checked in the session; **U** subagent-derived, not spot-checked. Every claim
is falsifiable at its citation; the leg's job is to agree, refute or qualify each, in writing.

| # | claim | citation | status |
|---|---|---|---|
| 1 | `Code/` at HEAD equals tag `optin-v1.0.3` | `git diff --stat optin-v1.0.3 -- Code/` empty | S |
| 2 | Import target = percent × station's own max storage; vanilla station = 60/resource | `StationRows_40:188-191`; `Station.lua:74` | S |
| 3 | An Import row's floor is its whole stock; Export orders nothing | `StationRows_40:852`; `:838` | S |
| 4 | Vanilla gates a resource on the route-wide sum of supply-desired, then shares by storage | `Train.lua:896-897, 927, 933-937` | S |
| 5 | Export half ↦ vanilla policy "accept" ↦ supply-desired 0 | `ElevatorDepot_10:883, 1090-1113`; `Station.lua:975-980` | S |
| 6 | The depot's drone filter governs drones regardless of the vanilla policy | `ElevatorDepot_10:1403-1409` | S |
| 7 | Hubless view excludes depots; `effective()` is nil for them; depot floor 0, order = vanilla room | `StationRows_40:88, 197-199, 841-842, 851` | S |
| 8 | Depot lines pin untouched rows to the dial (owner 2026-10-05) | `StationRows_40:553-556, 806-809` | S |
| 9 | Hub path forwards: `child_need`, intermediate Import forwards, Export admits for children | `StationRows_40:510-516, 701-704, 622-623` | S |
| 10 | Row click cycle writes a row at every step; slider click writes Balanced; Ctrl+click broadcasts; only console Reset clears | `StationRows_45:34, 80-93, 184-189`; `StationRows_40:429` | S |
| 11 | Import inherits the dial as percent; vanilla dial default 10 units | `StationRows_45:56-57`; `StationBig.lua:15` | A |
| 12 | Concrete is 4th by SortKey; no positional loop in `Code/` | `Station.lua:110`; `Resources.lua:357-363,386`; the `ipairs` loops listed in 4.1 | U |
| 13 | View track = `next_track or self.track`, same as vanilla | `StationRows_40:891`; `Train.lua:863` | U |
| 14 | Vanilla "apply to all" policy broadcast has no caller in this build | `Station.lua:1060-1075` | U |
| 15 | `hubless_on()` is true with D16 **or** D17; both off ⇒ pass-through (one extra unload call) | `StationRows_40:95-99, 888` | A |
| 16 | Hub-side row caps unloads from a non-network track; no view there | `StationRows_40:593-628, 628-640` | S |
| 17 | D09 load path symmetric; one reload at +1 recorded as carry 2 | `Opt_DroneStatDials.lua:133-149`; `LabelContainer.lua:59-78`; `D09.md:30-33` | A |
| 18 | Vanilla tunnel busy-mark has no cleanup on an interrupted traverse | `TrainTransport.lua:39-51`; `TrackTunnel.lua:58,76` | A |
| 19 | Tunnels cannot be built underground; a hop changes no map | `Building.lua:253`; `TrackTunnel.lua:70` | U |

What the leg should also judge, beyond the register: whether recommendation 1's semantics table is
the right contract for "the way players expect"; whether one hop is enough; whether 5 (dropping the
depot pin) has a cost not listed; and whether any recommendation touches a persisted name (none is
intended — `SMROptIn_station_rows` entries keep their shape; "Default" means *absence* of a row).

## 10 · Not determined

- No player's save or mod list was seen; every "likely cause" is derived from code.
- Nothing was run in game; §7's predictions are the first thing to measure.
- Which capacity mod Xeryx runs, and what it does to `g_Consts`.
- Whether `train_track_routes` lets the hubless path enumerate a station's other routes as cheaply
  as the hub tree does; `Station:GetConnectedTrack` exists, cost unmeasured.

## 11 · Independent review — Codex, 2026-10-21

**Verdict: the hubless terminal behavior is real; the player-specific attribution is unproved,
and §6 is not yet a sufficient implementation design.** The junction and depot-dial cases
reproduce with archived native transfer bodies and request doubles. The review does not establish
what was in any player's save. In particular, the confidence percentages in §4.1 have no measured
basis, and finding a saved Concrete row alone would establish a precondition, not prove causation.

Review reader/action: the owner and the next design author can use this section to revise the
proposal before a behavior ruling or build. It creates no ruling and changes no shipping code.
Executed model attribution available in the transcript: **Codex, GPT-6 per session instruction**;
an exact runtime model identifier and effort were not exposed. No subagents were used for this leg.

### Evidence and scope

Working HEAD: `80766e74010ce667a2a2e6731e8c9af7e40caed1`. Commands executed from this repo:

```text
git rev-parse HEAD
git diff --exit-code optin-v1.0.3 -- Code/
python tools/doccheck.py --emit-fingerprint
python tools/trains/hub/tests/hubless_smoke.py
python docs/archive/station_rows_review_20261021/desk_check.py
```

The Code comparison exited zero. The fingerprint reported installed build **25579348**, matching
archived **1.1.1.406343**; its overall run was RED on an existing dirty-checklist date error:
`OI-52 is new, so its opened date is today, not 2026-10-04`. This is not a failed fingerprint or
a station-row finding. The pre-existing tree also contains unrelated arboretum work.

All game citations below resolve under
`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.406343\Src`, build **25579348**.
Abbreviations: **SR** = `Code/StationRows_40_TrainDistribution.lua`; **UI** =
`Code/StationRows_45_TrainDistributionUI.lua`; **ED** = `Code/ElevatorDepot_10_ElevatorDepot.lua`.
Both desk commands passed. They check parity of the native bodies inherited from the 405907
archive against 406343 before running them. Request objects, route traversal and scheduling are
doubles; neither command verifies engine scheduling, save serialization, pixels or player saves.

The independent [desk script](../../archive/station_rows_review_20261021/desk_check.py) and
[executed output](../../archive/station_rows_review_20261021/desk_check_output.txt) are preserved.
The script overrides the existing harness's deliberately large train hold to the vanilla
42-unit shared capacity (`Lua/Units/Train.lua:22`). Run it from the repository root.

| Independent desk scenario | Asserted result, resource units |
|---|---|
| Source 60, shared junction 0, far station 0; station capacities 60; one delivery on each line; junction Balanced 20 | source 48, junction 12, far station 0 |
| Same, junction Import 20 | source 48, junction 12, far station 0 |
| Same, junction Export 20 | source 60, junction 0, far station 0 |
| Same, junction untouched | source 30, junction 15, far station 15 |
| Source 60 untouched, receiver empty, capacities 60; receiver Import 20 | delivers 12 |
| Same, receiver Import 100 or untouched | delivers 30 in either case |
| Source Export 0, receiver Import 100, otherwise same | delivers 42, limited by the train |
| Depot double 250/250, ordinary receiver 0/60, depot policy accept, receiver default dial; rows off, two trips | depot 202, receiver 48 |
| Same, rows on, one trip | depot 240, receiver 10 |
| Both enabled endpoints accept, rows off | no balancing load; changing source to send permits a 42-unit load and changes its request desires |

These are single-resource fixtures using Metals; they demonstrate the resource-independent
mechanism, not a reproduction of Erion's particular Concrete save. Stock figures are observations
from the named script with the stated filters/fixtures, not game measurements.

### Claims register dispositions

The identifiers below match §9; no claim is silently inherited as verified.

| # | Disposition | Independent evidence / qualification |
|---|---|---|
| 1 | Agree | The `git diff --exit-code` command above returned zero at the recorded HEAD. |
| 2 | Agree, bound the prediction | SR:188–191 and `Lua/Buildings/Station.lua:74` give the target and base capacity. Import 20 at an empty unmodified station is a 12-unit target; delivery also depends on source floor, reservations and free train capacity. It is not a throughput guarantee. |
| 3 | Agree for the configured hubless path | SR:832–852: Export orders zero and Import holds its current stock against pickup. Disabled resources and the separate unload path need their own treatment. |
| 4 | Qualify | `Lua/Units/Train.lua:891–908,934–969`: positive route desire enables ordinary balancing, but the zero-desire path can still evacuate forbidden stock. The total also includes cargo on every train in the route. “Only if” is too broad; it is correct for the fixture with both endpoints enabled and no forbidden stock. |
| 5 | Agree on the mapping, correct the UI story | ED:882,1092–1110 and `Station.lua:976–980` yield supply desire zero for hand-out. `Station:ToggleAcceptResource` is the normal store/disabled cycle (`:1053–1058`), not a click to accept. `ToggleTransportResource` cycles default → send → accept → default (`:1061–1075`), takes two steps from default to accept, and does not itself call `SetDesiredAmount`. The report's one-click player scenario is unsupported. |
| 6 | Qualify; the inference used by recommendation 6 is false | ED:1400–1408 filters which requests reach DroneControl. It does not replace their desired amounts. `Station.lua:976–986` sets supply desire to zero for accept and full capacity for send, with the opposite demand desires. The desk check confirms that mutation. An unchanged direction filter is not proof of unchanged drone scheduling; shuttles explicitly bypass that filter too. |
| 7 | Agree | SR:87–88,195–199,832–852 excludes depots from ordinary rows; its non-row order is demand target (available room after reservations), floor zero. Correct the original order citation to SR:842–843. The actual depot's row writer still controls enabled state and native requests. |
| 8 | Behavior agrees; owner attribution refuted | SR:554–556,794–810 pins ordinary rows on depot lines. **D16.md:25–38 explicitly calls the depot exception an agent decision, not ruled, and says that exception has no live run.** The owner's recorded ruling preserves vanilla balancing for untouched hubless rows. Dropping the exception is not accurately described as reversing that owner's ruling. |
| 9 | Agree on the mechanism, qualify “cannot happen with a hub” | SR:492–516 recursively computes branch demand; :700–705 permits intermediate Import surplus; :637–642 admits Export transit/child demand. The original Export citation :622–623 only detects a child. These mechanisms do not establish liveness for every setting, full junction, topology or old cargo state. |
| 10 | Qualify | UI:34,80–99,184–189: entering disabled does not write a new row in an ordinary click; existing saved settings remain. Slider edits retain the current mode and create Balanced only from an untouched Balanced state. Ctrl broadcasts within the city, skips the originating station and depots, and only writes rows where the network gate permits. There is no reset action in the inspected panel code; SR:429–457 implements Reset. Disabled → Balanced, not Import. Two clicks from Balanced do land on Import, but the first click is Export, not “off.” |
| 11 | Qualify | UI:53–59 inherits an existing saved percent, otherwise converts the dial. Untouched 10/60 rounds to 17%; 17% of 60 targets 10.2 units, subject to whole-unit train allocation. `Data/BuildingTemplate/StationBig.lua:14–15` supplies the base dial. Import does not always start from that dial if a previous row exists. |
| 12 | Partly supported; ordinal not independently established | The sorting code is **CommonLua/Libs/Resources/Resources.lua:351–363,385–387**, not `Lua/Resources.lua`. `Station.lua:110` copies the preprocessed list; `Data/Resource.lua:68,102,133` supplies the named sort keys. The reviewed SR/Floor loops use full `ipairs`, with no Concrete transfer branch in those bodies. A fixed fourth position would additionally require the complete preprocessed runtime resource list, including mods; this review does not certify that ordinal or a pack-wide absence of all positional behavior. |
| 13 | Agree, narrow the inference | SR:891 and `Train.lua:863` both choose `next_track or self.track`. This rules out that particular track-selection mismatch, not every possible multi-track defect. |
| 14 | Agree only as a literal-source search result; correct what broadcasts | `rg --no-ignore -n 'ToggleTransportResource' <archive>/Src` finds just `Station.lua:1061`, the definition. No literal caller in the decoded archived source; this does not exclude dynamic dispatch or engine callers. Its `all` flag applies one policy to all resources of the same station. The city-wide station broadcast is `SetAcceptResourceState`, `Station.lua:1021–1025`, and is a different operation. |
| 15 | Agree with the existing-hub exception | SR:95–99 enables hubless rows for D16 or D17; :888 performs an extra unload before delegating. With both off, a genuinely hubless line delegates. Existing placed hubs keep operating and can still manage their networks (`:91–93,899–901`); toggles off alone do not imply vanilla everywhere. |
| 16 | Qualify | SR:656–679 declines a hub allocation view on an unrelated line, and :791–793 declines a local view if a member is hub-owned. A saved hub row can still affect unload via :594–645. The cap has transit/overflow/from-child exceptions (:635–642), so it is not invariably the simple row amount. Several cited line ranges in §5 miss the current implementation. |
| 17 | Agree on idempotent intent and the historical read; no interaction diagnosis | `Opt_DroneStatDials.lua:127–149`, `Lua/LabelContainer.lua:59–78` remove the previous registered modifier before applying the replacement. D09:31–34 records carry 2 after a load with +1 still selected. It is a historical observation, not a fresh repeated-reload test or proof of compatibility with an unidentified mod. The proposed other-mod explanation and non-self-healing assertion remain hypotheses. |
| 18 | Agree as a candidate mechanism, not an observed cause | `Lua/TrainTransport.lua:43–50` has no protected cleanup around the yielding traverse; `TrackTunnel.lua:58,76` sleeps. A normal early return from TrainTraverse still reaches the outer clear; an abort/error that prevents return is the concern. A decoded-source grep for `trains_traversing` finds the default/read/set/clear sites only (command/scope below). The report has not established that the player's command was aborted or that the mark persisted. |
| 19 | Supported for the inspected base-game tunnel template/path | `Data/BuildingTemplate/UniversalTunnel.lua:3–27` selects TrackTunnelBase and omits an environment override; `Lua/Buildings/Building.lua:253` defaults to excluding Underground/Asteroid. `Lua/Buildings/TrackTunnel.lua:40–80` uses positions, with no map-switch call in that body. This is a base-template/source conclusion, not proof about modded placements or the player's save. |

Search receipts for the narrow absence claims above, against decoded archive source, build
25579348 (not a fresh runtime-pack parity assertion):

```text
rg --no-ignore -n 'ToggleTransportResource' B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src
rg --no-ignore -n 'trains_traversing' B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src
```

Presence-side reconciliation: the first has its definition at Station.lua:1061; the second has
TrainTransport.lua:4,40,46,47,49 (default, read, initialization, set, clear). No broad claim that
the fix pack cannot affect trains is needed: it contains connector, tunnel-power and salvage
code. Nor does the absence of a direct tunnel-busy hook prove that Station rows cannot alter
train departure behavior. Brad's case remains unattributed.

### Changes needed in the proposal

**1 — Relay behavior is a sensible goal, but one hop is insufficient.** Consider
source — J1 — J2 — consumer on separate lines: if J1 and J2 are at their local targets and
only the consumer is short, a scan of J1's adjacent station deficits sees no deficit at J2.
Demand has to propagate beyond that local horizon. Calling a recursive calculation “one hop”
does not specify its termination, accounting or cost.

The route index also has aliases: `Lua/TrainTransport.lua:328–332` assigns the same route
object to each segment key. Counting table keys as independent lines double-counts demand;
`Station:GetConnectedTrack` finds an aligned continuation (`Station.lua:931–957`), not all
of a station's routes. A revised design can use distinct route objects and directed
station/route edges, with an explicit rule for cycles and competing paths, cargo already in
transit, inbound reservations, unavailable surplus and people-only legs. A visited set stops
recursion but alone does not decide which competing route may spend the same demand or supply.

The proposed Import semantics conflict with the proposed default at full capacity. At a
60-unit junction, Import 100 reserves 60 and leaves no space for stock above its floor, so
“forward above N” cannot relay anything. This also qualifies §5's blanket hub reassurance.
The product decision is whether a full Import reserve deliberately blocks transit or transit
may use part of that reserve. A solver cannot satisfy both promises using the same physical
store. Equivalent staging-headroom concerns apply to a full Balanced target.

The untouched path also merits a narrower promise: where another station has a saved row,
SR:820–830 approximates a vanilla share from stations plus **this train's** cargo, whereas
vanilla `Train.lua:903–908` includes every train in the route. This is a source-derived
discrepancy, not a measured additional defect. A revised multi-train test would decide its
practical effect. Recommendation 1 should not promise to fix Erion outright before reproducing
the player's relevant state.

**2 — Better defaults help first use, but do not repair existing settings or guarantee supply.**
Import 100 removes the low receiver cap; the desk result still gives 30 from an untouched source,
and the ordinary train carries at most 42 shared units. Preserve deliberate saved percentages
unless an owner chooses a migration. Specify whether switching modes resets a deliberate slider;
the proposed 100/0 behavior would currently do so on every mode change if implemented literally.
A separate storage-capacity mod cannot be dismissed without identifying it: a change to the
station's max capacity changes this calculation, while a change only to an external depot
affects drainage/storage behavior rather than this target formula.

**3 — A visible Default is useful for hubless rows, with explicit scope.** It can be represented
by row absence with no new mode string in saves. The proposed cycle's rationale needs the
correction in claim 10. Reset is not automatically safe to wire into the panel: SR:429–457
clears both local settings and matching hub settings. A UI reset needs to target the settings
currently being edited, preserving the dormant other set. On a hub, row absence currently means
Balanced at the dial, not vanilla sharing; a “Default (vanilla)” label there would be false.

**4 — Depot integration is broader than changing effective().** Reading `HubEntry` before
`IsRowStation` would expose depot rows only at callers that actually use effective. If the depot
pin is removed, SR's local `row` and `configured` helpers (:801–814) still read only saved
ordinary rows. Its hubless unload branch (:571) also excludes depots. Both allocation and unload
need a coherent depot entry contract, including disabled and lone halves. With D16 and D17 off,
`hubless_on()` still prevents this solver entirely: it cannot fulfill a D18-only slider promise.
That independent-module behavior needs an explicit design choice, not an implicit dependency.

Use the existing surface target in both directions if reusing HubEntry. ED:1395–1396 gives
fixed 100/0 only to the underground half; the surface Import uses its slider. §6's blanket
“Import half at 100” would discard an existing surface control and is not equivalent to the
current hub implementation.

**5 — Removing the depot exception has costs beyond replaying one test.** It changes the
behavior of existing untouched stations on depot lines and increases receiving stock, which can
reduce stock retained in the depot or available to its cabin/other destinations. That may be
desirable, but it is a behavior change. D16:33–38 establishes that the exception was an agent
choice and was not independently seen live; do not present it as an owner ruling being reversed.
The general record-the-behavior-ruling duty still applies to an eventual build.

**6 — Do not adopt the send remapping as a proven isolated fix.** The gate-opening arithmetic
is correct, but the same policy writes the drone/shuttle-facing request desires. Direction
filtering and desired-amount priority are different controls. A proposed train-only desire
override could avoid that particular mutation, but it would still need a D18-only integration
design and scheduling tests. No remedy is approved by this review.

**7 — Clarify the units and configuration honestly.** The current rollover already states
percent of capacity and the corresponding amount (UI:109–115). Explicit station capacity and
the source/transport limits would make it clearer. Tooltip changes alone do not satisfy the
owner's stated desire for functioning hubless sliders.

**Save contract.** None of these goals inherently requires renaming a persisted field or
changing the `{mode, percent}` shape. Default as absence is compatible in shape. However,
reinterpreting an existing row, globally resetting settings, overwriting mode percentages,
changing the saved native `transport_policy`, or changing the meaning of an absent hub/depot
row has behavioral compatibility consequences even when every name is preserved. The build
design needs to distinguish those from a cosmetic or text-only change.

### Handoff and limits

This review is complete as a source-and-desk check of the report. The next useful artifact is
a revised behavior proposal resolving transit versus full reserves, multi-hop routing, active
versus dormant reset scope, and depot-only operation. Owner decisions about that proposal belong
in this mod's `docs/PLAYTEST_CHECKLIST.md` when requested; this review neither asks for nor records
a ruling. An eventual attended fixture should cover a simple junction, consecutive junctions,
a cycle, multiple trains, Import 100 at a junction, a full destination, mode changes with cargo
aboard, and depot-only/rows/hub configurations with Drone Access both ways. These are proposed
acceptance cases, not newly scheduled playtests.

Player attribution remains open pending saves/settings and the unnamed carry mod. The
all-stations Concrete Reset in §7 also clears hub Concrete settings through SR:442–457; use
the narrow affected-station control on a copy when diagnosing, rather than treating a global
settings wipe as evidence of one cause. A failed delivery at Import 100 alone does not refute
the low-cap mechanism: source floors, train capacity, reservations and drainage must be controlled.

Shipping code and module status are unchanged. Review artifacts are uncommitted; the existing
checklist error prevents a green documentation gate, so no commit was made.

## 12 · Revised proposal — Claude Fable 5.1, second session, 2026-10-21 (answers §11)

**Status: a proposal with a desk-checked prototype. No owner ruling is recorded here and no
shipping code changed.** Written for the owner's rulings and for the next independent check.
Everything measured below comes from
[`docs/archive/station_rows_proposal_20261021/`](../../archive/station_rows_proposal_20261021/):
the prototype `StationRows_40_TrainDistribution.proposal.lua`, its `proposal.diff` against the
shipping file, `proposal_check.py` and its output, and `hubless_smoke_on_proposal.py` with its
output (the shipped hubless smoke run against the prototype). Check run at HEAD `5ba8f3f`;
`git diff --stat optin-v1.0.3 -- Code/` still prints nothing. Shipping
`Code/StationRows_40_TrainDistribution.lua` sha256 `b0de6db1…255e`, prototype `ecec2df9…62a`.
Same harness as §7 and §11 (archived native Train and Station bodies, request and route
doubles, the base train's 42-unit hold); same limits: no engine scheduling, saves, drones, UI
or player saves.

This session also re-read §4.3 on its own before reading §11; the two reads agree with each
other and with §11's dispositions of claims 5, 6, 8 and 14. Three things §11 did not reach are
in 12.3 and 12.5: the share arithmetic that still strands 81 percent at the depot after §6's
items 1, 4 and 5; the depot's own slider default of 4 percent; and the reachable gate trap.

### 12.1 One fix

The three train reports fail in one function, the hubless view in
`Code/StationRows_40_TrainDistribution.lua` (`local_train_view`, with the hubless branch of
`Train:UnloadAll`). A set row is applied as a hard terminal pin on every line the station
touches, and a member that refuses to take, an Export row or the depot's Export half, still
counts its whole capacity in the line's share, so its surplus strands. Erion's junction,
Xeryx's trickle and TheGodUncle's depot are three faces of that one gap. One rule closes all
three; the depot's valve is the leaf case of it.

### 12.2 The rule

> A row keeps its amount for its own station. What a station holds beyond that balances with
> the line as the base game balances, so cargo for other lines passes through a station that
> joins lines.

Per line and per resource, each member contributes four things. A row's number is a percent of
that station's own store, as today.

| member | reserve | orders for itself | stock it lets the line balance | capacity it balances with |
|---|---|---|---|---|
| untouched | 0 | 0 | all of it | its whole store |
| Import N, on one line | N | up to N | nothing; its stock never leaves | its whole store (the game's weight, so the line gives to it as to any station) |
| Balanced N, on one line | N | up to N | what is above N | its shortfall below N |
| Export N, on one line | N | nothing | what is above N | nothing |
| any set row, on a station that joins lines | N | Import and Balanced: up to N | what is above N | as above, plus the store beyond N (its relay room) |
| disabled resource | — | nothing | all of it (the game drains it) | nothing |
| a depot half | its surface row through the hub's existing read: Export = Export N, Import = Import N, the underground half fixed at 100 or 0, a lone half untouched | | | |

A member's balance share is the pool times its relay room over the line's total weight, capped
at its relay room. Its order is what it still wants for its reserve, plus its share less what it
already holds beyond the reserve, less inbound reservations, capped by its free room. Its floor,
below which it gives nothing, is reserve plus share; an Import on one line keeps all of its
stock. The pool counts the cargo aboard every train on the route, as the game counts it
(`Lua/Units/Train.lua:903-908` on 1.1.1.406343). "Joins lines" means a member of two or more
distinct route objects in the city's `train_track_routes`, counted by identity because one
object serves every segment of a line (`Lua/TrainTransport.lua:328-332`); the count is cleared on
the game's `TrainRoutesRebuilt` and in `D.Refresh`. There is no hop, tree, recursion or demand
propagation: pass-through is the base game's own diffusion, confined to the room beyond each
reserve. A line with a depot takes this view whatever the Station rows toggle says, as a hub's
network takes its rows; a set station row still needs the toggle. A line with no set row and no
depot stays on the native path, as the 2026-10-05 ruling has it.

### 12.3 Desk results, from `proposal_check_output.txt`

Resource units. "Shipping" is what §11's desk check or the shipped smoke prints for the same
fixture. The far station on the junction fixture is drained to its dial of 10 after each round,
as a consumer line would be.

| scenario | prototype | shipping |
|---|---|---|
| junction, untouched: source 60/60 · J 0/60 on both lines · far 0/60 | 30 · 15 · far 10 (got 15) | the same, native path |
| junction, J Balanced 20 (12 units) | 30 · 20 · far 10 (got 10) | 48 · 12 · far 0 |
| junction, J Import 20 | 30 · 21 · far 9 | 48 · 12 · far 0 |
| junction, J Export 20 | 36 · 18 · far 6 | 60 · 0 · far 0 |
| junction, J Import 100 | 30 · 30 · far 0 (no relay room, by design) | — |
| junction, J Balanced 20, four rounds | source 18 · J 23 · far kept at 10 every round | far 0 |
| leaf: Export 20 with 80 beside an untouched 0/100 | 20 · 60 | 40 · 40 (20 stranded above the floor) |
| leaf: untouched 10 beside Import 50 (the 2026-10-05 reporter's line) | 5 · 5 | 5 · 5 |
| leaf: Balanced 50 with 80 beside untouched; then from the neighbour | 50 · 30; nothing back | the same |
| leaf: Export 20 with 80 to Import 50 | 30 kept, 50 aboard | the same |
| depot, rows OFF (D18 alone): Export half 250 at the 4 percent floor, receiver 0/60, two trips | 190 · 60 | 202 · 48 |
| depot, rows ON, same line | 190 · 60; refills to 52 after the receiver's drones take 50 | 240 · 10 |
| depot: an Export half beside a neighbour set to Export 0 | the half orders nothing | — |
| depot, rows OFF, receiver's Desire Amount at 0 | 42 delivered (the view opens the gate) | nothing moves |
| depot: Import half at its 4 percent default, station 60 | depot 10 · station 50 | depot 50 · station 10 |
| depot: Import half at 100 percent | depot 42 (one train) · station 18 | — |
| depot: an Import half asked to give | nothing aboard | — |
| depot: the train idle at the empty receiver | goes to the Export half | — |
| depot: a lone half, rows OFF | native: 208 · 42 | the same |
| save snapshot, hub ownership of a line | as before | — |

The shipped `hubless_smoke.py` run against the prototype passes every assertion but the two
that encode the call being replaced: a depot line without an entry now balances natively, 40 ·
40 instead of the pinned 10 · 70, and the depot's read is consulted on a hubless line. The
lone-half figures it prints are unchanged.

### 12.4 What changes for each report

- **Erion.** A row on the big station no longer makes it a terminal. Whatever Erion's Concrete
  row was, Balanced at a slider click, Import or Export, the big station keeps that amount and
  passes the rest between its lines, so Concrete reaches the far line again. This does not
  prove what was in Erion's save; it removes the mechanism §4.1 found.
- **Xeryx.** A row cycled to Import starts at 100 percent on a station of one line, not the
  dial's 17 percent, and the help names the number as a percent of this station's store. An Import still caps at its
  number; Import 100 at an empty station takes the share the game would give it from an
  untouched source (30 of 60 on the fixture), and more from a source set to Export.
- **TheGodUncle.** The surface Export half hands out everything above its slider floor to the
  stations on its line, with or without Station rows, with or without a hub; the receiver fills
  to its capacity and refills as its drones take from it. The slider is what the depot keeps,
  default 0 under 12.5. An Import half gathers up to its slider, default 100 percent, and never
  gives; it takes the share the game would give a 250 store, not everything above the stations'
  dials as the pinned line did.

### 12.5 §11's "changes needed", answered

1. **Relay.** No hop count to get wrong: the base game's diffusion over the room beyond each
   reserve. The four-round run shows a chain still flowing on later trips. Routes are counted by
   object identity, so aliases do not double-count. Import 100 on a station that joins lines
   leaves no relay room, and the help says so: lower the number to let cargo pass. A full
   Balanced target is the same case. The reserve wins; transit never spends it. The untouched
   share now counts every train's cargo on the route.
2. **Defaults.** A click to Export sets 0; a click to Import sets 100 on a station of one line
   and 50 on a station that joins lines, so cargo can still pass through, and the slider shows
   the number at once; a click to Default clears the row; the slider from Default makes Balanced at its value, and from Export or Import keeps
   the mode and changes its number. Rows already saved keep their numbers; no migration. The
   depot's unset targets follow the same defaults instead of the dial: Export 0, Import 100.
   That changes what an existing depot with untouched sliders does on load (12.6, R5).
3. **Default.** Row absence in the set being edited: the station's own table off a hub, the
   hub's entry for that station on one. A scoped clear, not `D.Reset`, which empties both. On a
   hub the title stays "Default" and the help says it holds the desired amount there.
4. **Depot.** The depot's rows enter the hubless view through the hub's existing read, surface
   slider in both directions, underground fixed, lone half untouched, Not accepted through the
   game's disabled path. A depot line takes the view regardless of the toggle, so D18 alone is
   served; that is the explicit design choice §11 asked for. At the depot itself the train
   unloads natively, so leftover unassigned cargo can still land in an Export half; it is
   exported again on the next visit.
5. **The dial pin** goes. It was the agent's call of 2026-10-05, never seen live; the rule
   above replaces it with what the 2026-10-05 ruling asked for, the game's balancing.
6. **The "send" remapping** is dropped. It would make Drone Access on an Export half do nothing,
   and the view now opens the gate itself, which also closes the reachable trap: a receiver
   whose Desire Amount sits at 0 no longer freezes the resource.
7. **Text.** Import and Export help name the number as a percent of this station's store and say
   that a station joining lines carries other lines' cargo in the room beyond its number, and
   holds that cargo on its way, so its panel reads above the number. A tooltip line appears on a
   joining station whose number leaves no room at all. The Import help says an Import takes
   from an untouched source what the base game would send, and that Export at the source sends
   everything. The depot's Export help names the slider as what the depot keeps. The
   untouched-row help stands.

### 12.6 Decisions for the owner

Listed, not ruled. They go on `docs/PLAYTEST_CHECKLIST.md` only when the owner asks, after the
next independent check.

- **R1** the rule in 12.2 as the contract for hubless rows, including: the reserve wins, a station
  that joins lines relays only its room beyond the reserve, and Import 100 there blocks
  pass-through.
- **R2** a line with an Elevator Depot takes the hubless view whatever the Station rows toggle
  says, as a hub's network takes its rows.
- **R3** the depot-line dial pin is dropped (reverses the agent's 2026-10-05 call, not the ruling).
- **R4** the defaults and the Default state in 12.5 items 2 and 3, including Import's 50 on a
  station that joins lines.
- **R5** the depot's unset slider targets change meaning on existing saves: an Import half with an
  untouched slider gathers to 100 percent instead of 10 units, an Export half keeps 0 instead of
  10. Alternative: keep the dial default for existing depots and apply the new one only to rows
  the player sets.
- **R6** the Export and Balanced leaf change in 12.3 (surplus above a set number now drains to
  untouched neighbours instead of stranding) is accepted as part of R1.

### 12.6a Where players may still be surprised

Judged against the owner's words in §2, after the rule and the defaults above:

- **Import 100 on a station that joins lines** stops pass-through of that resource, because a
  full reserve leaves no room to carry anything between lines. Nothing physical satisfies both
  wishes once the station is full. The 50 default keeps pass-through alive on a first click; the
  tooltip line names the cause when a player drags it to 100; the far line going quiet is then
  the player's visible setting, not a mystery.
- **Export or Balanced on a joining station reads above its number**, by its transit share.
  Export at its default of 0 on a joining station behaves as untouched. The help sentence in
  item 7 is the whole mitigation; a rare setting.
- **An Import takes from an untouched source only the base game's share.** Deliberate: the
  untouched source keeps the balancing the 2026-10-05 ruling gave it. The help points at Export
  at the source.
- **The click order is older than this fix and unchanged.** Default, Export, Import, Not
  accepted: a base-game habit of one click to switch a resource off lands on Export, which local
  drones then fill. Under the shipped code that click on a joining station starved its far line;
  under the rule it no longer does. Making a plain click toggle Default and Not accepted as the
  base game does, with the slider or a second control choosing Export and Import, would touch
  the 2026-09-26 row-shape ruling; named here, not proposed.
- **A hub network is unchanged**, so a junction inside one keeps the hub's rules and §11's
  concerns about it.

### 12.7 Build and test, without a sitting

One change set, one release (v1.0.4), one outbox entry; replies to the three players after it
is live. Files: `Code/StationRows_40_TrainDistribution.lua` (the archived diff, cleaned of its
prototype comments), `Code/StationRows_45_TrainDistributionUI.lua` (cycle, defaults, Default,
the scoped clear, help), `Code/ElevatorDepot_10_ElevatorDepot.lua` (unset target defaults, help),
`tools/trains/hub/tests/hubless_smoke.py` (the two assertions), `proposal_check.py` promoted to a
test under `tools/trains/hub/tests/`, then `module_gates_smoke.py`, the parse sweep and
doccheck. No persisted name changes shape or meaning except the absent depot target under R5;
no new wrapper; no vanilla method replaced; the hub path is untouched. What is not measured
before shipping: engine scheduling, drones, saves, the panel. That is the same basis the
2026-10-05 fix shipped on, with one live look after; here the live look is the reporters'
replies and the owner's play. The one cheap in-game check that covers a new risk, if the owner
wants one: a Large Station joining two lines with a Balanced row, no hub, and the far line
receiving.

### 12.8 For the second independent check

- The contract in 12.2 against the owner's words in §2, in particular Import 100 blocking
  pass-through on a station that joins lines, the reserve winning over transit, and whether the
  50 default and the tooltip line in 12.5 are enough, or 12.6a's click-order change belongs in
  this fix after all.
- The weights: an Import weighs its whole store, a Balanced row its shortfall, an Export nothing,
  a joining station adds its room beyond the reserve. Each has a reason in 12.2; a better choice
  is welcome.
- Junction detection by route identity: loop routes where a station appears twice, three or
  more routes through one station, tracks under construction (the route walk stops there),
  tunnels.
- The same relay room ordered on two lines at once; it is bounded by the demand target and
  inbound reservations, as the game bounds its own balance.
- The depot entry contract (surface slider both ways, underground fixed, lone, Not accepted),
  depot-only operation, and native unloading at the depot.
- The defaults' effect on existing saves (R5), and whether the Default state can be represented
  by absence without a new mode string in `SMROptIn_station_rows`.
- The prototype diff line by line, and anything the check scenarios do not cover: a disabled
  resource beside a set row, a people-only leg, an empty line, a station with no demand request.

### 12.9 Limits

No game was launched. Every figure above is a desk observation from the named script against
request and route doubles and the archived native bodies, not a measurement. No player's save
or mod list was seen; 12.4 removes mechanisms, it does not prove causes. The hub path and §11's
concerns about junctions inside a hub network are unchanged and outside this proposal. Brad's
tunnels and Xeryx's carry dial stay in §8.

**Executed model:** Claude Fable 5.1 (`claude-fable-5-1`), this session; no subagents. Skills:
smr-orientation, doc-editing.

## 13 · Second independent review — Codex, 2026-10-21

**Verdict: keep the local diffusion approach as a candidate; correct the allocation weights and
depot unloading before treating §12 as ready to build.** This review reproduced the supplied
checks and added counterexamples to the stronger promises. It does not approve a behavior
ruling, a shipping change or a release without an in-game check.

### 13.1 Evidence

HEAD `5ba8f3f2a95be26d08f0edb4cfdd34a0ebfc8ed6`; shipping `Code/` still equals
`optin-v1.0.3` (`git diff --exit-code optin-v1.0.3 -- Code/` exited zero).
Prototype SHA-256:
`ecec2df95a2e9b80a83b0062a916a963a58f8b29b8b2bae42a80cb93a952d62a`.
`python tools/doccheck.py --emit-fingerprint` reports installed build **25579348**, archived
**1.1.1.406343**, and GREEN. The prior OI-52 error in §11 is historical and no longer blocks this
tree. All game citations in this section refer to that build's archived `Src` tree, not the
live installation. **P** below denotes the archived proposal Lua file in §12.

Executed from the repository root:

```text
python docs/archive/station_rows_proposal_20261021/proposal_check.py
python docs/archive/station_rows_proposal_20261021/hubless_smoke_on_proposal.py docs/archive/station_rows_proposal_20261021
python docs/archive/station_rows_second_review_20261021/second_check.py
```

The supplied scripts passed. The new [independent script](../../archive/station_rows_second_review_20261021/second_check.py)
and its [output](../../archive/station_rows_second_review_20261021/second_check_output.txt)
preserve the additional checks. A successful exit means its witnesses reproduced; the lines
marked COUNTEREXAMPLE are failures of proposal claims, not release passes. The script copies
the archived prototype and the shipping Floor helper into its own scratch directory. It never
writes shipping code or prior archive artifacts.

Native Train/Station bodies are the existing harness's pinned bodies with parity checked against
406343. The additional route-mode cases also execute archived
`Lua/TrainTransport.lua:371`'s `ForEachStationAlongTrack` body; its file hash is printed.
Requests, topology construction, train movement and consumption remain doubles. The added
fixtures use Metals, a 42-unit train hold, and the capacities specified below. The supplied
proposal script temporarily uses a larger hold for its leaf comparisons, and the modified
hubless smoke retains its original large hold; §12's blanket 42-unit description does not apply
to those assertions.

### 13.2 Corrections demonstrated by counterexamples

**A — A satisfied Import still strands an Export's surplus (design defect).**
On one line, give each station capacity 60: source Export 0 holds 60, an untouched receiver
holds 0, and an Import 100 already holds 60. After delivery and another attempted trip, the
stocks are **30 / 30 / 60**. The Export still has 30 above its floor; the untouched receiver
still has 30 free; the next trip moves nothing. Total stock remains 120.

P:857–859 gives the full Import weight 60, but :867 excludes its stock from the pool and
:897–904 gives it no order. The untouched receiver's share is therefore only 30. Its unused
potential share is not redistributed. This is precisely the class of stranded-surplus problem
§12.1 and §12.4 promise to remove, now caused by an Import that cannot receive rather than an
Export's capacity. The prototype implements §12.2's unconditional Import weight here; changing
that single line to match the prose will not solve it because the prose itself has this flaw.

Recommended revision: distinguish a station's intended balancing weight from the stock it can
actually receive, and settle how unused receiving shares are redistributed while respecting
source floors. A full Import with no releasable stock and no order cannot absorb part of an
Export's distributable surplus forever. Preserve the known untouched-source/Import first-fill
case while testing a full Import, a partially satisfied one and inbound reservations. A revised
formula needs those controls, not just the present two-endpoint examples.

**B — An empty Export has a receiving weight the contract says is zero (implementation defect).**
On one line with capacities 60, put 60 at an untouched source, leave an untouched receiver empty,
and add an empty Export 100. The prototype delivers **20**, leaving **40 / 20 / 0**. The declared
zero Export weight would split the pool between the participating untouched stores, delivering
30 and leaving **30 / 30 / 0**.

P:860–861 applies `Max(n - stock, 0)` to both Balanced and Export. §12.2 instead assigns zero
weight to an Export leaf. That branch needs a distinct Export case; a joining Export should
add its actual relay weight, not an unsolicited reserve shortfall. This is separate from A:
fixing the Export branch does not remove the full-Import counterexample.

**C — The depot's Import cap is not enforced at unload (contract gap).**
An empty capacity-250 depot with Import 4 has a target of 10. Give its visiting train 42 units
of cargo and call the normal `UnloadAll`. The prototype puts **42** into the depot, both when
the cargo is unassigned and when it is an existing assignment to this depot. In the latter
case, the state models an assignment made before lowering the target. The other endpoint stays
empty and stock is conserved. D16 and D17 are off in this witness, so it also exercises D18-only
behavior.

P:583 requires `D.IsRowStation(st)`, which excludes the depot. It therefore delegates to native
unloading, whose physical-room check is in archived `Lua/Units/Train.lua:787–830`. The new
allocation order bounds new bookings; it cannot retroactively bound retained cargo or a new
slider setting. §12.5 deliberately accepts this exception for an Export half, but the same
exception also breaches “Import gathers up to its slider.” Import 100 as a new default hides
the issue at that setting, but players can still choose a lower target.

Recommended revision: specify and implement depot unload behavior for both Import and Export,
including reservations and whole existing assignments. Either keep the Import cap at unload,
as ordinary leaf rows already do, or explicitly propose an overflow exception for the owner.
The current unconditional Import-cap wording is false. No cabin/drone behavior was simulated;
later cabin drainage does not prove the receiving cap held.

### 13.3 What the additional checks support

| Case / filter in `second_check.py` | Observed result and limit |
|---|---|
| Two sources, each 60/60, on distinct lines booking the same empty Balanced 20 junction of capacity 60 before either unloads | Combined booking 36; reverse arrival order delivers 36 with 24 free. Request targets restore and total stock reconciles to 120. No overfill in this ordering. |
| Untouched source 60/60, Import 100 receiver 0/60, another train already carrying and reserving 20 for that receiver | Current train loads 20; receiver retains 20 unreserved free room. The other train's cargo is counted. |
| Station in distinct route objects, aliased keys, a repeated member in one route, then `TrainRoutesRebuilt` | Distinct routes create a junction; duplicate keys/members do not. Removing the other routes and sending the message invalidates the cached result. |
| Disabled source holding 30 beside an empty Import 100 | All 30 drain. A separate missing-destination-demand fixture books nothing. These are bounded request-layout checks, not a guarantee for arbitrary malformed stations. |
| Empty Export 0 and Import 100 endpoints | No cargo manufactured, no pickup stop and no division error. |
| Source → J1 → J2 → consumer, capacities 60, both junctions Balanced 20; source refilled to 60 and consumer drained each round | Consumer receives 131 over 12 rounds, including 13 in the last round. Remaining stock plus consumed stock equals initial stock plus replenishment. This actually exercises consecutive junctions. |
| Cycle source → J1 → J2 → source with a J2 → consumer branch; same capacities, reserve settings and replenishment/drain schedule | Consumer receives 131 over 12 rounds, 13 in the last round. The script checks conservation including carried cargo and capacity bounds. Native route walking is used here. This is one directed service order, not a convergence proof for every cycle. |

The last two checks support the revised choice to use local diffusion rather than propagate
remote demand. §11's one-hop objection applied to the abandoned demand-forwarding algorithm;
it is not a reason to require a tree or recursive solver for this version. Route deduplication
by identity is also appropriate for the archived route index. Tunnel traversal contributes
segments to an edge (`Lua/TrainTransport.lua:264–269`), so counting aliases as routes would have
been wrong; the proposal avoids that error.

**Cargo reachability still needs a product definition.** `IsJunction` counts structural route
membership, not usable cargo routes. With an Import 50 station holding 60/60 on one cargo line
and one people-only line, the actual route walker blocks freight on the people line, but the
prototype returns **15** to the ordinary station on the cargo line. The Import becomes a giving
junction although it has no second usable cargo route. A retained indexed route with an edge
under construction produces the same result: the walker stops there, but membership still
permits surplus to leave on the working line. That fixture proves the conditional behavior
when such a route is indexed; it does not prove how long a real rebuild retains it.

This follows the literal “distinct route objects” definition, so it is not a mismatch between
that definition and its implementation. It is a consequence to include in R1/R4, or a reason
to define junctions using usable cargo connectivity and invalidate that classification when
transport mode/construction changes. A tooltip about cargo passing to another line does not
explain an Import sending cargo back when its other line is passenger-only. A looping route
with repeated station membership remains one route under the proposed definition; the identity
test is correct for that definition. Real route reconstruction was not executed in this leg.

### 13.4 Contract, defaults and scope

The reserve-winning choice in R1 is coherent and respects finite storage. Import 100 and
Balanced 100 at a junction deliberately have no forwarding room. Import 50 on first selection
leaves room, but it does not repair a saved 100-percent setting, prove sufficient throughput,
or ensure that all lines are usable for cargo. §12.4's “whatever Erion's Concrete row was” is
therefore too strong even before the new counterexamples: the proposal intentionally retains
the full-reserve blocking case. Player-specific causation remains unproved.

Default as absence remains compatible with the stored row shape, provided the proposed clear
targets only the active local or hub settings. The scoped clear, revised click defaults,
tooltip warning and R5 target defaults are **not implemented in the archived prototype**.
Their treatment in §12 is a design proposal, not a tested UI result. Keeping the established
click order is a reasonable scope choice for this transport correction; the audit provides no
new evidence that a second control is necessary. Clear mode labels and a genuine reset still
need their own UI validation.

R5 accurately identifies a change to absent saved depot targets. Preserving old absent values
until the player explicitly selects a new setting is the less disruptive option; applying
100/0 to all absent targets is an explicit product choice, not a data-shape migration. The
owner can choose either, with the consequence stated. It also affects **hub-managed depots**:
`Code/ElevatorDepot_10_ElevatorDepot.lua:1395–1396` calls `D.Target` for the surface half on the
hub path too. Revised row-click defaults can likewise affect hub rows unless deliberately
scoped. “Hub solver unchanged” is accurate for the archived core diff; “hub-network behavior
unchanged” is not accurate for the full proposed defaults change.

The D18-only allocation gate works in the tested paired-depot configurations without changing
native policy/desires; the old dial pin is removed and the dial-zero gate trap is addressed.
The real depot's entry contract is unchanged by this diff: surface target both ways,
underground 100/0, lone/disabled entries false. Those identities were checked in the shipping
reader in the first review; this leg uses doubles and does not claim a new real-depot run.
Dropping the send remapping is justified by the previously demonstrated request mutation;
the categorical claim that it would make Drone Access do “nothing” is not an engine measurement.

### 13.5 Test claims and the next revision

The supplied four-round liveness assertion is
`s4 < s1 or f4 == 10000`. Its second arm can stay true if the first delivery fills the consumer
and no later delivery happens. That fixture is one junction, not consecutive junctions. The
added checks above track continued delivery and conservation with replenishment/drainage.
The supplied hub-seam check verifies ownership and absence of an error, but records `calls`
without asserting the subsequent result; it does not prove unchanged hub allocation behavior.

§12.7's release-without-a-sitting proposal does not inherit authority from a previous release.
Current `docs/agent/WORKFLOW.md:315–318` calls for an attended A/B for a player-visible defect.
`docs/agent/FIX_POLICY.md` §8 waives the train modules' **fix-pack-absent** run, while retaining
the fix-pack-present run and both toggle directions. The brief should cite those current terms
or obtain an explicit owner exception; reporter replies are not a recorded substitute. No
sitting or release was requested or scheduled by this review.

The next revision has concrete work: repair A's full-Import allocation trap and B's Export
weight mismatch, settle C's depot unload contract, specify whether passenger/blocked routes
make a cargo junction, and narrow the hub/default and release claims. The existing reproduced
cases provide regression inputs. They do not authorize changing shipping behavior. The
owner-facing decisions in §12.6 can be presented after those corrections; no ruling or new
checklist item was created here.

Shipping code and module statuses remain unchanged. The prior report and prototype archive
were preserved; this section and its new evidence directory are the review artifacts. Executed
model attribution visible in the transcript: **Codex, GPT-6 per session instruction**; exact
runtime model identifier and effort not exposed. No subagents or game launches were used.

## 14 · Revision b of the proposal — Claude Fable 5.1, second session, 2026-10-21 (answers §13)

**Status: the three corrections in §13.2 and the junction definition in §13.3 are built into a
second prototype and desk-checked; §12's rule stands with its weights revised below. No owner
ruling is recorded and no shipping code changed.** Artifacts in
[`docs/archive/station_rows_proposal_20261021b/`](../../archive/station_rows_proposal_20261021b/):
the prototype `StationRows_40_TrainDistribution.proposal.lua` (sha256 `336e911d…`), its
`proposal.diff` against the shipping file (sha256 `b0de6db1…255e`, still equal to
`optin-v1.0.3`), `proposal_check.py` with its output, and the shipped hubless smoke run against
it with its output. HEAD `5ba8f3f`. The first folder is left as §13 cites it. Same harness and
limits as §12 and §13: archived native bodies, request and route doubles, no game run.

### 14.1 What changed, and why

- **Shares are water-filled (§13.2 A and B).** Each part of a member has a weight, how the line
  splits the pool, and a room, the most it takes. The pool is split by weight; any part that
  would get more than its room is held at its room and the rest is split again among the others,
  until no part is over its room. A full Import, with room 0, therefore takes nothing and its
  weight no longer dilutes the receiver beside it; an Export has no reserve part at all, so an
  empty Export 100 weighs nothing. The weights: an Import's reserve part weighs the whole store,
  the game's weight, so it is served as any station is; a Balanced row's reserve part weighs its
  amount; a joining station's relay part weighs the store beyond the amount; an untouched station
  weighs its store. Rooms: reserve = amount − stock − inbound reservations; relay = store − amount;
  untouched = the store.
- **A depot half unloads by its row (§13.2 C).** The hubless unload branch now takes a depot
  through the hub's read, with or without the rows module: an Import half unloads loose cargo
  only up to its target, keeps a whole old assignment above the target aboard as an ordinary
  Import row does, and an Export half refuses leftover cargo as an ordinary Export row does. A
  lone half unloads natively. §12.5's Export-half exception is withdrawn.
- **A station joins lines when it can exchange cargo on two or more routes (§13.3).** Routes are
  still counted by object identity, but a route counts only if the game's own walk from the
  station reaches another station on it that can take cargo. A people-only leg or a leg under
  construction stops that walk, so such a line is not a cargo line of the station. The count is
  cleared by `D.Refresh`, which the view already runs at most a second apart, and by the game's
  route rebuild. The transport-mode toggle itself sends no message (`StationsLink.lua:98-104`), so
  a changed mode is seen within a second of game time, not at once. The handler §12's prototype
  hung on `TransportLinkChanged` is gone: that message is about vehicles joining a link.
- **Inbound reservations** count once: against the reserve part first, the remainder against
  the relay or untouched part.

### 14.2 Desk results, from `proposal_check_output.txt`

Resource units; "§13 result" is what §13's script printed against the first prototype.

| scenario | revision b | §13 result |
|---|---|---|
| §13.2 B: untouched 60 · untouched 0 · empty Export 100 | 30 · 30 · 0 | 40 · 20 · 0 |
| §13.2 A: Export 0 with 60 · untouched 0 · Import 100 full, two trips | 0 · 60 · 60 | 30 · 30 · 60 |
| the same with the Import half full (30 of 60) | booked 30 for the Import, 30 for the receiver | — |
| §13.2 C: depot Import at 10, 42 loose aboard, native unload, D16 and D17 off | 10 kept, 32 stay aboard | 42 |
| §13.2 C: the same cargo assigned before the target was lowered | 0, the whole 42 stays aboard | 42 |
| an Export half with 42 loose aboard | refused, 42 stay aboard | — |
| a lone half with 42 loose aboard | 42 unloaded natively | — |
| §13.3: Import 50 full on one cargo line, second line people-only, train at the ordinary station | nothing loads; the station is not a joining station | 15 |
| the same second line made cargo-capable, after a refresh | the station is a joining station again | — |
| Import 20 (12 of 60) from an untouched 60/60 source | 48 · 12: the whole amount | — |
| Import 100 from an untouched 60/60 source | 30 · 30 | — |
| junction: untouched · Balanced 20 · Import 20 · Export 20 · Import 100 (source · J · far) | 30·15·10 · 30·20·10 · 27·22·10 · 34·19·7 · 30·30·0 | 30·15·10 · 30·20·10 · 30·21·9 · 36·18·6 · 30·30·0 |
| junction, Balanced 20, four rounds | source 18, J 23, far kept at 10 | the same |
| depot Export at the 4 percent floor, rows off and on; refill; dial-0 receiver; empty receiver's pickup trip | 190 · 60 in both; 52 after a drain; 42; goes to the depot | the same |
| depot Import at 4 percent, at 100 percent | 10 · 50; 42 · 18 | the same |
| the 2026-10-05 reporter's line; Balanced 50 beside untouched; Export 20 to Import 50; Balanced 80 with a 10 reservation; disabled drain; untouched line native | all as in §12 | the same |

The shipped `hubless_smoke.py` against revision b flips the same two assertions as before and
nothing else. §13's `second_check.py` run against revision b stops at its first witness, the
empty Export 100 leaf asserting 40 · 20 · 0, because that counterexample no longer holds; its
other two counterexamples are the §13.2 A and C rows above.

### 14.3 §13.4, answered

- **Erion.** §12.4's "whatever Erion's Concrete row was" is withdrawn. A row short of a full
  reserve on the big station relays again; Import 100 or Balanced 100 there still blocks, by
  the contract, and the tooltip line names it. Causation in Erion's save stays unproved.
- **Hub scope of the defaults.** The 50 default on a joining station applies only off a hub,
  where the relay room is the pass-through; on a hub network Import still starts at 100, since
  the hub's own tree forwards. The depot's absent-target default (R5) reaches hub-managed depots
  too, because the surface target is read on the hub path as well; the owner's two choices
  stand: apply 100/0 to every absent target, or keep absent values until the player sets a row.
- **The UI pieces** (click defaults, the Default state, the scoped clear, the tooltip line, the
  help text) remain design, not prototype. The transport correction is complete without them.

### 14.4 For the third check

- The water-filling: termination, rounding with three or more parts, and the order of parts
  (sorted by handle, so rounding falls the same way on every call).
- The weights: an Import's reserve weighing the whole store while a Balanced row's weighs its
  amount. Each has its reason in 14.1; a counterexample to either is welcome.
- The usable-cargo definition: its cost (one native walk per connected track per station, cached
  at most a second), and loop routes where a station appears twice.
- The depot unload rule against the cabin: an Import half capped at its target while the cabin
  takes stock down between visits, and whether a whole old assignment kept aboard can starve a
  line of its one train.
- The prototype diff line by line, as before.

## 15 · The build — Claude Fable 5.1, third session, 2026-10-21

**Status: built and desk-verified against the archived native bodies at `83149ea`; audit pending
(OI-53).** The owner fired `docs/agent/prompts/STATION_ROWS_RELAY_BUILD_high.md`, which ruled the
six decisions of §12.6 as amended by §14.3 (R1–R6, recorded verbatim in `docs/agent/bugs/D16.md`
and `D18.md`, the rule in the train spec §4.7). The prompt is deleted with this section. Nothing
here is tested in game; no pack, upload or player reply was made.

Commits, each verified before the next began (HEAD `5ba8f3f` at the start; `git pull` up to date):

| commit | unit |
|---|---|
| `8490c5e` | R1–R6 recorded; this report, its four archive folders and the prompt filed |
| `a731a20` | the 40 file: revision b's diff ported whole (prototype sha256 `336e911d…`, shipping before it `b0de6db1…255e` = `optin-v1.0.3`), its three prototype comments rewritten as the ruling's record; `hubless_smoke.py`'s two dial-pin assertions flipped; `proposal_check.py` promoted to `tools/trains/hub/tests/hubless_relay_smoke.py` without the temp-folder copy |
| `00e2dff` | the 45 file: the Default state and the click defaults (R4); `D.Clear` in the 40 file; `distribution_ui_smoke.py` |
| `83149ea` | the depot's unset targets (R5) and Export help; the stations' Import/Export help and the joining-station line; `wiring_smoke.py` |

Before any code moved, both archived checks were re-run from the repo root at `5ba8f3f` and
reproduced §14.2 (`proposal_check.py` PASS; `hubless_smoke_on_proposal.py` the same two FLIPs). The
engine names the port relies on were re-derived by grep in the 406343 archive (build 25579348):
`TrackConnectedObjBase:ForEachConnectedTrack(callback, ...)` passing `(track, destination)`
(`Lua/TrainTransport.lua:68`), `ForEachTrainInRoute` (`:485`), `Msg("TrainRoutesRebuilt")` (`:357`),
`routes[segment] = route` with the route a station list (`:328-332`, `:371-373`), and
`Station:GetResAcceptIcon` returning `resource_storing.tga` (`Lua/Buildings/Station.lua:1003-1004`).

### 15.1 Calls made within the authority

- **The cycle** is Default, Export, Import, Not accepted, Default. Default is the absence of a row
  in the set being edited (no new mode string in `SMROptIn_station_rows` or `SMROptIn_distribution`);
  a saved Balanced row, made by the slider from Default, shows as Balanced and clicks on to Export.
  Not accepted keeps the saved row, as before; the next click clears it. On a hub network Default
  is the hub's own untouched default (Balanced at the dial) and the help says so.
- **Icons:** Default keeps vanilla's own `resource_storing.tga`; a set Balanced row takes
  `resource_accept.tga` (the storage depot's accept icon); Export, Import, Not accepted unchanged.
- **Defaults:** Export 0 everywhere; Import 100 on a hub network and on a hubless station of one
  cargo line, 50 on a hubless station `D.IsJunction` reports as joining lines. Ctrl+click copies the
  clicked row's state and number, Default included (each station's own set is cleared).
- **The depot's unset target** is Import 100 / Export 0 by the surface word (Not accepted 0, slider
  disabled), on every depot; the `Pair()` witness prints `(default)` where it printed `(dial)`.
- **Help:** Import and Export name the number as a share of this station's own store; Import says a
  Default source shares as the base game would and Export there sends everything; a hubless joining
  station gets the pass-through line and, at a full Import or Balanced number, the "nothing can pass"
  sentence; the depot's Export help names the slider as what the depot keeps.
- **Tests:** `hubless_relay_smoke.py` is `proposal_check.py` run against the shipping `Code/`;
  `distribution_ui_smoke.py` gained the five-state cycle, the defaults, the scoped clear, the
  joining-station default and lines; `wiring_smoke.py`'s unset target reads 100. Harness note kept
  in the UI smoke: the fixture's colony label is the first line's member list, so a station added to
  the label already sits on that route.

### 15.2 Outside the scope, reported and not edited

- The Mod Options help line for Station rows (`items.lua`, `Code/Opt_StationRows.lua`'s title) still
  reads "Import, Export, Balanced or Not accepted"; Balanced is now reached by the slider, Default by
  a click. Its wording, and the store copy's, belong to `release_prompt.md`.
- §8 stands: Brad's tunnels and Xeryx's carry dial are untouched.
- The hub's own allocation tree and §11's junction concerns inside a hub network are unchanged.

### 15.3 Claim limits and the audit

Supported: built and desk-verified against the archived native bodies at `83149ea`; audit pending.
Not supported: tested in game; fixes any named player's save; any figure about throughput, drones,
the panel or save and load. The owner runs the audit on a model of their choice (OI-53); it judges
the port against §14 and the three player cases. **Executed model:** Claude Fable 5.1
(`claude-fable-5-1`), no subagents; skills smr-orientation, doc-editing, smr-bug-library,
smr-session-close.
