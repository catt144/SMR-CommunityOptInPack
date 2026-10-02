"""Run every train-hub *_smoke.py and preserve command/HEAD/exit receipts.

An existing destination is refused so an archived receipt can never be rewritten.
The traffic-smoke baseline is separately run against this brief's starting commit.
Any smoke failure leaves this command red, including a matching baseline failure.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    kit_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent/'SMR-BugFixPack-TestKit',text=True).strip()
    print('command:',subprocess.list2cmdline([sys.executable,*sys.argv]),flush=True)
    print('HEAD:',head,'TestKit HEAD:',kit_head,flush=True)
    rows=[]
    for path in sorted(HERE.glob('*_smoke.py')):
        command=[sys.executable,str(path.relative_to(ROOT))]
        result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                              text=True,encoding='utf8',errors='replace')
        receipt=f'command: {subprocess.list2cmdline(command)}\nHEAD: {head}\nTestKit HEAD: {kit_head}\nexit: {result.returncode}\n\n'+result.stdout
        (args.output/(path.stem+'.txt')).write_text(receipt,encoding='utf8')
        rows.append({'test':path.name,'exit':result.returncode})
        print(path.name,result.returncode,flush=True)
    with tempfile.TemporaryDirectory(prefix='train_bay_baseline_') as tmp:
        baseline=Path(tmp)/'20_TrainHub.lua'
        baseline.write_bytes(subprocess.check_output(['git','show','d0f2b8a:tools/devmods/train_hub/Code/20_TrainHub.lua'],cwd=ROOT))
        script="import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); import traffic_smoke as t; t.SOURCE=Path(sys.argv[2]); t.run()"
        command=[sys.executable,'-c',script,str(HERE),str(baseline)]
        result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                              text=True,encoding='utf8',errors='replace')
        (args.output/'traffic_baseline.txt').write_text(
            f'command: {subprocess.list2cmdline(command)}\nbaseline: d0f2b8a\nexit: {result.returncode}\n\n'+result.stdout,encoding='utf8')
        baseline_matches=result.returncode!=0 and '-10800 != 0' in result.stdout
    summary={'head':head,'testkit_head':kit_head,'filter':'tools/trains/hub/tests/*_smoke.py',
             'total':len(rows),'passed':sum(r['exit']==0 for r in rows),
             'failed':sum(r['exit']!=0 for r in rows),'members':rows,
             'traffic_baseline_matches':baseline_matches}
    assert summary['passed']+summary['failed']==summary['total']
    (args.output/'results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
    print(json.dumps(summary,indent=2),flush=True)
    return 1 if summary['failed'] or not baseline_matches else 0


if __name__=='__main__':
    raise SystemExit(main())
