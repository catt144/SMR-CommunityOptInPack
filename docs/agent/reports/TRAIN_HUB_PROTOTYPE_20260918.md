# Train hub prototype — pre-boot predictions and go/no-go record

**Authority.** Owner ruling 2026-09-18 (OI-10): “prototype B via 3a”, interchange only. The
prototype answers whether one station-class hub can carry at least three ordinary linear routes;
it does not test cargo routing or train route-switching. Appearance is deliberately unfinished.
Disposable saves only.

**Build call, before boot.** Commit `dfb8052` keeps the prototype in a separate dev mod under
`tools/prototypes/train_hub/`, outside the shipping mod's code list and excluded from its package.
It reuses `TrainStationLargeCCP3` so station storage and train surfaces remain vanilla, while Lua
computes three opposite connector pairs and their train movement points. Class and mod ids are
prototype-only and must not touch a kept save.

## Fixture to build

`<<PENDING-RUN>>` One prototype hub H and six vanilla end stations arranged as three independent
through-routes A–H–A′, B–H–B′ and C–H–C′, one route per opposite connector pair. Each route gets
one train. The named B and C ends start with zero Metals; A is stocked through the prepared setup
action. Stations must be far enough apart that drones and shuttles cannot carry between ends.
Both shipping mods and the TestKit stay loaded; neither shipping mod touches trains.

## Predictions written before boot

All timings below are planned operator limits, not measurements. Stop on the first unexpected
taint, Lua error, assert, or mutation and do not rerun for a preferred verdict.

1. **Boot status — Scratch / `SMRTK_ACTION action=slot_scratch`.** Expected `status=OK`; its DUMP
   names both repository heads, the clean stale-probe sweep, game build, map, taint read and
   `eligibility=UNAVAILABLE:sandbox`. First-screen witness: no console log overlay. Normal
   `<<PENDING-RUN>>` 10 seconds; abort `<<PENDING-RUN>>` 30 seconds.
2. **Computed-spot spike — slot 2 / `SMRTK_ACTION action=slot_2`.** With H selected, expected
   `status=OK`, `connectors=6`, six distinct connector hexes, six outward direction hexes and six
   valid connector elements. Before tracks, connected count may be zero; after the fixture it must
   be six. First-screen witness: the selected object is “DEV Train Hub Prototype”. Normal
   `<<PENDING-RUN>>` 10 seconds; abort `<<PENDING-RUN>>` 30 seconds.
3. **Fixture read — slot 1 / `SMRTK_ACTION action=slot_1`.** Expected `status=OK`; route DUMPs show
   three distinct two-station paths containing H, with one or more trains on each, and connector
   DUMPs show all six attached track ends. First-screen witness: three lines visibly leave H.
   Normal `<<PENDING-RUN>>` 15 seconds; abort `<<PENDING-RUN>>` 45 seconds.
4. **Resource setup — slots 3 and 4.** Slot 4 clears Metals at B and C to zero; slot 3 adds at most
   60 units at A, bounded by free capacity. Each act is MARK → mutation → DUMP → MARK and returns
   the selected station plus before/after stock. First-screen witness: the station storage row
   changes. Normal `<<PENDING-RUN>>` 10 seconds each; abort `<<PENDING-RUN>>` 30 seconds each.
5. **Train setup — slot 5 / `SMRTK_ACTION action=slot_5`.** Run once at each end station, never H.
   It refuses unless the station belongs to exactly one route. Expected `status=OK`; after game
   time advances, slot 1 shows one train on each route. First-screen witness: a train appears at
   that end. Normal `<<PENDING-RUN>>` one game minute; abort `<<PENDING-RUN>>` three game minutes.
6. **Interchange — pin B and C, then slot 6.** It refuses unless both destinations begin at zero,
   arms `hub_cargo_two_ends` plus Run Until, and pauses when both hold Metals. Expected trigger
   `status=OK` with positive `b_after` and `c_after`; slot 1 must still show three separate routes
   sharing H. First-screen witness: both destination storage rows become non-zero. Normal
   `<<PENDING-RUN>>` six sols; abort `<<PENDING-RUN>>` eighteen sols.
7. **Teardown.** With tracks and trains attached, use the vanilla demolish action on H, then read
   the toolkit error count and the complete flushed log. Expected: no Lua error or assert and no
   orphan connector at H's six hexes. First-screen witness: H and its attachment ends disappear
   cleanly. Normal `<<PENDING-RUN>>` 30 seconds; abort `<<PENDING-RUN>>` 90 seconds.
8. **Reload.** Rebuild if teardown was destructive, save to a disposable TestKit slot, reload it,
   then rerun Scratch, slot 2 and slot 1. Expected: H still has six connector elements, the three
   routes and trains remain, and cargo still transfers. Pins clear on load by design. Normal
   `<<PENDING-RUN>>` two minutes; abort `<<PENDING-RUN>>` six minutes.

## Confounds and standing observations

- Setup mutations are stock changes and train spawning only. They create the fixture but do not
  alter connector enumeration, route rebuilding, station balancing, teardown or persistence.
- Cheats are expected on this disposable colony. Count and attribute vanilla cheat markers once;
  toolkit action records are intentional and need no owner attribution.
- The four post-`f5fa650` toolkit observations remain a deliberate later sitting: depot fill/empty
  before/after, dark field-editor text, missing-field refusal followed by a live field trigger, and
  no console overlay. For this sitting each is **NOT RUN** unless the owner happens to witness it;
  the hub verdict does not depend on them.

## Result

**Sitting 1, 2026-09-18: STOPPED at prediction 2 on a Lua error; no verdict.** One colony
(`train1.savegame.sav`, sol 71, `BlankBig_02`), build 403908; the fingerprint lists both shipping
mods, the TestKit and `SMR_TrainHubPrototype_20260918`. Log
`%APPDATA%\Surviving Mars Relaunched\logs\Mars.exe-20260918-15.32.53-6a91a190.log`.

- **Prediction 2 held on its count:** slot 2 read `connectors=6 valid_elements=6
  connected_tracks=0 routes=0`, with six distinct connector hexes around a hub centred near
  (79,253): pair (1,2) at (86,253)/(72,253), pair (3,4) at (79,260)/(79,246), and pair (5,6) at
  (72,260)/(86,246). No track was attached, so attachment is untested.
- **It also read `errors=1`, and that error stopped the sitting.** Log lines 258–273:
  `[LUA ERROR] HGE::l_GetSpotBeginIndex: Invalid spot` at `Station.lua(620)` `CanBuildOver`,
  called from `Construction.lua(1749)` `UpdateConstructionObstructors` during placement. `this`
  was the `CursorBuilding` and the loop index was 5. Vanilla `CanBuildOver` reads spots from
  `cursor_obj` (1.1.0.403908 `Station.lua:615-622`). The cursor does not carry the prototype's
  virtual spot methods, so indices 1–4 came from the vanilla entity and index 5 failed. The hub
  still placed, but its placement obstruction check ran against the wrong hexes.
- **Owner, in play:** the connectors are invisible and the body reads as an ordinary station, so
  they could not tell where to connect track (*"I cannot tell where to connect the tracks"*).

Predictions 3–8 were not run. Sitting 2 follows the rebuild round
(`docs/agent/prompts/TRAIN_HUB_PROTOTYPE_high.md`). Do not issue a go/no-go or ask for asset
investment until the fixture, interchange, teardown and reload legs are recorded from one
colony.

## Round 2 — what changed, and predictions written before boot

**Build.** Pack `625053c` (dev mod version 2), TestKit `73f857e`. Parse-checked only; nothing
below has run in game. All source lines were read on 1.1.0.403908.

- **Placement (defect 1).** The hub carries its own `CanBuildOver`, vanilla's body with the six
  hexes computed from the cursor's position and angle. Two more literal `0..4` readers sat on the
  same path. `GridConstructionController:Activate` (`GridConstruction.lua:287-295`) moves a track's
  start from a connector element to its direction hex; a wrapper now does that for every hub
  connector. `PlaceUnderconstructionSigns` (`UnderconstructionSign.lua:41-56`) attaches signs to
  the vanilla body's `Sign` spots; the hub reports none, so no sign shows at the vanilla platforms.
- **⚠️ Connector geometry changed, and this is the round's largest unmeasured claim.** Vanilla
  resolves a station from a connector hex through the object hex grid
  (`Tracks.lua:19-24`, used by `TrackElement.lua:344`, `Tracks.lua:240,535` and `Train.lua:658`).
  A connector outside the body's footprint therefore cannot attach a track, and round 1's fixed
  radius 7 was never checked against the footprint, which is not readable from Lua source. Each
  connector now sits on the **last footprint hex along its line**, and its direction hex on the
  first hex outside. The radii print once: `[TrainHubPrototype] <entity> line radii d0..d5 = …`.
  The two diagonal lines will sit much closer to the centre than the long one.
- **Markers (defect 2).** Each line has one colour at both ends: **A (1,2) red, B (3,4) green,
  C (5,6) blue.** A marked end is four hex tiles, the connector hex and the three hexes beyond it,
  with a bouncing tutorial arrow above the first hex outside the body. The same tiles follow the
  placement ghost. Markers are unsaved and are rebuilt on load.

**Fixture.** Unchanged from above, with one constraint read from source: station centres must be
at least ten hexes apart (`Station.lua` `min_dist_to_other`, `Construction.lua:2924-2927`), so
place H first on open flat ground, then the six ends. A track to H starts by clicking a coloured
arrow hex, or the connector hex beside it.

Predictions 1 and 3–8 stand as written; slot 2's line gains fields. New lines:

- **R2-a. Placement raises no Lua error.** Move the ghost over open ground and once across an
  existing track (`CanBuildOver` runs only when something obstructs), then place H. Expected: the
  status bar's error count stays at its boot value and the log holds no `l_GetSpotBeginIndex`.
  First-screen witness: three coloured lines of tiles move with the ghost. Normal
  `<<PENDING-RUN>>` 30 seconds; abort `<<PENDING-RUN>>` 90 seconds.
- **R2-b. Slot 2, with H complete and selected and no placement ghost up.** Expected `status=OK`,
  `connectors=6 in_footprint=6 direction_free=6 valid_elements=6 marker_tiles=24
  marker_arrows=6`, and the radii line in the log. `in_footprint` below 6 is a geometry defect in
  the prototype, not a no-go: stop before dragging track and report. `marker_arrows=0` with the
  tiles visible is a marker shortfall the owner judges by eye. First-screen witness: two red, two
  green and two blue ends around H, each pair opposite. Normal `<<PENDING-RUN>>` 10 seconds; abort
  `<<PENDING-RUN>>` 30 seconds.
- **R2-c. A track starts from every line.** Clicking the connector hex of lines A, B and C each
  starts the track on the first hex outside the body, and the finished track reads as attached in
  slot 2 (`connected_tracks` rises, `destination` names the end station). A track that will not
  attach with `in_footprint=6` is the brief's **no-go** stop. Normal `<<PENDING-RUN>>` two minutes
  per line; abort `<<PENDING-RUN>>` six minutes.

**Sitting 2 result:** `<<PENDING-RUN>>`.

### Sitting 2 amendment, written before the cargo leg ran (orchestrator, 2026-09-18)

**Fixture, as built by the owner.** Save `Japan Sol 490.savegame.sav`, map `BlankBig_04`, sol
497. It is a large, populated colony, chosen by the owner for realism and kept as a test save for
later rechecks. It is never the owner's played game. Log `Mars.exe-20260918-18.41.47-6a91a190.log`.
H is `SMRTrainHubPrototype(8922)`, and the log prints its radii as `d0..d5 = 5 6 5 4 4 4`.

**Legs measured so far.** Slot 2 read `connectors=6 in_footprint=6 direction_free=6
valid_elements=6 connected_tracks=6 marker_tiles=24 marker_arrows=6 routes=3 errors=0` (id 150).
The log has no `LUA ERROR`. Slot 1 (ids 169–176) shows three routes through H:
- Line A: `9190 > H > 10099`, 2 trains.
- Line B: `1878 > 1867 > H > 6165`, 1 train.
- Line C: `9822 > H > 6150`, 2 trains.

A fourth route, `4782 > 4724`, does not touch H. Slot 1 reports `hubs=0` and leaves H out of its
station list. That is a TestKit counting gap, not a hub fault. Not recorded: whether the ghost
was moved over existing track, which is the only condition in which R2-a's error path runs.

**The confound, and the control that replaces isolation.** The owner reports that every end
station is inside drone range and H is outside it. The drone-range isolation the fixture above
asked for therefore does not hold. §7.2 T1 measured no drone deliveries into a
default-policy station in drone range: the stations' total held at 60. Drones can remove Metals,
which only slows the witness. The added control is conservation. Take a slot 1 read after setup
and before unpausing, then another after slot 6 fires. Read H's Metals last with slot 4, whose
`before=` is the read. **Pass:** B and C are both positive, and the Metals total across the seven
route stations, H and the trains does not exceed the post-setup total. **A rise in that total
voids the leg**, because drones fed Metals in and the leg cannot show a crossing through H. It
then has to be rerun with end stations outside drone range. Source: one line A end. B: a line B
end. C: a line C end. Every other route station and H are cleared first.

### Sitting 2 cargo leg: INCONCLUSIVE (orchestrator read, 2026-09-18)

Same log, lines 1040–1334.

- **Attempt 1 is void.** Slot 6 armed at `t=360360670` with every route station at 0 and the
  source at 60 (ids 349–413). A save cancelled both the witness and Run Until at `t=361375966`
  (`DISARM reason=SaveGameStart`, ids 414–415), and the witness never fired. H also read
  `enabled=false` for Metals at both of its reads (ids 250 and 419), so no Metals could have
  crossed H in that attempt. The log does not show who switched it off. For roughly two game
  sols in this period, the owner's console switched every drone hub and shuttle hub off. That
  was a setup mutation; the owner reversed it when colonists began to starve. The console lines
  themselves are not logged.
- **Attempt 2 fired, but its reading does not discriminate.** Metals was on at H (id 476). The
  owner restocked the source `StationSmall(10099)` from 0 to 60 (id 432), and slot 6 armed with
  `b_before=0 c_before=0` (id 436). The trigger fired after **24000 game-ms** at sol 504:
  `b_after=1 c_after=4` (id 440). **No pre-arm station read exists for this attempt.** The clear
  command's `[HUBTEST]` line is absent, and slot 1 did not run before arming. After the fire
  (ids 448–479), the seven route stations held 43 in total: source 32, the two middle stations on
  line B 2 and 4, B 1, C 4, and the line A and C far ends 0 each. H held 0 and every train
  carried 0. The off-hub `StationSmall(4782)` had risen from 0 (id 352) to 6. Drones were on.
- **Why it does not count.** The pre-registered conservation control catches drones adding
  Metals. It does **not** catch drones moving Metals from one station to another inside the
  fixture, and that path is open here. Every end station is in drone range, 17 of the source's 28
  departed units are missing from stations and trains, an off-network station gained 6, and H,
  the one station out of drone range, held 0 at the read. INFERRED, not measured: drones filled
  B and C directly from the source. Nothing in this log shows a Metals unit leaving H on a
  different route from the one it arrived on.
- **Still standing from sitting 2:** R2-a over open ground, R2-b and R2-c all pass. So do three
  routes through H with trains, with 0 Lua errors. Teardown and reload are NOT RUN.

### Sitting 2 teardown and reload, and the verdict

- **Teardown: PASS, as a proof of concept.** Tracks and trains were attached. The TestKit logged
  `selected_destroy method=CheatDestroy ... valid_after=true` (id 482), which leaves a wreck. The
  owner then cleared it with the vanilla salvage action, and the log does not record that action
  itself. The owner's screenshot shows H gone, its stock left on the ground as stockpiles, and
  the six lines ending cleanly with no visible track stub at H. The whole log holds 0 `LUA ERROR`
  and no assert (`grep -c "LUA ERROR"` = 0; `grep -i assert` = no match). Invisible orphan
  connector elements were not read.
- **Reload: PASS for a colony whose hub was removed.** The owner saved after the salvage, at a
  game time later than id 482, and reloaded. The load lists the prototype mod and raises no error
  (lines 1343–1431). A reload of a *working* hub was not run.

**Verdict: QUALIFIED GO (owner, 2026-09-18).** The owner asked for *"a proof of concept"* and
did not need *"perfection before we move to the next phase"*. Proved in one colony: six
connectors, all attached; three routes through H with trains stopping at it; placement and
removal with 0 Lua errors; a clean reload after removal. **Carried into the next hub build as
must-pass checks:**
1. A direct cargo witness: a Metals unit unloaded at H by one route and loaded by another.
2. A save and reload with a working hub.
3. Why H read Metals `enabled=false` in attempt 1.
4. Placement across existing track, the R2-a path that was not exercised.
5. A slot 1 that lists H.
