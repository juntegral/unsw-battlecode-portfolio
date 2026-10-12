#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier extraction 9 (run of 2026-10-07 09:18 KST) for the queue F38 / F39.
F38: open sides of the queen's head tile at every one of her turn starts, own-team bodies beside her, narrow-tile
episodes, and the board at the start of her last turn for every queen death.
F39: at every queen turn start, short enemy heads within 6 path steps, own heads within 5 tiles; one row per lone
turn (other queen already dead) and per-window sums for turns with both queens alive.
Own state rebuild from the raw replays; only the byte decoder (battlecode/replay.py) is shared.
One JSON line per game. Usage: python3 extract9.py <shard> <shards>"""
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


def window(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


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
    """dest[tile][d] = destination tile index, -1 behind kelp, -2 for a portal that cannot be followed; via[tile][d] = 1
    if the step goes through a portal."""
    pairs = {}
    for e, (kind, pid) in edges.items():
        if kind == 2:
            pairs.setdefault(pid, []).append(e)
    bad = sum(1 for v in pairs.values() if len(v) != 2)
    N = W * H
    dest = [[0, 0, 0, 0] for _ in range(N)]
    via = [[0, 0, 0, 0] for _ in range(N)]
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
                    via[u][d] = 1
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
    return dest, via, bad, len(pairs)


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
    sig_src = json.dumps([W, H, sorted((e, k, p) for e, (k, p) in edges.items() if k), sorted(c for t, c in dragons)])
    hs = hashes.get(bots[ours], '')
    code = 'main' if hs.startswith(MAIN_HASH) else 'v31' if hs.startswith(OLD_HASH) else 'other'
    rec = dict(game=meta['id'], battle=battle, map=meta['mapName'], our_side='AB'[ours], bot=bots[ours],
               their_bot=bots[1 - ours], code=code, completedAt=meta['completedAt'], W=W, H=H,
               layout=hashlib.sha1(sig_src.encode()).hexdigest()[:12])
    res = root.pointer(4)
    winner = res.u16(6) if res.u16(4) == 1 else None
    rec.update(end_reason=res.u16(2), win=winner == ours, drawn=winner is None)
    dest, via, bad_portals, n_portals = build_dest(W, H, edges)
    n_open = sum(1 for u in range(W * H) if any(v != -1 for v in dest[u]))
    open_sides = [sum(1 for v in dest[u] if v != -1) for u in range(W * H)]
    tiles_by_open = [0, 0, 0, 0, 0]
    for u in range(W * H):
        tiles_by_open[open_sides[u]] += 1
    reach_cache = {}

    def reach_of(u):
        r = reach_cache.get(u)
        if r is None:
            seen = {u}
            frontier = [u]
            for step in range(6):
                nxt = []
                for a in frontier:
                    for v in dest[a]:
                        if v >= 0 and v not in seen:
                            seen.add(v)
                            nxt.append(v)
                frontier = nxt
            r = frozenset(seen)
            reach_cache[u] = r
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
    parent = {}

    qdeath = [None, None]
    hist = [[Counter() for _ in range(4)], [Counter() for _ in range(4)]]
    episodes = [[0] * 4, [0] * 4]
    prev_narrow = [False, False]
    prev_w = [-1, -1]
    last_start = [None, None]
    lone_rows = []
    base = [[[0] * 10 for _ in range(4)], [[0] * 10 for _ in range(4)]]
    total100 = None
    alive100 = None
    rnd = 0
    actor = None
    T = dict(kind=2, dirs=[], used=0, split=0)

    def look(i, s):
        """what is behind each of the four edges (N, E, S, W) of the head of dragon i of side s: K kelp, X a portal
        that cannot be followed, F free tile, T her own tail tile, S her own body, C a direct child of hers, M another
        dragon of her team, H an enemy head, E an enemy body. A lower case h is appended for the head of a dragon of
        her own team and a lower case p when the step goes through a portal."""
        b = bodies[i]
        h = b[0]
        u = h[1] * W + h[0]
        tail = b[-1][1] * W + b[-1][0]
        out = []
        for d in range(4):
            v = dest[u][d]
            if v == -1:
                out.append('K')
                continue
            if v == -2:
                out.append('X')
                continue
            o = owner.get(v)
            if o is None:
                c = 'F'
            elif o == i:
                c = 'T' if v == tail else 'S'
            else:
                ob = bodies[o][0]
                head = ob[1] * W + ob[0] == v
                if team[o] == s:
                    c = 'C' if parent.get(o) == i else 'M'
                    if head:
                        c += 'h'
                else:
                    c = 'H' if head else 'E'
            if via[u][d]:
                c += 'p'
            out.append(c)
        return out

    def totals():
        tt = [0, 0]
        aa = [0, 0]
        for i, b in bodies.items():
            tt[team[i]] += len(b)
            aa[team[i]] += 1
        return tt, aa

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k == 12 or k == 2 or k == 3 or 5 <= k <= 8:
            continue
        p = ev.pointer(0)
        if k == 0:
            if rnd == 100:
                total100, alive100 = totals()
            rnd = p.i32(0)
            actor = None
            continue
        if k == 1:
            actor = p.i32(0)
            T['kind'] = 2
            T['dirs'] = []
            T['used'] = 0
            T['split'] = 0
            if actor not in bodies:
                anomalies['turn of a dead dragon'] += 1
                actor = None
                continue
            s = qside.get(actor)
            if s is None:
                continue
            w = window(rnd)
            b = bodies[actor]
            h = b[0]
            u = h[1] * W + h[0]
            cls = look(actor, s)
            nopen = sum(1 for c in cls if c != 'K')
            nlegal = sum(1 for c in cls if c[0] == 'F')
            beside = 1 if any(c[0] in 'CM' for c in cls) else 0
            hist[s][w]['%d,%d,%d' % (nopen, beside, nlegal)] += 1
            narrow = nopen <= 2
            if narrow and (not prev_narrow[s] or prev_w[s] != w):
                episodes[s][w] += 1
            prev_narrow[s] = narrow
            prev_w[s] = w
            last_start[s] = dict(cls=cls, legal=nlegal, open=nopen, beside=beside, length=len(b), head=list(h),
                                 round=rnd)
            reach = reach_of(u)
            e_all = 0
            e_short = 0
            short6 = 0
            any6 = 0
            own5 = 0
            own_alive = 0
            hx, hy = h
            for z, bz in bodies.items():
                if z == actor:
                    continue
                zx, zy = bz[0]
                if team[z] == s:
                    own_alive += 1
                    dx = abs(zx - hx)
                    if W - dx < dx:
                        dx = W - dx
                    dy = abs(zy - hy)
                    if H - dy < dy:
                        dy = H - dy
                    if dx + dy <= 5:
                        own5 += 1
                else:
                    e_all += 1
                    inr = (zy * W + zx) in reach
                    if inr:
                        any6 += 1
                    if len(bz) <= 4:
                        e_short += 1
                        if inr:
                            short6 += 1
            if queen[1 - s] not in bodies:
                lone_rows.append([s, rnd, short6, e_short, e_all, own5, own_alive, len(reach), len(b), any6, nopen])
            else:
                a = base[s][w]
                a[0] += 1
                a[1] += 1 if short6 > 0 else 0
                a[2] += e_short
                a[3] += 1 if e_short == 0 else 0
                a[4] += short6
                a[5] += own5
                a[6] += 1 if own5 == 0 else 0
                a[7] += 1.0 - (1.0 - len(reach) / n_open) ** e_short
                a[8] += own_alive
                a[9] += 1 if any6 > 0 else 0
        elif k == 4:
            a = p.pointer(0)
            if a is None:
                T['kind'] = 2
                T['dirs'] = []
            else:
                z = a.u16(0)
                T['kind'] = z if z < 3 else 2
                T['dirs'] = [int(x) for x in a.pointer(0)] if z == 0 and a.pointer(0) is not None else []
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
                    T['used'] += 1
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
            parent[ch] = par
            if par == actor:
                T['split'] = 1
        elif k == 11:
            i = p.i32(0)
            reason = p.u16(4)
            b = bodies.get(i)
            if b is None:
                anomalies['death of unknown dragon'] += 1
                continue
            s = qside.get(i)
            if s is not None:
                is_actor = i == actor
                d = dict(round=rnd, reason=reason, actor=is_actor, length=len(b), event=idx,
                         other_queen_dead=queen[1 - s] not in bodies,
                         alive_us=sum(1 for z in bodies if team[z] == 0),
                         alive_them=sum(1 for z in bodies if team[z] == 1))
                now = look(i, s)
                d.update(now_cls=now, now_legal=sum(1 for c in now if c[0] == 'F'), now_head=list(b[0]),
                         now_open=sum(1 for c in now if c != 'K'),
                         now_beside=1 if any(c[0] in 'CM' for c in now) else 0)
                st = last_start[s]
                if st is not None:
                    d.update(start_cls=st['cls'], start_legal=st['legal'], start_open=st['open'],
                             start_beside=st['beside'], start_len=st['length'], start_head=st['head'],
                             start_round=st['round'])
                if is_actor:
                    d.update(kind=T['kind'], ndirs=len(T['dirs']), used=T['used'], split=T['split'])
                    if T['kind'] == 0 and T['used'] < len(T['dirs']):
                        fd = T['dirs'][T['used']]
                        d.update(fatal_dir=fd, fatal_cls=now[fd])
                        u = b[0][1] * W + b[0][0]
                        v = dest[u][fd]
                        if v >= 0 and v in owner:
                            o = owner[v]
                            d.update(hit=o, hit_side=team[o], hit_is_child=parent.get(o) == i,
                                     hit_is_queen=o in qside, hit_len=len(bodies[o]))
                else:
                    d.update(killer=actor, killer_side=team.get(actor) if actor is not None else None)
                qdeath[s] = d
            for c in b:
                ci = c[1] * W + c[0]
                if owner.get(ci) == i:
                    del owner[ci]
                else:
                    anomalies['dead body tile not owned'] += 1
            bodies.pop(i)

    if rnd == 100:
        total100, alive100 = totals()
    final_ok = True
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if (team[i] == 0) == (z == ours)]
        st = res.pointer(z)
        if (len(ls), max(ls, default=0), sum(ls)) != (st.i32(0), st.i32(4), st.i32(8)):
            final_ok = False
    own_ok = len(owner) == sum(len(b) for b in bodies.values())
    rec.update(last_round=rnd, queen=queen, qdeath=qdeath,
               hist=[[dict(c) for c in hh] for hh in hist], episodes=episodes, lone=lone_rows,
               base=[[[round(x, 4) for x in a] for a in bb] for bb in base],
               total100=total100, alive100=alive100, n_open=n_open, tiles_by_open=tiles_by_open,
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
        out = open(P + 'x9-0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'x9-1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'x9-2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'x9-3.jsonl', 'w')
    elif shard == 4:
        out = open(P + 'x9-4.jsonl', 'w')
    elif shard == 5:
        out = open(P + 'x9-5.jsonl', 'w')
    else:
        out = open(P + 'x9-test.jsonl', 'w')
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
