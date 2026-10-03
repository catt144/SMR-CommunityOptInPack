"""Archive the B1 flushed prefix while the owner continues in the same process.

One-shot capture, append-only. A later complete log needs a different archive path.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
name = "Mars.exe-20261003-12.28.41-6aba6e65.log"
source = Path.home() / "AppData/Roaming/Surviving Mars Relaunched/logs" / name
raw = source.read_bytes()
lines = raw.decode("utf-8-sig").splitlines()
patterns = {
    "lua_errors": r"LUA ERROR",
    "shutdown": r"Debug::Done\(\)",
    "departure": r"^\[SMRTK\].*verdict=departed",
    "arrival": r"^\[SMRTK\].*verdict=arrived",
    "snapshots": r"^\[SMRTK\].*fixpack_version=",
    "depot_reads": r"^\[SMRTK\].*aboard_metals=",
    "fixture_writes": r"^\[SMRTK\].*method=CheatFill",
    "trace": r"^\[SMRTK\].*action=slot_scratch.*trace=",
    "stream": r"^\[SMRTK\].*(?:action=slot_10|reason=ChangeMap|reason=change_map|STREAM_STOP)",
    "diagnostics": r"(?i)\berror\b|\bwarning\b|\bfailed\b|unpersist|Savegame references",
}
members = {key: [{"line": i, "text": line} for i, line in enumerate(lines, 1)
                 if re.search(pattern, line)] for key, pattern in patterns.items()}
assert members["departure"] and any("cabin=up" in row["text"] and
    "aboard_Metals=622" in row["text"] for row in members["departure"])
assert any("s_Metals=622" in row["text"] for row in members["arrival"])
assert any("metals=62166" in row["text"] and "half=9036" in row["text"]
           for row in members["depot_reads"])
assert not members["lua_errors"]
receipt = {
    "command": "python docs/archive/train_b1_20261003/capture.py",
    "read_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "captured_utc": datetime.now(timezone.utc).isoformat(), "source": str(source),
    "boundary": "Live-process flushed prefix; not a complete closed-log absence verdict.",
    "bytes": len(raw), "lines": len(lines), "sha256": hashlib.sha256(raw).hexdigest(),
    "decode": "strict utf-8-sig; 1-based splitlines; SMRTK anchors exclude [mod] echoes",
    "filters": patterns, "counts": {k: len(v) for k, v in members.items()}, "members": members,
}
with (HERE / name).open("xb") as f:
    f.write(raw)
with (HERE / "receipt.json").open("x", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, indent=2)
    f.write("\n")
assert (HERE / name).read_bytes() == raw
print(json.dumps({k: receipt[k] for k in ("read_head", "bytes", "lines", "sha256", "counts")}))
