# Project State — the one mandatory read

Current only, rewritten in place; history newest-first in
`docs/archive/SESSION_LOG.md`. Module truth `agent/bugs/INDEX.md` · engine facts
`agent/facts/INDEX.md` · doc map `docs/README.md` · authoring `agent/WORKFLOW.md`
· code `agent/FIX_POLICY.md` · what came from where `agent/PROVENANCE.md`.

## Where the project is

⚠️⚠️ **MID-SPLIT — this repo is a SCAFFOLD and does not load yet.** Commit 1 of
the `split-optins` build (fix pack `docs/agent/prompts/split-optins/`, prompt 3,
2026-08-12) is the teaching skeleton: policies, engine facts, tooling, the
provenance ledger. **No `Code/`, no `metadata.lua`, no `items.lua` yet** — the
framework port and the 8 modules land in the next two commits of the same
session. If you are reading this line in a later session, the build did not
finish: check the fix pack's chain folder and `docs/archive/SESSION_LOG.md`
before touching anything.

⇒ **What this mod IS, once it loads:** eight opt-in behaviour modules
(D01–D07, D09, D12), each off or at base until the player enables it in
Options → Mod Options, over its OWN copy of the pack framework
(`SMROptInPack`). **TRUE STANDALONE** — it must work with the Community Fix
Pack present and identically with it absent.

## Build state — `python tools/doccheck.py --emit-counts`, never hand-typed

```
(not yet emitted — Code/ is empty at commit 1)
PREDICTED at split close: Code/*.lua 9 · registered 8 · optional-gated 7 ·
default-active 1 (DroneStatDials, which registers without `optional` and is
active at its base dial positions) · bugs index rows 9 D
```

Re-emit after any module/entry change (red refuses); game pinned
**1.0.7.396349** (fpk parity — `agent/facts/EF-014`). The TestKit probe count
doccheck prints is the SHARED suite's, not this mod's share.

## Gates and holds

- ⛔ **PERSISTED NAMES ARE SAVE CONTRACT** — the `SMRFixPack_*` fields and
  modifier ids this mod writes keep their exact bytes forever. Inventory:
  `agent/PROVENANCE.md` §2. **Renaming one is forbidden here.**
- ⛔ **ZERO `SMRFixPack` references in executable code** (the standalone
  invariant). The persisted strings above are data, not references.
- ⛔ **No behaviour change to any module** while the split chain runs — the
  port is byte-conservative by construction, and `Opt_DroneOverhaul` carries
  PT-52's freeze with it.
- **OWED, in order:** the framework port + the 8 modules (this session) → the
  three-cell verification matrix + save-compat witness (chain prompt 4, needs
  the game) → the terminal audit and the no-retraining acceptance test (prompt
  5) → then the D13 chain, which covers BOTH mods with one artifact.
- **Owner decisions open (routed to the FIX PACK's `PLAYTEST_CHECKLIST.md`,
  item 15):** DISPLAY NAME + store description (placeholder sites listed in
  `agent/PROVENANCE.md` §3) · GitHub remote (until then LOCAL git — do not
  create one unasked) · the stay-OFF-by-default recommendation (build took OFF).
- ⚠️ **The mod id changed, so Mod Options state resets ONCE** — the owner
  re-ticks their toggles in one ~1-minute visit. Predicted, not a defect.
- ⚠️ **Rig has CHEATS ENABLED**, and **BOTH MODS LOADED is the rig's standing
  configuration** from the split onward (owner rule, `agent/WORKFLOW.md`).
