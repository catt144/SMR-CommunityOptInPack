"""Desk lifecycle of the staged dust reference; no native rendering claim."""
import json
from pathlib import Path
import subprocess

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
SMRTK={armed={}}; empty_table={}; const={DustMaterialExterior=0}
function empty_func() end
function IsValid(o) return o and not o.deleted end
function IsKindOf(o,c) return o.class==c end
factor=0; function GetTimeFactor() return factor end
CObject={}; writes=0
function CObject.SetDust(o,n) o.dust=n; writes=writes+1 end
v={dust=0,SetDust=empty_func,handle=42,entity='SMROptInTrainHubReactor'}
function v:GetDust() return self.dust end
function v:GetEntity() return self.entity end
h={class='SMROptInTrainHubBase',attaches={v}}
function h:GetAttaches() return self.attaches end
function SMRTK.Bind(n,label,fn,opts) slot={n=n,fn=fn,opts=opts} end
function CreateRealTimeThread(fn)
 local co=coroutine.create(fn); assert(coroutine.resume(co)); return co
end
function Sleep(ms) assert(ms==2000); coroutine.yield() end
function IsValidThread(t) return coroutine.status(t)~='dead' end
function CurrentThread() return coroutine.running() end
function DeleteThread(t) coroutine.close(t) end
marks=0; function mark() marks=marks+1; return marks end
function log(_,fields) last_dump=fields end
function arm(sel)
 ctx={sel=sel,state={},mark=mark,log=log}
 SMRTK.armed.slot_2={state=ctx.state}
 return slot.fn(ctx)
end
function SMRTK.Disarm(id,reason)
 assert(id=='slot_2'); slot.opts.on_disarm(ctx); SMRTK.armed.slot_2=nil
end
''')
lua.execute((Path(__file__).with_name('82_ReactorDustSlot.lua.txt')).read_text(encoding='utf8'))
lua.execute(r'''
assert(slot.n==2 and slot.opts.mode=='armed')
local ok,why=arm(nil); assert(ok==false and writes==0)
factor=1000; ok,why=arm(h); assert(ok==false and writes==0); factor=0
h.attaches={}; ok,why=arm(h); assert(ok==false and writes==0)
h.attaches={v,v}; ok,why=arm(h); assert(ok==false and writes==0); h.attaches={v}
v.SetDust=CObject.SetDust; ok,why=arm(h); assert(ok==false and writes==0); v.SetDust=empty_func
v.dust=1; ok,why=arm(h); assert(ok==false and writes==0); v.dust=0
local result=arm(h); assert(result.hold_real_ms==2000 and v.dust==255)
local thread=ctx.state.thread
assert(coroutine.resume(thread)); assert(v.dust==0 and SMRTK.armed.slot_2==nil)
assert(last_dump.dust==0 and ctx.state.visual==nil and v.SetDust==empty_func)
-- The toolkit also uses disarm on save/load/map change: cancel before the timer.
arm(h); thread=ctx.state.thread; SMRTK.Disarm('slot_2','save')
assert(v.dust==0 and coroutine.status(thread)=='dead')
arm(h); v.deleted=true; SMRTK.Disarm('slot_2','map change'); v.deleted=nil; v.dust=0
-- Old timer must not clean up a later arm.
arm(h); thread=ctx.state.thread; SMRTK.armed.slot_2={state={}}
assert(coroutine.resume(thread)); assert(v.dust==255)
slot.opts.on_disarm(ctx); assert(v.dust==0)
''')
print(json.dumps({
    'command': 'python tools/trains/hub/tests/reactor_dust_slot_smoke.py',
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'status': 'PASS: fixture refusals, timed restore, cancellation, removed visual, stale timer',
    'limit': 'mocked lifecycle; native dust appearance and toolkit integration NOT RUN',
}))
