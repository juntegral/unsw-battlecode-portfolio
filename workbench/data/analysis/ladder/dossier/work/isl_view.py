# Scratch (diag-islands): who holds the fast pearl tiles, round by round, in every main game on one layout.
# Reads per-game.jsonl, maps.json and replays. Writes work/isl_trace-<tag>.jsonl (one line per game).
# Usage: python3 data/analysis/ladder/dossier/work/isl_trace.py "<layout key>" <tag>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

WORK = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
INF = 9999
BIN = 25
CAUSE = ('wall', 'own', 'body', 'headon', 'noact')


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
        self.cache = {}

    def dist(self, src):
        d = self.cache.get(src)
        if d is None:
            d = [INF] * (self.w * self.h)
            d[src] = 0
            q = deque([src])
            while q:
                c = q.popleft()
                nd = d[c] + 1
                for t in self.adj[c]:
                    if d[t] == INF:
                        d[t] = nd
                        q.append(t)
            self.cache[src] = d
        return d


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def main():
    # Usage: isl_view.py <game id> <dragon id or -1 for the team's pearl-side turns> <first round> <last round> [map]
    game, did, r0, r1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    draw = len(sys.argv) > 5
    rec = None
    for line in Path('data/analysis/ladder/dossier/per-game.jsonl').open():
        r = json.loads(line)
        if r['game'] == game and r['relation'] == 'us':
            rec = r
    maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
    oi = maps[rec['layout_key']].get('observed_intervals') or {}
    root = replay.load(Path(rec['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    fast = set(int(k.split(',')[1]) * w + int(k.split(',')[0]) for k, v in oi.items() if v.get('fast'))
    tile = lambda p: p[1] * w + p[0]
    xy = lambda c: '%d,%d' % (c % w, c // w)
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    g = Geo(w, h, raw)
    ours = rec['our_side']
    side = lambda i: 'u' if teams[i] == ours else 't'
    present = {}
    rnd, actor, cur = 0, None, None

    def man(a, b):
        return torus(a % w, b % w, w) + torus(a // w, b // w, h)

    def show():
        nonlocal cur
        if cur is None:
            return
        c = cur
        cur = None
        print('r%d id %d len %d %s -> %s%s%s | beside: %s | mates<=9: %s | enemies<=6: %s | pearls<=4: %s' % (
            c['r'], c['id'], c['L'], xy(c['head']), ' '.join(xy(x) for x in c['steps']) or 'stay',
            ' ATE%d' % c['ate'] if c['ate'] else '', ' ' + c['ev'] if c['ev'] else '',
            ' '.join(xy(x) + ('F' if x in fast else '') for x in c['adj']) or '-', c['mates'], c['en'], c['near']))
        if draw and c['adj'] and not c['ate']:
            hx, hy = c['head'] % w, c['head'] // w
            for dy in range(-4, 5):
                row = ''
                for dx in range(-6, 7):
                    t = ((hy + dy) % h) * w + (hx + dx) % w
                    ch = c['grid'].get(t, 'o' if t in c['pearls'] else '.')
                    west = g.moves[t][3][0]
                    row += ('|' if west == 1 else ' ') + ch
                print('      ' + row)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            show()
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd > r1:
                break
        elif k == 1:
            actor = p.i32(0)
            if r0 <= rnd <= r1 and side(actor) == 'u' and (actor == did or did < 0):
                body = bodies[actor]
                hd = body[0]
                adj = [dest for kind, dest in g.moves[hd] if kind != 1 and dest in present]
                if did >= 0 or adj:
                    mates = ' '.join('%d:L%d@%s(d%d)' % (i, len(b), xy(b[0]), man(hd, b[0])) for i, b in bodies.items()
                                     if i != actor and side(i) == 'u' and man(hd, b[0]) <= 9)
                    en = ' '.join('%d:L%d@%s(d%d)' % (i, len(b), xy(b[0]), man(hd, b[0])) for i, b in bodies.items()
                                  if side(i) == 't' and man(hd, b[0]) <= 6)
                    near = ' '.join(xy(x) + ('F' if x in fast else '') for x in present if man(hd, x) <= 4)
                    grid = {}
                    for i, b in bodies.items():
                        for n, x in enumerate(b):
                            grid[x] = ('@' if i == actor else 'M' if side(i) == 'u' else 'E') if n == 0 else ('m' if side(i) == 'u' else 'e')
                    cur = dict(r=rnd, id=actor, L=len(body), head=hd, adj=adj, steps=[], ate=0, ev='', mates=mates or '-', en=en or '-',
                               near=near or '-', grid=grid, pearls=set(present))
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present[c] = rnd
            else:
                present.pop(c)
                if cur is not None:
                    cur['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if cur is not None and i == actor:
                    cur['steps'].append(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            if cur is not None and p.i32(0) == cur['id']:
                cur['ev'] += 'SPLIT->%d,%d' % (p.i32(0), p.i32(4))
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 11:
            i = p.i32(0)
            if cur is not None:
                cur['ev'] += ' DEATH %d reason %d' % (i, p.u16(4))
            bodies.pop(i)
    show()


main()
