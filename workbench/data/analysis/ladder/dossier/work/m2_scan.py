"""Scratch (diag-med20): rounds 0-20 turn by turn on layouts of 701-1200 cells, both sides of every game.
Rows: k='g' one per game (marks per round 0-40, starters, natural births), k='t' one per dragon turn of rounds 0-20 (what is in
its 7 by 7, what it does, distances before and after the first step), k='p' one per pearl eaten in rounds 0-40.
Side 0 = the studied team (the index team, or ours), side 1 = the other. For ours side 0 also carries the rebuilt
score_step inputs of every step on offer (o2_scan.py's rebuild of agg8-bot/main.cpp 5039-5248, now for children too).
Countdowns are not in replays: a tile's countdown is taken as rounds to its next natural pearl in that game.
Distances are path steps on the empty map (kelp shut, portals open).
Usage: python3 data/analysis/ladder/dossier/work/m2_scan.py <T3|O|T1> <shard> <shards> [limit]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import defaultdict, deque
from pathlib import Path

D = '개인 프로젝트'
OUT = '~/01. Project/' + D + '/unsw-swarm/data/analysis/ladder/dossier/work/'
ARMS = (('agg7-m1-new', 'MAIN'), ('agg7-m2-new', 'MAIN'), ('agg7-m3-new', 'MAIN'), ('agg7-b1-new', 'B7'), ('agg7-b2-new', 'B7'),
        ('agg8-q1-new', 'B7Q'), ('agg8-q2-new', 'B7Q'))
MED = ('Queen Of Spades', 'Default', 'Maze', 'Trauma')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LAST = 40
PLAST = 40
INF = 1 << 28
FOREVER = 1 << 20


TERMS = ('centre', 'room', 'terr', 'cramped', 'pearl', 'soon', 'hot', 'unseen', 'portal', 'far', 'eat', 'look', 'mate', 'pocket', 'sc', 'queen')
VARIANTS = ('base', 'head', 'head3', 'headblind', 'head20')
SIMLAST = 40
SIMBORN = 5


def tb(d, wt):
    return 0.0 if d < 0 else max(0.0, wt * (260 - 40 * d))


def parts(row, o, k):
    dest, room, terr, tailhit, dp, ds, dh, du, dpo, dk, eat, sc, pocket, look, mate, cd, pk, kr, dsa, dpa = o
    L, r = row['L'], row['r']
    cr = 0.0
    want = 3.0 * L + 8.0
    if room < want:
        cr += 400.0 * (want - room)
    if room < L + 2.0:
        cr += 5000.0 * (L + 2.0 - room)
    if not tailhit:
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
    if mate:
        t['mate'] = -450.0
    t['look'] = look
    if pk == 1:
        t['portal'] -= 150.0
    t['tie'] = 0.25 * ((row['i'] * 31 + r * 17 + k * 7) % 5)
    return t


def scores(row):
    out, ps = [None] * 4, [None] * 4
    base = None
    blind = []
    for k, o in enumerate(row['o']):
        if o is None:
            continue
        if len(o) == 2:
            blind.append(k)
            continue
        t = parts(row, o, k)
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

    def add(folder, team, arm, label):
        folder = Path(folder)
        if not folder.is_dir():
            return
        for mp in sorted(folder.glob('game-*.json')):
            try:
                j = json.loads(mp.read_text())
            except Exception:
                continue
            if j.get('mapName') not in MED or team not in (j.get('teamAId'), j.get('teamBId')):
                continue
            rp = folder / ('M%d.replay' % j['id'])
            if rp.exists():
                out.append((rp, j, team, arm, label))

    if src == 'O':
        for label, arm in ARMS:
            add(Path('data/online/smoke') / label, 1119, arm, label)
        for f in sorted(Path('data/online/smoke').glob('top-l*')):
            if f.is_dir():
                add(f, 1119, 'B7Q', f.name)
    elif src == 'T3':
        for line in Path('data/online/top3/index.jsonl').read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                add('data/online/top3/%d' % r['battle'], r['team'], 'T%d' % r['team'], 'top3')
    elif src == 'T1':
        for line in Path('data/top1/index.jsonl').read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r['team'] in (306, 91, 264, 842, 454):
                    add('data/online/top1/%d' % r['battle'], r['team'], 'T%d' % r['team'], 'top1')
    seen, uniq = set(), []
    for x in out:
        if x[1]['id'] not in seen:
            seen.add(x[1]['id'])
            uniq.append(x)
    return uniq


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
    if not 700 < N <= 1200:
        return None
    own = 0 if j['teamAId'] == team else 1
    sd = {i: 0 if teams[i] == own else 1 for i in bodies}
    moves, pair = build(w, h, raw)
    plain = [[((t // w + dy) % h) * w + (t % w + dx) % w for dx, dy in STEP] for t in range(N)]
    adj = [[t2 for k, t2 in row if k != 1] for row in moves]
    walls = [sum(1 for k, t2 in row if k == 1) for row in moves]
    mouths = sorted({t for (t, d) in pair})
    mouthset = set(mouths)
    pwatch = defaultdict(list)
    for (t, d), (a, b) in pair.items():
        pwatch[a].append((t, d))
        pwatch[b].append((t, d))
    cx, cy = w // 2, h // 2
    cdist = [min(abs(t % w - cx), w - abs(t % w - cx)) + min(abs(t // w - cy), h - abs(t // w - cy)) for t in range(N)]
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
    last_round = rnd
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

    queens = {s: min(i for i in sd if sd[i] == s) for s in (0, 1)}
    info = {i: dict(s=sd[i], ro='q' if i == queens[sd[i]] else 'o', born=0, par=-1, gen=0, root=i, pc=0, sh=bodies[i][0], L0=len(bodies[i])) for i in sd}
    starters = sorted(info)
    start_head = {i: bodies[i][0] for i in starters}
    d_start = {i: sdist([start_head[i]]) for i in starters}
    side_starts = {s: [start_head[i] for i in starters if sd[i] == s] for s in (0, 1)}
    d_side = {s: sdist(side_starts[s]) for s in (0, 1)}

    def facing(b):
        if len(b) < 2:
            return -1
        return next((d for d in range(4) if moves[b[1]][d][0] != 1 and moves[b[1]][d][1] == b[0]), -1)

    face0 = {i: facing(bodies[i]) for i in starters}
    mem = {i: Mem(N, plain) for i in starters}
    rebuild = team == 1119
    isq_cells = N > 600
    spawn_clear = arm in ('B7', 'B7Q')
    pocket_loop = arm in ('B7', 'B7Q')
    present = {}
    alive = [sum(1 for i in sd if sd[i] == s) for s in (0, 1)]
    tseen = [set(), set()]
    cnt = dict(eat=[0, 0], nat=[0, 0], split=[0, 0], death=[0, 0], pseen=[0, 0], dt=[0, 0], pstep=[0, 0], two=[0, 0], eat2=[0, 0], paid=[0, 0])
    marks = {}
    births = []
    splits = []
    rnd, actor = 0, None
    tstep = 0
    cur = None
    cur_sets = None
    pid_next = 0

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
        return len(fresh)

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
            for t in bb:
                if t in wn:
                    enter[t] = FOREVER
            if bb[0] in wn:
                (mates if sd[jx] == 0 else foes).append(bb[0])
        for off, t in enumerate(b):
            if enter[t] < FOREVER:
                enter[t] = max(enter[t], L - off + 1)
        tail = b[-1]
        isq = info[i]['ro'] == 'q' and isq_cells
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
                  1 if dest in mate_adj else 0, cdist[dest], pk, kr, 0, dpres[dest]]
            opts.append(o)
        return opts, 1 if isq else 0

    def close():
        if cur is not None:
            out.append(json.dumps(cur, separators=(',', ':')))

    def snapshot(r):
        marks[r] = [[alive[s], sum(len(bb) for jx, bb in bodies.items() if sd[jx] == s), cnt['eat'][s], cnt['nat'][s], cnt['split'][s],
                     cnt['death'][s], len(tseen[s]), cnt['pseen'][s], cnt['dt'][s], cnt['pstep'][s], cnt['two'][s], cnt['eat2'][s], cnt['paid'][s],
                     len(bodies[queens[s]]) if queens[s] in bodies else 0] for s in (0, 1)]

    sim = {}

    def simulate(actor):
        for v in VARIANTS:
            st = sim[actor][v]
            if st['dead'] >= 0:
                continue
            st['last'] = rnd
            vb = st['body']
            hidden = [(t, present.pop(t)) for t in list(st['eaten']) if t in present]
            vm = st['mem']
            observe(vm, vb[0])
            L = len(vb)
            if L >= (5 if (info[actor]['ro'] == 'q' and arm == 'B7Q') else 4) and rnd >= 1:
                st['body'] = deque(list(vb)[:L - 2])
                st['splits'].append(rnd)
                st['path'] += '*'
                for t, val in hidden:
                    present[t] = val
                continue
            opts, isq = options(actor, vb, vm)
            row = dict(L=L, r=rnd, i=actor, isq=isq, o=opts)
            sc, ps = scores(row)
            if v != 'base' and st['dir'] >= 0 and sc[st['dir']] is not None and L <= 4:
                blind = all(q is None or 'blind' in q or (q['pearl'] <= 0 and q['hot'] <= 0 and q['eat'] <= 0) for q in ps)
                if (v != 'head20' or rnd < 20) and (v != 'headblind' or blind):
                    sc[st['dir']] += 3.0 if v == 'head3' else 1.5
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

    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            cur = None
            new = p.i32(0)
            if new != rnd or new == 0:
                if new > 0 and rnd <= PLAST:
                    snapshot(rnd)
            rnd, actor = new, None
            if rnd > PLAST + 1:
                break
        elif k == 1:
            close()
            cur = None
            actor = p.i32(0)
            tstep = 0
            b = bodies.get(actor)
            if b is None:
                continue
            m = mem[actor]
            head = b[0]
            fresh = observe(m, head)
            if rebuild and sd[actor] == 0 and rnd <= SIMLAST:
                if actor not in sim and info[actor]['born'] <= SIMBORN and info[actor].get('turns', 0) == 0:
                    sim[actor] = {v: dict(body=deque(b), mem=Mem(N, plain), eaten=set(), dir=facing(b), path='', eats=[], portal=[], dead=-1, splits=[], last=-1) for v in VARIANTS}
                if actor in sim:
                    simulate(actor)
            info[actor]['turns'] = info[actor].get('turns', 0) + 1
            if rnd > PLAST:
                continue
            s = sd[actor]
            f = info[actor]
            wn = win(head)
            ts = tseen[s]
            tnew = 0
            for t in wn:
                if t not in ts:
                    ts.add(t)
                    tnew += 1
            pv = []
            for t in wn:
                pr = present.get(t)
                if pr is not None:
                    pv.append(t)
                    if pr['ss'][s] < 0:
                        pr['ss'][s] = rnd
                        cnt['pseen'][s] += 1
                    if actor not in pr['ds']:
                        pr['ds'][actor] = rnd
            cnt['dt'][s] += 1
            if rnd > LAST:
                continue
            dist = sdist([head])
            unseen = [t for t in range(N) if m.sr[t] < 0]
            tunseen = [t for t in range(N) if t not in ts]
            soon = [t for t in wn if t not in present and 0 < timer(t, rnd) <= 8]
            soon10 = [t for t in spawn if t not in present and 0 < timer(t, rnd) <= 10]
            wset = set(wn)
            mh = [bb[0] for jx, bb in bodies.items() if sd[jx] == s and jx != actor]
            ne = sum(1 for jx, bb in bodies.items() if sd[jx] != s and bb[0] in wset)
            nm = sum(1 for t in mh if t in wset)
            wm = [t for t in wn if t in mouthset]
            occ = set()
            for bb in bodies.values():
                occ.update(bb)
            free = sum(1 for kd, t2 in moves[head] if kd != 1 and t2 not in occ)
            tsoon = min(soon, key=lambda t: dist[t]) if soon else -1
            cur = dict(k='t', g=gi, i=actor, s=s, r=rnd, L=len(b), h=head, ro=f['ro'] if f['gen'] == 0 else 'c', gen=f['gen'], born=f['born'],
                       root=f['root'], al=alive[s], fc=facing(b), fr=free, fresh=fresh, tnew=tnew,
                       np=len(pv), dpv=near(dist, pv), nso=len(soon), dso=near(dist, soon), cso=timer(tsoon, rnd) if tsoon >= 0 else -1,
                       nsp=sum(1 for t in wn if t in nat), nmo=len(wm), dmo=near(dist, wm),
                       du=near(dist, unseen), dut=near(dist, tunseen), dpa=near(dist, present), dsp=near(dist, spawn), dsn=near(dist, soon10),
                       dma=near(dist, mouths), cd=cdist[head], des=d_side[1 - s][head], ds0=d_start[f['root']][head], dmh=near(dist, mh),
                       ne=ne, nm=nm, st=rnd - m.stall_round, act='n', nh=-1, ns=0, ate=0, ps=0)
            cur_sets = (pv, unseen, tunseen, list(present), soon10, mh, soon)
            if rebuild and s == 0:
                opts, isq = options(actor, b, m)
                cur.update(o=opts, isq=isq)
        elif k == 4:
            a = p.pointer(0)
            if cur is not None and a and a.u16(0) == 0 and a.pointer(0) is not None:
                cur['dirs'] = list(a.pointer(0))
        elif k == 3:
            c = replay.point(p.pointer(0))
            t = c[1] * w + c[0]
            if p.u32(0):
                present[t] = dict(born=rnd, nat=actor is None, ss=[-1, -1], ds={}, v0=[0, 0])
                if actor is None and rnd <= PLAST:
                    births.append([rnd, t, d_side[0][t], d_side[1][t]])
                if rnd == 0 and actor is None:
                    for s in (0, 1):
                        if any(t in win(hh) for hh in side_starts[s]):
                            present[t]['v0'][s] = 1
            else:
                pr = present.pop(t)
                s = sd[actor]
                f = info[actor]
                cnt['eat'][s] += 1
                cnt['nat'][s] += 1 if pr['nat'] else 0
                step = tstep + 1
                if step >= 2:
                    cnt['eat2'][s] += 1
                if cur is not None:
                    cur['ate'] += 1
                    if cur['ate'] == 1:
                        cur['as'] = step
                if rnd <= PLAST:
                    b = bodies[actor]
                    if pr['ss'][s] < 0:
                        pr['ss'][s] = rnd
                        cnt['pseen'][s] += 1
                    y, x = divmod(t, w)
                    cl = sum(1 for dy in range(-2, 3) for dx in range(-2, 3) if (((y + dy) % h) * w + (x + dx) % w) in nat)
                    out.append(json.dumps(dict(k='p', g=gi, s=s, r=rnd, t=t, nat=1 if pr['nat'] else 0, born=pr['born'], i=actor,
                                               ro=f['ro'] if f['gen'] == 0 else 'c', gen=f['gen'], db=f['born'], root=f['root'], step=step, L=len(b),
                                               fsd=pr['ds'].get(actor, rnd), fss=pr['ss'][s], v0=pr['v0'][s], down=d_side[s][t], droot=d_start[f['root']][t],
                                               den=d_side[1 - s][t], cdt=cdist[t], cds=cdist[start_head[f['root']]], wall=walls[t], pc=f['pc'],
                                               cl=cl, nb=len(nat.get(t, ()))), separators=(',', ':')))
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                if i == actor:
                    tstep += 1
                    if tstep == 2:
                        cnt['two'][sd[i]] += 1
                        if 2 > (len(b) + 3) // 4:
                            cnt['paid'][sd[i]] += 1
                    old = b[0]
                    dr = next((d for d in range(4) if moves[old][d][0] != 1 and moves[old][d][1] == hd), -1)
                    port = dr >= 0 and moves[old][dr][0] == 2
                    if port:
                        cnt['pstep'][sd[i]] += 1
                        info[i]['pc'] += 1
                    if cur is not None:
                        cur['ns'] += 1
                        if port:
                            cur['ps'] += 1
                        if cur['ns'] == 2:
                            cur['nh2'] = hd
                        if cur['ns'] == 1:
                            cur['act'] = 'm'
                            cur['nh'] = hd
                            cur['dir'] = dr
                            dist = sdist([hd])
                            pv, unseen, tunseen, pres, soon10, mh, soon = cur_sets
                            cur.update(dpv2=near(dist, pv), du2=near(dist, unseen), dut2=near(dist, tunseen), dpa2=near(dist, pres),
                                       dsp2=near(dist, spawn), dsn2=near(dist, soon10), dma2=near(dist, mouths), cd2=cdist[hd],
                                       des2=d_side[1 - sd[i]][hd], ds02=d_start[info[i]['root']][hd], dmh2=near(dist, mh), dso2=near(dist, soon))
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            sd[c] = sd[a]
            alive[sd[a]] += 1
            cnt['split'][sd[a]] += 1
            before = len(bodies[a])
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
            fa = info[a]
            info[c] = dict(s=sd[a], ro='c', born=rnd, par=a, gen=fa['gen'] + 1, root=fa['root'], pc=fa['pc'], sh=bodies[c][0], L0=len(bodies[c]))
            mem[c] = Mem(N, plain)
            if rnd <= PLAST:
                splits.append([rnd, sd[a], a, c, before, len(bodies[c]), fa['ro'] if fa['gen'] == 0 else 'c', cur['np'] if (cur is not None and a == actor) else -1])
            if cur is not None and a == actor:
                cur['act'] = 's'
                cur['child'] = c
        elif k == 11:
            i = p.i32(0)
            if cur is not None and i == actor:
                cur['died'] = p.u16(4)
            alive[sd[i]] -= 1
            cnt['death'][sd[i]] += 1
            bodies.pop(i)
    close()
    for r in range(0, PLAST + 1):
        if r not in marks and r >= rnd:
            snapshot(r)
    dsp = sdist(spawn) if spawn else [INF] * N
    dmo = sdist(mouths) if mouths else [INF] * N
    won = (j.get('winner') == 'a') == (own == 0) if j.get('winner') in ('a', 'b') else None
    names = (j.get('teamAName'), j.get('teamBName'))
    ids = (j.get('teamAId'), j.get('teamBId'))
    elos = (j.get('teamAElo'), j.get('teamBElo'))
    return dict(k='g', g=gi, gid=j['id'], src=src, arm=arm, label=label, map=j['mapName'], w=w, h=h, own=own, team=team,
                name=names[own], opp=names[1 - own], oppid=ids[1 - own], elo=elos[own], oppelo=elos[1 - own], won=won,
                starters={str(i): [info[i]['ro'], sd[i], start_head[i], info[i]['L0'], face0[i], dsp[start_head[i]], dmo[start_head[i]]] for i in starters},
                nspawn=len(spawn), nat0=sum(1 for t in nat if nat[t][0] == 0), births=births, splits=splits, marks=marks, rounds=last_round,
                mouths=mouths, sim={str(i): dict(born=info[i]['born'], ro=info[i]['ro'], root=info[i]['root'],
                                                 v={v: dict(path=s['path'], eats=s['eats'], portal=s['portal'], dead=s['dead'], splits=s['splits'], last=s['last']) for v, s in sv.items()})
                                    for i, sv in sim.items()})


def save(tag, body):
    if tag == 'T30':
        Path(OUT + 'm2_scan-T3.jsonl').write_text(body)
    elif tag == 'O0':
        Path(OUT + 'm2_scan-O.jsonl').write_text(body)
    elif tag == 'T10':
        Path(OUT + 'm2_scan-T1-0.jsonl').write_text(body)
    elif tag == 'T11':
        Path(OUT + 'm2_scan-T1-1.jsonl').write_text(body)
    else:
        Path(OUT + 'm2_scan-test.jsonl').write_text(body)


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
        out.extend(rows)
        if z % 10 == 9:
            print(z + 1, len(todo), j['id'], j['mapName'], arm, len(rows), 'bad', len(bad), flush=True)
    save('test' if limit else src + str(shard), '\n'.join(out) + '\n')
    print('done', src, shard, len(todo), 'bad', bad)


main()
