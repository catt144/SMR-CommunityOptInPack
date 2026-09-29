-- Distribution centre, dev only. Authority: Train_Hub_Project/09, pass 4;
-- owner rulings in TRAIN_LOGISTICS_DESIGN_20260917.md section 4.8.
-- Archived game 1.1.1.405907: Units/Train.lua:744-831,862-1043;
-- Buildings/Station.lua:964-997; MultiResourceDepot.lua:217-245,380-407.
-- No train body copy. Synchronous getter answers + claims supply vanilla's
-- allocator with a source having no capacity share and destinations whose
-- effective capacity is their remaining order (at least one resource unit).
-- Demand claims retain the exact order. Vanilla owns every cargo write.
-- Rung 0: these answers/claims; rung 1: vanilla-written drone desired amounts;
-- rung 2: SMROptIn_distribution, one table on each hub, keyed by station object,
-- then resource, containing {mode, percent}. No custom field on vanilla objects.
-- Baselines linger without the mod until vanilla rewrites its desired amounts.
-- No thread, captured yielding frame, saved callback or standing claim.

SMROptInTrainDistribution = {}
local D = SMROptInTrainDistribution
local Floor = rawget(_G, "SMROptInTrainFloor")
local FIELD = "SMROptIn_distribution"
D.FIELD, D.calls = FIELD, 0
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
	local rows = hub and rawget(hub, FIELD)
	return rows and rows[st] and rows[st][res], hub
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
	if not hub or is_hub(st) then return end
	local rows = rawget(hub, FIELD)
	local entry = rows and rows[st] and rows[st][res]
	if entry then return entry end
	if D.HubFor(st) == hub then return { mode = "balanced", amount = st.desired_amount or 0 } end
end

function D.Effective(st, res)
	local hub = D.HubFor(st)
	return effective(st, res, hub), hub
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

function D.Apply(st)
	if saving or baseline or view or not IsValid(st) or is_hub(st) then return end
	local hub = D.HubFor(st)
	local rows = hub and rawget(hub, FIELD)
	rows = rows and rows[st]
	if not rows then
		if applied[st] then
			local dial = st.desired_amount
			st.desired_amount = false
			set_desired(st, dial)
			applied[st] = nil
		end
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
	applied[st] = true
end

function D.Set(st, res, mode, percent)
	if mode ~= "export" and mode ~= "import" and mode ~= "balanced" then return false, "invalid mode" end
	if type(percent) ~= "number" or percent ~= percent or percent < 0 or percent > 100 then
		return false, "slider must be 0 to 100 percent"
	end
	if not ready(st, res) or is_hub(st) then return false, "enable this resource at a station" end
	D.Refresh()
	local hub = D.HubFor(st)
	if not hub then return false, "connect this station to a distribution hub" end
	local rows = rawget(hub, FIELD) or {}
	rawset(hub, FIELD, rows)
	rows[st] = rows[st] or {}
	rows[st][res] = { mode = mode, percent = percent }
	D.Apply(st)
	ObjModified(st)
	return true
end

function D.Reset(st, res)
	D.Refresh()
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
		if not saving and not view and not baseline and (owners[self] or applied[self]) then D.Apply(self) end
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
function Train:UnloadAll(...)
	local st = self.current_station
	local hub = IsValid(st) and D.HubFor(st)
	local rows = hub and rawget(hub, FIELD)
	rows = rows and rows[st]
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

local transfer = Train.TransferCargo
function Train:TransferCargo(next_track, train_inbound, ...)
	if saving or view then return transfer(self, next_track, train_inbound, ...) end
	local st = self.current_station
	if not IsValid(st) or not (is_hub(st) or D.HubFor(st)) then return transfer(self, next_track, train_inbound, ...) end
	-- Include this train's own delivery before computing floors and orders.
	self:UnloadAll()
	if is_hub(st) then Floor.Reconcile(st) end
	local answers, claims, depart = train_view(self, next_track or self.track)
	if not answers then return transfer(self, next_track, train_inbound, ...) end
	D.calls = D.calls + 1
	calls_by_station[st] = D.CallsFor(st) + 1
	return with_view(answers, claims, transfer, self, next_track,
		train_inbound or (depart and not self.is_stopping), ...)
end

function D.HasDroneCoverage(st)
	for _, cc in ipairs(st.command_centers or empty_table) do
		if IsValid(cc) and cc:CanCommandDrones() and cc:IsInWorkRange(st) then return true end
	end
	return false
end

function D.Status(st, res)
	local entry, hub = D.Effective(st, res)
	if not entry or not ready(st, res) then return false, "resource is not on a hub network/enabled" end
	local s, d, scale = st.supply[res], st.demand[res], const.ResourceScale
	local result = { mode = entry.mode, percent = entry.percent, slider = amount(st, res, entry),
		stock = s:GetActualAmount(), supply_target = s:GetTargetAmount(), demand_target = d:GetTargetAmount(),
		supply_desired = s:GetDesiredAmount(), demand_desired = d:GetDesiredAmount(),
		covered = D.HasDroneCoverage(st), hub = hub, calls = D.calls,
		full = not hub.demand[res] or hub.demand[res]:GetTargetAmount() <= 0, transient = view and true or false }
	print(string.format("[TrainDistribution] station=%s res=%s mode=%s slider=%.3f stock=%.3f supply=%.3f/%.3f demand=%.3f/%.3f covered=%s hub_full=%s calls=%d",
		tostring(st.handle), res, entry.mode, result.slider/scale, result.stock/scale,
		result.supply_target/scale, result.supply_desired/scale, result.demand_target/scale,
		result.demand_desired/scale, tostring(result.covered), tostring(result.full), D.calls))
	return result
end

function D.Reapply()
	D.Refresh()
	for st in pairs(owners) do D.Apply(st) end
end
function OnMsg.SaveGameStart()
	saving = true
	view = false
	restore_baseline()
	Floor.ReleaseTransientClaims()
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
end
function OnMsg.CityStart() D.Reapply() end
function OnMsg.DoneGame()
	view, baseline, cache_time = false, false, false
	refused = setmetatable({}, { __mode = "k" })
	owners, hubs = {}, {}
end

D.active = true
print("[TrainDistribution] hub settings and transient train allocation loaded")
