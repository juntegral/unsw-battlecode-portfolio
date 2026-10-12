"""opp-uncancel: our queen's last N turns before death: every free neighbour with (gap to nearest foe head, that foe's length), and the one she took.
Usage: qlast.py <N> <gid> ..."""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque
from pathlib import Path

N = int(sys.argv[1])
for g in sys.argv[2:]:
    gid = int(g)
    mp = [Path(f) for f in glob.glob('data/online/live-one1/b*/game-%d.json' % gid)][0]
    j = json.load(open(mp))
    ours = 0 if j['teamAId'] == 1119 else 1
    root = replay.load(mp.parent / ('M%d.replay' % gid)).root()
    G = geometry(root.text(0))
    W, H, nb = G['W'], G['H'], G['nb']
    bodies = {i: deque(b) for i, b in G['bodies'].items()}
    teams = dict(G['teams'])
    Q = min(i for i in teams if teams[i] == ours)

    def gap(a, b):
        ax, ay, bx, by = a % W, a // W, b % W, b // W
        dx, dy = abs(ax - bx), abs(ay - by)
        return min(dx, W - dx) + min(dy, H - dy)

    turns = []
    rnd, actor, done = -1, None, False
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            actor = None
        elif k == 1:
            actor = p.i32(0)
            if actor == Q and Q in bodies:
                occ = set()
                for b in bodies.values():
                    occ.update(b)
                h = bodies[Q][0]
                foes = [(b[0], len(b), i) for i, b in bodies.items() if teams[i] != ours]
                mates = [(gap(h, b[0]), len(b)) for i, b in bodies.items() if i != Q and teams[i] == ours and gap(h, b[0]) <= 5]
                opts = {}
                for n in nb[h]:
                    if n in occ:
                        continue
                    near = sorted((gap(n, fh), L, i) for fh, L, i in foes)[:2]
                    opts[n] = near
                here = sorted((gap(h, fh), L, i) for fh, L, i in foes)[:3]
                turns.append(dict(r=rnd, L=len(bodies[Q]), h=h, opts=opts, here=here, mates=sorted(mates), path=[]))
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == Q and actor == Q and turns:
                    turns[-1]['path'].append(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            par, ch = p.i32(0), p.i32(4)
            for z, i in enumerate((par, ch)):
                bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
                teams[i] = p.u16(8)
        elif k == 11:
            i = p.i32(0)
            if i == Q:
                print('=== %d %s: queen dies r%d reason %d actor %s (L%s)' % (gid, j['mapName'], rnd, p.u16(4), actor, len(bodies[actor]) if actor in bodies else '?'))
                for t in turns[-N:]:
                    print('  r%d L%d at (%d,%d) foes here (gap,L,id) %s mates<=5 (gap,L) %s' % (t['r'], t['L'], t['h'] % W, t['h'] // W, t['here'], t['mates']))
                    for n, near in t['opts'].items():
                        print('      %s (%d,%d): nearest foes after step %s' % ('TOOK' if t['path'] and t['path'][0] == n else 'opt ', n % W, n // W, near))
                done = True
            bodies.pop(i)
        if done:
            break
