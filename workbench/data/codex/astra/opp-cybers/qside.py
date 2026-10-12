"""opp-cybers: both queens' habits, same code for both sides. Usage (ROOT): python3 -B qside.py <gameid> ...
Per side, per 50-round window: queen turns, mean length, mean free neighbours, share of turns with free<=1, mean mates within 4,
mean gap to nearest foe head, gap from her start cell; plus first side split round, queen split rounds, queen death."""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque, defaultdict
from pathlib import Path

for gid in map(int, sys.argv[1:]):
    mp = [Path(f) for f in glob.glob('data/online/live-one1/b*/game-%d.json' % gid) + glob.glob('data/online/smoke/*-old/game-%d.json' % gid)][0]
    j = json.load(open(mp))
    ours = 0 if j['teamAId'] == 1119 else 1
    root = replay.load(mp.parent / ('M%d.replay' % gid)).root()
    G = geometry(root.text(0))
    W, H, nb = G['W'], G['H'], G['nb']
    bodies = {i: deque(b) for i, b in G['bodies'].items()}
    teams = dict(G['teams'])
    Q = {s: min(i for i in teams if teams[i] == s) for s in (0, 1)}
    start = {s: bodies[Q[s]][0] for s in (0, 1)}
    acc = {s: defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0]) for s in (0, 1)}
    first_split = {0: None, 1: None}
    qsplit = {0: [], 1: []}
    qdie = {0: None, 1: None}
    rnd = -1

    def gap(a, b):
        ax, ay, bx, by = a % W, a // W, b % W, b // W
        dx, dy = abs(ax - bx), abs(ay - by)
        return min(dx, W - dx) + min(dy, H - dy)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
        elif k == 1:
            a = p.i32(0)
            for s in (0, 1):
                if a == Q[s] and a in bodies:
                    occ = set()
                    for b in bodies.values():
                        occ.update(b)
                    h = bodies[a][0]
                    fr = sum(1 for n in nb[h] if n not in occ)
                    fg = [gap(h, b[0]) for i, b in bodies.items() if teams[i] != s]
                    mates = sum(1 for i, b in bodies.items() if i != a and teams[i] == s and gap(h, b[0]) <= 4)
                    x = acc[s][rnd // 50]
                    x[0] += 1
                    x[1] += len(bodies[a])
                    x[2] += fr
                    x[3] += fr <= 1
                    x[4] += mates
                    x[5] += min(fg) if fg else 99
                    x[6] += gap(h, start[s])
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            par, ch = p.i32(0), p.i32(4)
            for z, i in enumerate((par, ch)):
                bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
                teams[i] = p.u16(8)
            s = teams[par]
            if first_split[s] is None:
                first_split[s] = rnd
            if par == Q[s] or ch == Q[s]:
                qsplit[s].append(rnd)
        elif k == 11:
            i = p.i32(0)
            for s in (0, 1):
                if i == Q[s]:
                    qdie[s] = (rnd, len(bodies[i]), p.u16(4))
            bodies.pop(i, None)
    print('=== %d %s seat %s winner %s' % (gid, j['mapName'], 'AB'[ours], j['winner']))
    for s, name in ((ours, 'US  '), (1 - ours, 'THEM')):
        print(' %s first split r%s, queen splits %d (first %s), queen death %s' % (name, first_split[s], len(qsplit[s]), qsplit[s][:4], qdie[s]))
        for w in sorted(acc[s]):
            n, L, f, f1, m, fg, d = acc[s][w]
            print('   r%3d+ turns %2d  L %.1f  free %.2f  free<=1 %2d%%  mates<=4 %.1f  nearest foe %.1f  from start %.1f' % (w * 50, n, L / n, f / n, 100 * f1 / n, m / n, fg / n, d / n))
