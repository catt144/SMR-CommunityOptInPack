-- Console-only mechanism experiment, NOT the distribution-centre feature.
-- Authority: prompts/Train_Hub_Project/07_DISTRIBUTION_PROTOTYPE_high.md.
-- Source: SMR-SrcArchive/1.1.1.405907/Src/Lua/Units/Train.lua:862-1045.
-- That synchronous body reads source supply AND destination supply/demand.
-- Claims therefore cover configured route members, not just current_station.
-- No fields on stations, GameVars, threads, standing claims, UI or save hooks.
-- Set stores only a local session configuration. Drone baselines are SAMPLES:
-- applying them between calls would persist native request data on save.
-- No claim here promises strict floors, exact balancing, or a drone response.

SMROptInTrainDistribution = {}
local D = SMROptInTrainDistribution
local Floor = rawget(_G, "SMROptInTrainFloor")
local entries = setmetatable({}, { __mode = "k" })
local active = false
D.calls = 0

local function check(station, res)
	if not IsValid(station) or not IsKindOf(station, "Station") then
		return "select a vanilla station"
	end
	-- The hub's maintenance reserve belongs to the parallel chain.
	if type(station.GetTrainExportFloor) == "function" then return "hub/reserve station excluded" end
	if not station.supply or not station.demand or not station.supply[res] or not station.demand[res] then
		return "resource requests missing"
	end
	if not station:IsResourceEnabled(res) then return "enable this resource first" end
	if type(Floor) ~= "table" or type(Floor.WithTransientClaims) ~= "function" then
		return "train floor helper unavailable"
	end
end

local function amount(station, res, entry)
	return math.floor(station:GetMaxStorage(res) * entry.percent / 100)
end

function D.Set(station, res, mode, percent)
	local why = check(station, res)
	if why then print("[TrainDistribution] " .. why) return false, why end
	if mode ~= "export" and mode ~= "import" and mode ~= "balanced" then
		return false, "mode must be export, import or balanced"
	end
	if type(percent) ~= "number" or percent ~= percent or percent < 0 or percent > 100 then
		return false, "slider is a percentage from 0 to 100"
	end
	entries[station] = entries[station] or {}
	entries[station][res] = { mode = mode, percent = percent }
	print("[TrainDistribution] armed " .. res .. " " .. mode .. " at " .. percent ..
		"%; drone baseline remains vanilla (sample only)")
	return true
end

function D.Reset(station, res)
	if not station then entries = setmetatable({}, { __mode = "k" })
	elseif not res then entries[station] = nil
	elseif entries[station] then entries[station][res] = nil end
	print("[TrainDistribution] reset; no standing claims or baseline edits to undo")
end

local function snapshot(station, res)
	local s, d = station.supply[res], station.demand[res]
	return { supply_actual = s:GetActualAmount(), supply_target = s:GetTargetAmount(),
		supply_desired = s:GetDesiredAmount(), demand_actual = d:GetActualAmount(),
		demand_target = d:GetTargetAmount(), demand_desired = d:GetDesiredAmount() }
end

local function claims_for(station, res, entry, claims)
	local s, d = station.supply[res], station.demand[res]
	local n = amount(station, res, entry)
	local supply_hold = entry.mode == "import" and Max(s:GetTargetAmount(), 0) or n
	local demand_hold = 0
	if entry.mode == "export" then demand_hold = Max(d:GetTargetAmount(), 0)
	elseif entry.mode == "balanced" then
		local room = Max(n - s:GetActualAmount(), 0)
		demand_hold = Max(d:GetTargetAmount() - room, 0)
	end
	claims[#claims + 1] = { s, supply_hold }
	claims[#claims + 1] = { d, demand_hold }
end

-- Samples the requested drone desired amounts, restoring even on runtime errors.
-- Desired amount is a scheduling preference, NOT a hard reservation/floor.
local function baseline_sample(station, res, entry, fn)
	local s, d = station.supply[res], station.demand[res]
	local old_s, old_d = s:GetDesiredAmount(), d:GetDesiredAmount()
	local n, cap = amount(station, res, entry), station:GetMaxStorage(res)
	if entry.mode == "export" then n = cap end
	local results = table.pack(pcall(function()
		s:SetDesiredAmount(n)
		d:SetDesiredAmount(cap - n)
		return fn()
	end))
	s:SetDesiredAmount(old_s)
	d:SetDesiredAmount(old_d)
	if not results[1] then print("[TrainDistribution] sample failed: " .. tostring(results[2])) return end
	return table.unpack(results, 2, results.n)
end

local function print_view(label, v)
	local scale = ResourceScale
	print(string.format("[TrainDistribution] %s supply actual/target/desired=%.3f/%.3f/%.3f; demand actual/target/desired=%.3f/%.3f/%.3f",
		label, v.supply_actual/scale, v.supply_target/scale, v.supply_desired/scale,
		v.demand_actual/scale, v.demand_target/scale, v.demand_desired/scale))
end

function D.Status(station, res)
	local why = check(station, res)
	if why then print("[TrainDistribution] " .. why) return false, why end
	local entry = entries[station] and entries[station][res]
	if not entry then return false, "call Set first" end
	local current = snapshot(station, res)
	local drone, train
	baseline_sample(station, res, entry, function()
		drone = snapshot(station, res)
	end)
	local claims = {}
	claims_for(station, res, entry, claims)
	Floor.WithTransientClaims(claims, function() train = snapshot(station, res) end)
	if not drone or not train then return false, "sample failed" end
	print_view("CURRENT (drones now)", current)
	print_view("DRONE SAMPLE (not installed)", drone)
	print_view("TRAIN SAMPLE (claims inside call)", train)
	print("[TrainDistribution] native calls=" .. D.calls .. "; samples do not prove hauling")
	return { current = current, drone = drone, train = train,
		mode = entry.mode, percent = entry.percent, slider = amount(station, res, entry) }
end

-- Keep vanilla's desired gate: do not force a route with zero aggregate desire
-- open. A claim can only remove availability; it cannot override capacity shares.
local previous = Train and Train.TransferCargo
if type(previous) == "function" and Floor and type(Floor.WithTransientClaims) == "function" then
	function Train:TransferCargo(...)
		if active or not next(entries) then return previous(self, ...) end
		local track = select(1, ...) or self.track
		local routes = self.city and self.city.train_track_routes
		local route = routes and routes[track]
		if not route then return previous(self, ...) end
		local claims = {}
		for _, station in ipairs(route) do
			for res, entry in pairs(entries[station] or empty_table) do
				if not check(station, res) then claims_for(station, res, entry, claims) end
			end
		end
		if #claims == 0 then return previous(self, ...) end
		active = true
		D.calls = D.calls + 1
		local result = table.pack(Floor.WithTransientClaims(claims, previous, self, ...))
		active = false
		return table.unpack(result, 1, result.n)
	end
end

print("[TrainDistribution] synchronous console prototype loaded; drone baselines are samples only")
