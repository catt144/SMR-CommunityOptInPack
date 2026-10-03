# Store surfaces and the shared site — 2026-10-03

Result report of `Launch_Prep/03_STORE_AND_SITE_medium.md`. Authority: the owner's 2026-10-02
launch-prep request, OI-42's approved metadata description and summary, OI-45 (owner,
2026-10-03: demolish first, disclosed by an uninstall note at the bottom of each store page).
Fired by the owner on 2026-10-03 at `214f0ad`; startup `git log --oneline -5`, `git pull`
(already up to date) and `git status --short` (empty) ran first. Site `fd31bcf`, status empty.
Fix pack `56d72579`, ` M docs/agent/reports/RULE_PLACEMENT_TEST.md` (not ours, untouched).

This report is preparation, not a readiness verdict. Nothing here was uploaded or deployed.

## Preconditions found at fire time, and how this run treats them

| precondition | state | treatment |
|---|---|---|
| Root `RELEASE_SYSTEM_high.md` built (`docs/UPLOAD_WORKFLOW.md`, `STORE_CARD_LIVE.md`, `RELEASE_SURFACES.md`, outbox) | **Not fired.** The prompt map still lists it live; none of those files exists here (`rg --files docs \| rg 'UPLOAD_WORKFLOW\|STORE_CARD\|RELEASE_SURFACES\|OUTBOX'` → 0). | The maintained store bodies, change note and first-publish steps that 03 was told to *fill into* those files are kept **here**, in the donor's exact block shape (§3 below), for the release-system build to lift into place. Recorded as drift for 04 and as upstream notes for `RELEASE_SYSTEM_high.md`. |
| Links 01 and 02 fired | **Not fired**; both briefs still live and unstruck. | Allowed by the chain README ("independent drafts may start earlier"). Every behaviour claim below rests on evidence already accepted in an entry or ruling; the claim map in §4 names each source. No claim depends on 01/02. |
| OI-21 store-tool route | **Unruled.** | Stop 1 (missing tool decision): local ports prepared as the concrete choice, because the only alternative (parameterising the donor's copies) needs donor writes this brief does not grant. Reversible; OI-21 stays open to confirm or delete. |
| OI-12 preview and gallery | **Unselected.** No clean capture of the shipping hub or depot exists in the owner's drop folder (every `SMRTK_*.png` there carries the toolkit overlay, and all predate the final look). | Candidates and a shot list prepared (§5); nothing wired. `upload_preflight` stays red on exactly the missing `image`. |
| OI-44 listings / console | **Owner-only facts.** | First-publish steps written with explicit post-creation fill steps (§6). No id guessed. |

## Work list

| unit | state |
|---|---|
| Store bodies, metadata description/`last_changes`, public README, parity proof | COMPLETE (this commit) |
| Tool ports (`paradox_card.py`, `store_screenshots.py`, `store_parity.py`), ignore parity, sync declarations | COMPLETE (this commit) |
| Shared site Opt-In section, nav, README row, scoped sweep, `mkdocs build --strict` | COMPLETE, committed in the site repo, **not deployed** |
| Preview candidates, gallery shot list, drop folder, OI-12 refresh | COMPLETE; owner selection owed |
| Publish-day donor handoff (parked references reconciled) | COMPLETE (§7) |
| First-publish steps draft for `UPLOAD_WORKFLOW` | COMPLETE (§6); lifted by the release-system build |
| Gates, notes to 04 / RELEASE_SYSTEM / 01, checklist refresh, commits and push | COMPLETE |

## 1 · Evidence receipt

| class | command, run at Opt-In `214f0ad` unless stated | result and limit |
|---|---|---|
| MEASURED | `python tools/doccheck.py --emit-counts` | GREEN; 7 registered modules (1 default-active, 6 optional-gated); 19 `Code/*.lua`; 14 D rows. Membership control `rg -n 'Register\(' Code -g 'Opt_*.lua'`. |
| MEASURED | `python tools/doccheck.py --emit-fingerprint` | installed build 25579348, archive 1.1.1.406343 (read in the train final battery, 2026-10-03). |
| MEASURED | `python tools/upload_preflight.py` before this run | 1 FAIL: missing `image`; 1 UNCHECKABLE: Paradox login. Re-run after the edits: see §8. |
| SOURCE | `Get-Content metadata.lua` | approved description named D02, D04, D09 and the three train modules; D15 absent; `last_changes` split-era; no `image`, no screenshots, no portal ids. |
| SOURCE | `Get-Content README.md` | eight modules listed, four of them retired or parked; no trains, no D15, dial-only uninstall note. |
| SOURCE | `git -C B:/Dev/SMR/SMR-CommunityMods status --short`; `rg -n 'opt-in' content/report.md worker/src/index.js` | clean at `fd31bcf`; the report form already offers Opt-In Modules and the worker labels it `opt-in`; no new backend owed. |
| SOURCE | `ls B:/Dev/SMR/SMR-ScreenCaptures`; contact sheets of `SMRTK_0064`–`0087` | every capture carries the SMR Tool Kit panel; newest is 2026-09-28, before the final hub storage/paint and depot revision passes. Not store-grade. |
| SOURCE | `B:/Dev/SMR/SMR-Assets/trainhub/icon/README.md`, `elevatorstation/icon/README.md` | shipped build-menu icons are `icon_B_ring` (hub) and `icon_A_mouth` (depot); their full renders (`render_B_ring.png` 1160×1000 RGBA, `render_A_mouth.png` 1160×1000 RGBA) are on disk with transparent film. |

## 2 · What the copy may and may not say — the claim boundary

- Approved OI-42 sentences are kept verbatim as the lede of the store body; the one change is the
  insertion of the D15 clause ("interest tags that show which Colonist interests a service
  building serves"), which OI-42's reviewer could not have seen (D15 was absent from that text).
  The approved uninstall sentence stays in the lede; OI-45's full note is the **last** section.
- Every module block says what the entry records and nothing more. "Both toggle directions take
  effect at Apply" rests on D05 and the train battery's B0; the sun relink on D04's 2026-09-22
  change and the owner's 2026-10-02 play clearance; the hub/depot "keep working when off" on the
  battery's current contract (OI-19).
- **Not said:** clean removal, "load first", any count of modules, the save-rescue tool, credits
  by name (01 owns provenance; see §9), a full "what it puts in your save" list (01 owns the
  final residual set; the hub-upgrade receipt residual in FIX_POLICY §3 row 18 is a "may" that
  needs 01's measured answer before it is disclosed or omitted).
- Platform wording is FIX_POLICY §7's: "Steam and other PC versions", never "PC".

## 3 · Store bodies — maintained copies, pre-publication state

These are the blocks `docs/UPLOAD_WORKFLOW.md` §3 carries in the donor's shape, held here until
the release system exists. `metadata.lua`'s `description` is generated **from the Paradox block**
(`python tools/store_parity.py --write-metadata`), and `python tools/store_parity.py` proves all
three agree: Paradox block == metadata description byte for byte; Steam block == the same text
once BBCode tags and list markers are stripped. `python tools/paradox_card.py --source
docs/agent/reports/STORE_AND_SITE_20261003.md` opens the Paradox block formatted for pasting.

#### 📋 Title

```
Relaunched Fix Pack: Opt-In Modules
```

#### 📋 Short summary (approved OI-42, unchanged)

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

PLAYING ON XBOX, PLAYSTATION OR THE MICROSOFT STORE

Every switch and dial is on the Mod Options page, which works with a controller. One rule that applies to every mod rather than to this one: while any mod is enabled, the game does not unlock achievements on Xbox, PlayStation or the Microsoft Store. Steam and other PC versions are not affected.

BUGS, QUESTIONS AND MORE DETAIL

Each module is written up on the mods' site, with what it changes and what it leaves alone. Bugs can be reported there from a browser, with no account needed, and a save or a log can be attached privately. If this page has a comment section, that works too. Built and tested on game version 1.1.1.
https://catt144.github.io/SMR-CommunityMods/

BEFORE YOU UNINSTALL

1. Set both Drone dials back to base, press Apply, and save the game.
2. Demolish every Train Hub and both halves of every Elevator Depot, then save the game.
3. Then disable or remove the mod and restart the game fully.

Removing the mod while hubs or depots are still standing leaves buildings in your save that the game no longer knows, and the game reports errors when that save loads. With them demolished first, your stations go back to the game's own import and export requests.
```

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

[h2]Playing on Xbox, PlayStation or the Microsoft Store[/h2]
Every switch and dial is on the Mod Options page, which works with a controller. One rule that applies to every mod rather than to this one: while any mod is enabled, the game does not unlock achievements on Xbox, PlayStation or the Microsoft Store. Steam and other PC versions are not affected.

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
```

#### 📋 Change note (both stores — Paradox CHANGELOG / Steam Change Notes) — first release

```
First release. Every module is off, or at its base setting, until you turn it on in Options → Mod Options: acknowledged warnings, more than one Artificial Sun, two Drone stat dials, service interest tags, and train logistics with station import/export rows, the Train Hub and the Elevator Depot. Read the uninstall note at the bottom of the page before you ever remove the mod.
```

The outbox, when the release system creates it, holds this first-publish scope as its one
Pending entry. The development history before first publication (the 2026-09-22 widenings,
the train rebuilds) never shipped broken and gets no entry.

## 4 · Claim-to-source map

| claim in the store body / site / README | source |
|---|---|
| every module off or at base until enabled; Mod Options is the switch; controller-capable | `metadata.lua` `default_options` (all false / base strings); D05 `tested`; FIX_POLICY §7 |
| switches take effect at Apply, both directions | D05 (OnMsg.ApplyModOptions reconciler), train battery B0 (owner toggled each train module both ways), D15 sitting log (`deactivated` / `re-activated via Mod Options`) |
| whole-mod enable/disable needs a full restart | engine fact carried on the site's installing page; D15 enable-path leg used an in-place reload at the menu, which is the game's own exception, not the rule players rely on |
| works with or without the fix pack | D02/D04/D09: owner ruling 2026-10-02 plus the retained fix-pack-absent log; D15: both halves passed 2026-09-30; trains: fix-pack-present PASS on released 1.0.26, absent run waived by owner 2026-10-03 (`TRAIN_FIXPACK_OVERLAP_20261003.md`, no dependency either way) |
| acknowledged warnings: per-building, recovery re-arms, new breakage warns, 4-game-hour window otherwise | D02 PT-48 (1.0.7), 2026-09-22 eight-id widening desk-verified, owner play clearance 2026-10-02 |
| multiple suns: limit lift, panel binding, relink on demolition, reload for pre-existing panels | D04 PT-50/PT-55, 2026-09-22 `Done` wrapper, owner play clearance 2026-10-02 ("including demoing") |
| dials: additive on base, drones only, carry stacks with Artificial Muscles, base = vanilla, residue after uninstall | D09 PT-56, `items.lua` Help strings, FIX_POLICY §3 rows 4–7 |
| interest tags: hover line, Interests section with popout, display only, stores nothing | D15 `tested-attended` 2026-09-30; §3a tier 1 |
| station rows: four states + slider, every station, forced on by Train Hub, off restores native requests | D16; battery B0 (Rows slot 4) and B2 (native 10000/110000 restored with the mod absent) |
| hub: three crossing lines, storage for its network, own drones for track work, upgrades, stations on a hub use its rows, no spoilage while on, off = no new hubs | D17; FIX_POLICY §3 rows 10–19; `items.lua` Help; battery contract ("Hub/depot OFF hides new construction; placed content keeps working") |
| depot: two halves, cabin, surface Import/Export, loads to need, one pair, drone access per half, capacity upgrade doubles | D18 rulings (spec §11), battery B1 |
| demolish first; errors on load with buildings standing; native requests restored after demolition | OI-45 ruling; `TRAIN_FINAL_BATTERY_20261002.md` B2 and "Full-mod removal with buildings standing" |
| achievements blocked on Xbox / PlayStation / Microsoft Store, not Steam and other PC versions | FIX_POLICY §7, EF-106 |
| game version 1.1.1 | battery on 1.1.1.406343; D15 sitting `lua_revision: 406343` |
| report route (form, no account, private attachment) | site `content/report.md` and worker `opt-in` label at `fd31bcf` |

## 5 · Preview and gallery (OI-12)

**Preview candidates** (not wired; the owner selects, then `metadata.lua` gets
`'image', "Mod/SMR_CommunityOptInPack/preview.png"` and the file lands at the repo root):

| file (under `local/store_art_candidates/`) | made from | size |
|---|---|---|
| `preview_A_hub.png` | `SMR-Assets/trainhub/icon/render_B_ring.png` (the shipped icon's render) on a dark Mars-red field, 1024×1024, title lettering | see `python tools/upload_preflight.py` after wiring; each candidate is under Steam's 1 MB when generated |
| `preview_B_pair.png` | hub render and `elevatorstation/icon/render_A_mouth.png` side by side, same field | as above |
| `preview_C_hub_plain.png` | the hub render alone, no lettering | as above |

Regenerate with `python local/store_art_candidates/make_candidates.py` (kept beside them; the
imagegen skill named in the brief is not installed in this session, so the composites are
Pillow work on the mod's own renders). None is a gameplay claim: they are the shipped icon art.

**Gallery shot list** — real captures only, taken by the owner with the SMR Tool Kit panel
hidden, dropped as PNG into `B:\Dev\SMR\SMR-ScreenCaptures\optin_store\` with these names, then
`python tools/store_screenshots.py` re-encodes them under 1 MB into `store_screenshots/`
(excluded from the pack by `ignore_files`, still uploadable as `screenshot1..5`):

| order | capture | what it shows |
|---|---|---|
| 1 | `1_hub_day.png` | a Train Hub with trains on at least two lines, daylight, no panel open |
| 2 | `2_hub_panel.png` | the hub selected: resource rows, drones, track work, one upgrade |
| 3 | `3_depot_pair.png` | the Elevator Depot surface half with its rows, and the underground half if one capture can hold both |
| 4 | `4_station_rows.png` | a vanilla Train Station panel with Import/Export rows set |
| 5 | `5_interests_popout.png` | a service building's Interests section with its popout open |

Steam takes five; Paradox the same files. Limits enforced by `upload_preflight.py`: 1 MB per
image for Steam, 2 MB recorded for Paradox. The Mod Options page is the sixth candidate if the
owner prefers it to one of the five.

## 6 · First-publish steps — draft for `docs/UPLOAD_WORKFLOW.md`

To be lifted verbatim into the owner file the release system creates. Written for the owner.

1. **Is there already an Opt-In listing?** Sign in to Paradox Mods and the Steam Workshop and look
   for a draft named *Relaunched Fix Pack: Opt-In Modules* under your account. If one exists, say
   so; the agent records its id. If none, the first upload creates it (OI-44).
2. **Preview art first.** Choose the preview and the gallery captures (OI-12). The agent wires them
   and re-runs `python tools/upload_preflight.py`; it must read zero FAIL before step 3.
3. **Mod Editor → Pack Mod.** Read the Last changes box: it is the first-release note in §3. Do not
   press Save.
4. **Paradox Mods first.** Upload. If the portal asks about platforms, choose the ones you want
   this mod on; Xbox and PlayStation go through Paradox's own approval, and the fix pack's
   approval does not carry over. Keep whatever receipt or status page it shows you.
5. **Steam second.** Upload. A new Workshop item may stay hidden until the Workshop agreement is
   accepted on the account; accept it if asked. Set visibility when the page looks right.
6. **Gallery and styling.** On both pages check the screenshots arrived in order. The description
   auto-fills as plain text; run `python tools/paradox_card.py` for the Paradox paste, and paste
   the Steam BBCode block for Steam.
7. **Writeback.** Tell the agent "uploaded". The editor will have written `pdx_id`, `steam_id`
   and version fields into `metadata.lua` and stripped its comments; the agent keeps the ids,
   restores the comments and records the ids in the release record. **The ids are filled in
   after creation, from that writeback, never typed ahead.**
8. **Downloaded archive.** Once each store serves the mod, the agent runs
   `python tools/pack_list.py <ModContent.fpk> --tree .` on the downloaded copy and reconciles it
   against the predicted pack.
9. **Site last.** Run the *Publish docs site* workflow in the site repo; the Opt-In pages are
   already committed.

## 7 · Publish-day donor handoff — `PARKED_OPTIN_REFERENCES.md` reconciled

The donor file is a 2026-08-17 restore record for an eight-module product. Today's product has
seven modules (D01, D06, D07, D12 retired; D03 parked), store pages of its own, a dedicated site
section (built by this run) and a publish-day trigger that is still "the opt-in mod publishes".
**Nothing was restored and nothing in the fix pack was edited.** Disposition per passage:

| passages | disposition | reason |
|---|---|---|
| P1 (two-mod intro), P4 ("Do I need both?"), P5 (heading), P6 (tab group), P19 ("Do I need both mods?") | **SUPERSEDED** by the site's Opt-In section and landing-page pointer this run added; do not paste. | P6/P19 name eight modules and retired ones; the new pages carry the current set and the standalone statement. |
| P2, P10, P15, P18, P35 (drone-dial caveat and save-data passages) | **SUPERSEDED**; the dial caveat now lives on `content/opt-in/index.md` together with the demolish-first note. | The parked text knows only the dial; today's exit has two steps (OI-45). |
| P3, P21, P27b (preferences "live in the optional mod") | **RESTORE-ADAPTED at publish**, one clause each, by the fix pack's own release (its site pages are its surfaces). Exact text proposed in the site commit's FAQ/index wording is not required; a one-clause link to `opt-in/` suffices. | Harmless, improves routing; the fix pack's pages are the donor's to edit, not this brief's. |
| P7, P8, P36 (no-store-links notes) | **DROP**; already gone from the live site, the fix pack is published. | Obsolete. |
| P9, P29, P30, P33, P34 (plural "both mods" prose, repo links, listing calls) | **RESTORE-ADAPTED at publish** on `for-modders.md`, by the site's normal sweep: add the Opt-In repository link and the `SMROptInPack` veto example with a **current** id (`TrainHub`, not `NoHomeless`). | The persisted-prefix warning in P35 still holds (FIX_POLICY §3) and belongs on the modders page. This run already added the current form; see the site commit. |
| P11, P12, P13, P14, P16, P22, P23 (install/FAQ passages about the optional mod's switches) | **SUPERSEDED** by `content/opt-in/index.md`; the fix pack's install page keeps its one-switch note as is. | Current wording lives with the mod it describes. |
| P17 (one tracker covers both mods) | **DROP**; the report form already routes by mod. | Already true in a better form. |
| P20 (toggles reset after the split) | **DROP**. | Never a player's experience; the donor itself says to reconsider. |
| P24 (acknowledged-warnings remedy pointer in the FAQ) | **RESTORE-ADAPTED at publish** by the fix pack's release: one sentence pointing at the Opt-In module page. | The FAQ answer is on a fix-pack page; the pointer is the only safe addition. |
| P25 (Retirement Dome hotel), P26 (classic rockets), P27 (second sun reload) | P25, P26 **DROP** (D12, D01 retired). P27 **SUPERSEDED**: the reload note is on the Opt-In module page. | Retired modules get no player text. |
| P28 (fix-list boundary paragraph) | **RESTORE-ADAPTED at publish** by the fix pack's release, naming the mod and linking `opt-in/`, without the eight/seven count. | Count is stale. |
| P31, P32 (veto example and id rule) | **SUPERSEDED** by this run's modders-page addition with current ids. | `NoHomeless` is retired. |
| P35b (`site_description`), P37 (README mods row) | **DONE in this run's site commit** (both are shared surfaces this brief owns). | — |
| P38, P39 (fix pack `metadata.lua` strings), P40a–d (fix pack store card) | **FIX PACK RELEASE, publish day or later**: the separate-mod clause and companion bullet may return, adapted to the live store link and the two-step uninstall pointer; `last_changes` describes that release, never P39. Needs a fix-pack version bump and upload through its own release prompt. | Donor metadata/store changes require the donor's release and owner upload. |
| ④ sheet `RELEASE_PORTAL_PREP.md` parked markers, `RELEASE_DESCRIPTION_OPTIN.md` banner | **FIX PACK HOUSEKEEPING** after publish: reverse the markers that still apply; `RELEASE_DESCRIPTION_OPTIN.md` and `STORE_OPTIN.md` are **historical** (eight modules, holes, 1.0.7) and are not the paste source; §3 above is. | The donor's own notes already say the opt-in text is release-prep's option, not a mandate. |

The donor-side items are a single publish-day job for the fix pack's `release_prompt.md`: three
one-clause restores (P3/P21/P27b, P24, P28 class), the modders-page plural restore, and the
store-card/metadata companion clauses, all adapted to the live link. This report is the exact
input; no donor file was touched.

## 8 · Gates and limits — gate results

Run at the working tree that became `736e6e6` (this repo) and `d87c700` (site), 2026-10-03.

| gate | command | result |
|---|---|---|
| doccheck | `python tools/doccheck.py` after `--regen` | GREEN; PACK IGNORE PARITY 17 filters; TOOL CATALOG 30 scripts, 30 rows; LOCAL 3 rows; CHECKLIST PASS 76 lines |
| store parity | `python tools/store_parity.py` | 5 checked, 0 FAIL: Paradox == metadata description (5978 chars), Steam == same words (1026 words), summary, change note, 5 sections = 5 `[h2]` |
| parse | `python tools/parsecheck.py --dir <scratch copy of metadata.lua>` (the tool's relpath cannot cross drives, so the copy sits under `scratch/`) | 1 file, 0 errors. `Code/` is unchanged by this run; doccheck's PARSE covers it (19 files, 0 errors). The `--dir .` sweep reports one pre-existing BOM file under `scratch/`, not shipping |
| upload preflight | `python tools/upload_preflight.py` | 33 checked, **1 FAIL** (`image` empty; OI-12), 1 UNCHECKABLE (login). Not a handoff state; recorded, not waived |
| pack prediction | `python tools/pack_predict.py .` | 74 files = root 3 + Code 19 + Data 2 + Entities 5 + Fallbacks 17 + Materials 4 + Meshes 5 + Textures 17 + UI 2; 102,578,114 B = 526,635 non-asset (preflight) + 102,051,479 asset; `*/store_screenshots/*` matches nothing yet (folder absent) |
| site build | `python -m mkdocs build --strict` in `SMR-CommunityMods` | clean, no warnings |
| sync ledger | `python tools/sync_from_fixpack.py --tools` | ports declared; pre-existing `upload_preflight.py` DIFFERS (undeclared since OI-18's adaptation) and `doccheck.py` RECHECK left for the knowledge-sync pass |

**Commits.** This repo: `736e6e6` (work), then the records commit that adds this section. Site:
`d87c700`, **committed, not deployed**; the owner's *Publish docs site* workflow deploys it after
the store pages exist. Both pushed to `origin/main`.

**Peer activity observed, untouched:** an untracked `tools/trains/soak/` folder appeared in this
tree between 13:49 and 13:57 on 2026-10-03 (another seat's SMRTK soak preparation); it is outside
every pathspec above.

**Limits.** No upload, no portal state, no deployment, no game run. Claims rest on the entries
and rulings in §4; 01/02 may still change the evidence under them. The preflight is red on the
preview by design until the owner selects art. Subagent work (site pages on Opus 5.5, tool ports
on Sonnet 5.5) was cleared by one check each (`mkdocs --strict` plus a read of every page and
diff; `paradox_card.py --check` on the maintained block) and corrected in three places (landing
sentence, FAQ console wording, acknowledged-warnings save line).

**Executed model:** Claude Fable 5.1 (`claude-fable-5-1`), from this session's model line.
Skills: smr-orientation, doc-editing, subagents (read), prompt-authoring (read), smr-bug-library
(read); the imagegen skill named by the brief is not installed.

## 9 · Routed, not done here

- **Credits in player text** wait for 01's provenance inventory (01 work item 5). The LICENSE
  notice ships; ChoGGi and LukeH are WORKFLOW's prior-art leads, not verified credits, so no name
  is on the store page yet. 01's notes carry this dependency.
- **Residual disclosure beyond the dial and the buildings** (FIX_POLICY §3 row 18's hub-upgrade
  receipt "may remain") waits for 01's measured residual set. The site's save-data passage is
  written to what is established.
- **Six once-per-load train notices** (open owner choice from the train close-out) are not a
  store matter; 01 holds it.

## 10 · Owner actions remaining (also on `docs/PLAYTEST_CHECKLIST.md`)

- OI-12: pick a preview candidate (or supply art) and capture the five gallery shots.
- OI-21: say "keep the ports" or "run from the fix pack".
- OI-44: confirm whether listings exist and which platforms/approvals the Paradox account offers.
- Deploy the site when the store pages are live (the owner's manual workflow); committed site sha
  is recorded below.
