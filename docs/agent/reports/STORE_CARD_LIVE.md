# Store card — what is live on each portal

The record of the published store pages, kept by
`docs/agent/support/POST_UPLOAD_CLOSE.md` §4 after each owner-confirmed upload. The
**source** of the store body is `docs/UPLOAD_WORKFLOW.md` §3; `metadata.lua` is generated
from it (`python tools/store_parity.py --write-metadata`). This file never leads: it
records what the portals were given.

## State: LIVE since 2026-10-04

First publication, batch `2026-10-04-01` (base `03dfda8`, tag `optin-v1.0.2`). The owner's
receipt for both portals: "Ok its uploaded and everything looks good". The upload auto-filled
the base commit's body (module paragraphs as `·` bullets); the owner then pasted the current
§3 blocks on both pages (owner, 2026-10-04), so the copy below is the per-module-heading body.

| portal | id | page | version live | platforms / approval | body as published |
|---|---|---|---|---|---|
| Paradox Mods | `pdx_id` 161911 | `https://mods.paradoxplaza.com/mods/161911/Any` | `metadata.lua` `version` 2; `pdx_version` "1" | owner, 2026-10-04: nothing was asked at upload and no approval step was shown (OI-44) | current copy below, pasted via `paradox_card.py` |
| Steam Workshop | `steam_id` 3813142702 | `https://steamcommunity.com/sharedfiles/filedetails/?id=3813142702` | `metadata.lua` `version` 2 | PC | current copy below, BBCode block pasted |

**Packages.** Steam: snapshot `local/release/2026-10-04-01/steam-1`, sha256
`7c709ca9aff86433c9d13b0ebadf84d48345e82b6dc1b776f513313db717db74`, 22,599,753 bytes, 75 of 75
members byte-identical to the launch tree (`python tools/pack_list.py … --tree …`, exit 0).
Paradox: no snapshot and no verdict; the Steam upload deleted that package before one was taken.

## Markup, per portal

- **Paradox Mods** stores the description as HTML. The auto-fill arrives as plain text
  without headings or line breaks; `python tools/paradox_card.py` renders the §3 block
  (first line as the heading, ALL-CAPS lines bold, one paragraph per line, URLs linked)
  for a Ctrl+A / Ctrl+C paste. The first upload's body and the pasted copy
  both arrived; the owner reported nothing wrong on either page (2026-10-04).
- **Steam Workshop** renders BBCode: `[h2]`, `[b]`, `[i]`, `[list]`/`[olist]` with `[*]`,
  `[url=…]`. The §3 Steam block uses only those.
- **Both** auto-fill title, short summary, tags (Gameplay, Buildings), change note and,
  once declared, `image` and `screenshot1..5` from `metadata.lua`.

## Links block

| link | value | confirmed by |
|---|---|---|
| Paradox Mods page | `https://mods.paradoxplaza.com/mods/161911/Any` | built from the `pdx_id` writeback; the page returns this mod's title (read 2026-10-04) |
| Steam Workshop page | `https://steamcommunity.com/sharedfiles/filedetails/?id=3813142702` | built from the `steam_id` writeback |
| Steam changelog | `https://steamcommunity.com/sharedfiles/filedetails/changelog/3813142702` | one `Update:` entry, "Oct 3 @ 11:19pm", first-release note (read 2026-10-04) |
| Site section | `https://catt144.github.io/SMR-CommunityMods/opt-in/` | Pages deployment of site `6c02476`, status `success`; the live page carries both store links (read 2026-10-04) |
| Repository | `https://github.com/catt144/SMR-CommunityOptInPack` | public |

## Later releases

`POST_UPLOAD_CLOSE.md` §5 moves the bodies below into a dated
`## ⭐ <date> — <what changed on the page>` section and replaces the current copy;
`store_parity.py` never selects a history section, and `--confirm-live` requires the current
copy to equal the §3 blocks at close-out.

## Current live copy

#### 📋 Paradox Mods — description (plain text, paste as-is)

```
Opt-in modules for Surviving Mars: Relaunched — every one of them off, or at its vanilla base setting, until you turn it on in Options → Mod Options. Acknowledged "not working" warnings, more than one Artificial Sun, two Drone stat dials (speed, carry capacity), interest tags that show which Colonist interests a service building serves, and train logistics: Import/Export rows for each resource on every Train Station, the Train Hub where three lines cross, and the Elevator Depot linking surface and underground lines.

THE MODULES

Every module has its own switch on the Mod Options page, and a switch takes effect as soon as you press Apply, in both directions. Turning the whole mod on or off in the Mod Manager is different: that takes effect after a full restart of the game.

ACKNOWLEDGED WARNINGS:

Dismissing a "Building Not Working" warning acknowledges the buildings it lists: they stay quiet until they recover, and a building that recovers and breaks again warns again. A newly broken building always warns immediately. Without this, dismissing the warning silences it for four game hours and then it comes back. Only these building warnings change.

MULTIPLE ARTIFICIAL SUNS:

Build more than one Artificial Sun. The game's own solar panels only ever look at the first sun for night-time light, so this module also connects panels to whichever sun covers them, and reconnects them when a sun is demolished. Panels already standing when you switch it on pick up a second sun after you save and load; panels built afterwards connect straight away. Off, the one-per-colony limit returns and suns you have built keep working.

DRONE SPEED AND DRONE CARRY CAPACITY:

Two dials. Drone speed adds a multiple of base Drone movement speed on top of any speed techs you have; Drones only, rovers and shuttles are untouched. Drone carry capacity adds extra units per trip on top of the base one, and the Artificial Muscles breakthrough still stacks. Both take effect immediately, and the base positions are exactly the unmodded game. ⚠️ A dial left off its base position stays in your save as an ordinary bonus after the mod is gone, so set both dials back to base, press Apply and save before you uninstall.

SERVICE INTEREST TAGS:

Shows which Colonist interests each service building satisfies (an Electronics Store counts for Shopping and Gaming): in the build menu when you hover a service building, and as an "Interests" section on a placed building, whose popout lists the traits that gain or lose something there. Display only: how Colonists choose and use services does not change, and it stores nothing in your save.

STATION IMPORT/EXPORT ROWS:

Set each resource at a Train Station to Import, Export, Balanced or Not accepted, with a slider for the target. Works on every station, with or without a Train Hub, and is always on while the Train Hub module is on. Off, stations go back to the game's own requests.

TRAIN HUB:

A junction where three train lines cross and cargo changes lines. It stores resources for the stations on its lines, runs its own drones to build and repair track, and has upgrades of its own; stations served by a hub use the hub's Import/Export rows. While it is on, Train Stations don't spoil food. Off, no new hubs can be built and hubs already built keep working. ⚠️ Demolish every Train Hub before removing the mod.

ELEVATOR DEPOT:

Two halves, one on the surface and one underground, joined by a cabin that carries cargo between them: set each resource on the surface half to Import (goes down) or Export (comes up), and the cabin loads what the other side needs. One pair per colony; drones can be given access to either half; one upgrade doubles its capacity. Off, no new depot can be built and a pair already built keeps working. ⚠️ Demolish both halves before removing the mod.

YOUR SAVE, AND REMOVING THE MOD

Turning a module off puts the game's own behaviour back; what the module already did stays done, and buildings already placed keep working. Removing the whole mod is different, because the Train Hub and the Elevator Depot exist only while it is installed: follow the note at the bottom of this page first. The Drone dials are the other thing to know: a dial left off its base position keeps boosting your drones after the mod is gone, so put both back to base, press Apply and save before you uninstall.

Bought Train Hub upgrades remain recorded in your save after all hubs are demolished, and their ordinary game bonuses may remain after the mod is removed.

Nothing is patched on disk: the mod wraps the game's own Lua at runtime. A module you leave off behaves like the unmodded game, except that hubs and depots already built keep working. Works with or without the Relaunched Fix Pack. ⚠️ Before uninstalling: set both Drone dials back to base and save, and demolish every Train Hub and both halves of each Elevator Depot.

BUGS, QUESTIONS AND MORE DETAIL

Each module is written up on the mods' site, with what it changes and what it leaves alone. Bugs can be reported there from a browser, with no account needed, and a save or a log can be attached privately. If this page has a comment section, that works too. Built and tested on game version 1.1.1.
https://catt144.github.io/SMR-CommunityMods/

BEFORE YOU UNINSTALL

1. Set both Drone dials back to base, press Apply, and save the game.
2. Demolish every Train Hub and both halves of every Elevator Depot, then save the game.
3. Then disable or remove the mod and restart the game fully.

Removing the mod while hubs or depots are still standing leaves buildings in your save that the game no longer knows, and the game reports errors when that save loads. With them demolished first, your stations go back to the game's own import and export requests.

Demolish every Train Hub and both halves of every Elevator Depot while the mod is installed, then save, remove the mod and fully restart the game. References to the custom building classes can remain in the save after demolition and may produce missing-class warnings when loaded without the mod. This is not a guarantee of clean removal; no train-building recovery is provided.
```

#### 📋 Steam Workshop — description (BBCode, paste as-is)

```
Opt-in modules for [i]Surviving Mars: Relaunched[/i] — every one of them off, or at its vanilla base setting, until you turn it on in Options → Mod Options. Acknowledged "not working" warnings, more than one Artificial Sun, two Drone stat dials (speed, carry capacity), interest tags that show which Colonist interests a service building serves, and train logistics: Import/Export rows for each resource on every Train Station, the Train Hub where three lines cross, and the Elevator Depot linking surface and underground lines.

[h2]The modules[/h2]
Every module has its own switch on the Mod Options page, and a switch takes effect as soon as you press Apply, in both directions. Turning the whole mod on or off in the Mod Manager is different: that takes effect after a full restart of the game.

[h2]Acknowledged warnings:[/h2]
Dismissing a "Building Not Working" warning acknowledges the buildings it lists: they stay quiet until they recover, and a building that recovers and breaks again warns again. A newly broken building always warns immediately. Without this, dismissing the warning silences it for four game hours and then it comes back. Only these building warnings change.

[h2]Multiple Artificial Suns:[/h2]
Build more than one Artificial Sun. The game's own solar panels only ever look at the first sun for night-time light, so this module also connects panels to whichever sun covers them, and reconnects them when a sun is demolished. Panels already standing when you switch it on pick up a second sun after you save and load; panels built afterwards connect straight away. Off, the one-per-colony limit returns and suns you have built keep working.

[h2]Drone speed and Drone carry capacity:[/h2]
Two dials. Drone speed adds a multiple of base Drone movement speed on top of any speed techs you have; Drones only, rovers and shuttles are untouched. Drone carry capacity adds extra units per trip on top of the base one, and the Artificial Muscles breakthrough still stacks. Both take effect immediately, and the base positions are exactly the unmodded game. ⚠️ A dial left off its base position stays in your save as an ordinary bonus after the mod is gone, so set both dials back to base, press Apply and save before you uninstall.

[h2]Service interest tags:[/h2]
Shows which Colonist interests each service building satisfies (an Electronics Store counts for Shopping and Gaming): in the build menu when you hover a service building, and as an "Interests" section on a placed building, whose popout lists the traits that gain or lose something there. Display only: how Colonists choose and use services does not change, and it stores nothing in your save.

[h2]Station import/export rows:[/h2]
Set each resource at a Train Station to Import, Export, Balanced or Not accepted, with a slider for the target. Works on every station, with or without a Train Hub, and is always on while the Train Hub module is on. Off, stations go back to the game's own requests.

[h2]Train Hub:[/h2]
A junction where three train lines cross and cargo changes lines. It stores resources for the stations on its lines, runs its own drones to build and repair track, and has upgrades of its own; stations served by a hub use the hub's Import/Export rows. While it is on, Train Stations don't spoil food. Off, no new hubs can be built and hubs already built keep working. ⚠️ Demolish every Train Hub before removing the mod.

[h2]Elevator Depot:[/h2]
Two halves, one on the surface and one underground, joined by a cabin that carries cargo between them: set each resource on the surface half to Import (goes down) or Export (comes up), and the cabin loads what the other side needs. One pair per colony; drones can be given access to either half; one upgrade doubles its capacity. Off, no new depot can be built and a pair already built keeps working. ⚠️ Demolish both halves before removing the mod.

[h2]Your save, and removing the mod[/h2]
Turning a module off puts the game's own behaviour back; what the module already did stays done, and buildings already placed keep working. Removing the whole mod is different, because the Train Hub and the Elevator Depot exist only while it is installed: follow the note at the bottom of this page first. The Drone dials are the other thing to know: a dial left off its base position keeps boosting your drones after the mod is gone, so put both back to base, press Apply and save before you uninstall.

Bought Train Hub upgrades remain recorded in your save after all hubs are demolished, and their ordinary game bonuses may remain after the mod is removed.

Nothing is patched on disk: the mod wraps the game's own Lua at runtime. A module you leave off behaves like the unmodded game, except that hubs and depots already built keep working. Works with or without the Relaunched Fix Pack. ⚠️ Before uninstalling: set both Drone dials back to base and save, and demolish every Train Hub and both halves of each Elevator Depot.

[h2]Bugs, questions and more detail[/h2]
Each module is written up on the mods' site, with what it changes and what it leaves alone. Bugs can be reported there from a browser, with no account needed, and a save or a log can be attached privately. If this page has a comment section, that works too. Built and tested on game version 1.1.1.
[url=https://catt144.github.io/SMR-CommunityMods/]https://catt144.github.io/SMR-CommunityMods/[/url]

[h2]Before you uninstall[/h2]
[olist]
[*]Set both Drone dials back to base, press Apply, and save the game.
[*]Demolish every Train Hub and both halves of every Elevator Depot, then save the game.
[*]Then disable or remove the mod and restart the game fully.
[/olist]
Removing the mod while hubs or depots are still standing leaves buildings in your save that the game no longer knows, and the game reports errors when that save loads. With them demolished first, your stations go back to the game's own import and export requests.

Demolish every Train Hub and both halves of every Elevator Depot while the mod is installed, then save, remove the mod and fully restart the game. References to the custom building classes can remain in the save after demolition and may produce missing-class warnings when loaded without the mod. This is not a guarantee of clean removal; no train-building recovery is provided.
```
