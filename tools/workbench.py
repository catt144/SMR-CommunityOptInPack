"""Check workbench ownership, load lists, option contracts and production package isolation."""
import json
import re
from pathlib import Path

PRODUCTION_ID = "SMR_CommunityOptInPack"
WORKBENCH_ID = PRODUCTION_ID + "_Workbench"
BOOTSTRAP = "Code/00_Workbench.lua"
ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return Path(path).read_text(encoding="utf-8-sig")


def lua_data(source):
    """Read our Lua data files in an isolated environment with no IO/global access."""
    from lupa import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    return lua.execute('''
        local source = ...
        local env = {
            PlaceObj = function(class, fields)
                local obj = {__class = class}
                for i=1,#fields,2 do obj[fields[i]] = fields[i+1] end
                return obj
            end,
            Untranslated = function(s) return s end,
            set = function(...) local t={} for _,k in ipairs({...}) do t[k]=true end return t end,
        }
        local fn, err = load(source, "data", "t", env)
        assert(fn, err)
        debug.sethook(function() error("data instruction limit") end, "", 100000)
        local value = fn()
        debug.sethook()
        return value
    ''', source)


def array(value):
    return [value[i] for i in range(1, len(value) + 1)] if value is not None else []


def metadata(root):
    return lua_data(read(root / "metadata.lua"))


def items(root):
    return array(lua_data(read(root / "items.lua")))


def manifest(root):
    value = json.loads(read(root / "staging/modules.json"))
    if value.get("schema") != 1 or not isinstance(value.get("modules"), dict):
        raise ValueError("invalid staging/modules.json schema")
    return value


def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError(f"invalid relative path: {relative!r}")
    p = Path(relative)
    if (p.is_absolute() or p.as_posix() != relative
            or any(x in ("..", ".", "") for x in relative.split("/"))):
        raise ValueError(f"unsafe relative path: {relative!r}")
    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes root: {relative}")
    for part in [target, *target.parents]:
        if part == root:
            break
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise ValueError(f"linked workbench path: {relative}")
    return target


def registrations(root):
    found = {}
    for path in sorted((root / "Code").rglob("*.lua")):
        source = read(path)
        # Calls must use a literal or a local constant; opaque registration is refused.
        for match in re.finditer(r"^\s*SMROptInPack\.Register\(\s*([^,]+),", source, re.M):
            arg = match[1].strip()
            literal = re.fullmatch(r'["\']([A-Za-z0-9_]+)["\']', arg)
            if not literal:
                literal = re.search(r'\blocal\s+' + re.escape(arg) + r'\s*=\s*["\']([A-Za-z0-9_]+)["\']', source)
            if not literal:
                raise ValueError(f"cannot resolve Register id in {path}")
            name = literal[1]
            if name in found:
                raise ValueError(f"duplicate Register id {name}: {found[name]} and {path}")
            found[name] = path.relative_to(root).as_posix()
    return found


def field_span(source, field):
    match = re.search(r"^\t'" + re.escape(field) + r"',\s*\{\n(.*?)^\t\},", source, re.M | re.S)
    if not match:
        raise ValueError(f"missing canonical {field} table")
    return match.span(1)


def item_blocks(source):
    blocks = list(re.finditer(r"^\tPlaceObj\('[^']+', \{\n.*?^\t\}\),\n", source, re.M | re.S))
    parsed = array(lua_data(source))
    if len(blocks) != len(parsed):
        raise ValueError("items.lua needs canonical top-level PlaceObj blocks")
    return [(m, lua_data("return " + m[0].strip().rstrip(","))) for m in blocks]


def check(root=ROOT):
    root = Path(root)
    stage = root / "staging"
    errors = []
    try:
        prod, dev = metadata(root), metadata(stage)
        if prod["id"] != PRODUCTION_ID or dev["id"] != WORKBENCH_ID:
            errors.append("production/workbench mod ids differ from their contract")
        if array(dev["ignore_files"]) != ["*"]:
            errors.append("dev-only workbench must exclude all files from its own package")
        for filename in ("metadata.lua", "items.lua"):
            # ignore_files is the sole permitted production reference to staging.
            source = read(root / filename)
            if filename == "metadata.lua":
                start, end = field_span(source, "ignore_files")
                source = source[:start] + source[end:]
            if re.search(r"staging[/\\]|SMR_CommunityOptInPack_Workbench", source, re.I):
                errors.append(f"production {filename} references the workbench")
        deps = array(dev["dependencies"])
        if not any(d["id"] == PRODUCTION_ID and d["required"] is True for d in deps):
            errors.append("workbench must require production through ModDependency")
        if array(dev["code"])[:1] != [BOOTSTRAP]:
            errors.append("workbench bootstrap must be first")
        from parsecheck import runtime, scan
        parser, why = runtime()
        if parser is None:
            errors.append(why)
        else:
            errors.extend(f"Lua parse: {p}: {err}" for p, err in scan(str(stage / "Code"), parser))
        code = array(dev["code"])
        disk = sorted(p.relative_to(stage).as_posix() for p in (stage / "Code").rglob("*.lua"))
        if len(code) != len(set(code)) or sorted(code) != disk:
            errors.append("workbench code list and Code files disagree (or duplicate)")
        seen_generated = False
        for path in code:
            safe_path(stage, path)
            if path.endswith(".generated.lua"):
                seen_generated = True
            elif seen_generated:
                errors.append("workbench handwritten code follows generated code")
        dev_items = items(stage)
        listed = [i["CodeFileName"] for i in dev_items if i["__class"] == "ModItemCode"]
        if listed != [p for p in code if not p.endswith(".generated.lua")]:
            errors.append("workbench ModItemCode order disagrees with metadata")
        for item in dev_items:
            if item["__class"] == "ModItemCode" and item["CodeFileName"] != f'Code/{item["name"]}.lua':
                errors.append("workbench ModItemCode name does not derive its file")
        options = [i for i in dev_items if i["__class"].startswith("ModItemOption")]
        defaults = dict(dev["default_options"].items())
        names = [i["name"] for i in options]
        if len(names) != len(set(names)) or set(names) != set(defaults):
            errors.append("workbench option items/defaults disagree (or duplicate)")
        for option in options:
            if option["DefaultValue"] != defaults.get(option["name"]):
                errors.append(f'workbench default differs: {option["name"]}')
        prod_names = {i["name"] for i in items(root) if i["__class"].startswith("ModItemOption")}
        if prod_names.intersection(names):
            errors.append("options registered in both production and workbench")
        production_ids, stage_ids = registrations(root), registrations(stage)
        if production_ids.keys() & stage_ids.keys():
            errors.append("module registered in both production and workbench")
        data = manifest(root)
        owned, declared_code, declared_options = [], [], []
        for name, module in data["modules"].items():
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
                errors.append(f"invalid module name: {name}")
            files = module["files"]
            if stage_ids.get(name) not in module["code"]:
                errors.append(f"module has no owned Register call: {name}")
            for rel in files:
                if not rel.startswith(("Code/", "Data/", "SourceData/", "tools/", "Entities/", "Meshes/", "Materials/", "Textures/", "Fallbacks/", "UI/")):
                    errors.append(f"unsupported module file: {rel}")
                if not safe_path(stage, rel).is_file():
                    errors.append(f"missing owned file: {rel}")
            if not set(module["code"]) <= set(files):
                errors.append(f"code outside owned files: {name}")
            owned.extend(files)
            declared_code.extend(module["code"])
            declared_options.extend(module["options"])
        if len(owned) != len({p.casefold() for p in owned}):
            errors.append("files owned by more than one module")
        if set(data["modules"]) != set(stage_ids):
            errors.append("manifest and registered workbench modules disagree")
        if sorted(declared_code) != sorted(p for p in code if p != BOOTSTRAP):
            errors.append("manifest and workbench code list disagree")
        if sorted(declared_options) != sorted(names):
            errors.append("manifest and workbench option list disagree")
        actual = {p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_file()
                  and "__pycache__" not in p.parts and p.suffix != ".pyc"}
        infrastructure = {"metadata.lua", "items.lua", "modules.json", "README.md", BOOTSTRAP}
        if actual - infrastructure != set(owned):
            errors.append(f"unowned/missing workbench files: {sorted((actual-infrastructure) ^ set(owned))}")
        from pack_predict import predict
        packed, ignored, links = predict(str(root), array(prod["ignore_files"]))
        leaks = [p for p, _ in packed if p.lower().startswith("staging/")]
        leaks += [p for p, pattern in links if p.lower().startswith("staging") and pattern is None]
        if leaks:
            errors.append(f"workbench leaks into package: {leaks}")
        # Positive witness prevents an empty/misrooted scan passing isolation.
        ignored_stage = {p for p, _ in ignored if p.startswith("staging/")}
        if not {"staging/metadata.lua", "staging/" + BOOTSTRAP} <= ignored_stage:
            errors.append("package scan did not witness the excluded workbench")
        summary = f"{len(stage_ids)} modules; {len(code)} code files; {len(names)} options; {len(ignored_stage)} staged files excluded; {len(leaks)} leaks"
    except Exception as exc:
        errors.append(str(exc))
        summary = "unreadable workbench"
    return errors, summary


if __name__ == "__main__":
    import subprocess
    print("COMMAND: python tools/workbench.py")
    print("HEAD:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip())
    errors, summary = check()
    print("WORKBENCH:", "RED" if errors else "GREEN", summary)
    for error in errors:
        print("  " + error)
    raise SystemExit(bool(errors))
