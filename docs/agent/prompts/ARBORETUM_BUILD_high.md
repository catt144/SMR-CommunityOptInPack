# Arboretum — investigate, then build a test module

One-off. Authored 2026-10-03 at `9330ca4`. Delete this file and its row in
`docs/agent/prompts/README.md` in the commit that closes the work.

## The owner's decision

Owner, 2026-10-03: build an **Arboretum** for this mod — *"a new service type building people
could use like an arboretum, that would give relaxation / comfort bonuses, something higher end
than some of the other types like parks, that would consume seeds"* — and *"proceed with the
Arboretum … a deep dive and a module build of that to test with."*

The problem it answers is the owner's: late-game colonies drown in Seeds, the few consumers stop
consuming, and players build ever-larger seed depots. The Arboretum is a permanent seed sink that
grows with population.

This is a new opt-in content module, off until the player turns it on, under `FIX_POLICY` §0.
The owner asked for a build **to test with**: rough and in the game fast, on placeholder vanilla
art. The owner tunes numbers and looks by eye afterwards. No new art is commissioned by this brief.

**Owner, 2026-10-03, later the same day: the Arboretum ships after launch, not in the launch
set** (`docs/agent/prompts/Launch_Prep/README.md`). Until launch is done, its `metadata.lua`,
`items.lua` and `RELEASE_OUTBOX.md` hunks stay uncommitted in the working tree: never commit,
restore or ship them. OI-47 and OI-48 wait until after launch.

Two design positions are **provisional, not ruled**. Build them as the starting values and put
each ask on `docs/PLAYTEST_CHECKLIST.md`:

- **Category:** its own service category, so its comfort stacks on top of Parks, rather than
  joining Parks and competing with Hanging Gardens.
- **Placement:** a normal garden-style footprint, one per dome, rather than a spire slot.

## End state

1. A module in this mod that registers like the others, with its Mod Options toggle off by
   default, and that offers one new in-dome building, the Arboretum, only while the toggle is on.
2. The Arboretum takes Seeds by drone delivery, gives its comfort while stocked and working, and
   stops giving it when empty, on vanilla mechanisms.
3. A module record filed through the `smr-bug-library` skill, carrying the owner's decision
   above, the provisional positions, every new persisted name, and what removal leaves in a save.
4. Desk verification that the mod loads with the module on and off, with the fix pack installed
   and absent (`FIX_POLICY` §8).
5. A short attended sitting prepared for the owner, and a report under `docs/agent/reports/`
   stating what was measured, what was only derived, and what is still owed.

Completion evidence: the commits, the gate output with its command and HEAD, the game log lines
from the load checks, and the sitting brief.

## Your judgment

Everything inside the decision is yours: the placeholder entity, the class parents, the numbers,
the file split, the investigation's read path and order, whether a question needs a subagent
(`subagents` skill). Record each call in the commit message that makes it. Do not bring the owner
a choice you can make; do bring them the two provisional positions and anything that changes what
a player sees beyond this brief.

Keep a live work list, one item per commit-and-verify unit, one in progress.

## Starting state

Run `git log --oneline -3` and `git pull` first. The tree is shared and a peer session had
uncommitted work in `docs/agent/prompts/README.md`, `tools/` and `docs/agent/reports/` when this
was authored; recheck shared paths before writing and commit by the `CLAUDE.md` header rule.

## Evidence in hand

All of it is a scout's claim, read from the archived tree for build **1.1.1.406343**
(`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.406343\Src`). Two points were spot-checked by the
author: per-visit consumption in `Service:Service`, and the empty-store refusal in
`Service:CanService`. Clear the rest with one check each, re-deriving every line number with
`grep -n` when you use it. If the game has moved to a newer build, read that build's tree.

- **Seeds can be a consumable.** `HasConsumption` is a parent of every `Building`
  (`Lua/HasConsumption.lua`, `Lua/Buildings/Building.lua`). `consumption_resource_type` accepts
  any physical resource; `consumption_type` 2 is per visit. Vanilla Seeds consumers are
  `ForestationPlant` and `OpenFarm`, both `dome_forbidden`.
  Falsify: `grep -n "consumption_resource_type" Data/BuildingTemplate/ForestationPlant.lua`.
- **No in-dome building consumes Seeds today.** Of 11 template files naming Seeds, 2 consume it
  and neither is in a dome. In-dome shops do receive non-food resources from drones:
  `ShopsElectronics` consumes 0.2 Electronics per visit, `ShopsJewelry` 0.2 Polymers.
  Falsify: `grep -rln Seeds Data/BuildingTemplate DLC/*/Presets/BuildingTemplate`.
- **Comfort comes from dome coverage, not from visits.** Each service category places its
  `service_capacity` against the dome population and applies a coverage-weighted stat
  (`Lua/Stats.lua`); categories add together. Only working services count. Visits still call
  `Consume_Visit` (`Lua/Buildings/Service.lua`), and a service with an empty store refuses
  visitors and stops working.
- **The classic names are gone.** `needRelaxation` and `service_comfort` have 0 hits in this
  build; interests are in `Lua/Interests.lua`, stats are the template's `Comfort` / `Sanity` /
  `Health` / `Morale` values.
- **Vanilla positioning.** Ordinary parks share the `GardenStone` category at Comfort 10,
  Sanity 10, capacity 5 to 40. `HangingGardens` (spire) is Comfort 30, Sanity 10, capacity 60,
  20 visitors. Stat file units are inferred as 10000 = 10; `const.Scale.Stat` is engine-set.
- **A validation rule.** A service without shifts needs `max_visitors * 3 <= service_capacity`
  (`Lua/ServiceBase.lua`).
- **Seeds availability gates.** Seeds starts hidden and is unlocked by a tech;
  `IsSeedsResourceAvailable()` (`Lua/Terraforming.lua`) answers it, and the `NoTerraforming` game
  rule removes Seeds.
- **Useful vanilla art and effects.** `Tree_01..05`, `Bush_*`, `Flowers_*` attach and sway;
  particle presets include `HangingGardens_FallingLeaves` and `GardenFountains_01..07`. Entities
  `GardenBig` and `GardenSmall` have no Lua references outside `_EntityData`; that is not proof
  they are unused or usable.
- **This repo's precedent.** `Code/Opt_TrainHub.lua` and `Code/Opt_ElevatorDepot.lua` show the
  module wiring, the module-off build lock through `GetAdditionalBuildingLocks`, a
  `ModItemBuildingTemplate` with its generated class, and reuse of vanilla art through a
  shapeshifter attach. `Code/Opt_ServiceInterestTags.lua` already touches the service system.
  Player strings take new ids; a reused shipped id loses its text on retail (EF-039).
- **A starting proposal, not a spec:** Comfort 15, Sanity 10 in its own category; capacity 40,
  12 visitors, 4-hour visits; 0.5 Seeds per visit, 10 stored; power, water and Polymer upkeep a
  step above a large garden.

Further records: `docs/agent/bugs/INDEX.md`, `docs/agent/facts/INDEX.md`.

## What the investigation must answer

These are questions, not a read order.

- How many Seeds a stocked Arboretum uses per sol in a populated dome. Nothing has measured
  visit frequency; a sink that eats a handful of seeds does not solve the owner's problem, and
  the per-visit amount is the dial.
- Whether drones, and shuttles, deliver Seeds to a consumption request inside a dome without
  help.
- Which vanilla entity serves as the placeholder, what footprint it brings, and whether it
  places in every dome type.
- What the player sees when Seeds is unavailable (tech not researched, `NoTerraforming`), and
  whether the building should be offered at all then.
- Whether its own category shows correctly in the dome's service readouts, and how it interacts
  with `ServiceInterestTags`.
- What the module writes into a save, and what a save holds after the module is turned off and
  after the mod is removed.

## Scope

In scope: the Arboretum module, its record, its checks, its sitting brief and its report.

Out of scope: the map-wide seed wonder (parked as `docs/FUTURE_IDEAS.md` §12), new imported art,
any change to a vanilla building's or another module's behaviour, the fix pack, and publication.
Report findings outside this scope; do not act on them.

## Stops

Report instead of continuing when:

1. no vanilla entity can stand in as an in-dome placeholder, so the build would need new art;
2. Seeds cannot reach an in-dome building without crossing one of the two bans or changing
   vanilla logistics for other buildings — offer the option with its risk and wait (§0);
3. the comfort effect cannot be had without changing how an existing service category or another
   module behaves.

## Claim limits

- Not "it works in game" from a desk check. Say "loads clean with the module on and off, per the
  log" until a loaded-game run shows the building built, stocked and serving.
- Not a seeds-per-sol figure from source alone. Mark it `<<PENDING-RUN>>` until measured, and
  give the command or slot that measured it.
- Not "removes cleanly". Say what the save holds after removal.

## Tests and the sitting

Apply `docs/agent/WORKFLOW.md`'s test-design and execution requirements. Preload the sitting into
SMRTK slots (`tools/SMRTK.md`); the owner clicks and does not type. The console needs a loaded
game. Scope the sitting to what the build exists to show: the Arboretum can be built in a dome,
drones stock it with Seeds, dome comfort rises while it is stocked and falls when it is empty,
and the seed use over a run of sols. Readings come from the building's infopanel and the dome's,
not from hunting among colonists. Live runs of this mod's modules are listed on the fix pack's
`docs/PLAYTEST_CHECKLIST.md`; `docs/README.md` says which list takes what.

## Player text

Vanilla build-menu tone: one or two sentences, `<em>` on keywords, no numbers in tooltips.

## Unattended runs

If this runs unattended, execution and audit are on different owner-selected models, and nothing
enters the record unaudited.

## References

Skills: `smr-orientation`, `smr-bug-library`, `doc-editing`, `subagents`, `smr-session-close`.
House rules `CLAUDE.md`; process `docs/agent/WORKFLOW.md`; code `docs/agent/FIX_POLICY.md`, its
header first.
