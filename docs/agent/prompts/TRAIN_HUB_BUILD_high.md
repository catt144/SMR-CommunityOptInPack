# Train hub build: the real six-connector hub, with its own drones and a maintenance reserve

## Authority

- **Owner, 2026-09-18:** the hub prototype is a **qualified GO**. Build the real Module B hub. The
  rulings, in the owner's words, are in spec §10
  (`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`) under "Owner rulings, 2026-09-18,
  for the real hub build":
  - Six connectors, with a four-connector variant later.
  - A built-in, small-radius drone controller whose drones serve anything in range.
  - A Metals maintenance reserve that trains and drones do not take.
  - Vanilla storage.
- MODULE FREEZE is lifted (`CLAUDE.md`). Both bans in `FIX_POLICY.md` bind, as do spec §8's
  constraints.
- **The owner is making the asset.** Their reference pack and its layout requirements are at
  `C:\Dev\SMR-TrainHubAssets\reference\README.md`. Until the asset lands, use the prototype body
  (`TrainStationLargeCCP3` with computed connectors) as a stand-in. Leave the swap to the asset
  as one clean change.

## Start

Run `git log --oneline -5` and `git pull`. This brief landed at the commit that
`git log -1 --format=%h -- docs/agent/prompts/TRAIN_HUB_BUILD_high.md` names. If
`git diff --stat <that sha>..HEAD -- tools/prototypes/train_hub docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md docs/agent/reports/TRAIN_HUB_PROTOTYPE_20260918.md`
is empty, the facts below hold. Before any write, put the end state in the todo tool, one item per
commit-and-verify unit.

## Where things stand

- **The prototype** is `tools/prototypes/train_hub/`, a separate dev mod, as of `625053c`.
  Everything it proved and the five checks it carried forward are in
  `docs/agent/reports/TRAIN_HUB_PROTOTYPE_20260918.md` §"Sitting 2 teardown and reload, and the
  verdict". Read that section first; it is the evidence base.
- **Its placement fix and its two extra construction-path readers are proven** over open
  ground (R2-a). Reuse them rather than re-deriving them.
- **Sitting 2 taught three rig lessons.** Build these into the TestKit so the owner does not
  pay for them again:
  - Clearing stations one at a time while the game runs does not work, because trains refill
    them. Clear every station on the network in one action.
  - An autosave or manual save disarms a running witness (`DISARM reason=SaveGameStart`).
  - Slot 1 did not list the hub.

## End state

1. **Structure.** A shared base holds the connector count and the line geometry, with a thin
   class per size. Build and ship the six first. **Name the four now** in the report without
   building it, because a name that reaches a kept save is permanent (ban 1). Your call is where
   the code lives during the build: stay a dev mod, or go into `Code/` off by default. See
   Stops for where it ships.
2. **Built-in drone controller (spike first).** Can a `Station` also be a drone controller?
   Vanilla precedent is `RocketBase`, which combines storage with `DroneControl`
   (`RocketBase.lua:2`), and `RCRover` (`RCRover.lua:6`). If the spike holds, build it: a small
   work radius (the hub plus about two hexes, your call), its own starting drones and a
   charging point. Its drones serve anything in the radius, with no hub-only filter.
3. **Maintenance reserve.** The hub keeps back a Metals reserve for its own maintenance, at
   least one maintenance's worth; the amount is your call. Trains must not export below it, and
   its own drones must not haul below it. For trains, this is the export floor spec §4 marks as
   the one missing mechanism (`Train:TransferCargo`). Build it so Module A can generalise it
   to per-resource floors later.
4. **The prototype's five carried checks, plus one new one:**
   - A **direct cargo-crossing witness**: a unit unloaded at the hub by one route and loaded
     by another, read from the train side. It must hold even though the hub now has drones.
   - A save and reload with a **working** hub.
   - Why Metals read `enabled=false` at the hub.
   - Placement across existing track.
   - Slot 1 listing the hub.
   - **New:** Waste Rock rides a train out of the hub. This is INFERRED from source only
     (spec §10).
5. **A sitting with the owner** through SMRTK. Give about five steps at a time, and write the
   predictions before boot. The owner's test colony `Japan Sol 490` is available, and its drones
   are always on: do not ask the owner to turn them off (colonists starved on 2026-09-18). A
   fresh colony is fine too.
6. **Record** the results in the report and spec §10, and ask the owner for anything that is
   theirs on `docs/PLAYTEST_CHECKLIST.md`.

**Done means:** in one colony, the six hub places, attaches all six lines and carries three
routes. Cargo is **seen** crossing between routes from the train side. The hub's own drones
maintain it from its reserve, and trains leave the reserve alone. It demolishes and reloads
cleanly while working. If time runs out, drop the Waste Rock check first, then the four's
naming note. Never drop the crossing witness, the reserve, or teardown and reload.

## Facts you would otherwise re-derive

All were read on 1.1.0.403908 (`C:\Dev\SMR-SrcArchive\1.1.0.403908\Src`) or measured
2026-09-18.

- **A large station's maintenance is 5 Metals and its power draw is 10**
  (`StationBig.generated.lua:29-30,49`).
- **A drone hub turned off stops giving drones new work** (`DroneHub.lua:150-168`). A hub
  with no power keeps commanding drones but cannot recharge them.
- **The train reads `available = Min(target, actual)` and holds back no floor.** That is spec
  §4's "MISSING" row.
- **A connector must sit inside the footprint** (`Tracks.lua:19-24`). The prototype's
  footprint-edge radii on the stand-in body were `5 6 5 4 4 4`.
- **Stations must be at least 10 hexes apart** (`Construction.lua:2924-2927`).

## Scope

In: the hub classes, the drone controller, the reserve, TestKit slots in
`80_AgentSlots.lua` (standing permission, `tools/SMRTK.md`), the sitting, and the records.
Out: routing (5c/5d), Module A beyond the reserve's reusable core, the art itself, and
shipping modules D02, D03, D04 and D09.

## Stops

- **The hub ships in this mod** (owner, 2026-09-18, OI-16 = 4b; spec §6 OPTION 4). The
  building stays out of the build menu while the module is off. If the release packaging or
  checks refuse an entity folder, stop and report the tool and the rule.
- **What happens to built hubs when a player turns the module off** is a save-safety design
  question. Propose an answer in the report. If no answer keeps saves loadable, stop and ask.
- **The drone-controller spike fails:** report it, ship the hub without drones, and ask the
  owner how to keep it maintained.

## Do not claim

- "Routing works." The true claim is that N routes exchange cargo through one hub in the tested
  colony.
- "The reserve works" from station stock alone. The hub's drones and trains both move Metals,
  so show that neither took the reserve.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` once the hub's sitting
is recorded.
