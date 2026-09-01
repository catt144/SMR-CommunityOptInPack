#!/usr/bin/env python3
"""List a Surviving Mars .fpk WITHOUT extracting it, and reconcile it
against the tree it was supposed to be built from.

Reuses tools/flpk_extract.py's directory-table parser verbatim (imported,
not copied) so this tool cannot drift from the extractor the project already
falsifier-tested.

Usage:
  python tools/pack_list.py <ModContent.fpk> [--tree <mod-root>] [--names]
"""
import argparse
import hashlib
import importlib.util
import os
import shutil
import struct
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def load_extractor():
    path = os.path.join(REPO, "tools", "flpk_extract.py")
    spec = importlib.util.spec_from_file_location("flpk_extract", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def listing(fpk_path):
    fx = load_extractor()
    buf = open(fpk_path, "rb").read()
    if buf[:4] != b"FLPK":
        sys.exit(f"not an FLPK archive: {fpk_path}")
    dir_off = struct.unpack_from("<I", buf, 0x0C)[0]
    dir_size = struct.unpack_from("<I", buf, 0x14)[0]
    files = []
    fx.parse_table(buf, dir_off, dir_size, dir_off, "", files)
    return buf, files


FLAG = {0x10: "stored", 0x30: "zstd"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fpk")
    ap.add_argument("--tree", help="mod root to reconcile against")
    ap.add_argument("--names", action="store_true", help="print every entry")
    a = ap.parse_args()

    buf, files = listing(a.fpk)
    files.sort(key=lambda r: r[0])
    print(f"ARCHIVE  {a.fpk}")
    print(f"  size   {os.path.getsize(a.fpk):,} bytes")
    print(f"  md5    {hashlib.md5(buf).hexdigest()}")
    print(f"  mtime  {__import__('datetime').datetime.fromtimestamp(os.path.getmtime(a.fpk))}")
    print(f"  ENTRIES {len(files)}\n")

    buckets, flags = {}, {}
    for name, fl, off, size in files:
        top = name.split("/")[0] if "/" in name else "(root)"
        buckets.setdefault(top, []).append(name)
        flags[FLAG.get(fl, hex(fl))] = flags.get(FLAG.get(fl, hex(fl)), 0) + 1
    for top in sorted(buckets):
        print(f"  {top:<14} {len(buckets[top]):>4}")
    print("\n  storage:", ", ".join(f"{k}={v}" for k, v in sorted(flags.items())))

    print("\n  non-Code entries:")
    for name, fl, off, size in files:
        if not name.startswith("Code/"):
            print(f"    {name:<40} {FLAG.get(fl, fl):<7} {size:>8,} B")

    if a.names:
        print("\n  all entries:")
        for name, fl, off, size in files:
            print(f"    {name}")

    if a.tree:
        sys.path.insert(0, HERE)
        import pack_predict as predict_pack  # noqa
        want = set()
        for dirpath, _dn, fns in os.walk(a.tree):
            for fn in fns:
                rel = os.path.relpath(os.path.join(dirpath, fn), a.tree).replace(os.sep, "/")
                full = predict_pack.CONTENT_PREFIX + rel
                if not any(rx.match(full) for _p, rx in predict_pack.PATS):
                    want.add(rel)
        have = {n for n, _f, _o, _s in files}
        print(f"\nRECONCILE against {a.tree}")
        print(f"  predicted {len(want)} · in archive {len(have)}")
        missing = sorted(want - have)
        extra = sorted(have - want)
        print(f"  [!] in tree, NOT in archive : {len(missing)}")
        for m in missing:
            print(f"      {m}")
        print(f"  [!] in archive, NOT in tree : {len(extra)}")
        for e in extra:
            print(f"      {e}")
        if not missing and not extra:
            print("  [OK] exact match")

        # ---- content reconcile. The NAME list says the packer picked the right
        # files; only this says it did not TRANSFORM them. Measured 2026-08-19
        # against the engine-built 08-17 archive: 78 of 80 byte-identical, and
        # the 2 that differed were exactly `git diff 7824cbc..HEAD`.
        # ⛔ Extraction goes through flpk_extract's OWN extract(), never a
        # reimplementation. A hand-rolled "scan for zstd frame magics" pass was
        # written here first and reported 7 files differing where the real
        # extractor reports 2 — the magic bytes occur inside compressed data,
        # so the naive split silently truncates multi-chunk files. Instrument
        # defect found and disclosed rather than shipped.
        fx = load_extractor()
        tmp = tempfile.mkdtemp(prefix="fpklist_")
        try:
            fx.extract(a.fpk, tmp)
            same, diff = 0, []
            for name, _fl, _off, _size in files:
                got = os.path.join(tmp, name.replace("/", os.sep))
                disk = os.path.join(a.tree, name.replace("/", os.sep))
                if not (os.path.exists(got) and os.path.exists(disk)):
                    continue
                if open(got, "rb").read() == open(disk, "rb").read():
                    same += 1
                else:
                    diff.append(name)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        print(f"\n  CONTENT: {same} byte-identical to disk, {len(diff)} differ")
        for d in diff:
            print(f"      DIFFERS {d}")
        return 0 if not missing and not extra else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
