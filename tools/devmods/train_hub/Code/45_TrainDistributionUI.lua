-- UI only: an independent section on a station's ipBuilding, following the
-- TestKit's section_attach / DialogOpen route. No resource-row method is wrapped.
-- Owner ruling 94bb535, spec 4.7: own tabs, visible slider value, header hover help.
-- Archived 1.1.1.405907: Lua/Resources.lua:86-162 (groups/hidden resources),
-- Lua/X/Infopanel.lua:104-109,428-445 (native refresh), and
-- Lua/XDef/InfopanelSection.generated.lua, InfopanelSlider.generated.lua.
local D = rawget(_G, "SMROptInTrainDistribution")
if not D or not D.active then return end

local reported = {}
local function ui_failure(reason)
	D.ui_error = reason
	if not reported[reason] then
		reported[reason] = true
		print("[TrainDistribution] " .. reason)
	end
end

local tabs = {
	{ "BasicResources", "Basic" }, { "AdvancedResources", "Advanced" },
	{ "MealIngredients", "Delicacies" }, { "OtherResources", "Other" },
}
local HELP = "Export: local drones fill the station; trains take stock above Keep to the hub."
	.. "<newline>Import: trains fill to the selected amount; local drones may drain it to zero."
	.. "<newline>Neither checked: Balanced; trains hold the selected amount and drones use it as their target."
	.. "<newline>The value is a percentage of current station capacity. A full hub refuses exports."
	.. "<newline>Enable a resource in the vanilla storage section to change its distribution controls."

local function named_child(parent, id)
	local child = parent and parent:ResolveId(id)
	local cursor = child
	while cursor and cursor ~= parent do cursor = cursor.parent end
	return cursor == parent and child or nil
end

local function label(parent, text, props)
	props = props or {}
	props.Text, props.TextStyle, props.Translate = text, "InfopanelText", true
	props.HandleMouse = props.HandleMouse or false
	return XText:new(props, parent)
end

local function row_state(st, res)
	local entry = D.Get(st, res)
	local cap = st:GetMaxStorage(res)
	local percent = entry and entry.percent or (cap > 0
		and Clamp(MulDivRound(st.desired_amount or 0, 100, cap), 0, 100) or 0)
	return entry and entry.mode or "balanced", percent, cap
end

local function resource_groups(st)
	local visible = {}
	for _, res in ipairs(st.storable_resources or empty_table) do
		if Resources[res] and GetPresetLockStateAndText(Resources[res], st.player) ~= "hidden" then
			visible[#visible + 1] = res
		end
	end
	-- Keep a lone resource in its named tab; vanilla's IP helper flattens singleton
	-- groups into Other, which would make these independent tabs change meaning.
	local groups = GroupResourcesForSelector(visible, false)
	local result = { BasicResources = {}, AdvancedResources = {}, MealIngredients = {}, OtherResources = {} }
	for _, group in ipairs(groups) do
		local target = result[group.id] or result.OtherResources
		for _, res in ipairs(group.items or { group.id }) do target[#target + 1] = res end
	end
	local signature = {}
	for _, tab in ipairs(tabs) do
		table.sort(result[tab[1]], ResourceCmp)
		signature[#signature + 1] = table.concat(result[tab[1]], ",")
	end
	return result, table.concat(signature, "|")
end

local refresh
local function resource_row(section, parent, res)
	local st = section.station
	local row = XWindow:new({ LayoutMethod = "VList", LayoutVSpacing = 2,
		Margins = box(0, 0, 0, 8), RolloverTemplate = "" }, parent)
	row.resource = res
	local heading = XWindow:new({ MinHeight = 24, MaxHeight = 24 }, row)
	row.stock = label(heading, "", { Dock = "right", TextHAlign = "right", MinWidth = 85 })
	row.name = label(heading, Resources[res].display_name, { Dock = "box", Shorten = true })
	local line = XWindow:new({ MinHeight = 24, MaxHeight = 24 }, row)
	row.value = label(line, "", { Dock = "right", TextHAlign = "right", MinWidth = 116 })
	local toggles = XWindow:new({ Dock = "box", LayoutMethod = "HList", LayoutHSpacing = 4 }, line)
	local function checkbox(text, mode)
		return XCheckButton:new({ Text = Untranslated(text), TextStyle = "InfopanelText",
			TextColor = RGB(255, 255, 255), IconColor = RGB(255, 255, 255),
			MinWidth = 80, MaxWidth = 80, MinHeight = 24, MaxHeight = 24,
			IconScale = point(420, 420), VAlign = "center",
			RolloverTemplate = "", RolloverOnFocus = false,
			OnChange = function(button, checked)
				if section.refreshing then return end
				local _, percent = row_state(st, res)
				D.Set(st, res, checked and mode or "balanced", percent)
				refresh(section)
			end,
		}, toggles)
	end
	row.import = checkbox("Import", "import")
	row.export = checkbox("Export", "export")
	row.slider = InfopanelSlider:new({ Min = 0, Max = 100, StepSize = 1,
		Margins = box(0, 0, 0, 0), RolloverTemplate = "", RolloverOnFocus = false,
		ScrollTo = function(slider, value)
			local result = InfopanelSlider.ScrollTo(slider, value)
			if not section.refreshing then
				local mode = row_state(st, res)
				D.Set(st, res, mode, slider:GetScroll())
				refresh(section)
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
	}, row)
	-- Fit the native art to this section, including when a scrollbar is present.
	row.slider.idBar:SetMinWidth(0)
	for _, child in ipairs(row.slider.idBar) do child:SetMinWidth(0) end
	row.note = label(row, "", { FoldWhenHidden = true })
	return row
end

refresh = function(section)
	if not section.rows_host or section.refreshing then return end
	local st = section.station
	local hub = IsValid(st) and not st.destroyed and D.HubFor(st)
	section:SetVisible(not not hub)
	if not hub then return end
	section.refreshing = true
	section.coverage:SetVisible(not D.HasDroneCoverage(st))
	local groups, signature = resource_groups(st)
	if signature ~= section.signature then
		section.rows_host:DeleteChildren()
		section.pages, section.rows, section.signature = {}, {}, signature
		for _, tab in ipairs(tabs) do
			local page = XWindow:new({ LayoutMethod = "VList", FoldWhenHidden = true }, section.rows_host)
			section.pages[tab[1]] = page
			for _, res in ipairs(groups[tab[1]]) do
				section.rows[res] = resource_row(section, page, res)
			end
			if #groups[tab[1]] == 0 then label(page, Untranslated("No resources in this group.")) end
			if section.window_state == "open" then page:Open() end
		end
	end
	for _, tab in ipairs(tabs) do
		local selected = section.tab == tab[1]
		section.pages[tab[1]]:SetVisible(selected)
		section.tabs[tab[1]]:SetBackground(selected and RGBA(64, 101, 119, 255) or RGBA(35, 47, 57, 255))
	end
	for res, row in pairs(section.rows) do
		local mode, percent, cap = row_state(st, res)
		local s, d = st.supply and st.supply[res], st.demand and st.demand[res]
		local enabled = not not (s and d and st:IsResourceEnabled(res))
		row.import:SetCheck(mode == "import")
		row.export:SetCheck(mode == "export")
		row.import:SetEnabled(enabled)
		row.export:SetEnabled(enabled)
		row.slider:SetEnabled(enabled)
		row.slider:SetScroll(percent)
		if row.slider.window_state == "open" then row.slider:UpdateProgress() end
		local verb = mode == "export" and "Keep" or mode == "import" and "Fill to" or "Hold"
		row.value:SetText(Untranslated(string.format("%s %g (%g%%)", verb,
			MulDivRound(cap, percent, 100) / const.ResourceScale, percent)))
		row.stock:SetText(Untranslated(string.format("%g/%g", (s and s:GetActualAmount() or 0)
			/ const.ResourceScale, cap / const.ResourceScale)))
		local full = hub.demand and hub.demand[res] and hub.demand[res]:GetTargetAmount() <= 0
		local note = not enabled and "Resource disabled in storage" or mode == "export" and full and "Hub full" or ""
		row.note:SetText(Untranslated(note))
		row.note:SetVisible(note ~= "")
	end
	section.refreshing = false
end

function D.AttachStationSection(dlg)
	if not dlg or dlg.window_state == "destroying" or not IsKindOf(dlg, "ipBuilding") then return end
	local st = ResolvePropObj(dlg.context)
	if not IsValid(st) or not IsKindOf(st, "Station") or IsKindOf(st, "SMROptInTrainHubBase") then return end
	-- XDef classes are built after mod code loads. Register the callback at load;
	-- check the class only when a station card actually opens, and allow a retry.
	if not InfopanelSection or type(InfopanelSection.new) ~= "function" then
		ui_failure("InfopanelSection unavailable")
		return
	end
	local host = named_child(dlg, "idContent")
	if not host then
		ui_failure("station ipBuilding has no contained idContent")
		return
	end
	D.ui_error = nil
	local existing = named_child(host, "idTrainDistribution")
	if existing then return existing end
	local section = InfopanelSection:new({ Id = "idTrainDistribution", IdNode = true,
		Title = Untranslated("Import / Export"), ShowRightTitle = false,
		Icon = "UI/IconsRemaster/Buildings/group_basic_resources.png",
		RolloverTemplate = "", RolloverText = "", RolloverOnFocus = false,
		OnContextUpdate = refresh,
		-- Navigate to a row before changing it; the base section's shoulder
		-- shortcut otherwise edits its first slider even when that tab is hidden.
		OnShortcut = XSection.OnShortcut,
	}, host, dlg.context)
	section.station, section.tab, section.tabs = st, "BasicResources", {}
	-- The title container belongs to this new section. Docking the help chip
	-- reserves header space; its rollover is mouse-only and has no click action.
	section.help = label(section.idSectionTitle.parent, Untranslated("?"), {
		Dock = "right", MinWidth = 26, MaxWidth = 26, TextHAlign = "center",
		HandleMouse = true, RolloverTemplate = "Rollover", RolloverOnFocus = false,
		RolloverTitle = Untranslated("Import / Export"), RolloverText = Untranslated(HELP),
	})
	section.coverage = label(section.idContent, Untranslated("No drones in range — trains only"),
		{ FoldWhenHidden = true, Margins = box(0, 0, 0, 4) })
	local tab_bar = XWindow:new({ LayoutMethod = "HList", LayoutHSpacing = 3,
		Margins = box(0, 0, 0, 6) }, section.idContent)
	for _, tab in ipairs(tabs) do
		local id = tab[1]
		section.tabs[id] = XTextButton:new({ Text = Untranslated(tab[2]), TextStyle = "InfopanelText",
			TextColor = RGB(255, 255, 255), Padding = box(5, 2, 5, 2),
			MinHeight = 26, MaxHeight = 26, RolloverTemplate = "", RolloverOnFocus = false,
			RolloverBackground = RGBA(78, 111, 128, 255),
			OnPress = function()
				section.tab = id
				refresh(section)
				section.rows_host:ScrollTo(0, 0)
			end,
		}, tab_bar)
	end
	local frame = XWindow:new({ IdNode = true, MinHeight = 80, MaxHeight = 300 }, section.idContent)
	XSleekScroll:new({ Id = "idScroll", Target = "idRows", Dock = "right", AutoHide = true }, frame)
	section.rows_host = XScrollArea:new({ Id = "idRows", Dock = "box", LayoutMethod = "VList",
		VScroll = "idScroll" }, frame)
	-- Put the new section next to storage; never reparent or edit vanilla rows.
	for at, child in ipairs(host) do
		if IsKindOf(child, "sectionMultiResourceStorage") then
			table.remove_entry(host, section)
			table.insert(host, at + 1, section)
			break
		end
	end
	refresh(section)
	section:Open()
	return section
end

function OnMsg.DialogOpen(dlg) D.AttachStationSection(dlg) end

print("[TrainDistribution] station import/export section loaded")
