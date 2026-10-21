"""Run the complete inherited baseline and verify the obsolete audit's expected stop."""
from pathlib import Path
import os
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf8')
env=dict(os.environ,PYTHONIOENCODING='utf-8')
print('COMMAND:',subprocess.list2cmdline([sys.executable,*sys.argv]),flush=True)
print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),flush=True)
cmd=[sys.executable,'docs/archive/station_rows_audit_20261021/baseline.py']
print('COMMAND:',subprocess.list2cmdline(cmd),flush=True)
p=subprocess.run(cmd,capture_output=True,encoding='utf8',env=env)
print(p.stdout,end='',flush=True); print(p.stderr,end='',flush=True); print('EXIT:',p.returncode,flush=True)
assert p.returncode==0
token='[TrainHub] transient claim failed'
old=Path('docs/archive/station_rows_audit_20261021/baseline_output.txt').read_text(encoding='utf8')
assert p.stdout.count(token)==old.count(token)==1
print('PASS inherited caught diagnostic: exact token count current=1 old=1; both baseline runs exit0',flush=True)
cmd=[sys.executable,'docs/archive/station_rows_audit_20261021/adversarial.py']
print('COMMAND (expected historical assertion failure):',subprocess.list2cmdline(cmd),flush=True)
p=subprocess.run(cmd,capture_output=True,encoding='utf8',env=env)
print(p.stdout,end='',flush=True); print(p.stderr,end='',flush=True); print('EXIT:',p.returncode,flush=True)
assert p.returncode==1 and 'assertion failed' in p.stderr and '[string "<python>"]:90:' in p.stderr
assert 'COUNTEREXAMPLE people-only tail' not in p.stdout
print('PASS expected stop: first historical A1 assertion at chunk90; later first-audit assertions not reached. Positive replacements are native_math.py/ui_check.py.',flush=True)
