# Project State — pull; read it when a task, a prompt or the owner calls for status

Current only; history is newest-first in `docs/archive/SESSION_LOG.md`.
Module truth `agent/bugs/INDEX.md` · engine facts `agent/facts/INDEX.md` · doc map `docs/README.md`.
Pre-2026-08-31 STATE: `git show e8d8cee:docs/agent/STATE.md`.

## Now

- LIVE since 2026-10-04 on Paradox Mods (`pdx_id` 161911) and the Steam Workshop (`steam_id`
  3813142702), tag `optin-v1.0.2`. What is live: `docs/agent/reports/STORE_CARD_LIVE.md`.

## Build state — pulled, not stored

Live counts: `python tools/doccheck.py --emit-counts`. Installed build and fact groups:
`python tools/doccheck.py --emit-fingerprint`.

## Holds

- The two bans are in `FIX_POLICY.md`'s header; module freeze and measurement, in `CLAUDE.md`'s.
  Nothing in this mod is frozen (owner ruling 2026-09-18).
- The fix pack's kit-edit gate (checklist item 83) is dissolved (owner ruling 2026-09-18);
  `60_Probes_Opt.lua` needs no separate fix-pack sign-off. That gate's own record stays theirs.

## Open owner decisions

Shared TestKit, EF-id allocation and a fix-pack feature remain in the fix pack's checklist
because they bind that repo.
