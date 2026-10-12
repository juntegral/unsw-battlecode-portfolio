"""Scratch (diag-australia): chances and exposures of short dragons (length 2-4, not the queen), both sides, r101-300.
chance   = at turn start an enemy head of at least the actor's length is within the actor's sprint reach (length-1 steps
           over free tiles). edge = allied heads in the 7x7 view (without the actor) >= enemy heads in it (the bot's local rule).
exposure = the actor ends its turn alive within the sprint reach of an enemy head of length 2-4 (that head's length-1).
Prints totals only. Usage: python3 .../au_scan2.py "<layout key>" """
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LO, HI = 101, 300


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

    def window(self, src):
        s = self.wins.get(src)
        if s is None:
            y, x = divmod(src, self.w)
            s = frozenset(((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4))
            self.wins[src] = s
        return s


def scan(row, geos, tot):
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
    heads = {b[0]: i for i, b in bodies.items()}
    occ = Counter()
    for b in bodies.values():
        for c in b:
            occ[c] += 1
    res = row['result']
    rnd, actor = 0, None
    cur = None
    pend = {}
    alive = Counter(side(i) for i in bodies)

    def reach_heads(src, depth, s):
        # enemy heads of side != s within depth steps over free tiles; returns list of (dist, id)
        out = []
        d = {src: 0}
        q = deque([src])
        while q:
            c = q.popleft()
            if d[c] >= depth:
                continue
            for t in g.adj[c]:
                if t in d:
                    continue
                d[t] = d[c] + 1
                i = heads.get(t)
                if i is not None and side(i) != s:
                    out.append((d[t], i))
                    continue
                if occ[t]:
                    continue
                q.append(t)
        return out

    def view(src, s, me):
        e = a = 0
        for c in g.window(src):
            i = heads.get(c)
            if i is None or i == me:
                continue
            if side(i) == s:
                a += 1
            else:
                e += 1
        return a, e

    def finish():
        nonlocal cur
        if cur is None:
            return
        c = cur
        cur = None
        i = c['id']
        if i in bodies and c['track']:
            s = c['side']
            L = len(bodies[i])
            hd = bodies[i][0]
            near = reach_heads(hd, 3, s)
            exp = [j for dist, j in near if 2 <= len(bodies[j]) <= 4 and dist <= len(bodies[j]) - 1]
            a, e = view(hd, s, i)
            pend[i] = (bool(exp), e > a, s, set(exp), c['capk'])
            if exp:
                t = tot[(s, c['capk'])]
                t['exposed'] += 1
                t['exposed_out'] += int(e > a)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            finish()
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd > HI:
                break
        elif k == 1:
            actor = p.i32(0)
            s = side(actor)
            L = len(bodies[actor])
            pend.pop(actor, None)
            track = LO <= rnd <= HI and actor > 1 and L <= 4
            capk = 'cap' if alive['u'] >= 59 else 'below'
            cur = dict(id=actor, side=s, track=track, capk=capk, can=False, edge=False, took=False)
            if track:
                hd = bodies[actor][0]
                near = reach_heads(hd, L - 1, s)
                can = [j for dist, j in near if len(bodies[j]) >= L]
                a, e = view(hd, s, actor)
                t = tot[(s, capk)]
                t['turns'] += 1
                t['seen'] += int(e > 0)
                if can:
                    cur['can'] = True
                    cur['edge'] = a >= e
                    t['can'] += 1
                    t['can_edge'] += int(a >= e)
                    t['can_rule'] += int(any(len(bodies[j]) >= max(5, L + 2) for j in can))
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                if heads.get(b[0]) == i:
                    del heads[b[0]]
                b.appendleft(hd)
                heads[hd] = i
                occ[hd] += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for c in bodies[parent]:
                occ[c] -= 1
            if heads.get(bodies[parent][0]) == parent:
                del heads[bodies[parent][0]]
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
                heads[bodies[i][0]] = i
                for c in bodies[i]:
                    occ[c] += 1
            alive[side(parent)] += 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            if reason == 3:
                if i == actor and cur is not None and cur['track']:
                    t = tot[(s, cur['capk'])]
                    t['rams'] += 1
                    t['rams_can'] += int(cur['can'])
                    t['rams_can_edge'] += int(cur['can'] and cur['edge'])
                    t['took_edge'] += int(cur['can'] and cur['edge'])
                    t['took_noedge'] += int(cur['can'] and not cur['edge'])
                elif i != actor and i in pend:
                    ex, out, ps, who, capk = pend[i]
                    t = tot[(ps, capk)]
                    t['hit_tracked'] += 1
                    if ex and actor in who:
                        t['exposed_hit'] += 1
                        t['exposed_out_hit'] += int(out)
            if heads.get(bodies[i][0]) == i:
                del heads[bodies[i][0]]
            for c in bodies[i]:
                occ[c] -= 1
            bodies.pop(i)
            pend.pop(i, None)
            alive[s] -= 1
    finish()


def main():
    lay = sys.argv[1]
    rows = json.loads(Path('data/analysis/ladder/dossier/input-snapshot.json').read_text())['rows']
    rows = sorted((r for r in rows if r['map_key'] == lay), key=lambda r: r['game'])
    tot = defaultdict(Counter)
    geos = {}
    for r in rows:
        scan(r, geos, tot)
    n = len(rows)
    print(lay, n, 'games; short dragons (length 2-4, not queens), rounds', LO, HI, '; per game')
    print('side, our count | turns | enemy head in view | chance (equal or longer head in reach) | of those with the local edge | meets the size rule | rams made | rams at a chance: with edge / without | take rate with edge / without | ends turn exposed | exposed and outnumbered | rammed by an exposing head | hazard exposed / exposed and outnumbered')
    for key in (('u', 'below'), ('u', 'cap'), ('t', 'below'), ('t', 'cap')):
        t = tot[key]
        if not t['turns']:
            continue
        print('%s %-5s | %.0f | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f / %.1f | %.3f / %.3f | %.1f | %.1f | %.1f | %.3f / %.3f' % (
            'ours' if key[0] == 'u' else 'theirs', key[1], t['turns'] / n, t['seen'] / n, t['can'] / n, t['can_edge'] / n, t['can_rule'] / n,
            t['rams'] / n, t['took_edge'] / n, t['took_noedge'] / n,
            t['took_edge'] / max(1, t['can_edge']), t['took_noedge'] / max(1, t['can'] - t['can_edge']),
            t['exposed'] / n, t['exposed_out'] / n, t['exposed_hit'] / n,
            t['exposed_hit'] / max(1, t['exposed']), t['exposed_out_hit'] / max(1, t['exposed_out'])))
        print('      raw', dict(t))


main()
