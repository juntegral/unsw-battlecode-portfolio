#!/usr/bin/env python3
"""Compare matched local games: leader.py armA armB [map-substring]."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
from statistics import mean
from pathlib import Path
from count_local import LEADER_FIELDS, key, metric_value, fmt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('armA')
    parser.add_argument('armB')
    parser.add_argument('map_substring', nargs='?', default='')
    args = parser.parse_args()
    by = {arm: {} for arm in (args.armA, args.armB)}
    for line in (Path(__file__).resolve().parent/'rows.jsonl').read_text().splitlines():
        row = json.loads(line)
        if row['arm'] in by and args.map_substring in row['map']:
            by[row['arm']][key(row)] = row
    keys = sorted(by[args.armA].keys() & by[args.armB].keys())
    pairs = [(by[args.armA][k], by[args.armB][k]) for k in keys]
    print(f'Matched games: {len(pairs)}; A={args.armA}; B={args.armB}; filter={args.map_substring!r}')
    print('metric | A ours/theirs | B ours/theirs')
    for field in ('games', 'wins') + LEADER_FIELDS:
        values = []
        for index in (0, 1):
            games = [pair[index] for pair in pairs]
            if field == 'games':
                values.append(str(len(games)))
            elif field == 'wins':
                values.append(str(sum(r['result'] == 'win' for r in games)))
            else:
                values.append('/'.join(fmt(mean(metric_value(r['measures'][s][field]) for r in games)) if games else '—' for s in ('ours', 'theirs')))
        print(f'{field} | '+ ' | '.join(values))
    longest = [b['measures']['ours']['longest_end']-a['measures']['ours']['longest_end'] for a, b in pairs]
    wins = [int(b['result'] == 'win')-int(a['result'] == 'win') for a, b in pairs]
    print(f'Paired B-A (ours): longest_end mean={fmt(mean(longest)) if pairs else "—"}; wins mean={fmt(mean(wins)) if pairs else "—"}, net={sum(wins)}')
    print('List means: per-game event mean, empty=0; kept share with no late peak=0.')


if __name__ == '__main__':
    main()
