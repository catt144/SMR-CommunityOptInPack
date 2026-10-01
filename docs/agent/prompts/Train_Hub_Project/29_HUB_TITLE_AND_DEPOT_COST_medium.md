# Brief 29 — the hub's long-title fix and the depot's cost proposal · _medium

## Authority and outcome

Two small jobs the owner ruled on 2026-10-01 (spec §10's and §11's last blocks):

1. **The hub's long-title fault, fixed now.** Brief 27 found and fixed it in the Elevator Depot
   (`1122115`: a true ceiling plus a 2-unit guard, where the hub's floored `math.ceil` lost a line at
   another panel scale; engine integer division, EF-116). It reported, without fixing, that the hub's
   own `fit_title` in `tools/devmods/train_hub/Code/45_TrainDistributionUI.lua` carries the same fault
   (`reports/ELEVATOR_DEPOT_WIRING_20261001.md`, "Reported, not fixed"). Port the fix to the hub.
   **Done when** the hub's `fit_title` gives the depot's answers and the hub's smokes pass.
2. **The depot's construction cost, proposed.** The owner: a depot half costs **less than vanilla's
   elevator**. Read vanilla's elevator cost from source, propose numbers per half with your reasons
   (it is a smaller, cargo-only elevator, one pair per colony, needing the underground unlocked), and
   put them in your report for the owner's yes. **Done when** the proposal is in the report. Do not
   write it into the template: brief `28` holds the depot's Mod Editor session, so the numbers go to
   whichever brief next saves the depot, after the owner's yes.

**Yours to decide:** how the port is shaped (shared helper or matching copy) and how the proposal is
reasoned. Say which and why in the commit message.

## Start

Authored at the commit that adds this file. Run `git log --oneline -3` and `git pull`; keep a live
todo list before any write, one item per commit-and-verify unit, one in progress. Build must be
**25579348** (`python tools/doccheck.py --emit-fingerprint`); cite source from that build's archived
tree under `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive`. Read the wiring report's "long title" section and
`1122115`'s diff first.

## Evidence (claims, each cleared by one check)

- The depot's fix and its 60-case smoke against the hub's arithmetic: `6da522f`, `1122115`.
- Integer division in the engine's Lua: `docs/agent/facts/` EF-116; a desktop Lua run does not prove it.
- Further records: `docs/agent/bugs/INDEX.md`, `docs/agent/facts/INDEX.md`.

## Scope

- In: the hub's `fit_title` and its smoke; the cost proposal in the report.
- Out: the depot's files (brief `28` is live in them); any other hub behaviour; writing the cost.

## Stops — report instead of continuing if

1. The hub's fix needs more than `fit_title` and its callers.
2. The installed build is no longer 25579348.

## Claim limits

The title fix is desk-verified: claim its smokes, not an in-game look (OI-38 carries the in-game
glance). The cost is a proposal until the owner says yes.

## Hand back

Report `docs/agent/reports/HUB_TITLE_AND_DEPOT_COST_20261001.md` (dated later if it slips): commits,
the port, the commands and what they printed, the cost proposal with vanilla's figures and citations,
what you did not do. Commit with pathspecs. Update this brief's row in this folder's `README.md`; do
not delete or move this brief. Skills: `smr-bug-library`, `doc-editing`, `smr-session-close`. House
rules `CLAUDE.md`, code `docs/agent/FIX_POLICY.md`.
