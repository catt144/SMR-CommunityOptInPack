# Geometry oracle — the instrument, its rules, and build 3b's geometry answers

**Authority.** Owner, 2026-09-19: every train-hub failure so far was geometry, caught by eye
after a manual re-import; buy that loop out (`GEOMETRY_ORACLE_high.md`, consumed by this report).
Its two standards are met as written: the five paid-for failures are retrodicted without tuning,
and every rule carries two derivations and a status. Labels as in the hub reports: **MEASURED**
(a command ran), **SOURCE** (game Lua read on 1.1.0.403908 from
`C:\Dev\SMR-SrcArchive\1.1.0.403908\Src`), **OBSERVED** (a log or the owner in game),
**UNCONFIRMED**. Game runs tonight were the owner's; this session ran none.

## 0. Outcome

**The instrument:** `C:\Dev\SMR-Assets\_shared\geometry\hub_oracle.py` (stdlib Python, runs
without either mod repo; SMR-Assets commit of 2026-09-19 "Geometry oracle"). It reads the entity
file, the hub Lua (parsed, not re-typed) and the Blender skeleton, and prints a verdict per
invariant with the rule each rests on, its provenance and CONFIRMED/UNCONFIRMED; `--json` for
machines; exit 1 on any FAIL. `--corpus` replays the five failures from git-extracted fixtures
(`corpus/`, truths and log lines in `EXPECTED.json`): **17 of 17 truths reproduced** (24 of 24
since run B added two vanilla shapes, §10).
`--selftest` breaks each invariant and asserts only that one flips: **6 of 6**. Both MEASURED by
this session on the committed file (`python hub_oracle.py --corpus`, `--selftest`).

**The root cause behind the train choreography failures is in the code, not the asset.**
`SMROptInTrainHub6Base.hub_connector_directions = {0,3,1,4,2,5}` names the hex direction each
connector index lies on, but the imported body's connectors 1..4 lie on directions 4, 1, 3, 0
(5 and 6 on 2 and 5 as written). Every synthetic Ramparrive/Stop/Spawn/Rampdepart for connectors
1 to 4 is therefore computed on a different line from the track that uses it. MEASURED in game
2026-09-19: the owner's console read of all six connectors, Stop and Ramparrive spots, then TestKit
slot 6 (`geometry_reads`, kit `bd32d30`) reading all 24 synthetic spots, match the file-side
prediction with **zero delta on every spot** (`docs/archive/geometry_oracle_readings_20260919.log`,
`docs/archive/geometry_oracle_slot6_Mars.exe-20260919-23.01.18-6a91a190.log`).

## 1. Retrodiction of the paid-for failures (MEASURED, `hub_oracle.py --corpus`)

| failure | fixture | game truth | oracle |
|---|---|---|---|
| 85 outline hexes, radii 5 5 5 5 4 4 | `preinset_06b5a62` | log 13.47.41 line 412; owner console 85 | FOOTPRINT FAIL: 61 certain, 30 ambiguous, band [61, 91]; each game radius inside [certain 4, union 5] |
| 66 hexes, radii 4×6 | `prefixbox_d07a457`, `current_5002a49` | logs 19.05.02 … 20.33.45 | 66 certain, 0 ambiguous, radii 4×6, inset margin 49.999 units |
| cubes beside their beds | `prefixbox_d07a457` | owner; the five-cube fit | CARGO FAIL: 1 of 60 on every bed |
| 60 of 60 cubes | `current_5002a49` | slot 3 fill, 2850 cubes at max_z 9, no clipping | CARGO PASS 60×6; stack top 959 units, glass over the bed edge 1315.9 (clips at max_z 14: 1464) |
| trains on the ground | `lua_predeck_5002a49` | owner, build 3 smoke (`6123ae7`) | SYNTHETIC (b) FAIL dz −800 |
| interior slide, far-side jump, sideways into the legs | `lua_current_6123ae7` | owner (3b brief) | CHOREOGRAPHY: arrival on lines 1–4 is a 5966-unit instant teleport (`Station.lua:1105`, over 50 m), then 1143 slide; same-track departure teleports 3428 units to the far side, slides 4571 back; final approach into connectors 1–4 at 24.5° to the line; lines 5–6 clean (1143 slide, 0.0°) |

The 85 case is retrodicted as a **band with a FAIL**, not as the number 85: no simple tie-break
model reproduced 85 with radii 5 5 5 5 4 4 from the file's floats (seven tried: counts 61 to 89),
and fitting one would have been the failure this work exists to prevent. The verdict that matters
is that the instrument would have stopped that import.

## 2. Rules, derivations and independence

"Codex" is GPT-5.4 run non-interactively on copies of the named files with no hint of the answer.
"Sonnet" is a Sonnet subagent writing its own code from a description. The builder (Opus) is not a
derivation: its output was checked against this session's reference computation and the game.

| rule | derivation A | derivation B | status |
|---|---|---|---|
| R-MAP: Blender (x,y,z) m after the +30° turn → game (−y, −x, z)×100, det −1 | Codex: 25 spots, max residual 0.0002 units, from `build3_export_geometry.json` vs the entity | IMPORTER_FACTS, measured from the first import by another worker; in game the connectors read at radius 4 on all six axes | CONFIRMED |
| R-ANGLE: game angle = −(post-turn rot_z) = 330 − pre-turn rot_z; the Blender +X arrow lands at a − 90° | Codex: 25 spots, 1.2e-5° | the oracle's SPOTS check, and R-CARGO's 60/60 in game | CONFIRMED |
| R-CARGO: 12 columns at 116 along (cos a, sin a), 5 rows at 113 at +90°, layers 101 | SOURCE `20_TrainHub.lua` `GetCubePosRelative`, `Station.lua:99-100` | OBSERVED five cubes (fit script; the console read is not archived) and the owner's 60/60; Sonnet's own code gives 1/60 pre-fix, 60/60 now | CONFIRMED |
| R-LATTICE: pitch 1000, row 866 (integer), direction d at 60·d° counter-clockwise, HexRotate (q,r)→(−r,q+r) | SOURCE `_GameConst.lua:26-34`, `LuaDoc_hex` | MEASURED: hub y 166272 = 192×866; synthetic spots computed this way matched all 24 game reads to the unit | CONFIRMED |
| R-DECK: connector z 800 = the running surface | Blender DECK_Z, entity z 800 | OBSERVED `stub=10800:running=10800` ×6; slot 6 Enter1/Enter2 z 10800 | CONFIRMED |
| R-SYNTH: the Lua's synthetic spots (sevenths, opposite, deck lift, `hub_connector_directions`) | this session and Codex (blind), identical tables | MEASURED in game, 24 spots, zero delta | CONFIRMED |
| R-CHOREO: arrive → Ramparrive (teleport if > 50 m, else slide) → Stop; same track: teleport to Spawn, slide to Rampdepart, to the element; other track: Stop → Rampdepart_j → element; pass-through: one slide element to element; all slides straight | SOURCE `Station.lua:1085-1118`, `:1184-1207`, `Train.lua:507-519` | Codex blind on the same excerpts: same sequence; it surfaced the 50 m branch and the pass-through path this session had missed | CONFIRMED (source); the owner's three observations agree qualitatively |
| R-ELEMENT: the connector element sits on the connector hex; its Enter1/Enter2 are 289 units left and right of the track's centreline (HexSize/2 = 288.7), same z | SOURCE `TrainTransport.lua:116-150` | MEASURED slot 6: Enter midpoint = the hex centre on all six; lateral ±288.5…289, along 0.0…0.6 | CONFIRMED |
| R-FOOT: the centre rule is a lower bound on the game's reading and the touch union (any hex within 0.5 units of the shape) an upper bound; between them neither the file nor the covered area decides (§10) | this session, exact clipping: hub 61/30/91 and 66/0/66; large station 85 centres, 10 more covered 15.4 to 48.9 percent, union 95; FusionReactor 7 centres, 6 more covered 11.9 percent each, union 13 | run A, Sonnet (own code) on the hub: union 91 and vertex distances 577.35 / 519.615; run B, `gpt-5.6-sol` blind through Codex (own clipping code) on the two vanilla shapes: identical to four decimals | CONFIRMED as a band. The game read 85 (inside), 66 (single number), 95 (the top) and 7 (the bottom); no rule places a reading inside a band |
| R-STRUCT: the skeleton's constants describe the mesh | the oracle against `lookpass_workfile_geometry.json` (headless snapshot of the current work file): bays, ring radii, 12 ring pillars, 7 line pillars, all residual 0 | `verify_look_pass.py`'s proof (13 → 7 pillars) | CONFIRMED; beam width and train size UNCONFIRMED |
| R-TRAIN: the train's box is 4150 x 416 x 432 units (41.5 m long, 4.16 m wide), x -1332..2818, y -207..209, z 4..436 in its own frame, so not centred on its origin along its length | MEASURED slot 6, `train:GetEntityBBox()` on `TrainCCP3`: four reads at four positions and three headings, identical (`docs/archive/geometry_oracle_slot6_train_Mars.exe-20260919-23.34.07-6a91a190.log`) | file, width and height only: `TrainEngine` bbox 416 wide, 431 high (`entities_dat.py`); `TrainCCP3` carries no file bbox (the train is assembled at run time), so the length has the in-game read alone | CONFIRMED (§10); the oracle had assumed 10 m by 2.04 m |

## 3. Build 3b's geometry questions

- **Lane offset: 289 units (2.887 m, HexSize/2) either side of the track centreline**, Enter1 on
  the element's left (+90° from its angle), Enter2 on its right; the element's angle is the track's
  running direction (`GetTrackAngle`), so a train uses Enter1 when facing against that angle and
  Enter2 when facing with it: trains keep to the right of the centreline in their direction of
  travel. MEASURED slot 6 on all six elements. The vanilla element's bbox y of 204 is not the deck
  width; the spots lie outside it. The vanilla file gives the same ±289 (§9); the oracle's own LANE
  run, and why its paths do not yet use the offset, is §10.
- **Where a train goes today, per line and departure kind** (hub-local units, deck z 800; from
  the oracle's CHOREOGRAPHY, equal to this session's reference computation): lines 1–4: teleport
  5966 from the portal to a spot 2857 out on the wrong axis, slide 1143 to Stop at 1714; lines 5–6:
  slide 1143 to Ramparrive, slide 1143 to Stop. Same track: teleport 3428 to the far side, slide
  4571 through the centre, then to the element. Straight through: slide 4571 through the centre.
  Another line: slide 2490 (60°) or 4000 (120°) across open floor to Rampdepart_j, then to the
  element. Final approach into connectors 1–4 at 24.5°, into 5–6 at 0.0°.
- **Which paths cross the ring, the legs or the stacks:** every departure into connectors 1–4 and
  every stopping-path slide off a line crosses open floor; departure slides hit the ring wall band
  (3165–3560 units) on 28 of 36 (k, j) pairs and a loaded bed on 24 of 36; pass-through chords
  between adjacent lines (60°) pass at 3464 from the centre, inside the wall band, and between 120°
  lines at 2000, across a bed. Clearance rests on the UNCONFIRMED train size.
- **Can two trains meet:** 1391 of 1995 path pairs come within one train width (204 units)
  somewhere; a crossing lock is load-bearing until the spots are on their own lines, after which
  the oracle should be re-run to see what remains.
- **Vanilla StationBig's own layout** (slot 6, station local frame, angle removed): connector to
  Ramparrive 1926–2002 along the line, to Rampdepart 2976–3018, to Spawn 3497–3602, to Stop 4496;
  lateral offsets 216–409 units, Stop and Spawn on opposite sides. Outline 95 hexes; FusionReactor
  7; the track element 1.

## 4. Findings routed (faults, not edits; scope)

1. To 3b: correct `hub_connector_directions` for this body to `{4,1,3,0,2,5}`, or derive the
   synthetic line from the body's real connector hex; under either the oracle's SYNTHETIC (a)
   flips to PASS (selftest case 4). `CanBuildOver` (`20_TrainHub.lua:329`) also reads the table.
   The brief's hold block already carries the finding; the measurement now confirms it.
2. To 3b: the same-track Spawn is 3428 units from Stop (end state 2 makes it 0); the occupancy
   validation holds today because Stop_k coincides with Spawn_opposite(k) (0 units, all six).
3. To 3b: pass-through trains between adjacent lines cut through the ring wall band.
4. To the look pass: the beam width is a guess (`BEAM_W`); cube stacks clip the glass at max_z 14.
5. Slot 6 printed `pos=` empty for elements in the 23.01.18 log (`GetPos` on a `TrackGridElement`)
   and printed it on all four runs of the 23.34.07 log (`pos=278000,162808,10000`, the hex centre
   at ground z), same kit HEAD `bd32d30`, clean tree. The cause of the empty read is not known; the
   Enter midpoint supplies the position either way.

## 5. What only the game can still confirm

- Where inside its band the game reads a hex_shape, only if one ever has a partly covered or touched
  hex: dump `GetEntityOutlineShape` and compare with the band; the rule of thumb is never to need it.

## 6. Deviations from the sketch

- The seed's footprint rule (triangle centroid → hex) is not the game's; retired as a rule.
- The framing widened from Blender↔importer to code↔body: a table written for the intended
  layout, not the imported one. The oracle reads both sides and checks them against each other.
- The four console lines first offered were superseded by a selection-free TestKit slot
  (`tools/SMRTK.md`'s rule), which also logs itself on LoadGame when a hub exists, so an
  agent-launched run (owner ruling recorded in `tools/SMRTK.md`, `978768b`) needs no click; whether
  the kit can reach a placed hub unattended is untested.
- An Opus decode of vanilla `BinAssets.fpk:entities.dat` (spot names are readable strings) was
  still running at close; if `entities_dat.py` appears in `_shared/geometry/`, it is that agent's
  unjudged claim until its anchors (TrackPillarCCP3 bbox 1000×204, Enter1/2 at ±289, station radii
  5 6 5 4 4 4, FusionReactor 7) are checked.

## 7. Not claimed

Not "the hub's geometry is correct". Not the beam's right width, nor where inside its band the game
reads a partly covered hex_shape. The choreography numbers are predictions from measured spots
under source-read rules; no train movement was watched tonight. The five-cube observation behind R-CARGO has no
archived log.

## 8. Executed models

Fable 5.1 (this session, judge); Opus (oracle build; entity decode); Sonnet (blind footprint and
cargo check); GPT-5.4 via Codex (three blind derivations).

## 9. Addendum, late in run A: the vanilla entity table decoded

An Opus agent decoded `BinAssets.fpk:entities.dat` (`C:\Dev\SMR-Assets\_shared\geometry\entities_dat.py`,
SMR-Assets commit "entities_dat.py"). Judged by this session against anchors set before the decode:
`TrackPillarCCP3` bbox 1000 x 204, z -1726..1069 PASS; its `Enter1`/`Enter2` at (0, +-289, 800) PASS,
equal to slot 6's in-game read, so **R-LANE now has two derivations of different kind** (vanilla file,
in-game read) and is CONFIRMED at 289 units; `FusionReactor` 7 hex centres PASS. **R-FOOT:** the
large station's eight hex_shape triangles cover 85 hex centres, but the game read 95 tonight
(slot 6) with radii 5 6 5 4 4 4 (the dev mod's `line_radii()` log lines of 2026-09-18), so the centre
rule is a lower bound and the touch union an upper bound. Run A went further here and wrote that
the game includes partly covered hexes; run B's exact computation refutes that on the FusionReactor
and found the rasteriser behind it defective (§10). The hub's inset file has no partly covered hex
(nearest non-certain hex 49.999 units away), so every hub verdict above stands.
**R-TRAIN, one file derivation:** `TrainEngine` bbox 873 x 416 x 431
units, `TrainCar` 868 x 379 x 286; `TrainCCP3` (the Train class's entity) has no bbox of its own; the
in-game read is in §10. Not decoded: the mesh/skeleton blob, LOD distances.

## 10. Addendum, run B (2026-09-19, late): the footprint rule corrected, the lane run, the train measured

Run B is `GEOMETRY_ORACLE_B_high.md` (consumed by this addendum); its instrument changes are
SMR-Assets `015bc64`. Method as run A's: an Opus subagent built, this session judged, and the one
new derivation that a rule rests on was taken blind from another model family.

**R-FOOT is a band, and covered area does not settle it.** Run A's §9 concluded from the large
station that the game includes partly covered hexes. The FusionReactor refutes it. Exact polygon
clipping of each vanilla hex_shape against the lattice (file side read through `entities_dat.py`,
`entities.dat` sha256 `121afd89…9056`, 14,168,326 bytes, AssetsRevision 33006):

| entity | centres inside | partly covered, not centre | touch union | the game reads |
|---|---|---|---|---|
| `TrainStationLargeCCP3` | 85, radii 4 6 5 3 4 4 | 10, covered 15.4 to 48.9 percent | 95, radii 5 6 5 4 4 4 | 95 (slot 6), radii 5 6 5 4 4 4: all 10 in |
| `FusionReactor` | 7 | 6, covered 11.9 percent each | 13 | 7 (slot 6): none of the 6 in |
| hub, pre-inset | 61 | 30 touching at shared corners, area 0 | 91 | 85, radii 5 5 5 5 4 4 |
| hub, inset (current) | 66 | 0 | 66 | 66 |

Two derivations, identical to four decimals on both vanilla shapes: this session's reference
(Sutherland-Hodgman clip, scratch) and `gpt-5.6-sol` through Codex, blind (given only the
triangles and the lattice; it wrote its own clipping code). An area threshold between 11.9 and
15.4 percent would fit the two vanilla cases; it is two points with no source behind it and is
not adopted. Distance does not order them either: the station's thinnest included hex has its
centre 306 units from the shape, the reactor's excluded ones 232. The rule of thumb stands and is
now stronger: a hex_shape is predictable only when its band is a single number, which the hub's
is. Three corrections to run A's record follow from this: `hexcover.py` (the decode agent's area
rasteriser) had the two coefficients of its slanted hex edge swapped, so its "15 to 26 percent"
was wrong, and it returns 13 for the reactor at its own default threshold, which "7 by both rules"
had not checked; it is deleted, the oracle now clips exactly. The station's radii 5 6 5 4 4 4 are
not a slot 6 read (slot 6 gives only the count) but the dev mod's `line_radii()` log lines of
2026-09-18 (`Mars.exe-20260918-23.44.18-6a91a190.log` line 326, and two more logs). The oracle's
R-FOOT text, `corpus/EXPECTED.json` and `_shared/IMPORTER_FACTS.md` carry the corrected rule; the
corpus gains the two vanilla shapes as footprint-only cases (`entities_dat.py --hexshape` writes
the fixtures). MEASURED by this session on the builder's tree before commit: `python hub_oracle.py
--corpus` **24 of 24** (the 17 hub truths unchanged, 4 for the station, 3 for the reactor),
`--selftest` **6 of 6**; both fixtures regenerate byte-identical from `entities.dat`.

**R-TRAIN measured.** The owner put a train on the map and ran slot 6 four times
(`docs/archive/geometry_oracle_slot6_train_Mars.exe-20260919-23.34.07-6a91a190.log`, game 403908,
kit `bd32d30`): `train:GetEntityBBox()` on `TrainCCP3` read min (-1332, -207, 4), max
(2818, 209, 436) on every run, at four positions and headings of 240, 240, 60 and 180 degrees, so
the box is in the train's own frame: **4150 long, 416 wide, 432 high**, and it is not centred on
the train's origin along its length (1332 one way, 2818 the other). The file agrees on width and
height (`TrainEngine` 416 x 431); the length has the in-game read alone. The owner also took a
console read a few minutes earlier; no console read of the box appears in the night's logs, so it
is not among the evidence. The oracle's defaults were a guessed 10 m by 2.04 m and are now 41.5 by 4.16. Its sweep
still centres the rectangle on the path point, so along-path clearance carries up to 743 units of
error; lateral clearance and the two-train test depend on the width only. One verdict criterion
changed with it: the same-track teleport check compared the jump with the train's length, which at
41.5 m would have passed a 3428-unit jump the owner watched happen; it now fails anything over
1 guim, the scale `GetOccupyingTrain` validates Spawn at. Re-run on the current fixtures
(`current_5002a49.entjson`, `lua_current_6123ae7.lua`, the look-pass work-file snapshot, no
`--element-spots`): no verdict's status moves. TWO-TRAIN: 1395 of 1995 path pairs come within one
train width (416 units); the old guess (`--train-width-m 2.04 --train-length-m 10`) reproduces
§3's 1391, so the two are comparable. CLEARANCE: the swept train touches 37 of 40 obstacles and the
same 12 block it under both sizes (the six beds' cube stacks and six ring-wall sectors). The paths
cross so much open floor that the train's size barely changes the count; §3's answers stand, with
416 for 204.

**LANE run, and why the paths do not use the offset yet (the brief's stop).** The brief's command,
with `corpus/element_spots_measured_20260919.json` (`Enter1` (0, 289, 0), `Enter2` (0, -289, 0)):
LANE **PASS**, lateral offset 289.0 units for `Enter1` and for `Enter2` on all six connectors, the
third agreeing number beside the in-game read and the vanilla file. The magnitudes are all that
run may be used for. The oracle applies the offsets in each connector's outward frame and routes
every path through `Enter1`; the game does neither. MEASURED (slot 6, both logs): an element's
angle is the track's, shared by both ends of a line (elements 1 and 2 at 60 degrees, 3 and 4 at
180, 5 and 6 at 120), so `Enter1`, left of that angle, is on the left looking outward at
connectors 2, 3 and 5 and on the right at 1, 4 and 6. SOURCE (`Train.lua:665`, 1.1.0.403908): a
train takes `"Enter" .. ((step == 1) and "1" or "2")`, by its direction of travel along the track,
so an arrival and a departure at one connector use different spots. To carry the offset into
CHOREOGRAPHY, CLEARANCE and TWO-TRAIN the oracle needs the element-angle rule and the arrival or
departure spot choice, which is more than the JSON; that was this brief's stop, so the path model
is unchanged and the numbers those three verdicts print under `--element-spots` (1438 of 1995 in
this run) are not to be used. The fixture file carries the same warning. It falls to whoever next
runs the oracle for 3b's re-scope, after `hub_connector_directions` is corrected.

**Executed models, run B:** Fable 5.1 (this session, judge, reference computation); Opus (the
oracle build); `gpt-5.6-sol` through Codex v0.149.1 (one blind derivation). Run A's §2 and §8 name
its Codex model as GPT-5.4; run B did not check that, and records only its own.

## 11. Addendum, paths run (2026-09-20): the path model carries the lane side and the yaw; what 3b still has to solve

The paths run is `GEOMETRY_ORACLE_PATHS_high.md` (consumed by this addendum); its instrument
changes are SMR-Assets `66240ae`. Method as before: an Opus subagent built, this session judged
against its own reference computation (scratch, independent of the oracle's path code), and each
new rule took a blind second derivation from another model family. Every number below is a
**prediction** from measured spots under source-read rules; no train movement has been watched
since `6123ae7`. SOURCE lines are 1.1.0.403908, from `C:\Dev\SMR-SrcArchive\1.1.0.403908\Src\Lua`.

**The element-angle rule as the brief carried it is one scene's state; the invariant is the side of
travel (new rule R-LANESIDE, CONFIRMED).** SOURCE: a straight element's angle points along the
track toward its start end, `elements[1]` (`Buildings/TrackElement.lua:80-122`), and the start is
the end with the lower hex q, then the lower r (`Tracks.lua:626-631`), so at a hub connector the
angle is the outward heading or its reverse depending on where the track's far end lies on the map.
That is why slot 6 read 60, 60, 180, 180, 120, 120: each is its connector's axis, and the sign is
that scene's tracks. The spot choice flips with the same state: `step` is +1 travelling start to
end and the train takes `Enter1` on +1, `Enter2` on -1 (`Units/Train.lua:650,665`; the departure
side at `Buildings/Station.lua:1089-1091` and `:1200-1205`). The two flips cancel. The oracle now
computes the spot for both states at all twelve (connector, travel) pairs and checks they agree:
max distance 0.0 units, and all twelve lie **right of the train's own heading**. So each connector
has one ARRIVE spot and one DEPART spot, 578 units apart, whatever the map (hub-local units, z 800):

| connector (outward) | ARRIVE | DEPART |
|---|---|---|
| 1 (240°) | -1749.7, -3608.6 | -2250.3, -3319.6 |
| 2 (60°) | 1749.7, 3608.6 | 2250.3, 3319.6 |
| 3 (180°) | -4000.0, -289.0 | -4000.0, 289.0 |
| 4 (0°) | 4000.0, 289.0 | 4000.0, -289.0 |
| 5 (120°) | -2250.3, 3319.6 | -1749.7, 3608.6 |
| 6 (300°) | 2250.3, -3319.6 | 1749.7, -3608.6 |

These are the same twelve points slot 6 read as `enter1`/`enter2` on the six elements. Derivations:
this session's source reading; `gpt-5.6-sol` through Codex, blind on the excerpts alone, same
conclusion at every step (`docs/archive/geometry_oracle_paths_codex_lane_20260920.md`); and one
measured read, a train on open track at heading 180 standing 289 units to the right of its hex
centre (`docs/archive/geometry_oracle_slot6_train_Mars.exe-20260919-23.34.07-6a91a190.log`, the
fourth dump, train pos 161500,243635). Which spot *name* a train uses at a given connector stays
per-map state; code that needs the spot should ask the track (`step`), never hard-code a name.

**The train holds its arrival yaw through every station slide (new rule R-YAW, CONFIRMED from
source).** `Train:GotoSpot` moves with `SetPos` and sets no yaw, and `WaitChangeDir` with a nil yaw
keeps the current one (`Units/Train.lua:507-519`, `:470-476`); on the track the yaw is the travel
heading (`:579-583`). The one exception is the same-track departure, which takes the Spawn spot's
angle (`Buildings/Station.lua:1188-1193`). Derivations: this session and `gpt-5.6-sol` blind
(`docs/archive/geometry_oracle_paths_codex_yaw_20260920.md`), agreeing on every question; the
owner's "sideways into the legs" agrees in kind only, and no yaw was read in game during a slide.
With it the work list's item 4 landed rather than being dropped: CLEARANCE now sweeps the measured
box (x -1332 to 2818, so not centred) at the yaw the train holds, as the convex hull of the box at
a segment's two ends, and each segment reports its crab angle (yaw against heading).

**The instrument.** `--connector-directions 4,1,3,0,2,5` overrides the Lua's parsed table for one
run and edits nothing. MEASURED by this session on `66240ae`: `python hub_oracle.py --corpus`
**24 of 24**, `--selftest` **8 of 8** (new: swapping `Enter1`/`Enter2` flips only LANE's
right-of-travel check; the override makes SYNTHETIC (a) pass 12 of 12 where the parsed table passes
4). Without `--element-spots` the 66 paths are identical to `015bc64` (the builder's check against
a HEAD copy, its claim); CLEARANCE's sweep changed for every run, by design. The judge's reference
(`ref_paths.py`, scratch) and the oracle agree on the spots, the arrival and departure lengths and
angles, the chords, and TWO-TRAIN exactly (1291 as-is, 1224 under the corrected table). One flag is
stale and was left alone: R-ELEMENT is a static UNCONFIRMED in the oracle, so the three path
verdicts still print "rests on UNCONFIRMED: R-ELEMENT" under the measured fixture, although §2
holds it CONFIRMED.

**The deliverable: what the model predicts under `{4,1,3,0,2,5}`, and what build 3b still has to
solve.** Command, from `_shared/geometry/`: `python hub_oracle.py --entity
corpus/current_5002a49.entjson --lua corpus/lua_current_6123ae7.lua --workfile-snapshot
../../trainhub/blender/export/lookpass_workfile_geometry.json --element-spots
corpus/element_spots_measured_20260919.json --connector-directions 4,1,3,0,2,5`; the as-is column is
the same command without the last flag. Both exit 1.

| | as-is `{0,3,1,4,2,5}` | what-if `{4,1,3,0,2,5}` |
|---|---|---|
| SYNTHETIC | FAIL, 14 of 37: (a) off the real line by 120° on connectors 1-4, (c) on all six | FAIL, 6 of 37: only (c) on all six |
| arrival, element to Ramparrive | lines 1-4 teleport 5851.8 to 6091.7 (over 50 m); 5-6 slide 1178.8 | all six slide 1178.8 to 1179.1, no teleport |
| that slide's angle to its line | 21.9° to 27.0° on 1-4 (the teleport's own line), 14.2° (5-6) | 14.2° on all six |
| final approach into the departure element | 14.2° to 27.0° | 14.2° on all 36 |
| same-track teleport, Stop to Spawn | 3428.0 / 3429.1 | 3428.0 / 3429.1 |
| CHOREOGRAPHY | FAIL, 114 of 123 | FAIL, 114 of 127 |
| CLEARANCE, blocking obstacles | 12: six ring-wall sectors, six beds' cube stacks | the same 12; per sector 16 stopping and 14 pass-through paths, per bed 10 and 10 |
| TWO-TRAIN, pairs within 416 units | 1291 of 1995 | 1224 of 1995 |
| max crab angle: arrive / depart / pass-through | 120.0° / 180° / 60° | 14.2° / 180° / 60° |
| LANE | PASS | PASS |

What the corrected table clears: the four 50 m arrival teleports, the 120° misplacement of every
synthetic spot on connectors 1-4, and the approaches above 14.2°. What it leaves, in the order the
model says they bite:

1. **The lane dogleg (newly exposed).** The element spots sit 289 units right of the centreline
   and the hub's Ramparrive, Stop, Spawn and Rampdepart sit on it, so every arrival starts and
   every departure ends with a 1179-unit slide at 14.2° to its line, the train crabbing by the same
   angle. Vanilla's station offsets its ramps and stops laterally (216 to 409 units, §3). 3b wants
   the synthetic spots on the lanes, right of travel: arrival-side spots on the ARRIVE lane,
   departure-side spots on the DEPART lane.
2. **The same-track Spawn (§4 item 2, unchanged, and one thing worse).** Still a 3428-unit jump
   to the far side and a 4571-unit slide back through the centre. Newly exposed by R-YAW: the hub
   computes a Spawn spot's angle as centre-to-spot (`lua_current_6123ae7.lua:180-187`), and the
   spot is on the opposite connector's side, so the train faces 180° away from the connector it
   then leaves by and makes the whole departure backwards. Vanilla's Spawn spots face their own
   connector (slot 6: `van_Spawn1` at 0° with connector 1 to the east, `van_Spawn2` at 180° with
   connector 2 to the west). The occupancy coincidence of §4 item 2 still holds under the table.
3. **Departures to another line still cross open floor, sideways.** Stop to Rampdepart of a 60°
   line is 2491 units, of a 120° line 4000, across the floor, and the train holds its arrival yaw
   the whole way (crab 60° or 120°) until the track re-aims it past the element. These are the
   stopping paths that hit the ring wall and the cube stacks above. Nothing in the table touches
   this; it is the route-through-the-centre-with-a-turn that 3b's brief already names, and the
   turn has to set the yaw, because nothing in the game's station code will.
4. **The ring-wall pass-through (§4 item 3, unchanged).** A pass-through is one straight slide
   from the ARRIVE spot to the DEPART spot. Between adjacent lines it passes 3319.6 to 3608.6
   units from the centre, inside or grazing the wall band (3165 to 3560); between 120° lines
   1749.7 to 2250.3, across a bed; straight through it runs true, 289 off the centreline. All 14
   pass-throughs that touch a sector are blocked there, at a 60° crab.
5. **The crossing lock stays load-bearing.** 1224 of 1995 path pairs still come within a train
   width; the table moved 67 pairs. Re-run after the spots are on the lanes and the routes turn at
   the centre.
6. **A stopped train does not fit its half-line (new; the brief's second stop, for the owner
   through the orchestrator).** The measured box is 4150 long and a line is 4000 from centre to
   connector. At Stop (1714 out, yaw inward) the box runs from 3047 out to 1103 units *past the
   centre*; 15 of 15 pairs of stopped trains overlap, on any two lines. MEASURED by this session
   (scratch, the oracle's `box_corners_at` on the reference Stop positions). Moving Stop outward
   cannot cure it, since 4150 exceeds 4000 and 3b's stub platforms are shorter still. Trains have
   no collision, so this is a look and a capacity question, not a crash: either one stopped train
   at a time is the rule the occupancy model enforces, or the body grows, or the overlap is
   accepted. That is an asset-or-design call, not 3b's to make, and not this run's.

**What may now be used.** CHOREOGRAPHY, CLEARANCE and TWO-TRAIN under `--element-spots`, as
predictions, for both tables; §10's "not to be used" is lifted by `66240ae`. The ARRIVE and DEPART
spots above as the lane geometry. Not claimed: that trains behave, that the hub's geometry is
correct, or that the corrected table fixes 3b. The narrow claim: under the corrected table and the
measured lane rules the model predicts the table above, and it is unwatched. What only the game can
still settle here: a yaw read during a slide (slot 6 already prints the train's angle; run it
mid-departure), which would turn R-YAW from source-confirmed to measured.

**Executed models, paths run:** Fable 5.1 (`claude-fable-5-1`, this session: judge, source
reading, reference computation); Opus (the oracle build, requested through the Agent tool's model
override; the completion notice carries no model id); `gpt-5.6-sol` through Codex v0.149.1 (two
blind derivations, from the run headers).

## 12. Build 3b step-0 gate, 2026-09-20: redesign before implementation

**INFERRED verdict: the current asset, six independent radial stops and vanilla's connector
queue do not clear the owner's bar together.** Stop here under `TRAIN_HUB_TRAINS_high.md` item 0.
No mod Lua, TestKit slot or asset changed, including the optional table correction; no smoke ran.
The alternatives below are proposals, not owner rulings. The open-ring choice and outward-tail
preference stand. OI-22 holds the design call; build 4 remains behind build 3b's smoke.

### Reproduction and limits

**MEASURED computation, not observed movement:** pack `e671d77`, SMR-Assets `66240ae`, source
`C:\Dev\SMR-SrcArchive\1.1.0.403908\Src` (installed build `24995074`, fingerprint HOLDS from
`python tools/doccheck.py --emit-fingerprint`, run 2026-09-20). `git diff --stat 6019492..HEAD --
tools/devmods/train_hub/` was empty. The §11 WHAT-IF CLI reproduced its six remaining SYNTHETIC
failures and TWO-TRAIN 1224 conflicting + 771 clear = 1995 pairs; exact command, HEADs, hashed
inputs and selected results are in
[`baseline result`](../../archive/train_hub_gate_baseline_20260920.json). Exit 1 is the expected
failing baseline, not a candidate-build pass.

Run `python docs/archive/train_hub_gate_20260920.py` from this repo (RAN 2026-09-20). This
[`experiment`](../../archive/train_hub_gate_20260920.py) imports the **unchanged** oracle's
`box_corners_at`, `convex_hull`, `convex_separation` and snapshot transforms. It does not edit
the oracle or pretend the existing moving-path CLI supports new stop parameters. It brackets
each threshold, checks either side, verifies input revisions and records every compared pair.
The [`result`](../../archive/train_hub_gate_20260920.json) carries its command, HEADs and hashes.
Positive SAT gap means separate; zero means touching and is rejected. Axes 0..5 in this output
are angular order, not connector ids. Exact 60° axes are used; a later game build needs margin
for integer coordinate rounding. Thresholds are infima, not safe implementation positions.
All counts below come from the script's named subsets, with members in the result.

### Clearance and the actual envelope

**MEASURED prediction.** Let `s` be the inward-facing train's inner end measured outward from
the centre. Its origin is `s+2818`, its outer tail `s+4150`; the connector is at 4000. Thus tail
beyond connector = `s+150`. The asymmetric y box is retained.

| configuration | minimum s, units | Stop origin radius, units | tail beyond connector |
|---|---:|---:|---:|
| six, centreline | 359.689 | 3177.689 | 5.09689 m |
| six, ARRIVE lane +289 | 193.990 | 3011.990 | 3.43990 m |
| six, other lane -289 | 192.835 | 3010.835 | 3.42835 m |

The 60° pair governs. Old centreline Stop (`12000/7`) intersects on 15/15 pairs. The integer
ARRIVE example `s=195`, Stop 3013, tail 4345 yields 15 clear + 0 intersecting = 15 pairs at
3.45 m overhang. The other lane saves only about 1.15 cm and requires a 5.78 m lane change.

**MEASURED asset check.** The workfile's positive-X portal reaches x=45 m overall, but those far
parts are below the train. Complete mesh faces that can reach deck z=8 m end at **35.98681 m**:
579 selected faces, every face index and the spatial filter in the result. This tests complete
faces, so a long triangle cannot be missed between vertex slices. Tail at 43.43990 m is outside
that upper envelope by **7.45309 m**. The overall 45 m box therefore does not hide it. This is a
conservative outer-envelope measurement, not a render or proof of a watertight tunnel. A new
hood must clear train top z=12.36 m and the two-lane envelope of **9.96 m total width**, before
wall thickness/margins. Existing skeleton constants (2.6 m hood half-opening, 3.5 m beam width)
do not establish that clearance; the asset pass must measure actual openings and support.

### Vanilla parks inside; its queue does not fit the hub

**MEASURED prediction from OBSERVED spots.** Projecting vanilla Stop minus connector onto Stop's
inward yaw in the archived slot-6 train log (script input) gives **4496 units inward on each of
four platforms**, not outward. The stopped box occupies 3164..7314 inward from its arrival
connector. The paired connector positions are 7993 units apart along each row, so the train
fits between them. This settles parking direction, not the rendered wall boundary; vanilla
offers no evidence here that a visible train tail outside its body is normal presentation.

**SOURCE, 1.1.0.403908 archived tree:** `Lua/Units/Train.lua:645-672` traverses to the endpoint
element; `:371-390` calls `WaitForTrackInBuilding` afterwards; `:313-326` stops interpolation
and waits there until `CanEnter` permits entry. `:616-634` checks admission; `ShouldStopOnTrack`
does not choose a waiting point further out. `:550-587` moves to the next element's Enter spot
regardless of that flag's acceleration choice. The stable waiting origin is therefore the
connector ARRIVE spot, same lane and yaw as the stopped arrival. No queue animation was observed.

**MEASURED prediction:** the waiting nose reaches radius `4000-2818=1182`. Stopped tail reaches
4343.990: **31.61990 m overlap** on the same lane. Vanilla's waiting nose reaches 2818 inward
from its connector, versus parked near end 3164, leaving **3.46 m**. Stop-outward makes the hub
queue conflict worse. To clear it, the waiting origin must be **beyond radius 7161.990 units**,
over 31.61990 m outward of today's connector. Whole straight elements require **four extra
10 m intervals**, radius 80 m. This is a level, straight lower bound; short/curved/sloped
approaches need separate treatment.

`TrackBase:IsTrackFreeFor` (`Lua/Buildings/Track.lua:357-365`) limits a following same-direction
train on the track, but arrival removes the stopped train from that list
(`Lua/Buildings/Station.lua:1113-1117`). A following train can then reach the connector.
**INFERRED:** a hub-local occupancy override alone cannot move that waiter. Earlier stopping
or upstream reservation needs a design and contract review; neither was built, and this study
does not claim that a global `Train.lua` wrapper is necessary.

### Options costed before choosing

Numbers are **MEASURED predictions** from the experiment; costs and recommendations are
**INFERRED design assessments**, not tested behaviour.

| option | geometry left on the table | cost / disposition |
|---|---|---|
| Stop outward, centreline | 5.09689 m tail | Clears stopped pairs, fails the visual bar; queue remains a conflict. |
| ARRIVE lane; try the other lane | 3.43990 m; 3.42835 m | Visible tail. ARRIVE leaves 31.61990 m queue overlap. Wrong-lane parking saves about 1.15 cm while adding a lane crossing. |
| Stagger adjacent stops | alternating s=0 / 526.543 units gives tails 1.5 / 6.76543 m | Worse worst tail. Arbitrary staggering cannot improve the equal-radius maximum within own-half-line origin positions: each box contains a common inner rectangle already intersecting its neighbour below that bound. The script checks that subset witness; it does not claim this about arbitrary curved routes. |
| **Three alternating lines** (new) | s > -138.564 units; tail > **0.11436 m**; integer-margin example 0.13 m, 3/3 pairs clear | Attractive small-tail option. Only one alternating set admitted at a time; a train may wait with its own line empty. Nose enters the crossing about 1.39 m. Capacity and through-traffic policy change, and queue still must move. Owner decision. |
| **Opposite pair only** (new), or owner's one-stop fallback | s=-150: **zero tail**, inner end 1.5 m past centre; opposite pair 1/1 clear | Lower capacity; non-opposite through trains must wait for the crossing. Still **28.18 m queue overlap**, even with only one stopped train. Capacity lock alone is insufficient. |
| **Move stopping lanes farther sideways** (new) | zero tail at offset >8.84808 m, another 5.95808 m beyond ARRIVE; corridor half-width >10.93808 m | Leaves current beam/portal corridor. Needs real sidings, wider openings and turns; a Lua slide would recreate the rejected floating/crabbing. Asset redesign. |
| Extend portals into real tunnels | cover beyond 43.43990 m, >7.45309 m beyond measured upper envelope; includes 3.43990 m past connector | **Recommended asset basis for retaining six stops.** Widen/support both lanes, recheck hood joins, footprint and approach construction. Move queue or reserve upstream separately; hiding overlapping trains is insufficient. |
| Grow full body/connector radius to 50 m | contains stopped tail by 6.56010 m at unchanged Stop | +25% radial size, asset/footprint/track consequences. Queue overlap remains **21.61990 m** at that Stop. Enlargement alone fails. |
| **Extend only connector approaches to radius 80 m** (new) | four extra intervals meet straight-track waiting-origin bound >71.61990 m | Station-owned arms could move vanilla's waiter without growing the ring. Requires footprint/buildability/track-join redesign and existing-hub migration or rebuild. Parked tail still needs cover. |
| **Shorter train/consist** (new) | length <=38.06010 m at unchanged width/lane: >=8.28891% shorter | New train asset/consist or visible resizing on entry, attachment/animation and capacity work. Not a silent scale change to vanilla trains. Queue still needs fixing. |
| **Separate crossing decks vertically** (new) | >4.32 m deck separation for boxes alone, plus deck structure/margins | Major asset and slope/route redesign; separate levels can use centre space. Queue and transitions remain. Moving Lua spots above today's deck would float the trains. |

**INFERRED recommendation:** keep the open ring and redesign local tunnel/approach geometry if
six independent stops are essential. Specify parked and waiting envelopes together. If small
tail matters more than independent capacity, take the alternating-three option to the owner
before modelling, including through-traffic waits and the queue change. The one-stop fallback
remains available but is not sufficient alone. There is no measured basis here to call 3.44 m
unnoticeable; whether 11.44 cm is acceptable is the owner's visual judgement. No option was
chosen on their behalf.

### Another constraint for the eventual reverse

**MEASURED prediction:** a 180° flip at the *same origin* shifts the radial box endpoints by
**14.86 m** because the box is asymmetric. At the six-stop ARRIVE threshold the reversed box
would overhang **18.29990 m**, not 3.43990 m. Preserving its longitudinal envelope requires the
new outward-facing origin **14.86 m inward**. Switching to DEPART also moves it **5.78 m
sideways**. These are envelope predictions, not animation observations. `Spawn=Stop` alone
does not establish an invisible reverse: the redesign needs a turning route or concealed
origin/lane transfer. This qualifies item 2's proposed mechanism while preserving the owner's
desired reverse-in-place appearance.

**End state:** gate failed under the current combined constraints; OI-22, then revise the held
build brief. Retain that brief until its smoke-recorded lifecycle condition is met. Executed
model: GPT-6 (Codex), as identified by this session's instructions; the transcript provides no
more specific runtime model id. No subagents were used.

## 13. Owner correction, 2026-09-20: R-TRAIN is DISPUTED and the §12 gate verdict is set aside

**The owner measured a train against the game's own hex grid** — a build cursor superimposed to make
the grid show, in and out of the hub — and read **about two hexes, ~20 m, with three hexes of
comfortable margin** (owner, 2026-09-20, from in-game screenshots). §10's 4150 units / 41.5 m
disagrees by roughly a factor of two. **Where they disagree, the hex measurement governs**: a 10 m
hex is an unambiguous ruler and needs no interpretation.

**Why the 41.5 m is suspect, not merely outvoted.** It came from `train:GetEntityBBox()`. `Train` is
an `AutoAttachObject` (`Train.lua:16`) and `TrainCCP3` has **no mesh of its own** — `mesh_bbox` is
null in `entities.dat` (decoded 2026-09-20 via `entities_dat.py` on the pack-extracted file; the
same decode returns `TrainStationLargeCCP3` at 89.94 x 90.95 m, which confirms 100 units = 1 m, so
this is not a scale error). The call was therefore made on an assembly, and what it spanned is not
established: it may cover auto-attached parts or the 42-cube cargo grid (`max_x = 7, max_y = 3,
max_z = 2`, `Train.lua:31-33`). §10 recorded the weakness at the time — the file agreed on width and
height, and *the length had the in-game read alone* — and the reading of it as "a whole train" was
an interpretation that later work treated as settled. The owner also confirmed (2026-09-20) that a
passenger does **not** spawn an extra car, so whatever the length is, it is fixed.

**Consequences.** R-TRAIN is **DISPUTED**; the oracle's `--train-length-m` default rests on it, and
every clearance, CLEARANCE-sweep and stopped-train figure derived from it inherits the doubt
(TWO-TRAIN's width-only results do not). **§12's gate verdict is set aside** — its method was sound
and its arithmetic reproduces, but its input is in doubt, so its "redesign before implementation"
conclusion is not to be acted on. **OI-22 is withdrawn** from the owner's list, where the gate run had filed it.

**The resolution, owner 2026-09-20: park position is a tunable in our own Lua.** Stop, Spawn and the
ramps are synthetic spots this mod computes (`synthetic_spot_pos`, `kind_sevenths`), so where a
train parks is a number we own and tune by eye — *"easier than resizing the mesh, building a tunnel
onto the mesh, or runtime scaling the train"*. The alternatives costed earlier in the day (runtime
`SetScale`, three alternating lines, a new tunnel hood, `FOOTPRINT_R = 5` with the connectors at
50 m, resizing the dome to the footprint edge) are **withdrawn**, all having been generated
downstream of the disputed figure. Build 3b carries the tunable and owes the clean measurement:
a hex-grid read of a stopped train, and the engine's own bbox plus each auto-attached part read
separately rather than the assembly's.

