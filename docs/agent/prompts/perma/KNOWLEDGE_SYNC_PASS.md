# KNOWLEDGE SYNC PASS — does this repo hold what it cites, and what it needs?

**Fire with:** `task docs/agent/prompts/KNOWLEDGE_SYNC_PASS.md` in a fresh session rooted at
`C:\Dev\SMR-OptInPack`. Any model. Re-runnable — it is a sweep, not a one-off.
**Written 2026-09-12 from the fix-pack side**, after a cross-repo inventory found one live gap here.

## 0 · Why this exists

This mod split out of the Relaunched Fix Pack (`C:\Dev\SMR-BugFixPack`) on 2026-08-12 and has had
two ports since — the 2026-08-31 readiness pass and a one-file repair on 2026-09-12
(donor @ `bec2e06` and `85d95cb`). Ports move what someone *noticed* was missing. Nobody has asked the
mechanical question:

> **Does this repo contain everything it cites?**

That question found §7's gap. Five files here cited `DRONE_PRIORITY_SYSTEM` by name — including the
**live** D06 drone-rebuild design and build docs — and the 30 KB file was only in the fix pack. The
citations looked fine; the target did not exist. Nothing flagged it, because nothing checks.

**Trust by source:** the owner's instruction is authority · tool output carrying its command and sha
is a derived fact · everything else authored — this prompt included — is a **claim**.

## 0.5 · Run the helper FIRST — it does the mechanical half

```sh
python tools/sync_from_fixpack.py          # --facts, --donor-log, --citations, --tools; read-only in both repos
```

It answers, by measurement rather than by reading:

- **`--facts`** — is the fact mirror still a mirror, apart from the adaptations we DECLARE? Its
  `LOCAL_ADAPTATIONS` constant is the retired prose port ledger in the only form that
  cannot go stale, because the thing that reads it is the thing that checks it.
- **`--donor-log`** — what changed on a shared donor surface since `LAST_SYNC`. ⛔ Move `LAST_SYNC`
  in the same commit that lands a sync, or the next run re-reports everything.
- **`--citations`** — §1's sweep, mechanised, with the presence control §1 demands already built in.
  Donor-owned names (WORKFLOW "Donor names"), shipped-game source and the placeholder examples in this
  prompt are counted, not listed.
- **`--tools`** — which donor tools are new, differ or exist only here, apart from what its `TOOLS_*`
  tables DECLARE, and whether the mirrored kit docs are still the donor's bytes. §2.5 adjudicates it.

⛔ **The helper finds CANDIDATES. It decides nothing** — it never writes, stages or copies, because
"does this subject apply to this mod" is judgement. Everything below is how you adjudicate what it
prints, and §2 is a question it cannot ask at all.

⚠️ **Its output is a claim like any other.** Before filing anything it reports, read the sentence
that makes the citation — a name cited *as deleted on purpose* looks identical to a dangling one.

## 1 · The main sweep: dangling citations (the helper's `--citations` pass, adjudicated)

For every file under `docs/` in THIS repo, extract what it cites and check the target exists here.

Citation shapes to catch — all four, because the fix-pack sweep found that name-only searching
misses real references:
1. backticked paths: `` `agent/reports/X.md` ``, `` `docs/agent/facts/EF-0NN.md` ``, `` `tools/y.py` ``
2. bare file names with an extension: `X.md`, `y.py`, `Opt_Z.lua`
3. **ids**: `D0N`, `EF-0NN`, `PT-NN` — resolve to `docs/agent/bugs/<id>.md` / `facts/<id>.md`
4. **section references into another file**: "X.md §4", "X §Control" — the file must exist *and*
   carry that heading

For each citation, classify:
- **RESOLVES** — the target is here. Nothing to do.
- **DANGLING, DONOR HAS IT** — absent here, present in `C:\Dev\SMR-BugFixPack`. **This is the action
  list.** Say which file cites it, whether that citer is live work or a record, and the donor's size.
- **DANGLING, NOWHERE** — absent in both. A broken reference; report it, do not invent a target.
- **STALE-SHAPED** — resolves, but the citer names a section/line the target no longer has.

⚠️ A "not found" is a claim. Before reporting anything DANGLING, prove your search would have found
it if present: run the same method against a file you know exists and show the hit.

## 2 · The reverse question: what does the donor hold that this repo needs?

Narrower and judgement-heavy, so keep it bounded. In `C:\Dev\SMR-BugFixPack` (**read-only — never
write to that repo**), look only for material whose *subject* is this mod:
- anything naming `Opt_AcknowledgedWarnings`, `Opt_ClassicRockets`, `Opt_CohortHousing`,
  `Opt_DroneOverhaul`, `Opt_DroneStatDials`, `Opt_MultipleSuns`, `Opt_NoHomeless`,
  `Opt_ResidencyControl`, `SMR_CommunityOptInPack`, `SMROptInPack`
- the `D01`–`D12` tombstone entries in its `docs/agent/bugs/`

For each, check whether the content is already here **by content, not filename** — the earlier
inventory found most of it already duplicated here, often *larger and more developed here* than in
the donor. Report only genuine gaps. Known and deliberately NOT gaps:
- the donor's `reports/PARKED_OPTIN_REFERENCES.md` — 46 of the **donor's own** wordings, parked until
  this mod publishes. Its text, its obligation. Not ours to hold.
- the donor's opt-in store drafts (`RELEASE_DESCRIPTION_OPTIN.md`, `STORE_OPTIN.md`, the opt-in
  strings in `STORE_METADATA_STRINGS.md`) — a launch-ready listing for this mod, parked there on
  purpose. **Flag them for the launch checklist; do not pull them now** — this mod is NOT PUBLISHED
  (`metadata.lua` version 0, `agent/STATE.md`), and a store draft pulled early goes stale.

## 2.5 · Tools: what the donor built or fixed since (the helper's `--tools` pass, adjudicated)

The owner, 2026-09-18: the sync covers tools too, "since we are often adding new tools".

```sh
python tools/sync_from_fixpack.py --tools   # tools/*.py + tools/hooks/*, then the kit-doc mirror
```

Give each finding one decision, in the commit that acts on it:
- **Port.** Copy the donor's file, then change only what is repo-specific: the module token, paths,
  this repo's lists. Whatever still differs gets a `TOOLS_ADAPTED` row saying why. A new tool's
  header first line becomes its `tools/README.md` catalog row (`python tools/doccheck.py --regen`).
- **Declare.** A donor tool this mod has no use for is a `TOOLS_NOT_PORTED` row with its reason; a
  deliberate local difference is a `TOOLS_ADAPTED` row. ⛔ Never declare an unported donor fix: the
  row would silence exactly what this pass exists to show.
- **Propose to the donor.** A fix or tool that belongs in both (an `ONLY HERE`, or a row reading
  "propose there") goes in the report; the donor is read-only from here.

`NEW THERE` is a donor tool not here. `DIFFERS` is a shared tool differing with no row: a donor fix
not received until shown otherwise. `RECHECK` is a declared adaptation the donor changed since
`LAST_SYNC`: carry the change, keep the row. `NOTE` is a row that no longer matches the tree.
`DRIFT`/`MISSING` concern `tools/TESTKIT.md` and `tools/SMRTK.md`, which are the donor's bytes by
the owner's decision (2026-09-18, one kit serves every mod): re-copy them, and make a change that
belongs in them in the donor first.

⛔ When the sync completes, move `LAST_SYNC` to the donor HEAD you synced against, in that commit.

## 3 · Structure pass (only after §1 and §2)

Cheap checks, report-only:
- `python tools/doccheck.py` — GREEN? Copy any WARN line verbatim.
- Does `docs/README.md`'s map match what is actually on disk, both directions?
- Any file in `docs/agent/reports/` that nothing cites and that records no decision — candidate to
  retire. ⛔ **"Nobody reads it" is NOT "nothing points at it."** The donor learned this the
  expensive way: of 57 files it proposed archiving on read-counts, **43 turned out to be cited**.
  Cite-check before proposing any move, and propose — never move — in this pass.

## 4 · Rules

- **Write only in this repo.** `C:\Dev\SMR-BugFixPack` is read-only from here. If something needs to
  change there, put it in the report and say so; a human carries it across.
- **Copy verbatim or not at all.** A ported file is byte-identical; record its donor sha and md5 in
  the commit message, and move `LAST_SYNC` in that commit when a sync completes. Two identical
  copies is the intended state; an edited copy is a fork nobody will notice. A tool is the one
  exception, and only through a declared `TOOLS_ADAPTED` row (§2.5).
- The kernel's donor-name, archive, documentation-check and commit rules apply.

## 5 · Report

1. §1 counts: citations checked · RESOLVES · **DANGLING-DONOR-HAS-IT** · DANGLING-NOWHERE · STALE.
2. The DANGLING-DONOR-HAS-IT list, each with its citer and whether that citer is live work.
3. §2 genuine gaps only, with the evidence that they are absent here.
3a. §2.5 `--tools` findings, each with its decision: port, declare or propose to the donor.
4. §3 findings, as proposals.
5. Your presence-control from §1's warning — the check that proves your "not found"s mean something.
6. What you could not determine. Say it plainly rather than rounding it to done.
