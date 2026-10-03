"""Reproduce 34b's attended log counts; no game or code mutation.

Only primary [mod] [SMRTK] lines count, excluding console mirrors and ring copies.
Ledger event time is game_time; its t is the later dump time.
"""
import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

PREFIX = '[mod] [SMRTK] '
FIELD = re.compile(r'(\w+)=("(?:[^"\\]|\\.)*"|\S+)')


def read(path):
    data = path.read_bytes()
    rows, clock = [], None
    lines = data.decode('utf8', errors='replace').splitlines()
    for lineno, line in enumerate(lines, 1):
        stamp = re.fullmatch(r'\s*Lua (\d+):(\d+):(\d+):(\d+)\s*', line)
        if stamp:
            h, m, s, ms = map(int, stamp.groups())
            clock = ((h * 60 + m) * 60 + s) * 1000 + ms
        if line.startswith(PREFIX):
            fields = {k: (json.loads(v) if v.startswith('"') else v)
                      for k, v in FIELD.findall(line)}
            fields.update(verb=line[len(PREFIX):].split(' ', 1)[0], line=lineno,
                          boot_clock_ms=clock)
            rows.append(fields)
    return rows, lines, {'file': path.name, 'bytes': len(data),
                         'sha256': hashlib.sha256(data).hexdigest()}


def members(rows, key):
    parts = dict(sorted(Counter(r[key] for r in rows).items()))
    assert sum(parts.values()) == len(rows)
    return {'total': len(rows), 'members': parts}


def n(row, key):
    return Decimal(row[key])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sitting1', type=Path, required=True)
    ap.add_argument('--sitting2', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    old, _, old_id = read(args.sitting1)
    rows, lines, identity = read(args.sitting2)
    hauls = [r for r in rows if r['verb'] == 'SMRTK_STREAM' and r.get('row') == 'haul']
    exports = [r for r in hauls if r['destination_is_export_station'] == 'true']
    export_below = [r for r in exports if n(r, 'source_after') < n(r, 'source_desired')]
    stops = [r for r in rows if r['verb'] == 'SMRTK_STREAM' and r.get('row') == 'stop']
    arms = [r for r in rows if r['verb'] == 'SMRTK_ARM' and r.get('action') == 'slot_9']
    intervals = []
    for arm, stop in zip(arms, stops, strict=True):
        contained = [r for r in hauls if arm['line'] < r['line'] < stop['line']]
        assert len(contained) == int(stop['hauls']), 'stream stop tally mismatch'
        intervals.append({'arm_line': arm['line'], 'start': arm['t'],
                          'stop_line': stop['line'], 'end': stop['t'],
                          'reason': stop['reason'], 'hauls': len(contained)})
    assert sum(i['hauls'] for i in intervals) == len(hauls)
    ledger = [r for r in rows if r.get('ledger') == 'witness' and r.get('leg') == 'pairing']
    bad = [r for r in ledger if r['export_below_floor'] == 'true']
    gap_start, gap_end = int(intervals[0]['end']), int(intervals[1]['start'])
    in_gap = [r for r in bad if gap_start < int(r['game_time']) < gap_end]
    raw_bad = [r for r in bad if n(r, 'supply_actual') - n(r, 'amount') < n(r, 'supply_desired')]
    already_below = [r for r in bad if n(r, 'supply_actual') < n(r, 'supply_desired')]
    assert len(in_gap) == len(raw_bad) == len(already_below) == len(bad), 'reconciliation changed'
    sol = [r for r in rows if r['verb'] == 'SMRTK_TRIGGER' and r.get('verdict') == 'sol_done']
    for r in sol:
        assert int(r['filter_retried']) == int(r['filter_refused']) + int(r['filter_substituted'])
        assert int(r['export_below_floor']) == len(bad)
    counters = ['calls', 'pairings', 'filter_retried', 'filter_refused',
                'filter_substituted', 'filter_capped', 'export_from_storage',
                'export_from_producer', 'export_below_floor']
    delta = {k: int(sol[1][k]) - int(sol[0][k]) for k in counters}
    cost = []
    for label, r in [('first completion, cumulative', sol[0]),
                     ('second completion, cumulative', sol[1]), ('second interval delta', delta)]:
        c = {k: int(r[k]) for k in counters}
        c.update(label=label, retry_fraction_of_calls=c['filter_retried']/c['calls'],
                 refused_fraction_of_retries=c['filter_refused']/c['filter_retried'])
        cost.append(c)
    snapshots = [r for r in rows if r['verb'] == 'SMRTK_STREAM' and r.get('row') == 'snapshot']
    snapshot_ends = [r for r in rows if r['verb'] == 'SMRTK_STREAM' and r.get('row') == 'snapshot_end']
    grouped = defaultdict(list)
    for r in snapshots:
        grouped[(r['t'], r['phase'])].append(r)
    assert len(grouped) == len(snapshot_ends)
    for r in snapshot_ends:
        assert len(grouped[r['t'], r['phase']]) == int(r['stores'])
    wanted = ['StorageFood(1067)', 'StorageFood(10907)']
    depot_snapshots = {store: [{k:r[k] for k in ['line','t','phase','stock','desired']}
                             for r in snapshots if r['store'] == store and r['resource'] == 'Food']
                       for store in wanted}
    diners = [r for r in hauls if r['source'] in wanted and r['destination'].startswith('Diner(')]
    reads = [r for r in rows if r['verb'] == 'SMRTK_ACTION' and r.get('action') in ['slot_4','slot_5']]
    bay = [(i,line) for i,line in enumerate(lines,1) if '[TrainBay]' in line]
    refusal = [(i,line) for i,line in bay if '[TrainBay] refused ' in line]
    spawn = [(i,line) for i,line in bay if re.search(r'\[TrainBay\] (fill|spawn)\b', line)]
    errors = [(i,line) for i,line in enumerate(lines,1) if re.search(r'SMRTK_ERROR|LUA ERROR',line)]
    # Sitting 1 is an observational characterization, not a proof of the C truth table.
    pairs = [r for r in old if r.get('ledger') == 'witness' and r.get('leg') == 'pairing']
    desired = defaultdict(set)
    for r in pairs:
        desired[r['supply'],r['resource']].add(r['supply_desired'])
    classifications, branches = Counter(), Counter()
    inferred = {}
    # Archived 1.1.1.406343 capacities: StorageDepot.lua:332,
    # Elevator.lua:16, Norman StorageSugar/StorageSpices.generated.lua:29.
    # Station capacity is also read in this boot. Native demand desired is
    # capacity minus the storage's Desired slider; source observations win.
    capacities = {'UniversalStorageDepot': Decimal(30), 'Elevator': Decimal(50),
                  'StationSmall': Decimal(120), 'StorageSugar': Decimal(180),
                  'StorageSpices': Decimal(180)}
    capacity_inferred = []
    for r in pairs:
        key = r['demand'],r['resource']
        values = desired[key]
        if not values:
            # Same boot's actual row read, not the failed capacity demand write.
            supply_desired = {s['supply_desired'] for s in old
                              if s.get('station') == key[0] and s.get('resource') == key[1]
                              and 'supply_desired' in s}
            values = supply_desired
        if not values:
            cls = r['demand'].split('(')[0]
            assert cls in capacities, ('unread capacity', cls)
            assert n(r, 'demand_target') > n(r, 'demand_desired'), 'partition needs live destination Desired'
            values = {str(capacities[cls] - n(r, 'demand_desired'))}
            capacity_inferred.append({'line':r['line'], 'destination':r['demand'],
                                      'resource':r['resource'], 'capacity':str(capacities[cls]),
                                      'desired':next(iter(values))})
        assert len(values) == 1, ('destination desired is not uniquely established',key,values)
        want = n(r,'demand_target') > n(r,'demand_desired')
        rank = Decimal(next(iter(values))) > n(r,'supply_desired')
        push = n(r,'supply_actual') > n(r,'supply_desired')
        for label,yes in [('want',want),('rank',rank),('push',push)]:
            if yes: branches[label] += 1
        classifications['+'.join(label for label,yes in [('want',want),('rank',rank),('push',push)] if yes) or 'none'] += 1
        inferred[' / '.join(key)] = next(iter(values))
    assert sum(classifications.values()) == len(pairs)
    old_below = [r for r in pairs if n(r,'supply_actual') - n(r,'amount') < n(r,'supply_desired')]
    result = {'command': subprocess.list2cmdline([sys.executable,*sys.argv]),
              'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              'build':'game 1.1.1.406343 build 25579348',
              'filter': 'primary [mod] [SMRTK]; STREAM row=haul/snapshot; ledger=witness leg=pairing; use game_time for ledger events',
              'sitting2':identity, 'stream_intervals':intervals,
              'stream_hauls_by_export':members(hauls,'destination_is_export_station'),
              'stream_exports_by_source':members(exports,'source'),
              'stream_export_below_desired':export_below,
              'witness_below':bad,
              'reconciliation': {'all_flags_in_stream_gap':len(in_gap),
                                 'raw_actual_minus_amount_below':len(raw_bad),
                                 'already_below_before_pairing':len(already_below),
                                 'reservation_only':len(bad)-len(raw_bad),
                                 'gap_game_ms':gap_end-gap_start},
              'sol_completions':sol, 'filter_cost':cost,
              'snapshot_total':len(snapshots),'snapshot_groups':len(grouped),
              'depot_snapshots':depot_snapshots, 'diner_draws':diners,
              'train_reads':reads, 'trainbay_lines':bay,'trainbay_refused':refusal,
              'trainbay_fill_spawn':spawn,'error_markers':errors,
              'sitting1':old_id,'matcher_pairs':len(pairs),
              'matcher_branches_overlap':dict(branches),
              'matcher_disjoint_members':dict(sorted(classifications.items())),
              'matcher_priority_partition':{
                  'want':sum(v for k,v in classifications.items() if 'want' in k.split('+')),
                  'not_want_rank':sum(v for k,v in classifications.items() if 'want' not in k.split('+') and 'rank' in k.split('+')),
                  'neither_want_nor_rank_push':classifications['push'],
                  'none':classifications['none']},
              'matcher_overlap_limit':'Rank totals involving capacity-inferred destinations use base capacities, not live upgraded values; priority partition does not depend on those want=true rows.',
              'matcher_below_desired':members(old_below,'demand'),
              'matcher_export_below_sources':members([r for r in old_below if r['demand']=='StationSmall(10650)'],'supply'),
              'matcher_destination_desired':inferred,
              'matcher_capacity_inferred_rows':capacity_inferred}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:result[k] for k in ['head','stream_intervals','stream_hauls_by_export',
                     'stream_exports_by_source','reconciliation','filter_cost','matcher_pairs',
                     'matcher_branches_overlap','matcher_disjoint_members','matcher_below_desired']},indent=2))
    print('receipt:',args.output)


if __name__ == '__main__':
    main()
