-- Distribution centre, dev only. Authority: Train_Hub_Project/09, pass 2;
-- owner rulings in TRAIN_LOGISTICS_DESIGN_20260917.md section 4.8.
-- Archived game 1.1.1.405907: Units/Train.lua:744-831,862-1043;
-- Buildings/Station.lua:964-997; MultiResourceDepot.lua:217-245,380-407.
-- No train body copy. Synchronous getter answers + claims supply vanilla's
-- allocator with a source having no capacity share and destinations whose
-- effective capacity is their remaining order. Vanilla owns every cargo write.
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
local owners, hubs, cache_time = {}, {}, false
local applied = setmetatable({}, { __mode = "k" })
local calls_by_station = setmetatable({}, { __mode = "k" })
function D.CallsFor(st) return calls_by_station[st] or 0 end

-- Standalone dev-mod Require: no dependency on the shipping pack. Include
-- declaring methods AND early-bound aliases; check before installing anything.
D.Require = {
	{ "Train", "TransferCargo" }, { "Train", "UnloadAll" },
	{ "Station", "SetDesiredAmount" }, { "Station", "GetTrainTransportPolicy" },
	{ "Station", "GetResDesiredAmount" }, { "Station", "SetAcceptResourceState" },
	{ "Station", "BuildingUpdate" },
	{ "MultiResourceCubeVisuals", "GetMaxStorage" },
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
	owners, hubs = {}, {}
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
	cache_time = GameTime()
end

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
	return MulDivRound(st:GetMaxStorage(res), entry.percent, 100)
end

-- IsResourceEnabled is an alias of IsStoring. Wrap the consumed alias, never
-- IsStoring, which also controls the persistent demand flags.
function MultiResourceDepotBase:IsResourceEnabled(res)
	local row = view and view[self] and view[self][res]
	if row then return row.enabled end
	return enabled(self, res)
end

local function capacity_wrapper(previous)
	return function(self, res, ...)
		local row = view and view[self] and view[self][res]
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
	if row and row.enabled then return const.ResourceScale end
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

-- Old inbound reservations may predate a mode change. Vanilla keeps a cargo
-- entry aboard if it no longer fits; the hub can receive it later. No custom
-- writes to assigned_resources, request flags or transport_policy.
local unload = Train.UnloadAll
function Train:UnloadAll(...)
	local st = self.current_station
	local hub = IsValid(st) and D.HubFor(st)
	local rows = hub and rawget(hub, FIELD)
	rows = rows and rows[st]
	local old = view
	view = false
	if saving or not rows then
		local result = table.pack(pcall(unload, self, ...))
		view = saving and false or old
		if not result[1] then D.error = tostring(result[2]) return end
		return table.unpack(result, 2, result.n)
	end
	local answers, claims = { [st] = {} }, {}
	for res, entry in pairs(rows) do
		if ready(st, res) then
			local s, d = st.supply[res], st.demand[res]
			local room = Max(amount(st, res, entry) - s:GetActualAmount(), 0)
			local own = (self.assigned_resources[st] or empty_table)[res] or 0
			answers[st][res] = { enabled = entry.mode ~= "export" and own <= room }
			local reserved = Max(d:GetActualAmount() - d:GetTargetAmount(), 0)
			claims[#claims + 1] = { d, Max(d:GetTargetAmount() - Max(room - reserved, 0), 0) }
		end
	end
	local result = table.pack(with_view(answers, claims, unload, self, ...))
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
	if not members[hub] then return end
	local rows = rawget(hub, FIELD) or empty_table
	local answers, claims = {}, {}
	for _, res in ipairs(st.storable_resources or empty_table) do
		local entry = rows[st] and rows[st][res]
		local configured = entry and ready(st, res)
		if st == hub then
			for dest in pairs(members) do
				if rows[dest] and rows[dest][res] and ready(dest, res) then configured = true break end
			end
		end
		if configured and ready(st, res) then
			local floor = entry and (entry.mode == "import" and st.supply[res]:GetActualAmount()
				or amount(st, res, entry)) or 0
			claims[#claims + 1] = { st.supply[res], floor }
			for dest in pairs(members) do
				if dest.supply and dest.supply[res] and dest.demand and dest.demand[res] then
					local order = 0
					if dest ~= st and can_receive[dest] and ready(dest, res) then
						if dest == hub and entry and entry.mode ~= "import" then
							order = Max(dest.demand[res]:GetTargetAmount(), 0)
						elseif st == hub then
							local target = rows[dest] and rows[dest][res]
							if target and target.mode ~= "export" then
								local reserved = Max(dest.demand[res]:GetActualAmount() - dest.demand[res]:GetTargetAmount(), 0)
								order = Max(amount(dest, res, target) - dest.supply[res]:GetActualAmount() - reserved, 0)
								order = Min(order, Max(dest.demand[res]:GetTargetAmount(), 0))
							end
						end
					end
					answers[dest] = answers[dest] or {}
					answers[dest][res] = { enabled = order > 0, capacity = order }
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
	return answers, claims
end

local transfer = Train.TransferCargo
function Train:TransferCargo(...)
	if saving or view then return transfer(self, ...) end
	local st = self.current_station
	if not IsValid(st) or not (is_hub(st) or D.HubFor(st)) then return transfer(self, ...) end
	-- Include this train's own delivery before computing floors and orders.
	self:UnloadAll()
	if is_hub(st) then Floor.Reconcile(st) end
	local answers, claims = train_view(self, select(1, ...) or self.track)
	if not answers then return transfer(self, ...) end
	D.calls = D.calls + 1
	calls_by_station[st] = D.CallsFor(st) + 1
	return with_view(answers, claims, transfer, self, ...)
end

function D.HasDroneCoverage(st)
	for _, cc in ipairs(st.command_centers or empty_table) do
		if IsValid(cc) and cc:CanCommandDrones() and cc:IsInWorkRange(st) then return true end
	end
	return false
end

function D.Status(st, res)
	local entry, hub = D.Get(st, res)
	if not entry or not ready(st, res) then return false, "resource is not configured/enabled" end
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
	applied = setmetatable({}, { __mode = "k" })
	D.Reapply()
end
function OnMsg.CityStart() D.Reapply() end
function OnMsg.DoneGame()
	view, baseline, cache_time = false, false, false
	owners, hubs = {}, {}
end

D.active = true
print("[TrainDistribution] hub settings and transient train allocation loaded")
