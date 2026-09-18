# Work prompt — start here for ordinary work on this mod

Standing prompt for module design or changes, investigation, documentation, tooling and launch
preparation. Live field issues use `DISPATCH.md`; attended play uses the fix pack's
`GENERAL_USE_PROMPT.md`. Written 2026-08-31 at `6f002cb`; start with
`git log --oneline -10` and `git pull` before trusting named status.

This is an instruction surface, not a logbook. Results and status go to their durable homes.

## Context and authority

This is an unpublished opt-in behaviour mod for Surviving Mars: Relaunched, standalone beside the
Relaunched Fix Pack. Live counts come from `python tools/doccheck.py --emit-counts`. `CLAUDE.md`
supplies the always-loaded rules and two bans; `docs/README.md` maps the tree; `STATE.md` carries
current status and holds.

## Orient

1. Invoke `smr-orientation` and read STATE.
2. Invoke `smr-bug-library`; scan the bugs index and grep the facts index before opening a record.
3. Create a live work list at commit-and-verify granularity, with one item in progress.
4. If the job will launch retail, apply `WORKFLOW.md` "Probe hygiene" before any test.

## Route by work type

| work | governing home |
|---|---|
| module behaviour or a new module | `FIX_POLICY.md` §1–§8; STATE supplies freeze status |
| drone work | `DRONE_OVERHAUL_OPTIONS.md`, `SEED_LOGISTICS_HANDOFF.md`, and the current owner decisions; D06 is parked |
| engine investigation | archived Src for the cited build; `smr-bug-library` for a proved fact |
| documentation | `doc-editing` and `docs/README.md` |
| prompt or brief | `prompt-authoring` |
| tooling | `tools/README.md`; provenance ledger until its queued dissolution |
| launch preparation | STATE launch list, `WORKFLOW.md` release sections, upload preflight, fix-pack parked-reference restore |
| effort over about two sessions | `support/CHAIN_METHOD.md` |
| STATE size warning | `STATE_EVICTION.md` |

## Owner boundary

Design-flavoured calls belong to the owner: module scope or semantics, defect-versus-rebalance,
freeze changes, contract-name changes, uploads, and player-facing wording. Present neutral options
with measured trade-offs, use the owner-decision route in `CLAUDE.md`, and stop at the decision.

## Code-change loop

1. Confirm the game process is absent. Read the module, entry and cited facts, then enumerate the
   target's shipped call sites and reachability.
2. Apply `FIX_POLICY.md`: least-invasive technique, fail-safe enable path, declaring-class and
   Require discipline, save-safety layer, foreign-object inertness and per-call veto.
3. Parse every edited Lua file. Run the applicable desk instruments from `tools/README.md`.
4. Build the shared-TestKit A/B under `WORKFLOW.md` "Testing checklist per module".
5. Update the entry and code together. A status flip or measured verdict carries the probe-sweep
   receipt and its archived log. Apply the kernel checks, then push what was committed.

`tested-attended` means the owner witnessed the game; `tested-unattended` is limited to
instrument-readable behaviour. Desk simulation is `desk-verified`, not an in-game verdict.

## Investigation and filing

Apply `WORKFLOW.md` "Records and rulings", "Testing checklist per module", "Log review", "Cheats
on playtest saves" and "Both mods loaded" to investigations.

Records and facts use `smr-bug-library`; reports and session legs use `docs/README.md`; future
duties use `doc-editing`'s placement test. Out-of-scope findings are filed, not built.

## Stops

- The next step is an owner ruling, attended action, or unavailable fixture.
- The edit touches a persisted name, registration id, mod id, log tag, or frozen behaviour.
- Current Src contradicts a fact that must be corrected before the work can rely on it.
- The effort exceeds one context; propose a chain.

## Claims bounded by evidence

- In-game status requires a retail run; unattended work cannot claim a screen event.
- Standalone behaviour requires the both-configuration ship test in `FIX_POLICY.md` §8.
- Save safety requires the current persisted-name census and the entry's §3a shape statement.
- Probe totals are labelled as the shared suite and come from the emitting command.

## Close

Invoke `smr-session-close`. STATE changes only when the current kernel changes and passes its
admission door. Apply the kernel checks, push committed work, and name where filed work remains.
