#!/usr/bin/env python3
"""Compare matched local games: rams.py armA armB [map-substring]."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
from pathlib import Path
from statistics import mean
from count_local import key, fmt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('armA')
    parser.add_argument('armB')
    parser.add_argument('map_substring', nargs='?', default='')
    args = parser.parse_args()
    by = {arm: {} for arm in (args.armA, args.armB)}
    for line in (Path(__file__).resolve().parent/'rows.jsonl').read_text().splitlines():
        r = json.loads(line)
        if r['arm'] in by and args.map_substring in r['map']:
            by[r['arm']][key(r)] = r
    keys = sorted(by[args.armA].keys() & by[args.armB].keys())
    groups = [[by[arm][k] for k in keys] for arm in (args.armA, args.armB)]
    print(f'Matched games: {len(keys)}; A={args.armA}; B={args.armB}; filter={args.map_substring!r}')
    print('metric | A ours/theirs | B ours/theirs')
    fields = ('games', 'wins', 'ram_added_chances', 'ram_added_take_rate',
              'ram_twice_count', 'ram_twice_swing_per_meeting', 'ram_headons_started',
              'ram_meeting_net', 'alive_r300', 'longest_end')
    for field in fields:
        vals = []
        for rows in groups:
            if field in ('games', 'wins'):
                vals.append(str(len(rows) if field == 'games' else sum(r['result'] == 'win' for r in rows)))
                continue
            sides = []
            for s in ('ours', 'theirs'):
                ms = [r['measures'][s] for r in rows]
                if not ms:
                    sides.append('—')
                    continue
                if field == 'ram_added_take_rate':
                    value = sum(m['ram_added_taken'] for m in ms)/max(1, sum(m['ram_added_chances'] for m in ms))
                elif field == 'ram_twice_swing_per_meeting':
                    value = sum(m['ram_twice_swing_sum'] for m in ms)/max(1, sum(m['ram_twice_count'] for m in ms))
                else:
                    value = mean(m[field] for m in ms)
                sides.append(fmt(value))
            vals.append('/'.join(sides))
        print(field+' | '+' | '.join(vals))
    for field in fields[-3:]:
        vals = []
        for s in ('ours', 'theirs'):
            ds = [b['measures'][s][field]-a['measures'][s][field] for a, b in zip(*groups)]
            vals.append(fmt(mean(ds)) if ds else '—')
        print(f'Paired B-A {field} | '+ '/'.join(vals))
    print('Rates and swing are pooled; other measures and paired differences are game means; empty event pool=0.')


if __name__ == '__main__':
    main()
