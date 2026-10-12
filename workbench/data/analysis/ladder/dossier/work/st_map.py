# Scratch (diag-stripes): draw a layout from a replay header (kelp, portals by id letter, starts), its portal-free
# components, and where natural pearls are born over the listed replays.
# Usage: python3 data/analysis/ladder/dossier/work/st_map.py <replay> [more replays for the birth heat map]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import Counter, defaultdict, deque
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
root = replay.load(Path(sys.argv[1])).root()
text = root.text(0)
w, h = map(int, text.splitlines()[0].split()[1:3])
raw, spawn, tiles = [], {}, {}
for line in text.splitlines():
    q = line.split()
    if q and q[0] == 'EDGE':
        raw.append(tuple(map(int, q[1:4])))
    elif q and q[0] == 'DRAGON':
        for k in range(int(q[2])):
            spawn[(int(q[3 + 2 * k]), int(q[4 + 2 * k]))] = ('AB'[int(q[1])] if k == 0 else 'ab'[int(q[1])])
edges = canonical_edges(w, h, raw)
portals = defaultdict(list)
for e, kp in edges.items():
    if kp[0] == 2:
        portals[kp[1]].append(e)
PORT = 'abcdefghijklmnopqrstuvwxyz'


def move(x, y, d):
    e = edge_id(w, h, x, y, d)
    kind, pid = edges.get(e, (0, -1))
    if kind == 2:
        partner = [z for z in portals[pid] if z != e][0]
        ry, px = divmod(partner, w + 1)
        return kind, ((px - (d == 3)) % w, (ry // 2 - (d == 0)) % h), pid
    return kind, ((x + STEP[d][0]) % w, (y + STEP[d][1]) % h), pid


comp = {}
sizes = []
for y in range(h):
    for x in range(w):
        if (x, y) in comp:
            continue
        n = len(sizes)
        comp[(x, y)] = n
        q = deque([(x, y)])
        k = 0
        while q:
            c = q.popleft()
            k += 1
            for d in range(4):
                kind, t, pid = move(c[0], c[1], d)
                if kind == 0 and t not in comp:
                    comp[t] = n
                    q.append(t)
        sizes.append(k)
print('size', w, h, 'portal pairs', len(portals), 'components without portals', sorted(sizes, reverse=True))


def draw(title, cell):
    print()
    print(title)
    print('   ' + ''.join(' %-1s' % (x % 10) for x in range(w)))
    for y in range(h):
        top, mid = '   ', '%2d ' % y
        for x in range(w):
            kn, pn = edges.get(edge_id(w, h, x, y, 0), (0, -1))
            kw, pw = edges.get(edge_id(w, h, x, y, 3), (0, -1))
            top += '+' + ('-' if kn == 1 else PORT[pn % 26] if kn == 2 else ' ')
            mid += ('|' if kw == 1 else PORT[pw % 26] if kw == 2 else ' ') + cell((x, y))
        print(top + '+')
        ke, pe = edges.get(edge_id(w, h, w - 1, y, 1), (0, -1))
        print(mid + ('|' if ke == 1 else PORT[pe % 26] if ke == 2 else ' '))


draw('starts (A/B head, a/b body); letters on edges are portal ids', lambda c: spawn.get(c, '.'))
draw('component size (9 = 9 or more)', lambda c: str(min(9, sizes[comp[c]])))
for pid, es in sorted(portals.items()):
    out = []
    for e in es:
        row, x = divmod(e, w + 1)
        if row % 2 == 0:
            a, b = (x, (row // 2 - 1) % h), (x, (row // 2) % h)
            o = 'horizontal'
        else:
            a, b = ((x - 1) % w, row // 2), (x % w, row // 2)
            o = 'vertical'
        out.append('%s between %s (room of %d) and %s (room of %d)' % (o, a, sizes[comp[a]], b, sizes[comp[b]]))
    print('portal', PORT[pid % 26], pid, '|', ' <-> '.join(out))
births = Counter()
games = 0
for path in sys.argv[1:]:
    r = replay.load(Path(path)).root()
    actor = None
    games += 1
    for ev in r.pointer(3):
        k = ev.u16(0)
        if k == 0:
            actor = None
        elif k == 1:
            actor = ev.pointer(0).i32(0)
        elif k == 3:
            p = ev.pointer(0)
            if p.u32(0) and actor is None:
                births[replay.point(p.pointer(0))] += 1
top = max(births.values(), default=1)
draw('natural pearl births over %d replays (1-9 scaled to the busiest tile; %d births)' % (games, sum(births.values())),
     lambda c: '.' if births.get(c, 0) == 0 else str(min(9, 1 + (8 * births[c]) // top)))
bysize = Counter()
for c, n in births.items():
    bysize[sizes[comp[c]]] += n
print('births by component size', sorted(bysize.items()))
print('tiles that ever spawned', len(births), 'by component size', sorted(Counter(sizes[comp[c]] for c in births).items()))
