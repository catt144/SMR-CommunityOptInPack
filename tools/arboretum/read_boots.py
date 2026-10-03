"""Validate complete menu-load logs, including positive controls for every negative."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'docs/archive/arboretum_20261003'
records = []
for leg in ('present_off', 'present_on', 'absent_off', 'absent_on', 'restored'):
    path = ARCHIVE / (leg + '.log')
    data = path.read_bytes()
    text = data.decode('utf-8-sig')
    on = str(leg.endswith('_on')).lower()
    present = not leg.startswith('absent')
    expected = ('SMR_CommunityFixPack,' if present else '') + 'SMR_CommunityFixPackTestKit,SMR_CommunityOptInPack'
    required = ['Lua revision: 406343', '[ARBORETUM-BOOT] loaded=' + expected,
                '[ARBORETUM-BOOT] saved=' + expected,
                f'[ARBORETUM-BOOT] cold active={on} expected={on} fixpack={str(present).lower()}',
                '[ARBORETUM-BOOT] template=SMROptInArboretum entity=GardenLargeCP3 resource=Seeds stat_scale=1000',
                '[ARBORETUM-BOOT] live=false reconciled=false', '[ARBORETUM-BOOT] live=true reconciled=true',
                '[ARBORETUM-BOOT] result=true', '*** Debug::Done()']
    for marker in required:
        if marker not in text:
            raise SystemExit(f'{leg}: missing positive control {marker}')
    errors = re.findall(r'^.*(?:\[LUA ERROR\]|\[ARBORETUM-BOOT\] result=false|\[ARBORETUM-BOOT\] FAIL).*$', text, re.M)
    if errors:
        raise SystemExit(f'{leg}: unexpected errors {errors}')
    braze = [line for line in text.splitlines() if line.startswith('[Braze]') and re.search(r'error|Failed',line)]
    lines = {marker: next(i for i,line in enumerate(text.splitlines(),1) if marker in line) for marker in required}
    records.append(dict(leg=leg, sha256=hashlib.sha256(data).hexdigest(), controls=lines,
                        lua_error_lines=len(errors), braze_error_lines=len(braze), braze_members=braze))
print(json.dumps(dict(command='python tools/arboretum/read_boots.py',
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    scope='menu loads only; working diff; matrix used handle 11, restored uses collision-free handle 12',
    records=records), indent=2))
