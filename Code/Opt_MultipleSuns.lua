-- D04 — OPTIONAL module, OFF BY DEFAULT. Not a bug fix.
--
-- Enable it in-game: Options → Mod Options → Community Opt-In Pack (D05; toggles
-- take effect immediately, both directions — the build menu re-reads
-- CanBuildOnlyOnce() live, so on_activate/on_deactivate below flip the
-- template flag on the spot; existing suns are ordinary buildings and keep
-- working either way). The binding-fix half (the SolarPanelBase.GameInit
-- wrap) is installed at FILE SCOPE, classdef time, so it propagates through
-- class flattening and the FIRST mid-session enable binds new panels too —
-- an apply()-time install ran after flattening and left that half silently
-- dead until restart (audit A2, fixed 2026-07-29; the Opt_DroneOverhaul
-- pattern). Other mods / power users can also pre-seed
-- SMROptInPack_Optional = { MultipleSuns = true } before this mod loads.
-- `SMROptInPack.ListFixes()` reports it as inactive until enabled.
--
-- Why it exists: the shipped game hard-limits the Artificial Sun to ONE per
-- colony — it is a `build_once` wonder, enforced colony-wide including
-- construction sites (Building.lua:3691-3692, BuildMenu.lua:711-719 counting
-- UIColony.labels). PT-26 (2026-07-27) proved that makes the pack's original
-- F39 fix unreachable dead code in an unmodded game: two suns can never
-- coexist, so `labels.ArtificialSun[1]` is always the only sun. But players DO
-- run "allow multiple wonders" mods, and any such mod walks straight into the
-- vanilla panel-binding bug this module repairs — so the module ships both
-- halves together: it lifts the limit AND makes the lifted limit actually work.
--
-- WHAT THIS SHIPS:
--
--   1. LIMIT LIFT — `BuildingTemplates.ArtificialSun.build_once = false`,
--      applied through SMROptInPack.OnDataReady (template presets exist only
--      after DataLoaded — the GlobalMap is EMPTY at mod-load time, the F75
--      lesson — and the engine re-posts Msg("DataChanged", false) right after
--      every DataLoaded, Dlc.lua:715-717, so the patch re-asserts idempotently;
--      OnDataReady also carries the ENABLE path, where DataLoaded never fires
--      at all and this lift used to be skipped for the session — F87). The
--      build menu re-reads CanBuildOnlyOnce() live (verified in-session via a
--      console toggle of this exact flag), so no UI refresh is needed.
--      `wonder` stays true — sight category and placement behavior untouched.
--
--   2. BINDING FIX (absorbed from the deleted Fix_SecondArtificialSun.lua,
--      unchanged) — SolarPanelBase:GameInit (SolarPanel.lua:8-14) only ever
--      tests labels.ArtificialSun[1] with TestSunPanelRange; a panel built in
--      range of sun #2 only never registers (the reverse direction is correct,
--      ArtificialSun.lua:34-48, so the bug shows exactly when the panel is
--      built last — the common case). Chained post-wrapper: the shipped body
--      runs untouched; if it left the panel unlit we walk the rest of the
--      label and hand the first sun in range to the shipped SetArtificialSun
--      (:66-69), which also refreshes production. GameInit is a combined
--      method (DefineCombinedMethod, CommonLua\Classes\_object.lua:22)
--      assembled after mod load, so writing onto SolarPanelBase reaches every
--      panel class and RCSolar. Plus the LoadGame sweep: `artificial_sun` is a
--      persisted member nothing re-evaluates, so panels already dark beside a
--      second sun in a modded save stay dark without one.
--
-- However a save acquired its extra suns (this module, a third-party limit
-- lifter, or a B&B-era import), the resulting state is identical — two suns in
-- city.labels.ArtificialSun — and that state is all the binding fix reads.
-- With the module OFF, vanilla is untouched in both directions: the limit
-- stays, and the binding bug is unreachable without the lift.
--
-- Savegame footprint: none. The lifted limit is a preset patch re-applied per
-- session; suns and panels built under it are ordinary game objects, and a
-- save with two standing suns loads fine without the module (the second sun
-- keeps working — only NEW panels beside it would hit the vanilla binding bug
-- again, and the build menu simply refuses further suns).

SMROptInPack_Optional = rawget(_G, "SMROptInPack_Optional") or {}

local FIX_ID = "MultipleSuns"

local log = SMROptInPack.Log

local function module_active()
	local fix = SMROptInPack.fixes[FIX_ID]
	return fix and fix.status == "active"
end

local function find_sun_in_range(panel)
	local city = panel.city
	local suns = city and city.labels and city.labels.ArtificialSun
	if not suns then return end
	for _, sun in ipairs(suns) do
		if IsValid(sun) and TestSunPanelRange(sun, panel) then
			return sun
		end
	end
end

-- Binding-fix half, installed at FILE SCOPE (audit A2, 2026-07-29) so the
-- wrap is part of the classdef when GameInit's combined method is assembled
-- and reaches every panel class and RCSolar even on a first mid-session
-- enable. Guarded by the same existence checks apply() runs, so a missing
-- target degrades to apply()'s reason string instead of erroring at load.
do
	local SP = rawget(_G, "SolarPanelBase")
	if type(SP) == "table" and type(SP.GameInit) == "function"
			and type(SP.SetArtificialSun) == "function"
			and type(rawget(_G, "TestSunPanelRange")) == "function" then
		local orig = SP.GameInit
		function SP:GameInit(...)
			local r = orig(self, ...)
			-- FIX (F39, absorbed): the shipped body only ever tested
			-- labels.ArtificialSun[1]. module_active makes the Mod Options
			-- toggle live: off = exact vanilla behavior.
			if module_active() and not self.artificial_sun then
				local sun = find_sun_in_range(self)
				if sun then self:SetArtificialSun(sun) end
			end
			return r
		end
	end
end

-- forward locals — defined below, captured by the Register def's callbacks
local lift_build_limit, restore_build_limit

SMROptInPack.Register(FIX_ID, {
	title = "OPTIONAL: build more than one Artificial Sun (and panels bind to any sun in range)",
	optional = true,
	-- Mod Options live-toggle hooks (D05): the wrappers gate themselves on
	-- registry status, but the template flag is state, not a call path — flip
	-- it explicitly when the toggle changes mid-session.
	on_activate = function() lift_build_limit() end,
	on_deactivate = function() restore_build_limit() end,
	apply = function()
		if not SMROptInPack.OptionEnabled("MultipleSuns") then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end

		-- the binding-fix wrap is installed at file scope above — see the
		-- header; the limit lift waits for DataLoaded. apply() only validates.
		local SP = rawget(_G, "SolarPanelBase")
		if type(SP) ~= "table" or type(SP.GameInit) ~= "function"
				or type(SP.SetArtificialSun) ~= "function" then
			return "SolarPanelBase.GameInit/SetArtificialSun not found (game update changed it?)"
		end
		if type(rawget(_G, "TestSunPanelRange")) ~= "function" then
			return "TestSunPanelRange not found (game update changed it?)"
		end
	end,
})

-- Limit lift: BuildingTemplates exists EMPTY before DataLoaded, so the patch
-- runs from the messages below. Gating on the registry status covers both the
-- opt-in flag and the SMROptInPack_Disabled veto (a vetoed fix never reaches
-- "active"), which OnMsg handlers must re-check themselves (the F75 lesson).
local lifted_logged = false
local we_lifted = false
local data_loaded = false
function lift_build_limit()
	if not module_active() then return end
	local templates = rawget(_G, "BuildingTemplates")
	local sun = type(templates) == "table" and templates.ArtificialSun
	if type(sun) ~= "table" then
		-- Before DataLoaded this miss is EXPECTED (the GlobalMap exists empty;
		-- an early DataChanged can land here) — only a post-DataLoaded miss is
		-- a real "game update renamed it" signal worth surfacing.
		local fix = SMROptInPack.fixes[FIX_ID]
		if data_loaded and fix and fix.detail == "" then
			fix.detail = "BuildingTemplates.ArtificialSun not found — build limit NOT lifted (binding fix still active)"
			log("%s: %s", FIX_ID, fix.detail)
		end
		return
	end
	local fix = SMROptInPack.fixes[FIX_ID]
	if fix and fix.detail ~= "" and fix.detail:find("ArtificialSun not found", 1, true) then
		fix.detail = ""   -- clear a transient pre-DataLoaded miss
	end
	if sun.build_once then
		sun.build_once = false
		we_lifted = true
		if not lifted_logged then
			lifted_logged = true
			log("%s: Artificial Sun build-once limit lifted", FIX_ID)
		end
	end
end

-- Mod Options live-off (D05): put the limit back — but only if WE lifted it,
-- so a third-party limit mod's own lift is never stomped.
function restore_build_limit()
	if not we_lifted then return end
	local templates = rawget(_G, "BuildingTemplates")
	local sun = type(templates) == "table" and templates.ArtificialSun
	if type(sun) == "table" and not sun.build_once then
		sun.build_once = true
		we_lifted = false
		lifted_logged = false
		log("%s: Artificial Sun build-once limit restored (module turned off)", FIX_ID)
	end
end

-- F87 sweep: this used to hang off DataLoaded/DataChanged alone, and neither
-- fires when the player ticks the mod at the main menu — so on the enable path
-- (with the toggle already ON from a previous session, which is account state)
-- the build-once limit was never lifted for that whole session, while the
-- file-scope binding half worked. OnDataReady adds ClassesBuilt/ModsReloaded and
-- still re-asserts on DataChanged; the lift is idempotent either way.
SMROptInPack.OnDataReady(function()
	data_loaded = true
	lift_build_limit()
end)

-- Panels built beside a second sun BEFORE this module was enabled (typically
-- under a third-party limit mod) are still dark in the save; nothing re-runs
-- the range test for them.
OnMsg.LoadGame = SMROptInPack.WhenActive(FIX_ID, function()
	if type(rawget(_G, "AllMapsForEach")) ~= "function" then return end

	local lit = 0
	AllMapsForEach("map", "SolarPanelBase", function(panel)
		if not panel.artificial_sun then
			local sun = find_sun_in_range(panel)
			if sun then
				panel:SetArtificialSun(sun)
				lit = lit + 1
			end
		end
	end)

	if lit > 0 then
		log("%s: reconnected %d solar panel(s) to an Artificial Sun in range", FIX_ID, lit)
	end
end)
