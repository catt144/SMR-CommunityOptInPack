# Train hub: the transition, and trains on the centre of our track

**LIVE, fire when ready.** Owns `tools/devmods/train_hub/Code/20_TrainHub.lua`. Authoring shas:
SMR-OptInPack `<HEAD at fire>`, the imported model is SMR-Assets `TrainHub_work.blend` as exported
2026-09-20 (untextured). Build 4 (`TRAIN_HUB_REPAIR_high.md`) stays held behind this.

## Authority

**Owner, 2026-09-20 — function before texture.** *"Just function, no textures until I fully green
the function from transition, enter, load, exit and transition back on the vanilla track."* No
texture pass, no bake, no material work, and no asset change unless a stop below forces one. A
re-import throws away a bake, so the model is frozen only after the owner greens the whole cycle.

**Owner, same day — the method.** Quick and iterative. Prototype the action, let the owner look,
then dial it in by eye. No oracle run, no prediction battery, no redesign options. A smoke test only.

**Owner, same day — the action to build, in their words.** *"Getting the end of the train to stop as
soon as it clears the vanilla portion and smoothly slide over onto our track and then move forward
into the tunnel."* And the mirror on the way out, back onto the vanilla track.

**Owner, same day — trains ride the CENTRE of our track inside the hub.** This replaces build 3b's
two-lane interior: on vanilla track a train rides beside the rail, on ours it rides on top, down the
middle. 3b's 13 m park distance was measured against a lane and is a starting number only — judge it
again on the centre. Build 3b is retired into this brief; its implementation, its unattended smoke
and the owner's sitting are recorded in `TRAIN_HUB_BUILD_20260918.md` §"Build 3b", and the geometry
rules it was built on are `GEOMETRY_ORACLE_20260919.md` §11. Read both; do not redo them.

⛔ **The train's length is DISPUTED** (`GEOMETRY_ORACLE_20260919.md` §13). The owner measured about
two hexes against the game's hex grid; a `GetEntityBBox` read said 41.5 m. **Do not solve any
position from a train length.** Both new positions below are tunables, tuned by eye.

## The model you are building against (imported and in game, 2026-09-20)

Each of the six lines now ends in a two-hex stub with its connector at **50 m** from the hub centre,
and twelve **transition platform arms**, three hexes long, one either side of every line. Each arm's
deck top is at **8 m**, level with the stub, and its centre is **3.45 m** off the line, so a train
riding 289 units (2.89 m) off the line sits on it with the beam carrying its inner side. The one-hex
path between each pair of arms is where the vanilla track runs in. MEASURED by the owner in game:
the hub places, a track attaches down that path, and a train parks on the deck at the right height.

**The six loading sidings are in the model too** (imported and seen in game 2026-09-20; the
generator constants are `SIDING_*` in `C:\Dev\SMR-Assets\trainhub\blender\hub_skeleton.py`, and spec
§9 records the pass). One runs beside each interior spur, all six on the same hand — the owner
confirmed the side in game. Each deck runs **from about 3.0 m to 22.7 m from the hub centre** along
its spur, is **4.0 m wide** outward from the beam's edge, and its top is at **8 m**, level with the
beam and the stub. Its inner end is cut parallel to the neighbouring spur so a train passing there is
not clipped. The frame carries an opaque panel in the body mesh — real glass is the texture pass's
question, gated. ⛔ **These are the dimensions to place the loading position against; do not solve it
from a train length** (see the dispute above). Anything the sidings turn out to need is an asset
change and therefore the owner's call, not this build's — report it, per the stops.

## End state (the owner's decisions; the mechanism is yours)

1. **Inside the hub, a train is on the centreline** — arriving, stopped, loading, turning, crossing
   and departing. `lane_offset` (`20_TrainHub.lua:171`) stays as the reader of vanilla's own
   `Enter1`/`Enter2`, because outside the connector the train is still vanilla's and still beside the
   rail. What changes is where our synthetic spots put it once it is ours.
2. **The transition in.** The train runs in beside the rail, over the arm, and **stops the moment its
   tail clears the last vanilla element**; then one smooth lateral move onto the centre; then forward
   into the tunnel to its stop position. Two clearly named tunables, not magic fractions: **where it
   pauses before the slide**, and **the park distance**. Bring both to the smoke for the owner to
   move live. Lead, not the route: vanilla's arrival is already two moves, `GotoSpot("Ramparrive")`
   then `GotoSpot("Stop")` (`Station.lua:1097-1121`, 1.1.0.403908), and both spots are ours to place;
   mind the 50 m teleport at `Station.lua:1105`. The smoothstep lateral join already in
   `HubRouteTrain` (`20_TrainHub.lua:462-479`) is the same move at twice the distance — reuse it, it
   is defined by distance along the path, so its shape holds at any game speed.
3. **The transition out mirrors it**, ending with the train beside the rail on the other arm, riding
   the vanilla track away as normal.
4. **Loading happens on the siding, not on the centre** (owner, 2026-09-20; the model pass added six,
   one per spur, and they are in the game — the geometry is above). ⚠️ **This is TWO more movements
   than build 3b had, on top of the transition in and out, and they are the point of this item:**
   **(a) off the running centreline onto the siding**, ending parked on the deck where it loads, and
   **(b) back off the siding onto the centreline** once its exit is free, feeding into the departure.
   Between them the train **waits on the siding for a free lane** — that wait is the whole reason the
   sidings exist, and its duration is the traffic's, not a timer's. Name both movements and their
   positions as tunables the owner moves live, the same way the pause and park distances are.
   This is what answers the question build 3b's pass hit and deferred: vanilla picks a loading train's exit only after it has loaded, and with a siding
   a blocked exit no longer forces a choice between blocking the running line and reversing into the
   arrival lane. ⛔ **Fold the slide into the braking and the rejoin into the acceleration** — one
   curved motion, never stop-then-slide-then-stop. The hub already adds transitions to every trip and
   the owner will not accept them costing time: *"I want the transition to be quick but smooth
   because we are adding so many transitions."* The `Stop` spot moves onto the siding, so re-check the
   reservation validation build 3b flagged. **Loading policy and full queueing are the owner's next
   pass, deferred 2026-09-20; do not design them here.** The occupied-exit guard (`2606719`) stays.
   **The owner supplies the movement parameters by eye in the sitting** — expose them, do not solve them.
5. **The cold-start power fix** (spec §10, owner 2026-09-20): a hub must start in a remote, droneless
   place with no grid. Today `CreateElectricityElement` (`20_TrainHub.lua:877`) counts its production
   only while the hub is working, and a hub with no other supply never works. Make production count
   while it is merely unpowered, and stop only for malfunction or switched off. It is the same file,
   so it goes in here. The fixtures carry seven Stirling Generators that mask this (spec §10), so the
   owner removes or disables them for that one check.
6. **Halve the loading dwell, for hub trains only** (owner ruling, 2026-09-20; spec §10 holds the
   measurement and the source lines). A vanilla stop is a flat **12 game seconds** each way —
   `Train:LoadTrain` and `Train:UnloadTrain` both end on
   `WaitWakeup(Max(const.HourDuration / 5 - GameTime() + time_stamp, 100))` (`Train.lua:281`, `:450`,
   1.1.0.403908) — so a train that unloads and loads stands for about 24 s. Vanilla never wakes a
   train early, but `command_thread` is a public `CommandObject` field
   (`CommonLua/Classes/CommandObject.lua:90`) and a `Wakeup` on it ends the stop at a moment we pick;
   the cargo has already moved before the wait, so nothing is skipped. Owner's words: *"cut each in
   half... 6s / 6s so the whole transfer can take a max of 12s if it has to do both."*
   ⛔ **Only trains stopped at our hub.** The owner declined a colony-wide override: *"I would rather
   not over ride it for all stations unless we can't find other ways to make it 'feel' good."* A
   vanilla station's 12 s stays 12 s. Build it as a named constant the owner moves live in the smoke,
   timed in **game time** so it scales with the speed slider as vanilla's does, as a deadline from the
   start of the command with vanilla's 100 ms floor, not as an added delay. ⛔ **The slide and the
   reversal turn are measured and DEFERRED** (spec §10: 1.2 s a slide, twice a visit; 1 s a turn).
   The owner wants the halved dwell in front of their eye first and rules on those after. Do not
   change either here.
7. **Keep vanilla's occupancy and reservation contract satisfied.** The call sites and what build 3b
   found about them are in the hub report §"Build 3b", "Reservation contract". Moving `Stop` breaks
   the coincidence that makes reservation validation hold today — check it as you go.
8. **Smoke with the owner**, about five steps at a time, one colony: a train arrives, pauses, slides
   on and comes in; it loads; it leaves and transitions back onto the vanilla track; a 60° and a 120°
   departure; two trains at once with the second waiting outside; a save and reload with one train
   stopped and one crossing. Autosave disarms a crossing watch — the owner re-presses the slot.
   Include the dwell: the owner watches one hub stop against the clock and says whether 6 s feels
   right, and **one vanilla station stop is the control** — it must still take 12 s.
9. **Record** in the hub report and spec §10, and commit with pathspecs. `doc-editing` first.

**Done means:** the owner can watch a train come off the vanilla track, stop, slide onto our centre,
run in, load, leave and slide back, and say it looks right — at normal, fast and fastest speed.

## Scope

In: `20_TrainHub.lua`, TestKit slots, the sitting, the records, the cold-start fix.
Out: textures, materials and any re-import; the asset (report what it should change); build 4's
drones; routing; the hub's economy; the oracle; the four-connector hub.

## Stops

- **The pause-and-slide cannot be done without wrapping `Train.lua`**, or the stop position breaks a
  reservation you cannot repair in our Lua: report the wrap or the break, do not do it.
- **No arm length or deck width makes the move look right** — not from a number, but because you have
  looked at it: report what you tried with what each looked like. An asset change is the owner's call.
- **The cold-start fix needs persisted state or a vanilla wrap:** report it; it is a small fix or it
  is the owner's.

## Do not claim

Not "the transition works" from a desktop harness: it is a look, and only the owner's eye closes it.
Not that trains behave like vanilla's — vanilla hides its slides inside a five-hex building and ours
happen in the open. Claim what the smoke showed, per departure kind, from the owner's view.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` when the owner's smoke is
recorded.
