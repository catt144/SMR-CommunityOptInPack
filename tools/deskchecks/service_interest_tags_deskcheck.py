"""Desk check for Code/Opt_ServiceInterestTags.lua (D15). Desk-verified only: no game runs.

It runs the game's own 1.1.1.405907 bodies, taken from the archived tree at run time rather
than copied: the service description funnel and its three GetIPDescription callers, the
interest predicate (with the Medical override), the interest names, the two generated
infopanel sections whole, and the real BuildingTemplate data files. The module and this
repo's 00_Core.lua load on top of them. Mocked, and so not evidence: T rendering (eager, to
plain strings), the class system (__index chains standing in for flattening), window
construction, and a few leaf getters (capacity, stats, workers, shifts).

Four passes over the same buildings:
  vanilla    module not loaded
  off        module loaded, toggle off   -> must equal vanilla byte for byte
  on         toggle turned on through the real ApplyModOptions reconciler
  off-again  toggle turned off the same way -> must equal vanilla byte for byte
On: the build-menu hover gains the Interests line (under "Service <category>", or its own
block for a food service with no category), the placed building's Visitors section (or the
food service block) gains one Interests row, and the Encyclopedia call and the placed
building's description stay vanilla.

Run: python tools/deskchecks/service_interest_tags_deskcheck.py [--show]
Exit 0 = every assertion held. --show prints each surface for the record.
"""
from pathlib import Path
import sys

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[2]
BUILD = '1.1.1.405907'
SRC = Path(r'B:\Dev\SMR\SMR-Shared\SMR-SrcArchive') / BUILD / 'Src'
SHOW = '--show' in sys.argv

TEMPLATES = ['ShopsElectronics', 'CasinoComplex', 'Spacebar', 'MedicalCenter', 'Infirmary',
             'Diner', 'ShopsFood', 'MegaMall', 'GardenStone', 'LightDecorationSmall']
# (building, object class, host expected on the placed building, interests expected, in order)
CASES = [
    ('ShopsElectronics', 'visitors', 'Gaming, Shopping'),
    ('CasinoComplex', 'visitors', 'Social, Gaming, Luxury\nGambling'),
    ('MedicalCenter', 'visitors', 'Medical Checks'),
    ('Infirmary', 'visitors', 'Medical Checks'),
    ('Diner', 'food', 'Social, Dining, Food'),
    ('ShopsFood', 'food', 'Food'),
    ('MegaMall', 'visitors', 'Social, Relaxation, Exercise\nGaming, Shopping, Luxury\n'
                             'Drinking, Gambling, Playing\nDining, Food'),
    ('GardenStone', 'visitors', 'Relaxation, Exercise, Playing'),
    ('LightDecorationSmall', None, None),
]

receipts = []


def extract(rel, header, closer='end'):
    """The block starting at the line that begins with `header`, through the first line equal
    to `closer`. Recorded with its line span so the receipt cites what ran."""
    lines = (SRC / rel).read_text(encoding='utf8').splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith(header)]
    assert len(starts) == 1, (rel, header, starts)
    i = starts[0]
    j = next(k for k in range(i + 1, len(lines)) if lines[k] == closer)
    receipts.append('%s:%d-%d  %s' % (rel, i + 1, j + 1, header.strip()))
    return '\n'.join(lines[i:j + 1])


lua = LuaRuntime(unpack_returned_tuples=True)
g = lua.globals()

lua.execute(r'''
-- ---- mocks: T values render eagerly to strings --------------------------------------
local function render(text, params, ctx)
  return (text:gsub("<([%w_]+)>", function(tag)
    local v = params and params[tag]
    if v == nil and type(ctx) == "table" then
      local getter = ctx["Get" .. tag]
      if type(getter) == "function" then v = getter(ctx) else v = ctx[tag] end
    end
    if v == nil then return nil end
    return tostring(v)
  end))
end
RenderT = render
function T(a, b)
  if type(a) == "table" then
    local numbered = type(a[1]) == "number"
    local text = numbered and a[2] or a[1]
    local ctx = numbered and a[3] or a[2]
    return render(text, a, type(ctx) == "table" and ctx or nil)
  end
  return type(a) == "number" and b or a
end
function Untranslated(s) return s end
function TList(list, sep) return table.concat(list, sep or ", ") end
function set(...) local t = {} for _, v in ipairs({...}) do t[v] = true end return t end
function range(a, b) return {a, b} end
function IsValid(o) return type(o) == "table" and rawget(o, "__valid") == true end

-- ---- mock class system: __index chains stand in for flattening -------------------------
classes = {}
function DefineClassNamed(name, def)
  local c = def or {}
  c.class = name
  c.__parents = c.__parents or {}
  c.__index = c
  classes[name] = c
  rawset(_G, name, c)
  setmetatable(c, { __index = function(_, k)
    for _, p in ipairs(c.__parents) do
      local pc = classes[p]
      local v = pc and pc[k]
      if v ~= nil then return v end
    end
  end })
  return c
end
DefineClass = setmetatable({}, { __newindex = function(_, k, v) DefineClassNamed(k, v) end })
function UndefineClass() end
local function walk(n, want)
  if n == want then return true end
  local c = classes[n]
  if not c then return false end
  for _, p in ipairs(c.__parents) do if walk(p, want) then return true end end
  return false
end
function IsKindOf(o, want) return type(o) == "table" and type(o.class) == "string" and walk(o.class, want) end
function IsKindOfClasses(o, ...) for _, w in ipairs({...}) do if IsKindOf(o, w) then return true end end return false end
IsContextOfKind = IsKindOf

-- windows: new() builds the instance, appends it to its parent, then runs Init
local function new_window(cls, args, parent, context)
  local o = setmetatable(args or {}, cls)
  o.context = context
  o.idContent = {}
  if parent then parent[#parent + 1] = o end
  if o.Init then o:Init(parent, context) end
  return o
end
DefineClassNamed("XWindow", { new = new_window })
DefineClassNamed("InfopanelSection", { __parents = { "XWindow" }, new = new_window })
function InfopanelSection.__content(parent) return parent.idContent end
DefineClassNamed("InfopanelText", { __parents = { "XWindow" }, new = new_window })
function InfopanelText:SetText(t) self.Text = t end
DefineClassNamed("sectionIngredientRow", { __parents = { "XWindow" }, new = new_window })
function SubContext(ctx, t) t[1] = ctx return t end
function IsDlcAvailable() return true end

-- building classes, with the defaults the template-driven bodies read
DefineClassNamed("Building", { description = "", city = false, max_workers = 0 })
DefineClassNamed("ServiceBase", { same_category_as = "", category_name = "", filter_visitors = "Everyone",
  service_capacity = 5,
  interest1 = "", interest2 = "", interest3 = "", interest4 = "", interest5 = "", interest6 = "",
  interest7 = "", interest8 = "", interest9 = "", interest10 = "", interest11 = "" })
DefineClassNamed("Service", { __parents = { "Building", "ServiceBase" } })
DefineClassNamed("ShiftsBuilding", { __parents = { "Building" } })
DefineClassNamed("Workplace", { __parents = { "ShiftsBuilding" } })
DefineClassNamed("ServiceWorkplace", { __parents = { "Service", "Workplace" } })
DefineClassNamed("FoodBuilding", { __parents = { "Building" } })
DefineClassNamed("FoodServiceBuilding", { __parents = { "FoodBuilding", "ServiceWorkplace" }, max_meals = 0 })
DefineClassNamed("MedicalBuilding", { __parents = { "ServiceWorkplace" }, rejuvenation_upgrade = "" })
DefineClassNamed("MedicalCenterBase", { __parents = { "MedicalBuilding" }, rejuvenation_upgrade = "MedicalCenter_RejuvenationTreatment" })
DefineClassNamed("InfirmaryBase", { __parents = { "MedicalBuilding" }, rejuvenation_upgrade = "Infirmary_RejuvenationTreatment" })
DefineClassNamed("CasinoComplexBase", { __parents = { "ServiceWorkplace" } })
DefineClassNamed("SpacebarBase", { __parents = { "ServiceWorkplace" } })
DefineClassNamed("DinerBase", { __parents = { "FoodServiceBuilding" } })
DefineClassNamed("Grocery", { __parents = { "FoodServiceBuilding" } })
DefineClassNamed("MegaMallBase", { __parents = { "FoodServiceBuilding" } })
DefineClassNamed("Decoration", { __parents = { "Building" } })
DefineClassNamed("DecorationService", { __parents = { "Decoration", "Service" } })
DefineClassNamed("FlowerLamp", { __parents = { "DecorationService" } })
DefineClassNamed("FlowerLampSmall", { __parents = { "FlowerLamp" } })

-- leaf getters (mocked)
function GetModifierObject() return { ModifyValue = function(_, v) return v end } end
ColonistFilterDisplayName = {}
function ShiftsBuilding:GetUIDescriptionShifts()
  local n = 0
  for i = 1, 3 do if self["enabled_shift_" .. i] ~= false then n = n + 1 end end
  return n
end
function ServiceBase:GetUIStatText() return "+10 Comfort" end
function ServiceBase:GetUsedCapacity() return 2 end
function ServiceBase:GetServiceCapacity() return self.service_capacity end
function ServiceBase:GetOtherDomesUsedCapacity() return 0 end
function ServiceBase:GetUIEffectiveStatText() return "+10 Comfort" end
function ServiceBase:GetTipsLastSol() return 0 end
function Workplace:GetWorkersDescription(texts)
  if (self.max_workers or 0) > 0 then
    texts[#texts + 1] = ""
    texts[#texts + 1] = "Workers<right>" .. self.max_workers
  end
end
function FoodServiceBuilding:GetServeableIngredients() return {} end
function Building:IsUpgradeOn(id) return self.upgrades_on and self.upgrades_on[id] or false end
BuildingTemplates = {}

-- the Mod runtime the core reads
OnMsg = {}
function CreateRealTimeThread() end
CurrentModOptions = { ServiceInterestTags = false }
''')

vanilla = [
    ('Lua/Interests.lua', 'ServiceInterestsList = {', '}'),
    ('Lua/Interests.lua', 'Interests = {', '}'),
    ('Lua/Interests.lua', 'function GetInterestDisplayName(', 'end'),
    ('Lua/ServiceBase.lua', 'function ServiceBase:GetServiceCategory(', 'end'),
    ('Lua/ServiceBase.lua', 'function GetServiceCategoryDisplayName(', 'end'),
    ('Lua/ServiceBase.lua', 'function ServiceBase:IsOneOfInterests(', 'end'),
    ('Lua/Buildings/Service.lua', 'function Service:GetServiceDescription(', 'end'),
    ('Lua/Buildings/Service.lua', 'function Service:GetIPDescription(', 'end'),
    ('Lua/Buildings/Service.lua', 'function ServiceWorkplace:GetIPDescription(', 'end'),
    ('Lua/Buildings/FoodServiceBuilding.lua', 'function FoodServiceBuilding:GetIPDescription(', 'end'),
    ('Lua/Buildings/MedicalCenter.lua', 'function MedicalBuilding:IsRejuvenationTreatment(', 'end'),
    ('Lua/Buildings/MedicalCenter.lua', 'function MedicalBuilding:IsOneOfInterests(', 'end'),
]
for rel, header, closer in vanilla:
    lua.execute(extract(rel, header, closer))
for rel in ('Lua/XDef/sectionVisitors.generated.lua', 'Lua/XDef/sectionFoodService.generated.lua'):
    text = (SRC / rel).read_text(encoding='utf8')
    receipts.append('%s:1-%d  (whole file)' % (rel, len(text.splitlines())))
    lua.execute(text)

# Real template data: each becomes a class over its object_class, and BuildingTemplates[id]
# is the same shape the game builds (Buildings/Building.lua:2701).
lua.execute(r'''
function PlaceObj(_, t) LoadedTemplate = t end
function MakeTemplate(t)
  local id = t.id
  t.__parents = { t.object_class }
  DefineClassNamed(id, t)
  BuildingTemplates[id] = setmetatable({ template_name = id }, classes[id])
end
''')
for tid in TEMPLATES:
    rel = 'Data/BuildingTemplate/%s.lua' % tid
    lua.execute((SRC / rel).read_text(encoding='utf8'))
    receipts.append('%s  (data)' % rel)
    lua.eval('MakeTemplate')(g.LoadedTemplate)

lua.execute(r'''
function Placed(id, upgrades)
  return setmetatable({ __valid = true, upgrades_on = upgrades, serveable_ingredients = {},
    city = upgrades and { colony = { IsTechResearched = function() return true end } } or false },
    classes[id])
end
function RowTexts(section)
  local out = {}
  local function collect(win)
    for _, child in ipairs(win) do
      if IsKindOf(child, "InfopanelText") then
        out[#out + 1] = RenderT(child.Text, nil, child.context)
      end
      if child.idContent then collect(child.idContent) end
      collect(child)
    end
  end
  if section then
    collect(section.idContent)
    collect(section)
  end
  return table.concat(out, " | ")
end
function Surfaces(id, upgrades)
  local tmpl = BuildingTemplates[id]
  local oc = classes[tmpl.object_class]
  local obj = Placed(id, upgrades)
  local visitors = sectionVisitors:new(nil, nil, obj)
  local food = sectionFoodService:new(nil, nil, obj)
  return {
    build_menu = oc.GetIPDescription(tmpl),
    encyclopedia = oc.GetIPDescription(tmpl, ": ", true),
    placed_description = obj:GetIPDescription(),
    visitors = visitors and RowTexts(visitors) or "(no section)",
    food = food and RowTexts(food) or "(no section)",
  }
end
''')


def snapshot():
    out = {}
    for tid, _, _ in CASES:
        s = lua.eval('Surfaces')(tid)
        out[tid] = {k: s[k] for k in s.keys()}
    s = lua.eval('Surfaces')('MedicalCenter', lua.table_from({'MedicalCenter_RejuvenationTreatment': True}))
    out['MedicalCenter+rejuvenation'] = {k: s[k] for k in s.keys()}
    return out


failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


passes = {'vanilla': snapshot()}

for rel in ('Code/00_Core.lua', 'Code/Opt_ServiceInterestTags.lua'):
    lua.execute((ROOT / rel).read_text(encoding='utf8'))
status = lambda: lua.eval('SMROptInPack.fixes.ServiceInterestTags.status')
check(status() == 'inactive', 'toggle off at load: status %r, want inactive' % status())
passes['off'] = snapshot()

g.CurrentModOptions.ServiceInterestTags = True
lua.eval('OnMsg.ApplyModOptions')('SMR_CommunityOptInPack')
check(status() == 'active', 'toggle on: status %r, want active' % status())
passes['on'] = snapshot()

g.CurrentModOptions.ServiceInterestTags = False
lua.eval('OnMsg.ApplyModOptions')('SMR_CommunityOptInPack')
check(status() == 'inactive', 'toggle off again: status %r, want inactive' % status())
passes['off-again'] = snapshot()

van, on = passes['vanilla'], passes['on']
for name in ('off', 'off-again'):
    check(passes[name] == van, '%s differs from vanilla' % name)

for tid, host, want in CASES + [('MedicalCenter+rejuvenation', 'visitors', 'Relaxation, Medical Checks')]:
    v, o = van[tid], on[tid]
    for surface in ('encyclopedia', 'placed_description'):
        check(o[surface] == v[surface], '%s %s changed with the toggle on' % (tid, surface))
    if want is None:
        for surface in v:
            check(o[surface] == v[surface], '%s %s changed (not covered, must stay vanilla)' % (tid, surface))
        continue
    line = 'Interests<right>' + want
    # The build menu hovers the template, which never has an upgrade on: Rejuvenation's
    # Relaxation shows on the placed building only.
    bm_line = 'Interests<right>Medical Checks' if tid == 'MedicalCenter+rejuvenation' else line
    bm_v = v['build_menu'].split('<newline><left>')
    bm_o = o['build_menu'].split('<newline><left>')
    check(bm_o.count(bm_line) == 1, '%s build menu lacks %r' % (tid, bm_line))
    if bm_line in bm_o:
        i = bm_o.index(bm_line)
        rest = bm_o[:i] + bm_o[i + 1:]
        if host == 'visitors':
            check(bm_o[i - 1].startswith('<em>Service</em>'), '%s line not under the category line' % tid)
            check(rest == bm_v, '%s build menu changed beyond the one line' % tid)
        else:
            check(bm_o[i - 1] == '' and rest[:i - 1] == bm_v[:i - 1] and rest[i:] == bm_v[i - 1:],
                  '%s food block: want "" + line added before the Meals block' % tid)
    other = 'food' if host == 'visitors' else 'visitors'
    check(o[other] == v[other], '%s %s host changed (want no row there)' % (tid, other))
    check(o[host] == (v[host] + ' | ' if v[host] else '') + line,
          '%s %s: want vanilla rows then the Interests row, got %r' % (tid, host, o[host]))

# The row follows the building live: turn Rejuvenation on under an open Visitors section.
g.CurrentModOptions.ServiceInterestTags = True
lua.eval('OnMsg.ApplyModOptions')('SMR_CommunityOptInPack')
live = lua.eval('''(function()
  local obj = Placed("MedicalCenter")
  local sec = sectionVisitors:new(nil, nil, obj)
  local row = sec.idContent[#sec.idContent]
  local before = row.Text
  obj.upgrades_on = { MedicalCenter_RejuvenationTreatment = true }
  obj.city = { colony = { IsTechResearched = function() return true end } }
  row:OnContextUpdate(obj)
  return before, row.Text
end)()''')
check(live == ('Interests<right>Medical Checks', 'Interests<right>Relaxation, Medical Checks'),
      'live context update: %r' % (live,))

print('Desk check: Opt_ServiceInterestTags (D15), vanilla bodies from %s' % BUILD)
print('Ran, from the archived tree:')
for r in receipts:
    print('  ' + r)
if SHOW:
    for tid in on:
        print('\n== %s' % tid)
        for surface in ('build_menu', 'visitors', 'food'):
            print('  [%s] vanilla: %s' % (surface, van[tid][surface].replace('<newline><left>', ' / ')))
            print('  [%s] on:      %s' % (surface, on[tid][surface].replace('<newline><left>', ' / ')))
    print('\n  live update: %r -> %r' % live)
n_cases = len(CASES) + 1
if failures:
    print('FAIL: %d of the assertions over %d buildings' % (len(failures), n_cases))
    for f in failures:
        print('  - ' + f)
    sys.exit(1)
print('PASS: %d buildings x 4 passes (vanilla / off / on / off-again), 5 surfaces each, '
      'plus the live Rejuvenation update' % n_cases)
