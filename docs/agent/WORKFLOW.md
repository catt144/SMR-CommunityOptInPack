# Development Workflow

> ## ⭐ ADAPTED COPY — read this ledger before you trust a clause
>
> Copied from `SMR-BugFixPack/docs/agent/WORKFLOW.md` at `33d69f5` on 2026-08-12
> (chain `split-optins`). Its harness rules bind here: probe hygiene and the ARM gate, resolution
> cross-checks, leg design, log review, cheats, co-runs, prompt authoring, EF-047/048/049/050,
> PowerShell 5.1 hazards, the parse sweep and the `PROBE SWEEP:` line.
>
> The six adaptations are:
>
> 1. **Layout and install:** this repo, its `SMR-OptInPack` junction, its title and
>    `SMROptInPack.ListFixes()` replace the donor's. The TestKit is shared, not copied.
> 2. **Namespace:** `SMRFixPack.*` becomes `SMROptInPack.*`, but persisted `SMRFixPack_*` field and
>    modifier-id strings keep their exact bytes (`FIX_POLICY.md` §3).
> 3. **Reading path:** the human playtest file lives in the fix pack; facts and emitted counts are
>    this repo's. `PLAYTEST_HELP.md` was dissolved there on 2026-09-15.
> 4. **Both mods loaded:** the standing rule below is this repo's twin of the donor's clause.
> 5. **Release:** use this document's opt-in-specific release duties, not the donor's release list.
> 6. **Donor names and figures in this document** are `BUG_LIST_AUDIT.md`, `PLAYTEST_ARCHIVE.md`,
>    `AUDIT_FINDINGS.md`, `PRIOR_ART_SURVEY.md`, `DRONE_RESEARCH_BRIEF.md`, `CORUN_RIG_SPEC.md`,
>    `MOD_DESCRIPTION.md`, `F86_EXECUTION_PLAN.md`, every `F##`/`C##`/`D13`, `Fix_*.lua`, and donor
>    site/module counts. Where they resolve is the kernel's rule, not restated here. A future
>    cross-mod sweep searches those names as well as `SMRFixPack`/`Community`; `\bC[0-9]{2}\b`
>    over-reports co-run corrections and audit ids, so it cannot supply a count by itself.
>
> “The pack” means this mod unless the Relaunched Fix Pack is named explicitly. Pre-split records
> use older names; translate them mentally and do not edit them.

Process rules for this repo. Code rules are `FIX_POLICY.md`; global duties and the two bans are in
`CLAUDE.md`; orientation, entry/fact filing, documentation edits, prompt authoring and session close
are the skills in `.claude/skills/`. Situational binding protocol lives in `support/`; the map is
`docs/README.md`.

## Layout

- Dev repo: `C:\Dev\SMR-OptInPack`, git-versioned and canonical. Its public remote is
  `github.com/catt144/SMR-CommunityOptInPack` (owner, 2026-08-13); push what you commit.
- Companion product: `C:\Dev\SMR-BugFixPack`. It shares no runtime files with this mod. Its
  `docs/PLAYTEST_CHECKLIST.md` is the owner's single playtest queue for both mods.
- Game install: `A:\SteamLibrary\steamapps\common\Project Spark`. Shipped Lua source is the
  read-only `<game>\ModTools\Src`; versioned source trees are under
  `C:\Dev\SMR-SrcArchive\<version>\Src`. Never modify the game folder.
- Mod install point: `%AppData%\Surviving Mars Relaunched\Mods\SMR-OptInPack`, a junction to this
  repo, so the checked-out tree is live. The fix pack has a separate junction beside it.
- Tools: `tools/`; `tools/README.md` says what each instrument proves. Audit
  instruments over-report by design: adjudicate a row from its source, never from the tally.
- Shared TestKit, local-only and never shipped: `C:\Dev\SMR-BugFixPack-TestKit`. Change a shared
  probe once there. `SMRTest.OptMissing` SKIPs when this mod is not installed.

## Install for testing

```powershell
New-Item -ItemType Directory -Force "$env:APPDATA\Surviving Mars Relaunched\Mods" | Out-Null
New-Item -ItemType Junction -Path "$env:APPDATA\Surviving Mars Relaunched\Mods\SMR-OptInPack" -Target "C:\Dev\SMR-OptInPack"
```

Enable “Relaunched Fix Pack: Opt-In Modules” in the Mod Manager and restart after editing Lua. A
Mod-Manager disable takes effect only after a full process restart; re-enabling an owner's mod is
the owner's call. `SMROptInPack.ListFixes()` prints this mod's module states. The fix pack has its
own registry and prefix; grep logs with the full `[CommunityOptInPack]` token because `Pack]`
matches both.

## Per-module discipline

1. Every module links to its `bugs/` entry and obeys `FIX_POLICY.md`.
2. Before patching, re-verify the target in the archived source tree for the cited build. Runtime
   `apply()` checks return a reason rather than erroring if a target moved.
3. Parse-check every edited Lua file before commit with Python + `luaparser`, calling
   `ast.parse(open(path, encoding="utf-8-sig").read())`; a syntax error in any listed file breaks
   the whole mod at load.
4. Use one commit per module or tight unit. Update its entry and any player-facing
   `metadata.lua`/`items.lua` text in the same commit as the code.

## Records and rulings

- A proposed cause is filed only after a control pins it; until then, record symptom and hypothesis
  separately. A claimed player route is walked on the surface the player actually uses.
- Every console line, lever or command printed in a human doc carries `[RAN <date>, log <name>]` or
  `[NEVER RUN]`.
- Load-bearing claims in entries, specs and briefs are tagged MEASURED / SOURCE / INFERRED /
  INHERITED / GUESS per row, never once over a table. Tag the route sentence separately from its
  citations, and re-check that route rather than only its cited lines.
- Routed work names its prompt and takeable precondition. A situation-dependent item goes directly
  to the owner's checklist as a rider, not through a prompt that will forward it again.
- A log cited by a status flip is copied into `docs/archive/` in the same commit with `git add -f`;
  `.gitignore` silently drops ordinary `*.log` adds.
- A decision about this mod is not asked until it is mirrored into `docs/DECISIONS_OWED.md` under
  the next `OI-` id, and leaves that list when decided. The kernel names the three classes that
  instead bind the fix pack and go to its checklist.
- For a status flip, edit the entry's front-matter `status:` first and its heading tag second in the
  same edit; regenerate rather than hand-editing `bugs/INDEX.md`.

## After a game patch

Source citations come from `ModTools\Src`, while the game executes `Packs\Lua.fpk` and `Data.fpk`.
Read the installed build and fact hold/move groups with `python tools/doccheck.py
--emit-fingerprint`; never infer them from a prior run.

1. Archive an unarchived source tree under `C:\Dev\SMR-SrcArchive\<version>\Src` before Steam
   overwrites it.
2. Re-extract `Packs\Lua.fpk` and diff it against that build's Src tree; re-verify every full-body
   replacement target byte-for-byte.
3. Run the applicable source-diff instruments routed by `tools/README.md`, and read both source
   bodies before claiming a vanilla fix, continued need, harmlessness or complete coverage.
4. Alongside the fpk diff, re-run the save-exposure enumeration over all five shapes: class method,
   table slot, global assignment, preset field and own thread. Persisted-body version skew is a
   standing failure mode, not only a launch-time one.

Runtime existence/layout checks remain mandatory, but cannot detect an edited same-named function.
A clean mechanical sweep is not evidence that every module still works.

## Probe hygiene (owner, 2026-08-01)

No attended or unattended test starts and no result is recorded until this sweep is clean:

```text
grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/
```

CLEAN is zero hits, or exactly the probes declared by this session's brief and live work list.
Anything else is repaired first (delete file and registration, then commit) or the session stops.

- Every temporary probe/experiment has literal `TEMPORARY` in its header. A temporary probe without
  it is a defect: file it on sight.
- A probe is stale when its answer is recorded. Delete it and its registration in the same commit
  that records the answer.
- Every commit that flips an entry status, records a MEASURED fact or reports PASS/FAIL carries
  `PROBE SWEEP: clean` or `PROBE SWEEP: armed: <files>, declared by <test>`. Re-verify a result
  committed without that line before building on it.
- The sweep covers this repo and the shared TestKit.
- A probe file is present in `Code/` only while its run is happening (owner, 2026-08-04): placing
  and running are one act; deleting and recording are one commit. Until the sitting, keep source
  as a fenced block in the brief, where it is inert because only `metadata.lua`'s code list loads.
  At the sitting place and register it, parse-check it, run, then remove it with the result.
  `doccheck` deliberately blocks a commit while a probe is armed; `--no-verify` is not an escape.
- Long-lived instrumentation has no established home in this repo. Adding one changes the shipped
  code list and requires an owner ruling; it is not a `TEMPORARY` probe.

## Testing checklist per module

Leg-design rules:

- An objective counter can fail and has a liveness witness beside it.
- Reach code by its production route and compute expectations independently from vanilla logic or
  hand-derived constants, never the module's own patched logic. A guard probe also proves that the
  guard still delegates.
- If a selection trigger cannot be steered, invoke the shipped call site on a chosen target and
  settle selection separately by reconstructing its pool.
- A negative result states the condition sampled as well as the count; absence of a never-sampled
  condition is no result.
- A gate on an owner action detects the condition. A typed token is convenience, never the primary
  signal.

Steps:

1. Load a save or new game where the behavior is observable; establish the disabled/base control.
2. Exercise both live Mod Options directions: mid-session enable and mid-session disable, and
   confirm the promised behavior in each state.
3. Review `%AppData%\Surviving Mars Relaunched\logs` for errors.
4. Test uninstall safety separately: save with the mod enabled, disable it in the Mod Manager,
   restart the full process, then load. A Mod Options toggle is not an uninstall test: hooks and the
   environment remain loaded and can no-op cleanly while saved residue still breaks.
5. Update the entry's front-matter status and heading tag together. `tested-attended` means the
   owner was at the keyboard; `tested-unattended` is a real launch without a witness and carries
   weight only for instrument-readable behavior. Bare `tested` is legacy and closed to new work
   (owner, 2026-08-15); do not promote or reinterpret one without its archived evidence.

Run the shared TestKit's `SMRTest.RunAll()` A/B pair when STATE or the brief says it is owed.

### Log review (owner, 2026-08-01)

A flushed log can cover hours of continuous play, and the owner reviews errors with the agent.
“Not caused by our leg” is an attribution verdict, never a reason to stop looking. Report every
unexplained line with its age and let the owner decide; stop and say so when something is out of
the ordinary. Old logs can hold evidence no leg was designed to collect, so mining them for
`[LUA ERROR]` is useful.

### Cheats on playtest saves (owner, 2026-08-12)

Playtest colonies are deliberately oversized and under-industrialized. `CheatFill` on food and
maintenance is life support for the fixture, so cheat markers are the normal condition.

- Count and name them, record the reason, and ask for it once.
- A cheat is a confound only where the reading intersects what it changed; name the intersection or
  state there is none.
- A leg needing a no-cheat run declares that in its brief and prepares a resource-rich save; it
  cannot ask the owner to stop supporting a colony that needs the cheats.
- `[SMRTK] SMRTK_<Verb>` is an intentional TestKit action and needs no owner question. A new vanilla
  `ObjCheat`/`Cheat` marker merits one attribution question. Taint and eligibility are separate
  (`EF-095`/`EF-096`); no-taint does not prove eligibility.

### Both mods loaded (owner, 2026-08-12; active since the split audit that day)

The rig baseline is the Relaunched Fix Pack and this opt-in mod both enabled. A gate read shows two
registries in the player's enable order (`EF-054`).

- Every “the pack” claim names which pack. A `[CommunityFixPack]` line in this mod's leg is expected
  background, attributed and never treated as foreign.
- A loaded module is a confound only where the reading intersects what it changes; name the
  intersection or state there is none.
- A leg needing either mod off declares it in the brief, budgets a full process restart, and hands
  re-enable back to the owner.
- The standing configuration is the compatibility soak. Whole-log review treats cross-mod
  interference as a named class and routes a hit to both repos.

Pre-split single-pack gate reads are historical and never quoted as current.

## Co-runs

`support/CO_RUNS.md` is binding when a batch is tested attended.

## Sign-off tiers (owner, 2026-08-04)

- Tier A, witness: the owner's eyes add information the log cannot carry; they attend the measure
  moment.
- Tier B, evidence card: log-demonstrable; the owner reads a one-screen card with scenario,
  forced/organic state, raw before/after lines, run conditions and one-sentence falsifier. For
  hands-only, the owner performs the named act and then reads the card as Tier B.
- Tier C, delegated: mechanically self-verifying; it ships on the suite verdict with a one-line
  digest per batch, while the owner keeps the veto.
- A demotion from designed Tier A is stated on the card and applies to the next instance, never
  silently.

These tiers govern what the owner reads afterwards; they do not redefine attendance status or
reclassify an existing result.

## Release marking (owner-adopted 2026-08-17; carried here 2026-08-31)

Mark what is live on the portal with an annotated `optin-v<version_major>.<version_minor>.<version>`
tag at upload. The tag and `metadata.lua` agree; `main` remains latest verified work and normally
runs ahead of what shipped. Do not keep standing `testing` or `published` branches: the junction
makes checkout live and the truth-bearing documents are rewritten in place.

The upload sitting/Mod Editor sets `metadata.lua`'s patch `version`; an agent never hand-sets it,
because the editor increments it on save. Record portal version to commit SHA in the fix pack's
`docs/agent/reports/RELEASE_PORTAL_PREP.md` in the same pass.

To inspect shipped code without disturbing `main`, create a worktree at the tag and point the
junction there temporarily. While pointed there, suite readings describe shipped code, not current
work. Create a hotfix branch from the tag only when needed; merge it back, and keep documentation
changes on `main`.

## Release

The launch session owns this list; this mod is not published. Before upload:

1. Schedule the owner's preview image, screenshots and description wording first, and check current portal
   rules. Write the description from the current module entries; it states that this mod works with
   or without the Relaunched Fix Pack and tells Drone Stat Dials users to return both dials to base
   before uninstalling.
2. Walk the fix pack's `docs/agent/reports/PARKED_OPTIN_REFERENCES.md` restore checklist on publish
   day, not earlier; re-read the display-name sites in the current shipped files.
3. Update `metadata.lua`'s `version_major`/`version_minor` and `last_changes` without changing
   `lua_revision`. Any add/remove/reorder of `Code/` files changes `metadata.lua` `code` and the
   `items.lua` `ModItemCode` list together, in the same order and commit.
4. Run `python tools/upload_preflight.py` to zero FAIL before opening the Mod Editor, inspect
   `python tools/pack_predict.py .`, and reconcile the downloaded archive with
   `python tools/pack_list.py <ModContent.fpk> --tree .`. The TestKit is never uploaded.
5. Recount every player-facing probe total with the emitting command before quoting it. Credit
   ChoGGi (Fix Bugs) and LukeH (Martian Express) as prior art.
6. Apply the save-exit duties (owner, 2026-07-31) in `FIX_POLICY.md` §3: publish the uninstall
   procedure and residual disclosure, record a disposition for every exposed site, and have the
   D13 rescue artifact ready. Its one-artifact scope covers both mods, but this mod's residue is
   measured from this tree, never inherited. A separately shipped rescue artifact receives its own
   metadata, preview, description, portal pass, console certification, version-skew statement and
   zero-residue proof.
7. Run every shipping module in both configurations—with the fix pack installed and absent—as
   required by `FIX_POLICY.md` §8, and name the tested fix-pack version in the release note.
8. Tag the exact uploaded commit as described above and push the tag.

## Authoring a prompt

Use the `prompt-authoring` skill. It owns brief structure, staleness, live work-list granularity,
scope, stops, testing rails and lifecycle.

## `[FAQ]` tag

Mark behavior a player could mistake for a bug, or a deliberate design answer of “no”, with
literal `[FAQ]` on the entry or module source that already explains it. Never create a document
just to hold a tag. A tag is a bookmark, not work or a promise; remove it in the commit that changes
the behavior. Collect the current set mechanically:

```text
grep -rn "\[FAQ\]" docs/ Code/
```
