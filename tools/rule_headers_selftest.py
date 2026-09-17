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
Rule: Read the header before editing a document that has one.
Rule: Run the checker before committing.
<!-- /RULES -->

Prose that states no duty.
"""

CLEAN_MAP = """# Prompt map

## Must_Read_Header
<!-- RULES -->
Rule: Keep every prompt reachable from this map.
<!-- /RULES -->
"""


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
        "<!-- RULES -->\nRule: A second block is not allowed.\n<!-- /RULES -->\n"
    case("two header blocks in one doc", two_blocks, True,
         "must contain exactly one ordered")

    state = dict(base)
    state["docs/agent/STATE.md"] = "# State\n\nRule: Status is not law.\n"
    case("Rule line in STATE.md", state, True,
         "STATE.md must contain zero Rule lines")

    archived = dict(base)
    archived["docs/archive/SESSION_LOG.md"] = "# Log\n\nRule: History is not law.\n"
    case("Rule line on an archived surface", archived, True,
         "forbidden on generated or archived surfaces")

    generated = dict(base)
    generated["docs/agent/bugs/INDEX.md"] = "GENERATED\n\nRule: Not here either.\n"
    case("Rule line on a generated index", generated, True,
         "forbidden on generated or archived surfaces")

    shouty = dict(base)
    shouty["CLAUDE.md"] = CLEAN_KERNEL.replace(
        "Rule: Run the checker before committing.",
        "Rule: You MUST run the checker before committing.")
    case("malformed — shouting (MUST)", shouty, True, "malformed canonical Rule")

    bolded = dict(base)
    bolded["CLAUDE.md"] = CLEAN_KERNEL.replace(
        "Rule: Run the checker before committing.",
        "Rule: **Run** the checker before committing.")
    case("malformed — bold", bolded, True, "malformed canonical Rule")

    emoji = dict(base)
    emoji["CLAUDE.md"] = CLEAN_KERNEL.replace(
        "Rule: Run the checker before committing.",
        "Rule: ⛔ Run the checker before committing.")
    case("malformed — emoji", emoji, True, "malformed canonical Rule")

    nofullstop = dict(base)
    nofullstop["CLAUDE.md"] = CLEAN_KERNEL.replace(
        "Rule: Run the checker before committing.",
        "Rule: Run the checker before committing")
    case("malformed — no terminating period", nofullstop, True,
         "malformed canonical Rule")

    dupe = dict(base)
    dupe["docs/agent/prompts/README.md"] = CLEAN_MAP.replace(
        "Rule: Keep every prompt reachable from this map.",
        "Rule: Run   the checker   before committing.")
    case("duplicate duty across two headers (whitespace/case folded)", dupe,
         True, "duplicate canonical duties")

    oversize = dict(base)
    filler = "\n".join(
        "Rule: Pad the header past its hard cap with sentence number %d." % i
        for i in range(120))
    oversize["CLAUDE.md"] = CLEAN_KERNEL.replace("<!-- /RULES -->",
                                                 filler + "\n<!-- /RULES -->")
    case("kernel header over its hard byte cap", oversize, True,
         "hard cap is")

    # A WARN, not a RED — the gate still returns ok, so this case asserts the
    # line appears rather than asserting failure. Proving the distinction is
    # the point: a misplaced rule is reported without blocking a commit.
    stray = dict(base)
    stray["docs/agent/WORKFLOW.md"] = "# Workflow\n\nRule: A stray duty in prose.\n"
    case("Rule line outside any header is WARNed, not RED", stray, False,
         "RULE PLACEMENT: WARN")

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
