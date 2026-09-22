"""Read-only Blender measurement of L2R's native-scale, level-Wasp exit.

Run with Blender -b <work.blend> --python-exit-code 1 --python <this file>.
No blend is saved. Includes optional siding panels and evaluated curve ribs.
Sweeps a circumscribed 32-sided cylinder along each vertical/horizontal leg.
Triangle/prism SAT gives a conservative separating-plane distance, not a native
collision verdict. A nonpositive margin fails. Runtime cargo is not in this mesh.
"""
import hashlib
import json
import math
from pathlib import Path
import subprocess

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'tools/devmods/train_hub/Code/30_TrainHubDrones.lua'
BLEND = Path(bpy.data.filepath)
blend_hash = hashlib.sha256(BLEND.read_bytes()).hexdigest()
EXCLUDED = {'hex_shape', 'Collision', 'Selection', 'terrain_hole',
            'Glass', 'Guide_Hexes_MustStayFree'}


def hull(points):
    pts = sorted(set(map(tuple, points)))
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for result, ordered in ((lower, pts), (upper, reversed(pts))):
        for p in ordered:
            while len(result) >= 2 and cross(result[-2], result[-1], p) <= 0:
                result.pop()
            result.append(p)
    return np.array(lower[:-1]+upper[:-1])


def sweep(a, b, triangles):
    # Horizontal or vertical extrusion; the polygon contains the full yaw cylinder.
    assert a[2] == b[2] or a[:2] == b[:2]
    radius = math.hypot(1.38, 1.08)/math.cos(math.pi/32)
    circle = [(radius*math.cos(i*math.tau/32), radius*math.sin(i*math.tau/32)) for i in range(32)]
    poly = hull([(p[0]+x, p[1]+y) for p in (a,b) for x,y in circle])
    zlo, zhi = min(a[2],b[2])+.24, max(a[2],b[2])+1.83
    vertices = np.array([(x,y,z) for z in (zlo,zhi) for x,y in poly])
    edges = np.column_stack((np.roll(poly,-1,axis=0)-poly, np.zeros(len(poly))))
    edges = np.vstack((edges, [0,0,1]))
    face_axes = np.vstack((np.cross(edges[:-1], [0,0,1]), [0,0,1]))
    tri_edges = np.roll(triangles,-1,axis=1)-triangles
    # Largest separating-plane gap per triangle is a lower bound on Euclidean clearance.
    gaps = np.full(len(triangles), -np.inf)
    def shared(axis):
        length=np.linalg.norm(axis)
        if length < 1e-9: return
        axis=axis/length
        tv=triangles @ axis; pv=vertices @ axis
        np.maximum(gaps, np.maximum(tv.min(axis=1)-pv.max(), pv.min()-tv.max(axis=1)), out=gaps)
    for axis in face_axes: shared(axis)
    # Each triangle has its own normal and edge cross-product axes.
    axes=[np.cross(tri_edges[:,0],tri_edges[:,1])]
    axes += [np.cross(tri_edges[:,i],edge) for edge in edges for i in range(3)]
    for axis in axes:
        norms=np.linalg.norm(axis,axis=1)
        good=norms>1e-9
        unit=axis/np.where(good,norms,1)[:,None]
        tv=np.einsum('nij,nj->ni',triangles,unit)
        # Avoid a large vertex/triangle matrix in the common-axis loop above.
        pv=unit @ vertices.T
        gap=np.maximum(tv.min(axis=1)-pv.max(axis=1),pv.min(axis=1)-tv.max(axis=1))
        np.maximum(gaps,np.where(good,gap,-np.inf),out=gaps)
    return gaps


deps=bpy.context.evaluated_depsgraph_get()
groups={}
for ob in bpy.context.scene.objects:
    if ob.type not in {'MESH','CURVE'} or ob.name in EXCLUDED: continue
    ev=ob.evaluated_get(deps); mesh=ev.to_mesh(); mesh.calc_loop_triangles()
    vs=[tuple(ev.matrix_world @ v.co) for v in mesh.vertices]
    groups[ob.name]=np.array([[vs[i] for i in t.vertices] for t in mesh.loop_triangles])
    ev.to_mesh_clear()

# Entity <-> generator transform verified against current imported pit spots below.
def generator(p):
    x,y,z=p
    return (-.5*x-math.sqrt(3)/2*y, -math.sqrt(3)/2*x+.5*y, z)

entity=json.loads((ROOT/'tools/devmods/train_hub/Entities/SMROptInTrainHub6.entjson').read_text())
# Read constants from the implemented source, so tuning invalidates this measurement.
import re
source=SOURCE.read_text()
def constant(name):
    return float(re.search(r'\b'+name+r'\s*=\s*(-?[\d.]+)',source).group(1))/100

spots={s['name']:s['spotPos'] for s in entity['$value']['meshDescriptions'][0]['attaches']}
def offset_spot(name):
    x,y,z=spots[name]
    return generator((x/100+constant('PitOffsetX'),y/100+constant('PitOffsetY'),z/100))
floor=offset_spot('Pitfloor'); rim=offset_spot('Pitrim'); pit=rim
for name in ('Pitfloor','Pitrim',*(n for n in spots if n.startswith('Trackconnector'))):
    imported=generator(tuple(v/100 for v in spots[name]))
    source_spot=bpy.data.objects.get('-'+name)
    assert source_spot is not None, name
    assert np.linalg.norm(np.array(imported)-np.array(source_spot.matrix_world.translation))<.001
crest=(*pit[:2],constant('PitExitZ'))
cruise=(*pit[:2],constant('UnderDeckHeight'))
out=generator((constant('ExitDirectionX')/10*constant('OutwardDistance'),
               constant('ExitDirectionY')/10*constant('OutwardDistance'),constant('UnderDeckHeight')))
high=(*out[:2],constant('TransferHeight'))
points=[floor,rim,crest,cruise,out,high]
names=['floor_to_rim','rim_to_crest','crest_to_cruise','under_deck_out','outside_climb']
results={}
legs=list(zip(names,points,points[1:]))
for name,spot in spots.items():
    if not name.startswith('Trackconnector'): continue
    rail=generator(tuple(v/100 for v in spot))
    ride=(*rail[:2],rail[2]+constant('OverTrackHeight')+constant('HoverHeight'))
    transfer=(*rail[:2],max(high[2],ride[2]))
    legs += [(name+'_transfer',high,transfer),(name+'_onto_rail',transfer,ride)]
# Positive/negative controls: intersecting and clearly separated triangles.
assert sweep((0,0,0),(10,0,0),np.array([[[5,-1,1],[5,1,1],[5,0,2]]],dtype=float))[0]<=0
assert sweep((0,0,0),(10,0,0),np.array([[[5,-1,10],[5,1,10],[5,0,11]]],dtype=float))[0]>0
for name,a,b in legs:
    margins={}; worst_triangles={}
    for ob,triangles in groups.items():
        # The bottom of the drone is .24 m above the floor; include floor and shaft.
        gaps=sweep(a,b,triangles)
        margins[ob]=float(gaps.min())
        worst_triangles[ob]=triangles[int(gaps.argmin())].tolist()
    worst=min(margins,key=margins.get)
    families={'deck':('Track_','CentrePlate','Siding_'), 'centre_pillars':('Pillar_',),
              'ring_pillars':('RingPillar_',), 'beds':('Bay_',), 'ring_wall':('Ring',),
              'hoods':('Hood_',), 'portal_arches':('Portal',)}
    nearest={}
    for family,prefixes in families.items():
        members={n:m for n,m in margins.items() if n.startswith(prefixes)}
        if family=='ring_wall': members={n:m for n,m in members.items() if not n.startswith('RingPillar_')}
        member=min(members,key=members.get)
        nearest[family]={'object':member,'margin_m':members[member]}
    results[name]={'worst_object':worst,'margin_m':margins[worst],
                  'worst_triangle_generator_m':worst_triangles[worst], 'families':nearest}
result={'command':'blender -b <work.blend> --python-exit-code 1 --python tools/devmods/train_hub/tests/exit_clearance.py',
        'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'assets_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=BLEND.parents[2],text=True).strip(),
        'blend':bpy.data.filepath,'blend_sha256':blend_hash,
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'entity_sha256':hashlib.sha256((ROOT/'tools/devmods/train_hub/Entities/SMROptInTrainHub6.entjson').read_bytes()).hexdigest(),
        'object_triangles':{n:len(t) for n,t in groups.items()},
        'triangle_total':sum(map(len,groups.values())),
        'excluded_names':sorted(EXCLUDED), 'generator_waypoints_m':points,
        'leg_count':len(legs),'legs':results}
print('EXIT_CLEARANCE_JSON='+json.dumps(result))
assert hashlib.sha256(BLEND.read_bytes()).hexdigest()==blend_hash, 'Shared geometry changed during measurement'
assert all(v['margin_m']>0 for v in results.values()), 'Swept envelope overlaps geometry'
