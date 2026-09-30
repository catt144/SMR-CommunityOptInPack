-- DEV ONLY: the Elevator Depot's look (brief 25, owner rulings 2026-09-29, spec section 11).
-- One placeable stand-in on both maps: our own station class based on vanilla's Station, on our own
-- base entity (SMROptInElevatorDepot: footprint, plinth and the 14 vanilla train spots, built by
-- SMR-Assets/elevatorstation/blender/depot_build.py). The code attaches the scaled vanilla elevator
-- at run time, so vanilla's elevator is untouched and nothing of ours but the
-- template's class enters a save. Demolish every stand-in before removing this mod.
--
--   * vanilla's Space Elevator art at 75 % on the origin, with a SpaceElevatorCabin running a rope of
--     SpaceElevatorRope tiles and the ElevatorMoving FX on both, as the wonder does
--     (SpaceElevator.lua:56-74, :391-410, :652-655 at 1.1.1.405907). D1: on the surface the cabin
--     goes DOWN into the ground; underground it goes UP into the cave ceiling.
--   * the owner-approved (2026-09-30) rounded mouth tapers into the base between the front pads;
--     the elevator turns 90 degrees. The below-grade Stop/Spawn and Rampdepart spots request a
--     descent and ascent using vanilla Station alone. This prepared revision still needs a live
--     train run; the desk clearance model is conditional, not a runtime result. Trackconnector2
--     and its direction remain inside the footprint, so no track can reach that end
--     (TrackElement.lua:345-348; Tracks.lua:240, archived build 25390750).
--
-- Cargo, per-resource modes, the drone crew and the underground twin are the next brief.
--
-- Console, for the owner's sitting (output lands in the game log as [ElevatorDepotDev]):
--   SMRElevatorDepotDev.Report()           every depot: map, hex, label, its 14 spots, connector elements
--   SMRElevatorDepotDev.Measure()          the current map's camera, elevators and ceiling objects
--   SMRElevatorDepotDev.Show()             the live layout table
--   SMRElevatorDepotDev.Set("key", value)  move a visual by eye, e.g. Set("tunnel_lift", 250),
--                                          Set("scale", 80), Set("rope_underground_m", 400),
--                                          Set("receiver_z", -250), Set("signs", true); re-dresses all
--   SMRElevatorDepotDev.Redress()          rebuild every depot's visuals from the layout
--   SMRElevatorDepotDev.Sweep()            clear gone-depot props and the identified legacy rope tiles
--   SMRElevatorDepotDev.InspectProps()     read-only census, including CObject ropes and attachments
--   SMRElevatorDepotDev.RemoveInspectedRope(n)  remove ONE inspected, unowned underground 75% rope
--   SMRElevatorDepotDev.Preview(...)       the earlier free-standing previews still work (see below)
-- SMRElevatorStationDev is kept as an alias, so the earlier console lines still run.

SMRElevatorDepotDev = rawget(_G, "SMRElevatorDepotDev") or {}
SMRElevatorStationDev = SMRElevatorDepotDev
local D = SMRElevatorDepotDev

local template_id = "SMROptInElevatorDepotDev"
local entity_id = "SMROptInElevatorDepot"
local mod_entities = { SMROptInElevatorDepot = true, SMROptInElevatorDepotReceiver = true }
local log_prefix = "[ElevatorDepotDev]"

-- ArtSpecEditor.lua:565-573 (archived 1.1.1.406343) calls an editor-only helper on retail
-- mod load. This spec has no legacy color properties to migrate; skip only its editor load
-- when that helper is absent. Preserve other specs and the hub's existing wrapper (D14(e)).
local function install_depot_art_spec_guard()
	local spec = g_Classes and g_Classes.EntitySpec
	local previous = spec and rawget(spec, "OnPresetPostLoad")
	if type(previous) ~= "function" or previous == D.ArtSpecGuard then return end
	local wrapper = function(self, ...)
		if mod_entities[self.id] and type(rawget(_G, "EntitySpecPathToEntity")) ~= "function" then return end
		return previous(self, ...)
	end
	spec.OnPresetPostLoad = wrapper
	D.ArtSpecGuard = wrapper
end

function OnMsg.ClassesPostprocess()
	install_depot_art_spec_guard()
end

-- The layout: depot_build.py's numbers, game units (cm) and degrees. The entity's spots and
-- footprint are baked from the same constants; a Set() here moves only a visual. A move the owner
-- keeps goes back into depot_build.py for a regenerate and re-import, so the spots follow.
D.layout = D.layout or {
	scale = 75,                         -- both vanilla arts, percent
	elevator_entity = "SpaceElevator",
	elevator_x = 0, elevator_y = 0, elevator_z = 0,
	elevator_angle = 90,                -- approved portal between the two front pads (2026-09-30)
	tunnel_entity = false,              -- the mouth is the entity's own rounded descending shell;
	                                    -- Set("tunnel_entity", "TrainTunnelUniversal")
	                                    -- brings the vanilla art back for comparison
	tunnel_x = -750, tunnel_y = -2598, tunnel_lift = 200, tunnel_angle = 180,
	rope_surface_m = 0,                 -- D1: the surface cabin goes down, so no rope above by default
	rope_underground_m = 300,           -- the cabin goes up into the cave ceiling; the sitting measures it
	travel_down_m = 60,                 -- surface: how deep the cabin sinks
	travel_up_m = 0,                    -- underground: 0 means the rope's height
	leg_ms = 20000,                     -- game ms per leg (vanilla's leg is one game hour)
	dwell_ms = 8000,                    -- parked at each end
	tick_ms = 250,
	cabin_on = true,
	-- brief 26 (owner's list, 2026-09-30)
	signs = false,                      -- vanilla hangs an UnderconstructionSignCCP3 8.4..13.3 m over every
	                                    -- Sign<i> spot (UnderconstructionSign.lua:41-56): the "floating
	                                    -- element". false removes them; true puts vanilla's back
	receiver_entity = "SMROptInElevatorDepotReceiver",   -- item 8: the landing floor in the well, underground only
	receiver_z = -300,                  -- cm under the origin; the cabin's underside rests 245 below it
	receiver_scale = 100,
	receiver_underground_only = true,   -- false shows it on the surface too, for comparison
	elevator_hide = "",                 -- item 6, the frame in the core: entity names (comma-separated) of the
	                                    -- elevator art's own auto-attaches to remove; Report() lists them
}

-- The vanilla Station's 14 spot names at the design's positions (depot_build.py `spots()`), so
-- Report() can say whether the imported entity carries what was designed.
local design_spots = {
	Trackconnector1 = point(-5000, 0, 800), Trackdirection1 = point(-6000, 0, 800),
	Trackconnector2 = point(1000, 0, 800), Trackdirection2 = point(0, 0, 800),
	Ramparrive1 = point(-3600, -335, 800), Stop1 = point(-500, -335, -1400), Spawn2 = point(-500, -335, -1400),
	Spawn1 = point(-500, 335, -1400), Stop2 = point(-500, 335, -1400), Rampdepart1 = point(0, 335, -1400),
	Ramparrive2 = point(900, 335, -1400), Rampdepart2 = point(800, -335, -1400),
	Sign1 = point(-5000, 0, 0),   -- Sign2 dropped (brief 26, item 1): connector 2 is buried
}

-- ---- the class ---------------------------------------------------------------------------------
DefineClass.SMROptInElevatorDepotDevBase = {
	__parents = { "Station" },
}

-- City labels, as the hub does it: Building.lua:435-447 adds only the class and object_class, so a
-- template whose object_class is not "Station" never joins the "Station" label that Train.lua:94,
-- :134 walk to free a platform. AddToCityLabels is a combined method, so this adds.
function SMROptInElevatorDepotDevBase:AddToCityLabels()
	self.city:AddToLabel("Station", self)
end

function SMROptInElevatorDepotDevBase:RemoveFromCityLabels()
	self.city:RemoveFromLabel("Station", self)
end

function SMROptInElevatorDepotDevBase:GameInit()
	D.Dress(self)
end

function SMROptInElevatorDepotDevBase:Done()
	D.Undress(self)
end

function SMROptInElevatorDepotDevBase:OnDestroyed()
	D.Undress(self)
end

-- ---- the visuals ------------------------------------------------------------------------------
D.rigs = D.rigs or setmetatable({}, { __mode = "k" })   -- depot -> { elevator, tunnel, cabin, ropes, thread }

local function is_depot(obj)
	return IsValid(obj) and IsKindOf(obj, "SMROptInElevatorDepotDevBase")
end

local function environment_of(obj)
	return GetEnvironment(obj:GetMap())
end

local function unselectable(o)
	o:ClearEnumFlags(const.efCollision + const.efApplyToGrids + const.efWalkable + const.efSelectable)
	-- never saved: a saved rope outlived its deleted depot and came back on every load (2026-09-30)
	o:ClearGameFlags(const.gofPermanent)
end

local function free_prop(class, map, pos, scale)
	local o = PlaceObjectIn(class, map)
	o:SetPos(pos)
	o:SetScale(scale)
	o:SetGameFlags(const.gofAlwaysGatherForVisibility)
	unselectable(o)
	DeleteOnLoadGame(o)
	o.smr_depot_prop = true   -- ours, never vanilla's wonder: Sweep() deletes only marked props
	return o
end

-- A rope tile never moves, so it rides as an attachment and dies with the depot in the engine
-- itself (2026-09-30: rope tiles outlived a deleted underground depot).
local function attached_prop(bld, class, offset, scale)
	local o = PlaceObjectIn(class, bld:GetMap())
	o:SetScale(scale)
	o:SetGameFlags(const.gofAlwaysGatherForVisibility)
	unselectable(o)
	local spot = bld:GetSpotBeginIndex("Origin")
	if spot and spot >= 0 then bld:Attach(o, spot) else bld:Attach(o) end
	o:SetAttachOffset(offset)
	DeleteOnLoadGame(o)
	o.smr_depot_prop = true
	return o
end

local function attach_visual(bld, entity, offset, angle_deg, scale, actor)
	if not IsValidEntity(entity) then
		print(log_prefix, "no such entity", entity)
		return
	end
	local v = PlaceObjectIn("ShapeshifterAutoAttach", bld:GetMap())
	v:ChangeEntity(entity)                 -- brings the art's own auto-attaches (AutoAttach.lua:2606-2619)
	if actor then v.fx_actor_class = actor end
	unselectable(v)
	local spot = bld:GetSpotBeginIndex("Origin")
	if spot and spot >= 0 then bld:Attach(v, spot) else bld:Attach(v) end
	v:SetAttachOffset(offset)
	v:SetAttachAngle(angle_deg * 60)
	v:SetScale(scale)
	DeleteOnLoadGame(v)
	return v
end

local function stop_cycle(rig)
	if rig and IsValidThread(rig.thread) then DeleteThread(rig.thread) end
	if rig then rig.thread = false end
end

local function start_cycle(rig)
	if not rig or not IsValid(rig.cabin) or IsValidThread(rig.thread) then return end
	rig.thread = CreateGameTimeThread(function(rig)
		local L = D.layout
		local steps = Max(1, L.leg_ms / L.tick_ms)
		while IsValid(rig.cabin) and IsValid(rig.elevator) do
			for _, target in ipairs{ rig.far, rig.base } do
				PlayFX("ElevatorMoving", "start", rig.elevator)
				PlayFX("ElevatorMoving", "start", rig.cabin)
				local from = rig.cabin:GetPos()
				for i = 1, steps do
					if not IsValid(rig.cabin) then return end
					rig.cabin:SetPos(point(from:x(), from:y(), from:z() + MulDivRound(target:z() - from:z(), i, steps)), L.tick_ms)
					Sleep(L.tick_ms)
				end
				if not IsValid(rig.elevator) or not IsValid(rig.cabin) then return end
				PlayFX("ElevatorMoving", "end", rig.elevator)
				PlayFX("ElevatorMoving", "end", rig.cabin)
				Sleep(L.dwell_ms)
			end
		end
	end, rig)
end

function D.Undress(bld)
	local rig = D.rigs[bld]
	if not rig then return end
	stop_cycle(rig)
	for _, o in ipairs(rig.ropes or empty_table) do
		if IsValid(o) then DoneObject(o) end
	end
	if IsValid(rig.cabin) then DoneObject(rig.cabin) end
	if IsValid(rig.receiver) then DoneObject(rig.receiver) end
	if IsValid(rig.tunnel) then DoneObject(rig.tunnel) end
	if IsValid(rig.elevator) then DoneObject(rig.elevator) end
	D.rigs[bld] = nil
end

function D.Dress(bld)
	if not is_depot(bld) or IsKindOf(bld, "ConstructionSite") then return end
	D.Undress(bld)
	local L = D.layout
	local map = bld:GetMap()
	local underground = environment_of(bld) == "Underground"
	local rig = { ropes = {} }
	rig.elevator = attach_visual(bld, L.elevator_entity, point(L.elevator_x, L.elevator_y, L.elevator_z),
		L.elevator_angle, L.scale, "SpaceElevator")
	if rig.elevator and L.elevator_hide ~= "" then
		local hide = {}
		for name in tostring(L.elevator_hide):gmatch("[^,%s]+") do hide[name] = true end
		local gone = 0
		rig.elevator:ForEachAttach(function(a)
			if hide[a:GetEntity() or ""] then DoneObject(a); gone = gone + 1 end
		end)
		print(log_prefix, "elevator attaches hidden:", gone, "(", L.elevator_hide, ")")
	end
	if L.tunnel_entity then
		rig.tunnel = attach_visual(bld, L.tunnel_entity, point(L.tunnel_x, L.tunnel_y, L.tunnel_lift),
			L.tunnel_angle, L.scale)
	end
	-- brief 26, item 8: the receiver sits in the well; the surface keeps the bare shaft
	if L.receiver_entity and (underground or not L.receiver_underground_only) then
		rig.receiver = attach_visual(bld, L.receiver_entity, point(0, 0, L.receiver_z), 0, L.receiver_scale)
	end
	-- brief 26, item 1: vanilla's end-of-track barrier signs (Station.lua:132 places one per Sign<i>
	-- spot; every handler finds them through GetAttaches, so removing the attaches is enough)
	bld:DestroyAttaches("UnderconstructionSign")
	if L.signs and rawget(_G, "PlaceUnderconstructionSigns") then
		PlaceUnderconstructionSigns(bld)
	end
	if rig.elevator and L.cabin_on then
		-- the cabin and rope are free objects at the elevator's world position, as vanilla's are
		local base = bld:GetRelativePoint(point(L.elevator_x, L.elevator_y, L.elevator_z))
		rig.base = base
		rig.cabin = free_prop("SpaceElevatorCabin", map, base, L.scale)
		local rope_m = underground and L.rope_underground_m or L.rope_surface_m
		local rope_step = MulDivRound(100 * guim, L.scale, 100)   -- vanilla lays a tile every 100 m
		local z = 0
		while z < rope_m * guim do
			rig.ropes[#rig.ropes + 1] = attached_prop(bld, "SpaceElevatorRope", point(L.elevator_x, L.elevator_y, L.elevator_z + z), L.scale)
			z = z + rope_step
		end
		local reach
		if underground then
			reach = (L.travel_up_m > 0 and L.travel_up_m or rope_m) * guim   -- up into the ceiling
		else
			reach = -L.travel_down_m * guim                                  -- D1: down into the ground
		end
		rig.far = base + point(0, 0, reach)
		start_cycle(rig)
	end
	rig.bld = bld
	D.rigs[bld] = rig
	print(string.format("%s dressed %s env=%s elevator=%s tunnel=%s cabin=%s ropes=%d scale=%d receiver=%s signs=%d",
		log_prefix, tostring(bld), environment_of(bld), tostring(IsValid(rig.elevator)), tostring(IsValid(rig.tunnel)),
		tostring(IsValid(rig.cabin)), #rig.ropes, L.scale, tostring(IsValid(rig.receiver)),
		#(bld:GetAttaches("UnderconstructionSign") or empty_table)))
end

-- Props whose depot is gone (any delete path) are removed by this sweep; Sweep() runs it now and
-- also clears every marked prop on every map that no live rig owns.
local function sweep_rigs()
	local n = 0
	for bld, rig in pairs(D.rigs) do
		if not IsValid(bld) then
			stop_cycle(rig)
			for _, o in ipairs(rig.ropes or empty_table) do if IsValid(o) then DoneObject(o); n = n + 1 end end
			for _, k in ipairs{ "cabin", "receiver", "tunnel", "elevator" } do
				if IsValid(rig[k]) then DoneObject(rig[k]); n = n + 1 end
			end
			D.rigs[bld] = nil
		end
	end
	return n
end

-- Brief 26's saved-rope investigation. SpaceElevatorRope has no class_parent in
-- Lua/_EntityData.generated.lua:20651; EntityClass.lua:9-12,50 makes it a CObject,
-- not an Object (archived build 25579348 / 1.1.1.406343). Inspect by ENTITY before
-- removing anything. Native ownership comes from SpaceElevatorBase.pod/ropes
-- (Lua/Buildings/SpaceElevator.lua:56-69), not the old sweep's distance heuristic.
local function prop_owners()
	local owners = {}
	local function add(rig, label)
		for _, key in ipairs{ "elevator", "tunnel", "cabin", "receiver", "pod" } do
			if IsValid(rig[key]) then owners[rig[key]] = label end
		end
		for _, o in ipairs(rig.ropes or empty_table) do
			if IsValid(o) then owners[o] = label end
		end
	end
	for bld, rig in pairs(D.rigs) do
		if is_depot(bld) then add(rig, "depot:" .. tostring(bld.handle)) end
	end
	for i, rig in ipairs(D.previews or empty_table) do add(rig, "preview:" .. i) end
	AllMapsForEach(true, "SpaceElevatorBase", function(bld)
		add(bld, "vanilla:" .. tostring(bld.handle))
	end)
	return owners
end

local function print_prop(row, index, owner, action)
	local o = row.object
	local delete_list = rawget(_G, "ObjsToDeleteOnLoadGame")
	local delete_on_load = type(delete_list) == "table" and tostring(not not delete_list[o]) or "unavailable"
	print(string.format("%s prop %s index=%d object=%s class=%s entity=%s slot=%s env=%s pos=%s visual=%s scale=%s parent=%s owner=%s Object=%s permanent=%s gameflags=%s enumflags=%s delete_on_load=%s",
		log_prefix, action, index, tostring(o), tostring(o.class), row.entity,
		tostring(o:GetMapSlot()), environment_of(o), tostring(row.pos), tostring(o:GetVisualPos()),
		tostring(row.scale), tostring(o:GetParent()), owner or "UNOWNED",
		tostring(IsKindOf(o, "Object")), tostring(o:GetGameFlags(const.gofPermanent) ~= 0),
		tostring(o:GetGameFlags()), tostring(o:GetEnumFlags()), delete_on_load))
end

-- Recovery signature from the owner's actual InspectProps() result, build 25579348:
-- Mars.exe-20260930-17.32.07-6aba6e65.log:343,345,347,349 (archived with brief 26).
-- These parentless duplicates are outside DeleteOnLoadGame and already non-permanent.
-- This identifies that saved rig only; a rope elsewhere needs its own inspection.
local function identified_legacy_rope(o)
	if o.class ~= "SpaceElevatorRope" or o:GetEntity() ~= "SpaceElevatorRope"
		or o:GetMapSlot() ~= 2 or environment_of(o) ~= "Underground" or o:GetScale() ~= 75
		or o:GetParent() or o:GetGameFlags(const.gofPermanent) ~= 0 then return false end
	local p = o:GetPos()
	local z = p:z()
	return p:x() == 384000 and p:y() == 303100
		and (z == 10000 or z == 17500 or z == 25000 or z == 32500)
end

function D.Sweep()
	local n = sweep_rigs()
	local owners, candidates = prop_owners(), {}
	AllMapsForEach(true, "CObject", function(o)
		if not IsValid(o) or owners[o] then return end
		if o.smr_depot_prop or identified_legacy_rope(o) then candidates[#candidates + 1] = o end
	end)
	local orphans = 0
	for i, o in ipairs(candidates) do
		if IsValid(o) then
			print_prop({ object = o, entity = o:GetEntity(), pos = o:GetPos(), scale = o:GetScale() },
				i, owners[o], "sweep")
			DoneObject(o)
			if not IsValid(o) then orphans = orphans + 1 end
		end
	end
	print(log_prefix, "swept", n, "props of gone depots and", orphans, "orphaned props")
end

function D.InspectProps()
	local owners, rows, seen = prop_owners(), {}, {}
	local visited = 0
	local function visit(o)
		if not IsValid(o) or seen[o] then return end
		seen[o] = true
		visited = visited + 1
		local entity = o:GetEntity() or ""
		if entity:find("Elevator", 1, true) then
			rows[#rows + 1] = { object = o, entity = entity, map = o:GetMap(),
				pos = o:GetPos(), scale = o:GetScale() }
		end
		if o.ForEachAttach then o:ForEachAttach(visit) end
	end
	AllMapsForEach(true, "CObject", visit)
	table.sort(rows, function(a, b)
		local ak = tostring(a.object:GetMapSlot()) .. ":" .. tostring(a.pos) .. ":" .. a.entity .. ":" .. tostring(a.object)
		local bk = tostring(b.object:GetMapSlot()) .. ":" .. tostring(b.pos) .. ":" .. b.entity .. ":" .. tostring(b.object)
		return ak < bk
	end)
	D.inspected_props = rows
	local ropes, unowned, non_object = 0, 0, 0
	for i, row in ipairs(rows) do
		local o = row.object
		print_prop(row, i, owners[o], "inspect")
		if row.entity == "SpaceElevatorRope" then
			ropes = ropes + 1
			if not IsKindOf(o, "Object") then non_object = non_object + 1 end
			if not owners[o] and not o:GetParent() then unowned = unowned + 1 end
		end
	end
	print(string.format("%s prop census CObjects=%d elevator_entities=%d ropes=%d ropes_outside_Object=%d parentless_unowned_ropes=%d; read-only",
		log_prefix, visited, #rows, ropes, non_object, unowned))
	return rows
end

-- Only called after the owner/agent has identified a row in InspectProps()'s log.
-- Re-read ownership and identity: an old index cannot delete a replacement or a
-- rope that has since joined a live rig. No load handler calls this repair.
function D.RemoveInspectedRope(index)
	local row = (D.inspected_props or empty_table)[index]
	local o = row and row.object
	if not IsValid(o) then print(log_prefix, "rope removal refused: inspect again"); return false end
	local owner = prop_owners()[o]
	if row.entity ~= "SpaceElevatorRope" or o:GetEntity() ~= row.entity or o:GetMap() ~= row.map
		or o:GetPos() ~= row.pos or o:GetScale() ~= row.scale or row.scale ~= 75
		or environment_of(o) ~= "Underground" or owner or o:GetParent() then
		print(log_prefix, "rope removal refused: changed, owned, attached, or not an underground 75% rope", index)
		return false
	end
	print_prop(row, index, owner, "remove")
	DoneObject(o)
	local removed = not IsValid(o)
	print(log_prefix, "rope removal index", index, "valid_after", not removed)
	return removed
end

if not IsValidThread(rawget(D, "sweeper")) then
	D.sweeper = CreateGameTimeThread(function()
		while true do
			Sleep(2000)
			if next(D.rigs) then
				local n = sweep_rigs()
				if n > 0 then print(log_prefix, "sweeper removed", n, "props of a deleted depot") end
			end
		end
	end)
end

local function for_each_depot(fn)
	AllMapsForEach("map", "Building", function(bld)
		if is_depot(bld) then fn(bld) end
	end)
end

function D.Redress()
	local n = 0
	for_each_depot(function(bld) D.Dress(bld); n = n + 1 end)
	print(log_prefix, "redressed", n)
end

function D.Set(key, value)
	if D.layout[key] == nil then
		print(log_prefix, "no such layout key", tostring(key))
		return
	end
	D.layout[key] = value
	print(log_prefix, "layout", key, "=", tostring(value))
	D.Redress()
end

function D.Show()
	for _, k in ipairs(table.keys(D.layout, true)) do
		print(log_prefix, "layout", k, "=", tostring(D.layout[k]))
	end
end

function OnMsg.LoadGame()
	D.rigs = setmetatable({}, { __mode = "k" })   -- the visuals were DeleteOnLoadGame
	D.previews = {}
	D.inspected_props = nil
	for_each_depot(D.Dress)
end

-- No thread of ours enters a save: the cycles stop before it and restart after it (the previews'
-- pattern, 2026-09-29).
function OnMsg.SaveGameStart()
	for _, rig in pairs(D.rigs) do stop_cycle(rig) end
	for _, p in ipairs(D.previews or empty_table) do stop_cycle(p) end
end

function OnMsg.SaveGameDone()
	for _, rig in pairs(D.rigs) do start_cycle(rig) end
	for _, p in ipairs(D.previews or empty_table) do start_cycle(p) end
end

-- ---- reads ----------------------------------------------------------------------------------
function D.Report()
	local n = 0
	for_each_depot(function(bld)
		n = n + 1
		local pos = bld:GetPos()
		local q, r = WorldToHex(pos)
		local rig = D.rigs[bld] or {}
		local labelled = bld.city and table.find(bld.city.labels.Station or empty_table, bld) and "yes" or "NO"
		print(string.format("%s depot %d slot=%s env=%s pos=%s hex=(%d,%d) angle=%d entity=%s valid=%s working=%s label.Station=%s elevator=%s tunnel=%s cabin=%s ropes=%d",
			log_prefix, n, tostring(bld:GetMapSlot()), environment_of(bld), tostring(pos), q, r,
			bld:GetAngle() / 60, bld:GetEntity(), tostring(IsValidEntity(bld:GetEntity())), tostring(bld.working),
			labelled, tostring(IsValid(rig.elevator)), tostring(IsValid(rig.tunnel)),
			IsValid(rig.cabin) and tostring(rig.cabin:GetPos()) or "none", #(rig.ropes or empty_table)))
		-- brief 26: the terrain hole the entity carries (the pit and the well render only through it),
		-- the receiver, and vanilla's signs
		local hole = HasAnySurfaces(bld, EntitySurfaces.TerrainHole, true)
		local hole_box = hole and GetEntitySurfacesBBox(bld:GetEntity(), EntitySurfaces.TerrainHole, EntitySurfaces.TerrainHole, bld:GetState())
		print(string.format("%s   terrain_hole=%s bbox=%s receiver=%s (%s) signs=%d hexes=%d",
			log_prefix, tostring(hole), hole_box and tostring(hole_box) or "-",
			IsValid(rig.receiver) and tostring(rig.receiver:GetEntity()) or "none",
			IsValidEntity(D.layout.receiver_entity or "") and "entity imported" or "ENTITY MISSING: import it",
			#(bld:GetAttaches("UnderconstructionSign") or empty_table), #(bld:GetEntityOutlineShape() or empty_table)))
		-- the elevator art's own auto-attaches (item 6: which one is the frame in the core, if any is)
		if IsValid(rig.elevator) then
			local n_att = 0
			rig.elevator:ForEachAttach(function(a)
				n_att = n_att + 1
				local bb = a:GetEntityBBox()
				print(string.format("%s   elevator attach %d entity=%s class=%s offset=%s spot=%s bbox_z=%d..%d", log_prefix, n_att,
					tostring(a:GetEntity()), a.class, tostring(a:GetAttachOffset()), tostring(a:GetAttachSpot()),
					(bb and bb:IsValid()) and bb:minz() or 0, (bb and bb:IsValid()) and bb:maxz() or 0))
			end)
			print(log_prefix, "   elevator attaches", n_att)
		end
		for _, name in ipairs(table.keys(design_spots, true)) do
			local idx = bld:GetSpotBeginIndex(name)
			local want = bld:GetRelativePoint(design_spots[name])
			local wq, wr = WorldToHex(want)
			if idx and idx >= 0 then
				local got = bld:GetSpotPos(idx)
				local gq, gr = WorldToHex(got)
				print(string.format("%s   %-16s spot=%s hex=(%d,%d) design=%s off=%d cm %s", log_prefix, name,
					tostring(got), gq, gr, tostring(want), got:Dist(want),
					(gq == wq and gr == wr and got:Dist(want) < 100) and "MATCH" or "DIFFERENT"))
			else
				print(string.format("%s   %-16s MISSING on the entity; design hex=(%d,%d)", log_prefix, name, wq, wr))
			end
		end
		for i = 1, 2 do
			local el = bld.GetConnectorElement and bld:GetConnectorElement(i)
			print(string.format("%s   connector %d element=%s pos=%s", log_prefix, i,
				IsValid(el) and el.class or "none", IsValid(el) and tostring(el:GetPos()) or "-"))
		end
	end)
	print(log_prefix, "depots", n)
end

-- The ceiling read (brief 25: size the rope so it never visibly stops short, and report what was
-- measured). Prints the camera, every elevator on the current map with its own shaft top, and,
-- within radius_m of each, every object group standing well above the ground there, by entity: the
-- stalactites and cave pillars hang from the ceiling, so their heights are the ceiling's.
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
			-- Terrain-relative GetPos() has no Z. GetVisualPos supplies terrain Z
			-- (GameObject.lua:510-515, archived build 25579348 / 1.1.1.406343).
			local oz = o:GetVisualPos():z() - ground
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

-- ---- free-standing previews (2026-09-29, kept): scaled vanilla art on the hex under the cursor,
-- for comparing by eye. Visual only; nothing is kept across a load.
--   SMRElevatorDepotDev.Preview(scale, mode, rope_m)         the elevator with its cabin cycle
--   SMRElevatorDepotDev.PreviewTunnel(scale, lift_m, angle_deg, entity)
--   SMRElevatorDepotDev.ClearPreview()
D.previews = D.previews or {}

function D.Preview(scale, mode, rope_m)
	local map = CurrentMap
	local L = D.layout
	scale = scale or L.scale
	local underground = GetEnvironment(map) == "Underground"
	mode = mode or (underground and "up" or "down")
	rope_m = rope_m or (mode == "up" and L.rope_underground_m or L.rope_surface_m)
	local pos = point(HexToWorld(WorldToHex(GetTerrainCursor())))
	pos = pos:SetZ(terrain.GetHeight(map, pos))
	local p = { scale = scale, mode = mode, base = pos, ropes = {} }
	p.elevator = PlaceObjectIn("ShapeshifterAutoAttach", map)
	p.elevator:ChangeEntity(L.elevator_entity)
	p.elevator.fx_actor_class = "SpaceElevator"
	unselectable(p.elevator)
	p.elevator:SetPos(pos)
	p.elevator:SetScale(scale)
	DeleteOnLoadGame(p.elevator)
	p.cabin = free_prop("SpaceElevatorCabin", map, pos, scale)
	local rope_step = MulDivRound(100 * guim, scale, 100)
	local z = 0
	while z < rope_m * guim do
		p.ropes[#p.ropes + 1] = free_prop("SpaceElevatorRope", map, pos + point(0, 0, z), scale)
		z = z + rope_step
	end
	local reach = mode == "up" and Max(rope_m, 120) * guim or -L.travel_down_m * guim
	p.far = pos + point(0, 0, reach)
	D.previews[#D.previews + 1] = p
	start_cycle(p)
	print(string.format("%s preview %d: %d%% at %s env=%s mode=%s rope %d m (%d tiles), cabin travels %d m",
		log_prefix, #D.previews, scale, tostring(pos), GetEnvironment(map), mode, rope_m, #p.ropes, reach / guim))
	return p
end

function D.PreviewTunnel(scale, lift_m, angle_deg, entity)
	local map = CurrentMap
	local L = D.layout
	scale = scale or L.scale
	entity = entity or L.tunnel_entity or "TrainTunnelUniversal"
	local lift = lift_m and (lift_m * guim) or L.tunnel_lift
	local pos = point(HexToWorld(WorldToHex(GetTerrainCursor())))
	pos = pos:SetZ(terrain.GetHeight(map, pos) + lift)
	local v = PlaceObjectIn("ShapeshifterAutoAttach", map)
	v:ChangeEntity(entity)
	unselectable(v)
	v:SetPos(pos)
	v:SetAngle((angle_deg or L.tunnel_angle) * 60)
	v:SetScale(scale)
	DeleteOnLoadGame(v)
	D.previews[#D.previews + 1] = { elevator = v, ropes = {} }
	local mouth = MulDivRound(50 * guim, scale, 100)   -- Trackconnector0 at (5000, 0, 0), entities.dat 25390750
	print(string.format("%s tunnel preview %d: %s at %d%%, lifted %d cm; its rail meets vanilla track (800 cm) at %d cm here; mouth connector %d cm from its centre (a hex is 1000)",
		log_prefix, #D.previews, entity, scale, lift, MulDivRound(800, scale, 100) + lift, mouth))
	return v
end

function D.ClearPreview()
	for _, p in ipairs(D.previews) do
		stop_cycle(p)
		for _, o in ipairs(p.ropes or empty_table) do if IsValid(o) then DoneObject(o) end end
		if IsValid(p.cabin) then DoneObject(p.cabin) end
		if IsValid(p.elevator) then DoneObject(p.elevator) end
	end
	print(log_prefix, "previews cleared", #D.previews)
	D.previews = {}
end
