# Drones chain L2R — under-deck exit

Owner ruling, 2026-09-22: leave and re-enter beneath the deck, never through a train portal;
no train awareness, lane guard or arbitration. Travel directly above the track centreline,
above passing trains, then descend to the element to work. The flight mechanism, graph walk,
console API and save-start teardown remain L2's. No native flight was run here.

## Route and defaults

`30_TrainHubDrones.lua` preserves OI-25: offset floor → offset rim → local z +1000.
Because this brief explicitly retains that crest, it then lowers in the same clear column to
the under-deck cruise, exits toward the generator's 30-degree gap, and climbs outside the
footprint. This extra rise/lower is a deliberate interpretation of the retained OI-25 point;
the subsequent outward flight is entirely under the deck. L3 must judge its appearance.

Native-scale entity-local waypoints (engine units; live spots supply the column):

| point | x | y | z |
|---|---:|---:|---:|
| floor | −1310 | −397.35 | −2000 |
| rim | −1310 | −397.35 | 30 |
| OI-25 crest | −1310 | −397.35 | 1000 |
| under-deck cruise | −1310 | −397.35 | 300 |
| outside | −7794 | −4500 | 300 |
| outside climb top | −7794 | −4500 | 2500 |

Then transfer horizontally at the greater of local +2500 and the first rail's cruise altitude,
lower vertically to its cruise point, and keep L2's ordered track/tunnel path. The final point
is the target's visual origin + `FixHeight`. Work happens there. Return reverses every segment,
including climbing from fix height before the track ride and landing on the pit floor.
Early recall reverses only the flown prefix. `PitPoints` retains its original first three
indices and adds the under-deck/outside/high points; `Create` still hovers at index 3 until sent.

All tuneable defaults are guesses for L3 except OI-25's retained column and crest:
`UnderDeckHeight=300`, `OutwardDistance=9000`, `ClimbRate=1500`, `TransferHeight=2500`,
`OverTrackHeight=1200`, `HoverHeight=300`, `FixHeight=100`, `Speed=6000`,
`LaunchTime=3000`, `LandingTime=3000`, `WorkTime=5000`.
Heights/distances are engine units; rates units/game second; times game milliseconds.
`SetHubDroneTune` accepts these names after the console drone is removed.

**Train-height basis: stated guess.** `OverTrackHeight` is an assumed 12 m train envelope
above rail origin, with the existing `HoverHeight` serving as a 3 m buffer: total ride offset
15 m. No train dimension was measured or inferred from the withdrawn length. L3 owes a train
passing directly beneath the hovering Wasp, judged by eye; also check tunnel concealment and
arches at this higher offset. These are not train-clearance guarantees.

## Measured static envelope

Command, run from this repo (no assets are saved):

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b 'B:/Dev/SMR/SMR-Assets/trainhub/blender/TrainHub_work.blend' --python-exit-code 1 --python 'B:/Dev/SMR/SMR-OptInPack/tools/devmods/train_hub/tests/exit_clearance.py'
```

The committed `tools/devmods/train_hub/tests/exit_clearance_receipt.json` carries command,
HEAD, input hashes, exact waypoint coordinates, member triangle counts and the worst triangle
at each leg. Final inventory: **147 objects, 40302 triangles, 17 legs**, reconciled by
`sum(object_triangles.values()) == triangle_total` and `len(legs) == leg_count`; object
counts use the script's mesh/curve filter and explicit exclusion set. The source geometry includes evaluated ribs and optional siding panels; the
explicit exclusions are metadata surfaces, the guide and unexported dome glass. A circumscribed
polygon encloses L1's level-Wasp cylinder, radius `hypot(1.38,1.08)` m, z +0.24…+1.83 m.
Triangle/prism separating-axis tests cover the whole segment, not sampled points. Reported
margins are conservative separating-plane lower bounds on distance, not closest-point distances.
Intersecting/separated synthetic triangles exercise both outcomes. Any overlapping triangle
or a blend hash change during the run fails the command.

L1's Wasp input was checked once: `tools/flpk_extract.py` decoded the installed
`A:/SteamLibrary/steamapps/common/Project Spark/Packs/BinAssets.fpk` into scratch;
`hashlib.sha256(entities.dat)` matched L1's
`121afd89292532238c194f0a6f74c1eceaaa1e47ed369c6b8d355dd642019056`.
The installed manifest still reads build **24995074**, game **1.1.0.403908**.

| swept leg / obstacle family | minimum bound, m | location |
|---|---:|---|
| floor/rim, including floor | 0.240000 | PitFloor_1; intentional landing separation |
| rim/crest and crest/cruise | 0.347332 | Siding_1 edge beside the retained column |
| under-deck / deck underside | 1.970000 | Track_B |
| under-deck / centre pillars | 3.288301 | Pillar_4 |
| under-deck / ring pillars | 3.712918 | RingPillar_4 |
| under-deck / cargo beds | 2.140000 | Bay_1 |
| under-deck / ring and clamps | 0.792286 | RingClamp_1, worst outward margin |
| outside climb / all geometry | 37.995904 | Platform_6 |
| outside climb / hoods | 59.304747 | Hood_1 |
| outside climb / portal pieces | 57.258361 | PortalThroat_1 |
| high transfer to a connector | 6.011501 | Rib_2 on Trackconnector2 transfer |

This measures the native-scale source mesh and a level, unladen Wasp. It does not certify the
imported renderer, cargo stacks, other runtime attachments (including the crown light), terrain,
banking, other drones, moving trains, station/tunnel geometry elsewhere or scaled hubs.
L3 records the worst live margin and location, checks the complete route and work pose, then
settles constants. A new geometry hash requires another measurement.

## Verification and drift

`python tools/devmods/train_hub/tests/flight_smoke.py` passes at base HEAD `0e9ec05`, flight
source SHA256 `8edffe9cefed4e919bc6471d9dab848d8b40e0cd6e4ad241f67bea14785bc2b9`.
Actual Lua runs under mocked engine objects. Checks cover the low-before-outside-climb order,
high transfer, centreline rail sequence, fix-height work, vertical-rate limit, rotated/scaled
waypoints, full reverse route, under-deck recall, and L2's lifecycle/tunnel checks.
`python tools/doccheck.py` is GREEN; metadata also passes a Lua `load` parse.
The fixture reports arrival **10981**, work end **16981**, removal **27962** game ms;
**13 created = 13 removed**, reconciled over all fixture creations/removals. No native behavior
or clearance verdict follows from this smoke.

| finding / departure | evidence | home and next action | disposition |
|---|---|---|---|
| OI-25 crest and low exit both retained | Brief's explicit +1000 requirement | Spec §10 and L3 notes; judge extra rise/lower | Implemented |
| Flight registration disappeared | First smoke failed; `git show d48871e -- tools/devmods/train_hub/metadata.lua` removes the entry | Restored the single metadata line; L3 checks next import | Necessary scope extension; no importer-survival claim |
| Shared source mesh moved between measurement runs | Different blend hashes and triangle inventories | Receipt pins the final run; rerun if its hash changes | Re-measured, no art edits |
| Initial read mistakes | Nonexistent skill placeholder; escaped prompt path; PowerShell wildcard path guesses | This report / L6 notes | Read-only failures, resolved |
| Retirement wording | Brief says strike; prompt-map gate rejects tombstones | Remove spent file and row together | Follow existing chain/map convention |
| Native tests still owed | No game driven in this link | L3 notes: train pass, full route, work pose, import, save behavior | Open attended work |

Work list was stated before writes in commentary; no todo tool was available. The hub
implementation file was never opened. Assets were read only; no art, geometry, dispatch,
economy or persisted state was edited. Primary executed model from transcript: **GPT-6**;
no subagents.
