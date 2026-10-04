"""Falsify workbench guards, promotion rollback and the shared account-option bridge."""
import contextlib
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import promote_module as promote
import workbench as wb


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts}


def fixture(root):
    (root / "staging/Code").mkdir(parents=True)
    (root / "Code").mkdir()
    (root / "Code/00_Core.lua").write_text("-- fixture production\n", encoding="utf-8")
    for name in ("metadata.lua", "items.lua"):
        shutil.copyfile(wb.ROOT / name, root / name)
        shutil.copyfile(wb.ROOT / "staging" / name, root / "staging" / name)
    meta = wb.read(root / "staging/metadata.lua")
    meta = promote.replace_field(meta, "code", '\t\t"Code/00_Workbench.lua",\n\t\t"Code/Opt_Example.lua",\n')
    meta = promote.replace_field(meta, "default_options", '\t\tExample = false,\n')
    (root / "staging/metadata.lua").write_text(meta, encoding="utf-8", newline="\n")
    (root / "staging/items.lua").write_text('''return {
\tPlaceObj('ModItemCode', {
\t\t'name', "00_Workbench",
\t\t'CodeFileName', "Code/00_Workbench.lua",
\t}),
\tPlaceObj('ModItemCode', {
\t\t'name', "Opt_Example",
\t\t'CodeFileName', "Code/Opt_Example.lua",
\t}),
\tPlaceObj('ModItemOptionToggle', {
\t\t'name', "Example",
\t\t'DisplayName', "Example",
\t\t'Help', "A comma, brace } and escaped \\"quote\\" remain intact.",
\t\t'DefaultValue', false,
\t}),
}
''', encoding="utf-8", newline="\n")
    (root / "staging/Code/00_Workbench.lua").write_text("-- bridge fixture\n", encoding="utf-8")
    (root / "staging/Code/Opt_Example.lua").write_text('local ID = "Example"\nSMROptInPack.Register(ID, {optional=true})\n', encoding="utf-8")
    data = {"schema": 1, "modules": {"Example": {"files": ["Code/Opt_Example.lua"],
            "code": ["Code/Opt_Example.lua"], "options": ["Example"]}}}
    (root / "staging/modules.json").write_text(json.dumps(data), encoding="utf-8")
    (root / "staging/README.md").write_text("fixture\n", encoding="utf-8")


def bridge_check():
    from lupa import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('''
        handlers={}
        OnMsg=setmetatable({}, {__newindex=function(_,k,v)
            handlers[k]=handlers[k] or {}; table.insert(handlers[k],v)
        end})
        function Msg(name,...) for _,f in ipairs(handlers[name] or {}) do f(...) end end
        function CreateRealTimeThread() end
        function ModLog() end
        function Untranslated(s) return s end
        function IsSeedsResourceAvailable() return true end
        function IsGameRuleActive() return false end
        LifeSupportConsumerService={}; ElectricityConsumer={}
        HasConsumption={Consume_Visit=function() end}; DefineClass={}
        SMROptInPack_Disabled={}
        local function option(name,default)
            return {name=name,DefaultValue=default,GetOptionMeta=function(self)
                return {id=self.name,default=self.DefaultValue}
            end}
        end
        local function getitems(self,test)
            if test then return #self.items>0 end
            local result={} for _,v in ipairs(self.items) do result[#result+1]=v end return result
        end
        local function hasoptions(self) return next(self.default_options) end
        production={options={Existing=true, Arboretum=true},default_options={Existing=false},
            items={option('Existing',false)},GetOptionItems=getitems,HasOptions=hasoptions}
        workbench={options={Arboretum=false},default_options={Arboretum=false},
            items={option('Arboretum',false)},GetOptionItems=getitems,HasOptions=hasoptions}
        Mods={SMR_CommunityOptInPack=production,SMR_CommunityOptInPack_Workbench=workbench}
        core_env=setmetatable({CurrentModOptions=production.options},{__index=_G,__newindex=_G})
        dev_env=setmetatable({CurrentModOptions=workbench.options},{__index=_G,__newindex=_G})
        function execute(source,env) assert(load(source,'test','t',env))() end
    ''')
    execute = lua.globals().execute
    execute(wb.read(wb.ROOT / "Code/00_Core.lua"), lua.globals().core_env)
    bridge = wb.read(wb.ROOT / "staging" / wb.BOOTSTRAP)
    execute(bridge, lua.globals().dev_env)
    execute('''SMROptInPack.Register("Arboretum", {
        title="fixture", optional=true,
        apply=function() if not SMROptInPack.OptionEnabled("Arboretum") then return "off" end end,
    })''', lua.globals().dev_env)
    lua.execute('''
        assert(SMROptInPack.IsActive('Arboretum'), 'existing account value lost')
        assert(dev_env.CurrentModOptions == production.options)
        assert(not workbench:HasOptions(), 'second account page visible')
        assert(#production:GetOptionItems()==2 and #production.items==1)
        assert(production.default_options.Arboretum==nil, 'production metadata mutated')
        for _,v in ipairs({false,true,false,true}) do
            production.options.Arboretum=v
            Msg('ApplyModOptions','SMR_CommunityOptInPack')
            assert(SMROptInPack.IsActive('Arboretum')==v)
            assert(production.options.Existing==true)
        end
        production.options.properties={}; Msg('ModItemsLoaded')
        assert(production.options.properties==nil)
    ''')
    execute(bridge, lua.globals().dev_env)
    lua.execute('''
        assert(#production:GetOptionItems()==2, 'reload duplicated staged options')
        Msg('ModsReloading')
        assert(#production:GetOptionItems()==1 and workbench:HasOptions())
        production.options.Arboretum=nil
    ''')
    execute(bridge, lua.globals().dev_env)
    lua.execute("assert(production.options.Arboretum==false, 'new staged option not off by default')")


def main():
    passed = []
    def case(name, fn):
        fn()
        passed.append(name)
    with tempfile.TemporaryDirectory(prefix="smr-workbench-") as tmp:
        root = Path(tmp)
        fixture(root)
        assert not wb.check(root)[0], wb.check(root)
        original = snapshot(root)
        def dry():
            promote.promote(root, "Example", True)
            assert snapshot(root) == original
        case("check is byte-for-byte read-only", dry)
        def failed_gate():
            def fail(*args):
                raise RuntimeError("injected gate failure")
            try:
                promote.promote(root, "Example", gate=fail)
            except RuntimeError:
                pass
            else:
                raise AssertionError("gate failure was ignored")
            assert snapshot(root) == original
        case("failed gate restores every touched byte", failed_gate)
        def real():
            gates = []
            def run(root, args):
                gates.append(args[0])
                assert not wb.check(root)[0], wb.check(root)
            promote.promote(root, "Example", gate=run)
            assert gates == ["tools/workbench.py", "tools/parsecheck.py", "tools/doccheck.py"]
            assert "Example" in wb.registrations(root) and not wb.registrations(root / "staging")
            assert dict(wb.metadata(root)["default_options"].items())["Example"] is False
        case("promotion transfers code/options and invokes all gates", real)
        # Restore fixture without deleting a computed tree.
        for rel in snapshot(root).keys() - original.keys():
            (root / rel).unlink()
        for rel, body in original.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes(body)
        def mutation(name, rel, change):
            path = root / rel
            before = path.read_bytes() if path.exists() else None
            path.write_bytes(change(before))
            try:
                assert wb.check(root)[0], f"guard accepted {name}"
            finally:
                if before is None:
                    path.unlink()
                else:
                    path.write_bytes(before)
            passed.append(name)
        mutation("package exclusion removed", "metadata.lua", lambda b: b.replace(b'"*/staging/*",', b''))
        mutation("required dependency removed", "staging/metadata.lua", lambda b: b.replace(b"'required', true", b"'required', false"))
        mutation("workbench made packageable", "staging/metadata.lua", lambda b: b.replace(b'"*",', b'"*/tools/*",'))
        mutation("production references staging", "metadata.lua", lambda b: b.replace(b'"Code/00_Core.lua"', b'"staging/Code/00_Workbench.lua"'))
        mutation("unlisted code file", "staging/Code/Stray.lua", lambda _: b"-- stray\n")
        mutation("duplicate registered module", "Code/Duplicate.lua", lambda _: b'SMROptInPack.Register("Example", {})\n')
        mutation("default mismatch", "staging/metadata.lua", lambda b: b.replace(b"Example = false", b"Example = true"))
        mutation("source path escapes staging", "staging/modules.json", lambda b: b.replace(b'"Code/Opt_Example.lua"', b'"../Opt_Example.lua"', 1))
        collision = root / "Code/Opt_Example.lua"
        collision.write_text("-- existing destination", encoding="utf-8")
        try:
            promote.plan(root, "Example")
        except ValueError as exc:
            assert "destination exists" in str(exc)
        else:
            raise AssertionError("destination overwritten")
        passed.append("destination collision refused")
    case("shared option storage, live toggles, reload and detach", bridge_check)
    print("WORKBENCH SELFTEST:", len(passed), "PASS")
    for name in passed:
        print("  PASS", name)


if __name__ == "__main__":
    main()
