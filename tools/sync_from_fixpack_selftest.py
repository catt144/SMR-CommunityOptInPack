#!/usr/bin/env python
"""Falsifier for sync_from_fixpack's --tools pass, kit-doc mirror check and citation resolver.

WHY THIS EXISTS. The --tools pass is silent by design: a declared row hides its
tool. A pass that is silent because it works and one that is silent because it
stopped looking print the same nothing. So each undeclared shape is planted in a
scratch pair of trees and must be REPORTED, and a clean pair must stay quiet —
the control that stops an always-firing pass from passing.

Method: `import sync_from_fixpack`, repoint its REPO, DONOR, LAST_SYNC and
declared tables at scratch trees, and call `pass_tools` / `pass_mirror`
directly — the real passes, not a re-implementation.

    python tools/sync_from_fixpack_selftest.py        # exit 0 = every leg fired

Legs: the control (identical, declared-adapted, declared-not-ported,
declared-local-only and a CRLF-only difference all silent); an undeclared new
donor tool; an undeclared differing tool; an undeclared tool only here; a
declared adaptation that stops differing; a donor change to a declared
adaptation since LAST_SYNC (a scratch git donor); and each mirrored kit doc
drifting or missing. Citation legs (`citation_legs`): every place the resolver
looks (TestKit, game-source subfolders, tools/devmods, the train asset repo, a
moved path, this repo's git history, the donor's history) is proved on one
citation it now resolves AND one genuinely gone that it still reports; each
declared table (CITERS_/CITATIONS_BY_DESIGN, CITATIONS_ABSENT) hides its own row
and only that row. Nothing touches the live tree or the donor: every fixture
lives under a temporary directory removed on the way out.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync_from_fixpack as sync  # noqa: E402 — the path insert above is the point

# ⛔ SCRUB GIT'S PER-INVOCATION ENVIRONMENT FIRST (rule_headers_selftest.py has
# the incident): doccheck runs this under the pre-commit hook, and an inherited
# GIT_DIR would point the scratch donor's git at the real commit in progress.
for _key in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[_key]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

MIRRORS = {"tools/TESTKIT.md": "kit", "tools/SMRTK.md": "toolkit"}

# name -> (here bytes, donor bytes); None = absent on that side.
BASE = {
    "same.py": (b"x = 1\n", b"x = 1\n"),
    "crlf.py": (b"a = 1\nb = 2\n", b"a = 1\r\nb = 2\r\n"),
    "adapted.py": (b"TOKEN = 'here'\n", b"TOKEN = 'there'\n"),
    "hooks/pre-commit": (b"# this repo\n", b"# the donor\n"),
    "casework.py": (None, b"# a donor desk harness\n"),
    "local.py": (b"# ours\n", None),
}
TABLES = dict(
    TOOLS_ADAPTED={"adapted.py": "scratch", "hooks/pre-commit": "scratch"},
    TOOLS_NOT_PORTED={"casework.py": "scratch"},
    TOOLS_LOCAL_ONLY={"local.py": "scratch"},
    MIRRORED_DOCS=MIRRORS,
)
FINDING = ("DIFFERS", "NEW THERE", "ONLY HERE", "RECHECK", "NOTE", "DRIFT",
           "MISSING", "GONE THERE", "⚠️")


def write(root, rel, data):
    path = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)


def git(repo, *args):
    subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t",
                    "-c", "core.autocrlf=false"] + list(args),
                   check=True, capture_output=True, env=dict(os.environ))


def build(tmp, tools, mirrors=None, git_donor=True):
    """Two scratch trees; returns (here, there)."""
    here, there = os.path.join(tmp, "here"), os.path.join(tmp, "there")
    for name, (mine, theirs) in tools.items():
        if mine is not None:
            write(here, "tools/" + name, mine)
        if theirs is not None:
            write(there, "tools/" + name, theirs)
    for rel, (mine, theirs) in (mirrors or {r: (b"kit\n", b"kit\n")
                                            for r in MIRRORS}).items():
        if mine is not None:
            write(here, rel, mine)
        if theirs is not None:
            write(there, rel, theirs)
    if git_donor:
        subprocess.run(["git", "init", "-q", there], check=True, capture_output=True)
        git(there, "add", "-A")
        git(there, "commit", "-q", "-m", "base")
    return here, there


def run(here, there, last_sync="HEAD"):
    saved = {k: getattr(sync, k) for k in
             ("REPO", "DONOR", "LAST_SYNC", *TABLES)}
    try:
        sync.REPO, sync.DONOR, sync.LAST_SYNC = here, there, last_sync
        for k, v in TABLES.items():
            setattr(sync, k, v)
        out = []
        found = (sync.pass_tools(out), sync.pass_mirror(out))
    finally:
        for k, v in saved.items():
            setattr(sync, k, v)
    return found, out


results, failures = [], []


def leg(name, tools, needle, subject=None, mirrors=None, git_donor=True, after=None):
    """needle None = the clean control: no finding line, both passes False.

    The donor is a scratch git repo with LAST_SYNC at its base commit, so the
    RECHECK half runs on every leg; `after` then changes the donor past it."""
    tmp = tempfile.mkdtemp(prefix="syncself_")
    try:
        here, there = build(tmp, tools, mirrors, git_donor)
        last = "HEAD"
        if git_donor:
            last = subprocess.run(["git", "-C", there, "rev-parse", "HEAD"], check=True,
                                  capture_output=True, text=True).stdout.strip()
        if after:
            after(here, there)
        found, out = run(here, there, last)
        text = "\n".join(out)
        if needle is None:
            bad = [ln for ln in out if ln.strip().startswith(FINDING)]
            ok = found == (False, False) and not bad and "PASS - nothing undeclared" in text
        else:
            hit = [ln for ln in out if ln.strip().startswith(needle)
                   and (subject is None or subject in ln)]
            # NOTE is reported but, as in the facts pass, not a --strict finding;
            # a RECHECK that could not run leaves the pass SKIPPED (None), never clean.
            if needle == "NOTE":
                ok = bool(hit)
            elif needle == "⚠️":
                ok = bool(hit) and found[0] is None
            else:
                ok = bool(hit) and any(found)
        results.append((name, ok))
        if not ok:
            failures.append("%s: wanted %s%s; got %r\n%s"
                            % (name, needle or "silence",
                               " for " + subject if subject else "", found, text))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


CITE_TABLES = ("REPO", "DONOR", "SRC_ARCHIVE", "TESTKIT", "TRAIN_ASSETS",
               "CITERS_BY_DESIGN", "CITATIONS_BY_DESIGN", "CITATIONS_ABSENT",
               "TOOLS_NOT_PORTED", "DONOR_OWNED_FILES")


def citation_legs():
    """Plant every place a citation can resolve, plus a gone twin of each, and read
    the REAL pass_citations output. Each pair: the present name must leave the
    listing (and be counted), the gone name must still be reported."""
    tmp = tempfile.mkdtemp(prefix="syncself_cite_")
    saved = {k: getattr(sync, k) for k in CITE_TABLES}
    try:
        here, there = os.path.join(tmp, "here"), os.path.join(tmp, "there")
        kit, src, assets = (os.path.join(tmp, n) for n in ("kit", "src", "assets"))
        cites = [
            "kit_probe.lua", "kit_gone.lua",                    # TestKit
            "Sub/Mod.lua", "Sub/Missing.lua",                   # game subfolder
            "Code/dev_entity.lua", "Code/dev_missing.lua",      # tools/devmods
            "asset_tool.py", "asset_missing.py",                # train assets
            "used_up.md", "never_existed.md",                   # this repo's history
            "donor_used_up.md", "donor_never.md",               # the donor's history
            "docs/old/moved.md", "docs/old/nowhere.md",         # moved by name
            "declared_donor.md", "undeclared_donor.md",         # CITATIONS_BY_DESIGN
            "fact_donor.md", "mixed_donor.md",                  # CITERS_BY_DESIGN
            "absent_ok.md", "absent_gone.md",                   # CITATIONS_ABSENT
            "C47.md",                                           # a donor id's file
        ]
        body = "\n".join("`%s`" % c for c in cites if c != "fact_donor.md")
        write(here, "docs/agent/WORKFLOW.md", b"# w\n")
        write(here, "docs/agent/moved.md", b"# moved here\n")
        write(here, "docs/README.md", body.encode())
        write(here, "docs/agent/facts/EF-900.md",
              b"`fact_donor.md` `mixed_donor.md`\n")
        write(here, "tools/devmods/m/Code/dev_entity.lua", b"x\n")
        write(kit, "Code/kit_probe.lua", b"x\n")
        write(src, "1.1.0.1/Src/Sub/Mod.lua", b"x\n")
        write(assets, "blender/asset_tool.py", b"x\n")
        for name in ("declared_donor.md", "undeclared_donor.md", "fact_donor.md",
                     "mixed_donor.md", "donor_used_up.md"):
            write(there, "docs/" + name, b"x\n")
        # history: a file committed here and deleted, and one in the donor
        write(here, "docs/agent/prompts/used_up.md", b"x\n")
        for repo, gone in ((here, "docs/agent/prompts/used_up.md"),
                           (there, "docs/donor_used_up.md")):
            if repo is there:
                write(there, gone, b"x\n")
            subprocess.run(["git", "init", "-q", repo], check=True, capture_output=True)
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "base")
            os.remove(os.path.join(repo, *gone.split("/")))
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "used up")
        sync.REPO, sync.DONOR = here, there
        sync.SRC_ARCHIVE, sync.TESTKIT, sync.TRAIN_ASSETS = src, kit, assets
        sync.CITERS_BY_DESIGN = {"docs/agent/facts/": "scratch"}
        sync.CITATIONS_BY_DESIGN = {"declared_donor.md": "scratch"}
        sync.CITATIONS_ABSENT = {"absent_ok.md": "scratch"}
        sync.TOOLS_NOT_PORTED = {}
        sync._indexes.clear()
        out = []
        sync.pass_citations(out)
        text = "\n".join(out)

        def listed(name, kind):
            return any(ln.strip().startswith(kind) and (" %s " % name) in ln + " "
                       for ln in out)

        def check(label, ok):
            results.append((label, bool(ok)))
            if not ok:
                failures.append("%s\n%s" % (label, text))

        for present, gone, place in (
                ("kit_probe.lua", "kit_gone.lua", "TestKit"),
                ("Sub/Mod.lua", "Sub/Missing.lua", "game-source subfolder"),
                ("Code/dev_entity.lua", "Code/dev_missing.lua", "tools/devmods"),
                ("asset_tool.py", "asset_missing.py", "train asset repo"),
                ("used_up.md", "never_existed.md", "this repo's git history"),
                ("donor_used_up.md", "donor_never.md", "the donor's git history"),
                ("docs/old/moved.md", "docs/old/nowhere.md", "a moved path")):
            check("citation resolver: %s resolves %s" % (place, present),
                  not listed(present, "NOWHERE") and not listed(present, "DONOR HAS"))
            check("citation resolver: %s still reports the gone %s" % (place, gone),
                  listed(gone, "NOWHERE"))
        check("declared CITATIONS_BY_DESIGN row hides its own row",
              not listed("declared_donor.md", "DONOR HAS"))
        check("an undeclared donor-has-it row is still listed",
              listed("undeclared_donor.md", "DONOR HAS"))
        check("CITERS_BY_DESIGN hides a citation cited only by the declared citer",
              not listed("fact_donor.md", "DONOR HAS"))
        check("CITERS_BY_DESIGN never hides a citation with a citer outside the class",
              listed("mixed_donor.md", "DONOR HAS"))
        check("declared CITATIONS_ABSENT row hides its own row",
              not listed("absent_ok.md", "NOWHERE"))
        check("an undeclared absent row is still reported", listed("absent_gone.md", "NOWHERE"))
        check("a donor id's entry file is donor-owned, not listed",
              not listed("C47.md", "DONOR HAS") and not listed("C47.md", "NOWHERE"))
    finally:
        for k, v in saved.items():
            setattr(sync, k, v)
        sync._indexes.clear()
        shutil.rmtree(tmp, ignore_errors=True)


def with_(**changes):
    tools = dict(BASE)
    for k, v in changes.items():
        tools[k.replace("__", "/").replace("_py", ".py")] = v
    return tools


def main():
    leg("control: declared, identical and CRLF-only rows are silent", BASE, None)
    leg("undeclared new donor tool is reported", with_(newtool_py=(None, b"# new\n")),
        "NEW THERE", "newtool.py")
    leg("undeclared differing tool is reported", with_(same_py=(b"x = 1\n", b"x = 2\n")),
        "DIFFERS", "same.py")
    leg("undeclared tool only here is reported", with_(stray_py=(b"# mine\n", None)),
        "ONLY HERE", "stray.py")
    leg("declared adaptation that stops differing is reported",
        with_(adapted_py=(b"TOKEN = 'there'\n", b"TOKEN = 'there'\r\n")),
        "NOTE", "adapted.py")
    leg("declared not-ported tool that got ported is reported",
        with_(casework_py=(b"# a donor desk harness\n", b"# a donor desk harness\n")),
        "NOTE", "casework.py")

    def donor_fix(here, there):
        write(there, "tools/adapted.py", b"TOKEN = 'there'  # a fix\n")
        git(there, "commit", "-q", "-am", "fix")
    leg("donor change to a declared adaptation since LAST_SYNC is reported", BASE,
        "RECHECK", "adapted.py", after=donor_fix)

    def donor_other(here, there):
        write(there, "tools/other.txt", b"x\n")
        git(there, "add", "-A")
        git(there, "commit", "-q", "-m", "other")
    leg("donor change past LAST_SYNC to a file no row declares: no RECHECK", BASE,
        None, after=donor_other)
    leg("donor without git history: RECHECK not run, pass is SKIPPED not clean", BASE,
        "⚠️", "RECHECK not run", git_donor=False)

    for rel in sorted(MIRRORS):
        drift = {r: (b"kit\n", b"kit\n") for r in MIRRORS}
        drift[rel] = (b"kit, edited here\n", b"kit\n")
        leg("mirrored %s drifting is reported" % rel, BASE, "DRIFT", rel, mirrors=drift)
        crlf = {r: (b"kit\n", b"kit\n") for r in MIRRORS}
        crlf[rel] = (b"kit\r\n", b"kit\n")
        leg("mirrored %s differing only in line endings is reported" % rel, BASE,
            "DRIFT", rel, mirrors=crlf)
        gone = {r: (b"kit\n", b"kit\n") for r in MIRRORS}
        gone[rel] = (None, b"kit\n")
        leg("mirrored %s missing here is reported" % rel, BASE, "MISSING", rel,
            mirrors=gone)

    citation_legs()

    width = max(len(n) for n, _ in results)
    for name, ok in results:
        print("  %-*s  %s" % (width, name, "FIRED" if ok else "DID NOT FIRE"))
    print("")
    if failures:
        print("sync_from_fixpack_selftest: RED — %d leg(s) did not behave as claimed"
              % len(failures))
        for f in failures:
            print("  " + f)
        return 1
    print("sync_from_fixpack_selftest: GREEN — %d leg(s), including the silent controls"
          % len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
