-- Auto-fill and siding placement; spec section 4.8 ruling 10, owner 2026-09-28.
-- Retired extras and tests: docs/archive/train_bay_extras_20260928/.
-- Keep the saved class name: existing HubTrain objects now inherit vanilla Train
-- behavior, including Idle, route counting and storage. No new HubTrain is spawned.
-- The old snapshot's delete-on-load list and prepaid pool use vanilla's loader.
DefineClass.HubTrain = {
    __parents = { "Train" },
    persist_baseclass = "Train",
}

SMROptInTrainBay = {}
local B = SMROptInTrainBay
B.tick_minutes = 10
B.fill_window = const.HourDuration * 2
B.stats = { filled = 0 }
B.error = false
B.Require = { { "TrackBase", "CanAddVehicle" }, { "TrackBase", "AssignTrain" } }
for _, pair in ipairs(B.Require) do
    local class = rawget(_G, pair[1])
    if not class or type(class[pair[2]]) ~= "function" then
        B.error = pair[1] .. "." .. pair[2] .. " unavailable"
        print("[TrainBay] inactive: " .. B.error)
        return
    end
end
if type(rawget(_G, "ColonyGetPrefabs")) ~= "function" then
    B.error = "ColonyGetPrefabs unavailable"
    return
end

local owed = {}
local snapshot = false
local function h(o) return IsValid(o) and tostring(o.handle) or "none" end
local function is_hub(o) return IsValid(o) and IsKindOf(o, "SMROptInTrainHubBase") and not o.destroyed end

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

-- AssignTrain sends this before assigning the track or starting LoadTrain.
function OnMsg.TransportLinkChanged(link, vehicle, action)
    if action ~= "add" or not IsValid(vehicle) then return end
    local hub = vehicle.current_station
    if not is_hub(hub) or not vehicle.at_spawn_track then return end
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

local function free_arm(hub, line)
	for _, arm in ipairs(line.arms) do
		if not hub:GetOccupyingTrain(arm.track) then return arm end
	end
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

function B.Tick()
    local live = {}
    each_hub(function(hub)
        for _, line in ipairs(hub_lines(hub)) do
            live[line.key] = true
            if owed[line.key] then try_fill(hub, line) end
        end
    end)
    for key in pairs(owed) do if not live[key] then owed[key] = nil end end
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
    if B.active then take_snapshot(snapshot and true or false) end
end

local function reset() owed, snapshot = {}, false end
function OnMsg.LoadGame() reset(); take_snapshot(false) end
function OnMsg.CityStart() reset(); take_snapshot(false) end
function OnMsg.DoneGame() reset() end

B.active = true
print("[TrainBay] loaded: vanilla auto-fill and siding placement; legacy HubTrain compatibility")
