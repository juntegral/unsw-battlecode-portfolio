"""Scratch (diag-opening2): forward what-if of our second starter, built from o2_scan.py (same rebuild of score_step).
From round 0 the second starter of our side is walked as a virtual dragon for 40 rounds by the rebuilt score under each
variant, in the world of the replay (the other dragons and the pearls as they really were; a pearl the virtual dragon
eats is gone for it only). Variants: base (as built), head (a tie-size bonus for the step straight ahead),
nocentre (centre term off), units2 (centre term off while the side has 2 dragons or fewer), and head with each.
Not simulated: its children, the real queen reacting to it, enemies reacting, threat terms.
Usage: python3 data/analysis/ladder/dossier/work/o2_sim.py <O|L> 0 1 [limit]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import defaultdict, deque
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
DOS = Path('data/analysis/ladder/dossier')
ARMS = (('agg7-m1', 'MAIN'), ('agg7-m2', 'MAIN'), ('agg7-m3', 'MAIN'), ('agg7-b1', 'B7'), ('agg7-b2', 'B7'),
        ('agg8-q1', 'B7Q'), ('agg8-q2', 'B7Q'))
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LAST = 60
INF = 1 << 28
FOREVER = 1 << 20


TERMS = ('centre', 'room', 'terr', 'cramped', 'pearl', 'soon', 'hot', 'unseen', 'portal', 'far', 'eat', 'look', 'mate', 'pocket', 'sc', 'queen')
VARIANTS = ('base', 'head', 'nocentre', 'units2', 'head1', 'head6', 'headalone', 'head20', 'headblind')
SIMLAST = 40
HEAD_BONUS = 3.0


def tb(d, wt):
    return 0.0 if d < 0 else max(0.0, wt * (260 - 40 * d))


def parts(row, o, k, release, centre=True, variant=None):
    """Score terms of one step on offer; a dict term -> value (signed)."""
    dest, room, terr, tailhit, dp, ds, dh, du, dpo, dk, eat, sc, pocket, look, mate, cd, pk, kr, dsa, dpa = o
    L, r = row['L'], row['r']
    on = row['cm'] and r < row['cr'] and L <= 4 and row['ne'] - row['nm'] <= row['mg']
    released = release and row['cm'] and r < row['cr'] and L <= 4 and row['st'] >= 12
    cr = 0.0
    want = 3.0 * L + 8.0
    if room < want:
        cr += 400.0 * (want - room)
    if room < L + 2.0:
        cr += 5000.0 * (L + 2.0 - room)
    if not tailhit and not (released and room >= 6 * L + 8.0):
        cr += 600.0
    t = dict.fromkeys(TERMS, 0.0)
    t['room'] = 1.5 * room
    t['terr'] = 1.5 * terr
    t['cramped'] = -cr
    if row['isq']:
        q = 0.0
        if ((not tailhit) and room < want) or room < L + 8:
            q += 6000.0
        if kr > 0:
            q += 6000.0 + 400.0 * kr
        t['queen'] = -q
    cand = (('pearl', tb(dp, 2.0)), ('soon', tb(ds, 0.45)), ('hot', tb(dh, 1.2)), ('unseen', tb(du, 0.2)), ('portal', tb(dpo, 0.4)))
    name, val = max(cand, key=lambda kv: kv[1])
    if val > 0:
        t[name] = val
    far = [x for x in (dp, ds, dh, du) if x >= 0]
    if far:
        t['far'] = 2.0 * max(0, 80 - min(far))
    grown = L + eat
    full = pocket < 48 and grown > pocket // 2
    if full:
        t['pocket'] = -1000.0 * (grown - pocket // 2)
    if eat and not full:
        t['eat'] = 300.0
    if sc:
        t['sc'] = -300.0
    if centre and on and max(tb(dp, 2.0), tb(dh, 1.2)) <= 0.0:
        off = False
        if variant == 'units2':
            off = row['al'] <= 2
        elif variant == 'units3':
            off = row['al'] <= 3
        elif variant == 'nq':
            off = row['ro'] == 'o'
        elif variant == 'spawn':
            off = row.get('mdk', -1) >= 0 and row['mdk'] <= row['cd']
        elif variant == 'unfed':
            off = row.get('unfed', 0) == 1
        if not off:
            t['centre'] = -40.0 * ((min(du, 30) if du >= 0 else 30) if released else cd)
    if mate:
        t['mate'] = -450.0
    t['look'] = look
    if pk == 1:
        t['portal'] -= 150.0
    t['tie'] = 0.25 * ((row['i'] * 31 + r * 17 + k * 7) % 5)
    return t


def scores(row, release, centre=True, variant=None, drop=None):
    """Returns ([score or None] * 4, [parts or None] * 4)."""
    out, ps = [None] * 4, [None] * 4
    base = None
    blind = []
    for k, o in enumerate(row['o']):
        if o is None:
            continue
        if len(o) == 2:
            blind.append(k)
            continue
        t = parts(row, o, k, release, centre, variant)
        if drop:
            t[drop] = 0.0
        ps[k] = t
        out[k] = sum(t.values())
        if o[16] == 0:
            b = out[k] - t['tie'] - max(t['pearl'], t['soon'], t['hot'], t['unseen'], max(t['portal'], 0.0))
            if base is None or b > base:
                base = b
    for k in blind:
        if base is not None:
            out[k] = base + 88.0 + 0.25 * ((row['i'] * 31 + row['r'] * 17 + k * 7) % 5)
            ps[k] = dict(blind=out[k])
    return out, ps


def best(sc):
    v = [(s, -k) for k, s in enumerate(sc) if s is not None]
    return -max(v)[1] if v else -1


def jobs(src):
    out = []
    if src == 'O':
        for label, arm in ARMS:
            folder = Path('data/online/smoke') / (label + '-new')
            if not folder.is_dir():
                continue
            for mp in sorted(folder.glob('game-*.json')):
                j = json.loads(mp.read_text())
                rp = folder / ('M%d.replay' % j['id'])
                if rp.exists():
                    out.append((rp, j, 1119, arm, label))
    else:
        path = DOS / ('per-game.jsonl' if src == 'L' else 'target/per-game-top1.jsonl')
        team = 1119 if src == 'L' else 306
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            st = r['all_starting_dragons']
            if not all(len(st[s]) == 2 and 4 <= sum(d['length'] for d in st[s]) <= 6 for s in ('us', 'them')):
                continue
            rp = Path(r['replay'])
            j = json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text())
            j['opponent_rating'] = r.get('opponent_rating')
            out.append((rp, j, team, 'LADDER' if src == 'L' else 'RANK1', src))
    return out


def edge_id(w, h, x, y, d):
    return (2 * y * (w + 1) + x if d == 0 else (2 * y + 1) * (w + 1) + (x + 1) % w if d == 1
            else 2 * ((y + 1) % h) * (w + 1) + x if d == 2 else (2 * y + 1) * (w + 1) + x)


def build(w, h, raw):
    edges = {}
    for e, k, p in raw:
        row, x = divmod(e, w + 1)
        if row % 2 == 0 and x == w:
            continue
        e = 2 * ((row // 2) % h) * (w + 1) + x if row % 2 == 0 else row * (w + 1) + x % w
        if e not in edges or k > edges[e][0]:
            edges[e] = (k, p)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
    moves, pair = [], {}
    for y in range(h):
        for x in range(w):
            row = []
            for d, (dx, dy) in enumerate(STEP):
                e = edge_id(w, h, x, y, d)
                k, pid = edges.get(e, (0, -1))
                if k == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    ry, px = divmod(partner, w + 1)
                    dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    a = (ry // 2) * w + px % w
                    b = ((ry // 2 - 1) % h) * w + px % w if ry % 2 == 0 else (ry // 2) * w + (px - 1) % w
                    pair[(y * w + x, d)] = (a, b)
                else:
                    dest = ((y + dy) % h) * w + (x + dx) % w
                row.append((k, dest))
            moves.append(row)
    return moves, pair


class Mem:
    def __init__(self, n, plain):
        self.sr = [-1] * n
        self.fs = [-1] * n
        self.pe = bytearray(n)
        self.tm = [-2] * n
        self.hot = bytearray(n)
        self.low = [-1000] * n
        self.ka = [list(p) for p in plain]
        self.kk = [[0, 0, 0, 0] for _ in range(n)]
        self.stall_best = -1
        self.stall_round = 0


def scan(path, j, team, arm, label, gi, src, out):
    root = replay.load(Path(path)).root()
    lines = root.text(0).splitlines()
    w = h = 0
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = int(q[1]), int(q[2])
        elif q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    N = w * h
    own = 0 if j['teamAId'] == team else 1
    sd = {i: 0 if teams[i] == own else 1 for i in bodies}
    if sorted(sd.values()) != [0, 0, 1, 1]:
        return None
    if any(not 4 <= sum(len(bodies[i]) for i in sd if sd[i] == s) <= 6 for s in (0, 1)):
        return None
    moves, pair = build(w, h, raw)
    plain = [[((t // w + dy) % h) * w + (t % w + dx) % w for dx, dy in STEP] for t in range(N)]
    adj = [[t2 for k, t2 in row if k != 1] for row in moves]
    walls = [sum(1 for k, t2 in row if k == 1) for row in moves]
    pwatch = defaultdict(list)
    for (t, d), (a, b) in pair.items():
        pwatch[a].append((t, d))
        pwatch[b].append((t, d))
    cx, cy = w // 2, h // 2
    cdist = [min(abs(t % w - cx), w - abs(t % w - cx)) + min(abs(t // w - cy), h - abs(t // w - cy)) for t in range(N)]
    long_map = w >= 2 * h
    center_map = N <= 1000 and (long_map or N <= 700)
    center_rounds = 60 if long_map else 30
    center_margin = N if long_map else 0
    events = list(root.pointer(3))
    nat = defaultdict(list)
    rnd, actor = 0, None
    for ev in events:
        k = ev.u16(0)
        if k == 0:
            rnd, actor = ev.pointer(0).i32(0), None
        elif k == 1:
            actor = ev.pointer(0).i32(0)
        elif k == 3 and actor is None and ev.pointer(0).u32(0):
            c = replay.point(ev.pointer(0).pointer(0))
            nat[c[1] * w + c[0]].append(rnd)
    spawn = sorted(nat)
    wins = {}

    def win(c):
        v = wins.get(c)
        if v is None:
            y, x = divmod(c, w)
            v = tuple(((y + dy) % h) * w + (x + dx) % w for dy in range(-3, 4) for dx in range(-3, 4))
            wins[c] = v
        return v

    def timer(t, r):
        v = nat.get(t)
        if not v:
            return -1
        for s in v:
            if s > r:
                return s - r
        return 80

    def sdist(srcs):
        dist = [INF] * N
        qq = list(srcs)
        for t in qq:
            dist[t] = 0
        for t in qq:
            s = dist[t] + 1
            for nb in adj[t]:
                if dist[nb] == INF:
                    dist[nb] = s
                    qq.append(nb)
        return dist

    def near(dist, tiles):
        best = INF
        for t in tiles:
            if dist[t] < best:
                best = dist[t]
        return -1 if best == INF else best

    dspawn = sdist(spawn) if spawn else [INF] * N
    queens = {s: min(i for i in sd if sd[i] == s) for s in (0, 1)}
    starters = {i: ('q' if i == queens[sd[i]] else 'o') for i in sd}
    start_head = {i: bodies[i][0] for i in starters}
    start_len = {i: len(bodies[i]) for i in starters}
    d_start = {i: sdist([start_head[i]]) for i in starters}
    mem = {i: Mem(N, plain) for i in starters}
    rebuild = src in ('O', 'L')
    isq_cells = N > 600
    spawn_clear = arm in ('B7', 'B7Q')
    pocket_loop = arm in ('B7', 'B7Q')
    present = {}
    alive = [2, 2]
    eats = {i: [] for i in starters}
    side_eats = [[], []]
    side_splits = [[], []]
    marks = {}
    rnd, actor = 0, None
    cur = None

    def set_edge(m, t, d):
        k, dest = moves[t][d]
        if k == 0:
            m.kk[t][d] = 1
            m.ka[t][d] = dest
        elif k == 1:
            m.kk[t][d] = 2
            m.ka[t][d] = -1
        else:
            a, b = pair[(t, d)]
            m.kk[t][d] = 3
            m.ka[t][d] = dest if (m.sr[a] >= 0 or m.sr[b] >= 0) else -2

    def learn(m, t):
        for d in range(4):
            set_edge(m, t, d)
            set_edge(m, plain[t][d], d ^ 2)
        for t2, d2 in pwatch.get(t, ()):
            if m.kk[t2][d2] == 3:
                m.ka[t2][d2] = moves[t2][d2][1]

    def observe(m, head):
        sr, pe, tm, hot, low = m.sr, m.pe, m.tm, m.hot, m.low
        fresh = []
        for t in win(head):
            if sr[t] < 0:
                m.fs[t] = rnd
                fresh.append(t)
            sr[t] = rnd
            pe[t] = 1 if t in present else 0
            tv = timer(t, rnd)
            tm[t] = tv
            if 0 <= tv <= 4:
                g = rnd - low[t]
                if 6 <= g <= 25:
                    hot[t] = 1
                if g >= 6:
                    low[t] = rnd
            elif tv > 8:
                hot[t] = 0
        for t in fresh:
            learn(m, t)
        gap = cdist[head]
        if m.stall_best < 0 or gap < m.stall_best:
            m.stall_best = gap
            m.stall_round = rnd

    def options(i, b, m):
        head = b[0]
        L = len(b)
        sr, pe, tm, hot, ka, kk = m.sr, m.pe, m.tm, m.hot, m.ka, m.kk
        wn = set(win(head))
        enter = [0] * N
        mates, foes = [], []
        for jx, bb in bodies.items():
            if jx == i:
                continue
            vis = False
            for t in bb:
                if t in wn:
                    enter[t] = FOREVER
                    vis = True
            if bb[0] in wn:
                (mates if sd[jx] == 0 else foes).append(bb[0])
        for off, t in enumerate(b):
            if enter[t] < FOREVER:
                enter[t] = max(enter[t], L - off + 1)
        tail = b[-1]
        isq = starters[i] == 'q' and isq_cells
        scouting = L <= 6 and not isq

        def flood(heads):
            dist = [INF] * N
            qq = list(heads)
            for t in qq:
                dist[t] = 0
            for t in qq:
                s = dist[t] + 1
                for nb in ka[t]:
                    if nb >= 0 and dist[nb] == INF and enter[nb] == 0:
                        dist[nb] = s
                        qq.append(nb)
            return dist

        dpres = sdist(list(present)) if present else [INF] * N
        rival = flood(foes) if foes else None
        ally = flood(mates) if mates else None
        mate_adj = set()
        for mh in mates:
            for nb in ka[mh]:
                if nb >= 0:
                    mate_adj.add(nb)
        valuable = [t for t in range(N) if sr[t] >= 0 and (pe[t] or (tm[t] >= 0 and 1 <= tm[t] - (rnd - sr[t]) <= 8))]

        def gap(a, c):
            dx = abs(a % w - c % w)
            dy = abs(a // w - c // w)
            return min(dx, w - dx) + min(dy, h - dy)

        def cell_value(cell, t):
            if pe[cell]:
                found = 1.0
            elif sr[cell] >= 0 and tm[cell] >= 0 and 1 <= tm[cell] - (rnd - sr[cell]) <= t:
                found = 0.5
            else:
                return 0.0
            th = rival[cell] if rival else INF
            share = 1.0 if t < th else 0.5 if t == th else 0.0
            if ally and ally[cell] < t:
                share = 0.0
            return 80.0 * found * share * 0.85 ** (t - 1)

        look_cells = []

        def extend(cell, t, eaten):
            if t >= 8:
                return 0.0
            best = 0.0
            for d in range(4):
                if kk[cell][d] >= 2:
                    continue
                nx = plain[cell][d]
                fa = enter[nx]
                for kx, c in enumerate(look_cells):
                    if c == nx:
                        fa = max(fa, kx + 2 + L)
                if t + 1 - eaten < fa:
                    continue
                g = cell_value(nx, t + 1)
                look_cells.append(nx)
                g += extend(nx, t + 1, eaten + (1 if pe[nx] else 0))
                look_cells.pop()
                if g > best:
                    best = g
            return best

        def look(first):
            if not any(gap(first, v) <= 7 for v in valuable):
                return 0.0
            look_cells.append(first)
            g = cell_value(first, 1) + extend(first, 1, 1 if pe[first] else 0)
            look_cells.pop()
            return g

        def pocket(start):
            seen = {start}
            qq = [start]
            doors = []
            for t in qq:
                for d in range(4):
                    e = kk[t][d]
                    if e == 0:
                        return 48
                    if e != 1:
                        if pocket_loop and e == 3 and ka[t][d] >= 0:
                            doors.append((plain[t][d], ka[t][d]))
                        continue
                    nx = plain[t][d]
                    if nx in seen:
                        continue
                    if len(qq) >= 48:
                        return 48
                    seen.add(nx)
                    qq.append(nx)
            for a, e in doors:
                if a in seen and e not in seen:
                    return 48
            return len(qq)

        def known_room(start, limit):
            stp = {start: 1}
            eat = {start: pe[start]}
            qq = [start]
            qh = 0
            while qh < len(qq) and len(qq) < limit:
                t = qq[qh]
                qh += 1
                for d in range(4):
                    if kk[t][d] != 1:
                        continue
                    nx = plain[t][d]
                    if nx in stp or sr[nx] < 0:
                        continue
                    fa = enter[nx]
                    if fa >= FOREVER or stp[t] + 1 - eat[t] < fa:
                        continue
                    if nx == tail:
                        return limit
                    stp[nx] = stp[t] + 1
                    eat[nx] = eat[t] + pe[nx]
                    qq.append(nx)
            return min(len(qq), limit)

        def survey(start):
            stp = [0] * N
            eat = [0] * N
            stp[start] = 1
            eat[start] = pe[start]
            qq = [start]
            a_seen = a_un = 0
            o_seen = o_un = 0.0
            dp = ds = dh = du = dpo = dk = -1
            tailhit = 0
            for t in qq:
                s = stp[t]
                e = eat[t]
                th = rival[t] if rival else INF
                al = ally[t] if ally else INF
                share = 1.0 if s < th else 0.5 if s == th else 0.0
                if al < s:
                    share = 0.0
                if sr[t] < 0:
                    a_un += 1
                    o_un += share
                    if du < 0:
                        du = s
                else:
                    a_seen += 1
                    tv = tm[t]
                    if pe[t]:
                        o_seen += share
                        if dp < 0 and (share >= 1.0 or (L <= 4 and s <= th + 1 and al >= s)):
                            dp = s
                    elif tv < 0:
                        o_seen += share * 0.3
                    else:
                        o_seen += share * 80.0 / (80.0 + max(0, tv - (rnd - sr[t])))
                    if tv >= 0:
                        if dk < 0:
                            dk = s
                        sp = tv - (rnd - sr[t])
                        if share >= 1.0 and ds < 0 and sp <= s + 6:
                            ds = s + max(0, sp - s)
                    if hot[t] and dh < 0 and al >= s and s <= th + 1:
                        sp = 0 if pe[t] else tv - (rnd - sr[t])
                        dh = s + max(0, sp - s)
                if t == tail:
                    tailhit = 1
                kat = ka[t]
                for d in range(4):
                    nb = kat[d]
                    if nb < 0:
                        if nb == -2 and scouting and dpo < 0:
                            dpo = s + 1
                        continue
                    if stp[nb]:
                        continue
                    fa = enter[nb]
                    if fa >= FOREVER or s + 1 - e < fa:
                        continue
                    stp[nb] = s + 1
                    eat[nb] = e + pe[nb]
                    qq.append(nb)
            return [start, a_seen + 0.5 * a_un, round(o_seen + 0.5 * o_un, 2), tailhit, dp, ds, dh, du, dpo, dk]

        opts = []
        for d in range(4):
            k, tdest = moves[head][d]
            if k == 1:
                opts.append(None)
                continue
            pk = 0
            if k == 2:
                ex = ka[head][d]
                if isq:
                    opts.append(None)
                    continue
                if ex < 0:
                    opts.append([-1, 2] if scouting else None)
                    continue
                dest = ex
                pk = 1
            else:
                dest = tdest
            if enter[dest] > 1:
                opts.append(None)
                continue
            o = survey(dest)
            sc = 0
            if spawn_clear and not pe[dest] and tm[dest] >= 0 and sr[dest] >= 0:
                sp = tm[dest] - (rnd - sr[dest])
                if 0 <= sp <= min(L, 4):
                    sc = 1
            kr = 0
            if isq:
                kr = max(0, L + 2 - known_room(dest, L + 2))
            o += [1 if pe[dest] else 0, sc, pocket(dest), round(look(dest), 1) if pk == 0 else 0.0,
                  1 if dest in mate_adj else 0, cdist[dest], pk, kr, dspawn[dest], dpres[dest]]
            opts.append(o)
        return opts, len(mates), len(foes), 1 if isq else 0

    def close():
        if cur is not None:
            out.append(json.dumps(cur, separators=(',', ':')))

    def snapshot(r):
        marks[r] = [alive[0], alive[1], len(side_eats[0]), len(side_eats[1]),
                    sum(len(bb) for jx, bb in bodies.items() if sd[jx] == 0), sum(len(bb) for jx, bb in bodies.items() if sd[jx] == 1)]

    sim = {}
    if rebuild:
        me = next(i for i in starters if starters[i] == 'o' and sd[i] == 0)
        b0 = list(bodies[me])
        face = next((d for d in range(4) if moves[b0[1]][d][0] != 1 and moves[b0[1]][d][1] == b0[0]), -1)
        for v in VARIANTS:
            sim[v] = dict(body=deque(b0), mem=Mem(N, plain), eaten=set(), dir=face, path='', eats=[], portal=[], dead=-1, splits=[], cds=[])

    def simulate(actor):
        for v in VARIANTS:
            st = sim[v]
            if st['dead'] >= 0:
                continue
            vb = st['body']
            hidden = [(t, present.pop(t)) for t in list(st['eaten']) if t in present]
            vm = st['mem']
            observe(vm, vb[0])
            L = len(vb)
            if L >= 4:
                keep = list(vb)[:L - 2]
                st['body'] = deque(keep)
                st['splits'].append(rnd)
                st['path'] += '*'
                for t, val in hidden:
                    present[t] = val
                continue
            opts, nmv, nev, isq = options(actor, vb, vm)
            row = dict(L=L, r=rnd, i=actor, ro='o', isq=isq, cm=1 if center_map else 0, cr=center_rounds, mg=center_margin,
                       ne=nev, nm=nmv, st=rnd - vm.stall_round, al=alive[0], cd=cdist[vb[0]], o=opts)
            sc, ps = scores(row, src == 'O', centre=('nocentre' not in v), variant=('units2' if 'units2' in v else None))
            if v.startswith('head') and st['dir'] >= 0 and sc[st['dir']] is not None:
                # head1 / head6: bonus 1.5 / 6; headalone: only with no team mate's head in view; head20: rounds 0-19 only;
                # headblind: only when no step on offer has a pearl or hot bonus
                hb = 1.5 if v == 'head1' else 6.0 if v == 'head6' else HEAD_BONUS
                blind = all(p is None or 'blind' in p or (p['pearl'] <= 0 and p['hot'] <= 0 and p['eat'] <= 0) for p in ps)
                if (v != 'headalone' or nmv == 0) and (v != 'head20' or rnd < 20) and (v != 'headblind' or blind):
                    sc[st['dir']] += hb
            d = best(sc)
            for t, val in hidden:
                present[t] = val
            if d < 0:
                st['dead'] = rnd
                st['path'] += 'x'
                continue
            kind, dest = moves[vb[0]][d]
            if kind == 1 or any(dest in bb for jx, bb in bodies.items() if jx != actor) or dest in list(vb)[:-1]:
                st['dead'] = rnd
                st['path'] += 'X'
                continue
            st['path'] += 'NESW'[d].lower() if kind == 2 else 'NESW'[d]
            if kind == 2:
                st['portal'].append(rnd)
            st['dir'] = d
            vb.appendleft(dest)
            if dest in present and dest not in st['eaten']:
                st['eaten'].add(dest)
                st['eats'].append(rnd)
            else:
                vb.pop()
            st['cds'].append(cdist[dest])

    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            cur = None
            if rnd in (10, 20, 30, 40, 60):
                snapshot(rnd)
            rnd, actor = p.i32(0), None
            if rnd > LAST + 1:
                break
        elif k == 1:
            close()
            cur = None
            actor = p.i32(0)
            b = bodies.get(actor)
            if b is None or actor not in starters:
                continue
            m = mem[actor]
            head = b[0]
            observe(m, head)
            if rebuild and actor == me and rnd <= SIMLAST:
                simulate(actor)
            if rnd > LAST:
                continue
            s = sd[actor]
            wn = win(head)
            pv = [t for t in wn if t in present]
            dist = sdist([head])
            unseen = [t for t in range(N) if m.sr[t] < 0]
            known = [t for t in range(N) if m.pe[t]]
            kspawn = [t for t in range(N) if m.sr[t] >= 0 and t in nat]
            wset = set(wn)
            ne = sum(1 for jx, bb in bodies.items() if sd[jx] != s and bb[0] in wset)
            nm = sum(1 for jx, bb in bodies.items() if sd[jx] == s and jx != actor and bb[0] in wset)
            cur = dict(k='t', g=gi, i=actor, ro=starters[actor], s=s, r=rnd, L=len(b), h=head, cd=cdist[head],
                       al=alive[s], op=alive[1 - s], np=len(pv), nb=len(present), ne=ne, nm=nm,
                       dpv=near(dist, pv), dpk=near(dist, known), dpa=near(dist, present), du=near(dist, unseen),
                       dsp=near(dist, spawn), dks=near(dist, kspawn), ds0=d_start[actor][head],
                       st=rnd - m.stall_round, act='n', nh=-1, ns=0, ate=0)
            cur['_sets'] = (pv, known, list(present), unseen, kspawn)
            if pv:
                tgt = min(pv, key=lambda t: dist[t])
                dt = sdist([tgt])
                dm, mq, df = INF, 0, INF
                for jx, bb in bodies.items():
                    if jx == actor:
                        continue
                    v = dt[bb[0]]
                    if sd[jx] == s:
                        if v < dm:
                            dm, mq = v, 1 if jx == queens[s] else 0
                    elif v < df:
                        df = v
                cur.update(dm=-1 if dm == INF else dm, mq=mq, df=-1 if df == INF else df, tg=tgt)
            if rebuild and s == 0:
                opts, nmv, nev, isq = options(actor, b, m)
                cur.update(o=opts, isq=isq, cm=1 if center_map else 0, cr=center_rounds, mg=center_margin)
            sets = cur.pop('_sets')
            cur_sets = sets
        elif k == 3:
            c = replay.point(p.pointer(0))
            t = c[1] * w + c[0]
            if p.u32(0):
                present[t] = (rnd, actor is None)
            else:
                born = present.pop(t)
                s = sd[actor]
                side_eats[s].append(rnd)
                if actor in starters:
                    m = mem[actor]
                    eats[actor].append([rnd, t, 1 if born[1] else 0, born[0], cdist[t], d_start[actor][t], walls[t],
                                        min(d_start[jx][t] for jx in starters if sd[jx] != s),
                                        min(d_start[jx][t] for jx in starters if sd[jx] == s), m.fs[t]])
                    if cur is not None:
                        cur['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                if cur is not None and i == actor:
                    cur['ns'] += 1
                    if cur['ns'] == 1:
                        old = b[0]
                        cur['act'] = 'm'
                        cur['nh'] = hd
                        cur['dir'] = next((d for d in range(4) if moves[old][d][0] != 1 and moves[old][d][1] == hd), -1)
                        dist = sdist([hd])
                        pv, known, pres, unseen, kspawn = cur_sets
                        cur.update(cd2=cdist[hd], dpv2=near(dist, pv), dpk2=near(dist, known), dpa2=near(dist, pres),
                                   du2=near(dist, unseen), dsp2=near(dist, spawn), dks2=near(dist, kspawn))
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            sd[c] = sd[a]
            alive[sd[a]] += 1
            side_splits[sd[a]].append(rnd)
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
            if cur is not None and a == actor:
                cur['act'] = 's'
        elif k == 11:
            i = p.i32(0)
            if cur is not None and i == actor:
                cur['died'] = p.u16(4)
            alive[sd[i]] -= 1
            bodies.pop(i)
    close()
    for r in (10, 20, 30, 40, 60):
        if r not in marks:
            snapshot(r)
    won = (j.get('winner') == 'a') == (own == 0) if j.get('winner') in ('a', 'b') else None
    return dict(k='g', g=gi, gid=j['id'], src=src, arm=arm, label=label, map=j['mapName'], w=w, h=h, own=own,
                opp=j['teamBName'] if own == 0 else j['teamAName'], rating=j.get('opponent_rating'), won=won, cm=1 if center_map else 0, cr=center_rounds,
                starters={str(i): [starters[i], sd[i], start_head[i], start_len[i], cdist[start_head[i]]] for i in starters},
                spawn=spawn, nat0=sum(1 for t in nat if nat[t][0] == 0), eats={str(i): v for i, v in eats.items()},
                sim={v: dict(path=s['path'], eats=s['eats'], portal=s['portal'], dead=s['dead'], splits=s['splits'], cd20=(s['cds'][19] if len(s['cds']) > 19 else -1)) for v, s in sim.items()},
                me=(me if rebuild else -1), side_eats=[v[:12] for v in side_eats], side_splits=[v[:6] for v in side_splits], marks=marks, rounds=rnd)


def save(tag, body):
    if tag == 'O0':
        Path(OUT + 'o2_sim-O0.jsonl').write_text(body)
    elif tag == 'L0':
        Path(OUT + 'o2_sim-L0.jsonl').write_text(body)
    elif tag == 'L1':
        Path(OUT + 'o2_sim-L1.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'o2_sim-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'o2_sim-R1.jsonl').write_text(body)
    else:
        Path(OUT + 'o2_sim-test.jsonl').write_text(body)


def main():
    src, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    todo = [(n, x) for n, x in enumerate(jobs(src)) if n % shards == shard]
    if limit:
        todo = todo[::max(1, len(todo) // limit)][:limit]
    out, bad = [], []
    for z, (n, (rp, j, team, arm, label)) in enumerate(todo):
        rows = []
        try:
            g = scan(rp, j, team, arm, label, n, src, rows)
        except Exception as e:
            bad.append((j['id'], repr(e)[:300]))
            continue
        if g is None:
            continue
        out.append(json.dumps(g, separators=(',', ':')))
        print(z + 1, len(todo), j['id'], j['mapName'], arm, len(rows), 'bad', len(bad), flush=True)
    save('test' if limit else src + str(shard), '\n'.join(out) + '\n')
    print('done', src, shard, len(todo), 'bad', bad)


main()
