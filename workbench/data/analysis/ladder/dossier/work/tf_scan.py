"""Scratch (diag-topfight): every head-on, every chance to start one, and where dragons end their turns, both sides.
Sides are 0 = team A, 1 = team B of the game file; the aggregator maps them to team ids.
reach   = from a head of length L over free tiles: free steps ceil(L/4), then one segment a step down to length 2;
          a step onto a pearl costs nothing. Search by steps first, capped at 8 steps.
chance  = at the start of a dragon's turn an enemy head is inside its reach. One row per (dragon turn, enemy head).
exposed = at the end of a dragon's own turn its head is inside the reach of an enemy head (2 = free steps, 1 = paid).
head-on = a death with engine reason 3; the mover is the dragon whose turn it is. Drops followed 5 and 15 rounds.
Writes one JSON line per game. Usage: python3 tf_scan.py <tag> <label> <shard> <shards> [limit] [files of games to skip...]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAP = 8
MARKS = (100, 200, 300, 400)


def save(tag, body):
    if tag == 'T3-0':
        Path(OUT + 'tf_scan-T3-0.jsonl').write_text(body)
    elif tag == 'T3-1':
        Path(OUT + 'tf_scan-T3-1.jsonl').write_text(body)
    elif tag == 'T3b-0':
        Path(OUT + 'tf_scan-T3b-0.jsonl').write_text(body)
    elif tag == 'T3b-1':
        Path(OUT + 'tf_scan-T3b-1.jsonl').write_text(body)
    elif tag == 'T3c-0':
        Path(OUT + 'tf_scan-T3c-0.jsonl').write_text(body)
    elif tag == 'T3d-0':
        Path(OUT + 'tf_scan-T3d-0.jsonl').write_text(body)
    elif tag == 'T1-0':
        Path(OUT + 'tf_scan-T1-0.jsonl').write_text(body)
    elif tag == 'T1-1':
        Path(OUT + 'tf_scan-T1-1.jsonl').write_text(body)
    elif tag == 'T1-2':
        Path(OUT + 'tf_scan-T1-2.jsonl').write_text(body)
    elif tag == 'T1-3':
        Path(OUT + 'tf_scan-T1-3.jsonl').write_text(body)
    elif tag == 'OQ-0':
        Path(OUT + 'tf_scan-OQ-0.jsonl').write_text(body)
    elif tag == 'OQ-1':
        Path(OUT + 'tf_scan-OQ-1.jsonl').write_text(body)
    elif tag == 'OM-0':
        Path(OUT + 'tf_scan-OM-0.jsonl').write_text(body)
    elif tag == 'OM-1':
        Path(OUT + 'tf_scan-OM-1.jsonl').write_text(body)
    elif tag == 'OB-0':
        Path(OUT + 'tf_scan-OB-0.jsonl').write_text(body)
    elif tag == 'OB-1':
        Path(OUT + 'tf_scan-OB-1.jsonl').write_text(body)
    elif tag == 'OT-0':
        Path(OUT + 'tf_scan-OT-0.jsonl').write_text(body)
    elif tag == 'OT-1':
        Path(OUT + 'tf_scan-OT-1.jsonl').write_text(body)
    else:
        Path(OUT + 'tf_scan-test.jsonl').write_text(body)


def lb(L):
    return L if L <= 7 else 8 if L <= 9 else 10 if L <= 14 else 15 if L <= 24 else 25


def band(r):
    return 0 if r <= 100 else 1 if r <= 300 else 2


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


def scan(path, meta, geos, want_rows):
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
    sd = {}

    def side(i):
        s = sd.get(i)
        if s is None:
            s = 0 if teams[i] == 'A' else 1
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
    hos, rows_out = [], []
    turns = Counter()
    ch = defaultdict(lambda: [0, 0])
    ex = defaultdict(lambda: [0] * 8)
    lr = defaultdict(lambda: [0] * 8)
    qa = defaultdict(lambda: [0, 0, 0])
    la = defaultdict(lambda: [0, 0, 0])
    sp = Counter()
    tr = Counter()
    dth = defaultdict(lambda: [0, 0])
    series, mix = {}, {}
    hist = {}
    parent = {}
    est, lkst = {}, {}
    top = [(0, -1), (0, -1)]
    st8 = dict(rnd=0, actor=None, used=0, ate=0, cur=None, half=None)

    def gap(a, c):
        return torus(a % w, c % w, w) + torus(a // w, c // w, h)

    def kind_of(i, L):
        s = sd[i]
        if i == queen[s]:
            return 1
        if L >= 8 and L >= top[s][0]:
            return 2
        return 0

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

    def lmix():
        out = [[0] * 6, [0] * 6]
        for i, b in bodies.items():
            L = len(b)
            out[side(i)][0 if L <= 2 else 1 if L == 3 else 2 if L == 4 else 3 if L <= 7 else 4 if L <= 14 else 5] += 1
        return out

    def reach_map(src, L):
        free = (L + 3) // 4
        budget = free + L - 2
        d = {src: (0, 0)}
        hits = {}
        q = deque([src])
        while q:
            c = q.popleft()
            stp, co = d[c]
            if stp >= CAP:
                continue
            for t in adj[c]:
                if occ[t]:
                    if co + 1 <= budget:
                        v = (stp + 1, co + 1)
                        o = hits.get(t)
                        if o is None or v < o:
                            hits[t] = v
                    continue
                nc = co if t in present else co + 1
                if nc > budget - 1:
                    continue
                o = d.get(t)
                if o is not None and o <= (stp + 1, nc):
                    continue
                d[t] = (stp + 1, nc)
                q.append(t)
        return d, hits, free

    def near_heads(c, s, skip, rad):
        n = 0
        for t in hset[s]:
            if heads[t] != skip and gap(t, c) <= rad:
                n += 1
        return n

    def anc_pos(i, r):
        hh = hist.get(r)
        if hh is None:
            return None
        while i not in hh and i in parent:
            i = parent[i]
        return hh.get(i)

    def nearest_long(c, s, skip):
        best, bl = 99, 0
        for i, b in bodies.items():
            if i != skip and sd[i] == s and len(b) >= 10:
                d_ = gap(b[0], c)
                if d_ < best:
                    best, bl = d_, len(b)
        return best, bl

    def end_turn():
        cur = st8['cur']
        if cur is None:
            return
        st8['cur'] = None
        s, a, L0, bd = cur['s'], cur['id'], cur['L'], cur['bd']
        for r_ in cur['rows'].values():
            k_ = (s, lb(L0), lb(r_[6]), r_[15], r_[7], int(r_[11] + 1 <= r_[12]), bd, cur['kind'])
            v = ch[k_]
            v[0] += 1
            if r_[14] == 1:
                v[1] += 1
            if want_rows:
                rows_out.append(r_)
        lk = cur['lk']
        b = bodies.get(a)
        if b is None:
            if lk is not None:
                lr[lk[0]][5] += 1
            est.pop(a, None)
            tr[(s,) + cur['tr'] + (8,)] += 1
            return
        hd1 = b[0]
        L1 = len(b)
        en = 1 - s
        d1 = 7
        for e in g.ball(hd1).intersection(hset[en]):
            d_ = gap(hd1, e)
            if d_ < d1:
                d1 = d_
        tr[(s,) + cur['tr'] + (d1 if d1 <= 4 else 5 if d1 <= 6 else 7,)] += 1
        if lk is not None:
            v = lr[lk[0]]
            v[0] += 1
            if lk[1] is not None:
                d1 = gap(hd1, lk[1])
                v[1 if d1 < lk[2] else 2 if d1 == lk[2] else 3] += 1
            if st8['used'] >= 2:
                v[4] += 1
            v[7] += st8['used']
        if cur['qa'] is not None:
            gb, g0, t = cur['qa']
            g1 = gap(hd1, t)
            v = qa[(s, bd, gb)]
            v[0] += 1
            if g1 < g0:
                v[1] += 1
            elif g1 > g0:
                v[2] += 1
        if cur['la'] is not None:
            gb, g0, t = cur['la']
            g1 = gap(hd1, t)
            v = la[(s, bd, gb)]
            v[0] += 1
            if g1 < g0:
                v[1] += 1
            elif g1 > g0:
                v[2] += 1
        state = 0
        safe = 0
        maps = {}
        near = g.ball(hd1).intersection(hset[en])
        for e in near:
            M = len(bodies[heads[e]])
            m = reach_map(e, M)
            maps[e] = m
            hv = m[1].get(hd1)
            if hv is not None:
                state = max(state, 2 if hv[0] <= m[2] else 1)
        if state:
            for x in adj[cur['hd']]:
                if occ[x] or x == hd1:
                    continue
                sx = 0
                for e in g.ball(x).intersection(hset[en]):
                    m = maps.get(e)
                    if m is None:
                        m = reach_map(e, len(bodies[heads[e]]))
                        maps[e] = m
                    hv = m[0].get(x)
                    if hv is not None:
                        sx = max(sx, 2 if hv[0] <= m[2] else 1)
                        if sx == 2:
                            break
                if sx == 0:
                    safe = 1
                    break
        k_ = (s, bd, lb(L1), kind_of(a, L1))
        v = ex[k_]
        v[0] += 1
        if state:
            v[state] += 1
            if safe:
                v[2 + state] += 1
        est[a] = (k_, state, safe)

    events = root.pointer(3)
    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            end_turn()
            rnd = p.i32(0)
            st8['rnd'] = rnd
            st8['actor'] = None
            hist[rnd] = {i: b[0] for i, b in bodies.items()}
            tp = [(0, -1), (0, -1)]
            for i, b in bodies.items():
                s = side(i)
                if i != queen[s] and len(b) > tp[s][0]:
                    tp[s] = (len(b), i)
            top[0], top[1] = tp
            if rnd in MARKS:
                series[rnd] = stand()
                mix[rnd] = lmix()
        elif k == 1:
            end_turn()
            actor = p.i32(0)
            rnd = st8['rnd']
            st8['actor'] = actor
            st8['used'] = 0
            st8['ate'] = 0
            b = bodies[actor]
            s = side(actor)
            en = 1 - s
            L = len(b)
            hd = b[0]
            bd = band(rnd)
            kd = kind_of(actor, L)
            turns[(s, bd, lb(L), kd)] += 1
            lkst.pop(actor, None)
            cur = dict(id=actor, s=s, L=L, hd=hd, kind=kd, bd=bd, rows={}, ov=-1, ev=-1, lk=None, qa=None, la=None)
            st8['cur'] = cur
            near = g.ball(hd).intersection(hset[en])
            d0, m0 = 7, 0
            for e in near:
                d_ = gap(hd, e)
                if d_ < d0:
                    d0, m0 = d_, len(bodies[heads[e]])
            cur['tr'] = (3 if kd == 1 else 0 if L <= 4 else 1 if L <= 7 else 2, 3 if d0 > 6 else 0 if m0 < L else 1 if m0 == L else 2,
                         d0 if d0 <= 4 else 5 if d0 <= 6 else 7)
            if near:
                d, hits, free = reach_map(hd, L)
                found = [(t, hits[t]) for t in near if t in hits]
                if found:
                    win = g.window(hd)
                    ov = ev_ = 0
                    for c in win:
                        j = heads.get(c)
                        if j is None or j == actor:
                            continue
                        if sd[j] == s:
                            ov += 1
                        else:
                            ev_ += 1
                    cur['ov'], cur['ev'] = ov, ev_
                    for t, (stp, co) in found:
                        j = heads[t]
                        tb = bodies[j]
                        M = len(tb)
                        vis = sum(1 for z in tb if z in win)
                        rc = 0 if stp <= free else 1 if stp - free == 1 else 2
                        cur['rows'][j] = [rnd, s, actor, L, kd, j, M, kind_of(j, M), stp, free, stp - co, ov, ev_, vis, 0, rc,
                                          alive[s], alive[en], hd % w, hd // w, t % w, t // w]
            if L >= 8 or kd == 1:
                best = None
                for e in near:
                    if len(bodies[heads[e]]) <= 5:
                        d_ = gap(hd, e)
                        if d_ <= 6 and (best is None or d_ < best[0]):
                            best = (d_, e)
                n5 = near_heads(hd, s, actor, 5)
                btw = 0
                if best is not None:
                    for t in hset[s]:
                        if t != hd and gap(t, best[1]) < best[0] and gap(t, best[1]) + gap(t, hd) <= best[0] + 1:
                            btw = 1
                            break
                cls = (0 if L <= 4 else 1) if kd == 1 else (2 if L <= 14 else 3)
                d0b = 0 if best is None else 1 if best[0] <= 2 else 2 if best[0] == 3 else 3
                k_ = (s, bd, cls, d0b, min(n5, 2), btw)
                cur['lk'] = (k_, best[1] if best else None, best[0] if best else 0)
                lkst[actor] = k_
            elif L <= 4:
                eq = bodies.get(queen[en])
                if eq is not None:
                    g0 = gap(hd, eq[0])
                    cur['qa'] = (0 if g0 <= 3 else 1 if g0 <= 6 else 2 if g0 <= 12 else 3 if g0 <= 20 else 4, g0, eq[0])
                tl, ti = top[en]
                et = bodies.get(ti) if tl >= 10 else None
                if et is not None:
                    g0 = gap(hd, et[0])
                    cur['la'] = (0 if g0 <= 3 else 1 if g0 <= 6 else 2 if g0 <= 12 else 3 if g0 <= 20 else 4, g0, et[0])
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
                st8['ate'] += 1
                actor = st8['actor']
                if rec is not None:
                    ho, which = rec
                    age = st8['rnd'] - ho['r']
                    if age <= 15:
                        es = side(actor)
                        tag = which + ('m' if es == ho['ms'] else 'v')
                        ho[tag + '15'] += 1
                        if age <= 5:
                            ho[tag] += 1
                            if es == ho['ms']:
                                La = len(bodies[actor])
                                if actor == queen[es]:
                                    ho['fq'] += 1
                                elif La >= 10:
                                    ho['fb'] += 1
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
                if i == st8['actor']:
                    st8['used'] += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            par, child = p.i32(0), p.i32(4)
            s = side(par)
            before = len(bodies[par])
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
            parent[child] = par
            alive[s] += 1
            sp[(s, band(st8['rnd']), min(before, 16), min(len(bodies[par]), 16), int(par == queen[s]))] += 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            actor = st8['actor']
            rnd = st8['rnd']
            cur = st8['cur']
            s = side(i)
            b = bodies[i]
            L = len(b)
            hd = b[0]
            rec = None
            code = reason
            if reason == 3 and i != actor:
                ms = side(actor)
                code = 6 if ms != s else 16
                mrow = cur['rows'].get(i) if cur else None
                if mrow is not None:
                    mrow[14] = 1
                L0 = cur['L']
                e_ = est.get(i)
                lk_ = lkst.get(i)
                if lk_ is not None:
                    lr[lk_][6] += 1
                if e_ is not None and ms != s:
                    ex[e_[0]][5 + e_[1]] += 1
                gs = []
                for back in (10, 20):
                    pm, pv = anc_pos(actor, rnd - back), anc_pos(i, rnd - back)
                    gs.append(gap(pm, pv) if pm is not None and pv is not None else -1)
                ml = nearest_long(hd, ms, actor)
                vl = nearest_long(hd, s, i)
                half = dict(r=rnd, ms=ms, mid=actor, vid=i, cross=int(ms != s), L0=L0, Ld=len(bodies[actor]), Lv=L,
                            mk=cur['kind'], vk=kind_of(i, L), d=mrow[8] if mrow else -1, k=st8['used'] + 1, free=(L0 + 3) // 4,
                            ate=st8['ate'], ov=cur['ov'], ev=cur['ev'], vis=mrow[13] if mrow else -1,
                            m5=near_heads(hd, ms, actor, 5), v5=near_heads(hd, s, i, 5), nm=alive[ms], nv=alive[s],
                            vs=e_[1] if e_ else -1, vsafe=e_[2] if e_ else 0, g10=gs[0], g20=gs[1],
                            ml=ml[0], mll=ml[1], vl=vl[0], vll=vl[1],
                            sx=cur['hd'] % w, sy=cur['hd'] // w, x=hd % w, y=hd // w,
                            dm=0, dv=(L + 1) // 2, mm=0, mv=0, vm=0, vv=0, mm15=0, mv15=0, vm15=0, vv15=0, fb=0, fq=0)
                st8['half'] = half
                hos.append(half)
                rec = (half, 'v')
            elif reason == 3 and i == actor:
                half = st8['half']
                half['dm'] = (L + 1) // 2
                rec = (half, 'm')
                code = 5 if half['cross'] else 15
            v = dth[(s, band(rnd), code)]
            v[0] += 1
            v[1] += L
            if heads.get(hd) == i:
                del heads[hd]
                hset[s].discard(hd)
            for seg, c in enumerate(b):
                occ[c] -= 1
                if seg % 2 == 0:
                    expected.append((c, rec))
            bodies.pop(i)
            est.pop(i, None)
            lkst.pop(i, None)
            alive[s] -= 1
    end_turn()
    final = stand()
    for z in (0, 1):
        stt = root.pointer(4).pointer(z)
        assert (final[4 * z], final[4 * z + 1], final[4 * z + 2]) == (stt.i32(0), stt.i32(4), stt.i32(8)), (final, z)

    def flat(dct):
        return [list(k_) + (list(v) if isinstance(v, list) else [v]) for k_, v in sorted(dct.items())]

    out = dict(meta, w=w, h=h, cells=w * h, last_round=st8['rnd'], queen=queen, final=final, series=series, mix=mix,
               turns=flat(turns), ch=flat(ch), ex=flat(ex), lr=flat(lr), qa=flat(qa), la=flat(la), sp=flat(sp), dth=flat(dth), tr=flat(tr),
               hos=hos)
    if want_rows:
        out['rows'] = rows_out
    return out


def folders(label):
    base = Path('data/online')
    if label == 'T3':
        return sorted(p for p in (base / 'top3').iterdir() if p.is_dir())
    if label == 'T1':
        out = []
        for line in Path('data/top1/index.jsonl').read_text().splitlines():
            if line.strip():
                out.append(base / 'top1' / str(json.loads(line)['battle']))
        return sorted(set(out))
    names = dict(OQ=['agg8-q1-new'], OM=['agg7-m1-new', 'agg7-m2-new', 'agg7-m3-new'], OB=['agg7-b1-new', 'agg7-b2-new'])
    if label in names:
        return [base / 'smoke' / n for n in names[label]]
    if label == 'OT':
        return sorted(p for p in (base / 'smoke').iterdir() if p.is_dir() and p.name.startswith('top-l'))
    raise SystemExit('label')


def main():
    tag, label, shard, shards = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    limit = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    skip = set()
    for name in sys.argv[6:]:
        f = Path(name)
        if not f.is_file():
            continue
        for line in f.read_text().splitlines():
            if line.strip():
                skip.add(json.loads(line)['game'])
    games = []
    for f in folders(label):
        if not f.is_dir():
            continue
        for gj in sorted(f.glob('game-*.json')):
            j = json.loads(gj.read_text())
            rp = f / ('M%d.replay' % j['id'])
            if not rp.is_file() or j.get('status') != 'completed' or j['id'] in skip:
                continue
            games.append((j['id'], rp, dict(game=j['id'], folder=f.name, label=label, a=j['teamAId'], b=j['teamBId'],
                                            an=j.get('teamAName'), bn=j.get('teamBName'), ae=j.get('teamAElo'), be=j.get('teamBElo'),
                                            winner=j.get('winner'), map=j.get('mapName'), ranked=j.get('ranked'))))
    games.sort(key=lambda t: t[0])
    games = [t for n, t in enumerate(games) if n % shards == shard]
    if limit:
        games = games[:limit]
    geos, bad, out = {}, [], []
    want_rows = label != 'T1'
    for n, (gid, rp, meta) in enumerate(games):
        try:
            out.append(json.dumps(scan(rp, meta, geos, want_rows), separators=(',', ':')))
        except Exception as e:
            bad.append((gid, repr(e)[:200]))
        if n % 5 == 4:
            save(tag, '\n'.join(out) + '\n')
            print(n + 1, len(games), len(bad), flush=True)
    save(tag, '\n'.join(out) + '\n')
    print('done', tag, label, shard, len(games), 'ok', len(out), 'bad', bad, flush=True)


main()
