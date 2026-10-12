"""Scratch (job C): local picture round a dragon. Usage: o1_look.py <set> <gid> <dragon id> <r0> <r1>
Prints per round at the dragon's turn start: head, body, pearls within the 7x7 (with free-path steps), spawn timers unknown;
a 7x7 map: # kelp edge marks omitted, o pearl, H head, b own body, m mate, E enemy head, e enemy body, . free."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from o1_scan import jobs, STEP
name, gid, did, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
if '/' in name:
    path = name
else:
    label, path, j = [t for t in jobs(name) if t[2]['id'] == gid][0]
root = replay.load(path).root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
bodies, teams, raw = {}, {}, []
for line in lines:
    q = line.split()
    if q and q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
        teams[i] = int(q[1])
    elif q and q[0] == 'EDGE':
        raw.append((int(q[1]), int(q[2]), int(q[3])))
edges = canonical_edges(W, H, raw)
portals = defaultdict(list)
for e, (k, p) in edges.items():
    if k == 2:
        portals[p].append(e)


def ek(c, d):
    return edges.get(edge_id(W, H, c[0], c[1], d), (0, -1))[0]


def dest(h, d):
    x, y = h
    e = edge_id(W, H, x, y, d)
    kind, pid = edges.get(e, (0, -1))
    if kind == 1:
        return None
    if kind == 2:
        partner = [z for z in portals[pid] if z != e][0]
        prow, px = divmod(partner, W + 1)
        py = prow // 2
        return ((px - (d == 3)) % W, (py - (d == 0)) % H)
    dx, dy = STEP[d]
    return ((x + dx) % W, (y + dy) % H)


def flood(h, R, occ):
    seen = {h: 0}
    qu = deque([h])
    while qu:
        c = qu.popleft()
        if seen[c] >= R:
            continue
        for d in range(4):
            n = dest(c, d)
            if n is None or n in seen or n in occ:
                continue
            seen[n] = seen[c] + 1
            qu.append(n)
    return seen


pearls = {}
rnd = -1
births = defaultdict(list)
for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
        if rnd > r1:
            break
    elif k == 1:
        a = p.i32(0)
        if a == did and r0 <= rnd <= r1:
            b = bodies[a]
            h = b[0]
            occ = set()
            for bb in bodies.values():
                occ.update(bb)
            fl = flood(h, 8, occ - {h})
            near = [(fl.get(c, 99), c, pearls[c]) for c in pearls if abs((c[0] - h[0] + W // 2) % W - W // 2) <= 3 and abs((c[1] - h[1] + H // 2) % H - H // 2) <= 3]
            print('r%d head %s body %s | pearls in view (steps, tile, born round): %s' % (rnd, h, list(b), sorted(near)))
            for dy in range(-3, 4):
                row = ''
                for dx in range(-3, 4):
                    c = ((h[0] + dx) % W, (h[1] + dy) % H)
                    ch = '.'
                    if c in pearls:
                        ch = 'o'
                    for z, bb in bodies.items():
                        if c in bb:
                            mine = teams[z] == teams[a]
                            ch = ('H' if z == a else 'M' if mine else 'E') if bb[0] == c else ('b' if z == a else 'm' if mine else 'e')
                    wall = ''.join('NESW'[d] if ek(c, d) == 1 else 'nesw'[d] if ek(c, d) == 2 else '' for d in range(4))
                    row += '%-6s' % (ch + wall)
                print('      ' + row)
    elif k == 3:
        c = replay.point(p.pointer(0))
        if p.u32(0):
            pearls[c] = rnd
        else:
            pearls.pop(c, None)
            if r0 - 3 <= rnd <= r1:
                print('   r%d dragon %d eats %s' % (rnd, a, c))
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
            teams[i] = p.u16(8)
    elif k == 11:
        bodies.pop(p.i32(0))
