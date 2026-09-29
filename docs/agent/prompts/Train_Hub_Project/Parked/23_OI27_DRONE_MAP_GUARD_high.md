# Brief 23 — OI-27: hub repair drones stay on the hub's map · _high

## Authority and outcome

**Owner ruling OI-27, 2026-09-29** (spec `docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md`
§10, grep `Owner ruling` + `OI-27`): *"I think it would be best if they don't see anything on
another map as far as repair drones go."* Hub repair drones get no work, target or flight leg on
any map but the hub's own. A tunnel `linked_obj` whose far mouth is on another map (a rail shaft)
is not followed for drone work. Same-map tunnels are unaffected.

**Not ruled, so unchanged by this build:** whether far-map stations count toward hub membership or
distribution (`D.Refresh`, `route_key`). The owner rules that later, with the fixture in front of
them. If the hub's graph currently serves both drone work and membership, the guard must restrict
drone work only.

Done when: the guard is in the dev hub (`tools/devmods/train_hub/`), a desk test proves the shaft
case is refused and the same-map tunnel case still followed, and a short attended smoke script is
written into your report for the orchestrator to run with the owner.

## Start

Authored at `66c3515`. Run `git log --oneline -3` and `git pull` first. Keep a live todo list,
one item per commit-and-verify unit, one in progress.

## Evidence (claims from a read-only desk audit at `3eccf57`; re-derive every line with `grep -n`)

- The hub's track walk follows tunnel partners with no map check:
  `20_TrainHub.lua` near `local far = live(node) and node.linked_obj` (read at `:2426-2427`;
  the orchestrator confirmed this line). Further partner sites reported at `:2461-2468`, `:3210-3211`.
- Drone flight: `30_TrainHubDrones.lua` `F.Route` (reported `:315-324`) routes through a tunnel
  partner; `F.Site` (`:333-341`) accepts any target; hub drones spawn on the hub's map
  (`20_TrainHub.lua` reported `:2916`). A cross-map leg ends at the far coordinates on the
  drone's own map.
- A "cross-map pair" is only this: a `TrackTunnelBase` whose `linked_obj` is on another map. The
  rail shaft dev mod stores no marker (`tools/devmods/rail_shaft/Code/10_RailShaft.lua`, grep
  `IsSameMap` / `linked_obj`). Use the game's own map test; do not import or depend on the rail
  shaft mod — the hub must behave identically with it absent.
- Control fixture: `docs/agent/bugs/D14.md` item (b) — the shaft case beside the same-map tunnel case.
- Background: `docs/agent/reports/RAIL_SHAFT_PROTOTYPE.md`; the handoff
  `Train_Hub_Project/RAIL_SHAFT_PROTOTYPE_high.md` (work list item 2 is this brief).

## Scope

- In: the hub's drone work, targets and flight legs across a cross-map tunnel; its desk test; the
  smoke script; the D14 entry's item (b) status.
- Out: hub membership and distribution; the rail shaft dev mod; any same-map tunnel behaviour;
  movement (finished, owner 2026-09-21).

## Stops — report instead of continuing if

1. The guard cannot be placed without changing same-map tunnel behaviour or hub membership.
2. The installed build is no longer 25390750 (`python tools/doccheck.py --emit-fingerprint`).

## Claim limits

Do not claim "hub drones work with a rail shaft". Supported: the desk test's two cases, and what
the smoke shows on which save with which mods loaded.

## Hand back

Commit with a pathspec. Report: commits, the desk test's printed output, the guard's sites, the
smoke script (about five steps, SMRTK slots per `tools/SMRTK.md`, each slot named by function), and
what you did not do. Do not delete or move this brief; the orchestrator owns its lifecycle.

Skills: `smr-bug-library` for D14, `doc-editing` for docs. House rules `CLAUDE.md`; code
`docs/agent/FIX_POLICY.md`.
