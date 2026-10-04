"""Read-only audit controls. Writes only new scratch files and an optional NEW receipt.

Run: python docs/archive/final_launch_audit_20261003/verify.py [new-receipt.json]
Expected baseline failures are captured findings, not repaired or treated as PASS.
"""
from pathlib import Path
import contextlib
import hashlib
import importlib.util
import io
import json
import re
import struct
import subprocess
import sys
import tempfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'CLAUDE.md').is_file())
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT.parent / 'SMR-BugFixPack/tools'))
import patchcheck

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    return json.loads((ROOT / p).read_text(encoding='utf-8-sig'))

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

r = {'command': 'python ' + Path(__file__).relative_to(ROOT).as_posix(),
     'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
     'build': patchcheck.installed_build(), 'source_receipts': {}, 'logs': {}}
source = read('docs/archive/ship_evidence_20261003/source_receipt.json')
assert r['build'] == source['build']
src = ROOT.parent / 'SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src'
for name, rec in source['packs'].items():
    pack = Path(patchcheck.INSTALL) / 'Packs' / name
    assert sha(pack) == rec['pack_sha256'], name
    paths = [m['path'] for m in rec['members']]
    assert len(paths) == len(set(paths)) == rec['matched'] > 0
    for member in rec['members']:
        p = src / member['path']
        assert sha(p) == member['sha256'] and p.stat().st_size == member['bytes'], str(p)
    r['source_receipts'][name] = {'sha256': sha(pack), 'members_verified': len(paths),
        'filter': 'each member in source_receipt.json packs[' + name + '].members'}

receipt = read('docs/archive/train_final_result_20261003/receipt.json')
loglines = {}
for key, rec in receipt['logs'].items():
    p = ROOT / 'docs/archive/train_final_result_20261003' / rec['file']
    assert sha(p) == rec['sha256'] and p.stat().st_size == rec['bytes']
    lines = p.read_text(encoding='utf-8-sig').splitlines()
    assert len(lines) == rec['lines']
    for kind, pattern in rec['filters'].items():
        actual = [{'line': i, 'text': s} for i, s in enumerate(lines, 1) if re.search(pattern, s)]
        assert actual == rec['members'][kind], (key, kind)
        assert len(actual) == rec['counts'][kind]
    loglines[key] = lines
    r['logs'][key] = {'sha256': sha(p), 'verified_filters': rec['counts']}

lines = loglines['20261003-12.55.31']
stock = receipt['stock_control']
keys = set()
for row in stock['members']:
    keys.add((row['object'], row['resource']))
    a, b = row['before']['fields'], row['after']['fields']
    assert a['stock'] == b['stock'] and a['t'] == b['t']
    assert (a['capacity'], b['capacity']) == ('4000000', '2000000')
    for side in ('before', 'after'):
        witness = lines[row[side]['line'] - 1]
        for key, value in row[side]['fields'].items():
            assert re.search(r'\b' + re.escape(key + '=' + value) + r'(?=\s|$)', witness), (key, value)
assert len(keys) == len(stock['members']) == stock['compared'] > 0
removal = loglines['20261003-13.05.06']
before = [i for i, s in enumerate(removal, 1) if i < 404 and s.startswith('[LUA ERROR]')]
after = [i for i, s in enumerate(removal, 1) if i >= 404 and s.startswith('[LUA ERROR]')]
assert before == [213, 265, 286, 336, 372] and not after and len(removal) == 481
assert 'native_match=true' in removal[477] and 'optin_present=false' in removal[477]
assert 'SMROptInElevatorDepotDevBase:SMROptInElevatorDepotDev' in removal[423]
assert 'SMROptInTrainHub6Base:SMROptInTrainHub6' in removal[425]
r['stock_control'] = {'compared': len(keys), 'filter': stock['filter']}
r['removal_window'] = {'lines': [404, 481], 'errors_before': before, 'errors_after': after,
                       'class_warning_lines': [424, 426], 'native_match_line': 478}
residual = read('docs/archive/ship_residual_20261003/receipt.json')
assert sha(ROOT / 'local/ship-evidence-20261003/SMRTK_B.sav') == residual['save_sha256']
r['save_sha256'] = residual['save_sha256']

parity = module('audit_store_parity', 'tools/store_parity.py')
with tempfile.TemporaryDirectory(prefix='final_launch_audit_', dir=ROOT / 'scratch') as td:
    temp = Path(td)
    doc = (ROOT / 'docs/UPLOAD_WORKFLOW.md').read_text(encoding='utf-8')
    card = temp / 'card.md'
    parity.CARD = str(card)
    bodies = '\n'.join(h + '\n\n```\n' + parity.fenced_block(doc, h) + '\n```\n'
                       for h in (parity.H_PARADOX, parity.H_STEAM))
    def parity_case(label, contents):
        card.write_text(contents, encoding='utf-8')
        stream = io.StringIO()
        try:
            with contextlib.redirect_stdout(stream):
                code = parity.main([])
            result = {'exit': code}
        except Exception as exc:
            result = {'exception': type(exc).__name__, 'message': str(exc)}
        result['stdout'] = stream.getvalue()
        r.setdefault('parity_controls', {})[label] = result
    parity_case('live_matching_bodies', '# LIVE\n' + bodies)
    parity_case('live_missing_one_body', '# LIVE\n' + bodies.split(parity.H_STEAM)[0])
    parity_case('prepublication_control', '# PRE-PUBLICATION\n')

    # A real minimal stored FLPK exercises the production directory reader/extractor.
    tree = temp / 'tree'
    tree.mkdir()
    (tree / 'items.lua').write_bytes(b'tree bytes\n')
    payload = b'packed bytes\n'
    name = b'items.lua'
    table = struct.pack('<III', 32, (len(name) << 24) | (0x10 << 16), len(payload)) + name + bytes(4)
    header = bytearray(32)
    header[:4] = b'FLPK'
    struct.pack_into('<I', header, 12, 32 + len(payload))
    struct.pack_into('<I', header, 20, len(table))
    fpk = temp / 'fixture.fpk'
    fpk.write_bytes(header + payload + table)
    for label, value in [('different_bytes', b'tree bytes\n'), ('matching_control', payload)]:
        (tree / 'items.lua').write_bytes(value)
        out = subprocess.run([sys.executable, str(ROOT / 'tools/pack_list.py'), str(fpk), '--tree', str(tree)],
                             cwd=ROOT, text=True, encoding='utf-8', capture_output=True)
        r.setdefault('pack_controls', {})[label] = {'exit': out.returncode, 'stdout': out.stdout, 'stderr': out.stderr}

print(json.dumps(r, indent=2))
if len(sys.argv) > 1:
    with Path(sys.argv[1]).open('x', encoding='utf-8', newline='\n') as dest:
        json.dump(r, dest, indent=2)
        dest.write('\n')
