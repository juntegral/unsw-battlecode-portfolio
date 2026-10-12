#!/usr/bin/env python3
P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
"""Verifier extraction 14b (extract14.py plus the path distance in the turns she is in view, a finer age split and the dragon counts at each meeting; run of 2026-10-07 18:20 KST) for the queue F45 (late wipe-outs and the state at
raw round 100), F44 (early wipe-outs by queen distance; who is the mover in head-on meetings) and F42 (the
sighting rule: her head within 3 columns and rows of a head of the other side).
Own state rebuild from the raw replays; only the byte decoder (battlecode/replay.py) is shared.
Sides in the output: 0 = ours (team 1119), 1 = theirs.
One JSON line per game. Usage: python3 extract14.py <shard> <shards>"""
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


def age_class(a):
    if a is None:
        return 4
    return 0 if a <= 20 else 1 if a <= 50 else 2 if a <= 100 else 3


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
            for d in range(1, 13):
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
    anomalies = Counter()
    for i, (t, cells) in enumerate(dragons):
        bodies[i] = deque(cells)
        team[i] = 0 if t == ours else 1
    queen = [min(i for i in team if team[i] == 0), min(i for i in team if team[i] == 1)]
    qside = {queen[0]: 0, queen[1]: 1}
    spawn_n = [sum(1 for i in team if team[i] == 0), sum(1 for i in team if team[i] == 1)]
    h0, h1 = bodies[queen[0]][0], bodies[queen[1]][0]
    dx = abs(h0[0] - h1[0])
    dy = abs(h0[1] - h1[1])
    qdist = min(dx, W - dx) + min(dy, H - dy)

    qdeath = [None, None]
    lone = [None, None]
    for s in (0, 1):
        lone[s] = dict(turns=0, age=[0] * 5, near6=[0] * 5, near12=[0] * 5, view=0, ageX=[0] * 5, ageY=[0] * 5,
                       n_other=0, n_same=0, zero_same=0, expV=0.0, first=None,
                       h_turns=[0, 0], h_fresh=[0, 0], h_freshnear=[0, 0], viewnear6=0, viewnear12=0, fine=[0] * 4, fine_near6=[0] * 4)
    seen_at = [None, None]
    seenX_at = [None, None]
    seenY_at = [None, None]
    qturns = [0, 0]
    qview = [0, 0]
    alive = [[], []]
    eaten = [[], []]
    total = [[], []]
    cum = [0, 0]
    rounds_seen = []
    meetings = []
    same_team_meetings = 0
    rnd = 0
    started = False
    actor = None

    def snap(r):
        rounds_seen.append(r)
        for s in (0, 1):
            ls = [len(bz) for z, bz in bodies.items() if team[z] == s]
            alive[s].append(len(ls))
            total[s].append(sum(ls))
            eaten[s].append(cum[s])

    def close(a, b):
        ddx = abs(a[0] - b[0])
        if ddx > 3 and W - ddx > 3:
            return False
        ddy = abs(a[1] - b[1])
        return ddy <= 3 or H - ddy <= 3

    for idx, ev in enumerate(root.pointer(3)):
        k = ev.u16(0)
        if k == 12 or k == 2 or k == 3 and False or 5 <= k <= 8:
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
            b = bodies.get(actor)
            if b is None:
                anomalies['turn of a dead dragon'] += 1
                actor = None
                continue
            s = qside.get(actor)
            if s is None:
                continue
            head = b[0]
            heads = [bz[0] for z, bz in bodies.items() if team[z] != s]
            qturns[s] += 1
            inview = False
            for hz in heads:
                if close(head, hz):
                    inview = True
                    break
            if inview:
                seen_at[s] = rnd
                qview[s] += 1
            vx = inview
            if not vx:
                for seg in b:
                    for hz in heads:
                        if close(seg, hz):
                            vx = True
                            break
                    if vx:
                        break
            if vx:
                seenX_at[s] = rnd
            vy = inview
            if not vy:
                for z, bz in bodies.items():
                    if team[z] == s:
                        continue
                    for seg in bz:
                        if close(head, seg):
                            vy = True
                            break
                    if vy:
                        break
            if vy:
                seenY_at[s] = rnd
            if queen[1 - s] in bodies or rnd < 100:
                continue
            f = lone[s]
            if f['first'] is None:
                f['first'] = rnd
            u = head[1] * W + head[0]
            bl = ball(u)
            cu = comp[u]
            md = 13
            n_same = 0
            for hz in heads:
                hu = hz[1] * W + hz[0]
                if comp[hu] == cu:
                    n_same += 1
                d = bl.get(hu)
                if d is not None and d < md:
                    md = d
            ac = age_class(None if seen_at[s] is None else rnd - seen_at[s])
            f['turns'] += 1
            f['age'][ac] += 1
            if md <= 6:
                f['near6'][ac] += 1
            elif md <= 12:
                f['near12'][ac] += 1
            f['view'] += 1 if inview else 0
            if inview:
                if md <= 6:
                    f['viewnear6'] += 1
                elif md <= 12:
                    f['viewnear12'] += 1
            if ac == 0:
                ag = rnd - seen_at[s]
                fc = 0 if ag == 0 else 1 if ag <= 5 else 2 if ag <= 10 else 3
                f['fine'][fc] += 1
                if md <= 6:
                    f['fine_near6'][fc] += 1
            f['ageX'][age_class(None if seenX_at[s] is None else rnd - seenX_at[s])] += 1
            f['ageY'][age_class(None if seenY_at[s] is None else rnd - seenY_at[s])] += 1
            f['n_other'] += len(heads)
            f['n_same'] += n_same
            f['zero_same'] += 1 if n_same == 0 else 0
            f['expV'] += 1 - (1 - min(1.0, 49.0 / N)) ** len(heads)
            hh = 0 if rnd < 300 else 1
            f['h_turns'][hh] += 1
            if ac == 0:
                f['h_fresh'][hh] += 1
                if md <= 6:
                    f['h_freshnear'][hh] += 1
        elif k == 3:
            if p.u32(0) == 0:
                if actor is not None and actor in team:
                    cum[team[actor]] += 1
                else:
                    anomalies['pearl removed outside a turn'] += 1
        elif k == 4:
            pass
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
            while len(b) > 1 and b[-1] != t:
                b.pop()
            if b[-1] != t:
                anomalies['tail mismatch'] += 1
        elif k == 10:
            par, ch, tm = p.i32(0), p.i32(4), p.u16(8)
            sd = 0 if tm == ours else 1
            if par in team and team[par] != sd:
                anomalies['split team differs'] += 1
            bodies[par] = deque(replay.point(c) for c in p.pointer(0))
            bodies[ch] = deque(replay.point(c) for c in p.pointer(1))
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
            if reason == 3 and i != actor and actor is not None and actor in bodies:
                if team[actor] != sd:
                    meetings.append([rnd, team[actor], len(bodies[actor]), len(b), 1 if i in qside else 0,
                                     1 if actor in qside else 0,
                                     sum(1 for z in bodies if team[z] == 0), sum(1 for z in bodies if team[z] == 1)])
                else:
                    same_team_meetings += 1
            s = qside.get(i)
            if s is not None:
                qdeath[s] = dict(round=rnd, reason=reason, was_mover=i == actor, length=len(b),
                                 actor_side=team[actor] if actor is not None and actor in team else -1)
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
                          queen=len(bodies[queen[s]]) if queen[s] in bodies else 0))
    rec.update(last_round=rnd, rounds_ok=rounds_seen == list(range(rnd + 1)), queen=queen, qdeath=qdeath, lone=lone,
               qturns=qturns, qview=qview, alive=alive, eaten=eaten, total=total, meetings=meetings,
               same_team_meetings=same_team_meetings, final=final, spawn_n=spawn_n, qdist=qdist,
               n_comp=len([c for c in comp_size if c > 1]), anomalies=dict(anomalies), final_ok=final_ok,
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
        out = open(P + 'x14b-0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'x14b-1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'x14b-2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'x14b-3.jsonl', 'w')
    elif shard == 4:
        out = open(P + 'x14b-4.jsonl', 'w')
    elif shard == 5:
        out = open(P + 'x14b-5.jsonl', 'w')
    else:
        out = open(P + 'x14b-test.jsonl', 'w')
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
