#!/usr/bin/env python3
# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
"""L6 — dead-coded targets. Does the shipped game still CALL what we patch?

The L6 lens question: "Dead-coded targets: is F85 the only one? Its
dialog's sole caller sits behind a literal `local cond = false`. Nobody has
swept for a second instance."

This is the sweep. It resolves this mod's patch targets through file-local
aliases (link 1's lesson: `local C = rawget(_G,"Colonist")` then
`function C:Idle` — a plain grep cannot join those across files), then counts
call sites for each target in the whole shipped tree.

⛔ A count is a triage instrument, not a verdict. 0 callers is the F28 shape
and 1-2 callers is where the F85 shape hides; both are printed for reading, and
neither is decided here.

Usage: python tools/l6_reachability.py [--src PATH]
"""
import os
import re
import sys
from collections import defaultdict

# The reports are full of non-cp1252 markup (⛔ ⭐ ⚠️ ⇒); a Windows console must
# not die on printing a finding (same guard as doccheck.py / l2_reload_sim.py).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(ROOT, "Code")
SRC_DEFAULT = r"A:\SteamLibrary\steamapps\common\Project Spark\ModTools\Src"


def read(p):
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def strip_comments(text):
    """Blank out -- line comments so a cited `Foo:Bar` in a header is not a site."""
    out = []
    for line in text.split("\n"):
        i = line.find("--")
        out.append(line if i < 0 else line[:i])
    return "\n".join(out)


# ------------------------------------------------------- target extraction

# link 1's lesson: resolve the file-local alias FIRST
ALIAS_RAWGET = re.compile(r'local\s+([A-Za-z_]\w*)\s*=\s*rawget\(\s*_G\s*,\s*"([^"]+)"\s*\)')
ALIAS_PLAIN = re.compile(r'local\s+([A-Za-z_]\w*)\s*=\s*([A-Z][A-Za-z0-9_]*)\s*$', re.M)

SETGLOBAL = re.compile(r'SMROptInPack\.SetGlobal\(\s*"([^"]+)"')
# `function C:Idle(` / `function C.Idle(`
FUNC_DECL = re.compile(r'^\s*function\s+([A-Za-z_]\w*)\s*[:.]\s*([A-Za-z_]\w*)\s*\(', re.M)
# `C.Idle = function` / `C.Idle = wrapped`
FIELD_ASSIGN = re.compile(r'^\s*([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*=\s*(?!=)', re.M)
# `local orig = C.Idle`
CAPTURE = re.compile(r'local\s+\w+\s*=\s*([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*$', re.M)

OURS = {"SMROptInPack", "SMROptInPack_Disabled", "SMROptInPack_Optional", "ctx",
        "OnMsg", "stats", "opts", "entry", "self", "params", "def"}


def targets_for(path):
    raw = read(path)
    text = strip_comments(raw)
    alias = {}
    for var, real in ALIAS_RAWGET.findall(text):
        alias[var] = real
    for var, real in ALIAS_PLAIN.findall(text):
        alias.setdefault(var, real)

    def resolve(name):
        seen = set()
        while name in alias and name not in seen:
            seen.add(name)
            name = alias[name]
        return name

    found = set()
    for g in SETGLOBAL.findall(text):
        found.add(("global", g))
    for rx, kind in ((FUNC_DECL, "method"), (FIELD_ASSIGN, "method"),
                     (CAPTURE, "capture")):
        for holder, member in rx.findall(text):
            h = resolve(holder)
            if h in OURS or h.startswith("SMROptInPack"):
                continue
            # a lowercase holder that did not resolve to a class is a local table
            if not h[:1].isupper():
                continue
            found.add((kind, h + "." + member))
    return found


# ------------------------------------------------------------ Src scanning

def src_files(src):
    for dirpath, _dirs, files in os.walk(src):
        for f in files:
            if f.endswith(".lua"):
                yield os.path.join(dirpath, f)


def main():
    src = SRC_DEFAULT
    if "--src" in sys.argv:
        src = sys.argv[sys.argv.index("--src") + 1]
    if not os.path.isdir(src):
        print("Src not found at %s — UNMEASURED" % src)
        return 2

    per_module = {}
    for f in sorted(os.listdir(CODE)):
        if f.endswith(".lua") and f != "00_Core.lua":
            per_module[f] = targets_for(os.path.join(CODE, f))

    globals_ = sorted({n for s in per_module.values() for k, n in s if k == "global"})
    methods = sorted({n for s in per_module.values() for k, n in s if k in ("method", "capture")})

    print("targets extracted: %d global replacements · %d class/table members "
          "(alias-resolved, over %d modules)"
          % (len(globals_), len(methods), len(per_module)))

    # one pass over Src, counting every target
    gcount = defaultdict(int)
    mcount = defaultdict(int)
    mstr = defaultdict(int)
    gdecl = defaultdict(int)
    gfiles = defaultdict(set)
    mfiles = defaultdict(set)
    # ⛔ OWN-INSTRUMENT DEFECT, found and fixed 2026-08-19 before any count below
    # was taken: this used to require a call shape, `NAME\s*[({"']`. That misses
    # the reference that matters most to this lens — a function passed as a
    # VALUE. `RainsDisasterActivation` read ZERO uses and is in fact handed to
    # `CreateGameTimeThread(RainsDisasterActivation, settings)`
    # (TerraformingDisasters.lua:313). A dead-code sweep that cannot see a
    # function used as a value is blind to exactly the shape it hunts.
    grx = {g: re.compile(r'\b' + re.escape(g) + r'\b') for g in globals_}
    gdrx = {g: re.compile(r'^\s*function\s+' + re.escape(g) + r'\s*\(', re.M) for g in globals_}
    # ⛔ OWN-INSTRUMENT LIMIT, found and widened 2026-08-19 before any count below
    # was taken. A call-shaped pattern is blind to the two ways this engine
    # reaches a method WITHOUT writing `:Name(`, and both are common in exactly
    # the code this pack patches:
    #   * command methods dispatched by STRING — `Colonist:ExitVehicle` read
    #     ZERO callers and is reached from `colonist:SetCommand("ExitVehicle",
    #     self)` (Train.lua:447), which the module's own header already said;
    #   * a method handed on as a value — `self:PushDestructor(self.OnArrival)`.
    # A dead-code sweep blind to string dispatch would have reported a live
    # command method as unreachable. Count the quoted name too, and keep the
    # two counts apart so a reader can see which kind of evidence a row rests on.
    mrx = {}
    msrx = {}
    for m in methods:
        cls, mem = m.split(".", 1)
        mrx[m] = re.compile(r'[:.]\s*' + re.escape(mem) + r'\s*[({"\']')
        msrx[m] = re.compile(r'["\']' + re.escape(mem) + r'["\']')

    nfiles = 0
    for p in src_files(src):
        t = strip_comments(read(p))
        nfiles += 1
        for g, rx in grx.items():
            n = len(rx.findall(t))
            if n:
                gcount[g] += n
                gfiles[g].add(os.path.relpath(p, src))
            gdecl[g] += len(gdrx[g].findall(t))
        for m, rx in mrx.items():
            n = len(rx.findall(t))
            if n:
                mcount[m] += n
                mfiles[m].add(os.path.relpath(p, src))
            ns = len(msrx[m].findall(t))
            if ns:
                mstr[m] += ns
                mfiles[m].add(os.path.relpath(p, src))

    print("Src scanned: %d .lua files\n" % nfiles)

    print("=" * 78)
    print("GLOBAL REPLACEMENTS — call sites in the shipped tree")
    print("=" * 78)
    print("%-36s %6s %6s %6s" % ("global", "decls", "uses", "files"))
    for g in globals_:
        uses = gcount[g] - gdecl[g]
        flag = "  <- ZERO shipped uses (F28 shape)" if uses <= 0 else (
            "  <- FEW — read every one (F85 shape)" if uses <= 2 else "")
        print("%-36s %6d %6d %6d%s" % (g, gdecl[g], uses, len(gfiles[g]), flag))
        if uses <= 2:
            for f in sorted(gfiles[g]):
                print("        %s" % f)

    print()
    print("=" * 78)
    print("CLASS / TABLE MEMBERS — call sites AND string-dispatch sites")
    print("=" * 78)
    print("%-46s %5s %5s  files" % ("member", "call", "str"))
    thin = [(m, mcount[m], mstr[m], sorted(mfiles[m])) for m in methods
            if mcount[m] + mstr[m] <= 3]
    for m, n, ns, fs in sorted(thin, key=lambda r: r[1] + r[2]):
        print("%-46s %5d %5d  %s"
              % (m, n, ns, fs if (n or ns) else "ZERO of BOTH kinds — read it"))
    print("\n%d of %d members have <= 3 sites of either kind tree-wide"
          % (len(thin), len(methods)))
    print("⛔ TRIAGE ONLY. Member-name granularity over-counts a common name; a "
          "preset/data reference by FIELD is a third route neither column sees; "
          "and a row is decided by READING it, never by its count.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
