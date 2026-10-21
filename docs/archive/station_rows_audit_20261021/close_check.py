"""Audit close-out invariants and count reconciliation. Run from repo root."""
from pathlib import Path
import re
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf8')
print('COMMAND:',subprocess.list2cmdline([sys.executable,*sys.argv]),flush=True)
print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),flush=True)
def git(*args): return subprocess.check_output(['git',*args],text=True,encoding='utf8')
assert not git('diff','83149ea','--','Code/','tools/trains/')
print('PASS shipping Code/ and tools/trains/ unchanged from83149ea including working tree')
paths=git('ls-tree','-r','--name-only','83149ea','--','Code/').splitlines()
tokens=sorted({t for p in paths for t in re.findall(r'\bSMR(?:FixPack|OptIn)_[A-Za-z0-9_]+',git('show','83149ea:'+p))})
print('PERSISTED-NAME TOKEN FILTER: regex \\bSMR(?:FixPack|OptIn)_[A-Za-z0-9_]+ over git ls-tree83149ea Code/ -> git show each member')
print('UNIQUE TOKENS:',len(tokens))
for i,t in enumerate(tokens,1): print(i,t)
prompt='STATION_ROWS_RELAY_AUDIT_high.md'
assert not Path('docs/agent/prompts',prompt).exists()
assert prompt not in Path('docs/agent/prompts/README.md').read_text(encoding='utf8')
assert '### OI-53 ' not in Path('docs/PLAYTEST_CHECKLIST.md').read_text(encoding='utf8')
report=Path('docs/agent/reports/STATION_ROWS_RELAY_20261021.md').read_text(encoding='utf8')
assert '## 16 · Independent build audit' in report
assert '**Verdict: corrections needed' in report
assert 'NOT RUN:' in report
for name in ['D16','D18']:
    text=Path(f'docs/agent/bugs/{name}.md').read_text(encoding='utf8')
    assert re.search(r'^status: "tested-attended"$',text,re.M)
    assert 'Audited 2026-10-21 (Codex, GPT-6 per transcript): corrections needed' in text
print('PASS verdict/model/limits filed; D16/D18 status tags retained; OI-53/prompt/map row consumed')
outbox=Path('docs/agent/prompts/perma/RELEASE_OUTBOX.md').read_text(encoding='utf8')
assert 'Fixes three Workshop reports' not in outbox
assert 'independent audit requires' in outbox
assert 'No named player\'s save is verified fixed' in outbox
print('PASS outbox names correction outcome and limits instead of pending audit or verified player fixes')
assert not git('diff','--name-only','--','docs/archive/station_rows_review_20261021/','docs/archive/station_rows_second_review_20261021/','docs/archive/station_rows_proposal_20261021/','docs/archive/station_rows_proposal_20261021b/')
print('PASS prior evidence archives unchanged')
