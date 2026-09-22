-- Drones chain L2: console-only Wasp flight prototype. Owner OI-25, 2026-09-22.
-- No dispatch, resources, task requests, class additions or persisted mod fields.
-- Save policy: synchronous sampling from a REAL-time driver (no saved mod frames).
-- Layer 3 inputs cannot express a track ride; layer 2 cannot animate after yielding.
-- Layer 1 removes the vanilla visual at SaveGameStart and gates spawns until Done.
-- This prototype cancels at save/load; L4 owns persisted deadlines and reconstruction.
-- Source surfaces: archived 1.1.0.403908, build 24995074: Unit.lua:42-51
-- (init_with_command=false), FlyingDrone.lua:120-123 (TakeOff), Track.lua:194-199,
-- TrainTransport.lua:57-65, TrackTunnel.lua:20-28; EF-112/115 (FX and battery).

if SMROptInHubFlight and SMROptInHubFlight.ClearAll then SMROptInHubFlight.ClearAll() end
SMROptInHubFlight = {
  HoverHeight = 300,        -- engine units above each track element origin; GUESS, tune in L3
  Speed = 6000,             -- engine units per game second; GUESS
  LaunchTime = 3000,        -- game ms, floor -> rim -> above deck
  LandingTime = 3000,       -- game ms, above deck -> rim -> floor
  WorkTime = 5000,          -- game ms in constructIdle, excludes start/end animations
  PitOffsetX = -310, PitOffsetY = 180, PitExitZ = 1000, -- OI-25, entity local
  BatteryMax = 800000,
  Palette = false,          -- optional array of four colours, L3 visual verdict
  SampleTime = 20,          -- real ms; position and deadlines use GameTime(), not wall time
}

local F = SMROptInHubFlight
local active, save_gate, driver = false, false, false
local visuals = {}

local function live(o)
  return IsValid(o) and not o.destroyed and not IsBeingDestructed(o)
end

local function hub_ok(h)
  return live(h) and h:GetEntity() == "SMROptInTrainHub6" and h.city
end

local function elevated(o)
  local p = o:GetVisualPos()
  if not p or p:z() == nil then return nil end
  return p + point(0, 0, F.HoverHeight)
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
  return {floor, rim, exit}
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
  return best and best + point(0, 0, F.HoverHeight)
end

function F.Route(hub, target)
  local pit, reason = F.PitPoints(hub)
  if not pit then return nil, reason end
  if not live(target) then return nil, "Select a track element or its repair site" end
  local original = target
  if target.is_construction_site and live(target.broken) then original = target.broken end
  local target_track = original.track_obj
  if not live(target_track) then return nil, "Target has no physical track" end
  local queue = {{hub = hub, path = {{pos = pit[3], owner = hub}}}}
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
    if found then return found end
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

local function duration(a, b)
  return Max(1, MulDivRound(a:Dist(b), 1000, F.Speed))
end

local function segment(plan, a, b, ms, state, hidden, owner)
  local start = plan.total
  plan.total = start + ms
  plan[#plan + 1] = {a = a, b = b, start = start, finish = plan.total,
    state = state or "fly", hidden = hidden or false, owner = owner}
end

local function path_segments(plan, path, reverse)
  if reverse then
    for i = #path, 2, -1 do
      segment(plan, path[i].pos, path[i-1].pos, duration(path[i].pos, path[i-1].pos),
        "fly", path[i].hidden, path[i-1].owner)
    end
  else
    for i = 2, #path do
      segment(plan, path[i-1].pos, path[i].pos, duration(path[i-1].pos, path[i].pos),
        "fly", path[i].hidden, path[i].owner)
    end
  end
end

local function pit_segments(plan, pit, landing)
  local first = MulDivRound(landing and F.LandingTime or F.LaunchTime,
    pit[1]:Dist(pit[2]), Max(1, pit[1]:Dist(pit[2]) + pit[2]:Dist(pit[3])))
  if landing then
    segment(plan, pit[3], pit[2], Max(1, F.LandingTime-first))
    segment(plan, pit[2], pit[1], Max(1, first))
  else
    segment(plan, pit[1], pit[2], Max(1, first))
    segment(plan, pit[2], pit[3], Max(1, F.LaunchTime-first))
  end
  plan[#plan-1].pit = true
  plan[#plan].pit = true
end

function F.Remove(old)
  if old then visuals[old] = nil end
  if old and IsValid(old.drone) then
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
    removed = active.removed, now = GameTime()}
end

-- L4 may keep ephemeral records outside objects and sample any number of visuals.
-- It owns their registry, save teardown, pending data and completion authority.
function F.Update(a, now)
  if not a then return false end
  if save_gate or not hub_ok(a.hub) or not live(a.drone) or a.drone.command_center ~= a.hub
    or a.drone.command then F.Remove(a); return false end
  a.drone.battery = a.drone.battery_max
  local elapsed = Max(0, (now or GameTime()) - a.started)
  local step
  for _, s in ipairs(a.plan) do
    if elapsed < s.finish then step = s; break end
  end
  if not step then
    if a.remove then a.drone:LandingEnd(); F.Remove(a); return false end
    a.phase = "hover"
    a.drone:SetPos(a.pit[3])
    return true
  end
  if step.owner and not live(step.owner) then F.Remove(a); return false end
  if a.step ~= step then
    a.drone:StopFX()
    a.step = step
    a.phase = step.state
    a.drone:SetState(step.state)
    a.drone:SetVisible(not step.hidden)
    if step.state == "constructStart" or step.state == "constructIdle" then
      a.drone:StartFX("Construct", live(a.target) and a.target or nil)
    end
    if step.a:x() ~= step.b:x() or step.a:y() ~= step.b:y() then
      a.drone:SetAngle(CalcOrientation(step.a, step.b))
    end
  end
  local t, span = Clamp(elapsed-step.start, 0, step.finish-step.start), step.finish-step.start
  local function axis(x, y) return x + MulDivRound(y-x, t, span) end
  a.drone:SetPos(point(axis(step.a:x(), step.b:x()), axis(step.a:y(), step.b:y()), axis(step.a:z(), step.b:z())))
  return true
end

function F.Sample()
  if active and not F.Update(active) then active = false end
end

local function start_driver()
  if IsValidThread(driver) then return end
  driver = CreateRealTimeThread(function()
    while SMROptInHubFlight do
      SMROptInHubFlight.Sample()
      Sleep(SMROptInHubFlight.SampleTime)
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
  if F.Palette then Building.SetPalette(drone, table.unpack(F.Palette)) end
  local plan = {total = 0}
  pit_segments(plan, pit, false)
  local record = {hub = hub, drone = drone, pit = pit, plan = plan, started = started or GameTime(), phase = "launch"}
  visuals[record] = true
  return record
end

function SpawnHubDrone(hub)
  if save_gate then return nil, "Save in progress" end
  if active and live(active.drone) then return active.drone, F.Status() end
  F.Clear()
  local record, reason = F.Create(hub or SelectedObj)
  if not record then return nil, reason end
  active = record
  start_driver()
  return active.drone, F.Status()
end

function F.Send(record, target, keep_start)
  if save_gate then return nil, "Save in progress" end
  if not record or not live(record.drone) then return nil, "No live flight" end
  if record.target == target then return record end
  if record.target then return nil, "Return the current flight first" end
  local path, reason = F.Route(record.hub, target)
  if not path then return nil, reason end
  local drone = record.drone
  -- Finish the existing launch first, using its original deadline (no floor teleport).
  local plan = {total = 0}
  local start = record.started
  pit_segments(plan, record.pit, false)
  local wait = keep_start and 0 or Max(0, GameTime()-start-plan.total)
  if wait > 0 then segment(plan, path[1].pos, path[1].pos, wait) end
  path_segments(plan, path, false)
  local arrival = start + plan.total
  local pos = path[#path].pos
  segment(plan, pos, pos, Max(1, drone:GetAnimDuration("constructStart")), "constructStart")
  segment(plan, pos, pos, F.WorkTime, "constructIdle")
  segment(plan, pos, pos, Max(1, drone:GetAnimDuration("constructEnd")), "constructEnd")
  local work_done = start + plan.total
  path_segments(plan, path, true)
  pit_segments(plan, record.pit, true)
  record.plan, record.target, record.remove = plan, target, true
  record.arrival, record.work_done, record.removed = arrival, work_done, start + plan.total
  record.step = false
  return record
end

function SendHubDroneTo(target, hub)
  if save_gate then return nil, "Save in progress" end
  target = target or SelectedObj
  hub = hub or (active and active.hub)
  if active and active.hub ~= hub then return nil, "Prototype already belongs to another hub" end
  -- Validate before creating any visual, so an isolated target cannot leave one behind.
  local path, reason = F.Route(hub, target)
  if not path then return nil, reason end
  local drone, err = SpawnHubDrone(hub)
  if not drone then return nil, err end
  local record, why = F.Send(active, target)
  if not record then return nil, why end
  return drone, F.Status()
end

function ReturnHubDrone()
  if not active then return true end
  if active.returning then return active.drone, F.Status() end
  -- Retrace only the actually traversed movement segments, including hidden tunnel legs.
  F.Sample()
  if not active then return true end
  local a, plan, now = active, {total = 0}, GameTime()
  if a.work_done and now >= a.work_done then
    a.returning = true
    return a.drone, F.Status()
  end
  local elapsed = now-a.started
  local movements = {}
  for _, s in ipairs(a.plan) do
    if s.start >= elapsed then break end
    if s.state == "fly" then movements[#movements+1] = s end
    if elapsed < s.finish then break end
  end
  local pos = a.drone:GetPos()
  for i = #movements, 1, -1 do
    local s = movements[i]
    -- Reverse the full prefix, even if already inbound: no off-track shortcut.
    local ms = duration(pos, s.a)
    if s.pit then
      local full_distance = Max(1, s.a:Dist(s.b))
      ms = Max(1, MulDivRound(MulDivRound(s.finish-s.start, F.LandingTime, F.LaunchTime),
        pos:Dist(s.a), full_distance))
    end
    segment(plan, pos, s.a, ms, "fly", s.hidden, s.owner)
    pos = s.a
  end
  a.drone:StopFX()
  a.plan, a.started, a.remove, a.returning, a.step = plan, now, true, true, false
  a.arrival, a.work_done, a.removed = false, false, now+plan.total
  return a.drone, F.Status()
end

function SetHubDroneTune(name, value)
  if active then return false, "Return the prototype before changing its constants" end
  local tuneable = {HoverHeight = true, Speed = true, LaunchTime = true, LandingTime = true, WorkTime = true}
  if not tuneable[name] or type(value) ~= "number" or value <= 0 or value ~= math.floor(value) then
    return false, "Use a named flight constant and a positive integer" end
  F[name] = value
  return true
end

function OnMsg.SaveGameStart() save_gate = true; F.ClearAll() end
function OnMsg.SaveGameDone() save_gate = false end
function OnMsg.LoadGame() F.ClearAll(); save_gate = false end
function OnMsg.DoneGame()
  F.ClearAll(); save_gate = false
end
