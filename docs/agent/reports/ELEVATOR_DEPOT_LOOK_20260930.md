# Elevator Depot — descending portal candidate (brief 25)

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

`git log --oneline -3` / `git rev-parse HEAD`: OptInPack `de9ac7c`, Assets `ac0233a`.
`git pull --ff-only`: OptInPack up to date; Assets has no upstream or remote configured
(`git remote -v` empty). The pre-existing untracked trainhub Blender backups are outside this work.
`python tools/doccheck.py --emit-fingerprint`: installed build **25390750**, GREEN.
`tasklist /FI "IMAGENAME eq Mars.exe"`: game closed at start.

No todo tool is exposed in this session; this is the live list, one commit-and-verify unit per item.

- [x] Candidate, independent export check, renders and departure study: Assets `7f087ce`.
- [x] Report, OI-33 and brief/map handoff: this commit; doccheck GREEN.
- [ ] **Next owner action:** OI-33, keep the rendered shape or name changes.
- [ ] After the owner keeps a shape: finish the vanilla movement layout/clearance, synchronize the dev layout, checkpoint, import once, then run the surface/train/underground sitting.

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

## Candidate and renders

The new body is an arched mouth with a descending, panelled roof, recessed navy fascia, thin blue
edge, service louvres and a grounded skirt. The elevator turns 90° so the portal occupies the gap
between pads. The shell ends at the outside of the core ring; it does not cover the cabin well.
The existing body swatch atlas is reused. The current imported tube, Lua, material source and
live ScenePath were left intact; `git diff --exit-code -- tools/devmods/elevator_station` was empty.

[Concept/candidate review sheet](B:/Dev/SMR/SMR-Assets/elevatorstation/blender/review_descent/index.html)
contains the unchanged owner reference beside the new render, with additional mouth/top views.

![Candidate from the concept side](B:/Dev/SMR/SMR-Assets/elevatorstation/blender/review_descent/concept.png)

![Mouth and base join](B:/Dev/SMR/SMR-Assets/elevatorstation/blender/review_descent/mouth.png)

**Render limit:** the portal is the actual exported candidate mesh. The elevator and approach
track are dimensioned, render-only reference proxies; they are not vanilla's detailed mesh.
The exact art join, in-game lighting and quality acceptance remain the owner's sitting. The
proxy retains the visible ground in the core; it makes no claim to have fixed the deferred core.

## Measured at the desk

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

## Departure hold and what it establishes

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

The continuation is still within vanilla Station: investigate the placement of Rampdepart and
the connector, including whether the second departure leg (which does request pitch zero) can
carry the ascent. That is a lead, not a prescribed solution or a successful run. A revised layout
must account for the whole departure and arrival envelopes, terrain, the tapered roof, the rail
and the actual off-centre train origin. If it cannot, brief 25's stop requires options with
numbers and renders; no custom train movement is authorized. The compact shell is kept for
review without pretending its proposed spots are ready for import.

## Owner decision and continuation

**OI-33** asks whether the owner keeps this portal shape/placement or names a change. No reply or
acceptance has been recorded. The reason for this decision point is brief 25: **"Show before you
import"** and **"The owner says yes or names the change. Only then the Mod Editor import."**

After that decision, the agent finishes movement clearance under the brief's stops, promotes the
accepted geometry and spots into `depot_build.py` / `verify_depot.py`, synchronizes the dev Lua's
`layout` and `design_spots`, and commits a checkpoint. Then the owner uses the **existing**
EntitySpec's `mesh` → Open in Importer → Import → save, followed by the required restart and
surface/train/underground sitting. The earlier README instruction to create another EntitySpec
has been corrected; the existing one is already imported.

No import, game launch, Lua change, train run, cabin/sound verification or ceiling measurement
was performed here. Underground rope remains the prior unmeasured default, 300 m; cabin travel,
timing and ropes were not retuned. Cargo, drone crew, twin placement, the vanilla elevator, hub
code/art, rail shaft and deferred core defects were not worked.

## Close-out routing

| finding/block | evidence and home | next action | disposition |
|---|---|---|---|
| owner concept and arrow | verbatim authority above; original report §7 and reference images | OI-33 look decision | preserved |
| candidate/static proof | scripts, hashes, JSON and renders above | keep or revise shell | reviewable; no acceptance claim |
| departure source and clearance | archived build lines and departure study above | brief 25, vanilla layout work after shape decision | open, homed here; no universal impossibility claim |
| imported baseline/Lua synchronization | baseline entity read and empty dev-mod diff | synchronize only with the accepted prepared revision | preserved in brief and Assets README |
| surface/cabin/train/underground sitting | brief 25's done-condition and sitting | after prepared accepted import | all still owed |
| core sand/frame and cargo wiring | owner deferral above; prior station report §6 | later design/wiring pass | preserved, untouched |

Executed agent: **Codex, GPT-6 family as identified by the session instructions**. The exact
serving-model identifier and effort are not exposed in this transcript; no subagents were used.
`PROBE SWEEP: clean` from `rg -n 'TEMPORARY' Code/ ../SMR-BugFixPack-TestKit/Code/` (exit 1,
the explicit wrapper reported clean). Python compilation and `git diff --check` passed for the
Assets changes. `python tools/doccheck.py` ran GREEN on 2026-09-30 with these documentation edits.

| repository | commit | scope |
|---|---|---|
| SMR-Assets | `7f087ce` | candidate generator/workfile, independent FBX proof, renders/review sheet, departure study and pipeline README |
| OptInPack | this report's commit | report, OI-33, brief 25 handoff and its map row |

Handoff byte measurement, both by `len(Path(...).read_bytes())`: brief 25 was **17,567 → 18,801
bytes** (+1,234). The removed stale request to repeat owner feedback is homed in the verbatim
authority above and the prior report §7. Imported-entity evidence, model/import continuation and
the full sitting remain linked in the brief; no open obligation was dropped. Assets has no
remote, so its commit remains local. The pre-existing untracked trainhub backups remain untouched.
