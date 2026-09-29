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
-- Cargo alone has no heat, including cleanup of heat left by the old Cargo build.
check(both,false)
SelectedObj=both; both:ToggleUpgradeOnOff(CARGO); check(both,false)
both:ApplyHeat(true); OnMsg.LoadGame(); check(both,false)
both:ToggleUpgradeOnOff(CARGO)
local P,Q=hub(501),hub(601)
local function power(h,n)
 assert(h.electricity.production==n*1000,'power grid production: '..tostring(h.handle)..' got '..tostring(h.electricity.production)..' expected '..n*1000)
 assert(h:GetUIPowerProduction()==n*1000,'power panel output')
 local r=table.pack(h:GetPerformanceModifiedElectricityProduction())
 assert(r.n==3 and r[2]==nil and r[3]=='prior-production','power prior returns preserved')
end
power(P,75); power(Q,75)
-- Existing-save regression: class 75 does not replace a saved placement base of 70.
local legacy=hub(6430)
legacy:SetBase('electricity_production',70000); legacy:ApplyUpgrade(3)
power(legacy,145) -- actual vanilla Modifiable arithmetic, the reported failure
local mods=legacy.upgrade_modifiers[POWER]; local modifier=mods[1]
OnMsg.LoadGame(); power(legacy,150)
assert(legacy.base_electricity_production==75000 and legacy.upgrade_modifiers[POWER]==mods
 and mods[1]==modifier and modifier:IsApplied(),'rebase preserves upgrade identity/state')
SelectedObj=legacy; legacy:ToggleUpgradeOnOff(POWER); power(legacy,75)
legacy:SetBase('electricity_production',70000); OnMsg.LoadGame(); power(legacy,75)
assert(not modifier:IsApplied() and not legacy:IsUpgradeOn(POWER),'rebase preserves off state')
local bare=hub(6431); bare:SetBase('electricity_production',70000); OnMsg.LoadGame(); power(bare,75)
local extra=ObjectModifier:new{target=bare,prop='electricity_production',amount=10000,percent=20}
bare:SetBase('electricity_production',70000); OnMsg.LoadGame(); power(bare,100)
assert(extra:IsApplied() and #bare.modifications.electricity_production==1,'rebase retains unrelated modifiers')
bare:SetBase('electricity_production',80000); OnMsg.LoadGame(); power(bare,106)
assert(bare.base_electricity_production==80000,'rebase only old 70')
local before_mods=bare.modifications.electricity_production
OnMsg.LoadGame(); assert(bare.modifications.electricity_production==before_mods,'rebase idempotence')
extra:TurnOff(); power(bare,80)
legacy:StopUpgradeModifiers(); remove(city.labels.Station,legacy); legacy.deleted=true
local ruined=hub(6432); ruined:SetBase('electricity_production',70000); ruined:ApplyUpgrade(3)
ruined.destroyed=true; OnMsg.LoadGame()
assert(ruined.base_electricity_production==75000 and ruined.electricity_production==75000
 and ruined.electricity.production==0,'old ruin rebased but inactive')
check(ruined,false)
ruined:StopUpgradeModifiers(); remove(city.labels.Station,ruined); ruined.deleted=true
-- Cancelled construction retains the colony claim, as with Cargo and Capacity.
P.reqs_pending={{GetResource=function() return 'Metals' end,GetActualAmount=function() return 0 end}}
Q.reqs_pending=P.reqs_pending
P:ConstructUpgrade(POWER)
assert(P.upgrades_under_construction and P.upgrades_under_construction[POWER],'power construction start')
P:StopUpgradeConstruction(POWER); Q:ConstructUpgrade(POWER)
assert(not Q.upgrades_under_construction or not Q.upgrades_under_construction[POWER],'power colony construction claim')
P:ApplyUpgrade(3); power(P,150); power(Q,150); check(P,true); check(Q,true)
assert(Q:HasUpgrade(POWER) and not Q:CanDisableUpgrade(POWER),'power spent on other hub')
Q:ApplyUpgrade(3); assert(not Building.HasUpgrade(Q,POWER),'power cannot buy twice')
SelectedObj=Q; P:ToggleUpgradeOnOff(POWER); power(P,150); power(Q,150)
local later=hub(701); power(later,150); check(later,true)
assert(later:HasUpgrade(POWER) and not later:CanDisableUpgrade(POWER),'later hub spent')
-- Another map's hub receives output and heat from the same colony.
local remote_hub=hub(801); remote_hub.city={labels={Station={remote_hub}},colony=UIColony}
OnMsg.LoadGame(); power(remote_hub,150); check(remote_hub,true)
Q.performance=120; Q:HubUpdateProduction(); power(Q,180)
Q.performance=nil; Q:HubUpdateProduction()
local doomed=hub(851); doomed.destroyed=true; OnMsg.BuildingDemolished(doomed)
assert(doomed:GetUIPowerProduction()==0,'Power receiver ruins production'); check(doomed,false)
power(P,150); power(Q,150)
local foreign_hub=hub(901); foreign_hub.city={labels={Station={foreign_hub}},colony={labels={Station={foreign_hub}}}}
foreign_hub:InitHubCapacityUpgrade(); power(foreign_hub,75); check(foreign_hub,false)
heat=0; research={}; ActiveLaws={}
assert(speed()==700,'Power alone: warm without cargo boost')
local remote={city={labels={Station={}},colony=UIColony}}
assert(speed(remote)==700,'Power warms another city in same colony')
local foreign={city={labels={Station={}},colony={labels={Station={}}}}}
assert(speed(foreign)==233,'Power does not warm another colony')
SelectedObj=both; both:ToggleUpgradeOnOff(CARGO)
assert(speed()==875,'both effects compose')
SelectedObj=P; Q:ToggleUpgradeOnOff(POWER); power(Q,150); check(Q,true)
P:ToggleUpgradeOnOff(POWER); power(P,75); power(Q,75); power(later,75)
check(P,false); check(Q,false); check(later,false)
assert(speed()==291,'Power off restores cold with cargo bonus')
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
Q:ConstructUpgrade(POWER)
assert(not Q.upgrades_under_construction or not Q.upgrades_under_construction[POWER],'Power ruins hold claim')
-- The existing rebuild carry remains symmetric; normal hub rebuild is not a live requirement.
local rebuilt=hub(502,501000); rebuilt:ApplyCopyParams({})
assert(Building.HasUpgrade(rebuilt,POWER),'Power carries existing shared claim')
power(rebuilt,150); power(Q,150); check(rebuilt,true); check(Q,true)
P:StopUpgradeModifiers(); check(rebuilt,true)
Q:StopUpgradeModifiers(); check(Q,false) -- non-owning Done removes its own heater
remove(city.labels.Station,Q); Q.deleted=true
assert(speed()==1995,'receiver deletion preserves colony Power')
rebuilt:StopUpgradeModifiers(); remove(city.labels.Station,rebuilt); rebuilt.deleted=true
power(later,75); check(later,false); assert(speed()==665,'owner deletion removes colony Power')
later:ApplyUpgrade(3); power(later,150); check(later,true)
SelectedObj=later; later:ToggleUpgradeOnOff(POWER); power(later,75); check(later,false)
-- Old per-hub saves may contain two receipts. Preserve the active buyer,
-- demote the inactive receipt to spent, and do not stack or recreate modifiers.
local duplicate=hub(1001); duplicate.HasUpgrade=Building.HasUpgrade
Building.ApplyUpgrade(duplicate,3); duplicate.HasUpgrade=nil
local receipt=duplicate.upgrade_modifiers[POWER][1]
OnMsg.LoadGame()
assert(Building.HasUpgrade(duplicate,POWER) and not Building.HasUpgrade(later,POWER),'Power active legacy buyer retained')
assert(later:HasUpgrade(POWER) and not later:CanDisableUpgrade(POWER),'Power duplicate becomes spent')
power(later,150); power(duplicate,150); check(later,true)
OnMsg.LoadGame(); assert(duplicate.upgrade_modifiers[POWER][1]==receipt,'Power claim repair idempotent')
SelectedObj=duplicate; duplicate:ToggleUpgradeOnOff(POWER); power(later,75); check(later,false)
-- All-off duplicate receipts stay off after consolidation.
later.HasUpgrade=Building.HasUpgrade; Building.ApplyUpgrade(later,3); later.HasUpgrade=nil
Building.ToggleUpgradeOnOff(later,POWER)
OnMsg.LoadGame(); power(later,75); power(duplicate,75)
assert(Building.HasUpgrade(later,POWER) and not Building.HasUpgrade(duplicate,POWER),'Power first off claim retained')
SelectedObj=later
local underground={heat_grid=false}
later.map=underground; later:ToggleUpgradeOnOff(POWER) -- no heat grid: safe
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
    print('PASS Power: colony 75/150, spent claim, later hub, heat, cold immunity, salvage, load, carry, deletion')
    mutations = {
        'no heat': ('hub:ApplyHeat(on)', 'hub:ApplyHeat(false)'),
        'wrong range': ('return self.work_radius * const.GridSpacing', 'return 20 * const.GridSpacing'),
        'bulk cleanup': ('table.pack(Building.StopUpgradeModifiers(self, ...))', 'table.pack()'),
        'heat gated on Cargo': ('local on = not hub.destroyed and colony_power_on(hub.city and hub.city.colony)', 'local on = upgrade_applied(hub, hub_cargo_upgrade)'),
        'warm network': ('if power then result = warm_speed(previous, self, ...)', 'if power then result = table.pack(previous(self, ...))'),
        'heat restore': ('\t_G.GetHeatAt = heat\n', '\n'),
        'base output': ('electricity_production = 75000', 'electricity_production = 70000'),
        'production notification': ('if prop == "electricity_production" or prop == "performance" then', 'if prop == "performance" then'),
        'power ownership': ('return id == hub_capacity_upgrade or id == hub_cargo_upgrade or id == hub_power_upgrade end', 'return id == hub_capacity_upgrade or id == hub_cargo_upgrade end'),
        'per-hub power': ('result[1] = result[1] + MulDivRound(75000', 'result[1] = result[1] + MulDivRound(0'),
        'per-hub heat': ('local on = not hub.destroyed and colony_power_on(hub.city and hub.city.colony)', 'local on = upgrade_applied(hub, hub_power_upgrade)'),
        'later hub': ('\tunlock_capacity_upgrade()\n\tsync_power_heat(self)\n\tif self.HubUpdateProduction then self:HubUpdateProduction() end', '\tunlock_capacity_upgrade()'),
        'salvage Power': ('hub:StopUpgradeModifiersForUpgrade(id)', 'if id ~= hub_power_upgrade then hub:StopUpgradeModifiersForUpgrade(id) end'),
        'Power carry': ('ipairs(hub_upgrades) do carry_upgrade', 'ipairs({ hub_capacity_upgrade, hub_cargo_upgrade }) do carry_upgrade'),
        'colony scope': ('local colony = train.city and train.city.colony', 'local colony = train.city'),
        'ruins bulk guard': ('\tif self.destroyed then return end\n\tlocal result = table.pack(Building.ApplyUpgradeModifiers', '\tlocal result = table.pack(Building.ApplyUpgradeModifiers'),
        'Power unlock': ('local hub_upgrades = { hub_capacity_upgrade, hub_cargo_upgrade, hub_power_upgrade }', 'local hub_upgrades = { hub_capacity_upgrade, hub_cargo_upgrade }'),
        'duplicate claim': ('\treconcile_power_claim()\n', '\n'),
        'saved-base migration': ('then rebase_hub_power(hub) end', 'then --[[ no rebase ]] end'),
        'saved-base scope': ('if hub.base_electricity_production ~= 70000 then return end', 'if false then return end'),
    }
    for name, (before, after) in mutations.items():
        assert before in code, name
        try:
            run(code.replace(before, after, 1))
        except (LuaError, AssertionError) as exc:
            assert any(s in str(exc) for s in ['heater registration', 'heater geometry', 'outside stays cold', 'assertion failed',
        'Power', 'power', 'heat read restored', 'base output', 'grid production', 'rebase']), str(exc)
            print('PASS mutation rejected:', name)
        else:
            raise AssertionError('mutation survived: ' + name)
    before = "h['upgrade3_add_value_1'] = 75000"
    assert before in FIXTURE
    try:
        run(code, FIXTURE.replace(before, "h['upgrade3_add_value_1'] = 0"))
    except LuaError as exc:
        assert 'power grid production' in str(exc), str(exc)
        print('PASS mutation rejected: Power output addition')
    else:
        raise AssertionError('mutation survived: Power output addition')
