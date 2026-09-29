"""Cargo upgrade over capacity_smoke's archived vanilla bodies; no game/save claim.

Reads authored Data fields before the owner's required Mod Editor regeneration.
Mutants run in memory; no working-tree source changes or generated-byte edits.
"""
import contextlib
import hashlib
import io
import re
import subprocess
import sys
from pathlib import Path
from lupa import LuaError

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = HERE.parent / 'Code/20_TrainHub.lua'
DATA = HERE.parent / 'Data/BuildingTemplate/SMROptInTrainHub6.lua'
harness = (HERE / 'capacity_smoke.py').read_text(encoding='utf8')
prefix, rest = harness.split("lua.execute(r'''\nlocal ID =", 1)
fixture = 'local ID =' + rest.split('-- 1. Unlocked from the start', 1)[0]
fields = dict(re.findall(r"^\t'(upgrade[23]_\w+|electricity_production)', (.*),$", DATA.read_text(encoding='utf8'), re.M))
# Mod Editor may omit values equal to the property's default. Compare effective fields:
# self is UpgradableBuilding's default target; output inherits the hub's class value.
class_power = re.search(r'^\telectricity_production = (\d+),$', SOURCE.read_text(encoding='utf8'), re.M)[1]
defaults = {'upgrade3_mod_target_1': '"self"', 'electricity_production': class_power}
fields = defaults | fields
expected = {
    'upgrade2_id': '"SMROptInTrainHub6_TrainCargo"',
    'upgrade2_mod_target_1': '"city"', 'upgrade2_mod_label_1': '"Train"',
    'upgrade2_mod_prop_id_1': '"max_shared_storage"', 'upgrade2_mul_value_1': '100',
    'upgrade2_upgrade_cost_Metals': '40000', 'upgrade2_upgrade_cost_Polymers': '20000',
    'upgrade3_id': '"SMROptInTrainHub6_Power"',
    'upgrade3_mod_target_1': '"self"', 'upgrade3_mod_prop_id_1': '"electricity_production"',
    'upgrade3_add_value_1': '75000',
    'upgrade3_upgrade_cost_Metals': '30000', 'upgrade3_upgrade_cost_Electronics': '20000',
    'electricity_production': '75000',
}
for key, value in expected.items():
    assert fields.get(key) == value, (key, fields.get(key), value)
assert not any('mod_prop_id' in k and k not in ('upgrade2_mod_prop_id_1', 'upgrade3_mod_prop_id_1') for k in fields)
assert not any('require' in k or 'unlock' in k for k in fields), 'no tech requirement'
generated = dict(re.findall(r'^\t(upgrade[23]_\w+|electricity_production) = (.*),$',
    (HERE.parent / 'Code/BuildingTemplate/SMROptInTrainHub6.generated.lua').read_text(encoding='utf8'), re.M))
generated = defaults | generated
assert not any(word in fields['upgrade2_description'] for word in ('warm', 'heat', 'cold')), 'cargo has no cold protection'
assert '75 to 150' in fields['upgrade3_description'] and 'Each hub' in fields['upgrade3_description']
generated_current = generated == fields
if '--require-generated' in sys.argv:
    assert generated_current, ('Mod Editor regeneration owed',
        {k: (generated.get(k), fields.get(k)) for k in generated.keys() | fields.keys() if generated.get(k) != fields.get(k)})
template = '\n'.join('h[%r] = %s' % (k, v) for k, v in expected.items() if k.startswith('upgrade2_'))

SPEED_SETUP = r'''
SMROptInTrainFloor = {}; Train={move_speed=1000}
function MulDivRound(a,b,c) return math.floor(a*b/c+0.5) end
local function tech(values) return {ResolveValue=function(_,k) return values[k] end} end
Techs={FasterTrains=tech({param1=100,param2=70}),EvenFasterTrains=tech({speed=50})}
research={}; heat=100; ActiveLaws={}
function UIColony:IsTechResearched(id) return research[id] end
function GetHeatAt(o) last_heat_object=o; return heat end
real_heat=GetHeatAt; const=const or {}; const.MaxHeat=const.MaxHeat or 256
law={ResolveValue=function() return 33 end}
'''

CASES = r'''
local CARGO=SMROptInTrainHubBase.hub_cargo_upgrade
local old_hub=hub
hub=function(...)
 local h=old_hub(...)
 TEMPLATE
 h.upgrade2_add_value_1=0; h.upgrade2_can_disable=true
 -- The native label container applies active modifiers to new members.
 for _,m in pairs(city.label_modifiers.Station or {}) do
  if m:IsApplied() then
   h.mods[m.prop]=h.mods[m.prop] or {}; table.insert(h.mods[m.prop],m)
   h[m.prop]=h[m.prop]+h.base[m.prop]*m.percent//100+m.amount
  end
 end
 return h
end
OnMsg.CityStart()
assert(UIColony:IsUpgradeUnlocked(ID) and UIColony:IsUpgradeUnlocked(CARGO))
local A,B=hub(201),hub(202)
local T1=train(301)
local small=depot(Building,101,60000,{'Station'})
local function speed(t,element) return Train.GetNominalMoveSpeed(t or T1,element) end
assert(speed()==700)
-- Independent claims: B may buy cargo while A owns capacity.
A:ApplyUpgrade(1)
B.reqs_pending={{GetResource=function() return 'Metals' end,GetActualAmount=function() return 0 end}}
B:ConstructUpgrade(CARGO)
A:ConstructUpgrade(CARGO)
assert(not A.upgrades_under_construction or not A.upgrades_under_construction[CARGO], 'cargo construction claim')
B:StopUpgradeConstruction(CARGO); A:ConstructUpgrade(CARGO)
assert(not A.upgrades_under_construction or not A.upgrades_under_construction[CARGO], 'cancelled claim held')
B.reqs_pending=false; B:ApplyUpgrade(2)
assert(T1.max_shared_storage==126000 and T1.max_colonists_to_transport==24, 'additive cargo; passengers unchanged')
assert(small.max_storage_per_resource==120000, 'cargo does not change station storage')
assert(count_mods()==4 and speed()==875, 'one cargo modifier and speed boost')
assert(A:HasUpgrade(CARGO) and not A:CanDisableUpgrade(CARGO), 'other hub spent')
B.working=false; assert(speed()==875, 'vanilla power behavior')
-- Every prior return is retained; both speed outputs scale, extra nil/value survive.
local el={}
local r=table.pack(speed(T1,el))
assert(r.n==4 and r[1]==875 and r[2]==2625 and r[3]==nil and r[4]=='prior-wrapper')
assert(last_element==el, 'element argument chained')
local foreign={city={labels={Station={}}}}
assert(speed(foreign)==700, 'foreign city delegates unchanged')
SelectedObj=A; B:ToggleUpgradeOnOff(CARGO)
assert(speed()==875, 'spent-hub broadcast inert')
SelectedObj=B; B:ToggleUpgradeOnOff(CARGO)
assert(speed()==700 and T1.max_shared_storage==84000, 'toggle off')
local off=table.pack(speed())
assert(off.n==4 and off[2]==2100 and off[3]==nil and off[4]=='prior-wrapper')
B:ToggleUpgradeOnOff(CARGO)
-- Tech/law/cold are computed by the actual archived vanilla function.
research.FasterTrains=true; assert(speed()==1250, 'Faster Trains')
research.EvenFasterTrains=true; assert(speed()==1875, 'Vacuum Rail')
ActiveLaws.TrainSpeedStandards=law; assert(speed()==2494, 'law rounds after vanilla')
local warm=table.pack(speed(T1,el))
-- Cargo no longer warms trains: the bonus multiplies vanilla's actual cold result.
heat=0; assert(speed()==831, 'cargo alone: cold penalty retained')
assert(GetHeatAt==real_heat, 'cargo leaves heat unchanged')
research.SafeTransport=true; assert(speed()==1663, 'cargo alone: safe cold penalty retained')
local cold=table.pack(speed(T1,el))
assert(cold.n==4 and cold[1]==1663 and cold[2]==4988 and cold[3]==nil and cold[4]=='prior-wrapper' and last_element==el, 'cold returns chained')
SelectedObj=B; B:ToggleUpgradeOnOff(CARGO)
assert(speed()==1330, 'upgrade off: vanilla safe cold')
research.SafeTransport=nil; assert(speed()==665, 'upgrade off: vanilla cold')
heat=100; assert(speed()==1995, 'upgrade off: vanilla warm')
B:ToggleUpgradeOnOff(CARGO); heat=0; research={}; ActiveLaws={}
assert(speed()==291, 'cargo alone: cold penalty without tech')
heat=100
local tech=LabelModifier:new{container=city,label='Train',prop='max_shared_storage',percent=50,amount=0}
tech:TurnOn()
assert(T1.max_shared_storage==147000, 'fixture +50% tech adds to both upgrades')
-- Salvage disables both boosts immediately; ruins hold cargo, A still owns capacity.
B.destroyed=true; OnMsg.BuildingDemolished(B)
assert(T1.max_shared_storage==105000 and speed()==700, 'salvage stops cargo and speed')
B:ApplyUpgradeModifiersForUpgrade(CARGO)
assert(speed()==700 and T1.max_shared_storage==105000, 'ruins cannot reactivate')
A:ConstructUpgrade(CARGO)
assert(not Building.HasUpgrade(A,CARGO), 'ruins retain claim')
local wrong=hub(210,202000); wrong.map='underground'; wrong:ApplyCopyParams({})
assert(not Building.HasUpgrade(wrong,CARGO), 'rebuild map guard')
wrong.map='surface'; wrong=hub(211,202001); wrong:ApplyCopyParams({})
assert(not Building.HasUpgrade(wrong,CARGO), 'rebuild position guard')
local R=hub(203,202000); R:ApplyCopyParams({})
assert(Building.HasUpgrade(R,CARGO) and not Building.HasUpgrade(B,CARGO))
assert(T1.max_shared_storage==147000 and speed()==875, 'rebuild restores once')
R:ApplyCopyParams({}); assert(T1.max_shared_storage==147000, 'idempotent carry')
SelectedObj=R; R:ToggleUpgradeOnOff(CARGO)
R.destroyed=true; OnMsg.BuildingDemolished(R)
local R2=hub(204,202000); R2:ApplyCopyParams({})
assert(Building.HasUpgrade(R2,CARGO) and not R2:IsUpgradeOn(CARGO) and speed()==700, 'off state carried')
SelectedObj=R2; R2:ToggleUpgradeOnOff(CARGO)
OnMsg.LoadGame(); assert(speed()==875 and T1.max_shared_storage==147000, 'load no doubling')
R2.destroyed=true; OnMsg.BuildingDemolished(R2)
-- Simulate a pre-fix ruin with its modifier on, then run the real LoadGame fixup.
Building.ApplyUpgradeModifiersForUpgrade(R2,CARGO)
OnMsg.LoadGame()
assert(T1.max_shared_storage==105000 and speed()==700, 'ruins load fixup')
R2:StopUpgradeModifiers(); remove(city.labels.Station,R2); R2.deleted=true
A:ConstructUpgrade(CARGO)
assert(A:IsUpgradeBeingConstructed(CARGO), 'claim released after clearing')
A:ApplyUpgrade(2)
assert(Building.HasUpgrade(A,CARGO) and speed()==875 and T1.max_shared_storage==147000, 'clear and re-buy')
-- Both claims on one owner transfer independently; OFF cargo stays off.
SelectedObj=A; A:ToggleUpgradeOnOff(CARGO)
A.destroyed=true; OnMsg.BuildingDemolished(A)
local both=hub(220,201000); both:ApplyCopyParams({})
assert(Building.HasUpgrade(both,ID) and Building.HasUpgrade(both,CARGO), 'both upgrades carry')
assert(both:IsUpgradeOn(ID) and not both:IsUpgradeOn(CARGO) and speed()==700)
'''.replace('TEMPLATE', template)


def run(code, extra_cases='', heater_setup='', heater_fixture=''):
    # Reuse the existing fixture without executing its first-upgrade scenario.
    env = {'__file__': str(HERE / 'capacity_smoke.py'), 'SPEED_SETUP': SPEED_SETUP + heater_setup}
    script = prefix.replace('code = SOURCE.read_text(encoding="utf8")', 'code = supplied_code')
    script = script.replace('lua.execute(section)', '''lua.execute(SPEED_SETUP)
speed_source = (ARCHIVE / 'Units/Train.lua').read_text(encoding='utf8')
lua.execute(extract(speed_source, 'Train:GetNominalMoveSpeed'))
lua.execute("local original=Train.GetNominalMoveSpeed; Train.GetNominalMoveSpeed=function(...) last_element=select(2,...); local a,b=original(...); return a,b,nil,'prior-wrapper' end")
lua.execute('local Floor = SMROptInTrainFloor\\n' + section)''')
    env['supplied_code'] = code
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(script, str(HERE / 'capacity_smoke.py'), 'exec'), env)
    env['lua'].execute(fixture + heater_fixture + CASES + extra_cases)


def main():
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]))
    print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
    code = SOURCE.read_text(encoding='utf8')
    print('source_sha256:', hashlib.sha256(SOURCE.read_bytes()).hexdigest())
    print('template_source_sha256:', hashlib.sha256(DATA.read_bytes()).hexdigest())
    run(code)
    print('PASS cargo: additive 126000; with +50% cargo tech 147000; passengers/stations unchanged by cargo')
    print('PASS independent claims, construction/cancel, spent click, toggle, power, salvage/rebuild, load, clear/re-buy')
    print('PASS chained speed and animation, extra returns, tech/law, foreign city')
    print('PASS cargo alone: vanilla cold penalty retained with and without Safe Transport and tech')
    mutations = {
        'speed multiplier': ('MulDivRound(result[1], 125, 100)', 'MulDivRound(result[1], 100, 100)'),
        'animation multiplier': ('MulDivRound(result[2], 125, 100)', 'MulDivRound(result[2], 100, 100)'),
        'cargo must not warm': ('power_warm_on(self)', 'cargo_speed_on(self)'),
        'salvage cargo': ('hub:StopUpgradeModifiersForUpgrade(id)', 'if id ~= hub_cargo_upgrade then hub:StopUpgradeModifiersForUpgrade(id) end'),
        'cargo ownership': ('local function network_upgrade(id) return id == hub_capacity_upgrade or id == hub_cargo_upgrade end', 'local function network_upgrade(id) return id == hub_capacity_upgrade end'),
        'rebuild cargo': ('do carry_upgrade(self, id) end', 'do if id ~= hub_cargo_upgrade then carry_upgrade(self, id) end end'),
        'off state carry': ('if not on then Building.ToggleUpgradeOnOff(self, id) end', '-- lost off state'),
    }
    for name, (before, after) in mutations.items():
        assert before in code, name
        try:
            run(code.replace(before, after, 1))
        except LuaError as exc:
            assert 'assertion failed' in str(exc) or any(s in str(exc) for s in [
                'one cargo modifier', 'salvage stops', 'cargo construction claim', 'off state carried',
                'cold penalty']), str(exc)
            print('PASS mutation rejected:', name)
        else:
            raise AssertionError('mutation survived: ' + name)
    print('Generated upgrade slots 2/3 and base power match source' if generated_current else
          'OWNER STEP OWED: Mod Editor save for Cargo description, Power slot 3 and base power; code_hash remains editor-owned')


if __name__ == '__main__':
    main()
