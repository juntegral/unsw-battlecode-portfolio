"""Scratch (diag-toprams): every head-on, every contact turn of a dragon of 2 to 4, and every meeting of two short dragons.
Sides are 0 = team A, 1 = team B of the game file; the aggregator maps them to team ids.
Engine reach (rules/execution-order.md 46-53): the first ceil(L/4) steps are free (L at the move start); a later step needs
current length 3 or more; a pearl on a step adds one, a paid step then removes one; the hit is checked before the pay.
plain reach = over free tiles, pearls not counted: ceil(L/4) + L - 2 steps (the bot's sprint_reach).
class of a tile for an enemy head: 4 = inside its free steps, 3 = free steps plus one paid, 2 = more paid steps, 1 = only with a pearl on the way.
Usage: python3 tr_scan.py <tag> <label> <shard> <shards> [limit]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
RMAX = 150
RB = 5
BALL = 6


def save(tag, body):
    if tag == 'D0':
        Path(OUT + 'tr_scan-D0.jsonl').write_text(body)
    elif tag == 'D1':
        Path(OUT + 'tr_scan-D1.jsonl').write_text(body)
    elif tag == 'T0':
        Path(OUT + 'tr_scan-T0.jsonl').write_text(body)
    elif tag == 'T1':
        Path(OUT + 'tr_scan-T1.jsonl').write_text(body)
    elif tag == 'Q0':
        Path(OUT + 'tr_scan-Q0.jsonl').write_text(body)
    elif tag == 'Q1':
        Path(OUT + 'tr_scan-Q1.jsonl').write_text(body)
    else:
        Path(OUT + 'tr_scan-test.jsonl').write_text(body)


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
        d = self.balls.get(src)
        if d is None:
            d = {src: 0}
            q = deque([src])
            while q:
                c = q.popleft()
                if d[c] >= BALL:
                    continue
                for t in self.adj[c]:
                    if t not in d:
                        d[t] = d[c] + 1
                        q.append(t)
            self.balls[src] = d
        return d

    def field(self, srcs):
        d = [-1] * (self.w * self.h)
        q = deque()
        for c in srcs:
            d[c] = 0
            q.append(c)
        while q:
            c = q.popleft()
            for t in self.adj[c]:
                if d[t] < 0:
                    d[t] = d[c] + 1
                    q.append(t)
        return d


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def scan(path, meta, geos):
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
    key = (w, h, hash(tuple(raw)))
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    adj = g.adj
    cells = w * h
    sd = {}

    def side(i):
        s = sd.get(i)
        if s is None:
            s = 0 if teams[i] == 'A' else 1
            sd[i] = s
        return s

    queen = [min(i for i in bodies if side(i) == 0), min(i for i in bodies if side(i) == 1)]
    zd = [g.field([b[0] for i, b in bodies.items() if side(i) == s]) for s in (0, 1)]
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
    rams, rows, meets = [], [], []
    turns = Counter()
    marks = {}
    last_row = {}
    had_turn = set()
    active = {}
    by_id = defaultdict(set)
    st = dict(rnd=0, actor=None, used=0, ate=0, cur=None, half=None, first=None, split=0, L0=0, hd0=0, info=None)

    def gap(a, c):
        return torus(a % w, c % w, w) + torus(a // w, c // w, h)

    def zone(c, s):
        du, dt = zd[s][c], zd[1 - s][c]
        if du < 0 or dt < 0:
            return 3
        if du + dt == 0:
            return 1
        q_ = du / (du + dt)
        return 0 if q_ < 0.4 else 2 if q_ > 0.6 else 1

    def bfs_free(src, depth):
        out = {}
        seen = {src}
        cur = [src]
        for j in range(depth):
            nxt = []
            for c in cur:
                for t in adj[c]:
                    if t in seen:
                        continue
                    seen.add(t)
                    out[t] = j + 1
                    if not occ[t]:
                        nxt.append(t)
            cur = nxt
            if not cur:
                break
        return out

    def strike(src, M):
        free = (M + 3) // 4
        plain = bfs_free(src, min(free + M - 2, 5))
        true = {}
        best = {src: M}
        cur = {src: M}
        for j in range(5):
            paid = j + 1 > free
            nxt = {}
            for c, ln in cur.items():
                if paid and ln < 3:
                    continue
                for t in adj[c]:
                    if t == src:
                        continue
                    if t not in true:
                        true[t] = j + 1
                    if occ[t] or t in best:
                        continue
                    l2 = ln + (1 if t in present else 0) - (1 if paid else 0)
                    if nxt.get(t, 0) < l2:
                        nxt[t] = l2
            for t, l2 in nxt.items():
                best[t] = l2
            cur = nxt
            if not cur:
                break
        return plain, true, free

    def cls_of(sm, x):
        k = sm[0].get(x)
        if k is not None:
            return 4 if k <= sm[2] else 3 if k == sm[2] + 1 else 2
        return 1 if x in sm[1] else 0

    def lunge_pearl(src, L, cap, win):
        reach = min((L + 3) // 4 + L - 2, cap)
        dist = {src: 0}
        dq = deque([src])
        out = {}
        while dq:
            c = dq.popleft()
            stp = dist[c]
            if stp >= reach:
                continue
            for t in adj[c]:
                if t in dist:
                    continue
                if occ[t]:
                    if t not in out:
                        out[t] = stp + 1
                    continue
                if t in present and t in win:
                    dist[t] = stp
                    dq.appendleft(t)
                else:
                    dist[t] = stp + 1
                    dq.append(t)
        return out

    def pearl_dist(src):
        if src in present:
            return 0
        seen = {src}
        cur = [src]
        for j in range(7):
            nxt = []
            for c in cur:
                for t in adj[c]:
                    if t in seen or occ[t]:
                        continue
                    if t in present:
                        return j + 1
                    seen.add(t)
                    nxt.append(t)
            cur = nxt
            if not cur:
                break
        return -1

    def near_heads(c, s, skip, rad):
        n = 0
        for t in hset[s]:
            if heads[t] != skip and gap(t, c) <= rad:
                n += 1
        return n

    def expo(m, mkey, mover):
        a, bb = mkey
        ta, tb = bodies[a][0], bodies[bb][0]
        ea = cls_of(strike(tb, len(bodies[bb])), ta)
        eb = cls_of(strike(ta, len(bodies[a])), tb)
        if ea or eb:
            m['first'] = [st['rnd'], mover, ea, eb, len(bodies[a]), len(bodies[bb])]

    def m_end(mkey, code, who, ri):
        m = active.pop(mkey)
        by_id[mkey[0]].discard(mkey)
        by_id[mkey[1]].discard(mkey)
        m['r1'] = st['rnd']
        m['end'] = code
        m['who'] = who
        m['ri'] = ri
        m['L1'] = [len(bodies[z]) if z in bodies else 0 for z in mkey]
        meets.append(m)

    def end_turn():
        cur = st['cur']
        a = st['actor']
        st['cur'] = None
        if a is None:
            return
        rnd = st['rnd']
        b = bodies.get(a)
        had_turn.add(a)
        if b is None:
            if cur is not None and cur.get('dead') is None:
                cur['dead'] = 9
            if cur is not None and (cur['near'] or cur.get('dead') == 3) and not cur.get('_e'):
                cur['_e'] = 1
                rows.append(cur)
            return
        s = sd[a]
        en = 1 - s
        hd1 = b[0]
        L1 = len(b)
        bl = g.ball(hd1)
        if cur is not None:
            endl = []
            for t in hset[en]:
                d = bl.get(t)
                if d is None or d > RB:
                    continue
                j = heads[t]
                M = len(bodies[j])
                sm = strike(t, M)
                endl.append([j, M, d, cls_of(sm, hd1), sm[1].get(hd1, 0)])
            cur['L1'] = L1
            cur['hd1'] = hd1
            cur['k'] = st['used']
            cur['ate'] = st['ate']
            cur['sp'] = st['split']
            cur['first'] = st['first'] if st['first'] is not None else -1
            cur['end'] = endl
            last_row[a] = cur
            if (cur['near'] or endl) and rnd <= RMAX:
                cur['_e'] = 1
                rows.append(cur)
        for mkey in list(by_id.get(a, ())):
            y = mkey[1] if mkey[0] == a else mkey[0]
            d = bl.get(bodies[y][0], 99)
            if d > 3:
                m_end(mkey, 'part', -1, -1)
                continue
            m = active[mkey]
            m['n'] += 1
            if m['first'] is None:
                expo(m, mkey, s)
        if L1 <= 4 and rnd <= RMAX:
            for t in list(hset[en]):
                d = bl.get(t)
                if d is None or d > 3:
                    continue
                y = heads[t]
                if len(bodies[y]) > 4:
                    continue
                mkey = (a, y) if s == 0 else (y, a)
                if mkey in active:
                    continue
                m = dict(r0=rnd, ids=list(mkey), q=[int(mkey[0] == queen[0]), int(mkey[1] == queen[1])],
                         L0=[len(bodies[mkey[0]]), len(bodies[mkey[1]])], by=s, born=int(st['born']), d0=d,
                         z=zone(bodies[mkey[0]][0], 0), first=None, ts=[[0, 0, 0, 0], [0, 0, 0, 0]],
                         fn=[-1, -1], fo=[-1, -1], fe=[-1, -1], n=0, h5=[near_heads(hd1, 0, mkey[0], 5), near_heads(hd1, 1, mkey[1], 5)])
                active[mkey] = m
                by_id[mkey[0]].add(mkey)
                by_id[mkey[1]].add(mkey)
                expo(m, mkey, s)

    events = root.pointer(3)
    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            end_turn()
            rnd = p.i32(0)
            st['rnd'] = rnd
            st['actor'] = None
            if rnd in (50, 100, 150):
                ln = [[0, 0, 0, 0], [0, 0, 0, 0]]
                for i, b in bodies.items():
                    v = ln[side(i)]
                    L = len(b)
                    v[0] += 1
                    v[1] += L
                    if L <= 4:
                        v[2] += 1
                    v[3] = max(v[3], L)
                marks[rnd] = ln
            if rnd == RMAX + 21:
                for mkey in list(active):
                    m_end(mkey, 'open', -1, -1)
        elif k == 1:
            end_turn()
            actor = p.i32(0)
            rnd = st['rnd']
            b = bodies[actor]
            s = side(actor)
            en = 1 - s
            L = len(b)
            hd = b[0]
            st['actor'] = actor
            st['used'] = 0
            st['ate'] = 0
            st['first'] = None
            st['split'] = 0
            st['L0'] = L
            st['hd0'] = hd
            st['born'] = actor not in had_turn
            bd = 0 if rnd <= 100 else 1 if rnd <= RMAX else 2
            turns[(s, bd, min(L, 5), int(actor == queen[s]))] += 1
            needrow = L <= 4 and rnd <= RMAX
            mine = by_id.get(actor)
            if not needrow and not mine:
                continue
            bl = g.ball(hd)
            near = []
            for t in hset[en]:
                d = bl.get(t)
                if d is not None and d <= RB:
                    near.append((t, d))
            if not near and not mine:
                if needrow:
                    st['cur'] = dict(r=rnd, s=s, id=actor, q=int(actor == queen[s]), L=L, hd=hd, near=[], lite=1)
                continue
            win = g.window(hd)
            isq = actor == queen[s]
            nA = sum(1 for t in hset[s] if t in win) - 1
            view = [t for t in hset[en] if t in win]
            nE = len(view)
            aggr = cells <= 1200
            units_ok = alive[s] >= (1 if aggr else 8)
            edge_ok = nA + 1 - nE >= 1
            cap = 3 if aggr else 4
            tn = tw = 0
            mnow, msst = set(), set()
            vparts = {}
            for t in view:
                j = heads[t]
                parts = sum(1 for z in bodies[j] if z in win)
                vparts[j] = parts
                if units_ok and edge_ok and parts >= L:
                    tn = 1
                if units_ok and edge_ok and parts >= L - 1:
                    tw = 1
                if parts < 5:
                    for x, dx in bfs_free(t, max(1, parts - 1)).items():
                        if dx <= 1:
                            mnow.add(x)
                        msst.add(x)
            su = strike(hd, L)
            lp = lunge_pearl(hd, L, cap, win) if L <= 4 else {}
            smaps = {}
            entries = []
            info = {}
            for t, d in near:
                j = heads[t]
                M = len(bodies[j])
                sm = strike(t, M)
                smaps[j] = sm
                parts = vparts.get(j, 0)
                eng = su[1].get(t, 0)
                pl = su[0].get(t, 0)
                if pl > cap:
                    pl = 0
                pp = lp.get(t, 0)
                hunt = int(parts >= 2 * L and not isq and L <= 4)
                t_now = int(units_ok and edge_ok and parts >= L and parts > 0 and L <= 4 and not isq)
                t_new = int(units_ok and edge_ok and parts >= L - 1 and parts > 0 and L <= 4 and not isq)
                el_now = int((t_now or hunt) and pl > 0)
                el_new = int((t_new or hunt) and pp > 0)
                entries.append([j, M, int(j == queen[en]), d, int(t in win), parts, cls_of(sm, hd), sm[1].get(hd, 0), eng, pl, pp,
                                t_now, t_new, hunt, el_now, el_new, t % w, t // w])
                info[j] = (eng, el_now, el_new)
            for mkey in list(mine or ()):
                y = mkey[1] if mkey[0] == actor else mkey[0]
                iv = info.get(y)
                m = active[mkey]
                v = m['ts'][s]
                v[0] += 1
                if iv is None:
                    continue
                if iv[0] > 0:
                    v[1] += 1
                    if m['fe'][s] < 0:
                        m['fe'][s] = rnd
                if iv[1]:
                    v[2] += 1
                    if m['fo'][s] < 0:
                        m['fo'][s] = rnd
                if iv[2]:
                    v[3] += 1
                    if not iv[1] and m['fn'][s] < 0:
                        m['fn'][s] = rnd
            if not needrow:
                continue
            opts = []
            for x in adj[hd]:
                if occ[x]:
                    continue
                cl = [cls_of(smaps[e_[0]], x) for e_ in entries]
                opts.append([x, int(x in present), pearl_dist(x), cl, int(x in mnow), int(x in msst)])
            st['cur'] = dict(r=rnd, s=s, id=actor, q=int(isq), L=L, hd=hd, z=zone(hd, s), nA=nA, nE=nE,
                             pv=sum(1 for c in win if c in present), dp=pearl_dist(hd), tn=tn, tw=tw, un=alive[s],
                             born=int(st['born']), near=entries, opt=opts, x=hd % w, y=hd // w)
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
                st['ate'] += 1
                actor = st['actor']
                if rec is not None:
                    ho, which = rec
                    if st['rnd'] - ho['r'] <= 5:
                        ho[which + ('m' if side(actor) == ho['ms'] else 'v')] += 1
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
                if i == st['actor']:
                    st['used'] += 1
                    if st['first'] is None:
                        st['first'] = hd
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            par, child = p.i32(0), p.i32(4)
            s = side(par)
            for c in bodies[par]:
                occ[c] -= 1
            if heads.get(bodies[par][0]) == par:
                del heads[bodies[par][0]]
                hset[s].discard(bodies[par][0])
            for z, i in enumerate((par, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
                heads[bodies[i][0]] = i
                hset[side(i)].add(bodies[i][0])
                for c in bodies[i]:
                    occ[c] += 1
            alive[s] += 1
            if par == st['actor']:
                st['split'] = 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            actor = st['actor']
            rnd = st['rnd']
            cur = st['cur']
            s = side(i)
            b = bodies[i]
            L = len(b)
            hd = b[0]
            rec = None
            ri = -1
            if reason == 3 and i != actor:
                ms = side(actor)
                L0 = st['L0']
                lr = last_row.get(i)
                ri = len(rams)
                half = dict(r=rnd, ms=ms, mid=actor, vid=i, cross=int(ms != s), mq=int(actor == queen[ms]), vq=int(i == queen[s]),
                            L0=L0, Ld=len(bodies[actor]), Lv=L, k=st['used'] + 1, free=(L0 + 3) // 4, ate=st['ate'],
                            sx=st['hd0'] % w, sy=st['hd0'] // w, x=hd % w, y=hd // w, zv=zone(hd, s), zm=zone(st['hd0'], ms),
                            m5=near_heads(hd, ms, actor, 5), v5=near_heads(hd, s, i, 5), inv=int(st['hd0'] in g.window(hd)),
                            nm=alive[ms], nv=alive[s], vrow=int(lr is not None), vnew=int(i not in had_turn),
                            dm=0, dv=(L + 1) // 2, mm=0, mv=0, vm=0, vv=0)
                if lr is not None:
                    lr['hit'] = ri
                    if not lr.get('_e') and not lr.get('lite'):
                        lr['_e'] = 1
                        rows.append(lr)
                    elif lr.get('lite'):
                        half['vlite'] = 1
                if cur is not None:
                    cur['dead'] = 3
                    cur['ri'] = ri
                st['half'] = half
                rams.append(half)
                rec = (half, 'v')
            elif reason == 3 and i == actor:
                half = st['half']
                half['dm'] = (L + 1) // 2
                rec = (half, 'm')
            elif i == actor and cur is not None:
                cur['dead'] = reason if reason != 3 else 9
            for mkey in list(by_id.get(i, ())):
                y = mkey[1] if mkey[0] == i else mkey[0]
                if reason == 3 and i != actor:
                    if actor == y:
                        m_end(mkey, 'ram', side(actor), ri)
                    else:
                        m_end(mkey, 'ram3', s, ri)
                elif reason == 3:
                    m_end(mkey, 'out', s, -1)
                else:
                    m_end(mkey, 'die', s, -1)
            if heads.get(hd) == i:
                del heads[hd]
                hset[s].discard(hd)
            for seg, c in enumerate(b):
                occ[c] -= 1
                if seg % 2 == 0:
                    expected.append((c, rec))
            bodies.pop(i)
            last_row.pop(i, None)
            alive[s] -= 1
    end_turn()
    for mkey in list(active):
        m_end(mkey, 'open', -1, -1)
    final = []
    for s in (0, 1):
        ls = [len(b) for i, b in bodies.items() if side(i) == s]
        final += [len(ls), max(ls, default=0), sum(ls)]
    for z in (0, 1):
        stt = root.pointer(4).pointer(z)
        assert (final[3 * z], final[3 * z + 1], final[3 * z + 2]) == (stt.i32(0), stt.i32(4), stt.i32(8)), (final, z)
    for r_ in rows:
        r_.pop('_e', None)
    return dict(meta, w=w, h=h, cells=cells, last_round=st['rnd'], queen=queen, final=final, marks=marks,
                turns=[list(k_) + [v] for k_, v in sorted(turns.items())], rams=rams, rows=rows, meets=meets)


def folders(label):
    base = Path('data/online')
    if label == 'T3':
        return sorted(p for p in (base / 'top3').iterdir() if p.is_dir())
    if label == 'OQ':
        return [base / 'smoke' / 'agg8-q1-new']
    if label == 'OT':
        return sorted(p for p in (base / 'smoke').iterdir() if p.is_dir() and p.name.startswith('top-l'))
    raise SystemExit('label')


def main():
    tag, label, shard, shards = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    limit = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    games = []
    for f in folders(label):
        if not f.is_dir():
            continue
        for gj in sorted(f.glob('game-*.json')):
            j = json.loads(gj.read_text())
            rp = f / ('M%d.replay' % j['id'])
            if not rp.is_file() or j.get('status') != 'completed':
                continue
            games.append((j['id'], rp, dict(game=j['id'], folder=f.name, label=label, a=j['teamAId'], b=j['teamBId'],
                                            an=j.get('teamAName'), bn=j.get('teamBName'), ae=j.get('teamAElo'), be=j.get('teamBElo'),
                                            winner=j.get('winner'), map=j.get('mapName'))))
    games.sort(key=lambda t: t[0])
    games = [t for n, t in enumerate(games) if n % shards == shard]
    if limit:
        games = games[:limit]
    geos, bad, out = {}, [], []
    for n, (gid, rp, meta) in enumerate(games):
        try:
            out.append(json.dumps(scan(rp, meta, geos), separators=(',', ':')))
        except Exception as e:
            bad.append((gid, repr(e)[:200]))
        if n % 5 == 4:
            save(tag, '\n'.join(out) + '\n')
            print(n + 1, len(games), len(bad), flush=True)
    save(tag, '\n'.join(out) + '\n')
    print('done', tag, label, shard, len(games), 'ok', len(out), 'bad', bad, flush=True)


main()
