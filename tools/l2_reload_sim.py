#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ADAPTED 2026-08-31 from SMR-BugFixPack @ bec2e06 (tools/l2_reload_sim.py). The
# donor's simulator is built around four DataPatch modules and their preset
# fixtures; no Opt_* module calls DataPatch, so the fixtures are N/A here. What
# is carried is the METHOD — real shipped source, twice, in one Lua 5.4 process,
# with the engine's reload persistence rules reproduced — pointed at the one
# lifecycle defect this repo has MEASURED: double registration after ReloadLua.
# Ledger: docs/agent/PROVENANCE.md section 6.
"""L2 (lifecycle & idempotency) — two-Lua-load simulator for the registry.

WHY THIS EXISTS
    `ReloadLua` re-executes every mod file in the SAME process (lib.lua:353-382 ->
    autorun.lua `ModsLoadCode()`), and `SMROptInPack` is deliberately preserved
    across it (`rawget(_G, "SMROptInPack") or {...}`, Code/00_Core.lua:17). Until
    2026-08-20 `Register` appended to `order` unconditionally, so every reload
    pushed a SECOND copy of each id — MEASURED on this mod on 2026-08-17: the
    update dialog read "2 of this mod's modules … NoHomeless, NoHomeless" over ONE
    module (STATE.md; the guard is Code/00_Core.lua:402-420). The guard was
    mirrored here from the fix pack's repair (2f077e8) and STATE records it as
    NOT verified in a running game in this repo. This is the desk half of that
    verification: it cannot replace the boot check, but it can fail.

WHAT IT DOES
    Runs the REAL shipped source of every file in metadata.lua's `code` list
    under a Lua 5.4 runtime (lupa), twice in one process, with:
      * `SMROptInPack`, `SMROptInPack_Disabled`, `SMROptInPack_Optional`
        PERSISTING between loads (they are `rawget(_G, ...) or {}` globals);
      * the OnMsg store DISCARDED between loads (`message_to_staticfuncs` is a
        plain file-local, cthreads.lua:6);
      * no game classes at all — every module's target check fails and it reports
        `inactive`, which is fine: this instrument measures REGISTRATION, not
        coverage. A module that throws at file scope is reported as such.

    Verdict after load 2: every id in `order` exactly once, `#order` == the
    number of registering files, one apply-verdict log line per id per load.

CONTROL (the falsifier — a simulator that cannot reproduce the measurement is
    not evidence about it): `--core <path>` swaps in another 00_Core.lua. Run it
    on the pre-guard core from git and the tool MUST report the doubling:
        git show 2cedf7d~1:Code/00_Core.lua > <scratch>/old_core.lua
        python tools/l2_reload_sim.py --core <scratch>/old_core.lua
    → expected: 16 order entries, every id twice. `--expect-doubling` exits 1 if
    it does not see that, so the control can be scripted.

USAGE
    python tools/l2_reload_sim.py                      # report both loads
    python tools/l2_reload_sim.py --strict             # exit 1 on any duplicate
    python tools/l2_reload_sim.py --core F --expect-doubling   # the control
"""

import os
import re
import sys

try:
    import lupa
except ImportError:  # pragma: no cover
    sys.exit("l2_reload_sim: needs `lupa` (pip install lupa)")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(ROOT, "Code")
METADATA = os.path.join(ROOT, "metadata.lua")
LOG_PREFIX = "[CommunityOptInPack] "


def code_list():
    """metadata.lua's `code` list, in order — the order the engine loads in."""
    with open(METADATA, encoding="utf-8-sig") as fh:
        text = fh.read()
    return re.findall(r'"Code/([^"]+\.lua)"', text)


# ---------------------------------------------------------------------------
# The engine stubs. Reproduced from Src where behaviour matters; never a
# stand-in for our own code, which is always loaded from Code/ verbatim.
# ---------------------------------------------------------------------------
BOOT = r"""
SMRSIM = SMRSIM or { log = {}, threads = 0 }
-- ModLog stores the message and its ModPrint output path formats the single
-- argument AGAIN (Mod.lua:109-132, lib.lua:164-174); SMROptInPack.Log escapes
-- '%' for that second pass. Reproduce it so the captured text is what lands in
-- the game's log file.
function ModLog(msg) SMRSIM.log[#SMRSIM.log + 1] = string.format(msg) end

-- cthreads.lua:6 — `local message_to_staticfuncs = {}` is a plain file-local,
-- NOT under FirstLoad, so registrations do NOT survive a Lua reload. The
-- simulator recreates this store at the head of every load.
function SMRSIM_ResetMessages()
    SMRSIM_msgs = {}
    OnMsg = setmetatable({}, { __newindex = function(_, name, fn)
        local t = SMRSIM_msgs[name]
        if not t then t = {}; SMRSIM_msgs[name] = t end
        t[#t + 1] = fn
    end })
end
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
function IsValid() return false end
function PlaceObj(cls, t) t = t or {}; t.class = cls; return t end
empty_table = {}
CurrentModOptions = false
Mods = false
DataLoaded = false
"""


def run(core_path=None, loads=2):
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(BOOT)
    files = code_list()
    results = []
    for n in range(1, loads + 1):
        lua.execute("SMRSIM_ResetMessages()")
        lua.execute("SMRSIM.log = {}")
        dead = []
        for m in files:
            path = os.path.join(CODE, m)
            if core_path and m == "00_Core.lua":
                path = core_path
            with open(path, encoding="utf-8-sig") as f:
                src = f.read()
            try:
                lua.execute(src)
            except lupa.LuaError as e:
                dead.append((m, str(e).strip().splitlines()[0]))
        if n == 1:
            lua.execute('Msg("ClassesBuilt")')
        else:
            lua.execute('Msg("ClassesBuilt")')
            lua.execute('Msg("ModsReloaded", false)')
        order = [lua.eval("SMROptInPack.order[%d]" % i)
                 for i in range(1, int(lua.eval("#SMROptInPack.order")) + 1)]
        fixes = {}
        for fid in set(order):
            e = lua.eval('SMROptInPack.fixes["%s"]' % fid)
            fixes[fid] = (e["status"], e["detail"] or "")
        log = [l[len(LOG_PREFIX):] if l.startswith(LOG_PREFIX) else l
               for l in list(lua.eval("SMRSIM.log").values())]
        results.append({"order": order, "fixes": fixes, "log": log, "dead": dead})
    return files, results


def main():
    strict = "--strict" in sys.argv
    expect_doubling = "--expect-doubling" in sys.argv
    core = None
    if "--core" in sys.argv:
        core = sys.argv[sys.argv.index("--core") + 1]
    files, results = run(core)
    registering = len(files) - 1          # 00_Core.lua registers nothing
    bad = 0

    for n, r in enumerate(results, 1):
        print("=" * 72)
        print("LUA LOAD %d  (mod code re-executed in the same process)%s"
              % (n, "  core=" + core if core else ""))
        print("=" * 72)
        for m, err in r["dead"]:
            print("  DEAD | %-28s %s" % (m, err))
        seen = {}
        for fid in r["order"]:
            seen[fid] = seen.get(fid, 0) + 1
        for fid in sorted(seen):
            st, det = r["fixes"][fid]
            verdicts = [l for l in r["log"] if l.startswith(fid + ":")]
            print("  %s | %-22s x%d in order  %-9s  %d verdict line(s)%s"
                  % ("DUP " if seen[fid] > 1 else "ok  ", fid, seen[fid], st,
                     len(verdicts), ("  " + verdicts[0][len(fid) + 1:].strip()[:60]) if verdicts else ""))
        for l in r["log"]:
            if l.startswith("SIMERROR"):
                print("  SIM  | " + l)
        print("  order: %d entries, %d distinct (registering files: %d)"
              % (len(r["order"]), len(seen), registering))
        print()

    last = results[-1]
    dups = sorted(f for f in set(last["order"]) if last["order"].count(f) > 1)
    dead = [m for m, _ in last["dead"]]

    if expect_doubling:
        ok = len(dups) == registering and len(last["order"]) == 2 * registering
        print("CONTROL  — pre-guard core must double every id: %s (%d dup id(s), %d order entries)"
              % ("REPRODUCED" if ok else "NOT REPRODUCED", len(dups), len(last["order"])))
        return 0 if ok else 1

    print("VERDICT  — after load 2: %d duplicate id(s) in order %s; %d file(s) dead %s; "
          "%d of %d registering files present"
          % (len(dups), dups or "", len(dead), dead or "", len(set(last["order"])), registering))
    if dups or dead or len(set(last["order"])) != registering:
        bad = 1
    if strict and bad:
        print("\nFAIL: --strict and the second load is not clean.")
        return 1
    if strict:
        print("\nPASS: every module registers exactly once across a reload, no file died.")
    return bad


if __name__ == "__main__":
    sys.exit(main())
