"""Exercise real SMRTK dispatch/binding with the composed slots; no game verdict.

This checks sitting assembly and refusal controls, not the inherited instruments'
game behavior. Their own source-pinned smokes remain separate.
"""
from pathlib import Path
from lupa import LuaRuntime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KIT = ROOT.parent / "SMR-BugFixPack-TestKit"

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
empty_table = {}; empty_func = function() end
OnMsg = setmetatable({}, {__newindex=function(t,k,v) end})
SMRTK = {slots={}, armed={}, actions={}, triggers={}, error_count=0, fires={},
  after_record={}, pins={}, pages={}, slot_count=12, line_index=0}
local T = SMRTK
function T.Action(def)
  if T.armed[def.id] then return false,"disarm before replacing action" end
  T.actions[def.id]=def; return def
end
function T.Bind(n,label,fn,opts) error("legacy Bind was not expected") end
function T.Log(...) end
function T.Mark(label) return 1 end
function T.Page(...) end
function T.PreloadProbeSweep(e) T.preloaded=e end
function T.Run(...) return true,{} end
function T.Trigger(spec)
  T.triggers[spec.id]=spec
  return {disarm=function() return {} end}
end
function GetTimeFactor() return speed or 0 end
function GameTime() return 100 end
const={HourDuration=3600000}
function IsValid(o) return type(o)=="table" and not o.dead end
function IsKindOf(o,k) return o.class==k end
function GetEnvironment(map) return map end
SMROptInPack={fixes={}, IsActive=function() return true end,
  OptionEnabled=function() return true end, PackVersion=function() return "0.0.0" end}
SMRFixPack={PackVersion=function() return "1.0.26" end}
Cities={}; UIColony={labels={}}
''')
# Use actual current Bind/slot_context implementation, retaining trigger stubs.
agent = (KIT / "Code/74_SMRTK_Agent.lua").read_text(encoding="utf-8-sig")
lua.execute(agent[:agent.index('for _, pin in ipairs')])
source = (HERE / "80_AgentSlots_final.lua.txt").read_text(encoding="utf-8")
source = source.replace('local expected_fixpack = "absent"', 'local expected_fixpack = "present"', 1)
lua.execute(source)
lua.execute(r'''
local T=SMRTK
function invoke(n)
  return T.actions["slot_"..n].run({state={},selected=nil})
end
assert(T.preloaded.exit==1)
assert(T.preloaded.command=='grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/', "native probe gate requires its exact command")
assert(next(T.armed)==nil, "load armed a watch")
assert(SMROptInPack.TrainTrace==nil, "load changed trace")
for n=1,12 do assert(T.actions["slot_"..n], "missing slot "..n) end
assert(T.actions.slot_7.label:match("^Crossings:"))
local original=SMRFixPack
SMRFixPack=nil
local ok,why=invoke(7)
assert(ok==false and why:match("wrong process configuration"))
ok,why=T.triggers.crossing_hub.prepare({state={}})
assert(ok==false and why:match("wrong process configuration"))
SMRFixPack=original
-- The existing witness refuses an unarmed ledger rather than reading success.
ok,why=invoke(10); assert(ok==false and why:match("no ledger"))
T.armed.example={}
ok,why=invoke(12); assert(ok==false and why:match("cancel all watches"))
T.armed.example=nil
speed=1000
ok,why=invoke(12); assert(ok==false and why:match("pause"))
speed=0
local names={"Depot","Rows","Upgrades","34b","Crossings"}
for _,name in ipairs(names) do
  local fields=invoke(12); assert(fields.group==name)
  for n=1,10 do assert(T.actions["slot_"..n].label:match("^"..name..":")) end
end
local fields=invoke(11)
assert(fields.fixpack=="present" and fields.trace=="false" and fields.stations==0)
local trace=T.actions.slot_scratch.run({state={}})
assert(trace.trace==true)
trace=T.actions.slot_scratch.run({state={}}); assert(trace.trace==false)
-- Quiet timer reports liveness separately from completion.
local state={}
local train={command="Idle",stockpiled_amount={Metals=10}}
Cities={{labels={Train={train}}}}
local before=T.triggers.battery_35_hour.prepare({state=state})
assert(before.live_trains==1 and before.train_state_changes==0)
train.command="Moving"
assert(T.triggers.battery_35_hour.when({state=state})==false)
GameTime=function() return state.deadline end
local done,result=T.triggers.battery_35_hour.when({state=state})
assert(done and result.verdict=="hour_done" and result.train_state_changes==1)
T.error_count=1
done,result=T.triggers.battery_35_hour.when({state=state})
assert(done and result.verdict=="new_error")
Cities={}; T.error_count=0
''')
lua.execute('SMRFixPack=nil')
lua.execute(source.replace('local expected_fixpack = "present"', 'local expected_fixpack = "absent"', 1))
lua.execute(r'''
local fields=SMRTK.actions.slot_11.run({state={}})
assert(fields.fixpack=="absent")
SMRFixPack={}
local ok,why=SMRTK.actions.slot_7.run({state={}})
assert(ok==false and why:match("wrong process configuration"))
''')
print("PASS: assembly, real Bind, group cycle, no automatic arm/mutation, both configuration guards, paused/armed guards, trace toggle, quiet-hour liveness/error controls")
