# Exact Save B residual read — 2026-10-03

Authority: Launch_Prep/01A and OI-45, demolish first, disclose, no recovery work.
Started at `0ff4a85`; pull was already up to date. **01A stop 1 applies: serialized
class owners and original modifier registrations remain UNKNOWN.** This is desk
evidence and a shared-kit implementation handoff, not a completed native read.
01A stays live, its manifest row stays unstruck, and the launch residue row stays held.
The accepted train battery and soak retain their owner-scoped acceptance.

## Work and evidence

| commit-and-verify unit | state | evidence / remaining action |
|---|---|---|
| Instrument → evidence → disposition/handoff | desk committed `b1c1e32` | exact-B receipt, source assessment, negative fixture control and doccheck GREEN; stop-1 handoff below |
| Serialized ownership and native effects | held at stop 1 | validated graph decoder or suitable native reader capability, then reviewed shared-kit work under sibling authority |

MEASURED: `python docs/archive/ship_residual_20261003/read_residual_v2.py` at
`0ff4a85` plus this task's documentation/instrument diff. Its archived `receipt.json`
records command, HEAD, hashes, search scope, member offsets and source checks.
It reuses `ship_evidence_20261003/save_decode.py` with only SOURCE/OUT rebound in
memory; it reads the preserved fixture, not today's campaign slot. Decoded outputs
are in ignored scratch. The fixture hash is checked before and after reading.

- Save SHA-256: `b07a3cebc193c6eb129aa25e7e22da815cb152253f201a69282a4ae86dccd7d6`.
- Persist SHA-256: `512213c5bc0dc5c67571966c496f29b91aff20d05d2d9d3dbf9d8c8039074e14`.
- Metadata agrees with the existing receipt: GameTime `35790404`, saved toolkit
  session `1791046548:158077098:67966858:460623979`, last action id `2383`,
  internal savename `SMRTK_B.sav`. Those are saved values, not a new process identity.
- The exact-token census and offsets reproduce the prior receipt. Each of its
  hub-class, depot-class, hub-upgrade and station-row tokens occurs once. The
  command runs `rg -a -n -o` on the decoded persist member and independently
  reconciles offsets with `re.finditer`; neither result counts objects.
- Regex `\d+_upgrade\d+_mod_\d+` finds three distinct strings, each once:
  `6430_upgrade1_mod_1` at `6170151`, `6430_upgrade1_mod_2` at `6184187`,
  `6430_upgrade1_mod_3` at `6184351`. The receipt reconciles distinct/occurrence
  totals to these members. They are candidate strings, not proved registrations,
  upgrade owners, recipients or active effects.

MEASURED capability search: receipt command `rg -n
'SPCONRT|EngineLoadGame|GetLuaLoadGamePermanents' tools ../SMR-BugFixPack/tools
../SMR-BugFixPack-TestKit/Code -g '*.py' -g '*.lua'` returns no hits. Positive
controls find the native load call and permanent-table function/blacklist in
the archived game tree. This bounds the search to those tool/kit trees; it does
not establish that no decoder exists elsewhere. The source-census instrument
`tools/l3_save_footprint.py` describes write sites, not binary graph edges.
No candidate decoder with validated positive-control edges was found in that scope.

## Sourced boundaries and modifier contract

Every game citation below is from
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src`, Steam build `25579348`.
`doccheck.py --emit-fingerprint` read the installed build. The instrument compares
each cited source file's SHA-256 to the earlier pack-parity receipt; these bytes
hold. Module source hashes are in the new receipt, read at `0ff4a85`.

| claim | source and limit |
|---|---|
| SOURCE: permanent names resolve class tables | `CommonLua/Core/persist.lua:149–167`, especially `:165`. A class token does not establish a retained building instance or its owner. |
| SOURCE: Lua global save roots come from PersistableGlobals | `CommonLua/Core/persist.lua:123–147`. Runtime global enumeration is a starting point, not a native serializer schema. |
| SOURCE: map serialization transforms its input | `CommonLua/Core/map.lua:121–146` builds a selected-field table. A raw runtime map path alone does not prove that edge was serialized. |
| SOURCE: native deserialization precedes LoadGame and fixups | `CommonLua/Savegame.lua:799–814`: EngineLoadGame at `:803`, LoadGame at `:808`, FixupSavegame at `:809`, then PostLoadGame. |
| SOURCE: ordinary mod hooks cannot observe the persistence messages | `CommonLua/Modding/Mod.lua:1332–1333,1443–1453` blocks GetLuaSaveGameData/GetLuaLoadGamePermanents and PersistGatherPermanents/PersistLoad/PersistSave. No sandbox bypass is proposed. |
| SOURCE: native modifier ids derive from the buyer handle, tier and modifier index | `Lua/Buildings/Building.lua:1209–1230`. A matching byte string supplies no registration edge. |
| SOURCE: colony registration applies to current label members | `Lua/LabelContainer.lua:59–78`; `Lua/Modifiers.lua:316–327`: TurnOn sets working and the container registration; IsApplied only returns working. Both identities must be sampled. |
| SOURCE: effective numeric formula | `Lua/Modifiers.lua:41–85,90–103`: aggregate additive amount/percent, use DirectlyModifiedConstValue when applicable, then `Clamp(MulDivRound(base, percent or 100, 100) + (amount or 0), min, max)`. Do not assume base ×2 in a colony with other modifiers. |
| SOURCE: native fixup may remove a registration during load | `Lua/Buildings/Building.lua:1333–1367` removes matching generated ids not owned by buildings' upgrade maps. Execution/applicability on exact B is UNKNOWN. |
| SOURCE: Opt-In can restore a registration during load | `Code/TrainHub_20_TrainHub.lua:3627–3653,3663–3693,3776–3785`. Colony receipt owns native objects; adoption/sync can call TurnOn. Native fixups follow LoadGame, so later removal is also possible; no actual outcome is inferred. |

SOURCE intended native targets from
`Code/BuildingTemplate/SMROptInTrainHub6.generated.lua:18–43`:
CapacityNetwork adds +100 percent to Station `max_storage_per_resource`, Train
`max_shared_storage`, and Train `max_colonists_to_transport`; TrainCargo adds
+100 percent to Train `max_shared_storage`. These are additive percentage
contributions to the native aggregate, not measured values in B.

SOURCE distinctions: adoption excludes Power and StorageHub from retained native
modifier arrays (`TrainHub_20_TrainHub.lua:3684–3693`). Storage uses hub base
changes (`:3543–3550`); power output/heat uses module behavior. Cargo speed and
Power's cold handling are wrappers (`:3788–3836`), not evidence of a native
speed registration. The receipt can survive without that executable behavior.
Legacy contents of exact B remain UNKNOWN; do not assume empty modifier arrays
merely because current adoption would create them that way.

## Residual dispositions and exact disclosure

| residual | evidence status | disposition |
|---|---|---|
| `SMROptInTrainHub6Base:SMROptInTrainHub6` | MEASURED permanent token and inherited bounded B2 warning; root/owner/field-or-key UNKNOWN | Keep OI-45 demolition instruction. No harmless-reference, zero-instance or clean-save certification. |
| `SMROptInElevatorDepotDevBase:SMROptInElevatorDepotDev` | MEASURED permanent token and inherited bounded B2 warning; root/owner/field-or-key UNKNOWN | Demolish both halves; same ownership limit. |
| `UIColony.SMROptIn_hub_upgrades` | SOURCE writer/reader path; MEASURED token; binary owner edges and each saved entry UNKNOWN | Bought upgrades remain recorded by design. Native registrations, switch states, recipient identities and effects in exact B remain UNKNOWN. |
| Generated native modifier ids above | MEASURED strings only | Candidate search keys for the native slot; not a count of applied modifiers. |

Retain the existing exact player sentence:
**“Bought Train Hub upgrades remain recorded in your save after all hubs are
demolished, and their ordinary game bonuses may remain after the mod is removed.”**

Additional exact disclosure for 03's review, alongside OI-45:
**“Demolish every Train Hub and both halves of every Elevator Depot while the mod
is installed, then save, remove the mod and fully restart the game. References
to the custom building classes can remain in the save after demolition and may
produce missing-class warnings when loaded without the mod. This is not a
guarantee of clean removal; no train-building recovery is provided.”**

The existing B2 observation remains limited to its archived lines 404–481. This
desk read supplies no new load result, harmful-effect measurement or rescue
decision. No new repair is proposed and OI-45 is not reopened.

## Concrete shared-kit handoff — not preloaded or run

Recipient: shared TestKit worker under that repo's authority; launch 02 integrates
the sitting only after the implemented bindings receive the required second-seat
read. Launch 01A owns interpretation and retains the serialized-ownership hold.
This task does not grant sibling writes. Kit inspected at `b58ae18`, with
uncommitted Arboretum `Code/80_AgentSlots.lua`; preserve it until its owning work
releases the file. The contract below is the bounded runtime read to implement,
not a promise that it can discharge the serialized-ownership question.

Required missing capability for the original question: a validated parser of B's
native graph that exposes root/object/reference ids, keys, values, permanent
references and serialized metatable edges, or engine-supported equivalent
instrumentation before deserialization/resolution and LoadGame/fixups. Validate
edges against known ordinary and target-class positive controls. A wrapper around
LoadGame, a missing-permanent name logger, and a post-load raw walker do not expose
these original edges. No available reader reviewed here does so. Keep this
question UNKNOWN even if the runtime read succeeds.

Desk preparation before sibling write/launch: obtain sibling authority; check its
checklist for the shared sitting under its entrance gate; recheck kit HEAD/status
and release of Arboretum slots; review actual 70/74/75 APIs and sandbox reach;
implement and desk-test the following contract; get the independent seat's review.
Do not schedule or launch on the strength of this specification alone.

1. **Load exact residual fixture.** With the game closed, inventory/backup the
   actual save destinations and autosaves under shared-sitting authority. Stage
   a disposable byte copy of preserved B; hash it against the receipt. Never
   overwrite B or a campaign save. Prefer a dedicated filename-specific slot:
   `Savegame.Load(name, callback)` with `LoadMetadata(folder)` as the read-only
   metadata route, then compare saved GameTime/session/last_id/internal savename
   to the receipt before `LoadGame(name)` in real time. This is the current 75
   route, without LoadMetadataCallback (which calls DoneGame). Reject wrong
   metadata before load. A current A/B/C slot name alone is insufficient.
   After successful load, record build, actual enabled mods and class identities,
   saved and current toolkit sessions separately, and phase `post-load with Opt-In
   present`. Recheck this identity gate before every sampling slot; do not rely
   on a flag that survives a different load. Record rather than silently enabling
   historical dev mods from save metadata. A registry mismatch stops the read.
2. **Read residual paths.** Seed only readable enabled PersistableGlobals roots;
   record every inaccessible root. Include Maps/LoadedMaps, Cities, UIColony and
   relevant labels through their raw paths. Resolve the target class identities
   from g_Classes for comparison; do not seed that registry as evidence of a
   persisted owner, or walk class internals as though they were instance state.
   Use `next`/`rawget` on tables; never pairs metamethods, getmetatable traversal,
   arbitrary methods or object tostring. Assign local numeric node ids, a visited
   table, and a spanning-parent path; retain every incoming key/value edge even
   when its target was visited. Print root → owner id/path → key/value position
   → target id for both target classes, plus aliases. Class identity and retained
   instance identity are separate. Raw handle/class/destroyed fields and a
   validated native IsValid read may describe candidate instances; unclassifiable
   tables stay UNKNOWN rather than disappearing. Functions, threads, userdata,
   metatables and native-only edges remain explicitly opaque. Never call
   __persist to substitute its result for raw state.
   Bound nodes, edges, depth, elapsed time and output; report chosen budgets,
   consumed amounts, pending frontier ids, inaccessible roots and truncation.
   A truncated walk cannot PASS. Immediate reads need no game-time advance.
3. **Read colony upgrades and recipients.** Separate slot; same identity gate and
   phase label. Enumerate every raw entry under UIColony.SMROptIn_hub_upgrades,
   including unexpected keys. Emit key/on and each modifier's local object id,
   upgrade_id/id, container identity/path, label, prop, amount, percent, working
   and check_if_prop_exists. Correlate object identity against colony and city
   label_modifiers, not string equality alone; print matching and conflicting
   registrations and every relevant label recipient. For ordinary Stations read
   raw base_max_storage_per_resource, max_storage_per_resource and the entire
   modifications record including member identities/amount/percent/min/max.
   Do the corresponding Train cargo/passenger fields to cover all native targets.
   Inherited/default/unreadable values remain distinguished from raw values;
   use separately sourced defaults only when their applicability is established.
   Compare aggregate arithmetic to the archived formula above, including other
   modifiers and direct-constant overrides. No setters, TurnOn/Off, upgrade
   toggles, cargo movement, save or cleanup calls. A mismatch is evidence, not
   permission to repair. Original persisted registrations and after-removal
   effects remain UNKNOWN regardless of this post-load comparison.
4. **Flush and preserve.** MARK → read → auxiliary DUMP → MARK via ctx helpers;
   callbacks return fields or `false, reason`. Current 70 dispatch uses OK,
   REFUSED and ERROR: OK means callback completed, never ownership PASS. Bindings
   must expose named result fields for completion, identity, controls and limits.
   Preserve the complete flushed boot log, not a possibly truncated ring copy,
   plus fixture/binding hashes and process identity. Finish normal taint and
   eligibility reads; no new clean-eligibility promise. Do not save the fixture.

Desk controls before review: an isolated cyclic graph with target tables as both
keys and values, shared aliases, destroyed/invalid candidate nodes, a known
ordinary Station owner, and hostile __pairs/__index/__tostring traps; the walker
must find the expected raw edges without firing traps or changing the graph.
Remove a target edge and verify the output changes; lower each traversal/output
budget and require non-PASS plus frontier evidence. Wrong metadata must refuse
before load. At runtime, the known ordinary live Station must be found through
its actual colony/map label owner and target-class references must be found before
any absence claim. Failure to find a target is an insufficient reader, not proof
of absence. The second seat fills exact binding numbers, verbs, predictions and
bounded runtime expectations from the implemented source before any sitting.

## Drift and close-out

The first instrument (`read_residual.py`, preserved) wrongly assumed persist
started with literal SPCONRT and named its metadata member metadata.lua. It
stopped at its format assertion after decoding and hash checks, before a receipt.
The corrected v2 records the actual `mgvs` prefix and reads savegame_metadata.
Its `rg -a -o SPCONRT` over decoded persist returns no matches; the named residual
tokens are positive controls. The brief's SPCONRT description is unverified as a
format name, not a reason to reject this hash-identical fixture. No guessed tag
layout or token-adjacency ownership is used. A source-locator typo was corrected
before using its Building.lua citations.

Additional routed drift: OI-50 still asks a settled question in the checklist,
and 02's first prerequisite still treats it as open. Chain README and commits
`7f9c0e6`/`0ff4a85` already carry the owner's post-launch D19 ruling; use that
authority, never ask again. These shared scope records are left to their owning
launch/package work. STATE's historical train/build assertions are likewise not
substitutes for this task's command-read fingerprint and accepted battery record.

Execution: Codex, GPT-6 (the only executed-model identity exposed by this
transcript; no finer model id is available). No subagents, independent audit,
game launch, sibling write or campaign-save change occurred. 04 still requires
the owner's different-model independent audit. Session-close skill applies to
these records; all findings are homed here and passed to 02/03/04. No obligation
or original brief is removed. Completion checks and commit are recorded by the
owning report's live work row and the commit message.

Checks: `python scratch/residual_checks.py` rejects a changed fixture before
decoding, verifies the archived reader hash, and reconciles receipt totals.
Its source/output are preserved as `archive/ship_residual_20261003/checks.py`
and `checks.json`. The same command measured this handoff's raw bytes against
`0ff4a85`: exact 01A/02/03/04 member paths and before/after values are in that
receipt. `python tools/doccheck.py` GREEN and `git diff --check` clean before
commit. Expected frozen-row warnings, existing archive EOL warnings and the
shared kit's uncommitted Arboretum slots remain report-only. No Lua was changed.

The close-out records commit pins `b1c1e32` in downstream notes; final handoff
byte measurements are appended as `archive/ship_residual_20261003/final_sizes.json`,
using the same command/filter/base as checks.json. No brief or obligation was
removed. Next work is the shared-kit capability/implementation handoff above;
this is not authority to start launch 02 or to treat the residue hold as cleared.
