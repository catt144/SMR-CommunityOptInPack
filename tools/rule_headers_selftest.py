#!/usr/bin/env python
"""Falsifier for doccheck's RULES HEADERS / RULE PLACEMENT gate.

WHY THIS EXISTS. The donor shipped a gate DEAD: a `cwd` vs `REPO` mistake raised
a NameError that fell into a bare `except Exception` and rendered as a benign
`SKIPPED`. It would have skipped silently forever. A gate that passes on a clean
tree has proved nothing — it has to be shown FIRING on a known-bad case, one
case per red it claims to raise.

Method: `sys.path.insert(0, "tools")` then `import doccheck`, repoint its REPO
at a scratch git repository, and call `check_rule_headers` directly. Reusing
doccheck's own parsers is the point — a falsifier that re-implements the parser
tests the re-implementation.

    python tools/rule_headers_selftest.py          # exit 0 = every case fired

It also carries the legs for `check_checklist`, the gate on the owner's list
under its own Must_Read_Header; the donor has no falsifier for that gate. And the
legs for `check_parked`, the per-entry gate on docs/PARKED_MODULES.md (this repo only).

Nothing here touches the live tree: every fixture is written under a temporary
directory that is removed on the way out.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doccheck  # noqa: E402 — the path insert above is the point

# ⛔ SCRUB GIT'S PER-INVOCATION ENVIRONMENT BEFORE ANYTHING ELSE. doccheck runs
# this falsifier and the pre-commit hook runs doccheck, so in a commit every
# subprocess here would otherwise inherit GIT_INDEX_FILE / GIT_DIR pointing at
# the temporary index git is building the commit from. Two distinct failures
# came out of that: the scratch repo's `git add` wrote fixtures into the real
# commit's index (killing it with `invalid object … for` an untouched path),
# and the gate's own `git ls-files` enumerated the REAL tree while claiming to
# test the scratch one — a falsifier passing for the wrong reason.
for _key in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[_key]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

# A minimal well-formed kernel. Cases mutate a copy of this.
CLEAN_KERNEL = """# Scratch kernel

## Must_Read_Header
<!-- RULES -->
Rule: Read the header before editing a document that has one. [A3: pass]
Rule: Run the checker before committing. [A3: pass]
<!-- /RULES -->

Prose that states no duty.
"""

CLEAN_MAP = """# Prompt map

## Must_Read_Header
<!-- RULES -->
Rule: Keep every prompt reachable from this map. [A3: pass]
<!-- /RULES -->
"""

# Every fixture Rule: line carries the tag, so each case below plants exactly
# one defect; `untagged` plants the missing tag itself.
CHECKER = "Rule: Run the checker before committing. [A3: pass]"


def clean_git_env():
    """An environment with git's per-invocation variables REMOVED.

    ⛔ THIS IS LOAD-BEARING, AND IT COST A COMMIT TO LEARN. doccheck runs this
    falsifier, and the pre-commit hook runs doccheck — so inside a commit these
    subprocesses inherit GIT_INDEX_FILE, GIT_DIR and friends, which git sets to
    the TEMPORARY index it is building the commit from. `git add` in the scratch
    repo then wrote this file's fixtures into that temporary index, and the
    commit died with `invalid object … for 'docs/agent/prompts/README.md'` —
    naming a path nothing here had touched. A scratch repo is only isolated if
    its environment is too.
    """
    env = dict(os.environ)
    for key in list(env):
        if key.startswith("GIT_"):
            del env[key]
    return env


def build(tmp, files):
    """Write `files` into a fresh git repo and return its path."""
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo, exist_ok=True)
    env = clean_git_env()
    subprocess.run(["git", "init", "-q", repo], check=True,
                   capture_output=True, env=env)
    for rel, text in files.items():
        path = os.path.join(repo, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    # The placement half enumerates tracked Markdown, so the fixtures must be
    # staged. `git add` alone is enough — check_rule_headers never reads a blob.
    subprocess.run(["git", "-C", repo, "add", "-A"], check=True,
                   capture_output=True, env=env)
    return repo


def run_gate(repo, required=("CLAUDE.md", "docs/agent/prompts/README.md")):
    """Call the real gate against `repo`, returning (ok, output lines)."""
    saved_repo = doccheck.REPO
    saved_docs = doccheck.RULE_HEADER_DOCS
    try:
        doccheck.REPO = repo
        doccheck.RULE_HEADER_DOCS = required
        out = []
        ok = doccheck.check_rule_headers(out)
        return ok, out
    finally:
        doccheck.REPO = saved_repo
        doccheck.RULE_HEADER_DOCS = saved_docs


def main():
    base = {"CLAUDE.md": CLEAN_KERNEL,
            "docs/agent/prompts/README.md": CLEAN_MAP}
    failures = []
    results = []

    def case(name, files, want_red, needle, required=None):
        tmp = tempfile.mkdtemp(prefix="rulehdr_")
        try:
            repo = build(tmp, files)
            kwargs = {"required": required} if required else {}
            ok, out = run_gate(repo, **kwargs)
            text = "\n".join(out)
            red_ok = (not ok) if want_red else ok
            hit = needle in text
            passed = red_ok and hit
            results.append((name, passed, text.replace("\n", " | ")))
            if not passed:
                failures.append(
                    "%s: wanted %s containing %r, got ok=%s\n    %s"
                    % (name, "RED" if want_red else "GREEN", needle, ok, text))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # ---- NEGATIVE CONTROL -------------------------------------------------
    # If this does not pass, every RED below is meaningless: the gate might be
    # failing for a reason that has nothing to do with the mutation.
    case("negative control (clean fixture passes)", dict(base), False,
         "RULES HEADERS: PASS")

    # ---- one case per red the gate claims ---------------------------------
    missing = dict(base)
    missing["CLAUDE.md"] = "# Scratch kernel\n\nNo header at all.\n"
    case("required doc has no header block", missing, True,
         "must contain exactly one ordered")

    two_blocks = dict(base)
    two_blocks["CLAUDE.md"] = CLEAN_KERNEL + "\n## Must_Read_Header\n" \
        "<!-- RULES -->\nRule: A second block is not allowed. [A3: pass]\n" \
        "<!-- /RULES -->\n"
    case("two header blocks in one doc", two_blocks, True,
         "must contain exactly one ordered")

    state = dict(base)
    state["docs/agent/STATE.md"] = "# State\n\nRule: Status is not law. [A3: pass]\n"
    case("Rule line in STATE.md", state, True,
         "STATE.md must contain zero Rule lines")

    archived = dict(base)
    archived["docs/archive/SESSION_LOG.md"] = \
        "# Log\n\nRule: History is not law. [A3: pass]\n"
    case("Rule line on an archived surface", archived, True,
         "forbidden on generated or archived surfaces")

    generated = dict(base)
    generated["docs/agent/bugs/INDEX.md"] = \
        "GENERATED\n\nRule: Not here either. [A3: pass]\n"
    case("Rule line on a generated index", generated, True,
         "forbidden on generated or archived surfaces")

    shouty = dict(base)
    shouty["CLAUDE.md"] = CLEAN_KERNEL.replace(
        CHECKER, "Rule: You MUST run the checker before committing. [A3: pass]")
    case("malformed — shouting (MUST)", shouty, True, "malformed canonical Rule")

    bolded = dict(base)
    bolded["CLAUDE.md"] = CLEAN_KERNEL.replace(
        CHECKER, "Rule: **Run** the checker before committing. [A3: pass]")
    case("malformed — bold", bolded, True, "malformed canonical Rule")

    emoji = dict(base)
    emoji["CLAUDE.md"] = CLEAN_KERNEL.replace(
        CHECKER, "Rule: ⛔ Run the checker before committing. [A3: pass]")
    case("malformed — emoji", emoji, True, "malformed canonical Rule")

    nofullstop = dict(base)
    nofullstop["CLAUDE.md"] = CLEAN_KERNEL.replace(
        CHECKER, "Rule: Run the checker before committing [A3: pass]")
    case("malformed — no terminating period", nofullstop, True,
         "malformed canonical Rule")

    untagged = dict(base)
    untagged["CLAUDE.md"] = CLEAN_KERNEL.replace(
        CHECKER, "Rule: Run the checker before committing.")
    case("malformed — no [A3: pass] tag", untagged, True,
         "malformed canonical Rule")

    dupe = dict(base)
    dupe["docs/agent/prompts/README.md"] = CLEAN_MAP.replace(
        "Rule: Keep every prompt reachable from this map. [A3: pass]",
        "Rule: Run   the checker   before committing. [A3: pass]")
    case("duplicate duty across two headers (whitespace/case folded)", dupe,
         True, "duplicate canonical duties")

    oversize = dict(base)
    filler = "\n".join(
        "Rule: Pad the header past its hard cap with sentence number %d. [A3: pass]"
        % i for i in range(120))
    oversize["CLAUDE.md"] = CLEAN_KERNEL.replace("<!-- /RULES -->",
                                                 filler + "\n<!-- /RULES -->")
    case("kernel header over its hard byte cap", oversize, True,
         "hard cap is")

    # A WARN, not a RED — the gate still returns ok, so this case asserts the
    # line appears rather than asserting failure. Proving the distinction is
    # the point: a misplaced rule is reported without blocking a commit.
    stray = dict(base)
    stray["docs/agent/WORKFLOW.md"] = "# Workflow\n\nRule: A stray duty in prose. [A3: pass]\n"
    case("Rule line outside any header is WARNed, not RED", stray, False,
         "RULE PLACEMENT: WARN")

    # ---- CHECKLIST gate (docs/PLAYTEST_CHECKLIST.md) ------------------------
    # The donor has no falsifier for its check_checklist, so its legs live here.
    # Each leg commits a list at a chosen date into a scratch repo, so the gate's
    # git pin reads real history, then optionally rewrites the working copy.
    import datetime
    today = datetime.date.today()

    def day(offset):
        return (today + datetime.timedelta(days=offset)).isoformat()

    def checklist(heading):
        return ("# List\n\n## Must_Read_Header\n<!-- RULES -->\n"
                "Rule: Admit only the owner's next actions. [A3: pass]\n"
                "<!-- /RULES -->\n\nIntro.\n\n## Decide\n\n"
                "%s\nIs this the question?\n- one bullet\n"
                "Home: `docs/agent/bugs/D01.md`\n" % heading)

    def list_case(name, committed, commit_day, working, want_red, needle):
        tmp = tempfile.mkdtemp(prefix="checklist_")
        env = clean_git_env()
        try:
            repo = build(tmp, {"docs/agent/bugs/D01.md": "# D01\n"})
            path = os.path.join(repo, "docs", "PLAYTEST_CHECKLIST.md")
            # A base commit, so a leg with nothing committed still reads a real
            # (empty) history rather than failing on "git history unread".
            benv = dict(env, GIT_AUTHOR_DATE="%sT12:00:00" % day(-60),
                        GIT_COMMITTER_DATE="%sT12:00:00" % day(-60))
            subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t",
                            "commit", "-q", "-m", "base"],
                           check=True, capture_output=True, env=benv)
            if committed is not None:
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(committed)
                stamp = "%sT12:00:00" % commit_day
                cenv = dict(env, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
                subprocess.run(["git", "-C", repo, "add", "-A"], check=True,
                               capture_output=True, env=cenv)
                subprocess.run(["git", "-C", repo, "-c", "user.name=t",
                                "-c", "user.email=t@t", "commit", "-q", "-m", "x"],
                               check=True, capture_output=True, env=cenv)
            if working is not None:
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(working)
            saved = doccheck.REPO
            try:
                doccheck.REPO = repo
                out = []
                ok = doccheck.check_checklist(out)
            finally:
                doccheck.REPO = saved
            text = "\n".join(out)
            passed = (((not ok) if want_red else ok) and needle in text
                      and "history unread" not in text)
            results.append((name, passed, text.replace("\n", " | ")))
            if not passed:
                failures.append("%s: wanted %s containing %r, got ok=%s\n    %s"
                                % (name, "RED" if want_red else "GREEN", needle, ok, text))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    good = checklist("### OI-01 · opened %s" % day(0))
    list_case("checklist negative control (well-formed item passes)",
              good, day(0), None, False, "CHECKLIST: PASS")
    list_case("checklist — malformed heading", good, day(0),
              checklist("### OI-1 opened %s" % day(0)), True, "an item heading is")
    list_case("checklist — fix pack ck id is not this list's id", None, None,
              checklist("### ck01 · opened %s" % day(0)), True, "an item heading is")
    old = checklist("### OI-01 · opened %s" % day(-40))
    list_case("checklist — >30-day item without launch", old, day(-40), None,
              True, "days old")
    old_launch = checklist("### OI-01 · opened %s · launch" % day(-40))
    list_case("checklist — >30-day launch item passes", old_launch, day(-40), None,
              False, "CHECKLIST: PASS")
    pinned = checklist("### OI-01 · opened %s" % day(-5))
    list_case("checklist — committed item back-dated", pinned, day(-5),
              checklist("### OI-01 · opened %s" % day(-10)), True, "differs from")
    list_case("checklist — new item back-dated", None, None,
              checklist("### OI-02 · opened %s" % day(-10)), True, "is new")

    # ---- PARKED gate (docs/PARKED_MODULES.md) ------------------------------
    # One leg per RED the gate claims, each planting exactly one defect into an
    # otherwise well-formed file; the controls prove a 10-line entry and the
    # header's own markup (the RULES markers, `<name>` in a code span) pass.
    parked_prose = ("# Parked modules\n\nIntro prose.\n\n## Must_Read_Header\n"
                    "<!-- RULES -->\n"
                    "Rule: Write each entry as `### <name> · parked <date>`. [A3: pass]\n"
                    "<!-- /RULES -->\n\n## Entries\n\n")
    fields = ["What: A module that does one thing.",
              "Scope: full module (D06)",
              "Revives by: an owner ruling.",
              "Evidence: docs/agent/bugs/D06.md · docs/agent/reports/R.md",
              "Basic summary: One plain sentence."]

    def entry(name="Alpha", date=None, body=None):
        return "\n".join(["### %s · parked %s" % (name, date or day(-1))]
                         + (fields if body is None else body))

    def parked_file(*entries, gap="\n\n", prose=parked_prose):
        return prose + gap.join(entries) + "\n"

    ten = entry(body=fields + ["continuation %d of the summary." % i for i in range(1, 5)])
    eleven = entry(body=fields + ["continuation %d of the summary." % i for i in range(1, 6)])

    def parked_case(name, text, want_red, needle, extra=()):
        tmp = tempfile.mkdtemp(prefix="parked_")
        try:
            repo = os.path.join(tmp, "repo")
            files = {"docs/agent/bugs/D06.md": "# D06\n",
                     "docs/agent/reports/R.md": "# R\n",
                     "CLAUDE.md": "# kernel\n",
                     "docs/PARKED_MODULES.md": text}
            files.update({rel: "# x\n" for rel in extra})
            for rel, body in files.items():
                path = os.path.join(repo, *rel.split("/"))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(body)
            saved = doccheck.REPO
            try:
                doccheck.REPO = repo
                out = []
                ok = doccheck.check_parked(out)
            finally:
                doccheck.REPO = saved
            text_out = "\n".join(out)
            # A RED leg must fire ONLY the planted defect, or it proves nothing
            # about which condition the gate caught.
            single = (not want_red) or "RED  1 violation(s)" in text_out
            passed = ((not ok) if want_red else ok) and needle in text_out and single
            results.append((name, passed, text_out.replace("\n", " | ")))
            if not passed:
                failures.append("%s: wanted %s containing %r, got ok=%s\n    %s"
                                % (name, "RED" if want_red else "GREEN", needle, ok, text_out))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def swap(old, new):
        """The clean pair of entries with one field line replaced."""
        return parked_file(entry(), entry("Beta", body=[new if f == old else f for f in fields]))

    def add(line, after="Basic summary: One plain sentence."):
        """The clean pair with `line` inserted after the named field of Beta."""
        body = []
        for f in fields:
            body.append(f)
            if f == after:
                body.append(line)
        return parked_file(entry(), entry("Beta", body=body))

    parked_case("parked negative control (two clean entries pass)",
                parked_file(entry(), entry("Beta")), False, "PARKED: PASS")
    parked_case("parked — a 10-line entry passes", parked_file(ten), False, "PARKED: PASS")
    parked_case("parked — an 11-line entry fails", parked_file(eleven), True, "11 lines, cap 10")
    parked_case("parked — malformed heading",
                parked_file(entry(), "### Beta parked %s\n" % day(-1) + "\n".join(fields)),
                True, "an entry heading is")
    parked_case("parked — invalid date", parked_file(entry(date="2026-02-30")),
                True, "not a real date")
    parked_case("parked — future date", parked_file(entry(date=day(3))), True, "in the future")
    parked_case("parked — blank line inside an entry",
                add("", after="Scope: full module (D06)"), True, "blank line inside an entry")
    parked_case("parked — two blank lines between entries",
                parked_file(entry(), entry("Beta"), gap="\n\n\n"), True, "exactly one blank line")
    parked_case("parked — no blank line between entries",
                parked_file(entry(), entry("Beta"), gap="\n"), True, "exactly one blank line")
    parked_case("parked — line over 100 characters",
                add("x" * 101), True, "101 characters, cap 100")
    parked_case("parked — entry over 1,024 bytes",
                parked_file(entry(body=fields + ["€" * 99] * 4)), True,
                "without its Evidence line, cap 1024")
    parked_case("parked — field missing",
                parked_file(entry(body=[f for f in fields if not f.startswith("Scope:")])),
                True, "fields must be")
    parked_case("parked — field duplicated", add("What: A second what."), True, "fields must be")
    parked_case("parked — fields out of order",
                parked_file(entry(body=[fields[1], fields[0]] + fields[2:])),
                True, "fields must be")
    parked_case("parked — stray line before the summary",
                add("A stray note.", after="What: A module that does one thing."),
                True, "only a field line")
    parked_case("parked — Scope off its template",
                swap("Scope: full module (D06)", "Scope: most of it, see D06"),
                True, "Scope is")
    for label, line in (("HTML comment", "<!-- hidden -->"),
                        ("<details>", "<details>hidden</details>"),
                        ("<br>", "text<br>more"),
                        ("any tag", "a <b>bold</b> word")):
        parked_case("parked — %s in an entry" % label, add(line), True, "carries HTML")
    parked_case("parked — HTML in the prose above the entries",
                parked_file(entry(), prose=parked_prose.replace(
                    "Intro prose.", "Intro <details>hidden</details> prose.")),
                True, "carries HTML")
    for label, line in (("code fence", "```"), ("table row", "| a | b |"),
                        ("blockquote", "> quoted"), ("bullet -", "- item"),
                        ("bullet *", "* item"), ("bullet 1.", "1. item"),
                        ("footnote", "see note[^1]"), ("sub-heading", "#### More")):
        parked_case("parked — %s in an entry" % label, add(line), True, "inside an entry")
    for code in (0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x2060, 0xFEFF, 0x00AD):
        parked_case("parked — U+%04X in an entry" % code,
                    add("Basic words%sthat hide." % chr(code)), True, "invisible or zero-width")
    parked_case("parked — U+200B in the prose",
                parked_file(entry(), prose=parked_prose.replace("Intro", "In" + chr(0x200B) + "tro")),
                True, "invisible or zero-width")
    parked_case("parked — evidence path missing",
                swap(fields[3], "Evidence: docs/agent/bugs/D99.md"), True, "does not exist")
    parked_case("parked — evidence outside the agent record folders",
                swap(fields[3], "Evidence: CLAUDE.md"), True, "not a bare path")
    parked_case("parked — evidence escaping by ..",
                swap(fields[3], "Evidence: docs/agent/bugs/../../../CLAUDE.md"),
                True, "not a bare path")

    # ---- the Evidence ruling (owner, 2026-09-18): paths only, 400 columns,
    # at most 8 paths, and outside the 1,024-byte entry count.
    def long_evidence(total):
        """-> (Evidence line of exactly `total` characters, the 4 paths it names)."""
        room = total - len("Evidence: ") - 3 * len(" · ")
        sizes = [room // 4] * 3 + [room - 3 * (room // 4)]
        paths = ["docs/agent/reports/" + ch * (n - len("docs/agent/reports/.md")) + ".md"
                 for ch, n in zip("abcd", sizes)]
        line = "Evidence: " + " · ".join(paths)
        assert len(line) == total, (len(line), total)
        return line, paths

    ev400, paths400 = long_evidence(400)
    ev401, paths401 = long_evidence(401)
    parked_case("parked — a 400-character path-only Evidence line passes",
                swap(fields[3], ev400), False, "PARKED: PASS", extra=paths400)
    parked_case("parked — a 401-character Evidence line fails",
                swap(fields[3], ev401), True, "401 characters, cap 400", extra=paths401)
    for label, line in (("a path plus a word", "Evidence: docs/agent/bugs/D06.md record"),
                        ("a path with a comment", "Evidence: docs/agent/bugs/D06.md (the record)"),
                        ("a trailing note", "Evidence: docs/agent/bugs/D06.md · see also D07"),
                        ("a backticked path", "Evidence: `docs/agent/bugs/D06.md`")):
        parked_case("parked — Evidence with %s fails" % label, swap(fields[3], line),
                    True, "not a bare path")
    parked_case("parked — 8 Evidence paths pass",
                swap(fields[3], "Evidence: " + " · ".join(["docs/agent/bugs/D06.md"] * 8)),
                False, "PARKED: PASS")
    parked_case("parked — 9 Evidence paths fail",
                swap(fields[3], "Evidence: " + " · ".join(["docs/agent/bugs/D06.md"] * 9)),
                True, "9 evidence paths, cap 8")
    parked_case("parked — Evidence continued onto a second line fails",
                add("docs/agent/reports/R.md", after=fields[3]), True, "only a field line")

    def byte_entry(target):
        """-> a 10-line entry whose lines other than Evidence total `target` bytes."""
        head = ["### Alpha · parked %s" % day(-1)] + fields[:3]
        slots = [("Basic summary: ", 85)] + [("", 100)] * 4
        fixed = sum(len(x.encode("utf-8")) for x in head) + len("Basic summary: ")
        need = target - fixed - (len(head) + len(slots) - 1)      # the joining newlines
        shares = [need // len(slots)] * (len(slots) - 1)
        shares.append(need - sum(shares))
        body = []
        for (prefix, cap), share in zip(slots, shares):
            euros, rest = divmod(share, 3)
            assert 0 < euros + rest <= cap, (share, cap)
            body.append(prefix + "€" * euros + "a" * rest)
        text = "\n".join(head[1:] + [ev400] + body)
        assert len(("\n".join(head + body)).encode("utf-8")) == target
        return head[0] + "\n" + text

    parked_case("parked — 1,024 B besides a 400-column Evidence line passes",
                parked_file(byte_entry(1024)), False, "PARKED: PASS", extra=paths400)
    parked_case("parked — 1,025 B besides the Evidence line fails",
                parked_file(byte_entry(1025)), True,
                "1025 bytes without its Evidence line, cap 1024", extra=paths400)

    width = max(len(n) for n, _, _ in results)
    for name, passed, _text in results:
        print("  %-*s  %s" % (width, name, "FIRED" if passed else "DID NOT FIRE"))
    print("")
    if failures:
        print("rule_headers_selftest: RED — %d case(s) did not behave as claimed"
              % len(failures))
        for f in failures:
            print("  " + f)
        return 1
    print("rule_headers_selftest: GREEN — %d case(s), including the negative "
          "control" % len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
