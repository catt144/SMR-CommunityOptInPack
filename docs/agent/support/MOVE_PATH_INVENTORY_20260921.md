# The SMR tree move: what holds an absolute path, and who repoints it

Built 2026-09-21, before the move, because hunting these afterwards is how a silent breakage
happens. **Every SMR repo is moving** to a dedicated structure (owner, 2026-09-21), so every
absolute `C:\Dev\...` below changes. Counted by
`grep -rIn --exclude-dir=.git --exclude-dir=archive -E "C:[/\\]+Dev"` over `SMR-OptInPack` and
`SMR-Assets` on that date: **5 editor-held, 29 in scripts, 13 in config, 134 in prose.**

⛔ **The one that bites silently.** The Mod Editor **stores absolute paths and reasserts them over a
drag**: drop a different FBX on the Importer and it imports the stored file instead, with no error
and no visible change. MEASURED 2026-09-21; it cost the owner an import and an hour. Repoint those
files **on disk with the editor closed**, then reopen and read the Importer's header to prove it.

## Who does what

| Owner | Items |
|---|---|
| **The doc orchestrator** (owns the move) | the move itself; prose path references; `docs/` maps; `doccheck.py` and the packaging tooling it is already in; keeping doccheck green |
| **The train orchestrator** | the 5 editor-held paths; the game's mod symlinks; the dev mod's test scripts; the verification import with the owner |
| **The owner** | where everything lands; running the Mod Editor for the verification import |

⛔ **The doc orchestrator MOVES files under `tools/devmods/**` and `tools/prototypes/**` but does not
EDIT their contents.** Those are editor-generated and stamped "DO NOT EDIT MANUALLY"; they are
repointed under the procedure above.

## 1 · Editor-held (5) — REPOINTED, header read still owed

All five — `SIE_ImportItem/SMROptInTrainHub6.lua:6` (`ScenePath`, the body FBX) and
`GFXMaterial/SMROptInTrainHub6.lua:4-7` (`BaseColor`, `Normal`, `RM`, `SI`) — were rewritten on disk
with the editor closed, each in its own file's slash style, and every target resolves under
`B:\Dev\SMR\SMR-Assets`. The diff is path-only. **The Importer header has NOT been read yet**: that
is step 5 below and it is the proof, so nothing is imported until the owner runs it.

Each new entity adds its own pair, so **the glass and the themed reactor will add up to ten more**.
Import them after the move and they are born correct.

## 2 · The game's mod symlinks — DONE

`%APPDATA%\Surviving Mars Relaunched\Mods\` holds symlinks, not copies, so a dead one means **the mod
silently ceases to exist for the game**. `SMR-OptInPack`, `SMR-TrainHubDev` and
`SMR-TrainHubPrototype` were recreated against `B:\Dev\SMR\SMR-OptInPack`. `SMR-BugFixPack` and
`SMR-BugFixPack-TestKit` still point at `C:\Dev\` and are CORRECT: those two repos have not moved.

## 3 · Scripts — the ones that resolve at run time

- **Parameterised, and every default now names the new root, so NO environment variable has to be
  set** for them to resolve: `tools/doccheck.py:66` (`SMR_TESTKIT`),
  `tools/sync_from_fixpack.py:51,333,337-338` (`SMR_FIXPACK`, `SMR_SRCARCHIVE`, `SMR_TESTKIT`,
  `SMR_TRAINASSETS`). The two fix-pack defaults stay on `C:\Dev\` because that repo has not moved.
- **Were hard-coded, now REWRITTEN:** `tools/devmods/train_hub/tests/traffic_smoke.py` takes
  `SMR_SRCARCHIVE` and `SMR_TRAINASSETS` with new-root defaults, matching the pattern the
  `SMR-Assets` scripts already use; `SMR-Assets/_shared/geometry/hub_oracle.py`,
  `patch_box_spots.py`, `predict_from_entity.py` and `trainhub/blender/build_workfile.py` were done
  in the asset tree's own pass. `tests/record_evidence.py:23` was LEFT: it names the fix pack's
  saves, which have not moved.
- ⛔ **`SMR-SrcArchive` did not land beside its siblings**: it is
  `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive`, not `B:\Dev\SMR\`. The archived `Train.lua` and
  `Station.lua` hash identical to the pre-move copies, so the repoint is faithful.
- **Fixed 2026-09-21 in passing, they pointed at the deleted junction and would have failed on next
  use:** `snap_baseline.py:4` (hard-coded, not a fallback) and `export_prep_untextured.py:22`.
- **Left alone deliberately:** `_before_claude_pass2_20260918/` and `export/build_workfile_build3.py`
  are historical snapshots, and `C:\Dev\SMR-Optin-Assets\…fbx` in them is a donor that predates
  this tree.

## 4 · Config (13) — DONE

`.claude/settings.json:4-9` (six permission entries naming repo paths),
`tools/devmods/train_hub/tests/{read,smoke}_leg.json` (`kit` and `park`), and three Blender proof
JSONs under `trainhub/blender/` whose `command` records the path it ran at — those are **evidence of
a past run and are not rewritten**; they record where it happened.

## After the move, in this order

1. Recreate the five symlinks; 2. set the environment variables; 3. rewrite the hard-coded scripts;
4. rewrite the 5 editor-held paths with the editor closed; 5. open the Importer and read its header;
6. only then import, with the owner. A wrong header at step 5 means stop, not proceed.

**Steps 1, 3 and 4 are done and step 2 turned out to be unnecessary** (the defaults carry the new
roots). ⛔ **Steps 5 and 6 are the owner's and are still owed**, and they gate the awaiting import
round of the rebuilt body, the glass and the reactor.

**Git carries no absolute paths**, so every commit and tag — `hub-model-final-untextured`,
`hub-centre-lights-20260921` — restores correctly wherever the tree lives.
