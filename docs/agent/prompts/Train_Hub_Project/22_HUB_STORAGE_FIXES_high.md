# Hub storage fixes: station cargo display, hub base 1,000, and a Storage Hub upgrade

Authored at `d70f3cd` (2026-09-29). Start with `git log --oneline -5`, `git status` and `git pull`.
Keep a live todo list before the first write, with one item per commit-and-verify unit and one item
in progress at a time.

## Authority (owner, 2026-09-29; settled, in spec §4.10 under grep `Owner's fix list before the audit`)

The three items below are the owner's pre-audit fix list. The rulings are recorded verbatim in the
spec. Do not reopen them.

1. **An upgraded station shows no cargo.** A small station holding Metals **60.4/120** (Export,
   Capacity Network on) shows nothing on its pads (owner's screenshot). The owner suspects the
   station's cube display scales stock against the doubled capacity, so a modest stock draws as
   empty. **That cause is a claim, not a finding.** Find the real cause, and make the pads show
   cargo the way vanilla does for a station of that fill. The owner judges the look by eye.
2. **Hub storage: base 1,000 per resource.** Capacity Network doubles it to **2,000** (today it
   is 240, and 480 with Capacity Network). Capacity Network's effect on stations and trains does
   not change.
3. **A new fourth hub upgrade, Storage Hub.** It is late game and doubles the hub's storage again
   to **4,000** per resource, the size of a vanilla Mechanized Depot. It affects the hub only, not
   stations or trains. It costs **60 Metals + 30 Machine Parts**, needs no tech, and **raises
   the hub's power consumption by 19 while on**, one per stored resource. It works in the
   all-upgrades style (spec §4.10, grep `a bought upgrade is a global unlock`): bought once for
   the colony, one on/off state shown on and switchable from every hub, salvage changes nothing,
   and present and future hubs inherit it. vanilla's Excavator carries six upgrades, so a
   fourth slot is a shape the game already has (owner's screenshot).

## Evidence you would otherwise re-derive

- The hub's Metals peaked at ~479800 in log `Mars.exe-20260929-13.36.00-6aad2d75.log` (grep
  `res=Metals row=stock station=6430`), the full 480. A full hub is why the owner's full-depot
  Export test looked stalled.
- The colony upgrade state is the `SMROptIn_hub_upgrades` table on `UIColony`, row 18 of
  `FIX_POLICY`'s persisted-name inventory, keyed by the three existing upgrade ids (rows 13, 16
  and 17). A fourth id is a new persisted name. It is expected and permitted: add it to the
  inventory under ban 1, with its reason.
- Save migration: existing saves carry 240/480 hubs, and the owner's fixtures have Capacity
  Network bought. Loading one must yield 1,000 or 2,000 without losing stock. The Power repair at
  `9bffa5c` rebased a saved base on load for the same kind of change.
- Records: `docs/agent/bugs/INDEX.md` and `docs/agent/facts/INDEX.md`.

## Done

- Desk tests cover:
  - the hub at 1,000 base and 2,000 with Capacity Network;
  - 4,000 with Storage Hub, with stations and trains unchanged by Storage Hub;
  - the +19 consumption appearing and disappearing with the toggle;
  - the shared state, salvage and a future hub, as for the other upgrades;
  - a load of a 240/480 save;
  - the station display fix.
- Each test has a mutation that fails it. Run every train hub smoke and report members = passing +
  failing.
- The template gains slot 4. The owner's Mod Editor save regenerates it. Extend
  `cargo_upgrade_smoke.py --require-generated` to cover slot 4 and the new capacity.
- A short attended sitting written in the report, as a smoke test only (spec §10 testing depth),
  preloaded into TestKit slots where a slot fits. It covers:
  - the pads showing cargo at a modest fill;
  - the hub panel at 2,000, then 4,000 after buying Storage Hub from one hub;
  - the other hub showing it on;
  - consumption +19;
  - a full-depot Export no longer stalling.
- Name each slot's function beside its number.

## Scope and stops

**In:** the hub's storage figures and their load migration, the Storage Hub upgrade, the template's
slot 4, the station cargo display, and their tests. **Out:** movement, dispatch and distribution
rules, the other three upgrades' behaviour, and the look of the hub.

Stop and report if:
- the station display fault is vanilla behaviour that a fix would have to replace a vanilla body
  to change;
- a fourth upgrade slot cannot be made to work on this class;
- the load migration cannot keep a saved hub's stock.

Do not claim a live PASS. Desk results are the claim; the owner's sitting is the check.

## References

`CLAUDE.md`, `docs/agent/FIX_POLICY.md` (both bans; §8), `docs/agent/WORKFLOW.md`, and the skills
`doc-editing` and `smr-bug-library`. Write the report as `reports/TRAIN_HUB_STORAGE_<date>.md`.
Record the executed model at close-out.

## Lifecycle

One-off. The orchestrator deletes it with its README row once its sitting passes.
