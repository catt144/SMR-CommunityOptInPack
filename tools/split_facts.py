#!/usr/bin/env python
"""split_facts.py — docs/agent/ENGINE_FACTS.md -> docs/agent/facts/
(DOC_RESTRUCTURE_SPEC §3b, executed by the docs-restructure chain's prompt 3).

    python tools/split_facts.py --dry-run     # accounting only, writes nothing
    python tools/split_facts.py --write       # perform the split
    python tools/split_facts.py --dry-run --from-git HEAD~1   # source from git

PORTED 2026-08-12 (split-optins prompt 3) from SMR-BugFixPack @ 33d69f5.
⚠️ The MIGRATION half is N/A here — this repo never held a
`docs/agent/ENGINE_FACTS.md`; `docs/agent/facts/` arrived as a whole-folder
copy. What doccheck imports every run IS live: `load_from_dir`, `FACT_FIELDS`,
`BULLET_RE` and `render_index`, which must keep reproducing the copied
`INDEX.md` byte-for-byte — so nothing below is edited, not even prose.

Sibling of `tools/split_bugs.py` and deliberately parasitic on it: the front
matter is written in the SAME dialect (JSON scalars, so backslashes, quotes and
em-dashes round-trip through `json.loads` with no YAML library) and is read back
with `split_bugs.parse_front`. There is exactly one front-matter parser in this
repo.

WHAT THE FILE LOOKS LIKE (verified 2026-08-03 against 713 lines):

  ENGINE_FACTS.md is a BULLET LIST, not a document of headings. A fact starts
  at every COLUMN-0 `- ` and owns every following line — blank or indented —
  up to the next one. Facts carry multi-paragraph indented continuation,
  nested `*` sub-bullets, and one full markdown table (the "OFF is three
  different things" fact). Everything before the first column-0 bullet is the
  preamble and goes to `_preamble.md`.

  ⚠️ THE FAILURE MODE THIS GUARDS (inherited from the chain's prompt 2, which
  found a fourth structural `##` line in BUGS.md that byte-accounting could
  never have seen): a stray column-0 line that is NOT a fact — a divider, a
  de-indented continuation paragraph — is swallowed into the previous fact,
  or splits one in half, and EVERY LINE STILL ADDS UP. Byte-accounting is
  blind to it. So the fact set is derived TWO independent ways and the two
  must agree:

    A. by shape   — column-0 lines matching `- `;
    B. by block   — column-0 lines that are not blank, at all, whatever they
                    start with. Every one of them must be a fact from set A;
                    a column-0 line that is not a bullet means the file grew a
                    structure this splitter does not model, and the run aborts
                    rather than guessing which fact should own it.

  and both are then asserted against the RECORDED table below (43 facts, start
  line + first 40 characters), so a fact that moved, merged or split is a red
  run and not a silent re-numbering.
"""

import argparse
import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TOOLS)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import split_bugs  # noqa: E402  (parse_front, blame plumbing, SplitError)

SplitError = split_bugs.SplitError

SOURCE_REL = "docs/agent/ENGINE_FACTS.md"
OUT_REL = "docs/agent/facts"
SPLIT_DATE = "2026-08-03"

BULLET_RE = re.compile(r"^- ")
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# A date the fact's own text presents as an observation. Mechanical: one of
# these words, then at most 24 characters, then an ISO date, first match wins,
# searched over the fact's lines JOINED (the phrase straddles a line break in
# EF-039 and would be missed line-by-line). This fills spec §3b's `verified:`
# "where the text states one" — it is an EXTRACTION, not an adjudication; the
# body, which for several facts carries an explicit "what is measured and what
# is not" paragraph, stays authoritative.
VERIFIED_RE = re.compile(
    r"(?i)(measured|verified|proven|proved|observed|recorded|established|"
    r"enumerated|confirmed|found|source-read|source-verified)[^\n]{0,24}?"
    r"(\d{4}-\d{2}-\d{2})")

SUMMARY_MAX = 120
GENERATED_BANNER = split_bugs.GENERATED_BANNER
FACT_FIELDS = ["id", "seq", "summary", "updated", "verified", "lines"]

# --- recorded facts, asserted at run time (they are claims, not licences) ----
# 43 facts: (start line, first 40 characters after the `- `). Generated from
# the file and then FROZEN — the point is that the next run must reproduce it.
RECORDED = [
    (9, "**Mod code loads BEFORE the classes are "),
    (36, "**\"OFF\" IS THREE DIFFERENT THINGS, and o"),
    (92, "`g_Consts` is a **GameVar** (`Lua\\Modifi"),
    (95, "**`CurrentModOptions` is PER-MOD-ENV** ("),
    (103, "Engine Lua tolerates `#nil`/`next(nil)`/"),
    (107, "**Mods run in a sandbox (LuaModEnv) on A"),
    (117, "**`Msg`/`OnMsg` are PER-ENV OWN KEYS and"),
    (130, "**`error()` and `assert()` do NOT unwind"),
    (135, "**`rawset(_G, k, v)` from mod code write"),
    (140, "**CORRECTION of an earlier \"fact\": `debu"),
    (146, "Patch points that work: `PeriodicRepeatI"),
    (151, "A post-wrapper on a **command** method ("),
    (154, "Mod registry: every fix goes through `SM"),
    (158, "All line numbers reference `ModTools\\Src"),
    (179, "**`print` does NOT reach the log file — "),
    (191, "Sample mod format in `<game>\\ModTools\\Sa"),
    (192, "**Replacing an EXISTING global from mod "),
    (198, "**`OnMsg` is additive, confirmed structu"),
    (201, "**GAME-TIME THREADS PERSIST BY DEFAULT —"),
    (217, "**A named GLOBAL game-time thread's BODY"),
    (240, "**Every shipped popup is ASYNC — the per"),
    (251, "**A MOD-AUTHORED CLOSURE STORED ON A PER"),
    (279, "**THE REAL RULE (measured 2026-07-31, PT"),
    (348, "**MODS *DO* GET A PRE-SAVE HOOK — `OnMsg"),
    (373, "**ENABLING A MOD AT THE MAIN MENU IS A D"),
    (406, "**`Msg` dispatches static handlers throu"),
    (412, "**THE BY-VALUE THREAD SERIALISATION IS D"),
    (425, "**THE SAVE/LOAD HOOK SURFACE — enumerate"),
    (451, "**`CreateGameTimeThread` DEFERS — the bo"),
    (484, "**THE PRE-SAVE HOOK COVERS AUTOSAVES — `"),
    (502, "**`IsValidThread` returns NO VALUE for a"),
    (506, "**`Wakeup(thread)` only wakes a thread s"),
    (510, "**TOOLING: never round-trip a doc throug"),
    (517, "**Label membership: `AddToCityLabels` is"),
    (540, "**Units and rovers are labelled through "),
    (549, "**`Init` and `Done` are COMBINED methods"),
    (560, "**Pin release is guarded, and `TogglePin"),
    (571, "**The fastest PLAYER-REACHABLE game spee"),
    (586, "**RE-USING A SHIPPED TRANSLATION ID TO C"),
    (636, "**`GameRandom:Random` — BOTH FORMS MEASU"),
    (672, "**UI coordinate spaces: `XWindow.box` an"),
    (691, "**`UIL.GetSafeArea()` returns FOUR ABSOL"),
    (706, "**`terminal.desktop.scale` is `GetUIScal"),
]
PREAMBLE_LINES = 8


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

def load_lines(rev=None, path=None):
    """-> source lines. Same loader as the BUGS split, pointed elsewhere."""
    saved = split_bugs.SOURCE_REL
    split_bugs.SOURCE_REL = SOURCE_REL
    try:
        return split_bugs.load_lines(rev=rev, path=path)
    finally:
        split_bugs.SOURCE_REL = saved


def blame_dates(rev, nlines):
    saved = split_bugs.SOURCE_REL
    split_bugs.SOURCE_REL = SOURCE_REL
    try:
        return split_bugs.blame_dates(rev, nlines)
    finally:
        split_bugs.SOURCE_REL = saved


def summarize(lines, start, end):
    """The fact's summary: its opening bold phrase, else its first 8 words.

    Judgment-free by construction: the bold branch fires only when the fact
    OPENS with `**` (three of the 43 do not), and the phrase may span lines —
    `THE REAL RULE ...` runs to three — so the fact's text is joined before the
    closing `**` is looked for.
    """
    text = " ".join(x.strip() for x in lines[start - 1:end]).strip()
    text = re.sub(r"^-\s+", "", text)
    text = re.sub(r"\s+", " ", text)
    if text.startswith("**"):
        close = text.find("**", 2)
        if close > 2:
            summary = text[2:close].strip()
        else:
            raise SplitError("line %d: opening `**` is never closed" % start)
    else:
        summary = " ".join(text.split(" ")[:8])
    summary = summary.rstrip(" :;,")
    if not summary:
        raise SplitError("line %d: empty summary" % start)
    if len(summary) > SUMMARY_MAX:
        summary = summary[:SUMMARY_MAX - 1].rstrip() + "…"
    return summary


def verified_date(lines, start, end):
    """-> the first date the fact's own text presents as an observation, or None."""
    text = re.sub(r"\s+", " ", " ".join(lines[start - 1:end]))
    m = VERIFIED_RE.search(text)
    return m.group(2) if m else None


def parse(lines):
    """-> the split model. Raises SplitError on any structural surprise."""
    n = len(lines)

    # ---- derivation A: the shape rule --------------------------------------
    by_shape = [i + 1 for i, line in enumerate(lines) if BULLET_RE.match(line)]
    if not by_shape:
        raise SplitError("no column-0 `- ` bullets — is this the pre-split file?")
    first = by_shape[0]

    # ---- derivation B: every column-0 line, whatever it starts with --------
    # If B finds a column-0 line that A did not, the file grew a structure this
    # splitter does not model and a human must look — see the module docstring.
    by_block = [i + 1 for i, line in enumerate(lines)
                if i + 1 >= first and line.strip() and not line[0].isspace()]
    if by_block != by_shape:
        extra = [(ln, lines[ln - 1][:60]) for ln in by_block if ln not in set(by_shape)]
        raise SplitError(
            "the two derivations disagree — column-0 line(s) that are not "
            "facts:\n  " + "\n  ".join("%d: %r" % x for x in extra))

    # ---- and both against the record ---------------------------------------
    shaped = [(ln, lines[ln - 1][2:42]) for ln in by_shape]
    if shaped != RECORDED:
        only_now = [x for x in shaped if x not in RECORDED]
        only_rec = [x for x in RECORDED if x not in shaped]
        raise SplitError(
            "the fact set changed (%d found, %d on record).\n  new/moved: %r\n"
            "  gone:      %r" % (len(shaped), len(RECORDED),
                                 only_now[:4], only_rec[:4]))
    if first - 1 != PREAMBLE_LINES:
        raise SplitError("preamble is %d lines, %d on record"
                         % (first - 1, PREAMBLE_LINES))

    # ---- facts -------------------------------------------------------------
    facts = []
    for seq, start in enumerate(by_shape, 1):
        end = by_shape[seq] - 1 if seq < len(by_shape) else n
        facts.append({
            "seq": seq, "id": "EF-%03d" % seq, "start": start, "end": end,
            "summary": summarize(lines, start, end),
            "verified": verified_date(lines, start, end),
        })
    preamble = list(range(1, first))

    # ---- the accounting ----------------------------------------------------
    owned = {}
    def claim(line, owner):
        if line in owned:
            raise SplitError("line %d claimed by %s and %s" % (line, owned[line], owner))
        owned[line] = owner
    for fact in facts:
        for ln in range(fact["start"], fact["end"] + 1):
            claim(ln, fact["id"])
    for ln in preamble:
        claim(ln, "_preamble.md")
    missing = [ln for ln in range(1, n + 1) if ln not in owned]
    if missing:
        raise SplitError("lines owned by nothing: %r" % missing[:20])
    fact_lines = sum(f["end"] - f["start"] + 1 for f in facts)
    if fact_lines + len(preamble) != n:
        raise SplitError("accounting does not balance")

    return {"lines": lines, "n": n, "facts": facts, "preamble": preamble,
            "first": first,
            "counts": {"fact_lines": fact_lines, "preamble": len(preamble),
                       "total": n}}


def enrich(model, dates):
    """`updated:` per fact.

    The brief said "git blame of the fact's first line"; this takes the MAX over
    the fact's whole line range instead, which is what `updated` means in the
    sibling schema (spec §2, "date of last substantive edit") — a fact whose
    body was corrected last week has not been unchanged since its heading was
    written. Deliberate, recorded here and in the split commit body.
    """
    for fact in model["facts"]:
        fact["updated"] = max(dates[ln] for ln in
                              range(fact["start"], fact["end"] + 1))
        fact["head_updated"] = dates[fact["start"]]
        fact["lines"] = fact["end"] - fact["start"] + 1
    return model


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

def render_fact(model, fact):
    out = ["---"]
    for field in FACT_FIELDS:
        value = fact[field]
        if isinstance(value, int):
            out.append("%s: %d" % (field, value))
        else:
            out.append("%s: %s" % (field, json.dumps(value, ensure_ascii=False)))
    out.append("---")
    out.extend(model["lines"][fact["start"] - 1:fact["end"]])
    return out


def render_preamble(model):
    front = ["---", 'kind: "preamble"',
             "source: %s" % json.dumps(
                 "%s, split %s by tools/split_facts.py" % (SOURCE_REL, SPLIT_DATE),
                 ensure_ascii=False),
             "---"]
    added = [
        "# ENGINE_FACTS.md preamble — byte-preserved",
        "",
        "The %d lines below the `---` opened `%s` before it was split into"
        % (len(model["preamble"]), SOURCE_REL),
        "one file per fact on %s. They are preserved exactly; the facts"
        % SPLIT_DATE,
        "themselves are `EF-###.md` in this folder and `INDEX.md` lists them.",
        "",
        "---",
        "",
    ]
    body = [model["lines"][ln - 1] for ln in model["preamble"]]
    return front + added + body, len(front), len(added), len(body)


def index_rows(model):
    return [{"id": f["id"], "summary": f["summary"], "updated": f["updated"],
             "verified": f["verified"] or "—", "lines": f["lines"],
             "file": "%s.md" % f["id"]} for f in model["facts"]]


def render_index(model):
    rows = index_rows(model)
    dated = len([r for r in rows if r["verified"] != "—"])
    out = [
        GENERATED_BANNER,
        "<!-- regenerate: python tools/split_facts.py --write "
        "(migration) / verify: python tools/doccheck.py -->",
        "",
        "# Engine facts index — %d facts" % len(rows),
        "",
        "One file per top-level bullet of the old `docs/agent/ENGINE_FACTS.md`, in",
        "source order; ids are stable. `updated` is git's last touch of the fact's",
        "own lines. `verified` is the first date the fact's TEXT presents as an",
        "observation (%d of %d state one) — a mechanical extraction, not an"
        % (dated, len(rows)),
        "adjudication: read the fact for what was actually measured, several of",
        "which carry their own ⚖️ \"what is measured and what is not\" paragraph.",
        "The preamble that opened the old file is `_preamble.md`.",
        "",
        "| id | summary | verified | updated | lines | fact |",
        "|----|---------|----------|---------|-------|------|",
    ]
    for row in rows:
        out.append("| %s | %s | %s | %s | %d | [%s](%s) |" % (
            row["id"], split_bugs.cell(row["summary"]), row["verified"],
            row["updated"], row["lines"], row["file"], row["file"]))
    out.append("")
    return out


def render_stub():
    return [
        "# Engine Facts — MOVED %s" % SPLIT_DATE,
        "",
        "One file per fact: `docs/agent/facts/EF-###.md` · generated index: "
        "`docs/agent/facts/INDEX.md` · the old file's opening prose: "
        "`docs/agent/facts/_preamble.md`.",
        "",
    ]


# --------------------------------------------------------------------------
# verification + accounting
# --------------------------------------------------------------------------

def accounting(model, out):
    counts = model["counts"]
    facts = model["facts"]
    longest = max(facts, key=lambda f: f["end"] - f["start"])
    dated = len([f for f in facts if f["verified"]])
    out.append("SOURCE: %s — %d lines" % (SOURCE_REL, counts["total"]))
    out.append("  lines 1..%d       preamble → _preamble.md      %5d"
               % (model["first"] - 1, counts["preamble"]))
    out.append("  lines %d..%d     %d facts → EF-001..EF-%03d      %5d"
               % (model["first"], counts["total"], len(facts), len(facts),
                  counts["fact_lines"]))
    out.append("  ---------------------------------------------------------------")
    out.append("  %d fact + %d preamble = %d == %d source lines  %s"
               % (counts["fact_lines"], counts["preamble"],
                  counts["fact_lines"] + counts["preamble"], counts["total"],
                  "OK" if counts["fact_lines"] + counts["preamble"]
                  == counts["total"] else "MISMATCH"))
    out.append("  every source line is claimed exactly once (checked line by line)")
    out.append("DERIVATIONS: shape (column-0 `- `) and block (every column-0 "
               "non-blank line) both yield the same %d starts, and both match "
               "the recorded table" % len(facts))
    out.append("FACTS: shortest %d lines, longest %d (%s), median %d; "
               "%d of %d state an observation date"
               % (min(f["end"] - f["start"] + 1 for f in facts),
                  longest["end"] - longest["start"] + 1, longest["id"],
                  sorted(f["end"] - f["start"] + 1 for f in facts)[len(facts) // 2],
                  dated, len(facts)))
    drift = [f["id"] for f in facts if f["updated"] != f["head_updated"]]
    out.append("UPDATED: from git blame, max over each fact's own lines; %d of "
               "%d differ from the first line's own date" % (len(drift), len(facts)))


def verify_written(model, outdir, out):
    """Re-read what was written and compare it to the source, line by line."""
    problems = []
    expected = {"%s.md" % f["id"] for f in model["facts"]}
    present = {n for n in os.listdir(outdir)
               if n.endswith(".md") and n not in ("INDEX.md", "_preamble.md")}
    if present != expected:
        problems.append("fact file set differs: extra %r, missing %r"
                        % (sorted(present - expected), sorted(expected - present)))
    for fact in model["facts"]:
        path = os.path.join(outdir, "%s.md" % fact["id"])
        if not os.path.exists(path):
            continue
        _front, body = split_bugs.parse_front(path)
        source = model["lines"][fact["start"] - 1:fact["end"]]
        if body != source:
            problems.append("%s: body differs from source lines %d-%d"
                            % (fact["id"], fact["start"], fact["end"]))
    _front, pre_body = split_bugs.parse_front(os.path.join(outdir, "_preamble.md"))
    preserved = [model["lines"][ln - 1] for ln in model["preamble"]]
    if pre_body[-len(preserved):] != preserved:
        problems.append("_preamble.md: preserved tail differs from source")
    if problems:
        raise SplitError("written output failed verification:\n  "
                         + "\n  ".join(problems))
    out.append("WRITTEN: %d fact files re-read and compared line-by-line to their "
               "source slices — identical; _preamble.md's %d preserved lines "
               "identical and in source order" % (len(model["facts"]), len(preserved)))


def write_all(model, out):
    outdir = os.path.join(REPO, OUT_REL)
    os.makedirs(outdir, exist_ok=True)
    for fact in model["facts"]:
        split_bugs.write_lines(os.path.join(outdir, "%s.md" % fact["id"]),
                               render_fact(model, fact))
    pre, n_front, n_added, n_body = render_preamble(model)
    split_bugs.write_lines(os.path.join(outdir, "_preamble.md"), pre)
    split_bugs.write_lines(os.path.join(outdir, "INDEX.md"), render_index(model))
    split_bugs.write_lines(os.path.join(REPO, SOURCE_REL), render_stub())
    out.append("WROTE: %d fact files, _preamble.md (%d front-matter + %d added + "
               "%d preserved lines), INDEX.md (%d rows), and the %s stub"
               % (len(model["facts"]), n_front, n_added, n_body,
                  len(index_rows(model)), SOURCE_REL))
    verify_written(model, outdir, out)


def build(rev=None, path=None):
    lines = load_lines(rev=rev, path=path)
    model = parse(lines)
    return enrich(model, blame_dates(rev, len(lines)))


def verify_split(rev, out):
    """doccheck --verify-facts-split: re-run the whole accounting against the
    pre-split blob and compare it to what is on disk today. Sibling of
    split_bugs.verify_split; REV must be a commit whose tree still has the
    unsplit ENGINE_FACTS.md, so pass the sha explicitly."""
    import subprocess
    try:
        model = build(rev=rev)
    except subprocess.CalledProcessError:
        raise SplitError("cannot read %s:%s" % (rev, SOURCE_REL))
    accounting(model, out)
    verify_written(model, os.path.join(REPO, OUT_REL), out)


# --------------------------------------------------------------------------
# reading the split back — the surface doccheck validates from here on
# --------------------------------------------------------------------------

def load_from_dir(outdir=None):
    """-> the model shape render_index() needs, rebuilt from the split files."""
    outdir = outdir or os.path.join(REPO, OUT_REL)
    facts = []
    for name in sorted(os.listdir(outdir)):
        if not name.endswith(".md") or name in ("INDEX.md", "_preamble.md"):
            continue
        front, body = split_bugs.parse_front(os.path.join(outdir, name))
        fact = dict(front)
        fact["file"] = name[:-3]
        fact["body"] = body
        facts.append(fact)
    facts.sort(key=lambda f: f.get("seq", 0))
    return {"facts": facts}


def main():
    ap = argparse.ArgumentParser(description="ENGINE_FACTS.md -> agent/facts/")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="print the accounting only")
    mode.add_argument("--write", action="store_true", help="perform the split")
    ap.add_argument("--from-git", metavar="REV",
                    help="read the source from a git revision instead of the worktree")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    out = []
    try:
        model = build(rev=args.from_git)
        accounting(model, out)
        if args.write:
            write_all(model, out)
        else:
            out.append("DRY RUN — nothing written.")
    except SplitError as exc:
        print("\n".join(out))
        print("\nsplit_facts: ABORTED — %s" % exc)
        return 1
    print("\n".join(out))
    print("split_facts: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
