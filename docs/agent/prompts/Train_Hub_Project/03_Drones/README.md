# 03_Drones/ — the hub's drones, as a chain

Build 4 split into links so the work that does not touch the hub's Lua runs **now, while the
structure pass finishes**, and the link that must wait starts fully briefed instead of cold.

`DESIGN.md` is the owner's settled design, unchanged. It is reference, never fired.

| # | link | tag | attended? | what it drains |
|---|---|---|---|---|
| 3 | `3_FLIGHTLOOK_low.md` | low | **yes** | **NEXT.** The owner judges the rebuilt motion and tunes the under-deck flight by eye: curves, heading, bank, heights, speed, launch, landing, work descent, a passing train, stations, hoods and tunnels. Records values and checks import survival |
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
- **Order.** 3 is independent of the structure pass. 4 waits for the
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

## Link 3 blocked a third time, 2026-09-22 (fluidity)

The owner flew L2M's build (`74b1e4a`): *"Its studdered very bad coming out, the flight path is
sorta better but still pretty sharp on the angles and its kinda glitchy / suttery when it lands to
do the repair sequence. I needs the be, natural, fluid, and respemble flight."* The route is still
not in question. Link 2M2 reopened the motion verdict and landed as `d77efa4` (the engine flies
the chords from a game-time driver; report `docs/agent/reports/drones_chain/L2M2_FLUIDITY_20260922.md`);
link 3 resumes on that build.
