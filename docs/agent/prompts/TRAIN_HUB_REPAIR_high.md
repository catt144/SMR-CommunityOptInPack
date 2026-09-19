# Train hub build 4: the repair train

⛔ **HELD until build 3's smoke test is recorded** (`TRAIN_HUB_BUILD3_high.md`). It changes the hub's
economy, so it builds on build 3's power, cost and storage numbers, not build 2's.

## Authority

- **Owner, 2026-09-19.** Trains should be long-range transport that does not need drone coverage
  across the whole map, but a disaster breaks track wherever it lands and outside drone range it
  stays broken. The hub **auto-dispatches a repair train** to breaks on its network. The owner
  chose the **cheap version**: the hub pays the repair from its own stock and completes the site
  after a travel time; the train is a **cosmetic vehicle**, not a unit, with a **distinct repair
  livery** (a recolour) as a nice-to-have. Not a drone: drone range, batteries and material
  sourcing are not to be touched.
- Both bans in `FIX_POLICY.md` bind. **This build adds persisted state** (the pending-repair list):
  name it once, permanently, and add it to the persisted-name inventory in the same commit.
- Testing depth (owner): a smoke test only.

## Read first

`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §10 and `TRAIN_HUB_BUILD_20260918.md`
(builds 2 and 3). Facts from the 1.1.0.403908 source, each with the line that could falsify it:

- **A break is a construction site.** `TrackBase:BreakTrackElement` (`Track.lua:623-655`) hides the
  element and places a `TrackGridElement` construction site over it, costed like new track, the
  cost halved under the `SafeTransport` tech. Repair is drones completing that site. Trains cannot
  run while `#repair_cgs > 0` (`Track.lua:372-384`).
- **A train on a broken element is destroyed** and its passengers roll for death, 80% or 20%
  with SafeTransport (`TrainDisasterHandling.lua:1-28`). A real unit driving to the break fights
  this; the cosmetic vehicle never becomes a train.
- **Completion is vanilla's own path:** `ConstructionSite:Complete()` (`ConstructionSite.lua:1675`),
  not the cheat branch. The hub is a Station and stores every resource, so it can pay the site's
  cost from stock.
- The network is a graph: stations and the tracks between them (`ForEachConnectedTrack`,
  `Station.lua`; `GetStartStation`/`GetEndStation`, `Track.lua:104`).

## End state

1. **Dispatch.** On `TrackBroken` for a track on the hub's network, if the hub is working and
   holds the site's cost, deduct it **at the cheaper rate, the SafeTransport-halved cost, whether
   or not that tech is researched** (owner, 2026-09-19: the hub is a perk, not a penalty; a
   repair through the hub never costs more than a drone repair would), record a pending repair with its **deadline in game time**
   (distance along the track from the hub at the repair speed), and notify:
   "Repair train dispatched, ETA N h". If stock is short, sign the hub and retry when stock lands.
   **Reachability (owner, 2026-09-19):** anything the dispatch vehicle could physically reach:
   every track on the network connected to the hub through its stations, however far; never a
   track on an isolated network the hub does not touch. **Speed (owner, same day):** faster than a
   normal train, an emergency vehicle, because the network can be big. Pick the multiplier as a
   dial and report it with the smoke's measured ETAs. The route to a break may itself cross an
   earlier break; your call whether the vehicle queues repairs nearest-first or in break order,
   recorded in the report.
2. **Completion.** At the deadline, `Complete()` the site through vanilla's path. The timer is the
   only authority: it is persisted; the vehicle is not.
3. **The vehicle.** An unsaved prop moving along the track's element positions to the break and
   back, rebuilt from the deadline on load, so a reload can move the picture but never lose or
   double a repair. Livery: a distinct palette, colony colours with a red accent. Cargo cubes for
   the paid load if cheap. Drop the livery first, then the vehicle, never the repair.
4. **Player controls.** A toggle on the hub's infopanel; a stock reserve the repair may not dip
   below is your call.
5. **Smoke with the owner:** break a far element with the TestKit (`Track.lua:618`
   `CanGetDamagedBy`; a meteor at click), watch the dispatch, save and reload mid-trip, watch the
   completion and the train run again; a break with the hub short of stock; hub toggle off.
6. **Record** in the hub report and spec §10; persisted names in the inventory.

**Done means:** a break outside every drone's range on the hub's network is repaired from the hub's
stock without player action, survives a reload mid-trip, and the toggle stops it.

## Scope

In: the dev mod, TestKit slots (`tools/SMRTK.md`), the sitting, the records.
Out: drone logic, real train pathing, Module A, routing, tunnels (report if they break the walk).

## Stops

- **Completing the site through `Complete()` needs the site's own drone-work state** to be faked
  in a way that touches vanilla tables: report the exact fields and stop.
- **The pending list cannot be persisted without a new class or a save-format risk:** report.

## Do not claim

"Repairs work" from one break. The claim is the smoke's breaks, distances and reload, in that
colony.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` once its smoke is recorded.
