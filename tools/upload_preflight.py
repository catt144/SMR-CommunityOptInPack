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

from pack_predict import predict

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
# The whole shipped pack is ~0.6 MB. A pack an order of magnitude past that is
# carrying something that is not the mod (2026-09-16: 1.2 GB of transcripts).
# ⚖️ OI-18 (owner, 2026-09-21 / 2026-10-01): this mod ships models, so the
# ceiling binds everything EXCEPT the asset files below. The transcript guard
# survives for what it was for; texture size is a look decision (train spec §9,
# grep `OUR OWN GUARD`).
PACK_MAX_BYTES = 5 * 1024 * 1024

# What a shipped model is made of: folder, extension. One level deep each; the
# `.entjson`/`.mtljson` files name their meshes and materials by full
# `Mod/<id>/...` path (ModItem.lua:671-711 on 1.1.1.406343), so the folders are
# what those paths spell. Fallbacks are found by name beside their texture.
ASSET_DIRS = (("Entities/", ".entjson"), ("Meshes/", ".hgrm"),
              ("Materials/", ".mtljson"), ("Textures/", ".dds"),
              ("Fallbacks/Textures/", ".dds"), ("UI/", ".png"))
MOD_PATH_RE = re.compile(r"Mod/([A-Za-z0-9_]+)/([^\"'\s\]\)]+)")


def is_asset(rel):
    return any(rel.startswith(d) and rel.endswith(e) and "/" not in rel[len(d):]
               for d, e in ASSET_DIRS)


def is_generated(rel):
    return rel.endswith(".generated.lua")


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
    for key in ("code", "ignore_files", "entities"):
        m = re.search(r"^\t'%s',\s*\{(.*?)^\t\},\s*$" % key, src, re.M | re.S)
        if m:
            out[key] = re.findall(r'"([^"]*)"', m.group(1))
    return out


def asset_checks(mod_dir, md, packed, check, note):
    """OI-18: the shipped models, templates and icons resolve inside THIS mod.

    Every `Mod/<id>/...` path the packed text names must name this mod's id and
    a file the pack carries; every asset the pack carries must be named by
    something, so no dead texture ships; the `entities` list, the Entities/
    folder and SourceData/ArtSpec-mod.lua must agree, because the portals'
    forced SaveDef rebuilds `entities` from that file's EntitySpec items alone
    (`ModDef:UpdateEntities`, Mod.lua:816-827) and the packer skips SourceData/.
    """
    mod_id = md.get("id", "")
    packed_set = {rel for rel, _ in packed}
    assets = sorted(r for r in packed_set if is_asset(r))
    entities = md.get("entities") or []
    templates = sorted(r for r in packed_set
                       if r.startswith("Data/BuildingTemplate/") and r.endswith(".lua"))
    if not assets and not entities and not templates:
        note("model assets", "none — nothing to resolve")
        return

    named, foreign, unresolved = set(), [], []
    for rel in sorted(packed_set):
        if not rel.endswith((".entjson", ".mtljson", ".lua")) or rel == "metadata.lua":
            continue
        text = open(os.path.join(mod_dir, rel.replace("/", os.sep)),
                    encoding="utf-8", errors="replace").read()
        for m in MOD_PATH_RE.finditer(text):
            target_id, target = m.group(1), m.group(2)
            if target_id != mod_id:
                foreign.append("%s -> Mod/%s/%s" % (rel, target_id, target))
            elif target not in packed_set:
                unresolved.append("%s -> %s" % (rel, target))
            else:
                named.add(target)
    check(not foreign, "every Mod/<id>/ path names this mod (%s)" % mod_id,
          "%d distinct target(s)" % len(named),
          "%d path(s) name another mod, e.g. %s" % (len(foreign), foreign[:3]))
    check(not unresolved, "every Mod/%s/ path resolves to a packed file" % mod_id,
          "%d distinct target(s)" % len(named),
          "%d unresolved, e.g. %s" % (len(unresolved), unresolved[:3]))

    textures = {os.path.basename(r) for r in assets
                if r.startswith("Textures/") and r in named}
    unused = [r for r in assets
              if not r.startswith(("Entities/", "Fallbacks/")) and r not in named]
    unused += [r for r in assets if r.startswith("Fallbacks/Textures/")
               and os.path.basename(r) not in textures]
    check(not unused, "every packed asset is used",
          "%d asset file(s), each named by a path in the pack (fallbacks by "
          "their texture's name)" % len(assets),
          "%d unused file(s) would ship: %s" % (len(unused), unused[:6]))

    on_disk_ents = sorted(r[len("Entities/"):-len(".entjson")]
                          for r in assets if r.startswith("Entities/"))
    check(sorted(entities) == on_disk_ents,
          "metadata `entities` == Entities/*.entjson",
          "%d entities" % len(entities),
          "listed %s, packed %s" % (sorted(entities), on_disk_ents))
    art = os.path.join(mod_dir, "SourceData", "ArtSpec-mod.lua")
    if entities and not os.path.isfile(art):
        check(False, "SourceData/ArtSpec-mod.lua names every entity", "",
              "missing — the portals' forced SaveDef would empty `entities` "
              "and no model would load (Mod.lua:816-827)")
    elif entities:
        art_text = open(art, encoding="utf-8", errors="replace").read()
        spec_ids = sorted(re.findall(r"^\s*id = \"([^\"]+)\",", art_text, re.M))
        save_ins = set(re.findall(r"save_in = \"([^\"]+)\"", art_text))
        check(spec_ids == sorted(entities),
              "SourceData/ArtSpec-mod.lua names every entity",
              "%d EntitySpec item(s) = `entities`" % len(spec_ids),
              "EntitySpec %s vs `entities` %s — a SaveDef rebuilds the list "
              "from these (Mod.lua:816-827)" % (spec_ids, sorted(entities)))
        check(save_ins <= {"Mod/" + mod_id},
              "ArtSpec save_in is this mod", "Mod/%s" % mod_id,
              "save_in %s — the item binds to another mod" % sorted(save_ins))

    for rel in templates:
        tid = rel[len("Data/BuildingTemplate/"):-len(".lua")]
        text = open(os.path.join(mod_dir, rel.replace("/", os.sep)),
                    encoding="utf-8", errors="replace").read()
        save_in = re.search(r"'SaveIn',\s*\"([^\"]*)\"", text)
        check(bool(save_in) and save_in.group(1) == "Mod/" + mod_id,
              "template %s SaveIn is this mod" % tid, "Mod/%s" % mod_id,
              "%s — a SaveIn on another id binds the preset there "
              "(ModItem.lua:2484-2494, Mod.lua:666)"
              % (save_in.group(1) if save_in else "no SaveIn"))
        gen = [c for c in md.get("code", [])
               if c.endswith("BuildingTemplate/%s.generated.lua" % tid)]
        check(bool(gen), "template %s has its generated class in `code`" % tid,
              gen[0] if gen else "",
              "no Code/**/BuildingTemplate/%s.generated.lua listed — the build "
              "menu reads the class (Building.lua:2695-2707)" % tid)


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
    for pat in ("*/docs/*", "*/tools/*", "*CLAUDE.md", "*AGENTS.md", "*.git/*"):
        check(pat in ignore, "ignore_files carries %s" % pat, "present",
              "MISSING — that content would ship inside the player's download")

    # ⛔ 2026-09-16: a junction to the user's Claude projects folder sat in the
    # mod folder, outside every ignore pattern. The packer walks through
    # junctions, so ~1.2 GB of private transcripts entered the pack list; the
    # pack failed only because of its size, and nothing here looked. These
    # three guards read what the packer will COLLECT, with the live patterns.
    packed, _ignored, links = predict(mod_dir, ignore)
    live_links = [rel for rel, pat in links if not pat]
    check(not live_links,
          "no junction/symlink whose contents would be packed",
          "%d link(s), all under an ignore pattern" % len(links) if links else "none",
          "%s — the packer walks through it; move it out of the mod folder or add "
          "an ignore_files pattern" % live_links)
    image_name = os.path.basename(md.get("image") or "")
    stray = [rel for rel, _ in packed
             if not ((rel.startswith("Code/") and rel.endswith(".lua"))
                     or (rel.startswith("Data/") and rel.endswith(".lua"))
                     or is_asset(rel)
                     or rel in ("metadata.lua", "items.lua", "LICENSE", image_name))]
    check(not stray,
          "predicted pack holds only shipping files",
          "%d files: Code/**/*.lua, Data/**/*.lua, model assets, metadata.lua, "
          "items.lua, LICENSE, %s" % (len(packed), image_name or "(no image)"),
          "%d NON-SHIPPING file(s) would upload to both stores, e.g. %s"
          % (len(stray), stray[:5]))
    asset_bytes = sum(size for rel, size in packed if is_asset(rel))
    pack_bytes = sum(size for rel, size in packed if not is_asset(rel))
    check(pack_bytes <= PACK_MAX_BYTES,
          "predicted pack size <= %d MB, model assets aside (OI-18)"
          % (PACK_MAX_BYTES // (1024 * 1024)),
          "%s bytes" % format(pack_bytes, ","),
          "%s bytes — something other than the mod is in the folder" % format(pack_bytes, ","))
    if asset_bytes:
        note("model assets (raw, before the pack's compression)",
             "%s bytes in %d file(s); no ceiling, owner OI-18"
             % (format(asset_bytes, ","), len([r for r, _ in packed if is_asset(r)])))
    asset_checks(mod_dir, md, packed, check, note)

    code = md.get("code", [])
    code_root = os.path.join(mod_dir, "Code")
    on_disk = sorted(
        os.path.relpath(os.path.join(root, f), mod_dir).replace(os.sep, "/")
        for root, _dirs, files in os.walk(code_root)
        for f in files if f.endswith(".lua")) if os.path.isdir(code_root) else []
    check(sorted(code) == on_disk,
          "metadata `code` list matches Code/**/*.lua on disk",
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
        # Generated files (a BuildingTemplate's class, `_EntityData`) come from
        # Data/ and SourceData/ items, not ModItemCode. With no ModItemRef
        # lines those items are appended after items.lua's own, in handle
        # order (`ModDef:ResolveModItemRefs`, Mod.lua:535-556 on 1.1.1.406343),
        # so a SaveDef puts every generated file after every hand file.
        hand = [c for c in code if not is_generated(c)]
        generated = [c for c in code if is_generated(c)]
        if generated:
            first_gen = min(code.index(g) for g in generated)
            check(first_gen >= len(hand),
                  "generated code files listed after every hand-written one",
                  "%d generated file(s) last, as a SaveDef appends them" % len(generated),
                  "a generated file precedes a hand file — a SaveDef would move it "
                  "(Mod.lua:535-556, :829-853)")
        missing = [c for c in hand if c not in item_files]
        extra = [c for c in item_files if c not in code]
        order_ok = item_files == hand
        check(order_ok,
              "items.lua ModItemCode list == metadata `code` (generated files aside), "
              "same files, same order",
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
