"""Capacity Network desk regression, owner global-purchase ruling 2026-09-29.

Executes archived 1.1.1.405907 building upgrade and storage resize bodies.
Labels/modifier arithmetic and lifecycle are doubles; no native save claim.
The fixture prefix is reused by Cargo, Power and shared TestKit slot tests.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
MOD = ROOT / "tools/devmods/train_hub"
SOURCE = MOD / "Code/20_TrainHub.lua"
# The sibling SMR-Shared checkout; a nested checkout sits deeper, so take the nearest ancestor that has it.
ARCHIVE = next((d / "SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua" for d in ROOT.parents
                if (d / "SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua").is_dir()),
               ROOT.parent / "SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua")
VANILLA = {
    "Buildings/Building.lua": [
        "Building:ApplyUpgrade", "Building:ToggleUpgradeOnOff", "Building:OnUpgradeToggled",
        "Building:ApplyUpgradeModifiersForUpgrade", "Building:StopUpgradeModifiersForUpgrade",
        "Building:StopUpgradeModifiers", "Building:HasUpgrade", "Building:GetUpgradeValue",
        "Building:CanDisableUpgrade", "Building:IsUpgradeOn", "Building:ConstructUpgrade",
        "Building:IsUpgradeBeingConstructed", "Building:StopUpgradeConstruction",
    ],
    "Buildings/UpgradableBuilding.lua": ["UpgradableBuilding:GetUpgradeID", "UpgradableBuilding:GetUpgradeTier"],
    "UpgradeUnlocks.lua": ["UpgradeUnlocks:IsUpgradeUnlocked", "UpgradeUnlocks:UnlockUpgrade"],
    "Buildings/MultiResourceDepot.lua": [
        "MultiResourceDepotBase:UpdateRequestCapacity", "MultiResourceDepotBase:OnModifiableValueChanged",
    ],
}


def extract(text, name):
    m = re.search(r"^function %s\(.*?^end\n" % re.escape(name), text, re.S | re.M)
    assert m, "vanilla body not found: " + name
    return m.group(0)


print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
print("HEAD:", head, flush=True)

code = SOURCE.read_text(encoding="utf8")
section = code[code.index("-- The Capacity Network Upgrade"):code.index("print(\"[TrainHubDev] hub classes loaded")]
cargo = code[code.index("local function own_pallets(self)"):code.index("function SMROptInTrainHubBase:GetCubePosRelative")]

# Static gates on the section's source.
plain = "\n".join(line.split("--", 1)[0] for line in section.split("\n"))
assert not re.search(r"CreateGameTimeThread|CreateRealTimeThread|\bSleep\(|WaitMsg\(|rawset\(", plain), "no thread, no yield, no rawset"
assert "SMRFixPack" not in plain, "ban 2"
writes = sorted(set(re.findall(r"\bself\.(\w+)\s*=[^=]", plain)))
assert not writes, "instance state writes belong to the bounded mirror helper: %r" % writes
assert 'local hub_capacity_upgrade = "SMROptInTrainHub6_CapacityNetwork"' in plain
hub_ovc = code[code.index("function SMROptInTrainHubBase:OnModifiableValueChanged"):]
hub_ovc = hub_ovc[:hub_ovc.index("\nend\n")]
assert "max_storage_per_resource" not in hub_ovc and "MultiResourceDepotBase" not in hub_ovc, \
    "the hub's combined OnModifiableValueChanged leaves the resize to vanilla's body"
assert "Building:Destroy" not in plain and "OnDestroyed" not in plain, "no override of an auto-resolved destroy method"
assert "function OnMsg.BuildingDemolished" in plain and "function SMROptInTrainHubBase:ApplyCopyParams" in plain

# The template half: both files carry the same upgrade, and its id is the section's.
fields = {}
for rel, pat in [("Code/BuildingTemplate/SMROptInTrainHub6.generated.lua", r"^\t(upgrade1_\w+) = (.*),$"),
                 ("Data/BuildingTemplate/SMROptInTrainHub6.lua", r"^\t'(upgrade1_\w+)', (.*),$")]:
    fields[rel] = dict(re.findall(pat, (MOD / rel).read_text(encoding="utf8"), re.M))
gen, data = fields.values()
assert {k:v for k,v in gen.items() if k != "upgrade1_description"} == {k:v for k,v in data.items() if k != "upgrade1_description"}, "generated Capacity numeric fields disagree"
expect = {
    "upgrade1_id": '"SMROptInTrainHub6_CapacityNetwork"',
    "upgrade1_upgrade_cost_Metals": "20000", "upgrade1_upgrade_cost_Concrete": "20000",
    "upgrade1_mod_target_1": '"city"', "upgrade1_mod_label_1": '"Station"',
    "upgrade1_mod_prop_id_1": '"max_storage_per_resource"', "upgrade1_mul_value_1": "100",
    "upgrade1_mod_target_2": '"city"', "upgrade1_mod_label_2": '"Train"',
    "upgrade1_mod_prop_id_2": '"max_shared_storage"', "upgrade1_mul_value_2": "100",
    "upgrade1_mod_target_3": '"city"', "upgrade1_mod_label_3": '"Train"',
    "upgrade1_mod_prop_id_3": '"max_colonists_to_transport"', "upgrade1_mul_value_3": "100",
}
for k, v in expect.items():
    assert gen.get(k) == v, "template %s = %r, want %r" % (k, gen.get(k), v)
# The second upgrade is checked from its authored Data source by cargo_upgrade_smoke.py;
# these fields deliberately select only upgrade1, the existing generated template.

vanilla, hashes = [], {}
for rel, names in VANILLA.items():
    path = ARCHIVE / rel
    hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    text = path.read_text(encoding="utf8").replace("\r\n", "\n")
    vanilla += [extract(text, n) for n in names]

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
OnMsg = {}; empty_table = {}; ResourceScale = 1000
const = { ResourceScale = 1000, Building = { MaxUpgrades = 6, UpgradeModifierSlots = 3 } }
function Min(a, b) return a < b and a or b end
function Max(a, b) return a > b and a or b end
function Clamp(v, lo, hi) return Max(lo, Min(hi, v)) end
function IsValid(o) return type(o) == "table" and not o.deleted end
function IsKindOf(o, c) return type(o) == "table" and o.kinds ~= nil and o.kinds[c] == true end
function Msg() end
function RebuildInfopanel() end
function CreateGameTimeThread() end
function GetPropScale() return 1 end
function print(...) printed = (printed or 0) + 1 end
SelectedObj = false
UpgradeModifierModifiers = {}; BuildingTemplates = {}
function table.get(t, k) return t and t[k] end
g_Classes = {}

-- A label container with vanilla's modifier arithmetic (Modifiers.lua, Modifiable comment :20-26).
local function recompute(obj, prop)
  local p, a = 0, 0
  for _, m in ipairs(obj.mods[prop] or empty_table) do p = p + m.percent; a = a + m.amount end
  local old = obj[prop]
  obj[prop] = obj.base[prop] * (100 + p) // 100 + a
  if old ~= obj[prop] then obj:Notify(prop) end
end
LabelModifier = {}
LabelModifier.__index = LabelModifier
function LabelModifier:new(t) setmetatable(t, LabelModifier); t:TurnOn(); return t end
function LabelModifier:IsApplied() return self.working end
function LabelModifier:TurnOn() self.working=true; self.container:SetLabelModifier(self.label,self.id,self) end
function LabelModifier:TurnOff() self.working=false; self.container:SetLabelModifier(self.label,self.id,nil) end
city = { labels = { Station = {}, Train = {} }, label_modifiers = {} }
function city:SetLabelModifier(label,id,mod)
  self.label_modifiers[label] = self.label_modifiers[label] or {}
  local old=self.label_modifiers[label][id]
  for _,obj in ipairs(self.labels[label] or {}) do
    if old then
      local t=obj.mods[old.prop] or {}
      for i=#t,1,-1 do if t[i]==old then table.remove(t,i) end end
      recompute(obj,old.prop)
    end
    if mod then
      obj.mods[mod.prop]=obj.mods[mod.prop] or {}
      table.insert(obj.mods[mod.prop],mod); recompute(obj,mod.prop)
    end
  end
  self.label_modifiers[label][id]=mod
end
function add_later_modifiers(obj,label)
 for _,container in ipairs({city,UIColony}) do
  for _,mod in pairs(container.label_modifiers[label] or {}) do
   obj.mods[mod.prop]=obj.mods[mod.prop] or {}; table.insert(obj.mods[mod.prop],mod)
   recompute(obj,mod.prop)
  end
 end
end
UpgradeUnlocks = {}
UIColony = setmetatable({ unlocked_upgrades = {}, force_locked_upgrades = {}, labels = city.labels, label_modifiers={} },
  { __index = UpgradeUnlocks })

city.colony=UIColony; UIColony.SetLabelModifier=city.SetLabelModifier
Building, UpgradableBuilding, MultiResourceDepotBase = {}, {}, {}
Station = {}
function Station.GetTotalStorageColumns(self) return 6 end
CObject = { HasSpot = function() return false end }
''')
for body in vanilla:
    lua.execute(body)
lua.execute(r'''
-- One method table per class, vanilla's resolution order for what these tests touch.
for k, v in pairs(UpgradableBuilding) do if Building[k] == nil then Building[k] = v end end
for k, v in pairs(MultiResourceDepotBase) do if Building[k] == nil then Building[k] = v end end
function Building:GetPropertyMetadata() return nil end
function Building:CreateUpgradeUpkeepObject() end
function Building:UpdateWorking() end
function Building:StartUpgradeConstruction(id)
  self.upgrades_under_construction = self.upgrades_under_construction or {}
  self.upgrades_under_construction[id] = { id = id, tier = self:GetUpgradeTier(id), reqs = self.reqs_pending or false, canceled = false }
end
function Building:CleanUpgradeConstructionRequests() end
function Building:GetUpgradeCost(tier, r) return self[string.format("upgrade%s_upgrade_cost_%s", tostring(tier), r)] or 0 end
function Building:GetMaxStorage(res) return self.max_storage_per_resource end
function Building:GetMaxStorageForAnyOneResource() return self.max_storage_per_resource end
function Building:RecalculateDerivedMaxZ() end
function Building:ReallocateVisualColumns() end
function Building:RebuildInfopanel() end
function Building:Notify(prop)
  -- Combined OnModifiableValueChanged: parents' bodies run first (Modifiers.lua:20-26).
  if self.depot then MultiResourceDepotBase.OnModifiableValueChanged(self, prop) end
  self.changed = self.changed or {}; self.changed[prop] = (self.changed[prop] or 0) + 1
end
Building.__index = Building
SMROptInTrainHubBase = setmetatable({}, Building)
SMROptInTrainHubBase.__index = SMROptInTrainHubBase
''')
lua.execute(cargo)
lua.execute(section)
lua.execute(r'''
local ID = SMROptInTrainHubBase.hub_capacity_upgrade
local req = {}
req.__index = req
function req:GetActualAmount() return self.actual end
function req:SetAmount(n) self.amount = n end
function req:SetDesiredAmount(n) self.desired = n end
local function depot(cls, handle, cap, labels, extra)
  local o = setmetatable({ handle = handle, kinds = {}, mods = {}, base = { max_storage_per_resource = cap },
    max_storage_per_resource = cap, depot = true, city = city, storable_resources = { "Metals" },
    desire_slider_max = cap // 1000, desired_amount = 10000,
    supply = { Metals = setmetatable({ actual = 0 }, req) }, demand = { Metals = setmetatable({}, req) } }, cls)
  for _, l in ipairs(labels) do table.insert(city.labels[l], o) end
  for k, v in pairs(extra or empty_table) do o[k] = v end
  return o
end
local function hub(handle, x)
  local h = depot(SMROptInTrainHubBase, handle, 240000, { "Station" }, {
    has_visual_cubes = true, upgrade1_id = ID, upgrade1_can_disable = true,
    upgrade1_upgrade_cost_Metals = 20000, upgrade1_upgrade_cost_Concrete = 20000 })
  h.kinds = { SMROptInTrainHubBase = true }
  for i = 1, 3 do
    h["upgrade1_mod_target_" .. i] = "city"
    h["upgrade1_mod_label_" .. i] = i == 1 and "Station" or "Train"
    h["upgrade1_mod_prop_id_" .. i] = ({ "max_storage_per_resource", "max_shared_storage", "max_colonists_to_transport" })[i]
    h["upgrade1_mul_value_" .. i] = 100
    h["upgrade1_add_value_" .. i] = 0
  end
  for t = 2, 6 do h["upgrade" .. t .. "_id"] = "" h["upgrade" .. t .. "_mod_prop_id_1"] = "" end
  function h:PartitionVisualResources() return nil, nil, 1 end
  function h:GetAttaches() return {} end
  local pos = { xy = function() return x or handle * 1000, 0 end }
  function h:GetPos() return pos end
  h.map = "surface"
  function h:GetMap() return self.map end
  add_later_modifiers(h,"Station")
  h:InitHubCapacityUpgrade()
  return h
end
local function train(handle)
  local t = setmetatable({ handle = handle, kinds = {}, mods = {}, city = city,
    base = { max_shared_storage = 42000, max_colonists_to_transport = 12 },
    max_shared_storage = 42000, max_colonists_to_transport = 12 }, Building)
  table.insert(city.labels.Train, t)
  add_later_modifiers(t,"Train")
  return t
end
local function remove(list, o) for i = #list, 1, -1 do if list[i] == o then table.remove(list, i) end end end
-- Applied modifiers only: whether a turned-off LabelModifier stays registered on its container is
-- the engine's (SavegameFixups.RemoveLeakedUpgradeModifiers exists for the leak), not modelled here.
local function count_mods() local n = 0 for _, t in pairs(UIColony.label_modifiers) do for _, m in pairs(t) do if m:IsApplied() then n = n + 1 end end end return n end

-- 1. Unlocked from the start; vanilla still charges/builds only once.
OnMsg.CityStart(); assert(UIColony:IsUpgradeUnlocked(ID))
local small=depot(Building,101,60000,{'Station'})
local big=depot(Building,102,120000,{'Station'})
local A,B=hub(201),hub(202)
local T1=train(301)
small.supply.Metals.actual=100000
local maxz0=(function() A:RecalculateDerivedMaxZ(); return A.max_z end)()
A.reqs_pending={{GetResource=function() return 'Metals' end,GetActualAmount=function() return 0 end}}
A:ConstructUpgrade(ID); B:ConstructUpgrade(ID)
assert(A:IsUpgradeBeingConstructed(ID) and not B:IsUpgradeBeingConstructed(ID),'one construction claim')
A:StopUpgradeConstruction(ID); B:ConstructUpgrade(ID)
assert(not B:IsUpgradeBeingConstructed(ID),'cancelled construction claim')
A:ApplyUpgrade(1)
assert(count_mods()==3 and UIColony.label_modifiers.Station['201_upgrade1_mod_1'],'vanilla modifier id retained on colony')
assert(small.max_storage_per_resource==120000 and big.max_storage_per_resource==240000)
assert(A.max_storage_per_resource==480000 and B.max_storage_per_resource==480000)
assert(T1.max_shared_storage==84000 and T1.max_colonists_to_transport==24)
assert(small.demand.Metals.amount==20000 and small.desire_slider_max==120,'native request resize')
assert(math.floor(A.max_z)==math.floor(maxz0),'cargo visual cap unchanged')
assert(B:CanDisableUpgrade(ID) and B:IsUpgradeOn(ID),'receiver display and switch')
B:ApplyUpgrade(1); assert(count_mods()==3,'no duplicate purchase')
B:ToggleUpgradeOnOff(ID)
assert(not A:IsUpgradeOn(ID) and not B:IsUpgradeOn(ID),'shared off display')
assert(A.upgrade_on_off_state[ID]==false and B.upgrade_on_off_state[ID]==false,'raw panel mirror')
assert(small.max_storage_per_resource==60000 and small.demand.Metals.amount==0 and small.supply.Metals.actual==100000,'over-cap stock preserved')
B:ToggleUpgradeOnOff(ID); assert(A:IsUpgradeOn(ID) and small.max_storage_per_resource==120000)
local enable=not B.upgrade_on_off_state[ID]
for _,h in ipairs({A,B}) do if h.upgrade_on_off_state[ID]~=enable then h:ToggleUpgradeOnOff(ID) end end
assert(not A:IsUpgradeOn(ID) and not B:IsUpgradeOn(ID),'broadcast switches once')
B:ToggleUpgradeOnOff(ID)
A.destroyed=true; OnMsg.BuildingDemolished(A); A:StopUpgradeModifiers()
remove(city.labels.Station,A); A.deleted=true
assert(count_mods()==3 and T1.max_shared_storage==84000,'buyer salvage and clear preserve effects')
local later=hub(203); local T2=train(302)
assert(later:IsUpgradeOn(ID) and later:CanDisableUpgrade(ID) and later.max_storage_per_resource==480000,'later hub inherits')
assert(T2.max_shared_storage==84000 and T2.max_colonists_to_transport==24,'later train inherits')
B:ToggleUpgradeOnOff(ID)
for _,h in ipairs({B,later}) do h:StopUpgradeModifiers(); remove(city.labels.Station,h); h.deleted=true end
OnMsg.LoadGame()
local new=hub(204)
assert(new:HasUpgrade(ID) and not new:IsUpgradeOn(ID) and new:CanDisableUpgrade(ID),'off purchase survives zero hubs and reload')
new:ToggleUpgradeOnOff(ID)
assert(count_mods()==3 and T2.max_shared_storage==84000,'new hub switches retained purchase')
OnMsg.LoadGame(); assert(count_mods()==3 and T2.max_shared_storage==84000,'idempotent load')
''')
print('PASS Capacity: global display/switch, broadcast, construction, native resize, salvage/clear, zero hubs, future hubs/trains, load')
