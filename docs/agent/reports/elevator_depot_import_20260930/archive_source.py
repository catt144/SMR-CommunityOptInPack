"""Archive and verify the newly observed ModTools source version, without overwriting it.
python docs/agent/reports/elevator_depot_import_20260930/archive_source.py
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = Path('A:/SteamLibrary/steamapps/common/Project Spark/ModTools/Src')
ARCHIVE_ROOT = ROOT.parent / 'SMR-Shared/SMR-SrcArchive'
DEST = ARCHIVE_ROOT / '1.1.1.406343'
ACF = Path('A:/SteamLibrary/steamapps/appmanifest_3215050.acf')
build = re.search(r'"buildid"\s+"(\d+)"', ACF.read_text(encoding='utf-8')).group(1)
assert build == '25579348', build
assert DEST.resolve().parent == ARCHIVE_ROOT.resolve()


def manifest(root):
    rows = []
    for path in sorted(root.rglob('*')):
        if path.is_file():
            rows.append((path.relative_to(root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest()))
    rows.sort()
    return ''.join(f'{digest}  {path}\n' for path, digest in rows).encode(), len(rows)


original, count = manifest(SOURCE)
if not DEST.exists():
    DEST.mkdir()
    shutil.copytree(SOURCE, DEST / 'Src')
    copied, copied_count = manifest(DEST / 'Src')
    assert copied == original and copied_count == count
    (DEST / 'MANIFEST.sha256').write_bytes(copied)
else:
    copied, copied_count = manifest(DEST / 'Src')
    assert copied == original and copied_count == count
    assert (DEST / 'MANIFEST.sha256').read_bytes() == copied
assert manifest(SOURCE)[0] == original, 'installed source changed during archive'
report = {
    'command': 'python docs/agent/reports/elevator_depot_import_20260930/archive_source.py',
    'optin_head': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'build': build, 'build_source': str(ACF), 'version': '1.1.1.406343',
    'source': str(SOURCE), 'archive': str(DEST), 'filter': 'all files recursively under Src',
    'file_count': count, 'member_manifest': str(DEST / 'MANIFEST.sha256'),
    'tree_digest': hashlib.sha256(original).hexdigest(), 'source_copy_manifest_match': True,
}
(HERE / 'archive_receipt.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(report))
