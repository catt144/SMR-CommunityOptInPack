#!/usr/bin/env python3
# Provenance: ported from SMR-BugFixPack @ 8754e00 on 2026-09-18, unchanged; its dated history is the fix pack's.
"""Does every Lua file in the pack actually parse?

Written 2026-09-09 (hotfix2 link 05) to end a three-time recurrence. There is
no `lua` binary on this rig, so THREE consecutive chain links each hand-rolled a
block-balance checker to stand in for a syntax check -- and TWO of them silently
accused byte-identical, perfectly valid files:

  * link 01's counted a `for ... ipairs({` whose `do` sits on a later line as
    TWO openers and flagged `Fix_RocketInteractGuard`;
  * link 02's stripped comments and strings by regex, merged lines, and flagged
    SIXTEEN byte-identical files;
  * link 03 wrote a third, got the counting rule right, and recorded it -- but
    it stayed a scratchpad script, so a fourth session would have written a
    fourth.

⛔ THE RIGHT ANSWER IS NOT A BETTER BALANCE CHECKER. Every one of those bugs is
a bug in re-implementing Lua's grammar: which keywords open a block, what a `do`
belongs to, where a long bracket ends. A real parser cannot get those wrong
because it IS the grammar. `lupa` embeds one, it is on this rig, and `load()`
answers the exact question a balance count was approximating.

    python tools/parsecheck.py                  # the pack's Code/
    python tools/parsecheck.py --dir <path>     # another Code/ (e.g. the Test Kit)
    python tools/parsecheck.py --selftest       # the falsifier
    python tools/parsecheck.py --quiet          # one summary line

⚠️ WHAT THIS IS NOT. It is a SYNTAX gate and nothing more. A file that parses
can still be wrong in every way this project cares about -- it is weaker than
`sigcheck`, far weaker than `bodycheck`, and it clears nothing. Its whole job is
that a truncated function or an unbalanced `if` never reaches a commit, which
until now rested on a hand-written counter that had been wrong twice.

⚠️ AND THE DIALECT IS NOT PINNED. The embedded interpreter's version is printed
on every run, and it is not necessarily the engine's -- nothing in the shipped
tree or in our facts records which Lua the game runs, and `lua_revision`
(350453) is a content revision, not a language version. So this catches syntax
BOTH dialects reject, and could in principle pass something newer that the
engine would refuse. It has never had cause to: the pack uses no version-marked
syntax at all (no `<const>`/`<close>`, no `goto`), and neither does the shipped
tree. Treat a GREEN as "not obviously broken", never as "the engine will accept
this".
"""

import argparse
import glob
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(HERE, "Code")


def runtime():
    """(loader, version) or (None, why). An absent parser is REPORTED, never
    silently treated as a pass -- that is the whole failure mode this file is
    about."""
    try:
        import lupa
    except ImportError as exc:
        return None, "lupa not installed (%s)" % exc
    try:
        lua = lupa.LuaRuntime(encoding="utf-8")
        version = lua.eval("_VERSION")
        # returns nil on success, the parser's message on failure
        check = lua.eval("function(s, n) local f, e = load(s, n) "
                         "if f then return nil else return e end end")
    except Exception as exc:                                 # noqa: BLE001
        return None, "lupa present but unusable (%s)" % exc
    return check, version


def scan(directory, check):
    """-> [(path, error)] for every file that does not parse."""
    bad = []
    for path in sorted(glob.glob(os.path.join(directory, "*.lua"))):
        with open(path, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        err = check(src, "@" + os.path.basename(path))
        if err:
            bad.append((path, err))
    return bad


# --- the falsifier -----------------------------------------------------------
#
# ⛔ 01's condition, and it is the right one: this ships with its falsifier or
# not at all. Every RED leg below is a shape one of the three hand-rolled
# checkers actually got wrong, and the GREEN leg is the nasty-but-valid file
# that made two of them accuse clean code.

VALID_BUT_NASTY = '''\
local t = {}
for _, name in ipairs({
	"a", "b", "c",
}) do
	t[#t + 1] = name          -- the `do` sits on a LATER line than the `for`
end
local s = "this string contains the word end, twice: end"
--[[ and so does this long comment: end end end
     across several lines, with an if and a function in it ]]
local long = [[ a long string with ]inside] and the word end ]]
local nested = [==[ end ]] end ]==]
while true do break end
repeat
	local x = 1
until x == 1
local function f(a)
	if a then
		return (function() return 1 end)()
	elseif not a then
		return 2
	end
end
return f, t, s, long, nested
'''

BROKEN = [
    ("truncated function",
     "local function f()\n\tif true then\n\t\treturn 1\n\tend\n"),
    ("one `end` too many",
     "local function f()\n\treturn 1\nend\nend\n"),
    ("unterminated long string",
     "local s = [[ never closed\nreturn s\n"),
    ("unterminated long comment",
     "--[[ never closed\nlocal x = 1\nreturn x\n"),
    ("`for` with no `do`",
     "for i = 1, 10\n\tprint(i)\nend\n"),
    ("`repeat` with no `until`",
     "repeat\n\tlocal x = 1\nreturn x\n"),
]


def selftest():
    check, version = runtime()
    if check is None:
        print("SELFTEST CANNOT RUN: %s" % version)
        return 2
    print("parser: %s" % version)
    fails = []

    def leg(label, cond, detail=""):
        print("  %-4s %s%s" % ("ok" if cond else "FAIL", label,
                               ("   " + detail) if detail and not cond else ""))
        if not cond:
            fails.append(label)

    # THE GREEN LEG. Two of the three hand-rolled checkers went red on exactly
    # this file's shapes, on code that was byte-identical at HEAD.
    err = check(VALID_BUT_NASTY, "@nasty")
    leg("nasty-but-VALID file parses (the false-accusation shapes)",
        err is None, str(err))

    # THE RED LEGS. A checker that cannot go red is indistinguishable from one
    # that agrees with you.
    for label, src in BROKEN:
        leg("rejects: " + label, check(src, "@broken") is not None)

    print("=" * 78)
    if fails:
        print("SELFTEST FAILED: %s" % ", ".join(fails))
        return 1
    print("selftest: %d leg(s) pass. Syntax only -- a file that parses can still"
          % (1 + len(BROKEN)))
    print("be wrong in every way this project cares about. It clears nothing.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=CODE, help="directory of .lua files to parse")
    ap.add_argument("--quiet", action="store_true", help="one summary line")
    ap.add_argument("--selftest", action="store_true", help="the falsifier")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    check, version = runtime()
    if check is None:
        print("PARSE: not checked (%s)" % version)
        return 0                       # absent parser is reported, not a failure
    if not os.path.isdir(a.dir):
        print("PARSE: not checked (%s is not a directory)" % a.dir)
        return 0

    bad = scan(a.dir, check)
    total = len(glob.glob(os.path.join(a.dir, "*.lua")))
    if not a.quiet:
        for path, err in bad:
            print("PARSE ERROR  %s" % os.path.relpath(path, HERE))
            print("             %s" % err)
    print("PARSE: %d file(s) in %s, %d error(s) [%s]"
          % (total, os.path.relpath(a.dir, HERE), len(bad), version))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
