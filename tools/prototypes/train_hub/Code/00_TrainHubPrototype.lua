-- Disposable-save, code-only train-hub prototype for game 1.1.0.403908.
-- This separate dev mod is excluded from the shipping Opt-In Modules package.

DefineClass.SMRTrainHubPrototypeBase = {
	__parents = { "Station" },
	first_connector_idx = 1,
	last_connector_idx = 6,
}

local synthetic_base = 900000
local kind_code = {
	Trackconnector = 1,
	Trackdirection = 2,
	Ramparrive = 3,
	Stop = 4,
	Spawn = 5,
	Rampdepart = 6,
	Sign = 7,
}
local code_kind = {
	[1] = "Trackconnector",
	[2] = "Trackdirection",
	[3] = "Ramparrive",
	[4] = "Stop",
	[5] = "Spawn",
	[6] = "Rampdepart",
	[7] = "Sign",
}
-- Pair order is load-bearing: (1,2), (3,4), (5,6) are opposite ends of
-- three straight lines. The whole star rotates with the building.
local connector_direction = { 0, 3, 1, 4, 2, 5 }

local function parse_synthetic_name(name)
	if type(name) ~= "string" then return end
	local kind, number = name:match("^([%a]+)(%d+)$")
	local idx = tonumber(number)
	local code = kind_code[kind]
	if code and idx and idx >= 1 and idx <= 6 then
		return synthetic_base + code * 10 + idx
	end
end

local function decode_synthetic_spot(spot)
	if type(spot) ~= "number" then return end
	local value = spot - synthetic_base
	local code = value // 10
	local idx = value % 10
	local kind = code_kind[code]
	if kind and idx >= 1 and idx <= 6 then return kind, idx end
end

-- Round 2 marker objects per hub; module-local, so no field reaches a save.
local hub_markers = setmetatable({}, weak_keys_meta)

local function delete_markers(list)
	for _, obj in ipairs(list or empty_table) do
		if IsValid(obj) then DoneObject(obj) end
	end
end

local function opposite(idx)
	return idx % 2 == 1 and idx + 1 or idx - 1
end

-- Round 2: every connector sits on the last hex of the body's own footprint
-- along its line, and its direction hex is the first hex outside. Vanilla finds
-- a station from a connector hex through the object hex grid
-- (Tracks.lua:19-24 on 1.1.0.403908), so a connector outside the footprint
-- could never attach a track. Radii are per local direction 0..5.
local line_radius_cache = {}
local function line_radii(entity)
	local radii = line_radius_cache[entity]
	if radii then return radii end
	local inside = {}
	for _, pt in ipairs(GetEntityOutlineShape(entity) or empty_table) do
		local q, r = pt:xy()
		inside[q * 1000 + r] = true
	end
	radii = {}
	for direction = 0, 5 do
		local dq, dr = HexRotate(1, 0, direction)
		local radius = 0
		while radius < 30 and inside[dq * (radius + 1) * 1000 + dr * (radius + 1)] do
			radius = radius + 1
		end
		-- 0 means the footprint has no hex on this line next to the origin. Keep
		-- the six connector hexes distinct; slot 2 then reads in_footprint < 6.
		radii[direction] = Max(radius, 1)
	end
	line_radius_cache[entity] = radii
	print(string.format("[TrainHubPrototype] %s line radii d0..d5 = %d %d %d %d %d %d",
		tostring(entity), radii[0], radii[1], radii[2], radii[3], radii[4], radii[5]))
	return radii
end

-- Sevenths of the way from the centre to the connector; nil is a whole hex.
local kind_sevenths = { Ramparrive = 5, Rampdepart = 5, Stop = 3, Spawn = 3 }

local function line_hex(self, direction_idx, extra)
	local local_direction = connector_direction[direction_idx]
	local radius = line_radii(self:GetEntity())[local_direction] + (extra or 0)
	local building_direction = HexAngleToDirection(self:GetAngle())
	local q, r = WorldToHex(self:GetPos())
	local lq, lr = HexRotate(radius, 0, local_direction)
	local dq, dr = HexRotate(lq, lr, building_direction)
	return q + dq, r + dr, (local_direction + building_direction) % 6
end

local function synthetic_spot_pos(self, kind, idx)
	local sevenths = kind_sevenths[kind]
	local direction_idx = kind == "Spawn" and opposite(idx) or idx
	local q, r, direction = line_hex(self, direction_idx, kind == "Trackdirection" and 1 or 0)
	local x, y = HexToWorld(q, r)
	local cx, cy, z = self:GetPosXYZ()
	if sevenths then
		x = cx + MulDivRound(x - cx, sevenths, 7)
		y = cy + MulDivRound(y - cy, sevenths, 7)
	end
	return point(x, y, z), direction
end

local function synthetic_spot_hex(self, kind, idx)
	local pos, direction = synthetic_spot_pos(self, kind, idx)
	local q, r = WorldToHex(pos)
	return q, r, direction
end

local function synthetic_spot_angle(self, kind, idx)
	local pos = synthetic_spot_pos(self, kind, idx)
	if not pos then return 0 end
	local center = self:GetPos()
	if kind == "Stop" or kind == "Ramparrive" then
		return CalcOrientation(pos, center)
	end
	return CalcOrientation(center, pos)
end

function SMRTrainHubPrototypeBase:GetSpotBeginIndex(state, type_id)
	local name = type_id == nil and state or type_id
	local synthetic = parse_synthetic_name(name)
	if synthetic then return synthetic end
	if type_id == nil then return CObject.GetSpotBeginIndex(self, state) end
	return CObject.GetSpotBeginIndex(self, state, type_id)
end

-- PlaceUnderconstructionSigns (UnderconstructionSign.lua:41-56) attaches a
-- sign to every "Sign<i>" spot the body has. The vanilla body's four point
-- along its platforms, the wrong way for this hub, and a computed spot is not
-- an attach point. Report none; GetSign then finds no sign to show or hide.
function SMRTrainHubPrototypeBase:HasSpot(name, ...)
	if type(name) == "string" and name:match("^Sign%d+$") then return false end
	return CObject.HasSpot(self, name, ...)
end

function SMRTrainHubPrototypeBase:GetSpotPos(spot)
	local kind, idx = decode_synthetic_spot(spot)
	if kind then return synthetic_spot_pos(self, kind, idx) end
	return CObject.GetSpotPos(self, spot)
end

function SMRTrainHubPrototypeBase:GetSpotLoc(spot)
	local kind, idx = decode_synthetic_spot(spot)
	if kind then
		return synthetic_spot_pos(self, kind, idx), synthetic_spot_angle(self, kind, idx), axis_z, 100
	end
	return CObject.GetSpotLoc(self, spot)
end

function SMRTrainHubPrototypeBase:GetSpotPosHex(spot)
	local kind, idx = decode_synthetic_spot(spot)
	if kind then return synthetic_spot_hex(self, kind, idx) end
	return CObject.GetSpotPosHex(self, spot)
end

function SMRTrainHubPrototypeBase:GetSpotAxisAngle(spot)
	local kind, idx = decode_synthetic_spot(spot)
	if kind then return axis_z, synthetic_spot_angle(self, kind, idx) end
	return CObject.GetSpotAxisAngle(self, spot)
end

-- Vanilla creates only indices 0..4. The same body with the class bounds is
-- the only connector-count change; every spot read remains virtual.
function SMRTrainHubPrototypeBase:CreateConnectorElements(force)
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

-- Done is a combined method. Vanilla's TrackConnectedObjBase body removes
-- 0..4; this body removes only the two extra connector elements.
function SMRTrainHubPrototypeBase:Done(done_map)
	delete_markers(hub_markers[self])
	hub_markers[self] = nil
	if done_map then return end
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

-- Vanilla searches only indices 0..4. This makes the two extra connector and
-- direction hexes visible to every caller, including Tracks.lua and Station.
function SMRTrainHubPrototypeBase:GetTrackConnectionSpot(q, r, spot_name)
	for i = self.first_connector_idx, self.last_connector_idx do
		local spot = self:GetSpotBeginIndex((spot_name or "Trackconnector") .. i)
		if spot >= 0 then
			local qq, rr = self:GetSpotPosHex(spot)
			if q == qq and r == rr then return i end
		end
	end
	return false
end

-- Round 2, defect 1. Vanilla Station:CanBuildOver (Station.lua:615-660 on
-- 1.1.0.403908) reads the connector spots from the construction cursor, which
-- is a CursorBuilding without this class's virtual spots. Same body, with the
-- hexes computed from the cursor's position and angle.
function SMRTrainHubPrototypeBase:CanBuildOver(obstructors, cursor_obj)
	local spots = {}
	local this = cursor_obj or self
	local map = ResolveMap(this)
	for i = self.first_connector_idx, self.last_connector_idx do
		local q, r = line_hex(this, i)
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

-- Round 2, defect 1's sibling. GridConstructionController:Activate
-- (GridConstruction.lua:287-295) moves a track's start from a station's
-- connector element to its direction hex, but searches indices 0..4 only.
-- Do the same move for every hub connector before vanilla looks.
local vanilla_grid_activate = GridConstructionController.Activate
function GridConstructionController:Activate(pt, ...)
	if self.mode == "track_grid" and not self.starting_point and pt then
		local q, r = WorldToHex(pt)
		local el = HexGetTrackGridElement(self:GetMap().object_hex_grid, q, r)
		local hub = el and el.station
		if IsValid(hub) and IsKindOf(hub, "SMRTrainHubPrototypeBase") then
			local idx = hub:GetTrackConnectionSpot(q, r)
			if idx then
				local dq, dr = hub:GetConnectorElementDirection(idx)
				pt = point(HexToWorld(dq, dr))
			end
		end
	end
	return vanilla_grid_activate(self, pt, ...)
end

-- Round 2, defect 2: prototype-only markers. Each line has one colour at both
-- of its ends: line A (1,2) red, line B (3,4) green, line C (5,6) blue. A
-- marked end is the connector hex plus the three hexes a track leaves over,
-- with an arrow above the first of them. Nothing here is saved.
local line_colour = { RGB(255, 40, 40), RGB(40, 255, 40), RGB(60, 120, 255) }
local cursor_markers = false
local cursor_watch = false

local function marker_hexes(obj)
	local hexes = {}
	for idx = 1, 6 do
		for extra = 0, 3 do
			local q, r = line_hex(obj, idx, extra)
			hexes[#hexes + 1] = { q = q, r = r, line = (idx + 1) // 2, first_outside = extra == 1 }
		end
	end
	return hexes
end

local function place_tile(map, hex)
	local x, y = HexToWorld(hex.q, hex.r)
	local tile = PlaceObjectIn("GridTile", map)
	tile:SetPos(x, y, GetMaxHeightInHex(map, x, y) + 31)
	tile:SetColorModifier(line_colour[hex.line])
	DeleteOnLoadGame(tile)
	return tile
end

local function place_hub_markers(hub)
	delete_markers(hub_markers[hub])
	local map = ResolveMap(hub)
	local list = {}
	for _, hex in ipairs(marker_hexes(hub)) do
		list[#list + 1] = place_tile(map, hex)
		if hex.first_outside then
			local ok, arrow = pcall(PlaceObjectIn, "ArrowTutorial", map)
			if ok and IsValid(arrow) then
				local x, y = HexToWorld(hex.q, hex.r)
				arrow:SetPos(x, y, GetMaxHeightInHex(map, x, y) + 12 * guim)
				arrow:SetColorModifier(line_colour[hex.line])
				DeleteOnLoadGame(arrow)
				list[#list + 1] = arrow
			end
		end
	end
	hub_markers[hub] = list
end

-- GameInit is a recursive call, so this runs after Station's own body.
function SMRTrainHubPrototypeBase:GameInit()
	place_hub_markers(self)
end

function OnMsg.LoadGame()
	AllMapsForEach("map", "SMRTrainHubPrototypeBase", place_hub_markers)
end

-- The same tiles follow the construction cursor, so the three lines are
-- visible before the hub is placed.
local vanilla_update_obstructors = ConstructionController.UpdateConstructionObstructors
function ConstructionController:UpdateConstructionObstructors(...)
	local cursor = self.cursor_obj
	if IsValid(cursor) and IsKindOf(self.template_obj, "SMRTrainHubPrototypeBase") then
		local map = self:GetMap()
		local hexes = marker_hexes(cursor)
		cursor_markers = cursor_markers or {}
		for i, hex in ipairs(hexes) do
			local tile = cursor_markers[i]
			if not IsValid(tile) then
				cursor_markers[i] = place_tile(map, hex)
			else
				local x, y = HexToWorld(hex.q, hex.r)
				tile:SetPos(x, y, GetMaxHeightInHex(map, x, y) + 31)
			end
		end
		if not IsValidThread(cursor_watch) then
			cursor_watch = CreateRealTimeThread(function()
				while IsValid(cursor) do Sleep(200) end
				delete_markers(cursor_markers)
				cursor_markers = false
			end)
		end
	end
	return vanilla_update_obstructors(self, ...)
end

print("[TrainHubPrototype] round 2 loaded: six footprint-edge connectors, line markers; disposable saves only")
