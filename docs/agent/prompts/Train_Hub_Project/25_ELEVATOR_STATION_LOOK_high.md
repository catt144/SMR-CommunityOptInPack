# Brief 25 — the Elevator Depot: a 75 % space elevator with a tunnel mouth (handoff) · _high

## Authority and outcome

**Owner rulings, 2026-09-29.** The earlier ones are in spec §11 of
`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`; the evening's words are in
`reports/ELEVATOR_STATION_LOOK_20260929.md` §6. Do not reopen them.

- **Kept from §11:**
  - trains never change maps; cargo does;
  - our own station class based on vanilla's;
  - vanilla's elevator is not altered;
  - each mod works with the other absent.
- **The look (evening):** vanilla's Space Elevator at **75 %** — *"lets try the 75% one"*.
- **The train mouth:** a smaller vanilla tunnel blended into the elevator. *"Traints can deliver
  into or out of it. Drones can as well. Depending on player setup."* *"The train just goes
  "inside" and comes out."*
- **What it is:** *"More of a depot. Trains still dont goto new maps it enters the elevator, and the
  cargo transfers from the elvator."*
- **The method** (owner, 2026-09-20): rough and fast; the owner dials it in by eye; no gate between
  the owner and something to look at. Design comes before wiring (§11's order).

**The owner's calls, made when firing** (ask once, in one message at the start, if they are not
answered here):

| # | decision | options | answer |
|---|---|---|---|
| D1 | Surface cabin direction | up into the sky (vanilla) · down into the ground | _owner_ |
| D2 | Tunnel art | `TrainTunnelUniversal` (the owner's screenshot, with drone doors) · `TrainTunnel` | _owner_ |
| D3 | Stand-in in the owner's normal game is a working vanilla Station, so trains can drive in | yes · no (plain building, look only) | _owner_ |
| D4 | The dome model (first build of this brief) | retire it · keep it on hold | _owner_ |

**Done when** the owner places the **Elevator Depot** on both maps in their normal game and sees
three things:
- the 75 % elevator and the tunnel mouth on one base;
- the cabin running its rope with vanilla's sound: up into the cave ceiling underground, and D1's
  way on the surface;
- **a vanilla train driving into the mouth, stopping out of sight and coming back out** (with D3
  yes).

The owner then accepts the look or adjusts it by eye, and you iterate.

**Not this brief** (the next one, written after acceptance): the cabin carrying cargo between maps,
per-resource modes, the depot's own drone crew, the underground twin and its placement rule.

## Start

Authored on top of OptInPack `8408f9a`. Run `git log --oneline -3` and `git pull`, and keep a live todo
list, one item per commit-and-verify unit, one in progress. Game build must be **25390750**
(`python tools/doccheck.py --emit-fingerprint`). Check `tasklist /FI "IMAGENAME eq Mars.exe"`
before writing a dev mod's `Code/` while the owner plays, and tell them a restart is needed.

## What exists

- **Dev mod** `tools/devmods/elevator_station/` (`SMR_ElevatorStationDev_20260929`), junctioned
  into the game as `%APPDATA%\Surviving Mars Relaunched\Mods\SMR-ElevatorStationDev`. Its console
  helpers:
  - `SMRElevatorStationDev.Preview(scale, mode, rope_m)`: scaled vanilla SpaceElevator art, with its
    cabin cycling up or down and the `ElevatorMoving` FX;
  - `PreviewTunnel(scale, lift_m, angle_deg, entity)`: the scaled tunnel art;
  - `ClearPreview()`;
  - `Measure()`: camera, elevators and the ceiling objects near them;
  - `Report()`: each stand-in's connectors against vanilla's.

  The previews are visual only (`DeleteOnLoadGame`; no thread is saved).
  Its template `SMROptInElevatorStationDev` is a plain `Building` on the retired dome entity, which
  was never imported. Replace or retarget it; the dev mod is yours.
- **Asset pipeline** `B:\Dev\SMR\SMR-Assets\elevatorstation\blender\` (Blender 5.2, headless). It
  writes the FBXs and the dev mod's import items and materials. Reuse it for the depot's own base
  entity.
  - `station_build.py`: the generator;
  - `verify_station.py`: re-imports each FBX and checks spots, footprint and UVs against a table;
  - `station_render.py`: the renders;
  - `README.md`: **the owner's Mod Editor import, step by step**.

  The Art Spec cannot be pre-written: the editor rebuilds mesh specs only from an existing
  `.entjson` (`ArtSpecEditor.lua:565-603`). The owner creates each EntitySpec with Ctrl-Alt-A;
  everything else can be pre-written.
- **Record of the first build:** `reports/ELEVATOR_STATION_LOOK_20260929.md`. It holds the station
  spot table, the footprint method, the ceiling readings and §6's owner words.

## Evidence

Sources are from `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src` (build 25390750).
Entity data is `Packs/BinAssets.fpk:entities.dat` (sha256 `64b68206…`), decoded with
`SMR-Assets/_shared/geometry/entities_dat.py` and extracted as in `reports/CROSSING_SHAPE_20260929.md`
§9. Re-derive any line number with `grep -n` before you lean on it.

**The space elevator is reusable piece by piece.**
- `SpaceElevatorBase:GameInit` places a `SpaceElevatorCabin` at the building's position and
  `SpaceElevatorRope` tiles every 100 m (`SpaceElevator.lua:56-73`).
- `MovePod` slides the cabin with `SetPos(pos, tick)` (`:391-410`).
- The sound is `PlayFX("ElevatorMoving", "start"/"end", …)` on the building and the cabin (`:395-407`),
  with actors `SpaceElevator` and `SpaceElevatorCabin` (`:652-659`).
- Don't inherit `SpaceElevatorBase`: it is Earth trade, and `CargoTransporterNew` and its
  `NewHour` label loop are tied to `MainCity.labels.SpaceElevator`.
- A scaled vanilla visual keeps its auto-attaches (`ShapeshifterAutoAttach:ChangeEntity`,
  `AutoAttach.lua:2606-2619`). The hub runs a vanilla FusionReactor at 75 % that way
  (`20_TrainHub.lua`, `reactor_scale`).

**Footprints do not scale with art.** The building's hexes come from its own entity's `hex_shape`,
so a mini needs our own base entity drawn to cover the scaled visuals. The counts below are on
the game lattice (rows 866 / pitch 1000). Positive control: the large station gives 85 / 95, the
band `IMPORTER_FACTS` records (the game reads 95).

| art | centre rule | touch union | extent |
|---|---:|---:|---|
| `SpaceElevator` at 75 % | 19 | 40 | 64 × 59 m |
| `TrainTunnel(Universal)` at 100 % / 75 % | 49 / 25 | — | 110 × 43 m at 100 % |
| the two at 75 %, butted | about 35–44 | — | — |
| vanilla `TrainStationCCP3` | 24 | 41 | 82 × 47 m |

**What does not scale: track and trains.**
- Vanilla track runs **8.00 m** up. `TrackCCP3`'s `Enter1/2` are at z 800, and its beam spans
  8.53–10.69 m.
- A train rides 2.89 m beside the rail and is 4.16 m wide (`_shared/IMPORTER_FACTS.md`). Its
  length is **disputed**: the owner measured about two hexes; don't use 41.5 m.
- At 75 %, the tunnel's rail stub sits at 6 m, and its connector (`Trackconnector0` at
  (5000, 0, 0), `Trackdirection0` at (6000, 0, 0)) moves to 37.5 m from its centre, off the hex
  lattice. `PreviewTunnel` prints both. Lifting the art on a podium, keeping the mouth end at full
  size, or a scale the owner picks by eye are all yours to choose.

**A vanilla station already does "in and back out".**
- `Station` reads `Trackconnector1..4`, `Ramparrive`/`Stop`/`Spawn`/`Rampdepart`
  (`Station.lua:620, 1101-1103, 1162, 1188, 1202`).
- Routes are linear chains that end at stations, and trains turn back at a line end
  (`reports/CROSSING_SHAPE_20260929.md` S4/S5; the hub's settled terminating arm, spec).
- A lead, not a prescription: keep vanilla's two connectors, with `Trackconnector1` at the mouth and
  connector 2 buried where its `Trackdirection` points into the building, so no track can reach it.
  Put the stop spots inside the tunnel so the train stops out of sight. The same file warns that
  `TrainArrive` teleports when `Ramparrive` is more than 50 m from the train.
- Our first build copied `TrainStationCCP3`'s 14 train spots exactly. That table is in the first
  report §2 and in `station_build.py`.

**Building on both maps.**
- The template default `disabled_in_environment` is `set("Underground","Asteroid")`
  (`Building.lua:253`). Set `set("Asteroid")` on our own template, as vanilla's stations and the hub
  do. Never write the global `DisabledInEnvironment`.
- A plain `Building` switches its glow off when not working (`Building.lua:1422-1439`).

**The cave ceiling.**
- The underground flight roof is terrain + 100 m (`Flight.lua:82-83`).
- Vanilla's underground elevator shaft tops out at 128.6 m (`ElevatorUnderground` bbox z 12861).
- No Lua ceiling object exists.
- The in-game camera and ceiling read (`Measure()`) is **still owed**. Size the rope so it never
  visibly stops short, and report what you measured.

**The importer.** One mesh node and one material per entity. `hex_shape` faces are inset 0.9.
Blender (x, y) maps to game (−y, −x) × 100. All of this is in `_shared/IMPORTER_FACTS.md`.

## Scope

- **In:**
  - the depot's base entity: footprint, podium or blend, spots;
  - the assembled look: the 75 % elevator and tunnel visuals, cabin, rope and FX;
  - the placeable dev building on both maps, with trains in and out per D3;
  - live tunables the owner can move by eye;
  - renders if they help, and the viewing sitting.
- **Out:**
  - cargo between maps, store modes and the drone crew (next brief);
  - the twin and its placement rule;
  - vanilla's elevator, hub code and the hub's asset;
  - the rail shaft.

## Stops — report instead of continuing if

1. A train will not enter, stop and leave through the mouth with vanilla `Station` code (it refuses
   the route, teleports or sticks). Report with the log; do not write custom train movement.
2. No layout gets the mouth onto an 8 m hex-centred connector with the combined footprint under
   about 45 hexes (centre rule). Report the options with their numbers.
3. The installed build is no longer 25390750.

## Claim limits

Do not claim the look is accepted or that cargo crosses maps: nothing in this brief moves cargo.
You may claim what the owner has seen and said, and what `verify_station.py`-style re-imports and
`Report()` read.

## The sitting

Preload SMRTK slots (`tools/SMRTK.md`). At authoring, all six slots and Scratch in
`B:\Dev\SMR\SMR-BugFixPack-TestKit\Code\80_AgentSlots.lua` (kit `587f474`) were bound to the live
train-hub sittings. If they still are, use the dev mod's console helpers, say why, and never
rebind a slot another sitting owns. Give the owner about five steps at a time.

## Hand back

Commit with pathspecs in both repos. Report in `docs/agent/reports/ELEVATOR_DEPOT_LOOK_<date>.md`:
- your commits, the renders' paths and your design calls;
- the measured footprint, connector positions and rope height, and the ceiling read;
- what the owner saw and said;
- what you did not do.

Update this brief's row in `prompts/Train_Hub_Project/README.md`. Leave this file for the
orchestrator to park or delete. Skills: `doc-editing`, `prompt-authoring` (for the next brief's
notes). House rules are in `CLAUDE.md`, code policy in `docs/agent/FIX_POLICY.md`.
