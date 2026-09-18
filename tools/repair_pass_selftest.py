#!/usr/bin/env python3
"""Falsifier for doccheck's --emit-fingerprint build routing and pack-ignore parity, and home of the scratch-copy loader the other falsifiers import.

Run: python tools/repair_pass_selftest.py        # exit 0 = every leg fired

Ported from SMR-BugFixPack 2026-09-17 (its file of the same name). The
donor's marker-integrity legs are not carried: they exercise a checklist-marker
gate this repo never had, and a leg for a gate that does not exist would pass
for the wrong reason. Its pack-ignore parity legs (03fc504) followed on
2026-09-18 with the gate itself, drifting patterns THIS repo's list holds.

Each demand is paired with a control, then rerun against a reverted scratch
copy of doccheck.py that must FAIL it. Mutants execute only in a temporary
directory; the live checker is hashed before and after.
"""
import hashlib
from pathlib import Path
import sys
import tempfile
import types

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
        assert hashlib.sha256(scratch.read_bytes()).hexdigest() == digest
        print("RESTORED doccheck.py SHA256 " + digest)
    assert live.read_bytes() == original, "self-test wrote the live checker"


if __name__ == "__main__":
    main()
