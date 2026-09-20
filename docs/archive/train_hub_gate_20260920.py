"""Step-0 desk experiment; imports the unchanged oracle, never writes mod/asset code.

Run from SMR-OptInPack: python docs/archive/train_hub_gate_20260920.py
All lengths are game units (100/m). Predictions, not a game observation.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ASSETS = Path('C:/Dev/SMR-Assets')
GEOM = ASSETS / '_shared/geometry'
sys.path.insert(0, str(GEOM))
import hub_oracle as oracle


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def box(k, inner, lane=289, xspan=None):
    # k is an angular index, not a connector id. Local +x points inward.
    a = math.radians(k * 60)
    origin = inner + (xspan or oracle.TRAIN_BOX_X)[1]
    p = (origin * math.cos(a) - lane * math.sin(a),
         origin * math.sin(a) + lane * math.cos(a))
    return oracle.convex_hull(oracle.box_corners_at(
        p, k * 60 + 180, xspan=xspan or oracle.TRAIN_BOX_X))


def members(inner, lane=289, subset=range(6)):
    return [{'axes': [i, j], 'SAT_gap': oracle.convex_separation(
        box(i, inner[i], lane), box(j, inner[j], lane))}
        for i, j in itertools.combinations(subset, 2)]


def gap(inner, lane=289, subset=range(6)):
    return min(p['SAT_gap'] for p in members(inner, lane, subset))


def threshold(fn, lo, hi):
    assert fn(lo) < 0 and fn(hi) > 0, 'search must bracket an actual crossing'
    for _ in range(60):
        mid = (lo + hi) / 2
        if fn(mid) > 0:
            hi = mid
        else:
            lo = mid
    assert fn(hi + .01) > 0 and fn(hi - .01) < 0
    return hi


def summary(inner, lane=289, subset=range(6)):
    pp = members(inner, lane, subset)
    bad = [p for p in pp if p['SAT_gap'] <= 0]
    good = [p for p in pp if p['SAT_gap'] > 0]
    assert len(pp) == len(bad) + len(good)
    return {'inner_ends': inner, 'lane': lane, 'compared': len(pp),
            'intersect_or_touch': len(bad), 'clear': len(good), 'members': pp}


result = {'command': 'python docs/archive/train_hub_gate_20260920.py',
          'pack_HEAD': git(ROOT, 'rev-parse', 'HEAD'),
          'assets_HEAD': git(ASSETS, 'rev-parse', 'HEAD'),
          'game_source': 'C:/Dev/SMR-SrcArchive/1.1.0.403908/Src',
          'units_per_m': 100,
          'oracle_sha256': hashlib.sha256((GEOM / 'hub_oracle.py').read_bytes()).hexdigest()}
assert not git(ASSETS, 'diff', '66240ae', '--', '_shared/geometry/hub_oracle.py')
assert not git(ROOT, 'diff', '6019492', '--', 'tools/devmods/train_hub/')
result['baseline'] = summary([12000 / 7 - 2818] * 6, 0)
assert result['baseline']['intersect_or_touch'] == result['baseline']['compared'] == 15
for name, lane in [('centreline', 0), ('arrival_lane', 289), ('other_lane', -289)]:
    s = threshold(lambda s: gap([s] * 6, lane), -150, 1000)
    result[name] = {'inner_threshold': s, 'stop_origin': s + 2818,
                    'tail_past_connector': s + 150,
                    'integer_example': summary([math.ceil(s) + 1] * 6, lane)}

# A shared small inner portion proves arbitrary staggering cannot beat the
# equal-radius minimax within own-half-line origins 0..3177 (s >= -2818).
# Every candidate contains this rectangle, so its intersection is unavoidable.
for lane in (0, 289):
    s = result['centreline' if lane == 0 else 'arrival_lane']['inner_threshold'] - .01
    core = [box(k, s, lane, xspan=(s - 1332, 0)) for k in range(6)]
    assert all(oracle.convex_separation(core[k], core[(k + 1) % 6]) < 0 for k in range(6))
result['minimax_core_proof'] = 'PASS: adjacent common subsets intersect below equal-radius bound'
stagger = threshold(lambda s: gap([0, s, 0, s, 0, s]), 194, 1000)
result['stagger'] = {'inner_even': 0, 'inner_odd': stagger,
                     'max_tail': stagger + 150,
                     'example': summary([0, math.ceil(stagger) + 1] * 3)}
tri = threshold(lambda s: gap([s] * 6, subset=(0, 2, 4)), -150, 0)
result['alternating_three'] = {'inner_threshold': tri, 'tail': tri + 150,
                              'example': summary([math.ceil(tri) + 1] * 6, subset=(0, 2, 4))}
result['opposite_two_zero_tail'] = summary([-150] * 6, subset=(0, 3))
lane = threshold(lambda x: gap([-150] * 6, x), 289, 1200)
result['wide_lane_zero_tail'] = {'lane_threshold': lane, 'extra_side_shift': lane - 289,
                                'corridor_halfwidth': lane + 209}
s = result['arrival_lane']['inner_threshold']
tail_r = s + 4150
result['queue'] = {'waiting_origin_radius': 4000, 'waiting_nose_radius': 4000 - 2818,
                   'stopped_tail_radius': tail_r, 'overlap': tail_r - (4000 - 2818),
                   'required_wait_origin_radius': tail_r + 2818,
                   'outward_whole_hexes': math.ceil((tail_r + 2818 - 4000) / 1000),
                   'one_train_zero_tail_queue_overlap': 2818}
result['alternatives'] = {
    'shorter_train_max_length_same_width_lane': 4000 - s,
    'length_reduction_percent': (4150 - (4000 - s)) / 4150 * 100,
    'body_radius_50_tail_margin': 5000 - tail_r,
    'body_radius_50_queue_overlap_same_stop': tail_r - (5000 - 2818),
    'one_stopped_train_zero_tail_inner': -150,
    'grade_separation_min_deck_delta': 436 - 4,
    'same_origin_reverse_extra_outward_reach': 2818 - 1332,
    'same_origin_reverse_tail': s + 150 + 2818 - 1332,
    'footprint_preserving_reverse_origin_shift_inward': 2818 - 1332,
    'different_departure_lane_shift': 2 * 289}

log = ROOT / 'docs/archive/geometry_oracle_slot6_train_Mars.exe-20260919-23.34.07-6a91a190.log'
text = log.read_text(encoding='utf-8')
result['vanilla'] = []
for k in range(1, 5):
    def read(name):
        m = re.search(r'van_' + name + str(k) + r'=(-?\d+),(-?\d+),(-?\d+)@(-?\d+)', text)
        return list(map(float, m.groups()))
    c, t = read('Trackconnector'), read('Stop')
    yaw = math.radians(t[3] / 60)
    u = (math.cos(yaw), math.sin(yaw))
    depth = sum((t[i] - c[i]) * u[i] for i in range(2))
    assert depth > 0
    result['vanilla'].append({'connector': k, 'stop_inward': depth,
                              'train_inward_extent': [depth - 1332, depth + 2818],
                              'waiting_nose_gap': depth - 4150})

wf = ASSETS / 'trainhub/blender/export/lookpass_workfile_geometry.json'
w = json.loads(wf.read_text())
vertices = oracle.snapshot_world_verts(w['Hub_Portals'])
# Positive-X portal sector. Include complete faces, not just a vertex slice:
# the outermost x among every face that can reach running-surface height.
faces = [[vertices[i] for i in face] for face in w['Hub_Portals']['faces']]
upper = [f for f in faces if max(p[2] for p in f) >= 8
         and max(p[0] for p in f) > 28 and min(p[0] for p in f) > 0
         and all(abs(p[1]) < 12 for p in f)]
outer = max(p[0] for f in upper for p in f)
result['portal'] = {'snapshot_sha256': hashlib.sha256(wf.read_bytes()).hexdigest(),
                    'all_vertices_max_x_m': max(p[0] for p in vertices),
                    'upper_faces_filter': 'max z >= 8m, max x > 28m, min x > 0m, all abs(y)<12m',
                    'selected_faces': len(upper), 'members_face_indices': [i for i, f in enumerate(faces) if f in upper],
                    'upper_faces_max_x_m': outer,
                    'required_roof_extension_m': tail_r / 100 - outer,
                    'two_lane_corridor_min_width_m': (289 + 209) * 2 / 100,
                    'train_roof_height_m': (800 + 436) / 100}
assert outer < 40 < tail_r / 100
print(json.dumps(result, indent=2))
