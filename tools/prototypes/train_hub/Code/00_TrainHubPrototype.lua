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
}
local code_kind = {
	[1] = "Trackconnector",
	[2] = "Trackdirection",
	[3] = "Ramparrive",
	[4] = "Stop",
	[5] = "Spawn",
	[6] = "Rampdepart",
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

local function opposite(idx)
	return idx % 2 == 1 and idx + 1 or idx - 1
end

local function spot_radius_and_index(kind, idx)
	if kind == "Trackconnector" then return 7, idx end
	if kind == "Trackdirection" then return 8, idx end
	if kind == "Ramparrive" or kind == "Rampdepart" then return 5, idx end
	if kind == "Stop" then return 3, idx end
	if kind == "Spawn" then return 3, opposite(idx) end
end

local function synthetic_spot_hex(self, kind, idx)
	local radius, direction_idx = spot_radius_and_index(kind, idx)
	if not radius then return end
	local q, r = WorldToHex(self:GetPos())
	local building_direction = HexAngleToDirection(self:GetAngle())
	local direction = (connector_direction[direction_idx] + building_direction) % 6
	local dq, dr = HexRotate(radius, 0, direction)
	return q + dq, r + dr, direction
end

local function synthetic_spot_pos(self, kind, idx)
	local q, r, direction = synthetic_spot_hex(self, kind, idx)
	if not q then return end
	local x, y = HexToWorld(q, r)
	local _, _, z = self:GetPosXYZ()
	return point(x, y, z), direction
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

print("[TrainHubPrototype] loaded six computed connectors; disposable saves only")
