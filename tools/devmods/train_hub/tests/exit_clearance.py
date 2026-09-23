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
import sys
import argparse

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


def sweep(a, b, triangles, controls=None, bank=0):
    # Convex control hull + a yaw-independent Wasp envelope. Roll enlargement is
    # conservative for any |bank| <= the configured cap; pitch remains zero.
    if controls is None:
        assert a[2] == b[2] or a[:2] == b[:2]
        controls=[a,b]
    lateral=math.hypot(1.38,1.08)
    rounding=.005 if bank or len(controls)>2 else 0
    radius = (lateral+1.83*math.sin(bank)+rounding)/math.cos(math.pi/32)
    circle = [(radius*math.cos(i*math.tau/32), radius*math.sin(i*math.tau/32)) for i in range(32)]
    poly = hull([(p[0]+x, p[1]+y) for p in controls for x,y in circle])
    zlo = min(p[2] for p in controls)+.24*math.cos(bank)-lateral*math.sin(bank)-rounding
    zhi = max(p[2] for p in controls)+1.83+lateral*math.sin(bank)+rounding
    vertices = np.array([(x,y,z) for z in (zlo,zhi) for x,y in poly])
    broad=np.maximum(triangles.min(axis=1)-vertices.max(axis=0),
                     vertices.min(axis=0)-triangles.max(axis=1)).max(axis=1)
    nearby=broad<=2
    if not nearby.any(): return broad
    triangles=triangles[nearby]
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
    broad[nearby]=gaps
    return broad


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
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
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
parser=argparse.ArgumentParser()
parser.add_argument('--motion',type=Path)
parser.add_argument('--receipt',type=Path)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
names=['floor_to_rim','rim_to_crest','crest_to_cruise','under_deck_out','outside_climb']
results={}
legs=list(zip(names,points,points[1:]))
for name,spot in spots.items():
    if not name.startswith('Trackconnector'): continue
    rail=generator(tuple(v/100 for v in spot))
    ride=(*rail[:2],rail[2]+constant('OverTrackHeight')+constant('HoverHeight'))
    transfer=(*rail[:2],max(high[2],ride[2]))
    legs += [(name+'_transfer',high,transfer),(name+'_onto_rail',transfer,ride)]
motion=None
control_sets={}
contexts={}
bank=0
if args.motion:
    motion=json.loads(args.motion.read_text())
    assert motion['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert motion['entity_sha256']==hashlib.sha256((ROOT/'tools/devmods/train_hub/Entities/SMROptInTrainHub6.entjson').read_bytes()).hexdigest()
    bank=math.radians(motion['bank_angle_minutes']/60)
    # L2M2: the engine flies straight chords cut at every span boundary, so no rendered
    # chord straddles two spans; the export states the horizon it needs (0 for cut chords).
    horizon=motion.get('chord_horizon_ms',100)
    def split(control,u):
        rows=[np.array(control,dtype=float)]
        while len(rows[-1])>1: rows.append(rows[-1][:-1]*(1-u)+rows[-1][1:]*u)
        return [r[0].tolist() for r in rows], [r[-1].tolist() for r in rows[::-1]]
    def clip(c,lo,hi):
        u0=max(0,(lo-c['start'])/(c['finish']-c['start']))
        u1=min(1,(hi-c['start'])/(c['finish']-c['start']))
        left,_=split(c['points'],u1)
        return split(left,u0/u1)[1] if u0>0 else left
    legs=[]
    bank_of={}
    for name,curves in motion['routes'].items():
        for i,c in enumerate(curves):
            # Runtime chords span at most 100 game-ms; include clipped neighbour
            # hulls so a chord straddling a curve seam is bounded too. Recall's
            # source clock advances no faster than this forward clock.
            lo,hi=c['start']-horizon,c['finish']+horizon
            controls=[generator(tuple(v/100 for v in p)) for other in curves
                      if other['finish']>lo and other['start']<hi
                      for p in clip(other,lo,hi)]
            label=f'{name}_curve_{i:02d}'
            control_sets[label]=controls
            contexts[label]=(curves,c['start'],c['finish'])
            # L2M2 exports the roll actually commanded on each span; a span without one
            # (older exports) is swept at the configured cap.
            bank_of[label]=math.radians(c.get('bank_minutes',motion['bank_angle_minutes'])/60)
            legs.append((label,controls[0],controls[-1]))
# Positive/negative controls: intersecting and clearly separated triangles.
assert sweep((0,0,0),(10,0,0),np.array([[[5,-1,1],[5,1,1],[5,0,2]]],dtype=float))[0]<=0
assert sweep((0,0,0),(10,0,0),np.array([[[5,-1,10],[5,1,10],[5,0,11]]],dtype=float))[0]>0
cache={}
for name,a,b in legs:
    margins={}; worst_triangles={}
    refinements={}
    controls=control_sets.get(name)
    cache_key=repr(controls or [a,b])
    if cache_key in cache:
        results[name]=cache[cache_key]
        continue
    for ob,triangles in groups.items():
        # The bottom of the drone is .24 m above the floor; include floor and shaft.
        leg_bank=bank_of.get(name,bank)
        gaps=sweep(a,b,triangles,controls,leg_bank)
        margin=float(gaps.min()); triangle=int(gaps.argmin())
        if margin<=0 and name in contexts:
            # A prism spreads one corner's height across a long straight. If it
            # intersects, subdivide TIME (not the safety envelope) and require
            # every smaller, still conservative prism to separate.
            curves,t0,t1=contexts[name]
            leaves=[]
            def refine(lo,hi):
                pts=[generator(tuple(v/100 for v in p)) for c in curves
                     if c['finish']>lo-horizon and c['start']<hi+horizon
                     for p in clip(c,lo-horizon,hi+horizon)]
                gs=sweep(pts[0],pts[-1],triangles,pts,leg_bank)
                value=float(gs.min()); index=int(gs.argmin())
                if value<=0 and hi-lo>1:
                    return min(refine(lo,(lo+hi)/2),refine((lo+hi)/2,hi))
                leaves.append({'start':lo,'finish':hi,'margin_m':value,'controls':pts})
                return value,index
            margin,triangle=refine(t0,t1)
            refinements[ob]=leaves
        margins[ob]=margin
        worst_triangles[ob]=triangles[triangle].tolist()
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
                  'worst_triangle_generator_m':worst_triangles[worst], 'families':nearest,
                  'refined_objects':refinements}
    cache[cache_key]=results[name]
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
if motion:
    result.update(motion=motion,bank_angle_minutes=motion['bank_angle_minutes'],
                  span_bank_minutes={n:round(math.degrees(b)*60) for n,b in bank_of.items()},
                  interpolation_horizon_game_ms=horizon,control_hulls_generator_m=control_sets)
    result['command']='blender -b '+str(BLEND)+' --python-exit-code 1 --python tools/devmods/train_hub/tests/exit_clearance.py -- --motion '+str(args.motion)+' --receipt '+str(args.receipt)
assert hashlib.sha256(BLEND.read_bytes()).hexdigest()==blend_hash, 'Shared geometry changed during measurement'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash, 'Flight source changed during measurement'
assert len(results)==len(legs)
assert sum(len(t) for t in groups.values())==result['triangle_total']
if args.receipt: args.receipt.write_text(json.dumps(result,indent=2)+'\n')
worst=min(results,key=lambda n:results[n]['margin_m'])
print('EXIT_CLEARANCE_SUMMARY='+json.dumps({'head':result['head'],'source_sha256':result['source_sha256'],
      'objects':len(groups),'triangles':result['triangle_total'],'legs':len(legs),
      'worst_leg':worst,**results[worst]}))
if not args.receipt: print('EXIT_CLEARANCE_JSON='+json.dumps(result))
assert all(v['margin_m']>0 for v in results.values()), 'Swept envelope overlaps geometry'
