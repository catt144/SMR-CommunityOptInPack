# Drones chain L1 — pit geometry

Read-only survey, 2026-09-22. No files edited, no commits, no game probe.

**Recommendation — INFERRED from the measurements below:** launch and return at the pit floor, offset from both pit spots by **entity-local `point(-310, 180, 0)` engine units**. At hub scale 100, this moves the origin 3.58469 m within the pit and puts the Wasp beneath a clear vertical opening. Keep the drone level during the scripted lift/descent. The geometric STOP condition does **not** apply.

## Revisions and evidence boundary

**MEASURED:** opening and closing `git rev-parse HEAD` returned:

- OptInPack: `d8a5ca8bdf598fb60e205e01bc7a61f654e5b53d`.
- SMR-Assets: `a38c8dab72b171c7dd4e260d7027e86b33133cff`.

**MEASURED:** `Get-FileHash -Algorithm SHA256` returned the following. The work blend, skeleton, exporter, imported entity and hub Lua were hashed near the beginning and again at close; none moved. The preparation script was also checked twice without change.

| File | SHA256 |
|---|---|
| Assets `trainhub/blender/TrainHub_work.blend` | `4F69CB374F73CD99AF4D5CBF22583A8C582B37AF7BAD754D2C01382BCB7B0D29` |
| Assets `trainhub/blender/hub_skeleton.py` | `2C2AC0BB4D97222B56EC544E2087505B0747B1552F0CB5EAF2443FCCEAB86EF7` |
| Assets `trainhub/blender/prepare_concept.py` | `B5CC9BF801D5BA24DD3F830C2AA996CA1D4368F6A5F615C953C70FF932ED0A10` |
| Assets `trainhub/blender/export_prep.py` | `AA175376BEB51DBE4DB6EF824CF282F156DD2D9FBEA8AE008FB11041960C8CD7` |
| OptIn `tools/devmods/train_hub/Entities/SMROptInTrainHub6.entjson` | `225B2166601530944A6509FE06C3AFFDD4CB5CFEADCDEE623EB3F220A3F88BE1` |
| OptIn `tools/devmods/train_hub/Code/20_TrainHub.lua` | `96CC89E2E5F3BB63F5AB04ABEB353855BEB01C80B0512446382F982F0A263781` |

**MEASURED, closing hashes:** body mesh `Meshes/SMROptInTrainHub6_mesh.sub_0.hgrm` was `A5D3708DBE5CE3841E97DE9E69713E9CE3A007A90E24970AD93335AB86216F2E`; archived `1.1.0.403908/Src/Lua/Units/FlyingDrone.lua` was `ACA5A4B1930B869A2350934A8D407DF99D6D9F2FCDABCB0E5EB1873076BDE25E`.

The Assets worktree was already dirty. Its dirty set expanded to include `validate_structure.py` during the read. The measured geometry inputs above remained unchanged.

## Spots, transforms and dimensions

**MEASURED:** imported entity `SMROptInTrainHub6.entjson:48–56` contains:

| Spot | Entity-local engine units |
|---|---|
| `Pitfloor` | `(-999.999634, -577.349792, -2000)` |
| `Pitrim` | `(-999.999634, -577.349792, 30.000002)` |

**MEASURED:** Blender `matrix_world` positions are `(9.999995, 5.773500, -20)` m and `(9.999995, 5.773500, 0.30)` m respectively.

**SOURCE:** `prepare_concept.py:128,214–216` applies a 30° preparation turn. **INFERRED and checked against the named connector/spot coordinate pairs:** the complete generator-to-import transform, including importer axes, is:

```text
entity_x / 100 = -0.5 * generator_x - sqrt(3)/2 * generator_y
entity_y / 100 = -sqrt(3)/2 * generator_x + 0.5 * generator_y
entity_z / 100 = generator_z
```

**INFERRED world positions:** for an upright hub with origin `H`, yaw `θ`, scale factor `s = GetScale()/100`:

```text
world(Pitfloor) = H + s * RotateZ(θ, (-999.999634, -577.349792, -2000))
world(Pitrim)   = H + s * RotateZ(θ, (-999.999634, -577.349792,    30))
```

These are derived world positions, not observations of a particular placed hub. Use the engine’s actual spot positions in code; do not hard-code a colony coordinate or assume its terrain height.

**MEASURED from work-blend vertices; SOURCE constants at `hub_skeleton.py:272–320`, construction at `:1530–1592`:**

| Feature | Metres in generator coordinates |
|---|---:|
| Mouth radius / diameter | 5.75 / 11.50 |
| Mouth’s 48-sided inscribed radius | 5.737689 |
| Pit floor top / underside | −20.00 / −20.40 |
| Plate top and `Pitrim` height | +0.30 |
| Floor-to-`Pitrim` rise | 20.30 |
| Kerb inner / outer radius | 5.75 / 6.35 |
| Kerb top | +0.60 |
| Posts’ top | +1.90 |
| Terrain-hole radius / height | 6.05 / 0.00 |
| Recessed shaft bands’ outer radius | 6.00 |

`Pitrim` is at the mouth centre at plate height, **not on top of the kerb**.

## What roofs the mouth

**SOURCE:** the original 73.6% calculation in `build_pit_candidates.py:211–237` excludes `Glass` and operates on mesh objects. Current export preparation also excludes the dome `Glass`, but converts curve objects to meshes first (`prepare_concept.py:30–31,202–220`). The six ribs therefore belong in a complete structural obstruction check.

**SOURCE:** `SidingPanel_*` becomes a separate optional glass entity, not part of the body. `20_TrainHub.lua:1069–1093` attaches it only if `IsValidEntity("SMROptInTrainHub6Glass")` succeeds.

**MEASURED:** `rg --files tools/devmods/train_hub | rg -i 'glass|entjson|hgrm'` found the body entity/mesh and no glass entity/mesh. That establishes the checked-in devmod inventory; it does not establish what an installed editor copy has loaded.

**MEASURED:** current raycasts used integer-grid samples `ix,iy ∈ [-20,20]`, filter `ix²+iy² <= 400`, mouth offsets `5.75*(ix,iy)/20`, origin height 0.61 m, upward distance 60 m:

| Geometry filter | Blocked / total | Reconciled first-hit members | Unblocked |
|---|---:|---|---:|
| Deck comparison, including optional panels; mesh-only | 925 / 1,257 = **73.5879%** | `Track_A` 133 + `Track_B` 118 + `Siding_1` 142 + `SidingPanel_1` 532 | 332 |
| Body plus optional panels, including evaluated ribs | 963 / 1,257 = **76.6110%** | Previous 925 + `Rib_1` 38 | 294 |
| Body-only export geometry, including evaluated ribs | 538 / 1,257 = **42.8003%** | `Track_A` 133 + `Track_B` 118 + `Siding_1` 142 + `Rib_1` 139 + `RibBand_2` 6 | 719 |

The historical “about 74%” remains a reasonable **deck-plus-panels** figure. It is neither the whole structural roof nor a direct measurement of the installed runtime attachments.

**MEASURED:** the lowest deck underside over the sampled mouth is z 6.80 m: 6.20 m above the kerb top, 6.50 m above `Pitrim`, and 26.80 m above the pit floor. At the exact pit centre, the optional siding panel’s underside is z 7.745 m.

**INFERRED:** the centre permits a scripted floor-to-rim lift, but a continuing vertical flight there encounters the panel when present and higher structure thereafter. The proposed offset avoids both body structure and optional siding panels.

## Wasp envelope and the recommended column

**SOURCE, game build 1.1.0.403908, archived tree:** `Lua/Units/FlyingDrone.lua:11–48` declares `FlyingDrone`, entity `DroneJapanFlying`, collision radius 120, default hover height `7*guim`, minimum hover height `1*guim`; `:115` selects `"fly"`. `:181–201` lands against map height, so vanilla landing is not a pit-floor descent.

**MEASURED:** the installed `Packs/BinAssets.fpk` was decoded in memory through `tools/flpk_extract.py:parse_table` and its ZSTD wrapper. Decompressed `entities.dat` SHA256:

```text
121afd89292532238c194f0a6f74c1eceaaa1e47ed369c6b8d355dd642019056
```

The `DroneJapanFlying` `"fly"` and `"idle"` records both decode to:

```text
bbox min = (-87, -108, 24)
bbox max = (138, 108, 183)    engine units
duration = 3333 ms
```

The box scan required matching centre, positive extents, and matching encoded X/Y sizes; calibration recovered the documented `ElevatorSurfaceDoor` and `WayPointBig` boxes. Installed Steam manifest build ID was `24995074`; the inspected game log reports `1.1.0.403908`.

**INFERRED conservative visual envelope:** at native scale, level pitch/roll, any yaw, the box fits inside a vertical cylinder of radius `sqrt(1.38²+1.08²) = 1.752370 m`, extending 0.24–1.83 m above the entity origin.

**MEASURED:** adding entity-local `(-310,+180,0)` to the spots gives generator XY:

```text
(9.991150, 9.358179) metres
```

At this column:

| Clearance | Result |
|---|---:|
| Offset from shaft centre | 3.584690 m |
| Distance to nearest projected overhead triangle | 2.108179 m |
| Conservative distance to shaft boundary | 2.152999 m |
| Margin after Wasp visual radius, overhead | **0.355809 m** |
| Margin after Wasp visual radius, shaft | **0.400629 m** |

**MEASURED:** the nearest overhead projection is the siding edge at generator y 7.25 m. The vertical centre ray found no obstruction through the complete evaluated body plus optional panels. A separate sampled swept-box check cast **13,248 rays = 24 yaw angles × 24 X samples × 23 Y samples**, with **0 blocked**, against the mesh-only conservative set. Evaluating all six ribs afterward preserved the continuous projected-distance margins and the clear central column.

**INFERRED prototype waypoints, native hub scale:**

```text
Spawn/return origin: entity-local (-1309.999634, -397.349792, -2000)
Mouth waypoint:      entity-local (-1309.999634, -397.349792,    30)
Above-deck waypoint: entity-local (-1309.999634, -397.349792,  1000)
```

Use world `Pitfloor`/`Pitrim` plus the rotated, scale-adjusted offset. The proposed above-deck waypoint is z +10 m relative to the hub, or `Pitrim` +9.70 m. Ascend and descend in that same column under script control; hand over after clearing the deck. The ±3.58 m offset is within the existing pit and requires no geometry change.

This establishes a static, level Wasp launch column. Banking, carried resources, moving trains, simultaneous drones, arbitrary runtime attachments and the onward flight route remain prototype/smoke concerns. Recheck this measurement if dome glass is introduced or any fingerprinted geometry moves.

## Owner decision and routing

**SOURCE authority already recorded:** spec §9 at `TRAIN_LOGISTICS_DESIGN_20260917.md:1914–1920` accepts the hangar beneath the deck. The chain README separately leaves the floor launch/return ruling open.

**Recommended exact ask:**

> Approve launching and returning at the pit floor, using the same offset column `(-310,+180,0)` from `Pitfloor` and `Pitrim` in entity-local engine units? It clears the current shaft and deck, including the optional siding panels, by at least 0.35 m around a level vanilla Wasp. The prototype will script the rise/descent through that column and begin onward flight above the deck.

Route that ruling to this mod’s `docs/PLAYTEST_CHECKLIST.md`; record the answer in link 2’s upstream notes and spec §10. No geometry STOP is warranted.

## Measurement commands and QA drift

Measurements ran with:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' `
  -b 'B:/Dev/SMR/SMR-Assets/trainhub/blender/TrainHub_work.blend' `
  --python-expr $measure
```

The inline read used transformed vertex positions and `mathutils.bvhtree.BVHTree.FromPolygons`; export curves were converted only in the unsaved process. It excluded metadata surfaces, the guide, the unexported dome, and floor/pit geometry from overhead tests. The continuous clearance test projected nondegenerate overhead triangles onto XY and compared nearest-triangle distance with the Wasp radius; shaft clearance used the 48-gon apothem. Assertions required an empty vertical-hit list and margins greater than 0.30 m.

**QA drift to preserve:** an early diagnostic included unexported dome glass and found complete roof coverage; the export filter disproved its applicability. An initial mesh-only read omitted exported curve ribs; evaluating those changed complete coverage to 76.6110% while preserving the recommended column. Floating-point mouth-boundary filtering initially changed sample membership; final reported coverage uses the explicit integer mask above.

Executed model: **GPT-6**, as stated by the active transcript instructions.
