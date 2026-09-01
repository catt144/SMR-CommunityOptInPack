# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
# Terminal-audit instrument (2026-08-19): preset-FIELD write census over Code/.
#
# WHY THIS EXISTS: three lenses named preset-field patches as unswept territory
# and none swept it — L1's preset map was read, not extracted; L6's dead-target
# sweep covered globals and class/table members but not preset fields; L8 left
# them unswept for foreign contention. This tool makes the candidate set
# mechanical. Adjudication of each row stays a human read.
#
# WHAT IT DOES
#   1. Derives the preset-container roster from Src itself at runtime
#      (every `GlobalMap = "Name"`), plus the `Presets` tree root — never a
#      hardcoded list that can go stale.
#   2. Scans every Code/*.lua for ASSIGNMENTS whose receiver chain is rooted at
#      a container: direct (`TechDef.x.f = v`), via a one-or-more-level local
#      alias (`local t = TechDef[...] ... t.f = v`), or via a generic-for loop
#      variable over a rooted expression (`for _, p in pairs(TraitPresets) do
#      p.f = v end`). Also table.insert/table.remove with a rooted first arg.
#   3. Emits rows file:line | root | receiver | field | rhs-snippet, then two
#      mechanical crosses: (a) COLLISIONS — the same root+field written by two
#      modules; (b) FOREIGN FIELDS — written field names that never occur in
#      the shipped Src tree (candidate dead targets / mod-invented keys).
#
# DISCLOSED LIMITS (kept, not closed):
#   * comment stripping is line-based and quote-aware only per line — a
#     multi-line string containing `--` could confuse it (none exist in Code/);
#   * a preset reaching a FUNCTION PARAMETER is not tracked (call-site dataflow);
#     rows from wrapped engine functions whose params happen to hold presets do
#     not appear. The census is a LOWER bound on preset writes, same soundness
#     direction as l8_deference_map;
#   * a container passed through a table field (x.cache = TechDef; x.cache.f=v)
#     is not tracked.
#
# CONTROL: --selftest builds a fixture exercising direct write, bracket write,
# one-level alias, two-level alias, loop-var alias, table.insert, a shadowed
# local that must NOT count, and a read that must NOT count. 8/8 expected.

import os, re, sys, io
from collections import defaultdict
import sys

# The Windows console defaults to cp1252 and this tool prints the project's
# non-ASCII vocabulary; without this it dies on its own output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass


SRC_DEFAULT = r"A:\SteamLibrary\steamapps\common\Project Spark\ModTools\Src"
CODE_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Code")

GLOBALMAP_RE = re.compile(r'GlobalMap\s*=\s*"([A-Za-z_][A-Za-z0-9_]*)"')
NAME = r"[A-Za-z_][A-Za-z0-9_]*"

def src_containers(src):
    out = set()
    for dirpath, _dirs, files in os.walk(src):
        for fn in files:
            if not fn.endswith(".lua"):
                continue
            try:
                with io.open(os.path.join(dirpath, fn), "r", encoding="utf-8", errors="replace") as f:
                    for m in GLOBALMAP_RE.finditer(f.read()):
                        out.add(m.group(1))
            except OSError:
                pass
    out.add("Presets")
    return out

def strip_comment(line):
    # quote-aware per line: cut at the first `--` outside quotes
    q = None
    i = 0
    while i < len(line):
        c = line[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == q:
                q = None
        else:
            if c in "'\"":
                q = c
            elif c == "-" and i + 1 < len(line) and line[i + 1] == "-":
                return line[:i]
        i += 1
    return line

def rooted(expr, roots):
    m = re.match(r"\s*(" + NAME + ")", expr)
    return bool(m and m.group(1) in roots)

def scan_file(path, containers):
    rows = []
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except OSError:
        return rows
    roots = set(containers)
    aliases = set()
    lines = raw.splitlines()
    # pass 1: grow the alias set to a fixed point (handles use-before-def order
    # and multi-level aliasing without real scoping — over-approximates, which
    # for a candidate list is the safe direction)
    for _ in range(4):
        grew = False
        for line in lines:
            code = strip_comment(line)
            m = re.search(r"\blocal\s+(" + NAME + r")\s*=\s*(.+)$", code)
            if m:
                rhs = m.group(2)
                names = "|".join(re.escape(r) for r in (roots | aliases))
                hit = re.search(r"\b(" + names + r")\b(?=\s*[.\[(]|\s*$)", rhs)
                # this mod's dominant idiom: local X = rawget(_G, "Container")
                if not hit:
                    hit = re.search(r"rawget\s*\(\s*_G\s*,\s*['\"](" + names + r")['\"]", rhs)
                if hit and m.group(1) not in aliases and m.group(1) not in roots:
                    aliases.add(m.group(1)); grew = True
            m = re.search(r"\bfor\s+" + NAME + r"\s*,\s*(" + NAME + r")\s+in\s+i?pairs\s*\(\s*(" + NAME + r")\b", code)
            if m and m.group(2) in (roots | aliases):
                if m.group(1) not in aliases and m.group(1) not in roots:
                    aliases.add(m.group(1)); grew = True
        if not grew:
            break
    live = roots | aliases
    # pass 2: assignments + inserts whose receiver is rooted
    asg = re.compile(
        r"^\s*((?:" + NAME + r")(?:\s*[.:]\s*" + NAME + r"|\s*\[[^\]]+\])+)\s*=(?!=)")
    ins = re.compile(r"\btable\s*\.\s*(insert|remove)\s*\(\s*((?:" + NAME + r")(?:\s*\.\s*" + NAME + r"|\s*\[[^\]]+\])*)")
    for n, line in enumerate(lines, 1):
        code = strip_comment(line)
        m = asg.match(code)
        if m and rooted(m.group(1), live):
            recv = m.group(1)
            fm = re.search(r"[.:]\s*(" + NAME + r")\s*$|\[\s*['\"](" + NAME + r")['\"]\s*\]\s*$", recv)
            field = (fm.group(1) or fm.group(2)) if fm else "[dynamic]"
            rows.append((n, recv.strip(), field, code.split("=", 1)[1].strip()[:60]))
        m = ins.search(code)
        if m and rooted(m.group(2), live):
            rows.append((n, m.group(2).strip(), "(%s)" % m.group(1), code.strip()[:60]))
    return rows

FIXTURE = """
local direct = 1
TechDef.some_tech.repeatable = false          -- direct write        (row 1)
TraitPresets["Saint"].group = "x"             -- bracket write       (row 2)
local t = TechDef["BreakthroughX"]
t.description = "y"                           -- one-level alias     (row 3)
local u = t
u.icon = "z"                                  -- two-level alias     (row 4)
for _, p in pairs(FactionDefs) do
    p.weight = 5                              -- loop-var alias      (row 5)
end
table.insert(Presets.MapSettings.DustDevils, x) -- rooted insert     (row 6)
local via_rawget = rawget(_G, "TraitPresets")
via_rawget.Saint.rare = true                  -- rawget alias        (row 7)
for _, q in pairs(via_rawget) do
    q.dome_filter = "x"                       -- loop over rawget    (row 8)
end
local shadow = {}
shadow.field = 1                              -- NOT rooted          (no row)
local r = TechDef.some_tech.repeatable        -- read                (no row)
if TechDef.some_tech.cost == 5 then end       -- comparison          (no row)
SMROptInPack.data = 1                           -- NOT a container     (no row)
"""

def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "fixture.lua")
        with io.open(p, "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        rows = scan_file(p, {"TechDef", "TraitPresets", "FactionDefs", "Presets"})
        got = {(r[2]) for r in rows}
        want = {"repeatable", "group", "description", "icon", "weight", "(insert)",
                "rare", "dome_filter"}
        ok = got == want and len(rows) == 8
        print("selftest rows:", sorted(got))
        print("selftest: %s (%d rows, want 8)" % ("PASS" if ok else "FAIL", len(rows)))
        return 0 if ok else 1

def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    src = SRC_DEFAULT
    containers = src_containers(src)
    print("containers from Src: %d (+Presets)" % (len(containers) - 1))
    per_field = defaultdict(set)
    total = 0
    for fn in sorted(os.listdir(CODE_DEFAULT)):
        if not fn.endswith(".lua"):
            continue
        rows = scan_file(os.path.join(CODE_DEFAULT, fn), containers)
        if rows:
            print("\n%s" % fn)
            for n, recv, field, rhs in rows:
                print("  :%d  %s  [field: %s] = %s" % (n, recv, field, rhs))
                per_field[field].add(fn)
                total += 1
    print("\nTOTAL rows: %d" % total)
    coll = {f: ms for f, ms in per_field.items() if len(ms) > 1 and not f.startswith("(")}
    print("\nCOLLISIONS (same field name written by >1 module — adjudicate whether same preset):")
    for f, ms in sorted(coll.items()):
        print("  %s <- %s" % (f, ", ".join(sorted(ms))))
    if not coll:
        print("  none")
    # foreign-field cross: does the field name occur anywhere in Src?
    print("\nFOREIGN-FIELD CROSS (field name absent from the whole Src tree):")
    fields = {f for f in per_field if not f.startswith("(") and f != "[dynamic]"}
    present = set()
    pats = {f: re.compile(r"\b" + re.escape(f) + r"\b") for f in fields}
    for dirpath, _dirs, files in os.walk(src):
        for fn in files:
            if not fn.endswith(".lua"):
                continue
            try:
                with io.open(os.path.join(dirpath, fn), "r", encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            for f in list(fields - present):
                if pats[f].search(text):
                    present.add(f)
        if fields == present:
            break
    absent = fields - present
    for f in sorted(absent):
        print("  ABSENT from Src: %s <- %s" % (f, ", ".join(sorted(per_field[f]))))
    if not absent:
        print("  none — every written field name exists in shipped code")

if __name__ == "__main__":
    main()
