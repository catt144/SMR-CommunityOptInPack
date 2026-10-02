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
	'description', "Opt-in modules for Surviving Mars: Relaunched — every one of them off, or at its vanilla base setting, until you turn it on in Options → Mod Options. Acknowledged \"not working\" warnings, more than one Artificial Sun, and two Drone stat dials (speed, carry capacity). Nothing is patched on disk: the mod wraps the game's own Lua at runtime, and a module you leave off behaves exactly like the unmodded game. Works with or without the Relaunched Fix Pack. ⚠️ Set both Drone dials back to base and then save before uninstalling — setting them to base clears the boost from the colony you are playing, and saving is what clears it from the file.",
	'short_description', "Opt-in gameplay modules, all off or at base until you enable them in Mod Options. Applied at runtime, no game files modified. Works with or without the Relaunched Fix Pack.",
	-- Split out of the Community Fix Pack on 2026-08-12: shipped there as
	-- `optional = true` files and moved here whole, behaviour unchanged and
	-- persisted names unchanged (docs/agent/FIX_POLICY.md §3). Module count has
	-- moved since (three RETIRED 2026-09-17, one more 2026-09-18) — live count:
	-- `python tools/doccheck.py --emit-counts`. ⚠️ `last_changes` below still
	-- describes the split-era set and is launch-prep's to finalize (OI-12-14 shape).
	'last_changes', "Initial release: the optional modules, split out of the Relaunched Fix Pack into their own mod.",
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
