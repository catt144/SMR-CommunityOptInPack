"""Recover named L5 logs once, byte-for-byte, and write a bounded line inventory."""
import hashlib, json, os, re, subprocess
from pathlib import Path
root=Path.cwd()
dest=root/'docs/archive/drones_l6_20260925'
dest.mkdir(exist_ok=True)
src=Path(os.environ['APPDATA'])/'Surviving Mars Relaunched/logs'
tokens=['20260924-12.35.05','20260924-17.07.20','20260924-17.18.02','20260924-21.01.51','20260924-21.44.09','20260925-13.34.56','20260925-13.43.07','20260925-14.14.01']
receipt={'command':'python scratch/drones_l6_logs.py','head':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),'scope':'late recovered original logs, not committed by L5; no mod source hash in logs','logs':{}}
patterns={'repair':r'\[TrainHubDev\] repair (dispatched|relaunched|done):',
 'save_load':r'^\[SMRTK\] SMRTK_(SAVE|LOAD) ',
 'failure':r'(?i)persist.*(error|fail)|C function expected|luaSPersist|\[LUA ERROR\]|Invalid spot',
 'identity':r'^Lua revision:|Stopping the game threads from the Lua side',
 'control_line':r'print\(7/2|3\s+3\.5\s+integer'}
for token in tokens:
    matches=list(src.glob('Mars.exe-'+token+'-*.log')); assert len(matches)==1,(token,matches)
    p=matches[0]; raw=p.read_bytes(); target=dest/p.name
    assert not target.exists(),str(target)
    target.write_bytes(raw)
    assert p.read_bytes()==raw==target.read_bytes(), 'source moved during copy'
    lines=raw.decode('utf-8-sig',errors='replace').splitlines()
    hits={k:[{'line':i,'text':s} for i,s in enumerate(lines,1) if re.search(pattern,s)] for k,pattern in patterns.items()}
    assert any('Lua revision: 405907' in s for s in lines)
    assert any('Stopping the game threads from the Lua side with exit code 0.' in s for s in lines)
    receipt['logs'][p.name]={'source':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'line_total':len(lines),'hits':hits,'counts':{k:len(v) for k,v in hits.items()}}
receipt['log_total']=len(receipt['logs']); receipt['byte_total']=sum(v['bytes'] for v in receipt['logs'].values())
target=dest/'log_receipt.json'; assert not target.exists()
target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='logs'},indent=2))
for n,v in receipt['logs'].items(): print(n,json.dumps(v['counts']))
