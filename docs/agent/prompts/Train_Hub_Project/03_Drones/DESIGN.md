# Train hub drones (build 4) — THE DESIGN, not a brief

⛔ **This file is the chain's settled design and reference. Do not fire it and do not edit its
owner rulings.** The work is the numbered links beside it (`README.md` is the manifest). Every link
reads this file for what the owner decided; a link that finds a ruling here overtaken by a later
one records that in its own notes and in spec §10, and leaves this text alone.

**What later rulings have overtaken here** — read this file with these in hand:

1. **The pad is gone** (owner, 2026-09-22): the recharge-pad model inside the ring is REMOVED
   (`51b89a5`) and the **drone pit** in the floor plate is the drones' place (`Pitfloor`, `Pitrim`
   spots; OI-25 settles the column). Where this file says "pad", read the pit.
2. **Not a constant 30 in the air** (owner, 2026-09-23): the fleet **scales with load** — a couple
   out when work is light, more as it rises, recalled as it falls. Thirty is the ceiling, not the
   standing count. The tiers and the step size are link 4's to choose; `4_HUB_high.md` carries it.
3. **Flight is a hybrid** (owner, 2026-09-23): our code owns the launch, the return and the
   commands; the **engine paths between them** (`SetHubDroneMode`, built in `9a540dd`). The scripted
   flight is kept restorable at tag `drones-scripted-flight-20260923`. Consequence for section 3's
   ride: a Wasp's `hover_height` is **class-static** (`Flight.lua:175`), so an engine leg rides at
   7 m and cannot be dialled per drone — **`OI-26` asks the owner whether that clears the
   side-hanging trains**, and until it is answered, "above any train that may be coming" holds only
   for the scripted ends.
4. **A malfunctioned or unpowered hub still repairs**, and **a destroyed hub despawns its drones**
   (owner, 2026-09-22): both are recorded in `4_HUB_high.md`, which builds them. Section 1's "if the
   hub is working" means the player's switch, never `IsWorking`.

⚠️ **Version.** Every citation in this file was read on **1.1.0.403908**. The game patched to
**1.1.1.405907** (installed build 25390750) mid-chain, and `doccheck --emit-fingerprint` reports
every fact group MOVED. Re-read any line number on the installed tree before building on it; the
sweep is queued at `prompts/perma/gamepatch/`.

## Authority

- **Owner, 2026-09-19.** Trains should be long-range transport that does not need drone coverage
  across the whole map, but a disaster breaks track wherever it lands and outside drone range it
  stays broken. The hub **auto-dispatches its repair drones** to breaks on its network. The
  owner chose the **cheap version**: the hub pays the repair from its own stock and completes the
  site after a travel time on a persisted deadline.
- **Owner, same day: the hub's repair drones.**
  They are **vanilla Wasp drones** (`FlyingDrone`, entity `DroneJapanFlying`, `FlyingDrone.lua:11-21`)
  whose controller is the train hub, made ours by per-drone data: display name "Repair Drone", our
  recolour, a large `battery_max` topped up by the hub so they **never charge** (`Drone.lua:10`).
  Near the hub, vanilla's AI seeks a charger only at about twice the emergency level
  (`Drone.lua:629`, `:697`), so the top-up keeps them well clear of it. The top-up runs whatever the
  hub's state, including malfunction and no power, because its drones exist to repair it.
  No subclass: a repair drone is identified live as a Wasp whose `command_center` is a train hub,
  so nothing sweeps other Wasps (Japan sponsor colonies), saves hold only vanilla Wasps, and on
  removal they are ordinary Wasps.
  - **A constant 30, launched on demand** (owner): the hub launches them when it has work and
    removes them when they return idle. **They launch from and return to a pad, never from
    nothing** (owner, 2026-09-19): the vanilla recharge pad model (`RechargeStationPlatform` /
    `RechargeStation` entity) inside the ring, where build 3 leaves it, recoloured to our look
    (vanilla colours pads with `Building.SetPalette`, `AttachedRechargeStations.lua:24-26`). A drone
    appears on the pad and lifts off; a returning drone flies back, lands and is removed. The pad
    is a plain model, not a working charger; it may play its working effect on launch. A destroyed repair drone is simply gone; the hub can always put up
    to 30 out, so losses never shrink it. No prefabs, no prefab controls, no charger.
  - **Inside a fixed 15-hex radius** (owner; build 3 cuts the slider) they do **anything a drone
    does**, through vanilla's own drone AI.
  - **Beyond it, track work only:** the same drone follows the track's element positions, hovering
    over the track, never drone pathing, so it cannot cut across open ground; it plays the vanilla
    repair work at the break (the Wasp's work animation state and the effects actions of the
    `DroneWork` path, `Drone.lua:983-1021`; find the exact names). **It charges from the track**
    (owner, 2026-09-19, for very long lines): in track mode the hub holds its battery at full the
    whole time, since tracks carry power; our track command never calls `Drone:UseBattery`
    (`Drone.lua:1760`), so this is a guard, not the mechanism. **Owner, 2026-09-19: "track work"
    is any maintenance, repair, upkeep or cleaning** of anything on the track, or joined to
    it by a track connector, like the stations, on the network connected to the hub (the same graph
    as Reachability, End state 1); never anything on an isolated network. Report which of those
    the drones do out there (malfunction repair, maintenance supply, dust cleaning, and whatever
    else you find), and any kind they cannot do in track mode.
  - **Save guard for track mode:** our follow-the-track command would be saved mid-step, so at
    `SaveGameStart` every drone in track mode is removed, and after the save and on load the hub
    respawns it where its persisted deadline puts it (`FIX_POLICY` §3a layer 1; re-arm from the
    deadline, never restart it). Idle drones near the hub are also recalled at save; busy ones stay
    in the save as vanilla Wasps, so a carried cube is never lost.
  - **No free-drone leak:** wrap `Drone:CanBeControlled` (`Drone.lua:2171`, chained per
    `FIX_POLICY` §1) to return false for drones whose controller is a train hub, which greys out
    both reassign buttons (`Drone.lua:1988-1991`, `:2016-2019`). Backstop: a repair drone whose
    controller is ever not a train hub, or whose hub is gone, is removed. Drones have no
    pack-into-prefab action of their own.
  - **Never a train:** not in any train list or count, no passengers, no UI text says train.
  - The panel shows one line, "Repair drones: N out / 30" (wording yours).
- `FIX_POLICY` §0 sets this mod's risk standard (owner, 2026-09-19): content may stay in a save
  on removal, and disabling stops new dispatches.
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
  this; the repair drone flies above the track and is never a train.
- **Completion is vanilla's own path:** `ConstructionSite:Complete()` (`ConstructionSite.lua:1675`),
  not the cheat branch. The hub is a Station and stores every resource, so it can pay the site's
  cost from stock.
- The network is a graph: stations and the tracks between them (`ForEachConnectedTrack`,
  `Station.lua`; `GetStartStation`/`GetEndStation`, `Track.lua:104`).

## End state

1. **Dispatch.** On `TrackBroken` for a track on the hub's network, if the hub is working and
   holds the site's cost, reserve it **at the cheaper rate, the SafeTransport-halved cost, whether
   or not that tech is researched** (owner, 2026-09-19: the hub is a perk, not a penalty; a
   repair through the hub never costs more than a drone repair would), record a pending repair with its **deadline in game time**
   (distance along the track from the hub at the repair speed), and notify:
   "Repair drone dispatched, ETA N h" (wording yours; never "train"). If stock is short, sign the hub and retry when stock lands.
   **Reachability (owner, 2026-09-19):** anything a repair drone following the track could reach:
   every track on the network connected to the hub through its stations, however far; never a
   track on an isolated network the hub does not touch. **Speed (owner, same day):** faster than a
   normal train, an emergency vehicle, because the network can be big. **The principle (owner):
   the repair must not replace one pain point with another through speed.** The ETA is a
   nuisance the player notices, never a wait they plan around: pick the multiplier so that the
   farthest break on a large network repairs within a fraction of a sol, and treat the dial as a
   floor on responsiveness, not a balance knob. Report it with the smoke's measured ETAs. The route to a break may itself cross an
   earlier break; your call whether the drones queue repairs nearest-first or in break order,
   recorded in the report.
   **Design the pending list for two kinds, repair and build** (owner, 2026-09-19): build 5,
   `04_TRAIN_HUB_BUILDTRACK_high.md`, will have the hub construct new track through the same
   completion path, sequentially from the connected end. Give the list a kind field now so build 5
   adds no second persisted name; ship only the repair kind here.
2. **Completion.** At the deadline, `Complete()` the site through vanilla's path. The timer is the
   only authority: it is persisted; the drone's position is rebuilt from it.
   **Drones are never limited** (owner, 2026-09-19): a break in any drone's range is repaired by
   drones exactly as today, the hub works the same site alongside them, and whichever finishes
   first wins. So the hub charges a site's **outstanding** cost at the moment it completes it,
   never the full cost, and drops a pending repair silently when drones complete the site first.
   Deduct at completion, not at dispatch, so nothing is paid twice.
3. **Track mode.** The repair drone moves along the track's element positions to the break and
   back; a save or reload can move it but never lose or double a repair (the save guard above). **Tunnels (observed by the owner, 2026-09-19):** a vanilla train vanishes when
   its nose reaches the black backdrop just inside a tunnel mouth; the portal arch has ample
   clearance above the rail. Do the same: drive into the backdrop, hide, advance on the timer,
   show at the far mouth. Tunnels are in scope. **Ride position (owner, 2026-09-19): hovering
   over the track**, clear of the side-hanging trains; keep the height one value, and check
   clearance at stations, the hub's hoods and tunnel arches. Recolour: ours (above). Drop the recolour first, never the
   repair or the save guard.
4. **Player controls.** A toggle on the hub's infopanel for track repair; a stock reserve the repair may not dip
   below is your call.
5. **Smoke with the owner:** break a far element with the TestKit (`Track.lua:618`
   `CanGetDamagedBy`; a meteor at click), watch the dispatch, save and reload mid-trip, watch the
   completion and trains run again; a break with the hub short of stock; hub toggle off; a
   repair drone near the hub doing ordinary drone work, never charging; the reassign buttons
   greyed on a repair drone; more than 30 jobs queued with 30 out; one destroyed and the hub
   still able to put 30 out; an autosave mid-trip.
6. **Train construction needs a drone (owner, 2026-09-19).** The owner found that a station cannot
   build a train without drones, although the build itself is internal: `Station:UpdateTrainConstruction`
   (`Station.lua:541`) only advances a counter, the drones seen are the `ConstructingDrones` effect
   (`:526`), and the Metals and Machine Parts arrive through demand requests
   (`:462-470`, `SelfService` `:503`). **Test it on the hub with no repair drone out:** stock it with
   Metals and Machine Parts, queue a train, and report whether it builds and, if not, what the
   hub is waiting for (read the request that stays open). **Owner ruling: if a drone is the missing
   piece, the hub may dispatch a repair drone just to acknowledge the call.** The drone need not
   move or work, since the build is internal; a launch from the pad and a return is enough. Count
   train construction as work for the on-demand launch, so the hub is never left with no drone to
   answer it. Report whether stations elsewhere on the network are held up by the same thing;
   build the acknowledgement for them only if it is the same mechanism and costs a line or two.
7. **Record** in the hub report and spec §10; persisted names in the inventory.

**Done means:** a break outside every drone's range on the hub's network is repaired from the hub's
stock without player action, survives a reload mid-trip, and the toggle stops it.

## Scope

**Test save (owner, 2026-09-20):** sittings load `train_hub_base`, which has the stations, tracks and lines prebuilt; only the hub is built each round. Spec §10, "The standing test save". Do not build trains or lines each sitting. Unattended legs load `train_hub_base_agent` (hub prebuilt, full and switched off; spec §10).

**Cold start (owner, 2026-09-20):** the hub must start in a remote, droneless area with no grid and only what a person brought. This works and has for a long time (owner, 2026-09-21): it is not a job for this build. Keep it working; the requirement is spec §10, "Owner requirement, 2026-09-20".

In: the dev mod, TestKit slots (`tools/SMRTK.md`), the sitting, the records.
Out: vanilla drone AI changes beyond the scoped wrap above, real train pathing, Module A, routing.

## Stops

- **Completing the site through `Complete()` needs the site's own drone-work state** to be faked
  in a way that touches vanilla tables: report the exact fields and stop.
- **The pending list cannot be persisted without a new class or a save-format risk:** report.

## Do not claim

"Repairs work" from one break. The claim is the smoke's breaks, distances and reload, in that
colony.

## Lifecycle

Done when its smoke is recorded. Lifecycle: the orchestrator decides, once this is fired and done: park it in `Parked/` if it is kept for touch-up work, or delete it; either way its row in `README.md` follows (owner, 2026-09-21).
