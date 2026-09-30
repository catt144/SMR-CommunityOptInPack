# Elevator Depot — approved shell, verified import and sitting (brief 25)

Brief: [25_ELEVATOR_STATION_LOOK_high.md](../prompts/Train_Hub_Project/25_ELEVATOR_STATION_LOOK_high.md).
Previous builds and the original owner record: [20260929 report §7](ELEVATOR_DEPOT_LOOK_20260929.md#7-the-owners-concept-restated-with-pictures-2026-09-30-orchestrator).

## Owner authority, recorded before the model changes

Verbatim from the owner's record in the previous report:

> "Ok this is the concept I send in that I wanted basically a shrunk tunnel in one of the coreners
> of the elevator and blended in to look natural and clean. 2nd screenshot is what I got back. So I
> reexplained it and my frustrations. And the 3rd is what I got back the next time. The arrow I
> drew on it is where i want the tunnel."

> "I am fine creating our own custom one, but the quailty of the train hub is the bar for a custom
> module. I am fine with using vanillas tunnel if it works, or slightly cleaned up and updated
> looks. But it also needs to look right. With the shrunk elevator the tunnel is bigger that the
> elevator. We need to blend whatever design we are doing so that it sits high enough for the
> train to go into it, and tappers down towards the groun to make it look like the train is going
> under the elevator in its storage hold to offload and then up and back out."

The three reference images were inspected. The arrow reads as the gap between the front pads,
at the foot of the central ring. This is an interpretation, not another owner ruling.
The bare sand and frame inside the elevator core remain deferred: owner, "this is minor we can
save it for another design pass" (brief 25).

## Start and live work list

The candidate pass began at the commits below; the approval continuation began at OptInPack
`6327ccd` / Assets `7f087ce`, with build 25390750 still GREEN and the game closed.

`git log --oneline -3` / `git rev-parse HEAD`: OptInPack `de9ac7c`, Assets `ac0233a`.
`git pull --ff-only`: OptInPack up to date; Assets has no upstream or remote configured
(`git remote -v` empty). The pre-existing untracked trainhub Blender backups are outside this work.
`python tools/doccheck.py --emit-fingerprint`: installed build **25390750**, GREEN.
`tasklist /FI "IMAGENAME eq Mars.exe"`: game closed at start.

No todo tool is exposed in this session; this is the live list, one commit-and-verify unit per item.

- [x] Candidate, independent export check, renders and departure study: Assets `7f087ce`.
- [x] First report, OI-33 and brief/map handoff: OptInPack `6327ccd`; doccheck GREEN.
- [x] OI-33: owner replied **"approved"**, 2026-09-30, to the rendered shape and placement.
- [x] Record approval and prepare the vanilla spot layout with a conditional sampled clearance check.
- [x] Accepted shell, builder/verifier and renders checkpoint: Assets `172e992`; synchronized dev Lua and this handoff in the OptInPack commit.
- [x] Owner replied **"done"** after import/save; imported entity and metadata audit PASS (receipt below).
- [x] Owner carried the brief to hotfix build 25579348; relevant source fingerprints unchanged; OI-34 resolved.
- [x] Import receipt, source archive and bounded startup repairs verified; checkpoint with this handoff.
- [ ] ck221 surface/train/underground sitting; final in-game acceptance remains open.

## Movement evidence

SOURCE, archived `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src`, build **25390750**;
line numbers read with `rg -n -A 50 -B 5 'function Station:TrainArrive|function Station:TrainDepart'
.../Lua/Buildings/Station.lua` and the corresponding `Train:WaitChangeDir` / `Train:GotoSpot` reads:

- `Station.lua:1105-1114`: the 50 m teleport test is horizontal distance. Arrival slides first to
  Ramparrive and then Stop; both calls request final pitch zero.
- `Train.lua:507-518`: GotoSpot reads the full spot position and interpolates to it. With a final
  pitch argument, it derives an intermediate pitch from the destination.
- `Train.lua:470-503`: that intermediate pitch returns to final pitch over the movement.
- `Station.lua:1184-1205`: reversal sets Spawn position and yaw. The first departure GotoSpot
  call, to Rampdepart, supplies no final pitch; the second, to the connector, supplies zero.

INFERRED: below-grade Stop/Spawn positions can request vertical translation through vanilla
movement, but that alone does not demonstrate a train following a descending rail. Departure's
first leg retains its existing pitch. Roof, ground and rail clearance need the full train's swept
volume, including its off-centre origin. This candidate is not a claim of a working descent.

## First render pass: candidate and renders

The new body is an arched mouth with a descending, panelled roof, recessed navy fascia, thin blue
edge, service louvres and a grounded skirt. The elevator turns 90° so the portal occupies the gap
between pads. The shell ends at the outside of the core ring; it does not cover the cabin well.
The existing body swatch atlas is reused. In this first pass, the imported tube, Lua, material source and
live ScenePath were left intact; `git diff --exit-code -- tools/devmods/elevator_station` was empty.

[Concept/candidate review sheet](B:/Dev/SMR/SMR-Assets/elevatorstation/blender/review_descent/index.html)
contains the unchanged owner reference beside the new render, with additional mouth/top views.

![Candidate from the concept side](B:/Dev/SMR/SMR-Assets/elevatorstation/blender/review_descent/concept.png)

![Mouth and base join](B:/Dev/SMR/SMR-Assets/elevatorstation/blender/review_descent/mouth.png)

**Render limit:** the portal is the actual exported candidate mesh. The elevator and approach
track are dimensioned, render-only reference proxies; they are not vanilla's detailed mesh.
The exact art join, in-game lighting and quality acceptance remain the owner's sitting. The
proxy retains the visible ground in the core; it makes no claim to have fixed the deferred core.

## First render pass: measured at the desk

Commands ran in `SMR-Assets/elevatorstation/blender/`, Blender 5.2.2 LTS. Artifacts name Assets
`ac0233a` plus source hashes and identify the FBX as
`05a821fecc1675e4baf662fa31cd310ca53e8ba06096e27fa5c6721b78664808`.

```text
blender --background --factory-startup --python-exit-code 1 --python depot_candidate.py
blender --background --factory-startup --python-exit-code 1 --python verify_depot_candidate.py
blender --background ElevatorDepot_candidate.blend --python-exit-code 1 --python depot_candidate_render.py -- concept mouth top
blender --background --factory-startup --python-exit-code 1 --python study_depot_departure.py
```

`export/candidate_descent/proof.json` holds the build; `verify.json` the independent FBX read;
`departure_study.json` the bounded motion study. `review_descent/render_manifest.json` identifies
the render inputs and cameras. Generated FBX and import-source Lua remain rebuildable local
artifacts. The proofs, blend, render images and scripts are committed in Assets.

| reading | command/filter | measured result |
|---|---|---|
| shell dimensions | candidate build, named shell constants before rim/skirt | 14.3 m wide; 21.5 m long; crown 15.8 → 5.7 m; x −35 → −13.5 m |
| full mesh bounds | build, all exported body vertices, beam included | x −36.4..0.032 m; y ±8.605 m; z −17.47..15.8 m |
| footprint | build, centre membership in turned elevator or portal rectangle, plus connector; independent verifier uses half-planes | **23**, reconciled as 20 elevator + 2 portal + 1 connector; identical member sets in both JSON files |
| spots | verifier, exact names and full position/angle table below | **14**; 0.00000954-unit worst position error; pairing holds in 3D |
| footprint face inset | verifier, every corner | minimum 57.7349 units |
| mouth headroom | verifier, upward rays at y −544, −335, −126, 126, 335, 544 and x −3540, train roof z 1236 | minimum 118.046 units (1.18046 m) |
| body/UV import | verifier, visible body excluding named surfaces | one mesh and material; no UV outside the unit square or zero-area face |

Candidate spot table, game units, **not imported**:

| spot | position | angle |
|---|---|---:|
| Trackconnector1 | (−4000, 0, 800) | 180 |
| Trackdirection1 | (−5000, 0, 800) | 180 |
| Trackconnector2 | (1000, 0, 800) | 180 |
| Trackdirection2 | (0, 0, 800) | 180 |
| Ramparrive1 | (−3300, −335, 800) | 180 |
| Stop1, Spawn2 | (0, −335, −1800) | 0 |
| Spawn1, Stop2 | (0, 335, −1800) | 180 |
| Rampdepart1 | (−3300, 335, 800) | 180 |
| Ramparrive2 | (900, 335, −1800) | 180 |
| Rampdepart2 | (800, −335, −1800) | 0 |
| Sign1 | (−4000, 0, 0) | 0 |
| Sign2 | (1000, 0, 0) | 180 |

The table groups the coincident Stop/Spawn pairs; its names reconcile to the verifier's exact set.

## First spot proposal: departure hold (superseded by the prepared revision)

[Cross-section](B:/Dev/SMR/SMR-Assets/elevatorstation/blender/review_descent/departure_clearance.svg).
The study casts downward rays onto the exported roof at the departing lane, every 10 game units,
and places a horizontal train bounding envelope at the exported Rampdepart1 pose. This is the
pose vanilla's first departure leg reaches without a requested pitch change.

| envelope assumption | x at that pose | roof exceedance | samples beyond roof |
|---|---|---|---|
| previously reported, disputed box, local x −1332..2818 | −6118..−1968 | up to 501.133 units (5.01 m) | 76, x −2720..−1970 in steps of 10 |
| owner's approximately 20 m length, **centred origin assumed** | −4300..−2300 | up to 289.391 units (2.89 m) | 43, x −2720..−2300 in steps of 10 |

Both use the earlier measured vertical bound z 4..436 relative to the train origin. A bbox may
contain empty space: this is a conservative clearance failure, not observed mesh clipping. It
rejects these spots as proven-ready; it does not prove the whole concept impossible. Stop 1's
live refusal/clipping/sticking condition was not tested, and stop 2 was not established for every
possible vanilla layout. The build match clears stop 3.

This led to the revised vanilla layout below: the first departure leg stays below grade, and the
second leg supplies the ascent. The historical failed proposal remains evidence about those
spots. The prepared revision has a conditional sampled clearance result, not a successful game run.

## Owner decision and continuation

**OI-33 ruled, 2026-09-30:** the owner replied **"approved"** to the candidate's rendered shape and
placement. The approved source is Assets `7f087ce`, shown in `review_descent/concept.png` and the
comparison sheet above. This clears brief 25's render-before-import gate for that shape. It is
not final in-game acceptance or a successful train run. The checklist item is removed with this
ruling; the approval is not asked for again.

After that decision, the approved shell was promoted into the live builder, with revised spots,
beam and footprint. The dev Lua now uses the same spot table and a 90° elevator turn. The
prepared FBX and import source were ready at this checkpoint; the completed import is recorded below.

## Prepared revision: what changed and what passed

Assets **`172e992`** contains the prepared source and evidence. Commands ran with Blender 5.2.2
LTS on input HEAD `7f087ce` plus the identified source hashes, against build **25390750**:

```text
blender --background --factory-startup --python-exit-code 1 --python depot_build.py
blender --background --factory-startup --python-exit-code 1 --python verify_depot.py
blender --background --factory-startup --python-exit-code 1 --python study_depot_motion.py
blender --background ElevatorDepot_work.blend --python-exit-code 1 --python depot_candidate_render.py -- concept mouth
```

The prepared FBX SHA-256 is
`7203729241a1fb0d26f53447972b94b2b2544f7cb72cda6fba81496335c82b6f`.
Build, independent FBX verification and the sampled study are respectively
`export/depot_proof.json`, `export/verify_depot.json` and `export/depot_motion.json`.
The verifier compares against the **tracked approved blend** at `7f087ce`, checking its Git
blob `7f18718ec196d06cf878f4bbbd16f79a9f4a8883` before comparing geometry. It does not need an
untracked historical FBX to reproduce this comparison.

| reading | executed command/filter | result |
|---|---|---|
| approved exterior | verifier, face-coordinate/UV multisets after the explicitly permitted sill/beam exclusions | **7,758 faces preserved**, including skirt, seams, fascia, panels and mouth; the prepared body's **7,798 = 7,758 + 40 beam faces**; the approved snapshot's 6 raised-sill faces are removed |
| footprint | builder centre membership; independent verifier half-plane membership | **24 = 20 elevator + 2 portal + 1 approach + 1 connector**; complete member sets agree in both JSON files |
| connector/route | verifier, exact spot literals and footprint membership | outward connector inside, direction outside; buried end remains inaccessible; Stop/Spawn pairs coincide in full 3D |
| spots and dev Lua | verifier, exact named spot set, positions, angles, Lua diagnostic table and ScenePath | **14 names**, reconciled to the table below; worst position error **0.00000954 units**; synchronized |
| aperture and import | verifier, same mouth rays as the first pass, UVs and surface normals | minimum static headroom **118.046 units**; raised sill absent; UV and upward-surface checks pass |
| arrival, sampled owner-length model | motion study, above-grade envelope points beneath the exported shell | minimum sampled roof margin **57.123 units**; no sampled soil crossing outside the mouth or above-grade extension beyond the rear |
| departure, same assumptions | motion study, below-grade reposition then pitching ascent | minimum sampled roof margin **367.828 units**; same sampled ground/rear checks clear |
| arrival teleport branch | motion study, exported arrival-to-connector XY distance with element lane 289 | **1,400.756 units**, below the source's 5,000-unit threshold |

The spot names below reconcile to the verifier's exact set; grouped rows contain coincident pairs.
Positions are game units and angles are degrees.

| spot | prepared position | angle |
|---|---|---:|
| Trackconnector1 | (−5000, 0, 800) | 180 |
| Trackdirection1 | (−6000, 0, 800) | 180 |
| Trackconnector2 | (1000, 0, 800) | 180 |
| Trackdirection2 | (0, 0, 800) | 180 |
| Ramparrive1 | (−3600, −335, 800) | 180 |
| Stop1, Spawn2 | (−500, −335, −1400) | 0 |
| Spawn1, Stop2 | (−500, 335, −1400) | 180 |
| Rampdepart1 | (0, 335, −1400) | 180 |
| Ramparrive2 | (900, 335, −1400) | 180 |
| Rampdepart2 | (800, −335, −1400) | 0 |
| Sign1 | (−5000, 0, 0) | 0 |
| Sign2 | (1000, 0, 0) | 180 |

The connector moved one hex outward; the approach beam bridges from the native element to the
mouth, and the internal beam descends. Arrival starts level. The Stop/Spawn positions and first
departure leg are below grade; the second departure leg requests the vanilla pitch interpolation.
The shell dimensions, 75% elevator scale and 90° placement match the approved render.
`depot_geometry.py` holds helpers extracted from the old builder, allowing the approved
candidate and prepared builder to share geometry without an import side effect or circular import.

**Authority and limits of the movement check.** The owner's approximately two-hex/20 m
measurement governs, as recorded in [GEOMETRY_ORACLE_20260919.md §13](GEOMETRY_ORACLE_20260919.md).
The disputed assembled 41.5 m bbox is retained only as sensitivity data in the JSON; it fails
parts of this model and does not reinstate the owner's withdrawn length gate or authorize
rescaling the train.

The study assumes a centred rigid 20 m box, z 4..436, y ±209, fixed ±335 lanes and flat terrain.
It uses continuous constant-acceleration position and the source's triangular pitch. The first
arrival call returns at half its time, hence 7/12 of its distance in this model, before the Stop
leg replaces it. Sampling is recorded as 81 time points per full leg, 41 longitudinal positions,
two vertical edges and the three positive-lane roof rays 126/335/544; the shell is symmetric.
These are sampling parameters, not a claim of continuous collision detection.

Native time steps, GetPitchYaw/SetPos semantics, the actual origin/mesh, lateral/yaw interpolation,
wheel/beam fit and visual rail following remain unmeasured. No train has run, and **no custom
train movement was added**. This check supports an attended import trial; it does not establish
D3 or close brief 25. A live refusal, teleport, clip or stuck train triggers the brief's stop.

[Prepared concept view](B:/Dev/SMR/SMR-Assets/elevatorstation/blender/review_prepared/concept.png) ·
[Prepared mouth view](B:/Dev/SMR/SMR-Assets/elevatorstation/blender/review_prepared/mouth.png).
Both were rendered and inspected; the portal is the prepared mesh, and the elevator/approach
remain explicitly dimensioned proxies. `review_prepared/render_manifest.json` identifies their
blend/FBX inputs. The original approved render, blend and proof files remain unchanged.

## Import receipt and hotfix continuation, 2026-09-30

Owner replied **"done"** to the existing-entity import/save batch. Input checkpoint: OptInPack
`457ab7f`, Assets `172e992`. This completes the import and generated-file check, not a live
placement, train run or final look acceptance.

`python tools/doccheck.py --emit-fingerprint` reads installed Steam build
**25579348**, and both latest main executable logs identify **1.1.1.406343**. The saved metadata
also records revision 406343. The prior stop 3 named 25390750, prompting OI-34's build question.
The owner replied:

> "There should be no issues, this is a minor hotfix specifically targeted only at linux systems. No game content changed"

That reply carries the brief forward to **25579348**; OI-34 is resolved and removed. The checker
below compares **6 source files** against both archives and the installed ModTools tree:
`Lua/Buildings/Station.lua`, `Lua/Units/Train.lua`, `Lua/Tracks.lua`,
`Lua/Buildings/TrackElement.lua`, `Lua/Buildings/SpaceElevator.lua` and
`CommonLua/Editor/ArtSpecEditor.lua`. All hashes match, with members and hashes in `result.json`.
The existing source/motion evidence retains its original build; unchanged source fingerprints
carry the relevant code findings forward. The next action is the fresh surface placement.

`python docs/agent/reports/elevator_depot_import_20260930/archive_source.py` copied and verified
the newly observed version at `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/`.
[Archive receipt](elevator_depot_import_20260930/archive_receipt.json): **4,719 files**, all files
recursively under `Src`, reconciled against the sorted `MANIFEST.sha256`; installed tree and
copy match. Tree digest: `d753f949af92e2b753f44163a2e47229e371f810ef3c2752d30a98953af2663c`.
`Get-FileHash -Algorithm SHA256 -LiteralPath 'B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.405907/MANIFEST.sha256'`
returns that same digest for the prior manifest. Input OptInPack HEAD for these commands is `457ab7f`.

Read-only command:

```text
python docs/agent/reports/elevator_depot_import_20260930/check.py
```

[Result and member sets](elevator_depot_import_20260930/result.json) ·
[Log excerpts with source hashes and line numbers](elevator_depot_import_20260930/log_excerpt.txt).
The checker measures the installed build from the Steam manifest, compares the imported
`.entjson` against the prepared export proof and records the source fingerprints. It does not
load the game; runtime behavior remains for the owner's sitting.

| imported reading | command/filter | result |
|---|---|---|
| named spots | checker, exact attaches vs prepared proof; complete members in result JSON | **14**, all positions/angles match within 0.01 game units; worst error **3.67394e−13**; Stop/Spawn pairs coincide |
| footprint | checker, independently map imported triangle centroids to the hex lattice; compare member sets | **24 = 20 elevator + 2 portal + 1 approach + 1 connector**; direction outside, buried end inside |
| surfaces | checker, imported surface type counts and per-cell membership | **142 = 96 hex + 23 collision + 23 selection**; **96 = 24 × 4** hex triangles; agrees with the editor's 142 |
| body import | checker, linked mesh/material files, FBX hash and imported bbox vs prepared proof | expected files present; maximum bbox error **0.000263184 units** |
| metadata code list | checker, exact names plus file existence | **3**: `10_ElevatorDepotDev.lua`, `_EntityData.generated.lua`, `BuildingTemplate/SMROptInElevatorDepotDev.generated.lua`; none dropped |
| generated code/template/spec at import receipt | `git diff --exit-code -- tools/devmods/elevator_station/{Code,Data,items.lua,SourceData/ArtSpec-mod.lua}` (paths expanded in PowerShell, before the guard below) | unchanged from the checkpoint by the editor save |

Entity SHA-256: `5e2e49efe214542b7e5c5df982e45261245bf45d483eca015faafa4e8ab35984`.
Compiled mesh SHA-256: `7739a4cb20f560b3311e90d5c09086334c44d5448cad4a127f78f7ca68f5a2d4`.
Editor log `MarsDebug.exe-20260930-10.58.36-6aba6e9d.log` lines 315–330 identifies the depot,
successful mesh/material export, spots/surfaces and **Importing Mesh Done**. The normal log
`Mars.exe-20260930-10.54.44-6aba6e65.log` predates the import; both are captured by the excerpt
generator. `tasklist` for both `Mars.exe` and `MarsDebug.exe` found no running process during
this read.

### Startup findings, separate from the completed mesh import

- **Opt-In startup syntax defect, repaired:** editor log line 198 reports failure to load the
  main mod's `items.lua`; its locals identify line 91, an unescaped apostrophe in the
  ServiceInterestTags Help string (`building's`). The existing source at input HEAD `457ab7f`
  reproduces the same error with `python tools/parsecheck.py --dir .`. Escaping that apostrophe
  restores parsing without changing the displayed sentence, option names or intended behavior.
  The same command then passes; the dev `Code/` parse check passes too. This is a syntax repair,
  not a current-build Station compatibility claim. A clean game startup after it remains unrun.
- **Existing EntitySpec startup path, guarded for the depot:** the normal log's
  `ArtSpecEditor.lua:573 / EntitySpecPathToEntity` error names `SMROptInElevatorDepot`.
  [D14(e)](../bugs/D14.md) already records this path and the hub's scoped guard; that guard covers
  the hub's specs. The depot now installs the same narrow pattern at `ClassesPostprocess`: skip
  its own EntitySpec's editor post-load only when the helper is missing, otherwise delegate to
  the prior method. Its generated ArtSpec has no legacy color properties. Source:
  `CommonLua/Editor/ArtSpecEditor.lua:565–573`, archived **1.1.1.406343 / build 25579348**; hash above.
  `python docs/agent/reports/elevator_depot_import_20260930/guard_smoke.py` runs the actual depot
  Lua and existing hub guard in both installation orders. [Results](elevator_depot_import_20260930/guard_smoke.json)
  pass own/hub skipping without the helper, unrelated-spec delegation, editor delegation with
  arguments/returns, reinstall and helper transitions. These are stubbed Lua checks; normal-game
  startup with the imported entity still needs observation. Generated ArtSpec remains unchanged.

The editor rewrote its generated import source by removing the builder comment and restoring
its usual trailing blank line. It is preserved as editor output. `git diff --check` reports
that one generated EOF blank-line warning; the hand-edited files pass their scoped check.
No generated source was manually normalized.

## Next sitting: first surface batch

The shared-game owner action is **ck221** in the fix pack's `docs/PLAYTEST_CHECKLIST.md`, homed in
`docs/agent/reports/OPTIN_ELEVATOR_DEPOT_LOOK_20260930.md` there. The approval does not need repeating.

The owner completed the existing EntitySpec `SMROptInElevatorDepot` → mesh → Open in Importer
→ Import → save flow, using `export/SMROptInElevatorDepot.fbx` and material
`SMROptInElevatorStation`. The generated-file audit is complete; no repeat import is needed.

1. Restart, load the normal game and place a **fresh** depot at least 100 m from another station.
   The connector/footprint moved, so an old placed depot is not the connection fixture.
2. Look at the surface join by day and watch the cabin descend; check its sound.
3. Run `SMRElevatorDepotDev.Report()`, then flush the log and report what needs moving.

The next batch is the vanilla train test with slot 6's existing stream, then underground
`Measure()` / `Report()` and the lowest-pitch, fully-zoomed-out rope view.

`tasklist /FI "IMAGENAME eq Mars.exe"` found the game closed immediately before the dev Lua edit.
`python tools/parsecheck.py --dir tools/devmods/elevator_station/Code` passed.
The agent did not launch the game; the owner's import logs supply the receipt above.
No post-repair startup, train run, cabin/sound verification or ceiling measurement occurred.
The underground rope remains the prior unmeasured 300 m default. Cabin timing, cargo wiring,
drone crew, twin placement, vanilla elevator, hub and rail-shaft code/art, and deferred core
sand/frame were not changed.

## Close-out routing

| finding/block | evidence and home | next action | disposition |
|---|---|---|---|
| owner concept and arrow | verbatim authority above; original report §7 and reference images | execute approved shape | OI-33 ruled "approved" |
| approved shell/import | Assets `172e992`, imported entity and receipt above | ck221 sitting | owner import and disk audit complete; live acceptance open |
| movement | source and conditional `depot_motion.json` above | ck221 vanilla train batch | sampled model clear; actual native behavior open |
| imported entity/Lua | import receipt matches prepared spots, footprint and metadata | fresh placement | imported and synchronized |
| hotfix build | owner ruling, fingerprint 25579348 and source hashes above | run on the new target | OI-34 resolved; source archived |
| surface/cabin/train/underground sitting | brief 25 done-condition and ck221 | next surface batch above | all live checks still owed |
| main-mod startup quote | editor log and root parse fail→pass above | verify next startup | repaired in this import-receipt commit |
| depot EntitySpec startup error | normal log, D14(e), guard smoke results above | verify next normal startup | depot-scoped guard added; stubbed checks pass |
| core sand/frame and cargo wiring | owner deferral above; prior station report §6 | later design/wiring pass | preserved, untouched |

Executed agent: **Codex, GPT-6 family as identified by the session instructions**. The exact
serving-model identifier and effort are not exposed in this transcript; no subagents were used.
`PROBE SWEEP: clean` from `rg -n 'TEMPORARY' Code/ tools/devmods/elevator_station/Code/ ../SMR-BugFixPack-TestKit/Code/` (exit 1,
the explicit wrapper reported clean). Python compilation and `git diff --check` passed for the
Assets changes. `python tools/doccheck.py` ran GREEN on 2026-09-30 with these documentation edits.

| repository | commit | scope |
|---|---|---|
| SMR-Assets | `7f087ce` | candidate generator/workfile, independent FBX proof, renders/review sheet, departure study and pipeline README |
| OptInPack | `6327ccd` | first report, OI-33, brief 25 handoff and its map row |
| SMR-Assets | `172e992` | approved shell promotion, revised vanilla route, independent verification and prepared renders |
| OptInPack | `457ab7f` | OI-33 ruled, dev Lua synchronized, import source regenerated, report and brief/map |
| Fix pack | `3fdee71` | ck221 shared-game owner import and attended sitting, with a local report pointer; pushed |
| SMR-Assets | `05fc97e` | completed import receipt, hotfix continuation and next surface placement in pipeline/review docs |
| Fix pack | `0bf8700` | ck221 import step complete, owner hotfix ruling and fresh surface batch; pushed |

First-pass handoff byte measurement at `6327ccd`, both by `len(Path(...).read_bytes())`: brief 25 was **17,567 → 18,801
bytes** (+1,234). The removed stale request to repeat owner feedback is homed in the verbatim
authority above and the prior report §7. Imported-entity evidence, model/import continuation and
the full sitting remain linked in the brief; no open obligation was dropped. The pre-existing
untracked trainhub backups remain untouched.

Historical approval-continuation verification at `457ab7f`: `python tools/doccheck.py` GREEN in both documentation repos;
the final `--emit-fingerprint` run still reads installed build **25390750**. The dev metadata
still lists `10_ElevatorDepotDev.lua`, `_EntityData.generated.lua` and the generated depot template
(`rg -n` for those exact paths); recheck after the editor save. Brief 25 measures **18,801 →
19,789 bytes** (+988), by `len(git show 6327ccd:<brief>)` versus `len(Path(<brief>).read_bytes())`.
The superseded tube constants/footprint and pending render decision became the prepared source
map, ruled approval and ck221 sitting; historical evidence remains in the first-pass sections.

Import-continuation verification on input OptInPack `457ab7f`: import/source audit PASS, root
and dev Lua parsing PASS, guard smoke PASS, documentation checks GREEN in both repos, and the
hand-edited diff checks pass. The editor-generated EOF warning is recorded above. Brief 25
measures **19,789 → 20,339 bytes** (+550), by
`len(git show 457ab7f:<brief>)` versus `len(Path(<brief>).read_bytes())`.
The pending-import block is replaced by its verified receipt; the prior build target is replaced
by the owner's recorded hotfix continuation. Both superseded obligations are traced to the
import/continuation section above: **2/2**, with **0 unhomed content dropped**. The sitting and
its original acceptance conditions remain live. No unresolved filing remains within this pass.

This receipt commit includes the imported entity/mesh, editor metadata/import item, startup
repairs and proof files. Unrelated fix-pack prompt-map/casebook work and the untracked Assets
trainhub Blender backups remain outside it. The new source archive is local and outside git,
as its README specifies. The remaining task work is ck221's attended game sitting.

## Sitting 2026-09-30, orchestrator-guided (log `Mars.exe-20260930-12.23.04-6aba6e65.log`)

Fixture: the owner's new save **double hub+elev** (the double hub build plus a vanilla elevator
and a ready track at its underground half). Build 25579348.

**Batch 1, surface and underground look — PASS as a test model.** Owner: *"both ends build,
sounds seem right. animation works."* `Report()` read two depots, all 14 spots on each MATCH
the design at 0 cm, surface connector 1 carrying a `TrackGridElement`; no Lua error.
Screenshots: `SMR-Assets/elevatorstation/owner_feedback/sitting_20260930_underground.png`,
`sitting_20260930_range_off_centre.png`.

**Findings, routed to the wiring brief, not defects of the look:**
- Trains: on Balanced with zero stock the depot got deliveries only while the hub was filling its
  other stations, then none; **after the owner let it run a while it began balancing and now gets
  trains regularly** (owner). So the hub does serve a station chained behind another; the early
  gap is not diagnosed (queue order or the Balanced target settling). Not a blocker.
- No drones (the depot's crew is wiring work).
- The underground depot's panel shows no import/export/balanced controls.
- ~~Service-range ring off-centre~~ **Resolved, not a defect:** the ring is the vanilla elevator's drone service
  area, shown in white because the selected depot lies inside it (vanilla range display); selecting the
  elevator shows the same ring in blue. The depot has no service area of its own yet (no crew).
- Owner: *"when we get to multiple, design tweaks are needed"* — for the next design pass; the
  tweaks are not yet named.

**Batch 2, the train — PASS as a test model.** Slot 6 streamed 191 ticks of a train on the depot's
line (`7985-7873`), 12 of them `at_station=true` at the depot (surface, id 7985). The visual
of the train at the mouth is **design feedback, deferred by the owner** to the design-pass list.

**Batch 3, underground — PASS; the rope is accepted as is.** `Measure()` on the underground map:
vanilla `ElevatorUnderground` shaft top 12,861 cm over its base; the nearest cliffs top at
13,896 cm; our `SpaceElevatorRope` x8 runs 0..22,500 cm, top 50,254 cm (`rope_underground_m`
300, unchanged). Owner: *"the cable looks about as good as i think it can, it goes very high up;
only when you are zoomed out to the whole sector view does it look a little odd but I think that
is about as good as we can expect. When you are at max normal view it looks very clean."*
Screenshot `owner_feedback/sitting_20260930_rope_underground.png`. The ceiling itself was not read as
a height (no ceiling object in the sweep); the rope's top is what matters and it is accepted.

**Batch 4, brief 22's smoke — NOT RUN, deferred by the owner.** Its slot 4 needs a Mod Editor save
of `SMR_TrainHubDev` made after `81efabf` (2026-09-29 14:28); the generated template on disk
dates from 12:54 that day and the owner's later editor save was of the Elevator Depot mod, not
the hub's. Owner, 2026-09-30: *"we will move onto the next redesign. If we are going through the
full editor and import, design should just be folded into it"*: the hub mod's editor save and
brief 22's five steps run in the next design pass's editor-and-import session.

**Sitting result:** the depot is a working test model on both maps (look, cabin, sound, rope,
trains). Next: the design pass, from the owner's list.
