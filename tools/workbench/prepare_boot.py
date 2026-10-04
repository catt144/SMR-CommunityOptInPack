"""Prepare a workbench menu-only integration leg for the canonical TestKit arming harness."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
scratch = ROOT / "scratch/workbench_boot"
scratch.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("step", choices=["setup", "present", "absent", "restored"])
parser.add_argument("--original", help="comma-separated original order read from setup log")
args = parser.parse_args()
if args.original:
    (scratch / "original.json").write_text(json.dumps(args.original.split(",")), encoding="utf-8")
original = json.loads((scratch / "original.json").read_text()) if args.step != "setup" else []
next_order = (["SMR_CommunityOptInPack_Workbench"] + [x for x in original if x != "SMR_CommunityFixPack"]
              if args.step == "present" else original)
prefix = f'WB_STEP = "{args.step}"\n'
prefix += "WB_ORIGINAL = {" + ", ".join(map(json.dumps, original)) + "}\n"
prefix += "WB_NEXT = {" + ", ".join(map(json.dumps, next_order)) + "}\n"
(scratch / "98_WorkbenchBoot.lua.txt").write_bytes((prefix + Path(__file__).with_name("boot.lua.txt").read_text(encoding="utf-8")).encode("ascii"))
manifest = dict(leg="workbench-" + args.step, kit=str(ROOT.parent / "SMR-BugFixPack-TestKit"),
                park=str(scratch), stripPattern="Code/98_WorkbenchBoot", bootSymbol="WorkbenchBoot.Boot",
                symbolNamespace="WorkbenchBoot", permanent=["Code/80_AgentSlots.lua"],
                mustNotBeListed=["Code/96_AutoRunFlag.lua"], mustNotBeListedWhy="menu-only integration",
                bannedPatterns=["SaveGame\\s*\\(", "LoadGame\\s*\\("],
                payloads=[dict(src="98_WorkbenchBoot.lua.txt", dst="98_WorkbenchBoot.lua", selfDrives=True)])
(scratch / "leg.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(scratch / "leg.json")
