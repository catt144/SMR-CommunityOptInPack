-- UI only, no saved class/field. Extend the existing resource row in place;
-- keep its title, stored/max readout, icon and grouping. Hub card is excluded.
-- Archived 1.1.1.405907 Lua/XDef/sectionStorageRow.generated.lua:27-45 and
-- InfopanelSlider.generated.lua:15-90 supply the row and slider presentation.
local D = rawget(_G, "SMROptInTrainDistribution")
if not D or not D.active or not sectionStorageRow or
	type(sectionStorageRow.OnContextUpdate) ~= "function" then return end

local function selection(row)
	local ctx = row.context
	local station, res = ctx and ctx[1], ctx and ctx.res
	if not station or not res then return end
	local entry, hub = D.Get(station, res)
	if not hub then return end
	local cap = station:GetMaxStorage(res)
	local percent = entry and entry.percent or (cap > 0 and MulDivRound(station.desired_amount, 100, cap) or 0)
	return station, res, entry and entry.mode or "balanced", percent, hub
end

local function controls(row)
	local panel = XWindow:new({ LayoutMethod = "VList", LayoutVSpacing = 0,
		Margins = box(0, 0, 0, 2), FoldWhenHidden = true }, row.idContent, row.context)
	local line = XWindow:new({ LayoutMethod = "HList", LayoutHSpacing = 8,
		MinHeight = 24, MaxHeight = 24 }, panel, row.context)
	local function checkbox(label, mode)
		return XCheckButton:new({ Text = Untranslated(label), TextStyle = "InfopanelText",
			TextColor = RGB(255, 255, 255), IconColor = RGB(255, 255, 255),
			MinWidth = 78, MaxWidth = 90, MinHeight = 24, MaxHeight = 24,
			IconScale = point(420, 420), VAlign = "center",
			RolloverTitle = Untranslated(label), RolloverTemplate = "Rollover",
			RolloverText = Untranslated(mode == "export"
				and "Drones fill this station. Trains take stock above the slider to the hub."
				or "Trains bring stock up to the slider. Local drones distribute it to the area."),
			OnChange = function(button, checked)
				if panel.refreshing then return end
				local station, res, _, percent = selection(row)
				if station then D.Set(station, res, checked and mode or "balanced", percent) end
			end,
		}, line, row.context)
	end
	panel.import = checkbox("Import", "import")
	panel.export = checkbox("Export", "export")
	panel.slider = InfopanelSlider:new({ Min = 0, Max = 100, StepSize = 1,
		MinWidth = 110, MaxWidth = 160, Margins = box(0, 0, 0, 0),
		RolloverTemplate = "Rollover", RolloverTitle = Untranslated("Station amount"),
		RolloverText = Untranslated("Export: minimum left by trains. Import: train fill target. Balanced: amount held by trains. Neither box checked is balanced."),
		ScrollTo = function(slider, value)
			local result = InfopanelSlider.ScrollTo(slider, value)
			if not panel.refreshing then
				local station, res, mode = selection(row)
				if station then D.Set(station, res, mode, slider:GetScroll()) end
			end
			return result
		end,
		OnShortcut = function(slider, shortcut, source)
			if shortcut == "LeftShoulder" or shortcut == "RightShoulder" then
				slider:ScrollTo(Clamp(slider:GetScroll() + (shortcut == "LeftShoulder" and -1 or 1), 0, 100))
				return "break"
			end
			return InfopanelSlider.OnShortcut(slider, shortcut, source)
		end,
	}, line, row.context)
	-- Vanilla's slider art has a 320-wide minimum in its children. Keep the
	-- same art at this row's width; no extra section or different widget style.
	panel.slider.idBar:SetMinWidth(0)
	for _, child in ipairs(panel.slider.idBar) do child:SetMinWidth(0) end
	panel.note = XText:new({ TextStyle = "InfopanelText", Translate = true,
		Margins = box(0, 1, 0, 0), MaxHeight = 24, Shorten = true,
		HandleMouse = false }, panel, row.context)
	row.distribution_controls = panel
	if row.window_state == "open" then panel:Open() end
	return panel
end

local previous = sectionStorageRow.OnContextUpdate
function sectionStorageRow:OnContextUpdate(context, ...)
	local result = table.pack(previous(self, context, ...))
	local station, res, mode, percent, hub = selection(self)
	local panel = self.distribution_controls
	if not station or not self.idContent then
		if panel then panel:SetVisible(false) end
		return table.unpack(result, 1, result.n)
	end
	panel = panel or controls(self)
	panel:SetVisible(true)
	panel.refreshing = true
	panel.import:SetCheck(mode == "import")
	panel.export:SetCheck(mode == "export")
	panel.slider:SetScroll(percent)
	local enabled = station:IsResourceEnabled(res)
	panel.import:SetEnabled(enabled)
	panel.export:SetEnabled(enabled)
	panel.slider:SetEnabled(enabled)
	local n = MulDivRound(station:GetMaxStorage(res), percent, 100) / const.ResourceScale
	local label = mode == "export" and "Keep" or mode == "import" and "Fill to" or "Hold"
	local note = string.format("%s %g (%g%%)", label, n, percent)
	if not D.HasDroneCoverage(station) then note = note .. " · No drones in range" end
	if hub.demand and hub.demand[res] and hub.demand[res]:GetTargetAmount() <= 0 then note = note .. " · Hub full" end
	panel.note:SetText(Untranslated(note))
	panel.refreshing = false
	return table.unpack(result, 1, result.n)
end

print("[TrainDistribution] station resource-row controls loaded")
