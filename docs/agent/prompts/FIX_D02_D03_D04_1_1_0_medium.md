# Three 1.1.0 fixes: D03's dead tourist guard, D04's sun-removal relink, D02's split notification ids

## Authority

- Owner ruling 2026-09-18: MODULE FREEZE is lifted on every remaining shipping module (`CLAUDE.md`).
  `D01` `ClassicRockets` was retired the same day, separately (`docs/agent/bugs/D01.md`) — not this
  brief's concern.
- `OI-03` ruled **(a)**: repair `ResidencyControl`'s tourist guard.
- `OI-04` ruled **(a)** (owner, 2026-09-18 — overriding this item's own recommended (b)): build the
  `MultipleSuns` sun-removal relink, not just document the gap.
- `OI-17` ruled **(a)**: widen `AcknowledgedWarnings`' id set now, not at launch-day re-verification.
- The fix pack's TestKit kit-edit gate (checklist item 83) is dissolved (owner ruling 2026-09-18,
  `docs/agent/STATE.md` Holds) — `60_Probes_Opt.lua`/`30_Probes_Wave3.lua` may be edited from this
  side without separate fix-pack sign-off.
- Both bans in `FIX_POLICY.md`'s header still bind. None of the three fixes below adds a persisted
  name or touches the framework; skip re-arguing that — just don't violate it.

## Start

`git log --oneline -5`, `git pull --ff-only`. This brief landed at the commit
`git log -1 --format=%h -- docs/agent/prompts/FIX_D02_D03_D04_1_1_0_medium.md` names.
`git diff --stat <that sha>..HEAD -- Code/Opt_ResidencyControl.lua Code/Opt_MultipleSuns.lua Code/Opt_AcknowledgedWarnings.lua docs/agent/bugs/D02.md docs/agent/bugs/D03.md docs/agent/bugs/D04.md`
empty ⇒ the facts below still hold. If D01's retirement from this same session is still
uncommitted, commit it separately first so this brief's own diff stays legible.

Put the three fixes in the todo tool before any write — one item per commit-and-verify unit, one
in progress at a time.

## Where things stand

All three findings are desk-read only, from the two archived trees
(`B:\Dev\SMR\SMR-Shared\SMR-SrcArchive\1.0.7.396349\Src`, `…\1.1.0.403908\Src`) — none has been run in the actual
game. Read each module's own bug entry before touching its file; each carries the exact citations
this brief summarizes. The fix pack's own `F117`
(`C:\Dev\SMR-BugFixPack\docs\agent\bugs\F117.md`) independently hit and *executed-fixed* the
identical `ChooseDome` argument-shape change in a different module — read it before writing D03's
guard; it confirms `colonist.traits.Tourist` is where the flag lives on 1.1.0, with a real Lua
harness, not just a source read.

## End state

### 1 · D03 `ResidencyControl` — repair the dead tourist guard

- `Code/Opt_ResidencyControl.lua:209-210`. `ChooseDome`'s first argument changed from a traits
  table (1.0.7) to the colonist/applicant object (1.1.0); `Tourist` now only exists at
  `traits.traits.Tourist`. Write a shape-tolerant check — safe on both shapes, since a colonist
  object never carries a bare `.Tourist` and a traits table never carries a nested `.traits` — a
  small `is_tourist(traits)` helper is enough. No runtime probe needed: unlike F117, guessing wrong
  here has no throw/mis-score risk, just a wrong boolean. Your call on the exact helper shape.
- Fix the probe that would otherwise keep passing regardless of the bug:
  `C:\Dev\SMR-BugFixPack-TestKit\Code\60_Probes_Opt.lua:140` calls
  `ChooseDome({ Tourist = true }, ...)` — the 1.0.7 shape. Change it to the 1.1.0 shape
  (`{ traits = { Tourist = true } }` or equivalent) so it actually exercises the regression.
  Confirm it FAILs against the unfixed wrapper before landing the code fix, then PASSes after —
  a probe that could pass vacuously either way is exactly how this regression escaped notice.
- Close `OI-03` in the commit that lands this. Append the repair to `docs/agent/bugs/D03.md`'s
  2026-09-17 finding; do not rewrite it.

### 2 · D04 `MultipleSuns` — relink on sun removal

- `ArtificialSunBase:Done` (`1.1.0.403908/Src/Lua/Buildings/ArtificialSun.lua:65-74`) unbinds every
  panel bound to the removed sun (`panel.artificial_sun = false`, `panel:UpdateProduction()`) and
  never re-tests whether another sun still covers them. `Code/Opt_MultipleSuns.lua` already has the
  exact re-test this needs — `find_sun_in_range` (`:77-86`) — used by the existing
  `SolarPanelBase:GameInit` wrap and the `OnMsg.LoadGame` sweep.
- Post-wrap `ArtificialSunBase.Done` the same way the file already wraps `SolarPanelBase.GameInit`:
  a chain wrapper, guarded by `module_active()`, added to `apply()`'s `Require` check with a reason
  string. Capture the affected panel list *before* calling the original — it clears
  `panel.artificial_sun`, so take the list from `self.city.labels.SolarPanelBase` filtered on
  `panel.artificial_sun == self` first. After the original runs, for each captured panel now dark,
  run `find_sun_in_range` and `panel:SetArtificialSun(new_sun)` if one exists.
- **Verify, don't assume:** whether `self` (the sun being removed) is still `IsValid` and still
  present in `city.labels.ArtificialSun` at the point `Done` runs. `find_sun_in_range` already
  excludes invalid suns via `IsValid(sun)` — confirm that actually excludes `self` here; add an
  explicit `sun ~= self` guard if it doesn't.
- `done_map` truthy means "kept, whole map being torn down" and the shipped body already early-outs
  on it (`if done_map then return end`) — your wrapper should skip relink work in that case too.
- Turn `OI-04` from (b) to (a) in the commit message — the owner overrode its own recommendation on
  2026-09-18. Append to `docs/agent/bugs/D04.md`'s finding.

### 3 · D02 `AcknowledgedWarnings` — widen the id set

- `Code/Opt_AcknowledgedWarnings.lua:67`, `local ID = "NotWorkingBuildings"`, used at three call
  sites (`:99`, `:115`, `:125`), all `== ID`. Replace with a set and switch each site to membership:
  `NotWorkingBuildings` plus the seven `ReasonNotification` targets — `DepositExhausted`,
  `PowerShortage`, `WaterShortage`, `OxygenShortage`, `NoDroneService`, `UnreachableBuilding`,
  `EnvironmentalProblem` (enumerated at
  `1.1.0.403908/Src/Lua/Buildings/BaseBuilding.lua:243-266`, and there's already a shipped
  `RoutedNotifications` table built from those same values at `:280-281` — read it, don't retype
  this brief's list).
- **`MaintenanceStuckBuildings` is explicitly OUT of this fix.** It never reaches
  `ShouldShowNotWorkingNotification` — `Malfunction`/`MalfunctionRes` are in `SuppressedReasons`
  (`:268-278`), a different notification raised from `RequiresMaintenance.lua`. Covering it means
  wrapping a different hook, not adding an id to this list; that is a separate, larger question and
  does not belong in this "already know how to fix it" pass.
- Same three call sites, same already-wrapped globals — no new `Require` targets needed.
- Rule `OI-17` (a) in the commit. Append to `docs/agent/bugs/D02.md`'s finding.

**Done means:** all three fixes land, each with its probe/test updated to actually exercise the
fixed behaviour, each bug entry gets its dated addendum, and `OI-03`/`OI-04`/`OI-17` are deleted in
the commits that rule them. If time runs out, land D03 first (it's the smallest and has the
independent F117 confirmation), then D02 (mechanical), then D04 (the most new code) — never leave
a fix landed without its probe/test update.

## Facts you would otherwise re-derive

- `ChooseDome`'s 1.1.0 signature and all nine current call sites: `docs/agent/bugs/D03.md`'s
  2026-09-17 section; independently confirmed, executed, by the fix pack's `F117`.
- `ArtificialSunBase:Done`'s body, verbatim above, read
  `1.1.0.403908/Src/Lua/Buildings/ArtificialSun.lua:65-74` this session.
- `ReasonNotification`/`SuppressedReasons`/`RoutedNotifications`, verbatim above, read
  `1.1.0.403908/Src/Lua/Buildings/BaseBuilding.lua:243-281` this session.

## Scope

In: the three code fixes above, their probe/test coverage, their bug-entry addenda, and closing
`OI-03`/`OI-04`/`OI-17`. Out: `D01` (already retired, separate), anything on the parked/dead
modules (`D06`/`D07`/`D12`), any new persisted name, and `MaintenanceStuckBuildings` coverage for
D02.

## Stops

- If `ArtificialSunBase:Done`'s shape on the installed build differs from what's quoted above (a
  further 1.1.x patch moved it), stop and report the drift rather than porting the design blind.
- If the TestKit probe edit needs touching a file this brief doesn't name, stop and ask — the kit
  is shared with the fix pack even though the sign-off gate is dissolved.
- If any fix would need a new persisted name or a new `SMRFixPack_*`/`SMROptInPack_*` field, stop —
  that is a bigger decision than this brief covers.

## Do not claim

- "D03/D04/D02 are fixed" from source and probes alone. None of the three falsifiers named in each
  bug entry has been run in the actual game; the true claim is "the source-derived defect is
  repaired and the probe/test exercises it," not "confirmed in play."
- "The probe passes" as proof for D03 specifically, without first showing it FAILs pre-fix — a
  shape mismatch could make it pass vacuously either way, which is exactly how the original
  regression escaped notice.

## Lifecycle

One-off. Delete this file and its row in `docs/agent/prompts/README.md` once all three fixes land
and their checklist items close.
