# Brief 34c, phase 1 — SMR-Assets cleanup proposal, 2026-10-02

Authority: [brief 34c](../prompts/Train_Hub_Project/34c_ASSETS_CLEANUP_medium.md) (owner,
2026-10-02: *"clean up SMR assets, getting rid of any failed / or retired models and only keep a
few cherry picked checkpoints that are good bases if we ever need to make major or minor
changes."*). Read at this repo's HEAD `b643110` and SMR-Assets HEAD `4aeb59b`, both pulled
(`Already up to date`). Executed model: Fable 5.1 (`claude-fable-5-1`), no subagents.

**State: done (2026-10-02).** The owner ruled on every question (§6) and phase 2 ran the same
day: 569 files, 4,427.7 MB deleted, SMR-Assets at `443206f`, both checks pass.

## Work list

| # | Item | State |
|---|---|---|
| 1 | Inventory, every class, with sizes | done (this report) |
| 2 | Reference check: every path the shipping mod stores resolves on disk | done, 22 of 22 |
| 3 | Classification and the proposal | done (this report) |
| 4 | Owner approval | done, §6 |
| 5 | K2: five checkpoint blends tracked | SMR-Assets `441f6e2` |
| 6 | U1: dome set `git rm`, READMEs and `.gitignore` noted | SMR-Assets `443206f` |
| 7 | Irreversible deletions A–E, K5 payload, U1 ignored; recheck | §6, this commit |

## 1. Inventory

Command: `git ls-files`, `git ls-files --others --exclude-standard`, `git ls-files --others
--ignored --exclude-standard`, then `os.walk` sizes, at SMR-Assets `4aeb59b`. The TSV of every
file (path, bytes, state) is `scratch/assets_cleanup_inventory_20261002.tsv` (git-ignored); the totals reconcile to it.

| Class | Files | MB | Where |
|---|---:|---:|---|
| tracked | 301 | 195.6 | scripts, proofs, review sheets, owner screenshots, icons, five work files |
| untracked | 5 | 2.0 | `trainhub/blender/TrainHub_work_before_*.blend` (five pass checkpoints) |
| ignored | 903 | 5,395.1 | textures, exports, renders, candidates, reference art, caches |
| `.git` | 1,135 | 320.2 | history; **out of scope** (rewriting is the owner's call) |
| **total** | **2,344** | **5,912.9** | |

Ignored files are the whole problem: tracked and untracked together are under 200 MB.

| Ignored folder | Files | MB |
|---|---:|---:|
| `trainhub/blender/export/` | 713 | 3,791.2 |
| `trainhub/blender/textures/` | 51 | 1,134.7 |
| `elevatorstation/blender/textures/` | 13 | 248.3 |
| `trainhub/reference/` | 76 | 115.5 |
| `elevatorstation/blender/export/` | 15 | 49.4 |
| hub preview renders, `trainhub/blender/*.png` | 29 | 46.7 |
| `__pycache__` and `.blend1` backups, everywhere | 79 | 51.3 |
| depot preview renders, `elevatorstation/blender/*.png` | 7 | 6.8 |

## 2. What is referenced (the SHIPPING floor)

The Mod Editor projects are the three symlinks in `%APPDATA%\Surviving Mars Relaunched\Mods\`
(`SMR-OptInPack`, `SMR-BugFixPack`, `SMR-BugFixPack-TestKit`); the two loose mods there
(`SMR_FR1TempWorkaround`, `SaveBufferFix`) hold no asset path. The only stored absolute paths
into SMR-Assets are this mod's `SourceData/SIE_ImportItem/*.lua` (five `ScenePath`) and
`SourceData/GFXMaterial/*.lua` (seventeen map paths). The fix pack, the TestKit and
`tools/devmods/rail_shaft/` reference nothing in SMR-Assets (`grep -rIl SMR-Assets`, prose hits
only). The dev mods `train_hub` and `elevator_station` were retired by brief 34
(`TRAIN_MOVE_20261002.md`); their old import items survive only as a copy under
`SMR-Shared/SMR-HubBackups/hub-bays-20260922/`, out of scope.

**Check, RAN:** every stored path extracted from the nine `SourceData` files and tested with
`[ -f ]`: **22 of 22 exist** (3 hub FBX in `export/concept/`, 2 depot FBX in
`elevatorstation/blender/export/`, 4 hub body maps in `textures/structure/`, 8 glass maps in
`textures/concept/`, 5 depot maps in `elevatorstation/blender/textures/`). This is the check
phase 2 reruns.

Live pipeline inputs beyond the stored paths, from the scripts' own path strings
(`grep -o 'textures/...|export/...' *.py`) and `trainhub/blender/README.md`:
`export/concept/TrainHub_prepaint.blend` (every bake and verifier runs on it), `export/ao/`
(the frozen AO layer `bake_structure.py` reads), `export/uv/` and `export/final/` (the proof
chain and the before-pass FBX that `verify_fbx_reimport.py` diffs), `export/structure/`
(`validation.json`, read by `validate_structure.py` and `measure_dds.py`),
`trainhub/decals/` and `trainhub/reference/` (the paint's and the icons' references),
`elevatorstation/blender/export/ao/` (the depot paint's AO). `validate_structure.py` names
`textures/thinlines_all` only as a string it records (`HELD`, line 38 and 1091); it does not read it.

## 3. Classification

Sizes are MB. "git" says whether `git rm` can undo it; **irreversible** marks what git cannot
bring back (ignored or untracked). Evidence is a commit in SMR-Assets unless named otherwise.

### SHIPPING — stays

| Path | MB | git | Evidence |
|---|---:|---|---|
| `trainhub/blender/export/concept/` (3 FBX, `TrainHub_prepaint.blend`, proofs) | 7.5 | ignored | the three `ScenePath`s; every bake runs on the prepaint blend (README §commands) |
| `trainhub/blender/textures/structure/` | 163.6 | ignored | `GFXMaterial/SMROptInTrainHub6.lua`; the reactor palette `a5535fb` |
| `trainhub/blender/textures/concept/` | 65.1 | ignored | the two glass materials; `54dc43f`, `83bf874` |
| `trainhub/blender/export/ao/` | 79.5 | ignored | the frozen AO layer, `2fb01e7`; README line 1230 |
| `trainhub/blender/export/uv/`, `export/final/` | 42.2 | ignored | proof chain and before-pass FBX, README lines 313-322, 698-709, 883-890 |
| `trainhub/blender/export/structure/` | 212.1 | ignored | `validation.json`, density and DDS measurements, published previews (`3be561d`, `cb60471`) |
| `trainhub/blender/export/floor_pass_proof.json` | 0.0 | ignored | written by `verify_floor_pass.py`, run by every build |
| `trainhub/blender/TrainHub_work.blend`, the scripts, `concept_freeze*.json`, `*_baseline.json`, `GLASS_IMPORT.md`, `DOME_GLASS_IMPORT.md`, `README.md`, `paint_source/` | 2.5 | tracked | the production work file and the pipeline (out of scope by the brief) |
| `trainhub/blender/export/` tracked baselines (`TrainHub_build2_work.blend`, `TrainHub_build3_work.blend`, `TrainHub_untextured.blend`, `SMROptInTrainHub6_untextured.fbx`, `*_geometry.json`, `*_proof.json`, `hub_skeleton_build3.py`, `build_workfile_build3.py`) | 6.3 | tracked | `.gitignore` whitelist; `verify_build3_source.py`, `verify_look_pass.py` read them; this is the radius-6 model tag `hub-model-final-untextured` that `Parked/TRAIN_HUB_MODEL_high.md` keeps for reopening |
| `trainhub/decals/storage_cubes_owner_ref.png` | 0.6 | tracked | the bays' decal source, `53a15b4` |
| `trainhub/icon/`, `elevatorstation/icon/` | 6.0 | tracked | the shipped icons' sources: hub B `2dcb019`, depot A_mouth `4aeb59b` |
| `trainhub/reference/` (23 PNG + `raw/` 53 DDS) | 115.5 | ignored | game art, "local only, never committed" (SMR-Assets README); `paint_concept.py` reads the reactor reference, both `compose_icon.py` read the IconsRemaster PNGs; `Parked/TRAIN_HUB_LOOK_high.md` names `Concept.png` and `overall.png` |
| `elevatorstation/blender/ElevatorDepot_work.blend`, `depot_*.py`, `compose_*.py`, `verify_depot.py`, `diag_*.py`, `study_*.py`, `README.md`, the six tracked proofs in `export/` | 0.7 | tracked | the depot's live builder and painter (`533791c` … `635022e`) |
| `elevatorstation/blender/export/SMROptInElevatorDepot*.fbx`, `*_faces.json`, `*_preview_1024.png` | 1.7 | ignored | the two depot `ScenePath`s and the painter's outputs |
| `elevatorstation/blender/textures/SMROptInElevatorDepot_*.tga` (5) | 234.9 | ignored | `GFXMaterial/SMROptInElevatorDepot.lua` |
| `elevatorstation/blender/export/ao/` | 46.9 | ignored (proof tracked) | the depot paint's AO/bevel/cavity bake, `f059a97` |
| `elevatorstation/owner_feedback/` | 53.8 | tracked | the owner's screenshots, cited by rulings (`0dd71de` … `f3346d2`) |
| `elevatorstation/blender/review_descent/`, `review_design_pass/`, `review_paint/`, `review_prepared/` | 122.0 | tracked | the approval renders the README links; in git, so deleting frees the working tree only. Kept; say the word and they become a line in phase 2 |
| `_shared/` | 0.5 | tracked | out of scope by the brief |

### CHECKPOINT CANDIDATES — the few bases

| Path | MB | git | Base for |
|---|---:|---|---|
| **K1** `trainhub/blender/export/` build-3 baselines (listed under SHIPPING) and tag `hub-model-final-untextured` | 6.3 | tracked | the final radius-6 geometry before the look pass, the one the parked MODEL brief reopens on. Already kept; no action |
| **K2** the five untracked `TrainHub_work_before_{floor,portal_pit,rim_edges,floor_islands,crown}.blend` (2026-09-21 03:04 … 09-22 17:36) | 2.0 | **untracked, irreversible** | the work file before each look-pass step: the proofs cite them (`crown_baseline.json` is taken from `before_crown`, README line 233; `--legacy` reproduces `before_portal_pit` 99 of 99, line 969; `before_rim_edges` 764; `before_floor_islands` 708). **Recommendation: keep all five and commit them** (2 MB; they are the pass-by-pass model checkpoints, and a `.blend` under 1 MB is within the README's size rule) |
| **K3** `trainhub/blender/TrainHub_work_before_glass_cleanup.blend` (2026-09-18) and `_before_claude_pass2_20260918/` | 1.2 | tracked | the Tripo-import era model before pass 2, the oldest base. Already kept; no action |
| **K4** `elevatorstation/blender/ElevatorDepot_candidate.blend` + `export/candidate_descent/` | 0.7 | tracked (3 of 6 ignored) | the depot's accepted model snapshot, "the comparison input, do not rebuild over it" (depot README, "Historical candidate and imported baseline"). Already kept; no action |
| **K5** `trainhub/blender/export/structure_seams/` and `structure_solid/` | 749.6 | ignored, irreversible | the last production bake's two variants (`seams` is what `textures/structure/` publishes), each with `bake_proof.json` and the 14 MB `preview.blend` the icon render ran on (`render_icon.py` line 4). Regenerable: `bake_structure.py` rebakes both in about 205 s (README line 469). **Owner's call: keep as the bake checkpoint, or free 750 MB and rebake when needed** |

### RETIRED or FAILED — proposed deletions

All of these are **ignored by git and therefore irreversible** on this disk. For the hub's map
sets there is a second copy: every restore tag `hub-*-2026092x` copied the then-current ignored
maps to `B:\Dev\SMR\SMR-Shared\SMR-HubBackups\<tag>\` (4.6 GB, 12 folders, out of scope). The
exact path list (503 files) is `scratch/assets_cleanup_proposed_delete_20261002.txt` (git-ignored, beside `scratch/assets_cleanup_inventory_20261002.tsv`) and is what phase 2 deletes.

| Group | Paths | Files | MB | Evidence it is retired |
|---|---|---:|---:|---|
| **A** regenerable caches | every `__pycache__/`; every `.blend1` (Blender's own previous-save backup, 11 of them) | 79 | 51.3 | Blender and Python regenerate them on the next run |
| **B1** legacy and `.55` bake variants | `export/structure_seams_legacypaint/`, `structure_solid_legacypaint/`, `structure_seams_si55/`, `structure_solid_si55/` | 89 | 1,311.8 | the legacy palette is one knob away and byte-reproducible (`bake_structure.py -- --legacy-paint`, README lines 27-28, 436); `.55` was the fallback never chosen (`537b02e`, README line 526) |
| **B2** build-3 imported maps | `export/textures_build3_imported/` | 3 | 151.0 | the pre-look-pass `texture_hub.py` set, superseded by the concept paint `35cda1a` and every pass since |
| **B3** candidate-pass payloads (maps, renders, preview blends; the `.md`/`.json`/`.log` proofs in each folder stay) | `export/bays/`, `edges/`, `pad/`, `pad_before/`, `nostrips/`, `thinlines/`, `thinlines_all/`, `siding/`, `pit_candidates/`, `portal_candidates/`, `previews_build3/`, `for_texturing/`, `glow/` | 252 | 1,210.3 | each pass was ruled and its winner published into `textures/structure/`: bays A `70b1ab9`; edges `332548e`/`24a98b7`; pad/nostrips/thinlines chain `ea82ef4` … `a93a143`, superseded by structure `a2b9727`; siding `253c180`; pit and portal B `2f4b782` (candidates A, C withdrawn; "run them on the legacy workfile if another candidate is ever wanted", README line 1661, the builders are tracked); `for_texturing/` was the Tripo texturing export `df9bb50`, never used; `previews_build3/` are build-3 renders |
| **C** superseded published map sets | `textures/pad/`, `nostrips/`, `thinlines/`, `thinlines_all/`, `structure_before_bays/`, `structure_before_siding/`, `structure_seams/`, `structure_si55/`, and the root `textures/TrainHub_{BC,NM,RM}.tga` | 33 | 906.0 | the material points at `structure/` only; `structure_seams/` and `structure_si55/` are "DEAD-ATLAS leftovers" (README lines 310, 676, 872); the `_before_*` byte copies served the isolation proofs, already written (`bay_isolation_production.py`, `siding_isolation_production.py`); the root TGAs are build 3's. `Parked/01_TRAIN_HUB_STRUCTURE_high.md` names `thinlines_all`, `structure_seams`, `structure_si55` and `structure_before_*`, but that brief's work shipped (`a5535fb`) and the restore-tag copies in SMR-Shared hold these sets |
| **D** build-3-era export root files | `export/SMROptInTrainHub6.fbx` (the pre-concept export; the `ScenePath` is `concept/`), `_build3_imported.fbx`, `_prepaint_backup.fbx`, `_body_for_tripo.glb` (`df9bb50`), `TrainHub_export.blend`, `build3_export_geometry.json`, `geometry_mismatch.json`, `geometry_proof.json`, `unwrap_{before,after}.json`, `asset_validation.json`, `smoke_import.{json,log}`, the four `.log`, `inspect_pad.py` | 18 | 7.5 | written by `texture_hub.py`, `smoke_import.py`, `verify_assets.py`, the build-3 chain before the UV freeze `69b23fc`; `floor_pass_proof.json` is excluded and stays |
| **E** stale hub preview renders | `trainhub/blender/preview_*.png`, `diagnostic_*.png`, `transition_*.png` | 29 | 46.7 | headless renders of earlier passes; `render_previews.py` remakes them; the depot's seven `preview_*.png` stay (its README names them as the current render output) |
| | **total proposed** | **503** | **3,684.6** | of 5,395.1 ignored; about 1,710 MB of ignored files stay (the SHIPPING rows, K5 and the UNSURE rows) |

Not proposed, noted: a tracked script that serves only a retired folder (`tripo_cleanup.py`,
`tripo_body_export.py`, `export_for_texturing.py`, `texture_hub.py`, `smoke_import.py`,
`verify_assets.py`, `bake_pad.py`, `bake_nostrips.py`, `bake_thinlines.py`, `validate_pad.py`,
`validate_nostrips.py`, `validate_thinlines*.py`, `render_*` for the candidate passes). The brief
puts the pipeline scripts out of scope; they are small and in git. Say the word and they become
one `git rm` line.

### UNSURE — the owner rules

| Path | MB | git | Why it is the owner's |
|---|---:|---|---|
| **U1** the Elevator Station dome: `elevatorstation/blender/ElevatorStation_work.blend`, `station_build.py`, `station_render.py`, `verify_station.py`, `export/station_proof.json`, `export/verify_station.json` (tracked, 0.4); `export/SMROptInElevatorStation{,Glass,Shaft}.fbx`, `textures/SMROptInElevatorStation*_*.tga`, `preview_*.png` (ignored, 20.6) | 21.0 | mixed | "on hold (owner, D4)" (depot README line 3), a parked feature. Nothing references it: the dev mod that placed it was retired by brief 34 and this mod's `Entities/` holds no `SMROptInElevatorStation`. Stop 3 applies |
| **U2** `trainhub/blender/TrainHub_work_Owner_edit.blend` (2026-09-20) | 0.4 | tracked | the owner's own save; `Parked/TRAIN_HUB_MODEL_high.md` line 64: "leave the owner's file where it is" |
| **U3** `trainhub/reference/raw/` (53 `.dds`, the decoded sources of the 23 reference PNGs) | 88.8 | ignored | game art; the PNGs beside it are what the scripts read. Delete the raw DDS, or keep the pair |
| **U4** the 12 restore-tag copies in `SMR-Shared/SMR-HubBackups/` | 4,600 | outside git | outside this brief's scope (another folder), named here because they are the only copy of the group C sets once C is deleted, and because they are 4.6 GB of the same kind of thing |
| **U5** `.git` | 320.2 | — | reported, not touched (brief scope) |

Nothing in SMR-Assets belongs to the rail shaft (`grep -ril shaft` finds only the dome's
`SMROptInElevatorStationShaft`) or to another mod.

## 4. The questions for the owner

1. **Approve the deletion groups A–E** (503 files, 3,684.6 MB, all irreversible on this disk;
   the hub map sets have copies under the restore tags in SMR-Shared). Any group can be struck.
2. **K2:** commit the five untracked `TrainHub_work_before_*.blend` as tracked checkpoints
   (recommended), or delete some of them.
3. **K5:** keep `export/structure_seams/` and `structure_solid/` (749.6 MB) as the bake
   checkpoint, or delete them and rebake when needed.
4. **U1** the Elevator Station dome, **U2** the owner's edit, **U3** `reference/raw/`: keep or go.
5. Optional lines: the review render folders (122 MB tracked), the scripts that serve only
   retired folders, and the 4.6 GB of restore-tag copies in SMR-Shared.

## 5. Phase 2 plan (on approval)

- Tracked deletions (only U1, U2 and the optional lines can be tracked): `git rm` by pathspec,
  one commit in SMR-Assets naming this report and the approved lines.
- K2: `git add` the five blends, one commit.
- Irreversible deletions: from the saved path list, only the approved groups, with a count
  before and after.
- Rerun the §2 check (22 stored paths) and a `--legacy --check-rebuild` of `build_workfile.py`
  is **not** needed: no proposed line is a build input. Then `git status --ignored` and the
  per-class totals again, reconciled against the list.

## 6. Owner rulings and phase 2 (2026-10-02)

Asked and answered the same day: **A–E approved whole; K2 commit all five; K5 delete and rebake
when needed; U1 delete the dome set; U2 and U3 keep.** The optional lines (review renders, the
scripts that serve only retired folders, the restore-tag copies in SMR-Shared) were not put to the
owner and stand untouched.

| Unit | What | Result |
|---|---|---|
| K2 | `git add` the five `TrainHub_work_before_*.blend` | SMR-Assets `441f6e2`, 5 files, 2.0 MB |
| U1 tracked | `git rm` `ElevatorStation_work.blend`, `station_build.py`, `station_render.py`, `verify_station.py`, `export/station_proof.json`, `export/verify_station.json`; the two whitelist lines left `.gitignore`; both READMEs carry a one-line note pointing at `07d67b1` | SMR-Assets `443206f` |
| A–E | the saved list | 503 files, 3,684.6 MB, 0 already absent |
| K5 | `export/structure_seams/` and `structure_solid/` payload (`.json`/`.md` proofs kept) | 48 files, 722.4 MB (the two `.blend1` had gone with group A) |
| U1 ignored | 3 station FBX, 8 station TGA, 7 `preview_*.png` | 18 files, 20.6 MB |
| | **total** | **569 files, 4,427.7 MB**; 25 emptied folders removed; every path is logged in `scratch/assets_cleanup_deleted_20261002.txt` |

**After:** tracked 300, untracked 0, ignored 334 (was 301 / 5 / 903); working tree without `.git`
**1,164.7 MB** (was 5,592.7). The `structure_*_legacypaint/` and `_si55/` folders still exist
because their `bake_proof.json`/`validation.json` stayed, as the proposal said.

**Recheck, RAN after the deletions:** the 22 stored paths from the nine `SourceData` files,
**22 of 22 exist**; and 14 named pipeline inputs (`TrainHub_prepaint.blend`, the AO, UV, final,
structure and floor-pass proofs, the decal, the two reference PNGs the scripts read, the depot's
AO proof, candidate snapshot and the two kept `bake_proof.json`) all present. Nothing the shipping
mod, a dev mod or a Mod Editor project references was removed.
