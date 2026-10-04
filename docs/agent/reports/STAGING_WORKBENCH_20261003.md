# Staging workbench — 2026-10-03

Owner scope: a dev-only sibling mod for modules in progress, kept out of the
production package, with one promotion tool. Starting HEAD `cc121b3`; pull was
already up to date. The Arboretum's registration edits in `metadata.lua` and
`items.lua` were present in the shared working tree. Its code, generated template
and tooling were already committed; this change moves them into `staging/`.
The release correction session owns its separate release-tooling changes.

## Design and save contract

`staging/metadata.lua` declares `SMR_CommunityOptInPack_Workbench`, visibly titled
DEV ONLY, with a required dependency on `SMR_CommunityOptInPack`. Production's
`ignore_files` excludes `*/staging/*`; the workbench's own exclusion is `*`.
The installed local junction is `Mods/SMR-OptInPack-Workbench` → this repo's
`staging/`. It is never an upload source.

The bridge extends the production ModDef instance's `GetOptionItems` at runtime.
It does not add any item to production's editor list. Native options therefore
render on the Opt-In page and save under `AccountStorage.ModOptions.SMR_CommunityOptInPack`.
The workbench's own options page is hidden. Both environments read the production
option object. Absent values receive the staged defaults; existing values remain.
The bridge clears native option caches after item load and detaches before a mod
reload; direct Lua reload first detaches the previous bridge.

No production core or shipping-module behavior was changed. Arboretum's module
body is moved unchanged. The generator changes only output location, its command
banner and the editor preset's `SaveIn` ModDef id. Class, template, parent,
service category, option and permanent names remain those in FIX_POLICY rows 32–33.
The native saved mod list can retain the workbench id and show a missing-mod
warning after promotion; this tool does not suppress that warning. A real colony
save/promotion/load and D19 gameplay acceptance remain unmeasured.

SOURCE evidence: archived build **1.1.1.406343**, Steam **25579348**, under
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/CommonLua/Modding/Mod.lua`.
Read with `rg -n` and scoped source slices; installed fingerprint was emitted by
`python tools/doccheck.py --emit-fingerprint` at `25f38d5` plus this working diff.

| mechanism | archived source | implication |
|---|---|---|
| Dependency traversal | `:1907`, `:1954`, `:1974`, `:2285` | Dependency is visited before the dependent is queued; code follows that queue. |
| Option loading | `:680`, `:2157` | Account values, including keys outside defaults, are loaded before code. |
| Native option metadata | `:479`, `:2647` | Rendering gets option items from the owning ModDef; cache invalidation exposes the staged items. |
| Apply and account write | `:753` | The page posts the production id and stores values under that id. |
| Editor defaults | `:463` | SaveDef's defaults come from the editor items, which the bridge never changes. |
| Reload cleanup | `:2116`, `:2190` | ModsReloading precedes unloading; ModItemsLoaded follows all item loads. |

## Tools and limits

`tools/promote_module.py <name> --check` reads `staging/modules.json`, validates
the workbench and prints the exact move/edit plan. Without `--check` it transfers
owned files, code list entries, option defaults and editor items; runs declared
generators and the workbench, Lua parse and doccheck gates; and restores the
reviewed move/edit set on failure. Existing destinations and editor handles refuse
before writing. It does not commit, publish, or settle an owner's ship decision.
Custom imported model promotion is refused until a shared ArtSpec/entities merge
route is implemented. Current support is owned Code/Data/tools/UI files.

Doccheck's WORKBENCH gate reconciles files, code lists, editor items, manifest
ownership and options, rejects a duplicate module or option across mods, requires
the native dependency, parses staging Lua and proves package exclusion with a
positive witness. Its selftest exercises broken guards and failed-gate rollback.
The tool catalog is generated from these scripts' headers. WORKFLOW routes module
builders to the workbench README and promotion command; no new memory-only rule
was added (rule-placement result: a guard and a task-specific procedure).

## Verification

MEASURED at `25f38d5` plus this workbench diff, on game **1.1.1.406343**:

- `python tools/workbench/read_boots.py` verifies the four completed `*_clean.log`
  members in `docs/archive/workbench_20261003/verification_receipt.json`. Required witnesses
  cover real dependency ordering, native option metadata, class/template identity,
  cold state and live OFF/ON reconciliation with the fix pack present and absent.
  The final boot confirms the original saved and loaded mod order and that production
  alone has neither the Arboretum registry entry nor its template. Every accepted log
  has zero matches for the receipt's fatal-error filter. The deliberate false check
  fails before the positive checks, proving that the instrument can reject a condition.
- Whole-log filter `error|assert|exception|fail|warning` produces seven lines in each
  accepted log: the successful AcknowledgedWarnings module name plus two sets of Braze
  SessionStart DNS, launcher-event and initialization failures. Those startup network
  failures also occur in the production-only controls. Exact lines and members are
  in the receipt; no unexplained Lua errors remain in the accepted runs. The receipt
  includes LF-normalized hashes for Git's text checkout convention as well as raw
  log hashes. The earlier `boot_receipt.json` retains the original raw reading.
- `python tools/workbench_selftest.py`: thirteen named controls pass, including
  read-only planning, failed-gate rollback, duplicate registration, package leakage,
  dependency loss, unsafe paths, option defaults and bridge reload/detach.
- `python tools/promote_module.py WorkbenchPromotionProbe --check` and the same command
  without `--check` ran against a throwaway module in this tree. The real promotion
  passed its workbench, Lua parse and full doccheck gates, then the fixture was removed
  and every touched list restored byte-for-byte. Commands, full output and before/after
  hashes are in `docs/archive/workbench_20261003/promotion_roundtrip.json`.
- `python tools/pack_predict.py . --json`, filtered for `staging/` or `Arboretum`,
  has zero leaked members. `python tools/workbench.py` separately reconciles the
  excluded staging files against its manifest and requires the metadata/bootstrap
  exclusion witnesses. Pack members and filter are in `pack_receipt.json` beside the logs.
- `python staging/tools/arboretum/generate.py --check` passes; its deskcheck passes
  native debit/empty/restart and building-lock controls. Comparison with `git show
  25f38d5:Code/Opt_Arboretum.lua` proves the module body unchanged (SHA-256
  `4214c5d636575247d8ac5867780cf55b5d3f36a05971893e1fad89ea37711219`); the generated
  runtime class differs only in its generation-command banner.
- `python tools/doccheck.py` is GREEN after the fixture restore and probe disarm.

The boots were armed with `python tools/workbench/prepare_boot.py <step>` and the
fix pack's `tools/arm_leg.ps1 -Manifest scratch/workbench_boot/leg.json -Mode arm`;
each fresh retail process exited before its log was copied. `-Mode disarm` restored
the TestKit metadata and removed the temporary payload. Its pre-existing AgentSlots
edit was untouched. RAM option flips were restored. The workbench junction remains
installed, but the original enabled mods are restored; enable the DEV ONLY workbench
and restart for local work. No colony was loaded or saved by these tests. D19's owner
asks and attended gameplay task remain unchanged; its brief and report stay with
the build session. This evidence does not establish placement, visitors, throughput
or a real saved-colony promotion.

Failed attempts are retained under `docs/archive/workbench_20261003/`:
`attempt1_setup.log` caught an assigned `assert()` rejected by the retail loader;
`attempt2_setup.log` was stopped before testing to replace assertions with explicit
failing checks. `present.log` and `attempt_absent.log` rejected an overstrict
saved-order assumption: the fix pack's `01_LoadFirst.lua` puts itself first.
`attempt_warning.log` caught a probe formatting error on a zero-return warning
method. `present_pass.log` and `absent_pass.log` are **rejected**, despite their
internal result lines: firing the native building-lock message at the menu caused
map-state errors in Station and BuildMenu handlers. Whole-log review caught them.
The final menu probe omits that map-only message; the unchanged Arboretum desk
test covers its own lock handler. `restored.log` belongs to that rejected matrix.

Executed model recorded from this transcript: **GPT-6 (Codex)**; no more specific
model identifier or effort was exposed to this session. No subagents were used.
