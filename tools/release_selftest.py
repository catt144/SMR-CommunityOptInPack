#!/usr/bin/env python3
"""Falsifier for the release gates: store parity, package comparison and batch recovery.

Built 2026-10-03 for the final launch audit's F2-F4. Every leg runs the PRODUCTION code
(`store_parity.main`, `pack_list.reconcile`, `release_batch.main`) against scratch fixtures:
no production file is read for a verdict or written. Each failure control sits beside a
success control, because a gate only ever seen passing has not been tested.

  parity   first publication, staged update over an older live copy, confirmed update with
           dated history, live card missing a body, a damaged word, a card with no state,
           a pre-publication card holding a body, a missing source document
  package  exact match, changed bytes, missing member, extra member, unread member,
           a declared allowed difference, an allowed difference beside an undeclared one
  batch    first publish, partial upload, allocated-id-but-failed-upload, interrupted close,
           a later Pending entry during the hold, an ordinary update after a live release,
           a stale held-out row, a tampered launch tree

    python tools/release_selftest.py        exit 0 when every leg holds, 1 otherwise
"""
import contextlib
import io
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack_list  # noqa: E402
import release_batch  # noqa: E402
import store_parity  # noqa: E402

RESULTS = []


def leg(label, ok, detail=""):
    RESULTS.append(bool(ok))
    print("  %-4s %s%s" % ("PASS" if ok else "FAIL", label, ("  — " + detail) if detail and not ok else ""))


def run(fn, *args, **kw):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = fn(*args, **kw)
    return code, out.getvalue()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


# ── parity ───────────────────────────────────────────────────────────────────
PARADOX = "Lede line.\n\nTHE MODULES\n\n· One. Does a thing."
STEAM = "Lede line.\n\n[h2]The modules[/h2]\n[list]\n[*]One. Does a thing.\n[/list]"


def source_doc(paradox=PARADOX, steam=STEAM):
    return "\n".join([
        store_parity.H_SUMMARY, "", "```", "Short.", "```", "",
        store_parity.H_PARADOX, "", "```", paradox, "```", "",
        store_parity.H_STEAM, "", "```", steam, "```", "",
        store_parity.H_CHANGE, "", "```", "Note.", "```", ""])


def metadata(paradox=PARADOX):
    return ("return PlaceObj('ModDef', {\n\t'description', \"%s\",\n\t'short_description', \"Short.\",\n"
            "\t'last_changes', \"Note.\",\n})\n" % store_parity.lua_escape(paradox))


def card(state, paradox=None, steam=None, history=""):
    text = "# Store card\n\n## State: %s\n\nwords\n" % state if state else "# Store card\n\nwords\n"
    if paradox is not None or steam is not None:
        text += "\n" + store_parity.CARD_CURRENT + "\n\n"
        if paradox is not None:
            text += "%s\n\n```\n%s\n```\n\n" % (store_parity.H_PARADOX, paradox)
        if steam is not None:
            text += "%s\n\n```\n%s\n```\n\n" % (store_parity.H_STEAM, steam)
    return text + history


def parity_legs(tmp):
    src, meta, crd = (os.path.join(tmp, n) for n in ("source.md", "metadata.lua", "card.md"))

    def case(card_text, *flags, paradox=PARADOX, steam=STEAM):
        write(src, source_doc(paradox, steam))
        write(meta, metadata(paradox))
        write(crd, card_text)
        return run(store_parity.main, ["--source", src, "--metadata", meta, "--card", crd] + list(flags))

    old_p, old_s = PARADOX.replace("a thing", "an older thing"), STEAM.replace("a thing", "an older thing")
    history = ("\n## ⭐ 2026-01-01 — the first body\n\n%s\n\n```\n%s\n```\n\n%s\n\n```\n%s\n```\n"
               % (store_parity.H_PARADOX, old_p, store_parity.H_STEAM, old_s))

    code, out = case(card("PRE-PUBLICATION"))
    leg("parity: first publication prepares (pre-publication card, no body)", code == 0 and "pre-publication" in out, out)
    code, out = case(card("PRE-PUBLICATION"), "--confirm-live")
    leg("parity: --confirm-live refuses a pre-publication card", code == 1, out)
    code, out = case(card("LIVE", old_p, old_s))
    leg("parity: staged update over an older live copy prepares, and is reported", code == 0 and "DIFFER" in out, out)
    code, out = case(card("LIVE", old_p, old_s), "--confirm-live")
    leg("parity: --confirm-live fails while the card still holds the older copy", code == 1, out)
    code, out = case(card("LIVE", PARADOX, STEAM, history), "--confirm-live")
    leg("parity: confirmed update passes; dated history is never selected", code == 0, out)
    code, out = case(card("LIVE", PARADOX, STEAM))
    leg("parity: nothing staged over a live copy prepares", code == 0 and "equal" in out, out)
    code, out = case(card("LIVE", PARADOX, None))
    leg("parity: live card missing one body FAILS (audit F2 false GREEN)", code == 1, out)
    code, out = case(card("LIVE", PARADOX, None, history))
    leg("parity: a missing current body is not satisfied from history", code == 1, out)
    code, out = case(card("LIVE", PARADOX.replace("thing", "thinq"), STEAM), "--confirm-live")
    leg("parity: one damaged word in the live copy FAILS --confirm-live", code == 1, out)
    code, out = case(card(None, PARADOX, STEAM))
    leg("parity: a card with no state line FAILS", code == 1, out)
    code, out = case(card("PRE-PUBLICATION", PARADOX, STEAM))
    leg("parity: a pre-publication card holding a body FAILS", code == 1, out)
    write(meta, metadata(PARADOX.replace("Lede", "Lead")))
    code, out = run(store_parity.main, ["--source", src, "--metadata", meta, "--card", crd])
    leg("parity: metadata description differing from the block FAILS", code == 1, out)
    code, out = run(store_parity.main, ["--source", os.path.join(tmp, "absent.md"), "--metadata", meta, "--card", crd])
    leg("parity: a missing source document FAILS (no report fallback)", code == 1 and "note:" not in out, out)


# ── package ──────────────────────────────────────────────────────────────────
def build_fpk(path, members):
    """A minimal stored FLPK, root files only. members: [(name, bytes, flags)]."""
    payload, table, off = b"", b"", 32
    for name, data, flags in members:
        nb = name.encode()
        table += struct.pack("<III", off, (len(nb) << 24) | (flags << 16), len(data)) + nb + bytes(4)
        payload += data
        off += len(data)
    header = bytearray(32)
    header[:4] = b"FLPK"
    struct.pack_into("<I", header, 12, 32 + len(payload))
    struct.pack_into("<I", header, 20, len(table))
    open(path, "wb").write(bytes(header) + payload + table)


def package_legs(tmp):
    tree = os.path.join(tmp, "tree")
    fpk = os.path.join(tmp, "fixture.fpk")

    def case(tree_files, members, allow=()):
        shutil.rmtree(tree, ignore_errors=True)
        for name, data in tree_files.items():
            os.makedirs(tree, exist_ok=True)
            open(os.path.join(tree, name), "wb").write(data)
        build_fpk(fpk, members)
        _buf, files = pack_list.listing(fpk)
        res, out = run(pack_list.reconcile, fpk, tree, files, set(allow))
        return res, out

    two = {"items.lua": b"items\n", "metadata.lua": b"meta\n"}
    stored = [("items.lua", b"items\n", 0x10), ("metadata.lua", b"meta\n", 0x10)]
    res, out = case(two, stored)
    leg("package: exact names and bytes PASS", res["ok"] and res["identical"] == 2, out)
    res, out = case(two, [("items.lua", b"ITEMS\n", 0x10), stored[1]])
    leg("package: changed bytes FAIL (audit F3 exit 0)", not res["ok"] and res["differ"] == ["items.lua"], out)
    res, out = case(two, stored[:1])
    leg("package: a tree file missing from the archive FAILS", not res["ok"] and res["missing"] == ["metadata.lua"], out)
    res, out = case({"items.lua": b"items\n"}, stored)
    leg("package: an archive member absent from the tree FAILS", not res["ok"] and res["extra"] == ["metadata.lua"], out)
    res, out = case(two, [stored[0], ("metadata.lua", b"meta\n", 0x20)])
    leg("package: an unread member FAILS and is not counted as matching",
        not res["ok"] and res["unread"] == ["metadata.lua"] and res["identical"] == 1, out)
    res, out = case(two, [stored[0], ("metadata.lua", b"META\n", 0x10)], allow=["metadata.lua"])
    leg("package: a declared allowed difference PASSES and is listed", res["ok"] and res["allowed"] == ["metadata.lua"], out)
    res, out = case(two, [("items.lua", b"ITEMS\n", 0x10), ("metadata.lua", b"META\n", 0x10)], allow=["metadata.lua"])
    leg("package: an undeclared difference beside an allowed one FAILS", not res["ok"] and res["differ"] == ["items.lua"], out)
    build_fpk(fpk, stored)
    shutil.rmtree(tree, ignore_errors=True)
    os.makedirs(tree)
    open(os.path.join(tree, "items.lua"), "wb").write(b"other\n")
    open(os.path.join(tree, "metadata.lua"), "wb").write(b"meta\n")
    p = subprocess.run([sys.executable, os.path.join(HERE, "pack_list.py"), fpk, "--tree", tree],
                       capture_output=True)
    leg("package: the command line exits 1 on changed bytes", p.returncode == 1, str(p.returncode))


# ── batch ────────────────────────────────────────────────────────────────────
META = """-- a hand comment the editor would strip
return PlaceObj('ModDef', {
\t'title', "Fixture",
\t'id', "Fixture",
\t'version_major', 1,
\t'version', 1,
%s})
"""
OUTBOX = """# Outbox

## Pending — goes out with the next upload

### Pending · First thing (2026-10-03)
- one

### Pending · Second thing (2026-10-03)
- two

## Last released

**Nothing yet.**
"""


def git(repo, *args):
    subprocess.run(("git",) + args, cwd=repo, check=True, capture_output=True)


def batch_legs(tmp):
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    ctx = release_batch.Ctx(repo=repo, launch=os.path.join(tmp, "launch"),
                            pack=os.path.join(tmp, "Pack", "ModContent.fpk"),
                            mods_link=os.path.join(tmp, "Mods", "link"),
                            held_out={"Code/Opt_Held.lua": "fixture ruling"},
                            held_tokens=("HeldThing",), untracked=())
    write(os.path.join(repo, "metadata.lua"), META % "")
    write(os.path.join(repo, "items.lua"), "return {\n}\n")
    write(os.path.join(repo, "Code", "Opt_A.lua"), 'SMROptInPack.Register("A", {})\n')
    write(os.path.join(repo, "Code", "Opt_Held.lua"), 'SMROptInPack.Register("HeldThing", {})\n')
    write(ctx.outbox, OUTBOX)
    write(ctx.history, "# Release history\n")
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "selftest@example.invalid")
    git(repo, "config", "user.name", "selftest")
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    launch_meta = os.path.join(ctx.launch, "metadata.lua")

    def rb(*argv):
        return run(release_batch.main, list(argv), ctx)

    def editor_save(extra):
        # what the editor's SaveWholeMod leaves: no comments, new fields
        write(launch_meta, (META % extra).split("\n", 1)[1])

    def upload_pack(data):
        os.makedirs(os.path.dirname(ctx.pack), exist_ok=True)
        open(ctx.pack, "wb").write(data)

    code, out = rb("status")
    leg("batch: Pending with no open batch is NEW_BATCH", "RELEASE STATE: NEW_BATCH" in out, out)
    stale = release_batch.Ctx(repo=repo, launch=ctx.launch, pack=ctx.pack, mods_link=ctx.mods_link,
                              held_out={"Code/Gone.lua": "x"}, held_tokens=(), untracked=())
    code, out = run(release_batch.main, ["begin"], stale)
    leg("batch: a held-out row naming an untracked path refuses begin", code == 1 and "HELD_OUT" in out, out)

    # uncommitted work in the repo must never reach the launch tree
    write(os.path.join(repo, "Code", "Opt_Dirty.lua"), "-- uncommitted peer work\n")
    code, out = rb("begin")
    leg("batch: begin opens a first-publish batch", code == 0 and "first-publish" in out, out)
    held_absent = not os.path.exists(os.path.join(ctx.launch, "Code", "Opt_Held.lua"))
    dirty_absent = not os.path.exists(os.path.join(ctx.launch, "Code", "Opt_Dirty.lua"))
    leg("batch: launch tree omits held-out and uncommitted files, keeps the rest",
        held_absent and dirty_absent and os.path.isfile(os.path.join(ctx.launch, "Code", "Opt_A.lua")))
    code, out = rb("verify")
    leg("batch: verify passes on the pinned tree", code == 0 and "registered modules (1): A" in out, out)
    write(os.path.join(ctx.launch, "Code", "Opt_Stray.lua"), "-- stray\n")
    code, out = rb("verify")
    leg("batch: verify FAILS on a file added to the launch tree", code == 1, out)
    os.remove(os.path.join(ctx.launch, "Code", "Opt_Stray.lua"))
    write(os.path.join(ctx.launch, "Code", "Opt_A.lua"), 'SMROptInPack.Register("A", {}) -- HeldThing\n')
    code, out = rb("verify")
    leg("batch: verify FAILS on a held token / changed non-editor file", code == 1, out)
    write(os.path.join(ctx.launch, "Code", "Opt_A.lua"), 'SMROptInPack.Register("A", {})\n')
    code, out = rb("status")
    leg("batch: prepared batch reads PREPARED", "RELEASE STATE: PREPARED" in out, out)
    code, out = rb("begin")
    leg("batch: a second begin on an open batch is refused", code == 1, out)
    code, out = rb("snapshot", "paradox")
    leg("batch: snapshot with no package is refused, not invented", code == 1, out)

    # Paradox succeeds: the package is built, then ids are written back
    upload_pack(b"FLPK paradox package")
    editor_save("\t'pdx_id', 111,\n\t'pdx_version', 1,\n\t'version', 2,\n".replace("\t'version', 2,\n", ""))
    code, out = rb("snapshot", "paradox")
    leg("batch: paradox snapshot keeps the package and serializer output", code == 0, out)
    code, out = rb("snapshot", "paradox")
    leg("batch: repeating a snapshot is a no-op", code == 0 and "already kept" in out, out)
    code, out = rb("snapshot", "steam")
    leg("batch: the paradox package is refused as the steam snapshot", code == 1, out)
    code, out = rb("status")
    leg("batch: writeback without a receipt is UPLOADING, paradox UNCONFIRMED",
        "RELEASE STATE: UPLOADING" in out and re.search(r"paradox\s+UNCONFIRMED", out), out)
    rb("receipt", "paradox", "uploaded", "paradox page shows it")
    code, out = rb("status")
    leg("batch: one confirmed portal is PARTIAL", "RELEASE STATE: PARTIAL" in out and re.search(r"steam\s+OWED", out), out)
    code, out = rb("drain")
    leg("batch: drain is refused on a partial upload", code == 1, out)

    # Steam allocates an id and saves, then the upload fails
    editor_save("\t'pdx_id', 111,\n\t'pdx_version', 1,\n\t'steam_id', \"999\",\n")
    code, out = rb("status")
    leg("batch: an allocated steam_id alone is UNCONFIRMED, never an upload",
        "RELEASE STATE: PARTIAL" in out and re.search(r"steam\s+UNCONFIRMED", out) and "not an upload" in out, out)
    rb("receipt", "steam", "failed", "steam said upload failed")
    code, out = rb("status")
    leg("batch: a failed receipt reads FAILED and keeps the batch PARTIAL",
        "RELEASE STATE: PARTIAL" in out and re.search(r"steam\s+FAILED", out), out)
    code, out = rb("drain")
    leg("batch: drain is refused after an allocated id and a failed upload", code == 1, out)
    code, out = rb("abandon", "give up")
    leg("batch: abandon is refused once any portal shows activity", code == 1, out)

    # a later change lands in Pending during the hold
    write(ctx.outbox, read(ctx.outbox).replace("## Last released", "### Pending · Later thing (2026-10-04)\n- three\n\n## Last released"))

    # Steam retried and succeeds with a NEW package
    upload_pack(b"FLPK steam package, built again")
    code, out = rb("snapshot", "steam")
    leg("batch: steam snapshot keeps the second, different package", code == 0, out)
    rb("receipt", "steam", "uploaded", "workshop page shows it")
    code, out = rb("status")
    leg("batch: both receipts read CLOSE_OWED with every close step listed",
        "RELEASE STATE: CLOSE_OWED" in out and out.count("close step owed") == 3
        and "NOT in this batch, stays Pending: ### Pending · Later thing" in out, out)
    code, out = rb("verify")
    leg("batch: verify accepts the editor's writeback set only", code == 0 and "writeback set only" in out, out)
    code, out = rb("close")
    leg("batch: close is refused while steps are owed", code == 1, out)

    # interrupted close: drain twice, as a fresh session would
    code, out = rb("drain")
    first_history = read(ctx.history)
    leg("batch: drain moves the two pinned entries and leaves the later one",
        code == 0 and "First thing" not in read(ctx.outbox) and "Later thing" in read(ctx.outbox)
        and first_history.count("### Released in v") == 1 and "#### Second thing" in first_history, out)
    code, out = rb("drain")
    leg("batch: a repeated drain appends nothing and removes nothing more",
        code == 0 and read(ctx.history) == first_history and "Later thing" in read(ctx.outbox), out)
    rb("mark", "writeback", "abc1234")
    rb("mark", "tag", "optin-v1.0.1")
    code, out = rb("close")
    leg("batch: close succeeds once every step is recorded", code == 0, out)
    code, out = rb("status")
    leg("batch: later Pending after a live release is NEW_BATCH, not an unfinished upload",
        "RELEASE STATE: NEW_BATCH" in out and "Later thing" in out and "last closed batch" in out, out)

    # ordinary update: ids already exist at the base commit
    write(os.path.join(repo, "metadata.lua"), META % "\t'pdx_id', 111,\n\t'pdx_version', 1,\n\t'steam_id', \"999\",\n")
    os.remove(os.path.join(repo, "Code", "Opt_Dirty.lua"))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "close first release")
    code, out = rb("begin")
    leg("batch: begin after a live release opens an UPDATE batch", code == 0 and "(update)" in out, out)
    code, out = rb("status")
    leg("batch: existing ids do not count as uploads of the update batch",
        "RELEASE STATE: PREPARED" in out and re.search(r"paradox\s+OWED", out) and re.search(r"steam\s+OWED", out), out)
    leg("batch: the update's launch tree keeps the repo's comments until the editor saves",
        read(launch_meta).startswith("-- a hand comment"))
    code, out = rb("abandon", "fixture ends")
    leg("batch: an untouched batch can be abandoned and Pending survives",
        code == 0 and "Later thing" in read(ctx.outbox), out)


def read(path):
    return io.open(path, encoding="utf-8").read()


def main():
    tmp = tempfile.mkdtemp(prefix="release_selftest_")
    try:
        for name, fn in (("parity", parity_legs), ("package", package_legs), ("batch", batch_legs)):
            sub = os.path.join(tmp, name)
            os.makedirs(sub)
            fn(sub)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = RESULTS.count(False)
    print("\nRELEASE SELFTEST: %d leg(s), %d FAIL" % (len(RESULTS), bad))
    return 1 if bad or not RESULTS else 0


if __name__ == "__main__":
    sys.exit(main())
