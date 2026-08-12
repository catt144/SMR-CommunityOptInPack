-- D09 — OPTIONAL stat dials, BASE (= vanilla) BY DEFAULT. Not a bug fix.
--
-- Two Mod Options dropdowns (Options → Mod Options → Community Opt-In Pack):
--   * "Drone speed"          — 1x (base) / 2x / 3x / 5x
--   * "Drone carry capacity" — +0 (base) / +1 / +2
-- Decision record: docs/DRONE_OVERHAUL_OPTIONS.md, DECISION 2026-07-29 —
-- the drone overhaul ships with player-facing stat dials (breakthrough-lottery
-- insurance and hauling relief), while the structural dispatch work stays
-- gated on the v2 harness data. These dials are relief, not the fix for the
-- structural hauling bottleneck — the A/B save was AT the vanilla stat
-- ceiling and hauling was still 88% of elapsed repair time.
--
-- MECHANISM — the exact machinery the game's own techs use
-- (Effect_ModifyLabel, MarsGameEffects.lua:161-178):
--   * Speed: a percent Modifier on label "Drone", prop `move_speed`, on
--     UIColony — identical to Advanced Drone Drive (Data/TechPreset.lua:702-706,
--     Percent=40) and Low-G Drive. Percents stack ADDITIVELY on base
--     (Modifiers.lua:100,112-113), so the worst case is 5x + both speed
--     breakthroughs = base × (1 + 0.60 + 4.00) = 8064 — under the 10000
--     raw-set the 2026-07-29 live probe proved clean (no C-side clamp, no
--     clipping/pathing failures at ultra). Drones only — rovers/shuttles
--     untouched.
--   * Carry: an amount Modifier on label "Consts", prop
--     `DroneResourceCarryAmount` (base 1, __const.lua:637-641) — identical to
--     Artificial Muscles (Data/TechPreset.lua:626-630, Amount=1); plain
--     addition on one global, consumed at Drone.lua:719 and auto-rebuilt via
--     OnMsg.ConstValueChanged (Drone.lua:724).
-- New drones inherit label modifiers automatically (LabelContainer:AddToLabel,
-- LabelContainer.lua:17-28); SetLabelModifier with the same id first removes
-- the old modifier from every labeled object, so re-applying is idempotent
-- (LabelContainer.lua:59-78).
--
-- DIAL SEMANTICS (both directions, live):
--   * Choice values arrive as the choice STRING itself (the text IS the
--     value, Mod.lua:2764-2771) — mapped to numbers below; unknown/missing
--     values read as base.
--   * Reconciled from CurrentModOptions on ApplyModOptions (player hits
--     Apply — live, both directions), on CityStart (new game) and on
--     PostLoadGame (loaded saves may carry a previous session's persisted
--     modifiers under our ids — replaced or removed to match the CURRENT
--     dial positions).
--   * Base position, veto (SMROptInPack_Disabled) or error status = modifiers
--     REMOVED BY ID = byte-vanilla behavior (FIX_POLICY §5), including
--     cleaning a stale modifier out of a loaded save.
--
-- SAVE FOOTPRINT (FIX_POLICY §3): no new classes or GameVars. Non-base dials
-- persist vanilla `Modifier` objects under string ids
-- ("SMRFixPack_DroneSpeedDial" / "SMRFixPack_DroneCarryDial") in UIColony's
-- label_modifiers — a save made with a dial active loads CLEAN without the
-- mod (vanilla class, string key), but keeps the boost permanently. Set both
-- dials to base (or load once with the mod) before uninstalling; documented
-- in MOD_DESCRIPTION.md.
--
-- NOT a ModItemOptionToggle module: the two option names (DroneSpeedDial /
-- DroneCarryDial) are NOT Register ids, the module registers WITHOUT
-- `optional = true` (00_Core's boolean reconciler must not manage it), and it
-- reports `active` whenever its targets validate — "active at base" simply
-- means the dial machinery is armed and behavior is vanilla. FIX_POLICY §5's
-- dial addendum covers this shape.

SMROptInPack_Disabled = rawget(_G, "SMROptInPack_Disabled") or {}

local ID = "DroneStatDials"
local SPEED_MOD_ID = "SMRFixPack_DroneSpeedDial"
local CARRY_MOD_ID = "SMRFixPack_DroneCarryDial"

-- Choice text → effect. The strings must stay byte-identical to items.lua's
-- ChoiceList entries and metadata.lua's default_options values.
-- Dial range widened from the DECISION's 1.0x/1.5x/2.0x by user call,
-- 2026-07-29 pre-build, after the no-clamp probe: labels mean "+(N-1)×100%
-- of BASE speed added", stacking additively with tech percents.
local SPEED_PERCENT = { ["1x (base)"] = 0, ["2x"] = 100, ["3x"] = 200, ["5x"] = 400 }
local CARRY_ADD     = { ["+0 (base)"] = 0, ["+1"] = 1, ["+2"] = 2 }

-- Validate every target before installing anything; apply() reports failures.
-- Pre-flattening rules (ENGINE_FACTS, the F64 lesson — and this module's own
-- first A/B leg 2026-07-29, which FAILed on checking Modifier.new here):
-- a classdef exposes only members it declares ITSELF, so file scope may only
-- check presence (Modifier declares data fields, `new` is inherited) and
-- methods on their DECLARING class (SetLabelModifier is declared on
-- LabelContainer itself, Lua/LabelContainer.lua:59). Capability checks that
-- need the BUILT class (`Modifier:new`) and the modifiable-prop scale table
-- live in the reapply guard, which runs post-build at msg time.
local install_error
do
	if type(rawget(_G, "Modifier")) ~= "table" then
		install_error = "Modifier class not found (game update changed it?)"
	end
	local LC = rawget(_G, "LabelContainer")
	if not install_error
			and (type(LC) ~= "table" or type(LC.SetLabelModifier) ~= "function") then
		install_error = "LabelContainer.SetLabelModifier not found (game update changed it?)"
	end
end

-- What the dials currently ask for; anything but healthy+active reads as base.
local function DesiredDials()
	-- Handlers re-check BOTH the veto and the registry status per call
	-- (FIX_POLICY §2, the A1 lesson). Off in any way = base = remove.
	if SMROptInPack_Disabled[ID] or not SMROptInPack.IsActive(ID) then
		return 0, 0
	end
	local opts = CurrentModOptions
	if type(opts) ~= "table" then
		return 0, 0
	end
	return SPEED_PERCENT[opts.DroneSpeedDial] or 0, CARRY_ADD[opts.DroneCarryDial] or 0
end

local function ReapplyDials()
	-- UIColony is a GameVar (Colony.lua:102) — only touched here, at msg time.
	-- In the main menu it is not a Colony yet; the CityStart/PostLoadGame
	-- handlers reconcile once a game is up.
	local colony = rawget(_G, "UIColony")
	if type(colony) ~= "table" or type(colony.SetLabelModifier) ~= "function" then
		return
	end
	local M = rawget(_G, "Modifier")
	if type(M) ~= "table" or type(M.new) ~= "function" then
		return -- classes not built yet (never at msg time) or a game update
	end
	if not (rawget(_G, "HasModifiablePropScale")
			and HasModifiablePropScale("move_speed")
			and HasModifiablePropScale("DroneResourceCarryAmount")) then
		return -- a game update un-registered a prop; leave everything untouched
	end
	local speed_pct, carry_add = DesiredDials()
	colony:SetLabelModifier("Drone", SPEED_MOD_ID, speed_pct ~= 0 and Modifier:new{
		prop = "move_speed",
		amount = 0,
		percent = speed_pct,
	} or nil)
	colony:SetLabelModifier("Consts", CARRY_MOD_ID, carry_add ~= 0 and Modifier:new{
		prop = "DroneResourceCarryAmount",
		amount = carry_add * GetModifiablePropScale("DroneResourceCarryAmount"),
		percent = 0,
	} or nil)
end

if not install_error then

	function OnMsg.ApplyModOptions(mod_id)
		if mod_id == "SMR_CommunityOptInPack" then
			ReapplyDials()
		end
	end

	OnMsg.CityStart = ReapplyDials
	OnMsg.PostLoadGame = ReapplyDials

end -- install guard

SMROptInPack.Register(ID, {
	title = "OPTIONAL: Drone speed / carry capacity dials (set them in Mod Options)",
	apply = function()
		if install_error then
			return install_error
		end
		-- Always armed; behavior is vanilla until a dial leaves base. No
		-- opt-in gate here — the dials themselves are the control surface.
	end,
})
