"""Execute shared TestKit slot 3 against the upgrade fixture; require a read-only snapshot."""
import hashlib
import subprocess
import sys
from pathlib import Path
from cargo_upgrade_smoke import ROOT, SOURCE, run

kit = ROOT.parent / 'SMR-BugFixPack-TestKit'
# The sitting this smoke checks: a byte copy of TestKit 587f474's Code/80_AgentSlots.lua, staged
# here so a later sitting's slots in the shared kit cannot fail it (brief 33, audit 2026-10-02 §7).
slots = Path(__file__).resolve().parent / '80_AgentSlots_upgrades.lua.txt'
print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]))
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
print('TestKit HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=kit, text=True).strip())
print('slots_sha256:', hashlib.sha256(slots.read_bytes()).hexdigest())
setup = r'''
SMRTK={slots={},error_count=0}
function SMRTK.Bind(n,label,fn) SMRTK.slots[n]={label=label,fn=fn} end
function SMRTK.BindScratch() end
function SMRTK.Trigger(spec) return spec end
function GameTime() return 100 end
local factor=0
function GetTimeFactor() return factor end
Cities={city}
T1.GetNominalMoveSpeed=Train.GetNominalMoveSpeed
-- These UI/fixture methods would change state: a read must not reach them.
function SMROptInTrainHubBase:HasUpgrade() error('read called mutating HasUpgrade') end
function Building:AddResource() error('read changed stock') end
function Building:SetStoredAmount() error('read filled train') end
function SMROptInTrainHubBase:ToggleUpgradeOnOff() error('read toggled upgrade') end
'''
cases = r'''
local rows={}
local ctx={mark=function() return 1 end,log=function(_,r) rows[#rows+1]=r end}
local before=T1.max_shared_storage
local claim=both.upgrades_built
local onoff=both.upgrade_on_off_state
local out=SMRTK.slots[3].fn(ctx)
assert(out.cargo_unlocked and out.trains==1)
assert(out.owner=='colony' and out.modifiers==4 and out.applied==3,'colony modifier dedup and off state')
local train_read,cargo_read,capacity_mod,cargo_mod=false,false,false,false
for _,r in ipairs(rows) do
 if r.row=='train' then
  train_read=true
  assert(r.cargo_cap==105000 and r.passenger_cap==24 and r.nominal_speed==700 and r.turn_anim_speed==2100)
 elseif r.row=='cargo_upgrade' and r.object==tostring(both.handle) then
  cargo_read=true; assert(r.own and not r.on)
 elseif r.row=='modifier' then
  if r.upgrade==ID then capacity_mod=true end
  if r.upgrade==CARGO then cargo_mod=true end
 end
end
assert(train_read and cargo_read and capacity_mod and cargo_mod,'slot must expose both upgrade modifier groups')
assert(T1.max_shared_storage==before and both.upgrades_built==claim and both.upgrade_on_off_state==onoff)
assert(not both:IsUpgradeOn(CARGO),'read did not change off state')
for i=#city.labels.Station,1,-1 do
 if IsKindOf(city.labels.Station[i],'SMROptInTrainHubBase') then table.remove(city.labels.Station,i) end
end
rows={}; out=SMRTK.slots[3].fn(ctx)
assert(out.owner=='colony' and out.hubs==0 and out.modifiers==4 and out.applied==3,'colony read without hubs')
factor=1
local ok,why=SMRTK.slots[3].fn(ctx)
assert(ok==false and why=='pause first')
'''
source=SOURCE.read_text(encoding='utf8')
slot_code=slots.read_text(encoding='utf8')
run(source, setup + '\n' + slot_code + '\n' + cases)
from lupa import LuaError
for name,before,after in [
    ('duplicate modifier rows','if seen[m] then return end','-- no dedup'),
    ('no-hub off modifiers','pairs(UIColony.SMROptIn_hub_upgrades or empty_table)','pairs(empty_table)'),
]:
    assert before in slot_code
    try: run(source,setup+'\n'+slot_code.replace(before,after,1)+'\n'+cases)
    except LuaError as e:
        assert 'colony' in str(e),str(e)
        print('PASS mutation rejected:',name)
    else: raise AssertionError('mutation survived: '+name)
print('PASS slot 3: both upgrade states/modifiers, capacities, speed/animation, paused gate; no fill/toggle/UI allocation')
