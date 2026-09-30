"""Exercise the real depot Lua guard alongside the existing hub guard, outside the game.
python docs/agent/reports/elevator_depot_import_20260930/guard_smoke.py
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

from lupa import LuaRuntime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DEPOT = ROOT / 'tools/devmods/elevator_station/Code/10_ElevatorDepotDev.lua'
HUB = ROOT / 'tools/devmods/train_hub/Code/20_TrainHub.lua'
hub_guard = re.search(r'local function install_hub_art_spec_guard\(\)\n.*?\nend\n',
                      HUB.read_text(encoding='utf-8'), re.S).group(0)
checks = []
for order in ('depot_first', 'hub_first'):
    lua = LuaRuntime()
    lua.execute('''
        OnMsg = {}
        DefineClass = setmetatable({}, {__newindex=function(t,k,v) rawset(t,k,v); _G[k]=v end})
        point = function(...) return {...} end
        calls = 0
        g_Classes = {EntitySpec={OnPresetPostLoad=function(self, value)
            calls = calls + 1
            return self.id, value
        end}}
        Floor = {}
    ''')
    lua.execute(DEPOT.read_text(encoding='utf-8'))
    lua.execute(hub_guard + '\nInstallHub = install_hub_art_spec_guard')
    lua.execute('''
        Check = function(id, expected_calls)
            local before = calls
            local got_id, got_value = g_Classes.EntitySpec.OnPresetPostLoad({id=id}, "argument")
            assert(calls - before == expected_calls)
            if expected_calls == 1 then assert(got_id == id and got_value == "argument") end
        end
    ''')
    if order == 'depot_first':
        lua.execute('OnMsg.ClassesPostprocess(); InstallHub()')
    else:
        lua.execute('InstallHub(); OnMsg.ClassesPostprocess()')
    lua.execute('''
        Check("SMROptInElevatorDepot", 0)
        Check("SMROptInTrainHub6", 0)
        Check("SMROptInTrainHub6Glass", 0)
        Check("SMROptInTrainHub6DomeGlass", 0)
        Check("UnrelatedEntity", 1)
        EntitySpecPathToEntity = function() end
        Check("SMROptInElevatorDepot", 1)
        Check("SMROptInTrainHub6", 1)
        Check("UnrelatedEntity", 1)
        OnMsg.ClassesPostprocess()
        local installed = g_Classes.EntitySpec.OnPresetPostLoad
        OnMsg.ClassesPostprocess()
        assert(installed == g_Classes.EntitySpec.OnPresetPostLoad)
        Check("SMROptInElevatorDepot", 1)
        EntitySpecPathToEntity = nil
        Check("SMROptInElevatorDepot", 0)
        Check("SMROptInTrainHub6", 0)
        Check("UnrelatedEntity", 1)
    ''')
    checks.append({'order': order, 'retail_own_and_hub_skip': 'PASS',
                   'foreign_delegation': 'PASS', 'editor_delegation_and_returns': 'PASS',
                   'reinstall_and_helper_transition': 'PASS'})
report = {
    'command': 'python docs/agent/reports/elevator_depot_import_20260930/guard_smoke.py',
    'optin_head': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
    'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (DEPOT, HUB, Path(__file__))},
    'checks': checks,
    'limit': 'Stubbed Lua callbacks; actual normal-game startup remains for the owner sitting.',
}
(HERE / 'guard_smoke.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(report))
