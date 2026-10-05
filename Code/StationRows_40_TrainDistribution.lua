-- Distribution centre (module StationRows, Code/Opt_StationRows.lua; moved from the train hub
-- dev mod by brief 34, 2026-10-02). Authority: Train_Hub_Project/09, pass 4;
-- owner rulings in TRAIN_LOGISTICS_DESIGN_20260917.md section 4.8.
-- Archived game 1.1.1.405907: Units/Train.lua:744-831,862-1043;
-- Buildings/Station.lua:964-997; MultiResourceDepot.lua:217-245,380-407.
-- No train body copy. Synchronous getter answers + claims supply vanilla's
-- allocator with a source having no capacity share and destinations whose
-- effective capacity is their remaining order (at least one resource unit).
-- Demand claims retain the exact order. Vanilla owns every cargo write.
-- Rung 0: these answers/claims; rung 1: vanilla-written drone desired amounts;
-- rung 2: SMROptIn_distribution, one table on each hub, keyed by station object,
-- then resource, containing {mode, percent}.
-- Brief 30: SMROptIn_station_rows is an inert {resource = {mode, percent}}
-- table on an ordinary station. It is dormant while a hub owns that station;
-- hub settings never migrate into it. Hubless baselines are restored to vanilla
-- during saving, so removing the mod leaves only ignored settings data.
-- Hub baselines linger without the mod until vanilla rewrites desired amounts.
-- Brief 34b (owner 2026-10-02): Export pairings keep storage's own Desired Amount,
-- including already booked pickups. Vanilla's send baseline stays intact.
-- No thread, captured yielding frame, saved callback or standing claim.

SMROptInTrainDistribution = {}
local D = SMROptInTrainDistribution
local Floor = rawget(_G, "SMROptInTrainFloor")
local FIELD = "SMROptIn_distribution"
D.FIELD, D.calls = FIELD, 0
local LOCAL_FIELD = "SMROptIn_station_rows"
D.LOCAL_FIELD = LOCAL_FIELD
local view, baseline, saving = false, false, false
local owners, hubs, parents, children, cache_time = {}, {}, {}, {}, false
local applied = setmetatable({}, { __mode = "k" })
local calls_by_station = setmetatable({}, { __mode = "k" })
-- An actual hub unload refusal, not an allocation view, authorizes overflow
-- on the return trip. Runtime only: loading a save requires a new hub attempt.
local refused = setmetatable({}, { __mode = "k" })
function D.CallsFor(st) return calls_by_station[st] or 0 end

-- Standalone dev-mod Require: no dependency on the shipping pack. Include
-- declaring methods AND early-bound aliases; check before installing anything.
D.Require = {
	{ "TaskRequestHub", "FindTask" }, { "TaskRequestHub", "FindSupplyRequest" },
	{ "Train", "TransferCargo" }, { "Train", "UnloadAll" },
	{ "Station", "SetDesiredAmount" }, { "Station", "GetTrainTransportPolicy" },
	{ "Station", "GetResDesiredAmount" }, { "Station", "SetAcceptResourceState" },
	{ "Station", "BuildingUpdate" },
	{ "MultiResourceCubeVisuals", "GetMaxStorage" },
	{ "MultiResourceCubeVisuals", "SetCount" },
	{ "MultiResourceDepotBase", "SetCount" },
	{ "MultiResourceCubeVisuals", "GetMaxStorageForAnyOneResource" },
	{ "MultiResourceDepotBase", "GetMaxStorage" },
	{ "MultiResourceDepotBase", "GetMaxStorageForAnyOneResource" },
	{ "MultiResourceDepotBase", "IsResourceEnabled" },
	{ "MultiResourceDepotBase", "UpdateRequestCapacity" },
	{ "MultiResourceDepotBase", "OnModifiableValueChanged" },
	{ "MultiResourceDepotBase", "RecalculateAfterResourceListChange" },
}
for _, pair in ipairs(D.Require) do
	local class = rawget(_G, pair[1])
	if not class or type(class[pair[2]]) ~= "function" then
		D.error = pair[1] .. "." .. pair[2] .. " unavailable"
		print("[TrainDistribution] inactive: " .. D.error)
		return
	end
end
if not Floor or type(Floor.WithTransientClaims) ~= "function" then
	D.error = "train floor helper unavailable"
	return
end

local function is_hub(o)
	return IsValid(o) and IsKindOf(o, "SMROptInTrainHubBase")
end

-- Elevator Depot (brief 27, spec section 11 ruling 2): the depot owns its rows and the
-- hub reads them through its HubEntry; the hub never stores a row for a depot. Absent
-- depot mod: both answer nil and the hub behaves as before.
local function is_depot(st)
	local depot = rawget(_G, "SMRElevatorDepot")
	return depot and type(depot.IsDepot) == "function" and depot.IsDepot(st) or false
end
local function depot_entry(st, res)
	local depot = rawget(_G, "SMRElevatorDepot")
	if depot and type(depot.HubEntry) == "function" then return depot.HubEntry(st, res) end
end
D.IsDepotStation = is_depot

function D.IsRowStation(st)
	return IsValid(st) and IsKindOf(st, "Station") and not is_hub(st) and not is_depot(st)
end

-- The shipping gate (brief 34; owner 2026-10-02, spec §10 "Brief 34's checkpoint"). A hub's
-- network always has its rows: they are part of the hub, which keeps working with its module off.
-- A HUBLESS station has them while Station rows is on, and always while the Train Hub is on.
-- Without the framework (the desk harnesses) the rows stay on, as the dev mod shipped them.
local function hubless_on()
	local P = rawget(_G, "SMROptInPack")
	if type(P) ~= "table" or type(P.IsActive) ~= "function" then return true end
	return P.IsActive("StationRows") or P.IsActive("TrainHub")
end
D.HublessOn = hubless_on

local function station_rows(st, hub)
	if hub then
		local rows = rawget(hub, FIELD)
		return rows and rows[st]
	end
	return D.IsRowStation(st) and hubless_on() and rawget(st, LOCAL_FIELD) or nil
end

function D.Refresh()
	owners, hubs, parents, children = {}, {}, {}, {}
	local colony = rawget(_G, "UIColony")
	for _, st in ipairs(colony and colony.labels.Station or empty_table) do
		if is_hub(st) and not st.destroyed then hubs[#hubs + 1] = st end
	end
	table.sort(hubs, function(a, b) return a.handle < b.handle end)
	for _, hub in ipairs(hubs) do
		local nodes = hub:HubTrackGraph()
		for st in pairs(nodes) do
			if not is_hub(st) and IsValid(st) and IsKindOf(st, "Station") then
				local old = owners[st]
				-- Keep an existing hub's saved settings when hubs share a graph.
				if not old or (not (rawget(old, FIELD) or empty_table)[st]
					and (rawget(hub, FIELD) or empty_table)[st]) then owners[st] = hub end
			end
		end
	end
	-- One hop is one train line. A breadth-first tree gives every station one
	-- upstream stop; ties use station handle order. Nothing persists.
	for _, hub in ipairs(hubs) do
		-- Routes are map-local City state, not Colony state (archived
		-- 1.1.1.405907 City.lua:33, TrainTransport.lua:305-308).
		local routes = hub.city and hub.city.train_track_routes or empty_table
		local distance, queue = { [hub] = 0 }, { hub }
		local cursor = 1
		while queue[cursor] do
			local source = queue[cursor]
			cursor = cursor + 1
			local adjacent = {}
			for _, line in pairs(routes) do
				if table.find(line, source) then
					for _, dest in ipairs(line) do
						if dest ~= source and (dest == hub or owners[dest] == hub) then
							adjacent[#adjacent + 1] = dest
						end
					end
				end
			end
			table.sort(adjacent, function(a, b) return a.handle < b.handle end)
			for _, dest in ipairs(adjacent) do
				if not distance[dest] then
					distance[dest] = distance[source] + 1
					parents[dest] = source
					children[source] = children[source] or {}
					children[source][#children[source] + 1] = dest
					queue[#queue + 1] = dest
				end
			end
		end
	end
	cache_time = GameTime()
end

function D.Parent(st) return parents[st] end

function D.HubFor(st)
	if not IsValid(st) or is_hub(st) then return end
	if not cache_time or GameTime() - cache_time >= 1000 then D.Refresh() end
	local hub = owners[st]
	return is_hub(hub) and not hub.destroyed and hub or nil
end

function D.Get(st, res)
	local hub = D.HubFor(st)
	local own = depot_entry(st, res)
	if own ~= nil then return own or nil, hub end
	local rows = station_rows(st, hub)
	return rows and rows[res], hub
end

local enabled = MultiResourceDepotBase.IsResourceEnabled
local set_desired = Station.SetDesiredAmount
local function ready(st, res)
	return IsValid(st) and st.supply and st.demand and st.supply[res]
		and st.demand[res] and enabled(st, res)
end

local function amount(st, res, entry)
	if entry.amount ~= nil then return entry.amount end
	return MulDivRound(st:GetMaxStorage(res), entry.percent, 100)
end

-- An untouched row is Balanced at the live vanilla dial, not at a rounded
-- percentage. This value exists only for the call; D.Get still reads settings.
local function effective(st, res, hub)
	if not hub then
		if not D.IsRowStation(st) or not hubless_on() then return end
		local rows = rawget(st, LOCAL_FIELD)
		return rows and rows[res] or { mode = "balanced", amount = st.desired_amount or 0 }
	end
	if is_hub(st) then return end
	local own = depot_entry(st, res)
	if own then return own end
	local rows = own == nil and rawget(hub, FIELD)
	local entry = rows and rows[st] and rows[st][res]
	if entry then return entry end
	if D.HubFor(st) == hub then return { mode = "balanced", amount = st.desired_amount or 0 } end
end

function D.Effective(st, res)
	local hub = D.HubFor(st)
	return effective(st, res, hub), hub
end

-- Archived 1.1.1.406343 Lua/_TaskRequest.lua:65-86: FindTask returns an
-- unassigned supply/demand pair; FindSupplyRequest supports exclude_building.
-- Installed before class flattening, so every controller inherits the wrapper.
-- The one retry is the starvation guard: the rejected source cannot win it.
-- No recursive FindTask or queue scan; if the alternative also has no surplus,
-- return no task; the live smoke must prove continued traffic across retries.
local find_task = TaskRequestHub.FindTask
local pairing_stats = { capped = 0, retried = 0, substituted = 0, refused = 0 }
D.ExportPairingStats = pairing_stats
local function export_surplus(supply, n)
	if supply:IsAnyFlagSet(const.rfStorageDepot) then
		-- Target subtracts outstanding pickups. Actual alone would promise the same
		-- surplus to several drones (Drone.lua:1130-1139 assigns before travelling).
		return Min(n, Min(supply:GetActualAmount(), supply:GetTargetAmount()) - supply:GetDesiredAmount())
	end
	return n -- producer output / loose piles keep the engine's amount
end
local function assignable_pair(supply, demand, n)
	return n > 0 and (n >= const.ResourceScale
		or not (supply:IsAnyFlagSet(const.rfWaitToFill) or demand:IsAnyFlagSet(const.rfWaitToFill)))
		and supply:CanAssignUnit(n) and demand:CanAssignUnit(n)
end
function TaskRequestHub:FindTask(agent, ...)
	local supply, demand, res, n, priority = find_task(self, agent, ...)
	if saving or not supply or not demand or not res or not n
		or not supply:IsAnyFlagSet(const.rfSupply) or not demand:IsAnyFlagSet(const.rfDemand)
		or not supply:IsAnyFlagSet(const.rfStorageDepot) then
		return supply, demand, res, n, priority
	end
	local st = demand:GetSource(agent)
	if not D.IsRowStation(st) or not st.demand or st.demand[res] ~= demand or not enabled(st, res) then
		return supply, demand, res, n, priority
	end
	local entry = D.Get(st, res)
	if not entry or entry.mode ~= "export" then return supply, demand, res, n, priority end
	local take = export_surplus(supply, n)
	if take == n then return supply, demand, res, n, priority end
	if assignable_pair(supply, demand, take) then
		pairing_stats.capped = pairing_stats.capped + 1
		return supply, demand, res, take, priority
	end
	-- Keep special pairing compatibility just as Drone:ImproveDemandRequest does
	-- (Drone.lua:845-846). The engine retains distance, reachability and slots.
	pairing_stats.retried = pairing_stats.retried + 1
	local ignore = (~demand:GetFlags()) & (const.rfSpecialDemandPairing | const.rfSpecialSupplyPairing)
	local excluded = supply:GetSource(agent)
	local other, offered = self:FindSupplyRequest(agent, res, n, nil, ignore, nil, excluded)
	if other and other ~= supply and offered then
		local source = other:GetSource(agent)
		-- The standalone supply finder has no destination argument: it can offer
		-- this station's own supply. Such a self-haul is not a substitute pairing.
		if IsValid(source) and source ~= st and source ~= excluded then
			take = export_surplus(other, Min(n, Min(offered, demand:GetTargetAmount())))
			if assignable_pair(other, demand, take) then
				pairing_stats.substituted = pairing_stats.substituted + 1
				return other, demand, res, take, priority
			end
		end
	end
	pairing_stats.refused = pairing_stats.refused + 1
	return nil
end

local function line_has_hub(train, track, hub)
	if not hub or not (train.city and train.city.train_track_routes[track]) then return false end
	local found = false
	ForEachStationAlongTrack(train.current_station, track, const.trfInclusive | const.trfBidirectional, function(st)
		if st == hub then found = true end
	end)
	return found
end

local function line_managed(train, track, st, hub)
	if not hub or not (train.city and train.city.train_track_routes[track]) then return false end
	if line_has_hub(train, track, hub) then return true end
	local found = false
	ForEachStationAlongTrack(st, track, const.trfInclusive | const.trfBidirectional, function(o)
		if o == parents[st] then found = true end
		if o ~= st and owners[o] == hub then found = true end
		for _, child in ipairs(children[st] or empty_table) do
			if o == child then found = true end
		end
	end)
	return found
end

-- IsResourceEnabled is an alias of IsStoring. Wrap the consumed alias, never
-- IsStoring, which also controls the persistent demand flags.
function MultiResourceDepotBase:IsResourceEnabled(res)
	local row = view and view[self] and view[self][res]
	if row then return row.enabled end
	return enabled(self, res)
end

-- Drawing is synchronous inside TransferCargo's allocation view. Give only
-- that receiver physical capacity while vanilla draws; keep allocation intact.
local drawing = setmetatable({}, { __mode = "k" })
local function draw_wrapper(previous)
	return function(self, ...)
		if not (view and view[self]) or is_hub(self) then return previous(self, ...) end
		local before = drawing[self]
		drawing[self] = true
		local result = table.pack(pcall(previous, self, ...))
		drawing[self] = before
		if not result[1] then error(result[2], 0) end
		return table.unpack(result, 2, result.n)
	end
end
MultiResourceCubeVisuals.SetCount = draw_wrapper(MultiResourceCubeVisuals.SetCount)
MultiResourceDepotBase.SetCount = draw_wrapper(MultiResourceDepotBase.SetCount)

local function capacity_wrapper(previous)
	return function(self, res, ...)
		local row = not drawing[self] and view and view[self] and view[self][res]
		if row and row.capacity then return row.capacity end
		return previous(self, res, ...)
	end
end
MultiResourceCubeVisuals.GetMaxStorage = capacity_wrapper(MultiResourceCubeVisuals.GetMaxStorage)
MultiResourceDepotBase.GetMaxStorage = capacity_wrapper(MultiResourceDepotBase.GetMaxStorage)

local function one_capacity_wrapper(previous)
	return function(self, ...)
		if baseline and baseline.station == self then return baseline.capacity end
		return previous(self, ...)
	end
end
MultiResourceCubeVisuals.GetMaxStorageForAnyOneResource = one_capacity_wrapper(MultiResourceCubeVisuals.GetMaxStorageForAnyOneResource)
MultiResourceDepotBase.GetMaxStorageForAnyOneResource = one_capacity_wrapper(MultiResourceDepotBase.GetMaxStorageForAnyOneResource)

local policy = Station.GetTrainTransportPolicy
function Station:GetTrainTransportPolicy(res)
	if baseline and baseline.station == self and baseline.res == res then return baseline.policy end
	return policy(self, res)
end
local desired = Station.GetResDesiredAmount
function Station:GetResDesiredAmount(res)
	local row = view and view[self] and view[self][res]
	-- Keep the positive-desire lane open despite an import's zero drone target.
	if row then return row.enabled and const.ResourceScale or 0 end
	return desired(self, res)
end

local function restore_baseline()
	if baseline then
		baseline.station.demand = baseline.demand
		baseline.station.desired_amount = baseline.dial
		baseline = false
	end
end

local function vanilla_baseline(st)
	local dial = st.desired_amount
	st.desired_amount = false
	set_desired(st, dial)
end

function D.Apply(st)
	if saving or baseline or view or not IsValid(st) or is_hub(st) or is_depot(st) then return end
	local hub = D.HubFor(st)
	local rows = station_rows(st, hub)
	-- Joining/leaving a hub changes the owner of the rows. Restore resources
	-- present only in the previous set before applying the newly active set.
	if applied[st] and applied[st] ~= rows then
		vanilla_baseline(st)
		applied[st] = nil
	end
	if not rows then
		return
	end
	for res, entry in pairs(rows) do
		if ready(st, res) then
			baseline = { station = st, res = res, demand = st.demand, dial = st.desired_amount,
				capacity = st:GetMaxStorage(res), policy = entry.mode == "export" and "send"
					or entry.mode == "import" and "accept" or "default" }
			local n = amount(st, res, entry)
			-- Vanilla writes this resource. Restore the dial/map even on errors.
			st.demand = { [res] = baseline.demand[res] }
			st.desired_amount = false
			local ok, why = pcall(set_desired, st, n)
			restore_baseline()
			if not ok then D.error = tostring(why) end
		end
	end
	applied[st] = rows
end

function D.Set(st, res, mode, percent)
	if mode ~= "export" and mode ~= "import" and mode ~= "balanced" then return false, "invalid mode" end
	if type(percent) ~= "number" or percent ~= percent or percent < 0 or percent > 100 then
		return false, "slider must be 0 to 100 percent"
	end
	if not ready(st, res) or is_hub(st) then return false, "enable this resource at a station" end
	if is_depot(st) then return false, "the Elevator Depot owns this row" end
	if not D.IsRowStation(st) then return false, "not a station resource row" end
	D.Refresh()
	local hub = D.HubFor(st)
	if not hub and not hubless_on() then return false, "Station rows is off" end
	local rows
	if hub then
		local all = rawget(hub, FIELD) or {}
		rawset(hub, FIELD, all)
		all[st] = all[st] or {}
		rows = all[st]
	else
		rows = rawget(st, LOCAL_FIELD) or {}
		rawset(st, LOCAL_FIELD, rows)
	end
	rows[res] = { mode = mode, percent = percent }
	D.Apply(st)
	ObjModified(st)
	return true
end

function D.Reset(st, res)
	D.Refresh()
	local colony = rawget(_G, "UIColony")
	for _, station in ipairs(st and { st } or colony and colony.labels.Station or empty_table) do
		local rows = D.IsRowStation(station) and rawget(station, LOCAL_FIELD)
		if rows then
			if res then rows[res] = nil end
			if not res or not next(rows) then rawset(station, LOCAL_FIELD, nil) end
			vanilla_baseline(station)
			D.Apply(station)
			ObjModified(station)
		end
	end
	for _, hub in ipairs(hubs) do
		local rows = rawget(hub, FIELD) or empty_table
		for station, resources in pairs(rows) do
			if not st or station == st then
				if res then resources[res] = nil else rows[station] = nil end
				if not next(resources) then rows[station] = nil end
				if IsValid(station) then
					local dial = station.desired_amount
					station.desired_amount = false
					set_desired(station, dial)
					D.Apply(station)
					ObjModified(station)
				end
			end
		end
	end
end

local function after(previous)
	return function(self, ...)
		local result = table.pack(previous(self, ...))
		if not saving and not view and not baseline
			and (owners[self] or applied[self] or rawget(self, LOCAL_FIELD)) then D.Apply(self) end
		return table.unpack(result, 1, result.n)
	end
end
Station.SetDesiredAmount = after(Station.SetDesiredAmount)
Station.SetAcceptResourceState = after(Station.SetAcceptResourceState)
MultiResourceDepotBase.UpdateRequestCapacity = after(MultiResourceDepotBase.UpdateRequestCapacity)
MultiResourceDepotBase.OnModifiableValueChanged = after(MultiResourceDepotBase.OnModifiableValueChanged)
-- The enclosing hook catches request creation through RegisterResourceRequest's
-- captured alias, without wrapping that alias or missing its new requests.
MultiResourceDepotBase.RecalculateAfterResourceListChange = after(MultiResourceDepotBase.RecalculateAfterResourceListChange)
local update = Station.BuildingUpdate
function Station:BuildingUpdate(...)
	local result = table.pack(update(self, ...))
	D.Apply(self)
	return table.unpack(result, 1, result.n)
end

local function with_view(answers, claims, fn, ...)
	local old = view
	view = answers
	local result = table.pack(Floor.WithTransientClaims(claims, fn, ...))
	view = saving and false or old
	return table.unpack(result, 1, result.n)
end

-- Net need of a branch. A surplus can feed a sibling before the hub supplies
-- it; an Export below its floor does not request a train delivery for itself.
local function branch_need(st, res)
	local net = 0
	if not is_hub(st) then
		local entry = effective(st, res, D.HubFor(st))
		if entry and ready(st, res) then
			local stock = st.supply[res]:GetActualAmount()
			local reserved = Max(st.demand[res]:GetActualAmount() - st.demand[res]:GetTargetAmount(), 0)
			local target = amount(st, res, entry)
			net = entry.mode == "export" and -Max(stock - target, 0)
				or target - stock - reserved
		end
	end
	for _, child in ipairs(children[st] or empty_table) do
		net = net + branch_need(child, res)
	end
	return net
end

local function child_need(st, res)
	local n = 0
	for _, child in ipairs(children[st] or empty_table) do
		n = n + Max(branch_need(child, res), 0)
	end
	return n
end
-- Read-only exports for the train bay's need signal (brief Train_Hub_Project/13).
D.BranchNeed, D.ChildNeed = branch_need, child_need

local function dump_route(train, hub)
	local members, gateway, depth = {}, nil, nil
	ForEachStationAlongTrack(train.current_station, train.track,
		const.trfInclusive | const.trfBidirectional, function(st)
			members[st] = true
			local at, n = st, 0
			while at and at ~= hub do at, n = parents[at], n + 1 end
			if at == hub and (not depth or n < depth or n == depth and st.handle < gateway.handle) then
				gateway, depth = st, n
			end
		end)
	return members, gateway
end

local function needs_dump(train, res, members, hub)
	local loose = (train.stockpiled_amount or empty_table)[res] or 0
	if loose <= 0 then return false end
	for dest, cargo in pairs(train.assigned_resources or empty_table) do
		local n = cargo[res] or 0
		loose = loose - n
		if n > 0 then
			if not members[dest] or not ready(dest, res) then return true end
			local entry = effective(dest, res, hub)
			if entry and (entry.mode == "export" or n > Max(amount(dest, res, entry)
				+ child_need(dest, res) - dest.supply[res]:GetActualAmount(), 0)) then return true end
		end
	end
	return loose > 0
end

-- Old inbound reservations may predate a mode change. Vanilla keeps a cargo
-- entry aboard if it no longer fits; the hub can receive it later. No custom
-- writes to assigned_resources, request flags or transport_policy.
local unload = Train.UnloadAll
-- A hubless line that ends at an Elevator Depot keeps its dial pins on untouched rows
-- (the depot's exchange was built and sat against them). Every other hubless line
-- leaves an untouched row to the game (owner 2026-10-05).
local function depot_line(train, st, track)
	if not (IsValid(track) and train.city and train.city.train_track_routes[track]) then return false end
	local found = false
	ForEachStationAlongTrack(st, track, const.trfInclusive | const.trfBidirectional, function(o)
		if is_depot(o) then found = true end
	end)
	return found
end
function Train:UnloadAll(...)
	local st = self.current_station
	local hub = IsValid(st) and D.HubFor(st)
	-- Hubless rows have no transit or hub-overflow exceptions. Keep a whole
	-- old assignment aboard when it exceeds the new cap; vanilla can unload
	-- it at another accepting stop. Never rewrite the cargo ledger ourselves.
	if not saving and not hub and D.IsRowStation(st) and hubless_on() then
		local old = view
		view = false
		local answers, claims = { [st] = {} }, {}
		local pinned = depot_line(self, st, self.track)
		local rows = rawget(st, LOCAL_FIELD) or empty_table
		for _, res in ipairs(st.storable_resources or empty_table) do
			-- An untouched row unloads natively; only a set row caps the delivery.
			local entry = pinned and effective(st, res) or rows[res]
			if entry and ready(st, res) then
				local d = st.demand[res]
				local room = Max(Min(amount(st, res, entry), st:GetMaxStorage(res))
					- st.supply[res]:GetActualAmount(), 0)
				local own = ((self.assigned_resources or empty_table)[st] or empty_table)[res] or 0
				local reserved = Max(d:GetActualAmount() - d:GetTargetAmount(), 0)
				answers[st][res] = { enabled = entry.mode ~= "export" and own <= room }
				claims[#claims + 1] = { d, Max(d:GetTargetAmount() - Max(room - reserved, 0), 0) }
			end
		end
		local result = table.pack(with_view(answers, claims, unload, self, ...))
		view = saving and false or old
		return table.unpack(result, 1, result.n)
	end
	local rows = hub and rawget(hub, FIELD)
	rows = rows and rows[st]
	if is_depot(st) then rows = nil end
	local defaults = line_managed(self, self.track, st, hub)
	local old = view
	view = false
	if saving or not (rows or defaults) then
		local result = table.pack(pcall(unload, self, ...))
		if result[1] and not saving and not old and is_hub(st) then
			local remaining = {}
			for res, n in pairs(self.stockpiled_amount or empty_table) do
				if n > 0 then remaining[res] = st end
			end
			refused[self] = remaining
		end
		view = saving and false or old
		if not result[1] then D.error = tostring(result[2]) return end
		return table.unpack(result, 2, result.n)
	end
	local answers, claims = { [st] = {} }, {}
	local members, gateway = dump_route(self, hub)
	for _, res in ipairs(st.storable_resources or empty_table) do
		local entry = defaults and effective(st, res, hub) or rows and rows[res]
		if entry and ready(st, res) then
			local s, d = st.supply[res], st.demand[res]
			local from_child = false
			ForEachStationAlongTrack(st, self.track, const.trfInclusive | const.trfBidirectional, function(o)
				for _, child in ipairs(children[st] or empty_table) do
					if o == child then from_child = true end
				end
			end)
			local cargo = (self.stockpiled_amount or empty_table)[res] or 0
			local rejected = (refused[self] or empty_table)[res] == hub
			local hub_room = ready(hub, res) and hub.demand[res]:GetTargetAmount() or 0
			local hub_own = ((self.assigned_resources or empty_table)[hub] or empty_table)[res] or 0
			-- Nested native unloads see allocation claims on the hub's demand.
			-- Only the outer call can decide whether real room is still absent.
			local overflow = not old and cargo > 0 and rejected and hub_room + hub_own < cargo
			-- A train cannot leave its line. Old cargo on a sideways line must
			-- enter the hubward station as transit so its upstream train can
			-- carry it to the hub. Same physical bound as child-line transit.
			local transit = not members[hub] and gateway == st and needs_dump(self, res, members, hub)
			local admit = from_child or transit or overflow
			local limit = admit and st:GetMaxStorage(res)
				or amount(st, res, entry) + child_need(st, res)
			local room = Max(Min(limit, st:GetMaxStorage(res)) - s:GetActualAmount(), 0)
			local own = ((self.assigned_resources or empty_table)[st] or empty_table)[res] or 0
			answers[st][res] = { enabled = (entry.mode ~= "export" or admit or child_need(st, res) > 0)
				and own <= room }
			local reserved = Max(d:GetActualAmount() - d:GetTargetAmount(), 0)
			claims[#claims + 1] = { d, Max(d:GetTargetAmount() - Max(room - reserved, 0), 0) }
		end
	end
	local result = table.pack(with_view(answers, claims, unload, self, ...))
	for res in pairs(refused[self] or empty_table) do
		if (self.stockpiled_amount[res] or 0) <= 0 then refused[self][res] = nil end
	end
	view = saving and false or old
	return table.unpack(result, 1, result.n)
end

-- Build from real state before installing any answers or claims.
local function train_view(train, track)
	local st = train.current_station
	local hub = is_hub(st) and st or D.HubFor(st)
	if not hub then return end
	if not (train.city and train.city.train_track_routes[track]) then return end
	local members, can_receive = {}, {}
	ForEachStationAlongTrack(st, track, const.trfInclusive | const.trfBidirectional, function(o)
		members[o] = true
	end)
	ForEachStationAlongTrack(st, track, 0, function(o, mode)
		if mode ~= "people" then can_receive[o] = true end
	end)
	local upstream = st ~= hub and members[parents[st]]
	if not members[hub] and not upstream then
		local has_child = false
		for _, child in ipairs(children[st] or empty_table) do
			if members[child] then has_child = true break end
		end
		local has_peer = false
		for dest in pairs(members) do
			if dest ~= st and owners[dest] == hub then has_peer = true break end
		end
		if not has_child and not has_peer then return end
	end
	local answers, claims = {}, {}
	for _, res in ipairs(st.storable_resources or empty_table) do
		local entry = effective(st, res, hub)
		local configured = entry and ready(st, res)
		if st == hub then
			for dest in pairs(members) do
				if parents[dest] == st and effective(dest, res, hub) and ready(dest, res) then configured = true break end
			end
		end
		if configured and ready(st, res) then
			local dumping = needs_dump(train, res, members, hub)
				or (refused[train] or empty_table)[res] == hub
			local floor = entry and amount(st, res, entry) or 0
			local routed = upstream or st == hub
			if not routed then
				for _, child in ipairs(children[st] or empty_table) do
					if members[child] then routed = true break end
				end
			end
			if not routed then floor = st.supply[res]:GetActualAmount() end
			-- A leaf Import never becomes a train source. An intermediate
			-- Import may forward stock above its own pin.
			if entry and entry.mode == "import" and not children[st] then
				floor = Max(floor, st.supply[res]:GetActualAmount())
			end
			if upstream then floor = floor + child_need(st, res) end
			-- Clear retained cargo before adding another load of that resource.
			if dumping then floor = st.supply[res]:GetActualAmount() end
			claims[#claims + 1] = { st.supply[res], floor }
			for dest in pairs(members) do
				if dest.supply and dest.supply[res] and dest.demand and dest.demand[res] then
					local order = 0
					if not dumping and dest ~= st and can_receive[dest] and ready(dest, res) then
						if upstream and dest == parents[st] then
							-- Export only stock beyond this station's floor and its
							-- downstream orders. The hub's native demand refuses a full hub.
							order = Max(dest.demand[res]:GetTargetAmount(), 0)
							if dest ~= hub and hub.demand[res] and hub.demand[res]:GetTargetAmount() <= 0 then
								local own = effective(dest, res, hub)
								local want = own and own.mode ~= "export"
									and Max(amount(dest, res, own) - dest.supply[res]:GetActualAmount(), 0) or 0
								order = Min(order, want + child_need(dest, res))
							end
						elseif not upstream and parents[dest] == st then
							order = Max(branch_need(dest, res), 0)
							order = Min(order, Max(dest.demand[res]:GetTargetAmount(), 0))
						end
					end
					answers[dest] = answers[dest] or {}
					-- Vanilla divides capacity by ResourceScale before allocating.
					-- Positive desire with a sub-unit capacity would divide by zero
					-- (archived 1.1.1.405907 Train.lua:896-897,946). Demand below
					-- still caps the real order; this does not round up a delivery.
					answers[dest][res] = { enabled = order > 0,
						capacity = order > 0 and Max(order, const.ResourceScale) or 0 }
					if dest ~= st then
						-- Capacity is an order, so its matching stored value is zero.
						-- Actual stock still contributes to vanilla's line total.
						claims[#claims + 1] = { dest.supply[res], Max(dest.supply[res]:GetTargetAmount(), 0) }
					end
					claims[#claims + 1] = { dest.demand[res], Max(dest.demand[res]:GetTargetAmount() - order, 0) }
				end
			end
		end
	end
	if not next(answers) then return end
	-- Allocation hides destination stock, so vanilla cannot also use that
	-- view to discover an empty pickup trip. Retained old cargo likewise
	-- produces has_work without next_stop when no new load is possible.
	-- Use LoadTrain's existing should-move input to make the native walk pick
	-- a stop for these trips (1.1.1.405907 Train.lua:250-264,914-918).
	local depart = false
	for dest in pairs(can_receive) do
		if dest ~= st then
			for _, res in ipairs(st.storable_resources or empty_table) do
				if ready(dest, res) then
					if (train.stockpiled_amount[res] or 0) > 0 then depart = true end
					if upstream and dest == parents[st] and branch_need(st, res) > 0 then
						local entry = effective(dest, res, hub)
						local floor = entry and amount(dest, res, entry) or 0
						if dest.supply[res]:GetTargetAmount() > floor
							or (ready(hub, res) and hub.supply[res]:GetTargetAmount() > 0) then depart = true end
					elseif not upstream and parents[dest] == st and branch_need(dest, res) < 0 then
						depart = true
					end
				end
			end
		end
	end
	return answers, claims, depart
end

-- Module A without a hub: orders belong to the stations on this train line.
-- No hub class, graph, parent tree, hub setting or scheduler is needed. A
-- non-row endpoint (the Elevator Depot) keeps its native storage/row writers;
-- only its exchange with an ordinary station is bounded by that station's row.
-- Owner 2026-10-05: an untouched row keeps the game's balancing here. A resource
-- no station on the line has set gets no answers or claims, so vanilla allocates
-- it alone. Where a row is set, an untouched station holds and orders the share
-- vanilla would leave it: line total by storage capacity (archived 1.1.1.405907
-- Train.lua:894-897,931,946). A depot line keeps the dial pins it was built on.
local function local_train_view(train, track)
	if not hubless_on() then return end
	local st = train.current_station
	if not (train.city and train.city.train_track_routes[track]) then return end
	local members, can_receive, managed = {}, {}, false
	ForEachStationAlongTrack(st, track, const.trfInclusive | const.trfBidirectional, function(o)
		members[o] = true
		if D.IsRowStation(o) then managed = true end
	end)
	if not managed then return end
	for o in pairs(members) do
		if is_hub(o) or D.HubFor(o) then return end
	end
	local pinned = false
	for o in pairs(members) do
		if is_depot(o) then pinned = true break end
	end
	ForEachStationAlongTrack(st, track, 0, function(o, mode)
		if mode ~= "people" then can_receive[o] = true end
	end)
	local function saved(o, res)
		local rows = D.IsRowStation(o) and rawget(o, LOCAL_FIELD)
		return rows and rows[res] or nil
	end
	local function row(o, res)
		if pinned then return effective(o, res) end
		return saved(o, res)
	end
	local function configured(res)
		if pinned then return true end
		for o in pairs(members) do
			if saved(o, res) then return true end
		end
		return false
	end
	local totals = {}
	local function share(o, res)
		local line = totals[res]
		if not line then
			line = { total = train.stockpiled_amount[res] or 0, storage = 0 }
			for member in pairs(members) do
				if member.supply and member.supply[res] then
					line.total = line.total + member.supply[res]:GetActualAmount()
					if ready(member, res) then line.storage = line.storage + member:GetMaxStorage(res) end
				end
			end
			totals[res] = line
		end
		if line.storage <= 0 then return 0 end
		return Min(MulDivRound(line.total, o:GetMaxStorage(res), line.storage), o:GetMaxStorage(res))
	end
	local function order(o, res)
		if not ready(o, res) then return 0 end
		local entry = row(o, res)
		local d = o.demand[res]
		local target
		if entry then
			if entry.mode == "export" then return 0 end
			target = amount(o, res, entry)
		elseif D.IsRowStation(o) then
			target = share(o, res)
		else
			return Max(d:GetTargetAmount(), 0)
		end
		local reserved = Max(d:GetActualAmount() - d:GetTargetAmount(), 0)
		return Max(Min(target - o.supply[res]:GetActualAmount() - reserved, d:GetTargetAmount()), 0)
	end
	local function floor(o, res)
		if not ready(o, res) then return 0 end
		local entry = row(o, res)
		if not entry then return D.IsRowStation(o) and share(o, res) or 0 end
		return entry.mode == "import" and o.supply[res]:GetActualAmount() or amount(o, res, entry)
	end
	local answers, claims, depart = {}, {}, false
	for _, res in ipairs(st.storable_resources or empty_table) do
		if st.supply and st.supply[res] and configured(res) then
			claims[#claims + 1] = { st.supply[res], floor(st, res) }
			for dest in pairs(members) do
				if dest.supply and dest.supply[res] and dest.demand and dest.demand[res] then
					local wanted = dest ~= st and can_receive[dest] and order(dest, res) or 0
					answers[dest] = answers[dest] or {}
					answers[dest][res] = { enabled = wanted > 0,
						capacity = wanted > 0 and Max(wanted, const.ResourceScale) or 0 }
					if dest ~= st then
						claims[#claims + 1] = { dest.supply[res], Max(dest.supply[res]:GetTargetAmount(), 0) }
						-- The native allocator cannot discover a pickup after its
						-- destination stock is hidden. Its existing should-move
						-- input makes the native stop selection visit the supplier.
						if can_receive[dest] and ((order(st, res) > 0
							and dest.supply[res]:GetTargetAmount() > floor(dest, res))
							or wanted > 0 and (train.stockpiled_amount[res] or 0) > 0) then depart = true end
					end
					claims[#claims + 1] = { dest.demand[res], Max(dest.demand[res]:GetTargetAmount() - wanted, 0) }
				end
			end
		end
	end
	if next(answers) then return answers, claims, depart end
end

local transfer = Train.TransferCargo
function Train:TransferCargo(next_track, train_inbound, ...)
	if saving or view then return transfer(self, next_track, train_inbound, ...) end
	local st = self.current_station
	if not IsValid(st) or not IsKindOf(st, "Station") then return transfer(self, next_track, train_inbound, ...) end
	local on_hub = is_hub(st) or D.HubFor(st)
	-- Include this train's own delivery before computing floors and orders.
	self:UnloadAll()
	if is_hub(st) then Floor.Reconcile(st) end
	local build_view = on_hub and train_view or local_train_view
	local answers, claims, depart = build_view(self, next_track or self.track)
	if not answers then return transfer(self, next_track, train_inbound, ...) end
	D.calls = D.calls + 1
	calls_by_station[st] = D.CallsFor(st) + 1
	return with_view(answers, claims, transfer, self, next_track,
		train_inbound or (depart and not self.is_stopping), ...)
end

-- Whether a station shows and applies the rows now: always on a hub's network, else per the gate.
function D.RowsOn(st)
	return D.IsRowStation(st) and (hubless_on() or D.HubFor(st) ~= nil)
end

function D.HasDroneCoverage(st)
	for _, cc in ipairs(st.command_centers or empty_table) do
		if IsValid(cc) and cc:CanCommandDrones() and cc:IsInWorkRange(st) then return true end
	end
	return false
end

function D.Status(st, res)
	local entry, hub = D.Effective(st, res)
	if not entry or not ready(st, res) then return false, "resource is not a station row/enabled" end
	local s, d, scale = st.supply[res], st.demand[res], const.ResourceScale
	local result = { mode = entry.mode, percent = entry.percent, slider = amount(st, res, entry),
		stock = s:GetActualAmount(), supply_target = s:GetTargetAmount(), demand_target = d:GetTargetAmount(),
		supply_desired = s:GetDesiredAmount(), demand_desired = d:GetDesiredAmount(),
		covered = D.HasDroneCoverage(st), hub = hub, calls = D.calls,
		full = hub and (not hub.demand[res] or hub.demand[res]:GetTargetAmount() <= 0) or false,
		transient = view and true or false }
	print(string.format("[TrainDistribution] station=%s res=%s mode=%s slider=%.3f stock=%.3f supply=%.3f/%.3f demand=%.3f/%.3f covered=%s hub_full=%s calls=%d",
		tostring(st.handle), res, entry.mode, result.slider/scale, result.stock/scale,
		result.supply_target/scale, result.supply_desired/scale, result.demand_target/scale,
		result.demand_desired/scale, tostring(result.covered), tostring(result.full), D.calls))
	return result
end

function D.Reapply()
	D.Refresh()
	local colony = rawget(_G, "UIColony")
	for _, st in ipairs(colony and colony.labels.Station or empty_table) do D.Apply(st) end
end
function OnMsg.SaveGameStart()
	saving = true
	view = false
	restore_baseline()
	Floor.ReleaseTransientClaims()
	-- Inert custom rows can survive removal; inaccessible vanilla policy or
	-- desired amounts must not. transport_policy is never written by this file.
	for st in pairs(applied) do
		if D.IsRowStation(st) and not D.HubFor(st) then vanilla_baseline(st) end
	end
end
function OnMsg.SaveGameDone()
	saving = false
	D.Reapply()
end
function OnMsg.LoadGame()
	saving, view, baseline = false, false, false
	refused = setmetatable({}, { __mode = "k" })
	applied = setmetatable({}, { __mode = "k" })
	D.Reapply()
	-- Saved empty cube arrays can outlive the transfer that erased them.
	-- Refresh managed station visuals from physical stock after clearing the view.
	for station in pairs(owners) do
		if IsValid(station) and station.has_visual_cubes then
			for _, resource in ipairs(station.storable_resources or empty_table) do
				station:UpdateVisualCount(resource)
			end
		end
	end
end
function OnMsg.CityStart() D.Reapply() end
function OnMsg.DoneGame()
	view, baseline, cache_time = false, false, false
	refused = setmetatable({}, { __mode = "k" })
	owners, hubs = {}, {}
end

D.active = true
print("[TrainDistribution] station rows loaded (brief 30: hub + hubless)")
