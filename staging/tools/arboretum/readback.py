"""Read the owner-imported Arboretum assets back against the export proof; read-only.

python staging/tools/arboretum/readback.py [<fbx_dump.json>]

Compares staging/Entities, Meshes, Materials and SourceData with SMR-Assets
arboretum/blender/export/model_proof.json: the FBX the editor was pointed at is the proved one,
every proved spot (name, position, angle, annotation) is in the compiled entity and nothing else
is, the HexShape triangles are the proved ones, and the compiled mesh's triangle list parses.
With a dump of the FBX meshes (world-space cm positions and triangle counts, written by Blender)
it also requires the compiled positions and the FBX positions to cover each other.
Does not run the game. The .hgrm layout is IMPORTER_FACTS's (elevatorstation diag_hgrm_depot.py).
"""
import collections
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
REPO = STAGE.parent
ASSETS = REPO.parent / 'SMR-Assets'
EXPORT = ASSETS / 'arboretum/blender/export'
BODY, GLASS = 'SMROptInArboretumPavilion', 'SMROptInArboretumGlass'
PREFIX = 'Mod/SMR_CommunityOptInPack_Workbench/'
TOL = 0.5   # cm; the compiled mesh quantises positions to sint16 over the bbox


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def entity(name):
    return json.loads((STAGE / 'Entities' / (name + '.entjson')).read_text(encoding='utf-8'))['$value']


def hgrm(name):
    b = (STAGE / 'Meshes' / (name + '_mesh.sub_0.hgrm')).read_bytes()
    assert b[:4] == b'dhsm', name
    lod = entity(name)['meshDescriptions'][0]['lods'][0]
    lo, hi = lod['boxMin'], lod['boxMax']
    vb = struct.unpack_from('<I', b, 281)[0]
    assert vb % 20 == 0, 'vertex buffer is not 20-byte vertices'
    raw = [struct.unpack_from('<hhBBBBhhBBhB', b, 285 + i * 20) for i in range(vb // 20)]
    qmax = max(max(abs(r[0]), abs(r[1]), abs(r[10])) for r in raw)
    c = [(l + h) / 2 for l, h in zip(lo, hi)]
    s = max((h - l) / 2 for l, h in zip(lo, hi)) / qmax
    verts = [(c[0] + r[0] * s, c[1] + r[1] * s, c[2] + r[10] * s) for r in raw]
    ib = 285 + vb
    count = struct.unpack_from('<I', b, ib)[0]
    idx = struct.unpack_from('<%dH' % count, b, ib + 4)
    assert count % 3 == 0 and max(idx) < len(verts), 'index list does not parse'
    assert ib + 4 + count * 2 <= len(b)
    return dict(vertices=len(verts), triangles=count // 3, scale_cm=round(s, 5), verts=verts)


def covers(a, b, tol=TOL):
    """Largest distance from a point of a to its nearest point of b, by grid lookup."""
    grid = collections.defaultdict(list)
    for p in b:
        grid[tuple(int(x // 8) for x in p)].append(p)
    worst = 0.0
    for p in a:
        k = tuple(int(x // 8) for x in p)
        best = min((sum((u - v) ** 2 for u, v in zip(p, q)) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                    for dz in (-1, 0, 1) for q in grid.get((k[0] + dx, k[1] + dy, k[2] + dz), ())),
                   default=1e12)
        worst = max(worst, best ** .5)
    return round(worst, 3)


def spot_key(name, pos, angle, annotation):
    return (name, tuple(round(x) for x in pos), round(angle) % 360, annotation or '')


def main():
    proof = json.loads((EXPORT / 'model_proof.json').read_text(encoding='utf-8'))
    out = dict(command='python staging/tools/arboretum/readback.py' + ''.join(' ' + a for a in sys.argv[1:]),
               head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
               proof_assets_head=proof['assets_head'], game=proof['game'], entities={})
    dump = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')) if len(sys.argv) > 1 else None
    for name in (BODY, GLASS):
        fbx = EXPORT / (name + '.fbx')
        assert sha(fbx) == proof['entities'][name]['fbx_sha256'], f'{name}: FBX on disk is not the proved one'
        item = (STAGE / 'SourceData/SIE_ImportItem' / (name + '.lua')).read_text(encoding='utf-8')
        assert re.search(r'ScenePath = "([^"]+)"', item)[1] == fbx.as_posix(), f'{name}: import item points elsewhere'
        mesh_file = STAGE / 'Meshes' / (name + '_mesh.sub_0.hgrm')
        assert mesh_file.stat().st_mtime > fbx.stat().st_mtime, f'{name}: compiled mesh is older than the FBX'
        ent = entity(name)
        assert ent['strName'] == name and [s['name'] for s in ent['states']] == ['idle']
        desc = ent['meshDescriptions'][0]
        assert len(desc['lods']) == 1 and len(desc['lods'][0]['meshes_data']) == 1
        leaf = desc['lods'][0]['meshes_data'][0]
        assert leaf['mesh'] == PREFIX + 'Meshes/' + mesh_file.name
        assert leaf['material'] == PREFIX + f'Materials/{name}.mtljson'
        material = json.loads((STAGE / 'Materials' / (name + '.mtljson')).read_text(encoding='utf-8'))['$value'][0]
        for key in ('BaseColor', 'Normal', 'RM', 'SI'):
            assert material[key].startswith(PREFIX) and (STAGE / material[key][len(PREFIX):]).is_file(), material[key]
        m = hgrm(name)
        rec = dict(fbx_sha256=sha(fbx), hgrm_sha256=sha(mesh_file), entjson_sha256=sha(STAGE / 'Entities' / (name + '.entjson')),
                   compiled_vertices=m['vertices'], compiled_triangles=m['triangles'], scale_cm_per_unit=m['scale_cm'],
                   boxMin=desc['lods'][0]['boxMin'], boxMax=desc['lods'][0]['boxMax'],
                   proof_vertices=proof['entities'][name]['vertices'], proof_faces=proof['entities'][name]['faces'])
        if dump:
            d = dump[name]
            # Blender's FBX axes are not the game's. Two maps are tried; exactly one may fit the
            # compiled mesh, and that same map must carry the FBX spot empties onto the compiled
            # spots, so mesh and spots are proved to share one frame.
            maps = {'(y,-x,z)': lambda x, y, z: (y, -x, z), '(-y,-x,z)': lambda x, y, z: (-y, -x, z)}
            fits = {}
            for label, f in maps.items():
                moved = [f(*q) for q in d['positions']]
                fits[label] = max(covers(m['verts'], moved), covers(moved, m['verts']))
            frame = [k for k, v in fits.items() if v <= TOL]
            rec.update(fbx_triangles=d['triangles'], fbx_polygons=d['polygons'], fbx_vertices=len(d['positions']),
                       fit_max_cm=fits, frame=frame)
            assert d['polygons'] == rec['proof_faces'] and len(d['positions']) == rec['proof_vertices'], (
                f'{name}: FBX mesh is not the proved one')
            assert d['triangles'] == m['triangles'], f'{name}: compiled triangle count differs from the FBX'
            # The glass shell is mirror-symmetric, so both maps fit it; it must fit the body's.
            if name == BODY:
                assert len(frame) == 1, f'{name}: compiled positions drift from the FBX: {rec}'
                out['frame'] = frame[0]
            assert out['frame'] in frame, f'{name}: compiled positions drift from the FBX: {rec}'
            frame = [out['frame']]
            empties = collections.Counter(tuple(round(c) + 0 for c in maps[frame[0]](*q)) for q in d['empties'])
            spots = collections.Counter(tuple(round(c) + 0 for c in a.get('spotPos', [0, 0, 0])) for a in desc.get('attaches', []))
            assert empties == spots, f'{name}: spots and mesh are not in one frame'
            rec['spots_in_mesh_frame'] = sum(spots.values())
        if name == GLASS:
            assert material['BlendType'] == 'blendGlass' and material['DepthWrite'] is False
            assert material['TwoSidedShading'] is True and material['CastShadow'] is False
            assert not desc.get('attaches') and not desc.get('surfaces')
            rec['material'] = {k: material[k] for k in ('BlendType', 'DepthWrite', 'TwoSidedShading', 'CastShadow')}
        else:
            want = collections.Counter(spot_key(s['name'], s['pos'], s['angle'],
                                                'att,%s,show' % s['attach'] if 'attach' in s else s.get('annotation'))
                                       for s in proof['spots'])
            got = collections.Counter()
            for a in desc['attaches']:
                sign = -1 if a.get('spotRotAxis', [0, 0, 1])[2] < 0 else 1
                assert a.get('spotRotAxis', [0, 0, 1])[:2] == [0, 0], a
                got[spot_key(a['name'], a.get('spotPos', [0, 0, 0]), sign * a.get('spotRotAngle', 0), a.get('annotation'))] += 1
            assert got == want, dict(missing=sorted(map(str, (want - got).elements()))[:10],
                                     extra=sorted(map(str, (got - want).elements()))[:10])
            attached = collections.Counter(re.fullmatch(r'att,(\w+),show', a['annotation'])[1]
                                           for a in desc['attaches'] if a.get('annotation', '').startswith('att,'))
            assert dict(attached) == proof['attached'], 'attached classes differ from the proof'
            lights = sorted(a['annotation'] for a in desc['attaches'] if a['name'] == 'Autolight')
            assert lights == sorted(proof['lights'])
            surfaces = collections.Counter(s['type'] for s in desc['surfaces'])
            # The importer fans each proved hex face into triangles: same corner set, 4 per face.
            corners = lambda faces: {tuple(round(x) for x in p) for f in faces for p in f}
            compiled = [s['points'] for s in desc['surfaces'] if s['type'] == 'eHexShape']
            assert corners(compiled) == corners(proof['hex_faces']), 'HexShape differs from the proof'
            assert len(compiled) == 4 * len(proof['hex_faces']), 'HexShape triangle count'
            assert 'eBuild' not in surfaces, 'a Build surface was imported; the Large Garden has none'
            rec.update(spots=sum(got.values()), spot_names=dict(sorted(collections.Counter(
                           'Plant*' if k[0].startswith('Plant') else k[0] for k in got.elements()).items())),
                       attached_total=sum(attached.values()), attached=dict(sorted(attached.items())),
                       lights=len(lights), surfaces=dict(surfaces))
        out['entities'][name] = rec
    spec = (STAGE / 'Code/_EntityData.generated.lua').read_text(encoding='utf-8')
    assert re.search(r'EntityData\["%s"\] = \{[^}]*entity = \{\s*class_parent = "BuildingEntityClass"' % BODY, spec, re.S)
    glass_block = re.search(r'EntityData\["%s"\] = \{(.*?)\n\}' % GLASS, spec, re.S)[1]
    assert 'class_parent' not in glass_block
    out['result'] = 'compiled assets match the export proof'
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
