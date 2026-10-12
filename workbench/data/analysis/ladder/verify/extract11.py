#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier extraction 11 (run of 2026-10-07 11:17 KST) for the queue F38 (long stays on narrow tiles) and F39
(lone queen death rate by how many short dragons an opponent brings).
F38: one row per stay of a queen on narrow tiles (turn starts), with how it ended, the engine death reason, and
flags taken at its turn starts (own dragon body beside her head, enemy head within 3 columns and rows, enemy body
beside her head, dead-end tile); one row per run of consecutive head positions on narrow tiles (every step, so a
sprint does not shorten it); queen turn starts, steps and turns of two or more steps.
F39: one row per turn start of a queen whose opposite queen is dead: round, short dragons of the other side alive,
within 12 and 6 path steps of her head, heads of the other side within 3 columns and rows of any tile of her body
and of her head.
Own state rebuild from the raw replays; only the byte decoder (battlecode/replay.py) is shared.
One JSON line per game. Usage: python3 extract11.py <shard> <shards>"""
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
    n_dead_tiles = sum(1 for u in range(N) if open_sides[u] == 1)
    nbrs = [[v for v in dest[u] if v >= 0] for u in range(N)]

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
        """the 49 tiles with wrapped column and row distance 3 or less from u"""
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

    qdeath = [None, None]
    lone_rows = []
    stays = []
    truns = []
    stay = [None, None]
    stay_tiles = [None, None]
    trun = [None, None]
    turns = [[0, 0, 0, 0], [0, 0, 0, 0]]
    narrow_turns = [[0, 0, 0, 0], [0, 0, 0, 0]]
    steps = [0, 0]
    multi_turns = [0, 0]
    step_in_turn = 0
    rnd = 0
    actor = None
    dirs = []
    used = 0
    last_death = None

    for s in (0, 1):
        hq = bodies[queen[s]][0]
        uq = hq[1] * W + hq[0]
        if 0 < open_sides[uq] <= 2:
            trun[s] = [s, 0, 1, 0, 0, open_sides[uq]]

    def window(r):
        return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3

    def head_moved(s, hu, r):
        """the queen of side s has a new head tile hu (one step) in round r"""
        if open_sides[hu] <= 2:
            if trun[s] is None:
                trun[s] = [s, r, 1, 0, 0, open_sides[hu]]
            else:
                trun[s][2] += 1
                if open_sides[hu] < trun[s][5]:
                    trun[s][5] = open_sides[hu]
        elif trun[s] is not None:
            truns.append(trun[s])
            trun[s] = None

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k == 12 or k == 2 or k == 3 or 5 <= k <= 8:
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            actor = None
            continue
        if k == 1:
            actor = p.i32(0)
            dirs = []
            used = 0
            step_in_turn = 0
            last_death = None
            b = bodies.get(actor)
            if b is None:
                anomalies['turn of a dead dragon'] += 1
                actor = None
                continue
            s = qside.get(actor)
            if s is None:
                continue
            h = b[0]
            u = h[1] * W + h[0]
            w = window(rnd)
            nopen = open_sides[u]
            narrow = nopen <= 2
            turns[s][w] += 1
            if narrow:
                narrow_turns[s][w] += 1
                own_beside = 0
                foe_beside = 0
                for v in nbrs[u]:
                    z = owner.get(v)
                    if z is None or z == actor:
                        continue
                    if team[z] == s:
                        own_beside = 1
                    else:
                        foe_beside = 1
                zh = square(u)
                zb = set()
                for c in b:
                    zb |= square(c[1] * W + c[0])
                foe_head3 = 0
                foe_head3_body = 0
                foe_short_head3 = 0
                for z, bz in bodies.items():
                    if team[z] == s:
                        continue
                    zu = bz[0][1] * W + bz[0][0]
                    if zu in zb:
                        foe_head3_body = 1
                        if zu in zh:
                            foe_head3 = 1
                            if len(bz) <= 4:
                                foe_short_head3 = 1
                free_exits = sum(1 for v in nbrs[u] if v not in owner)
                if stay[s] is None:
                    # 0 side, 1 round, 2 length, 3 death, 4 at end, 5 reason, 6 own beside any, 7 own beside first,
                    # 8 foe head3 any, 9 foe head3 first, 10 foe head3 of body any, 11 foe body beside any,
                    # 12 min open sides, 13 open sides first, 14 queen length first, 15 distinct tiles,
                    # 16 turn starts with no free exit, 17 short foe head3 any, 18 own beside turn starts
                    stay[s] = [s, rnd, 1, 0, 0, -1, own_beside, own_beside, foe_head3, foe_head3, foe_head3_body,
                               foe_beside, nopen, nopen, len(b), 1, 1 if free_exits == 0 else 0, foe_short_head3,
                               own_beside]
                    stay_tiles[s] = {u}
                else:
                    st = stay[s]
                    st[2] += 1
                    st[6] = max(st[6], own_beside)
                    st[8] = max(st[8], foe_head3)
                    st[10] = max(st[10], foe_head3_body)
                    st[11] = max(st[11], foe_beside)
                    st[12] = min(st[12], nopen)
                    stay_tiles[s].add(u)
                    st[15] = len(stay_tiles[s])
                    st[16] += 1 if free_exits == 0 else 0
                    st[17] = max(st[17], foe_short_head3)
                    st[18] += own_beside
            else:
                if stay[s] is not None:
                    stays.append(stay[s])
                    stay[s] = None
            if queen[1 - s] not in bodies:
                r6, r12 = reach_of(u)
                zb = set()
                for c in b:
                    zb |= square(c[1] * W + c[0])
                zh = square(u)
                e_all = e_short = short12 = short6 = any12 = seers = seers_head = 0
                for z, bz in bodies.items():
                    if team[z] == s:
                        continue
                    e_all += 1
                    zu = bz[0][1] * W + bz[0][0]
                    in12 = zu in r12
                    if in12:
                        any12 += 1
                    if zu in zb:
                        seers += 1
                        if zu in zh:
                            seers_head += 1
                    if len(bz) <= 4:
                        e_short += 1
                        if in12:
                            short12 += 1
                            if zu in r6:
                                short6 += 1
                lone_rows.append([s, rnd, e_short, short12, short6, e_all, any12, seers, seers_head, len(b)])
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
                sq = qside.get(i)
                if sq is not None:
                    steps[sq] += 1
                    step_in_turn += 1
                    if step_in_turn == 2:
                        multi_turns[sq] += 1
                    head_moved(sq, hi2, rnd)
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
            old_head = bodies[par][0] if par in bodies else None
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
            sq = qside.get(par)
            if sq is not None and old_head is not None and bodies[par][0] != old_head:
                anomalies['queen head changed by a split'] += 1
                nh = bodies[par][0]
                head_moved(sq, nh[1] * W + nh[0], rnd)
        elif k == 11:
            i = p.i32(0)
            reason = p.u16(4)
            b = bodies.get(i)
            if b is None:
                anomalies['death of unknown dragon'] += 1
                continue
            s = qside.get(i)
            if s is not None:
                # who killed her: 0 nobody (wall, own body, other), 1 a dragon of her own side, 2 the other side,
                # 3 a body that could not be resolved
                by = 0
                hu = b[0][1] * W + b[0][0]
                if reason == 3:
                    if i == actor:
                        by = 3 if last_death is None else (1 if last_death[1] == s else 2)
                    elif actor is not None and actor in team:
                        by = 1 if team[actor] == s else 2
                    else:
                        by = 3
                elif reason == 2:
                    by = 3
                    if i == actor and used < len(dirs) and dirs[used] < 4:
                        dv = dest[hu][dirs[used]]
                        if dv >= 0 and dv in owner:
                            by = 1 if team[owner[dv]] == s else 2
                other_dead = queen[1 - s] not in bodies
                odr = None
                if other_dead and qdeath[1 - s] is not None:
                    odr = qdeath[1 - s]['round']
                qdeath[s] = dict(round=rnd, reason=reason, actor=i == actor, length=len(b), by=by,
                                 open_sides=open_sides[hu], in_stay=stay[s] is not None, other_queen_dead_round=odr)
                if stay[s] is not None:
                    stay[s][3] = 1
                    stay[s][5] = reason
                    stays.append(stay[s])
                    stay[s] = None
                if trun[s] is not None:
                    trun[s][3] = 1
                    truns.append(trun[s])
                    trun[s] = None
            last_death = (i, team[i])
            for c in b:
                ci = c[1] * W + c[0]
                if owner.get(ci) == i:
                    del owner[ci]
                else:
                    anomalies['dead body tile not owned'] += 1
            bodies.pop(i)

    for s in (0, 1):
        if stay[s] is not None:
            stay[s][4] = 1
            stays.append(stay[s])
            stay[s] = None
        if trun[s] is not None:
            trun[s][4] = 1
            truns.append(trun[s])
            trun[s] = None
    final_ok = True
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if (team[i] == 0) == (z == ours)]
        st = res.pointer(z)
        if (len(ls), max(ls, default=0), sum(ls)) != (st.i32(0), st.i32(4), st.i32(8)):
            final_ok = False
    own_ok = len(owner) == sum(len(b) for b in bodies.values())
    rec.update(last_round=rnd, queen=queen, qdeath=qdeath, lone=lone_rows, stays=stays, truns=truns,
               turns=turns, narrow_turns=narrow_turns, steps=steps, multi_turns=multi_turns,
               n_open=n_open, n_narrow_tiles=n_narrow_tiles, n_dead_tiles=n_dead_tiles,
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
        out = open(P + 'x11-0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'x11-1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'x11-2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'x11-3.jsonl', 'w')
    elif shard == 4:
        out = open(P + 'x11-4.jsonl', 'w')
    elif shard == 5:
        out = open(P + 'x11-5.jsonl', 'w')
    else:
        out = open(P + 'x11-test.jsonl', 'w')
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
