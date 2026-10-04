"""03A receipt: run the release gates on a dry launch assembly of HEAD and keep every output.

Run: python docs/archive/release_corrections_20261003/receipt.py <new-receipt.json>
Writes scratch/launch-proof (a dry assembly; no batch is opened) and the NEW receipt only.
"""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'CLAUDE.md').is_file())
PROOF = ROOT / 'scratch' / 'launch-proof'
sys.path.insert(0, str(ROOT / 'tools'))
import upload_preflight  # noqa: E402


def run(*cmd):
    p = subprocess.run([sys.executable, *cmd], cwd=ROOT, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return {'command': 'python ' + ' '.join(cmd), 'exit': p.returncode,
            'stdout': p.stdout, 'stderr': p.stderr}


r = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
     'status_short': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
     'runs': {}}
runs = r['runs']
runs['selftest'] = run('tools/release_selftest.py')
runs['batch_status'] = run('tools/release_batch.py', 'status')
runs['assemble'] = run('tools/release_batch.py', 'assemble', '--out', str(PROOF))
runs['preflight_launch'] = run('tools/upload_preflight.py', str(PROOF))
runs['predict_launch'] = run('tools/pack_predict.py', str(PROOF), '--json')
runs['predict_repo'] = run('tools/pack_predict.py', '.', '--json')
runs['parity_launch'] = run('tools/store_parity.py', '--metadata', str(PROOF / 'metadata.lua'))
runs['parity_confirm_live_prepublication'] = run('tools/store_parity.py', '--confirm-live')
runs['counts'] = run('tools/doccheck.py', '--emit-counts')

# Membership, each list read from the launch tree by its own filter.
md = upload_preflight.parse_metadata(str(PROOF / 'metadata.lua'))
meta_text = (PROOF / 'metadata.lua').read_text(encoding='utf-8')
items_text = (PROOF / 'items.lua').read_text(encoding='utf-8')
block = re.search(r"'default_options',\s*\{(.*?)\n\t\},", meta_text, re.S)
packed = json.loads(runs['predict_launch']['stdout'])['packed']
repo_packed = json.loads(runs['predict_repo']['stdout'])['packed']
modules = sorted(p.name[4:-4] for p in (PROOF / 'Code').glob('Opt_*.lua')
                 if 'SMROptInPack.Register(' in p.read_text(encoding='utf-8'))
r['membership'] = {
    'registered_modules': {'filter': 'Code/Opt_*.lua containing SMROptInPack.Register(', 'members': modules},
    'default_options': {'filter': "metadata.lua 'default_options' keys",
                        'members': re.findall(r"^\t\t(\w+) = ", block.group(1), re.M) if block else None},
    'option_items': {'filter': "items.lua PlaceObj('ModItemOption*') names",
                     'members': re.findall(r"PlaceObj\('ModItemOption\w+',\s*\{\s*'name',\s*\"([^\"]+)\"", items_text)},
    'code_list': {'filter': "metadata.lua 'code'", 'members': md.get('code')},
    'packed_code': {'filter': 'predicted pack, Code/', 'members': [p for p in packed if p.startswith('Code/')]},
    'packed_data': {'filter': 'predicted pack, Data/', 'members': [p for p in packed if p.startswith('Data/')]},
    'generated': {'filter': 'predicted pack, *.generated.lua', 'members': [p for p in packed if p.endswith('.generated.lua')]},
    'ignore_files': {'filter': "metadata.lua 'ignore_files'", 'members': md.get('ignore_files')},
    'packed_total': len(packed),
    'launch_vs_repo_pack': {'only_in_repo_prediction': sorted(set(repo_packed) - set(packed)),
                            'only_in_launch_prediction': sorted(set(packed) - set(repo_packed))},
}
hits = []
for p in PROOF.rglob('*'):
    if p.is_file():
        if 'arboretum' in p.name.lower() or (p.suffix in ('.lua', '.entjson', '.mtljson', '')
                                             and b'Arboretum' in p.read_bytes()):
            hits.append(p.relative_to(PROOF).as_posix())
control = [p.relative_to(ROOT).as_posix() for p in (ROOT / 'staging').rglob('*.lua')
           if b'Arboretum' in p.read_bytes()]
r['held_token'] = {'token': 'Arboretum', 'launch_tree_hits': hits,
                   'presence_control': {'filter': 'staging/**/*.lua containing the token', 'members': control}}
assert sorted(md.get('code')) == sorted(r['membership']['packed_code']['members'])
assert not hits and control, (hits, control)

with Path(sys.argv[1]).open('x', encoding='utf-8', newline='\n') as dest:
    json.dump(r, dest, indent=1, ensure_ascii=False)
    dest.write('\n')
for name, res in runs.items():
    print('%-40s exit %d' % (name, res['exit']))
for key, val in r['membership'].items():
    if isinstance(val, dict) and 'members' in val:
        print('%-18s %d  %s' % (key, len(val['members']), val['filter']))
print('modules:', modules)
print('default_options:', r['membership']['default_options']['members'])
print('option_items:', r['membership']['option_items']['members'])
print('launch vs repo pack:', r['membership']['launch_vs_repo_pack'])
print('held token control:', len(control), 'file(s) in staging; launch hits', len(hits))
