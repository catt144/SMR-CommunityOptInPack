#!/usr/bin/env python3
# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
"""L6 — promise vs behaviour. Mechanical censuses over this mod's promise surfaces.

Five surfaces have to agree and have drifted before: the registry this mod
builds at runtime, `metadata.lua`'s `code` list, `items.lua`, the shipped
package, and the player-facing pages. This emits the tables that let a reader
check the agreement instead of being told about it.

Censuses
  1  identity   — Register id per file, resolved through file-local aliases,
                  against the filename the README tells players to derive it from
  2  package    — metadata `code` list vs items.lua vs Code/*.lua on disk, ORDER
                  included (items order is load-bearing, items.lua:19-23)
  3  veto       — every site that runs pack work, tagged with which of the three
                  veto gates in 00_Core covers it (Register / DataPatch / WhenActive)
                  — everything else is a site `SMROptInPack_Disabled` does not stop
  4  entries    — every registered module against its docs/agent/bugs/ entry:
                  status, recorded reachability tier, and whether one exists
  5  fixlist    — the player-facing fix list (site repo) against the module set

Run:  python tools/l6_promise_map.py            (tables to stdout)
      python tools/l6_promise_map.py --json     (machine-readable)
"""
import json
import os
import re
import sys

# The reports are full of non-cp1252 markup (⛔ ⭐ ⚠️ ⇒); a Windows console must
# not die on printing a finding (same guard as doccheck.py / l2_reload_sim.py).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(ROOT, "Code")
BUGS = os.path.join(ROOT, "docs", "agent", "bugs")
SITE = os.path.join(os.path.dirname(ROOT), "SMR-CommunityMods", "content")


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- census 1+3

# `local FIX_ID = "Name"` — the alias half of link 1's lesson, applied to ids
ALIAS = re.compile(r'^\s*local\s+([A-Za-z_][\w]*)\s*=\s*"([^"]+)"', re.M)
REGISTER = re.compile(r'SMROptInPack\.Register\(\s*(?:"([^"]+)"|([A-Za-z_][\w]*))')
TITLE = re.compile(r'^\s*title\s*=\s*"((?:[^"\\]|\\.)*)"', re.M)


def register_id(text):
    """Resolve the Register id through file-local string aliases."""
    m = REGISTER.search(text)
    if not m:
        return None, None
    if m.group(1) is not None:
        return m.group(1), "literal"
    name = m.group(2)
    for var, val in ALIAS.findall(text):
        if var == name:
            return val, "alias:" + name
    return None, "UNRESOLVED:" + name


def register_span(text):
    """(start, end) character offsets of the SMROptInPack.Register(...) call.

    Balanced-paren scan from the call's own '(' — string literals and comments
    are skipped so a ')' inside either cannot close the call early.
    """
    m = REGISTER.search(text)
    if not m:
        return None
    i = text.index("(", m.start())
    depth, j, n = 0, i, len(text)
    while j < n:
        c = text[j]
        if c == "-" and text[j:j + 2] == "--":
            nl = text.find("\n", j)
            j = n if nl < 0 else nl
            continue
        if c == '"' or c == "'":
            q, j = c, j + 1
            while j < n and text[j] != q:
                j += 2 if text[j] == "\\" else 1
            j += 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return (m.start(), j + 1)
        j += 1
    return (m.start(), n)


# Sites that run or install pack work.  Each is tagged with the veto gate that
# covers it; a site with gate "-" is one SMROptInPack_Disabled does not reach.
# ⛔ OWN-INSTRUMENT DEFECT, found and fixed 2026-08-19 before any count below was
# taken. The ungated-OnMsg pattern was a negative lookahead behind `=\s*`, and
# `\s*` backtracks to zero width — so the lookahead was tested at the SPACE
# after `=` and always succeeded. Every `OnMsg.X = SMROptInPack.WhenActive(...)`
# read as UNGATED: 27 sites, where the true ungated set is 7. A lookahead cannot
# be trusted behind a variable-width quantifier; match the whole line and
# classify the right-hand side in code instead. The `^\s*` in the `function`
# forms was a second, cosmetic instance — `\s` eats the preceding newline, which
# is why those rows reported line-1.
ONMSG = re.compile(r'^[ \t]*(?:(function)[ \t]+)?OnMsg\.(\w+)[ \t]*(=?)[ \t]*(.*)$', re.M)

SITE_PATTERNS = [
    ("ondataready", re.compile(r'SMROptInPack\.OnDataReady\s*\(')),
    ("datapatch", re.compile(r'SMROptInPack\.DataPatch\s*\(')),
    ("gamevar", re.compile(r'^[ \t]*GameVar\s*\(', re.M)),
    ("realtime_thread", re.compile(r'CreateRealTimeThread\s*\(')),
    ("gametime_thread", re.compile(r'CreateGameTimeThread\s*\(')),
    ("method_decl", re.compile(r'^[ \t]*function[ \t]+([A-Za-z_][\w]*)[:.]([A-Za-z_][\w]*)[ \t]*\(', re.M)),
]

# a handler body that re-reads the veto itself (FIX_POLICY §2, the A1 lesson)
SELF_VETO = re.compile(r'SMROptInPack_Disabled')
SELF_ACTIVE = re.compile(r'SMROptInPack\.IsActive\s*\(')


def decomment(text):
    """Blank the body of every `--` comment, preserving line and column offsets.

    ⛔ OWN-INSTRUMENT DEFECT, found and fixed 2026-08-19 before any count below
    was taken: the site scan ran over the raw file, so a thread constructor
    QUOTED IN A HEADER counted as a real site — a fix-pack module's header was the
    vanilla defect the module exists to describe, reproduced verbatim in its
    own header comment. This project's headers quote shipped code constantly,
    so a census that cannot tell a quotation from a call over-reports exactly
    where the reading is most careful.
    """
    out = []
    for line in text.split("\n"):
        i = line.find("--")
        out.append(line if i < 0 else line[:i] + " " * (len(line) - i))
    return "\n".join(out)


def scan_module(path):
    text = decomment(read(path))
    fname = os.path.basename(path)
    stem = fname[:-4]
    rid, how = register_id(text)
    tm = TITLE.search(text)
    span = register_span(text)

    def scope(pos):
        return "apply" if span and span[0] <= pos < span[1] else "file"

    sites = []
    for m in ONMSG.finditer(text):
        is_func, msg, eq, rhs = m.groups()
        if is_func:
            kind = "onmsg_bare_func"          # `function OnMsg.X()` — never wrapped
        elif "SMROptInPack.WhenActive" in rhs:
            kind = "onmsg_whenactive"
        elif eq:
            kind = "onmsg_bare_assign"
        else:
            continue                           # a read of OnMsg.X, not a registration
        sites.append({"kind": kind, "name": msg,
                      "line": text.count("\n", 0, m.start()) + 1,
                      "scope": scope(m.start())})
    for kind, rx in SITE_PATTERNS:
        for m in rx.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            name = m.group(1) if m.groups() and m.lastindex else ""
            if kind == "method_decl":
                # only class/table method installs matter; SMROptInPack.* helpers
                # are our own namespace, not a patch on the game
                if m.group(1) == "SMROptInPack":
                    continue
                name = m.group(1) + ":" + m.group(2)
            sites.append({"kind": kind, "name": name, "line": line,
                          "scope": scope(m.start())})
    return {
        "file": fname,
        "stem": stem,
        "id": rid,
        "id_source": how,
        "id_matches_filename": rid is not None and stem in (
            "Fix_" + rid, "Opt_" + rid, rid, "90_" + rid),
        "title": tm.group(1) if tm else None,
        "sites": sites,
        "self_veto": bool(SELF_VETO.search(text)),
        "self_active": bool(SELF_ACTIVE.search(text)),
        "lines": text.count("\n") + 1,
    }


# ------------------------------------------------------------------ census 2

def metadata_code():
    text = read(os.path.join(ROOT, "metadata.lua"))
    block = text[text.index("'code', {"):]
    block = block[:block.index("},")]
    return re.findall(r'"([^"]+)"', block)


def items_entries():
    text = read(os.path.join(ROOT, "items.lua"))
    return re.findall(
        r"'name',\s*\"([^\"]+)\",\s*\n\s*'CodeFileName',\s*\"([^\"]+)\"", text)


# ------------------------------------------------------------------ census 4

FM = re.compile(r"^---\n(.*?)\n---\n", re.S)
TIER = re.compile(r"\b(?:tier|Tier)\s*\**\s*([RU][1-4]?)\b|\*\*(R[1-4]|U)\*\*|\b(R[1-4])\b")


def bug_entries():
    out = {}
    for fn in sorted(os.listdir(BUGS)):
        if not fn.endswith(".md") or fn in ("INDEX.md", "_notes.md"):
            continue
        text = read(os.path.join(BUGS, fn))
        m = FM.search(text)
        if not m:
            continue
        fm = {}
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
        body = text[m.end():]
        # which Code/ modules does this entry name?
        mods = sorted(set(re.findall(r"(?:Code[/\\])?((?:Fix_|Opt_|90_)\w+)", text)))
        tiers = sorted(set(t for grp in TIER.findall(body) for t in grp if t))
        out[fm.get("id", fn[:-3])] = {
            "file": fn, "status": fm.get("status"), "title": fm.get("title", "")[:90],
            "modules": mods, "tiers": tiers,
        }
    return out


# ------------------------------------------------------------------ census 5

def fixlist_entries():
    p = os.path.join(SITE, "fix-list.md")
    if not os.path.exists(p):
        return None
    text = read(p)
    entries = re.findall(r'^\?\?\?\s*\w+\s*"(.+?)"\s*$', text, re.M)
    judgment = len(re.findall(r"judgment call", text, re.I))
    return {"entries": entries, "judgment_mentions": judgment,
            "sections": re.findall(r"^## (.+)$", text, re.M)}


# ---------------------------------------------------------------------- main

def main():
    files = sorted(f for f in os.listdir(CODE) if f.endswith(".lua"))
    mods = [scan_module(os.path.join(CODE, f)) for f in files]
    registered = [m for m in mods if m["id"]]
    meta = metadata_code()
    items = items_entries()
    bugs = bug_entries()
    fl = fixlist_entries()

    data = {"modules": mods, "metadata_code": meta, "items": items,
            "bugs": bugs, "fixlist": fl}
    if "--json" in sys.argv:
        print(json.dumps(data, indent=1))
        return

    print("=" * 78)
    print("CENSUS 1 — identity: Register id vs the filename players derive it from")
    print("=" * 78)
    print(f"{len(files)} Code/*.lua · {len(registered)} register · "
          f"{len(files) - len(registered)} do not")
    bad = [m for m in registered if not m["id_matches_filename"]]
    print(f"id != filename-derived: {len(bad)}")
    for m in bad:
        print(f"  MISMATCH {m['file']}  id={m['id']!r} ({m['id_source']})")
    unres = [m for m in mods if m["id_source"] and str(m["id_source"]).startswith("UNRESOLVED")]
    for m in unres:
        print(f"  UNRESOLVED {m['file']} — {m['id_source']}")
    notitle = [m for m in registered if not m["title"]]
    for m in notitle:
        print(f"  NO TITLE {m['file']}")

    print()
    print("=" * 78)
    print("CENSUS 2 — package: metadata `code` vs items.lua vs disk, order included")
    print("=" * 78)
    disk = set(files)
    metaset = set(os.path.basename(p) for p in meta)
    itemfiles = [os.path.basename(c) for _, c in items]
    print(f"metadata code: {len(meta)} · items: {len(items)} · disk: {len(disk)}")
    print(f"in metadata, not on disk : {sorted(metaset - disk)}")
    print(f"on disk, not in metadata : {sorted(disk - metaset)}")
    print(f"metadata order == items order: "
          f"{[os.path.basename(p) for p in meta] == itemfiles}")
    badname = [(n, c) for n, c in items if n != os.path.basename(c)[:-4]]
    print(f"items `name` != CodeFileName stem: {badname}")

    print()
    print("=" * 78)
    print("CENSUS 3 — the veto route: which sites SMROptInPack_Disabled does NOT stop")
    print("=" * 78)
    kinds = {}
    for m in mods:
        for s in m["sites"]:
            kinds.setdefault((s["kind"], s["scope"]), []).append((m["file"], s))
    for (kind, sc), rows in sorted(kinds.items()):
        print(f"  {kind:20s} scope={sc:5s} {len(rows):4d}")
    print()
    print("  -- sites outside all three gates, by module --")
    UNGATED = {"onmsg_bare_assign", "onmsg_bare_func", "ondataready",
               "method_decl", "gametime_thread", "realtime_thread", "gamevar"}
    total = 0
    for m in mods:
        rows = [s for s in m["sites"]
                if s["kind"] in UNGATED and not (
                    s["kind"] == "method_decl" and s["scope"] == "apply")]
        if not rows:
            continue
        total += len(rows)
        flag = "" if (m["self_veto"] or m["self_active"]) else "  <- no self-check anywhere in file"
        print(f"  {m['file']}{flag}")
        for s in rows:
            print(f"      :{s['line']:<5d} {s['kind']:18s} {s['scope']:5s} {s['name']}")
    print(f"  TOTAL ungated sites: {total}")

    print()
    print("=" * 78)
    print("CENSUS 4 — every registered module against its bugs/ entry")
    print("=" * 78)
    claimed = {}
    for bid, b in bugs.items():
        for mod in b["modules"]:
            claimed.setdefault(mod, []).append((bid, b["status"], tuple(b["tiers"])))
    orphan = [m for m in registered if m["stem"] not in claimed]
    print(f"registered modules with NO bugs entry naming them: {len(orphan)}")
    for m in orphan:
        print(f"  {m['file']}")
    print()
    print("  -- shipped modules whose entry is not a shipping status --")
    SHIPPING = {"fixed", "fixed*", "tested", "tested-attended", "tested-unattended",
                "closed", "folded", "built", "speced"}
    for m in registered:
        rows = claimed.get(m["stem"], [])
        odd = [r for r in rows if r[1] not in SHIPPING]
        if odd:
            print(f"  {m['file']:42s} {odd}")
    print()
    print("  -- recorded reachability tiers on entries naming a SHIPPED module --")
    r4 = []
    for m in registered:
        for bid, st, tiers in claimed.get(m["stem"], []):
            if "R4" in tiers:
                r4.append((m["file"], bid, st, tiers))
    for row in r4:
        print(f"  R4-mentioning: {row}")
    print(f"  ({len(r4)} entries mention R4 while naming a shipped module — "
          f"mention is not a verdict; read each)")

    print()
    print("=" * 78)
    print("CENSUS 5 — the player-facing fix list")
    print("=" * 78)
    if fl is None:
        print("  site repo not present — UNMEASURED")
    else:
        print(f"  entries: {len(fl['entries'])}  sections: {len(fl['sections'])}")
        print(f"  'judgment call' mentions: {fl['judgment_mentions']}")


if __name__ == "__main__":
    main()
