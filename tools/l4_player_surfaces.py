#!/usr/bin/env python3
# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
"""L4 — census of every surface a PLAYER can see or read, over the shipped tree.

Lens L4 (player experience) instrument. The question
this instrument exists to answer is not "is this module correct" but "what does
a player actually SEE and READ, across every Code/*.lua file at once, and is any of it
alarming, false, or untranslated".

It emits five censuses, each mechanical and each citing file:line:

  1. SCREEN      — every call to an engine function that draws pixels or speaks.
                   The API set is re-derived from Src (see SCREEN_API below), not
                   assumed: each name was confirmed to be a global `function` in
                   the shipped tree.
  2. TEXT        — every `T{...}` / `T(...)` / `Untranslated(...)` site. A `T` id
                   resolves in the player's own language pack (EF-063); an
                   `Untranslated` literal reaches EVERY language as English.
  3. LOG         — every `log(` / `ModLog(` / `print(` site with its format
                   string. This is what a player sees if they open the log,
                   which the public pages ask them to do for a bug report.
  4. VERDICT     — every string that can become a registry entry's `detail`:
                   a `Require` reason, a `latch(...)` detail, or a bare
                   `return "..."` out of an apply. These are read by ListFixes
                   AND classified by UpdateSuspects.
  5. SUSPECT     — census 4 crossed with `UpdateSuspects`' four substring tests
                   (00_Core.lua:532-535). ⭐ THE ONE NO PER-MODULE REVIEW CAN DO:
                   a benign verdict string that happens to contain one of those
                   substrings fires the player-facing "the game code changed"
                   dialog on a working pack; a genuine patch-rot string that
                   matches none of them, and whose site sets no update_suspect
                   mark, is invisible to that dialog.

⛔ Lexical, therefore an over-reporter by design: a string built by
concatenation or returned through a local is a candidate to be read at source,
not a verdict. Same discipline as the L1 and L3 extractors.

Usage:  python tools/l4_player_surfaces.py [--csv <dir>]
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
# 1 · the screen-producing API set
#
# Re-derived 2026-08-18 by enumerating `^function <name>` over the whole shipped
# Src tree; every name below was confirmed to exist there as a global function.
# Grouped by what the player experiences, because that is the L4 question.
# ---------------------------------------------------------------------------

SCREEN_API = {
    # a modal box that stops the game and demands a click — the loudest surface
    "WaitMessage": "modal",
    "CreateMessageBox": "modal",
    "WaitQuestion": "modal",
    "CreateQuestionBox": "modal",
    "OpenDialog": "modal",
    # the corner popup card with a portrait
    "ShowPopupNotification": "popup",
    "WaitPopupNotification": "popup",
    # the right-hand notification stack
    "AddNotification": "notification",
    "AddOnScreenNotification": "notification",
    "AddCustomOnScreenNotification": "notification",
    "AddObjectToNotification": "notification",
    "RemoveNotification": "notification-",
    "RemoveObjectFromNotification": "notification-",
    "RemoveDisasterNotifications": "notification-",
    "AddDisasterNotification": "notification",
    "CreateStopAutomodeNotification": "notification",
    # voice lines
    "QueueVoice": "voice",
    "PlayVoiceResponse": "voice",
}

TEXT_API = ("T", "Untranslated")

# UpdateSuspects' four substring tests, 00_Core.lua:532-535. Kept as literals so
# a drift between this census and the runtime classifier shows up as a diff.
SUSPECT_SUBSTRINGS = (
    "game update changed",
    "could not install",
    "could not replace",
    "did not land",
)

COMMENT = re.compile(r"^\s*--")


def code_files():
    """Every Code/*.lua in metadata.lua `code` order — the order they load in."""
    with open(METADATA, encoding="utf-8") as fh:
        meta = fh.read()
    names = re.findall(r'"(Code/[^"]+\.lua)"', meta)
    out = []
    for n in names:
        p = os.path.join(ROOT, n.replace("/", os.sep))
        if os.path.isfile(p):
            out.append((n, p))
    return out


def lines_of(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read().split("\n")


def is_comment(line):
    return bool(COMMENT.match(line))


# ---------------------------------------------------------------------------
# censuses
# ---------------------------------------------------------------------------

def census_screen(files):
    rows = []
    pat = re.compile(r"\b(" + "|".join(map(re.escape, SCREEN_API)) + r")\s*\(")
    for name, path in files:
        for i, line in enumerate(lines_of(path), 1):
            if is_comment(line):
                continue
            for m in pat.finditer(line):
                api = m.group(1)
                # a Require spec cites the global by NAME as a precondition; it
                # is not a call site. `{ global = "AddNotification" }`
                if re.search(r'(global|class)\s*=\s*"' + api, line):
                    continue
                rows.append((name, i, api, SCREEN_API[api], line.strip()))
    return rows


def census_text(files):
    rows = []
    for name, path in files:
        for i, line in enumerate(lines_of(path), 1):
            if is_comment(line):
                continue
            for m in re.finditer(r"(?<![A-Za-z0-9_])(T|Untranslated)\s*[\({]", line):
                api = m.group(1)
                if re.search(r'global\s*=\s*"' + api + r'"', line):
                    continue
                tid = None
                mm = re.match(r"T\s*[\({]\s*(\d+)", line[m.start():])
                if mm:
                    tid = mm.group(1)
                rows.append((name, i, api, tid or "", line.strip()))
    return rows


def census_log(files):
    rows = []
    for name, path in files:
        for i, line in enumerate(lines_of(path), 1):
            if is_comment(line):
                continue
            if not re.search(r"(?<![A-Za-z0-9_.])(log|ModLog|print)\s*\(", line):
                continue
            if re.search(r"function\s+SMROptInPack\.Log|local\s+log\s*=", line):
                continue
            fmt = re.search(r'"((?:[^"\\]|\\.)*)"', line)
            rows.append((name, i, fmt.group(1) if fmt else "(non-literal)", line.strip()))
    return rows


def census_verdict(files):
    """Strings that can become an entry's `detail`, i.e. what ListFixes prints
    and what UpdateSuspects classifies."""
    rows = []
    for name, path in files:
        src = lines_of(path)
        for i, line in enumerate(src, 1):
            if is_comment(line):
                continue
            kind = None
            if re.search(r"\breason\s*=", line):
                kind = "Require reason"
            elif re.search(r"\bctx\.latch\s*\(", line):
                kind = "latch detail"
            elif re.search(r"^\s*return\s+\"", line):
                kind = "apply return"
            elif re.search(r"^\s*local\s+[A-Z_]+\s*=\s*\"", line):
                kind = "reason const"
            if not kind:
                continue
            for s in re.findall(r'"((?:[^"\\]|\\.)*)"', line):
                if not s:
                    continue
                benign = bool(re.search(r'"\s*,\s*true\s*\)|,\s*true\s*\)\s*$', line)) \
                    if kind == "latch detail" else None
                rows.append((name, i, kind, s, benign))
    return rows


def census_suspect(verdicts):
    rows = []
    for name, i, kind, s, benign in verdicts:
        hits = [t for t in SUSPECT_SUBSTRINGS if t in s]
        if hits:
            rows.append((name, i, kind, s, ",".join(hits), benign))
    return rows


def main():
    files = code_files()
    outdir = None
    if "--csv" in sys.argv:
        outdir = sys.argv[sys.argv.index("--csv") + 1]
        os.makedirs(outdir, exist_ok=True)

    print("L4 PLAYER-SURFACE CENSUS — %d Code/*.lua in metadata.lua order" % len(files))
    print("=" * 78)

    screen = census_screen(files)
    print("\n1 · SCREEN — calls that draw pixels or speak (%d sites)" % len(screen))
    by_kind = collections.Counter(r[3] for r in screen)
    for k, n in sorted(by_kind.items()):
        print("    %-14s %d" % (k, n))
    for r in screen:
        print("    %-34s :%-4d %-32s [%s]" % (r[0].replace("Code/", ""), r[1], r[2], r[3]))

    text = census_text(files)
    print("\n2 · TEXT — translated and untranslated strings (%d sites)" % len(text))
    for r in text:
        tag = ("T id " + r[3]) if r[3] else r[2]
        print("    %-34s :%-4d %s" % (r[0].replace("Code/", ""), r[1], tag))

    logs = census_log(files)
    print("\n3 · LOG — lines a player can read in the log (%d sites)" % len(logs))
    per_file = collections.Counter(r[0] for r in logs)
    for f, n in per_file.most_common():
        print("    %-40s %d" % (f.replace("Code/", ""), n))

    verdicts = census_verdict(files)
    print("\n4 · VERDICT — strings that can become an entry `detail` (%d)" % len(verdicts))
    by_kind = collections.Counter(r[2] for r in verdicts)
    for k, n in sorted(by_kind.items()):
        print("    %-18s %d" % (k, n))

    suspects = census_suspect(verdicts)
    print("\n5 · SUSPECT — verdict strings matching UpdateSuspects' substrings (%d)"
          % len(suspects))
    print("    (00_Core.lua:532-535 — any match fires the player-facing dialog)")
    for r in suspects:
        print("    %-34s :%-4d [%s] %s" % (r[0].replace("Code/", ""), r[1], r[4], r[3][:78]))

    unmatched = [v for v in verdicts if v not in
                 [(s[0], s[1], s[2], s[3], s[5]) for s in suspects]]
    print("\n    verdict strings matching NO substring: %d — these reach the dialog"
          % len(unmatched))
    print("    only via the `update_suspect` mark Require/latch sets.")

    if outdir:
        for fname, rows, hdr in (
            ("l4_screen.csv", screen, ("file", "line", "api", "kind", "source")),
            ("l4_text.csv", text, ("file", "line", "api", "t_id", "source")),
            ("l4_log.csv", logs, ("file", "line", "format", "source")),
            ("l4_verdict.csv", verdicts, ("file", "line", "kind", "string", "benign")),
            ("l4_suspect.csv", suspects,
             ("file", "line", "kind", "string", "matched", "benign")),
        ):
            with open(os.path.join(outdir, fname), "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(hdr)
                w.writerows(rows)
        print("\nCSV written to %s" % outdir)


if __name__ == "__main__":
    main()
