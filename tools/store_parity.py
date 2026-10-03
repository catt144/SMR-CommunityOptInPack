"""Prove the maintained store copies agree: Paradox block == metadata.lua description, Steam block == same words.

The store page body ships inside `metadata.lua` (`description` auto-fills both portals) and is
also kept as two paste blocks in the owner's upload file: the Paradox block (plain text, pasted
through `paradox_card.py`) and the Steam block (BBCode). The three must say the same thing.
This reads the two fenced blocks under their `#### 📋` headings in the source document, reads
`metadata.lua`, and checks:

  * Paradox block == metadata `description`, byte for byte (after Lua unescaping);
  * Steam block == Paradox block once BBCode tags and list markers are stripped, whitespace
    is collapsed and case is folded (the markup and heading case may differ, the words may not);
  * the "Short summary" block == `short_description`;
  * the "Change note" block == `last_changes`;
  * every ALL-CAPS section line in the Paradox block has an `[h2]` in the Steam block;
  * after the first publish, the as-published copies in `docs/agent/reports/STORE_CARD_LIVE.md`
    equal the source blocks (before it, the card holds no body and is reported INFO).

`--write-metadata` rewrites `description` and `last_changes` in `metadata.lua` FROM the blocks
(the blocks are the source; the Lua string is generated), then re-checks. It never touches a
version field, `short_description`, or any other line.

    python tools/store_parity.py                      check (default source: docs/UPLOAD_WORKFLOW.md)
    python tools/store_parity.py --source <file.md>   check against another document
    python tools/store_parity.py --write-metadata     regenerate metadata.lua from the blocks, then check

Exit 0 when every check passes, 1 otherwise. A zero-length block is a failure, never a pass.
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SOURCE = os.path.join(ROOT, "docs", "UPLOAD_WORKFLOW.md")
FALLBACK_SOURCE = os.path.join(ROOT, "docs", "agent", "reports", "STORE_AND_SITE_20261003.md")
METADATA = os.path.join(ROOT, "metadata.lua")
CARD = os.path.join(ROOT, "docs", "agent", "reports", "STORE_CARD_LIVE.md")

H_PARADOX = "#### 📋 Paradox Mods — description (plain text, paste as-is)"
H_STEAM = "#### 📋 Steam Workshop — description (BBCode, paste as-is)"
H_SUMMARY = "#### 📋 Short summary"
H_CHANGE = "#### 📋 Change note"

BBCODE_TAG = re.compile(r"\[/?(?:h[1-3]|b|i|u|url(?:=[^\]]*)?|list|olist)\]")
BULLET = re.compile(r"^(?:· |\[\*\]|\d+\. )", re.M)


def fenced_block(text, heading):
    i = text.find(heading)
    if i < 0:
        raise KeyError("heading not found: %s" % heading)
    a = text.index("```\n", i) + 4
    return text[a:text.index("\n```", a)]


def lua_unescape(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            out.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\", "'": "'"}.get(n, "\\" + n))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def lua_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def metadata_field(src, key):
    m = re.search(r"^\t'%s',\s*\"((?:\\.|[^\"\\])*)\",\s*$" % key, src, re.M)
    if not m:
        raise KeyError("metadata.lua has no single-line string field %r" % key)
    return m, lua_unescape(m.group(1))


def normalise(text, strip_bbcode):
    if strip_bbcode:
        text = BBCODE_TAG.sub("", text)
    text = BULLET.sub("", text)
    # Heading case is portal styling (Paradox bolds ALL-CAPS lines; Steam has [h2]), not words.
    return " ".join(text.split()).casefold()


def caps_sections(paradox):
    return [ln.strip() for ln in paradox.split("\n")
            if ln.strip() and ln.strip() == ln.strip().upper()
            and re.search(r"[A-Z]{3}", ln) and not re.match(r"^\d", ln.strip())]


def main(argv):
    source = DEFAULT_SOURCE
    write = False
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--source":
            source = os.path.abspath(args.pop(0))
        elif a == "--write-metadata":
            write = True
        else:
            print("unknown argument %r" % a)
            return 2
    if not os.path.isfile(source):
        if source == DEFAULT_SOURCE and os.path.isfile(FALLBACK_SOURCE):
            print("note: %s does not exist yet; reading the maintained blocks from %s"
                  % (os.path.relpath(DEFAULT_SOURCE, ROOT), os.path.relpath(FALLBACK_SOURCE, ROOT)))
            source = FALLBACK_SOURCE
        else:
            print("FAIL  source document missing: %s" % source)
            return 1

    doc = io.open(source, encoding="utf-8").read().replace("\r\n", "\n")
    blocks = {}
    for name, heading in (("paradox", H_PARADOX), ("steam", H_STEAM),
                          ("summary", H_SUMMARY), ("change", H_CHANGE)):
        try:
            blocks[name] = fenced_block(doc, heading).strip("\n")
        except KeyError as exc:
            print("FAIL  %s" % exc)
            return 1
        if not blocks[name].strip():
            print("FAIL  empty block under %s" % heading)
            return 1

    meta = io.open(METADATA, encoding="utf-8").read()
    if write:
        new = meta
        for key, value in (("description", blocks["paradox"]), ("last_changes", blocks["change"])):
            m, _ = metadata_field(new, key)
            new = new[:m.start(1)] + lua_escape(value) + new[m.end(1):]
        if new != meta:
            io.open(METADATA, "w", encoding="utf-8", newline="\n").write(new)
            print("wrote   metadata.lua description and last_changes from the blocks")
        else:
            print("note    metadata.lua already matched the blocks; nothing written")
        meta = new

    rows = []

    def check(ok, what, detail):
        rows.append(("PASS" if ok else "FAIL", what, detail))

    _, desc = metadata_field(meta, "description")
    _, short = metadata_field(meta, "short_description")
    _, last = metadata_field(meta, "last_changes")

    check(desc == blocks["paradox"], "Paradox block == metadata description (byte for byte)",
          "%d chars" % len(desc) if desc == blocks["paradox"]
          else "differ; first difference at char %d"
          % next((i for i, (a, b) in enumerate(zip(desc, blocks["paradox"])) if a != b),
                 min(len(desc), len(blocks["paradox"]))))
    p_norm = normalise(blocks["paradox"], strip_bbcode=False)
    s_norm = normalise(blocks["steam"], strip_bbcode=True)
    check(p_norm == s_norm, "Steam block == Paradox block, markup and list markers stripped",
          "%d words" % len(p_norm.split()) if p_norm == s_norm
          else "differ; first difference at char %d: paradox %r / steam %r"
          % ((lambda i: (i, p_norm[i:i + 40], s_norm[i:i + 40]))(
              next((i for i, (a, b) in enumerate(zip(p_norm, s_norm)) if a != b),
                   min(len(p_norm), len(s_norm))))))
    check(short == blocks["summary"], "Short summary block == short_description", "%d chars" % len(short))
    check(last == blocks["change"], "Change note block == last_changes", "%d chars" % len(last))
    # The store card is a third copy only after the first publish (POST_UPLOAD_CLOSE §4
    # appends the as-published blocks); before that it holds no body on purpose.
    if os.path.isfile(CARD):
        card = io.open(CARD, encoding="utf-8").read().replace("\r\n", "\n")
        has = lambda h: re.search("^" + re.escape(h) + r"\s*$", card, re.M) is not None
        if has(H_PARADOX) and has(H_STEAM):
            check(fenced_block(card, H_PARADOX).strip("\n") == blocks["paradox"],
                  "STORE_CARD_LIVE Paradox copy == source block", "matches", "differs")
            check(normalise(fenced_block(card, H_STEAM).strip("\n"), True) == s_norm,
                  "STORE_CARD_LIVE Steam copy == source words", "matches", "differs")
        else:
            rows.append(("INFO", "STORE_CARD_LIVE holds no body (pre-publication)", "not compared"))
    caps = caps_sections(blocks["paradox"])
    h2 = re.findall(r"\[h2\](.*?)\[/h2\]", blocks["steam"])
    check(len(caps) == len(h2) and len(caps) > 0,
          "every ALL-CAPS Paradox section has a Steam [h2]",
          "%d sections: %s" % (len(caps), ", ".join(caps)) if len(caps) == len(h2)
          else "%d caps lines vs %d [h2]: %s / %s" % (len(caps), len(h2), caps, h2))

    width = max(len(w) for _, w, _ in rows)
    print("STORE PARITY — %s vs metadata.lua" % os.path.relpath(source, ROOT))
    for v, w, d in rows:
        print("  %-4s  %-*s  %s" % (v, width, w, d))
    fails = [r for r in rows if r[0] == "FAIL"]
    print("\n  %d checked · %d FAIL" % (len(rows), len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
