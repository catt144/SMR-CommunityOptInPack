"""Proposal 2026-10-21: the hubless view balances parts, a depot's rows enter, junctions relay.

Desk check of the PROTOTYPE file beside this script, never of shipping code: the
shipping StationRows_10 is copied to a temporary mod folder next to the prototype 40,
and the existing harness (tools/trains/hub/tests/distribution_smoke.py: archived
native Train/Station bodies with request and route doubles) runs against it.
No engine scheduling, save, drone, UI or player-save claim. Run from the repo root.
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools/trains/hub/tests"))
import distribution_smoke  # noqa: E402

print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
print("HEAD:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), flush=True)
current = distribution_smoke.ARCHIVE.parents[2] / "1.1.1.406343/Src/Lua"
for name in ["Units/Train.lua", "Buildings/Station.lua",
             "Buildings/MultiResourceDepot.lua", "Buildings/MultiResourceCubeVisuals.lua"]:
    assert (distribution_smoke.ARCHIVE / name).read_bytes() == (current / name).read_bytes(), name
print("PASS native-body archive parity: 1.1.1.405907 -> 1.1.1.406343", flush=True)

tmp = Path(tempfile.mkdtemp(prefix="smr_proposal_"))
(tmp / "Code").mkdir()
shutil.copy(ROOT / "Code/StationRows_10_TrainFloor.lua", tmp / "Code/StationRows_10_TrainFloor.lua")
proposal = HERE / "StationRows_40_TrainDistribution.proposal.lua"
shutil.copy(proposal, tmp / "Code/StationRows_40_TrainDistribution.lua")
print("prototype:", proposal.name, "sha256:", hashlib.sha256(proposal.read_bytes()).hexdigest(), flush=True)
print("shipping 40 sha256:", hashlib.sha256((ROOT / "Code/StationRows_40_TrainDistribution.lua").read_bytes()).hexdigest(), flush=True)
distribution_smoke.MOD = tmp
lua = distribution_smoke.runtime()
lua.execute(r'''
debug.setmetatable(nil, {__len=function() return 0 end})
local D = SMROptInTrainDistribution
assert(SMROptInTrainHubBase == nil)
local function vanilla_train(t)
    function t:GetEmptyStorage()
        local n = 0; for _, v in pairs(self.stockpiled_amount) do n = n + v end
        return 42000 - n   -- Train.lua:22 max_shared_storage on 1.1.1.406343
    end
end
function plain(a, b, ac, bc)
    local t, s, d = fixture(a, b, ac, bc or ac)
    d.hub = false; d.GetTrainExportFloor = nil; d.HubTrackGraph = nil; d.nodes = nil
    vanilla_train(t)
    D.Refresh()
    assert(not D.HubFor(s) and not D.HubFor(d))
    return t, s, d
end
local function u(x) return x / 1000 end
local function say(label, ...) print(label, ...) end

-- ===== 1. Junction relay: Astra's fixture (desk_check.py), shipping result far=0 for every set row.
-- source 60/60 untouched on line L; J on L and R; far 0/60 untouched on R; one delivery each line.
-- A row's number is a percent of the station's own store: 20 = 12 units of 60, 100 = 60.
local function junction(mode, percent, rounds)
    local t, s, j = plain(60, 0, 60)
    local far = station(0, 60); far.handle = 3; far.city = s.city
    local right = { members = { j, far }, trains = {} }
    function right:GetDestStation(st) return st == j and far or j end
    local tu = setmetatable({ current_station = j, track = right, city = s.city,
        stockpiled_amount = {}, assigned_resources = {}, units = {}, is_stopping = false,
        AddResource = t.AddResource, LogCargo = t.LogCargo,
        PushDestructor = t.PushDestructor, PopDestructor = t.PopDestructor }, { __index = Train })
    vanilla_train(tu)
    right.trains = { tu }; s.city.train_track_routes[right] = right.members
    UIColony.labels.Station = { s, j, far }; D.Refresh()
    assert(D.IsJunction(j) and not D.IsJunction(s) and not D.IsJunction(far), 'junction detection by distinct routes')
    if mode ~= 'untouched' then assert(D.Set(j, 'Metals', mode, percent)) end
    for _ = 1, rounds or 1 do
        t.current_station = s; checked_transfer(t); deliver(t, j)
        tu.current_station = j; checked_transfer(tu); deliver(tu, far)
        -- drones at the far station take what arrives (its dial is 10), as a consumer line would
        if stock(far) > 10000 then far:AddResource(-(stock(far) - 10000), 'Metals') end
    end
    return stock(s), stock(j), stock(far), far
end
local function expect(label, got, want)
    assert(got == want, label .. ': got ' .. tostring(got) .. ' want ' .. tostring(want))
end
local s1, j1, f1 = junction('untouched')
say('JUNCTION untouched      source=' .. u(s1) .. ' junction=' .. u(j1) .. ' far=' .. u(f1))
expect('untouched = vanilla share both lines', s1 .. ',' .. j1 .. ',' .. f1, '30000,15000,10000')
s1, j1, f1 = junction('balanced', 20)
say('JUNCTION balanced 20    source=' .. u(s1) .. ' junction=' .. u(j1) .. ' far=' .. u(f1))
expect('Balanced 20 at a junction relays beyond its 20', f1 > 0, true)
expect('Balanced 20 (12 units of 60): source keeps its share, J keeps 12 plus its relay share', s1 .. ',' .. j1, '30000,20000')
s1, j1, f1 = junction('import', 20)
say('JUNCTION import 20      source=' .. u(s1) .. ' junction=' .. u(j1) .. ' far=' .. u(f1))
expect('Import 20 at a junction still relays beyond its 20', f1 > 0, true)
s1, j1, f1 = junction('export', 20)
say('JUNCTION export 20      source=' .. u(s1) .. ' junction=' .. u(j1) .. ' far=' .. u(f1))
expect('Export 20 at a junction relays what it holds beyond 20', f1 > 0, true)
s1, j1, f1 = junction('import', 100)
say('JUNCTION import 100     source=' .. u(s1) .. ' junction=' .. u(j1) .. ' far=' .. u(f1))
expect('Import 100 at a junction leaves no room to relay (documented)', f1, 0)
expect('Import 100 at a junction is filled like any station', j1, 30000)
local s4, j4, f4, far4 = junction('balanced', 20, 4)
say('JUNCTION balanced 20 x4 source=' .. u(s4) .. ' junction=' .. u(j4) .. ' far(kept 10)=' .. u(f4))
expect('relay keeps flowing on later trips', s4 < s1 or f4 == 10000, true)
print('PASS 1 junction relay: untouched unchanged, a set row keeps its amount and relays the rest, Import 100 blocks')

-- ===== 2. Leaf rows: the owner-seen hubless results hold, and an Export leaf is drained.
local t, s, d = plain(80, 0, 100)
assert(D.Set(s, 'Metals', 'export', 20)); assert(D.Set(d, 'Metals', 'import', 50))
t.GetEmptyStorage = function() return 1000000 end
checked_transfer(t); expect('Export 20 to Import 50', stock(s) .. ',' .. t.stockpiled_amount.Metals, '30000,50000')
deliver(t, d); expect('Import 50 received', stock(d), 50000)
t.current_station = s; checked_transfer(t); expect('nothing more wanted', t.stockpiled_amount.Metals or 0, 0)
t, s, d = plain(10, 0, 100); t.GetEmptyStorage = function() return 1000000 end
assert(D.Set(d, 'Metals', 'import', 50)); checked_transfer(t); deliver(t, d)
expect('reporter line 2026-10-05: untouched 10 beside Import 50 shares as the game would', stock(s) .. ',' .. stock(d), '5000,5000')
t.current_station = d; checked_transfer(t); expect('an Import never becomes a source', stock(d) .. ',' .. (t.stockpiled_amount.Metals or 0), '5000,0')
t, s, d = plain(80, 0, 100); t.GetEmptyStorage = function() return 1000000 end
assert(D.Set(s, 'Metals', 'balanced', 50)); checked_transfer(t); deliver(t, d)
expect('Balanced 50 gives its surplus to an untouched neighbour', stock(s) .. ',' .. stock(d), '50000,30000')
t.current_station = d; checked_transfer(t); expect('the neighbour does not send it back', stock(d) .. ',' .. (t.stockpiled_amount.Metals or 0), '30000,0')
t, s, d = plain(80, 0, 100); t.GetEmptyStorage = function() return 1000000 end
assert(D.Set(s, 'Metals', 'export', 20)); checked_transfer(t); deliver(t, d)
say('LEAF export 20 (80) beside untouched 0/100: source=' .. u(stock(s)) .. ' neighbour=' .. u(stock(d)))
expect('an Export leaf is drained to its floor (shipping strands 20 above it)', stock(s) .. ',' .. stock(d), '20000,60000')
t, s, d = plain(80, 0, 100); t.GetEmptyStorage = function() return 1000000 end
local calls = D.calls
checked_transfer(t); deliver(t, d)
expect('an untouched line takes the native path', stock(s) .. ',' .. stock(d) .. ',' .. tostring(D.calls == calls), '40000,40000,true')
print('PASS 2 leaf rows: owner-seen results hold; an Export leaf drains to its floor')

-- ===== 3. The depot: TheGodUncle's line, a surface Export half (250) beside a vanilla station (60).
local function depot_line(rows_on, mode, percent, depot_stock, receiver_stock)
    local t, d, r = plain(depot_stock or 250, receiver_stock or 0, 250, 60)   -- d = depot double, r = receiver
    SMROptInPack = { IsActive = function() return rows_on end }
    SMRElevatorDepot = { IsDepot = function(o) return o == d end,
        HubEntry = function(o, res) if mode == 'lone' then return false end return { mode = mode, percent = percent } end }
    -- the depot's own vanilla policy for its drones (ElevatorDepot_10 apply_row): accept for hand-out, send for gather
    d.transport_policy.Metals = mode == 'export' and 'accept' or 'send'; d.desired_amount = false; d:SetDesiredAmount(10000)
    return t, d, r
end
local function finish() SMRElevatorDepot = nil; SMROptInPack = nil end
-- 3a rows OFF, D18 alone: Export floor 4% (the dial default) hands out above 10; two trips (42 each)
local t, d, r = depot_line(false, 'export', 4)
checked_transfer(t); deliver(t, r); t.current_station = d; checked_transfer(t); deliver(t, r)
say('DEPOT rows off, Export 4%: depot=' .. u(stock(d)) .. ' receiver=' .. u(stock(r)) .. ' (shipping: 202 / 48)')
expect('D18 alone: the receiver fills to its capacity from the Export half', stock(r), 60000)
expect('D18 alone: the depot hands out, keeping its floor of 10 at most', stock(d), 190000)
finish()
-- 3b rows ON, same line: identical
t, d, r = depot_line(true, 'export', 4)
checked_transfer(t); deliver(t, r); t.current_station = d; checked_transfer(t); deliver(t, r)
say('DEPOT rows on,  Export 4%: depot=' .. u(stock(d)) .. ' receiver=' .. u(stock(r)) .. ' (shipping: 240 / 10)')
expect('rows on: the same', stock(d) .. ',' .. stock(r), '190000,60000')
-- the receiver's drones take it; the next trip refills
r:AddResource(-50000, 'Metals'); t.current_station = d; checked_transfer(t); deliver(t, r)
expect('refilled after the drones drained it', stock(r), 52000)
-- an Export half never takes: the train at the receiver with surplus loads nothing for the depot
t, d, r = depot_line(true, 'export', 4, 100, 60)
assert(D.Set(r, 'Metals', 'export', 0))
t.current_station = r; checked_transfer(t)
expect('an Export half orders nothing even from an exporting neighbour', t.stockpiled_amount.Metals or 0, 0)
finish()
-- 3c the receiver's vanilla dial at 0 (the reachable gate trap) no longer stops the line
t, d, r = depot_line(false, 'export', 4)
r.desired_amount = false; r:SetDesiredAmount(0)
checked_transfer(t); deliver(t, r)
say('DEPOT rows off, receiver dial 0: receiver=' .. u(stock(r)) .. ' (shipping: nothing moves, desire sum 0)')
expect('the view opens the gate itself', stock(r), 42000)
finish()
-- 3d Import half at the dial default (4% = 10 units) gathers a trickle; at 100% it gathers as a big station would
t, d, r = depot_line(true, 'import', 4, 0, 60)
t.current_station = r; checked_transfer(t); deliver(t, d)
say('DEPOT Import 4% (dial default): depot=' .. u(stock(d)) .. ' station=' .. u(stock(r)))
expect('Import at the dial default gathers 10', stock(d), 10000)
finish()
t, d, r = depot_line(true, 'import', 100, 0, 60)
t.current_station = r; checked_transfer(t); deliver(t, d)
say('DEPOT Import 100%: depot=' .. u(stock(d)) .. ' station=' .. u(stock(r)) .. ' (station keeps its 60/310 share)')
expect('Import 100 gathers the share the game would give a 250 store', stock(d) .. ',' .. stock(r), '42000,18000')
t.current_station = d; checked_transfer(t)
expect('an Import half never gives', t.stockpiled_amount.Metals or 0, 0)
finish()
-- 3d2 the pickup trip: a train idle at the empty receiver must go to the Export half (the native
-- should-move input; the hub path's 'empty importer visits a supplier' for a depot line)
t, d, r = depot_line(true, 'export', 4)
t.current_station = r
local work, stop = t:TransferCargo(nil, false)
expect('an empty receiver sends the train to the Export half', tostring(work) .. ',' .. tostring(stop == d), 'true,true')
finish()
-- 3e a lone half (no twin) is an untouched station; rows off => native path
t, d, r = depot_line(false, 'lone')
calls = D.calls; checked_transfer(t); deliver(t, r)
expect('lone half, rows off: native balance', stock(d) .. ',' .. stock(r) .. ',' .. tostring(D.calls == calls), '208000,42000,true')
finish()
print('PASS 3 depot: Export drains to its floor in every hubless configuration; Import gathers; the dial-0 trap is closed')

-- ===== 4. Save and hub seams unchanged: snapshot restores vanilla desires; a hub-owned line declines this view
t, s, d = plain(80, 0, 100); assert(D.Set(s, 'Metals', 'export', 20))
OnMsg.SaveGameStart()
assert(s.supply.Metals.desired == s.desired_amount and s.transport_policy.Metals == nil)
OnMsg.SaveGameDone(); OnMsg.LoadGame()
assert(rawget(s, D.LOCAL_FIELD).Metals.mode == 'export')
local hub = station(0, 400, true); hub.handle = 42; hub.city = s.city; hub.nodes = { [s] = true, [hub] = true }
table.insert(UIColony.labels.Station, hub); D.Refresh()
assert(D.HubFor(s) == hub)
calls = D.calls; t.current_station = s; t:TransferCargo(nil, true)
print('PASS 4 seams: save baseline and hub ownership as before')
assert(not D.error and not SMROptInTrainFloor.stats.last_error)
''')
print("PASS proposal scenarios; NOT RUN: engine scheduling, saves, drones, UI, player saves", flush=True)
shutil.rmtree(tmp, ignore_errors=True)
