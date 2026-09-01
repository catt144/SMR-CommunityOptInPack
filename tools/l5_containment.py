#!/usr/bin/env python3
# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
"""L5 — census of every route by which pack code can THROW, and what catches it.

Lens L5 (failure & containment) instrument. The
question this instrument exists to answer is not "is this module correct" but
**"when something in this pack throws, who catches it, and what does the player
see"** — asked over every Code/*.lua file at once.

⭐ The framing that makes it worth building: this mod's whole fail-safe story is
told about `apply` (`FIX_POLICY` §2 — "apply runs under pcall; an error
deactivates only that fix"). `apply` is ONE of six entry classes. The other five
have never been enumerated, and three of them are not caught by anything the
pack owns.

Four censuses, each mechanical and each citing file:line:

  1. FILESCOPE  — every executable statement at column 0, i.e. OUTSIDE every
                  pcall this mod owns. The only thing catching these is the
                  engine's own `pdofile` (`lib.lua:242-251`) inside
                  `ModDef:LoadCode` (`Mod.lua:490-520`), whose collected errors
                  become a PLAYER-FACING message box (`Mod.lua:2254-2275`).
                  Classified by whether the statement can throw at all.
  2. ENTRY      — every callable this mod hands to the engine, tagged with the
                  catcher that stands between a throw in it and the player.
  3. DEFERRED   — the F87 shape: modules whose actual repair work happens AFTER
                  apply returns (message handler, thread, wrapper), crossed with
                  whether that later path can report its own failure into the
                  registry. A module in this set can log `applied` and be doing
                  nothing.
  4. GUARD      — every `pcall` this mod owns, so census 3's "reports failure"
                  column is derived from sites, not from belief.

⛔ Lexical, therefore an over-reporter by design, exactly like the L1/L3/L4
extractors: column 0 means file scope because every function body in this tree
is indented with tabs, and a statement flagged `may-throw` is a candidate to be
READ AT SOURCE, not a verdict. Every number below is an enumeration; every
adjudication belongs in a lens report made by reading the line (the fix pack's
`reports/L5_CONTAINMENT_MAP.md` is the model; this mod has none yet).

Usage:  python tools/l5_containment.py [--csv <dir>]
"""

import os
import re
import sys
import csv
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
# The catchers, re-derived at Src this session (1.0.7.396349), by symbol.
# ---------------------------------------------------------------------------
#
#   pdofile      lib.lua:242-251     pcall around a whole mod code FILE
#   ModDef:LoadCode  Mod.lua:490-520 collects each file's error into `errs`
#   ModsLoadCode Mod.lua:2254-2275   ModLog + ModsLoadCodeErrorsMessage -> BOX
#   run_apply    00_Core.lua:388     pcall(def.apply)  -> status "error" + log
#   DataPatch    00_Core.lua:309     pcall(opts.pass)  -> status "error" + log
#   OnDataReady  00_Core.lua:372     *** no pcall ***
#   Msg          cthreads.lua:15-21  procall per handler — swallowed, no report
#   ReportModLuaError Mod.lua:2958-2993  engine-owned player message box
#
CATCHERS = {
    "filescope": "pdofile pcall -> ModsLoadCode message box (Mod.lua:2254-2275)",
    "apply": "run_apply pcall -> status=error + log (00_Core.lua:388-393)",
    "datapatch": "DataPatch pcall -> status=error + log (00_Core.lua:309-318)",
    "ondataready": "NONE -- Msg procall swallows it (00_Core.lua:372)",
    "onmsg": "Msg procall -- swallowed, no report (cthreads.lua:20)",
    "wrapper": "the engine caller's context — unknown per call site",
    "thread": "the thread dies; ThreadErrorHandler (cthreads.lua:137-141)",
}

# ---------------------------------------------------------------------------
# lexical shapes
# ---------------------------------------------------------------------------

RE_COMMENT = re.compile(r"^\s*--")
RE_TERMINATOR = re.compile(r"^(end\b.*|\}\)?,?|\)\s*,?|\}\s*,?)$")

# file-scope statement kinds, in match order
FILESCOPE_KINDS = [
    ("decl-local-fn", re.compile(r"^local\s+function\s+")),
    ("decl-fn", re.compile(r"^function\s+")),
    ("register", re.compile(r"^SMROptInPack\.Register\s*\(")),
    ("onmsg", re.compile(r"^OnMsg\.\w+\s*=")),
    ("local", re.compile(r"^local\s+")),
    ("global-assign", re.compile(r"^[A-Za-z_][\w]*\s*=")),
    ("field-assign", re.compile(r"^[A-Za-z_][\w]*[.\[][^=]*=")),
    ("call", re.compile(r"^[A-Za-z_][\w.:]*\s*\(")),
]

# an RHS this mod itself guarantees cannot be nil at this point:
#   * a literal / table constructor
#   * rawget(_G, "...") — returns nil rather than throwing
#   * SMROptInPack.* — 00_Core.lua is first in metadata `code`, so it is loaded
#     before every other file; a throw there is its own row
SAFE_RHS = re.compile(
    r"=\s*(\{|\"|'|\d|true|false|nil|rawget\s*\(|SMRFixPack[.\[]|function\b)"
)

RE_ENTRY = {
    "register": re.compile(r"SMROptInPack\.Register\s*\(\s*([A-Za-z_\"][\w\"]*)"),
    "datapatch": re.compile(r"SMROptInPack\.DataPatch\s*\("),
    "ondataready": re.compile(r"SMROptInPack\.OnDataReady\s*\("),
    "whenactive": re.compile(r"SMROptInPack\.WhenActive\s*\("),
    "onmsg-raw": re.compile(r"^\s*(?:function\s+)?OnMsg\.(\w+)"),
    "setglobal": re.compile(r"SMROptInPack\.SetGlobal\s*\("),
    "gt-thread": re.compile(r"CreateGameTimeThread\s*\("),
    "rt-thread": re.compile(r"CreateRealTimeThread\s*\("),
    "periodic": re.compile(r"PeriodicRepeatInfo\s*\["),
    "pcall": re.compile(r"\bpcall\s*\("),
    # a method wrapper installed inside apply(): indented `function <X>:<Y>`
    "method-wrap": re.compile(r"^\s+function\s+([A-Za-z_]\w*)[:.](\w+)\s*\("),
}


def code_files():
    """Code/*.lua in metadata.lua `code` order — load order is failure order."""
    order, seen = [], set()
    with open(METADATA, encoding="utf-8") as fh:
        for m in re.finditer(r'"(Code/[^"]+\.lua)"', fh.read()):
            name = os.path.basename(m.group(1))
            if name not in seen:
                seen.add(name)
                order.append(name)
    on_disk = sorted(f for f in os.listdir(CODE) if f.endswith(".lua"))
    order += [f for f in on_disk if f not in seen]
    return [f for f in order if os.path.exists(os.path.join(CODE, f))]


def scan():
    filescope, entries, guards, sweeps = [], [], [], []
    for name in code_files():
        path = os.path.join(CODE, name)
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        # function bodies defined in this file, by bare name — census 5 follows
        # one level of delegation through this map
        defs = {}
        for i, raw in enumerate(lines, 1):
            dm = re.match(r"^\s*(?:local\s+)?function\s+([A-Za-z_][\w.:]*)\s*\(", raw)
            if dm:
                defs[dm.group(1).replace(":", ".").split(".")[-1]] = _block(lines, i)
        for n, raw in enumerate(lines, 1):
            line = raw.rstrip()
            if not line.strip() or RE_COMMENT.match(line):
                continue
            body = line.strip()

            # --- census 1: column-0 statements -----------------------------
            if line[0] not in " \t" and not RE_TERMINATOR.match(body):
                kind = "other"
                for label, rx in FILESCOPE_KINDS:
                    if rx.match(body):
                        kind = label
                        break
                # can this statement throw when executed?
                if kind in ("decl-local-fn",):
                    risk = "no"
                elif kind == "decl-fn":
                    # `function A.B()` indexes A at definition time
                    risk = "no" if re.match(
                        r"^function\s+(OnMsg|SMRFixPack)\.", body) else "check"
                elif kind in ("register", "call"):
                    risk = "call"
                elif kind in ("onmsg",):
                    risk = "no" if SAFE_RHS.search(body) else "check"
                elif kind in ("local", "global-assign", "field-assign"):
                    risk = "no" if SAFE_RHS.search(body) else "check"
                else:
                    risk = "check"
                filescope.append((name, n, kind, risk, body))

            # --- census 2 + 4: entry points and guards ---------------------
            for label, rx in RE_ENTRY.items():
                m = rx.search(line)
                if not m:
                    continue
                if label == "pcall":
                    guards.append((name, n, body))
                else:
                    entries.append((name, n, label,
                                    "file" if line[0] not in " \t" else "nested",
                                    body))

            # --- census 5: message-handler sweeps and their per-item guard --
            m = RE_ENTRY["onmsg-raw"].match(line)
            if m and name != "00_Core.lua":
                text = _block(lines, n)
                # ⚠️ follow ONE level of delegation: most load-time passes are a
                # two-line handler calling a named body in the same file, and a
                # census that only reads the handler literal sees 2 of 6 sweeps
                # instead of all of them. (Own-instrument defect, caught by
                # eyeballing 90_SaveSanitizer against the first output.)
                # bare identifiers, not just call-shaped ones: the most common
                # delegation in this tree is `pcall(SMROptInPack.MigrateRainsState)`,
                # where the body's name is never followed by "(".
                named = set(re.findall(r"[A-Za-z_][\w]*", text))
                for short in named:
                    if short in defs:
                        text += "\n" + defs[short]
                loops = len(re.findall(r"\bfor\s+[\w,\s]+\bin\s+\w*pairs\s*\(", text))
                if loops:
                    sweeps.append((name, n, m.group(1), loops,
                                   len(re.findall(r"\bpcall\s*\(", text)),
                                   len(text.splitlines())))
    return filescope, entries, guards, sweeps


def _block(lines, start_line):
    """Text of the statement beginning at 1-indexed start_line, to its `end`."""
    line = lines[start_line - 1]
    indent = len(line) - len(line.lstrip())
    out = []
    for k in range(start_line - 1, len(lines)):
        b = lines[k]
        out.append(b)
        if k > start_line - 1 and b.strip() in ("end", "end)", "end),") and \
                (len(b) - len(b.lstrip())) == indent:
            break
    return "\n".join(out)


def main():
    filescope, entries, guards, sweeps = scan()
    files = code_files()

    print("L5 CONTAINMENT CENSUS -- %d Code/*.lua in metadata load order" % len(files))
    print()

    print("=== 1 . FILE-SCOPE STATEMENTS (outside every pcall this mod owns) ===")
    by_kind = collections.Counter(k for _, _, k, _, _ in filescope)
    by_risk = collections.Counter(r for _, _, _, r, _ in filescope)
    print("  %d statements at column 0" % len(filescope))
    for k, c in sorted(by_kind.items(), key=lambda kv: -kv[1]):
        print("    %-14s %4d" % (k, c))
    print("  throw risk: " + ", ".join("%s=%d" % (r, c) for r, c in sorted(by_risk.items())))
    print()
    print("  --- rows needing a source read (risk 'check' or 'call') ---")
    for name, n, kind, risk, body in filescope:
        if risk in ("check", "call"):
            print("    %-34s :%-4d %-13s %s" % (name, n, kind, body[:88]))
    print()

    print("=== 2 . ENTRY POINTS the engine can call into ===")
    by_label = collections.Counter(l for _, _, l, _, _ in entries)
    for label in sorted(by_label):
        catcher = CATCHERS.get(
            {"onmsg-raw": "onmsg", "gt-thread": "thread", "rt-thread": "thread",
             "method-wrap": "wrapper", "setglobal": "wrapper",
             "periodic": "thread", "whenactive": "onmsg"}.get(label, label), "-")
        print("  %-12s %4d   catcher: %s" % (label, by_label[label], catcher))
    print()

    print("  --- OnMsg registrations, by whether WhenActive gates them ---")
    for name, n, label, scope, body in entries:
        if label != "onmsg-raw":
            continue
        gated = "WhenActive" if "WhenActive" in body else "BARE(!)"
        print("    %-34s :%-4d %-9s %-10s %s" % (name, n, scope, gated, body[:70]))
    print()

    print("=== 3 . DEFERRED-WORK (F87) SET — work that happens after apply returns ===")
    per_file = collections.defaultdict(set)
    for name, n, label, scope, body in entries:
        per_file[name].add(label)
    print("  %-34s %-9s %-10s %-11s %s"
          % ("file", "datapatch", "ondataready", "onmsg", "own pcall"))
    guarded = collections.Counter(g[0] for g in guards)
    deferred = 0
    for name in files:
        labels = per_file.get(name, set())
        has_def = labels & {"datapatch", "ondataready", "onmsg-raw",
                            "gt-thread", "rt-thread"}
        if not has_def:
            continue
        deferred += 1
        print("  %-34s %-9s %-10s %-11s %d"
              % (name,
                 "yes" if "datapatch" in labels else "-",
                 "yes" if "ondataready" in labels else "-",
                 "yes" if "onmsg-raw" in labels else "-",
                 guarded.get(name, 0)))
    print("  %d of %d files defer work past apply()" % (deferred, len(files)))
    print()

    print("=== 5 . MESSAGE-HANDLER SWEEPS -- one bad object vs the whole repair ===")
    print("  A handler that iterates a collection is entered through Msg's procall")
    print("  (cthreads.lua:20). A throw on item 3 of 400 aborts items 4..400 AND is")
    print("  swallowed: no log line, no status change, entry still reads 'active'.")
    print("  A per-item pcall costs one object instead of the whole sweep.")
    print()
    print("  %-34s %-6s %-18s %-6s %-7s %s"
          % ("file", "line", "message", "loops", "pcalls", "verdict"))
    unguarded = 0
    for name, n, msg, loops, pcalls, span in sorted(sweeps):
        verdict = "per-item guard" if pcalls else "NO GUARD"
        if not pcalls:
            unguarded += 1
        print("  %-34s :%-5d %-18s %-6d %-7d %s"
              % (name, n, msg, loops, pcalls, verdict))
    print("  %d iterating handlers; %d carry no pcall anywhere in the handler"
          % (len(sweeps), unguarded))
    print()

    print("=== 4 . GUARDS this mod owns (pcall sites) ===")
    print("  %d pcall sites in %d files" % (len(guards), len(set(g[0] for g in guards))))
    for name, n, body in guards:
        print("    %-34s :%-4d %s" % (name, n, body[:88]))

    if "--csv" in sys.argv:
        out = sys.argv[sys.argv.index("--csv") + 1]
        os.makedirs(out, exist_ok=True)
        for fname, rows, header in (
            ("l5_filescope.csv", filescope,
             ["file", "line", "kind", "risk", "statement"]),
            ("l5_entries.csv", entries, ["file", "line", "kind", "scope", "statement"]),
            ("l5_guards.csv", guards, ["file", "line", "statement"]),
        ):
            with open(os.path.join(out, fname), "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(header)
                w.writerows(rows)
        print("\nCSV written to %s" % out)


if __name__ == "__main__":
    main()
