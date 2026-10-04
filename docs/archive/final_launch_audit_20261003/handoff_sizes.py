"""Measure this audit's handoff bytes; stdout only, no archive mutation."""
from pathlib import Path
import json
import subprocess

base = '298ff9b76d6fca4293da9d8e5c734537cb691bd2'
paths = [
    'docs/agent/prompts/Launch_Prep/03_STORE_AND_SITE_medium.md',
    'docs/agent/prompts/Launch_Prep/03A_RELEASE_CORRECTIONS_high.md',
    'docs/agent/prompts/Launch_Prep/04_FINAL_AUDIT_high.md',
    'docs/agent/prompts/Launch_Prep/README.md',
    'docs/agent/prompts/README.md',
]
rows = []
for path in paths:
    old = subprocess.run(['git', 'show', base + ':' + path], capture_output=True)
    assert old.returncode == 0 or path.endswith('03A_RELEASE_CORRECTIONS_high.md')
    rows.append({'path': path, 'before': len(old.stdout) if old.returncode == 0 else 0,
                 'after': len(Path(path).read_bytes())})
before, after = (sum(row[key] for row in rows) for key in ('before', 'after'))
print(json.dumps({'command': 'python docs/archive/final_launch_audit_20261003/handoff_sizes.py',
                  'base': base, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                  'filter': 'exact paths in members, raw file bytes, absent before = 0',
                  'members': rows, 'before': before, 'after': after, 'delta': after - before}, indent=2))
