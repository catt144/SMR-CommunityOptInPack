"""Execute shared TestKit slot 3 against the upgrade fixture; require a read-only snapshot."""
import hashlib
import subprocess
import sys
from cargo_upgrade_smoke import ROOT, SOURCE, run

kit = ROOT.parent / 'SMR-BugFixPack-TestKit'
slots = kit / 'Code/80_AgentSlots.lua'
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
factor=1
local ok,why=SMRTK.slots[3].fn(ctx)
assert(ok==false and why=='pause first')
'''
run(SOURCE.read_text(encoding='utf8'), setup + '\n' + slots.read_text(encoding='utf8') + '\n' + cases)
print('PASS slot 3: both upgrade states/modifiers, capacities, speed/animation, paused gate; no fill/toggle/UI allocation')
