"""Reproduce stocked hub cubes erased by a transient distribution capacity.

Archived TransferCargo/AddResource/SetCountColumnAlloc execute with request and
cube doubles. Distribution's real allocator stays loaded and unmodified.
"""
import subprocess
import sys
from lupa import LuaError
import distribution_smoke as distribution
from pallet_visuals_smoke import extract, integer_divisions

SOURCE=distribution.MOD/'Code/20_TrainHub.lua'
START='-- Cube rendering needs physical storage'
END='-- Owner report 2026-09-27'


def setup(lua, fix):
    src=(distribution.ARCHIVE/'Buildings/MultiResourceCubeVisuals.lua').read_text(encoding='utf8')
    names=['SetCount','SetCountColumnAlloc','AddResource','UpdateVisualCount']
    bodies='\n'.join(extract(src,'MultiResourceCubeVisuals:'+n) for n in names)
    lua.execute('ResourceScale=const.ResourceScale\n'+integer_divisions(bodies,1,'cube bodies'))
    depot=(distribution.ARCHIVE/'Buildings/MultiResourceDepot.lua').read_text(encoding='utf8')
    lua.execute(extract(depot,'MultiResourceDepotBase:OnResourceCountChanged'))
    lua.execute(r'''
MultiResourceDepotBase.SetCount=MultiResourceCubeVisuals.SetCount
MultiResourceDepotBase.SetCountColumnAlloc=MultiResourceCubeVisuals.SetCountColumnAlloc
MultiResourceDepotBase.UpdateVisualCount=MultiResourceCubeVisuals.UpdateVisualCount
SMROptInTrainHubBase=setmetatable({}, {__index=Station})
function PlaceObjectIn(_,_,init)
 local c={resource=init.resource}
 function c:SetAngle() end
 function c:SetAttachOffset(p) self.pos=p end
 return c
end
function DoneObject(o) o.invalid=true end
function install_visuals(h)
 setmetatable(h,{__index=SMROptInTrainHubBase})
 h.visual_cubes={Metals={},Food={}}
 h.stockpiled_amount={Metals=stock(h),Food=0}
 h.AddResource=MultiResourceCubeVisuals.AddResource
 function h:GetMap() return {} end
 function h:Attach() end
 function h:OnAfterRequestUpdate() end
 function h:GetCubePosRelative(i) if i<171 then return i end end
 for _,requests in ipairs({h.supply,h.demand}) do for _,r in pairs(requests) do
  function r:AddAmount(n) self.actual=self.actual+n; self.target=self.target+n end
 end end
 h:UpdateVisualCount('Metals')
end
''')
    if fix:
        lua.execute(fix)


CASES=r'''
local t,s,h=fixture(0,220,120,480)
install_visuals(h)
assert(#h.visual_cubes.Metals==171,'fixture starts visibly full')
t.current_station=h
checked_transfer(t)
assert(stock(h)==210000 and t.stockpiled_amount.Metals==10000,'same distribution transfer')
assert(#h.visual_cubes.Metals==171,'stocked hub lost its cubes during zero-capacity allocation view')
assert(h:GetMaxStorage('Metals')==480000,'outside draw: real capacity remains')
h:AddResource(-200000,'Metals')
assert(stock(h)==10000 and #h.visual_cubes.Metals==10,'drain draws exact remaining stock')
h:AddResource(200000,'Metals')
assert(#h.visual_cubes.Metals==171,'refill stops at existing height cap')
h.max_storage_per_resource=240000
h:UpdateVisualCount('Metals')
assert(#h.visual_cubes.Metals==171,'base capacity has same visual ceiling')
'''


def run(fix):
    lua=distribution.runtime(lambda runtime:setup(runtime,fix))
    lua.execute(CASES)
    # An error in native drawing must not leave the receiver in drawing mode.
    if fix:
        lua.execute(r'''
local t,s,h=fixture(0,220,120,480)
install_visuals(h)
local previous=MultiResourceDepotBase.SetCount
MultiResourceDepotBase.SetCount=function() error('draw fault') end
local ok,err=pcall(h.SetCount,h,200000,'Metals')
assert(not ok and tostring(err):find('draw fault'))
MultiResourceDepotBase.SetCount=previous
-- A later wrapper still governs allocation reads outside rendering.
MultiResourceDepotBase.GetMaxStorage=function() return 1234 end
assert(h:GetMaxStorage('Metals')==1234,'failed draw leaked physical capacity scope')
''')


def main():
    print('command:',subprocess.list2cmdline([sys.executable,*sys.argv]),flush=True)
    print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],cwd=distribution.ROOT,text=True).strip())
    code=SOURCE.read_text(encoding='utf8')
    fix=code[code.index(START):code.index(END)] if START in code else None
    run(fix)
    print('PASS stocked cube display survives actual distribution transfer; draw/error/height controls')
    assert fix,'missing fix'
    try:
        run(None)
    except LuaError as exc:
        assert 'stocked hub lost its cubes' in str(exc),str(exc)
        print('PASS mutation rejected: removing rendering scope erases stocked cubes')
    else:
        raise AssertionError('cube mutation survived')


if __name__=='__main__':
    main()
