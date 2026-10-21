"""Source and record controls for the second relay audit. Run from repository root."""
from pathlib import Path
import hashlib
import re
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf8')
print('COMMAND:',subprocess.list2cmdline([sys.executable,*sys.argv]),flush=True)
print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),flush=True)
def git(*args): return subprocess.check_output(['git',*args],text=True,encoding='utf8')
def show(rev,p): return git('show',rev+':'+p)
assert not git('diff','3aa5402','--','Code/','tools/trains/')
print('PASS git diff3aa5402 -- Code/ tools/trains/: empty including working tree')
p='Code/StationRows_40_TrainDistribution.lua'
old=show('5ba8f3f',p); current=Path(p).read_text(encoding='utf8')
for start,end in [('local function branch_need(', 'local function child_need('),('local function child_need(', 'local function '),('local function train_view(', '\n-- '),('\tlocal rows = hub and rawget(hub, FIELD)\n\trows = rows and rows[st]', '-- Build from real state')]:
    def extract(s):
        a=s.index(start)
        return s[a:s.index(end,a+len(start))]
    assert extract(old)==extract(current),start
    print('PASS unchanged from5ba8f3f:',start.splitlines()[0])
ui='Code/StationRows_45_TrainDistributionUI.lua'
before=show('83149ea',ui); now=Path(ui).read_text(encoding='utf8')
def helpblock(s): return s[s.index('local help = {'):s.index('local local_help = {')]
assert helpblock(before)==helpblock(now)
print('PASS hub-network help byte-identical to83149ea')
assert 'rows[res] = { mode = mode, percent = percent }' in old and 'rows[res] = { mode = mode, percent = percent }' in current
print('PASS saved row writer unchanged {mode,percent}; Default clears active data, adds no mode string')
def token_set(rev):
    paths=git('ls-tree','-r','--name-only',rev,'--','Code/').splitlines()
    return {t for p in paths for t in re.findall(r'\bSMR(?:FixPack|OptIn)_[A-Za-z0-9_]+',show(rev,p))}
a,b=token_set('optin-v1.0.3'),token_set('3aa5402')
assert a==b
print('PASS unique persisted-name token regex set unchanged since release; members=',len(b))
for i,t in enumerate(sorted(b),1): print(i,t)
cmd=['rg','-n','SMRFixPack','Code/']
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8'); assert r.returncode==0
print('COMMAND:',subprocess.list2cmdline(cmd)); print(r.stdout,end='')
comments=strings=0
for line in r.stdout.splitlines():
    source=line.split(':',2)[2]
    if source.strip().startswith('--'): comments+=1
    else: strings+=1
    code=re.sub(r'--.*$', '',source)
    code=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', '',code)
    assert 'SMRFixPack' not in code
print(f'PASS executable-reference scan on plain decoded Code/: {len(r.stdout.splitlines())} matching lines = {comments} comments + {strings} existing string constants; zero executable matches')
decl=r'^\s*(?:function\s+([\w.:]+)|([\w.]+)\s*=\s*function)'
paths=git('diff','--name-only','optin-v1.0.3','3aa5402','--','Code/').splitlines()
print('RELEASE DIFF MEMBERS:',len(paths),paths)
for p in paths:
    names=lambda s:{a or b for a,b in re.findall(decl,s,re.M)}
    new=names(show('3aa5402',p))-names(show('optin-v1.0.3',p))
    assert new<={'D.Clear','OnMsg.TrainRoutesRebuilt'}
    print('PASS new named callable assignments',p,sorted(new),'no new vanilla wrapper target')
assert 'D.WaterFill = water_fill' in current
print('PASS D.WaterFill is an export of a synchronous local helper, not a vanilla wrap')
for id in ['D16','D18']:
    p=f'docs/agent/bugs/{id}.md'
    assert re.search(r'^status: "tested-attended"$',Path(p).read_text(encoding='utf8'),re.M)
    assert re.search(r'^status: "tested-attended"$',show('optin-v1.0.3',p),re.M)
    print('PASS status unchanged since release:',id,'tested-attended')
# Pin record claims to the audited HEAD so this script remains replayable after
# the audit updates their status and clarifies the wording.
rev='aa7dac1'
for p,pattern in [('docs/agent/reports/STATION_ROWS_RELAY_20261021.md',r'The current station is always|cost\s+is one route walk per click|Not measured on a large colony'),('docs/agent/bugs/D16.md',r'\*\*R7\*\*|Corrected 2026-10-21'),('docs/agent/bugs/D18.md',r'\*\*R7\*\*|Corrected 2026-10-21'),('docs/agent/prompts/perma/RELEASE_OUTBOX.md',r'Fixes three Workshop reports|No named player|second audit \(OI-54\)')]:
    source=show(rev,p)
    matches=list(re.finditer(pattern,source))
    print('RECORD SCAN:',rev,p,'filter=',pattern,'matches=',len(matches))
    for m in matches:
        line=source.count('\n',0,m.start())+1
        print(line,repr(m.group()))
    if p.endswith('D18.md'): assert '**R7**' not in source; print('RECORD QUALIFICATION: D18 has R1-R6 and correction pointer; R7 verbatim is in D16/spec, not D18')
spec=show(rev,'docs/agent/reports/TRAIN_LOGISTICS_DESIGN_20260917.md')
assert 'R7' in spec
print('PASS R7 canonical record in D16/spec; no owner ruling reopened')
archive=Path.cwd().parent/'SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/Lua'
for name,pattern in [('TrainTransport.lua',r'route\[idx\].working|function ForEachStationAlongTrack'),('Units/Train.lua',r'function Train:LoadTrain|function Train:TransferCargo|self:TransferCargo\(')]:
    cmd=['rg','-n',pattern,str(archive/name)]
    p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8'); assert p.returncode==0
    print('COMMAND:',subprocess.list2cmdline(cmd)); print(p.stdout,end='')
print('PASS structural/contract controls; NOT RUN engine/save/UI/player-save behavior',flush=True)

# The original audit's actual-depot Target/HubEntry control is independent of
# its now-obsolete record-presence assertions. Reuse that bounded section only.
import runpy
ROOT=Path.cwd()
prior=(ROOT/'docs/archive/station_rows_audit_20261021/contract.py').read_text(encoding='utf8')
section=prior.split('# Read the real depot target/HubEntry after the full wiring harness executes.',1)[1]
exec(compile(section,'audit1_depot_target_control','exec'),globals())
