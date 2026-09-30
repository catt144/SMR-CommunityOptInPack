-- D15 — OPTIONAL module, OFF BY DEFAULT. Not a bug fix: a display choice.
--
-- Owner ruling 2026-09-28 (verbatim in docs/agent/bugs/D15.md): show each service
-- building's interests in the build-menu hover and in the placed building's
-- infopanel. Owner ruling 2026-09-29 (same file): on the placed building that
-- is an "Interests" SECTION of its own whose popout carries the building's
-- description, category, visitor filter and the trait effects. Display only —
-- nothing about how colonists choose or use a service changes.
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
--   2. PLACED BUILDING — an "Interests" InfopanelSection, created as a SIBLING
--      straight after the service section by post-wraps of two generated
--      Inits; no vanilla section is replaced or edited:
--        * sectionVisitors:Init (XDef/sectionVisitors.generated.lua:20-51),
--          built for every ServiceBase except same_category_as "Ignore" (:13-18);
--        * sectionFoodService:Init (XDef/sectionFoodService.generated.lua), for
--          the "Ignore" food services only (Diner, Grocer) — the exact
--          complement, so no building gets the section twice.
--      Init is a combined parents-first method (CommonLua/PropertyObject.lua:1741)
--      and XWindow:Init appends the window to its parent first, so when the
--      wrapper runs the host section is the last child of ipBuilding's content
--      window and the new section lands directly after it. RebuildInfopanel
--      only posts ObjModified and never re-runs Init (X/Infopanel.lua:428-447).
--      Body: the interest list. Popout (the section's RolloverText): the
--      building's description, service category, visitor filter, and the trait
--      effects that apply there (TRAIT RULES below). Both recompute on every
--      context update, so Rejuvenation turning on shows Relaxation live. With
--      no interests the section hides itself, and a hidden section is not
--      counted by Infopanel:OnContextUpdate's description rule.
--      Accepted cost (owner, 2026-09-29): a panel with exactly two visible
--      sections (the Open Air Gym) loses its inline description block, which
--      shows only while two or fewer are visible (XDef/Infopanel.generated.lua:
--      666-669); that block's unique lines are in the popout.
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
-- TRAIT RULES — every per-colonist effect a service visit has on 1.1.1.405907
-- (research 2026-09-29; the full table, DLC and law cases included, is in D15):
--   Gamer      interestGaming           +param Sanity per visit  Units/Colonist.lua:2671-2674
--   Extrovert  interestSocial           +param Sanity per visit  Units/Colonist.lua:2675-2678
--   Gambler    CasinoComplexBase        -param Sanity, 50% roll  Buildings/CasinoComplex.lua:4-9
--   Fit        FitService (gym, TaiChi) param% chance to gain    Buildings/OpenAirGym.lua:6-15
--   Hippie     GardenStone category     +param Comfort at rest   Data/TraitPreset.lua:338-341
--   Child      PlaygroundBase           Perk when grown          Buildings/Playground.lua:5-7
--   Glutton    FoodServiceBuilding      double portion           Units/Colonist.lua:4925-4927
--   Vegan      FoodServiceBuilding      vegan delicacies only    Buildings/FoodServiceBuilding.lua:517-522
-- Conditional (owner, 2026-09-29), each shown only while its condition holds:
--   Foodie      FoodServiceBuilding, norman DLC data   +Comfort with delicacies
--               DLC/norman/Presets/TraitPreset.lua:51-58 (parameter Comfort)
--   CoffeeEnth. consumes Coffee (norman DLC buildings) +/-Comfort at rest
--               DLC/norman/Presets/StatsImpact.lua:40-55 (StatsImpacts, Comfort)
--   Tourist     FoodServiceBuilding, WHILE the Food Tours law is active
--               ActiveLaws.Policy_FoodTours, Units/Colonist.lua:2702-2705, :4931-4933
-- Numbers come from TraitPresets[id].param, preset parameters and g_Consts at
-- call time, so a balance patch shows through. Hard-coded in vanilla and so
-- here: Gambler's 50%. Left out (owner): the mystery-only Infected cure.
--
-- Not covered, by owner ruling 2026-09-30 (mystery content stays out): the
-- Fireflies mystery's Wisp Lamps, prefab-only Ignore-category services that
-- neither hooked section exists for.
--
-- Strings: labels and sentences are new text, so Untranslated per FIX_POLICY §6
-- (built as T{..., untranslated = true} where they carry parameters — the shape
-- Untranslated itself returns). Interest, trait, stat, category and filter
-- names are the game's own localized T values; a stat amount uses vanilla's
-- own "<icon><delta(amount)>" T (Stats.lua:30), unchanged.
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

local function untranslated(text, params)
	params = params or {}
	params[1] = text
	params.untranslated = true
	return T(params)
end

-- vanilla's stat amount, icon and colour: StatValues:GetUIStatText's part (Stats.lua:30)
local function stat(amount, id)
	return T{948271635221, "<icon><delta(amount)>", icon = ColonistStat[id].icon_tag, amount = amount}
end

local function trait_line(lines, id, effect_text, params)
	local trait = TraitPresets[id]
	if not trait then return end
	params = params or {}
	params.name = trait.display_name
	params.param = trait.param
	lines[#lines + 1] = untranslated("<name><right>" .. effect_text, params)
end

-- a preset's named parameter (CommonLua/Preset.lua:544-552)
local function preset_param(preset, key)
	if type(preset.GetParameterValue) == "function" then
		return preset:GetParameterValue(key)
	end
	for _, param in ipairs(preset.Parameters or {}) do
		if param.Name == key then return param.Value end
	end
end

local function trait_param(id)
	local trait = TraitPresets[id]
	return trait and trait.param or 0
end

local function trait_lines(obj)
	local lines = {}
	if obj:IsOneOfInterests("interestGaming") then
		trait_line(lines, "Gamer", "<stat> per visit", { stat = stat(trait_param("Gamer"), "Sanity") })
	end
	if obj:IsOneOfInterests("interestSocial") then
		trait_line(lines, "Extrovert", "<stat> per visit", { stat = stat(trait_param("Extrovert"), "Sanity") })
	end
	if IsKindOf(obj, "CasinoComplexBase") then
		trait_line(lines, "Gambler", "<stat> per visit, 50% chance", { stat = stat(-trait_param("Gambler"), "Sanity") })
	end
	if IsKindOf(obj, "FitService") then
		trait_line(lines, "Fit", "<param>% chance to gain, per visit")
	end
	if obj:GetServiceCategory() == "GardenStone" then
		trait_line(lines, "Hippie", "<stat> living in this Dome", { stat = stat(trait_param("Hippie"), "Comfort") })
	end
	if IsKindOf(obj, "PlaygroundBase") then
		local consts = rawget(_G, "g_Consts")
		local chance = type(consts) == "table" and consts.positive_playground_chance
		if chance then
			trait_line(lines, "Child", "<chance>% chance of a Perk when grown", { chance = chance })
		else
			trait_line(lines, "Child", "a Perk when grown")
		end
	end
	if IsKindOf(obj, "FoodServiceBuilding") then
		trait_line(lines, "Glutton", "eats a double portion")
		trait_line(lines, "Vegan", "eats vegan delicacies only")
	end
	-- Conditional lines (owner, 2026-09-29): each shows only while its condition
	-- holds; the popout is rebuilt on every context update, so they come and go live.
	-- Stat presets store scaled values; `//` keeps them integers in the game's Lua
	-- and in a standard one alike (EF-116).
	local scale = const.Scale.Stat
	if IsKindOf(obj, "FoodServiceBuilding") then
		-- norman DLC trait: present only when the DLC's data is loaded
		local comfort = TraitPresets.Foodie and preset_param(TraitPresets.Foodie, "Comfort")
		if comfort then
			trait_line(lines, "Foodie", "<stat> when served delicacies",
				{ stat = stat(comfort // scale, "Comfort") })
		end
		-- the law, only while it is active: the game's own test (Units/Colonist.lua:2702)
		local laws = rawget(_G, "ActiveLaws")
		local law = type(laws) == "table" and laws.Policy_FoodTours
		if law then
			trait_line(lines, "Tourist", "<stat> per meal, eats <meals>x (<law>)", {
				stat = stat(preset_param(law, "MoraleIncrease") or 0, "Morale"),
				meals = preset_param(law, "MealsMultiplier") or 1,
				law = law.display_name,
			})
		end
	end
	-- norman DLC: only its buildings consume Coffee (Buildings/Dome.lua:2109-2117)
	if obj.consumption_resource_type == "Coffee" then
		local impacts = rawget(_G, "StatsImpacts")
		local impact = type(impacts) == "table" and impacts.CoffeeEnthusiast
		if impact and impact.Comfort then
			-- a swing: +Comfort with a stocked Coffee service in the Dome, -Comfort without (:43-44)
			trait_line(lines, "CoffeeEnthusiast", "<stat> living in this Dome with Coffee, <minus> without", {
				stat = stat(impact.Comfort // scale, "Comfort"),
				minus = stat(-(impact.Comfort // scale), "Comfort"),
			})
		end
	end
	return lines
end

local function popout_text(obj)
	local lines = {}
	if (obj.description or "") ~= "" then
		lines[#lines + 1] = T{obj.description, obj}
		lines[#lines + 1] = ""
	end
	local cat = obj:GetServiceCategory()
	if cat then
		lines[#lines + 1] = untranslated("Service<right><em><category></em>",
			{ category = GetServiceCategoryDisplayName(cat) })
	end
	local filter_name = ColonistFilterDisplayName[obj.filter_visitors or ""]
	if filter_name then
		lines[#lines + 1] = untranslated("Visitors<right><filter>", { filter = filter_name })
	end
	lines[#lines + 1] = untranslated("Colonists come here when their daily interest is one of these.")
	local traits = trait_lines(obj)
	if #traits > 0 then
		lines[#lines + 1] = ""
		lines[#lines + 1] = untranslated("<em>Traits</em>")
		for _, line in ipairs(traits) do
			lines[#lines + 1] = line
		end
	end
	return TList(lines, "<newline><left>")
end

local function refresh_section(section, obj)
	local list = interests_text(obj)
	section:SetVisible(list and true or false)
	local body = rawget(section, "idSMROptInInterestsBody")
	if body then
		body:SetText(list or "")
	end
	local ok, text = pcall(popout_text, obj)
	section:SetRolloverText(ok and text or "")
end

-- host = ipBuilding's content window; the new section is appended after the
-- service section that is being initialised.
local function add_section(host, context)
	local section = InfopanelSection:new({
		Title = untranslated("Interests"),
		Icon = "UI/IconsRemaster/Sections/traits.png",
		OnContextUpdate = function(self, context)
			refresh_section(self, context)
		end,
	}, host, context)
	rawset(section, "idSMROptInInterestsBody", InfopanelText:new({}, section.idContent, context))
	refresh_section(section, context)
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
				pcall(add_section, self.parent or parent, context)
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
				pcall(add_section, self.parent or parent, context)
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
			{ class = "InfopanelSection" },
			{ class = "InfopanelText" },
			{ global = "ColonistStat", kind = "table" },
			{ global = "ColonistFilterDisplayName", kind = "table" },
			{ global = "GetServiceCategoryDisplayName" },
		})
		if err then return err end
	end,
})
