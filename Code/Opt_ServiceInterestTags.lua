-- D15 — OPTIONAL module, OFF BY DEFAULT. Not a bug fix: a display choice.
--
-- Owner ruling 2026-09-28 (verbatim in docs/agent/bugs/D15.md): show each service
-- building's interests in the build-menu hover and in the placed building's
-- infopanel. Display only — nothing about how colonists choose or use a
-- service changes.
--
-- Enable it in-game: Options → Mod Options → Relaunched Fix Pack: Opt-In Modules (D05).
-- Toggles take effect immediately in both directions: every hook below checks
-- SMROptInPack.IsActive per call and passes through while off, so the build
-- menu shows the change the next time a category is opened and the infopanel
-- the next time one is built (a panel already open keeps its rows until
-- reselected). All three hooks are installed at FILE SCOPE, classdef time, so
-- they propagate through class flattening and the first mid-session enable
-- works without a restart. Other mods / power users can also pre-seed
-- SMROptInPack_Optional = { ServiceInterestTags = true } before this mod loads.
--
-- Why it exists: Relaunched shows a service building's CATEGORY ("Stores",
-- "Parks") and hides its INTERESTS, which still drive play on 1.1.1.405907:
-- colonists look a building up for their daily interest by interest label
-- (Service:SetCustomLabels, Buildings/Service.lua:170-230; Dome:GetService,
-- Buildings/Dome.lua:3622),
-- and the Gamer / Extrovert traits pay Sanity on entering any working building
-- whose interests include Gaming / Social (Colonist:VisitService,
-- Units/Colonist.lua:2671-2678). A player cannot see that an Electronics Store
-- counts for Gamers. Prior art: 1.0.7.396349 showed it —
-- Service:GetIPDescription appended "Services: <list>" (Buildings/Service.lua:58-62,
-- again :190-194 for ServiceWorkplace) and sectionVisitors ended with
-- "Needs serviced: <ServiceList>" (XDef/sectionVisitors.generated.lua:44). Both are
-- gone from 1.1.1; ServiceBase:GetServiceList (ServiceBase.lua:166-212) still
-- ships with no caller.
--
-- WHAT THIS SHIPS — one "Interests" line, in the game's canonical interest
-- order (ServiceInterestsList, Interests.lua:2-16), three names per line:
--
--   1. BUILD-MENU HOVER — post-wrap of Service:GetServiceDescription
--      (Buildings/Service.lua:124-163), the one funnel all three service
--      GetIPDescription bodies call (Service :165, ServiceWorkplace :333,
--      FoodServiceBuilding FoodServiceBuilding.lua:924). The build menu calls
--      `object_class.GetIPDescription(template)` (X/BuildMenu.lua:832) with a
--      BuildingTemplates entry, which is a table whose metatable is the
--      building's class (Buildings/Building.lua:2701), so the service methods resolve on
--      it. The line is added only for exactly that call shape: `self` is not a
--      valid object and `dont_modify` is unset — the same condition vanilla
--      uses to read colony modifiers (:126). The Encyclopedia passes
--      dont_modify = true (UI/Encyclopedia.lua:435) and the placed building's
--      description passes a valid object (XDef/Infopanel.generated.lua:655), so
--      neither changes. Placement: straight under "Service <category>". A food
--      service with no category (Diner, Grocer: same_category_as "Ignore", so
--      vanilla writes no service block at all) gets its own blank-separated
--      block, ahead of the Meals block.
--   2. PLACED BUILDING — post-wraps of two generated infopanel Inits that add
--      one InfopanelText row; neither section is replaced:
--        * sectionVisitors:Init (XDef/sectionVisitors.generated.lua:20-51):
--          the row goes last, after "Service effect" / "Tips". This section
--          exists for every ServiceBase except same_category_as "Ignore" (:13-18).
--        * sectionFoodService:Init (XDef/sectionFoodService.generated.lua):
--          for the "Ignore" food services only (the exact complement, so no
--          building shows the row twice), inside the section's LAST
--          InfopanelSection child: for a FoodServiceBuilding that is the
--          untitled service block holding "Meals served last Sol" (:95-108).
--      The row recomputes on every context update, so a Medical building that
--      turns on Rejuvenation shows Relaxation without reselecting.
--
-- Which interests: ServiceInterestsList filtered by the building's own
-- IsOneOfInterests — the predicate the game itself uses for the daily-interest
-- match and both trait bonuses (Colonist.lua:2671-2679). That keeps
-- MedicalBuilding's Rejuvenation override (MedicalCenter.lua:29-33) and
-- deduplicates by construction. GetServiceList is NOT reused: it drops needs a
-- law auto-satisfies (g_AutoSatisfiedNeeds), which would hide, for example,
-- Gaming while the Gamer bonus still pays on it. Food and Medical Checks are
-- listed: they are interests colonists visit for.
--
-- Not covered: Ignore-category services that are not food services (the
-- Fireflies mystery's flower lamps) — vanilla gives them no service section to
-- host the row, and adding a section is a bigger UI change than the ruling asks.
--
-- Strings: the label is new text, so Untranslated per FIX_POLICY §6 (built as
-- T{..., untranslated = true} so it can carry the list parameter — the shape
-- Untranslated itself returns). Interest names are the game's own localized
-- T values (Interests.lua, GetInterestDisplayName).
--
-- Savegame footprint: none. Every hook is synchronous UI code that writes no
-- field, stores no function value and starts no thread (FIX_POLICY §3a tier 1).

SMROptInPack_Optional = rawget(_G, "SMROptInPack_Optional") or {}

local FIX_ID = "ServiceInterestTags"
local PER_LINE = 3

local function module_active()
	return SMROptInPack.IsActive(FIX_ID)
end

-- The building's interests as one T value, or nil when it has none.
local function interests_text(obj)
	local names = {}
	for _, interest in ipairs(ServiceInterestsList) do
		if obj:IsOneOfInterests(interest) then
			local name = GetInterestDisplayName(interest)
			if name then
				names[#names + 1] = name
			end
		end
	end
	if #names == 0 then return end
	local lines, line = {}, {}
	for _, name in ipairs(names) do
		line[#line + 1] = name
		if #line == PER_LINE then
			lines[#lines + 1] = TList(line)
			line = {}
		end
	end
	if #line > 0 then
		lines[#lines + 1] = TList(line)
	end
	return TList(lines, "\n")
end

local function interests_line(obj, label_separator)
	local list = interests_text(obj)
	if not list then return end
	return T{"Interests<right><list>", list = list, right = label_separator, untranslated = true}
end

-- Build menu: add the line to the service block vanilla just wrote.
local function add_build_menu_line(self, texts, start, label_separator)
	local line = interests_line(self, label_separator)
	if not line then return end
	if #texts > start then
		-- vanilla's block: "" separator at start + 1, "Service <category>" at start + 2
		if texts[start + 1] == "" and #texts >= start + 2 then
			table.insert(texts, start + 3, line)
		else
			texts[#texts + 1] = line
		end
	elseif IsKindOf(self, "FoodBuilding") then
		texts[#texts + 1] = ""
		texts[#texts + 1] = line
	end
end

local function after_description(self, texts, start, label_separator, ...)
	pcall(add_build_menu_line, self, texts, start, label_separator)
	return ...
end

local function add_row(parent, context)
	InfopanelText:new({
		Text = interests_line(context) or "",
		OnContextUpdate = function(self, context)
			self:SetText(interests_line(context) or "")
		end,
	}, parent, context)
end

-- Hooks, at FILE SCOPE (FIX_POLICY §5), each behind the existence check apply()
-- repeats, so a missing target leaves vanilla alone and apply() reports why.
do
	local S = rawget(_G, "Service")
	if type(S) == "table" and type(S.GetServiceDescription) == "function" then
		local orig = S.GetServiceDescription
		function S:GetServiceDescription(texts, label_separator, dont_modify, ...)
			if not module_active() or dont_modify or type(texts) ~= "table" or IsValid(self) then
				return orig(self, texts, label_separator, dont_modify, ...)
			end
			local start = #texts
			return after_description(self, texts, start, label_separator,
				orig(self, texts, label_separator, dont_modify, ...))
		end
	end

	local SV = rawget(_G, "sectionVisitors")
	if type(SV) == "table" and type(SV.Init) == "function" then
		local orig = SV.Init
		function SV:Init(parent, context, ...)
			local r = orig(self, parent, context, ...)
			if module_active() and IsKindOf(context, "ServiceBase") then
				pcall(add_row, self.idContent, context)
			end
			return r
		end
	end

	local SF = rawget(_G, "sectionFoodService")
	if type(SF) == "table" and type(SF.Init) == "function" then
		local orig = SF.Init
		function SF:Init(parent, context, ...)
			local r = orig(self, parent, context, ...)
			if module_active() and IsKindOf(context, "ServiceBase")
					and context.same_category_as == "Ignore" then
				pcall(function()
					for i = #self, 1, -1 do
						if IsKindOf(self[i], "InfopanelSection") then
							add_row(self[i].idContent, context)
							return
						end
					end
				end)
			end
			return r
		end
	end
end

SMROptInPack.Register(FIX_ID, {
	title = "OPTIONAL: show each service building's interests in the build menu and its infopanel",
	optional = true,
	apply = function()
		if not SMROptInPack.OptionEnabled(FIX_ID) then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end
		-- Every method below is declared by the class named (Service.lua:124,
		-- the two generated XDef files), so the classdef lookup is valid at
		-- mod-load time (FIX_POLICY §2, F64).
		local err = SMROptInPack.Require(FIX_ID, {
			{ class = "Service", method = "GetServiceDescription",
			  reason = "Service.GetServiceDescription not found (game update changed the build menu text?)" },
			{ class = "sectionVisitors", method = "Init",
			  reason = "sectionVisitors/sectionFoodService Init not found (game update changed the infopanel?)" },
			{ class = "sectionFoodService", method = "Init",
			  reason = "sectionVisitors/sectionFoodService Init not found (game update changed the infopanel?)" },
			{ global = "ServiceInterestsList", kind = "table" },
			{ global = "GetInterestDisplayName" },
			{ global = "TList" },
		})
		if err then return err end
	end,
})
