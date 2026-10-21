-- D19: optional content, OFF by default. Owner 2026-10-03 requested a
-- seed-consuming Arboretum test build; category and one-per-dome are provisional.
-- ON offers new buildings; OFF (including a live toggle) hides new buildings.
-- Placed Arboretums keep running in either state. Demolish them before removing the mod.
-- Save names and residuals: bugs/D19.md.
--
-- Agreed design (owner, 2026-10-05; brief ARBORETUM_MODEL_high.md §"Agreed design"): a staffed
-- service with no required specialization. Unstaffed it runs at the Large Garden's 100; staff
-- with Seeds lift it; Seeds are used by the staff once per staffed shift; an empty store never
-- closes it. Three upgrades: Service Bots, Seasonal Blooms, Rare Specimens. Display beds and
-- specimen plants are attached to the pavilion's `Cropbed` / `Specimen` spots.
-- Every behaviour here is a method on this module's own class or an OnMsg handler; no vanilla
-- method is replaced. Engine lines are cited from the archived 1.1.1.406343 tree.
-- Integer maths only: in the game int / int is integer division, so nothing here uses `/`.

local ID = "Arboretum"
local TEMPLATE = "SMROptInArboretum"
local log = SMROptInPack.Log

-- ===== Tunables: prototype numbers from the agreed design; the owner moves these =====
-- The unstaffed floor is the template's auto_performance (100, the Large Garden's parity).
-- Staffed with Seeds: by filled worker slots (one of two, both); a full staff and Service Bots
-- take the last entry. The workers' own performance wins when it is higher.
local STAFFED_PERFORMANCE = { 125, 150 }
-- Seasonal Blooms: what each visitor gains on leaving, in stat points (x const.Scale.Stat).
local BLOOMS_VISIT_COMFORT = 5
-- A Melancholic visitor also gains Sanity: Party Animal's (Extrovert) param,
-- Data/TraitPreset.lua:283-293 @1.1.1.406343.
local BLOOMS_MELANCHOLIC_SANITY = 10
-- Display beds (contract between model and code: three `Cropbed`, two `Specimen`, floor level).
local BED_SPOT = "Cropbed"
local SPECIMEN_SPOT = "Specimen"
local BED_DIAMETER = 800          -- clear circle at each Cropbed; a crop is scaled to fit it
local SPECIMEN_DIAMETER = 500     -- clear circle at each Specimen
local BED_STAGGER_PARTS = 3       -- beds start a third of a sol apart
local CROP_SCALE_MIN, CROP_SCALE_MAX = 10, 300  -- percent; guard against a degenerate bbox
-- Bed display (owner, 2026-10-05, "do a plus our own"): every bed is always in bloom; Seasonal
-- Blooms grows it by scale over its own sol and changes the variety at each replant. A bed's sol
-- starts at its replant (bed.grown = 0, in ms of game time like const.DayDuration).
local BED_GROW_START_PCT = 20     -- size at replant, percent of the bed's full size (terraforming's 20)
local BED_GROW_FULL_PCT = 120     -- full size, a little over the 800 circle (giant-crop style)
local BED_GROW_FULL_AT = 10 * const.HourDuration  -- "mid-morning": hour 10 of the bed's own sol
local BED_BASE_PCT = 100          -- base building, no Seasonal Blooms: Herb held at its fitted size
local BED_SCALE_TIME = false      -- ms for a timed SetScale(scale, time); false = one-argument form
local BED_NEUTRAL = RGB(100, 100, 100)  -- SetColorModifier's "no modification"
-- Varieties: the rotation index saved in each bed selects one entry. `state` is the bloom state
-- shown all sol; `tint` multiplies the lit colour per channel (100 = unchanged), so it acts on
-- the whole mesh: petals and leaves on the vanilla Herb, petals mostly on our white-petal meshes.
-- `base_scale` (optional) is the object scale at 100% for a mesh authored at bed size; without
-- it the bloom state's bbox is fitted to the BED_DIAMETER circle. Herb bloom is its 4th of 4
-- stages (SMR-Assets reference/crops/props.json); Packs/Meshes.fpk base game, never DLC.
-- The three custom entities may be absent: a missing entry is skipped and logged once.
-- Tints are starting values; the owner tunes them by eye.
local BED_VARIETIES = {
	{ entity = "CropHerb", state = "idle4", tint = RGB(100, 100, 100) },  -- vanilla red/purple/blue
	{ entity = "CropHerb", state = "idle4", tint = RGB(125, 85, 110) },   -- rose
	{ entity = "CropHerb", state = "idle4", tint = RGB(85, 95, 125) },    -- cornflower
	{ entity = "CropHerb", state = "idle4", tint = RGB(125, 115, 70) },   -- marigold
	{ entity = "CropHerb", state = "idle4", tint = RGB(105, 80, 125) },   -- violet
	{ entity = "CropHerb", state = "idle4", tint = RGB(125, 95, 80) },    -- coral
	{ entity = "SMROptInArboretumBloomSpike", state = "idle", tint = RGB(120, 70, 140), base_scale = 100 }, -- lavender spikes
	{ entity = "SMROptInArboretumBloomRound", state = "idle", tint = RGB(150, 110, 60), base_scale = 100 }, -- amber globes
	{ entity = "SMROptInArboretumBloomLow", state = "idle", tint = RGB(150, 80, 90), base_scale = 100 },    -- crimson carpet
}
local BASE_BED = BED_VARIETIES[1]  -- base building: neutral Herb in bloom
-- Rare Specimens showpieces, one per `Specimen` spot in turn (fruit trees at fruiting).
local SPECIMENS = {
	{ entity = "CropApples", bloom = 4 },
	{ entity = "CropApples", bloom = 4 },
}
-- Default planting on every `Specimen` spot until Rare Specimens replaces it (owner, 2026-10-05:
-- "put something modest there by default ... Maybe just do shrubs"). Vanilla shrubs the pavilion
-- already attaches (class Bush, Lua/Decor.lua:123; Lua/_EntityData.generated.lua:1430-1490
-- @1.1.1.406343). Offsets in cm from the spot, angles in arc-minutes (60 per degree), unscaled.
-- Footprints from SMR-Assets reference/meshes/props.json: offset + half-size stays inside the
-- SPECIMEN_DIAMETER circle (Bush_06 87, Bush_04 96, Bush_03 76 half-size).
local SPECIMEN_SHRUBS = {
	{ entity = "Bush_06", x = 0, y = 0, angle = 0 },              -- tall centre
	{ entity = "Bush_04", x = 130, y = 0, angle = 30 * 60 },
	{ entity = "Bush_03", x = -70, y = 115, angle = 120 * 60 },
	{ entity = "Bush_03", x = -70, y = -115, angle = 240 * 60 },
}
-- Upgrade ids: saved names (UIColony.unlocked_upgrades, the building's upgrade tables). They
-- must equal template.json's upgradeN_id values; the desk check compares them.
local UPGRADE_BOTS = "SMROptInArboretum_ServiceBots"
local UPGRADE_BLOOMS = "SMROptInArboretum_SeasonalBlooms"
local UPGRADE_SPECIMENS = "SMROptInArboretum_RareSpecimens"
local SERVICE_BOTS_TECH = "ServiceBots"   -- Data/Tech.lua:1949 @1.1.1.406343

-- persist_baseclass is a permanent-key namespace, not a parent: the key is "<it>:<class>"
-- (CommonLua/Core/persist.lua:163-168 @1.1.1.406343). Placed buildings are instances of the
-- generated SMROptInArboretum, keyed "SMROptInArboretumBase:SMROptInArboretum"; nothing is an
-- instance of this base, so its own key only has to stay stable. It keeps the inventoried
-- string from before the parent change. Parent order follows FarmBase (Lua/Buildings/Farm.lua:36)
-- and SpacebarBase (Lua/Buildings/Spacebar.lua:2).
DefineClass.SMROptInArboretumBase = {
	__parents = { "ElectricityConsumer", "LifeSupportConsumer", "ServiceWorkplace" },
	persist_baseclass = "LifeSupportConsumerService",
	-- Saved per building, created only when the pavilion carries the spots:
	SMROptInBeds = false,        -- { [bed] = { variety = BED_VARIETIES index, grown = ms, obj = crop } }
	SMROptInSpecimens = false,   -- { [spot] = { kind = "shrubs" | "showpiece", objs = { objects } } }
}

SMROptInPack.Register(ID, {
	title = "OPTIONAL: Arboretum, a staffed in-dome service whose gardeners use Seeds",
	optional = true,
	apply = function()
		if not SMROptInPack.OptionEnabled(ID) then
			return "opt-in module, off by default — enable it in Options → Mod Options"
		end
		return SMROptInPack.Require(ID, {
			{ class = "ServiceWorkplace", method = "UpdateServicePerformance" },
			{ class = "LifeSupportConsumer" },
			{ class = "ElectricityConsumer" },
			{ class = "Workplace", method = "GetWorkshiftPerformance" },
			{ class = "Workplace", method = "GetWorkersPerformance" },
			{ class = "HasConsumption", method = "Consume_Workshift" },
			{ class = "Service", method = "Service" },
			{ global = "IsSeedsResourceAvailable" },
			{ global = "IsGameRuleActive" },
		})
	end,
})

-- BuildMenu.lua:731 (archived 1.1.1.406343): additional locks hide the entry.
-- Restrict the handler to our template before inspecting any runtime state.
function OnMsg.GetAdditionalBuildingLocks(template, locks)
	if not template or (template.id ~= TEMPLATE and template.class ~= TEMPLATE
		and template.template_name ~= TEMPLATE) then return end
	if SMROptInPack_Disabled[ID] or not SMROptInPack.IsActive(ID) then
		locks.smr_arboretum_off = true
	elseif IsGameRuleActive("NoTerraforming") or not IsSeedsResourceAvailable() then
		locks.smr_arboretum_seeds = true
	end
end

-- The pavilion's glass, plants, benches, lamps and door leaves are `att,<class>,show`
-- spot annotations. The game turns annotations into Attaches[entity] only on DataChanged
-- (CommonLua/Classes/AutoAttach.lua:799-821,851-853 @1.1.1.406343), and a first load posts
-- that before a mod's entities exist: they are queued (CommonLua/Modding/Mod.lua:2150-2154)
-- and loaded with the first map's assets (CommonLua/Core/map.lua:245). Build this one
-- entity's table when it arrives, with the game's own reader. Not saved; a later
-- DataChanged rebuilds the same table natively.
local PAVILION = "SMROptInArboretumPavilion"
function OnMsg.AdditionalEntitiesLoaded(entities)
	if table.find(entities, PAVILION) and not Attaches[PAVILION] then
		Attaches[PAVILION] = GetEntityAutoAttachTable(PAVILION) or nil
	end
end

-- ===== Fail-soft helpers (RAM only, never saved) =====
local warned = {}
local function warn_once(key, fmt, ...)
	if warned[key] then return end
	warned[key] = true
	log("Arboretum: " .. fmt, ...)
end

local function stat_points(points)
	return points * const.Scale.Stat
end

-- ===== Upgrade unlocks =====
-- Upgrades are offered per id from UIColony.unlocked_upgrades (Lua/UpgradeUnlocks.lua:23-34,
-- Lua/Buildings/UpgradableBuilding.lua:330-332 @1.1.1.406343); vanilla Service Bots ids are
-- unlocked by the tech's Effect_UnlockUpgrade list (Data/Tech.lua:1950-1992), which cannot
-- name ours. Blooms and Specimens need no research; Service Bots follows the tech.
local function sync_unlocks()
	local colony = rawget(_G, "UIColony")
	if not (colony and colony.UnlockUpgrade and colony.IsUpgradeUnlocked) then
		warn_once("upgrade_api", "the upgrade unlock API is missing; Arboretum upgrades are not offered")
		return
	end
	for _, id in ipairs{ UPGRADE_BLOOMS, UPGRADE_SPECIMENS } do
		if not colony:IsUpgradeUnlocked(id) then colony:UnlockUpgrade(id) end
	end
	if colony:IsUpgradeUnlocked(UPGRADE_BOTS) then return end
	local techs = rawget(_G, "Techs")
	if not (techs and techs[SERVICE_BOTS_TECH] and colony.IsTechResearched) then
		warn_once("bots_tech", "tech %s is missing; Service Bots is not offered", SERVICE_BOTS_TECH)
	elseif colony:IsTechResearched(SERVICE_BOTS_TECH) then
		colony:UnlockUpgrade(UPGRADE_BOTS)
	end
end

-- Colony labels mirror each city's per-class labels (Lua/City.lua:82-85,
-- Lua/Buildings/Building.lua:461, Lua/Colony.lua:626-628 @1.1.1.406343).
local function any_arboretum()
	local colony = rawget(_G, "UIColony")
	local list = colony and colony.GetCityLabels and colony:GetCityLabels(TEMPLATE)
	return type(list) == "table" and #list > 0
end

function OnMsg.LoadGame()
	if any_arboretum() then sync_unlocks() end
end

function OnMsg.TechResearched(tech_id)
	if tech_id == SERVICE_BOTS_TECH and any_arboretum() then sync_unlocks() end
end

function SMROptInArboretumBase:SMROptInUpgradeOn(id)
	return self.IsUpgradeOn and self:IsUpgradeOn(id) and true or false
end

-- ===== Staffing, Seeds and performance =====

-- Filled worker slots on a shift and whether that is a full staff. Service Bots multiplies
-- max_workers by -100% (as Data/BuildingTemplate/Diner.lua:57-67 @1.1.1.406343); with no slots
-- left, every shift counts as fully staffed.
function SMROptInArboretumBase:SMROptInStaff(shift)
	local max = self.max_workers or 0
	if max <= 0 then return 0, true end
	local list = shift and self.workers and self.workers[shift]
	local filled = Min(list and #list or 0, max)
	return filled, filled >= max
end

-- Stocked: the store holds this shift's Seeds (the amount Consume_Workshift will charge).
function SMROptInArboretumBase:SMROptInStocked()
	return (self:GetConsumptionStoredResources() or 0) >= (self.consumption_amount or 0)
end

function SMROptInArboretumBase:SMROptInCurrentShift()
	return self.active_shift > 0 and self.active_shift or self.current_shift
end

-- Tended: working, the current shift staffed (or bots), and the Seeds there.
function SMROptInArboretumBase:SMROptInTended()
	if not self.working then return false end
	local filled, full = self:SMROptInStaff(self:SMROptInCurrentShift())
	return (filled > 0 or full) and self:SMROptInStocked()
end

-- Workplace:GetWorkshiftPerformance (Lua/Buildings/Workplace.lua:271-296 @1.1.1.406343) with
-- automation 1 already gives Max(workers, auto_performance): the unstaffed 100 keeps the
-- building working (HasWorkforce :183-186). On top of it: staffed and stocked lifts to the
-- STAFFED_PERFORMANCE floor or the workers' own (GetWorkersPerformance :250-269) when higher;
-- staffed without Seeds stays at the unstaffed floor. ServiceWorkplace averages this over the
-- open shifts into service_performance (Lua/Buildings/Service.lua:304-313), which scales the
-- dome's stats (Lua/Stats.lua:219-241).
function SMROptInArboretumBase:GetWorkshiftPerformance(shift)
	if self.active_shift > 0 then shift = self.active_shift end
	local max = self.max_workers or 0
	-- Before the first shift change current_shift is false (Lua/Buildings/ShiftsBuilding.lua:11).
	if not shift and max > 0 then return self.auto_performance end
	local native = Workplace.GetWorkshiftPerformance(self, shift)
	if native <= 0 then return native end -- shrouded in rubble (Workplace.lua:272-274)
	local filled, full = self:SMROptInStaff(shift)
	if (filled == 0 and not full) or not self:SMROptInStocked() then
		return self.automation > 0 and Min(native, self.auto_performance) or native
	end
	local count = #STAFFED_PERFORMANCE
	local floor = STAFFED_PERFORMANCE[full and count or Min(filled, count)]
	local own = max > 0 and self:GetWorkersPerformance(shift) or 0
	return Max(own, floor)
end

-- Workplace:UpdatePerformance (Workplace.lua:298-308) writes auto_performance directly when
-- max_workers is 0, which would bypass the method above under Service Bots. Same body, one path.
-- ServiceWorkplace:GetEffectivePerformance (Service.lua:340-352) reads this value when
-- colonists choose a service (Lua/ServiceBase.lua:288-306).
function SMROptInArboretumBase:UpdatePerformance()
	self:SetBase("performance", self:GetWorkshiftPerformance(self:SMROptInCurrentShift()))
	ObjModified(self)
end

function SMROptInArboretumBase:SMROptInRefreshPerformance()
	if not self.workers then return end -- before Workplace:Init (Workplace.lua:37-46)
	self:UpdatePerformance()
	self:UpdateServicePerformance()
end

-- An empty store never closes it. HasConsumption:Consume_Internal stops the building when
-- CanConsume turns false (Lua/HasConsumption.lua:397-402) and Building:GetWorkNotPossibleReason
-- reports it (Lua/Buildings/Building.lua:640-642); ReconCenterBase answers true the same way
-- (Lua/Buildings/ReconCenter.lua:104-106 @1.1.1.406343).
function SMROptInArboretumBase:CanConsume()
	return true
end

-- Seeds by the staff: Workplace:OnChangeWorkshift charges every shift change
-- (Workplace.lua:1154-1182, HasConsumption.lua:382-386). ShiftsBuilding:SetWorkshift calls it
-- before current_shift moves (ShiftsBuilding.lua:131-136), so current_shift is the shift that
-- just ended. Charge only a shift that worked, was staffed (or bots) and had its Seeds; the
-- unstaffed or unstocked shift ran at the floor and costs nothing.
function SMROptInArboretumBase:Consume_Workshift()
	local shift = self:SMROptInCurrentShift()
	if not shift or not self.working or self:IsClosedShift(shift) then return 0 end
	local filled, full = self:SMROptInStaff(shift)
	if (filled == 0 and not full) or not self:SMROptInStocked() then return 0 end
	return HasConsumption.Consume_Workshift(self) or 0
end

-- Upgrades change consumption_amount (the stocked threshold), Comfort and service_capacity
-- through modifiers (Lua/Buildings/Building.lua:1171-1225). OnModifiableValueChanged is a
-- combined "call" method (Lua/Modifiers.lua:1), so this adds to the parents' handlers.
-- A toggle does not restart the building (Building.lua:1261-1283), so ask for a reassignment.
function SMROptInArboretumBase:OnModifiableValueChanged(prop)
	if prop == "consumption_amount" then
		self:SMROptInRefreshPerformance()
	elseif prop == "service_capacity" or prop == "Comfort" then
		if prop == "Comfort" then self:ComputeServiceImpact() end
		QueueReassignServices(self.parent_dome, self:GetServiceCategory())
	end
end

-- Seasonal Blooms: Comfort on leaving, and Sanity for a Melancholic. Service:Service plays the
-- visit through Unit:PlayPrg, which returns when the visit ends (Lua/Buildings/Service.lua:269-275,
-- Lua/Units/Unit.lua:902-928 @1.1.1.406343); CasinoComplexBase extends Service the same way
-- (Lua/Buildings/CasinoComplex.lua:4-12). The template name as reason logs "Visited Arboretum"
-- (Lua/Units/Colonist.lua:4183-4190).
function SMROptInArboretumBase:Service(unit, duration, daily_interest)
	ServiceWorkplace.Service(self, unit, duration, daily_interest)
	if not IsValid(self) or not IsValid(unit) or (unit.IsDead and unit:IsDead()) then return end
	if not self:SMROptInUpgradeOn(UPGRADE_BLOOMS) then return end
	local reason = self.template_name
	if unit.ChangeComfort then
		unit:ChangeComfort(stat_points(BLOOMS_VISIT_COMFORT), reason)
	end
	if unit.traits and unit.traits.Melancholic and unit.ChangeSanity then
		unit:ChangeSanity(stat_points(BLOOMS_MELANCHOLIC_SANITY), reason)
	end
end

-- ===== Display beds and specimens =====
-- The farm's route (Lua/Buildings/Farm.lua:334-345 @1.1.1.406343): place an object of the crop
-- entity's class, or CropEntityClass (Farm.lua:1-8) when no class carries the entity, and attach
-- it to a spot. A crop entity's growth states are "idle", "idle2", "idle3"... (Lua/Crop.lua:17-22
-- fallback; Lua/Vegetation.lua:163-172 walks them with HasState); the survey's mesh, mesh2...
-- stages are those states in order. CropEntityClass attaches are removed on demolish and warped
-- by wind like a farm's (Lua/Buildings/Building.lua:1449,2531).

local function spot_range(obj, spot)
	if not obj:HasSpot(spot) then return end
	local first, last = obj:GetSpotRange(spot)
	if not first or first < 0 or not last or last < first then return end
	return first, last
end

local function stage_state(stage)
	return stage <= 1 and "idle" or ("idle" .. stage)
end

-- The highest state at or below `stage` that the entity has.
local function best_state(obj, stage)
	for s = stage, 2, -1 do
		local state = stage_state(s)
		if HasState(obj, state) then return state end
	end
	return "idle"
end

-- IsValidEntity: "whether an entity with the specified name exists and can be loaded"
-- (CommonLua/LuaExportedDocs/Game/LuaExports.lua:17-22 @1.1.1.406343).
local function entity_ok(ent)
	if ent and IsValidEntity(ent) then return true end
	warn_once("entity:" .. tostring(ent), "entity %s is missing; that display is skipped", tostring(ent))
end

local function show_state(obj, state)
	if not HasState(obj, state) then state = "idle" end
	if obj:GetState() ~= GetStateIdx(state) then obj:SetState(state) end
end

-- Bed records hold one `obj`; Specimen records hold `objs`.
local function clear_record(rec)
	if type(rec) ~= "table" then return end
	for _, o in ipairs(rec.objs or { rec.obj }) do
		if IsValid(o) then DoneObject(o) end
	end
end

local function clear_objects(list)
	for _, rec in pairs(list or empty_table) do clear_record(rec) end
end

-- Place an object showing `ent` on a spot. Base-game crops have a class named for the entity
-- (generated from EntityData, CommonLua/Classes/EntityClass.lua:17-80); a mod entity may not, so
-- it goes on a CropEntityClass object with object:ChangeEntity (LuaExportedDocs/Game/GameObject.lua:180-185).
local function place_display(bld, spot_idx, ent)
	local obj
	if g_Classes[ent] then
		obj = PlaceObjectIn(ent, bld)
	else
		obj = PlaceObjectIn("CropEntityClass", bld)
		obj:ChangeEntity(ent)
	end
	bld:Attach(obj, spot_idx)
	return obj
end

-- The scale at which the object's current state fits a circle: object:GetEntityBBox is the
-- current state's box without the object's scale (GameObject.lua:403-407); Max(sizex, sizey)
-- as Lua/Buildings/MarsReservation.lua:46-47 @1.1.1.406343. Cached per entity and state, RAM only.
local fit_cache = {}
local function fit_scale(obj, diameter)
	local key = obj:GetEntity() .. ":" .. obj:GetState() .. ":" .. diameter
	local scale = fit_cache[key]
	if scale then return scale end
	local box = obj:GetEntityBBox()
	local extent = box and Max(box:sizex(), box:sizey()) or 0
	scale = extent > 0 and Clamp(MulDivTrunc(diameter, 100, extent), CROP_SCALE_MIN, CROP_SCALE_MAX) or 100
	fit_cache[key] = scale
	return scale
end

-- The one place a display's scale is written. The exported docs give SetScale one argument
-- (GameObject.lua:1006-1012); XPrg generates a two-argument call (CommonLua/X/XPrg.lua:1144,1148)
-- that is unconfirmed in the game, so BED_SCALE_TIME stays false until it is.
local function set_scale(obj, scale)
	if obj:GetScale() == scale then return end
	if BED_SCALE_TIME then obj:SetScale(scale, BED_SCALE_TIME) else obj:SetScale(scale) end
end

-- SetColorModifier, RGB(100, 100, 100) = no modification (GameObject.lua:187-194).
local function set_tint(obj, tint)
	if obj:GetColorModifier() ~= tint then obj:SetColorModifier(tint) end
end

-- One Rare Specimens showpiece, fitted to the Specimen circle at its bloom stage.
function SMROptInArboretumBase:SMROptInShowSpecimen(spot_idx, crop)
	if not entity_ok(crop.entity) then return false end
	local obj = place_display(self, spot_idx, crop.entity)
	obj:SetState(best_state(obj, crop.bloom))
	set_scale(obj, fit_scale(obj, SPECIMEN_DIAMETER))
	return obj
end

-- One bed: `variety` in bloom at `pct` of its full size, tinted. Reuses the bed's object while
-- the entity matches (a new variety of the same entity only changes tint and size).
function SMROptInArboretumBase:SMROptInShowBed(obj, spot_idx, variety, pct)
	if not (IsValid(obj) and obj:GetEntity() == variety.entity) then
		if IsValid(obj) then DoneObject(obj) end
		if not entity_ok(variety.entity) then return false end
		obj = place_display(self, spot_idx, variety.entity)
	end
	show_state(obj, variety.state)
	local full = variety.base_scale or fit_scale(obj, BED_DIAMETER)
	set_scale(obj, Clamp(MulDivTrunc(full, pct, 100), 1, CROP_SCALE_MAX))
	set_tint(obj, variety.tint or BED_NEUTRAL)
	return obj
end

-- The first variety at or after `index` (wrapping) whose entity exists; false if none does.
local function usable_variety(index)
	local n = #BED_VARIETIES
	if type(index) ~= "number" or index ~= index then index = 1 end
	for k = 0, n - 1 do
		local i = (index - 1 + k) % n + 1
		if entity_ok(BED_VARIETIES[i].entity) then return i end
	end
	return false
end

-- Percent of full size `grown` ms into a bed's sol: BED_GROW_START_PCT at the replant, rising
-- linearly to BED_GROW_FULL_PCT at BED_GROW_FULL_AT, then held until the next replant.
local function bed_pct(grown)
	if grown >= BED_GROW_FULL_AT then return BED_GROW_FULL_PCT end
	return BED_GROW_START_PCT + MulDivTrunc(BED_GROW_FULL_PCT - BED_GROW_START_PCT, grown, BED_GROW_FULL_AT)
end

-- Without Seasonal Blooms each bed shows BASE_BED at BED_BASE_PCT. With it, each bed grows by
-- scale over one sol of tended time and is then replanted with the next variety. Growth runs
-- only while tended: unstaffed, out of Seeds or not working, nothing grows or is replanted.
-- The record keeps its shape ({ variety, grown, obj }); a variety index from an earlier table
-- is wrapped into range, and an object of another entity is replaced.
function SMROptInArboretumBase:SMROptInUpdateBeds(delta)
	local first, last = spot_range(self, BED_SPOT)
	if not first then
		if self.SMROptInBeds then
			clear_objects(self.SMROptInBeds)
			self.SMROptInBeds = false
		end
		warn_once("no_beds", "the pavilion has no %s spots; display beds are off", BED_SPOT)
		return
	end
	local blooms = self:SMROptInUpgradeOn(UPGRADE_BLOOMS)
	local tended = blooms and delta > 0 and self:SMROptInTended()
	local sol = const.DayDuration
	local beds = self.SMROptInBeds or {}
	self.SMROptInBeds = beds
	for i = 1, last - first + 1 do
		local bed = beds[i]
		if not bed then
			bed = { variety = (i - 1) % #BED_VARIETIES + 1,
				grown = MulDivTrunc(sol, (i - 1) % BED_STAGGER_PARTS, BED_STAGGER_PARTS) }
			beds[i] = bed
		end
		if type(bed.grown) ~= "number" then bed.grown = 0 end
		local variety, pct
		if blooms then
			if tended then
				bed.grown = bed.grown + delta
				if bed.grown >= sol then
					bed.grown = bed.grown - sol
					bed.variety = (type(bed.variety) == "number" and bed.variety or 0) + 1
				end
			end
			local index = usable_variety(bed.variety)
			if index then bed.variety = index end
			variety, pct = index and BED_VARIETIES[index], bed_pct(bed.grown)
		else
			variety, pct = entity_ok(BASE_BED.entity) and BASE_BED, BED_BASE_PCT
		end
		if variety then
			bed.obj = self:SMROptInShowBed(bed.obj, first + i - 1, variety, pct)
		else
			if IsValid(bed.obj) then DoneObject(bed.obj) end
			bed.obj = false
		end
	end
end

-- The shrub group on one Specimen spot: attach to the spot, then offset and turn it, as
-- BaseBuilding:DoUpdateSignsVisibility attaches then SetAttachOffset (Lua/Buildings/BaseBuilding.lua:843-847)
-- and Building.lua:1659-1661 sets SetAttachOffset / SetAttachAngle before Attach @1.1.1.406343.
-- Any missing shrub entity leaves the spot empty.
local function place_shrubs(bld, spot_idx)
	for _, shrub in ipairs(SPECIMEN_SHRUBS) do
		if not entity_ok(shrub.entity) then return {} end
	end
	local objs = {}
	for i, shrub in ipairs(SPECIMEN_SHRUBS) do
		local obj = PlaceObjectIn(shrub.entity, bld)
		bld:Attach(obj, spot_idx)
		obj:SetAttachOffset(point(shrub.x, shrub.y, 0))
		obj:SetAttachAngle(shrub.angle)
		objs[i] = obj
	end
	return objs
end

local function record_intact(rec, kind)
	if type(rec) ~= "table" or rec.kind ~= kind or not rec.objs or #rec.objs == 0 then return false end
	for _, o in ipairs(rec.objs) do
		if not IsValid(o) then return false end
	end
	return true
end

-- The one path that decides what each Specimen spot shows: the shrub group by default, the
-- showpiece while Rare Specimens is on. Runs at build, every building update (so after a load)
-- and on every upgrade change; a spot already showing the right kind is left alone.
function SMROptInArboretumBase:SMROptInUpdateSpecimens()
	local first, last = spot_range(self, SPECIMEN_SPOT)
	if not first then
		if self.SMROptInSpecimens then
			clear_objects(self.SMROptInSpecimens)
			self.SMROptInSpecimens = false
		end
		warn_once("no_specimens", "the pavilion has no %s spots; specimen plantings are off", SPECIMEN_SPOT)
		return
	end
	local showpiece = self:SMROptInUpgradeOn(UPGRADE_SPECIMENS)
	local kind = showpiece and "showpiece" or "shrubs"
	local list = self.SMROptInSpecimens or {}
	self.SMROptInSpecimens = list
	for i = 1, last - first + 1 do
		local rec = list[i]
		local spot_idx = first + i - 1
		if not record_intact(rec, kind) then
			clear_record(rec)
			local objs
			if showpiece then
				local crop = SPECIMENS[(i - 1) % #SPECIMENS + 1]
				local obj = self:SMROptInShowSpecimen(spot_idx, crop)
				objs = obj and { obj } or {}
			else
				objs = place_shrubs(self, spot_idx)
			end
			list[i] = { kind = kind, objs = objs }
		end
	end
end

function SMROptInArboretumBase:SMROptInUpdateDisplay(delta)
	self:SMROptInUpdateBeds(delta or 0)
	self:SMROptInUpdateSpecimens()
end

-- One error stops the displays for the session, logged once; the service keeps running.
local display_broken = false
local function update_display(bld, delta)
	if display_broken then return end
	local ok, err = pcall(bld.SMROptInUpdateDisplay, bld, delta)
	if not ok then
		display_broken = true
		log("Arboretum: display beds stopped after an error: %s", tostring(err))
	end
end

-- ===== Hooks (combined or own-class methods; parents still run) =====

-- GameInit is a combined procall (CommonLua/Classes/_object.lua:22 @1.1.1.406343).
function SMROptInArboretumBase:GameInit()
	sync_unlocks()
	update_display(self, 0)
end

-- BuildingUpdate is a combined "call", parents first, every building_update_time with the
-- elapsed time (Lua/Buildings/Building.lua:1,810-830; Workplace.lua:25 a quarter hour).
-- Deliveries and spoilage change the stock between shifts; refresh when "stocked" flips.
local seen_stocked = setmetatable({}, { __mode = "k" })
function SMROptInArboretumBase:BuildingUpdate(delta)
	local stocked = self:SMROptInStocked()
	if seen_stocked[self] ~= stocked then
		seen_stocked[self] = stocked
		self:SMROptInRefreshPerformance()
	end
	update_display(self, delta or 0)
end

-- Building:OnUpgradeToggled is an empty callback after the on/off state flips
-- (Lua/Buildings/Building.lua:1261-1287 @1.1.1.406343).
function SMROptInArboretumBase:OnUpgradeToggled(upgrade_id, new_state)
	update_display(self, 0)
end

-- ApplyUpgrade marks a new upgrade on, then posts BuildingUpgraded (Building.lua:1236,1254).
function OnMsg.BuildingUpgraded(id, bld)
	if IsKindOf(bld, "SMROptInArboretumBase") then update_display(bld, 0) end
end
