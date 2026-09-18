#!/usr/bin/env python3
"""Falsifier for doccheck's --emit-counts block: counts follow the source, a RED run withholds the block, and --regen never writes STATE.

Run: python tools/counts_selftest.py        # exit 0 = every leg fired

Ported from SMR-BugFixPack 2026-09-17 (its file of the same name), adapted to
this doccheck: the `SMROptInPack.Register(` needle, the ANCHORED optional-field
pattern (and its comment trap), the shared-kit probe label, an LF-normalised
AGENTS.md, and this main()'s gate list. Every leg runs on a scratch copy in a
temporary directory; each mutant must FAIL the leg it reverts.
"""
from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
import types
from unittest.mock import patch

from repair_pass_selftest import ROOT, load_copy

COUNTS = dict(modules=2, default_active=1, optional=1, files=3,
              probes=2, rows_F=2, rows_D=1, rows_C=2)
MARKER = "BUILD STATE (emitted by tools/doccheck.py)"


def recount_cases(m, root):
    code, tk = root / "Code", root / "TestKit" / "Code"
    code.mkdir(parents=True)
    tk.mkdir(parents=True)
    m.CODE, m.TESTKIT = str(code), str(tk.parent)
    (code / "00_Core.lua").write_text("function SMROptInPack.Register(spec) end\n")
    # The trap OPTIONAL_FIELD_RE is anchored against: a COMMENT naming the field.
    (code / "Always.lua").write_text(
        "-- registers WITHOUT optional = true, on purpose\n"
        "SMROptInPack.Register({})\n")
    (code / "Opt.lua").write_text("SMROptInPack.Register({\n  optional = true,\n})\n")
    (code / "ignored.txt").write_text("SMROptInPack.Register({})\n")
    (tk / "00_TestCore.lua").write_text("function SMRTest.Register(spec) end\n")
    probes = tk / "Probes.lua"
    probes.write_text("SMRTest.Register({})\n" * 2)
    model = {"entries": [{"id": "F01", "members": [{"id": "F02"}]},
                         {"id": "D01"}, {"id": "C01"}],
             "orphans": ["C02"], "by_id": {"C02": {"id": "C02"}}}
    assert m.recount(model, []) == COUNTS, "fixture membership/count mismatch"
    block = m.counts_block(COUNTS)
    assert block.splitlines() == [MARKER,
        "- modules: 2 registered (1 default-active, 1 optional-gated files)",
        "- Code/*.lua files: 3", "- TestKit probes: 2 (shared kit — serves both mods)",
        "- BUGS index rows: 2 F + 1 D + 2 C"], block
    (code / "Added.lua").write_text("SMROptInPack.Register({})\n")
    probes.write_text("SMRTest.Register({})\n" * 3)
    model["entries"].append({"id": "F03"})
    expected = dict(COUNTS, files=4, modules=3, default_active=2, probes=3, rows_F=3)
    assert m.recount(model, []) == expected, "counts failed to follow source changes"
    m.TESTKIT = str(root / "absent")
    expected["probes"] = None
    absent = m.recount(model, [])
    assert absent == expected
    assert "not counted (TestKit absent)" in m.counts_block(absent)


def regen_cases(m, root):
    root.mkdir(parents=True)
    m.STATE = str(root / "STATE.md")
    m.BUGS_DIR, m.FACTS_DIR = str(root / "bugs"), str(root / "facts")
    m.CLAUDE_MD, m.AGENTS_MD = str(root / "CLAUDE.md"), str(root / "AGENTS.md")
    # regen() ends by splicing tools/README.md; point it at an absent scratch
    # path so the leg can never write the live catalog.
    m.TOOLS_README = str(root / "tools-README.md")
    for directory in (m.BUGS_DIR, m.FACTS_DIR):
        Path(directory).mkdir()
    sb = types.SimpleNamespace(load_from_dir=lambda: {}, render_index=lambda model: ["index"])
    m.splitter = m.facts_splitter = lambda: sb
    m.regen_skills = lambda: []
    Path(m.CLAUDE_MD).write_bytes(b"entry\r\n")
    state = Path(m.STATE)
    for ending in (b"\n", b"\r\n"):
        original = b"# State\n\nOwner OWES: one scope ruling.\n".replace(b"\n", ending)
        state.write_bytes(original)
        m.regen([])
        assert state.read_bytes() == original, "regen rewrote hand-authored STATE"
        snapshots = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
        m.regen([])
        assert snapshots == {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
        assert Path(m.AGENTS_MD).read_bytes() == b"entry\n", "AGENTS.md is not LF CLAUDE.md"
        for directory in (m.BUGS_DIR, m.FACTS_DIR):
            assert (Path(directory) / "INDEX.md").read_bytes() == b"index\n"
    assert not Path(m.TOOLS_README).exists()


def cli_cases(m, root):
    # Isolate CLI routing from the repository-wide checks (this test included:
    # an unstubbed required_selftest would recurse into the falsifiers).
    sb = types.SimpleNamespace(load_from_dir=lambda: {}, SplitError=ValueError)
    m.splitter = m.facts_splitter = lambda: sb
    for name in ("check_entries", "check_index", "check_facts", "check_facts_index",
                 "check_agents_mirror", "check_skills", "check_prompt_map",
                 "check_rule_headers", "required_selftest", "check_tools_catalog",
                 "eol_report", "check_state", "check_state_admission",
                 "temporary_sweep", "load_order", "wrap_targets_check"):
        setattr(m, name, lambda *args: True)
    for name in ("push_set_report", "testkit_tree"):
        setattr(m, name, lambda out: None)
    # A gate added to main() later and not stubbed above must fail loudly here,
    # not quietly shell out against the real tree.
    m.subprocess = None
    m.recount = lambda model, out: COUNTS
    for green, emit in ((True, True), (False, True), (True, False)):
        m.check_root = lambda out: green
        output = io.StringIO()
        argv = ["doccheck.py"] + (["--emit-counts"] if emit else [])
        with patch.object(sys, "argv", argv), redirect_stdout(output):
            result = m.main()
        printed = output.getvalue()
        assert result == (0 if green else 1), printed
        assert (MARKER in printed) == (green and emit), printed
        assert ("BUILD STATE withheld" in printed) == (not green and emit), printed
        if green and emit:
            assert m.counts_block(COUNTS) in printed, printed


def main():
    live = ROOT / "tools/doccheck.py"
    original = live.read_bytes()
    source = original.decode("utf-8-sig").replace("\r\n", "\n")
    with tempfile.TemporaryDirectory(prefix="counts-") as directory:
        root = Path(directory)
        scratch = root / "doccheck.py"
        for cases in (recount_cases, regen_cases, cli_cases):
            cases(load_copy(scratch, source), root / cases.__name__)
            print("PASS", cases.__name__)
        mutants = (
            ("optional membership", 'counts["modules"] - counts["optional"]',
             'counts["modules"]', recount_cases),
            ("unanchored optional field",
             'OPTIONAL_FIELD_RE = re.compile(r"^\\s+optional = true,\\s*$", re.M)',
             'OPTIONAL_FIELD_RE = re.compile(r"optional = true")', recount_cases),
            ("STATE rewrite", '    wrote.extend("skill:" + n for n in regen_skills())\n',
             '    wrote.extend("skill:" + n for n in regen_skills())\n'
             '    open(STATE, "wb").close()\n', regen_cases),
            ("RED withholding", "print(counts_block(counts) if ok",
             "print(counts_block(counts) if True", cli_cases),
        )
        for i, (label, needle, replacement, cases) in enumerate(mutants):
            assert source.count(needle) == 1, label + " mutation is ambiguous"
            broken = load_copy(scratch, source.replace(needle, replacement))
            try:
                cases(broken, root / ("mutant-%d" % i))
            except AssertionError:
                print("PASS instrument mutant FAILS:", label)
            else:
                raise AssertionError(label + " mutant survived")
            cases(load_copy(scratch, source), root / ("restored-%d" % i))
    assert live.read_bytes() == original, "self-test wrote the live checker"
    print("PASS restored controls; live checker unchanged")


if __name__ == "__main__":
    main()
