# Arboretum — independent audit of the D19 test build, then close it

One-off. Authored 2026-10-04 at `35020f2`. Delete this file and its row in
`docs/agent/prompts/README.md` in the commit that closes the work.

## The owner's decision

Owner, 2026-10-03: build an Arboretum test module (D19) and ship it **after launch**; it lives in
the excluded `staging/` workbench until promoted. The mod launched 2026-10-04. Owner, 2026-10-04:
this audit runs on a model the owner selected, different from the build's executor (the build
report's close-out names that executor). That selection settles independence; do not re-flag it.

The build brief `ARBORETUM_BUILD_high.md` says nothing enters the record unaudited. That was
breached once: `0ff4a85` committed the build unaudited (its message says so) and `78eed20` moved
it into `staging/`. This audit is the review the record still owes. Its subject is **committed
HEAD**, not a working diff — the report's "Resume" paragraph predates both commits and is stale.

## End state

- An audit verdict, appended as an `## Independent audit` section to
  `docs/agent/reports/ARBORETUM_BUILD_20261003.md`: each claim checked, the command that checked
  it, and PASS / FINDING. The report's `Live work` and `Resume` text rewritten to the true state.
- On PASS: the seven boot logs in `docs/archive/arboretum_20261003/` (`*.log`, ignored by
  `.gitignore`, present on disk, never committed) force-added with `git add -f` by exact path.
- `ARBORETUM_BUILD_high.md` and its map row deleted in the closing commit, and this prompt with
  its row in the same commit. Pushed.
- The auditor's model and effort recorded at close-out from Codex's own session record or stdout
  `model:` line, never from this brief.

Completion evidence: `git log` shows the audit commit(s); `git ls-files docs/archive/arboretum_20261003/`
lists the logs; `python tools/doccheck.py` GREEN; `git status --short` clean of your paths.

## Live work

1. Audit the build (claims below) → report section. One commit.
2. Record the evidence: force-add the logs (PASS only) with the report's evidence table reconciled.
3. Close: rewrite Live work/Resume, delete both one-off prompts and their map rows, doccheck, push.

Keep the list in your todo tool; one item in progress.

## What to audit

Judge the approach yourself. These are the claims, each a claim until one check clears it:

- **Module behaviour.** `staging/Code/Opt_Arboretum.lua`, `staging/Data/BuildingTemplate/SMROptInArboretum.lua`
  and its generated class: off by default, no vanilla method replaced, Seeds lock and
  NoTerraforming lock, one per dome, native consumption/coverage only. The report's source table
  cites build **1.1.1.406343** lines under `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/`;
  spot-check the load-bearing ones there (`grep -n`, not the report's numbers).
- **Save contract.** D19 and `docs/agent/FIX_POLICY.md` §"The persisted-name inventory" rows for
  this module agree with the names the code and template actually write. Both bans
  (`FIX_POLICY` header) hold.
- **The move.** `git diff -M 0ff4a85 78eed20 --stat` shows the code file moved unchanged but the
  template file changed (2 lines). Decide whether that changes runtime behaviour or only identity.
- **Desk evidence.** `python staging/tools/arboretum/deskcheck.py`,
  `python staging/tools/arboretum/generate.py --check`, `python tools/parsecheck.py`. Read the
  deskcheck enough to judge whether a broken module could pass it.
- **Boot evidence.** `python staging/tools/arboretum/read_boots.py` against the seven logs; confirm
  it would fail on a missing positive marker or a `[LUA ERROR]` (scope the check so contrary
  evidence could fail it). Reconcile the report's five-leg table and two retained failed attempts
  against the files.
- **Sitting slots.** `staging/tools/arboretum/slots.lua.txt` against the report's sitting table:
  each slot does what the owner is told it does, refuses where the report says, writes no object
  fields. Callbacks have never run in a loaded game; desk reading only.
- **Path drift.** The report still cites `tools/arboretum/...`; the files are under `staging/`.
  Correct the report's paths. D19 already uses the staging paths.

## Scope

In: the D19 module, its staging files and tools, its report, D19, its FIX_POLICY rows, the boot
logs, and the two one-off prompts' lifecycle.
Out: gameplay acceptance, Seeds-per-sol, footprint and category (OI-47/OI-48, the owner's ck223
sitting in the fix pack's checklist); promotion out of `staging/`; the outbox entry; anything in
`B:\Dev\SMR\SMR-BugFixPack` (its staged `KIT_SLOT_HOLDER`/`SMRTK.md`/`doccheck.py` changes belong
to another session). Report outside findings; do not edit them.

## Findings

A finding in records, paths or evidence wording: correct it in this audit and say so in the
commit. A finding that would change module behaviour: do not fix it — `CLAUDE.md`'s header wants an
owner ruling for a behaviour change. Record it in the report as a FINDING with its falsifying
command, leave the logs uncommitted and the build prompt live, and stop.

## Stops

- A behaviour finding (above).
- `read_boots.py` or the deskcheck fails at HEAD.
- A save-contract name in code that is absent from the persisted-name inventory.

## Claim limits

Not supported: "Arboretum tested", "accepted", or any Seeds-per-sol figure. Supported: "audited
at `<sha>`; menu-load and desk evidence verified; gameplay NOT RUN (ck223 owed)". D19's tag stays
as it is unless its own vocabulary says an audited menu-load build moves it; check
`docs/agent/bugs/INDEX.md` before touching it.

## References

Skills: `smr-orientation`, `smr-bug-library`, `doc-editing`, `smr-session-close`. House rules
`CLAUDE.md`; process `docs/agent/WORKFLOW.md`; code `docs/agent/FIX_POLICY.md`, its header first.
Commit with exact pathspecs; recheck shared paths before writing.
