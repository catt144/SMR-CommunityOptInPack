-- Native storage-row extension, owner rulings 79c0ec9, 817b778 / spec 4.7.
-- Archived 1.1.1.405907: Data/XDef/sectionStorageRow.lua and sectionDome.lua;
-- Lua/XDef/InfopanelActiveSection.generated.lua (idSectionTitles),
-- InfopanelSlider.generated.lua; Buildings/Station.lua:1003-1059.
-- XDefs ship compiled constructors, not evaluated XTemplate trees. Chain the
-- compiled row's context callback; keep its constructor, activation and children.
-- XDef checks/install happen at runtime, never as a file-level early return.
local D = rawget(_G, "SMROptInTrainDistribution")
if not D or not D.active or D.native_ui_registered then return end
D.native_ui_registered = true
local reported = {}
local function failure(reason)
	D.ui_error = reason
	if not reported[reason] then
		reported[reason] = true
		print("[TrainDistribution] " .. reason)
	end
end

-- Declaring methods used below. UI entries are checked only after XDefs exist.
D.UIRequire = {
	{ "Station", "ToggleAcceptResource" }, { "Station", "SetAcceptResourceState" },
	{ "Station", "GetResAcceptIcon" }, { "Station", "ResourceRolloverText" },
	{ "sectionStorageRow", "OnContextUpdate" },
	{ "InfopanelSlider", "ScrollTo" }, { "InfopanelSlider", "OnShortcut" },
	{ "XFontControl", "GetFontId" },
}
local function network(st)
	return IsValid(st) and IsKindOf(st, "Station") and D.HubFor(st)
end
local titles = { balanced = "Balanced", export = "Export", import = "Import", disabled = "Not accepted" }
local following = { balanced = "export", export = "import", import = "disabled", disabled = "balanced" }
local icons = {
	balanced = "UI/IconsRemaster/Sections/resource_storing.tga",
	export = "UI/IconsRemaster/Sections/elevator_resource_up.png",
	import = "UI/IconsRemaster/Sections/elevator_resource_down.png",
}
local help = {
	balanced = "Balanced: trains hold the selected amount; local drones use it as their desired amount.",
	export = "Export: trains take stock above the selected minimum to the hub. Local drones fill this station. A full hub refuses exports.",
	import = "Import: trains bring stock from the hub up to the selected amount. Local drones may drain this station to zero.",
	disabled = "Not accepted: vanilla storage is disabled for this resource. Trains and drones may carry its remaining stock away.",
}
function D.RowState(st, res)
	local entry = D.Get(st, res)
	local cap = st:GetMaxStorage(res)
	local percent = entry and entry.percent or (cap > 0
		and Clamp(MulDivRound(st.desired_amount or 0, 100, cap), 0, 100) or 0)
	return not st:IsResourceEnabled(res) and "disabled" or entry and entry.mode or "balanced", percent, cap
end

local station_installed, row_installed
local function install_station()
	if station_installed then return true end
	for i = 1, 4 do
		local pair = D.UIRequire[i]
		local class = rawget(_G, pair[1])
		if not class or type(class[pair[2]]) ~= "function" then
			failure(pair[1] .. "." .. pair[2] .. " unavailable")
			return
		end
	end
	local toggle = Station.ToggleAcceptResource
	local set_accept = Station.SetAcceptResourceState
	local icon = Station.GetResAcceptIcon
	local rollover = Station.ResourceRolloverText
	Station.ToggleAcceptResource = function(st, res, broadcast, ...)
		if not network(st) then return toggle(st, res, broadcast, ...) end
		local mode = D.RowState(st, res)
		if not broadcast then mode = following[mode] end
		-- Preserve vanilla's city-wide scope and its own disabled/request-flag path.
		for _, target in ipairs(broadcast and st.city.labels.Station or { st }) do
			if not broadcast or target ~= st then
				set_accept(target, res, mode == "disabled" and "disabled" or "store", false)
				if network(target) and mode ~= "disabled" then
					local _, percent = D.RowState(target, res)
					D.Set(target, res, mode, percent)
				end
				ObjModified(target)
			end
		end
	end
	Station.GetResAcceptIcon = function(st, res, ...)
		if not network(st) then return icon(st, res, ...) end
		return icons[D.RowState(st, res)] or "UI/IconsRemaster/Sections/resource_no_accept.png"
	end
	Station.ResourceRolloverText = function(st, res, ...)
		if not network(st) then return rollover(st, res, ...) end
		local mode, percent, cap = D.RowState(st, res)
		local text = help[mode] .. "<newline><newline>Slider: " .. tostring(percent)
			.. "% of current capacity (" .. tostring(MulDivRound(cap, percent, 100) / const.ResourceScale) .. ")."
		if not D.HasDroneCoverage(st) then text = text .. "<newline><newline>No drones in range — trains only." end
		return Untranslated(text)
	end
	station_installed = true
	return true
end

-- Native word wrapping splits a word only when it cannot fit a whole line
-- (1.1.1.405907 CommonLua/X/XTextParser.lua:1057-1107). Keep the title's
-- allocated width from collapsing to the width of a shorter wrapped line.
local function fit_title(title)
	local font = title:GetFontId()
	local sx, sy = title.scale:xy()
	local padding = title:GetPadding()
	local width = 154
	for word in (title.text or ""):gsub("<[^>]*>", ""):gmatch("%S+") do
		width = Max(width, math.ceil((UIL.MeasureText(word, font) + 1) * 1000 / sx)
			+ padding:minx() + padding:maxx())
	end
	title:SetMinWidth(width)
	title:SetMaxWidth(width)
	title:SetMaxHeight(math.ceil(2 * title.font_height * 1000 / sy)
		+ padding:miny() + padding:maxy())
end

local function make_slider(row, context)
	local title, right = row.idSectionTitle, row.idSectionTitleRight
	if not title or not right or title.parent ~= right.parent then
		failure("sectionStorageRow title line unavailable")
		return
	end
	local saved = { title_dock = title.Dock, title_width = title.MaxWidth,
		title_min_width = title.MinWidth, title_height = title.MaxHeight,
		title_shorten = title.Shorten, right_dock = right.Dock,
		title = row:GetTitle(), hint = row.RolloverHint, gamepad_hint = row.RolloverHintGamepad,
		focus_help = row.RolloverOnFocus }
	row.distribution_native = saved
	-- Reserve the native right title first; the existing left title and the new
	-- slider share the remaining line. Neither the row nor idContent gains height.
	right:SetDock("right")
	title:SetDock("left")
	title:SetMaxWidth(154)
	title:SetShorten(true)
	-- XWindow.UpdateMeasure clamps to MaxHeight, while SetLayoutSpace with
	-- VAlign=stretch takes the parent's height. Contribute zero height, then fill
	-- the native title line: the slider cannot make even a short row taller.
	-- Archived 1.1.1.405907 CommonLua/X/XWindow.lua:623-665,744-794.
	local slider = InfopanelSlider:new({ Id = "idDistributionSlider", Dock = "box", VAlign = "stretch",
		MinWidth = 64, MinHeight = 0, MaxHeight = 0, Margins = box(6, 0, 6, 0),
		Min = 0, Max = 100, StepSize = 1, RolloverTemplate = "", RolloverOnFocus = false,
		OnScroll = function(self, value)
			local ctx = row.context
			local st, res = ctx[1], ctx.res
			if not network(st) then return end
			local mode = D.RowState(st, res)
			if mode ~= "disabled" then D.Set(st, res, mode, value) end
		end,
		OnShortcut = function(self, shortcut, source)
			if shortcut == "LeftShoulder" or shortcut == "RightShoulder" then
				if self:GetEnabled() then
					self:ScrollTo(Clamp(self:GetScroll() + (shortcut == "LeftShoulder" and -1 or 1), 0, 100))
				end
				return "break"
			end
			return InfopanelSlider.OnShortcut(self, shortcut, source)
		end,
	}, title.parent, context)
	-- The native slider's art has a 320px minimum at both levels.
	slider.idBar:SetMinWidth(0)
	for _, child in ipairs(slider.idBar) do child:SetMinWidth(0) end
	row.distribution_slider = slider
	if row.window_state == "open" then slider:Open() end
	return slider
end

local function update_row(row, context)
	local st, res = context and context[1], context and context.res
	if not st or not res or not network(st) then
		local saved = row.distribution_native
		if saved then
			row.distribution_slider:delete()
			row.distribution_slider, row.distribution_native = nil, nil
			row.idSectionTitle:SetDock(saved.title_dock)
			row.idSectionTitle:SetMinWidth(saved.title_min_width)
			row.idSectionTitle:SetMaxWidth(saved.title_width)
			row.idSectionTitle:SetMaxHeight(saved.title_height)
			row.idSectionTitle:SetShorten(saved.title_shorten)
			row.idSectionTitleRight:SetDock(saved.right_dock)
			row:SetTitle(saved.title)
			row:SetRolloverHint(saved.hint)
			row:SetRolloverHintGamepad(saved.gamepad_hint)
			row:SetRolloverOnFocus(saved.focus_help)
		end
		return
	end
	local slider = row.distribution_slider or make_slider(row, context)
	if not slider then return end
	local mode, percent = D.RowState(st, res)
	row:SetTitle(T{Untranslated("<resource(res)> · " .. titles[mode]), context})
	fit_title(row.idSectionTitle)
	row:SetRolloverOnFocus(false)
	row:SetRolloverHint(Untranslated("<left_click> " .. titles[following[mode]]
		.. "<newline><em>Ctrl + <left_click></em> Apply to all stations"))
	row:SetRolloverHintGamepad(Untranslated("<ButtonA> " .. titles[following[mode]]
		.. "<newline><ButtonY> Apply to all stations"))
	slider:SetEnabled(mode ~= "disabled")
	-- SetScroll does not invoke OnScroll: merely opening/refreshing a row saves nothing.
	slider:SetScroll(percent)
	if slider.window_state == "open" then slider:UpdateProgress() end
end

local function install_row()
	if row_installed then return true end
	for i = 5, #D.UIRequire do
		local pair = D.UIRequire[i]
		local class = rawget(_G, pair[1])
		if not class or type(class[pair[2]]) ~= "function" then
			failure(pair[1] .. "." .. pair[2] .. " unavailable")
			return
		end
	end
	local previous = sectionStorageRow.OnContextUpdate
	sectionStorageRow.OnContextUpdate = function(row, context, ...)
		local result = table.pack(previous(row, context, ...))
		update_row(row, context)
		return table.unpack(result, 1, result.n)
	end
	row_installed = true
	return true
end

-- Data/XDef/Infopanel.lua's AdjustConstrainedScale is a per-instance function.
-- Preserve its snapping, then clamp only a network station's local scale.
D.PanelScaleFloor = 800
local function walk(win, fn)
	fn(win)
	for _, child in ipairs(win) do walk(child, fn) end
end
function D.AttachStationRows(dlg)
	if not dlg or dlg.window_state == "destroying" or not IsKindOf(dlg, "ipBuilding") then return end
	local st = ResolvePropObj(dlg.context)
	if not IsValid(st) or not IsKindOf(st, "Station") then return end
	if not install_station() or not install_row() then return end
	D.ui_error = nil
	walk(dlg, function(win)
		if IsKindOf(win, "sectionStorageRow") then win:OnContextUpdate(win.context) end
		if IsKindOf(win, "XSizeConstrainedWindow") and not win.distribution_scale then
			-- Guard the actual per-template instance member, not the unused base default.
			local previous = rawget(win, "AdjustConstrainedScale")
			if type(previous) ~= "function" then failure("Infopanel scale callback unavailable"); return end
			win.distribution_scale = true
			win.AdjustConstrainedScale = function(self, x, y)
				x, y = previous(self, x, y)
				if network(ResolvePropObj(dlg.context)) then
					return Max(x, D.PanelScaleFloor), Max(y, D.PanelScaleFloor)
				end
				return x, y
			end
			win:InvalidateMeasure()
		end
	end)
end

function OnMsg.DialogOpen(dlg) D.AttachStationRows(dlg) end
-- Station methods exist at code load; XDefs deliberately do not need to.
install_station()
print("[TrainDistribution] native storage-row UI registered")
