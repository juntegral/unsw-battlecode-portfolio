# Scratch (diag-opening), second pass: rounds 0-100, both sides of each game (u = followed side, t = its opponent).
#  pc3 / pc6 = the first round in which, at one of the side's turn starts, an enemy head is within 3 / 6 PATH steps
#              of that head (open edges and portals, bodies ignored). The dossier's first contact is the 7 by 7 view,
#              which also looks across kelp and across the wrapped border.
#  kids      = for each split of rounds 0-40: [round, path distance between the parent's head and the child's head at
#              the end of the split round, 3, 5 and 10 rounds later] (41 = further than 40 or no path, -1 = one is dead).
#  pearls    = natural pearls born in rounds 0-60, by the path distance of the side's nearest head at birth
#              (a 0-3, b 4-7, c 8-15, d 16+): [born, in the side's view at birth, seen by the side by round 100,
#              sum of rounds birth to first seen, eaten by the side by round 100, sum of rounds birth to eaten,
#              sum of rounds first seen to eaten, eaten by the other side, eaten by the side in the birth round,
#              eaten by the side within 10 rounds of birth].
#  first8    = the directions of each starting dragon's first 8 turns (S = split, - = none), for reading.
# Usage: python3 data/analysis/ladder/dossier/work/op_scan2.py <O|R> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
BORN = 60
STOP = 100
NAMES = 'NESW'


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
        self.wins, self.balls = {}, {}

    def window(self, c):
        s = self.wins.get(c)
        if s is None:
            y, x = divmod(c, self.w)
            s = tuple(sorted({((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4)}))
            self.wins[c] = s
        return s

    def ball(self, c):
        """Tiles within 6 path steps of c, as (tile, distance) pairs, nearest first."""
        s = self.balls.get(c)
        if s is None:
            d = {c: 0}
            q = deque([c])
            while q:
                z = q.popleft()
                if d[z] >= 6:
                    continue
                for t in self.adj[z]:
                    if t not in d:
                        d[t] = d[z] + 1
                        q.append(t)
            s = tuple(d.items())
            self.balls[c] = s
        return s

    def pdist(self, a, c, cap=40):
        if a == c:
            return 0
        d = {a: 0}
        q = deque([a])
        while q:
            z = q.popleft()
            if d[z] >= cap:
                break
            for t in self.adj[z]:
                if t not in d:
                    if t == c:
                        return d[z] + 1
                    d[t] = d[z] + 1
                    q.append(t)
        return cap + 1

    def multi(self, srcs):
        N = self.w * self.h
        d = [9999] * N
        q = deque()
        for c in srcs:
            if d[c]:
                d[c] = 0
                q.append(c)
        while q:
            z = q.popleft()
            for t in self.adj[z]:
                if d[t] == 9999:
                    d[t] = d[z] + 1
                    q.append(t)
        return d


def dbucket(d):
    return 'a' if d <= 3 else 'b' if d <= 7 else 'c' if d <= 15 else 'd'


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
    starters = {i: side(i) for i in bodies}
    first8 = {i: [] for i in bodies}
    events = list(root.pointer(3))
    hg = dict(u=[0] * N, t=[0] * N)
    for i, b in bodies.items():
        hg[side(i)][b[0]] += 1
    pv = [0] * N
    present = {}
    pc3 = dict(u=None, t=None)
    pc6 = dict(u=None, t=None)
    vc = dict(u=None, t=None)
    pearls = dict(u=defaultdict(lambda: [0] * 10), t=defaultdict(lambda: [0] * 10))
    kids = dict(u=[], t=[])
    watch = []
    fresh = []
    rnd, actor = 0, None
    started = False

    def classify():
        if not fresh:
            return
        for s in 'ut':
            heads = [b[0] for i, b in bodies.items() if side(i) == s]
            if not heads:
                continue
            dist = g.multi(heads)
            eg = hg[s]
            for c in fresh:
                rec = present.get(c)
                if rec is None or rec['born'] != rnd:
                    continue
                rec['b' + s] = dbucket(dist[c])
                inview = False
                for z in g.window(c):
                    if eg[z]:
                        inview = True
                        break
                v = pearls[s][rec['b' + s]]
                v[0] += 1
                if inview:
                    v[1] += 1
                    v[2] += 1
                    rec['s' + s] = rnd
        fresh.clear()

    def settle():
        keep = []
        for wt in watch:
            age = rnd - wt[0]
            if age in (0, 3, 5, 10):
                a, c = bodies.get(wt[1]), bodies.get(wt[2])
                wt[3].append(g.pdist(a[0], c[0]) if a is not None and c is not None else -1)
            if age < 10:
                keep.append(wt)
        watch[:] = keep

    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            if started:
                classify()
                settle()
            started = True
            rnd, actor = p.i32(0), None
            if rnd > STOP:
                break
        elif k == 1:
            classify()
            actor = p.i32(0)
            s = side(actor)
            head = bodies[actor][0]
            eg = hg[other[s]]
            win = g.window(head)
            if vc[s] is None:
                for c in win:
                    if eg[c]:
                        vc[s] = rnd
                        break
            if pc6[s] is None or pc3[s] is None:
                for c, d in g.ball(head):
                    if eg[c]:
                        if pc6[s] is None:
                            pc6[s] = rnd
                        if d <= 3 and pc3[s] is None:
                            pc3[s] = rnd
            if pv[head] > 0:
                for c in win:
                    rec = present.get(c)
                    if rec is not None and rec.get('s' + s) is None and rec.get('b' + s) is not None:
                        rec['s' + s] = rnd
                        v = pearls[s][rec['b' + s]]
                        v[2] += 1
                        v[3] += rnd - rec['born']
        elif k == 4:
            if actor in first8 and len(first8[actor]) < 8:
                a = p.pointer(0)
                kind = a.u16(0) if a else 2
                if kind == 0 and a.pointer(0) is not None:
                    first8[actor].append(''.join(NAMES[d] for d in a.pointer(0)))
                else:
                    first8[actor].append('S' if kind == 1 else '-')
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                for z in g.window(c):
                    pv[z] += 1
                if actor is None and rnd <= BORN:
                    present[c] = dict(born=rnd)
                    fresh.append(c)
                else:
                    present[c] = dict(born=-1)
            else:
                for z in g.window(c):
                    pv[z] -= 1
                rec = present.pop(c, None)
                if rec is not None and rec['born'] >= 0:
                    s = side(actor)
                    o = other[s]
                    if rec.get('b' + s) is not None:
                        v = pearls[s][rec['b' + s]]
                        v[4] += 1
                        v[5] += rnd - rec['born']
                        seen_at = rec.get('s' + s)
                        if seen_at is None:
                            seen_at = rnd
                            v[2] += 1
                            v[3] += rnd - rec['born']
                        v[6] += rnd - seen_at
                        v[8] += int(rnd == rec['born'])
                        v[9] += int(rnd - rec['born'] <= 10)
                    if rec.get('b' + o) is not None:
                        pearls[o][rec['b' + o]][7] += 1
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
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s0 = side(parent)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            hg[s0][bodies[child][0]] += 1
            if rnd <= 40 and len(kids[s0]) < 60:
                rec = [rnd]
                kids[s0].append(rec)
                watch.append([rnd, parent, child, rec])
        elif k == 11:
            i = p.i32(0)
            b = bodies.pop(i)
            hg[side(i)][b[0]] -= 1
    if started and rnd <= STOP:
        classify()
        settle()
    out = dict(who=row['who'], game=row['game'], layout=row['layout'], result=row['result'], last_round=row['last_round'], sides={})
    for s in 'ut':
        out['sides'][s] = dict(pc3=pc3[s], pc6=pc6[s], vc=vc[s], kids=kids[s], pearls=dict(pearls[s]),
                               first8=[' '.join(first8[i]) for i in sorted(first8) if starters[i] == s])
    return out


def save(who, shard, body):
    tag = who + str(shard)
    if tag == 'O0':
        Path(OUT + 'op_scan2-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'op_scan2-O1.jsonl').write_text(body)
    elif tag == 'O2':
        Path(OUT + 'op_scan2-O2.jsonl').write_text(body)
    elif tag == 'O3':
        Path(OUT + 'op_scan2-O3.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'op_scan2-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'op_scan2-R1.jsonl').write_text(body)
    elif tag == 'R2':
        Path(OUT + 'op_scan2-R2.jsonl').write_text(body)
    elif tag == 'R3':
        Path(OUT + 'op_scan2-R3.jsonl').write_text(body)
    else:
        Path(OUT + 'op_scan2-test.jsonl').write_text(body)


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
            fc, mc = r['first_contact'], rec['sides']['u']['vc']
            if (fc is not None and fc <= STOP and fc != mc) or (mc is not None and mc != fc):
                off += 1
                if off <= 12:
                    print('MISMATCH', r['game'], 'contact', fc, mc, flush=True)
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
    save(who, shard if not limit else 9, '\n'.join(out) + '\n')
    print('done', who, shard, len(out), 'bad', bad, 'mismatches', off)


main()
