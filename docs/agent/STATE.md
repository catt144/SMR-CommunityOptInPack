# Project State — pull; read it when a task, a prompt or the owner calls for status

Current only; history is newest-first in `docs/archive/SESSION_LOG.md`.
Module truth `agent/bugs/INDEX.md` · engine facts `agent/facts/INDEX.md` · doc map `docs/README.md`.
Pre-2026-08-31 STATE: `git show e8d8cee:docs/agent/STATE.md`.

## Now

- NOT PUBLISHED. The owner launched the fix pack alone on 2026-08-17 ("its not ready imo").
- Owner 2026-09-01, verbatim: "the opt in modules has not fully tested yet." Testing precedes
  launch. D02/D03/D04/D09 passed pre-split; D01/D06/D07/D12 are retired.
- Every shipping module still owes the `FIX_POLICY` §8 both-configuration test on the shipping
  build. Launch order and evidence: `agent/reports/READINESS_REVIEW_0831.md` §6. That plan predates
  1.1.0 and lacks a re-verification step. Upload preflight currently fails on preview art (OI-12).

## Build state — pulled, not stored

Live counts: `python tools/doccheck.py --emit-counts`. Installed build and fact groups:
`python tools/doccheck.py --emit-fingerprint`.

## Holds

- The two bans are in `FIX_POLICY.md`'s header; module freeze and measurement, in `CLAUDE.md`'s.
  Nothing in this mod is frozen (owner ruling 2026-09-18).
- The fix pack's kit-edit gate (checklist item 83) is dissolved (owner ruling 2026-09-18);
  `60_Probes_Opt.lua` needs no separate fix-pack sign-off. That gate's own record stays theirs.
- The game moved to 1.1.0 + DLC, build 24995074, on 2026-09-08. Archived trees are under
  `C:\Dev\SMR-SrcArchive`; fingerprint routing is `EF-083`. No module, probe, gate or test result
  in this repo has been re-verified on 1.1.0.

## Open owner decisions

Bodies are in `docs/PLAYTEST_CHECKLIST.md`. Open: OI-03, OI-04, OI-10, OI-17; launch: OI-11–OI-14.
Shared TestKit, EF-id allocation and a fix-pack feature remain in the fix pack's checklist
because they bind that repo.
