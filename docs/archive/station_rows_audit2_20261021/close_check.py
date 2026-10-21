"""Check this audit's recorded outcome without running or changing shipping behavior."""
from pathlib import Path
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf8')
print('COMMAND:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), flush=True)

def git(*args):
    return subprocess.check_output(['git', *args], encoding='utf8')

def read(path):
    return Path(path).read_text(encoding='utf8')

assert not git('diff', '3aa5402', '--', 'Code/', 'tools/trains/')
assert not git('diff', 'aa7dac1', '--', 'docs/archive/station_rows_audit_20261021/')
print('PASS shipping Code/tools/trains unchanged from3aa5402; first audit archive unchanged fromaa7dac1')
for name in ['D16', 'D18']:
    path=f'docs/agent/bugs/{name}.md'
    current=read(path); old=git('show', f'aa7dac1:{path}')
    assert current.split('---',2)[1]==old.split('---',2)[1]
    assert 'status: "tested-attended"' in current
    assert 'Audited 2026-10-21 (Codex, GPT-6 per transcript): confirmed as desk-verified at `3aa5402`' in current
    assert 'the second audit is owed' not in current
    print(f'PASS {name} front matter/status unchanged; confirmed audit line present; pending debt removed')

prompt='docs/agent/prompts/STATION_ROWS_RELAY_AUDIT2_high.md'
assert not Path(prompt).exists()
checks=[('OI-54', 'docs/PLAYTEST_CHECKLIST.md'),
        ('STATION_ROWS_RELAY_AUDIT2_high.md', 'docs/agent/prompts/README.md')]
for needle,path in checks:
    cmd=['rg','-n','-F',needle,path]
    p=subprocess.run(cmd,capture_output=True,encoding='utf8')
    print('COMMAND:',subprocess.list2cmdline(cmd), 'EXIT:',p.returncode)
    assert p.returncode==1 and not p.stdout and not p.stderr
assert '### OI-52' in read('docs/PLAYTEST_CHECKLIST.md')
assert 'ARBORETUM_MODEL_high.md' in read('docs/agent/prompts/README.md')
print('PASS consumed prompt/map row/OI-54 absent; neighboring live work remains')

report=read('docs/agent/reports/STATION_ROWS_RELAY_20261021.md')
assert '**Latest independent verdict in §18: confirmed as desk-verified at `3aa5402`.**' in report
section=report.split('## 18 · Independent correction audit',1)[1]
for text in ['**A1 / R7 — confirmed.**','**A2 — confirmed.**','**A3 — confirmed within synchronous callbacks.**',
             '**A4 — confirmed.**','**A5 — confirmed.**','5200 cases = 1200 original-seed cases + 4000 broader cases',
             'Large-colony latency is NOT RUN','Exact-identifier-does-not-exist'][:-1]:
    assert text in section,text
assert 'GPT-6 per session instruction; exact runtime model identifier' in section
assert 'The confirmed verdict clears the audit gate for v1.0.4' in section
for name in ['native_math','ui_check','current_boundary','contract','regressions']:
    assert read(f'docs/archive/station_rows_audit2_20261021/{name}_output.txt').rstrip().endswith('EXIT: 0')
print('PASS current verdict, A1-A5 evidence, executed-model limit, NOT RUN boundaries and release route recorded')

outbox=read('docs/agent/prompts/perma/RELEASE_OUTBOX.md')
assert 'confirmed as desk-verified' in outbox and 'R1–R7' in outbox
assert 'second audit (OI-54) is owed' not in outbox
assert "No named player's save is verified fixed" in outbox
marker='### Pending · Arboretum'
assert outbox.split(marker,1)[1]==git('show','aa7dac1:docs/agent/prompts/perma/RELEASE_OUTBOX.md').split(marker,1)[1]
assert "R7's later cargo-reachability ruling" in read('docs/agent/bugs/D18.md')
print('PASS outbox qualified and audit gate cleared; unrelated pending/released entries unchanged; D18 points to canonical R7')
print('NOT RUN: engine scheduling/rebuild timing, saves, cabin/drones, pixels, player saves, large-colony latency, either in-game shipping configuration, packing/upload.')
