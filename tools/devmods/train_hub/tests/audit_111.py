"""Reproduce the 1.1.1 source/log inventory; candidates are NOT semantic certification.

Writes a new evidence JSON (--output), including input hashes, every lexical call,
member name, message handler and citation, candidate engine declarations and their
body diffs. Uses the fix pack's canonical extractor; no alternate Lua body parser.
"""
import argparse
from collections import Counter, defaultdict
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
DONOR = ROOT.parent / 'SMR-BugFixPack'
sys.path.insert(0, str(DONOR / 'tools'))
import patchcheck as pc

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
archive = ROOT.parent / 'SMR-Shared/SMR-SrcArchive'
old, new = (archive / v / 'Src' for v in ('1.1.0.403908', '1.1.1.405907'))
cmp = pc.Compare(str(old), str(new))
files = sorted(p for mod in ('train_hub', 'rail_shaft')
               for p in (ROOT / 'tools/devmods' / mod).rglob('*.lua')
               if 'SourceData' not in p.parts)
records, touched = [], set()
bybare = defaultdict(set)
for rk in set(cmp.old) | set(cmp.new):
    bybare[rk[1].split('#')[0].split('.')[-1]].add(rk)
for p in files:
    raw = p.read_text(encoding='utf8')
    plain = pc.strip_lua_comments(raw)
    h = pc.harvest(str(p))
    members = sorted(set(re.findall(r'[.:]([A-Za-z_]\w*)', plain)))
    calls = sorted(h['calls'])
    # All candidates, never silently choose an unrelated class's method by name.
    candidates = set()
    for call in calls:
        candidates.update(bybare.get(call, ()))
    for pin in h['pins'] | h['reqs']:
        candidates.update(cmp.old_bykey.get(pin, ()))
        candidates.update(cmp.new_bykey.get(pin, ()))
    citations = []
    for f, a, b in sorted(h['cites'] | h['bare']):
        rels = [f] if f in cmp.oldlines else sorted(cmp.basenames.get(f, ()))
        rows = []
        for rel in rels:
            key = cmp.enclosing(rel, a)
            if key:
                candidates.add(key)
            rows.append({'file': rel, 'file_status': cmp.file_changed[rel],
                         'old_enclosing': key[1] if key else None,
                         'new_same_line': cmp.newlines.get(rel, [])[a-1:a]})
        citations.append({'citation': [f, a, b], 'candidates': rows})
    touched.update(candidates)
    records.append({'path': p.relative_to(ROOT).as_posix(),
                    'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                    'calls': calls, 'member_names': members,
                    'assignment_names': sorted(set(re.findall(r'\b([A-Za-z_]\w*)\s*=(?!=)', plain))),
                    'unresolved_calls': sorted(n for n in calls if not bybare.get(n)),
                    'handlers': re.findall(r'function OnMsg\.(\w+)', plain),
                    'string_classes': sorted(set(re.findall(r'(?:PlaceObj|DefineClass)\(\s*[\'"]([^\'"]+)', plain))),
                    'citations': citations,
                    'candidate_declarations': sorted(':'.join(rk) for rk in candidates)})

rows = []
for rk in sorted(touched):
    nkey = cmp.moved_to.get(rk, rk)
    o, n = cmp.old.get(rk), cmp.new.get(nkey)
    st = cmp.status.get(rk, 'added')
    oldbody = cmp.oldlines[rk[0]][o['span'][0]:o['span'][1]+1] if o else []
    newbody = cmp.newlines[nkey[0]][n['span'][0]:n['span'][1]+1] if n else []
    rows.append({'file': rk[0], 'key': rk[1], 'status': st,
                 'old_line': o['line'] if o else None, 'new_line': n['line'] if n else None,
                 'old_signature': o['sig'] if o else None, 'new_signature': n['sig'] if n else None,
                 'diff': list(difflib.unified_diff(oldbody, newbody, n=3, lineterm='')) if st != 'identical' else []})

logs = Path.home() / 'AppData/Roaming/Surviving Mars Relaunched/logs'
log_records, daily = [], []
warning = re.compile(r'\[LUA ERROR\]|Persist error|ASSERT\(|(?i:warning:|error |failed |failed$|different version|not loaded)')
for p in sorted(logs.glob('Mars.exe-20260923-*.log')):
    lines = p.read_text(encoding='utf8', errors='replace').splitlines()
    errors = [i+1 for i,l in enumerate(lines) if 'Persist error' in l]
    daily.append({'file': p.name, 'persist_lines': errors})
    if not any(t in p.name for t in ('21.19.58', '22.13.30', '23.38.53')):
        continue
    events = [{'line': i+1, 'text': l} for i,l in enumerate(lines) if warning.search(l)]
    fires = [{'line': i+1, 'text': l} for i,l in enumerate(lines)
             if l.startswith('[mod] [SMRTK] SMRTK_FIRE')]
    repairs = [{'line': i+1, 'text': l} for i,l in enumerate(lines) if '[TrainHubDev] repair' in l]
    stacks = []
    for i in errors:
        j = i
        while j < len(lines) and not (j > i+3 and lines[j].startswith('[mod]')):
            if re.match(r'^\s+function: [0-9A-Fa-f]+\s*$', lines[j]):
                j += 1
                break
            j += 1
        stacks.append({'line': i, 'text': lines[i-1:j]})
    log_records.append({'file': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                        'line_count': len(lines), 'events': events, 'fires': fires,
                        'repairs': repairs, 'persist_stacks': stacks,
                        'hub_presence': sum('[TrainHubDev]' in l for l in lines),
                        'shaft_presence': [{'line': i+1,'text':l} for i,l in enumerate(lines) if '[RailShaftDev]' in l]})
counts = Counter(r['status'] for r in rows)
assert sum(counts.values()) == len(rows)
assert len(records) == len(files)
result = {'command': subprocess.list2cmdline(['python', *sys.argv]),
          'head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'donor_head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=DONOR,text=True).strip(),
          'builds': [str(old), str(new)],
          'limits': 'Lexical inventory. Bare-name candidates do not prove receiver type; member names are inventoried, not all resolved. C++ implementation, computed access and runtime delivery remain unverified. Citations are matched in OLD tree; mixed-build comments require manual resolution.',
          'file_count': len(files), 'candidate_count': len(rows), 'candidate_status_counts': dict(counts),
          'files': records, 'declarations': rows, 'logs': log_records, 'daily_persist': daily}
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open('x',encoding='utf8',newline='\n') as out:
    json.dump(result,out,indent=2,ensure_ascii=False)
    out.write('\n')
print(json.dumps({k:result[k] for k in ('command','head','file_count','candidate_count','candidate_status_counts')},indent=2))
for log in log_records:
    print(log['file'], 'events', len(log['events']), 'persist', len(log['persist_stacks']), 'fires', len(log['fires']), 'hub_lines',log['hub_presence'])
