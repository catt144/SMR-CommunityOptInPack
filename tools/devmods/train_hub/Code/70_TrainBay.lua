-- Train bay, dev only. Authority: spec section 4.8 ruling 9 (owner, 2026-09-28);
-- brief Train_Hub_Project/13. The bay is the colony's stored-train pool.
-- Archived 1.1.1.405907: Units/Train.lua:86-97 (Done), :157-192 (DestroySilent,
-- OnDemolish), :220-228, :230-289 (LoadTrain; a spawn always departs);
-- Buildings/Track.lua:206-209, :423-457 (CanAddVehicle, AssignTrain);
-- Buildings/StationsLink.lua:36-49 (AddTransportLink, TransportLinkChanged);
-- TrainTransport.lua:302-357 (TrainRoutesRebuilt), :492-537 (GetTrainsOnRoute);
-- City.lua:478-485 (AddPrefabs); CommonLua/Core/persist.lua:73-84, :164, :190-205;
-- Classes/_cobject.lua:135-138; Classes/_object.lua:233-240; Savegame.lua:853-867.
-- No vanilla body is copied. Vanilla places, loads, moves and stores every train.
--
-- Hub extras are class HubTrain (persist_baseclass "Train"): vanilla's own
-- AssignTrain spawns a Train; the hub passes the cap gate for that one call and
-- ChangeClass makes it a HubTrain. GetTrainsOnRoute leaves HubTrains out, so the
-- player's placement gate and route counts stay vanilla. An extra is recalled
-- (DestroySilent, back to the pool) as soon as it goes Idle empty.
-- Save rungs: 0 the gate pass and the hidden count; 1 empty extras on vanilla's
-- delete-on-load list plus the pool count, inside the snapshot only; 5 loaded
-- extras as HubTrain, which loads as a plain Train without the mod (route
-- briefly over cap). No field on any object, no GameVar, no thread of ours.

SMROptInTrainBay = rawget(_G, "SMROptInTrainBay") or {}
local B = SMROptInTrainBay
B.max_extras = 5 -- per hub route (owner: tunable by eye)
B.tick_minutes = 10 -- game minutes between need checks
B.cooldown = const.HourDuration * 2 -- after an extra is recalled without work
B.fill_window = const.HourDuration * 2 -- an owed auto-fill is retried this long
B.shortfall_delay = const.HourDuration -- continuous need with vanilla working
B.settle_delay = const.HourDuration * 3 -- after load / new game
B.stats = { requested = 0, deployed = 0, recalled = 0, filled = 0, stored = 0, kept = 0 }
B.error = false

B.Require = {
	{ "Train", "DestroySilent" }, { "Train", "AssignToTrack" },
	{ "TrackBase", "CanAddVehicle" }, { "TrackBase", "AssignTrain" },
	{ "City", "AddPrefabs" },
}
for _, pair in ipairs(B.Require) do
	local class = rawget(_G, pair[1])
	if not class or type(class[pair[2]]) ~= "function" then
		B.error = pair[1] .. "." .. pair[2] .. " unavailable"
		print("[TrainBay] inactive: " .. B.error)
		return
	end
end
for _, name in ipairs({ "GetTrainsOnRoute", "ColonyGetPrefabs", "DeleteOnLoadGame",
	"CancelDeleteOnLoadGame", "PersistGame" }) do
	if type(rawget(_G, name)) ~= "function" then
		B.error = name .. " unavailable"
		print("[TrainBay] inactive: " .. B.error)
		return
	end
end

DefineClass.HubTrain = {
	__parents = { "Train" },
	persist_baseclass = "Train",
}

local pending = {} -- track -> { hub, time }: one extra spawn in flight
local owed = {} -- route key -> game time a station joined it
local cooldown = {} -- station-set key -> game time deploys resume
local worked = setmetatable({}, { __mode = "k" }) -- extra -> carried cargo
local snapshot = false -- hub -> arm idx -> station count on its route
local shortfall = {} -- line key -> first qualifying check; runtime only
local settle_until = GameTime() + B.settle_delay

local function h(o) return IsValid(o) and tostring(o.handle) or "none" end
local function is_hub(o) return IsValid(o) and IsKindOf(o, "SMROptInTrainHubBase") and not o.destroyed end
local function is_extra(t) return IsValid(t) and IsKindOf(t, "HubTrain") end

local function cargo(t)
	local n = 0
	for _, amount in pairs(t.stockpiled_amount or empty_table) do n = n + amount end
	return n
end

local function empty(t)
	return IsValid(t) and not t.destroyed and cargo(t) == 0
		and not next(t.assigned_resources or empty_table) and #(t.units or empty_table) == 0
end

local function route_key(route)
	local seen, handles = {}, {}
	for _, st in ipairs(route or empty_table) do
		if IsValid(st) and not seen[st] then seen[st] = true; handles[#handles + 1] = st.handle end
	end
	table.sort(handles)
	return table.concat(handles, "-"), #handles
end

local function each_hub(fn)
	for _, city in ipairs(Cities or empty_table) do
		for _, st in ipairs(city.labels.Station or empty_table) do
			if is_hub(st) then fn(st) end
		end
	end
end

-- The hub's arms that carry a route, grouped by route in connector order.
local function hub_lines(hub)
	local routes = hub.city and hub.city.train_track_routes or empty_table
	local lines, by_route = {}, {}
	for i = hub.first_connector_idx or 1, hub.last_connector_idx or 0 do
		local el = hub:GetConnectorElement(i)
		local track = IsValid(el) and el.track_obj
		local route = IsValid(track) and routes[track]
		if route then
			local line = by_route[route]
			if not line then
				local set, stations = route_key(route)
				line = { route = route, set = set, key = h(hub) .. ":" .. set, stations = stations, arms = {} }
				by_route[route] = line
				lines[#lines + 1] = line
			end
			line.arms[#line.arms + 1] = { idx = i, track = track }
		end
	end
	return lines
end

-- HubTrains that vanilla's count would include for this route.
local function extras_counted(route, routes, seen)
	local n = 0
	for _, st in ipairs(route) do
		for _, t in pairs(st.track_busy or empty_table) do
			if is_extra(t) and not seen[t] and routes[t.track] == route then seen[t] = true; n = n + 1 end
		end
	end
	for _, edge in ipairs(route.edges or empty_table) do
		for _, segment in ipairs(edge.tracks or empty_table) do
			for _, t in ipairs(segment.assigned_vehicles or empty_table) do
				if is_extra(t) and not seen[t] then seen[t] = true; n = n + 1 end
			end
		end
	end
	return n
end

local function extras_on(route, city)
	local n = 0
	local routes = city.train_track_routes or empty_table
	for _, t in ipairs(city.labels.Train or empty_table) do
		if is_extra(t) and not t.destroyed and IsValid(t.track) and routes[t.track] == route then n = n + 1 end
	end
	return n
end

-- The player sees vanilla: every caller's count and the cap gate leave extras out.
local vanilla_count = GetTrainsOnRoute
function GetTrainsOnRoute(track, seen)
	local routes = IsValid(track) and track.city and track.city.train_track_routes
	local route = routes and routes[track]
	local counted_before = route and seen and seen[route]
	local trains, cap = vanilla_count(track, seen)
	if route and not counted_before and trains > 0 then
		trains = Max(trains - extras_counted(route, routes, {}), 0)
	end
	return trains, cap
end

-- The hub's own spawn passes the gate for its one AssignTrain call.
local can_add = TrackBase.CanAddVehicle
function TrackBase:CanAddVehicle(...)
	local p = pending[self]
	if p and GameTime() - p.time <= 1000 then return true end
	return can_add(self, ...)
end

function OnMsg.TransportLinkChanged(link, vehicle, action)
	local p = pending[link]
	if action ~= "add" or not IsValid(vehicle) then return end
	local hub = vehicle.current_station
	if not is_hub(hub) or not vehicle.at_spawn_track then return end
	if p and hub == p.hub
		and not is_extra(vehicle) then
		pending[link] = nil
		vehicle:ChangeClass("HubTrain")
		B.stats.deployed = B.stats.deployed + 1
		print(string.format("[TrainBay] deploy train=%s hub=%s arm=%s line=%s pool=%d t=%d",
			h(vehicle), h(p.hub), tostring(p.idx), p.key, ColonyGetPrefabs("Train", p.hub.city), GameTime()))
	end
	-- AssignTrain has placed the object, but has not assigned its track or
	-- started LoadTrain yet. Place AFTER ChangeClass, for both bay extras and
	-- vanilla/auto-fill spawns. Never reposition a travelling/arriving train.
	local floor = rawget(_G, "SMROptInTrainFloor")
	local idx = hub:GetConnectionSpot(link)
	if floor and floor.HubSpawnLocation and idx then
		local before, before_angle = vehicle:GetPos(), vehicle:GetAngle()
		local pos, angle = floor.HubSpawnLocation(hub, idx)
		vehicle:SetPos(pos)
		vehicle:SetAngle(angle)
		print(string.format("[TrainBay] spawn train=%s hub=%s arm=%s before=%s before_angle=%s target=%s angle=%s actual=%s actual_angle=%s t=%d",
			h(vehicle), h(hub), tostring(idx), tostring(before), tostring(before_angle), tostring(pos),
			tostring(angle), tostring(vehicle:GetPos()), tostring(vehicle:GetAngle()), GameTime()))
	end
end

function OnMsg.TrainLoadedUnloaded(train)
	if is_extra(train) and cargo(train) > 0 then worked[train] = true end
end

-- Recall: an idle, empty extra holds a platform (no signals, Track.lua:448).
function HubTrain:Idle(...)
	if B.active and empty(self) then
		local routes = self.city and self.city.train_track_routes or empty_table
		local route = IsValid(self.track) and routes[self.track]
		-- A spawn that found nothing to carry: that line's signal and vanilla disagree.
		if not worked[self] and route then cooldown[route_key(route)] = GameTime() + B.cooldown end
		B.stats.recalled = B.stats.recalled + 1
		print(string.format("[TrainBay] recall train=%s station=%s worked=%s pool_before=%d t=%d",
			h(self), h(self.current_station), tostring(worked[self] or false),
			ColonyGetPrefabs("Train", self.city), GameTime()))
		self:DestroySilent()
		return
	end
	return Train.Idle(self, ...)
end

local function per_train(city)
	for _, t in ipairs(city.labels.Train or empty_table) do
		if IsValid(t) and (t.max_shared_storage or 0) > 0 then return t.max_shared_storage end
	end
	return rawget(Train, "max_shared_storage") or 42 * const.ResourceScale -- the property default
end

-- Brief 11's need signal over brief 10's stop arithmetic: per resource, what the
-- line's hub-parented stations (with their off-hub branches) want delivered,
-- capped by hub stock, plus what they offer back, capped by hub room.
function B.LineNeed(hub, line)
	local D = rawget(_G, "SMROptInTrainDistribution")
	if not (D and D.active and D.BranchNeed) then return 0 end
	local total = 0
	for _, res in ipairs(hub.storable_resources or empty_table) do
		local deliver, collect = 0, 0
		local seen = {}
		for _, st in ipairs(line.route) do
			if not seen[st] and st ~= hub and IsValid(st) and D.HubFor(st) == hub and D.Parent(st) == hub then
				seen[st] = true
				local n = D.BranchNeed(st, res)
				if n > 0 then deliver = deliver + n else collect = collect - n end
			end
		end
		local supply, demand = hub.supply and hub.supply[res], hub.demand and hub.demand[res]
		local stock = supply and supply:GetActualAmount() or 0
		local room = demand and Max(demand:GetTargetAmount(), 0) or 0
		total = total + Min(deliver, stock) + Min(collect, room)
	end
	return total
end

local function free_arm(hub, line)
	for _, arm in ipairs(line.arms) do
		if not pending[arm.track] and not hub:GetOccupyingTrain(arm.track) then return arm end
	end
end

local function vanilla_working(hub, line, expected)
	local n = 0
	local routes = hub.city.train_track_routes or empty_table
	for _, t in ipairs(hub.city.labels.Train or empty_table) do
		if IsValid(t) and not t.destroyed and not is_extra(t) and routes[t.track] == line.route then
			n = n + 1
			local travelling = t.command == "GotoStation" and not t.at_station
			local handling = (t.command == "LoadTrain" or t.command == "UnloadTrain") and not empty(t)
			if not travelling and not handling then return false end
		end
	end
	-- Missing/unknown trains fail closed; an empty line is vanilla's to serve first.
	return n > 0 and n == expected
end

function B.LineRow(hub, line)
	local vanilla, cap = GetTrainsOnRoute(line.arms[1].track)
	local extras = extras_on(line.route, hub.city)
	local need = B.LineNeed(hub, line)
	local per = per_train(hub.city)
	local loads = need > 0 and (need + per - 1) // per or 0
	local wanted = Min(Max(loads - vanilla, 0), B.max_extras)
	return { line = line.key, stations = line.stations, vanilla = vanilla, cap = cap, extras = extras,
		need = need, loads = loads, wanted = wanted, arms = #line.arms,
		working = vanilla_working(hub, line, vanilla),
		shortfall = shortfall[line.key] and Max(GameTime() - shortfall[line.key], 0) or 0,
		settle = Max(settle_until - GameTime(), 0),
		cooldown = Max((cooldown[line.set] or 0) - GameTime(), 0),
		owed = owed[line.key] and true or false }
end

local function try_fill(hub, line)
	local since = owed[line.key]
	if GameTime() - since > B.fill_window then owed[line.key] = nil return end
	if ColonyGetPrefabs("Train", hub.city) <= 0 then return end
	local arm = free_arm(hub, line)
	if not arm or not arm.track:CanAddVehicle() then return end
	owed[line.key] = nil
	B.stats.filled = B.stats.filled + 1
	print(string.format("[TrainBay] fill line=%s arm=%d pool=%d t=%d", line.key, arm.idx,
		ColonyGetPrefabs("Train", hub.city), GameTime()))
	arm.track:AssignTrain(hub)
end

local function try_extra(hub, line)
	local row = B.LineRow(hub, line)
	if not hub.working or not row.working or row.extras >= row.wanted then
		shortfall[line.key] = nil
		return
	end
	shortfall[line.key] = shortfall[line.key] or GameTime()
	if GameTime() - shortfall[line.key] < B.shortfall_delay or row.settle > 0 then return end
	if ColonyGetPrefabs("Train", hub.city) <= 0 or row.cooldown > 0 then return end
	local arm = free_arm(hub, line)
	if not arm then return end
	pending[arm.track] = { hub = hub, idx = arm.idx, key = line.key, time = GameTime() }
	B.stats.requested = B.stats.requested + 1
	arm.track:AssignTrain(hub)
	return true
end

function B.Tick()
	for track, p in pairs(pending) do
		if not IsValid(track) or GameTime() - p.time > 1000 then pending[track] = nil end
	end
	local checked, live = {}, {}
	each_hub(function(hub)
		for _, line in ipairs(hub_lines(hub)) do
			live[line.key] = true
			if owed[line.key] then try_fill(hub, line) end
			-- A route through multiple hubs still gets at most one extra per check.
			if not checked[line.set] and try_extra(hub, line) then checked[line.set] = true end
		end
	end)
	for key in pairs(shortfall) do if not live[key] then shortfall[key] = nil end end
end

function OnMsg.NewMinute(hour, minute)
	if not B.active or minute % B.tick_minutes ~= 0 then return end
	local ok, err = pcall(B.Tick)
	if not ok and not B.error then
		B.error = tostring(err)
		print("[TrainBay] tick error: " .. B.error)
	end
end

-- Auto-fill: a station joining a hub route owes that route one vanilla train.
local function take_snapshot(owe)
	local next_snapshot = {}
	each_hub(function(hub)
		local arms = {}
		for _, line in ipairs(hub_lines(hub)) do
			local grew = false
			for _, arm in ipairs(line.arms) do
				arms[arm.idx] = line.stations
				local old = snapshot and snapshot[hub] and snapshot[hub][arm.idx] or 0
				if line.stations > old then grew = true end
			end
			if owe and grew then owed[line.key] = GameTime() end
		end
		next_snapshot[hub] = arms
	end)
	snapshot = next_snapshot
end

function OnMsg.TrainRoutesRebuilt()
	shortfall = {}
	if B.active then take_snapshot(snapshot and true or false) end
end

-- Save: empty extras go on vanilla's delete-on-load list and into the pool
-- for the snapshot only; loaded extras stay as HubTrain. Scoped to PersistGame,
-- not SaveGameStart/Done, because autosaves run game time between those.
-- LoadTrain and UnloadTrain are skipped: colonists may be boarding or leaving.
function B.StoreForSave()
	local stored = { trains = {}, pools = {} }
	if not B.active then return stored end
	local marked, kept = rawget(_G, "ObjsToDeleteOnLoadGame") or empty_table, 0
	for _, city in ipairs(Cities or empty_table) do
		local n = 0
		for _, t in ipairs(city.labels.Train or empty_table) do
			if is_extra(t) then
				if empty(t) and t.command ~= "LoadTrain" and t.command ~= "UnloadTrain" and not marked[t] then
					DeleteOnLoadGame(t)
					stored.trains[#stored.trains + 1] = t
					n = n + 1
				else
					kept = kept + 1
				end
			end
		end
		if n > 0 then
			city:AddPrefabs("Train", n, false) -- vanilla's writer; no build-menu refresh thread
			stored.pools[#stored.pools + 1] = { city = city, n = n }
		end
	end
	B.stats.stored, B.stats.kept = B.stats.stored + #stored.trains, B.stats.kept + kept
	print(string.format("[TrainBay] save: stored=%d kept=%d t=%d", #stored.trains, kept, GameTime()))
	return stored
end

function B.RestoreAfterSave(stored)
	for _, t in ipairs(stored.trains) do CancelDeleteOnLoadGame(t) end
	for _, pool in ipairs(stored.pools) do pool.city:AddPrefabs("Train", -pool.n, false) end
end

if not B.persist_wrapped then
	local previous = PersistGame
	_G.PersistGame = function(...)
		local ok, stored = pcall(SMROptInTrainBay.StoreForSave)
		if not ok then SMROptInTrainBay.error = tostring(stored); stored = false end
		local result = table.pack(pcall(previous, ...))
		if stored then SMROptInTrainBay.RestoreAfterSave(stored) end
		if not result[1] then error(result[2], 0) end
		return table.unpack(result, 2, result.n)
	end
	B.persist_wrapped = true
end

local function reset()
	pending, owed, cooldown, snapshot = {}, {}, {}, false
	shortfall, settle_until = {}, GameTime() + B.settle_delay
	worked = setmetatable({}, { __mode = "k" })
end
function OnMsg.LoadGame() reset(); take_snapshot(false) end
function OnMsg.CityStart() reset(); take_snapshot(false) end
function OnMsg.DoneGame() reset() end

-- Read for the sitting slot and the console. Read-only.
function B.Read()
	local out = { pool = 0, extras = 0, hubs = 0, lines = {}, stats = B.stats, error = B.error,
		game_time = GameTime() }
	for _, city in ipairs(Cities or empty_table) do
		out.pool = out.pool + (ColonyGetPrefabs("Train", city) or 0)
		for _, t in ipairs(city.labels.Train or empty_table) do
			if is_extra(t) then out.extras = out.extras + 1 end
		end
	end
	each_hub(function(hub)
		out.hubs = out.hubs + 1
		for _, line in ipairs(hub_lines(hub)) do out.lines[#out.lines + 1] = B.LineRow(hub, line) end
	end)
	return out
end

B.active = true
print("[TrainBay] loaded: hub extras up to " .. B.max_extras .. " per hub route; HubTrain class defined")
