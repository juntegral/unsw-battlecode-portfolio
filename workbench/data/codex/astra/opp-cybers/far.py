"""opp-cybers: at r400/425/450, per side, how many dragons have their head within 15 of the side's longest dragon. Usage (ROOT): python3 -B far.py <gameid> ..."""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque
from pathlib import Path

for gid in map(int, sys.argv[1:]):
    mp = [Path(f) for f in glob.glob('data/online/live-one1/b*/game-%d.json' % gid)][0]
    j = json.load(open(mp))
    ours = 0 if j['teamAId'] == 1119 else 1
    root = replay.load(mp.parent / ('M%d.replay' % gid)).root()
    G = geometry(root.text(0))
    W, H = G['W'], G['H']
    bodies = {i: deque(b) for i, b in G['bodies'].items()}
    teams = dict(G['teams'])
    done = set()

    def gap(a, b):
        ax, ay, bx, by = a % W, a // W, b % W, b // W
        dx, dy = abs(ax - bx), abs(ay - by)
        return min(dx, W - dx) + min(dy, H - dy)

    print('=== %d %s %dx%d' % (gid, j['mapName'], W, H))
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            if rnd in (350, 400, 425, 450, 475) and rnd not in done:
                done.add(rnd)
                out = []
                for s, nm in ((ours, 'us'), (1 - ours, 'them')):
                    mine = [b for i, b in bodies.items() if teams[i] == s]
                    if not mine:
                        continue
                    top = max(mine, key=len)
                    near = sum(1 for b in mine if b is not top and gap(b[0], top[0]) <= 15)
                    out.append('%s longest %d, others %d, within 15 of it %d' % (nm, len(top), len(mine) - 1, near))
                print('  r%d  %s' % (rnd, ' | '.join(out)))
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
        elif k == 11:
            bodies.pop(p.i32(0), None)
