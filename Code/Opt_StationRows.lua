-- D16 — OPTIONAL module, OFF BY DEFAULT: per-resource station rows.
--
-- Owner rulings (train spec docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md §4.7, §4.8,
-- §10 "Brief 34's checkpoint"): every vanilla train station's resource rows cycle Balanced /
-- Export / Import / Not accepted, with a slider, with or without a Train Hub (2026-10-02,
-- "Some people may never want to use the hub"). Forced on while the TrainHub module is on
-- (owner, 2026-10-02).
--
-- Parts, loaded right after this file (FIX_POLICY §8): Code/StationRows_10_TrainFloor.lua
-- (the transient claims the rows use; its standing hold serves the hub),
-- StationRows_40_TrainDistribution.lua (rows, train views, desired amounts) and
-- StationRows_45_TrainDistributionUI.lua (the native row hook).
-- They always load: a built hub's network keeps its rows whatever the toggles say, because
-- they are part of the hub. This toggle gates the HUBLESS rows, per call
-- (SMROptInTrainDistribution's hubless gate and D.RowsOn).
--
-- Toggle semantics, both directions, including the first mid-session enable:
--   ON  hubless stations show the four-state rows; any stored settings apply at once.
--   OFF hubless stations show vanilla rows and get vanilla train transport; their stored
--       settings stay on the station, unused, and each station's vanilla desired amounts are
--       restored. Nothing changes while the TrainHub module is on.
-- Saves: SMROptIn_station_rows on a station (FIX_POLICY persisted-name inventory row 20);
-- hubless baselines are restored to vanilla while saving.

local FIX_ID = "StationRows"

-- Re-apply every station through the rows' own reconciler: OFF restores vanilla desired
-- amounts (the rows read as absent), ON applies the stored settings. No colony, no work.
local function reapply()
	local D = rawget(_G, "SMROptInTrainDistribution")
	if type(D) == "table" and D.active and type(D.Reapply) == "function" and rawget(_G, "UIColony") then
		D.Reapply()
	end
end
SMROptInPack.StationRowsReapply = reapply

SMROptInPack.Register(FIX_ID, {
	title = "OPTIONAL: Import / Export / Balanced / Not accepted and a slider on every train station's resource rows",
	optional = true,
	apply = function()
		if not SMROptInPack.OptionEnabled(FIX_ID) then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end
	end,
	on_activate = reapply,
	on_deactivate = reapply,
})
