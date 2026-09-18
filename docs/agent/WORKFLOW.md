# Development Workflow

Process rules for this repo. Code rules are `FIX_POLICY.md`; the global duties are `CLAUDE.md`'s
`Must_Read_Header`; orientation, filing, prompt writing and session close are the skills in
`.claude/skills/`. Situational procedures live in `support/`; the map is `docs/README.md`.

## Layout

- Dev repo: `C:\Dev\SMR-OptInPack`, git-versioned, canonical. Public remote
  `github.com/catt144/SMR-CommunityOptInPack` (owner, 2026-08-13); push what you commit.
- Game install: `A:\SteamLibrary\steamapps\common\Project Spark` ("Project Spark" is the Steam
  folder name). Shipped Lua source, read-only: `<game>\ModTools\Src` (`Lua\`, `CommonLua\`, `Data\`,
  `DLC\`). Nothing under the game folder is ever modified.
- Archived source trees, one per game version: `C:\Dev\SMR-SrcArchive\<version>\Src` with a
  `MANIFEST.sha256`; that folder's README holds the archive rule.
- Mod install point: `%AppData%\Surviving Mars Relaunched\Mods\SMR-OptInPack`, a junction into the
  dev repo, so the checked-out tree is the running mod.
- Saves: reach them through the fix pack's `saves/` folder (its WORKFLOW "Layout"); this repo has
  none.
- TestKit, never shipped and local-only by decision, shared with the fix pack:
  `C:\Dev\SMR-BugFixPack-TestKit`; a shared probe is changed once, there. Its README is the kit's
  own build-state document; the durable pack-side view is `tools/TESTKIT.md`, and the SMR Tool Kit
  plus its sitting slots are `tools/SMRTK.md`. Both are the fix pack's bytes, mirrored (owner,
  2026-09-18) and checked by `python tools/sync_from_fixpack.py --tools`: change them there first.
- Sibling mods: the Relaunched Fix Pack `C:\Dev\SMR-BugFixPack` (its own docs) and the save-rescue
  tool `C:\Dev\SMR-CommunitySaveRescue` (design and status in the fix pack's `bugs/D13.md`;
  unpublished, held as a contingency).

## Install for testing

```powershell
New-Item -ItemType Directory -Force "$env:APPDATA\Surviving Mars Relaunched\Mods" | Out-Null
New-Item -ItemType Junction -Path "$env:APPDATA\Surviving Mars Relaunched\Mods\SMR-OptInPack" `
  -Target "C:\Dev\SMR-OptInPack"
```

Enable "Relaunched Fix Pack: Opt-In Modules" in the game's Mod Manager; restart the game after
editing Lua. The console line `SMROptInPack.ListFixes()` prints each module's status. Grep logs
with the full `[CommunityOptInPack]` token: `Pack]` matches both mods.

## Per-module discipline

1. Every module links to a `bugs/` entry with file:line evidence and obeys `FIX_POLICY.md`.
2. Re-verify the target against the cited Src lines before patching; `apply()`'s self-check guards
   it at runtime and returns a reason string, never an error, if a game update moved it.
3. `python tools/parsecheck.py` before any commit that touches Lua: a syntax error in any listed
   file breaks the whole mod at load.
4. One commit per module or tight group, with its entry and any player-facing `metadata.lua` or
   `items.lua` text in the same commit.

## Records and rulings

- Every console line, lever or command printed in a human doc carries `[RAN <date>, log <name>]`
  or `[NEVER RUN]`; unmarked, a never-executed snippet reads like a proven one.
- Load-bearing claims in entries, specs and briefs are tagged MEASURED / SOURCE / INFERRED /
  INHERITED / GUESS per row, never as one claim over a table. The route sentence ("therefore the
  only way is…") is tagged separately from the lines it cites.
- A routed item names its owner prompt and its precondition. An item whose precondition is a
  situation goes to the checklist as a rider, not to a prompt that will forward it again.
- A log a status flip will cite is copied into `docs/archive/` in the same commit, with
  `git add -f` (`.gitignore` drops `*.log` silently). The game keeps about 20 log files.
- A ruling is recorded with the condition it was made under; re-read it against today's state before
  treating it as binding, and never record a later ruling as a reversal without checking whether the
  earlier condition still holds.

## After a game patch — the source-diff instruments

fpk verification: line numbers in `bugs/` and `facts/` come from `ModTools\Src`, and the game
executes `Packs\Lua.fpk` and `Data.fpk`. Parity was byte-identical for 1.1.0.403908 (`EF-085`);
re-prove it after every update, since a same-named function edited under a full replacement is
invisible to the runtime self-checks.

0. Archive first. Copy `ModTools\Src` to `C:\Dev\SMR-SrcArchive\<version>\Src` with its
   `MANIFEST.sha256` before the update lands, and whenever an unarchived version is on disk. Steam
   updates and branch switches overwrite the tree in place and unasked (`EF-075`).
1. Re-extract `Packs\Lua.fpk` (`tools/flpk_extract.py`) and diff it against the new Src tree.
2. This repo has none of the fix pack's body, arity or tree-diff instruments (`FIX_POLICY.md`'s
   adaptation note): every module target is re-read in both trees' bodies.
3. The 1.0.7 → 1.1.0 diff is already analysed in the fix pack, under
   `C:\Dev\SMR-BugFixPack\docs\agent\reports\`: `GAME_1_1_0_AUDIT.md` and `GAME_1_1_0_IMPACT.md`
   (what the patch changed), `VANILLA_DIFF_DISPOSITION.md`, `PACK_1_1_0_REVERIFICATION.md`, and the
   precomputed `vanillahunt\*.tsv` tables (files, function inventory, callers, presets). Read those
   before sweeping either tree; a bare `reports/GAME_1_1_0_*` or `PACK_1_1_0_*` citation in a
   mirrored fact resolves there.
   This repo's own module re-read is `reports/MODULE_REVALIDATION_1_1_0.md`.

What an instrument licenses. On its output alone you may state exactly four things: a pinned body's
bytes did or did not change; a named arity did or did not change; a stated regex is or is not
present in a named body; a named function or preset field exists in one tree and not the other.
"Vanilla fixed it", "this fix is still needed", "that change is harmless" and "nothing moved under
us" each need a second source: a read of the replacement body in both trees, or a run in the game.

- None of them see the engine, runtime-only behaviour, or the 1.0.7 `DLC/` subtree.
- A clean run over every module is not evidence that every module still works.

Each instrument's own header defines its flags, its verdicts and what each verdict obliges;
`tools/README.md` routes to them, and to every other script in `tools/`. Which `--selftest` runs are
gated is what `python tools/doccheck.py` prints — read its `SELFTEST:` lines. What the output above
licenses is decided here, not there.

## Probe hygiene (owner, 2026-08-01)

No test session starts and no result is recorded until the stale-probe sweep has run clean:

```
grep -rln "TEMPORARY" Code/ ../SMR-BugFixPack-TestKit/Code/
```

CLEAN is zero hits, or every hit is a probe that this session's brief and todo list declare it
needs. Anything else: repair first (delete the file and its `metadata.lua` line, commit) or stop
and report. Stale probes are how false facts got recorded.

- Every temporary probe carries the literal word `TEMPORARY` in its header comment; that is what the
  sweep greps for. One without the marker is a defect: file it on sight.
- A probe is stale the moment its answer is recorded. Delete it in the commit that records the
  answer.
- Every commit that flips an entry status, records a MEASURED fact or reports a PASS/FAIL carries a
  `PROBE SWEEP:` line, `clean` or `armed: <files>, declared by <test>`. A result commit without one
  is re-verified before anything builds on it.
- A probe file is in `Code/` only while its run is actually happening (owner, 2026-08-04): placing
  and running are one act, deleting and recording are one commit. Until the sitting, park the
  probe's source as a fenced block in the brief, where it is inert: the mod loads only the files
  in `metadata.lua` `code` (`Mod.lua:490-521`). doccheck's `temporary_sweep()` is red on any marker
  in `Code/` and the hook blocks on red; `--no-verify` is not an alternative. Long-lived
  instrumentation belongs in the TestKit's `90_Loggers.lua` behind a toggle, never marked
  `TEMPORARY`.
- A sweep is fresh for 24 hours, or until a change touches a probe, a module a probe reads, or the
  kit's registration. A stale sweep is owed at the next playtest before its probes run, never
  between sittings. No agent, gate or kit code refuses a boot, a suite run, an upload or any other
  work over a sweep's age, and none overrides the owner (ck184, 2026-09-15: a gate, not a hard
  rule).

## Testing checklist per module

Leg-design rules:

- An objective counter is only objective if it can fail, and it needs a liveness witness beside it.
- A probe reaches the code the way production does and computes its expectation independently
  (vanilla's algorithm or hand-derived constants), never with the module's own logic. A guard probe
  also asserts that the guard still delegates.
- When the trigger is a selection you cannot steer, delete the lottery: invoke the shipped call site
  directly on a chosen target and settle the selection half by reconstructing the pool.
- A negative result states the condition it sampled, not just the count. Absence of a never-sampled
  condition is not a negative result.
- A gate on an owner action detects the condition; a typed token is a convenience, never the
  primary signal.

Steps:

1. Load a save or new game where the behaviour is observable; establish the control with the module
   off or at its base setting.
2. Exercise both live Mod Options directions, a mid-session enable and a mid-session disable, and
   confirm the promised behaviour in each state.
3. Confirm no error spam in `%AppData%\Surviving Mars Relaunched\logs`.
4. Save with the mod enabled, disable it in the Mod Manager, restart the process, load: the game
   must not break (PT-20 shape; `FIX_POLICY.md` §3). A Mod-Manager disable takes effect only after
   a full process restart; without one the mod is still loaded and the reading is a mixed state
   (PT-20 redo, 2026-08-14; D13's four-states rule). Never a Mod Options toggle: a toggled-off
   module keeps its hooks and reads clean by construction (`EF-002`).
5. Set the entry's status, front matter and heading tag together. `tested-attended`: the owner was
   at the keyboard. `tested-unattended`: real launches with nobody watching; full weight for what an
   instrument can read, never for a screen event. Bare `tested` is legacy and closed to new work
   (owner, 2026-08-15): it means attendance unaudited, so never promote one without re-deriving it
   from the archived record and never read it as attended.

The TestKit's `SMRTest.RunAll()` A/B pair (mod disabled, then enabled) is the regression harness.

### Log review (owner, 2026-08-01)

A flushed log covers hours of continuous play, and the owner reviews the errors with the agent;
every time they have pushed back it turned up a vanilla defect. "Not caused by our leg" is an
attribution verdict, never a reason to stop looking: report every unexplained line with its age and
let the owner decide, and stop and say so when something is out of the ordinary. Old logs hold
evidence no leg was designed to collect; mining them for `[LUA ERROR]` is cheap.

### Cheats on playtest saves (owner, 2026-08-12)

Playtest colonies are oversized and under-industrialised, so `CheatFill` on food and maintenance is
life support for the fixture and cheat markers are the normal condition.

- Count them, name them, attribute the reason, and ask for it once.
- A cheat is a confound only where the reading intersects what it changed; name the intersection or
  state there is none.
- A leg that needs a no-cheat run declares it in its brief and preps a resource-rich save in
  advance; it may not ask the owner to stop cheating on a colony that needs it.
- Toolkit `[SMRTK] SMRTK_<Verb>` records are intentional test actions: never ask the owner about
  one. A vanilla `ObjCheat`/`Cheat` marker in a new log is worth one attribution question. Taint
  and eligibility are `EF-095`/`EF-096`; no-taint never proves eligibility.

### Both mods loaded (owner, 2026-08-12)

The rig's baseline is the fix pack and the opt-in pack both enabled; a gate read shows two
registries, in the player's enable order (`EF-054`).

- Every "the pack" claim names which pack. A `[CommunityFixPack]` line in an opt-in log is expected
  background, attributed, never flagged as foreign.
- A loaded fix-pack module is a confound only where the reading intersects what it changes; name the
  intersection or state there is none.
- A leg that needs the fix pack off declares it in its brief and budgets a full process restart for
  the disable; the re-enable is handed back to the owner.
- The standing configuration is the compatibility soak: cross-mod interference is a named class in
  whole-log reviews, and a hit routes to both repos' records.

Single-pack gate reads predate the split and are never quoted as current.

## Co-runs

`support/CO_RUNS.md`, binding when a batch of modules is tested attended.

## Sign-off tiers (owner, 2026-08-04)

- Tier A, witness: the owner's eyes add information the log cannot carry; they attend the measure
  moment.
- Tier B, evidence card: log-demonstrable; the owner reads a one-screen card (scenario, forced or
  organic, the raw before/after log lines, run conditions, the one-sentence falsifier) and OKs it.
  Hands-only: the owner does the named act, then reads the card as Tier B.
- Tier C, delegated: mechanically self-verifying (the probe-suite class); ships on the suite
  verdict with a one-line digest per batch; the owner keeps the veto.
- A demotion from a designed Tier A is stated on the card and applies to the next instance, never
  silently.

The tiers say what the owner reads afterwards; a status word still needs the attendance it names.

## Release

This mod is not published; the launch session owns this list, and the owner uploads through the fix
pack's `docs/UPLOAD_WORKFLOW.md`. This mod's release duties are `FIX_POLICY.md` §3a and §8 (save
exit, both configurations). Before upload:

1. Schedule the owner's preview image, screenshots and description wording first, and check current
   portal rules. Write the description from the current module entries; it states that this mod
   works with or without the Relaunched Fix Pack and tells Drone Stat Dials users to return both
   dials to base before uninstalling.
2. Walk the fix pack's `docs/agent/reports/PARKED_OPTIN_REFERENCES.md` restore checklist on publish
   day, not earlier; re-read the display-name sites in the current shipped files. Its P38
   `description` still says the mod "stands down if an official patch changes what it was written
   for", a promise the fix pack retired on 2026-09-12: write the description per step 1 and never
   paste P38 back verbatim.
3. Update `metadata.lua`'s `version_major`/`version_minor` and `last_changes` without changing
   `lua_revision`. The Mod Editor sets the patch `version` on save; an agent never hand-sets it.
4. Run `python tools/upload_preflight.py` to zero FAIL before opening the Mod Editor, inspect
   `python tools/pack_predict.py .`, and reconcile the downloaded archive with
   `python tools/pack_list.py <ModContent.fpk> --tree .`.
5. Publish the uninstall procedure and residual disclosure, and have the D13 rescue artifact ready:
   its one-artifact scope covers both mods, but this mod's residue is measured from this tree, never
   inherited. A separately shipped rescue artifact gets its own metadata, preview, description,
   portal pass, console certification, version-skew statement and zero-residue proof.

Standing facts with no other home:

- The upload packs the whole mod folder, junctions and symlinks included, filtered only by
  `metadata.lua` `ignore_files` (`GedModEditor.lua:678-741`). Never put a link inside the mod folder
  unless a pattern covers it. `tools/upload_preflight.py` fails on a link whose contents would pack,
  on any packed file outside `Code/*.lua`, `metadata.lua`, `items.lua`, `LICENSE` and the preview
  image, and on a pack over 5 MB; doccheck's PACK IGNORE PARITY gate keeps `pack_predict.py`'s copy
  of the list equal to `metadata.lua`'s.
- `items.lua` carries one `ModItemCode` per `Code/` file in `metadata.lua` order, so the editor
  round-trip regenerates the same code list; add, remove or reorder in both, same commit.
- The TestKit is never uploaded.
- Prior art: ChoGGi (Fix Bugs) and LukeH (Martian Express), the fix pack's
  `reports/PRIOR_ART_SURVEY.md`, which also backs the save-safety claim in player-facing text.

## Release marking (2026-08-17)

What is live on the portal is marked with an annotated tag per mod, `fixpack-`/`optin-`/`rescue-`
plus `version_major.version_minor.version` from `metadata.lua`, pushed at upload; the tag and
`metadata.lua` must agree, and the portal version is recorded against the sha in the fix pack's
`reports/RELEASE_PORTAL_PREP.md`. `main` is latest verified work and normally runs ahead of what
shipped. No standing `testing` or `published` branch: the junction makes the checked-out tree the
running mod, and STATE and both generated indexes are rewritten in place, so long-lived branches
conflict on exactly those files and silently change what the rig loads. To reproduce what a player
runs, `git worktree add ../SMR-OptInPack-shipped <tag>` and point the junction there for the
investigation; while it is pointed there no suite reading describes current work. A hotfix branch
is cut from the tag the day it is needed. A short-lived code-only branch per chain is justified for
code nobody is sure about; doc changes still go to `main` directly.

## Authoring a prompt

Use the `prompt-authoring` skill. R-D, self-split: depth is the cost, so legs are packed at
authoring to roughly `filesize/4 × 1.7` and about 75% fill, never to the edge of a window; a retry
is a fresh fire, not a continuation; working legs are blinded to the budget. Attended sittings are
indivisible and exempt.

## `[FAQ]` tag

Behaviour a player could mistake for a bug, or a question the design deliberately answers "no" to,
is marked with the literal `[FAQ]` on the entry that already explains it, never in a new doc;
`grep -rn "\[FAQ\]" docs/ Code/` collects them. A tag is a bookmark, not work and not a promise.
Remove it in the commit that changes the tagged behaviour.

## Verification rails

The global duties are in `CLAUDE.md`; facts with falsifiers are in the `prompt-authoring` skill. R-F: size the
verification by owner-observability. A player-visible defect is verified by one attended A/B in the
game, the owner being the cheapest verifier of "can a player actually do this"; an engine-internal
defect by desk harness plus audit, because watching would show nothing. Build legs inherit behind a
fingerprint and re-derive only what moved; zero-trust re-derivation is the terminal audit's job.

## Donor names

"The pack" means this mod unless the Relaunched Fix Pack is named. This file is the fix pack's
WORKFLOW with this repo's names; a donor name left in it (a bare `F##`/`C##`/`PT-##`/`ck###`/`D13`,
a `Fix_*.lua`, `PRIOR_ART_SURVEY.md`, `RELEASE_PORTAL_PREP.md`, `PARKED_OPTIN_REFERENCES.md`,
`UPLOAD_WORKFLOW.md`) resolves in `C:\Dev\SMR-BugFixPack`. A cross-mod sweep searches
those names as well as `SMRFixPack`/`Community`; `\bC[0-9]{2}\b` over-reports co-run corrections
and audit ids, so it cannot supply a count by itself.
