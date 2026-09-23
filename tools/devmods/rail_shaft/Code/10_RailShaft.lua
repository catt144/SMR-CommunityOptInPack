-- Rail shaft: a cross-map train tunnel, as a throwaway prototype.
--
-- DEV ONLY. Nothing here ships, nothing enters Code/, there is no module
-- record. Use it on a throwaway save only: it writes into vanilla's own
-- DisabledInEnvironment GameVar and it re-links finished buildings by hand.
--
-- Every source line cited below was read on the INSTALLED build,
-- 25390750 / 1.1.1.405907, from that build's archived tree
-- (B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src). The brief this was
-- built from cited 1.1.0.403908 / build 24995074, which the rig no longer has;
-- every claim was re-derived rather than carried over.
--
-- UNVERIFIED IN GAME. Not one line below has been run. The sitting that would
-- run it is docs/agent/reports/RAIL_SHAFT_PROTOTYPE.md.
--
--
-- THE MECHANISM, and why the prototype has the shape it does.
--
-- A train tunnel hop is TrackTunnelBase:TrainTraverse (Buildings/TrackTunnel.lua
-- :40-80). It drives the train into one mouth, SetPos-teleports it to the linked
-- mouth (:70) and drives it out. SetPos does not change a unit's map, so the
-- stock hop is single-map by construction. It runs inside the train's own
-- GotoStation command thread: Train:GotoStation (Units/Train.lua:338-414) calls
-- next_station:TrainPassThrough (:407), which calls TrainTraverse
-- (TrainTransport.lua:43-51).
--
-- ROUTING ALREADY CROSSES MAPS. EnumRouteTracks follows next_struct.linked_obj
-- with no map check (TrainTransport.lua:264-269), and so does GetArrivalTrack
-- (:239-241). RebuildTrainRoutes (:302-358) walks every city and keys the route
-- by every track segment in it (:331), so a route that crosses maps lands in
-- BOTH cities' train_track_routes -- the outbound lookup and the return lookup
-- each find it. This is why the prototype does not touch routing at all.
--
-- THE CROSSING ITSELF is object:TransferToMap(map, pos), a C function
-- (CommonLua/LuaExportedDocs/Game/GameObject.lua:1529). Two shipped callers:
--   * PFTunnel:TraverseTunnel (CommonLua/Movable.lua:622-629) -- the two-argument
--     form, map and position.
--   * ElevatorBase:UseElevator (Buildings/Elevator.lua:961-1002) -- the ONE
--     argument form, unit:TransferToMap(self.other) at :982, followed by
--     SetHolder and Disembark to place the unit.
-- The stock rover tunnel never crosses maps at all: TunnelBase:TraverseTunnel
-- (Buildings/Tunnel.lua:211-258) overrides the PFTunnel one and uses
-- DetachFromMap/SetHolder/ExitBuilding instead.
--
-- WHAT THE TRANSFER DOES TO A UNIT. Unit:OnTransferToMap (Units/Unit.lua
-- :942-945) drops the selection arrow and calls ClearCommandQueue, which nils
-- the QUEUE only (CommandObject.lua:577-579) -- it does not by itself end the
-- running command. CityObject:OnTransferToMapDone (CityObject.lua:73-80)
-- reassigns self.city and re-adds the labels, which is why the console probe on
-- 2026-09-21 saw a train's city bookkeeping follow it across.
--
-- WHY THE BODY IS IN A DESTRUCTOR. Both shipped crossings -- the elevator's and
-- the rover tunnel's -- wrap their ENTIRE body in PushDestructor /
-- PopAndCallDestructor, and both Sleep inside it. A destructor is what the
-- engine runs when a command is interrupted (CommandObject.lua:406-462), and
-- while one is running, thread_running_destructors keeps it counting as the
-- command thread (:400-404, :448-453). The 2026-09-21 console hop ran the
-- transfer OUTSIDE a destructor and the train never moved again. So the open
-- question -- does the command thread survive a transfer? -- is exactly what the
-- stage log below is for: if the hop stops, the last stage line names where.
--
-- WHAT A CROSS-MAP PAIR MUST NOT DO. TunnelBase:GameInit (Tunnel.lua:77-90)
-- wires three single-map registries, and all three are wrong across maps:
--   * RegPoints -> g_TunnelsAdjacency, a table keyed on hex (q,r) with NO map in
--     the key (:50-66). Two mouths at the same hex on two maps collide.
--   * Notify(self, "AddPFTunnel") -> pf.AddTunnel (:193-205), a single-map
--     rover path.
--   * MergeGrids("electricity"/"water") (:160-172), a single-map grid merge.
-- The prototype unwires the first two when it links a pair, and guards the
-- entry points so a reload cannot re-wire them (OnMsg.LoadGame re-runs
-- AddPFTunnel over every TunnelBase, Tunnel.lua:260-262).
--
-- WHY THE OWNER BUILDS NORMAL TUNNELS AND WE RE-LINK. Tunnel construction is
-- single-map by design: TunnelConstructionController:Activate makes ONE
-- construction group on ONE map for both mouths (Construction/TunnelConstruction
-- .lua:254-275). Rewriting that is a real module's job, not a prototype's. The
-- pairing itself, though, is map-agnostic already -- TunnelBase:Init pairs
-- through the global g_LastPlacedTunnel with no map check (:23-31). So the
-- cheapest honest prototype is: let the owner build two ordinary pairs, one per
-- map, through the ordinary UI, then cross-link one mouth from each and dispose
-- of the two orphans. Every object involved is a real, track-connected,
-- retail-built TrackTunnelBase.
--
-- FIX_POLICY notes for a real module, recorded here because this is where they
-- were learned:
--   * DisabledInEnvironment is a GameVar (Buildings/Building.lua:41) -- it is
--     SAVED. Writing it leaves the underground-allowed flag in the save after
--     the mod is gone. A real module should override the prerequisite check
--     instead of writing the table.
--   * UndisableInEnvironment (:94-98) is a NO-OP while DisabledInEnvironment[id]
--     is nil; the lazy fill only happens in DisableInEnvironment and
--     IsBuildingAllowedIn (:89-92, :100-104). Read first, then undisable.
--   * No SMRFixPack_* field and no new persisted name is introduced here. The
--     only state this file keeps between calls is in a plain global table that
--     is never saved.

if rawget(_G, "SMRRailShaft") then return end

SMRRailShaft = {
	listing = false,   -- runtime only: the last List() result, for Link(i, j)
	trains  = false,   -- runtime only: the last Sweep() result, for Kill(i)
}

local RS = SMRRailShaft

local function log(fmt, ...)
	local ok, msg = pcall(string.format, "[RailShaftDev] " .. tostring(fmt), ...)
	print(ok and msg or ("[RailShaftDev] " .. tostring(fmt)))
end
RS.log = log

-- ---------------------------------------------------------------------------
-- identity

function RS.MapName(obj)
	if not obj then return "?" end
	local map = ResolveMap(obj)
	if not map then return "?" end
	if UndergroundMap and map == UndergroundMap then return "underground" end
	if MainMap and map == MainMap then return "surface" end
	return tostring(map)
end

-- A rail shaft is exactly a TunnelBase pair whose two mouths are on two maps.
-- Nothing is stored to mark one: the condition IS the marker, so it survives a
-- save/load without this mod persisting anything.
function RS.IsCrossMap(tunnel)
	local other = tunnel and tunnel.linked_obj
	if not IsValid(tunnel) or not IsValid(other) then return false end
	return not IsSameMap(tunnel, other)
end
local IsCrossMap = RS.IsCrossMap

-- ---------------------------------------------------------------------------
-- 1. let a Universal Tunnel be built underground
--
-- UniversalTunnel's template carries no disabled_in_environment of its own
-- (Data/BuildingTemplate/UniversalTunnel.lua), so it inherits the property
-- default, set("Underground", "Asteroid") (Buildings/Building.lua:253).

function RS.AllowUnderground(on)
	if not UIColony then
		log("no UIColony yet; load a save first.")
		return false
	end
	if not UIColony.underground_map_unlocked then
		log("REFUSED: UIColony.underground_map_unlocked is false. The gate is one-way and")
		log("  belongs to the player -- Colony:UnlockUnderground (Colony.lua:654-660) sets it")
		log("  when a surface elevator completes (:949). Build one. Nothing was changed.")
		return false
	end

	on = on ~= false
	-- read first: UndisableInEnvironment does nothing while the key is nil
	IsBuildingAllowedIn("UniversalTunnel", "Underground")
	if on then
		UndisableInEnvironment("UniversalTunnel", "Underground")
	else
		DisableInEnvironment("UniversalTunnel", "Underground")
	end

	log("UniversalTunnel allowed underground = %s (DisabledInEnvironment is a GameVar: this is",
		tostring(IsBuildingAllowedIn("UniversalTunnel", "Underground")))
	log("  written into the save, and stays there if this mod is removed -- throwaway saves only)")
	return true
end

function OnMsg.LoadGame()
	if UIColony and UIColony.underground_map_unlocked then
		RS.AllowUnderground(true)
	else
		log("loaded; underground is locked in this save, so the tunnel stays surface-only.")
	end
	log("ready. SMRRailShaft.Status() for where things stand.")
end

-- ---------------------------------------------------------------------------
-- 2. keep the single-map registries off a cross-map pair

local Orig_AddPFTunnel = TunnelBase.AddPFTunnel
function TunnelBase:AddPFTunnel()
	if IsCrossMap(self) then
		log("AddPFTunnel skipped for rail-shaft mouth %s: pf.AddTunnel is single-map (Tunnel.lua:193-205)",
			tostring(self.handle))
		return
	end
	return Orig_AddPFTunnel(self)
end

local Orig_MergeGrids = TunnelBase.MergeGrids
function TunnelBase:MergeGrids(type_of_grid)
	if IsCrossMap(self) then
		return  -- a cross-map electricity/water merge is meaningless (Tunnel.lua:160-172)
	end
	return Orig_MergeGrids(self, type_of_grid)
end

-- ---------------------------------------------------------------------------
-- 3. listing and linking

function RS.List()
	local list = {}
	AllMapsForEach("map", "TrackTunnelBase", function(t)
		if IsValid(t) then list[#list + 1] = t end
	end)
	table.sort(list, function(a, b)
		local ma, mb = RS.MapName(a), RS.MapName(b)
		if ma ~= mb then return ma < mb end
		return (a.handle or 0) < (b.handle or 0)
	end)
	RS.listing = list

	log("%d track tunnel mouth(s):", #list)
	for i, t in ipairs(list) do
		local other = t.linked_obj
		log("  [%d] handle %s  %s  pos %s  %s  linked -> %s%s",
			i, tostring(t.handle), RS.MapName(t), tostring(t:GetPos()), t.class,
			IsValid(other) and (tostring(other.handle) .. " on " .. RS.MapName(other)) or "NOTHING",
			IsCrossMap(t) and "   <== RAIL SHAFT" or "")
	end
	if #list == 0 then
		log("  none. Build a Universal Tunnel pair on each map first.")
	end
	return #list
end

-- Undo what GameInit wired for this mouth's CURRENT pair, on both maps, while
-- the pairing is still intact (RegPoints reads self.linked_obj.registered_point).
local function UnwirePair(t)
	if not IsValid(t) then return end
	local other = t.linked_obj
	pcall(t.RegPoints, t, true)              -- drop the hex adjacency for the pair
	pcall(t.RemovePFTunnel, t)
	if IsValid(other) then pcall(other.RemovePFTunnel, other) end
	-- registered_point and the tunnel mask are left alone on purpose: they are
	-- per-map and harmless, and TunnelBase:Done (Tunnel.lua:92-105) reads
	-- registered_point without a nil guard.
end

function RS.Link(i, j)
	local list = RS.listing
	if not list then
		log("run SMRRailShaft.List() first")
		return false
	end
	local a, b = list[i], list[j]
	if not IsValid(a) or not IsValid(b) then
		log("no mouth at [%s] / [%s]; re-run SMRRailShaft.List()", tostring(i), tostring(j))
		return false
	end
	if a == b then
		log("those are the same mouth")
		return false
	end
	if IsSameMap(a, b) then
		log("[%d] and [%d] are both on %s. A rail shaft needs one mouth on each map.",
			i, j, RS.MapName(a))
		return false
	end

	local oa, ob = a.linked_obj, b.linked_obj
	log("linking %s (%s) <-> %s (%s)", tostring(a.handle), RS.MapName(a),
		tostring(b.handle), RS.MapName(b))

	UnwirePair(a)
	UnwirePair(b)

	-- Break the old pairings in BOTH directions before disposing the orphans:
	-- TunnelBase:Done kills its linked_obj (Tunnel.lua:99-104), and we do not
	-- want an orphan taking the new partner down with it.
	if IsValid(oa) then oa.linked_obj = false end
	if IsValid(ob) then ob.linked_obj = false end
	a.linked_obj = false
	b.linked_obj = false

	if IsValid(oa) and oa ~= b then
		log("  disposing orphan mouth %s on %s", tostring(oa.handle), RS.MapName(oa))
		DoneObject(oa)
	end
	if IsValid(ob) and ob ~= a then
		log("  disposing orphan mouth %s on %s", tostring(ob.handle), RS.MapName(ob))
		DoneObject(ob)
	end

	a.linked_obj = b
	b.linked_obj = a

	log("  linked. Electricity/water grids are NOT un-merged -- whatever the old")
	log("  pairs merged stays merged; that is cosmetic for this test.")

	RebuildTrainRoutes()
	log("  RebuildTrainRoutes() done. Now connect track to both mouths and give a")
	log("  train a stop on each map. SMRRailShaft.Status() to check.")
	return true
end

-- ---------------------------------------------------------------------------
-- 4. the cross-map hop

local function Stage(train, n, what)
	log("hop train %s | stage %d %s | map %s pos %s | cmd %s | station %s",
		tostring(train.handle), n, what, RS.MapName(train), tostring(train:GetPos()),
		tostring(train.command), tostring(train.current_station and train.current_station.handle))
end

function RS.CrossMapTraverse(tunnel, train, arrival_track, departure_track)
	local other = tunnel.linked_obj
	if not IsValid(other) then
		log("hop aborted: mouth %s has no valid partner", tostring(tunnel.handle))
		return
	end

	local near_el = tunnel:GetInnerTrackElement()
	local far_el = other:GetInnerTrackElement()
	local far_connector = other:GetConnectorElement(0)
	if not near_el or not far_el or not far_connector then
		log("hop aborted: missing track element (near %s / far %s / far connector %s). Track is",
			tostring(near_el), tostring(far_el), tostring(far_connector))
		log("  probably not connected to one of the two mouths.")
		return
	end

	local far_map = ResolveMap(other)
	local move_speed = train.move_speed

	-- The whole crossing sits in a destructor, the shape both shipped crossings
	-- use (Elevator.lua:966-1001, Tunnel.lua:215-256). See the header.
	train:PushDestructor(function(train)
		if not IsValid(train) then return end
		Stage(train, 1, "enter")

		train:SetState("moveWalk", 0, 0)
		train:SetMoveSpeed(move_speed)

		-- drive into the near mouth, exactly as TrackTunnel.lua:47-58 does
		local step = (train:GetDepartedStation() == arrival_track:GetStartStation()) and 1 or -1
		local near_pos = near_el:GetSpotPos(near_el:GetSpotBeginIndex("Enter" .. ((step == 1) and "1" or "2")))
		local move_time = pf.GetMoveTime(train, train:GetDist(near_pos))
		train:SetPos(near_pos, move_time)
		Sleep(move_time)
		if not IsValid(train) then return end
		Stage(train, 2, "at-near-mouth")

		-- work out where on the far map the train is going (TrackTunnel.lua:66-71)
		local far_step = (other == departure_track:GetStartStation()) and 1 or -1
		local far_spot = "Enter" .. ((far_step == 1) and "1" or "2")
		local far_pos = far_el:GetSpotPos(far_el:GetSpotBeginIndex(far_spot))
		local connector_pos = far_connector:GetSpotPos(far_connector:GetSpotBeginIndex(far_spot))
		Stage(train, 3, "pre-transfer")
		log("hop train %s | far map %s | far_pos %s | connector_pos %s",
			tostring(train.handle), RS.MapName(other), tostring(far_pos), tostring(connector_pos))

		-- The elevator drops selection and the camera before it transfers
		-- (Elevator.lua:976-981). The 2026-09-21 probe left a train that could
		-- not be selected afterwards, so do the same here.
		if IsInSelection(train) then SelectionRemove(train) end
		if CameraFollowObj == train then UnfollowObjAndCloseModeDialog() end

		-- vanilla SetPos-teleports here (TrackTunnel.lua:70); the map has to
		-- change instead. Two-argument form, as PFTunnel uses (Movable.lua:626).
		train:TransferToMap(far_map, far_pos)
		if not IsValid(train) then
			log("hop train: gone after TransferToMap")
			return
		end
		Stage(train, 4, "post-transfer")

		train:SetPos(far_pos)
		train:Face(connector_pos)
		Stage(train, 5, "at-far-mouth")

		move_time = pf.GetMoveTime(train, train:GetDist(connector_pos))
		train:SetPos(connector_pos, move_time)
		Sleep(move_time)
		if not IsValid(train) then return end
		Stage(train, 6, "at-far-connector")

		train.current_station = other
		table.remove_value(arrival_track.assigned_vehicles, train)
		Stage(train, 7, "done")
	end)
	train:PopAndCallDestructor()
end

local Orig_TrainTraverse = TrackTunnelBase.TrainTraverse
function TrackTunnelBase:TrainTraverse(train, arrival_track, departure_track)
	if not IsCrossMap(self) then
		return Orig_TrainTraverse(self, train, arrival_track, departure_track)
	end
	return RS.CrossMapTraverse(self, train, arrival_track, departure_track)
end

-- ---------------------------------------------------------------------------
-- 5. finding and removing a stranded train

function RS.Sweep()
	local found = {}
	for _, city in ipairs(Cities or empty_table) do
		for _, train in ipairs((city.labels and city.labels.Train) or empty_table) do
			if IsValid(train) then found[#found + 1] = train end
		end
	end
	RS.trains = found

	log("%d train(s):", #found)
	for i, t in ipairs(found) do
		log("  [%d] handle %s  %s  pos %s  cmd %s  station %s  track %s",
			i, tostring(t.handle), RS.MapName(t), tostring(t:GetPos()), tostring(t.command),
			tostring(t.current_station and t.current_station.handle),
			tostring(t.track and t.track.handle))
	end
	return #found
end

function RS.Kill(i)
	local t = RS.trains and RS.trains[i]
	if not IsValid(t) then
		log("no train at [%s]; run SMRRailShaft.Sweep() first", tostring(i))
		return false
	end
	log("removing train %s on %s -- this is the stranded-train escape hatch",
		tostring(t.handle), RS.MapName(t))
	DoneObject(t)
	RS.trains = false
	return true
end

-- ---------------------------------------------------------------------------
-- 6. where things stand

function RS.Status()
	log("--- rail shaft status ---")
	log("underground unlocked: %s", tostring(UIColony and UIColony.underground_map_unlocked))
	log("UniversalTunnel allowed underground: %s",
		tostring(IsBuildingAllowedIn("UniversalTunnel", "Underground")))

	local shafts = 0
	AllMapsForEach("map", "TrackTunnelBase", function(t)
		if IsCrossMap(t) then shafts = shafts + 1 end
	end)
	log("cross-map mouths: %d (a linked shaft is 2)", shafts)

	local trains = 0
	for _, city in ipairs(Cities or empty_table) do
		trains = trains + #((city.labels and city.labels.Train) or empty_table)
	end
	log("trains: %d", trains)
	log("List() / Link(i,j) / Sweep() / Kill(i) / AllowUnderground(true|false)")
	return shafts
end

print("[RailShaftDev] loaded: cross-map train tunnel prototype. UNVERIFIED IN GAME.")
