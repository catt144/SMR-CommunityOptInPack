# tools/ — what each script is, and what its output does NOT license

The map of this repo's instruments. **Route from here; read the script's own header before you
quote it.**

⛔ **Every instrument is an over-reporter.** Adjudicate a row by reading the source line it cites,
never by its count (the readiness tooling ledger below). A tool that finds 30 hits has found
30 candidates, not 30 defects.

⛔ **A desk PASS is "desk-verified", never "verified."** Nothing in this folder launches the retail
game. `tested-attended` / `tested-unattended` are claims about a real game run and no script here
can earn one (`WORK_PROMPT.md` "Claims bounded by evidence").

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

*25 scripts, every `tools/*.py` on disk. This block is GENERATED: a row's text is copied from the script's own header, so a wrong row is repaired in the script, never here.*

### Repo gates, and the falsifiers that keep them honest

The pre-commit hook runs `doccheck.py`; the five `*_selftest.py` are required BY it, so a gate whose falsifier stops firing is itself RED. A gate that has only ever been seen passing on a clean tree has not been tested.

| script | what its own header says |
|---|---|
| [`doccheck.py`](doccheck.py) | doccheck.py — the structure checker (DOC_RESTRUCTURE_SPEC.md §5). |
| [`rule_headers_selftest.py`](rule_headers_selftest.py) | Falsifier for doccheck's RULES HEADERS / RULE PLACEMENT gate. |
| [`ck170_selftest.py`](ck170_selftest.py) | Falsifier for doccheck's STATE byte budget, the standing-prompt line budget and the skills mirror, on disk copies. |
| [`counts_selftest.py`](counts_selftest.py) | Falsifier for doccheck's --emit-counts block: counts follow the source, a RED run withholds the block, and --regen never writes STATE. |
| [`prompt_map_selftest.py`](prompt_map_selftest.py) | Falsifier for doccheck's PROMPT MAP gate: one broken fixture per red it claims to raise. |
| [`repair_pass_selftest.py`](repair_pass_selftest.py) | Falsifier for doccheck's --emit-fingerprint build routing and pack-ignore parity, and home of the scratch-copy loader the other falsifiers import. |

### Generated-document machinery

The splitters own `bugs/INDEX.md` and `facts/INDEX.md`. ⛔ Never run either with `--write`: that re-runs the one-time migration from a retired pre-split document. `--regen` is the cure for drift.

| script | what its own header says |
|---|---|
| [`split_bugs.py`](split_bugs.py) | split_bugs.py — docs/BUGS.md -> docs/agent/bugs/ (DOC_RESTRUCTURE_SPEC §3a, as amended by the ROUTE (a) decision in the docs-restructure chain's prompt 2). |
| [`split_facts.py`](split_facts.py) | split_facts.py — docs/agent/ENGINE_FACTS.md -> docs/agent/facts/ (DOC_RESTRUCTURE_SPEC §3b, executed by the docs-restructure chain's prompt 3). |

### Desk instruments — what a module does without launching the game

The L-series. ⛔ A desk PASS is "desk-verified", never "verified" (`WORK_PROMPT.md` "Code-change loop"): none of these launches the retail game. Every one is an over-reporter — adjudicate a row by reading the source line it cites, never by its count.

| script | what its own header says |
|---|---|
| [`l2_reload_sim.py`](l2_reload_sim.py) | Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port. |
| [`l3_save_footprint.py`](l3_save_footprint.py) | Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port. |
| [`l4_player_surfaces.py`](l4_player_surfaces.py) | Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port. |
| [`l5_containment.py`](l5_containment.py) | Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port. |
| [`l6_promise_map.py`](l6_promise_map.py) | Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port. |
| [`l6_reachability.py`](l6_reachability.py) | Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port. |
| [`l7_env_map.py`](l7_env_map.py) | L7 (environment & namespace) — the global map, taken from the COMPILER. |
| [`l8_hostile_input.py`](l8_hostile_input.py) | Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port. |

### This mod's own code gates

Run by `doccheck` as well as by hand; the allowlists live beside the detectors, with a source citation per entry (`FIX_POLICY` §2).

| script | what its own header says |
|---|---|
| [`harvest_wrap_targets.py`](harvest_wrap_targets.py) | Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port. |
| [`parsecheck.py`](parsecheck.py) | Provenance: ported from SMR-BugFixPack @ 8754e00 on 2026-09-18, unchanged; its dated history is the fix pack's. |

### Reading the shipped game by hand

⛔ Cite a line only with the build it was read on, from the archived tree for that build (`C:\Dev\SMR-SrcArchive`). The game moved to 1.1.0 on 2026-09-08 and overwrote `ModTools\Src`.

| script | what its own header says |
|---|---|
| [`flpk_extract.py`](flpk_extract.py) | FLPK (Surviving Mars: Relaunched .fpk) extractor, v2. |
| [`pack_list.py`](pack_list.py) | List a Surviving Mars .fpk WITHOUT extracting it, and reconcile it against the tree it was supposed to be built from. |
| [`audit_preset_fields.py`](audit_preset_fields.py) | Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port. |
| [`blocking_analysis.py`](blocking_analysis.py) | Blocking analysis, v2 -- v1 was useless: bare-name resolution marked half the codebase blocking (IsValid, SetText, Random all collided with some unrelated blocking method). |

### Cross-repo sync with the fix pack

Fired by `docs/agent/prompts/perma/KNOWLEDGE_SYNC_PASS.md` when the owner has changed the main pack and wants to know what lands here. ⛔ Read-only in BOTH repos, and it decides nothing — its `LOCAL_ADAPTATIONS` and `LAST_SYNC` constants are the retired prose port ledger in the only form that cannot go stale, because the thing that reads them is the thing that checks them.

| script | what its own header says |
|---|---|
| [`sync_from_fixpack.py`](sync_from_fixpack.py) | Cross-repo sync helper: what has the fix pack got that this repo needs? |

### Launch

⛔ This mod is NOT PUBLISHED. `upload_preflight.py` FAILS today on the missing preview art (owner, `PLAYTEST_CHECKLIST.md` OI-12).

| script | what its own header says |
|---|---|
| [`upload_preflight.py`](upload_preflight.py) | Upload preflight — run every portal guard clause locally, before the sitting. |
| [`pack_predict.py`](pack_predict.py) | Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port. |

<!-- END GENERATED TOOL ROWS -->

## Why the rows below are generated

A hand-kept list of N rows is a list that goes stale — quietly, because nothing fails when it does.
Each row's text is copied from the script's **own opening header**, and the row set is reconciled
**both ways** against `glob(tools/*.py)`: a new script with no row is RED, and a row naming a script
that no longer exists is RED. There is no exempt class. The cure for drift is always
`python tools/doccheck.py --regen`, never a hand edit — a wrong row is repaired **in the script's
header**, which is the only place a reader would look next.

## The 2026-08-31 readiness tooling port (donor @ `bec2e06`)

The fix pack kept building after the split; this pass carried across what it
grew, measured against THIS tree. Report: `agent/reports/READINESS_REVIEW_0831.md`.
Donor sha for every row: `SMR-BugFixPack` @ `bec2e06d` (v5 closed, 2026-08-30).

| artifact here | how | what changed / what it proves here |
|---|---|---|
| `tools/doccheck.py` (v5) | ADAPTED | four donor checks carried: STATE **byte** budget (9 KiB warn / 18 KiB hard / 200 B line), `tested-attended`/`-unattended` vocabulary, `LOAD_ORDER_RULES` (this repo's two shared-symbol orders), `wrap_targets_check`. `GENERAL_USE` cap kept, N/A |
| `tools/harvest_wrap_targets.py` | ADAPTED | `SMROptInPack.Require` needle; allowlist emptied then refilled with the 3 sites verified benign at Src 2026-08-31 (`Opt_DroneOverhaul` ×2, `Opt_MultipleSuns`) |
| `tools/upload_preflight.py`, `pack_list.py`, `flpk_extract.py`, `l7_env_map.py` | VERBATIM | generic; preflight FAILS here on the missing `image` (the launch gate) |
| `tools/pack_predict.py` | ADAPTED | `CONTENT_PREFIX` = this mod's id |
| `tools/l2_reload_sim.py` | REWRITTEN | the donor's is bound to four DataPatch fixtures (N/A: no `Opt_*` calls DataPatch); this one loads the whole `code` list twice and checks registration; `--core --expect-doubling` is its falsifier (pre-guard core `2cedf7d~1` REPRODUCES the 08-17 doubling) |
| `tools/l3_save_footprint.py` | ADAPTED | `NAMED_STATE` matches BOTH prefixes (persisted names keep `SMRFixPack_`), rows labelled by the token found; `REGISTER`/`resolved` renamed |
| `tools/l4_player_surfaces.py`, `l5_containment.py`, `l6_reachability.py`, `audit_preset_fields.py` | ADAPTED | token rename only; donor `Fix_*` citations in comments left as its history |
| `tools/l6_promise_map.py` | ADAPTED | token rename + `Opt_` added to the filename derivation; census 5 (site fix list) N/A while parked |
| `tools/l8_hostile_input.py` | ADAPTED | token rename; module trio = `Opt_ClassicRockets`, `Opt_DroneStatDials`, `Opt_NoHomeless`; control case vetoes `ClassicRockets` |
| `tools/l8_deference_map.py` | NOT PORTED | quarantined in the donor (TA-3) until repaired there |
| `docs/agent/support/CHAIN_METHOD.md` | VERBATIM (re-sync) | method, not content — §5a and the commit-the-folder rule arrive |
| `docs/agent/facts/` | VERBATIM (re-sync) | 7 donor-updated shared facts taken whole (EF-008/023/039/051/054/055/056); EF-057…068 added; this repo's old EF-057/058 are now EF-061/062 (their donor ids). ⛔ ids are allocated by the fix pack from here on (the `smr-bug-library` skill) |
| `docs/agent/prompts/perma/DISPATCH.md`, `STATE_EVICTION.md` | ADAPTED | this repo's paths, bans, route table; the playtest prompt stays single-sourced in the fix pack |
| `docs/agent/WORKFLOW.md`, `FIX_POLICY.md` | ADAPTED | rules carried, each marked with its donor date and this repo's state at adoption (listed in the report §4) |
| `.claude/settings.json` | ADAPTED | the donor's read-only git allowances, plus this repo's |

**Hardened the same evening (2026-08-31, after a second session hit it):** every
tool forces UTF-8 stdout (the Windows console is cp1252 and the tools print
⛔/⭐/§ — `l3` died on its own §7 line), the multi-line PORTED headers shrank to
one provenance line pointing here, docstrings and printed labels now say "this
mod" rather than "the pack", and `l3 --src` refuses a path with no `Lua/` under
it BEFORE printing (a wrong path had produced a silent all-absent census).

**Not carried, by decision:** the donor's sweep-chain folders and lens reports
(they are ITS evidence; this repo's lens sweep, if ever run, produces its own),
`GENERAL_USE_PROMPT.md` / `RELEASE*.md` / `POST_UPLOAD_CLOSE.md` /
`PUBLIC_SURFACE_SWEEP.md` / `SITE_AUDIT.md` (all bound to the fix pack's live
listing and site; this mod's launch session adapts them when it exists),
`UPLOAD_WORKFLOW.md` (owner file, single-sourced there like the playtest files).
