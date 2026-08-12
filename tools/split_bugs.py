#!/usr/bin/env python
"""split_bugs.py — docs/BUGS.md -> docs/agent/bugs/ (DOC_RESTRUCTURE_SPEC §3a,
as amended by the ROUTE (a) decision in the docs-restructure chain's prompt 2).

    python tools/split_bugs.py --dry-run     # accounting only, writes nothing
    python tools/split_bugs.py --write       # perform the split
    python tools/split_bugs.py --dry-run --from-git HEAD~1   # source from git

PORTED 2026-08-12 (split-optins prompt 3) from SMR-BugFixPack @ 33d69f5.
⚠️ N/A IN THIS REPO, except for the two halves doccheck imports every run —
`parse_front`/`load_from_dir` (reading the entries back) and `render_index`
(regenerating docs/agent/bugs/INDEX.md). This repo never held a `docs/BUGS.md`,
so `parse`/`build`/`write_all`/`verify_split` and the frozen tables they assert
(STRUCTURAL, HEADLESS_ROWS, GROUPED_FILES, EXPECTED_ORPHANS) describe the
DONOR's migration. They are kept rather than deleted so the entry format has
exactly one definition and one parser, in both repos (chain rule 7: a clause
that does not apply is marked N/A, never silently dropped). The only edit is
the index header's prose, below.

This is a ONE-SHOT migration, but it stays in tools/ because doccheck's
`--verify-split` imports it to re-run the accounting against the pre-split blob
(`git show <rev>:docs/BUGS.md`). Everything here is mechanical: no line of entry
content is edited, reflowed, or re-ordered.

WHAT THE FILE LOOKS LIKE (verified 2026-08-03 against 12726 lines, twice — the
chain's prompt 1 and again here; every claim below is ASSERTED at run time and
the run aborts if the file stopped matching):

  region 1  lines 1 .. first `### <ID>` heading - 1
            intro prose + the ONE index table (151 contiguous rows, kind runs
            F x63, D x12, F x35, C x41, no interior header) + the Severity
            legend + a `---` + `## P1 - gameplay-breaking`.
            The TABLE LINES are consumed (INDEX.md replaces them) — but every
            cell of every row is preserved verbatim in front matter, so nothing
            the table said is lost. The prose lines go to _notes.md.
  region 2  the entries, in file order. An entry runs from its `### <ID>`
            heading to the next boundary. `^### ` alone is NOT a boundary:
            entries carry their own `##`/`###` sub-headings (F97's rate-question
            block, D12's "WHAT D12 SHIPS", F86/F87's `> ##` quotes).
  region 3  `## Not yet swept (follow-up targets)` .. EOF -> _notes.md. It
            FOLLOWS the C41 entry and is not part of it.

  THREE STRUCTURAL LINES belong to no entry (`## P2`, `## P3`, `## Phase 2
  findings`). A naive "entry runs to the next heading" rule swallows each into
  the PRECEDING entry and byte-accounting still balances, because nothing is
  lost — the corruption is invisible to the only check. They are found two
  independent ways (shape: a `## ` line followed by a blank and then an entry
  heading; and the recorded line/text table below) and the two must agree.

  35 INDEX ROWS HAVE NO HEADING OF THEIR OWN — C02 and 34 IDs whose text lives
  inside two grouped entries. Route (a), decided 2026-08-03: 116 entry files;
  the grouped files adopt their members' rows into front matter (`members:`) so
  the generated INDEX can still carry all 151 rows; C02, which has no entry text
  anywhere in the file, keeps an INDEX row that points at nothing and is
  recorded in _notes.md. Nothing is invented: a grouped member's row cells are
  copied verbatim, and no per-ID anchor is fabricated inside grouped prose.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TOOLS)
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import doccheck  # noqa: E402  (status_word is imported, never re-implemented)

SOURCE_REL = "docs/BUGS.md"
OUT_REL = "docs/agent/bugs"
SPLIT_DATE = "2026-08-03"

HEAD_RE = doccheck.HEAD_RE          # ^### ([FDC]\d+)\b   — the ONLY delimiter
ROW_RE = doccheck.ROW_RE            # ^\|\s*([FDC]\d+)\s*\|
TAG_RE = doccheck.TAG_RE            # last `[...]` group on the heading line
SECTION_RE = re.compile(r"^## ")
INDEX_HEAD_RE = re.compile(r"^## Index\s*$")
SWEPT_RE = re.compile(r"^## Not yet swept\b")
# A grouped section's members are its `- **C12 ...` bullets.
MEMBER_RE = re.compile(r"^-\s+\*\*(C\d+)\b")

# --- recorded facts, asserted at run time (they are claims, not licences) ----

# Structural section headers that belong to no entry. Verified 2026-08-03.
# ⚠️ The chain's prompt 1 recorded THREE of these; there are FOUR. The fourth
# (`## Candidates under investigation`, between the D11 and D12 entries) was
# found by the shape rule below and confirmed by reading all 34 `## ` lines in
# region 2 — the other 30 are entry sub-headings and none is followed by a
# blank line and an entry heading. Left unfound it would have been swallowed
# into D11 with the accounting still balancing.
STRUCTURAL = [
    (666, "## P2 — wrong numbers / notable misbehavior"),
    (932, "## P3 — cosmetic / latent / mod-facing"),
    (1327, "## Phase 2 findings — details (2026-07-24)"),
    (10122, "## Candidates under investigation"),
]

# The 35 index rows with no `###` heading of their own. Asserted EXACTLY: a 36th
# heading-less row means the file changed under us and a human must look.
HEADLESS_ROWS = (
    {"C02"}
    | {"C%02d" % n for n in range(4, 12)}
    | {"C%02d" % n for n in range(13, 39)}
)

# Grouped entries: heading ID -> the file name it gets. The second heading's
# stated range ("C12-C31") is STALE — it holds C12 through C38 — so the FILE
# NAME tells the truth while the heading bytes stay preserved.
GROUPED_FILES = {"C03": "C03-C11", "C12": "C12-C38"}

# Rows that end up owned by nobody: an INDEX row with no entry text anywhere.
EXPECTED_ORPHANS = {"C02"}
ORPHAN_NOTE = "NO ENTRY TEXT (verified prompt 1, %s)" % SPLIT_DATE

GENERATED_BANNER = "<!-- GENERATED by tools/doccheck.py — do not hand-edit -->"

FRONT_FIELDS = ["id", "seq", "row", "title", "status", "status_source",
                "priority", "evidence", "row_status", "updated", "copies"]


class SplitError(Exception):
    """Any accounting or structure claim that failed. The caller stops."""


# --------------------------------------------------------------------------
# source loading
# --------------------------------------------------------------------------

def load_lines(rev=None, path=None):
    """-> list of source lines, terminator-free, EOL-convention-independent.

    str.splitlines() is NOT used: it also breaks on \\x0b, \\x0c, \\u2028 and
    friends, so a stray character would silently change the line count relative
    to git's view of the same file.
    """
    if rev:
        raw = subprocess.check_output(
            ["git", "show", "%s:%s" % (rev, SOURCE_REL)], cwd=REPO)
        text = raw.decode("utf-8-sig")
    else:
        with open(path or os.path.join(REPO, SOURCE_REL),
                  encoding="utf-8-sig") as fh:
            text = fh.read()
    text = text.replace("\r\n", "\n")
    if "\r" in text:
        raise SplitError("source carries lone CR characters; refusing to guess")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()  # trailing newline, not a line
    return lines


def blame_dates(rev, nlines):
    """-> {line_no: 'YYYY-MM-DD'} of the last commit to touch each line."""
    args = ["git", "blame", "--porcelain", rev or "HEAD", "--", SOURCE_REL]
    out = subprocess.check_output(args, cwd=REPO).decode("utf-8", "replace")
    sha_re = re.compile(r"^([0-9a-f]{40}) (\d+) (\d+)(?: (\d+))?$")
    stamp, tz, line_sha, cur = {}, {}, {}, None
    for line in out.split("\n"):
        if line.startswith("\t"):
            continue
        m = sha_re.match(line)
        if m:
            cur = m.group(1)
            line_sha[int(m.group(3))] = cur
            continue
        if line.startswith("author-time "):
            stamp[cur] = int(line.split()[1])
        elif line.startswith("author-tz "):
            tz[cur] = line.split()[1]
    dates = {}
    for lineno, sha in line_sha.items():
        secs = stamp.get(sha)
        if secs is None:
            continue
        off = tz.get(sha, "+0000")
        sign = -1 if off.startswith("-") else 1
        secs += sign * (int(off[1:3]) * 3600 + int(off[3:5]) * 60)
        dates[lineno] = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=secs)
    if len(dates) < nlines:
        raise SplitError("git blame covered %d of %d lines" % (len(dates), nlines))
    return {n: d.strftime("%Y-%m-%d") for n, d in dates.items()}


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

def split_row(line):
    """-> the 5 cells of an index row (ID, title, sev, conf, status), stripped.

    The table pads its cells for alignment; only that padding is dropped, so a
    stored cell and its source cell differ by whitespace and by nothing else
    (asserted by verify_rows()).
    """
    cells = line.rstrip().split("|")
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    if len(cells) != 6 or cells[0].strip() != "":
        raise SplitError("index row is not 6-field: %r" % line[:90])
    return [c.strip() for c in cells[1:]]


def c_status(row):
    """Status word for a row with no heading tag to derive from.

    Order matters and is not the F/D order: on a C row, column 4 is the
    DISPOSITION column (`cand`, `**CLOSED - promoted**`), not a confidence
    column, so it is read first. Only if neither cell carries a vocabulary word
    does the row fall back to `cand`, which is what an unclassifiable C row is
    by construction. The choice is recorded per row in `status_source:`.
    """
    word = doccheck.status_word(row["evidence"])
    if word:
        return word, "row-evidence"
    word = doccheck.status_word(row["row_status"])
    if word:
        return word, "row-status"
    return "cand", "c-row-default"


def parse(lines):
    """-> the split model. Raises SplitError on any structural surprise."""
    n = len(lines)
    heads = [(i + 1, m.group(1)) for i, line in enumerate(lines)
             if (m := HEAD_RE.match(line))]
    if not heads:
        raise SplitError("no entry headings found — is this the pre-split file?")
    first_head = heads[0][0]

    # ---- region 3 ---------------------------------------------------------
    swept = [i + 1 for i, line in enumerate(lines) if SWEPT_RE.match(line)]
    if len(swept) != 1:
        raise SplitError("expected exactly one '## Not yet swept' line, got %r" % swept)
    tail_start = swept[0]
    if tail_start < heads[-1][0]:
        raise SplitError("'## Not yet swept' precedes the last entry heading")

    # ---- region 1: the index table ---------------------------------------
    idx_heads = [i + 1 for i, line in enumerate(lines[:first_head - 1])
                 if INDEX_HEAD_RE.match(line)]
    if len(idx_heads) != 1:
        raise SplitError("expected exactly one '## Index' heading, got %r" % idx_heads)
    table_head = idx_heads[0]

    rows, row_lines = [], []
    for i in range(table_head - 1, first_head - 1):
        m = ROW_RE.match(lines[i])
        if not m:
            continue
        cells = split_row(lines[i])
        if cells[0] != m.group(1):
            raise SplitError("row id cell disagrees with the row regex: %r" % lines[i][:90])
        rows.append({
            "row": len(rows) + 1, "line": i + 1, "id": cells[0], "title": cells[1],
            "priority": cells[2], "evidence": cells[3], "row_status": cells[4],
        })
        row_lines.append(i + 1)
    if not rows:
        raise SplitError("no index rows found in region 1")
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise SplitError("duplicate index rows: %r" % [i for i in ids if ids.count(i) > 1])
    if row_lines != list(range(row_lines[0], row_lines[-1] + 1)):
        raise SplitError("the index rows are not contiguous — a second table?")
    consumed = list(range(table_head, row_lines[-1] + 1))
    scaffold = [ln for ln in consumed if ln not in set(row_lines)]
    if len(scaffold) != 4:
        raise SplitError("expected 4 table scaffold lines (## Index, blank, "
                         "header, separator), got %d" % len(scaffold))
    # The F97 rate table also starts its lines with `| F97 |`; it lives inside
    # region 2 and is never scanned, so the trap cannot fire here — assert it.
    strays = [i + 1 for i in range(first_head - 1, n) if ROW_RE.match(lines[i])]
    if any(s in consumed for s in strays):
        raise SplitError("region-2 row scan leaked into the index table")

    # ---- structural section headers ---------------------------------------
    shaped = []
    for i in range(first_head - 1, tail_start - 1):
        if not SECTION_RE.match(lines[i]):
            continue
        if i + 2 < n and lines[i + 1].strip() == "" and HEAD_RE.match(lines[i + 2]):
            shaped.append((i + 1, lines[i]))
    if shaped != STRUCTURAL:
        raise SplitError(
            "structural `##` lines changed.\n  by shape:    %r\n  on record:   %r"
            % (shaped, STRUCTURAL))
    structural_lines = [ln for ln, _ in STRUCTURAL]

    # ---- entry boundaries -------------------------------------------------
    bounds = sorted([h[0] for h in heads] + structural_lines + [tail_start])
    entries, struct_blocks = [], []
    for pos, start in enumerate(bounds):
        end = bounds[pos + 1] - 1 if pos + 1 < len(bounds) else n
        if start in structural_lines:
            struct_blocks.append((start, end))
        elif start == tail_start:
            pass
        else:
            entries.append({"start": start, "end": end,
                            "id": HEAD_RE.match(lines[start - 1]).group(1)})
    if len(entries) != len(heads):
        raise SplitError("entry count %d != heading count %d" % (len(entries), len(heads)))

    # ---- rows <-> headings ------------------------------------------------
    by_id = {r["id"]: r for r in rows}
    head_ids = [e["id"] for e in entries]
    if len(set(head_ids)) != len(head_ids):
        raise SplitError("duplicate entry heading ids: %r"
                         % [i for i in head_ids if head_ids.count(i) > 1])
    no_row = [i for i in head_ids if i not in by_id]
    if no_row:
        raise SplitError("heading with no index row: %r" % no_row)
    headless = {i for i in ids if i not in set(head_ids)}
    if headless != HEADLESS_ROWS:
        raise SplitError(
            "the heading-less row set changed — a human must look.\n"
            "  now:      %r\n  on record: %r"
            % (sorted(headless - HEADLESS_ROWS), sorted(HEADLESS_ROWS - headless)))

    # ---- grouped entries and their members --------------------------------
    adopted = {}
    for entry in entries:
        entry["kind"] = "entry"
        entry["members"] = []
        if entry["id"] not in GROUPED_FILES:
            continue
        found = []
        for i in range(entry["start"] - 1, entry["end"]):
            m = MEMBER_RE.match(lines[i])
            if m and m.group(1) not in found:
                found.append(m.group(1))
        if not found or found[0] != entry["id"]:
            raise SplitError("%s: grouped bullets do not open with the heading id: %r"
                             % (entry["id"], found[:3]))
        nums = sorted(int(x[1:]) for x in found)
        if nums != list(range(nums[0], nums[-1] + 1)):
            raise SplitError("%s: member ids are not a contiguous range: %r"
                             % (entry["id"], found))
        name = "C%02d-C%02d" % (nums[0], nums[-1])
        if name != GROUPED_FILES[entry["id"]]:
            raise SplitError("%s: derived file name %s != decided %s"
                             % (entry["id"], name, GROUPED_FILES[entry["id"]]))
        entry["kind"] = "grouped"
        entry["file"] = name
        entry["contains"] = ["C%02d" % x for x in nums]
        for member in entry["contains"]:
            if member == entry["id"]:
                continue
            if member not in by_id:
                raise SplitError("%s: member %s has no index row" % (name, member))
            if member in adopted:
                raise SplitError("%s claimed twice" % member)
            adopted[member] = entry
        # members carry the ROW order, so the INDEX can reproduce the old table
        entry["members"] = sorted(
            (by_id[m] for m in entry["contains"] if m != entry["id"]),
            key=lambda r: r["row"])

    orphans = sorted(headless - set(adopted), key=lambda i: by_id[i]["row"])
    if set(orphans) != EXPECTED_ORPHANS:
        raise SplitError("orphan rows changed: %r (on record: %r)"
                         % (orphans, sorted(EXPECTED_ORPHANS)))

    # ---- notes ------------------------------------------------------------
    consumed_set = set(consumed)
    notes = [ln for ln in range(1, first_head) if ln not in consumed_set]
    for start, end in struct_blocks:
        notes.extend(range(start, end + 1))
    notes.extend(range(tail_start, n + 1))
    notes.sort()

    # ---- the accounting ---------------------------------------------------
    owned = {}
    def claim(line, owner):
        if line in owned:
            raise SplitError("line %d claimed by %s and %s" % (line, owned[line], owner))
        owned[line] = owner
    for entry in entries:
        for ln in range(entry["start"], entry["end"] + 1):
            claim(ln, entry["id"])
    for ln in consumed:
        claim(ln, "index-table")
    for ln in notes:
        claim(ln, "_notes.md")
    missing = [ln for ln in range(1, n + 1) if ln not in owned]
    if missing:
        raise SplitError("lines owned by nothing: %r" % missing[:20])

    entry_lines = sum(e["end"] - e["start"] + 1 for e in entries)
    if entry_lines + len(consumed) + len(notes) != n:
        raise SplitError("accounting does not balance")

    return {
        "lines": lines, "n": n, "rows": rows, "by_id": by_id, "entries": entries,
        "consumed": consumed, "scaffold": scaffold, "row_lines": row_lines,
        "notes": notes, "orphans": orphans, "struct_blocks": struct_blocks,
        "first_head": first_head, "tail_start": tail_start,
        "table_head": table_head, "adopted": adopted,
        "counts": {"entry_lines": entry_lines, "consumed": len(consumed),
                   "notes": len(notes), "total": n},
    }


def enrich(model, dates):
    """Attach front-matter fields (seq, status, updated) to every entry."""
    for seq, entry in enumerate(model["entries"], 1):
        lines = model["lines"]
        head = lines[entry["start"] - 1]
        row = model["by_id"][entry["id"]]
        tag = TAG_RE.search(head)
        if tag:
            word = doccheck.status_word(tag.group(1))
            if word is None:
                raise SplitError("%s: heading tag has no vocabulary status word"
                                 % entry["id"])
            source = "tag"
            row_word = doccheck.status_word(row["row_status"])
            if row_word is not None and row_word != word:
                raise SplitError("%s: index row says %r, heading tag says %r"
                                 % (entry["id"], row_word, word))
        else:
            # C01 and the two grouped headings carry no tag; the row is all
            # there is. Recorded per entry rather than smoothed over.
            word, source = c_status(row)
        entry.setdefault("file", entry["id"])
        entry.update({
            "seq": seq, "row": row["row"], "title": row["title"],
            "status": word, "status_source": source, "priority": row["priority"],
            "evidence": row["evidence"], "row_status": row["row_status"],
            "updated": max(dates[ln] for ln in range(entry["start"], entry["end"] + 1)),
            "copies": [],
        })
        for member in entry["members"]:
            member["status"], member["status_source"] = c_status(member)
    for orphan in model["orphans"]:
        row = model["by_id"][orphan]
        row["status"], row["status_source"] = c_status(row)
    return model


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

def yaml_scalar(value):
    """JSON-quoted, which is valid YAML and round-trips exactly. Entry titles
    carry backslashes (`Lua\\Buildings\\...`), quotes and em-dashes; nothing
    here may mangle one."""
    return json.dumps(value, ensure_ascii=False)


MEMBER_KEYS = ("row", "id", "title", "status", "status_source", "priority",
               "evidence", "row_status")


def render_member(row, extra=None):
    """One adopted index row, as a JSON object — which is also a valid YAML
    flow mapping, so it round-trips through `json.loads` with no YAML library
    and no guessing about the commas inside a title."""
    data = {k: row[k] for k in MEMBER_KEYS}
    if extra:
        data.update(extra)
    return "  - " + json.dumps(data, ensure_ascii=False)


def render_entry(model, entry):
    out = ["---"]
    for field in FRONT_FIELDS:
        value = entry[field]
        if field == "copies":
            out.append("copies: []")
        elif isinstance(value, int):
            out.append("%s: %d" % (field, value))
        else:
            out.append("%s: %s" % (field, yaml_scalar(value)))
    if entry["kind"] == "grouped":
        out.append('kind: "grouped"')
        out.append("contains: [%s]" % ", ".join(yaml_scalar(c) for c in entry["contains"]))
        out.append("members:")
        out.extend(render_member(m) for m in entry["members"])
    out.append("---")
    out.extend(model["lines"][entry["start"] - 1:entry["end"]])
    return out


def render_notes(model):
    front = ["---", 'kind: "notes"',
             'source: %s' % yaml_scalar("docs/BUGS.md, split %s by tools/split_bugs.py"
                                        % SPLIT_DATE)]
    if model["orphans"]:
        front.append("orphan_rows:")
        for orphan in model["orphans"]:
            front.append(render_member(model["by_id"][orphan],
                                       extra={"note": ORPHAN_NOTE}))
    front.append("---")
    added = [
        "# BUGS.md residue — everything that belonged to no entry",
        "",
        "Split out of `docs/BUGS.md` on %s by `tools/split_bugs.py`."
        % SPLIT_DATE,
        "",
        "Every line below the `---` is **byte-preserved** from that file, in source",
        "order: the intro, the five `##` section dividers whose entries moved out",
        "(P1, P2, P3, Phase 2, Candidates — they stack up here because nothing is",
        "left between them), and the “Not yet swept” backlog.",
        "",
        "The index table it also held is *not* here — `INDEX.md` replaces it, and",
        "every cell of all 151 rows is preserved verbatim in entry front matter.",
        "",
        "**C02 has an index row and no entry text anywhere in BUGS.md** (verified",
        "twice, %s): it keeps an INDEX row pointing at nothing rather than"
        % SPLIT_DATE,
        "getting an invented entry. Its row is in this file's front matter.",
        "",
        "---",
        "",
    ]
    body = [model["lines"][ln - 1] for ln in model["notes"]]
    return front + added + body, len(front), len(added), len(body)


def index_rows(model):
    """-> all 151 INDEX rows, in the order the old index table had them."""
    out = []
    for entry in model["entries"]:
        target = "%s.md" % entry["file"]
        out.append({
            "row": entry["row"], "seq": entry["seq"], "id": entry["id"],
            "title": entry["title"], "status": entry["status"],
            "priority": entry["priority"], "evidence": entry["evidence"],
            "link": ("[%s](%s)" % (target, target) if entry["kind"] != "grouped"
                     else "grouped → [%s](%s)" % (target, target)),
        })
        for member in entry["members"]:
            out.append({
                "row": member["row"], "seq": "", "id": member["id"],
                "title": member["title"], "status": member["status"],
                "priority": member["priority"], "evidence": member["evidence"],
                "link": "grouped → [%s](%s)" % (target, target),
            })
    for orphan in model["orphans"]:
        row = model["by_id"][orphan]
        out.append({
            "row": row["row"], "seq": "", "id": row["id"], "title": row["title"],
            "status": row["status"], "priority": row["priority"],
            "evidence": row["evidence"], "link": ORPHAN_NOTE,
        })
    out.sort(key=lambda r: r["row"])
    return out


def cell(text):
    """A table cell that cannot break the table it sits in."""
    return str(text).replace("|", "\\|")


def render_index(model):
    rows = index_rows(model)
    kinds = {k: len([r for r in rows if r["id"].startswith(k)]) for k in "FDC"}
    grouped = [e for e in model["entries"] if e["kind"] == "grouped"]
    out = [
        GENERATED_BANNER,
        "<!-- regenerate: python tools/split_bugs.py --write "
        "(migration) / verify: python tools/doccheck.py -->",
        "",
        "# Bug index — %d rows, %d entry files" % (len(rows), len(model["entries"])),
        "",
        "%d F + %d D + %d C. `seq`/`row` are this repo's own numbering, "
        "assigned when the" % (kinds["F"], kinds["D"], kinds["C"]),
        "entries moved here from SMR-BugFixPack (split-optins, 2026-08-12); "
        "each entry's front",
        "matter keeps the donor's `donor_seq`/`donor_row`. Generated from the "
        "front matter of",
        "`docs/agent/bugs/*.md` — edit an entry, not this file.",
        "",
    ]
    for entry in grouped:
        out.append("- `%s.md` is a **grouped** entry: %s share one body, and "
                   "their rows link to it. Per-ID anchors inside it do not exist "
                   "and are not invented."
                   % (entry["file"], "–".join([entry["contains"][0],
                                                    entry["contains"][-1]])))
    if model["orphans"]:
        out.append("- %s: index row with no entry text anywhere in BUGS.md "
                   "(verified %s); recorded in `_notes.md`."
                   % (", ".join(model["orphans"]), SPLIT_DATE))
    out.extend([
        "",
        "| seq | id | title | status | priority | evidence | entry |",
        "|----|----|-------|--------|----------|----------|-------|",
    ])
    for row in rows:
        out.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            row["seq"], row["id"], cell(row["title"]), cell(row["status"]),
            cell(row["priority"]), cell(row["evidence"]), row["link"]))
    out.append("")
    return out


def render_stub():
    return [
        "# Bug Tracker — MOVED %s" % SPLIT_DATE,
        "",
        "Per-entry files: `docs/agent/bugs/<ID>.md` · generated index: "
        "`docs/agent/bugs/INDEX.md` · residue (intro, section dividers, the "
        "“Not yet swept” backlog): `docs/agent/bugs/_notes.md`.",
        "",
    ]


# --------------------------------------------------------------------------
# verification + accounting
# --------------------------------------------------------------------------

def verify_rows(model, out):
    """Every index row cell is preserved verbatim (modulo alignment padding)."""
    bad = []
    for row in model["rows"]:
        source = split_row(model["lines"][row["line"] - 1])
        stored = [row["id"], row["title"], row["priority"], row["evidence"],
                  row["row_status"]]
        if source != stored:
            bad.append(row["id"])
    if bad:
        raise SplitError("row cells not preserved: %r" % bad)
    out.append("ROW CELLS: %d/%d index rows preserved verbatim in front matter "
               "(id/title/priority/evidence/row_status)"
               % (len(model["rows"]), len(model["rows"])))


def accounting(model, out):
    counts = model["counts"]
    n_rows = len(model["rows"])
    grouped = [e for e in model["entries"] if e["kind"] == "grouped"]
    notes_first = model["notes"][0]
    out.append("SOURCE: %s — %d lines" % (SOURCE_REL, counts["total"]))
    out.append("  region 1  lines 1..%d   intro + the ONE index table"
               % (model["first_head"] - 1))
    out.append("     consumed by INDEX.md      %5d  (%d rows + %d scaffold lines; "
               "every cell preserved in front matter)"
               % (counts["consumed"], n_rows, len(model["scaffold"])))
    out.append("     to _notes.md              %5d  (intro prose, legend, `---`, "
               "`## P1`)"
               % len([ln for ln in model["notes"] if ln < model["first_head"]]))
    out.append("  region 2  lines %d..%d  the entries"
               % (model["first_head"], model["tail_start"] - 1))
    out.append("     to %d entry files          %5d"
               % (len(model["entries"]), counts["entry_lines"]))
    out.append("     structural `##` headers   %5d  (%s — to _notes.md, NOT to "
               "the preceding entry)"
               % (sum(e - s + 1 for s, e in model["struct_blocks"]),
                  ", ".join(str(s) for s, _ in model["struct_blocks"])))
    out.append("  region 3  lines %d..%d  “Not yet swept” → _notes.md  %5d"
               % (model["tail_start"], counts["total"],
                  counts["total"] - model["tail_start"] + 1))
    out.append("  ---------------------------------------------------------------")
    out.append("  %d entry + %d consumed + %d notes = %d == %d source lines  %s"
               % (counts["entry_lines"], counts["consumed"], counts["notes"],
                  counts["entry_lines"] + counts["consumed"] + counts["notes"],
                  counts["total"],
                  "OK" if counts["entry_lines"] + counts["consumed"] + counts["notes"]
                  == counts["total"] else "MISMATCH"))
    out.append("  every source line is claimed exactly once (checked line by line)")
    out.append("ENTRIES: %d files — %d plain + %d grouped (%s)"
               % (len(model["entries"]), len(model["entries"]) - len(grouped),
                  len(grouped), ", ".join("%s.md holds %s" % (
                      e["file"], "–".join([e["contains"][0], e["contains"][-1]]))
                      for e in grouped)))
    out.append("ROWS: %d index rows → %d own an entry file, %d adopted into "
               "grouped front matter, %d orphan (%s)"
               % (n_rows, len(model["entries"]), len(model["adopted"]),
                  len(model["orphans"]), ", ".join(model["orphans"]) or "none"))
    out.append("NOTES: first preserved line is source line %d (%r)"
               % (notes_first, model["lines"][notes_first - 1][:40]))
    verify_rows(model, out)


def verify_written(model, outdir, out):
    """Re-read what was written and compare it to the source, line by line."""
    problems = []
    expected = {"%s.md" % e["file"] for e in model["entries"]}
    present = {n for n in os.listdir(outdir)
               if n.endswith(".md") and n not in ("INDEX.md", "_notes.md")}
    if present != expected:
        problems.append("entry file set differs: extra %r, missing %r"
                        % (sorted(present - expected), sorted(expected - present)))
    for entry in model["entries"]:
        path = os.path.join(outdir, "%s.md" % entry["file"])
        with open(path, encoding="utf-8") as fh:
            body = fh.read().replace("\r\n", "\n").split("\n")
        if body and body[-1] == "":
            body.pop()
        if body[0] != "---":
            problems.append("%s: no front matter" % entry["file"])
            continue
        close = body.index("---", 1)
        body = body[close + 1:]
        source = model["lines"][entry["start"] - 1:entry["end"]]
        if body != source:
            problems.append("%s: body differs from source lines %d-%d"
                            % (entry["file"], entry["start"], entry["end"]))
    notes_path = os.path.join(outdir, "_notes.md")
    with open(notes_path, encoding="utf-8") as fh:
        notes = fh.read().replace("\r\n", "\n").split("\n")
    if notes and notes[-1] == "":
        notes.pop()
    preserved = [model["lines"][ln - 1] for ln in model["notes"]]
    if notes[-len(preserved):] != preserved:
        problems.append("_notes.md: preserved tail differs from source")
    if problems:
        raise SplitError("written output failed verification:\n  " + "\n  ".join(problems))
    out.append("WRITTEN: %d entry files re-read and compared line-by-line to their "
               "source slices — identical; _notes.md's %d preserved lines "
               "identical and in source order"
               % (len(model["entries"]), len(preserved)))


def write_all(model, out):
    outdir = os.path.join(REPO, OUT_REL)
    os.makedirs(outdir, exist_ok=True)
    seen = {}
    for entry in model["entries"]:
        name = "%s.md" % entry["file"]
        if name in seen:
            raise SplitError("duplicate output file %s (%s and %s)"
                             % (name, seen[name], entry["id"]))
        seen[name] = entry["id"]
        write_lines(os.path.join(outdir, name), render_entry(model, entry))
    notes, n_front, n_added, n_body = render_notes(model)
    write_lines(os.path.join(outdir, "_notes.md"), notes)
    write_lines(os.path.join(outdir, "INDEX.md"), render_index(model))
    write_lines(os.path.join(REPO, SOURCE_REL), render_stub())
    out.append("WROTE: %d entry files, _notes.md (%d front-matter + %d added + %d "
               "preserved lines), INDEX.md (%d rows), and the %s stub"
               % (len(model["entries"]), n_front, n_added, n_body,
                  len(index_rows(model)), SOURCE_REL))
    verify_written(model, outdir, out)


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def build(rev=None, path=None):
    lines = load_lines(rev=rev, path=path)
    model = parse(lines)
    return enrich(model, blame_dates(rev, len(lines)))


def verify_split(rev, out):
    """doccheck --verify-split: re-run the whole accounting against the
    pre-split blob and compare it to what is on disk today."""
    try:
        model = build(rev=rev)
    except subprocess.CalledProcessError:
        raise SplitError("cannot read %s:%s" % (rev, SOURCE_REL))
    accounting(model, out)
    verify_written(model, os.path.join(REPO, OUT_REL), out)


# --------------------------------------------------------------------------
# reading the split back — the surface doccheck validates from here on
# --------------------------------------------------------------------------

def parse_front(path):
    """-> (front-matter dict, body lines). Scalars are JSON, so they decode
    exactly; `members:`/`orphan_rows:` items are JSON objects one per line."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().replace("\r\n", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines or lines[0] != "---":
        raise SplitError("%s: no front matter" % os.path.basename(path))
    try:
        close = lines.index("---", 1)
    except ValueError:
        raise SplitError("%s: front matter is never closed" % os.path.basename(path))
    front, key = {}, None
    for line in lines[1:close]:
        if line.startswith("  - "):
            if key is None or not isinstance(front.get(key), list):
                raise SplitError("%s: stray list item %r" % (path, line[:40]))
            front[key].append(json.loads(line[4:]))
            continue
        name, sep, value = line.partition(": ")
        if not sep:
            if not line.endswith(":"):
                raise SplitError("%s: unparseable front-matter line %r" % (path, line[:60]))
            key = line[:-1]
            front[key] = []
            continue
        key = name
        try:
            front[name] = json.loads(value)
        except ValueError:
            raise SplitError("%s: front-matter value for %r is not JSON: %r"
                             % (path, name, value[:60]))
    return front, lines[close + 1:]


def load_from_dir(outdir=None):
    """-> the same model shape parse() produces, rebuilt from the split files.

    Only the fields INDEX generation and validation need; body lines are kept
    so the heading tag can still be checked against the derived status."""
    outdir = outdir or os.path.join(REPO, OUT_REL)
    entries, by_id, orphans = [], {}, []
    for name in sorted(os.listdir(outdir)):
        if not name.endswith(".md") or name == "INDEX.md":
            continue
        front, body = parse_front(os.path.join(outdir, name))
        if name == "_notes.md":
            for row in front.get("orphan_rows", []):
                orphans.append(row["id"])
                by_id[row["id"]] = row
            continue
        entry = dict(front)
        entry["file"] = name[:-3]
        entry["body"] = body
        entry["kind"] = front.get("kind", "entry")
        entry.setdefault("members", [])
        entry.setdefault("contains", [])
        entries.append(entry)
        by_id[entry["id"]] = entry
        for member in entry["members"]:
            by_id[member["id"]] = member
    entries.sort(key=lambda e: e.get("seq", 0))
    return {"entries": entries, "by_id": by_id, "orphans": orphans}


def main():
    ap = argparse.ArgumentParser(description="BUGS.md -> agent/bugs/ migration")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="print the accounting only")
    mode.add_argument("--write", action="store_true", help="perform the split")
    ap.add_argument("--from-git", metavar="REV",
                    help="read BUGS.md from a git revision instead of the worktree")
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
        print("\nsplit_bugs: ABORTED — %s" % exc)
        return 1
    print("\n".join(out))
    print("split_bugs: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
