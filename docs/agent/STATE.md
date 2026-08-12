# Project State — the one mandatory read

Current only, rewritten in place; history newest-first in
`docs/archive/SESSION_LOG.md`. Module truth `agent/bugs/INDEX.md` · engine facts
`agent/facts/INDEX.md` · doc map `docs/README.md` · authoring `agent/WORKFLOW.md`
· code `agent/FIX_POLICY.md` · what came from where `agent/PROVENANCE.md`.

## Where the project is

⭐ **BUILT 2026-08-12, NOT YET LAUNCHED.** Split out of `SMR-BugFixPack` @
`33d69f5` by that repo's chain `docs/agent/prompts/split-optins/` (prompt 3).
Eight opt-in behaviour modules (D01–D07, D09, D12) over their OWN copy of the
pack framework (`SMROptInPack`), each off or at base until the player enables it
in Options → Mod Options. ⛔ **TRUE STANDALONE** — must work with the Community
Fix Pack present and identically with it absent.
⇒ **NEXT, and it is owned by the fix pack's chain folder, not by this repo:**
① `04_OPUS_VERIFY.md` — the three-cell matrix (both mods · this mod alone · fix
pack alone) + a save-compat witness on a `CP15PT15` copy. Unattended; needs the
game. **Nothing here has been run in a game yet: every number below is static.**
② `05_FABLE_AUDIT.md` — byte-compare, whole-log read, and the no-retraining
acceptance test run from THIS repo with the fix pack closed.
③ then the D13 chain (save-rescue artifact — ONE artifact covering BOTH mods by
owner ruling; its exposed set is re-derived over this tree, never inherited).

## Build state — `python tools/doccheck.py --emit-counts`, never hand-typed

```
BUILD STATE (emitted by tools/doccheck.py)
- modules: 8 registered (1 default-active, 7 optional-gated files)
- Code/*.lua files: 9
- TestKit probes: 88 (shared kit — serves both mods)
- BUGS index rows: 0 F + 9 D + 0 C
```

The 1 default-active is `DroneStatDials`, which registers WITHOUT `optional`
and is active at its base dial positions (vanilla behaviour, armed). Game
pinned **1.0.7.396349** (`agent/facts/EF-014`). ⚠️ The probe count is the
SHARED suite's, not this mod's share. **Predicted gate read at fresh account
defaults: `1/8`** — unmeasured until leg ①.

## Gates and holds

- ⛔ **PERSISTED NAMES ARE SAVE CONTRACT** — the five `SMRFixPack_*` fields and
  modifier ids this mod writes keep those exact bytes forever, prefix and all
  (`agent/PROVENANCE.md` §2). **Renaming one is forbidden here.** Verified at
  the port: all five carried across byte-for-byte, counted before and after.
- ⛔ **ZERO `SMRFixPack` references in executable code.** The 11 surviving
  tokens in `Code/` are exactly those five persisted STRINGS (5 definitions, 6
  comments) — data, not references.
- ⛔ **No behaviour change to any module** while the split chain runs.
  `Opt_DroneOverhaul` carries PT-52's freeze with it — frozen it stays.
- ⚠️ **The mod id changed, so Mod Options state resets ONCE.** The owner re-ticks
  7 toggles + 2 dials in one ~1-minute visit, AFTER leg ① reports clean.
  Predicted, not a defect; it is on the fix pack's checklist, item 15.
- **Owner decisions open (routed to the FIX PACK's `PLAYTEST_CHECKLIST.md`,
  item 15):** DISPLAY NAME + store description (placeholders listed in
  `agent/PROVENANCE.md` §3) · GitHub remote (until then LOCAL git — do not
  create one unasked) · stay-OFF-by-default (build took OFF).
- ⚠️ **Rig has CHEATS ENABLED**, and **BOTH MODS LOADED is the rig's standing
  configuration** from the split onward (owner rule, `agent/WORKFLOW.md`).
