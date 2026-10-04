"""Generate the Arboretum editor preset and class from template.json; --check is read-only."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = next(p for p in Path(__file__).resolve().parents if (p / "tools/doccheck.py").is_file())
SOURCE = Path(__file__).with_name("template.json")


def lua(value):
    if isinstance(value, dict):
        if "text" in value:
            return "Untranslated(" + lua(value["text"]) + ")"
        return "set(" + ", ".join(map(lua, value["set"])) + ")"
    return json.dumps(value, ensure_ascii=False)


def outputs():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    name, props = data["id"], data["properties"]
    own_preset = ROOT / f"Data/BuildingTemplate/{name}.lua"
    for folder in (ROOT / "Data", ROOT / "SourceData"):
        for path in folder.rglob("*.lua"):
            if path == own_preset:
                continue
            handles = re.findall(r"(?:'mod_handle',|mod_handle\s*=)\s*(\d+)", path.read_text(encoding="utf-8"))
            if str(data["handle"]) in handles:
                raise SystemExit(f"mod_handle collision: {path}")
    route = Path(__file__).resolve().parent.relative_to(REPO).as_posix()
    banner = f"-- GENERATED: python {route}/generate.py; source {route}/template.json\n\n"
    mod_id = re.search(r"'id',\s*\"([^\"]+)\"", (ROOT / "metadata.lua").read_text(encoding="utf-8"))[1]
    fields = dict(Group="Decorations", Id=name, SaveIn="Mod/" + mod_id,
                  mod_handle=data["handle"], **props)
    preset = banner + "PlaceObj('ModItemBuildingTemplate', {\n"
    preset += "".join(f"\t'{key}', {lua(value)},\n" for key, value in fields.items()) + "})\n"
    cls = banner + f"UndefineClass('{name}')\nDefineClass.{name} = {{\n"
    cls += f'\t__parents = {{ "{props["object_class"]}" }},\n'
    cls += '\t__generated_by_class = "ModItemBuildingTemplate",\n'
    cls += f'\tmod_handle = {data["handle"]},\n'
    cls += "".join(f"\t{key} = {lua(value)},\n" for key, value in props.items())
    cls += f'\tpersist_baseclass = "{props["object_class"]}",\n}}\n'
    return {ROOT / f"Data/BuildingTemplate/{name}.lua": preset,
            ROOT / f"Code/BuildingTemplate/{name}.generated.lua": cls}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, body in outputs().items():
        if args.check:
            if not path.exists() or path.read_bytes() != body.encode("utf-8"):
                raise SystemExit(f"STALE: {path}")
        else:
            path.write_bytes(body.encode("utf-8"))
    print("Arboretum template/class: " + ("fresh" if args.check else "generated"))
