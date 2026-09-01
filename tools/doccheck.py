#!/usr/bin/env python
"""doccheck.py — the structure checker (DOC_RESTRUCTURE_SPEC.md §5).

v1 (prompt 1, 2026-08-03): BUGS.md row<->tag status-word agreement, a counts
recount printed as a STATE-ready block, and a TEMPORARY sweep over both repos.
v2 (prompt 2, 2026-08-03): docs/BUGS.md is now 116 entry files under
docs/agent/bugs/ plus a GENERATED INDEX.md, so the row<->tag check moves onto
front matter, INDEX freshness is checked by regenerating and diffing, and
`--verify-split` re-runs the migration's byte-accounting against the pre-split
blob in git.
v5 (2026-08-31, readiness pass): the four checks the donor grew after the
split, carried across from SMR-BugFixPack @ bec2e06 — (1) STATE.md is
budgeted in BYTES with a per-line cap (owner ruling 2026-08-18, checklist
42; the 60-line cap is RETIRED); (2) `tested-attended` / `tested-unattended`
join the status vocabulary (owner ruling 2026-08-15, checklist 26b);
(3) LOAD_ORDER_RULES — this repo's two shared-symbol wrap orders in
`metadata.lua`'s `code` list are enforced, not just commented; (4) the F107
wrap-target check (`harvest_wrap_targets.py --check`, FIX_POLICY §2).
GENERAL_USE_PROMPT.md's line cap is kept but N/A — that prompt is
single-sourced in the fix pack (docs/README.md).

v4 (split-optins prompt 3, 2026-08-12): PORTED to SMR-OptInPack from
SMR-BugFixPack @ 33d69f5. Four deliberate differences, each recorded in
docs/agent/PROVENANCE.md: (1) the registered-module needle is
`SMROptInPack.Register(`; (2) the optional-module count is the ANCHORED
def-field form and `default_active = modules - optional` — the donor's
hard-coded `- 7` and its substring `optional = true` count were BOTH wrong
(the substring matches a comment in Opt_DroneStatDials.lua, and the constant
would have read 67 on the post-split fix-pack side); (3) the three STUBS are
DROPPED, not faked — they exist in the donor so pre-restructure references
resolve, and this repo has no such history; (4) the probe count is reported as
SHARED — one TestKit serves both mods, so this number is the same number the
fix pack emits and is labelled so it can never read as a second suite.
`--verify-split` / `--verify-facts-split` are kept but are N/A here: they
re-run migrations against the DONOR repo's git history.

v3 (prompt 3, 2026-08-03): the tree moved. Adds the docs/ root allowlist,
checked BOTH DIRECTIONS **against the README map itself** (the list is PARSED
out of docs/README.md, never duplicated here, so the map cannot drift from the
folder it documents); the STATE.md line budget; stub presence; and the same
front-matter + INDEX-freshness treatment for the 43 files under
docs/agent/facts/.

    python tools/doccheck.py                 # check; exit 1 on any red
    python tools/doccheck.py --emit-counts   # + the pasteable counts block
    python tools/doccheck.py --verify-split [REV]   # REV defaults to HEAD~1

Every parsing rule below that carries a "trap" note was learned the hard way by
the 2026-08-03 QA session that hand-ran these checks. Do not "simplify" them.
"""

import argparse
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ONE kit serves both mods (split-optins, 2026-08-12): the probe count below
# is the SAME number the fix pack's doccheck emits, not a second suite.
TESTKIT = os.environ.get("SMR_TESTKIT", r"C:\Dev\SMR-BugFixPack-TestKit")

DOCS = os.path.join(REPO, "docs")
BUGS = os.path.join(DOCS, "BUGS.md")                  # a stub since 2026-08-03
BUGS_DIR = os.path.join(DOCS, "agent", "bugs")
FACTS_DIR = os.path.join(DOCS, "agent", "facts")
README = os.path.join(DOCS, "README.md")
STATE = os.path.join(DOCS, "agent", "STATE.md")
CODE = os.path.join(REPO, "Code")

# 2026-08-18 owner ruling (checklist 42), carried here 2026-08-31: STATE.md is
# budgeted in BYTES, not lines. The 60-line budget was satisfied while being
# defeated — single lines grew into thousand-word walls (the fix pack's hit
# 71,077 B = 33,066 tokens; this repo's line 28 was 1,734 B). Bytes are the
# resource a session actually spends at boot. Crossing WARN prints a warn
# line that close-out reports must copy to the owner verbatim; the owner then
# fires agent/prompts/STATE_EVICTION.md. The hard cap is the backstop if flags
# go unread. The per-line cap keeps lines atomic (grep/diff/Edit-safe) so
# walls cannot return inside the budget; never widen lines to satisfy anything.
STATE_WARN_BYTES = 9 * 1024
STATE_MAX_BYTES = 18 * 1024
STATE_MAX_LINE_BYTES = 200

# The standing prompt is instructions, not a logbook (rule added 2026-08-04
# after two sittings appended their lessons to it — the habit that grew the
# old 43k-token prompt). The cap is a tripwire, not a prohibition: at the cap,
# relocate per the prompt's own routing rule (WORKFLOW / PLAYTEST_HELP /
# agent/facts/ / the entry), then trim.
# The standing prompts are instructions, not logbooks (donor rule 2026-08-04).
# Here the capped files are WORK_PROMPT.md (start-here for any work) and
# DISPATCH.md (live-issue triage); GENERAL_USE_PROMPT.md is single-sourced in
# the fix pack and only checked if someone ever copies it here.
GENERAL_USE = os.path.join(DOCS, "agent", "prompts", "GENERAL_USE_PROMPT.md")
STANDING_PROMPTS = [os.path.join(DOCS, "agent", "prompts", n)
                    for n in ("WORK_PROMPT.md", "DISPATCH.md", "GENERAL_USE_PROMPT.md")]
GENERAL_USE_MAX_LINES = 220

# N/A HERE (split-optins, 2026-08-12) — the donor carries three MOVED stubs
# (docs/BUGS.md, docs/STATUS.md, docs/agent/ENGINE_FACTS.md) so its
# pre-2026-08-03 references resolve one hop away. This repo has no
# pre-restructure history, so the stubs are DROPPED rather than faked: a faked
# signpost is a lie the tool would then enforce. The clause is kept in writing
# so nobody re-adds it by reading the donor.

# Index rows. Trap (a): this pattern also matches a rate table inside the F97
# entry (`| F97 | **50%** (gate fails) | ...`) — dedupe by ID, keep the FIRST.
ROW_RE = re.compile(r"^\|\s*([FDC]\d+)\s*\|")

# Entry headings. Trap: `^### ` alone is NOT an entry delimiter — entries carry
# their own `###` sub-headings (e.g. F97's "### THE UNINSTALL LOG..."), so the
# ID must be matched explicitly.
HEAD_RE = re.compile(r"^### ([FDC]\d+)\b")

# Heading tag. Trap: titles contain backticks (e.g. `table.remove`), so the tag
# is the LAST `[...]` group on the line, never the first backtick group.
TAG_RE = re.compile(r"`\[(.*)\]`\s*$")

# Status vocabulary, longest-first so `fixed*` is never read as `fixed` and
# `tested-attended` is never read as `tested` (status_word() uses startswith).
#
# ⚖️ Owner ruling 2026-08-15 (fix-pack checklist 26b), carried 2026-08-31:
# `tested` SPLITS by who was present.
#   tested-attended    — a human was at the keyboard when it was confirmed.
#   tested-unattended  — confirmed by real launches with nobody watching:
#                        measurements are real, screen events are NOT claimable.
#   tested             — ⛔ LEGACY ONLY, pre-2026-08-15 (D02/D03/D04/D09 here).
#                        Attendance is NOT recorded; never apply it to new work.
STATUS_WORDS = sorted(
    [
        "tested-unattended", "tested-attended", "tested",
        "fixed*", "fixed", "wontfix", "blocked", "todo", "open",
        "investigating", "closed", "built", "directed", "parked", "opt-in",
        "candidate", "folded", "filed", "speced", "cand", "dsgn",
    ],
    key=len,
    reverse=True,
)

# Emphasis/attention markup that can precede the status word in either place:
# bold stars, strikethrough, backticks and a growing zoo of emoji (⭐ ⛔ ✅ ⚠️
# ⏸️ ⚖️ ...). Strip every leading non-letter rather than enumerate them.
MARKUP_RE = re.compile(r"^[^A-Za-z]+")


def read(path):
    with open(path, encoding="utf-8-sig") as fh:
        return fh.read().splitlines()


def status_word(cell):
    """First vocabulary status word of a row cell or heading tag, or None."""
    text = MARKUP_RE.sub("", cell or "").lower()
    for word in STATUS_WORDS:
        if text.startswith(word):
            return word
    return None


def mentions(text, word):
    """Does `word` occur in `text` on a left word boundary?"""
    return re.search(r"(?<![A-Za-z])" + re.escape(word), text, re.IGNORECASE) is not None


def splitter():
    """The migration module, imported lazily so it can import this one."""
    import split_bugs
    return split_bugs


def all_rows(model):
    """-> every index row the split preserved: 116 entry-owning rows, the rows
    adopted into grouped front matter, and the orphan rows in _notes.md."""
    rows = []
    for entry in model["entries"]:
        rows.append(entry)
        rows.extend(entry.get("members", []))
    rows.extend(model["by_id"][i] for i in model["orphans"])
    return rows


def check_entries(model, out):
    """Front-matter validation + the row<->tag check on its new surface.

    v1 compared a hand-written index row against the heading tag. The row is
    gone as a hand-written artifact — it is now `row_status:`, copied verbatim
    and never re-typed — so the same drift is checked between the DERIVED
    `status:` and the tag the entry body still carries. The tag stays
    authoritative; a `row_status` that opens with prose instead of a status word
    is a warn, exactly as before, and is never silently discounted.
    """
    sb = splitter()
    red, warns = [], []
    seqs, rows = {}, {}
    tagged = 0

    for entry in model["entries"]:
        name = entry["file"]
        for field in sb.FRONT_FIELDS:
            if field not in entry:
                red.append("%s: front matter is missing %r" % (name, field))
        if red and red[-1].startswith(name):
            continue
        if entry["status"] not in STATUS_WORDS:
            red.append("%s: status %r is not in the vocabulary"
                       % (name, entry["status"]))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(entry["updated"])):
            red.append("%s: updated %r is not a date" % (name, entry["updated"]))
        if not isinstance(entry["copies"], list):
            red.append("%s: copies must be a list" % name)
        if entry["kind"] == "grouped":
            if name != "%s-%s" % (entry["contains"][0], entry["contains"][-1]):
                red.append("%s: file name does not state the range it holds" % name)
            member_ids = [m["id"] for m in entry["members"]]
            if sorted(entry["contains"]) != sorted([entry["id"]] + member_ids):
                red.append("%s: contains: disagrees with members: + id" % name)
        elif name != entry["id"]:
            red.append("%s: file name does not match id %r" % (name, entry["id"]))

        # the body must still open with the heading the split preserved
        body = entry["body"]
        head = HEAD_RE.match(body[0]) if body else None
        if not head or head.group(1) != entry["id"]:
            red.append("%s: body does not open with its `### %s` heading"
                       % (name, entry["id"]))
        else:
            tag = TAG_RE.search(body[0])
            if tag:
                tagged += 1
                word = status_word(tag.group(1))
                if word is None:
                    red.append("%s: heading tag has no vocabulary status word: %r"
                               % (name, tag.group(1)[:60]))
                elif word != entry["status"]:
                    red.append("%s: front matter says %r, heading tag says %r"
                               % (name, entry["status"], word))
                elif entry["status_source"] != "tag":
                    red.append("%s: status_source is %r but the heading is tagged"
                               % (name, entry["status_source"]))
            elif entry["status_source"] == "tag":
                red.append("%s: status_source says 'tag' but the heading has none"
                           % name)

        seqs.setdefault(entry["seq"], []).append(name)

    sources = {}
    for row in all_rows(model):
        rows.setdefault(row["row"], []).append(row["id"])
        sources[row["status_source"]] = sources.get(row["status_source"], 0) + 1
        word = status_word(row["row_status"])
        if word is not None and word != row["status"]:
            # NOT red, and the difference from v1 is deliberate. v1 compared two
            # LIVE hand-written surfaces, so drift between them was a defect.
            # `row_status` is now a frozen copy of the row the migration
            # deleted: a status that has since advanced (fixed -> tested) MUST
            # be free to leave it behind. Reported so it is never invisible.
            warns.append("%s: the frozen index-row cell says %r, entry says %r "
                         "(from %r)"
                         % (row["id"], word, row["status"], row["status_source"]))

    dup_seq = {k: v for k, v in seqs.items() if len(v) > 1}
    if dup_seq:
        red.append("duplicate seq: %r" % dup_seq)
    if sorted(seqs) != list(range(1, len(model["entries"]) + 1)):
        red.append("seq is not 1..%d contiguous" % len(model["entries"]))
    dup_row = {k: v for k, v in rows.items() if len(v) > 1}
    if dup_row:
        red.append("duplicate index row numbers: %r" % dup_row)
    if sorted(rows) != list(range(1, len(rows) + 1)):
        red.append("index row numbers are not 1..%d contiguous" % len(rows))

    out.append("ENTRIES: %d files (%d grouped), %d preserved index rows, "
               "%d heading tags compared"
               % (len(model["entries"]),
                  len([e for e in model["entries"] if e["kind"] == "grouped"]),
                  len(rows), tagged))
    out.append("  status derived from: %s"
               % ", ".join("%s x%d" % (k, v) for k, v in sorted(sources.items())))
    for line in red:
        out.append("  RED  " + line)
    for line in warns:
        out.append("  warn " + line)
    return not red


def check_index(model, out):
    """INDEX.md is generated: regenerate it and require an empty diff."""
    sb = splitter()
    path = os.path.join(BUGS_DIR, "INDEX.md")
    if not os.path.exists(path):
        out.append("INDEX: RED  %s is missing" % path)
        return False
    with open(path, encoding="utf-8") as fh:
        have = fh.read().replace("\r\n", "\n").split("\n")
    if have and have[-1] == "":
        have.pop()
    want = sb.render_index(model)
    if have == want:
        out.append("INDEX: fresh — regenerating from front matter reproduces "
                   "%s.md byte for byte (%d rows)"
                   % (os.path.basename(path)[:-3], len(sb.index_rows(model))))
        return True
    out.append("INDEX: RED  regenerated INDEX.md differs from the file "
               "(%d lines on disk, %d regenerated)" % (len(have), len(want)))
    for n, (a, b) in enumerate(zip(have, want), 1):
        if a != b:
            out.append("  RED  first difference at line %d:" % n)
            out.append("    on disk:     %r" % a[:100])
            out.append("    regenerated: %r" % b[:100])
            break
    return False


def facts_splitter():
    import split_facts
    return split_facts


def check_facts(model, out):
    """Front-matter validation for docs/agent/facts/.

    Deliberately thinner than check_entries: a fact has no index row and no
    status vocabulary, so what is checkable is that the ids are the contiguous
    source order the split produced, that the file name states the id, and that
    every body still opens with the column-0 bullet the fact IS.
    """
    sf = facts_splitter()
    red = []
    facts = model["facts"]
    for fact in facts:
        name = fact["file"]
        missing = [f for f in sf.FACT_FIELDS if f not in fact]
        if missing:
            red.append("%s: front matter is missing %r" % (name, missing))
            continue
        if name != fact["id"]:
            red.append("%s: file name does not match id %r" % (name, fact["id"]))
        if fact["id"] != "EF-%03d" % fact["seq"]:
            red.append("%s: id does not match seq %d" % (name, fact["seq"]))
        if not str(fact["summary"]).strip():
            red.append("%s: empty summary" % name)
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(fact["updated"])):
            red.append("%s: updated %r is not a date" % (name, fact["updated"]))
        if fact["verified"] is not None and not re.match(
                r"^\d{4}-\d{2}-\d{2}$", str(fact["verified"])):
            red.append("%s: verified %r is neither a date nor null"
                       % (name, fact["verified"]))
        body = fact["body"]
        if not body or not sf.BULLET_RE.match(body[0]):
            red.append("%s: body does not open with its column-0 `- ` bullet" % name)
        elif fact["lines"] != len(body):
            red.append("%s: lines: says %d, body has %d"
                       % (name, fact["lines"], len(body)))
    seqs = sorted(f.get("seq", 0) for f in facts)
    if seqs != list(range(1, len(facts) + 1)):
        red.append("fact seq is not 1..%d contiguous" % len(facts))
    dated = len([f for f in facts if f.get("verified")])
    out.append("FACTS: %d files, %d state an observation date, %d source lines "
               "preserved" % (len(facts), dated,
                              sum(len(f.get("body", [])) for f in facts)))
    for line in red:
        out.append("  RED  " + line)
    return not red


def check_facts_index(model, out):
    """INDEX.md is generated: regenerate it and require an empty diff."""
    sf = facts_splitter()
    path = os.path.join(FACTS_DIR, "INDEX.md")
    if not os.path.exists(path):
        out.append("FACTS INDEX: RED  %s is missing" % path)
        return False
    with open(path, encoding="utf-8") as fh:
        have = fh.read().replace("\r\n", "\n").split("\n")
    if have and have[-1] == "":
        have.pop()
    want = sf.render_index(model)
    if have == want:
        out.append("FACTS INDEX: fresh — regenerating from front matter "
                   "reproduces INDEX.md byte for byte (%d rows)" % len(model["facts"]))
        return True
    out.append("FACTS INDEX: RED  regenerated INDEX.md differs from the file "
               "(%d lines on disk, %d regenerated)" % (len(have), len(want)))
    for n, (a, b) in enumerate(zip(have, want), 1):
        if a != b:
            out.append("  RED  first difference at line %d:" % n)
            out.append("    on disk:     %r" % a[:100])
            out.append("    regenerated: %r" % b[:100])
            break
    return False


def readme_map(out):
    """-> the set of docs/ root names the README map declares, or None.

    The allowlist is PARSED, never duplicated here: the map and the folder are
    the two things that must agree, so a second hard-coded copy in this file
    would just be a third thing to drift. Rows are the fenced-block lines
    indented EXACTLY two spaces (deeper indents are `agent/`'s contents or a
    description wrapping onto its own line); a row may name several files
    separated by ` · `.
    """
    if not os.path.exists(README):
        out.append("ROOT: RED  docs/README.md is missing — nothing to check against")
        return None
    lines = read(README)
    fence = [i for i, line in enumerate(lines) if line.strip() == "```"]
    names = set()
    if len(fence) >= 2:
        for line in lines[fence[0] + 1:fence[1]]:
            if not re.match(r"^ {2}\S", line):
                continue
            field = re.split(r"\s{2,}", line.strip())[0]
            for part in field.split(" · "):
                part = part.strip()
                if part and part != "docs/":
                    names.add(part.rstrip("/") if part.endswith("/") else part)
    if not names:
        # Never pass silently: an unparseable map is a red map.
        out.append("ROOT: RED  could not read a file list out of docs/README.md's "
                   "map block — the allowlist has no source")
        return None
    return names


def check_root(out):
    """The docs/ root allowlist, BOTH directions, against the README map."""
    declared = readme_map(out)
    if declared is None:
        return False
    present = set(os.listdir(DOCS))
    extra = sorted(present - declared)
    missing = sorted(declared - present)
    if not extra and not missing:
        out.append("ROOT: docs/ holds exactly the %d entries docs/README.md's map "
                   "declares (%s)" % (len(declared), ", ".join(sorted(declared))))
        return True
    for name in extra:
        out.append("  RED  docs/%s exists but the README map does not declare it "
                   "— move it under agent/ or archive/, or add it to the map" % name)
    for name in missing:
        out.append("  RED  the README map declares docs/%s and it is not there" % name)
    out.append("ROOT: RED  %d undeclared, %d declared-but-absent"
               % (len(extra), len(missing)))
    return False


def check_state(out):
    """STATE.md's byte budget (checklist 42); the stub half is N/A here."""
    red, warns = [], []
    if not os.path.exists(STATE):
        red.append("docs/agent/STATE.md is missing — it is the mandatory read")
        n_state = None
    else:
        with open(STATE, "rb") as f:
            raw = f.read()
        n_state = len(raw)
        if n_state > STATE_MAX_BYTES:
            red.append("STATE.md is %d bytes, hard cap is %d — run "
                       "agent/prompts/STATE_EVICTION.md; history belongs in "
                       "archive/SESSION_LOG.md" % (n_state, STATE_MAX_BYTES))
        elif n_state > STATE_WARN_BYTES:
            warns.append("STATE.md is %d bytes, warn threshold is %d — copy "
                         "this line VERBATIM into the owner report; the owner "
                         "fires agent/prompts/STATE_EVICTION.md"
                         % (n_state, STATE_WARN_BYTES))
        for i, ln in enumerate(raw.split(b"\n"), 1):
            if len(ln) > STATE_MAX_LINE_BYTES:
                red.append("STATE.md line %d is %d bytes, per-line cap is %d — "
                           "one fact per line; walls defeat grep, diff and "
                           "audit" % (i, len(ln), STATE_MAX_LINE_BYTES))
    for prompt in STANDING_PROMPTS:
        if not os.path.exists(prompt):
            continue
        n_gu = len(read(prompt))
        if n_gu > GENERAL_USE_MAX_LINES:
            red.append("%s is %d lines, budget is %d — it is instructions, not "
                       "a logbook; route the lesson to its home (WORKFLOW / "
                       "FIX_POLICY / agent/facts/ / the entry) and trim"
                       % (os.path.basename(prompt), n_gu, GENERAL_USE_MAX_LINES))
    out.append("STATE: STATE.md %s bytes (warn %d, hard %d, line %d); stub "
               "check N/A in this repo"
               % ("?" if n_state is None else n_state, STATE_WARN_BYTES,
                  STATE_MAX_BYTES, STATE_MAX_LINE_BYTES))
    for line in red:
        out.append("  RED  " + line)
    for line in warns:
        out.append("  warn " + line)
    return not red


def lua_files(directory):
    if not os.path.isdir(directory):
        return None
    return sorted(f for f in os.listdir(directory) if f.endswith(".lua"))


# The optional-module def field, ANCHORED. The donor counted the bare
# substring "optional = true", which also matches a COMMENT in
# Opt_DroneStatDials.lua saying the module registers *without* it — so the
# donor reported 8 where 7 files carry the field. Anchor it.
OPTIONAL_FIELD_RE = re.compile(r"^\s+optional = true,\s*$", re.M)


def files_matching(directory, names, pattern):
    hits = []
    for name in names:
        with open(os.path.join(directory, name), encoding="utf-8-sig",
                  errors="replace") as fh:
            if pattern.search(fh.read()):
                hits.append(name)
    return hits


def files_containing(directory, names, needle):
    hits = []
    for name in names:
        with open(os.path.join(directory, name), encoding="utf-8-sig",
                  errors="replace") as fh:
            if needle in fh.read():
                hits.append(name)
    return hits


def occurrences(directory, names, needle):
    total = 0
    for name in names:
        with open(os.path.join(directory, name), encoding="utf-8-sig",
                  errors="replace") as fh:
            total += fh.read().count(needle)
    return total


def recount(model, out):
    """The counts block. Reported, never asserted — adding a module is legal."""
    counts = {}
    rows = [r["id"] for r in all_rows(model)]
    names = lua_files(CODE) or []
    counts["files"] = len(names)
    registered = files_containing(CODE, names, "SMROptInPack.Register(")
    # 00_Core.lua defines Register; it is not itself a registered module.
    counts["modules"] = len([n for n in registered if n != "00_Core.lua"])
    counts["optional"] = len(files_matching(CODE, names, OPTIONAL_FIELD_RE))
    # Every module that is NOT option-gated is active as shipped — here that is
    # DroneStatDials, which registers without `optional` and reports active at
    # its base dial positions. Derived, never a constant (the donor's hard-coded
    # `- 7` was accidentally right only while the pack held exactly 7 gated
    # modules).
    counts["default_active"] = counts["modules"] - counts["optional"]

    tk_code = os.path.join(TESTKIT, "Code")
    tk_names = lua_files(tk_code)
    if tk_names is None:
        counts["probes"] = None
        out.append("NOTE: TestKit not found at %s — probe count skipped "
                   "(set SMR_TESTKIT to override)" % TESTKIT)
    else:
        # minus 1: the SMRTest.Register definition in 00_TestCore.lua.
        counts["probes"] = occurrences(tk_code, tk_names, "SMRTest.Register(") - 1
        out.append("NOTE: the TestKit at %s is SHARED with the fix pack — the "
                   "probe count below is the whole suite, not this mod's share"
                   % TESTKIT)

    for kind in "FDC":
        counts["rows_" + kind] = len([i for i in rows if i.startswith(kind)])

    out.append("COUNTS: %d Code/*.lua files, %d registered modules "
               "(%d default-active, %d files carry optional = true), %s probes"
               % (counts["files"], counts["modules"], counts["default_active"],
                  counts["optional"],
                  "?" if counts["probes"] is None else counts["probes"]))
    out.append("        index rows: %d F + %d D + %d C = %d (in %d entry files)"
               % (counts["rows_F"], counts["rows_D"], counts["rows_C"],
                  counts["rows_F"] + counts["rows_D"] + counts["rows_C"],
                  len(model["entries"])))
    return counts


def temporary_sweep(out):
    """No TEMPORARY markers may survive in shipped or TestKit Lua."""
    hits = []
    for directory in (CODE, os.path.join(TESTKIT, "Code")):
        names = lua_files(directory)
        if names is None:
            continue
        for name in names:
            path = os.path.join(directory, name)
            with open(path, encoding="utf-8-sig", errors="replace") as fh:
                for n, line in enumerate(fh, 1):
                    if "TEMPORARY" in line:
                        hits.append("%s:%d: %s" % (path, n, line.strip()))
    out.append("TEMPORARY SWEEP: %d hit(s) in Code/ + TestKit Code/" % len(hits))
    for hit in hits:
        out.append("  RED  " + hit)
    return not hits


def testkit_tree(out):
    """REPORT-ONLY (owner GO, 2026-08-04): a dirty TestKit working tree is how
    a true, verified record sat stranded unseen for a day — no gate checked
    that repo. This says so on every run; it deliberately does NOT block, so
    TestKit work-in-progress never jams a pack commit. A reported line is
    routed or committed, never `git restore`d (uncommitted work has no reflog)."""
    if not os.path.isdir(os.path.join(TESTKIT, ".git")):
        out.append("TESTKIT TREE: not checked (no repo at %s)" % TESTKIT)
        return True
    try:
        res = subprocess.run(["git", "-C", TESTKIT, "status", "--porcelain"],
                             capture_output=True, text=True, timeout=30)
    except OSError as exc:
        out.append("TESTKIT TREE: not checked (%s)" % exc)
        return True
    if res.returncode != 0:
        out.append("TESTKIT TREE: not checked (git exited %d)" % res.returncode)
        return True
    lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
    if not lines:
        out.append("TESTKIT TREE: clean")
    else:
        out.append("TESTKIT TREE: %d uncommitted change(s) — report-only, "
                   "never a block. Route or commit them; never `git restore` "
                   "(the 2026-08-03 orphan lesson)." % len(lines))
        for ln in lines:
            out.append("  WARN " + ln)
    return True


# ---------------------------------------------------------------------------
# Load-order constraints (carried 2026-08-31 from the donor's sweep-chain link 1)
#
# `metadata.lua`'s `code` list IS the intra-mod load order (FIX_POLICY §8), and
# it is ours to set. Where two modules wrap the SAME function, the LAST one
# listed installs LAST and is the OUTER wrapper. metadata.lua has carried these
# two constraints as a comment since the split ("ORDER IS LOAD-BEARING … so wrap
# nesting is unchanged"); a comment does not fail a build. This check does.
#
# Provenance of the rules: INHERITED from the fix pack's order, MEASURED as the
# nesting every 8/8 leg ran (2026-08-12), never re-derived as a necessity —
# D12's own header says its FindEmigrationDome veto is order-independent with
# D07. The constraint therefore preserves the SHIPPED configuration; reordering
# is a behaviour change under the module freeze, not a tidy-up.
#
# ⛔ It lives in tools/ ON PURPOSE: `*/tools/*` is in `metadata.lua`'s
# `ignore_files`, so nothing here ships.
LOAD_ORDER_RULES = [
    {
        "before": "Code/Opt_CohortHousing.lua",
        "after": "Code/Opt_NoHomeless.lua",
        "symbol": "Colonist:FindEmigrationDome",
        "why": "both post-wrap Colonist:FindEmigrationDome (Opt_CohortHousing.lua:168, "
               "Opt_NoHomeless.lua:449); NoHomeless is the OUTER wrapper as shipped, "
               "so its flagged-dome veto has the last word over CohortHousing's "
               "cross-dome redirect.",
    },
    {
        "before": "Code/Opt_ResidencyControl.lua",
        "after": "Code/Opt_NoHomeless.lua",
        "symbol": "ChooseDome",
        "why": "both pre-filter the global ChooseDome through SetGlobal "
               "(Opt_ResidencyControl.lua:228, Opt_NoHomeless.lua:906); NoHomeless "
               "is OUTER as shipped, so arrivals are screened for flagged domes "
               "before ResidencyControl screens for closed ones.",
    },
]


def load_order(out):
    """Two modules wrapping one function: the list order decides which wins."""
    path = os.path.join(REPO, "metadata.lua")
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        out.append("LOAD ORDER: not checked (%s)" % exc)
        return True
    listed = re.findall(r'"(Code/[^"]+\.lua)"', text)
    index = {}
    for pos, name in enumerate(listed):
        index.setdefault(name, pos)

    ok = True
    checked = 0
    for rule in LOAD_ORDER_RULES:
        first, second = rule["before"], rule["after"]
        if first not in index or second not in index:
            out.append("  RED  load order: %s or %s is not in metadata.lua's "
                       "code list — the %s constraint cannot be checked"
                       % (first, second, rule["symbol"]))
            ok = False
            continue
        checked += 1
        if index[first] >= index[second]:
            out.append("  RED  load order VIOLATED for %s: %s (position %d) "
                       "must be listed BEFORE %s (position %d) — %s"
                       % (rule["symbol"], first, index[first],
                          second, index[second], rule["why"]))
            ok = False
    out.append("LOAD ORDER: %d shared-symbol constraint(s) checked, %d file(s) "
               "in the code list" % (checked, len(listed)))
    return ok


def wrap_targets_check(out):
    """FIX_POLICY §2, the F107 rule (donor 2026-08-24, here 2026-08-31): every
    capture+install wrap site must declare its (class, method) pair in its
    module's Require block. The detector and its allowlist live in
    harvest_wrap_targets.py."""
    try:
        import harvest_wrap_targets as hwt
        violations, allowlisted = hwt.check()
    except Exception as exc:                          # a tool bug must report, not crash the gate
        out.append("WRAP CHECK: not checked (%s)" % exc)
        return True
    out.append("WRAP CHECK: %d wrap site(s) outside Require, %d allowlisted "
               "(FIX_POLICY §2; detector+allowlist in tools/harvest_wrap_targets.py)"
               % (len(violations), len(allowlisted)))
    for mod, c, m, note in violations:
        out.append("  RED  %s wraps %s.%s — %s" % (mod, c, m, note))
    return not violations


def counts_block(counts):
    """A STATE-ready block; commit bodies may paste it verbatim."""
    lines = [
        "BUILD STATE (emitted by tools/doccheck.py)",
        "- modules: %d registered (%d default-active, %d optional-gated files)"
        % (counts["modules"], counts["default_active"], counts["optional"]),
        "- Code/*.lua files: %d" % counts["files"],
        "- TestKit probes: %s"
        % ("not counted (TestKit absent)" if counts["probes"] is None
           else "%d (shared kit — serves both mods)" % counts["probes"]),
        "- BUGS index rows: %d F + %d D + %d C"
        % (counts["rows_F"], counts["rows_D"], counts["rows_C"]),
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="SMR-OptInPack doc structure check")
    ap.add_argument("--emit-counts", action="store_true",
                    help="also print the STATE-ready counts block")
    ap.add_argument("--verify-split", nargs="?", const="HEAD~1", metavar="REV",
                    help="N/A in this repo (kept from the donor): re-runs the "
                         "BUGS split accounting against REV's docs/BUGS.md, "
                         "which only exists in SMR-BugFixPack's history")
    ap.add_argument("--verify-facts-split", metavar="REV",
                    help="N/A in this repo (kept from the donor): re-runs the "
                         "ENGINE_FACTS split accounting against REV's "
                         "docs/agent/ENGINE_FACTS.md, which only exists in "
                         "SMR-BugFixPack's history")
    args = ap.parse_args()

    # The docs are full of non-cp1252 markup; a Windows console (or a git hook
    # running under one) must not die on printing a finding.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    out = []
    sb = splitter()
    sf = facts_splitter()
    try:
        model = sb.load_from_dir()
        ok = check_entries(model, out)
        ok = check_index(model, out) and ok
        facts = sf.load_from_dir()
        ok = check_facts(facts, out) and ok
        ok = check_facts_index(facts, out) and ok
    except sb.SplitError as exc:
        print("doccheck: RED — %s" % exc)
        return 1
    ok = check_root(out) and ok
    ok = check_state(out) and ok
    counts = recount(model, out)
    ok = temporary_sweep(out) and ok
    ok = load_order(out) and ok
    ok = wrap_targets_check(out) and ok
    testkit_tree(out)  # report-only by owner decision (2026-08-04) — never gates

    if args.verify_split:
        try:
            out.append("VERIFY-SPLIT against %s:%s" % (args.verify_split, "docs/BUGS.md"))
            sb.verify_split(args.verify_split, out)
        except sb.SplitError as exc:
            out.append("  RED  %s" % exc)
            ok = False

    if args.verify_facts_split:
        try:
            out.append("VERIFY-FACTS-SPLIT against %s:%s"
                       % (args.verify_facts_split, sf.SOURCE_REL))
            sf.verify_split(args.verify_facts_split, out)
        except sb.SplitError as exc:
            out.append("  RED  %s" % exc)
            ok = False

    print("\n".join(out))
    print("doccheck: %s" % ("GREEN" if ok else "RED"))
    if args.emit_counts:
        print()
        # Never hand a pasteable block to a red run: the whole point of the
        # block is that a commit body can quote it as verified state, and the
        # numbers above a failure are not verified state.
        print(counts_block(counts) if ok
              else "BUILD STATE withheld — doccheck is RED; fix it, then re-run.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
