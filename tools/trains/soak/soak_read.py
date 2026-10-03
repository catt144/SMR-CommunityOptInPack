"""Read a game log for the pre-launch train SOAK (slots from soak_slots.lua.txt).

    python tools/trains/soak/soak_read.py [LOG] [--json] [--examples N]

LOG defaults to the newest %APPDATA%\\Surviving Mars Relaunched\\logs\\Mars.exe-*.log.
Prints, per soak in the log: start/stop, game hours covered, every SOAK_FLAG grouped by
kind with counts (and how many cleared), per-resource total drift per game hour from the
SOAK_TOTALS lines, the suppressed-flag count, and the log's LUA ERROR count. Also counts
the train modules' own trace lines that report refusals or pairing trouble.

SMRTK lines can appear twice (the ModLog copy prefixed "[mod] " and the console copy);
each record is counted once, by its SMRTK sequence id.
"""
import argparse
from collections import Counter, OrderedDict, defaultdict
import glob
import json
import os
from pathlib import Path
import re
import sys

LINE = re.compile(r'^(?:\[mod\] )?\[SMRTK\] SMRTK_(?P<verb>\w+)(?P<rest>.*)$')
FIELD = re.compile(r'(\w+)=("(?:[^"\\]|\\.)*"|\S+)')
LUA_ERROR = re.compile(r'LUA ERROR')
# The train modules' trace lines worth counting (printed only while TrainTrace is on).
TRACE = OrderedDict([
    ("bay_refused", re.compile(r'^\[TrainBay\] refused hub=')),
    ("depot_no_pair", re.compile(r'^\[ElevatorDepot\] no pair:')),
    ("depot_pair_limit", re.compile(r'^\[ElevatorDepot\] pair limit:')),
    ("depot_pair_formed", re.compile(r'^\[ElevatorDepot\] pair formed:')),
    ("depot_cabin_held", re.compile(r'^\[ElevatorDepot\] cabin held:')),
    ("depot_half_gone", re.compile(r'^\[ElevatorDepot\] half gone:')),
    ("depot_rows_read_only", re.compile(r'^\[ElevatorDepot\] underground rows are read-only')),
    ("depot_cabin_departed", re.compile(r'^\[ElevatorDepot\] cabin departed')),
    ("depot_cabin_arrived", re.compile(r'^\[ElevatorDepot\] cabin arrived')),
    ("transient_claim_failed", re.compile(r'^\[TrainHub\] transient claim failed')),
    ("module_inactive", re.compile(r'^\[(?:TrainBay|TrainDistribution|TrainHub|ElevatorDepot)\] inactive')),
    ("hub_track_job", re.compile(r'^\[TrainHub\] (?:repair|build) ')),
])


def newest_log():
    base = os.path.join(os.environ.get("APPDATA", ""), "Surviving Mars Relaunched", "logs")
    logs = glob.glob(os.path.join(base, "Mars.exe-*.log"))
    if not logs:
        raise SystemExit("no Mars.exe-*.log under " + base)
    return Path(max(logs, key=os.path.getmtime))


def fields(rest):
    out = {}
    for k, v in FIELD.findall(rest):
        if v.startswith('"'):
            v = bytes(v[1:-1], "utf-8").decode("unicode_escape")
        out[k] = v
    return out


def amounts(text):
    """'Metals:12.3,Food:4.0' -> {'Metals': 12.3, 'Food': 4.0}; 'none' -> {}"""
    out = {}
    if not text or text == "none":
        return out
    for part in text.split(","):
        name, _, value = part.rpartition(":")
        try:
            out[name] = float(value)
        except ValueError:
            pass
    return out


def read(path):
    raw = path.read_bytes().decode("utf-8", errors="replace").splitlines()
    records, seen = [], set()
    lua_errors, trace = [], Counter()
    for n, line in enumerate(raw, 1):
        if LUA_ERROR.search(line):
            lua_errors.append(n)
        for name, rx in TRACE.items():
            if rx.search(line):
                trace[name] += 1
        m = LINE.match(line)
        if not m:
            continue
        f = fields(m.group("rest"))
        key = (m.group("verb"), f.get("id"))
        if f.get("id") and key in seen:
            continue
        seen.add(key)
        records.append({"line": n, "verb": m.group("verb"), "f": f})
    return raw, records, lua_errors, trace


def segment(records):
    """One soak = SOAK_START .. SOAK_STOP (or end of log)."""
    soaks, cur = [], None
    for r in records:
        if r["verb"] == "SOAK_START":
            if cur:
                soaks.append(cur)
            cur = {"start": r, "stop": None, "records": []}
        elif cur is not None:
            cur["records"].append(r)
            if r["verb"] == "SOAK_STOP":
                cur["stop"] = r
                soaks.append(cur)
                cur = None
    if cur:
        soaks.append(cur)
    return soaks


def summarise(soak, examples):
    recs = soak["records"]
    totals = [r for r in recs if r["verb"] == "SOAK_TOTALS" and r["f"].get("h", "").lstrip("-").isdigit()]
    hours = [int(r["f"]["h"]) for r in totals]
    start_h = int(soak["start"]["f"].get("h", hours[0] if hours else 0))
    end_h = max(hours) if hours else start_h
    flags = [r for r in recs if r["verb"] == "SOAK_FLAG"]
    clears = Counter(r["f"].get("kind") for r in recs if r["verb"] == "SOAK_CLEAR")
    by_kind = OrderedDict()
    for r in flags:
        by_kind.setdefault(r["f"].get("kind", "?"), []).append(r)
    # per-resource drift per game hour between consecutive totals lines
    drift = defaultdict(lambda: {"first": None, "last": None, "max_up": 0.0, "max_down": 0.0})
    prev = None
    for r in totals:
        cur = (int(r["f"]["h"]), amounts(r["f"].get("all")))
        if prev is None:
            for res, v in cur[1].items():
                drift[res]["first"] = v
        else:
            dh = cur[0] - prev[0]
            if dh > 0:
                for res in set(prev[1]) | set(cur[1]):
                    rate = (cur[1].get(res, 0.0) - prev[1].get(res, 0.0)) / dh
                    d = drift[res]
                    if d["first"] is None:
                        d["first"] = prev[1].get(res, 0.0)
                    d["max_up"] = max(d["max_up"], rate)
                    d["max_down"] = min(d["max_down"], rate)
        prev = cur
    covered = end_h - start_h
    if prev:
        for res in drift:
            drift[res]["last"] = prev[1].get(res, 0.0)
    for res, d in drift.items():
        first, last = d["first"] or 0.0, d["last"] if d["last"] is not None else (d["first"] or 0.0)
        d["first"], d["last"] = first, last
        d["net"] = last - first
        d["per_hour"] = (last - first) / covered if covered > 0 else 0.0
    suppressed = max([int(r["f"].get("suppressed", 0)) for r in totals] or [0])
    events = Counter(r["f"].get("what") for r in recs if r["verb"] == "SOAK_EVENT")
    smrtk_errors = sum(1 for r in recs if r["verb"] == "ERROR")
    return {
        "start": {"line": soak["start"]["line"], **{k: soak["start"]["f"].get(k) for k in
                  ("sol", "h", "modules", "optin_version", "fixpack", "hubs", "stations", "depots", "trains")}},
        "stop": soak["stop"] and {"line": soak["stop"]["line"], **{k: soak["stop"]["f"].get(k) for k in
                                  ("reason", "hours", "flags", "suppressed", "errors", "trace_restored")}},
        "game_hours_covered": covered, "first_h": start_h, "last_h": end_h,
        "sols": [totals[0]["f"].get("sol"), totals[-1]["f"].get("sol")] if totals else None,
        "totals_lines": len(totals),
        "flags": OrderedDict((k, {"count": len(v), "cleared": clears.get(k, 0),
                                  "examples": [dict(line=r["line"], **r["f"]) for r in v[:examples]]})
                             for k, v in sorted(by_kind.items(), key=lambda kv: (-len(kv[1]), kv[0]))),
        "flags_total": len(flags), "suppressed": suppressed,
        "drift": OrderedDict(sorted(drift.items())), "events": dict(events),
        "smrtk_error_records": smrtk_errors,
        "lines_by_verb": dict(Counter(r["verb"] for r in recs if r["verb"].startswith("SOAK_"))),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log", nargs="?")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--examples", type=int, default=3)
    args = ap.parse_args()
    path = Path(args.log) if args.log else newest_log()
    raw, records, lua_errors, trace = read(path)
    soaks = [summarise(s, args.examples) for s in segment(records)]
    result = {"log": str(path), "lines": len(raw), "lua_error_lines": len(lua_errors),
              "lua_error_line_numbers": lua_errors[:50], "trace_counts": dict(trace), "soaks": soaks}
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print("log: %s (%d lines)" % (path, len(raw)))
    print("LUA ERROR lines: %d%s" % (len(lua_errors), (" at " + ", ".join(map(str, lua_errors[:20]))) if lua_errors else ""))
    print("trace lines: " + (", ".join("%s=%d" % kv for kv in trace.items()) or "none"))
    if not soaks:
        print("no SOAK_START in this log")
        return
    for i, s in enumerate(soaks, 1):
        st, sp = s["start"], s["stop"]
        print("\n=== soak %d: start line %d sol %s h %s | modules %s | opt-in %s | fix pack %s" % (
            i, st["line"], st["sol"], st["h"], st["modules"], st["optin_version"], st["fixpack"]))
        print("    at start: hubs %s stations %s depot halves %s trains %s" % (st["hubs"], st["stations"], st["depots"], st["trains"]))
        if sp:
            print("    stop line %d reason=%s flags=%s suppressed=%s errors=%s trace_restored=%s" % (
                sp["line"], sp["reason"], sp["flags"], sp["suppressed"], sp["errors"], sp["trace_restored"]))
        else:
            print("    no SOAK_STOP (still on when the log ended, or the game closed)")
        print("    game hours covered: %d (h %d..%d, sols %s), %d totals lines" % (
            s["game_hours_covered"], s["first_h"], s["last_h"], s["sols"], s["totals_lines"]))
        print("    events: " + (", ".join("%s=%d" % kv for kv in sorted(s["events"].items(), key=str)) or "none"))
        print("    SMRTK_ERROR records: %d" % s["smrtk_error_records"])
        print("    FLAGS: %d printed, %d suppressed by the per-hour cap" % (s["flags_total"], s["suppressed"]))
        for kind, info in s["flags"].items():
            print("      %-26s %4d  (cleared %d)" % (kind, info["count"], info["cleared"]))
            for ex in info["examples"]:
                detail = " ".join("%s=%s" % (k, v) for k, v in ex.items() if k not in ("kind", "t", "id", "line"))
                print("          line %d: %s" % (ex["line"], detail[:220]))
        if s["drift"]:
            print("    per-resource totals (hubs+stations+depots+trains+cabin), units:")
            print("      %-16s %10s %10s %10s %10s %10s %10s" % ("resource", "first", "last", "net", "net/h", "max+/h", "max-/h"))
            for res, d in s["drift"].items():
                print("      %-16s %10.1f %10.1f %10.1f %10.2f %10.1f %10.1f" % (
                    res, d["first"], d["last"], d["net"], d["per_hour"], d["max_up"], d["max_down"]))
        print("    lines by type: " + ", ".join("%s=%d" % kv for kv in sorted(s["lines_by_verb"].items())))


if __name__ == "__main__":
    main()
