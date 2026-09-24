"""D14(a): source-copy and native-wait permanent regression. No native save claim.

--source accepts the pre-fix file for the failing control. The collector body is
executed from the 1.1.1 archive, with coroutine.yield as a native C waiter.
"""
import argparse
from pathlib import Path
import subprocess
import sys

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
DONOR_TOOLS = ROOT.parent / 'SMR-BugFixPack/tools'
sys.path.insert(0, str(DONOR_TOOLS))
from luafn import find_bodies, read_lines

ARCHIVE = ROOT.parent / 'SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, default=ROOT / 'tools/devmods/train_hub/Code/20_TrainHub.lua')
args = parser.parse_args()
text = args.source.read_text(encoding='utf8')
marker = 'local function hub_dwell_timeout(' if 'local function hub_dwell_timeout(' in text else 'local function hub_dwell_train('
section = text[text.index(marker):text.index('local hub_work_radius')]
lua = LuaRuntime()
lua.execute('''
SMROptInTrainFloor={HubDwellTime=6000}; OnMsg={}; CObject={}
Train={LoadTrain=function() end, UnloadTrain=function() end}
WaitWakeup=coroutine.yield; native_wait=WaitWakeup
function AllMapsForEach() error('must never query maps at startup') end
''')
lua.execute('local Floor=SMROptInTrainFloor\n' + section + '\ninstall_hub_dwell()')
lines = read_lines(ARCHIVE / 'CommonLua/Core/cthreads.lua')
start, end = find_bodies(lines, r'^function OnMsg.PersistGatherPermanents\(')[0]
lua.execute('\n'.join(lines[start:end + 1]))
lua.execute('''
local permanents={}; OnMsg.PersistGatherPermanents(permanents,'save')
assert(permanents['cthread.WaitWakeup']==native_wait,
 'native C waiter lost its permanent: deficit and MarkFlight stacks cannot save')
assert(WaitWakeup==native_wait, 'global waiter was replaced')
local thread=coroutine.create(function() WaitWakeup(6000) end)
assert(coroutine.resume(thread)); assert(coroutine.status(thread)=='suspended')
OnMsg.PersistGatherPermanents(permanents,'load')
assert(permanents['cthread.WaitWakeup']==native_wait)
''')

# Refuse drift in either copied command outside the ownership guard and deadline.
source_lines = text.splitlines()
vanilla_lines = read_lines(ARCHIVE / 'Lua/Units/Train.lua')
for name, previous in [('LoadTrain', 'previous_load'), ('UnloadTrain', 'previous_unload')]:
    a, b = find_bodies(source_lines, rf'^\tfunction Train:{name}\(\)')[0]
    body = '\n'.join(line[1:] if line.startswith('\t') else line for line in source_lines[a:b+1])
    guard = f'''\t-- FIX: only our station uses the copied command.
\tif not IsValid(self.current_station) or not IsKindOf(self.current_station, "SMROptInTrainHubBase") then
\t\treturn {previous}(self)
\tend
'''
    assert guard in body
    body = body.replace(guard, '')
    body = body.replace('\t-- FIX: shorten this train\'s deadline, preserving the native waiter.\n', '')
    body = body.replace('hub_dwell_timeout(self)', 'const.HourDuration / 5')
    a, b = find_bodies(vanilla_lines, rf'^function Train:{name}\(\)')[0]
    assert body == '\n'.join(vanilla_lines[a:b+1]), name + ' changed outside the declared fix'

print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]))
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
print('PASS: 1.1.1.405907 native waiter permanent, unchanged global, suspended C waiter, exact command copies')
print('Native save/reload and train restart remain owner checks.')
