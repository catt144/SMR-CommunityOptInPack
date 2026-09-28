"""Execute the distribution sitting callbacks with the desk fixture, without launching Mars."""
import subprocess
import sys
import hashlib
import re
from distribution_smoke import ROOT
from distribution_ui_smoke import ui_runtime


def main():
    print('command:',subprocess.list2cmdline([sys.executable,*sys.argv]),flush=True)
    print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),flush=True)
    kit=ROOT.parent/'SMR-BugFixPack-TestKit'
    print('TestKit HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],cwd=kit,text=True).strip(),flush=True)
    lua=ui_runtime()
    lua.execute(r'''
SMRTK={slots={},triggers={},armed={},actions={},after_record={},fires={},error_count=0,trigger_revision=0}
function SMRTK.Bind(n,label,fn) SMRTK.slots[n]={label=label,fn=fn} end
function SMRTK.BindScratch(label,fn) SMRTK.scratch={label=label,fn=fn} end
SMRTK.Taint=function() return false end
SMRTK.Log=function(kind,data) SMRTK.last_log=data end
SMRTK.Mark=function() return 1 end
function CreateGameTimeThread(fn)
    local co=coroutine.create(fn); assert(coroutine.resume(co)); return co
end
CreateRealTimeThread=function(fn) fn() end
CurrentThread=coroutine.running
IsValidThread=function(co) return coroutine.status(co)~='dead' end
DeleteThread=function(co) coroutine.close(co) end
PlayFX=function() end
SetGameSpeed=function(n) speed=n end
GetTimeFactor=function() return 0 end
function context(s)
    local ctx={sel=s,mark=function() return 1 end,readings={}}
    ctx.log=function(kind,data) ctx.readings[#ctx.readings+1]=data end
    return ctx
end
''')
    core=(kit/'Code/70_SMRTK_Core.lua').read_text(encoding='utf8')
    agent=(kit/'Code/74_SMRTK_Agent.lua').read_text(encoding='utf8')
    for name,source in [('70_SMRTK_Core.lua',core),('74_SMRTK_Agent.lua',agent)]:
        print(name,'sha256:',hashlib.sha256(source.encode()).hexdigest(),flush=True)
    lua.execute('local T=SMRTK; local function check_taint() end; local recording={}\n'+
                core[core.index('function T.ArmedCount()'):core.index('function T.Bind(')])
    lua.execute('local T=SMRTK\n'+agent[agent.index('local function stop_thread('):agent.index('local function scalar(')])
    lua.execute('local T=SMRTK\n'+re.search(r'function OnMsg.SaveGameStart\(\).*? end',core)[0])
    lua.execute(r'''
SMRTK.specs={}
local trigger=SMRTK.Trigger
SMRTK.Trigger=function(spec) SMRTK.specs[spec.id]=spec;return trigger(spec) end
for _,name in ipairs({'speed_ultra','taint_read','eligibility'}) do
    SMRTK.Action{id=name,run=function() return {} end}
end
function poll(id)
    local co=SMRTK.armed[id].state.thread
    assert(coroutine.resume(co))
end
''')
    lua.execute((kit/'Code/80_AgentSlots.lua').read_text(encoding='utf8'))
    lua.execute(r'''
local T,D=SMRTK,SMROptInTrainDistribution
local t,s,h=fixture(120,0,120,480)
local dlg,row=dialog(s);OnMsg.DialogOpen(dlg)
row:OnActivate(row.context) -- One native hex click: Balanced -> Export.
row.distribution_slider:ScrollTo(20)
local ctx=context(s)
assert(T.slots[4].fn(ctx).rows==2)
assert(ctx.readings[1].mode=='export' and ctx.readings[1].enabled==true)
assert(ctx.readings[1].percent==20 and ctx.readings[1].target==24000)
assert(ctx.readings[1].configured and ctx.readings[2].res=='Food')
assert(ctx.readings[2].mode=='balanced' and ctx.readings[2].target==10000 and not ctx.readings[2].configured)
assert(not D.Get(s,'Food'))
do
    local train,spoke,hub=fixture(48,177,120,480)
    local read=context(spoke)
    assert(T.slots[4].fn(read).rows==2)
    for _,v in ipairs(read.readings) do
        assert(v.mode=='balanced' and v.percent==8 and v.target==10000 and not v.configured)
    end
    spoke:SetDesiredAmount(25000);read=context(spoke);T.slots[4].fn(read)
    assert(read.readings[1].target==25000 and read.readings[1].percent==21)
    spoke.max_storage_per_resource=240000;spoke:OnModifiableValueChanged('max_storage_per_resource')
    read=context(spoke);T.slots[4].fn(read)
    assert(read.readings[1].target==25000 and read.readings[1].percent==10)
    assert(rawget(hub,D.FIELD)==nil and rawget(spoke,D.FIELD)==nil)
    UIColony=s.city;D.Refresh()
    print('PASS slot 4 reads every untouched row as effective Balanced, exact live dial with derived percent; no settings written')
end
assert(T.slots[5].fn(ctx).trigger=='distribution_target')
local watch=T.armed.distribution_target
assert(not T.specs.distribution_target.when(watch))
checked_transfer(t)
local fired,result=T.specs.distribution_target.when(watch)
assert(fired and result.verdict=='at_target' and result.stock==24000 and result.target==24000)
deliver(t,h)
assert(T.slots[5].fn(ctx).trigger=='distribution_target')
watch=T.armed.distribution_target
checked_transfer(t) -- A hub call alone cannot witness the export-floor return trip.
assert(not T.specs.distribution_target.when(watch))
t.current_station=s;checked_transfer(t)
fired,result=T.specs.distribution_target.when(watch)
assert(fired and result.stock==24000 and result.calls>watch.state.calls)
assert(T.DistributionFullHubLeg(ctx)==false) -- At the floor is no refusal witness.
T.DisarmAll('new fixture')
t,s,h=fixture(120,0,120,480);D.Set(s,'Metals','export',20);ctx=context(s)
assert(T.DistributionFullHubLeg(ctx).held==480000)
assert(h.supply.Metals:GetActualAmount()==480000 and h.supply.Metals:GetTargetAmount()==0)
assert(not h.supply.Metals:AssignUnit(1000)) -- Competing hauler cannot drain the hub.
t.current_station=h;checked_transfer(t);poll('distribution_full_hub')
assert(T.armed.distribution_full_hub) -- Hub visit alone is not a spoke witness.
t.current_station=s;checked_transfer(t)
local ready,reading=T.specs.distribution_full_hub.when(T.armed.distribution_full_hub)
assert(ready and reading.verdict=='full_refused' and reading.stock==120000 and reading.hub_stock==480000)
poll('distribution_full_hub') -- Actual native trigger + dispatcher completion cleanup.
assert(not T.armed.distribution_full_hub and h.supply.Metals:GetTargetAmount()==480000 and speed==0)
assert(T.DistributionFullHubLeg(ctx).held==480000)
OnMsg.SaveGameStart()
assert(not T.armed.distribution_full_hub and h.supply.Metals:GetTargetAmount()==480000)
for _,reason in ipairs({'cancel','PreLoadGame','ChangeMap','DoneGame'}) do
    assert(T.DistributionFullHubLeg(ctx).held==480000);T.DisarmAll(reason)
    assert(h.supply.Metals:GetTargetAmount()==480000)
end
assert(h.supply.Metals:AssignUnit(1000))
assert(T.DistributionFullHubLeg(ctx)==false) -- Existing outgoing reservation is refused without changing it.
assert(h.supply.Metals:GetTargetAmount()==479000)
h.supply.Metals:UnassignUnit(1000,false)
h:AddResource(-1000,'Metals');assert(h.demand.Metals:AssignUnit(1000))
assert(T.DistributionFullHubLeg(ctx)==false) -- Existing incoming cargo must settle first.
h.demand.Metals:UnassignUnit(1000,false)
assert(T.DistributionFullHubLeg(ctx).held==480000)
h:AddResource(-1000,'Metals') -- External fixture corruption must not count as refusal.
ready,reading=T.specs.distribution_full_hub.when(T.armed.distribution_full_hub)
assert(ready and reading.verdict=='hold_broken')
poll('distribution_full_hub');assert(h.supply.Metals:GetTargetAmount()==479000)
assert(T.DistributionFullHubLeg(ctx).held==480000)
local old_time=GameTime;GameTime=function() return 300000 end
ready,reading=T.specs.distribution_full_hub.when(T.armed.distribution_full_hub)
assert(ready and reading.verdict=='deadline');poll('distribution_full_hub');GameTime=old_time
assert(h.supply.Metals:GetTargetAmount()==480000)
h.supply.Metals.reject=true
assert(T.DistributionFullHubLeg(ctx)==false and not T.armed.distribution_full_hub)
h.supply.Metals.reject=nil
assert(h.supply.Metals:GetTargetAmount()==480000)
do -- Scratch balances and slot 1 empties every non-hub station (owner, 2026-09-28).
    SMROptInTrainHubBase={}
    local kind=IsKindOf
    IsKindOf=function(o,c) if c=='SMROptInTrainHubBase' then return o.hub==true end return kind and kind(o,c) end
    local tr,sp,hb=fixture(120,0,120,480)
    local ctx=context(sp)
    local out=T.scratch.fn(ctx)
    assert(out.stations==1 and out.removed==110000 and out.added==10000 and out.held==0)
    assert(sp.supply.Metals:GetActualAmount()==10000 and sp.supply.Food:GetActualAmount()==10000)
    assert(sp.demand.Metals:GetActualAmount()==110000 and hb.supply.Metals:GetActualAmount()==0)
    tr:AddResource(5000,'Metals');UIColony.labels.Train={tr}
    out=T.slots[1].fn(context(sp))
    assert(out.removed==20000 and out.trains_loaded==1 and out.train_cargo==5000)
    assert(sp.supply.Metals:GetActualAmount()==0 and sp.supply.Food:GetActualAmount()==0)
    tr,sp,hb=fixture(120,0,120,480)
    assert(sp.supply.Metals:AssignUnit(115000)) -- A hauler's claim is never taken away.
    ctx=context(sp);out=T.scratch.fn(ctx)
    assert(out.removed==5000 and out.held==105000 and sp.supply.Metals:GetActualAmount()==115000)
    assert(sp.supply.Metals:GetTargetAmount()==0 and ctx.readings[1].row=='held')
    assert(sp.demand.Metals:AssignUnit(sp.demand.Metals:GetTargetAmount())) -- Incoming cargo keeps its room.
    T.slots[1].fn(context(sp));assert(sp.supply.Food:GetActualAmount()==0)
    assert(sp.demand.Food:AssignUnit(sp.demand.Food:GetTargetAmount()))
    out=T.scratch.fn(context(sp))
    assert(sp.supply.Food:GetActualAmount()==0 and sp.demand.Food:GetTargetAmount()==0 and out.held>=10000)
    local tf=GetTimeFactor;GetTimeFactor=function() return 1000 end
    assert(T.scratch.fn(context(sp))==false and T.slots[1].fn(context(sp))==false)
    GetTimeFactor=tf;IsKindOf=kind;SMROptInTrainHubBase=nil
    print('PASS Scratch balances non-hub rows to target and slot 1 empties them through AddResource; hub untouched; reserved stock and room kept and counted; train cargo counted; paused only')
end
do -- Slot 6 streams every train and station row that changed (owner, 2026-09-28).
    local tr,sp,hb=fixture(120,0,120,480)
    UIColony.labels.Train={tr}
    function tr.track:GetStartStation() return hb end
    function tr.track:GetEndStation() return sp end
    local logged,real_log={},T.Log
    T.Log=function(verb,kv,screen) logged[#logged+1]={verb=verb,kv=kv,screen=screen} end
    local sleep=Sleep;Sleep=function() coroutine.yield() end
    local ctx=context(sp);ctx.state={}
    local out=T.slots[6].fn(ctx)
    local trains,stocks=0,0
    for _,l in ipairs(logged) do
        assert(l.verb=='STREAM' and l.screen==false)
        if l.kv.row=='train' then trains=trains+1 elseif l.kv.row=='stock' then stocks=stocks+1 end
    end
    assert(trains==1 and stocks==4 and out.baseline==5 and out.rows==5, 'baseline '..trains..' '..stocks)
    logged={};assert(coroutine.resume(ctx.state.thread));assert(#logged==0) -- Quiet tick: nothing changed.
    sp:AddResource(-3000,'Metals');tr:AddResource(3000,'Metals');tr.assigned_resources={[hb]={Metals=3000}}
    assert(coroutine.resume(ctx.state.thread))
    assert(#logged==2, 'changes '..#logged)
    local st,tn=logged[1].kv,logged[2].kv
    if st.row~='stock' then st,tn=tn,st end
    assert(st.res=='Metals' and st.stock==117000 and st.before==120000 and st.target==10000)
    assert(tn.cargo=='Metals:3000' and tn.assigned:match(':Metals:3000$'))
    SMROptInTrainHubBase={}
    hb:AddResource(120000,'Metals')
    hb.capacity_columns={Metals=20}; hb.visual_col_start={Metals=0}; hb.max_z=9
    hb.visual_cubes.Metals={}
    for i=1,120 do hb.visual_cubes.Metals[i]={} end
    logged={};assert(coroutine.resume(ctx.state.thread))
    assert(#logged==1 and logged[1].kv.cubes==120 and logged[1].kv.expected_cubes==120)
    hb.visual_cubes.Metals={}
    logged={};assert(coroutine.resume(ctx.state.thread))
    assert(#logged==1 and logged[1].kv.stock==120000 and logged[1].kv.cubes==0
        and logged[1].kv.expected_cubes==120,'visual-only regression reaches stream without a stock change')
    ctx.state.cancelled=true;assert(coroutine.resume(ctx.state.thread))
    assert(coroutine.status(ctx.state.thread)=='dead')
    T.Log,Sleep=real_log,sleep
    print('PASS slot 6 streams a full baseline, then only changed train and stock rows, file-only; stops when disarmed')
end
assert(T.slots[1] and T.slots[2] and T.slots[3] and T.slots[6] and T.scratch)
print('PASS slot 4 mode/percent/target; slot 5 floor 24 and source return; the full-hub leg holds 480 against competing haulers and hub visits, refuses source export at 120; native trigger/dispatch cleanup on completion/save/cancel/deadline; reserved/changed fixtures rejected; slots 1-3, 6 and Scratch bound')
''')
    print('NOT TESTED: native engine ledger, thread scheduling and actual game UI',flush=True)


if __name__=='__main__':
    main()
