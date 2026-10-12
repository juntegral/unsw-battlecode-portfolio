# Own count for F7 (analyst, run 20261007-0208): are pearls reachable in raw rounds 0-50, and how far by path?
# Path = steps through edges that are not kelp (kind 1); portal edges (kind 2) lead to the partner edge; dragons ignored.
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from statistics import median
from pathlib import Path

D = Path('data/analysis/ladder')
rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
LAYOUTS = ('Tower Defense #1', 'Queen Of Spades #1', 'Trophy #1', 'Trauma #1')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def study(battle, game, upto=50):
    folder = Path('data/online/ladder') / str(battle)
    j = json.loads((folder / ('game-%d.json' % game)).read_text())
    root = replay.load(folder / ('M%d.replay' % game)).root()
    text = root.text(0)
    W, H = map(int, text.splitlines()[0].split()[1:3])
    bodies = {}
    teams = {}
    raw = []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    nxt = {}
    for y in range(H):
        for x in range(W):
            out = []
            for d in range(4):
                e = edge_id(W, H, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    continue
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e]
                    if len(partner) != 1:
                        continue
                    row, px = divmod(partner[0], W + 1)
                    out.append(((px - (d == 3)) % W, (row // 2 - (d == 0)) % H))
                else:
                    out.append(((x + STEP[d][0]) % W, (y + STEP[d][1]) % H))
            nxt[(x, y)] = out
    ours = 'A' if j['teamAId'] == 1119 else 'B'

    def side(i):
        return 'us' if teams[i] == ours else 'them'

    def bfs(starts):
        dist = dict((s, 0) for s in starts)
        todo = deque(starts)
        while todo:
            c = todo.popleft()
            for n in nxt[c]:
                if n not in dist:
                    dist[n] = dist[c] + 1
                    todo.append(n)
        return dist

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    region = dict((s, bfs([bodies[queens[s]][0]])) for s in ('us', 'them'))
    same_region = bodies[queens['them']][0] in region['us']
    S = dict((s, dict(pd=[], reach=[], unreachable=0, rounds=0)) for s in ('us', 'them'))
    present = set()
    rnd = 0
    started = False
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            if started:
                for s in ('us', 'them'):
                    heads = [b[0] for i, b in bodies.items() if side(i) == s]
                    if not heads:
                        continue
                    dist = bfs(heads)
                    ds = [dist[c] for c in present if c in dist]
                    S[s]['rounds'] += 1
                    S[s]['reach'].append(len(ds))
                    if ds:
                        S[s]['pd'].append(min(ds))
                    else:
                        S[s]['unreachable'] += 1
            started = True
            rnd = p.i32(0)
            if rnd > upto:
                break
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
                present.discard(c)
        elif k == 'dragonUpdate':
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                b.appendleft(h)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif k == 'dragonSplit':
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 'dragonDeath':
            bodies.pop(p.i32(0))
    out = dict(same_region=same_region)
    for s in ('us', 'them'):
        x = S[s]
        out[s] = dict(region=len(region[s]), path_median=median(x['pd']) if x['pd'] else None, unreachable_rounds=x['unreachable'], rounds=x['rounds'],
                      reachable_pearls_median=median(x['reach']) if x['reach'] else None,
                      within3=sum(d <= 3 for d in x['pd']), within8=sum(d <= 8 for d in x['pd']))
    return out


def med(xs):
    xs = [x for x in xs if x is not None]
    return median(xs) if xs else None


sel = [r for r in rows if r['our_code'] == 'main' and r['map_key'] in LAYOUTS and r['curves']['100']]
res = []
for r in sel:
    c = r['curves']['100']
    res.append((r, c['us']['alive'] <= 6 and c['them']['alive'] >= 15, study(r['battle'], r['game'])))
print('STALL GAMES')
bad = 0
for r, stall, o in res:
    if not stall:
        continue
    u = o['us']
    t = o['them']
    fail = u['path_median'] is None or u['path_median'] > 10 or u['unreachable_rounds'] > u['rounds'] / 2
    bad += fail
    print(r['game'], r['map_key'], 'queens in one region:', o['same_region'], '| us region', u['region'], 'path median', u['path_median'], 'rounds with pearl within 3 steps', u['within3'], 'within 8', u['within8'], 'of', u['rounds'],
          'reachable pearls median', u['reachable_pearls_median'], '| them region', t['region'], 'path median', t['path_median'], 'within 3', t['within3'], 'within 8', t['within8'], 'reachable', t['reachable_pearls_median'])
print('stall games failing the bar (median path > 10 or mostly unreachable):', bad, 'of', sum(s for _, s, _ in res))
print()
for lay in LAYOUTS:
    for label, flag in (('stall', True), ('non-stall', False)):
        g = [o for r, s, o in res if s == flag and r['map_key'] == lay]
        if not g:
            continue
        print(lay, label, 'games', len(g), '| us: region', med([o['us']['region'] for o in g]), 'path median', med([o['us']['path_median'] for o in g]), 'rounds within 3', med([o['us']['within3'] for o in g]), 'within 8', med([o['us']['within8'] for o in g]),
              'reachable pearls', med([o['us']['reachable_pearls_median'] for o in g]),
              '| them: path median', med([o['them']['path_median'] for o in g]), 'rounds within 3', med([o['them']['within3'] for o in g]), 'within 8', med([o['them']['within8'] for o in g]), 'reachable pearls', med([o['them']['reachable_pearls_median'] for o in g]))
