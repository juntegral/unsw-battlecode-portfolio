"""Scratch (diag-queenkill): queen fates, queen killers and every chance at a queen's head, both sides.
queen   = lowest starting id of a side. Side 0 = the focus team (1119, or 306 for top1), side 1 = its opponent.
chance  = at the start of a dragon's turn the ENEMY QUEEN's head can be entered this turn over tiles free at turn
          start, within free steps ceil(L/4) plus one paid segment a step down to length 2 (d at most ceil(L/4)+L-2,
          plain BFS). A second class (pe above 0) = only with pearls eaten on the way (0-1 search).
          One row per dragon turn. taken = the queen dies head-on in that turn with this dragon as mover.
Writes one JSON line per game to qk_scan-<tag>.jsonl.
Usage: python3 qk_scan.py online <label> <tag> | ladder <shard> <shards> <tag> [limit] | top1 <shard> <shards> <tag> [limit]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAP = 8
ACTS = ('unpaid sprint', 'illegal split', 'no action')


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.adj = []
        self.nxt = []
        for y in range(h):
            for x in range(w):
                row = set()
                four = [-1, -1, -1, -1]
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 1:
                        continue
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.add(dest)
                    four[d] = dest
                self.adj.append(sorted(row))
                self.nxt.append(four)
        self.wins = {}
        self.balls = {}

    def window(self, src):
        s = self.wins.get(src)
        if s is None:
            y, x = divmod(src, self.w)
            s = frozenset(((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4))
            self.wins[src] = s
        return s

    def ball(self, src):
        s = self.balls.get(src)
        if s is None:
            d = {src: 0}
            q = deque([src])
            while q:
                c = q.popleft()
                if d[c] >= CAP:
                    continue
                for t in self.adj[c]:
                    if t not in d:
                        d[t] = d[c] + 1
                        q.append(t)
            s = d
            self.balls[src] = s
        return s


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def scan(path, own_letter, meta, geos):
    root = replay.load(Path(path)).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams, raw = {}, {}, []
    name = ''
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
        elif q and q[0] == 'MAP_NAME':
            name = ' '.join(q[1:])
    key = (w, h, tuple(sorted(raw)))
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    sd = {}

    def side(i):
        s = sd.get(i)
        if s is None:
            s = 0 if teams[i] == own_letter else 1
            sd[i] = s
        return s

    queen = [min(i for i in bodies if side(i) == 0), min(i for i in bodies if side(i) == 1)]
    heads = {}
    hset = [set(), set()]
    occ = Counter()
    alive = [0, 0]
    for i, b in bodies.items():
        heads[b[0]] = i
        hset[side(i)].add(b[0])
        alive[side(i)] += 1
        for c in b:
            occ[c] += 1
    present = set()
    chs = []
    qd = [None, None]
    qlast = [None, None]
    last_row = {}
    series = {}
    sight = [{}, {}]
    dirs = []
    fun = Counter()
    first_seen = [-1, -1]
    seen_n = [0, 0]
    state = dict(rnd=0, actor=None, used=0, ate=0, act=None, split=False, cur=None, victim=None)
    turns = Counter()

    def gap(a, c):
        return torus(a % w, c % w, w) + torus(a // w, c // w, h)

    def longest(s, skip=-1):
        best = 0
        for i, b in bodies.items():
            if i != skip and sd[i] == s and len(b) > best:
                best = len(b)
        return best

    def near(c, s, skip, rad):
        n = 0
        for t in hset[s]:
            if gap(t, c) <= rad and heads[t] != skip:
                n += 1
        return n

    def stand():
        out = []
        for s in (0, 1):
            n = tot = big = 0
            for i, b in bodies.items():
                if side(i) == s:
                    n += 1
                    tot += len(b)
                    big = max(big, len(b))
            out += [n, big, tot, len(bodies.get(queen[s], ()))]
        return out

    def plain(hd, target, budget):
        if budget <= 0:
            return -1
        d = {hd: 0}
        q = deque([hd])
        while q:
            c = q.popleft()
            dc = d[c]
            for t in g.adj[c]:
                if t == target:
                    return dc + 1
                if occ[t] or t in d or dc + 1 >= budget:
                    continue
                d[t] = dc + 1
                q.append(t)
        return -1

    def pearly(hd, target, budget):
        d = {hd: (0, 0)}
        q = deque([hd])
        best = None
        while q:
            c = q.popleft()
            cc, cs = d[c]
            if cs >= CAP:
                continue
            for t in g.adj[c]:
                if t == target:
                    if cc + 1 <= budget and (best is None or (cs + 1, cc + 1) < best):
                        best = (cs + 1, cc + 1)
                    continue
                if occ[t]:
                    continue
                nc = cc if t in present else cc + 1
                if nc > budget - 1:
                    continue
                o = d.get(t)
                if o is not None and o <= (nc, cs + 1):
                    continue
                d[t] = (nc, cs + 1)
                if nc == cc:
                    q.appendleft(t)
                else:
                    q.append(t)
        return best

    def close_turn():
        cur = state['cur']
        if cur is None:
            return
        r_ = cur.get('row')
        if r_ is not None:
            a = cur['actor']
            r_[19] = state['used']
            r_[21] = state['ate']
            r_[22] = int(state['split'])
            en = 1 - cur['s']
            if a in bodies and queen[en] in bodies:
                r_[20] = gap(bodies[a][0], bodies[queen[en]][0])
        sg = cur.get('sight')
        if sg is not None:
            a = cur['actor']
            en = 1 - cur['s']
            if cur['took']:
                o = 'T'
            elif a not in bodies:
                o = 'D'
            elif queen[en] not in bodies:
                o = 'X'
            else:
                g2 = gap(bodies[a][0], bodies[queen[en]][0])
                o = 'C' if g2 < sg[5] else 'S' if g2 == sg[5] else 'F'
            fun[(sg[0], sg[1], sg[2], sg[3], sg[4], o)] += 1
        state['cur'] = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close_turn()
            state['rnd'], state['actor'] = p.i32(0), None
            if state['rnd'] % 50 == 0:
                series[state['rnd']] = stand()
        elif k == 1:
            close_turn()
            actor = p.i32(0)
            rnd = state['rnd']
            state.update(actor=actor, used=0, ate=0, act=None, split=False, victim=None)
            b = bodies[actor]
            s = side(actor)
            en = 1 - s
            L = len(b)
            hd = b[0]
            isq = int(actor == queen[s])
            cur = dict(actor=actor, s=s, L=L, hd=hd, row=None, sight=None, took=False)
            state['cur'] = cur
            turns[(s, min(rnd // 100, 4), min(L, 5), isq)] += 1
            if isq:
                win = g.window(hd)
                qlast[s] = dict(r=rnd, free=sum(1 for t in g.adj[hd] if not occ[t]), L=L,
                                foes={heads[c]: [gap(c, hd), len(bodies[heads[c]])] for c in hset[en] if c in win},
                                own=sum(1 for c in hset[s] if c in win) - 1)
            qe = queen[en]
            qb = bodies.get(qe)
            since_other = since_self = -1
            if qb is not None and gap(hd, qb[0]) <= 6 and qb[0] in g.window(hd):
                for j, when in sight[s].items():
                    if j != actor and rnd - when <= 40 and (since_other < 0 or rnd - when < since_other):
                        since_other = rnd - when
                if actor in sight[s]:
                    since_self = rnd - sight[s][actor]
                if not isq and L <= 4:
                    sight[s][actor] = rnd
                if not isq:
                    fb = (L + 3) // 4 + L - 2
                    dw = plain(hd, qb[0], 8)
                    db = 'R' if 0 < dw <= fb else 'N' if 0 < dw <= 3 else 'M' if 0 < dw <= 6 else 'F'
                    cur['sight'] = [s, min(L, 5), db, 0 if rnd <= 100 else 1 if rnd <= 300 else 2, int(queen[s] in bodies), gap(hd, qb[0])]
                    if first_seen[s] < 0:
                        first_seen[s] = rnd
                    seen_n[s] += 1
            if qb is not None and qb[0] in g.ball(hd):
                th = qb[0]
                free = (L + 3) // 4
                d = plain(hd, th, min(free + L - 2, CAP))
                pe = 0
                if d < 0:
                    got = pearly(hd, th, free + L - 2)
                    if got is not None:
                        d, pe = got[0], got[0] - got[1]
                if d > 0:
                    win = g.window(hd)
                    ov = ev_ = 0
                    for c in win:
                        j = heads.get(c)
                        if j is None or j == actor:
                            continue
                        if sd[j] == s:
                            ov += 1
                        else:
                            ev_ += 1
                    Lq = len(qb)
                    vis = sum(1 for z in qb if z in win)
                    ft = (Lq + 3) // 4
                    mut = 2 if d <= ft else 1 if d <= ft + Lq - 2 else 0
                    oq = bodies.get(queen[s])
                    row = [rnd, s, actor, L, isq, int(L >= longest(s, actor)), d, free, Lq, vis, ov, ev_, alive[s], alive[en],
                           len(oq) if oq is not None else 0, mut, pe, gap(hd, th), 0, 0, -1, 0, 0, -1, -1, -1, -1,
                           near(th, s, actor, 5), near(th, en, qe, 5), longest(s), longest(en), since_other, since_self]
                    # 0 round, 1 side, 2 id, 3 L, 4 mover is a queen, 5 mover is its side's longest, 6 steps d, 7 free steps, 8 her length,
                    # 9 her parts in the mover's 7x7, 10 own heads in view, 11 enemy heads in view, 12 alive own, 13 alive enemy,
                    # 14 own queen length (0 dead), 15 she could hit back (2 free, 1 paid), 16 pearls needed on the way, 17 gap at start,
                    # 18 taken, 19 steps moved, 20 gap after, 21 pearls eaten, 22 split, 23 mover's death reason this turn,
                    # 24 rammed another head (its length), 25 mover dies within 5 rounds: delta, 26 its reason (10+ = not on its turn),
                    # 27 own heads within 5 of her, 28 her side's heads within 5 of her, 29 own longest, 30 enemy longest,
                    # 31 rounds since another own non-queen of 4 or less had her head in its 7x7 at its turn start (-1 none in 40),
                    # 32 rounds since this dragon last had her in view at a turn start (-1 never)
                    chs.append(row)
                    cur['row'] = row
                    last_row[actor] = row
        elif k == 4:
            a = p.pointer(0)
            used_up = p.pointer(1)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            state['act'] = 'timeout' if p.bit(32) or (used_up is not None and used_up.bit(64)) else ACTS[a.u16(0)] if a and a.u16(0) < 3 else 'no action'
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present.add(c)
            else:
                present.discard(c)
                state['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                s = side(i)
                if heads.get(b[0]) == i:
                    del heads[b[0]]
                    hset[s].discard(b[0])
                b.appendleft(hd)
                heads[hd] = i
                hset[s].add(hd)
                occ[hd] += 1
                if i == state['actor']:
                    state['used'] += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s = side(parent)
            state['split'] = True
            for c in bodies[parent]:
                occ[c] -= 1
            if heads.get(bodies[parent][0]) == parent:
                del heads[bodies[parent][0]]
                hset[s].discard(bodies[parent][0])
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
                heads[bodies[i][0]] = i
                hset[side(i)].add(bodies[i][0])
                for c in bodies[i]:
                    occ[c] += 1
            alive[s] += 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            rnd, actor, used, ate, cur = state['rnd'], state['actor'], state['used'], state['ate'], state['cur']
            s = side(i)
            b = bodies[i]
            L = len(b)
            hd = b[0]
            isq = i == queen[s]
            row = cur.get('row') if cur else None
            ql = qlast[s] or {}
            common = dict(r=rnd, L=L, own5=near(hd, s, i, 5), foe5=near(hd, 1 - s, -1, 5), alive=[alive[0], alive[1]],
                          oq=len(bodies.get(queen[1 - s], ())), qfree=ql.get('free', -1), qturn=ql.get('r', -1),
                          big=[longest(0), longest(1)], seenfoes=len(ql.get('foes') or {})) if isq else None
            if reason == 3 and i != actor:
                ms = side(actor)
                L0 = cur['L']
                Ld = len(bodies[actor])
                state['victim'] = dict(vid=i, vs=s, vL=L, vq=int(isq))
                if isq:
                    cur['took'] = cur['took'] or ms != s
                    hit = row is not None and ms != s
                    if hit:
                        row[18] = 1
                    seen = (ql.get('foes') or {}).get(actor)
                    common.update(cause='rammed', enemy=int(ms != s), kid=actor, kL0=L0, kLd=Ld, k=used + 1, free=(L0 + 3) // 4, ate=ate,
                                  paid=L0 + ate - Ld, d=row[6] if hit else -1, pe=row[16] if hit else -1,
                                  kq=int(actor == queen[ms]), ktop=int(L0 >= longest(ms, actor)),
                                  seen=seen[0] if seen else -1, kgap=gap(cur['hd'], hd))
                    qd[s] = common
                elif row is not None and side(actor) != s:
                    row[24] = L
            elif reason == 3 and i == actor:
                if isq:
                    v = state['victim'] or {}
                    common.update(cause='she rammed', enemy=int(v.get('vs') != s), kid=v.get('vid'), vL=v.get('vL'), vq=v.get('vq'),
                                  k=used + 1, L0=cur['L'])
                    qd[s] = common
                if row is not None:
                    row[23] = 3
            else:
                if i == actor and row is not None:
                    row[23] = reason
                if isq:
                    cause = ('wall', 'own body', 'another body', 'head-on', state['act'] or 'no action')[reason] if reason <= 4 else 'other'
                    owner = -1
                    olen = -1
                    if reason == 2 and i == actor and used < len(dirs):
                        dest = g.nxt[hd][dirs[used]]
                        for z, zb in bodies.items():
                            if z != i and dest in zb:
                                owner = int(side(z) != s)
                                olen = len(zb)
                    common.update(cause=cause, enemy=owner, olen=olen, k=used + 1, mine=int(i == actor))
                    qd[s] = common
            lr = last_row.pop(i, None)
            if lr is not None and lr is not row and rnd - lr[0] <= 5:
                lr[25] = rnd - lr[0]
                lr[26] = reason if i == actor else 10 + reason
            if heads.get(hd) == i:
                del heads[hd]
                hset[s].discard(hd)
            for c in b:
                occ[c] -= 1
            bodies.pop(i)
            alive[s] -= 1
    close_turn()
    final = stand()
    fin = root.pointer(4)
    winner = 'AB'[fin.u16(6)] if fin.u16(4) == 1 else None
    win = None if winner is None else int(winner == own_letter)
    decided = ('elimination' if not final[0] or not final[4] else 'queen' if final[3] != final[7] else
               'longest' if final[1] != final[5] else 'total' if final[2] != final[6] else 'draw')
    out = dict(meta)
    out.update(map=name, w=w, h=h, cells=w * h, win=win, decided=decided, last_round=state['rnd'], queen=queen, final=final,
               qd=qd, chs=chs, series=series, turns=[[a, b_, c, d_, n] for (a, b_, c, d_), n in sorted(turns.items())],
               bots=[root.text(1), root.text(2)], fun=[list(key_) + [n] for key_, n in sorted(fun.items())],
               first_seen=first_seen, seen_n=seen_n)
    return out


def jobs_online(label):
    folder = Path('data/online/smoke') / (label + '-new')
    out = []
    for mp in sorted(folder.glob('game-*.json')):
        m = json.loads(mp.read_text())
        rp = folder / ('M%d.replay' % m['id'])
        if not rp.exists() or m.get('status') != 'completed':
            continue
        own = 'A' if m['teamAId'] == 1119 else 'B'
        opp = 'B' if own == 'A' else 'A'
        out.append((str(rp), own, dict(src='online', label=label, game=m['id'], opp=m['team' + opp + 'Name'],
                                       rating=m.get('team' + opp + 'Elo'), meta_winner=m.get('winner'), own=own)))
    return out


def jobs_rows(src, shard, shards, limit):
    f = 'data/analysis/ladder/dossier/per-game.jsonl' if src == 'ladder' else 'data/analysis/ladder/dossier/target/per-game-top1.jsonl'
    every = [json.loads(x) for x in Path(f).read_text().splitlines() if x.strip()]
    rows = sorted((r for r in every if r['relation'] == 'us'), key=lambda r: r['game'])
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[:limit]
    opp = {r['game']: r['team'] for r in every if r['relation'] == 'them'}
    return [(r['replay'], r['our_side'], dict(src=src, label=src, game=r['game'], opp=opp.get(r['game']), rating=r['opponent_rating'],
                                              row_result=r['our_result'], row_ended=r['ended_by'], own=r['our_side'],
                                              row_final=r['final_reconstructed'])) for r in rows]


def emit(tag, body):
    if tag == 'sr51':
        Path(OUT + 'qk_scan-sr51.jsonl').write_text(body)
    elif tag == 'm1':
        Path(OUT + 'qk_scan-m1.jsonl').write_text(body)
    elif tag == 'm2':
        Path(OUT + 'qk_scan-m2.jsonl').write_text(body)
    elif tag == 'm3':
        Path(OUT + 'qk_scan-m3.jsonl').write_text(body)
    elif tag == 'b1':
        Path(OUT + 'qk_scan-b1.jsonl').write_text(body)
    elif tag == 'b2':
        Path(OUT + 'qk_scan-b2.jsonl').write_text(body)
    elif tag == 'b3':
        Path(OUT + 'qk_scan-b3.jsonl').write_text(body)
    elif tag == 'L0':
        Path(OUT + 'qk_scan-L0.jsonl').write_text(body)
    elif tag == 'L1':
        Path(OUT + 'qk_scan-L1.jsonl').write_text(body)
    elif tag == 'L2':
        Path(OUT + 'qk_scan-L2.jsonl').write_text(body)
    elif tag == 'T0':
        Path(OUT + 'qk_scan-T0.jsonl').write_text(body)
    elif tag == 'T1':
        Path(OUT + 'qk_scan-T1.jsonl').write_text(body)
    elif tag == 'T2':
        Path(OUT + 'qk_scan-T2.jsonl').write_text(body)
    elif tag == 'sr51f':
        Path(OUT + 'qk_scanf-sr51.jsonl').write_text(body)
    elif tag == 'm1f':
        Path(OUT + 'qk_scanf-m1.jsonl').write_text(body)
    elif tag == 'm2f':
        Path(OUT + 'qk_scanf-m2.jsonl').write_text(body)
    elif tag == 'm3f':
        Path(OUT + 'qk_scanf-m3.jsonl').write_text(body)
    elif tag == 'b1f':
        Path(OUT + 'qk_scanf-b1.jsonl').write_text(body)
    elif tag == 'L0f':
        Path(OUT + 'qk_scanf-L0.jsonl').write_text(body)
    elif tag == 'L1f':
        Path(OUT + 'qk_scanf-L1.jsonl').write_text(body)
    elif tag == 'L2f':
        Path(OUT + 'qk_scanf-L2.jsonl').write_text(body)
    elif tag == 'T0f':
        Path(OUT + 'qk_scanf-T0.jsonl').write_text(body)
    elif tag == 'T1f':
        Path(OUT + 'qk_scanf-T1.jsonl').write_text(body)
    elif tag == 'T2f':
        Path(OUT + 'qk_scanf-T2.jsonl').write_text(body)
    else:
        Path(OUT + 'qk_scan-test.jsonl').write_text(body)


def main():
    src = sys.argv[1]
    if src == 'online':
        jobs = jobs_online(sys.argv[2])
        tag = sys.argv[3]
    else:
        jobs = jobs_rows(src, int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[5]) if len(sys.argv) > 5 else 0)
        tag = sys.argv[4]
    geos, bad, out = {}, [], []
    for n, (path, own, meta) in enumerate(jobs):
        try:
            rec = scan(path, own, meta, geos)
            if 'row_final' in meta:
                f, want = rec['final'], meta['row_final']
                assert [f[0], f[1], f[2], f[3]] == [want['alive'], want['longest'], want['total'], want['queen_length']], (f, want)
                assert (rec['win'] == 1) == (meta['row_result'] == 'win'), (rec['win'], meta['row_result'])
                del rec['row_final']
            if meta.get('meta_winner') in ('a', 'b'):
                assert (rec['win'] == 1) == (meta['meta_winner'].upper() == own), (rec['win'], meta)
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((meta['game'], repr(e)[:300]))
        if n % 10 == 9:
            print(n + 1, len(jobs), len(bad), flush=True)
    emit(tag, '\n'.join(out) + '\n')
    print('done', src, tag, len(out), 'bad', bad, flush=True)


main()
