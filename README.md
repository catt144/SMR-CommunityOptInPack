# Relaunched Fix Pack: Opt-In Modules — Surviving Mars: Relaunched

Opt-in modules for *Surviving Mars: Relaunched*. Every one of them is **off, or at its
vanilla base setting, until you turn it on** in **Options → Mod Options**. Nothing is
patched on disk: the mod wraps the game's own Lua at runtime, and a module you leave off
behaves like the unmodded game, except that hubs and depots already built keep working.

**It works with or without the Relaunched Fix Pack.** The two mods are separate downloads,
share no files, and can be installed in either combination.

**Get it:** [Paradox Mods](https://mods.paradoxplaza.com/mods/161911/Any) ·
[Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3813142702).
The player pages are on the family's site, under *Opt-In Modules*:
<https://catt144.github.io/SMR-CommunityMods/>

| module | what it does | when it is off |
|---|---|---|
| Acknowledged warnings | dismissing a "Building Not Working" warning acknowledges the buildings it lists: they stay quiet until they recover, a building that breaks again warns again, and a newly broken building always warns immediately | the game's own four-game-hour quiet window returns |
| Multiple Artificial Suns | build more than one Artificial Sun; panels connect to whichever sun covers them and reconnect when a sun is demolished (panels already standing when you switch it on pick up a second sun after a save and load) | the one-per-colony limit returns; suns you built keep working |
| Drone speed / Drone carry capacity | two dials: a multiple of base Drone movement speed, and extra units carried per trip, both on top of any techs you have; Drones only | base is exactly vanilla |
| Service interest tags | shows which Colonist interests each service building satisfies, in the build-menu hover and as an "Interests" section on a placed building; display only, stores nothing | vanilla panels |
| Station import/export rows | set each resource at a Train Station to Import, Export, Balanced or Not accepted, with a target slider; every station, hub or no hub; always on while the Train Hub is on | stations go back to the game's own requests |
| Train Hub | a junction where three train lines cross and cargo changes lines; stores for its stations, runs its own drones for track work, has upgrades of its own; stations keep food from spoiling while it is on | no new hubs; built hubs keep working |
| Elevator Depot | two halves, surface and underground, joined by a cabin that carries cargo between them; the surface half sets Import or Export per resource; one pair per colony | no new depot; a built pair keeps working |

## Before you uninstall

1. Set both Drone dials back to base, press Apply, and save the game.
2. Demolish every Train Hub and both halves of every Elevator Depot, then save the game.
3. Then disable or remove the mod and restart the game fully.

A dial left off its base position stays in your save as an ordinary bonus after the mod is
gone. Removing the mod while hubs or depots are still standing leaves buildings in your save
that the game no longer knows, and the game reports errors when that save loads; with them
demolished first, your stations go back to the game's own import and export requests.

Demolish every Train Hub and both halves of every Elevator Depot while the mod is installed,
then save, remove the mod and fully restart the game. References to the custom building classes
can remain in the save after demolition and may produce missing-class warnings when loaded
without the mod. This is not a guarantee of clean removal; no train-building recovery is provided.

Bought Train Hub upgrades remain recorded in your save after all hubs are demolished, and their
ordinary game bonuses may remain after the mod is removed.

## Console and gamepad players

Every switch and dial is on the Mod Options page, which works with a controller. While any mod
is enabled, the game does not unlock achievements on Xbox, PlayStation or the Microsoft Store.
Steam and other PC versions are not affected.

Built and tested on game version 1.1.1. Bug reports: the form on the site above takes a save
or a log privately and needs no account.

Thanks to ChoGGi for prior Surviving Mars modding work, and LukeH for Martian Express patch
research.

---

*Development repo. `docs/`, `tools/` and `.claude/` never ship — see `metadata.lua`'s
`ignore_files`. Agent-facing documentation starts at `docs/README.md`;
`docs/agent/STATE.md` is pull-only status.*
