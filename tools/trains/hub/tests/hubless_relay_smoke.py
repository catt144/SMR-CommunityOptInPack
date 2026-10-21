"""Owner rulings 2026-10-21 (R1-R3, R6; docs/agent/bugs/D16.md): the hubless relay rule.

A set row keeps its amount for its own station; the rest balances as the game balances,
split by weight and water-filled, so a station that joins lines passes cargo through; a
depot line takes the view whatever the Station rows toggle says, and a depot half unloads
by its row; the 2026-10-05 depot-line dial pin is gone. The fixtures are the report's
(STATION_ROWS_RELAY_20261021.md sections 12-14): Erion's junction, Xeryx's Import,
TheGodUncle's depot, and the three Codex counterexamples of its section 13.2 (A, B, C).

Promoted from docs/archive/station_rows_proposal_20261021b/proposal_check.py, which ran
the same scenarios against the prototype through a temporary copy; this runs the shipping
Code/ directly through the existing harness (distribution_smoke.py: archived native
Train/Station bodies with request and route doubles). Desk smoke only: no engine
scheduling, save, drone, UI or player-save claim. Run from the repo root.
"""
import hashlib
import subprocess
import sys

from distribution_smoke import ROOT, MOD, ARCHIVE, runtime


def main():
    print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print("HEAD:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), flush=True)
    # The harness pins 405907. Check its consumed files against the installed build's archive.
    current = ARCHIVE.parents[2] / "1.1.1.406343/Src/Lua"
    for name in ["Units/Train.lua", "Buildings/Station.lua",
                 "Buildings/MultiResourceDepot.lua", "Buildings/MultiResourceCubeVisuals.lua"]:
        assert (ARCHIVE / name).read_bytes() == (current / name).read_bytes(), name
    print("PASS native-body archive parity: 1.1.1.405907 -> 1.1.1.406343", flush=True)
    shipping = MOD / "Code/StationRows_40_TrainDistribution.lua"
    print("shipping 40 sha256:", hashlib.sha256(shipping.read_bytes()).hexdigest(), flush=True)
    lua = runtime()
    lua.execute(r'''
debug.setmetatable(nil, {__len=function() return 0 end})
local D = SMROptInTrainDistribution
assert(SMROptInTrainHubBase == nil)
-- the harness walk, with a per-track transport mode and the native "break" (TrainTransport.lua:371-447)
ForEachStationAlongTrack = function(st, track, flags, fn, ...)
    for _, s in ipairs(track.members) do
        if flags ~= 0 or s ~= st then
            if fn(s, track.mode or 'cargo', ...) == 'break' then return end
        end
    end
end
local function vanilla_train(t)
    function t:GetEmptyStorage()
        local n = 0; for _, v in pairs(self.stockpiled_amount) do n = n + v end
        return 42000 - n   -- Train.lua:22 max_shared_storage on 1.1.1.406343
    end
end
local function big_train(t) t.GetEmptyStorage = function() return 1000000 end end
function plain(a, b, ac, bc)
    local t, s, d = fixture(a, b, ac, bc or ac)
    d.hub = false; d.GetTrainExportFloor = nil; d.HubTrackGraph = nil; d.nodes = nil
    vanilla_train(t)
    D.Refresh()
    assert(not D.HubFor(s) and not D.HubFor(d))
    return t, s, d
end
local function u(x) return x / 1000 end
local function expect(label, got, want)
    assert(got == want, label .. ': got ' .. tostring(got) .. ' want ' .. tostring(want))
end
-- a third station on the first line, or a second line through j
local function add_station(s, stock, cap, handle)
    local x = station(stock, cap); x.handle = handle; x.city = s.city
    return x
end
local function second_line(s, j, far, mode)
    local right = { members = { j, far }, trains = {}, mode = mode }
    function right:GetDestStation(st) return st == j and far or j end
    local tu = setmetatable({ current_station = j, track = right, city = s.city,
        stockpiled_amount = {}, assigned_resources = {}, units = {}, is_stopping = false,
        AddResource = Train.AddResource, LogCargo = function() end,
        PushDestructor = function() end, PopDestructor = function() end }, { __index = Train })
    function tu:AddResource(n, r) self.stockpiled_amount[r] = (self.stockpiled_amount[r] or 0) + n end
    vanilla_train(tu)
    right.trains = { tu }; s.city.train_track_routes[right] = right.members
    return right, tu
end

-- ===== 1. Junction relay (Erion's fixture): source 60/60 untouched on L; J on L and R; far 0/60 on R.
-- A row's number is a percent of the station's own store: 20 = 12 units of 60, 100 = 60.
local function junction(mode, percent, rounds)
    local t, s, j = plain(60, 0, 60)
    local far = add_station(s, 0, 60, 3)
    local right, tu = second_line(s, j, far)
    UIColony.labels.Station = { s, j, far }; D.Refresh()
    assert(D.IsJunction(j) and not D.IsJunction(s) and not D.IsJunction(far), 'junction by usable cargo routes')
    if mode ~= 'untouched' then assert(D.Set(j, 'Metals', mode, percent)) end
    for _ = 1, rounds or 1 do
        t.current_station = s; checked_transfer(t); deliver(t, j)
        tu.current_station = j; checked_transfer(tu); deliver(tu, far)
        if stock(far) > 10000 then far:AddResource(-(stock(far) - 10000), 'Metals') end
    end
    return stock(s), stock(j), stock(far)
end
local s1, j1, f1 = junction('untouched')
print('JUNCTION untouched      source=' .. u(s1) .. ' junction=' .. u(j1) .. ' far=' .. u(f1))
expect('untouched = vanilla share both lines', s1 .. ',' .. j1 .. ',' .. f1, '30000,15000,10000')
s1, j1, f1 = junction('balanced', 20)
print('JUNCTION balanced 20    source=' .. u(s1) .. ' junction=' .. u(j1) .. ' far=' .. u(f1))
expect('Balanced 20 (12 of 60): J keeps 12 plus its relay share, relays the rest', s1 .. ',' .. j1 .. ',' .. f1, '30000,20000,10000')
s1, j1, f1 = junction('import', 20)
print('JUNCTION import 20      source=' .. u(s1) .. ' junction=' .. u(j1) .. ' far=' .. u(f1))
expect('Import 20 at a junction still relays beyond its 12', f1 > 0, true)
s1, j1, f1 = junction('export', 20)
print('JUNCTION export 20      source=' .. u(s1) .. ' junction=' .. u(j1) .. ' far=' .. u(f1))
expect('Export 20 at a junction relays what it holds beyond 12', f1 > 0, true)
s1, j1, f1 = junction('import', 100)
print('JUNCTION import 100     source=' .. u(s1) .. ' junction=' .. u(j1) .. ' far=' .. u(f1))
expect('Import 100 at a junction leaves no room to relay (R1: the reserve wins)', f1, 0)
expect('Import 100 at a junction is filled like any station', j1, 30000)
local s4, j4, f4 = junction('balanced', 20, 4)
print('JUNCTION balanced 20 x4 source=' .. u(s4) .. ' junction=' .. u(j4) .. ' far(kept 10)=' .. u(f4))
expect('relay keeps flowing on later trips', s4 < 30000 and f4 == 10000, true)
print('PASS 1 junction relay')

-- ===== 1b. A people-only second line does not make a joining station (report 13.3)
do
    local t, s, j = plain(0, 60, 60)
    local far = add_station(s, 0, 60, 3)
    local right = second_line(s, j, far, 'people')
    UIColony.labels.Station = { s, j, far }; D.Refresh()
    expect('a people-only line is not a cargo route of J', D.IsJunction(j), false)
    assert(D.Set(j, 'Metals', 'import', 50))
    t.current_station = s; checked_transfer(t)
    expect('a full Import on one cargo line gives nothing back', t.stockpiled_amount.Metals or 0, 0)
    -- the same line made cargo-capable makes J a joining station again at the next refresh
    right.mode = nil; D.Refresh()
    expect('a cargo-capable second line restores the joining station', D.IsJunction(j), true)
end
print('PASS 1b usable-cargo junctions')

-- ===== 2. Leaf rows: owner-seen hubless results hold; Export leaves drain (R6); report 13.2 B.
local t, s, d = plain(80, 0, 100); big_train(t)
assert(D.Set(s, 'Metals', 'export', 20)); assert(D.Set(d, 'Metals', 'import', 50))
checked_transfer(t); expect('Export 20 to Import 50', stock(s) .. ',' .. t.stockpiled_amount.Metals, '30000,50000')
deliver(t, d); expect('Import 50 received', stock(d), 50000)
t.current_station = s; checked_transfer(t); expect('nothing more wanted', t.stockpiled_amount.Metals or 0, 0)
t, s, d = plain(80, 0, 100); big_train(t)
assert(D.Set(s, 'Metals', 'export', 20)); assert(D.Set(d, 'Metals', 'balanced', 80))
assert(d.demand.Metals:AssignUnit(10000))
checked_transfer(t); expect('Balanced 80 with a 10 reservation orders 60 of the 60 surplus', stock(s) .. ',' .. t.stockpiled_amount.Metals, '20000,60000')
deliver(t, d); expect('reservation preserved', stock(d) .. ',' .. d.demand.Metals.target, '60000,30000')
t, s, d = plain(10, 0, 100); big_train(t)
assert(D.Set(d, 'Metals', 'import', 50)); checked_transfer(t); deliver(t, d)
expect('reporter line 2026-10-05: untouched 10 beside Import 50 shares as the game would', stock(s) .. ',' .. stock(d), '5000,5000')
t.current_station = d; checked_transfer(t); expect('an Import never becomes a source', stock(d) .. ',' .. (t.stockpiled_amount.Metals or 0), '5000,0')
t, s, d = plain(80, 0, 100); big_train(t)
assert(D.Set(s, 'Metals', 'balanced', 50)); checked_transfer(t); deliver(t, d)
expect('Balanced 50 gives its surplus to an untouched neighbour', stock(s) .. ',' .. stock(d), '50000,30000')
t.current_station = d; checked_transfer(t); expect('the neighbour does not send it back', stock(d) .. ',' .. (t.stockpiled_amount.Metals or 0), '30000,0')
t, s, d = plain(80, 0, 100); big_train(t)
assert(D.Set(s, 'Metals', 'export', 20)); checked_transfer(t); deliver(t, d)
expect('R6: an Export leaf is drained to its floor', stock(s) .. ',' .. stock(d), '20000,60000')
t, s, d = plain(80, 0, 100); big_train(t)
local calls = D.calls; checked_transfer(t); deliver(t, d)
expect('an untouched line takes the native path', stock(s) .. ',' .. stock(d) .. ',' .. tostring(D.calls == calls), '40000,40000,true')
-- Xeryx: Import 20 from an untouched 60/60 source takes the full 12, not a dial-pinned trickle
t, s, d = plain(60, 0, 60); big_train(t)
assert(D.Set(d, 'Metals', 'import', 20)); checked_transfer(t); deliver(t, d)
print('LEAF Import 20 (12 of 60) from untouched 60/60: source=' .. u(stock(s)) .. ' importer=' .. u(stock(d)))
expect('an Import below the game share takes its whole amount', stock(s) .. ',' .. stock(d), '48000,12000')
t, s, d = plain(60, 0, 60); big_train(t)
assert(D.Set(d, 'Metals', 'import', 100)); checked_transfer(t); deliver(t, d)
expect('Import 100 from an untouched source takes the game share', stock(s) .. ',' .. stock(d), '30000,30000')
-- 13.2 B: an empty Export 100 beside two untouched stations takes no share
do
    local t, s, r = plain(60, 0, 60); big_train(t)
    local e = add_station(s, 0, 60, 3)
    table.insert(t.track.members, e); table.insert(UIColony.labels.Station, e); D.Refresh()
    assert(D.Set(e, 'Metals', 'export', 100))
    checked_transfer(t); deliver(t, r)
    print('LEAF 13.2B untouched 60 | untouched 0 | Export 100 empty: ' .. u(stock(s)) .. ' / ' .. u(stock(r)) .. ' / ' .. u(stock(e)))
    expect('13.2 B: an empty Export has no receiving weight', stock(s) .. ',' .. stock(r) .. ',' .. stock(e), '30000,30000,0')
end
print('PASS 2 leaf rows')

-- ===== 2b. Report 13.2 A: a full Import no longer strands an Export's surplus
do
    local t, e, r = plain(60, 0, 60)   -- e = Export 0 with 60, r = untouched receiver
    local i = add_station(e, 60, 60, 3)
    table.insert(t.track.members, i); table.insert(UIColony.labels.Station, i); D.Refresh()
    assert(D.Set(e, 'Metals', 'export', 0)); assert(D.Set(i, 'Metals', 'import', 100))
    checked_transfer(t); deliver(t, r)
    t.current_station = e; checked_transfer(t); deliver(t, r)
    print('LEAF 13.2A Export 0 (60) | untouched 0 | Import 100 full: ' .. u(stock(e)) .. ' / ' .. u(stock(r)) .. ' / ' .. u(stock(i)))
    expect('13.2 A: the untouched receiver takes what the full Import cannot', stock(e) .. ',' .. stock(r) .. ',' .. stock(i), '0,60000,60000')
    -- partially satisfied Import: Import 100 holding 30 beside the same Export and receiver
    t, e, r = plain(60, 0, 60)
    i = add_station(e, 30, 60, 3)
    table.insert(t.track.members, i); table.insert(UIColony.labels.Station, i); D.Refresh()
    assert(D.Set(e, 'Metals', 'export', 0)); assert(D.Set(i, 'Metals', 'import', 100))
    big_train(t); checked_transfer(t)
    local aboard = t.stockpiled_amount.Metals or 0
    local for_i = ((t.assigned_resources[i] or {}).Metals or 0)
    local for_r = ((t.assigned_resources[r] or {}).Metals or 0)
    print('LEAF 13.2A half-full Import: aboard=' .. u(aboard) .. ' for Import=' .. u(for_i) .. ' for receiver=' .. u(for_r))
    expect('the whole surplus is booked: Import takes its 30 room, the receiver the other 30', for_i .. ',' .. for_r, '30000,30000')
end
print('PASS 2b full and half-full Import beside an Export and an untouched receiver')

-- ===== 3. The depot (R2): TheGodUncle's line, a surface Export half (250) beside a vanilla station (60).
local function depot_line(rows_on, mode, percent, depot_stock, receiver_stock)
    local t, d, r = plain(depot_stock or 250, receiver_stock or 0, 250, 60)
    SMROptInPack = { IsActive = function() return rows_on end }
    SMRElevatorDepot = { IsDepot = function(o) return o == d end,
        HubEntry = function(o, res) if mode == 'lone' then return false end return { mode = mode, percent = percent } end }
    d.transport_policy.Metals = mode == 'export' and 'accept' or 'send'; d.desired_amount = false; d:SetDesiredAmount(10000)
    return t, d, r
end
local function finish() SMRElevatorDepot = nil; SMROptInPack = nil end
local t, d, r = depot_line(false, 'export', 4)
checked_transfer(t); deliver(t, r); t.current_station = d; checked_transfer(t); deliver(t, r)
print('DEPOT rows off, Export 4%: depot=' .. u(stock(d)) .. ' receiver=' .. u(stock(r)) .. ' (v1.0.3: 202 / 48)')
expect('D18 alone: the receiver fills to its capacity from the Export half', stock(d) .. ',' .. stock(r), '190000,60000')
finish()
t, d, r = depot_line(true, 'export', 4)
checked_transfer(t); deliver(t, r); t.current_station = d; checked_transfer(t); deliver(t, r)
print('DEPOT rows on,  Export 4%: depot=' .. u(stock(d)) .. ' receiver=' .. u(stock(r)) .. ' (v1.0.3: 240 / 10)')
expect('rows on: the same', stock(d) .. ',' .. stock(r), '190000,60000')
r:AddResource(-50000, 'Metals'); t.current_station = d; checked_transfer(t); deliver(t, r)
expect('refilled after the drones drained it', stock(r), 52000)
t, d, r = depot_line(true, 'export', 4, 100, 60)
assert(D.Set(r, 'Metals', 'export', 0))
t.current_station = r; checked_transfer(t)
expect('an Export half orders nothing even from an exporting neighbour', t.stockpiled_amount.Metals or 0, 0)
finish()
t, d, r = depot_line(false, 'export', 4)
r.desired_amount = false; r:SetDesiredAmount(0)
checked_transfer(t); deliver(t, r)
expect('receiver dial 0: the view opens the gate itself', stock(r), 42000)
finish()
t, d, r = depot_line(true, 'import', 4, 0, 60)
t.current_station = r; checked_transfer(t); deliver(t, d)
print('DEPOT Import 4% (the old dial default): depot=' .. u(stock(d)) .. ' station=' .. u(stock(r)))
expect('Import at 4 percent gathers 10', stock(d), 10000)
finish()
t, d, r = depot_line(true, 'import', 100, 0, 60)
t.current_station = r; checked_transfer(t); deliver(t, d)
print('DEPOT Import 100%: depot=' .. u(stock(d)) .. ' station=' .. u(stock(r)))
expect('Import 100 gathers the share the game would give a 250 store', stock(d) .. ',' .. stock(r), '42000,18000')
t.current_station = d; checked_transfer(t)
expect('an Import half never gives', t.stockpiled_amount.Metals or 0, 0)
finish()
t, d, r = depot_line(true, 'export', 4)
t.current_station = r
local work, stop = t:TransferCargo(nil, false)
expect('an empty receiver sends the train to the Export half', tostring(work) .. ',' .. tostring(stop == d), 'true,true')
finish()
-- 13.2 C: the depot's row holds at unload too, with D16 and D17 off
t, d, r = depot_line(false, 'import', 4, 0, 0)
t.stockpiled_amount.Metals = 42000; t.current_station = d; t:UnloadAll()
print('DEPOT 13.2C Import 4% (10), 42 aboard unassigned: depot=' .. u(stock(d)) .. ' aboard=' .. u(t.stockpiled_amount.Metals or 0))
expect('13.2 C: unassigned cargo unloads only up to the Import target', stock(d) .. ',' .. (t.stockpiled_amount.Metals or 0), '10000,32000')
t, d, r = depot_line(false, 'import', 4, 0, 0)
t.stockpiled_amount.Metals = 42000; t.assigned_resources[d] = { Metals = 42000 }; assert(d.demand.Metals:AssignUnit(42000))
t.current_station = d; t:UnloadAll()
print('DEPOT 13.2C same, assigned before the target was lowered: depot=' .. u(stock(d)) .. ' aboard=' .. u(t.stockpiled_amount.Metals or 0))
expect('13.2 C: a whole old assignment above the target stays aboard, as at an ordinary row', stock(d) .. ',' .. (t.stockpiled_amount.Metals or 0), '0,42000')
t, d, r = depot_line(false, 'export', 4, 0, 0)
t.stockpiled_amount.Metals = 42000; t.current_station = d; t:UnloadAll()
expect('13.2 C: an Export half refuses leftover cargo, as an ordinary Export row does', stock(d) .. ',' .. (t.stockpiled_amount.Metals or 0), '0,42000')
t, d, r = depot_line(false, 'lone', nil, 0, 0)
t.stockpiled_amount.Metals = 42000; t.current_station = d; t:UnloadAll()
expect('a lone half unloads natively', stock(d), 42000)
finish()
t, d, r = depot_line(false, 'lone')
calls = D.calls; checked_transfer(t); deliver(t, r)
expect('lone half, rows off: native balance', stock(d) .. ',' .. stock(r) .. ',' .. tostring(D.calls == calls), '208000,42000,true')
finish()
print('PASS 3 depot')

-- ===== 4. Save and hub seams unchanged
t, s, d = plain(80, 0, 100); assert(D.Set(s, 'Metals', 'export', 20))
OnMsg.SaveGameStart()
assert(s.supply.Metals.desired == s.desired_amount and s.transport_policy.Metals == nil)
OnMsg.SaveGameDone(); OnMsg.LoadGame()
assert(rawget(s, D.LOCAL_FIELD).Metals.mode == 'export')
local hub = station(0, 400, true); hub.handle = 42; hub.city = s.city; hub.nodes = { [s] = true, [hub] = true }
table.insert(UIColony.labels.Station, hub); D.Refresh()
assert(D.HubFor(s) == hub)
t.current_station = s; t:TransferCargo(nil, true)
print('PASS 4 seams: save baseline and hub ownership as before')
assert(not D.error and not SMROptInTrainFloor.stats.last_error)
''')
    print("PASS hubless relay (R1-R3, R6); NOT RUN: engine scheduling, saves, drones, UI, player saves", flush=True)


if __name__ == "__main__":
    main()
