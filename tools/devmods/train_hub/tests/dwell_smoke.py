"""D14(a): snapshot waiter guard using archived collector/driver bodies.

Native persistence is mocked: owner legacy-load/new-save/reload remains required.
--source accepts a prior implementation for the failing control.
"""
from pathlib import Path
import subprocess
import argparse
import sys
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", type=Path, default=ROOT/"tools/devmods/train_hub/Code/20_TrainHub.lua")
args=parser.parse_args()
ARCHIVE = ROOT.parent/'SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src'
sys.path.insert(0, str(ROOT.parent/'SMR-BugFixPack/tools'))
from luafn import find_bodies, read_lines

def body(path, pattern):
    lines=read_lines(ARCHIVE/path)
    a,b=find_bodies(lines,pattern)[0]
    return '\n'.join(lines[a:b+1])

lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
OnMsg={}; CObject={}; empty_table={}; Platform={developer=false}
SMROptInTrainFloor={HubDwellTime=6000}; WaitWakeup=coroutine.yield; native_wait=WaitWakeup
const={HourDuration=60000}; Max=math.max; Min=math.min
function AllMapsForEach() end
function CurrentThread() return coroutine.running() end
function CanSaveGame() return true end
function ReportPersistErrors() end
''')
lua.execute(body('CommonLua/Core/cthreads.lua',r'^function OnMsg.PersistGatherPermanents\('))
lua.execute(body('CommonLua/Savegame.lua',r'^function PersistGame\('))
source=args.source.read_text(encoding='utf8')
part=source[source.index('local function hub_dwell_train('):source.index('local hub_work_radius')]
# The function resolved by legacy saves keeps its original body and upvalue uses.
legacy=subprocess.check_output(['git','show','d73d701:tools/devmods/train_hub/Code/20_TrainHub.lua'],cwd=ROOT).decode('utf8')
start='\tlocal wrapper = function(timeout, ...)'; end='\n\t_G.WaitWakeup = wrapper'
assert source[source.index(start):source.index(end)]==legacy[legacy.index(start):legacy.index(end)]
assert 'local function install_hub_save_guard()' in part, 'snapshot guard missing: native waiter remains unregistered at save'
lua.execute('local Floor=SMROptInTrainFloor\n'+part+'\ninstall_hub_dwell(); install_hub_save_guard()')
lua.execute('''
local floor=SMROptInTrainFloor
assert(floor.HubDwellInstalled and floor.HubSaveGuardInstalled)
local old_permanents={}; OnMsg.PersistGatherPermanents(old_permanents,'save')
assert(old_permanents['cthread.WaitWakeup']==floor.HubDwellWrapper)
assert(debug.getinfo(floor.HubDwellWrapper).what=='Lua')
local saved_metadata={active_mods={{id='SMR_TrainHubDev_20260918',version=49}}}
OnMsg.GatherGameMetadata(saved_metadata)
assert(saved_metadata.SMROptIn_hub_native_waiter==1)
local waited=coroutine.create(function() WaitWakeup(6000) end)
assert(coroutine.resume(waited)); assert(coroutine.status(waited)=='suspended')
local calls=0
function EngineSaveGame(filename)
    calls=calls+1
    assert(filename=='fixture/persist')
    assert(WaitWakeup==native_wait,'native waiter missing at actual snapshot')
    local permanents={}; OnMsg.PersistGatherPermanents(permanents,'save')
    assert(permanents['cthread.WaitWakeup']==native_wait)
    assert(debug.getinfo(permanents['cthread.WaitWakeup']).what=='C')
    if fail_kind=='throw' then error('snapshot exception') end
    return fail_kind
end
assert(PersistGame('fixture/')==nil)
assert(WaitWakeup==floor.HubDwellWrapper,'successful snapshot did not restore dwell')
fail_kind='disk error'; assert(PersistGame('fixture/')=='disk error')
assert(WaitWakeup==floor.HubDwellWrapper,'returned failure did not restore dwell')
fail_kind='throw'; local ok,err=pcall(PersistGame,'fixture/')
assert(not ok and err:find('snapshot exception',1,true))
assert(WaitWakeup==floor.HubDwellWrapper,'thrown failure did not restore dwell')
fail_kind=nil
local legacy={active_mods={{id='SMR_TrainHubDev_20260918',version=49}}}
OnMsg.PreLoadGame(legacy)
local load_permanents={}; OnMsg.PersistGatherPermanents(load_permanents,'load')
assert(load_permanents['cthread.WaitWakeup']==old_permanents['cthread.WaitWakeup'])
OnMsg.UnpersistEnd()
assert(WaitWakeup==floor.HubDwellWrapper)
OnMsg.PreLoadGame(saved_metadata)
load_permanents={}; OnMsg.PersistGatherPermanents(load_permanents,'load')
assert(load_permanents['cthread.WaitWakeup']==native_wait,'new save got legacy Lua mapping')
OnMsg.UnpersistEnd()
assert(WaitWakeup==floor.HubDwellWrapper)
OnMsg.PreLoadGame({active_mods={}})
assert(WaitWakeup==native_wait,'ordinary native save got legacy Lua mapping')
OnMsg.UnpersistEnd('load failed')
assert(WaitWakeup==floor.HubDwellWrapper,'failed load did not restore dwell')
local foreign=function() end; WaitWakeup=foreign
local previous_calls=calls
assert(PersistGame('fixture/'):find('cancelled',1,true))
assert(calls==previous_calls and WaitWakeup==foreign,'conflicting waiter captured under wrong metadata')
''')
print('command:', subprocess.list2cmdline([sys.executable,*sys.argv]))
print('HEAD',subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
print('PASS: snapshot mapping, old/new/native load selection, save return/error and failed-load restoration, foreign conflict rejection')
print('LIMIT: no native serialization; ambiguous unmarked pre-wrapper hub saves are not classified')
