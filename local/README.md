# local/

Git-ignored home for DURABLE material that belongs to THIS tree but must not
be committed — large binaries, logs, evidence a report links to. Owner
decision, 2026-09-21 (ported the same day from the fix pack, which landed the
pattern first): material that belongs to one tree lives in that tree (the
exceptions are things every SMR mod uses — the TestKit and Assets repos, the
archived game source, the Workshop mod corpus, the owner's screen-capture
drop folder — see `docs/README.md` "Outside the repo"). An in-tree home with
no gate becomes a dumping ground, so this folder gets one.

Unlike `scratch/` (working space, swept at 14 days by the eviction prompt),
`local/` is **not swept**. Nothing here ages out on its own; it leaves when
its row's condition is met.

**The gate: one row per subfolder, below.** No row, no folder — `doccheck`
reports a subfolder with no row, and a row that names a folder not on disk,
both RED. Nothing in this table is itself a record; the record is the entry
or report in the citing column, or git history.

| folder | holds | cited by | ends when |
|---|---|---|---|
| `retired-modules/` | Convenience copies of four retired opt-in modules (`DEAD-Opt_CohortHousing.lua`, `DEAD-Opt_NoHomeless.lua`, `OVERTAKEN-Opt_ClassicRockets.lua`, `PARKED-Opt_DroneOverhaul.lua`) plus its own `README.md`, moved in 2026-09-21 from the formerly out-of-tree `C:\Dev\SMR-OptInPack-archive\` | [`agent/bugs/D01.md`](../docs/agent/bugs/D01.md), [`agent/bugs/D06.md`](../docs/agent/bugs/D06.md), [`agent/bugs/D07.md`](../docs/agent/bugs/D07.md), [`agent/bugs/D12.md`](../docs/agent/bugs/D12.md), [`agent/reports/MODULE_REVALIDATION_1_1_0.md`](../docs/agent/reports/MODULE_REVALIDATION_1_1_0.md), `metadata.lua`, `tools/doccheck.py` | Never on a fixed date — these are convenience copies; git history (restore shas `cc846e4` and `1716471`, per `retired-modules/README.md`) is the real record, so the folder is unnecessary the day nothing above still needs to read a module without a `git show` |
