# Drones chain, link 1 — the survey: every name and limit the build would otherwise guess

**Link 1 of the `03_Drones` chain** (`README.md`). Read `DESIGN.md` first: it is the owner's settled
design and you do not re-open it. **Read-only on the game source; you write facts, not game code.**
Start with `git log`, `git pull` in `B:\Dev\SMR\SMR-OptInPack` and `B:\Dev\SMR\SMR-Assets`.

⚠️ **The structure pass is running in parallel and owns `tools/devmods/train_hub/` and
`B:\Dev\SMR\SMR-Assets\trainhub\`.** Do not write in either. Your outputs are `docs/agent/facts/`,
your notes into links 2 and 4, and spec §10.

## Authority

The owner, 2026-09-22: build 4 is split so the discovery runs while the hub's look finishes.
`DESIGN.md` carries every design ruling and is not yours to change. Where it says the drones launch
from the vanilla recharge-pad model, that pad is gone: the **drone pit** in the floor plate is the
drones' place (`51b89a5`; spec §9 "the pit"), and the entity carries `Pitfloor` and `Pitrim` spots.

## End state — a fact per question, each with the line that could falsify it

Fan-out is yours to organise: several independent read lenses, then a synthesis you write. Give an
investigating subagent a deep-reasoning model; a scripted read can take a lighter one. Commit each
subagent's verbatim report under `docs/agent/reports/drones_chain/agents/`.

1. **Work kinds out on track.** Which vanilla drone work a drone can actually perform on a track
   element and on things joined to it (malfunction repair, maintenance supply, dust cleaning, and
   whatever else exists), and which it cannot without a command centre in range. `DESIGN.md` §3 and
   the owner's 2026-09-19 ruling define "track work".
2. **The animation and effect names** of the `DroneWork` path (`Drone.lua:983-1021`), exactly as the
   1.1.0 source spells them, so link 2 can play the work state without guessing.
3. **The battery, palette and control surfaces:** `battery_max` and the charge-seek thresholds
   (`Drone.lua:10`, `:629`, `:697`), how vanilla recolours a drone or pad (`Building.SetPalette`,
   `AttachedRechargeStations.lua:24-26`), and `Drone:CanBeControlled` (`Drone.lua:2171`) with the
   two reassign buttons it greys (`:1988-1991`, `:2016-2019`).
4. **The network graph** the hub's reachability rests on: `ForEachConnectedTrack`,
   `GetStartStation` / `GetEndStation` (`Track.lua:104`), and how an isolated network reads.
5. **The pit, measured, not assumed:** where `Pitfloor` and `Pitrim` sit, their world positions and
   headroom, what a drone spawned there would clear on the way out, and whether the deck roofs it
   (spec §9 records about 74% coverage per wedge). Recommend a launch and return point, with the
   numbers, and route the owner's ruling (chain README, "Open owner decision").
6. **Save and load hooks** the save guard in `DESIGN.md` needs: `SaveGameStart`, what a mid-command
   drone persists, and `FIX_POLICY` §3a layer 1's re-arm shape.

File each as an engine fact through `smr-bug-library` where it is a durable engine truth; keep the
rest in your report. **Then write the notes:** what link 2 needs (names, thresholds, pit numbers,
clearances) into `2_FLIGHT_medium.md` §"Notes from upstream", and what link 4 needs (graph,
reachability, save hooks, control surface) into `4_HUB_high.md` §"Notes from upstream".

## Live work list

One todo item per commit-and-verify unit, before any write. Mark each as it lands.

## Scope

In: reading the 1.1.0 source, the dev mod's entity and spots, our own records; writing facts,
reports and the two links' notes. Out: any file under `tools/devmods/train_hub/` or in SMR-Assets,
any game code, any design change.

## Stops

1. A work kind cannot be settled from source and needs a game probe: write the probe, route it to
   the owner as a checklist item, and carry on.
2. The pit cannot seat a launch point at all: stop and report, because link 2 rests on it.

## Do not claim

Do not claim a drone "can" do a work kind because a function exists. Claim what the call path shows
and name the condition you could not test. Tag every spec detail MEASURED / SOURCE / INFERRED.

## Notes from upstream

*(none — this is link 1)*

## Lifecycle

Append your notes into links 2 and 4, record in spec §10, then **delete this file and strike its
row in `README.md` in the same commit**.
