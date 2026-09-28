# Train distribution 5d — chained-line routing, 2026-09-27

## Forwarding rule

Each connected train line is one hop. A runtime breadth-first tree rooted at the
distribution hub chooses the nearest upstream station; equal-length choices use
station handle order. The next hop for 6243 is 2012, then the hub. A station with
a direct hub line uses that line for its upstream hop. A sideways line between two
stations already directly connected to the hub creates no new managed load. Old
stranded cargo hands off at its nearest hubward station, with handle order breaking
ties, for that station's upstream train to collect. Trains remain on their own lines.

A station's own row target has first claim on its stock. Its free physical storage
may temporarily hold **up to the remaining capacity** as transit stock. Excess
above its own target moves upstream after downstream shortfalls are allowed for;
downstream branch needs move toward it from the hub. Native train assignments and
station stock carry the transit across save/load. No transit tag is persisted.
"Wanted" means an enabled Import or Balanced row is below its configured amount,
less incoming reservations. An untouched row is Balanced at its live absolute dial.
Export never requests a delivery for its own floor; stock above that floor may
feed another branch or move to the hub. Balanced sends overage back and requests
shortfall. An intermediate Import can forward stock above its own pin; a leaf
Import never becomes a train source. A full hub refuses upstream excess unless
another station on the path has a shortfall. A station with no hub connection
keeps vanilla behavior.

The branch total is recalculated from live stock and native demand reservations
inside each train call. Transient enabled/capacity answers and claims express the
next hop to vanilla's unchanged `TransferCargo`/`LoadResourceForStation` path.
`UnloadAll` admits a child line's transit into the intermediate's actual free
storage, then its next train forwards stock while respecting that station's pin.
No route model, train body, drone path or shipping module changed. One hub owns
the tree; routing between different hubs is outside this build.

## Save ladder

| Part | Rung | Measurement closing the lower rung |
|---|---:|---|
| Per-call hop selection, train orders and transit unload | 0 | Archived-body cases move Export, Balanced, Import and untouched loads over the chain with only temporary answers/claims. Intermediate stock survives simulated save/load and forwards afterward. No custom saved field is needed. |
| Drone baselines | 1 | Existing distribution implementation: the 2026-09-25 live sitting measured drones responding to vanilla-written desired amounts; session-only samples did not leave that behavior. No new writer added here. |
| Player row settings | 2 | Existing `SMROptIn_distribution` on the hub; session-only settings could not retain player choices across load. This build adds no key or field. |
| UI tooltip and routing counters | 0 | Tooltip reads the runtime parent; counters and parent tree are rebuilt in memory. |
| Stranded-cargo admission and hub refusal | 0 | Native unload releases obsolete assignments; runtime refusal evidence permits overflow after a hub visit. Reload clears the evidence and the train attempts the hub again. Delivery watchdog receipt below. |

Overall distribution remains at rung 2. The existing rung-1 residual remains:
native drone desired amounts may linger after removal until vanilla rewrites them.
The hub's existing content-removal residual also remains. Native save serialization
and gameplay after a real load are not measured by the desk harness.

## Initial desk result and limits

The archived 1.1.1.405907 `Units/Train.lua` body ran with its 12 resource divisions
modeled as integer division (EF-116). The one-hop case holds the intermediate at
its own dial of 10 while sending a 60-unit leaf's Export/Balanced excess to the
hub; untouched 60 settles at 10; Import fills the leaf through the intermediate.
A full hub refuses the chain's export. The intermediate can retain an Import pin
of 24 while forwarding 30 to the leaf. In the dual-line case, 2009 uses its direct
hub line while its sideways line leaves both stations' pins intact. Disconnected
and disabled controls, all existing direct-line cases, the UI suite and the slot
suite pass. The chained tooltip names its upstream station and transit storage.

The explicit command/filter and HEAD receipt is
[`desk_suite_final.txt`](../../archive/train_routing_5d_20260927/desk_suite_final.txt):
`tools/devmods/train_hub/tests/*smoke.py` sorted, shipping/dev/TestKit
`parsecheck.py`, and `harvest_wrap_targets.py --check` reconcile to 16 commands:
15 pass, one known failure. `traffic_smoke.py` still reports `-10800 != 0` at its
arrival assertion. It is outside this routing change. The desk doubles do not
measure actual train timing, drone scheduling, native serialization or UI layout
in the game. The direct-line assertions passed at the desk; the first live sitting
below disproved equivalence in the game. No new persisted name, saved transit
marker or copied vanilla train body was needed.

## Initial sitting predictions

Written before the first sitting, which failed as recorded below. Orchestrator-attended from the owner's
`build6_capacity_covered_pass3` fixture, with both mods loaded and a fresh boot
for this Lua. Preloaded TestKit slot 4 reads all rows of a selected station; slot
5 watches a configured Metals row. If a station lacks a slot fit, a console read
is acceptable under the owner's 2026-09-27 ruling. Preserve the full closed log
and use the actual handles and times it emits.

1. MARK; select 6243, 2012, 2009 and the small station; run slot 4 on each.
   Predict `SMRTK_ACTION action=slot_4 status=OK`. Chained untouched rows show
   `configured=false`, `mode=balanced`, and `target` equal to that station's
   live dial. After train visits, chained untouched spokes settle at that dial;
   2012 keeps its own number while transit passes through. The row tooltip on
   6243 names 2012 as its hop.
2. Configure one chained Metals row Export and one Import at visible, reachable
   percentages; MARK and read with slot 4. Use slot 5 for each configured row
   if its setup gate accepts the selected station. Predict the Export falls to
   its floor, Import rises to its target through 2012, and 2012 returns to its
   own number after forwarding. Read the hub's room before Export: a full hub
   should refuse it. Record the actual target, stock, calls and train cargo
   rather than inferring arrival from the row display alone.
3. Run at top speed for at least one sol, close the log, and count the exact
   `LUA ERROR` token in that closed log. Predict zero. Stop on an unexpected
   error or taint, preserve the log, and report the first contrary witness.

These are predictions for the named single-hub colony, not a claim about every
network shape or a completed live result.

## First sitting failure and departure repair

**RELAY, owner/orchestrator, 2026-09-27 19:13, `6e187dd`: FAIL.** Fresh boot of
`build6_capacity_covered_pass3`, both mods. The report of no stock movement,
retained old cargo and repeated Idle/Loading transitions is recorded in spec
§4.8 at `cad784f`; the orchestrator owns the closed sitting log. The third relay
corrects the second: this is a repeated decision, not a single load wait.

**MEASURED, desk reproduction:** the old harness conflated Colony with City,
called `TransferCargo(nil, true)` (which forces a stop), and delivered trains to
destinations chosen by the test. It therefore never exercised the game's normal
departure decision after load. With distinct Colony/City objects, a loaded train
holding Butter 69 reproduces three evaluations with no valid departure and three
violations of vanilla's `has_work`/`next_stop` invariant:
[`repair_before.txt`](../../archive/train_routing_5d_20260927/repair_before.txt).

The production repair addresses two independently reproduced faults:

1. `D.Refresh` read the route map from `UIColony`. It now reads `hub.city`.
   Archived **1.1.1.405907** `Lua/City.lua:33` declares that field and
   `Lua/TrainTransport.lua:305-308` rebuilds it on each City. The original fixture
   supplied a route map on Colony that the production code could not use.
2. Fixing that lookup alone still fails the Butter departure watchdog:
   [`repair_city_only.txt`](../../archive/train_routing_5d_20260927/repair_city_only.txt).
   Vanilla counts retained cargo as work (`Lua/Units/Train.lua:1044`) but does not
   necessarily choose a stop when no new cargo loads. The distribution view also
   hides destination stock from vanilla's empty pickup decision. Before applying
   claims, the wrapper now checks real cargo and branch needs. Retained cargo,
   upstream pickup with stock available at the parent or hub, and downstream
   surplus collection use vanilla's existing should-move input. Its unchanged
   track walk selects the stop (`Train.lua:250-264,914-918`). Refabbing trains do
   not receive the additional departure input. All return values still come from
   the native body; no destination assignment or route model is replaced.

**MEASURED, repaired desk:** `distribution_departure_smoke.py` executes archived
`LoadTrain` and `ForEachStationAlongTrack`, with loaded cargo snapshots followed
by `OnMsg.LoadGame`. Its watchdog fails after three calls at the same station
without a valid native `GotoStation` command. Native movement is then doubled by
following only that command's destination. At train capacity 105, Butter 69
(including a partially unassigned load), Metals 98 and an empty pickup train
depart and deliver. With the chain initially empty and hub Metals 220, the native
commands fill the leaf and intermediate to 10 each and leave hub Metals 200;
old Butter 69 passes through the intermediate, leaving 10/10/49. Supply and demand
claims reconcile after delivery. Satisfied pins and a full-hub refusal remain
quiet instead of producing phantom trips. Existing direct-line amount cases,
dual-line behavior, UI and TestKit slots still pass.

The final receipt is
[`repair_suite_final.txt`](../../archive/train_routing_5d_20260927/repair_suite_final.txt).
Its explicit sorted `tests/*smoke.py` filter plus shipping/dev/TestKit parsechecks
and wrap check reconcile to **17 commands: 16 pass, one failure**. The failure
remains `traffic_smoke.py`, `-10800 != 0`. Command, HEAD and input hashes are in
the receipt. TestKit remains at `f3ab13c`; its current slots need no change.

The repair is **rung 0**; overall distribution remains rung 2 with its existing
residuals. No persisted name or additional saved state is introduced. Request
objects, physical movement and timing remain doubles; the harness models engine
nil-length behavior and observes retail assertions without using them as stops.
This tests loaded state and the load message, not the engine's save serializer.
The repaired build still needs the orchestrator's live sitting. Executed model:
GPT-6 as declared by this session; the exact variant is not exposed.

## Repair sitting predictions — not results

These were the predictions for `9a2d470`; the second sitting below disproved the
delivery claim while confirming the departure repair.

**<<PENDING-RUN>>** Fresh boot of `build6_capacity_covered_pass3`, both mods. Keep
the existing slot 4 reads and slot 5 configured-Metals watch.

1. Before running a whole sol, watch the trains that retained Butter and Metals.
   Predict actual departures after their load evaluation, followed by changing
   cargo or stock on arrival. A counter increasing while a train repeatedly
   returns to Idle at the same station with unchanged cargo is a failure; relay
   it immediately with the selected station, train, cargo and row read.
2. Read 6243 and 2012 with slot 4 before and after train visits. Predict
   `SMRTK_ACTION action=slot_4 status=OK`, increasing `calls` at 6243, Metals
   arriving through 2012, and untouched rows approaching their live dial.
   Recheck 2009 and its small station as the direct/sideways control. Covered
   stock can fluctuate with drones; transit may temporarily exceed 2012's pin.
3. Once departures and untouched stock movement are witnessed, run the original
   chained Export/Import targets and at least one sol at top speed. Predict the
   row targets are reached and the closed log has zero `LUA ERROR`. The
   orchestrator retains and archives the log and relays the result.

## Second sitting failure and stranded-cargo repair

**RELAY, owner/orchestrator, 2026-09-27 21:40, `9a2d470`: departures repaired,
delivery incomplete.** The sitting reached 6243 and filled the other untouched
rows, but Metals at 2012 and 6243 stayed empty while train 2000001844 retained
`cargo=98000`, `assigned_here=0`. Spec §4.8 retains the sitting measurements and
the owner's hub-first dump ruling; the orchestrator retains the closed log.
The live cargo's resource identity remains inferred. The desk fixture explicitly
uses Metals plus untouched Butter.

The previous departure watchdog accepted a train that circled with unchanged
cargo. Native **1.1.1.405907** `Lua/Units/Train.lua:787-830` unloads assigned cargo
only as a whole, releases its original destination's request even when landing
elsewhere, and limits unassigned cargo to available demand. A pin can therefore
make an old assignment unreachable. Sideways lines had no admission for old
cargo when neither endpoint was the other's parent.

**MEASURED before repair:**
[`dump_before.txt`](../../archive/train_routing_5d_20260927/dump_before.txt)
reproduces an off-line assignment remaining aboard after the delivery watchdog's
six `LoadTrain` calls, despite departures. Hub-room control passes on the old code;
full-hub overflow fails. The repaired admission still delegates every cargo and
assignment write to the archived native body:

- A train on a hub line first attempts a real hub unload. Remaining cargo records
  a runtime refusal for that train/resource/hub. If the hub still cannot take it,
  the return stop admits it up to physical room, including above the row's pin.
- Actual room is checked outside the allocation view. A nested native unload's
  transient demand claims cannot authorize overflow. Room becoming available at
  the hub sends cargo there; reload requires a fresh hub visit.
- On a line without the hub, the nearest hubward stop admits stranded cargo as
  transit. This extends the existing child-line transit rule to sideways lines;
  the upstream train carries the excess to the hub. A full hub refuses a new
  upstream load, leaving the overflow at that station under the owner's ruling.
- While a resource has an obsolete, unreachable or unassigned load aboard, the
  allocation view prevents another load of that resource. Native departure
  selection and the ordinary order calculation resume once it clears.

The extended `distribution_departure_smoke.py` counts native unload quantities
for each resource aboard at load, follows only native `GotoStation` commands,
and fails on retained cargo without departure or without delivery within six
calls. It checks the actual hub visit before direct-line overflow, both resources'
obsolete reservations releasing, and physical landing stock. Measured cases:

| Loaded state | Calls to clear watched cargo | Witness |
|---|---:|---|
| Off-line assignment or unassigned, hub room | 2 each | Metals 98 and Butter 7 land at hub |
| Off-line assignment or unassigned, full hub | 3 each | Hub attempted first; spoke Metals 10 → 108, Butter 10 → 17 |
| Assignment blocked by shrunken pin, hub already refused | 1 | Old Metals 98 lands above pin |
| Same, hub room opens before return unload | 2 | Hub receives cargo; spoke stays 10 |
| Same, reload after refusal | 3 | Fresh hub attempt before overflow |
| Sideways off-line assignment, hub room or full | 2 each | Gateway receives 98; with room its upstream train forwards all 98; when full gateway holds 108 |

Call counts exclude the setup hub visit in the shrunken-pin cases. This is a
bounded smoke for the named shapes with sufficient physical landing capacity,
not a bound for every network, disabled resource or full physical storage.
Requests, movement, waits and loading a serialized save remain doubled. No
persisted name, callback, thread, assigned-cargo writer or copied train body is
introduced. Repair rung 0; overall distribution remains rung 2.

The first full-suite attempt is preserved as
[`dump_suite.txt`](../../archive/train_routing_5d_20260927/dump_suite.txt).
It caught concurrent brief-11 registration work between metadata and items, as
well as the known `traffic_smoke.py` failure. The final receipt,
[`dump_suite_final.txt`](../../archive/train_routing_5d_20260927/dump_suite_final.txt),
reconciles its sorted `tests/*smoke.py` filter plus shipping/dev/TestKit parsechecks
and wrap check to **17 commands: 16 pass, one known failure**, `traffic_smoke.py`,
`-10800 != 0`. For `distribution_smoke.py` only, a temporary snapshot combines
HEAD's consistent items/metadata registration with byte-identical working Lua;
the receipt includes its full runnable command and hashes. The other commands
read the shared working tree. Brief 11's unfinished registration is excluded
from that registration assertion, and its files were not edited by this repair.
[`dump_gates.txt`](../../archive/train_routing_5d_20260927/dump_gates.txt) records
GREEN doccheck and a clean `git diff --check`.
Executed model: GPT-6 as declared by this session; exact variant unavailable.

## Stranded-cargo sitting predictions — not results

**<<PENDING-RUN>>** Fresh boot of `build6_capacity_covered_pass3`, both mods;
orchestrator attends and retains the log. Existing TestKit slots need no edit.

1. Watch train 2000001844's cargo and station stock through visits using slot 4.
   Predict the old load reaches the hub, or hands off at the hubward station on
   a line without the hub. Cargo must change as stock lands; repeated departures
   with the same load fail this repair.
2. With a full hub, predict an actual hub attempt on a direct line before the
   return station rises above its slider. Unassigned cargo and untouched Butter
   follow the same admission. If hub room opens, it takes precedence over overflow.
3. Predict Metals reaches 2012 and 6243 after the old load clears. The chained
   Export/Import legs and their sol at top speed remain owed, with zero `LUA ERROR`
   predicted; spec §4.8 ruling 7 puts brief 11's dispatch investigation before
   those remaining live legs. This fix's own smoke can run now.
