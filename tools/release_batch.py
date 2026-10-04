#!/usr/bin/env python3
"""Pin one release batch: the launch tree it uploads from, each portal's progress, and its close.

WHY THIS EXISTS (final launch audit 2026-10-03, F1 and F4). The Mod Editor packs every file
under the mod folder, so whatever sits in the working repo ships: held work, a peer's
uncommitted hunks, a tracked module the owner ruled out of this release. And the release
procedure could not tell a new batch from a half-done upload, a listing id from a successful
upload, or its own Pending entries from a later one. This tool makes those states data.

THE LAUNCH TREE. `begin` exports a pinned commit into a sibling folder, minus the HELD_OUT
paths, plus the shipping folders git ignores (UNTRACKED_SHIPPING), and records a sha256 per
member. The owner points the game's Mods link at that folder, uploads from it, and points the
link back (`link launch` / `link repo`). The repo's own `metadata.lua` and `items.lua` are
never opened by the editor, so their comments are never stripped; the close-out copies the
writeback FIELDS across (`writeback`).

WHAT THE GAME DOES, from the archived 1.1.1.406343 source (source claims, not portal
observations): each upload builds its own package — `UploadMod` runs prepare, then
`CreatePackageForUpload`, then upload (`CommonLua/Classes/GedModEditor.lua:770`), and
`CreatePackageForUpload` first deletes the previous one (`:678`). A first Steam upload
allocates the item id and saves the whole mod BEFORE packaging
(`CommonLua/Platforms/steam/SteamWorkshop.lua:17-22`), so a `steam_id` proves a listing, not
an upload. Paradox writes `pdx_id`/`pdx_version` and saves only AFTER the publish call
succeeded (`CommonLua/Libs/Paradox/ParadoxMods.lua:171-177`). So the two portals never
receive "the same packed file", and `snapshot <portal>` copies each actual package and the
serializer's output out of the temp folder before the next upload deletes it.

    python tools/release_batch.py status              what state is the release in, and what is next
    python tools/release_batch.py assemble --out DIR  dry assembly of HEAD (no batch is opened)
    python tools/release_batch.py begin               pin a batch at HEAD and build the launch tree
    python tools/release_batch.py verify              launch tree vs its manifest, membership, held tokens
    python tools/release_batch.py link launch|repo    point the game's Mods link (owner runs this)
    python tools/release_batch.py snapshot paradox|steam   keep the package just uploaded + serializer output
    python tools/release_batch.py receipt paradox|steam uploaded|failed "<owner's words>"
    python tools/release_batch.py writeback           the fields the editor wrote, against the repo's copy
    python tools/release_batch.py drain               move THIS batch's Pending entries to the history
    python tools/release_batch.py mark writeback|tag <value>
    python tools/release_batch.py close               finish; refuses while a close step is owed
    python tools/release_batch.py abandon "<reason>"  drop a batch nothing was uploaded from

Exit 0 on success, 1 on a refusal or a failed check. Falsifier: `tools/release_selftest.py`.
"""
import datetime
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pack_predict  # noqa: E402
import upload_preflight  # noqa: E402

# Tracked paths that exist in this repo and are NOT part of the next upload, each with the
# ruling that holds it out. A path listed here must exist at the batch's base commit: when
# the work leaves the tree (or ships), `begin` fails until its row is removed, so this list
# cannot go stale quietly.
HELD_OUT = {
    # (none) The Arboretum (D19, owner OI-50) was the first entry; it left this mod's tree
    # for staging/ in 78eed20, which the ignore list already keeps out of every pack.
}
# Words that must not occur anywhere in the launch tree: work the owner ruled out of the
# shipping set, whether HELD_OUT removes it or it lives outside the tree (staging/).
HELD_TOKENS = ("Arboretum",)
# Shipping folders git ignores (.gitignore: the Mod Editor writes the textures on import).
# They are copied from the working tree and have no commit identity; the manifest hashes them.
UNTRACKED_SHIPPING = ("Textures", "Fallbacks")
# Not packed, but the editor reads them at upload: SaveDef rebuilds `entities` from
# SourceData/ArtSpec-mod.lua, and the uploaders read the gallery files.
EDITOR_INPUTS = ("SourceData/", "store_screenshots/")
# What the editor's upload save rewrites. Any other change in the launch tree is a finding.
EDITOR_OWNED = ("metadata.lua", "items.lua")
PORTALS = ("paradox", "steam")
WRITEBACK_FIELDS = ("version_major", "version_minor", "version", "pdx_id", "pdx_version", "steam_id")
PENDING = re.compile(r"^### Pending · .*$", re.M)


class Ctx:
    """Every path the tool touches, so the selftest can run it against a scratch repo."""

    def __init__(self, repo=REPO, launch=None, pack=None, mods_link=None,
                 held_out=None, held_tokens=None, untracked=UNTRACKED_SHIPPING):
        self.repo = repo
        self.launch = launch or os.path.join(os.path.dirname(repo),
                                             os.path.basename(repo) + "-launch")
        local = os.environ.get("LOCALAPPDATA", "")
        self.pack = pack or os.path.join(local, "Temp", "Surviving Mars Relaunched",
                                         "ModUpload", "Pack", "ModContent.fpk")
        self.mods_link = mods_link or os.path.join(
            os.environ.get("APPDATA", ""), "Surviving Mars Relaunched", "Mods", "SMR-OptInPack")
        self.held_out = HELD_OUT if held_out is None else held_out
        self.held_tokens = HELD_TOKENS if held_tokens is None else held_tokens
        self.untracked = untracked
        self.state = os.path.join(repo, "docs", "agent", "support", "RELEASE_BATCH.json")
        self.outbox = os.path.join(repo, "docs", "agent", "prompts", "perma", "RELEASE_OUTBOX.md")
        self.history = os.path.join(repo, "docs", "archive", "RELEASE_HISTORY.md")
        self.snapshots = os.path.join(repo, "local", "release")

    def git(self, *args, binary=False):
        out = subprocess.run(("git",) + args, cwd=self.repo, capture_output=True, check=True).stdout
        return out if binary else out.decode("utf-8", "replace")


class Refuse(Exception):
    """A refusal with a reason; main() prints it and exits 1."""


# ── small helpers ────────────────────────────────────────────────────────────
def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_text(path):
    return io.open(path, encoding="utf-8").read().replace("\r\n", "\n")


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)


def today():
    return datetime.date.today().isoformat()


def load_state(ctx):
    if not os.path.isfile(ctx.state):
        return {"schema": 1, "batch": None, "closed": []}
    return json.loads(read_text(ctx.state))


def save_state(ctx, state):
    write_text(ctx.state, json.dumps(state, indent=1, ensure_ascii=False) + "\n")


def fields(metadata_path):
    md = upload_preflight.parse_metadata(metadata_path)
    return {k: md.get(k) for k in WRITEBACK_FIELDS}


def version_of(f):
    return "%s.%s.%s" % (f.get("version_major") or 0, f.get("version_minor") or 0,
                         f.get("version") if f.get("version") is not None else "?")


def pending_entries(outbox_text):
    """-> [(heading, whole entry text)] for each `### Pending · …` entry, in file order."""
    out = []
    for m in PENDING.finditer(outbox_text):
        nxt = re.search(r"^#{2,3} ", outbox_text[m.end():], re.M)
        end = m.end() + nxt.start() if nxt else len(outbox_text)
        out.append((m.group(0).strip(), outbox_text[m.start():end]))
    return out


# ── the launch tree ──────────────────────────────────────────────────────────
def launch_members(ctx, base):
    """Tracked paths at `base` that the launch tree carries, HELD_OUT removed."""
    tracked = ctx.git("ls-tree", "-r", "--name-only", "-z", base).split("\0")
    tracked = [t for t in tracked if t]
    absent = sorted(set(ctx.held_out) - set(tracked))
    if absent:
        raise Refuse("HELD_OUT names path(s) not tracked at %s: %s — the held work moved or "
                     "shipped; remove its HELD_OUT row(s) in tools/release_batch.py"
                     % (base[:7], absent))
    pats = [pack_predict.to_regex(p) for p in pack_predict.IGNORE]
    keep = []
    for rel in tracked:
        if rel in ctx.held_out:
            continue
        packed = not any(rx.match(pack_predict.CONTENT_PREFIX + rel) for rx in pats)
        if packed or rel.startswith(EDITOR_INPUTS):
            keep.append(rel)
    return keep


def assemble(ctx, base, out_dir):
    """Build the launch tree at out_dir from `base`. -> manifest {rel: {sha256, bytes, source}}."""
    if os.path.lexists(out_dir):
        marker = out_dir.rstrip("\\/") + ".manifest.json"
        if not os.path.isfile(marker):
            raise Refuse("%s exists and is not a launch tree this tool built (no %s); "
                         "move it away first" % (out_dir, os.path.basename(marker)))
        shutil.rmtree(out_dir)
    manifest = {}
    for rel in launch_members(ctx, base):
        data = ctx.git("cat-file", "blob", "%s:%s" % (base, rel), binary=True)
        dest = os.path.join(out_dir, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(data)
        manifest[rel] = {"sha256": sha256(data), "bytes": len(data), "source": "commit"}
    for top in ctx.untracked:
        src_top = os.path.join(ctx.repo, top)
        for dirpath, _dirs, files in os.walk(src_top):
            for fn in sorted(files):
                src = os.path.join(dirpath, fn)
                rel = os.path.relpath(src, ctx.repo).replace(os.sep, "/")
                data = open(src, "rb").read()
                dest = os.path.join(out_dir, rel.replace("/", os.sep))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                open(dest, "wb").write(data)
                manifest[rel] = {"sha256": sha256(data), "bytes": len(data),
                                 "source": "working tree (git-ignored, no commit identity)"}
    write_text(out_dir.rstrip("\\/") + ".manifest.json",
               json.dumps({"base": base, "built": today(), "held_out": ctx.held_out,
                           "members": manifest}, indent=1) + "\n")
    return manifest


def tree_report(ctx, tree, manifest):
    """Compare a launch tree with its manifest and read its membership. -> dict."""
    on_disk = {}
    for dirpath, _dirs, files in os.walk(tree):
        for fn in files:
            p = os.path.join(dirpath, fn)
            on_disk[os.path.relpath(p, tree).replace(os.sep, "/")] = p
    changed = sorted(r for r in manifest if r in on_disk
                     and sha256(open(on_disk[r], "rb").read()) != manifest[r]["sha256"])
    missing = sorted(set(manifest) - set(on_disk))
    extra = sorted(set(on_disk) - set(manifest))
    packed, _ignored, links = pack_predict.predict(tree)
    token_hits = []
    for tok in ctx.held_tokens:
        for rel, p in sorted(on_disk.items()):
            if tok.lower() in rel.lower():
                token_hits.append("%s (path)" % rel)
            elif rel.endswith((".lua", ".entjson", ".mtljson", ".md", ".txt")) or "." not in rel:
                if tok.encode() in open(p, "rb").read():
                    token_hits.append("%s (contents: %s)" % (rel, tok))
    modules = []
    code_dir = os.path.join(tree, "Code")
    for fn in sorted(os.listdir(code_dir)) if os.path.isdir(code_dir) else []:
        if fn.startswith("Opt_") and fn.endswith(".lua"):
            if re.search(r"SMROptInPack\.Register\(", read_text(os.path.join(code_dir, fn))):
                modules.append(fn[len("Opt_"):-len(".lua")])
    items = os.path.join(tree, "items.lua")
    options = re.findall(r"PlaceObj\('ModItemOption\w+',\s*\{\s*'name',\s*\"([^\"]+)\"",
                         read_text(items)) if os.path.isfile(items) else []
    return {"changed": changed, "missing": missing, "extra": extra,
            "packed": [r for r, _ in packed], "packed_bytes": sum(s for _, s in packed),
            "links": links, "token_hits": token_hits, "modules": modules, "options": options,
            "templates": sorted(r for r, _ in packed if r.startswith("Data/BuildingTemplate/")),
            "generated": sorted(r for r, _ in packed if r.endswith(".generated.lua"))}


def print_tree_report(rep, held_tokens):
    print("  packed: %d files, %s raw bytes" % (len(rep["packed"]), format(rep["packed_bytes"], ",")))
    print("  registered modules (%d): %s" % (len(rep["modules"]), ", ".join(rep["modules"])))
    print("  option items (%d): %s" % (len(rep["options"]), ", ".join(rep["options"])))
    print("  Data templates (%d): %s" % (len(rep["templates"]), ", ".join(rep["templates"])))
    print("  generated code (%d): %s" % (len(rep["generated"]), ", ".join(rep["generated"])))
    for kind in ("changed", "missing", "extra"):
        print("  %s vs manifest: %d%s" % (kind, len(rep[kind]),
                                          "" if not rep[kind] else "  " + ", ".join(rep[kind])))
    if held_tokens:
        print("  held tokens %s: %d hit(s)%s" % (list(held_tokens), len(rep["token_hits"]),
              "" if not rep["token_hits"] else "  " + "; ".join(rep["token_hits"][:8])))


# ── state classification (pure: the selftest drives it with fixtures) ────────
def portal_state(batch, portal, live):
    """-> (code, sentence). `live` is the launch tree's current writeback fields."""
    p = batch["portals"][portal]
    pre = batch["pre_upload"]
    receipts = p.get("receipts") or []
    last = receipts[-1]["result"] if receipts else None
    snap = bool(p.get("snapshots"))
    if portal == "paradox":
        moved = (live.get("pdx_id"), live.get("pdx_version")) != (pre.get("pdx_id"), pre.get("pdx_version"))
        evidence = ("writeback shows a publish (pdx_id %s, pdx_version %s; the game saves these "
                    "only after the publish call succeeds)" % (live.get("pdx_id"), live.get("pdx_version"))
                    if moved else "no Paradox writeback")
    else:
        moved = live.get("steam_id") != pre.get("steam_id")
        evidence = ("steam_id %s is new — a LISTING was allocated; the game saves it before it "
                    "packs or uploads, so this is not an upload" % live.get("steam_id")
                    if moved else "steam_id unchanged (an update re-uses the listing; the id says "
                    "nothing about this batch)" if pre.get("steam_id") else "no steam_id")
    if last == "uploaded":
        return "CONFIRMED", "owner confirmed the upload; %s; package snapshot %s" % (
            evidence, "kept" if snap else "MISSING")
    if last == "failed":
        return "FAILED", "owner reported the upload failed; %s — retry is owed" % evidence
    if moved or snap:
        return "UNCONFIRMED", "%s; no owner receipt yet" % evidence
    return "OWED", "not uploaded; %s" % evidence


CLOSE_STEPS = (("writeback", "writeback fields merged into the repo's metadata.lua/items.lua and committed"),
               ("drained", "this batch's Pending entries moved to RELEASE_HISTORY"),
               ("tag", "annotated optin-v<major.minor.version> tag on the base commit"))


def classify(state, outbox_text, live):
    """-> (code, [lines]). Codes: IDLE, NEW_BATCH, PREPARED, UPLOADING, PARTIAL, CLOSE_OWED."""
    batch = state.get("batch")
    pending = [h for h, _ in pending_entries(outbox_text)]
    if not batch:
        last = state["closed"][-1] if state.get("closed") else None
        was = ("last closed batch %s (v%s)" % (last["id"], last.get("released_version"))
               if last else "no batch has ever closed (nothing is live)")
        if not pending:
            return "IDLE", ["no open batch and Pending is empty; %s" % was]
        return "NEW_BATCH", ["no open batch; %s" % was,
                             "%d Pending entr%s staged — this is a NEW batch to derive, not an "
                             "unfinished upload:" % (len(pending), "y" if len(pending) == 1 else "ies")
                             ] + ["  " + h for h in pending]
    lines = ["open batch %s (%s) pinned at %s, opened %s" % (
        batch["id"], batch["kind"], batch["base"][:7], batch["opened"])]
    lines += ["  in batch: " + h for h in batch["entries"]]
    later = [h for h in pending if h not in batch["entries"]]
    lines += ["  NOT in this batch, stays Pending: " + h for h in later]
    states = {p: portal_state(batch, p, live) for p in PORTALS}
    for p in PORTALS:
        lines.append("  %-8s %-11s %s" % (p, states[p][0], states[p][1]))
    codes = [states[p][0] for p in PORTALS]
    if all(c == "OWED" for c in codes):
        return "PREPARED", lines + ["next: the owner uploads (docs/UPLOAD_WORKFLOW.md)"]
    if all(c == "CONFIRMED" for c in codes):
        close = batch.get("close") or {}
        owed = [text for key, text in CLOSE_STEPS if not close.get(key)]
        lines += ["  close step owed: " + t for t in owed]
        return "CLOSE_OWED", lines + ["next: POST_UPLOAD_CLOSE.md%s"
                                      % ("" if owed else "; every step is recorded — run `close`")]
    if "CONFIRMED" in codes:
        return "PARTIAL", lines + ["next: the other portal; never drain or tag on a partial upload"]
    return "UPLOADING", lines + ["next: get the owner's receipt per portal; an id alone is not an upload"]


# ── drain (pure text in, text out) ───────────────────────────────────────────
def drain_texts(batch, version, outbox_text, history_text, date):
    """Move exactly the batch's entries. Idempotent. -> (outbox, history, moved, already)."""
    marker = "batch `%s`" % batch["id"]
    already = marker in history_text
    entries = dict(pending_entries(outbox_text))
    moved = [h for h in batch["entries"] if h in entries]
    if not already:
        missing = [h for h in batch["entries"] if h not in entries]
        if missing:
            raise Refuse("the outbox no longer holds batch entr%s %s and the history has no "
                         "section for this batch — restore the outbox before draining"
                         % ("y" if len(missing) == 1 else "ies", missing))
        section = ["", "### Released in v%s (%s) · %s, base `%s`" % (version, date, marker, batch["base"][:7]), ""]
        for h in batch["entries"]:
            body = entries[h].split("\n", 1)[1] if "\n" in entries[h] else ""
            section += ["#### " + h[len("### Pending · "):], body.strip("\n"), ""]
        history_text = history_text.rstrip("\n") + "\n" + "\n".join(section).rstrip("\n") + "\n"
    for h in moved:
        outbox_text = outbox_text.replace(entries[h], "", 1)
    m = re.search(r"^## Last released\n", outbox_text, re.M)
    if m:
        nxt = re.search(r"^## ", outbox_text[m.end():], re.M)
        rest = outbox_text[m.end() + nxt.start():] if nxt else ""
        outbox_text = outbox_text[:m.end()] + rest
        outbox_text = outbox_text[:m.end()] + (
            "\n**v%s, %s** — %s, base `%s`. Its entries are in "
            "`docs/archive/RELEASE_HISTORY.md`.\n" % (version, date, marker, batch["base"][:7])) + (
            ("\n" + rest) if rest else "")
    return outbox_text, history_text, moved, already


# ── commands ─────────────────────────────────────────────────────────────────
def need_batch(state):
    if not state.get("batch"):
        raise Refuse("no open batch (run `status`)")
    return state["batch"]


def live_fields(ctx, batch):
    meta = os.path.join(batch["launch_tree"], "metadata.lua") if batch else None
    return fields(meta) if meta and os.path.isfile(meta) else {}


def cmd_status(ctx, args):
    state = load_state(ctx)
    code, lines = classify(state, read_text(ctx.outbox), live_fields(ctx, state.get("batch")))
    print("RELEASE STATE: %s" % code)
    for ln in lines:
        print("  " + ln)
    return 0


def cmd_assemble(ctx, args):
    if "--out" not in args:
        raise Refuse("assemble needs --out <dir> (a dry assembly never uses the launch folder)")
    out = os.path.abspath(args[args.index("--out") + 1])
    base = ctx.git("rev-parse", args[args.index("--base") + 1] if "--base" in args else "HEAD").strip()
    manifest = assemble(ctx, base, out)
    print("ASSEMBLED %s from %s — %d members, no batch opened" % (out, base[:7], len(manifest)))
    rep = tree_report(ctx, out, manifest)
    print_tree_report(rep, ctx.held_tokens)
    bad = rep["changed"] or rep["missing"] or rep["extra"] or rep["token_hits"] or \
        any(not pat for _rel, pat in rep["links"])
    return 1 if bad else 0


def cmd_begin(ctx, args):
    state = load_state(ctx)
    if state.get("batch"):
        raise Refuse("batch %s is already open; finish or `abandon` it — a second batch is "
                     "never prepared on top of an open one" % state["batch"]["id"])
    base = ctx.git("rev-parse", "HEAD").strip()
    outbox_at_base = ctx.git("show", "%s:%s" % (base, os.path.relpath(ctx.outbox, ctx.repo).replace(os.sep, "/")))
    entries = [h for h, _ in pending_entries(outbox_at_base.replace("\r\n", "\n"))]
    hold = [args[i + 1] for i, a in enumerate(args) if a == "--hold"]
    held_entries = [h for h in entries if any(x in h for x in hold)]
    unmatched = [x for x in hold if not any(x in h for h in entries)]
    if unmatched:
        raise Refuse("--hold matched no committed Pending entry: %s" % unmatched)
    entries = [h for h in entries if h not in held_entries]
    if not entries:
        raise Refuse("no committed Pending entry at %s; there is nothing to release" % base[:7])
    manifest = assemble(ctx, base, ctx.launch)
    pre = fields(os.path.join(ctx.launch, "metadata.lua"))
    kind = "update" if (pre.get("pdx_id") or pre.get("steam_id")) else "first-publish"
    n = len(state.get("closed") or []) + 1
    state["batch"] = {
        "id": "%s-%02d" % (today(), n), "kind": kind, "opened": today(), "base": base,
        "entries": entries, "held_entries": held_entries, "held_out": dict(ctx.held_out),
        "launch_tree": ctx.launch, "manifest": manifest, "pre_upload": pre,
        "portals": {p: {"snapshots": [], "receipts": []} for p in PORTALS},
        "close": {"writeback": None, "drained": False, "tag": None}}
    save_state(ctx, state)
    print("BATCH %s opened (%s) at %s" % (state["batch"]["id"], kind, base[:7]))
    for h in entries:
        print("  in batch: " + h)
    for h in held_entries:
        print("  held, stays Pending: " + h)
    print("  launch tree: %s (%d members)" % (ctx.launch, len(manifest)))
    print("  commit %s, then run `verify`" % os.path.relpath(ctx.state, ctx.repo))
    return 0


def cmd_verify(ctx, args):
    batch = need_batch(load_state(ctx))
    rep = tree_report(ctx, batch["launch_tree"], batch["manifest"])
    print("LAUNCH TREE %s — batch %s, base %s" % (batch["launch_tree"], batch["id"], batch["base"][:7]))
    print_tree_report(rep, ctx.held_tokens)
    uploaded = any(batch["portals"][p]["snapshots"] or batch["portals"][p]["receipts"] for p in PORTALS)
    live = fields(os.path.join(batch["launch_tree"], "metadata.lua"))
    moved = live != batch["pre_upload"]
    allowed = set(EDITOR_OWNED) if (uploaded or moved) else set()
    unexpected = [r for r in rep["changed"] if r not in allowed]
    bad = unexpected or rep["missing"] or rep["extra"] or rep["token_hits"] or \
        any(not pat for _rel, pat in rep["links"])
    if rep["changed"] and not unexpected:
        print("  changed files are the editor's writeback set only: %s" % ", ".join(rep["changed"]))
    print("  VERDICT: %s" % ("FAIL — the launch tree is not the pinned one" if bad
                             else "the launch tree is the pinned batch" +
                             (" plus the editor's writeback" if rep["changed"] else "")))
    return 1 if bad else 0


def cmd_link(ctx, args):
    target = {"launch": None, "repo": ctx.repo}.get(args[0] if args else "")
    if not args or args[0] not in ("launch", "repo"):
        raise Refuse("link needs `launch` or `repo`")
    if args[0] == "launch":
        target = need_batch(load_state(ctx))["launch_tree"]
    link = ctx.mods_link
    if os.path.lexists(link):
        try:
            current = os.path.normcase(os.path.realpath(link))
            is_link = os.path.normcase(os.path.abspath(link)) != current
        except OSError:
            is_link, current = False, ""
        ours = {os.path.normcase(os.path.realpath(ctx.repo)), os.path.normcase(os.path.realpath(ctx.launch))}
        if not is_link or current not in ours:
            raise Refuse("%s is not a link to this repo or its launch tree; not touching it" % link)
        os.rmdir(link)      # removes the junction, never its target
    subprocess.run(["cmd", "/c", "mklink", "/J", link, target], check=True, capture_output=True)
    print("Mods link %s -> %s" % (link, target))
    print("  restart the game before opening the Mod Editor" if args[0] == "launch"
          else "  the game loads the working repo again after a restart")
    return 0


def cmd_snapshot(ctx, args):
    state = load_state(ctx)
    batch = need_batch(state)
    if not args or args[0] not in PORTALS:
        raise Refuse("snapshot needs `paradox` or `steam`")
    portal = args[0]
    if not os.path.isfile(ctx.pack):
        raise Refuse("no package at %s — the game deletes it at the start of the next upload "
                     "and nothing can rebuild those bytes; record this limit in the batch "
                     "receipt instead of claiming an exact package" % ctx.pack)
    data = open(ctx.pack, "rb").read()
    digest = sha256(data)
    for p in PORTALS:
        for s in batch["portals"][p]["snapshots"]:
            if s["pack_sha256"] == digest:
                if p == portal:
                    print("snapshot already kept for %s (%s); nothing to do" % (portal, digest[:12]))
                    return 0
                raise Refuse("this package (%s) is already kept as the %s snapshot — the %s "
                             "upload has not built a new one" % (digest[:12], p, portal))
    snaps = batch["portals"][portal]["snapshots"]
    dest = os.path.join(ctx.snapshots, batch["id"], "%s-%d" % (portal, len(snaps) + 1))
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, "ModContent.fpk"), "wb").write(data)
    record = {"taken": today(), "dir": os.path.relpath(dest, ctx.repo).replace(os.sep, "/"),
              "pack_sha256": digest, "pack_bytes": len(data),
              "pack_mtime": datetime.datetime.fromtimestamp(os.path.getmtime(ctx.pack)).isoformat(timespec="seconds"),
              "serializer": {}, "fields": fields(os.path.join(batch["launch_tree"], "metadata.lua"))}
    for name in EDITOR_OWNED:
        src = os.path.join(batch["launch_tree"], name)
        blob = open(src, "rb").read()
        open(os.path.join(dest, name), "wb").write(blob)
        record["serializer"][name] = sha256(blob)
    snaps.append(record)
    save_state(ctx, state)
    print("SNAPSHOT %s #%d: %s bytes, sha256 %s" % (portal, len(snaps), format(len(data), ","), digest))
    print("  kept in %s with the editor's metadata.lua and items.lua as they are now" % record["dir"])
    print("  compare: python tools/pack_list.py %s/ModContent.fpk --tree \"%s\" "
          "--allow-differ metadata.lua --allow-differ items.lua" % (record["dir"], batch["launch_tree"]))
    return 0


def cmd_receipt(ctx, args):
    state = load_state(ctx)
    batch = need_batch(state)
    if len(args) < 3 or args[0] not in PORTALS or args[1] not in ("uploaded", "failed"):
        raise Refuse('receipt needs: paradox|steam uploaded|failed "<the owner\'s words>"')
    batch["portals"][args[0]]["receipts"].append(
        {"date": today(), "result": args[1], "owner_words": args[2]})
    save_state(ctx, state)
    print("receipt recorded: %s %s" % (args[0], args[1]))
    return 0


def cmd_writeback(ctx, args):
    batch = need_batch(load_state(ctx))
    live = upload_preflight.parse_metadata(os.path.join(batch["launch_tree"], "metadata.lua"))
    ours = upload_preflight.parse_metadata(os.path.join(ctx.repo, "metadata.lua"))
    keys = sorted(set(live) | set(ours))
    diffs = [(k, ours.get(k), live.get(k)) for k in keys if ours.get(k) != live.get(k)]
    print("WRITEBACK — launch tree's metadata.lua (the editor's) vs the repo working copy")
    for k, a, b in diffs:
        owned = "editor-owned: copy it" if k in WRITEBACK_FIELDS else \
                "NOT a writeback field: explain it (held work, or the serializer changed it)"
        print("  %-16s repo %r -> launch %r   [%s]" % (k, _short(a), _short(b), owned))
    if not diffs:
        print("  no parsed field differs (scalars and the code / ignore_files / entities lists)")
    print("  limit: comments, table fields other than those three lists, and items.lua are "
          "not parsed here; diff the snapshot's files by hand for those")
    return 0


def _short(v):
    s = repr(v) if not isinstance(v, str) else v
    return s if len(s) <= 60 else s[:57] + "..."


def cmd_drain(ctx, args):
    state = load_state(ctx)
    batch = need_batch(state)
    live = live_fields(ctx, batch)
    states = {p: portal_state(batch, p, live)[0] for p in PORTALS}
    if any(c != "CONFIRMED" for c in states.values()):
        raise Refuse("drain refused: %s — every portal needs the owner's receipt first"
                     % ", ".join("%s %s" % kv for kv in states.items()))
    version = version_of(live)
    outbox, history, moved, already = drain_texts(
        batch, version, read_text(ctx.outbox), read_text(ctx.history), today())
    write_text(ctx.outbox, outbox)
    write_text(ctx.history, history)
    batch["close"]["drained"] = True
    batch["released_version"] = version
    save_state(ctx, state)
    print("DRAIN v%s: %d entr%s removed from Pending; history section %s"
          % (version, len(moved), "y" if len(moved) == 1 else "ies",
             "already present (not appended twice)" if already else "appended"))
    left = [h for h, _ in pending_entries(outbox)]
    for h in left:
        print("  stays Pending (not in this batch): " + h)
    return 0


def cmd_mark(ctx, args):
    state = load_state(ctx)
    batch = need_batch(state)
    if len(args) != 2 or args[0] not in ("writeback", "tag"):
        raise Refuse("mark needs: writeback <commit sha> | tag <tag name>")
    batch["close"][args[0]] = args[1]
    save_state(ctx, state)
    print("recorded %s = %s" % (args[0], args[1]))
    return 0


def cmd_close(ctx, args):
    state = load_state(ctx)
    batch = need_batch(state)
    code, lines = classify(state, read_text(ctx.outbox), live_fields(ctx, batch))
    owed = [t for key, t in CLOSE_STEPS if not batch["close"].get(key)]
    if code != "CLOSE_OWED" or owed:
        raise Refuse("close refused in state %s%s" % (code, "".join("\n  owed: " + t for t in owed)))
    batch["closed"] = today()
    batch.pop("manifest", None)      # the sibling .manifest.json and the snapshots keep it
    state.setdefault("closed", []).append(batch)
    state["batch"] = None
    save_state(ctx, state)
    print("BATCH %s closed (v%s)" % (batch["id"], batch.get("released_version")))
    return 0


def cmd_abandon(ctx, args):
    state = load_state(ctx)
    batch = need_batch(state)
    if not args:
        raise Refuse('abandon needs a reason: abandon "<why>"')
    live = live_fields(ctx, batch)
    touched = [p for p in PORTALS if portal_state(batch, p, live)[0] != "OWED"]
    if touched:
        raise Refuse("abandon refused: %s shows upload activity. An allocated id or a publish "
                     "must be carried into the repo, not dropped; finish or repair the batch"
                     % ", ".join(touched))
    state["batch"] = None
    state.setdefault("abandoned", []).append({"id": batch["id"], "base": batch["base"],
                                              "date": today(), "reason": args[0]})
    save_state(ctx, state)
    print("batch %s abandoned; Pending is untouched" % batch["id"])
    return 0


COMMANDS = {"status": cmd_status, "assemble": cmd_assemble, "begin": cmd_begin,
            "verify": cmd_verify, "link": cmd_link, "snapshot": cmd_snapshot,
            "receipt": cmd_receipt, "writeback": cmd_writeback, "drain": cmd_drain,
            "mark": cmd_mark, "close": cmd_close, "abandon": cmd_abandon}


def main(argv, ctx=None):
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 2
    try:
        return COMMANDS[argv[0]](ctx or Ctx(), argv[1:])
    except Refuse as exc:
        print("REFUSED: %s" % exc)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
