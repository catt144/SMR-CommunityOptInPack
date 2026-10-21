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
	-- Every ordinary station gets the rows, with or without a hub (brief 30), while the
	-- shipping gate allows (D.RowsOn: a hub's network always; hubless per the modules).
	return D.RowsOn(st)
end
-- Owner 2026-10-21 (R4): Default is the absence of a row, the state a station is in until a
-- row is set; the click cycle is Default, Export, Import, Not accepted, Default. A set
-- Balanced row (the slider moved from Default) shows as Balanced and clicks on to Export.
-- A click to Export sets 0, to Import 100, or 50 on a station that joins lines off a hub;
-- the slider from Default makes Balanced at its value and from Export or Import keeps the
-- mode. Rows already saved keep their numbers until clicked.
local titles = { default = "Default", balanced = "Balanced", export = "Export", import = "Import", disabled = "Not accepted" }
local following = { default = "export", balanced = "export", export = "import", import = "disabled", disabled = "default" }
local function default_percent(st, mode)
	if mode == "export" then return 0 end
	if mode == "import" then return (not D.HubFor(st) and D.IsJunction(st)) and 50 or 100 end
end
local icons = {
	default = "UI/IconsRemaster/Sections/resource_storing.tga",   -- vanilla's own row icon
	balanced = "UI/IconsRemaster/Sections/resource_accept.tga",
	export = "UI/IconsRemaster/Sections/elevator_resource_up.png",
	import = "UI/IconsRemaster/Sections/elevator_resource_down.png",
}
local help = {
	default = "Default: trains hold this station's Desired Amount, as every row on the hub's network does until it is set. Changing this row gives it its own setting.",
	balanced = "Balanced: trains hold the selected amount, and local drones use it as their desired amount. Surplus in nearby storage stays put; choose Export to send it to the hub.",
	export = "Export: trains take stock above the selected minimum to the hub. Local drones bring in what nearby storage holds above its Desired Amount. A full hub refuses exports.",
	import = "Import: trains bring stock from the hub up to the selected amount. Local drones may drain this station to zero.",
	disabled = "Not accepted: vanilla storage is disabled for this resource. Trains and drones may carry its remaining stock away.",
}
local local_help = {
	-- owner 2026-10-05: a row nobody has set keeps the game's balancing on a line with no hub
	default = "Default: trains spread this resource between the stations on the line, as in the base game. Changing this row gives the station its own setting.",
	balanced = "Balanced: trains exchange stock with other stations to hold the selected amount, and local drones use it as their desired amount. Surplus in nearby storage stays put; choose Export to send it out.",
	-- audit 2026-10-21 (A4): the clauses name what the station keeps, so the joining-station line below
	-- (cargo for other lines passing through the room above the number) does not contradict them
	export = "Export: trains take what this station holds above the selected amount, a share of its own store, to accepting stations, and bring nothing for its own use. Local drones bring in what nearby storage holds above its Desired Amount.",
	import = "Import: trains bring stock from other stations up to the selected amount, a share of this station's own store, and take none of that amount away. From a station left at Default they bring what the base game would share; set Export there to send everything. Local drones may drain this station to zero.",
}
function D.RowState(st, res)
	local entry = D.Get(st, res)
	local cap = st:GetMaxStorage(res)
	local percent = entry and entry.percent or (cap > 0
		and Clamp(MulDivRound(st.desired_amount or 0, 100, cap), 0, 100) or 0)
	local target = entry and MulDivRound(cap, percent, 100) or st.desired_amount or 0
	return not st:IsResourceEnabled(res) and "disabled" or entry and entry.mode or "default", percent, cap, target
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
		-- One ownership snapshot per click (audit 2026-10-21, A3): the row is read, its successor
		-- chosen and the write made against the same hub graph; D.Set and D.Clear refresh too, so
		-- a hub joining or leaving inside the cache's second cannot land the write in the other set.
		D.Refresh()
		if not network(st) then return toggle(st, res, broadcast, ...) end
		local mode, percent = D.RowState(st, res)
		if not broadcast then
			mode = following[mode]
			percent = default_percent(st, mode) or percent
		end
		-- Preserve vanilla's city-wide scope and its own disabled/request-flag path.
		for _, target in ipairs(broadcast and st.city.labels.Station or { st }) do
			-- an Elevator Depot's setting is written only on its surface panel (brief 27)
			local depot = D.IsDepotStation and D.IsDepotStation(target)
			if (not broadcast or target ~= st) and not depot then
				if broadcast and mode == "disabled" and network(target) then
					-- D.Set uses enabled requests. Copy the remembered slider first,
					-- then finish through vanilla's disabled path, without yielding.
					local entry = D.Get(st, res)
					set_accept(target, res, "store", false)
					if entry then D.Set(target, res, entry.mode, percent) else D.Clear(target, res) end
				end
				set_accept(target, res, mode == "disabled" and "disabled" or "store", false)
				if network(target) and mode ~= "disabled" then
					if mode == "default" then D.Clear(target, res) else D.Set(target, res, mode, percent) end
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
		local mode, percent, cap, target = D.RowState(st, res)
		local hub = D.HubFor(st)
		local text = (not hub and local_help[mode] or help[mode])
			.. "<newline><newline>Slider: " .. tostring(percent)
			.. "% of current capacity (" .. tostring(target / const.ResourceScale) .. ")."
		if not hub then text = text .. "<newline><newline>No hub: these settings are kept at this station. Connecting a hub uses its separate settings; disconnecting restores these." end
		-- owner 2026-10-21 (R1): a joining station relays in the room above its number; a full number leaves none
		if not hub and mode ~= "disabled" and D.IsJunction(st) then
			text = text .. "<newline><newline>This station joins lines: cargo for its other lines passes through the room above its number, so its stock reads above the number on the way."
			if mode ~= "default" and mode ~= "export" and percent >= 100 then
				text = text .. " At 100 nothing can pass between its lines; lower the number to let cargo through."
			end
		end
		local parent = D.Parent(st)
		if parent and parent ~= D.HubFor(st) then
			text = text .. "<newline><newline>Trains forward this resource through station "
				.. tostring(parent.handle) .. " on its way to or from the hub. Transit may use that station's free storage."
		end
		if not D.HasDroneCoverage(st) then text = text .. "<newline><newline>No drones in range — trains only." end
		return Untranslated(text)
	end
	station_installed = true
	return true
end

-- The title box in panel units, rounded up. In the engine int/int truncates (EF-116), so the former
-- `math.ceil(a * 1000 / s)` got an already-floored integer; XWindow then scales MaxHeight and the padding
-- to pixels separately through ScaleXY (CommonLua/X/XWindow.lua:766-784, archived build 25579348), which
-- can lose another unit. At scale 1000 both are exact; at other panel scales the box came out short and
-- the label shortened a long title to one line with "..." (found on the Elevator Depot, sitting E; the
-- depot's fix is 1122115). So: a true ceiling, plus FIT_SLACK units for the scaling truncation (2 units:
-- far below a third line, which needs ~35). Kept bit-equal to the depot's copy; tests/distribution_ui_smoke.py
-- runs both.
local FIT_SLACK = 2
local function mul_div_ceil(a, b, c)
	local q = MulDivRound(a, b, c)
	if q * c < a * b then q = q + 1 end
	return q
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
		width = Max(width, mul_div_ceil(UIL.MeasureText(word, font) + 1, 1000, sx) + FIT_SLACK
			+ padding:minx() + padding:maxx())
	end
	title:SetMinWidth(width)
	title:SetMaxWidth(width)
	title:SetMaxHeight(mul_div_ceil(2 * title.font_height, 1000, sy) + FIT_SLACK
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
			D.Refresh()   -- the same snapshot rule as the click (A3)
			if not network(st) then return end
			local mode = D.RowState(st, res)
			if mode == "default" then mode = "balanced" end
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
