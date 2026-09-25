#!/usr/bin/env python3
# Provenance: carried from the fix pack 2026-08-31 — tools/README.md readiness tooling port.
# Re-synced 2026-09-18 to SMR-BugFixPack @ 9d15550 (predict(), link reporting).
"""Predict the file list DbgPackMod will put into ModContent.fpk.

Mirrors GedModEditor.lua:716-732 exactly:
    AsyncListFiles(content_path, nil, "recursive")  -> every file, recursively
    for each ignore_files filter: MatchWildcard(file, filter) -> skip
    dst = string.sub(file, #content_path + 1)

MatchWildcard: `*` crosses `/` (MEASURED 2026-08-17 against the real .fpk,
seed note in the fix pack's SWEEP_LEDGER.md), `?` is one char. Case-insensitive is NOT
assumed; the patterns and the tree agree in case anyway.

IGNORE below is a literal copy of THIS repo's metadata.lua `ignore_files`, in
order — not the fix pack's list, because it predicts what this mod ships. Edit
both in one commit: doccheck's `pack_ignore_parity` fails when they disagree.

⛔ JUNCTIONS AND SYMLINKS. The engine's recursive listing walks through a
directory junction as if it were a folder. 2026-09-16, in the fix pack: a
junction to the user's Claude projects folder inside the mod folder put ~1.2 GB of private
session transcripts into the pack list; the pack then failed silently
(DbgPackMod ignores CreatePackageForUpload's error and opens `explorer ""`).
`predict()` reports every reparse point it meets and does not descend into it,
so a caller can refuse the upload instead of silently walking the link.

Usage: python tools/pack_predict.py <mod-root> [--json]
"""
import os
import re
import stat
import sys
import json

# The Windows console defaults to cp1252; the report speaks ⛔ and —.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

# from metadata.lua 'ignore_files' — kept in order by doccheck PACK IGNORE PARITY
IGNORE = [
    "*.git/*",
    "*.svn/*",
    "*/Source/*",
    "*/SourceData/*",
    "*/docs/*",
    "*/.agents/*",
    "*/.claude/*",
    "*/tools/*",
    "*README.md",
    "*CLAUDE.md",
    "*AGENTS.md",
    "*.gitignore",
    "*.rgignore",
    "*.gitattributes",
    "*/local/*",
    "*/scratch/*",
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


def is_reparse_point(path):
    """True for a symlink or a Windows junction (any reparse point)."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    if stat.S_ISLNK(st.st_mode):
        return True
    return bool(getattr(st, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def predict(root, patterns=IGNORE):
    """Walk <root> the way the packer does, without following links.

    Returns (packed, ignored, links): packed = [(rel, size)], ignored =
    [(rel, pattern)], links = [(rel, ignored_pattern_or_None)] for every
    reparse point met. A link whose contents would be packed has None.
    """
    pats = [(p, to_regex(p)) for p in patterns]

    def hit(rel):
        full = CONTENT_PREFIX + rel
        return next((p for p, rx in pats if rx.match(full)), None)

    packed, ignored, links = [], [], []
    for dirpath, dirnames, filenames in os.walk(root):
        keep = []
        for d in dirnames:
            abs_d = os.path.join(dirpath, d)
            rel_d = os.path.relpath(abs_d, root).replace(os.sep, "/")
            if d == ".git" and dirpath == root:
                continue
            if is_reparse_point(abs_d):
                # a file inside it is what the packer would test
                links.append((rel_d, hit(rel_d + "/x")))
                continue
            keep.append(d)
        dirnames[:] = keep
        for fn in sorted(filenames):
            abs_p = os.path.join(dirpath, fn)
            rel = os.path.relpath(abs_p, root).replace(os.sep, "/")
            if is_reparse_point(abs_p):
                links.append((rel, hit(rel)))
                continue
            pat = hit(rel)
            if pat:
                ignored.append((rel, pat))
            else:
                packed.append((rel, os.path.getsize(abs_p)))
    packed.sort()
    return packed, ignored, links


def main():
    root = sys.argv[1]
    as_json = "--json" in sys.argv
    packed, ignored, links = predict(root)
    names = [rel for rel, _ in packed]

    if as_json:
        print(json.dumps({"packed": names, "count": len(names),
                          "bytes": sum(s for _, s in packed),
                          "links": [{"path": r, "ignored_by": p} for r, p in links]},
                         indent=1))
        return

    print(f"PREDICTED PACK CONTENTS — {len(names)} files, "
          f"{sum(s for _, s in packed):,} bytes\n")
    buckets = {}
    for f in names:
        top = f.split("/")[0] if "/" in f else "(root)"
        buckets.setdefault(top, []).append(f)
    for top in sorted(buckets):
        print(f"  {top:<12} {len(buckets[top]):>4}")
    print()
    for f in names:
        if not f.startswith("Code/"):
            print("   ", f)
    print(f"\n  Code/*.lua : {sum(1 for f in names if f.startswith('Code/') and f.endswith('.lua'))}")
    if links:
        print(f"\nLINKS (junction/symlink, not followed) — {len(links)}")
        for rel, pat in links:
            print(f"  {rel:<40} {'ignored by ' + pat if pat else '⛔ WOULD BE PACKED'}")
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
