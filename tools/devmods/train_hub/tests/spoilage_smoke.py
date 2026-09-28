"""Stations keep their food, the hub and ordinary depots still spoil (owner, 2026-09-28).

Runs the archived 1.1.1.405907 spoilage bodies (Spoilage.lua's CalcResourceSpoilage,
StorageDepot:BuildingDailyUpdate and :SpoilStoredResources) over a depot, a station and
the hub, before and after Code/60_StationSpoilage.lua loads.
"""
import re
import subprocess
import sys
from pathlib import Path
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
ARCHIVE = ROOT.parent / "SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua"
CODE = ROOT / "tools/devmods/train_hub/Code/60_StationSpoilage.lua"


def body(path, start):
    text = (ARCHIVE / path).read_text(encoding="utf8")
    i = text.index(start)
    return text[i:text.index("\nend\n", i) + 5]


def main():
    print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print("HEAD:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), flush=True)
    building = (ARCHIVE / "Buildings/Building.lua").read_text(encoding="utf8")
    assert re.search(r'RecursiveCallMethods\.BuildingDailyUpdate = "call"', building)
    depot = (ARCHIVE / "Buildings/StorageDepot.lua").read_text(encoding="utf8")
    assert re.search(r"function StorageDepot:BuildingDailyUpdate\(day\)\s+self:SpoilStoredResources\(\)", depot)
    assert "Spoil" not in (ARCHIVE / "Units/Train.lua").read_text(encoding="utf8")
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(r'''
Min=math.min
const={ResourceScale=1000}
g_Consts={FoodDecay=4}
FoodResources={'Food','Butter',Food=true,Butter=true}
CurrentSpoilage={}
InteractionRand=function(n) return 0 end -- the fraction always rounds up
local function request(n)
    return {n=n,GetActualAmount=function(r) return r.n end}
end
local function class(parent) local c={} return setmetatable(c,{__index=parent}) end
StorageDepot={}
Station=class(StorageDepot)
SMROptInTrainHubBase=class(Station)
function make(cls,food)
    local o=setmetatable({supply={Food=request(food),Butter=request(food),Metals=request(food)}},{__index=cls})
    function o:AddDepotResource(n,res) self.supply[res].n=self.supply[res].n+n end
    return o
end
''')
    for part in (body("Spoilage.lua", "function CalcResourceSpoilage("),
                 body("Buildings/StorageDepot.lua", "function StorageDepot:BuildingDailyUpdate("),
                 body("Buildings/StorageDepot.lua", "function StorageDepot:SpoilStoredResources(")):
        lua.execute(part)
    lua.execute(r'''
local d,s,h=make(StorageDepot,10000),make(Station,10000),make(SMROptInTrainHubBase,480000)
for _,o in ipairs({d,s,h}) do StorageDepot.BuildingDailyUpdate(o,1) end
assert(d.supply.Food.n==9000 and s.supply.Food.n==9000 and h.supply.Food.n==460000)
assert(s.supply.Butter.n==9000 and s.supply.Metals.n==10000)
''')
    print("CONTROL vanilla: depot, station and hub each lose 4% of Food and Butter a sol; Metals keeps", flush=True)
    lua.execute(CODE.read_text(encoding="utf8"))
    lua.execute(r'''
local d,s,h=make(StorageDepot,10000),make(Station,10000),make(SMROptInTrainHubBase,480000)
for day=1,3 do
    for _,o in ipairs({d,s,h}) do StorageDepot.BuildingDailyUpdate(o,day) end
end
assert(s.supply.Food.n==10000 and s.supply.Butter.n==10000, "station spoiled")
assert(d.supply.Food.n<10000 and h.supply.Food.n<480000, "depot or hub stopped spoiling")
assert(StorageDepot.SpoilStoredResources==SMROptInTrainHubBase.SpoilStoredResources)
''')
    print("PASS stations keep Food and delicacies over three sols; hub and ordinary depots still spoil", flush=True)
    print("NOT TESTED: the engine's class build, the combined-method dispatch and a live sol", flush=True)


if __name__ == "__main__":
    main()
