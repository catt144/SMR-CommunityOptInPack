"""Offline claim tests; C++ requests and drone scheduling are NOT emulated proof.

Runs the archived 1.1.1.405907 Train:TransferCargo body with explicit doubles.
Never opens the parallel drones-chain files. Run from the repo root.
"""
from pathlib import Path
import hashlib
import re
import subprocess
import sys

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
MOD = ROOT / "tools/devmods/train_hub"
ARCHIVE = ROOT.parent / "SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src"
SOURCE = ARCHIVE / "Lua/Units/Train.lua"


def main():
    print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print("HEAD:", subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), flush=True)
    print("source:", SOURCE, "sha256:", hashlib.sha256(SOURCE.read_bytes()).hexdigest(), flush=True)
    # Regenerate only explicit code registrations from their ModItemCode source.
    # The editor owns generated preset/entity entries and code_hash; preserve them.
    items = (MOD / "items.lua").read_text(encoding="utf8")
    metadata_path = MOD / "metadata.lua"
    metadata = metadata_path.read_text(encoding="utf8")
    code = re.search(r"('code', \{\n)(.*?)(\t\},)", metadata, re.S)
    assert code
    explicit = re.findall(r"'CodeFileName', \"([^\"]+)\"", items)
    existing = re.findall(r'"([^\"]+)"', code[2])
    generated = [p for p in existing if p.endswith(".generated.lua")]
    assert all(p in explicit or p in generated for p in existing)
    expected = explicit + generated
    if "--regen-code" in sys.argv:
        updated = metadata[:code.start(2)] + "".join(
            f'\t\t"{p}",\n' for p in expected) + metadata[code.end(2):]
        metadata_path.write_text(updated, encoding="utf8", newline="\n")
        existing = expected
    assert existing == expected, "metadata drift; run this test with --regen-code"
    assert explicit.count("Code/40_TrainDistribution.lua") == 1
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(r'''
Min, Max = math.min, math.max
ResourceScale = 1000
empty_table = {}
const = {trfInclusive=1, trfBidirectional=2}
IsValid = function(o) return type(o) == "table" and not o.invalid end
IsKindOf = function(o, c) return o.class == c end
MulDivRound = function(a,b,c) return math.floor(a*b/c+0.5) end
table.find = function(t,v) for i,x in ipairs(t) do if x == v then return i end end end
table.copy = function(t) local r={} for k,v in pairs(t) do r[k]=v end return r end
table.keys = function(t) local r={} for k in pairs(t) do r[#r+1]=k end return r end
ripairs = function(t) local i=#t+1 return function() i=i-1 if i>0 then return i,t[i] end end end
GetNextConnectedStation = function(st) return st end
ForEachTrainInRoute = function() end
GetRouteDist = function() return 1 end
ForEachStationAlongTrack = function(st, track, flags, fn, ...)
    if flags ~= 0 then fn(st, "cargo", ...) end
    fn(track:GetDestStation(st), "cargo", ...)
end
function request(actual, desired)
    return {
        actual=actual, target=actual, desired=desired,
        GetActualAmount=function(r) return r.actual end,
        GetTargetAmount=function(r) return r.target end,
        GetDesiredAmount=function(r) return r.desired end,
        SetDesiredAmount=function(r,n) r.desired=n end,
        CanAssignUnit=function(r,n) return n>0 and n<=r.target end,
        AssignUnit=function(r,n)
            if r.reject or not r:CanAssignUnit(n) then return false end
            r.target=r.target-n return true
        end,
        UnassignUnit=function(r,n,fulfilled)
            assert(not fulfilled) r.target=r.target+n
        end,
    }
end
function station(stock)
    local s={class="Station", handle=stock+1, storable_resources={"Metals"},
        waiting_for_train={}, transport_policy={},
        supply={Metals=request(stock*1000,50000)},
        demand={Metals=request((100-stock)*1000,50000)}}
    function s:GetMaxStorage() return 100000 end
    function s:GetResDesiredAmount(res) return self.supply[res]:GetDesiredAmount() end
    function s:IsResourceEnabled() return true end
    function s:AddResource(n,res)
        for _,pair in ipairs({{self.supply[res],n},{self.demand[res],-n}}) do
            pair[1].actual=pair[1].actual+pair[2]
            pair[1].target=pair[1].target+pair[2]
        end
    end
    return s
end
Train = {}
function fixture(a,b)
    local src,dst=station(a),station(b)
    local track={GetDestStation=function(_,s) return s==src and dst or src end}
    local t=setmetatable({current_station=src,track=track,
        city={train_track_routes={[track]={src,dst}}},
        stockpiled_amount={},assigned_resources={},is_stopping=false}, {__index=Train})
    function t:GetEmptyStorage() return 100000 end
    function t:AddResource(n,res) self.stockpiled_amount[res]=(self.stockpiled_amount[res] or 0)+n end
    function t:LogCargo() end
    function t:PushDestructor() end
    function t:PopDestructor() end
    return t,src,dst
end
RequestAssignUnit=function(r,u,n) return r:AssignUnit(n) end
RequestUnassignUnit=function(r,u,n,f) r:UnassignUnit(n,f) end
''')
    source = SOURCE.read_text(encoding="utf8")
    # Exact delimited archived bodies, not a reimplementation of the balancer.
    sections = [
        ("local ttPrioBalance =", "function Train:LogCargo"),
        ("function Train:TransferCargo(", "function Train:OnContinuousTaskTick("),
    ]
    chunks = [source[source.index(start):source.index(end)] for start, end in sections]
    lua.execute("\n".join(chunks))
    lua.execute("vanilla_transfer = Train.TransferCargo")
    floor_path = MOD / "Code/10_TrainFloor.lua"
    lua.execute(floor_path.read_text(encoding="utf8"))
    print("floor sha256:", hashlib.sha256(floor_path.read_bytes()).hexdigest(), flush=True)
    lua.execute(r'''
local F=SMROptInTrainFloor
local r=request(80000,50000)
local returns=table.pack(F.WithTransientClaims({{r,20000}},function(a)
    assert(a==7 and r:GetTargetAmount()==60000 and r:GetActualAmount()==80000)
    return true,nil,7,nil
end,7))
assert(returns.n==4 and returns[1] and returns[2]==nil and returns[3]==7)
assert(r.target==80000 and r.actual==80000)
r.reject=true
F.WithTransientClaims({{r,20000}},function() assert(r.target==80000) end)
r.reject=false
F.WithTransientClaims({{r,20000}},function() local absent; return absent.field end)
assert(r.target==80000 and F.stats.last_error)
-- A real cargo reservation survives the prototype releasing its own demand claim.
local d=request(100000,50000)
F.WithTransientClaims({{d,20000}},function() assert(d:AssignUnit(30000)) end)
assert(d.target==70000)
local t,s,dest=fixture(80,0)
t:TransferCargo()
assert(t.stockpiled_amount.Metals==40000 and s.supply.Metals.actual==40000)
print("PASS vanilla archived balancer: 80/0 -> source 40, cargo 40")
t,s,dest=fixture(80,0)
function s:GetTrainExportFloor() return 20000,false end
t:TransferCargo()
assert(t.stockpiled_amount.Metals==20000 and s.supply.Metals.actual==60000)
assert(s.supply.Metals.target==60000 and rawget(s,F.FIELD)==nil)
print("PASS existing transient path: floor 20 -> source 60, cargo 20; claim released")
-- Standing hub reserve regression, without loading either fenced hub file.
t,s,dest=fixture(80,0)
function s:GetTrainExportFloor() return 20000,true end
F.Reconcile(s)
assert(F.Held(s,"Metals")==20000)
t:TransferCargo()
assert(F.Held(s,"Metals")==20000 and s.supply.Metals.actual==60000)
F.ReleaseAll(s)
assert(s.supply.Metals.target==s.supply.Metals.actual)
print("PASS rejection, runtime failure cleanup, nil returns, other reservations, standing reserve")
''')
    distribution_path = MOD / "Code/40_TrainDistribution.lua"
    lua.execute(distribution_path.read_text(encoding="utf8"))
    print("distribution sha256:", hashlib.sha256(distribution_path.read_bytes()).hexdigest(), flush=True)
    lua.execute(r'''
local D=SMROptInTrainDistribution
SMROptInTrainFloor.stats.last_error=nil
local t,s,d=fixture(80,0)
assert(D.Set(s,"Metals","export",20))
local v=D.Status(s,"Metals")
assert(v.current.supply_target==80000 and v.drone.supply_target==80000)
assert(v.drone.supply_desired==100000 and v.drone.demand_desired==0)
assert(v.train.supply_target==60000 and v.train.demand_target==0)
assert(s.supply.Metals.desired==50000 and s.demand.Metals.desired==50000)
assert(s.supply.Metals.target==80000 and s.demand.Metals.target==20000)
t:TransferCargo()
assert(t.stockpiled_amount.Metals==20000 and s.supply.Metals.target==60000)
D.Reset()
-- A configured destination must be claimed when the train is at another station.
t,s,d=fixture(80,0)
assert(D.Set(d,"Metals","export",20))
t:TransferCargo(nil,true)
assert(not t.stockpiled_amount.Metals and d.demand.Metals.target==100000)
D.Reset()
t,s,d=fixture(80,0)
assert(D.Set(s,"Metals","import",20))
t:TransferCargo(nil,true)
assert(not t.stockpiled_amount.Metals and s.supply.Metals.target==80000)
D.Reset()
t,s,d=fixture(80,0)
assert(D.Set(d,"Metals","import",20))
t:TransferCargo()
assert(t.stockpiled_amount.Metals==40000)
assert(d.demand.Metals.target==60000) -- real train reservation retained
print("PASS import destination still gets share 40, not full capacity 100")
D.Reset()
t,s,d=fixture(80,0)
assert(D.Set(d,"Metals","balanced",20))
t:TransferCargo()
assert(t.stockpiled_amount.Metals==20000 and d.demand.Metals.target==80000)
D.Reset()
-- Existing hauler claims, partial stock and capacity changes.
t,s,d=fixture(10,0)
assert(s.supply.Metals:AssignUnit(3000))
assert(D.Set(s,"Metals","export",20))
v=D.Status(s,"Metals")
assert(v.train.supply_target==0 and s.supply.Metals.target==7000)
function s:GetMaxStorage() return 200000 end
v=D.Status(s,"Metals")
assert(v.slider==40000 and s.supply.Metals.target==7000)
assert(not D.Set(s,"Metals","export",101))
assert(not D.Set(s,"Metals","export",0/0))
assert(not D.Set(s,"Missing","export",20))
function s:GetTrainExportFloor() return 0,true end
assert(not D.Set(s,"Metals","export",20))
D.Reset()
-- Sample failure restores desired amounts; disabled resources are bypassed.
t,s,d=fixture(80,0)
assert(D.Set(s,"Metals","balanced",20))
local old=s.supply.Metals.GetActualAmount
s.supply.Metals.GetActualAmount=function(r)
    if r.desired==20000 then local absent; return absent.field end
    return old(r)
end
assert(not D.Status(s,"Metals"))
assert(s.supply.Metals.desired==50000 and s.demand.Metals.desired==50000)
s.supply.Metals.GetActualAmount=old
function s:IsResourceEnabled() return false end
assert(not D.Status(s,"Metals"))
D.Reset()
assert(D.calls>0)
assert(not SMROptInTrainFloor.stats.last_error, "unexpected error inside native transfer")
print("PASS modes, route destination, reservation cleanup, live percentage, invalid input, sample failure")
-- Claims bracket evaluation, but existing incoming assignments predate them.
-- Demonstrate the limit without changing vanilla unload behaviour.
D.Reset()
t,s,d=fixture(0,0)
t.stockpiled_amount.Metals=10000
t.assigned_resources[s]={Metals=10000}
assert(s.demand.Metals:AssignUnit(10000))
assert(D.Set(s,"Metals","export",20))
t:TransferCargo(nil,true)
assert(s.supply.Metals.actual==5000 and t.stockpiled_amount.Metals==5000)
print("PASS limitation: existing inbound 10 unloads, then 5 reloads despite export floor 20")
D.Reset()
''')
    print("PASS offline scope only: native requests, drones, engine load/save NOT tested", flush=True)


if __name__ == "__main__":
    main()
