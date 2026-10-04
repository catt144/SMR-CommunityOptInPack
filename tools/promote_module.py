"""Promote an owned workbench module into production; --check prints a read-only plan."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import workbench as wb


def replace_field(source, field, body):
    start, end = wb.field_span(source, field)
    return source[:start] + body + source[end:]


def remove_code(source, paths):
    start, end = wb.field_span(source, "code")
    body = source[start:end]
    for path in paths:
        body, count = re.subn(r'^\t\t"' + re.escape(path) + r'",\n', "", body, flags=re.M)
        if count != 1:
            raise ValueError(f"expected one canonical code line: {path}")
    return replace_field(source, "code", body)


def insert_code(source, paths):
    start, end = wb.field_span(source, "code")
    body = source[start:end]
    ordinary = [p for p in paths if not p.endswith(".generated.lua")]
    generated = [p for p in paths if p.endswith(".generated.lua")]
    # Preserve comments and existing order; handwritten code precedes all generated files.
    first_generated = re.search(r'^\t\t"Code/[^"\n]+\.generated.lua",', body, re.M)
    point = first_generated.start() if first_generated else len(body)
    body = body[:point] + "".join(f'\t\t"{p}",\n' for p in ordinary) + body[point:]
    body += "".join(f'\t\t"{p}",\n' for p in generated)
    return replace_field(source, "code", body)


def plan(root, name):
    root = Path(root)
    errors, _ = wb.check(root)
    if errors:
        raise ValueError("workbench guard failed: " + "; ".join(errors))
    data = wb.manifest(root)
    if name not in data["modules"]:
        raise ValueError(f"no staged module named {name}")
    module = data["modules"][name]
    stage = root / "staging"
    # Imported model metadata shares SourceData/ArtSpec-mod.lua with other modules.
    # Refuse it until an explicit merge route exists, rather than dropping registrations.
    if any(p.startswith(("SourceData/", "Entities/", "Meshes/", "Materials/", "Textures/", "Fallbacks/"))
           for p in module["files"]):
        raise ValueError("custom model promotion needs an ArtSpec/entities merge; this route supports Code/Data/tools/UI files")
    moves = []
    for rel in module["files"]:
        src, dst = wb.safe_path(stage, rel), wb.safe_path(root, rel)
        if dst.exists():
            raise ValueError(f"destination exists: {rel}")
        moves.append((src, dst))
    # Editor handles are local to a ModDef. Promotion must not collide with production.
    handles = {}
    for folder in (root / "Data", root / "SourceData"):
        for path in folder.rglob("*.lua"):
            for handle in re.findall(r"(?:'mod_handle',|mod_handle\s*=)\s*(\d+)", wb.read(path)):
                handles[handle] = path
    for src, _ in moves:
        if src.suffix == ".lua" and src.relative_to(stage).parts[0] in ("Data", "SourceData"):
            for handle in re.findall(r"(?:'mod_handle',|mod_handle\s*=)\s*(\d+)", wb.read(src)):
                if handle in handles:
                    raise ValueError(f"editor handle {handle} collides with {handles[handle]}")
                handles[handle] = src
    prod_meta, dev_meta = wb.read(root / "metadata.lua"), wb.read(stage / "metadata.lua")
    prod_meta = insert_code(prod_meta, module["code"])
    dev_meta = remove_code(dev_meta, module["code"])
    start, end = wb.field_span(dev_meta, "default_options")
    defaults, moved_defaults = dev_meta[start:end], ""
    for option in module["options"]:
        match = re.search(r'^\t\t' + re.escape(option) + r' = [^\n]+,\n', defaults, re.M)
        if not match:
            raise ValueError(f"expected canonical default: {option}")
        moved_defaults += match[0]
        defaults = defaults[:match.start()] + defaults[match.end():]
    dev_meta = replace_field(dev_meta, "default_options", defaults)
    start, end = wb.field_span(prod_meta, "default_options")
    prod_meta = replace_field(prod_meta, "default_options", prod_meta[start:end] + moved_defaults)
    prod_items, dev_items = wb.read(root / "items.lua"), wb.read(stage / "items.lua")
    moving = []
    for match, item in wb.item_blocks(dev_items):
        if ((item["__class"] == "ModItemCode" and item["CodeFileName"] in module["code"])
                or (item["__class"].startswith("ModItemOption") and item["name"] in module["options"])):
            moving.append(match)
    for match in reversed(moving):
        dev_items = dev_items[:match.start()] + dev_items[match.end():]
    last = re.search(r"^\}\s*$", prod_items, re.M)
    if not last:
        raise ValueError("production items.lua has no canonical closing brace")
    prod_items = prod_items[:last.start()] + "".join(m[0] for m in moving) + prod_items[last.start():]
    del data["modules"][name]
    changes = {
        root / "metadata.lua": prod_meta.encode("utf-8"),
        root / "items.lua": prod_items.encode("utf-8"),
        stage / "metadata.lua": dev_meta.encode("utf-8"),
        stage / "items.lua": dev_items.encode("utf-8"),
        stage / "modules.json": (json.dumps(data, indent=2) + "\n").encode("utf-8"),
    }
    generators = module.get("regenerate", [])
    for script in generators:
        if script not in module["files"] or not script.startswith("tools/") or not script.endswith(".py"):
            raise ValueError(f"invalid regeneration script: {script}")
    return moves, changes, generators


def run_gate(root, args):
    print("GATE:", " ".join(args), flush=True)
    subprocess.run([sys.executable, *args], cwd=root, check=True)


def promote(root, name, check_only=False, gate=run_gate):
    root = Path(root)
    moves, changes, generators = plan(root, name)
    print("CHECK" if check_only else "PROMOTE", name)
    for src, dst in moves:
        print(f"  MOVE {src.relative_to(root).as_posix()} -> {dst.relative_to(root).as_posix()}")
    for path in changes:
        print("  EDIT", path.relative_to(root).as_posix())
    for script in generators:
        print("  REGENERATE", script)
    if check_only:
        return
    # Capture exact bytes, including existing shared-tree edits. Refuse a race before writing.
    paths = set(changes) | {p for pair in moves for p in pair}
    before = {p: p.read_bytes() if p.exists() else None for p in paths}
    # Replanning reads shared files again, detecting changes since the first plan.
    if plan(root, name) != (moves, changes, generators):
        raise ValueError("shared files changed while planning; retry")
    created_dirs = set()
    try:
        for src, dst in moves:
            for parent in dst.parents:
                if parent == root or parent.exists():
                    break
                created_dirs.add(parent)
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dst)
        for path, body in changes.items():
            path.write_bytes(body)
        for script in generators:
            gate(root, [script])
        for _, dst in moves:
            if dst.relative_to(root).parts[0] in ("Code", "Data", "UI") and dst.suffix in (".lua", ".json"):
                if "Mod/" + wb.WORKBENCH_ID in wb.read(dst):
                    raise ValueError(f"promoted content still points at workbench: {dst.relative_to(root)}")
        gate(root, ["tools/workbench.py"])
        gate(root, ["tools/parsecheck.py", "--quiet"])
        gate(root, ["tools/doccheck.py"])
    except BaseException:
        # Rollback is limited to the reviewed move/edit set; no recursive deletion.
        for path, body in before.items():
            if body is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
        for folder in sorted(created_dirs, key=lambda p: len(p.parts), reverse=True):
            try:
                folder.rmdir()
            except OSError:
                pass
        print("ROLLED BACK: promotion gates failed; original touched bytes restored", flush=True)
        raise
    print("PROMOTED:", name, "— review docs/release outbox, then commit the printed paths")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        promote(wb.ROOT, args.name, args.check)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print("REFUSED:", exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
