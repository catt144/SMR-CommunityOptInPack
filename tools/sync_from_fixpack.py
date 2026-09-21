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

Four passes, each answering one question:

  --facts       is the fact mirror still a mirror, apart from what we DECLARE
                is locally adapted?
  --donor-log   what has changed in the donor's shared surfaces since our last
                recorded sync?
  --citations   does this repo contain everything it cites, and does the donor
                hold what we are missing?
  --tools       which donor tools (tools/*.py, tools/hooks/*) are new, differ
                or exist only here, apart from what we DECLARE — and are the
                kit docs (`MIRRORED_DOCS`) still byte-identical mirrors?

WHY THE DECLARED CONSTANTS BELOW MATTER. `LOCAL_ADAPTATIONS`, the `TOOLS_*`
tables, `MIRRORED_DOCS` and `LAST_SYNC` replace the retired prose port ledger. A
ledger written as prose goes stale in silence; these cannot, because the thing
that reads them is the thing that checks them. Add a row when you deliberately
diverge from the donor, and move `LAST_SYNC` when you finish a sync.
`tools/sync_from_fixpack_selftest.py` proves the --tools pass fires on each
undeclared shape; doccheck requires it.

    python tools/sync_from_fixpack.py                 # all four passes
    python tools/sync_from_fixpack.py --facts
    python tools/sync_from_fixpack.py --tools         # tools + kit-doc mirror
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
# THE DECLARED LEDGER. This is what 15,599 B of port-ledger narrative reduced
# to, once measured: on 2026-09-17 the fact mirror differed
# from the donor's in exactly these three files and nothing else.
#
# A row here is a PROMISE that the difference is deliberate. Anything differing
# that is NOT listed here is the finding this pass exists to surface.
LOCAL_ADAPTATIONS = {
    "EF-062.md": "its FUTURE_IDEAS pointer is adapted to this repo's file "
                 "(the only CONTENT adaptation in the mirror)",
    "_preamble.md": "carries this repo's dated copy note and sync-tool pointer "
                    "on top of the donor's text",
}

# The last donor sha this repo synced from. Move it when a sync completes, in
# the same commit that lands the sync.
LAST_SYNC = "fc10083"

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

# ---------------------------------------------------------------------------
# THE TOOLS LEDGER, measured 2026-09-18 against donor 869ce8d: every shared
# tool diffed after LF normalisation, and every donor-only tool's header read.
# Keys are paths under tools/. A row is a PROMISE; an undeclared difference is
# the finding. ⛔ Never declare an UNPORTED DONOR FIX here — a row would hide
# exactly what this pass exists to show. Port it, then declare what is left.

# Donor tools this repo deliberately lacks. A donor tool absent here and NOT
# listed is reported as NEW THERE — a candidate to port.
_DONOR_CASEWORK = ("the fix pack's own case work: a desk harness or receipt for "
                   "its F/C entries, modules or chains, not a reusable instrument")
TOOLS_NOT_PORTED = {
    **{name: _DONOR_CASEWORK for name in (
        "c90_scratch_verify.py", "seam_coverage.py",
        "desk_c104_political_animal.py", "desk_c105_water_reclamation.py",
        "desk_c107_dry_farming.py", "desk_c108_wildfire_cure.py",
        "desk_c74_hit_moment_fx.py", "desk_c83_arrivals.py", "desk_c85_clogged.py",
        "desk_c86_scan_downgrade.py", "desk_c88_prefab.py", "desk_c89_faction_gate.py",
        "desk_c90_datapatch.py", "desk_c92_achievement.py", "desk_c93_open_pasture.py",
        "desk_c95_habitat_draft.py", "desk_c95_return_home.py",
        "desk_c96_rover_subclass.py", "desk_caller_seam.py",
        "desk_ck53_hostile_globals.py", "desk_f117_argshape.py",
        "desk_f117_kitprobe.py", "desk_f117_recipe.py", "desk_f119_trade_fuel.py",
        "desk_f59_expedition.py", "desk_f59_interact.py",
        "desk_migration_cluster.py", "desk_migration_observations.py",
        "desk_mystery_tech_migration.py", "desk_probes_f67_f59.py",
        "desk_progress_seam.py", "desk_seam_food.py", "desk_shelter_reflex.py")},
    "bodycheck.py": "pins manifest headers this repo's Opt_ modules do not carry "
                    "(FIX_POLICY's adaptation note omits §2b)",
    "patchcheck.py": "the fix pack's game-patch job runs it FROM the fix pack against "
                     r"this Code/ (--code B:\Dev\SMR\SMR-OptInPack\Code) and leaves the "
                     "result in prompts/perma/gamepatch/; a copy here would fork the hash",
    "patchcheck_selftest.py": "the falsifier for patchcheck.py, which is not ported",
    "l8_deference_map.py": "quarantined in the donor (terminal audit TA-3: misses "
                           "`local orig = Name` captures) and unrepaired there",
    # Adjudicated 2026-09-19 (knowledge sync vs donor eaff679); c7b7a00 left
    # these nine open for this pass.
    "aliascheck.py": "gates the shared TestKit's probe files, which live in the kit's "
                     "own repo and serve every mod: run the donor's copy",
    "deskbench.py": "bound to the donor's Register shape and the shared kit; no desk "
                    "harness here uses it",
    "fact_provenance.py": "facts are allocated and dated in the donor; this repo holds "
                          "a byte mirror, so provenance is read there",
    "logscan.py": "the donor's copy already tags this mod's [CommunityOptInPack] lines "
                  "in the one shared log (its TAGGED pattern); only its heal-shape table "
                  "reads the donor's Code/ alone. Reading this repo's Code/ too: "
                  "propose there",
    "luafn.py": "FIX_POLICY omits §2b here: no SRC: pins or manifest headers for it to "
                "hash; for a game-source read, run the donor's copy",
    "presetdiff.py": "a game-tree instrument whose answer does not depend on the repo "
                     "it runs from: run the donor's copy",
    "treediff.py": "a game-tree instrument whose answer does not depend on the repo; "
                   "its SRC: pin cross-check has no pins here: run the donor's copy",
    "paradox_card.py": "a store-page tool, and this mod is NOT PUBLISHED: revisit on "
                       "the launch checklist",
    "store_screenshots.py": "a store-gallery tool, and this mod is NOT PUBLISHED: "
                            "revisit on the launch checklist",
}

# Shared tools that differ from the donor ON PURPOSE. Silent while they differ;
# a NOTE when a row stops differing; RECHECK when the donor's copy changed since
# LAST_SYNC, because a fix there may not have been received here.
_GUARD = "cp1252 console guard (ac47380)"
TOOLS_ADAPTED = {
    "audit_preset_fields.py": "provenance line, " + _GUARD + ", SMROptInPack in its fixture",
    "blocking_analysis.py": _GUARD + " only — the donor lacks it: propose there",
    "ck170_selftest.py": "legs only for gates live here (STATE bytes, skills mirror); "
                         "no marker/owner-register legs — this doccheck has neither gate",
    "counts_selftest.py": "this mod's Register needle, anchored optional-field trap, "
                          "shared-kit probe label and this main()'s gate list",
    "doccheck.py": "this repo's gate set, paths and module token (check_agents_mirror "
                   "is the donor's check_entry_mirror; no bodycheck/alias gates)",
    "flpk_extract.py": "the donor's reader (341550f) plus only the " + _GUARD,
    "harvest_wrap_targets.py": "SMROptInPack.Require needle, this mod's allowlist, "
                               "SMRFixPack kept out of _NOT_CLASSES (ban 2)",
    "hooks/pre-commit": "its header comment names this repo; the body is the donor's",
    "l2_reload_sim.py": "REWRITTEN: loads this mod's whole code list twice; the "
                        "donor's is bound to its own DataPatch fixtures",
    "l3_save_footprint.py": "token rename; NAMED_STATE matches both prefixes "
                            "(persisted names keep SMRFixPack_); " + _GUARD,
    "l4_player_surfaces.py": "provenance line, token rename, " + _GUARD,
    "l5_containment.py": "provenance line, token rename, " + _GUARD,
    "l6_promise_map.py": "token rename, Opt_ filename derivation, " + _GUARD,
    "l6_reachability.py": "provenance line, token rename, " + _GUARD,
    "l7_env_map.py": "'this mod' wording, " + _GUARD,
    "l8_hostile_input.py": "token rename and this mod's module trio "
                           "(ClassicRockets, DroneStatDials, NoHomeless)",
    "pack_list.py": _GUARD + " only — the donor lacks it: propose there",
    "pack_predict.py": "this repo's ignore_files and CONTENT_PREFIX; keeps PATS, which "
                       "pack_list --tree imports (the donor dropped it in 9d15550: "
                       "propose there)",
    "parsecheck.py": "provenance line only",
    "prompt_map_selftest.py": "this prompt map's classes: no ledger-exception row "
                              "or migration allowance",
    "repair_pass_selftest.py": "no marker-integrity legs (no such gate here); parity "
                               "legs drift this repo's own ignore list; C1/C2 "
                               "mutants end at the next def",
    "sigcheck.py": "provenance line and the SMROptInPack token; its forward-declared-"
                   "local blind spot (a false ABSENT on Opt_MultipleSuns): propose there",
    "split_bugs.py": "N/A-migration note and this repo's INDEX header prose",
    "split_facts.py": "port note: the migration half is N/A here",
}

# Tools only this repo has. Anything else only here is reported as ONLY HERE.
TOOLS_LOCAL_ONLY = {
    "rule_headers_selftest.py": "falsifier for the RULES HEADERS gate, which the "
                                "donor runs without one: propose there",
    "sync_from_fixpack.py": "this repo's side of the sync; the donor pulls from nobody",
    "sync_from_fixpack_selftest.py": "the falsifier for this file's --tools pass",
}

# Owner, 2026-09-18 ("Mirror them"): one TestKit serves every mod, so the kit
# docs are the donor's BYTES. No adaptation row exists for these on purpose: a
# change that belongs here belongs in the donor first.
MIRRORED_DOCS = {
    "tools/TESTKIT.md": "the kit's verdict semantics and per-mod registry table",
    "tools/SMRTK.md": "the in-game toolkit and sitting preload",
}

# Citation shapes, from KNOWLEDGE_SYNC_PASS section 1.
CITE_PATH = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|lua|json))`")
CITE_ID = re.compile(r"\b(EF-\d{3}|D\d{2}|F\d{2,3}|C\d{2,3})\b")

# ---------------------------------------------------------------------------
# EXPECTED donor-owned citations — `WORKFLOW.md` "Donor names", as data.
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
    # "Donor names"' named list
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
    # `C47.md`, `agent/bugs/F104.md`: the entry FILE of a donor id is as much the
    # donor's as the bare id (2026-09-19: 8 such rows were listed as actions).
    if base.endswith(".md") and DONOR_ID.fullmatch(base[:-3]):
        return True
    return base in DONOR_OWNED_FILES or base.startswith("Fix_")


# ---------------------------------------------------------------------------
# CITATIONS DONOR-HAS-IT ON PURPOSE, by class -- the same shape as the TOOLS_*
# tables: a row is a PROMISE that the citation is meant to point into the
# donor, and the reason is what a later reader checks. Consulted only for a
# citation the donor HAS; a NOWHERE row is never hidden by any of these.
# Measured 2026-09-19 (donor eaff679): the DONOR-HAS-IT rows were all cited on
# purpose.
#
# By CITER: a citer whose citations of donor files are its purpose. Prefix
# match on the citing file's repo-relative path.
CITERS_BY_DESIGN = {
    "docs/agent/facts/": "the fact mirror is the donor's bytes (facts are allocated "
                         "there), so its citations are the donor's own paths",
    "docs/agent/WORKFLOW.md": "its 'Donor names' and 1.1.0-report pointers name the "
                              "fix pack's documents on purpose",
}
# By CITATION (bare file name; the directory a citer spells is not compared).
_RELEASE = ("the release system this repo will build on the donor's "
            "(prompts/RELEASE_SYSTEM_high.md, a live prompt); a pull now goes stale")
_RECORD = ("a dated record cites evidence that lives in the donor; a record is not "
           "rewritten, and the donor's copy is its home")
_GAMEPATCH = ("prompts/perma/gamepatch/ is the outbox for the fix pack's game-patch "
              "job, which runs FROM the fix pack first (owner, 2026-09-18)")
CITATIONS_BY_DESIGN = {
    **{name: _RELEASE for name in (
        "RELEASE_HISTORY.md", "RELEASE_OUTBOX.md", "RELEASE_SURFACES.md",
        "release_prompt.md", "POST_UPLOAD_CLOSE.md", "LIVE_SITE_READ.md",
        "STORE_CARD_LIVE.md")},
    **{name: _RECORD for name in (
        "L3_SAVE_FOOTPRINT.md", "MEMORY.md", "RULES_HEADERS_INVENTORY.json",
        "SWEEP_FINDINGS.md")},
    **{name: _GAMEPATCH for name in ("GAME_PATCH_PROMPT.md", "patchcheck.py")},
}


# Citations that resolve NOWHERE on purpose: the citer's own sentence says the
# thing is external, temporary or retired. Keyed by the exact citation text; the
# reason is what was read on 2026-09-19 (this repo eaff679-era docs). A row the
# citer stops making is inert, a row that starts to resolve is never reached.
CITATIONS_ABSENT = {
    "97_OptInLeg.lua": "D05: a TEMPORARY flag file, deleted after the leg it enabled",
    "BlenderExport.py": "TRAIN_LOGISTICS_DESIGN: a file inside the game's ModTools "
                        "distribution, read from the install, not a repo file",
    "D08": "D06 and the drone briefs: a retired drone layer whose entry was folded "
           "into D06 and never filed as a file",
    "_LuaRevision.lua": "EF-014, EF-085: the game's fpk-only file, not in any archived "
                        "Src tree (the mirrored fact says so)",
    "Lua/Config/_LuaRevision.lua": "EF-085: as _LuaRevision.lua",
    "for-modders.md": "EF-054: a doc the donor names as unchanged, absent from every "
                      "tree here (the mirrored fact's own words)",
}


def by_design(c, citers):
    """The declared reason a DONOR-HAS-IT citation is intentional, or None.

    A citation is declared when its file name has a CITATIONS_BY_DESIGN row, its
    name is a tool declared not ported (TOOLS_NOT_PORTED -- the deliberate
    absence), or EVERY citing file falls under a CITERS_BY_DESIGN prefix. One
    citer outside every class keeps the row listed."""
    base = c.rsplit("/", 1)[-1]
    if base in CITATIONS_BY_DESIGN:
        return CITATIONS_BY_DESIGN[base]
    if base in TOOLS_NOT_PORTED:
        return "a donor tool declared not ported: " + TOOLS_NOT_PORTED[base]
    reasons = []
    for citer in citers:
        hit = [r for pre, r in CITERS_BY_DESIGN.items() if citer.startswith(pre)]
        if not hit:
            return None
        reasons.append(hit[0])
    return reasons[0] if reasons else None


# Illustrative placeholders in the prompts that TEACH the citation shapes. They
# are not citations of anything and must not be reported as broken.
PLACEHOLDERS = {"X.md", "y.py", "tools/y.py", "agent/reports/X.md",
                "docs/agent/facts/EF-0NN.md", "Opt_Z.lua", "X.py",
                "docs/agent/bugs/Dxx.md"}

# The GAME's own source, cited constantly by facts. It lives in neither repo —
# it is read from the archived tree for the build the fact was derived on
# (CLAUDE.md: cite a line only with the build it was read on).
SRC_ARCHIVE = os.environ.get("SMR_SRCARCHIVE", r"C:\Dev\SMR-SrcArchive")

# Places a citation may resolve that are neither this repo's docs/ nor the donor
# (2026-09-19: the first run listed 78 NOWHERE rows, most of them these):
TESTKIT = os.environ.get("SMR_TESTKIT", r"C:\Dev\SMR-BugFixPack-TestKit")
TRAIN_ASSETS = os.environ.get("SMR_TRAINASSETS", r"B:\Dev\SMR\SMR-Assets\trainhub")
_SKIP_DIRS = (".git", "__pycache__", "node_modules")
_indexes = {}


def _suffixes(rel, into):
    """Add REL and every suffix of it that starts at a `/` boundary."""
    parts = rel.split("/")
    for i in range(len(parts)):
        into.add("/".join(parts[i:]))


def _tree_index(root):
    """{every `/`-boundary suffix of every file under ROOT}, built once per root.
    A suffix index makes `Lua/Buildings/Station.lua`, `Station.lua` and
    `1.1.0.403908/Src/Lua/Buildings/Station.lua` (after _hit drops the build
    prefix) all hit the same file."""
    if root not in _indexes:
        idx = set()
        if root and os.path.isdir(root):
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
                for fn in filenames:
                    rel = os.path.relpath(os.path.join(dirpath, fn), root)
                    _suffixes(rel.replace(os.sep, "/"), idx)
        _indexes[root] = idx
    return _indexes[root]


def _hit(c, idx):
    """True when citation C names a file in IDX. A leading `TestKit/` or a
    `<build>/Src/` the citer spelled is dropped before the suffix test."""
    c = re.sub(r"^(?:TestKit/|[0-9][0-9.]*/Src/)", "", c)
    return c in idx


def game_owned(c):
    """True when a citation names a shipped game file, not a repo file. A
    subfolder path (`CommonLua/Classes/Mod.lua`, `1.1.0.403908/Src/...`)
    resolves as well as the bare name."""
    if not c.endswith((".lua", ".md")) or ("/" in c and c.endswith(".md")):
        return False
    return _hit(c, _tree_index(SRC_ARCHIVE))


def sibling_owned(c):
    """The kit repo, this repo's dev mods, or the train asset repo hold it."""
    for root in (TESTKIT, os.path.join(REPO, "tools", "devmods"), TRAIN_ASSETS):
        if _hit(c, _tree_index(root)):
            return True
    return False


def history_owned(c, root=None):
    """True when the repo at ROOT (default: this one) once tracked a file of that
    name and it is gone now: a consumed prompt or a retired module, cited by the
    record that used it. (`git log --all --name-only`, once per repo.) Only
    reached after every live place failed, so a file still on disk is never
    reported as history."""
    root = root or REPO
    key = ("history", root)
    if key not in _indexes:
        idx = set()
        try:
            names = subprocess.check_output(
                ["git", "-C", root, "log", "--all", "--name-only", "--pretty=format:"],
                text=True, encoding="utf-8", errors="replace",
                stderr=subprocess.PIPE, env=git_env()).splitlines()
        except (OSError, subprocess.CalledProcessError):
            names = []
        for n in names:
            if n.strip():
                _suffixes(n.strip(), idx)
        _indexes[key] = idx
    return _hit(c, _indexes[key])


def lf(path):
    with open(path, "rb") as fh:
        return fh.read().replace(b"\r\n", b"\n")


def donor_ok(out):
    if not os.path.isdir(DONOR):
        out.append("  SKIPPED - the donor is not at %s (set SMR_FIXPACK). This "
                   "run says NOTHING about drift." % DONOR)
        return False
    return True


def git_env():
    """os.environ without GIT_*: under the pre-commit hook (doccheck runs the
    selftest that runs this) GIT_DIR/GIT_INDEX_FILE would point `git -C DONOR`
    at THIS repo's commit-in-progress (tools/README.md, top)."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


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
                   "THERE first (the smr-bug-library skill)" % name)
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
                                 LAST_SYNC + "^{commit}"], stderr=subprocess.PIPE,
                                env=git_env())
    except (OSError, subprocess.CalledProcessError):
        out.append("  SKIPPED - %s is not a commit in the donor. Its history may "
                   "have been rewritten, or LAST_SYNC is wrong." % LAST_SYNC)
        return None
    try:
        head = subprocess.check_output(
            ["git", "-C", DONOR, "rev-parse", "--short", "HEAD"],
            text=True, encoding="utf-8", errors="replace", env=git_env()).strip()
        log = subprocess.check_output(
            ["git", "-C", DONOR, "log", "--oneline", "%s..HEAD" % LAST_SYNC, "--"]
            + SHARED_SURFACES,
            text=True, encoding="utf-8", errors="replace", env=git_env()).splitlines()
        stat = subprocess.check_output(
            ["git", "-C", DONOR, "diff", "--stat", "%s..HEAD" % LAST_SYNC, "--"]
            + SHARED_SURFACES,
            text=True, encoding="utf-8", errors="replace", env=git_env()).splitlines()
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


def moved_here(c):
    """A path citation whose exact path is gone but whose file name is here: an
    older record's pre-split path (`docs/reports/X.md`, now `docs/agent/reports/`)."""
    if "/" not in c:
        return False
    base = c.rsplit("/", 1)[-1]
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        if base in filenames:
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
    designed, sibling, moved, history, other_history = [], [], [], [], []
    absent = []
    for c in sorted(cites):
        if c in PLACEHOLDERS or _resolves_here(c):
            continue
        if donor_owned(c):
            expected.append(c)
            continue
        if game_owned(c):
            game.append(c)
            continue
        if sibling_owned(c):
            sibling.append(c)
            continue
        if moved_here(c):
            moved.append(c)
            continue
        if _resolves_donor(c):
            if by_design(c, cites[c]):
                designed.append(c)
            else:
                donor_has.append(c)
            continue
        if history_owned(c):
            history.append(c)
        elif any(history_owned(c, r) for r in (DONOR, TESTKIT)):
            other_history.append(c)
        elif c in CITATIONS_ABSENT:
            absent.append(c)
        else:
            nowhere.append(c)

    out.append("  %d distinct citation(s) checked across docs/ (archive excluded)"
               % len(cites))
    out.append("  %d expected donor-owned (WORKFLOW 'Donor names') — counted, not listed"
               % len(expected))
    out.append("  %d shipped-game source file(s) under %s — counted, not listed"
               % (len(game), SRC_ARCHIVE))
    out.append("  %d in a sibling repo (TestKit, tools/devmods, train assets) — "
               "counted, not listed" % len(sibling))
    out.append("  %d at another path here (moved since the record was written) — "
               "counted, not listed" % len(moved))
    out.append("  %d in the donor ON PURPOSE (CITERS_/CITATIONS_BY_DESIGN, each with "
               "a reason) — counted, not listed" % len(designed))
    out.append("  %d only in this repo's git history (consumed prompt, retired "
               "module) — counted, not listed" % len(history))
    out.append("  %d only in the donor's or the TestKit's git history (a mirrored "
               "fact citing what the donor retired) — counted, not listed"
               % len(other_history))
    out.append("  %d resolve nowhere ON PURPOSE (CITATIONS_ABSENT, each with a "
               "reason) — counted, not listed" % len(absent))
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


# ---------------------------------------------------------------------------
def tool_set(root):
    """{path under tools/} for every tools/*.py and tools/hooks/* file."""
    tools = os.path.join(root, "tools")
    found = set()
    if os.path.isdir(tools):
        found.update(n for n in os.listdir(tools)
                     if n.endswith(".py") and os.path.isfile(os.path.join(tools, n)))
    hooks = os.path.join(tools, "hooks")
    if os.path.isdir(hooks):
        found.update("hooks/" + n for n in os.listdir(hooks)
                     if os.path.isfile(os.path.join(hooks, n)))
    return found


def donor_tools_changed():
    """{path under tools/} the donor changed since LAST_SYNC, or None if git failed."""
    try:
        names = subprocess.check_output(
            ["git", "-C", DONOR, "diff", "--name-only", LAST_SYNC, "HEAD", "--", "tools/"],
            text=True, encoding="utf-8", errors="replace", stderr=subprocess.PIPE,
            env=git_env()).splitlines()
    except (OSError, subprocess.CalledProcessError):
        return None
    return {n[len("tools/"):] for n in names if n.startswith("tools/")}


def pass_tools(out):
    """Which donor tools are new, differ, or exist only here — beyond the declared?"""
    out.append("")
    out.append("== TOOLS (tools/*.py, tools/hooks/*) ==")
    if not donor_ok(out):
        return None
    here, there = tool_set(REPO), tool_set(DONOR)
    if not there:
        out.append("  SKIPPED - the donor has no tools/*.py")
        return None

    new_there, only_here, both = there - here, here - there, here & there
    same, adapted, differing = [], [], []
    for name in sorted(both):
        a = lf(os.path.join(REPO, "tools", *name.split("/")))
        b = lf(os.path.join(DONOR, "tools", *name.split("/")))
        if a == b:
            same.append(name)
        else:
            (adapted if name in TOOLS_ADAPTED else differing).append(name)
    new_undeclared = sorted(new_there - set(TOOLS_NOT_PORTED))
    only_undeclared = sorted(only_here - set(TOOLS_LOCAL_ONLY))

    out.append("  %d tool(s) here, %d there: %d identical, %d declared adapted, "
               "%d declared not ported, %d declared local-only — silent"
               % (len(here), len(there), len(same), len(adapted),
                  len(new_there & set(TOOLS_NOT_PORTED)),
                  len(only_here & set(TOOLS_LOCAL_ONLY))))

    # Declarations that no longer describe the tree. NOTE, as the facts pass does.
    for name in sorted(set(TOOLS_ADAPTED) & set(same)):
        out.append("  NOTE      %-30s declared adapted but does NOT differ — the "
                   "row may be obsolete" % name)
    for name in sorted(set(TOOLS_ADAPTED) - both):
        out.append("  NOTE      %-30s declared adapted but not present in both "
                   "repos — the row may be obsolete" % name)
    for name in sorted(set(TOOLS_NOT_PORTED) - new_there):
        out.append("  NOTE      %-30s declared not ported but %s — the row may be "
                   "obsolete" % (name, "present here" if name in here
                                 else "the donor no longer has it"))
    for name in sorted(set(TOOLS_LOCAL_ONLY) - only_here):
        out.append("  NOTE      %-30s declared local-only but %s — the row may be "
                   "obsolete" % (name, "the donor has it too" if name in there
                                 else "absent here"))

    recheck = []
    changed = donor_tools_changed() if adapted else set()
    if changed is None:
        out.append("  ⚠️ RECHECK not run: `git diff %s HEAD` failed in the donor, so a "
                   "fix landing there in a declared-adapted tool would go unseen"
                   % LAST_SYNC)
    else:
        recheck = [n for n in adapted if n in changed]

    for name in differing:
        out.append("  DIFFERS   %-30s differs and is NOT declared — a donor fix not "
                   "received, or an adaptation: port it, or add a TOOLS_ADAPTED row"
                   % name)
    for name in recheck:
        out.append("  RECHECK   %-30s declared adapted, and the donor changed it since "
                   "%s — carry the change, then keep the row" % (name, LAST_SYNC))
    for name in new_undeclared:
        out.append("  NEW THERE %-30s a donor tool this repo lacks — port it, or add a "
                   "TOOLS_NOT_PORTED row" % name)
    for name in only_undeclared:
        out.append("  ONLY HERE %-30s not in the donor — propose it there, or add a "
                   "TOOLS_LOCAL_ONLY row" % name)
    found = bool(differing or recheck or new_undeclared or only_undeclared)
    if not found:
        out.append("  PASS - nothing undeclared")
    if changed is None:
        return True if found else None
    return found


def pass_mirror(out):
    """Are the mirrored kit docs still the donor's bytes?"""
    out.append("")
    out.append("== MIRRORED DOCS (byte-identical by owner decision, 2026-09-18) ==")
    if not donor_ok(out):
        return None
    bad = []
    for rel in sorted(MIRRORED_DOCS):
        mine = os.path.join(REPO, *rel.split("/"))
        theirs = os.path.join(DONOR, *rel.split("/"))
        if not os.path.isfile(theirs):
            bad.append("  GONE THERE %-18s the donor no longer has it — drop the mirror "
                       "or find where it moved" % rel)
        elif not os.path.isfile(mine):
            bad.append("  MISSING   %-18s mirrored by decision but absent here — copy "
                       "the donor's bytes" % rel)
        else:
            with open(mine, "rb") as fh:
                a = fh.read()
            with open(theirs, "rb") as fh:
                b = fh.read()
            if a != b:
                bad.append("  DRIFT     %-18s differs from the donor — a mirror takes no "
                           "local edit: copy the donor's bytes, and make a change that "
                           "belongs in both THERE first" % rel)
    out.extend(bad)
    if not bad:
        out.append("  PASS - %d mirrored doc(s) match the donor byte for byte"
                   % len(MIRRORED_DOCS))
    return bool(bad)


def main():
    ap = argparse.ArgumentParser(
        description="Read-only cross-repo sync report (SMR-OptInPack <- SMR-BugFixPack)")
    ap.add_argument("--facts", action="store_true", help="fact-mirror drift only")
    ap.add_argument("--donor-log", action="store_true", help="donor changes since LAST_SYNC")
    ap.add_argument("--citations", action="store_true", help="dangling-citation sweep only")
    ap.add_argument("--tools", action="store_true",
                    help="tools/ drift against the TOOLS_* ledger, plus the kit-doc mirror")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when a pass reports something to adjudicate")
    args = ap.parse_args()
    run_all = not (args.facts or args.donor_log or args.citations or args.tools)

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
    if run_all or args.tools:
        findings.append(pass_tools(out))
        findings.append(pass_mirror(out))

    out.append("")
    if any(f is None for f in findings):
        out.append("⚠️ At least one pass SKIPPED — this run is not a clean bill.")
    out.append("⛔ A finding is not a work list. Nothing lands here without a "
               "human deciding its subject applies to this mod.")
    print("\n".join(out))
    return 1 if (args.strict and any(findings)) else 0


if __name__ == "__main__":
    sys.exit(main())
