# Sync the entry file, the chain method and the skills to the fix pack's text

**Authored 2026-09-17 at `990281c`** by the fix-pack coordinator seat.

```sh
git log --oneline -8 && git pull && python tools/doccheck.py | tail -1
git diff --stat 990281c..HEAD -- CLAUDE.md docs/agent/support/CHAIN_METHOD.md .claude/skills/
```

## Authority — settled

⚖️ **Owner, 2026-09-17:** this repo standardises on the fix pack (`C:\Dev\SMR-BugFixPack`), which it
was forked from on 2026-08-12 — *"the same rules and structure there. The same overall workflow and
feel."* The feel is carried by the always-loaded entry file, the `Must_Read_Header` tiering, the five
skills, and the trust classes with status-as-pull. **They should be the same text in both repos,
except where a repo's own document names or genuinely mod-specific content appear.** The rules
blocks are already mirrored (`38b4e7c`, `990281c`); this job is everything around them.

⚖️ **OI-09:** agent-facing documents may be machine-tuned hard; content already recorded elsewhere is
deleted, not re-archived. Retire silently.

## End state — in this order; if budget runs out, drop 3 first

1. **`CLAUDE.md` prose** (everything outside the `<!-- RULES -->` block) takes the fix pack's
   `CLAUDE.md` prose, with this repo's names substituted. Three known defects it must not carry
   forward: a sentence calling `support/` *"authority, unlike `reports/`"*, which contradicts the
   trust-class rule; *"duties are in the header above"* for the prompt map, whose rule lives in
   `prompts/README.md`; and nothing now tells a reader that a decision binding the fix pack goes to
   the fix pack's checklist — keep that routing in one sentence, since it is genuinely this repo's.
   Before rewriting, list every obligation the current prose carries and give each a home, a
   rule it duplicates, or a cut under the `rule-placement` test; put that list in the commit message.
   Then `python tools/doccheck.py --regen` so `AGENTS.md` follows.
2. **`docs/agent/support/CHAIN_METHOD.md`** becomes the fix pack's current file, verbatim. This copy
   is an older, longer version that drifted (the fix pack's is 135 lines, headed *"Chain method —
   building a multi-session effort"*). If this copy holds anything specific to this mod, list it
   and say where it went; general method it holds that the fix pack's lacks is a proposal to the fix
   pack, listed in your report, not kept here.
3. **The five skills** (`.claude/skills/`; `.agents/skills/` is generated): diff each against the fix
   pack's. Drift becomes the fix pack's text; genuinely mod-specific content (module freeze,
   both-configuration testing, toggle directions, the log token, the shared TestKit) stays. List
   each difference and its disposition.

## Scope

**In:** `CLAUDE.md`, `AGENTS.md` (by `--regen`), `docs/agent/support/CHAIN_METHOD.md`, `.claude/skills/`,
`.agents/skills/` (by `--regen`), and citations your edits break.
**Out:** every `<!-- RULES -->` block, `FIX_POLICY.md` (its own rebase brief may be running),
`DECISIONS_OWED.md`, `Code/`. Recheck `git status` before each write; another seat shares this tree.

## Stops

1. A fix-pack passage contradicts a live owner ruling here — keep this repo's text there, report it.
2. A skill difference you cannot classify as drift or mod-specific — leave it and list it.

## Do not claim

- ❌ *"Now identical to the fix pack."* ✅ the diff against the fix pack's file after your edit, with
  every remaining difference named and justified.

## Lifecycle

One-off. `git rm` this file and delete its row in `docs/agent/prompts/README.md` in the commit that
lands the result.
