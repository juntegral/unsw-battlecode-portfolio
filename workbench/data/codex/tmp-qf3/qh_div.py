#!/usr/bin/env python3
"""First round at which two local replays of the same game differ (moves, splits, deaths compared in order).
Usage: python3 qh_div.py <arm a> <arm b> [game ...]   (default: every game both arms have)"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
LOCAL = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/local'
sys.path.insert(0, LOCAL)
from replay_format import load, point

RUNS = Path('~/meow-redteam/solo/runs')


def stream(path):
    rnd = -1
    for ev in load(path).root().pointer(3):
        k = ev.u16(0)
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
        elif k == 9:
            yield rnd, (9, p.i32(0), point(p.pointer(0)), point(p.pointer(1)))
        elif k == 10:
            yield rnd, (10, p.i32(0), p.i32(4))
        elif k == 11:
            yield rnd, (11, p.i32(0), p.u16(4))


a, b = sys.argv[1], sys.argv[2]
names = sys.argv[3:] or sorted(d.name for d in (RUNS / b).iterdir()
                               if (d / 'result.txt').exists() and (RUNS / a / d.name / 'result.txt').exists())
for n in names:
    first = None
    sa, sb = stream(RUNS / a / n / 'game.replay'), stream(RUNS / b / n / 'game.replay')
    while True:
        x, y = next(sa, None), next(sb, None)
        if x is None and y is None:
            break
        if x != y:
            first = (x or y)[0]
            break
    print(n, 'identical' if first is None else 'first differs in round %d' % first)
