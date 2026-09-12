# Decisions owed — the opt-in mod's own list

⭐ **Created 2026-09-12 by the owner's ruling (fix pack, checklist 167): the opt-in mod's decisions
live HERE, not on the fix pack's list.** *"Can we fully offload anything opt-in related to its repo,
and just retain anything that's fact based that could be useful — and rehome those facts where they
should be?"*

**What moved, and what did not.** Everything below was carried on the FIX PACK's
`docs/PLAYTEST_CHECKLIST.md` as items 84, 85, 89–97 while it waited for this mod to launch. It is
reproduced **verbatim**, so nothing is lost in the move and no reasoning was re-summarised. ⛔ Three
items did **NOT** move, because they bind the fix pack rather than this mod, and they stay on its list:

| item | why it stayed |
|---|---|
| **83** | TestKit edits — the kit is **SHARED**, so the changes land in the fix pack's tree |
| **86** | `EF-###` ids are allocated by the FIX PACK repo — a rule about ITS facts index |
| **88** | `FUTURE_IDEAS.md` #9 is a **fix-pack feature** (per-fix player toggles) that was parked here by analogy |

✅ **Engine facts were checked and none needed rehoming.** The four facts these items cite —
`EF-023`, `EF-059`, `EF-069`, `EF-072` — are **already in the fix pack's `agent/facts/INDEX.md`**,
which is the canonical home for both repos (see item 86). Nothing was extracted, because nothing was
stranded.

⚠️ **Staleness.** These were written 2026-08-31 / 09-01, **before** the game shipped 1.1.0 + the
first DLC on 09-08. ⛔ **Re-read every citation against the live tree before acting on any of them** —
the fix pack's own experience is that line numbers moved, modules were deleted and some defects were
fixed by vanilla. None of this has been re-verified since.

⛔ **Nothing here is owed by anyone right now.** This mod is not launching; these are its launch
obligations. The source reports are in `docs/agent/reports/`.

---

### 2026-09-01 — ITEMS 94–97 OPEN: the D06 rebuild DESIGN SPEC (opt-in repo, `docs/agent/reports/DRONE_REBUILD_DESIGN_20260901.md`)

> The spec is the build-out of the tiers **under your directive that it must not need the Save
> Rescue or any uninstall mod** — which makes "uninstall-clean" and "nothing for the Rescue to do"
> hard constraints rather than trade-offs. Its build brief
> (`prompts/DRONE_REBUILD_BUILD.md`) is written and **will not start until item 94 has a line.**

97. **The disclaimer's final player-facing wording.** A full draft is spec §7 — what the module
    does, what it does NOT do (it changes which job is served first, never which pile feeds it —
    a broken water extractor can still wait on parts scavenged across the map while a full depot
    sits beside it, `EF-059`), and the off-ramp. Two of its sentences are gated on the playtest's
    uninstall legs actually running and do not ship before that. Reword, approve, or say "at the
    build".

96. **Repair moonlighting: keep or drop?** The spec recommends **KEEP, mechanism unchanged.**
    For: it serves ground the tiers do not — the tiers reorder work *within a hub's poll*, and a
    workless drone helping a saturated neighbour is the only thing in the module that moves labour
    between fleets; its F86 leak was repaired 08-01 and verified by PT-58; it reads the flat
    `const.MaxBuildingPriority`, which the tiers never touch, so there is no interaction to reason
    about. Against: it was never measured (the B2 table records `vetoed`, not `moonlighted`), and
    dropping it makes the rebuild a strictly smaller product. Spec §6 part 2.

95. **Food-service default priority 3: in the rebuild, separate, or dropped?** `ServiceWorkplace`
    AND a Food demand = exactly four buildings (Diner, Mega Mall, Grocer, Small Grocer). Q4 makes
    it clean — `priority` is a class member, no template sets one, instances carry it only after a
    real change, so it is omitted from saves and reverts on uninstall. ⚠️ One honest limit the
    spec adds: priority is baked at queue-insert, so on an existing colony the change reaches the
    four only at their next re-registration — the build handles that with a **targeted** reconnect
    of those four buildings, not a colony-wide one. Your 07-31 framing was "correct attribution of
    failure", which ties it to the same complaint as the tiers; the counter is that it is a
    *supply-allocation* opinion riding on an *urgency* toggle. Spec §2 row 3, §6 part 5.

94. **RATIFY THE D06 REBUILD SPEC — the mechanism and the tier table. This answers item 91.**
    Mechanism: **V-a "view tiers"** — the tiers are a VIEW handed to the matcher in transient
    tables, the filing stays vanilla's; nothing is ever written at band 4 or 5. Fallback ladder
    already written into the spec and the brief: **P** (finder pre-emption) if E-4 fails, **2-S**
    (table surgery at band 3, no experiment owed, one band) if E-8 fails too, **D** (the devs' own
    tier on the five producers) if you rule the 5/4/3 distinction a preference. The claim gate is
    deleted; ONE toggle; D09 stays separate. Footprint: **zero new persisted names**, argued per
    structure from `EF-072`'s only-route rule — and it is an argument, not yet a witness (the
    Mod-Manager-disable and both-config legs are what witness it). Two matcher cells still need
    item 92. **Nothing is built until this line exists.**

### 2026-09-01 — ITEMS 91–93 OPEN: the drone bands-and-clean-revert report (opt-in repo, `docs/agent/reports/DRONE_BANDS_CLEAN_REVERT_20260901.md`)

93. **Should the urgency tiers apply to rockets and RC Rovers, or to Drone Hubs only?**
    Every `DroneControl` carrier shares `FindTask`, so a wrapper there serves tiers on
    rockets/rovers too unless gated on `DroneHubBase` the way v1's claim gate is
    (`Opt_DroneOverhaul.lua:185`). Rovers are player-zoned; rockets refuel/unload. Say
    "hubs only", "all carriers", or "decide at the build brief" (report §4.2 V, R11).

92. **Run the two matcher experiments (E-4, E-8; ≈ 70 attended minutes, one sitting, NEW
    game, TEMPORARY TestKit module)?** They are the only cells the desk could not fill:
    does `Request_FindTask` honour a mod-built table set, and is a wrapper-substituted
    pairing claimed and executed like a matcher-chosen one. E-9 (tier precedence, n≥3)
    follows if both pass; E-3/E-5 only if option 1 is chosen; E-6 turns EF-069 from
    source-read to measured; E-2 is refused by EF-023. Cards with predictions: report §5.
    Say which to run, or "none yet".

91. **The D06 design decision, restated with the new inputs (supersedes the three-option
    framing in `prompts/perma/DRONE_PROJECT_PROMPT.md` §3 as the thing to decide).** The report's
    ranked shortlist: (1) **V** view tiers — bands 4–5 as tier ORDER handed to the matcher
    in transient tables, full 5/4/3 distinction, zero residue by construction, pending E-4
    and E-8; (2) **P** finder pre-emption, same result, pending E-8 only; (3) **2-S** table
    surgery at band 3 — clean revert from citations alone, no experiment, but ONE band
    (the pipes/dome tier); (4) **D** the devs' own tier on the five producers only.
    Bands 4–5 as PERSISTED data (option 1) fail uninstall by the §9 measurements and the
    Rescue would have to learn a queue shape; tear-down-on-save is layer 1, which you
    declined 2026-07-31, and Src shows it cannot hold its invariant on autosaves. **Two
    questions decide it:** (a) is *5 vs 4 vs player-3* a requirement (V/P) or a preference
    (2-S/D suffice)? — the devs' own tier is one band and they withdrew a one-band urgency
    in 2018; (b) if a requirement, do you authorise item 92 first? The recommendation is V
    with 2-S as the documented fallback; the pick is yours. Nothing is built until you say.
    ⭐ **2026-09-01: ANSWERED IN FORM BY ITEM 94** — the opt-in mod's rebuild-design session
    turned the recommendation into a full spec (mechanism, tier table, guard, footprint,
    playtest, build brief). Rule item 94 and 91 closes with it.

### 2026-09-01 — ITEMS 88–90 OPEN: raised by the OPT-IN mod's contamination audit (its repo, `docs/agent/reports/CONTAMINATION_AUDIT_20260901.md`)

90. **Does your 2026-08-02 loc-table ruling extend to the opt-in mod?** You ruled
    (this repo's `FIX_POLICY` §6) that *the pack* WILL ship its own `ModItemLocTable`
    translations post-release — twelve days before the split, about THIS mod. The
    opt-in mod has 17 `Untranslated(` sites (rollover titles, policy rows, the
    stand-down dialog) and its `FUTURE_IDEAS.md` #4(b) hangs on the answer. Say
    "both", "fix pack only", or "decide at its launch".

89. **Opt-in `Code/`: allow a comment-only wording sweep?** Five comments still speak
    the donor's terms — "the pack" meaning the opt-in mod itself
    (`00_Core.lua:497`, `:536`, `:558`, `Opt_ResidencyControl.lua:63`) and one that
    points players' FAQ guidance at THIS repo's frozen `MOD_DESCRIPTION.md`
    (`Opt_NoHomeless.lua:319`). Zero behaviour change, parse sweep after; but it is a
    module-file edit, so it is yours. Say "sweep" or "leave as history".

*(Item **88** was here and has been left with the FIX PACK — `FUTURE_IDEAS.md` #9 is a fix-pack
feature, per-fix player toggles for THIS mod's fixes, parked in this repo only by analogy. See the table
at the top.)*

---

## From the readiness pass, 2026-08-31 (`reports/READINESS_REVIEW_0831.md`)

85. **Preview art for the opt-in mod (owner task).** `tools/upload_preflight.py`
    run against `C:\Dev\SMR-OptInPack` FAILS on exactly one clause: no `image` /
    `preview.png` — Paradox rejects before packing (`ParadoxMods.lua:39`). Same
    limits as ours (≤1 MB Steam / ≤2 MB PDX). Not urgent — that mod is not launching —
    but it is the only mechanical FAIL between it and an upload sitting.

84. **Opt-in: name three wrap pairs in `Require` blocks?** The F107 check (now run by
    its doccheck) found three capture+install sites with no Require pair:
    `Opt_DroneOverhaul` → `Drone.CleanUnreachables` + `TaskRequestHub.FindTask` (that
    module uses inline guards, no `Require` at all) and `Opt_MultipleSuns` →
    `SolarPanelBase.GameInit`. Each captured class DECLARES the method at Src
    (Drone.lua:879, _TaskRequest.lua:72, SolarPanel.lua:8), so `prev` is real and
    nothing is broken — they are allowlisted with those citations. The tidy fix is a
    code edit to frozen modules (`DroneOverhaul` carries PT-52's freeze) and needs an
    A/B. **Options:** (a) leave allowlisted until the next planned edit of each file;
    (b) do it at the opt-in launch session with its boot check. Recommend (a).
