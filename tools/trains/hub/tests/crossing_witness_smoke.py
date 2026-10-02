"""Desk smoke for brief 33's crossing witness (80_AgentSlots_crossing.lua.txt), without launching Mars.

Transfers run through the archived vanilla Train bodies and the hub dev mod's real UnloadAll and
TransferCargo (distribution_smoke.runtime). The depot cabin is a stand-in with the real module's
shape; the source checks below pin the facts the witness rests on. NOT TESTED: the engine's class
builder, thread scheduling, real drones, real saves and the real cabin; the attended check covers them.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

from lupa import LuaError

from distribution_smoke import ARCHIVE, MOD, ROOT, runtime

HERE = Path(__file__).resolve().parent
OVERLAY = HERE / '80_AgentSlots_crossing.lua.txt'
GAME = ROOT.parent / 'SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/Lua'
DEPOT = ROOT / 'Code/ElevatorDepot_10_ElevatorDepot.lua'


def code_lines(text):
    return [line for line in text.splitlines() if not line.lstrip().startswith('--')]


def source_checks():
    # Station stock writes by a train: LoadResourceForStation and unload_cargo, nowhere else.
    for tree in (ARCHIVE, GAME):
        train = (tree / 'Units/Train.lua').read_text(encoding='utf8')
        sites = [l.strip() for l in code_lines(train) if 'station:AddResource(' in l]
        assert sites == ['station:AddResource(-amount, res)', 'station:AddResource(amount, res)'], sites
        print('source:', tree.parent.parent.name, 'Units/Train.lua sha256:',
              hashlib.sha256((tree / 'Units/Train.lua').read_bytes()).hexdigest(), 'station writes:', len(sites))
    # The cabin moves stock only in deliver/load_cabin, reached through the global module's Tick.
    depot = DEPOT.read_text(encoding='utf8')
    sites = [l.strip() for l in code_lines(depot) if 'AddResource(' in l]
    assert sites == ['dest:AddResource(k, res)', 'origin:AddResource(-n, res)'], sites
    assert 'local D = SMRElevatorDepot\n' in depot  # brief 34: the shipped name (the Dev aliases follow it)
    assert 'function OnMsg.NewMinute(hour, minute) D.Tick(minute) end' in depot
    assert 'D.CABIN' in depot and 'function D.PairOf(o)' in depot
    # The hub's own stock writes are outflows only (construction jobs), so never a proof's input.
    hub_sites = []
    # brief 34: the hub's former Code/ is now the TrainHub and StationRows module folders
    for path in sorted([*ROOT.glob('Code/TrainHub_*.lua'), *ROOT.glob('Code/StationRows_*.lua')], key=lambda p: p.name.split('_', 1)[1]):
        hub_sites += [l.strip() for l in code_lines(path.read_text(encoding='utf8')) if 'AddResource(' in l]
    assert hub_sites == ['self:AddResource(-amount, res)', 'leader:AddResource(amount, res)',
                         'if amount > 0 then self:AddResource(-amount, res) end'], hub_sites
    print('source: depot', hashlib.sha256(DEPOT.read_bytes()).hexdigest(), 'cabin writes: 2; hub writes: outflows only')


FIXTURE = r'''
const.HourDuration = 3600000
now = 0
GameTime = function() return now end
GetTimeFactor = function() return 0 end
Station.desired_amount = 10000
Train.__ancestors = {}
Station.__ancestors = { MultiResourceDepotBase = true }
g_Classes.Train, g_Classes.Station = Train, Station
-- A drone hands over inside the call, as Building.DroneUnloadResource does.
function Station:DroneUnloadResource(drone, req, res, n) self:AddResource(n, res) end
-- A drone load can yield mid-call (its presentation sleeps, MultiResourceDepot.lua:192-199).
function Station:DroneLoadResource(drone, req, res, n)
    self:AddResource(-n, res)
    if drone_yields then coroutine.yield() end
end

SMRTK = { slots = {}, specs = {}, armed = {}, error_count = 0 }
function SMRTK.Bind(n, label, fn) SMRTK.slots[n] = { label = label, fn = fn } end
function SMRTK.BindScratch() end
function SMRTK.Trigger(spec) SMRTK.specs[spec.id] = spec; return spec end
function SMRTK.Arm(key)
    local ctx = { state = {} }
    local result, why = SMRTK.specs[key].prepare(ctx)
    if result == false then return false, { reason = why } end
    SMRTK.armed[key] = ctx
    return true, result
end
function SMRTK.Disarm(key) SMRTK.armed[key] = nil end
function SMRTK.Run(key) speed = key; return true end
rows = {}
ctx = { mark = function() return 1 end, log = function(_, row) rows[#rows + 1] = row end }
-- One poll of an armed run, as the kit's trigger thread does.
function poll(key)
    local armed = SMRTK.armed[key]
    local fired, f = SMRTK.specs[key].when(armed)
    if fired then SMRTK.armed[key] = nil end
    return fired, f
end
function slot(n) rows = {}; return SMRTK.slots[n].fn(ctx) end

local next_handle = 100
local function line(city, a, b)
    local track = { members = { a, b }, trains = {} }
    function track:GetDestStation(st) return st == a and b or a end
    city.train_track_routes[track] = track.members
    return track
end
local function train(city, track, at)
    local t = setmetatable({ current_station = at, track = track, city = city, stockpiled_amount = {},
        assigned_resources = {}, units = {}, is_stopping = false }, { __index = Train })
    next_handle = next_handle + 1; t.handle = next_handle; t.class = 'Train'
    function t:GetEmptyStorage() local n = 0 for _, v in pairs(self.stockpiled_amount) do n = n + v end return 1000000 - n end
    function t:AddResource(n, r) self.stockpiled_amount[r] = (self.stockpiled_amount[r] or 0) + n end
    function t:LogCargo() end
    function t:PushDestructor() end
    function t:PopDestructor() end
    track.trains[#track.trains + 1] = t
    city.labels.Train[#city.labels.Train + 1] = t
    return t
end
local function make(stock, cap, hub, handle)
    local st = station(stock, cap, hub)
    st.handle = handle
    return st
end
-- Two routes through one hub (surface), and a depot pair, each half on its own map's line.
function world(hubstock, s_stock, u_stock)
    local surface = { train_track_routes = {}, labels = { Station = {}, Train = {} } }
    local under = { train_track_routes = {}, labels = { Station = {}, Train = {} } }
    A, B, H = make(100, 120, false, 11), make(0, 120, false, 12), make(hubstock or 0, 480, true, 1)
    SP, S = make(100, 250, false, 21), make(s_stock or 0, 250, false, 31)
    U, UP = make(u_stock or 0, 250, false, 32), make(0, 250, false, 41)
    for _, st in ipairs { A, B, H, SP, S } do st.city = surface; table.insert(surface.labels.Station, st) end
    for _, st in ipairs { U, UP } do st.city = under; table.insert(under.labels.Station, st) end
    -- A hubless Balanced row takes cargo up to its desired amount (the mod's station rows).
    for _, st in ipairs { SP, S, U, UP } do st.desired_amount = 250000 end
    H.nodes = { [A] = true, [B] = true, [H] = true }
    local ta, tb, ts, tu = line(surface, A, H), line(surface, B, H), line(surface, SP, S), line(under, U, UP)
    TA, TB, TS, TU = train(surface, ta, A), train(surface, tb, H), train(surface, ts, SP), train(under, tu, U)
    Cities = { surface, under }
    UIColony = { labels = surface.labels }
    SMROptInTrainDistribution.Refresh()
end
function load(t, at, n, dest) t.current_station = at; t:LoadResourceForStation('Metals', n * 1000, dest) end
function arrive(t, at) t.current_station = at; t:UnloadAll() end

-- The cabin stand-in: the real module's shape (PairOf, CABIN record with cargo, stock moved by
-- AddResource inside Tick), one leg per call: load at the origin, then deliver at the other end.
SMRElevatorDepotDev = { CABIN = 'SMROptIn_depot_cabin' }
function SMRElevatorDepotDev.PairOf() return S, U end
function SMRElevatorDepotDev.Tick()
    local rec = rawget(S, 'SMROptIn_depot_cabin')
    if not rec then rec = { phase = 'at_top', cargo = {} }; rawset(S, 'SMROptIn_depot_cabin', rec) end
    local here = (rec.phase == 'at_top' or rec.phase == 'up') and S or U
    if rec.phase == 'down' or rec.phase == 'up' then
        local n = rec.cargo.Metals or 0
        if n > 0 then here:AddResource(n, 'Metals') end
        rec.cargo.Metals = nil
        rec.phase = rec.phase == 'down' and 'at_bottom' or 'at_top'
    else
        local n = Min(here.supply.Metals:GetTargetAmount(), 250000)
        if n > 0 then here:AddResource(-n, 'Metals'); rec.cargo.Metals = n end
        rec.phase = rec.phase == 'at_top' and 'down' or 'up'
    end
end
'''

CASES = r'''
local function find(leg, station, res)
    for _, r in ipairs(rows) do
        if r.leg == leg and r.station == station and r.resource == res then return r end
    end
end
local function id(o) return o.class .. '(' .. o.handle .. ')' end
local function u(n) return n % 1000 == 0 and tostring(n // 1000) or string.format('%d.%03d', n // 1000, n % 1000) end

-- Loading the overlay is inert: nothing armed, nothing wrapped.
assert(not next(SMRTK.armed) and SMRTK.slots[7] and SMRTK.slots[10])
assert(Train.UnloadAll == dev_unload and Train.LoadResourceForStation == vanilla_load, 'no wrap at load')

-- H1 PASS: route A delivers 20 assigned + 10 unassigned (the old witness booked the 10 as other_in);
-- route B loads 25 at the hub. The hub held nothing at the start.
world(0)
local w = slot(7)
assert(w.wiring_ok == 'true' and w.trains == 4 and w.trains_wired == 4 and w.hubs == 1, 'wiring proof')
assert(w.classes_unload == 1 and w.classes_drone_unload == 1 and w.cabin_wired == 'true' and w.depot_pair == 'true')
assert(Train.UnloadAll ~= dev_unload and TA.UnloadAll == Train.UnloadAll, 'live trains resolve to the wrapper')
assert(slot(8).trigger == 'crossing_hub' and speed == 'speed_ultra')
load(TA, A, 20, H); TA.stockpiled_amount.Metals = TA.stockpiled_amount.Metals + 10000
arrive(TA, H)
assert(H.supply.Metals:GetActualAmount() == 30000, 'pass-through/unassigned cargo unloaded at the hub')
local fired = poll('crossing_hub'); assert(not fired, 'A alone proves nothing')
SMRTK.armed.crossing_hub = nil
assert(slot(8))
load(TB, H, 25, B)
local fired, f = poll('crossing_hub')
assert(fired and f.verdict == 'proved' and f.resource == 'Metals' and f.crossed_at_least == '25', f and f.verdict)
assert(f.train_mismatch == '0' and f.cabin_mismatch == '0' and f.stuck == 0 and f.rearms == 1)
local read = slot(10)
local r = find('crossing_ledger', id(H), 'Metals')
assert(r.train_in == 'R1=30' and r.train_out == 'R2=25' and r.other_in == '0', r.train_in .. ' ' .. r.other_in)
assert(read.hub_verdict:find('crossed>=25') and read.controls_ok == 'true')

-- H2 (stock at the start): the hub held 50; A delivers 20, B loads 40. The STRICT bound refuses
-- (B could have loaded the starting stock alone; the 2026-09-18 rule out > other_in + own_in
-- would have called 40 proved). The NET bound proves 20: the stock fell by 20, A's 20 covered the rest.
world(50); slot(7); slot(8)
load(TA, A, 20, H); arrive(TA, H); load(TB, H, 40, B)
fired, f = poll('crossing_hub')
assert(fired and f.bound == 'net' and f.crossed_at_least == '20' and f.strict_excess == '-10', f and f.bound)
-- N2 FAIL (net): a stocked hub, B loads 25, no other route delivered: all of it is drawdown.
world(50); slot(7); slot(8)
load(TB, H, 25, B)
assert(not poll('crossing_hub') and slot(10).hub_verdict == 'none', 'drawdown is not a crossing')
-- N1 PASS (net, the first attended check's shape): a hub holding 400 of 480, A delivers 30, B takes 25.
world(400); slot(7); slot(8)
load(TA, A, 30, H); arrive(TA, H); load(TB, H, 25, B)
fired, f = poll('crossing_hub'); assert(fired and f.bound == 'net' and f.crossed_at_least == '25')

-- H3 FAIL (own route): A delivers 20; B delivers 30 and loads 30 back out.
world(0); slot(7); slot(8)
load(TA, A, 20, H); arrive(TA, H)
TB.stockpiled_amount.Metals = 30000; arrive(TB, H); load(TB, H, 30, B)
assert(not poll('crossing_hub'), 'a route reloading its own delivery is not a crossing')
-- ... until B loads more than its own: 5 more units can only be A's.
load(TB, H, 5, B)
fired, f = poll('crossing_hub'); assert(fired and f.crossed_at_least == '5')

-- H4 FAIL (drones): A delivers 20; a drone brings 10 inside its call; B loads 10.
world(0); slot(7); slot(8)
load(TA, A, 20, H); arrive(TA, H)
H:DroneUnloadResource(nil, nil, 'Metals', 10000); load(TB, H, 10, B)
assert(not poll('crossing_hub'), 'drone stock is not a train unload')
slot(10); r = find('crossing_ledger', id(H), 'Metals')
assert(r.drone_in == '10' and r.train_in == 'R1=20' and r.hub_excess == '0')

-- H5 PASS (Ultra, blind): ten deliveries and three loads with no poll at all, then one poll.
world(0); slot(7); slot(8)
for i = 1, 10 do load(TA, A, 2, H); arrive(TA, H) end
for i = 1, 3 do load(TB, H, 5, B) end
fired, f = poll('crossing_hub'); assert(fired and f.crossed_at_least == '15' and f.train_events == 13)

-- H6 (autosave): the save disarms the run, an unexplained +7 lands while blind, the re-press
-- keeps the ledger. The 7 is other_in, never a train unload, and it raises the bar.
world(0); slot(7); slot(8)
load(TA, A, 20, H); arrive(TA, H)
SMRTK.armed.crossing_hub = nil
OnMsg.SaveGameStart(); H:AddResource(7000, 'Metals'); OnMsg.SaveGameDone()
now = 5000
local again = slot(8); assert(again.rearms == 1 and again.blind_ms == 5000)
load(TB, H, 27, B)
fired, f = poll('crossing_hub'); assert(fired and f.crossed_at_least == '20')
slot(10); r = find('crossing_ledger', id(H), 'Metals')
assert(r.other_in == '7' and r.train_in == 'R1=20', r.other_in)

-- H7 the real TransferCargo path at the hub (the mod's UnloadAll twice, then vanilla's loads):
-- the bracket books exactly what the train took and the train-side control stays 0.
world(0); slot(7); slot(8)
load(TA, A, 60, H); arrive(TA, H)
TB.current_station = H; checked_transfer(TB)
local took = TB.stockpiled_amount.Metals or 0
slot(10); r = find('crossing_ledger', id(H), 'Metals')
assert(took > 0 and r.train_out == 'R2=' .. u(took), 'loads booked to R2: ' .. tostring(took) .. ' ' .. r.train_out)
assert(slot(10).controls_ok == 'true')

-- H8 control: a train load whose train never receives the cargo taints that station and resource:
-- no verdict uses it, and the read names the call.
world(0); slot(7); slot(8)
load(TA, A, 20, H); arrive(TA, H)
TB.AddResource = function() end
load(TB, H, 10, B)
assert(not poll('crossing_hub'), 'a tainted resource proves nothing')
read = slot(10)
assert(read.controls_ok == 'false' and read.train_mismatch == '10' and read.tainted == 1)
r = find('crossing_ledger', id(H), 'Metals'); assert(r.tainted == 'true')
local m = rows[#rows - 0] and nil
for _, row in ipairs(rows) do if row.leg == 'crossing_mismatch' then m = row end end
assert(m and m.call == 'LoadResourceForStation' and m.train_delta == '0' and m.station_delta == '-10', 'mismatch named')

-- Y1 (the first attended check's stuck=1): a drone load that yields mid-call, a poll and a train
-- unload during the yield, then the drone resumes. Nothing is left open and the unload is booked.
world(0); slot(7); slot(8)
H:AddResource(5000, 'Metals')
drone_yields = true
local co = coroutine.create(function() H:DroneLoadResource(nil, nil, 'Metals', 5000) end)
assert(coroutine.resume(co))
assert(not poll('crossing_hub'))
load(TA, A, 20, H); arrive(TA, H)
assert(coroutine.resume(co)); drone_yields = false
load(TB, H, 20, B)
fired, f = poll('crossing_hub'); assert(fired and f.stuck == 0 and f.bound == 'strict' and f.crossed_at_least == '15' and f.net_excess == '20', 'stuck ' .. tostring(f and f.stuck))

-- D1 PASS (down): the surface line delivers 30 to the surface half, the cabin carries it down,
-- the underground line loads 30 from the underground half.
world(0); slot(7); assert(slot(9).trigger == 'crossing_depot')
load(TS, SP, 30, S); arrive(TS, S)
SMRElevatorDepotDev.Tick(); SMRElevatorDepotDev.Tick()
assert(U.supply.Metals:GetActualAmount() == 30000)
assert(not poll('crossing_depot'), 'nothing has left the underground half yet')
SMRTK.armed.crossing_depot = nil; slot(9)
load(TU, U, 30, UP)
fired, f = poll('crossing_depot')
assert(fired and f.crossing == 'depot_down' and f.cabin_took_train_cargo == '30' and f.trains_took_cabin_cargo == '30')
assert(f.cabin_events == 4 and f.cabin_mismatch == '0')

-- D2 FAIL (link 1): the surface half's own starting stock rides down; no train delivered it.
world(0, 30); slot(7); slot(9)
SMRElevatorDepotDev.Tick(); SMRElevatorDepotDev.Tick(); load(TU, U, 30, UP)
assert(not poll('crossing_depot') and slot(10).depot_verdict == 'none')

-- D3 (link 2 on a stocked half): the underground half held 40; the cabin brings 30; its trains
-- load 30. Strict refuses (the 40 could have gone); net proves 30 (the half's stock did not fall).
world(0, 0, 40); slot(7); slot(9)
load(TS, SP, 30, S); arrive(TS, S)
SMRElevatorDepotDev.Tick(); SMRElevatorDepotDev.Tick(); load(TU, U, 30, UP)
fired, f = poll('crossing_depot'); assert(fired and f.bound == 'net' and f.trains_took_cabin_cargo == '30')
-- D3n FAIL (link 2, net): the surface delivers and the cabin goes down, but the underground trains
-- take 30 from the half's own 40 before the cabin arrives: all of it drawdown.
world(0, 0, 40); slot(7); slot(9)
load(TS, SP, 30, S); arrive(TS, S); SMRElevatorDepotDev.Tick()
load(TU, U, 30, UP)
assert(not poll('crossing_depot'), 'drawdown at the destination is not a crossing')

-- D4 control: a cabin that takes stock and carries nothing breaks cabin conservation and taints
-- that resource on both halves.
world(0); slot(7); slot(9)
load(TS, SP, 30, S); arrive(TS, S)
SMRElevatorDepotDev_leak = true
SMRElevatorDepotDev.Tick()
SMRElevatorDepotDev_leak = false
assert(not poll('crossing_depot'))
read = slot(10); assert(read.cabin_mismatch == '30' and read.tainted == 2 and read.controls_ok == 'false')

-- A loaded save ends the books.
world(0); slot(7); slot(8)
OnMsg.LoadGame()
fired, f = poll('crossing_hub'); assert(fired and f.verdict == 'ledger_reset_by_load')
local ok, why = SMRTK.slots[8].fn(ctx); assert(ok == false and why:find('slot 7'))
'''


def run(overlay):
    lua = runtime()
    lua.execute('dev_unload, vanilla_load = Train.UnloadAll, Train.LoadResourceForStation')
    lua.execute(FIXTURE)
    # D4's leak switch sits inside the stand-in, behind the wrapper slot 7 installs.
    lua.execute(r'''
local tick = SMRElevatorDepotDev.Tick
SMRElevatorDepotDev.Tick = function(...)
    if SMRElevatorDepotDev_leak then S:AddResource(-30000, 'Metals'); return end
    return tick(...)
end''')
    lua.execute(overlay)
    lua.execute(CASES)


def main():
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), flush=True)
    source_checks()
    overlay = OVERLAY.read_text(encoding='utf8')
    print('80_AgentSlots_crossing.lua.txt sha256:', hashlib.sha256(OVERLAY.read_bytes()).hexdigest(), flush=True)
    run(overlay)
    print('PASS: hub crossing proved from real unloads incl. pass-through/unassigned cargo; strict refused and net '
          'proved on a stocked hub; refused for pure drawdown, own-route reloads and drone stock; exact with no polls '
          '(Ultra); a yielding drone load leaves nothing open; a save is blind but loses no transfer; real '
          'TransferCargo booked to its route; depot down-crossing proved strict and net, refused for either missing '
          'link; train and cabin mismatches taint and are named; load resets')
    mutations = [
        ('no entry checkpoint (the gap booked to the train)',
         '        checkpoint(b, "other")\n        local before = {}', '        local before = {}'),
        ('starting stock left out of the bar', '(b.stock0[res] or 0) + ', ''),
        ('the route\'s own unloads left out', 'local own = ins[route] or 0', 'local own = 0'),
        ('drone stock left out of the bar', ' + (b.drone_in[res] or 0)', ''),
        ('the cabin not wrapped', '        if not original_of[d.Tick] then', '        if false then'),
        ('assigned-only unloads (the 2026-09-18 rule)',
         '        local deltas = checkpoint(b, "train", route)',
         '        local deltas = checkpoint(b, (self.assigned_resources or empty_table)[self.current_station]'
         ' and "train" or "other", route)'),
        ('the net bound without drawdown', 'local netx = out - own - drawdown(b, res) - nontrain - unknown',
         'local netx = out - own - nontrain - unknown'),
        ('a drone bracket held open across its yield',
         '        checkpoint(b, "other")\n        local result = table.pack(orig(self, ...))\n        checkpoint(b, "drone")',
         '        depth = depth + 1\n        checkpoint(b, "other")\n        local result = table.pack(orig(self, ...))\n'
         '        depth = depth - 1\n        checkpoint(b, "drone")'),
    ]
    for name, before, after in mutations:
        assert overlay.count(before) == 1, name
        try:
            run(overlay.replace(before, after, 1))
        except LuaError:
            print('PASS mutation rejected:', name, flush=True)
        else:
            raise AssertionError('mutation survived: ' + name)
    print('NOT TESTED: engine class flattening, trigger threads, real drones/saves/cabin; the attended check covers them')


if __name__ == '__main__':
    main()
