# Scratch (diag-opening), third pass: rounds 0-60, both sides (u = followed side, t = its opponent).
#  eat    = pearls eaten by window (0: r0-10, 1: r11-20, 2: r21-40, 3: r41-60) and origin: n natural, o a dead dragon of the
#           eater's own side, e a dead dragon of the other side.
#  chase  = every turn that starts with a pearl in the 7 by 7 view. P = the pearl nearest the head by path (open edges
#           and portals, bodies ignored, 8 steps at most; X = none within 8 path steps although one is in view).
#           key: window (0: r0-20, 1: r21-60) | distance to P (1, 2, 3-4, 5-8, X) | who else: solo = no team mate's head as
#           near P, tie = a mate exactly as near, mate = a mate nearer; a trailing f = that mate is its parent or child |
#           F when an enemy head is as near or nearer, else -.
#           value: [turns, the turn ends nearer P or on it, P eaten by this dragon this turn, the turn is a split,
#                   P eaten by this dragon within 8 rounds, P eaten by a team mate within 8 rounds, by the enemy within 8 rounds].
# Usage: python3 data/analysis/ladder/dossier/work/op_scan3.py <O|R> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LAST = 60
STOP = 70


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
        s = self.balls.get(c)
        if s is None:
            d = {c: 0}
            q = deque([c])
            while q:
                z = q.popleft()
                if d[z] >= 8:
                    continue
                for t in self.adj[z]:
                    if t not in d:
                        d[t] = d[z] + 1
                        q.append(t)
            s = d
            self.balls[c] = s
        return s


def dclass(d):
    return '1' if d <= 1 else '2' if d == 2 else '3-4' if d <= 4 else '5-8'


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
    events = list(root.pointer(3))
    pv = [0] * N
    present = {}
    family = {}
    eat = dict(u=defaultdict(int), t=defaultdict(int))
    chase = dict(u=defaultdict(lambda: [0] * 7), t=defaultdict(lambda: [0] * 7))
    open_marks = defaultdict(list)
    dying = None
    rnd, actor, cur, kind = 0, None, None, 2

    def close_turn():
        nonlocal cur
        if cur is None:
            return
        t = cur
        cur = None
        v = chase[t['s']][t['key']]
        v[0] += 1
        if kind == 1:
            v[3] += 1
        if t['p'] is not None:
            b = bodies.get(t['id'])
            if t['ate']:
                v[1] += 1
                v[2] += 1
            elif b is not None:
                nd = g.ball(t['p']).get(b[0])
                if nd is not None and nd < t['d']:
                    v[1] += 1

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
            kind = 2
            dying = None
            s = side(actor)
            head = bodies[actor][0]
            if rnd <= LAST and pv[head] > 0:
                target, dist = None, None
                for c, d in g.ball(head).items():
                    if c in present and c != head:
                        target, dist = c, d
                        break
                if target is None:
                    cur = dict(s=s, id=actor, p=None, d=None, ate=False, key='%d|X|solo|-' % (0 if rnd <= 20 else 1))
                else:
                    bp = g.ball(target)
                    dm, who, df = None, None, None
                    for z, bb in bodies.items():
                        if z == actor:
                            continue
                        dd = bp.get(bb[0])
                        if dd is None:
                            continue
                        if teams[z] == teams[actor]:
                            if dm is None or dd < dm:
                                dm, who = dd, z
                        elif df is None or dd < df:
                            df = dd
                    rel = 'solo' if dm is None or dm > dist else 'tie' if dm == dist else 'mate'
                    if rel != 'solo' and who is not None and (family.get(who) == actor or family.get(actor) == who):
                        rel += 'f'
                    foe = 'F' if df is not None and df <= dist else '-'
                    cur = dict(s=s, id=actor, p=target, d=dist, ate=False,
                               key='%d|%s|%s|%s' % (0 if rnd <= 20 else 1, dclass(dist), rel, foe))
                    open_marks[target].append((rnd, s, actor, cur['key']))
        elif k == 4:
            a = p.pointer(0)
            kind = a.u16(0) if a else 2
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                for z in g.window(c):
                    pv[z] += 1
                present[c] = 'n' if actor is None else dying
                open_marks.pop(c, None)
            else:
                for z in g.window(c):
                    pv[z] -= 1
                origin = present.pop(c, 'n')
                s = side(actor)
                if rnd <= LAST:
                    wb = 0 if rnd <= 10 else 1 if rnd <= 20 else 2 if rnd <= 40 else 3
                    eat[s]['%d|%s' % (wb, 'n' if origin == 'n' else 'o' if origin == s else 'e')] += 1
                if cur is not None and cur['p'] == c:
                    cur['ate'] = True
                for r0, s0, who, key0 in open_marks.pop(c, ()):
                    if rnd - r0 <= 8:
                        v = chase[s0][key0]
                        if who == actor:
                            v[4] += 1
                        elif s0 == s:
                            v[5] += 1
                        else:
                            v[6] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            old = b[0]
            if old != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            s0 = side(parent)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            family[child] = parent
        elif k == 11:
            i = p.i32(0)
            b = bodies.pop(i)
            dying = side(i)
    close_turn()
    out = dict(who=row['who'], game=row['game'], layout=row['layout'], result=row['result'], last_round=row['last_round'], sides={})
    for s in 'ut':
        out['sides'][s] = dict(eat=dict(eat[s]), chase=dict(chase[s]))
    return out


def save(who, shard, body):
    tag = who + str(shard)
    if tag == 'O0':
        Path(OUT + 'op_scan3-O0.jsonl').write_text(body)
    elif tag == 'O1':
        Path(OUT + 'op_scan3-O1.jsonl').write_text(body)
    elif tag == 'O2':
        Path(OUT + 'op_scan3-O2.jsonl').write_text(body)
    elif tag == 'O3':
        Path(OUT + 'op_scan3-O3.jsonl').write_text(body)
    elif tag == 'R0':
        Path(OUT + 'op_scan3-R0.jsonl').write_text(body)
    elif tag == 'R1':
        Path(OUT + 'op_scan3-R1.jsonl').write_text(body)
    elif tag == 'R2':
        Path(OUT + 'op_scan3-R2.jsonl').write_text(body)
    elif tag == 'R3':
        Path(OUT + 'op_scan3-R3.jsonl').write_text(body)
    else:
        Path(OUT + 'op_scan3-test.jsonl').write_text(body)


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
