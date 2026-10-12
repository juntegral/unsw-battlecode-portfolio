"""Scratch (diag-opening2): list the games on two-dragon starts (each side starts with two dragons, total length 4 to 6)
in the three sources, by layout, and print one per-game row's keys. Usage: python3 .../o2_list.py"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter

DOS = Path('data/analysis/ladder/dossier')
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'agg7-b1', 'agg7-b2', 'agg8-q1', 'agg8-q2')


def main():
    for src, path in (('L', DOS / 'per-game.jsonl'), ('R', DOS / 'target/per-game-top1.jsonl')):
        rows = [json.loads(x) for x in path.read_text().splitlines()]
        if src == 'L':
            print(sorted(rows[0].keys()))
            print({k: rows[0][k] for k in ('game', 'replay', 'relation', 'cells', 'map', 'all_starting_dragons') if k in rows[0]})
        c = Counter()
        cnt = Counter()
        for r in rows:
            cnt[r['relation']] += 1
            if r['relation'] != 'us':
                continue
            st = r['all_starting_dragons']
            key = tuple(sorted(d['length'] for d in st['us'])), tuple(sorted(d['length'] for d in st['them']))
            two = all(len(st[s]) == 2 and 4 <= sum(d['length'] for d in st[s]) <= 6 for s in ('us', 'them'))
            c[(r.get('map'), r['cells'], key, two)] += 1
        print(src, dict(cnt))
        for k, v in sorted(c.items(), key=lambda kv: (not kv[0][3], kv[0][1])):
            print('  ', k, v)
    for label in LABELS:
        folder = Path('data/online/smoke') / (label + '-new')
        if not folder.is_dir():
            print(label, 'no folder')
            continue
        n = have = 0
        for mp in sorted(folder.glob('game-*.json')):
            j = json.loads(mp.read_text())
            n += 1
            have += (folder / ('M%d.replay' % j['id'])).exists()
        print(label, 'games', n, 'replays', have)
        if label == 'agg7-m1':
            print(sorted(j.keys()))
            print({k: j[k] for k in j if k not in ('replay',)})


main()
