"""Prepare a scratch arming manifest; run canonical arm_leg.ps1 to install it.

--original is the enabled-mod order captured from a boot log's `saved=` line. `setup` enables the
workbench for the next boot, present_on removes the fix pack, absent_on puts the captured order
back and `restored` confirms it.
Expected spot and attachment counts come from the SMR-Assets export proof.
"""
import argparse
import collections
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools/doccheck.py').is_file())
PROOF = ROOT.parent / 'SMR-Assets/arboretum/blender/export/model_proof.json'
FIXPACK = 'SMR_CommunityFixPack'
p = argparse.ArgumentParser()
p.add_argument('leg', choices=['setup', 'present_off', 'present_on', 'absent_off', 'absent_on', 'restored'])
p.add_argument('--original', help='comma-separated enabled-mod order captured from the first leg')
a = p.parse_args()
scratch = ROOT / 'scratch/arboretum_boot'
scratch.mkdir(parents=True, exist_ok=True)
WORKBENCH = 'SMR_CommunityOptInPack_Workbench'
if not a.original:
    raise SystemExit('pass --original: the enabled-mod order captured from a boot log')
original = a.original.split(',')
# The workbench is requested first, as its own boots did; the game still loads its dependency first.
enabled = [WORKBENCH] + [m for m in original if m != WORKBENCH]
next_order = {'setup': enabled, 'present_on': [m for m in enabled if m != FIXPACK],
              'absent_on': original}.get(a.leg)
mode = a.leg if a.leg in ('setup', 'restored') else 'check'

def lua_table(mapping):
    return '{' + ', '.join(f'[{json.dumps(k)}] = {v}' for k, v in sorted(mapping.items())) + '}'


proof = json.loads(PROOF.read_text(encoding='utf-8'))
spots = collections.Counter(s['name'] for s in proof['spots'] if not s['name'].startswith('Plant'))
prefix = 'ARB_MODE = ' + json.dumps(mode) + '\n'
prefix += 'ARB_ORIGINAL = {' + ', '.join(map(json.dumps, original)) + '}\n'
prefix += 'ARB_ON = ' + str(a.leg.endswith('_on')).lower() + '\n'
prefix += 'ARB_FIXPACK = ' + str(not a.leg.startswith('absent')).lower() + '\n'
prefix += 'ARB_NEXT_ORDER = ' + ('{' + ', '.join(map(json.dumps, next_order)) + '}' if next_order else 'false') + '\n'
prefix += 'ARB_ATTACHED = ' + lua_table(proof['attached']) + '\n'
prefix += 'ARB_SPOTS = ' + lua_table(spots) + '\n'
payload = prefix + Path(__file__).with_name('boot.lua.txt').read_text(encoding='utf-8')
(scratch / '98_ArboretumBoot.lua.txt').write_bytes(payload.encode('ascii'))
manifest = dict(leg='arboretum-' + a.leg, kit=str(ROOT.parent / 'SMR-BugFixPack-TestKit'),
                park=str(scratch), stripPattern='Code/98_ArboretumBoot',
                bootSymbol='ArboretumBoot.Boot', symbolNamespace='ArboretumBoot',
                permanent=['Code/80_AgentSlots.lua'],
                mustNotBeListed=['Code/96_AutoRunFlag.lua'],
                mustNotBeListedWhy='menu-only load checks',
                bannedPatterns=['SaveGame\\s*\\(', 'LoadGame\\s*\\('],
                payloads=[dict(src='98_ArboretumBoot.lua.txt', dst='98_ArboretumBoot.lua', selfDrives=True)])
(scratch / 'leg.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(scratch / 'leg.json')
