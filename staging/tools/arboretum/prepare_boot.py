"""Prepare a scratch arming manifest; run canonical arm_leg.ps1 to install it."""
import argparse
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools/doccheck.py').is_file())
p = argparse.ArgumentParser()
p.add_argument('leg', choices=['present_off', 'present_on', 'absent_off', 'absent_on', 'restored'])
a = p.parse_args()
scratch = ROOT / 'scratch/arboretum_boot'
scratch.mkdir(parents=True, exist_ok=True)
original = ['SMR_CommunityFixPack', 'SMR_CommunityFixPackTestKit', 'SMR_CommunityOptInPack']
if Path(__file__).resolve().parents[2].name == 'staging':
    original.append('SMR_CommunityOptInPack_Workbench')
next_order = original[1:] if a.leg == 'present_on' else original if a.leg == 'absent_on' else None
prefix = 'ARB_ON = ' + str(a.leg.endswith('_on')).lower() + '\n'
prefix += 'ARB_FIXPACK = ' + str(not a.leg.startswith('absent')).lower() + '\n'
prefix += 'ARB_NEXT_ORDER = ' + ('{' + ', '.join(map(json.dumps, next_order)) + '}' if next_order else 'false') + '\n'
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
