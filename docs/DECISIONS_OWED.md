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

⚠️⚠️ **A LAUNCH TRAP, homed here 2026-09-12 so it is not lost — read this before restoring anything.**
The fix pack's `agent/reports/PARKED_OPTIN_REFERENCES.md` §P38 (line ~697) holds the parked
`metadata.lua` `description` for this mod, and its restore checklist says to **paste P38 back
verbatim** at launch. That text still contains the over-promise the fix pack **retired** on
2026-09-12 — *"stands down if an official patch changes what it was written for"* — because the
parked file was deliberately NOT updated. ⇒ **Restoring it as written puts a retired over-promise
straight back onto a store card.** ⛔ The fix pack's hazard **H-07** forbids touching the parked
references before this mod launches, so it must be fixed **at the restore**, not before. Whoever
runs that restore: compare P38 against the fix pack's live `metadata.lua` wording first.

⛔ **Nothing here is owed by anyone right now.** This mod is not launching; these are its launch
obligations. The source reports are in `docs/agent/reports/`.

**Numbering.** Items 84–97 keep the fix-pack numbers they were carried across under, so their
citations elsewhere still resolve. Items raised HERE from 2026-09-17 on use an `OI-` prefix, so the
two lists can never collide no matter how far the fix pack's numbering runs.

---

### 2026-09-17 — ⚖️ RULED BY THE OWNER: three modules retired. This CLOSES OI-02, OI-05, OI-06, OI-07

> **The ruling, 2026-09-17 (owner).** Archive **`Opt_DroneOverhaul` (D06) as PARKED**; archive
> **`Opt_CohortHousing` (D07)** and **`Opt_NoHomeless` (D12) as DEAD**; **keep `Opt_DroneStatDials`
> (D09)**. MODULE FREEZE was lifted for exactly those three and for nothing else.
>
> ⛔ **OI-01 (`ClassicRockets`), OI-03 (D03's dead tourist guard) and OI-04 (D04's sun-removal gap)
> were NOT ruled on and remain OPEN below.**

**What was carried out.** All three modules were **deleted** — the `Code/Opt_*.lua` file, the
`items.lua` `ModItemCode` + `ModItemOptionToggle` entries, and the `metadata.lua` `code` entry +
`default_options` key. Counts after, pulled with `python tools/doccheck.py --emit-counts` and never
hand-typed: **6 `Code/*.lua` files, 5 registered modules** (1 default-active, 4 carrying
`optional = true`), the two sets agree; **1 allowlisted wrap site** (was 3 — D06's two left with its
file); **0 shared-symbol load-order constraints** (both retired rules named `NoHomeless`; the pair is
preserved verbatim as a comment in `tools/doccheck.py`). Shipping modules are now `ClassicRockets`
(D01), `AcknowledgedWarnings` (D02), `ResidencyControl` (D03), `MultipleSuns` (D04), `DroneStatDials`
(D09).

**Where the code went.** ⛔ **Git is the record.** Restore sha **`cc846e4`** — the last commit in
which all three still shipped: `git show cc846e4:Code/Opt_DroneOverhaul.lua`. Untracked convenience
copies sit at `C:\Dev\SMR-OptInPack-archive\`, deliberately OUTSIDE the mod root so the Mod Editor
cannot sweep a retired module into an upload pack and the junctioned game folder cannot see them.

**Where the reasoning lives now.** Each entry carries a dated retirement section —
`docs/agent/bugs/D06.md`, `D07.md`, `D12.md` — with what left, where the code is and what reviving
it would take; the consequences are §10 of `docs/agent/reports/MODULE_REVALIDATION_1_1_0.md`.
Historical `status:` words were KEPT (`built`, `tested-attended`, `speced`), per the hotfix-2
precedent the fix pack set on 2026-09-12: retirement does not un-test what was tested.

⚠️ **Three things the ruling did NOT settle, preserved from the closed items:**

1. **D12's defect is still real on 1.1.0.** The emigration tie survived **verbatim**, relocated into
   `Colonist:GetBestReachableCommunities` (`1.1.0.403908/Src/Lua/Units/Colonist.lua:3474-3492`). The
   module died; the bug did not, and nothing of ours now aims at it. Reviving it means **porting the
   field** (`exclusive_trait` → `filter_residents`, naming `Children` and `Seniors` explicitly
   because 1.1.0 also ships `Adults`; the Hotel carve-out maps to `"Tourists"`, plural) — the same
   port D07 would need. The owner's stated cheapest next step stands: **look again in the game
   first**, because 1.1.0 softened the overpopulation penalty from a hardcoded -500 to
   `CommunityEvalOverpopulated = -200` and that alone may drain the origin scenario. Full body:
   `docs/agent/bugs/D12.md`.
2. **Items 94 and 92 are still specified against 1.0.7 machinery** and should not be ruled on until
   the D06 rebuild is re-based on 1.1.0. That caveat was raised under OI-05 and survives its closure;
   both items remain OPEN below.
3. ⛔ **Three TestKit probes are now orphaned, and the kit was NOT edited.**
   `C:\Dev\SMR-BugFixPack-TestKit\Code\60_Probes_Opt.lua` still registers `CohortHousing` (`:215`)
   and `NoHomeless` (`:392`), and `OptionsMenuOptIn`'s `WANT` list (`:892-901`) names all three
   retired ids, so that probe asserts toggles the pack no longer declares. The kit is **SHARED** with
   the fix pack, so this is **fix pack checklist item 83** (see the table at the top of this file) —
   raised here so it is not lost, but it must be ruled and edited over there. **This is the one piece
   of fallout from the ruling that is still outstanding.**

**Stale Mod-Options keys are inert — the account-state worry raised under OI-01 is answered.**
Removing a toggle leaves its key in `AccountStorage.ModOptions[mod.id]` forever, and nothing reads
it: `ModDef:LoadOptions` (`1.1.0.403908/Src/CommonLua/Modding/Mod.lua:680-699`) overwrites from
storage and then seeds defaults for the currently declared properties, and the write path
(`:755-770`) iterates the **current** `options:GetProperties()` and never clears a removed key. No
crash, no reset of the player's other toggles, and the UI does not render it. Source-read, not run.
⛔ It deserves an `EF-` fact and does not have one — `EF-` ids are allocated by the FIX PACK
(item 86), so file it there first and mirror it here. No number was minted. Working: report §10.1.

---

### 2026-09-17 — OI-01 OPEN: the game moved to 1.1.0 and one module was overtaken by it

> Raised by the tooling/process parity pass against the fix pack @ `e6ec192`. The pass ported
> skills, the archive boundary, the entry-file rules header and doccheck `--regen` /
> `--emit-fingerprint`, and re-synced the fact mirror (68 → 107 files). Those are process changes
> and needed no ruling. The one below is a **module** question and MODULE FREEZE reserves it for
> you. Nothing about it was acted on. (Its companion, **OI-02** — *"the other seven modules have
> not been re-checked against 1.1.0; check them when?"* — was CLOSED on 2026-09-17: option (a) was
> carried out, and its output is the ruling above.)

OI-01. **`ClassicRockets` (D01) is obsolete on 1.1.0 and now points the other way — retire it,
    rewrite it, or leave it?** *This is the "classic rockets is probably no longer needed" call.*

    **What changed.** The module exists because 1.0.7's
    `UniversalRocketBase:GetFuelResourceRequest` returned **0** for a rocket parked with no
    destination picked, so drones never topped it up
    (`SMR-SrcArchive\1.0.7.396349\Src\Lua\UniversalRocket.lua:1639-1642`). On 1.1.0 the same
    function returns the **full ration** in that state:

    > `if not self.arrival_loc then return self:IsPlayerControlled() and not self:IsSpecialAutomode() and amount or 0 end`
    > — `SMR-SrcArchive\1.1.0.403908\Src\Lua\UniversalRocket.lua:1891-1895`

    ⇒ **Vanilla now ships the module's entire feature**, for exactly the rockets it was written for.

    **The part that is not just redundant.** The wrapper only fires when the shipped answer is `0`
    (`Code/Opt_ClassicRockets.lua:83-90`). On 1.1.0 the only way to get `0` while still passing the
    module's own `IsPlayerControlled()` + `GetDepartureLocType() == "our_colony"` guards is
    `IsSpecialAutomode()` — Trade, TradePad and Rival rockets (`UniversalRocket.lua:2020-2026`).
    So its whole remaining reach is **forcing a fuel request onto the rockets 1.1.0 deliberately
    excludes**. That is the opposite of "restore the legacy behaviour": nothing about trade rockets
    was ever part of D01.

    **How this was established, and its limit.** Read off the two archived source trees, 2026-09-17.
    **Desk only — not run in the game**, and the toggle is off by default, so no player has seen
    either behaviour on 1.1.0. Falsifier: enable the module on 1.1.0, park a player rocket with no
    destination, and confirm vanilla already refuels it; then park a Trade rocket and watch whether
    it starts demanding fuel.

    **Options:** (a) **retire the module** — delete the file, drop its `items.lua` toggle and its
    `metadata.lua` `default_options` entry, keep D01 as the record. Cheapest, and the store copy
    for it (fix pack `reports/RELEASE_DESCRIPTION_OPTIN.md`) never has to be written. ⚠️ Removing a
    Mod Options toggle is an **account-state** change, not a save-state one — check what a stale
    `ClassicRockets` key in `AccountStorage.ModOptions` does before promising it is clean.
    (b) **keep it, narrowed** — add `and not self:IsSpecialAutomode()` so it can never fire on
    1.1.0, leaving it as a no-op that would come back if a future patch reverted the change.
    (c) **leave it exactly as it is** and document the trade-rocket effect as intended.
    **Recommend (a)** — it is the module whose reason for existing vanilla has adopted.
    Whichever you pick, it is a behaviour change to a frozen module and needs your line.

---
### 2026-09-17 — OI-03, OI-04 OPEN: the other seven modules, re-read against 1.1.0 (this answered OI-02)

> This is OI-02 option (a), carried out: one desk pass over the seven modules other than
> `ClassicRockets`, against `C:\Dev\SMR-SrcArchive\1.0.7.396349\Src` and `…\1.1.0.403908\Src`.
> ⛔ **Source-only. The game was not launched and no playtest was run**, every item below names a
> falsifier, and **no code, no `status:` word and no heading tag was changed.** Full working:
> `docs/agent/reports/MODULE_REVALIDATION_1_1_0.md`; each module's own record carries its dated
> section. **Two of the seven are complete no-ops on 1.1.0 while still reporting `active`.**
>
> | module | verdict |
> |---|---|
> | D09 `DroneStatDials` | **STILL NEEDED** — every cited mechanism unchanged. No ask; ⚖️ KEPT 09-17. |
> | D04 `MultipleSuns` | **STILL NEEDED** — both halves. One new uncovered case → OI-04. |
> | D03 `ResidencyControl` | **STILL NEEDED**, one guard silently dead → OI-03. |
> | D02 `AcknowledgedWarnings` | **PARTLY OVERTAKEN** — the id was split seven ways. No ask (see the entry). |
> | D06 `DroneOverhaul` | **NEEDS A PLAYTEST TO TELL** → was OI-05 → ⚖️ RULED 09-17: PARKED, module deleted. |
> | D07 `CohortHousing` | **OVERTAKEN in-dome + INERT** → was OI-06 → ⚖️ RULED 09-17: DEAD, module deleted. |
> | D12 `NoHomeless` | **NEEDED in principle, INERT in practice** → was OI-07 → ⚖️ RULED 09-17: DEAD, module deleted — ⚠️ the DEFECT survives. |

OI-03. **`ResidencyControl` (D03): its tourist exemption is dead code on 1.1.0 and the row now
    lies to the player. Repair it, or accept the new behaviour?**

    **What changed.** `ChooseDome`'s first parameter went from a **traits table** to the
    **colonist**, and every caller followed:

    > `1.0.7.396349/Src/Lua/_GameUtils.lua:426` — `function ChooseDome(traits, domes, safety_dome, dome_elevators)`
    > `1.1.0.403908/Src/Lua/_GameUtils.lua:486` — `function ChooseDome(colonist, domes, safety_dome, dome_elevators)`

    `Tourist` is only ever a key of `colonist.traits`, never a direct member
    (`1.1.0.403908/Src/Lua/Units/Colonist.lua:2671, :2675, :2705`). The wrapper's guard
    `not (traits and traits.Tourist)` (`Code/Opt_ResidencyControl.lua:217`) is therefore `nil`
    for every caller ⇒ **tourists are now filtered out of closed domes too**, while the row's own
    rollover still reads *"Manual relocation and Tourists are unaffected"* (`:159`).

    **What is NOT at issue.** The feature itself is not overtaken — vanilla 1.1.0 still ships no
    middle setting between "open" and "quarantine"; its two new dome policies
    (`allow_work_in_connected`, `allow_service_in_connected`) govern residents leaving, which this
    module deliberately never touches.

    **Options:** (a) **repair the guard** — read the traits off either shape, one line, no design
    change; (b) **accept it and reword the rollover** — closed means closed, tourists included;
    (c) leave it until launch-day re-verification. **Recommend (a)**: the exemption was a
    deliberate design call (hotel rooms are not residency) and (b) silently reverses it. Either way
    it is a behaviour change to a frozen module and needs your line.
    **Falsifier:** close a dome and land a rocket carrying a Tourist with that dome the only
    sensible choice. If the Tourist checks in, this reading is wrong.

OI-04. **`MultipleSuns` (D04): 1.1.0 unbinds panels when a sun is demolished and never re-tests
    the other sun. Close the gap or document it?**

    **What changed.** Both halves are still needed — `build_once = true` is still on the template
    (`1.1.0.403908/Src/Lua/BuildingTemplate/ArtificialSun.generated.lua:16`) and
    `SolarPanelBase:GameInit` still tests only `labels.ArtificialSun[1]`
    (`1.1.0.403908/Src/Lua/Buildings/SolarPanel.lua:11-16`). But 1.1.0 added
    `ArtificialSunBase:Done` (`1.1.0.403908/Src/Lua/Buildings/ArtificialSun.lua:65-73`), which
    clears `artificial_sun` on every panel bound to the removed sun **without** checking whether
    another sun still covers them. With the limit lifted and two overlapping suns, demolishing one
    leaves panels dark until the next load — this module's only sweep is `OnMsg.LoadGame`
    (`Code/Opt_MultipleSuns.lua:196-215`). On 1.0.7 the case could not arise from vanilla.

    **Options:** (a) **add a `Done`-side re-link** mirroring the existing LoadGame sweep — small,
    same idiom, same guard; (b) **document it** the way D01's already-parked-rocket limitation was
    documented (owner, 2026-07-30) — it self-heals on the next load; (c) leave it for launch day.
    **Recommend (b)** — it is the same shape as a limitation you have already accepted, it costs
    nothing, and (a) is a module edit for a case that needs two suns AND a demolition AND no reload.
    **Falsifier:** with two overlapping suns, demolish one and watch the panels in the survivor's
    range. If they stay lit, there is nothing to decide.

---

### 2026-09-01 — ITEMS 94–97 OPEN: the D06 rebuild DESIGN SPEC (opt-in repo, `docs/agent/reports/DRONE_REBUILD_DESIGN_20260901.md`)

> The spec is the build-out of the tiers **under your directive that it must not need the Save
> Rescue or any uninstall mod** — which makes "uninstall-clean" and "nothing for the Rescue to do"
> hard constraints rather than trade-offs. Its build brief
> (`prompts/DRONE_REBUILD_BUILD_high.md`) is written and **will not start until item 94 has a line.**

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
