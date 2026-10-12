"""loss15-sonnet: our queen's turns. Usage (via run2.sh): qtrace.py <gameid> <r0> <r1>
Per queen turn start in [r0, r1]: round, length, head, free neighbour cells, enemy heads within 6 (id, length), and when she splits / dies."""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque
from pathlib import Path

gid, r0, r1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); THEM = len(sys.argv) > 4; STEP = int(sys.argv[5]) if len(sys.argv) > 5 else 1
mp = [Path(f) for f in glob.glob('data/online/live-one1/b*/game-%d.json' % gid) + glob.glob('data/online/smoke/*-old/game-%d.json' % gid)][0]
j = json.load(open(mp))
rp = mp.parent / ('M%d.replay' % gid)
ours = 0 if j["teamAId"] == 1119 else 1
ours = 1 - ours if THEM else ours
root = replay.load(rp).root()
G = geometry(root.text(0))
W, H, nb = G['W'], G['H'], G['nb']
bodies = {i: deque(b) for i, b in G['bodies'].items()}
teams = dict(G['teams'])
Q = min(i for i in teams if teams[i] == ours)
rnd = -1
actor = None


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
        actor = None
        if rnd > r1:
            break
    elif k == 1:
        actor = p.i32(0)
        if actor == Q and r0 <= rnd <= r1 and Q in bodies and rnd % STEP == 0:
            occ = set()
            for b in bodies.values():
                occ.update(b)
            h = bodies[Q][0]
            fr = [n for n in nb[h] if n not in occ]
            foes = sorted((gap(h, b[0]), i, len(b)) for i, b in bodies.items() if teams[i] != ours and gap(h, b[0]) <= 6)
            mates = sum(1 for i, b in bodies.items() if i != Q and teams[i] == ours and gap(h, b[0]) <= 4)
            print('r%d Q%d L%d head(%d,%d) free %d mates<=4 %d foes<=6 %s' % (rnd, Q, len(bodies[Q]), h % W, h // W, len(fr), mates, foes[:4]))
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
        if r0 <= rnd <= r1 and Q in (par, ch):
            print('   r%d SPLIT queen -> parent %d L%d, child %d L%d (queen now L%d)' % (rnd, par, len(bodies[par]), ch, len(bodies[ch]), len(bodies[Q])))
    elif k == 11:
        i = p.i32(0)
        if i == Q and r0 <= rnd <= r1 + 5:
            print('   r%d QUEEN DIES (reason %d) L%d actor %s' % (rnd, p.u16(4), len(bodies[i]), actor))
        bodies.pop(i)
