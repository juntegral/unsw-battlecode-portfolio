# Scratch (diag-opening), fourth pass: one-way steps. Rounds 0-100, both sides (u = followed side, t = its opponent),
# dragons of length 4 or less, turns that are a move with at least one free step.
# For each free step (a neighbouring tile across an open edge or portal that holds no body): can the dragon's own tail tile
# be reached from it without crossing the rest of its body (true map, other dragons ignored, whole board searched)?
#   way     = yes (a loop back to the tail exists)
#   one-way = no; "big" when 6L+8 or more tiles lie ahead (the room test of the stall release rule), else "small".
# key: window (0: r0-30, 1: r31-100) | what is in view (P pearl, N none) | rounds since the dragon last grew or was born
#      (a 0-11, b 12-29, c 30+) | options (C = a way step and a big one-way step both free, O = only one-way steps free and
#      one is big, W = no big one-way step free)
# value: [turns, took a big one-way step, took a way step, took a small one-way step]
# Also per side: 'inroom' = turns r0-60 that start inside the start pocket, where the start pocket is the set of tiles
# reachable from the queen's first head tile without passing a "door" (a tile with exactly two open neighbours); and the
# first round a head of the side is outside it.
# Usage: python3 data/analysis/ladder/dossier/work/op_scan4.py <O|R> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
STOP = 100
CAP = 600


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
        self.wins, self.pockets, self.memo = {}, {}, {}

    def window(self, c):
        s = self.wins.get(c)
        if s is None:
            y, x = divmod(c, self.w)
            s = tuple(sorted({((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4)}))
            self.wins[c] = s
        return s

    def pocket(self, src):
        s = self.pockets.get(src)
        if s is None:
            got = {src}
            q = deque([src])
            while q:
                z = q.popleft()
                if z != src and len(self.adj[z]) <= 2:
                    continue
                for t in self.adj[z]:
                    if t not in got:
                        got.add(t)
                        q.append(t)
            s = got
            self.pockets[src] = s
        return s

    def probe(self, d, blocked, tail):
        """(reaches the tail, tiles found) from d without entering blocked tiles; capped."""
        if d == tail:
            return True, 1
        got = {d}
        q = deque([d])
        while q:
            z = q.popleft()
            for t in self.adj[z]:
                if t in got or t in blocked:
                    continue
                if t == tail:
                    return True, len(got)
                got.add(t)
                q.append(t)
        return False, len(got)


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
    adj = g.adj
    mine = row['side']
    side = lambda i: 'u' if teams[i] == mine else 't'
    queen = {s: min(i for i in bodies if side(i) == s) for s in 'ut'}
    home = {s: g.pocket(bodies[queen[s]][0]) for s in 'ut'}
    events = list(root.pointer(3))
    occ = [0] * N
    for b in bodies.values():
        for c in b:
            occ[c] += 1
    pv = [0] * N
    grew = {i: 0 for i in bodies}
    tab = dict(u=defaultdict(lambda: [0] * 4), t=defaultdict(lambda: [0] * 4))
    inroom = dict(u=[0, 0], t=[0, 0])
    out_round = dict(u=None, t=None)
    rnd, actor, cur, kind, first = 0, None, None, 2, None

    def close_turn():
        nonlocal cur
        if cur is None:
            return
        t = cur
        cur = None
        if kind != 0 or first is None:
            return
        cls = t['steps'].get(first)
        if cls is None:
            return
        v = tab[t['s']][t['key']]
        v[0] += 1
        v[1 if cls == 'big' else 2 if cls == 'way' else 3] += 1

    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0 or k == 1:
            close_turn()
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd > STOP:
                break
        elif k == 1:
            actor = p.i32(0)
            kind, first = 2, None
            s = side(actor)
            b = bodies[actor]
            head, L = b[0], len(b)
            if rnd <= 60:
                inroom[s][0] += 1
                inroom[s][1] += int(head in home[s])
            if out_round[s] is None and head not in home[s]:
                out_round[s] = rnd
            if L <= 4:
                free = [t for t in adj[head] if occ[t] == 0]
                if free:
                    tail = b[-1]
                    blocked = set(b)
                    blocked.discard(tail)
                    steps = {}
                    shape = tuple(b)
                    for d in free:
                        hit = g.memo.get((d, shape))
                        if hit is None:
                            hit = g.probe(d, blocked, tail)
                            g.memo[(d, shape)] = hit
                        ok, n = hit
                        steps[d] = 'way' if ok else 'big' if n >= 6 * L + 8 else 'small'
                    vals = set(steps.values())
                    opt = 'C' if 'big' in vals and 'way' in vals else 'O' if 'big' in vals else 'W'
                    age = rnd - grew.get(actor, 0)
                    cur = dict(s=s, steps=steps, key='%d|%s|%s|%s' % (0 if rnd <= 30 else 1, 'P' if pv[head] > 0 else 'N',
                                                                      'a' if age < 12 else 'b' if age < 30 else 'c', opt))
        elif k == 4:
            a = p.pointer(0)
            kind = a.u16(0) if a else 2
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                for z in g.window(c):
                    pv[z] += 1
            else:
                for z in g.window(c):
                    pv[z] -= 1
                grew[actor] = rnd
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                occ[hd] += 1
                if i == actor and first is None:
                    first = hd
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for c in bodies[parent]:
                occ[c] -= 1
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
                for c in bodies[i]:
                    occ[c] += 1
            grew[child] = rnd
        elif k == 11:
            i = p.i32(0)
            for c in bodies.pop(i):
                occ[c] -= 1
    close_turn()
    out = dict(who=row['who'], game=row['game'], layout=row['layout'], result=row['result'], last_round=row['last_round'],
               pocket={s: len(home[s]) for s in 'ut'}, cells=N, sides={})
    for s in 'ut':
        out['sides'][s] = dict(tab=dict(tab[s]), inroom=inroom[s], out=out_round[s])
    return out


def save(who, shard, body):
    tag = who + str(shard)
    if tag == 'O0':
        Path(OUT + 'op_scan4-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'op_scan4-O1.jsonl').write_text(body)
    elif tag == 'O2':
        Path(OUT + 'op_scan4-O2.jsonl').write_text(body)
    elif tag == 'O3':
        Path(OUT + 'op_scan4-O3.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'op_scan4-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'op_scan4-R1.jsonl').write_text(body)
    elif tag == 'R2':
        Path(OUT + 'op_scan4-R2.jsonl').write_text(body)
    elif tag == 'R3':
        Path(OUT + 'op_scan4-R3.jsonl').write_text(body)
    else:
        Path(OUT + 'op_scan4-test.jsonl').write_text(body)


def main():
    who, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    rows = sorted([r for r in rows if r['who'] == who], key=lambda r: (r['layout'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[::max(1, len(rows) // limit)][:limit]
    geos, out, bad = {}, [], []
    for n, r in enumerate(rows):
        try:
            out.append(json.dumps(scan(r, geos), separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
    save(who, shard if not limit else 9, '\n'.join(out) + '\n')
    print('done', who, shard, len(out), 'bad', bad)


main()
