from pathlib import Path
import hashlib, json, subprocess, sys, difflib
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'CLAUDE.md').is_file())
sys.path.insert(0, str(ROOT.parent / 'SMR-BugFixPack/tools'))
import patchcheck
A = ROOT.parent / 'SMR-Shared/SMR-SrcArchive'
OUT = ROOT / 'docs/archive/ship_evidence_20261003'
OUT.mkdir(exist_ok=True)
def sha(b): return hashlib.sha256(b).hexdigest()
r = {'command':'python scratch/ship_evidence_capture.py', 'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(), 'build':patchcheck.installed_build(), 'archives':{}, 'packs':{}}
for ver in ['1.1.0.403908','1.1.1.405907','1.1.1.406343']:
    body=patchcheck.manifest_body(str(A/ver/'Src')).encode()
    assert body==(A/ver/'MANIFEST.sha256').read_bytes()
    r['archives'][ver]={'digest':sha(body),'files':len(body.splitlines())}
assert r['archives']['1.1.1.405907']==r['archives']['1.1.1.406343']
assert r['build']=='25579348'
src=A/'1.1.1.406343/Src'
for pack,prefixes,prepend in [('Lua.fpk',('Lua/','CommonLua/'),''),('Data.fpk',('Data/',),'Data/')]:
    p=Path(patchcheck.INSTALL)/'Packs'/pack
    entries={prepend+k:v for k,v in patchcheck.fpk_entries(str(p)).items()}
    members=[]
    for f in sorted(src.rglob('*')):
        if not f.is_file(): continue
        rel=f.relative_to(src).as_posix()
        if not rel.startswith(prefixes): continue
        data=f.read_bytes()
        assert rel in entries, rel
        assert data==entries[rel],rel
        members.append({'path':rel,'sha256':sha(data),'bytes':len(data)})
    assert members
    r['packs'][pack]={'pack_sha256':sha(p.read_bytes()),'decoded_entries':len(entries),'matched':len(members),'members':members}
    if pack=='Lua.fpk':
        r['revision']=entries['Lua/Config/_LuaRevision.lua'].decode()
        assert '406343' in r['revision']
    print(pack, 'matched',len(members),flush=True)
changed=['Lua/RequiresMaintenance.lua','Lua/Colony.lua','Lua/MarsGameEffects.lua','Lua/X/BuildMenu.lua']
diff=[]
for rel in changed:
    old=(A/'1.1.0.403908/Src'/rel).read_text(encoding='utf-8').splitlines(True)
    new=(src/rel).read_text(encoding='utf-8').splitlines(True)
    d=list(difflib.unified_diff(old,new,fromfile='1.1.0.403908/'+rel,tofile='1.1.1.406343/'+rel))
    assert d
    diff.extend(d)
with (OUT/'source_receipt.json').open('x',encoding='utf-8',newline='\n') as f: json.dump(r,f,indent=2);f.write('\n')
with (OUT/'moved_bodies.diff').open('x',encoding='utf-8',newline='\n') as f:f.writelines(diff)
old=ROOT/'docs/archive/train_final_result_20261003'
receipt=json.loads((old/'receipt.json').read_text())
for record in receipt['logs'].values():
    b=(old/record['file']).read_bytes()
    assert sha(b)==record['sha256']
    assert len(b.decode('utf-8-sig').splitlines())==record['lines']
    assert all(record['counts'][k]==len(v) for k,v in record['members'].items())
print('Train final receipt hashes and membership counts verified')
print(json.dumps({k:v for k,v in r.items() if k not in ['packs']},indent=2))
