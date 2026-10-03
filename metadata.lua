return PlaceObj('ModDef', {
	-- ✅ DISPLAY NAME DECIDED (owner, 2026-08-13): family-prefixed so the two
	-- mods sort together in mod lists. Swept everywhere the same day
	-- (the current shipped title; its settled history remains in git).
	-- ⭐ FAMILY RENAMED (owner, 2026-08-17, fix-pack checklist 36): "Community
	-- Fix Pack" → "Relaunched Fix Pack" across the whole set, before any upload;
	-- owner ruled the sibling titles move NOW, then widened the license the
	-- same day ("fix any references that you recommend") — so the
	-- `description`/`short_description`/`last_changes` strings below carry the
	-- new name too, renamed IN PLACE (no other wording change). The richer
	-- description draft in the fix-pack repo's STORE_METADATA_STRINGS.md
	-- remains release-prep's option at this mod's own launch.
	'title', "Relaunched Fix Pack: Opt-In Modules",
	'description', "Opt-in modules for Surviving Mars: Relaunched — every one of them off, or at its vanilla base setting, until you turn it on in Options → Mod Options. Acknowledged \"not working\" warnings, more than one Artificial Sun, two Drone stat dials (speed, carry capacity), interest tags that show which Colonist interests a service building serves, and train logistics: Import/Export rows for each resource on every Train Station, the Train Hub where three lines cross, and the Elevator Depot linking surface and underground lines. Nothing is patched on disk: the mod wraps the game's own Lua at runtime. A module you leave off behaves like the unmodded game, except that hubs and depots already built keep working. Works with or without the Relaunched Fix Pack. ⚠️ Before uninstalling: set both Drone dials back to base and save, and demolish every Train Hub and both halves of each Elevator Depot.\n\nTHE MODULES\n\nEvery module has its own switch on the Mod Options page, and a switch takes effect as soon as you press Apply, in both directions. Turning the whole mod on or off in the Mod Manager is different: that takes effect after a full restart of the game.\n\n· Acknowledged warnings. Dismissing a \"Building Not Working\" warning acknowledges the buildings it lists: they stay quiet until they recover, and a building that recovers and breaks again warns again. A newly broken building always warns immediately. Without this, dismissing the warning silences it for four game hours and then it comes back. Only these building warnings change.\n\n· Multiple Artificial Suns. Build more than one Artificial Sun. The game's own solar panels only ever look at the first sun for night-time light, so this module also connects panels to whichever sun covers them, and reconnects them when a sun is demolished. Panels already standing when you switch it on pick up a second sun after you save and load; panels built afterwards connect straight away. Off, the one-per-colony limit returns and suns you have built keep working.\n\n· Drone speed and Drone carry capacity. Two dials. Drone speed adds a multiple of base Drone movement speed on top of any speed techs you have; Drones only, rovers and shuttles are untouched. Drone carry capacity adds extra units per trip on top of the base one, and the Artificial Muscles breakthrough still stacks. Both take effect immediately, and the base positions are exactly the unmodded game. ⚠️ A dial left off its base position stays in your save as an ordinary bonus after the mod is gone, so set both dials back to base, press Apply and save before you uninstall.\n\n· Service interest tags. Shows which Colonist interests each service building satisfies (an Electronics Store counts for Shopping and Gaming): in the build menu when you hover a service building, and as an \"Interests\" section on a placed building, whose popout lists the traits that gain or lose something there. Display only: how Colonists choose and use services does not change, and it stores nothing in your save.\n\n· Station import/export rows. Set each resource at a Train Station to Import, Export, Balanced or Not accepted, with a slider for the target. Works on every station, with or without a Train Hub, and is always on while the Train Hub module is on. Off, stations go back to the game's own requests.\n\n· Train Hub. A junction where three train lines cross and cargo changes lines. It stores resources for the stations on its lines, runs its own drones to build and repair track, and has upgrades of its own; stations served by a hub use the hub's Import/Export rows. While it is on, Train Stations don't spoil food. Off, no new hubs can be built and hubs already built keep working. ⚠️ Demolish every Train Hub before removing the mod.\n\n· Elevator Depot. Two halves, one on the surface and one underground, joined by a cabin that carries cargo between them: set each resource on the surface half to Import (goes down) or Export (comes up), and the cabin loads what the other side needs. One pair per colony; drones can be given access to either half; one upgrade doubles its capacity. Off, no new depot can be built and a pair already built keeps working. ⚠️ Demolish both halves before removing the mod.\n\nYOUR SAVE, AND REMOVING THE MOD\n\nTurning a module off puts the game's own behaviour back; what the module already did stays done, and buildings already placed keep working. Removing the whole mod is different, because the Train Hub and the Elevator Depot exist only while it is installed: follow the note at the bottom of this page first. The Drone dials are the other thing to know: a dial left off its base position keeps boosting your drones after the mod is gone, so put both back to base, press Apply and save before you uninstall.\n\nPLAYING ON XBOX, PLAYSTATION OR THE MICROSOFT STORE\n\nEvery switch and dial is on the Mod Options page, which works with a controller. One rule that applies to every mod rather than to this one: while any mod is enabled, the game does not unlock achievements on Xbox, PlayStation or the Microsoft Store. Steam and other PC versions are not affected.\n\nBUGS, QUESTIONS AND MORE DETAIL\n\nEach module is written up on the mods' site, with what it changes and what it leaves alone. Bugs can be reported there from a browser, with no account needed, and a save or a log can be attached privately. If this page has a comment section, that works too. Built and tested on game version 1.1.1.\nhttps://catt144.github.io/SMR-CommunityMods/\n\nBEFORE YOU UNINSTALL\n\n1. Set both Drone dials back to base, press Apply, and save the game.\n2. Demolish every Train Hub and both halves of every Elevator Depot, then save the game.\n3. Then disable or remove the mod and restart the game fully.\n\nRemoving the mod while hubs or depots are still standing leaves buildings in your save that the game no longer knows, and the game reports errors when that save loads. With them demolished first, your stations go back to the game's own import and export requests.",
	'short_description', "Opt-in gameplay modules, including train logistics, all off or at base until you enable them in Mod Options. Applied at runtime, no game files modified. Works with or without the Relaunched Fix Pack.",
	-- Split out of the Community Fix Pack on 2026-08-12: shipped there as
	-- `optional = true` files and moved here whole, behaviour unchanged and
	-- persisted names unchanged (docs/agent/FIX_POLICY.md §3). Live module count:
	-- `python tools/doccheck.py --emit-counts`.
	-- ⛔ `description` ABOVE and `last_changes` BELOW ARE GENERATED (Launch_Prep/03,
	-- 2026-10-03): `python tools/store_parity.py --write-metadata` copies them from the
	-- maintained Paradox block and change note, whose home is docs/UPLOAD_WORKFLOW.md §3
	-- once the release system builds it and, until then,
	-- docs/agent/reports/STORE_AND_SITE_20261003.md §3. Edit the block, never these
	-- strings; `python tools/store_parity.py` proves Paradox == this string and Steam ==
	-- the same words. The lede is OI-42's approved text plus the D15 clause; the last
	-- section is OI-45's uninstall note (owner, 2026-10-03: at the bottom of each page).
	'last_changes', "First release. Every module is off, or at its base setting, until you turn it on in Options → Mod Options: acknowledged warnings, more than one Artificial Sun, two Drone stat dials, service interest tags, and train logistics with station import/export rows, the Train Hub and the Elevator Depot. Read the uninstall note at the bottom of the page before you ever remove the mod.",
	'id', "SMR_CommunityOptInPack",
	'author', "catt144",
	-- ✅ SHIP VALUE 1.0.0, owner-ruled 2026-08-14 at launch prep ("we go 1.0,
	-- especially with the amount of QA we have done") — matches the changelog's
	-- "Initial release" and the sibling pack. PackVersion reads
	-- major.minor.version.
	'version', 0,
	'version_major', 1,
	'version_minor', 0,
	'lua_revision', 350453,
	-- saves made with this mod load fine without it (FIX_POLICY §3), so don't
	-- nag players who removed it with the missing-mods prompt.
	-- ⚠️ ONE documented caveat, unchanged by the split: a non-base Drone dial
	-- persists its boost into a save loaded WITHOUT this mod
	-- (Code/Opt_DroneStatDials.lua) — hence the uninstall instruction above.
	'optional_mod', true,
	-- the packer includes EVERYTHING recursively minus this list (Mod.lua:250-256,
	-- GedModEditor.lua:716-732) — without the extra patterns docs/, README.md,
	-- .gitignore and .claude/ all ship inside the .hpk. LICENSE ships on purpose.
	-- ⭐ THREE PATTERNS ADDED 2026-08-14 AT LAUNCH PREP (fix-pack chain
	-- `release-3` prompt 1) — checklist item 23, the owner's ruling "YES, add the
	-- missing patterns, at launch prep", all three mods. MEASURED before and
	-- after over the real tree: without them this package shipped `CLAUDE.md`,
	-- `.gitattributes` and all EIGHT files of `tools/` into a player's download —
	-- 22 files where 12 belong. Nothing there ever RUNS (only `code` executes),
	-- but CLAUDE.md is agent instructions and `tools/` is build machinery.
	-- ⚠️ `LICENSE` is NOT excluded, deliberately — see the fix pack's note.
	'ignore_files', {
		"*.git/*",
		"*.svn/*",
		"*/Source/*",
		"*/SourceData/*",
		"*/docs/*",
		"*/.agents/*",
		"*/.claude/*",
		"*/tools/*",
		"*README.md",
		"*CLAUDE.md",
		"*AGENTS.md",
		"*.gitignore",
		"*.rgignore",
		"*.gitattributes",
		-- 2026-09-21: durable in-tree material (local/) and agent/subagent
		-- working space (scratch/) — both git-ignored, ported from the fix
		-- pack's same-day ruling on where non-repo material lives; the
		-- README gate for local/ is local/README.md. Never ship either.
		"*/local/*",
		"*/scratch/*",
		-- 2026-10-03 (Launch_Prep/03): the store GALLERY. Both uploaders read
		-- screenshot1..5 from here (`Mod/`-prefixed paths), so the files must sit
		-- inside the mod folder, but they are store art, not mod content:
		-- `tools/store_screenshots.py` writes them, this pattern keeps them out
		-- of the player's pack. Same shape as the fix pack's.
		"*/store_screenshots/*",
	},
	-- Mod Options defaults (D05): must mirror items.lua's ModItemOptionToggle
	-- names, all false. This field is what makes Options → Mod Options list the
	-- mod (ModDef:HasOptions reads it, Mod.lua:473-475), and the engine seeds
	-- CurrentModOptions from it before our code loads. The two D09 dial
	-- entries are ModItemOptionChoice values — base STRINGS, byte-identical
	-- to items.lua's ChoiceList and Opt_DroneStatDials.lua's maps, not false.
	-- ⛔ ALL NINE KEYS AND VALUES ARE LIFTED FROM THE FIX PACK BYTE-FOR-BYTE
	-- (docs/agent/FIX_POLICY.md §3, persisted-name inventory rows 6-9). Do not retype them.
	'default_options', {
		AcknowledgedWarnings = false,
		MultipleSuns = false,
		-- D15 (owner, 2026-09-28): a NEW key, not a donor lift; account contract
		-- from here on (FIX_POLICY §3 inventory row 8).
		ServiceInterestTags = false,
		DroneSpeedDial = "1x (base)",
		DroneCarryDial = "+0 (base)",
		-- D16-D18 (owner, 2026-10-02, OI-41): the train modules' NEW keys, account
		-- contract from their first ship (FIX_POLICY §3 inventory row 8).
		StationRows = false,
		TrainHub = false,
		ElevatorDepot = false,
	},
	-- ⛔ ORDER IS LOAD-BEARING: ModDef:LoadCode iterates THIS list and scans no
	-- directory (Mod.lua:490-521), so 00_Core.lua must stay first — every module
	-- calls SMROptInPack.Register at file scope. The rest below keep the
	-- relative order they had in the fix pack.
	-- ⚖️ 2026-09-17 (owner): DroneOverhaul PARKED, CohortHousing + NoHomeless DEAD
	-- on 1.1.0 — all three removed from this list and from items.lua. Both wrap-order
	-- constraints this comment used to record involved NoHomeless and left with it;
	-- ResidencyControl now wraps ChooseDome alone. Archive + restore steps:
	-- local/retired-modules/README.md; the record is git (bugs/D06, D07, D12).
	-- ⚖️ 2026-09-18 (owner): ClassicRockets RETIRED (OVERTAKEN) — vanilla 1.1.0's
	-- GetFuelResourceRequest ships the fuel half natively; the module's residual
	-- reach fought a new deliberate rule (zeroing Trade/TradePad/Rival rockets).
	-- Removed from this list and from items.lua; restore sha `1716471`; record
	-- is git + bugs/D01.md; archive copy at local/retired-modules/README.md.
	-- ⚖️ 2026-10-02 (owner): ResidencyControl PARKED for launch — it sits against
	-- 1.1.x's rewritten migration and its 09-22 repair was never seen in play.
	-- Removed from this list, `default_options` and items.lua; restore sha
	-- `43f4c0e`; record bugs/D03.md and docs/PARKED_MODULES.md.
	'code', {
		"Code/00_Core.lua",
		"Code/Opt_AcknowledgedWarnings.lua",
		"Code/Opt_MultipleSuns.lua",
		"Code/Opt_DroneStatDials.lua",
		"Code/Opt_ServiceInterestTags.lua",
		-- ⚖️ 2026-10-02 (owner, OI-41; brief 34): the train modules. Each Opt_ file
		-- registers its module and is followed by its parts, Code/<id>_*.lua
		-- (FIX_POLICY §8: a ModItemCode's file is Code/<its name>.lua, so a
		-- part cannot live in a subfolder, ModItem.lua:164-168). File-scope orders that matter, enforced by doccheck's
		-- LOAD ORDER: 10_TrainFloor before 40 (the transient claims), 40 before 45
		-- (D.active), 20_TrainHub before 60 (SMROptInTrainHubBase).
		"Code/Opt_StationRows.lua",
		"Code/StationRows_10_TrainFloor.lua",
		"Code/StationRows_40_TrainDistribution.lua",
		"Code/StationRows_45_TrainDistributionUI.lua",
		"Code/Opt_TrainHub.lua",
		"Code/TrainHub_20_TrainHub.lua",
		"Code/TrainHub_30_TrainHubDrones.lua",
		"Code/TrainHub_60_StationSpoilage.lua",
		"Code/TrainHub_70_TrainBay.lua",
		"Code/Opt_ElevatorDepot.lua",
		"Code/ElevatorDepot_10_ElevatorDepot.lua",
		-- Editor-generated, LAST: a SaveDef appends them after every ModItemCode,
		-- in item-handle order (Mod.lua:535-556, :829-853); Data/ and SourceData/
		-- hold their sources. Never hand-edit them; the owner's Mod Editor save
		-- regenerates them (upload_preflight.py checks position and sources).
		"Code/BuildingTemplate/SMROptInTrainHub6.generated.lua",
		"Code/_EntityData.generated.lua",
		"Code/BuildingTemplate/SMROptInElevatorDepotDev.generated.lua",
	},
	-- The train modules' five models (brief 34). A SaveDef rebuilds this list
	-- from SourceData/ArtSpec-mod.lua alone (Mod.lua:816-827), which the packer
	-- skips but the editor reads, so that file must stay in the folder.
	'entities', {
		"SMROptInTrainHub6",
		"SMROptInTrainHub6Glass",
		"SMROptInTrainHub6DomeGlass",
		"SMROptInElevatorDepot",
		"SMROptInElevatorDepotReceiver",
	},
	'has_data', true,
	'TagGameplay', true,
	'TagBuildings', true,
})
