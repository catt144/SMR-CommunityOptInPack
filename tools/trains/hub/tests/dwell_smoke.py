"""D14(a), owner 2026-10-23: no Lua replacement of the native WaitWakeup.

Scans every shipped Lua file for an assignment to WaitWakeup, then runs the
hub's metadata handler beside the archived permanents collector. Native
persistence is not exercised. --source substitutes the hub file, so a prior
implementation (git show f08918d:Code/TrainHub_20_TrainHub.lua) is the failing control.
"""
from pathlib import Path
import argparse
import re
import subprocess
import sys
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
HUB = ROOT/'Code/TrainHub_20_TrainHub.lua'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, default=HUB)
args = parser.parse_args()
ARCHIVE = ROOT.parent/'SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src'
sys.path.insert(0, str(ROOT.parent/'SMR-BugFixPack/tools'))
from luafn import find_bodies, read_lines

def body(path, pattern):
    lines = read_lines(ARCHIVE/path)
    a, b = find_bodies(lines, pattern)[0]
    return '\n'.join(lines[a:b+1])

ASSIGN = re.compile(r'''(?:\b_G\s*(?:\.\s*WaitWakeup|\[\s*["']WaitWakeup["']\s*\])\s*=(?!=)'''
                    r'''|\brawset\s*\(\s*_G\s*,\s*["']WaitWakeup["']'''
                    r'''|^\s*(?:local\s+)?function\s+WaitWakeup\b'''
                    r'''|^\s*WaitWakeup\s*=(?!=))''', re.M)
files = sorted(p for p in (ROOT/'Code').rglob('*.lua') if p.resolve() != HUB.resolve())
files.append(args.source)
hits = []
for path in files:
    text = path.read_text(encoding='utf8')
    for m in ASSIGN.finditer(text):
        hits.append(f'{path}:{text.count(chr(10), 0, m.start())+1}: {m.group(0).strip()}')
print(f'scanned {len(files)} Lua file(s) for WaitWakeup assignments: {len(hits)} hit(s)')
for h in hits:
    print('  ' + h)
assert not hits, 'a shipped file replaces the native WaitWakeup'

source = args.source.read_text(encoding='utf8')
part = source[source.index('local function install_hub_art_spec_guard()'):source.index('local hub_work_radius')]
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
OnMsg = {}; empty_table = {}; g_Classes = {}; CObject = {}; Platform = {developer = false}
native_wait = coroutine.yield; WaitWakeup = native_wait
''')
lua.execute(body('CommonLua/Core/cthreads.lua', r'^function OnMsg.PersistGatherPermanents\('))
lua.execute('local Floor = {}\n' + part)
lua.execute('''
assert(OnMsg.GatherGameMetadata, 'marker writer missing')
local metadata = {}
OnMsg.GatherGameMetadata(metadata)
assert(metadata.SMROptIn_hub_native_waiter == 1, 'persisted-name row 12 marker not written')
local permanents = {}
OnMsg.PersistGatherPermanents(permanents, 'save')
assert(permanents['cthread.WaitWakeup'] == native_wait, 'save permanent is not the native waiter')
assert(WaitWakeup == native_wait, 'handler changed the global waiter')
''')
print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]))
print('HEAD', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
print('PASS: no WaitWakeup assignment in Code/; marker written; save permanent stays native')
print('LIMIT: no native serialization here; the native loads are tools/trains/hub/tests/ww_leg.json (D14)')
