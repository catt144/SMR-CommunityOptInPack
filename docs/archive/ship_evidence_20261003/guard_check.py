from pathlib import Path
import sys, hashlib, json, subprocess
import lupa
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'CLAUDE.md').is_file())
sys.path.insert(0,str(ROOT/'tools'))
from l2_reload_sim import BOOT
core=(ROOT/'Code/00_Core.lua').read_text(encoding='utf-8-sig')
source=(ROOT/'Code/Opt_MultipleSuns.lua').read_text(encoding='utf-8-sig')
rows=[]
for enabled,missing in [(True,False),(False,False),(True,True)]:
    lua=lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(BOOT)
    lua.execute('SMRSIM_ResetMessages()')
    lua.execute('''CurrentModOptions={MultipleSuns=true}
    SolarPanelBase={GameInit=function(self) self.original_calls=(self.original_calls or 0)+1;return 73 end,
      SetArtificialSun=function(self,sun) self.artificial_sun=sun end}
    ArtificialSunBase={Done=function() return 42 end}
    function TestSunPanelRange(sun,panel) return true end
    function IsValid(o) return o~=nil end
    BuildingTemplates={ArtificialSun={build_once=true}}
    ''')
    if not enabled: lua.execute('CurrentModOptions.MultipleSuns=false')
    if missing: lua.execute('SolarPanelBase.GameInit=nil')
    lua.execute(core)
    lua.execute(source)
    status=lua.eval('SMROptInPack.fixes.MultipleSuns.status')
    if missing:
        assert status!='active'
        assert 'GameInit' in lua.eval('SMROptInPack.fixes.MultipleSuns.detail')
    else:
        lua.execute('panel={city={labels={ArtificialSun={{}}}},SetArtificialSun=SolarPanelBase.SetArtificialSun};returned=SolarPanelBase.GameInit(panel)')
        assert lua.eval('returned')==73
        assert lua.eval('panel.original_calls')==1
        assert lua.eval('panel.artificial_sun~=nil')==enabled
        assert (status=='active')==enabled
    rows.append({'enabled':enabled,'missing_GameInit':missing,'status':status,'result':'PASS'})
# Mutation control: missing declarative pair must fail the actual wrap checker.
import harvest_wrap_targets as wrap
import tempfile
with tempfile.TemporaryDirectory() as temp:
    wrap.CODE=temp
    p=Path(temp)/'Opt_MultipleSuns.lua'
    p.write_text(source,encoding='utf-8')
    assert not wrap.check()[0]
    mutant=source.replace('{ class = "SolarPanelBase", method = "GameInit",','{ class = "SolarPanelBase", method = "SetArtificialSun",')
    assert mutant!=source
    p.write_text(mutant,encoding='utf-8')
    assert any(r[:3]==('Opt_MultipleSuns','SolarPanelBase','GameInit') for r in wrap.check()[0])
rows.append({'control':'remove GameInit Require pair in isolated copy','result':'expected wrap violation'})
print('guard behavioral controls:',json.dumps(rows))
r={'command':'python scratch/ship_guard_check.py','head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'rows':rows,'limit':'Lua harness, not native sitting'}
(ROOT/'scratch/ship_guard_result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
