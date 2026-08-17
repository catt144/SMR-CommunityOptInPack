# Relaunched Fix Pack: Opt-In Modules — Surviving Mars: Relaunched

Eight opt-in modules for *Surviving Mars: Relaunched*. Every one of them is
**off, or at its vanilla base setting, until you turn it on** in
**Options → Mod Options**. Nothing is patched on disk: the mod wraps the game's
own Lua at runtime, and a module you leave off behaves exactly like the
unmodded game.

**It works with or without the Relaunched Fix Pack.** The two mods are separate
downloads, share no files, and can be installed in either combination.

| module | what it does |
|---|---|
| Classic rockets | a player-controlled rocket parked at your colony keeps requesting launch fuel, so drones keep it fuelled while it waits |
| Acknowledged warnings | dismissing a "Building Not Working" warning acknowledges the buildings it listed; a newly broken building still warns immediately |
| Residency control | a per-Dome "Closed to new residents" policy row — no new Colonists move in, residents carry on normally |
| Multiple Artificial Suns | build more than one, and solar panels stop checking only the first one for night-time light |
| Drone dispatch overhaul (experimental) | the closest Drone Hub's fleet gets first claim on repair and cleaning jobs |
| Cohort housing | Seniors and Children move themselves into free Retirement Home / Nursery slots when such a slot exists |
| Nursery / Retirement Dome policy | a per-Dome toggle that moves unemployed, unhoused Colonists out of a Dome dedicated to Children or Seniors |
| Drone speed / carry dials | two dropdowns: a multiple of base Drone movement speed, and extra carry capacity per trip |

⚠️ **Before uninstalling, set both Drone dials back to base.** A non-base dial
leaves its boost in the savegame, and with the mod gone nothing is left to take
it back off.

---

*Development repo. `docs/` and `.claude/` never ship — see `metadata.lua`'s
`ignore_files`. Agent-facing documentation starts at `docs/README.md`; the
mandatory read is `docs/agent/STATE.md`.*
