"""One-shot append-only capture and final-battery evidence reconciliation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = Path.home() / "AppData/Roaming/Surviving Mars Relaunched/logs"
stems = ["20261003-12.28.41", "20261003-12.55.31", "20261003-13.05.06"]
receipt = {
    "command": "python docs/archive/train_final_result_20261003/capture.py",
    "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "captured_utc": datetime.now(timezone.utc).isoformat(),
    "decode": "strict utf-8-sig, splitlines, 1-based lines; canonical [SMRTK] excludes [mod] echoes",
    "logs": {},
}
logs = {}
for stem in stems:
    paths = list(SOURCE.glob("Mars.exe-" + stem + "*.log"))
    assert len(paths) == 1, paths
    p = paths[0]
    raw = p.read_bytes()
    lines = raw.decode("utf-8-sig").splitlines()
    with (HERE / p.name).open("xb") as f:
        f.write(raw)
    assert (HERE / p.name).read_bytes() == raw
    patterns = {
        "shutdown": r"Debug::Done\(\)", "lua_errors": r"^\[LUA ERROR\]",
        "permanents": r"Unpersist missing permanent:",
        "diagnostics": r"(?i)\berror\b|\bwarning\b|\bfailed\b|unpersist|Savegame references",
        "hub_metals": r"^\[SMRTK\].*object=SMROptInTrainHub6.*resource=Metals",
        "saves": r"^\[SMRTK\] SMRTK_SAVE ",
        "removal": r"^\[SMRTK\].*sitting=final35_removal",
        "row_export": r"^\[SMRTK\].*mode=export.*resource=Metals.*station=10531",
        "delete_build": r"^\[SMRTK\].*action=selected_(?:delete|quick_build)",
    }
    members = {k: [{"line": i, "text": l} for i, l in enumerate(lines, 1) if re.search(v, l)]
               for k, v in patterns.items()}
    receipt["logs"][stem] = {
        "file": p.name, "bytes": len(raw), "lines": len(lines),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "closed": bool(members["shutdown"]), "filters": patterns,
        "counts": {k: len(v) for k, v in members.items()}, "members": members,
    }
    logs[stem] = lines
    if stem == stems[0]:
        prefix = (ROOT / "docs/archive/train_b1_20261003" / p.name).read_bytes()
        assert raw.startswith(prefix), "closed B1 log changed its archived prefix"

lines = logs[stems[1]]
def requests(lo, hi):
    out = {}
    for i, line in enumerate(lines, 1):
        if lo <= i <= hi and line.startswith("[SMRTK]") and "row=request" in line and "object=SMROptInTrainHub6(" in line:
            fields = dict(re.findall(r'(\w+)=([^ ]+)', line))
            out[(fields["object"], fields["resource"])] = {"line": i, "fields": fields}
    return out

before, after = requests(1122, 1976), requests(1977, 2828)
assert before and before.keys() == after.keys()
comparisons = []
for key in sorted(before):
    b, a = before[key], after[key]
    bf, af = b["fields"], a["fields"]
    assert bf["stock"] == af["stock"] and bf["t"] == af["t"]
    assert bf["capacity"] == "4000000" and af["capacity"] == "2000000"
    comparisons.append({"object": key[0], "resource": key[1], "before": b, "after": a})
receipt["stock_control"] = {"filter": "canonical hub row=request; before lines 1122..1976, after 1977..2828",
    "assertions": "same nonempty object/resource keys, same stock and game time, capacity 4000000 -> 2000000",
    "compared": len(comparisons), "members": comparisons}
for label, lo, hi, pattern in [
    ("zero_hubs", 2837, 4318, r"object=SMROptInTrainHub6\("),
    ("content_free", 4372, 5024, r"object=SMROptIn(?:TrainHub6|ElevatorDepotDev)\("),
]:
    objects = [{"line": i, "text": l} for i, l in enumerate(lines, 1)
               if lo <= i <= hi and l.startswith("[SMRTK]") and "row=object" in l]
    hits = [x for x in objects if re.search(pattern, x["text"])]
    assert objects and not hits
    receipt[label] = {"range": [lo, hi], "filter": pattern, "positive_objects": len(objects), "hits": hits, "members": objects}

removal = logs[stems[2]]
assert removal[403].startswith("Load Game:"), "SMRTK_B load boundary moved"
errors_before = [{"line": i, "text": l} for i, l in enumerate(removal, 1) if i < 404 and l.startswith("[LUA ERROR]")]
errors_after = [{"line": i, "text": l} for i, l in enumerate(removal, 1) if i >= 404 and l.startswith("[LUA ERROR]")]
assert len(errors_before) == 5 and not errors_after
assert any(l.startswith("[SMRTK]") and "sitting=final35_removal" in l and
           "native_match=true" in l and "optin_present=false" in l for l in removal)
receipt["removal_error_boundary"] = {"load_line": 404, "before_count": len(errors_before),
    "after_count": len(errors_after), "before": errors_before, "after": errors_after,
    "limit": "No errors after B load in the captured prefix; not a closed-process claim if closed=false."}
with (HERE / "receipt.json").open("x", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, indent=2)
    f.write("\n")
print(json.dumps({"logs": {k: {x: v[x] for x in ["file", "bytes", "lines", "closed"]}
    for k, v in receipt["logs"].items()}, "stocks_compared": len(comparisons),
    "zero_hub_positive_objects": receipt["zero_hubs"]["positive_objects"],
    "content_free_positive_objects": receipt["content_free"]["positive_objects"]}))
