"""01A read-only evidence: replay the archived envelope decoder on exact B.

Run from the Opt-In repo root. Output goes to scratch; no native graph decoding.
The archived decoder is unmodified. Its SOURCE/OUT assignments alone are rebound
in memory, so a current campaign SMRTK_B is never accidentally selected.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path.cwd()
OUT = ROOT / 'scratch/ship_residual_20261003'
OLD = ROOT / 'docs/archive/ship_evidence_20261003'
ARCHIVE = Path('B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src')
SOURCE = ROOT / 'local/ship-evidence-20261003/SMRTK_B.sav'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def command(args, expected=(0,)):
    run = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
    assert run.returncode in expected, (args, run.returncode, run.stderr)
    return {'command': subprocess.list2cmdline(args), 'exit': run.returncode,
            'stdout': run.stdout, 'stderr': run.stderr}


old = json.loads((OLD / 'save_receipt.json').read_text())
assert sha(SOURCE.read_bytes()) == old['save_sha256'], 'wrong exact-B fixture'
decoder = OLD / 'save_decode.py'
tree = ast.parse(decoder.read_text(encoding='utf-8'))
replaced = []
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id in ('SOURCE', 'OUT'):
            value = SOURCE if target.id == 'SOURCE' else OUT / 'decoded'
            node.value = ast.Call(func=ast.Name(id='Path', ctx=ast.Load()),
                                  args=[ast.Constant(str(value))], keywords=[])
            replaced.append(target.id)
assert sorted(replaced) == ['OUT', 'SOURCE']
exec(compile(ast.fix_missing_locations(tree), str(decoder), 'exec'), {})
persist_path = OUT / 'decoded/persist'
persist = persist_path.read_bytes()
assert sha(persist) == old['persist_sha256'], 'different persist member'
assert len(persist) == old['persist_bytes']
assert persist.startswith(b'SPCONRT'), 'unexpected native format'
tokens = {}
for token, want in old['members_offsets'].items():
    members = [m.start() for m in re.finditer(re.escape(token.encode()), persist)]
    assert members == want, (token, members, want)
    tokens[token] = {'count': len(members), 'offsets': members}

meta = (OUT / 'decoded/metadata.lua').read_text(encoding='utf-8')
identity_patterns = {
    'GameTime': r'GameTime\s*=\s*35790404\b',
    'session': re.escape(old['identity']['smrtk_session']),
    'last_id': r'id\s*=\s*"2383"',
    'savename': r'savename\s*=\s*"SMRTK_B.sav"',
}
for key, pattern in identity_patterns.items():
    assert re.search(pattern, meta), ('identity mismatch', key)

source_receipt = json.loads((OLD / 'source_receipt.json').read_text())
known = {x['path']: x for x in source_receipt['packs']['Lua.fpk']['members']}
paths = [
    'CommonLua/Core/persist.lua', 'CommonLua/Core/map.lua',
    'CommonLua/Savegame.lua', 'CommonLua/Modding/Mod.lua',
    'Lua/Modifiers.lua', 'Lua/LabelContainer.lua', 'Lua/Buildings/Building.lua',
]
sources = {}
for name in paths:
    data = (ARCHIVE / name).read_bytes()
    assert sha(data) == known[name]['sha256'], ('source drift', name)
    sources[name] = {'sha256': sha(data), 'bytes': len(data)}

searches = [
    command(['rg', '-a', '-n', '-o',
             'SMROptIn_hub_upgrades|SMROptInTrainHub6Base:SMROptInTrainHub6|'
             'SMROptInElevatorDepotDevBase:SMROptInElevatorDepotDev|SMROptIn_station_rows',
             str(persist_path)]),
    command(['rg', '-n', 'SPCONRT|EngineLoadGame|GetLuaLoadGamePermanents',
             'tools', '../SMR-BugFixPack/tools', '../SMR-BugFixPack-TestKit/Code',
             '-g', '*.py', '-g', '*.lua'], expected=(1,)),
    command(['rg', '-n', 'EngineLoadGame|GetLuaLoadGamePermanents|PersistGatherPermanents = true|'
             'PersistLoad = true|PersistSave = true',
             str(ARCHIVE / 'CommonLua/Savegame.lua'),
             str(ARCHIVE / 'CommonLua/Modding/Mod.lua'),
             str(ARCHIVE / 'CommonLua/Core/persist.lua')]),
]
# Candidate text only: native interned strings carry no owner/recipient edges.
ids = {}
for token in sorted(set(re.findall(rb'\d+_upgrade\d+_mod_\d+', persist))):
    offsets = [m.start() for m in re.finditer(re.escape(token), persist)]
    ids[token.decode()] = {'count': len(offsets), 'offsets': offsets}

assert sha(SOURCE.read_bytes()) == old['save_sha256'], 'fixture changed during read'
receipt = {
    'command': 'python docs/archive/ship_residual_20261003/read_residual.py',
    'head': command(['git', 'rev-parse', 'HEAD'])['stdout'].strip(),
    'status': command(['git', 'status', '--short']),
    'build': '1.1.1.406343', 'steam_build': '25579348',
    'source': str(SOURCE), 'save_sha256': sha(SOURCE.read_bytes()),
    'persist_sha256': sha(persist), 'persist_bytes': len(persist),
    'identity': old['identity'], 'identity_patterns': identity_patterns,
    'decoder_sha256': sha(decoder.read_bytes()),
    'reader_sha256': sha(Path(__file__).read_bytes()),
    'tokens': tokens, 'candidate_modifier_id_tokens': ids,
    'candidate_modifier_id_count': len(ids),
    'candidate_modifier_id_occurrences': sum(x['count'] for x in ids.values()),
    'source_archive': str(ARCHIVE), 'source_members': sources,
    'module_members': {p: sha((ROOT / p).read_bytes()) for p in (
        'Code/TrainHub_20_TrainHub.lua', 'Code/BuildingTemplate/SMROptInTrainHub6.generated.lua')},
    'kit_head': command(['git', '-C', '../SMR-BugFixPack-TestKit', 'rev-parse', 'HEAD'])['stdout'].strip(),
    'kit_status': command(['git', '-C', '../SMR-BugFixPack-TestKit', 'status', '--short']),
    'searches': searches,
    'limit': 'Envelope and token evidence only. No native graph edges decoded; '
             'candidate modifier strings are NOT registrations or effects. '
             'Reader search is confined to the named tool/kit trees, not proof that no decoder exists elsewhere.',
}
(OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print('Receipt:', OUT / 'receipt.json')
print('Exact fixture, decoded hash, token offsets, identity, archived sources: verified.')
