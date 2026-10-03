# Launch-prep audit — 2026-10-02

The launch still owes its release system, shipping evidence, player surfaces and the owner's
portal work. This report is an inventory and work assignment, not a readiness verdict.
Authority: the owner's 2026-10-02 launch-prep request in the consumed
`LAUNCH_PREP_AUDIT_high.md` (readable at `63424af:docs/agent/prompts/LAUNCH_PREP_AUDIT_high.md`).
Scope: this repo, the fix pack's release system and the shared site's local tree. No code,
metadata, store copy or sibling-repo edits were made by this audit; no game or upload was run.

## Work list

- Complete: inspect the release obligations and sources, run the desk gates, and assign every
  finding below; author/revise the briefs and checklist questions as one commit-and-verify unit.
- Follow-up execution belongs to the briefs below. Their completion is not this audit's claim.

## Evidence receipt

All local readings below were made at Opt-In HEAD `63424af`; startup `git log --oneline -5`
and `git pull` reported up to date. `git status --short` was empty. The fix pack was at
`a565a34`, with ` M docs/agent/reports/RULE_PLACEMENT_TEST.md`; the site was at `fd31bcf`,
with **empty** `git status --short`. Commands: `git -C <repo> log --oneline -3` and
`git -C <repo> status --short`. The historical warning about dirty site edits is not today's
reading; every future writer still reads status before writing.

| class | command / filter, run at that HEAD | result and limit |
|---|---|---|
| MEASURED | `python tools/doccheck.py --emit-counts`; membership control `rg -n 'Register\(' Code -g 'Opt_*.lua'` | GREEN; 7 registered modules = D02 AcknowledgedWarnings + D04 MultipleSuns + D09 DroneStatDials + D15 ServiceInterestTags + D16 StationRows + D17 TrainHub + D18 ElevatorDepot. D09 is the default-active reconciler at base; the other 6 are optional-gated. D05 is the enable surface, not another module. |
| MEASURED | `python tools/doccheck.py --emit-fingerprint` | Installed build **25579348**, archive **1.1.1.406343**. Older fact groups MOVED; the STATE sentence naming 1.1.0 is not the installed-build reading. |
| MEASURED | `python tools/upload_preflight.py` | **1 FAIL:** missing `image`; **1 UNCHECKABLE:** Paradox login. The train asset, generated-code order, code-list and pack guards pass. No screenshots declared. This is local validation, not portal acceptance. |
| MEASURED | `python tools/pack_predict.py .` | 74 packed files = root 3 + Code 19 + Data 2 + Entities 5 + Fallbacks 17 + Materials 4 + Meshes 5 + Textures 17 + UI 2. Raw total **102,571,766 bytes** = **520,287** non-asset + **102,051,479** asset bytes. Asset members are the last six directory groups, 50 files. This is not compressed upload size. |
| MEASURED | same preflight and doccheck `PACK IGNORE PARITY` | 16 ordered ignore filters agree; no packable junction; the SourceData source is excluded from the package but remains available to the editor. OI-18's asset exemption works; do not reinstate the old whole-pack 5 MB limit. |
| SOURCE | `Get-Content metadata.lua`; `rg -n 'Register\(' Code -g 'Opt_*.lua'` | Approved description names trains and uninstall steps, but omits D15 Service Interest Tags. Short description is current. `last_changes` still says the modules were split out; no preview, gallery fields or portal ids. `optional_mod` is true; tags Gameplay and Buildings are set. |
| SOURCE | `Get-Content docs/agent/bugs/INDEX.md` after doccheck regenerated it in memory | D02/D04/D09/D05 retain legacy `tested`; D15 is `tested-attended`; D16–D18 are `built`; D14 remains `open`. Status alone does not certify a shipping build. |

`README.md` is also stale: it advertises retired modules and lacks trains, D15 and the current
content-removal caveat. Check with `Get-Content README.md`, against the emitted membership above.
The existing OI-14 text's old string count is not a launch inventory: the command
`rg -n 'Untranslated\(' Code -g '*.lua' | Measure-Object` returned **31 matching lines**,
not a count of unique strings. The localisation decision covers the actual shipping set.

## Fire order and owners

1. **First launch-prep brief: `task docs/agent/prompts/RELEASE_SYSTEM_high.md`.** Revised in this
   audit, not fired. Build the local release machinery now; its named gaps may remain explicit.
2. **Train prerequisite:** `Train_Hub_Project/35_FINAL_BATTERY_high.md` owns the final train
   battery, D14 residue, OI-38 and the train D-entry verdicts. It was ready at this audit HEAD.
   Launch waits for its durable close-out; no launch brief repeats that battery. If its folder
   has disappeared, recover the deletion commit's report, not a dead path.
3. **`Launch_Prep/01_SHIP_EVIDENCE_high.md`:** after 35, reconcile source/build coverage,
   the remaining modules' evidence, uninstall/rescue applicability, credits and owner rulings;
   finish the bounded attended test plan. No new sitting before this preparation.
4. **`Launch_Prep/02_SHIP_TESTS_medium.md`:** owner-attended tests for gaps left by 01, with
   an independent read of the attended plan before the owner sits. Existing accepted evidence
   stays accepted within its conditions.
5. **`Launch_Prep/03_STORE_AND_SITE_medium.md`:** approved copy and art, both store paste
   surfaces, shared site integration, tooling and final package preparation. It may prepare
   independent drafts earlier, but final claims wait for evidence and the owner's decisions.
6. **`Launch_Prep/04_FINAL_AUDIT_high.md`:** fresh-context adversarial review of the whole
   launch preparation, including the release-system job. Then the owner fires the permanent
   `perma/release_prompt.md` to prepare the actual upload, hand off, hold and close it.

The owner starts the chain by hand and chooses distinct execution/audit models for unattended
work. The chain empties when prep is complete and all remaining owner upload obligations have
live homes in the release system; publication itself is not a chain side effect.

## Release-system comparison

The donor inputs read were `docs/UPLOAD_WORKFLOW.md`, `prompts/perma/release_prompt.md`,
`RELEASE_OUTBOX.md`, and support `RELEASE_SURFACES.md`, `POST_UPLOAD_CLOSE.md`, `LIVE_SITE_READ.md`
under `B:/Dev/SMR/SMR-BugFixPack/docs/`. This repo still has the old WORKFLOW release paragraphs
and the unfired system-build brief. File inventory command: `rg --files docs tools`, compared
with the explicitly named destinations in `RELEASE_SYSTEM_high.md`.

**Disposition: revise `RELEASE_SYSTEM_high.md`, retaining its name.** Its 2026-09-18 authority
to standardise on the donor, owner workflow and destination names still applies. Its module
description, no-`last_changes` assertion, old packaging assumptions and update-only examples
do not. The revision gives first publish and later updates separate paths, and assigns actual
store/site production to chain 03.

| surface | exists / gap | owed to |
|---|---|---|
| Owner upload workflow | Donor procedure exists; local one absent. Needs first creation, portal login/ids, preview/gallery, tags, formatting backups, console steps and resumable receipt. | RELEASE_SYSTEM builds it; 03 fills it; owner uploads. |
| Permanent release prompt | Donor has derive → prepare → owner HOLD → verify writeback → archive outbox. Local prompt absent. | RELEASE_SYSTEM, then terminal QA. |
| Outbox and history | Need local Pending ledger with a first-publish batch, not a fabricated previous release; empty historical ledger is honest. | RELEASE_SYSTEM; only confirmed upload drains Pending. |
| Support docs and gates | Same donor names; local maps, ROOT allowlist, required rule headers, prompt map/outbox class, WORKFLOW and sync citation exemptions need wiring. | RELEASE_SYSTEM; doccheck. |
| Store-card maintained copies | Donor `STORE_CARD_LIVE.md` shape useful, but there is no live Opt-In card. | RELEASE_SYSTEM defines draft state/parity; 03 creates first-publish copies, then close-out records actual publication. |
| Post-upload recovery | Editor can rewrite metadata/items and strip comments; first creation assigns ids. | Local POST_UPLOAD_CLOSE preserves writeback, restores comments, reconciles downloaded package and records exact bytes/tag. |
| Cross-repo release | Site pages and shared nav/front page can collide with a fix-pack release. | Local release procedure checks status/HEAD, merges only its paths/hunks, and rechecks before commit; owner alone deploys. |

**Copy conflicts to expose, not silently inherit:** the donor's `fixpack-v1.0.0` tag, store ids,
repair counts and load-first claim are that product's, not this one's. Its save-removal promise
does not describe placed hubs/depots. Any runtime helper carrying executable `SMRFixPack`
references would violate this repo's header ban; none of the reviewed prose procedures requires
such a helper. Persisted `SMRFixPack_*` strings remain unchanged. The local WORKFLOW still says
agents change major/minor, whereas the current donor forbids hand-setting all version fields;
the system builder must reconcile that text under the owner's standardisation authority,
preserving the decided initial major/minor and editor-owned writeback. Do not reset versions
or borrow the donor tag. The donor's surface support also calls backups the delivery path,
while its owner workflow records settled auto-fill with formatting loss: preserve the owner's
settled observation and maintained paste backups without asking that question again.

## Shared site

SOURCE at site `fd31bcf`: `Get-Content mkdocs.yml` and `README.md`; `rg --files content`;
`rg -n 'opt-in|GITHUB_REPO' content/report.md worker/src/index.js worker/wrangler.toml`.
The nav and README mods table describe the fix pack, with no Opt-In module pages. The report
form **already offers Opt-In Modules** and the worker labels it `opt-in`, filing into
`catt144/SMR-CommunityMods`. Preserve that existing route; no new reporting service is owed.
No form submission was made and no deployment freshness is claimed.

Chain 03 owns module pages, an Opt-In landing/module index, nav, README table and the public
mod repo README. It also owns a scoped sweep of `content/index.md`, `install.md`, `faq.md`,
`for-modders.md`, `report.md` and `mkdocs.yml`'s site description: a fix-pack-only removal or
load-order instruction cannot become a family-wide promise. In particular the report form's
"disable every mod" troubleshooting needs a safe content-mod path with a backed-up save.
Keep existing fix-pack URLs stable; a dedicated `content/opt-in/` section is the recommended
layout, delegated to the writer. No owner site choice blocks this layout.

The donor `PARKED_OPTIN_REFERENCES.md` is a **publish-day checklist**, not copy to restore
verbatim: it contains retired-module text, nonexistent-link placeholders, and a no-longer-valid
stand-down promise. Its fix-pack metadata/store edits require that repo's release and owner
upload. Chain 03 prepares an exact donor-side handoff without editing the fix pack. The local
release system owns executing/routing the restoration at first publication, never early.
Site content commits remain undeployed until the owner runs the existing manual workflow.

## Storefront and upload ledger

The donor publishes to **Paradox Mods and Steam Workshop** (its UPLOAD_WORKFLOW §2).
Console distribution is the Paradox path, not a third Steam listing. Local title, id and author
already identify this separate product. Never copy donor portal ids or require the fix pack.

| item | exists / gap | owner / decision |
|---|---|---|
| Description | OI-42 approved metadata body includes trains, standalone operation and uninstall actions; D15 is absent. Donor `STORE_OPTIN.md`, `RELEASE_DESCRIPTION_OPTIN.md`, `STORE_METADATA_STRINGS.md` are historical leads, not approved replacements. | 03 adds complete module coverage to maintained store/site copy while preserving OI-42 meaning; any substantive new owner choice is filed before changing it. |
| Short description | Approved current metadata text. | 03 copies/checks it; no reopening. |
| Preview | No `image` field; local preflight fails. | OI-12 owner art choice; 03 prepares candidate/files and adds the selected asset. |
| Screenshots | None declared, locally allowed but no Opt-In gallery prepared. Train icons are not store screenshots. | OI-12 owner selects captures/gallery; 03 prepares upload files and excludes gallery-only sources from the mod package. |
| Tags | Gameplay and Buildings already true. | 03 verifies current portal choices and consistency; no request to redesign tags. |
| Changelog | Split-era first-release sentence exists. | 03 and release prompt replace it with the actual first-publish scope; no unreleased development-fix history advertised. |
| Store tools | Donor tools are hard-wired: `paradox_card.py` resolves its own repo's UPLOAD_WORKFLOW; `store_screenshots.py` has fix-pack capture paths and gallery map. Running them from a different cwd does not select Opt-In. | OI-21: recommend port here. Running donor copies would need explicit parameterisation/authority there. |
| Store creation and ids | No local ids; account state uncheckable. | OI-44 owner uses existing Opt-In drafts if any, otherwise creates first listings; record assigned ids from writeback. No credentials in git. |
| Portal formatting | Donor observation: description auto-fills, styling does not. Steam BBCode and Paradox formatted paste backups must remain current. | RELEASE_SYSTEM/03 prepare; owner pastes after upload. |
| Console/platform approval | No Opt-In approval receipt reviewed. Fix-pack approval does not transfer to this product. | OI-44 owner confirms actual Paradox platform selection/approval flow and receipts; workflow records owed versus confirmed. |
| Package | OI-18 asset guards pass. Ignore parity holds. README/tools/docs/SourceData remain excluded; LICENSE and required templates/models ship. | 03 reruns preflight after art/gallery edits, release reruns on final tree; owner pack/upload, then `pack_list.py <downloaded ModContent.fpk> --tree .`. |
| Version, tag, release receipts | Initial major/minor already 1/0; patch 0. No Opt-In publication receipt. | Editor owns generated writeback; release system records archive/tree differences for each portal, exact tag/sha, Steam changelog and owner receipt, not matching storefront counters. |

External check, 2026-10-02: Valve's
[Workshop implementation guide](https://partner.steamgames.com/doc/features/workshop/implementation#Legal)
states that a new item gets an assigned id and can remain hidden pending the contributor's
Workshop agreement. Treat that as a first-publish owner check, not evidence that this account
still owes acceptance. The Paradox modding diary fetch was restricted; no current console
certification procedure or server-side text cap was verified from it. Current portal checks
therefore remain in OI-44/the upload procedure. The preflight's image-size checks are local
guard evidence; they are not a claim about every current server-side limit.

## `optional_mod` decision — OI-43

SOURCE re-derived from the archived **1.1.1.406343 / build 25579348** tree, not the live Src:
`B:/Dev/SMR/SMR-Shared/SMR-SrcArchive/1.1.1.406343/Src/CommonLua/SavegameMetadata.lua`.
Command: `rg -n -C 4 'optional_mod|optional =|active_mods' <that file>`.
`GetLoadedModsSavegameData` lines 11–30 copies `optional = mod.optional_mod` into the save;
`GetMissingMods` lines 94–104 suppresses the warning when either installed definition or saved
entry is optional; validation calls it at lines 344–350. This is SOURCE, not an observed dialog.

| option | consequence / evidence | recommendation |
|---|---|---|
| Set false before first publish | New saves written with the enabled mod no longer suppress the engine's missing/disabled/outdated warning. It warns for this whole mod, even if the player never built content. It does not repair a save or make removal safe. | **Recommended:** placed hubs/depots make silent removal an unsuitable default. Keep the explicit uninstall procedure too. |
| Keep true | Maintains quiet removal for behaviour-only users, but removes the missing-mod warning for users with placed content as well. Relies on the player reading and performing the uninstall steps. | Owner can accept that tradeoff under §0; no agent change implied. |
| Make optionality conditional on save content | Could distinguish behaviour-only saves, but the current field is ModDef-wide and the saved flag persists. Needs a new design/ruling and measured save-metadata behaviour. | Not necessary for launch; no speculative implementation brief. |

Existing dev saves with `optional=true` can still suppress the warning after a metadata change:
the boolean expression falls back to the saved value. Loading and saving with the changed,
enabled mod replaces its entry; saving while it is absent does not. An approved flag change
needs a bounded new-save/old-save control, including full process restart for disable/removal.
The warning cannot replace §3/§0 residual disclosure or the save-rescue assessment.

## Shipping evidence and every open owner item

| obligation | done / owed and next owner |
|---|---|
| Train final build, toggles, both configurations | **Owed, brief 35.** Its outcome must name the released fix-pack version and shipping layout; includes OI-38's scripted up-leg, quiet logging and D14 gaps. 01 imports its exact result and limits. |
| D02 and D04 shipping tests | **Owed, 01 → 02.** Entries' 2026-09-22 repairs were desk-verified; D02's routed-warning falsifiers and D04's two-sun demolition remain unrun in their entries. |
| D09 / D05 | **Owed coverage review, 01 → 02.** Legacy test labels are not proof on the current shipping build. Include base/on/off, stale-save dial cleanup and actual Mod Options enable path where evidence is missing. |
| D15 | **Accepted evidence exists**, entry's 2026-09-30 sitting and explicit owner rulings settle both configurations, enable path and bounded uninstall leg. 01 checks changes against those conditions; no automatic repeat merely because STATE is stale. A future persisted-state change reopens uninstall; fix-pack changes on named surfaces reopen that half. |
| `Packs/Lua.fpk` and shipping build | **Owed, 01.** Fingerprint build alone is not body verification. Consume pending `perma/gamepatch/1.1.1.405907_2026-09-23.md`, close applicable changed targets against decoded shipping packs and archived Src, and cover train targets not in that old module set. Record file/body digests and build. |
| D-entry status | **Owed, 35/02.** Update only from evidence, including attendance; D14 subcases need dispositions, not a blanket promotion of its open label. Retired/parked entries remain history. |
| Credits and assets | LICENSE ships and names game-derived portions. WORKFLOW names ChoGGi and LukeH as prior-art leads. **Owed, 01/03:** verify relevant provenance (including model/texture sources), preserve licenses and put applicable credits in player-facing surfaces. No assumption that a generic notice proves every asset's provenance. |
| Standalone / separate product | Identity and own asset paths pass local checks. **Owed, 35/02/03/release:** both configurations, own preview/listings and console receipt, no dependency or load-order instruction. |
| Player text / quiet logs | OI-42 approved metadata; 5ad1ff3 quieted development logging. **Owed checks:** 35 quiet-log control; 03 vanilla-style text parity, all shipping modules, content persistence, achievement/platform disclosure and safe uninstall steps. |
| Save exit and rescue | **Owed applicability proof, 01 then 02.** §3 and WORKFLOW require the exit and applicable shared D13 rescue ready against the final residual set. Donor uninstall assembly is a dial-era lead; it does not establish hub/depot rescue. Do not promise a recovery tool exists for trains. If the existing rescue cannot cover measured residue, file a concrete owner decision/implementation dependency; prep cannot erase this duty. No rescue repo edits in this audit or chain. |
| OI-21 store tools | Open; owner says port here or run donor route. Recommendation and actual hard-coded constraints above; RELEASE_SYSTEM can build placeholders, 03 executes the ruling. |
| OI-14 localisation | Open owner scope decision; 01 records ruling in FIX_POLICY and scopes any resulting build before shipping tests. Do not silently impose the donor's translations on this mod. |
| OI-13 comments | Open owner sweep/keep choice; 01 locates surviving sites (the parked D03 file no longer ships), applies only a granted comments-only sweep and parse-checks it. |
| OI-11 MultipleSuns Require | Open owner choice; its old “frozen” justification is stale under 2026-09-18 authority. D04 has since been edited. 01 rechecks the allowlist/capture and routes or implements the owner's ruling; do not turn the stale wording into a new freeze. |
| OI-12 preview / gallery | Open; 03 prepares, owner selects, final preflight must pass. |
| OI-38 | Open owner test; 35 owns it, not a second launch sitting. |
| OI-43 optional flag | New owner decision, evidence above; 01 records ruling, applies only if approved, 02 owns needed control. |
| OI-44 first listings / console | New owner-only facts/actions; RELEASE_SYSTEM carries explicit first-publish placeholders and 03/release resolve them. |

No additional owner question is needed to choose a page layout, inspect credits, reconcile old
source readings or write the release system. A new behaviour change found during verification
still requires the recorded ruling; route it to a build brief and rerun affected evidence only.

## Limits and close-out

No public site deployment, private portal state or console certification was inferred from the
local trees. No full shipping battery or `Lua.fpk` target verification was performed here.
This audit's gate result is doccheck GREEN; upload preflight remains red on preview art.
The existing archive EOL warnings are not rewritten: `log_receipt.json` under
`train_34b_sitting2_20261002`, and `lifecycle.json`, `log_receipts.json`, `smokes.json` under
`train_audit_20261002`, are whole-CRLF files.

Executed model: **gpt-6-astra**, read from `turn_context.payload.model` in
`C:/Users/stkot/.codex/sessions/2026/10/02/rollout-2026-10-02T21-55-54-01a0ff79-99b8-75a3-8414-a4d844d37ac0.jsonl`.
Verification: Python JSONL scan matched this audit's user task in a `response_item` and emitted
the model set from that transcript's `turn_context` records. No subagents were launched. Skills:
smr-orientation, doc-editing, prompt-authoring, rule-placement, smr-bug-library and smr-session-close.
