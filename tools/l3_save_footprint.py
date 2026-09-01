#!/usr/bin/env python3
# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
"""L3 — aggregate save-footprint census over the shipped Code/ tree.

Lens L3 (save & exit) instrument. The question this
instrument exists to answer is the AGGREGATE one: not "is this module save-safe"
(every module was verified alone) but "what does the whole pack put into one
savegame, and what happens to all of it at once when this mod is removed".

It emits five censuses, each mechanical and each citing file:line:

  1. WRITE SITES   — every assignment whose target is not a file-local, bucketed
                     by receiver kind through a per-file alias map. The bucket
                     `instance` is the one that can reach a savegame.
  2. THREADS       — every thread constructor, game-time (persisted by default,
                     EF-019) separated from real-time (never persisted).
  3. NAMED STATE   — every `SMRFixPack_*` / `SMROptInPack_*` token: the
                     persisted names (save contract, PROVENANCE §2) and the
                     framework globals (FIX_POLICY §3).
  4. GAMEVARS      — every `GameVar(` declaration (registers in
                     PersistableGlobals, so it self-clears on uninstall).
  5. LOAD ORDER    — every file-scope `OnMsg.<M> =` registration, in metadata.lua
                     `code` order, which IS the order the handlers run in. This
                     is the aggregate view no per-module review can produce.

⛔ Lexical, therefore an over-reporter by design: it cannot see a write behind an
indirection it did not resolve, and it does not know whether a receiver is a live
persisted object. Every row it emits is a candidate to be read, not a verdict.
Same discipline as the L1 collision extractor: resolve the file-local alias
first, then adjudicate at source.

Usage:  python tools/l3_save_footprint.py [--csv <dir>]
"""

import os
import re
import sys
import collections

# The reports are full of non-cp1252 markup (⛔ ⭐ ⚠️ ⇒); a Windows console must
# not die on printing a finding (same guard as doccheck.py / l2_reload_sim.py).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(ROOT, "Code")
METADATA = os.path.join(ROOT, "metadata.lua")

# ---------------------------------------------------------------------------
# receiver taxonomy — which kinds of carrier can reach a savegame
#
# `class`    a class table. Permanents; savegames store a reference, never the
#            table (D13 §2c). A method wrapper lives here.
# `preset`   preset / template data. Rebuilt from shipped data on every load;
#            the ONE exception is a preset SUB-object reachable from a GameVar
#            (D13 row E11), which this script cannot see and the report reads.
# `modtable` our own tables (SMROptInPack.*). Mod env, never persisted.
# `engine`   a vanilla global table that is itself a GameVar or holds one.
# `ui`       an XWindow / dialog. Not persisted.
# `instance` a live game object (or something reached from one). ⭐ THE BUCKET.
# `local`    a file-local. Not a write site at all; excluded.
# ---------------------------------------------------------------------------

CLASS_RECEIVERS = {
    # class tables this mod patches, by the name it writes through (alias map
    # resolves the file-local form first)
    "Building", "Colonist", "Drone", "Workplace", "City", "TrackBase",
    "RCTransport", "TunnelBase", "Shroudable", "LabelContainer",
}

ENGINE_PERSISTED_GLOBALS = {
    # vanilla globals that ARE GameVars or live inside the persisted graph
    "Notifications", "RainsDisasterThreads", "ActiveLaws", "UIColony",
    "MainCity", "Cities", "g_MeteorStorm", "g_RainDisaster",
    "MilestoneCompleted", "MilestoneEnactors", "g_PopupQueue",
    "g_TransportationModeToCommunityCache", "GlobalGameTimeThreadFuncs",
    "PeriodicRepeatInfo",
}

UI_HINTS = ("win", "dlg", "dialog", "panel", "rollover", "ctrl", "wnd")

ALIAS_RAWGET = re.compile(r'^\s*local\s+(\w+)\s*=\s*rawget\s*\(\s*_G\s*,\s*["\'](\w+)["\']\s*\)')
ALIAS_PLAIN = re.compile(r'^\s*local\s+(\w+)\s*=\s*([A-Z]\w*)\s*$')
LOCAL_DECL = re.compile(r'^\s*local\s+(?:function\s+)?([\w, ]+)')

# an assignment to something with a receiver:  a.b = ...   or   a[k] = ...
ASSIGN = re.compile(r'(?<![=~<>])(?<!\.\.)\b(\w+)\s*((?:\.\w+|\[[^\]\[]*\])+)\s*=(?!=)')
FUNC_VALUE = re.compile(r'=\s*function\s*\(')

THREAD_GT = re.compile(r'\b(CreateGameTimeThread|CreateMapGameTimeThread|GlobalGameTimeThread|MapGameTimeRepeat|MakeThreadPersistable)\s*\(')
THREAD_RT = re.compile(r'\b(CreateRealTimeThread|CreateMapRealTimeThread)\s*\(')

NAMED_STATE = re.compile(r'\b(?:SMRFixPack|SMROptInPack)_(\w+)')
GAMEVAR = re.compile(r'^\s*GameVar\s*\(\s*([^,)]+)')
# ⚠️ TWO registration forms, and the first draft of this script saw only one.
# `OnMsg.X = f` and `function OnMsg.X() … end` are the same act; missing the
# second hid two of the fix pack's PostLoadGame passes from the load-order
# census when this tool was first written there. Own-instrument defect,
# found by cross-checking the census against a plain grep — disclosed here
# because a load-order table that silently omits two passes is worse than none.
ONMSG_ANY = re.compile(r'^(\s*)(?:function\s+)?OnMsg\.(\w+)\s*[=(]')
REGISTER = re.compile(r'SMROptInPack\.Register\s*\(\s*(?:["\'](\w+)["\']|(\w+))')

# lines that are pure comment
COMMENT = re.compile(r'^\s*--')


def strip_strings(line):
    """Blank out string literals so their contents cannot produce hits."""
    out = []
    i, n = 0, len(line)
    quote = None
    while i < n:
        c = line[i]
        if quote:
            if c == "\\":
                out.append(" ")
                i += 2
                out.append(" ")
                continue
            if c == quote:
                quote = None
            out.append(" ")
        elif c in "\"'":
            quote = c
            out.append(" ")
        else:
            out.append(c)
        i += 1
    return "".join(out)


def code_lines(path):
    """Yield (lineno, raw, code) skipping comments and long-comment blocks."""
    with open(path, "r", encoding="utf-8") as fh:
        raw_lines = fh.read().split("\n")
    in_block = False
    for n, raw in enumerate(raw_lines, 1):
        if in_block:
            if "]]" in raw:
                in_block = False
            continue
        if re.match(r'^\s*--\[\[', raw):
            if "]]" not in raw:
                in_block = True
            continue
        if COMMENT.match(raw):
            continue
        # trailing comment
        code = raw.split("--", 1)[0] if "--" in strip_strings(raw) else raw
        yield n, raw, code


def build_alias_map(path):
    """file-local name -> the global it aliases (L1's lesson: resolve first)."""
    aliases = {}
    for _, _, code in code_lines(path):
        m = ALIAS_RAWGET.match(code)
        if m:
            aliases[m.group(1)] = m.group(2)
            continue
        m = ALIAS_PLAIN.match(code.rstrip())
        if m:
            aliases[m.group(1)] = m.group(2)
    return aliases


def collect_locals(path):
    names = set()
    for _, _, code in code_lines(path):
        m = LOCAL_DECL.match(code)
        if m:
            for part in m.group(1).split(","):
                part = part.strip()
                if part.isidentifier():
                    names.add(part)
    return names


def classify(receiver, aliases, locals_, path_name):
    resolved = aliases.get(receiver, receiver)
    if resolved in CLASS_RECEIVERS or (resolved[:1].isupper() and resolved.endswith("Base")):
        return "class", resolved
    if resolved in ENGINE_PERSISTED_GLOBALS:
        return "engine", resolved
    if resolved.startswith(("SMROptInPack", "SMRFixPack")):
        return "modtable", resolved
    if resolved in ("OnMsg", "_G"):
        return "engine", resolved
    low = receiver.lower()
    if any(h in low for h in UI_HINTS):
        return "ui", resolved
    if resolved.endswith("Presets") or resolved.endswith("Preset") or resolved in ("TechDef", "PopupNotificationPresets"):
        return "preset", resolved
    if receiver in ("self", "obj", "o", "b", "bld", "unit", "col", "colonist",
                    "drone", "track", "el", "station", "dome", "city", "hub",
                    "rocket", "train", "n", "notification", "entry", "site",
                    "deposit", "req", "transporter", "sphere", "tunnel"):
        return "instance", resolved
    if resolved[:1].isupper():
        # an unresolved capitalised global: could be a class table or a preset
        return "global?", resolved
    if receiver in locals_:
        return "local?", resolved
    return "unknown", resolved


def metadata_order():
    """The `code` list from metadata.lua — the intra-mod load order."""
    with open(METADATA, "r", encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"'code',\s*\{(.*?)\}", text, re.S)
    if not m:
        return []
    return re.findall(r'"([^"]+\.lua)"', m.group(1))


def main():
    # Validate --src BEFORE printing anything: a wrong path must not pass
    # silently — with 0 files scanned every field would read "absent from the
    # whole shipped tree", a false census.
    if "--src" in sys.argv:
        _src = sys.argv[sys.argv.index("--src") + 1]
        if not os.path.isdir(os.path.join(_src, "Lua")):
            sys.exit("l3_save_footprint: --src %r is not a ModTools Src tree "
                     "(no Lua/ under it); the game's is <game>/ModTools/Src "
                     "(WORKFLOW.md 'Layout')" % _src)
    files = metadata_order()
    on_disk = sorted(f for f in os.listdir(CODE) if f.endswith(".lua"))
    listed = [os.path.basename(f) for f in files]
    missing = set(on_disk) - set(listed)
    extra = set(listed) - set(on_disk)

    writes = []
    threads = []
    named = collections.defaultdict(list)
    gamevars = []
    handlers = []
    registrations = {}

    for rel in files:
        name = os.path.basename(rel)
        path = os.path.join(CODE, name)
        if not os.path.exists(path):
            continue
        aliases = build_alias_map(path)
        locals_ = collect_locals(path)
        for n, raw, code in code_lines(path):
            code_s = strip_strings(code)

            m = REGISTER.search(code)
            if m:
                registrations[name] = m.group(1) or m.group(2)

            for m in ASSIGN.finditer(code_s):
                recv, rest = m.group(1), m.group(2)
                if recv in ("local",):
                    continue
                kind, resolved = classify(recv, aliases, locals_, name)
                writes.append({
                    "file": name, "line": n, "receiver": recv,
                    "resolved": resolved, "path": rest.strip(),
                    "kind": kind,
                    "func_value": bool(FUNC_VALUE.search(code[m.end() - 1:])),
                    "text": raw.strip()[:150],
                })

            for m in THREAD_GT.finditer(code_s):
                threads.append({"file": name, "line": n, "kind": "game-time",
                                "call": m.group(1), "text": raw.strip()[:150]})
            for m in THREAD_RT.finditer(code_s):
                threads.append({"file": name, "line": n, "kind": "real-time",
                                "call": m.group(1), "text": raw.strip()[:150]})

            # ⚠️ named state and GameVar names are USUALLY string literals
            # (`local FLAG = "SMRFixPack_..."`), so these two scan the code line
            # BEFORE strings are blanked. The first draft scanned the stripped
            # line and silently lost 4 of the 13 names.
            for m in NAMED_STATE.finditer(code):
                named[m.group(0)].append((name, n))

            m = GAMEVAR.match(code)
            if m:
                gamevars.append({"file": name, "line": n,
                                 "name": m.group(1).strip(), "text": raw.strip()[:150]})

            m = ONMSG_ANY.match(code)
            if m:
                handlers.append({"file": name, "line": n, "msg": m.group(2),
                                 "file_scope": m.group(1) == "",
                                 "text": raw.strip()[:150]})

    # ---------------------------------------------------------------- report
    print("=" * 78)
    print("L3 AGGREGATE SAVE-FOOTPRINT CENSUS")
    print("=" * 78)
    print("files in metadata `code` list : %d" % len(files))
    print("files on disk in Code/        : %d" % len(on_disk))
    print("registered ids seen           : %d" % len(registrations))
    if missing:
        print("⛔ on disk but NOT listed     : %s" % ", ".join(sorted(missing)))
    if extra:
        print("⛔ listed but NOT on disk     : %s" % ", ".join(sorted(extra)))

    print()
    print("--- 1. WRITE SITES by receiver kind " + "-" * 42)
    by_kind = collections.Counter(w["kind"] for w in writes)
    for kind, count in by_kind.most_common():
        fn = sum(1 for w in writes if w["kind"] == kind and w["func_value"])
        print("  %-9s %4d site(s)%s" % (kind, count,
              ("   (%d store a FUNCTION VALUE)" % fn) if fn else ""))
    print("  %-9s %4d" % ("TOTAL", len(writes)))

    print()
    print("  ⭐ receiver kind `instance` — the only bucket that reaches a save:")
    inst = [w for w in writes if w["kind"] == "instance"]
    for w in sorted(inst, key=lambda w: (w["file"], w["line"])):
        print("    %-34s :%-4d %s%s%s" % (w["file"], w["line"], w["receiver"],
              w["path"], "   ⛔FUNCTION VALUE" if w["func_value"] else ""))

    print()
    print("  ⚠️ receiver kind `global?` / `unknown` — MUST be adjudicated by reading:")
    for w in sorted([w for w in writes if w["kind"] in ("global?", "unknown")],
                    key=lambda w: (w["file"], w["line"])):
        print("    %-34s :%-4d %-24s %s%s" % (w["file"], w["line"], w["kind"],
              w["receiver"] + w["path"],
              "   ⛔FUNCTION VALUE" if w["func_value"] else ""))

    print()
    print("--- 2. THREADS " + "-" * 63)
    gt = [t for t in threads if t["kind"] == "game-time"]
    rt = [t for t in threads if t["kind"] == "real-time"]
    print("  game-time (PERSISTED BY DEFAULT, EF-019): %d site(s)" % len(gt))
    for t in gt:
        print("    %-34s :%-4d %s" % (t["file"], t["line"], t["call"]))
    print("  real-time (never persisted):              %d site(s)" % len(rt))
    for t in rt:
        print("    %-34s :%-4d %s" % (t["file"], t["line"], t["call"]))

    print()
    print("--- 3. NAMED STATE (persisted `SMRFixPack_*` + framework `SMROptInPack_*`) " + "-" * 8)
    print("  %d distinct name(s)" % len(named))
    for key in sorted(named):
        sites = named[key]
        files_ = sorted(set(f for f, _ in sites))
        print("    %-38s %2d site(s) in %s" % (key, len(sites), ", ".join(files_)))

    print()
    print("--- 4. GAMEVARS " + "-" * 62)
    print("  %d declaration(s)" % len(gamevars))
    for g in gamevars:
        print("    %-34s :%-4d GameVar(%s)" % (g["file"], g["line"], g["name"]))

    print()
    print("--- 5. LOAD-TIME PASS ORDER (metadata `code` order = run order) " + "-" * 14)
    load_msgs = ("LoadGame", "PostLoadGame", "SaveGameStart", "SaveGameDone",
                 "PersistSave", "PersistLoad", "PersistGatherPermanents")
    seq = 0
    for h in handlers:
        if h["msg"] in load_msgs and h["file_scope"]:
            seq += 1
            print("  %2d. %-14s %-34s :%d" % (seq, h["msg"], h["file"], h["line"]))
    print()
    counts = collections.Counter(h["msg"] for h in handlers if h["file_scope"])
    print("  every file-scope OnMsg registration, by message:")
    for msg, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print("    %-26s %d" % (msg, c))
    nested = [h for h in handlers if not h["file_scope"]]
    if nested:
        print()
        print("  ⚠️ NOT at file scope (registered from inside a function — %d):" % len(nested))
        for h in nested:
            print("    %-34s :%-4d OnMsg.%s" % (h["file"], h["line"], h["msg"]))

    print()
    print("--- 6. SAVE/EXIT HOOK COVERAGE " + "-" * 47)
    for msg in ("SaveGameStart", "SaveGameDone"):
        n = counts.get(msg, 0)
        print("  OnMsg.%-14s %d registration(s)%s" % (
            msg, n, "   ⇒ this mod installs NO layer-1 tear-down" if n == 0 else ""))

    # ------------------------------------------------------------------
    # 7. ⭐ MOD-AUTHORED PERSISTED KEYS — the census the `SMRFixPack_*` token
    #    sweep structurally cannot do.
    #
    # FIX_POLICY §3 says anything we persist carries one of the two prefixes, and the
    # authoritative exposed-set derivation (D13 §1.1) swept route-(c) state with
    # exactly that token as its key. So a site that writes a differently-named
    # key onto a persisted carrier is INVISIBLE to that derivation — the naming
    # rule is not style, it is the grep key.
    #
    # The decisive test does not need the convention: a field name we write onto
    # a game object either exists somewhere in the shipped Lua or it does not.
    # If it does not, the key is ours, whatever it is called.
    # ------------------------------------------------------------------
    if "--src" in sys.argv:
        src = sys.argv[sys.argv.index("--src") + 1]
        print()
        print("--- 7. MOD-AUTHORED PERSISTED KEYS (field names absent from Src) " + "-" * 13)
        tokens = set()
        nfiles = 0
        for dirpath, _, filenames in os.walk(src):
            for fn in filenames:
                if not fn.endswith(".lua"):
                    continue
                nfiles += 1
                try:
                    with open(os.path.join(dirpath, fn), "r", encoding="utf-8",
                              errors="replace") as fh:
                        tokens.update(re.findall(r'\b\w+\b', fh.read()))
                except OSError:
                    pass
        print("  Src scanned: %d .lua file(s), %d distinct token(s)" % (nfiles, len(tokens)))

        candidates = {}
        for w in writes:
            if w["kind"] in ("local?", "modtable", "ui", "class", "preset"):
                continue
            for field in re.findall(r'\.(\w+)', w["path"]):
                candidates.setdefault(field, []).append(w)

        foreign = {f: ws for f, ws in candidates.items() if f not in tokens}
        print("  field names written on non-local carriers : %d" % len(candidates))
        print("  ⛔ ABSENT from the whole shipped tree      : %d" % len(foreign))
        print()
        for field in sorted(foreign):
            conv = ("SMRFixPack_" in field) or ("SMROptInPack_" in field)
            print("    %-34s %s" % (field, "(follows §3 naming)" if conv else "⛔ BREAKS §3 NAMING — invisible to a prefix sweep"))
            for w in sorted(foreign[field], key=lambda w: (w["file"], w["line"])):
                print("        %-34s :%-4d  %s%s   [%s]" % (
                    w["file"], w["line"], w["receiver"], w["path"], w["kind"]))

    if "--csv" in sys.argv:
        out = sys.argv[sys.argv.index("--csv") + 1]
        os.makedirs(out, exist_ok=True)
        import csv
        with open(os.path.join(out, "l3_writes.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(writes[0].keys()))
            w.writeheader()
            w.writerows(writes)
        print("\nwrote %s/l3_writes.csv" % out)


if __name__ == "__main__":
    main()
