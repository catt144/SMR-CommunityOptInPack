# Staging workbench: a non-shipping sibling mod for modules in progress, with a promote path

**Fire with:** `task docs/agent/prompts/STAGING_WORKBENCH_BUILD_high.md` in a fresh session rooted
at `B:\Dev\SMR\SMR-OptInPack`. Reasoning: high (packaging, load order and the save contract).

## Authority and outcome

The owner, 2026-10-03, after the final launch audit (`reports/FINAL_LAUNCH_AUDIT_20261003.md`)
found the package would carry the post-launch Arboretum: *"A place to park and still work on
modules while still being able to upload and move things out of it and into production."*

The orchestrator session proposed this design and the owner asked for it:

- **`staging/` in this repo is its own mod**, the workbench, with its own `metadata.lua`,
  `items.lua` and mod id (for example `SMR_CommunityOptInPack_Workbench`), titled so it is
  obviously dev-only. The owner enables it locally through a second link in the Mods folder (this
  mod's own link is `%APPDATA%\Surviving Mars Relaunched\Mods\SMR-OptInPack` → the repo). It is
  never uploaded.
- **This mod's package never contains it.** `staging/` is in `ignore_files`, and
  `tools/pack_predict.py` (or its equivalent) proves the package holds nothing from it.
- **Workbench modules use this mod's framework.** They register into the `SMROptInPack` registry
  and options exactly as production modules do, and load after this mod. A workbench module
  behaves as it will after promotion.
- **Persisted names are final from day one.** A workbench module writes only the names it will
  keep in production (`FIX_POLICY` persisted-name inventory and both bans), so a save carries
  across promotion unchanged.
- **One promotion tool.** `tools/promote_module.py <name>` moves the module's files and
  registration lines from the workbench into this mod, and removes them from the workbench. It
  then runs the gates and prints what it changed. A `--check` mode reports without moving.
- **A doccheck guard.** Production `metadata.lua`/`items.lua` never reference `staging/`; no
  module is registered in both mods; the workbench's code list and files agree.
- **The Arboretum (D19) is its first resident.** The owner ruled it ships after launch.

Done when: the workbench loads in game beside this mod with the Arboretum working from it; this
mod's package is the launch set alone, proved by the pack prediction; promotion of a throwaway
test module round-trips under `--check` and for real, then is reverted; and doccheck is GREEN with
the guard live.

## Starting state and coordination

`git log --oneline -5`, `git pull`, `git status --short`; authored at `d790f43`. The Arboretum's
build session left its work in the shared tree. That includes uncommitted hunks in this mod's
`metadata.lua` and `items.lua`, and untracked `Code/Opt_Arboretum.lua`,
`Code/BuildingTemplate/…`, `Data/BuildingTemplate/…`, `tools/arboretum/` and `docs/agent/bugs/D19.md`.

**Recheck `git status` before touching any of it.** Move those files into the workbench, and take
the Arboretum registration out of this mod's two files. Leave the ARBORETUM brief and its report to
that session. Record in the commit message what you moved, and re-derive D19's paths.

`Launch_Prep/03A_RELEASE_CORRECTIONS_high.md` may be running beside you. It owns release tooling,
and you own `staging/`, the promote tool and the guard. Recheck shared paths before writing
(`CLAUDE.md`). If you both need `metadata.lua`'s `ignore_files`, the later writer merges and does
not revert.

## Judgment delegated

The workbench's folder layout, how it finds and loads after this mod (dependency field or load
order, from engine evidence), how its options appear, the promote tool's interface, and where its
documentation lives (`docs/README.md` map; `tools/README.md` catalogue row) are your calls. Record
them in the commit messages.

## Scope

In: the workbench mod, the Arboretum's move into it, the promote tool, the guard, the pack proof,
and docs. Out: changing the Arboretum's behaviour, the Arboretum's open owner asks (OI-47, OI-48),
release tooling owned by 03A, and any upload.

## Stops

1. The engine cannot load a second mod against this mod's framework without changing a
   production module's behaviour. Report it with the evidence.
2. A workbench module would need a persisted name it cannot keep in production. That is the
   owner's decision.

## Lifecycle

One-off. In the closing commit, delete this prompt and its row in `docs/agent/prompts/README.md`,
and add a line for the promote route where module-building work reads it (`perma/WORK_PROMPT.md`
or `docs/agent/WORKFLOW.md`). References: `CLAUDE.md`, `docs/agent/FIX_POLICY.md`,
`docs/agent/WORKFLOW.md`; skills `doc-editing`, `smr-bug-library`.
