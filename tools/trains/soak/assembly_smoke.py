"""Desk smoke for the composed SOAK slots: real SMRTK 70/74 dispatch, a mock colony, no game.

What it proves: the composed file loads with no arm, thread or mutation; slots 1-3 bind and
refuse correctly; the soak's stream, flag/clear lifecycle, confirmation delay, per-tick and
per-hour caps, autosave survival and load stop behave as designed; every engine integer
helper receives integers and the source has no bare division (EF-116: lupa divides to floats,
the engine does not). What it cannot prove: any game behaviour or field the mock invents.

    python tools/trains/soak/assembly_smoke.py
"""
from pathlib import Path
import re
import sys
from lupa import LuaRuntime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KIT = ROOT.parent / "SMR-BugFixPack-TestKit"
COMPOSED = HERE / "80_AgentSlots_soak.lua.txt"
INSTALLED = KIT / "Code" / "80_AgentSlots.lua"

source = COMPOSED.read_text(encoding="utf-8")


# ---- source gates -------------------------------------------------------------------------------
def code_only(text):
    """Strip Lua comments and string literals, keep code."""
    out, i, n = [], 0, len(text)
    while i < n:
        if text.startswith("--", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text[i] in "\"'":
            q, i = text[i], i + 1
            while i < n and text[i] != q:
                i += 2 if text[i] == "\\" else 1
            i += 1
            out.append('""')
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


code = code_only(source)
bare_div = [m.start() for m in re.finditer(r"(?<!/)/(?!/)", code)]
assert not bare_div, "bare division in slot code: %r" % [code[max(0, k - 30):k + 10] for k in bare_div]
assert "TEMPORARY" not in source
assert not re.search(r"^\s*print\(", source, re.M)
assert not re.search(r"NetSyncEvent|LogCheatUsed", source)
assert not re.search(r"CreateGameTimeThread|T\.Arm\(|T\.Trigger", code), "no game-time thread, arm or trigger"
assert source.splitlines()[0].startswith("-- SITTING: pre-launch train logistics SOAK")
# positive control: the gate regex does catch a bare division
assert re.search(r"(?<!/)/(?!/)", code_only("local x = a / b -- c / d")), "gate control failed"

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
log_lines = {}
handlers = {}
OnMsg = setmetatable({}, { __newindex = function(t, k, v)
  handlers[k] = handlers[k] or {}; table.insert(handlers[k], v) end })
function Msg(name, ...) for _, f in ipairs(handlers[name] or {}) do f(...) end end
function ModLog(line) table.insert(log_lines, line) end
function ConsolePrint() end
function FlushLogFile() flushes = (flushes or 0) + 1 end
empty_table = setmetatable({}, { __newindex = function() error("write to empty_table") end })
game_time = 0
function GameTime() return game_time end
const = { HourDuration = 30000, MinuteDuration = 500, ResourceScale = 1000 }
local function ints(name, ...)
  for i = 1, select("#", ...) do
    local v = select(i, ...)
    assert(math.type(v) == "integer", name .. " argument " .. i .. " is " .. tostring(math.type(v)) .. " " .. tostring(v))
  end
end
function MulDivRound(a, b, c)
  ints("MulDivRound", a, b, c)
  local p = a * b
  local s = (p < 0) ~= (c < 0) and -1 or 1
  p, c = math.abs(p), math.abs(c)
  return s * ((p + c // 2) // c)
end
function Min(a, b) ints("Min", a, b) return a < b and a or b end
function Max(a, b) ints("Max", a, b) return a > b and a or b end
function Clamp(v, lo, hi) ints("Clamp", v, lo, hi) return v < lo and lo or v > hi and hi or v end
function IsValid(o) return type(o) == "table" and o.handle ~= nil and not o.dead end
parents = { SMROptInTrainHubBase = "Station", SMROptInElevatorDepotDevBase = "Station",
  StationSmall = "Station", SMROptInTrainHub6 = "SMROptInTrainHubBase",
  SMROptInElevatorDepotDev = "SMROptInElevatorDepotDevBase", HubTrain = "Train" }
function IsKindOf(o, k)
  if type(o) ~= "table" then return false end
  local c = o.class
  while c do if c == k then return true end c = parents[c] end
  return false
end
function GetEnvironment(map) return map == "ug" and "Underground" or "Surface" end
-- threads: real-time threads are coroutines the test resumes one poll at a time
threads = {}
function CreateRealTimeThread(fn, ...)
  local co = coroutine.create(fn); table.insert(threads, co)
  local ok, err = coroutine.resume(co, ...)
  assert(ok, err)
  return co
end
function CreateGameTimeThread() error("game-time thread created") end
function Sleep() coroutine.yield() end
function IsValidThread(co) return type(co) == "thread" and coroutine.status(co) ~= "dead" end
function DeleteThread(co) if coroutine.status(co) == "suspended" then coroutine.close(co) end end
function CurrentThread() return coroutine.running() end
function poll_all()
  for _, co in ipairs(threads) do
    if coroutine.status(co) == "suspended" then
      local ok, err = coroutine.resume(co); assert(ok, err)
    end
  end
end
function live_threads()
  local n = 0
  for _, co in ipairs(threads) do if coroutine.status(co) == "suspended" then n = n + 1 end end
  return n
end
function RGBA() return 0 end
SMRTK = { Page = function() end, Button = function() end, ControlRow = function() end }
''')

lua.execute((KIT / "Code/70_SMRTK_Core.lua").read_text(encoding="utf-8-sig"))
lua.execute((KIT / "Code/74_SMRTK_Agent.lua").read_text(encoding="utf-8-sig"))
lua.execute((KIT / "Code/76_SMRTK_Kit.lua").read_text(encoding="utf-8-sig"))

# The mock colony. Field names are the shipping code's (soak_slots.lua.txt header lists files).
lua.execute(r'''
local T = SMRTK
speed_calls = {}
T.Action { id = "speed", verb = "SPEED", run = function(ctx, n) table.insert(speed_calls, n); return { requested = n } end }
T.Action { id = "speed_ultra", verb = "SPEED", run = function() table.insert(speed_calls, 128); return { requested = 128, factor = 128000 } end }
function GetGameSpeed() return speed_calls[#speed_calls] == 0 and "pause" or "play" end

local function request(actual, desired, target)
  return { actual = actual, desired = desired, target = target or actual,
    GetActualAmount = function(self) return self.actual end,
    GetDesiredAmount = function(self) return self.desired end,
    GetTargetAmount = function(self) return self.target end }
end
local next_handle = 100
local function obj(class, fields)
  next_handle = next_handle + 1
  local o = fields or {}
  o.class, o.handle = class, o.handle or next_handle
  o.GetMap = function(self) return self.map or "surface" end
  return o
end
local function depot_like(class, cap, resources, map)
  local o = obj(class, { storable_resources = resources, supply = {}, demand = {}, cap = cap, map = map,
    working = true, desired_amount = 10000, enabled = {} })
  for _, res in ipairs(resources) do
    o.supply[res] = request(0, 10000)
    o.demand[res] = request(0, cap - 10000)
    o.enabled[res] = true
  end
  o.GetMaxStorage = function(self, res) return self.cap end
  o.GetMaxStorageForAnyOneResource = function(self) return self.cap end
  o.IsResourceEnabled = function(self, res) return self.enabled[res] end
  return o
end
make_station = function(cap, map) return depot_like("StationSmall", cap or 60000, { "Metals", "Food" }, map) end

colony = { SMROptIn_hub_upgrades = { SMROptInTrainHub6_CapacityNetwork = { on = true } } }
city = { colony = colony, labels = { Station = {}, Train = {} } }
hub = depot_like("SMROptInTrainHub6", 1000000, { "Metals", "Food" })
hub.city, hub.ui_working, hub.drones = city, true, {}
hub.electricity_production, hub.electricity_consumption = 75000, 10000
hub.base_max_storage_per_resource = 1000000
hub.upgrade_on_off_state = { SMROptInTrainHub6_CapacityNetwork = true }
hub.GetMaxDrones = function() return 60 end
hub.HasUpgrade = function(self, id) return colony.SMROptIn_hub_upgrades[id] ~= nil end
hub.IsUpgradeOn = function(self, id) local e = colony.SMROptIn_hub_upgrades[id]; return e and e.on or false end
hub.SMROptIn_track_work = { jobs = {} }
st1 = make_station(); st2 = make_station(); st3 = make_station()
surface = depot_like("SMROptInElevatorDepotDev", 250000, { "Metals", "Food" })
underground = depot_like("SMROptInElevatorDepotDev", 250000, { "Metals", "Food" }, "ug")
surface.SMROptIn_depot_cabin = { phase = "down", ends = 1000000000, cargo = { Metals = 50000 }, legs = 4, started = true }
surface.SMROptIn_depot_rows = { Metals = "to_underground", Food = "to_surface" }
underground.SMROptIn_depot_rows = { Metals = "to_underground", Food = "to_surface" }
for _, o in ipairs({ hub, st1, st2, st3, surface, underground }) do table.insert(city.labels.Station, o) end
local function train(at, command)
  local t = obj("Train", { current_station = at, command = command, stockpiled_amount = {},
    max_shared_storage = 42000, at_station = true, x = 1000, y = 2000 })
  t.GetPos = function(self) return { x = function() return self.x end, y = function() return self.y end } end
  return t
end
make_train = train
t_idle = train(st1, "Idle"); t_move = train(st2, "Idle")
table.insert(city.labels.Train, t_idle); table.insert(city.labels.Train, t_move)
Cities = { city }
UIColony = { day = 5 }
CurrentMap = "Mars"

rows = { [st1] = { Metals = { mode = "export", percent = 20 } }, [st2] = { Metals = { mode = "balanced", percent = 30 } } }
SMROptInTrainDistribution = { active = true, ExportPairingStats = { capped = 0, retried = 0, substituted = 0, refused = 0 },
  RowsOn = function(st) return true end,
  Get = function(st, res) return rows[st] and rows[st][res], hub end,
  HubFor = function(st) return hub end, Parent = function(st) return hub end }
-- desired amounts the code writes (Station.lua:964-995 via D.Apply): export 20% of 60
st1.supply.Metals.desired, st1.demand.Metals.desired = 60000, 0
st2.supply.Metals.desired, st2.demand.Metals.desired = 18000, 42000
local hw = { [surface] = { Metals = "gather", Food = "hand_out" }, [underground] = { Metals = "hand_out", Food = "gather" } }
local policy = { gather = "send", hand_out = "accept" }
for o, words in pairs(hw) do
  o.transport_policy = {}
  for res, w in pairs(words) do
    o.transport_policy[res] = policy[w]
    if w == "gather" then o.supply[res].desired, o.demand[res].desired = 250000, 0
    else o.supply[res].desired, o.demand[res].desired = 0, 250000 end
  end
end
SMRElevatorDepot = { CABIN = "SMROptIn_depot_cabin", ROWS = "SMROptIn_depot_rows", DRONES = "SMROptIn_depot_drones",
  CAPACITY_UPGRADE = "SMROptInElevatorDepotDev_Capacity",
  PairOf = function() return surface, underground end,
  IsDepot = function(o) return o == surface or o == underground end,
  CabinCapacity = function() return 250 end,
  HalfWord = function(o, res) return hw[o][res] end,
  State = function(o, res) return surface.SMROptIn_depot_rows[res] end,
  WordOf = function(s) return s == "to_surface" and "export" or "import" end }
SMROptInTrainBay = { stats = { refused = 0 } }
SMROptInTrainFloor = { stats = {}, HubRepairTune = { FlightGrace = 100 } }
SMROptInPack = { TrainTrace = false, IsActive = function(id) return true end,
  OptionEnabled = function() return true end, PackVersion = function() return "0.9.0" end }
''')

# Load the composed slots: nothing may arm, run or mutate.
before = len(lua.globals().log_lines)
lua.execute(source)
G = lua.globals()
T = G.SMRTK
assert G.SMROptInPack.TrainTrace is False, "load changed the trace"
assert lua.eval("next(SMRTK.armed) == nil"), "load armed something"
assert lua.eval("live_threads()") == 0, "load started a thread"
assert lua.eval("SMRTK.actions.slot_scratch == nil"), "scratch should stay unbound"
for n in range(4, 13):
    assert lua.eval("SMRTK.actions.slot_%d == nil" % n), "slot %d should be unbound" % n
labels = {n: lua.eval("SMRTK.actions.slot_%d.label" % n) for n in (1, 2, 3)}
assert labels[1].startswith("SOAK OFF") and labels[2].startswith("Read now") and labels[3].startswith("Run Ultra")
assert lua.eval("SMRTK.slots[1] == 'slot_1' and SMRTK.slots[2] == 'slot_2' and SMRTK.slots[3] == 'slot_3'")
assert lua.eval("SMRTK.slots[4] == nil")
assert lua.eval("type(SMRTK.actions.slot_1.arm)") == "nil", "slot 1 is a once action, not an armed one"
# the preloaded probe sweep passes the kit's own probe_preflight validation when stamped live
ok = lua.eval('''(function()
  local e = SMRTK.kit.sweep_preload
  local stamp = {}
  for k, v in pairs(e) do stamp[k] = v end
  SMRTK.session, LuaRevision, CurrentMap = "s1", 406343, "Mars"
  stamp.session, stamp.sitting, stamp.game = SMRTK.session, SMRTK.kit.sitting, LuaRevision
  local ok, f = SMRTK.Run("probe_preflight", stamp)
  return ok and f.clean == true and f.exit == 1 and f.hits == 0
end)()''')
assert ok, "preloaded sweep refused by probe_preflight"


def lines(verb=None, start=0):
    out = []
    for i in range(start + 1, len(G.log_lines) + 1):
        line = G.log_lines[i]
        if verb is None or ("SMRTK_" + verb + " ") in line:
            out.append(line)
    return out


def field(line, key):
    m = re.search(r"\b%s=(\"(?:[^\"\\]|\\.)*\"|\S+)" % re.escape(key), line)
    return m and m.group(1)


def run(slot):
    return lua.eval('(function() local ok, f = SMRTK.Run("slot_%s"); return ok, f.status, f.reason end)()' % slot)


def advance(ms, polls=1):
    for _ in range(polls):
        lua.execute("game_time = game_time + %d" % (ms // polls))
        lua.execute("poll_all()")


HOUR = 30000

# refusals
lua.execute("saved_colony = UIColony; UIColony = nil")
ok, status, reason = run(1)
assert not ok and status == "REFUSED" and "load a colony" in reason
ok, status, reason = run(2)
assert not ok and status == "REFUSED"
lua.execute("UIColony = saved_colony; saved_pack = SMROptInPack; SMROptInPack = nil")
ok, status, reason = run(1)
assert not ok and "Opt-In registry missing" in reason
lua.execute("SMROptInPack = saved_pack")
assert lua.eval("live_threads()") == 0

# Read now with the soak off
mark = len(G.log_lines)
ok, status, _ = run(2)
assert ok, status
read = lines(start=mark)
assert len(lines("SOAK_READ", mark)) == 1 and len(lines("SOAK_TOTALS", mark)) == 1
assert len(lines("SOAK_HUB", mark)) == 1 and len(lines("SOAK_DEPOT", mark)) == 1
assert len(lines("SOAK_STATION", mark)) == 3 and len(lines("SOAK_TRAIN", mark)) == 2
assert G.SMROptInPack.TrainTrace is False and lua.eval("live_threads()") == 0
tot = lines("SOAK_TOTALS", mark)[0]
# hub 0 + stations 0 + cabin 50 Metals = 50.0
assert field(tot, "all") == "Metals:50.0", tot
st1_line = [l for l in lines("SOAK_STATION", mark) if "StationSmall(%d)" % lua.eval("st1.handle") in l][0]
assert "Metals:export20:0.0:60.0:0.0" in st1_line, st1_line
depot = lines("SOAK_DEPOT", mark)[0]
assert field(depot, "phase") == "down" and field(depot, "aboard") == "Metals:50.0" and field(depot, "cabin_cap") == "250"

# Start the soak
mark = len(G.log_lines)
ok, status, _ = run(1)
assert ok, status
assert G.SMROptInPack.TrainTrace is True
assert lua.eval("live_threads()") == 1
assert lua.eval("SMRTK.actions.slot_1.label").startswith("SOAK is ON")
assert len(lines("SOAK_START", mark)) == 1 and len(lines("SOAK_FLAG", mark)) == 0
assert lua.eval("next(SMRTK.armed) == nil"), "the soak arms nothing"

# A quiet hour: totals, the queued baseline lines, no flags
mark = len(G.log_lines)
advance(HOUR, polls=4)
assert len(lines("SOAK_TOTALS", mark)) == 1, lines(start=mark)
assert len(lines("SOAK_STATION", mark)) == 3 and len(lines("SOAK_TRAIN", mark)) == 2
assert len(lines("SOAK_FLAG", mark)) == 0, lines("SOAK_FLAG", mark)

# Station desired mismatch: flagged only after the confirmation delay, once, then cleared
lua.execute("st1.supply.Metals.desired = 0")
mark = len(G.log_lines)
advance(HOUR)
assert len(lines("SOAK_FLAG", mark)) == 0, "flagged before confirmation"
advance(5000)
assert len(lines("SOAK_FLAG", mark)) == 0, "flagged inside the confirmation delay"
advance(20000)
f = lines("SOAK_FLAG", mark)
assert len(f) == 1 and field(f[0], "kind") == "station_desired_mismatch", f
assert field(f[0], "expected_supply") == "60.0" and field(f[0], "supply_desired") == "0.0"
advance(HOUR)
assert len(lines("SOAK_FLAG", mark)) == 1, "a standing condition must not repeat"
lua.execute("st1.supply.Metals.desired = 60000")
advance(HOUR)
c = lines("SOAK_CLEAR", mark)
assert len(c) == 1 and field(c[0], "kind") == "station_desired_mismatch", c
# a transient mismatch the rows repair within the delay is never flagged
mark = len(G.log_lines)
lua.execute("st2.supply.Metals.desired = 0")
advance(HOUR)
lua.execute("st2.supply.Metals.desired = 18000")
advance(25000)
assert len(lines("SOAK_FLAG", mark)) == 0

# Stuck train: a non-Idle train in one place for 3 game hours; the Idle train never
mark = len(G.log_lines)
lua.execute("t_move.command = 'GotoStation'")
advance(3 * HOUR, polls=3)
assert not [l for l in lines("SOAK_FLAG", mark) if field(l, "kind") == "train_stuck"], "flagged before 3 game hours"
advance(HOUR)
f = [l for l in lines("SOAK_FLAG", mark) if field(l, "kind") == "train_stuck"]
assert len(f) == 1 and "Train(%d)" % lua.eval("t_move.handle") in f[0], lines("SOAK_FLAG", mark)
assert "Train(%d)" % lua.eval("t_idle.handle") not in "".join(lines("SOAK_FLAG", mark)), "Idle is never stuck"
lua.execute("t_move.x = 9000")
advance(HOUR)
assert any(field(l, "kind") == "train_stuck" for l in lines("SOAK_CLEAR", mark))
lua.execute("t_move.command = 'Idle'")

# Hub over capacity: static overflow (a capacity drop, ruled fine) is quiet; a rise is flagged
mark = len(G.log_lines)
lua.execute("hub.cap = 2000000; hub.supply.Metals.actual = 1200000")
advance(HOUR)
lua.execute("hub.cap = 1000000")  # Storage Hub or Capacity Network switched off: stock now above cap
advance(HOUR)
advance(HOUR)
assert not [l for l in lines("SOAK_FLAG", mark) if field(l, "kind") == "hub_over_capacity"]
lua.execute("hub.supply.Metals.actual = 1250000")
advance(HOUR)
f = [l for l in lines("SOAK_FLAG", mark) if field(l, "kind") == "hub_over_capacity"]
assert len(f) == 1 and field(f[0], "stock") == "1250.0", f
lua.execute("hub.supply.Metals.actual = 0")

# Event flags: a train spawned in the hub, a bay refusal, a Lua error, a code error
mark = len(G.log_lines)
lua.execute("t_new = make_train(st3, 'LoadTrain'); table.insert(city.labels.Train, t_new)")
advance(100)
assert len(lines("SOAK_FLAG", mark)) == 0 and len(lines("SOAK_EVENT", mark)) == 1  # train_added
lua.execute("t_bad = make_train(hub, 'LoadTrain'); t_bad.at_spawn_track = true; table.insert(city.labels.Train, t_bad)")
lua.execute("SMROptInTrainBay.stats.refused = 2; SMRTK.error_count = SMRTK.error_count + 1")
lua.execute("SMROptInTrainDistribution.error = 'boom'")
advance(100)
kinds = sorted(field(l, "kind") for l in lines("SOAK_FLAG", mark))
assert kinds == ["bay_refused", "code_error", "lua_error", "train_in_hub"], kinds
advance(100)
assert len(lines("SOAK_FLAG", mark)) == 4, "event flags print once per change"
lua.execute("t_new.dead = true; t_bad.dead = true")
advance(100)
assert sum(field(l, "what") == "train_removed" for l in lines("SOAK_EVENT", mark)) == 2

# Depot: overdue cabin, rows copy differing (confirmed), stalled cabin
mark = len(G.log_lines)
lua.execute("surface.SMROptIn_depot_cabin.phase = 'down'; surface.SMROptIn_depot_cabin.ends = game_time - 20000")
lua.execute("underground.SMROptIn_depot_rows = { Metals = 'disabled', Food = 'to_surface' }")
advance(HOUR)
advance(25000)
kinds = sorted(field(l, "kind") for l in lines("SOAK_FLAG", mark))
assert kinds == ["cabin_overdue", "depot_rows_mismatch"], kinds

# Autosave: SMRTK disarms every armed action; the soak keeps streaming and logs the save
mark = len(G.log_lines)
lua.execute("SavingGame = true; Msg('SaveGameStart', { autosave = true })")
advance(HOUR)
assert len(lines("SOAK_TOTALS", mark)) == 0, "no reads while saving"
lua.execute("SavingGame = false; Msg('SaveGameDone', 'autosave', true, nil); Msg('SavegameSaved', 'autosave')")
advance(HOUR)
ev = [field(l, "what") for l in lines("SOAK_EVENT", mark)]
assert "save_start" in ev and "save_done" in ev, ev
assert len(lines("SOAK_TOTALS", mark)) == 1 and lua.eval("live_threads()") == 1

# Per-hour flag cap: 40 new stuck trains print 30 flags, the rest are counted
mark = len(G.log_lines)
lua.execute("for i = 1, 40 do table.insert(city.labels.Train, make_train(st3, 'WaitForTrack')) end")
advance(100)
advance(4 * HOUR, polls=4)
f = lines("SOAK_FLAG", mark)
assert len(f) == 30 and all(field(l, "kind") == "train_stuck" for l in f), [field(l, "kind") for l in f]
assert any(int(field(l, "suppressed")) == 10 for l in lines("SOAK_TOTALS", mark))

# Line budget: one hour tick prints at most 40 queued station/train lines
per_tick = []
for _ in range(14):
    m0 = len(G.log_lines)
    advance(HOUR)
    per_tick.append(len(lines("SOAK_STATION", m0)) + len(lines("SOAK_TRAIN", m0)))
assert max(per_tick) <= 40 and sum(per_tick) > 0, per_tick

# Slot 3: Ultra for N hours from the note box, then pause, flush and mark
lua.execute("SMRTK.agent_note = '2'")
mark = len(G.log_lines)
ok, status, _ = run(3)
assert ok, status
assert lua.eval("speed_calls[#speed_calls]") == 128
assert lua.eval("SMRTK.actions.slot_3.label").startswith("Ultra run in progress")
advance(HOUR)
assert lua.eval("speed_calls[#speed_calls]") == 128
advance(HOUR)
assert lua.eval("speed_calls[#speed_calls]") == 0, "run did not pause"
assert any(field(l, "what") == "run_done" for l in lines("SOAK_EVENT", mark))
assert any(field(l, "label") == "SOAK_RUN_DONE" for l in lines("MARK", mark))
# press during a run cancels the run, the soak stays on
ok, status, _ = run(3)
ok, status, _ = run(3)
assert ok and lua.eval("SMRTK.actions.slot_1.label").startswith("SOAK is ON")

# A load stops the soak visibly and restores the trace
mark = len(G.log_lines)
lua.execute("Msg('PreLoadGame')")
stop = lines("SOAK_STOP", mark)
assert len(stop) == 1 and field(stop[0], "reason") == "PreLoadGame", stop
assert G.SMROptInPack.TrainTrace is False
assert lua.eval("live_threads()") == 0
assert lua.eval("SMRTK.actions.slot_1.label").startswith("SOAK OFF")

# Manual on/off: final dump on stop
ok, status, _ = run(1)
assert ok and G.SMROptInPack.TrainTrace is True
mark = len(G.log_lines)
ok, status, _ = run(1)
assert ok and G.SMROptInPack.TrainTrace is False
assert len(lines("SOAK_STOP", mark)) == 1 and len(lines("SOAK_TOTALS", mark)) == 1
assert field(lines("SOAK_STOP", mark)[0], "reason") == "manual"

# Optional: --dump PATH writes the smoke's log as the game would ([mod] copy plus console copy)
# so soak_read.py can be exercised on it.
if "--dump" in sys.argv:
    out = Path(sys.argv[sys.argv.index("--dump") + 1])
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for i in range(1, len(G.log_lines) + 1):
            fh.write("[mod] " + G.log_lines[i] + "\n")
            fh.write(G.log_lines[i] + "\n")
        fh.write("[LUA ERROR] Mock/Error.lua:1: attempt to index a nil value\n")
        fh.write("[TrainBay] refused hub=50 track=9 t=100\n")

# The installed file, when present, is this composed file byte for byte
installed = INSTALLED.read_bytes() == COMPOSED.read_bytes() if INSTALLED.exists() else None
print("PASS: source gates (no bare division, no probe word, no print, no game-time thread/arm/trigger);"
      " load arms/starts/mutates nothing; slots 1-3 bound, 4-12 and Scratch unbound; refusals;"
      " read-now snapshot; start/stop trace switch; quiet hour; confirmed mismatch flag+clear and"
      " transient control; stuck train vs Idle control; static vs rising over-capacity; event flags"
      " (train in hub, bay refusal, Lua error, code error); depot cabin/rows flags; autosave survival;"
      " per-hour flag cap; per-tick line cap; Ultra run pause+flush+mark and cancel; load stop."
      " installed_matches_composed=%s; log lines in smoke=%d" % (installed, len(G.log_lines)))
