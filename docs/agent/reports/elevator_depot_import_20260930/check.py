"""Read-only import and source audit on the owner-authorized hotfix build.
python docs/agent/reports/elevator_depot_import_20260930/check.py
"""
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MOD = ROOT / 'tools/devmods/elevator_station'
ASSETS = ROOT.parent / 'SMR-Assets'
EXPORT = ASSETS / 'elevatorstation/blender/export'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
head = lambda p: subprocess.check_output(['git', '-C', str(p), 'rev-parse', 'HEAD'], text=True).strip()
proof = json.loads((EXPORT / 'depot_proof.json').read_text(encoding='utf-8'))
entity_path = MOD / 'Entities/SMROptInElevatorDepot.entjson'
entity = json.loads(entity_path.read_text(encoding='utf-8'))['$value']
assert entity['strName'] == 'SMROptInElevatorDepot'
assert len(entity['meshDescriptions']) == 1
mesh = entity['meshDescriptions'][0]
assert len(mesh['lods']) == 1 and len(mesh['lods'][0]['meshes_data']) == 1
lod = mesh['lods'][0]
payload = lod['meshes_data'][0]
prefix = 'Mod/SMR_ElevatorStationDev_20260929/'
assert payload['mesh'] == prefix + 'Meshes/SMROptInElevatorDepot_mesh.sub_0.hgrm'
assert payload['material'] == prefix + 'Materials/SMROptInElevatorStation.mtljson'
compiled = MOD / payload['mesh'].removeprefix(prefix)
assert compiled.stat().st_size > 0
assert (MOD / payload['material'].removeprefix(prefix)).is_file()
assert sha(EXPORT / 'SMROptInElevatorDepot.fbx') == proof['entity']['fbx_sha256']
bbox_error = max(abs(got - want) for got_box, want_box in
                 zip((lod['boxMin'], lod['boxMax']), proof['entity']['game_bbox'])
                 for got, want in zip(got_box, want_box))
assert bbox_error < .01, bbox_error

expected = {s['name']: s for s in proof['spots']}
actual = {s['name']: s for s in mesh['attaches']}
assert len(actual) == len(mesh['attaches']) and actual.keys() == expected.keys()
rows = []
for name, want in sorted(expected.items()):
    got = actual[name]
    delta = math.dist(got['spotPos'], want['game_units'])
    angle = got.get('spotRotAngle', 0) * (-1 if got.get('spotRotAxis', [0, 0, 1])[2] < 0 else 1)
    angle_error = abs((angle - want['game_angle'] + 180) % 360 - 180)
    assert delta < .01 and angle_error < .01, (name, delta, angle_error)
    rows.append({'name': name, 'position': got['spotPos'], 'angle': angle,
                 'position_error': delta, 'angle_error': angle_error})
for a, b in (('Stop1', 'Spawn2'), ('Stop2', 'Spawn1')):
    assert math.dist(actual[a]['spotPos'], actual[b]['spotPos']) < .01

# Independently map each imported triangle's centroid to the nearest hex, not to the
# intended set; every triangle vertex must stay in that hex's inset envelope.
members = collections.Counter()
inset_radius = 900 / math.sqrt(3)
for surface in mesh['surfaces']:
    if surface['type'] != 'eHexShape':
        continue
    pts = surface['points']
    assert len(pts) == 3
    x, y = [sum(p[i] for p in pts) / 3 for i in (0, 1)]
    row = round(y / 866)
    nearby = [(c * 1000 + (500 if r % 2 else 0), r * 866)
              for r in range(row - 1, row + 2)
              for c in range(round(x / 1000) - 2, round(x / 1000) + 3)]
    centre = min(nearby, key=lambda p: math.dist(p, (x, y)))
    assert all(abs(p[2]) < .01 and math.dist(p[:2], centre) <= inset_radius + .01 for p in pts)
    members[centre] += 1
expected_cells = {(x, y) for x, y, cover in proof['footprint']['cells']}
assert set(members) == expected_cells
assert set(members.values()) == {4}, members
assert len(members) == proof['footprint']['hexes'] == sum(proof['footprint']['by_cover'].values())
assert (-5000, 0) in members and (-6000, 0) not in members
assert (1000, 0) in members and (0, 0) in members
surfaces = collections.Counter(s['type'] for s in mesh['surfaces'])
assert surfaces == {'eHexShape': 4 * len(members), 'eCollision': 23, 'eSelection': 23}, surfaces

metadata = (MOD / 'metadata.lua').read_text(encoding='utf-8')
code_block = metadata.split("'code', {", 1)[1].split('}', 1)[0]
code = re.findall(r'"([^"]+\.lua)"', code_block)
assert set(code) == {'Code/10_ElevatorDepotDev.lua', 'Code/_EntityData.generated.lua',
                     'Code/BuildingTemplate/SMROptInElevatorDepotDev.generated.lua'}
assert all((MOD / p).is_file() for p in code)
acf = Path(os.environ.get('SMR_ACF', 'A:/SteamLibrary/steamapps/appmanifest_3215050.acf'))
build = re.search(r'"buildid"\s+"(\d+)"', acf.read_text(encoding='utf-8')).group(1)
assert build == '25579348', build
archive_root = ROOT.parent / 'SMR-Shared/SMR-SrcArchive'
old_source = archive_root / '1.1.1.405907/Src'
new_source = archive_root / '1.1.1.406343/Src'
live_source = Path('A:/SteamLibrary/steamapps/common/Project Spark/ModTools/Src')
source_rows = []
for relative in ('Lua/Buildings/Station.lua', 'Lua/Units/Train.lua', 'Lua/Tracks.lua',
                 'Lua/Buildings/TrackElement.lua', 'Lua/Buildings/SpaceElevator.lua',
                 'CommonLua/Editor/ArtSpecEditor.lua'):
    hashes = [sha(root / relative) for root in (old_source, new_source, live_source)]
    assert len(set(hashes)) == 1, (relative, hashes)
    source_rows.append({'path': relative, 'old_archive_sha256': hashes[0],
                        'new_archive_sha256': hashes[1], 'installed_sha256': hashes[2]})
log_dir = Path(os.environ['APPDATA']) / 'Surviving Mars Relaunched/logs'
log_receipts = []
excerpt = []
for name in ('Mars.exe-20260930-10.54.44-6aba6e65.log',
             'MarsDebug.exe-20260930-10.58.36-6aba6e9d.log'):
    path = log_dir / name
    lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    marked = set()
    for i, line in enumerate(lines):
        if '[IMPORT]' in line or 'Lua revision:' in line or 'Build version:' in line:
            marked.add(i)
        if '[LUA ERROR]' in line:
            marked.update(range(i, min(i + 17, len(lines))))
    excerpt.append(name + ' sha256=' + sha(path))
    excerpt.extend(str(i+1) + ': ' + lines[i] for i in sorted(marked))
    log_receipts.append({'file': name, 'sha256': sha(path),
                         'lua_errors': [[i+1, line] for i, line in enumerate(lines) if '[LUA ERROR]' in line]})
(HERE / 'log_excerpt.txt').write_text('\n'.join(excerpt) + '\n', encoding='utf-8', newline='\n')
report = {
    'command': 'python docs/agent/reports/elevator_depot_import_20260930/check.py',
    'optin_head': head(ROOT), 'assets_head': head(ASSETS), 'checker_sha256': sha(Path(__file__)),
    'installed_build': build, 'build_source': str(acf), 'brief_required_build': '25579348',
    'static_import': 'PASS', 'live_trial': 'not performed',
    'source_fingerprints': {'old_archive': str(old_source), 'new_archive': str(new_source),
                            'installed_source': str(live_source), 'status': 'all identical',
                            'files': source_rows},
    'entity_sha256': sha(entity_path), 'mesh_sha256': sha(compiled),
    'fbx_sha256': proof['entity']['fbx_sha256'], 'bbox_max_error_units': bbox_error,
    'spot_count': len(rows), 'spots': rows,
    'worst_spot_error_units': max(s['position_error'] for s in rows),
    'footprint_count': len(members), 'by_cover': proof['footprint']['by_cover'],
    'hex_triangles_by_cell': [[x, y, n] for (x, y), n in sorted(members.items())],
    'surfaces_by_type': surfaces, 'surface_total': sum(surfaces.values()),
    'code_files': code, 'saved_with_revision': re.search(r"'saved_with_revision', (\d+)", metadata).group(1),
    'logs': log_receipts,
    'limits': 'Disk entity/spot/footprint/metadata audit only; no in-game placement or movement verdict.',
}
(HERE / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(report))
