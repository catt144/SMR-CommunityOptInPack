#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""L7 (environment & namespace) — the global map, taken from the COMPILER.

WHY THIS EXISTS
    L7's first question is "enumerate every global this mod creates or writes",
    and every previous census in this project has been a regex over source text.
    A regex cannot answer this one, because whether `x = 1` is a global or a
    local is decided by SCOPE, not by shape: the same eight characters are a
    local write inside `local x` and a global write outside it. Link 6's own
    extractors were wrong three times in one session on much easier questions.

    So do not ask a pattern. Ask the compiler. In Lua 5.2+ every global access
    compiles to an indexed access on the `_ENV` upvalue, which means the
    bytecode carries the answer with zero ambiguity:

        SETTABUP  A B C   -- UpValue[A][RK(B)] := RK(C)   ... A names _ENV  => a global WRITE
        GETTABUP  A B C   -- R(A) := UpValue[B][RK(C)]    ... B names _ENV  => a global READ

    This tool compiles each shipped file with Lua 5.3 (`lupa.lua53`), dumps the
    prototype tree unstripped, parses it, and emits every global read and write
    with its file:line. A name that is not in the output is not a global; a name
    that is, is one. Shadowing, nested closures, method definitions, for-loop
    variables and parameters are all handled BY THE COMPILER, not by this file.

WHY IT MATTERS THAT WRITES ARE SPLIT BY WHEN THEY RUN
    `ModEnvMeta.__newindex` (Mod.lua:1557-1563, read at Src this session) is:

        if env_blacklist[key] then return end
        if not Loading and PersistableGlobals[key] == nil
                       and rawget(original_G, key) == nil then
            assert(false, "Attempt to create a new global '" .. key .. "'", 1)
        end
        rawset(original_G, key, value)

    Three consequences this tool is built to expose:
      1. EVERY global write from mod code lands in the REAL _G. There is no
         such thing as a mod-private global. An accidental one is a cross-mod
         collision, not a private slip.
      2. The create-assert is suppressed while `Loading` is true, and all mod
         code loads inside that window (autorun.lua:1/:423/:560). So a global
         created at FILE SCOPE is silent, and the same slip inside a wrapper
         body that runs in-game is NOT.
      3. A blacklisted key is dropped SILENTLY on write and reads back nil.

    Hence writes are reported as `chunk` (runs during Loading) vs `nested`
    (a function body; may run at any time, including after Loading).

CONTROL
    `--selftest` runs a battery of snippets whose correct answer is written out
    by hand, including every shadowing shape that would fool a regex. The
    battery must pass before any count below is trusted; the harness is not
    evidence about this mod until it reproduces known answers.

USAGE
    python tools/l7_env_map.py --selftest
    python tools/l7_env_map.py                 # this mod
    python tools/l7_env_map.py --tree ../SMR-BugFixPack-TestKit
    python tools/l7_env_map.py --json out.json
"""

import argparse
import io
import json
import os
import struct
import sys

# The Windows console defaults to cp1252 and this tool prints the project's
# non-ASCII vocabulary; without this it dies on its own output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- Lua 5.3 dump

LUAC_SIG = b"\x1bLua"
LUAC_VERSION = 0x53

# opcode numbers, Lua 5.3 lopcodes.h
OP_GETTABUP = 6
OP_SETTABUP = 8

BITRK = 1 << 8  # lopcodes.h: ISK / INDEXK


class Reader(object):
    def __init__(self, buf):
        self.b = buf
        self.i = 0

    def bytes(self, n):
        out = self.b[self.i:self.i + n]
        if len(out) != n:
            raise ValueError("dump truncated")
        self.i += n
        return out

    def byte(self):
        return self.bytes(1)[0]

    def integer(self, size):
        return int.from_bytes(self.bytes(size), "little", signed=False)


class Proto(object):
    def __init__(self):
        self.source = None
        self.linedefined = 0
        self.lastlinedefined = 0
        self.code = []
        self.consts = []
        self.upvalnames = []
        self.protos = []
        self.lineinfo = []


def parse_dump(buf):
    r = Reader(buf)
    if r.bytes(4) != LUAC_SIG:
        raise ValueError("not a Lua dump")
    ver = r.byte()
    if ver != LUAC_VERSION:
        raise ValueError("unexpected Lua bytecode version 0x%02x" % ver)
    r.byte()          # format
    r.bytes(6)        # LUAC_DATA
    size_int = r.byte()
    size_size_t = r.byte()
    size_instr = r.byte()
    size_lua_int = r.byte()
    size_lua_num = r.byte()
    r.bytes(size_lua_int)   # LUAC_INT
    r.bytes(size_lua_num)   # LUAC_NUM
    r.byte()                # sizeupvalues of the main closure
    sizes = (size_int, size_size_t, size_instr, size_lua_int, size_lua_num)
    return read_proto(r, sizes, None)


def read_string(r, sizes):
    size_int, size_size_t, _, _, _ = sizes
    n = r.byte()
    if n == 0:
        return None
    if n == 0xFF:
        n = r.integer(size_size_t)
    return r.bytes(n - 1).decode("utf-8", "replace")


def read_proto(r, sizes, parent_source):
    size_int, size_size_t, size_instr, size_lua_int, size_lua_num = sizes
    p = Proto()
    p.source = read_string(r, sizes) or parent_source
    p.linedefined = r.integer(size_int)
    p.lastlinedefined = r.integer(size_int)
    r.byte()  # numparams
    r.byte()  # is_vararg
    r.byte()  # maxstacksize

    n = r.integer(size_int)
    raw = r.bytes(n * size_instr)
    p.code = list(struct.unpack("<%dI" % n, raw))

    n = r.integer(size_int)
    for _ in range(n):
        t = r.byte()
        if t == 0:            # nil
            p.consts.append(None)
        elif t == 1:          # boolean
            p.consts.append(bool(r.byte()))
        elif t == 3:          # LUA_TNUMFLT
            p.consts.append(struct.unpack("<d", r.bytes(size_lua_num))[0])
        elif t == 0x13:       # LUA_TNUMINT
            p.consts.append(r.integer(size_lua_int))
        elif t in (0x04, 0x14):   # short / long string
            p.consts.append(read_string(r, sizes))
        else:
            raise ValueError("unknown constant tag 0x%02x" % t)

    n = r.integer(size_int)
    for _ in range(n):
        r.byte()  # instack
        r.byte()  # idx
    nup = n

    n = r.integer(size_int)
    for _ in range(n):
        p.protos.append(read_proto(r, sizes, p.source))

    # debug
    n = r.integer(size_int)
    p.lineinfo = [r.integer(size_int) for _ in range(n)]
    n = r.integer(size_int)
    for _ in range(n):
        read_string(r, sizes)
        r.integer(size_int)
        r.integer(size_int)
    n = r.integer(size_int)
    p.upvalnames = [read_string(r, sizes) for _ in range(n)]
    while len(p.upvalnames) < nup:
        p.upvalnames.append(None)
    return p


# ------------------------------------------------------------------ extraction

def _rk_const(p, x):
    """RK(x) -> the constant, or None when x is a register."""
    if x & BITRK:
        idx = x & ~BITRK
        if 0 <= idx < len(p.consts):
            return p.consts[idx]
    return None


def walk(p, depth, out):
    for pc, instr in enumerate(p.code):
        op = instr & 0x3F
        if op not in (OP_GETTABUP, OP_SETTABUP):
            continue
        a = (instr >> 6) & 0xFF
        c = (instr >> 14) & 0x1FF
        b = (instr >> 23) & 0x1FF
        line = p.lineinfo[pc] if pc < len(p.lineinfo) else 0
        if op == OP_SETTABUP:
            up, key = a, _rk_const(p, b)
            kind = "write"
        else:
            up, key = b, _rk_const(p, c)
            kind = "read"
        name = p.upvalnames[up] if up < len(p.upvalnames) else None
        if name != "_ENV":
            continue
        if not isinstance(key, str):
            # _ENV[expr] with a computed key — report it, it is unresolvable
            out.append({"kind": kind, "name": None, "line": line,
                        "scope": "chunk" if depth == 0 else "nested"})
            continue
        out.append({"kind": kind, "name": key, "line": line,
                    "scope": "chunk" if depth == 0 else "nested"})
    for sub in p.protos:
        walk(sub, depth + 1, out)


def globals_of_source(src, chunkname):
    import lupa.lua53 as lua53
    L = lua53.LuaRuntime(unpack_returned_tuples=True, encoding=None)
    L.globals()[b"__src"] = src.encode("utf-8")
    L.globals()[b"__name"] = chunkname.encode("utf-8")
    dumped = L.execute(
        b"local f, err = load(__src, __name, 't')\n"
        b"if not f then error(err, 0) end\n"
        b"return string.dump(f, false)")
    if isinstance(dumped, str):
        dumped = dumped.encode("latin-1")
    p = parse_dump(dumped)
    out = []
    walk(p, 0, out)
    return out


# ------------------------------------------------------------------- self-test

BATTERY = [
    # (source, expected writes, expected reads)  -- names only, hand-derived
    ("x = 1", {"x"}, set()),
    ("local x x = 1", set(), set()),
    ("local function f() y = 2 end", {"y"}, set()),
    ("local t = {} t.k = 1", set(), set()),
    ("function G() end", {"G"}, set()),
    ("local M = {} function M.f() end", set(), set()),
    ("for i = 1, 3 do i = i + 1 end", set(), set()),
    ("for k, v in pairs(t) do k = 1 end", set(), {"pairs", "t"}),
    ("local function f(p) p = 1 end", set(), set()),
    ("local a a = b", set(), {"b"}),
    ("do local z = 1 end z = 2", {"z"}, set()),
    ("local x = 1 do local x = 2 x = 3 end x = 4", set(), set()),
    ("local x = 1 local f = function() x = 2 end", set(), set()),
    ("q = function() r = 1 end", {"q", "r"}, set()),
    ("print(A.B.C)", set(), {"print", "A"}),
    ("A.B = 1", set(), {"A"}),
    ("local _ENV = {} w = 1", set(), set()),
    ("rawset(_G, 'k', 1)", set(), {"rawset", "_G"}),
    ("_G['k'] = 1", set(), {"_G"}),
    ("local s = ...  s = s", set(), set()),
    ("function Cls:m() self.x = 1 end", set(), {"Cls"}),
    ("OnMsg.Ready = function() end", set(), {"OnMsg"}),
    ("local ok, e = pcall(function() nope = 1 end)", {"nope"}, {"pcall"}),
]


def selftest():
    bad = 0
    for src, want_w, want_r in BATTERY:
        got = globals_of_source(src, "=battery")
        gw = {g["name"] for g in got if g["kind"] == "write"}
        gr = {g["name"] for g in got if g["kind"] == "read"}
        ok = (gw == want_w and gr == want_r)
        if not ok:
            bad += 1
            print("  FAIL %-46s writes %s (want %s)  reads %s (want %s)"
                  % (src, sorted(map(str, gw)), sorted(want_w),
                     sorted(map(str, gr)), sorted(want_r)))
    total = len(BATTERY)
    print("selftest: %d/%d cases pass" % (total - bad, total))
    return 1 if bad else 0


# ----------------------------------------------------------------------- main

def code_files(tree):
    code = os.path.join(tree, "Code")
    meta = os.path.join(tree, "metadata.lua")
    ordered = []
    if os.path.isfile(meta):
        txt = open(meta, "r", encoding="utf-8", errors="replace").read()
        import re
        for m in re.finditer(r'filename\s*=\s*"Code/([^"]+)"', txt):
            ordered.append(m.group(1))
    seen = set(ordered)
    for f in sorted(os.listdir(code)):
        if f.endswith(".lua") and f not in seen:
            ordered.append(f)
    return [(f, os.path.join(code, f)) for f in ordered
            if os.path.isfile(os.path.join(code, f))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default=ROOT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    tree = os.path.abspath(args.tree)
    rows = []
    for name, path in code_files(tree):
        src = open(path, "r", encoding="utf-8", errors="replace").read()
        try:
            hits = globals_of_source(src, "@" + name)
        except Exception as exc:
            print("!! %s: %s" % (name, exc))
            return 2
        for h in hits:
            h["file"] = name
            rows.append(h)

    writes = [r for r in rows if r["kind"] == "write"]
    reads = [r for r in rows if r["kind"] == "read"]

    if not args.quiet:
        print("TREE: %s" % tree)
        print("files compiled: %d" % len(code_files(tree)))
        print("global WRITE sites: %d   global READ sites: %d"
              % (len(writes), len(reads)))
        print()
        print("=== every global this mod WRITES ===")
        byname = {}
        for w in writes:
            byname.setdefault(w["name"], []).append(w)
        for nm in sorted(byname, key=lambda s: (s is None, s or "")):
            sites = byname[nm]
            scopes = sorted({s["scope"] for s in sites})
            print("  %-26s %d site(s)  [%s]" % (nm, len(sites), ",".join(scopes)))
            for s in sites:
                print("        %s:%d  (%s)" % (s["file"], s["line"], s["scope"]))
        print()
        print("=== global names this mod READS (distinct) ===")
        rnames = {}
        for r in reads:
            rnames.setdefault(r["name"], []).append(r)
        print("  %d distinct" % len(rnames))
        for nm in sorted(rnames, key=lambda s: (s is None, s or "")):
            print("  %-34s %d" % (nm, len(rnames[nm])))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=1)
        print("\nwrote %s (%d rows)" % (args.json, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
