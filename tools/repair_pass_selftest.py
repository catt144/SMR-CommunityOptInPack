#!/usr/bin/env python3
"""Falsifier for doccheck's --emit-fingerprint build routing, and home of the scratch-copy loader the other falsifiers import.

Run: python tools/repair_pass_selftest.py        # exit 0 = every leg fired

Ported from SMR-BugFixPack 2026-09-17 (its file of the same name). Only the
fingerprint legs are carried: the donor's marker-integrity legs exercise a
checklist-marker gate this repo never had, and its pack-ignore parity legs a
gate this doccheck does not define. A leg for a gate that does not exist would
pass for the wrong reason.

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
        assert hashlib.sha256(scratch.read_bytes()).hexdigest() == digest
        print("RESTORED doccheck.py SHA256 " + digest)
    assert live.read_bytes() == original, "self-test wrote the live checker"


if __name__ == "__main__":
    main()
