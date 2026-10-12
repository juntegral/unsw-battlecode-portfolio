# Scratch (early-growth brief): per-turn and per-pearl rows for the opening of every main game on a 2-dragon-start layout.
# Reads replays only. Writes one JSON line per game to eg_rows-<shard>.jsonl in this directory.
# Usage: python3 data/analysis/ladder/losses/work/eg_scan.py <shard> <shards>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

WORK = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/losses/work/'
OUT0 = Path(WORK + 'eg_rows-0.jsonl')
OUT1 = Path(WORK + 'eg_rows-1.jsonl')
OUT2 = Path(WORK + 'eg_rows-2.jsonl')
OUT3 = Path(WORK + 'eg_rows-3.jsonl')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
INF = 9999
MAXR = 120
CAUSE = ('wall', 'own body', 'other body', 'head-on', 'no action')


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
        self.wins = {}
        self.cx, self.cy = w // 2, h // 2

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

    def window(self, src):
        s = self.wins.get(src)
        if s is None:
            y, x = divmod(src, self.w)
            s = frozenset(((y + dy) % self.h) * self.w + (x + dx) % self.w for dy in range(-3, 4) for dx in range(-3, 4))
            self.wins[src] = s
        return s

    def centre(self, c):
        y, x = divmod(c, self.w)
        ax, ay = abs(x - self.cx), abs(y - self.cy)
        return min(ax, self.w - ax) + min(ay, self.h - ay)


def scan(rec, geos):
    root = replay.load(Path(rec['replay'])).root()
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
    key = rec['map_key']
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    ours = rec['our_side']
    side = lambda i: 'u' if teams[i] == ours else 't'
    starts = set(bodies)
    present = {}
    pearls = []
    mem = defaultdict(dict)
    dseen = defaultdict(set)
    tseen = {'u': set(), 't': set()}
    trail = defaultdict(lambda: deque(maxlen=12))
    lastdir = {}
    turns, snaps = [], []
    rnd, actor, cur, started = 0, None, None, False

    def snapshot(n):
        row = [n]
        for s in 'ut':
            ls = [len(b) for i, b in bodies.items() if side(i) == s]
            row += [len(ls), sum(ls), max(ls, default=0)]
        row.append(len(present))
        snaps.append(row)

    def finish():
        nonlocal cur
        if cur is None:
            return
        c = cur
        cur = None
        head, steps = c['head'], c['steps']
        first = steps[0] if steps else None
        cd1 = g.centre(first) if first is not None else c['cd']
        closer = []
        for d0, t in ((c['dv'], c['tv']), (c['dm'], c['tm']), (c['dg'], c['tg'])):
            closer.append(None if (t is None or first is None) else int(g.dist(t)[first] < d0))
        st, portal, revisit = None, 0, None
        if first is not None:
            dirs = [d for d in range(4) if g.moves[head][d][0] != 1 and g.moves[head][d][1] == first]
            d = dirs[0] if dirs else None
            if d is not None:
                portal = int(g.moves[head][d][0] == 2)
                prev = lastdir.get(c['id'])
                st = None if prev is None else 'S' if prev == d else 'R' if prev == (d + 2) % 4 else 'T'
                lastdir[c['id']] = d
            revisit = int(first in trail[c['id']])
            for s_ in steps:
                trail[c['id']].append(s_)
        turns.append([c['r'], c['s'], c['id'], c['L'], int(c['id'] in starts), int(c['id'] in (0, 1)), head, c['cd'], cd1,
                      c['dv'], c['dm'], c['dg'], c['gh'], closer[0], closer[1], closer[2], c['eh'], c['de'],
                      len(steps), c['ate'], c['nt'], c['nd'], st, portal, revisit, c['pa'], c['ns'],
                      c['died'], c['split'], c['kills'], c['nu'], c['nth'], first if first is not None else -1])

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            finish()
        if k == 0:
            if started:
                snapshot(rnd)
            started = True
            rnd, actor = p.i32(0), None
            if rnd > MAXR:
                break
        elif k == 1:
            actor = p.i32(0)
            s = side(actor)
            head = bodies[actor][0]
            win = g.window(head)
            m = mem[actor]
            for c in win:
                pr = present.get(c)
                m[c] = None if pr is None else pr['e']
                if pr is not None and pr['s' + s] is None:
                    pr['s' + s] = rnd
            nt = len(win - tseen[s])
            nd = len(win - dseen[actor])
            tseen[s] |= win
            dseen[actor] |= win
            dist = g.dist(head)
            best = [(None, None), (None, None), (None, None)]
            vis = [c for c in win if c in present]
            if vis:
                t = min(vis, key=lambda c: (dist[c], c))
                if dist[t] < INF:
                    best[0] = (dist[t], t)
            known = [c for c, b in m.items() if b is not None and c in present and present[c]['e'] == b]
            if known:
                t = min(known, key=lambda c: (dist[c], c))
                if dist[t] < INF:
                    best[1] = (dist[t], t)
            if present:
                t = min(present, key=lambda c: (dist[c], c))
                if dist[t] < INF:
                    best[2] = (dist[t], t)
            ghosts = [dist[c] for c, b in m.items() if b is not None and (c not in present or present[c]['e'] != b)]
            enemies = [b[0] for i, b in bodies.items() if side(i) != s]
            eh = int(any(c in win for c in enemies))
            de = min((dist[c] for c in enemies), default=INF)
            pa = 0
            ns = 0
            for d in range(4):
                kind, dest = g.moves[head][d]
                if kind == 1:
                    continue
                ns += 1
                if dest in present:
                    pa = max(pa, 1 if kind == 0 else pa if pa == 1 else 2)
            cur = dict(r=rnd, s=s, id=actor, L=len(bodies[actor]), head=head, cd=g.centre(head),
                       dv=best[0][0], tv=best[0][1], dm=best[1][0], tm=best[1][1], dg=best[2][0], tg=best[2][1],
                       gh=min(ghosts, default=None), eh=eh, de=None if de == INF else de, nt=nt, nd=nd, pa=pa, ns=ns,
                       steps=[], ate=0, died=None, split=0, kills=0,
                       nu=sum(side(i) == 'u' for i in bodies), nth=sum(side(i) == 't' for i in bodies))
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                heads = {'u': [], 't': []}
                for i, b in bodies.items():
                    heads[side(i)].append(b[0])
                dd = g.dist(c)
                pr = dict(e=len(pearls), c=c, b=rnd, o='n' if actor is None else 'd',
                          du=min((dd[x] for x in heads['u']), default=INF), dt=min((dd[x] for x in heads['t']), default=INF),
                          su=None, st=None, by=None, er=None, eid=None, eL=None)
                present[c] = pr
                pearls.append(pr)
            else:
                pr = present.pop(c)
                pr['by'], pr['er'], pr['eid'] = side(actor), rnd, actor
                pr['eL'] = len(bodies[actor])
                if cur is not None:
                    cur['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            moved = b[0] != hd
            if moved:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
            if moved and i == actor and cur is not None:
                cur['steps'].append(hd)
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            if cur is not None:
                cur['split'] = 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if cur is not None:
                if i == actor:
                    cur['died'] = CAUSE[reason]
                else:
                    cur['kills'] += 1
            bodies.pop(i)
    finish()
    return dict(game=rec['game'], battle=rec['battle'], map_key=key, group=rec['group'], result=rec['result'],
                our_side=ours, w=w, h=h, L0=rec['sides']['us']['starting_dragons'][0]['initial_length'],
                turns=turns, snaps=snaps,
                pearls=[[q['c'], q['b'], q['o'], q['du'], q['dt'], q['su'], q['st'], q['by'], q['er'], q['eid'], q['eL']] for q in pearls])


def main():
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    per = json.loads(Path('data/analysis/ladder/losses/split/per-game.json').read_text())
    per = [r for n, r in enumerate(sorted(per, key=lambda r: r['game'])) if n % shards == shard]
    geos = {}
    if shard == 0:
        f = open(OUT0, 'w')
    elif shard == 1:
        f = open(OUT1, 'w')
    elif shard == 2:
        f = open(OUT2, 'w')
    else:
        f = open(OUT3, 'w')
    for n, r in enumerate(per):
        f.write(json.dumps(scan(r, geos), separators=(',', ':')) + '\n')
        if n % 10 == 9:
            print(shard, n + 1, len(per), flush=True)
    f.close()
    print('done', shard, len(per))


main()
