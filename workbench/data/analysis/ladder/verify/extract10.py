#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier extraction 10 (run of 2026-10-07 10:21 KST) for the queue F39 / F38 (new parts).
F39: one row per lone-queen turn start (other queen already dead): short dragons of the other side alive, within 12
and within 6 path steps of her head, in her kelp-bounded component, whether a head of the other side has her body (or
her head) inside its 7 by 7 window at her turn start, and the rounds since a head of the other side last had her in
its window at ITS OWN turn start (the exact sighting, not the queen-turn approximation).
F38: one row per chance (queen turn start on a tile with three or more open sides and a narrow neighbour), with what
was free, where a pearl lay and where she stood at her next turn start; one row per stay on narrow tiles.
Own state rebuild from the raw replays; only the byte decoder (battlecode/replay.py) is shared.
One JSON line per game. Usage: python3 extract10.py <shard> <shards>"""
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
    open_sides = [sum(1 for v in dest[u] if v != -1) for u in range(N)]
    n_open = sum(1 for u in range(N) if open_sides[u] > 0)
    n_narrow_tiles = sum(1 for u in range(N) if 0 < open_sides[u] <= 2)
    nbrs = [[v for v in dest[u] if v >= 0] for u in range(N)]

    comp = [-1] * N
    comp_size = []
    for u0 in range(N):
        if comp[u0] != -1:
            continue
        cid = len(comp_size)
        comp[u0] = cid
        stack = [u0]
        n = 0
        while stack:
            a = stack.pop()
            n += 1
            for v in nbrs[a]:
                if comp[v] == -1:
                    comp[v] = cid
                    stack.append(v)
        comp_size.append(n)

    reach_cache = {}

    def reach_of(u):
        """tiles within 6 and within 12 path steps of u (bodies ignored)"""
        r = reach_cache.get(u)
        if r is None:
            seen = {u}
            frontier = [u]
            r6 = None
            for step in range(12):
                nxt = []
                for a in frontier:
                    for v in nbrs[a]:
                        if v not in seen:
                            seen.add(v)
                            nxt.append(v)
                frontier = nxt
                if step == 5:
                    r6 = frozenset(seen)
            r = (r6, frozenset(seen))
            reach_cache[u] = r
        return r

    sq_cache = {}

    def square(u):
        """the 49 tiles with wrapped Chebyshev distance 3 or less from u"""
        r = sq_cache.get(u)
        if r is None:
            x0, y0 = u % W, u // W
            r = frozenset(((y0 + dy) % H) * W + (x0 + dx) % W for dx in range(-3, 4) for dy in range(-3, 4))
            sq_cache[u] = r
        return r

    bodies = {}
    team = {}
    owner = {}
    anomalies = Counter()
    for i, (t, cells) in enumerate(dragons):
        bodies[i] = deque(cells)
        team[i] = 0 if t == ours else 1
        for c in cells:
            ci = c[1] * W + c[0]
            if ci in owner:
                anomalies['two bodies on a tile at spawn'] += 1
            owner[ci] = i
    queen = [min(i for i in team if team[i] == 0), min(i for i in team if team[i] == 1)]
    qside = {queen[0]: 0, queen[1]: 1}
    pearls = set()

    qdeath = [None, None]
    lone_rows = []
    chances = []
    stays = []
    pending = [None, None]
    stay = [None, None]
    turns = [[0, 0, 0, 0], [0, 0, 0, 0]]
    narrow_turns = [[0, 0, 0, 0], [0, 0, 0, 0]]
    zone = [None, None]
    last_exact = [None, None]
    last_exact_head = [None, None]
    lone_side = None
    rnd = 0
    actor = None

    def window(r):
        return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3

    def settle(s, u_now, alive):
        """close the pending chance of side s: u_now is her head tile at her next turn start or at the end"""
        pd = pending[s]
        if pd is None:
            return
        pending[s] = None
        row = pd['row']
        if alive and 0 < open_sides[u_now] <= 2:
            row[8] = 1
            row[9] = 1 if u_now in pd['pearl'] else 0
            row[10] = 1 if u_now in pd['free_narrow'] else 0
            row[11] = 1 if u_now in pd['narrow'] else 0
        row[12] = 0 if alive else 1
        chances.append(row)

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k == 12 or k == 2 or 5 <= k <= 8 or k == 4:
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            actor = None
            continue
        if k == 1:
            actor = p.i32(0)
            b = bodies.get(actor)
            if b is None:
                anomalies['turn of a dead dragon'] += 1
                actor = None
                continue
            s = qside.get(actor)
            if s is None:
                if lone_side is not None and team[actor] != lone_side:
                    ls = lone_side
                    qb = bodies[queen[ls]]
                    hu = b[0][1] * W + b[0][0]
                    if zone[ls] is None:
                        z = set()
                        for c in qb:
                            z |= square(c[1] * W + c[0])
                        zone[ls] = z
                    if hu in zone[ls]:
                        last_exact[ls] = rnd
                        if hu in square(qb[0][1] * W + qb[0][0]):
                            last_exact_head[ls] = rnd
                continue
            h = b[0]
            u = h[1] * W + h[0]
            w = window(rnd)
            nopen = open_sides[u]
            narrow = nopen <= 2
            settle(s, u, True)
            turns[s][w] += 1
            if narrow:
                narrow_turns[s][w] += 1
                if stay[s] is None:
                    stay[s] = [s, rnd, 1, 0, 0]
                else:
                    stay[s][2] += 1
            else:
                if stay[s] is not None:
                    stays.append(stay[s])
                    stay[s] = None
                nn = [v for v in nbrs[u] if open_sides[v] <= 2]
                if nn:
                    free_narrow = [v for v in nn if v not in owner]
                    wide = [v for v in nbrs[u] if open_sides[v] >= 3]
                    free_wide = [v for v in wide if v not in owner]
                    pearl = [v for v in free_narrow if v in pearls]
                    pearl_wide = [v for v in free_wide if v in pearls]
                    row = [s, rnd, nopen, len(set(nn)), len(set(free_narrow)), len(set(free_wide)), len(set(pearl)),
                           len(set(pearl_wide)), 0, 0, 0, 0, 0, len(b)]
                    pending[s] = dict(row=row, pearl=set(pearl), free_narrow=set(free_narrow), narrow=set(nn))
            if queen[1 - s] not in bodies:
                r6, r12 = reach_of(u)
                if zone[s] is None:
                    z = set()
                    for c in b:
                        z |= square(c[1] * W + c[0])
                    zone[s] = z
                zs = zone[s]
                zh = square(u)
                cq = comp[u]
                e_all = e_short = short12 = short6 = any12 = in_comp = seers = seers_head = seer_short12 = 0
                for z, bz in bodies.items():
                    if team[z] == s:
                        continue
                    e_all += 1
                    zu = bz[0][1] * W + bz[0][0]
                    in12 = zu in r12
                    if in12:
                        any12 += 1
                    sees = zu in zs
                    if sees:
                        seers += 1
                        if zu in zh:
                            seers_head += 1
                    if len(bz) <= 4:
                        e_short += 1
                        if in12:
                            short12 += 1
                            if zu in r6:
                                short6 += 1
                            if sees:
                                seer_short12 += 1
                        if comp[zu] == cq:
                            in_comp += 1
                le = last_exact[s]
                lh = last_exact_head[s]
                lone_rows.append([s, rnd, e_short, short12, short6, e_all, any12, in_comp, seers, seers_head,
                                  seer_short12, -1 if le is None else rnd - le, -1 if lh is None else rnd - lh,
                                  len(r12), len(b), comp_size[cq]])
        elif k == 3:
            c = replay.point(p.pointer(0))
            ci = c[1] * W + c[0]
            v = p.u32(0)
            if v == 1:
                if ci in pearls:
                    anomalies['pearl on pearl'] += 1
                pearls.add(ci)
            elif v == 0:
                if ci not in pearls:
                    anomalies['remove without pearl'] += 1
                pearls.discard(ci)
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
            sq = qside.get(i)
            if sq is not None:
                zone[sq] = None
            if b[0] != h:
                b.appendleft(h)
                hi2 = h[1] * W + h[0]
                if hi2 in owner:
                    anomalies['head onto an occupied tile'] += 1
                owner[hi2] = i
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
            sq = qside.get(par)
            if sq is not None:
                zone[sq] = None
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
            s = qside.get(i)
            if s is not None:
                qdeath[s] = dict(round=rnd, reason=reason, actor=i == actor, length=len(b))
                settle(s, -1, False)
                if stay[s] is not None:
                    stay[s][3] = 1
                    stays.append(stay[s])
                    stay[s] = None
                zone[s] = None
                if queen[1 - s] in bodies:
                    lone_side = 1 - s
                else:
                    lone_side = None
            for c in b:
                ci = c[1] * W + c[0]
                if owner.get(ci) == i:
                    del owner[ci]
                else:
                    anomalies['dead body tile not owned'] += 1
            bodies.pop(i)

    for s in (0, 1):
        qb = bodies.get(queen[s])
        if qb is not None:
            settle(s, qb[0][1] * W + qb[0][0], True)
            if stay[s] is not None:
                stay[s][4] = 1
                stays.append(stay[s])
                stay[s] = None
    final_ok = True
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if (team[i] == 0) == (z == ours)]
        st = res.pointer(z)
        if (len(ls), max(ls, default=0), sum(ls)) != (st.i32(0), st.i32(4), st.i32(8)):
            final_ok = False
    own_ok = len(owner) == sum(len(b) for b in bodies.values())
    rec.update(last_round=rnd, queen=queen, qdeath=qdeath, lone=lone_rows, chances=chances, stays=stays,
               turns=turns, narrow_turns=narrow_turns, n_open=n_open, n_narrow_tiles=n_narrow_tiles,
               n_comp=sum(1 for c in comp_size if c > 1), big_comp=max(comp_size),
               q_alive_end=[queen[0] in bodies, queen[1] in bodies],
               anomalies=dict(anomalies), final_ok=final_ok, own_ok=own_ok,
               bad_portals=bad_portals, portals=n_portals)
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
        out = open(P + 'x10-0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'x10-1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'x10-2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'x10-3.jsonl', 'w')
    elif shard == 4:
        out = open(P + 'x10-4.jsonl', 'w')
    elif shard == 5:
        out = open(P + 'x10-5.jsonl', 'w')
    else:
        out = open(P + 'x10-test.jsonl', 'w')
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
