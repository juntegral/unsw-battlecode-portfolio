# Scratch (diag-stripes): where the dragons spend their turns in the opening: inside a room, or in the open area
# within 2 open steps of a door (a tile with a portal step into a room under 48 tiles), by the kind of room.
# Usage: python3 data/analysis/ladder/dossier/work/st_where.py <rows file> <one replay of the layout> [last round, default 100]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import Counter, defaultdict, deque
from pathlib import Path

LAST = int(sys.argv[3]) if len(sys.argv) > 3 else 100
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
games = [json.loads(line) for line in open(sys.argv[1])]
g0 = games[0]
w, h, comp, size, loop = g0['w'], g0['h'], g0['comp'], g0['size'], g0['loop']
text = replay.load(Path(sys.argv[2])).root().text(0)
raw = []
for line in text.splitlines():
    q = line.split()
    if q and q[0] == 'EDGE':
        raw.append(tuple(map(int, q[1:4])))
edges = canonical_edges(w, h, raw)
portals = defaultdict(list)
for e, kp in edges.items():
    if kp[0] == 2:
        portals[kp[1]].append(e)
moves = []
for y in range(h):
    for x in range(w):
        row = []
        for d in range(4):
            e = edge_id(w, h, x, y, d)
            kind, pid = edges.get(e, (0, -1))
            if kind == 2:
                partner = [z for z in portals[pid] if z != e][0]
                ry, px = divmod(partner, w + 1)
                dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
            else:
                dest = ((y + STEP[d][1]) % h) * w + (x + STEP[d][0]) % w
            row.append((kind, dest))
        moves.append(row)
births = Counter()
for g in games:
    for c, b, o, by, er, eid, eL, eq in g['pearls']:
        if o == 'n':
            births[comp[c]] += 1
doors = defaultdict(list)
for c in range(w * h):
    if size[comp[c]] < 48:
        continue
    for kind, dest in moves[c]:
        if kind == 2 and size[comp[dest]] < 48:
            cp = comp[dest]
            k = ('loop room with pearls' if births[cp] else 'loop room, no pearls') if loop[cp] else 'dead-end room'
            doors[k].append(c)
near = {}
for k, src in doors.items():
    dist = {c: 0 for c in src}
    q = deque(src)
    while q:
        c = q.popleft()
        if dist[c] == 2:
            continue
        for kind, dest in moves[c]:
            if kind == 0 and dest not in dist:
                dist[dest] = dist[c] + 1
                q.append(dest)
    near[k] = set(dist)
    print(k, 'door tiles', sorted((c % w, c // w) for c in src), 'tiles within 2 open steps', len(dist))
ORDER = ('loop room with pearls', 'dead-end room', 'loop room, no pearls')
tot = Counter()
for g in games:
    for t in g['turns']:
        if t['r'] > LAST:
            break
        who = ['all']
        if t['st']:
            who.append('queen' if t['q'] else 'other starter')
        if t['hs'] < 48:
            z = 'inside a room'
        else:
            z = 'elsewhere in the open area'
            for k in ORDER:
                if t['head'] in near[k]:
                    z = 'within 2 steps of a door: ' + k
                    break
        for x in who:
            tot[t['s'], x, z, 'turns'] += 1
            tot[t['s'], x, z, 'ate'] += t['ate']
            tot[t['s'], x, 'turns'] += 1
print('rounds 0-%d, %d games: share of dragon turns by where the head is at the start of the turn (pearls eaten in those turns)' % (LAST, len(games)))
for x in ('queen', 'other starter', 'all'):
    print(x)
    for z in ['inside a room'] + ['within 2 steps of a door: ' + k for k in ORDER] + ['elsewhere in the open area']:
        u, t = tot['u', x, z, 'turns'], tot['t', x, z, 'turns']
        print('  %-50s ours %5d %.3f (ate %4d)   theirs %5d %.3f (ate %4d)' % (
            z, u, u / max(1, tot['u', x, 'turns']), tot['u', x, z, 'ate'], t, t / max(1, tot['t', x, 'turns']), tot['t', x, z, 'ate']))
