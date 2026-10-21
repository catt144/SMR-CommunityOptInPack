"""Audit correction A3-A5 through actual installed UI callbacks and window doubles."""
from pathlib import Path
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf8')
print('COMMAND:',subprocess.list2cmdline([sys.executable,*sys.argv]),flush=True)
print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),flush=True)
sys.path.insert(0,str(Path.cwd()/'tools/trains/hub/tests'))
import distribution_ui_smoke as ui
u=ui.ui_runtime()
u.execute(r'''
D=SMROptInTrainDistribution
local refresh=D.Refresh
refresh_calls=0
D.Refresh=function(...) refresh_calls=refresh_calls+1; return refresh(...) end
function make_ui()
    SMRElevatorDepot=nil; SMROptInPack=nil
    local t,s,h=fixture(0,0,60,250)
    local dlg,row=dialog(s); OnMsg.DialogOpen(dlg)
    return t,s,h,row
end
-- Repeat the first audit's leave/join witnesses, now expecting the active saved row.
local t,s,h,row=make_ui()
assert(D.Set(s,'Metals','export',0)); rawset(s,D.LOCAL_FIELD,{Metals={mode='import',percent=70}})
h.nodes[s]=nil; assert(D.HubFor(s)==h)
refresh_calls=0; s:ToggleAcceptResource('Metals',false)
assert(not s:IsResourceEnabled('Metals') and rawget(s,D.LOCAL_FIELD).Metals.percent==70)
assert(rawget(h,D.FIELD)[s].Metals.mode=='export' and rawget(h,D.FIELD)[s].Metals.percent==0)
assert(refresh_calls==1)
print('PASS leave-hub click: local Import70 kept disabled; dormant hub Export0 kept; refresh calls='..refresh_calls)
t,s,h,row=make_ui()
assert(D.Set(s,'Metals','import',77)); h.nodes[s]=nil; D.Refresh(); h.nodes[s]=true
assert(D.HubFor(s)==nil)
refresh_calls=0; s:ToggleAcceptResource('Metals',false)
assert(not s:IsResourceEnabled('Metals') and rawget(h,D.FIELD)[s].Metals.percent==77)
assert(rawget(s,D.LOCAL_FIELD)==nil and refresh_calls==1)
print('PASS join-hub click: hub Import77 kept disabled; dormant local absent; refresh calls='..refresh_calls)

-- Scrolls choose the newly active set and its mode in both directions.
for _,joining in ipairs({false,true}) do
    t,s,h,row=make_ui()
    assert(D.Set(s,'Metals','import',77))
    rawset(s,D.LOCAL_FIELD,{Metals={mode='export',percent=23}})
    if joining then h.nodes[s]=nil; D.Refresh(); h.nodes[s]=true else h.nodes[s]=nil end
    refresh_calls=0; row.distribution_slider:OnScroll(44)
    local active=joining and rawget(h,D.FIELD)[s].Metals or rawget(s,D.LOCAL_FIELD).Metals
    assert(active.percent==44 and active.mode==(joining and 'import' or 'export'))
    assert((joining and rawget(s,D.LOCAL_FIELD).Metals.percent or rawget(h,D.FIELD)[s].Metals.percent)==(joining and 23 or 77))
    assert(refresh_calls==2)
    print('PASS scroll joining='..tostring(joining)..' active='..active.mode..'44; dormant kept; refresh calls='..refresh_calls)
end

-- A single synchronous broadcast has a leaving source, leaving destination and
-- joining destination. Each destination must write its own now-active set.
function broadcast_fixture()
    local t,s,h,row=make_ui()
    local leave,join,depot=station(0,60),station(0,60),station(0,60)
    leave.handle=3; join.handle=4; depot.handle=5
    for _,o in ipairs({leave,join,depot}) do o.city=s.city end
    s.city.labels.Station={s,h,leave,join,depot}; UIColony.labels=s.city.labels
    h.nodes[leave]=true
    rawset(h,D.FIELD,{[s]={Metals={mode='import',percent=77}},[leave]={Metals={mode='import',percent=55}},[join]={Metals={mode='import',percent=66}}})
    rawset(s,D.LOCAL_FIELD,{Metals={mode='export',percent=23}})
    rawset(leave,D.LOCAL_FIELD,{Metals={mode='balanced',percent=33}})
    rawset(join,D.LOCAL_FIELD,{Metals={mode='import',percent=44}})
    rawset(depot,D.LOCAL_FIELD,{Metals={mode='balanced',percent=99}})
    SMRElevatorDepot={IsDepot=function(o) return o==depot end}
    D.Refresh(); h.nodes[s]=nil; h.nodes[leave]=nil; h.nodes[join]=true
    return s,h,leave,join,depot
end
for _,mode in ipairs({'export','disabled','disabled_default','default'}) do
    local s,h,leave,join,depot=broadcast_fixture()
    if mode=='disabled' or mode=='disabled_default' then s:SetAcceptResourceState('Metals','disabled') end
    if mode=='default' or mode=='disabled_default' then rawset(s,D.LOCAL_FIELD,nil) end
    refresh_calls=0; s:ToggleAcceptResource('Metals',true)
    local le=rawget(leave,D.LOCAL_FIELD); le=le and le.Metals
    local je=rawget(h,D.FIELD)[join]; je=je and je.Metals
    if mode=='default' or mode=='disabled_default' then assert(not le and not je)
    else assert(le.mode=='export' and le.percent==23 and je.mode=='export' and je.percent==23) end
    local enabled=mode=='export' or mode=='default'
    assert(leave:IsResourceEnabled('Metals')==enabled and join:IsResourceEnabled('Metals')==enabled)
    assert(rawget(h,D.FIELD)[leave].Metals.percent==55)
    assert(rawget(join,D.LOCAL_FIELD).Metals.percent==44 and rawget(h,D.FIELD)[s].Metals.percent==77)
    assert(rawget(depot,D.LOCAL_FIELD).Metals.percent==99 and depot:IsResourceEnabled('Metals'))
    assert(refresh_calls==3)
    print('PASS stale-ownership broadcast '..mode..': each destination active set updated; dormant sets/source hub/depot kept; refresh calls='..refresh_calls..' (1 entry + 2 setters)')
end
SMRElevatorDepot=nil

-- Clear retains other resources, other station entries and dormant local state.
t,s,h,row=make_ui()
local peer=station(0,60); peer.handle=3; peer.city=s.city; h.nodes[peer]=true
s.city.labels.Station={s,h,peer}; UIColony.labels=s.city.labels
assert(D.Set(s,'Metals','import',41)); assert(D.Set(s,'Food','export',13)); assert(D.Set(peer,'Metals','balanced',29))
rawset(s,D.LOCAL_FIELD,{Metals={mode='export',percent=17}})
assert(D.Clear(s,'Metals')); assert(rawget(h,D.FIELD)[s].Food.percent==13 and rawget(h,D.FIELD)[peer].Metals.percent==29)
assert(D.Clear(s,'Food')); assert(not rawget(h,D.FIELD)[s] and rawget(h,D.FIELD)[peer].Metals.percent==29)
assert(D.Clear(peer,'Metals') and rawget(h,D.FIELD)==nil)
assert(rawget(s,D.LOCAL_FIELD).Metals.percent==17)
h.nodes[s]=nil; D.Refresh(); assert(D.Clear(s,'Metals') and rawget(s,D.LOCAL_FIELD)==nil)
print('PASS A5 clear: other resource/other station/dormant set kept; final hub root and final local table removed')

-- Missing city route index is valid before rebuild; both click default and gate remain safe.
t,s,h,row=make_ui(); h.hub=false; h.GetTrainExportFloor=nil; h.HubTrackGraph=nil; h.nodes=nil
s.city.train_track_routes=false; D.Refresh()
refresh_calls=0; s:ToggleAcceptResource('Metals',false)
assert(D.Get(s,'Metals').mode=='export' and D.Get(s,'Metals').percent==0 and refresh_calls==2)
s:ToggleAcceptResource('Metals',false); assert(D.Get(s,'Metals').mode=='import' and D.Get(s,'Metals').percent==100)
print('PASS false route index: Export0 then Import100; ordinary set click refresh calls=2')

-- Qualify all changed help clauses through the installed rollover.
local far=station(0,60); far.handle=3; far.city=s.city
local a,b={members={h,s},trains={}},{members={s,far},trains={}}
s.city.train_track_routes={[a]=a.members,[b]=b.members}; s.city.labels.Station={s,h,far}; UIColony.labels=s.city.labels; D.Refresh()
assert(D.IsJunction(s))
for _,mode in ipairs({'import','export','balanced'}) do
    for _,pct in ipairs({20,100}) do
        assert(D.Set(s,'Metals',mode,pct)); local tip=s:ResourceRolloverText('Metals')
        assert(tip:find('passes through',1,true) and not tip:find('never',1,true))
        if mode=='import' then assert(tip:find('take none of that amount away',1,true)) end
        if mode=='export' then assert(tip:find('bring nothing for its own use',1,true)) end
        assert((tip:find('At 100 nothing',1,true)~=nil)==(pct==100 and mode~='export'))
    end
end
print('PASS A4 rollover: joining Import/Export keep-amount clauses; relay line; Import/Balanced100 warning; Export100 no full-reserve warning')
assert(not D.ui_error and not D.error)
''')
print('NOT RUN: large-colony refresh latency, engine scheduling/rebuild timing, real UI pixels/hit tests, saves or player saves.',flush=True)
