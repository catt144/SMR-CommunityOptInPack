"""Check the hub's retail EntitySpec guard and editor delegation."""
from pathlib import Path
import subprocess
import sys
from lupa import LuaRuntime

root = Path(__file__).resolve().parents[4]
source = (root / "tools/devmods/train_hub/Code/20_TrainHub.lua").read_text(encoding="utf8")
guard = source[source.index("local function install_hub_art_spec_guard()"):
               source.index("function OnMsg.ChangeMap()")]
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute("""
SMROptInTrainFloor = {}
calls = {}
g_Classes = {EntitySpec = {OnPresetPostLoad = function(self)
    calls[#calls+1] = self.id
end}}
""")
lua.execute("local Floor = SMROptInTrainFloor\n" + guard + "\ninstall_hub_art_spec_guard()")
lua.execute("""
local method = g_Classes.EntitySpec.OnPresetPostLoad
for _, id in ipairs({'SMROptInTrainHub6', 'SMROptInTrainHub6Glass',
                     'SMROptInTrainHub6DomeGlass'}) do
    method({id=id})
end
assert(#calls == 0, 'retail tried the editor-only post-load')
method({id='VanillaEntity'})
assert(#calls == 1 and calls[1] == 'VanillaEntity', 'other specs did not delegate')
EntitySpecPathToEntity = function() return 'editor/path' end
method({id='SMROptInTrainHub6'})
assert(#calls == 2 and calls[2] == 'SMROptInTrainHub6', 'editor did not delegate')
""")
print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]))
print("HEAD", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip())
print("PASS: retail skips only the hub's three specs; other specs and editor delegate")
print("LIMIT: real retail load still needs the owner's session log")
