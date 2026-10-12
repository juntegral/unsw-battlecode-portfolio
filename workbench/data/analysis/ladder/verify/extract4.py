#!/usr/bin/env python3
"""Verifier extraction 4 (run of 2026-10-07 05:20 KST) for the queue F23 (queens in small rooms on Portals),
F24 (queen rammed, by opponent rating), F20 (heads near busy tiles: rating bands, rounds 50 and 75, cost),
F13 (a safe single step against the full reach). Own state rebuild from the raw replays; only the byte decoder
(battlecode/replay.py) is shared. One JSON line per game. Usage: python3 extract4.py <shard> <shards>"""
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
SNAP = (50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300)
FAR = 9999


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
    """nbr[u] = [(v, via_portal)] over open and portal edges (kelp closed, wrap applied); nbd[u][d] the same by
    direction (None = kelp); comp[u] = size of the room of u over open edges only (kelp and portal edges closed)."""
    pairs = {}
    for e, (kind, pid) in edges.items():
        if kind == 2:
            pairs.setdefault(pid, []).append(e)
    bad = sum(1 for v in pairs.values() if len(v) != 2)
    N = W * H
    nbr = [[] for _ in range(N)]
    nbr_open = [[] for _ in range(N)]
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
                    nbr[u].append((v, 1))
                    nbd[u][d] = (v, 1)
                else:
                    if d == 0:
                        v = ((y - 1) % H) * W + x
                    elif d == 1:
                        v = y * W + (x + 1) % W
                    elif d == 2:
                        v = ((y + 1) % H) * W + x
                    else:
                        v = y * W + (x - 1) % W
                    nbr[u].append((v, 0))
                    nbr_open[u].append(v)
                    nbd[u][d] = (v, 0)
    comp = [0] * N
    seen = [False] * N
    for s in range(N):
        if seen[s]:
            continue
        seen[s] = True
        st = [s]
        members = [s]
        while st:
            u = st.pop()
            for v in nbr_open[u]:
                if not seen[v]:
                    seen[v] = True
                    st.append(v)
                    members.append(v)
        for u in members:
            comp[u] = len(members)
    return nbr, nbd, comp, bad, len(pairs)


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
    if code == 'other':
        return rec
    nbr, nbd, comp, bad_portals, n_portals = build_graph(W, H, edges)
    N = W * H
    big = open_tiles >= 1500
    track = meta['mapName'] in ('Portals', 'Stripes')
    room_sizes = Counter(comp)

    bodies = {}
    team = {}
    for i, (t, cells) in enumerate(dragons):
        bodies[i] = deque(cells)
        team[i] = t

    def side(i):
        return 'us' if team[i] == ours else 'them'
    queen = dict(us=min(i for i in team if team[i] == ours), them=min(i for i in team if team[i] != ours))
    qid = {queen['us']: 'us', queen['them']: 'them'}
    other = dict(us='them', them='us')
    q_len0 = dict(us=len(bodies[queen['us']]), them=len(bodies[queen['them']]))
    q_room0 = dict(us=comp[bodies[queen['us']][0][1] * W + bodies[queen['us']][0][0]],
                   them=comp[bodies[queen['them']][0][1] * W + bodies[queen['them']][0][0]])

    def wrapped(a, b):
        dx = abs(a[0] - b[0])
        dx = min(dx, W - dx)
        dy = abs(a[1] - b[1])
        dy = min(dy, H - dy)
        return dx + dy

    def friends(i):
        h = bodies[i][0]
        near = 0
        alive = 0
        for z, bb in bodies.items():
            if z == i or team[z] != team[i]:
                continue
            alive += 1
            if wrapped(h, bb[0]) <= 5:
                near += 1
        return near, alive

    def bfs(src):
        dist = [-1] * N
        dist[src] = 0
        q = deque([src])
        while q:
            u = q.popleft()
            du = dist[u] + 1
            for v, via in nbr[u]:
                if dist[v] < 0:
                    dist[v] = du
                    q.append(v)
        return dist

    rnd = 0
    actor = None
    turn_id = 0
    pearls = {}
    drop_ctx = None
    drops = []
    t_steps = 0
    t_len0 = 0
    dirs = []
    n_nat = 0
    snaps = {}
    tile_births = Counter()
    tile_eat = dict(us=Counter(), them=Counter())
    eat = dict(us=[0, 0, 0], them=[0, 0, 0])
    eat_nat = dict(us=[0, 0, 0], them=[0, 0, 0])
    last_q = dict(us=None, them=None)
    rams = []
    lone = dict(us=[0, 0, 0], them=[0, 0, 0])
    qs = {}
    for s in ('us', 'them'):
        qs[s] = dict(turns=0, turns_small=0, first_small=None, turns_r100=0, portal_steps=[], track=[], death=None,
                     small_hist={})
    headon = {}
    anomalies = Counter()
    ei = -1

    for ev in root.pointer(3):
        ei += 1
        k = ev.u16(0)
        if k != 3:
            drop_ctx = None
        if k == 12 or k == 2 or 5 <= k <= 8:
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            actor = None
            turn_id += 1
            if big and rnd in SNAP:
                snaps[str(rnd)] = dict(us=[list(b[0]) for i, b in bodies.items() if team[i] == ours],
                                       them=[list(b[0]) for i, b in bodies.items() if team[i] != ours])
        elif k == 1:
            actor = p.i32(0)
            turn_id += 1
            t_steps = 0
            dirs = []
            b = bodies.get(actor)
            if b is None:
                anomalies['turn of a dead dragon'] += 1
                t_len0 = 0
                continue
            t_len0 = len(b)
            if actor in qid:
                s = qid[actor]
                q = qs[s]
                hx, hy = b[0]
                c = comp[hy * W + hx]
                q['turns'] += 1
                if rnd <= 100:
                    q['turns_r100'] += 1
                if c <= 6:
                    q['turns_small'] += 1
                    q['small_hist'][str(c)] = q['small_hist'].get(str(c), 0) + 1
                    if q['first_small'] is None:
                        q['first_small'] = rnd
                if track and (not q['track'] or q['track'][-1][1] != c):
                    q['track'].append([rnd, c, t_len0])
                last_q[s] = (rnd, {i: tuple(bb) for i, bb in bodies.items()})
                if qs[other[s]]['death'] is not None:
                    fr, alive = friends(actor)
                    lone[s][0] += 1
                    if fr < 2:
                        lone[s][1] += 1
                    if fr == 0:
                        lone[s][2] += 1
        elif k == 4:
            dirs = []
            try:
                a = p.pointer(0)
                if a is not None and a.u16(0) == 0:
                    lst = a.pointer(0)
                    if lst is not None:
                        dirs = [int(z) for z in lst]
            except Exception:
                anomalies['action decode'] += 1
                dirs = []
        elif k == 3:
            c = replay.point(p.pointer(0))
            ci = c[1] * W + c[0]
            v = p.u32(0)
            if v == 1:
                if ci in pearls:
                    anomalies['pearl on pearl'] += 1
                if drop_ctx is not None:
                    drop_ctx['spawned'] += 1
                    pearls[ci] = 0
                else:
                    if actor is not None:
                        anomalies['natural spawn inside a turn'] += 1
                    n_nat += 1
                    if big:
                        tile_births[ci] += 1
                    pearls[ci] = 1
            elif v == 0:
                if ci not in pearls:
                    anomalies['remove without pearl'] += 1
                    continue
                nat = pearls.pop(ci)
                if actor is None or actor not in team:
                    anomalies['remove without actor'] += 1
                    continue
                s = side(actor)
                w = 0 if rnd <= 100 else 1 if rnd <= 300 else 2
                eat[s][w] += 1
                if nat:
                    eat_nat[s][w] += 1
                    if big:
                        tile_eat[s][ci] += 1
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
                if i in qid:
                    u = b[0][1] * W + b[0][0]
                    v = h[1] * W + h[0]
                    geo_portal = any(vv == v and via for vv, via in nbr[u])
                    geo_open = any(vv == v and not via for vv, via in nbr[u])
                    by_dir = None
                    if i == actor and t_steps < len(dirs) and 0 <= dirs[t_steps] < 4:
                        nb = nbd[u][dirs[t_steps]]
                        if nb is None or nb[0] != v:
                            anomalies['queen step differs from her action'] += 1
                        else:
                            by_dir = nb[1]
                    elif i == actor:
                        anomalies['queen step without a direction'] += 1
                    if by_dir is None:
                        if geo_portal and geo_open:
                            anomalies['ambiguous portal step'] += 1
                        by_dir = 1 if geo_portal and not geo_open else 0
                    if not geo_portal and not geo_open:
                        anomalies['queen step not on the graph'] += 1
                    if by_dir:
                        qs[qid[i]]['portal_steps'].append(rnd)
                b.appendleft(h)
                if i == actor:
                    t_steps += 1
            while len(b) > 1 and b[-1] != t:
                b.pop()
            if b[-1] != t:
                anomalies['tail mismatch'] += 1
        elif k == 10:
            par, ch, tm = p.i32(0), p.i32(4), p.u16(8)
            if team.get(par) != tm:
                anomalies['split team differs'] += 1
            bodies[par] = deque(replay.point(c) for c in p.pointer(0))
            bodies[ch] = deque(replay.point(c) for c in p.pointer(1))
            team[par] = tm
            team[ch] = tm
        elif k == 11:
            i = p.i32(0)
            reason = p.u16(4)
            b = bodies.get(i)
            if b is None:
                anomalies['death of unknown dragon'] += 1
                continue
            s = side(i)
            if reason == 3:
                headon.setdefault(turn_id, []).append((i, actor))
                if i in qid and i != actor and actor in bodies:
                    fr, alive = friends(i)
                    qh = b[0]
                    qhi = qh[1] * W + qh[0]
                    r = dict(side=s, round=rnd, cross=team[actor] != team[i],
                             other_queen_dead=qs[other[s]]['death'] is not None, mover_is_queen=actor in qid,
                             friends=fr, others_alive=alive, qlen=len(b), mover_len=len(bodies[actor]),
                             mover_len_turn_start=t_len0, mover_steps=t_steps + 1,
                             enemies_alive=sum(1 for z in bodies if team[z] != team[i]))
                    snap = last_q[s]
                    if snap is None or i not in snap[1]:
                        r['no_snapshot'] = True
                    else:
                        srnd, sb = snap
                        r['snap_round'] = srnd
                        r['born_later'] = actor not in sb
                        q0 = sb[i][0]
                        q0i = q0[1] * W + q0[0]
                        occ = set()
                        fr0 = 0
                        own0 = 0
                        en6 = 0
                        for z, bb in sb.items():
                            for c in bb:
                                occ.add(c[1] * W + c[0])
                            if z == i:
                                continue
                            dz = wrapped(q0, bb[0])
                            if team[z] == team[i]:
                                own0 += 1
                                if dz <= 5:
                                    fr0 += 1
                            elif dz <= 6:
                                en6 += 1
                        legal = sorted(set(v for v, via in nbr[q0i] if v not in occ))
                        foes = []
                        for z, bb in sb.items():
                            if team[z] == team[i]:
                                continue
                            dz = wrapped(q0, bb[0])
                            if dz <= 6 or z == actor:
                                dist = bfs(bb[0][1] * W + bb[0][0])
                                foes.append([1 if z == actor else 0, len(bb), dz,
                                             [FAR if dist[v] < 0 else dist[v] for v in legal],
                                             FAR if dist[q0i] < 0 else dist[q0i],
                                             FAR if dist[qhi] < 0 else dist[qhi]])
                        r.update(friends0=fr0, own0=own0, enemies6=en6, n_legal=len(legal), foes=foes,
                                 moved=q0i != qhi, exits=len(nbr[q0i]), qlen0=len(sb[i]))
                    rams.append(r)
            if i in qid and qs[s]['death'] is None:
                hx, hy = b[0]
                u = hy * W + hx
                hit = None
                if reason == 2:
                    dest = None
                    if i == actor and t_steps < len(dirs) and 0 <= dirs[t_steps] < 4:
                        nb = nbd[u][dirs[t_steps]]
                        if nb is not None:
                            dest = (nb[0] % W, nb[0] // W)
                    if dest is not None:
                        owners = [z for z, bb in bodies.items() if z != i and dest in bb]
                        if len(owners) == 1:
                            hit = 'own' if team[owners[0]] == team[i] else 'enemy'
                        else:
                            hit = 'unresolved %d' % len(owners)
                    else:
                        sides = set()
                        for v, via in nbr[u]:
                            c2 = (v % W, v // W)
                            for z, bb in bodies.items():
                                if z != i and c2 in bb:
                                    sides.add('own' if team[z] == team[i] else 'enemy')
                        hit = 'guess ' + '/'.join(sorted(sides))
                qs[s]['death'] = dict(round=rnd, reason=reason, length=len(b), is_actor=i == actor, room=comp[u],
                                      hit=hit, ei=ei, steps_in_turn=t_steps, x=hx, y=hy,
                                      own_alive=sum(1 for z in bodies if z != i and team[z] == team[i]),
                                      enemy_alive=sum(1 for z in bodies if team[z] != team[i]))
            bodies.pop(i)
            drop_ctx = dict(spawned=0, need=(len(b) + 1) // 2)
            drops.append(drop_ctx)

    drop_mismatch = sum(1 for d in drops if d['spawned'] != d['need'])
    final_ok = True
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if team[i] == z]
        st = res.pointer(z)
        if (len(ls), max(ls, default=0), sum(ls)) != (st.i32(0), st.i32(4), st.i32(8)):
            final_ok = False
    bad_groups = 0
    for tid, g in headon.items():
        if len(g) != 2 or g[0][0] == g[0][1] or g[1][0] != g[1][1]:
            bad_groups += 1
    rec.update(last_round=rnd, queen=queen, qs=qs, rams=rams, lone=lone, n_nat=n_nat, eat=eat, eat_nat=eat_nat,
               anomalies=dict(anomalies), drop_mismatch=drop_mismatch, final_ok=final_ok,
               bad_head_on_groups=bad_groups, head_on_groups=len(headon), bad_portals=bad_portals, portals=n_portals,
               q_len0=q_len0, q_room0=q_room0, q_alive_end=dict(us=queen['us'] in bodies, them=queen['them'] in bodies),
               final_alive=dict(us=sum(1 for i in bodies if team[i] == ours), them=sum(1 for i in bodies if team[i] != ours)),
               rooms_le_6=sorted((sz, n // sz) for sz, n in room_sizes.items() if sz <= 6),
               rooms_top=sorted(((sz, n // sz) for sz, n in room_sizes.items()), reverse=True)[:6])
    if big:
        rec.update(snaps=snaps, tiles={str(ci): [n, tile_eat['us'].get(ci, 0), tile_eat['them'].get(ci, 0)]
                                       for ci, n in tile_births.items()})
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
        out = open(P + 'x4-0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'x4-1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'x4-2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'x4-3.jsonl', 'w')
    elif shard == 4:
        out = open(P + 'x4-4.jsonl', 'w')
    elif shard == 5:
        out = open(P + 'x4-5.jsonl', 'w')
    else:
        out = open(P + 'x4-test.jsonl', 'w')
    done = 0
    for k, (gid, folder, meta) in enumerate(games):
        if shard < 6 and k % n != shard:
            continue
        if shard >= 6 and k % 60 != 7:
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
