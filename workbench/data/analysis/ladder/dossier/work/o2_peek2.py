"""Scratch (diag-opening2): event kinds of one online, one ladder and one rank-1 replay; when countdown events come.
Usage: python3 .../o2_peek2.py"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from pathlib import Path
from collections import Counter

DOS = Path('data/analysis/ladder/dossier')


def show(path):
    root = replay.load(Path(path)).root()
    c = Counter()
    pre = 0
    rnd = -1
    first = []
    tiles = set()
    per_round = Counter()
    for ev in root.pointer(3):
        k = ev.u16(0)
        c[replay.EVENT_NAMES[k]] += 1
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
        if k == 2:
            if rnd < 0:
                pre += 1
            t = replay.point(p.pointer(0))
            tiles.add(t)
            per_round[rnd] += 1
            if len(first) < 6:
                first.append((rnd, t, p.i32(0)))
        if len(first) < 6 and k in (0, 1, 3) and rnd <= 1:
            first.append((rnd, replay.EVENT_NAMES[k]))
    print(path)
    print('  ', dict(c))
    print('   countdown events before round 0:', pre, 'distinct tiles', len(tiles), 'by round', sorted(per_round.items())[:6])
    print('  ', first)
    print('   bots', root.text(1), '|', root.text(2), '| version', root.u32(0))


def main():
    show('data/online/smoke/agg7-m1-new/M1397920.replay')
    for src in ('per-game.jsonl', 'target/per-game-top1.jsonl'):
        rows = [json.loads(x) for x in (DOS / src).read_text().splitlines()]
        rows = [r for r in rows if r['relation'] == 'us' and r['cells'] in (288, 875)]
        for r in (rows[0], rows[-1]):
            print(r['game'], r['map_name'], r['width'], r['height'], r['team'], r['our_side'], r.get('battle'))
            show(r['replay'])


main()
