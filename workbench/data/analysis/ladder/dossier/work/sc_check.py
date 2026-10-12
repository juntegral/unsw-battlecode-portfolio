# Scratch (diag-sacrifice): independent recount of the boxed-in test. Second implementation (x,y bodies, kelp read
# straight from the edge list, no Geo class) over every 10th game; compares the free-tile count of every death up
# to round 300 with the compact rows of sc_ev-*.jsonl. Heads beside a portal side are counted apart.
# Usage: python3 data/analysis/ladder/dossier/work/sc_check.py
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import deque, Counter
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
ev = {}
for n in range(4):
    for line in Path(W + 'sc_ev-%d.jsonl' % n).read_text().splitlines():
        if line:
            g = json.loads(line)
            ev[g['game']] = g
snap = json.loads(Path('data/analysis/ladder/dossier/input-snapshot.json').read_text())
rows = sorted(snap['rows'], key=lambda r: r['game'])[5::10]
tot = Counter()
for row in rows:
    path = Path('data/online/ladder') / str(row['battle']) / ('M%d.replay' % row['game'])
    root = replay.load(path).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    edges = canonical_edges(w, h, raw)
    ours = row['our_side']
    mine = []
    rnd, actor, act = 0, None, None
    for e in root.pointer(3):
        k = e.u16(0)
        if k not in (0, 1, 4, 9, 10, 11):
            continue
        p = e.pointer(0)
        if k == 0:
            rnd = p.i32(0)
        elif k == 1:
            actor = p.i32(0)
            act = None
        elif k == 4:
            a = p.pointer(0)
            act = a.u16(0) if a else 2
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if rnd <= 300:
                occupied = set()
                for b in bodies.values():
                    occupied.update(b)
                x, y = bodies[i][0]
                free, portal = 0, False
                for d in range(4):
                    kind = edges.get(edge_id(w, h, x, y, d), (0, -1))[0]
                    if kind == 2:
                        portal = True
                    elif kind == 0 and ((x + STEP[d][0]) % w, (y + STEP[d][1]) % h) not in occupied:
                        free += 1
                mine.append((rnd, 'u' if teams[i] == ours else 't', len(bodies[i]), reason, free, portal, act if i == actor else None))
            bodies.pop(i)
    theirs = ev[row['game']]['compact']
    assert len(mine) == len(theirs), (row['game'], len(mine), len(theirs))
    for a, c in zip(mine, theirs):
        assert a[0] == c[0] and a[1] == c[1] and a[2] == c[2], (row['game'], a, c)
        tot['deaths'] += 1
        if a[5]:
            tot['beside a portal side (not compared)'] += 1
            continue
        tot['compared'] += 1
        tot['same free count'] += int(a[4] == c[4])
        tot['same boxed verdict'] += int((a[4] == 0) == (c[4] == 0))
        if a[3] != 3:
            tot[a[1], 'nonram', 'boxed' if a[4] == 0 else 'free'] += 1
        if a[3] == 4 and a[1] == 't' and a[6] == 2 and a[0] <= 100:
            tot['their no order r0-100', 'boxed' if a[4] == 0 else 'free'] += 1
print('games', len(rows))
for k, v in sorted(tot.items(), key=str):
    print(' ', k, v)
