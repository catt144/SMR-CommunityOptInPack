"""Desk check for Code/Opt_ServiceInterestTags.lua (D15). Desk-verified only: no game runs.

It runs the game's own 1.1.1.405907 code and data, taken from the archived tree at run time
rather than copied: the service description funnel and its three GetIPDescription callers, the
interest predicate (with the Medical override), the interest names, the two generated infopanel
sections whole, ColonistStat and ColonistFilterDisplayName, every TraitPreset, and the real
BuildingTemplate data files. The module and this repo's 00_Core.lua load on top of them.
Mocked, and so not evidence: T rendering (eager, to plain strings), the class system (__index
chains standing in for flattening), window construction (append to the parent, then Init, as
XWindow:Init does), g_Consts, and a few leaf getters (capacity, stats, workers, shifts).

Four passes over the same buildings:
  vanilla    module not loaded
  off        module loaded, toggle off   -> must equal vanilla byte for byte
  on         toggle turned on through the real ApplyModOptions reconciler
  off-again  toggle turned off the same way -> must equal vanilla byte for byte
On (owner rulings 2026-09-28 and 2026-09-29): the build-menu hover gains the Interests line
(under "Service <category>", or its own block for a food service with no category); the placed
building gains exactly one "Interests" section, directly after its Visitors section (or the food
section for a Diner or Grocer), whose body is the interest list and whose popout carries the
description, category, visitor filter and the trait effects that apply there. Vanilla sections'
own rows, the Encyclopedia call and the placed building's description stay vanilla.

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
             'Diner', 'ShopsFood', 'MegaMall', 'GardenStone', 'OpenAirGym', 'Playground',
             'LightDecorationSmall']
# (building, host section, interests body, trait display names in order, filter line or None,
#  category line expected)
CASES = [
    ('ShopsElectronics', 'visitors', 'Gaming, Shopping', ['Gamer'], 'Adults', True),
    ('CasinoComplex', 'visitors', 'Social, Gaming, Luxury\nGambling',
     ['Gamer', 'Party Animal', 'Gambler'], 'Adults', True),
    ('MedicalCenter', 'visitors', 'Medical Checks', [], None, True),
    ('Infirmary', 'visitors', 'Medical Checks', [], None, True),
    ('Diner', 'food', 'Social, Dining, Food', ['Party Animal', 'Glutton', 'Vegan'], None, False),
    ('ShopsFood', 'food', 'Food', ['Glutton', 'Vegan'], None, False),
    ('MegaMall', 'visitors', 'Social, Relaxation, Exercise\nGaming, Shopping, Luxury\n'
                             'Drinking, Gambling, Playing\nDining, Food',
     ['Gamer', 'Party Animal', 'Glutton', 'Vegan'], None, True),
    ('GardenStone', 'visitors', 'Relaxation, Exercise, Playing', ['Hippie'], None, True),
    ('OpenAirGym', 'visitors', 'Social, Exercise', ['Party Animal', 'Fit'], 'Adults', True),
    ('Playground', 'visitors', 'Playing', ['Child'], 'Children', True),
    ('LightDecorationSmall', None, None, None, None, None),
]
# The popout's trait lines must carry the trait's number the game's way.
TRAIT_AMOUNT = {'Gamer': '+10', 'Party Animal': '+10', 'Gambler': '-20', 'Hippie': '+10',
                'Fit': '10%', 'Child': '100%'}

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
  text = text:gsub("<delta%(([%w_]+)%)>", function(tag)
    local v = params and tonumber(params[tag])
    if v == nil then return nil end
    return (v > 0 and "+" or "") .. tostring(v)
  end)
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
stat_scale = 1000
const = { Scale = { Stat = 1000 } }
g_Consts = { positive_playground_chance = 100 }  -- Lua/__const.lua:326-329, mocked

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

-- windows: new() appends the instance to its parent, then runs Init (XWindow:Init's order)
local function new_window(cls, args, parent, context)
  local o = setmetatable(args or {}, cls)
  o.context = context
  o.parent = parent
  o.idContent = {}
  o.visible = true
  if parent then parent[#parent + 1] = o end
  if o.Init then o:Init(parent, context) end
  return o
end
DefineClassNamed("XWindow", { new = new_window })
function XWindow:SetVisible(v) self.visible = v end
function XWindow:SetRolloverText(t) self.RolloverText = t end
function XWindow:SetTitle(t) self.Title = t end
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
DefineClassNamed("FitService", { __parents = { "Service" } })
DefineClassNamed("OpenAirGymBase", { __parents = { "FitService" } })
DefineClassNamed("PlaygroundBase", { __parents = { "Service" } })

-- leaf getters (mocked)
function GetModifierObject() return { ModifyValue = function(_, v) return v end } end
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
TraitPresets = {}

-- the Mod runtime the core reads
OnMsg = {}
function CreateRealTimeThread() end
CurrentModOptions = { ServiceInterestTags = false }
''')

vanilla = [
    ('Lua/Interests.lua', 'ServiceInterestsList = {', '}'),
    ('Lua/Interests.lua', 'Interests = {', '}'),
    ('Lua/Interests.lua', 'function GetInterestDisplayName(', 'end'),
    ('Lua/Stats.lua', 'ColonistFilterDisplayName = {', '}'),
    ('Lua/Units/Colonist.lua', 'ColonistStat =', '}'),
    ('Lua/Units/Colonist.lua', 'for stat_name, stat in pairs(ColonistStat) do', 'end'),
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

# Real data. Each template becomes a class over its object_class, and BuildingTemplates[id]
# is the same shape the game builds (Buildings/Building.lua:2701).
lua.execute(r'''
function PlaceObj(class, t)
  if class == "TraitPreset" then TraitPresets[t.id] = t end
  LoadedTemplate = t
  return t
end
function MakeTemplate(t)
  local id = t.id
  t.__parents = { t.object_class }
  DefineClassNamed(id, t)
  BuildingTemplates[id] = setmetatable({ template_name = id }, classes[id])
end
''')
lua.execute((SRC / 'Data/TraitPreset.lua').read_text(encoding='utf8'))
receipts.append('Data/TraitPreset.lua  (data, %d traits)' % len(list(g.TraitPresets.keys())))
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
        out[#out + 1] = RenderT(child.Text or "", nil, child.context)
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
-- the panel as ipBuilding builds it: both sections into one content window, in order
function Surfaces(id, upgrades)
  local tmpl = BuildingTemplates[id]
  local oc = classes[tmpl.object_class]
  local obj = Placed(id, upgrades)
  local content = {}
  local visitors = sectionVisitors:new(nil, content, obj)
  local food = sectionFoodService:new(nil, content, obj)
  local order, interests = {}, {}
  for i, child in ipairs(content) do
    if child == visitors then order[#order + 1] = "visitors"
    elseif child == food then order[#order + 1] = "food"
    elseif child.Title == "Interests" then
      order[#order + 1] = "interests"
      interests[#interests + 1] = child
    else order[#order + 1] = "other" end
  end
  local sec = interests[1]
  return {
    build_menu = oc.GetIPDescription(tmpl),
    encyclopedia = oc.GetIPDescription(tmpl, ": ", true),
    placed_description = obj:GetIPDescription(),
    visitors = visitors and RowTexts(visitors) or "(no section)",
    food = food and RowTexts(food) or "(no section)",
    order = table.concat(order, ","),
    interests_count = #interests,
    interests_visible = sec and tostring(sec.visible) or "",
    interests_body = sec and RowTexts(sec) or "",
    interests_icon = sec and sec.Icon or "",
    popout = sec and (sec.RolloverText or "") or "",
    description = RenderT(tmpl.description or "", nil, obj),
  }
end
''')


def snapshot():
    out = {}
    for case in CASES:
        s = lua.eval('Surfaces')(case[0])
        out[case[0]] = {k: s[k] for k in s.keys()}
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

rejuv = ('MedicalCenter+rejuvenation', 'visitors', 'Relaxation, Medical Checks', [], None, True)
for tid, host, want, traits, filt, has_cat in CASES + [rejuv]:
    v, o = van[tid], on[tid]
    for surface in ('encyclopedia', 'placed_description', 'visitors', 'food'):
        check(o[surface] == v[surface], '%s %s changed with the toggle on' % (tid, surface))
    if want is None:
        for surface in v:
            check(o[surface] == v[surface], '%s %s changed (not covered, must stay vanilla)' % (tid, surface))
        continue

    # build menu: one line, placed as before
    # The build menu hovers the template, which never has an upgrade on: Rejuvenation's
    # Relaxation shows on the placed building only.
    bm_want = 'Medical Checks' if tid == 'MedicalCenter+rejuvenation' else want
    bm_line = 'Interests<right>' + bm_want
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

    # placed building: one section, straight after its host, vanilla order otherwise
    # MegaMall is a food service with a category: Visitors, then the food section
    want_v = 'visitors,food' if tid == 'MegaMall' else host
    want_o = want_v.replace(host, host + ',interests')
    check(v['order'] == want_v, '%s vanilla panel order %r, want %r' % (tid, v['order'], want_v))
    check(o['order'] == want_o, '%s panel order %r, want %r' % (tid, o['order'], want_o))
    check(o['interests_count'] == 1, '%s has %d Interests sections' % (tid, o['interests_count']))
    check(o['interests_visible'] == 'true', '%s Interests section hidden' % tid)
    check(o['interests_body'] == want, '%s section body %r, want %r' % (tid, o['interests_body'], want))
    check(o['interests_icon'].startswith('UI/IconsRemaster/Sections/'), '%s icon %r' % (tid, o['interests_icon']))

    pop = o['popout'].split('<newline><left>')
    desc = v['description']
    check(bool(desc) and pop[0] == desc, '%s popout does not open with the description' % tid)
    cat_lines = [l for l in pop if l.startswith('Service<right><em>')]
    check(len(cat_lines) == (1 if has_cat else 0), '%s category lines %r' % (tid, cat_lines))
    filt_lines = [l for l in pop if l.startswith('Visitors<right>')]
    check(filt_lines == (['Visitors<right>' + filt] if filt else []), '%s filter lines %r' % (tid, filt_lines))
    trait_names = [l.split('<right>')[0] for l in pop[pop.index('<em>Traits</em>') + 1:]] \
        if '<em>Traits</em>' in pop else []
    check(trait_names == traits, '%s traits %r, want %r' % (tid, trait_names, traits))
    for l in pop:
        name = l.split('<right>')[0]
        if name in TRAIT_AMOUNT and name in traits:
            check(TRAIT_AMOUNT[name] in l, '%s %s line lacks %s: %r' % (tid, name, TRAIT_AMOUNT[name], l))

# The section follows the building live: turn Rejuvenation on under an open panel.
g.CurrentModOptions.ServiceInterestTags = True
lua.eval('OnMsg.ApplyModOptions')('SMR_CommunityOptInPack')
live = lua.eval('''(function()
  local obj = Placed("MedicalCenter")
  local content = {}
  sectionVisitors:new(nil, content, obj)
  local sec = content[#content]
  local before = RowTexts(sec)
  obj.upgrades_on = { MedicalCenter_RejuvenationTreatment = true }
  obj.city = { colony = { IsTechResearched = function() return true end } }
  sec:OnContextUpdate(obj)
  return before, RowTexts(sec)
end)()''')
check(live == ('Medical Checks', 'Relaxation, Medical Checks'), 'live context update: %r' % (live,))


# Conditional lines (owner, 2026-09-29): the norman DLC's data, then the Food Tours law.
# Everything above ran without either, so their lines were already proven absent.
def traits_of(popout):
    pop = popout.split('<newline><left>')
    if '<em>Traits</em>' not in pop:
        return [], pop
    rest = pop[pop.index('<em>Traits</em>') + 1:]
    return [l.split('<right>')[0] for l in rest], rest


lua.execute(r'''
StatsImpacts = {}
function PlaceObj(class, t)
  if type(t[1]) == "string" then          -- array-style key/value pairs
    local kv = {}
    for i = 1, #t, 2 do kv[t[i]] = t[i + 1] end
    t = kv
  end
  if class == "TraitPreset" then TraitPresets[t.id] = t end
  if class:find("^StatsImpact") and t.id then StatsImpacts[t.id] = t end
  if class == "LawDef" then LoadedLaws = LoadedLaws or {} LoadedLaws[t.id] = t end
  LoadedTemplate = t
  return t
end
DefineClassNamed("BaristaCafe", { __parents = { "ServiceWorkplace" } })
''')
for rel in ('DLC/norman/Presets/TraitPreset.lua', 'DLC/norman/Presets/StatsImpact.lua'):
    lua.execute((SRC / rel).read_text(encoding='utf8'))
    receipts.append('%s  (data, norman DLC)' % rel)
for tid in ('CoffeeVendingMachine', 'BaristaCafe'):
    rel = 'DLC/norman/Presets/BuildingTemplate/%s.lua' % tid
    lua.execute((SRC / rel).read_text(encoding='utf8'))
    receipts.append('%s  (data, norman DLC)' % rel)
    lua.eval('MakeTemplate')(g.LoadedTemplate)
rel = 'DLC/norman/Presets/LawDef/LawDef-Food.lua'
lua.execute((SRC / rel).read_text(encoding='utf8'))
receipts.append('%s  (data, norman DLC)' % rel)

conditional = {}
for label, law_on in (('dlc', False), ('dlc+law', True), ('dlc+law-off', False)):
    lua.execute('ActiveLaws = %s' % ('{ Policy_FoodTours = LoadedLaws.Policy_FoodTours }' if law_on else '{}'))
    conditional[label] = {tid: lua.eval('Surfaces')(tid)['popout']
                          for tid in ('Diner', 'ShopsFood', 'MegaMall', 'BaristaCafe', 'ShopsElectronics')}

want = {
    'dlc': {
        'Diner': ['Party Animal', 'Glutton', 'Vegan', 'Foodie'],
        'ShopsFood': ['Glutton', 'Vegan', 'Foodie'],
        'MegaMall': ['Gamer', 'Party Animal', 'Glutton', 'Vegan', 'Foodie'],
        'BaristaCafe': ['Party Animal', 'Coffee Enthusiast'],
        'ShopsElectronics': ['Gamer'],
    },
}
want['dlc+law'] = {k: v + ['Tourist'] if k in ('Diner', 'ShopsFood', 'MegaMall') else v
                   for k, v in want['dlc'].items()}
want['dlc+law-off'] = want['dlc']
for label, per in want.items():
    for tid, names in per.items():
        got, lines = traits_of(conditional[label][tid])
        check(got == names, '%s %s traits %r, want %r' % (label, tid, got, names))
        for l in lines:
            if l.startswith('Foodie<right>'):
                check('+5' in l and 'delicacies' in l, '%s %s Foodie line %r' % (label, tid, l))
            if l.startswith('Coffee Enthusiast<right>'):
                check('+10' in l and '-10 without' in l and 'Coffee' in l, '%s %s Coffee line %r' % (label, tid, l))
            if l.startswith('Tourist<right>'):
                check('+10' in l and '3x' in l and 'Food Tours' in l, '%s %s Tourist line %r' % (label, tid, l))

# the law line follows the law live under one open panel
live_law = lua.eval('''(function()
  ActiveLaws = {}
  local obj = Placed("Diner")
  local content = {}
  sectionFoodService:new(nil, content, obj)
  local sec = content[#content]
  local function has() return (sec.RolloverText or ""):find("Tourist<right>", 1, true) ~= nil end
  local before = has()
  ActiveLaws = { Policy_FoodTours = LoadedLaws.Policy_FoodTours }
  sec:OnContextUpdate(obj)
  local enacted = has()
  ActiveLaws = {}
  sec:OnContextUpdate(obj)
  return before, enacted, has()
end)()''')
check(live_law == (False, True, False), 'live law toggle (before, enacted, repealed): %r' % (live_law,))
if SHOW:
    for label in conditional:
        for tid in ('Diner', 'BaristaCafe'):
            print('  [%s %s] %s' % (label, tid, ' | '.join(traits_of(conditional[label][tid])[1])))

print('Desk check: Opt_ServiceInterestTags (D15), vanilla code and data from %s' % BUILD)
print('Ran, from the archived tree:')
for r in receipts:
    print('  ' + r)
if SHOW:
    for tid in on:
        print('\n== %s' % tid)
        print('  [build_menu] on: %s' % on[tid]['build_menu'].replace('<newline><left>', ' / '))
        print('  [panel]      vanilla: %s   on: %s' % (van[tid]['order'], on[tid]['order']))
        print('  [section]    %s' % on[tid]['interests_body'].replace('\n', ' / '))
        for line in on[tid]['popout'].split('<newline><left>'):
            print('  [popout]     %s' % line)
    print('\n  live update: %r -> %r' % live)
n_cases = len(CASES) + 1
if failures:
    print('FAIL: %d of the assertions over %d buildings' % (len(failures), n_cases))
    for f in failures:
        print('  - ' + f)
    sys.exit(1)
print('PASS: %d buildings x 4 passes (vanilla / off / on / off-again): build-menu hover, '
      'Encyclopedia, placed description, vanilla section rows, the Interests section '
      '(place, body, popout), the live Rejuvenation update, and the conditional lines '
      '(norman DLC data loaded; Food Tours law on, off, and toggled live)' % n_cases)
