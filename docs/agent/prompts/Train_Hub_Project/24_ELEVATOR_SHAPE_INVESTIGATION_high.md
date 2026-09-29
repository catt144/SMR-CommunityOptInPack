# Brief 24 — the cross-map train crossing: its best shape beside the hub · investigation · _high

## Authority and outcome

The owner, 2026-09-29: the rail shaft project joins the train hub project so the two are designed
together, not found colliding afterwards. The hub is nearly done; the crossing is built next and
the two are tested together at the end. **Your job is to answer, with evidence, the best shape
for the crossing**, in the owner's words: *"from the view point of working together and being
able to work without each other in case one is on but not the other. Or both are on and the user
has no underground unlocked or the underground is unlocked but the player hasn't done anything
with it yet. Find out what things should touch and what they shouldn't. What's possible / safe /
unsafe. Should we have a custom elevator or tie into the vanilla elevator?"*

Done when a report at `docs/agent/reports/CROSSING_SHAPE_20260929.md` gives:

1. **A recommendation on the shape**: a custom elevator (option G), a tie-in to vanilla's
   elevator, the tunnel shaft (option F), or something better you find, with the reasons and the
   evidence for and against each.
2. **The state matrix**. For each state, say what the player sees, what each mod does, and
   whether it is safe, unsafe or impossible:
   - Mods loaded: hub alone, crossing alone, both.
   - Underground: locked; unlocked but untouched (nothing built underground); in use.
   - Changing state mid-save: turning a module on or off; adding or removing a mod.
   - Saving at the crossing: a save made while a train is inside it, and loading that save.
3. **The touch list**: what the hub and the crossing *should* share, and through which seam (a
   vanilla data field, a message, a capability check that works with the other mod absent). Also
   what they must *never* share, each with the reason.
4. **The design rules a build brief can take as given**, each marked as proven from source, proven
   from a log, or inferred.
5. **What cannot be known from the desk**, with the smallest sitting step that would settle it.

## Settled — do not reopen

- **2026-09-21:** vanilla's elevator is not altered; prototype first
  (`docs/agent/reports/ELEVATOR_LOGISTICS_OPTIONS.md` head). The owner now asks whether to tie in
  to vanilla's elevator. Answer that question fully. If a tie-in would need vanilla's elevator
  changed (for example, a wrapped method, a changed template or a changed save field), say
  exactly what and why. That makes it an owner question against the 09-21 ruling; do not treat
  the ruling as reopened.
- **2026-09-23:** a shaft on the hub attaches to a hub connector whose opposite side is empty, so
  it terminates at the hub (`reports/RAIL_SHAFT_PROTOTYPE.md` §6 step 5).
- **OI-27, 2026-09-29:** hub repair drones see nothing on another map (spec
  `TRAIN_LOGISTICS_DESIGN_20260917.md` §10). Briefed as `23`, not built yet. Whether far-map
  stations count toward hub membership or distribution is **not ruled**. Lay out the options and
  their consequences; do not decide.
- **2026-09-29:** the rail shaft dev mod stays enabled in the owner's sessions. Hub testing folds
  into the crossing's sittings, and there is one full battery at the end.

## Evidence to start from (claims; clear each with one check)

- **Option F (the tunnel shaft), measured 2026-09-23:** a train crosses maps both ways, and its
  command thread survives `TransferToMap` inside a destructor.
  - Save/reload keeps the linked pair.
  - Hub-line trains stalled afterwards; the cause is not attributed.
  - Read `reports/RAIL_SHAFT_PROTOTYPE.md` §5, §7, §9 and §10.
  - The dev mod is `tools/devmods/rail_shaft/Code/10_RailShaft.lua`.
- **Option G (a rail elevator, direction only):** our own class, vanilla's elevator plus a train
  pass-through, with no buffer. Its source facts, its bill and its list "Unverified, check before
  building" are in `reports/ELEVATOR_LOGISTICS_OPTIONS.md`. Settle that list.
- **The orchestrator's desk audit, 2026-09-29, at `3eccf57`:** a read-only agent looked at
  where the dev shaft and the dev hub (`tools/devmods/train_hub/`) collide. Everything here is a
  claim; re-derive line numbers with `grep -n`.
  - C1: the hub's track walk follows a tunnel partner on another map. The orchestrator confirmed
    `20_TrainHub.lua`, grep `local far = live(node) and node.linked_obj`. Far-map stations then
    become hub-commanded.
  - C2: a hub drone's flight is routed through the shaft to the far coordinates, but on its own
    map (`30_TrainHubDrones.lua` `F.Route`, `F.Site`).
  - C3: `Link()` rebuilds every route and may overwrite hub-line routes. This is inferred, not
    measured.
  - C4: the resulting "routes rebuilt" message may make the hub's train bay give a free train
    (`70_TrainBay.lua` `route_key`). Inferred.
  - C5: distribution counts far-map stations as members.
  - C6: a save made mid-hop stores the dev mod's function in the train's thread, so loading it
    without the mod probably crashes (compare the hub's recorded crash at the top of
    `20_TrainHub.lua`). Inferred.
  - C7: removing the mod leaves the cross-map tunnel pair in the save, and trains strand there.
  - C8: on every load after underground is unlocked, the dev mod writes the saved
    `DisabledInEnvironment` table, and the change stays in the save.
  - C9: the two mods wrap no method in common, so load order does not matter.
  - The dev shaft has no off switch; its hooks install unconditionally.
- **Game source:** cite each line with the build it was read on, from that build's archived tree
  (`CLAUDE.md`). Check the installed build with `python tools/doccheck.py --emit-fingerprint`.
- **Records:** `docs/agent/bugs/INDEX.md` (see `D14` item (b)) and `docs/agent/facts/INDEX.md`
  for engine facts, including `EF-070` (autosave).

Leave the approach and read order to your judgement. The C-list gives leads, not hypotheses to
confirm.

## Scope

- In: vanilla's elevator, tunnel and train source; both dev mods; the hub spec; the state matrix;
  the shape recommendation. Throwaway probes that run nothing in the owner's game are also in.
- Out: editing any mod code, the spec or any ruling. Anything you find outside the question goes
  in the report and stays unedited.

## Stops — report what you have if

1. The installed build is no longer 25390750.
2. Some shape needs a live measurement before the others can be compared. Name it, with the
   smallest sitting step that would take it.

## Claim limits

Do not claim that any shape "works" or "is safe" in the game. The supported forms are "source
shows …", "log `<file>` shows …" and "inferred from …", each at a named build.

## Working

Run `git log --oneline -3` and `git pull` first. This brief was authored at `0a731be`. Keep a live
todo list, one item per unit and one in progress. Write only the report, and commit it with a
pathspec. The orchestrator audits the report on a different model before it enters the spec.
Your hand-back lists the commits, the commands whose output your claims rest on, and what you did
not check. Do not move or delete this brief.

Skills: `smr-bug-library` (facts), `doc-editing` (the report). House rules are in `CLAUDE.md`,
code policy in `docs/agent/FIX_POLICY.md`.
