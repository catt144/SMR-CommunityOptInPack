-- Mod Options — the in-game enable surface for the eight modules
-- (Options → Mod Options → Relaunched Fix Pack: Opt-In Modules). Moved here from the
-- Community Fix Pack on 2026-08-12 with the split; the entries below are
-- BYTE-IDENTICAL to the ones that shipped there.
--
-- Why this file exists: the old "set SMROptInPack_Optional from the console
-- before the mod loads" instruction was unusable — module gates run at mod
-- code load, DURING game startup, before any console exists (and the console
-- platforms Paradox Mods targets have no console at all). The engine's native
-- mod options are the supported path: values persist per account
-- (AccountStorage.ModOptions), are loaded BEFORE mod code so the gates can
-- read them (CommonLua/Classes/Mod.lua:2128-2131, exposed as
-- CurrentModOptions), and the page works with a gamepad on PS/Xbox.
--
-- RULES:
--   * Each toggle's `name` MUST equal the module's SMROptInPack.Register id —
--     00_Core.lua's OptionEnabled/reconcile read them by that id.
--   * Every toggle here must also appear (as false) in metadata.lua
--     `default_options` — that field is what makes the Options screen list
--     the mod at all (ModDef:HasOptions, Mod.lua:473-475).
--   * EXCEPTION — the two ModItemOptionChoice dials (DroneSpeedDial /
--     DroneCarryDial) belong to the NON-toggle module DroneStatDials (D09):
--     their names are NOT Register ids, 00_Core's boolean reconciler does
--     not manage them, and the module reads CurrentModOptions directly and
--     reconciles itself (FIX_POLICY §5 dial addendum). Their
--     `default_options` entries are the base STRINGS (must stay
--     byte-identical to the ChoiceList/module maps), not false.
--   * Toggling takes effect immediately (00_Core's OnMsg.ApplyModOptions
--     reconciliation activates/deactivates the module live); the tooltips
--     stay behavior-only.
--   * ⛔ THESE NINE OPTION NAMES AND EVERY CHOICE STRING ARE ACCOUNT/SAVE
--     CONTRACT and keep their exact bytes (docs/agent/PROVENANCE.md §2).
--
-- ModItemCode entries (audit 2026-07-29, A3): the Mod Editor's SaveDef
-- regenerates metadata.lua's `code` list SOLELY from these items
-- (Mod.lua:960-974 via UpdateCode :816-840) — without them an editor
-- round-trip (and the editor upload flow, which saves-if-dirty) would write
-- `code = false` and publish a mod that loads NO code at all. ORDER IS
-- LOAD-BEARING: the entries below must stay in exactly metadata.lua's
-- current `code` order (00_Core first, then the eight Opt_ in their current
-- order), or a round-trip reorders the load sequence.
return {
	PlaceObj('ModItemCode', {
		'name', "00_Core",
		'CodeFileName', "Code/00_Core.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "Opt_ClassicRockets",
		'CodeFileName', "Code/Opt_ClassicRockets.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "Opt_AcknowledgedWarnings",
		'CodeFileName', "Code/Opt_AcknowledgedWarnings.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "Opt_ResidencyControl",
		'CodeFileName', "Code/Opt_ResidencyControl.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "Opt_MultipleSuns",
		'CodeFileName', "Code/Opt_MultipleSuns.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "Opt_DroneOverhaul",
		'CodeFileName', "Code/Opt_DroneOverhaul.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "Opt_CohortHousing",
		'CodeFileName', "Code/Opt_CohortHousing.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "Opt_NoHomeless",
		'CodeFileName', "Code/Opt_NoHomeless.lua",
	}),
	PlaceObj('ModItemCode', {
		'name', "Opt_DroneStatDials",
		'CodeFileName', "Code/Opt_DroneStatDials.lua",
	}),
	PlaceObj('ModItemOptionToggle', {
		'name', "ClassicRockets",
		'DisplayName', "Classic rockets — refuel while parked",
		'Help', "A player-controlled rocket parked at your colony keeps its launch fuel requested even with no destination selected, so drones keep it fueled while it waits — the original game's behavior.",
		'DefaultValue', false,
	}),
	PlaceObj('ModItemOptionToggle', {
		'name', "AcknowledgedWarnings",
		'DisplayName', "Acknowledged warnings",
		'Help', 'Dismissing a "Building Not Working" warning acknowledges the buildings it lists: they stay quiet until they recover (a later breakage warns again), while a NEWLY broken building always warns immediately. Without this, dismissal silences the whole category for 4 game hours and then it returns.',
		'DefaultValue', false,
	}),
	PlaceObj('ModItemOptionToggle', {
		'name', "ResidencyControl",
		'DisplayName', "Residency control",
		'Help', 'Adds a per-Dome "Closed to new residents" policy row to the Dome infopanel: no new Colonists move in, while current residents keep commuting, working and using services normally. Not a quarantine — that toggle still exists and still seals the Dome.',
		'DefaultValue', false,
	}),
	PlaceObj('ModItemOptionToggle', {
		'name', "MultipleSuns",
		'DisplayName', "Multiple Artificial Suns",
		'Help', "Lets you build more than one Artificial Sun, and fixes the base-game bug where solar panels only ever check the first sun for night-time light. Turning it off restores the one-per-colony limit (existing suns keep working).",
		'DefaultValue', false,
	}),
	PlaceObj('ModItemOptionToggle', {
		'name', "DroneOverhaul",
		'DisplayName', "Drone dispatch overhaul (experimental)",
		'Help', "With overlapping Drone Hub coverage, the base game lets a far-away hub's drone claim a repair that idle drones are parked next to. This makes the CLOSEST hub's fleet get first claim on repair and cleaning jobs (a far fleet still serves if the near one doesn't respond within seconds), and lets idle drones help a neighboring OVERLOADED hub with nearby repairs. Player orders, hauling, construction and RC rovers are untouched.",
		'DefaultValue', false,
	}),
	PlaceObj('ModItemOptionToggle', {
		'name', "CohortHousing",
		'DisplayName', "Cohort housing — Seniors & Children",
		'Help', "Seniors and Children living in normal housing automatically move into free Retirement Home / Nursery slots — in their own Dome first, in any reachable Dome second — and are left completely alone when no such slot exists. Employed Seniors stay put; your manual residence and Dome assignments always win; quarantine and closed Domes are respected. No dome designation needed: concentrate the cohort buildings where you want the cohort to live.",
		'DefaultValue', false,
	}),
	PlaceObj('ModItemOptionToggle', {
		'name', "NoHomeless",
		'DisplayName', "Nursery / Retirement Dome policy",
		'Help', 'For the Dome you dedicate to Children or Seniors. Such a Dome keeps only enough ordinary housing to staff its services, so unhoused jobseekers pile up in it — and once it holds enough homeless it counts as overcrowded and stops receiving anyone, including the cohort it was built for. This adds a per-Dome toggle row: when it is on, UNEMPLOYED Colonists with no home there move to the nearest Dome with housing they can use. Colonists who work there stay, and Seniors and Children stay even while homeless — a homeless Senior in a Retirement Dome is the game telling you to build more Retirement Homes, and hiding it would not help. Nobody is ever put outside, and a quarantined Dome still releases no one.',
		'DefaultValue', false,
	}),
	PlaceObj('ModItemOptionChoice', {
		'name', "DroneSpeedDial",
		'DisplayName', "Drone speed",
		'Help', "Adds a multiple of base Drone movement speed: 2x adds +100%, 3x adds +200%, 5x adds +400%, stacking on top of any speed techs the save has (Low-G Drive, Advanced Drone Drive). Drones only — rovers and shuttles are untouched. Takes effect immediately; 1x is exactly vanilla.",
		'DefaultValue', "1x (base)",
		'ChoiceList', { "1x (base)", "2x", "3x", "5x" },
	}),
	PlaceObj('ModItemOptionChoice', {
		'name', "DroneCarryDial",
		'DisplayName', "Drone carry capacity",
		'Help', "How many extra units of a resource a Drone carries per trip, on top of the base 1 (the Artificial Muscles breakthrough adds another +1 — they stack). Takes effect immediately; +0 is exactly vanilla.",
		'DefaultValue', "+0 (base)",
		'ChoiceList', { "+0 (base)", "+1", "+2" },
	}),
}
