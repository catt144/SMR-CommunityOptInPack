# The Test Kit — this mod's measurement surface

**Reader: a worker seat with this repo open.** This is the opt-in-mod side of the
companion mod that measures the Relaunched Fix Pack family. It tells you how to
install the shared kit, which registry surface belongs to this mod, and what its
gate lines license. Probe hygiene remains policy in
`docs/agent/WORKFLOW.md`, "Probe hygiene".

## How to run the suite (rule 8: answerable from this repo alone)

The **TestKit is a separate, never-shipped local repo at
`C:\Dev\SMR-BugFixPack-TestKit`**, and ONE kit serves BOTH mods. It is not
duplicated here — a second kit would be a second set of probe verdicts to
reconcile.

* Install both mods as directory junctions under
  `%AppData%\Surviving Mars Relaunched\Mods\` (this repo's is
  `SMR-OptInPack`), plus the TestKit's own junction; enable them in the Mod
  Manager. Full recipe: `docs/agent/WORKFLOW.md` → "Install for testing".
* Probe hygiene is a HARD GATE before any testing —
  `docs/agent/WORKFLOW.md` → "Probe hygiene", including the parked-instrument
  rule, the ARM gate and the `PROBE SWEEP:` line every result commit carries.
* **This mod's registry surface in the kit** is `SMRTest.OptStatus(id)` /
  `SMRTest.OptMissing(id)` (the fix pack's is `FixStatus`/`FixMissing`), and
  `SMRTest.FromOptInPack(fn)` recognises source paths from this repo.
  ⛔ `OptMissing` returns **SKIP**, never FAIL, when the whole opt-in registry
  is absent — a mod that is legitimately not installed is not a failing suite.
* `SMRTest.RunAll()` prints **two** gate lines, one per mod:
  `fix pack present: %d/%d fixes active` and
  `opt-in pack present: %d/%d modules active`. ⛔ Grep logs with the FULL
  bracketed token (`[CommunityOptInPack]` / `[CommunityFixPack]`) — `Pack]`
  matches both.
* In-game console: `SMROptInPack.ListFixes()` prints every module's status.
