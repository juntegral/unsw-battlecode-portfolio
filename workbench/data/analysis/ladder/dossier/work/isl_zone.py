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


def phase(r):
    for lo, hi, name in PH:
        if lo <= r <= hi:
            return name
    return 'f'


def scan(rec, fast_xy, geos):
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
    rnd, actor, cur = 0, None, None
    examples = []

    def finish():
        nonlocal cur
        if cur is None:
            return
        c = cur
        cur = None
        if c['adj'] is None:
            return
        key = '%s|%s|z%d|e%d|f%d|L%d' % (c['s'], phase(c['r']), c['z'], c['e'], c['f'], c['big'])
        C[key + '|n'] += 1
        if not c['ate']:
            C[key + '|skip'] += 1
            if c['s'] == 'u' and c['z'] and not c['e'] and 151 <= c['r'] <= 300 and len(examples) < 12 and c['died'] is None:
                examples.append([c['r'], c['id'], c['L'], c['head'] % w, c['head'] // w, c['pearl'] % w, c['pearl'] // w, c['zid'], c['zl'], c['zd']])

    def idle_mark():
        # a pearl lying on a fast tile at round start: who stands within 2 path steps
        hu = [b[0] for i, b in bodies.items() if side(i) == 'u']
        ht = [b[0] for i, b in bodies.items() if side(i) == 't']
        ph = phase(rnd)
        for c in fast:
            if c in present:
                d = g.dist(c)
                nu = any(d[x] <= 2 for x in hu)
                nt = any(d[x] <= 3 for x in ht)
                C['idle|%s|%s' % (ph, 'both' if nu and nt else 'u' if nu else 't' if nt else 'none')] += 1
        C['rounds|' + ph] += 1
        C['alive_u|' + ph] += len(hu)
        C['alive_t|' + ph] += len(ht)
        C['long_u|' + ph] += sum(1 for i, b in bodies.items() if side(i) == 'u' and len(b) > 4)
        C['long_t|' + ph] += sum(1 for i, b in bodies.items() if side(i) == 't' and len(b) > 4)

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
            if actor is None:
                idle_mark()
            actor = p.i32(0)
            s = side(actor)
            body = bodies[actor]
            head = body[0]
            L = len(body)
            cur = dict(r=rnd, s=s, id=actor, L=L, head=head, adj=None, ate=0, died=None)
            if actor > 1:
                adj = [dest for kind, dest in g.moves[head] if kind != 1 and dest in present]
                if adj:
                    z, zid, zl, zd, e, pick = 0, -1, 0, 99, 0, adj[0]
                    for c in adj:
                        cx, cy = c % w, c // w
                        for i, b in bodies.items():
                            hx, hy = b[0] % w, b[0] // w
                            dd = torus(cx, hx, w) + torus(cy, hy, h)
                            if side(i) == s:
                                if i != actor and len(b) > L and dd <= 9:
                                    if not z or dd < zd:
                                        z, zid, zl, zd, pick = 1, i, len(b), dd, c
                            elif dd <= 2:
                                e = 1
                    cur.update(adj=adj, z=z, zid=zid, zl=zl, zd=zd, e=e, pearl=pick,
                               f=int(any(c in fast for c in adj)), big=int(L > 4))
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present[c] = rnd
            else:
                present.pop(c)
                C['eat_%s|%s|%s' % ('fast' if c in fast else 'other', side(actor), phase(rnd))] += 1
                if cur is not None:
                    cur['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            C['split|%s|%s' % (side(p.i32(0)), phase(rnd))] += 1
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 11:
            i = p.i32(0)
            C['death|%s|%s' % (side(i), phase(rnd))] += 1
            if cur is not None and i == actor:
                cur['died'] = 1
            bodies.pop(i)
    finish()
    return dict(game=rec['game'], rating=rec['opponent_rating'], result=rec['our_result'], last_round=rec['last_round'],
                counts=dict(C), examples=examples)


def main():
    layout, tag = sys.argv[1], sys.argv[2]
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
        out.append(json.dumps(scan(r, fast_xy, geos), separators=(',', ':')))
        if n % 5 == 4:
            print(n + 1, len(recs), flush=True)
    body = '\n'.join(out) + '\n'
    if tag == 'islands':
        Path(WORK + 'isl_zone-islands.jsonl').write_text(body)
    elif tag == 'australia':
        Path(WORK + 'isl_zone-australia.jsonl').write_text(body)
    elif tag == 'unsw':
        Path(WORK + 'isl_zone-unsw.jsonl').write_text(body)
    elif tag == 'slithery':
        Path(WORK + 'isl_zone-slithery.jsonl').write_text(body)
    elif tag == 'school1':
        Path(WORK + 'isl_zone-school1.jsonl').write_text(body)
    elif tag == 'school2':
        Path(WORK + 'isl_zone-school2.jsonl').write_text(body)
    elif tag == 'maze':
        Path(WORK + 'isl_zone-maze.jsonl').write_text(body)
    elif tag == 'default':
        Path(WORK + 'isl_zone-default.jsonl').write_text(body)
    elif tag == 'autarky':
        Path(WORK + 'isl_zone-autarky.jsonl').write_text(body)
    else:
        Path(WORK + 'isl_zone-other.jsonl').write_text(body)
    print('done', layout, len(out), 'fast tiles', len(fast_xy))


main()
