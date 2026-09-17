# KNOWLEDGE SYNC PASS — does this repo hold what it cites, and what it needs?

**Fire with:** `task docs/agent/prompts/KNOWLEDGE_SYNC_PASS.md` in a fresh session rooted at
`C:\Dev\SMR-OptInPack`. Any model. Re-runnable — it is a sweep, not a one-off.
**Written 2026-09-12 from the fix-pack side**, after a cross-repo inventory found one live gap here.

## 0 · Why this exists

This mod split out of the Relaunched Fix Pack (`C:\Dev\SMR-BugFixPack`) on 2026-08-12 and has had
two ports since — the 2026-08-31 readiness pass and a one-file repair on 2026-09-12
(`agent/PROVENANCE.md` §6, §7). Ports move what someone *noticed* was missing. Nobody has asked the
mechanical question:

> **Does this repo contain everything it cites?**

That question found §7's gap. Five files here cited `DRONE_PRIORITY_SYSTEM` by name — including the
**live** D06 drone-rebuild design and build docs — and the 30 KB file was only in the fix pack. The
citations looked fine; the target did not exist. Nothing flagged it, because nothing checks.

**Trust by source:** the owner's instruction is authority · tool output carrying its command and sha
is a derived fact · everything else authored — this prompt included — is a **claim**.

## 1 · The main sweep: dangling citations (do this first, it is the one that pays)

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
- **Copy verbatim or not at all.** A ported file is byte-identical and gets a `PROVENANCE.md` row
  with its donor sha and md5 (§7 is the worked example). Two identical copies is the intended state;
  an edited copy is a fork nobody will notice.
- **Never edit a record** (`docs/archive/`, dated log lines) — translate mentally.
- Commit by pathspec: `git add <exact paths>` then `git commit -F <msgfile> -- <same paths>`.
  Never `-a`; never a bare `-m` (PowerShell 5.1 splits it on embedded quotes).
- doccheck GREEN before any commit.

## 5 · Report

1. §1 counts: citations checked · RESOLVES · **DANGLING-DONOR-HAS-IT** · DANGLING-NOWHERE · STALE.
2. The DANGLING-DONOR-HAS-IT list, each with its citer and whether that citer is live work.
3. §2 genuine gaps only, with the evidence that they are absent here.
4. §3 findings, as proposals.
5. Your presence-control from §1's warning — the check that proves your "not found"s mean something.
6. What you could not determine. Say it plainly rather than rounding it to done.
