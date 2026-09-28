from pathlib import Path
import hashlib, json, subprocess, sys
root=Path.cwd()
out=root/'scratch/cargo_smokes'
out.mkdir(exist_ok=True)
files=sorted((root/'tools/devmods/train_hub/tests').glob('*_smoke.py'))
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
results=[]
for p in files:
    cmd=[sys.executable,str(p.relative_to(root))]
    result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
    log='command: '+subprocess.list2cmdline(cmd)+'\nHEAD: '+head+'\n'+result.stdout+result.stderr
    (out/(p.stem+'.txt')).write_text(log,encoding='utf8',newline='\n')
    results.append({'test':p.name,'exit':result.returncode})
    print(p.name,result.returncode,flush=True)
summary={'command':'python scratch/run_cargo_smokes.py','head':head,
         'filter':'sorted(Path("tools/devmods/train_hub/tests").glob("*_smoke.py"))',
         'total':len(results),'pass':sum(r['exit']==0 for r in results),
         'fail':sum(r['exit']!=0 for r in results),'members':results}
assert summary['total']==summary['pass']+summary['fail']==len(summary['members'])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps(summary,indent=2))
sys.exit(any(r['exit']!=0 and r['test']!='traffic_smoke.py' for r in results))
