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
2026-08-12 belong to the donor's history. Provenance: `docs/agent/PROVENANCE.md`.

---

# Engine Facts — hard-won, do not re-derive

**Sole authoritative home** for the engine behaviors this project has proven
(extracted verbatim from STATUS.md "Key technical facts", audit remediation
3.2, 2026-07-29 — additions go HERE, with a date). Read this before writing or
reviewing any fix: several of these behaviors are the opposite of what the
code suggests.

