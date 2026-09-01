#!/usr/bin/env python3
# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
"""Predict the file list DbgPackMod will put into ModContent.fpk.

Mirrors GedModEditor.lua:716-732 exactly:
    AsyncListFiles(content_path, nil, "recursive")  -> every file, recursively
    for each ignore_files filter: MatchWildcard(file, filter) -> skip
    dst = string.sub(file, #content_path + 1)

MatchWildcard: `*` crosses `/` (MEASURED 2026-08-17 against the real .fpk,
seed note in the fix pack's SWEEP_LEDGER.md), `?` is one char. Case-insensitive is NOT
assumed; the patterns and the tree agree in case anyway.

Usage: python tools/pack_predict.py <mod-root> [--json]
"""
import os
import re
import sys
import json

# The Windows console defaults to cp1252 and this tool prints the project's
# non-ASCII vocabulary; without this it dies on its own output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass


# from metadata.lua 'ignore_files'
IGNORE = [
    "*.git/*",
    "*.svn/*",
    "*/Source/*",
    "*/SourceData/*",
    "*/docs/*",
    "*/.claude/*",
    "*/tools/*",
    "*README.md",
    "*CLAUDE.md",
    "*.gitignore",
    "*.gitattributes",
]

# the engine hands paths with forward slashes and the content_path prefix
CONTENT_PREFIX = "AppData/Mods/SMR_CommunityOptInPack/"


def to_regex(pat):
    out = []
    for ch in pat:
        if ch == "*":
            out.append(".*")
        elif ch == "?":
            out.append(".")
        else:
            out.append(re.escape(ch))
    return re.compile("^" + "".join(out) + "$")


PATS = [(p, to_regex(p)) for p in IGNORE]


def main():
    root = sys.argv[1]
    as_json = "--json" in sys.argv
    packed, ignored = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in sorted(filenames):
            abs_p = os.path.join(dirpath, fn)
            rel = os.path.relpath(abs_p, root).replace(os.sep, "/")
            full = CONTENT_PREFIX + rel
            hit = next((p for p, rx in PATS if rx.match(full)), None)
            if hit:
                ignored.append((rel, hit))
            else:
                packed.append(rel)
    packed.sort()

    if as_json:
        print(json.dumps({"packed": packed, "count": len(packed)}, indent=1))
        return

    print(f"PREDICTED PACK CONTENTS — {len(packed)} files\n")
    buckets = {}
    for f in packed:
        top = f.split("/")[0] if "/" in f else "(root)"
        buckets.setdefault(top, []).append(f)
    for top in sorted(buckets):
        print(f"  {top:<12} {len(buckets[top]):>4}")
    print()
    for f in packed:
        if not f.startswith("Code/"):
            print("   ", f)
    print(f"\n  Code/*.lua : {sum(1 for f in packed if f.startswith('Code/') and f.endswith('.lua'))}")
    print(f"\nIGNORED — {len(ignored)} files, by pattern")
    bypat = {}
    for rel, pat in ignored:
        bypat.setdefault(pat, []).append(rel)
    for pat in IGNORE:
        n = len(bypat.get(pat, []))
        print(f"  {pat:<20} {n:>5}")
    unused = [p for p in IGNORE if p not in bypat]
    if unused:
        print("\n  patterns that matched NOTHING: " + ", ".join(unused))


if __name__ == "__main__":
    main()
