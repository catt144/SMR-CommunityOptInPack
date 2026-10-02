"""Brief 30 depot follow-up: real Lua and archived 406343 upgrade/resize/panel bodies.

Engine requests, UI windows and world are doubles. No claim about native saves or art rendering.
"""
from pathlib import Path
import hashlib
import re
import runpy
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
env = runpy.run_path(str(HERE / 'wiring_smoke.py'))
lua = env['lua']
ARCHIVE = ROOT.parent / 'SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/Lua'


def body(rel, name):
    text = (ARCHIVE / rel).read_text(encoding='utf8')
    match = re.search(r'^function ' + re.escape(name) + r'\(.*?^end\n', text, re.M | re.S)
    assert match, name
    return match.group(0)


lua.execute('''
Modifiable={}; Building={}; UpgradableBuilding={}; MultiResourceDepotBase={}
min_int64=math.mininteger; max_int64=math.maxinteger; ResourceScale=1000
const.Building={MaxUpgrades=6, UpgradeModifierSlots=3}; UpgradeModifierModifiers={}
function GetMissionSponsor() return {id='IMM'} end
function RebuildInfopanel() end
function Msg(name,...) if OnMsg[name] then OnMsg[name](...) end end
''')
for cls, rel, methods in [
    ('Modifiable', 'Modifiers.lua', ['SetBase', 'ModifyValue']),
    ('Building', 'Buildings/Building.lua', ['ApplyUpgrade', 'ConstructUpgrade', 'HasUpgrade',
        'GetUpgradeValue', 'CanDisableUpgrade', 'IsUpgradeOn', 'IsUpgradeBeingConstructed']),
    ('UpgradableBuilding', 'Buildings/UpgradableBuilding.lua', ['GetUpgradeID', 'GetUpgradeTier', 'GetUpgradeCost']),
    ('MultiResourceDepotBase', 'Buildings/MultiResourceDepot.lua', ['UpdateRequestCapacity', 'OnModifiableValueChanged']),
]:
    for method in methods:
        code = body(rel, cls + ':' + method)
        # Native integer division; Lua 5.5 uses floating division otherwise.
        code = code.replace(' / ResourceScale', ' // ResourceScale')
        lua.execute(code)

lua.execute(r'''
local D, Base = SMRElevatorDepotDev, SMROptInElevatorDepotDevBase
D.layout.cabin_capacity=250
UIColony.labels.SMROptInElevatorDepotDev={}; D.WiringLoad()
UIColony.unlocked={}
function UIColony:IsUpgradeUnlocked(id) return self.unlocked[id] end
function UIColony:UnlockUpgrade(id) self.unlocked[id]=true end
for _, class in ipairs{Modifiable, Building, UpgradableBuilding, MultiResourceDepotBase} do
  for k,v in pairs(class) do if Base[k]==nil then Base[k]=v end end
end
for i=1,3 do Base['upgrade1_mod_prop_id_'..i]='' end
function fresh(map)
  local o=depot(map)
  o.SetBase=nil; o.base_max_storage_per_resource=60000; o.max_storage_per_resource=60000
  o.GetMaxStorage=function(self) return self.max_storage_per_resource end
  o.GetMaxStorageForAnyOneResource=o.GetMaxStorage
  o.RecalculateDerivedMaxZ=empty_func; o.ReallocateVisualColumns=empty_func; o.RebuildInfopanel=empty_func
  o.CreateUpgradeUpkeepObject=empty_func; o.CanWork=function() return true end
  o.SetWorking=function(self,v) self.working=v end
  o.HasMember=function(self,k) return self[k]~=nil end
  o.StartUpgradeConstruction=function(self,id)
    self.upgrades_under_construction=self.upgrades_under_construction or {}
    self.upgrades_under_construction[id]={cost_Metals=self:GetUpgradeCost(1,'Metals'),cost_Concrete=self:GetUpgradeCost(1,'Concrete')}
  end
  for _,reqs in ipairs{o.supply,o.demand} do for _,r in pairs(reqs) do
    r.SetAmount=function(self,n) self.amount=n end
    r.SetDesiredAmount=function(self,n) self.desired=n end
  end end
  D.SyncCapacity()
  return o
end
S=fresh(surface_map); U=fresh(cave)
assert(S:GetMaxStorage('Metals')==250000 and U:GetMaxStorage('Metals')==250000)
assert(S.demand.Metals.amount==250000 and D.CabinCapacity(S)==250, 'old bases migrate to 250')

local function stocks(o, values)
  for _,res in ipairs(RESOURCES) do
    o.supply[res].amount=(values[res] or 0)*1000; o.supply[res].assigned=0
    o.demand[res].amount=o:GetMaxStorage(res)-o.supply[res].amount; o.demand[res].assigned=0
  end
end
local function depart(down)
  local rec={phase=down and 'at_top' or 'at_bottom', ends=now, started=true, cargo={}, legs=0}
  rawset(S,D.CABIN,rec); D.Tick(1); return rec
end
for _,down in ipairs{true,false} do
  local from,to=down and S or U, down and U or S
  D.SetRow(S,'Concrete',down and 'import' or 'export')
  D.SetRow(S,'Metals',down and 'import' or 'export'); D.SetRow(S,'Polymers','disabled')
  stocks(from,{Concrete=250,Metals=250}); stocks(to,{Concrete=240})
  local rec=depart(down)
  assert(rec.cargo.Metals==250000 and rec.cargo.Concrete==nil, 'empty Metals precedes nearly full Concrete on both legs')
  stocks(from,{Concrete=250}); stocks(to,{Concrete=240})
  to.demand.Concrete.assigned=5000 -- another carrier has already promised five
  rec=depart(down)
  assert(rec.cargo.Concrete==5000 and rec.cargo.Metals==nil, 'room cap includes incoming reservations')
  to:AddResource(5000,'Concrete') -- other delivery fills its promised room while cabin travels
  to.demand.Concrete.assigned=0 -- native carrier releases its completed reservation
  now=rec.ends; D.Tick(1)
  assert(to.supply.Concrete.amount==250000, 'arrival fills exactly to capacity')
end

-- A hub upgrade cannot double the depot; unrelated modifiers still apply, and no table is mutated.
local network={upgrade_id='SMROptInTrainHub6_CapacityNetwork', percent=100, amount=0}
S.modifications={max_storage_per_resource={network,percent=200,amount=0}}
S:SetBase('max_storage_per_resource',250000)
assert(S.max_storage_per_resource==250000 and S.modifications.max_storage_per_resource.percent==200)
assert(S:ModifyValue(250000,'max_storage_per_resource',{network,percent=210,amount=7000})==282000)
assert(S:ModifyValue(10,'unrelated',{percent=200})==20)

-- One native cost/receipt for the pair, no duplicate construction from the other end.
local id=D.CAPACITY_UPGRADE
S:ConstructUpgrade(id)
local order=S.upgrades_under_construction[id]
assert(order.cost_Metals==10000 and order.cost_Concrete==10000)
U:ConstructUpgrade(id); assert(not U.upgrades_under_construction, 'cannot queue two purchases')
local stock_before=S.supply.Concrete.amount
Building.ApplyUpgrade(S,1)
assert(S:HasUpgrade(id) and U:HasUpgrade(id) and not S:CanDisableUpgrade(id))
assert(S.upgrades_built[1] and not U.upgrades_built[1], 'one paid salvage receipt; mirrors cannot multiply refunds')
assert(S:GetMaxStorage('Metals')==500000 and U:GetMaxStorage('Metals')==500000)
assert(S.supply.Concrete.amount==stock_before and D.CabinCapacity(U)==500, 'stock retained, both ends upgraded')
for _,down in ipairs{true,false} do
  local from,to=down and S or U, down and U or S
  D.SetRow(S,'Metals',down and 'import' or 'export'); D.SetRow(S,'Concrete','disabled')
  stocks(from,{Metals=500}); stocks(to,{})
  assert(depart(down).cargo.Metals==500000, '500 aboard in either direction')
end
D.WiringLoad(); D.SyncCapacity()
assert(D.CabinCapacity(S)==500 and U:GetMaxStorage('Metals')==500000, 'reload reconciles the native receipt')
S.destroyed=true; D.HalfGone(S,nil,'destroyed'); D.InvalidatePair()
assert(D.CabinCapacity(U)==500, 'survivor keeps purchase')
S=fresh(surface_map)
assert(S:HasUpgrade(id) and S.max_storage_per_resource==500000, 'replacement adopts paid upgrade')
assert(not S.upgrades_built[1], 'a replacement does not recreate the spent-resource receipt')

-- The actual follower ends moving FX and keeps polling at rest; re-pairing resumes it.
local rig={bld=U,base=point(0,0,1000),far=point(0,0,30000),elevator={valid=true},cabin={valid=true}}
local p=point(0,0,8000)
function rig.cabin:GetPos() return p end
function rig.cabin:SetPos(v) p=v end
rig.cabin.SetEnumFlags=empty_func; rig.cabin.ClearEnumFlags=empty_func
fx={}; function PlayFX(_,action) fx[#fx+1]=action end
function Sleep() coroutine.yield() end
S.destroyed=true; D.InvalidatePair()
local follower=coroutine.create(function() D.FollowLoop(rig) end)
assert(coroutine.resume(follower)); assert(p:z()==1000 and fx[1]=='end')
assert(coroutine.resume(follower)); assert(p:z()==1000)
S.destroyed=false; D.InvalidatePair()
rawset(S,D.CABIN,{phase='down',leg_ms=30000,ends=now+15000,cargo={}})
assert(coroutine.resume(follower)); assert(p:z()==15500 and fx[#fx]=='start', 'same follower resumes on re-pair')
''')

# Execute the native exact-class lookup and native button definitions, not a copied UI.
lua.execute('''
function UndefineClass() end
function T(_,text) return text end
function IsContextOfKind(o,k) return IsKindOf(o,k) end
function SubContext(o) return o end
windows={}
local window={new=function(self,args,parent,context)
  args.context=context; windows[#windows+1]=args; return args
end,__content=function(self) return self end}
InfopanelButton=window; InfopanelSection=window; XContentTemplate=window
BuildingTemplates={SMROptInElevatorDepotDev={object_class='SMROptInElevatorDepotDevBase'}}
XTemplates={}; XDefs={customStation={id='customStation',__content=function(p) return p end}}
function XTemplateSpawn(id,parent,context) _G[id].Init(parent,parent,context) end
''')
for name in ['sectionCustom', 'customStation']:
    lua.execute((ARCHIVE / f'XDef/{name}.generated.lua').read_text(encoding='utf8'))
lua.execute('''
SMRElevatorDepotDev.InstallStationPanel()
for _,o in ipairs{S,U} do
  windows={}; o.class='SMROptInElevatorDepotDev'; o.kinds.Station=true; o.waiting_for_train={}
  o.ConstructTrain=function(self,n) self.train_order=n end
  sectionCustom.Init({},nil,o)
  local build,route
  for _,w in ipairs(windows) do
    if w.Id=='idConstructTrain' then build=w elseif w.Id=='idTrainRoute' then route=w end
  end
  assert(build and route and route.OnPressParam=='ToggleCreateRouteMode', 'both native train buttons on either map')
  build:OnPress(); assert(o.train_order==1); build:OnAltPress(); assert(o.train_order==-1)
end
''')
# The current editor output inherits the authored upgrade; no generated file edit/save is needed.
lua.execute("function set(...) return {} end")
lua.execute((ROOT / 'Code/BuildingTemplate/SMROptInElevatorDepotDev.generated.lua').read_text(encoding='utf8'))
lua.execute('''
setmetatable(SMROptInElevatorDepotDev,{__index=SMROptInElevatorDepotDevBase})
-- Model native InjectUpgradeCostPropertiesSingle's raw zero on the descendant.
SMROptInElevatorDepotDev.upgrade1_upgrade_cost_Metals=0
SMROptInElevatorDepotDev.upgrade1_upgrade_cost_Concrete=0
g_Classes.SMROptInElevatorDepotDev=SMROptInElevatorDepotDev
SMRElevatorDepotDev.InstallStationPanel()
assert(SMROptInElevatorDepotDev.upgrade1_id==SMRElevatorDepotDev.CAPACITY_UPGRADE)
assert(SMROptInElevatorDepotDev.upgrade1_upgrade_cost_Metals==10000)
assert(SMROptInElevatorDepotDev.upgrade1_upgrade_cost_Concrete==10000)
assert(SMROptInElevatorDepotDev.max_storage_per_resource==250000)
''')

lua.execute('''
SMRTK.armed={}; armed_runs={}
for _,o in ipairs{S,U} do
  o.GetAvailableTrains=function(self) return self.available_trains or 0 end
  o.upgrades_built=nil; o.upgrade_on_off_state=nil; o.upgrades_under_construction=nil
  o.trains_in_construction=0
  for _,reqs in ipairs{o.supply,o.demand} do for _,r in pairs(reqs) do r.assigned=0 end end
end
SMRElevatorDepotDev.SyncCapacity(); CurrentMap=surface_map
''')
lua.execute((HERE / '80_AgentSlots_revision.lua.txt').read_text(encoding='utf8'))
lua.execute('''
assert(not next(SMRTK.armed) and #armed_runs==0, 'overlay load is inert')
local D=SMRElevatorDepotDev
local ctx=ctx_for(S)
-- Carriers' reservations are kept, not refused (brief 33): all but 220 of the underground Metals
-- room and 1 of the surface Metals stock are promised. The real cabin must load what the slot predicts.
for _,o in ipairs{S,U} do for _,res in ipairs{'Metals','Concrete'} do  -- requests consistent with stock
  o.demand[res].amount=o:GetMaxStorage(res)-o.supply[res].amount
end end
local promised=U:GetMaxStorage('Metals')-220000
U.demand.Metals.assigned=promised; S.supply.Metals.assigned=1000
local held=slots[1].fn(ctx)
assert(ctx.mutated and held.expected_metals==220000 and held.expected_concrete==10000, 'reservations bound the prediction')
assert(held.reserved=='Metals=1000/0/0/'..promised..' Concrete=0/0/0/0', held.reserved)
assert(U.demand.Metals:GetTargetAmount()==220000 and S.supply.Metals:GetActualAmount()==250000, 'promised room and stock kept')
D.Tick(1)
local fired,f=triggers.depot_next_departure.when(SMRTK.armed.depot_next_departure)
assert(fired and f.aboard_Metals==2200 and f.aboard_Concrete==100, 'the real cabin loads the predicted amounts')
U.demand.Metals.assigned=0; S.supply.Metals.assigned=0
ctx=ctx_for(S)
for _,slot in ipairs{1,4} do
  local setup=slots[slot].fn(ctx)
  assert(setup.expected_metals==250000 and ctx.mutated and armed_runs[#armed_runs]=='speed_ultra')
  assert(D.State(S,'Polymers')=='disabled' and not rawget(S,D.DRONES) and not rawget(U,D.DRONES), 'only the fixture rows enabled, Drone Access off')
  D.Tick(1)
  local fired,f=triggers.depot_next_departure.when(SMRTK.armed.depot_next_departure)
  assert(fired and f.aboard_Metals==2500 and f.aboard_Concrete==0, 'prepared load witness in tenths')
  slots[2].fn(ctx)
  assert(not SMRTK.armed.depot_next_departure, 'arrival replaces the departure watch')
  local rec=rawget(S,D.CABIN); now=rec.ends; D.Tick(1)
  fired,f=triggers.depot_next_arrival.when(SMRTK.armed.depot_next_arrival)
  assert(fired and f.verdict=='arrived' and f.aboard_Metals==0)
end
local f=slots[3].fn(ctx)
assert(f.storage==250000 and f.cabin_capacity==250 and f.cost_metals==10000)
SMRTK.armed.station_rows_30={state={}}
local wait=slots[5].fn(ctx); local first=SMRTK.armed.depot_revision_wait
assert(wait.mode=='rest' and not SMRTK.armed.station_rows_30, 'slot 5 cancels the stale station-row watch')
slots[5].fn(ctx); assert(SMRTK.armed.depot_revision_wait~=first, 'slot 5 re-arms itself')
local st=SMRTK.armed.depot_revision_wait; now=st.state.deadline
local fired,done=triggers.depot_revision_wait.when(st); assert(fired and done.verdict=='hour_done')
S:ConstructUpgrade(D.CAPACITY_UPGRADE)
assert(slots[5].fn(ctx).mode=='upgrade'); st=SMRTK.armed.depot_revision_wait
Building.ApplyUpgrade(S,1)
fired,done=triggers.depot_revision_wait.when(st)
assert(fired and done.verdict=='upgrade_complete' and done.storage==500000)
S.trains_in_construction=1
assert(slots[5].fn(ctx).mode=='train'); st=SMRTK.armed.depot_revision_wait
S.trains_in_construction=0; S.available_trains=1
fired,done=triggers.depot_revision_wait.when(st); assert(fired and done.verdict=='train_complete')
S.trains_in_construction=1; S.available_trains=0
local route={trains=0}
S.ForEachConnectedTrack=function(self,fn) fn(route) end
function GetTrainsOnRoute(track) return track.trains end
slots[5].fn(ctx); st=SMRTK.armed.depot_revision_wait
S.trains_in_construction=0; route.trains=1
fired,done=triggers.depot_revision_wait.when(st)
assert(fired and done.verdict=='train_complete' and done.trains==0, 'native automatic assignment does not time out the train watch')
''')
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
print(f'command: python tools/trains/depot/tests/revision_smoke.py; HEAD={head} + working tree')
print('PASS: twinless rest/resume FX; lowest-stock/room/reservations both legs; 250/500 cabin and storage; '
      'native upgrade cost, shared receipt, no duplicate purchase, replacement, hub isolation; native train buttons both halves; '
      'generated class inheritance, staged fixture/run/read slots and stale-run replacement.')
for rel in ['Modifiers.lua', 'Buildings/Building.lua', 'Buildings/MultiResourceDepot.lua',
            'Buildings/UpgradableBuilding.lua', 'XDef/sectionCustom.generated.lua', 'XDef/customStation.generated.lua']:
    print('source: 1.1.1.406343', rel, hashlib.sha256((ARCHIVE / rel).read_bytes()).hexdigest())
