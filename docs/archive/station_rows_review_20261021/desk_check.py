"""Independent review: native transfer bodies with request/route doubles, no game run."""
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools/trains/hub/tests'))
from distribution_smoke import ARCHIVE, runtime

print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), flush=True)
current = ARCHIVE.parents[2] / '1.1.1.406343/Src/Lua'
for name in ['Units/Train.lua', 'Buildings/Station.lua',
             'Buildings/MultiResourceDepot.lua', 'Buildings/MultiResourceCubeVisuals.lua']:
    assert (ARCHIVE / name).read_bytes() == (current / name).read_bytes(), name
lua = runtime()
lua.execute(r'''
debug.setmetatable(nil, {__len=function() return 0 end})
local D = SMROptInTrainDistribution
function plain(a,b,ac,bc)
    local t,s,d=fixture(a,b,ac,bc or ac)
    d.hub=false; d.GetTrainExportFloor=nil; d.HubTrackGraph=nil; d.nodes=nil
    function t:GetEmptyStorage()
        local n=0; for _,v in pairs(self.stockpiled_amount) do n=n+v end
        return 42000-n
    end
    D.Refresh()
    return t,s,d
end
-- One shared station, two distinct lines; resource-independent production code.
for _,mode in ipairs({'balanced','import','export','untouched'}) do
    local t,s,j=plain(60,0,60)
    local far=station(0,60); far.handle=3; far.city=s.city
    local right={members={j,far},trains={}}
    function right:GetDestStation(st) return st==j and far or j end
    local u=setmetatable({current_station=j,track=right,city=s.city,
        stockpiled_amount={},assigned_resources={},units={},is_stopping=false,
        GetEmptyStorage=t.GetEmptyStorage,AddResource=t.AddResource,
        LogCargo=t.LogCargo,PushDestructor=t.PushDestructor,PopDestructor=t.PopDestructor}, {__index=Train})
    right.trains={u}; s.city.train_track_routes[right]=right.members
    UIColony.labels.Station={s,j,far}; D.Refresh()
    if mode~='untouched' then assert(D.Set(j,'Metals',mode,20)) end
    checked_transfer(t); deliver(t,j); checked_transfer(u); deliver(u,far)
    local expected=mode=='untouched' and 15000 or 0
    assert(stock(far)==expected,mode)
    print('JUNCTION mode='..mode..' source='..(stock(s)/1000)..' junction='..(stock(j)/1000)..' far='..(stock(far)/1000))
end
for _,mode in ipairs({'import20','import100','untouched','export_import100'}) do
    local t,s,d=plain(60,0,60)
    if mode~='untouched' then assert(D.Set(d,'Metals','import',mode=='import20' and 20 or 100)) end
    if mode=='export_import100' then assert(D.Set(s,'Metals','export',0)) end
    checked_transfer(t); deliver(t,d)
    local expected=mode=='import20' and 12000 or mode=='export_import100' and 42000 or 30000
    assert(stock(d)==expected,mode)
    print('IMPORT mode='..mode..' delivered='..stock(d)/1000)
end
for _,rows_on in ipairs({false,true}) do
    local t,s,d=plain(250,0,250,60)
    SMROptInPack={IsActive=function() return rows_on end}
    SMRElevatorDepot={IsDepot=function(o) return o==s end, HubEntry=function() return {mode='export',percent=0} end}
    s.transport_policy.Metals='accept'; s.desired_amount=false; s:SetDesiredAmount(10000)
    checked_transfer(t); deliver(t,d)
    assert(stock(d)==(rows_on and 10000 or 42000))
    if not rows_on then
        t.current_station=s; checked_transfer(t); deliver(t,d)
        assert(stock(d)==48000)
    end
    print('DEPOT rows_on='..tostring(rows_on)..' depot='..(stock(s)/1000)..' receiver='..(stock(d)/1000))
    SMRElevatorDepot=nil; SMROptInPack=nil
end
-- No hub and row modules off: both enabled stations with zero desire do not balance.
local t,s,d=plain(250,0,250,60)
SMROptInPack={IsActive=function() return false end}
for _,st in ipairs({s,d}) do st.transport_policy.Metals='accept'; st.desired_amount=false; st:SetDesiredAmount(10000) end
checked_transfer(t); assert((t.stockpiled_amount.Metals or 0)==0)
assert(s.supply.Metals:GetDesiredAmount()==0)
s.transport_policy.Metals='send'; s.desired_amount=false; s:SetDesiredAmount(10000)
assert(s.supply.Metals:GetDesiredAmount()==250000 and s.demand.Metals:GetDesiredAmount()==0)
checked_transfer(t); assert(t.stockpiled_amount.Metals==42000)
print('POLICY accept/accept blocks balance; send opens gate AND changes request desired amounts')
SMROptInPack=nil
''')
print('PASS review scenarios; NOT RUN engine scheduling, saves, UI, player-save reproduction', flush=True)
