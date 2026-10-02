"""Brief 30 sitting overlay: fixture guards and falsifiable target watch; desk only."""
import subprocess
from pathlib import Path
import sys

from distribution_ui_smoke import ROOT, MOD, ui_runtime


def main():
    print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print("HEAD:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), flush=True)
    lua = ui_runtime()
    lua.execute(r'''
SMRTK={armed={},error_count=0}; slots={}; triggers={}; speed=0; now=0; CurrentMap={}
GameTime=function() return now end; GetTimeFactor=function() return speed end
const.HourDuration=10000
SMRTK.Bind=function(n,label,fn,opts) slots[n]=fn end
SMRTK.Trigger=function(spec) triggers[spec.id]=spec end
SMRTK.Log=function() end
SMRTK.Run=function(id) assert(id=='speed_ultra');speed=100;return true,{} end
SMRTK.Disarm=function(id) SMRTK.armed[id]=nil end
SMRTK.Arm=function(id,o)
    local ctx={state={}};local result,why=triggers[id].prepare(ctx,o)
    if result==false then return false,{reason=why} end
    SMRTK.armed[id]=ctx;return true,result
end
function context(o) return {sel=o,mark=function() return 42 end,log=function() end} end
''')
    lua.execute((Path(__file__).resolve().parent / "80_AgentSlots_station_rows.lua.txt").read_text(encoding="utf8"))
    lua.execute(r'''
assert(speed==0 and not next(SMRTK.armed),'loading never mutates/arms')
local D=SMROptInTrainDistribution
local t,s,other=fixture(10,0,100,100)
other.hub=false;other.HubTrackGraph=nil;other.GetTrainExportFloor=nil;D.Refresh()
function s:GetMap() return CurrentMap end
function other:GetMap() return CurrentMap end
local ctx=context(s)
assert(s.demand.Metals:AssignUnit(50000))
local out=slots[1](ctx)
assert(out.stock==50000 and out.reserved_shortfall==30000 and out.added==40000)
assert(s.demand.Metals.actual-s.demand.Metals.target==50000)
speed=1;assert(slots[1](ctx)==false);speed=0
s:SetAcceptResourceState('Metals','disabled');assert(slots[1](ctx)==false)
s:SetAcceptResourceState('Metals','store');s.demand.Metals:UnassignUnit(50000,false)
local wrong=context({class='Depot'});assert(slots[1](wrong)==false)
assert(D.Set(s,'Metals','export',20));assert(D.Set(other,'Metals','import',100))
assert(slots[4](ctx).hub=='none')
local trigger=triggers.station_rows_30
local watch={state={}}
assert(trigger.prepare(watch,s).mode=='export')
assert(trigger.when(watch)==false)
-- Stock equality alone cannot pass a leg which never evaluated native loading.
s:AddResource(-30000,'Metals');assert(trigger.when(watch)==false)
s:AddResource(30000,'Metals');checked_transfer(t)
local fired,result=trigger.when(watch)
assert(fired and result.verdict=='target_sampled' and result.stock==20000)
-- Independent counterexamples: wrong floor, edit, native error, timeout.
s:AddResource(10000,'Metals');watch={state={}};trigger.prepare(watch,s)
s:AddResource(-11000,'Metals');local _,r=trigger.when(watch);assert(r.verdict=='below_floor')
assert(D.Set(s,'Metals','import',50));watch={state={}};trigger.prepare(watch,s)
s:AddResource(32000,'Metals');local _,r=trigger.when(watch);assert(r.verdict=='above_cap')
watch={state={}};trigger.prepare(watch,s);D.Set(s,'Metals','import',51)
local _,r=trigger.when(watch);assert(r.verdict=='row_changed')
watch={state={}};trigger.prepare(watch,s);SMRTK.error_count=1
local _,r=trigger.when(watch);assert(r.verdict=='new_error')
watch={state={}};trigger.prepare(watch,s);now=watch.state.deadline
local _,r=trigger.when(watch);assert(r.verdict=='deadline')
assert(slots[5](ctx).mark==42 and speed==100 and SMRTK.armed.station_rows_30)
speed=0;local old=SMRTK.armed.station_rows_30
assert(slots[5](ctx).mark==42 and SMRTK.armed.station_rows_30~=old,'slot 5 replaces its stale run')
print('PASS overlay: inert load, native stock/reservation guards, read, target requires stock change and native call; floor/cap/edit/error/deadline falsifiers; explicit arm only')
''')


if __name__ == "__main__":
    main()
