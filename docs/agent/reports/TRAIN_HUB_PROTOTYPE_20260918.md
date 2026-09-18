# Train hub prototype — pre-boot predictions and go/no-go record

**Authority.** Owner ruling 2026-09-18 (OI-10): “prototype B via 3a”, interchange only. The
prototype answers whether one station-class hub can carry at least three ordinary linear routes;
it does not test cargo routing or train route-switching. Appearance is deliberately unfinished.
Disposable saves only.

**Build call, before boot.** Commit `dfb8052` keeps the prototype in a separate dev mod under
`tools/prototypes/train_hub/`, outside the shipping mod's code list and excluded from its package.
It reuses `TrainStationLargeCCP3` so station storage and train surfaces remain vanilla, while Lua
computes three opposite connector pairs and their train movement points. Class and mod ids are
prototype-only and must not touch a kept save.

## Fixture to build

`<<PENDING-RUN>>` One prototype hub H and six vanilla end stations arranged as three independent
through-routes A–H–A′, B–H–B′ and C–H–C′, one route per opposite connector pair. Each route gets
one train. The named B and C ends start with zero Metals; A is stocked through the prepared setup
action. Stations must be far enough apart that drones and shuttles cannot carry between ends.
Both shipping mods and the TestKit stay loaded; neither shipping mod touches trains.

## Predictions written before boot

All timings below are planned operator limits, not measurements. Stop on the first unexpected
taint, Lua error, assert, or mutation and do not rerun for a preferred verdict.

1. **Boot status — Scratch / `SMRTK_ACTION action=slot_scratch`.** Expected `status=OK`; its DUMP
   names both repository heads, the clean stale-probe sweep, game build, map, taint read and
   `eligibility=UNAVAILABLE:sandbox`. First-screen witness: no console log overlay. Normal
   `<<PENDING-RUN>>` 10 seconds; abort `<<PENDING-RUN>>` 30 seconds.
2. **Computed-spot spike — slot 2 / `SMRTK_ACTION action=slot_2`.** With H selected, expected
   `status=OK`, `connectors=6`, six distinct connector hexes, six outward direction hexes and six
   valid connector elements. Before tracks, connected count may be zero; after the fixture it must
   be six. First-screen witness: the selected object is “DEV Train Hub Prototype”. Normal
   `<<PENDING-RUN>>` 10 seconds; abort `<<PENDING-RUN>>` 30 seconds.
3. **Fixture read — slot 1 / `SMRTK_ACTION action=slot_1`.** Expected `status=OK`; route DUMPs show
   three distinct two-station paths containing H, with one or more trains on each, and connector
   DUMPs show all six attached track ends. First-screen witness: three lines visibly leave H.
   Normal `<<PENDING-RUN>>` 15 seconds; abort `<<PENDING-RUN>>` 45 seconds.
4. **Resource setup — slots 3 and 4.** Slot 4 clears Metals at B and C to zero; slot 3 adds at most
   60 units at A, bounded by free capacity. Each act is MARK → mutation → DUMP → MARK and returns
   the selected station plus before/after stock. First-screen witness: the station storage row
   changes. Normal `<<PENDING-RUN>>` 10 seconds each; abort `<<PENDING-RUN>>` 30 seconds each.
5. **Train setup — slot 5 / `SMRTK_ACTION action=slot_5`.** Run once at each end station, never H.
   It refuses unless the station belongs to exactly one route. Expected `status=OK`; after game
   time advances, slot 1 shows one train on each route. First-screen witness: a train appears at
   that end. Normal `<<PENDING-RUN>>` one game minute; abort `<<PENDING-RUN>>` three game minutes.
6. **Interchange — pin B and C, then slot 6.** It refuses unless both destinations begin at zero,
   arms `hub_cargo_two_ends` plus Run Until, and pauses when both hold Metals. Expected trigger
   `status=OK` with positive `b_after` and `c_after`; slot 1 must still show three separate routes
   sharing H. First-screen witness: both destination storage rows become non-zero. Normal
   `<<PENDING-RUN>>` six sols; abort `<<PENDING-RUN>>` eighteen sols.
7. **Teardown.** With tracks and trains attached, use the vanilla demolish action on H, then read
   the toolkit error count and the complete flushed log. Expected: no Lua error or assert and no
   orphan connector at H's six hexes. First-screen witness: H and its attachment ends disappear
   cleanly. Normal `<<PENDING-RUN>>` 30 seconds; abort `<<PENDING-RUN>>` 90 seconds.
8. **Reload.** Rebuild if teardown was destructive, save to a disposable TestKit slot, reload it,
   then rerun Scratch, slot 2 and slot 1. Expected: H still has six connector elements, the three
   routes and trains remain, and cargo still transfers. Pins clear on load by design. Normal
   `<<PENDING-RUN>>` two minutes; abort `<<PENDING-RUN>>` six minutes.

## Confounds and standing observations

- Setup mutations are stock changes and train spawning only. They create the fixture but do not
  alter connector enumeration, route rebuilding, station balancing, teardown or persistence.
- Cheats are expected on this disposable colony. Count and attribute vanilla cheat markers once;
  toolkit action records are intentional and need no owner attribution.
- The four post-`f5fa650` toolkit observations remain a deliberate later sitting: depot fill/empty
  before/after, dark field-editor text, missing-field refusal followed by a live field trigger, and
  no console overlay. For this sitting each is **NOT RUN** unless the owner happens to witness it;
  the hub verdict does not depend on them.

## Result

`<<PENDING-RUN>>` No in-game evidence yet. Do not issue a go/no-go or ask for asset investment
until the fixture, interchange, teardown and reload legs above are recorded from one colony.
