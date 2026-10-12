#!/usr/bin/env python3
"""Verifier extraction 7 (run of 2026-10-07 07:35 KST) for the queue F31: pearls and splits per raw round and side,
dragons alive / total / longest at the end of every raw round, and the adjacent-pearl turns (a pearl next to the head
of a non-queen dragon at its turn start, on a tile no body is on, not every such pearl with an enemy head within 2).
Own state rebuild from the raw replays; only the byte decoder (battlecode/replay.py) is shared.
One JSON line per game. Usage: python3 extract7.py <shard> <shards>"""
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
FAR = 99
NR = 520


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
    pairs = {}
    for e, (kind, pid) in edges.items():
        if kind == 2:
            pairs.setdefault(pid, []).append(e)
    bad = sum(1 for v in pairs.values() if len(v) != 2)
    N = W * H
    nbr = [[] for _ in range(N)]
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
                if v not in nbr[u]:
                    nbr[u].append(v)
    return nbr, bad, len(pairs)


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
    sig_src = json.dumps([W, H, sorted((e, k, p) for e, (k, p) in edges.items() if k), sorted(c for t, c in dragons)])
    code = 'main' if bots[ours] in MAIN else 'v31' if bots[ours] in OLD else 'other'
    rec = dict(game=meta['id'], battle=battle, map=meta['mapName'], our_side='AB'[ours], bot=bots[ours],
               code=code, completedAt=meta['completedAt'], W=W, H=H,
               layout=hashlib.sha1(sig_src.encode()).hexdigest()[:12])
    res = root.pointer(4)
    winner = res.u16(6) if res.u16(4) == 1 else None
    rec.update(end_reason=res.u16(2), win=winner == ours, drawn=winner is None)
    nbr, bad_portals, n_portals = build_graph(W, H, edges)
    big = W * H > 1200
    lo, hi = (76, 225) if big else (226, 375)

    bodies = {}
    team = {}
    occ = {}
    for i, (t, cells) in enumerate(dragons):
        bodies[i] = deque(cells)
        team[i] = 0 if t == ours else 1
        for c in cells:
            ci = c[1] * W + c[0]
            occ[ci] = occ.get(ci, 0) + 1
    queen = [min(i for i in team if team[i] == 0), min(i for i in team if team[i] == 1)]
    qset = set(queen)
    init_alive = [sum(1 for i in team if team[i] == 0), sum(1 for i in team if team[i] == 1)]

    eat = [[0] * NR, [0] * NR]
    spl = [[0] * NR, [0] * NR]
    adjT = [[0] * NR, [0] * NR]
    adjL = [[0] * NR, [0] * NR]
    turns = [[0] * NR, [0] * NR]
    alive_a = [[0] * NR, [0] * NR]
    total_a = [[0] * NR, [0] * NR]
    longest_a = [[0] * NR, [0] * NR]
    qlen_a = [[0] * NR, [0] * NR]
    dead_a = [[0] * NR, [0] * NR]
    recs = []
    pearls = {}
    anomalies = Counter()
    T = [0, 0, 0, 3, 0]
    cur = [None]
    rnd = 0
    actor = None

    def snapshot(r):
        for s in (0, 1):
            ls = [len(b) for i, b in bodies.items() if team[i] == s]
            alive_a[s][r] = len(ls)
            total_a[s][r] = sum(ls)
            longest_a[s][r] = max(ls, default=0)
            qb = bodies.get(queen[s])
            qlen_a[s][r] = len(qb) if qb is not None else 0

    def finish():
        c = cur[0]
        if c is not None:
            cur[0] = None
            s, r, rr = c
            left = 1 if T[1] == 0 else 0
            adjT[s][r] += 1
            adjL[s][r] += left
            if rr is not None:
                rr[2] = left
                rr[3] = T[3]
                rr[4] = T[4]
                rr[5] = T[0]
                recs.append(rr)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k == 12 or k == 2 or 5 <= k <= 8:
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            finish()
            if k == 0:
                snapshot(rnd)
                rnd = p.i32(0)
                actor = None
                continue
            actor = p.i32(0)
            T[0] = 0
            T[1] = 0
            T[2] = 0
            T[3] = 3
            T[4] = 0
            b = bodies.get(actor)
            if b is None:
                anomalies['turn of a dead dragon'] += 1
                actor = None
                continue
            if actor in qset:
                continue
            s = team[actor]
            turns[s][rnd] += 1
            h = b[0]
            cand = [v for v in nbr[h[1] * W + h[0]] if v in pearls and not occ.get(v)]
            if not cand:
                continue
            unc = []
            for v in cand:
                vx = v % W
                vy = v // W
                contested = False
                for i, bb in bodies.items():
                    if team[i] == s:
                        continue
                    e = bb[0]
                    dx = e[0] - vx
                    if dx < 0:
                        dx = -dx
                    if dx > W - dx:
                        dx = W - dx
                    if dx > 2:
                        continue
                    dy = e[1] - vy
                    if dy < 0:
                        dy = -dy
                    if dy > H - dy:
                        dy = H - dy
                    if dx + dy <= 2:
                        contested = True
                        break
                if not contested:
                    unc.append(v)
            if not unc:
                continue
            rr = None
            if lo <= rnd <= hi:
                alen = len(b)
                mates = [(len(bb), bb[0]) for i, bb in bodies.items() if team[i] == s and i != actor]
                topA = max((m[0] for m in mates), default=0)
                topB = topA if topA > alen else alen
                headsA = [m[1] for m in mates if m[0] == topA]
                headsB = [m[1] for m in mates if m[0] == topB]
                headsN = [m[1] for m in mates if m[0] > alen]
                qb = bodies.get(queen[s])
                headsQ = [qb[0]] if qb is not None else []
                out = []
                for group in (cand, unc):
                    for heads in (headsA, headsB, headsN, headsQ):
                        worst = 0
                        for v in group:
                            vx = v % W
                            vy = v // W
                            best = FAR
                            for e in heads:
                                dx = e[0] - vx
                                if dx < 0:
                                    dx = -dx
                                if dx > W - dx:
                                    dx = W - dx
                                dy = e[1] - vy
                                if dy < 0:
                                    dy = -dy
                                if dy > H - dy:
                                    dy = H - dy
                                if dx + dy < best:
                                    best = dx + dy
                            if best > worst:
                                worst = best
                        out.append(worst)
                rr = [rnd, s, 0, 3, 0, 0, alen, len(mates) + 1, len(cand), len(unc)] + out + [topA, len(headsN)]
            cur[0] = (s, rnd, rr)
        elif k == 4:
            a = p.pointer(0)
            if a is None:
                T[3] = 2
            else:
                z = a.u16(0)
                T[3] = z if z < 3 else 2
        elif k == 3:
            c = replay.point(p.pointer(0))
            ci = c[1] * W + c[0]
            v = p.u32(0)
            if v == 1:
                if ci in pearls:
                    anomalies['pearl on pearl'] += 1
                pearls[ci] = True
            elif v == 0:
                if ci not in pearls:
                    anomalies['remove without pearl'] += 1
                    continue
                pearls.pop(ci)
                if actor is None or actor not in team:
                    anomalies['remove without actor'] += 1
                    continue
                eat[team[actor]][rnd] += 1
                T[1] += 1
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
                hi2 = h[1] * W + h[0]
                occ[hi2] = occ.get(hi2, 0) + 1
                if i == actor:
                    T[0] += 1
            while len(b) > 1 and b[-1] != t:
                c = b.pop()
                occ[c[1] * W + c[0]] -= 1
            if b[-1] != t:
                anomalies['tail mismatch'] += 1
        elif k == 10:
            par, ch, tm = p.i32(0), p.i32(4), p.u16(8)
            sd = 0 if tm == ours else 1
            if par in team and team[par] != sd:
                anomalies['split team differs'] += 1
            if par in bodies:
                for c in bodies[par]:
                    occ[c[1] * W + c[0]] -= 1
            bodies[par] = deque(replay.point(c) for c in p.pointer(0))
            bodies[ch] = deque(replay.point(c) for c in p.pointer(1))
            for z in (par, ch):
                for c in bodies[z]:
                    ci = c[1] * W + c[0]
                    occ[ci] = occ.get(ci, 0) + 1
            team[par] = sd
            team[ch] = sd
            spl[sd][rnd] += 1
            if par == actor:
                T[2] = 1
        elif k == 11:
            i = p.i32(0)
            b = bodies.get(i)
            if b is None:
                anomalies['death of unknown dragon'] += 1
                continue
            for c in b:
                occ[c[1] * W + c[0]] -= 1
            dead_a[team[i]][rnd] += 1
            if i == actor:
                T[4] = 1
            bodies.pop(i)

    finish()
    snapshot(rnd)
    final_ok = True
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if (team[i] == 0) == (z == ours)]
        st = res.pointer(z)
        if (len(ls), max(ls, default=0), sum(ls)) != (st.i32(0), st.i32(4), st.i32(8)):
            final_ok = False
    occ_ok = sum(occ.values()) == sum(len(b) for b in bodies.values()) and min(occ.values(), default=0) >= 0
    n = rnd + 1
    rec.update(last_round=rnd, big=big, init_alive=init_alive, eat=[a[:n] for a in eat], spl=[a[:n] for a in spl],
               adjT=[a[:n] for a in adjT], adjL=[a[:n] for a in adjL], turns=[a[:n] for a in turns],
               alive=[a[:n] for a in alive_a], total=[a[:n] for a in total_a], longest=[a[:n] for a in longest_a],
               qlen=[a[:n] for a in qlen_a], dead=[a[:n] for a in dead_a], recs=recs,
               anomalies=dict(anomalies), final_ok=final_ok, occ_ok=occ_ok, bad_portals=bad_portals, portals=n_portals)
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
        out = open(P + 'x7-0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'x7-1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'x7-2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'x7-3.jsonl', 'w')
    elif shard == 4:
        out = open(P + 'x7-4.jsonl', 'w')
    elif shard == 5:
        out = open(P + 'x7-5.jsonl', 'w')
    else:
        out = open(P + 'x7-test.jsonl', 'w')
    done = 0
    for k, (gid, folder, meta) in enumerate(games):
        if shard < 6 and k % n != shard:
            continue
        if shard >= 6 and k % 120 != 9:
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
