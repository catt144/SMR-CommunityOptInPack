"""Execute the distribution sitting callbacks with the desk fixture, without launching Mars."""
import subprocess
import sys
from distribution_smoke import ROOT
from distribution_ui_smoke import ui_runtime


def main():
    print('command:',subprocess.list2cmdline([sys.executable,*sys.argv]),flush=True)
    print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),flush=True)
    kit=ROOT.parent/'SMR-BugFixPack-TestKit'
    print('TestKit HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],cwd=kit,text=True).strip(),flush=True)
    lua=ui_runtime()
    lua.execute(r'''
SMRTK={slots={},triggers={},armed={},error_count=0}
function SMRTK.Bind(n,label,fn) SMRTK.slots[n]={label=label,fn=fn} end
function SMRTK.BindScratch() end
function SMRTK.Trigger(spec) SMRTK.triggers[spec.id]=spec end
function SMRTK.Run(id) return true,{} end
function SMRTK.Arm(id,...)
    local ctx={state={}}
    local r,why=SMRTK.triggers[id].prepare(ctx,...)
    if r==false then return false,{reason=why} end
    SMRTK.armed[id]=ctx
    return true,r
end
function SMRTK.Disarm(id) SMRTK.armed[id]=nil end
GetTimeFactor=function() return 0 end
function context(s)
    local ctx={sel=s,mark=function() return 1 end,readings={}}
    ctx.log=function(kind,data) ctx.readings[#ctx.readings+1]=data end
    return ctx
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
assert(T.slots[4].fn(ctx).rows==1)
assert(ctx.readings[1].mode=='export' and ctx.readings[1].enabled==true)
assert(ctx.readings[1].percent==20 and ctx.readings[1].target==24000)
assert(T.slots[5].fn(ctx).trigger=='distribution_target')
local watch=T.armed.distribution_target
assert(not T.triggers.distribution_target.when(watch))
checked_transfer(t)
local fired,result=T.triggers.distribution_target.when(watch)
assert(fired and result.verdict=='at_target' and result.stock==24000 and result.target==24000)
deliver(t,h)
assert(T.slots[5].fn(ctx).trigger=='distribution_target')
watch=T.armed.distribution_target
checked_transfer(t) -- A hub call alone cannot witness the export-floor return trip.
assert(not T.triggers.distribution_target.when(watch))
t.current_station=s;checked_transfer(t)
fired,result=T.triggers.distribution_target.when(watch)
assert(fired and result.stock==24000 and result.calls>watch.state.calls)
assert(T.slots[6].fn(ctx).after==480000)
assert(T.slots[6].fn(ctx).after==0)
assert(T.slots[1] and T.slots[2] and T.slots[3])
print('PASS native hex click -> Export: slot 4 proves mode/percent/target; capacity 120, slot 5 witnesses floor 24 plus a source return (rejects hub-only witness), slot 6 fills hub to 480/empties; capacity slots retained')
''')
    print('NOT TESTED: native kit dispatch, trigger timing and actual game UI',flush=True)


if __name__=='__main__':
    main()
