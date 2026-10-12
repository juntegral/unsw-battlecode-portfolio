# Scratch (diag-islands): who holds the fast pearl tiles, round by round, in every main game on one layout.
# Reads per-game.jsonl, maps.json and replays. Writes work/isl_trace-<tag>.jsonl (one line per game).
# Usage: python3 data/analysis/ladder/dossier/work/isl_trace.py "<layout key>" <tag>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

WORK = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
INF = 9999
BIN = 25
CAUSE = ('wall', 'own', 'body', 'headon', 'noact')


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.moves = []
        for y in range(h):
            for x in range(w):
                row = []
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.append((kind, dest))
                self.moves.append(row)
        self.adj = [sorted({dest for kind, dest in row if kind != 1}) for row in self.moves]
        self.cache = {}

    def dist(self, src):
        d = self.cache.get(src)
        if d is None:
            d = [INF] * (self.w * self.h)
            d[src] = 0
            q = deque([src])
            while q:
                c = q.popleft()
                nd = d[c] + 1
                for t in self.adj[c]:
                    if d[t] == INF:
                        d[t] = nd
                        q.append(t)
            self.cache[src] = d
        return d


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


PH = ((0, 100, 'a'), (101, 150, 'b'), (151, 200, 'c'), (201, 300, 'd'), (301, 400, 'e'), (401, 500, 'f'))
STALE = 25
RADIUS = 9


def phase(r):
    for lo, hi, name in PH:
        if lo <= r <= hi:
            return name
    return 'f'


def scan(rec, fast_xy, geos, which):
    # Emulates main.cpp 1415-1422 (expire, self report), 1523 and 1782-1796 (sightings), 2339-2363 (zone), 3328 (is_leader).
    # Sonar reports (1798-1823) are not emulated: a dragon here knows only what it has seen itself, so "self" is an upper bound.
    root = replay.load(Path(rec['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    if 'g' not in geos:
        geos['g'] = Geo(w, h, raw)
    g = geos['g']
    fast = set(y * w + x for x, y in fast_xy)
    ours = rec['our_side']
    side = lambda i: 'u' if teams[i] == ours else 't'
    C = Counter()
    present = {}
    known = {}
    rnd, actor, cur = 0, None, None
    lines = []

    def inview(a, c):
        return torus(a % w, c % w, w) <= 3 and torus(a // w, c // w, h) <= 3

    def finish():
        nonlocal cur
        if cur is None:
            return
        c = cur
        cur = None
        if c.get('cat') is None:
            return
        key = '%s|%s|%s|e%d|L%d' % (c['s'], phase(c['r']), c['cat'], c['e'], c['big'])
        C[key + '|n'] += 1
        if not c['ate']:
            C[key + '|skip'] += 1
        if which and c['s'] == 'u' and c['r'] in which and c['r'] > 150:
            lines.append([c['r'], c['id'], c['L'], c['head'] % w, c['head'] // w, c['cat'], c['kid'], c['klen'], c['e'],
                          [[x % w, x // w] for x in c['adj']], c['ate'], c['to'] % w if c['to'] is not None else -1,
                          c['to'] // w if c['to'] is not None else -1])

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            finish()
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            s = side(actor)
            body = bodies[actor]
            head = body[0]
            L = len(body)
            kn = known.get(actor)
            if kn is not None and kn[0] != actor and rnd - kn[2] > STALE:
                kn = None
            if kn is None or kn[0] == actor or L > kn[1] or (L == kn[1] and rnd > kn[2]):
                kn = [actor, L, rnd, head]
            live = None
            for i, b in bodies.items():
                if i == actor or side(i) != s or not inview(head, b[0]):
                    continue
                vis = sum(1 for x in b if inview(head, x))
                if i == kn[0]:
                    kn[1] = max(kn[1], vis)
                    kn[3] = b[0]
                elif vis > kn[1]:
                    kn = [i, vis, rnd, b[0]]
            known[actor] = kn
            if kn[0] != actor and kn[0] in bodies and inview(head, bodies[kn[0]][0]):
                live = bodies[kn[0]][0]
            zone_head = None if kn[0] == actor else (live if live is not None else kn[3])
            C['turns|%s|%s|%s' % (s, phase(rnd), 'self' if kn[0] == actor else 'follower')] += 1
            cur = dict(r=rnd, s=s, id=actor, L=L, head=head, ate=0, cat=None, to=None)
            if actor > 1:
                adj = [dest for kind, dest in g.moves[head] if kind != 1 and dest in present]
                if adj:
                    e = 0
                    for c in adj:
                        for i, b in bodies.items():
                            if side(i) != s and torus(c % w, b[0] % w, w) + torus(c // w, b[0] // w, h) <= 2:
                                e = 1
                    if zone_head is None:
                        cat = 'self'
                    else:
                        inz = [torus(c % w, zone_head % w, w) + torus(c // w, zone_head // w, h) <= RADIUS for c in adj]
                        cat = 'zone' if all(inz) else 'zmix' if any(inz) else 'zout'
                    if not e and any(side(i) != s and inview(head, b[0]) for i, b in bodies.items()):
                        e = 2
                    mates = sum(1 for i, b in bodies.items() if i != actor and side(i) == s and inview(head, b[0]))
                    C['mates|%s|%s|%d' % (s, phase(rnd), min(mates, 4))] += 1
                    cur.update(cat=cat, e=e, adj=adj, big=min(mates, 3), kid=kn[0], klen=kn[1])
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present[c] = rnd
            else:
                present.pop(c)
                if cur is not None:
                    cur['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if cur is not None and i == actor and cur['to'] is None:
                    cur['to'] = hd
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            C['split|%s|%s|%s' % (side(p.i32(0)), phase(rnd), 'self' if known.get(p.i32(0), [p.i32(0)])[0] == p.i32(0) else 'follower')] += 1
        elif k == 11:
            i = p.i32(0)
            bodies.pop(i)
            known.pop(i, None)
    finish()
    return dict(game=rec['game'], rating=rec['opponent_rating'], result=rec['our_result'], last_round=rec['last_round'],
                counts=dict(C), lines=lines)


def main():
    layout, tag = sys.argv[1], sys.argv[2]
    which = set(int(x) for x in sys.argv[3].split(',')) if len(sys.argv) > 3 else set()
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    oi = maps[layout].get('observed_intervals') or {}
    fast_xy = [tuple(int(z) for z in k.split(',')) for k, v in oi.items() if v.get('fast')]
    recs = []
    for line in Path('data/analysis/ladder/dossier/per-game.jsonl').open():
        r = json.loads(line)
        if r['layout_key'] == layout and r['relation'] == 'us':
            recs.append(r)
    recs.sort(key=lambda r: r['game'])
    geos = {}
    out = []
    for n, r in enumerate(recs):
        out.append(json.dumps(scan(r, fast_xy, geos, which), separators=(',', ':')))
        if n % 5 == 4:
            print(n + 1, len(recs), flush=True)
    body = '\n'.join(out) + '\n'
    if tag == 'islands':
        Path(WORK + 'isl_lead2-islands.jsonl').write_text(body)
    elif tag == 'australia':
        Path(WORK + 'isl_lead-australia.jsonl').write_text(body)
    elif tag == 'unsw':
        Path(WORK + 'isl_lead-unsw.jsonl').write_text(body)
    elif tag == 'slithery':
        Path(WORK + 'isl_lead-slithery.jsonl').write_text(body)
    else:
        Path(WORK + 'isl_lead-other.jsonl').write_text(body)
    print('done', layout, len(out))


main()
