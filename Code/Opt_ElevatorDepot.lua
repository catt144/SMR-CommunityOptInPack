-- D18 — OPTIONAL module, OFF BY DEFAULT: the Elevator Depot.
--
-- Owner rulings: train spec docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md §11 (the
-- crossing between the surface and the underground: two manually placed halves, one pair per
-- colony, surface-owned Import / Export rows, the scheduled cabin, 250/500 capacity and its
-- upgrade, Drone Access default off).
--
-- Parts, loaded right after this file (FIX_POLICY §8): Code/ElevatorDepot_10_ElevatorDepot.lua;
-- the template SMROptInElevatorDepotDev (Data/ + the generated class; "Dev" is save contract,
-- owner 2026-10-02, never shown) and two entities. They always load, so a built pair keeps
-- working with this module off. The depot needs neither the hub nor the StationRows module.
--
-- Toggle semantics, both directions, including the first mid-session enable:
--   ON  the Elevator Depot is in the Stations build menu (still needing the underground).
--   OFF no new halves: the build menu hides it (a lock below). A built pair keeps working.
-- Removing the mod with a placed pair is unsupported (FIX_POLICY §0): the description says to
-- demolish both halves first. Saves: the depot's names in the FIX_POLICY persisted-name inventory.

local FIX_ID = "ElevatorDepot"
local TEMPLATE = "SMROptInElevatorDepotDev"

SMROptInPack.Register(FIX_ID, {
	title = "OPTIONAL: the Elevator Depot, a two-half train station carrying cargo between the surface and the underground",
	optional = true,
	apply = function()
		if not SMROptInPack.OptionEnabled(FIX_ID) then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end
	end,
})

-- Off: the build menu leaves the depot out (BuildMenu.lua:731 on 1.1.1.406343). Per call.
function OnMsg.GetAdditionalBuildingLocks(template, locks)
	if not template or (template.template_name ~= TEMPLATE and template.class ~= TEMPLATE
		and template.id ~= TEMPLATE) then return end
	if not SMROptInPack.IsActive(FIX_ID) then locks.smr_depot_module_off = true end
end
