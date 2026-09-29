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
function table.remove_entry(list,value)
 for i=#list,1,-1 do if list[i]==value then table.remove(list,i) end end
end
function DirectlyModifiedConstValue() end
Modifiable={}; min_int64=-(2^63); max_int64=2^63-1
'''
for method in ['UpdateModifier', 'ModifyValue', 'SetBase']:
    SETUP += extract('Modifiers.lua', 'Modifiable:' + method)
SETUP += '''
Building.UpdateModifier=Modifiable.UpdateModifier
Building.ModifyValue=Modifiable.ModifyValue
Building.SetBase=Modifiable.SetBase
'''
SETUP += extract('ElectricityProducer.lua', 'ElectricityProducer:GetPerformanceModifiedElectricityProduction')
SETUP += extract('ElectricityProducer.lua', 'ElectricityProducer:GetUIPowerProduction')
SETUP += r'''
local prior=ElectricityProducer.GetPerformanceModifiedElectricityProduction
ElectricityProducer.GetPerformanceModifiedElectricityProduction=function(...)
 return prior(...),nil,'prior-production'
end
'''

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
 h.upgrade_modifiers={} -- fixture bulk-cleanup table, normally made by ApplyUpgrade
 h.upgrade3_can_disable=true
 h.base_electricity_production=h.electricity_production
 h.electricity={SetProduction=function(self,n) self.production=n end}
 h.GetUIPowerProduction=ElectricityProducer.GetUIPowerProduction
 h.ui_working=true
 h.Notify=function(self,prop) Building.Notify(self,prop); self:OnModifiableValueChanged(prop) end
 h:HubUpdateProduction()
 h.map=surface; h.work_radius=15
 function h:GetVisualPosXYZ() return self:GetPos():xy() end
 h:InitHubCapacityUpgrade()
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
check(both,false)
both:ApplyHeat(true); OnMsg.LoadGame(); check(both,false)
heat=0; research={}; ActiveLaws={}
assert(speed()==233,'Cargo off: vanilla cold')
local P,Q=hub(501),hub(601)
local function power(h,n)
 assert(h:GetUIPowerProduction()==n*1000,'power panel output '..h.handle..' got '..h:GetUIPowerProduction())
 local r=table.pack(h:GetPerformanceModifiedElectricityProduction())
 assert(r.n==3 and r[2]==nil and r[3]=='prior-production','power prior returns preserved')
end
power(P,75); power(Q,75)
P.reqs_pending={{GetResource=function() return 'Metals' end,GetActualAmount=function() return 0 end}}
P:ConstructUpgrade(POWER); P:StopUpgradeConstruction(POWER); Q:ConstructUpgrade(POWER)
assert(not Q:IsUpgradeBeingConstructed(POWER),'Power single construction claim')
P:ApplyUpgrade(3); power(P,150); power(Q,150); check(P,true); check(Q,true)
assert(Q:HasUpgrade(POWER) and Q:CanDisableUpgrade(POWER) and Q:IsUpgradeOn(POWER),'Power shared panel on')
Q:ApplyUpgrade(3); power(P,150); power(Q,150)
assert(speed()==700,'Power alone warm speed')
local remote={city={labels={Station={}},colony=UIColony}}
assert(speed(remote)==700,'Power same colony other map')
local foreign={city={labels={Station={}},colony={labels={Station={}}}}}
assert(speed(foreign)==233,'Power excludes other colony')
Q:ToggleUpgradeOnOff(POWER)
power(P,75); power(Q,75); check(P,false); check(Q,false)
assert(not P:IsUpgradeOn(POWER) and not Q:IsUpgradeOn(POWER),'Power shared panel off')
assert(P.upgrade_on_off_state[POWER]==false and Q.upgrade_on_off_state[POWER]==false,'Power raw panel off')
assert(speed()==233,'Power off cold speed')
Q:ToggleUpgradeOnOff(POWER); assert(speed()==700,'Power receiver switches on')
local later=hub(701); power(later,150); check(later,true)
assert(later:HasUpgrade(POWER) and later:IsUpgradeOn(POWER) and later:CanDisableUpgrade(POWER),'Power later hub panel')
Q.performance=120; Q:HubUpdateProduction(); power(Q,180)
Q.performance=nil; Q:HubUpdateProduction()
local doomed=hub(851); doomed.destroyed=true; OnMsg.BuildingDemolished(doomed)
power(doomed,0); check(doomed,false); power(P,150); power(Q,150)
both:ToggleUpgradeOnOff(CARGO); assert(speed()==875,'Power and Cargo compose')
Q:ToggleUpgradeOnOff(POWER); assert(speed()==291,'Cargo alone retains cold')
Q:ToggleUpgradeOnOff(POWER); both:ToggleUpgradeOnOff(CARGO)
research.FasterTrains=true; research.EvenFasterTrains=true; ActiveLaws.TrainSpeedStandards=law
local el={}; local warm=table.pack(speed(T1,el))
assert(warm.n==4 and warm[1]==1995 and warm[2]==5985 and warm[3]==nil and warm[4]=='prior-wrapper' and last_element==el,'Power preserves prior returns')
research.SafeTransport=true; assert(speed()==1995,'Power suppresses safe cold too')
local faster=Techs.FasterTrains; Techs.FasterTrains=nil
assert(not pcall(speed) and GetHeatAt==real_heat,'heat read restored after error'); Techs.FasterTrains=faster
assert(GetHeatAt==real_heat,'heat read restored')
Q:ToggleUpgradeOnOff(POWER); assert(speed()==1330,'Power off safe cold')
research.SafeTransport=nil; assert(speed()==665,'Power off ordinary cold')
Q:ToggleUpgradeOnOff(POWER)
P.working=false; P:HubUpdateProduction(); power(P,150); check(P,true)
local changes=grid.changed; OnMsg.LoadGame(); assert(grid.changed==changes,'Power load heat idempotent')
P.work_radius=19; OnMsg.LoadGame(); check(P,true)
-- A buyer is no longer the owner of the colony effects.
P.destroyed=true; OnMsg.BuildingDemolished(P); check(P,false); power(P,0)
power(Q,150); check(Q,true); assert(speed()==1995,'Power survives buyer salvage')
P:ToggleUpgradeOnOff(POWER); assert(not Q:IsUpgradeOn(POWER) and not P:IsUpgradeOn(POWER) and P:CanDisableUpgrade(POWER),'Power ruins share panel state')
P:ToggleUpgradeOnOff(POWER); power(Q,150)
P:StopUpgradeModifiers(); remove(city.labels.Station,P); P.deleted=true
power(Q,150); assert(speed()==1995,'Power survives buyer clear')
Q:ToggleUpgradeOnOff(POWER); power(later,75); check(later,false)
Q.destroyed=true; OnMsg.BuildingDemolished(Q); OnMsg.LoadGame()
assert(not later:IsUpgradeOn(POWER) and speed()==665,'Power off survives salvage/load')
later:ToggleUpgradeOnOff(POWER); power(later,150)
-- Remove all hubs, retaining ordinary stations and trains. State/modifiers live on the colony.
for i=#city.labels.Station,1,-1 do
 local h=city.labels.Station[i]
 if IsKindOf(h,'SMROptInTrainHubBase') then h:StopUpgradeModifiers(); h.deleted=true; table.remove(city.labels.Station,i) end
end
OnMsg.LoadGame(); assert(speed()==1995,'Power survives zero hubs/load')
local next_hub=hub(1001); power(next_hub,150); check(next_hub,true)
assert(next_hub:HasUpgrade(POWER) and next_hub:IsUpgradeOn(POWER),'Power future hub after zero hubs')
next_hub:ToggleUpgradeOnOff(POWER); power(next_hub,75); check(next_hub,false)
local underground={heat_grid=false}
next_hub.map=underground; next_hub:ToggleUpgradeOnOff(POWER) -- safe without heat grid

'''


MIGRATION = r'''
local POWER=SMROptInTrainHubBase.hub_power_upgrade
local old=hub(6430)
old:SetBase('electricity_production',70000)
Building.ApplyUpgrade(old,3)
assert(old:GetUIPowerProduction()==145000,'power old save reproduces 145')
local obsolete=old.upgrade_modifiers[POWER][1]
OnMsg.LoadGame()
assert(old:GetUIPowerProduction()==150000 and old.base_electricity_production==75000,'power old base repair')
assert(not obsolete:IsApplied() and #old.upgrade_modifiers[POWER]==0,'power old self modifier retired')
local receiver=hub(6431); assert(receiver:GetUIPowerProduction()==150000,'power migrated colony output')
receiver:ToggleUpgradeOnOff(POWER)
assert(old:GetUIPowerProduction()==75000,'power migrated switch')
old:SetBase('electricity_production',70000); OnMsg.LoadGame()
assert(old:GetUIPowerProduction()==75000 and not old:IsUpgradeOn(POWER),'power old base off repair')
local extra=ObjectModifier:new{target=old,prop='electricity_production',amount=10000,percent=20}
old:SetBase('electricity_production',70000); OnMsg.LoadGame()
assert(old:GetUIPowerProduction()==100000 and extra:IsApplied(),'power repair preserves unrelated modifier')
old:SetBase('electricity_production',80000); OnMsg.LoadGame()
assert(old:GetUIPowerProduction()==106000 and old.base_electricity_production==80000,'power repair only old 70')
'''


def run(code, power_fixture=FIXTURE):
    # Read every authored base assignment, not a second independent test constant.
    values = re.findall(r'\belectricity_production = (\d+)', code)
    assert values == ['75000', '75000', '75000'], ('base output assignments', values)
    bodies = '\n'.join(re.search(r'^function SMROptInTrainHubBase:' + name + r'\(.*?^end\n', code, re.M | re.S)[0]
                       for name in ['HubUpdateProduction', 'OnModifiableValueChanged'])
    cargo.run(code, CASES, SETUP, bodies + power_fixture)
    cargo.run(code, MIGRATION, SETUP, bodies + power_fixture)


if __name__ == '__main__':
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]))
    print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())
    code = cargo.SOURCE.read_text(encoding='utf8')
    print('source_sha256:', hashlib.sha256(cargo.SOURCE.read_bytes()).hexdigest())
    run(code)
    print('PASS Power: colony 75/150, shared controls, later hub, heat, cold immunity, salvage persistence, load, zero hubs')
    mutations = {
        'no heat': ('hub:ApplyHeat(on)', 'hub:ApplyHeat(false)'),
        'wrong range': ('return self.work_radius * const.GridSpacing', 'return 20 * const.GridSpacing'),
        'heat gated on Cargo': ('return colony_upgrade_on(colony, hub_power_upgrade)', 'return colony_upgrade_on(colony, hub_cargo_upgrade)'),
        'warm network': ('if power then result = warm_speed(previous, self, ...)', 'if power then result = table.pack(previous(self, ...))'),
        'heat restore': ('\t_G.GetHeatAt = heat\n', '\n'),
        'base output': ('electricity_production = 75000', 'electricity_production = 70000'),
        'production notification': ('if prop == "electricity_production" or prop == "performance" then', 'if prop == "performance" then'),
        'power output': ('result[1] = result[1] + MulDivRound(75000', 'result[1] = result[1] + MulDivRound(0'),
        'per-hub display': ('return colony_upgrade_on(self.city.colony, id)', 'return true'),
        'receiver switch refused': ('entry.on = not entry.on', 'if self.handle == 601 then return end\n\tentry.on = not entry.on'),
        'raw display': ('hub.upgrade_on_off_state[id] = entry.on', 'hub.upgrade_on_off_state[id] = true'),
        'later hub heat': ('\tmirror_upgrades(self, colony_upgrades(self.city and self.city.colony))\n\tsync_power_heat(self)', '\tmirror_upgrades(self, colony_upgrades(self.city and self.city.colony))'),
        'salvage persistence': ('if IsKindOf(bld, "SMROptInTrainHubBase") then sync_colony_upgrades(bld.city and bld.city.colony) end', 'if IsKindOf(bld, "SMROptInTrainHubBase") then local e = colony_upgrades(bld.city.colony)[hub_power_upgrade]; if e then e.on = false end; sync_colony_upgrades(bld.city.colony) end'),
        'zero hubs persistence': ('local state = colony_upgrades(colony)', 'if #colony.labels.Station == 1 then colony.SMROptIn_hub_upgrades = nil end\n\tlocal state = colony_upgrades(colony)'),
        'power unlock': ('local hub_upgrades = { hub_capacity_upgrade, hub_cargo_upgrade, hub_power_upgrade }', 'local hub_upgrades = { hub_capacity_upgrade, hub_cargo_upgrade }'),
        'saved-base migration': ('then rebase_hub_power(hub) end', 'then --[[ no rebase ]] end'),
        'saved-base scope': ('if hub.base_electricity_production ~= 70000 then return end', 'if false then return end'),
    }
    for name, (before, after) in mutations.items():
        assert before in code, name
        try:
            run(code.replace(before, after, 1))
        except (LuaError, AssertionError) as exc:
            assert any(s in str(exc) for s in ['heater registration', 'heater geometry', 'outside stays cold', 'assertion failed',
        'Power', 'power', 'global off display', 'cargo alone', 'heat read restored', 'base output', 'grid production', 'rebase']), str(exc)
            print('PASS mutation rejected:', name)
        else:
            raise AssertionError('mutation survived: ' + name)
    before = "h['upgrade3_add_value_1'] = 75000"
    assert before in FIXTURE
    try:
        run(code, FIXTURE.replace(before, "h['upgrade3_add_value_1'] = 0"))
    except LuaError as exc:
        assert 'power old save' in str(exc), str(exc)
        print('PASS mutation rejected: Power output addition')
    else:
        raise AssertionError('mutation survived: Power output addition')
