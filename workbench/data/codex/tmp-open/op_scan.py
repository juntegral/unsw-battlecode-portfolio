#!/usr/bin/env python3
"""op_scan.py <arm> [<arm>...] : opening counts for our side of each game under solo/runs/<arm>/, one JSON line a game to op_<arm>.jsonl."""
import sys
sys.dont_write_bytecode = True
import json
import os
from collections import deque, Counter
from pathlib import Path
L = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/local'
sys.path.insert(0, L)
from replay_format import load, point
from count_local import Geo

HERE = Path(__file__).resolve().parent
RUNS = Path(os.path.expanduser('~/meow-redteam/solo/runs'))
MARKS = (10, 20, 40, 60, 100, 150, 300)
REASON = {0: 'wall', 1: 'own', 2: 'body', 3: 'head'}


def scan(path, our):
    root = load(path).root()
    bodies, teams, raw = {}, {}, []
    w = h = 0
    for line in root.text(0).splitlines():
        q = line.split('#', 1)[0].split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = map(int, q[1:3])
        elif q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    g = Geo(w, h, raw)
    nport = sum(1 for row in g.moves for k, t in row if k == 2)
    tile = lambda p: p[1]*w+p[0]
    xy = lambda c: (c % w, c // w)
    mine = lambda i: teams[i] == our
    starters = sorted(i for i in bodies if mine(i))
    queen = starters[0]
    line = {i: i for i in bodies}
    born = {i: -1 for i in bodies}
    first_split = {i: None for i in starters}
    start_len = {i: len(bodies[i]) for i in starters}
    enemy_start = sorted(len(b) for i, b in bodies.items() if not mine(i))
    pearls_by = Counter()
    portal_first = {}
    snaps = {}
    qsnap = {}
    deaths = []
    splits = []
    qsplits = []
    qturn4 = qsplit4 = 0
    q2hunt = 0
    qmin40 = None
    qdeath = None
    pearls = 0
    rnd, actor = -1, None
    eaten_first = {}

    def man(a, c):
        dx, dy = abs(a % w-c % w), abs(a // w-c // w)
        return min(dx, w-dx)+min(dy, h-dy)

    def snap():
        ours = [len(b) for i, b in bodies.items() if mine(i)]
        return dict(n=len(ours), tot=sum(ours), pearls=pearls, q=len(bodies[queen]) if queen in bodies else 0)

    def near_enemy(c):
        return min((man(c, b[0]) for i, b in bodies.items() if not mine(i)), default=99)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            if rnd >= 0:
                snaps[rnd] = snap()
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            if actor == queen and rnd <= 40:
                Lq = len(bodies[queen])
                qmin40 = Lq if qmin40 is None else min(qmin40, Lq)
                if Lq >= 4:
                    qturn4 += 1
                if Lq <= 2 and near_enemy(bodies[queen][0]) <= 4:
                    q2hunt += 1
        elif k == 3:
            if not p.bit(0) and actor is not None and mine(actor):
                pearls += 1
                eaten_first.setdefault(line[actor], rnd)
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(point(p.pointer(0))), tile(point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                old = b[0]
                kinds = [kk for kk, t in g.moves[old] if t == hd]
                if kinds and all(kk == 2 for kk in kinds) and mine(i):
                    portal_first.setdefault(line[i], rnd)
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            before = len(bodies[parent])
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(point(c)) for c in p.pointer(z))
            teams[child] = teams[parent]
            line[child] = line[parent]
            born[child] = rnd
            if mine(parent):
                if parent in first_split and first_split[parent] is None:
                    first_split[parent] = rnd
                if parent == queen and rnd <= 40 and before >= 4:
                    qsplit4 += 1
                if parent == queen and rnd < 40:
                    qsplits.append([rnd, before, near_enemy(bodies[parent][0])])
                if rnd <= 60:
                    splits.append([rnd, parent, before, len(bodies[child]), near_enemy(bodies[parent][0])])
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies.pop(i)
            if mine(i):
                if reason == 3:
                    if i == actor:
                        cause = 'rams-head'
                    else:
                        cause = 'rammed-by-' + ('mate' if actor is not None and mine(actor) else 'enemy')
                else:
                    cause = REASON.get(reason, 'noact%d' % reason)
                rec = [rnd, i, len(b), cause, born[i], list(xy(b[0]))]
                if rnd <= 100:
                    deaths.append(rec)
                if i == queen:
                    qdeath = rec
    snaps[rnd] = snap()
    last = rnd
    out = dict(w=w, h=h, cells=w*h, portal_edges=nport, rounds=last, starters=[start_len[i] for i in starters],
               enemy_starters=enemy_start, queen=queen,
               first_split=[first_split[i] for i in starters], queen_first_split=first_split[queen],
               portal_first={str(k2): v for k2, v in portal_first.items()},
               portal_r10=int(any(v <= 10 for v in portal_first.values())),
               portal_r20=int(any(v <= 20 for v in portal_first.values())),
               portal_nq_r10=int(any(v <= 10 for k2, v in portal_first.items() if k2 != queen)),
               portal_nq_r20=int(any(v <= 20 for k2, v in portal_first.items() if k2 != queen)),
               qturn4=qturn4, qsplit4=qsplit4, q2hunt=q2hunt, qmin40=qmin40, qdeath=qdeath,
               deaths_r5=[d for d in deaths if d[0] <= 5],
               deaths_child10=[d for d in deaths if 0 <= d[4] <= 1 and d[0]-d[4] <= 10],
               ndeaths_r40=sum(1 for d in deaths if d[0] <= 40),
               splits=splits[:12], qsplits=qsplits, eaten_first={str(k2): v for k2, v in eaten_first.items()})
    for r in MARKS:
        s = snaps.get(r, snaps[last] if r > last else None)
        for f in ('n', 'tot', 'pearls', 'q'):
            out[f'{f}_r{r}'] = s[f]
    out['q_end'] = snaps[last]['q']
    return out


def main():
    for arm in sys.argv[1:]:
        rows = []
        for d in sorted((RUNS/arm).iterdir()):
            f = d/'game.replay'
            if not f.exists() or not (d/'result.txt').exists():
                continue
            name = d.name
            our = int(name.rsplit('-side', 1)[1])
            try:
                row = scan(f, our)
            except Exception as e:
                print('ERR', arm, name, repr(e), file=sys.stderr)
                continue
            row.update(arm=arm, game=name, map=name.split('-seed')[0], side=our, result=(d/'result.txt').read_text().strip())
            rows.append(row)
        with open(HERE/f'op_{arm}.jsonl', 'w') as fh:
            for row in rows:
                fh.write(json.dumps(row)+'\n')
        print(arm, len(rows))


if __name__ == '__main__':
    main()
