-- D17 — OPTIONAL module, OFF BY DEFAULT: the Train Hub.
--
-- Owner rulings: train spec docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md §4.8-§4.10
-- and §10 (the hub, its drones, distribution, bay, upgrades, economy and module-off default,
-- OI-19 2026-10-01); brief 34's checkpoint (2026-10-02): station food spoilage goes with this
-- module, and the StationRows module is forced on while this one is on.
--
-- Parts, loaded right after this file (FIX_POLICY §8): Code/TrainHub_20_TrainHub.lua (the
-- building, upgrades, track work), TrainHub_30_TrainHubDrones.lua,
-- TrainHub_60_StationSpoilage.lua and TrainHub_70_TrainBay.lua; the template SMROptInTrainHub6 (Data/ + the generated class) and three
-- entities. They always load, so a placed hub keeps working with this module off (OI-19).
--
-- Toggle semantics, both directions, including the first mid-session enable:
--   ON  the Train Hub is in the Stations build menu; train stations keep their food; every
--       station has the rows (StationRows forced on).
--   OFF no new hubs: the build menu hides it (a lock below). Built hubs, their drones,
--       upgrades and their networks' rows keep working. Stations spoil food as vanilla. Hubless
--       stations follow the StationRows toggle.
-- Removing the mod with placed hubs is unsupported (FIX_POLICY §0): the description says to
-- demolish every hub first. Saves: the hub's names in the FIX_POLICY persisted-name inventory.

local FIX_ID = "TrainHub"
local TEMPLATE = "SMROptInTrainHub6"

local function rows_reapply()
	local reapply = SMROptInPack.StationRowsReapply
	if type(reapply) == "function" then reapply() end
end

SMROptInPack.Register(FIX_ID, {
	title = "OPTIONAL: the Train Hub, a three-line junction station with its own drones and upgrades",
	optional = true,
	apply = function()
		if not SMROptInPack.OptionEnabled(FIX_ID) then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end
	end,
	on_activate = rows_reapply,
	on_deactivate = rows_reapply,
})

-- Off: the build menu leaves the hub out (BuildMenu.lua:731 on 1.1.1.406343 returns false for a
-- locked template). Read per call, so a live toggle needs no hook state.
function OnMsg.GetAdditionalBuildingLocks(template, locks)
	if not template or (template.template_name ~= TEMPLATE and template.class ~= TEMPLATE
		and template.id ~= TEMPLATE) then return end
	if not SMROptInPack.IsActive(FIX_ID) then locks.smr_train_hub_module_off = true end
end
