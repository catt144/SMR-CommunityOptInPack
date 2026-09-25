"""Read-only L6 evidence checks. Run from the Opt-In repository root."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from lupa import LuaRuntime

ROOT = Path.cwd()
def git(*args, root=ROOT):
    return subprocess.check_output(['git', '-C', str(root), *args]).decode('utf-8')
def blob(rev, path):
    return git('show', f'{rev}:{path}')
flight = 'tools/devmods/train_hub/Code/30_TrainHubDrones.lua'
hub = 'tools/devmods/train_hub/Code/20_TrainHub.lua'
code = (ROOT / hub).read_text(encoding='utf-8')
head = git('rev-parse', 'HEAD').strip()
out = {'command': 'python ' + sys.argv[0], 'head': head,
       'hub_sha256': hashlib.sha256((ROOT / hub).read_bytes()).hexdigest()}

# Execute the exact source function, with explicit live/released/dead controls.
body = code[code.index('local function rising_count(self)'):code.index('local loaded_pending = false')]
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('rising = {}; function IsValid(o) return o and o.valid end')
lua.execute(body + '\ncount_rising = rising_count')
out['rising_reproduction'] = json.loads(lua.execute('''
local a, b = {}, {}
local ra = {hub=a, drone={valid=true}}
local rb = {hub=b, drone={valid=true}}
local dead = {hub=a, drone={valid=false}}
local released = {hub=a, drone={valid=true}, released=true}
rising[ra], rising[dead], rising[released] = true, true, true
assert(count_rising(a) == 1 and rising[ra] and not rising[dead] and not rising[released])
rising[rb] = true
local before = rising[rb] and true or false
assert(count_rising(a) == 1)
local after = rising[rb] and true or false
local b_count = count_rising(b)
assert(before and not after and b_count == 0, "current cross-hub deletion no longer reproduces")
return '{"same_hub_live_control":"PASS","dead_and_released_cleanup":"PASS",' ..
 '"other_hub_live_entry_before":true,"other_hub_live_entry_after":false,"other_hub_count":' .. b_count .. '}'
'''))
# Diagnostic counterfactual in memory only: distinguish owner mismatch from stale entry.
fixed = body.replace('if record.hub == self and not record.released and IsValid(record.drone) then n = n + 1 else rising[record] = nil end',
 'if record.released or not IsValid(record.drone) then rising[record] = nil elseif record.hub == self then n = n + 1 end')
assert fixed != body
lua.execute(fixed + '\ncount_rising = rising_count')
lua.execute('local a,b={},{}; local ra={hub=a,drone={valid=true}}; local rb={hub=b,drone={valid=true}}; rising={ [ra]=true,[rb]=true }; assert(count_rising(a)==1 and rising[rb] and count_rising(b)==1 and rising[ra])')
out['rising_reproduction']['memory_only_counterfactual'] = 'PASS; no production edit'

# Verify handoffs in the same commits that delete their link, not just today's narrative.
folder = 'docs/agent/prompts/Train_Hub_Project/03_Drones/'
deletions = git('log', '--diff-filter=D', '--format=COMMIT %H', '--name-only', '--', folder)
commits = []
for chunk in deletions.split('COMMIT ')[1:]:
    lines = chunk.splitlines(); sha=lines[0]
    paths=[x for x in lines[1:] if x.endswith('.md')]
    changed=git('diff-tree','--no-commit-id','--name-status','-r',sha)
    commits.append({'commit':sha, 'deleted':paths, 'changes':changed.splitlines()})
out['link_deletion_commits'] = commits
out['folder_members'] = sorted(p.name for p in (ROOT/folder).iterdir())
out['tag_commit'] = git('rev-parse','drones-scripted-flight-20260923^{}').strip()
assert blob('drones-scripted-flight-20260923',flight) == blob('b84f106',flight)
samples = {
 'L2_no_command_thread': ('0edc0c9',flight,['init_with_command = false','CreateRealTimeThread','function F.Route']),
 'L2R_underdeck': ('0ad2e3d',flight,['UnderDeckHeight = 300','PitExitZ = 1000','OutwardDistance = 9000']),
 'L2M_interpolation': ('74b1e4a',flight,['SetPos','SetRollPitchYaw','CreateRealTimeThread']),
 'L2M2_game_driver_and_numeric_gate': ('b84f106',flight,['CreateGameTimeThread','local function div(a, b) return (a * 1.0) / b end','SetAcceleration']),
 'L2E_stock_commands': ('9a540dd',flight,['"FlightGoto", "WaitUninterruptable"','QueueCommand(STOCK_HOLD','function F.Persists']),
 'L4_shape_and_cost': ('b556035',hub,['local TRACK_WORK = "SMROptIn_track_work"','kind = "repair"','return researched and 100 or 50','req:AssignUnit(amount)','entry.req:UnassignUnit(entry.amount, false)','self:AddResource(-amount, res)','leader:Complete()']),
 'L5_actual_door_fix': ('ad5113b',flight,['CObject.HasSpot(hub, "Trackconnector"','ExitVia = "door"']),
}
out['historical_samples']={}
for name,(rev,path,needles) in samples.items():
    text=blob(rev,path)
    found={n:[i+1 for i,s in enumerate(text.splitlines()) if n in s] for n in needles}
    assert all(found.values()), (name,found)
    out['historical_samples'][name]={'revision':rev,'path':path,'matches':found}

# Decoded text inputs; count positive controls alongside the forbidden-token scan.
lua_paths=sorted((ROOT/'tools/devmods/train_hub').rglob('*.lua'))
out['dev_lua_scan']={'filter':'tools/devmods/train_hub/**/*.lua, decoded UTF-8',
 'members':[str(p.relative_to(ROOT)).replace('\\','/') for p in lua_paths],
 'forbidden_hits':[], 'own_namespace_lines':0}
for p in lua_paths:
    for i,s in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1):
        if 'SMRFixPack' in s: out['dev_lua_scan']['forbidden_hits'].append([str(p),i,s])
        if 'SMROptIn' in s: out['dev_lua_scan']['own_namespace_lines']+=1
assert not out['dev_lua_scan']['forbidden_hits'] and out['dev_lua_scan']['own_namespace_lines']>0
out['dev_lua_scan']['file_total']=len(lua_paths)
out['dev_lua_scan']['compressed_inputs']=[str(p) for p in (ROOT/'tools/devmods/train_hub').rglob('*') if p.suffix.lower() in ('.gz','.zip','.fpk','.hpk')]
assert not out['dev_lua_scan']['compressed_inputs']

# Search complete tracked name inventories in both repositories, then historical archive names.
named=['20260923-16.09.06','20260924-17.07.20','20260924-17.18.02','20260924-21.01.51','20260924-21.44.09','20260925-13.34.56','20260925-13.43.07','20260925-14.14.01','20260924-12.35.05']
out['log_archive_search']={}
for root in [ROOT,ROOT.parent/'SMR-BugFixPack']:
    names=git('ls-files',root=root).splitlines()
    historical=git('log','--all','--format=','--name-only','--','docs/archive',root=root).splitlines()
    out['log_archive_search'][root.name]={token:{'current':[n for n in names if token in n], 'historical':sorted({n for n in historical if token in n})} for token in named}
out['log_archive_search']['filter']='tracked names and all-ref archive-history names; reports are not log evidence; compressed-name candidates listed separately'
out['archive_compressed_candidates']={str(root):[n for n in git('ls-files','docs/archive',root=root).splitlines() if Path(n).suffix.lower() in ('.zip','.gz','.7z','.zst','.hpk','.fpk')] for root in [ROOT,ROOT.parent/'SMR-BugFixPack']}
out['historical_receipts']={}
for rev,name in [('0ad2e3d','exit_clearance_receipt.json'),('74b1e4a','motion_clearance_receipt.json'),('b84f106','motion_clearance_receipt.json'),('HEAD','motion_clearance_receipt.json')]:
    data=json.loads(blob(rev,'tools/devmods/train_hub/tests/'+name))
    assert data['triangle_total']==sum(data['object_triangles'].values())
    assert data['leg_count']==len(data['legs'])
    source=subprocess.check_output(['git','show',rev+':'+flight])
    assert data['source_sha256']==hashlib.sha256(source).hexdigest()
    out['historical_receipts'][rev]={'command':data['command'],'measurement_head':data['head'],'leg_total':len(data['legs']),'triangle_total':sum(data['object_triangles'].values()),'source_hash_matches':True,'mode':data.get('mode','historical scripted')}
scan=subprocess.run(['rg','-n','SMRFixPack','tools/devmods/train_hub','-g','*.lua'],capture_output=True,text=True)
assert scan.returncode==1 and not scan.stdout and not scan.stderr
out['dev_lua_scan']['grep_command']='rg -n SMRFixPack tools/devmods/train_hub -g *.lua'
out['recovered_log_checks']={}
for p in sorted((ROOT/'docs/archive/drones_l6_20260925').glob('*.log')):
    lines=p.read_text(encoding='utf-8-sig',errors='replace').splitlines()
    patterns={'invalid_spot_events':r'^\[LUA ERROR\] HGE::l_GetSpotBeginIndex: Invalid spot',
      'persist_errors':r'Persist error:|Attempt to persist|luaSPersist|Unpersisted function|Unpersist missing permanent|Savegame error:|LoadGame error:',
      'repairs_done':r'^\[TrainHubDev\] repair done:', 'save_load':r'^\[SMRTK\] SMRTK_(SAVE|LOAD) ',
      'load_completed':r'^Game loaded on map', 'shutdown':r'Stopping the game threads from the Lua side with exit code 0'}
    hits={key:[{'line':i,'text':s} for i,s in enumerate(lines,1) if re.search(pat,s)] for key,pat in patterns.items()}
    out['recovered_log_checks'][p.name]={'members':hits,'counts':{key:len(v) for key,v in hits.items()}}
    assert hits['shutdown']
out['recovered_log_filter']=patterns
out['prior_brief_bytes']=len(subprocess.check_output(['git','show','cc3d6f1:'+folder+'6_QA_high.md']))
print(json.dumps(out,indent=2))
