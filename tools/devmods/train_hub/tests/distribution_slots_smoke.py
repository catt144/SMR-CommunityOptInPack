"""Execute the distribution sitting callbacks with the desk fixture, without launching Mars."""
import subprocess
import sys
from distribution_smoke import ROOT, runtime


def main():
    print('command:',subprocess.list2cmdline([sys.executable,*sys.argv]),flush=True)
    print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),flush=True)
    kit=ROOT.parent/'SMR-BugFixPack-TestKit'
    print('TestKit HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],cwd=kit,text=True).strip(),flush=True)
    lua=runtime()
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
function context(s) return {sel=s,mark=function() return 1 end,log=function() end} end
''')
    lua.execute((kit/'Code/80_AgentSlots.lua').read_text(encoding='utf8'))
    lua.execute(r'''
local T,D=SMRTK,SMROptInTrainDistribution
local t,s,h=fixture(60,0,60,240)
assert(D.Set(s,'Metals','export',20))
local ctx=context(s)
assert(T.slots[4].fn(ctx).rows==1)
assert(T.slots[5].fn(ctx).trigger=='distribution_target')
local watch=T.armed.distribution_target
assert(not T.triggers.distribution_target.when(watch))
checked_transfer(t)
local fired,result=T.triggers.distribution_target.when(watch)
assert(fired and result.verdict=='at_target' and result.stock==12000)
assert(T.slots[6].fn(ctx).after==240000)
assert(T.slots[6].fn(ctx).after==0)
assert(T.slots[1] and T.slots[2] and T.slots[3])
print('PASS slot 4 reads, slot 5 arms and sees actual transfer witness, slot 6 explicitly fills/empties; capacity slots retained')
''')
    print('NOT TESTED: native kit dispatch, trigger timing and actual game UI',flush=True)


if __name__=='__main__':
    main()
