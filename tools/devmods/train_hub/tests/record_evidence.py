"""Archive the unattended 3b smoke and verify original saves, after Mars exits.

Run from the Opt-In repo. Outputs are exclusive creations: never rewrite archives.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


root = Path(__file__).resolve().parents[4]
assert not re.search(r"\bMars\.exe\b", subprocess.check_output(
    ["tasklist", "/FI", "IMAGENAME eq Mars.exe"], text=True), re.I), "Exit game first"
logs = Path(os.environ["APPDATA"]) / "Surviving Mars Relaunched/logs"
backup = Path(os.environ["TEMP"]) / "SMRTrainHub3b-20260920-035736"
saves = Path("C:/Dev/SMR-BugFixPack/saves/game")
archive = root / "docs/archive"
record = {
    "command": subprocess.list2cmdline(["python", *sys.argv]),
    "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
    "game": "1.1.0.403908",
    "inputs": {str(p.relative_to(root)): digest(p) for p in sorted(
        (root / "tools/devmods/train_hub").rglob("*")) if p.is_file() and
        p.suffix in (".lua", ".py", ".txt", ".json")},
    "original_saves": [], "logs": [], "screenshots": [],
}
for old in sorted(backup.glob("*.sav")):
    current = saves / old.name
    assert current.exists() and digest(old) == digest(current), old.name
    record["original_saves"].append({"name": old.name, "sha256": digest(old)})
assert record["original_saves"], "Missing original save backup"
for log in sorted(logs.glob("Mars.exe-20260920-*.log")):
    if log.name < "Mars.exe-20260920-03.57.39":
        continue
    body = log.read_text(encoding="utf-8", errors="replace")
    if "[HUB3B" not in body:
        continue
    target = archive / ("TRAIN_HUB_3B_" + log.name)
    with target.open("xb") as stream:
        stream.write(log.read_bytes())
    errors = [line for line in body.splitlines() if line.startswith("[LUA ERROR]")]
    markers = [line for line in body.splitlines() if "[HUB3BSMOKE]" in line and
               re.search(r"RESULT|STAGE_COMPLETE|RELOAD_|SPARE_PARKED|SAVED", line)]
    record["logs"].append({"archive": target.name, "sha256": digest(log),
        "lua_error_count": len(errors), "lua_errors": errors, "markers": markers})
    for line in body.splitlines():
        if line.startswith("[mod]") and "action=screenshot_mark" in line:
            match = re.search(r"path=(.+?\.png) status=OK", line)
            if match:
                shot = Path(match[1])
                record["screenshots"].append({"path": str(shot), "sha256": digest(shot),
                    "log": target.name, "marker": line})
assert record["logs"]
final = next(x for x in record["logs"] if "04.22.55" in x["archive"])
assert sum("RESULT" in x and "ok=true" in x for x in final["markers"]) == 3
assert any("RELOAD_LOCK_OK" in x for x in final["markers"])
assert any("RELOAD_PARKED_OK" in x for x in final["markers"])
assert len(final["lua_errors"]) == 1 and "ArtSpecEditor.lua:573" in final["lua_errors"][0]
straight = record["logs"][-1]
assert any("RESULT stage=1 ok=true" in x for x in straight["markers"])
assert len(straight["lua_errors"]) == 1 and "ArtSpecEditor.lua:573" in straight["lua_errors"][0]
with (archive / "TRAIN_HUB_3B_NATIVE_20260920.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, indent=2)
    stream.write("\n")
print(json.dumps({"original_saves_unchanged": len(record["original_saves"]),
    "logs_archived": len(record["logs"]), "screenshots_hashed": len(record["screenshots"]),
    "final_stages_passed": [1, 2, 3, 4], "final_new_runtime_errors": 0}, indent=2))
