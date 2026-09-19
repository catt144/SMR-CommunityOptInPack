#!/usr/bin/env python3
"""Falsifier for doccheck's --emit-fingerprint build routing and pack-ignore parity, and home of the scratch-copy loader the other falsifiers import.

Run: python tools/repair_pass_selftest.py        # exit 0 = every leg fired

Ported from SMR-BugFixPack 2026-09-17 (its file of the same name). The
donor's marker-integrity legs are not carried: they exercise a checklist-marker
gate this repo never had, and a leg for a gate that does not exist would pass
for the wrong reason. Its pack-ignore parity legs (03fc504) followed on
2026-09-18 with the gate itself, drifting patterns THIS repo's list holds.
Its TOOLS COMPILE (C1) and FLPK SELFTEST (C2) legs (5bb1b44) followed on
2026-09-19; C2 falsifies the RED-when-absent branch this repo already had.

Each demand is paired with a control, then rerun against a reverted scratch
copy of doccheck.py that must FAIL it. Mutants execute only in a temporary
directory; the live checker is hashed before and after.
"""
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def load_copy(path, source):
    """Write SOURCE to PATH and execute it as a fresh module. Shared by every falsifier here."""
    path.write_bytes(source.encode("utf-8"))
    module = types.ModuleType("repair_scratch")
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def fingerprint_cases(module):
    """Exact build identity HOLDS; a prefix, an extension or no build does not."""
    module.facts_splitter = lambda: types.SimpleNamespace(
        load_from_dir=lambda: {"facts": [{"derived_at": "game 1.1.0 build 24995074"}]})
    for build, expected in (("24995074", "HOLDS"), ("2499507", "MOVED"),
                            ("249950740", "MOVED"), (None, "cannot check")):
        module.installed_build = lambda: build
        out = []
        module.emit_fingerprints(out)
        assert any(expected in x for x in out), (build, out)


def parity_cases(module, root):
    """Drift real list copies without ever mutating the live metadata."""
    metadata = root / "metadata.lua"
    predictor = root / "tools/pack_predict.py"
    predictor.parent.mkdir(exist_ok=True)
    metadata.write_bytes((ROOT / "metadata.lua").read_bytes())
    predictor.write_bytes((ROOT / "tools/pack_predict.py").read_bytes())
    originals = {p: p.read_bytes() for p in (metadata, predictor)}
    original_repo = module.REPO
    module.REPO = str(root)
    try:
        out = []
        assert module.pack_ignore_parity(out), out
        print("CONTROL " + out[0])
        source = predictor.read_text(encoding="utf-8-sig")
        # The donor drops "*.rgignore", which this repo's list does not carry;
        # a drift that changes nothing would be a vacuous leg.
        for label, drift in (
            ("membership", source.replace('    "*.gitignore",\n', "")),
            ("order", source.replace('    "*.git/*",\n    "*.svn/*",',
                                     '    "*.svn/*",\n    "*.git/*",')),
        ):
            assert drift != source, label + " drift matched nothing"
            predictor.write_bytes(drift.encode("utf-8"))
            out = []
            result = module.pack_ignore_parity(out)
            assert not result and any("PACK IGNORE PARITY: RED" in x for x in out), out
            print(label.upper() + " " + out[0])
            predictor.write_bytes(originals[predictor])
        out = []
        assert module.pack_ignore_parity(out), out
        print("RESTORED " + out[0])
        for path, content in originals.items():
            assert path.read_bytes() == content
            print("RESTORED %s SHA256 %s" % (path.name, hashlib.sha256(content).hexdigest()))
    finally:
        module.REPO = original_repo
        for path, content in originals.items():
            path.write_bytes(content)


def compile_cases(module, root):
    """TOOLS COMPILE over a scratch copy of every live tools/*.py.

    Control: the clean copy passes. Demand: a syntax error planted at the end
    of one copy goes RED and names that file and line.
    """
    tools = root / "compile-tools"
    shutil.rmtree(tools, ignore_errors=True)
    tools.mkdir()
    for path in sorted((ROOT / "tools").glob("*.py")):
        shutil.copyfile(path, tools / path.name)
    original_dir = module.TOOLS_DIR
    module.TOOLS_DIR = str(tools)
    try:
        out = []
        assert module.tools_compile(out), out
        assert out[0].startswith("TOOLS COMPILE: PASS"), out
        print("CONTROL " + out[0])
        planted = tools / "pack_list.py"
        good = planted.read_bytes()
        assert good.endswith(b"\n")
        line = good.count(b"\n") + 1
        planted.write_bytes(good + b"def broken(:\n")
        out = []
        assert not module.tools_compile(out), out
        assert out[0].startswith("TOOLS COMPILE: RED"), out
        assert any("tools/pack_list.py:%d:" % line in x for x in out), out
        print("PLANTED " + out[0] + " | " + out[1].strip())
        planted.write_bytes(good)
        out = []
        assert module.tools_compile(out), out
        print("RESTORED " + out[0])
    finally:
        module.TOOLS_DIR = original_dir


def flpk_cases(module, root):
    """FLPK SELFTEST: present passes; absent, unspawnable or failing is RED."""
    tree = root / "flpk-tree"
    tool = tree / "tools" / "flpk_extract.py"
    tool.parent.mkdir(parents=True, exist_ok=True)
    live = (ROOT / "tools" / "flpk_extract.py").read_bytes()
    tool.write_bytes(live)
    original_repo = module.REPO
    module.REPO = str(tree)
    try:
        out = []
        assert module.flpk_selftest(out), out
        print("CONTROL " + out[0])
        tool.unlink()
        out = []
        assert not module.flpk_selftest(out), out
        assert out[0].startswith("FLPK SELFTEST: RED") and "absent" in out[0], out
        print("ABSENT " + out[0])
        tool.write_bytes(live)
        with patch.object(module.subprocess, "run", side_effect=OSError("spawn refused")):
            out = []
            assert not module.flpk_selftest(out), out
        assert out[0].startswith("FLPK SELFTEST: RED") and "could not run" in out[0], out
        print("UNSPAWNABLE " + out[0])
        tool.write_bytes(b"import sys\nsys.exit(1)\n")
        out = []
        assert not module.flpk_selftest(out), out
        assert out[0].startswith("FLPK SELFTEST: RED") and "FAILED" in out[0], out
        print("FAILING " + out[0][:60])
        tool.write_bytes(live)
        out = []
        assert module.flpk_selftest(out), out
        print("RESTORED " + out[0])
    finally:
        module.REPO = original_repo


def main():
    live = ROOT / "tools/doccheck.py"
    original = live.read_bytes()
    source = original.decode("utf-8-sig")
    digest = hashlib.sha256(source.encode()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="smr-repair-") as directory:
        scratch = Path(directory) / "doccheck.py"
        fingerprint_cases(load_copy(scratch, source))
        print("PASS fingerprint control and demands on the live copy")
        # Revert exact identity to substring containment: a build id that is a
        # PREFIX of the pinned one would then read as HOLDS.
        needle = "elif hit and hit.group(1) == build:"
        assert source.count(needle) == 1, "fingerprint mutation is ambiguous"
        broken = load_copy(scratch, source.replace(needle, "elif hit and build in bare:"))
        try:
            fingerprint_cases(broken)
        except AssertionError as error:
            assert error.args[0][0] == "2499507", error
            print("PASS reverted scratch: exact control passes, prefix demand FAILS")
        else:
            raise AssertionError("fingerprint mutant survived")
        restored = load_copy(scratch, source)
        fingerprint_cases(restored)
        # Pack-ignore parity: control + two drifts on the live copy, then a
        # mutant that always passes must FAIL the drift demand.
        parity_cases(restored, Path(directory))
        start = source.index("def pack_ignore_parity(")
        end = source.index("\n\n\ndef ", start)
        broken = load_copy(scratch, source[:start] + (
            'def pack_ignore_parity(out):\n'
            '    out.append("PACK IGNORE PARITY: PASS (mutant)")\n'
            '    return True\n') + source[end:])
        try:
            parity_cases(broken, Path(directory))
        except AssertionError:
            print("PASS reverted scratch: parity control passes, drift demand FAILS")
        else:
            raise AssertionError("parity mutant survived")
        restored = load_copy(scratch, source)
        fingerprint_cases(restored)
        parity_cases(restored, Path(directory))
        # C1: every tools/*.py byte-compiles. A gate that always passes must
        # not satisfy the planted-error demand.
        root = Path(directory)
        compile_cases(restored, root)
        start = source.index("def tools_compile(")
        end = source.index("\n\n\ndef ", start)
        mutant = source[:start] + (
            'def tools_compile(out):\n'
            '    out.append("TOOLS COMPILE: PASS (mutant)")\n'
            '    return True\n') + source[end:]
        try:
            compile_cases(load_copy(scratch, mutant), root)
        except AssertionError:
            print("PASS C1 reverted scratch: clean control passes, planted error FAILS")
        else:
            raise AssertionError("C1 mutant survived")
        # C2: the FLPK gate cannot vanish green. Each mutant is the donor's
        # pre-fix body of one branch ("not checked", passing).
        restored = load_copy(scratch, source)
        flpk_cases(restored, root)
        for label, needle, replacement in (
            ("absent",
             '        out.append("FLPK SELFTEST: RED — tools/flpk_extract.py is absent "\n'
             '                   "(pack_list.py imports its parser)")\n'
             '        return False\n',
             '        out.append("FLPK SELFTEST: not checked (tools/flpk_extract.py absent)")\n'
             '        return True\n'),
            ("unspawnable",
             '        out.append("FLPK SELFTEST: RED — could not run (%s)" % exc)\n'
             '        return False\n',
             '        out.append("FLPK SELFTEST: not checked (%s)" % exc)\n'
             '        return True\n'),
        ):
            assert source.count(needle) == 1, label + " mutation is ambiguous"
            try:
                flpk_cases(load_copy(scratch, source.replace(needle, replacement)), root)
            except AssertionError:
                print("PASS C2 reverted scratch (%s): control passes, demand FAILS" % label)
            else:
                raise AssertionError("C2 %s mutant survived" % label)
        restored = load_copy(scratch, source)
        fingerprint_cases(restored)
        compile_cases(restored, root)
        flpk_cases(restored, root)
        assert hashlib.sha256(scratch.read_bytes()).hexdigest() == digest
        print("RESTORED doccheck.py SHA256 " + digest)
    assert live.read_bytes() == original, "self-test wrote the live checker"


if __name__ == "__main__":
    main()
