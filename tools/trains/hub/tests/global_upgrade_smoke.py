'''Global upgrade migration and native leak-fixup recovery; no native save claim.'''
import hashlib
import subprocess
import sys
from lupa import LuaError
import cargo_upgrade_smoke as cargo

CASES = r'''
-- Restore the pre-global representation with Capacity ON and Cargo OFF on ruins.
for _,entry in pairs(UIColony.SMROptIn_hub_upgrades) do
 for _,m in ipairs(entry.modifiers) do m:TurnOff() end
end
UIColony.SMROptIn_hub_upgrades=nil
for _,h in ipairs(city.labels.Station) do
 if IsKindOf(h,'SMROptInTrainHubBase') then
  h.upgrades_built={}; h.upgrade_on_off_state={}; h.upgrade_modifiers={}; h.upgrade_id_to_modifiers={}
 end
end
Building.ApplyUpgrade(A,1); Building.ApplyUpgrade(A,2)
Building.ToggleUpgradeOnOff(A,CARGO)
local duplicate=hub(991)
Building.ApplyUpgrade(duplicate,1); Building.ToggleUpgradeOnOff(A,ID)
local inherited=duplicate.upgrade_modifiers[ID][1]
A.destroyed=true
OnMsg.LoadGame()
assert(UIColony.SMROptIn_hub_upgrades[ID].on and not UIColony.SMROptIn_hub_upgrades[CARGO].on,'legacy saved switches imported')
assert(UIColony.SMROptIn_hub_upgrades[ID].modifiers[1]==inherited and inherited.container==UIColony,'native modifier identity transferred')
assert(next(city.label_modifiers.Station)==nil,'legacy city registration removed')
assert(T1.max_shared_storage==105000 and T1.max_colonists_to_transport==24 and speed()==700,'legacy effects exactly once')
assert(both:CanDisableUpgrade(ID) and both:CanDisableUpgrade(CARGO),'legacy receiver controls')
both:ToggleUpgradeOnOff(CARGO)
assert(T1.max_shared_storage==147000 and speed()==875,'legacy receiver toggles globally')
-- All hubs disappear while upgrades are ON; ordinary stations and trains stay.
for i=#city.labels.Station,1,-1 do
 local h=city.labels.Station[i]
 if IsKindOf(h,'SMROptInTrainHubBase') then h:StopUpgradeModifiers(); h.deleted=true; table.remove(city.labels.Station,i) end
end
assert(T1.max_shared_storage==147000 and speed()==875,'global survives zero hubs')
-- Native historical fixup sees no owning Building and drops generated-id modifiers.
-- The receipt must restore registration even if LabelModifier.working is still true.
UIColony.labels.Building={}; UIColony.labels.Dome={}; Cities={city}
SavegameFixups.RemoveLeakedUpgradeModifiers()
assert(T1.max_shared_storage==63000,'native leak fixup actually removed bonuses')
OnMsg.LoadGame()
assert(T1.max_shared_storage==147000 and speed()==875,'global recovers native fixup with no hubs')
OnMsg.LoadGame(); assert(T1.max_shared_storage==147000,'global repeated load no stacking')
local later=hub(9901)
assert(later:IsUpgradeOn(ID) and later:IsUpgradeOn(CARGO) and later:CanDisableUpgrade(CARGO),'global future hub panel')
Building.StopUpgradeModifiers(later)
assert(T1.max_shared_storage==147000,'global modifiers not owned by building cleanup')
later:ToggleUpgradeOnOff(CARGO)
assert(T1.max_shared_storage==105000 and speed()==700,'global future hub switch')
-- Copy the plain receipt table, as a deserializer would, retaining native object refs.
local saved=UIColony.SMROptIn_hub_upgrades; local restored={}
for id,e in pairs(saved) do restored[id]={on=e.on,modifiers=e.modifiers} end
UIColony.SMROptIn_hub_upgrades=restored
OnMsg.LoadGame(); assert(not later:IsUpgradeOn(CARGO) and T1.max_shared_storage==105000,'global restored OFF receipt')
'''

archive=cargo.ROOT.parent/'SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua/Buildings/Building.lua'
import re
setup='SavegameFixups={}\nlocal native_ipairs=ipairs; ipairs=function(t) return native_ipairs(t or {}) end\n'+re.search(r'^function SavegameFixups.RemoveLeakedUpgradeModifiers\(.*?^end\n',archive.read_text(encoding='utf8'),re.M|re.S)[0]

def run(code):
    cargo.run(code,CASES,setup)

if __name__=='__main__':
    print('command:',subprocess.list2cmdline([sys.executable,*sys.argv]))
    print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
    code=cargo.SOURCE.read_text(encoding='utf8')
    print('source_sha256:',hashlib.sha256(cargo.SOURCE.read_bytes()).hexdigest())
    run(code)
    print('PASS legacy migration, saved switches, native modifier identity, zero hubs, native leak fixup, future hub, restored receipt')
    mutations={
        'lost off state': ('on = Building.IsUpgradeOn(buyer, id) and true or false', 'on = true'),
        'local container': ('mod.container = colony','-- retain old city container'),
        'missing registration repair': ('if not mod:IsApplied() or not registered then mod:TurnOn() end','if not mod:IsApplied() then mod:TurnOn() end'),
        'building owns modifiers': ('hub.upgrade_modifiers[id] = {}','hub.upgrade_modifiers[id] = entry.modifiers'),
        'lost receipt': ('\tadopt_colony_upgrades(UIColony)','\tUIColony.SMROptIn_hub_upgrades = nil\n\tadopt_colony_upgrades(UIColony)'),
    }
    for name,(before,after) in mutations.items():
        assert before in code,name
        try: run(code.replace(before,after,1))
        except LuaError as e:
            assert any(x in str(e) for x in ['legacy','global','cargo','future hub']),str(e)
            print('PASS mutation rejected:',name)
        else: raise AssertionError('mutation survived: '+name)
