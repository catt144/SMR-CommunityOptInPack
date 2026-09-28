# Train bay fixes: vanilla first, spawn on the siding, stacks that show their stock

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/15_TRAIN_BAY_FIXES_high.md` in a fresh
session rooted at `B:\Dev\SMR\SMR-OptInPack`. Authored at `4ac2685` plus the spec commit that
lands with this brief. Start with `git log --oneline -5`, `git status` and `git pull`.

## Authority

Spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §4.8, ruling 9 and its amendments
(grep `Hub dispatch is a train bay`, then read to the end of that item). Settled; do not reopen:
- The bay is the colony's stored-train pool. Extras are hidden from the player's count, up to 5
  per hub route, and recalled when idle. Empty extras are stored inside the save snapshot. The
  no-work pause is 2 game hours.
- ⚖️ **New, owner 2026-09-28: vanilla first.** Grep `operates as vanilla until it knows`. An extra
  deploys only when all four hold:
  - (a) every vanilla train on that line is out working;
  - (b) the shortfall has persisted a set time, 1 game hour to start and tunable;
  - (c) at most one extra per line per check;
  - (d) no deploys for the first 3 game hours after a load or a new game.

## The three defects (from the owner's sitting, 2026-09-28, log `Mars.exe-20260928-14.27.05`)

1. **Deploys ignore vanilla.** Four extras went out at the first tick after the stations were
   emptied. `B.LineRow` in `tools/devmods/train_hub/Code/70_TrainBay.lua` counts need purely from
   station shortfall minus vanilla trains. Implement the ruling. How you judge "out working" and
   "persisted" is yours; record your calls in the commit.
2. **Spawned trains are misplaced.** The owner saw them bunched and angled at the hub centre, not
   on the arm sidings where a parked train sits. This happened twice (this sitting's screenshot,
   and the 11.52.17 probe: "right in the middle of the hub kind off center"). Brief 13's desk
   check of archived `GetSpawnPoint` (`bay_smoke.py`, "spawn spot") predicted the siding exactly
   and was wrong. **The owner's observation governs.** Find why the live spawn differs, and make a
   deployed train stand where a parked train stands on its arm, facing out. Train movement through
   the hub is finished and owner-accepted (the orchestrator prompt, "Movement is FINISHED"). Do not
   change how trains move; this is only where a spawned train is placed.
3. **Hub stacks read empty while holding stock.** The owner: several resources show visually empty
   stacks while holding over 100. They call it "broken again". `20_TrainHub.lua` already has cargo
   column repair (grep `HealCargoColumns`). Find what breaks the stacks now, which may be the
   bay's spawning or storing at the hub or something else, and fix it at its cause.

For facts you might otherwise re-derive, read the brief 13 report,
`docs/agent/reports/TRAIN_HUB_BAY_20260928.md`, and spec §10. Treat both as claims.

## Done

- Each defect is fixed with a desk test in `tools/devmods/train_hub/tests/`. A mutation of the
  fix must make that test fail. For defect 2, the desk test alone does not prove placement,
  because the last desk proof was wrong: say what live reading would.
- `bay_smoke.py` and the other train hub smokes still pass. `python tools/doccheck.py` is GREEN
  before each doc commit.
- A report, `docs/agent/reports/TRAIN_BAY_FIXES_<date>.md`, with a one-line pointer under
  ruling 9. It holds an attended smoke of **about five steps**, written stream-first: TestKit
  slot 6 streams to the log. **Name each slot's function beside its number** ("slot 3 (bay
  read)"); the last sitting pressed slot 2 for slot 3. It is a smoke, not a battery.
- Keep a live todo list before any write, one item per commit-and-verify unit.

## Scope and stops

**In:** `70_TrainBay.lua`, the stack defect wherever its cause lives in the dev mod, their tests,
the report, the spec pointer. A TestKit slot change only if a reading needs it, in
`Code/80_AgentSlots.lua` of `B:\Dev\SMR\SMR-BugFixPack-TestKit`, a repo shared with the fix pack.
**Out:** the capacity upgrade (brief `14` audits it, in worktree
`.claude/worktrees/agent-af033497203ef0c8a`, so do not touch its section of `20_TrainHub.lua`),
train movement, and the distribution rules. Report outside findings without editing them.

Stop and report instead of continuing if:
- placing the train on its siding needs a change to how trains move;
- the stack fault's cause is in the capacity section brief `14` is auditing;
- the ruling cannot be met without a new persisted name (see `FIX_POLICY` §"The persisted-name
  inventory").

Claim limit: desk PASS means the mocked vanilla agrees, not that it works in the game.

References: `CLAUDE.md`, `docs/agent/FIX_POLICY.md` (header first), `docs/agent/WORKFLOW.md`,
skills `doc-editing` and `smr-bug-library`.

## Lifecycle

One-off. The orchestrator deletes or parks it, with its README row, once its sitting passes.
