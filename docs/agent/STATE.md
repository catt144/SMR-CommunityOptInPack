# Project State — pull; read it when a task, a prompt or the owner calls for status

Current only; history is newest-first in `docs/archive/SESSION_LOG.md`.
Module truth `agent/bugs/INDEX.md` · engine facts `agent/facts/INDEX.md` · doc map `docs/README.md`.
Pre-2026-08-31 STATE: `git show e8d8cee:docs/agent/STATE.md`.

## Now

- NOT PUBLISHED. The owner launched the fix pack alone on 2026-08-17 ("its not ready imo").
- Owner 2026-09-01, verbatim: "the opt in modules has not fully tested yet." Testing precedes
  launch. D01 is `tested-attended`; D02/D03/D04/D09 passed pre-split; D06/D07/D12 are retired.
- Every shipping module still owes the `FIX_POLICY` §8 both-configuration test on the shipping
  build. Launch order and evidence: `agent/reports/READINESS_REVIEW_0831.md` §6. That plan predates
  1.1.0 and lacks a re-verification step. Upload preflight currently fails on preview art (OI-85).

## Build state — pulled, not stored

Live counts: `python tools/doccheck.py --emit-counts`. Installed build and fact groups:
`python tools/doccheck.py --emit-fingerprint`.

## Holds

- The two bans are in `FIX_POLICY.md`'s header; module freeze and measurement, in `CLAUDE.md`'s.
  D09 `DroneStatDials` is the sole live unfrozen module.
- The game moved to 1.1.0 + DLC, build 24995074, on 2026-09-08. Archived trees are under
  `C:\Dev\SMR-SrcArchive`; fingerprint routing is `EF-083`. No module, probe, gate or test result
  in this repo has been re-verified on 1.1.0.

## Open owner decisions

Bodies are in `docs/DECISIONS_OWED.md`. Open: OI-01, OI-03, OI-04, 84, 85 and 89–97. Items 94 and
92 remain gated on a 1.1.0 rebase. The launch items are dormant while this mod is not launching,
and their source citations predate 1.1.0. Shared TestKit, EF-id allocation and a fix-pack feature
remain in the fix pack's checklist because they bind that repo.
