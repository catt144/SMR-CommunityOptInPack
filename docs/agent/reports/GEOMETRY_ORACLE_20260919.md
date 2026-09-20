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
(`corpus/`, truths and log lines in `EXPECTED.json`): **17 of 17 truths reproduced**.
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
| R-FOOT: a hex whose centre is inside the hex_shape union is in; a hex only touched within 0.5 units at its boundary is undetermined by the file | this session: 61/30/91 and 66/0/66 | Sonnet (own code): union 91 and vertex distances 577.35 / 519.615; its strict-interior "certain" count was wrong for a reason it diagnosed itself (the fan diagonal through the hex centre), which the oracle's inclusive test avoids | CONFIRMED as stated; the game's tie-break is not modelled |
| R-STRUCT: the skeleton's constants describe the mesh | the oracle against `lookpass_workfile_geometry.json` (headless snapshot of the current work file): bays, ring radii, 12 ring pillars, 7 line pillars, all residual 0 | `verify_look_pass.py`'s proof (13 → 7 pillars) | CONFIRMED; beam width and train size UNCONFIRMED |
| R-TRAIN: the train's size | none (no train in tonight's colony; `train=nil`) | — | UNCONFIRMED: `print(GetEntityBBox("TrainCCP3"))` (`Train.lua:38`) |

## 3. Build 3b's geometry questions

- **Lane offset: 289 units (2.887 m, HexSize/2) either side of the track centreline**, Enter1 on
  the element's left (+90° from its angle), Enter2 on its right; the element's angle is the track's
  running direction (`GetTrackAngle`), so a train uses Enter1 when facing against that angle and
  Enter2 when facing with it: trains keep to the right of the centreline in their direction of
  travel. MEASURED slot 6 on all six elements. The vanilla element's bbox y of 204 is not the deck
  width; the spots lie outside it. A second, vanilla-file derivation waits on the `entities.dat`
  decode (below).
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
5. Slot 6 prints `pos=` empty for elements (`GetPos` on a `TrackGridElement`); the Enter
   midpoint supplies it. Fix when the slot is next touched.

## 5. What only the game can still confirm

- `print(GetEntityBBox("TrainCCP3"))` with any train present (or slot 6 with a train on the map).
- The hex tie-break, only if a hex_shape ever needs boundary vertices: dump
  `GetEntityOutlineShape` and compare with the band; the rule of thumb is never to need it.

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

Not "the hub's geometry is correct". Not the train's size, the beam's right width, nor the game's
corner tie-break. The choreography numbers are predictions from measured spots under source-read
rules; no train movement was watched tonight. The five-cube observation behind R-CARGO has no
archived log.

## 8. Executed models

Fable 5.1 (this session, judge); Opus (oracle build; entity decode); Sonnet (blind footprint and
cargo check); GPT-5.4 via Codex (three blind derivations).
