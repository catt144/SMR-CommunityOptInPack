# Provenance: ported from SMR-BugFixPack @ 56d72579 on 2026-10-03; adapted: --source, missing-file message.
"""Open the Paradox store description as a formatted page, ready to copy.

The Paradox Mods page stores its description as HTML, so the plain text the
upload fills in arrives with no heading, no bold and no line breaks. This reads
the Paradox block from a source file (`--source`, default
docs/UPLOAD_WORKFLOW.md) and opens it in the browser in the owner's page format
(2026-09-19): the first line as the one heading, each ALL-CAPS section line in
bold, and every other line exactly as written, line breaks and blank lines
included. No bold inside the paragraphs and no font of its own, so the paste
takes the editor's font. Select all, copy, paste into the Paradox editor.

The block is the fenced one under the heading
"#### 📋 Paradox Mods — description (plain text, paste as-is)". Nothing is
stored: the page is rebuilt from the source on every run, so it cannot drift
from the maintained block.

    python tools/paradox_card.py                    build and open the page
    python tools/paradox_card.py --check            build only; print the headings
    python tools/paradox_card.py --source PATH      read the block from PATH

Exit 1 when the source file does not exist.
"""
import argparse
import html
import io
import os
import re
import sys
import tempfile
import webbrowser

# The report tools print the same unicode vocabulary as the rest of the
# project's tooling; a cp1252 console would die on it rather than on a finding.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SOURCE = os.path.join(ROOT, "docs", "UPLOAD_WORKFLOW.md")
INTERIM_SOURCE = "docs/agent/reports/STORE_AND_SITE_20261003.md"
PARADOX_HEADING = "#### 📋 Paradox Mods — description (plain text, paste as-is)"
URL_RE = re.compile(r"https?://\S+")


def fenced_block(text, heading):
    i = text.index(heading)
    a = text.index("```\n", i) + 4
    return text[a:text.index("\n```", a)]


def is_section(line):
    """A line of only upper-case letters, spaces and punctuation, >= 3 letters."""
    s = line.strip()
    return s == s.upper() and re.search(r"[A-Z]{3}", s) is not None


def build(source):
    text = io.open(source, encoding="utf-8").read().replace("\r\n", "\n")
    plain = fenced_block(text, PARADOX_HEADING)
    lines = plain.split("\n")
    body, sections = [f"<h3>{html.escape(lines[0].strip())}</h3>"], []
    # One paragraph per source line, an empty one per blank line: the same shape
    # as pressing Enter at the end of every line in the editor.
    for line in lines[1:]:
        if not line.strip():
            body.append("<p><br></p>")
        elif is_section(line):
            sections.append(line.strip())
            body.append(f"<p><strong>{html.escape(line.strip())}</strong></p>")
        else:
            text = URL_RE.sub(lambda m: f'<a href="{m.group(0)}">{m.group(0)}</a>',
                              html.escape(line.rstrip()))
            body.append(f"<p>{text}</p>")
    page = ("<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Paradox description</title></head><body>"
            + "\n".join(body) + "</body></html>")
    return page, lines[0].strip(), sections


def main():
    ap = argparse.ArgumentParser(description="Open the Paradox store description as a formatted page.")
    ap.add_argument("--check", action="store_true", help="build only; print the headings")
    ap.add_argument("--source", metavar="PATH", default=None,
                    help="file holding the Paradox block (default docs/UPLOAD_WORKFLOW.md)")
    args = ap.parse_args()
    source = os.path.abspath(args.source) if args.source else DEFAULT_SOURCE
    if not os.path.isfile(source):
        print(f"source not found: {source}")
        if not args.source:
            print("The default source is docs/UPLOAD_WORKFLOW.md, which this repo does not have yet.")
            print(f"The maintained block currently lives in {INTERIM_SOURCE}; pass it with --source.")
        sys.exit(1)
    page, title, sections = build(source)
    print("heading:", title)
    print("bold section lines:", ", ".join(sections))
    if args.check:
        return
    path = os.path.join(tempfile.gettempdir(), "smr_paradox_description.html")
    io.open(path, "w", encoding="utf-8").write(page)
    print("opened", path)
    print("In the browser: Ctrl+A, Ctrl+C. In the Paradox editor: select all, paste.")
    webbrowser.open("file:///" + path.replace("\\", "/"))


if __name__ == "__main__":
    main()
