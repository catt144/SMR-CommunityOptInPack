# Shipping evidence and remaining plan — 2026-10-03

Authority: Launch_Prep/01, owner launch preparation and its recorded 2026-10-03
rulings. Started at `82369ec`; `git pull` reported already up to date. This is a
desk preparation record, not a new attended test or publication approval.

## Live work list

| unit | state | completion evidence |
|---|---|---|
| Source/build and accepted evidence ledger | prepared | packaged source receipts and scoped module verdicts below |
| Granted OI actions | prepared | guard_result.json, parsecheck; documentation gate at commit |
| Save residue, rescue applicability and provenance | prepared with holds | exact Save B preserved; graph ownership and Tripo origin unresolved |
| Remaining attended plan and independent review route | prepared | filled 02 and 01A; corrected plan reread by the second seat; 04 drift notes |
| Close and push | IN PROGRESS | exact-path/hunk commits, checks, model transcript receipt |

The initial shared tree contains an Arboretum test build (D19) and changes to
metadata, items, policy, checklist, future ideas, generated index and prompt map.
Those changes are outside this brief's original shipping set and are preserved.
Its first-release scope is awaiting the owner's answer; no all-modules certification
can silently omit a module present in the package. No sibling writes are authorised.

## Build and source ledger

MEASURED at `82369ec` plus the explicitly named shared worktree diff. Commands:
`python tools/doccheck.py --emit-counts` and `--emit-fingerprint` both GREEN.
The emitted set is **8 registered modules**, reconciled to AcknowledgedWarnings,
MultipleSuns, DroneStatDials, ServiceInterestTags, StationRows, TrainHub,
ElevatorDepot and the uncommitted Arboretum. D05 is the enable surface, not an
additional module. Original launch rows below exclude no package member silently:
D19 is explicitly uncovered, awaiting OI-50 and its own build/audit acceptance.

`python scratch/ship_evidence_capture.py` decoded the installed `Lua.fpk` and
`Data.fpk` through the existing fix-pack FLPK/ZSTD reader, compared every matching
archive member byte-for-byte and failed on absence/divergence. Captured implementation:
`docs/archive/ship_evidence_20261003/source_capture.py`; receipt
`source_receipt.json` contains command, HEAD, pack hashes, every member and digest.
Results: Lua/CommonLua **2374/2374**, Data **2192/2192**; totals are the lengths of
their receipt member lists, filtered by those exact archive prefixes. Includes
the core, Mod Options, save metadata, every source-defined target of the newer
train/D15 modules and relevant Data. C++ internals are outside this source claim.

Installed Steam build **25579348**, decoded revision **406343**, version
**1.1.1.406343**. Recomputed manifests match the archives. Both 405907 and 406343
trees have digest `d753f949af92e2b753f44163a2e47229e371f810ef3c2752d30a98953af2663c`.
Thus citations derived on 405907 retain their bodies on the shipping build;
doccheck's MOVED label compares build identities, not those bytes. No blanket
promotion of older fact groups is implied.

The pending gamepatch command's default old-tree selection now chooses 405907,
so it cannot reproduce its historical 1.1.0 comparison. Actual run from fix-pack
`30dacada`: `python tools/patchcheck.py --code Code --code
B:/Dev/SMR/SMR-OptInPack/Code --no-notes --rows 100` reports no moved groups,
full pack parity and identical declarations. The deliberate historic comparison
`--old 1.1.0.403908 --new 1.1.1.406343 --code B:/Dev/SMR/SMR-OptInPack/Code
--no-notes --no-parity --rows 100` exposes the old pending rows plus later modules.
`--no-parity` there avoids repeating the separate captured parity measurement.
Later modules were authored against 1.1.1; their 1.1.0 differences are not new
post-acceptance changes. Their 405907→406343 baseline holds. No patch-notes
fetch or whole-engine semantic claim is inferred from either instrument.

SOURCE body review of both versions is preserved in `moved_bodies.diff`:

| entry / target family | disposition on 1.1.1.406343 | reason and falsifier |
|---|---|---|
| D02, RequiresMaintenance | KEEP | Added maintenance-demand completion at UpdateMaintenanceStuckNotification's caller; acknowledgement reads/writes and routed warning boundary remain. The diff would refute this if it changed routing or acknowledgement. |
| D09, Colony.CityStart / MarsGameEffects | KEEP | Added NoPolitics tech hiding and a tech modifier display name. Neither changes the dial modifier ids, arithmetic or SetLabelModifier contract. |
| D04, BuildMenu | KEEP | Nil-template guard and mouse-leave delegation added; valid ArtificialSun build_once handling and panel/sun hooks remain. The upstream lead omitted the mouse-leave change; read and recorded here. |
| D15 and D16–D18 source targets / Data | KEEP existing implementation | Their 1.1.1 baseline has identical current packaged bodies. No move requiring re-derivation; preserve accepted native scope below. |
| D05, CommonLua Mod/option loading and metadata | KEEP; final surface cell open | Pack parity proves source inputs; it does not show that today's displayed option rows work. |
| D19 | NOT CERTIFIED | Source pack parity includes its native dependencies; launch acceptance belongs to its own build and OI-50. |

`python tools/sigcheck.py` exited successfully but reported MISMATCH/ABSENT/MULTI
candidates over lexical declarations, including module-owned functions. This is
not a clean-signature or semantics verdict. The pack/body evidence above, existing
module controls and retained native acceptance supply the actual disposition.

## Accepted evidence and uncovered cells

| member | accepted evidence | remaining work / limits |
|---|---|---|
| D02 AcknowledgedWarnings | OWNER 2026-10-02: played routed-warning widening; both configurations accepted through `f3d6c78` | `git diff f3d6c78 -- Code/Opt_AcknowledgedWarnings.lua` empty. No repeated warning sitting. Legacy status retained. |
| D04 MultipleSuns | OWNER 2026-10-02: sun demolition/relink and both configurations accepted through `f3d6c78` | Initial diff empty; this pass adds the granted declarative guard and one comment only. Guard A/B below. No repeated sun battery. |
| D09 DroneStatDials | OWNER 2026-10-02: extensive use and both configurations accepted; legacy PT-56 includes stale-save/base cleanup | `git diff f3d6c78 -- Code/Opt_DroneStatDials.lua` empty. No repeated dial battery. |
| D15 ServiceInterestTags | Attended 2026-09-30; off/on, save/load, menu enable and both configurations accepted | Runtime file unchanged since `102aad0`; uninstall acceptance rests on no persisted state, still unchanged. Fix-pack present acceptance is conditional on no newly shared hooks. |
| D16 StationRows | Train 35 retained-scope PASS; P released 1.0.26; A owner-waived | No train rerun. B2 vanilla requests restored after full removal on station 10531, underground. Saved row table is inert without module code. |
| D17 TrainHub | Train 35 retained-scope PASS; hub soak owner-accepted; P 1.0.26, A waived | Retained class references and colony upgrades are exit disclosures/investigation, not a new movement/soak battery. |
| D18 ElevatorDepot | Train 35 retained-scope PASS; OI-38 accepted scripted UP leg; P 1.0.26, A waived | Depot soak and positive soak control declined; add neither. Demolish both halves before removal. |
| D05 enable surface | Legacy PT-51 plus D15 and train enable/toggle evidence | 02 checks final option membership/labels/defaults, main-menu enable and cold persistence in P/A. It does not repeat accepted module behaviour. |
| OI-43 warning | SOURCE new/save-old flag distinction; metadata now false | 02 samples new nonoptional save versus untouched old optional=true save after full restart, including screen dialog. No warning result claimed yet. |
| D19 Arboretum | Separate test-build report and pending audit/owner decisions | OI-50 decides launch scope; 02 stops on an unaccepted addition. |

D15 present-side check: `git -C ../SMR-BugFixPack rev-parse HEAD` gave
`30dacadad4257532ddeb4897826036186657b049`. Literal-name regex search over its
`Code/` for `GetServiceDescription|sectionVisitors|sectionFoodService|IsOneOfInterests|
ServiceInterestsList|GetServiceList|InfopanelSection|ipBuilding` returned no hits;
the same search in this mod supplies the positive membership control in the
review receipt. This is a named-hook comparison, not an all-interactions proof.

Train receipt verification: the capture command's archived log hashes and every
filter count were reconciled to its members once by `source_capture.py`.
`TRAIN_FINAL_BATTERY_20261002.md` owns the native detail: B0/B1/B2 and retained B4
PASS; B3/B6 OWNER CLEARED; B5 OWNER SKIPPED; other B2/B4 items STRUCK; A WAIVED.
The B2 error-free window is lines 404–481 of the archived 13.05.06 log, not the
whole process. Its earlier content-bearing load raised errors. No skipped case
becomes a native pass and no extra UP crossing-ledger proof is inferred.

D14 disposition: (a) native waiter repaired/verified; (b) cross-map ownership,
(c) nanite early-return and (d) split-after-discovery remain conditional historical
findings, not proved native defects by this desk pass; (e) EntitySpec retail/editor
path repaired; (f) siding departure repaired/owner-confirmed; (g) launch-accounting
desk repair; (h) active notification cold-load fixture not sampled by B0; (i)
strict-global flight load repaired; (j) pad visuals desk repair. The owner's final
scope closes launch battery work without converting these individual limits into
passes. Preserve the D14 open record; future recurrence is situation-gated shared
sitting work, not another launch battery. The B3/B5/B6 review mapping is in
`git show c5db1f4^:docs/agent/reports/TRAIN_FINAL_BATTERY_20261002.md`: B3 cargo
recovery, B5 drone accounting/notification/legacy-save edges, B6 depot contention
and travel/upgrade receipts. D14(g)/(h)'s B5 cases were skipped, not passed.

## Granted actions

OI-43 **warn** is recorded in FIX_POLICY §3 and implemented as false in metadata.
OI-11(b) is recorded in D04: `SolarPanelBase.GameInit` now appears in Require;
its allowlist exception is removed. `guard_result.json` names real-source hashes
and the ON/OFF delegation, absent-target and isolated missing-pair controls.
`python tools/parsecheck.py` passed. These are desk controls, not game launches.
OI-13 **sweep** changes exactly the surviving `the pack` comments in core and
MultipleSuns, with no executable change from the comment sweep. OI-14 is recorded
at FIX_POLICY §6 and FUTURE_IDEAS §4(b): English only for launch, own translations
post-release. The asks had already been removed before this session; their
unperformed actions are now homed, not re-asked. OI-46 stays post-launch.

## Save residue and exit

MEASURED: exact final Save B was still available. Its decoded metadata matches
the battery's game time, toolkit session, last action id and filename. A byte copy
now lives at `local/ship-evidence-20261003/SMRTK_B.sav`; `save_receipt.json` pins
its SHA-256 and decoded persist member. `save_decode.py` validates BPUL fragments,
ZSTD lengths and frame-offset tables. Subsequent `rg -a -o` finds the colony
upgrade receipt, station-row field and both custom-class permanent keys; each
token has one occurrence, with every offset in the receipt. Those are token
counts, not object counts. Original save unchanged.

| residual | evidence / owner | exit disposition |
|---|---|---|
| Non-base Drone modifiers | SOURCE D09; native historical PT-56/D13 evidence | Set both dials to base, Apply, save while enabled. Re-enable this mod to do that if already removed. Existing rescue targets both exact ids; do not promise a train rescue. |
| Acknowledgement flag | SOURCE D02, FIX_POLICY inventory | Inert without module code; rescue also names it. No harmful effect inferred. |
| Extra suns / panel links | SOURCE D04 | Vanilla objects remain; build-once limit returns. No custom class to rescue. |
| Station row settings | MEASURED token; SOURCE `SMROptIn_station_rows` writer/reader; native B2 requests | Retained inert settings; no cleanup promise. |
| Colony hub upgrades / native modifiers | MEASURED `SMROptIn_hub_upgrades` in content-free Save B; SOURCE `colony_upgrades`, `adopt_colony_upgrades`, `sync_colony_upgrades` | Receipt survives demolition by design. Native modifier effects can survive removal as FIX_POLICY §3 already warns. Disclose possibility; exact loaded modifier effects/registrations remain unmeasured here. |
| Hub/depot class references after deletion | MEASURED exact keys in decoded Save B and native missing-class warnings | Native serialized graph ownership is NOT decoded. Do not label the references harmless or recovered. Exact read-only ownership prerequisite below. |
| Standing custom buildings | MEASURED errors on first removal load; OWNER OI-45 | Demolish hubs and both depot halves while installed, save, then disable/remove and fully restart. No recovery work authorised for standing buildings. |
| D19 content | Outside original launch set | OI-50 and D19 must supply its exit if included. |

SOURCE rescue comparison: `../SMR-CommunitySaveRescue/Code/10_SaveRescue.lua`
ROWS contains exact DroneSpeedDial/DroneCarryDial and acknowledgement fields;
it has no hub/depot/row-state or colony-upgrade targets. The search and positive
members are in `review_receipt.json`. D13's 2026-08-14 grant and 0.1.0 local
artifact cover the old target set only. No train coverage follows from that grant.
OI-45's no-recovery disposition is honoured; it is not a blanket erasure of §3.
Release dependency: the permanent release job/04 must establish availability and
applicability of that existing standalone dial-rescue artifact with its sibling
owner. This task makes no rescue/fix-pack edit or publication claim.

Unresolved prerequisite for a final residue certification: a read-only graph
inspection of this hash-pinned Save B with the mod loaded, identifying native
root→owner→field/key paths to both retained custom classes, plus the actual
colony modifier registrations/effects. A token scan cannot supply those edges;
unpersist is native, and no object-graph decoder is present in the inspected
tooling. Launch remains held on this row under 01 stop 2. The exact continuation
in 02's prerequisite section owns preparation/execution; it may use a bounded
read-only native slot under shared-kit authority. No destructive cleanup, battery
rerun or new recovery promise is authorised. If it discovers harmful residue,
record the concrete owner choice/build prerequisite before any behaviour change.

Player disclosure for 03/release, now justified by actual content-free Save B:
**"Bought Train Hub upgrades remain recorded in your save after all hubs are
demolished, and their ordinary game bonuses may remain after the mod is removed."**
Added under YOUR SAVE, AND REMOVING THE MOD in both maintained UPLOAD_WORKFLOW §3
blocks and regenerated metadata. Mirror on `content/opt-in/index.md` through 03;
sibling site writes remain outside this link's authority.

## Provenance and exact credit handoff

| shipped family | source route | credit/notice disposition |
|---|---|---|
| Original runtime/tooling | This repository and split donor history; LICENSE | Preserve original MIT notice. No claim that MIT owns the game's portions. |
| Game-derived Lua / vanilla objects and art references | Archived 406343 source; LICENSE existing game-derived notice | Preserve Haemimont Games / Paradox Interactive notice. Native props are referenced by entity name, not claimed as original art. |
| Train hub body and glass | `SMR-Assets/trainhub/blender/hub_skeleton.py`, `build_workfile.py`, `export_prep.py`, paint/bake scripts → SourceData SIE/GFX paths → Entities | Scripted geometry/textures plus retained Tripo-derived under-deck beds/pylons/feet. The generated replacement collars did not remove the whole Tripo mesh. OI-49 asks origin/plan for the remaining notice. |
| Depot/receiver | `SMR-Assets/elevatorstation/blender/depot_build.py`, `depot_geometry.py`, `depot_paint.py`, `depot_bake_ao.py` → SourceData and imported entities | Project-generated geometry and baked texture route; vanilla cabin/rope remain game references. |
| Icons, preview, screenshots | Assets render sources; STORE_SCREENSHOTS_20261003; source import paths | Model renders and owner gameplay captures with local annotations; same underlying asset credits apply. |
| Prior-art acknowledgement | Donor `PRIOR_ART_SURVEY.md` §5; donor archive `RESEARCH.md` LukeH Martian Express entries | Credit as prior modding/patch research, not authorship of this mod's modules or imported code. |

Exact general credit line for 03's maintained bodies and public README/site:
**"Thanks to ChoGGi for prior Surviving Mars modding work, and LukeH for Martian
Express patch research."** Preserve LICENSE's separate game-derived notice.
No source inspected establishes direct incorporation of their code into these
shipping modules; the acknowledgement is intentionally scoped to prior art.

Tripo source check 2026-10-03: [official terms](https://www.tripo3d.ai/terms),
§5.2, and [official usage guidance](https://www.tripo3d.ai/help/privacy-policy/how-to-use-tripo-models-commercially)
distinguish free and paid generation. They do not identify this model's origin.
OI-49 owns that missing fact; 03 supplies the resulting exact attribution/notice
before publication. This is an asset-provenance hold, not a new product design.

## Shared TestKit handoff (no sibling edits)

At kit `b58ae18`, `60_Probes_Opt.lua`'s OptionsMenuOptIn WANT still starts with
retired ClassicRockets and also contains parked/retired ResidencyControl,
DroneOverhaul, CohortHousing, NoHomeless. It omits D15 and train ids. It fails
before proving current membership. Kit owner: replace its expected contract with
the owner-selected final shipping toggle list and separate DroneStatDials choice
keys; assert no retired rows, exact registry/options/default membership and base
choice strings. Positive control is the final manifest; negative control removes
a required row in a synthetic isolated fixture and must fail. Do not call the
old probe PASS or widen the train battery to repair it.

`75_SMRTK_Saves.lua:12` derives filenames from `config.SaveGameExt` (it was not
proved newly changed; an early commentary inference is withdrawn). Its Saves
page already exposes **Override load A/B/C**, with metadata inspection before the
foreign-session bypass. Use that explicit triage route after verifying filename
and provenance. Ordinary Load refusal is intentional. Native menu discovery of
the historical `.sav` files remains unproved; do not instruct native-menu loading
of them. Shared owner should reconcile SaveGameExt versus the native save tag and
menu filter, with new-save discovery and cross-process controls. Do not rename
historical saves or alter their evidence. The recorded console workaround stays
a historical successful action, not a requirement for the new plan.

## Second-seat review and execution limits

Sequential read-only second seat requested on `gpt-6.1-sol`, high, through the
subagents skill. It found: AccountStorage is blacklisted; transition liveness
must cover every selected row; W needs an explicit Opt-In-absent gate; native
save completion needs running game time; class permanent tokens do not prove
retained building objects; loading with Opt-In can rebuild modifier registrations
and refresh the old optional flag in memory. All were corrected in 02/01A.
Primary source check: archived 406343 Mod.lua:1283, SavegameMetadata.lua:13,303,
Core/persist.lua:149–165; current TrainHub LoadGame and sync_colony_upgrades.
The immutable `save_flag_receipt.json` now pins OLD's true flag to raw metadata.
No original archive was rewritten. The reviewer found the corrected scope suitable
for conditional kit implementation; implemented bindings still need their own
second-seat read before any sitting. No new game process was launched.

Executed root model: **gpt-6-astra**, read from turn_context model records in
`C:/Users/stkot/.codex/sessions/2026/10/03/rollout-2026-10-03T19-05-51-01a10404-45df-7c31-9a22-8e6e931229c0.jsonl`.
The JSONL scan matched the owner's exact 01 task in a user response_item and
emitted its model set. Review invocation: `gpt-6.1-sol` / high; read-only,
sequential, no sibling edits or git mutations. Session-close skill applied to
the findings/routes in this report. 04 remains the different owner-selected terminal audit.

## Validation and close routing

At `82369ec` plus this staged preparation and the separately identified Arboretum
worktree, `python tools/doccheck.py` is GREEN, including parser and wrap checks.
The first run was RED because the consumed gamepatch path had not yet been staged;
staging the byte-identical move made the tracked-path check agree. No gate was
bypassed. `python tools/upload_preflight.py` passes all checkable local guards;
the portal login remains UNCHECKABLE. `python tools/store_parity.py` passes.
`git diff --cached --check` reports only original whitespace inside the archived
engine diff; that immutable evidence is preserved. The same command excluding
that exact evidence file is the authored-change whitespace check.

The final second-seat reread at `82369ec` confirmed every correction listed above
and conditional readiness for kit implementation. No native game tests ran.
Granted code changes, residue/disclosure, provenance, D14 limits, stale kit probes,
save filename/override semantics, and model/drift evidence all have explicit homes
above and in 02/03/04. The remaining graph read is owned by 01A; provenance and
package scope are OI-49/OI-50; existing dial-rescue availability belongs to the
release owner/04. OI-51 is a non-gating preference. No unhomed finding is dropped
when 01 is consumed. The original brief remains recoverable from its deletion
commit. Shared Arboretum changes are excluded through partial-hunk staging;
no sibling work is committed or edited by this task.
