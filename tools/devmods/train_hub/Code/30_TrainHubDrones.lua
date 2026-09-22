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
  HoverHeight = 300,        -- GUESS safety buffer above the guessed train envelope
  OverTrackHeight = 1200,   -- GUESS train envelope above rail; total ride offset = this + buffer
  FixHeight = 100,          -- GUESS work origin above the target element, not cruise altitude
  UnderDeckHeight = 300,    -- entity-local z; native-scale mesh measured by exit_clearance.py
  OutwardDistance = 9000,   -- radius from hub origin before climbing, beyond arms/platforms
  ClimbRate = 1500,         -- GUESS nominal vertical rate for deadline budgeting
  TransferHeight = 2500,    -- entity-local z for crossing back above the hub after outside climb
  ExitDirectionX = -866, ExitDirectionY = -500, -- /1000; generator 30-degree pillar gap
  Speed = 6000,             -- engine units per game second; GUESS
  LaunchTime = 3000,        -- game ms, floor -> rim -> OI-25 crest
  LandingTime = 3000,       -- game ms, OI-25 crest -> rim -> floor
  WorkTime = 5000,          -- game ms in constructIdle, excludes start/end animations
  PitOffsetX = -310, PitOffsetY = 180, PitExitZ = 1000, -- OI-25, entity local
  BatteryMax = 800000,
  Palette = false,          -- optional array of four colours, L3 visual verdict
  SampleTime = 20,          -- real ms; position and deadlines use GameTime(), not wall time
  TurnRadius = 300,         -- GUESS maximum corner trim, units (not lateral lane offset)
  BlendTime = 400,          -- GUESS full velocity-blend window, game ms
  AccelTime = 400,          -- GUESS start/stop easing window, game ms; deadlines win
  HeadingTime = 400,        -- GUESS yaw/roll response time, game ms
  BankAngle = 180,          -- GUESS maximum bank in angle minutes; 0 disables bank
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
        local z = Max(high:z(), first:z())
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

local function duration(a, b)
  -- Budget time by vertical and total distance. Eased starts/stops can peak at
  -- 4/3 nominal speed within that fixed budget; these are not physics speed caps.
  return Max(Max(1, MulDivRound(a:Dist(b), 1000, F.Speed)),
    MulDivRound(math.abs(b:z()-a:z()), 1000, F.ClimbRate))
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

-- Deadline-owned curves, independent of the engine path solver. Ordinary corners
-- use a quadratic Bezier with matching incoming/outgoing velocities. Reversals,
-- work and visibility boundaries reach the exact waypoint with zero velocity.
-- All control points lie on the original legs: the convex hull bounds clearance.
local function mix(a, b, t)
  return {a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t, a[3]+(b[3]-a[3])*t}
end
local function xyz(p) return {p:x(), p:y(), p:z()} end
local function length(v) return math.sqrt(v[1]^2+v[2]^2+v[3]^2) end
local function velocity(s)
  local dt = s.finish-s.start
  return {(s.b[1]-s.a[1])/dt, (s.b[2]-s.a[2])/dt, (s.b[3]-s.a[3])/dt}
end
local function offset(p, v, dt) return {p[1]+v[1]*dt,p[2]+v[2]*dt,p[3]+v[3]*dt} end

function F.PrepareMotion(plan)
  local edges, curves = {}, {}
  local pending=0
  for index, s in ipairs(plan) do
    local previous = edges[#edges]
    local following=plan[index+1]
    -- Duplicate route vertices retain their milliseconds, without a spurious stop.
    if s.state == "fly" and s.a:Dist(s.b) == 0 and previous
      and s.finish-s.start==1 and following and following.state=="fly"
      and previous.state == "fly" and previous.hidden == s.hidden
      and following.hidden==s.hidden then
      -- Share the duplicate's millisecond symmetrically: reverse uses the same
      -- curve. A real hover wait remains a stationary edge with a full stop.
      previous.finish=previous.finish+.5
      pending=pending+.5
    else
      edges[#edges+1] = {a=xyz(s.a), b=xyz(s.b), start=s.start-pending, finish=s.finish,
        state=s.state, hidden=s.hidden}
      pending=0
    end
  end
  local joins = {}
  for i=1,#edges-1 do
    local a,b = edges[i],edges[i+1]
    local va,vb = velocity(a),velocity(b)
    local la,lb = length(va),length(vb)
    local dot = va[1]*vb[1]+va[2]*vb[2]+va[3]*vb[3]
    if la>0 and lb>0 and a.hidden==b.hidden and dot > -.95*la*lb then
      joins[i] = Min(F.BlendTime/2, (a.finish-a.start)/4, (b.finish-b.start)/4,
        F.TurnRadius/Max(la,lb))
    end
  end
  local function add(t0,t1,points)
    if t1>t0 then curves[#curves+1]={start=t0,finish=t1,points=points} end
  end
  for i,s in ipairs(edges) do
    local v=velocity(s)
    local w0=joins[i-1] or Min(F.AccelTime,(s.finish-s.start)/4)
    local w1=joins[i] or Min(F.AccelTime,(s.finish-s.start)/4)
    local a,b=offset(s.a,v,w0),offset(s.b,v,-w1)
    if not joins[i-1] then
      add(s.start,s.start+w0,{s.a,s.a,offset(a,v,-w0/3),a})
    end
    add(s.start+w0,s.finish-w1,{a,b})
    if joins[i] then
      add(s.finish-w1,s.finish+w1,{b,s.b,offset(s.b,velocity(edges[i+1]),w1)})
    else
      add(s.finish-w1,s.finish,{b,offset(b,v,w1/3),s.b,s.b})
    end
  end
  plan.motion=curves
  return curves
end

-- Public pure sampler: tests/clearance and L4 reconstruction use the same curve.
local function recall_time(plan,t)
  local brake=plan.brake
  if t<brake then return plan.turnaround-(brake-t)^2/(2*brake) end
  t=t-brake
  if t<brake then return plan.turnaround-t*t/(2*brake) end
  return Max(0,plan.turnaround-t+brake/2)
end
function F.Position(plan, elapsed)
  if plan.source then return F.Position(plan.source,recall_time(plan,elapsed)) end
  local curves=plan.motion or F.PrepareMotion(plan)
  local selected=curves[#curves]
  for _,c in ipairs(curves) do if elapsed<c.finish then selected=c; break end end
  if not selected then return nil end
  local p=selected.points
  local u=Clamp((elapsed-selected.start)/(selected.finish-selected.start),0,1)
  local q={}
  for i,v in ipairs(p) do q[i]=v end
  for n=#q-1,1,-1 do for i=1,n do q[i]=mix(q[i],q[i+1],u) end end
  return point(math.floor(q[1][1]+.5),math.floor(q[1][2]+.5),math.floor(q[1][3]+.5))
end

local function render(a, elapsed, step)
  local drone=a.drone
  if a.sampled==elapsed then return end -- pause: leave game-time interpolation alone
  local dt=a.sampled and Clamp(elapsed-a.sampled,1,100) or F.SampleTime
  local until_time=Min(elapsed+dt,step and step.finish or a.plan.total)
  if a.plan.source then
    until_time=Min(until_time,a.plan.total)
    local function same_visibility(t)
      local original=recall_time(a.plan,t)
      for _,s in ipairs(a.plan.source) do
        if original<s.finish then return s.hidden==(a.step and a.step.hidden or false) end
      end
      return true
    end
    -- Do not predict a visible chord beyond a tunnel's concealment boundary.
    if not same_visibility(until_time) then
      local lo,hi=elapsed,until_time
      for _=1,12 do local mid=(lo+hi)/2
        if same_visibility(mid) then lo=mid else hi=mid end
      end
      until_time=math.floor(lo)
    end
  end
  local pos=F.Position(a.plan,elapsed)
  -- First/rebuilt frame or a missed prediction catches up to absolute time.
  -- Ordinary ticks start where the previous interpolation ended.
  if a.predicted~=elapsed then drone:SetPos(pos) end
  local target=F.Position(a.plan,until_time)
  local direction=F.Position(a.plan,Min(a.plan.total,elapsed+F.HeadingTime))
  local yaw=a.yaw or drone:GetAngle()
  local delta=0
  if direction:x()~=pos:x() or direction:y()~=pos:y() then
    delta=(CalcOrientation(pos,direction)-yaw+10800)%21600-10800
  end
  local blend=dt/(F.HeadingTime+dt)
  local turn=delta*blend
  a.yaw=(yaw+turn)%21600
  local bank=Clamp(-turn*1000/Max(1,dt),-F.BankAngle,F.BankAngle)
  a.bank=(a.bank or 0)+(bank-(a.bank or 0))*blend
  -- Build 24995074: GameObject.lua:707; Train.lua:495 uses timed
  -- SetRollPitchYaw. ComponentInterpolation is used; curvature stays OFF
  -- so the engine cannot bow the measured hull or choose another route.
  local time=Max(0,until_time-elapsed)
  drone:SetPos(target,time)
  drone:SetRollPitchYaw(math.floor(a.bank+.5),0,math.floor(a.yaw+.5),Max(1,dt))
  a.sampled,a.predicted=elapsed,until_time
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
    or a.drone.command or a.drone.run_cmd_on_land then F.Remove(a); return false end
  a.drone.battery = a.drone.battery_max
  local elapsed = Max(0, (now or GameTime()) - a.started)
  local sampled_plan, sampled_time=a.plan,elapsed
  if a.plan.source then
    if elapsed>=a.plan.total then a.drone:LandingEnd(); F.Remove(a); return false end
    sampled_plan,sampled_time=a.plan.source,recall_time(a.plan,elapsed)
  end
  local step
  for _, s in ipairs(sampled_plan) do
    if sampled_time < s.finish then step = s; break end
  end
  if not step then
    if a.remove then a.drone:LandingEnd(); F.Remove(a); return false end
    a.phase = "hover"
    render(a, a.plan.total)
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
  end
  -- A recalled flight reads visibility/owner from the original curve's time.
  -- Its render horizon cannot use a forward trip's semantic timestamp.
  if a.plan.source then render(a,elapsed) else render(a,elapsed,step) end
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
  drone:SetCurvature(false)
  drone:SetAcceleration(0)
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
  record.step,record.predicted = false,false
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
  local a, now = active, GameTime()
  if a.work_done and now >= a.work_done then
    a.returning = true
    return a.drone, F.Status()
  end
  local elapsed = Min(now-a.started,a.arrival and a.arrival-a.started or a.plan.total)
  -- Brake along the same curve, then play its prefix backwards. No new chord
  -- across the rounded corner. Never brake into work or across a visibility seam.
  local limit=a.arrival and a.arrival-a.started or a.plan.total
  for _,s in ipairs(a.plan) do
    if s.finish>elapsed and s.hidden~=(a.step and a.step.hidden or false) then
      limit=Min(limit,s.start); break
    end
  end
  local brake=Min(F.AccelTime,2*Max(0,limit-elapsed))
  local turnaround=Min(limit,elapsed+brake/2)
  local plan={source=a.plan,brake=brake,turnaround=turnaround,
    total=math.ceil(turnaround+brake*1.5)}
  a.drone:StopFX()
  a.plan, a.started, a.remove, a.returning, a.step = plan, now, true, true, false
  a.arrival, a.work_done, a.removed = false, false, now+plan.total
  a.sampled,a.predicted=false,false
  return a.drone, F.Status()
end

function SetHubDroneTune(name, value)
  if active then return false, "Return the prototype before changing its constants" end
  local tuneable = {HoverHeight = true, OverTrackHeight = true, FixHeight = true,
    UnderDeckHeight = true, OutwardDistance = true, ClimbRate = true, TransferHeight = true,
    Speed = true, LaunchTime = true, LandingTime = true, WorkTime = true,
    TurnRadius=true, BlendTime=true, AccelTime=true, HeadingTime=true, BankAngle=true}
  if not tuneable[name] or type(value) ~= "number" or value < (name=="BankAngle" and 0 or 1)
    or value ~= math.floor(value) or (name=="BankAngle" and value>300) then
    return false, "Use a named positive integer; BankAngle allows 0..300 angle minutes" end
  F[name] = value
  return true
end

function OnMsg.SaveGameStart() save_gate = true; F.ClearAll() end
function OnMsg.SaveGameDone() save_gate = false end
function OnMsg.LoadGame() F.ClearAll(); save_gate = false end
function OnMsg.DoneGame()
  F.ClearAll(); save_gate = false
end
