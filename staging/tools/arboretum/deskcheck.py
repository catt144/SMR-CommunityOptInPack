"""Arboretum staffing, Seeds, visitor bonus, display beds and build-lock controls; not an in-game measurement."""
import json
import re
import subprocess
from pathlib import Path
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[2]
SRC = Path('B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src')
CROPS = Path('B:/Dev/SMR/SMR-Assets/arboretum/reference/crops/props.json')
MESHES = Path('B:/Dev/SMR/SMR-Assets/arboretum/reference/meshes/props.json')
MODULE = ROOT / 'Code/Opt_Arboretum.lua'
TEMPLATE = json.loads((Path(__file__).with_name('template.json')).read_text(encoding='utf-8'))


def body(path, name):
    source = (SRC / path).read_text(encoding='utf-8')
    match = re.search(r'^function ' + re.escape(name) + r'\([^\n]*\).*?^end\s*$', source, re.M | re.S)
    if not match:
        raise RuntimeError(name)
    return match.group()


# Source gate: the game divides int / int as integers, lupa does not (EF-116). The module must
# not use `/` at all outside comments and strings, so the desk results cannot hide a division.
code = MODULE.read_text(encoding='utf-8')
stripped = re.sub(r'--[^\n]*', '', re.sub(r'"(?:[^"\\\n]|\\.)*"', '""', code))
assert '/' not in stripped, 'module code uses "/" (integer division in game)'
# Upgrade ids in the module must be the template's.
lua_ids = dict(re.findall(r'^local (UPGRADE_\w+) = "([^"]+)"', code, re.M))
props = TEMPLATE['properties']
assert lua_ids == {'UPGRADE_BOTS': props['upgrade1_id'], 'UPGRADE_BLOOMS': props['upgrade2_id'],
                   'UPGRADE_SPECIMENS': props['upgrade3_id']}, lua_ids
assert all(v.startswith('SMROptIn') for v in lua_ids.values())

# Crop stage counts and footprints from the survey, keyed by entity.
survey = json.loads(CROPS.read_text(encoding='utf-8'))['entities']
crops = {name: (len(e['stages']), e['max_cm'][0] - e['min_cm'][0], e['max_cm'][1] - e['min_cm'][1])
         for name, e in survey.items()}
# Vanilla shrubs (one state) and their largest horizontal half-size, for the Specimen default.
meshes = json.loads(MESHES.read_text(encoding='utf-8'))['entities']
bushes = {name: e for name, e in meshes.items() if re.fullmatch(r'Bush_0[1-6]', name)}
assert len(bushes) == 6, sorted(bushes)
for name, e in bushes.items():
    crops[name] = (1, e['max_cm'][0] - e['min_cm'][0], e['max_cm'][1] - e['min_cm'][1])
bush_half = {name: max(abs(v) for v in e['min_cm'][:2] + e['max_cm'][:2]) for name, e in bushes.items()}

lua = LuaRuntime()
lua.execute('''
DefineClass = setmetatable({}, {__newindex=function(t,k,v) rawset(t,k,v); _G[k]=v end})
OnMsg = {}; HasConsumption = {}; Service = {}; ServiceBase = {}; ServiceWorkplace = {}
Workplace = {}; ShiftsBuilding = {}; Building = {}
function Untranslated(s) return s end
function UndefineClass() end
function set(...) local t={} for _, k in ipairs({...}) do t[k]=true end return t end
SMROptInPack_Disabled = {}; enabled = false; veto = false; seeds = true; no_terraform = false
logs = {}
SMROptInPack = {
  Register=function(id, def) definition=def end,
  OptionEnabled=function() return enabled end,
  IsActive=function() return enabled and not veto end,
  Require=function() end,
  Log=function(fmt, ...) logs[#logs+1]=string.format(fmt, ...) end,
}
function IsSeedsResourceAvailable() return seeds end
function IsGameRuleActive() return no_terraform end
function IsFoodResource() return false end
function IsKindOfClasses() return false end
function Min(a,b) return math.min(a,b) end
function Max(a,b) return math.max(a,b) end
function Clamp(v,a,b) return math.max(a, math.min(b, v)) end
function MulDivRound(a,b,c) return math.floor(a*b/c+0.5) end
function MulDivTrunc(a,b,c) return (a*b)//c end
function RebuildInfopanel() end
function ObjModified() end
function StatsImpactColonist() end
function ApplyConditionalStatsImpacts() end
function T(t) return t end
function RGB(r,g,b) return r*65536+g*256+b end
function GetVisitPrg() return false end
empty_table = setmetatable({}, {__newindex=function() error('empty_table write') end})
function IsValid(o) return type(o)=='table' and not o.done end
function IsKindOf(o, cls) return type(o)=='table' and o.IsKindOf and o:IsKindOf(cls) end
function DoneObject(o) o.done=true end
const = {HourDuration=30000, DayDuration=720000, Scale={Stat=1000}, ResourceScale=1000}
g_Consts = {NoWorkersPerformance=100, OvertimedShiftPerformance=20}
g_ConsumptionType = {Production=1, Visit=2, Shuttle=3, Workshop=4, Workshift=5}
reassigned = 0
function QueueReassignServices(dome, cat) if dome then reassigned = reassigned + 1 end end
''')
lua.execute(MODULE.read_text(encoding='utf-8'))
lua.execute((ROOT / 'Code/BuildingTemplate/SMROptInArboretum.generated.lua').read_text(encoding='utf-8'))
consumption = 'Lua/HasConsumption.lua'
for name in ('GetConsumptionStoredResources', 'ChangeConsumptionStoredResources',
             'CanConsume', 'DoesHaveConsumption', 'Consume_Internal', 'ConsumptionDroneUnload',
             'Consume_Workshift'):
    lua.execute(body(consumption, 'HasConsumption:' + name))
lua.execute('local typeVisit = 2\n' + body(consumption, 'HasConsumption:Consume_Visit'))
for path, name in (('Lua/Buildings/Workplace.lua', 'Workplace:GetWorkshiftPerformance'),
                   ('Lua/Buildings/Workplace.lua', 'Workplace:GetWorkersPerformance'),
                   ('Lua/Buildings/Workplace.lua', 'Workplace:SetWorkshift'),
                   ('Lua/Buildings/Workplace.lua', 'Workplace:OnChangeWorkshift'),
                   ('Lua/Buildings/Workplace.lua', 'Workplace:HasAnyWorkers'),
                   ('Lua/Buildings/Workplace.lua', 'Workplace:UpdatePerformance'),
                   ('Lua/Buildings/ShiftsBuilding.lua', 'ShiftsBuilding:SetWorkshift'),
                   ('Lua/Buildings/ShiftsBuilding.lua', 'ShiftsBuilding:IsClosedShift'),
                   ('Lua/Buildings/Service.lua', 'ServiceWorkplace:OnChangeWorkshift'),
                   ('Lua/Buildings/Service.lua', 'ServiceWorkplace:UpdateServicePerformance'),
                   ('Lua/Buildings/Service.lua', 'Service:Service'),
                   ('Lua/ServiceBase.lua', 'ServiceBase:ServiceInternal'),
                   ('Lua/Buildings/Building.lua', 'Building:IsUpgradeOn')):
    lua.execute(body(path, name))

# Build locks and template shape (unchanged controls, ShiftsBuilding warning rule).
lua.execute('''
local template = DefineClass.SMROptInArboretum
template.id = 'SMROptInArboretum'
local function locked(t) local l={} OnMsg.GetAdditionalBuildingLocks(t or template,l) return next(l)~=nil end
assert(locked(), 'default-off must hide')
enabled=true; assert(not locked(), 'enabled with seeds must offer')
seeds=false; assert(locked(), 'locked Seeds must hide')
seeds=true; no_terraform=true; assert(locked(), 'NoTerraforming must hide')
no_terraform=false; SMROptInPack_Disabled.Arboretum=true
assert(locked(), 'explicit veto must hide even with stale active status')
SMROptInPack_Disabled.Arboretum=nil
enabled=false; assert(not locked({id='GardenStone'}), 'foreign garden unchanged')
assert(locked(), 'live disable must hide again')
enabled=true; assert(not locked(), 'live re-enable must offer')
-- ServiceBase:GetWarning for a ShiftsBuilding (ServiceBase.lua:52-55): slots <= capacity per shift.
assert(template.max_visitors <= template.service_capacity)
assert(template.build_once_per_dome and template.dome_required)
assert(template.same_category_as=='', 'category must not join Parks')
assert(template.automation > 0 and template.auto_performance == 100, 'unstaffed floor is the Large Garden 100')
assert(template.max_workers == 2 and template.specialist == 'none')
assert(template.consumption_type == g_ConsumptionType.Workshift and template.consumption_amount == 1000)
assert(template.consumption_max_storage == 30000)
''')

# Flattened parent lookup: the class system is not loaded on the desk.
lua.execute('''
local P = {}
for _, cls in ipairs{Building, HasConsumption, ServiceBase, Service, ShiftsBuilding, Workplace, ServiceWorkplace} do
  for k, v in pairs(cls) do P[k] = v end
end
setmetatable(SMROptInArboretumBase, {__index=P})
setmetatable(SMROptInArboretum, {__index=SMROptInArboretumBase})
ServiceWorkplace.Service = Service.Service
ServiceBase.ServiceInternal = ServiceBase.ServiceInternal

function worker(perf) return {GetWorkPerformance=function() return perf end,
  IsInWorkCommand=function() return false end, IsGoingByTrainToWorkAt=function() return false end,
  CanChangeCommand=function() return false end} end

function make(stock)
  local b = setmetatable({template_name='SMROptInArboretum', handle=1, max_shifts=3, active_shift=0,
    current_shift=1, closed_shifts={}, workers={{},{},{}}, working=true, visitors={},
    visitors_per_day=0, visitors_lifetime=0, consumption_stored_resources=stock or 0,
    upgrade_on_off_state={}, upgrades_built={}, debits={}, stopped=0, parent_dome={},
    charged=0}, {__index=SMROptInArboretum})
  b.consumption_resource_request={amount=b.consumption_max_storage-(stock or 0),
    AddAmount=function(self,n) self.amount=self.amount+n end}
  b.city={OnConsumptionResourceConsumed=function(_,res,n) assert(res=='Seeds'); b.charged=b.charged+n end}
  function b:IsKindOf(c) return c=='Building' or c=='SMROptInArboretumBase' end
  function b:AttachSign() end
  function b:UpdateWorking(v) if v==false then self.stopped=self.stopped+1; self.working=false end end
  function b:UpdateVisualStockpile() end
  function b:UpdateRequestConnectivity() end
  function b:IsShroudedInRubble() return false end
  function b:IsOvertime() return false end
  function b:SetBase(prop, v) self[prop]=v end
  function b:SetWorkplaceWorking() end
  function b:UpdateAttachedSigns() end
  function b:UpdateNotWorkingBuildingsNotification() end
  function b:GetDisplayName() return 'Arboretum' end
  function b:HasSpot() return false end
  function b:GetServiceCategory() return 'SMROptInArboretum' end
  function b:ComputeServiceImpact() end
  return b
end
function staff(b, shift, ...) b.workers[shift]={} for _, p in ipairs{...} do table.insert(b.workers[shift], worker(p)) end end
function upgrade(b, id, on)
  b.upgrade_on_off_state[id]=on
  -- the upgrade modifiers, as ApplyUpgrade builds them from the template (Building.lua:1173-1206)
  local t=SMROptInArboretum
  local amount=t.consumption_amount
  if b.upgrade_on_off_state[t.upgrade2_id] then amount=amount+t.upgrade2_add_value_1*const.ResourceScale end
  if b.upgrade_on_off_state[t.upgrade3_id] then amount=amount+t.upgrade3_add_value_3*const.ResourceScale end
  b.consumption_amount=amount
  b.max_workers=b.upgrade_on_off_state[t.upgrade1_id] and MulDivRound(t.max_workers, 100+t.upgrade1_mul_value_1, 100) or t.max_workers
end
''')

# Performance: unstaffed, one, two, above 150, without Seeds, bots.
lua.execute('''
local b=make(30000)
assert(b:GetWorkshiftPerformance(1)==100, 'unstaffed must be the Large Garden 100')
staff(b,1,100); assert(b:GetWorkshiftPerformance(1)==125, 'one of two with Seeds is 125')
staff(b,1,100,100); assert(b:GetWorkshiftPerformance(1)==150, 'both with Seeds is 150')
staff(b,1,180,180); assert(b:GetWorkshiftPerformance(1)==180, 'workers above 150 keep their own')
staff(b,1,300); assert(b:GetWorkshiftPerformance(1)==150, 'one strong worker: own 150 over floor 125')
staff(b,1,40); assert(b:GetWorkshiftPerformance(1)==125, 'one weak worker still gets the staffed floor')
b.consumption_stored_resources=0
staff(b,1,180,180); assert(b:GetWorkshiftPerformance(1)==100, 'staffed without Seeds is the unstaffed 100')
b.consumption_stored_resources=999
assert(b:GetWorkshiftPerformance(1)==100, 'less than one shift of Seeds is not stocked')
local bots=make(30000); upgrade(bots, SMROptInArboretum.upgrade1_id, true)
assert(bots.max_workers==0)
assert(bots:GetWorkshiftPerformance(1)==150, 'bots count as a full staff')
bots:UpdatePerformance(); assert(bots.performance==150, 'performance must not take the native auto_performance path')
local native_bots=make(30000); native_bots.max_workers=0; Workplace.UpdatePerformance(native_bots)
assert(native_bots.performance==100, 'control: the native path would report 100 under bots')
bots.consumption_stored_resources=0; assert(bots:GetWorkshiftPerformance(1)==100, 'bots without Seeds are 100')
local c=make(30000); staff(c,1,100,100); staff(c,2,100); c:UpdateServicePerformance()
assert(c.service_performance==125, 'service performance averages 150, 125, 100 over open shifts')
''')

# Seeds per staffed shift at 1, 2, 3, none unstaffed; never stops at empty.
lua.execute('''
local t=SMROptInArboretum
local b=make(30000); staff(b,1,100)
b:SetWorkshift(2); assert(b.charged==1000 and b.consumption_stored_resources==29000, 'one Seed per staffed shift')
assert(b.current_shift==2)
b:SetWorkshift(3); assert(b.charged==1000, 'an unstaffed shift costs nothing')
upgrade(b, t.upgrade2_id, true); staff(b,3,100)
b:SetWorkshift(1); assert(b.charged==3000, 'Seasonal Blooms: two Seeds per staffed shift')
upgrade(b, t.upgrade3_id, true); staff(b,1,100)
b:SetWorkshift(2); assert(b.charged==6000, 'both upgrades: three Seeds per staffed shift')
upgrade(b, t.upgrade2_id, false); staff(b,2,100)
b:SetWorkshift(3); assert(b.charged==8000, 'Rare Specimens alone: two Seeds per staffed shift')
local first=make(30000); first.current_shift=false; staff(first,1,100)
first:SetWorkshift(1); assert(first.charged==0, 'no charge before the first shift')
local closed=make(30000); staff(closed,1,100); closed.working=false
closed:SetWorkshift(2); assert(closed.charged==0, 'a shift that did not work costs nothing')
local bots=make(30000); upgrade(bots, t.upgrade1_id, true)
bots:SetWorkshift(2); bots:SetWorkshift(3); assert(bots.charged==2000, 'bots use Seeds every shift')
-- empty store: the last Seed goes, the building stays open and keeps serving
local e=make(1000); staff(e,1,100,100)
e:SetWorkshift(2); assert(e.consumption_stored_resources==0 and e.working and e.stopped==0, 'empty store must not stop it')
assert(e:CanConsume() and e:GetWorkshiftPerformance(1)==100)
staff(e,2,100); e:SetWorkshift(3); assert(e.charged==1000, 'no Seeds: shift runs at the floor, nothing charged')
e.consumption_stored_resources=500; staff(e,3,100); e:SetWorkshift(1)
assert(e.charged==1000 and e.consumption_stored_resources==500, 'a partial shift of Seeds is not taken')
HasConsumption.Consume_Internal(e, 500); assert(e.working and e.stopped==0, 'native debit to zero must not stop it')
-- drone delivery: performance follows on the next building update
staff(e,1,100,100); e:UpdatePerformance(); assert(e.performance==100)
e:BuildingUpdate(0); assert(e.performance==100)
e.consumption_resource_request.amount=30000
e:ConsumptionDroneUnload(nil, e.consumption_resource_request, 'Seeds', 3000)
assert(e.performance==100, 'control: delivery alone does not refresh')
e:BuildingUpdate(0); assert(e.performance==150, 'delivery must lift the staffed performance')
-- placed content continues while the option is off
enabled=false; local off=make(30000); staff(off,1,100); off:SetWorkshift(2)
assert(off.charged==1000, 'placed content continues while option off'); enabled=true
-- the visit itself charges nothing (Workshift type)
assert(off:Consume_Visit({})==nil)
''')

# Visitor Comfort and Melancholic Sanity only with Seasonal Blooms.
lua.execute('''
local t=SMROptInArboretum
local function visitor(traits)
  local u={traits=traits, comfort=0, sanity=0, reasons={}}
  function u:ChangeComfort(n, r) self.comfort=self.comfort+n; self.reasons[#self.reasons+1]=r end
  function u:ChangeSanity(n, r) self.sanity=self.sanity+n; self.reasons[#self.reasons+1]=r end
  function u:PlayPrg() self.played=true end
  function u:IsDead() return false end
  return u
end
local b=make(30000)
local plain, sad=visitor({}), visitor({Melancholic=true})
b:Service(plain); b:Service(sad)
assert(plain.played and plain.comfort==0 and sad.sanity==0, 'no bonus without Seasonal Blooms')
upgrade(b, t.upgrade2_id, true)
b:Service(plain); b:Service(sad)
assert(plain.comfort==5000 and plain.sanity==0, 'Comfort 5 on leaving')
assert(sad.comfort==5000 and sad.sanity==10000, 'Melancholic also gains Party Animal Sanity')
assert(plain.reasons[1]=='SMROptInArboretum', 'reason is the template name')
assert(b.visitors_lifetime==4 and b.charged==0, 'visits counted natively and no Seeds per visit')
upgrade(b, t.upgrade2_id, false); b:Service(plain); assert(plain.comfort==5000, 'toggled off: no bonus')
''')

# Display beds and specimens.
# Bed varieties as written in the module, checked against the ruling: Herb bloom first and
# neutral, the three custom entities named exactly, single-state `idle`, authored at bed size.
block = re.search(r'^local BED_VARIETIES = \{\n(.*?)^\}', code, re.M | re.S).group(1)
row = re.compile(r'\{ entity = "(\w+)", state = "(\w+)", tint = RGB\((\d+), (\d+), (\d+)\)'
                 r'(?:, base_scale = (\d+))? \},')
varieties = [(m[0], m[1], (int(m[2]), int(m[3]), int(m[4])), int(m[5]) if m[5] else None)
             for m in row.findall(block)]
assert len(varieties) == block.count('entity =') and len(varieties) >= 6, block
assert varieties[0][:3] == ('CropHerb', 'idle4', (100, 100, 100)), varieties[0]
herb = [v for v in varieties if v[0] == 'CropHerb']
assert len(herb) >= 6 and all(v[1] == 'idle4' and v[3] is None for v in herb), herb
assert crops['CropHerb'][0] == 4, 'idle4 must be the Herb bloom: last of its surveyed stages'
CUSTOM = ['SMROptInArboretumBloomSpike', 'SMROptInArboretumBloomRound', 'SMROptInArboretumBloomLow']
custom = [v for v in varieties if v[0].startswith('SMROptIn')]
assert [v[0] for v in custom] == CUSTOM and all(v[1] == 'idle' and v[3] == 100 for v in custom), custom
assert len({v[2] for v in varieties}) == len(varieties), 'every variety has its own tint'
assert all(v[0] in crops or v[0] in CUSTOM for v in varieties), 'vanilla varieties are surveyed entities'
assert not re.search(r'\bROTATION\b', stripped), 'the old crop rotation table is gone'

lua.globals().CROPS = lua.table_from({k: lua.table_from(list(v)) for k, v in crops.items()})
lua.globals().BUSH_HALF = lua.table_from(bush_half)
lua.globals().VARIETIES = lua.table_from([lua.table_from(
    {'entity': e, 'state': s, 'tint': t[0] * 65536 + t[1] * 256 + t[2], 'base': b or False})
    for e, s, t, b in varieties])
lua.globals().CUSTOM = lua.table_from(CUSTOM)
lua.execute('''
placed = {}
g_Classes = {CropEntityClass = {}}
for name in pairs(CROPS) do g_Classes[name] = {} end
function IsValidEntity(e) return CROPS[e] ~= nil and not missing_entity[e] end
missing_entity = {}
local function idx(state) return state=='idle' and 1 or tonumber(state:match('^idle(%d+)$')) end
function GetStateIdx(state) return idx(state) end
function HasState(obj, state) local i=idx(state); local c=CROPS[obj.entity]; return i~=nil and c~=nil and i<=c[1] end
function PlaceObjectIn(cls, parent)
  assert(g_Classes[cls], 'no class '..tostring(cls))
  local o={class=cls, entity=cls=='CropEntityClass' and 'InvisibleObject' or cls, state=1, scale=100,
    tint=RGB(100,100,100), scale_calls=0}
  function o:GetEntity() return self.entity end
  function o:ChangeEntity(e) self.entity=e end
  function o:SetState(s) assert(HasState(self, s), 'state '..s..' missing on '..self.entity); self.state=idx(s) end
  function o:GetState() return self.state end
  function o:GetScale() return self.scale end
  function o:SetScale(s, time) assert(time==nil, 'timed SetScale is unconfirmed'); self.scale=s; self.scale_calls=self.scale_calls+1 end
  function o:GetColorModifier() return self.tint end
  function o:SetColorModifier(c) self.tint=c end
  function o:GetEntityBBox() local c=CROPS[self.entity]; return {sizex=function() return c[2] end, sizey=function() return c[3] end} end
  function o:SetAttachOffset(p) self.offset=p end
  function o:SetAttachAngle(a) self.angle=a end
  placed[#placed+1]=o
  return o
end
function point(x, y, z) return {x=x, y=y, z=z} end
-- A Specimen record must be the shrub group: Bush_0x entities on that spot, offset and turned,
-- every one inside the 500 circle.
function shrubs_ok(rec, spot)
  if type(rec)~='table' or rec.kind~='shrubs' or #rec.objs<2 then return false end
  for _, o in ipairs(rec.objs) do
    if o.done or not BUSH_HALF[o.entity] or o.spot~=spot or not o.offset or o.angle==nil then return false end
    if math.sqrt(o.offset.x^2+o.offset.y^2)+BUSH_HALF[o.entity] > 250 then return false end
  end
  return true
end
function spotted(b, beds, specimens)
  local spots={Cropbed=beds, Specimen=specimens}
  function b:HasSpot(name) return spots[name]~=nil end
  function b:GetSpotRange(name) local s=spots[name]; return s[1], s[2] end
  function b:Attach(o, i) o.spot=i end
  return b
end
function count_logs(pat) local n=0 for _, l in ipairs(logs) do if l:find(pat, 1, true) then n=n+1 end end return n end
local t=SMROptInArboretum
local quarter=const.HourDuration//4
local sol=const.DayDuration
local ticks=sol//quarter
local NEUTRAL=RGB(100,100,100)
-- The ruling's numbers, independent of the module's constants: 20 at replant, 120 full,
-- reached at hour 10 of the bed's own sol (this module's reading of "mid-morning"), base 100.
local START, FULL, FULL_AT, BASE = 20, 120, 10*const.HourDuration, 100
local herb_fit=800*100//math.max(CROPS.CropHerb[2], CROPS.CropHerb[3])
local function pct(grown) return grown>=FULL_AT and FULL or START+(FULL-START)*grown//FULL_AT end
local function want_scale(v, grown) return (v.base or herb_fit)*pct(grown)//100 end

-- no spots: nothing placed, no field written, upgrades or not
local bare=make(30000); staff(bare,1,100,100)
upgrade(bare, t.upgrade2_id, true); upgrade(bare, t.upgrade3_id, true)
for _=1, ticks do bare:BuildingUpdate(quarter) end
bare:OnUpgradeToggled(t.upgrade2_id, true)
assert(#placed==0 and bare.SMROptInBeds==false and bare.SMROptInSpecimens==false, 'absent spots must do nothing')
upgrade(bare, t.upgrade3_id, false); bare:OnUpgradeToggled(t.upgrade3_id, false)
for _=1, ticks do bare:BuildingUpdate(quarter) end
assert(#placed==0 and bare.SMROptInSpecimens==false, 'absent Specimen spots: no default shrubs either')
assert(count_logs('no Specimen spots')==1, 'missing Specimen spots logged once')
assert(count_logs('no Cropbed spots')==1, 'missing spots logged once')

-- base building: neutral Herb in bloom on every bed at 100 of its 800-circle fit, never changing
for _, name in ipairs(CUSTOM) do missing_entity[name]=true end
local b=spotted(make(30000), {10,12}, {20,21}); staff(b,1,100,100)
b:BuildingUpdate(quarter)
assert(#b.SMROptInBeds==3)
local function base_ok(bed, i)
  local o=bed.obj
  return o.entity=='CropHerb' and o.state==4 and o.spot==9+i and o.scale==herb_fit*BASE//100 and o.tint==NEUTRAL
end
for i, bed in ipairs(b.SMROptInBeds) do assert(base_ok(bed, i), 'base bed '..i..': neutral Herb in bloom at 100') end
assert(#b.SMROptInSpecimens==2, 'both Specimen spots planted by default')
for i, rec in ipairs(b.SMROptInSpecimens) do assert(shrubs_ok(rec, 19+i), 'default shrubs on Specimen spot '..i) end
local base_obj=b.SMROptInBeds[1].obj
local base_shrub=b.SMROptInSpecimens[1].objs[1]
for _=1, ticks*2 do b:BuildingUpdate(quarter) end
for i, bed in ipairs(b.SMROptInBeds) do assert(base_ok(bed, i), 'base beds never grow, tint or rotate') end
assert(b.SMROptInBeds[1].obj==base_obj and base_obj.scale_calls==1, 'base bed object kept, scale set once')
assert(b.SMROptInSpecimens[1].objs[1]==base_shrub and not base_shrub.done, 'shrubs are not replanted every update')
assert(count_logs('entity SMROptInArboretumBloom')==0, 'base building never looks for the custom entities')

-- Seasonal Blooms, tended: always in bloom; 20 -> 120 by hour 10, held, replanted each sol with
-- the next variety and its tint; beds a third of a sol apart; custom entities absent here.
upgrade(b, t.upgrade2_id, true)
b:OnUpgradeToggled(t.upgrade2_id, true)
local function bed_ok(bed, where)
  local v=VARIETIES[bed.variety]; local o=bed.obj
  assert(v and o and not o.done, where..': bed shows a variety')
  assert(o.entity==v.entity, where..': entity of variety '..bed.variety)
  assert(o.state==(v.state=='idle' and 1 or tonumber(v.state:match('%d+'))), where..': always in its bloom state')
  assert(o.tint==v.tint, where..': tint of variety '..bed.variety)
  assert(o.scale==want_scale(v, bed.grown), where..': scale '..o.scale..' want '..want_scale(v, bed.grown)..' at '..bed.grown)
end
for i, bed in ipairs(b.SMROptInBeds) do
  assert(bed.variety==i and bed.grown==sol*(i-1)//3, 'beds start staggered on varieties 1, 2, 3')
  bed_ok(bed, 'start bed '..i)
end
assert(b.SMROptInBeds[1].obj==base_obj, 'same entity: the base Herb object is reused')
assert(b.SMROptInBeds[1].obj.scale==herb_fit*START//100, 'bed 1 at replant: 20')
assert(b.SMROptInBeds[2].obj.scale==herb_fit*100//100, 'bed 2 at hour 8: 100')
assert(b.SMROptInBeds[3].obj.scale==herb_fit*FULL//100, 'bed 3 past hour 10: 120')
local replants={{},{},{}}
local seq={{b.SMROptInBeds[1].variety},{b.SMROptInBeds[2].variety},{b.SMROptInBeds[3].variety}}
local full_ticks={0,0,0}
local seen_mid=false
local prev={}
for i, bed in ipairs(b.SMROptInBeds) do prev[i]={bed.variety, bed.obj.scale} end
for tick=1, ticks*8 do
  b:BuildingUpdate(quarter)
  for i, bed in ipairs(b.SMROptInBeds) do
    bed_ok(bed, 'tick '..tick..' bed '..i)
    local s=bed.obj.scale
    if bed.variety~=prev[i][1] then
      assert(s==herb_fit*START//100, 'replant restarts at 20')
      assert(prev[i][2]==herb_fit*FULL//100, 'the bed reached full before replanting')
      replants[i][#replants[i]+1]=tick; seq[i][#seq[i]+1]=bed.variety
    else
      assert(s>=prev[i][2], 'no shrinking within a sol')
    end
    if s==herb_fit*FULL//100 then full_ticks[i]=full_ticks[i]+1 end
    if i==1 and bed.grown==FULL_AT//2 then seen_mid=true; assert(s==herb_fit*70//100, 'mid-growth: 70') end
    prev[i]={bed.variety, s}
  end
end
assert(seen_mid, 'the desk sampled mid-growth')
local hold=(sol-FULL_AT)//quarter
for i=1,3 do
  assert(#replants[i]==8, 'one replant per sol: bed '..i..' had '..#replants[i])
  for k=2,8 do assert(replants[i][k]-replants[i][k-1]==ticks, 'exactly one sol between replants') end
  assert(full_ticks[i]==hold*8, 'held at full for the rest of each sol: '..full_ticks[i]..' want '..hold*8)
end
assert(replants[1][1]-replants[2][1]==ticks//3 and replants[2][1]-replants[3][1]==ticks//3, 'beds staggered by a third of a sol')
-- bed 1 walked 1..6 and wrapped past the three missing custom entities
local want={1,2,3,4,5,6,1,2,3}
for k, v in ipairs(want) do assert(seq[1][k]==v, 'variety order skips missing entities: '..table.concat(seq[1], ',')) end
for _, name in ipairs(CUSTOM) do assert(count_logs('entity '..name..' is missing')==1, name..' logged once') end
for _, l in ipairs(logs) do assert(not l:find('display beds stopped'), 'no display error: '..l) end

-- holds: unstaffed, out of Seeds, not working; growth resumes when tended
local function snapshot() local s={} for i, bed in ipairs(b.SMROptInBeds) do s[i]={bed.obj, bed.obj.scale, bed.obj.tint, bed.grown, bed.variety} end return s end
local function same(a, c) for i=1,3 do for k=1,5 do if a[i][k]~=c[i][k] then return false end end end return true end
b.workers={{},{},{}}
local before=snapshot(); for _=1, ticks*2 do b:BuildingUpdate(quarter) end
assert(same(before, snapshot()), 'unstaffed: no growth, no replant')
staff(b,1,100,100); b.consumption_stored_resources=0
for _=1, ticks*2 do b:BuildingUpdate(quarter) end
assert(same(before, snapshot()), 'out of Seeds: no growth, no replant')
b.consumption_stored_resources=30000; b.working=false
for _=1, ticks do b:BuildingUpdate(quarter) end
assert(same(before, snapshot()), 'not working: beds hold'); b.working=true
b:BuildingUpdate(quarter); assert(not same(before, snapshot()), 'tended again: growth resumes')
-- bots tend too
local bots=spotted(make(30000), {1,3}, nil); upgrade(bots, t.upgrade1_id, true); upgrade(bots, t.upgrade2_id, true)
for _=1, ticks do bots:BuildingUpdate(quarter) end
assert(bots.SMROptInBeds[1].variety==2, 'bots tend the beds')

-- Blooms off again: back to neutral Herb at 100
upgrade(b, t.upgrade2_id, false); b:OnUpgradeToggled(t.upgrade2_id, false)
for i, bed in ipairs(b.SMROptInBeds) do assert(base_ok(bed, i), 'Blooms off: neutral Herb at 100 again') end

-- custom entities present: placed on CropEntityClass, entity changed, base_scale not fitted
for _, name in ipairs(CUSTOM) do missing_entity[name]=nil; CROPS[name]={1, 1600, 1600} end
local cu=spotted(make(30000), {1,3}, nil); staff(cu,1,100,100); upgrade(cu, t.upgrade2_id, true)
cu:BuildingUpdate(0)
local cvar=#VARIETIES-#CUSTOM+1
cu.SMROptInBeds[1].variety=cvar; cu.SMROptInBeds[1].grown=FULL_AT
cu:BuildingUpdate(0)
local co=cu.SMROptInBeds[1].obj
bed_ok(cu.SMROptInBeds[1], 'custom bed')
assert(co.class=='CropEntityClass' and co.entity==CUSTOM[1] and co.scale==FULL, 'custom bloom at base_scale 100 x 120')
for _=1, ticks*3 do cu:BuildingUpdate(quarter) end
for _, bed in ipairs(cu.SMROptInBeds) do bed_ok(bed, 'custom rotation') end
for _, name in ipairs(CUSTOM) do assert(count_logs('entity '..name..' is missing')==1, name..': no second log once present') end

-- a bed record from the earlier crop-rotation build loads: index wrapped, foreign crop replaced
local old=spotted(make(30000), {1,1}, nil); staff(old,1,100,100); upgrade(old, t.upgrade2_id, true)
local stale=PlaceObjectIn('CropRapeseed_SmallFarm', old)
old.SMROptInBeds={{variety=#VARIETIES+3, grown=sol//2, obj=stale}}
old:BuildingUpdate(quarter)
assert(stale.done and old.SMROptInBeds[1].variety==3, 'old index wrapped into the table')
bed_ok(old.SMROptInBeds[1], 'old record')

-- Rare Specimens: the showpiece replaces the shrubs, scaled to 500; switched off, shrubs return
local old_shrubs={}
for _, rec in ipairs(b.SMROptInSpecimens) do for _, o in ipairs(rec.objs) do old_shrubs[#old_shrubs+1]=o end end
upgrade(b, t.upgrade3_id, true); b:OnUpgradeToggled(t.upgrade3_id, true)
assert(#b.SMROptInSpecimens==2)
for _, o in ipairs(old_shrubs) do assert(o.done, 'shrubs removed under Rare Specimens') end
for i, rec in ipairs(b.SMROptInSpecimens) do
  assert(rec.kind=='showpiece' and #rec.objs==1, 'one showpiece per spot, no shrubs')
  local o=rec.objs[1]
  assert(o.entity=='CropApples' and o.state==4 and o.spot==19+i and o.tint==NEUTRAL)
  assert(o.scale==500*100//math.max(CROPS.CropApples[2], CROPS.CropApples[3]))
end
local sp=b.SMROptInSpecimens[1].objs[1]
for _=1, ticks do b:BuildingUpdate(quarter) end
assert(b.SMROptInSpecimens[1].objs[1]==sp and not sp.done, 'showpiece kept across updates')
upgrade(b, t.upgrade3_id, false); b:OnUpgradeToggled(t.upgrade3_id, false)
assert(sp.done, 'showpiece removed when the upgrade is off')
for i, rec in ipairs(b.SMROptInSpecimens) do assert(shrubs_ok(rec, 19+i), 'shrubs restored on spot '..i) end
-- a shrub lost from outside is replanted on the next update
b.SMROptInSpecimens[2].objs[1].done=true; b:BuildingUpdate(quarter)
assert(shrubs_ok(b.SMROptInSpecimens[2], 21), 'damaged shrub group replanted')
-- a missing shrub entity leaves the spot empty, logged once; restored entity fills it
missing_entity.Bush_04=true
local ms=spotted(make(30000), nil, {1,2}); local before_n=#placed
for _=1, 4 do ms:BuildingUpdate(quarter) end
assert(#placed==before_n, 'missing shrub entity: spot left empty')
for _, rec in ipairs(ms.SMROptInSpecimens) do assert(rec.kind=='shrubs' and #rec.objs==0) end
assert(count_logs('Bush_04 is missing')==1, 'missing shrub entity logged once')
missing_entity.Bush_04=nil; ms:BuildingUpdate(quarter)
assert(shrubs_ok(ms.SMROptInSpecimens[1], 1) and shrubs_ok(ms.SMROptInSpecimens[2], 2), 'entity back: shrubs planted')
for _, l in ipairs(logs) do assert(not l:find('display beds stopped'), 'no display error: '..l) end
''')

# Upgrade unlocks: Blooms and Specimens at once, Service Bots with the tech; missing API is soft.
lua.execute('''
local t=SMROptInArboretum
local function colony(researched)
  local c={unlocked={}, labels={SMROptInArboretum={1}}}
  function c:UnlockUpgrade(id) self.unlocked[id]=true end
  function c:IsUpgradeUnlocked(id) return self.unlocked[id] or false end
  function c:IsTechResearched(id) return researched[id] end
  function c:GetCityLabels(l) return self.labels[l] or empty_table end
  return c
end
Techs={ServiceBots={}}
local researched={}
UIColony=colony(researched)
local b=make(30000); b:GameInit()
assert(UIColony.unlocked[t.upgrade2_id] and UIColony.unlocked[t.upgrade3_id], 'Blooms and Specimens offered')
assert(not UIColony.unlocked[t.upgrade1_id], 'Service Bots waits for the tech')
OnMsg.TechResearched('ServiceBots')
assert(not UIColony.unlocked[t.upgrade1_id], 'not researched yet')
researched.ServiceBots=true; OnMsg.TechResearched('SomethingElse')
assert(not UIColony.unlocked[t.upgrade1_id], 'other techs ignored')
OnMsg.TechResearched('ServiceBots'); assert(UIColony.unlocked[t.upgrade1_id], 'Service Bots offered with the tech')
UIColony=colony(researched); UIColony.labels={}; OnMsg.LoadGame()
assert(not next(UIColony.unlocked), 'no Arboretum, nothing written on load')
UIColony.labels={SMROptInArboretum={1}}; OnMsg.LoadGame()
assert(UIColony.unlocked[t.upgrade1_id] and UIColony.unlocked[t.upgrade2_id], 'load restores unlocks')
Techs={}; UIColony=colony({}); b:GameInit(); b:GameInit()
local n=0 for _, l in ipairs(logs) do if l:find('tech ServiceBots is missing') then n=n+1 end end
assert(n==1 and UIColony.unlocked[t.upgrade2_id], 'missing tech logged once, others still offered')
UIColony={}; b:GameInit(); b:GameInit()
n=0 for _, l in ipairs(logs) do if l:find('upgrade unlock API is missing') then n=n+1 end end
assert(n==1, 'missing upgrade API logged once')
UIColony=nil
''')

# Sitting slots (slots.lua.txt) on a native-consumption fixture; debits are direct native calls.
lua.execute('''
local b=setmetatable({consumption_stored_resources=500, consumption_max_storage=30000,
 consumption_resource_type='Seeds', consumption_type=5, consumption_amount=1000,
 working=true, consumed=0}, {__index=HasConsumption})
b.consumption_resource_request={amount=29500, AddAmount=function(self,n) self.amount=self.amount+n end}
b.city={OnConsumptionResourceConsumed=function(_,res,n) assert(res=='Seeds'); b.consumed=b.consumed+n end}
function b:AttachSign() end
function b:UpdateWorking(value) self.working=value~=false end
function b:UpdateVisualStockpile() end
function b:UpdateRequestConnectivity() end
fixture=b
''')
lua.execute('''
SMRTK={slots={},armed={},error_count=0,logs={}}
function SMRTK.Bind(n,label,fn) SMRTK.slots[n]=fn end
function SMRTK.Mark() return 1 end
function SMRTK.Log(verb,fields) SMRTK.logs[#SMRTK.logs+1]=fields end
function SMRTK.Arm(id) SMRTK.armed[id]={}; return true,{} end
function SMRTK.Disarm(id) SMRTK.armed[id]=nil; return true,{} end
function SetGameSpeed() end
function GetEntityOutlineShape() return {1,2,3} end
ActiveMapID=1; UIColony={day=10}; const={DayDuration=1000}; now=0
function GameTime() return now end
g_Classes={SMROptInArboretum=HasConsumption}
fixture.class='SMROptInArboretum'; fixture.handle=12; fixture.visitors_lifetime=4
fixture.parent_dome={handle=13, labels={Colonist={1,2}}, serviced={}}
function fixture:IsKindOf(name) return name=='Building' end
function fixture:GetMapID() return 1 end
function fixture:GetInDomeUsedCapacity() return 2 end
function fixture.consumption_resource_request:GetActualAmount() return self.amount end
context={pin={A=fixture},log=SMRTK.Log,mark=SMRTK.Mark}
''')
lua.execute((ROOT / 'tools/arboretum/slots.lua.txt').read_text(encoding='utf-8'))
lua.execute('''
local native=HasConsumption.Consume_Internal
local start=SMRTK.slots[4](context)
assert(start.target==13 and HasConsumption.Consume_Internal~=native)
fixture:Consume_Internal(500); fixture.visitors_lifetime=5
fixture:ConsumptionDroneUnload(nil,fixture.consumption_resource_request,'Seeds',1000)
fixture:Consume_Internal(500); fixture.visitors_lifetime=6
now=3000; UIColony.day=13
local result=SMRTK.slots[5](context)
assert(result.result=='MEASURED' and result.consumed_milli==1000)
assert(result.seeds_milli_per_sol==333 and result.stock_milli==500,
 'rate must measure debits despite delivery replacing the consumed stock')
assert(result.visits_delta==2 and result.native_debits==2)
assert(HasConsumption.Consume_Internal==native, 'observer must be removed at finish')
SMRTK.slots[4](context)
OnMsg.SaveGameStart()
assert(HasConsumption.Consume_Internal==native, 'save must not serialize observer')
assert(SMRTK.logs[#SMRTK.logs].result=='ABORTED')
assert(SMRTK.slots[5](context)==false, 'aborted measurement must not become success')
-- Model sitting readout must refuse the placeholder, missing visual stock and stale stock.
function fixture:GetEntity() return self.entity end
function fixture:ForEachAttach(fn)
 fn({GetEntity=function() return 'SMROptInArboretumGlass' end})
end
fixture.entity='GardenLargeCP3'
assert(SMRTK.slots[9](context)==false, 'placeholder must not pass model witness')
fixture.entity='SMROptInArboretumPavilion'
assert(SMRTK.slots[9](context)==false, 'missing visual stock must refuse')
fixture.consumption_resource_stockpile={stockpiled_amount=-1,count=0}
assert(SMRTK.slots[9](context)==false, 'stale visual stock must refuse')
fixture.consumption_resource_stockpile.stockpiled_amount=fixture:GetConsumptionStoredResources()
local visual=SMRTK.slots[9](context)
assert(visual.stock_matches and visual.entity=='SMROptInArboretumPavilion')
assert(visual.visual_milli==visual.stock_milli and visual.attaches=='SMROptInArboretumGlass')
''')
repo = next(p for p in Path(__file__).resolve().parents if (p / 'tools/doccheck.py').is_file())
print('COMMAND: python ' + Path(__file__).resolve().relative_to(repo).as_posix())
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
print('SOURCE: archived 1.1.1.406343 bodies; working-tree module and generated template; crop and mesh survey props.json')
print('PASS: no "/" in module code; upgrade ids match template; build locks and foreign control; template shape')
print('PASS: performance 100 unstaffed, 125/150 staffed with Seeds, own above 150, 100 without Seeds, bots 150/100')
print('PASS: Seeds 1/2/3 per staffed shift via native SetWorkshift chain, 0 unstaffed/unworked/first; empty store never stops; delivery refresh')
print('PASS: Comfort 5 on leaving and Melancholic Sanity 10 only with Seasonal Blooms; no per-visit Seeds')
print('PASS: beds always in bloom; Blooms: 20 at replant, 70 mid-growth, 120 by hour 10 and held to the replant, one variety and tint per sol, staggered a third; hold unstaffed/no Seeds/not working; base neutral Herb at 100; absent spots do nothing')
print('PASS: Specimen spots: default shrubs inside 500, showpiece replaces them, shrubs restored when off; absent spots/entity soft')
print('PASS: missing custom bloom entities skipped, one log line each; present ones placed on CropEntityClass at base_scale; old bed record wraps and replaces its crop; upgrade unlocks incl. tech and missing API')
print('PASS: sitting measures actual debits across replacement deliveries; finish/save remove observer; interrupted sample refuses')
print('PASS: model readout refuses placeholder/missing/stale visual stock; matching native stock reports its amount')
print('NOT MEASURED: class composition, modifiers, drone routing, bed visuals, scale, tint and entity loading in the engine, UI, real boot, save/load, Seeds/sol')
