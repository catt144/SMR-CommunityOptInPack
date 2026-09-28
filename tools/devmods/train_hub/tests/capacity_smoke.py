"""Desk smoke for the Capacity Network Upgrade (spec §4.10, brief 08). Requires lupa.

Runs vanilla's OWN upgrade and resize bodies, extracted verbatim from the archived 1.1.1.405907
tree (Building:ApplyUpgrade, ToggleUpgradeOnOff, the modifier on/off pair, StopUpgradeModifiers,
HasUpgrade, CanDisableUpgrade, IsUpgradeOn, ConstructUpgrade, IsUpgradeBeingConstructed,
UpgradableBuilding's id/tier lookups, UpgradeUnlocks, MultiResourceDepotBase's
OnModifiableValueChanged and UpdateRequestCapacity), with this file's section and the hub's
capped RecalculateDerivedMaxZ loaded over them. The modifier container, the label lists and the
modifiable arithmetic (Modifiers.lua: base x (100 + sum percent) / 100 + sum amount) are doubles.

What this holds: the unlock from the start; the three modifiers applied (small 60 -> 120, big
120 -> 240, hub 240 -> 480, train 42 -> 84 and 12 -> 24) and removed; a live station resizing
through OnModifiableValueChanged with the hub's cargo look still capped at 150; a second hub
reading the upgrade as spent and unable to build, switch or double it; a start refused while
another hub builds, cancelled or not; toggle off and on; the over-capacity drop (demand 0, stock
kept); salvage switching the bonus off while the ruins keep the claim, a rebuild carrying it to
the new hub built once and in the on/off state the ruins held, and clearing the ruins releasing it
for re-purchase (owner, 2026-09-26 amended 2026-09-28); static gates on the section. No game, no
save file, no native claim.
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
assert writes == ["upgrade_on_off_state"], "the section writes only vanilla's own table: %r" % writes
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
assert gen == data, "the generated class and its Data source disagree"
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
assert not any(k.startswith("upgrade2_") for k in gen), "one upgrade, not two (owner, 2026-09-25)"

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
function LabelModifier:new(t) return setmetatable(t, LabelModifier) end
function LabelModifier:IsApplied() return self.on == true end
function LabelModifier:TurnOn()
  if self.on then return end
  self.on = true
  for _, obj in ipairs(self.container.labels[self.label] or empty_table) do
    obj.mods[self.prop] = obj.mods[self.prop] or {}
    table.insert(obj.mods[self.prop], self); recompute(obj, self.prop)
  end
end
function LabelModifier:TurnOff()
  if not self.on then return end
  self.on = false
  for _, obj in ipairs(self.container.labels[self.label] or empty_table) do
    local t = obj.mods[self.prop]
    for i = #t, 1, -1 do if t[i] == self then table.remove(t, i) end end
    recompute(obj, self.prop)
  end
end
city = { labels = { Station = {}, Train = {} }, label_modifiers = {} }
function city:SetLabelModifier(label, id, mod)
  self.label_modifiers[label] = self.label_modifiers[label] or {}
  self.label_modifiers[label][id] = mod
  if mod then mod:TurnOn() end
end
UpgradeUnlocks = {}
UIColony = setmetatable({ unlocked_upgrades = {}, force_locked_upgrades = {}, labels = city.labels },
  { __index = UpgradeUnlocks })

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
  return h
end
local function train(handle)
  local t = setmetatable({ handle = handle, kinds = {}, mods = {}, city = city,
    base = { max_shared_storage = 42000, max_colonists_to_transport = 12 },
    max_shared_storage = 42000, max_colonists_to_transport = 12 }, Building)
  table.insert(city.labels.Train, t)
  return t
end
local function remove(list, o) for i = #list, 1, -1 do if list[i] == o then table.remove(list, i) end end end
-- Applied modifiers only: whether a turned-off LabelModifier stays registered on its container is
-- the engine's (SavegameFixups.RemoveLeakedUpgradeModifiers exists for the leak), not modelled here.
local function count_mods() local n = 0 for _, t in pairs(city.label_modifiers) do for _, m in pairs(t) do if m:IsApplied() then n = n + 1 end end end return n end

-- 1. Unlocked from the start, no tech; idempotent across a load.
assert(not UIColony:IsUpgradeUnlocked(ID))
OnMsg.CityStart(); assert(UIColony:IsUpgradeUnlocked(ID), "unlocked at CityStart")
OnMsg.LoadGame(); assert(UIColony:IsUpgradeUnlocked(ID))

local small = depot(Building, 101, 60000, { "Station" })
local big = depot(Building, 102, 120000, { "Station" })
local A, B = hub(201), hub(202)
local T1 = train(301)
small.supply.Metals.actual = 100000
local maxz0 = (function() A:RecalculateDerivedMaxZ() return A.max_z end)()

-- 2. Hub A builds it through vanilla's ApplyUpgrade: three modifiers, the vanilla ids.
A:ApplyUpgrade(1)
assert(A:HasUpgrade(ID) and A:IsUpgradeOn(ID))
assert(count_mods() == 3 and city.label_modifiers.Station["201_upgrade1_mod_1"]
  and city.label_modifiers.Train["201_upgrade1_mod_2"] and city.label_modifiers.Train["201_upgrade1_mod_3"])
applied = { small.max_storage_per_resource, big.max_storage_per_resource, A.max_storage_per_resource,
  B.max_storage_per_resource, T1.max_shared_storage, T1.max_colonists_to_transport }
assert(small.max_storage_per_resource == 120000 and big.max_storage_per_resource == 240000)
assert(A.max_storage_per_resource == 480000 and B.max_storage_per_resource == 480000)
assert(T1.max_shared_storage == 84000 and T1.max_colonists_to_transport == 24)
-- A train built after the upgrade is not in the label when the modifier turned on; vanilla's
-- LabelModifier container applies to later label members natively. Not modelled here.

-- 3. Live resize through vanilla's OnModifiableValueChanged: demand re-sized, slider re-ranged,
-- the hub's cargo look still sized from the 150 cap.
assert(small.demand.Metals.amount == 20000, "120 cap - 100 stored")
assert(small.desire_slider_max == 120 and A.desire_slider_max == 480)
assert(math.floor(A.max_z) == math.floor(maxz0), "the hub's stacks keep the 150 look")

-- 4. A second hub reads it as spent, cannot switch it, cannot build it, cannot double it.
assert(B:HasUpgrade(ID) == true and B:CanDisableUpgrade(ID) == false)
assert(type(B.upgrade_on_off_state) == "table", "the panel's Ctrl+click indexes it raw")
assert(not B:IsUpgradeBeingConstructed(ID))
B:ToggleUpgradeOnOff(ID); assert(A:IsUpgradeOn(ID) and small.max_storage_per_resource == 120000)
local p = printed or 0
B:ConstructUpgrade(ID); assert(not B.upgrades_under_construction and printed == p + 1, "refused, logged")
B:ApplyUpgrade(1); assert(count_mods() == 3 and small.max_storage_per_resource == 120000, "never +200%")
B:StopUpgradeModifiersForUpgrade(ID); B:ApplyUpgradeModifiersForUpgrade(ID)
assert(small.max_storage_per_resource == 120000)

-- The panel's Ctrl+click (sectionUpgrades.generated.lua:69-92, UpgradableBuilding.lua:368-392): the
-- clicked hub is selected, `enable` is its raw state negated, sent to every hub of the class;
-- ruins pass BroadcastAction's GetUIInteractionState filter (BaseBuilding.lua:541-552).
local function broadcast_toggle(from)
  local was = SelectedObj
  SelectedObj = from
  local enable = not from.upgrade_on_off_state[ID]
  for _, bld in ipairs(city.labels.Station) do
    if IsKindOf(bld, "SMROptInTrainHubBase") and bld:HasUpgrade(ID) and bld.upgrade_on_off_state[ID] ~= enable then
      bld:ToggleUpgradeOnOff(ID)
    end
  end
  SelectedObj = was
end

-- 5. Toggle off and on on the owner; the over-capacity drop keeps the stock.
A:ToggleUpgradeOnOff(ID)
assert(not A:IsUpgradeOn(ID) and A:HasUpgrade(ID) and B:HasUpgrade(ID), "off is still spent")
toggled_off = { small.max_storage_per_resource, big.max_storage_per_resource, A.max_storage_per_resource,
  T1.max_shared_storage, T1.max_colonists_to_transport }
assert(small.max_storage_per_resource == 60000 and A.max_storage_per_resource == 240000)
assert(T1.max_shared_storage == 42000 and T1.max_colonists_to_transport == 12)
assert(small.demand.Metals.amount == 0 and small.supply.Metals.actual == 100000, "demand 0, no stock lost")
assert(small.desire_slider_max == 60)
-- A Ctrl+click from spent B is inert (owner, 2026-09-28): the owner stays off, and it is logged.
local p5 = printed or 0
broadcast_toggle(B)
assert(not A:IsUpgradeOn(ID) and count_mods() == 0 and small.max_storage_per_resource == 60000, "B's broadcast inert")
assert(printed == p5 + 1, "refusal logged once")
-- The owner's own Ctrl+click still switches it.
broadcast_toggle(A)
assert(A:IsUpgradeOn(ID) and small.max_storage_per_resource == 120000 and T1.max_colonists_to_transport == 24)

-- 6. Salvaged (Building:OnDemolish -> Destroy, then Msg BuildingDemolished, Building.lua:910-919):
-- the bonus goes off, the ruins keep the claim (owner, 2026-09-28).
local function salvage(h) h.destroyed = true; OnMsg.BuildingDemolished(h) end
-- Vanilla completion order (ConstructionSite.lua:1724-1745): new building placed at the site,
-- ApplyCopyParams, then DoneObject(ruins) -> Building:Done's StopUpgradeModifiers (:534) and the
-- label removal; the new hub joins the Station label at its GameInit, later.
local function rebuild(ruins, handle)
  local n = hub(handle, (ruins:GetPos():xy()))
  n:ApplyCopyParams({})
  ruins:StopUpgradeModifiers(); remove(city.labels.Station, ruins); ruins.deleted = true
  table.insert(city.labels.Station, n)
  return n
end
salvage(A)
assert(small.max_storage_per_resource == 60000 and big.max_storage_per_resource == 120000, "bonus off at salvage")
assert(T1.max_shared_storage == 42000 and T1.max_colonists_to_transport == 12 and count_mods() == 0)
assert(small.demand.Metals.amount == 0 and small.supply.Metals.actual == 100000, "demand 0, no stock lost")
assert(A:IsUpgradeOn(ID), "the state the player left stays for the rebuild")
assert(B:HasUpgrade(ID) and B:CanDisableUpgrade(ID) == false, "claim held by the ruins")
B:ConstructUpgrade(ID); assert(not B.upgrades_under_construction, "second hub refused")
A:ToggleUpgradeOnOff(ID); A:ToggleUpgradeOnOff(ID); B:ToggleUpgradeOnOff(ID)
assert(count_mods() == 0 and small.max_storage_per_resource == 60000, "no toggle revives it on ruins")
salvaged = { small.max_storage_per_resource, big.max_storage_per_resource, T1.max_shared_storage, T1.max_colonists_to_transport }
-- A hub standing elsewhere never takes the ruins' upgrade.
B:ApplyCopyParams({}); assert(not Building.HasUpgrade(B, ID) and Building.HasUpgrade(A, ID))
-- Nor one on another map at the same x, y (UIColony's labels span maps).
local F = hub(206, (A:GetPos():xy())); F.map = "underground"
F:ApplyCopyParams({}); assert(not Building.HasUpgrade(F, ID) and Building.HasUpgrade(A, ID), "other map")
remove(city.labels.Station, F)

-- 6b. Rebuild: the new hub owns it, built once, on as it was, without buying it again.
local D = rebuild(A, 204)
assert(Building.HasUpgrade(D, ID) and D:IsUpgradeOn(ID) and not A.upgrades_built[ID])
assert(count_mods() == 3 and small.max_storage_per_resource == 120000 and big.max_storage_per_resource == 240000, "doubled once")
assert(T1.max_shared_storage == 84000 and T1.max_colonists_to_transport == 24)
assert(not D.upgrades_under_construction, "not bought again")
assert(B:HasUpgrade(ID) and B:CanDisableUpgrade(ID) == false and D:CanDisableUpgrade(ID) == true)
D:ApplyCopyParams({}); assert(count_mods() == 3 and small.max_storage_per_resource == 120000, "idempotent")
rebuilt_on = { small.max_storage_per_resource, big.max_storage_per_resource, T1.max_shared_storage, T1.max_colonists_to_transport }

-- 6c. Toggled off before salvage: it comes back built but still off; the owner may switch it on.
D:ToggleUpgradeOnOff(ID); assert(not D:IsUpgradeOn(ID) and small.max_storage_per_resource == 60000)
salvage(D)
-- A Ctrl+click from spent B on the ruins: they keep the off state.
broadcast_toggle(B)
assert(not D:IsUpgradeOn(ID) and count_mods() == 0 and small.max_storage_per_resource == 60000, "ruins keep off")
-- Nor a direct switch with no spent hub selected (the ruins' own panel or hotkey).
D:ToggleUpgradeOnOff(ID); assert(not D:IsUpgradeOn(ID), "ruins refuse their own switch")
-- The modifier guard stands on its own, whatever reaches it (Building.lua:1145, TechTree.lua:1438).
D:ApplyUpgradeModifiersForUpgrade(ID); assert(count_mods() == 0, "ruins never apply")
-- Rebuild completing while spent B is selected: the carry still keeps the state off.
SelectedObj = B
local E = rebuild(D, 205)
SelectedObj = false
assert(Building.HasUpgrade(E, ID) and not E:IsUpgradeOn(ID), "built, still off")
assert(count_mods() == 0 and small.max_storage_per_resource == 60000 and T1.max_shared_storage == 42000)
assert(B:HasUpgrade(ID) and B:CanDisableUpgrade(ID) == false)
E:ToggleUpgradeOnOff(ID); assert(E:IsUpgradeOn(ID) and count_mods() == 3 and small.max_storage_per_resource == 120000)
rebuilt_off = { small.max_storage_per_resource, T1.max_shared_storage }

-- 6d. Load of a save whose ruins still carry the bonus (made before this ruling): switched off.
E.destroyed = true
assert(small.max_storage_per_resource == 120000)
OnMsg.LoadGame(); assert(count_mods() == 0 and small.max_storage_per_resource == 60000, "off on load")

-- 6e. Ruins cleared: Building:Done runs vanilla's StopUpgradeModifiers (Building.lua:534) and
-- CityObject's Done takes it out of its labels. The claim is released.
E:StopUpgradeModifiers(); remove(city.labels.Station, E); E.deleted = true
released = { small.max_storage_per_resource, big.max_storage_per_resource, B.max_storage_per_resource,
  T1.max_shared_storage, T1.max_colonists_to_transport }
assert(small.max_storage_per_resource == 60000 and B.max_storage_per_resource == 240000 and T1.max_shared_storage == 42000)
assert(small.demand.Metals.amount == 0 and small.supply.Metals.actual == 100000)
assert(not B:HasUpgrade(ID) and B:CanDisableUpgrade(ID) == true, "free again: " .. tostring(B:HasUpgrade(ID)) .. " " .. tostring(B:CanDisableUpgrade(ID)) .. " " .. #city.labels.Station)

-- 7. Re-buy on B; a third hub is refused while B builds, cancelled or not; B completes once.
local C = hub(203)
B.reqs_pending = { setmetatable({ GetResource = function() return "Metals" end, GetActualAmount = function() return 0 end }, req) }
B:ConstructUpgrade(ID); assert(B:IsUpgradeBeingConstructed(ID))
C:ConstructUpgrade(ID); assert(not C.upgrades_under_construction, "refused while B builds")
B:ConstructUpgrade(ID); assert(B.upgrades_under_construction[ID].canceled == true, "delivered resources: cancelled, kept")
C:ConstructUpgrade(ID); assert(not C.upgrades_under_construction, "refused while B's cancelled one can resume")
assert(not C:HasUpgrade(ID), "under construction elsewhere is not spent")
B:ApplyUpgrade(1)
assert(count_mods() == 3 and small.max_storage_per_resource == 120000 and C.max_storage_per_resource == 480000)
assert(C:HasUpgrade(ID) and C:CanDisableUpgrade(ID) == false)
rebought = { small.max_storage_per_resource, B.max_storage_per_resource, C.max_storage_per_resource,
  T1.max_shared_storage, T1.max_colonists_to_transport }
''')

g = lua.globals()
result = {
    "command": "python tools/devmods/train_hub/tests/capacity_smoke.py",
    "head": head,
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "vanilla_sha256": hashes,
    "vanilla_bodies_run": sum(len(v) for v in VANILLA.values()),
    "scope": "vanilla 1.1.1.405907 upgrade and resize bodies over mocked modifiers and labels; no native run, no save file",
    "applied (small, big, hub A, hub B, train cargo, train passengers)": list(g.applied.values()),
    "toggled off (small, big, hub A, train cargo, train passengers)": list(g.toggled_off.values()),
    "salvaged (small, big, train cargo, train passengers)": list(g.salvaged.values()),
    "rebuilt, was on (small, big, train cargo, train passengers)": list(g.rebuilt_on.values()),
    "rebuilt, was off, then switched on (small, train cargo)": list(g.rebuilt_off.values()),
    "ruins cleared (small, big, hub B, train cargo, train passengers)": list(g.released.values()),
    "re-bought on B (small, hub B, hub C, train cargo, train passengers)": list(g.rebought.values()),
    "result": "PASS",
}
print(json.dumps(result, indent=2))
