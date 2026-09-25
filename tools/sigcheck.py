#!/usr/bin/env python3
"""Compare every function this pack replaces against the SHIPPED signature.

Ported from SMR-BugFixPack @ eaff679: only the SMROptInPack token differs.

Written 2026-09-08, immediately after F115: `Fix_LandscapeUnitFilter` replaced
`LandscapeForEachUnit(mark, callback, ...)` while game 1.1.0 had changed it to
`LandscapeForEachUnit(map, mark, callback, ...)`. Every argument arrived one
slot late and the module threw on the first landscaping site -- while reporting
`applied`, because its self-check only asked whether the NAME existed.

⛔ THE GAP THIS TOOL EXISTS TO CLOSE. The 1.1.0 sweep behind F113 checked 106
global call-names and 174 method names. Names. A NAME SWEEP CANNOT SEE AN ARITY
CHANGE -- the name is still there, which is exactly why the module applied. This
is the same failure shape EF-078 recorded when path specs were verified by their
last segment's NAME instead of as a path, and that one made the desk audit wrong
by 5. Check the THING, not its label.

    python tools/sigcheck.py                    # compare against the live source
    python tools/sigcheck.py --src <path>       # point at another ModTools/Src
    python tools/sigcheck.py --all              # include matches, not just problems
    python tools/sigcheck.py --coverage         # sites carrying no SRC: pin of their own
    python tools/sigcheck.py --selftest         # the falsifier

WHAT IT REPORTS
  MISMATCH   our parameter list differs from the shipped one -- read every one
  ABSENT     we define a name the shipped tree no longer declares anywhere
  MULTI      several shipped declarations share the name; shown for a human
  UNRESOLVED a `SetGlobal("Name", <expr>)` whose <expr> this tool cannot follow
             to a parameter list. NOT a pass: it is a site with no arity bound
             at all, printed so it cannot hide inside the OK count
  OK         parameter lists agree

TWO KINDS OF SITE ARE READ (2026-09-09, hotfix2 link 05, augment A-4). The
original tool read `function Name(...)` declarations only, so every global the
pack installs through `SMROptInPack.SetGlobal("Name", <expr>)` -- the pack's ONLY
sanctioned route to a global replacement (FIX_POLICY §1.4b) -- was outside it
entirely, along with the anonymous function literals those sites pass. Both
forms are now resolved to a parameter list and checked like any other site:

    SMROptInPack.SetGlobal("WaitBombard", replacement, ...)   -- a named local:
        resolved to the LAST `local replacement = function(...)`,
        `replacement = function(...)` or `local function replacement(...)`
        at or above the SetGlobal line in the same file (the forward-declared
        form `local replacement` / `replacement = function(...)` is the shape
        Fix_BombardmentSpread uses, so it is not optional)
    SMROptInPack.SetGlobal("GetRareTraitChance", function() ... )  -- a literal:
        read straight off the SetGlobal line

Anything else -- a value on a later line, a call, a table index -- is reported
UNRESOLVED rather than skipped. A site this tool cannot follow is a site with
no arity bound, and F115 is what an unbounded site costs.

⚠️ EXTENDING THE SIGHT DOES NOT EXTEND THE VERDICT. This tool is an ARITY bound
and stays one. A `SetGlobal` site that now reads OK has had its parameter list
compared and NOTHING ELSE: the body behind it is exactly as unread as it was
before. F114 shipped because "the instrument was green" was allowed to mean
"the code was checked"; do not let a wider green mean a stronger one.

⚠️ WHAT IT CANNOT DECIDE, AND MUST NOT BE READ AS DECIDING. A matching arity is
NOT proof a replacement is still correct: a same-named, same-arity function
whose BODY changed is invisible here, exactly as it is to the runtime
self-checks. This narrows the search; it does not clear anything. And a
MISMATCH on a wrapper that forwards with `...` may still be harmless -- read
the site.
"""

import argparse
import os
import re
import sys

# The console on this rig is cp1252 and these tools print em-dashes, arrows and
# warning marks. Without this, `--help` alone raises UnicodeEncodeError -- which
# it already did for sigcheck.py, bodycheck.py and upload_preflight.py before
# 2026-09-09. `errors="replace"` so a redirected or piped run still cannot die
# on a character: a census tool that crashes instead of reporting is worse than
# one that prints a question mark.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):        # not a reconfigurable stream
        pass


DEFAULT_SRC = r"A:\SteamLibrary\steamapps\common\Project Spark\ModTools\Src"

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(HERE, "Code")

# `function Class:Method(a, b)` / `function Class.Method(a)` / `function Name(a)`
DEF_METHOD = re.compile(r"^\s*function\s+([A-Za-z_][\w.]*)\s*([:.])\s*([A-Za-z_]\w*)\s*\(([^)]*)\)")
DEF_GLOBAL = re.compile(r"^\s*function\s+([A-Za-z_]\w*)\s*\(([^)]*)\)")
# `local C = Colonist` / `local C = rawget(_G, "Colonist")`
ALIAS = re.compile(r"^\s*local\s+([A-Za-z_]\w*)\s*=\s*(?:rawget\s*\(\s*_G\s*,\s*[\"']([\w]+)[\"']\s*\)|([A-Z][\w]*))\s*$")
# A later `function name(...)` assigns a previously declared local, rather
# than replacing a shipped global (Opt_MultipleSuns.lua uses this shape).
LOCAL_DECL = re.compile(r"^\s*local\s+((?:[A-Za-z_]\w*\s*,\s*)*[A-Za-z_]\w*)\b")

# `SMROptInPack.SetGlobal("Name", <expr>` -- the pack's only sanctioned route to a
# global replacement (FIX_POLICY §1.4b), and invisible to DEF_GLOBAL above.
SETGLOBAL = re.compile(r"""SMROptInPack\.SetGlobal\s*\(\s*["'](?P<name>\w+)["']\s*,\s*(?P<val>.+)$""")
# the value is an anonymous literal, right there on the line
VAL_LITERAL = re.compile(r"^function\s*\(([^)]*)\)")
# ...or an identifier we then have to resolve backwards in the file
VAL_IDENT = re.compile(r"^([A-Za-z_]\w*)\s*(?:,|\)|$)")


def resolve_local_fn(lines, ident, before):
    """Parameter list of `ident` as a function, declared at or above line `before`.

    Three declaration shapes, all present in the pack:
        local ident = function(a, b)
        ident = function(a, b)          -- after a forward `local ident`
        local function ident(a, b)
    The LAST one at or above the use wins, which is Lua's own binding order for
    the straight-line module bodies these sites live in. Returns None when the
    name resolves to nothing this tool can read -- reported UNRESOLVED, never
    silently dropped.
    """
    assign = re.compile(r"^\s*(?:local\s+)?%s\s*=\s*function\s*\(([^)]*)\)" % re.escape(ident))
    declfn = re.compile(r"^\s*local\s+function\s+%s\s*\(([^)]*)\)" % re.escape(ident))
    found = None
    for i, line in enumerate(lines[:before], 1):
        m = assign.match(line) or declfn.match(line)
        if m:
            found = params(m.group(1))
    return found

# names that are ours, not the game's
OURS = ("SMROptInPack", "OnMsg", "SMRTest", "ctx")


def params(s):
    out = [p.strip() for p in s.split(",")]
    return [p for p in out if p]


def scan_source(src):
    """name -> list of (paramlist, file, line). Indexed by bare method/global name."""
    table = {}
    for root, _dirs, files in os.walk(src):
        for fn in files:
            if not fn.endswith(".lua"):
                continue
            path = os.path.join(root, fn)
            try:
                fh = open(path, "r", encoding="utf-8", errors="replace")
            except OSError:
                continue
            with fh:
                for n, line in enumerate(fh, 1):
                    m = DEF_METHOD.match(line)
                    if m:
                        cls, _sep, meth, ps = m.groups()
                        rel = os.path.relpath(path, src)
                        table.setdefault(meth, []).append((cls, params(ps), rel, n))
                        continue
                    m = DEF_GLOBAL.match(line)
                    if m:
                        name, ps = m.groups()
                        rel = os.path.relpath(path, src)
                        table.setdefault(name, []).append((None, params(ps), rel, n))
    return table


def scan_pack(code=None):
    """Our replacement sites: (file, line, cls_or_None, name, params, how).

    `how` records HOW the parameter list was reached -- "declaration" for a
    `function Name(...)` line, "SetGlobal literal" / "SetGlobal local <ident>"
    for the two SetGlobal forms. It is printed, because a reader of an OK row
    is entitled to know which of them the tool actually resolved. `params` is
    None for an UNRESOLVED SetGlobal.
    """
    code = code or CODE
    sites = []
    for fn in sorted(os.listdir(code)):
        if not fn.endswith(".lua"):
            continue
        path = os.path.join(code, fn)
        aliases = {}
        locals_declared = set()
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        for line in lines:
            m = ALIAS.match(line)
            if m:
                aliases[m.group(1)] = m.group(2) or m.group(3)
            m = LOCAL_DECL.match(line)
            if m:
                locals_declared.update(x.strip() for x in m.group(1).split(","))
        for n, line in enumerate(lines, 1):
            m = DEF_METHOD.match(line)
            if m:
                cls, _sep, meth, ps = m.groups()
                if cls.split(".")[0] in OURS:
                    continue
                sites.append((fn, n, aliases.get(cls, cls), meth, params(ps), "declaration"))
                continue
            m = DEF_GLOBAL.match(line)
            if m:
                name, ps = m.groups()
                if name in OURS or name.startswith("OnMsg") or name in locals_declared:
                    continue
                sites.append((fn, n, None, name, params(ps), "declaration"))
                continue
            m = SETGLOBAL.search(line)
            if m:
                name, val = m.group("name"), m.group("val").strip()
                lit = VAL_LITERAL.match(val)
                if lit:
                    sites.append((fn, n, None, name, params(lit.group(1)),
                                  "SetGlobal literal"))
                    continue
                ident = VAL_IDENT.match(val)
                if ident:
                    ps = resolve_local_fn(lines, ident.group(1), n)
                    if ps is not None:
                        sites.append((fn, n, None, name, ps,
                                      "SetGlobal local %s" % ident.group(1)))
                        continue
                # a value on a later line, a call, a table index: NOT a pass.
                sites.append((fn, n, None, name, None,
                              "SetGlobal %s" % val.rstrip(",")[:40]))
    return sites


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--code", default=CODE,
                    help="the pack Code/ to scan (default: this pack)")
    ap.add_argument("--all", action="store_true", help="also print OK rows")
    ap.add_argument("--coverage", action="store_true",
                    help="list replacement sites carrying no SRC: pin of their own function")
    ap.add_argument("--selftest", action="store_true",
                    help="falsify the A-4 SetGlobal resolution, both directions")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if not os.path.isdir(a.src):
        print("source tree not found: %s" % a.src)
        return 2
    if not os.path.isdir(a.code):
        print("pack Code/ not found: %s" % a.code)
        return 2

    shipped = scan_source(a.src)
    sites = scan_pack(a.code)

    counts = {"MISMATCH": 0, "ABSENT": 0, "MULTI": 0, "UNRESOLVED": 0, "OK": 0}
    rows = []
    for fn, ln, cls, name, ours, how in sites:
        if ours is None:
            # a SetGlobal whose value this tool could not follow. It has no
            # arity bound at all -- the one thing it must not do is pass.
            counts["UNRESOLVED"] += 1
            rows.append(("UNRESOLVED", fn, ln, cls, name, [], None, how))
            continue
        cands = shipped.get(name, [])
        if not cands:
            counts["ABSENT"] += 1
            rows.append(("ABSENT", fn, ln, cls, name, ours, None, how))
            continue
        # prefer a declaration on the same class
        same = [c for c in cands if cls and c[0] == cls]
        pool = same or cands
        # A trailing `...` on OUR side is the pack's deliberate forwarding
        # convention (FIX_POLICY wrapping) and is NOT a mismatch. What matters
        # is whether the FIXED leading parameters still line up POSITIONALLY:
        # F115 was `(mark, callback, ...)` against a shipped
        # `(map, mark, callback, ...)` -- same trailing vararg, every argument
        # one slot late. Compare names by position, not lengths.
        def fixed(ps):
            return [p for p in ps if p != "..."]
        ours_f = fixed(ours)
        ok = None
        for c in pool:
            theirs_f = fixed(c[1])
            n = min(len(ours_f), len(theirs_f))
            shifted = any(ours_f[i] != theirs_f[i] for i in range(n))
            # we drop a fixed parameter the game still passes, and we have no
            # vararg to catch it => arguments are silently lost
            short = len(ours_f) < len(theirs_f) and "..." not in ours
            if not shifted and not short:
                ok = c
                break
        if ok:
            counts["OK"] += 1
            if a.all:
                rows.append(("OK", fn, ln, cls, name, ours, ok[1],
                             "%s:%d  via %s" % (ok[2], ok[3], how)))
            continue
        best = pool[0]
        kind = "MISMATCH" if len(pool) == 1 or same else "MULTI"
        counts[kind] += 1
        alts = "; ".join("%s(%s) @%s:%d" % (c[0] or "<global>", ", ".join(c[1]), c[2], c[3])
                         for c in pool[:4])
        rows.append((kind, fn, ln, cls, name, ours, best[1], alts + "  via " + how))

    order = {"MISMATCH": 0, "ABSENT": 1, "UNRESOLVED": 2, "MULTI": 3, "OK": 4}
    rows.sort(key=lambda r: (order[r[0]], r[1], r[2]))

    for kind, fn, ln, cls, name, ours, theirs, note in rows:
        target = ("%s:%s" % (cls, name)) if cls else name
        print("%-10s %s:%d" % (kind, fn, ln))
        if kind == "UNRESOLVED":
            print("            ours    %s(?)  -- value not followable" % target)
        else:
            print("            ours    %s(%s)" % (target, ", ".join(ours)))
        if theirs is not None:
            print("            shipped %s(%s)" % (name, ", ".join(theirs)))
        if note:
            print("            %s" % note)

    gaps = coverage(a.code)
    if a.coverage:
        print("=" * 78)
        print("MANIFEST COVERAGE -- replacement sites with no SRC: pin of their")
        print("own function. NOT a defect list: a site nothing watches.")
        for fn, ln, target, how in gaps:
            print("  %-40s %s:%d  (%s)" % (target, fn, ln, how))

    setglobal = sum(1 for s in sites if s[5].startswith("SetGlobal"))
    print("=" * 78)
    print("%d replacement site(s) (%d of them SetGlobal): "
          "%d MISMATCH, %d ABSENT, %d MULTI, %d UNRESOLVED, %d OK" % (
              len(sites), setglobal, counts["MISMATCH"], counts["ABSENT"],
              counts["MULTI"], counts["UNRESOLVED"], counts["OK"]))
    print("An OK is NOT a clearance: a same-name, same-arity function whose BODY")
    print("changed is invisible here, exactly as it is to the runtime self-checks.")
    print("%d site(s) carry no SRC: pin of their own function%s -- nothing watches"
          % (len(gaps), "" if a.coverage else " (--coverage lists them)"))
    print("those bodies for a change. A count, not a failure (link 01: the FIX and")
    print("REMOVE sets are unstamped until the pack is whole), and a LOWER bound.")
    return 0


# --- manifest coverage: which replacement sites nothing watches ---------------
#
# Filed by the 2026-09-09 cross-branch runs (hotfix2 link 04b) and built here
# because this file already enumerates every replacement site. The gap it names
# is real and was MEASURED: 11 sites carry no `SRC:` pin of THEIR OWN function
# -- the module pins a neighbour instead -- and 8 of those wrapped bodies DID
# change between 1.0.7 and 1.1.0. `bodycheck` cannot see that at all; it checks
# the pins that exist, and a site with no pin is simply not a row.
#
# ⚠️ IT IS A LOWER BOUND, DELIBERATELY. It sees the sites this file sees, which
# is `function X:Y(` declarations plus `SetGlobal("Y", ...)`. A function literal
# handed to something else is invisible to both -- the same blind spot the A-4
# work narrowed rather than closed.
#
# ⚠️ AND AN UNPINNED SITE IS NOT A DEFECT. It is a site whose body nothing is
# watching, which is a thing to decide about, not a thing to fix. The FIX and
# REMOVE sets are deliberately unstamped until the pack is whole (link 01), so
# this count is expected to be non-zero and is reported, never gated.

RE_SRC_SELECTOR = re.compile(r"^\s*--\s*SRC:\s*(?:none\b|(\S+)\s+(\S+))")


def manifest_selectors(path):
    """Every bare name a module's `SRC:` lines pin, from `Class:Method`,
    `Class.Method` or a plain `Name`. A `L<a>-<b>` span pins no name and an
    `SRC: none` pins nothing at all -- both correctly contribute none."""
    names = set()
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = RE_SRC_SELECTOR.match(line)
            if not m or not m.group(2):
                continue
            sel = m.group(2)
            if re.match(r"^L\d+-\d+$", sel):
                continue
            names.add(re.split(r"[:.]", sel)[-1])
    return names


def coverage(code=None):
    """-> [(file, line, target, how)] for every replacement site whose own
    module carries no `SRC:` pin naming that function."""
    code = code or CODE
    cache, gaps = {}, []
    for fn, ln, cls, name, ours, how in scan_pack(code):
        if fn not in cache:
            cache[fn] = manifest_selectors(os.path.join(code, fn))
        if name not in cache[fn]:
            gaps.append((fn, ln, ("%s:%s" % (cls, name)) if cls else name, how))
    return gaps


# --- the falsifier -----------------------------------------------------------
#
# A tool that returns GREEN on everything is indistinguishable from a broken
# one (hotfix2 link 01's rule, and this project has now shipped two checkers
# that silently accused clean files). The A-4 extension adds INFERENCE -- it
# follows an identifier backwards through a file to a parameter list -- so it
# needs legs that pin both directions: the resolution must find the right list,
# and it must FAIL LOUDLY rather than pass when it cannot.

SELFTEST_SHIPPED = '''\
function TriggerCaveIn(map, pos)
end
function WaitBombard(obj, radius, count, delay_min, delay_max)
end
function IsLRTransportAvailable(city)
end
function LandscapeForEachUnit(map, mark, callback)
end
'''

SELFTEST_MODULE = '''\
-- fixture
	local wrapped = function(map, pos, ...)
		return orig(map, pos, ...)
	end
	local err = SMROptInPack.SetGlobal("TriggerCaveIn", wrapped,
		"could not install the TriggerCaveIn wrapper")

	local replacement
	replacement = function(obj, radius, count, delay_min, delay_max)
	end
	return SMROptInPack.SetGlobal("WaitBombard", replacement, "nope")

	return SMROptInPack.SetGlobal("IsLRTransportAvailable", function(city)
	end)

	local shifted = function(mark, callback, ...)
	end
	SMROptInPack.SetGlobal("LandscapeForEachUnit", shifted, "F115's shape")

	SMROptInPack.SetGlobal("GetTable", SomeTable.field, "not a function literal")
'''

SELFTEST_LOCALFN = '''\
local lift_build_limit, restore_build_limit
function lift_build_limit(a, b)
end
function restore_build_limit()
end
function DeliberatelyMissingGlobal(x, y)
end
'''

# coverage fixtures: one site pinned by its own SRC:, three that are not, for
# each of the three ways a manifest can fail to name a function.
SELFTEST_PINNED = '''\
-- SRC: Lua/Fixture.lua Vanilla:Watched sha256=0000000000000000000000000000000000000000000000000000000000000000
-- SRC: none a data patch, pins no name at all
-- SRC: Lua/Fixture.lua L4-25 sha256=0000000000000000000000000000000000000000000000000000000000000000
-- SRC: Lua/Fixture.lua Neighbour:Pinned sha256=0000000000000000000000000000000000000000000000000000000000000000
function Vanilla:Watched(a)
end
function Vanilla:Unwatched(a)
end
function SpanOnly(a)
end
'''


def selftest():
    import tempfile
    fails = []

    def check(label, cond, detail=""):
        print("  %-4s %s%s" % ("ok" if cond else "FAIL", label,
                               ("   " + detail) if detail and not cond else ""))
        if not cond:
            fails.append(label)

    tmp = tempfile.mkdtemp(prefix="sigcheck_selftest_")
    src = os.path.join(tmp, "Src")
    code = os.path.join(tmp, "Code")
    os.makedirs(os.path.join(src, "Lua"))
    os.makedirs(code)
    with open(os.path.join(src, "Lua", "Fixture.lua"), "w", encoding="utf-8") as fh:
        fh.write(SELFTEST_SHIPPED)
    with open(os.path.join(code, "Fix_Selftest.lua"), "w", encoding="utf-8") as fh:
        fh.write(SELFTEST_MODULE)
    with open(os.path.join(code, "Opt_SelftestLocalFn.lua"), "w", encoding="utf-8") as fh:
        fh.write(SELFTEST_LOCALFN)
    with open(os.path.join(code, "Fix_SelftestPinned.lua"), "w", encoding="utf-8") as fh:
        fh.write(SELFTEST_PINNED)

    sites = {s[3]: s for s in scan_pack(code)}

    print("A-4 SetGlobal resolution")
    # 1. the named-local form, declared `local X = function(...)`
    check("local X = function(...) resolves",
          sites.get("TriggerCaveIn", (None,) * 6)[4] == ["map", "pos", "..."],
          repr(sites.get("TriggerCaveIn")))
    # 2. the FORWARD-DECLARED form. Fix_BombardmentSpread uses it, and a
    #    resolver that only knew `local X = function` would silently miss it --
    #    silently, because the site would simply not be reported at all.
    check("forward-declared `local X` / `X = function(...)` resolves",
          sites.get("WaitBombard", (None,) * 6)[4]
          == ["obj", "radius", "count", "delay_min", "delay_max"],
          repr(sites.get("WaitBombard")))
    # 3. the anonymous literal, read off the SetGlobal line
    check("inline `function(...)` literal resolves",
          sites.get("IsLRTransportAvailable", (None,) * 6)[4] == ["city"],
          repr(sites.get("IsLRTransportAvailable")))
    # 4. THE CONVERSE LEG. A value that is not a function this tool can follow
    #    must land as UNRESOLVED, never be dropped and never be counted OK.
    check("unfollowable value is reported, not skipped",
          "GetTable" in sites and sites["GetTable"][4] is None,
          repr(sites.get("GetTable")))

    print("A-4 comparison against a shipped tree")
    shipped = scan_source(src)
    got = {}
    for fn, ln, cls, name, ours, how in scan_pack(code):
        if ours is None:
            got[name] = "UNRESOLVED"
            continue
        cands = shipped.get(name, [])
        if not cands:
            got[name] = "ABSENT"
            continue
        ours_f = [p for p in ours if p != "..."]
        theirs_f = [p for p in cands[0][1] if p != "..."]
        n = min(len(ours_f), len(theirs_f))
        shifted_ = any(ours_f[i] != theirs_f[i] for i in range(n))
        short = len(ours_f) < len(theirs_f) and "..." not in ours
        got[name] = "OK" if not shifted_ and not short else "MISMATCH"
    # 5. THE RED LEG, and it is F115's actual shape: a SetGlobal site whose
    #    parameters are one slot late. Before A-4 this site was invisible; the
    #    point of the extension is that it now goes RED.
    check("F115's shape goes MISMATCH through a SetGlobal site",
          got.get("LandscapeForEachUnit") == "MISMATCH", repr(got))
    # 6. ...and the negative control, so leg 5 cannot pass by being always red.
    check("the three correct SetGlobal sites stay OK",
          [got.get(k) for k in ("TriggerCaveIn", "WaitBombard",
                                "IsLRTransportAvailable")] == ["OK"] * 3,
          repr(got))

    print("manifest coverage (link 04b's filed gap)")
    gaps = {t for _f, _l, t, _h in coverage(code)}
    # 7. a site its own module pins by name is NOT a gap...
    check("a site pinned by its own SRC: selector is not a gap",
          "Vanilla:Watched" not in gaps, repr(sorted(gaps)))
    # 8. ...and the three ways a manifest can fail to name it all ARE. This is
    #    the leg that matters: a module pinning a NEIGHBOUR looks stamped, and
    #    04b measured 8 such bodies that DID change between branches.
    check("unpinned, span-only and SRC-none sites are all gaps",
          {"Vanilla:Unwatched", "SpanOnly"} <= gaps
          and "Neighbour:Pinned" not in gaps, repr(sorted(gaps)))
    # 9. a SetGlobal site is covered by the same check, not exempt from it
    check("SetGlobal sites are covered by the gap check too",
          "TriggerCaveIn" in gaps and "GetTable" in gaps, repr(sorted(gaps)))

    check("forward-declared locals are not global replacement sites",
          not ({"lift_build_limit", "restore_build_limit"} & set(sites)),
          repr(sorted(set(sites) & {"lift_build_limit", "restore_build_limit"})))
    check("an undeclared global still reports ABSENT",
          got.get("DeliberatelyMissingGlobal") == "ABSENT", repr(got))

    print("=" * 78)
    if fails:
        print("SELFTEST FAILED: %s" % ", ".join(fails))
        return 1
    print("selftest: 11 leg(s) pass. This falsifies A-4 resolution and local declaration parsing --")
    print("it says nothing about whether an OK row's BODY is still correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
