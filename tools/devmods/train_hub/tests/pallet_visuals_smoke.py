"""Desk reproduction of the 2026-09-27 pallet report (empty beds while stocked), and the heal.

Runs the archived vanilla column/cube bodies (1.1.1.405907) with the dev hub's own cargo
overrides. Reproduces the stale-split state: a hub whose column split was derived when
GetTotalStorageColumns() returned 240 (four stand-in sub-depots) draws every stocked
resource on four of six beds after the asset's six pallets arrive, because nothing
recomputes the persisted split. Then verifies HealCargoColumns re-derives the split on
load, restores the spec-Sec10 look (18/19 columns a resource, max_z 9, all six beds
carry columns), and is idempotent and silent when the split is already right.
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
MOD = ROOT / "tools/devmods/train_hub"
SOURCE = MOD / "Code/20_TrainHub.lua"
ARCHIVE = Path(r"B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.1.1.405907\Src\Lua")

VANILLA = {
    "Buildings/MultiResourceCubeVisuals.lua": [
        "MultiResourceCubeVisuals:SetCount",
        "MultiResourceCubeVisuals:SetCountColumnAlloc",
        "MultiResourceCubeVisuals:TakesVisualSpace",
        "MultiResourceCubeVisuals:PartitionVisualResources",
        "MultiResourceCubeVisuals:RecalculateCapacityColumns",
        "MultiResourceCubeVisuals:UpdateVisualCount",
        "MultiResourceCubeVisuals:RepositionCubes",
        "MultiResourceCubeVisuals:ReallocateVisualColumns",
        "MultiResourceCubeVisuals:GetMaxStorage",
    ],
    "Buildings/MultiResourceDepot.lua": [
        "MultiResourceDepotBase:UpdateVisualCount",
        "MultiResourceDepotBase:RecalculateCapacityColumns",
        "MultiResourceDepotBase:ReallocateVisualColumns",
    ],
    "Buildings/Station.lua": [
        "Station:GetTotalStorageColumns",
    ],
}


def extract(text, name):
    m = re.search(r"^function %s\(.*?^end\n" % re.escape(name), text, re.S | re.M)
    assert m, "vanilla body not found: " + name
    return m.group(0)


def integer_divisions(body, sites, label):
    """Engine integer resource arithmetic (EF-116): the game's Lua divides integers to an
    integer; lupa's does not. Every division in these pinned bodies is a nonnegative
    count / count, so `//` is exact. Fail closed if a source change adds another shape."""
    assert body.count(" / ") == sites, \
        "%s: expected %d division sites, found %d" % (label, sites, body.count(" / "))
    assert body.count("/") == sites, "%s: a division outside the counted shape" % label
    return body.replace(" / ", " // ")


def main():
    print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    print("HEAD:", head, flush=True)

    vanilla = []
    for rel, names in VANILLA.items():
        path = ARCHIVE / rel
        print(rel, "sha256:", hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
        text = path.read_text(encoding="utf8").replace("\r\n", "\n")
        vanilla += [extract(text, n) for n in names]
    vanilla = [integer_divisions("\n".join(vanilla), 3, "vanilla bodies")]

    code = SOURCE.read_text(encoding="utf8")
    cargo = code[code.index("local function own_pallets(self)"):
                 code.index("-- Load. Markers and the reactor helper are unsaved.")]
    cargo = cargo[:cargo.rindex("-- =====")]
    cargo = integer_divisions(cargo, 6, "hub cargo block")
    assert "function SMROptInTrainHubBase:HealCargoColumns()" in cargo, \
        "the heal lives in the cargo-on-show block"
    heal_after_load = code[code.index("local function heal_after_load(hub)"):
                           code.index("function OnMsg.LoadGame()")]
    assert "hub:HealCargoColumns()" in heal_after_load, "heal_after_load runs the cargo heal"

    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(r'''
empty_table = {}
ResourceScale = 1000
const = { ResourceScale = 1000 }
function Min(a, b) return a < b and a or b end
function Max(a, b) return a > b and a or b end
function IsValid(o) return type(o) == "table" and not o.deleted end
printed = {}
local rawprint = print
function print(line) printed[#printed + 1] = line end
function DoneObject(o) o.deleted = true end
function PlaceObjectIn(cls, map, init) return { resource = init.resource } end
Resources = {
  BlackCube = { visually_placed_in_storage = false },
  MysteryResource = { visually_placed_in_storage = false },
}

-- Integer world points; angle 0 everywhere, so Rotate is the identity.
local point_mt
point_mt = { __add = function(a, b) return setmetatable({ a[1]+b[1], a[2]+b[2], a[3]+b[3] }, point_mt) end,
             __sub = function(a, b) return setmetatable({ a[1]-b[1], a[2]-b[2], a[3]-b[3] }, point_mt) end }
function point(x, y, z) return setmetatable({ x, y, z }, point_mt) end
function Rotate(p, a) assert(a == 0, "the desk fixture keeps every angle at 0") return p end

MultiResourceCubeVisuals, MultiResourceDepotBase, Station = {}, {}, {}
CObject = {
  HasSpot = function(self, name) return self.box_spots ~= nil end,
  GetSpotLoc = function(self, spot) return point((spot - self.box_first) * 1000000, 0, 0), 0 end,
}
''')
    for body in vanilla:
        lua.execute(body)
    lua.execute(r'''
SMROptInTrainHubBase = {}
MultiResourceDepotBase.SetCount = MultiResourceCubeVisuals.SetCount
MultiResourceDepotBase.GetMaxStorage = MultiResourceCubeVisuals.GetMaxStorage
''')
    lua.execute(cargo)
    lua.execute(r'''
-- Flat method table: the hub's own methods win, then the depot's gated forwards,
-- then the cube bodies (vanilla's resolution order for what this smoke touches).
Hub = {}
for _, cls in ipairs({ SMROptInTrainHubBase, MultiResourceDepotBase, MultiResourceCubeVisuals }) do
  for k, v in pairs(cls) do if Hub[k] == nil then Hub[k] = v end end
end
Hub.__index = Hub
function Hub:GetAttaches(cls) return self.attaches[cls] end
function Hub:GetSpotRange(name) assert(name == "Box1") return self.box_first, self.box_last end
function Hub:GetPos() return point(0, 0, 0) end
function Hub:GetAngle() return 0 end
function Station.GetCubePosRelative() assert(false, "the fallback draw path must not run here") end

ORDER = { "BlackCube", "MysteryResource", "Metals", "Concrete", "Food", "PreciousMetals",
  "PreciousMinerals", "Polymers", "MachineParts", "Electronics", "Fuel", "Seeds", "WasteRock",
  "Herbs", "Spices", "Sugar", "Butter", "Bread", "Cheese", "Coffee", "Meat" }

-- The owner's panel, 2026-09-27 (leaf figures as shown; group remainders split so every
-- group total is exact: Advanced 700, Delicacies 1318, Other 360).
STOCK = { Metals = 251, Concrete = 150, Food = 161, PreciousMetals = 170, PreciousMinerals = 170,
  Polymers = 175, MachineParts = 175, Electronics = 175, Fuel = 175,
  Seeds = 0, WasteRock = 360,
  Herbs = 400, Spices = 300, Sugar = 0, Butter = 0, Bread = 300, Cheese = 0, Coffee = 0, Meat = 318 }

local req = {}
req.__index = req
function req:GetActualAmount() return self.actual end

function make_hub()
  local h = setmetatable({
    handle = 6430, has_visual_cubes = true, respect_visual_placement = true,
    max_storage_per_resource = 480000, max_x = 12, max_y = 5, switch_fill_order = true,
    box_diam = 100, spacing_x = 16, spacing_y = 13, box_height = 101, spacing_z = 0,
    cube_class = "cube", pending_removal = {},
    capacity_columns = {}, visual_col_start = {}, visual_cubes = {}, supply = {},
    attaches = {}, box_spots = true, box_first = 10, box_last = 15,
  }, Hub)
  h.storable_resources = {}
  for i, res in ipairs(ORDER) do
    h.storable_resources[i] = res
    h.storable_resources[res] = true
    h.visual_cubes[res] = {}
    if STOCK[res] then h.supply[res] = setmetatable({ actual = STOCK[res] * 1000 }, req) end
  end
  function h:GetMap() return {} end
  function h:Attach() end
  return h
end

-- One drawn picture: per-resource cube count and the set of beds carrying cubes.
function draw(h)
  for _, res in ipairs(ORDER) do
    if h.supply[res] then h:UpdateVisualCount(res) end
  end
  local beds, drawn = {}, {}
  for res, cubes in pairs(h.visual_cubes) do
    local n = 0
    for _, cube in ipairs(cubes) do
      if IsValid(cube) then
        n = n + 1
        beds[cube.offset[1] // 1000000] = true
      end
    end
    drawn[res] = n
  end
  local bed_count = 0
  for _ in pairs(beds) do bed_count = bed_count + 1 end
  return drawn, beds, bed_count
end
''')
    lua.execute(r'''
-- Cube placement is observable through the recorded attach offset.
function Hub:SetAttachOffset() end
local place = PlaceObjectIn
function PlaceObjectIn(cls, map, init) return { resource = init.resource } end
''')
    # SetCountColumnAlloc attaches then SetAttachOffset(pos); record the offset per cube.
    lua.execute(r'''
local alloc = MultiResourceCubeVisuals.SetCountColumnAlloc
-- Wrap nothing: instead record offsets by patching the cube's setter through Attach.
-- Vanilla calls self:Attach(cube); cube:SetAngle(0); cube:SetAttachOffset(pos).
-- Give every placed cube its own recorders.
function PlaceObjectIn(cls, map, init)
  local cube = { resource = init.resource }
  function cube:SetAngle() end
  function cube:SetAttachOffset(pos) cube.offset = pos end
  return cube
end
''')
    lua.execute(r'''
-- ==== The stale epoch: split derived while four stand-in sub-depots gave 240 columns.
local h = make_hub()
h.attaches.StorageDepotFood = { {}, {}, {}, {} }
assert(h:GetTotalStorageColumns() == 240, "stand-in epoch: 4 depots x 60")
h:RecalculateCapacityColumns()
h:RecalculateDerivedMaxZ()
assert(h.max_z == 13, "stale epoch height: ceil(150 / (240//19)) = 13, got " .. tostring(h.max_z))
assert(h.capacity_columns.Metals == 13 and h.capacity_columns.Meat == 12,
  "240 columns over 19 visible: first twelve resources take 13, the rest 12")
assert(h.visual_col_start.BlackCube == nil and h.capacity_columns.BlackCube == 12,
  "hidden resources hold columns but no start")

-- The asset arrives: six pallets, no sub-depots. Vanilla re-derives ONLY max_z (the
-- capacity upgrade's OnModifiableValueChanged), never the split. Live receipts: max_z 9
-- before and after the upgrade (capacity log 2026-09-26; boot dump 2026-09-27 23:52).
h.attaches.StorageDepotFood = nil
assert(h:GetTotalStorageColumns() == 360, "asset: 6 pallets x 60")
h:RecalculateDerivedMaxZ()
assert(h.max_z == 9, "the upgrade apply re-derives max_z to 9")

local drawn, beds, bed_count = draw(h)
assert(bed_count == 4 and not beds[4] and not beds[5],
  "stale split: every cube sits on the first four beds, two beds bare, got " .. bed_count)
assert(drawn.Metals == 13 * 9, "Metals under-draws at 13 cols x 9 of its intended 171")
assert(drawn.WasteRock == 13 * 9 and drawn.Herbs == 13 * 9 and drawn.Spices == 12 * 9,
  "each capped by its stale share: 13 columns through Herbs, 12 from Spices on")
local stale_total = 0
for _, n in pairs(drawn) do stale_total = stale_total + n end
print(string.format("[desk] stale picture: %d cubes, beds 0-3 only", stale_total))

-- ==== The heal: one load pass re-derives the split and repositions.
local before_prints = #printed
h:HealCargoColumns()
assert(#printed == before_prints + 1 and printed[#printed]:find("cargo columns re%-derived"),
  "a changed split logs the old values once")
assert(h.max_z == 9)
assert(h.capacity_columns.Metals == 19 and h.capacity_columns.Meat == 18,
  "360 columns over 19 visible: eighteen resources take 19, the last 18")
local col = 0
for _, res in ipairs(ORDER) do
  local start = h.visual_col_start[res]
  if Resources[res] == nil or Resources[res].visually_placed_in_storage ~= false then
    assert(start == col, res .. " starts at " .. tostring(start) .. ", want " .. col)
    col = col + h.capacity_columns[res]
  else
    assert(start == nil)
  end
end
assert(col == 360, "the split walks every column once, got " .. col)

drawn, beds, bed_count = draw(h)
assert(bed_count == 6, "healed: every bed carries cubes, got " .. bed_count)
for res, stock in pairs(STOCK) do
  if stock > 0 then
    local want = Min(stock, h.capacity_columns[res] * 9)
    assert(drawn[res] == want,
      res .. " draws " .. tostring(drawn[res]) .. ", want min(stock, cols x 9) = " .. want)
  end
end
assert(drawn.Metals == 171 and drawn.Concrete == 150,
  "fill up, excess stored invisibly: Metals caps at 171 of 251, Concrete draws all 150")
local healed_total = 0
for _, n in pairs(drawn) do healed_total = healed_total + n end
assert(healed_total > stale_total, "the heal draws more of the same stock")
print(string.format("[desk] healed picture: %d cubes over all six beds", healed_total))

-- ==== Idempotent and silent when the split is already right.
before_prints = #printed
local cols_before, start_before = {}, {}
for k, v in pairs(h.capacity_columns) do cols_before[k] = v end
for k, v in pairs(h.visual_col_start) do start_before[k] = v end
h:HealCargoColumns()
assert(#printed == before_prints, "a clean split logs nothing")
for k, v in pairs(cols_before) do assert(h.capacity_columns[k] == v) end
for k, v in pairs(start_before) do assert(h.visual_col_start[k] == v) end
drawn, beds, bed_count = draw(h)
assert(bed_count == 6)
for res, stock in pairs(STOCK) do
  if stock > 0 then assert(drawn[res] == Min(stock, h.capacity_columns[res] * 9)) end
end
''')
    for line in lua.eval("printed".strip()).values():
        print(line, flush=True)
    print("PASS stale 240-column split reproduces the report (four beds drawn, two bare, "
          "max_z 9 by the upgrade's own re-derive); HealCargoColumns restores 19/18-column "
          "slabs over all six beds, logs the old split once, and is a silent no-op when clean",
          flush=True)
    print("NOT TESTED: the live save's actual epoch (slot 2 reads it), engine spot "
          "geometry, and the game's own load order", flush=True)


if __name__ == "__main__":
    main()
