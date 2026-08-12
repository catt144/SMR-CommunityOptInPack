# Blocking analysis, v2 -- v1 was useless: bare-name resolution marked half the
# codebase blocking (IsValid, SetText, Random all collided with some unrelated
# blocking method). Two changes:
#
#   1. DIRECT verdict is the trustworthy one: does THIS function's own body
#      contain Sleep / WaitMsg / WaitWakeup / PlayState? No name resolution
#      involved, so no collisions.
#   2. Propagation only through UNAMBIGUOUS callees: a call to name N marks the
#      caller blocking only if EVERY definition of N in the source blocks. Names
#      with a mix of blocking and non-blocking definitions are reported as
#      AMBIGUOUS and read by hand rather than guessed.
import io, os, re, sys, json

SRC = r"A:\SteamLibrary\steamapps\common\Project Spark\ModTools\Src"
PRIM = re.compile(r'\b(Sleep|WaitMsg|WaitWakeup|PlayState)\s*\(')
FUNC = re.compile(r'^function\s+(?:([A-Za-z_][\w]*)\s*[:.])?([A-Za-z_][\w]*)\s*\(', re.M)
CALL = re.compile(r'[:.]([A-Za-z_][\w]*)\s*\(')

defs = {}   # bare name -> list of (class, body)
for root, _d, files in os.walk(SRC):
    for fn in files:
        if not fn.endswith(".lua"):
            continue
        try:
            txt = io.open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        lines = txt.split("\n")
        for m in FUNC.finditer(txt):
            ln = txt.count("\n", 0, m.start())
            j = ln + 1
            while j < len(lines) and lines[j].rstrip() != "end":
                j += 1
            defs.setdefault(m.group(2), []).append((m.group(1), "\n".join(lines[ln:j + 1])))

direct = {n for n, ds in defs.items() if any(PRIM.search(b) for _c, b in ds)}
allblock = {n for n, ds in defs.items() if all(PRIM.search(b) for _c, b in ds)}
for p in ("Sleep", "WaitMsg", "WaitWakeup", "PlayState"):
    allblock.add(p); direct.add(p)

# fixpoint over UNAMBIGUOUS blocking callees only
block = set(allblock)
for _ in range(30):
    grew = False
    for n, ds in defs.items():
        if n in block:
            continue
        if all(set(CALL.findall(b)) & block for _c, b in ds) and ds:
            block.add(n); grew = True
    if not grew:
        break

print("%d names; %d yield directly somewhere; %d block on every definition\n"
      % (len(defs), len(direct), len(block)))
print("%-32s %-34s %-12s %s" % ("module", "target", "verdict", "evidence"))
for label, name in json.load(io.open(sys.argv[1], encoding="utf-8")):
    ds = defs.get(name)
    if not ds:
        print("%-32s %-34s %-12s" % (label, name, "NOT FOUND")); continue
    d = [(c, b) for c, b in ds if PRIM.search(b)]
    if len(d) == len(ds):
        v, e = "BLOCKS", "direct yield in all %d def(s)" % len(ds)
    elif d:
        v, e = "AMBIGUOUS", "%d of %d defs yield directly: %s" % (
            len(d), len(ds), ", ".join(str(c) for c, _b in d[:4]))
    else:
        sus = set()
        for _c, b in ds:
            sus |= set(CALL.findall(b)) & block
        if sus:
            v, e = "BLOCKS", "via unambiguous " + ", ".join(sorted(sus)[:3])
        else:
            amb = set()
            for _c, b in ds:
                amb |= {x for x in CALL.findall(b) if x in direct}
            v = "clear" if not amb else "clear?"
            e = "" if not amb else "check callees: " + ", ".join(sorted(amb)[:5])
    print("%-32s %-34s %-12s %s" % (label, name, v, e))
