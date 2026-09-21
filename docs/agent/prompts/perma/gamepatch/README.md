# gamepatch/ — the fix pack's game-patch findings for this mod

**What this is.** When the game updates, the fix pack's perma job
(`C:\Dev\SMR-BugFixPack\docs\agent\prompts\perma\GAME_PATCH_PROMPT.md`) runs first, always
(owner, 2026-09-18). Its sweep, `tools/patchcheck.py` in the fix pack, also hashes everything this
mod's `Code/` names one hop out: pinned bodies, `Require` targets, cited functions and the signature
of every call. For each patch it leaves one entry here, even when nothing is flagged. This folder
is the only route that sweep has to this repo.

## When there is an entry

1. Read the **newest** entry, `<new build>_<date>.md`. Older ones should already be in `done/`.
2. Run its command in the fix pack (`C:\Dev\SMR-BugFixPack`) and confirm the opt-in section
   reproduces. A mismatch is a finding: report it and stop.
3. Act per the entry. For each flagged module, read the flagged rows in **both** archived trees
   (`C:\Dev\SMR-SrcArchive\<version>\Src`) and file a FIX / REMOVE / KEEP verdict in this repo's
   `docs/agent/bugs/`. A REMOVE traces the replacement body (a rename reads as "gone", R-15). A
   clean module needs nothing.
4. `git mv` the entry to `done/` in the commit that lands the verdicts.

Stops: edit nothing outside this repo; boot the game only if the owner asks; questions go to
`docs/PLAYTEST_CHECKLIST.md`.

## Entry format (written by the fix pack's job, step 8)

```
# <new build> — game-patch sweep for the opt-in pack (<date>)

Build pair: old <version> (archive digest <16 hex>…) → new <version> (Steam <buildid>, digest <16 hex>…)
Fix-pack commit the sweep ran at: <sha>
Command (run in C:\Dev\SMR-BugFixPack):
    python tools/patchcheck.py --old <old> --new <new> --code Code --code B:\Dev\SMR\SMR-OptInPack\Code
Fix-pack verdict: <none | scoped | full> — P <holds|broken|n/a> · T <n> · B <n>

## Per module
### <Module>  [<columns>]            (or: ### <Module> — no row)
    <function>  <status> [(<old sig>)->(<new sig>)]  <old file:line> -> <new file:line>
    ...
D2/D3 rows for this module, verbatim.

## Asked
Per flagged module: a body read in both trees and a FIX / REMOVE / KEEP verdict filed in bugs/,
a REMOVE tracing the replacement. Nothing else.
```

Rows are copied from the patchcheck block verbatim; the fix-pack side interprets none of them.
Statuses: `body`, `body+sig`, `removed`, `moved` (same body, another file), `moved+body`.
