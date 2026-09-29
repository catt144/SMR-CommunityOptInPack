"""Archived vanilla heater/upgrade bodies; native circle rasterization is a desk double."""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from lupa import LuaError
import cargo_upgrade_smoke as cargo

ARCHIVE = cargo.ROOT.parent / 'SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua'


def extract(path, name):
    text = (ARCHIVE / path).read_text(encoding='utf8')
    return re.search(r'^function ' + re.escape(name) + r'\(.*?^end\n', text, re.M | re.S)[0]


SETUP = r'''
BaseHeater={}; SubsurfaceHeaterBase={heat=5*const.MaxHeat}; HeatGrid={}
const.GridSpacing=1000
function table.iequals(a,b)
 for i=1,math.max(#a,#b) do if a[i]~=b[i] then return false end end
 return true
end
function Heat_AddCircle(grid,x,y,radius,heat,border)
 table.insert(grid,{x=x,y=y,radius=radius,heat=heat,border=border})
end
function HeatGrid:OnHeatGridChanged() self.changed=(self.changed or 0)+1 end
function HeatGrid:sample(x,y)
 local heat=0 -- cold-wave background
 for _,v in ipairs(self.grid_target) do
  if (x-v.x)^2+(y-v.y)^2<=v.radius^2 then heat=heat+v.heat end
 end
 return math.min(const.MaxHeat,math.max(0,heat))
end
'''
for method in ['GetHeatCenter', 'ApplyHeat', 'ApplyForm']:
    SETUP += extract('Heater.lua', 'BaseHeater:' + method)
SETUP += extract('Heat.lua', 'HeatGrid:ApplyHeatForm')
SETUP += extract('Buildings/Building.lua', 'Building:ApplyUpgradeModifiers')

FIXTURE = r'''
local surface={heat_grid=setmetatable({heaters={},grid_target={},map_width=1000000,map_height=1000000}, {__index=HeatGrid})}
local original_hub=hub
hub=function(...)
 local h=original_hub(...)
 h.map=surface; h.work_radius=15
 function h:GetVisualPosXYZ() return self:GetPos():xy() end
 return h
end
'''

CASES = r'''
local grid=surface.heat_grid
local function check(h,on)
 local x,y=h:GetVisualPosXYZ()
 assert((grid.heaters[h]~=nil)==on,'heater registration state')
 if on then
  local info=grid.heaters[h]
  assert(info[1]==-SubsurfaceHeaterBase.heat and info[4]==h.work_radius*const.GridSpacing and info[5]==0,'heater geometry')
  assert(grid:sample(x+h.work_radius*const.GridSpacing,y)>90,'warm service edge')
 else
  assert(grid:sample(x,y)<=90,'cold after removal')
 end
 assert(grid:sample(x+(h.work_radius+1)*const.GridSpacing,y)<=90,'outside stays cold')
end
-- The cargo scenario ended with a rebuilt, off owner. Only it may switch cargo.
check(both,false)
SelectedObj=both; both:ToggleUpgradeOnOff(CARGO); check(both,true)
both.working=false; check(both,true)
local changes=grid.changed
OnMsg.LoadGame(); check(both,true)
assert(grid.changed==changes,'load is idempotent')
both.work_radius=19; OnMsg.LoadGame(); check(both,true)
both:ToggleUpgradeOnOff(CARGO); check(both,false)
both:ToggleUpgradeOnOff(CARGO); check(both,true)
both:StopUpgradeModifiers(); check(both,false) -- Building:Done's actual bulk path
both:ApplyUpgradeModifiers(); check(both,true)
both.destroyed=true; OnMsg.BuildingDemolished(both); check(both,false)
OnMsg.LoadGame(); check(both,false)
local rebuilt=hub(230,201000); rebuilt:ApplyCopyParams({})
check(rebuilt,true)
both:StopUpgradeModifiers(); check(rebuilt,true) -- old ruin cleanup cannot remove new heat
SelectedObj=rebuilt; rebuilt:ToggleUpgradeOnOff(CARGO); check(rebuilt,false)
local underground={heat_grid=false}
rebuilt.map=underground; rebuilt:ToggleUpgradeOnOff(CARGO) -- no heat grid: safe
'''


def run(code):
    cargo.run(code, CASES, SETUP, FIXTURE)


if __name__ == '__main__':
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]))
    print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip())
    code = cargo.SOURCE.read_text(encoding='utf8')
    print('source_sha256:', hashlib.sha256(cargo.SOURCE.read_bytes()).hexdigest())
    run(code)
    print('PASS heater lifecycle, actual radius, edge/outside, bulk cleanup, load, rebuild, no-grid')
    mutations = {
        'no heat': ('hub:ApplyHeat(on)', 'hub:ApplyHeat(false)'),
        'wrong range': ('return self.work_radius * const.GridSpacing', 'return 20 * const.GridSpacing'),
        'bulk cleanup': ('table.pack(Building.StopUpgradeModifiers(self, ...))', 'table.pack()'),
    }
    for name, (before, after) in mutations.items():
        assert before in code, name
        try:
            run(code.replace(before, after, 1))
        except LuaError as exc:
            assert any(s in str(exc) for s in ['heater registration', 'heater geometry', 'outside stays cold', 'assertion failed']), str(exc)
            print('PASS mutation rejected:', name)
        else:
            raise AssertionError('mutation survived: ' + name)
