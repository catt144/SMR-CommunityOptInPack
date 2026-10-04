#!/usr/bin/env python3
"""List a Surviving Mars .fpk WITHOUT extracting it, and reconcile it
against the tree it was supposed to be built from.

Reuses tools/flpk_extract.py's directory-table parser verbatim (imported,
not copied) so this tool cannot drift from the extractor the project already
falsifier-tested.

Usage:
  python tools/pack_list.py <ModContent.fpk> [--tree <mod-root>] [--names]
                            [--allow-differ <member>]...

With --tree the exit code is the verdict: 0 only when the names match and every member was
read and is byte-identical (allowed differences aside); 1 on a missing, extra, differing or
unread member.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import os
import shutil
import struct
import sys
import tempfile

# The Windows console defaults to cp1252 and this tool prints the project's
# non-ASCII vocabulary; without this it dies on its own output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass


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
    ap.add_argument("--allow-differ", action="append", default=[], metavar="NAME",
                    help="a member expected to differ from the tree (repeatable)")
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
        res = reconcile(a.fpk, a.tree, files, set(a.allow_differ))
        return 0 if res["ok"] else 1
    return 0


def reconcile(fpk, tree, files, allow_differ=frozenset()):
    """Names AND bytes of the archive against the tree. -> dict; ["ok"] is the verdict.

    ok is False on any of: a predicted file absent from the archive, an archive member
    absent from the prediction, a member whose bytes differ from disk, and a member this
    could not READ (the extractor skipped it, warned on its length, or wrote nothing).
    An unread member is never counted as matching. `allow_differ` names members whose
    difference is expected and declared by the caller (the editor's writeback rewrites
    `metadata.lua` and `items.lua` after a pack is built); they are printed as ALLOWED,
    every other difference still fails, and an allowed name that is missing still fails.

    Local adaptation, 2026-10-03 (final launch audit F3): the donor's copy returns 0 on a
    byte difference and skips unread members. Declared in sync_from_fixpack.TOOLS_ADAPTED.
    """
    sys.path.insert(0, HERE)
    import pack_predict as predict_pack  # noqa
    # predict() walks the way the packer does and builds its regexes from IGNORE, so
    # this cannot drift from the predictor.
    packed, _ignored, _links = predict_pack.predict(tree)
    want = {rel for rel, _size in packed}
    have = {n for n, _f, _o, _s in files}
    print(f"\nRECONCILE against {tree}")
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
        print("  [OK] names match")

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
    same, diff, allowed, unread = 0, [], [], []
    try:
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            fx.extract(fpk, tmp)
        # The extractor reports what it could not read on stdout: `SKIP <name>:` for an
        # unknown storage flag and `WARN <name>:` for a length that disagrees with the header.
        flagged = {ln.split()[1].rstrip(":") for ln in log.getvalue().splitlines()
                   if ln.strip().startswith(("SKIP ", "WARN "))}
        for name, _fl, _off, _size in files:
            got = os.path.join(tmp, name.replace("/", os.sep))
            disk = os.path.join(tree, name.replace("/", os.sep))
            if name in flagged or not os.path.isfile(got):
                unread.append(name)
            elif not os.path.isfile(disk):
                continue            # already listed under "in archive, NOT in tree"
            elif open(got, "rb").read() == open(disk, "rb").read():
                same += 1
            elif name in allow_differ:
                allowed.append(name)
            else:
                diff.append(name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n  CONTENT: {same} byte-identical to disk, {len(diff)} differ, "
          f"{len(allowed)} allowed difference(s), {len(unread)} unread")
    for d in diff:
        print(f"      DIFFERS {d}")
    for d in allowed:
        print(f"      ALLOWED {d}  (declared by the caller)")
    for d in unread:
        print(f"      UNREAD  {d}  (not extracted; never counted as matching)")
    ok = not (missing or extra or diff or unread)
    print("\n  VERDICT: %s" % ("EXACT MATCH" + (" except the allowed difference(s)" if allowed else "")
                               if ok else "MISMATCH — exit 1"))
    return {"ok": ok, "predicted": len(want), "in_archive": len(have), "missing": missing,
            "extra": extra, "identical": same, "differ": diff, "allowed": allowed,
            "unread": unread}


if __name__ == "__main__":
    sys.exit(main())
