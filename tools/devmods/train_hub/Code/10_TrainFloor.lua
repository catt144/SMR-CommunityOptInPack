-- Train export floor: the reusable core of the hub's maintenance reserve.
-- Dev build for game 1.1.0.403908; every source line below was read on that
-- build (C:\Dev\SMR-SrcArchive\1.1.0.403908\Src). UNVERIFIED in game until the
-- sitting in docs/agent/reports/TRAIN_HUB_BUILD_20260918.md is recorded.
--
-- THE MECHANISM. A depot's per-resource supply request carries two amounts.
-- `GetActualAmount` is the stock; `GetTargetAmount` is the stock nobody has
-- claimed yet. Every hauler claims through the engine's own reservation,
-- `request:AssignUnit(amount)` (Lua\_TaskRequest.lua:391-392), which lowers the
-- target and leaves the stock alone. Trains read the target everywhere they
-- decide what may leave a station (Units\Train.lua `Train:TransferCargo`,
-- :836-1020: `available = Min(target, actual)`, the forbidden branch's
-- `forbidden_excess = target`, and the execution pass's `stored = target`), and
-- drones are paired against the target by the C-side task finder. So a floor is
-- a claim the STATION holds on its own supply request: the held amount stays in
-- stock, stays on the infopanel, and is invisible to trains, drones and
-- shuttles alike. Nothing of vanilla's is copied or replaced.
--
-- TWO SHAPES, one primitive (`hold` / `release`):
--   * STANDING hold (the hub's reserve): kept at all times, topped up from
--     `OnAfterRequestUpdate`, which vanilla calls after every stock change
--     (MultiResourceCubeVisuals.lua:434, :454, :466). Binds trains AND drones.
--   * TRANSIENT hold (Module A's export floor, spec §4.3): taken only around
--     `Train:TransferCargo` and released after it, so trains leave the floor
--     alone while drones may still use it. No station asks for this yet, so
--     this path is NOT EXERCISED by the hub sitting.
--
-- A station opts in by answering `GetTrainExportFloor(res)` -> amount, standing.
-- A station without that method takes the wrapper's first-line fast path.
--
-- SAVE CONTRACT (FIX_POLICY ban 1). One persisted field, on hub objects only:
--   SMROptIn_floor_hold = { [res] = { req = <the supply request>, amount = n } }
-- The request is stored beside the amount because vanilla REPLACES a supply
-- request when a resource is removed and re-added (FinalizePendingRemoval,
-- MultiResourceCubeVisuals.lua:395-399, then RegisterResourceRequest :372-393).
-- A hold recorded against a dead request is forgotten, never released onto the
-- new one: releasing a claim that was never made would mint phantom stock.
-- The engine's claim itself rides inside the request, which vanilla persists.
--
-- FIX_POLICY §3a: everything here is synchronous. No thread, no stored function.

local FIELD = "SMROptIn_floor_hold"

SMROptInTrainFloor = rawget(_G, "SMROptInTrainFloor") or {}
local Floor = SMROptInTrainFloor
Floor.FIELD = FIELD
Floor.stats = Floor.stats or { wrap_calls = 0, wrap_floor_calls = 0, transient_holds = 0 }

local function supply_of(station, res)
	local supply = station.supply
	return supply and supply[res] or nil
end

-- Claim up to `want` of what is still unclaimed. Returns the amount claimed.
local function hold(req, want)
	if want <= 0 then return 0 end
	local free = Min(req:GetTargetAmount(), req:GetActualAmount())
	local take = Min(want, free)
	if take <= 0 then return 0 end
	if not req:AssignUnit(take) then return 0 end
	return take
end

-- Give a claim back. `false` = not fulfilled: the stock stays, the target returns.
local function release(req, amount)
	if amount > 0 then req:UnassignUnit(amount, false) end
end

function Floor.Wanted(station, res)
	local fn = station.GetTrainExportFloor
	if type(fn) ~= "function" then return 0, false end
	local amount, standing = fn(station, res)
	return Max(amount or 0, 0), standing and true or false
end

function Floor.Held(station, res)
	local record = rawget(station, FIELD)
	local entry = record and record[res]
	if not entry then return 0 end
	if entry.req ~= supply_of(station, res) then return 0 end
	return entry.amount or 0
end

-- Bring one resource's standing hold to min(floor, stock). Safe to call at any
-- time and as often as wanted; it is the whole of the standing shape.
function Floor.ReconcileRes(station, res)
	local req = supply_of(station, res)
	local record = rawget(station, FIELD)
	local entry = record and record[res]
	if not req then
		if entry then record[res] = nil end
		return 0
	end
	if entry and entry.req ~= req then
		-- vanilla replaced the request; the old claim died with it
		entry = nil
		record[res] = nil
	end
	local held = entry and entry.amount or 0
	local want, standing = Floor.Wanted(station, res)
	if not standing then want = 0 end

	local target, actual = req:GetTargetAmount(), req:GetActualAmount()
	-- 1. A `SetAmount` (ClearAllResources, MultiResourceCubeVisuals.lua:469-476)
	--    rewrites the request and drops our claim without telling us. True target
	--    is `actual - held - hauler claims`, so target above `actual - held` can
	--    only mean the record overstates. Forget the excess; do not release it.
	local overstated = target - (actual - held)
	if overstated > 0 then held = Max(held - overstated, 0) end
	-- 2. Stock removed from under the hold (`AddAmount(-n)`) drives the target
	--    below zero. Hand back what is needed to return it to zero.
	if target < 0 and held > 0 then
		local back = Min(held, -target)
		release(req, back)
		held = held - back
	end
	-- 3. Settle on the wanted amount.
	if held > want then
		release(req, held - want)
		held = want
	elseif held < want then
		held = held + hold(req, want - held)
	end

	if held > 0 then
		record = record or {}
		rawset(station, FIELD, record)
		record[res] = { req = req, amount = held }
	elseif record then
		record[res] = nil
	end
	return held
end

function Floor.Reconcile(station)
	if not IsValid(station) or not station.supply then return end
	for _, res in ipairs(station.storable_resources or empty_table) do
		local want, standing = Floor.Wanted(station, res)
		if (standing and want > 0) or Floor.Held(station, res) > 0 then
			Floor.ReconcileRes(station, res)
		end
	end
end

-- Hand every standing hold back, for the one consumer the reserve exists for.
-- The caller reconciles again before it returns, with no yield in between.
function Floor.ReleaseAll(station)
	local record = rawget(station, FIELD)
	if not record then return end
	for res, entry in pairs(record) do
		if entry.req == supply_of(station, res) then release(entry.req, entry.amount or 0) end
		record[res] = nil
	end
end

-- ---------------------------------------------------------------------------
-- The train side. FIX_POLICY §1.4: a chained wrapper that always calls the
-- original and passes every return through. `Train` declares TransferCargo
-- (Units\Train.lua:836), so this installs on the declaring class (F64).
--
-- `TransferCargo` opens with `self:UnloadAll()` (:845), and a floor must count
-- what this train is about to unload. Calling UnloadAll first is safe: vanilla's
-- own call then finds nothing left to unload and an empty assignment list.
-- The function does not yield (no Sleep, Wait or Goto on any path, :836-1020),
-- so the transient claims never outlive this call.
local vanilla_transfer_cargo = Train.TransferCargo
function Train:TransferCargo(...)
	Floor.stats.wrap_calls = Floor.stats.wrap_calls + 1
	local station = self.current_station
	if not IsValid(station) or type(station.GetTrainExportFloor) ~= "function" or not station.supply then
		return vanilla_transfer_cargo(self, ...)
	end
	Floor.stats.wrap_floor_calls = Floor.stats.wrap_floor_calls + 1
	self:UnloadAll()
	local transient
	for _, res in ipairs(station.storable_resources or empty_table) do
		local want, standing = Floor.Wanted(station, res)
		if want > 0 then
			if standing then
				Floor.ReconcileRes(station, res)
			else
				local req = supply_of(station, res)
				local took = req and hold(req, want) or 0
				if took > 0 then
					transient = transient or {}
					transient[#transient + 1] = { req, took }
					Floor.stats.transient_holds = Floor.stats.transient_holds + 1
				end
			end
		end
	end
	if not transient then return vanilla_transfer_cargo(self, ...) end
	local results = table.pack(vanilla_transfer_cargo(self, ...))
	for _, claim in ipairs(transient) do release(claim[1], claim[2]) end
	return table.unpack(results, 1, results.n)
end

print("[TrainHubDev] train export floor loaded (standing + transient holds)")
