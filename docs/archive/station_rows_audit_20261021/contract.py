"""Bounded source, contract, record and baseline controls; run from repo root."""
from pathlib import Path
import hashlib
import os
import re
import runpy
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf8')

ROOT=Path.cwd()
print('COMMAND:', subprocess.list2cmdline([sys.executable,*sys.argv]), flush=True)
print('HEAD:', subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(), flush=True)
def git(*args): return subprocess.check_output(['git',*args],text=True,encoding='utf8')
def show(rev,path): return git('show',f'{rev}:{path}')
def body(text,start,end): return text[text.index(start):text.index(end,text.index(start))]
path='Code/StationRows_40_TrainDistribution.lua'
before=show('5ba8f3f',path); after=show('83149ea',path)
assert not git('diff','83149ea','HEAD','--','Code/','tools/trains/')
print('PASS git diff 83149ea HEAD -- Code/ tools/trains/: empty')
prototype=ROOT/'docs/archive/station_rows_proposal_20261021b/StationRows_40_TrainDistribution.proposal.lua'
norm=lambda s: [re.sub(r'[ \t]*--.*$', '',l).strip() for l in s.splitlines() if re.sub(r'[ \t]*--.*$', '',l).strip()]
assert norm(show('a731a20',path))==norm(prototype.read_text(encoding='utf8'))
print('PASS a731a20/prototype equal after comment/blank normalization; prototype SHA256:',hashlib.sha256(prototype.read_bytes()).hexdigest())
assert show('optin-v1.0.3',path)==before
print('PASS pre-port file equals optin-v1.0.3; git blob SHA256:',hashlib.sha256(before.encode()).hexdigest())
for start,end in [('local function branch_need(', 'local function child_need('), ('local function child_need(', 'local function '), ('local function train_view(', '-- Module A without a hub:'), ('\tlocal rows = hub and rawget(hub, FIELD)\n\trows = rows and rows[st]', '-- Build from real state')]:
    # child_need's next marker must start past its own declaration.
    if start=='local function child_need(':
        extract=lambda s: s[s.index(start):s.index(end,s.index(start)+len(start))]
    else: extract=lambda s: body(s,start,end)
    assert extract(before)==extract(after),start
    print('PASS unchanged bytes:',start.strip())
assert 'rows[res] = { mode = mode, percent = percent }' in before and 'rows[res] = { mode = mode, percent = percent }' in after
persist_pattern=r'\bSMR(?:FixPack|OptIn)_[A-Za-z0-9_]+'
def tokens(rev):
    paths=git('ls-tree','-r','--name-only',rev,'--','Code/').splitlines()
    return {t for p in paths for t in re.findall(persist_pattern,show(rev,p))}
old,new=tokens('5ba8f3f'),tokens('83149ea')
assert old==new
print('PASS persisted-name token set unchanged:',len(new),'unique tokens; added=',sorted(new-old),'removed=',sorted(old-new))
# Shipping Lua is plain source (no compressed inputs in this scope). Count the
# positive side; doccheck supplies the wider wrapper/Require gate.
p=subprocess.run(['rg','-n','SMRFixPack','Code/'],capture_output=True,text=True,encoding='utf8')
assert p.returncode in (0,1)
print('COMMAND: rg -n SMRFixPack Code/; exit=',p.returncode)
print(p.stdout,end='')
print('PRESENCE:',len(p.stdout.splitlines()),'lines; each is an existing persisted string; unchanged token set alone is not an executable-reference proof')
for line in p.stdout.splitlines():
    text=line.split(':',2)[-1]
    code=re.sub(r'--.*$', '',text)
    code=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', '',code)
    assert 'SMRFixPack' not in code,line
decl=r'^\s*(?:function\s+([\w.:]+)|([\w.]+)\s*=\s*function)'
for p in ['Code/StationRows_40_TrainDistribution.lua','Code/StationRows_45_TrainDistributionUI.lua','Code/ElevatorDepot_10_ElevatorDepot.lua']:
    names=lambda s: {a or b for a,b in re.findall(decl,s,re.M)}
    additions=names(show('83149ea',p))-names(show('5ba8f3f',p))
    assert additions <= {'D.Clear','OnMsg.TrainRoutesRebuilt'},(p,additions)
    print('PASS new named method assignments',p,sorted(additions),'(no new vanilla wrapper target)')
src=ROOT.parent/'SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/Lua'
for name,pattern in [('TrainTransport.lua','ForEachConnectedTrack\\(callback|ForEachTrainInRoute|TrainRoutesRebuilt|routes\\[segment\\] = route|function ForEachStationAlongTrack'),('Buildings/Station.lua','resource_storing.tga'),('City.lua','train_track_routes = false')]:
    command=['rg','-n',pattern,str(src/name)]
    p=subprocess.run(command,capture_output=True,text=True,encoding='utf8')
    assert p.returncode==0
    print('COMMAND:',subprocess.list2cmdline(command)); print(p.stdout,end='')
    print('PRESENCE:',len(p.stdout.splitlines()),'matching lines in decoded archived source; build1.1.1.406343')
for name in ['D16','D18']:
    p=f'docs/agent/bugs/{name}.md'
    oldstatus=re.search(r'^status:.*$',show('5ba8f3f',p),re.M)[0]
    newstatus=re.search(r'^status:.*$',Path(p).read_text(encoding='utf8'),re.M)[0]
    assert oldstatus==newstatus=='status: "tested-attended"'
    print('PASS unchanged status',name,newstatus)
for name,pattern in [('docs/agent/prompts/perma/RELEASE_OUTBOX.md','Fixes three Workshop reports'),('Code/StationRows_45_TrainDistributionUI.lua','never deliver here|never take it away|At 100 nothing can pass'),('docs/agent/bugs/D16.md','cycles Balanced'),('docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md','cycles four states')]:
    p=subprocess.run(['rg','-n',pattern,name],capture_output=True,text=True,encoding='utf8')
    assert p.returncode==0
    print('COMMAND:',subprocess.list2cmdline(['rg','-n',pattern,name])); print(p.stdout,end='')
    print('RECORD/TEXT REVIEW: quoted above for the verdict; presence is not correctness')

# The click seam predates the relay build. Execute the same leaving-hub
# control on both unmodified revisions, then refresh before click as control.
sys.path.insert(0,str(ROOT/'tools/trains/hub/tests'))
import distribution_smoke as h
import distribution_ui_smoke as ui
for rev in ['5ba8f3f','83149ea']:
    work=ROOT/'scratch/station_audit_versions'/rev
    (work/'Code').mkdir(parents=True,exist_ok=True)
    for name in ['StationRows_10_TrainFloor.lua','StationRows_40_TrainDistribution.lua','StationRows_45_TrainDistributionUI.lua']:
        (work/'Code'/name).write_text(show(rev,'Code/'+name),encoding='utf8')
    h.MOD=work; ui.MOD=work
    u=ui.ui_runtime()
    for refresh in [False,True]:
        u.globals().refresh_first=refresh
        u.execute(r'''
local D=SMROptInTrainDistribution
local t,s,h=fixture(0,0,60,250); local dlg=dialog(s); OnMsg.DialogOpen(dlg)
assert(D.Set(s,'Metals','export',0)); rawset(s,D.LOCAL_FIELD,{Metals={mode='import',percent=70}})
h.nodes[s]=nil
if refresh_first then D.Refresh() end
s:ToggleAcceptResource('Metals',false)
local e=rawget(s,D.LOCAL_FIELD).Metals
if refresh_first then assert(not s:IsResourceEnabled('Metals') and e.percent==70)
else assert(s:IsResourceEnabled('Metals') and e.mode=='import') end
print('UI SEAM refresh='..tostring(refresh_first)..' local='..e.mode..'/'..e.percent..' enabled='..tostring(s:IsResourceEnabled('Metals')))
''')
    print('PASS seam provenance/control revision',rev,flush=True)

# Read the real depot target/HubEntry after the full wiring harness executes.
env=runpy.run_path(str(ROOT/'tools/trains/depot/tests/wiring_smoke.py'))
d=env['lua']
d.execute(r'''
local D=SMRElevatorDepot
local s,u=D.PairOf(); assert(s and u)
rawset(s,'SMROptIn_depot_targets',nil); rawset(u,'SMROptIn_depot_targets',nil)
assert(D.SetRow(s,'Metals','import'))
assert(D.Target(s,'Metals')==100 and not select(2,D.Target(s,'Metals')))
assert(D.HubEntry(s,'Metals').percent==100 and D.HubEntry(u,'Metals').percent==0)
assert(D.SetRow(s,'Metals','export'))
assert(D.Target(s,'Metals')==0 and D.HubEntry(s,'Metals').percent==0 and D.HubEntry(u,'Metals').percent==100)
assert(D.SetTarget(s,'Metals',37)); assert(D.Target(s,'Metals')==37)
assert(D.SetRow(s,'Metals','import') and D.Target(s,'Metals')==37)
''')
print('PASS real depot Target/HubEntry: absent Import100/Export0; underground inverse100/0; explicit37 survives row changes; no actual save load',flush=True)
print('NOT RUN: engine scheduling/saves/drones/pixels/player saves.',flush=True)
