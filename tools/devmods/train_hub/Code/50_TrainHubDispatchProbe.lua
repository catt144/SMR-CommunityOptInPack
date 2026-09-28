-- THROWAWAY dispatch probe, brief Train_Hub_Project/11 (2026-09-27). Dev mod only.
-- Question: can a train parked at the hub be put onto another hub line and then
-- serve it through vanilla's own LoadTrain/GotoStation? Mutation only on an
-- explicit call. No thread, no persisted field, no wrapper. Archived 1.1.1.405907:
-- Units/Train.lua:220-228 (AssignToTrack), :230-289 (LoadTrain), :338-414
-- (GotoStation); Buildings/Track.lua:423-457 (CanAddVehicle, AssignTrain);
-- Buildings/StationsLink.lua:36-49 (Add/RemoveTransportLink); TrainTransport.lua:492-537.
-- Console: SMROptInHubDispatchProbe.Run(SelectedObj)  -- parked hub train -> other line
--          SMROptInHubDispatchProbe.Read(SelectedObj) -- where is it now
--          SMROptInHubDispatchProbe.Forget()          -- allow a second Run on the same train
SMROptInHubDispatchProbe = {}
local P = SMROptInHubDispatchProbe
P.last = false -- in-memory record of the last Run; never saved

local function h(o) return IsValid(o) and tostring(o.handle) or "none" end
local function is_hub(o) return IsValid(o) and IsKindOf(o, "SMROptInTrainHubBase") end
local function say(fields)
	local keys = {}
	for k in pairs(fields) do keys[#keys + 1] = k end
	table.sort(keys)
	local parts = {}
	for _, k in ipairs(keys) do parts[#parts + 1] = k .. "=" .. tostring(fields[k]) end
	print("[HubDispatchProbe] " .. table.concat(parts, " "))
	return fields
end

local function cargo_of(train)
	local total = 0
	for _, amount in pairs(train.stockpiled_amount or empty_table) do total = total + amount end
	return total
end

-- Every hub line with a completed far station: connector idx, track, route, counts.
function P.Lines(hub)
	local lines = {}
	if not is_hub(hub) then return lines end
	local routes = hub.city and hub.city.train_track_routes or empty_table
	for i = hub.first_connector_idx, hub.last_connector_idx do
		local el = hub:GetConnectorElement(i)
		local track = IsValid(el) and el.track_obj
		local dest = IsValid(track) and track:GetDestStation(hub)
		local station = dest and GetNextConnectedStation(dest)
		if IsValid(station) and station ~= hub and routes[track] then
			local trains, cap = GetTrainsOnRoute(track)
			lines[#lines + 1] = { idx = i, track = track, station = station, route = routes[track],
				trains = trains, cap = cap, occupied = hub:GetOccupyingTrain(track) }
		end
	end
	return lines
end

function P.Read(train)
	train = train or SelectedObj
	if not IsValid(train) or not IsKindOf(train, "Train") then return say({ refused = "select a train" }) end
	local st, track = train.current_station, train.track
	local fields = { train = h(train), command = tostring(train.command), at_station = train.at_station,
		at_spawn_track = train.at_spawn_track, station = h(st), at_hub = is_hub(st),
		arrival_idx = tostring(train.station_arrival_track), track = h(track), cargo = cargo_of(train),
		assigned = next(train.assigned_resources or empty_table) ~= nil, passengers = #(train.units or empty_table),
		game_time = GameTime() }
	if IsValid(track) then
		fields.track_start, fields.track_end = h(track:GetStartStation()), h(track:GetEndStation())
		local ok, nxt = pcall(train.GetNextStation, train)
		fields.next_station = ok and h(nxt) or "error"
	end
	if is_hub(st) and IsValid(track) then fields.hub_idx = tostring(st:GetConnectionSpot(track)) end
	local last = P.last
	if last and last.train == train.handle then
		fields.dispatched_to_track, fields.dispatched_to_station = last.new_track, last.new_station
		local routes = train.city and train.city.train_track_routes or empty_table
		fields.on_dispatched_line = IsValid(track) and (h(track) == last.new_track or routes[track] == last.route) or false
	end
	return say(fields)
end

-- Move one parked, empty hub train onto another of that hub's lines, then hand it
-- to vanilla with Train:Start (the NewHour restart path, Train.lua:64-70,133-140).
function P.Run(train, want_idx)
	train = train or SelectedObj
	if not IsValid(train) or not IsKindOf(train, "Train") then return say({ refused = "select a train" }) end
	local hub = train.current_station
	if not is_hub(hub) or not train.at_station then return say({ refused = "train is not parked at a hub", train = h(train) }) end
	if P.last and P.last.train == train.handle then return say({ refused = "already dispatched; Read it, or Forget() first", train = h(train) }) end
	-- A parked idle train has no command at all; vanilla's NewHour treats that as idle (Train.lua:63).
	if train.command and train.command ~= "Idle" and train.command ~= "LoadTrain" then return say({ refused = "command is " .. tostring(train.command), train = h(train) }) end
	if next(train.assigned_resources or empty_table) then return say({ refused = "train carries cargo assigned to a station", train = h(train) }) end
	if #(train.units or empty_table) > 0 then return say({ refused = "train carries passengers", train = h(train) }) end
	if train.is_stopping then return say({ refused = "train is headed for refab", train = h(train) }) end
	local old = train.track
	local old_route = IsValid(old) and hub.city.train_track_routes[old]
	local chosen
	for _, line in ipairs(P.Lines(hub)) do
		local other = line.route ~= old_route
		if other and (not want_idx or want_idx == line.idx) and line.trains < line.cap then
			if not chosen or (chosen.occupied and not line.occupied) then chosen = line end
		end
	end
	if not chosen then
		-- Name each line's route load so a refusal says which cap is full (idx:station:trains/cap, * = own route).
		local detail = {}
		for _, line in ipairs(P.Lines(hub)) do
			detail[#detail + 1] = line.idx .. ":" .. h(line.station) .. ":" .. line.trains .. "/" .. line.cap
				.. (line.route == old_route and "*" or "")
		end
		return say({ refused = "no other hub line with vanilla route room", train = h(train),
			lines = table.concat(detail, ",") })
	end
	local before = { old_track = h(old), old_idx = tostring(IsValid(old) and hub:GetConnectionSpot(old)),
		arrival_idx = tostring(train.station_arrival_track), command = tostring(train.command) }
	-- Vanilla's own placement order (Track.lua:448-455): the link's cap gate, then the membership move.
	if IsValid(old) then old:RemoveTransportLink(train) end
	if not chosen.track:AddTransportLink(train) then
		if IsValid(old) then old:AddTransportLink(train) end
		return say({ refused = "AddTransportLink refused on the new line", train = h(train) })
	end
	train:AssignToTrack(chosen.track)
	train:Start()
	P.last = { train = train.handle, new_track = h(chosen.track), new_station = h(chosen.station),
		new_idx = chosen.idx, route = chosen.route, game_time = GameTime() }
	return say({ mutation = "RemoveTransportLink+AddTransportLink+AssignToTrack+Start", train = h(train), hub = h(hub),
		old_track = before.old_track, old_idx = before.old_idx, arrival_idx = before.arrival_idx,
		command_before = before.command, command_after = tostring(train.command),
		new_track = h(chosen.track), new_idx = chosen.idx, new_station = h(chosen.station),
		new_arm_occupied = h(chosen.occupied), route_trains = chosen.trains, route_cap = chosen.cap,
		game_time = GameTime() })
end

function P.Forget() P.last = false return say({ forgot = true }) end

print("[HubDispatchProbe] loaded; Run/Read/Forget on SMROptInHubDispatchProbe")
