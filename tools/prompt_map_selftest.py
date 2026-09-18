#!/usr/bin/env python3
"""Falsifier for doccheck's PROMPT MAP gate: one broken fixture per red it claims to raise.

Run: python tools/prompt_map_selftest.py        # exit 0 = every leg fired

Ported from SMR-BugFixPack 2026-09-17 (its file of the same name), adapted to
this doccheck's gate as it actually is: every perma and root row must declare
`prompt` and every chain row `live`. The donor's `ledger-exception` row and its
migration-allowance cases are dropped, because this repo carries neither class
(see the comment above PROMPT_MAP_DEFAULT_CLASSES). Fixtures are disposable
directories; the live doccheck is loaded from a scratch copy and hashed.
"""
import hashlib
from pathlib import Path
import shutil
import tempfile

from repair_pass_selftest import ROOT, load_copy


GOOD_MAP = """# fixture prompt map

## `perma/` — standing prompts

| prompt | declared class | use |
|---|---|---|
| `PROMPT.md` | `prompt` | fixture prompt |

## Root — live one-offs

| prompt | declared class | state |
|---|---|---|
| `ONE.md`, `TWO.md` | `prompt` | grouped fixture prompts |

## Chain folders

| chain | declared class | state |
|---|---|---|
| `live-a/`, `live-b/` | `live` | grouped live fixture chains |
"""


def make_fixture(module, root):
    docs = root / "docs"
    prompts = docs / "agent" / "prompts"
    perma = prompts / "perma"
    perma.mkdir(parents=True)
    (perma / "PROMPT.md").write_text("fixture\n", encoding="utf-8")
    for name in ("ONE.md", "TWO.md"):
        (prompts / name).write_text("fixture\n", encoding="utf-8")
    (prompts / "README.md").write_text(GOOD_MAP, encoding="utf-8")
    (prompts / "live-a").mkdir()
    (prompts / "live-a" / "README.md").write_text("fixture\n", encoding="utf-8")
    (prompts / "live-a" / "evidence.json").write_text("{}\n", encoding="utf-8")
    (prompts / "live-b").mkdir()
    (prompts / "live-b" / "evidence.txt").write_text("fixture\n", encoding="utf-8")
    module.DOCS = str(docs)
    return prompts


def rewrite_map(prompts, old, new):
    path = prompts / "README.md"
    body = path.read_text(encoding="utf-8")
    assert old in body
    path.write_text(body.replace(old, new), encoding="utf-8")


def run_case(module, root, label, mutate, should_pass, needle=None):
    prompts = make_fixture(module, root / label.replace(" ", "-"))
    if mutate is not None:
        mutate(prompts)
    out = []
    result = module.check_prompt_map(out)
    assert result is should_pass, (label, out)
    if should_pass:
        assert any(line.startswith("PROMPT MAP: PASS") for line in out), out
    else:
        assert any(line.startswith("PROMPT MAP: RED") for line in out), out
    if needle is not None:
        assert any(needle in line for line in out), (label, needle, out)
    print("PASS %s: %s" % (label, "gate passes" if result else "broken fixture fails"))
    return out


def main():
    live = ROOT / "tools" / "doccheck.py"
    original = live.read_bytes()
    source = original.decode("utf-8-sig")
    with tempfile.TemporaryDirectory(prefix="prompt-map-") as directory:
        root = Path(directory)
        module = load_copy(root / "doccheck.py", source)

        # Control: chain folders holding a README and evidence are permitted,
        # and the map itself is not read as an unmapped root prompt.
        run_case(module, root, "mapped live evidence and map", None, True,
                 "1 perma + 2 one-off + 2 chain row(s) agree")

        run_case(module, root, "missing map",
                 lambda p: (p / "README.md").unlink(), False, "README.md is missing")
        run_case(module, root, "missing perma",
                 lambda p: shutil.rmtree(p / "perma"), False, "perma/ is missing")
        run_case(module, root, "unmapped chain",
                 lambda p: (p / "unmapped").mkdir(), False, "unmapped/ exists")
        run_case(module, root, "unmapped root prompt",
                 lambda p: (p / "STRAY.md").write_text("x\n"), False, "STRAY.md exists")
        run_case(module, root, "unmapped perma prompt",
                 lambda p: (p / "perma" / "STRAY.md").write_text("x\n"), False,
                 "perma/STRAY.md exists")
        run_case(module, root, "mapped missing chain",
                 lambda p: rewrite_map(
                     p, "| `live-a/`, `live-b/` | `live` |",
                     "| `live-a/`, `live-b/`, `missing/` | `live` |"), False,
                 "row for missing/")
        run_case(module, root, "mapped missing root prompt",
                 lambda p: (p / "TWO.md").unlink(), False, "row for TWO.md")
        run_case(module, root, "mapped missing perma prompt",
                 lambda p: (p / "perma" / "PROMPT.md").unlink(), False,
                 "row for perma/PROMPT.md")
        run_case(module, root, "wrong class at perma",
                 lambda p: rewrite_map(
                     p, "| `PROMPT.md` | `prompt` |",
                     "| `PROMPT.md` | `support-migration-leg-03` |"), False,
                 "requires `prompt`")
        run_case(module, root, "wrong class at root",
                 lambda p: rewrite_map(
                     p, "| `ONE.md`, `TWO.md` | `prompt` |",
                     "| `ONE.md`, `TWO.md` | `ledger-exception` |"), False,
                 "requires `prompt`")

        def closed_chain(prompts):
            (prompts / "old").mkdir()
            rewrite_map(
                prompts, "| `live-a/`, `live-b/` | `live` |",
                "| `live-a/`, `live-b/` | `live` |\n"
                "| `old/` | `closed-migration-leg-02` | closed |")

        run_case(module, root, "closed chain declared", closed_chain, False,
                 "requires `live`")
        run_case(module, root, "two declared classes",
                 lambda p: rewrite_map(
                     p, "| `PROMPT.md` | `prompt` |",
                     "| `PROMPT.md` | `prompt` `live` |"), False,
                 "exactly one declared class")
        run_case(module, root, "repeated row",
                 lambda p: rewrite_map(
                     p, "| `ONE.md`, `TWO.md` | `prompt` |",
                     "| `ONE.md`, `TWO.md` | `prompt` |\n| `ONE.md` | `prompt` |"),
                 False, "repeats root/ONE.md")
        run_case(module, root, "struck map row",
                 lambda p: rewrite_map(
                     p, "| `ONE.md`, `TWO.md` | `prompt` |",
                     "| ~~`ONE.md`, `TWO.md`~~ | `prompt` |"), False,
                 "struck-through row")

    assert live.read_bytes() == original
    print("UNCHANGED live doccheck SHA256 " + hashlib.sha256(original).hexdigest())


if __name__ == "__main__":
    main()
