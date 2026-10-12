"""Scratch (diag-attack): every head-on meeting and every chance to start one, both sides, all rounds, 500 main games.
chance  = at the start of a dragon's turn an enemy head can be entered this turn over free tiles: within its free steps
          (ceil(L/4)) or by paying one segment a step down to length 2 (ceil(L/4)+L-2 steps; search capped at 8 steps).
          One row per (dragon turn, enemy head in reach).
head-on = a death with engine reason 3; the mover is the dragon whose turn it is. Drops of both bodies are followed for 15 rounds.
Writes one line per game to at_scan-<shard>.jsonl. Usage: python3 data/analysis/ladder/dossier/work/at_scan.py <shard> <shards> [limit]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAP = 8


def lclass(L):
    return 0 if L <= 2 else 1 if L == 3 else 2 if L == 4 else 3 if L <= 7 else 4 if L <= 14 else 5


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.adj = []
        for y in range(h):
            for x in range(w):
                row = set()
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 1:
                        continue
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.add(dest)
                self.adj.append(sorted(row))
        self.wins = {}
        self.balls = {}

    def window(self, src):
        s = self.wins.get(src)
        if s is None:
            y, x = divmod(src, self.w)
            s = frozenset(((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4))
            self.wins[src] = s
        return s

    def ball(self, src):
        s = self.balls.get(src)
        if s is None:
            d = {src: 0}
            q = deque([src])
            while q:
                c = q.popleft()
                if d[c] >= CAP:
                    continue
                for t in self.adj[c]:
                    if t not in d:
                        d[t] = d[c] + 1
                        q.append(t)
            del d[src]
            s = frozenset(d)
            self.balls[src] = s
        return s


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def scan(row, geos):
    path = Path('data/online/ladder') / str(row['battle']) / ('M%d.replay' % row['game'])
    root = replay.load(path).root()
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
    key = (row['map_key'], w, h)
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    ours = row['our_side']
    sd = {}

    def side(i):
        s = sd.get(i)
        if s is None:
            s = 0 if teams[i] == ours else 1
            sd[i] = s
        return s

    queen = [min(i for i in bodies if side(i) == 0), min(i for i in bodies if side(i) == 1)]
    heads = {}
    hset = [set(), set()]
    occ = Counter()
    alive = [0, 0]
    for i, b in bodies.items():
        heads[b[0]] = i
        hset[side(i)].add(b[0])
        alive[side(i)] += 1
        for c in b:
            occ[c] += 1
    present = {}
    expected = deque()
    hos, chs = [], []
    turns = Counter()
    series = {}
    pend = {}
    rnd, actor, used, ate = 0, None, 0, 0
    cur = None
    half = None

    def gap(a, c):
        return torus(a % w, c % w, w) + torus(a // w, c // w, h)

    def longest(s, skip=-1):
        best = 0
        for i, b in bodies.items():
            if i != skip and sd[i] == s and len(b) > best:
                best = len(b)
        return best

    def near(c, s, skip, rad):
        n = 0
        for t in hset[s]:
            if gap(t, c) <= rad and heads[t] != skip:
                n += 1
        return n

    def stand():
        out = []
        for s in (0, 1):
            n = tot = big = 0
            for i, b in bodies.items():
                if side(i) == s:
                    n += 1
                    tot += len(b)
                    big = max(big, len(b))
            out += [n, big, tot, len(bodies.get(queen[s], ()))]
        return out

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor, cur = p.i32(0), None, None
            if rnd % 25 == 0:
                series[rnd] = stand()
        elif k == 1:
            actor = p.i32(0)
            used, ate = 0, 0
            b = bodies[actor]
            s = side(actor)
            L = len(b)
            hd = b[0]
            turns[(s, (rnd - 1) // 25 if rnd > 0 else 0, lclass(L), int(actor == queen[s]))] += 1
            pend.pop(actor, None)
            cur = dict(hd=hd, L=L, rows={}, ov=-1, ev=-1, lng=0)
            en = 1 - s
            if not g.ball(hd).isdisjoint(hset[en]):
                free = (L + 3) // 4
                found = []
                budget = free + L - 2
                d = {hd: (0, 0)}
                q = deque([hd])
                seen_t = {}
                while q:
                    c = q.popleft()
                    cc, cs = d[c]
                    if cs >= CAP:
                        continue
                    for t in g.adj[c]:
                        if occ[t]:
                            if t in hset[en] and cc + 1 <= budget:
                                old_ = seen_t.get(t)
                                if old_ is None or (cs + 1, cc + 1) < old_:
                                    seen_t[t] = (cs + 1, cc + 1)
                            continue
                        nc = cc if t in present else cc + 1
                        if nc > budget - 1:
                            continue
                        o = d.get(t)
                        if o is not None and o <= (nc, cs + 1):
                            continue
                        d[t] = (nc, cs + 1)
                        if nc == cc:
                            q.appendleft(t)
                        else:
                            q.append(t)
                for t, (st_, co_) in seen_t.items():
                    found.append((st_, heads[t], st_ - co_))
                if found:
                    win = g.window(hd)
                    ov = ev_ = lng = 0
                    bigs = []
                    for c in win:
                        j = heads.get(c)
                        if j is None or j == actor:
                            continue
                        if sd[j] == s:
                            ov += 1
                            if len(bodies[j]) > L:
                                lng += 1
                            if sum(1 for z in bodies[j] if z in win) >= 10:
                                bigs.append(c)
                        else:
                            ev_ += 1
                    cur.update(ov=ov, ev=ev_, lng=lng)
                    top_own = longest(s, actor)
                    top_en = longest(en)
                    for dist, j, pe in found:
                        tb = bodies[j]
                        Lt = len(tb)
                        th = tb[0]
                        vis = sum(1 for z in tb if z in win)
                        ft = (Lt + 3) // 4
                        mut = 2 if dist <= ft else 1 if dist <= ft + Lt - 2 else 0
                        r_ = [rnd, s, actor, L, int(actor == queen[s]), int(L >= top_own), j, Lt, int(j == queen[en]), int(Lt >= top_en),
                              dist, free, ov, ev_, near(th, s, actor, 5), near(th, en, j, 5), vis, alive[s], alive[en], lng,
                              int(any(gap(c, th) <= 6 for c in bigs)), mut, 0, 0, pe]
                        chs.append(r_)
                        cur['rows'][j] = r_
                    pend[actor] = cur['rows']
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                if expected:
                    xy, rec = expected.popleft()
                    assert xy == c
                    present[c] = rec
                else:
                    present[c] = None
            else:
                rec = present.pop(c)
                ate += 1
                if rec is not None and rnd - rec[0]['r'] <= 15:
                    ho, which = rec
                    es = side(actor)
                    ho[which + ('m' if es == ho['ms'] else 'v')] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                s = side(i)
                if heads.get(b[0]) == i:
                    del heads[b[0]]
                    hset[s].discard(b[0])
                b.appendleft(hd)
                heads[hd] = i
                hset[s].add(hd)
                occ[hd] += 1
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s = side(parent)
            for c in bodies[parent]:
                occ[c] -= 1
            if heads.get(bodies[parent][0]) == parent:
                del heads[bodies[parent][0]]
                hset[s].discard(bodies[parent][0])
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
                heads[bodies[i][0]] = i
                hset[side(i)].add(bodies[i][0])
                for c in bodies[i]:
                    occ[c] += 1
            alive[s] += 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            b = bodies[i]
            L = len(b)
            hd = b[0]
            rec = None
            if reason == 3 and i != actor:
                ms = side(actor)
                pr = pend.get(i)
                vc = 0
                if pr is not None:
                    for j, r_ in pr.items():
                        r_[23] = 1 if j == actor else 2
                    if actor in pr:
                        vc = 2 if pr[actor][10] <= pr[actor][11] else 1
                mrow = cur['rows'].get(i) if cur else None
                for j, r_ in (cur['rows'].items() if cur else ()):
                    r_[22] = 1 if j == i else 2
                L0 = cur['L']
                half = dict(r=rnd, ms=ms, mid=actor, vid=i, cross=int(ms != s), L0=L0, Ld=len(bodies[actor]), Lv=L,
                            mq=int(actor == queen[ms]), vq=int(i == queen[s]),
                            mtop=int(L0 >= longest(ms, actor)), vtop=int(L >= longest(s, i)),
                            vbig=int(L > longest(ms)), d=mrow[10] if mrow else -1, k=used + 1, free=(L0 + 3) // 4,
                            ate=ate, ov=cur['ov'], ev=cur['ev'], lng=cur['lng'], vis=mrow[16] if mrow else -1,
                            big=mrow[20] if mrow else -1, mut=mrow[21] if mrow else -1, pe=mrow[24] if mrow else -1,
                            m5=near(hd, ms, actor, 5), v5=near(hd, s, i, 5), nm=alive[ms], nv=alive[s], vc=vc,
                            sx=cur['hd'] % w, sy=cur['hd'] // w, x=hd % w, y=hd // w,
                            dm=0, dv=(L + 1) // 2, mm=0, mv=0, vm=0, vv=0)
                half['paid'] = max(0, half['k'] - half['free'])
                hos.append(half)
                rec = (half, 'v')
            elif reason == 3 and i == actor:
                half['dm'] = (L + 1) // 2
                rec = (half, 'm')
            elif i == actor and cur is not None and cur['rows']:
                for r_ in cur['rows'].values():
                    if r_[22] == 0:
                        r_[22] = 3
            if heads.get(hd) == i:
                del heads[hd]
                hset[s].discard(hd)
            for seg, c in enumerate(b):
                occ[c] -= 1
                if seg % 2 == 0:
                    expected.append((c, rec))
            bodies.pop(i)
            pend.pop(i, None)
            alive[s] -= 1
    final = stand()
    return dict(game=row['game'], battle=row['battle'], layout=row['map_key'], w=w, h=h, cells=w * h,
                rating=row['opponent_rating'], result=row['result'], ended_by=row['ended_by'],
                queens_at_end=row['queens_at_end'], last_round=rnd, queen=queen, final=final,
                series=series, turns=[[a, b_, c, d_, n] for (a, b_, c, d_), n in sorted(turns.items())], hos=hos, chs=chs)


def main():
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rows = json.loads(Path('data/analysis/ladder/dossier/input-snapshot.json').read_text())['rows']
    rows = sorted(rows, key=lambda r: r['game'])
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[:limit]
    geos, out, bad = {}, [], []
    for n, r in enumerate(rows):
        try:
            rec = scan(r, geos)
            f = rec['final']
            want = r['final']
            assert [f[0], f[1], f[2], f[4], f[5], f[6]] == [want['us']['alive'], want['us']['longest'], want['us']['total'],
                                                           want['them']['alive'], want['them']['longest'], want['them']['total']], (f, want)
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 10 == 9:
            print(n + 1, len(rows), len(bad), flush=True)
    body = '\n'.join(out) + '\n'
    if limit:
        Path(OUT + 'at_scan-test.jsonl').write_text(body)
    elif shard == 0:
        Path(OUT + 'at_scan-0.jsonl').write_text(body)
    elif shard == 1:
        Path(OUT + 'at_scan-1.jsonl').write_text(body)
    elif shard == 2:
        Path(OUT + 'at_scan-2.jsonl').write_text(body)
    elif shard == 3:
        Path(OUT + 'at_scan-3.jsonl').write_text(body)
    elif shard == 4:
        Path(OUT + 'at_scan-4.jsonl').write_text(body)
    else:
        Path(OUT + 'at_scan-5.jsonl').write_text(body)
    print('done', shard, len(out), 'bad', bad)


main()
