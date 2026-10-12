"""Scratch (diag-attack): every head-on meeting and every chance to start one, both sides, all rounds, 500 main games.
chance  = at the start of a dragon's turn an enemy head can be entered this turn over free tiles: within its free steps
          (ceil(L/4)) or by paying one segment a step down to length 2 (ceil(L/4)+L-2 steps; search capped at 8 steps).
          One row per (dragon turn, enemy head in reach).
head-on = a death with engine reason 3; the mover is the dragon whose turn it is. Drops of both bodies are followed for 15 rounds.
Writes one line per game to at_scan-<shard>.jsonl. Usage: python3 data/analysis/ladder/dossier/work/at_scan.py <shard> <shards> [limit]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAP = 8


def lclass(L):
    return 0 if L <= 2 else 1 if L == 3 else 2 if L == 4 else 3 if L <= 7 else 4 if L <= 14 else 5


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.adj = []
        for y in range(h):
            for x in range(w):
                row = set()
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
                self.adj.append(sorted(row))
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
            del d[src]
            s = frozenset(d)
            self.balls[src] = s
        return s


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def scan(row, geos):
    path = Path(row['replay'])
    root = replay.load(path).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    key = (row['map_key'], w, h)
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    ours = row['our_side']
    sd = {}

    def side(i):
        s = sd.get(i)
        if s is None:
            s = 0 if teams[i] == ours else 1
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
    present = {}
    expected = deque()
    hos, chs = [], []
    turns = Counter()
    series = {}
    pend = {}
    rnd, actor, used, ate = 0, None, 0, 0
    cur = None
    half = None
    history = defaultdict(lambda: deque(maxlen=2))
    turn_begin = None
    pending_net = []
    def finish_history():
        if actor is not None and actor in bodies and turn_begin is not None:
            history[actor].append((turn_begin, bodies[actor][0]))
    def distance(src, dst):
        if src == dst: return 0
        q = deque([src]); d = {src:0}
        while q:
            c=q.popleft()
            for t in g.adj[c]:
                if t in d: continue
                d[t]=d[c]+1
                if t==dst: return d[t]
                q.append(t)
        return None
    def reach(src, L, targets):
        budget=(L+3)//4+L-2
        d={src:0}; q=deque([src]); found=set()
        while q:
            c=q.popleft()
            for t in g.adj[c]:
                cost=d[c]+int(t not in present)
                if cost>budget: continue
                if t in targets: found.add(t)
                if occ[t]: continue
                if cost>=d.get(t,10**9): continue
                d[t]=cost
                if t in present:q.appendleft(t)
                else:q.append(t)
        return found
    def totals():
        out=[0,0]
        for i,b in bodies.items():out[side(i)]+=len(b)
        return out

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

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            finish_history()
            next_r=p.i32(0)
            for ho in pending_net[:]:
                if next_r > ho['r']+15:
                    ho['net15']=[totals()[z]-ho['pre_total'][z] for z in (ho['ms'],1-ho['ms'])]
                    pending_net.remove(ho)
            rnd, actor, cur = next_r, None, None
            if rnd % 25 == 0:
                series[rnd] = stand()
        elif k == 1:
            finish_history()
            actor = p.i32(0)
            used, ate = 0, 0
            b = bodies[actor]
            s = side(actor)
            L = len(b)
            hd = b[0]
            turn_begin = hd
            turns[(s, (rnd - 1) // 25 if rnd > 0 else 0, lclass(L), int(actor == queen[s]))] += 1
            pend.pop(actor, None)
            cur = dict(hd=hd, L=L, rows={}, ov=-1, ev=-1, lng=0)
            cur['open_start'] = sum(not occ[t] for t in g.adj[hd])
            cur['head_start'] = hd
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                if expected:
                    xy, rec = expected.popleft()
                    assert xy == c
                    present[c] = rec
                else:
                    present[c] = None
            else:
                rec = present.pop(c)
                ate += 1
                if rec is not None and rnd - rec[0]['r'] <= 15:
                    ho, which = rec
                    es = side(actor)
                    ho[which + ('m' if es == ho['ms'] else 'v')] += 1
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
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s = side(parent)
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
            s = side(i)
            b = bodies[i]
            L = len(b)
            hd = b[0]
            rec = None
            if reason == 3 and i != actor:
                ms = side(actor)
                pr = pend.get(i)
                vc = 0
                if pr is not None:
                    for j, r_ in pr.items():
                        r_[23] = 1 if j == actor else 2
                    if actor in pr:
                        vc = 2 if pr[actor][10] <= pr[actor][11] else 1
                mrow = cur['rows'].get(i) if cur else None
                for j, r_ in (cur['rows'].items() if cur else ()):
                    r_[22] = 1 if j == i else 2
                L0 = cur['L']
                half = dict(r=rnd, ms=ms, mid=actor, vid=i, cross=int(ms != s), L0=L0, Ld=len(bodies[actor]), Lv=L,
                            mq=int(actor == queen[ms]), vq=int(i == queen[s]),
                            mtop=int(L0 >= longest(ms, actor)), vtop=int(L >= longest(s, i)),
                            vbig=int(L > longest(ms)), d=mrow[10] if mrow else -1, k=used + 1, free=(L0 + 3) // 4,
                            ate=ate, ov=cur['ov'], ev=cur['ev'], lng=cur['lng'], vis=mrow[16] if mrow else -1,
                            big=mrow[20] if mrow else -1, mut=mrow[21] if mrow else -1, pe=mrow[24] if mrow else -1,
                            m5=near(hd, ms, actor, 5), v5=near(hd, s, i, 5), nm=alive[ms], nv=alive[s], vc=vc,
                            sx=cur['hd'] % w, sy=cur['hd'] // w, x=hd % w, y=hd // w,
                            dm=0, dv=(L + 1) // 2, mm=0, mv=0, vm=0, vv=0)
                half['paid'] = max(0, half['k'] - half['free'])
                if ms != s and ((L0>=5 and 2*L<L0) or (2<=L0<=4 and L==L0)):
                    qbody=bodies.get(queen[ms])
                    qhead=qbody[0] if qbody else None
                    qdist=distance(hd,qhead) if qbody else None
                    hist=list(history[i])
                    towards=[distance(a,qhead)>distance(z,qhead) for a,z in hist] if qbody and all(distance(a,qhead) is not None and distance(z,qhead) is not None for a,z in hist) else []
                    target_big={bb[0] for j,bb in bodies.items() if side(j)==ms and len(bb)>=8}
                    target_q={qhead} if qbody else set()
                    vr=reach(hd,L,target_big|target_q|{cur['head_start'],bodies[actor][0]})
                    half.update(qalive=bool(qbody),qdist=qdist,history_n=len(hist),toward_any=any(towards),toward_both=len(towards)==2 and all(towards),
                        victim_big=bool(vr & target_big),victim_queen=bool(vr & target_q),
                        first_start=cur['head_start'] in vr,first_impact=bodies[actor][0] in vr,
                        open_start=cur['open_start'],open_impact=sum(not occ[t] for t in g.adj[bodies[actor][0]]),
                        sweep3=near(hd,ms,actor,3),pre_total=totals(),net15=None)
                    pending_net.append(half)
                hos.append(half)
                rec = (half, 'v')
            elif reason == 3 and i == actor:
                half['dm'] = (L + 1) // 2
                rec = (half, 'm')
            elif i == actor and cur is not None and cur['rows']:
                for r_ in cur['rows'].values():
                    if r_[22] == 0:
                        r_[22] = 3
            if heads.get(hd) == i:
                del heads[hd]
                hset[s].discard(hd)
            for seg, c in enumerate(b):
                occ[c] -= 1
                if seg % 2 == 0:
                    expected.append((c, rec))
            bodies.pop(i)
            pend.pop(i, None)
            alive[s] -= 1
    for ho in pending_net:
        if rnd>=ho['r']+15:
            ho['net15']=[totals()[z]-ho['pre_total'][z] for z in (ho['ms'],1-ho['ms'])]
    final = stand()
    return dict(game=row['game'], battle=row['battle'], layout=row['map_key'], w=w, h=h, cells=w * h,
                rating=row['opponent_rating'], result=row['result'], ended_by=row['ended_by'],
                queens_at_end=row['queens_at_end'], last_round=rnd, queen=queen, final=final,
                series=series, turns=[[a, b_, c, d_, n] for (a, b_, c, d_), n in sorted(turns.items())], hos=hos, chs=chs)

