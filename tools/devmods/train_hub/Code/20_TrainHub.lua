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
--   SMROptIn_track_work      field on hub objects: the track-repair toggle and the
--       pending list (build 4; the TRACK WORK section below is its record)
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
-- Longer-stub model handoff: try 48 m, then 47-49 m by eye after import.
-- These are owner-directed visual trials, not solved train-length clearances.
-- All tunables reset on a full restart.
Floor.HubTransitionPauseDistance = 48 * guim
-- Owner: entrance looks good; exit slides too early. Separate outward trial.
Floor.HubExitSlideDistance = 50 * guim
-- Shift the whole siding movement 3.5 m inward from the Pass 3 trial.
-- Moving entry alone shortened the curve without changing parked overhang.
Floor.HubParkDistance = 11 * guim
-- Provisional owner-facing positions, never calculated from train length.
-- Positive offset is clockwise of the outward spur (the imported siding hand).
Floor.HubSidingOffset = 4.5 * guim -- next lateral trial: 5.0 m, by eye
Floor.HubSidingEntryDistance = 17 * guim -- first decoupled-rate trial: 2 m farther straight
Floor.HubSidingRejoinDistance = 1.5 * guim -- retain the original 9.5 m inward rejoin
Floor.HubSidingReverseRejoinDistance = 23 * guim -- retain the original 12 m reverse rejoin
Floor.HubDwellTime = 6000 -- game ms, each of LoadTrain and UnloadTrain

-- D14(a), 2026-09-24: rollback of 3a0faff after owner loads asserted in
-- luaSPersist.cpp:1272 and crashed, including known-good template saves.
-- Keep the legacy wrapper's body unchanged: older hub saves resolve its Lua
-- frames through cthread.WaitWakeup. The snapshot guard below temporarily
-- publishes the native waiter and marks new metadata for the matching loader.
-- Native old -> new -> save -> reload verification is required for that guard.
-- See docs/agent/reports/TRAIN_HUB_AUDIT_111_20260923.md, load-crash follow-up.
-- SOURCE: archived 1.1.0.403908 Train.lua:281,450. These commands each
-- issue exactly one WaitWakeup, after transfer/boarding, with the remaining
-- portion of a 12-second deadline. Subtract the difference from that input:
-- max(max(12000-elapsed,100)-6000,100) == max(6000-elapsed,100).
-- Layer 3 input adjustment; tail delegation has no post-yield work. No new
-- timer, saved timestamp, command replacement or early boarding wakeup.
local function hub_dwell_train(hub, thread, result)
	for _, train in ipairs(hub.city.labels.Train or empty_table) do
		if train.current_station == hub and train.at_station
			and train.command_thread == thread
			and (train.command == "LoadTrain" or train.command == "UnloadTrain") then
			result.train = train
			return
		end
	end
end

local function install_hub_dwell()
	if Floor.HubDwellInstalled then return end
	local previous = rawget(_G, "WaitWakeup")
	if type(previous) ~= "function" or type(AllMapsForEach) ~= "function" then
		print("[TrainHubDev] hub dwell unavailable: wait/map API missing")
		return
	end
	local wrapper = function(timeout, ...)
		if rawget(_G, "SMROptInTrainFloor") and type(timeout) == "number"
			and timeout >= 100 and timeout <= const.HourDuration / 5 then
			local result = {}
			AllMapsForEach("map", "SMROptInTrainHubBase", hub_dwell_train, CurrentThread(), result)
			if result.train then
				local dwell = Max(100, Min(SMROptInTrainFloor.HubDwellTime, const.HourDuration / 5))
				timeout = Max(timeout - (const.HourDuration / 5 - dwell), 100)
			end
		end
		return previous(timeout, ...)
	end
	_G.WaitWakeup = wrapper
	Floor.HubDwellInstalled = rawget(_G, "WaitWakeup") == wrapper
	Floor.HubDwellNativeWait = previous
	Floor.HubDwellWrapper = wrapper
end

-- D14(a): owner 2026-09-24 proposed removing our replacement around saving.
-- Scope it to the actual snapshot, not SaveGameStart: autosaves keep running
-- during earlier yields, and in-memory/bug-report saves skip those messages.
-- SOURCE: archived 1.1.1.405907 CommonLua/Savegame.lua:853-867,1004-1033,
-- 1117-1153; SavegameMetadata.lua:50-82; Core/cthreads.lua:466-478.
-- New save contract: metadata.SMROptIn_hub_native_waiter = 1. Keep unmarked
-- existing hub saves on their legacy mapping; do not infer it from mod version.
-- Pre-wrapper hub saves are an older ambiguous case, not classified here.
local function install_hub_save_guard()
	if Floor.HubSaveGuardInstalled then return end
	local previous = rawget(_G, "PersistGame")
	if type(previous) ~= "function" or not Floor.HubDwellInstalled
		or type(Floor.HubDwellNativeWait) ~= "function"
		or type(Floor.HubDwellWrapper) ~= "function" then return end
	local wrapper = function(...)
		local before = rawget(_G, "WaitWakeup")
		local native = Floor.HubDwellNativeWait
		if before ~= Floor.HubDwellWrapper and before ~= native then
			return "Train hub save waiter changed; snapshot cancelled"
		end
		_G.WaitWakeup = native
		local result = table.pack(pcall(previous, ...))
		if rawget(_G, "WaitWakeup") == native then _G.WaitWakeup = before end
		if not result[1] then error(result[2], 0) end
		return table.unpack(result, 2, result.n)
	end
	_G.PersistGame = wrapper
	Floor.HubSaveGuardInstalled = rawget(_G, "PersistGame") == wrapper
	if Floor.HubSaveGuardInstalled then
		print("[TrainHubDev] save guard: native waiter snapshot; legacy hub load mapping retained")
	end
end

function OnMsg.GatherGameMetadata(metadata)
	if Floor.HubSaveGuardInstalled then metadata.SMROptIn_hub_native_waiter = 1 end
end

function OnMsg.PreLoadGame(metadata)
	if not Floor.HubSaveGuardInstalled then return end
	local has_hub
	for _, mod in ipairs(metadata.active_mods or empty_table) do
		local id = type(mod) == "table" and mod.id or mod
		if id == "SMR_TrainHubDev_20260918" then has_hub = true; break end
	end
	local target = (metadata.SMROptIn_hub_native_waiter == 1 or not has_hub)
		and Floor.HubDwellNativeWait or Floor.HubDwellWrapper
	Floor.HubWaitLoadRestore = { before = rawget(_G, "WaitWakeup"), target = target }
	_G.WaitWakeup = target
end

function OnMsg.UnpersistEnd()
	local restore = Floor.HubWaitLoadRestore
	Floor.HubWaitLoadRestore = nil
	if restore and rawget(_G, "WaitWakeup") == restore.target then
		_G.WaitWakeup = restore.before
	end
end

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
	starting_drones = 5, -- the standing fleet (owner, 2026-09-23); Floor.HubRepairTune.Standing rules after placement
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
			and Floor.HubParkDistance or (kind == "Rampdepart"
				and Floor.HubExitSlideDistance or Floor.HubTransitionPauseDistance)
		local radius = self:GetDist2D(point(x, y))
		x = cx + MulDivRound(x - cx, distance, radius)
		y = cy + MulDivRound(y - cy, distance, radius)
	end
	if kind == "Ramparrive" or kind == "Rampdepart" then
		-- Only the transition's outer end is on vanilla's lane.
		local ox, oy = lane_offset(self, idx, kind ~= "Rampdepart")
		x, y = x + ox, y + oy
	end
	if kind == "Stop" or kind == "Spawn" then
		local radius = self:GetDist2D(point(x, y))
		local ox = MulDivRound(y - cy, Floor.HubSidingOffset, radius)
		local oy = MulDivRound(cx - x, Floor.HubSidingOffset, radius)
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

-- D14(f): the pre-siding exit guard treated every parked train as on the rail.
-- Two loaded trains on opposite sidings then waited on each other forever.
-- Owner's later 2026-09-20 siding design permits passing a parked train (spec
-- section 9). TrainArrive publishes at_station + station_arrival_track only
-- after the siding move finishes; TrainDepart clears at_station before moving.
-- Unknown/legacy or incoming reservations still block. The crossing lock and
-- vanilla outgoing-track exclusion still serialize actual movement (archived
-- 1.1.1.405907 Lua/Buildings/Track.lua:357-372). No queue/routing policy change.
function SMROptInTrainHubBase:HubExitClear(train, departure_track)
	if not IsValid(departure_track) then return false end
	local idx = self:GetConnectionSpot(departure_track)
	if not idx then return false end
	local occupant = self:HubReservations()[idx]
	local on_siding = occupant and occupant.current_station == self
		and occupant.at_station and occupant.station_arrival_track == idx
		and self:HubCrossingTrain() ~= occupant
	return (not occupant or occupant == train or on_siding)
		and departure_track:IsTrackFreeFor(train, self)
end

function SMROptInTrainHubBase:CanTrainTraverse(train, arrival_track, departure_track)
	local lock = self:HubCrossingTrain()
	local busy = self:HubReservations()[self:GetConnectionSpot(arrival_track)]
	return (not lock or lock == train) and (not busy or busy == train)
		and not self:HubIncomingTrain(train) and self:HubExitClear(train, departure_track)
end

function SMROptInTrainHubBase:HubAcquireCrossing(train, departure_track)
	while IsValid(self) and not self.destroyed and IsValid(train)
		and (not departure_track or IsValid(departure_track)) do
		local other = self:HubCrossingTrain()
		if (not other or other == train) and not self:HubIncomingTrain(train)
			and (not departure_track or self:HubExitClear(train, departure_track)) then
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

function SMROptInTrainHubBase:HubCentrePosition(idx, distance)
	local ramp = synthetic_spot_pos(self, "Ramparrive", idx)
	local ox, oy = lane_offset(self, idx, true)
	local cx, cy = self:GetPosXYZ()
	local centre = point(cx, cy, ramp:z())
	local radial = ramp - point(ox, oy, 0) - centre
	return centre + MulDivRound(radial, distance, Floor.HubTransitionPauseDistance)
end

-- One longitudinal acceleration/braking profile, with a smoothstep lateral
-- offset. Subdivision follows distance, not game speed. No sideways stop or
-- extra dwell is inserted; yaw stays along the spur as on the outer slide.
function SMROptInTrainHubBase:HubSidingCurve(train, destination, final_speed, idx)
	local start = train:GetPos()
	local cx, cy = self:GetPosXYZ()
	local centre = point(cx, cy, start:z())
	local axis = self:HubCentrePosition(idx, guim) - centre
	local delta = destination - start
	local along = MulDivRound(delta:x(), axis:x(), guim)
		+ MulDivRound(delta:y(), axis:y(), guim)
	local forward = MulDivRound(axis, along, guim)
	local lateral = delta - forward
	local initial_speed = pf.GetSpeed(train)
	for i = 1, 8 do
		local f = MulDivRound(i * i * (24 - 2 * i), 1000, 512)
		local pos = start + MulDivRound(forward, i, 8) + MulDivRound(lateral, f, 1000)
		-- v^2 varies linearly with distance under constant acceleration.
		local speed = sqrt(Max(0, initial_speed * initial_speed
			+ MulDivRound(final_speed * final_speed - initial_speed * initial_speed, i, 8)))
		if not self:HubMoveTrain(train, pos, speed) then return end
		if not rawget(_G, "SMROptInTrainFloor") then return end
	end
	return true
end

-- Match the accepted outer slide's eight 150 ms lateral smoothstep samples while
-- continuing forward. The Hermite forward term enters at the approach speed and
-- reaches zero at Stop, so onset position cannot retime the sideways movement.
function SMROptInTrainHubBase:HubSidingEntrySlide(train, destination, idx)
	local start = train:GetPos()
	local cx, cy = self:GetPosXYZ()
	local centre = point(cx, cy, start:z())
	local axis = self:HubCentrePosition(idx, guim) - centre
	local delta = destination - start
	local along = MulDivRound(delta:x(), axis:x(), guim)
		+ MulDivRound(delta:y(), axis:y(), guim)
	local forward = MulDivRound(axis, along, guim)
	local lateral = delta - forward
	local forward_distance = Max(1, train:GetDist2D(start + forward))
	local lead_distance = MulDivRound(pf.GetSpeed(train), 1200, 1000)
	local lead = MulDivRound(forward, lead_distance, forward_distance)
	for i = 1, 8 do
		local q = i * 125
		local f = MulDivRound(i * i * (24 - 2 * i), 1000, 512)
		local lead_f = MulDivRound(q * (1000 - q), 1000 - q, 1000000)
		local pos = start + MulDivRound(forward + lateral, f, 1000)
			+ MulDivRound(lead, lead_f, 1000)
		train:SetPos(pos, 150)
		train:SetAcceleration(0)
		Sleep(150)
		if not rawget(_G, "SMROptInTrainFloor") then return end
		if not IsValid(train) or not IsValid(self) or self.destroyed then return end
	end
	train:StopInterpolation()
	return true
end

function SMROptInTrainHubBase:HubMoveOntoSiding(train, idx)
	if not self:HubMoveTrain(train, self:HubCentrePosition(idx, Floor.HubSidingEntryDistance),
		train:GetNominalMoveSpeed() / 3) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	return self:HubSidingEntrySlide(train, synthetic_spot_pos(self, "Stop", idx), idx)
end

function SMROptInTrainHubBase:HubRejoinFromSiding(train, idx, reverse)
	local distance = reverse and Floor.HubSidingReverseRejoinDistance or Floor.HubSidingRejoinDistance
	if reverse then train:SetAngle(synthetic_spot_angle(self, "Rampdepart", idx)) end
	return self:HubSidingCurve(train, self:HubCentrePosition(idx, distance),
		train:GetNominalMoveSpeed() / 3, idx)
end

function SMROptInTrainHubBase:TrainArrive(train, arrival_track)
	local idx = self:GetConnectionSpot(arrival_track)
	if not idx or not self:HubAcquireCrossing(train) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	if not self:HubEnterTrain(train, idx) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
	if not self:HubMoveOntoSiding(train, idx) then return end
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
	-- Owner: slide, then immediately travel normally, without a slow exit leg.
	-- Use vanilla's outgoing-element speed (tech/heat/law modifiers included).
	local speed = train:GetNominalMoveSpeed(el)
	train:GotoSpot(el, step == 1 and "Enter1" or "Enter2", speed, speed, 0)
	if not rawget(_G, "SMROptInTrainFloor") then return end
	if not IsValid(train) or not IsValid(self) or self.destroyed then return end
	-- Vanilla LoadTrain/GotoStation requests teleport_to_next after a station
	-- or through hub (archived 1.1.0.403908 Train.lua:286,411). Traverse then
	-- snaps from the connector to the NEXT element's Enter spot (:649-682).
	-- Travel that segment with vanilla's own checks/pitch/speed first. Its
	-- later teleport lands at the position we have already reached, not ahead.
	if not train:CheckValidDest(departure_track) then return end
	local elements = departure_track.elements
	local first = step == 1 and 1 or #elements
	local reached = train:WaitTraverseElement(departure_track, elements, first, speed, step,
		nil, false, step == 1 and "Enter1" or "Enter2", step == 1 and "Exit1" or "Exit2")
	if not rawget(_G, "SMROptInTrainFloor") then return end
	if not reached then return end
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
	if not self:HubRejoinFromSiding(train, arrival_idx, arrival_idx == idx) then return end
	if not rawget(_G, "SMROptInTrainFloor") then return end
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

-- DroneControl:SpawnDrone is an empty "override me" (DroneControl.lua:725); this hub's is in
-- the TRACK WORK section below, where the fleet lives.

-- The old launch pad (a RechargeStationPlatform at q=1,r=1 with no charger behind it) is
-- gone (owner, 2026-09-22): InitHubLaunchPad now only clears what old saves still carry.

-- A visual-only reactor: the hub remains the sole grid object and producer.
-- Use the engine's existing shapeshifter class rather than introducing another
-- persisted class name. DeleteOnLoadGame removes the helper after save load and
-- heal_after_load recreates it. Seven vanilla outline hexes scaled by sqrt(4/7)
-- gives 75.6%, so 75% targets the owner's three-to-five-hex look.
-- Look pass (owner 2026-09-21, spec §9): our own themed entity; never restyle
-- vanilla's material. Retain the old visual until the owner imports the new one.
local reactor_entity = "SMROptInTrainHubReactor"
local reactor_fallback_entity = "FusionReactor"
local reactor_scale = 75
local reactor_offset = point(3897, 2250, 0) -- 45 m out, local angle 30 degrees

-- Palette pass (owner ask, 2026-09-22, in game): "close to base game, give us a few different
-- details and maybe more of a navy blue instead of the base game's light blue. And some metal
-- polished on some of the surfaces."
--
-- PER-OBJECT colorization, on OUR attached copy only. `obj:SetColorizationMaterial(channel,
-- color, roughness, metallic)` is the same call vanilla makes to paint every building per
-- instance from the colony colour scheme (`Lua/Buildings/Building.lua:752-760`:
-- `GetBuildingColors` -> `Building:SetPalette` -> `SetObjectPaletteRecursive`; the setter's own
-- signature at `CommonLua/Classes/Colorization.lua:802,:810,:818` and `CommonLua/Patterns.lua:283`).
-- It writes to the OBJECT, never to the shared material asset, so every other fusion reactor in
-- the colony keeps the base game's light blue and the 2026-09-21 ruling above stands.
-- Read on build 1.1.0.403908, from that build's archived tree
-- `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908\Src`:
--   * REACHABLE ON THE ATTACH. `AppendClass.CObject = { __parents = { "ColorizableObject" } }`
--     (`Colorization.lua:723-725`) puts the setter on every CObject, and our visual is one:
--     `ShapeshifterAutoAttach` -> `Shapeshifter` (`CommonLua/Classes/AutoAttach.lua:2598-2600`)
--     -> `Object` (`CommonLua/Classes/Shapeshifter.lua:6-8`) -> `CObject`
--     (`CommonLua/Classes/_object.lua:5-7`). `ChangeEntity` does not touch colorization
--     (`AutoAttach.lua:2606-2619`), so setting it after the entity swap is safe.
--   * FOUR CHANNELS. Vanilla's own per-object API is exactly cm1..cm4
--     (`Colorization.lua:889-895`) and a building's palette is four colours
--     (`Lua/ColonyColorScheme.lua:20-22`). The engine's `const.MaxColorizationMaterials` is
--     C-side, so `GetMaxColorizationMaterials` (`Colorization.lua:105-107`) narrows the 4 below
--     to whatever THIS entity's colorization texture actually carries.
--   * UNITS, and they are NOT 0-1 and NOT 0-255. `color` is a packed RGB; `roughness` and
--     `metallic` are SIGNED offsets on the entity's authored material -- the editor sliders are
--     `min = -128, max = 127` (`Colorization.lua:179-181, :189-191`) and 0 means "as the artist
--     made it" (`const.NoColorization = RGBRM(white point, 0, 0)`, `CommonLua/Core/const.lua:452`;
--     the game's own `DefaultCM` is `RGB(128,128,128), 0, 0`, `Lua/ColonyColorScheme.lua:1`).
--     So polished steel here is a NEGATIVE roughness with a strongly POSITIVE metallic.
--   * SUB-MODELS. This paints the visual itself. Vanilla's recursion for a building is
--     `SetObjectPaletteRecursive` (`Colorization.lua:855-861`); if the owner reports pieces of
--     the reactor staying light blue, that is the next step, not a sign the call failed.
--
-- WHICH channel paints WHICH surface is unknown until the owner looks, so the four variants below
-- move ONE polished channel at a time and the mapping is learnable by eye: P1 is the flat navy
-- reference, P2/P3 polish a single channel, P4 polishes two. Console, no restart, no import:
--   SMROptInTrainFloor.SetHubReactorPalette("P1")   -- .. "P2", "P3", "P4"
--   SMROptInTrainFloor.SetHubReactorPalette{ [3] = { color = RGB(200, 205, 210), roughness = -90, metallic = 110 } }
--   SMROptInTrainFloor.SetHubReactorPalette("vanilla")
-- Code constants plus a session-only override: no persisted class, no saved field, no thread.
local reactor_navy = RGB(18, 32, 78)        -- the owner's navy, against vanilla's light blue
local reactor_steel = RGB(200, 205, 210)    -- polished steel
local steel_roughness, steel_metallic = -90, 110
local function navy_ch() return { color = reactor_navy, roughness = 0, metallic = 0 } end
local function steel_ch() return { color = reactor_steel, roughness = steel_roughness, metallic = steel_metallic } end
local hub_reactor_palettes = {
	P1 = { name = "navy all", channels = { navy_ch(), navy_ch(), navy_ch(), navy_ch() } },
	P2 = { name = "navy + steel on 1", channels = { steel_ch(), navy_ch(), navy_ch(), navy_ch() } },
	P3 = { name = "navy + steel on 2", channels = { navy_ch(), steel_ch(), navy_ch(), navy_ch() } },
	P4 = { name = "navy + steel on 3 and 4", channels = { navy_ch(), navy_ch(), steel_ch(), steel_ch() } },
}
local hub_reactor_palette_order = { "P1", "P2", "P3", "P4" }
local hub_reactor_channels = 4
local hub_reactor_palette_default = "P4" -- owner, 2026-09-22 in game: "P4 is the winner"
-- A variant key, a patched channel table, or false for the base game's look. Session only: a
-- restart puts the default back, exactly like Floor.HubLightTune.
local hub_reactor_palette = hub_reactor_palette_default

local function hub_reactor_palette_channels()
	local selected = hub_reactor_palette
	if not selected then return nil end
	if type(selected) == "table" then return selected end
	local variant = hub_reactor_palettes[selected]
	return variant and variant.channels or nil
end

local function hub_reactor_palette_name()
	local selected = hub_reactor_palette
	if not selected then return "vanilla (the entity's own default colours)" end
	if type(selected) == "table" then return "patched channels" end
	local variant = hub_reactor_palettes[selected]
	return string.format("%s \"%s\"", selected, variant and variant.name or "?")
end

-- Returns how many channels were written, so the smoke and the console can see it.
local function apply_hub_reactor_palette(visual)
	local channels = hub_reactor_palette_channels()
	if not channels or not IsValid(visual) or not visual.SetColorizationMaterial then return 0 end
	local count = hub_reactor_channels
	if visual.GetMaxColorizationMaterials then
		local entity_count = visual:GetMaxColorizationMaterials() or 0
		if entity_count > 0 then count = Min(count, entity_count) end
	end
	local written = 0
	for i = 1, count do
		local ch = channels[i]
		if ch and ch.color then
			visual:SetColorizationMaterial(i, ch.color, ch.roughness or 0, ch.metallic or 0)
			written = written + 1
			local r, g, b = 0, 0, 0
			if type(GetRGB) == "function" then r, g, b = GetRGB(ch.color) end
			print(string.format("[TrainHubDev] reactor palette: channel %d = %d,%d,%d roughness %d metallic %d",
				i, r or 0, g or 0, b or 0, ch.roughness or 0, ch.metallic or 0))
		end
	end
	print(string.format("[TrainHubDev] reactor palette: %s, %d of %d channels written on the attached copy only (vanilla's own per-object call; no material is restyled)",
		hub_reactor_palette_name(), written, hub_reactor_channels))
	return written
end

local function is_hub_reactor(obj)
	return IsValid(obj) and IsKindOf(obj, "ShapeshifterAutoAttach")
		and (obj:GetEntity() == reactor_entity or obj:GetEntity() == reactor_fallback_entity)
end

local function set_hub_reactor_working(self, working)
	for _, visual in ipairs(self:GetAttaches("ShapeshifterAutoAttach") or empty_table) do
		if is_hub_reactor(visual) then
			local state = working and "working" or "idle"
			if visual:HasState(state) then visual:SetState(state) end
			PlayFX("Working", working and "start" or "end", visual)
			if visual:GetEntity() == reactor_entity then
				visual:SetSIModulation(working and 200 or 0)
			end
		end
	end
end

function SMROptInTrainHubBase:InitHubReactorVisual()
	for _, visual in ipairs(self:GetAttaches("ShapeshifterAutoAttach") or empty_table) do
		if is_hub_reactor(visual) then DoneObject(visual) end
	end
	local entity = IsValidEntity(reactor_entity) and reactor_entity or reactor_fallback_entity
	if not IsValidEntity(entity) then return end
	local visual = PlaceObjectIn("ShapeshifterAutoAttach", self:GetMap())
	visual:ChangeEntity(entity)
	apply_hub_reactor_palette(visual)
	visual.fx_actor_class = reactor_fallback_entity -- preserve the existing Working FX actor
	visual:ClearEnumFlags(const.efCollision + const.efApplyToGrids + const.efWalkable + const.efSelectable)
	self:Attach(visual, self:GetSpotBeginIndex("Origin"))
	visual:SetAttachOffset(reactor_offset)
	visual:SetAttachAngle(210 * 60) -- face the hub centre
	visual:SetScale(reactor_scale)
	DeleteOnLoadGame(visual)
	set_hub_reactor_working(self, self.working)
end

-- No dust on the reactor visual (owner, 2026-09-23: "our mini fusion reactor is having dust buildup
-- while none of our other buildings do"). The hub is a Building, so it accumulates dust like any
-- other and vanilla pushes that value onto EVERY attach: `BuildingVisualDustComponent:SetDustVisuals`
-- -> `ApplyToObjAndAttaches(self, SetObjDust, ...)` (Lua/Buildings/BuildingComponents.lua:326-337,
-- Building.lua:1711-1719, SupplyGrid.lua:256-260 on 1.1.0.403908). Our body and glass entities have
-- no dust channel, so they show nothing; the vanilla FusionReactor entity does, so the reactor alone
-- wore the hub's dust. Let vanilla run, then zero the reactor attach the same way it was set.
function SMROptInTrainHubBase:SetDustVisuals(dust, in_dome)
	local result = Station.SetDustVisuals(self, dust, in_dome)
	for _, visual in ipairs(self:GetAttaches("ShapeshifterAutoAttach") or empty_table) do
		if is_hub_reactor(visual) then
			visual:SetDust(0, in_dome and const.DustMaterialInterior or const.DustMaterialExterior)
		end
	end
	return result
end

local function reinit_hub_reactor_visuals()
	AllMapsForEach("map", "SMROptInTrainHubBase", function(hub) hub:InitHubReactorVisual() end)
end

-- Layer a partial table over whatever is selected now. A patch onto "vanilla" paints ONLY the
-- channels it names and leaves the rest of the reactor as the base game made it.
local function patched_reactor_channels(patch)
	local base = hub_reactor_palette_channels()
	local out = {}
	for i = 1, hub_reactor_channels do
		local ch = base and base[i]
		if ch then out[i] = { color = ch.color, roughness = ch.roughness or 0, metallic = ch.metallic or 0 } end
	end
	for i, fields in pairs(patch) do
		if type(i) == "number" and i >= 1 and i <= hub_reactor_channels and type(fields) == "table" then
			local ch = out[i] or navy_ch()
			for k, v in pairs(fields) do ch[k] = v end
			out[i] = ch
		else
			print(string.format("[TrainHubDev] reactor palette: ignoring \"%s\"; patch by channel number 1-%d",
				tostring(i), hub_reactor_channels))
		end
	end
	return out
end

-- SMROptInTrainFloor.SetHubReactorPalette("P3")
-- SMROptInTrainFloor.SetHubReactorPalette{ [2] = { color = RGB(200, 205, 210), roughness = -90, metallic = 110 } }
-- SMROptInTrainFloor.SetHubReactorPalette("vanilla")  -- or with no argument at all
-- Nothing here is saved; a restart returns to the default variant.
function Floor.SetHubReactorPalette(variant)
	if type(variant) == "table" then
		hub_reactor_palette = patched_reactor_channels(variant)
	elseif variant == nil or variant == "vanilla" then
		-- Back to the base game's look by RECREATING the visual and applying nothing, rather than
		-- re-deriving vanilla's colours ourselves: C initializes a freshly placed CObject from its
		-- entity's own default palette (`GetColorsByColorizationPaletteName` is "called by C when
		-- initializing CObjects with palettes", `CommonLua/Classes/Colorization.lua:763-764`,
		-- build 1.1.0.403908), so an untouched new object IS the base game's look. Vanilla's
		-- building path is not open to us anyway: `GetBuildingColors` reads
		-- `building.palette_color1..4` (`Lua/ColonyColorScheme.lua:20-22`) and this visual is an
		-- attach, not a Building.
		hub_reactor_palette = false
	elseif hub_reactor_palettes[variant] then
		hub_reactor_palette = variant
	else
		print(string.format("[TrainHubDev] reactor palette: no variant \"%s\"; try %s, or \"vanilla\"",
			tostring(variant), table.concat(hub_reactor_palette_order, ", ")))
		return
	end
	reinit_hub_reactor_visuals()
end

-- The six original panel prisms, in one separately imported glass entity.
-- No new persisted class/field or thread: same DeleteOnLoadGame + recreation
-- lifecycle as the reactor. OI-23's "no dome glass" (owner 2026-09-21) was
-- SUPERSEDED on 2026-09-22: the owner asked for the outer hub glass too, so
-- the dome shell rides here as a second entity on exactly the same lifecycle.
local siding_glass_entity = "SMROptInTrainHub6Glass"
local dome_glass_entity = "SMROptInTrainHub6DomeGlass"
-- Both attach at Origin with a zero offset; each is IsValidEntity-gated, so an entity that has
-- not been imported yet is simply absent and the rest of the hub is unaffected.
local hub_glass_entities = { siding_glass_entity, dome_glass_entity }

-- Only the SIDING panels carry the glow that SI modulation drives. The dome shell carries none,
-- so it is deliberately left out of this loop and never receives a SetSIModulation call.
local function set_hub_glass_working(self, working)
	for _, visual in ipairs(self:GetAttaches("ShapeshifterAutoAttach") or empty_table) do
		if IsValid(visual) and visual:GetEntity() == siding_glass_entity then
			visual:SetSIModulation(working and 200 or 0)
		end
	end
end

-- Named for the siding it started as; it now rebuilds every glass shell in `hub_glass_entities`,
-- so the three call sites (GameInit, heal_after_load, and this file's own re-init) are unchanged.
function SMROptInTrainHubBase:InitHubSidingGlass()
	for _, entity in ipairs(hub_glass_entities) do
		for _, visual in ipairs(self:GetAttaches("ShapeshifterAutoAttach") or empty_table) do
			if IsValid(visual) and visual:GetEntity() == entity then DoneObject(visual) end
		end
		if IsValidEntity(entity) then
			local visual = PlaceObjectIn("ShapeshifterAutoAttach", self:GetMap())
			visual:ChangeEntity(entity)
			visual:ClearEnumFlags(const.efCollision + const.efApplyToGrids + const.efWalkable + const.efSelectable)
			self:Attach(visual, self:GetSpotBeginIndex("Origin"))
			visual:SetAttachOffset(point(0, 0, 0))
			DeleteOnLoadGame(visual)
		end
	end
	set_hub_glass_working(self, self.working)
end

-- Real lights on the arms (owner 2026-09-21, spec §9): three reds and three blues, one variant
-- per arm, for the owner to choose from in game. The painted lines are back, thin and in the arm's
-- colour (SMR-Assets paint_concept.py, DECK_STRIPS = 'thin'), and these lights sit ALONG those
-- lines, small and dim, so the glow spills onto the road beside a line and never washes a
-- platform. Vanilla light classes attached to the hub, so no new persisted class or field;
-- DeleteOnLoadGame + recreation like the reactor. A stopped hub DESTROYS its lights (the owner
-- measures their cost by hub off against on), never dims them.
-- Distances are centimetres in the arm's own frame: `u` outward from the centre, `v` sideways.
-- A variant's colour is also painted: change one here and ARM_LINE_COLOUR there, then rebake.
local hub_light_variants = {
	R1 = { name = "Ember rail", class = "PointLight", color = RGB(255, 40, 20),
		intensity = 60, radius = 3 * guim, spacing = 6 * guim, height = 40 },
	R2 = { name = "Crimson wash", class = "SpotLight", color = RGB(220, 0, 30),
		intensity = 100, radius = 5 * guim, spacing = 10 * guim, height = 2 * guim, inner = 50, outer = 100 },
	R3 = { name = "Rose beads", class = "PointLight", color = RGB(255, 60, 90),
		intensity = 120, radius = 150, spacing = 3 * guim, height = 30 },
	B1 = { name = "Ice rail", class = "PointLight", color = RGB(40, 160, 255),
		intensity = 60, radius = 3 * guim, spacing = 6 * guim, height = 40 },
	B2 = { name = "Deep blue wash", class = "SpotLight", color = RGB(0, 40, 255), tuned = true,
		-- owner, 2026-09-21: intensity "slightly bumped" from 100, which R2 keeps
		-- `tuned`: Floor.HubLightTune below overrides these live, from the console (owner 2026-09-22)
		intensity = 130, radius = 5 * guim, spacing = 10 * guim, height = 2 * guim, inner = 50, outer = 100 },
	B3 = { name = "Cobalt beads", class = "PointLight", color = RGB(90, 110, 255),
		intensity = 120, radius = 150, spacing = 3 * guim, height = 30 },
}-- Reassign here: key = the arm's local hex direction, value = a variant above. The reactor stands
-- between arms 0 and 1, so every arm can be found in game without a compass.
local hub_light_arms = {
	-- Owner, 2026-09-21: B2 "might be the winner", on every arm for a look (B3, tried first on a
	-- misread screenshot, was "the wrong blue"). The comparison was R1, B1, R2, B3, R3, B2 for arms
	-- 0-5; the painted colour is ARM_LINE_WINNER in SMR-Assets bake_thinlines.py.
	[0] = "B2", -- flanks the reactor (was the red flank)
	[1] = "B2", -- flanks the reactor (was the blue flank)
	[2] = "B2", -- next to the blue flank
	[3] = "B2", -- opposite the red flank
	[4] = "B2", -- opposite the blue flank
	[5] = "B2", -- next to the red flank, the arm the owner picked
}
local hub_light_arm_names = {
	[0] = "flanks the reactor (red flank)", [1] = "flanks the reactor (blue flank)",
	[2] = "next to the blue flank", [3] = "opposite the red flank",
	[4] = "opposite the blue flank", [5] = "next to the red flank",
}
-- The painted line's own path (paint_concept.py approach_light): one line on the arm's centre
-- out to 40 m, then two that ease apart to the platform centres, 3.46 m out, by 60 m and run
-- straight to 80 m. Inside the ring the two floor curves stay within 0.9 m of the centre line.
local hub_line_first, hub_line_split, hub_line_apart, hub_line_last = 8 * guim, 40 * guim, 60 * guim, 80 * guim
local hub_line_offset = 346
local function hub_line_v(u)
	local t = Clamp(MulDivRound(u - hub_line_split, 1000, hub_line_apart - hub_line_split), 0, 1000)
	return MulDivRound(MulDivRound(MulDivRound(t, t, 1000), 3000 - 2 * t, 1000), hub_line_offset, 1000)
end
local hub_light_classes = { "PointLight", "SpotLight" }

-- Owner, 2026-09-22, with screenshots: unlit the painted lines read as a light navy and the owner
-- likes that; where an arm spot lands on one they go lavender/purple. Read (the orchestrator's,
-- not measured): overexposure, not a wrong colour — the emissive line, the direct light and the
-- mirror deck's reflection clip the blue channel and the tonemapper desaturates toward white.
-- The owner wants "navy when lit, just brighter, without changing the colour", so the dials are
-- LIVE, from the console, with no import and no bake: drop `intensity` and raise `radius` to
-- spread the same light, and push the spot off the line with `side` so it grazes the road beside
-- the line instead of burning the emissive strip itself:
--   SMROptInTrainFloor.SetHubLightTune("side", 2 * guim)
--   SMROptInTrainFloor.SetHubLightTune{ intensity = 80, radius = 7 * guim, side = 150 }
-- Applies to B2 only, the variant every arm carries (hub_light_variants stays the defaults, and
-- a variant that is not `tuned` ignores this table). Nothing here is saved; a restart resets it.
Floor.HubLightTune = {
	-- Owner, 2026-09-22 (second night look): the whole line went lavender with the spots on
	-- (spacing 10 m, radius 5 m: every metre of line inside a cone). Intensity 130 -> 50 and the
	-- spots 1.5 m off the line, so they wash the road beside it and the line keeps its navy.
	intensity = 50,
	side = 150,          -- cm sideways off the painted line, outward on each mirror side
	height = 2 * guim,   -- above the deck
	color = RGB(0, 40, 255),
	radius = 5 * guim,
	inner = 50,
	outer = 100,
}

-- The live tune layered over a variant's defaults; `spacing` is deliberately not tunable, so the
-- arm count does not move under the owner while a look is being judged.
local function tuned_variant(variant)
	if not variant or not variant.tuned then return variant end
	local merged = {}
	for k, v in pairs(variant) do merged[k] = v end
	for k, v in pairs(Floor.HubLightTune or empty_table) do merged[k] = v end
	return merged
end

-- The structure's own lights (owner 2026-09-22, brief 01 step 6, spec §9), on the rim + edges
-- build (assets 24a98b7): small, dim, deep blue points seated where the model's painted lines
-- are. Same shape as the arm lights and the reactor — vanilla light classes attached at Origin,
-- positions computed here, DeleteOnLoadGame and recreation from InitHubLights, heal_after_load
-- and OnSetWorking, and a stopped hub DESTROYS them rather than dimming them. No spot, no new
-- persisted class and no saved field: the per-hub lists live in a weak-keyed local table.
-- They sit ON the emissive lines, which is where the lavender came from, so they start LOW.
-- Each family is independently off-able from the console, with no import and no bake:
--   SMROptInTrainFloor.SetHubStructureLights{ floor = { on = true } }
--   SMROptInTrainFloor.SetHubStructureLights{ rim = { intensity = 50, step = 20 }, pit = { on = false } }
local hub_structure_lights = {
	-- Owner, 2026-09-22: the ring rim points (0.5 m off a wall) read as intense bleeding circles,
	-- so that family is OFF by default and the two kept families start much lower.
	portal = { on = true, name = "portal rims", class = "PointLight",
		color = RGB(0, 40, 255), intensity = 4, radius = 350 }, -- owner, 2026-09-22: 15 was "a bit intense"
	pit = { on = false, name = "drone pit kerb", class = "PointLight", -- owner, 2026-09-22: cut; other lighting covers the pit
		color = RGB(0, 40, 255), intensity = 15, radius = 300 },
	rim = { on = false, name = "ring rim strip", class = "PointLight",
		color = RGB(0, 40, 255), intensity = 12, radius = 400, step = 10 },
	floor = { on = false, name = "floor edge strip", class = "PointLight",
		color = RGB(0, 40, 255), intensity = 30, radius = 300, step = 15 },
	-- Owner, 2026-09-22: "one center floor light" — a single warm downlight hanging from the dome's
	-- apex, where the six ribs meet at x = y = 0, and DOING NORMAL LIGHTING: it lights the floor
	-- plate (top z 0.30 m, radius 31.35 m), it is not an accent. A fixture is being built in the
	-- assets tree with its lens underside at about z 19.2 m, so the light hangs just below it at
	-- `height` (19.00 m hub-local, tunable). Warm like the rovers' headlights, RGB(255, 214, 170),
	-- also tunable. `night = true` puts it on the VANILLA night schedule (see hub_is_night below).
	-- Numbers to judge in game, all live from the console:
	--   * 19.00 m above the floor's top face, so `radius` 35 m reaches the plate's centre easily;
	--     the plate's far edge is sqrt(18.70^2 + 31.35^2) = 36.5 m away, just past the default
	--     attenuation, so widen `radius` if the rim stays dark.
	--   * `outer` 90 is the cone angle the arm spots use in the same units; if the engine reads it
	--     as the FULL angle, the pool is about r 18.7 m of the 31.35 m plate. Raise `outer` (and
	--     `inner` with it) to spill wider.
	-- Owner, 2026-09-22, in game: as a SpotLight this shone SIDEWAYS along a rib -- the arm spots'
	-- quarter-turn aim (axis_y, 90 deg) is now measured wrong, not merely unverified. A flood
	-- light needs no aim: a PointLight at the apex lights the floor and the dome from inside.
	crown = { on = true, night = true, name = "crown floor light", class = "PointLight",
		color = RGB(255, 214, 170), intensity = 150, radius = 40 * guim, height = 1900 },
	-- Owner, 2026-09-22, night look at the whole hub: "the lighting is just close but I want just a
	-- bit more in the interior. They will be same color temp as the big overhead flood light but I
	-- want them underneath the tracks giving a little more light on the ground floor just to even
	-- the lighting out down there. They don't need fixtures as you cannot see the underneath of the
	-- tracks from any angle." So: the crown's colour exactly, no fixture, no spot, and hidden under
	-- the six track arms' decks where nothing can look at them.
	--   * Three per arm at `radii` 9, 17 and 25 m out from the hub centre along that arm's own
	--     direction (6 x 3 = 18), all inside the ring's 32.95 m glazing radius.
	--   * `height` 7.00 m: the deck's top face is DECK_Z 8.00 m, so these hang 1.00 m under it and
	--     well above the 0.30 m floor plate. The metre of clearance is deliberate -- a point light
	--     half a metre off a surface burns a hot circle into it (spec finding), and this is meant to
	--     be fill, not a pool.
	--   * intensity 40 / radius 12 m: "a little more", not a wash. The crown at 150 / 40 m stays the
	--     hub's light source; these only lift the shadow the deck casts on the ground floor.
	-- `night = true`, so they follow the same vanilla schedule as the crown and are NOT PLACED by day.
	-- Live from the console like every other family, `radii` included:
	--   SMROptInTrainFloor.SetHubStructureLights{ underdeck = { intensity = 60, radius = 15 * guim } }
	--   SMROptInTrainFloor.SetHubStructureLights{ underdeck = { radii = { 800, 1600, 2400 } } }
	underdeck = { on = true, night = true, name = "under-deck fill", class = "PointLight",
		color = RGB(255, 214, 170), intensity = 40, radius = 12 * guim, height = 700,
		radii = { 9 * guim, 17 * guim, 25 * guim } },
}
local hub_structure_order = { "portal", "pit", "rim", "floor", "crown", "underdeck" }

-- THE NIGHT SCHEDULE IS VANILLA'S, NOT A TIMER OF OURS. Read on build 1.1.0.403908 from that
-- build's archived tree, `B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.0.403908\Src`:
--   * The only dusk/dawn edge the game itself uses is `Msg("LightmodelChange", map, view, lm,
--     time, prev_lm, ...)` (`CommonLua/Classes/Lightmodel.lua:1022`), whose handler in
--     `Lua/NightLightObjects.lua:250-259` compares `prev_lm.night` to `lm.night` and calls
--     `NightLightsOn` / `NightLightsOff`. We register an ADDITIVE handler on the same Msg
--     (FIX_POLICY §1 technique 2), so this light switches with every other building's.
--   * The day/night truth those two publish is the MapVar `map.NightLightsState`
--     (`Lua/NightLightObjects.lua:22`, written at `:337` and `:388`, seeded at `:25-28`); it is
--     what `NightLightObject:IsNightLightPossible` reads at `:91-93`, and what unrelated systems
--     read directly (`Lua/AutoRemoveObj.lua:7`, `Lua/Mysteries/Fireflies.lua:655`). There is no
--     `IsNightTime()` and no `night_light` property on Light/PointLight/SpotLight
--     (`CommonLua/Classes/Light.lua:11,278,453`).
--   * We deliberately read ONLY the map half of `:92`, not the per-object `gofNightLightsEnabled`
--     flag: `Building` clears it at GameInit and re-derives it from `AreNightLightsAllowed`
--     (`Lua/Buildings/Building.lua:507-511`, `:1371-1393`), so a hub whose flag happened to be
--     clear would never show the light. A stopped hub already destroys its lights here anyway.
--   * Vanilla's own per-light "night only" data is `NightLightSpecs[entity][state]`, parsed from
--     `Autolight`/`L` SPOT ANNOTATIONS on the entity (`Lua/NightLightObjects.lua:430-542,:544-570`),
--     not from Lua — our imported body carries none, so that route needs a bake we do not have.
--     And `NightLightPointLight`/`NightLightSpotLight` (`:68-84`) are the wrong class to attach by
--     hand: `NightLightsOn` starts by destroying every `NightLightLight` attach (`:335`, `:187-189`).
--     So: vanilla classes, vanilla Msg, vanilla state — and no thread of our own.
-- OnMsg is additive and the order between handlers is NOT guaranteed, so when our handler runs it
-- passes the transition it was told rather than re-reading a MapVar vanilla may not have set yet.
-- The Msg is per-map and the rebuild walks every map, so the override is keyed by the map it came
-- from; a hub on any other map reads its own MapVar as usual.
local hub_night_forced = nil -- { map = <the map the Msg named>, night = <bool> }, only while it runs
local function hub_is_night(self)
	local map = self.GetMap and self:GetMap() or nil
	if hub_night_forced and hub_night_forced.map == map then return hub_night_forced.night end
	return (type(map) == "table" and map.NightLightsState) and true or false
end

-- Model numbers, hub-local centimetres, from the production run at assets `24a98b7` (spec §9).
-- z is measured from the hub's base, NOT from the 8.00 m train deck the arm lights use.
local portal_rim_z0, portal_rim_r0 = 730, 3353  -- the flush rim tube's foot, and
local portal_rim_z1, portal_rim_r1 = 1432, 2868 -- its crown: the tube is laid on the dome, so
                                                -- its radius falls as it rises (linear here, an
                                                -- approximation of the dome's curve).
local portal_crown, portal_half = 1312, 325     -- the clear opening: 13.125 m crown, 6.50 m wide
local portal_inset = 40                         -- sit 0.40 m inside the rim line
-- (v, z) round one mouth, v sideways off the portal's line: the crown, two shoulders, two jambs.
local hub_portal_rim_points = {
	{ v = 0, z = portal_crown - portal_inset },
	{ v = portal_half - portal_inset, z = 1125 },
	{ v = -(portal_half - portal_inset), z = 1125 },
	{ v = portal_half - portal_inset, z = 860 },
	{ v = -(portal_half - portal_inset), z = 860 },
}
local function portal_rim_radius(z)
	local t = Clamp(z, portal_rim_z0, portal_rim_z1) - portal_rim_z0
	return portal_rim_r0 + MulDivRound(t, portal_rim_r1 - portal_rim_r0, portal_rim_z1 - portal_rim_z0)
end
local pit_centre_distance, pit_centre_angle = 1155, 30 * 60 -- 11.547 m on the 30 degree midline
local pit_kerb_radius, pit_kerb_z, pit_posts = 590, 60, 6   -- mouth r 5.75 m, kerb 0.30 x 0.60
local pit_spot_z = 30                                        -- the Pitrim spot sits on the kerb top
local ring_rim_radius, ring_rim_z = 3610, 690               -- 0.50 m outside the wall's 35.60 m
local floor_edge_radius, floor_edge_z = 3060, 45            -- the blue strip just inside r 30.75

local function clear_hub_lights(self)
	for _, class in ipairs(hub_light_classes) do
		for _, light in ipairs(self:GetAttaches(class) or empty_table) do
			if IsValid(light) then DoneObject(light) end
		end
	end
end

local function place_hub_light(self, variant, x, y, z, spot_name)
	local light = PlaceObjectIn(variant.class, self:GetMap())
	light:SetDetailClass("Essential") -- a light's default, Eye Candy, drops out at low detail
	light:SetColor(variant.color)
	light:SetIntensity(variant.intensity)
	light:SetAttenuationRadius(variant.radius)
	if variant.class == "SpotLight" then
		light:SetConeInnerAngle(variant.inner)
		light:SetConeOuterAngle(variant.outer)
	end
	self:Attach(light, self:GetSpotBeginIndex(spot_name or "Origin"))
	light:SetAttachOffset(point(x, y, z))
	if variant.class == "SpotLight" then
		-- UNVERIFIED: assumes a spot shines along its own +X; a quarter turn about Y aims it down.
		light:SetAttachAxis(axis_y)
		light:SetAttachAngle(90 * 60)
	end
	DeleteOnLoadGame(light)
	return light
end

-- hub -> { arm = {lights}, portal = {...}, pit = {...}, rim = {...}, floor = {...} }. A plain
-- weak-keyed local: no field on the hub, nothing that can reach a save.
local hub_light_sets = setmetatable({}, weak_keys_meta)

-- Console/test read-out of what is standing right now.
function Floor.HubLightSet(hub)
	return hub_light_sets[hub]
end

-- One hex outward in the hub's own frame, and its length, for a hex direction.
local function hub_arm_axis(direction)
	local x0, y0 = HexToWorld(0, 0)
	local q, r = HexRotate(1, 0, direction)
	local hx, hy = HexToWorld(q, r)
	local ax, ay = hx - x0, hy - y0
	return ax, ay, point(ax, ay):Len()
end

-- u outward from the centre, v sideways, both in the arm's own frame.
local function hub_arm_point(ax, ay, length, u, v)
	return MulDivRound(ax, u, length) - MulDivRound(ay, v, length),
		MulDivRound(ay, u, length) + MulDivRound(ax, v, length)
end

local function place_hub_structure_lights(self, sets)
	local total = 0
	local night = hub_is_night(self)
	for _, key in ipairs(hub_structure_order) do
		local family = hub_structure_lights[key]
		local list = {}
		-- A `night` family is simply NOT PLACED by day, and is built at dusk: the same
		-- destroy-rather-than-dim idiom the rest of this block uses, and the same one vanilla
		-- uses (`NightLightOffAttaches` destroys, NightLightObjects.lua:187-189).
		if family and family.on and (not family.night or night) then
			if key == "crown" then
				-- One light, on the dome's axis: the six ribs meet at x = y = 0. place_hub_light
				-- aims a SpotLight straight down with exactly the arm spots' assumption (+X turned
				-- a quarter about Y), so this reuses that aim rather than making a second one.
				list[#list + 1] = place_hub_light(self, family, 0, 0, family.height)
			elseif key == "underdeck" then
				-- Straight down each arm's own axis: `hub_arm_point` with v = 0 is a point `u` cm out
				-- from the centre along that arm, the same helper the arm lights and the portal rims
				-- use. No spot and no fixture, so there is nothing to aim or to hang them from.
				for direction = 0, 5 do
					local ax, ay, length = hub_arm_axis(direction)
					for _, u in ipairs(family.radii or empty_table) do
						local x, y = hub_arm_point(ax, ay, length, u, 0)
						list[#list + 1] = place_hub_light(self, family, x, y, family.height)
					end
				end
			elseif key == "portal" then
				for direction = 0, 5 do
					local ax, ay, length = hub_arm_axis(direction)
					for _, p in ipairs(hub_portal_rim_points) do
						local x, y = hub_arm_point(ax, ay, length, portal_rim_radius(p.z), p.v)
						list[#list + 1] = place_hub_light(self, family, x, y, p.z)
					end
				end
			elseif key == "pit" then
				-- Owner, 2026-09-22: placed from the generator's 30-degree midline these landed on
				-- plain floor (the generator's axes are turned against the entity's). The imported
				-- Pitrim spot IS the mouth's centre at the kerb top, so the six hang on it; the
				-- hexagon does not care about the spot's own 60-degree turn. A stand-in entity
				-- without the spot keeps the computed centre.
				local on_spot = self:HasSpot("Pitrim")
				local centre = on_spot and point(0, 0) or Rotate(point(pit_centre_distance, 0), pit_centre_angle)
				local z = on_spot and pit_kerb_z - pit_spot_z or pit_kerb_z
				for i = 0, pit_posts - 1 do
					local post = centre + Rotate(point(pit_kerb_radius, 0), (30 + MulDivRound(360, i, pit_posts)) * 60)
					list[#list + 1] = place_hub_light(self, family, post:x(), post:y(), z, on_spot and "Pitrim" or nil)
				end
			else -- the two concentric rings, sparse points every `step` degrees
				local radius = key == "rim" and ring_rim_radius or floor_edge_radius
				local z = key == "rim" and ring_rim_z or floor_edge_z
				for angle = 0, 359, Max(1, family.step or 10) do
					local p = Rotate(point(radius, 0), angle * 60)
					list[#list + 1] = place_hub_light(self, family, p:x(), p:y(), z)
				end
			end
		end
		sets[key] = list
		total = total + #list
		print(string.format("[TrainHubDev] structure lights: %s %s, %d lights (intensity %d, radius %d cm)",
			family.name, family.on and "ON" or "OFF", #list, family.intensity, family.radius))
		if family and family.night then
			local cr, cg, cb = 0, 0, 0
			if type(GetRGB) == "function" then cr, cg, cb = GetRGB(family.color) end
			print(string.format("[TrainHubDev] structure lights: %s follows the VANILLA night schedule (OnMsg.LightmodelChange -> map.NightLightsState, NightLightObjects.lua:250-259, :22 on build 1.1.0.403908); it is %s now, so it is %s -- hanging at z %d cm, colour %d,%d,%d, cone %d/%d",
				family.name, night and "NIGHT" or "DAY", night and "LIT" or "NOT PLACED",
				family.height or 0, cr or 0, cg or 0, cb or 0, family.inner or 0, family.outer or 0))
		end
	end
	return total
end

local function set_hub_lights_working(self, working)
	clear_hub_lights(self)
	hub_light_sets[self] = nil
	if not working then return end
	local deck = train_deck_height(self)
	local tune = Floor.HubLightTune or empty_table
	local sets = { arm = {} }
	local total = 0
	for direction = 0, 5 do
		local key = hub_light_arms[direction]
		local variant = tuned_variant(hub_light_variants[key])
		if variant then
			local ax, ay, length = hub_arm_axis(direction)
			local off = variant.side or 0
			local count = 0
			for u = hub_line_first, hub_line_last, variant.spacing do
				local v = hub_line_v(u)
				for side = -1, v > 0 and 1 or -1, 2 do
					-- `side` pushes the light off the line: a pair moves apart, and the single
					-- centre run (v == 0, inside 40 m) moves to one side, the -1 side.
					local x, y = hub_arm_point(ax, ay, length, u, side * (v + off))
					sets.arm[#sets.arm + 1] = place_hub_light(self, variant, x, y, deck + variant.height)
					count = count + 1
				end
			end
			total = total + count
			local bearing = (CalcOrientation(point(0, 0), point(ax, ay)) + self:GetAngle()) % (360 * 60) / 60
			print(string.format("[TrainHubDev] lights: arm %d, %s = %s \"%s\" (%s), %d lights, engine bearing %d deg",
				direction, hub_light_arm_names[direction], key, variant.name, variant.class, count, bearing))
		end
	end
	local cr, cg, cb = 0, 0, 0
	if type(GetRGB) == "function" then cr, cg, cb = GetRGB(tune.color) end
	print(string.format("[TrainHubDev] lights: arm tune intensity %d, side %d cm, height %d cm, radius %d cm, cone %d/%d, colour %d,%d,%d",
		tune.intensity or 0, tune.side or 0, tune.height or 0, tune.radius or 0, tune.inner or 0, tune.outer or 0,
		cr or 0, cg or 0, cb or 0))
	local structure = place_hub_structure_lights(self, sets)
	hub_light_sets[self] = sets
	print(string.format("[TrainHubDev] lights: %d placed (%d arm + %d structure); a stopped hub destroys them all",
		total + structure, total, structure))
end

function SMROptInTrainHubBase:InitHubLights()
	set_hub_lights_working(self, self.working)
end

local function reinit_hub_lights()
	AllMapsForEach("map", "SMROptInTrainHubBase", function(hub) hub:InitHubLights() end)
end

-- SMROptInTrainFloor.SetHubLightTune("intensity", 80) or SetHubLightTune{ side = 150, radius = 700 }.
function Floor.SetHubLightTune(field, value)
	if type(field) == "table" then
		for k, v in pairs(field) do Floor.HubLightTune[k] = v end
	elseif field ~= nil then
		Floor.HubLightTune[field] = value
	end
	reinit_hub_lights()
end

-- SMROptInTrainFloor.SetHubStructureLights{ portal = { on = false }, rim = { intensity = 50 } }.
function Floor.SetHubStructureLights(changes)
	for family, fields in pairs(changes or empty_table) do
		local entry = hub_structure_lights[family]
		if entry then
			for k, v in pairs(fields) do entry[k] = v end
		else
			print(string.format("[TrainHubDev] structure lights: no family \"%s\"", tostring(family)))
		end
	end
	reinit_hub_lights()
end

-- Dusk and dawn. Additive, beside vanilla's own handler on the same Msg
-- (NightLightObjects.lua:250-259, build 1.1.0.403908) and comparing the same two booleans, so the
-- crown light comes on and goes off on exactly the game's edge. Only a real transition rebuilds,
-- so a storm or any other lightmodel swap inside one phase costs nothing.
function OnMsg.LightmodelChange(map, view, lm, time, prev_lm)
	local was = prev_lm and prev_lm.night and true or false
	local now = lm and lm.night and true or false
	if was == now then return end
	hub_night_forced = { map = map, night = now }
	reinit_hub_lights()
	hub_night_forced = nil
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
	-- Owner, 2026-09-22: the pad's platform model goes too; the drone pit in the floor plate
	-- is the launch and landing place now. Saves from before carry the platform attached, so
	-- the initializer removes it instead of placing it.
	for _, platform in ipairs(self:GetAttaches("RechargeStationPlatform") or empty_table) do
		if IsValid(platform) then DoneObject(platform) end
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
	self:InitHubSidingGlass()
	self:InitHubLights()
	top_up_hub_drones(self)
	place_hub_markers(self)
	Floor.Reconcile(self)
	self:InitHubTrackWork()
end

function SMROptInTrainHubBase:OnSetWorking(working)
	if working then
		top_up_hub_drones(self)
		self:SetWaitingDronesIdle()
	end
	self:NotifyWorkingChanged(self.connected_task_requesters)
	set_hub_reactor_working(self, working)
	set_hub_glass_working(self, working)
	set_hub_lights_working(self, working)
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
	-- Build 4: the track-work tick (jobs, the remote stations, the fleet), in every hub state.
	self:HubTrackWorkTick()
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
	hub:InitHubSidingGlass()
	hub:InitHubLights()
	Floor.Reconcile(hub)
end

function OnMsg.LoadGame()
	AllMapsForEach("map", "SMROptInTrainHubBase", heal_after_load)
end

-- ===========================================================================
-- TRACK WORK (build 4, drones chain link 4, 2026-09-23). The hub repairs broken track on its
-- own network from its own stock, without player action: a break becomes a pending job, the
-- hub pays the site's OUTSTANDING cost at the cheaper (SafeTransport) rate whether or not that
-- tech is researched, and completes the site at a deadline in game time. A vanilla Wasp flies
-- out and back for the look of it (30_TrainHubDrones.lua); the DEADLINE IS THE ONLY AUTHORITY
-- and the flight is advisory (DESIGN.md End state 2; owner, 2026-09-19 and 2026-09-23).
-- Every source line below was read on the INSTALLED build 25390750 / 1.1.1.405907 from
-- B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src.
--
-- SAVE CONTRACT (FIX_POLICY ban 1; inventory row 11). ONE persisted field, on hub objects,
-- `false` until the hub first uses it:
--   SMROptIn_track_work = {
--     repair = <bool>,             -- the player's track-repair toggle (infopanel), default true
--     jobs = { {                   -- the pending list; build 5 adds kind = "build" here and
--       kind = "repair",           --   so needs NO second persisted name
--       site = <ConstructionGroupLeader>, -- the break's repair group (Track.lua repair_cgs[i][1])
--       el = <TrackGridElement>,   -- the first broken original, the flight's target
--       track = <TrackBase>,
--       found = <game ms>, started = <game ms>|false, deadline = <game ms>|false,
--       drone = <FlyingDrone>|false,          -- the visual, adopted after a load
--       held = { [res] = { req = <supply request>, amount = n } }|false, -- the stock claim
--       waiting = <resource id>|false }, ... } }
--   Plain data and vanilla object references only: no function, no thread, no closure. A save
--   loaded without this mod carries an inert table on a mod building it cannot load anyway
--   (FIX_POLICY section 0). A job whose site is gone (drones finished it, or it was cancelled)
--   is dropped silently on the next tick (owner: whichever finishes first wins).
--
-- WHERE THE WORK RUNS: inside vanilla's own per-building update thread, BuildingUpdate every
-- building_update_time (5 s game), which runs while the object is valid whatever its working
-- state (Building.lua:811-826 StartUpdateThread; a watchdog restarts it, :832-840). No thread
-- of ours, nothing captured by a save (FIX_POLICY section 3a, layer 3 shape). The tick:
--   1. once after a load: adopt each job's surviving Wasp (F.Adopt), then sweep strays;
--   2. the hub-rooted physical graph (below), and every Station on it gets this hub as a
--      command centre (owner, 2026-09-23), the same AddCommandCenter call vanilla makes from
--      its hex-circle sweep (DroneControl.lua:466-468) with connectivity as the criterion;
--   3. new breaks on the graph become jobs (Track.lua repair_cgs, filled by BreakTracks,
--      Meteors.lua:713-727, before Msg("TrackBroken", track, true));
--   4. each job: dropped if its site is gone; dispatched when the switch, the toggle, a slot
--      and the stock allow; completed at its deadline; given a Wasp while it flies;
--   5. the fleet: vanilla's own load word (DroneControl.lua:1092-1107) picks a tier.
--
-- REACHABILITY (owner, 2026-09-19; enforcement moved to dispatch, 2026-09-23): anything a
-- repair drone following the track could reach, never an isolated network. Engine flight can
-- physically reach anything, so dispatch refuses a target off the graph. The graph is
-- hub-rooted, with visited nodes and visited tracks, over PHYSICAL edges: a connector element's
-- track (TrainTransport.lua:57-66 ForEachConnectorElement), the track's start/end station
-- owners (Track.lua:194-199, which never test construction), and a tunnel mouth's reciprocal
-- linked_obj (Tunnel.lua:8, :27-28; TrackTunnel.lua:7-9). ForEachConnectedTrack is NOT used:
-- it calls GetDestStation, which returns false while any element is under construction
-- (Track.lua:339-341), so it hides exactly the broken edge and everything beyond it (EF-114).
-- A track is an edge only while every unfinished element of it is a repair site over a broken
-- original (TrackElement.lua:139-152 `broken`); unfinished NEW track is build 5's.
--
-- COMPLETION (EF-112): the live repair group's leader, ConstructionGroupLeader:Complete
-- (ConstructionSite.lua:2671-2718), which calls each member's TrackConstructionSite:Complete
-- (TrackElement.lua:860-943): the hidden original is shown again, the track reconnects, and
-- Msg("TrackBroken", track, false) fires. No funding check sits on that path, so the hub pays
-- first. The OUTSTANDING cost is what the leader's demand requests still ask for
-- (ConstructionSite.lua:703-718 construction_resources; :742 GetActualAmount is "remaining");
-- delivered cubes are already consumed, so nothing is paid twice. The break costs
-- (#elements)*100 % of one element, halved by SafeTransport (Track.lua:651-656), so the hub's
-- rate is the site's remaining demand times 50 % without the tech and 100 % with it.
-- Paying: the claim taken at dispatch (below) is released and AddResource(-n) lowers the stock
-- (MultiResourceCubeVisuals.lua:422-435), which also runs the reserve's Reconcile.
--
-- THE STOCK CLAIM: at dispatch the hub claims the cost on its own supply requests through the
-- engine's reservation, request:AssignUnit(n), exactly as 10_TrainFloor.lua's reserve does, so
-- trains, drones and shuttles cannot take it before the deadline; the claim is recorded in the
-- job with its request, because vanilla replaces a supply request when a resource is removed
-- and re-added (10_TrainFloor.lua header); a claim on a dead request is forgotten, never
-- released onto the new one. The maintenance reserve is already claimed, so "free" stock is
-- Min(target, actual) and the repair never dips below the reserve (DESIGN.md End state 4).
--
-- THE FLEET (owner, 2026-09-23): five vanilla Wasps standing idle, launched more as work
-- rises and recalled as it falls; thirty is the ceiling for fleet and repair flights together.
-- They are FlyingDrone objects in hub.drones under vanilla's own AI (Idle draws tasks from
-- their own command_center only, Drone.lua:704-706; past distance_to_provoke_go_home_cmd Idle
-- sends them home, :709-711). A recall takes only an idle drone carrying nothing, removes it
-- through DroneControl:KillDrone (DroneControl.lua:729-733, which asserts hub.drones
-- membership) when it is near, and sends it home with the stock GoHome first when it is not.
--
-- A DESTROYED OR SALVAGED HUB DESPAWNS ITS DRONES (owner, 2026-09-22): Finalize below runs
-- from DroneControl:Done and :OnDestroyed (:341-352) and nowhere else; it drops every carried
-- cube on the ground (Drone:DropCarriedResource, Drone.lua:2098-2137, the same call
-- DespawnAtHub makes first, :2169) and removes each drone, fleet and flight alike, before
-- vanilla's Finalize would orphan them (:315-327). A save from between the two states heals
-- on load: the first tick sweeps any Wasp whose controller is a destroyed hub.
--
-- NO FREE-DRONE LEAK: FlyingDrone declares its own CanBeControlled (FlyingDrone.lua:144-146,
-- chaining Drone's, Drone.lua:2207-2209), so the wrap installs on the declaring class (F64):
-- the original is always called; false is returned only when the live command_center is a
-- train hub. Both reassign buttons (Drone.lua:2020-2023, :2048-2052) and the rocket's cargo
-- pick (CargoTransporter.lua:425) read it, and so does CanTakeTaskOnTheWay (:621-637), so a
-- repair drone never grabs a task on the way; the hub's FindTask still assigns it from Idle.
-- ===========================================================================

local TRACK_WORK = "SMROptIn_track_work"

-- The owner's dials (link 5 moves them by eye), from the console:
--   SetHubRepairTune("Standing", 5)        SetHubRepairTune{ StepMedium = 5, StepHigh = 10 }
--   SetHubRepairTune("WaspPalette", "P4")  -- the reactor's variants, per-object (spec §9 ask)
-- Nothing here is saved; a restart returns to these defaults.
Floor.HubRepairTune = {
	-- the deadline = LaunchTime + straight-line distance / Speed + WorkTime
	-- (game ms; Speed in units per game second; a hex is 1000 units)
	-- Owner, 2026-09-24 (option A): the repair takes the Wasp's own time, so completion lands
	-- while it works at any drone speed. Measured in the L5 sitting at move_speed 8960: engine
	-- legs flew 7296-7465 units/s (81-83 %), and the pit launch took 3.9 s.
	Speed = false,          -- false = a hub Wasp's live move_speed (drone dials and techs included) x SpeedPercent
	SpeedPercent = 80,      -- the share of move_speed an engine leg achieves; a little under measured, so it arrives first
	LaunchTime = 4000,      -- the pit rise and the exit, before the leg (measured 3944 ms)
	FlightGrace = 100,      -- percent of the predicted trip a live Wasp may run past the deadline before the fallback completes anyway
	WorkTime = false,       -- false = the flight's WorkTime + 2000 (both work animations)
	Visual = true,          -- fly a Wasp for each repair; false = deadlines only (a probe dial)
	-- the fleet (owner, 2026-09-23): five standing idle; more as vanilla's load reads medium/high
	Standing = 5,
	StepMedium = 5,
	StepHigh = 10,
	MaxDrones = 30,         -- fleet and repair flights together; the panel's "/ 30"
	RecallDelay = 60000,    -- game ms the count must stay above its target before a recall starts
	RecallStep = 15000,     -- game ms between recalls; one idle, empty-handed drone each
	RecallRadius = 6000,    -- units; an idle drone this close is removed, a farther one is sent home first
	WaspPalette = false,    -- false = vanilla's Wasp look; "P1".."P4" = the reactor's variants above
}

local function live(o)
	return IsValid(o) and not o.destroyed and not IsBeingDestructed(o)
end

local function is_hub(o)
	return IsValid(o) and IsKindOf(o, "SMROptInTrainHubBase")
end

-- A meteor damages the hub, never destroys it (owner, 2026-09-24: "Domes never get destroyed via
-- a meteor strike, they just get damaged and need repaired and our hub is a dome sized building").
-- The large meteor destroys any Station outright (Meteors.lua:927-932 on 1.1.1.405907) through
-- DestroyBuildingImmediate with reason "meteor"; the small one malfunctions it (:783-786). A hub
-- hit by either now malfunctions and waits for repair. `indestructible` would also block the
-- player's demolish (Building.lua:925), so the chain is scoped to the meteor reason alone; every
-- other building and every other cause gets vanilla's answer.
local vanilla_destroy_building_immediate = DestroyBuildingImmediate
function DestroyBuildingImmediate(bld, params, ...)
	if is_hub(bld) and not bld.destroyed and type(params) == "table" and params.reason == "meteor" then
		PlayFX("MeteorMalfunction", "start", bld)
		bld:SetMalfunction()
		return false
	end
	return vanilla_destroy_building_immediate(bld, params, ...)
end

local function flight_api()
	local F = rawget(_G, "SMROptInHubFlight")
	return type(F) == "table" and type(F.Create) == "function" and F or nil
end

-- The persisted record, created on first use. Reading never creates it (see HubRepairLine).
local function track_work(self)
	local record = rawget(self, TRACK_WORK)
	if type(record) ~= "table" then
		record = { repair = true, jobs = {} }
		rawset(self, TRACK_WORK, record)
	end
	if type(record.jobs) ~= "table" then record.jobs = {} end
	if record.repair == nil then record.repair = true end
	return record
end

-- The record's jobs without creating the record: for readers (UI, console).
local function track_jobs(self)
	local record = rawget(self, TRACK_WORK)
	return type(record) == "table" and record.jobs or empty_table, record
end

-- Ephemeral: flight records per job, and per-hub fleet timers. Weak-keyed, never saved.
local flights = setmetatable({}, weak_keys_meta)
local fleet_state = setmetatable({}, weak_keys_meta)
local loaded_pending = false

-- ---------------------------------------------------------------------------
-- The graph.
-- ---------------------------------------------------------------------------

-- An existing physical edge: every unfinished element is a repair site over a broken original.
local function physical_track(track)
	if not IsValid(track) then return false end
	for _, el in ipairs(track.elements_under_construction or empty_table) do
		if not IsValid(el.broken) then return false end
	end
	return true
end

-- nodes[obj] = true for every station and tunnel mouth reachable from this hub; tracks[track] =
-- true for every physical edge seen (false for an unfinished one, so it is not re-walked).
function SMROptInTrainHubBase:HubTrackGraph()
	local nodes, tracks = { [self] = true }, {}
	local queue, cursor = { self }, 1
	while queue[cursor] do
		local node = queue[cursor]
		cursor = cursor + 1
		if IsValid(node) and node.ForEachConnectorElement then
			node:ForEachConnectorElement(function(el)
				local track = el and el.track_obj
				if not IsValid(track) or tracks[track] ~= nil then return end
				tracks[track] = physical_track(track)
				if not tracks[track] then return end
				local a, b = track:GetStartStation(), track:GetEndStation()
				local other = (a == node) and b or a
				if IsValid(other) and not IsBeingDestructed(other) and not nodes[other] then
					nodes[other] = true
					queue[#queue + 1] = other
				end
			end)
		end
		local far = IsValid(node) and node.linked_obj
		if IsKindOf(node, "TrackTunnelBase") and IsValid(far) and far.linked_obj == node and not nodes[far] then
			nodes[far] = true
			queue[#queue + 1] = far
		end
	end
	return nodes, tracks
end

-- Every Station on the graph gets this hub as a command centre (owner approved, 2026-09-23):
-- the check a far station makes is list membership, not distance (Building.lua:853-858
-- IsOutsideCommandRange; RequiresMaintenance.lua:297-300 GetMaintenanceStuckReason), so this
-- clears "Too far from working Drone controller" and "No Drone Hub in range" out there, and
-- vanilla's own maintenance machinery then sends the fleet. A station that left the graph and
-- is outside the radius loses the hub again; one inside the radius is vanilla's to keep.
--
-- ONLY THE MAINTENANCE REQUESTS join the hub out there (owner, 2026-09-23, in play: with every
-- request joined, the fleet began balancing resources between the network's stations, which
-- the track-work ruling forbids beyond the radius). A controller asks the building before it
-- files each request, `building:ShouldAddRequestToCommandCenter(request, center, res)`
-- (DroneControl.lua:742, :754), declared once on TaskRequester as `return_true`
-- (_TaskRequest.lua:209-210); Station does not declare it. The chained override on Station
-- below answers false for a train hub that is out of range unless the request is the station's
-- maintenance material or maintenance work request (RequiresMaintenance.lua), and hands every
-- other case to the captured original. A station inside the radius keeps vanilla's full service.
local function register_remote_stations(self, nodes)
	if not self.are_requesters_connected then return end
	for node in pairs(nodes) do
		if node ~= self and IsValid(node) and IsKindOf(node, "Station") and node.auto_connect
			and node.AddCommandCenter and not table.find(node.command_centers or empty_table, self) then
			node:AddCommandCenter(self)
		end
	end
	local stale
	for _, o in ipairs(self.connected_task_requesters or empty_table) do
		if IsValid(o) and IsKindOf(o, "Station") and not nodes[o] and not self:IsInWorkRange(o) then
			stale = stale or {}
			stale[#stale + 1] = o
		end
	end
	for _, o in ipairs(stale or empty_table) do o:RemoveCommandCenter(self) end
end

local vanilla_should_add_request = TaskRequester.ShouldAddRequestToCommandCenter
function Station:ShouldAddRequestToCommandCenter(request, command_center, res_id)
	if is_hub(command_center) and command_center ~= self and not command_center:IsInWorkRange(self)
		and request ~= self.maintenance_resource_request and request ~= self.maintenance_work_request then
		return false
	end
	return vanilla_should_add_request(self, request, command_center, res_id)
end

-- A station registered before the filter above existed carries every request: once per load,
-- every out-of-range station on the graph is re-registered so the filter applies.
local function refilter_remote_stations(self)
	local again = {}
	for _, o in ipairs(self.connected_task_requesters or empty_table) do
		if IsValid(o) and IsKindOf(o, "Station") and not self:IsInWorkRange(o) then again[#again + 1] = o end
	end
	for _, o in ipairs(again) do
		o:RemoveCommandCenter(self)
		o:AddCommandCenter(self)
	end
end

-- ---------------------------------------------------------------------------
-- Jobs: discovery, cost, the claim, dispatch, completion.
-- ---------------------------------------------------------------------------

local function job_for_site(jobs, leader)
	for _, job in ipairs(jobs) do
		if job.site == leader then return job end
	end
end

-- Track.lua's repair_cgs holds one group per break event; cg[1] is its leader, cg[2..] its sites.
local function discover_breaks(self, record, tracks, now)
	for track, physical in pairs(tracks) do
		if physical then
			for _, cg in ipairs(track.repair_cgs or empty_table) do
				local leader = cg[1]
				if live(leader) and not job_for_site(record.jobs, leader) then
					local member = cg[2]
					local el = IsValid(member) and IsValid(member.broken) and member.broken or false
					record.jobs[#record.jobs + 1] = { kind = "repair", site = leader, el = el, track = track,
						found = now, started = false, deadline = false, drone = false, held = false, waiting = false }
				end
			end
		end
	end
end

local function repair_rate()
	local colony = rawget(_G, "UIColony")
	local researched = colony and colony.IsTechResearched and colony:IsTechResearched("SafeTransport")
	return researched and 100 or 50
end

-- { res = amount } the site still asks for, at the hub's rate. Empty under Free Construction.
local function outstanding_cost(leader)
	local cost, rate = {}, repair_rate()
	for res, req in pairs(leader.construction_resources or empty_table) do
		local remaining = req:GetActualAmount()
		if remaining > 0 then cost[res] = MulDivRound(remaining, rate, 100) end
	end
	return cost
end

-- Unclaimed stock: the standing reserve is already claimed, so this never dips into it.
local function stock_free(self, res)
	local req = self.supply and self.supply[res]
	if not req then return 0, nil end
	return Max(0, Min(req:GetTargetAmount(), req:GetActualAmount())), req
end

local function release_held(self, job)
	for res, entry in pairs(job.held or empty_table) do
		if entry.req and self.supply and entry.req == self.supply[res] and (entry.amount or 0) > 0 then
			entry.req:UnassignUnit(entry.amount, false)
		end
	end
	job.held = false
end

-- All or nothing: the claim is taken only when every resource covers its share.
local function hold_cost(self, job, cost)
	for res, amount in pairs(cost) do
		if amount > 0 and stock_free(self, res) < amount then return false, res end
	end
	local held = {}
	for res, amount in pairs(cost) do
		if amount > 0 then
			local _, req = stock_free(self, res)
			if req and req:AssignUnit(amount) then held[res] = { req = req, amount = amount } end
		end
	end
	job.held = held
	return true
end

-- A hub Wasp's live move_speed carries the label modifiers every Wasp shares (drone speed dials,
-- techs); with none standing, the class base. Scaled to what an engine leg achieves.
local function repair_speed(self)
	local tune = Floor.HubRepairTune
	if tune.Speed then return tune.Speed end
	local speed
	for _, d in ipairs(self and self.drones or empty_table) do
		if IsValid(d) and type(d.move_speed) == "number" and d.move_speed > 0 then speed = d.move_speed break end
	end
	speed = speed or FlyingDrone.move_speed or 1600
	return Max(1, MulDivRound(speed, tune.SpeedPercent, 100))
end

local function repair_work_time()
	local F = flight_api()
	return Floor.HubRepairTune.WorkTime or ((F and F.WorkTime or 5000) + 2000)
end

local hub_notification_id = "SMROptInTrackRepair"

-- Text-only, sixty real seconds, the vanilla "TrainRefabbed" preset's shape. Runtime-created
-- presets are not put in their map by PlaceObj, so the map entry is written here. A saved
-- notification whose preset the game no longer knows is purged at load (Notifications.lua:
-- 429-441), so a save without this mod carries nothing of it.
local function ensure_hub_notification()
	local presets = rawget(_G, "NotificationPresets")
	if type(presets) ~= "table" or presets[hub_notification_id] then return end
	local ok, preset = pcall(PlaceObj, "NotificationPreset", {
		Expiration = 60000,
		GameTime = false,
		NotificationTemplate = "NotificationImportant",
		RolloverTitle = T(909018002013, "Train hub"),
		Title = T(909018002014, "Repair drone dispatched"),
		TitlePl = T(909018002014, "Repair drone dispatched"),
		group = "Default",
		id = hub_notification_id,
	})
	if ok and preset then presets[hub_notification_id] = preset end
end

local function notify_dispatch(self, job, now)
	if type(AddOnScreenNotification) ~= "function" then return end
	ensure_hub_notification()
	local presets = rawget(_G, "NotificationPresets")
	if type(presets) ~= "table" or not presets[hub_notification_id] then return end
	-- No ETA (owner, 2026-09-23): game minutes read as seconds to a player, and real seconds
	-- change with the game speed.
	AddOnScreenNotification(hub_notification_id, nil, {
		override_text = T(909018002016, "Repair drone dispatched"),
		expiration = 60000,
	}, IsValid(job.el) and { job.el } or nil, self:GetMap())
end

-- The switch (ui_working) and not destroyed: NEVER IsWorking, which a malfunction or a dead
-- grid clears (owner, 2026-09-22: a malfunctioned or unpowered hub still dispatches).
local function can_dispatch(self, record)
	return record.repair ~= false and self.ui_working and not self.destroyed and true or false
end

-- Drone coverage for the sites a hub is repairing (owner, 2026-09-24: "Can't we make the game think
-- its covered as long as its connected to the hub?"). Vanilla calls a site uncovered when no
-- controller in its command_centers can command drones (ConstructionSite:IsOutsideCommandRange,
-- ConstructionSite.lua:3029 on 1.1.1.405907). Only the site's warning (:2038) and the no-controller
-- sign and notification (Building:ShouldShowNoCCSign, :860; BaseBuilding:UpdateNoDroneServiceNotification)
-- read it, so the answer is display-only. A site counts as covered while it is a job of a hub
-- whose switch and track-repair toggle are on. Coverage is refreshed through vanilla's own
-- updaters when it starts or stops, because they are event-driven.
local covered_sites = setmetatable({}, weak_keys_meta) -- group leader -> hub

local function refresh_coverage(leader)
	for _, site in ipairs(leader.construction_group or { leader }) do
		if live(site) then
			if site.UpdateNoCCSign then site:UpdateNoCCSign() end
			if site.UpdateNoDroneServiceNotification then site:UpdateNoDroneServiceNotification() end
		end
	end
end

local function update_coverage(self, record)
	local covering, now_set = can_dispatch(self, record), {}
	for _, job in ipairs(record.jobs) do
		if job.kind == "repair" and live(job.site) then now_set[job.site] = true end
	end
	for site, hub in pairs(covered_sites) do
		if hub == self and not (covering and now_set[site]) then
			covered_sites[site] = nil
			if live(site) then refresh_coverage(site) end
		end
	end
	if covering then
		for site in pairs(now_set) do
			if covered_sites[site] ~= self then
				covered_sites[site] = self
				refresh_coverage(site)
			end
		end
	end
end

local vanilla_site_outside_command_range = ConstructionSite.IsOutsideCommandRange
function ConstructionSite:IsOutsideCommandRange(...)
	local leader = self.construction_group and self.construction_group[1] or self
	local hub = covered_sites[leader]
	if hub and live(hub) then return false end
	return vanilla_site_outside_command_range(self, ...)
end

-- Fleet drones and dispatched jobs share the ceiling; waiting jobs count so the fleet makes room.
local function slot_counts(self, jobs)
	local dispatched, waiting = 0, 0
	for _, job in ipairs(jobs) do
		if job.deadline then dispatched = dispatched + 1 else waiting = waiting + 1 end
	end
	return #(self.drones or empty_table), dispatched, waiting
end

-- A trip's predicted end, from now: the fallback deadline (the Wasp's work is the completion).
local function schedule_trip(self, job, now, what)
	local tune = Floor.HubRepairTune
	local dist = IsValid(job.el) and self:GetDist2D(job.el:GetPos()) or 0
	local travel = MulDivRound(dist, 1000, repair_speed(self))
	job.started = now
	job.deadline = now + tune.LaunchTime + travel + repair_work_time()
	job.drone = false
	-- the smoke's ETA record (link 5): distance and the deadline's three parts, game ms
	print(string.format("[TrainHubDev] repair %s: %d m, deadline in %d ms (launch %d + travel %d + work %d) at t=%d",
		what, DivRound(dist, 100), job.deadline - now, tune.LaunchTime, travel, repair_work_time(), now))
end

local function dispatch_job(self, job, now)
	local cost = outstanding_cost(job.site)
	local ok, res = hold_cost(self, job, cost)
	if not ok then
		job.waiting = res
		return false
	end
	job.waiting = false
	schedule_trip(self, job, now, "dispatched")
	notify_dispatch(self, job, now)
	return true
end

-- "done": paid and completed. "gone": the site no longer exists. "short", res: keep waiting.
local function complete_job(self, job)
	local leader = job.site
	if not live(leader) or not leader.construction_group or leader.construction_group[1] ~= leader then
		release_held(self, job)
		return "gone"
	end
	local cost = outstanding_cost(leader)
	for res, amount in pairs(cost) do
		local entry = job.held and job.held[res]
		local have = (entry and self.supply and entry.req == self.supply[res]) and entry.amount or 0
		if amount > have and stock_free(self, res) < amount - have then return "short", res end
	end
	release_held(self, job)
	for res, amount in pairs(cost) do
		if amount > 0 then self:AddResource(-amount, res) end
	end
	leader:Complete()
	return "done"
end

-- ---------------------------------------------------------------------------
-- The visual: one flight record per dispatched job, created from the pit, adopted after a load.
-- ---------------------------------------------------------------------------

-- The reactor's per-object colorization on a hub Wasp (spec §9 owner ask, 2026-09-23), a dial.
local function apply_wasp_palette(drone)
	local variant = Floor.HubRepairTune.WaspPalette
	if not variant or not IsValid(drone) or not drone.SetColorizationMaterial then return end
	local channels = type(variant) == "table" and variant or (hub_reactor_palettes[variant] and hub_reactor_palettes[variant].channels)
	if not channels then return end
	local count = hub_reactor_channels
	if drone.GetMaxColorizationMaterials then
		local entity_count = drone:GetMaxColorizationMaterials() or 0
		if entity_count > 0 then count = Min(count, entity_count) end
	end
	for i = 1, count do
		local ch = channels[i]
		if ch and ch.color then drone:SetColorizationMaterial(i, ch.color, ch.roughness or 0, ch.metallic or 0) end
	end
end

local function ensure_visual(self, job, now)
	local tune = Floor.HubRepairTune
	if not tune.Visual or IsValid(job.drone) or not IsValid(job.el) then return end
	local F = flight_api()
	if not F then return end
	local record = F.Create(self)
	if not record then return end
	if not F.Send(record, job.el) then
		F.Remove(record)
		return
	end
	apply_wasp_palette(record.drone)
	job.drone = record.drone
	flights[job] = record
end

-- After a load: a job's Wasp that rode the save under a stock leg or hold is taken back at the
-- stage the deadline names. Anything F.Adopt refuses is forgotten here and swept below.
local function adopt_visual(self, job, now)
	local F = flight_api()
	local d = job.drone
	if flights[job] or not IsValid(d) then return end
	if F and F.Adopt and job.deadline and d.command_center == self then
		-- a job still in the list has not had its work done (the work's end completes it), so its
		-- Wasp resumes outbound whatever the clock says
		local record = F.Adopt(self, d, job.el, "out")
		if record then
			flights[job] = record
			return
		end
	end
	job.drone = false
end

-- A repair drone leaves the way DespawnAtHub leaves: its cube on the ground first, then gone.
-- DoneObject ends the command (CommandObject.lua:128-142) and Drone:Done removes it from the
-- fleet list (Drone.lua:122-135); the fleet's own route is KillDrone, which asserts the list.
local function remove_repair_drone(self, d)
	if not IsValid(d) then return end
	if SelectedObj == d then SelectObj(false) end
	if d.DropCarriedResource then d:DropCarriedResource() end
	if d.StopFX then d:StopFX() end
	local F = flight_api()
	for job, record in pairs(flights) do
		if record.drone == d then
			flights[job] = nil
			if F and F.Remove then F.Remove(record) return end
		end
	end
	if IsValid(d) and IsValid(self) and table.find(self.drones or empty_table, d) then
		self:KillDrone(d)
	elseif IsValid(d) then
		DoneObject(d)
	end
end

-- Once per load, from the first hub tick: every hub adopts, then the strays go. A stray is a
-- Wasp whose controller is a train hub that is destroyed, or that holds it neither in its
-- fleet list nor in a job (a leftover of the console prototype, or of a job that was dropped).
local function after_load(now)
	loaded_pending = false
	local keep = {}
	AllMapsForEach("map", "SMROptInTrainHubBase", function(hub)
		if not IsValid(hub) or hub.destroyed then return end
		refilter_remote_stations(hub)
		for _, job in ipairs(track_jobs(hub)) do
			adopt_visual(hub, job, now)
			if IsValid(job.drone) then keep[job.drone] = true end
		end
	end)
	AllMapsForEach(true, "FlyingDrone", function(d)
		local hub = IsValid(d) and d.command_center
		if not is_hub(hub) then return end
		if hub.destroyed then
			remove_repair_drone(hub, d)
		elseif not keep[d] and not table.find(hub.drones or empty_table, d) then
			remove_repair_drone(hub, d)
		end
	end)
end

-- ---------------------------------------------------------------------------
-- The fleet.
-- ---------------------------------------------------------------------------

function SMROptInTrainHubBase:GetMaxDrones()
	return Floor.HubRepairTune.MaxDrones
end

-- A vanilla Wasp (DESIGN.md: FlyingDrone, entity DroneJapanFlying), named, topped up, placed
-- around the body the way DroneControl:SpawnDronesAround places one (DroneControl.lua:244-255).
function SMROptInTrainHubBase:SpawnDrone()
	if #self.drones >= self:GetMaxDrones() then return false end
	local drone = FlyingDrone:new({ city = self.city }, self:GetMap())
	if not IsValid(drone) then return false end
	drone:SetCommandCenter(self)
	drone.name = "Repair Drone"
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
	apply_wasp_palette(drone)
	return true
end

-- Never adopt another controller's orphaned drones (owner, 2026-09-23): vanilla's
-- DroneControl:GatherOrphanedDrones (DroneControl.lua:292 on 1.1.1.405907) takes any drone on the
-- map up to the maximum, and the fleet's recall would then delete it. Every vanilla caller goes
-- through self (DroneControl.lua:857, DroneHubExtender.lua:162), so this covers them all.
function SMROptInTrainHubBase:GatherOrphanedDrones()
end

function SMROptInTrainHubBase:CheatSpawnDrone()
	self:SpawnDrone()
end

local function fleet_target(self, load, dispatched, waiting)
	local tune = Floor.HubRepairTune
	local target = tune.Standing
	if load == "medium" then
		target = target + tune.StepMedium
	elseif load == "high" then
		target = target + tune.StepMedium + tune.StepHigh
	end
	return Max(0, Min(target, tune.MaxDrones - dispatched - waiting))
end

local function idle_fleet_drone(self)
	for _, d in ipairs(self.drones or empty_table) do
		if IsValid(d) and (d.command == "Idle" or d.command == "WaitingCommand")
			and not (d.GetCarriedResource and d:GetCarriedResource()) then
			return d
		end
	end
end

function SMROptInTrainHubBase:HubFleetTick(now, dispatched, waiting)
	if not self:CanCommandDrones() then return end
	local tune = Floor.HubRepairTune
	local state = fleet_state[self]
	if not state then state = {}; fleet_state[self] = state end
	local load = self:GetDroneLoad()
	local target = fleet_target(self, load, dispatched, waiting)
	local count = #(self.drones or empty_table)
	if count < target then
		for _ = count + 1, target do
			if not self:SpawnDrone() then break end
		end
		state.above_since = false
	elseif count > target then
		state.above_since = state.above_since or now
		-- a waiting repair outranks a fleet drone: it makes room without the delay
		if (waiting > 0 or now - state.above_since >= tune.RecallDelay)
			and now - (state.last_recall or 0) >= tune.RecallStep then
			local d = idle_fleet_drone(self)
			if d then
				state.last_recall = now
				if self:GetDist2D(d:GetPos()) <= tune.RecallRadius then
					remove_repair_drone(self, d)
				else
					d:SetCommand("GoHome", nil, nil, nil, "ReturningToController")
				end
			end
		end
	else
		state.above_since = false
	end
	return target, load
end

-- Every repair drone of this hub, fleet or flight, in flight or idle: cube dropped, then gone.
function SMROptInTrainHubBase:HubDespawnRepairDrones()
	for i = #(self.drones or empty_table), 1, -1 do
		remove_repair_drone(self, self.drones[i])
	end
	for _, job in ipairs(track_jobs(self)) do
		if IsValid(job.drone) then remove_repair_drone(self, job.drone) end
		job.drone = false
	end
	AllMapsForEach(true, "FlyingDrone", function(d)
		if IsValid(d) and d.command_center == self then remove_repair_drone(self, d) end
	end)
end

-- Finalize is reached from DroneControl:Done (salvage, refab) and :OnDestroyed only
-- (DroneControl.lua:341-352). Ours removes the drones first, so vanilla's body finds none to
-- orphan; then it releases every stock claim and empties the job list.
function SMROptInTrainHubBase:Finalize()
	self:HubDespawnRepairDrones()
	local jobs, record = track_jobs(self)
	for _, job in ipairs(jobs) do release_held(self, job) end
	if record then record.jobs = {} end
	for site, hub in pairs(covered_sites) do
		if hub == self then covered_sites[site] = nil; if live(site) then refresh_coverage(site) end end
	end
	DroneControl.Finalize(self)
end

-- ---------------------------------------------------------------------------
-- The tick.
-- ---------------------------------------------------------------------------

-- The flight's work at the break has ended (owner, 2026-09-24: the site fixed only once the Wasp
-- was part way home). Measured: work ended 0.6 s before the deadline and the 5 s tick completed it
-- 4.2 s after, 35.0 s from dispatch against the Wasp leaving at 30.2 s. The deadline only moves
-- EARLIER. With a live Wasp this event is the completion; the deadline is the fallback (below).
local work_done = setmetatable({}, weak_keys_meta) -- job -> true; never saved, read on the same tick

local function on_work_done(hub, drone, now)
	if not is_hub(hub) then return end
	for _, job in ipairs(track_jobs(hub)) do
		if job.drone == drone and job.deadline then
			if now < job.deadline then job.deadline = now end
			work_done[job] = true
			hub:HubTrackWorkTick()
			return
		end
	end
end

local function wasps_fly()
	return Floor.HubRepairTune.Visual and flight_api() ~= nil
end

local function live_wasp(job)
	local record = flights[job]
	local d = record and record.drone
	return IsValid(d) and not record.lost and d == job.drone and d.command ~= "Dead" or false
end

local function service_job(self, record, job, now, tracks, dispatched_now)
	if job.kind ~= "repair" then return true, dispatched_now end -- build 5's jobs are not ours
	if not live(job.site) then return false, dispatched_now end
	if not job.deadline then
		if not can_dispatch(self, record) or not tracks[job.track] or dispatched_now then
			return true, dispatched_now
		end
		-- A new site builds its requests after GameInit (ConstructionSite.lua:806-815, :767-768 on
		-- 1.1.1.405907); until then its cost reads empty and the claim would hold nothing (L5
		-- sitting, 2026-09-24: an empty hub dispatched on TrackBroken's tick). Free Construction
		-- builds the table with no demand, so an empty table still dispatches.
		if not job.site.construction_resources then return true, dispatched_now end
		local fleet, dispatched, _ = slot_counts(self, record.jobs)
		if fleet + dispatched >= Floor.HubRepairTune.MaxDrones then return true, dispatched_now end
		local launched = dispatch_job(self, job, now) -- one launch per tick, so the pit is not crowded
		if launched then ensure_visual(self, job, now) end
		return true, launched
	end
	-- A repair under way always has a live Wasp (owner, 2026-09-24: a Wasp destroyed on the way,
	-- by a meteor storm say, must not leave the timer to repair the track with no drone there).
	-- One that died, was lost or never launched before its work was done is replaced from the
	-- pit, and the trip's fallback deadline restarts with it.
	if not work_done[job] and wasps_fly() and not live_wasp(job) then
		flights[job] = nil
		schedule_trip(self, job, now, "relaunched")
		ensure_visual(self, job, now)
		return true, dispatched_now
	end
	if now >= job.deadline then
		-- The flight is the authority (owner, 2026-09-24: "that way its never just one a timer"):
		-- a job with a live Wasp completes when that Wasp finishes its work (on_work_done); a lost
		-- one is relaunched above. The deadline completes a job only with Wasps off (the Visual
		-- dial or no flight code), or one stuck past FlightGrace percent of its predicted trip.
		if not work_done[job] and live_wasp(job) then
			local cap = job.deadline + MulDivRound(job.deadline - (job.started or job.deadline), Floor.HubRepairTune.FlightGrace, 100)
			if now < cap then return true, dispatched_now end
		end
		local result, res = complete_job(self, job)
		if result == "done" or result == "gone" then
			-- the Wasp's stage at completion: "out" = deadline early, "work" = on time, "back" = late
			local record = flights[job]
			print(string.format("[TrainHubDev] repair %s: %d ms after the deadline, the Wasp's stage %s",
				result, now - job.deadline, tostring(record and record.stage or (job.drone and "untracked") or "no Wasp")))
			return false, dispatched_now
		end
		job.waiting = res
		return true, dispatched_now
	end
	ensure_visual(self, job, now)
	return true, dispatched_now
end

function SMROptInTrainHubBase:HubTrackWorkTick()
	if not IsValid(self) or self.destroyed or IsBeingDestructed(self) then return end
	local now = GameTime()
	if loaded_pending then after_load(now) end
	local F = flight_api()
	if F and F.OnWorkDone ~= on_work_done then F.OnWorkDone = on_work_done end
	local record = track_work(self)
	local nodes, tracks = self:HubTrackGraph()
	register_remote_stations(self, nodes)
	discover_breaks(self, record, tracks, now)
	local jobs = record.jobs
	local dispatched_now, waiting_any = false, false
	for i = #jobs, 1, -1 do
		local job = jobs[i]
		local keep
		keep, dispatched_now = service_job(self, record, job, now, tracks, dispatched_now)
		if not keep then
			release_held(self, job)
			table.remove(jobs, i)
		elseif job.waiting then
			waiting_any = job.waiting
		end
	end
	if self.AttachSign then self:AttachSign(waiting_any and true or false, "SignNoConsumptionResource") end
	update_coverage(self, record)
	local _, dispatched, waiting = slot_counts(self, jobs)
	-- the notice goes when the last repair under way is done, not a minute later (owner, 2026-09-23)
	if dispatched == 0 and type(RemoveOnScreenNotification) == "function" then
		RemoveOnScreenNotification(hub_notification_id, self:GetMap())
	end
	self:HubFleetTick(now, dispatched, waiting)
end

-- A break on any map: the hubs there look now rather than on their next 5 s tick.
function OnMsg.TrackBroken(track, is_broken)
	if not is_broken or not rawget(_G, "SMROptInTrainFloor") or not IsValid(track) then return end
	local map = track:GetMap()
	AllMapsForEach("map", "SMROptInTrainHubBase", function(hub)
		if IsValid(hub) and hub:GetMap() == map then hub:HubTrackWorkTick() end
	end)
end

-- ---------------------------------------------------------------------------
-- Control, panel, console.
-- ---------------------------------------------------------------------------

-- Chained on the declaring class (FlyingDrone.lua:144-146). Inert for every other drone.
local vanilla_wasp_can_be_controlled = FlyingDrone.CanBeControlled
function FlyingDrone:CanBeControlled(...)
	local result = vanilla_wasp_can_be_controlled(self, ...)
	if result and is_hub(self.command_center) then return false end
	return result
end

-- The panel's status and destination lines for a Wasp on a repair flight (owner, 2026-09-24:
-- "Unknown" / "No particular destination" the whole trip). Vanilla reads the command's entry in
-- DroneCommands (Drone:Getui_command, Drone.lua:3168 on 1.1.1.405907), and the stock
-- FlightGoto/WaitUninterruptable legs have none. Chained on the declaring class; every drone
-- that is not a hub repair flight gets vanilla's answer.
local function repair_flight_stage(drone)
	local hub = drone.command_center
	if not IsKindOf(drone, "FlyingDrone") or not is_hub(hub) then return end
	for _, job in ipairs(track_jobs(hub)) do
		if job.drone == drone then
			local record = flights[job]
			return record and record.stage or "out"
		end
	end
end

local repair_flight_status = {
	rise = T(909018002017, "Launching for a track repair"),
	ready = T(909018002017, "Launching for a track repair"),
	exit = T(909018002017, "Launching for a track repair"),
	out = T(909018002018, "Flying to a track repair"),
	work = T(909018002019, "Repairing track"),
	back = T(909018002020, "Returning to the Train Hub"),
	descent = T(909018002020, "Returning to the Train Hub"),
}

local vanilla_drone_ui_command = Drone.Getui_command
function Drone:Getui_command(...)
	local stage = repair_flight_stage(self)
	if stage and repair_flight_status[stage] then return repair_flight_status[stage] end
	return vanilla_drone_ui_command(self, ...)
end

local vanilla_drone_dest_name = Drone.GetDestName
function Drone:GetDestName(...)
	local stage = repair_flight_stage(self)
	if stage == "back" or stage == "descent" then
		return T(909018002021, "Going to<right><em>Train Hub</em>")
	elseif stage then
		return T(909018002022, "Going to<right><em>Broken track</em>")
	end
	return vanilla_drone_dest_name(self, ...)
end

-- "Repair drones: N out / 30", the panel's one line (DESIGN.md), plus what waits.
function SMROptInTrainHubBase:GetHubRepairLine()
	local jobs, record = track_jobs(self)
	local fleet, dispatched, waiting = slot_counts(self, jobs)
	local text = string.format("Repair drones: %d out / %d", fleet + dispatched, self:GetMaxDrones())
	if dispatched > 0 then text = text .. string.format(", %d repair%s under way", dispatched, dispatched == 1 and "" or "s") end
	if waiting > 0 then text = text .. string.format(", %d waiting", waiting) end
	for _, job in ipairs(jobs) do
		if job.waiting then text = text .. " (short of " .. tostring(job.waiting) .. ")" break end
	end
	if record and record.repair == false then text = text .. "; track repair off" end
	return Untranslated(text)
end

function SMROptInTrainHubBase:HubTrackRepairEnabled()
	local _, record = track_jobs(self)
	return not record or record.repair ~= false
end

function SMROptInTrainHubBase:SetHubTrackRepair(on)
	track_work(self).repair = on and true or false
	RebuildInfopanel(self)
end

-- The hub's panel sections: vanilla's Drone Hub status narrowed to count and load, this build's
-- repair line under it, and the track-repair toggle as an InfopanelActiveSection with everything
-- set in OnContextUpdate. They are built in sectionCustom:Init, which ipBuilding spawns for every
-- building (ipBuilding.generated.lua:65 on 1.1.1.405907). That is the shipping
-- Opt_ResidencyControl shape: a generated XDef class declares Init itself, so the classdef capture
-- is valid at load. L5 sitting, 2026-09-24: the runtime XTemplate this replaces was registered and
-- on sectionCustom's lookup path, but never showed in play.
local function add_hub_sections(section, context)
	local status = InfopanelSection:new({
		RolloverText = T(359011926905, "<UISectionDroneHubRollover>"),
		RolloverTitle = T(167050805716, "Drones Status"),
		Title = T(732959546527, "Drones"),
		TitleRight = T(745904750458, "<drone(DronesCount,MaxDronesCount)>"),
		Icon = "UI/IconsRemaster/Sections/drone.png",
		TitleHAlign = "stretch",
	}, section, context)
	local content = InfopanelSection.__content(status, context)
	InfopanelText:new({ Text = T(935141416350, "<DronesStatusText>") }, content, context)
	InfopanelText:new({ Text = T(909018002010, "<HubRepairLine>") }, content, context)
	InfopanelActiveSection:new({
		Icon = "UI/IconsRemaster/Sections/drone.png",
		OnContextUpdate = function(self, context, ...)
			local hub = ResolvePropObj(context)
			local on = IsValid(hub) and hub:HubTrackRepairEnabled()
			self:SetIcon("UI/IconsRemaster/Sections/drone.png")
			self:SetIconBack(on and "UI/IconsRemaster/Sections/ip_sections_on.png" or "UI/IconsRemaster/Sections/ip_sections_limit")
			self:SetTitle(Untranslated(on and "Track repair: on" or "Track repair: off"))
			self:SetRolloverImageColor(on and "green" or "yellow", true)
			self.OnActivate = function(self, context, gamepad)
				local building = ResolvePropObj(context)
				if IsValid(building) then building:SetHubTrackRepair(not building:HubTrackRepairEnabled()) end
			end
			self:SetRolloverTitle(Untranslated("Track repair"))
			self:SetRolloverText(Untranslated(on
				and "A break on this hub's own track network is repaired from the hub's stock: a Repair Drone flies out and the track is fixed when it finishes its work, at the Safe Transport rate. Turning this off stops new dispatches; a repair already under way still completes.<newline><newline>Current status: <em>on</em>"
				or "No new track repairs are dispatched from this hub. Broken track on its network waits for ordinary Drones or for this to be turned on again.<newline><newline>Current status: <em>off</em>"))
			self:SetRolloverHint(Untranslated(on and "<left_click> Stop new track repairs" or "<left_click> Resume track repairs"))
			self:SetRolloverHintGamepad(Untranslated(on and "<ButtonA> Stop new track repairs" or "<ButtonA> Resume track repairs"))
		end,
	}, section, context)
end

local vanilla_section_custom_init = sectionCustom.Init
function sectionCustom:Init(parent, context, ...)
	vanilla_section_custom_init(self, parent, context, ...)
	if is_hub(ResolvePropObj(context)) then add_hub_sections(self, context) end
end

-- The console surface, the way SetHubDroneTune works: one name and a number, or a table.
--   SetHubRepairTune("Standing", 5)   SetHubRepairTune{ RecallDelay = 30000, WaspPalette = "P4" }
function SetHubRepairTune(name, value)
	local tune = Floor.HubRepairTune
	local changes = type(name) == "table" and name or { [name] = value }
	for k, v in pairs(changes) do
		if tune[k] == nil then
			return false, "No such dial; the names are " .. table.concat(table.keys(tune, true), ", ")
		end
		if k == "WaspPalette" then
			if v ~= false and type(v) ~= "table" and not hub_reactor_palettes[v] then
				return false, 'WaspPalette is false, "P1".."P4" or a channel table'
			end
		elseif k == "Visual" then
			v = v and true or false
		elseif k == "Speed" or k == "WorkTime" then
			if v ~= false and (type(v) ~= "number" or v < 1) then return false, k .. " is false or a positive integer" end
		elseif type(v) ~= "number" or v ~= math.floor(v) or v < 0 then
			return false, k .. " is a non-negative integer"
		end
		tune[k] = v
	end
	return true
end

-- HubRepairStatus(hub) prints the jobs, the fleet and the dials; returns the job list.
function HubRepairStatus(hub)
	hub = hub or SelectedObj
	if not is_hub(hub) then print("[TrainHubDev] repair: select a built train hub") return end
	local jobs, record = track_jobs(hub)
	local fleet, dispatched, waiting = slot_counts(hub, jobs)
	local now = GameTime()
	print(string.format("[TrainHubDev] repair: toggle %s, switch %s, fleet %d, load %s, repairs %d under way, %d waiting, max %d",
		(not record or record.repair ~= false) and "on" or "off", hub.ui_working and "on" or "off", fleet,
		tostring(hub:GetDroneLoad()), dispatched, waiting, hub:GetMaxDrones()))
	for i, job in ipairs(jobs) do
		print(string.format("[TrainHubDev] repair job %d: %s site %s deadline %s (%s) drone %s waiting %s",
			i, tostring(job.kind), tostring(job.site), tostring(job.deadline),
			job.deadline and (now >= job.deadline and "due" or tostring(job.deadline - now) .. " ms left") or "not dispatched",
			IsValid(job.drone) and tostring(job.drone.command) or "none", tostring(job.waiting)))
	end
	return jobs
end

function OnMsg.CityStart()
	ensure_hub_notification()
end

-- Every flight record and fleet timer belongs to the session that ends here (the flight file
-- clears its own records at LoadGame too); the loaded hubs adopt afresh on their first tick.
function OnMsg.LoadGame()
	flights = setmetatable({}, weak_keys_meta)
	fleet_state = setmetatable({}, weak_keys_meta)
	loaded_pending = true
	ensure_hub_notification()
end

function OnMsg.DoneGame()
	loaded_pending = false
end

function SMROptInTrainHubBase:InitHubTrackWork()
	ensure_hub_notification()
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
	install_hub_dwell()
	install_hub_save_guard()
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
