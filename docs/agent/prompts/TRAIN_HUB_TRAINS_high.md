# Train hub build 3b: trains at the hub

**READY: build 3's smoke is recorded.** This task now owns
`tools/devmods/train_hub/Code/20_TrainHub.lua`. Build 4 (`TRAIN_HUB_REPAIR_high.md`) remains held
behind it: a hub whose trains float is not smokeable for repairs.

⛔ **HOLD: this brief's premise is contradicted by a measured finding. Read the geometry oracle's
report before acting on anything below** (`docs/agent/reports/GEOMETRY_ORACLE_20260919.md`; the brief is consumed).

The brief below assumes the trains misbehave because `Train:GotoSpot` slides are exposed in an 80 m
building, and prescribes stubs-as-platforms, reverse-in-place and centre routing. That premise is at
least partly wrong. `hub_connector_directions = {0,3,1,4,2,5}` in `20_TrainHub.lua` does not match
the imported body: the body's connectors lie on hex directions `[4,1,3,0,2,5]`, so indices **1 to 4
are wrong** and 5 and 6 are right. Connectors resolve from the body and are correctly placed (boot
log, `connector spots: from the body`), but every synthetic `Ramparrive`/`Stop`/`Spawn`/`Rampdepart`
goes through that table, so on four of six lines they are computed on a **different line from their
own track**. Connector-to-Ramparrive is then 59.7 m on lines 1-4 against 11.4 m on 5-6 — and
`Station.lua:1105` replaces the slide with an instant `SetPos` teleport beyond 50 m. That retrodicts
both the far-side jump and the sideways drift into the portal legs.

Derived independently three times from files (the oracle, GPT-5.4 blind via Codex, and the
orchestrator from `Entities/SMROptInTrainHub6.entjson`), each agreeing; a constant hex-convention
offset cannot explain it, because the required offsets differ (0, 2, 4). **MEASURED in game
2026-09-19**: the owner's console read and TestKit slot 6 `geometry_reads` (kit `bd32d30`) returned
all 24 synthetic spots and six connectors with zero delta from the file-side prediction
(`docs/archive/geometry_oracle_slot6_Mars.exe-20260919-23.01.18-6a91a190.log`). The same read
measured the lane: each element's `Enter1`/`Enter2` sit 289 units (HexSize/2) left and right of
the track centreline at the connector hex centre, so end state 3's offset is known; the report's
§3 has the per-line paths and what a corrected table leaves for this build.

Consequence: much of what this brief asks for may be a one-line table correction rather than a
redesign, and the remainder may be only end state 1, stopping on the stub instead of inside the
ring. Re-scope against the oracle's report before building; the owner expects that re-scope, not
fidelity to the text below.

## Authority

**Owner, 2026-09-19, from build 3's smoke.** Trains arriving at the hub dropped through the beam to
the floor to load, climbed back and snapped to their track. After the deck-height fix (`6123ae7`)
they stay at deck height but slide across the open interior to wherever their next spot is, jump to
the far side and float back when they leave by the track they came on, and shift sideways into the
portal legs where the vanilla track meets our stub. **The owner keeps the open-ring design** and
ruled the fix is code: the vanilla model was considered and rejected, since the train spots are
computed in our Lua whatever the body looks like. **Trains wait outside the hub for their turn**
(owner): vanilla already does this, keep it. Testing depth: a smoke test only. `FIX_POLICY` §0 sets
this mod's risk standard; both bans bind; this build adds no persisted state unless the crossing
lock must survive a save, in which case name it once and add it to the inventory in the same commit.

## What the game does (read on 1.1.0.403908; each line could falsify it)

- **A train's move between station spots is a straight timed slide**, `Train:GotoSpot`
  (`Train.lua:507-519`): `SetPos(spot_pos, move_time)` with pitch handling only, no path and no
  yaw. Vanilla hides the slides inside a five-hex building. Our spots are up to 34 m apart.
- **Vanilla's spot choreography** (`Station.lua:1085-1118`, `:1183-1207`): arrive → `Ramparrive<k>`
  → `Stop<k>`; depart on `j` → `Rampdepart<j>` → the track element's `Enter1/2`; depart on the
  arrival track → `SetPos(Spawn<k>)` + `SetAngle`, a teleport, then `Rampdepart<k>`.
- **Platform occupancy is enforced**, and trains queue on their track for it: `Train:CanEnter`
  (`Train.lua:616-624`) asks `GetOccupyingTrain(track, "arrive")` before leaving the last element;
  `ShouldStopOnTrack` holds them. The other call sites are `Track.lua:433, 453`, `Tracks.lua:995, 1017`,
  `Train.lua:95, 136, 258, 389, 825`. Vanilla's bookkeeping (`Station.lua:1150-1180`) reserves the
  **opposite** platform on arrival and validates a reservation by distance to `Spawn<platform>`.
- **Our spots are synthetic** (`20_TrainHub.lua`, `synthetic_spot_pos`, `kind_sevenths`): Stop and
  Spawn at 3/7 of the way to a connector, ramps at 5/7, Spawn on the opposite connector's line,
  all now lifted to the deck (`train_deck_height`). The connectors are on the beam centreline at
  4,000 units and z 800; the beam is 3.5 m wide.
- **Vanilla trains run in a lane, not on the centreline** (owner's screenshots): the offset is
  **not measured**. It is the first thing to measure: a train's position against its element's
  position on a straight track, or the element's `Enter1`/`Enter2` spot offsets.

## End state (the owner's decisions; the mechanism is yours)

1. **The stubs are the platforms.** A train arriving on line `k` stops on stub `k`, centred under the
   portal arch, and loads there; it never enters the interior to load. Your call on the exact
   distances; the train must clear the connector hex so the track stays free behind it.
2. **Reverse in place.** `Spawn<k>` at `Stop<k>`'s position facing out, so vanilla's teleport is an
   invisible 180° flip where the train stands.
3. **Lanes.** Ramparrive on the arriving lane, Rampdepart on the leaving lane, at the measured
   offset, so the slide from the last element is straight along the rail. Report the number; the
   orchestrator restyles the stub to vanilla's two-lane profile from it.
4. **Route through the centre.** Departing on another line: stub `k` → the crossing → turn there
   (`SetAngle` with a time, never a snap) → `Rampdepart<j>` → out. Straight-through trains already
   cross the centre. Your call on waypoints; the owner judges the turn in the smoke. **If the pivot
   reads as a bar swinging rather than a train turning**, the fallback is vanilla's own trick: the
   train leaves by its portal and reappears on stub `j`. Report which you shipped and why.
5. **Occupancy.** A platform is the stub's own connector, plus one lock for the crossing, so two
   trains never cross the interior at once and a train whose stub is busy waits on its track outside
   the portal. Keep every call site above satisfied; the reservation validation by distance to
   `Spawn<platform>` must still hold for your spots.
6. **Smoke with the owner**, five steps at a time, one colony: a train arrives and loads on its stub;
   leaves straight through; leaves by a 60° and a 120° line; leaves by the track it came on; two trains
   at once, the second waiting outside; a save and reload with a train on a stub and one crossing;
   the track-to-stub join at the portal, from ground level.
7. **Record** in the hub report and spec §10; the lane offset goes in spec §9's cargo/spot facts.

**Done means:** a train arrives, loads, and leaves the hub by any of the six lines without leaving
the deck, sliding over open floor, or teleporting visibly, and two trains never touch.

## Scope

In: `20_TrainHub.lua`, TestKit slots, the sitting, the records. Out: the asset (report what it should
change), build 4's drones, loading speed (occupancy makes it a balance number, not a safety one).

## Stops

- Vanilla's occupancy call sites cannot be satisfied without wrapping `Train.lua`: report the wrap.
- The lane offset is not one number (it depends on the element or direction in a way you cannot
  express in a spot): report the shape of it.
- A train on a stub blocks the crossing for a straight-through train on the same line: report it,
  with the owner's call whether through trains wait or stubs shorten.

## Do not claim

Not "trains behave like vanilla's": vanilla hides its slides in a building and ours are in the open.
Claim what the smoke showed, per line and per departure kind, from the owner's view.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` when the smoke is recorded.
