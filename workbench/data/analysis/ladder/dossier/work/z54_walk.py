"""Scratch (z54): one dragon's turns in a round window, with the neighbourhood drawn at the start of each turn.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/z54_walk.py <replay> <id> <from> <to> [radius]
Grid: O/o this dragon's head/body (digits on o = body index mod 10 off), M/m mate head/body, E/e enemy head/body, * pearl, # kelp edge."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque

path, who, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
R = int(sys.argv[5]) if len(sys.argv) > 5 else 5
root = replay.load(path).root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
bodies, teams, raw = {}, {}, []
for line in lines:
    q = line.split()
    if not q:
        continue
    if q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
        teams[i] = int(q[1])
    elif q[0] == 'EDGE':
        raw.append((int(q[1]), int(q[2]), int(q[3])))
edges = canonical_edges(W, H, raw)
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
DN = 'NESW'
pearls = set()


def kelp(x, y, d):
    return edges.get(edge_id(W, H, x % W, y % H, d), (0, -1))[0] == 1


def owner(c):
    for i, b in bodies.items():
        if c in b:
            return i
    return None


def draw(me):
    hx, hy = bodies[me][0]
    cell = {}
    for i, b in bodies.items():
        for n, c in enumerate(b):
            if i == me:
                ch = 'O' if n == 0 else ('T' if n == len(b) - 1 else 'o')
            elif teams[i] == teams[me]:
                ch = 'M' if n == 0 else 'm'
            else:
                ch = 'E' if n == 0 else 'e'
            cell[c] = ch
    print('     ' + ''.join('%-2d' % ((hx + dx) % W % 100) for dx in range(-R, R + 1)))
    for dy in range(-R, R + 1):
        y = (hy + dy) % H
        top, mid = '     ', '%3d  ' % y
        for dx in range(-R, R + 1):
            x = (hx + dx) % W
            top += ('#' if kelp(x, y, 0) else ' ') + ' '
            c = cell.get((x, y), '*' if (x, y) in pearls else '.')
            mid += c + ('#' if kelp(x, y, 1) else ' ')
        if '#' in top:
            print(top)
        print(mid)
    near = []
    for i, b in bodies.items():
        if i == me:
            continue
        dx = abs(b[0][0] - hx); dy = abs(b[0][1] - hy)
        g = min(dx, W - dx) + min(dy, H - dy)
        if g <= 2 * R:
            near.append((g, 'mate' if teams[i] == teams[me] else 'ENEMY', i, len(b), b[0]))
    for n in sorted(near):
        print('   head gap %d %s id %d len %d at %s' % n)
    for d in range(4):
        x, y = (hx + STEP[d][0]) % W, (hy + STEP[d][1]) % H
        o = owner((x, y))
        what = 'KELP' if kelp(hx, hy, d) else ('free' if o is None else ('own body idx %d of %d' % (list(bodies[o]).index((x, y)), len(bodies[o])) if o == me else '%s body id %d len %d idx %d' % ('mate' if teams[o] == teams[me] else 'enemy', o, len(bodies[o]), list(bodies[o]).index((x, y)))))
        print('   step %s -> (%d, %d): %s%s' % (DN[d], x, y, what, ' pearl' if (x, y) in pearls else ''))


rnd, actor = -1, None
first = None
for ev in root.pointer(3):
    k = ev.u16(0)
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
        if first is None:
            first = rnd
            print('first roundStart value', first)
    elif k == 1:
        actor = p.i32(0)
        if actor == who and lo <= rnd <= hi:
            t = teams[who]
            print('\n=== round %d, dragon %d (team %d) turn starts: len %d head %s tail %s; team units %d (enemy %d)' % (
                rnd, who, t, len(bodies[who]), bodies[who][0], bodies[who][-1], sum(1 for i in bodies if teams[i] == t), sum(1 for i in bodies if teams[i] != t)))
            draw(who)
    elif k == 3:
        c = replay.point(p.pointer(0))
        if p.u32(0):
            pearls.add(c)
        else:
            pearls.discard(c)
            if actor == who and lo <= rnd <= hi:
                print('   ate pearl at', c)
    elif k == 4:
        if p.i32(0) == who and lo <= rnd <= hi:
            a = p.pointer(0)
            u = p.pointer(1)
            w = a.u16(0) if a else -1
            dirs = list(a.pointer(0)) if a and w == 0 and a.pointer(0) is not None else []
            print('   ACTION kind %s dirs %s childSize %s tle %s points %s' % (('move', 'split', 'suicide')[w] if 0 <= w < 3 else w, [DN[d] for d in dirs], a.i32(4) if w == 1 else '-', p.bit(32), u.u64(0) if u else None))
    elif k in (5, 6):
        if lo <= rnd <= hi and (k == 5 or p.i32(0) == who):
            try:
                print('   LOG', k, p.text(0)[:300])
            except Exception as e:
                print('   LOG?', k, e)
    elif k == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        b = bodies[i]
        if b[0] != hd:
            b.appendleft(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
        if i == who and lo <= rnd <= hi:
            print('   update: head %s tail %s len %d (actor %s)' % (hd, tl, len(b), actor))
    elif k == 10:
        parent, child = p.i32(0), p.i32(4)
        for z, i in enumerate((parent, child)):
            bodies[i] = deque(replay.point(c) for c in p.pointer(z))
            teams[i] = p.u16(8)
        if who in (parent, child) and lo - 30 <= rnd <= hi:
            print('   SPLIT round %d parent %d (len %d head %s) child %d (len %d head %s)' % (rnd, parent, len(bodies[parent]), bodies[parent][0], child, len(bodies[child]), bodies[child][0]))
    elif k == 11:
        i, reason = p.i32(0), p.u16(4)
        if lo <= rnd <= hi:
            b = bodies[i]
            hx, hy = bodies[who][0] if who in bodies else (-99, -99)
            if i == who:
                print('   DEATH round %d id %d len %d reason %d (%s) head %s, during turn of %s' % (rnd, i, len(b), reason, ('wall/kelp', 'own body', 'other body', 'head-on', 'no valid action')[reason] if reason < 5 else '?', b[0], actor))
            elif who in bodies and min(abs(b[0][0] - hx), W - abs(b[0][0] - hx)) + min(abs(b[0][1] - hy), H - abs(b[0][1] - hy)) <= 2 * R:
                print('   (nearby death round %d id %d team %d len %d reason %d head %s, during turn of %s)' % (rnd, i, teams[i], len(b), reason, b[0], actor))
        bodies.pop(i)
