"""Power Upgrade: archived heater, ObjectModifier and upgrade bodies; native grid is a double."""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from lupa import LuaError
import cargo_upgrade_smoke as cargo

ARCHIVE = cargo.ROOT.parent / 'SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua'


def extract(path, name):
    text = (ARCHIVE / path).read_text(encoding='utf8')
    return re.search(r'^function ' + re.escape(name) + r'\(.*?^end\n', text, re.M | re.S)[0]


SETUP = r'''
BaseHeater={}; SubsurfaceHeaterBase={heat=5*const.MaxHeat}; HeatGrid={}
const.GridSpacing=1000
function table.iequals(a,b)
 for i=1,math.max(#a,#b) do if a[i]~=b[i] then return false end end
 return true
end
function Heat_AddCircle(grid,x,y,radius,heat,border)
 table.insert(grid,{x=x,y=y,radius=radius,heat=heat,border=border})
end
function HeatGrid:OnHeatGridChanged() self.changed=(self.changed or 0)+1 end
function HeatGrid:sample(x,y)
 local heat=0 -- cold-wave background
 for _,v in ipairs(self.grid_target) do
  if (x-v.x)^2+(y-v.y)^2<=v.radius^2 then heat=heat+v.heat end
 end
 return math.min(const.MaxHeat,math.max(0,heat))
end
'''
for method in ['GetHeatCenter', 'ApplyHeat', 'ApplyForm']:
    SETUP += extract('Heater.lua', 'BaseHeater:' + method)
SETUP += extract('Heat.lua', 'HeatGrid:ApplyHeatForm')
SETUP += extract('Buildings/Building.lua', 'Building:ApplyUpgradeModifiers')
SETUP += '\nObjectModifier={}\nObjectModifier.__index=ObjectModifier\nElectricityProducer={}\n'
for method in ['Init', 'Add', 'Remove', 'IsApplied']:
    SETUP += extract('Modifiers.lua', 'ObjectModifier:' + method)
SETUP += r'''
ObjectModifier.TurnOn=ObjectModifier.Add; ObjectModifier.TurnOff=ObjectModifier.Remove
function ObjectModifier:new(t) setmetatable(t,self); t:Init(); return t end
function Building:GetProperty(key) return self[key] end
function Building:HasMember(key) return self[key]~=nil end
function Building:UpdateModifier(op,mod)
 local list=self.mods[mod.prop] or {}; self.mods[mod.prop]=list
 if op=='add' then table.insert(list,mod)
 else for i=#list,1,-1 do if list[i]==mod then table.remove(list,i) end end end
 local amount,percent=0,0
 for _,m in ipairs(list) do amount=amount+m.amount; percent=percent+m.percent end
 self[mod.prop]=self.base[mod.prop]*(100+percent)//100+amount
 self:Notify(mod.prop)
end
'''
SETUP += extract('ElectricityProducer.lua', 'ElectricityProducer:GetPerformanceModifiedElectricityProduction')

FIXTURE = r'''
local surface={heat_grid=setmetatable({heaters={},grid_target={},map_width=1000000,map_height=1000000}, {__index=HeatGrid})}
city.colony=UIColony
local original_hub=hub
hub=function(...)
 local h=original_hub(...)
 POWER_TEMPLATE
 for i=1,3 do
  h['upgrade3_mod_prop_id_'..i]=h['upgrade3_mod_prop_id_'..i] or ''
  h['upgrade3_mul_value_'..i]=h['upgrade3_mul_value_'..i] or 0
  h['upgrade3_add_value_'..i]=h['upgrade3_add_value_'..i] or 0
 end
 h.upgrade3_can_disable=true
 h.base.electricity_production=h.electricity_production
 h.electricity={SetProduction=function(self,n) self.production=n end}
 h.GetPerformanceModifiedElectricityProduction=ElectricityProducer.GetPerformanceModifiedElectricityProduction
 h.ui_working=true
 h.Notify=function(self,prop) Building.Notify(self,prop); self:OnModifiableValueChanged(prop) end
 h:HubUpdateProduction()
 h.map=surface; h.work_radius=15
 function h:GetVisualPosXYZ() return self:GetPos():xy() end
 return h
end
'''.replace('POWER_TEMPLATE', '\n'.join('h[%r] = %s' % (k, v) for k, v in cargo.expected.items()
                                     if k.startswith('upgrade3_') or k == 'electricity_production'))

CASES = r'''
local grid=surface.heat_grid
local function check(h,on)
 local x,y=h:GetVisualPosXYZ()
 assert((grid.heaters[h]~=nil)==on,'heater registration state')
 if on then
  local info=grid.heaters[h]
  assert(info[1]==-SubsurfaceHeaterBase.heat and info[4]==h.work_radius*const.GridSpacing and info[5]==0,'heater geometry')
  assert(grid:sample(x+h.work_radius*const.GridSpacing,y)>90,'warm service edge')
 else
  assert(grid:sample(x,y)<=90,'cold after removal')
 end
 assert(grid:sample(x+(h.work_radius+1)*const.GridSpacing,y)<=90,'outside stays cold')
end
local POWER=SMROptInTrainHubBase.hub_power_upgrade
assert(UIColony:IsUpgradeUnlocked(POWER),'power unlocked without tech')
-- Cargo alone has no heat, including cleanup of heat left by the old Cargo build.
check(both,false)
SelectedObj=both; both:ToggleUpgradeOnOff(CARGO); check(both,false)
both:ApplyHeat(true); OnMsg.LoadGame(); check(both,false)
both:ToggleUpgradeOnOff(CARGO)
local P,Q=hub(501),hub(601)
local function power(h,n) assert(h.electricity_production==n*1000,'power property'); assert(h.electricity.production==n*1000,'grid production') end
power(P,75); power(Q,75)
-- Construction at one hub, even cancelled with delivered resources, cannot claim the other.
P.reqs_pending={{GetResource=function() return 'Metals' end,GetActualAmount=function() return 0 end}}
Q.reqs_pending=P.reqs_pending
P:ConstructUpgrade(POWER); P:StopUpgradeConstruction(POWER); Q:ConstructUpgrade(POWER)
assert(P.upgrades_under_construction and P.upgrades_under_construction[POWER] and Q.upgrades_under_construction and Q.upgrades_under_construction[POWER],'independent power construction')
P:ApplyUpgrade(3); power(P,150); power(Q,75); check(P,true); check(Q,false)
assert(not Q:HasUpgrade(POWER),'power is not spent on another hub')
Q:ApplyUpgrade(3); power(P,150); power(Q,150); check(Q,true)
assert(P:CanDisableUpgrade(POWER) and Q:CanDisableUpgrade(POWER),'both power owners can switch')
heat=0; research={}; ActiveLaws={}
assert(speed()==700,'Power alone: warm without cargo boost')
local remote={city={labels={Station={}},colony=UIColony}}
assert(speed(remote)==700,'Power warms another city in same colony')
local foreign={city={labels={Station={}},colony={labels={Station={}}}}}
assert(speed(foreign)==233,'Power does not warm another colony')
SelectedObj=both; both:ToggleUpgradeOnOff(CARGO)
assert(speed()==875,'both effects compose')
SelectedObj=P; Q:ToggleUpgradeOnOff(POWER); power(Q,75); check(Q,false)
assert(speed()==875,'one Power owner keeps network warm')
P:ToggleUpgradeOnOff(POWER); power(P,75); check(P,false)
assert(speed()==291,'last Power off restores cold with cargo bonus')
SelectedObj=both; both:ToggleUpgradeOnOff(CARGO)
assert(speed()==233,'neither upgrade uses vanilla cold')
SelectedObj=P; P:ToggleUpgradeOnOff(POWER); power(P,150); check(P,true)
research.FasterTrains=true; research.EvenFasterTrains=true; ActiveLaws.TrainSpeedStandards=law
local el={}; local warm=table.pack(speed(T1,el))
assert(warm.n==4 and warm[1]==1995 and warm[2]==5985 and warm[3]==nil and warm[4]=='prior-wrapper' and last_element==el,'Power preserves prior returns')
research.SafeTransport=true; assert(speed()==1995,'Power suppresses safe cold too')
local faster=Techs.FasterTrains; Techs.FasterTrains=nil
assert(not pcall(speed) and GetHeatAt==real_heat,'heat read restored after error'); Techs.FasterTrains=faster
assert(GetHeatAt==real_heat,'heat read restored')
P:ToggleUpgradeOnOff(POWER); assert(speed()==1330,'Power off safe cold')
research.SafeTransport=nil; assert(speed()==665,'Power off ordinary cold')
P:ToggleUpgradeOnOff(POWER)
P.working=false; check(P,true); P:HubUpdateProduction(); power(P,150)
local changes=grid.changed
OnMsg.LoadGame(); check(P,true); power(P,150)
assert(grid.changed==changes,'load is idempotent')
P.work_radius=19; OnMsg.LoadGame(); check(P,true)
P:StopUpgradeModifiers(); check(P,false); power(P,75); assert(speed()==665,'bulk cleanup removes warmth')
P:ApplyUpgradeModifiers(); check(P,true); power(P,150)
P.destroyed=true; P:HubUpdateProduction(); OnMsg.BuildingDemolished(P); check(P,false)
assert(P.electricity_production==75000 and P.electricity.production==0,'ruins production off')
assert(speed()==665,'salvage removes last Power warmth')
P:ApplyUpgradeModifiersForUpgrade(POWER); P:ApplyUpgradeModifiers(); P:ToggleUpgradeOnOff(POWER)
assert(P.electricity_production==75000,'ruins cannot reactivate Power'); check(P,false)
-- Pre-fix saved ruins with active modifiers are reconciled on load.
Building.ApplyUpgradeModifiersForUpgrade(P,POWER); OnMsg.LoadGame(); check(P,false)
assert(P.electricity_production==75000,'loaded ruin Power removed')
local rebuilt=hub(502,501000); rebuilt:ApplyCopyParams({})
assert(not rebuilt:HasUpgrade(POWER),'Power never carries from ruins'); check(rebuilt,false); power(rebuilt,75)
rebuilt:ApplyUpgrade(3); power(rebuilt,150); check(rebuilt,true)
P:StopUpgradeModifiers(); check(rebuilt,true) -- old ruin cannot remove new hub heat
SelectedObj=Q; Q:ToggleUpgradeOnOff(POWER); check(Q,true)
rebuilt:StopUpgradeModifiers(); remove(city.labels.Station,rebuilt); rebuilt.deleted=true
assert(speed()==1995,'second hub survives first deletion')
SelectedObj=Q; Q:ToggleUpgradeOnOff(POWER); check(Q,false); power(Q,75)
assert(speed()==665,'all Power off after deletion')
local underground={heat_grid=false}
Q.map=underground; Q:ToggleUpgradeOnOff(POWER) -- no heat grid: safe
'''


def run(code, power_fixture=FIXTURE):
    # Read every authored base assignment, not a second independent test constant.
    values = re.findall(r'\belectricity_production = (\d+)', code)
    assert values == ['75000', '75000', '75000'], ('base output assignments', values)
    bodies = '\n'.join(re.search(r'^function SMROptInTrainHubBase:' + name + r'\(.*?^end\n', code, re.M | re.S)[0]
                       for name in ['HubUpdateProduction', 'OnModifiableValueChanged'])
    cargo.run(code, CASES, SETUP, bodies + power_fixture)


if __name__ == '__main__':
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]))
    print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())
    code = cargo.SOURCE.read_text(encoding='utf8')
    print('source_sha256:', hashlib.sha256(cargo.SOURCE.read_bytes()).hexdigest())
    run(code)
    print('PASS Power: per-hub 75/150, construction, toggles, heat, colony cold immunity, salvage, load, no carry, deletion')
    mutations = {
        'no heat': ('hub:ApplyHeat(on)', 'hub:ApplyHeat(false)'),
        'wrong range': ('return self.work_radius * const.GridSpacing', 'return 20 * const.GridSpacing'),
        'bulk cleanup': ('table.pack(Building.StopUpgradeModifiers(self, ...))', 'table.pack()'),
        'heat gated on Cargo': ('local on = upgrade_applied(hub, hub_power_upgrade)', 'local on = upgrade_applied(hub, hub_cargo_upgrade)'),
        'warm network': ('if power then result = warm_speed(previous, self, ...)', 'if power then result = table.pack(previous(self, ...))'),
        'heat restore': ('\t_G.GetHeatAt = heat\n', '\n'),
        'base output': ('electricity_production = 75000', 'electricity_production = 70000'),
        'production notification': ('if prop == "electricity_production" or prop == "performance" then', 'if prop == "performance" then'),
        'power ownership': ('return id == hub_capacity_upgrade or id == hub_cargo_upgrade end', 'return id == hub_capacity_upgrade or id == hub_cargo_upgrade or id == hub_power_upgrade end'),
        'salvage Power': ('hub:StopUpgradeModifiersForUpgrade(id)', 'if id ~= hub_power_upgrade then hub:StopUpgradeModifiersForUpgrade(id) end'),
        'Power must not carry': ('ipairs({ hub_capacity_upgrade, hub_cargo_upgrade }) do carry_upgrade', 'ipairs(hub_upgrades) do carry_upgrade'),
        'colony scope': ('local colony = train.city and train.city.colony', 'local colony = train.city'),
        'ruins bulk guard': ('\tif self.destroyed then return end\n\tlocal result = table.pack(Building.ApplyUpgradeModifiers', '\tlocal result = table.pack(Building.ApplyUpgradeModifiers'),
        'Power unlock': ('local hub_upgrades = { hub_capacity_upgrade, hub_cargo_upgrade, hub_power_upgrade }', 'local hub_upgrades = { hub_capacity_upgrade, hub_cargo_upgrade }'),
    }
    for name, (before, after) in mutations.items():
        assert before in code, name
        try:
            run(code.replace(before, after, 1))
        except (LuaError, AssertionError) as exc:
            assert any(s in str(exc) for s in ['heater registration', 'heater geometry', 'outside stays cold', 'assertion failed',
                'Power', 'power', 'heat read restored', 'base output', 'grid production']), str(exc)
            print('PASS mutation rejected:', name)
        else:
            raise AssertionError('mutation survived: ' + name)
    before = "h['upgrade3_add_value_1'] = 75000"
    assert before in FIXTURE
    try:
        run(code, FIXTURE.replace(before, "h['upgrade3_add_value_1'] = 0"))
    except LuaError as exc:
        assert 'power property' in str(exc), str(exc)
        print('PASS mutation rejected: Power output addition')
    else:
        raise AssertionError('mutation survived: Power output addition')
