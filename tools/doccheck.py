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
SMR-BugFixPack @ 33d69f5. Four deliberate differences, now recorded in the
readiness tooling port in tools/README.md: (1) the registered-module needle is
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
import ast
import glob
import os
import posixpath
import re
import subprocess
import sys
import time
import warnings

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ONE kit serves both mods (split-optins, 2026-08-12): the probe count below
# is the SAME number the fix pack's doccheck emits, not a second suite.
TESTKIT = os.environ.get("SMR_TESTKIT", os.path.join(os.path.dirname(REPO),
                                                     "SMR-BugFixPack-TestKit"))

DOCS = os.path.join(REPO, "docs")
BUGS = os.path.join(DOCS, "BUGS.md")                  # a stub since 2026-08-03
BUGS_DIR = os.path.join(DOCS, "agent", "bugs")
FACTS_DIR = os.path.join(DOCS, "agent", "facts")
README = os.path.join(DOCS, "README.md")
STATE = os.path.join(DOCS, "agent", "STATE.md")
CODE = os.path.join(REPO, "Code")
SCRATCH = os.path.join(REPO, "scratch")
LOCAL = os.path.join(REPO, "local")

# 2026-08-18 owner ruling (checklist 42), carried here 2026-08-31: STATE.md is
# budgeted in BYTES, not lines. The 60-line budget was satisfied while being
# defeated — single lines grew into thousand-word walls (the fix pack's hit
# 71,077 B = 33,066 tokens; this repo's line 28 was 1,734 B). Bytes are the
# resource a session actually spends at boot. Crossing WARN prints a warn
# line that close-out reports must copy to the owner verbatim; the owner then
# fires agent/prompts/perma/STATE_EVICTION.md. The hard cap is the backstop if flags
# go unread. The per-line cap keeps lines atomic (grep/diff/Edit-safe) so
# walls cannot return inside the budget; never widen lines to satisfy anything.
STATE_WARN_BYTES = 9 * 1024
STATE_MAX_BYTES = 18 * 1024
STATE_MAX_LINE_BYTES = 200

# The standing prompt is instructions, not a logbook (rule added 2026-08-04
# after two sittings appended their lessons to it — the habit that grew the
# old 43k-token prompt). The cap is a tripwire, not a prohibition: at the cap,
# relocate per the prompt's own routing rule (WORKFLOW / the fix pack's
# agent/facts/ / the entry), then trim.
# The standing prompts are instructions, not logbooks (donor rule 2026-08-04).
# Here the capped files are WORK_PROMPT.md (start-here for any work) and
# DISPATCH.md (live-issue triage); GENERAL_USE_PROMPT.md is single-sourced in
# the fix pack and only checked if someone ever copies it here.
GENERAL_USE = os.path.join(DOCS, "agent", "prompts", "perma", "GENERAL_USE_PROMPT.md")
STANDING_PROMPTS = [os.path.join(DOCS, "agent", "prompts", "perma", n)
                    for n in ("WORK_PROMPT.md", "DISPATCH.md", "GENERAL_USE_PROMPT.md")]
GENERAL_USE_MAX_LINES = 220

# 2026-09-17 RULES-HEADER ARCHITECTURE, ported from SMR-BugFixPack @ ac4e4d3
# (its constants at doccheck.py:138-162, its checks at :2255-2390).
#
# Every binding duty is ONE canonical `Rule:` line inside exactly one
# `## Must_Read_Header` / `<!-- RULES -->` block. This is a deduplication and
# authority mechanism: it makes "where does this rule live" a question with an
# answer, and it is what stops rules breeding in prose.
#
# Every rule carries the donor's trailing `[A3: pass]` tag, adopted by owner
# ruling 2026-09-17 because this repo's own census (cdce060) is the pass it
# records. RULE_STYLE_RE and RULE_DUTY_RE are the donor's forms.
#
# ⚠️ The list is the documents that carry a header TODAY, not an aspiration.
# Adding a file here forces it to grow a block, so a name lands here only when
# that document has a genuinely unique local duty. Absence from this list never
# licenses a Rule: line outside a Must_Read_Header — the placement scan below
# runs over every tracked Markdown file regardless.
RULE_HEADER_DOCS = (
    "CLAUDE.md",
    "docs/PLAYTEST_CHECKLIST.md",
    "docs/PARKED_MODULES.md",
    "docs/agent/FIX_POLICY.md",
    "docs/agent/prompts/README.md",
    # Synced from the donor 2026-09-26 (donor 753358c, owner ruling): chain
    # authoring gained two rules that bind nothing else — approval for a sitting
    # placed ahead of the build, and a second-seat read of an attended brief.
    "docs/agent/support/CHAIN_METHOD.md",
)
RULE_HEADER_WARN_BYTES = 1024
RULE_HEADER_MAX_BYTES = 2048
# The kernel is a different animal from a doc-local header and gets its own cap.
# The donor learned this the hard way: one shared cap forced correct rules to be
# compressed to fit, and the compression broke four of them (donor 396d7f2).
KERNEL_HEADER_WARN_BYTES = 2560
KERNEL_HEADER_MAX_BYTES = 3072
KERNEL_HEADER_FILE = "CLAUDE.md"
RULE_START = "<!-- RULES -->"
RULE_END = "<!-- /RULES -->"
RULE_HEADING = "## Must_Read_Header"
# A canonical rule is a plain imperative sentence ending in a period, then the
# tag. No bold, no emoji, and none of MUST/NEVER/ALWAYS: a rule that has to
# shout is a rule that has not been written precisely enough, and the shouting
# does not survive being quoted somewhere else.
RULE_STYLE_RE = re.compile(r"^Rule: \S.*\. \[A3: pass\]$")
RULE_DUTY_RE = re.compile(r"^Rule: (.+) \[A3: pass\]$")
RULE_EMOJI_RE = re.compile("[☀-➿️\U0001f000-\U0001faff]")
RULE_FORBIDDEN = {
    "AGENTS.md",  # generated mirror of CLAUDE.md, not a second surface
    "docs/agent/bugs/INDEX.md",
    "docs/agent/facts/INDEX.md",
}

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


# The owner's list, ported from SMR-BugFixPack @ 2ec1c62 (its check_checklist)
# when docs/DECISIONS_OWED.md became docs/PLAYTEST_CHECKLIST.md (owner,
# 2026-09-17: same name and rules as the fix pack's list). Two adaptations:
# ids are `OI-<n>`, never the fix pack's `ck<n>`, so the two lists cannot
# collide; and the 30-day age exempts a heading ending ` · launch` (owner,
# 2026-09-18), because this list holds launch obligations and launch is
# unscheduled.
#
# The FORMAT is the gate's measurable half: an item is a `### OI-<n> · opened
# <date>[ · launch]` heading, one ask line (Decide: a question; Run: "When ..."),
# at most six bullet lines, and a `Home:` line naming existing pull-only paths.
# Nothing else may sit in a section, so a ruling, a history or an agent note has
# no shape to take. AGE is by the opened date, never by last edit. The opened
# date is pinned to the date the id first entered git in this list (under either
# name), so re-dating, or deleting and re-adding an id, cannot reset the clock.
CHECKLIST_REL = "docs/PLAYTEST_CHECKLIST.md"
CHECKLIST_HISTORY = ("docs/PLAYTEST_CHECKLIST.md", "docs/DECISIONS_OWED.md")
CHECKLIST_MAX_LINES = 600
CHECKLIST_MAX_WIDTH = 120
CHECKLIST_MAX_BULLET_LINES = 6
CHECKLIST_MAX_AGE_DAYS = 30
CHECKLIST_SECTIONS = ("## Must_Read_Header", "## Decide", "## Run")
CHECKLIST_ITEM_RE = re.compile(
    r"^### (OI-(\d+)) · opened (\d{4}-\d{2}-\d{2})( · launch)?$")
CHECKLIST_ID_RE = re.compile(r"\bOI-(\d+)\b")
CHECKLIST_HOME_RE = re.compile(r"^Home: (`[^`]+`)(, `[^`]+`)*$")
CHECKLIST_HOME_ROOTS = ("docs/agent/", "docs/archive/")


def checklist_first_stamps():
    """-> {id number: date string} from the first commit that added a line naming it."""
    try:
        log = subprocess.check_output(
            ["git", "log", "--reverse", "--format=format:@%ad", "--date=short",
             "-p", "--"] + list(CHECKLIST_HISTORY),
            cwd=REPO, stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError):
        return None
    first, date = {}, None
    for line in log.decode("utf-8", "replace").split("\n"):
        if line.startswith("@") and re.fullmatch(r"@\d{4}-\d{2}-\d{2}", line):
            date = line[1:]
        elif line.startswith("+") and not line.startswith("+++") and date:
            for m in CHECKLIST_ID_RE.finditer(line):
                first.setdefault(int(m.group(1)), date)
    return first


def checklist_shape(lines, today, first_stamps):
    """-> list of violations of the list's entrance-gate format and age."""
    import datetime
    bad = []
    if len(lines) > CHECKLIST_MAX_LINES:
        bad.append("%d lines, cap %d" % (len(lines), CHECKLIST_MAX_LINES))
    section, in_rules, item = None, False, None
    seen = set()

    def close(item):
        if item is None:
            return
        n, cid, body = item
        if len(body) < 2 or not CHECKLIST_HOME_RE.match(body[-1]):
            bad.append("%s (line %d) must end with a `Home:` line of backticked paths" % (cid, n))
        else:
            for path in re.findall(r"`([^`]+)`", body[-1]):
                if not path.startswith(CHECKLIST_HOME_ROOTS):
                    bad.append("%s home %s is not a pull-only path" % (cid, path))
                elif not os.path.exists(os.path.join(REPO, path)):
                    bad.append("%s home %s does not exist" % (cid, path))
        ask = body[0] if body else ""
        if section == "## Decide" and not (ask and not ask.startswith("- ") and ask.endswith("?")):
            bad.append("%s (line %d): a Decide item's first line is the question, ending in ?" % (cid, n))
        if section == "## Run" and not ask.startswith("When "):
            bad.append("%s (line %d): a Run item's first line starts with \"When \"" % (cid, n))
        bullets = body[1:-1]
        if len(bullets) > CHECKLIST_MAX_BULLET_LINES:
            bad.append("%s (line %d) has %d bullet lines, cap %d"
                       % (cid, n, len(bullets), CHECKLIST_MAX_BULLET_LINES))
        for b in bullets:
            if not (b.startswith("- ") or b.startswith("  ")):
                bad.append("%s (line %d): between the ask and Home only bullets may sit" % (cid, n))
                break

    for n, line in enumerate(lines, 1):
        if line == RULE_START:
            in_rules = True
            continue
        if line == RULE_END:
            in_rules = False
            continue
        if in_rules:
            continue
        if len(line) > CHECKLIST_MAX_WIDTH:
            bad.append("line %d is %d characters, cap %d" % (n, len(line), CHECKLIST_MAX_WIDTH))
        if "<!--" in line or "<details" in line.lower():
            bad.append("line %d hides text in a comment or <details>" % n)
        if line.startswith("## "):
            close(item)
            item = None
            section = line.rstrip()
            if section not in CHECKLIST_SECTIONS:
                bad.append("line %d: section %r is not one of %s"
                           % (n, section, ", ".join(CHECKLIST_SECTIONS)))
            continue
        if line.startswith("#") and section in ("## Decide", "## Run"):
            close(item)
            item = None
            m = CHECKLIST_ITEM_RE.match(line)
            if not m:
                bad.append("line %d: an item heading is `### OI-<n> · opened YYYY-MM-DD`, "
                           "optionally ending ` · launch`" % n)
                continue
            cid, num, stamp, launch = m.group(1), int(m.group(2)), m.group(3), m.group(4)
            if num in seen:
                bad.append("line %d: %s appears twice" % (n, cid))
            seen.add(num)
            opened = datetime.date.fromisoformat(stamp)
            pinned = (first_stamps or {}).get(num)
            if pinned and pinned != stamp:
                bad.append("%s opened date %s differs from %s, the date it entered git with; "
                           "the opened date never changes" % (cid, stamp, pinned))
            elif not pinned and abs((opened - today).days) > 1:
                bad.append("%s is new, so its opened date is today, not %s" % (cid, stamp))
            age = (today - opened).days
            if age >= CHECKLIST_MAX_AGE_DAYS and not launch:
                bad.append("%s is %d days old: purge or archive it (the file's "
                           "Must_Read_Header)" % (cid, age))
            item = (n, cid, [])
            continue
        if section in ("## Decide", "## Run") and line.strip():
            if item is None:
                bad.append("line %d: text outside an item in %s" % (n, section))
            else:
                item[2].append(line)
    close(item)
    return bad


def check_checklist(out):
    import datetime
    path = os.path.join(REPO, *CHECKLIST_REL.split("/"))
    if not os.path.exists(path):
        out.append("CHECKLIST: RED  %s is missing" % CHECKLIST_REL)
        return False
    lines = read(path)
    first = checklist_first_stamps()
    bad = checklist_shape(lines, datetime.date.today(), first)
    if first is None:
        # A pin that cannot read history is a dead gate; say so loudly.
        bad.append("git history unread, so opened dates cannot be pinned")
    if not bad:
        out.append("CHECKLIST: PASS — %d lines, format and %d-day age hold "
                   "(launch obligations exempt from age)"
                   % (len(lines), CHECKLIST_MAX_AGE_DAYS))
        return True
    for b in bad:
        out.append("  RED  " + b)
    out.append("CHECKLIST: RED  %d violation(s); the gate is the file's Must_Read_Header"
               % len(bad))
    return False


# The parked-modules file (owner, 2026-09-18): designed or part-built work the
# owner declared parked, between live work and docs/archive/. Pull-only, read by
# the owner AND agents, and it must not become a journal. Enforcement is PER
# ENTRY, not per document: an entry is a `### <name> · parked <date>` heading
# through the next `### ` heading or EOF, at most 10 lines and 1,024 bytes, the
# five fields in the owner's order, and only `Basic summary:` may continue.
# The Evidence line (owner, 2026-09-18) is PATHS ONLY: at most 8 record paths
# joined by ` · `, its own 400-character cap instead of the 100-column one, and
# it is left out of the 1,024-byte count so paths never squeeze the summary. The
# markup bans exist because every one of them packs mass information into a
# line the caps count as one (a table row, a list, a comment, a <details>).
# The prose above the first entry is outside the entry checks but inside the
# HTML and invisible-character checks. Legs: tools/rule_headers_selftest.py.
PARKED_REL = "docs/PARKED_MODULES.md"
PARKED_MAX_LINES = 10
PARKED_MAX_WIDTH = 100
PARKED_MAX_BYTES = 1024          # every entry line except Evidence
PARKED_EVIDENCE_MAX_WIDTH = 400  # the Evidence line, whole
PARKED_EVIDENCE_MAX_PATHS = 8
PARKED_HEAD_RE = re.compile(r"^### (.+) · parked (\d{4}-\d{2}-\d{2})$")
PARKED_FIELDS = ("What:", "Scope:", "Revives by:", "Evidence:", "Basic summary:")
PARKED_SCOPE_RE = re.compile(r"^Scope: (full module|part of \S.*) \(D\d+\)$")
PARKED_EVIDENCE_ROOTS = ("docs/agent/bugs/", "docs/agent/reports/",
                         "docs/agent/facts/", "docs/agent/prompts/")
# A path is path characters and nothing else: no space, backtick, bracket or
# parenthesis can sit in one, so a word or a note after a path fails here.
PARKED_EVIDENCE_PATH_RE = re.compile(
    r"^docs/agent/(bugs|reports|facts|prompts)/[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$")
# Inline code renders its content literally, so HTML inside a closed code span
# hides nothing; spans are stripped per line before the HTML test (a span left
# open across lines is NOT stripped, so it is tested — the strict side).
PARKED_CODE_SPAN_RE = re.compile(r"`[^`\n]*`")
PARKED_HTML_RE = re.compile(r"<!--|</?[A-Za-z][A-Za-z0-9-]*(?=[\s/>]|$)")
PARKED_INVISIBLE_RE = re.compile(
    "[\u00ad\u180e\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]")
PARKED_MARKUP = (
    (re.compile(r"^\s*(```|~~~)"), "a code fence"),
    (re.compile(r"^\s*\|"), "a table row"),
    (re.compile(r"^\s*>"), "a blockquote"),
    (re.compile(r"^\s*([-*+]|\d+[.)])(\s|$)"), "a list bullet"),
    (re.compile(r"\[\^"), "a footnote"),
    (re.compile(r"^\s*#"), "a sub-heading"),
    (re.compile(r"^\s*(={2,}|-{3,}|\*{3,}|_{3,})\s*$"), "a heading underline or rule"),
)


def parked_shape(text, today, repo):
    """-> list of violations of the parked-modules entry gate."""
    import datetime
    bad = []
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()                                   # the file's final newline

    for n, line in enumerate(lines, 1):
        if PARKED_INVISIBLE_RE.search(line):
            bad.append("line %d carries an invisible or zero-width character" % n)
        if line in (RULE_START, RULE_END):
            continue                                  # the header's own markers
        if PARKED_HTML_RE.search(PARKED_CODE_SPAN_RE.sub("", line)):
            bad.append("line %d carries HTML (a comment, <details>, <br> or a tag)" % n)

    heads = [i for i, line in enumerate(lines) if line.startswith("### ")]
    for k, start in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        span = lines[start:end]
        trailing = 0
        while span and not span[-1].strip():
            span.pop()
            trailing += 1
        last = k + 1 == len(heads)
        n0 = start + 1
        m = PARKED_HEAD_RE.match(span[0])
        name = m.group(1) if m else "line %d" % n0
        if not m:
            bad.append("line %d: an entry heading is `### <name> · parked YYYY-MM-DD`" % n0)
        else:
            try:
                stamp = datetime.date.fromisoformat(m.group(2))
            except ValueError:
                stamp = None
                bad.append("%s: %s is not a real date" % (name, m.group(2)))
            if stamp and stamp > today:
                bad.append("%s: parked date %s is in the future" % (name, m.group(2)))
        if not last and trailing != 1:
            bad.append("%s: entries are separated by exactly one blank line, found %d"
                       % (name, trailing))
        if last and trailing:
            bad.append("%s: blank line inside the entry (after its last line)" % name)
        if len(span) > PARKED_MAX_LINES:
            bad.append("%s: %d lines, cap %d (heading included)"
                       % (name, len(span), PARKED_MAX_LINES))
        size = len("\n".join(line for line in span
                              if not line.startswith("Evidence: ")).encode("utf-8"))
        if size > PARKED_MAX_BYTES:
            bad.append("%s: %d bytes without its Evidence line, cap %d"
                       % (name, size, PARKED_MAX_BYTES))
        seen = []
        for i, line in enumerate(span):
            n = n0 + i
            cap = (PARKED_EVIDENCE_MAX_WIDTH if line.startswith("Evidence: ")
                   else PARKED_MAX_WIDTH)
            if len(line) > cap:
                bad.append("line %d is %d characters, cap %d" % (n, len(line), cap))
            if i == 0:
                continue
            if not line.strip():
                bad.append("line %d: blank line inside an entry" % n)
                continue
            for pattern, what in PARKED_MARKUP:
                if pattern.search(line):
                    bad.append("line %d: %s inside an entry" % (n, what))
            field = next((f for f in PARKED_FIELDS if line.startswith(f + " ")
                          or line == f), None)
            if field:
                seen.append(field)
                value = line[len(field):].strip()
                if not value:
                    bad.append("line %d: %s is empty" % (n, field))
                elif field == "Scope:" and not PARKED_SCOPE_RE.match(line):
                    bad.append("line %d: Scope is `full module (Dxx)` or "
                               "`part of <module> (Dxx)`" % n)
                elif field == "Evidence:":
                    parts = line[len("Evidence: "):].split(" · ")
                    if len(parts) > PARKED_EVIDENCE_MAX_PATHS:
                        bad.append("line %d: %d evidence paths, cap %d"
                                   % (n, len(parts), PARKED_EVIDENCE_MAX_PATHS))
                    for path in parts:
                        if (not PARKED_EVIDENCE_PATH_RE.match(path)
                                or posixpath.normpath(path) != path
                                or not path.startswith(PARKED_EVIDENCE_ROOTS)):
                            bad.append("line %d: evidence %r is not a bare path under %s; "
                                       "Evidence holds paths joined by ` · ` and nothing else"
                                       % (n, path, ", ".join(PARKED_EVIDENCE_ROOTS)))
                        elif not os.path.isfile(os.path.join(repo, *path.split("/"))):
                            bad.append("line %d: evidence %s does not exist" % (n, path))
            elif "Basic summary:" not in seen:
                bad.append("line %d: only a field line or a `Basic summary:` "
                           "continuation may follow the heading" % n)
        if tuple(seen) != PARKED_FIELDS:
            bad.append("%s: fields must be %s, once each, in that order; found %s"
                       % (name, ", ".join(PARKED_FIELDS), ", ".join(seen) or "none"))
    return bad


def check_parked(out):
    import datetime
    path = os.path.join(REPO, *PARKED_REL.split("/"))
    if not os.path.exists(path):
        out.append("PARKED: RED  %s is missing" % PARKED_REL)
        return False
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read().replace("\r\n", "\n").replace("\r", "\n")
    bad = parked_shape(text, datetime.date.today(), REPO)
    entries = sum(1 for line in text.split("\n") if line.startswith("### "))
    if not bad:
        out.append("PARKED: PASS — %d entr%s, each within %d lines / %d bytes / %d columns "
                   "(Evidence: paths only, %d columns, %d paths)"
                   % (entries, "y" if entries == 1 else "ies", PARKED_MAX_LINES,
                      PARKED_MAX_BYTES, PARKED_MAX_WIDTH, PARKED_EVIDENCE_MAX_WIDTH,
                      PARKED_EVIDENCE_MAX_PATHS))
        return True
    for b in bad:
        out.append("  RED  " + b)
    out.append("PARKED: RED  %d violation(s); the gate is the file's Must_Read_Header"
               % len(bad))
    return False


def check_state(out):
    """STATE.md's byte budget (checklist 42); the stub half is N/A here."""
    red, warns = [], []
    if not os.path.exists(STATE):
        red.append("docs/agent/STATE.md is missing — restore the pull-only status file")
        n_state = None
    else:
        with open(STATE, "rb") as f:
            raw = f.read()
        n_state = len(raw)
        if n_state > STATE_MAX_BYTES:
            red.append("STATE.md is %d bytes, hard cap is %d — run "
                       "agent/prompts/perma/STATE_EVICTION.md; history belongs in "
                       "archive/SESSION_LOG.md" % (n_state, STATE_MAX_BYTES))
        elif n_state > STATE_WARN_BYTES:
            warns.append("STATE.md is %d bytes, warn threshold is %d — copy "
                         "this line VERBATIM into the owner report; the owner "
                         "fires agent/prompts/perma/STATE_EVICTION.md"
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


# `git rev-parse --local-env-vars` (git 2.x): the variables that pin a git
# process to ONE repository. A hook inherits some of them from the commit that
# runs it, so any git call aimed at ANOTHER repo must drop them (testkit_tree).
GIT_LOCAL_ENV = frozenset((
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_COUNT", "GIT_OBJECT_DIRECTORY", "GIT_DIR", "GIT_WORK_TREE",
    "GIT_IMPLICIT_WORK_TREE", "GIT_GRAFT_FILE", "GIT_INDEX_FILE",
    "GIT_NO_REPLACE_OBJECTS", "GIT_REPLACE_REF_BASE", "GIT_PREFIX",
    "GIT_SHALLOW_FILE", "GIT_COMMON_DIR"))


def testkit_tree(out):
    """REPORT-ONLY (owner GO, 2026-08-04): a dirty TestKit working tree is how
    a true, verified record sat stranded unseen for a day — no gate checked
    that repo. This says so on every run; it deliberately does NOT block, so
    TestKit work-in-progress never jams a pack commit. A reported line is
    routed or committed, never `git restore`d (uncommitted work has no reflog).

    Re-synced 2026-09-18 from SMR-BugFixPack @ 558ad51 (and the 09-09 WARN
    before it). The dated history below is the donor's; the hook, the kit and
    the pathspec-commit rule are the same in this repo, so the defect was too.

    ⚠️ Two kinds of "not checked", and they are NOT the same (2026-09-09).
    No repo at all is *not applicable* — the kit is local-only by design, so a
    fresh clone has none, and that line is quiet on purpose. But once `.git`
    exists, a failure to run means the check produced **no information**, and
    the docstring's own promise ("says so on every run") went unmet. That path
    now also emits a WARN line, because a run that says NOTHING about the kit
    tree must not read like a run that found it clean — `not checked` is one
    word away from `clean` in a 17-line report whose summary still says GREEN.
    Seen live 2026-09-09: `not checked (git exited 128)` inside an otherwise
    green run, on the eve of link 07, whose entire subject is that repo — then
    blamed on "a transient git lock in the kit's tree".

    ⛔ RE-DIAGNOSED 2026-09-10 — it was not a lock, it was THE HOOK. Git exports
    `GIT_INDEX_FILE` to a pre-commit hook, and the `git commit -F msg -- <paths>`
    form the shared index requires sets it to the ABSOLUTE path of
    this repo's temporary index (`.git/next-index-<pid>.lock`). A child `git -C
    <kit>` still obeys it, reads blobs the kit's object store does not hold, and
    dies `fatal: unable to read <sha>` / 128 — on EVERY pathspec commit, while a
    standalone run reads clean (vanillahunt 03 hit it on all its commits).
    Reproduced in a throwaway repo: bare commit (relative `.git/index`, which
    under -C lands on the kit's OWN index by luck) exit 0, pathspec commit 128,
    same hook with `GIT_LOCAL_ENV` stripped 0. A relative temporary index would
    be worse — the kit reads a missing index and reports every file DELETED, a
    false dirty. Hence the stripped env below. Still report-only, still never a
    block — the owner's 2026-08-04 GO is untouched."""
    if not os.path.isdir(os.path.join(TESTKIT, ".git")):
        out.append("TESTKIT TREE: not checked (no repo at %s)" % TESTKIT)
        return True

    def did_not_run(why):
        out.append("TESTKIT TREE: not checked (%s) — the repo EXISTS and the "
                   "check did not run, so this run says nothing about the kit "
                   "tree" % why)
        out.append("  WARN kit-tree state is UNKNOWN on this run — re-run "
                   "doccheck before trusting a clean kit tree")
        return True

    env = {k: v for k, v in os.environ.items() if k not in GIT_LOCAL_ENV}
    try:
        res = subprocess.run(["git", "-C", TESTKIT, "status", "--porcelain"],
                             capture_output=True, text=True, timeout=30,
                             env=env)
    except OSError as exc:
        return did_not_run(exc)
    if res.returncode != 0:
        return did_not_run("git exited %d" % res.returncode)
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


def scratch_report(out):
    """REPORT-ONLY, same standing as testkit_tree() — never gates. Ported from
    the fix pack (owner decision, 2026-09-21, same day it landed there):
    `scratch/` is the git-ignored home for agent/subagent working files, built
    because loose working files kept landing in the repo's PARENT folder
    instead. Nothing swept that folder and nothing listed it; these two lines
    are the listing.
    """
    if os.path.isdir(SCRATCH):
        names = [n for n in os.listdir(SCRATCH)
                 if n != "README.md" and os.path.isfile(os.path.join(SCRATCH, n))]
    else:
        names = []
    if not names:
        out.append("SCRATCH: empty")
    else:
        oldest = min(os.path.getmtime(os.path.join(SCRATCH, n)) for n in names)
        age_days = int((time.time() - oldest) // 86400)
        out.append("SCRATCH: %d file(s), oldest is %d day(s) old"
                   % (len(names), age_days))

    # The mess this folder replaces landed one level up, not inside the repo —
    # so the second half of the report looks at REPO's own parent folder.
    parent = os.path.dirname(REPO)
    try:
        loose = sorted(n for n in os.listdir(parent)
                       if os.path.isfile(os.path.join(parent, n)))
    except OSError as exc:
        out.append("PARENT FILES (%s): not checked (%s)" % (parent, exc))
        return True
    if not loose:
        out.append("PARENT FILES (%s): none" % parent)
    else:
        shown = ", ".join(loose[:10])
        more = "" if len(loose) <= 10 else " (+%d more)" % (len(loose) - 10)
        out.append("PARENT FILES (%s): %d loose file(s) — %s%s"
                   % (parent, len(loose), shown, more))
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
    # ⚖️ EMPTIED 2026-09-17 by owner ruling: both rules named Opt_NoHomeless, which
    # no longer ships (DEAD on 1.1.0 — it reads the renamed `exclusive_trait`). With it
    # gone, no two shipping modules wrap the same symbol: CohortHousing left with it, and
    # ResidencyControl now wraps the global ChooseDome alone. The retired pair is kept
    # here verbatim because restoring either module must restore its rule with it:
    #
    #   CohortHousing before NoHomeless — both post-wrap Colonist:FindEmigrationDome
    #     (Opt_CohortHousing.lua:168, Opt_NoHomeless.lua:449); NoHomeless was the OUTER
    #     wrapper as shipped, so its flagged-dome veto had the last word over
    #     CohortHousing's cross-dome redirect.
    #   ResidencyControl before NoHomeless — both pre-filter the global ChooseDome
    #     through SetGlobal (Opt_ResidencyControl.lua:228, Opt_NoHomeless.lua:906);
    #     NoHomeless was OUTER, so arrivals were screened for flagged domes before
    #     ResidencyControl screened for closed ones.
    #
    # Code: local/retired-modules/README.md, or `git show cc846e4:Code/<file>`.
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
    # ⛔ THE EXCEPT HERE IS NARROW ON PURPOSE (2026-09-17, donor @ ac4e4d3's
    # method note 4). It used to be a bare `except Exception` whose failure path
    # printed "not checked" and returned True — i.e. GREEN. The donor shipped a
    # gate DEAD exactly that way: a NameError fell into a broad except, rendered
    # as a benign skip, and would have skipped silently forever. A missing or
    # unimportable tool is a real condition and still passes; a coding error
    # inside the detector now RAISES, loudly, and the pre-commit hook blocks.
    try:
        import harvest_wrap_targets as hwt
    except ImportError as exc:
        out.append("WRAP CHECK: not checked (%s)" % exc)
        return True
    violations, allowlisted = hwt.check()
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


# ---------------------------------------------------------------------------
# AGENTS.md — the Codex byte copy of CLAUDE.md.
#
# Carried from SMR-BugFixPack 2026-09-17. Two vendors read this
# tree and only one of them reads CLAUDE.md, so the entry file is mirrored
# rather than forked: a fork is a second set of house rules that drifts in
# silence. It is GENERATED — edit CLAUDE.md and run --regen.

CLAUDE_MD = os.path.join(REPO, "CLAUDE.md")
AGENTS_MD = os.path.join(REPO, "AGENTS.md")

REGEN_CURE = ("  → regenerate with `python tools/doccheck.py --regen` (never by "
              "hand-editing the generated file)")

# ---------------------------------------------------------------------------
# Skills, and the Codex mirror.
#
# `.claude/` is otherwise local scratch and gitignored; `.claude/skills/` is
# re-included by .gitignore because it is project material, not scratch.
# Codex reads `.agents/`, so the same bodies are mirrored there byte-for-byte:
# a fork would be two vendors working this tree under different instructions.
# Carried from SMR-BugFixPack 2026-09-17.
#
# Size is REPORTED, not gated — a skill body is PULL (loaded only on invoke),
# and this file's PUSH_SET comment says the budget belongs on the push set "as
# one number, and on nothing else". The donor tore its per-skill caps down for
# exactly that reason (its owner ruling 2026-09-14); this repo never had them
# and does not re-introduce them on an agent's judgement.

SKILLS_DIR = os.path.join(REPO, ".claude", "skills")
CODEX_SKILLS_DIR = os.path.join(REPO, ".agents", "skills")

# A user-level skill loads in every project for Claude but is invisible to
# Codex, which reads only .agents/skills/ in-repo. Each name below is mirrored
# from the owner's user-level copy, which stays canonical; the in-repo copy is
# generated, exactly as AGENTS.md is a byte copy of CLAUDE.md. Ported from the
# donor 2026-09-26 with the rule-placement skill it carries.
USER_SKILLS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "skills")
IMPORTED_SKILLS = ("rule-placement",)


def imported_skill_src(name):
    """-> the user-level canonical path for an imported skill, or None."""
    path = os.path.join(USER_SKILLS_DIR, name, "SKILL.md")
    return path if os.path.isfile(path) else None


def skill_names():
    """-> sorted skill folder names that actually hold a SKILL.md."""
    if not os.path.isdir(SKILLS_DIR):
        return []
    return sorted(n for n in os.listdir(SKILLS_DIR)
                  if os.path.isfile(os.path.join(SKILLS_DIR, n, "SKILL.md")))


def regen_skills():
    """Mirror every skill byte-for-byte into .agents/skills/ for Codex."""
    wrote = []
    for name in skill_names():
        dst_dir = os.path.join(CODEX_SKILLS_DIR, name)
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        with open(os.path.join(SKILLS_DIR, name, "SKILL.md"), "rb") as fh:
            data = fh.read()
        dst = os.path.join(dst_dir, "SKILL.md")
        if not os.path.exists(dst) or open(dst, "rb").read() != data:
            with open(dst, "wb") as fh:
                fh.write(data)
            wrote.append(name)
    for name in IMPORTED_SKILLS:
        src = imported_skill_src(name)
        if not src:
            continue
        dst_dir = os.path.join(CODEX_SKILLS_DIR, name)
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        with open(src, "rb") as fh:
            data = fh.read()
        dst = os.path.join(dst_dir, "SKILL.md")
        if not os.path.exists(dst) or open(dst, "rb").read() != data:
            with open(dst, "wb") as fh:
                fh.write(data)
            wrote.append(name)
    return wrote


def check_skills(out):
    """Both vendors' copies identical; body sizes reported, never gated."""
    names = skill_names()
    if not names:
        out.append("SKILLS: none")
        return True
    ok, rows, total = True, [], 0
    for name in names:
        src = os.path.join(SKILLS_DIR, name, "SKILL.md")
        dst = os.path.join(CODEX_SKILLS_DIR, name, "SKILL.md")
        total += len(lf_bytes(src))
        if not os.path.exists(dst):
            out.append("SKILLS: RED  .agents/skills/%s/SKILL.md is missing — Codex "
                       "cannot see this skill" % name)
            out.append(REGEN_CURE)
            ok = False
        else:
            with open(src, "rb") as a, open(dst, "rb") as b:
                if a.read() != b.read():
                    out.append("SKILLS: RED  %s differs between .claude/skills/ and "
                               ".agents/skills/ — the two vendors would read "
                               "different instructions" % name)
                    out.append(REGEN_CURE)
                    ok = False
        rows.append("    %-24s %5d B" % (name, len(lf_bytes(src))))
    imported = 0
    for name in IMPORTED_SKILLS:
        dst = os.path.join(CODEX_SKILLS_DIR, name, "SKILL.md")
        if not os.path.exists(dst):
            if not imported_skill_src(name):
                continue     # neither copy here: not this tree's concern
            out.append("SKILLS: RED  .agents/skills/%s/SKILL.md is missing — this "
                       "user-level skill reaches Codex only through the in-repo copy"
                       % name)
            out.append(REGEN_CURE)
            ok = False
            continue
        imported += 1
        size = len(lf_bytes(dst))
        src = imported_skill_src(name)
        if not src:
            rows.append("    %-24s %5d B  imported, canonical copy not on this machine"
                        % (name, size))
        else:
            with open(src, "rb") as ua, open(dst, "rb") as ub:
                if ua.read() != ub.read():
                    out.append("SKILLS: RED  %s differs from the owner's user-level "
                               "copy, which is canonical" % name)
                    out.append(REGEN_CURE)
                    ok = False
            rows.append("    %-24s %5d B  imported from ~/.claude/skills/" % (name, size))
        total += size
    out.append("SKILLS: %d skill(s), %d B of bodies, mirrored to .agents/skills/"
               % (len(names) + imported, total))
    out.extend(rows)
    return ok


# ---------------------------------------------------------------------------
# The prompt map.
#
# Carried from SMR-BugFixPack 2026-09-17. Its owner ruled (its checklist 174)
# that the map lists LIVE prompts only: a row that outlives its file is how a
# next session fires spent work. The donor's `ledger-exception` class and its
# migration-allowance machinery are NOT carried — this repo has no such ledger
# and no migration debt, and a class nothing can legally declare is a trap.

PROMPT_MAP_DEFAULT_CLASSES = {
    "perma": "prompt",
    "root": "prompt",
    "chain": "live",
}


def prompt_map_rows(mapfile):
    """Parse map paths and declared classes, including grouped first cells."""
    rows = {"perma": {}, "root": {}, "chain": {}}
    struck, malformed = [], []
    table = None
    for lineno, line in enumerate(read(mapfile), 1):
        if line.startswith("## "):
            table = ("perma" if "perma" in line
                     else "root" if "Root" in line
                     else "chain" if "Chain folders" in line else None)
            continue
        if table is None or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < 2:
            continue
        name_re = r"`([^`]+/)`" if table == "chain" else r"`([^`]+\.md)`"
        names = re.findall(name_re, cells[0])
        if not names:
            continue
        if "~~" in cells[0]:
            struck.append((table, cells[0], lineno))
            continue
        classes = re.findall(r"`([^`]+)`", cells[1])
        if len(classes) != 1:
            malformed.append("line %d %s row needs exactly one declared class"
                             % (lineno, table))
            continue
        declared = classes[0]
        for raw in names:
            name = raw[:-1] if table == "chain" else raw
            if name in rows[table]:
                malformed.append("line %d repeats %s/%s" % (lineno, table, name))
            else:
                rows[table][name] = declared
    return rows, struck, malformed


def check_prompt_map(out):
    """Gate prompt paths, chain directories, and declared classifications."""
    prompts = os.path.join(DOCS, "agent", "prompts")
    perma = os.path.join(prompts, "perma")
    mapfile = os.path.join(prompts, "README.md")
    if not os.path.exists(mapfile):
        out.append("PROMPT MAP: RED  docs/agent/prompts/README.md is missing "
                   "— the one-offs have no map")
        return False
    if not os.path.isdir(perma):
        out.append("PROMPT MAP: RED  docs/agent/prompts/perma/ is missing")
        return False
    rows, struck, malformed = prompt_map_rows(mapfile)
    disk = {
        "perma": {f for f in os.listdir(perma) if f.endswith(".md")},
        "root": {f for f in os.listdir(prompts)
                 if f.endswith(".md") and f != "README.md"},
        # Descendants are deliberately not enumerated: mapped LIVE chains may
        # contain their README and evidence. The map itself is the root README
        # excluded above. Neither exception licenses a supporting root file.
        "chain": {f for f in os.listdir(prompts)
                  if f != "perma" and os.path.isdir(os.path.join(prompts, f))},
    }
    red = ["  RED  prompts/README.md %s" % finding for finding in malformed]
    for cell in struck:
        red.append("  RED  prompts/README.md keeps a struck-through row (%s) — a "
                   "fired prompt leaves the map entirely" % cell[1])
    where = {"perma": "perma/", "root": "", "chain": ""}
    noun = {"perma": "file", "root": "file", "chain": "directory"}
    for table in ("perma", "root", "chain"):
        mapped = set(rows[table])
        suffix = "/" if table == "chain" else ""
        for name in sorted(mapped - disk[table]):
            red.append("  RED  prompts/README.md has a row for %s%s%s and the %s is "
                       "not there — delete the row in the commit that consumes it"
                       % (where[table], name, suffix, noun[table]))
        for name in sorted(disk[table] - mapped):
            red.append("  RED  docs/agent/prompts/%s%s%s exists and the map does not "
                       "list it — every prompt or chain is reachable from the map"
                       % (where[table], name, suffix))
        for name, declared in sorted(rows[table].items()):
            expected = PROMPT_MAP_DEFAULT_CLASSES[table]
            if declared != expected:
                red.append("  RED  prompts/README.md declares %s%s as `%s`; exact "
                           "path requires `%s`"
                           % (where[table], name, declared, expected))
    if red:
        out.extend(red)
        out.append("PROMPT MAP: RED  %d finding(s)" % len(red))
        return False
    out.append("PROMPT MAP: PASS — %d perma + %d one-off + %d chain row(s) agree "
               "with disk in both directions; declared classes hold; no tombstones"
               % (len(rows["perma"]), len(rows["root"]), len(rows["chain"])))
    return True


def lf_bytes(path):
    """Content bytes for budgets and comparisons, independent of CRLF checkout."""
    with open(path, "rb") as fh:
        return fh.read().replace(b"\r\n", b"\n")


def check_agents_mirror(out):
    """AGENTS.md must reproduce CLAUDE.md byte for byte (LF-normalised)."""
    if not os.path.exists(CLAUDE_MD):
        out.append("MIRROR: RED  CLAUDE.md is missing")
        return False
    if not os.path.exists(AGENTS_MD):
        out.append("MIRROR: RED  AGENTS.md is missing — run "
                   "python tools/doccheck.py --regen")
        return False
    want, have = lf_bytes(CLAUDE_MD), lf_bytes(AGENTS_MD)
    if want == have:
        out.append("MIRROR: AGENTS.md reproduces CLAUDE.md byte for byte (%d B)"
                   % len(want))
        return True
    out.append("MIRROR: RED  AGENTS.md has drifted from CLAUDE.md (%d B vs %d B) "
               "— edit CLAUDE.md, then python tools/doccheck.py --regen"
               % (len(have), len(want)))
    return False


# ---------------------------------------------------------------------------
# The push set.
#
# PUSH = the files loaded into EVERY session before it has decided anything.
# They are the only documents where bytes genuinely hurt, because nobody chooses
# to read them and the cost is paid every session, forever. Everything else is
# PULL (read a section on demand, uncapped) or RECORD (written once, read
# rarely, never capped). Report-only; it never gates.

def _memory_project_key(repo):
    r"""Claude keys its per-project memory by the absolute path, lowercased, with
    every non-alphanumeric run replaced by a dash: B:\Dev\SMR\SMR-OptInPack
    becomes b--Dev-SMR-SMR-OptInPack. Case is kept after the drive."""
    drive, rest = os.path.splitdrive(os.path.abspath(repo))
    parts = [q for q in rest.replace("\\", "/").split("/") if q]
    return drive[:1].lower() + "--" + "-".join(parts)


PUSH_SET = [
    ("CLAUDE.md", lambda: CLAUDE_MD),
    ("docs/agent/STATE.md", lambda: STATE),
    # Claude's own memory index: outside the repo, per-machine, and absent for
    # any other vendor — reported when present, never required. The project key
    # is derived from REPO, not spelled, so a tree move carries it: the 2026-09-21
    # move left this reading the old tree's stale copy until that copy was deleted.
    ("MEMORY.md (Claude, outside the repo)",
     lambda: os.environ.get("SMR_MEMORY", os.path.join(
         os.path.expanduser("~"), ".claude", "projects",
         _memory_project_key(REPO), "memory", "MEMORY.md"))),
]
PUSH_BUDGET = 24 * 1024
PUSH_CHARS_PER_TOKEN = 2.17     # measured on the donor's own documents


def push_set_report(out):
    rows, total, missing = [], 0, 0
    for label, resolve in PUSH_SET:
        path = resolve()
        if os.path.exists(path):
            size = len(lf_bytes(path))
            total += size
            rows.append("    %-38s %7d B" % (label, size))
        else:
            missing += 1
            rows.append("    %-38s   absent" % label)
    out.append("PUSH SET: %d B in %d file(s) ~ %dk tokens (budget %d B)%s"
               % (total, len(PUSH_SET) - missing,
                  round(total / PUSH_CHARS_PER_TOKEN / 1000), PUSH_BUDGET,
                  "" if total <= PUSH_BUDGET else "  WARN OVER"))
    out.extend(rows)
    if total > PUSH_BUDGET:
        out.append("    -> every session pays this before it has decided "
                   "anything; evict from the largest, not the easiest "
                   "(agent/prompts/perma/STATE_EVICTION.md)")


# ---------------------------------------------------------------------------
# Durable-fact fingerprints (carried from SMR-BugFixPack 2026-09-17).

ACF = os.environ.get("SMR_ACF", r"A:\SteamLibrary\steamapps\appmanifest_3215050.acf")


def installed_build():
    """-> the installed game's Steam buildid, read from the .acf, or None.

    A build id is VOLATILE-external: it changes without anyone here doing
    anything (the rig auto-updated into 1.1.0 unasked on 2026-09-08). So it is
    always read, never stored — a number pasted into a doc will be wrong.
    """
    try:
        with open(ACF, encoding="utf-8", errors="replace") as fh:
            hit = re.search(r'"buildid"\s+"(\d+)"', fh.read())
        return hit.group(1) if hit else None
    except OSError:
        return None


def emit_fingerprints(out):
    """--emit-fingerprint: route evidence checks by exact build identity.

    Identity alone does not verify a group's claims, scope or dependencies.
    HOLDS is a routing aid; MOVED identifies citations needing a new baseline.
    """
    sf = facts_splitter()
    groups, total = {}, 0
    for fact in sf.load_from_dir()["facts"]:
        total += 1
        pin = str(fact.get("derived_at") or "").strip()
        bare = re.sub(r"\s*\(inferred[^)]*\)", "", pin) or "(none)"
        g = groups.setdefault(bare, {"n": 0, "inferred": 0})
        g["n"] += 1
        g["inferred"] += 1 if "(inferred" in pin else 0

    build = installed_build()
    out.append("")
    out.append("FINGERPRINTS — derived_at across %d facts; installed game build %s"
               % (total, build or "UNREADABLE (%s)" % ACF))

    shas, behind = [], []
    for bare in sorted(groups, key=lambda k: (-groups[k]["n"], k)):
        g = groups[bare]
        note = " (%d inferred)" % g["inferred"] if g["inferred"] else ""
        if bare.startswith("game"):
            hit = re.search(r"\bbuild\s+(\d+)\b", bare)
            if build is None:
                verdict = "cannot check — the .acf is unreadable from here"
            elif hit and hit.group(1) == build:
                verdict = ("HOLDS — build identity matches; routing aid only, "
                           "check claim scope and source dependencies")
            else:
                verdict = ("MOVED — installed is %s, so these line citations "
                           "describe a tree that is not on disk; re-derive "
                           "against B:\\Dev\\SMR\\SMR-Shared\\SMR-SrcArchive (EF-083)" % build)
            out.append("  %-30s %3d fact(s)%s  %s" % (bare, g["n"], note, verdict))
        elif re.match(r"^[0-9a-f]{7,40}$", bare):
            shas.append((bare, g))
        else:
            out.append("  %-30s %3d fact(s)%s  no fingerprint — re-derive before "
                       "relying on it" % (bare, g["n"], note))

    # Repo shas collapse to one row: a dozen "N commits behind" lines is noise,
    # and the only thing a reader does with them is notice none is current.
    # NOTE: these shas are the FIX PACK's (facts are allocated and mirrored from
    # there), so most will not resolve in this clone. That is expected.
    if shas:
        nfacts = sum(g["n"] for _, g in shas)
        ninf = sum(g["inferred"] for _, g in shas)
        for sha, _ in shas:
            try:
                behind.append(int(subprocess.check_output(
                    ["git", "rev-list", "--count", "%s..HEAD" % sha],
                    cwd=REPO, stderr=subprocess.DEVNULL).decode().strip()))
            except (subprocess.CalledProcessError, OSError, ValueError):
                behind.append(-1)
        live = [b for b in behind if b >= 0]
        out.append("  %-30s %3d fact(s)%s  %s"
                   % ("shas (%d distinct)" % len(shas), nfacts,
                      " (%d inferred)" % ninf if ninf else "",
                      "behind HEAD by %d–%d commits — re-check before quoting"
                      % (min(live), max(live)) if live
                      else "none resolve in this clone (fix-pack shas)"))


# ---------------------------------------------------------------------------
# --regen: write every generated file from its source.

def regen(out):
    """Rewrite bugs/INDEX.md, facts/INDEX.md and AGENTS.md from their sources.

    Reads EVERY entry on disk, a peer's uncommitted ones included — check
    `git status docs/agent/` first and commit only your own paths.
    """
    wrote = []
    sb, sf = splitter(), facts_splitter()

    for label, path, lines in (
            ("bugs/INDEX.md", os.path.join(BUGS_DIR, "INDEX.md"),
             sb.render_index(sb.load_from_dir())),
            ("facts/INDEX.md", os.path.join(FACTS_DIR, "INDEX.md"),
             sf.render_index(sf.load_from_dir()))):
        body = ("\n".join(lines) + "\n").encode("utf-8")
        before = lf_bytes(path) if os.path.exists(path) else None
        if before != body:
            with open(path, "wb") as fh:
                fh.write(body)
            wrote.append(label)

    wrote.extend("skill:" + n for n in regen_skills())

    if os.path.exists(CLAUDE_MD):
        want = lf_bytes(CLAUDE_MD)
        if not os.path.exists(AGENTS_MD) or lf_bytes(AGENTS_MD) != want:
            with open(AGENTS_MD, "wb") as fh:
                fh.write(want)
            wrote.append("AGENTS.md")

    out.append("REGEN: %s" % (", ".join(wrote) + " rewritten" if wrote
                              else "nothing to do — every generated file was fresh"))
    # The tool rows are spliced in place, so this reports separately: its prose
    # is hand-authored and only the marked region is generated.
    regen_tools(out)


# ---------------------------------------------------------------------------
# The generated tools catalog (ported from SMR-BugFixPack @ ac4e4d3, where it
# landed 2026-09-17). A hand-kept list of N rows is a list that goes stale; this
# one is regenerated from each script's OWN opening header and reconciled both
# ways against glob(tools/*.py), so a new tool with no row is RED and a row with
# no tool is RED. There is no exempt class.
TOOLS_DIR = os.path.join(REPO, "tools")
TOOLS_README = os.path.join(TOOLS_DIR, "README.md")
TOOLS_BEGIN = ("<!-- GENERATED TOOL ROWS — never hand-edit; regenerate with: "
               "python tools/doccheck.py --regen -->")
TOOLS_END = "<!-- END GENERATED TOOL ROWS -->"

# Declared data, not a filename heuristic. A prefix rule would place the `l*_`
# instruments correctly and `blocking_analysis.py`, `pack_predict.py` and
# `audit_preset_fields.py` nowhere, and would silently reclassify a script on
# rename. Order here is the order the catalog renders in.
TOOL_GROUPS = (
    ("Repo gates, and the falsifiers that keep them honest",
     "The pre-commit hook runs `doccheck.py`; the five `*_selftest.py` are "
     "required BY it, so a gate whose falsifier stops firing is itself RED. A "
     "gate that has only ever been seen passing on a clean tree has not been "
     "tested.",
     ("doccheck.py", "rule_headers_selftest.py", "ck170_selftest.py",
      "counts_selftest.py", "prompt_map_selftest.py",
      "repair_pass_selftest.py")),
    ("Generated-document machinery",
     "The splitters own `bugs/INDEX.md` and `facts/INDEX.md`. ⛔ Never run "
     "either with `--write`: that re-runs the one-time migration from a "
     "retired pre-split document. `--regen` is the cure for drift.",
     ("split_bugs.py", "split_facts.py")),
    ("Desk instruments — what a module does without launching the game",
     "The L-series. ⛔ A desk PASS is \"desk-verified\", never \"verified\" "
     "(`WORK_PROMPT.md` \"Code-change loop\"): none of these launches the "
     "retail game. Every one is an over-reporter — adjudicate a row by reading "
     "the source line it cites, never by its count.",
     ("l2_reload_sim.py", "l3_save_footprint.py", "l4_player_surfaces.py",
      "l5_containment.py", "l6_promise_map.py", "l6_reachability.py",
      "l7_env_map.py", "l8_hostile_input.py")),
    ("This mod's own code gates",
     "Run by `doccheck` as well as by hand; the allowlists live beside the "
     "detectors, with a source citation per entry (`FIX_POLICY` §2).",
     ("harvest_wrap_targets.py", "parsecheck.py")),
    ("Reading the shipped game by hand",
     "⛔ Cite a line only with the build it was read on, from the archived tree "
     "for that build (`B:\\Dev\\SMR\\SMR-Shared\\SMR-SrcArchive`). The game moved to 1.1.0 on "
     "2026-09-08 and overwrote `ModTools\\Src`.",
     ("flpk_extract.py", "pack_list.py", "audit_preset_fields.py",
      "blocking_analysis.py", "sigcheck.py")),
    ("Cross-repo sync with the fix pack",
     "Fired by `docs/agent/prompts/perma/KNOWLEDGE_SYNC_PASS.md` when the owner "
     "has changed the main pack and wants to know what lands here. ⛔ Read-only "
     "in BOTH repos, and it decides nothing — its declared constants "
     "(`LOCAL_ADAPTATIONS`, the `TOOLS_*` tables, `MIRRORED_DOCS`, `LAST_SYNC`) "
     "are the retired prose port ledger in the "
     "only form that cannot go stale, because the thing that reads them is the "
     "thing that checks them. Its falsifier is required by `doccheck`.",
     ("sync_from_fixpack.py", "sync_from_fixpack_selftest.py")),
    ("Launch",
     "⛔ This mod is NOT PUBLISHED. `upload_preflight.py` FAILS today on the "
     "missing preview art (owner, `PLAYTEST_CHECKLIST.md` OI-12).",
     ("upload_preflight.py", "pack_predict.py")),
)
TOOLS_UNGROUPED = (
    "Ungrouped",
    "These carry no group in `TOOL_GROUPS`. They still render, because the "
    "catalog reconciles against the glob and not against the groups — giving "
    "them a group is tidying, not a fix.",
)


def tool_scripts():
    """Every tools/*.py on disk, by basename. The catalog's row set."""
    return sorted(os.path.basename(p)
                  for p in glob.glob(os.path.join(TOOLS_DIR, "*.py")))


def tool_header_line(name):
    """The script's own opening sentence(s), from its docstring or `#` header.

    Trap: a header's FIRST LINE is usually a fragment ("L6 — promise vs" …), so
    this reads the whole first paragraph and then cuts on sentence boundaries,
    taking a second sentence when the first is too short to route on. Purely
    mechanical: nothing here decides what a tool does, it only copies the claim
    the tool makes about itself.
    """
    with open(os.path.join(TOOLS_DIR, name), encoding="utf-8") as fh:
        lines = fh.read().replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines) and (lines[i].startswith("#!")
                              or lines[i].startswith("# -*-")
                              or not lines[i].strip()):
        i += 1
    para = []
    if i < len(lines) and lines[i].lstrip()[:3] in ('"""', "'''"):
        quote = lines[i].lstrip()[:3]
        for ln in [lines[i].lstrip()[3:]] + lines[i + 1:]:
            if quote in ln:
                para.append(ln.split(quote)[0])
                break
            if not ln.strip():
                break
            para.append(ln)
    elif i < len(lines) and lines[i].lstrip().startswith("#"):
        for ln in lines[i:]:
            if not ln.strip().startswith("#"):
                break
            stripped = ln.strip().lstrip("#").strip()
            if not stripped:
                break
            para.append(stripped)
    text = re.sub(r"\s+", " ", " ".join(x.strip() for x in para)).strip()
    out = ""
    for piece in re.split(r"(?<=[.?!])\s+", text):
        out = (out + " " + piece).strip() if out else piece
        if len(out) >= 45:
            break
    if not out:
        out = "*(no header — give this script an opening docstring)*"
    return out.replace("|", r"\|")


def render_tool_rows():
    """The generated region, marker lines included. Pure function of disk."""
    on_disk = tool_scripts()
    placed, body = set(), []
    for title, blurb, names in TOOL_GROUPS:
        rows = [n for n in names if n in on_disk]
        placed.update(rows)
        if not rows:
            continue
        body += ["", "### %s" % title, "", blurb, "",
                 "| script | what its own header says |", "|---|---|"]
        body += ["| [`%s`](%s) | %s |" % (n, n, tool_header_line(n))
                 for n in rows]
    rest = [n for n in on_disk if n not in placed]
    if rest:
        title, blurb = TOOLS_UNGROUPED
        body += ["", "### %s" % title, "", blurb, "",
                 "| script | what its own header says |", "|---|---|"]
        body += ["| [`%s`](%s) | %s |" % (n, n, tool_header_line(n))
                 for n in rest]
    head = ("*%d scripts, every `tools/*.py` on disk. This block is GENERATED: "
            "a row's text is copied from the script's own header, so a wrong "
            "row is repaired in the script, never here.*" % len(on_disk))
    return [TOOLS_BEGIN, "", head] + body + ["", TOOLS_END]


def _tools_region(lines):
    """(start, end) index of the marker lines, or None if either is missing."""
    try:
        return lines.index(TOOLS_BEGIN), lines.index(TOOLS_END)
    except ValueError:
        return None


def regen_tools(out):
    """Splice fresh rows into tools/README.md; leave every other line alone."""
    if not os.path.exists(TOOLS_README):
        out.append("REGEN: tools/README.md is missing — its PROSE is "
                   "hand-authored, so --regen cannot create it; only its rows "
                   "are generated")
        return
    with open(TOOLS_README, encoding="utf-8") as fh:
        lines = fh.read().replace("\r\n", "\n").split("\n")
    span = _tools_region(lines)
    if span is None:
        out.append("REGEN: tools/README.md has no generated-rows markers — "
                   "left untouched")
        return
    start, end = span
    new = lines[:start] + render_tool_rows() + lines[end + 1:]
    with open(TOOLS_README, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(new))
    out.append("REGEN: wrote tools/README.md's generated tool rows (%d scripts)"
               % len(tool_scripts()))


def check_tools_catalog(out):
    """The catalog lists every tools/*.py, and every row matches its header."""
    on_disk = tool_scripts()
    # The one condition under which there is nothing to check, stated exactly
    # rather than as "no scripts found": this checker IS a tools/*.py, so in any
    # real checkout it is always one of its own rows. This line cannot print in
    # the repo — if it ever does, doccheck is not running from tools/.
    if "doccheck.py" not in on_disk:
        out.append("TOOL CATALOG: not applicable — this checker is not running "
                   "from a tools/ directory (%d script(s) beside it)"
                   % len(on_disk))
        return True
    if not os.path.exists(TOOLS_README):
        out.append("TOOL CATALOG: RED  tools/README.md is missing (%d scripts "
                   "have nowhere to be routed from)" % len(on_disk))
        return False
    with open(TOOLS_README, encoding="utf-8") as fh:
        lines = fh.read().replace("\r\n", "\n").split("\n")
    span = _tools_region(lines)
    if span is None:
        out.append("TOOL CATALOG: RED  tools/README.md is missing one or both "
                   "generated-rows markers; restore them around the tool "
                   "tables, then regenerate:")
        out.append("    %s" % TOOLS_BEGIN)
        out.append("    %s" % TOOLS_END)
        out.append(REGEN_CURE)
        return False
    start, end = span
    have, want = lines[start:end + 1], render_tool_rows()
    if have != want:
        out.append("TOOL CATALOG: RED  the generated rows in tools/README.md "
                   "differ from the tools on disk (%d row-block lines, %d "
                   "regenerated, %d scripts)"
                   % (len(have), len(want), len(on_disk)))
        for n, (a, b) in enumerate(zip(have, want), start + 1):
            if a != b:
                out.append("  RED  first difference at line %d:" % n)
                out.append("    on disk:     %r" % a[:100])
                out.append("    regenerated: %r" % b[:100])
                break
        out.append(REGEN_CURE)
        return False
    declared = [n for _, _, names in TOOL_GROUPS for n in names]
    stale = sorted(set(declared) - set(on_disk))
    ungrouped = sorted(set(on_disk) - set(declared))
    out.append("TOOL CATALOG: %d script(s) on disk, %d row(s) rendered, both "
               "directions reconciled against glob(tools/*.py)"
               % (len(on_disk), len(on_disk)))
    if stale:
        out.append("  note  TOOL_GROUPS names %d script(s) no longer on disk "
                   "(dropped from the rows, harmless): %s"
                   % (len(stale), ", ".join(stale)))
    if ungrouped:
        out.append("  note  %d script(s) rendered under \"Ungrouped\"; giving "
                   "them a group in TOOL_GROUPS is tidying, not a fix: %s"
                   % (len(ungrouped), ", ".join(ungrouped)))
    return True


# ---------------------------------------------------------------------------
# Line endings (ported from SMR-BugFixPack @ ac4e4d3; the whole-CRLF listing and
# the --fix-eol-then-check flow re-synced to the donor 2026-09-18, once this tree
# went LF in a37d017: `* text=auto eol=lf`, local core.autocrlf=false).
#
# `.gitattributes` governs what a CHECKOUT writes; it does not stop a tool from
# writing CRLF into the working tree afterwards. A MIXED file is the hazard: git
# normalises both forms to one blob and shows nothing, while a reader that
# splits on the file's dominant ending silently DROPS the minority lines. The
# donor lost a script's `### ` headers exactly that way, and its checker stayed
# GREEN throughout.
#
# A whole-CRLF file is listed but not RED: every line agrees, so no reader
# splits it wrong — yet the next LF write into it makes it mixed.
_EOL_CONTROL = (
    "i/lf    w/mixed attr/text=auto eol=lf \tdocs/x.md\n"
    "i/lf    w/crlf  attr/text=auto eol=lf \tdocs/y.md\n"
    "i/-text w/-text attr/-text            \tdocs/archive/logs/z.log.raw\n"
    "i/lf    w/lf    attr/text eol=lf      \tdocs/agent/STATE.md\n"
)


def _eol_parse(text):
    """Return [(index_kind, worktree_kind, attr, path)] for `git ls-files --eol`."""
    rows = []
    for line in text.splitlines():
        head, tab, path = line.partition("\t")
        if not tab:
            continue
        parts = head.split()
        i = next((p[2:] for p in parts if p.startswith("i/")), "")
        w = next((p[2:] for p in parts if p.startswith("w/")), "")
        attr = head.split("attr/", 1)[1].strip() if "attr/" in head else ""
        rows.append((i, w, attr, path.replace("\\", "/")))
    return rows


def _eol_is_raw_evidence(rel):
    """Archived game logs are raw output whose mixed endings ARE the record: the
    game writes them that way and `docs/archive/` is append-only. Never listed,
    never rewritten."""
    return rel.startswith("docs/archive/") and rel.endswith((".log", ".raw"))


def _eol_counts(rel):
    with open(os.path.join(REPO, rel), "rb") as fh:
        data = fh.read()
    crlf = data.count(b"\r\n")
    return crlf, data.count(b"\n") - crlf


def _eol_rows():
    """[(worktree_kind, path)] for every tracked TEXT file that is not raw
    archived evidence, or None if git did not answer."""
    try:
        text = subprocess.check_output(["git", "ls-files", "--eol"], cwd=REPO,
                                       text=True, encoding="utf-8", errors="replace")
    except (OSError, subprocess.CalledProcessError):
        return None
    return [(w, path) for i, w, attr, path in _eol_parse(text)
            if i != "-text" and "-text" not in attr.split()
            and not _eol_is_raw_evidence(path)]


def eol_report(out):
    """RED on a mixed tracked text file, or on a failed parser control."""
    control = [w for _, w, _, _ in _eol_parse(_EOL_CONTROL)]
    if control != ["mixed", "crlf", "-text", "lf"]:
        out.append("EOL: RED  the ls-files --eol parser failed its positive control (%r) — "
                   "this run says nothing about line endings" % (control,))
        return False
    rows = _eol_rows()
    if rows is None:
        out.append("EOL: not checked (git ls-files --eol did not run) — this run says "
                   "nothing about line endings")
        return True
    mixed = sorted(p for w, p in rows if w == "mixed")
    crlf = sorted(p for w, p in rows if w == "crlf")
    if not mixed and not crlf:
        out.append("EOL: PASS — every tracked text file is LF in the working tree")
        return True
    if mixed:
        out.append("EOL: RED  %d tracked file(s) MIXED — a reader that splits on one "
                   "ending drops the other's lines. Cure: `python tools/doccheck.py "
                   "--fix-eol` (git sees no change)" % len(mixed))
        for rel in mixed:
            c, l = _eol_counts(rel)
            out.append("  RED  %-58s crlf=%d lf=%d" % (rel, c, l))
    if crlf:
        out.append("EOL: %d tracked file(s) whole-CRLF in an LF tree — not RED, every "
                   "line agrees; the next LF write makes one mixed. `--fix-eol` converts "
                   "them" % len(crlf))
        for rel in crlf[:10]:
            out.append("  WARN " + rel)
        if len(crlf) > 10:
            out.append("  WARN ... and %d more" % (len(crlf) - 10))
    return not mixed


def eol_fix(paths, out):
    """--fix-eol: convert CRLF to LF in every tracked text file that carries any
    (mixed or whole-CRLF), or only in the PATHs given. The stored blob is already
    LF, so git sees no content change; this only makes the working tree agree."""
    rows = _eol_rows()
    if rows is None:
        out.append("FIX-EOL: git ls-files --eol did not run; nothing rewritten")
        return
    fixable = set(p for w, p in rows if w in ("mixed", "crlf"))
    targets = sorted(fixable) if not paths else [p.replace("\\", "/") for p in paths]
    for rel in targets:
        if rel not in fixable:
            out.append("FIX-EOL: %s has no CRLF to convert, or is binary, -text or an "
                       "archived log; left alone" % rel)
            continue
        c, l = _eol_counts(rel)
        with open(os.path.join(REPO, rel), "rb") as fh:
            data = fh.read()
        with open(os.path.join(REPO, rel), "wb") as fh:
            fh.write(data.replace(b"\r\n", b"\n"))
        out.append("FIX-EOL: %s -> LF (was crlf=%d lf=%d)" % (rel, c, l))
    done = [t for t in targets if t in fixable]
    if not done:
        return
    # A converted file keeps the index's old stat size, so `git status` lists it
    # modified with an empty diff. `git add --renormalize` refreshes that record,
    # but it would also STAGE a peer's pending edit on the shared index, so it runs
    # only on files whose bytes now equal the stored blob exactly.
    try:
        worktree = subprocess.check_output(
            ["git", "hash-object", "--no-filters", "--stdin-paths"], cwd=REPO,
            input=("\n".join(done) + "\n").encode("utf-8")).decode().split()
        staged = {}
        listing = subprocess.check_output(["git", "ls-files", "-s", "--"] + done, cwd=REPO)
        for line in listing.decode("utf-8", "replace").splitlines():
            meta, _, p = line.partition("\t")
            staged[p] = meta.split()[1]
        clean = [p for p, h in zip(done, worktree) if staged.get(p) == h]
        if clean:
            subprocess.run(["git", "add", "--renormalize", "--"] + clean,
                           cwd=REPO, check=True, capture_output=True)
        for p in sorted(set(done) - set(clean)):
            out.append("FIX-EOL: %s carries an uncommitted edit; converted, index left "
                       "alone" % p)
    except (OSError, subprocess.CalledProcessError) as exc:
        out.append("FIX-EOL: index refresh failed (%s); `git status` may list the "
                   "converted files with an empty diff" % exc)


STATE_DOOR = "docs/agent/prompts/perma/STATE_EVICTION.md"


def state_added_lines():
    """Lines the working tree adds to STATE.md relative to HEAD.

    Returns (lines, note). `note` is set when the comparison could not be made
    and the caller must say so rather than imply a clean result.
    """
    import difflib
    if not os.path.exists(STATE):
        return [], "STATE.md is absent"
    # Only subprocess failures are recoverable here. A NameError or a typo must
    # raise: a broad except turns a coding error into a silent, permanent SKIP,
    # which is how this gate shipped DEAD in the donor on its first run.
    try:
        head = subprocess.check_output(
            ["git", "show", "HEAD:docs/agent/STATE.md"],
            cwd=REPO, stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError):
        cur = lf_bytes(STATE).decode("utf-8", "replace").split("\n")
        return [l for l in cur if l.strip()], "no HEAD copy to compare against"
    old = head.replace(b"\r\n", b"\n").decode("utf-8", "replace").split("\n")
    new = lf_bytes(STATE).decode("utf-8", "replace").split("\n")
    added = []
    for tag, _, _, j1, j2 in difflib.SequenceMatcher(None, old, new).get_opcodes():
        if tag in ("insert", "replace"):
            added.extend(l for l in new[j1:j2] if l.strip())
    return added, None


def check_state_admission(out):
    """Put the admission door in front of anyone adding a line to STATE.

    This gate CANNOT judge a line — no machine can answer "whose job is this".
    It makes the judgement unavoidable at the moment of the write by printing
    the added lines beside the four questions. A PASS here is not approval.

    Ported from SMR-BugFixPack @ ac4e4d3. The door's full text was already here
    (`prompts/perma/STATE_EVICTION.md`); only its gate was missing — which is
    what the owner ask OI-08 option (b) asked for before STATE's framing
    flipped from push to pull.
    """
    added, note = state_added_lines()
    if note:
        out.append("STATE ADMISSION: SKIPPED — %s (no judgement made)" % note)
        return True
    if not added:
        out.append("STATE ADMISSION: no lines added; door is %s" % STATE_DOOR)
        return True

    out.append("STATE ADMISSION: %d line(s) added — ANSWER THE DOOR BEFORE COMMITTING"
               % len(added))
    for line in added[:12]:
        out.append("    + %s" % line.strip()[:96])
    if len(added) > 12:
        out.append("    + ... %d more" % (len(added) - 12))
    out.append("  1 HARM        name the victim; a mechanism is not one; floor moderate")
    out.append("  2 REACH       (a) whose job is this?  (b) who needs to know?")
    out.append("                both must answer EVERYONE; self-consuming chain work")
    out.append("                never passes (b), by construction")
    out.append("  3 GATE        a machine catches it -> cite the gate, don't restate it")
    out.append("  4 VOLATILITY  can its state still change? settled means record, not state")
    out.append("  AND-ed, never OR-ed: one failure is enough. Full text: %s" % STATE_DOOR)
    out.append("  This gate cannot judge a line. It only makes you answer. "
               "A PASS is not approval.")
    return True


def required_selftest(filename, out):
    """Repo-local falsifiers need no game tree; missing/broken is always RED.

    A falsifier that stops firing is itself a red: it is the only evidence that
    the gate it guards is alive rather than silently skipping. Note the broad
    `except` here is correct BECAUSE its failure path is RED — the trap the
    donor hit was a broad except whose failure path printed as benign.
    """
    label = filename.removesuffix(".py").replace("_", " ").upper()
    tool = os.path.join(REPO, "tools", filename)
    started = time.perf_counter()
    try:
        p = subprocess.run([sys.executable, tool], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=60)
    except Exception as exc:                          # noqa: BLE001 — see docstring
        out.append("%s: RED — could not run (%s)" % (label, exc))
        return False
    elapsed = time.perf_counter() - started
    if p.returncode == 0:
        out.append("%s: PASS (%.3f s)" % (label, elapsed))
        return True
    out.append("%s: RED — FAILED (exit %d, %.3f s). Full output:"
               % (label, p.returncode, elapsed))
    out.extend("         " + line for stream in (p.stdout, p.stderr)
               for line in (stream or "").splitlines())
    return False


def flpk_selftest(out):
    """Run flpk_extract.py's falsifier as a gate, for the reason it exists.

    The pack reader had no fixture, and its nested-directory defect read 56
    entries out of a 54-entry pack for a day. The two phantom names were
    blamed on packaging, `STATE.md` recorded an "UNEXPLAINED" gap, and a
    session concluded the only way to settle it was re-downloading the pack --
    all from a parser bug a 40-line fixture catches. Needs no game tree: the
    arenas are built in memory, so there is no "cannot run" case.
    ⇒ An instrument whose output is used to SKIP evidence gets a fixture.

    Ported from SMR-BugFixPack @ 6cda0ac with this repo's discipline: absent
    or unrunnable is RED, not "not checked" -- `pack_list.py` imports the
    parser, and only a spawn failure is caught, so a coding error here raises.
    """
    tool = os.path.join(REPO, "tools", "flpk_extract.py")
    if not os.path.isfile(tool):
        out.append("FLPK SELFTEST: RED — tools/flpk_extract.py is absent "
                   "(pack_list.py imports its parser)")
        return False
    try:
        p = subprocess.run([sys.executable, tool, "--selftest"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        out.append("FLPK SELFTEST: RED — could not run (%s)" % exc)
        return False
    if p.returncode == 0:
        out.append("FLPK SELFTEST: PASS (nested + shallow; the pack reader "
                   "owns every descendant span)")
        return True
    out.append("FLPK SELFTEST: RED — flpk_extract --selftest FAILED (exit %d) "
               "-- every pack listing, entry count and alias claim read through "
               "this parser is untrustworthy until it is green. Full output:"
               % p.returncode)
    out.extend("         " + line for stream in (p.stdout, p.stderr)
               for line in (stream or "").splitlines())
    return False


# --- MODULE SETS + tools/upload_preflight.py: the three lists that decide what ships
#
# Ported 2026-09-18 from SMR-BugFixPack @ 29b7a68, unchanged: this mod ships
# by the same SaveDef rule, from the same three lists. The dated incident below
# is the donor's.
#
# ⛔ WHY THIS IS RED AND NOT A WARN. `Code/*.lua` is what exists, `items.lua` is
# the Mod Editor's item list, and `metadata.lua`'s `code` list is the load
# order. Both portals FORCE a `SaveDef` on upload, and `SaveDef` rebuilds the
# `code` list SOLELY from `items.lua` (`Mod.lua:816-840`, `:973`) -- Steam's
# before packing. So these three disagreeing does not merely lint badly: it
# DECIDES WHAT SHIPS. A module present in Code/ but absent from items.lua ships
# absent, and the player gets a pack quietly missing a fix.
#
# This gate exists because doccheck reported GREEN through exactly that state
# (hotfix2 link 02, 2026-09-08): 36 modules had been deleted, `items.lua` held
# 45 entries and `metadata.lua`'s `code` list still held 81. The only reason it
# was caught is that a human happened to read the LOAD ORDER line's file count
# against the number they expected. doccheck already computed both numbers and
# simply never compared them to each other.
#
# ⚠️ The comparison is by NAME and reports the SYMMETRIC DIFFERENCE. A count
# check would have passed a same-size swap, and a count is also what nearly let
# the 2026-09-08 state through.

CODE_IN_ITEMS = re.compile(r"'CodeFileName',\s*\"(Code/[^\"]+\.lua)\"")


def _metadata_code_list(text):
    """The `code` list, read as a list rather than as every Code/ string in the
    file -- a description or a comment could mention one."""
    m = re.search(r"'code',\s*\{", text)
    if not m:
        return None
    depth, i = 1, m.end()
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return re.findall(r"\"(Code/[^\"]+\.lua)\"", text[m.end():i])


def module_set_agreement(out):
    """Code/*.lua == items.lua == metadata.lua's `code` list, by name (MODULE SETS + tools/upload_preflight.py)."""
    names = lua_files(CODE)
    if names is None:
        out.append("MODULE SETS: not checked (Code/ not readable)")
        return True
    on_disk = {"Code/" + n for n in names}

    sets = {"Code/": on_disk}
    for label, rel, extract in (
            ("items.lua", "items.lua", lambda t: CODE_IN_ITEMS.findall(t)),
            ("metadata.lua 'code'", "metadata.lua", _metadata_code_list)):
        try:
            with open(os.path.join(REPO, rel), encoding="utf-8-sig",
                      errors="replace") as fh:
                found = extract(fh.read())
        except OSError as exc:
            out.append("MODULE SETS: not checked (%s)" % exc)
            return True
        if found is None:
            out.append("  RED  module sets: no `code` list found in %s -- a "
                       "SaveDef would rebuild it from items.lua and this gate "
                       "cannot see what would ship" % rel)
            return False
        sets[label] = set(found)

    ok = True
    labels = list(sets)
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            only_a = sorted(sets[a] - sets[b])
            only_b = sorted(sets[b] - sets[a])
            if not only_a and not only_b:
                continue
            ok = False
            out.append("  RED  module sets DISAGREE: %s vs %s (MODULE SETS + tools/upload_preflight.py -- a "
                       "SaveDef rebuilds metadata.lua's code list from "
                       "items.lua on upload, so this decides what ships)"
                       % (a, b))
            for n in only_a:
                out.append("         only in %-20s %s" % (a, n))
            for n in only_b:
                out.append("         only in %-20s %s" % (b, n))
    out.append("MODULE SETS: %d file(s) in Code/, items.lua and metadata.lua's "
               "code list %s" % (len(on_disk), "agree by name" if ok
                                 else "DISAGREE -- see above"))
    return ok


def parse_gate(out):
    """Every Code/*.lua must parse (tools/parsecheck.py).

    Ported 2026-09-18 from SMR-BugFixPack @ 8754e00, unchanged; the chain
    history below is the donor's. parsecheck_selftest() below runs the
    parser's own falsifier, which the donor leaves manual.

    Three consecutive chain links hand-rolled a Lua block-balance checker to
    stand in for a syntax check, and two of them silently accused
    byte-identical files -- 01's flagged one, 02's flagged sixteen. There is a
    real parser on this rig; parsecheck.py uses it, ships with its own
    falsifier (01's condition), and this is the gate that stops a fourth
    session writing a fourth counter.

    ⚠️ Syntax ONLY, and weaker than every other gate here. The Test Kit is
    reported, never gated -- same standing as testkit_tree, by the owner's
    2026-08-04 decision that the kit does not block the pack.
    """
    tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parsecheck.py")
    if not os.path.isfile(tool):
        out.append("PARSE: not checked (tools/parsecheck.py absent)")
        return True
    ok = True
    for label, path, gates in (("Code/", CODE, True),
                               ("TestKit", os.path.join(TESTKIT, "Code"), False)):
        if not os.path.isdir(path):
            continue
        try:
            p = subprocess.run([sys.executable, tool, "--dir", path],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=300)
        except Exception as exc:              # a tool bug must report, not crash
            out.append("PARSE (%s): not checked (%s)" % (label, exc))
            continue
        lines = (p.stdout or "").strip().splitlines()
        summary = lines[-1] if lines else "no output"
        out.append("%s%s" % (summary, "" if gates else "  (report-only)"))
        if p.returncode and gates:
            for line in lines[:-1]:
                out.append("  RED  %s" % line)
            ok = False
    return ok


def parsecheck_selftest(out):
    """Run parsecheck.py's falsifier as a gate, so PARSE is trusted only while
    it still rejects the six broken shapes and accepts the nasty-but-valid one.

    Not in the donor, whose parse gate leaves `--selftest` manual; added here
    under the 2026-09-17 standardisation ruling that a gate is not trusted
    until shown to fire on a known-bad case. A missing parser is exit 2 and is
    REPORTED, not red -- the same standing parse_gate() gives it -- because a
    rig without `lupa` must still be able to run doccheck. A failing leg is RED.
    """
    tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parsecheck.py")
    if not os.path.isfile(tool):
        out.append("PARSECHECK SELFTEST: RED — tools/parsecheck.py is absent "
                   "(the PARSE gate runs it)")
        return False
    try:
        p = subprocess.run([sys.executable, tool, "--selftest"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        out.append("PARSECHECK SELFTEST: RED — could not run (%s)" % exc)
        return False
    if p.returncode == 2:
        out.append("PARSECHECK SELFTEST: not run (%s)"
                   % ((p.stdout or "").strip().splitlines() or ["no parser"])[-1])
        return True
    if p.returncode == 0:
        out.append("PARSECHECK SELFTEST: PASS (valid shapes parse, six broken "
                   "shapes are rejected)")
        return True
    out.append("PARSECHECK SELFTEST: RED — parsecheck --selftest FAILED (exit %d) "
               "-- the PARSE line cannot be trusted until it is green. Full output:"
               % p.returncode)
    out.extend("         " + line for stream in (p.stdout, p.stderr)
               for line in (stream or "").splitlines())
    return False


# ---------------------------------------------------------------------------
# Pack-ignore parity (ported 2026-09-18 from SMR-BugFixPack @ 03fc504, unchanged).
#
# ⛔ DEFINED BUT NOT YET CALLED FROM main(). Its falsifier legs run every time,
# in repair_pass_selftest.py. The call waits on the owner's edit to this repo's
# metadata.lua `ignore_files` (it lacks the donor's `*/.agents/*`, `*AGENTS.md`
# and `*.rgignore`, so those files ship today), and pack_predict.py's IGNORE
# must change in the same commit as metadata.lua. Uncomment the call in main()
# with that commit.

def tools_compile(out):
    """Every tools/*.py must byte-compile.

    Ported from SMR-BugFixPack @ 5bb1b44, unchanged. Nothing else here
    compiles the tools: a script with a syntax error left doccheck GREEN, and
    the first to notice was whoever ran it next. Compiled in memory with
    `compile()`, so no `.pyc` lands in the tree; warnings are not failures.
    Falsifier: `repair_pass_selftest.py` (a planted syntax error in a scratch
    copy of the tools goes RED; the clean copy passes).
    """
    names = tool_scripts()
    bad = []
    for name in names:
        path = os.path.join(TOOLS_DIR, name)
        try:
            with open(path, "rb") as fh:
                source = fh.read()
        except OSError as exc:
            bad.append("tools/%s: unreadable (%s)" % (name, exc))
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                compile(source, path, "exec", dont_inherit=True)
        except SyntaxError as exc:
            bad.append("tools/%s:%s: %s: %s" % (name, exc.lineno,
                                                 type(exc).__name__, exc.msg))
        except ValueError as exc:        # null bytes, on older interpreters
            bad.append("tools/%s: %s" % (name, exc))
    if not bad:
        out.append("TOOLS COMPILE: PASS (%d tools/*.py byte-compile)" % len(names))
        return True
    out.append("TOOLS COMPILE: RED — %d of %d tools/*.py do not compile"
               % (len(bad), len(names)))
    out.extend("  RED  " + line for line in bad)
    return False


def pack_ignore_parity(out):
    """The shipped filters and prediction must agree, including precedence."""
    try:
        with open(os.path.join(REPO, "metadata.lua"), encoding="utf-8-sig") as fh:
            lua = re.sub(r"--[^\n]*", "", fh.read())
        hit = re.search(r"['\"]ignore_files['\"]\s*,\s*\{([^}]*)\}", lua, re.S)
        if not hit:
            raise ValueError("metadata.lua ignore_files list missing")
        body = hit.group(1)
        token = r'''(?:"[^"\\]*(?:\\.[^"\\]*)*"|'[^'\\]*(?:\\.[^'\\]*)*')'''
        if not re.fullmatch(r"\s*(?:" + token + r"\s*,\s*)*", body):
            raise ValueError("metadata.lua ignore_files list is not literal strings")
        shipped = [ast.literal_eval(s) for s in re.findall(token, body)]
        with open(os.path.join(REPO, "tools", "pack_predict.py"), encoding="utf-8-sig") as fh:
            tree = ast.parse(fh.read())
        assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == "IGNORE"
                               for t in node.targets)]
        if len(assignments) != 1:
            raise ValueError("pack_predict.py must define one literal IGNORE list")
        predicted = ast.literal_eval(assignments[0].value)
        if not isinstance(predicted, list) or not all(isinstance(p, str) for p in predicted):
            raise ValueError("pack_predict.py IGNORE must be a string list")
        if shipped != predicted:
            out.append("PACK IGNORE PARITY: RED — metadata.lua ignore_files and "
                       "pack_predict.py IGNORE differ in membership or order")
            out.append("  shipped: %r\n  predicted: %r" % (shipped, predicted))
            return False
    except (OSError, ValueError, SyntaxError) as exc:
        out.append("PACK IGNORE PARITY: RED — %s" % exc)
        return False
    out.append("PACK IGNORE PARITY: PASS — %d filters agree in order" % len(shipped))
    return True


def local_readme_rows(path):
    """Folder names (without trailing slash) declared as rows of local/README.md's
    gate table, keyed to the line each first appears on."""
    rows = []
    with open(path, encoding="utf-8-sig") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not cells:
                continue
            m = re.match(r"`([^`]+)/`", cells[0])
            if m:
                rows.append((m.group(1), lineno))
    return rows


def check_local(out):
    """LOCAL: gate `local/` the way PROMPT MAP gates prompts — both directions,
    and unlike SCRATCH (report-only) this one CAN go RED. Ported from the fix
    pack (owner ruling, 2026-09-21, same day it landed there): `local/` is the
    git-ignored home for durable in-tree material that must not be committed;
    `local/README.md` is the entry gate — one row per subfolder, naming what it
    holds, what cites it, and the condition that ends it. No row, no folder; a
    row naming a folder not on disk is equally RED.
    """
    readme = os.path.join(LOCAL, "README.md")
    if not os.path.isfile(readme):
        out.append("LOCAL: RED  local/README.md is missing — the entry gate itself is gone")
        return False
    rows = local_readme_rows(readme)
    red = []
    seen = {}
    for name, lineno in rows:
        if name in seen:
            red.append("  RED  local/README.md repeats a row for %s/ (lines %d and %d)"
                       % (name, seen[name], lineno))
        else:
            seen[name] = lineno
    disk = {n for n in os.listdir(LOCAL)
            if n != "README.md" and os.path.isdir(os.path.join(LOCAL, n))}
    mapped = set(seen)
    for name in sorted(mapped - disk):
        red.append("  RED  local/README.md has a row for %s/ and the folder is not "
                   "there — delete the row in the commit that consumes it" % name)
    for name in sorted(disk - mapped):
        red.append("  RED  local/%s/ exists and local/README.md does not list it — "
                   "no row, no folder" % name)
    total_bytes = 0
    file_count = 0
    for dirpath, _dirnames, filenames in os.walk(LOCAL):
        for fn in filenames:
            try:
                total_bytes += os.path.getsize(os.path.join(dirpath, fn))
                file_count += 1
            except OSError:
                pass
    size_line = ("LOCAL SIZE: %d file(s), %.1f MB under local/"
                % (file_count, total_bytes / (1024.0 * 1024.0)))
    if red:
        out.extend(red)
        out.append("LOCAL: RED  %d finding(s)" % len(red))
        out.append(size_line)
        return False
    out.append("LOCAL: PASS — %d row(s) agree with disk in both directions"
               % len(rows))
    out.append(size_line)
    return True


def _rule_text(rel):
    """Read one Markdown file with line endings normalized for byte checks."""
    with open(os.path.join(REPO, *rel.split("/")), encoding="utf-8-sig",
              newline="") as fh:
        return fh.read().replace("\r\n", "\n").replace("\r", "\n")


def _rule_block(lines):
    """Return the sole well-formed rule-block span, or None.

    Trap: a document may MENTION the markers in prose (the retired port ledger and the
    efficiency survey both quote them inside backticks). Requiring exactly one
    of each, in order, is what keeps a quotation from reading as a second block.
    """
    headings = [i for i, line in enumerate(lines) if line == RULE_HEADING]
    starts = [i for i, line in enumerate(lines) if line == RULE_START]
    ends = [i for i, line in enumerate(lines) if line == RULE_END]
    if (len(headings), len(starts), len(ends)) != (1, 1, 1):
        return None
    if not headings[0] < starts[0] < ends[0]:
        return None
    return headings[0], starts[0], ends[0]


def check_rule_headers(out):
    """Check the deliberately mechanical half of the rules-header model.

    An untagged sentence cannot be classified reliably by syntax, so this check
    deliberately does not pretend to find one. A one-time census and owner
    adjudication supply that semantic half; this function enforces the durable
    structure they produce. A PASS here is not approval of any rule's content.
    """
    ok = True
    required_blocks = {}
    header_rule_count = 0
    over_warn = []

    for rel in RULE_HEADER_DOCS:
        try:
            body = _rule_text(rel)
        except OSError as exc:
            out.append("RULES HEADERS: RED — cannot read %s: %s" % (rel, exc))
            ok = False
            continue
        lines = body.split("\n")
        block = _rule_block(lines)
        if block is None:
            out.append("RULES HEADERS: RED — %s must contain exactly one ordered "
                       "%s / RULES marker block" % (rel, RULE_HEADING))
            ok = False
            continue
        heading, start, end = block
        required_blocks[rel] = block
        size = len("\n".join(lines[heading:end + 1]).encode("utf-8"))
        is_kernel = rel.replace("\\", "/").endswith(KERNEL_HEADER_FILE)
        hard = KERNEL_HEADER_MAX_BYTES if is_kernel else RULE_HEADER_MAX_BYTES
        warn = KERNEL_HEADER_WARN_BYTES if is_kernel else RULE_HEADER_WARN_BYTES
        if size > hard:
            out.append("RULES HEADERS: RED — %s header is %d B; hard cap is %d B"
                       % (rel, size, hard))
            ok = False
        elif size > warn:
            over_warn.append("%s (%d B, warn %d)" % (rel, size, warn))
        header_rule_count += sum(1 for line in lines[start + 1:end]
                                 if line.startswith("Rule:"))

    # The placement half. It runs over EVERY tracked Markdown file, not just the
    # required ones — that is what makes the header the only legal home.
    try:
        tracked = subprocess.check_output(
            ["git", "ls-files", "*.md"], cwd=REPO,
            text=True, encoding="utf-8", errors="replace",
        ).splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        out.append("RULE PLACEMENT: RED — cannot enumerate tracked Markdown: %s" % exc)
        return False

    misplaced = []
    malformed = []
    forbidden = []
    duties = {}
    duplicate_duties = []
    state_rules = []
    for rel in tracked:
        rel = rel.replace("\\", "/")
        # AGENTS.md is a generated byte mirror, verified by check_agents_mirror.
        # Counting it would manufacture a second canonical surface and report
        # every kernel rule as its own duplicate.
        if rel == "AGENTS.md":
            continue
        try:
            lines = _rule_text(rel).split("\n")
        except OSError as exc:
            out.append("RULE PLACEMENT: RED — cannot read %s: %s" % (rel, exc))
            ok = False
            continue
        block = _rule_block(lines)
        for index, line in enumerate(lines):
            if not line.startswith("Rule:"):
                continue
            location = "%s:%d" % (rel, index + 1)
            if rel == "docs/agent/STATE.md":
                state_rules.append(location)
            if rel in RULE_FORBIDDEN or rel.startswith("docs/archive/"):
                forbidden.append(location)
            in_header = (block is not None and block[1] < index < block[2])
            if not in_header:
                misplaced.append(location)
            if in_header and (not RULE_STYLE_RE.fullmatch(line) or "**" in line
                              or RULE_EMOJI_RE.search(line)
                              or re.search(r"\b(?:MUST|NEVER|ALWAYS)\b", line)):
                malformed.append(location)
                continue
            if not in_header:
                continue
            duty_match = RULE_DUTY_RE.fullmatch(line)
            duty = re.sub(r"\s+", " ", duty_match.group(1)).casefold()
            previous = duties.get(duty)
            if previous is None:
                duties[duty] = location
            else:
                duplicate_duties.append((previous, location))

    # STATE is status, not law. A rule parked there is a rule that expires with
    # the next eviction, which is exactly how a duty gets silently lost.
    if state_rules:
        out.append("RULES HEADERS: RED — STATE.md must contain zero Rule lines: %s"
                   % ", ".join(state_rules))
        ok = False
    if forbidden:
        out.append("RULES HEADERS: RED — Rule lines are forbidden on generated or "
                   "archived surfaces: %s" % ", ".join(forbidden))
        ok = False
    if malformed:
        out.append("RULES HEADERS: RED — malformed canonical Rule line(s): %s"
                   % ", ".join(malformed))
        ok = False
    if duplicate_duties:
        out.append("RULES HEADERS: RED — duplicate canonical duties: %s"
                   % "; ".join("%s = %s" % pair for pair in duplicate_duties))
        ok = False

    if ok:
        out.append("RULES HEADERS: PASS — %d required block(s), %d canonical "
                   "header rule(s)" % (len(required_blocks), header_rule_count))
    if over_warn:
        out.append("RULES HEADERS: WARN — header over its warning threshold: %s"
                   % ", ".join(over_warn))
    if misplaced:
        out.append("RULE PLACEMENT: WARN — Rule line(s) outside Must_Read_Header: %s"
                   % ", ".join(misplaced))
    else:
        out.append("RULE PLACEMENT: PASS — every canonical Rule line is in a header")
    return ok


def main():
    ap = argparse.ArgumentParser(description="SMR-OptInPack doc structure check")
    ap.add_argument("--emit-counts", action="store_true",
                    help="also print the STATE-ready counts block")
    ap.add_argument("--emit-fingerprint", action="store_true",
                    help="group facts by derived_at and say which groups still "
                         "describe the installed game build")
    ap.add_argument("--regen", "--regen-index", action="store_true", dest="regen",
                    help="rewrite every generated file (bugs/INDEX.md, "
                         "facts/INDEX.md, the .agents/skills/ mirror, "
                         "tools/README.md's tool rows and AGENTS.md) from its "
                         "source, then check")
    ap.add_argument("--fix-eol", nargs="*", metavar="PATH", dest="fix_eol",
                    help="convert CRLF to LF in every tracked text file that has any "
                         "(mixed or whole-CRLF), or only the PATHs given, then run the "
                         "checks. The blob is already LF, so git sees no change")
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
    if args.regen:
        try:
            regen(out)
        except Exception as exc:                      # noqa: BLE001 — report, don't crash
            print("doccheck: RED — --regen failed: %s" % exc)
            return 1
    if args.fix_eol is not None:
        # The donor's order: convert, then run every check below, so the
        # run that fixed the endings also shows the tree it left.
        eol_fix(args.fix_eol, out)
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
    ok = check_checklist(out) and ok
    ok = check_parked(out) and ok
    ok = check_agents_mirror(out) and ok
    ok = check_skills(out) and ok
    ok = check_prompt_map(out) and ok
    ok = check_rule_headers(out) and ok
    ok = required_selftest("rule_headers_selftest.py", out) and ok
    ok = required_selftest("ck170_selftest.py", out) and ok
    ok = required_selftest("prompt_map_selftest.py", out) and ok
    ok = required_selftest("repair_pass_selftest.py", out) and ok
    ok = required_selftest("counts_selftest.py", out) and ok
    ok = required_selftest("sync_from_fixpack_selftest.py", out) and ok
    ok = flpk_selftest(out) and ok
    ok = check_tools_catalog(out) and ok
    ok = eol_report(out) and ok
    ok = check_state(out) and ok
    ok = check_state_admission(out) and ok
    push_set_report(out)
    counts = recount(model, out)
    ok = temporary_sweep(out) and ok
    ok = load_order(out) and ok
    ok = wrap_targets_check(out) and ok
    ok = parse_gate(out) and ok
    ok = parsecheck_selftest(out) and ok
    ok = tools_compile(out) and ok
    ok = module_set_agreement(out) and ok
    ok = pack_ignore_parity(out) and ok
    ok = check_local(out) and ok
    testkit_tree(out)  # report-only by owner decision (2026-08-04) — never gates
    scratch_report(out)  # report-only, same standing as testkit_tree

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

    if args.emit_fingerprint:
        emit_fingerprints(out)

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
