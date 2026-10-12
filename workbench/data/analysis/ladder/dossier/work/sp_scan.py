# Scratch (diag-spawn): replays the games of both teams on the 19 shared layouts.
# mode "tiles": per game, births and free round-starts of every tile (rounds 0-300) -> sp_t-<shard>.jsonl
# mode "full":  needs sp_tiles.json (from sp_class.py). Per game: one record per natural pearl birth
#               (where the heads of both sides were at birth and in the 6 rounds before, who ate it, what the
#               eater did in the next 12 rounds), per-class tile totals, the neighbour test (a head beside an
#               empty spawn tile: does it step on, does the pearl come), heads per cluster of fast tiles,
#               and deaths by whether the dragon was standing at a cluster -> sp_f-<shard>.jsonl
# Usage: python3 data/analysis/ladder/dossier/work/sp_scan.py <tiles|full|test> <shard> <shards> [games per layout per team]
# Focal side (index 0) = meow in its ladder games (team O), rank-1 in its games (team R); index 1 = the opponent.
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
RAD = 6
FAST_MAX = 2      # classes 0..2 (mean gap under 8 rounds) make the clusters
POST = 12


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.nbr = []
        for y in range(h):
            for x in range(w):
                row = []
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = edges.get(e, (0, -1))
                    if kind == 1:
                        continue
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.append(dest)
                self.nbr.append(row)
        self.balls = {}
        self.cls = None

    def ball(self, t):
        b = self.balls.get(t)
        if b is None:
            b = {t: 0}
            frontier = [t]
            for d in range(1, RAD + 1):
                nxt = []
                for u in frontier:
                    for v in self.nbr[u]:
                        if v not in b:
                            b[v] = d
                            nxt.append(v)
                frontier = nxt
            self.balls[t] = b
        return b

    def set_classes(self, table):
        cells = self.w * self.h
        self.cls = [-1] * cells
        for t, c in table.items():
            self.cls[int(t)] = c
        fast = [t for t in range(cells) if 0 <= self.cls[t] <= FAST_MAX]
        parent = {t: t for t in fast}

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for t in fast:
            for u, d in self.ball(t).items():
                if d <= 2 and u in parent:
                    parent[find(u)] = find(t)
        roots = sorted({find(t) for t in fast})
        cid = {r: n for n, r in enumerate(roots)}
        self.nclusters = len(roots)
        self.csize = Counter(cid[find(t)] for t in fast)
        self.near1 = [-1] * cells
        self.near2 = [-1] * cells
        best = [9] * cells
        for t in fast:
            c = cid[find(t)]
            for u, d in self.ball(t).items():
                if d <= 2 and d < best[u]:
                    best[u] = d
                    self.near2[u] = c
        for u in range(cells):
            if best[u] <= 1:
                self.near1[u] = self.near2[u]


def win(r):
    return 0 if r <= 100 else 1 if r <= 300 else 2


def scan(row, geos, classes, full):
    root = replay.load(row['replay']).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    cells = w * h
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    key = row['layout_key']
    if key not in geos:
        geos[key] = Geo(w, h, raw)
        if full:
            geos[key].set_classes(classes.get(key, {}))
    g = geos[key]
    assert (g.w, g.h) == (w, h)
    focal = row['our_side']
    side = lambda i: 0 if teams[i] == focal else 1
    born = {i: 0 for i in bodies}
    cls = g.cls if full else None

    st = [0] * cells          # 0 free, 1 pearl, 2 focal body, 3 other body (as an attempt at a round start meets it)
    since = [0] * cells
    cnt = [0] * cells
    acc = [[[0] * cells for s in range(4)] for z in range(2)]
    nbirth = [[0] * cells for z in range(2)]
    step_empty = [[Counter(), Counter()], [Counter(), Counter()]]
    eat_tile = [[Counter(), Counter()], [Counter(), Counter()]]
    state = dict(r=0)

    def add(s, t, a, b):
        lo, hi = max(a, 0), min(b, 100)
        if hi >= lo:
            acc[0][s][t] += hi - lo + 1
        lo, hi = max(a, 101), min(b, 300)
        if hi >= lo:
            acc[1][s][t] += hi - lo + 1

    def change(t, new):
        old = st[t]
        if old != new:
            r = state['r']
            if since[t] <= r:
                add(old, t, since[t], r)
            st[t] = new
            since[t] = r + 1

    def inc(t, s):
        cnt[t] += 1
        if cnt[t] == 1:
            change(t, 2 + s)

    def dec(t):
        cnt[t] -= 1
        if cnt[t] == 0:
            change(t, 0)

    for i, b in bodies.items():
        for c in b:
            cnt[c] += 1
            st[c] = 2 + side(i)

    present = {}
    expected = deque()
    hist = deque(maxlen=7)
    births = []
    trackers = []
    pend, watch = {}, {}
    adj = [[[[0, 0, 0, 0, 0] for c in range(6)] for s in range(2)] for z in range(2)]   # beside, stepped on, other body, free, born
    chist = [[[0] * 5 for s in range(2)] for z in range(2)]
    cboth = [0, 0]
    expo = [[[0, 0, 0] for s in range(2)] for z in range(3)]
    explen = [[[0, 0, 0] for s in range(2)] for z in range(3)]
    deaths = [[[Counter(), Counter(), Counter()] for s in range(2)] for z in range(3)]
    ram_len = [[[0, 0, 0] for s in range(2)] for z in range(3)]
    streak, last_c, cstate = {}, {}, {}
    rnd, actor, need_setup, just_ate = 0, None, False, -1
    turns = [[0, 0], [0, 0], [0, 0]]

    def setup():
        z = win(rnd)
        if z < 2:
            pend.clear()
            ccount = {}
            for i, b in bodies.items():
                s = side(i)
                hd = b[0]
                for nb in g.nbr[hd]:
                    c = cls[nb]
                    if c >= 0 and cnt[nb] == 0 and nb not in present:
                        flags = pend.get(nb)
                        if flags is None:
                            flags = pend[nb] = [0, 0]
                        if not flags[s]:
                            flags[s] = 1
                            adj[z][s][c][0] += 1
                c2 = g.near2[hd]
                if c2 >= 0:
                    ccount[(s, c2)] = ccount.get((s, c2), 0) + 1
            for c2 in range(g.nclusters):
                a, b2 = ccount.get((0, c2), 0), ccount.get((1, c2), 0)
                chist[z][0][min(a, 4)] += 1
                chist[z][1][min(b2, 4)] += 1
                if a and b2:
                    cboth[z] += 1
        for i, b in bodies.items():
            c1 = g.near1[b[0]]
            if c1 >= 0 and last_c.get(i, -1) == c1:
                streak[i] = streak.get(i, 0) + 1
            else:
                streak[i] = 1 if c1 >= 0 else 0
            last_c[i] = c1
            k = 2 if streak[i] >= 3 else 1 if streak[i] >= 1 else 0
            cstate[i] = k
            s = side(i)
            expo[z][s][k] += 1
            explen[z][s][k] += len(b)

    def heads():
        return [[(i, b[0]) for i, b in bodies.items() if side(i) == s] for s in (0, 1)]

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            state['r'] = rnd
            if full:
                watch.clear()
                z = min(win(rnd), 1)
                for t, flags in pend.items():
                    c = cls[t]
                    s0 = 1 if t in present else st[t] if cnt[t] else 0
                    for s in (0, 1):
                        if flags[s]:
                            if s0 == 0:
                                adj[z][s][c][3] += 1
                            elif s0 == 2 + s:
                                adj[z][s][c][1] += 1
                            else:
                                adj[z][s][c][2] += 1
                    if s0 == 0:
                        watch[t] = flags
                pend.clear()
                hist.append(heads())
                for tr in trackers:
                    b = bodies.get(tr[1])
                    tr[0][15] += 'x' if b is None else str(min(tr[2].get(b[0], 9), 9))
                if trackers and len(trackers[0][0][15]) >= POST:
                    trackers[:] = [tr for tr in trackers if len(tr[0][15]) < POST]
                need_setup = True
        elif k == 1:
            actor = p.i32(0)
            if full and need_setup:
                need_setup = False
                setup()
            turns[win(rnd)][side(actor)] += 1
            just_ate = -1
        elif k == 3:
            t = replay.point(p.pointer(0))
            t = t[1] * w + t[0]
            if p.u32(0):
                if expected:
                    xy = expected.popleft()
                    assert xy == t
                    present[t] = None
                    change(t, 1)
                else:
                    assert actor is None
                    z = win(rnd)
                    if z < 2:
                        nbirth[z][t] += 1
                    rec = None
                    if full and z < 2:
                        c = cls[t]
                        flags = watch.get(t)
                        if flags is not None:
                            for s in (0, 1):
                                if flags[s]:
                                    adj[z][s][c][4] += 1
                        ball = g.ball(t)
                        ds = ['', '']
                        near = {}
                        nlen = 0
                        for kk in range(len(hist)):
                            snap = hist[-1 - kk]
                            for s in (0, 1):
                                best = 9
                                for i, hd in snap[s]:
                                    d = ball.get(hd, 9)
                                    if d < best:
                                        best = d
                                        if kk == 0 and s == 0 and i in bodies:
                                            nlen = len(bodies[i])
                                    if kk == 0 and d <= RAD:
                                        near[i] = d
                                ds[s] += str(best)
                        zone = 0
                        top, tl = -1, 0
                        for i, b in bodies.items():
                            if side(i) == 0 and len(b) > tl:
                                top, tl = i, len(b)
                        if top >= 0:
                            hd = bodies[top][0]
                            dx = abs(hd % w - t % w)
                            dy = abs(hd // w - t // w)
                            zone = int(min(dx, w - dx) + min(dy, h - dy) <= 9)
                        n2 = [sum(1 for i, hd in hist[-1][s] if ball.get(hd, 9) <= 2) for s in (0, 1)]
                        rec = [rnd, t, c, ds[0], ds[1], zone, nlen, n2[0], n2[1], -1, -1, -1, 0, 0, 9, '', near]
                        births.append(rec)
                    present[t] = rec
                    change(t, 1)
            else:
                rec = present.pop(t)
                change(t, 0)
                just_ate = t
                z = win(rnd)
                s = side(actor)
                if z < 2:
                    eat_tile[z][s][t] += 1
                if rec is not None:
                    near = rec.pop()
                    rec[9:15] = [rnd, s, actor, len(bodies[actor]), min(rnd - born[actor], 999), near.get(actor, 9)]
                    trackers.append((rec, actor, g.ball(t)))
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                inc(hd, side(i))
                z = win(rnd)
                if hd != just_ate and z < 2:
                    step_empty[z][side(i)][hd] += 1
                just_ate = -1
            while len(b) > 1 and b[-1] != tl:
                dec(b.pop())
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            for cell in bodies.get(a, ()):
                dec(cell)
            teams[c] = teams[a] = 'AB'[p.u16(8)]
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
                for cell in bodies[i]:
                    inc(cell, side(i))
            born[c] = rnd
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            s = side(i)
            z = win(rnd)
            if full:
                kst = cstate.get(i, 0)
                if reason == 3:
                    if i == actor:
                        cause = 'rm'
                    else:
                        cause = 'rvx' if side(actor) != s else 'rvs'
                        ram_len[z][s][kst] += len(b)
                else:
                    cause = ('w', 'o', 'b', '?', 'n')[reason] if reason < 5 else '?'
                deaths[z][s][kst][cause] += 1
            for seg, cell in enumerate(b):
                dec(cell)
                if seg % 2 == 0:
                    expected.append(cell)
            bodies.pop(i)
    last = rnd
    for t in range(cells):
        if since[t] <= last:
            add(st[t], t, since[t], last)
    out = dict(game=row['game'], team=row['tm'], layout=key, w=w, h=h, focal=focal, result=row['result'],
               last=last, rating=row.get('opponent_rating'))
    if not full:
        out['births'] = {t: nbirth[0][t] + nbirth[1][t] for t in range(cells) if nbirth[0][t] + nbirth[1][t]}
        out['free'] = [acc[0][0][t] + acc[1][0][t] for t in range(cells)]
        return out
    for rec in births:
        if isinstance(rec[-1], dict):
            rec.pop()
    tot = [[[0] * 10 for c in range(6)] for z in range(2)]
    for z in range(2):
        for t in range(cells):
            c = cls[t]
            if c < 0:
                continue
            row_ = tot[z][c]
            row_[0] += acc[z][0][t]
            row_[1] += acc[z][1][t]
            row_[2] += acc[z][2][t]
            row_[3] += acc[z][3][t]
            row_[4] += nbirth[z][t]
            row_[5] += step_empty[z][0][t]
            row_[6] += step_empty[z][1][t]
            row_[7] += eat_tile[z][0][t]
            row_[8] += eat_tile[z][1][t]
            row_[9] += 1
    out.update(births=births, tot=tot, adj=adj, chist=chist, cboth=cboth, nclusters=g.nclusters,
               csize=sorted(g.csize.values()), expo=expo, explen=explen,
               deaths=[[[dict(d) for d in y] for y in x] for x in deaths], ram_len=ram_len, turns=turns)
    return out


def main():
    mode, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    full = mode != 'tiles'
    rows = []
    for tm, f in (('O', 'data/analysis/ladder/dossier/per-game.jsonl'),
                  ('R', 'data/analysis/ladder/dossier/target/per-game-top1.jsonl')):
        seen = Counter()
        for line in open(f):
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            seen[r['layout_key']] += 1
            if limit and seen[r['layout_key']] > limit:
                continue
            rows.append(dict(game=r['game'], tm=tm, layout_key=r['layout_key'], replay=r['replay'],
                             our_side=r['our_side'], result=r['result'], opponent_rating=r.get('opponent_rating')))
    rows.sort(key=lambda r: (r['layout_key'], r['tm'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    classes = json.loads(Path(OUT + 'sp_tiles.json').read_text())['cls'] if full else {}
    geos, out, bad = {}, [], []
    for n, r in enumerate(rows):
        try:
            out.append(json.dumps(scan(r, geos, classes, full), separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 20 == 19:
            print(n + 1, len(rows), len(bad), flush=True)
    text = '\n'.join(out) + '\n'
    if mode == 'test':
        Path(OUT + 'sp_test.jsonl').write_text(text)
    elif not full:
        if shard == 0:
            Path(OUT + 'sp_t-0.jsonl').write_text(text)
        elif shard == 1:
            Path(OUT + 'sp_t-1.jsonl').write_text(text)
        elif shard == 2:
            Path(OUT + 'sp_t-2.jsonl').write_text(text)
        elif shard == 3:
            Path(OUT + 'sp_t-3.jsonl').write_text(text)
        elif shard == 4:
            Path(OUT + 'sp_t-4.jsonl').write_text(text)
        else:
            Path(OUT + 'sp_t-5.jsonl').write_text(text)
    else:
        if shard == 0:
            Path(OUT + 'sp_f-0.jsonl').write_text(text)
        elif shard == 1:
            Path(OUT + 'sp_f-1.jsonl').write_text(text)
        elif shard == 2:
            Path(OUT + 'sp_f-2.jsonl').write_text(text)
        elif shard == 3:
            Path(OUT + 'sp_f-3.jsonl').write_text(text)
        elif shard == 4:
            Path(OUT + 'sp_f-4.jsonl').write_text(text)
        else:
            Path(OUT + 'sp_f-5.jsonl').write_text(text)
    print('done', mode, shard, len(out), 'bad', bad)


main()
