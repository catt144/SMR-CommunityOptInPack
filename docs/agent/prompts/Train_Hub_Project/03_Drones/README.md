# 03_Drones/ — the hub's drones, as a chain

Build 4 split into links so the work that does not touch the hub's Lua runs **now, while the
structure pass finishes**, and the link that must wait starts fully briefed instead of cold.

`DESIGN.md` is the owner's settled design, unchanged. It is reference, never fired.

Closed 2026-09-25: `reports/drones_chain/L6_QA_20260925.md`, **PASS WITH CORRECTIONS**.
It holds the evidence bounds and routed C1–C6; spec §10 “Drones L5” carries the current owner
rulings, including door exits and OI-26 kept as built, which overtake the historical sections below.

## Chain rules

- **Inbox/outbox.** A link ends by appending what the later links need into their own
  `## Notes from upstream` sections, committing, and **deleting its own file and striking its own
  row here in that same commit**. Nothing is handed over in chat or in memory. An empty folder
  (`DESIGN.md` and this README aside) is the done-condition, and the QA link holds that gate.
- **Route, never drop.** An out-of-scope finding goes to the link that owns it, to spec §10, or to
  `docs/PLAYTEST_CHECKLIST.md` as an owner ask with a recommendation. Defects go through
  `smr-bug-library`.
- **Order.** The terminal audit is complete; no runnable link remains here. The project map owns the next brief.
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

Link 2E landed engine mode in `9a540dd` (report `L2E_ENGINEFLIGHT_20260923.md`): stock
`FlightGoto` legs between our pit ends, the handoff held by a queued stock `WaitUninterruptable`,
`SetHubDroneMode` as the console switch. Engine legs and holds now survive a save; `OI-26` asks
the 7 m ride ruling.

## Link 4 landed, 2026-09-23

The hub half is in `b556035` on `b1f62be` (report `L4_HUB_20260923.md`): the pending list
`SMROptIn_track_work`, dispatch on the hub-rooted graph, completion at the outstanding cost, the
fleet by vanilla's load word, the destroyed-hub despawn, the control wrap, the panel toggle, and
the flight's adoption of a loaded Wasp. **Restart or reload before the sitting:** the owner's
running game took an uncommitted state that made the fleet balance resources between stations;
the committed code admits only a far station's maintenance requests. The Blender clearance at
L3's settled lane measures negative at `RingPillar_4` (5 cm) and on the scripted connector-1
transfer (64 cm); the receipt bounds the tagged flight only. Link 5's notes carry the sitting.
