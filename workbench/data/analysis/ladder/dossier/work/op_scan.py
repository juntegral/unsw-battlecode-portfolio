# Scratch (diag-opening): one pass over every game of ours (who=O, team 1119, 500 main ladder games) or of rank-1
# (who=R, team 306, 597 games), rounds 0-100, BOTH sides of each game (u = the followed side, t = its opponent).
# One output line per game. Series are sampled at the end of each round 0..60:
#   alive, total length, pearls eaten so far, tiles seen so far (7 by 7 view at each turn start, as the dossier),
#   front = the largest path distance of a head from the side's start (the queen's first head tile),
#   meand = the mean of the same x10, toward = the smallest path distance of a head to the other side's start,
#   spread = mean straight (wrapped) distance between the side's heads x10, qd / qt / ql = the queen's distance from
#   its start, to the other start, and its length (-1 when dead), cd = mean wrapped distance of heads to the centre x10.
# Path distance = steps over open edges and portals on the empty map (bodies ignored).
# Turn table key: window|length class|what is in view|queen -> [turns, splits, steps made, turns with 2+ steps,
#   paid steps, turns with a paid step, free steps beyond the first that were used, free steps beyond the first on offer].
# Usage: python3 data/analysis/ladder/dossier/work/op_scan.py <O|R> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LAST = 60
STOP = 100
FAR = 9999
CAUSES = ('wall', 'own', 'body', 'headon', 'nosplit', 'nopay', 'noact')


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
                        row.add(((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w)
                    else:
                        row.add(((y + dy) % h) * w + (x + dx) % w)
                self.adj.append(sorted(row))
        self.wins, self.dists = {}, {}

    def window(self, c):
        s = self.wins.get(c)
        if s is None:
            y, x = divmod(c, self.w)
            s = tuple(sorted({((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4)}))
            self.wins[c] = s
        return s

    def bfs(self, src):
        d = self.dists.get(src)
        if d is None:
            d = [FAR] * (self.w * self.h)
            d[src] = 0
            q = deque([src])
            while q:
                z = q.popleft()
                for t in self.adj[z]:
                    if d[t] == FAR:
                        d[t] = d[z] + 1
                        q.append(t)
            self.dists[src] = d
        return d

    def cdist(self, c):
        y, x = divmod(c, self.w)
        dx, dy = abs(x - self.w // 2), abs(y - self.h // 2)
        return min(dx, self.w - dx) + min(dy, self.h - dy)

    def mdist(self, a, c):
        ay, ax = divmod(a, self.w)
        cy, cx = divmod(c, self.w)
        dx, dy = abs(ax - cx), abs(ay - cy)
        return min(dx, self.w - dx) + min(dy, self.h - dy)


def lbucket(L):
    return '2' if L <= 2 else '3' if L == 3 else '4' if L == 4 else '5' if L <= 8 else '9'


def wbucket(r):
    return 0 if r <= 10 else 1 if r <= 20 else 2 if r <= 40 else 3


def scan(row, geos):
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    N = w * h
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
    key = (row['layout'], w, h)
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    mine = row['side']
    side = lambda i: 'u' if teams[i] == mine else 't'
    other = dict(u='t', t='u')
    queen = {s: min(i for i in bodies if side(i) == s) for s in 'ut'}
    start = {s: bodies[queen[s]][0] for s in 'ut'}
    dfrom = {s: g.bfs(start[s]) for s in 'ut'}
    cfg = {s: sorted(len(b) for i, b in bodies.items() if side(i) == s) for s in 'ut'}
    events = list(root.pointer(3))

    hg = dict(u=[0] * N, t=[0] * N)
    for i, b in bodies.items():
        hg[side(i)][b[0]] += 1
    pv = [0] * N
    info = {i: dict(s=side(i), born=0, len0=len(b), eat1=None, died=None, cause=None, q=int(i == queen[side(i)]), eats=0, splits=0)
            for i, b in bodies.items()}
    since4 = {i: (0 if len(b) >= 4 else None) for i, b in bodies.items()}
    seen = dict(u=set(), t=set())
    eaten = dict(u=0, t=0)
    contact = dict(u=None, t=None)
    see1 = dict(u=None, t=None)
    names = ('alive', 'total', 'eaten', 'seen', 'front', 'meand', 'toward', 'spread', 'qd', 'qt', 'ql', 'cd')
    series = {s: {n: [] for n in names} for s in 'ut'}
    splits = dict(u=[], t=[])
    turns = dict(u=defaultdict(lambda: [0] * 8), t=defaultdict(lambda: [0] * 8))
    deaths = dict(u=Counter(), t=Counter())
    chk = dict(turns=0, pearls=0, splits=0)
    at100 = {}
    rnd, actor, used, dirs, kind, cur = 0, None, 0, [], 2, None
    started = False

    def sample():
        for s in 'ut':
            o = other[s]
            ids = [i for i in bodies if side(i) == s]
            heads = [bodies[i][0] for i in ids]
            ds = [dfrom[s][c] for c in heads if dfrom[s][c] < FAR]
            dt = [dfrom[o][c] for c in heads if dfrom[o][c] < FAR]
            v = series[s]
            v['alive'].append(len(ids))
            v['total'].append(sum(len(bodies[i]) for i in ids))
            v['eaten'].append(eaten[s])
            v['seen'].append(len(seen[s]))
            v['front'].append(max(ds) if ds else -1)
            v['meand'].append(round(10 * sum(ds) / len(ds)) if ds else -1)
            v['toward'].append(min(dt) if dt else -1)
            n = len(heads)
            if n >= 2:
                tot = 0
                for a in range(n):
                    for c in range(a + 1, n):
                        tot += g.mdist(heads[a], heads[c])
                v['spread'].append(round(10 * tot / (n * (n - 1) / 2)))
            else:
                v['spread'].append(-1)
            qi = queen[s]
            if qi in bodies:
                qh = bodies[qi][0]
                v['qd'].append(dfrom[s][qh] if dfrom[s][qh] < FAR else -1)
                v['qt'].append(dfrom[o][qh] if dfrom[o][qh] < FAR else -1)
                v['ql'].append(len(bodies[qi]))
            else:
                v['qd'].append(-1)
                v['qt'].append(-1)
                v['ql'].append(-1)
            v['cd'].append(round(10 * sum(g.cdist(c) for c in heads) / n) if n else -1)

    def finish_turn():
        nonlocal cur
        if cur is None:
            return
        t = cur
        cur = None
        v = turns[t['s']][t['key']]
        v[0] += 1
        if kind == 1:
            v[1] += 1
        elif kind == 0:
            n = len(dirs)
            free = (t['L'] + 3) // 4
            v[2] += used
            v[3] += int(n >= 2)
            v[4] += max(0, n - free)
            v[5] += int(n > free)
            v[6] += min(n, free) - 1 if n >= 1 else 0
            v[7] += free - 1

    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            finish_turn()
        if k == 0:
            if started:
                if rnd <= LAST:
                    sample()
                if rnd == STOP:
                    at100 = {s: dict(alive=sum(1 for i in bodies if side(i) == s), total=sum(len(b) for i, b in bodies.items() if side(i) == s),
                                     eaten=eaten[s], seen=len(seen[s])) for s in 'ut'}
            started = True
            rnd, actor = p.i32(0), None
            if rnd > STOP:
                break
        elif k == 1:
            actor = p.i32(0)
            dirs, used, kind = [], 0, 2
            s = side(actor)
            b = bodies[actor]
            head, L = b[0], len(b)
            win = g.window(head)
            eg = hg[other[s]]
            enemy = False
            for c in win:
                if eg[c]:
                    enemy = True
                    break
            if enemy and contact[s] is None:
                contact[s] = rnd
            pearl = pv[head] > 0
            if pearl and see1[s] is None:
                see1[s] = rnd
            seen[s].update(win)
            if s == 'u':
                chk['turns'] += 1
            if rnd <= LAST:
                ctx = 'P' if pearl else 'E' if enemy else 'N'
                cur = dict(s=s, L=L, ctx=ctx, key='%d|%s|%s|%d' % (wbucket(rnd), lbucket(L), ctx, info[actor]['q']))
        elif k == 4:
            a = p.pointer(0)
            kind = a.u16(0) if a else 2
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                for z in g.window(c):
                    pv[z] += 1
            else:
                for z in g.window(c):
                    pv[z] -= 1
                s = side(actor)
                eaten[s] += 1
                f = info[actor]
                f['eats'] += int(rnd <= LAST)
                if f['eat1'] is None:
                    f['eat1'] = rnd
                if s == 'u':
                    chk['pearls'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            old = b[0]
            if old != hd:
                b.appendleft(hd)
                s = side(i)
                hg[s][old] -= 1
                hg[s][hd] += 1
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
            if len(b) >= 4:
                if since4.get(i) is None:
                    since4[i] = rnd
            else:
                since4[i] = None
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s0 = side(parent)
            before = len(bodies[parent])
            alive0 = sum(1 for i in bodies if side(i) == s0)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            hg[s0][bodies[child][0]] += 1
            info[child] = dict(s=s0, born=rnd, len0=len(bodies[child]), eat1=None, died=None, cause=None, q=0, eats=0, splits=0)
            if rnd <= LAST:
                held = rnd - since4[parent] if since4.get(parent) is not None else -1
                info[parent]['splits'] += 1
                if len(splits[s0]) < 80:
                    splits[s0].append([rnd, before, len(bodies[child]), info[parent]['q'], cur['ctx'] if cur else '?', alive0, held])
            since4[parent] = rnd if len(bodies[parent]) >= 4 else None
            since4[child] = rnd if len(bodies[child]) >= 4 else None
            if s0 == 'u':
                chk['splits'] += 1
        elif k == 11:
            i = p.i32(0)
            reason = p.u16(4)
            b = bodies.pop(i)
            s = side(i)
            hg[s][b[0]] -= 1
            cause = CAUSES[reason] if reason < 4 else (CAUSES[4] if kind == 1 else CAUSES[5] if kind == 0 else CAUSES[6]) if i == actor else CAUSES[6]
            if reason == 3:
                cause = 'headon' if i == actor else 'hit'
            info[i]['died'] = rnd
            info[i]['cause'] = cause
            if rnd <= LAST:
                deaths[s][cause] += 1
    finish_turn()
    if rnd <= LAST and started and len(series['u']['alive']) <= rnd:
        sample()
    out = dict(who=row['who'], game=row['game'], layout=row['layout'], result=row['result'], rating=row['rating'],
               last_round=row['last_round'], cells=N, w=w, h=h, sep=dfrom['u'][start['t']], chk=chk, sides={})
    for s in 'ut':
        dr = [[f['born'], f['len0'], f['eat1'], f['died'], f['cause'], f['q'], f['eats'], f['splits']]
              for i, f in sorted(info.items()) if f['s'] == s and f['born'] <= LAST][:120]
        out['sides'][s] = dict(cfg=cfg[s], series=series[s], splits=splits[s], turns=dict(turns[s]), deaths=dict(deaths[s]),
                               contact=contact[s], see1=see1[s], at100=at100.get(s), dragons=dr)
    return out


def save(who, shard, body):
    tag = who + str(shard)
    if tag == 'O0':
        Path(OUT + 'op_scan-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'op_scan-O1.jsonl').write_text(body)
    elif tag == 'O2':
        Path(OUT + 'op_scan-O2.jsonl').write_text(body)
    elif tag == 'O3':
        Path(OUT + 'op_scan-O3.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'op_scan-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'op_scan-R1.jsonl').write_text(body)
    elif tag == 'R2':
        Path(OUT + 'op_scan-R2.jsonl').write_text(body)
    elif tag == 'R3':
        Path(OUT + 'op_scan-R3.jsonl').write_text(body)
    else:
        Path(OUT + 'op_scan-test.jsonl').write_text(body)


def main():
    who, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    rows = sorted([r for r in rows if r['who'] == who], key=lambda r: (r['layout'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[::max(1, len(rows) // limit)][:limit]
    geos, out, bad, off = {}, [], [], 0
    for n, r in enumerate(rows):
        try:
            rec = scan(r, geos)
            if r['last_round'] >= STOP:
                want = dict(turns=r['0-100']['turns'], pearls=r['0-100']['pearls'], splits=r['0-100']['splits'])
                for f, val in want.items():
                    if rec['chk'][f] != val:
                        off += 1
                        if off <= 12:
                            print('MISMATCH', r['game'], f, val, rec['chk'][f], flush=True)
                if rec['sides']['u']['series']['seen'][50] != r['seen50']:
                    off += 1
                    if off <= 12:
                        print('MISMATCH', r['game'], 'seen50', r['seen50'], rec['sides']['u']['series']['seen'][50], flush=True)
            fc, mc = r['first_contact'], rec['sides']['u']['contact']
            if (fc is not None and fc <= STOP and fc != mc) or (mc is not None and mc != fc):
                off += 1
                if off <= 12:
                    print('MISMATCH', r['game'], 'contact', fc, mc, flush=True)
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 20 == 19:
            print(n + 1, len(rows), 'bad', len(bad), 'off', off, flush=True)
    save(who, shard if not limit else 9, '\n'.join(out) + '\n')
    print('done', who, shard, len(out), 'bad', bad, 'mismatches', off)


main()
