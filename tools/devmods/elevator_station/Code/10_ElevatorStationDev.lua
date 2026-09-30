-- DEV ONLY: the Elevator Station's look (brief 25, owner ruling 2026-09-29, spec section 11).
-- One placeable stand-in building on both maps. No store, no elevator range rule, no twin: those
-- are the next brief. The template is plain vanilla `Building`, so a save holds nothing of ours
-- but the template's own class; demolish every stand-in before removing this mod.
--
-- The body entity carries TrainStationCCP3's train spots at vanilla's own positions (decoded from
-- entities.dat, build 25390750), so the wiring brief inherits working geometry. Two visuals ride
-- on it, each IsValidEntity-gated so a missing import is simply absent: the dome glass (both maps)
-- and the lift shaft into the cave ceiling (underground only). Same attach lifecycle as the train
-- hub's glass: DeleteOnLoadGame plus recreation on load, nothing persisted.
--
-- Console, for the owner's sitting (output lands in the game log as [ElevatorStationDev]):
--   SMRElevatorStationDev.Report()       every stand-in: map, hex, connectors against vanilla's
--   SMRElevatorStationDev.Measure()      the current map's camera, elevators and ceiling objects
--   SMRElevatorStationDev.ShaftZ(m)      raise or sink the underground shaft live, metres
--   SMRElevatorStationDev.Shaft(false)   hide the shaft; true shows it again
--   SMRElevatorStationDev.Glow(v)        glow level 0..255 on the body and shaft (default 200)

SMRElevatorStationDev = rawget(_G, "SMRElevatorStationDev") or {}
local D = SMRElevatorStationDev

local template_id = "SMROptInElevatorStationDev"
local glass_entity = "SMROptInElevatorStationGlass"
local shaft_entity = "SMROptInElevatorStationShaft"
local log_prefix = "[ElevatorStationDev]"

D.shaft_z = D.shaft_z or 0          -- cm, the shaft's attach offset
D.shaft_on = D.shaft_on ~= false
D.glow = D.glow or 200

-- TrainStationCCP3's connectors, game units in the entity's own frame (entities.dat, 25390750).
local vanilla_connectors = {
	Trackconnector1 = point(-3997, -1731, 0),
	Trackconnector2 = point(3997, -1731, 0),
}

local function is_station(obj)
	return IsValid(obj) and obj.template_name == template_id
end

local function environment_of(obj)
	return GetEnvironment(obj:GetMap())
end

local function our_visual(v)
	if not IsValid(v) then return false end
	local e = v:GetEntity()
	return e == glass_entity or e == shaft_entity
end

function D.Dress(bld)
	if not is_station(bld) or IsKindOf(bld, "ConstructionSite") then return end
	for _, v in ipairs(bld:GetAttaches("ShapeshifterAutoAttach") or empty_table) do
		if our_visual(v) then DoneObject(v) end
	end
	local wanted = { glass_entity }
	if D.shaft_on and environment_of(bld) == "Underground" then
		wanted[#wanted + 1] = shaft_entity
	end
	for _, entity in ipairs(wanted) do
		if IsValidEntity(entity) then
			local v = PlaceObjectIn("ShapeshifterAutoAttach", bld:GetMap())
			v:ChangeEntity(entity)
			v:ClearEnumFlags(const.efCollision + const.efApplyToGrids + const.efWalkable + const.efSelectable)
			bld:Attach(v, bld:GetSpotBeginIndex("Origin"))
			v:SetAttachOffset(point(0, 0, entity == shaft_entity and D.shaft_z or 0))
			if entity == shaft_entity then v:SetSIModulation(D.glow) end
			DeleteOnLoadGame(v)
		end
	end
	bld:SetSIModulation(D.glow)
end

local function for_each_station(fn)
	AllMapsForEach("map", "Building", function(bld)
		if is_station(bld) then fn(bld) end
	end)
end

function OnMsg.BuildingInit(bld)
	if is_station(bld) then D.Dress(bld) end
end

function OnMsg.LoadGame()
	for_each_station(D.Dress)
end

-- A plain Building turns its self-illumination off whenever it stops "working"
-- (Building.lua:1422-1439, 1.1.1.405907); the look keeps its lines lit.
function OnMsg.OnSetWorking(bld, working)
	if is_station(bld) then bld:SetSIModulation(D.glow) end
end

function D.ShaftZ(metres)
	D.shaft_z = math.floor((metres or 0) * guim + 0.5)   -- whole cm: point() takes integers
	for_each_station(D.Dress)
	print(log_prefix, "shaft offset", D.shaft_z, "cm")
end

function D.Shaft(on)
	D.shaft_on = on ~= false
	for_each_station(D.Dress)
	print(log_prefix, "shaft", D.shaft_on and "on" or "off")
end

function D.Glow(v)
	D.glow = v or 200
	for_each_station(D.Dress)
	print(log_prefix, "glow", D.glow)
end

function D.Report()
	local n = 0
	for_each_station(function(bld)
		n = n + 1
		local pos = bld:GetPos()
		local q, r = WorldToHex(pos)
		local visuals = {}
		for _, v in ipairs(bld:GetAttaches("ShapeshifterAutoAttach") or empty_table) do
			if our_visual(v) then visuals[#visuals + 1] = v:GetEntity() end
		end
		print(string.format("%s station %d map slot=%s env=%s pos=%s hex=(%d,%d) angle=%d entity=%s valid=%s visuals=%s",
			log_prefix, n, tostring(bld:GetMapSlot()), environment_of(bld), tostring(pos),
			q, r, bld:GetAngle() / 60, bld:GetEntity(), tostring(IsValidEntity(bld:GetEntity())),
			table.concat(visuals, ",")))
		for name, local_pt in sorted_pairs(vanilla_connectors) do
			local idx = bld:GetSpotBeginIndex(name)
			local want = bld:GetRelativePoint(local_pt)
			local wq, wr = WorldToHex(want)
			if idx and idx >= 0 then
				local got = bld:GetSpotPos(idx)
				local gq, gr = WorldToHex(got)
				print(string.format("%s   %s spot=%s hex=(%d,%d) vanilla=%s hex=(%d,%d) off=%d cm %s",
					log_prefix, name, tostring(got), gq, gr, tostring(want), wq, wr,
					got:Dist2D(want), (gq == wq and gr == wr) and "MATCH" or "DIFFERENT HEX"))
			else
				print(string.format("%s   %s MISSING on the entity; vanilla hex=(%d,%d)", log_prefix, name, wq, wr))
			end
		end
	end)
	print(log_prefix, "stations", n)
end

-- The ceiling read (brief 25: "Cave ceiling height varies. Check it near the elevators on the
-- underground map"). Prints the camera, every elevator on the current map with its own shaft top,
-- and, within radius_m of each, every object group standing well above the ground there, by entity:
-- the stalactites and cave pillars hang from the ceiling, so their heights are the ceiling's.
function D.Measure(radius_m)
	local map = CurrentMap
	local radius = (radius_m or 150) * guim
	local eye, lookat = cameraRTS.GetPosLookAt()
	local ground_eye = terrain.GetHeight(map, eye)
	local ground_look = terrain.GetHeight(map, lookat)
	local zoom = cameraRTS.GetZoom()
	local zmin, zmax = cameraRTS.GetZoomLimits()
	print(string.format("%s measure env=%s camera eye z=%d, %d cm over the ground under it; look-at z=%d, ground there %d; eye over look-at ground %d cm; zoom %s of %s..%s",
		log_prefix, GetEnvironment(map), eye:z(), eye:z() - ground_eye, lookat:z(), ground_look,
		eye:z() - ground_look, tostring(zoom), tostring(zmin), tostring(zmax)))
	local elevators = 0
	map:MapForEach("map", "ElevatorBase", function(el)
		elevators = elevators + 1
		local p = el:GetPos()
		local ground = terrain.GetHeight(map, p)
		local bb = el:GetEntityBBox()
		print(string.format("%s elevator %d entity=%s pos=%s ground=%d shaft top %d cm over its base",
			log_prefix, elevators, el:GetEntity(), tostring(p), ground, (bb and bb:IsValid()) and bb:maxz() or -1))
		local groups = {}
		map:MapForEach(el, radius, "CObject", function(o)
			if o == el then return end
			local e = o:GetEntity() or ""
			local oz = o:GetPos():z() - ground
			local obb = e ~= "" and o:GetEntityBBox()
			local top = oz + ((obb and obb:IsValid()) and obb:maxz() or 0) * o:GetScale() / 100
			if oz > 20 * guim or top > 40 * guim or e:find("Stalactite") or e:find("Pillar") then
				local g = groups[e] or { n = 0, lo = max_int, hi = min_int, top = min_int }
				g.n, g.lo, g.hi, g.top = g.n + 1, Min(g.lo, oz), Max(g.hi, oz), Max(g.top, top)
				groups[e] = g
			end
		end)
		local keys = table.keys(groups, true)
		if #keys == 0 then
			print(log_prefix, "   nothing stands above 20 m within", radius / guim, "m")
		end
		for _, e in ipairs(keys) do
			local g = groups[e]
			print(string.format("%s   %-44s x%d  pos %d..%d cm over the elevator's ground, top %d cm",
				log_prefix, e, g.n, g.lo, g.hi, g.top))
		end
	end)
	print(log_prefix, "elevators on this map", elevators)
end
