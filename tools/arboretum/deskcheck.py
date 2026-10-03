"""Arboretum native consumption and build-lock controls, not an in-game measurement."""
import json
import re
import subprocess
from pathlib import Path
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[2]
SRC = Path('B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src')


def body(path, name):
    source = (SRC / path).read_text(encoding='utf-8')
    match = re.search(r'^function ' + re.escape(name) + r'\([^\n]*\).*?^end\s*$', source, re.M | re.S)
    if not match:
        raise RuntimeError(name)
    return match.group()


lua = LuaRuntime()
lua.execute('''
DefineClass = {}; OnMsg = {}; HasConsumption = {}; Service = {}; ServiceBase = {}
function Untranslated(s) return s end
function UndefineClass() end
function set(...) local t={} for _, k in ipairs({...}) do t[k]=true end return t end
SMROptInPack_Disabled = {}; enabled = false; veto = false; seeds = true; no_terraform = false
SMROptInPack = {
  Register=function(id, def) definition=def end,
  OptionEnabled=function() return enabled end,
  IsActive=function() return enabled and not veto end,
  Require=function() end,
}
function IsSeedsResourceAvailable() return seeds end
function IsGameRuleActive() return no_terraform end
function IsFoodResource() return false end
function Min(a,b) return math.min(a,b) end
function RebuildInfopanel() end
''')
lua.execute((ROOT / 'Code/Opt_Arboretum.lua').read_text(encoding='utf-8'))
lua.execute((ROOT / 'Code/BuildingTemplate/SMROptInArboretum.generated.lua').read_text(encoding='utf-8'))
consumption = 'Lua/HasConsumption.lua'
for name in ('GetConsumptionStoredResources', 'ChangeConsumptionStoredResources',
             'CanConsume', 'DoesHaveConsumption', 'Consume_Internal', 'ConsumptionDroneUnload'):
    lua.execute(body(consumption, 'HasConsumption:' + name))
lua.execute('local typeVisit = 2\n' + body(consumption, 'HasConsumption:Consume_Visit'))
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
assert(template.max_visitors*3 <= template.service_capacity)
assert(template.build_once_per_dome and template.dome_required)
assert(template.same_category_as=='', 'category must not join Parks')
local b=setmetatable({consumption_stored_resources=1000, consumption_max_storage=10000,
 consumption_resource_type='Seeds', consumption_type=2, consumption_amount=template.consumption_amount,
 working=true, delivered=0, consumed=0}, {__index=HasConsumption})
b.consumption_resource_request={amount=9000, AddAmount=function(self,n) self.amount=self.amount+n end}
b.city={OnConsumptionResourceConsumed=function(_,res,n) assert(res=='Seeds'); b.consumed=b.consumed+n end}
function b:IsKindOf() return true end
function b:AttachSign() end
function b:UpdateWorking(value) self.working=value~=false end
function b:UpdateVisualStockpile() end
function b:UpdateRequestConnectivity() end
assert(b:Consume_Visit({})==500 and b.working)
assert(b:Consume_Visit({})==500 and not b.working)
assert(b.consumed==1000 and b.consumption_resource_request.amount==10000)
-- Native drone task removes demand before the building callback.
b.consumption_resource_request.amount=9000
b:ConsumptionDroneUnload(nil,b.consumption_resource_request,'Seeds',1000)
assert(b.working and b:GetConsumptionStoredResources()==1000)
enabled=false
assert(b:Consume_Visit({})==500, 'placed content continues while option off')
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
function IsValid(o) return type(o)=='table' end
function GetEntityOutlineShape() return {1,2,3} end
function MulDivRound(a,b,c) return math.floor(a*b/c+0.5) end
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
fixture:Consume_Visit({}); fixture.visitors_lifetime=5
fixture:ConsumptionDroneUnload(nil,fixture.consumption_resource_request,'Seeds',1000)
fixture:Consume_Visit({}); fixture.visitors_lifetime=6
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
''')
print('COMMAND: python tools/arboretum/deskcheck.py')
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
print('SOURCE: archived 1.1.1.406343; working-tree module and generated template')
print('PASS: native Seeds debit, empty stop, drone callback restart, existing content off; build locks and foreign control')
print('PASS: sitting measures actual debits across replacement deliveries; finish/save remove observer; interrupted sample refuses')
print('NOT MEASURED: drone routing, footprint, UI, real boot, save removal, Seeds/sol')
