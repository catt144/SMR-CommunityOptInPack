#!/usr/bin/env python3
"""Falsifier for doccheck's STATE byte budget, the standing-prompt line budget and the skills mirror, on disk copies.

Run: python tools/ck170_selftest.py        # exit 0 = every leg fired

Ported from SMR-BugFixPack 2026-09-17 (its file of the same name, named for
the donor's checklist item 170). Carried: the byte legs against check_state
and the mirror legs against check_skills, both RED-capable gates here. Not
carried: the checklist-marker and owner-register legs (this repo has neither
gate), and the skill SIZE-cap legs (this repo never had the caps; see the
comment above SKILLS_DIR).

⚠️ Divergence kept visible, not tested away: this check_state counts RAW bytes,
where the donor counts LF-normalised ones, so the donor's LF/CRLF-equivalence
leg would fail here. The tree is pinned to LF (.gitattributes), so the caps
still read the same number; the leg is left out rather than made to pass.
"""
import hashlib
from pathlib import Path
import tempfile

from repair_pass_selftest import ROOT, load_copy


def byte_cases(m, root):
    root.mkdir(parents=True, exist_ok=True)
    path = root / "STATE.md"
    prompt = root / "WORK_PROMPT.md"
    m.STATE = str(path)
    m.STANDING_PROMPTS = [str(prompt), str(root / "absent.md")]
    m.STATE_MAX_BYTES, m.STATE_WARN_BYTES, m.STATE_MAX_LINE_BYTES = 14, 12, 5
    m.GENERAL_USE_MAX_LINES = 3
    good = b"abcde\nabcde\n"                      # 12 B: at the warn line, not over
    prompt.write_bytes(b"a\nb\nc\n")
    path.write_bytes(good)
    out = []
    assert m.check_state(out), out
    assert not any(x.startswith(("  warn ", "  RED ")) for x in out), out
    for ending in (b"\n", b"\r\n"):
        for label, data, expected in (
            ("total cap", good + b"xxx\n", "hard cap"),
            ("line cap", b"abcdef\n", "per-line cap"),
        ):
            path.write_bytes(data.replace(b"\n", ending))
            out = []
            assert not m.check_state(out), (label, out)
            assert any(expected in x for x in out), (label, out)
            print("PASS byte broken copy FAILS: %s (%r)" % (label, ending))
    path.write_bytes(good + b"x\n")               # 14 B: over warn, at the cap
    out = []
    assert m.check_state(out), out
    assert any("warn threshold" in x for x in out), out
    print("PASS warn fires without RED between the two thresholds")
    path.unlink()
    out = []
    assert not m.check_state(out) and any("STATE.md is missing" in x for x in out), out
    print("PASS missing STATE FAILS")
    path.write_bytes(good)
    prompt.write_bytes(b"a\nb\nc\nd\n")
    out = []
    assert not m.check_state(out) and any("budget is 3" in x for x in out), out
    print("PASS standing prompt over its line budget FAILS")
    prompt.write_bytes(b"a\nb\nc\n")
    assert m.check_state([])
    assert path.read_bytes() == good
    print("RESTORED STATE SHA256 " + hashlib.sha256(path.read_bytes()).hexdigest())


def skill_cases(m, root):
    m.SKILLS_DIR = str(root / "skills")
    m.CODEX_SKILLS_DIR = str(root / "mirror")
    src, dst = [Path(base) / "fixture/SKILL.md"
                for base in (m.SKILLS_DIR, m.CODEX_SKILLS_DIR)]
    good = b"abcde\nabcde\n"
    for p in (src, dst):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(good)
    assert m.check_skills([])
    for label, data in (("content drift", good + b"x\n"),
                        ("CRLF-only drift", good.replace(b"\n", b"\r\n"))):
        dst.write_bytes(data)
        out = []
        assert not m.check_skills(out), (label, out)
        assert any("differs between" in x for x in out), (label, out)
        print("PASS mirror broken copy FAILS: " + label)
    dst.unlink()
    out = []
    assert not m.check_skills(out) and any("is missing" in x for x in out), out
    print("PASS missing mirror FAILS")
    dst.write_bytes(good)
    assert m.check_skills([])
    assert src.read_bytes() == good and dst.read_bytes() == good
    print("RESTORED skill copies SHA256 " + hashlib.sha256(good).hexdigest())


def main():
    live = ROOT / "tools/doccheck.py"
    original = live.read_bytes()
    source = original.decode("utf-8-sig")
    with tempfile.TemporaryDirectory(prefix="ck170-") as directory:
        root = Path(directory)
        scratch = root / "doccheck.py"
        m = load_copy(scratch, source)
        byte_cases(m, root / "control")
        skill_cases(m, root / "control")
        # Each mutant silences one red; the leg that owns it must then FAIL.
        mutants = (
            ("hard cap", "if n_state > STATE_MAX_BYTES:", "if False:", byte_cases),
            ("per-line cap", "if len(ln) > STATE_MAX_LINE_BYTES:", "if False:", byte_cases),
            ("mirror comparison", "if a.read() != b.read():", "if False:", skill_cases),
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
        restored = load_copy(scratch, source)
        byte_cases(restored, root / "restored")
        skill_cases(restored, root / "restored")
        assert scratch.read_bytes() == source.encode()
        print("RESTORED doccheck copy SHA256 " + hashlib.sha256(scratch.read_bytes()).hexdigest())
    assert live.read_bytes() == original
    print("UNCHANGED live doccheck SHA256 " + hashlib.sha256(original).hexdigest())


if __name__ == "__main__":
    main()
