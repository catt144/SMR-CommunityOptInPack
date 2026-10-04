"""Verify completed workbench integration logs with positive controls and full error inventories."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "docs/archive/workbench_20261003"
MEMBERS = ["setup_clean.log", "present_clean.log", "absent_clean.log", "restored_clean.log"]
receipt = {"command": "python tools/workbench/read_boots.py",
           "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "build": "1.1.1.406343 / Steam 25579348", "logs": []}
for name in MEMBERS:
    path = ARCHIVE / name
    data = path.read_bytes()
    lines = data.decode("utf-8", errors="replace").splitlines()
    source = "\n".join(lines)
    required = ["[WORKBENCH-BOOT] result=true", "*** Debug::Done()",
                "SMRTK_TAINT_READ", "SMRTK_ELIGIBILITY"]
    if name in ("present_clean.log", "absent_clean.log"):
        required += ["falsifier_rejected=true", "native_option=true class=true template=true",
                     "live=false registry=false", "live=true registry=true"]
    if name == "restored_clean.log":
        required += ["production_only=true original_order_restored=true"]
    for token in required:
        if token not in source:
            raise SystemExit(f"FAIL {name}: missing {token}")
    fatal = [(n, line) for n, line in enumerate(lines, 1)
             if re.search(r"\[LUA ERROR\]|Errors while loading mod|\[WORKBENCH-BOOT\] result=false", line)]
    if fatal:
        raise SystemExit(f"FAIL {name}: {fatal}")
    problems = [(n, line) for n, line in enumerate(lines, 1)
                if re.search(r"error|assert|exception|fail|warning", line, re.I)]
    controls = [(n, line) for n, line in enumerate(lines, 1) if "[WORKBENCH-BOOT]" in line]
    receipt["logs"].append(dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(),
                                sha256_lf=hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest(),
                                required=required, control_count=len(controls), controls=controls,
                                fatal_filter=r"\[LUA ERROR\]|Errors while loading mod|\[WORKBENCH-BOOT\] result=false",
                                fatal_count=len(fatal), fatal=fatal,
                                review_filter="error|assert|exception|fail|warning",
                                review_count=len(problems), review=problems))
receipt["log_count"] = len(receipt["logs"])
print(json.dumps(receipt, indent=2))
