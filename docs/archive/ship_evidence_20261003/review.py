"""One-shot read-only source/provenance census; writes a new receipt only."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'CLAUDE.md').is_file())
OUT=Path(__file__).resolve().parent
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rg(pattern,root):
    command=['rg','-n',pattern,str(root)]
    p=subprocess.run(command,text=True,encoding='utf-8',capture_output=True)
    assert p.returncode in (0,1),p.stderr
    return {'command':command,'exit':p.returncode,'members':p.stdout.splitlines(),'count':len(p.stdout.splitlines())}
r={'command':'python docs/archive/ship_evidence_20261003/review.py','head':git(ROOT,'rev-parse','HEAD'),'source_hashes':{},'searches':{}}
for repo in ['SMR-BugFixPack','SMR-BugFixPack-TestKit','SMR-CommunitySaveRescue','SMR-Assets']:
    r[repo]={'head':git(ROOT.parent/repo,'rev-parse','HEAD'),'status':git(ROOT.parent/repo,'status','--short')}
pattern='GetServiceDescription|sectionVisitors|sectionFoodService|IsOneOfInterests|ServiceInterestsList|GetServiceList|InfopanelSection|ipBuilding'
for name,root in [('D15_positive',ROOT/'Code/Opt_ServiceInterestTags.lua'),('D15_fixpack',ROOT.parent/'SMR-BugFixPack/Code')]:r['searches'][name]=rg(pattern,root)
assert r['searches']['D15_positive']['count']>0 and r['searches']['D15_fixpack']['count']==0
rescue=ROOT.parent/'SMR-CommunitySaveRescue/Code'
r['searches']['rescue_dials']=rg('SMRFixPack_DroneSpeedDial|SMRFixPack_DroneCarryDial|SMRFixPack_ack_notworking',rescue)
r['searches']['rescue_trains']=rg('SMROptIn_hub_upgrades|SMROptInTrainHub6|SMROptInElevator|SMROptIn_station_rows',rescue)
assert r['searches']['rescue_dials']['count']>0 and r['searches']['rescue_trains']['count']==0
r['searches']['probe_sweep']=rg('TEMPORARY',ROOT/'Code')
r['searches']['kit_sweep']=rg('TEMPORARY',ROOT.parent/'SMR-BugFixPack-TestKit/Code')
assert not r['searches']['probe_sweep']['count'] and not r['searches']['kit_sweep']['count']
for name in ['Opt_AcknowledgedWarnings.lua','Opt_DroneStatDials.lua']:
    assert not git(ROOT,'diff','f3d6c78','--','Code/'+name)
assert not git(ROOT,'diff','102aad0','--','Code/Opt_ServiceInterestTags.lua')
code=re.findall(r'"(Code/[^"\n]+\.lua)"',(ROOT/'metadata.lua').read_text(encoding='utf-8'))
assert code and len(code)==len(set(code))
for name in code+['metadata.lua','items.lua','LICENSE']:
    r['source_hashes'][name]=digest(ROOT/name)
sources=['trainhub/blender/hub_skeleton.py','trainhub/blender/build_workfile.py','trainhub/blender/tripo_cleanup.py','trainhub/blender/paint_concept.py','trainhub/blender/export_prep.py','elevatorstation/blender/depot_build.py','elevatorstation/blender/depot_geometry.py','elevatorstation/blender/depot_paint.py','elevatorstation/blender/depot_bake_ao.py']
for name in sources:r['source_hashes']['SMR-Assets/'+name]=digest(ROOT.parent/'SMR-Assets'/name)
for p in sorted((ROOT/'SourceData').rglob('*.lua')):r['source_hashes'][p.relative_to(ROOT).as_posix()]=digest(p)
r['limits']='Source census and exact file hashes. Not a native test, code-copy attribution proof or asset licensing receipt.'
with (OUT/'review_receipt.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({'head':r['head'],'counts':{k:v['count'] for k,v in r['searches'].items()},'hash_members':len(r['source_hashes'])},indent=2))
