return PlaceObj('ModDef', {
	-- ✅ DISPLAY NAME DECIDED (owner, 2026-08-13): family-prefixed so the two
	-- mods sort together in mod lists. Swept everywhere the same day
	-- (docs/agent/PROVENANCE.md §3).
	'title', "Community Fix Pack: Opt-In Modules",
	'description', "Eight opt-in modules for Surviving Mars: Relaunched — every one of them off, or at its vanilla base setting, until you turn it on in Options → Mod Options. Rockets that keep requesting fuel while parked, acknowledged \"not working\" warnings, a per-Dome \"closed to new residents\" policy, more than one Artificial Sun, a closest-hub-first Drone dispatch overhaul (experimental), automatic cohort housing for Seniors and Children, a Nursery/Retirement Dome policy, and two Drone stat dials (speed, carry capacity). Nothing is patched on disk: the mod wraps the game's own Lua at runtime, and a module you leave off behaves exactly like the unmodded game. Works with or without the Community Fix Pack. ⚠️ Set both Drone dials back to base before uninstalling — a non-base dial leaves its boost in the savegame.",
	'short_description', "Eight opt-in gameplay modules, all off or at base until you enable them in Mod Options. Applied at runtime, no game files modified. Works with or without the Community Fix Pack.",
	-- Split out of the Community Fix Pack on 2026-08-12: these eight modules
	-- shipped there as `optional = true` files and moved here whole, behaviour
	-- unchanged and persisted names unchanged (docs/agent/PROVENANCE.md).
	'last_changes', "Initial release: the eight optional modules, split out of the Community Fix Pack into their own mod.",
	'id', "SMR_CommunityOptInPack",
	'author', "catt144",
	-- pre-release 0.1.0 (PackVersion reads major.minor.version); launch prep
	-- sets the ship value
	'version', 0,
	'version_major', 0,
	'version_minor', 1,
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
	'ignore_files', {
		"*.git/*",
		"*.svn/*",
		"*/Source/*",
		"*/SourceData/*",
		"*/docs/*",
		"*/.claude/*",
		"*README.md",
		"*.gitignore",
	},
	-- Mod Options defaults (D05): must mirror items.lua's ModItemOptionToggle
	-- names, all false. This field is what makes Options → Mod Options list the
	-- mod (ModDef:HasOptions reads it, Mod.lua:473-475), and the engine seeds
	-- CurrentModOptions from it before our code loads. The two D09 dial
	-- entries are ModItemOptionChoice values — base STRINGS, byte-identical
	-- to items.lua's ChoiceList and Opt_DroneStatDials.lua's maps, not false.
	-- ⛔ ALL NINE KEYS AND VALUES ARE LIFTED FROM THE FIX PACK BYTE-FOR-BYTE
	-- (docs/agent/PROVENANCE.md §2, rows 6-9). Do not retype them.
	'default_options', {
		ClassicRockets = false,
		AcknowledgedWarnings = false,
		ResidencyControl = false,
		MultipleSuns = false,
		DroneOverhaul = false,
		CohortHousing = false,
		NoHomeless = false,
		DroneSpeedDial = "1x (base)",
		DroneCarryDial = "+0 (base)",
	},
	-- ⛔ ORDER IS LOAD-BEARING: ModDef:LoadCode iterates THIS list and scans no
	-- directory (Mod.lua:490-521), so 00_Core.lua must stay first — every module
	-- calls SMROptInPack.Register at file scope. The eight below keep the
	-- relative order they had in the fix pack: CohortHousing before NoHomeless
	-- (both wrap Colonist:FindEmigrationDome) and ResidencyControl before
	-- NoHomeless (both wrap ChooseDome), so wrap nesting is unchanged.
	'code', {
		"Code/00_Core.lua",
		"Code/Opt_ClassicRockets.lua",
		"Code/Opt_AcknowledgedWarnings.lua",
		"Code/Opt_ResidencyControl.lua",
		"Code/Opt_MultipleSuns.lua",
		"Code/Opt_DroneOverhaul.lua",
		"Code/Opt_CohortHousing.lua",
		"Code/Opt_NoHomeless.lua",
		"Code/Opt_DroneStatDials.lua",
	},
	'TagGameplay', true,
})
