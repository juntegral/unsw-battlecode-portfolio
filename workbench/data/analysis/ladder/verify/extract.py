#!/usr/bin/env python3
"""Verifier extraction. Own state rebuild from the raw replays (only the byte decoder is shared);
one JSON line per game. Usage: python3 extract.py <shard> <shards>"""
import sys, json, hashlib
from pathlib import Path
from collections import deque, Counter
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path('../battlecode').resolve()))
import replay

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/verify/'
MAIN = ('18066', '18068', '18504', '18570')
US = 1119
LADDER = Path('data/online/ladder')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
MARKS = (50, 100, 150, 200, 300)


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
    name = None
    dragons = []
    edges = {}
    conflicts = 0
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'MAP_NAME':
            name = ' '.join(q[1:])
        elif q[0] == 'DRAGON':
            n = int(q[2])
            dragons.append((int(q[1]), [(int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(n)]))
        elif q[0] == 'EDGE':
            e, kind, pid = int(q[1]), int(q[2]), int(q[3])
            c = fold(W, H, e)
            if c is None:
                continue
            if c in edges and edges[c] != (kind, pid):
                conflicts += 1
                if kind <= edges[c][0]:
                    continue
            edges[c] = (kind, pid)
    return W, H, name, dragons, edges, conflicts


def build_step(W, H, edges):
    by_pid = {}
    for e, (kind, pid) in edges.items():
        if kind == 2:
            by_pid.setdefault(pid, []).append(e)
    partner = {}
    bad = 0
    for pid, es in by_pid.items():
        if len(es) == 2:
            partner[es[0]] = es[1]
            partner[es[1]] = es[0]
        else:
            bad += 1

    def step(x, y, d):
        e = edge_of(W, H, x, y, d)
        kind, pid = edges.get(e, (0, -1))
        if kind == 1:
            return None
        if kind == 2 and e in partner:
            row, px = divmod(partner[e], W + 1)
            py = row // 2
            flat = row % 2 == 0
            if flat and d == 0:
                return (px, (py - 1) % H)
            if flat and d == 2:
                return (px, py % H)
            if not flat and d == 1:
                return (px % W, py)
            if not flat and d == 3:
                return ((px - 1) % W, py)
            return 'turn'
        return ((x + STEP[d][0]) % W, (y + STEP[d][1]) % H)
    return step, bad, len(by_pid)


def nearest(nbr, heads, pset):
    if not heads or not pset:
        return None
    seen = set(heads)
    for h in seen:
        if h in pset:
            return 0
    frontier = list(seen)
    dist = 0
    while frontier:
        dist += 1
        nxt = []
        for c in frontier:
            for t in nbr[c]:
                if t in seen:
                    continue
                if t in pset:
                    return dist
                seen.add(t)
                nxt.append(t)
        frontier = nxt
    return None


def process(path, meta, battle):
    root = replay.load(path).root()
    bots = (root.text(1), root.text(2))
    if meta['teamAId'] == US:
        ours = 0
    elif meta['teamBId'] == US:
        ours = 1
    else:
        raise ValueError('team 1119 is on neither side')
    text = root.text(0)
    W, H, name, dragons, edges, conflicts = read_layout(text)
    sig_src = json.dumps([W, H, sorted((e, k, p) for e, (k, p) in edges.items() if k), sorted(c for t, c in dragons)])
    start = [sum(1 for t, c in dragons if t == ours), sum(1 for t, c in dragons if t != ours)]
    rec = dict(game=meta['id'], battle=battle, map=meta['mapName'], map_in_replay=name, our_side='AB'[ours],
               bot=bots[ours], other_bot=bots[1 - ours], main=bots[ours] in MAIN, completedAt=meta['completedAt'],
               meta_winner=meta.get('winner'), W=W, H=H, layout=hashlib.sha1(sig_src.encode()).hexdigest()[:12],
               start=dict(us=start[0], them=start[1]), edge_conflicts=conflicts)
    res = root.pointer(4)
    winner = res.u16(6) if res.u16(4) == 1 else None
    rec.update(end_reason=res.u16(2), winner=None if winner is None else 'AB'[winner], win=winner == ours)
    if not rec['main']:
        return rec

    bodies = {}
    team = {}
    for i, (t, cells) in enumerate(dragons):
        bodies[i] = deque(cells)
        team[i] = t

    def side(i):
        return 'us' if team[i] == ours else 'them'
    queen = dict(us=min(i for i in team if team[i] == ours), them=min(i for i in team if team[i] != ours))
    step, bad_portals, n_portals = build_step(W, H, edges)
    nbr = {}
    turn_portals = 0
    for x in range(W):
        for y in range(H):
            reach = []
            for d in range(4):
                t = step(x, y, d)
                if t == 'turn':
                    turn_portals += 1
                elif t is not None:
                    reach.append(t)
            nbr[(x, y)] = reach

    rnd = 0
    started = False
    first_round = None
    round_jumps = 0
    actor = None
    dirs = []
    used = 0
    turn_id = 0
    pearls = {}
    drop_ctx = None
    eats = dict(us=Counter(), them=Counter())
    eat_origin = dict(us=Counter(), them=Counter())
    turns = Counter()
    splits = Counter()
    all_deaths = []
    death_counts = dict(us=Counter(), them=Counter())
    queen_death = dict(us=None, them=None)
    headon = {}
    marks = {}
    partb = {}
    curve = []
    anomalies = Counter()
    stepcheck = [0, 0, 0]
    births_nat = 0
    alive = dict(us=start[0], them=start[1])

    def close_round(r):
        if r <= 200:
            curve.append([r, alive['us'], alive['them']])
        if r in MARKS:
            marks[str(r)] = {s: dict(alive=sum(1 for i in bodies if side(i) == s),
                                     total=sum(len(b) for i, b in bodies.items() if side(i) == s),
                                     pearls=sum(v for k, v in eats[s].items() if k <= r)) for s in ('us', 'them')}
        if r <= 50:
            pset = set(pearls)
            row = [None, None, 0, 0, len(pset)]
            for z, s in enumerate(('us', 'them')):
                heads = [bodies[i][0] for i in bodies if side(i) == s]
                row[z] = nearest(nbr, heads, pset)
                row[2 + z] = len(heads)
            partb[str(r)] = row

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
                if new != rnd + 1:
                    round_jumps += 1
            else:
                first_round = new
            started = True
            rnd = new
            actor = None
            turn_id += 1
        elif k == 1:
            actor = p.i32(0)
            dirs = []
            used = 0
            turn_id += 1
            if actor in team:
                turns[side(actor)] += 1
            else:
                anomalies['turn of unknown dragon'] += 1
        elif k == 4:
            a = p.pointer(0)
            dirs = []
            used = 0
            if p.i32(0) != actor:
                anomalies['action by non actor'] += 1
            if a is not None and a.u16(0) == 0:
                lst = a.pointer(0)
                if lst is not None:
                    dirs = list(lst)
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
                    pr = dict(side=d['side'], round=rnd, eat_round=None, eater=None)
                    d['pearls'].append(pr)
                    pearls[c] = pr
                else:
                    if actor is not None:
                        anomalies['natural spawn inside a turn'] += 1
                    pearls[c] = None
                    births_nat += 1
            elif v == 0:
                if c not in pearls:
                    anomalies['remove without pearl'] += 1
                    continue
                pr = pearls.pop(c)
                if actor is None or actor not in team:
                    anomalies['remove without actor'] += 1
                    continue
                if actor not in bodies:
                    anomalies['remove by dead actor'] += 1
                s = side(actor)
                eats[s][rnd] += 1
                if pr is None:
                    eat_origin[s]['natural'] += 1
                else:
                    eat_origin[s]['drop'] += 1
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
                if i == actor and used < len(dirs) and dirs[used] < 4:
                    pred = step(b[0][0], b[0][1], dirs[used])
                    stepcheck[0] += 1
                    if pred != h:
                        stepcheck[1] += 1
                    if ((b[0][0] + STEP[dirs[used]][0]) % W, (b[0][1] + STEP[dirs[used]][1]) % H) != h:
                        stepcheck[2] += 1
                    used += 1
                else:
                    anomalies['move without direction'] += 1
                b.appendleft(h)
            while len(b) > 1 and b[-1] != t:
                b.pop()
            if b[-1] != t:
                anomalies['tail mismatch'] += 1
        elif k == 10:
            par, ch, tm = p.i32(0), p.i32(4), p.u16(8)
            if ch in team:
                anomalies['child id reused'] += 1
            if team.get(par) != tm:
                anomalies['split team differs'] += 1
            bodies[par] = deque(replay.point(c) for c in p.pointer(0))
            bodies[ch] = deque(replay.point(c) for c in p.pointer(1))
            team[par] = tm
            team[ch] = tm
            splits[side(par)] += 1
            alive[side(par)] += 1
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
                     spawned=0, pearls=[], alive_us=alive['us'], alive_them=alive['them'])
            alive[s] -= 1
            death_counts[s][str(reason)] += 1
            all_deaths.append(d)
            if i == queen[s]:
                if queen_death[s] is None:
                    queen_death[s] = dict(round=rnd, reason=reason, length=len(b))
                else:
                    anomalies['queen died twice'] += 1
            if reason == 3:
                headon.setdefault(turn_id, []).append(d)
            drop_ctx = d
    close_round(rnd)

    drop_mismatch = sum(1 for d in all_deaths if d['spawned'] != (d['length'] + 1) // 2)
    final_ok = True
    for z in (0, 1):
        ls = [len(b) for i, b in bodies.items() if team[i] == z]
        st = res.pointer(z)
        if (len(ls), max(ls, default=0), sum(ls)) != (st.i32(0), st.i32(4), st.i32(8)):
            final_ok = False
    if alive['us'] != sum(1 for i in bodies if side(i) == 'us') or alive['them'] != sum(1 for i in bodies if side(i) == 'them'):
        anomalies['alive counter drift'] += 1

    meetings = []
    same_team = 0
    for tid, ds in headon.items():
        if len(ds) != 2:
            anomalies['head-on group of %d' % len(ds)] += 1
            continue
        if ds[0]['side'] == ds[1]['side']:
            same_team += 1
            continue
        m = dict(round=ds[0]['round'], actor_side=side(ds[0]['actor']) if ds[0]['actor'] in team else None,
                 alive_us=ds[0]['alive_us'], alive_them=ds[0]['alive_them'], len={}, drop={}, w15={}, later={}, never={}, censored={})
        for d in ds:
            s = d['side']
            m['len'][s] = d['length']
            m['drop'][s] = d['spawned']
            w = dict(us=0, them=0)
            later = 0
            never = 0
            censored = 0
            for pr in d['pearls']:
                if pr['eat_round'] is None:
                    if rnd - pr['round'] < 15:
                        censored += 1
                    else:
                        never += 1
                elif pr['eat_round'] - pr['round'] <= 15:
                    w[pr['eater']] += 1
                else:
                    later += 1
            m['w15'][s] = w
            m['later'][s] = later
            m['never'][s] = never
            m['censored'][s] = censored
        meetings.append(m)

    def window(c, lo, hi):
        return sum(v for k, v in c.items() if lo <= k <= hi)
    rec.update(last_round=rnd, first_round=first_round, round_jumps=round_jumps, queen=queen, queen_death=queen_death,
               marks=marks, curve=curve, partb=partb,
               pearls_0_100=dict(us=window(eats['us'], 0, 100), them=window(eats['them'], 0, 100)),
               pearls_all=dict(us=sum(eats['us'].values()), them=sum(eats['them'].values())),
               eat_origin=dict(us=dict(eat_origin['us']), them=dict(eat_origin['them'])),
               turns=dict(turns), splits=dict(splits), deaths=dict(us=dict(death_counts['us']), them=dict(death_counts['them'])),
               meetings=meetings, same_team_head_on=same_team, anomalies=dict(anomalies), drop_mismatch=drop_mismatch,
               final_ok=final_ok, stepcheck=stepcheck, bad_portals=bad_portals, portals=n_portals, turn_portals=turn_portals,
               births_natural=births_nat, final_alive=dict(alive))
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
        out = open(P + 'shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'shard3.jsonl', 'w')
    else:
        out = open(P + 'shard-test.jsonl', 'w')
    done = 0
    for k, (gid, folder, meta) in enumerate(games):
        if shard < 4 and k % n != shard:
            continue
        if shard >= 4 and k >= n:
            break
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
