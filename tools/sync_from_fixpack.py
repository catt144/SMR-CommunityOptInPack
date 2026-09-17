#!/usr/bin/env python
"""Cross-repo sync helper: what has the fix pack got that this repo needs?

Fired by `docs/agent/prompts/perma/KNOWLEDGE_SYNC_PASS.md` when the owner has
made significant changes in `C:\\Dev\\SMR-BugFixPack` and wants to know what
lands here. It does the MECHANICAL half only and never decides anything: the
session reads this report and adjudicates.

STOP - READ-ONLY IN BOTH REPOS. This script never writes a file, never stages
anything and never touches the donor at all beyond `git log` and reading bytes.
Copying a file across is a human act with a commit message, because "should this
land here" is a judgement and judgements are not scriptable.

Three passes, each answering one question:

  --facts       is the fact mirror still a mirror, apart from what we DECLARE
                is locally adapted?
  --donor-log   what has changed in the donor's shared surfaces since our last
                recorded sync?
  --citations   does this repo contain everything it cites, and does the donor
                hold what we are missing?

WHY THE DECLARED CONSTANTS BELOW MATTER. `LOCAL_ADAPTATIONS` and `LAST_SYNC`
replace the port-ledger sections of the retired `docs/agent/PROVENANCE.md`. A
ledger written as prose goes stale in silence; these cannot, because the thing
that reads them is the thing that checks them. Add a row when you deliberately
diverge from the donor, and move `LAST_SYNC` when you finish a sync.

    python tools/sync_from_fixpack.py                 # all three passes
    python tools/sync_from_fixpack.py --facts
    python tools/sync_from_fixpack.py --strict        # exit 1 on an UNEXPECTED finding
"""
import argparse
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONOR = os.environ.get("SMR_FIXPACK", r"C:\Dev\SMR-BugFixPack")

# ---------------------------------------------------------------------------
# THE DECLARED LEDGER. This is what `PROVENANCE.md`'s 15,599 B of port-ledger
# narrative reduced to, once measured: on 2026-09-17 the fact mirror differed
# from the donor's in exactly these three files and nothing else.
#
# A row here is a PROMISE that the difference is deliberate. Anything differing
# that is NOT listed here is the finding this pass exists to surface.
LOCAL_ADAPTATIONS = {
    "EF-062.md": "its FUTURE_IDEAS pointer is adapted to this repo's file "
                 "(the only CONTENT adaptation in the mirror)",
    "INDEX.md": "GENERATED here from local front matter by tools/split_facts.py; "
                "never copied from the donor",
    "_preamble.md": "carries this repo's dated copy note on top of the donor's text",
}

# The last donor sha this repo synced from. Move it when a sync completes, in
# the same commit that lands the sync.
LAST_SYNC = "e6ec192"

# Donor paths whose changes could matter here. Deliberately NOT the whole tree:
# its Fix_*.lua modules, its playtest checklist and its store drafts are its own
# business (KNOWLEDGE_SYNC_PASS section 2 lists the known not-gaps).
SHARED_SURFACES = [
    "docs/agent/facts/",
    "docs/agent/WORKFLOW.md",
    "docs/agent/FIX_POLICY.md",
    "tools/",
    ".claude/skills/",
    "CLAUDE.md",
]

# Citation shapes, from KNOWLEDGE_SYNC_PASS section 1.
CITE_PATH = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|lua|json))`")
CITE_ID = re.compile(r"\b(EF-\d{3}|D\d{2}|F\d{2,3}|C\d{2,3})\b")

# ---------------------------------------------------------------------------
# EXPECTED donor-owned citations — `WORKFLOW.md` banner clause 6, as data.
#
# ⛔ WITHOUT THIS THE CITATION PASS IS USELESS. Clause 6 says bare `F##`/`C##`
# ids, the donor's `Fix_*.lua`, and a named list of its documents resolve under
# the fix pack and NEVER here, deliberately. Reported as findings they drown the
# real ones: the first run of this pass printed ~90 rows, of which all but a
# handful were correct by design. A report that is mostly expected is a report
# nobody reads, which is how a check stops being read at all.
#
# So these are counted and summarised, not listed. Anything OUTSIDE this set is
# the actual action list.
DONOR_ID = re.compile(r"^(?:[FC]\d{2,3}|D1[0-3])$")   # F/C entries + D10-D13 are the donor's
DONOR_OWNED_FILES = {
    # clause 6's named list
    "AUDIT_FINDINGS.md", "BUG_LIST_AUDIT.md", "PRIOR_ART_SURVEY.md",
    "DRONE_RESEARCH_BRIEF.md", "CORUN_RIG_SPEC.md", "MOD_DESCRIPTION.md",
    "F86_EXECUTION_PLAN.md", "PLAYTEST_ARCHIVE.md",
    # the rest of the donor's own surfaces this repo cites on purpose
    "PLAYTEST_CHECKLIST.md", "PLAYTEST_HELP.md", "UPLOAD_WORKFLOW.md",
    "PARKED_OPTIN_REFERENCES.md", "RELEASE_PORTAL_PREP.md", "BLIND_AUDIT.md",
    "CHAIN_QA_REPORT.md", "DOC_STRUCTURE_REVIEW.md", "DOC_RESTRUCTURE_SPEC.md",
    "D13_EXPOSED_SET.md", "F86_ADJUDICATION.md", "SAVE_SAFETY_REDESIGN.md",
    "REACHABILITY_AUDIT.md", "L8_ADVERSARIAL_MAP.md", "L5_CONTAINMENT_MAP.md",
    "STORE_METADATA_STRINGS.md", "RELEASE_DESCRIPTION_OPTIN.md", "STORE_OPTIN.md",
    "GENERAL_USE_PROMPT.md", "DRONE_PROJECT_PROMPT.md", "RELEASE.md",
    "90_SaveSanitizer.lua", "90_Loggers.lua", "SWEEP_LEDGER.md",
    # pre-restructure donor names that only exist in its history
    "BUGS.md", "STATUS.md", "ENGINE_FACTS.md",
}


def donor_owned(c):
    """True when a citation is SUPPOSED to resolve in the donor and not here."""
    if DONOR_ID.fullmatch(c):
        return True
    base = c.rsplit("/", 1)[-1]
    return base in DONOR_OWNED_FILES or base.startswith("Fix_")


# Illustrative placeholders in the prompts that TEACH the citation shapes. They
# are not citations of anything and must not be reported as broken.
PLACEHOLDERS = {"X.md", "y.py", "tools/y.py", "agent/reports/X.md",
                "docs/agent/facts/EF-0NN.md", "Opt_Z.lua", "X.py"}

# The GAME's own source, cited constantly by facts. It lives in neither repo —
# it is read from the archived tree for the build the fact was derived on
# (CLAUDE.md: cite a line only with the build it was read on).
SRC_ARCHIVE = os.environ.get("SMR_SRCARCHIVE", r"C:\Dev\SMR-SrcArchive")
_src_index = None


def game_owned(c):
    """True when a citation names a shipped game file, not a repo file."""
    global _src_index
    if "/" in c or not c.endswith((".lua", ".md")):
        return False
    if _src_index is None:
        _src_index = set()
        if os.path.isdir(SRC_ARCHIVE):
            for dirpath, dirnames, filenames in os.walk(SRC_ARCHIVE):
                dirnames[:] = [d for d in dirnames if d != ".git"]
                _src_index.update(filenames)
    return c in _src_index


def lf(path):
    with open(path, "rb") as fh:
        return fh.read().replace(b"\r\n", b"\n")


def donor_ok(out):
    if not os.path.isdir(DONOR):
        out.append("  SKIPPED - the donor is not at %s (set SMR_FIXPACK). This "
                   "run says NOTHING about drift." % DONOR)
        return False
    return True


# ---------------------------------------------------------------------------
def pass_facts(out):
    """Is the fact mirror still a mirror, apart from the declared adaptations?"""
    out.append("== FACTS MIRROR ==")
    if not donor_ok(out):
        return None
    here = os.path.join(REPO, "docs", "agent", "facts")
    there = os.path.join(DONOR, "docs", "agent", "facts")
    if not os.path.isdir(there):
        out.append("  SKIPPED - donor has no docs/agent/facts/")
        return None

    ours = {n for n in os.listdir(here) if n.endswith(".md")}
    theirs = {n for n in os.listdir(there) if n.endswith(".md")}

    differing, expected = [], []
    for name in sorted(ours & theirs):
        if lf(os.path.join(here, name)) != lf(os.path.join(there, name)):
            (expected if name in LOCAL_ADAPTATIONS else differing).append(name)

    new_there = sorted(theirs - ours)
    only_here = sorted(ours - theirs)

    out.append("  %d file(s) here, %d there" % (len(ours), len(theirs)))
    for name in expected:
        out.append("  declared  %-16s %s" % (name, LOCAL_ADAPTATIONS[name]))
    stale = sorted(set(LOCAL_ADAPTATIONS) - set(expected) - (ours - theirs))
    for name in stale:
        out.append("  NOTE      %-16s declared as adapted but does NOT differ — "
                   "the row may be obsolete" % name)
    for name in differing:
        out.append("  DRIFT     %-16s differs and is NOT declared — adjudicate: "
                   "pull the donor's, or add a LOCAL_ADAPTATIONS row" % name)
    for name in new_there:
        out.append("  NEW THERE %-16s the donor has a fact this repo does not "
                   "(EF ids are allocated there — this is the normal direction)" % name)
    for name in only_here:
        out.append("  ONLY HERE %-16s not in the donor — it should be filed "
                   "THERE first (WORKFLOW reading path 2)" % name)
    if not (differing or new_there or only_here):
        out.append("  PASS - the mirror matches, apart from %d declared adaptation(s)"
                   % len(expected))
    return bool(differing or new_there or only_here)


# ---------------------------------------------------------------------------
def pass_donor_log(out):
    """What changed in the donor's shared surfaces since LAST_SYNC?"""
    out.append("")
    out.append("== DONOR CHANGES since %s ==" % LAST_SYNC)
    if not donor_ok(out):
        return None
    try:
        subprocess.check_output(["git", "-C", DONOR, "cat-file", "-e",
                                 LAST_SYNC + "^{commit}"], stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError):
        out.append("  SKIPPED - %s is not a commit in the donor. Its history may "
                   "have been rewritten, or LAST_SYNC is wrong." % LAST_SYNC)
        return None
    try:
        head = subprocess.check_output(
            ["git", "-C", DONOR, "rev-parse", "--short", "HEAD"],
            text=True, encoding="utf-8", errors="replace").strip()
        log = subprocess.check_output(
            ["git", "-C", DONOR, "log", "--oneline", "%s..HEAD" % LAST_SYNC, "--"]
            + SHARED_SURFACES,
            text=True, encoding="utf-8", errors="replace").splitlines()
        stat = subprocess.check_output(
            ["git", "-C", DONOR, "diff", "--stat", "%s..HEAD" % LAST_SYNC, "--"]
            + SHARED_SURFACES,
            text=True, encoding="utf-8", errors="replace").splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        out.append("  SKIPPED - git failed in the donor (%s)" % exc)
        return None

    out.append("  donor HEAD is %s; surfaces watched: %s"
               % (head, ", ".join(SHARED_SURFACES)))
    if not log:
        out.append("  PASS - nothing changed on a shared surface since the last sync")
        return False
    out.append("  %d commit(s) touching a shared surface:" % len(log))
    for line in log[:25]:
        out.append("    " + line)
    if len(log) > 25:
        out.append("    ... and %d more" % (len(log) - 25))
    for line in stat[-12:]:
        out.append("    " + line.rstrip())
    out.append("  ⇒ these are CANDIDATES, not a work list. A donor change lands "
               "here only if its subject applies to this mod.")
    return True


# ---------------------------------------------------------------------------
def _cited(root):
    """{citation: [citing files]} over every tracked .md under root."""
    cites = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "archive"]
        for name in filenames:
            if not name.endswith(".md"):
                continue
            p = os.path.join(dirpath, name)
            rel = os.path.relpath(p, REPO).replace("\\", "/")
            try:
                text = lf(p).decode("utf-8", "replace")
            except OSError:
                continue
            for m in set(CITE_PATH.findall(text)) | set(CITE_ID.findall(text)):
                cites.setdefault(m, []).append(rel)
    return cites


def _resolves_here(c):
    if re.fullmatch(r"EF-\d{3}", c):
        return os.path.exists(os.path.join(REPO, "docs", "agent", "facts", c + ".md"))
    if re.fullmatch(r"[DFC]\d{2,3}", c):
        return os.path.exists(os.path.join(REPO, "docs", "agent", "bugs", c + ".md"))
    if "/" in c:
        for base in ("", "docs", "docs/agent"):
            if os.path.exists(os.path.join(REPO, base, *c.split("/"))):
                return True
        return False
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        if c in filenames:
            return True
    return False


def _resolves_donor(c):
    if not os.path.isdir(DONOR):
        return False
    if re.fullmatch(r"EF-\d{3}", c):
        return os.path.exists(os.path.join(DONOR, "docs", "agent", "facts", c + ".md"))
    if re.fullmatch(r"[DFC]\d{2,3}", c):
        return os.path.exists(os.path.join(DONOR, "docs", "agent", "bugs", c + ".md"))
    base = os.path.basename(c)
    for dirpath, dirnames, filenames in os.walk(DONOR):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        if base in filenames:
            return True
    return False


def pass_citations(out):
    """Does this repo hold what it cites? If not, does the donor?"""
    out.append("")
    out.append("== DANGLING CITATIONS ==")
    cites = _cited(os.path.join(REPO, "docs"))

    # PRESENCE CONTROL, demanded by KNOWLEDGE_SYNC_PASS section 1: prove the
    # method would find a target that IS present, before any "not found" is
    # allowed to mean anything.
    control = "WORKFLOW.md"
    if not _resolves_here(control):
        out.append("  RED - presence control FAILED: the resolver cannot find %s, "
                   "which exists. Every 'dangling' below is meaningless." % control)
        return None
    out.append("  presence control: resolver finds %s — 'not found' now means "
               "something" % control)

    donor_has, nowhere, expected, game = [], [], [], []
    for c in sorted(cites):
        if c in PLACEHOLDERS or _resolves_here(c):
            continue
        if donor_owned(c):
            expected.append(c)
            continue
        if game_owned(c):
            game.append(c)
            continue
        (donor_has if _resolves_donor(c) else nowhere).append(c)

    out.append("  %d distinct citation(s) checked across docs/ (archive excluded)"
               % len(cites))
    out.append("  %d expected donor-owned (WORKFLOW clause 6) — counted, not listed"
               % len(expected))
    out.append("  %d shipped-game source file(s) under %s — counted, not listed"
               % (len(game), SRC_ARCHIVE))
    for c in donor_has:
        out.append("  DONOR HAS %-38s cited by %s" % (c, ", ".join(cites[c][:3])))
    for c in nowhere:
        out.append("  NOWHERE   %-38s cited by %s" % (c, ", ".join(cites[c][:3])))
    if not donor_has and not nowhere:
        out.append("  PASS - every citation either resolves here or is expected "
                   "donor-owned")
    else:
        out.append("  ⇒ DONOR HAS is the action list: a target this repo cites, does "
                   "not hold, and is NOT declared donor-owned.")
        out.append("  ⇒ NOWHERE is a broken reference: report it, never invent a target.")
        out.append("  ⚠️ Still read the sentence before filing — a name may be cited as "
                   "deleted on purpose, which reads identically to a dangling one.")
    return bool(donor_has or nowhere)


def main():
    ap = argparse.ArgumentParser(
        description="Read-only cross-repo sync report (SMR-OptInPack <- SMR-BugFixPack)")
    ap.add_argument("--facts", action="store_true", help="fact-mirror drift only")
    ap.add_argument("--donor-log", action="store_true", help="donor changes since LAST_SYNC")
    ap.add_argument("--citations", action="store_true", help="dangling-citation sweep only")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when a pass reports something to adjudicate")
    args = ap.parse_args()
    run_all = not (args.facts or args.donor_log or args.citations)

    out = ["SYNC REPORT — this repo <- %s" % DONOR,
           "⛔ READ-ONLY. Nothing here was written, staged or copied. Every line "
           "below is a CANDIDATE for a human to adjudicate.", ""]
    findings = []
    if run_all or args.facts:
        findings.append(pass_facts(out))
    if run_all or args.donor_log:
        findings.append(pass_donor_log(out))
    if run_all or args.citations:
        findings.append(pass_citations(out))

    out.append("")
    if any(f is None for f in findings):
        out.append("⚠️ At least one pass SKIPPED — this run is not a clean bill.")
    out.append("⛔ A finding is not a work list. Nothing lands here without a "
               "human deciding its subject applies to this mod.")
    print("\n".join(out))
    return 1 if (args.strict and any(findings)) else 0


if __name__ == "__main__":
    sys.exit(main())
