"""Storage Hub: native upgrade, SetBase and request resize bodies; desk only."""
import subprocess
import sys
from lupa import LuaError
import cargo_upgrade_smoke as cargo
from pallet_visuals_smoke import extract

archive=cargo.ROOT.parent/'SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua'
SETUP='Modifiable={}\nElectricityConsumer={}\n'
SETUP+=extract((archive/'Modifiers.lua').read_text(encoding='utf8'),'Modifiable:SetBase')
SETUP+=extract((archive/'ElectricityConsumer.lua').read_text(encoding='utf8'),'ElectricityConsumer:OnModifiableValueChanged')
SETUP+=r'''
Building.SetBase=Modifiable.SetBase
function Building:ModifyValue(value,prop)
 self.base[prop]=self['base_'..prop]
 local p,a=0,0
 for _,m in ipairs(self.mods[prop] or empty_table) do p=p+m.percent; a=a+m.amount end
 return value*(100+p)//100+a
end
function Building:OnModifiableValueChanged(prop)
 Building.Notify(self,prop)
 ElectricityConsumer.OnModifiableValueChanged(self,prop)
end
function Building:UpdateConsumption(when)
 assert(when=='immediate','storage consumption notification')
 self.electricity.consumption=self.electricity_consumption
end
'''
template='\n'.join('h[%r]=%s'%(k,v) for k,v in cargo.fields.items() if k.startswith('upgrade4_') and 'description' not in k and 'display_name' not in k)
FIXTURE=r'''
local base_hub=hub
hub=function(...)
 local h=base_hub(...)
 TEMPLATE
 h.upgrade4_can_disable=true
 for i=1,3 do h['upgrade4_mod_prop_id_'..i]='' end
 h.electricity={consumption=h.electricity_consumption}
 return h
end
'''.replace('TEMPLATE',template)
CASES=r'''
local STORAGE=SMROptInTrainHubBase.hub_storage_upgrade
local x,y=hub(801),hub(802)
assert(UIColony:IsUpgradeUnlocked(STORAGE),'storage unlocked without tech')
assert(x:GetUpgradeTier(STORAGE)==4,'storage fourth slot')
assert(x:GetUpgradeCost(4,'Metals')==60000 and x:GetUpgradeCost(4,'MachineParts')==30000,'storage costs')
assert(x.max_storage_per_resource==2000000,'storage capacity network 2000')
x:ToggleUpgradeOnOff(ID)
assert(x.max_storage_per_resource==1000000,'storage base 1000')
x:ToggleUpgradeOnOff(ID)
-- A saved 480 hub: restore its old base and stock, keeping native Capacity ON.
x:SetBase('max_storage_per_resource',240000)
x.supply.Metals.actual=479800
assert(x.max_storage_per_resource==480000,'storage legacy fixture')
OnMsg.LoadGame()
assert(x.max_storage_per_resource==2000000 and x.supply.Metals.actual==479800,'storage 480 migration stock')
assert(x.demand.Metals.amount==1520200,'storage migrated requests')
x:ToggleUpgradeOnOff(ID); x:SetBase('max_storage_per_resource',240000)
x.supply.Metals.actual=239800; OnMsg.LoadGame()
assert(x.max_storage_per_resource==1000000 and x.supply.Metals.actual==239800,'storage 240 migration stock')
x:ToggleUpgradeOnOff(ID)
local station_cap,train_cap,passengers=small.max_storage_per_resource,T1.max_shared_storage,T1.max_colonists_to_transport
x:ApplyUpgrade(4)
assert(x.max_storage_per_resource==4000000 and y.max_storage_per_resource==4000000,'storage doubles to 4000 globally')
assert(x.electricity_consumption==29000 and y.electricity.consumption==29000,'storage power +19 reaches grid')
assert(y:HasUpgrade(STORAGE) and y:IsUpgradeOn(STORAGE) and y:CanDisableUpgrade(STORAGE),'storage shared panel')
assert(small.max_storage_per_resource==station_cap and T1.max_shared_storage==train_cap and T1.max_colonists_to_transport==passengers,'storage station train scope')
y:ToggleUpgradeOnOff(STORAGE)
assert(x.max_storage_per_resource==2000000 and not x:IsUpgradeOn(STORAGE),'storage shared off')
assert(x.electricity.consumption==10000 and y.electricity_consumption==10000,'storage power off')
local later=hub(803)
assert(later:HasUpgrade(STORAGE) and not later:IsUpgradeOn(STORAGE) and later.max_storage_per_resource==2000000,'storage future off')
later:ToggleUpgradeOnOff(STORAGE)
local future_on=hub(804)
assert(future_on:IsUpgradeOn(STORAGE) and future_on.max_storage_per_resource==4000000 and future_on.electricity_consumption==29000,'storage future on')
-- No stock lost when switching below existing contents; demand becomes zero.
x.supply.Metals.actual=3500000
later:ToggleUpgradeOnOff(STORAGE)
assert(x.supply.Metals.actual==3500000 and x.demand.Metals.amount==0,'storage off preserves excess stock')
later:ToggleUpgradeOnOff(STORAGE)
for i=#city.labels.Station,1,-1 do
 local h=city.labels.Station[i]
 if IsKindOf(h,'SMROptInTrainHubBase') then
  h.destroyed=true; OnMsg.BuildingDemolished(h); h:StopUpgradeModifiers()
  h.deleted=true; table.remove(city.labels.Station,i)
 end
end
OnMsg.LoadGame()
local rebuilt=hub(805)
assert(rebuilt:HasUpgrade(STORAGE) and rebuilt:IsUpgradeOn(STORAGE) and rebuilt.max_storage_per_resource==4000000,'storage salvage zero hubs rebuild')
rebuilt:ToggleUpgradeOnOff(STORAGE); OnMsg.LoadGame(); OnMsg.LoadGame()
assert(not rebuilt:IsUpgradeOn(STORAGE) and rebuilt.max_storage_per_resource==2000000 and rebuilt.electricity_consumption==10000,'storage repeated load off')
'''

def run(code): cargo.run(code,CASES,SETUP,FIXTURE)

def main():
    global FIXTURE
    print('command:',subprocess.list2cmdline([sys.executable,*sys.argv]))
    print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
    code=cargo.SOURCE.read_text(encoding='utf8')
    run(code)
    print('PASS storage 1000/2000/4000, +19 grid consumption and off, slot 4 and costs, station/train scope')
    print('PASS legacy 240/480 stock and requests, shared controls, future on/off, salvage, zero hubs, repeated load')
    mutations={
      'base':('local storage = on and 2000000 or 1000000','local storage = on and 2000000 or 240000'),
      'doubling':('local storage = on and 2000000 or 1000000','local storage = on and 1000000 or 1000000'),
      'power on':('on and 29000 or 10000','on and 10000 or 10000'),
      'power off':('on and 29000 or 10000','on and 29000 or 29000'),
      'migration':('hub:SetBase("max_storage_per_resource", storage)','if hub.base_max_storage_per_resource ~= 240000 then hub:SetBase("max_storage_per_resource", storage) end'),
      'stock retention':('hub:SetBase("max_storage_per_resource", storage)','hub:SetBase("max_storage_per_resource", storage); hub.supply.Metals.actual = 0'),
      'shared state':('entry.on = not entry.on','if id == hub_storage_upgrade then return end; entry.on = not entry.on'),
      'future':('\tsync_hub_storage(self)','\t-- omit future hub storage'),
      'salvage':('if IsKindOf(bld, "SMROptInTrainHubBase") then sync_colony_upgrades(bld.city and bld.city.colony) end','if IsKindOf(bld, "SMROptInTrainHubBase") then bld.city.colony.SMROptIn_hub_upgrades[hub_storage_upgrade] = nil end'),
      'station scope':('local function sync_hub_storage(hub)','local function sync_hub_storage(hub)\n for _,s in ipairs(hub.city.colony.labels.Station) do if not IsKindOf(s,"SMROptInTrainHubBase") then s.max_storage_per_resource = 1 end end'),
    }
    for name,(before,after) in mutations.items():
        assert before in code,name
        try: run(code.replace(before,after,1))
        except LuaError as exc:
            assert any(s in str(exc) for s in ['storage','station storage','cargo survives','assertion failed']),str(exc)
            print('PASS mutation rejected:',name)
        else: raise AssertionError('mutation survived: '+name)
    original=FIXTURE
    for name,before,after in [
        ('Metals cost', "h['upgrade4_upgrade_cost_Metals']=60000", "h['upgrade4_upgrade_cost_Metals']=1"),
        ('Machine Parts cost', "h['upgrade4_upgrade_cost_MachineParts']=30000", "h['upgrade4_upgrade_cost_MachineParts']=1"),
    ]:
        assert before in original,name
        FIXTURE=original.replace(before,after,1)
        try: run(code)
        except LuaError as exc:
            assert 'storage costs' in str(exc),str(exc)
            print('PASS mutation rejected:',name)
        else: raise AssertionError('mutation survived: '+name)
        finally: FIXTURE=original

if __name__=='__main__': main()
