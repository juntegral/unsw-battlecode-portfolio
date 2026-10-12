#!/usr/bin/env python3
"""Verifier extraction 5b: large layouts only, with what stands on the pearl tile at the birth (field 20) and at the
start of the nearer dragon's turn (field 21): 0 nothing, 1 the nearer dragon's own body, 2 a team mate, 3 an enemy.
Otherwise extraction 5 (run of 2026-10-07 06:27 KST) for the queue F25 (share of total length after round 100),
F26 (natural pearls born nearer to one side), F24 (reach on our queen and paid sprints, by rating), F28 (queen comes
closer to a short enemy head at 3 or 4 steps). Own state rebuild from the raw replays; only the byte decoder
(battlecode/replay.py) is shared. One JSON line per game. Usage: python3 extract5.py <shard> <shards>"""
import sys, json, hashlib
from pathlib import Path
from collections import deque, Counter
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path('../battlecode').resolve()))
import replay

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
MAIN = ('18066', '18068', '18504', '18570')
OLD = ('17790',)
US = 1119
LADDER = Path('data/online/ladder')
MARKS = (50, 100, 150, 200, 250, 300, 400)
FAR = 99


def north_edge(W, x, y):
    return 2 * y * (W + 1) + x


def west_edge(W, x, y):
    return (2 * y + 1) * (W + 1) + x


def edge_of(W, H, x, y, d):
    if d == 0:
        return north_edge(W, x, y)
    if d == 2:
        return north_edge(W, x, (y + 1) % H)
    if d == 3:
        return west_edge(W, x, y)
    return west_edge(W, (x + 1) % W, y)


def fold(W, H, e):
    row, x = divmod(e, W + 1)
    if row % 2 == 0:
        if x == W:
            return None
        return north_edge(W, x, (row // 2) % H)
    return west_edge(W, x % W, row // 2)


def read_layout(text):
    lines = text.splitlines()
    W, H = int(lines[0].split()[1]), int(lines[0].split()[2])
    dragons = []
    edges = {}
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'DRAGON':
            n = int(q[2])
            dragons.append((int(q[1]), [(int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(n)]))
        elif q[0] == 'EDGE':
            e, kind, pid = int(q[1]), int(q[2]), int(q[3])
            c = fold(W, H, e)
            if c is None:
                continue
            if c in edges and kind <= edges[c][0]:
                continue
            edges[c] = (kind, pid)
    return W, H, dragons, edges


def build_graph(W, H, edges):
    """nbr[u] = tiles one step from u over open and portal edges (kelp closed, wrap applied); nbd[u][d] the same
    by direction (None = kelp)."""
    pairs = {}
    for e, (kind, pid) in edges.items():
        if kind == 2:
            pairs.setdefault(pid, []).append(e)
    bad = sum(1 for v in pairs.values() if len(v) != 2)
    N = W * H
    nbr = [[] for _ in range(N)]
    nbd = [[None, None, None, None] for _ in range(N)]
    for y in range(H):
        for x in range(W):
            u = y * W + x
            for d in range(4):
                e = edge_of(W, H, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    continue
                if kind == 2:
                    pr = pairs.get(pid, [])
                    if len(pr) != 2:
                        continue
                    pe = pr[0] if pr[1] == e else pr[1]
                    row, px = divmod(pe, W + 1)
                    if row % 2 != (0 if d in (0, 2) else 1):
                        bad += 1
                        continue
                    py = row // 2
                    if d == 0:
                        v = ((py - 1) % H) * W + px
                    elif d == 3:
                        v = py * W + (px - 1) % W
                    else:
                        v = py * W + px
                else:
                    if d == 0:
                        v = ((y - 1) % H) * W + x
                    elif d == 1:
                        v = y * W + (x + 1) % W
                    elif d == 2:
                        v = ((y + 1) % H) * W + x
                    else:
                        v = y * W + (x - 1) % W
                nbd[u][d] = v
                if v not in nbr[u]:
                    nbr[u].append(v)
    return nbr, nbd, bad, len(pairs)


def window(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


def process(path, meta, battle):
    root = replay.load(path).root()
    bots = (root.text(1), root.text(2))
    if meta['teamAId'] == US:
        ours = 0
    elif meta['teamBId'] == US:
        ours = 1
    else:
        raise ValueError('team 1119 is on neither side')
    W, H, dragons, edges = read_layout(root.text(0))
    open_tiles = 0
    for x in range(W):
        for y in range(H):
            if any(edges.get(edge_of(W, H, x, y, d), (0, -1))[0] != 1 for d in range(4)):
                open_tiles += 1
    sig_src = json.dumps([W, H, sorted((e, k, p) for e, (k, p) in edges.items() if k), sorted(c for t, c in dragons)])
    code = 'main' if bots[ours] in MAIN else 'v31' if bots[ours] in OLD else 'other'
    rec = dict(game=meta['id'], battle=battle, map=meta['mapName'], our_side='AB'[ours], bot=bots[ours],
               code=code, completedAt=meta['completedAt'], W=W, H=H, open_tiles=open_tiles,
               layout=hashlib.sha1(sig_src.encode()).hexdigest()[:12])
    res = root.pointer(4)
    winner = res.u16(6) if res.u16(4) == 1 else None
    rec.update(end_reason=res.u16(2), win=winner == ours, drawn=winner is None)
    if code == 'other' or open_tiles < 2000:
        rec['skip'] = True
        return rec
    nbr, nbd, bad_portals, n_portals = build_graph(W, H, edges)

    bodies = {}
    team = {}
    for i, (t, cells) in enumerate(dragons):
        bodies[i] = deque(cells)
        team[i] = 0 if t == ours else 1
    queen = [min(i for i in team if team[i] == 0), min(i for i in team if team[i] == 1)]
    qside = {queen[0]: 0, queen[1]: 1}

    def bfs(src, cap):
        dist = {src: 0}
        frontier = [src]
        d = 0
        while frontier and d < cap:
            d += 1
            nxt = []
            for u in frontier:
                for v in nbr[u]:
                    if v not in dist:
                        dist[v] = d
                        nxt.append(v)
            frontier = nxt
        return dist

    def occ_code(ci, ni):
        cx = ci % W
        cy = ci // W
        for z, bb in bodies.items():
            for seg in bb:
                if seg[0] == cx and seg[1] == cy:
                    return 1 if z == ni else 2 if team[z] == team[ni] else 3
        return 0

    def totals():
        out = []
        for s in (0, 1):
            ls = [len(b) for i, b in bodies.items() if team[i] == s]
            qb = bodies.get(queen[s])
            out.append([len(ls), sum(ls), max(ls, default=0), len(qb) if qb is not None else 0])
        return out

    rnd = 0
    actor = None
    T = [0, 0, 0]
    t_len0 = 0
    pearls = {}
    watch = {}
    births = []
    qcase = [None]
    cases = []
    last_q = [None, None]
    rams = []
    reach = [[0, 0, 0], [0, 0, 0]]
    snap = {}
    eat = [[[0, 0] for _ in range(4)] for _ in range(2)]
    dth = [[[[0, 0] for _ in range(5)] for _ in range(4)] for _ in range(2)]
    spl = [[[0, 0] for _ in range(4)] for _ in range(2)]
    first_r4 = [None, None]
    qdeath = [None, None]
    anomalies = Counter()
    drop_ctx = None
    drops = []
    n_nat = 0

    def finish(a):
        lst = watch.pop(a, None)
        b = bodies.get(a)
        if lst:
            for r in lst:
                if r[9] != 0:
                    continue
                if b is None:
                    r[9] = 5
                    continue
                ci = r[20]
                h = b[0]
                dx = abs(h[0] - ci % W)
                if dx > W - dx:
                    dx = W - dx
                dy = abs(h[1] - ci // W)
                if dy > H - dy:
                    dy = H - dy
                da = dx + dy
                r[9] = 1 if da > r[2] else 2
                r[10] = T[1]
                r[11] = T[0]
                r[12] = da
                r[13] = T[2]
        c = qcase[0]
        if c is not None:
            qcase[0] = None
            dref = c.pop('dref')
            if b is None:
                c['died'] = 1
                c['nd'] = -1
            else:
                c['died'] = 0
                c['nd'] = dref.get(b[0][1] * W + b[0][0], FAR)
            c['st'] = T[0]
            c['te'] = T[1]
            cases.append(c)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k != 3:
            drop_ctx = None
        if k == 12 or k == 2 or 5 <= k <= 8:
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            if actor is not None:
                finish(actor)
            if k == 0:
                if rnd in MARKS:
                    snap[str(rnd)] = totals()
                rnd = p.i32(0)
                actor = None
                continue
            actor = p.i32(0)
            T[0] = 0
            T[1] = 0
            T[2] = 0
            b = bodies.get(actor)
            if b is None:
                anomalies['turn of a dead dragon'] += 1
                t_len0 = 0
                actor = None
                continue
            t_len0 = len(b)
            wl = watch.get(actor)
            if wl:
                for r in wl:
                    if r[9] == 0:
                        r[23] = occ_code(r[20], actor)
            if actor in qside:
                s = qside[actor]
                u = b[0][1] * W + b[0][0]
                last_q[s] = (rnd, {i: (bb[0], len(bb)) for i, bb in bodies.items()})
                if rnd <= 200:
                    dist = bfs(u, 12)
                    reach[s][0] += 1
                    full = False
                    free = False
                    best = FAR
                    ref = -1
                    for i, bb in bodies.items():
                        if team[i] == s:
                            continue
                        hh = bb[0]
                        d = dist.get(hh[1] * W + hh[0])
                        if d is None:
                            continue
                        L = len(bb)
                        fr = (L + 3) // 4
                        fu = min(12, fr + L - 2)
                        if d <= fu:
                            full = True
                        if d <= fr:
                            free = True
                        if L <= 6 and d <= 4:
                            if d < best or (d == best and i < ref):
                                best = d
                                ref = i
                    if full:
                        reach[s][1] += 1
                    if free:
                        reach[s][2] += 1
                    if best == 3 or best == 4:
                        rb = bodies[ref]
                        rpos = rb[0][1] * W + rb[0][0]
                        dref = bfs(rpos, 16)
                        occ = set()
                        for bb in bodies.values():
                            for c in bb:
                                occ.add(c[1] * W + c[0])
                        legal = [v for v in nbr[u] if v not in occ]
                        alt = sum(1 for v in legal if dref.get(v, FAR) >= best)
                        qcase[0] = dict(s=s, r=rnd, d=best, ref=ref, rl=len(rb), rq=1 if ref in qside else 0,
                                        ql=len(b), nl=len(legal), alt=alt, sym=dref.get(u, FAR), dref=dref)
        elif k == 4:
            pass
        elif k == 3:
            c = replay.point(p.pointer(0))
            ci = c[1] * W + c[0]
            v = p.u32(0)
            if v == 1:
                if ci in pearls:
                    anomalies['pearl on pearl'] += 1
                if drop_ctx is not None:
                    drop_ctx['spawned'] += 1
                    pearls[ci] = False
                else:
                    if actor is not None:
                        anomalies['natural spawn inside a turn'] += 1
                    n_nat += 1
                    brec = None
                    tx, ty = c[0], c[1]
                    m0 = FAR
                    m1 = FAR
                    i0 = -1
                    i1 = -1
                    c0 = 0
                    c1 = 0
                    for i, bb in bodies.items():
                        h = bb[0]
                        dx = h[0] - tx
                        if dx < 0:
                            dx = -dx
                        if dx > W - dx:
                            dx = W - dx
                        dy = h[1] - ty
                        if dy < 0:
                            dy = -dy
                        if dy > H - dy:
                            dy = H - dy
                        d = dx + dy
                        if d > 6:
                            continue
                        if team[i] == 0:
                            c0 += 1
                            if d < m0 or (d == m0 and i < i0):
                                m0 = d
                                i0 = i
                        else:
                            c1 += 1
                            if d < m1 or (d == m1 and i < i1):
                                m1 = d
                                i1 = i
                    if m0 <= 6 and m1 <= 6 and m0 != m1:
                        if m0 < m1:
                            S, dn, df, ni, oi, nS, nO = 0, m0, m1, i0, i1, c0, c1
                        else:
                            S, dn, df, ni, oi, nS, nO = 1, m1, m0, i1, i0, c1, c0
                        nb = bodies[ni]
                        h = nb[0]
                        dx = abs(h[0] - tx)
                        if dx > W - dx:
                            dx = W - dx
                        dy = abs(h[1] - ty)
                        if dy > H - dy:
                            dy = H - dy
                        view = 1 if (dx <= 3 and dy <= 3) else 0
                        dt = bfs(ci, 8)
                        oh = bodies[oi][0]
                        brec = [rnd, S, dn, df, view, nS, nO, len(nb), 1 if ni in qside else 0, 0, 0, 0, -1, 0,
                                0, -1, 0, -1, dt.get(h[1] * W + h[0], FAR), dt.get(oh[1] * W + oh[0], FAR), ci, ni, occ_code(ci, ni), -1]
                        births.append(brec)
                        watch.setdefault(ni, []).append(brec)
                    pearls[ci] = brec if brec is not None else True
            elif v == 0:
                if ci not in pearls:
                    anomalies['remove without pearl'] += 1
                    continue
                pr = pearls.pop(ci)
                if actor is None or actor not in team:
                    anomalies['remove without actor'] += 1
                    continue
                s = team[actor]
                eat[s][window(rnd)][0 if pr is False else 1] += 1
                T[1] += 1
                if pr is not False and pr is not True:
                    pr[14] = 1
                    pr[15] = s
                    pr[16] = 1 if actor == pr[21] else 0
                    pr[17] = rnd - pr[0]
                    if pr[9] == 0:
                        pr[9] = 3 if actor == pr[21] else 4
            else:
                anomalies['tile value'] += 1
        elif k == 9:
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            t = replay.point(p.pointer(1))
            b = bodies.get(i)
            if b is None:
                anomalies['update of unknown dragon'] += 1
                continue
            if b[0] != h:
                b.appendleft(h)
                if i == actor:
                    T[0] += 1
            while len(b) > 1 and b[-1] != t:
                b.pop()
            if b[-1] != t:
                anomalies['tail mismatch'] += 1
        elif k == 10:
            par, ch, tm = p.i32(0), p.i32(4), p.u16(8)
            sd = 0 if tm == ours else 1
            if par in team and team[par] != sd:
                anomalies['split team differs'] += 1
            before = len(bodies[par]) if par in bodies else 0
            bodies[par] = deque(replay.point(c) for c in p.pointer(0))
            bodies[ch] = deque(replay.point(c) for c in p.pointer(1))
            team[par] = sd
            team[ch] = sd
            cell = spl[sd][window(rnd)]
            cell[0] += 1
            cell[1] += len(bodies[par]) + len(bodies[ch]) - before
            if par == actor:
                T[2] = 1
        elif k == 11:
            i = p.i32(0)
            reason = p.u16(4)
            b = bodies.get(i)
            if b is None:
                anomalies['death of unknown dragon'] += 1
                continue
            s = team[i]
            cell = dth[s][window(rnd)][reason if reason < 5 else 4]
            cell[0] += 1
            cell[1] += len(b)
            if reason == 4 and first_r4[s] is None:
                first_r4[s] = rnd
            lst = watch.pop(i, None)
            if lst:
                for r in lst:
                    if r[9] == 0:
                        r[9] = 5
            if reason == 3 and i in qside and i != actor and actor in bodies:
                rb = bodies[actor]
                r = dict(s=s, r=rnd, cross=1 if team[actor] != s else 0, ml=len(rb), ml0=t_len0, st=T[0] + 1,
                         mq=1 if actor in qside else 0, ql=len(b), oq_dead=1 if qdeath[1 - s] is not None else 0)
                snapq = last_q[s]
                if snapq is None:
                    r['nosnap'] = 1
                else:
                    srnd, heads = snapq
                    r['sr'] = srnd
                    if actor not in heads or i not in heads:
                        r['born_later'] = 1
                    else:
                        mh, mlen = heads[actor]
                        q0 = heads[i][0]
                        dist = bfs(mh[1] * W + mh[0], 4000)
                        r['L'] = mlen
                        r['d0'] = dist.get(q0[1] * W + q0[0], FAR)
                        r['d1'] = dist.get(b[0][1] * W + b[0][0], FAR)
                        r['moved'] = 1 if q0 != b[0] else 0
                rams.append(r)
            if i in qside and qdeath[s] is None:
                qdeath[s] = [rnd, reason, len(b), 1 if i == actor else 0]
            bodies.pop(i)
            drop_ctx = dict(spawned=0, need=(len(b) + 1) // 2)
            drops.append(drop_ctx)

    if actor is not None:
        finish(actor)
    if rnd in MARKS:
        snap[str(rnd)] = totals()
    final = totals()
    drop_mismatch = sum(1 for d in drops if d['spawned'] != d['need'])
    final_ok = True
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if (team[i] == 0) == (z == ours)]
        st = res.pointer(z)
        if (len(ls), max(ls, default=0), sum(ls)) != (st.i32(0), st.i32(4), st.i32(8)):
            final_ok = False
    rec.update(last_round=rnd, snap=snap, final=final, eat=eat, dth=dth, spl=spl, first_r4=first_r4, qdeath=qdeath,
               reach=reach, rams=rams, cases=cases, births=[r[:20] + r[22:24] for r in births], n_nat=n_nat,
               anomalies=dict(anomalies), drop_mismatch=drop_mismatch, final_ok=final_ok, bad_portals=bad_portals,
               portals=n_portals)
    return rec


def main():
    shard, n = int(sys.argv[1]), int(sys.argv[2])
    battles = {}
    for line in Path('data/analysis/ladder/battles.jsonl').read_text().splitlines():
        if line.strip():
            b = json.loads(line)
            battles[str(b['id'])] = b
    games = []
    for folder in sorted(LADDER.iterdir()):
        if not folder.is_dir():
            continue
        for mp in sorted(folder.glob('game-*.json')):
            meta = json.loads(mp.read_text())
            games.append((meta['id'], folder, meta))
    games.sort(key=lambda g: g[0])
    if shard == 0:
        out = open(P + 'x5b-0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'x5b-1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'x5b-2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'x5b-3.jsonl', 'w')
    elif shard == 4:
        out = open(P + 'x5b-4.jsonl', 'w')
    elif shard == 5:
        out = open(P + 'x5b-5.jsonl', 'w')
    else:
        out = open(P + 'x5b-test.jsonl', 'w')
    done = 0
    for k, (gid, folder, meta) in enumerate(games):
        if shard < 6 and k % n != shard:
            continue
        if shard >= 6 and k % 70 != 9:
            continue
        path = folder / ('M%d.replay' % gid)
        try:
            rec = process(path, meta, folder.name)
        except Exception as e:
            rec = dict(game=gid, battle=folder.name, error='%s: %s' % (type(e).__name__, e))
        b = battles.get(folder.name)
        if b:
            rec.update(opponentId=b['opponentId'], opponent=b['opponent'], opponentElo=b['opponentElo'], at_kst=b['at_kst'],
                       ranked=b['ranked'], ledger_complete=b.get('complete'))
        out.write(json.dumps(rec, ensure_ascii=False) + '\n')
        out.flush()
        done += 1
    out.close()
    print('shard', shard, 'of', n, 'games written', done, 'of', len(games))


main()
