-- Drones chain L2E: console-only Wasp flight prototype, two implementations behind one switch.
-- Owner OI-25 (2026-09-22) and L2R's under-deck route stand. No dispatch, resources, task
-- requests, class additions, class wraps or persisted mod fields.
--
-- MODE "engine" (owner redirect, 2026-09-23: "besides our launch and return parts the engine
-- handles that pathing and we handle the commands"; installed build 25390750, 1.1.1.405907):
--  * Ours, scripted as below: the pit rise through OI-25's column to the crest hold, the work
--    pose at the break, and the pit descent. HandoffAt="outside" also keeps L2R's under-deck
--    exit to the outside point, for a hub the engine's own path cannot leave cleanly.
--  * The engine's: every leg between them, under the STOCK command FlightGoto(xy)
--    (Flight.lua:1182; the C++ Flight component paths it over the flight surface at the
--    class-static hover_height, 7 m, Flight.lua:175). Only stock method names are ever written
--    onto the drone: "FlightGoto", "WaitUninterruptable" and false.
--  * The handoff race: a finished command falls into Idle in the same thread with no yield
--    (CommandObject.lua CommandThreadProc), and Idle lands, greys, seeks tasks and self-issues
--    GoHome. So every leg queues the stock hold WaitUninterruptable(HoldTimeout) behind it
--    (CommandObject.lua:359 QueueCommand; :168 ExecuteUninterruptable(WaitMsg)): the drone
--    holds itself at the arrival until our driver, polling every PollTime, ends the hold with
--    InterruptWait() and SetCommand(false). Vanilla's Idle can only follow the hold's timeout,
--    which is also what a save loaded without the mod does: the drone becomes a plain Wasp.
--  * Save: a drone under a stock command or hold has no mod thread and stays in the save
--    untouched (DESIGN.md:55-56); only scripted motion is removed at SaveGameStart. The driver
--    is deleted for the save and restarted at SaveGameDone.
--  * Load (drones chain L4, 2026-09-23): a Wasp that rode the save under a stock leg or hold is
--    taken back into a record by F.Adopt at the stage the hub's persisted deadline names ("out"
--    or "back"); the hub calls it on its first tick after load and then sweeps what nobody
--    adopted (20_TrainHub.lua). This file no longer sweeps at LoadGame; F.SweepLoaded remains
--    for the console prototype and skips any Wasp a registered record holds.
-- MODE "scripted": the tagged drones-scripted-flight-20260923 flight, unchanged below.
--
-- HOW SCRIPTED MOTION MOVES (installed build 24995074, archived 1.1.0.403908), the way the game's own units do:
--  * The route is scripted: pit column, under-deck duck, outside climb, over-track centreline.
--  * Corners are rounded (quadratic Bezier inside the corner's own legs) and the speed is a
--    physical profile: Accel bounds speed-up, braking and cornering; Speed and ClimbRate cap it.
--  * The ENGINE renders every chord: one timed drone:SetPos(dest, ms) + SetAcceleration(a) per
--    chord, chained end to end from a GAME-time thread, exactly the shipped shape of
--    Train.lua:512-513, :549-550, :585-586 and FlyingDrone.lua:194-201 (Land). No position is
--    written per frame; a chord lasts at most ChordTime (333 ms, the Wasp's max_sleep,
--    Flight.lua:806). Heading and bank ride on timed SetRollPitchYaw per chord (Train.lua:495).
--  * A landing decelerates to rest at the pose and only THEN changes state, as Land() sleeps its
--    move time before LandingEnd() (FlyingDrone.lua:198-201).
--  * Not used: FlightGoto/Flight_Step (hover_height and every move param are class-static and
--    "per-instance overrides are ignored by design", Flight.lua:149-160; the solver flies its own
--    spline over the terrain/obstacle height cache and cannot ride a rail or duck a deck) and
--    ComponentCurvature (no shipped Lua caller; its arc cannot be measured). SetCurvature(false)
--    keeps every chord a straight line, which the clearance receipt depends on.
--
-- SAVE POLICY (FIX_POLICY §3a, layer 1): the driver is a mod-owned GAME-time thread with no
-- upvalues; its orphan gate is the first statement after its only yield. OnMsg.SaveGameStart
-- deletes it and every scripted-motion visual before the persist walk and gates spawns until
-- SaveGameDone; engine-mode drones under a stock command or hold stay (see MODE "engine").
-- L4 owns persisted deadlines and reconstruction (F.Adopt is its way back in after a load).
-- Source surfaces: Unit.lua:42-51 (init_with_command=false), FlyingDrone.lua:114-132
-- (TakeOff/LandingEnd), Track.lua:194-199, TrainTransport.lua:57-65, TrackTunnel.lua:20-28;
-- EF-112/115 (FX and battery).

if SMROptInHubFlight and SMROptInHubFlight.ClearAll then SMROptInHubFlight.ClearAll() end
SMROptInHubFlight = {
  HoverHeight = 300,        -- GUESS safety buffer above the guessed train envelope
  OverTrackHeight = 1200,   -- GUESS train envelope above rail; total ride offset = this + buffer
  FixHeight = 100,          -- GUESS work origin above the target element, not cruise altitude
  UnderDeckHeight = 300,    -- entity-local z; native-scale mesh measured by exit_clearance.py
  OutwardDistance = 9000,   -- radius from hub origin before climbing, beyond arms/platforms
  TransferHeight = 2500,    -- entity-local z for crossing back above the hub after outside climb
  ExitDirectionX = -998, ExitDirectionY = -70, -- /1000; 184 deg, the measured pallet gap (L3)
                            -- Box1 spots sit on r=2492 at 40.7+60n deg, so gaps centre on 10.7+60n;
                            -- from the pit at (-1310,-397) 184 deg clears pallet 0 by 1.21 m, pallet 1 by 1.25 m
  Speed = 16000,            -- units per game second, level cruise cap; the Wasp's own move_speed (16*guim)
  ClimbRate = 8000,         -- units per game second, vertical cap; flown and accepted (L3)
  Accel = 8000,             -- units per game second^2: speed-up, braking and cornering limit; flown and accepted (L3)
  TurnRadius = 1500,        -- units: most a corner is rounded before and after its waypoint; GUESS
  BankAngle = 900,          -- angle minutes of roll in a full-rate turn; 0 disables, negative leans the other way; GUESS
  WorkTime = 5000,          -- game ms in constructIdle, excludes start/end animations
  PitOffsetX = -310, PitOffsetY = 180, PitExitZ = 1000, -- OI-25, entity local
  BatteryMax = 800000,
  Palette = false,          -- optional array of four colours, L3 visual verdict
  ChordTime = 333,          -- game ms, longest engine move (Wasp max_sleep); not an owner dial
  ChordAngle = 600,         -- angle minutes of turn per chord on a curve; not an owner dial
  ChordMinTime = 50,        -- game ms, shortest chord worth issuing; not an owner dial
  YawRate = 9000,           -- angle minutes per second; the Wasp's own max_yaw_speed is preferred
  Mode = "engine",          -- "engine": stock FlightGoto legs between our ends; "scripted": the tagged flight
  HandoffAt = "outside",    -- "outside": after L2R's under-deck exit; "crest" (the OI-25 hold) crosses the dome shell (L3, 2026-09-23)
  HoldTimeout = 60000,      -- game ms a stock WaitUninterruptable hold lasts before vanilla Idle; the driver re-arms at half
  PollTime = 250,           -- game ms between driver looks at an engine leg or hold; not an owner dial
  Lost = false,             -- diagnostics: the foreign command that last took a prototype drone away
}

local F = SMROptInHubFlight
local active, save_gate, driver = false, false, false
local visuals = {}
-- The only command names this file ever writes onto a drone. Both are shipped engine methods
-- (Flight.lua FlyingObject:FlightGoto; CommonLua CommandObject:WaitUninterruptable).
local STOCK_LEG, STOCK_HOLD = "FlightGoto", "WaitUninterruptable"

-- NUMBERS. This engine's Lua divides an integer by an integer as integers: shipped code writes
-- `party_size * 1.0 / remaining_seats`, `trip_time + 0.0` and DivAsFloats() before dividing
-- (Factions.lua:180, TransportStatistics.lua:56, Legislature.lua:1344), and Min/Max/Clamp are
-- its INTEGER helpers (LuaSharedLib docs). A standard-Lua mock cannot show this, so the rule
-- here is mechanical: every fractional division goes through div(), min/max/clamp are the
-- standard library's, and every number handed to the engine goes through int(). The smoke
-- refuses a bare `/` and a Min/Max/Clamp call in this file.
local function div(a, b) return (a * 1.0) / b end
local tointeger = math.tointeger or function(v) return v end
local function int(x)
  local v = math.floor(x + .5)
  if v ~= v or v == math.huge or v == -math.huge then return 0 end
  return tointeger(v) or 0
end
local min, max = math.min, math.max
local function clamp(v, lo, hi) return v < lo and lo or (v > hi and hi or v) end

local function live(o)
  return IsValid(o) and not o.destroyed and not IsBeingDestructed(o)
end

local function hub_ok(h)
  return live(h) and h:GetEntity() == "SMROptInTrainHub6" and h.city
end

local function elevated(o)
  local p = o:GetVisualPos()
  if not p or p:z() == nil then return nil end
  return p + point(0, 0, F.OverTrackHeight + F.HoverHeight)
end

function F.PitPoints(hub)
  if not hub_ok(hub) then return nil, "Select a built train hub" end
  local floor_idx, rim_idx = hub:GetSpotBeginIndex("Pitfloor"), hub:GetSpotBeginIndex("Pitrim")
  if floor_idx < 0 or rim_idx < 0 then return nil, "Pit spots missing; reimport the hub" end
  -- Transform a local vector and add it to the LIVE spot, preserving angle and scale.
  local delta = hub:GetRelativePoint(point(F.PitOffsetX, F.PitOffsetY, 0))
    - hub:GetRelativePoint(point(0, 0, 0))
  local floor = hub:GetSpotPos(floor_idx) + delta
  local rim = hub:GetSpotPos(rim_idx) + delta
  local local_rim = GetEntitySpotPos(hub:GetEntity(), rim_idx)
  local exit = hub:GetRelativePoint(point(local_rim:x() + F.PitOffsetX,
    local_rim:y() + F.PitOffsetY, F.PitExitZ))
  local cruise = hub:GetRelativePoint(point(local_rim:x() + F.PitOffsetX,
    local_rim:y() + F.PitOffsetY, F.UnderDeckHeight))
  local x = MulDivRound(F.OutwardDistance, F.ExitDirectionX, 1000)
  local y = MulDivRound(F.OutwardDistance, F.ExitDirectionY, 1000)
  local outside = hub:GetRelativePoint(point(x, y, F.UnderDeckHeight))
  local high = hub:GetRelativePoint(point(x, y, F.TransferHeight))
  -- OI-25's crest stays. Descend in the same clear column before travelling out.
  return {floor, rim, exit, cruise, outside, high}
end

local function copy(path)
  local result = {}
  for i, node in ipairs(path) do result[i] = node end
  return result
end

local function append(path, pos, hidden, owner)
  if not pos then return false end
  path[#path + 1] = {pos = pos, hidden = hidden or false, owner = owner}
  return true
end

local function track_elements(track, from)
  if not live(track) or not live(track:GetStartStation()) or not live(track:GetEndStation()) then
    return nil
  end
  -- Broken originals remain in elements. Do not include the duplicate repair site.
  -- Unfinished new track is outside this prototype's physical existing-track graph.
  for _, el in ipairs(track.elements_under_construction or empty_table) do
    if not live(el.broken) then return nil end
  end
  local elements = {}
  for _, el in ipairs(track.elements or empty_table) do
    if not live(el) or not el.node_idx then return nil end
    elements[#elements + 1] = el
  end
  table.sort(elements, function(a, b) return a.node_idx < b.node_idx end)
  if from == track:GetEndStation() then
    local reverse = {}
    for i = #elements, 1, -1 do reverse[#reverse + 1] = elements[i] end
    return reverse
  end
  if from ~= track:GetStartStation() then return nil end
  return elements
end

local function tunnel_inner(mouth)
  local inner = mouth:GetInnerTrackElement()
  local connector = mouth:GetConnectorElement(0)
  if not live(inner) or not live(connector) then return nil end
  -- Backdrop approximation: use the deeper of the inner rail's two enter spots.
  -- Native backdrop/portal clearance must be judged in L3, never inferred here.
  local best, distance
  for _, name in ipairs({"Enter1", "Enter2"}) do
    local idx = inner:GetSpotBeginIndex(name)
    if idx >= 0 then
      local pos = inner:GetSpotPos(idx)
      local d = pos:Dist(connector:GetPos())
      if not distance or d > distance then best, distance = pos, d end
    end
  end
  return best and best + point(0, 0, F.OverTrackHeight + F.HoverHeight)
end

function F.Route(hub, target)
  local pit, reason = F.PitPoints(hub)
  if not pit then return nil, reason end
  if not live(target) then return nil, "Select a track element or its repair site" end
  local original = target
  if target.is_construction_site and live(target.broken) then original = target.broken end
  local target_track = original.track_obj
  if not live(target_track) then return nil, "Target has no physical track" end
  local prefix = {}
  for i = 3, #pit do append(prefix, pit[i], false, hub) end
  local queue = {{hub = hub, path = prefix}}
  local seen, seen_tracks = {[hub] = true}, {}
  local cursor = 1
  while queue[cursor] do
    local item = queue[cursor]
    cursor = cursor + 1
    local station = item.hub
    local found
    station:ForEachConnectorElement(function(connector)
      local track = connector.track_obj
      if found or not live(track) or seen_tracks[track] then return end
      seen_tracks[track] = true
      local elements = track_elements(track, station)
      if not elements or #elements == 0 then return end
      local path = copy(item.path)
      if station == hub then
        -- Approach the first rail only AFTER the outside climb. Cross at or above
        -- TransferHeight, then lower vertically onto its centreline cruise point.
        local first = elevated(elements[1])
        if not first then return end
        local high = path[#path].pos
        local z = max(high:z(), first:z())
        append(path, point(high:x(), high:y(), z), false, hub)
        append(path, point(first:x(), first:y(), z), false, elements[1])
      end
      -- Inside stations, connector-to-connector is an explicit above-deck segment.
      -- Its geometry/hood clearance is a live L3 obligation.
      for _, el in ipairs(elements) do
        if not append(path, elevated(el), false, el) then return end
        if track == target_track and el == original then found = path; return end
      end
      local dest = station == track:GetStartStation() and track:GetEndStation() or track:GetStartStation()
      if live(dest) and not seen[dest] then
        seen[dest] = true
        queue[#queue + 1] = {hub = dest, path = path}
      end
    end)
    if found then
      local site = original:GetVisualPos()
      if not site or site:z() == nil then return nil, "Target position missing" end
      append(found, site + point(0, 0, F.FixHeight), false, original)
      return found
    end
    local far = station.linked_obj
    if IsKindOf(station, "TrackTunnelBase") and live(far) and far.linked_obj == station and not seen[far] then
      local near_pos, far_pos = tunnel_inner(station), tunnel_inner(far)
      local connector = far:GetConnectorElement(0)
      if near_pos and far_pos and live(connector) then
        local path = copy(item.path)
        append(path, near_pos, false, station)
        append(path, far_pos, true, far) -- hidden only during this segment, in either direction
        append(path, elevated(connector), false, connector)
        seen[far] = true
        queue[#queue + 1] = {hub = far, path = path}
      end
    end
  end
  return nil, "Target unreachable through existing physical track and reciprocal tunnels"
end

-- Engine mode needs no route: the break's own position, validated as F.Route validates it.
function F.Site(target)
  if not live(target) then return nil, "Select a track element or its repair site" end
  local original = target
  if target.is_construction_site and live(target.broken) then original = target.broken end
  if not live(original.track_obj) then return nil, "Target has no physical track" end
  local site = original:GetVisualPos()
  if not site or site:z() == nil then return nil, "Target position missing" end
  return site, original
end

---------------------------------------------------------------------------------------------
-- Geometry: waypoint nodes -> primitives (straights and quadratic Bezier corners).
-- All arithmetic in engine units (cm) and game ms; vectors are {x,y,z} tables.
---------------------------------------------------------------------------------------------
local function V(p) return {p:x(), p:y(), p:z()} end
local function P(v) return point(int(v[1]), int(v[2]), int(v[3])) end
local function sub(a, b) return {a[1]-b[1], a[2]-b[2], a[3]-b[3]} end
local function add(a, b) return {a[1]+b[1], a[2]+b[2], a[3]+b[3]} end
local function scale(a, k) return {a[1]*k, a[2]*k, a[3]*k} end
local function dot(a, b) return a[1]*b[1] + a[2]*b[2] + a[3]*b[3] end
local function cross(a, b) return {a[2]*b[3]-a[3]*b[2], a[3]*b[1]-a[1]*b[3], a[1]*b[2]-a[2]*b[1]} end
local function norm(a) return math.sqrt(a[1]^2 + a[2]^2 + a[3]^2) end
local function unit(a)
  local l = norm(a)
  if l == 0 then return {0, 0, 0}, 0 end
  return {div(a[1], l), div(a[2], l), div(a[3], l)}, l
end
local function lerp(a, b, t) return {a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t, a[3]+(b[3]-a[3])*t} end

local function bez(pts, u)
  local q = {}
  for i, v in ipairs(pts) do q[i] = v end
  for n = #q - 1, 1, -1 do for i = 1, n do q[i] = lerp(q[i], q[i+1], u) end end
  return q[1]
end
local function bez_d1(pts, u)
  if #pts == 2 then return sub(pts[2], pts[1]) end
  return scale(add(scale(sub(pts[2], pts[1]), 1-u), scale(sub(pts[3], pts[2]), u)), 2)
end
local function bez_d2(pts)
  if #pts == 2 then return {0, 0, 0} end
  return scale(add(sub(pts[1], pts[2]), sub(pts[3], pts[2])), 2)
end
local function curvature(pts, u)
  local d1, d2 = bez_d1(pts, u), bez_d2(pts)
  local l = norm(d1)
  if l == 0 then return 0 end
  return div(norm(cross(d1, d2)), l^3)
end
-- Curvature of the path's horizontal projection (what a banked turn answers to) and the
-- turn's sign: positive is a left turn (yaw increasing). Vertical-plane corners bank nothing.
local function yaw_curvature(pts, u)
  local d1, d2 = bez_d1(pts, u), bez_d2(pts)
  local lh = math.sqrt(d1[1]^2 + d1[2]^2)
  local l = norm(d1)
  if l == 0 or lh < .2 * l then return 0, 0, 0 end
  local z = d1[1]*d2[2] - d1[2]*d2[1]
  return div(math.abs(z), lh^3), z > 0 and 1 or (z < 0 and -1 or 0), div(lh, l)
end

local SAMPLES = 32
local function primitive(pts, hidden, owner, cap)
  local prim = {pts = pts, hidden = hidden or false, owner = owner, curved = #pts > 2, cap = cap}
  if not prim.curved then
    prim.dir, prim.len = unit(sub(pts[2], pts[1]))
    prim.kappa = 0
    return prim
  end
  local table_s, prev, s, kmax = {0}, pts[1], 0, 0
  for i = 1, SAMPLES do
    local q = bez(pts, div(i, SAMPLES))
    s = s + norm(sub(q, prev)); table_s[i+1] = s; prev = q
  end
  for i = 0, SAMPLES do kmax = max(kmax, (curvature(pts, div(i, SAMPLES)))) end
  local d0, d1 = unit(bez_d1(pts, 0)), unit(bez_d1(pts, 1))
  prim.turn = math.deg(math.acos(clamp(dot(d0, d1), -1, 1))) * 60 -- angle minutes of deflection
  prim.len, prim.table, prim.kappa = s, table_s, kmax
  return prim
end

-- arc length -> position and Bezier parameter
local function prim_point(prim, s)
  if not prim.curved then
    return lerp(prim.pts[1], prim.pts[2], prim.len > 0 and clamp(div(s, prim.len), 0, 1) or 0), 0
  end
  local t = prim.table
  if s <= 0 then return bez(prim.pts, 0), 0 end
  if s >= prim.len then return bez(prim.pts, 1), 1 end
  local lo, hi = 1, #t
  while hi - lo > 1 do
    local mid = math.floor(div(lo + hi, 2))
    if t[mid] <= s then lo = mid else hi = mid end
  end
  local span = t[hi] - t[lo]
  local u = div((lo - 1) + (span > 0 and div(s - t[lo], span) or 0), SAMPLES)
  return bez(prim.pts, u), u
end

local function dir_cap(d)
  local uz, cap = math.abs(d[3]), F.Speed
  if uz > 1e-6 then cap = min(cap, div(F.ClimbRate, uz)) end
  return cap
end

local function prim_cap(p)
  local cap = p.cap or F.Speed
  if not p.curved then return max(50, min(cap, dir_cap(p.dir))) end
  local d0, d1 = unit(bez_d1(p.pts, 0)), unit(bez_d1(p.pts, 1))
  cap = min(cap, dir_cap(d0), dir_cap(d1))
  if p.kappa > 0 then cap = min(cap, math.sqrt(div(F.Accel, p.kappa))) end
  return max(cap, 50) -- never below 0.5 m/s so a corner's time stays finite
end

-- nodes: {p={x,y,z}, hidden (of the leg ARRIVING here), owner, stop, dwell, sharp, cap, radius}
local function build_geometry(nodes)
  local list = {}
  for _, n in ipairs(nodes) do
    local last = list[#list]
    if last and norm(sub(n.p, last.p)) < 1 then
      last.stop = last.stop or n.stop
      last.dwell = (last.dwell or 0) + (n.dwell or 0)
      last.owner = n.owner or last.owner
      last.sharp = last.sharp or n.sharp
    else
      list[#list+1] = {p = n.p, hidden = n.hidden or false, owner = n.owner, stop = n.stop,
        dwell = n.dwell, sharp = n.sharp, cap = n.cap, radius = n.radius}
    end
  end
  local N = #list
  local legs, trim = {}, {}
  for k = 1, N - 1 do
    local d, l = unit(sub(list[k+1].p, list[k].p))
    legs[k] = {dir = d, len = l, hidden = list[k+1].hidden, owner = list[k+1].owner, cap = list[k+1].cap}
  end
  local straight_cos = math.cos(math.rad(1))
  for k = 2, N - 1 do
    local a, b, node = legs[k-1], legs[k], list[k]
    local c = dot(a.dir, b.dir)
    if c < -.95 then node.stop = true end            -- a reversal must pass through rest
    if a.hidden ~= b.hidden then node.sharp = true end -- a concealment seam is exact, never rounded
    trim[k] = 0
    if not node.stop and not node.sharp and c < straight_cos then
      local d = min(F.TurnRadius, node.radius or F.TurnRadius, div(a.len, 2), div(b.len, 2))
      if d >= 20 then trim[k] = d end
    end
  end
  local prims = {}
  for k = 1, N - 1 do
    local leg = legs[k]
    local a = add(list[k].p, scale(leg.dir, trim[k] or 0))
    local b = sub(list[k+1].p, scale(leg.dir, trim[k+1] or 0))
    local straight = primitive({a, b}, leg.hidden, leg.owner, leg.cap)
    if (trim[k+1] or 0) == 0 then straight.end_node = list[k+1] end
    prims[#prims+1] = straight
    if (trim[k+1] or 0) > 0 then
      local corner = primitive({b, list[k+1].p, add(list[k+1].p, scale(legs[k+1].dir, trim[k+1]))},
        leg.hidden, legs[k+1].owner, min(leg.cap or F.Speed, legs[k+1].cap or F.Speed))
      prims[#prims+1] = corner
    end
  end
  return prims, list
end

-- Speed at every primitive boundary: caps, stops, then forward/backward Accel passes.
local function profile(prims, v_start)
  local M, n = #prims, {}
  for j, p in ipairs(prims) do
    p.vcap = prim_cap(p)
    local v = (j == M or (p.end_node and p.end_node.stop)) and 0 or p.vcap
    if j < M then v = min(v, prim_cap(prims[j+1])) end
    n[j+1] = v
  end
  n[1] = min(v_start or 0, prims[1] and prims[1].vcap or 0)
  for j = 1, M do
    local p = prims[j]
    n[j+1] = min(n[j+1], p.curved and n[j] or math.sqrt(n[j]^2 + 2 * F.Accel * p.len))
  end
  for j = M, 1, -1 do
    local p = prims[j]
    n[j] = min(n[j], p.curved and n[j+1] or math.sqrt(n[j+1]^2 + 2 * F.Accel * p.len))
  end
  return n
end

-- One engine chord: a straight timed move with constant acceleration, chained on speed.
local function push_chord(steps, a, b, v0, v1, prim, t, v_mid, u_mid)
  local ap, bp = P(a), P(b)
  local av, bv = V(ap), V(bp)
  local len = norm(sub(bv, av))
  if len < .5 then return t end
  local prev = steps[#steps]
  local v_in = (prev and prev.state == "fly" and prev.finish == t) and prev.v1 or v0
  local T = max(1, int(div(2 * len, max(1, v_in + v1)) * 1000))
  local acc = div(2 * (len - div(v_in * T, 1000)), div(T, 1000)^2)
  local v_out = v_in + div(acc * T, 1000)
  if v_out < 0 then acc = -div(v_in^2, 2 * len); v_out = 0; T = max(1, int(div(2 * len, v_in) * 1000)) end
  local roll = 0
  if prim.curved and F.BankAngle ~= 0 then
    local kappa, sign, level = yaw_curvature(prim.pts, u_mid or .5)
    local lateral = ((v_mid or v_in) * level)^2 * kappa
    roll = -sign * F.BankAngle * min(1, div(lateral, F.Accel)) -- left turn (yaw increasing): left bank
  end
  steps[#steps+1] = {state = "fly", start = t, finish = t + T, a = av, b = bv, bp = bp, len = len,
    v0 = v_in, v1 = v_out, acc = acc, hidden = prim.hidden, owner = prim.owner, roll = roll,
    curved = prim.curved, turn = prim.turn}
  prim.start = prim.start or t
  prim.finish = t + T
  return t + T
end

local function trapezoid(L, v_in, v_out, cap)
  cap = max(cap, v_in, v_out)
  local d_acc, d_dec = div(cap^2 - v_in^2, 2 * F.Accel), div(cap^2 - v_out^2, 2 * F.Accel)
  if d_acc + d_dec <= L then
    return {{d_acc, v_in, cap}, {L - d_acc - d_dec, cap, cap}, {d_dec, cap, v_out}}
  end
  local vp = math.sqrt(max(0, div(2 * F.Accel * L + v_in^2 + v_out^2, 2)))
  return {{div(vp^2 - v_in^2, 2 * F.Accel), v_in, vp}, {div(vp^2 - v_out^2, 2 * F.Accel), vp, v_out}}
end

-- Chords for one straight primitive between boundary speeds.
local function straight_chords(steps, p, v_in, v_out, t)
  local base = 0
  for _, piece in ipairs(trapezoid(p.len, v_in, v_out, p.vcap)) do
    local d, v0, v1 = piece[1], piece[2], piece[3]
    if d > .5 then
      local T = div(2 * d, v0 + v1) * 1000
      local count = max(1, math.ceil(div(T, F.ChordTime)))
      count = min(count, max(1, math.floor(div(T, F.ChordMinTime))))
      local acc = div(v1 - v0, div(T, 1000))
      for i = 1, count do
        local tau0, tau1 = div(T * (i-1), count * 1000), div(T * i, count * 1000)
        local d0, d1 = v0 * tau0 + .5 * acc * tau0^2, v0 * tau1 + .5 * acc * tau1^2
        t = push_chord(steps, (prim_point(p, base + d0)), (prim_point(p, base + min(d, d1))),
          v0 + acc * tau0, v0 + acc * tau1, p, t)
      end
      base = base + d
    end
  end
  return t
end

-- Chords for one corner: constant speed, split by time and by turn angle.
local function corner_chords(steps, p, v, t)
  v = max(v, 50)
  local T = div(p.len, v) * 1000
  local count = max(1, math.ceil(div(T, F.ChordTime)), math.ceil(div(p.turn, max(1, F.ChordAngle))))
  count = min(count, max(1, math.floor(div(T, F.ChordMinTime))))
  for i = 1, count do
    local s0, s1 = div(p.len * (i-1), count), div(p.len * i, count)
    local a = prim_point(p, s0)
    local b = prim_point(p, s1)
    local _, u_mid = prim_point(p, div(s0 + s1, 2))
    t = push_chord(steps, a, b, v, v, p, t, v, u_mid)
  end
  return t
end

-- Headings: the horizontal direction of each chord; vertical and hidden chords look ahead
-- to the next visible horizontal motion so the drone turns while it rises or is concealed.
local function fill_headings(steps)
  local next_heading
  for i = #steps, 1, -1 do
    local s = steps[i]
    if s.state == "fly" then
      local dx, dy = s.b[1] - s.a[1], s.b[2] - s.a[2]
      -- A chord within about 11 degrees of vertical carries no heading of its own.
      if not s.hidden and dx*dx + dy*dy > .04 * s.len^2 then
        s.heading = CalcOrientation(P(s.a), P(s.b))
        next_heading = s.heading
      else
        s.heading = next_heading
      end
    end
  end
  local previous
  for _, s in ipairs(steps) do
    if s.state == "fly" then
      if not s.heading then s.heading = previous end
      previous = s.heading or previous
    end
  end
end

-- Public: nodes -> ordered steps (chords and dwell hovers) from time t0, plus primitives.
function F.Trajectory(nodes, v_start, t0)
  local prims = build_geometry(nodes)
  local steps, t = {}, t0 or 0
  if #prims == 0 then return steps, t, prims end
  local n = profile(prims, v_start)
  for j, p in ipairs(prims) do
    if p.len > .5 then
      if p.curved then t = corner_chords(steps, p, n[j], t) else t = straight_chords(steps, p, n[j], n[j+1], t) end
    end
    local node = p.end_node
    if node and (node.dwell or 0) > 0 then
      local at = steps[#steps] and steps[#steps].b or p.pts[2]
      steps[#steps+1] = {state = "hover", start = t, finish = t + node.dwell, pos = at, bp = P(at), owner = p.owner}
      t = t + node.dwell
    end
  end
  return steps, t, prims
end

-- Public pure sampler: tests, clearance export and L4 reconstruction read the same chords.
local function step_at(plan, elapsed)
  local steps = plan.steps
  local lo, hi = 1, #steps
  if hi == 0 then return nil end
  if elapsed >= steps[hi].finish then return steps[hi], hi end
  while hi > lo do
    local mid = math.floor(div(lo + hi, 2))
    if steps[mid].finish <= elapsed then lo = mid + 1 else hi = mid end
  end
  return steps[lo], lo
end

function F.Position(plan, elapsed)
  local s = step_at(plan, elapsed)
  if not s then return nil end
  if s.state ~= "fly" then return s.bp end
  if elapsed >= s.finish then return s.bp end
  local tau = div(max(0, elapsed - s.start), 1000)
  local d = s.v0 * tau + .5 * s.acc * tau^2
  return P(lerp(s.a, s.b, s.len > 0 and clamp(div(d, s.len), 0, 1) or 0))
end

local function speed_at(plan, elapsed)
  local s = step_at(plan, elapsed)
  if not s or s.state ~= "fly" or elapsed >= s.finish then return 0, s end
  return max(0, s.v0 + div(s.acc * max(0, elapsed - s.start), 1000)), s
end

---------------------------------------------------------------------------------------------
-- Issue one step to the engine: a chord (timed SetPos + SetAcceleration + SetRollPitchYaw),
-- or a state at rest. Called exactly at the chord's start by the game-time driver; a late
-- caller shortens the move so the visual never outlasts its deadline (the fence).
---------------------------------------------------------------------------------------------
local function issue(a, step, elapsed, skipped)
  local drone = a.drone
  -- First placement, or a sparse caller that skipped chords: catch up to the absolute
  -- position instantly (the fence), then fly the current chord from there.
  if not a.placed or skipped then
    drone:SetPos(F.Position(a.plan, elapsed))
    a.placed = true
  end
  local remaining = max(1, step.finish - elapsed)
  if step.state == "fly" then
    if a.state ~= "fly" then
      drone:StopFX()
      drone:SetState("fly")
      a.state = "fly"
    end
    if a.visible ~= (not step.hidden) then
      a.visible = not step.hidden
      drone:SetVisible(a.visible)
    end
    local T = div(remaining, 1000)
    local acc = step.acc
    if elapsed > step.start then
      acc = div(2 * (step.len - step.v0 * T), T * T)
      if step.v0 * T > step.len then acc = 0 end
    end
    drone:SetPos(step.bp, remaining)
    drone:SetAcceleration(int(acc))
    local yaw = a.yaw or drone:GetAngle()
    local target = step.heading or yaw
    local delta = ((target - yaw + 10800) % 21600) - 10800
    local limit = div((drone.max_yaw_speed or F.YawRate) * remaining, 1000)
    yaw = (yaw + clamp(delta, -limit, limit)) % 21600
    a.yaw = yaw
    local roll = F.BankAngle ~= 0 and clamp(step.roll or 0, -math.abs(F.BankAngle), math.abs(F.BankAngle)) or 0
    drone:SetRollPitchYaw(int(roll), 0, int(yaw), remaining)
  else
    -- At rest at step.bp: the last chord ended at zero speed and zero roll. Only now may
    -- the state, animation and FX change (Land -> MoveSleep -> LandingEnd order).
    if a.visible ~= true then a.visible = true; drone:SetVisible(true) end
    drone:SetAcceleration(0)
    if a.state ~= step.state then
      drone:StopFX()
      a.state = step.state
      if step.state ~= "hover" then drone:SetState(step.state) end
      if step.state == "constructStart" or step.state == "constructIdle" then
        drone:StartFX("Construct", live(a.target) and a.target or nil)
      end
    end
  end
  a.step, a.phase = step, step.state
end

-- DoneObject, not DespawnNow: the prototype never enters hub.drones, and DroneControl:KillDrone
-- asserts membership (DroneControl.lua:729-733). Drone:Done drops any carried resource itself.
function F.Remove(old)
  if old then visuals[old] = nil end
  if old and old == active then active = false end
  if old and old.lost then F.Lost = old.lost end
  if old and IsValid(old.drone) then
    if SelectedObj == old.drone then SelectObj(false) end
    old.drone:StopFX()
    DoneObject(old.drone)
  end
end

function F.Clear()
  local old = active
  active = false
  F.Remove(old)
end

function F.ClearAll()
  F.Clear()
  for record in pairs(visuals) do F.Remove(record) end
  DeleteThread(driver); driver = false
end

function F.Status()
  if not active then return false end
  return {drone = active.drone, hub = active.hub, phase = active.phase,
    started = active.started, arrival = active.arrival, work_done = active.work_done,
    removed = active.removed, now = GameTime(), mode = active.mode, stage = active.stage,
    handoff = active.handoff, command = live(active.drone) and active.drone.command or nil}
end

-- Play a scripted plan to `now`: issue the step that contains it, if not issued yet. Returns
-- the game ms until the next boundary, true once the plan has fully played out, or false when
-- the record was removed. Idempotent for a repeated `now`; a sparse caller catches up instead
-- of extending a deadline.
local function run_plan(a, elapsed)
  local plan, steps = a.plan, a.plan.steps
  if #steps == 0 or elapsed >= plan.total then -- a recall at the spawn instant has no chord to fly
    local last = steps[#steps]
    if last and (a.issued or 0) < #steps then
      a.drone:SetPos(last.bp)
      a.drone:SetAcceleration(0)
      a.issued, a.placed, a.step = #steps, true, last
    end
    return true
  end
  local i, target = a.issued or 0, a.issued or 0
  while steps[target+1] and steps[target+1].start <= elapsed do target = target + 1 end
  local current = steps[max(1, target)]
  if current.owner and not live(current.owner) then F.Remove(a); return false end
  if target > i then
    local skipped = false
    for j = i + 1, target - 1 do if steps[j].state == "fly" then skipped = true end end
    issue(a, current, elapsed, skipped)
    a.issued = target
  end
  return max(1, current.finish - elapsed)
end

function F.Update(a, now)
  if not a then return false end
  now = now or GameTime()
  if a.mode == "engine" then return F.UpdateEngine(a, now) end
  if save_gate or not hub_ok(a.hub) or not live(a.drone) or a.drone.command_center ~= a.hub
    or a.drone.command or a.drone.run_cmd_on_land then F.Remove(a); return false end
  a.drone.battery = a.drone.battery_max
  local wait = run_plan(a, max(0, now - a.started))
  if wait ~= true then return wait end
  if a.remove then a.drone:LandingEnd(); F.Remove(a); return false end
  a.phase = "hover"
  return 1000
end

local function rise_nodes(pit)
  return {{p = V(pit[1]), stop = true}, {p = V(pit[2])}, {p = V(pit[3]), stop = true}}
end

local function make_plan(steps, total, prims)
  for i, s in ipairs(steps) do s.index = i end
  return {steps = steps, total = total, prims = prims}
end

-- Steps already begun before `elapsed` were issued by the plan they came from (the rebuilt
-- launch has identical chords); a step starting exactly now is still owed.
local function issued_before(steps, elapsed)
  local i = 0
  while steps[i+1] and steps[i+1].start < elapsed do i = i + 1 end
  return i
end

---------------------------------------------------------------------------------------------
-- Engine mode. Stages: rise (ours) -> ready (stock hold at the crest) -> [exit (ours, when
-- HandoffAt="outside")] -> out (engine) -> work (ours) -> back (engine) -> descent (ours).
-- The drone is under a stock command or hold exactly in ready/out/back, and under no command
-- at all while our chords fly it.
---------------------------------------------------------------------------------------------
local function hold(a, now)
  a.drone:InterruptWait() -- a re-arm ends the running hold first, or the new command waits for its timeout
  a.drone:SetCommand(STOCK_HOLD, F.HoldTimeout)
  a.hold_at = now
end

-- End the stock hold before vanilla's Idle can follow it, leaving the drone with no command.
local function take_back(a)
  a.drone:InterruptWait()
  a.drone:SetCommand(false)
  a.state, a.hold_at = false, nil -- the next chord re-asserts the fly state after the engine's own
end

-- One engine leg: a stock FlightGoto to a 2D point (the shape FlyingDrone:Goto hands the same
-- call), with the stock hold queued behind it so the arrival is ours, not Idle's.
local function leg(a, now, stage)
  local dest = stage == "out" and a.site or a.pit[a.handoff]
  a.drone:InterruptWait()
  a.drone:SetCommand(STOCK_LEG, point(dest:x(), dest:y()))
  a.drone:QueueCommand(STOCK_HOLD, F.HoldTimeout)
  a.stage, a.phase, a.leg_at, a.state, a.hold_at = stage, stage, now, false, nil
  local from = a.drone:GetVisualPos()
  a.leg_from = point(from:x(), from:y(), 0)
end

-- The smoke's speed record (link 5): what the engine leg really flew, in game time.
local function report_leg(a, now)
  if not a.leg_at or not a.leg_from then return end
  local p = a.drone:GetVisualPos()
  local dist = point(p:x(), p:y(), 0):Dist(a.leg_from)
  local ms = max(1, now - a.leg_at)
  print(string.format("[TrainHubDev] engine leg %s: %d m in %d ms = %d units per s (move_speed %s) at t=%d",
    a.stage, int(div(dist, 100)), ms, MulDivRound(dist, 1000, ms), tostring(a.drone.move_speed), now))
end

local function scripted(a, now, steps, total, prims, stage)
  fill_headings(steps)
  a.plan, a.started, a.issued, a.placed = make_plan(steps, max(1, total), prims), now, 0, true
  a.stage, a.phase = stage, stage
end

local function here(a) return V(a.drone:GetVisualPos()) end

-- Ours from the crest hold: the rise already flown keeps its exact chords, the crest dwell
-- absorbs the hold, and `extra` continues from the crest. A recall retraces to the floor.
local function continue_from_crest(a, now, extra, stage)
  local _, rise_total = F.Trajectory(rise_nodes(a.pit), 0, 0)
  local nodes = rise_nodes(a.pit)
  nodes[#nodes].dwell = max(0, now - a.rise_started - rise_total)
  for _, n in ipairs(extra) do nodes[#nodes+1] = n end
  nodes[#nodes].stop = true
  local steps, total, prims = F.Trajectory(nodes, 0, 0)
  scripted(a, now, steps, total, prims, stage)
  a.started = a.rise_started
  a.issued = issued_before(steps, max(0, now - a.started))
end

-- Ours at the break: down from the engine's arrival to the work pose, the work, and back up
-- to the arrival height the engine chose, from where it takes the return leg.
local function work_plan(a, now)
  local drone, arrival = a.drone, here(a)
  local pose = {a.site:x(), a.site:y(), a.site:z() + F.FixHeight}
  local steps, total, prims = F.Trajectory({{p = arrival, stop = true}, {p = pose, stop = true}}, 0, 0)
  local at = steps[#steps] and steps[#steps].b or pose
  local bp = P(at)
  for _, state in ipairs({{"constructStart", max(1, drone:GetAnimDuration("constructStart"))},
      {"constructIdle", F.WorkTime}, {"constructEnd", max(1, drone:GetAnimDuration("constructEnd"))}}) do
    steps[#steps+1] = {state = state[1], start = total, finish = total + state[2], pos = at, bp = bp, owner = a.site_owner}
    total = total + state[2]
  end
  local up, up_total, up_prims = F.Trajectory({{p = at, stop = true}, {p = arrival, stop = true}}, 0, total)
  for _, s in ipairs(up) do steps[#steps+1] = s end
  for _, p in ipairs(up_prims) do prims[#prims+1] = p end
  scripted(a, now, steps, up_total, prims, "work")
  a.target_pose = bp
end

-- Ours at the end: from wherever the engine's return leg ended, down the settled route into
-- the pit. HandoffAt="outside" re-enters under the deck and keeps OI-25's crest reversal.
local function descent_plan(a, now)
  local nodes = {{p = here(a), stop = true}}
  for i = a.handoff, 1, -1 do nodes[#nodes+1] = {p = V(a.pit[i]), stop = i == 3 or i == 1} end
  local steps, total, prims = F.Trajectory(nodes, 0, 0)
  scripted(a, now, steps, total, prims, "descent")
  a.remove = true
end

function F.UpdateEngine(a, now)
  local d = a.drone
  if save_gate then return F.PollTime end -- the driver is gone for the save; nothing is issued
  if not hub_ok(a.hub) or not live(d) or d.command_center ~= a.hub or d.run_cmd_on_land then
    F.Remove(a); return false
  end
  d.battery = d.battery_max
  local stage, c = a.stage, d.command
  if stage == "out" or stage == "back" then
    if c == STOCK_LEG then return F.PollTime end
    if c ~= STOCK_HOLD then a.lost = c or "none"; F.Remove(a); return false end
    report_leg(a, now)
    take_back(a)
    if stage == "out" then work_plan(a, now) else descent_plan(a, now) end
    stage = a.stage
  elseif stage == "ready" then
    if c ~= STOCK_HOLD then a.lost = c or "none"; F.Remove(a); return false end
    if not a.target then
      if now - a.hold_at >= int(div(F.HoldTimeout, 2)) then hold(a, now) end
      return F.PollTime
    end
    if a.handoff == 5 then
      take_back(a)
      continue_from_crest(a, now, {{p = V(a.pit[4])}, {p = V(a.pit[5])}}, "exit")
      stage = "exit"
    else
      leg(a, now, "out")
      return F.PollTime
    end
  elseif c then
    a.lost = c; F.Remove(a); return false -- something else commanded the drone mid-chord
  end
  local wait = run_plan(a, max(0, now - a.started))
  if wait ~= true then return wait end
  if stage == "rise" then
    hold(a, now); a.stage, a.phase = "ready", "hover"
  elseif stage == "exit" then leg(a, now, "out")
  elseif stage == "work" then
    -- the hub completes the site as the Wasp lifts off, not on its next 5 s tick (L5, 2026-09-24)
    if F.OnWorkDone then F.OnWorkDone(a.hub, a.drone, now) end
    leg(a, now, "back")
  else d:LandingEnd(); F.Remove(a); return false end
  return F.PollTime
end

-- A drone under a stock command or hold has no mod thread and may stay in a save.
function F.Persists(a)
  return a.mode == "engine" and (a.stage == "ready" or a.stage == "out" or a.stage == "back")
end

-- Prototype leftovers in a loaded save: a Wasp whose controller is a train hub but that neither
-- the hub's own fleet list nor a registered record (an adopted repair flight) holds. The hub
-- runs its own sweep after adopting its jobs; this one serves the console prototype.
function F.SweepLoaded()
  local held = {}
  for record in pairs(visuals) do if live(record.drone) then held[record.drone] = true end end
  AllMapsForEach(true, "FlyingDrone", function(d)
    local hub = d.command_center
    if live(d) and hub_ok(hub) and not held[d] and not table.find(hub.drones or empty_table, d) then
      F.Lost = "load"
      d:StopFX()
      DoneObject(d)
    end
  end)
end

-- Services every registered visual; returns the shortest wait or nil when none is left.
function F.Sample()
  local wait
  for record in pairs(visuals) do
    local w = F.Update(record)
    if w then wait = wait and min(wait, w) or w end
  end
  return wait
end

-- GAME-time driver, the Wasp's own thread shape: sleep exactly until the chord ends.
-- Zero upvalues; the orphan gate is the first statement after the yield (FIX_POLICY §3a).
local function start_driver()
  if IsValidThread(driver) then return end
  driver = CreateGameTimeThread(function()
    while true do
      local wait = SMROptInHubFlight and SMROptInHubFlight.Sample()
      if not wait then return end
      Sleep(wait)
      if not SMROptInHubFlight then return end
    end
  end)
end

function F.Create(hub, started)
  if save_gate then return nil, "Save in progress" end
  local pit, reason = F.PitPoints(hub)
  if not pit then return nil, reason end
  local drone = FlyingDrone:new({city = hub.city, command_center = hub,
    init_with_command = false, battery_max = F.BatteryMax, battery = F.BatteryMax,
    name = Untranslated("Repair Drone")}, hub:GetMap())
  if not IsValid(drone) then return nil, "Wasp creation failed" end
  -- No command is started and no custom function is placed on a vanilla object.
  -- Keep the console visual out of controller dispatch lists; L4 owns fleet integration.
  drone:SetPos(pit[1])
  drone:TakeOff()
  drone:SetCurvature(false)
  drone:SetAcceleration(0)
  if F.Palette then Building.SetPalette(drone, table.unpack(F.Palette)) end
  local steps, total, prims = F.Trajectory(rise_nodes(pit), 0, 0)
  fill_headings(steps)
  local record = {hub = hub, drone = drone, pit = pit, plan = make_plan(steps, total, prims),
    started = started or GameTime(), phase = "launch", issued = 0, state = "fly", visible = true,
    yaw = drone:GetAngle(), placed = true, mode = F.Mode}
  if record.mode == "engine" then
    record.stage, record.rise_started = "rise", record.started
    record.handoff = F.HandoffAt == "outside" and 5 or 3
  end
  visuals[record] = true
  start_driver()
  return record
end

-- L4: take back a Wasp that rode a save under a stock leg or hold (F.Persists), at the stage
-- the hub's persisted deadline names: "out" (still flying to the break, or holding there) or
-- "back" (the work is done by the deadline's reckoning; the next hold ends in the descent).
-- Nothing is flown here: the driver's next look treats the record exactly like one it made
-- itself, so a leg still under way is polled and a hold is taken back within one PollTime.
-- A Wasp under any other command is refused; the hub then sweeps it as a stray.
function F.Adopt(hub, drone, target, stage)
  if save_gate then return nil, "Save in progress" end
  local pit, reason = F.PitPoints(hub)
  if not pit then return nil, reason end
  if not live(drone) or drone.command_center ~= hub then return nil, "Not this hub's Wasp" end
  if stage ~= "out" and stage ~= "back" then return nil, 'Stage is "out" or "back"' end
  local c = drone.command
  if c ~= STOCK_LEG and c ~= STOCK_HOLD then return nil, "Not under a stock leg or hold" end
  local site, owner = F.Site(target)
  if not site then return nil, owner end
  for record in pairs(visuals) do if record.drone == drone then return record end end
  local now = GameTime()
  drone.battery_max = F.BatteryMax
  drone.battery = F.BatteryMax
  drone:SetCurvature(false)
  local record = {hub = hub, drone = drone, pit = pit, plan = make_plan({}, 1, {}), started = now,
    phase = stage, issued = 0, state = false, visible = true, yaw = drone:GetAngle(), placed = true,
    mode = "engine", stage = stage, handoff = F.HandoffAt == "outside" and 5 or 3,
    target = target, site = site, site_owner = owner, leg_at = now, rise_started = now}
  visuals[record] = true
  start_driver()
  return record
end

function SpawnHubDrone(hub)
  if save_gate then return nil, "Save in progress" end
  if active and live(active.drone) then return active.drone, F.Status() end
  F.Clear()
  local record, reason = F.Create(hub or SelectedObj)
  if not record then return nil, reason end
  active = record
  return active.drone, F.Status()
end

function F.Send(record, target, keep_start)
  if save_gate then return nil, "Save in progress" end
  if not record or not live(record.drone) then return nil, "No live flight" end
  if record.target == target then return record end
  if record.target then return nil, "Return the current flight first" end
  if record.mode == "engine" then
    -- Only from the rise or the crest hold; the driver's next look issues the exit or the leg.
    if record.stage ~= "rise" and record.stage ~= "ready" then return nil, "Return the current flight first" end
    local site, owner = F.Site(target)
    if not site then return nil, owner end
    record.target, record.site, record.site_owner = target, site, owner
    return record
  end
  local path, reason = F.Route(record.hub, target)
  if not path then return nil, reason end
  local drone, start = record.drone, record.started
  -- The launch already flown keeps its exact chords; the drone dwells at the crest until now.
  local _, rise_total = F.Trajectory(rise_nodes(record.pit), 0, 0)
  local wait = keep_start and 0 or max(0, GameTime() - start - rise_total)
  local nodes = rise_nodes(record.pit)
  nodes[#nodes].dwell = wait
  for i = 2, #path do nodes[#nodes+1] = {p = V(path[i].pos), hidden = path[i].hidden, owner = path[i].owner} end
  nodes[#nodes].stop = true
  local steps, total, prims = F.Trajectory(nodes, 0, 0)
  local arrival = total
  local at = steps[#steps].b or steps[#steps].pos
  local site = P(at)
  for _, state in ipairs({{"constructStart", max(1, drone:GetAnimDuration("constructStart"))},
      {"constructIdle", F.WorkTime}, {"constructEnd", max(1, drone:GetAnimDuration("constructEnd"))}}) do
    steps[#steps+1] = {state = state[1], start = total, finish = total + state[2], pos = at, bp = site, owner = path[#path].owner}
    total = total + state[2]
  end
  local work_done = total
  local back = {}
  for i = #nodes, 1, -1 do
    local after = nodes[i+1]
    back[#back+1] = {p = nodes[i].p, hidden = after and after.hidden or false, owner = after and after.owner or nodes[i].owner,
      stop = i == #nodes or i == 1}
  end
  local back_steps, back_total, back_prims = F.Trajectory(back, 0, total)
  for _, s in ipairs(back_steps) do steps[#steps+1] = s end
  for _, p in ipairs(back_prims) do prims[#prims+1] = p end
  total = back_total
  fill_headings(steps)
  record.plan, record.target, record.remove = make_plan(steps, total, prims), target, true
  record.arrival, record.work_done, record.removed = start + arrival, start + work_done, start + total
  -- Chords the old plan issued are the same chords here; anything past them is still owed.
  record.issued = min(record.issued or 0, issued_before(steps, max(0, GameTime() - start)))
  return record
end

function SendHubDroneTo(target, hub)
  if save_gate then return nil, "Save in progress" end
  target = target or SelectedObj
  hub = hub or (active and active.hub)
  if active and active.hub ~= hub then return nil, "Prototype already belongs to another hub" end
  -- Validate before creating any visual, so an isolated target cannot leave one behind.
  local mode = active and active.mode or F.Mode
  local path, reason
  if mode == "engine" then path, reason = F.Site(target) else path, reason = F.Route(hub, target) end
  if not path then return nil, reason end
  local drone, err = SpawnHubDrone(hub)
  if not drone then return nil, err end
  local record, why = F.Send(active, target)
  if not record then return nil, why end
  return drone, F.Status()
end

-- Early recall: brake at Accel along the chords already planned, stop, then fly the flown
-- chords back to the pit floor with the same profile. No new chord cuts a rounded corner.
function ReturnHubDrone()
  if not active then return true end
  if active.returning then return active.drone, F.Status() end
  F.Sample()
  if not active then return true end
  local a, now = active, GameTime()
  if a.mode == "engine" then
    local stage = a.stage -- a.target stays: it is the work FX target, and the stage gates re-sends
    if stage == "out" then
      leg(a, now, "back") -- a mid-air SetCommand re-plans from the current velocity (FlyingDrone.lua:50)
    elseif stage == "ready" then
      take_back(a)
      continue_from_crest(a, now, {{p = V(a.pit[2])}, {p = V(a.pit[1])}}, "descent")
      a.remove = true
    elseif stage == "rise" or stage == "exit" then
      a.returning = true -- the scripted recall below retraces the flown chords to the floor
    end
    -- work: the pose finishes and the return leg follows anyway; back/descent: already returning
    if not a.returning then return a.drone, F.Status() end
    a.returning = nil
  elseif a.work_done and now >= a.work_done then
    a.returning = true
    return a.drone, F.Status()
  end
  local plan = a.plan
  local limit = a.arrival and a.arrival - a.started or plan.total
  local elapsed = min(max(0, now - a.started), limit)
  local v_now, current = speed_at(plan, elapsed)
  local here = V(F.Position(plan, elapsed))
  local nodes = {{p = here, stop = v_now <= 0}}
  local brake = div(v_now^2, 2 * F.Accel)
  local _, index = step_at(plan, elapsed)
  local flown = {}
  for i = 1, (index or 1) - 1 do
    local s = plan.steps[i]
    if s.state == "fly" and s.finish <= limit then flown[#flown+1] = s end
  end
  if current and current.state == "fly" and elapsed < current.finish and v_now > 0 then
    local travelled = 0
    local i = index
    local s = current
    local from = here
    while s and s.state == "fly" and s.finish <= limit and travelled < brake do
      local rest = norm(sub(s.b, from))
      local cap = max(s.v0, s.v1)
      if travelled + rest >= brake then
        local cut = lerp(from, s.b, rest > 0 and div(brake - travelled, rest) or 1)
        nodes[#nodes+1] = {p = cut, hidden = s.hidden, owner = s.owner, sharp = true, cap = cap, stop = true}
        travelled = brake
      else
        nodes[#nodes+1] = {p = s.b, hidden = s.hidden, owner = s.owner, sharp = true, cap = cap}
        travelled = travelled + rest
        from = s.b
        i = i + 1
        s = plan.steps[i]
      end
    end
    nodes[#nodes].stop = true
    -- The chord entered before the recall keeps its speed cap on the way back too.
    flown[#flown+1] = {a = current.a, b = here, hidden = current.hidden, owner = current.owner, v0 = current.v0, v1 = v_now}
  end
  for j = #nodes - 1, 1, -1 do
    local n, after = nodes[j], nodes[j+1]
    nodes[#nodes+1] = {p = n.p, hidden = after.hidden, owner = after.owner, sharp = true, cap = after.cap}
  end
  for i = #flown, 1, -1 do
    local s = flown[i]
    nodes[#nodes+1] = {p = s.a, hidden = s.hidden, owner = s.owner, sharp = true, cap = max(s.v0, s.v1)}
  end
  nodes[#nodes].stop = true
  local steps, total, prims = F.Trajectory(nodes, v_now, 0)
  fill_headings(steps)
  a.drone:StopFX()
  a.plan, a.started, a.remove, a.returning, a.issued = make_plan(steps, max(1, total), prims), now, true, true, 0
  a.arrival, a.work_done, a.removed = false, false, now + max(1, total)
  if a.mode == "engine" then a.stage, a.phase = "descent", "descent" end
  return a.drone, F.Status()
end

function SetHubDroneTune(name, value)
  if active then return false, "Return the prototype before changing its constants" end
  local tuneable = {HoverHeight = true, OverTrackHeight = true, FixHeight = true,
    UnderDeckHeight = true, OutwardDistance = true, ClimbRate = true, TransferHeight = true,
    Speed = true, WorkTime = true, TurnRadius = true, Accel = true, BankAngle = true,
    HoldTimeout = true, ExitDirectionX = true, ExitDirectionY = true}
  -- Dials that may be negative, with their magnitude limit; every other dial is a positive integer.
  local signed = {BankAngle = 2700, ExitDirectionX = 1000, ExitDirectionY = 1000}
  local limit = signed[name]
  if not tuneable[name] or type(value) ~= "number" or value ~= math.floor(value)
    or (limit and (value < -limit or value > limit)) or (not limit and value < 1) then
    return false, "Use a named positive integer; BankAngle -2700..2700 angle minutes, "
      .. "ExitDirectionX and ExitDirectionY -1000..1000 (a unit vector in thousandths)" end
  F[name] = value
  return true
end

-- The owner's switch, at the console, without a reload: it applies to the next SpawnHubDrone,
-- so link 3 can Return, switch and Spawn to A/B the two implementations in one sitting.
function SetHubDroneMode(mode, handoff)
  if mode ~= "engine" and mode ~= "scripted" then return false, 'Use "engine" or "scripted"' end
  if handoff ~= nil and handoff ~= "crest" and handoff ~= "outside" then
    return false, 'The handoff is "crest" or "outside"'
  end
  F.Mode = mode
  if handoff then F.HandoffAt = handoff end
  return true, F.Mode .. " " .. F.HandoffAt .. (active and " (next spawn)" or "")
end

-- Scripted motion has no thread in the save and is removed; a drone under a stock command or
-- hold completes itself and stays. The driver never rides in the save: it is deleted here
-- and restarted at SaveGameDone with its records intact in memory.
function OnMsg.SaveGameStart()
  save_gate = true
  DeleteThread(driver); driver = false
  for record in pairs(visuals) do
    if not F.Persists(record) then F.Remove(record) end
  end
end
function OnMsg.SaveGameDone()
  save_gate = false
  if next(visuals) then start_driver() end
end
-- The hub adopts its jobs' Wasps on its first tick after load and sweeps the rest (L4).
function OnMsg.LoadGame() F.ClearAll(); save_gate = false end
function OnMsg.DoneGame()
  F.ClearAll(); save_gate = false
end
