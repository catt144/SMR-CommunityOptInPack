# Arboretum test build — 2026-10-03

Owner scope and saved names: [D19](../bugs/D19.md). Starting HEAD `73d20d5`;
`git log --oneline -3; git pull` returned already up to date. Existing changes to
FUTURE_IDEAS, the prompt map, the supplied untracked prompt and store screenshots belong
to the starting tree. The build is for testing, not publication.

## Live work

- Prepared, awaiting audit/commit: module, D19, generated template/class and save contract.
- Prepared, awaiting audit/commit: real menu-load checks off/on, fix pack present/absent, original order restored.
- IN PROGRESS: sitting slots, owner asks, final gates and independent audit; then exact-path commits/push
  and consume `ARBORETUM_BUILD_high.md` with its map row. Audit selection is the remaining owner input.

Unattended audit is pending the owner's model selection requested in chat. Checks below are
working evidence until that independent review; no tested status or gameplay acceptance is claimed.

## Source findings

All paths below are under archived build **1.1.1.406343**, Steam build **25579348**,
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/`. Installed identity was read with
`python tools/doccheck.py --emit-fingerprint` at starting HEAD. These are SOURCE claims;
line locators were read with `rg -n` or the named function's source body.

| question | evidence and conclusion | falsifier / limit |
|---|---|---|
| Seeds and drones | `Lua/HasConsumption.lua:76` initializes a resource-agnostic demand; `:283` accepts delivery; `:375` charges a visit; `:388` debits and `:402` stops work at empty; `:441` tests positive stock. `Lua/_TaskRequest.lua:303` connects an in-dome requester to its dome's command centres. | A loaded dome with available Seeds and reachable drones never stocks the building. Desk callbacks do not prove pathfinding. |
| Shuttle delivery | `Lua/Buildings/StorageDepot.lua:1,53` provides ShuttleLanding and joins LRManager. The new service inherits neither that class nor its registration. | INFERRED: use shuttles to an exterior Seeds depot, then drones indoors. Direct shuttle delivery is not offered; no vanilla logistics change is needed. Confirm the two-stage route in play. |
| Comfort | `Lua/Stats.lua:219` weights service stats by people served/population; `:568,598` adds categories; `Lua/ServiceBase.lua:98,110` derives category and display name from the template. `Lua/Buildings/Service.lua:56` queues reassignment on working changes. | Comfort is coverage, not a reward tied to each visit. No visitors means no consumption even while stocked coverage exists. |
| Native visit path | `Lua/Buildings/Service.lua:271` calls `Consume_Visit`; `:240` refuses an empty store. | A nominal rate is not actual Seeds per sol. Measure debits during organic visits. |
| Placeholder | `Data/BuildingTemplate/GardenNatural_Large.lua` supplies `GardenLargeCP3`, the Large Garden icon, 40 capacity and 10 visitor slots; `Lua/_EntityData.generated.lua:11736` declares its entity. | Actual footprint and fit in each dome require runtime geometry and placement; no all-dome-fit claim. |
| One per dome | `Lua/Construction/Construction.lua:2959` checks `build_once_per_dome`, including queued construction through `FoundBuildingInDome`. | Try a second placement before and after the first finishes. |
| Seeds availability | `Lua/Terraforming.lua:512` reads Seeds' preset lock. Module adds its own lock for unavailable Seeds and NoTerraforming. | Hidden until available, rather than an unusable build entry. |
| Removal | `CommonLua/Core/persist.lua`, `PersistGatherPermanents` missing-class resolver uses the saved fallback prefix or UnpersistedMissingClass. | Source-derived residual only; real removal save/load remains owed. |

The implementation uses no replacement service or logistics methods. Its class/template data
keeps the native stock, working-state and coverage mechanisms. The starting constants are in
D19; balance is for the owner's next sitting. `max_visitors` follows the actual donor
template rather than the scout's proposed twelve; it satisfies the native no-shift validation.

## Verification evidence

`python staging/tools/arboretum/deskcheck.py` at HEAD `73d20d5` plus the Arboretum working diff:
native debit/empty/restart controls and build locks passed. This is a synthetic Lua check,
not a game boot. `python staging/tools/arboretum/generate.py --check` found fresh outputs;
`python tools/parsecheck.py` parsed the code list. Independent review remains pending.

Menu-load evidence (MEASURED; audited below; the seven logs are tracked, force-added past
`.gitignore`'s `*.log`, and all predate the move to `staging/`):
`python staging/tools/arboretum/read_boots.py` validates complete logs under
`docs/archive/arboretum_20261003/`, with required successful controls and a failing error check.
The receipt carries HEAD, hashes, line numbers, error filters and their members.

| archived log | cold option | fix pack | result |
|---|---|---|---|
| `present_off.log` | off | present | class/template and live off/on checks pass |
| `present_on.log` | on | present | same |
| `absent_off.log` | off | absent | same |
| `absent_on.log` | on | absent | same; requests restoration of original enabled order |
| `restored.log` | off | present | confirms original saved/loaded order and final editor handle |

Representative log evidence: `cold active=true expected=true fixpack=false`,
`template=SMROptInArboretum entity=GardenLargeCP3 resource=Seeds stat_scale=1000`,
`live=false reconciled=false`, `live=true reconciled=true`,
`result=true detail=menu class/template and toggles only; gameplay NOT RUN`.
The present configuration loaded local fix-pack metadata v1.00-026; this does not independently
verify which bytes were published. Each leg launched a fresh retail Mars.exe process and exited
before its log was copied. These are menu-load checks, not the full §8 shipping gameplay battery.

Commands per leg: `python staging/tools/arboretum/prepare_boot.py <leg>` then the sibling fix pack's
`tools/arm_leg.ps1 -Manifest scratch/arboretum_boot/leg.json -Mode arm`, a hidden-window
`Start-Process` of the installed Mars.exe, and `-Mode disarm` after exit. No colony was loaded
or saved. The script's opt-in override and live option changes are RAM-only. For the absent
pair it uses native TurnModOff/TurnModOn and the kit's persistent writer to flush account
order, restoring the kit's prior string bytes (an absent slot becomes an empty string).
The original order, both observed before mutation and confirmed in restored.log, is
fix pack → TestKit → Opt-In. The kit metadata diff is empty after disarming.

The failed first attempts are retained, not counted as successful runs:
`attempt1_present_off.log` hit a probe-only nil editor-id assumption; runtime templates
have `template_name`/`class`. `attempt2_present_off.log` rejected an empty Build surface.
That assertion was invalid for a garden: `hex.lua:232` only supplies Build shapes for
entities exposing that surface; ordinary placement also uses Outline. The revised check
compares the entity against the native Large Garden and defers geometry/placement to a map.
An editor handle collision with the depot material was found after the matrix; source was
changed from 11 to 12, a generator collision check was added, and restored.log verifies
the final generated template. This changes editor identity, not runtime balance or hooks.

Whole-log review command: `rg -n -i 'error|assert|exception|fail|warning'
docs/archive/arboretum_20261003 -g '*.log'`. The logs also report Braze SessionStart DNS
failure, launcher-event sending failure and initialization failure. These are named startup
network errors, separate from Lua/module results, and remain outside this build's scope.
The successful menu legs have no `[LUA ERROR]` matches; `read_boots.py` requires the positive
module/class/toggle/end-of-log markers before accepting that negative.

Actual Seeds per sol: **<<PENDING-RUN>>**. No source-derived throughput is substituted.
Built/stocked/serving witness, every-dome placement and removal load: **NOT RUN**.
The first-enable-from-Mod-Manager path also remains owner-attended: the sandbox blacklists
ModsReloadItems; cold boots and live Mod Options flips do not substitute for that path.

## Sitting

The SMRTK **Slots & notes** tab is preloaded from `staging/tools/arboretum/slots.lua.txt` by
`python staging/tools/arboretum/preload.py --install` [RAN 2026-10-03, disk receipt
`staging/tools/arboretum/preload_receipt.json`; callbacks not yet run in a loaded game].
Kit branch: `arboretum-sitting-20261003`; the previous train-soak sitting is recoverable from
kit commit `b58ae18` and `tools/trains/soak/compose.py`. No shared toolkit leaf is changed.

Fixture: a disposable current-build save with an inhabited dome, available Seeds in a depot
under drone coverage, and power/water. Prefer an isolated dome with 20–100 residents so the
coverage comparison is simple. Cheats for ordinary colony support remain permitted, but do
not fill consumption stock during the organic measurement. The slot observes actual returned
amounts from native consumption, so drone replenishment cannot conceal use. It writes no
object fields. A save/load/map change removes the observer and explicitly aborts the sample;
take the fixture save before starting the run. Autosave interruption is not a successful sample.

| order / slot | owner action and prediction | refuting result |
|---|---|---|
| 1 | Load the disposable save, open Slots & notes, press **1**. It reports active/Seeds/rule state. Enable Arboretum through Mod Options if needed. | No template when active with Seeds unlocked. |
| build | In Decorations → Gardens, place an Arboretum. Look at the footprint and appearance. Try a second in the same dome while the first is queued, then after completion. Let drones deliver construction and Seeds; Quick build is available for construction only. | Spire required, second placement accepted, or reachable drones never stock it. |
| 2, 3 | Select the completed Arboretum, press **2** to pin it, then **3**. View its infopanel and the dome's Services readout. A stocked working building has an Arboretums category with positive coverage. ServiceInterestTags, if on, displays its interests. | Working stock with no category/coverage, or category incorrectly merged into Parks. |
| 4 → 5 | Press **4** after natural stocking. Run until advances to the named sol at top speed and pauses; press **5**. It logs actual Seeds debits, elapsed game time, visitor delta and milli-Seeds per sol. | No native debit/visitor liveness, new Lua error, or an interrupted/short window: report INCOMPLETE, not a successful sink. |
| 6 | Press **6**. This deliberately consumes the stored Seeds, pauses, and flushes native service reassignment. The building reads empty/not working and its category contribution falls. This is forced depletion, excluded from the rate sample. | Empty stock still supplying the Arboretum contribution. |
| 7 → 3 | Press **7** to resume for a sol; drones may replenish naturally. Press **3** at the pause. Verify stock and coverage recover. | With supplied/reachable drones, stock stays empty; or stocked/working coverage never returns. |
| 8 | Press **8** off, reopen the build category, then press it on and reopen again. Off hides new Arboretums while the placed one remains. This toggle is session-only; use Mod Options to save a preference. | Existing building disappears/stops solely because of the option, or new buildings remain offered off. |

Each slot logs `SMRTK_ACTION action=slot_<n>` and its DUMP fields; Run until additionally
logs ARM/FIRE. A non-Arboretum selection in slot 2 and an unpinned slot 3 must REFUSE.
Positive visit/debit counters are the rate reading's liveness witnesses. The synthetic desk
check tests a replenished sample whose start/end stocks are equal but consumption is positive,
and checks observer cleanup on both finish and save.

Timing is in game time: organic window ends at the displayed current-sol +3 boundary;
refill ends at the next sol. Both use the toolkit's fastest supported Run until and pause.
Abort after three attempted windows without the corresponding liveness, or immediately on an
engine error; preserve the failed record. Visual checks require the owner's eyes because menu
loads cannot settle art, pathfinding or the UI. No console typing or colonist hunting.
Close the sitting with toolkit Taint, Eligibility and Flush + copy; archive the complete log
after game exit. The pre-existing toolkit UI witnesses in SMRTK.md are NOT RUN by this build.

Riders: when testing a different dome type, try the same placement; with a shuttle-fed distant
Seed source, witness the exterior-depot → drone → Arboretum route. Save-exit/removal and a real
main-menu mod enable remain separate shipping evidence, not claims made by this short sitting.
Owner decisions about category and footprint are OI-47/OI-48 in this mod's checklist; the
live sitting belongs to ck223 in the fix pack's checklist.

## Close-out

Executed model: **gpt-6-astra, high**, read from this session's `turn_context` record in
`C:/Users/stkot/.codex/sessions/2026/10/03/rollout-2026-10-03T17-35-28-01a103b1-872b-7a51-be98-d3e79e4ef242.jsonl`.
Only its model/effort fields were read for this receipt. Audit model and commits are pending
owner selection. Do not consume the prompt or promote the evidence until the independent
audit is complete. No new rule or engine-fact ID was minted.

Final checks: Opt-In and fix-pack `python tools/doccheck.py` GREEN; module and TestKit Lua
parse; generator parity and the native-body/slot desk checks pass. `upload_preflight.py`
accepts the Arboretum template/code wiring; it still fails on the existing missing preview
image. This is not an upload-ready release, and no publishing step was attempted.

The Opt-In gate's warnings, verbatim (existing archive files are append-only):

```text
  warn D16: the frozen index-row cell says 'built', entry says 'tested-attended' (from 'tag')
  warn D17: the frozen index-row cell says 'built', entry says 'tested-attended' (from 'tag')
  warn D18: the frozen index-row cell says 'built', entry says 'tested-attended' (from 'tag')
  WARN docs/archive/mechanized_depot_20261003/receipt.json
  WARN docs/archive/train_34b_sitting2_20261002/log_receipt.json
  WARN docs/archive/train_audit_20261002/lifecycle.json
  WARN docs/archive/train_audit_20261002/log_receipts.json
  WARN docs/archive/train_audit_20261002/smokes.json
  WARN docs/archive/train_final_battery_prep_20261002/smokes.json
  WARN docs/archive/train_final_battery_prep_20261002/smokes.txt
  WARN  M Code/80_AgentSlots.lua
```

Resume: audit the working diff, `tools/arboretum/` and complete boot logs on the owner's
selected different model. Then commit the module/record/save contract, followed by the
reviewed evidence and sitting. Exact paths only; force-add the ignored new archive logs.
Commit/push the sitting file on the kit's current task branch, and the fix pack's ck223 plus
its routing report without its pre-existing RULE_PLACEMENT_TEST edit. Consume the supplied
one-off and its map row only in the closing commit. Push the reviewed commits.
The owner's initial FUTURE_IDEAS changes and store captures remain outside these commits.

## Independent audit

Audited at `67fa46b` (committed HEAD, not a working diff), 2026-10-04, on the owner-selected
model named in Close-out. **Verdict: PASS — menu-load and desk evidence verified; gameplay
NOT RUN (ck223 owed).** No behaviour finding; no stop was hit. Records, locators and evidence
wording were corrected in the audit commit, listed under each row. Source root for every `grep`/`sed`
below: `B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/`.

| claim | check (command, at `67fa46b`) | result |
|---|---|---|
| Off by default | `grep -n "DefaultValue\|Arboretum = " staging/items.lua staging/metadata.lua` → `DefaultValue false`, `Arboretum = false`; deskcheck `default-off must hide`; mutation D1 (off lock removed) fails the deskcheck | PASS |
| No vanilla method replaced | `grep -n "^function\|= *function" staging/Code/Opt_Arboretum.lua` → 2 members: the Register `apply` and one `OnMsg.GetAdditionalBuildingLocks` handler; the generated class and template define data only | PASS |
| Seeds and NoTerraforming locks | `grep -n "function IsSeedsResourceAvailable" Lua/Terraforming.lua` → `:512`; `grep -rn '"NoTerraforming"' Lua` confirms the rule id; `sed -n 400,407p;731p Lua/X/BuildMenu.lua` shows any true lock hides the entry; mutations D2, D3, D4 (veto), D5 (template filter) each fail the deskcheck | PASS |
| One per dome | template `build_once_per_dome = true`; `grep -n build_once_per_dome Lua/Construction/Construction.lua` → `:2959`, `FoundBuildingInDome` on the template class | PASS (source; placement is ck223's) |
| Native consumption and coverage only | `consumption_type = 2`; `sed -n 29,35p;374-405p Lua/HasConsumption.lua` → `Visit = 2`, `Consume_Visit` → `Consume_Internal`, `UpdateWorking(false)` at empty; `Service.lua:271` calls it; category key is `self.class` (`ServiceBase.lua:98-102`) | PASS |
| Source table locators | each cited line re-read with `grep -n` | FINDING, corrected: nine locators were off by 1–6 lines (`HasConsumption` 74→76, 386→388/402; `_TaskRequest` 302→303; `StorageDepot` 52→53; `ServiceBase` 101,114→98,110; `Service` 57→56, 269→271, 246→240; `Construction` 2958→2959). No conclusion changed. The module's comment `BuildMenu.lua:731` is `Lua/X/BuildMenu.lua:731`; line correct, left as is |
| Save contract | `FIX_POLICY` inventory rows 32–33 against `staging/items.lua` (`Arboretum`), the template `Id`, both `DefineClass` names and `CommonLua/Core/persist.lua:164-165` (permanent-key form `<persist_baseclass>:<name>`); `grep -rn "GameVar\|Modifier\|rawset" staging/Code staging/Data` → 0 | PASS — no name in code is absent from the inventory. The lock keys `smr_arboretum_off`/`smr_arboretum_seeds` live in a per-query local table (`BuildMenu.lua:401`), not in a save |
| Both bans | `grep -rn "SMRFixPack" staging/Code staging/Data staging/items.lua staging/metadata.lua` → 0 lines; presence side `grep -c SMROptInPack staging/Code/Opt_Arboretum.lua` → 4. `boot.lua.txt` and slot 1 read `rawget(_G,"SMRFixPack")`; both are TestKit-installed probe text, not this mod's executable code | PASS |
| The move | `git diff -M 0ff4a85 78eed20 -- '*SMROptInArboretum*'`; `git rev-parse 0ff4a85:Code/Opt_Arboretum.lua HEAD:staging/Code/Opt_Arboretum.lua` → both `a9b8607` | PASS — identity only. The template's two changed lines are the GENERATED header comment and `SaveIn` (`Mod/SMR_CommunityOptInPack` → `…_Workbench`), the editor's owning-mod field; the generated class changed its header comment only. No property, hook or balance value moved |
| Desk evidence | `python staging/tools/arboretum/deskcheck.py` exit 0; `python staging/tools/arboretum/generate.py --check` → fresh; `python tools/parsecheck.py` → 19 files, 0 errors | PASS. Limit: the deskcheck's `IsGameRuleActive` stub ignores its argument and `typeVisit` is hard-coded 2, so a wrong rule id (mutation D6) or a wrong visit type would pass it; both values are cleared by the source greps above instead |
| Boot evidence | `python staging/tools/arboretum/read_boots.py` exit 0; on a scratch copy it exits 1 for an injected `[LUA ERROR]`, a removed `live=true` marker, `result=false`, and either failed attempt substituted for `present_off`; `sha256sum` of the five legs equals `review_package.json` | PASS. 5 legs + 2 retained failed attempts = 7 logs on disk; `attempt1` ends `result=false … nil value (field 'id')`, `attempt2` `result=false detail=invalid entity/consumption`, as described |
| Boot evidence scope | `git log --oneline 78eed20..HEAD -- staging/`; `grep -l -i arboretum docs/archive/workbench_20261003/*.log` | FINDING, wording: all seven logs predate `78eed20` and loaded the module from the production mod, four legs with editor handle 11. They verify the byte-identical module code, not the workbench load path; that path's evidence is `STAGING_WORKBENCH_20261003.md` and its own logs. `read_boots.py`'s receipt strings (stale command path, "working diff") corrected to say so |
| Sitting slots | desk reading of `staging/tools/arboretum/slots.lua.txt` against the sitting table | PASS. Slot 2 refuses a non-Arboretum or a construction site; slot 3 refuses unpinned; 4 refuses unless working, stocked and populated; 5 reports INCOMPLETE without debits or the target sol; 6 debits through native `Consume_Internal`, as the table says. No slot writes an object field: slot 4 wraps the class's `Consume_Internal` in RAM and removes it on finish, save, load and map change; slot 8 flips the mod's option object. Callbacks have never run in a loaded game |
| Path drift | `grep -n "tools/arboretum" <this report>` | FINDING, corrected: eight `tools/arboretum/` cites now read `staging/tools/arboretum/`. `staging/modules.json` lists paths relative to `staging/` by design |

Not supported by this audit: "tested", "accepted", any Seeds-per-sol figure, footprint, drone
routing, removal behaviour, or the first-enable-from-Mod-Manager path. D19 stays `built`.
