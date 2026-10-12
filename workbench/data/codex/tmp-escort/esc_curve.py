"""esc_curve.py <arm> <game> : own and enemy dragons and total length every 10 rounds, and head-ons by who moved, per 10 rounds."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/local')
from replay_format import load, point
from pathlib import Path
from collections import Counter

arm, game = sys.argv[1], sys.argv[2]
side = int(game[-1])
root = load(Path('~/meow-redteam/solo/runs') / arm / game / 'game.replay').root()
L, T = {}, {}
for line in root.text(0).splitlines():
    q = line.split('#', 1)[0].split()
    if q and q[0] == 'DRAGON':
        i = len(L)
        L[i] = int(q[2])
        T[i] = 0 if int(q[1]) == side else 1
rnd, actor = -1, None
ho = Counter()
rows = []
bodies = {}
for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        if rnd >= 0 and rnd % 10 == 0:
            rows.append((rnd, sum(1 for i in L if T[i] == 0), sum(v for i, v in L.items() if T[i] == 0),
                         sum(1 for i in L if T[i] == 1), sum(v for i, v in L.items() if T[i] == 1), dict(ho)))
            ho = Counter()
        rnd, actor = p.i32(0), None
    elif k == 1:
        actor = p.i32(0)
    elif k == 9:
        pass
    elif k == 10:
        parent, child = p.i32(0), p.i32(4)
        T[child] = T[parent]
        L[parent], L[child] = len(list(p.pointer(0))), len(list(p.pointer(1)))
    elif k == 11:
        i, reason = p.i32(0), p.u16(4)
        if reason == 3:
            ho[('we' if T[i] == 0 else 'they') + ('_moved' if i == actor else '_hit')] += 1
        else:
            ho[('we' if T[i] == 0 else 'they') + '_self'] += 1
        L.pop(i)
        T.pop(i)
for r in rows[:16]:
    print(r)
