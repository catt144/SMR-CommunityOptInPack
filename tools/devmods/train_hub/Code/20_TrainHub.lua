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

-- Load order is not guaranteed (the Mod Editor reorders code items on save), so
-- both files create the shared table if it is not there yet.
SMROptInTrainFloor = rawget(_G, "SMROptInTrainFloor") or {}
local Floor = SMROptInTrainFloor
-- Owner 2026-09-20, TRAIN_HUB_MOVE_high.md: tune both by eye, measured
-- outward from the hub centre. Neither is derived from the disputed length.
-- Pause is a provisional starting point; park starts at the owner's lane-era
-- 13 m and needs judging again on the centre. Both reset on a full restart.
Floor.HubTransitionPauseDistance = 30 * guim
Floor.HubParkDistance = 13 * guim
local hub_work_radius = 15
local hub_drone_battery_max = 100 * const.DroneBatteryMax

DefineClass.SMROptInTrainHubBase = {
	__parents = { "Station", "DroneControl", "ElectricityProducer" },
	flags = { cfConstructible = true, efWalkable = true },

	-- Geometry. `hub_connector_directions[i]` is connector i's local hex
	-- direction 0..5. Pair order is load-bearing: (1,2), (3,4), (5,6) are the
	-- opposite ends of straight lines, and the whole star turns with the body.
	first_connector_idx = 1,
	last_connector_idx = 0,
	hub_connector_directions = false,
	SMROptIn_hub_crossing = false, -- Train reference; save contract, FIX_POLICY inventory

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
	show_service_area = false,
	show_range = true,
	service_area_min = hub_work_radius,
	service_area_max = hub_work_radius,
	work_radius = hub_work_radius,
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

-- Trains run on the deck, never on the ground. Vanilla's station model has a ramp that takes an
-- arriving train down to its Stop spot; this hub has no ramp, so a Stop spot at ground level made
-- every train drop through the beam onto the floor (owner, build 3 smoke, 2026-09-19). These four
-- kinds are lifted to the deck height, read from the model's own connector spot.
local deck_kinds = { Ramparrive = true, Stop = true, Spawn = true, Rampdepart = true }
local train_deck_height

-- Ask the connected track for its step. Enter1 is NOT always the arrival lane.
-- SOURCE: 1.1.0.403908, Train.lua:650-665, Station.lua:1200-1205.
local function lane_offset(self, idx, arrival)
	local el = self:GetConnectorElement(idx)
	local track = IsValid(el) and el.track_obj
	if IsValid(track) then
		local is_start = track:GetStartStation() == self
		local step = (arrival and not is_start or not arrival and is_start) and 1 or -1
		local spot = el:GetSpotBeginIndex(step == 1 and "Enter1" or "Enter2")
		if spot and spot >= 0 then
			local p, c = el:GetSpotPos(spot), el:GetPos()
			return p:x() - c:x(), p:y() - c:y()
		end
	end
	-- An unconnected construction cursor has no track. Measured R-LANESIDE:
	-- arrival is +289 along the outward vector's left normal, departure -289.
	local q, r = line_hex(self, self, idx)
	local x, y = HexToWorld(q, r)
	local cx, cy = self:GetPosXYZ()
	local length = self:GetDist2D(point(x, y))
	local side = arrival and 289 or -289
	return MulDivRound(cy - y, side, length), MulDivRound(x - cx, side, length)
end

local function synthetic_spot_pos(self, kind, idx)
	local q, r, direction = line_hex(self, self, idx, kind == "Trackdirection" and 1 or 0)
	local x, y = HexToWorld(q, r)
	local cx, cy, z = self:GetPosXYZ()
	if deck_kinds[kind] then z = z + train_deck_height(self) end
	if deck_kinds[kind] then
		local distance = (kind == "Stop" or kind == "Spawn")
			and Floor.HubParkDistance or Floor.HubTransitionPauseDistance
		local radius = self:GetDist2D(point(x, y))
		x = cx + MulDivRound(x - cx, distance, radius)
		y = cy + MulDivRound(y - cy, distance, radius)
	end
	if kind == "Ramparrive" or kind == "Rampdepart" then
		-- Only the transition's outer end is on vanilla's lane. Stop/Spawn
		-- and every interior waypoint are on our rail's centreline.
		local ox, oy = lane_offset(self, idx, kind ~= "Rampdepart")
		x, y = x + ox, y + oy
	end
	return point(x, y, z), direction
end

local function synthetic_spot_angle(self, kind, idx)
	local q, r = line_hex(self, self, idx)
	local pos = point(HexToWorld(q, r))
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

-- Height of the deck above the hub's origin: the body's own Trackconnector1 spot when it carries
-- one (the asset puts every connector on the beam top), else 8 m, which is the vanilla track's.
train_deck_height = function(self)
	if uses_body_spots(self) then
		local spot = CObject.GetSpotBeginIndex(self, "Trackconnector1")
		if spot and spot >= 0 then
			local _, _, base_z = self:GetPosXYZ()
			return CObject.GetSpotPos(self, spot):z() - base_z
		end
	end
	return 8 * guim
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

-- ===========================================================================
-- Hub-local traffic. Reconstruction of Station.lua:1085-1211 and
-- TrainTransport.lua:39-51 (1.1.0.403908 archived tree), because vanilla's
-- opposite-platform reservations and single hidden slide cannot express this
-- open crossing. No Train method is replaced. track_busy keeps its vanilla
-- table type, but positive keys are this hub's OWN connector indices.
--
-- Save discipline: content residual under FIX_POLICY section 0. Layers 3/2
-- cannot insert waypoints and timed turns into GotoSpot's one blocking slide.
-- These bounded command frames and SMROptIn_hub_crossing ride the save; no
-- detached thread or saved callback is created. Every wake checks the dev
-- mod's own namespace (SMROptInTrainFloor, independent of either fix pack).
-- Removing a placed hub's content mod remains unsupported, as before.
-- ===========================================================================

function SMROptInTrainHubBase:HubCrossingTrain()
	local lock = self.SMROptIn_hub_crossing
	-- An interrupted train still occupies the crossing. Keep it blocked until
	-- vanilla's Start/Done cleanup removes it; a dead thread is not clearance.
	if IsValid(lock) then return lock end
	self.SMROptIn_hub_crossing = false
	-- A build-3 save may be sleeping inside vanilla TrainPassThrough. Its
	-- saved frame owns trains_traversing until it finishes; do not overlap it
	-- with a new crossing or copy it into a lock that frame cannot release.
	for _, train in pairs(self.trains_traversing or empty_table) do
		if IsValid(train) then return train end
	end
end

function SMROptInTrainHubBase:HubReservations()
	local busy = {}
	for _, train in pairs(self.track_busy or empty_table) do
		if IsValid(train) then
			-- Also migrates build-3's opposite-key reservations without moving
			-- a train or losing an inbound reservation. Never validate by radius.
			local idx = train.current_station == self and train.station_arrival_track
				or IsValid(train.track) and self:GetConnectionSpot(train.track)
			if idx then busy[idx] = train end
		end
	end
	self.track_busy = busy
	return busy
end

function SMROptInTrainHubBase:AddOccupyingTrain(train, platform, arrival)
	platform = platform or train.track
	local idx = IsValid(platform) and self:GetConnectionSpot(platform) or platform
	if idx then self:HubReservations()[idx] = train end
end

function SMROptInTrainHubBase:GetOccupyingTrain(track, arrival)
	local idx = IsValid(track) and self:GetConnectionSpot(track) or track
	local occupant = self:HubReservations()[idx]
	local crossing = self:HubCrossingTrain()
	if arrival then
		if crossing then return crossing end
		local incoming = self:HubIncomingTrain()
		if incoming then return incoming end
	end
	-- LoadTrain:258 asks if the REVERSE platform is free. With our own-line
	-- keys it finds itself: exempt only that train's own LoadTrain command.
	-- TrackBase:AssignTrain's separate thread still sees the occupied spawn.
	if not arrival and occupant and occupant.command == "LoadTrain"
		and CurrentThread() == occupant.command_thread then return nil end
	return occupant or crossing
end

function SMROptInTrainHubBase:RemoveOccupyingTrain(train)
	Station.RemoveOccupyingTrain(self, train)
	if self.SMROptIn_hub_crossing == train then self.SMROptIn_hub_crossing = false end
	for track, traversing in pairs(self.trains_traversing or empty_table) do
		if traversing == train then self.trains_traversing[track] = nil end
	end
	Msg("TrainLeave", train, self)
end

function SMROptInTrainHubBase:HubRestoreParkedTrains()
	-- Load-time migration, before the colony is shown. Existing stopped trains
	-- otherwise retain build-3's wrong synthetic position until their next trip.
	for _, train in ipairs(self.city.labels.Train or empty_table) do
		if train.current_station == self and (train.at_station or train.at_spawn_track)
			and train ~= self:HubCrossingTrain() then
			local idx = train.station_arrival_track or self:GetConnectionSpot(train.track)
			if idx then
				local kind = train.at_spawn_track and not train.station_arrival_track and "Spawn" or "Stop"
				train:StopInterpolation()
				train:SetPos((synthetic_spot_pos(self, kind, idx)))
				train:SetAngle(synthetic_spot_angle(self, kind, idx))
			end
		end
	end
	self:HubReservations()
end

function SMROptInTrainHubBase:HubIncomingTrain(except)
	for _, train in pairs(self:HubReservations()) do
		if train ~= except and train.current_station ~= self then return train end
	end
end

function SMROptInTrainHubBase:CanTrainTraverse(train, arrival_track, departure_track)
	local lock = self:HubCrossingTrain()
	local busy = self:HubReservations()[self:GetConnectionSpot(arrival_track)]
	return (not lock or lock == train) and (not busy or busy == train)
		and not self:HubIncomingTrain(train) and departure_track:IsTrackFreeFor(train, self)
end

function SMROptInTrainHubBase:HubAcquireCrossing(train, departure_track)
	while IsValid(self) and not self.destroyed and IsValid(train)
		and (not departure_track or IsValid(departure_track)) do
		local other = self:HubCrossingTrain()
		if (not other or other == train) and not self:HubIncomingTrain(train)
			and (not departure_track or departure_track:IsTrackFreeFor(train, self)) then
			self.SMROptIn_hub_crossing = train
			return true
		end
		train:StopInterpolation()
		WaitMsg("TrainLeave", 500)
		if not rawget(_G, "SMROptInTrainFloor") then return end
	end
end

function SMROptInTrainHubBase:HubMoveTrain(train, pos, final_speed, yaw)
	if not IsValid(train) or not IsValid(self) then return end
	local start_speed = pf.GetSpeed(train)
	-- A stop-to-stop run needs an acceleration leg before braking; asking
	-- the native constant-acceleration solver for zero at both ends cannot
	-- express it. This midpoint controls speed, never either tuned position.
	if final_speed == 0 and start_speed <= 0 and train:GetDist2D(pos) > 1 then
		local middle = train:GetPos() + MulDivRound(pos - train:GetPos(), 1, 2)
		start_speed = train:GetNominalMoveSpeed() / 3
		if not self:HubMoveTrain(train, middle, start_speed, yaw) then return end
		if not rawget(_G, "SMROptInTrainFloor") then return end
	end
	local accel, time = train:GetAccelerationAndTime(pos, final_speed, start_speed)
	if yaw then train:SetAngle(yaw, time) end
	train:SetPos(pos, time)
	train:SetAcceleration(accel)
	Sleep(time)
	if not rawget(_G, "SMROptInTrainFloor") then return end
	return IsValid(train) and IsValid(self) and not self.destroyed
end

-- Every interior line meets at the hub centre. Opposite lines need no pivot.
function SMROptInTrainHubBase:HubTurnPoint(arrival_idx, departure_idx)
	local a, b = self.hub_connector_directions[arrival_idx], self.hub_connector_directions[departure_idx]
	if (a - b) % 3 == 0 then return end
	local x, y, z = self:GetPosXYZ()
	return point(x, y, z + train_deck_height(self))
end

-- Reuse 3b's normalized smoothstep, now for a pure sideways transfer after
-- stopping. Keep the nose aimed down the rail. Game-time interpolation keeps
-- the same path at normal/fast/fastest; no realtime callback or Train wrapper.
function SMROptInTrainHubBase:HubSlideTrain(train, destination)
	local start = train:GetPos()
	train:StopInterpolation()
	for i = 1, 8 do
		local f = MulDivRound(i * i * (24 - 2 * i), 1000, 512)
		train:SetPos(start + MulDivRound(destination - start, f, 1000), 150)
		train:SetAcceleration(0)
		Sleep(150)
		if not rawget(_G, "SMROptInTrainFloor") then return end
		if not IsValid(train) or not IsValid(self) or self.destroyed then return end
	end
	train:StopInterpolation()
	return true
end

function SMROptInTrainHubBase:HubEnterTrain(train, idx)
	local ramp = synthetic_spot_pos(self, "Ramparrive", idx)
	local ox, oy = lane_offset(self, idx, true)
	-- Unlike Station.lua:1105 (archived 1.1.0.403908), never teleport a long
	-- arrival. Stop on the arm, then slide in before travelling into the tunnel.
	if not self:HubMoveTrain(train, ramp, 0) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	return self:HubSlideTrain(train, ramp - point(ox, oy, 0))
end

function SMROptInTrainHubBase:TrainArrive(train, arrival_track)
	local idx = self:GetConnectionSpot(arrival_track)
	if not idx or not self:HubAcquireCrossing(train) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	if not self:HubEnterTrain(train, idx) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	if not self:HubMoveTrain(train, synthetic_spot_pos(self, "Stop", idx), 0) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	train:StopInterpolation()
	train.current_station = self
	train.station_arrival_track = idx
	train.at_station = true
	table.remove_value(arrival_track.assigned_vehicles, train)
	-- Keep its own-line parking reservation, release only the moving lock.
	self.SMROptIn_hub_crossing = false
	Msg("TrainLeave", train, self)
end

function SMROptInTrainHubBase:HubRouteTrain(train, arrival_idx, departure_idx, departure_track, reverse)
	local el = self:GetConnectorElement(departure_idx)
	if not IsValid(el) then return end
	local speed = train:GetNominalMoveSpeed() / 3
	local ramp = synthetic_spot_pos(self, "Rampdepart", departure_idx)
	local outward = synthetic_spot_angle(self, "Rampdepart", departure_idx)
	if reverse then
		-- Owner's same-position flip; it stays centred until the outer slide.
		train:SetAngle(outward)
	else
		local turn = self:HubTurnPoint(arrival_idx, departure_idx)
		if turn then
			if not self:HubMoveTrain(train, turn, 0) then return end
			if not rawget(_G, "SMROptInTrainFloor") then return end
			train:SetAngle(outward, 1000)
			Sleep(1000)
			if not rawget(_G, "SMROptInTrainFloor") then return end
			if not IsValid(train) or not IsValid(self) or self.destroyed then return end
		end
	end
	local ox, oy = lane_offset(self, departure_idx, false)
	if not self:HubMoveTrain(train, ramp - point(ox, oy, 0), 0) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	if not self:HubSlideTrain(train, ramp) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	local step = self == departure_track:GetStartStation() and 1 or -1
	train:GotoSpot(el, step == 1 and "Enter1" or "Enter2", speed, nil, 0)
	if not rawget(_G, "SMROptInTrainFloor") then return end
	return IsValid(train) and IsValid(self) and not self.destroyed
end

function SMROptInTrainHubBase:TrainDepart(train, departure_track)
	local idx = self:GetConnectionSpot(departure_track)
	if not idx then return end
	-- GotoStation assigned the outgoing track and set at_station=false before
	-- calling us. While waiting on the deck, remain parked so we cannot take
	-- a track from a train already crossing towards that exit (Track.lua:357).
	train.at_station = true
	if not self:HubAcquireCrossing(train, departure_track) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	train.at_station = false
	local arrival_idx = train.station_arrival_track or idx
	if not self:HubRouteTrain(train, arrival_idx, idx, departure_track, arrival_idx == idx) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	train.station_arrival_track = nil
	train.at_station = false
	train.at_spawn_track = false
	self:RemoveOccupyingTrain(train)
end

function SMROptInTrainHubBase:TrainPassThrough(train, arrival_track, departure_track)
	local arrival_idx, idx = self:GetConnectionSpot(arrival_track), self:GetConnectionSpot(departure_track)
	if not arrival_idx or not idx then return end
	if not self:HubAcquireCrossing(train, departure_track) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	-- Reserve the outgoing track before the first movement yield. Vanilla
	-- normally does this only AFTER TrainPassThrough returns, allowing a
	-- parked train to claim that track while a through train is crossing.
	train:AssignToTrack(departure_track)
	train.current_station = self
	if not self:HubEnterTrain(train, arrival_idx) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	if not self:HubRouteTrain(train, arrival_idx, idx, departure_track, false) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	train.current_station = self
	table.remove_value(arrival_track.assigned_vehicles, train)
	self:RemoveOccupyingTrain(train)
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

-- DroneControl:SpawnDrone is an empty "override me" (DroneControl.lua:725).
-- Drones appear around the body the way DroneControl:SpawnDronesAround places
-- them (:244-255), because the stand-in has no drone entrance to walk out of.
function SMROptInTrainHubBase:SpawnDrone()
	if #self.drones >= self:GetMaxDrones() then return false end
	local drone = self.city:CreateDrone()
	drone:SetCommandCenter(self)
	drone.battery_max = hub_drone_battery_max
	drone.battery = hub_drone_battery_max
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

-- Visual launch pad for build 4's repair drones. It occupies q=1,r=1 inside
-- the ring but deliberately has no NotBuildingRechargeStation behind it, so it
-- cannot charge. Existing saves may still carry the old charger object; the
-- initializer removes that object and retains its platform model.
local function launch_pad_offset()
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
	self:HubUpdateProduction()
	self.electricity:SetConsumption(self.electricity_consumption)
end

-- Owner's cold-start ruling: lack of grid power must not disable our source.
-- No saved flag and no vanilla wrap. SetWorking also runs when the boolean
-- stays false, so switching off or malfunction while unpowered is observed.
function SMROptInTrainHubBase:HubUpdateProduction()
	if self.electricity then
		local enabled = self.ui_working and not self.is_malfunctioned and not self.destroyed
		self.electricity:SetProduction(enabled and self:GetPerformanceModifiedElectricityProduction() or 0)
	end
end

function SMROptInTrainHubBase:SetWorking(working)
	BaseBuilding.SetWorking(self, working)
	-- After the combined OnSetWorking callbacks, including ElectricityProducer.
	self:HubUpdateProduction()
end

function SMROptInTrainHubBase:OnModifiableValueChanged(prop)
	-- Modifiers.lua:20-26 (archived 1.1.0.403908): parents run first.
	if prop == "electricity_production" or prop == "performance" then
		self:HubUpdateProduction()
	end
end

function SMROptInTrainHubBase:InitHubLaunchPad()
	AttachedRechargeStations.SetWorking(self.charging_stations or empty_table, false)
	for _, station in ipairs(self.charging_stations or empty_table) do
		if IsValid(station) then DoneObject(station) end
	end
	self.charging_stations = {}
	-- Backstop old saves whose helper survived but whose saved list did not.
	for _, station in ipairs(self:GetAttaches("NotBuildingRechargeStation") or empty_table) do
		if IsValid(station) then DoneObject(station) end
	end
	local platforms = self:GetAttaches("RechargeStationPlatform") or empty_table
	if #platforms == 0 then
		local platform = PlaceObjectIn("RechargeStationPlatform", self:GetMap())
		self:Attach(platform, self:GetSpotBeginIndex("Origin"))
		platform:SetAttachOffset(launch_pad_offset())
		platforms = { platform }
	end
	local template = BuildingTemplates.RechargeStation
	local ccs = GetCurrentColonyColorScheme()
	local cm1, cm2, cm3, cm4 = GetBuildingColors(ccs, template)
	for _, platform in ipairs(platforms) do
		platform:ClearEnumFlags(const.efSelectable)
		if platform:HasState("idle") then platform:SetState("idle") end
		if cm1 then Building.SetPalette(platform, cm1, cm2, cm3, cm4) end
	end
end

local function top_up_hub_drones(self)
	for _, drone in ipairs(self.drones or empty_table) do
		if IsValid(drone) and drone.command_center == self then
			drone.battery_max = hub_drone_battery_max
			drone.battery = hub_drone_battery_max
			if drone.command == "EmergencyPower" or drone.command == "NoBattery" or drone.command == "Charge" then
				drone:SetCommand("Idle")
			end
		end
	end
end

function SMROptInTrainHubBase:GameInit()
	-- Runs after Station's and DroneControl's bodies, and before the Notify'd
	-- SpawnDrones and ConnectTaskRequesters (DroneControl.lua:230-236,
	-- TaskRequest.lua:260-266), which need the radius.
	self.work_radius = hub_work_radius
	self.UIWorkRadius = hub_work_radius
	self.show_service_area = false
	self.service_area_min = hub_work_radius
	self.service_area_max = hub_work_radius
	self:InitHubLaunchPad()
	self:InitHubReactorVisual()
	self:GatherOrphanedDrones()
	top_up_hub_drones(self)
	place_hub_markers(self)
	Floor.Reconcile(self)
end

function SMROptInTrainHubBase:OnSetWorking(working)
	if working then
		self:GatherOrphanedDrones()
		top_up_hub_drones(self)
		self:SetWaitingDronesIdle()
	end
	self:NotifyWorkingChanged(self.connected_task_requesters)
	set_hub_reactor_working(self, working)
end

-- Done is combined. TrackConnectedObjBase's body removes connectors 0..4
-- (TrainTransport.lua:14-37); this one removes the rest. Attached platform
-- visuals are removed with their parent.
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
	-- Owner ruling 2026-09-19: these stopgap drones never need a charger. This
	-- runs in every hub state, including malfunction and no power.
	top_up_hub_drones(self)
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
-- Load. Markers and the reactor helper are unsaved. Radius 15 is authoritative
-- over every saved slider value, and an old working charger becomes a plain pad.
-- ===========================================================================

local function heal_after_load(hub)
	hub:HubUpdateProduction()
	hub:HubRestoreParkedTrains()
	hub.UIWorkRadius = hub_work_radius
	hub.show_service_area = false
	hub.service_area_min = hub_work_radius
	hub.service_area_max = hub_work_radius
	hub:SetWorkRadius(hub_work_radius)
	place_hub_markers(hub)
	hub:InitHubLaunchPad()
	top_up_hub_drones(hub)
	hub:InitHubReactorVisual()
	Floor.Reconcile(hub)
end

function OnMsg.LoadGame()
	AllMapsForEach("map", "SMROptInTrainHubBase", heal_after_load)
end

-- ===========================================================================
-- The sizes. Thin by design: a size is a connector table and a count.
-- ===========================================================================

DefineClass.SMROptInTrainHub6Base = {
	__parents = { "SMROptInTrainHubBase" },
	last_connector_idx = 6,
	hub_connector_directions = { 4, 1, 3, 0, 2, 5 }, -- imported body's connector order
}

-- The BuildingTemplate companion is Mod-Editor generated. Its Data/ source is
-- authoritative and now names the imported entity; this postprocess keeps the
-- dev build runnable until the next editor save regenerates the companion.
function OnMsg.ClassesPostprocess()
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
