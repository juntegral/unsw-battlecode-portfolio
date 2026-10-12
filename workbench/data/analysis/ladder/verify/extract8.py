#!/usr/bin/env python3
"""Verifier extraction 8 (run of 2026-10-07 08:23 KST) for the queue F35 / F37: the two queens. Death round, engine
reason, the board around her head at the start of her fatal turn and at the fatal step, legal first steps at every
queen turn start, lone turns (turn starts with the other queen already dead), her splits, and totals per round.
Own state rebuild from the raw replays; only the byte decoder (battlecode/replay.py) is shared.
One JSON line per game. Usage: python3 extract8.py <shard> <shards>"""
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
    dest, via, bad_portals, n_portals = build_dest(W, H, edges)

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

    alive_a = [[0] * NR, [0] * NR]
    total_a = [[0] * NR, [0] * NR]
    longest_a = [[0] * NR, [0] * NR]
    qlen_a = [[0] * NR, [0] * NR]
    qdeath = [None, None]
    qsplits = [[], []]
    qturns = [[0] * 4, [0] * 4]
    lone_turns = [0, 0]
    lone_by = [[0] * 4, [0] * 4]
    legal_hist = [[[0] * 5 for _ in range(4)], [[0] * 5 for _ in range(4)]]
    zero_turns = [[], []]
    rnd = 0
    actor = None
    T = dict(kind=2, dirs=[], used=0, start=None, round=0, split=0, at_start=None)

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

    def snapshot(r):
        for s in (0, 1):
            ls = [len(b) for i, b in bodies.items() if team[i] == s]
            alive_a[s][r] = len(ls)
            total_a[s][r] = sum(ls)
            longest_a[s][r] = max(ls, default=0)
            qb = bodies.get(queen[s])
            qlen_a[s][r] = len(qb) if qb is not None else 0

    def finish():
        st = T['start']
        if st is not None:
            T['start'] = None
            s, r, nlegal = st
            if nlegal == 0:
                qd = qdeath[s]
                if qd is not None and qd['round'] == r and qd['actor']:
                    out = 'd%d' % qd['reason']
                elif T['split']:
                    out = 'split'
                else:
                    out = 'lived'
                zero_turns[s].append([r, out])

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k == 12 or k == 2 or k == 3 or 5 <= k <= 8:
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
            T['kind'] = 2
            T['dirs'] = []
            T['used'] = 0
            T['split'] = 0
            T['round'] = rnd
            T['at_start'] = None
            if actor not in bodies:
                anomalies['turn of a dead dragon'] += 1
                actor = None
                continue
            s = qside.get(actor)
            if s is None:
                continue
            w = window(rnd)
            qturns[s][w] += 1
            if queen[1 - s] not in bodies:
                lone_turns[s] += 1
                lone_by[s][w] += 1
            cls = look(actor, s)
            nlegal = sum(1 for c in cls if c[0] == 'F')
            legal_hist[s][w][nlegal] += 1
            T['at_start'] = (cls, nlegal, len(bodies[actor]), list(bodies[actor][0]))
            T['start'] = (s, rnd, nlegal)
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
            if par in qside:
                qsplits[qside[par]].append(rnd)
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
                d.update(now_cls=now, now_legal=sum(1 for c in now if c[0] == 'F'), now_head=list(b[0]))
                if is_actor:
                    st = T['at_start']
                    d.update(kind=T['kind'], ndirs=len(T['dirs']), used=T['used'])
                    if st is not None:
                        d.update(start_cls=st[0], start_legal=st[1], start_len=st[2], start_head=st[3])
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
                    d.update(killer=actor, killer_side=team.get(actor) if actor is not None else None,
                             killer_is_queen=(actor in qside) if actor is not None else None)
                qdeath[s] = d
            for c in b:
                ci = c[1] * W + c[0]
                if owner.get(ci) == i:
                    del owner[ci]
                else:
                    anomalies['dead body tile not owned'] += 1
            bodies.pop(i)

    finish()
    snapshot(rnd)
    final_ok = True
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if (team[i] == 0) == (z == ours)]
        st = res.pointer(z)
        if (len(ls), max(ls, default=0), sum(ls)) != (st.i32(0), st.i32(4), st.i32(8)):
            final_ok = False
    own_ok = len(owner) == sum(len(b) for b in bodies.values())
    n = rnd + 1
    rec.update(last_round=rnd, queen=queen, qdeath=qdeath, qsplits=qsplits, qturns=qturns, lone_turns=lone_turns,
               lone_by=lone_by, legal_hist=legal_hist, zero_turns=zero_turns,
               q_alive_end=[queen[0] in bodies, queen[1] in bodies],
               alive=[a[:n] for a in alive_a], total=[a[:n] for a in total_a], longest=[a[:n] for a in longest_a],
               qlen=[a[:n] for a in qlen_a], anomalies=dict(anomalies), final_ok=final_ok, own_ok=own_ok,
               bad_portals=bad_portals, portals=n_portals)
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
        out = open(P + 'x8-0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'x8-1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'x8-2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'x8-3.jsonl', 'w')
    elif shard == 4:
        out = open(P + 'x8-4.jsonl', 'w')
    elif shard == 5:
        out = open(P + 'x8-5.jsonl', 'w')
    else:
        out = open(P + 'x8-test.jsonl', 'w')
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
