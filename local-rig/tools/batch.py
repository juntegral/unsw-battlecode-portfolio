#!/usr/bin/env python3
"""Run every map with both side orders, one game at a time through play.sh."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def plan(bot_a, bot_b, group, seeds, output):
    maps = sorted((ROOT / 'maps' / group).glob('*.map'))
    for map_path in maps:
        for seed in seeds:
            for side in (0, 1):
                a, b = (bot_a, bot_b) if side == 0 else (bot_b, bot_a)
                folder = output / map_path.stem / f'seed-{seed}-A-side-{side}'
                yield map_path, seed, side, folder, [str(ROOT / 'play.sh'), str(a), str(b),
                                                   str(map_path), str(seed), str(folder)]


def summary(rows):
    by_map = defaultdict(list)
    for row in rows:
        by_map[row['map_name']].append(row)
    lines = ['Wins refer to the first bot supplied to batch.sh.',
             'map | side | games | first-bot wins | other-bot wins | draws | how games ended']
    for name, records in sorted(by_map.items()):
        for side in (0, 1):
            games = [r for r in records if r['first_bot_side'] == side]
            wins = sum(r['winner'] == side for r in games)
            losses = sum(r['winner'] == 1-side for r in games)
            draws = sum(r['winner'] == 'draw' for r in games)
            how = Counter(f'{r["how"]}: {r["verdict"]}' for r in games)
            ends = '; '.join(f'{key}={value}' for key, value in sorted(how.items()))
            lines.append(f'{name} | {side} | {len(games)} | {wins} | {losses} | {draws} | {ends}')
    wins = sum(r['winner'] == r['first_bot_side'] for r in rows)
    losses = sum(r['winner'] == 1-r['first_bot_side'] for r in rows)
    draws = sum(r['winner'] == 'draw' for r in rows)
    lines.append(f'TOTAL | both | {len(rows)} | {wins} | {losses} | {draws}')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('botA', type=Path)
    parser.add_argument('botB', type=Path)
    parser.add_argument('group', choices=['dev', 'eval'])
    parser.add_argument('seeds', help='comma-separated integers, e.g. 1,2,3 (quote spaces)')
    parser.add_argument('out_dir', type=Path)
    args = parser.parse_args()
    try:
        seeds = list(dict.fromkeys(int(s, 0) for s in re.split(r'[,\s]+', args.seeds.strip()) if s))
    except ValueError:
        parser.error('seeds must be comma-separated or space-separated integers')
    if not seeds or any(not 0 <= seed < 2**64 for seed in seeds):
        parser.error('provide at least one unsigned 64-bit seed')
    output = args.out_dir.resolve()
    if not output.is_relative_to(ROOT):
        parser.error('output must be inside the workspace')
    if output.exists() and any(output.iterdir()):
        parser.error('output directory must be empty')
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for map_path, seed, side, folder, command in plan(args.botA.resolve(), args.botB.resolve(),
                                                    args.group, seeds, output):
        subprocess.run(command, check=True)
        row = json.loads((folder / 'result.json').read_text())
        row.update(map_name=map_path.stem, first_bot_side=side)
        rows.append(row)
        with (output / 'rows.jsonl').open('a') as progress:
            progress.write(json.dumps(row) + '\n')
    table = summary(rows)
    (output / 'summary.txt').write_text(table + '\n')
    (output / 'summary.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(table)


if __name__ == '__main__':
    try:
        main()
    except (subprocess.CalledProcessError, OSError) as error:
        print(f'batch failed: {error}', file=sys.stderr)
        sys.exit(1)
