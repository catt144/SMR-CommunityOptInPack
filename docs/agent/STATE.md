# Project State — the one mandatory read

Current only, rewritten in place; history newest-first in
`docs/archive/SESSION_LOG.md`. Module truth `agent/bugs/INDEX.md` · engine facts
`agent/facts/INDEX.md` · doc map `docs/README.md` · authoring `agent/WORKFLOW.md` ·
code `agent/FIX_POLICY.md` · what came from where `agent/PROVENANCE.md`.

## Where the project is
⭐ **BUILT 2026-08-12 AND ✅✅ VERIFIED IN GAME THE SAME EVENING.** Split out of
`SMR-BugFixPack` @ `33d69f5` by that repo's chain `docs/agent/prompts/split-optins/`
(prompts 3+4). Eight opt-in behaviour modules (D01–D07, D09, D12) over their OWN
copy of the pack framework (`SMROptInPack`), each off or at base until the player
enables it in Options → Mod Options. ⭐⭐ **TRUE STANDALONE IS MEASURED** (fix pack's
`archive/sp*_20260812-*`, 9 launches): this mod ran **with the fix pack
UNINSTALLED** at `8/8`, its 8 probes reporting exactly what they report beside it;
and the fix pack ran with THIS mod uninstalled at `74/74`, registry absent, zero
`[CommunityOptInPack]` lines. Save contract PROVED: every persisted name read back
off 4 real saves under its exact `SMRFixPack_` bytes, plus an in-game
write→save→reload where **0 of 3 fields broke**. ⚠️ The leg's one finding was a
TestKit fixture, not this mod (`Opt_ClassicRockets.lua:89`'s
`self:IsPlayerControlled()`, reachable for the first time with the fix pack
absent; fixture repaired in the kit — the method is real,
`Lua/UniversalRocket.lua:2140`). ⚖️⚖️ **AUDIT CLOSED 08-12: everything above
SUSTAINED** (logs byte-compared + read whole, tallies recounted, persisted names
re-derived from THIS tree, EF-055 re-derived from Src); **no-retraining test
PASSED from this repo alone** (transcript: `docs/archive/SESSION_LOG.md`, top).
Both-mods WORKFLOW clause ACTIVE. ⇒ **NEXT: nothing owed by this repo** — the
D13 chain (ONE rescue artifact, BOTH mods) runs from the fix pack.

## Build state — `python tools/doccheck.py --emit-counts`, never hand-typed
```
BUILD STATE (emitted by tools/doccheck.py)
- modules: 8 registered (1 default-active, 7 optional-gated files)
- Code/*.lua files: 9
- TestKit probes: 88 (shared kit — serves both mods)
- BUGS index rows: 0 F + 9 D + 0 C
```
The 1 default-active is `DroneStatDials`, which registers WITHOUT `optional` and is
active at its base dial positions (vanilla behaviour, armed). Game pinned
**1.0.7.396349** (`EF-014`); the probe count is the SHARED suite's. ✅ **Gate
MEASURED `8/8` beside the fix pack, `1/8` at fresh defaults** (the latter from the
owner's 08-12 18:30 log — the only recording of that state there will ever be).
## Gates and holds
- ⛔ **PERSISTED NAMES ARE SAVE CONTRACT** — the five `SMRFixPack_*` fields and
  modifier ids this mod writes keep those exact bytes forever, prefix and all
  (`agent/PROVENANCE.md` §2). **Renaming one is forbidden here.** Carried across
  byte-for-byte at the port and ✅ **read back live off 4 real saves 08-12**.
  ⛔ **ZERO `SMRFixPack` references in executable code**: the 11 surviving tokens
  in `Code/` are exactly those five persisted STRINGS (5 definitions, 6 comments)
  — data, not references. ⛔ **No behaviour change to any module** while the split
  chain runs; `Opt_DroneOverhaul` carries PT-52's freeze — frozen it stays.
- ✅ **Re-tick SPENT** (owner, 08-12 18:30): mod enabled, 7 toggles on, dials
  `5x`/`+2`. Nothing owed. ⛔ **`EF-055`/`EF-056`**: a junction pull is a real
  uninstall (account untouched); a campaign COPY still runs that campaign's
  autosave — its rotation eats the owner's autosaves (pre-copy them first).
- ✅ **Remote DECIDED 08-13: PUBLIC** — `github.com/catt144/SMR-CommunityOptInPack`,
  `main` tracks `origin/main`. **Still open (on the FIX PACK's checklist, item
  15):** DISPLAY NAME + store description (placeholders `agent/PROVENANCE.md` §3)
  · stay-OFF-by-default (build took OFF). ⚠️ **CHEATS ENABLED on the rig**, and
  **BOTH MODS LOADED is its standing config** (owner rule, `agent/WORKFLOW.md`).
