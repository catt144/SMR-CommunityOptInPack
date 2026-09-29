"""Ordinary station cargo under real distribution/archived TransferCargo bodies."""
import contextlib
import io
import subprocess
import sys
from unittest.mock import patch
from pathlib import Path
from lupa import LuaError
import distribution_smoke as distribution
from cargo_view_smoke import setup

SOURCE = distribution.MOD / 'Code/40_TrainDistribution.lua'
CASES = r'''
local t,s,h=fixture(70.4,0,120,2000)
install_visuals(s)
-- A normal Station, not a hub subclass or its display override.
setmetatable(s,{__index=Station})
assert(#s.visual_cubes.Metals==70)
assert(SMROptInTrainDistribution.Set(s,'Metals','export',20))
function t:GetEmptyStorage() return 10000 end
checked_transfer(t)
assert(stock(s)==60400 and t.stockpiled_amount.Metals==10000,'transfer unchanged')
assert(#s.visual_cubes.Metals==60,'station at 60.4/120 lost cargo cubes')
assert(s:GetMaxStorage('Metals')==120000,'physical capacity outside transfer')
s.has_visual_cubes=true; s.visual_cubes.Metals={}
OnMsg.LoadGame()
assert(stock(s)==60400 and #s.visual_cubes.Metals==60,'station saved empty display repaired on load')
-- Unmanaged stations delegate, including their original return shape.
local foreign=station(7,60)
install_visuals(foreign);setmetatable(foreign,{__index=Station})
foreign:UpdateVisualCount('Metals')
assert(#foreign.visual_cubes.Metals==7,'foreign station display')
'''

def run(code):
    original = Path.read_text
    def read(path, *args, **kwargs):
        return code if path == SOURCE else original(path, *args, **kwargs)
    with patch.object(Path, 'read_text', read), contextlib.redirect_stdout(io.StringIO()):
        lua = distribution.runtime(lambda runtime: setup(runtime, None))
        lua.execute(CASES)

def main():
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]))
    print('HEAD:', subprocess.check_output(['git','rev-parse','HEAD'],cwd=distribution.ROOT,text=True).strip())
    code=SOURCE.read_text(encoding='utf8')
    run(code)
    print('PASS normal station: export leaves 60.4/120, vanilla draws 60 cubes; foreign delegation')
    old='local row = not drawing[self] and view and view[self] and view[self][res]'
    assert code.count(old)==1
    try:
        run(code.replace(old,'local row = view and view[self] and view[self][res]'))
    except LuaError as exc:
        assert 'station at 60.4/120 lost cargo cubes' in str(exc),str(exc)
        print('PASS mutation rejected: allocation capacity leaked into station drawing')
    else:
        raise AssertionError('station display mutation survived')
    old='station:UpdateVisualCount(resource)'
    assert code.count(old)==1
    try:
        run(code.replace(old,'-- omit saved display repair'))
    except LuaError as exc:
        assert 'station saved empty display repaired on load' in str(exc),str(exc)
        print('PASS mutation rejected: saved empty station display not repaired')
    else:
        raise AssertionError('saved station display mutation survived')

if __name__=='__main__': main()
