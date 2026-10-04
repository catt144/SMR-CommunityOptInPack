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
  * the store card `docs/agent/reports/STORE_CARD_LIVE.md` is well formed for its declared
    state (see below).

STAGED versus LIVE. The source blocks are the STAGED copy: what the next upload will carry.
The card is the last CONFIRMED LIVE copy: what an owner-confirmed upload put on the portals.
They legitimately differ while an update is being prepared, so the default (preparation) run
never fails on that difference; it reports it. `--confirm-live` is the publication check the
close-out runs after it has copied the as-published bodies into the card: there the card's
current copy must equal the source blocks exactly.

The card declares `## State: PRE-PUBLICATION` or `## State: LIVE`. A pre-publication card
holds no body. A live card holds exactly one `## Current live copy` section with both body
blocks under their `#### 📋` headings; dated history sections elsewhere in the card are never
selected. A card with no state line, a live card missing a body, and a pre-publication card
holding one are all failures, never "pre-publication".

`--write-metadata` rewrites `description` and `last_changes` in `metadata.lua` FROM the blocks
(the blocks are the source; the Lua string is generated), then re-checks. It never touches a
version field, `short_description`, or any other line.

    python tools/store_parity.py                      check (default source: docs/UPLOAD_WORKFLOW.md)
    python tools/store_parity.py --source <file.md>   check against another document
    python tools/store_parity.py --write-metadata     regenerate metadata.lua from the blocks, then check
    python tools/store_parity.py --confirm-live       close-out: the card's current copy == the blocks
    python tools/store_parity.py --metadata <file>    check another tree's metadata.lua (the launch tree)
    python tools/store_parity.py --card <file>        check another card (fixtures)

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
METADATA = os.path.join(ROOT, "metadata.lua")
CARD = os.path.join(ROOT, "docs", "agent", "reports", "STORE_CARD_LIVE.md")

H_PARADOX = "#### 📋 Paradox Mods — description (plain text, paste as-is)"
H_STEAM = "#### 📋 Steam Workshop — description (BBCode, paste as-is)"
H_SUMMARY = "#### 📋 Short summary"
H_CHANGE = "#### 📋 Change note"
CARD_STATE = re.compile(r"^## State: (PRE-PUBLICATION|LIVE)\b", re.M)
CARD_CURRENT = "## Current live copy"

BBCODE_TAG = re.compile(r"\[/?(?:h[1-3]|b|i|u|url(?:=[^\]]*)?|list|olist)\]")
BULLET = re.compile(r"^(?:· |\[\*\]|\d+\. )", re.M)


def fenced_block(text, heading):
    i = text.find(heading)
    if i < 0:
        raise KeyError("heading not found: %s" % heading)
    # The block must belong to THIS heading: a fence found only past the next heading is
    # another block, and returning it would let a missing body pass as present.
    nxt = re.search(r"^#{1,6} ", text[i + len(heading):], re.M)
    end = i + len(heading) + nxt.start() if nxt else len(text)
    try:
        a = text.index("```\n", i, end) + 4
        return text[a:text.index("\n```", a, end + 4)]
    except ValueError:
        raise KeyError("no fenced block under heading: %s" % heading)


def card_copy(card):
    """-> (state, {"paradox": body, "steam": body} or None, problems).

    The current copy is selected by section, never by "first heading in the file": a later
    release replaces the `## Current live copy` section and moves the old bodies into a dated
    history section, which this never reads.
    """
    states = CARD_STATE.findall(card)
    if len(states) != 1:
        return None, None, ["card declares %d `## State:` lines; exactly one of "
                            "PRE-PUBLICATION / LIVE is required" % len(states)]
    state = states[0]
    sections = re.split(r"^(?=## )", card, flags=re.M)
    current = [sec for sec in sections if sec.startswith(CARD_CURRENT)]
    if state == "PRE-PUBLICATION":
        bad = []
        if current:
            bad.append("pre-publication card holds a `%s` section" % CARD_CURRENT)
        if any(re.search("^" + re.escape(h) + r"\s*$", card, re.M) for h in (H_PARADOX, H_STEAM)):
            bad.append("pre-publication card holds a body heading")
        return state, None, bad
    if len(current) != 1:
        return state, None, ["live card holds %d `%s` sections; exactly one is required"
                             % (len(current), CARD_CURRENT)]
    bodies, bad = {}, []
    for name, heading in (("paradox", H_PARADOX), ("steam", H_STEAM)):
        n = len(re.findall("^" + re.escape(heading) + r"\s*$", current[0], re.M))
        if n != 1:
            bad.append("current live copy holds %d `%s` headings; exactly one is required"
                       % (n, heading))
            continue
        try:
            bodies[name] = fenced_block(current[0], heading).strip("\n")
        except KeyError:
            bad.append("no fenced block under `%s`" % heading)
            continue
        if not bodies[name].strip():
            bad.append("empty block under `%s`" % heading)
    return state, (None if bad else bodies), bad


def shown(path):
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:          # another drive (a fixture, or the launch tree)
        return path


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
    metadata_path = METADATA
    card_path = CARD
    write = False
    confirm_live = False
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--source":
            source = os.path.abspath(args.pop(0))
        elif a == "--write-metadata":
            write = True
        elif a == "--confirm-live":
            confirm_live = True
        elif a == "--metadata":
            metadata_path = os.path.abspath(args.pop(0))
        elif a == "--card":
            card_path = os.path.abspath(args.pop(0))
        else:
            print("unknown argument %r" % a)
            return 2
    if not os.path.isfile(source):
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

    meta = io.open(metadata_path, encoding="utf-8").read()
    if write:
        new = meta
        for key, value in (("description", blocks["paradox"]), ("last_changes", blocks["change"])):
            m, _ = metadata_field(new, key)
            new = new[:m.start(1)] + lua_escape(value) + new[m.end(1):]
        if new != meta:
            io.open(metadata_path, "w", encoding="utf-8", newline="\n").write(new)
            print("wrote   metadata.lua description and last_changes from the blocks")
        else:
            print("note    metadata.lua already matched the blocks; nothing written")
        meta = new

    rows = []

    def check(ok, what, detail, bad_detail=None):
        rows.append(("PASS" if ok else "FAIL", what,
                     detail if ok or bad_detail is None else bad_detail))

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
    # The card is the last CONFIRMED LIVE copy; the blocks are the STAGED copy (docstring).
    if not os.path.isfile(card_path):
        check(False, "store card exists", "", "missing: %s" % card_path)
    else:
        card = io.open(card_path, encoding="utf-8").read().replace("\r\n", "\n")
        state, live, problems = card_copy(card)
        check(not problems, "store card is well formed for its declared state",
              "State: %s" % state, "; ".join(problems))
        if confirm_live:
            if live is None:
                check(False, "--confirm-live: card holds the current live copy", "",
                      "no usable live copy (State: %s)" % state)
            else:
                for name in ("paradox", "steam"):
                    check(live[name] == blocks[name],
                          "--confirm-live: card %s copy == source block (byte for byte)" % name,
                          "%d chars" % len(live[name]),
                          "differs; first difference at char %d"
                          % next((i for i, (x, y) in enumerate(zip(live[name], blocks[name]))
                                  if x != y), min(len(live[name]), len(blocks[name]))))
        elif live is not None:
            same = all(live[n] == blocks[n] for n in ("paradox", "steam"))
            rows.append(("INFO", "staged copy vs confirmed live copy",
                         "equal: nothing new is staged for the store body" if same
                         else "DIFFER: an update to the store body is staged, not yet live"))
        elif not problems:
            rows.append(("INFO", "store card holds no body (pre-publication)", "not compared"))
    caps = caps_sections(blocks["paradox"])
    h2 = re.findall(r"\[h2\](.*?)\[/h2\]", blocks["steam"])
    check(len(caps) == len(h2) and len(caps) > 0,
          "every ALL-CAPS Paradox section has a Steam [h2]",
          "%d sections: %s" % (len(caps), ", ".join(caps)) if len(caps) == len(h2)
          else "%d caps lines vs %d [h2]: %s / %s" % (len(caps), len(h2), caps, h2))

    width = max(len(w) for _, w, _ in rows)
    print("STORE PARITY — %s vs %s%s" % (shown(source), shown(metadata_path),
                                         "  [--confirm-live]" if confirm_live else ""))
    for v, w, d in rows:
        print("  %-4s  %-*s  %s" % (v, width, w, d))
    fails = [r for r in rows if r[0] == "FAIL"]
    print("\n  %d checked · %d FAIL" % (len(rows), len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
