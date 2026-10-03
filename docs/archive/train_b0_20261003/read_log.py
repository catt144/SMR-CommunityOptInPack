"""Reproduce the B0 receipt from the adjacent, byte-preserved closed native log."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LOG = HERE / "Mars.exe-20261003-01.04.09-6aba6e65.log"
raw = LOG.read_bytes()
lines = raw.decode("utf-8-sig").splitlines()
patterns = {
    "shutdown": r"Debug::Done\(\)",
    "build": r"Build version:",
    "train_logging": r"^\[(?:TrainHub|TrainDistribution|TrainBay|StationSpoilage|ElevatorDepot)\]",
    "lua_errors": r"LUA ERROR",
    "diagnostics": r"(?i)\berror\b|\bwarning\b|\bfailed\b|unpersist|Savegame references",
    "missing_permanents": r"Unpersist missing",
    "old_mod_references": r"Savegame references",
    "hours": r"^\[SMRTK\] SMRTK_TRIGGER .*verdict=hour_done",
    "snapshots": r"^\[SMRTK\].*fixpack_version=",
    "module_status": r"^\[SMRTK\].*module=(?:TrainHub|StationRows|ElevatorDepot)\b",
    "hubs": r'^\[SMRTK\].*role="Hub [12]" row=object',
    "export_read": r"^\[SMRTK\].*mode=export .*resource=Metals .*station=10531\b",
    "metal_requests": r"^\[SMRTK\].*object=StationSmall\(10531\) resource=Metals",
}
members = {key: [{"line": i, "text": line} for i, line in enumerate(lines, 1)
                 if re.search(pattern, line)] for key, pattern in patterns.items()}
counts = {key: len(value) for key, value in members.items()}
assert counts["shutdown"] == 1 and counts["lua_errors"] == 0
assert counts["hours"] == 2 and counts["train_logging"] == 6
assert all("loaded" in x["text"] or "registered" in x["text"] or "save guard:" in x["text"]
           for x in members["train_logging"])
assert counts["snapshots"] > 0 and all("fixpack_version=1.0.26" in x["text"]
    and "trace=false" in x["text"] and "errors=0" in x["text"] for x in members["snapshots"])
assert counts["export_read"] > 0
assert all("live_trains=17" in x["text"] and "train_state_changes=0 " not in x["text"]
           for x in members["hours"])
result = {
    "command": "python docs/archive/train_b0_20261003/read_log.py",
    "read_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "game_build": "1.1.1.406343",
    "file": LOG.name, "bytes": len(raw), "lines": len(lines),
    "sha256": hashlib.sha256(raw).hexdigest(),
    "decode": "strict utf-8-sig; splitlines; 1-based line numbers",
    "counting": "Each count equals its complete member list; anchored SMRTK filters exclude [mod] echoes.",
    "filters": patterns, "counts": counts, "members": members,
}
print(json.dumps(result, indent=2))
