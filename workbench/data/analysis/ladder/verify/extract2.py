#!/usr/bin/env python3
"""Verifier extraction 2 (run of 2026-10-07 03:25 KST). Own state rebuild from the raw replays; only the
byte decoder (battlecode/replay.py) is shared. One JSON line per game, main and v31 games in full.
Usage: python3 extract2.py <shard> <shards>"""
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
MARKS = (50, 100, 200, 300)


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
    start = [sum(1 for t, c in dragons if t == ours), sum(1 for t, c in dragons if t != ours)]
    code = 'main' if bots[ours] in MAIN else 'v31' if bots[ours] in OLD else 'other'
    rec = dict(game=meta['id'], battle=battle, map=meta['mapName'], our_side='AB'[ours], bot=bots[ours],
               other_bot=bots[1 - ours], code=code, completedAt=meta['completedAt'], W=W, H=H,
               open_tiles=open_tiles, layout=hashlib.sha1(sig_src.encode()).hexdigest()[:12],
               start=dict(us=start[0], them=start[1]), queen_len0=[len(c) for t, c in dragons][:2])
    res = root.pointer(4)
    winner = res.u16(6) if res.u16(4) == 1 else None
    rec.update(end_reason=res.u16(2), win=winner == ours, drawn=winner is None)
    if code == 'other':
        return rec

    bodies = {}
    team = {}
    for i, (t, cells) in enumerate(dragons):
        bodies[i] = deque(cells)
        team[i] = t

    def side(i):
        return 'us' if team[i] == ours else 'them'
    queen = dict(us=min(i for i in team if team[i] == ours), them=min(i for i in team if team[i] != ours))
    rnd = 0
    started = False
    actor = None
    act = None
    turn_id = 0
    pearls = {}
    drop_ctx = None
    eat = dict(us=Counter(), them=Counter())
    eat_drop = dict(us=Counter(), them=Counter())
    splits = dict(us=[], them=[])
    queen_death = dict(us=None, them=None)
    headon = {}
    r4 = []
    all_deaths = []
    marks = {}
    anomalies = Counter()
    n_deaths = dict(us=Counter(), them=Counter())

    def close_round(r):
        if r in MARKS:
            marks[str(r)] = {s: [sum(1 for i in bodies if side(i) == s),
                                 sum(len(b) for i, b in bodies.items() if side(i) == s)] for s in ('us', 'them')}

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k != 3:
            drop_ctx = None
        if k == 12 or k == 2 or 5 <= k <= 8:
            continue
        p = ev.pointer(0)
        if k == 0:
            new = p.i32(0)
            if started:
                close_round(rnd)
            started = True
            rnd = new
            actor = None
            act = None
            turn_id += 1
        elif k == 1:
            actor = p.i32(0)
            act = 'no action event'
            turn_id += 1
        elif k == 4:
            a = p.pointer(0)
            if p.i32(0) != actor:
                anomalies['action by non actor'] += 1
            act = 'null action' if a is None else 'kind %d' % a.u16(0)
            if p.bit(32):
                act += ' timeout'
        elif k == 3:
            c = replay.point(p.pointer(0))
            v = p.u32(0)
            if v == 1:
                if c in pearls:
                    anomalies['pearl on pearl'] += 1
                if drop_ctx is not None:
                    d = drop_ctx
                    if c not in d['even']:
                        anomalies['drop off even segment'] += 1
                    d['spawned'] += 1
                    pr = dict(round=rnd, eat_round=None, eater=None)
                    d['pearls'].append(pr)
                    pearls[c] = pr
                else:
                    if actor is not None:
                        anomalies['natural spawn inside a turn'] += 1
                    pearls[c] = None
            elif v == 0:
                if c not in pearls:
                    anomalies['remove without pearl'] += 1
                    continue
                pr = pearls.pop(c)
                if actor is None or actor not in team:
                    anomalies['remove without actor'] += 1
                    continue
                s = side(actor)
                eat[s][rnd] += 1
                if pr is not None:
                    eat_drop[s][rnd] += 1
                    pr['eat_round'] = rnd
                    pr['eater'] = s
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
            splits[side(par)].append(rnd)
        elif k == 11:
            i = p.i32(0)
            reason = p.u16(4)
            b = bodies.pop(i, None)
            if b is None:
                anomalies['death of unknown dragon'] += 1
                continue
            b = list(b)
            s = side(i)
            d = dict(id=i, side=s, round=rnd, reason=reason, length=len(b), actor=actor, even=set(b[0::2]),
                     spawned=0, pearls=[])
            n_deaths[s][str(reason)] += 1
            all_deaths.append(d)
            if i == queen[s]:
                if queen_death[s] is None:
                    queen_death[s] = dict(round=rnd, reason=reason, length=len(b), role=None, other_side=None,
                                          is_actor=i == actor, alive_us=sum(1 for z in bodies if side(z) == 'us'),
                                          alive_them=sum(1 for z in bodies if side(z) == 'them'))
                else:
                    anomalies['queen died twice'] += 1
            if reason == 3:
                headon.setdefault(turn_id, []).append(d)
            if reason == 4:
                hx, hy = b[0]
                big = None
                own = None
                foe = None
                n_big = 0
                n_own = 0
                for z, bb in bodies.items():
                    zx, zy = bb[0]
                    dx = abs(zx - hx)
                    dx = min(dx, W - dx)
                    dy = abs(zy - hy)
                    dy = min(dy, H - dy)
                    dist = dx + dy
                    if team[z] == team[i]:
                        n_own += 1
                        if own is None or dist < own:
                            own = dist
                        if len(bb) >= 2 * len(b):
                            n_big += 1
                            if big is None or dist < big:
                                big = dist
                    elif foe is None or dist < foe:
                        foe = dist
                d.update(big=big, own=own, foe=foe, n_big=n_big, n_own=n_own,
                         act=act if i == actor else 'not the actor', is_queen=i == queen[s])
                r4.append(d)
            drop_ctx = d
    close_round(rnd)

    drop_mismatch = sum(1 for d in all_deaths if d['spawned'] != (d['length'] + 1) // 2)
    final_ok = True
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if team[i] == z]
        st = res.pointer(z)
        if (len(ls), max(ls, default=0), sum(ls)) != (st.i32(0), st.i32(4), st.i32(8)):
            final_ok = False

    meetings = []
    same_team = 0
    for tid, ds in headon.items():
        if len(ds) != 2:
            anomalies['head-on group of %d' % len(ds)] += 1
            continue
        victim, mover = ds
        order_ok = victim['id'] != victim['actor'] and mover['id'] == mover['actor']
        for d, role, other in ((victim, 'victim', mover), (mover, 'mover', victim)):
            qd = queen_death[d['side']]
            if d['id'] == queen[d['side']] and qd is not None and qd['round'] == d['round']:
                qd['role'] = role
                qd['other_side'] = other['side']
                qd['other_is_queen'] = other['id'] == queen[other['side']]
                qd['other_length'] = other['length']
        if victim['side'] == mover['side']:
            same_team += 1
            continue
        ln = {victim['side']: victim['length'], mover['side']: mover['length']}
        meetings.append([victim['round'], mover['side'], ln['us'], ln['them'], 1 if order_ok else 0,
                         1 if victim['id'] == queen[victim['side']] else 0, 1 if mover['id'] == queen[mover['side']] else 0])

    rows4 = []
    for d in r4:
        us15 = them15 = later = never = cens = 0
        for pr in d['pearls']:
            if pr['eat_round'] is None:
                if rnd - pr['round'] < 15:
                    cens += 1
                else:
                    never += 1
            elif pr['eat_round'] - pr['round'] <= 15:
                if pr['eater'] == 'us':
                    us15 += 1
                else:
                    them15 += 1
            else:
                later += 1
        rows4.append([d['side'], d['round'], d['length'], d['act'], d['big'], d['own'], d['foe'], d['n_big'], d['n_own'],
                      d['spawned'], us15, them15, later, never, cens, 1 if d['is_queen'] else 0])

    def series(c):
        return [c.get(r, 0) for r in range(rnd + 1)]
    rec.update(last_round=rnd, queen=queen, queen_death=queen_death, marks=marks,
               eat=dict(us=series(eat['us']), them=series(eat['them'])),
               eat_drop=dict(us=series(eat_drop['us']), them=series(eat_drop['them'])),
               splits=splits, meetings=meetings, same_team_head_on=same_team, r4=rows4,
               deaths=dict(us=dict(n_deaths['us']), them=dict(n_deaths['them'])),
               queen_alive_end=dict(us=queen['us'] in bodies, them=queen['them'] in bodies),
               final=dict(us=[sum(1 for i in bodies if side(i) == 'us'), max((len(b) for i, b in bodies.items() if side(i) == 'us'), default=0)],
                          them=[sum(1 for i in bodies if side(i) == 'them'), max((len(b) for i, b in bodies.items() if side(i) == 'them'), default=0)]),
               anomalies=dict(anomalies), drop_mismatch=drop_mismatch, final_ok=final_ok)
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
        out = open(P + 'x2-0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'x2-1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'x2-2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'x2-3.jsonl', 'w')
    elif shard == 4:
        out = open(P + 'x2-4.jsonl', 'w')
    elif shard == 5:
        out = open(P + 'x2-5.jsonl', 'w')
    else:
        out = open(P + 'x2-test.jsonl', 'w')
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
