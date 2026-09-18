# Parked modules

Designed or part-built work the owner has set aside: not live, and not dead.
Pull-only: open it when a task or the owner calls for it.

Where things go: `FUTURE_IDEAS.md` holds ideas never started. This file holds designed or
part-built work the owner declared parked. `docs/archive/` holds what is dead. A module's full
record is its `docs/agent/bugs/Dxx.md`, which its entry points at.

Only the opt-in pack keeps this file: the fix pack only fixes bugs, so it never parks a creation.

## Must_Read_Header
<!-- RULES -->
Rule: Admit an entry only for a module, or part of a module, that the owner has declared parked. [A3: pass]
Rule: Write each entry as `### <name> · parked <date>` followed by `What:`, `Scope:`, `Revives by:`, `Evidence:` and `Basic summary:` in that order, within 10 lines. [A3: pass]
Rule: Carry facts and pointers only; history, status updates and design belong in the evidence files. [A3: pass]
Rule: Fill `Evidence:` with paths to existing records and nothing else, and do not create a file to extend an entry. [A3: pass]
Rule: Write in plain words the owner can read. [A3: pass]
Rule: Delete an entry in the commit that records the owner unparking or killing it. [A3: pass]
<!-- /RULES -->

`check_parked` in `tools/doccheck.py` gates the entry shape below.

## Entries

### DroneOverhaul · parked 2026-09-17
What: Opt-in drone module: the nearest hub's drones take a repair first; idle drones help busy hubs.
Scope: full module (D06)
Revives by: rebase the design and build brief on 1.1.0 and replace CalcLapTime, then owner rulings.
Evidence: docs/agent/bugs/D06.md · docs/agent/reports/DRONE_REBUILD_DESIGN_20260901.md · docs/agent/reports/DRONE_PRIORITY_SYSTEM.md · docs/agent/prompts/DRONE_REBUILD_BUILD_high.md
Basic summary: Built 2026-07-28. Its 1.0.7 test found the claim gate barely fired: hauling
parts is 88% of repair time, and the module left hauling alone. The owner chose a rebuild,
designed 2026-09-01 and never built: broken air and water producers, then any broken building,
go ahead of the player's priority arrows. The problem is still there in 1.1.0, but 1.1.0 deleted
CalcLapTime, the module's only measure, so the owner parked it unjudged. Code: commit cc846e4.
