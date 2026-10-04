import ast, hashlib, json
from pathlib import Path
root=Path.cwd()
reader=root/'docs/archive/ship_residual_20261003/read_residual_v2.py'
tree=ast.parse(reader.read_text(encoding='utf-8'))
bad=root/'scratch/residual_invalid_fixture.sav'
bad.write_bytes(b'negative control: not Save B')
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SOURCE' for t in node.targets):
        node.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(str(bad))],keywords=[])
try:
    exec(compile(ast.fix_missing_locations(tree),str(reader),'exec'),{'__file__':str(reader)})
except AssertionError as e:
    assert str(e)=='wrong exact-B fixture', str(e)
    print('PASS: changed fixture rejected before decoder or graph claims')
else:
    raise AssertionError('bad fixture accepted')
r=json.loads((root/'docs/archive/ship_residual_20261003/receipt.json').read_text())
assert hashlib.sha256(reader.read_bytes()).hexdigest()==r['reader_sha256']
assert sum(x['count'] for x in r['candidate_modifier_id_tokens'].values())==r['candidate_modifier_id_occurrences']
assert all(len(x['offsets'])==x['count'] for x in r['tokens'].values())
print('PASS: archived reader hash and receipt member totals reconcile')
paths=['docs/agent/prompts/Launch_Prep/'+x for x in ['01A_RESIDUAL_READ_high.md','02_SHIP_TESTS_medium.md','03_STORE_AND_SITE_medium.md','04_FINAL_AUDIT_high.md']]
import subprocess
sizes=[]
for p in paths:
    before=len(subprocess.check_output(['git','show','0ff4a85:'+p]))
    after=len(Path(p).read_bytes())
    sizes.append({'path':p,'before_bytes':before,'after_bytes':after,'delta':after-before})
result={'command':'python scratch/residual_checks.py','head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'negative_fixture':'rejected before decoder','receipt_members':'reconciled','sizes':sizes,'before_total':sum(x['before_bytes'] for x in sizes),'after_total':sum(x['after_bytes'] for x in sizes)}
Path('scratch/residual_checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
