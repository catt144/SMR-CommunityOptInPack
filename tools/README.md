# tools/ — what each script is, and what its output does NOT license

The map of this repo's instruments. **Route from here; read the script's own header before you
quote it.**

⛔ **Every instrument is an over-reporter.** Adjudicate a row by reading the source line it cites,
never by its count (`WORK_PROMPT.md` §4, `PROVENANCE.md` §6). A tool that finds 30 hits has found
30 candidates, not 30 defects.

⛔ **A desk PASS is "desk-verified", never "verified."** Nothing in this folder launches the retail
game. `tested-attended` / `tested-unattended` are claims about a real game run and no script here
can earn one (`WORK_PROMPT.md` §7).

⛔ **Never hand-type a number any of these emits.** `python tools/doccheck.py --emit-counts` prints
the counts; `--emit-fingerprint` reads the installed game build from the Steam `.acf` and says which
fact groups still describe what is on disk.

Install the pre-commit hook once per clone: `git config core.hooksPath tools/hooks`.

⛔ **A tool here that shells out to `git` must scrub `GIT_*` from its environment first.** The hook
runs `doccheck`, `doccheck` runs the falsifiers, so during a commit every subprocess inherits
`GIT_INDEX_FILE` and `GIT_DIR` pointing at the **temporary index git is building the commit from**.
A scratch repository is not isolated unless its environment is too. Learned 2026-09-17: a scratch
`git add` wrote its fixtures into the real commit's index and killed it with
`invalid object … for 'docs/agent/prompts/README.md'` — naming a file nothing had touched. The
second failure is quieter and worse: a gate's own `git ls-files` enumerates the REAL tree while the
test believes it is reading the scratch one, so the falsifier passes for the wrong reason. Working
example: `rule_headers_selftest.py`, top of file.

<!-- GENERATED TOOL ROWS — never hand-edit; regenerate with: python tools/doccheck.py --regen -->

*19 scripts, every `tools/*.py` on disk. This block is GENERATED: a row's text is copied from the script's own header, so a wrong row is repaired in the script, never here.*

### Repo gates, and the falsifiers that keep them honest

The pre-commit hook runs `doccheck.py`; a `*_selftest.py` is required BY it, so a gate whose falsifier stops firing is itself RED. A gate that has only ever been seen passing on a clean tree has not been tested.

| script | what its own header says |
|---|---|
| [`doccheck.py`](doccheck.py) | doccheck.py — the structure checker (DOC_RESTRUCTURE_SPEC.md §5). |
| [`rule_headers_selftest.py`](rule_headers_selftest.py) | Falsifier for doccheck's RULES HEADERS / RULE PLACEMENT gate. |

### Generated-document machinery

The splitters own `bugs/INDEX.md` and `facts/INDEX.md`. ⛔ Never run either with `--write`: that re-runs the one-time migration from a retired pre-split document. `--regen` is the cure for drift.

| script | what its own header says |
|---|---|
| [`split_bugs.py`](split_bugs.py) | split_bugs.py — docs/BUGS.md -> docs/agent/bugs/ (DOC_RESTRUCTURE_SPEC §3a, as amended by the ROUTE (a) decision in the docs-restructure chain's prompt 2). |
| [`split_facts.py`](split_facts.py) | split_facts.py — docs/agent/ENGINE_FACTS.md -> docs/agent/facts/ (DOC_RESTRUCTURE_SPEC §3b, executed by the docs-restructure chain's prompt 3). |

### Desk instruments — what a module does without launching the game

The L-series. ⛔ A desk PASS is "desk-verified", never "verified" (`WORK_PROMPT.md` §7): none of these launches the retail game. Every one is an over-reporter — adjudicate a row by reading the source line it cites, never by its count.

| script | what its own header says |
|---|---|
| [`l2_reload_sim.py`](l2_reload_sim.py) | Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| [`l3_save_footprint.py`](l3_save_footprint.py) | Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| [`l4_player_surfaces.py`](l4_player_surfaces.py) | Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| [`l5_containment.py`](l5_containment.py) | Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| [`l6_promise_map.py`](l6_promise_map.py) | Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| [`l6_reachability.py`](l6_reachability.py) | Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| [`l7_env_map.py`](l7_env_map.py) | L7 (environment & namespace) — the global map, taken from the COMPILER. |
| [`l8_hostile_input.py`](l8_hostile_input.py) | Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |

### This mod's own code gates

Run by `doccheck` as well as by hand; the allowlists live beside the detectors, with a source citation per entry (`FIX_POLICY` §2).

| script | what its own header says |
|---|---|
| [`harvest_wrap_targets.py`](harvest_wrap_targets.py) | Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |

### Reading the shipped game by hand

⛔ Cite a line only with the build it was read on, from the archived tree for that build (`C:\Dev\SMR-SrcArchive`). The game moved to 1.1.0 on 2026-09-08 and overwrote `ModTools\Src`.

| script | what its own header says |
|---|---|
| [`flpk_extract.py`](flpk_extract.py) | FLPK (Surviving Mars: Relaunched .fpk) extractor, v2. |
| [`pack_list.py`](pack_list.py) | List a Surviving Mars .fpk WITHOUT extracting it, and reconcile it against the tree it was supposed to be built from. |
| [`audit_preset_fields.py`](audit_preset_fields.py) | Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |
| [`blocking_analysis.py`](blocking_analysis.py) | Blocking analysis, v2 -- v1 was useless: bare-name resolution marked half the codebase blocking (IsValid, SetText, Random all collided with some unrelated blocking method). |

### Launch

⛔ This mod is NOT PUBLISHED. `upload_preflight.py` FAILS today on the missing preview art (owner, `DECISIONS_OWED.md` 85).

| script | what its own header says |
|---|---|
| [`upload_preflight.py`](upload_preflight.py) | Upload preflight — run every portal guard clause locally, before the sitting. |
| [`pack_predict.py`](pack_predict.py) | Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6. |

<!-- END GENERATED TOOL ROWS -->

## Why the rows below are generated

A hand-kept list of N rows is a list that goes stale — quietly, because nothing fails when it does.
Each row's text is copied from the script's **own opening header**, and the row set is reconciled
**both ways** against `glob(tools/*.py)`: a new script with no row is RED, and a row naming a script
that no longer exists is RED. There is no exempt class. The cure for drift is always
`python tools/doccheck.py --regen`, never a hand edit — a wrong row is repaired **in the script's
header**, which is the only place a reader would look next.
