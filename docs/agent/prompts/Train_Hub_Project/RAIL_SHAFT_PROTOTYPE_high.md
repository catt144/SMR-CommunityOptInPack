# Rail shaft — handoff to the train hub coordinator · _high

**Owner, 2026-09-29:** this project passes to the train hub coordinator *"since their surfaces
touch"*. You now own its next steps. This file is the live remainder; the evidence lives in the
reports it links, not here.

Authored at `98168aa` plus the close-out commit that rewrote this file. Start with
`git log --oneline -3` and `git pull`; re-derive any line number with `grep -n` before you rely on
it (the hub files move daily), and re-read the installed build with
`python tools/doccheck.py --emit-fingerprint` (25390750 / 1.1.1.405907 at hand-over).

## Settled — do not reopen

- **2026-09-21:** the elevator's cargo pain is an Opt-In matter; explore a train crossing between
  maps; vanilla's elevator is not altered; prototype first. (`reports/ELEVATOR_LOGISTICS_OPTIONS.md` head)
- **2026-09-23:** a shaft on the hub attaches to a hub connector whose opposite is empty, so it
  terminates at the hub. (`reports/RAIL_SHAFT_PROTOTYPE.md` §6 step 5)
- **2026-09-23, direction:** the real thing is likely a *rail elevator* — our own class that is
  vanilla's elevator plus a train pass-through, vanilla's left untouched, no buffer because trains
  pass straight through. Recorded with its source facts and bill as **option G** in
  `reports/ELEVATOR_LOGISTICS_OPTIONS.md`. Direction only: F (tunnel) vs G is **not ruled**.
- **2026-09-29, OI-27:** hub repair drones see nothing on another map (spec
  `TRAIN_LOGISTICS_DESIGN_20260917.md` §10). **Not built.** Far-map hub membership and
  distribution are **not ruled**.

## Where it stands

Evidence and citations: `reports/RAIL_SHAFT_PROTOTYPE.md` §5 (sitting), §7 (bill), §10 (since).

- **Measured, retail, 2026-09-23:** a train crosses maps both ways; its command thread survives
  `TransferToMap` inside a destructor (3 hops of 3); routing resolves on both legs; save/reload
  keeps the linked pair and the `AddPFTunnel` guard fires. Stop (1) of the original brief is
  closed.
- **Unattributed:** hub-line trains stalled after the link. The next day's Codex audit
  (`TRAIN_HUB_AUDIT_111_20260923.md` §9) measured a hub siding deadlock, since fixed, on a
  sibling save of the same colony with every train `route_ok true` — the likelier cause. The
  report's route-overwrite mechanism (§7 item 0) is an untested source risk, kept as a free
  placement rule. Do not claim either as the cause.
- **Untested:** freight, passengers, wagon attaches, more than one lap, any hand-made map.
- **Dev mod:** `tools/devmods/rail_shaft/` (`SMRRailShaft.Status / List / Link / Routes / Sweep /
  Unlink / Kill`), junctioned as `SMR-RailShaftDev`. It has been **enabled in every session since
  09-23** — inert on same-map tunnels, but on 09-28 it wrote the underground-tunnel flag into
  saves from 5 sessions (report §10).
- **Shaft save unknown; its logs are gone.** Neither shaft-session log was archived. Loading the
  right save with the mod on logs `AddPFTunnel skipped for rail-shaft mouth` twice.

## Work list — keep it live with the todo tool, one item per commit-and-verify unit

1. **Owner, 2026-09-29: the dev mod stays enabled**; hub testing folds into the crossing's
   sittings, one full battery at the end. The shape question is item 5. No save loaded since 09-24 held a
   shaft. The shaft save stays unguarded until brief `23` lands: do not load it with the hub
   before then, or `Unlink()` it first.
2. **Hub build, briefed as `23_OI27_DRONE_MAP_GUARD_high.md`:** implement OI-27 at `SMROptInTrainHubBase:HubTrackGraph` and `F.Route` so repair
   drones never take work, a target or a flight leg across a cross-map `linked_obj`. Control per
   `bugs/D14.md` (b): the shaft fixture beside the same-map tunnel case.
3. **Owner call, when the hub sitting makes it takeable:** does a surface hub's membership and
   distribution (`D.Refresh` over `hub.city.train_track_routes`, which a shaft makes span both
   maps) reach underground stations through a shaft? Raise it as an `OI-` item then, not before —
   it is only answerable with the fixture in front of the owner.
4. **Rail sitting, after the hub ships** — preload it into SMRTK slots (`tools/SMRTK.md`); the
   owner clicks, does not type:
   - find the shaft save (item 1's log line), then `Sweep()` and `Routes()` on it, then `Unlink()`
     — this settles the stall attribution;
   - the positive control: a new shaft on a hub connector with an empty opposite, the underground
     end on a line end; `Routes()` 0 broken, every train `route_ok true`, then a freight round trip;
   - archive every log of it under `docs/archive/` in the same commit that records it.
5. **Owner call, after the fit sitting (OI-32):** the shape. Brief 24's investigation,
   `reports/CROSSING_SHAPE_20260929.md` (`787e525`), recommends **H**, our own rail terminals
   beside an existing vanilla elevator pair, reading its `other` and changing nothing on it. The
   recommendation is conditional on its §8.1 fit sitting; G (our own rail elevator) and F (this
   shaft) are the fallbacks. It settles G's unverified list (§3), the state matrix (§5), the
   mid-hop save exposures (§6) and the touch list (§7). Audited by the orchestrator on Opus,
   2026-09-29: claims S1, S2, the `other` link, `MergeGrids`, `D.Refresh` sharing `HubTrackGraph`,
   the bay's prefab spend and the SaveGameStart gap are all CONFIRMED against build 25390750.
   The fit of terminals beside an elevator is UNCLEAR from the desk. Generation clears a 3-hex
   ring (`SurfacePassage.lua:134-141`), but a colony's own buildings may fill it. One stretch is
   INFERRED, not ruled: §7 extends OI-27 to drone-task registration, saved jobs and payment.
6. **Optional, any time:** file the destructor fact (report §9 item 1) and the
   `disabled_in_environment` trap (§9 item 2) as engine facts — `EF-` ids come from the fix pack
   first (`smr-bug-library`).

## Scope, stops, claim limits

- In: the cross-map crossing, its hub touchpoints, the sitting, the F-vs-G decision. Out: building
  either module before a recorded ruling; editing vanilla's elevator.
- Stop and report if: the build is no longer 25390750; OI-27's guard cannot be placed without
  changing same-map tunnel behaviour; the shaft save cannot be found and item 4's first bullet has
  no fixture (then run the positive control alone and say the attribution stays open).
- Do not claim "trains run between maps" or that a shaft causes stalls. Supported: which legs of
  which round trips completed, on which save, with which mods loaded.

Skills: `doc-editing` for the reports, `smr-bug-library` for facts, `prompt-authoring` for any
brief you cut from this. **Lifecycle:** one-off; delete this file and its map row when item 5 is
ruled and the module, if any, has its own brief.
