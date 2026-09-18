---
kind: "preamble"
source: "docs/agent/ENGINE_FACTS.md, split 2026-08-03 by tools/split_facts.py"
---
# ENGINE_FACTS.md preamble — byte-preserved

The 8 lines below the `---` opened `docs/agent/ENGINE_FACTS.md` before it was split into
one file per fact on 2026-08-03. They are preserved exactly; the facts
themselves are `EF-###.md` in this folder and `INDEX.md` lists them.

⭐ **COPIED WHOLE into SMR-OptInPack on 2026-08-12** (chain `split-optins`,
prompt 3) from `SMR-BugFixPack` @ `33d69f5` — all 53 facts, this preamble and
the generated `INDEX.md`, byte-for-byte. Engine facts describe the GAME, so
both mods need every one of them. **The two copies diverge from that date
on** (chain rule 7): a fact learned in one repo does not appear in the other
until someone carries it across, and `updated:`/`verified:` dates older than
2026-08-12 belong to the donor's history. Declared local adaptations and the
last donor sync are in `tools/sync_from_fixpack.py`.

⚠️ **RE-SYNCED @ `bec2e06` (68 files, 2026-08-31) and @ `e6ec192` (107 files,
2026-09-17).** A re-sync is a **straight overwrite** of every `EF-*.md` from the fix
pack: the only local adaptation is `EF-062`'s `FUTURE_IDEAS` pointer, and it must be
re-applied afterwards. ⛔ **`EF-` ids are allocated by the fix pack** — file a new fact
there, then mirror it here at the same id. Run `python tools/doccheck.py --regen` after
any sync, and `--emit-fingerprint` to see which `derived_at:` groups still describe the
installed game build.

---

# Engine Facts — hard-won, do not re-derive

**Sole authoritative home** for the engine behaviors this project has proven
(extracted verbatim from STATUS.md "Key technical facts", audit remediation
3.2, 2026-07-29 — additions go HERE, with a date). Read this before writing or
reviewing any fix: several of these behaviors are the opposite of what the
code suggests.
