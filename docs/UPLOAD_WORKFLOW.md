# Upload workflow — owner

## Must_Read_Header
<!-- RULES -->
Rule: Keep this file limited to the owner-facing upload procedure and its maintained paste blocks. [A3: pass]
Rule: Change the store text in the §3 paste blocks and regenerate `metadata.lua` from them with `python tools/store_parity.py --write-metadata`, never the other way round. [A3: pass]
<!-- /RULES -->

**The order is: mod → store pages → site.** The store pages are what players
actually see; the site is a place people have to choose to visit.

This mod has **not been published yet.** The first time through, do section 0 as
well. After that, every upload is sections 1 to 5.

---

## Before you start

The agent does the words (store body, change note, site pages) and tells you when
it is ready. If nobody has said "ready to upload", ask.

For the **first** upload, two things are still yours and the agent cannot do them:

| gap | what it needs from you | tracked on |
|---|---|---|
| ⛔ Store listings | whether an Opt-In draft already exists on either store under your account; if not, the first upload creates the listing and its id is read back afterwards, never typed ahead | OI-44 |
| ⛔ Console / platform approval | which platforms you choose on Paradox Mods and what approval step it shows; the fix pack's approval does not carry over | OI-44 |

---

## 0 · First publish only

1. **Look for an existing listing.** Sign in to Paradox Mods and to Steam and look for
   a draft named *Relaunched Fix Pack: Opt-In Modules* under your account. If one
   exists, tell the agent before you upload; otherwise the upload creates it.
2. **Preview art is in place** and the agent has said the preflight is green. Paradox
   refuses a mod with no preview image before it packs anything.
3. **Platforms.** When Paradox Mods asks, choose the platforms you want this mod on.
   Xbox and PlayStation go through Paradox's own approval; keep whatever status page or
   receipt it shows you, and tell the agent what it said.
4. **Steam.** A brand-new Workshop item can stay hidden until the Workshop agreement is
   accepted on the account; accept it if asked. Set the item's visibility once the
   page looks right.
5. **Afterwards**, the agent reads the new ids out of `metadata.lua` (the editor writes
   them during the upload) and records them. You do not need to copy them anywhere.

---

## 1 · Pack

1. Main menu → **MOD EDITOR**.
2. It asks to restart the game. **Yes.** It reopens into the editor.
3. On the right, read the **Last changes** box. That text is the change note players
   will see on both stores. If it is wrong or still describes the last release, stop
   and say so.
4. **File → Pack Mod.**

⛔ Do not press the Save (floppy) button. It bumps the version for nothing.

---

## 2 · Upload

**Paradox Mods first. Steam second.** Always this order. Doing it backwards pushes
the two stores' version numbers further apart, and that cannot be undone.

These are **meant** to upload by themselves, with nothing pasted:

- the page description
- the short summary
- the title and tags (Gameplay, Buildings)
- the change note
- the gallery screenshots, once they are declared in `metadata.lua`; check each page
  shows them in order

✅ **They do fill themselves.** That was settled on the fix pack (owner, 2026-09-12)
and nothing in this mod changes it. What does **not** survive is the formatting, so
step 3 is a styling pass rather than a rescue, and the paste copies there stay current
for it. Nobody needs to report the result.

**Two things that look wrong and are not:**

- The version number goes up. That is the upload doing its job.
- **The two stores show different version numbers.** They always will. ⛔ Never
  re-upload to make them match; that bumps again and makes the gap bigger.

---

## 3 · Check the store pages — and paste if you need to

**Does the description start with "Opt-in modules for Surviving Mars: Relaunched"
and run all the way down to the BEFORE YOU UNINSTALL section at the end?**

### ✅ Yes — the automatic fill worked

The normal case. Nothing to report and nothing to paste, unless you want the styling,
which is the part the fill never carries. Go to the styling pass below.

### ❌ No — it is short, stale, or missing

Paste the matching block below by hand. **Paradox:** run `python tools/paradox_card.py`,
which opens the Paradox block already formatted in your browser; press Ctrl+A and
Ctrl+C there, then paste over the Paradox description. (Paradox stores the description
as HTML, so the plain block pasted directly arrives as one wall of text.) **Steam:**
paste the BBCode block as-is; its tags render. Then tell the agent, because this is the
exception.

`python tools/store_parity.py` proves these blocks and `metadata.lua` agree; the agent
runs it before every "ready to upload".

#### 📋 Title

```
Relaunched Fix Pack: Opt-In Modules
```

#### 📋 Short summary (only if it also came out blank)

```
Opt-in gameplay modules, including train logistics, all off or at base until you enable them in Mod Options. Applied at runtime, no game files modified. Works with or without the Relaunched Fix Pack.
```

#### 📋 Paradox Mods — description (plain text, paste as-is)

```
Opt-in modules for Surviving Mars: Relaunched — every one of them off, or at its vanilla base setting, until you turn it on in Options → Mod Options. Acknowledged "not working" warnings, more than one Artificial Sun, two Drone stat dials (speed, carry capacity), interest tags that show which Colonist interests a service building serves, and train logistics: Import/Export rows for each resource on every Train Station, the Train Hub where three lines cross, and the Elevator Depot linking surface and underground lines. Nothing is patched on disk: the mod wraps the game's own Lua at runtime. A module you leave off behaves like the unmodded game, except that hubs and depots already built keep working. Works with or without the Relaunched Fix Pack. ⚠️ Before uninstalling: set both Drone dials back to base and save, and demolish every Train Hub and both halves of each Elevator Depot.

THE MODULES

Every module has its own switch on the Mod Options page, and a switch takes effect as soon as you press Apply, in both directions. Turning the whole mod on or off in the Mod Manager is different: that takes effect after a full restart of the game.

· Acknowledged warnings. Dismissing a "Building Not Working" warning acknowledges the buildings it lists: they stay quiet until they recover, and a building that recovers and breaks again warns again. A newly broken building always warns immediately. Without this, dismissing the warning silences it for four game hours and then it comes back. Only these building warnings change.

· Multiple Artificial Suns. Build more than one Artificial Sun. The game's own solar panels only ever look at the first sun for night-time light, so this module also connects panels to whichever sun covers them, and reconnects them when a sun is demolished. Panels already standing when you switch it on pick up a second sun after you save and load; panels built afterwards connect straight away. Off, the one-per-colony limit returns and suns you have built keep working.

· Drone speed and Drone carry capacity. Two dials. Drone speed adds a multiple of base Drone movement speed on top of any speed techs you have; Drones only, rovers and shuttles are untouched. Drone carry capacity adds extra units per trip on top of the base one, and the Artificial Muscles breakthrough still stacks. Both take effect immediately, and the base positions are exactly the unmodded game. ⚠️ A dial left off its base position stays in your save as an ordinary bonus after the mod is gone, so set both dials back to base, press Apply and save before you uninstall.

· Service interest tags. Shows which Colonist interests each service building satisfies (an Electronics Store counts for Shopping and Gaming): in the build menu when you hover a service building, and as an "Interests" section on a placed building, whose popout lists the traits that gain or lose something there. Display only: how Colonists choose and use services does not change, and it stores nothing in your save.

· Station import/export rows. Set each resource at a Train Station to Import, Export, Balanced or Not accepted, with a slider for the target. Works on every station, with or without a Train Hub, and is always on while the Train Hub module is on. Off, stations go back to the game's own requests.

· Train Hub. A junction where three train lines cross and cargo changes lines. It stores resources for the stations on its lines, runs its own drones to build and repair track, and has upgrades of its own; stations served by a hub use the hub's Import/Export rows. While it is on, Train Stations don't spoil food. Off, no new hubs can be built and hubs already built keep working. ⚠️ Demolish every Train Hub before removing the mod.

· Elevator Depot. Two halves, one on the surface and one underground, joined by a cabin that carries cargo between them: set each resource on the surface half to Import (goes down) or Export (comes up), and the cabin loads what the other side needs. One pair per colony; drones can be given access to either half; one upgrade doubles its capacity. Off, no new depot can be built and a pair already built keeps working. ⚠️ Demolish both halves before removing the mod.

YOUR SAVE, AND REMOVING THE MOD

Turning a module off puts the game's own behaviour back; what the module already did stays done, and buildings already placed keep working. Removing the whole mod is different, because the Train Hub and the Elevator Depot exist only while it is installed: follow the note at the bottom of this page first. The Drone dials are the other thing to know: a dial left off its base position keeps boosting your drones after the mod is gone, so put both back to base, press Apply and save before you uninstall.

Bought Train Hub upgrades remain recorded in your save after all hubs are demolished, and their ordinary game bonuses may remain after the mod is removed.

PLAYING ON XBOX, PLAYSTATION OR THE MICROSOFT STORE

Every switch and dial is on the Mod Options page, which works with a controller. One rule that applies to every mod rather than to this one: while any mod is enabled, the game does not unlock achievements on Xbox, PlayStation or the Microsoft Store. Steam and other PC versions are not affected.

BUGS, QUESTIONS AND MORE DETAIL

Each module is written up on the mods' site, with what it changes and what it leaves alone. Bugs can be reported there from a browser, with no account needed, and a save or a log can be attached privately. If this page has a comment section, that works too. Built and tested on game version 1.1.1.
https://catt144.github.io/SMR-CommunityMods/

Thanks to ChoGGi for prior Surviving Mars modding work, and LukeH for Martian Express patch research.

BEFORE YOU UNINSTALL

1. Set both Drone dials back to base, press Apply, and save the game.
2. Demolish every Train Hub and both halves of every Elevator Depot, then save the game.
3. Then disable or remove the mod and restart the game fully.

Removing the mod while hubs or depots are still standing leaves buildings in your save that the game no longer knows, and the game reports errors when that save loads. With them demolished first, your stations go back to the game's own import and export requests.
```

**To paste it into Paradox with the formatting already applied:**

1. In a terminal in this repo, run `python tools/paradox_card.py`.
2. A page opens in your browser. Press **Ctrl+A**, then **Ctrl+C**.
3. In the Paradox editor, select the whole description and paste over it.

The heading, the bold section titles and the line breaks come across. The tool reads
the block above every time it runs. Keep section titles in capitals so they come out
bold, and keep this block under its heading, which is how the tool finds it.

#### 📋 Steam Workshop — description (BBCode, paste as-is)

```
Opt-in modules for [i]Surviving Mars: Relaunched[/i] — every one of them off, or at its vanilla base setting, until you turn it on in Options → Mod Options. Acknowledged "not working" warnings, more than one Artificial Sun, two Drone stat dials (speed, carry capacity), interest tags that show which Colonist interests a service building serves, and train logistics: Import/Export rows for each resource on every Train Station, the Train Hub where three lines cross, and the Elevator Depot linking surface and underground lines. Nothing is patched on disk: the mod wraps the game's own Lua at runtime. A module you leave off behaves like the unmodded game, except that hubs and depots already built keep working. Works with or without the Relaunched Fix Pack. ⚠️ Before uninstalling: set both Drone dials back to base and save, and demolish every Train Hub and both halves of each Elevator Depot.

[h2]The modules[/h2]
Every module has its own switch on the Mod Options page, and a switch takes effect as soon as you press Apply, in both directions. Turning the whole mod on or off in the Mod Manager is different: that takes effect after a full restart of the game.
[list]
[*][b]Acknowledged warnings.[/b] Dismissing a "Building Not Working" warning acknowledges the buildings it lists: they stay quiet until they recover, and a building that recovers and breaks again warns again. A newly broken building always warns immediately. Without this, dismissing the warning silences it for four game hours and then it comes back. Only these building warnings change.
[*][b]Multiple Artificial Suns.[/b] Build more than one Artificial Sun. The game's own solar panels only ever look at the first sun for night-time light, so this module also connects panels to whichever sun covers them, and reconnects them when a sun is demolished. Panels already standing when you switch it on pick up a second sun after you save and load; panels built afterwards connect straight away. Off, the one-per-colony limit returns and suns you have built keep working.
[*][b]Drone speed and Drone carry capacity.[/b] Two dials. Drone speed adds a multiple of base Drone movement speed on top of any speed techs you have; Drones only, rovers and shuttles are untouched. Drone carry capacity adds extra units per trip on top of the base one, and the Artificial Muscles breakthrough still stacks. Both take effect immediately, and the base positions are exactly the unmodded game. ⚠️ A dial left off its base position stays in your save as an ordinary bonus after the mod is gone, so set both dials back to base, press Apply and save before you uninstall.
[*][b]Service interest tags.[/b] Shows which Colonist interests each service building satisfies (an Electronics Store counts for Shopping and Gaming): in the build menu when you hover a service building, and as an "Interests" section on a placed building, whose popout lists the traits that gain or lose something there. Display only: how Colonists choose and use services does not change, and it stores nothing in your save.
[*][b]Station import/export rows.[/b] Set each resource at a Train Station to Import, Export, Balanced or Not accepted, with a slider for the target. Works on every station, with or without a Train Hub, and is always on while the Train Hub module is on. Off, stations go back to the game's own requests.
[*][b]Train Hub.[/b] A junction where three train lines cross and cargo changes lines. It stores resources for the stations on its lines, runs its own drones to build and repair track, and has upgrades of its own; stations served by a hub use the hub's Import/Export rows. While it is on, Train Stations don't spoil food. Off, no new hubs can be built and hubs already built keep working. ⚠️ Demolish every Train Hub before removing the mod.
[*][b]Elevator Depot.[/b] Two halves, one on the surface and one underground, joined by a cabin that carries cargo between them: set each resource on the surface half to Import (goes down) or Export (comes up), and the cabin loads what the other side needs. One pair per colony; drones can be given access to either half; one upgrade doubles its capacity. Off, no new depot can be built and a pair already built keeps working. ⚠️ Demolish both halves before removing the mod.
[/list]

[h2]Your save, and removing the mod[/h2]
Turning a module off puts the game's own behaviour back; what the module already did stays done, and buildings already placed keep working. Removing the whole mod is different, because the Train Hub and the Elevator Depot exist only while it is installed: follow the note at the bottom of this page first. The Drone dials are the other thing to know: a dial left off its base position keeps boosting your drones after the mod is gone, so put both back to base, press Apply and save before you uninstall.

Bought Train Hub upgrades remain recorded in your save after all hubs are demolished, and their ordinary game bonuses may remain after the mod is removed.

[h2]Playing on Xbox, PlayStation or the Microsoft Store[/h2]
Every switch and dial is on the Mod Options page, which works with a controller. One rule that applies to every mod rather than to this one: while any mod is enabled, the game does not unlock achievements on Xbox, PlayStation or the Microsoft Store. Steam and other PC versions are not affected.

[h2]Bugs, questions and more detail[/h2]
Each module is written up on the mods' site, with what it changes and what it leaves alone. Bugs can be reported there from a browser, with no account needed, and a save or a log can be attached privately. If this page has a comment section, that works too. Built and tested on game version 1.1.1.
[url=https://catt144.github.io/SMR-CommunityMods/]https://catt144.github.io/SMR-CommunityMods/[/url]

Thanks to ChoGGi for prior Surviving Mars modding work, and LukeH for Martian Express patch research.

[h2]Before you uninstall[/h2]
[olist]
[*]Set both Drone dials back to base, press Apply, and save the game.
[*]Demolish every Train Hub and both halves of every Elevator Depot, then save the game.
[*]Then disable or remove the mod and restart the game fully.
[/olist]
Removing the mod while hubs or depots are still standing leaves buildings in your save that the game no longer knows, and the game reports errors when that save loads. With them demolished first, your stations go back to the game's own import and export requests.
```

#### 📋 Change note (both stores — Paradox CHANGELOG / Steam Change Notes)

Usually auto-fills. If it is missing under **CHANGELOG** (Paradox) or **Change
Notes** (Steam), paste this:

```
First release. Every module is off, or at its base setting, until you turn it on in Options → Mod Options: acknowledged warnings, more than one Artificial Sun, two Drone stat dials, service interest tags, and train logistics with station import/export rows, the Train Hub and the Elevator Depot. Read the uninstall note at the bottom of the page before you ever remove the mod.
```

### Either way: the styling pass

The fill gives you plain text, correct but with no headings or bold, and the formatting
never survives an upload. So this pass runs every time, on **both** stores. **Steam:**
paste the BBCode block above. **Paradox:** run `python tools/paradox_card.py`, then
Ctrl+A and Ctrl+C in the browser page it opens, and paste over the description.

Cosmetic, and skippable; the page is correct without it. It is not optional for the
**agent**: keeping these blocks current is what makes the pass possible.

---

## 4 · Publish the site

The site does **not** update when the agent commits. It only updates when you run this:

1. Go to **github.com/catt144/SMR-CommunityMods**
2. **Actions** tab
3. **Publish docs site** in the left-hand list
4. **Run workflow** → **Run workflow**

Give it a minute, then check the *Opt-In Modules* section shows up in the site's
navigation and its "Get it" line carries the store links the agent added.

---

## 5 · Tell the agent

Say "uploaded", plus:

1. Anything that **looked wrong** on either page.
2. Whether the **site published**.
3. **First publish only:** the two store page links as your browser shows them, and
   what Paradox said about platforms or approval.

The agent writes the rest down, reads the ids and version out of the editor's writeback,
restores the comments the editor strips from `metadata.lua` and `items.lua`, compares
the downloaded package with the tree, and closes the release records.

> ⛔ **Page version numbers are not tracked, and agents must not ask for one.** The
> number on a store page ticks up on a bare save as well as on an upload (owner,
> 2026-09-23, on the fix pack). This project tracks its own `version` inside
> `metadata.lua` and confirms an upload landed from the Steam changelog.

> ⛔ **Agents: two questions are answered and are never asked again** (owner,
> 2026-09-12): the descriptions always auto-fill, and the owner always pastes for the
> formatting. Record that as the known state of every upload.

---

## If something goes wrong

| what you see | what to do |
|---|---|
| The mod editor asks to save before uploading | Stop. Tell the agent. Something changed that should not have. |
| An upload is rejected | Stop. Tell the agent what it said, word for word. |
| Paradox refuses because of the preview image | The preview is wired (`preview.png`), so this should not happen. Stop; tell the agent what it said. |
| The description came out short | Paste it by hand (step 3), then tell the agent; this is the exception, not the norm. |
| Paradox is done and Steam failed or was skipped | Say so. Do not re-pack: the agent records a partial release and you finish Steam with the same packed file when you can. |
| You uploaded Steam before Paradox | Not fixable, and not worth chasing. Say so, carry on. |
