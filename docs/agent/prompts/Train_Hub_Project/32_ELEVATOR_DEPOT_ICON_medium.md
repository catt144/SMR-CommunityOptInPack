# 32 — The Elevator Depot's icon (build, small)

**Fire with:** `task docs/agent/prompts/Train_Hub_Project/32_ELEVATOR_DEPOT_ICON_medium.md` in a
fresh session rooted at `B:\Dev\SMR\SMR-OptInPack`, **after brief `30` closes** (30's upgrade edits
the same depot template). Reasoning: medium (a render and an editor save, judged by the owner).

## Authority and outcome

The owner, 2026-10-02, with a screenshot of the build menu's Elevator Depot (dev) tile: *"we need
to get its icon to match its own icon in the build menu"* (spec
`docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md` §11, grep `the depot's icon`). The tile
shows a pale concept render from the design pass, not the depot as built and painted in brief 28.
Outcome: an icon rendered from the finished depot (the three pads with the 75 % elevator, the colony
palette, brief 28's paint), used wherever the depot shows an icon: the build menu and its infopanel.
Done when the owner has passed the render by eye and seen the icon in game.

## What is known

- Brief 28's renders and paint live in `B:\Dev\SMR\SMR-Assets` (Assets `635022e`..`8b53ab3`;
  report `docs/agent/reports/ELEVATOR_DEPOT_PAINT_20261001.md`). The pipeline is that repo's.
- The depot dev mod is `tools/devmods/elevator_station/`; its template is generated from the Mod
  Editor's save (`Code/BuildingTemplate/*.generated.lua`). Edit the source and have the owner save;
  never hand-edit generated output. The hub's own icon is the precedent to match in size and style.

## Scope and method

In: the depot's icon. Out: the depot's name and description (the move brief `34` rewrites them),
its behaviour, the hub. `git log --oneline -5` and `git pull` first; authored at `58ebf7e`+. Use the
todo tool before any write. Prototype first: show the owner a render quickly, then iterate by eye.
Write the owner's Mod Editor steps if a save is needed. The in-game check is a glance at the build
menu and the infopanel. References: `CLAUDE.md`, `docs/agent/WORKFLOW.md`, `docs/agent/FIX_POLICY.md`;
skill `doc-editing` for doc edits.

## Stops

1. Brief `30` has not closed, or the depot template has uncommitted changes from another session.

## Lifecycle

One-off; the orchestrator deletes it when done.
