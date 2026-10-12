"""Scratch (z54): map header and deaths of long dragons in a replay. Usage: python3 -B z54_probe.py <replay>"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter, deque
root = replay.load(sys.argv[1]).root()
lines = root.text(0).splitlines()
print(Counter(l.split()[0] for l in lines if l.split()))
for l in lines[:6]:
    print(l[:200])
print([l for l in lines if l.split() and l.split()[0] not in ('EDGE', 'DRAGON')][:20])
print('bots', root.text(1), '|', root.text(2))
bodies, teams = {}, {}
for l in lines:
    q = l.split()
    if q and q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
        teams[i] = int(q[1])
rnd = -1
for ev in root.pointer(3):
    k = ev.u16(0)
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
    elif k == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        b = bodies[i]
        if b[0] != hd:
            b.appendleft(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif k == 10:
        parent, child = p.i32(0), p.i32(4)
        for z, i in enumerate((parent, child)):
            bodies[i] = deque(replay.point(c) for c in p.pointer(z))
            teams[i] = p.u16(8)
    elif k == 11:
        i, reason = p.i32(0), p.u16(4)
        L = len(bodies[i])
        if L >= 10:
            print('death rnd', rnd, 'id', i, 'team', teams[i], 'len', L, 'reason', reason, 'head', bodies[i][0])
        bodies.pop(i)
print('last round', rnd)
