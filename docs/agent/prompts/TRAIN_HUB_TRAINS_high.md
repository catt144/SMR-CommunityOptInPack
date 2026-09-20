# Train hub build 3b: trains at the hub

⛔ **HELD, 2026-09-20.** The owner ran the first batch's steps 1-3 (report §"Build 3b", "Owner
sitting, 2026-09-20") and then redirected: trains ride the **centre** of our track and merge from
beside the vanilla rail on a longer stub (spec §9). Do not set a park distance or continue the lane
smoke; the model brief `TRAIN_HUB_MODEL_high.md` runs first and a short movement prototype follows.

**Was: LIVE, owner visual sitting next.** Implementation and unattended smoke are recorded in
[`TRAIN_HUB_BUILD_20260918.md`, Build 3b](../reports/TRAIN_HUB_BUILD_20260918.md#build-3b-2026-09-20).
That section carries the tested 20 m build, exact evidence and remaining first batch; do not
repeat the implementation below as new work. The native save/reload test passed; visual
acceptance, including the timed turn and queue, remains open. Shared TestKit slots are prepared.

Re-scoped 2026-09-20 after the owner set aside the step-0 gate. This
task owns `tools/devmods/train_hub/Code/20_TrainHub.lua`. Build 4 (`TRAIN_HUB_REPAIR_high.md`)
remains held behind it: a hub whose trains float is not smokeable for repairs.

Authoring sha: SMR-OptInPack `6019492`. `git diff --stat 6019492..HEAD --
tools/devmods/train_hub/` empty means this brief's facts hold.

⛔ **DO NOT DESIGN AROUND A TRAIN LENGTH OF 41.5 m.** That figure is **DISPUTED** (report §13). The
owner measured a train against the game's own hex grid with a superimposed build cursor at **about
two hexes, ~20 m, with three hexes of comfortable margin**. Where the two disagree the hex
measurement governs. Park position is a tunable in our own Lua, so it is tuned to what looks right
and judged by eye, not solved from a number.

## Authority

**Owner, 2026-09-19, from build 3's smoke — the end state, settled; do not re-argue it.** Trains
slide across the open interior, jump to the far side when they leave by the track they came on, and
shift sideways into the portal legs. The owner **keeps the open-ring design** and ruled the fix is
**code**: the vanilla model was considered and rejected, because the train spots are computed in our
Lua whatever the body looks like. **Trains wait outside the hub for their turn** — vanilla already
does this, keep it.

**Owner, 2026-09-20 — park position is a tunable, and that is the whole answer.** The hub's Stop,
Spawn, Ramparrive and Rampdepart are **synthetic spots computed in our own Lua**
(`synthetic_spot_pos`, `kind_sevenths`; Stop and Spawn currently at 3/7 of the way to a connector,
ramps at 5/7). Where a train parks is therefore a number we own. The owner's ruling:
*"We should be able to manipulate where its parked, that's got to be easier than resizing the mesh,
building a tunnel onto the mesh, or runtime scaling the train."*

**So expose the park distance as one clearly named tunable and tune it by eye.** The owner judges it
in the smoke and may move it live. No asset change, no mesh work, no `SetScale`, no redesign. A
whole session of alternatives — runtime shrinking, three alternating lines, a new tunnel hood,
`FOOTPRINT_R = 5`, resizing the dome — was generated downstream of the disputed 41.5 m and is
**withdrawn**. Do not revive any of it.

The earlier same-day rulings it replaces, for the record: the tail was to overhang outward through
the portal rather than at the centre, and an unnoticeable overhang was acceptable while a train
visibly half out of the station was not. **The look standard still stands** — it is now met by
tuning the number rather than by changing the body.

**Testing depth: a smoke test only** (owner, 2026-09-19); the full prediction battery runs once, on
the final build. `FIX_POLICY` §0 sets this mod's risk standard and both bans bind. This build adds
no persisted state unless the crossing lock must survive a save, in which case name it once and add
it to the persisted-name inventory in the same commit. MODULE FREEZE does not apply: the dev mod is
not a shipping module.

## State: what the oracle settled (committed; each a claim, one check clears it)

Read `docs/agent/reports/GEOMETRY_ORACLE_20260919.md` §11 in full before building. Its numbered list
is your work order and this section does not replace it. The instrument is
`C:\Dev\SMR-Assets\_shared\geometry\hub_oracle.py` at SMR-Assets `66240ae` (`--corpus` 24/24,
`--selftest` 8/8, re-run by the orchestrator on 2026-09-20); its README says how to run it, and §11
carries the exact command with `--element-spots` and `--connector-directions`.

- **The table is wrong and the correction is known.** `hub_connector_directions = {0,3,1,4,2,5}`;
  the imported body's connectors 1..4 lie on hex directions `4,1,3,0`. The corrected table is
  `{4,1,3,0,2,5}`. `CanBuildOver` (`20_TrainHub.lua:329`) reads it too. Correcting it clears all
  four 50 m arrival teleports and the 120° misplacement of every synthetic spot on connectors 1-4.
  **That correction is yours to make**; the oracle only modelled it.
- **The lane rule is the side of travel, not a fixed spot name** (R-LANESIDE, CONFIRMED, §11). A
  train takes the spot **289 units to the right of its own direction of travel**. Which *name*
  (`Enter1` or `Enter2`) that is at a given connector is per-map state: the element's angle points
  at its track's start end and `step` flips with it, and the two flips cancel. **Code that needs the
  spot asks the track (`step`), never hard-codes a name.** §11's table gives the twelve ARRIVE and
  DEPART points in hub-local units.
- **A train holds its arrival yaw through every station slide** (R-YAW, CONFIRMED from source,
  `Train.lua:507-519`, `:470-476`; the one exception is the same-track departure, which takes the
  Spawn spot's angle, `Station.lua:1188-1193`). **Nothing in the game's station code will turn your
  train.** Your centre turn has to set the yaw itself.
- **Platform occupancy is enforced and trains queue on their track for it.** `Train:CanEnter`
  (`Train.lua:616-624`) asks `GetOccupyingTrain(track, "arrive")`; other call sites are
  `Track.lua:433, 453`, `Tracks.lua:995, 1017`, `Train.lua:95, 136, 258, 389, 825`. Vanilla reserves
  the **opposite** platform on arrival and validates a reservation by distance to `Spawn<platform>`
  (`Station.lua:1150-1180`). The coincidence that makes today's validation hold (Stop_k = Spawn of
  the opposite connector, 0 units) survives the table fix — **and moving Stop will break it.** Check
  it as you go.
- **One stale flag, left alone deliberately:** the oracle prints "rests on UNCONFIRMED: R-ELEMENT"
  on the path verdicts even with the measured fixture. §2 holds R-ELEMENT CONFIRMED. Do not chase it.

## End state (the owner's decisions; the mechanism is yours)

0. **Make the park distance a tunable, and tune it.** One clearly named constant, not a magic
   fraction buried in `kind_sevenths`. Start from what the current 3/7 puts on screen, move it until
   the train sits well on its line, and bring it to the smoke for the owner to judge and adjust.
   Report where you landed and why. **While you are in there, settle the length**: measure a
   stopped train against the hex grid and, separately, read the engine's own bbox and each
   auto-attached part rather than the assembly's. `TrainCCP3` has no mesh of its own and `Train` is
   an `AutoAttachObject` (`Train.lua:16`), which is why the assembly read is in doubt. Record the
   result in report §13 and mark R-TRAIN resolved or still disputed.

1. **The line is the platform.** A train arriving on line `k` stops along line `k` and loads there;
   it never slides into the interior to load. The distance out is item 0's tunable.
2. **Reverse in place.** `Spawn<k>` at `Stop<k>`'s position **facing out along its own connector**,
   so vanilla's teleport becomes an invisible 180° flip where the train stands. This is what kills
   §11 item 2: today the hub computes a Spawn angle as centre-to-spot and puts the spot on the
   *opposite* connector's side, so the train faces 180° away from the connector it leaves by and
   runs the whole departure backwards. Vanilla's Spawn spots face their own connector.
3. **Spots on the lanes** (§11 item 1, the lane dogleg). Today the element spots sit 289 units
   right of the centreline and the hub's Ramparrive, Stop, Spawn and Rampdepart sit *on* it, so
   every arrival and departure includes a 1179-unit slide at 14.2°. Put the arrival-side spots on
   the ARRIVE lane and the departure-side spots on the DEPART lane, right of travel.
4. **Route through the centre, and turn there** (§11 item 3). Departing on another line is 2491
   units (60°) or 4000 (120°) across open floor, and by R-YAW the train crabs the whole way unless
   you turn it: line `k` → the crossing → turn (`SetAngle` with a time, never a snap) →
   `Rampdepart<j>` → out. Your call on waypoints; the owner judges the turn in the smoke. **If the
   pivot reads as a bar swinging rather than a train turning**, the fallback is vanilla's own trick:
   the train leaves by its portal and reappears on line `j`. Report which you shipped and why.
5. **Occupancy and the crossing lock** (§11 item 5). A platform is the line's own connector, plus
   one lock for the crossing, so two trains never cross the interior at once and a train whose line
   is busy waits on its track outside the portal. 1224 of 1995 path pairs still come within a train
   width under the corrected table, so the lock is load-bearing. Keep every call site above
   satisfied. **Re-run the oracle's TWO-TRAIN once your spots are on the lanes and your routes turn
   at the centre** — the number the lock has to cover is not §11's.
6. **Smoke with the owner**, about five steps at a time, one colony: a train arrives and loads on
   its line; leaves straight through; leaves by a 60° and a 120° line; leaves by the track it came
   on; two trains at once, the second waiting outside; a save and reload with one train stopped and
   one crossing; the track-to-line join at the portal, from ground level. The game cannot turn
   autosave off — after one, the owner re-presses the armed slot.
7. **One free measurement while you are in there** (optional, drop it first if time runs short):
   slot 6 already prints a train's angle, so a read taken **mid-slide** would turn R-YAW from
   source-confirmed into measured. Record it in report §11 if you take it.
8. **Record** in the hub report and spec §10. Owner rulings go in the record the obeying role reads,
   never only in chat.

**Done means:** a train arrives, loads, and leaves the hub by any of the six lines without leaving
the deck, sliding over open floor, crabbing sideways, or teleporting visibly; two trains never
touch; and the oracle, re-run on your spots, agrees with what the smoke showed.

## Scope

**In:** `20_TrainHub.lua`, TestKit slots, re-running the oracle as a check, the sitting, the records.
**Out:** the asset and the body (report what it should change — §11 item 4's ring-wall
pass-through is the orchestrator's and the look pass's, not yours); build 4's drones; loading speed;
editing the oracle beyond running it, and the hub's economy (spec §10, the owner's).

## Stops

- **No park distance looks right on this body.** If tuning the number cannot produce a train that
  sits well — not because of a figure, but because you have looked at it — report what you tried
  with what each looked like, and stop before any asset proposal. That is the owner's call.
- **Vanilla's occupancy call sites cannot be satisfied without wrapping `Train.lua`**, or moving
  Stop breaks the reservation validation in a way you cannot repair in our Lua: report the wrap or
  the break.
- **A train stopped on its line blocks the crossing for a straight-through train on that line:**
  report it with the choice between through trains waiting and the stop moving.

## Do not claim

Not "trains behave like vanilla's": vanilla hides its slides inside a five-hex building and ours are
in the open. Not that the oracle's numbers are observations — they are predictions, and until your
smoke runs no train movement has been watched since `6123ae7`. Claim what the smoke showed, per line
and per departure kind, from the owner's view.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` when the smoke is recorded.
