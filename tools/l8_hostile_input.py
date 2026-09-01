#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Provenance: carried from the fix pack 2026-08-31 — docs/agent/PROVENANCE.md §6.
"""L8 (adversarial / hostile modder) — hostile-input harness for this mod's
PUBLIC globals.

WHY THIS EXISTS
    `SMROptInPack_Disabled`, `SMROptInPack_Optional` and `SMROptInPack` are not private
    names. `00_Core.lua:11`/`:15`/`:17` each read them with `rawget(_G, ...) or {}`,
    which is an explicit contract: *another mod may create this before we load and
    we will adopt it*. `00_Core.lua:6-7` publishes that contract to modders, and
    `EF-064`'s route (`ModEnvMeta.__newindex` rawsets into the real `_G` in every
    branch, `Mod.lua:1562`) means a foreign mod's write really does reach us.

    ⇒ Three globals are an INPUT SURFACE, and their values are supplied by code
    this project does not control and has never seen. Nothing in this project has
    ever fed them anything but a well-formed table.

WHAT IT DOES
    Runs the REAL shipped source of Code/00_Core.lua plus real modules under a
    Lua 5.4 runtime (lupa), once per hostile value, with the engine's own
    containment reproduced:
      * each Code/*.lua runs inside its OWN pcall — that is `pdofile`
        (`lib.lua:242-251`), so a file-scope throw kills exactly that file and the
        others still load (`EF-065` (b));
      * a file that throws never reaches its `Register`, so its id is ABSENT from
        `SMROptInPack.fixes` and `order` — not `inactive`. The harness reports
        absent and errored separately for that reason.

    THE CONTROL runs first and is not decoration: the documented benign value
    must produce the documented behaviour (`<id>: disabled by user/mod setting`,
    status `disabled`) before any hostile result below it is evidence about
    anything.

USAGE
    python tools/l8_hostile_input.py           # the matrix
    python tools/l8_hostile_input.py --strict  # exit 1 if any hostile value
                                               # takes down a module
"""

import os
import sys

# The reports are full of non-cp1252 markup (⛔ ⭐ ⚠️ ⇒); a Windows console must
# not die on printing a finding (same guard as doccheck.py / l2_reload_sim.py).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

try:
    import lupa
except ImportError:  # pragma: no cover
    sys.exit("l8_hostile_input: needs `lupa` (pip install lupa)")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(ROOT, "Code")

# 00_Core plus three real modules chosen for shape, not for convenience:
#   * ClassicRockets   — the Require path, install at file scope guarded by it
#   * DroneStatDials   — reads SMROptInPack_Disabled at file scope, registers
#                        WITHOUT `optional` (the one default-active module)
#   * NoHomeless       — the largest module; a SetGlobal wrapper plus UI Init wraps
MODULES = ["00_Core.lua",
           "Opt_ClassicRockets.lua",
           "Opt_DroneStatDials.lua",
           "Opt_NoHomeless.lua"]

# --------------------------------------------------------------------------
# The engine stubs. Reproduced from Src where behaviour matters; never a
# stand-in for our own code, which is always loaded from Code/ verbatim.
# --------------------------------------------------------------------------

BOOT = r"""
SMRSIM = { log = {}, threads = 0 }
function ModLog(msg) SMRSIM.log[#SMRSIM.log + 1] = string.format(msg) end

SMRSIM_msgs = {}
OnMsg = setmetatable({}, { __newindex = function(_, name, fn)
    local t = SMRSIM_msgs[name]
    if not t then t = {}; SMRSIM_msgs[name] = t end
    t[#t + 1] = fn
end })
-- cthreads.lua:15-21 — Msg calls handlers through `procall`, which SWALLOWS.
function Msg(name, ...)
    for _, fn in ipairs(SMRSIM_msgs[name] or {}) do
        local ok, err = pcall(fn, ...)
        if not ok then SMRSIM.log[#SMRSIM.log + 1] = "SIMERROR " .. tostring(err) end
    end
end

function CreateRealTimeThread(fn) SMRSIM.threads = SMRSIM.threads + 1 end
function CreateGameTimeThread(fn) SMRSIM.threads = SMRSIM.threads + 1 end
function RealTime() return 0 end
function GameTime() return 0 end
function Sleep(ms) end
function Untranslated(s) return s end
function T(id, s) return s end
function GetPreGameMainMenu() return nil end
function WaitMessage() end
function IsValid() return false end
function AllMapsForEach() end
function MapForEach() end
function PlaceObj(cls, t) t = t or {}; t.class = cls; return t end
function GameVar(name, default) _G[name] = default end
function OverrideDisasterDescriptor(x) return x end
function GetDustDevilsDescr() return {} end
function StopMeteors() end
function StartMeteors() end
empty_table = {}
CurrentModOptions = false
Mods = false
DataLoaded = false

-- Whatever the game already has that our modules probe for. Kept deliberately
-- thin: a module that self-checks its target away and returns `inactive` is a
-- perfectly good outcome here — this harness measures THROWS, not coverage.
Meteors = false
SessionRandom = false
"""

# --------------------------------------------------------------------------
# The hostile values. Each is something a real modder could plausibly write, or
# a real fork could plausibly leave behind — not fuzzing for its own sake.
# --------------------------------------------------------------------------

CASES = [
    # (label, lua seed, why a real person would write this)
    ("CONTROL — the documented form",
     'SMROptInPack_Disabled = { ClassicRockets = true }',
     "00_Core.lua:6-7, verbatim. Must veto exactly one module."),

    ("CONTROL — nothing set at all",
     '',
     "the shipping case: no foreign mod, no console. Must veto nothing."),

    ("SMROptInPack_Disabled = true",
     'SMROptInPack_Disabled = true',
     'the natural misreading of "set SMROptInPack_Disabled to disable a fix"'),

    ('SMROptInPack_Disabled = "ClassicRockets"',
     'SMROptInPack_Disabled = "ClassicRockets"',
     'the other natural misreading — name the fix directly'),

    ('SMROptInPack_Disabled = {"ClassicRockets"}',
     'SMROptInPack_Disabled = {"ClassicRockets"}',
     'the LIST form: "setting a fix\'s identifier in that table" reads as a list'),

    ("SMROptInPack_Optional = true",
     'SMROptInPack_Optional = true',
     "the same misreading on this mod's other published override surface"),

    ("SMROptInPack = true",
     'SMROptInPack = true',
     "a foreign mod squatting the namespace, or a crude 'is it installed' flag"),

    ("SMROptInPack = {} (a fork or an older copy)",
     'SMROptInPack = {}',
     "a fork, a second copy of this mod, or a shim that reserves the table"),

    ("SMROptInPack = {fixes={}, order={}} (partial)",
     'SMROptInPack = { fixes = {}, order = {} }',
     "a shim that knows the two documented sub-tables and not the two later ones"),

    ("SMROptInPack_Disabled with a throwing __index",
     'SMROptInPack_Disabled = setmetatable({}, {__index = function() error("hostile") end})',
     "a mod implementing a dynamic veto policy, or simply a buggy proxy table"),
]


def run_case(seed):
    """Load the shipped source under one seeded _G. Returns (per-file results, log,
    registry snapshot). Each file gets its own pcall == pdofile (lib.lua:242-251)."""
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(BOOT)
    if seed:
        lua.execute(seed)

    files = []
    for m in MODULES:
        with open(os.path.join(CODE, m), encoding="utf-8") as f:
            src = f.read()
        # loadstring + pcall, mirroring pdofile's pcall(loadfile(...))
        lua.execute('SMRSIM_chunk = %s' % _lua_longstring(src))
        ok = lua.eval('(function() '
                      '  local fn, err = load(SMRSIM_chunk, "%s") '
                      '  if not fn then return "COMPILE: " .. tostring(err) end '
                      '  local ok2, err2 = pcall(fn) '
                      '  if ok2 then return true end '
                      '  return tostring(err2) '
                      'end)()' % m)
        files.append((m, ok))

    log = list(lua.eval("SMRSIM.log").values()) if lua.eval("#SMRSIM.log") else []
    reg = {}
    have = lua.eval('type(SMROptInPack) == "table" and type(SMROptInPack.fixes) == "table"')
    if have:
        ids = lua.eval("SMROptInPack.order")
        for i in range(1, int(lua.eval("#SMROptInPack.order")) + 1):
            fid = ids[i]
            e = lua.eval('SMROptInPack.fixes["%s"]' % fid)
            reg[fid] = e["status"]
    return files, log, reg


def _lua_longstring(src):
    """Wrap source in a Lua long-bracket literal deep enough not to collide."""
    n = 0
    while ("]" + "=" * n + "]") in src or ("[" + "=" * n + "[") in src:
        n += 1
    eq = "=" * n
    return "[" + eq + "[\n" + src + "]" + eq + "]"


def main():
    strict = "--strict" in sys.argv
    modules_expected = len(MODULES) - 1     # 00_Core is not a fix module
    worst = 0

    print("=" * 78)
    print("L8 — hostile input to this mod's three PUBLIC globals")
    print("    shipped source, %d files, each in its own pcall (pdofile, lib.lua:242-251)" % len(MODULES))
    print("=" * 78)

    for label, seed, why in CASES:
        files, log, reg = run_case(seed)
        dead = [(m, err) for m, err in files if err is not True]
        loaded = len(files) - len(dead)
        absent = modules_expected - len([k for k in reg])
        print()
        print("-" * 78)
        print("CASE  %s" % label)
        print("      %s" % why)
        print("      files loaded: %d/%d   registered: %d/%d   ABSENT: %d"
              % (loaded, len(files), len(reg), modules_expected, max(absent, 0)))
        for m, err in dead:
            first = str(err).strip().splitlines()[0]
            print("      DEAD  %-32s %s" % (m, first))
        for fid, st in reg.items():
            print("      reg   %-32s %s" % (fid, st))
        for line in log:
            if "disabled by user/mod setting" in line or line.startswith("SIMERROR"):
                print("      log   %s" % line.replace("[CommunityOptInPack] ", ""))
        if dead and not label.startswith("CONTROL"):
            worst = max(worst, len(dead))

    print()
    print("=" * 78)
    if strict and worst:
        print("FAIL: at least one hostile value took down %d shipped file(s)." % worst)
        return 1
    print("done. --strict exits 1 when any non-control case kills a file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
