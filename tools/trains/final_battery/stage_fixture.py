"""Stage the owner-selected byte copy and protect sitting-overwritten saves.

Run with the game closed. Never overwrites a previous fixture or backup.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SAVES = ROOT.parent / "SMR-BugFixPack/saves/game"
SOURCE = "Double Hub+elev Built Under2.savegame.sav"
TARGET = "FINAL35_P_20261002.savegame.sav"
BACKUP = ROOT / "local/train-final-battery-20261002"
RECEIPT = ROOT / "docs/archive/train_final_fixture_20261002/staging.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    process = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq Mars.exe", "/FO", "CSV"], text=True)
    assert '"Mars.exe"' not in process, "Close Mars.exe before staging"
    assert SAVES.resolve() == Path.home() / "Saved Games/Surviving Mars Relaunched/76561198020568696"
    source, target = SAVES / SOURCE, SAVES / TARGET
    assert source.is_file() and not target.exists()
    assert not BACKUP.exists() and not RECEIPT.exists()
    before = []
    for p in sorted(SAVES.iterdir(), key=lambda x: x.name.lower()):
        if p.is_file():
            before.append({"name": p.name, "bytes": p.stat().st_size, "mtime_ns": p.stat().st_mtime_ns})
    protected = [p for p in SAVES.iterdir() if p.is_file() and
                 ("autosave" in p.name.lower() or p.name in {"SMRTK_A.sav", "SMRTK_B.sav", "SMRTK_C.sav"})]
    BACKUP.mkdir(parents=True)
    copied = []
    for p in sorted(protected, key=lambda x: x.name.lower()):
        dest = BACKUP / p.name
        shutil.copy2(p, dest)
        sha = digest(p)
        assert digest(dest) == sha
        copied.append({"name": p.name, "bytes": p.stat().st_size, "sha256": sha,
                       "source": str(p.resolve()), "backup": str(dest)})
    shutil.copy2(source, BACKUP / SOURCE)
    shutil.copy2(source, target)
    sha = digest(source)
    assert digest(target) == sha == digest(BACKUP / SOURCE)
    receipt = {"checked_at": datetime.now(timezone.utc).isoformat(),
               "owner_instruction_date": "2026-10-02", "command": "python tools/trains/final_battery/stage_fixture.py",
               "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
               "save_root": str(SAVES.resolve()), "inventory_before": before,
               "protected": copied, "source": SOURCE, "fixture": TARGET,
               "fixture_sha256": sha, "fixture_bytes": target.stat().st_size,
               "fixture_mtime_ns": target.stat().st_mtime_ns,
               "load_route": '*r LoadGame("' + TARGET + '")',
               "native_load_back": "NOT RUN"}
    RECEIPT.parent.mkdir(parents=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"fixture": TARGET, "sha256": sha, "backed_up_names": [r['name'] for r in copied],
                      "receipt": str(RECEIPT), "native_load_back": "NOT RUN"}, indent=2))
