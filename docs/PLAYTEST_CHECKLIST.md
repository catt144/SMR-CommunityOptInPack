# Playtest checklist — the owner's list

## Must_Read_Header
<!-- RULES -->
Rule: Admit an item only when its next action is the owner's: a ruling in words, or a test only the owner can run. [A3: pass]
Rule: Write each item as `### OI-<n> · opened <date>`, its ask, at most six bullet lines and a `Home:` line. [A3: pass]
Rule: Never change an item's opened date; at 30 days old it is purged or archived, however recently it was touched, unless its heading ends ` · launch`, which marks a launch obligation. [A3: pass]
Rule: Delete an item in the commit that records the owner's action on it. [A3: pass]
<!-- /RULES -->

What waits on your word or your hands for the opt-in mod, and nothing else. doccheck enforces the
format and the age. Ids are `OI-<n>` so they never collide with the fix pack's `ck<n>`; what binds
the fix pack goes on its own checklist. A launch obligation waits for this mod's launch, which is
unscheduled, so it does not age.

## Decide

### OI-27 · opened 2026-09-24
When a rail shaft connects the hub to another map, should hub drones stop at the shaft?
- The graph enrolls far-map stations, but a Wasp's stock flight stays on its own map.
- Recommend restricting drone work to the hub's map, retaining ordinary same-map tunnels.
- Alternatively, keep that combined fixture parked until cross-map service is designed.
- The audit did not add a map restriction to your network-wide service rule.
Home: `docs/agent/reports/TRAIN_HUB_AUDIT_111_20260923.md`, `docs/agent/bugs/D14.md`

### OI-21 · opened 2026-09-19 · launch
When this mod publishes, do its store tools come from the fix pack or get ported here?
- `paradox_card.py` and `store_screenshots.py` are declared not ported; this mod is unpublished (`metadata.lua` v0).
- The fix pack holds this mod's listing drafts: `RELEASE_DESCRIPTION_OPTIN.md`, `STORE_OPTIN.md`,
  and the opt-in strings in `STORE_METADATA_STRINGS.md`; recheck all at launch.
- Say "run from the fix pack" or "port at launch".
Home: `docs/agent/prompts/RELEASE_SYSTEM_high.md`

### OI-14 · opened 2026-09-18 · launch
Does your 2026-08-02 ruling that the fix pack ships its own `ModItemLocTable` translations extend to this mod?
- This mod's `Code/` has 10 `Untranslated(` sites: rollover titles, policy rows, the stand-down dialog.
- `FUTURE_IDEAS.md` #4(b) hangs on the answer.
- Say "both", "fix pack only", or "decide at its launch".
Home: `docs/agent/FIX_POLICY.md`

### OI-13 · opened 2026-09-18 · launch
May an agent sweep four `Code/` comments that still call this mod "the pack", comments only?
- `00_Core.lua:497`, `:536`, `:558` and `Opt_ResidencyControl.lua:63`, re-read on 2026-09-18.
- Zero behaviour change and a parse sweep after, but it edits module files, so it is yours.
- Say "sweep" or "leave as history".
Home: `docs/agent/WORKFLOW.md`

### OI-11 · opened 2026-09-18 · launch
Name `Opt_MultipleSuns`'s `SolarPanelBase.GameInit` capture in its `Require` block, or leave it allowlisted?
- The F107 wrap check allowlists it: the class declares the method, so `prev` is real and nothing is broken.
- Naming it is a code edit to a frozen module and needs an A/B. D06's two sites left with that module.
- (a) leave it until the file's next planned edit — OI-04 (a) would be one; (b) do it at the launch session.
- Recommended: (a).
Home: `docs/agent/FIX_POLICY.md`, `docs/agent/bugs/D04.md`

### OI-18 · opened 2026-09-18
Train hub: widen `tools/upload_preflight.py` so the hub's template and model can ship in this mod (your OI-16 = 4b)?
- `:188-196` admits only `Code/*.lua`, `metadata.lua`, `items.lua`, `LICENSE` and the preview image.
- That refuses `Data/BuildingTemplate/*.lua` and any entity folder; `:203-211` lists `Code/` non-recursively too.
- It does not block the sitting or the model import test: the dev mod carries both.
- Ruled 2026-09-21: the 5 MB guard is the fix pack's and does not bind this mod, so it is no size ceiling here.
- Untested: the dev mod loads UNPACKED; nothing proven PACKED, and no `FIX_POLICY` §8 run for the hub.
- Say "widen it" (an agent edits the tool) or "keep the hub a separate mod".
Home: `docs/agent/reports/TRAIN_HUB_BUILD_20260918.md`

### OI-19 · opened 2026-09-18
Train hub: accept the remaining economic/module-off defaults, or name changes?
- Module off: no new hubs, built hubs keep working (as MultipleSuns). Removing the mod with hubs standing is unsafe.
- Cost 60 Concrete, 40 Metals, 10 Machine Parts and 15 Electronics.
- Maintenance is 2 Electronics; the reserve is two maintenances, 4 Electronics, which trains and drones leave alone.
- Radius 15 and the drones were separately ruled; storage is 240 per resource, stacks drawn to 150 (2026-09-25).
- Say "accept" or name changes to the module-off rule, cost, maintenance or reserve.
Home: `docs/agent/reports/TRAIN_HUB_BUILD_20260918.md`

## Run

### OI-29 · opened 2026-09-25
When you next open the hub dev mod in MarsDebug's Mod Editor, let the load log flush and tell the agent.
- `[TrainHubDev]` must appear; the original errors and undefined `SMROptInHubFlight` must be absent.
Home: `docs/agent/prompts/Train_Hub_Project/02_TRAIN_HUB_LOADERRORS_low.md`

### OI-12 · opened 2026-09-18 · launch
When this mod heads for upload, make its preview art: `tools/upload_preflight.py` FAILs only on that.
- Paradox rejects a mod with no `image` / `preview.png` before packing.
- Limits: at most 1 MB for Steam, 2 MB for Paradox.
Home: `docs/agent/WORKFLOW.md`
