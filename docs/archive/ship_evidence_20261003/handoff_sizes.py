from pathlib import Path
import subprocess,json
names=['01_SHIP_EVIDENCE_high.md','01A_RESIDUAL_READ_high.md','02_SHIP_TESTS_medium.md','03_STORE_AND_SITE_medium.md','04_FINAL_AUDIT_high.md','README.md']
rows=[]
for name in names:
    p='docs/agent/prompts/Launch_Prep/'+name
    old=subprocess.run(['git','show','82369ec:'+p],capture_output=True)
    before=len(old.stdout) if old.returncode==0 else 0
    after=len(Path(p).read_bytes()) if Path(p).exists() else 0
    rows.append({'file':name,'before':before,'after':after,'delta':after-before})
print(json.dumps({'command':'python scratch/ship_handoff_sizes.py','base':'82369ec','head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'method':'raw byte length of git base blob and final worktree file; absence zero','members':rows,'before':sum(r['before'] for r in rows),'after':sum(r['after'] for r in rows),'delta':sum(r['delta'] for r in rows)},indent=2))
