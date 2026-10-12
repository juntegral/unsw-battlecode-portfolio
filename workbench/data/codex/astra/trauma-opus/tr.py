"""tr.py <replay> <own seat 0/1> <r0> <r1> [step]: heads per round both sides, pearls, jumps (portal/wrap). Run from ROOT."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
path, own, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
step = int(sys.argv[5]) if len(sys.argv) > 5 else 1
root = replay.load(path).root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
bodies, teams = {}, {}
for line in lines:
    q = line.split()
    if q and q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
        teams[i] = int(q[1])
pearls = set()
rnd = -1
jumps = {0: [], 1: []}
eats = {0: [], 1: []}
actor = None


def side(i):
    return 0 if teams[i] == own else 1


def dump():
    if r0 <= rnd <= r1 and (rnd - r0) % step == 0:
        for s in (0, 1):
            print('r%3d %s' % (rnd, 'us ' if s == 0 else 'opp'), ' '.join('%d:%s L%d' % (i, '%d,%d' % b[0], len(b)) for i, b in sorted(bodies.items()) if side(i) == s))
        print('     pearls %d: %s' % (len(pearls), sorted(pearls)[:60]))


print('W H', W, H, 'start', {i: (teams[i], list(b)) for i, b in bodies.items()})
for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        if rnd >= 0:
            dump()
        rnd = p.i32(0)
    elif k == 1:
        actor = p.i32(0)
    elif k == 3:
        c = replay.point(p.pointer(0))
        if p.u32(0):
            pearls.add(c)
        else:
            pearls.discard(c)
            eats[side(actor)].append((rnd, actor, c))
    elif k == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        b = bodies[i]
        if b[0] != hd:
            if abs(b[0][0] - hd[0]) + abs(b[0][1] - hd[1]) > 1:
                jumps[side(i)].append((rnd, i, b[0], hd))
            b.appendleft(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif k == 10:
        parent, child = p.i32(0), p.i32(4)
        for z, i in enumerate((parent, child)):
            bodies[i] = deque(replay.point(c) for c in p.pointer(z))
            teams[i] = p.u16(8)
        if rnd <= r1:
            print('  split r%d side %d parent %d -> %s / child %d %s' % (rnd, side(parent), parent, list(bodies[parent]), child, list(bodies[child])))
    elif k == 11:
        i = p.i32(0)
        if rnd <= r1:
            print('  death r%d side %d dragon %d L%d head %s reason %d actor %s' % (rnd, side(i), i, len(bodies[i]), bodies[i][0], p.u16(4), actor))
        bodies.pop(i)
for s in (0, 1):
    print('jumps', 'us ' if s == 0 else 'opp', [j for j in jumps[s] if j[0] <= r1][:40])
    print('eats ', 'us ' if s == 0 else 'opp', [e for e in eats[s] if e[0] <= r1][:40])
