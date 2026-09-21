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

## 1 · Editor-held (5) — rewrite with the editor closed, then verify in the Importer header

All five point **outward into `SMR-Assets`**, so they survive a move of `SMR-OptInPack` alone and
break only when the asset tree moves — which it now does.

- `tools/devmods/train_hub/SourceData/SIE_ImportItem/SMROptInTrainHub6.lua:6` — `ScenePath`, the body
  FBX under `trainhub/blender/export/concept/`.
- `tools/devmods/train_hub/SourceData/GFXMaterial/SMROptInTrainHub6.lua:4-7` — `BaseColor`, `Normal`,
  `RM`, `SI`, the four maps under `trainhub/blender/textures/concept/`.

Each new entity adds its own pair, so **the glass and the themed reactor will add up to ten more**
once they are imported. Repoint after the move, or import them after it and they are born correct.

## 2 · The game's mod symlinks — recreate all five

`%APPDATA%\Surviving Mars Relaunched\Mods\` holds symlinks, not copies. After the move every one is
dead and **the mod silently ceases to exist for the game**:
`SMR-BugFixPack`, `SMR-BugFixPack-TestKit`, `SMR-OptInPack`,
`SMR-TrainHubDev` → `…/tools/devmods/train_hub`, `SMR-TrainHubPrototype` → `…/tools/prototypes/train_hub`.

## 3 · Scripts — the ones that resolve at run time

- **Already parameterised, so they move for free if the variables are set:** `tools/doccheck.py:66`
  (`SMR_TESTKIT`), `tools/sync_from_fixpack.py:51,333,337-338` (`SMR_FIXPACK`, `SMR_SRCARCHIVE`,
  `SMR_TESTKIT`, `SMR_TRAINASSETS`). **Setting those environment variables to the new roots is the
  cheapest single action in this whole list.**
- **Hard-coded, need rewriting:** `tools/devmods/train_hub/tests/traffic_smoke.py:20-21`
  (`SMR-SrcArchive`, the shared oracle), `tests/record_evidence.py:23` (the fix pack's saves),
  `SMR-Assets/_shared/geometry/hub_oracle.py:2176-2178`, `_shared/geometry/patch_box_spots.py:2` and
  `predict_from_entity.py:2` (both reach into the dev mod's entity file),
  `SMR-Assets/trainhub/blender/build_workfile.py:16`.
- **Fixed 2026-09-21 in passing, they pointed at the deleted junction and would have failed on next
  use:** `snap_baseline.py:4` (hard-coded, not a fallback) and `export_prep_untextured.py:22`.
- **Left alone deliberately:** `_before_claude_pass2_20260918/` and `export/build_workfile_build3.py`
  are historical snapshots, and `C:\Dev\SMR-Optin-Assets\…fbx` in them is a donor that predates
  this tree.

## 4 · Config (13)

`.claude/settings.json:4-9` (six permission entries naming repo paths),
`tools/devmods/train_hub/tests/{read,smoke}_leg.json` (`kit` and `park`), and three Blender proof
JSONs under `trainhub/blender/` whose `command` records the path it ran at — those are **evidence of
a past run and are not rewritten**; they record where it happened.

## After the move, in this order

1. Recreate the five symlinks; 2. set the environment variables; 3. rewrite the hard-coded scripts;
4. rewrite the 5 editor-held paths with the editor closed; 5. open the Importer and read its header;
6. only then import, with the owner. A wrong header at step 5 means stop, not proceed.

**Git carries no absolute paths**, so every commit and tag — `hub-model-final-untextured`,
`hub-centre-lights-20260921` — restores correctly wherever the tree lives.
