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


def sites_of(g, fast):
    # group fast tiles that are within 3 path steps of each other
    left, sites = sorted(fast), []
    while left:
        grp, front = [left.pop(0)], None
        grew = True
        while grew:
            grew = False
            for c in list(left):
                if any(g.dist(c)[x] <= 3 for x in grp):
                    grp.append(c)
                    left.remove(c)
                    grew = True
        sites.append(sorted(grp))
    return sites


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
        fast = sorted(y * w + x for x, y in fast_xy)
        geos['fast'] = fast
        geos['sites'] = sites_of(geos['g'], fast)
        near = [INF] * (w * h)
        site_of = [-1] * (w * h)
        for n, grp in enumerate(geos['sites']):
            for c in grp:
                d = geos['g'].dist(c)
                for x in range(w * h):
                    if d[x] < near[x]:
                        near[x] = d[x]
                        site_of[x] = n
        geos['near'], geos['site_of'] = near, site_of
    g, fast, sites, near, site_of = geos['g'], set(geos['fast']), geos['sites'], geos['near'], geos['site_of']
    ours = rec['our_side']
    side = lambda i: 'u' if teams[i] == ours else 't'
    bins = defaultdict(lambda: Counter())
    site_bins = defaultdict(lambda: Counter())
    present = {}
    rnd, actor, started = 0, None, False
    headons = []
    snaps = {}
    lens_at = {}

    def roundmark(n):
        b = n // BIN
        cnt = {'u': 0, 't': 0}
        st2 = {'u': 0, 't': 0}
        first = {}
        for i, body in bodies.items():
            s = side(i)
            cnt[s] += 1
            d = near[body[0]]
            if d <= 2:
                st2[s] += 1
            if d <= 3:
                k = site_of[body[0]]
                first.setdefault(k, set()).add(s)
        bins[b]['rounds'] += 1
        for s in 'ut':
            bins[b]['alive_sum_' + s] += cnt[s]
            bins[b]['near2_sum_' + s] += st2[s]
        for k in range(len(sites)):
            who = first.get(k, set())
            key = 'both' if len(who) == 2 else 'none' if not who else next(iter(who))
            bins[b]['site_' + key] += 1
            site_bins[(k, b)]['r_' + key] += 1
        if n % BIN == 0:
            snaps[n] = [cnt['u'], cnt['t'],
                        sum(len(x) for i, x in bodies.items() if side(i) == 'u'),
                        sum(len(x) for i, x in bodies.items() if side(i) == 't'),
                        max((len(x) for i, x in bodies.items() if side(i) == 'u'), default=0),
                        max((len(x) for i, x in bodies.items() if side(i) == 't'), default=0)]

    turn_deaths = []

    def close_turn():
        hs = [d for d in turn_deaths if d[1] == 3]
        if len(hs) == 2:
            a = [d for d in hs if d[0] == actor]
            v = [d for d in hs if d[0] != actor]
            if a and v:
                a, v = a[0], v[0]
                b = rnd // BIN
                cross = a[2] != v[2]
                nearf = near[v[4]] <= 3
                if cross:
                    bins[b]['ho_mover_' + a[2]] += 1
                    bins[b]['ho_hit_' + v[2]] += 1
                    if nearf:
                        bins[b]['ho_fast_mover_' + a[2]] += 1
                    headons.append([rnd, a[2], a[3], v[3], v[4], int(nearf), site_of[v[4]] if nearf else -1])
                else:
                    bins[b]['ho_same_' + a[2]] += 1
        for d in turn_deaths:
            if d[1] != 3:
                bins[rnd // BIN]['die_' + CAUSE[d[1]] + '_' + d[2]] += 1
            bins[rnd // BIN]['deaths_' + d[2]] += 1
        turn_deaths.clear()

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            close_turn()
        if k == 0:
            rnd, actor = p.i32(0), None
            started = True
        elif k == 1:
            if actor is None:
                roundmark(rnd)
            actor = p.i32(0)
            bins[rnd // BIN]['turns_' + side(actor)] += 1
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present[c] = ('n' if actor is None else 'd', rnd)
                if actor is None:
                    bins[rnd // BIN]['born_fast' if c in fast else 'born_slow'] += 1
            else:
                o, br = present.pop(c)
                s = side(actor)
                b = rnd // BIN
                kind = 'drop' if o == 'd' else 'fast' if c in fast else 'slow'
                bins[b]['eat_' + kind + '_' + s] += 1
                if kind == 'fast':
                    site_bins[(site_of[c], b)]['eat_' + s] += 1
                    bins[b]['wait_fast_sum'] += rnd - br
                    bins[b]['wait_fast_n'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            bins[rnd // BIN]['split_' + side(p.i32(0))] += 1
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            turn_deaths.append((i, reason, side(i), len(bodies[i]), bodies[i][0]))
            bodies.pop(i)
    close_turn()
    return dict(game=rec['game'], battle=rec['battle'], rating=rec['opponent_rating'], result=rec['our_result'],
                ended_by=rec['ended_by'], last_round=rec['last_round'], w=w, h=h,
                sites=[[[c % w, c // w] for c in grp] for grp in sites],
                bins={str(b): dict(v) for b, v in sorted(bins.items())},
                site_bins={'%d:%d' % k: dict(v) for k, v in sorted(site_bins.items())},
                snaps={str(n): v for n, v in sorted(snaps.items())}, headons=headons)


def main():
    layout, tag = sys.argv[1], sys.argv[2]
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    oi = maps[layout]['observed_intervals']
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
        print(n + 1, len(recs), r['game'], flush=True)
    body = '\n'.join(out) + '\n'
    if tag == 'islands':
        Path(WORK + 'isl_trace-islands.jsonl').write_text(body)
    elif tag == 'australia':
        Path(WORK + 'isl_trace-australia.jsonl').write_text(body)
    elif tag == 'unsw':
        Path(WORK + 'isl_trace-unsw.jsonl').write_text(body)
    elif tag == 'slithery':
        Path(WORK + 'isl_trace-slithery.jsonl').write_text(body)
    else:
        Path(WORK + 'isl_trace-other.jsonl').write_text(body)
    print('done', len(out), 'fast tiles', len(fast_xy), 'sites', len(geos['sites']))


main()
