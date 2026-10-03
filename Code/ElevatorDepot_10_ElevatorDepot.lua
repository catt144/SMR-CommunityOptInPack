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
-- Brief 27 wires the pair (the WIRING section at the end of this file): per-trip cabin loads on an
-- hourly schedule, the four row modes set on the surface half and shown read-only underground, Drone Access on both halves
-- (default off), one pair per colony, and what a surviving half does. No drone crew (owner, 2026-10-01).
--
-- Console, for the owner's sitting (output lands in the game log as [ElevatorDepot]):
--   SMRElevatorDepotDev.Report()           every depot: map, hex, label, its 14 spots, connector elements
--   SMRElevatorDepotDev.Measure()          the current map's camera, elevators and ceiling objects
--   SMRElevatorDepotDev.Show()             the live layout table
--   SMRElevatorDepotDev.Set("key", value)  move a visual by eye, e.g. Set("tunnel_lift", 250),
--                                          Set("scale", 80), Set("rope_underground_m", 400),
--                                          Set("receiver_z", -250), Set("signs", true),
--                                          Set("cabin_hide_below", -500); re-dresses all
--   SMRElevatorDepotDev.Redress()          rebuild every depot's visuals from the layout
--   SMRElevatorDepotDev.Sweep()            clear gone-depot props and the identified legacy rope tiles
--   SMRElevatorDepotDev.InspectProps()     read-only census, including CObject ropes and attachments
--   SMRElevatorDepotDev.RemoveInspectedRope(n)  remove ONE inspected, unowned underground 75% rope
--   SMRElevatorDepotDev.Preview(...)       the earlier free-standing previews still work (see below)
--   SMRElevatorDepotDev.Pair()             brief 27: the pair, the cabin, every row on both halves, drone reach
--   SMRElevatorDepotDev.SetRow(surface, "Metals", "import")  a row by console (either vocabulary); surface half only
--   SMRElevatorDepotDev.SetDroneAccess(half, true)        Drone Access by console
-- SMRElevatorStationDev is kept as an alias, so the earlier console lines still run.
-- Shipping (brief 34, 2026-10-02): the table is SMRElevatorDepot; SMRElevatorDepotDev and
-- SMRElevatorStationDev stay as aliases for the shared TestKit's installed slots. Not persisted.

SMRElevatorDepot = rawget(_G, "SMRElevatorDepot") or rawget(_G, "SMRElevatorDepotDev") or {}
SMRElevatorDepotDev = SMRElevatorDepot
SMRElevatorStationDev = SMRElevatorDepot
local D = SMRElevatorDepot

local template_id = "SMROptInElevatorDepotDev"
local entity_id = "SMROptInElevatorDepot"
local mod_entities = { SMROptInElevatorDepot = true, SMROptInElevatorDepotReceiver = true }
local log_prefix = "[ElevatorDepot]"

-- FIX_POLICY §8: per-event dev lines print only under SMROptInPack.TrainTrace (00_Core.lua).
-- The console read-outs below (Report, Pair, Measure, Show, ...) print regardless.
local function trace(...)
	local pack = rawget(_G, "SMROptInPack")
	if pack and pack.TrainTrace then print(...) end
end

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
	cabin_hide_below = -635,            -- sitting B (2026-09-30): the cabin (r 537, 10.7 m across at 75 %) showed in
	                                    -- the pit under the rear cap once it sank through the well's floor (-880);
	                                    -- its underside is 245 under its origin, so below this many cm under the
	                                    -- elevator's base the cabin is not drawn, and it is drawn again on the way up
	-- brief 27 (the wiring; live tunables, owner 2026-09-29: "leg time, pause and capacity")
	cabin_leg_minutes = 60,             -- one leg per game hour (SpaceElevator.lua:7's travel_time is 1 h)
	cabin_pause_minutes = 0,            -- parked at each end between legs
	cabin_capacity = 250,               -- resource units per leg, doubled by the depot's own upgrade
	cabin_follows_schedule = true,      -- the cabin art rides the real legs; false restores the show cycle
	row_words = "station",              -- "station": Import/Export/Balanced/Not accepted per half (ruling 2);
	                                    -- "elevator": vanilla elevator's Surface/Underground/ON/OFF (recommendation 3)
}

-- The vanilla Station's spot names at the design's positions plus Top (depot_build.py `spots()`),
-- so Report() can say whether the imported entity carries what was designed.
local design_spots = {
	Trackconnector1 = point(-5000, 0, 800), Trackdirection1 = point(-6000, 0, 800),
	Trackconnector2 = point(1000, 0, 800), Trackdirection2 = point(0, 0, 800),
	Ramparrive1 = point(-3600, -335, 800), Stop1 = point(-500, -335, -1400), Spawn2 = point(-500, -335, -1400),
	Spawn1 = point(-500, 335, -1400), Stop2 = point(-500, 335, -1400), Rampdepart1 = point(0, 335, -1400),
	Ramparrive2 = point(900, 335, -1400), Rampdepart2 = point(800, -335, -1400),
	Sign1 = point(-5000, 0, 0),   -- Sign2 dropped (brief 26, item 1): connector 2 is buried
	Top = point(-3500, 0, 1780),  -- the loader's required sign spot (Mod.lua:119), 2 m over the mouth crown
}

-- ---- the class ---------------------------------------------------------------------------------
DefineClass.SMROptInElevatorDepotDevBase = {
	__parents = { "Station" },
	max_storage_per_resource = 250000,
	upgrade1_id = "SMROptInElevatorDepotDev_Capacity",
	upgrade1_display_name = Untranslated("Expanded Depot"),
	upgrade1_description = Untranslated("Raises cabin capacity to 500 per leg and storage to 500 per resource at both ends. One purchase for the pair; either half can build it."),
	-- vanilla's default; the storage glyph (expanded_warehousing_02) is set on the template preset itself,
	-- because the editor's "Default upgrade icon" lint takes the class value AS the default (Composite.lua:327-335).
	upgrade1_icon = "UI/IconsRemaster/Upgrades/expanded_warehousing_01.png",
	upgrade1_upgrade_cost_Metals = 10000,
	upgrade1_upgrade_cost_Concrete = 10000,
	upgrade1_can_disable = false,
}

-- sectionCustom resolves only the template's exact object_class, not its parents.
-- Alias the native section, including its construction/route buttons and train readout.
-- Archived 1.1.1.406343: XDef/sectionCustom.generated.lua:14-36, customStation.generated.lua.
function D.InstallStationPanel()
	for _, registry in ipairs{ rawget(_G, "XDefs") or {}, rawget(_G, "XTemplates") or {} } do
		if registry.customStation then registry.customSMROptInElevatorDepotDevBase = registry.customStation end
	end
	-- UpgradableBuilding.lua:67-115 (406343) injects zero costs onto descendants,
	-- shadowing inherited values. Publish the ruled costs on our final class too.
	local classes = rawget(_G, "g_Classes")
	local depot = classes and classes.SMROptInElevatorDepotDev
	if depot then
		depot.upgrade1_upgrade_cost_Metals = 10000
		depot.upgrade1_upgrade_cost_Concrete = 10000
	end
end
function OnMsg.ClassesBuilt() D.InstallStationPanel() end
function OnMsg.ModsReloaded() D.InstallStationPanel() end
function OnMsg.DataLoaded() D.InstallStationPanel() end

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
	if D.HalfPlaced then D.HalfPlaced(self) end
end

function SMROptInElevatorDepotDevBase:Done(done_map)
	if D.HalfGone then D.HalfGone(self, done_map, "done") end
	D.Undress(self)
end

function SMROptInElevatorDepotDevBase:OnDestroyed()
	if D.HalfGone then D.HalfGone(self, nil, "destroyed") end
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
	-- Stay on the schedule follower even without a twin: it parks the cabin until pairing.
	if D.layout.cabin_follows_schedule and rig.bld and D.FollowTarget then
		rig.thread = CreateGameTimeThread(D.FollowLoop, rig)
		return
	end
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
					local z = from:z() + MulDivRound(target:z() - from:z(), i, steps)
					rig.cabin:SetPos(point(from:x(), from:y(), z), L.tick_ms)
					local hidden = rig.base and z < rig.base:z() + L.cabin_hide_below or false
					if hidden ~= (rig.cabin_hidden or false) then
						rig.cabin_hidden = hidden
						if hidden then
							PlayFX("ElevatorMoving", "end", rig.cabin)
							rig.cabin:ClearEnumFlags(const.efVisible)
						else
							rig.cabin:SetEnumFlags(const.efVisible)
							PlayFX("ElevatorMoving", "start", rig.cabin)
						end
					end
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

-- Brief 28: the colony's palette reaches the attached art. OnPlace paints the building's own
-- entity and its attaches synchronously (Building.lua:761-772 -> SetPalette :747-749 ->
-- SetObjectPaletteRecursive, Colorization.lua:846-858, all read on 406343), but Dress runs later,
-- in GameInit's thread and again after a load, so what it attaches was never painted: the owner's
-- paint_03 (2026-10-01) shows the depot's pads plain beside vanilla's banded elevator. The template
-- names vanilla's SpaceElevator's three palette colours, so these are the elevator's own colours.
-- SetColorizationMaterials is a no-op on an entity without a colourisation mask (:832-838, :881).
local function paint_rig(bld, rig)
	if not rawget(_G, "GetBuildingColors") or not rawget(_G, "GetCurrentColonyColorScheme") then return 0 end
	local cm1, cm2, cm3, cm4 = GetBuildingColors(GetCurrentColonyColorScheme(), bld)
	local n = 0
	local function paint(o)
		if IsValid(o) and o.SetObjectPaletteRecursive then
			o:SetObjectPaletteRecursive(cm1, cm2, cm3, cm4)
			n = n + 1
		end
	end
	paint(rig.elevator); paint(rig.tunnel); paint(rig.receiver); paint(rig.cabin)
	for _, o in ipairs(rig.ropes or empty_table) do paint(o) end
	return n
end

-- A scheme change repaints every Building through SetPalette (ColonyColorScheme.lua:95-103); the
-- recursion reaches the attached visuals and the rope tiles, so only the free cabin needs the hand.
function SMROptInElevatorDepotDevBase:SetPalette(cm1, cm2, cm3, cm4)
	Building.SetPalette(self, cm1, cm2, cm3, cm4)
	local rig = D.rigs[self]
	if rig and IsValid(rig.cabin) and rig.cabin.SetObjectPaletteRecursive then
		rig.cabin:SetObjectPaletteRecursive(cm1, cm2, cm3, cm4)
	end
end

-- Brief 28 (owner, 2026-10-01: "the preview of the building is only half rendered when in the
-- build mode"; their ruling the same evening: fix it under 28). CursorBuilding:Init
-- (Construction.lua:569-635, read on 406343) gives the placement cursor the template's entity and
-- that entity's own auto-attaches, paints it and sends CursorBuildingInit; the rig is dressed at
-- GameInit, which the cursor never runs, so the preview showed the portal shell alone. This hangs
-- the elevator art and the resting cabin on the cursor, painted with the template's colours as
-- vanilla paints the cursor itself (:600-603); no receiver, rope, signs or cycle. The attaches go
-- with the cursor when placement ends (vanilla's own handler: ModItemAttachment.lua:657-659).
function OnMsg.CursorBuildingInit(cursor)
	local template = cursor and cursor.template
	if not template or not IsKindOf(template, "SMROptInElevatorDepotDevBase") then return end
	local L = D.layout
	local at = point(L.elevator_x, L.elevator_y, L.elevator_z)
	local rig = {
		elevator = attach_visual(cursor, L.elevator_entity, at, L.elevator_angle, L.scale, "SpaceElevator"),
		cabin = L.cabin_on and attach_visual(cursor, "SpaceElevatorCabin", at, 0, L.scale) or nil,
		ropes = empty_table,
	}
	local painted = paint_rig(template, rig)
	trace(string.format("%s cursor dressed elevator=%s cabin=%s scale=%d palette=%d", log_prefix,
		tostring(IsValid(rig.elevator)), tostring(IsValid(rig.cabin)), L.scale, painted))
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
	local rig = { ropes = {}, bld = bld }
	rig.elevator = attach_visual(bld, L.elevator_entity, point(L.elevator_x, L.elevator_y, L.elevator_z),
		L.elevator_angle, L.scale, "SpaceElevator")
	if rig.elevator and L.elevator_hide ~= "" then
		local hide = {}
		for name in tostring(L.elevator_hide):gmatch("[^,%s]+") do hide[name] = true end
		local gone = 0
		rig.elevator:ForEachAttach(function(a)
			if hide[a:GetEntity() or ""] then DoneObject(a); gone = gone + 1 end
		end)
		trace(log_prefix, "elevator attaches hidden:", gone, "(", L.elevator_hide, ")")
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
	local painted = paint_rig(bld, rig)
	trace(string.format("%s dressed %s env=%s elevator=%s tunnel=%s cabin=%s ropes=%d scale=%d receiver=%s signs=%d cabin_hide_below=%d palette=%d",
		log_prefix, tostring(bld), environment_of(bld), tostring(IsValid(rig.elevator)), tostring(IsValid(rig.tunnel)),
		tostring(IsValid(rig.cabin)), #rig.ropes, L.scale, tostring(IsValid(rig.receiver)),
		#(bld:GetAttaches("UnderconstructionSign") or empty_table), L.cabin_hide_below, painted))
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
				if n > 0 then trace(log_prefix, "sweeper removed", n, "props of a deleted depot") end
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
	if D.WiringLoad then D.WiringLoad() end
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
			#(bld:GetAttaches("UnderconstructionSign") or empty_table), #(GetEntityOutlineShape(bld:GetEntity()) or empty_table)))
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
	if D.Pair then D.Pair() end
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

-- ==== WIRING (brief 27; owner rulings 2026-09-29 to 2026-10-01, spec section 11) ==================
-- Cargo crosses between the maps in the cabin; trains never change maps. Settled rulings:
--  1 per-trip loads: each half keeps its own storage; the cabin carries the cargo, nothing crosses
--    while it travels; 2 the four row modes on the depot's own rows (the depot owns them, a hub reads
--    them through D.HubEntry); 3 one setting per resource for the pair, surface Import = underground
--    Export, one word for the pair on both panels (Import = goes down, Export = comes up), no Balanced
--    (owner, 2026-10-01, sitting C), and (owner, 2026-10-01, amended) the SURFACE half owns it: its rows are the one writer,
--    the underground half's rows are read-only marks whose infotip points to the surface depot, and
--    the underground keeps a read-only cached copy a new surface twin adopts; 4 one pair per colony, either half anywhere, needs the underground unlocked;
--    5 one leg per game hour, down then up, repeating; 6 Drone Access on both halves, default off;
--    7 passengers need no depot code (none here); 8 vanilla's elevator is not touched.
-- Source, archived build 25579348 (1.1.1.406343):
--  Lua/Buildings/Elevator.lua:186-243 MapSharedDepot's four per-resource states, their icons and its
--    drone direction filter (ShouldAddRequestToCommandCenter); :89-110 overflow as a stockpile.
--  Lua/Buildings/Station.lua:964-995 SetDesiredAmount reads transport_policy; :1021-1051 accept states.
--  Lua/Units/Train.lua:744-831 a train's cargo writes: station:AddResource(+-n, res); room is the
--    demand request's target amount; BlackCube adjusts the city count.
--  Lua/Buildings/DroneControl.lua:741-757 every drone-controller registration asks the building's
--    ShouldAddRequestToCommandCenter; Lua/LRManager.lua:74 passes a map (shuttles), not a DroneControl;
--    Lua/_TaskRequest.lua:210 the default answers true.
--  Lua/X/BuildMenu.lua:735-751 the build-once check (template:CanBuildOnlyOnce() and the class label);
--    :400-408 GetAdditionalBuildingLock; Lua/Construction/Construction.lua:210-216 placement closes.
--  Lua/Colony.lua:655-661 underground_map_unlocked; Lua/DayTime.lua:69 NewMinute.
--  Lua/XDef/InfopanelButton.generated.lua:34-39 a button lands in idMainButtons;
--    Lua/XDef/ipBuilding.generated.lua:348-370 the Shuttle Access button (ToggleLRTServiceButton).
-- Persisted names (ban 1; inventory rows in reports/ELEVATOR_DEPOT_WIRING_20261001.md): the three
-- fields below on our own depot objects, each written only by this file's surface-row, toggle and
-- cabin code. Each tolerates its absence: an old save loads every unset row as Import,
-- Drone Access off and a fresh cabin at the surface.

local ROWS, DRONES, CABIN = "SMROptIn_depot_rows", "SMROptIn_depot_drones", "SMROptIn_depot_cabin"
local TARGETS = "SMROptIn_depot_targets"   -- the rows' slider targets (owner, 2026-10-01, sitting B)
D.ROWS, D.DRONES, D.CABIN, D.TARGETS = ROWS, DRONES, CABIN, TARGETS
local Base = SMROptInElevatorDepotDevBase
local apply_all

for k, v in pairs{ cabin_leg_minutes = 60, cabin_pause_minutes = 0, cabin_capacity = 250,
	cabin_follows_schedule = true, row_words = "station" } do
	if D.layout[k] == nil then D.layout[k] = v end
end
if D.layout.cabin_capacity == 42 then D.layout.cabin_capacity = 250 end -- in-place reload of the retired base

-- The pair's three settings (owner, 2026-10-01, sitting C: "maybe we should cut balanced from this. Make
-- it so the elevator only brings down or sends up"), in vanilla's elevator vocabulary (Elevator.lua:192-197,
-- its "bidirectional" dropped): to_underground (Import: goes down), to_surface (Export: comes up),
-- disabled (Not accepted). A row with no stored value is Import (owner, 2026-10-01, sitting C: "default
-- them to import since thats how most peoples first build out will be"): vanilla storage stays on, an old
-- save's unset (formerly Balanced) rows load as Import, and Not accepted is stored explicitly.
local states = { "to_surface", "to_underground", "disabled" }
local state_index = { to_surface = 1, to_underground = 2, disabled = 3 }
local up, down = "UI/IconsRemaster/Sections/elevator_resource_up.png", "UI/IconsRemaster/Sections/elevator_resource_down.png"
local no_accept = "UI/IconsRemaster/Sections/resource_no_accept.png"
-- One arrow meaning on both panels: the cabin's direction. Down = it goes down (Import), up = it comes up.
local state_icons = { to_surface = up, to_underground = down, disabled = no_accept }
local state_titles = { to_surface = "Surface", to_underground = "Underground", disabled = "OFF" }
-- the stations' words, verbatim from the hub's station rows (train_hub 45_TrainDistributionUI.lua:33-34,
-- `titles` and `following`), "Balanced" removed. ONE word for the pair, the surface's, on both panels
-- (owner, 2026-10-01, sitting C): Import = goes down, Export = comes up.
local word_titles = { import = "Import", export = "Export", disabled = "Not accepted" }
local word_next = { export = "import", import = "disabled", disabled = "export" }
-- drone desires per half (Station.lua:964-995), from each half's own flow: a half the cabin empties fills
-- like "send", a half the cabin fills drains like "accept"; a lone half is a plain station ("default").
local policy_of = { gather = "send", hand_out = "accept", plain = "default" }

local function normal_state(state)
	return (state == "to_surface" or state == "disabled") and state or "to_underground"
end

-- the pair's word, the surface's, shown on both panels
local function word_of(state)
	state = normal_state(state)
	if state == "to_underground" then return "import" end
	if state == "to_surface" then return "export" end
	return "disabled"
end

local function state_of(word)
	if word == "import" then return "to_underground" end
	if word == "export" then return "to_surface" end
	if word == "disabled" then return "disabled" end
end
D.WordOf, D.StateOf = word_of, state_of

local function is_underground(o) return environment_of(o) == "Underground" end
local gone = setmetatable({}, { __mode = "k" })    -- halves inside Done: still valid, no longer a half
local held = setmetatable({}, { __mode = "k" })    -- runtime: the "cabin held" line printed once
local connected = setmetatable({}, { __mode = "k" }) -- runtime: halves re-registered this session

local function live_depot(o)
	return is_depot(o) and not o.destroyed and not gone[o]
end

local pair_cache = false
function D.InvalidatePair() pair_cache = false end

local function all_depots()
	local list = {}
	local colony = rawget(_G, "UIColony")
	local label = colony and colony.labels and colony.labels[template_id]
	if label then
		for _, o in ipairs(label) do if live_depot(o) then list[#list + 1] = o end end
	else
		for_each_depot(function(o) if live_depot(o) then list[#list + 1] = o end end)
	end
	table.sort(list, function(a, b) return a.handle < b.handle end)
	return list
end

-- The pair: the first live depot by handle on each side. Further depots (an old save, or a path the
-- build-once check does not see) are unpaired extras: no cabin, a plain station to a hub, rows kept.
local function pair_now()
	local now = GameTime()
	if pair_cache and pair_cache.time == now then return pair_cache end
	local c = { time = now, extras = 0 }
	for _, o in ipairs(all_depots()) do
		if is_underground(o) then
			if c.underground then c.extras = c.extras + 1 else c.underground = o end
		elseif c.surface then
			c.extras = c.extras + 1
		else
			c.surface = o
		end
	end
	pair_cache = c
	return c
end

-- surface, underground when both halves stand; nil when o is given and is not one of them
function D.PairOf(o)
	local c = pair_now()
	if o and o ~= c.surface and o ~= c.underground then return end
	if c.surface and c.underground then return c.surface, c.underground end
end

function D.TwinOf(o)
	local s, u = D.PairOf(o)
	if not s then return end
	return o == s and u or s
end

function D.IsDepot(o) return is_depot(o) end

-- Native upgrade receipts live on the pair, not the colony. A replacement adopts the
-- survivor's paid receipt; removing both halves removes the purchase with them.
D.CAPACITY_UPGRADE = "SMROptInElevatorDepotDev_Capacity"
local function expanded(o)
	return o and o.upgrades_built and o.upgrades_built[D.CAPACITY_UPGRADE] or false
end

function D.CabinCapacity(o)
	return D.layout.cabin_capacity * ((expanded(o) or expanded(D.TwinOf(o))) and 2 or 1)
end

function D.SyncCapacity()
	if UIColony and not UIColony:IsUpgradeUnlocked(D.CAPACITY_UPGRADE) then
		UIColony:UnlockUpgrade(D.CAPACITY_UPGRADE)
	end
	for _, o in ipairs(all_depots()) do
		local bought = expanded(o) or expanded(D.TwinOf(o))
		if bought then
			o.upgrades_built = o.upgrades_built or {}
			-- Only the native buyer keeps the numeric tier receipt used for salvage
			-- refunds (Building.lua:983). A mirror grants the upgrade, not a second payment.
			o.upgrades_built[D.CAPACITY_UPGRADE] = true
			o.upgrade_on_off_state = o.upgrade_on_off_state or {}
			o.upgrade_on_off_state[D.CAPACITY_UPGRADE] = true
			o.upgrade_modifiers = o.upgrade_modifiers or {}
			o.upgrade_id_to_modifiers = o.upgrade_id_to_modifiers or {}
			o.upgrade_modifiers[D.CAPACITY_UPGRADE] = o.upgrade_modifiers[D.CAPACITY_UPGRADE] or {}
			o.upgrade_id_to_modifiers[D.CAPACITY_UPGRADE] = o.upgrade_id_to_modifiers[D.CAPACITY_UPGRADE] or {}
		end
		local storage = bought and 500000 or 250000
		local before = o.max_storage_per_resource
		o:SetBase("max_storage_per_resource", storage)
		if before ~= o.max_storage_per_resource and apply_all and o.supply and o.demand then apply_all(o) end
		ObjModified(o)
	end
end

-- The depot has its own capacity upgrade. Exclude only Capacity Network's storage
-- contribution; keep all other native/foreign modifiers. Modifiers.lua:40-103, build 406343.
function Base:ModifyValue(value, prop, modification)
	local m = modification or (self.modifications and self.modifications[prop])
	if prop == "max_storage_per_resource" and m then
		local filtered
		for _, mod in ipairs(m) do
			if mod.upgrade_id == "SMROptInTrainHub6_CapacityNetwork" then
				filtered = filtered or table.copy(m)
				filtered.percent = (filtered.percent or 100) - (mod.percent or 0)
				filtered.amount = (filtered.amount or 0) - (mod.amount or 0)
			end
		end
		m = filtered or m
	end
	return Modifiable.ModifyValue(self, value, prop, m)
end

function Base:ConstructUpgrade(id)
	if id == D.CAPACITY_UPGRADE then
		D.SyncCapacity()
		local twin = D.TwinOf(self)
		if twin and twin:IsUpgradeBeingConstructed(id) then return end
	end
	return Building.ConstructUpgrade(self, id)
end

function OnMsg.BuildingUpgraded(id, bld)
	if id == D.CAPACITY_UPGRADE and is_depot(bld) then D.SyncCapacity() end
end

local function rows_of(o) return rawget(o, ROWS) or empty_table end
-- The setting's owner: a paired underground half reads its surface twin; a lone half reads its own
-- (for a lone underground half, the read-only copy it keeps for the next surface depot).
local function owner_of(o)
	local s, u = D.PairOf(o)
	return s and o == u and s or o
end
function D.State(o, res) return normal_state(rows_of(owner_of(o))[res]) end

-- The row's target, percent of the surface half's capacity, set by the surface row's slider. Unset, it
-- is the hub's untouched-row default: the live dial as a percentage (45_TrainDistributionUI.lua:46-51,
-- D.RowState). A lone underground half reads its read-only copy, which a new surface twin adopts.
function D.Target(o, res)
	local owner = owner_of(o)
	local t = (rawget(owner, TARGETS) or empty_table)[res]
	if t then return t, true end
	local cap = owner.GetMaxStorage and owner:GetMaxStorage(res) or 0
	return cap > 0 and Clamp(MulDivRound(owner.desired_amount or 0, 100, cap), 0, 100) or 0, false
end

-- A half's own flow, for the hub's read and the drones (never shown): "gather" where the cabin loads
-- (surface on Import, underground on Export), "hand_out" where it delivers, "plain" for a lone half.
local function half_word(o, res)
	local state = D.State(o, res)
	if state == "disabled" then return "disabled" end
	if not D.TwinOf(o) then return "plain" end
	local ug = is_underground(o)
	if (state == "to_underground") ~= ug then return "gather" end
	return "hand_out"
end
D.HalfWord = half_word

local function vanilla(name)
	local station = rawget(_G, "g_Classes") and g_Classes.Station
	return station and station[name]
end

local function has_rows(o, res)
	return o.demand and o.demand[res] and o.supply and o.supply[res] and true or false
end

local function storage_request(o, request)
	local res = request and request.GetResource and request:GetResource()
	if res and ((o.supply and o.supply[res] == request) or (o.demand and o.demand[res] == request)) then
		return res
	end
end

-- Re-register with drone controllers so ShouldAddRequestToCommandCenter is asked again; the drones on
-- this half's storage requests are reset first, as MapSharedDepot does (Elevator.lua:322-325).
local function reconnect(o)
	if not (o.InterruptDrones and o.DisconnectFromCommandCenters and o.ConnectToCommandCenters) then return end
	o:InterruptDrones(nil, function(drone)
		local d, s = drone.d_request, drone.s_request
		if (d and storage_request(o, d)) or (s and storage_request(o, s)) then return drone end
	end)
	o:DisconnectFromCommandCenters()
	o:ConnectToCommandCenters()
	connected[o] = true
end

-- Vanilla's own accept state and drone desires follow the row. Returns true when vanilla changed.
local function apply_row(o, res)
	if not has_rows(o, res) then return false end
	local word = half_word(o, res)
	local enabled = o:IsResourceEnabled(res) and true or false
	local set_accept, changed = vanilla("SetAcceptResourceState"), false
	if word == "disabled" then
		if enabled and set_accept then set_accept(o, res, "disabled"); changed = true end
		return changed
	end
	if not enabled and set_accept then set_accept(o, res, "store"); changed = true end
	local policy = policy_of[word] or "default"
	o.transport_policy = o.transport_policy or {}
	if (o.transport_policy[res] or "default") ~= policy or changed then
		o.transport_policy[res] = policy ~= "default" and policy or nil
		local set_desired, dial = vanilla("SetDesiredAmount"), o.desired_amount
		if set_desired and dial then
			o.desired_amount = false
			set_desired(o, dial)
		end
		changed = true
	end
	return changed
end

apply_all = function(o)
	local n = 0
	for _, res in ipairs(o.storable_resources or empty_table) do
		if apply_row(o, res) then n = n + 1 end
	end
	return n
end

-- One setting per resource for the pair, written on the SURFACE half only (ruling 3 as amended
-- 2026-10-01). The underground half receives a read-only copy of the whole table.
function D.SetRow(o, res, value)
	if not live_depot(o) then return false, "not a live depot half" end
	if is_underground(o) then return false, "the underground rows are read-only: change them on the surface Elevator Depot" end
	if not has_rows(o, res) then return false, "this depot does not store " .. tostring(res) end
	local state = state_index[value] and value or state_of(value)
	if not state then return false, "unknown mode " .. tostring(value) end
	local rows = rawget(o, ROWS) or {}
	rows[res] = state ~= "to_underground" and state or nil   -- Import is the default, stored as absence
	rawset(o, ROWS, rows)
	local twin = D.TwinOf(o)
	if twin then rawset(twin, ROWS, table.copy(rows)) end
	for _, half in ipairs(twin and { o, twin } or { o }) do
		apply_row(half, res)
		if rawget(half, DRONES) then reconnect(half) end   -- the direction filter changed
		ObjModified(half)
	end
	trace(string.format("%s row %s = %s word=%s (set on the surface half %s; underground %s %s)",
		log_prefix, res, state, word_of(state), tostring(o.handle),
		twin and tostring(twin.handle) or "none", twin and "copy updated" or "absent"))
	return true
end

-- The slider (surface rows only). Same bounds and message as the hub's D.Set (40_TrainDistribution.lua:279-283).
function D.SetTarget(o, res, percent)
	if not live_depot(o) then return false, "not a live depot half" end
	if is_underground(o) then return false, "the underground rows are read-only: change them on the surface Elevator Depot" end
	if not has_rows(o, res) then return false, "this depot does not store " .. tostring(res) end
	if type(percent) ~= "number" or percent ~= percent or percent < 0 or percent > 100 then
		return false, "slider must be 0 to 100 percent"
	end
	percent = math.tointeger(math.floor(percent + 0.5))
	local targets = rawget(o, TARGETS) or {}
	if targets[res] == percent then return true end
	targets[res] = percent
	rawset(o, TARGETS, targets)
	local twin = D.TwinOf(o)
	if twin then rawset(twin, TARGETS, table.copy(targets)) end
	trace(string.format("%s target %s = %d%% (set on the surface half %s; underground %s)", log_prefix, res, percent,
		tostring(o.handle), twin and (tostring(twin.handle) .. " copy updated") or "absent"))
	ObjModified(o)
	if twin then ObjModified(twin) end
	return true
end

-- ---- the rows in the panel (sectionStorageRow calls these; Data/XDef/sectionStorageRow.lua:12-57)
-- Surface: a click cycles the setting. Underground: nothing to click; the row only shows.
function Base:ToggleAcceptResource(res, broadcast)
	if not live_depot(self) or not has_rows(self, res) then return end
	if is_underground(self) then
		trace(log_prefix, "underground rows are read-only; change", res, "on the surface Elevator Depot")
		return
	end
	local state = D.State(self, res)
	local nxt
	if D.layout.row_words == "elevator" then
		nxt = states[state_index[state] % #states + 1]
	else
		nxt = state_of(word_next[word_of(state)])
	end
	D.SetRow(self, res, nxt)
end

-- Vanilla's "apply to all stations" (Station.lua:1021-1027) reaches us as a method call. It never
-- writes the depot's setting: vanilla is put back to what the surface row says.
function Base:SetAcceptResourceState(res, state, broadcast)
	local set_accept = vanilla("SetAcceptResourceState")
	if broadcast or not live_depot(self) or not has_rows(self, res) then
		if set_accept then return set_accept(self, res, state, broadcast) end
		return
	end
	apply_row(self, res)
end

function Base:GetResAcceptIcon(res)
	return state_icons[D.State(self, res)]
end

function Base:GetResAcceptStateText(res)
	return Untranslated(state_titles[D.State(self, res)])
end

local surface_help = {
	import = "this half gathers it for the cabin: trains (and drones, with Drone Access on) bring it here, and each down leg carries it to the underground half.",
	export = "the cabin brings it up from the underground half on each up leg; trains (and drones, with Drone Access on) take it away from here.",
	disabled = "the cabin never carries it; trains take away what is left here.",
}
-- the underground half's flow in words (owner: "its infotip say its current info")
local underground_says = {
	to_surface = "Leaves this half: trains (and drones, with Drone Access on) bring it here, and each up leg carries it to the surface half.",
	to_underground = "Arrives here: each down leg brings it from the surface half; trains (and drones, with Drone Access on) take it away from here.",
	disabled = "The cabin never carries it; trains take away what is left here.",
}
D.UndergroundSays = underground_says

function D.RowText(o, res)
	local state, ug = D.State(o, res), is_underground(o)
	local word = word_titles[word_of(state)]
	local lead = word
	if D.layout.row_words == "elevator" then lead = "Status: " .. state_titles[state] .. ".<newline>" .. word end
	local text
	if ug then
		text = lead .. " (set on the surface Elevator Depot). " .. underground_says[state]
		text = text .. "<newline><newline>Read-only here: to change it, use the surface Elevator Depot."
	else
		text = string.format("%s: %s<newline>The underground half shows the same word, read-only.<newline>Vanilla elevator's word: %s.",
			lead, surface_help[word_of(state)], state_titles[state])
		-- the hub's slider line (45_TrainDistributionUI.lua:101-102); the amount via MulDivRound, not a bare /
		local percent = D.Target(o, res)
		text = text .. "<newline><newline>Slider: " .. tostring(percent) .. "% of current capacity ("
			.. tostring(MulDivRound(MulDivRound(o:GetMaxStorage(res), percent, 100), 1, const.ResourceScale)) .. ")."
	end
	-- Brief 30: lead with the missing-twin state, before the longer flow help.
	-- Both halves retain their settings and plain-station behavior unchanged.
	if not D.TwinOf(o) then
		local missing = ug and "No surface twin: the cabin is idle and this half works as a plain station; the setting is kept for the next surface depot."
			or "No underground twin: the cabin is idle and this half works as a plain station."
		text = missing .. "<newline><newline>" .. text
	end
	return text .. "<newline><newline>Drone Access: " .. (rawget(o, DRONES) and "on" or "off") .. "."
end

function Base:ResourceRolloverText(res)
	return Untranslated(D.RowText(self, res))
end

-- The rows in the hub's station-row shape (owner, 2026-10-01, sitting B: "We still need the sliders for
-- target values, and I would like the text to resemble our station ones"): title "<resource> · <word>",
-- a target slider on the surface rows, vanilla's stock/capacity on the right and its red no-accept look
-- for Not accepted (Data/XDef/sectionStorageRow.lua:16-32). Copied from the hub's 45_TrainDistributionUI.lua
-- (fit_title :118-131, make_slider :133-181, update_row :183-217): those are locals of the hub's file, so
-- the depot cannot call them without depending on the hub; the copies differ only where noted. The hub
-- patch keeps the hub's own slider and title off depot rows (its network() answers false), so nothing
-- is drawn twice. Underground rows: the same title, no slider, no click (the read-only ruling).
local read_only_hint = "Read-only here: change it on the surface Elevator Depot."

-- the word the row title shows, the same on both halves: the hub's D.RowState rule (disabled when vanilla
-- storage is off), else the pair's word
function D.RowWord(o, res)
	if not o:IsResourceEnabled(res) then return "disabled" end
	return word_of(D.State(o, res))
end

-- The hub's fit_title (train_hub 45_TrainDistributionUI.lua:114-130) with the ceiling its author wrote
-- (`math.ceil(... / sx)`, `:124`, `:129`). In the engine int/int truncates (EF-116), so the hub's math.ceil
-- gets an already-floored integer and the box can lose a unit; XWindow then scales MaxHeight and the
-- padding to pixels separately through ScaleXY (CommonLua/X/XWindow.lua:766-784, archived build 25579348),
-- which can lose another. At scale 1000 both are exact; at the depot panel's larger scale two lines no
-- longer fit and the label shortened "Exotic Minerals · Not accepted" to "Exotic Minerals · N..." (sitting
-- E, depot_rows_06; the hub station at its scale wraps it, depot_rows_07). So: a real ceiling, plus
-- FIT_SLACK units for the scaling truncation (2 units: far below a third line, which needs ~35).
local FIT_SLACK = 2
local function mul_div_ceil(a, b, c)
	local q = MulDivRound(a, b, c)
	if q * c < a * b then q = q + 1 end
	return q
end

local function fit_title(title)
	local font = title:GetFontId()
	local sx, sy = title.scale:xy()
	local padding = title:GetPadding()
	local width = 154
	for word in (title.text or ""):gsub("<[^>]*>", ""):gmatch("%S+") do
		width = Max(width, mul_div_ceil(UIL.MeasureText(word, font) + 1, 1000, sx) + FIT_SLACK
			+ padding:minx() + padding:maxx())
	end
	title:SetMinWidth(width)
	title:SetMaxWidth(width)
	title:SetMaxHeight(mul_div_ceil(2 * title.font_height, 1000, sy) + FIT_SLACK
		+ padding:miny() + padding:maxy())
end
D.FitTitle = fit_title

-- hub make_slider; OnScroll writes the depot's target instead of the hub's row
local function make_slider(row, context)
	local title, right = row.idSectionTitle, row.idSectionTitleRight
	if not title or not right or title.parent ~= right.parent then
		print(log_prefix, "sectionStorageRow title line unavailable")
		return
	end
	right:SetDock("right")
	title:SetDock("left")
	title:SetMaxWidth(154)
	title:SetShorten(true)
	local slider = InfopanelSlider:new({ Id = "idDistributionSlider", Dock = "box", VAlign = "stretch",
		MinWidth = 64, MinHeight = 0, MaxHeight = 0, Margins = box(6, 0, 6, 0),
		Min = 0, Max = 100, StepSize = 1, RolloverTemplate = "", RolloverOnFocus = false,
		OnScroll = function(self, value)
			local ctx = row.context
			local st, res = ctx[1], ctx.res
			if is_depot(st) and not is_underground(st) and D.RowWord(st, res) ~= "disabled" then
				D.SetTarget(st, res, value)
			end
		end,
		OnShortcut = function(self, shortcut, source)
			if shortcut == "LeftShoulder" or shortcut == "RightShoulder" then
				if self:GetEnabled() then
					self:ScrollTo(Clamp(self:GetScroll() + (shortcut == "LeftShoulder" and -1 or 1), 0, 100))
				end
				return "break"
			end
			return InfopanelSlider.OnShortcut(self, shortcut, source)
		end,
	}, title.parent, context)
	slider.idBar:SetMinWidth(0)
	for _, child in ipairs(slider.idBar) do child:SetMinWidth(0) end
	row.depot_slider = slider
	if row.window_state == "open" then slider:Open() end
	return slider
end

-- hub update_row for a depot row; the Ctrl line of the hub's hint is left out (Ctrl does nothing here)
function D.DecorateRow(row, context)
	local o, res = context[1], context.res
	local word = D.RowWord(o, res)
	-- Publish the current text on the actual control. The vanilla row stores a
	-- translated <ResourceRolloverText(res)> formatter; a direct method read
	-- alone did not witness what the owner's tooltip displayed (OI-38 E5).
	row:SetRolloverText(Untranslated(D.RowText(o, res)))
	if is_underground(o) then
		row:SetTitle(T{Untranslated("<resource(res)> · " .. word_titles[word]), context})
		row:SetRolloverOnFocus(false)
		row:SetRolloverHint(Untranslated(read_only_hint))
		row:SetRolloverHintGamepad(Untranslated(read_only_hint))
		row.OnActivate = empty_func
		return
	end
	local slider = row.depot_slider or make_slider(row, context)
	if not slider then return end
	row:SetTitle(T{Untranslated("<resource(res)> · " .. word_titles[word]), context})
	fit_title(row.idSectionTitle)
	row:SetRolloverOnFocus(false)
	row:SetRolloverHint(Untranslated("<left_click> " .. word_titles[word_next[word]]))
	row:SetRolloverHintGamepad(Untranslated("<ButtonA> " .. word_titles[word_next[word]]))
	slider:SetEnabled(word ~= "disabled")
	-- SetScroll does not invoke OnScroll: merely opening/refreshing a row saves nothing (hub, :214)
	slider:SetScroll(D.Target(o, res))
	if slider.window_state == "open" then slider:UpdateProgress() end
end

local row_hook = false
function D.InstallRowHook()
	if row_hook then return true end
	local row = rawget(_G, "sectionStorageRow")
	local previous = row and row.OnContextUpdate
	if type(previous) ~= "function" then return false end
	row.OnContextUpdate = function(self, context, ...)
		local result = table.pack(previous(self, context, ...))
		local o = type(context) == "table" and context[1]
		if is_depot(o) and context.res and has_rows(o, context.res) then D.DecorateRow(self, context) end
		return table.unpack(result, 1, result.n)
	end
	row_hook = true
	return true
end

-- ---- the hub's read (rule 2: the depot owns the row, the hub reads it) ----------------------------
-- nil: not a depot; false: a depot row the hub treats as its default (a plain station's row);
-- a table: the hub's own entry shape {mode, percent} (40_TrainDistribution.lua's amount()).
-- The slider is the surface half's station target, read as at any hub station: on Import the surface
-- gathers up to it, on Export it hands out down to it. The underground half has no slider: where the
-- cabin loads (Export) it gathers to full, where the cabin delivers (Import) it hands out everything.
-- In the hub's own vocabulary a gathering half is an "import" station and a handing-out half an "export"
-- one. A lone half and Not accepted rows: false (the hub's default; Not accepted is vanilla-disabled).
function D.HubEntry(st, res)
	if not is_depot(st) then return nil end
	local flow = half_word(st, res)
	if flow ~= "gather" and flow ~= "hand_out" then return false end
	local mode = flow == "gather" and "import" or "export"
	if is_underground(st) then return { mode = mode, percent = mode == "import" and 100 or 0 } end
	return { mode = mode, percent = (D.Target(st, res)) }
end

-- ---- Drone Access (ruling 6): both halves, default off ---------------------------------------------
function Base:ShouldAddRequestToCommandCenter(request, command_center, res_id)
	if not IsKindOf(command_center, "DroneControl") then return true end   -- shuttles pass a map
	local res = storage_request(self, request)
	if not res then return true end            -- maintenance, train construction: vanilla service
	if not rawget(self, DRONES) then return false end
	local flow = half_word(self, res)
	if flow == "gather" then return request == self.demand[res] end     -- drones bring it in only
	if flow == "hand_out" then return request == self.supply[res] end   -- drones take it out only
	return true
end

function D.SetDroneAccess(o, on)
	if not live_depot(o) then return false, "not a live depot half" end
	on = on and true or false
	if (rawget(o, DRONES) and true or false) ~= on then
		rawset(o, DRONES, on or nil)
		reconnect(o)
	end
	trace(log_prefix, "drone access", is_underground(o) and "underground" or "surface", tostring(o.handle), on and "on" or "off")
	ObjModified(o)
	return true
end

-- Each half's own switch: drone hubs are per map. Ctrl+click is a plain click (one depot per map).
function Base:ToggleDroneAccess(broadcast)
	D.SetDroneAccess(self, not rawget(self, DRONES))
end

-- Vanilla's on/off look (owner, 2026-10-01: "at a glance its impossible to tell"): the filled
-- green/red hex is baked into the icon image, swapped per state, plus the rollover colour; that is
-- StorageDepot:ToggleLRTService_Update's shuttle_allowed/shuttle_forbidden pair (StorageDepot.lua:306-314,
-- archived build 25579348). The plain drone.png carries its own dark hex and cannot be filled, so the
-- drone glyph is vanilla's filled drone pair drone_balacing_on/off (UI.fpk IconsRemaster/IPButtons,
-- shipped and unreferenced by vanilla Lua on that build).
D.drone_icons = { on = "UI/IconsRemaster/IPButtons/drone_balacing_on.tga",
	off = "UI/IconsRemaster/IPButtons/drone_balacing_off.tga" }
function Base:ToggleDroneAccess_Update(button)
	local on = rawget(self, DRONES) and true or false
	button:SetIcon(on and D.drone_icons.on or D.drone_icons.off)
	button:SetRolloverImageColor(on and "green" or "red")
	button:SetRolloverText(Untranslated("Depots with forbidden Drone Access are never serviced by Drones from Drone Hubs. Trains and the cabin still move this half's cargo; maintenance stays vanilla.<newline><newline>Current status:<right><em>"
		.. (on and "ON" or "OFF") .. "</em>"))
end

local function find_window(win, id)
	if win.Id == id then return win end
	for _, child in ipairs(win) do
		local w = find_window(child, id)
		if w then return w end
	end
end

-- Beside Shuttle Access: created after the panel opens, then ordered by ZOrder (XWindow.lua:324, :722).
function D.AttachDroneButton(dlg)
	if not dlg or dlg.window_state == "destroying" or not IsKindOf(dlg, "ipBuilding") then return end
	local bld = ResolvePropObj(dlg.context)
	if not is_depot(bld) or bld.destroyed or find_window(dlg, "idSMRDepotDroneAccess") then return end
	local lrt = find_window(dlg, "ToggleLRTServiceButton")
	local button = InfopanelButton:new({
		Id = "idSMRDepotDroneAccess",
		RolloverTitle = Untranslated("Drone Access"),
		RolloverHint = Untranslated("<left_click> Toggle"),
		RolloverHintGamepad = Untranslated("<ButtonA> Toggle"),
		OnPressParam = "ToggleDroneAccess",
		OnPress = function(self, gamepad)
			self.context:ToggleDroneAccess()
			RebuildInfopanel(self.context)
		end,
		AltPress = true,
		OnAltPress = function(self, gamepad)
			if gamepad then
				self.context:ToggleDroneAccess()
				RebuildInfopanel(self.context)
			end
		end,
		Icon = D.drone_icons.off,
	}, lrt or dlg, dlg.context)
	if not button then print(log_prefix, "drone access button: no button row on this panel") return end
	local host = button.parent
	if lrt and lrt.parent == host then
		local after = false
		for _, child in ipairs(host) do
			if child == lrt then after = true
			elseif after and child ~= button then child:SetZOrder(3) end
		end
		button:SetZOrder(2)
	end
	if host.window_state == "open" and button.window_state ~= "open" then button:Open() end
	button:OnContextUpdate(button.context)
end

-- The hub's panel-scale floor, copied (45_TrainDistributionUI.lua:239-269, D.PanelScaleFloor and the
-- XSizeConstrainedWindow wrap in D.AttachStationRows): Data/XDef/Infopanel.lua's AdjustConstrainedScale is
-- a per-instance function; keep its snapping, then clamp a depot panel's scale so its slider rows lay out
-- as a hub station's (sitting C defect: a long title wrapped and doubled its row). Own marker, so a hub
-- wrap on the same window (inert for a depot, its network() is false) and this one chain.
D.PanelScaleFloor = 800
local function walk(win, fn)
	fn(win)
	for _, child in ipairs(win) do walk(child, fn) end
end
function OnMsg.DialogOpen(dlg)
	if IsKindOf(dlg, "ipBuilding") and is_depot(ResolvePropObj(dlg.context)) and D.InstallRowHook() then
		walk(dlg, function(win)
			if IsKindOf(win, "sectionStorageRow") then win:OnContextUpdate(win.context) end   -- rows built before the hook
			if IsKindOf(win, "XSizeConstrainedWindow") and not win.depot_scale then
				-- Guard the actual per-template instance member, not the unused base default.
				local previous = rawget(win, "AdjustConstrainedScale")
				if type(previous) ~= "function" then print(log_prefix, "Infopanel scale callback unavailable"); return end
				win.depot_scale = true
				win.AdjustConstrainedScale = function(self, x, y)
					x, y = previous(self, x, y)
					if is_depot(ResolvePropObj(dlg.context)) then
						return Max(x, D.PanelScaleFloor), Max(y, D.PanelScaleFloor)
					end
					return x, y
				end
				win:InvalidateMeasure()
			end
		end)
	end
	D.AttachDroneButton(dlg)
end

-- ---- one pair per colony (ruling 4) ---------------------------------------------------------------
-- Build-once per map: true once a live depot stands on the map in view, so vanilla greys the menu item
-- with its own "You can build this building only once." and closes placement after the first.
function Base:CanBuildOnlyOnce()
	local map = rawget(_G, "CurrentMap")
	local slot = map and map.slot
	for _, o in ipairs(all_depots()) do
		if o:GetMapSlot() == slot then return true end
	end
	return false
end

function OnMsg.GetAdditionalBuildingLocks(template, locks)
	if not template or (template.template_name ~= template_id and template.class ~= template_id
		and template.id ~= template_id) then return end
	local colony = rawget(_G, "UIColony")
	locks.smr_depot_needs_underground = not (colony and colony.underground_map_unlocked)
end

function D.HalfPlaced(o)
	D.InvalidatePair()
	D.InstallStationPanel()
	D.SyncCapacity()
	local same = 0
	for _, other in ipairs(all_depots()) do
		if other ~= o and other:GetMapSlot() == o:GetMapSlot() then same = same + 1 end
	end
	if same > 0 then
		trace(log_prefix, "pair limit: a further depot on the", environment_of(o), "map:", tostring(o.handle), "stays unpaired")
	end
end

-- ---- the cabin (rulings 1 and 5) --------------------------------------------------------------------
local function minutes(n) return MulDivRound(n, const.MinuteDuration, 1) end

local function cabin_of(surface)
	local rec = rawget(surface, CABIN)
	if type(rec) ~= "table" then
		rec = { phase = "at_top", ends = 0, cargo = {}, legs = 0 }
		rawset(surface, CABIN, rec)
	end
	rec.cargo = rec.cargo or {}
	return rec
end

local function aboard(rec)
	local n = 0
	for _, a in pairs(rec.cargo or empty_table) do n = n + a end
	return n
end

local function black_cube(o, n)
	local adjust = rawget(_G, "BlackCubeMystery_AdjustStored")
	if adjust and o.city then adjust(o.city, n) end
end

local function list_text(t)
	local parts = {}
	for _, res in ipairs(table.keys(t, true)) do parts[#parts + 1] = res .. "=" .. tostring(t[res]) end
	return #parts > 0 and table.concat(parts, ",") or "none"
end

-- Everything aboard that fits; what does not stays aboard and rides back to where it came from.
local function destination_room(dest, res)
	local d = dest.demand and dest.demand[res]
	local s = dest.supply and dest.supply[res]
	if not d or not s then return 0 end
	return Max(Min(d:GetTargetAmount(), dest:GetMaxStorage(res) - s:GetActualAmount()), 0)
end

local function deliver(rec, dest)
	local moved = {}
	for _, res in ipairs(table.keys(rec.cargo, true)) do
		local n = rec.cargo[res]
		local k = Min(n, destination_room(dest, res))
		if k > 0 then
			dest:AddResource(k, res)
			if res == "BlackCube" then black_cube(dest, k) end
			moved[res] = k
		end
		rec.cargo[res] = n - k > 0 and n - k or nil
	end
	return moved
end

-- Only the rows that send this way: Import on the down leg, Export on the up leg; capacity is shared.
local function load_cabin(rec, origin, dest, carried)
	local cap = Max(MulDivRound(D.CabinCapacity(origin), const.ResourceScale, 1) - aboard(rec), 0)
	local moved = {}
	local function take(res, want)
		local s, d = origin.supply and origin.supply[res], dest.demand and dest.demand[res]
		if cap <= 0 or not want or want <= 0 or not s or not d then return end
		local room = Max(destination_room(dest, res) - (rec.cargo[res] or 0), 0)
		local n = Min(Min(want, Max(s:GetTargetAmount(), 0)), Min(room, cap))
		if n <= 0 then return end
		origin:AddResource(-n, res)
		if res == "BlackCube" then black_cube(origin, -n) end
		rec.cargo[res] = (rec.cargo[res] or 0) + n
		moved[res] = (moved[res] or 0) + n
		cap = cap - n
	end
	-- Both directions serve the emptiest destination row first; carried leftovers and
	-- incoming reservations count as stock already promised there. Ties are stable by id.
	local list, stocked = {}, {}
	for _, res in ipairs(origin.storable_resources or empty_table) do
		if D.State(origin, res) == carried and destination_room(dest, res) > (rec.cargo[res] or 0) then
			list[#list + 1] = res
			stocked[res] = dest:GetMaxStorage(res) - destination_room(dest, res) + (rec.cargo[res] or 0)
		end
	end
	table.sort(list, function(a, b) return stocked[a] < stocked[b] or (stocked[a] == stocked[b] and a < b) end)
	for _, res in ipairs(list) do
		local s = origin.supply and origin.supply[res]
		if s and D.State(origin, res) == carried then take(res, s:GetTargetAmount()) end
	end
	-- nothing else: the cabin carries only what a row sends (no Balanced, owner 2026-10-01, sitting C)
	return moved
end

-- (No seeding: an unset row is Import. A vanilla refusal on a never-wired half is not kept; an earlier
-- build's explicit "disabled" still reads Not accepted.)

-- A pair forms or breaks. A surface half with a setting keeps it; a surface half with none (newly
-- placed) adopts the underground's copy; the underground then holds a copy of the result. Vanilla
-- follows, both halves re-register (Drone Access), the cabin art switches mode.
function D.OnPairChanged(surface, underground)
	D.SyncCapacity()
	if surface and underground then
		local s_rows, u_rows = rawget(surface, ROWS) or {}, rawget(underground, ROWS)
		rawset(surface, ROWS, s_rows)
		if not next(s_rows) and u_rows and next(u_rows) then
			s_rows = table.copy(u_rows)
			rawset(surface, ROWS, s_rows)
		end
		rawset(underground, ROWS, table.copy(s_rows))
		local s_t, u_t = rawget(surface, TARGETS), rawget(underground, TARGETS)
		if not (s_t and next(s_t)) and u_t and next(u_t) then rawset(surface, TARGETS, table.copy(u_t)) end
		if rawget(surface, TARGETS) then rawset(underground, TARGETS, table.copy(rawget(surface, TARGETS))) end
		trace(log_prefix, "pair formed: surface", tostring(surface.handle), "underground", tostring(underground.handle),
			"rows", list_text(s_rows))
	else
		trace(log_prefix, "no pair: surface", surface and tostring(surface.handle) or "none",
			"underground", underground and tostring(underground.handle) or "none")
	end
	for _, o in ipairs(all_depots()) do
		apply_all(o)
		if not connected[o] then reconnect(o) end
	end
	for _, rig in pairs(D.rigs) do
		if rig.bld then stop_cycle(rig); start_cycle(rig) end
	end
end

D.pair_key = false
function D.Tick(minute)
	local c = pair_now()
	local surface, underground = c.surface, c.underground
	local key = (surface and surface.handle or 0) .. ":" .. (underground and underground.handle or 0)
	if key ~= D.pair_key then
		D.pair_key = key
		D.OnPairChanged(surface, underground)
	end
	if not (surface and underground) then return end
	local rec, now, L = cabin_of(surface), GameTime(), D.layout
	if rec.phase == "down" or rec.phase == "up" then
		if now < (rec.ends or 0) then return end
		local leg = rec.phase
		local dest = leg == "down" and underground or surface
		local moved = deliver(rec, dest)
		rec.legs = (rec.legs or 0) + 1
		rec.phase = leg == "down" and "at_bottom" or "at_top"
		rec.ends = now + minutes(L.cabin_pause_minutes)
		trace(string.format("%s cabin arrived %s (leg %d) delivered %s still aboard %s",
			log_prefix, leg == "down" and "underground" or "surface", rec.legs, list_text(moved), list_text(rec.cargo)))
		ObjModified(surface)
		ObjModified(underground)
	end
	if now < (rec.ends or 0) then return end
	if not rec.started and minute ~= 0 then return end   -- the first leg leaves on the hour
	if not (surface.working and underground.working) then
		if not held[surface] then
			held[surface] = true
			trace(log_prefix, "cabin held: surface working", tostring(surface.working), "underground working", tostring(underground.working))
		end
		return
	end
	held[surface] = nil
	local going_down = rec.phase ~= "at_bottom"
	local origin, dest = going_down and surface or underground, going_down and underground or surface
	local moved = load_cabin(rec, origin, dest, going_down and "to_underground" or "to_surface")
	rec.started = true
	rec.phase = going_down and "down" or "up"
	rec.leg_ms = Max(minutes(L.cabin_leg_minutes), 1)
	rec.ends = now + rec.leg_ms
	trace(string.format("%s cabin departed %s (leg %d) loaded %s aboard %s arrives in %d min",
		log_prefix, going_down and "down" or "up", (rec.legs or 0) + 1, list_text(moved), list_text(rec.cargo),
		MulDivRound(rec.leg_ms, 1, const.MinuteDuration)))
	ObjModified(surface)
	ObjModified(underground)
end

function OnMsg.NewMinute(hour, minute) D.Tick(minute) end

function D.WiringLoad()
	D.pair_key, pair_cache = false, false
	gone = setmetatable({}, { __mode = "k" })
	held = setmetatable({}, { __mode = "k" })
	connected = setmetatable({}, { __mode = "k" })
	D.InstallStationPanel()
	D.SyncCapacity()
end

-- ---- a half demolished or destroyed (recommendation 2) ------------------------------------------
-- The cargo aboard goes to the surviving half (what does not fit becomes a stockpile beside it, as
-- MapSharedDepot:ReturnStockpiledResources does); the survivor keeps its stock and rows, works as a plain station
-- until a new twin is placed, and the new twin adopts its rows.
function D.HalfGone(o, done_map, why)
	if done_map or not is_depot(o) or gone[o] then return end
	if why == "done" and o.destroyed then gone[o] = true return end   -- handled when it was destroyed
	local ug = is_underground(o)
	local first_same, other
	for _, d in ipairs(all_depots()) do
		if d ~= o then
			if is_underground(d) == ug then first_same = first_same or d else other = other or d end
		end
	end
	if why == "done" then gone[o] = true end   -- a destroyed half is already out: Building.lua:1580, :1596
	pair_cache = false
	if not other or (first_same and first_same.handle < o.handle) then return end   -- o was not a paired half
	local surface = ug and other or o
	local rec = rawget(surface, CABIN)
	if type(rec) ~= "table" then return end
	local delivered, dropped = {}, {}
	if next(rec.cargo or empty_table) then
		delivered = deliver(rec, other)
		local place = rawget(_G, "PlaceResourceStockpile_Delayed")
		for _, res in ipairs(table.keys(rec.cargo, true)) do
			if place and other:IsValidPos() then
				place(other:GetVisualPos(), other:GetMap(), res, rec.cargo[res], other:GetAngle(), true, "tall_piles")
			end
			dropped[res] = rec.cargo[res]
		end
		rec.cargo = {}
	end
	rec.phase, rec.ends, rec.started = "at_top", 0, nil
	trace(log_prefix, "half gone:", ug and "underground" or "surface", tostring(o.handle), "survivor", tostring(other.handle),
		"cargo delivered", list_text(delivered), "stockpiled", list_text(dropped))
end

-- ---- the cabin art on the real legs ---------------------------------------------------------------
-- The surface cabin rests at its base and sinks on the down leg; the underground cabin waits up in the
-- ceiling and comes down to the receiver on the same leg; the up leg reverses both.
function D.FollowTarget(rig)
	local bld = rig.bld
	if not live_depot(bld) or not rig.base or not rig.far then return end
	local surface, underground = D.PairOf(bld)
	if not surface then return rig.base:z(), false end
	local ug = bld == underground
	local top_z = ug and rig.far:z() or rig.base:z()       -- the cabin is at the surface end
	local bottom_z = ug and rig.base:z() or rig.far:z()    -- the cabin is at the underground end
	local rec = rawget(surface, CABIN)
	if type(rec) ~= "table" then return top_z, false end
	if rec.phase == "down" or rec.phase == "up" then
		local leg = Max(rec.leg_ms or 1, 1)
		local done = leg - Clamp((rec.ends or 0) - GameTime(), 0, leg)
		local from = rec.phase == "down" and top_z or bottom_z
		local to = rec.phase == "down" and bottom_z or top_z
		return from + MulDivRound(to - from, done, leg), true
	end
	return rec.phase == "at_bottom" and bottom_z or top_z, false
end

function D.FollowLoop(rig)
	local was_moving
	while IsValid(rig.cabin) and IsValid(rig.elevator) do
		local z, moving = D.FollowTarget(rig)
		if not z then break end
		local L = D.layout
		local p = rig.cabin:GetPos()
		rig.cabin:SetPos(point(p:x(), p:y(), z), L.tick_ms)
		local hidden = rig.base and z < rig.base:z() + L.cabin_hide_below or false
		if hidden ~= (rig.cabin_hidden or false) then
			rig.cabin_hidden = hidden
			if hidden then
				PlayFX("ElevatorMoving", "end", rig.cabin)
				rig.cabin:ClearEnumFlags(const.efVisible)
			else
				rig.cabin:SetEnumFlags(const.efVisible)
				if moving then PlayFX("ElevatorMoving", "start", rig.cabin) end
			end
		end
		if moving ~= was_moving then
			was_moving = moving
			PlayFX("ElevatorMoving", moving and "start" or "end", rig.elevator)
			if not hidden then PlayFX("ElevatorMoving", moving and "start" or "end", rig.cabin) end
		end
		Sleep(L.tick_ms)
	end
	rig.thread = false
end

-- ---- reads ----------------------------------------------------------------------------------------
local function drone_reach(o)
	local mine = {}
	for _, res in ipairs(o.storable_resources or empty_table) do
		if o.supply and o.supply[res] then mine[o.supply[res]] = true end
		if o.demand and o.demand[res] then mine[o.demand[res]] = true end
	end
	local controllers, registered, busy = 0, 0, 0
	for _, cc in ipairs(o.command_centers or empty_table) do
		if IsKindOf(cc, "DroneControl") then
			controllers = controllers + 1
			for _, queues in ipairs{ cc.supply_queues or empty_table, cc.demand_queues or empty_table } do
				for _, by_res in pairs(queues) do
					for _, list in pairs(by_res) do
						for _, r in ipairs(list) do if mine[r] then registered = registered + 1 end end
					end
				end
			end
			for _, drone in ipairs(cc.drones or empty_table) do
				if mine[drone.d_request or false] or mine[drone.s_request or false] then busy = busy + 1 end
			end
		end
	end
	return controllers, registered, busy
end
D.DroneReach = drone_reach

-- The witness that replaces the mirror check (owner, 2026-10-01): what the underground panel shows for
-- a resource, against what the surface half's own row says. The shown mark is what vanilla's row draws
-- (sectionStorageRow.lua:16-24: the no-accept mark when vanilla storage is off, else GetResAcceptIcon);
-- the infotip must say the surface setting in words and send the player to the surface depot.
local mark_names = { [up] = "up", [down] = "down", [no_accept] = "off" }
local expected_marks = { to_surface = "up", to_underground = "down", disabled = "off" }
function D.UndergroundPanel(u, s, res)
	local said = normal_state(rawget(s, ROWS) and rawget(s, ROWS)[res])
	local shown = u:IsResourceEnabled(res) and (mark_names[Base.GetResAcceptIcon(u, res)] or "?") or "off"
	local tip = D.RowText(u, res)
	local tip_ok = tip:find(underground_says[said], 1, true) and tip:find("use the surface Elevator Depot", 1, true) and true or false
	local copy = normal_state((rawget(u, ROWS) or empty_table)[res])
	-- the title word the underground row draws (D.RowWord) must be the surface's word, unchanged
	local title_word = D.RowWord(u, res)
	local title_ok = title_word == word_of(said)
	return shown, expected_marks[said], tip_ok, copy == said, said, title_ok, title_word
end

function D.Pair()
	local c = pair_now()
	local s, u = c.surface, c.underground
	local rec = s and u and rawget(s, CABIN)
	local L = D.layout
	local out = { surface = s and s.handle or false, underground = u and u.handle or false, extras = c.extras }
	print(string.format("%s pair surface=%s underground=%s extras=%d cabin=%s legs=%d ends_in_min=%d aboard=%s capacity=%s leg_min=%s pause_min=%s words=%s follows=%s",
		log_prefix, s and tostring(s.handle) or "none", u and tostring(u.handle) or "none", c.extras,
		type(rec) == "table" and tostring(rec.phase) or "none", type(rec) == "table" and (rec.legs or 0) or 0,
		type(rec) == "table" and MulDivRound(Max((rec.ends or 0) - GameTime(), 0), 1, const.MinuteDuration) or 0,
		type(rec) == "table" and list_text(rec.cargo or empty_table) or "none", tostring(D.CabinCapacity(s or u)),
		tostring(L.cabin_leg_minutes), tostring(L.cabin_pause_minutes), tostring(L.row_words), tostring(L.cabin_follows_schedule)))
	out.cabin = type(rec) == "table" and rec.phase or false
	out.legs = type(rec) == "table" and (rec.legs or 0) or 0
	out.capacity = D.CabinCapacity(s or u)
	for _, o in ipairs(all_depots()) do
		local ctrl, reg, busy = drone_reach(o)
		local twin = D.TwinOf(o)
		print(string.format("%s   half %s %s working=%s drone_access=%s controllers=%d registered=%d drones_busy=%d twin=%s rows=%s",
			log_prefix, environment_of(o), tostring(o.handle), tostring(o.working), rawget(o, DRONES) and "on" or "off",
			ctrl, reg, busy, twin and tostring(twin.handle) or "none", is_underground(o) and "read-only" or "set here"))
		out[o.handle] = { registered = reg, busy = busy, drones = rawget(o, DRONES) and true or false }
	end
	local half = s or u
	local match, differ, stale = 0, 0, 0
	for _, res in ipairs(half and half.storable_resources or empty_table) do
		local function stock(o)
			return o and o.supply and o.supply[res] and o.supply[res]:GetActualAmount() or -1
		end
		local function flag(o)
			if not o then return "-" end
			return (o:IsResourceEnabled(res) and "on" or "OFF") .. "/" .. tostring((o.transport_policy or empty_table)[res] or "default")
		end
		local panel = "-"
		if s and u and has_rows(u, res) then
			local shown, expected, tip_ok, copy_ok, _, title_ok, title_word = D.UndergroundPanel(u, s, res)
			local ok = shown == expected and tip_ok and title_ok
			if ok then match = match + 1 else differ = differ + 1 end
			if not copy_ok then stale = stale + 1 end
			panel = string.format("%s,%s(surface says %s)%s%s%s", shown, word_titles[title_word], expected,
				tip_ok and "" or " TIP-WRONG", title_ok and "" or " TITLE-WRONG", ok and "" or " DIFFERENT")
		end
		local target, set = D.Target(half, res)
		print(string.format("%s   row %-12s state=%-14s surface=%-8s underground=%-8s target=%d%%%s u_panel=%s stock_s=%d stock_u=%d vanilla_s=%s vanilla_u=%s",
			log_prefix, res, D.State(half, res), s and half_word(s, res) or "-", u and half_word(u, res) or "-",
			target, set and "" or "(dial)", panel, stock(s), stock(u), flag(s), flag(u)))
	end
	if s and u then
		out.underground_panel = differ == 0 and "matches" or "DIFFERENT"
		out.copy = stale == 0 and "current" or "STALE"
		print(string.format("%s underground panel: %d rows match the surface setting, %d differ; read-only copy %s",
			log_prefix, match, differ, out.copy))
	end
	return out
end
