-- Train hub (Module B): one shared base, one thin class per size.
-- Dev build for game 1.1.0.403908; every source line below was read on that
-- build (C:\Dev\SMR-SrcArchive\1.1.0.403908\Src). UNVERIFIED in game until the
-- sitting in docs/agent/reports/TRAIN_HUB_BUILD_20260918.md is recorded.
-- Authority: owner rulings 2026-09-18, spec §10
-- (docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md).
--
-- NAMES THAT REACH A SAVE (FIX_POLICY ban 1; permanent once a kept save sees them):
--   SMROptInTrainHub6        template id = the placed object's class, and a city label
--   SMROptInTrainHub6Base    the six's object_class, and a city label
--   SMROptInTrainHub4 / SMROptInTrainHub4Base   RESERVED for the four; not built
--   SMROptIn_floor_hold      field on hub objects (10_TrainFloor.lua)
--   "SMROptInTrainHub6Base:SMROptInTrainHub6"   the object's persist key: the
--       generated class carries persist_baseclass = its object_class, which is
--       what the Mod Editor writes (Composite.lua:522-523). The prototype's
--       hand-written "Station" is NOT carried over: an editor round-trip would
--       have changed the key under a kept save.
-- `SMROptInTrainHubBase` below is never instantiated and never a label.
--
-- THE ASSET SWAP IS ONE CHANGE: the template's `entity`. Everything that reads
-- the body asks the body first and computes only what it lacks:
--   * each real connector/direction spot wins; the asset lacks the train
--     operating spots, so those remain computed from the proven geometry;
--   * the charging point: `RechargeStationPlatform` auto-attaches win; a body
--     without one gets a computed platform;
--   * cargo pallets: attached `StorageDepotFood` sub-models win (the stand-in);
--     a body with its own `Box1` spots uses those (the owner's asset).

local Floor = SMROptInTrainFloor

DefineClass.SMROptInTrainHubBase = {
	__parents = { "Station", "DroneControl", "ElectricityProducer" },
	flags = { cfConstructible = true, efWalkable = true },

	-- Geometry. `hub_connector_directions[i]` is connector i's local hex
	-- direction 0..5. Pair order is load-bearing: (1,2), (3,4), (5,6) are the
	-- opposite ends of straight lines, and the whole star turns with the body.
	first_connector_idx = 1,
	last_connector_idx = 0,
	hub_connector_directions = false,

	-- Drone controller. Members both parents declare are pinned here, so the
	-- result never depends on parent order: Station.lua:87 vs DroneControl.lua:96
	-- (building_update_time), Station.lua:72 vs TaskRequest.lua:232
	-- (accept_requester_connects), PinnableObject.lua:267 vs DroneControl.lua:876
	-- (OnPinClicked; DroneHubBase makes the same choice, DroneHub.lua:19).
	building_update_time = 5000,
	accept_requester_connects = true,
	auto_connect_requesters_at_start = true,
	OnPinClicked = DroneControl.OnPinClicked,
	starting_drones = 2,
	show_service_area = true,
	show_range = true,
	service_area_min = 10,
	service_area_max = 20,
	work_radius = 10,
	charging_stations = false,
	electricity_consumption = 10000,
	electricity_production = 70000,

	-- Maintenance reserve: this many maintenances' worth of the maintenance
	-- resource is held back from trains and drones (10_TrainFloor.lua).
	hub_reserve_maintenances = 2,
}

-- Owner ruling 2026-09-19: keep this building's own Production/Consumption
-- presentation, but omit the shared-grid summary to leave panel room for the
-- train controls. ipBuilding gates only sectionPowerGrid through this method.
function SMROptInTrainHubBase:ShowUISectionElectricityGrid()
	return false
end

-- `sectionCustom` looks up an XTemplate named for the template's object_class.
-- Reuse the vanilla Drone Hub's prefab controls and status presentation. The
-- inherited DroneControl methods perform the actual unpack/pack operations;
-- this template adds no state and no persisted name. The service-area section
-- and slider are supplied by ipBuilding, while `show_range` makes the selected
-- building use vanilla's RangeHexRadius overlay.
local function ensure_hub_infopanel()
	if not XTemplates or XTemplates.customSMROptInTrainHub6Base then return end
	local template = PlaceObj("XTemplate", {
		group = "Infopanel Sections",
		id = "customSMROptInTrainHub6Base",
	}, {
		PlaceObj("XTemplateWindow", {
			"__class", "InfopanelButton",
			"RolloverText", T(8460, "Unpack an existing Drone Prefab to build a new Drone. Drone Prefabs can be created from existing Drones or in a Drone Assembler (requires research). This action can be used to quickly reassign Drones between controllers.<newline><newline>Available Drone Prefabs:<right><drone(available_drone_prefabs)>"),
			"RolloverTitle", T(349, "Unpack Drone"),
			"RolloverHint", T(8461, "<left_click> Unpack Drone <em>Ctrl + <left_click></em> Unpack five Drones"),
			"RolloverHintGamepad", T(830531229840, "<ButtonA> Unpack Drone <ButtonY> Unpack five Drones"),
			"OnContextUpdate", function(self, context)
				self:SetEnabled(ColonyGetAvailableDronePrefabs(UICity) > 0 and context:CanHaveMoreDrones())
			end,
			"OnPressParam", "UseDronePrefab",
			"OnPress", function(self, gamepad)
				self.context:UseDronePrefab(not gamepad and IsMassUIModifierPressed())
			end,
			"AltPress", true,
			"OnAltPress", function(self, gamepad)
				if gamepad then self.context:UseDronePrefab(true) end
			end,
			"Icon", "UI/IconsRemaster/IPButtons/drone_assemble.png",
		}),
		PlaceObj("XTemplateWindow", {
			"__class", "InfopanelButton",
			"RolloverText", T(8665, "Recalls a Drone and packs it into a Drone Prefab. Can be used to reassign Drones between controllers."),
			"RolloverDisabledText", T(8666, "No available Drones."),
			"RolloverTitle", T(8667, "Pack Drone for Reassignment"),
			"RolloverHint", T(8668, "<left_click> Pack Drone for reassignment <em>Ctrl + <left_click></em> Pack five Drones"),
			"RolloverHintGamepad", T(943040205774, "<ButtonA> Pack Drone for reassignment <ButtonY> Pack five Drones"),
			"OnContextUpdate", function(self, context)
				self:SetEnabled(not not context:FindDroneToConvertToPrefab())
			end,
			"OnPressParam", "ConvertDroneToPrefab",
			"OnPress", function(self, gamepad)
				self.context:ConvertDroneToPrefab(not gamepad and IsMassUIModifierPressed())
			end,
			"AltPress", true,
			"OnAltPress", function(self, gamepad)
				if gamepad then self.context:ConvertDroneToPrefab(true) end
			end,
			"Icon", "UI/IconsRemaster/IPButtons/drone_dismantle.png",
		}),
		PlaceObj("XTemplateWindow", {
			"__class", "InfopanelSection",
			"RolloverText", T(359011926905, "<UISectionDroneHubRollover>"),
			"RolloverTitle", T(167050805716, "Drones Status"),
			"Title", T(732959546527, "Drones"),
			"TitleRight", T(745904750458, "<drone(DronesCount,MaxDronesCount)>"),
			"Icon", "UI/IconsRemaster/Sections/drone.png",
			"TitleHAlign", "stretch",
		}, {
			PlaceObj("XTemplateCode", {
				"run", function(self, parent, context)
					local content = InfopanelSection.__content(parent, context)
					return InfopanelText:new({
						Text = T(935141416350, "<DronesStatusText>"),
					}, content, context)
				end,
			}),
		}),
	})
	-- Runtime-created presets are not inserted in their GlobalMap by PlaceObj.
	-- sectionCustom reads this exact map; the id is UI-only and never saved.
	XTemplates.customSMROptInTrainHub6Base = template
end

ensure_hub_infopanel()

-- ===========================================================================
-- Geometry (the prototype's, proven in sitting 2: six connectors attached,
-- three routes, 0 Lua errors). Computed spots are used only for names the body
-- does not carry itself.
-- ===========================================================================

local synthetic_base = 900000
local kind_code = { Trackconnector = 1, Trackdirection = 2, Ramparrive = 3, Stop = 4, Spawn = 5, Rampdepart = 6, Sign = 7 }
local code_kind = { "Trackconnector", "Trackdirection", "Ramparrive", "Stop", "Spawn", "Rampdepart", "Sign" }

local function parse_synthetic_name(self, name)
	if type(name) ~= "string" then return end
	local kind, number = name:match("^([%a]+)(%d+)$")
	local idx = tonumber(number)
	local code = kind_code[kind]
	if code and idx and idx >= 1 and idx <= (self.last_connector_idx or 0) then
		return synthetic_base + code * 10 + idx
	end
end

local function decode_synthetic_spot(spot)
	if type(spot) ~= "number" or spot < synthetic_base then return end
	local value = spot - synthetic_base
	local kind = code_kind[value // 10]
	local idx = value % 10
	if kind and idx >= 1 then return kind, idx end
end

local function opposite(idx)
	return idx % 2 == 1 and idx + 1 or idx - 1
end

-- A connector must sit inside the footprint (Tracks.lua:19-24), so each one is
-- the LAST footprint hex along its line and its direction hex the first outside.
local line_radius_cache = {}
local function line_radii(entity)
	local radii = line_radius_cache[entity]
	if radii then return radii end
	local inside = {}
	for _, pt in ipairs(GetEntityOutlineShape(entity) or empty_table) do
		local q, r = pt:xy()
		inside[q * 1000 + r] = true
	end
	radii = { inside = inside }
	for direction = 0, 5 do
		local dq, dr = HexRotate(1, 0, direction)
		local radius = 0
		while radius < 30 and inside[dq * (radius + 1) * 1000 + dr * (radius + 1)] do
			radius = radius + 1
		end
		radii[direction] = Max(radius, 1)
	end
	line_radius_cache[entity] = radii
	print(string.format("[TrainHubDev] %s line radii d0..d5 = %d %d %d %d %d %d",
		tostring(entity), radii[0], radii[1], radii[2], radii[3], radii[4], radii[5]))
	return radii
end

local function longest_line(self)
	local radii = line_radii(self:GetEntity())
	local longest = 1
	for _, direction in ipairs(self.hub_connector_directions or empty_table) do
		longest = Max(longest, radii[direction])
	end
	return longest
end

-- Sevenths of the way from the centre to the connector; nil is a whole hex.
local kind_sevenths = { Ramparrive = 5, Rampdepart = 5, Stop = 3, Spawn = 3 }

-- `body` is the hub or its construction cursor; `hub` supplies the class data.
local function line_hex(hub, body, connector_idx, extra)
	local local_direction = hub.hub_connector_directions[connector_idx]
	local radius = line_radii(body:GetEntity())[local_direction] + (extra or 0)
	local building_direction = HexAngleToDirection(body:GetAngle())
	local q, r = WorldToHex(body:GetPos())
	local lq, lr = HexRotate(radius, 0, local_direction)
	local dq, dr = HexRotate(lq, lr, building_direction)
	return q + dq, r + dr, (local_direction + building_direction) % 6
end

local function synthetic_spot_pos(self, kind, idx)
	local sevenths = kind_sevenths[kind]
	local connector_idx = kind == "Spawn" and opposite(idx) or idx
	local q, r, direction = line_hex(self, self, connector_idx, kind == "Trackdirection" and 1 or 0)
	local x, y = HexToWorld(q, r)
	local cx, cy, z = self:GetPosXYZ()
	if sevenths then
		x = cx + MulDivRound(x - cx, sevenths, 7)
		y = cy + MulDivRound(y - cy, sevenths, 7)
	end
	return point(x, y, z), direction
end

local function synthetic_spot_angle(self, kind, idx)
	local pos = synthetic_spot_pos(self, kind, idx)
	local center = self:GetPos()
	if kind == "Stop" or kind == "Ramparrive" then
		return CalcOrientation(pos, center)
	end
	return CalcOrientation(center, pos)
end

-- Does the body carry its own connector spots? Decided once per entity from
-- connector 1; a body carries either the whole set or none of it.
local body_has_spots = {}
local function uses_body_spots(self)
	local entity = self:GetEntity()
	local known = body_has_spots[entity]
	if known == nil then
		-- The stand-in carries vanilla's Trackconnector1..4 in vanilla's places,
		-- which are not this hub's lines. It is named, so nothing is guessed.
		known = entity ~= "TrainStationLargeCCP3" and CObject.HasSpot(self, "Trackconnector1") or false
		body_has_spots[entity] = known
		print(string.format("[TrainHubDev] %s connector spots: %s", tostring(entity), known and "from the body" or "computed"))
	end
	return known
end

function SMROptInTrainHubBase:GetSpotBeginIndex(state, type_id)
	local name = type_id == nil and state or type_id
	if not uses_body_spots(self) or not CObject.HasSpot(self, name) then
		local synthetic = parse_synthetic_name(self, name)
		if synthetic then return synthetic end
	end
	if type_id == nil then return CObject.GetSpotBeginIndex(self, state) end
	return CObject.GetSpotBeginIndex(self, state, type_id)
end

-- PlaceUnderconstructionSigns (UnderconstructionSign.lua:41-56) attaches a sign
-- to every `Sign<i>` spot. The stand-in's four point along vanilla's platforms.
function SMROptInTrainHubBase:HasSpot(name, ...)
	if not uses_body_spots(self) and type(name) == "string" and name:match("^Sign%d+$") then return false end
	if type(name) == "string" and not name:match("^Sign%d+$")
		and parse_synthetic_name(self, name)
		and (not uses_body_spots(self) or not CObject.HasSpot(self, name))
	then
		return true
	end
	return CObject.HasSpot(self, name, ...)
end

function SMROptInTrainHubBase:GetSpotPos(spot)
	local kind, idx = decode_synthetic_spot(spot)
	if kind then return (synthetic_spot_pos(self, kind, idx)) end
	return CObject.GetSpotPos(self, spot)
end

function SMROptInTrainHubBase:GetSpotLoc(spot)
	local kind, idx = decode_synthetic_spot(spot)
	if kind then
		return synthetic_spot_pos(self, kind, idx), synthetic_spot_angle(self, kind, idx), axis_z, 100
	end
	return CObject.GetSpotLoc(self, spot)
end

function SMROptInTrainHubBase:GetSpotPosHex(spot)
	local kind, idx = decode_synthetic_spot(spot)
	if kind then
		local pos, direction = synthetic_spot_pos(self, kind, idx)
		local q, r = WorldToHex(pos)
		return q, r, direction
	end
	return CObject.GetSpotPosHex(self, spot)
end

function SMROptInTrainHubBase:GetSpotAxisAngle(spot)
	local kind, idx = decode_synthetic_spot(spot)
	if kind then return axis_z, synthetic_spot_angle(self, kind, idx) end
	return CObject.GetSpotAxisAngle(self, spot)
end

-- Vanilla creates only indices 0..4 (TrainTransport.lua). Same body, class bounds.
function SMROptInTrainHubBase:CreateConnectorElements(force)
	local map = ResolveMap(self)
	local _, _, z = self:GetPosXYZ()
	for i = self.first_connector_idx, self.last_connector_idx do
		local dirspot = self:GetSpotBeginIndex("Trackdirection" .. i)
		local conspot = self:GetSpotBeginIndex("Trackconnector" .. i)
		if conspot >= 0 and dirspot >= 0 then
			local conpos = self:GetSpotPos(conspot)
			local dirpos = self:GetSpotPos(dirspot)
			local q, r = WorldToHex(conpos)
			local el = HexGetTrackGridElement(map.object_hex_grid, q, r)
			if IsValid(el) and (force or el.station ~= self) then
				assert(force or not IsValid(el.station) or IsBeingDestructed(el.station))
				DoneObject(el)
				el = nil
			end
			if not IsValid(el) then
				el = TrackGridElement:new({
					city = self.city,
					q = q,
					r = r,
					station = self,
					connections = {},
					track_obj = PlaceObjectIn("TrackBase", map),
					node_idx = 1,
				}, map)
				local x, y = HexToWorld(q, r)
				el:SetPos(x, y, z)
				el:Face(dirpos)
				el:SetGameFlags(const.gofPermanent)
				el:ClearEnumFlags(const.efVisible)
				el:ApplyToGrids()
				el:AutoConnectTracks("start element")
			end
		end
	end
end

-- Vanilla searches indices 0..4 only.
function SMROptInTrainHubBase:GetTrackConnectionSpot(q, r, spot_name)
	for i = self.first_connector_idx, self.last_connector_idx do
		local spot = self:GetSpotBeginIndex((spot_name or "Trackconnector") .. i)
		if spot >= 0 then
			local qq, rr = self:GetSpotPosHex(spot)
			if q == qq and r == rr then return i end
		end
	end
	return false
end

-- Vanilla Station:CanBuildOver (Station.lua:615-660) reads the connector spots
-- from the construction cursor, which has none of this class's computed spots
-- (sitting 1's Lua error). Same body, hexes computed from the cursor.
function SMROptInTrainHubBase:CanBuildOver(obstructors, cursor_obj)
	local spots = {}
	local this = cursor_obj or self
	local map = ResolveMap(this)
	for i = self.first_connector_idx, self.last_connector_idx do
		local q, r = line_hex(self, this, i)
		spots[i] = point(q, r)
	end
	for i = #spots - 1, 1, -2 do
		local q1, r1 = spots[i]:xy()
		local q2, r2 = spots[i + 1]:xy()
		local dir, len = HexGetDirection(q1, r1, q2, r2)
		local dq, dr = q2 - q1, r2 - r1
		if dq ~= 0 then dq = dq / abs(dq) end
		if dr ~= 0 then dr = dr / abs(dr) end
		for _, obj in ipairs(obstructors) do
			if not IsKindOf(obj, "TrackGridElement") then
				return false
			end
			local q, r = obj.q, obj.r
			local d, l = HexGetDirection(q1, r1, q, r)
			if not (q == q1 and r == r1) and (not d or d ~= dir or l > len) then
				table.remove(spots, i + 1)
				table.remove(spots, i)
				break
			end
		end
		local el = HexGetTrackGridElement(map.object_hex_grid, q1 - dq, r1 - dr)
		if el and not IsTrackElementStraight(el) then
			return false, el
		end
		el = HexGetTrackGridElement(map.object_hex_grid, q2 + dq, r2 + dr)
		if el and not IsTrackElementStraight(el) then
			return false, el
		end
	end
	return #spots > 0
end

-- GridConstructionController:Activate (GridConstruction.lua:287-295) moves a
-- track's start from a connector element to its direction hex, for 0..4 only.
-- As proven in sitting 2, the move is done here for every hub connector.
local vanilla_grid_activate = GridConstructionController.Activate
function GridConstructionController:Activate(pt, ...)
	if self.mode == "track_grid" and not self.starting_point and pt then
		local q, r = WorldToHex(pt)
		local el = HexGetTrackGridElement(self:GetMap().object_hex_grid, q, r)
		local hub = el and el.station
		if IsValid(hub) and IsKindOf(hub, "SMROptInTrainHubBase") then
			local idx = hub:GetTrackConnectionSpot(q, r)
			if idx then
				local dq, dr = hub:GetConnectorElementDirection(idx)
				pt = point(HexToWorld(dq, dr))
			end
		end
	end
	return vanilla_grid_activate(self, pt, ...)
end

-- ===========================================================================
-- Line markers. Until the asset shows where track attaches, each line has one
-- colour at both ends. Unsaved; rebuilt on load. They go when the asset lands.
-- ===========================================================================

local hub_markers = setmetatable({}, weak_keys_meta)
local line_colour = { RGB(255, 40, 40), RGB(40, 255, 40), RGB(60, 120, 255) }
local cursor_markers = false
local cursor_watch = false

local function delete_markers(list)
	for _, obj in ipairs(list or empty_table) do
		if IsValid(obj) then DoneObject(obj) end
	end
end

local function marker_hexes(hub, body)
	local hexes = {}
	for idx = hub.first_connector_idx, hub.last_connector_idx do
		for extra = 0, 3 do
			local q, r = line_hex(hub, body, idx, extra)
			hexes[#hexes + 1] = { q = q, r = r, line = (idx + 1) // 2, first_outside = extra == 1 }
		end
	end
	return hexes
end

local function place_tile(map, hex)
	local x, y = HexToWorld(hex.q, hex.r)
	local tile = PlaceObjectIn("GridTile", map)
	tile:SetPos(x, y, GetMaxHeightInHex(map, x, y) + 31)
	tile:SetColorModifier(line_colour[hex.line] or line_colour[1])
	DeleteOnLoadGame(tile)
	return tile
end

local function place_hub_markers(hub)
	delete_markers(hub_markers[hub])
	if uses_body_spots(hub) then hub_markers[hub] = nil return end
	local map = ResolveMap(hub)
	local list = {}
	for _, hex in ipairs(marker_hexes(hub, hub)) do
		list[#list + 1] = place_tile(map, hex)
		if hex.first_outside then
			local ok, arrow = pcall(PlaceObjectIn, "ArrowTutorial", map)
			if ok and IsValid(arrow) then
				local x, y = HexToWorld(hex.q, hex.r)
				arrow:SetPos(x, y, GetMaxHeightInHex(map, x, y) + 12 * guim)
				arrow:SetColorModifier(line_colour[hex.line] or line_colour[1])
				DeleteOnLoadGame(arrow)
				list[#list + 1] = arrow
			end
		end
	end
	hub_markers[hub] = list
end

local vanilla_update_obstructors = ConstructionController.UpdateConstructionObstructors
function ConstructionController:UpdateConstructionObstructors(...)
	local cursor = self.cursor_obj
	local template = self.template_obj
	if IsValid(cursor) and IsKindOf(template, "SMROptInTrainHubBase") then
		local map = self:GetMap()
		cursor_markers = cursor_markers or {}
		for i, hex in ipairs(marker_hexes(template, cursor)) do
			local tile = cursor_markers[i]
			if not IsValid(tile) then
				cursor_markers[i] = place_tile(map, hex)
			else
				local x, y = HexToWorld(hex.q, hex.r)
				tile:SetPos(x, y, GetMaxHeightInHex(map, x, y) + 31)
			end
		end
		if not IsValidThread(cursor_watch) then
			-- real-time and unsaved; it only ever deletes this file's own tiles
			cursor_watch = CreateRealTimeThread(function()
				while IsValid(cursor) do Sleep(200) end
				delete_markers(cursor_markers)
				cursor_markers = false
			end)
		end
	end
	return vanilla_update_obstructors(self, ...)
end

-- ===========================================================================
-- City labels. A template whose object_class is not "Station" never joins the
-- "Station" label (Building.lua:435-447 adds class and object_class only), and
-- vanilla walks that label to free a train's platform (Train.lua:94, :134), to
-- broadcast a resource toggle (Station.lua:1023), to link nearby buildings
-- (Building.lua:3793) and to route passengers (Colonist.lua:3188, :3289).
-- The prototype hub was missing from it, which is why slot 1 did not list it.
-- AddToCityLabels is a combined method (CityObject.lua:8), so this adds.
-- ===========================================================================

function SMROptInTrainHubBase:AddToCityLabels()
	self.city:AddToLabel("Station", self)
end

function SMROptInTrainHubBase:RemoveFromCityLabels()
	self.city:RemoveFromLabel("Station", self)
end

-- ===========================================================================
-- Built-in drone controller. Precedent: ElevatorBase is a Building with
-- DroneControl (Elevator.lua:561-590); DroneHubBase is a TaskRequester with it
-- (DroneHub.lua:1-2). Init, GameInit, Done, BuildingUpdate, OnSetWorking,
-- OnDestroyed and the label methods are all combined (Building.lua:1-12,
-- CityObject.lua:8-9), so both parents' bodies run and none is overridden here.
-- ===========================================================================

function SMROptInTrainHubBase:Init()
	self.charging_stations = {}
end

-- Station's is the workplace radius (Station.lua:344); DroneNode's is the drone
-- radius (DroneControl.lua:82). The drone radius is what a player needs to see.
function SMROptInTrainHubBase:GetSelectionRadiusScale()
	return self.work_radius
end

-- A vanilla hub stops commanding when it malfunctions (DroneHub.lua:150-153).
-- This one must not: its drones exist to repair it, and it may stand far from
-- any other controller. Turned off by the player still means no new work.
function SMROptInTrainHubBase:CanCommandDrones()
	return self.can_control_drones and self.ui_working and not self.destroyed and true or false
end

function SMROptInTrainHubBase:GetDronesStatusText()
	if not self:CanCommandDrones() then
		return T(647, "<red>Not working. Drones won't receive further instructions.</red>")
	end
	return DroneControl.GetDronesStatusText(self)
end

function SMROptInTrainHubBase:GetUISectionDroneHubRollover()
	return table.concat({
		T{293, "Low Battery<right><drone(DischargedDronesCount)>", self},
		T{294, "Broken<right><drone(BrokenDronesCount)>", self},
		T{295, "Idle<right><drone(IdleDronesCount)>", self},
	}, "<newline><left>")
end

function SMROptInTrainHubBase:ShouldShowAvailableDronePrefabInfo()
	return true
end

-- DroneControl:SpawnDrone is an empty "override me" (DroneControl.lua:725).
-- Drones appear around the body the way DroneControl:SpawnDronesAround places
-- them (:244-255), because the stand-in has no drone entrance to walk out of.
function SMROptInTrainHubBase:SpawnDrone()
	if #self.drones >= self:GetMaxDrones() then return false end
	local drone = self.city:CreateDrone()
	drone:SetCommandCenter(self)
	local map = self:GetMap()
	local centre = self:GetPos()
	local inner = longest_line(self) * const.GridSpacing
	local outer = self.work_radius * const.GridSpacing
	local pos = GetRandomPassableAroundOnMap(map, centre, outer, inner)
		or GetRandomPassableAroundOnMap(map, centre, outer)
		or centre
	drone:SetPos(pos)
	return true
end

function SMROptInTrainHubBase:CheatSpawnDrone()
	self:SpawnDrone()
end

-- The charging point. A body with RechargeStationPlatform auto-attaches gets
-- vanilla's chargers on them, exactly as a drone hub does
-- (AttachedRechargeStations.lua:2-29). A body without one gets a platform on the
-- q=1,r=1 footprint hex between two arms. Unlike build 2's first-outside hex,
-- the building footprint now protects the pad from construction overlap.
local function charger_offset(self)
	local x0, y0 = HexToWorld(0, 0)
	local x, y = HexToWorld(1, 1)
	return point(x - x0, y - y0, 0)
end

-- A visual-only reactor: the hub remains the sole grid object and producer.
-- Use the engine's existing shapeshifter class rather than introducing another
-- persisted class name. DeleteOnLoadGame removes the helper after save load and
-- heal_after_load recreates it. Seven vanilla outline hexes scaled by sqrt(4/7)
-- gives 75.6%, so 75% targets the owner's three-to-five-hex look.
local reactor_entity = "FusionReactor"
local reactor_scale = 75
local reactor_offset = point(3897, 2250, 0) -- 45 m out, local angle 30 degrees

local function is_hub_reactor(obj)
	return IsValid(obj) and IsKindOf(obj, "ShapeshifterAutoAttach")
		and obj:GetEntity() == reactor_entity
end

local function set_hub_reactor_working(self, working)
	for _, visual in ipairs(self:GetAttaches("ShapeshifterAutoAttach") or empty_table) do
		if is_hub_reactor(visual) then
			local state = working and "working" or "idle"
			if visual:HasState(state) then visual:SetState(state) end
			PlayFX("Working", working and "start" or "end", visual)
		end
	end
end

function SMROptInTrainHubBase:InitHubReactorVisual()
	for _, visual in ipairs(self:GetAttaches("ShapeshifterAutoAttach") or empty_table) do
		if is_hub_reactor(visual) then DoneObject(visual) end
	end
	if not IsValidEntity(reactor_entity) then return end
	local visual = PlaceObjectIn("ShapeshifterAutoAttach", self:GetMap())
	visual:ChangeEntity(reactor_entity)
	visual.fx_actor_class = reactor_entity
	visual:ClearEnumFlags(const.efCollision + const.efApplyToGrids + const.efWalkable + const.efSelectable)
	self:Attach(visual, self:GetSpotBeginIndex("Origin"))
	visual:SetAttachOffset(reactor_offset)
	visual:SetAttachAngle(210 * 60) -- face the hub centre
	visual:SetScale(reactor_scale)
	DeleteOnLoadGame(visual)
	set_hub_reactor_working(self, self.working)
end

-- A train station is normally only an ElectricityConsumer. This hub is both a
-- 70-power producer and a 10-power consumer on one grid element, so its stated
-- output covers itself plus six 10-power large stations. SupplyGridElement and
-- SupplyGridFragment natively support an element appearing in both lists
-- (SupplyGrid.lua:12-34, :537-553; build 1.1.0.403908).
function SMROptInTrainHubBase:CreateElectricityElement()
	self.electricity = SupplyGridElement:new({
		building = self,
		production = 0,
		throttled_production = 0,
		consumption = 0,
	})
	self.electricity:SetProduction(self.working and self:GetPerformanceModifiedElectricityProduction() or 0)
	self.electricity:SetConsumption(self.electricity_consumption)
end

function SMROptInTrainHubBase:InitHubChargers()
	for _, station in ipairs(self.charging_stations or empty_table) do
		if IsValid(station) then DoneObject(station) end
	end
	self.charging_stations = {}
	if #(self:GetAttaches("RechargeStationPlatform") or empty_table) == 0 then
		local platform = PlaceObjectIn("RechargeStationPlatform", self:GetMap())
		self:Attach(platform, self:GetSpotBeginIndex("Origin"))
		platform:SetAttachOffset(charger_offset(self))
	end
	AttachedRechargeStations.Init(self)
	AttachedRechargeStations.SetWorking(self.charging_stations, self.working)
end

function SMROptInTrainHubBase:GameInit()
	-- Runs after Station's and DroneControl's bodies, and before the Notify'd
	-- SpawnDrones and ConnectTaskRequesters (DroneControl.lua:230-236,
	-- TaskRequest.lua:260-266), which need the radius.
	self.work_radius = 10
	self.UIWorkRadius = self.work_radius
	self:InitHubChargers()
	self:InitHubReactorVisual()
	self:GatherOrphanedDrones()
	place_hub_markers(self)
	Floor.Reconcile(self)
end

function SMROptInTrainHubBase:OnSetWorking(working)
	if working then
		self:GatherOrphanedDrones()
		self:SetWaitingDronesIdle()
	end
	self:NotifyWorkingChanged(self.connected_task_requesters)
	-- like a drone hub: no power, no charging (DroneHub.lua:85-94)
	AttachedRechargeStations.SetWorking(self.charging_stations, working)
	set_hub_reactor_working(self, working)
end

-- Done is combined. TrackConnectedObjBase's body removes connectors 0..4
-- (TrainTransport.lua:14-37); this one removes the rest, then the chargers.
function SMROptInTrainHubBase:Done(done_map)
	delete_markers(hub_markers[self])
	hub_markers[self] = nil
	if done_map then return end
	for _, station in ipairs(self.charging_stations or empty_table) do
		if IsValid(station) then DoneObject(station) end
	end
	local map = ResolveMap(self)
	for i = 5, self.last_connector_idx do
		local q, r = self:GetSpotPosHex(self:GetSpotBeginIndex("Trackconnector" .. i))
		local el = HexGetTrackGridElement(map.object_hex_grid, q, r)
		if IsValid(el) then
			local track = el.track_obj
			if #track.elements == 2 and track.elements[1].station and track.elements[2].station then
				CreateGameTimeThread(DoneObject, track)
			else
				track:DisconnectStations()
				DoneObject(el)
				if #track.elements_under_construction == 0 then
					ProcessTrackElements(map, track.elements)
				end
			end
		end
	end
end

-- ===========================================================================
-- Maintenance reserve. Vanilla already pays a station's own maintenance from
-- its own stock: Station:SelfService moves the maintenance resource from the
-- supply request to the maintenance request every BuildingUpdate
-- (Station.lua:493-511). What it lacks is a guarantee that the stock is there,
-- and a drone for the repair work that follows (a train "can't do repair
-- work", RequiresMaintenance.lua StartWorkPhase). The reserve is the first and
-- the built-in controller is the second.
-- ===========================================================================

function SMROptInTrainHubBase:GetTrainExportFloor(res)
	if res ~= self.maintenance_resource_type or not self:DoesMaintenanceRequireResources() then return 0, true end
	return self.maintenance_resource_amount * self.hub_reserve_maintenances, true
end

-- Vanilla calls this after every stock change (MultiResourceCubeVisuals.lua
-- :434, :454, :466): a train unloading, a drone delivering, a drone loading.
function SMROptInTrainHubBase:OnAfterRequestUpdate()
	MultiResourceDepotBase.OnAfterRequestUpdate(self)
	Floor.Reconcile(self)
end

-- BuildingUpdate is combined; Station's body has already run SelfService, which
-- reads the supply target and so cannot see the reserve. While maintenance is
-- asking for its resource, hand the reserve back, let vanilla's SelfService pay
-- from it, and take the hold again. No yield in between.
function SMROptInTrainHubBase:BuildingUpdate()
	if self.maintenance_phase == "demand" then
		Floor.ReleaseAll(self)
		self:SelfService()
	end
	Floor.Reconcile(self)
end

-- ===========================================================================
-- Cargo on show. Vanilla draws a station's stock as cube stacks on its attached
-- `StorageDepotFood` sub-models, from each one's `Box1` spot, and derives the
-- stack height from max_storage_per_resource (Station.lua:1214-1262,
-- MultiResourceDepot.lua:119-141). The stand-in has those sub-models, so it
-- needs nothing. The owner's asset models empty pallet beds with a `Box1` spot
-- on each and no sub-models; then the pallets are the body's own spots.
-- ===========================================================================

local function own_pallets(self)
	if #(self:GetAttaches("StorageDepotFood") or empty_table) > 0 then return 0 end
	if not CObject.HasSpot(self, "Box1") then return 0 end
	local first, last = self:GetSpotRange("Box1")
	if not first or first < 0 then return 0 end
	return last - first + 1, first
end

function SMROptInTrainHubBase:GetTotalStorageColumns()
	local pallets = own_pallets(self)
	if pallets == 0 then return Station.GetTotalStorageColumns(self) end
	return pallets * self.max_x * self.max_y
end

function SMROptInTrainHubBase:GetCubePosRelative(idx, placement_offset, resource)
	local pallets, first = own_pallets(self)
	if pallets == 0 then return Station.GetCubePosRelative(self, idx, placement_offset, resource) end
	if not resource then return nil end
	local col_start = self.visual_col_start[resource]
	local cap_cols = self.capacity_columns[resource] or 0
	if not col_start or cap_cols == 0 then return nil end
	local mxmy = self.max_x * self.max_y
	local col_within = idx % cap_cols
	local z = idx / cap_cols
	if z >= self.max_z then return nil end
	local global_col = col_start + col_within
	if global_col >= pallets * mxmy then return nil end
	local local_col = global_col % mxmy
	local x, y
	if self.switch_fill_order then
		y = local_col % self.max_y
		x = local_col / self.max_y
	else
		x = local_col % self.max_x
		y = local_col / self.max_x
	end
	local spot = first + global_col / mxmy
	local spot_pos, spot_angle = CObject.GetSpotLoc(self, spot)
	-- each bed's grid follows that bed's own spot, so beds may face any way
	local in_bed = Rotate(point(x * (self.box_diam + self.spacing_x), y * (self.box_diam + self.spacing_y), 0),
		(spot_angle or 0) - self:GetAngle())
	return Rotate(spot_pos - self:GetPos(), -self:GetAngle()) + in_bed + point(0, 0, z * (self.box_height + self.spacing_z))
end

-- ===========================================================================
-- Load. Markers are unsaved. Chargers are rebuilt only if the save lost them.
-- ===========================================================================

local function heal_after_load(hub)
	-- The first build wrote radius 8. Upgrade that legacy value to the owner's
	-- new minimum, preserve later slider choices, and keep the non-saving UI
	-- mirror aligned with the vanilla persisted `work_radius` property.
	local radius = type(hub.work_radius) == "number" and hub.work_radius or 10
	radius = Clamp(radius, hub.service_area_min, hub.service_area_max)
	hub.UIWorkRadius = radius
	hub:SetWorkRadius(radius)
	place_hub_markers(hub)
	local charger = hub.charging_stations and hub.charging_stations[1]
	if not (IsValid(charger) and IsValid(charger.platform)) then
		hub:InitHubChargers()
	end
	hub:InitHubReactorVisual()
	Floor.Reconcile(hub)
end

function OnMsg.LoadGame()
	-- XTemplates is populated after the earlier class-processing callbacks in
	-- this build. Register at the first lifecycle point that can open a panel.
	ensure_hub_infopanel()
	AllMapsForEach("map", "SMROptInTrainHubBase", heal_after_load)
end

function OnMsg.CityStart()
	ensure_hub_infopanel()
end

-- ===========================================================================
-- The sizes. Thin by design: a size is a connector table and a count.
-- ===========================================================================

DefineClass.SMROptInTrainHub6Base = {
	__parents = { "SMROptInTrainHubBase" },
	last_connector_idx = 6,
	hub_connector_directions = { 0, 3, 1, 4, 2, 5 }, -- three lines, 60° apart
}

-- The BuildingTemplate companion is Mod-Editor generated. Its Data/ source is
-- authoritative and now names the imported entity; this postprocess keeps the
-- dev build runnable until the next editor save regenerates the companion.
function OnMsg.ClassesPostprocess()
	ensure_hub_infopanel()
	local class = g_Classes and g_Classes.SMROptInTrainHub6
	if class then
		class.entity = "SMROptInTrainHub6"
		class.construction_cost_Concrete = 60000
		class.construction_cost_Metals = 40000
		class.construction_cost_MachineParts = 10000
		class.construction_cost_Electronics = 15000
		class.maintenance_resource_type = "Electronics"
		class.maintenance_resource_amount = 2000
		class.electricity_consumption = 10000
		class.electricity_production = 70000
		class.description = T(909018002004, "A <em>Station</em> where three straight lines cross, so cargo can change routes. It powers itself and six large stations, has its own small <em>Drone</em> crew, and keeps back enough Electronics to maintain itself.")
	end
	local template = BuildingTemplates and BuildingTemplates.SMROptInTrainHub6
	if template then
		template.entity = "SMROptInTrainHub6"
		template.construction_cost_Concrete = 60000
		template.construction_cost_Metals = 40000
		template.construction_cost_MachineParts = 10000
		template.construction_cost_Electronics = 15000
		template.maintenance_resource_type = "Electronics"
		template.maintenance_resource_amount = 2000
		template.electricity_consumption = 10000
		template.electricity_production = 70000
		template.description = T(909018002004, "A <em>Station</em> where three straight lines cross, so cargo can change routes. It powers itself and six large stations, has its own small <em>Drone</em> crew, and keeps back enough Electronics to maintain itself.")
	end
end

-- RESERVED, NOT BUILT (owner, OI-15): the four-connector hub, two lines crossing
-- at 60°. When it is built it is exactly this, plus its own template
-- `SMROptInTrainHub4` and its own sitting:
--   DefineClass.SMROptInTrainHub4Base = {
--       __parents = { "SMROptInTrainHubBase" },
--       last_connector_idx = 4,
--       hub_connector_directions = { 0, 3, 1, 4 },
--   }

print("[TrainHubDev] hub classes loaded: six-connector hub, built-in drone controller, maintenance reserve")
