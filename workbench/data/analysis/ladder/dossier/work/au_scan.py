"""Scratch (diag-australia): one JSON line per main game with head-on meetings in context, adjacent-head chances,
25-round bins and snapshots, deaths of long dragons. Reads replays only.
Usage: python3 data/analysis/ladder/dossier/work/au_scan.py <shard> <shards>   (writes au_ev-<shard>.jsonl here)"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

WORK = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
OUT0 = Path(WORK + 'au_ev-0.jsonl')
OUT1 = Path(WORK + 'au_ev-1.jsonl')
OUT2 = Path(WORK + 'au_ev-2.jsonl')
OUT3 = Path(WORK + 'au_ev-3.jsonl')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAUSES = ('wall', 'own', 'other', 'mover', 'hit', 'noact')


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.moves = []
        for y in range(h):
            for x in range(w):
                row = []
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.append((kind, dest))
                self.moves.append(row)
        self.adj = [sorted({dest for kind, dest in row if kind != 1}) for row in self.moves]
        self.wins = {}

    def near(self, src, cap):
        d = {src: 0}
        q = deque([src])
        while q:
            c = q.popleft()
            if d[c] >= cap:
                continue
            for t in self.adj[c]:
                if t not in d:
                    d[t] = d[c] + 1
                    q.append(t)
        return d

    def window(self, src):
        s = self.wins.get(src)
        if s is None:
            y, x = divmod(src, self.w)
            s = frozenset(((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4))
            self.wins[src] = s
        return s


def lclass(n):
    return 0 if n <= 4 else 1


def scan(row, geos):
    path = Path('data/online/ladder') / str(row['battle']) / ('M%d.replay' % row['game'])
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
    key = row['map_key']
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    ours = row['our_side']
    side = lambda i: 'u' if teams[i] == ours else 't'
    queens = {side(0): 0, side(1): 1}
    heads = {b[0]: i for i, b in bodies.items()}
    present = {}
    nb = 20
    bins = {s: [dict(en=0, ed=0, sp=0, d={c: 0 for c in CAUSES}, dl={c: 0 for c in CAUSES},
                     opp=[0, 0], took=[0, 0], oppw=[0, 0], declhit=[0, 0], turns=0) for _ in range(nb)] for s in 'ut'}
    snaps, hos, bigs = [], [], []
    last = {}
    cur = None
    pend = {}
    turn_deaths = []
    rnd, actor, started = 0, None, False
    dirs, used, nact = [], 0, None

    def snapshot(n):
        if n % 25 and n != row['last_round']:
            return
        rec = [n]
        for s in 'ut':
            ls = sorted(((len(b), i) for i, b in bodies.items() if side(i) == s), reverse=True)
            hist = [sum(1 for L, i in ls if L == 2), sum(1 for L, i in ls if L == 3), sum(1 for L, i in ls if L == 4),
                    sum(1 for L, i in ls if 5 <= L <= 7), sum(1 for L, i in ls if L >= 8)]
            rec.append([len(ls), sum(L for L, i in ls), ls[0][0] if ls else 0, ls[0][1] if ls else -1,
                        len(bodies.get(queens[s], ())), hist, ls[1][0] if len(ls) > 1 else 0])
        snaps.append(rec)

    def finish():
        nonlocal cur
        hs = [d for d in turn_deaths if d['reason'] == 3]
        if len(hs) == 2:
            m = hs[0] if hs[0]['id'] == actor else hs[1]
            v = hs[1] if hs[0]['id'] == actor else hs[0]
            lv = last.get(v['id'])
            m0 = cur['head'] if cur else m['head']
            dm = g.near(m0, 8)
            ev = dict(r=rnd, ms=m['side'], cross=int(m['side'] != v['side']), Lm=m['len'], Lv=v['len'],
                      mq=int(m['q']), vq=int(v['q']), req=len(dirs), k=used + 1, free=(m['len'] + 3) // 4,
                      dafter=dm.get(v['head']), dbefore=None, vis=None, vate=None, vsteps=None, vr=None,
                      mtop=int(m['top']), vtop=int(v['top']), vsecond=v['rank'], mrank=m['rank'],
                      drop=0, eat={'u': 0, 't': 0}, tile=v['head'],
                      near_m=sum(1 for c, i in heads.items() if side(i) == m['side'] and dm.get(c, 99) <= 5),
                      near_v=sum(1 for c, i in heads.items() if side(i) == v['side'] and dm.get(c, 99) <= 5),
                      vpearl=int(any(t in present for t in g.adj[v['head']])),
                      decl=int(m['id'] in pend.get(v['id'], ())))
            if lv is not None:
                ev.update(dbefore=dm.get(lv['h0']), vis=int(m0 in g.window(lv['h0'])), vate=lv['ate'], vsteps=lv['steps'], vr=lv['r'],
                          vadjp=lv['adjp'])
            hos.append(ev)
            for pr in cur['drops'] if cur else ():
                pr['ho'] = ev
                ev['drop'] += 1
            if ev['cross'] and ev['decl'] and rnd <= 499:
                bins[v['side']][min(rnd // 25, nb - 1)]['declhit'][lclass(v['len'])] += 1
        turn_deaths.clear()
        if cur is not None:
            c = cur
            last[c['id']] = dict(h0=c['head'], r=c['r'], ate=c['ate'], steps=c['steps'], adjp=c['adjp'])
            if c['opp']:
                b = bins[c['side']][min(c['r'] // 25, nb - 1)]
                z = lclass(c['L'])
                b['opp'][z] += 1
                b['took'][z] += int(c['took'])
                b['oppw'][z] += int(c['oppw'])
            cur = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            finish()
        if k == 0:
            if started:
                snapshot(rnd)
            started = True
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            dirs, used = [], 0
            s = side(actor)
            head = bodies[actor][0]
            L = len(bodies[actor])
            adj_en = [heads[t] for kind, t in g.moves[head] if kind != 1 and t in heads and side(heads[t]) != s]
            pend[actor] = set(adj_en)
            worth = any(len(bodies[e]) >= max(5, L + 2) for e in adj_en)
            cur = dict(id=actor, side=s, head=head, r=rnd, L=L, ate=0, steps=0, drops=[], opp=bool(adj_en), took=False, oppw=worth,
                       adjp=int(any(t in present for t in g.adj[head])))
            bins[s][min(rnd // 25, nb - 1)]['turns'] += 1
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                pr = dict(b=rnd, o='n' if actor is None else 'd', ho=None)
                present[c] = pr
                if actor is not None and cur is not None:
                    cur['drops'].append(pr)
            else:
                pr = present.pop(c)
                s = side(actor)
                b = bins[s][min(rnd // 25, nb - 1)]
                b['en' if pr['o'] == 'n' else 'ed'] += 1
                if pr['ho'] is not None and rnd - pr['b'] <= 15:
                    pr['ho']['eat'][s] += 1
                if cur is not None:
                    cur['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            moved = b[0] != hd
            if moved:
                if heads.get(b[0]) == i:
                    del heads[b[0]]
                b.appendleft(hd)
                heads[hd] = i
            while len(b) > 1 and b[-1] != tl:
                b.pop()
            if moved and i == actor:
                used += 1
                if cur is not None:
                    cur['steps'] += 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s = side(parent)
            bins[s][min(rnd // 25, nb - 1)]['sp'] += 1
            if heads.get(bodies[parent][0]) == parent:
                del heads[bodies[parent][0]]
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
                heads[bodies[i][0]] = i
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            L = len(bodies[i])
            cause = ('wall', 'own', 'other', 'mover' if i == actor else 'hit', 'noact')[reason]
            ls = sorted((len(b) for j, b in bodies.items() if side(j) == s), reverse=True)
            d = dict(id=i, side=s, reason=reason, len=L, head=bodies[i][0], q=i == queens[s], top=L == ls[0], rank=ls.index(L))
            turn_deaths.append(d)
            b = bins[s][min(rnd // 25, nb - 1)]
            b['d'][cause] += 1
            b['dl'][cause] += L
            if cur is not None and i == actor and reason == 3:
                cur['took'] = True
            if L >= 8:
                bigs.append([rnd, s, L, cause, int(d['top'])])
            if heads.get(bodies[i][0]) == i:
                del heads[bodies[i][0]]
            bodies.pop(i)
    finish()
    snapshot(rnd)
    fin = row['final']
    for s, name in (('u', 'us'), ('t', 'them')):
        assert sum(side(i) == s for i in bodies) == fin[name]['alive'], (row['game'], s)
    for e in hos:
        e.pop('tile', None)
    return dict(game=row['game'], battle=row['battle'], layout=key, w=w, h=h, result=row['result'], ended=row['ended_by'],
                rating=row['opponent_rating'], last=rnd, final=fin, snaps=snaps, bins=bins, hos=hos, bigs=bigs)


def main():
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    only = sys.argv[3] if len(sys.argv) > 3 else None
    rows = json.loads(Path('data/analysis/ladder/dossier/input-snapshot.json').read_text())['rows']
    rows = sorted(rows, key=lambda r: r['game'])
    if only:
        rows = [r for r in rows if r['map_key'] == only][:2]
        geos = {}
        for r in rows:
            out = scan(r, geos)
            print(json.dumps(out)[:3000])
        return
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    geos = {}
    if shard == 0:
        f = open(OUT0, 'w')
    elif shard == 1:
        f = open(OUT1, 'w')
    elif shard == 2:
        f = open(OUT2, 'w')
    else:
        f = open(OUT3, 'w')
    for n, r in enumerate(rows):
        f.write(json.dumps(scan(r, geos), separators=(',', ':')) + '\n')
        if n % 20 == 19:
            print(shard, n + 1, len(rows), flush=True)
    f.close()
    print('done', shard, len(rows))


main()
