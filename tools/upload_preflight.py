"""Upload preflight — run every portal guard clause locally, before the sitting.

WHY THIS EXISTS (2026-08-17). The fix pack reached its upload sitting with no
`image` field in `metadata.lua`. `PDX_PrepareForUpload` (ModTools/Src/CommonLua/
Libs/Paradox/ParadoxMods.lua:38-42) fails on `mod.image == ""` BEFORE it packs
anything, so the afternoon would have ended at the first button — and nothing in
this project could have told anyone, because the checks live in the game.

The insight this tool is built on: **the upload's VALIDATION is separable from
its TRANSMISSION.** Every guard below is pure Lua reading `mod.*` fields, run
before any network call. So we can run all of them here, at zero cost, as often
as we like.

⛔ WHAT THIS TOOL CANNOT DO, and must never be read as doing:
  * It does not contact any portal. The Paradox login check
    (`ParadoxMods.lua:20-22`) is unrunnable here and is reported as UNCHECKABLE,
    never as passed.
  * A portal may enforce limits server-side that no local source states. Every
    character limit remains CHECK-AT-PASTE (RELEASE_PORTAL_PREP.md §3).
  * Passing here means "the game's own pre-upload guards would not reject this",
    NOT "the upload will succeed".

Usage:  python tools/upload_preflight.py [mod_dir]      (default: repo root)
Exit:   0 = every checkable guard passed · 1 = at least one FAIL
"""
import os
import re
import sys

# The Windows console defaults to cp1252 here and this file speaks the same
# ⛔/✅ vocabulary as the rest of the project's tooling; without this the run
# dies on its own summary line rather than on any finding.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

# ── the constants the game itself uses ───────────────────────────────────────
STEAM_MAX_IMAGE = 1 * 1024 * 1024   # SteamWorkshop.lua:85
PDX_MAX_IMAGE = 2 * 1024 * 1024     # recorded limit; PDX enforces server-side
MOD_REQUIRED_LUA_REVISION = 350453  # Mod.lua:19
MOD_CONTENT_PATH = "Mod/"           # Mod.lua:6


def parse_metadata(path):
    """Extract the ModDef fields we need. The file is a generated PlaceObj
    table: one `'key', value,` pair per line at a single tab of indent."""
    src = open(path, encoding="utf-8").read()
    out = {}

    # scalars: strings (with escaped quotes), numbers, booleans
    for m in re.finditer(r"^\t'(\w+)',\s*(.+?),\s*$", src, re.M):
        key, raw = m.group(1), m.group(2).strip()
        if raw.startswith('"'):
            body = re.match(r'"((?:\\.|[^"\\])*)"', raw)
            if body:
                out[key] = body.group(1).replace('\\"', '"').replace("\\\\", "\\")
        elif raw in ("true", "false"):
            out[key] = raw == "true"
        elif re.fullmatch(r"-?\d+", raw):
            out[key] = int(raw)

    # list fields: 'key', { "a", "b", },
    for key in ("code", "ignore_files"):
        m = re.search(r"^\t'%s',\s*\{(.*?)^\t\},\s*$" % key, src, re.M | re.S)
        if m:
            out[key] = re.findall(r'"([^"]*)"', m.group(1))
    return out


def main():
    mod_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    meta_path = os.path.join(mod_dir, "metadata.lua")
    if not os.path.isfile(meta_path):
        print("FAIL  no metadata.lua at %s" % mod_dir)
        return 1

    md = parse_metadata(meta_path)
    rows = []   # (verdict, guard, detail)

    def check(cond, guard, ok_detail, bad_detail):
        rows.append(("PASS" if cond else "FAIL", guard, ok_detail if cond else bad_detail))

    def note(guard, detail, verdict="INFO"):
        rows.append((verdict, guard, detail))

    updating = bool(md.get("pdx_id")) or bool(md.get("PdxMod"))

    # ── Paradox Mods: PDX_PrepareForUpload, in source order ──────────────────
    note("PDX login", "cannot be checked without an account — the ONLY guard "
         "this tool cannot run (ParadoxMods.lua:20-22)", "UNCHECKABLE")
    for field, line in (("title", 24), ("short_description", 29),
                        ("description", 34), ("image", 39), ("lua_revision", 44)):
        val = md.get(field, "")
        check(val != "" and val is not None,
              "PDX `%s` non-empty (ParadoxMods.lua:%d)" % (field, line),
              "%d chars" % len(str(val)) if not isinstance(val, int) else str(val),
              "EMPTY OR MISSING — upload is rejected before packing")
    check(not (md.get("last_changes", "") == "" and updating),
          "PDX `last_changes` required when updating (ParadoxMods.lua:48)",
          "set" if md.get("last_changes") else "empty, but this is a FIRST upload — not required",
          "empty on an UPDATE — rejected")

    # ── the preview image, on disk ───────────────────────────────────────────
    image = md.get("image", "")
    if image:
        rel = image[len(MOD_CONTENT_PATH):] if image.startswith(MOD_CONTENT_PATH) else image
        rel = rel.split("/", 1)[1] if image.startswith(MOD_CONTENT_PATH) and "/" in rel else rel
        img_path = os.path.join(mod_dir, rel.replace("/", os.sep))
        exists = os.path.isfile(img_path)
        check(exists, "preview image resolves on disk",
              "%s" % rel, "path does not resolve: %s" % img_path)
        if exists:
            size = os.path.getsize(img_path)
            check(size <= STEAM_MAX_IMAGE,
                  "preview <= 1 MB (Steam hard limit, SteamWorkshop.lua:85-92)",
                  "%s bytes" % f"{size:,}",
                  "%s bytes — Steam REJECTS the upload" % f"{size:,}")
            check(size <= PDX_MAX_IMAGE, "preview <= 2 MB (recorded PDX limit)",
                  "%s bytes" % f"{size:,}", "%s bytes" % f"{size:,}")
        check(image.startswith(MOD_CONTENT_PATH),
              "image path is content-path form",
              "starts with %r, so FixRelativePaths leaves it alone (Mod.lua:577) "
              "and the mod stays CLEAN — no editor save, no version bump" % MOD_CONTENT_PATH,
              "not %r form: the editor may rewrite it in memory, dirty the mod, "
              "and a forced save bumps the version (Mod.lua:967)" % MOD_CONTENT_PATH)

    # ── screenshots, if any are ever added ───────────────────────────────────
    shots = [md[k] for k in ("screenshot1", "screenshot2", "screenshot3",
                             "screenshot4", "screenshot5") if md.get(k)]
    if not shots:
        note("screenshots", "none declared — allowed; the mod page will show only the preview")
    for s in shots:
        p = os.path.join(mod_dir, s.split("/", 2)[-1].replace("/", os.sep))
        sz = os.path.getsize(p) if os.path.isfile(p) else -1
        check(0 <= sz <= STEAM_MAX_IMAGE, "screenshot <= 1 MB: %s" % s,
              "%s bytes" % f"{sz:,}", "missing or over 1 MB (%s)" % sz)

    # ── version, and what a player actually sees ─────────────────────────────
    # ⛔ 2026-08-20: these three READ AS ABSENT once a real upload has happened.
    # `SaveDef` omits any property still at its default, and `version_minor`'s
    # default is 0 (`Mod.lua:265`) — so the forced save that publishes the mod
    # deletes the field, and the `None not in (...)` guard below used to drop BOTH
    # version notes silently. The tool went quiet on the version at the exact
    # moment the version stopped being obvious (Paradox 1.0.0 / Steam 1.0.2 out of
    # one sitting). Defaulting a missing value to 0 mirrors the engine's own
    # default and keeps the reporting alive; None is kept only for `version`
    # itself, whose absence would be a genuinely broken file.
    vmaj = md.get("version_major", 0) or 0
    vmin = md.get("version_minor", 0) or 0
    vrev = md.get("version")
    if vrev is not None:
        note("PackVersion a player sees", "%d.%d.%d  (version_major.version_minor.version)"
             % (vmaj, vmin, vrev))
        note("VersionDisplayName sent to PDX", "%r — the REVISION ALONE, not the full "
             "version (ParadoxMods.lua:156). Edit it on the portal page if it lets you."
             % str(vrev))
    check(md.get("lua_revision") == MOD_REQUIRED_LUA_REVISION,
          "lua_revision pinned to ModRequiredLuaRevision (Mod.lua:19)",
          str(md.get("lua_revision")),
          "%s != %d — an editor save would rewrite it (Mod.lua:966)"
          % (md.get("lua_revision"), MOD_REQUIRED_LUA_REVISION))

    # ── packaging: what actually ships ───────────────────────────────────────
    ignore = md.get("ignore_files", [])
    for pat in ("*/docs/*", "*/tools/*", "*CLAUDE.md", "*.git/*"):
        check(pat in ignore, "ignore_files carries %s" % pat, "present",
              "MISSING — that content would ship inside the player's download")

    code = md.get("code", [])
    on_disk = sorted(
        "Code/" + f for f in os.listdir(os.path.join(mod_dir, "Code"))
        if f.endswith(".lua")) if os.path.isdir(os.path.join(mod_dir, "Code")) else []
    check(sorted(code) == on_disk,
          "metadata `code` list matches Code/*.lua on disk",
          "%d files, exactly" % len(code),
          "MISMATCH — only listed files execute. missing from list: %s | listed but absent: %s"
          % (sorted(set(on_disk) - set(code)), sorted(set(code) - set(on_disk))))

    items_path = os.path.join(mod_dir, "items.lua")
    if os.path.isfile(items_path):
        # ⛔ 2026-08-19 (pre-launch sweep, link 6): this guard used to count the
        # bare string "ModItemCode" over the whole file, which counts the
        # header COMMENT that explains the guard. items.lua then read 76
        # against a 76-entry `code` list while holding only 75 real entries —
        # two errors cancelling, and the one guard between a missing module and
        # the store said PASS. Parse the entries, and compare the ORDER too:
        # `ModDef:UpdateCode` (Mod.lua:816-840) rebuilds `code` by walking the
        # items in index order and nothing else, so both membership and
        # sequence are what a SaveWholeMod would write.
        items_text = open(items_path, encoding="utf-8").read()
        item_files = [
            m.group(1) for m in re.finditer(
                r"PlaceObj\(\s*'ModItemCode'\s*,\s*\{.*?'CodeFileName'\s*,\s*\"([^\"]+)\"",
                items_text, re.S)]
        missing = [c for c in code if c not in item_files]
        extra = [c for c in item_files if c not in code]
        order_ok = item_files == list(code)
        check(order_ok,
              "items.lua ModItemCode list == metadata `code`, same files, same order",
              "%d entries, in order" % len(item_files),
              "%d ModItemCode vs %d code entries — a SaveWholeMod REBUILDS `code` "
              "from these items alone (Mod.lua:816-840, called at :973), and both "
              "portals force one on a first upload (Steam BEFORE packing, "
              "SteamWorkshop.lua:17-22). in `code` but no item (WOULD STOP LOADING): "
              "%s | item with no `code` line: %s%s"
              % (len(item_files), len(code), missing or "none", extra or "none",
                 "" if (missing or extra) else " | same set, DIFFERENT ORDER — a "
                 "round-trip would reorder the load sequence"))

    # ── report ───────────────────────────────────────────────────────────────
    width = max(len(g) for _, g, _ in rows)
    print("UPLOAD PREFLIGHT — %s" % mod_dir)
    print("  mod id: %s   title: %r\n" % (md.get("id"), md.get("title")))
    for verdict, guard, detail in rows:
        print("  %-11s %-*s  %s" % (verdict, width, guard, detail))

    fails = [r for r in rows if r[0] == "FAIL"]
    unchecked = [r for r in rows if r[0] == "UNCHECKABLE"]
    print("\n  %d checked · %d FAIL · %d UNCHECKABLE"
          % (len(rows) - len(unchecked), len(fails), len(unchecked)))
    if fails:
        print("\n⛔ DO NOT OPEN THE MOD EDITOR until these are fixed.")
    else:
        print("\n✅ Every guard this tool can run would pass. ⛔ This is NOT "
              "'the upload will succeed' — the login guard is unrunnable here and "
              "portal character limits stay check-at-paste.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
