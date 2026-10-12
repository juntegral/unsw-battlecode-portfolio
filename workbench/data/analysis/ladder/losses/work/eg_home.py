# Scratch (early-growth brief): leaving the spawn area, pinning toward the centre, and how often a dragon goes without growing.
# Reads eg_rows-*.jsonl and one replay per layout (for the walls). Prints only.
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


def adjacency(g):
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
    adj = []
    for y in range(h):
        for x in range(w):
            out = set()
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
                    out.add(((y + STEP[d][1]) % h) * w + (x + STEP[d][0]) % w)
            adj.append(sorted(out))
    return adj


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


ADJ = {}
BUCKETS = ((0, 9), (10, 19), (20, 29), (30, 59), (60, 89), (90, 120))
for g in games:
    if g['map_key'] not in ADJ:
        ADJ[g['map_key']] = adjacency(g)
    adj = ADJ[g['map_key']]
    g['ds'] = {}
    for s in 'ut':
        heads = [t[6] for t in g['turns'] if t[1] == s and t[0] == 0 and t[4] == 1]
        g['ds'][s] = bfs(adj, heads)
    cells = g['w'] * g['h']
    long_map = g['w'] >= 2 * g['h']
    g['centre_rounds'] = (60 if long_map else 30) if (cells <= 1000 and (long_map or cells <= 700)) else 0

print('layout: bot centre rule rounds (read from main.cpp:473-476):', sorted({(g['map_key'], g['centre_rounds']) for g in games}))


def leave(gs, s, k):
    out = []
    for g in gs:
        rs = [t[0] for t in g['turns'] if t[1] == s and g['ds'][s][t[6]] >= k]
        out.append(min(rs) if rs else None)
    return out


def block(gs, label):
    print()
    print('=====', label, len(gs), 'games', dict(Counter(g['result'] for g in gs)))
    if not gs:
        return
    for s, name in (('u', 'OURS  '), ('t', 'THEIRS')):
        lv = leave(gs, s, 8)
        got = sorted(x for x in lv if x is not None)
        print(' ', name, 'first round a head is 8+ path steps from its start: median', median(got) if got else None,
              '| not by r30:', sum(1 for x in lv if x is None or x > 30), '| not by r60:', sum(1 for x in lv if x is None or x > 60),
              '| not by r120:', sum(1 for x in lv if x is None), 'of', len(gs))
        for lo, hi in BUCKETS:
            T = [(g, t) for g in gs for t in g['turns'] if t[1] == s and lo <= t[0] <= hi]
            if not T:
                continue
            mv = [t for g, t in T if t[18] >= 1]
            print('    r%3d-%3d turns %6d | 8+ steps from start %s | mean steps from start %5.2f | re-treads own last 12 tiles %s | centre dist %5.2f | ate/turn %.3f' % (
                lo, hi, len(T), pct(sum(g['ds'][s][t[6]] >= 8 for g, t in T), len(T)), mean(min(g['ds'][s][t[6]], 99) for g, t in T),
                pct(sum(t[24] == 1 for t in mv), len(mv)), mean(t[7] for g, t in T), sum(t[19] for g, t in T) / len(T)))


def hungry(gs, label):
    # rounds since this dragon last grew (starting dragons from r0, children from their first turn); ours, length<=4
    rows = []
    for g in gs:
        last = {}
        for t in g['turns']:
            if t[1] != 'u':
                continue
            if t[2] not in last:
                last[t[2]] = t[0]
            if t[3] <= 4 and t[0] <= 59:
                rows.append((g['game'], t[0], t[0] - last[t[2]], t))
            if t[19] > 0:
                last[t[2]] = t[0]
    n = len(rows)
    line = '  %-34s %3d games, our turns len<=4 r0-59: %6d' % (label, len(gs), n)
    for k in (8, 12, 16, 20, 30):
        line += ' | idle>=%d %s' % (k, pct(sum(r[2] >= k for r in rows), n))
    print(line)
    for k in (12, 16):
        ng = len({r[0] for r in rows if r[2] >= k})
        print('      games with any such turn (idle>=%d): %d of %d; ate/turn when idle>=%d: %.3f, when idle<%d: %.3f' % (
            k, ng, len(gs), k, sum(r[3][19] for r in rows if r[2] >= k) / max(1, sum(r[2] >= k for r in rows)),
            k, sum(r[3][19] for r in rows if r[2] < k) / max(1, sum(r[2] < k for r in rows))))


keys = sorted({g['map_key'] for g in games})
for key in keys:
    for grp in ('never_grew', 'grew', None):
        gs = [g for g in games if g['map_key'] == key and g['group'] == grp]
        if gs:
            block(gs, '%s / %s (start length %d)' % (key, grp, gs[0]['L0']))
print()
print('===== rounds without growing, our dragons (the idle test of a hunger switch)')
for key in keys:
    for grp in ('never_grew', 'grew', None):
        gs = [g for g in games if g['map_key'] == key and g['group'] == grp]
        if gs:
            hungry(gs, '%s / %s' % (key, grp))

# Tower Defense: the spawn room
print()
print('===== Tower Defense spawn room (tiles within 5 path steps of a start head)')
td = [g for g in games if g['map_key'].startswith('Tower')]
for s, name in (('u', 'OURS  '), ('t', 'THEIRS')):
    sizes = Counter(sum(1 for x in g['ds'][s] if x <= 5) for g in td)
    ex = []
    for g in td:
        rs = [t[0] for t in g['turns'] if t[1] == s and g['ds'][s][t[6]] > 5]
        ex.append(min(rs) if rs else None)
    got = sorted(x for x in ex if x is not None)
    print(' ', name, 'room sizes', dict(sizes), '| first round a head is outside: median', median(got) if got else None, 'min', got[0] if got else None,
          '| never by r30', sum(1 for x in ex if x is None or x > 30), '| never by r60', sum(1 for x in ex if x is None or x > 60), '| never by r120', sum(1 for x in ex if x is None), 'of', len(td))
    for lo, hi in BUCKETS:
        T = [(g, t) for g in td for t in g['turns'] if t[1] == s and lo <= t[0] <= hi]
        ins = [(g, t) for g, t in T if g['ds'][s][t[6]] <= 5]
        outs = [(g, t) for g, t in T if g['ds'][s][t[6]] > 5]
        near = 0
        for g, t in ins:
            room = sorted(g['w'] * g['h'] and c for c in range(g['w'] * g['h']) if g['ds'][s][c] <= 5)
            cx, cy = g['w'] // 2, g['h'] // 2

            def cd(c):
                y, x = divmod(c, g['w'])
                ax, ay = abs(x - cx), abs(y - cy)
                return min(ax, g['w'] - ax) + min(ay, g['h'] - ay)
            best = sorted(room, key=cd)[:9]
            near += int(t[6] in best)
        print('    r%3d-%3d turns %6d | inside the room %s | of those, on the 9 room tiles nearest the centre %s (9/49 = 18.4%% if even) | ate/turn inside %.3f outside %.3f' % (
            lo, hi, len(T), pct(len(ins), len(T)), pct(near, len(ins)),
            sum(t[19] for g, t in ins) / max(1, len(ins)), sum(t[19] for g, t in outs) / max(1, len(outs))))
print('  results of the 27 games by whether THEIR side left the room by r60:')
for g in td:
    pass
c = Counter()
for g in td:
    rs = [t[0] for t in g['turns'] if t[1] == 't' and g['ds']['t'][t[6]] > 5]
    c[('they left by r60' if rs and min(rs) <= 60 else 'they stayed', g['result'])] += 1
print('  ', dict(c))
