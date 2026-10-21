"""Run the prompt's bounded baseline and retain every command/output; repo root cwd."""
from pathlib import Path
import subprocess
import os
import sys
sys.stdout.reconfigure(encoding='utf8')
os.environ['PYTHONIOENCODING']='utf-8'

print('COMMAND:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), flush=True)
hub = 'hubless_relay hubless hubless_slots distribution_ui module_gates distribution distribution_slots distribution_departure export_pairing export_pairing_slots cargo_view crossing_witness food_stream station_visuals'.split()
depot = 'wiring props revision'.split()
commands = [[sys.executable, f'tools/trains/hub/tests/{s}_smoke.py'] for s in hub]
commands += [[sys.executable, f'tools/trains/depot/tests/{s}_smoke.py'] for s in depot]
commands += [[sys.executable, 'tools/parsecheck.py'], [sys.executable, 'tools/doccheck.py']]
results = []
for command in commands:
    print('\nCOMMAND:', subprocess.list2cmdline(command), flush=True)
    p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf8', errors='replace')
    print(p.stdout, end='', flush=True)
    print('EXIT:', p.returncode, flush=True)
    results.append((command[-1], p.returncode))
print('RECONCILED:', len(results), 'commands;', sum(rc == 0 for _, rc in results), 'passed;', sum(rc != 0 for _, rc in results), 'failed', flush=True)
for name, rc in results:
    print(rc, name, flush=True)
assert all(rc == 0 for _, rc in results)
