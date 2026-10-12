# Scratch (early-growth brief): finer checks. (1) the round-60 step on Tower Defense, (2) Stripes pearl rooms behind portals,
# (3) which ladder layouts fall under the bot's centre rule. Prints only.
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import Counter, defaultdict, deque
from statistics import median, mean
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
INF = 9999
games = []
for n in range(4):
    for line in Path('data/analysis/ladder/losses/work/eg_rows-%d.jsonl' % n).read_text().splitlines():
        games.append(json.loads(line))
per = {r['game']: r for r in json.loads(Path('data/analysis/ladder/losses/split/per-game.json').read_text())}


def graphs(g):
    root = replay.load(Path(per[g['game']]['replay'])).root()
    w, h = g['w'], g['h']
    raw = []
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    edges = canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    adj, plain = [], []
    for y in range(h):
        for x in range(w):
            out, flat = set(), set()
            for d in range(4):
                e = edge_id(w, h, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    continue
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    ry, px = divmod(partner, w + 1)
                    out.add(((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w)
                else:
                    t = ((y + STEP[d][1]) % h) * w + (x + STEP[d][0]) % w
                    out.add(t)
                    flat.add(t)
            adj.append(sorted(out))
            plain.append(sorted(flat))
    return adj, plain


def bfs(adj, sources):
    d = [INF] * len(adj)
    q = deque(sources)
    for s in sources:
        d[s] = 0
    while q:
        c = q.popleft()
        for t in adj[c]:
            if d[t] == INF:
                d[t] = d[c] + 1
                q.append(t)
    return d


def pct(a, b):
    return '%5.1f%% (%d/%d)' % (100.0 * a / b, a, b) if b else '  n/a'


G = {}
for g in games:
    if g['map_key'] not in G:
        G[g['map_key']] = graphs(g)

print('== (1) Tower Defense, our side, 27 games: 5-round bins round the end of the centre rule (main.cpp:475, 5061: round < 60)')
td = [g for g in games if g['map_key'].startswith('Tower')]
adj = G[td[0]['map_key']][0]
for g in td:
    for s in 'ut':
        heads = [t[6] for t in g['turns'] if t[1] == s and t[0] == 0 and t[4] == 1]
        ds = bfs(adj, heads)
        room = [c for c in range(len(adj)) if ds[c] <= 5]
        cx, cy = g['w'] // 2, g['h'] // 2

        def cd(c):
            y, x = divmod(c, g['w'])
            ax, ay = abs(x - cx), abs(y - cy)
            return min(ax, g['w'] - ax) + min(ay, g['h'] - ay)
        gate = [c for c in room if any(ds[t] > 5 for t in adj[c])]
        dgate = bfs(adj, gate)
        g[s] = dict(ds=ds, near=set(sorted(room, key=cd)[:9]), gate=gate, dgate=dgate, mincd=min(cd(c) for c in room))
print('   exit tiles of the room per game side (count of tiles with a neighbour outside):', dict(Counter(len(g['u']['gate']) for g in td)),
      '| room minimum centre distance', dict(Counter(g['u']['mincd'] for g in td)))
for s, name in (('u', 'OURS  '), ('t', 'THEIRS')):
    for lo in range(40, 80, 5):
        T = [(g, t) for g in td for t in g['turns'] if t[1] == s and lo <= t[0] <= lo + 4 and g[s]['ds'][t[6]] <= 5]
        A = [(g, t) for g in td for t in g['turns'] if t[1] == s and lo <= t[0] <= lo + 4]
        print('   %s r%2d-%2d in-room turns %4d of %4d | on the 9 tiles nearest the centre %s | within 2 steps of the exit tile %s | mean centre dist %.2f' % (
            name, lo, lo + 4, len(T), len(A), pct(sum(t[6] in g[s]['near'] for g, t in T), len(T)), pct(sum(g[s]['dgate'][t[6]] <= 2 for g, t in T), len(T)),
            mean(t[7] for g, t in T) if T else 0))
for s, name in (('u', 'OURS'), ('t', 'THEIRS')):
    dead = [(t[0], t[27], t[5]) for g in td for t in g['turns'] if t[1] == s and t[4] == 1 and t[27] and t[0] <= 60]
    print('  ', name, 'starting dragons dead by r60:', len(dead), 'of', 2 * len(td), dict(Counter(d[1] for d in dead)), 'rounds', sorted(d[0] for d in dead))

print()
print('== (2) Stripes, never-grew games: pearl rooms (tiles whose walk-only component, portals closed, has 6 tiles or fewer)')
st = [g for g in games if g['map_key'].startswith('Stripes') and g['group'] == 'never_grew']
adj, plain = G[st[0]['map_key']]
comp = {}
for c in range(len(plain)):
    if c in comp:
        continue
    seen = [c]
    comp[c] = c
    q = deque([c])
    while q:
        x = q.popleft()
        for t in plain[x]:
            if t not in comp:
                comp[t] = c
                seen.append(t)
                q.append(t)
sizes = Counter(comp.values())
room = {c for c in comp if sizes[comp[c]] <= 6}
print('   rooms:', sorted(Counter(sizes[v] for v in set(comp.values())).items()), '| tiles in rooms', len(room), 'of', len(plain))
P = [p for g in st for p in g['pearls'] if p[2] == 'n' and p[1] <= 60]
inr = [p for p in P if p[0] in room]
print('   natural births r0-60:', len(P), '| in rooms', pct(len(inr), len(P)))
for nm, X in (('in a room', inr), ('outside rooms', [p for p in P if p[0] not in room])):
    print('   born %s: %d | eaten by us by r60 %s | by them %s' % (nm, len(X), pct(sum(p[7] == 'u' and p[8] <= 60 for p in X), len(X)), pct(sum(p[7] == 't' and p[8] <= 60 for p in X), len(X))))
for s, name in (('u', 'OURS  '), ('t', 'THEIRS')):
    T = [t for g in st for t in g['turns'] if t[1] == s and t[0] <= 60]
    inside = [t for t in T if t[6] in room]
    mv = [t for t in T if t[18] >= 1]
    enter = [t for t in mv if t[6] not in room and t[32] in room]
    print('   %s turns %d | turns that start inside a room %s | steps into a room %d (%.2f per game) | eaten in rooms %d, outside %d | deaths inside rooms %s' % (
        name, len(T), pct(len(inside), len(T)), len(enter), len(enter) / len(st),
        sum(1 for g in st for p in g['pearls'] if p[7] == s and p[8] <= 60 and p[0] in room),
        sum(1 for g in st for p in g['pearls'] if p[7] == s and p[8] <= 60 and p[0] not in room),
        dict(Counter(t[27] for t in inside if t[27]))))
    for role, rn in ((1, 'queen'), (0, 'other starter')):
        X = [t for t in mv if t[4] == 1 and t[5] == role]
        print('        %s: steps into a room %d, turns with a pearl one portal step away %d, not taken %s' % (
            rn, sum(1 for t in X if t[6] not in room and t[32] in room), sum(1 for t in X if t[25] == 2), pct(sum(1 for t in X if t[25] == 2 and t[19] == 0), sum(1 for t in X if t[25] == 2))))
    X = [t for t in mv if t[4] == 0]
    print('        children: steps into a room %d, turns with a pearl one portal step away %d, not taken %s' % (
        sum(1 for t in X if t[6] not in room and t[32] in room), sum(1 for t in X if t[25] == 2), pct(sum(1 for t in X if t[25] == 2 and t[19] == 0), sum(1 for t in X if t[25] == 2))))
    # how long a dragon stays within 2 path steps of a pearl it does not eat
    wait = [t for t in T if t[10] is not None and t[10] <= 2 and t[19] == 0]
    print('        turns that start within 2 path steps of a known pearl and eat nothing: %s' % pct(len(wait), len(T)))

print()
print('== (3) ladder layouts under the centre rule (cells <= 1000 and (width >= 2*height or cells <= 700); main.cpp:473-476)')
maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
for key, m in sorted(maps.items()):
    w, h = m['width'], m['height']
    cells = w * h
    long_map = w >= 2 * h
    on = cells <= 1000 and (long_map or cells <= 700)
    print('   %-24s %2dx%2d cells %4d dragons at spawn %s length %s -> %s' % (key, w, h, cells, m.get('dragons_at_spawn'), m.get('queen_spawn_length'),
          ('centre pull for %d rounds' % (60 if long_map else 30)) if on else 'no centre pull'))
