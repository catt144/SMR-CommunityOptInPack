-- D01 — OPTIONAL module, OFF BY DEFAULT. Not a bug fix.
--
-- Enable it in-game: Options → Mod Options → Community Fix Pack: Opt-In Modules (D05; toggles
-- take effect immediately, both directions — including the FIRST mid-session
-- enable: the hook is installed at FILE SCOPE (classdef time, so it propagates
-- through class flattening) and gates per call on SMROptInPack.IsActive, the
-- Opt_DroneOverhaul pattern; the Register apply() only validates targets /
-- reports the opt-in status. (Before the 2026-07-29 audit fix the wrap was
-- installed from apply(), which on a first in-game enable ran AFTER class
-- flattening — invisible to the derived rocket classes until restart.) Other
-- mods / power users can also pre-seed SMROptInPack_Optional = { ClassicRockets
-- = true } before this mod loads. `SMROptInPack.ListFixes()` reports it as
-- inactive until enabled.
--
-- Why it exists: the remaster deliberately changed rocket logistics, and the
-- BUGS.md D01 entry records the verdict that this is a redesign and NOT a defect
-- — the legacy always-on behaviour survives only in the dead legacy class
-- (RocketBase:CreateExportRequests, Lua\Buildings\RocketBase.lua:1729-1736, whose
-- `allow_export` / `export_requests` / `max_export_storage` fields are nilled on
-- migration, RocketCompatibility.lua:58,95-99). Players who preferred the old
-- behaviour get it here, opt-in, so the pack itself stays a pure bug-fix mod
-- (FIX_POLICY §4). The file is named Opt_* rather than Fix_* for exactly that
-- reason.
--
-- WHAT THIS SHIPS: automatic refuelling of a landed rocket.
--
-- UniversalRocketBase:GetFuelResourceRequest (Lua\UniversalRocket.lua:1639-1650)
-- returns 0 whenever there is no `arrival_loc`, and manual landing clears
-- `arrival_loc` (CmdLand, :414). So a rocket sitting on its pad with no
-- destination picked asks for no fuel at all, and only starts being refuelled
-- once you have chosen where it is going — which is the "my rocket never has
-- fuel when I need it" complaint. That request feeds the drone demand directly:
-- CargoTransporterNew:UpdateCargoResourceRequests takes
-- `additional_amount = is_refuel_resource and self:GetFuelResourceRequest()`
-- straight into the demand (CargoTransporterNew.lua:1249-1265), so raising it is
-- the whole mechanism.
--
-- With this module on, a player-controlled rocket parked at the colony with no
-- destination keeps its launch ration requested, and drones top it up while it
-- waits. Neither notification branch fires in that state — they live in the
-- UniversalRocketBase:UpdateCargoResourceRequests OVERRIDE and both require
-- `arrival_loc` (UniversalRocket.lua:1687-1692) — so there is no "refuelled"
-- spam and no entry in g_LandedRocketsInNeedOfFuel. (A third path,
-- DroneUnloadResource's Msg("RocketRefueled") at CargoTransporterNew.lua:1367-1371,
-- can fire when the ration tops off, but its listeners are benign here:
-- RocketRefueledInADay is gated on arrival_loc (UniversalRocket.lua:1790), and
-- the remaining listener is a refuel achievement event (Achievement.lua:263) —
-- live on PC (mods only block achievements on console, Achievement.lua:61-63),
-- but a parked rocket topping off its ration IS a refuel, so crediting it is
-- defensible.)
--
-- Chained wrapper, and only when the shipped answer is 0 — every case the game
-- already answers, including F69's asteroid-lander reserve, falls through
-- untouched.
--
-- WHAT THIS DOES NOT SHIP: the standing Rare Metals export request. That half of
-- the D01 sketch is a gameplay system, not a hook: the modern cargo request is
-- driven by SetCargoRequest / the payload dialog / Automated Mode's
-- `export_above` thresholds, and injecting a permanent demand into it touches the
-- same machinery as F50, F68, F70 and F71. It is deliberately left for a design
-- decision plus an in-game test rather than improvised here — see the D01 entry
-- in docs/BUGS.md.

SMROptInPack_Optional = rawget(_G, "SMROptInPack_Optional") or {}

-- Validate every target before installing anything; apply() reports failures.
-- All three rocket methods are declared on UniversalRocketBase itself (:826
-- and :2140), so the classdef lookup is valid even though mod code loads
-- before the classes are flattened.
local install_error = SMROptInPack.Require("ClassicRockets", {
	{ class = "UniversalRocketBase", method = "GetFuelResourceRequest" },
	{ class = "UniversalRocketBase", method = "GetDepartureLocType" },
	{ class = "UniversalRocketBase", method = "IsPlayerControlled" },
	{ class = "CargoTransporterNew", method = "UpdateCargoResourceRequests" },
})

if not install_error then

	local R = UniversalRocketBase
	local orig = R.GetFuelResourceRequest
	function R:GetFuelResourceRequest(...)
		local amount, reserve = orig(self, ...)
		-- D01: parked at the colony with nowhere to go. The shipped answer is 0
		-- only because no destination is selected; keep the launch ration
		-- requested so drones fuel it while it waits. The IsActive check makes
		-- the Mod Options toggle live: off = shipped answer, always.
		if (amount or 0) <= 0 and SMROptInPack.IsActive("ClassicRockets")
				and not self.arrival_loc
				and self:IsPlayerControlled()
				and self:GetDepartureLocType() == "our_colony" then
			return Max(0, self.FuelResourceAmount or 0), reserve
		end
		return amount, reserve
	end

end -- install guard

SMROptInPack.Register("ClassicRockets", {
	title = "OPTIONAL: rockets refuel while parked, without a destination selected",
	optional = true,
	apply = function()
		if install_error then
			return install_error
		end
		if not SMROptInPack.OptionEnabled("ClassicRockets") then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end
	end,
})
