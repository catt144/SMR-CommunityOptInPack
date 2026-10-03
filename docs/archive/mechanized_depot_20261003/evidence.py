import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path('B:/Dev/SMR/SMR-OptInPack')
DONOR = Path('B:/Dev/SMR/SMR-BugFixPack')
ARCHIVE = Path('B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343')
SRC = ARCHIVE / 'Src'
LIVE = Path('A:/SteamLibrary/steamapps/common/Project Spark/ModTools/Src')

def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest = dict((line[66:].replace('\\', '/'), line[:64]) for line in
                (ARCHIVE / 'MANIFEST.sha256').read_text(encoding='utf-8-sig').splitlines())
names = ['Lua/Buildings/StorageDepot.lua', 'Lua/Buildings/ResourceStockpile.lua',
         'Lua/Buildings/StockpileController.lua', 'Lua/LRManager.lua',
         'Lua/Buildings/ShuttleHub.lua', 'Lua/_TaskRequest.lua', 'Lua/Units/Drone.lua']
templates = sorted(SRC.glob('Lua/BuildingTemplate/MechanizedDepot*.generated.lua'))
names += [p.relative_to(SRC).as_posix() for p in templates]
hashes = {}
for name in names:
    digest = sha(SRC / name)
    hashes[name] = {'sha256': digest, 'manifest': manifest.get(name) == digest,
                    'live_src': sha(LIVE / name) == digest}
    assert hashes[name]['manifest'] and hashes[name]['live_src'], name

patterns = {
    'Store': r'MechanizedDepot\.Store|:Store\(',
    'SetCount': r'[:.]SetCount\(',
    'UpdateStockpileAmounts': r'[:.]UpdateStockpileAmounts\(',
    'GetMax': r'[:.]GetMax\(',
    'five_unit_accounting': r'store_step|carrying.*ResourceScale',
}
callers = {key: [] for key in patterns}
source_files = sorted(SRC.rglob('*.lua'))
for path in source_files:
    for n, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        for key, pattern in patterns.items():
            if re.search(pattern, line) and (key != 'five_unit_accounting' or
                    path.name == 'StorageDepot.lua'):
                callers[key].append({'file': path.relative_to(SRC).as_posix(),
                                     'line': n, 'text': line.strip()})

families = []
for path in templates:
    body = path.read_text(encoding='utf-8-sig')
    name = re.search(r'DefineClass\.(\w+)', body).group(1)
    parent = re.search(r'__parents\s*=\s*\{([^}]+)\}', body).group(1).strip()
    capacity = re.search(r'max_storage_per_resource\s*=\s*(\d+)', body).group(1)
    families.append({'class': name, 'parent': parent, 'main_capacity_raw': int(capacity)})
assert all(r['parent'] in ('"MechanizedDepot"', '"MechanizedMysteryDepot"') for r in families)
assert 'DefineClass.MechanizedMysteryDepot' in (SRC / 'Lua/Buildings/StorageDepot.lua').read_text(encoding='utf-8-sig')
assert all(r['main_capacity_raw'] == 3950000 for r in families)

def census(root):
    files = sorted((root / 'Code').rglob('*.lua'))
    searched = [(p, p.read_text(encoding='utf-8-sig')) for p in files]
    pattern = r'MechanizedDepot|rfMechanizedStorage|StockpileController|ResourceStockpileBase|ResourceStockpileLR'
    hits = [{'file': p.relative_to(root).as_posix(), 'line': n, 'text': line.strip()}
            for p, body in searched for n, line in enumerate(body.splitlines(), 1)
            if re.search(pattern, line)]
    return {'filter': 'Code/**/*.lua, UTF-8 decoded; regex ' + pattern,
            'count': len(files), 'members': [p.relative_to(root).as_posix() for p in files],
            'hits': hits}

store = (SRC / 'Lua/Buildings/StorageDepot.lua').read_text(encoding='utf-8-sig')
resource = (SRC / 'Lua/Buildings/ResourceStockpile.lua').read_text(encoding='utf-8-sig')
assert 'new_count = Clamp(new_count, 0, self.max_x * self.max_y * self.max_z)' in resource
assert '__parents = { "Building", "StockpileController", "ResourceStockpileBase", "ElectricityConsumer" }' in store
assert len(callers['Store']) == 3, callers['Store']
assert len([r for r in callers['Store'] if 'CreateGameTimeThread' in r['text']]) == 2
scale = 1000
boosts = [{'multiplier': m, 'pad_units': 5*2*5*m, 'batch_ceiling_units': 5*m,
           'total_capacity_units': 3950000//scale + 5*2*5*m,
           'visual_slots': 5*2*5} for m in (1, 2, 5, 10)]
facts = sorted((DONOR / 'docs/agent/facts').glob('EF-*.md'))
ids = [int(p.stem[3:]) for p in facts]
assert ids == list(range(1, max(ids)+1))

result = {'command': 'python ' + ' '.join(sys.argv),
          'date': '2026-10-03', 'game': '1.1.1.406343', 'steam_build': '25579348',
          'optin_head': git(ROOT, 'rev-parse', 'HEAD'),
          'fixpack_head': git(DONOR, 'rev-parse', 'HEAD'),
          'manifest_sha256': sha(ARCHIVE / 'MANIFEST.sha256'),
          'source_filter': 'archived Src/**/*.lua, decoded UTF-8 including DLC and CommonLua',
          'source_file_count': len(source_files),
          'source_file_members': [p.relative_to(SRC).as_posix() for p in source_files],
          'hashes': hashes,
          'call_patterns': patterns, 'callers': callers, 'families': families,
          'optin_census': census(ROOT), 'fixpack_census': census(DONOR),
          'derived_boost_table': boosts, 'allocated_fact': f'EF-{max(ids)+1:03}',
          'fact_ids_before': ids}
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'scratch/mechanized_evidence.json'
out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: result[k] for k in ['command', 'game', 'steam_build', 'optin_head',
      'fixpack_head', 'manifest_sha256', 'source_file_count', 'families',
      'derived_boost_table', 'allocated_fact']}, indent=2))
for key in ['optin_census', 'fixpack_census']:
    print(key, result[key]['count'], 'files;', len(result[key]['hits']), 'hits;',
          result[key]['filter'])
print('Matched source files:', len(hashes), '=', len(names), '; all archived/manifest/live hashes agree')
print('Store rows:', len(callers['Store']), '= two native thread starts + one declaration')
