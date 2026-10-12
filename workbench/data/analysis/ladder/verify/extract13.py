#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier extraction 13 (run of 2026-10-07 15:12 KST) for the queue F44 (early wipe-outs on small layouts),
F42 (heads near the surviving queen after the other queen died) and F7 (6 or fewer dragons at raw round 100 on
layouts that start with 2 dragons).
Own state rebuild from the raw replays; only the byte decoder (battlecode/replay.py) is shared.
Sides in the output: 0 = ours (team 1119), 1 = theirs.
One JSON line per game. Usage: python3 extract13.py <shard> <shards>"""
import sys, json, hashlib
from pathlib import Path
from collections import deque, Counter
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path('../battlecode').resolve()))
import replay

MAIN_HASH = '724684aa35'
OLD_HASH = '2941093210'
US = 1119
LADDER = Path('data/online/ladder')


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


def build_dest(W, H, edges):
    """dest[tile][d] = destination tile index, -1 behind kelp, -2 for a portal that cannot be followed."""
    pairs = {}
    for e, (kind, pid) in edges.items():
        if kind == 2:
            pairs.setdefault(pid, []).append(e)
    bad = sum(1 for v in pairs.values() if len(v) != 2)
    N = W * H
    dest = [[0, 0, 0, 0] for _ in range(N)]
    for y in range(H):
        for x in range(W):
            u = y * W + x
            for d in range(4):
                e = edge_of(W, H, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    dest[u][d] = -1
                    continue
                if kind == 2:
                    pr = pairs.get(pid, [])
                    if len(pr) != 2:
                        dest[u][d] = -2
                        continue
                    pe = pr[0] if pr[1] == e else pr[1]
                    row, px = divmod(pe, W + 1)
                    if row % 2 != (0 if d in (0, 2) else 1):
                        bad += 1
                        dest[u][d] = -2
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
                dest[u][d] = v
    return dest, bad, len(pairs)


def window(r):
    return 0 if r <= 100 else 1 if r <= 300 else 2


def process(path, meta, battle, hashes):
    root = replay.load(path).root()
    bots = (root.text(1), root.text(2))
    if meta['teamAId'] == US:
        ours = 0
    elif meta['teamBId'] == US:
        ours = 1
    else:
        raise ValueError('team 1119 is on neither side')
    W, H, dragons, edges = read_layout(root.text(0))
    N = W * H
    sig_src = json.dumps([W, H, sorted((e, k, p) for e, (k, p) in edges.items() if k), sorted(c for t, c in dragons)])
    hs = hashes.get(bots[ours], '')
    code = 'main' if hs.startswith(MAIN_HASH) else 'v31' if hs.startswith(OLD_HASH) else 'other'
    rec = dict(game=meta['id'], battle=battle, map=meta['mapName'], our_side='AB'[ours], bot=bots[ours],
               their_bot=bots[1 - ours], code=code, completedAt=meta['completedAt'], W=W, H=H,
               layout=hashlib.sha1(sig_src.encode()).hexdigest()[:12])
    res = root.pointer(4)
    winner = res.u16(6) if res.u16(4) == 1 else None
    rec.update(end_reason=res.u16(2), win=winner == ours, drawn=winner is None)
    dest, bad_portals, n_portals = build_dest(W, H, edges)
    nbrs = [sorted(set(v for v in dest[u] if v >= 0)) for u in range(N)]
    open_tiles = sum(1 for u in range(N) if any(v != -1 for v in dest[u]))
    comp = [-1] * N
    comp_size = []
    for u0 in range(N):
        if comp[u0] >= 0:
            continue
        c = len(comp_size)
        comp[u0] = c
        stack = [u0]
        n = 0
        while stack:
            a = stack.pop()
            n += 1
            for v in nbrs[a]:
                if comp[v] < 0:
                    comp[v] = c
                    stack.append(v)
        comp_size.append(n)

    cache = {}

    def ball(u):
        r = cache.get(u)
        if r is None:
            r = {u: 0}
            frontier = [u]
            for d in range(1, 7):
                nxt = []
                for a in frontier:
                    for v in nbrs[a]:
                        if v not in r:
                            r[v] = d
                            nxt.append(v)
                frontier = nxt
            cache[u] = r
        return r

    bodies = {}
    team = {}
    owner = {}
    anomalies = Counter()
    for i, (t, cells) in enumerate(dragons):
        bodies[i] = deque(cells)
        team[i] = 0 if t == ours else 1
        for c in cells:
            owner[c[1] * W + c[0]] = i
    queen = [min(i for i in team if team[i] == 0), min(i for i in team if team[i] == 1)]
    qside = {queen[0]: 0, queen[1]: 1}
    spawn_n = [sum(1 for i in team if team[i] == 0), sum(1 for i in team if team[i] == 1)]
    h0, h1 = bodies[queen[0]][0], bodies[queen[1]][0]
    dx = abs(h0[0] - h1[0])
    dy = abs(h0[1] - h1[1])
    qdist = min(dx, W - dx) + min(dy, H - dy)
    qlen0 = [len(bodies[queen[0]]), len(bodies[queen[1]])]

    qdeath = [None, None]
    after = [None, None]
    for s in (0, 1):
        after[s] = dict(turns=0, A6=0, B6=0, A2=0, B2=0, same=0, n_other=0, n_short=0, n_same=0, zero_other=0,
                        ball=0, expA=0.0, expB=0.0, histA=[0] * 8, histB=[0] * 8, wt=[0, 0, 0, 0], wB=[0, 0, 0, 0],
                        wA=[0, 0, 0, 0])
    alive = [[], []]
    eaten = [[], []]
    total = [[], []]
    cum = [0, 0]
    rounds_seen = []
    dw = [[[0] * 5 for _ in range(3)] for _ in range(2)]
    early = []
    rnd = 0
    started = False
    actor = None
    dirs = []
    used = 0
    last_death = None

    def snap(r):
        rounds_seen.append(r)
        for s in (0, 1):
            ls = [len(bz) for z, bz in bodies.items() if team[z] == s]
            alive[s].append(len(ls))
            total[s].append(sum(ls))
            eaten[s].append(cum[s])

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k == 12 or k == 2 or 5 <= k <= 8:
            continue
        p = ev.pointer(0)
        if k == 0:
            if started:
                snap(rnd)
            started = True
            rnd = p.i32(0)
            actor = None
            continue
        if k == 1:
            actor = p.i32(0)
            dirs = []
            used = 0
            last_death = None
            b = bodies.get(actor)
            if b is None:
                anomalies['turn of a dead dragon'] += 1
                actor = None
                continue
            s = qside.get(actor)
            if s is None or queen[1 - s] in bodies:
                continue
            u = b[0][1] * W + b[0][0]
            bl = ball(u)
            cu = comp[u]
            mdA = 7
            mdB = 7
            n_other = n_short = n_same = n_same_short = 0
            for z, bz in bodies.items():
                if team[z] == s:
                    continue
                n_other += 1
                short = len(bz) <= 4
                if short:
                    n_short += 1
                hz = bz[0][1] * W + bz[0][0]
                if comp[hz] == cu:
                    n_same += 1
                    if short:
                        n_same_short += 1
                d = bl.get(hz)
                if d is not None:
                    if d < mdB:
                        mdB = d
                    if short and d < mdA:
                        mdA = d
            f = after[s]
            f['turns'] += 1
            f['A6'] += 1 if mdA <= 6 else 0
            f['B6'] += 1 if mdB <= 6 else 0
            f['A2'] += 1 if mdA <= 2 else 0
            f['B2'] += 1 if mdB <= 2 else 0
            f['histA'][mdA] += 1
            f['histB'][mdB] += 1
            f['same'] += 1 if n_same else 0
            f['n_other'] += n_other
            f['n_short'] += n_short
            f['n_same'] += n_same
            f['zero_other'] += 1 if n_other == 0 else 0
            f['ball'] += len(bl)
            share = (len(bl) - 1) / max(1, comp_size[cu] - 1)
            f['expA'] += 1 - (1 - share) ** n_same_short
            f['expB'] += 1 - (1 - share) ** n_same
            w4 = 0 if rnd <= 100 else 1 if rnd <= 200 else 2 if rnd <= 300 else 3
            f['wt'][w4] += 1
            f['wB'][w4] += 1 if mdB <= 6 else 0
            f['wA'][w4] += 1 if mdA <= 6 else 0
        elif k == 3:
            if p.u32(0) == 0:
                if actor is not None and actor in team:
                    cum[team[actor]] += 1
                else:
                    anomalies['pearl removed outside a turn'] += 1
        elif k == 4:
            if actor is not None and p.i32(0) == actor:
                a = p.pointer(0)
                lst = a.pointer(0) if (a is not None and a.u16(0) == 0) else None
                dirs = list(lst) if lst is not None else []
                used = 0
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
                if hi2 in owner:
                    anomalies['head onto an occupied tile'] += 1
                owner[hi2] = i
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != t:
                c = b.pop()
                ci = c[1] * W + c[0]
                if owner.get(ci) == i:
                    del owner[ci]
                else:
                    anomalies['tail tile not owned'] += 1
            if b[-1] != t:
                anomalies['tail mismatch'] += 1
        elif k == 10:
            par, ch, tm = p.i32(0), p.i32(4), p.u16(8)
            sd = 0 if tm == ours else 1
            if par in team and team[par] != sd:
                anomalies['split team differs'] += 1
            if par in bodies:
                for c in bodies[par]:
                    ci = c[1] * W + c[0]
                    if owner.get(ci) == par:
                        del owner[ci]
            bodies[par] = deque(replay.point(c) for c in p.pointer(0))
            bodies[ch] = deque(replay.point(c) for c in p.pointer(1))
            for z in (par, ch):
                for c in bodies[z]:
                    ci = c[1] * W + c[0]
                    if ci in owner:
                        anomalies['split onto an occupied tile'] += 1
                    owner[ci] = z
            team[par] = sd
            team[ch] = sd
        elif k == 11:
            i = p.i32(0)
            reason = p.u16(4)
            b = bodies.get(i)
            if b is None:
                anomalies['death of unknown dragon'] += 1
                continue
            sd = team[i]
            dw[sd][window(rnd)][reason if reason < 5 else 4] += 1
            mover_side = -1
            other_side = -1
            other_len = -1
            other_queen = 0
            if reason == 3:
                if i == actor:
                    mover_side = sd
                    if last_death is not None:
                        other_side = last_death[1]
                        other_len = last_death[2]
                        other_queen = last_death[3]
                elif actor is not None and actor in bodies:
                    mover_side = team[actor]
                    other_side = team[actor]
                    other_len = len(bodies[actor])
                    other_queen = 1 if actor in qside else 0
            elif reason == 2:
                hu = b[0][1] * W + b[0][0]
                if i == actor and used < len(dirs) and dirs[used] < 4:
                    dv = dest[hu][dirs[used]]
                    if dv >= 0 and dv in owner:
                        other_side = team[owner[dv]]
                        other_len = len(bodies[owner[dv]])
                        other_queen = 1 if owner[dv] in qside else 0
            if rnd <= 125:
                early.append([rnd, sd, reason, len(b), 1 if i == actor else 0, mover_side, other_side, other_len])
            s = qside.get(i)
            if s is not None:
                lens_now = [[len(bz) for z, bz in bodies.items() if team[z] == s2 and z != i] for s2 in (0, 1)]
                qdeath[s] = dict(round=rnd, reason=reason, was_mover=i == actor, length=len(b), mover_side=mover_side,
                                 other_side=other_side, other_len=other_len, other_queen=other_queen,
                                 other_queen_alive=queen[1 - s] in bodies,
                                 alive=[len(lens_now[0]), len(lens_now[1])])
            last_death = (i, sd, len(b), 1 if i in qside else 0)
            for c in b:
                ci = c[1] * W + c[0]
                if owner.get(ci) == i:
                    del owner[ci]
                else:
                    anomalies['dead body tile not owned'] += 1
            bodies.pop(i)

    snap(rnd)
    final_ok = True
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if (team[i] == 0) == (z == ours)]
        st = res.pointer(z)
        if (len(ls), max(ls, default=0), sum(ls)) != (st.i32(0), st.i32(4), st.i32(8)):
            final_ok = False
    final = []
    for s in (0, 1):
        ls = sorted((len(b) for i, b in bodies.items() if team[i] == s), reverse=True)
        final.append(dict(alive=len(ls), longest=ls[0] if ls else 0, total=sum(ls),
                          queen=len(bodies[queen[s]]) if queen[s] in bodies else 0, top=ls[:6]))
    own_ok = len(owner) == sum(len(b) for b in bodies.values())
    rec.update(last_round=rnd, rounds_ok=rounds_seen == list(range(rnd + 1)), queen=queen, qdeath=qdeath, after=after,
               alive=alive, eaten=eaten, total=total, dw=dw, early=early, final=final, spawn_n=spawn_n, qdist=qdist,
               qlen0=qlen0, open_tiles=open_tiles, n_comp=len([c for c in comp_size if c > 1]),
               anomalies=dict(anomalies), final_ok=final_ok, own_ok=own_ok, bad_portals=bad_portals, portals=n_portals)
    return rec


def main():
    shard, n = int(sys.argv[1]), int(sys.argv[2])
    battles = {}
    for line in Path('data/analysis/ladder/battles.jsonl').read_text().splitlines():
        if line.strip():
            b = json.loads(line)
            battles[str(b['id'])] = b
    subs = json.loads(Path('data/online/ladder/submissions.json').read_text())
    hashes = {str(k): (v.get('sourceHash') or '') for k, v in subs.items()}
    games = []
    for folder in sorted(LADDER.iterdir()):
        if not folder.is_dir():
            continue
        for mp in sorted(folder.glob('game-*.json')):
            meta = json.loads(mp.read_text())
            games.append((meta['id'], folder, meta))
    games.sort(key=lambda g: g[0])
    if shard == 0:
        out = open(P + 'x13-0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'x13-1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'x13-2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'x13-3.jsonl', 'w')
    elif shard == 4:
        out = open(P + 'x13-4.jsonl', 'w')
    elif shard == 5:
        out = open(P + 'x13-5.jsonl', 'w')
    else:
        out = open(P + 'x13-test.jsonl', 'w')
    done = 0
    for k, (gid, folder, meta) in enumerate(games):
        if shard < 6 and k % n != shard:
            continue
        if shard >= 6 and k % 150 != 9:
            continue
        path = folder / ('M%d.replay' % gid)
        try:
            rec = process(path, meta, folder.name, hashes)
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
