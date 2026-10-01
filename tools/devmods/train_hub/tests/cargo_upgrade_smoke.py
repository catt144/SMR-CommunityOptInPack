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
fields = dict(re.findall(r"^\t'(upgrade[1234]_\w+|electricity_production|max_storage_per_resource)', (.*),$", DATA.read_text(encoding='utf8'), re.M))
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
    'max_storage_per_resource': '1000000',
    'upgrade4_id': '"SMROptInTrainHub6_StorageHub"',
    'upgrade4_upgrade_cost_Metals': '60000',
    'upgrade4_upgrade_cost_MachineParts': '30000',
}
for key, value in expected.items():
    assert fields.get(key) == value, (key, fields.get(key), value)
assert not any('mod_prop_id' in k and k.startswith(('upgrade2_', 'upgrade3_')) and k not in ('upgrade2_mod_prop_id_1', 'upgrade3_mod_prop_id_1') for k in fields)
assert not any('require' in k or 'unlock' in k for k in fields), 'no tech requirement'
generated = dict(re.findall(r'^\t(upgrade[1234]_\w+|electricity_production|max_storage_per_resource) = (.*),$',
    (HERE.parent / 'Code/BuildingTemplate/SMROptInTrainHub6.generated.lua').read_text(encoding='utf8'), re.M))
generated = defaults | generated
assert not any(word in fields['upgrade2_description'] for word in ('warm', 'heat', 'cold')), 'cargo has no cold protection'
assert '+75' in fields['upgrade3_description'] and 'Production' in fields['upgrade3_description']
# Power glyph: vanilla's inline tag, never U+26A1 (the UI font lacks it; sitting A, 2026-10-01).
# <icon_Power> is registered from the Power resource's text_icon (archived 1.1.1.406343
# Lua/Resources.lua:527-531, Data/Resource.lua:395-398) and written inline after the number
# (Lua/Buildings/Dome.lua:2177-2179).
assert '+75<icon_Power> Production per hub;' in fields['upgrade3_description'], fields['upgrade3_description']
assert '+19<icon_Power> Consumption per hub.' in fields['upgrade4_description'], fields['upgrade4_description']
assert all(ord(c) < 128 for t in range(1, 5) for c in fields[f'upgrade{t}_description']), 'a glyph the UI font may lack'
for tier in range(1,5):
    desc=fields[f'upgrade{tier}_description']
    assert 'Colony upgrade: any hub can switch it.' in desc, (tier, desc)
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
 h:InitHubCapacityUpgrade()
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
assert(A:HasUpgrade(CARGO) and A:CanDisableUpgrade(CARGO), 'other hub can switch')
B.working=false; assert(speed()==875, 'vanilla power behavior')
-- Every prior return is retained; both speed outputs scale, extra nil/value survive.
local el={}
local r=table.pack(speed(T1,el))
assert(r.n==4 and r[1]==875 and r[2]==2625 and r[3]==nil and r[4]=='prior-wrapper')
assert(last_element==el, 'element argument chained')
local foreign={city={labels={Station={}}}}
assert(speed(foreign)==700, 'foreign city delegates unchanged')
SelectedObj=A; A:ToggleUpgradeOnOff(CARGO)
assert(not A:IsUpgradeOn(CARGO) and not B:IsUpgradeOn(CARGO), 'global off display')
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
local tech=LabelModifier:new{container=city,label='Train',id='fixture-tech',prop='max_shared_storage',percent=50,amount=0}
tech:TurnOn()
assert(T1.max_shared_storage==147000, 'fixture +50% tech adds to both upgrades')
-- Salvage changes neither purchase nor effects; any survivor can switch.
B.destroyed=true; OnMsg.BuildingDemolished(B)
assert(T1.max_shared_storage==147000 and speed()==875,'cargo survives buyer salvage')
B:StopUpgradeModifiers(); remove(city.labels.Station,B); B.deleted=true
assert(T1.max_shared_storage==147000 and speed()==875,'cargo survives buyer clear')
A:ToggleUpgradeOnOff(CARGO)
assert(T1.max_shared_storage==105000 and speed()==700 and not A:IsUpgradeOn(CARGO),'receiver turns global cargo off')
local both=hub(220)
assert(both:HasUpgrade(ID) and both:HasUpgrade(CARGO) and both:CanDisableUpgrade(CARGO),'future hub inherits purchase and switch')
assert(both:IsUpgradeOn(ID) and not both:IsUpgradeOn(CARGO) and speed()==700,'future hub mirrors off')
OnMsg.LoadGame(); assert(T1.max_shared_storage==105000 and speed()==700,'load preserves independent off')
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
    print('PASS independent claims, construction/cancel, shared display/toggle, salvage/clear persistence, future hubs, load')
    print('PASS chained speed and animation, extra returns, tech/law, foreign city')
    print('PASS cargo alone: vanilla cold penalty retained with and without Safe Transport and tech')
    mutations = {
        'speed multiplier': ('MulDivRound(result[1], 125, 100)', 'MulDivRound(result[1], 100, 100)'),
        'animation multiplier': ('MulDivRound(result[2], 125, 100)', 'MulDivRound(result[2], 100, 100)'),
        'cargo must not warm': ('power_warm_on(self)', 'cargo_speed_on(self)'),
        'receiver switch': ('entry.on = not entry.on', 'if not SelectedObj or self == SelectedObj then return end'),
        'cargo ownership': ('local function network_upgrade(id) return id == hub_capacity_upgrade or id == hub_cargo_upgrade or id == hub_power_upgrade or id == hub_storage_upgrade end', 'local function network_upgrade(id) return id == hub_capacity_upgrade end'),
        'global display': ('return colony_upgrade_on(self.city.colony, id)', 'return false'),
        'cargo salvage': ('if IsKindOf(bld, "SMROptInTrainHubBase") then sync_colony_upgrades(bld.city and bld.city.colony) end', 'if IsKindOf(bld, "SMROptInTrainHubBase") then bld.city.colony.SMROptIn_hub_upgrades[hub_cargo_upgrade].on = false; sync_colony_upgrades(bld.city.colony) end'),
    }
    for name, (before, after) in mutations.items():
        assert before in code, name
        try:
            run(code.replace(before, after, 1))
        except LuaError as exc:
            assert 'assertion failed' in str(exc) or any(s in str(exc) for s in [
                'one cargo modifier', 'cargo survives', 'cargo construction claim', 'global off display', 'receiver',
                'cold penalty', 'future hub']), str(exc)
            print('PASS mutation rejected:', name)
        else:
            raise AssertionError('mutation survived: ' + name)
    print('Generated upgrade slots 1/2/3/4, base storage and power match source' if generated_current else
          'OWNER STEP OWED: Mod Editor save for slot 4 and base storage; code_hash remains editor-owned')


if __name__ == '__main__':
    main()
