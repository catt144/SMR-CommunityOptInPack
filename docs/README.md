# docs/ — the map

Created 2026-08-12 by the `split-optins` chain (prompt 3), mirroring
`SMR-BugFixPack`'s tree so one set of habits serves both repos. **Human docs at
the root; everything an agent reads under `agent/`; everything spent under
`archive/`.** `python tools/doccheck.py` enforces this map — the root list
below is an allowlist checked in BOTH directions, so a new file at `docs/` root
is a red build until it is added here too.

```
docs/
  FUTURE_IDEAS.md         parking lot, NOT a backlog. Nothing in it is work
  README.md               this map
  agent/
    STATE.md              READ FIRST. Current state only, ≤60 lines
    WORKFLOW.md           process rules — commits, probe hygiene, todo discipline
    FIX_POLICY.md         what may be built, and how
    PROVENANCE.md         what came from where, at which sha — the port ledger
    bugs/                 defect/design truth — one file per entry
    facts/                engine behaviour — one file per fact
    reports/              reports, plans, specs, audits, surveys
    prompts/              the standing prompts + any live one-off
  archive/                spent. SESSION_LOG.md, retired prompts
```

## ⚠️ The two human playtest files live in the FIX PACK repo

`PLAYTEST_CHECKLIST.md` (the owner's test queue, the reporting protocol, and
**"Decisions waiting on you"**) and `PLAYTEST_HELP.md` (console facts, the
verified command table, fixture recipes) are **single-sourced in
`C:\Dev\SMR-BugFixPack\docs\`** and are NOT duplicated here.

**Why, decided at design time and sustained by the chain's QA gate:** the owner
plays ONE game with BOTH mods loaded (`agent/WORKFLOW.md`, "BOTH MODS
LOADED"), so two checklists would split one queue across two files and cost the
owner exactly the overhead the co-run model exists to remove. **An owner
decision from work in THIS repo still goes to that checklist**, never only into
an agent doc here.

This is the one place the split deliberately leaves a question unanswerable
from this repo alone. It is named rather than hidden: nothing about *build
state, policy, module records, the suite, the bans, or provenance* — the
questions a fresh session actually has to answer — lives in those two files.

## The two split folders

**`agent/bugs/` — one file per entry** (`D*.md` today: the eight modules plus
the Mod Options enable surface). `INDEX.md` is **generated**.

**`agent/facts/` — 53 fact files** (`EF-001` … `EF-053`) plus `_preamble.md`,
**copied whole from the fix pack @ `33d69f5` on 2026-08-12**. Engine facts
describe the GAME, so both mods need all of them; the two copies **diverge from
that date on** — see `_preamble.md` and `agent/PROVENANCE.md`. `INDEX.md` is
**generated**.

⚠️ **`INDEX.md` is generated in both folders and is never hand-edited.** Edit
the entry or fact file; doccheck regenerates the index and fails on any
difference. Generated files say so on line 1.

## Where new things go

- A **defect or module record** → a new file in `agent/bugs/`. Never a report.
- An **engine fact** → a new `EF-###.md` in `agent/facts/`, with its date.
  ⚠️ It probably belongs in the fix pack's copy too — carry it across and say
  so in both, or write down why it is this mod's alone.
- A **rule that binds future work** → `agent/WORKFLOW.md` or
  `agent/FIX_POLICY.md`, not buried in a report.
- A **report, plan, spec, audit or survey** → `agent/reports/`.
- A **prompt** → `agent/prompts/`; one-offs delete themselves when consumed.
- A **session leg** → `archive/SESSION_LOG.md` (append-only, newest first).
- A **decision the owner must make** → the FIX PACK's
  `docs/PLAYTEST_CHECKLIST.md` → "Decisions waiting on you" (see above).
- **Spent** anything → `archive/`, which is append-only and never edited.

⚠️ **Reports are not authority.** When a report disagrees with `agent/bugs/` or
`agent/facts/`, the entry wins — or the report is wrong and is corrected in the
same change that discovers it.
