# 03_Drones/ — the hub's drones, as a chain

Build 4 split into links so the work that does not touch the hub's Lua runs **now, while the
structure pass finishes**, and the link that must wait starts fully briefed instead of cold.

`DESIGN.md` is the owner's settled design, unchanged. It is reference, never fired.

| # | link | tag | attended? | what it drains |
|---|---|---|---|---|
| 2E | `2E_ENGINEFLIGHT_high.md` | high | no | **NEXT.** Owner redirect, 2026-09-23: our code keeps the pit launch, the stand-ready hold and the return; the engine paths every leg between them under stock commands only; we own the commands. Adds the console switch so link 3 can A/B it against the scripted flight |
| 3 | `3_FLIGHTLOOK_low.md` | low | **yes** | ⛔ **Waits for 2E.** The owner judges the flight by eye and tunes it: curves, heading, bank, heights, speed, launch, landing, work descent, a passing train, stations, hoods and tunnels. Records values and checks import survival |
| 4 | `4_HUB_high.md` | high | no | ⛔ Waits for the structure pass. The hub half in `20_TrainHub.lua`: dispatch on `TrackBroken`, the two-kind pending list and its persisted name, completion at the deadline, the save guard, `CanBeControlled`, the infopanel line and toggle |
| 5 | `5_SMOKE_medium.md` | medium | **yes** | `DESIGN.md` §5's smoke with the owner, and the train-construction question in §6. Records ETAs and the sitting |
| 6 | `6_QA_high.md` | high | no | Terminal adversarial backward QA in fresh context. Audits every handoff, samples claims against the code and logs, holds the folder-empty gate |

## Chain rules

- **Inbox/outbox.** A link ends by appending what the later links need into their own
  `## Notes from upstream` sections, committing, and **deleting its own file and striking its own
  row here in that same commit**. Nothing is handed over in chat or in memory. An empty folder
  (`DESIGN.md` and this README aside) is the done-condition, and the QA link holds that gate.
- **Route, never drop.** An out-of-scope finding goes to the link that owns it, to spec §10, or to
  `docs/PLAYTEST_CHECKLIST.md` as an owner ask with a recommendation. Defects go through
  `smr-bug-library`.
- **Order.** 2E then 3; both are independent of the structure pass. 4 waits for the
  structure pass to be out of `20_TrainHub.lua`. 5 follows 4. 6 is last, in fresh context, and the
  owner runs it on a different model from the links it audits.
- **Self-split** at a clean commit boundary into a continuation link that is a full chain member,
  rather than running to the edge of a context window. Say so in the notes.
- **Drift** (anything that went other than as briefed, however small) is appended to link 6's
  evidence list. A silently corrected instance is destroyed evidence.
- **Commits** name the link: `Drones chain L<n>: <what landed>`.

## Owner ruling OI-25, 2026-09-22

The owner approved the task's pending question: launch from and return to the pit floor,
offsetting both `Pitfloor` and `Pitrim` by entity-local `point(-310,180,0)`, then lifting through
that column to local z +10 m. The approval adopts L1's measured column; live flight clearance
still belongs to link 3.

## Owner redirect to engine pathing, 2026-09-23

The owner flew L2M2's `b84f106` and accepted it as a floor, not a finish: *"It is better now, still
not nearly as clean as vanilla but its useable."* They then redirected the design — *"besides our
launch and return parts the engine handles that pathing and we handle the commands"* — commissioned
as `2E_ENGINEFLIGHT_high.md`. The route topology (L2R) and OI-25 are unchanged.

The scripted flight is preserved at tag **`drones-scripted-flight-20260923`**, to snap back to if
the engine version disappoints. Restore the file alone with
`git checkout drones-scripted-flight-20260923 -- tools/devmods/train_hub/Code/30_TrainHubDrones.lua`.

The sitting's verdict, the owner's decisions, and every engine fact verified for 2E — each with a
falsifier, all re-read on the newly installed **1.1.1.405907** tree — are in
`docs/agent/reports/drones_chain/L3_FLIGHTLOOK_HYBRID_20260923.md`. Fleet scaling by load went to
`4_HUB_high.md`.
