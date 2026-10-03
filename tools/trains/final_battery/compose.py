"""Compose brief 35's sitting slots; never load/compile Lua strings in the game.

Writes an inert .lua.txt beside this script. Installation is a separate,
game-closed copy after reviewing the generated script and its gates.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCES = {
    "upgrades": "tools/trains/hub/tests/80_AgentSlots_upgrades.lua.txt",
    "depot": "tools/trains/depot/tests/80_AgentSlots_depot.lua.txt",
    "revision": "tools/trains/depot/tests/80_AgentSlots_revision.lua.txt",
    "rows": "tools/trains/hub/tests/80_AgentSlots_station_rows.lua.txt",
    "crossings": "tools/trains/hub/tests/80_AgentSlots_crossing.lua.txt",
    "floor": "tools/trains/hub/tests/80_AgentSlots_34b.lua.txt",
}


def compose(evidence, expected):
    parts = ["-- GENERATED sitting source: edit compose.py / controls.lua.txt and regenerate.\n"
             "-- Brief 35 predictions: docs/agent/reports/TRAIN_FINAL_BATTERY_20261002.md\n"
             "-- Slot 12 cycles named groups; slot 11 reads state; Scratch toggles trace.\n"
             "-- No fixture action or watch runs at load. Shipping Code/ is untouched.\n"]
    parts.append("local expected_fixpack = " + json.dumps(expected) + "\n")
    parts.append((HERE / "controls.lua.txt").read_text(encoding="utf-8"))
    parts.append("\nT.PreloadProbeSweep {\n")
    for key in ("command", "output", "pack_head", "testkit_head", "checked_at", "brief"):
        literal = json.dumps(evidence[key]).replace("TEMPORARY", 'TEMP" .. "ORARY')
        parts.append(f"    {key} = {literal},\n")
    parts.append(f"    exit = {int(evidence['exit'])}, hits = {{}}, needed = {{}},\n}}\n")
    receipts = {}
    for name, path in SOURCES.items():
        raw = (ROOT / path).read_bytes()
        receipts[path] = hashlib.sha256(raw).hexdigest()
        source = raw.decode("utf-8-sig")
        if name == "floor":
            # Replace the obsolete embedded attestation with this sitting's evidence.
            source, count = re.subn(r"T\.PreloadProbeSweep\s*\{.*?\n\}", "", source, count=1, flags=re.S)
            assert count == 1
        parts.append(f"\n-- BEGIN inherited instrument {name}: {path}\ndo\n"
                     f"local SMRTK = capture({json.dumps(name)})\n" + source + "\nend\n")
    parts.append((HERE / "groups.lua.txt").read_text(encoding="utf-8"))
    return "".join(parts), receipts


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--fixpack", choices=("present", "absent"), required=True)
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text(encoding="utf-8-sig"))
    assert evidence["exit"] == 1 and evidence["output"] == "" and evidence["hits"] == []
    source, receipts = compose(evidence, args.fixpack)
    output = HERE / "80_AgentSlots_final.lua.txt"
    output.write_text(source, encoding="utf-8", newline="\n")
    receipt = {"expected_fixpack": args.fixpack, "source_sha256": receipts,
               "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
               "sweep": evidence}
    (HERE / "preload_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(output)
