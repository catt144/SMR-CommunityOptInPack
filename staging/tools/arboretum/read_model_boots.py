"""Validate the staffed custom-model menu-load logs (2026-10-05), with positive controls for every negative.

python staging/tools/arboretum/read_model_boots.py [log-folder]

Reads docs/archive/arboretum_model_20261005staffed/ (or the folder given). Two check legs, option on:
fix pack present (present_on_nochange) and absent (absent_on). Every probe section must pass,
including `reservation`, which must equal the Large Garden's on all six shape kinds. attempt1_present_on
is a retained FAILED attempt: it must still show its failures and is never counted as a leg. No
option-off leg and no `restored` leg ran this round; the output says so. One startup Lua error from
the editor's EntitySpec post-load is a recorded open finding: exactly that line, once, in each leg
that loads the workbench, and nowhere else. Prints the receipt JSON on stdout.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools/doccheck.py').is_file())
ARCHIVE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs/archive/arboretum_model_20261005staffed'
BOOT = '[ARBORETUM-BOOT] '
KNOWN_ERROR = "[LUA ERROR] CommonLua/Editor/ArtSpecEditor.lua:573: attempt to call a nil value (global 'EntitySpecPathToEntity')"
PASSING = ['mods', 'template', 'entities', 'spots', 'attaches', 'lights', 'reservation', 'consumption', 'toggles']
OTHER = 'qL8sA2m'  # the owner's other loaded mod, kept in every order
STATES = ('CropHerb:true:idle/idle2/idle3/idle4 CropRapeseed_SmallFarm:true:idle/idle2/idle3/idle4 '
          'CropQuinoa_SmallFarm:true:idle/idle2/idle3/idle4 CropPumpkinFarmArm_SmallFarm:true:idle/idle2/idle3 '
          'CropCucumber:true:idle/idle2/idle3/idle4/idle5 CropPotatoes_SmallFarm:true:idle/idle2/idle3/idle4 '
          'CropApples:true:idle/idle2/idle3/idle4')
SHAPES = ('build', 'combined', 'interior', 'inverse_build', 'outline', 'peripheral')
ATTACH_CLASSES = ('BushArm_03=1,Bush_01=2,Bush_02=2,Bush_03=23,Bush_04=22,Bush_05=4,Bush_06=22,DecorInt_03=6,'
                  'DomeDoorEntrance_01=1,DomeDoorEntrance_02=1,LampGroundInner_01=10,LampInt_02=4,LampInt_03=6,'
                  'SMROptInArboretumGlass=1,TreeArm_02=2,TreeArm_03=2,Tree_03=2,Tree_05=4')
PACK_FIRST = f'SMR_CommunityFixPack,SMR_CommunityFixPackTestKit,SMR_CommunityOptInPack,{OTHER},SMR_CommunityOptInPack_Workbench'
LEGS = {  # leg -> (fix pack present, loaded order, next_order the probe staged)
    'present_on_nochange': (True, PACK_FIRST,
                            f'SMR_CommunityOptInPack_Workbench,SMR_CommunityFixPackTestKit,SMR_CommunityOptInPack,{OTHER}'),
    'absent_on': (False, f'SMR_CommunityOptInPack,SMR_CommunityOptInPack_Workbench,SMR_CommunityFixPackTestKit,{OTHER}',
                  PACK_FIRST),
}
records = []
for leg, (present, loaded, next_order) in LEGS.items():
    data = (ARCHIVE / (leg + '.log')).read_bytes()
    text = data.decode('utf-8-sig')
    lines = text.splitlines()
    boot = [l.split(BOOT, 1)[1] for l in lines if BOOT in l]
    required = ['Lua revision: 406343', '*** Debug::Done()',
                BOOT + 'loaded=' + loaded,
                BOOT + f'cold active=true expected=true fixpack={str(present).lower()}',
                BOOT + 'template=SMROptInArboretum entity=SMROptInArboretumPavilion stock_spot=Resourcepile'
                       ' prg_class=GardenNatural_Large resource=Seeds stat_scale=1000',
                BOOT + 'entities valid; build_surface pavilion=false donor=false',
                BOOT + 'spots Autolight=26,Cropbed=3,Door=1,Doorleaf=2,Glazing=1,Resourcepile=1,Specimen=2,'
                       'Top=1,Visitwarmup=10,Workdrone=1,Yard=1',
                BOOT + 'attaches total=115 ' + ATTACH_CLASSES,
                BOOT + 'lights parsed=26 emissive=1 registry=26',
                BOOT + 'own consumption overrides=CanConsume,Consume_Workshift',
                BOOT + 'staffing max_workers=2 automation=1 auto_performance=100 capacity=14 store=30000 type=5',
                BOOT + 'upgrade1=SMROptInArboretum_ServiceBots', BOOT + 'upgrade2=SMROptInArboretum_SeasonalBlooms',
                BOOT + 'upgrade3=SMROptInArboretum_RareSpecimens', BOOT + 'crops ' + STATES,
                BOOT + 'consumption methods=41 native=true default_spot=Resourcepile2',
                BOOT + 'live=false reconciled=false', BOOT + 'live=true reconciled=true',
                BOOT + 'next_order=' + next_order,
                BOOT + 'result=true detail=menu entity/template/toggle checks only; gameplay NOT RUN']
    required += [BOOT + f'section={name} ok=true' for name in PASSING]
    for marker in required:
        if marker not in text:
            raise SystemExit(f'{leg}: missing positive control {marker}')
    # Reservation: every shape kind equal between pavilion and Large Garden, and 10 hexes.
    res = [l for l in boot if l.startswith('reservation pavilion/donor ')]
    if len(res) != 1:
        raise SystemExit(f'{leg}: reservation line count {len(res)}')
    pairs = dict(re.findall(r'(\w+)=(\d+/\d+)', res[0].split('own_outline')[0]))
    if sorted(pairs) != sorted(SHAPES) or any(a != b for a, b in (v.split('/') for v in pairs.values())):
        raise SystemExit(f'{leg}: reservation shapes not all equal {pairs}')
    if pairs['combined'] != '10/10' or pairs['outline'] != '10/10' or 'own_outline=true' not in res[0]:
        raise SystemExit(f'{leg}: reservation is not the Large Garden 10 hexes {res[0]}')
    # Seven crops, each valid, none INVALID, every one with idle and idle2.
    crops = next(l for l in boot if l.startswith('crops ')).split()[1:]
    if len(crops) != 7 or any('INVALID' in c or not c.split(':')[2].startswith('idle/idle2') for c in crops):
        raise SystemExit(f'{leg}: crop entities {crops}')
    errors = [l for l in lines if '[LUA ERROR]' in l or BOOT + 'FAIL' in l]
    if errors != [KNOWN_ERROR]:
        raise SystemExit(f'{leg}: unexpected errors {errors}')
    failed = [l for l in lines if 'ok=false' in l and BOOT in l]
    if failed:
        raise SystemExit(f'{leg}: failed sections {failed}')
    braze = [l for l in lines if l.startswith('[Braze]') and re.search(r'error|Failed', l)]
    controls = {m: next(i for i, l in enumerate(lines, 1) if m in l) for m in required}
    records.append(dict(leg=leg, sha256=hashlib.sha256(data).hexdigest(), controls=controls,
                        lua_error_lines=len(errors), known_error_lines=1, braze_error_lines=len(braze)))
# The retained failed attempt: it must still read as failed (a pass here would mean the wrong file).
retained = []
for path in sorted(ARCHIVE.glob('attempt*.log')):
    data = path.read_bytes()
    lines = data.decode('utf-8-sig').splitlines()
    failed = [l.split(BOOT, 1)[1] for l in lines if 'ok=false' in l and BOOT in l]
    if not failed or BOOT + 'result=false detail=failed sections: mods,consumption' not in '\n'.join(lines):
        raise SystemExit(f'{path.name}: retained failed attempt does not show its failure {failed}')
    retained.append(dict(log=path.name, sha256=hashlib.sha256(data).hexdigest(), counted_as_leg=False,
                         failed_sections=failed))
print(json.dumps(dict(
    command='python staging/tools/arboretum/read_model_boots.py',
    head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    scope='menu loads of the working tree; entities loaded by the probe with the game\'s own '
          'WaitDelayedLoadEntities; gameplay NOT RUN',
    not_run=['option-off legs (present_off, absent_off): did not run this round',
             'restored leg: did not run this round; the next_order lines are the only order evidence'],
    findings=['reservation: pavilion equals the Large Garden, 10 hexes, all six shape kinds equal',
              'OPEN: one startup Lua error per workbench boot, not a pass: ' + KNOWN_ERROR,
              'store=30000 is the engine value (stat_scale 1000), i.e. 30',
              'ServiceWorkplace is enforced by the probe (section=consumption ok=true), not printed as a class name'],
    retained_failed_attempts=retained,
    records=records), indent=2))
