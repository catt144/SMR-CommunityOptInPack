"""Brief 34: the three train modules' shipping gates, through the real framework.

Loads Code/00_Core.lua (Register, IsActive, the Mod Options reconciler) and the three
Opt_ files over the distribution harness's native station bodies, then drives the toggles
the way the engine does (CurrentModOptions + OnMsg.ApplyModOptions). Owner rulings,
2026-10-02 (OI-41, spec §10 "Brief 34's checkpoint"):
  - hubless rows follow StationRows, and are forced on while TrainHub is on;
  - a hub's network keeps its rows with both modules off (part of the hub);
  - stations keep food only while TrainHub is on; the hub always spoils;
  - TrainHub / ElevatorDepot off hides their template from the build menu (a lock).
Mutations: each gate removed in turn must make this smoke fail.

Desk smoke only: no engine build menu, save serialization or pixel claim.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from lupa import LuaRuntime
from distribution_smoke import ROOT, runtime

CORE = ROOT / "Code/00_Core.lua"
OPT = {m: ROOT / ("Code/Opt_%s.lua" % m) for m in ("StationRows", "TrainHub", "ElevatorDepot")}
ROWS = ROOT / "Code/StationRows_40_TrainDistribution.lua"
SPOIL = ROOT / "Code/TrainHub_60_StationSpoilage.lua"
FRAMEWORK_STUBS = r'''
ModLog=function() end
CreateRealTimeThread=function() end
CurrentModOptions={}
function toggle(id, on)
    CurrentModOptions[id] = on
    OnMsg.ApplyModOptions("SMR_CommunityOptInPack")
end
'''


def rows_case(mutate_rows=None):
    """Hubless rows, the forced-on rule, live off restoring vanilla, and the hub's network."""
    lua = runtime() if mutate_rows is None else runtime_with(mutate_rows)
    lua.execute(FRAMEWORK_STUBS)
    lua.execute(CORE.read_text(encoding="utf8"))
    for m in ("StationRows", "TrainHub"):
        lua.execute(OPT[m].read_text(encoding="utf8"))
    lua.execute(r'''
local D, P = SMROptInTrainDistribution, SMROptInPack
debug.setmetatable(nil, {__len=function() return 0 end})
assert(P.fixes.StationRows.status=='inactive' and P.fixes.TrainHub.status=='inactive')
function plain()
    local t, s, other = fixture(80, 0, 100, 100)
    other.hub = false
    other.GetTrainExportFloor, other.HubTrackGraph, other.nodes = nil, nil, nil
    D.Refresh()
    return t, s, other
end
-- 1. both off: a hubless station shows and applies nothing
local t, s, other = plain()
assert(not D.RowsOn(s), 'hubless rows on with both modules off')
local ok, why = D.Set(s, 'Metals', 'export', 20)
assert(not ok and why=='Station rows is off', tostring(why))
assert(D.Effective(s, 'Metals')==nil)
print('PASS both off: a hubless station keeps vanilla rows; D.Set refuses')
-- 2. StationRows on (a live, first mid-session enable): the rows work
toggle('StationRows', true)
assert(P.IsActive('StationRows') and D.RowsOn(s))
assert(D.Set(s, 'Metals', 'export', 20))
assert(s.supply.Metals.desired==100000, 'export did not apply')
print('PASS StationRows on: four-state rows apply (export floor written)')
-- 3. live off: vanilla desired amounts back, the stored setting kept, unused
toggle('StationRows', false)
assert(not P.IsActive('StationRows') and not D.RowsOn(s))
assert(s.supply.Metals.desired==s.desired_amount, 'vanilla baseline not restored on off')
assert(rawget(s, D.LOCAL_FIELD).Metals.mode=='export', 'stored setting lost')
assert(D.Effective(s, 'Metals')==nil)
print('PASS StationRows off: vanilla desired restored, setting kept but unused')
-- 4. TrainHub on forces the rows on (owner, 2026-10-02), its on_activate re-applies them
toggle('TrainHub', true)
assert(P.IsActive('TrainHub') and not P.IsActive('StationRows'))
assert(D.RowsOn(s), 'forced rows not re-applied on TrainHub on: RowsOn false')
assert(s.supply.Metals.desired==100000, 'forced rows not re-applied on TrainHub on')
toggle('TrainHub', false)
assert(not D.RowsOn(s) and s.supply.Metals.desired==s.desired_amount)
print('PASS TrainHub forces the rows on, and off returns them to the StationRows toggle')
-- 5. a hub's network keeps its rows with both modules off
local t2, s2, hub = fixture(80, 0, 100, 400)
D.Refresh()
assert(D.HubFor(s2)==hub and D.RowsOn(s2), 'hub network lost its rows')
assert(D.Set(s2, 'Metals', 'import', 50))
assert(rawget(hub, D.FIELD)[s2].Metals.mode=='import')
print('PASS both off: a hub network keeps its rows (part of the hub)')
''')


def runtime_with(mutate):
    """The harness runtime, with 40 replaced by a mutated copy (for the falsifiers)."""
    import distribution_smoke as ds
    original = ds.MOD
    src = ROWS.read_text(encoding="utf8")
    mutated = mutate(src)
    assert mutated != src, "mutation did not apply"
    tmp = Path(tempfile.mkdtemp(prefix="module_gates_mutant_"))
    (tmp / "Code").mkdir(parents=True, exist_ok=True)
    for name in ("10_TrainFloor.lua", "40_TrainDistribution.lua"):
        text = mutated if name.startswith("40") else (ROOT / "Code" / ("StationRows_" + name)).read_text(encoding="utf8")
        (tmp / "Code" / ("StationRows_" + name)).write_text(text, encoding="utf8")
    ds.MOD = tmp
    try:
        return runtime()
    finally:
        ds.MOD = original


def spoil_case(spoil_source):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(r'''
OnMsg={}
active={}
SMROptInPack={IsActive=function(id) return active[id]==true end}
StorageDepot={}
function StorageDepot:SpoilStoredResources() self.spoiled=(self.spoiled or 0)+1 end
Station=setmetatable({}, {__index=StorageDepot})
SMROptInTrainHubBase=setmetatable({}, {__index=Station})
''')
    lua.execute(spoil_source)
    lua.execute(r'''
local function obj(cls) return setmetatable({}, {__index=cls}) end
local s, h = obj(Station), obj(SMROptInTrainHubBase)
s:SpoilStoredResources(); h:SpoilStoredResources()
assert(s.spoiled==1 and h.spoiled==1, 'TrainHub off: a station must spoil as vanilla')
active.TrainHub=true
s:SpoilStoredResources(); h:SpoilStoredResources()
assert(s.spoiled==1, 'TrainHub on: a station must keep its food')
assert(h.spoiled==2, 'the hub always spoils')
print('PASS spoilage: stations keep food only while TrainHub is on; the hub always spoils')
''')


def lock_case(opt_sources):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(r'''
handlers={}
OnMsg=setmetatable({}, {__newindex=function(_, k, f) handlers[k]=handlers[k] or {}; table.insert(handlers[k], f) end})
''' + FRAMEWORK_STUBS.replace('OnMsg.ApplyModOptions("SMR_CommunityOptInPack")',
                              'for _, f in ipairs(handlers.ApplyModOptions) do f("SMR_CommunityOptInPack") end'))
    lua.execute(CORE.read_text(encoding="utf8"))
    for src in opt_sources:
        lua.execute(src)
    lua.execute(r'''
local function locked(id)
    local locks = {}
    for _, f in ipairs(handlers.GetAdditionalBuildingLocks) do f({template_name=id, class=id, id=id}, locks) end
    -- as vanilla's GetAdditionalBuildingLock (BuildMenu.lua:400-408): any truthy value locks
    for _, v in pairs(locks) do if v then return true end end
    return false
end
assert(locked('SMROptInTrainHub6') and locked('SMROptInElevatorDepotDev'), 'off modules must lock their template')
assert(not locked('StationBig'), 'a vanilla template must stay unlocked')
toggle('TrainHub', true)
assert(not locked('SMROptInTrainHub6') and locked('SMROptInElevatorDepotDev'))
toggle('ElevatorDepot', true)
assert(not locked('SMROptInElevatorDepotDev'))
toggle('TrainHub', false); toggle('ElevatorDepot', false)
assert(locked('SMROptInTrainHub6') and locked('SMROptInElevatorDepotDev'))
print('PASS build menu: each module off hides only its own template; on offers it again')
''')


def must_fail(name, expect, fn):
    """The mutation must fail AT ITS GATE: `expect` must be in the error, so a harness
    error (a missing file, a syntax slip) can never pass as a rejected mutation."""
    try:
        fn()
    except Exception as exc:  # lupa raises LuaError; an AssertionError is also a failure
        msg = str(exc)
        assert expect in msg, "mutation %r failed for the wrong reason: %s" % (name, msg[:300])
        print("PASS mutation rejected: %s (%s)" % (name, expect))
        return
    raise AssertionError("mutation survived: " + name)


def main():
    print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print("HEAD:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), flush=True)
    rows_case()
    spoil = SPOIL.read_text(encoding="utf8")
    spoil_case(spoil)
    opts = [OPT["TrainHub"].read_text(encoding="utf8"), OPT["ElevatorDepot"].read_text(encoding="utf8")]
    lock_case(opts)
    # falsifiers: each gate removed must fail
    must_fail("hubless gate always open", "hubless rows on with both modules off", lambda: rows_case(
        lambda s: s.replace('return P.IsActive("StationRows") or P.IsActive("TrainHub")', 'return true')))
    must_fail("TrainHub no longer forces the rows", "forced rows not re-applied", lambda: rows_case(
        lambda s: s.replace('return P.IsActive("StationRows") or P.IsActive("TrainHub")',
                            'return P.IsActive("StationRows")')))
    must_fail("hub network gated like a hubless station", "hub network lost its rows", lambda: rows_case(
        lambda s: s.replace('return D.IsRowStation(st) and (hubless_on() or D.HubFor(st) ~= nil)',
                            'return D.IsRowStation(st) and hubless_on()')))
    must_fail("spoilage ungated", "a station must spoil as vanilla", lambda: spoil_case(re.sub(
        r'\tlocal P = rawget\(_G, "SMROptInPack"\)\n.*?\n\tend\n', '', spoil, flags=re.S)))
    must_fail("TrainHub lock removed", "off modules must lock their template", lambda: lock_case(
        [opts[0].replace("locks.smr_train_hub_module_off = true", "locks.smr_train_hub_module_off = false"), opts[1]]))
    print("NOT TESTED: the engine's build menu, Mod Options page, save serialization; the owner's in-game check covers loading")


if __name__ == "__main__":
    main()
