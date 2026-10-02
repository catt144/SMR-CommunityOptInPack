# 34c — Clean up SMR-Assets: drop failed and retired models, keep a few good bases (cleanup job)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/34c_ASSETS_CLEANUP_medium.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`. Fire it **after brief `34` closes**, because
34's move reads the shipping assets. It may run beside `34b`, which touches code only.

Reasoning: medium. This is classification against the repo's own history. The owner makes the keep
decisions.

## Authority and outcome

The owner, 2026-10-02: *"clean up SMR assets, getting rid of any failed / or retired models and
only keep a few cherry picked checkpoints that are good bases if we ever need to make major or
minor changes."*

When this is done, `B:\Dev\SMR\SMR-Assets` holds only:

- the sources of what ships (the hub's and the depot's models, textures and icons, as moved by
  brief 34);
- the shared pipeline tools and facts (`_shared/`);
- a few checkpoints the owner picked.

Every failed or retired model is gone.

It is done when:

1. the owner has approved the keep/delete list;
2. the approved deletions are made, and those of tracked files are committed in SMR-Assets;
3. a check shows that nothing the shipping mod, the dev mods or the Mod Editor projects reference
   was removed.

## Phase 1: inventory and proposal (no deletions)

1. **Inventory everything**, including untracked and ignored files: `git status --ignored`, and
   sizes per folder and per file. The repo is about 5.6 GB, and most of it is outside git, for
   example the untracked `trainhub/blender/TrainHub_work_before_*.blend` checkpoints. Report the
   size of each class, and what deleting it frees.
2. **Classify every model, work file and export** as one of the following, with the evidence for
   each: the commit, report or ruling, cited by hash or by grep anchor.
   - **SHIPPING:** a source the shipped entities, textures or icons came from, or a file anything
     references. That covers this mod's tree after 34's move, `tools/devmods/`, and the Mod Editor
     projects. The Mod Editor stores **absolute paths** and reasserts them, so read the stored
     paths rather than inferring them.
   - **CHECKPOINT CANDIDATE:** a good base for a later major or minor change. Propose **a few**,
     each with one line on what it is a base for. Examples to weigh:
     - the hub's final radius-6 model, which `Parked/TRAIN_HUB_MODEL_high.md` keeps for reopening;
     - a pre-look-pass base;
     - the depot's accepted model.

     Whatever a parked brief in `docs/agent/prompts/Train_Hub_Project/Parked/` would need to
     reopen belongs here or under SHIPPING.
   - **RETIRED or FAILED:** superseded or rejected work, naming the ruling or commit that retired
     it. Two examples are the withdrawn 41.5 m geometry options (`GEOMETRY_ORACLE_20260919.md` §13)
     and the cut portal doors (`8aef5de`).
   - **UNSURE:** this goes to the owner. It includes anything belonging to a parked feature (the
     rail shaft) or to another mod.
3. **Write the proposal** to `docs/agent/reports/` in this repo, as a table of path, class, size,
   evidence, and whether it is in git. Mark every deletion that git cannot undo (untracked or
   ignored files) as **irreversible**. Then stop and ask the owner to approve the list. The
   orchestrator relays it.

## Phase 2: delete what the owner approved

- Delete only what the owner approved.
- Tracked files: `git rm`, then commit in SMR-Assets by pathspec. The approved list and the
  report's name go in the commit message.
- Untracked or ignored files: delete them only where the owner approved that specific
  irreversible line.
- Then rerun the reference check from phase 1, step 2 against what remains, and show that it
  finds nothing missing.

## Scope

In: the contents of `B:\Dev\SMR\SMR-Assets`.

Out:

- rewriting git history to shrink `.git` (report its size; the owner decides);
- the other repos;
- `_shared/geometry/hub_oracle.py`, which the orchestrator keeps as an instrument;
- `_shared/IMPORTER_FACTS.md` and the pipeline scripts, except any material inside them that has
  been retired.

## Stops (report instead of continuing)

1. A deletion would remove something a shipping or dev mod, or a Mod Editor project, still
   references.
2. The owner has not approved the list. No deletion happens before that approval.
3. A file belongs to another mod or to a parked feature, and the owner has not ruled on it.

## Work list and references

Keep a work list, one item per commit-and-verify unit: in the todo tool if the session has one,
otherwise in the report. Start with `git log --oneline -5` and `git pull` in both repos. This
brief was authored at `9f217b5` in this repo and `4aeb59b` in SMR-Assets.

House rules are in `CLAUDE.md`. SMR-Assets' own `README.md` holds its layout and ignore rules. Use
`doc-editing` for any doc you write here. The orchestrator owns this brief's lifecycle; do not
move or delete it.
