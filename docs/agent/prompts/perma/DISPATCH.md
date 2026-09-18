# Dispatch — live-issue triage

Standing prompt, adapted from the fix pack on 2026-08-31. Owner scope: issues after this mod is
live — a player report, field bug, or something noticed in play. This mod is not published; ordinary
development uses `WORK_PROMPT.md`. Written at `6f002cb`; start with `git log --oneline -10` and
`git pull` before trusting a named status.

This is an orientation, not a logbook. Results and status belong in entries, STATE and the owner
decision register. A task with a dedicated prompt switches to that prompt.

## Context and authority

This is an opt-in behaviour mod for Surviving Mars: Relaunched, standalone beside the Relaunched
Fix Pack. `CLAUDE.md` supplies the always-loaded rules; `docs/README.md` maps the tree;
`FIX_POLICY.md` governs code and heads with the two bans; `WORKFLOW.md` governs testing, records
and releases.

## Orient

1. Invoke `smr-orientation` and read `docs/agent/STATE.md`.
2. Invoke `smr-bug-library`; scan the bugs index and grep the facts index before opening a record.
3. If the job will launch the retail game, apply `WORKFLOW.md` "Probe hygiene" before any test.
4. Create the live work list at commit-and-verify granularity.

## Triage loop

1. Preserve the reported symptom, conditions and build separately from the proposed cause.
2. Search this mod's runtime code first, then the relevant entry and facts. Game-source citations
   use the archived tree for their named build under `C:\Dev\SMR-SrcArchive`.
3. Apply `WORKFLOW.md` "Records and rulings", "Testing checklist per module" and "Log review" to
   the proposed cause, route, controls, logs and negative results.
4. File the result through `smr-bug-library` or the destinations in `docs/README.md`. Out-of-scope
   findings are filed with their evidence and left unbuilt.

## If the issue requires a code change

- Module-freeze status comes from STATE; the ruling must exist before behaviour changes.
- Read the module, entry and cited facts in full. Apply `FIX_POLICY.md` §1–§7, including the
  enable path, declaring class, wrapper, save-safety and veto rules.
- Follow `WORKFLOW.md` "Per-module discipline", "Probe hygiene" and "Testing checklist per module".
  The parse sweep covers every edited Lua file; the TestKit A/B reaches production code, computes
  its expectation independently, and includes a vanilla control.
- Status vocabulary remains `tested-attended` or `tested-unattended`; a desk pass is
  `desk-verified`. The shipping claim of standalone behaviour requires both configurations.

## Route table

| task | destination |
|---|---|
| ordinary development, docs, tooling or launch prep | `WORK_PROMPT.md` |
| live attended playtest with both mods | fix pack `prompts/perma/GENERAL_USE_PROMPT.md` |
| whole-mod launch | STATE launch list, `WORKFLOW.md` release sections, fix-pack parked-reference restore |
| owner's mechanical pack/upload | fix pack `docs/UPLOAD_WORKFLOW.md`, after upload preflight |
| drone system | `DRONE_OVERHAUL_OPTIONS.md` and `SEED_LOGISTICS_HANDOFF.md`; currently parked |
| effort over about two sessions | `support/CHAIN_METHOD.md` |
| STATE size warning | `STATE_EVICTION.md` |

## Stops

- An owner ruling or attended observation is the next evidence.
- The next edit would touch a persisted name, contract identifier, frozen module or unavailable
  fixture.
- The effort exceeds one context; propose a chain.

## Close

Invoke `smr-session-close`. STATE changes only when current status changes and still passes its
admission door. Apply the kernel checks, push committed work, and name where filed work remains.
