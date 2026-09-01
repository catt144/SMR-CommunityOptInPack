#!/usr/bin/env python3
# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
"""Harvest every `{ class = C, method = M }` target this mod declares.

Why this is a tool and not a hand-typed list: the count drifts with every
module edit (24 entries / 17 distinct pairs / 8 classes here at 2026-08-31;
the fix pack, where the tool was born, had estimated "~60" and measured 105). A hand-typed list is a silent under-sweep, and an
under-sweep is the expensive error — a wrap wrongly believed reachable stays
broken forever.

WHAT A TARGET IS, EXACTLY. `SMROptInPack.Require` (Code/00_Core.lua:114-165 here) takes
a spec list; a `{ class, method }` entry is a SHAPE SELF-CHECK ("this function
still exists on this class"). ⚠️ That is NOT the same as "the module wraps it":
some modules require a function they only READ. The sweep in
TestKit/Code/64_Probes_Wave14.lua is deliberately built on the Require targets
anyway, because the runtime test it applies is self-limiting — a target this mod
never wrote to still resolves identically on every descendant, so it reports
clean. Sweeping the superset costs nothing and cannot miss a wrap.

⛔ NOT harvested: `{ global = ... }` (SetGlobal replacements — no class
dispatch involved), `{ class = ... }` with no method (existence checks),
`{ path = ... }`, `{ test = ... }`. `changed_class = ...` is a DataChanged
re-run key, not a target, and the class-name regex excludes it by word boundary.

Usage:
    python tools/harvest_wrap_targets.py            # counts only
    python tools/harvest_wrap_targets.py --list     # module / Class.method
    python tools/harvest_wrap_targets.py --lua      # the Lua table body
"""

import os
import re
import sys

# The reports are full of non-cp1252 markup (⛔ ⭐ ⚠️ ⇒); a Windows console must
# not die on printing a finding (same guard as doccheck.py / l2_reload_sim.py).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(HERE, "Code")


def strip_comments(text):
    """Remove Lua comments without touching string literals.

    Needed because Code/00_Core.lua documents the spec shapes in a comment
    block — `-- { class = "Building", method = "X" }` — and a naive grep
    harvests the documentation as a target.
    """
    out, i, n = [], 0, len(text)
    while i < n:
        if text.startswith("--", i):
            m = re.match(r"--\[(=*)\[", text[i:])
            if m:                                   # long comment
                close = "]" + m.group(1) + "]"
                j = text.find(close, i)
                i = n if j < 0 else j + len(close)
            else:                                   # line comment
                j = text.find("\n", i)
                i = n if j < 0 else j
                out.append("\n")
            continue
        if text[i] == '"':                          # keep string literals whole
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == '"':
                    j += 1
                    break
                j += 1
            out.append(text[i:j])
            i = j
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def require_blocks(src):
    """Yield the argument text of each SMROptInPack.Require( ... ) call."""
    for m in re.finditer(r"SMROptInPack\.Require\s*\(", src):
        i = m.end()
        depth, j = 1, m.end()
        while j < len(src) and depth:
            c = src[j]
            if c in "({[":
                depth += 1
            elif c in ")}]":
                depth -= 1
            j += 1
        yield src[i:j - 1]


def entries(block):
    """Yield each `{ ... }` spec entry inside the block's spec table.

    Depth-aware, so multi-line entries (Opt_NoHomeless declares several) are
    harvested whole rather than truncated at the newline.
    """
    k = block.find("{")
    if k < 0:
        return
    depth, start = 0, None
    for j in range(k, len(block)):
        c = block[j]
        if c == "{":
            depth += 1
            if depth == 2:
                start = j
        elif c == "}":
            if depth == 2 and start is not None:
                yield block[start:j + 1]
                start = None
            depth -= 1


def harvest():
    """-> list of (module, class, method), in file then declaration order."""
    found = []
    for name in sorted(os.listdir(CODE)):
        if not name.endswith(".lua"):
            continue
        with open(os.path.join(CODE, name), encoding="utf-8") as fh:
            src = strip_comments(fh.read())
        for block in require_blocks(src):
            for entry in entries(block):
                # (?<![\w.]) keeps `changed_class` and `object_class` out.
                cm = re.search(r'(?<![\w.])class\s*=\s*"([^"]+)"', entry)
                mm = re.search(r'(?<![\w.])method\s*=\s*"([^"]+)"', entry)
                if cm and mm:
                    row = (name[:-4], cm.group(1), mm.group(1))
                    if row not in found:
                        found.append(row)
    return found


# ---------------------------------------------------------------------------
# --check: the F107 rule (this repo's FIX_POLICY §2; adopted in the fix pack
# 2026-08-24, carried here 2026-08-31).
#
# A module that CAPTURES a method off a class table and INSTALLS a replacement
# under the same name is wrapping that (class, method) pair — and `Require`
# validates only what the author DECLARES, so a pair wrapped but never declared
# bypasses the one check that would have caught a nil `prev` at apply time
# (the fix pack's F107: a module captured a leaf class's method while declaring
# only the base class's, and `prev` was nil on every boot).
#
# The detector is PRECISION-FIRST: it flags only the capture+install shape,
# resolving class aliases of this mod's stylised forms —
#     local A = rawget(_G, "Class")     local A = Class
#     for _, cls in ipairs({ "C1", … }) do local A = rawget(_G, cls)
# — and skips what it cannot resolve. Misses stay misses (the static audit on
# F107 records that limitation); a hit is real. RED means: add the pair to the
# module's Require block, or — with a reason — to the allowlist below.
# ---------------------------------------------------------------------------

# (module, class, method) -> reason. Every entry carries its own justification;
# an entry without a Src citation (or a filed defect id) does not belong here.
CHECK_ALLOWLIST = {
    # Pre-rule wrap sites verified benign at Src 2026-08-31 (each captured class
    # DECLARES the method it wraps, so `prev` is real on every boot). The proper
    # cure — naming the pair in a Require block — is a code edit to a frozen
    # module and sits with the owner (fix-pack checklist, 2026-08-31 items).
    # An entry carrying a defect id is a receipt for an open case, never a waiver.
    ("Opt_DroneOverhaul", "Drone", "CleanUnreachables"):
        "declares it — Drone.lua:879 (readiness pass 2026-08-31); module calls no Require at all, guards inline (Opt_DroneOverhaul.lua:158-172)",
    ("Opt_DroneOverhaul", "TaskRequestHub", "FindTask"):
        "declares it — _TaskRequest.lua:72 (readiness pass 2026-08-31); same inline guard",
    ("Opt_MultipleSuns", "SolarPanelBase", "GameInit"):
        "declares it — SolarPanel.lua:8 (readiness pass 2026-08-31); guarded inline at Opt_MultipleSuns.lua:95/132, not by a Require pair",
}

_NOT_CLASSES = {"SMROptInPack", "SMRFixPack", "SMRTest", "_G"}


def _aliases(src):
    """-> {local name: set of class names it can hold}, per file."""
    out = {}
    for m in re.finditer(r'local\s+(\w+)\s*=\s*rawget\(_G,\s*"(\w+)"\s*\)', src):
        out.setdefault(m.group(1), set()).add(m.group(2))
    for m in re.finditer(r'local\s+(\w+)\s*=\s*([A-Z]\w*)[ \t]*$', src, re.M):
        out.setdefault(m.group(1), set()).add(m.group(2))
    # loop form: for _, cls in ipairs({ "A", "B" }) do local C = rawget(_G, cls)
    lists = {}
    for m in re.finditer(r'for\s+\w+\s*,\s*(\w+)\s+in\s+ipairs\(\s*\{([^}]*)\}', src):
        names = re.findall(r'"(\w+)"', m.group(2))
        if names:
            lists.setdefault(m.group(1), set()).update(names)
    for m in re.finditer(r'local\s+(\w+)\s*=\s*rawget\(_G,\s*(\w+)\s*\)', src):
        if m.group(2) in lists:
            out.setdefault(m.group(1), set()).update(lists[m.group(2)])
    return out


def _resolve(name, aliases):
    """-> the set of class names an identifier can denote, or empty."""
    if name in aliases:
        return aliases[name] - _NOT_CLASSES
    if name in _NOT_CLASSES:
        return set()
    # a bare identifier used directly as a class (Building, Colonist, …):
    # capitalised and long enough not to be an unresolved one-letter alias.
    if re.fullmatch(r"[A-Z]\w{2,}", name):
        return {name}
    return set()


def check():
    """-> (violations, allowlisted) — each a list of (module, class, method, note)."""
    declared = {}
    for mod, c, m in harvest():
        declared.setdefault(mod, set()).add((c, m))

    violations, allowlisted = [], []
    for name in sorted(os.listdir(CODE)):
        if not name.endswith(".lua"):
            continue
        mod = name[:-4]
        with open(os.path.join(CODE, name), encoding="utf-8") as fh:
            src = strip_comments(fh.read())
        aliases = _aliases(src)
        captures = set(re.findall(r'local\s+\w+\s*=\s*(\w+)\.([A-Za-z_]\w*)[ \t]*$',
                                  src, re.M))
        installs = set(re.findall(r'(\w+)\.([A-Za-z_]\w*)\s*=\s*function', src))
        installs |= set(re.findall(r'function\s+(\w+)[:.]([A-Za-z_]\w*)', src))
        for ident, method in sorted(captures & installs):
            for cls in sorted(_resolve(ident, aliases)):
                if (cls, method) in declared.get(mod, set()):
                    continue
                reason = CHECK_ALLOWLIST.get((mod, cls, method))
                if reason is not None:
                    allowlisted.append((mod, cls, method, reason))
                else:
                    violations.append((mod, cls, method,
                                       "wrapped (captured + installed) but not in "
                                       "this module's Require block — FIX_POLICY §2"))
    return violations, allowlisted


def main():
    rows = harvest()
    pairs = sorted(set((c, m) for _, c, m in rows))
    classes = sorted(set(c for c, _ in pairs))
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "--lua":
        for mod, c, m in rows:
            print('\t{ %-32s %-38s %-40s },'
                  % ('"%s",' % mod, '"%s",' % c, '"%s"' % m))
        return
    if mode == "--check":
        violations, allowlisted = check()
        for mod, c, m, reason in allowlisted:
            print("  allowlisted  %-28s %s.%s — %s" % (mod, c, m, reason))
        for mod, c, m, note in violations:
            print("  RED  %-28s %s.%s — %s" % (mod, c, m, note))
        print("WRAP CHECK: %d wrap site(s) outside Require, %d allowlisted"
              % (len(violations), len(allowlisted)))
        sys.exit(1 if violations else 0)
    if mode == "--list":
        for mod, c, m in rows:
            print("  %-34s %s.%s" % (mod, c, m))
    print("TARGETS: %d entries, %d distinct (class, method) pairs, %d classes"
          % (len(rows), len(pairs), len(classes)))


if __name__ == "__main__":
    main()
