"""Reconcile the exact R1 native census before choosing its repair targets."""
from pathlib import Path
import re
import subprocess

p = Path(__file__).with_name('Mars.exe-20260930-17.32.07-6aba6e65.log')
text = p.read_text(encoding='utf-8')
rows = [(i, line) for i, line in enumerate(text.splitlines(), 1)
        if '[ElevatorDepotDev] prop inspect ' in line and ' entity=SpaceElevatorRope ' in line]
ghosts = [(i, line) for i, line in rows if 'parent=nil owner=UNOWNED ' in line]
owned = [(i, line) for i, line in rows if 'owner=depot:8404 ' in line]
assert len(rows) == 8 and len(ghosts) == len(owned) == 4
for group in (ghosts, owned):
    assert {int(re.search(r'pos=\(384000, 303100, (\d+)\)', line)[1]) for _, line in group} == {
        10000, 17500, 25000, 32500}
    assert all('slot=2 env=Underground' in line and 'scale=75 ' in line and 'Object=nil ' in line
               and 'permanent=false ' in line for _, line in group)
assert all('delete_on_load=false' in line for _, line in ghosts)
assert all('delete_on_load=true' in line for _, line in owned)
assert '[LUA ERROR]' not in text, 'native errors require review'
assert 'ropes=8 ropes_outside_Object=8 parentless_unowned_ropes=4; read-only' in text
root = Path(__file__).resolve().parents[3]
print('command: python docs/archive/elevator_rope_20260930/check_identified_rope_log.py')
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip())
print('filter: [ElevatorDepotDev] prop inspect + exact entity=SpaceElevatorRope')
print('ropes: 8 = 4 parentless unowned + 4 owned by depot 8404')
for name, group in [('unowned', ghosts), ('owned', owned)]:
    print(name, [(i, int(re.search(r'index=(\d+)', line)[1]),
                 re.search(r'pos=(\([^)]*\))', line)[1]) for i, line in group])
print('PASS: native class exclusion, identity, ownership, flags and count reconciliation; no removal claim.')
