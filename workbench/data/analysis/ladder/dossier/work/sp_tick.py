# Scratch (diag-spawn): spawn attempts seen through the mirror tile. A tile and its mirror share one countdown
# (rules/pearls.md), so when a pearl is born on a tile, its mirror tried in the same round. For every such
# attempt (rounds 0-300) this records what the attempt met on the tile: born, a pearl still lying, or a body
# (whose side, head or not, and whether that dragon came onto the tile by eating or onto an empty tile).
# For attempts on a tile that was empty one round earlier (a bot beside it saw the countdown at 1) it also
# records where the nearest head of each side was one round earlier and what happened.
# Usage: python3 data/analysis/ladder/dossier/work/sp_tick.py <shard> <shards> [games per layout per team]
# Needs sp_tiles.json. Writes sp_k-<shard>.jsonl (one line per game, counters only).
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
RAD = 4


class Geo:
    def __init__(self, w, h, raw, sym):
        self.w, self.h, self.sym = w, h, sym
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
        self.mirror = []
        for y in range(h):
            for x in range(w):
                mx = w - 1 - x if 'y' in sym else x
                my = h - 1 - y if 'x' in sym else y
                self.mirror.append(my * w + mx)

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


def scan(row, geos, classes):
    root = replay.load(row['replay']).root()
    text = root.text(0)
    lines = text.splitlines()
    w, h = map(int, lines[0].split()[1:3])
    cells = w * h
    bodies, teams, raw, sym = {}, {}, [], ''
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
        elif q and q[0] == 'SYMMETRY':
            sym = q[1]
    key = row['layout_key']
    if key not in geos:
        geos[key] = Geo(w, h, raw, sym)
        cl = [-1] * cells
        for t, c in classes.get(key, {}).items():
            cl[int(t)] = c
        geos[key].cls = cl
    g = geos[key]
    cls = g.cls
    focal = row['our_side']
    side = lambda i: 0 if teams[i] == focal else 1

    st = [0] * cells
    since = [0] * cells
    prev_st = [0] * cells
    prev_since = [0] * cells
    cnt = [0] * cells
    owner = [-1] * cells
    entry = {i: {c: 0 for c in b} for i, b in bodies.items()}    # dragon -> tile -> 1 if it came onto the tile by eating
    state = dict(r=0)

    def change(t, new):
        old = st[t]
        if old != new:
            prev_st[t], prev_since[t] = old, since[t]
            st[t] = new
            since[t] = state['r'] + 1

    def inc(t, i):
        cnt[t] += 1
        owner[t] = i
        if cnt[t] == 1:
            change(t, 2 + side(i))

    def dec(t):
        cnt[t] -= 1
        if cnt[t] == 0:
            change(t, 0)

    for i, b in bodies.items():
        for c in b:
            cnt[c] += 1
            owner[c] = i
            st[c] = 2 + side(i)

    present = set()
    expected = deque()
    hist = deque(maxlen=3)
    tick = []
    A = Counter()
    B = Counter()
    B2 = Counter()
    BL = Counter()
    C = Counter()
    A2 = Counter()
    BM = Counter()
    BLM = Counter()
    CM = Counter()
    found = []
    watch = {}
    rnd, actor, need_setup, just_ate = 0, None, False, -1

    def near(snap, ball):
        best, bl = 9, 0
        for hd, ln in snap:
            d = ball.get(hd, 9)
            if d < best:
                best, bl = d, ln
        return best, bl

    def setup():
        if not tick or rnd > 300:
            tick.clear()
            return
        z = 'a' if rnd <= 100 else 'b'
        born = {t: fs for t, fs in tick}
        todo = set(born)
        for t in born:
            todo.add(g.mirror[t])
        for m in todo:
            c = cls[m]
            free1 = free2 = False        # the tile was empty at the start of round r-1 / r-2
            step1 = step2 = -1           # side that came onto the empty tile during round r-1 / r-2 and covers it now
            if m in born:
                out = 'born'
                free1 = born[m] <= rnd - 1
                free2 = born[m] <= rnd - 2
            elif m in present:
                out = 'pearl'
            elif cnt[m] > 0:
                i = owner[m]
                if i not in bodies or m not in entry[i]:
                    out = 'body?'
                else:
                    s = side(i)
                    head = bodies[i][0] == m
                    ate = entry[i][m]
                    out = 'FX'[s] + ('h' if head else 'b') + ('_ate' if ate else '_empty')
                    if not ate and prev_st[m] == 0:
                        if since[m] == rnd and prev_since[m] <= rnd - 1:
                            free1, step1 = True, s
                            free2 = prev_since[m] <= rnd - 2
                        elif since[m] == rnd - 1 and prev_since[m] <= rnd - 2:
                            free2, step2 = True, s
            else:
                out = 'free_noborn'
            A[z + '|%d|%s' % (c, out)] += 1
            mb = m not in born or g.mirror[m] in born      # the mirror tile was born too: both tiles are on the same footing
            if mb and g.mirror[m] != m:
                A2[z + '|%d|%s' % (c, out)] += 1
            else:
                mb = False
            if free1 and len(hist) >= 2:
                ball = g.ball(m)
                for s in (0, 1):
                    d1, ln = near(hist[-2][s], ball)
                    if d1 > 3:
                        continue
                    if step1 == s:
                        res = 'on'
                    elif step1 >= 0:
                        res = 'other_on'
                    else:
                        d0, unused = near(hist[-1][s], ball)
                        res = 'born_d%d' % min(d0, 3)
                        if d1 <= 2:
                            watch.setdefault(m, []).append((z + '|%d|%s|%d|%d' % (c, 'FX'[s], d1, min(d0, 3)), rnd, s))
                    B[z + '|%d|%s|%d|%s' % (c, 'FX'[s], d1, res)] += 1
                    if mb:
                        BM[z + '|%d|%s|%d|%s' % (c, 'FX'[s], d1, res)] += 1
                    if d1 == 1:
                        BL[z + '|%s|%d|%s' % ('FX'[s], min(ln, 5), 'on' if res == 'on' else 'off')] += 1
                        if mb:
                            BLM[z + '|%s|%d|%s' % ('FX'[s], min(ln, 5), 'on' if res == 'on' else 'off')] += 1
                        if res == 'on' and len(found) < 400:
                            found.append((rnd, m % w, m // w, 'FX'[s], c, ln))
            if free2 and len(hist) >= 3:
                ball = g.ball(m)
                for s in (0, 1):
                    d2, ln = near(hist[-3][s], ball)
                    if d2 > 2:
                        continue
                    res = ('on2' if step2 == s else 'other_on2' if step2 >= 0 else
                           'on1' if step1 == s else 'other_on1' if step1 >= 0 else 'born')
                    C[z + '|%d|%s|%d|%s' % (c, 'FX'[s], d2, res)] += 1
                    if mb:
                        CM[z + '|%d|%s|%d|%s' % (c, 'FX'[s], d2, res)] += 1
        tick.clear()

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            state['r'] = rnd
            hist.append([[(b[0], len(b)) for i, b in bodies.items() if side(i) == s] for s in (0, 1)])
            need_setup = True
        elif k == 1:
            actor = p.i32(0)
            if need_setup:
                need_setup = False
                setup()
            just_ate = -1
        elif k == 3:
            t = replay.point(p.pointer(0))
            t = t[1] * w + t[0]
            if p.u32(0):
                if expected:
                    xy = expected.popleft()
                    assert xy == t
                else:
                    assert actor is None
                    tick.append((t, since[t] if st[t] == 0 else 9999))
                present.add(t)
                change(t, 1)
            else:
                present.discard(t)
                change(t, 0)
                just_ate = t
                for pre, r0, s in watch.pop(t, ()):
                    B2[pre + '|%s|%d' % ('self' if side(actor) == s else 'other', min(rnd - r0, 3))] += 1
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                entry[i][hd] = 1 if hd == just_ate else 0
                inc(hd, i)
                just_ate = -1
            while len(b) > 1 and b[-1] != tl:
                c = b.pop()
                entry[i].pop(c, None)
                dec(c)
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            old = entry.get(a, {})
            for cell in bodies.get(a, ()):
                dec(cell)
            teams[c] = teams[a] = 'AB'[p.u16(8)]
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
                entry[i] = {cell: old.get(cell, 0) for cell in bodies[i]}
                for cell in bodies[i]:
                    inc(cell, i)
        elif k == 11:
            i = p.i32(0)
            for seg, cell in enumerate(bodies[i]):
                dec(cell)
                if seg % 2 == 0:
                    expected.append(cell)
            bodies.pop(i)
            entry.pop(i, None)
    return dict(game=row['game'], team=row['tm'], layout=key, sym=sym, last=rnd, A=dict(A), B=dict(B), B2=dict(B2), BL=dict(BL), C=dict(C),
                A2=dict(A2), BM=dict(BM), BLM=dict(BLM), CM=dict(CM), found=found if row.get('find') else [])


def find(game):
    classes = json.loads(Path(OUT + 'sp_tiles.json').read_text())['cls']
    for tm, f in (('O', 'data/analysis/ladder/dossier/per-game.jsonl'),
                  ('R', 'data/analysis/ladder/dossier/target/per-game-top1.jsonl')):
        for line in open(f):
            if ('"game":%d,' % game) in line:
                r = json.loads(line)
                if r['relation'] == 'us':
                    res = scan(dict(game=game, tm=tm, layout_key=r['layout_key'], replay=r['replay'], our_side=r['our_side'], find=1), {}, classes)
                    print(tm, r['layout_key'], 'round, x, y, side, class, length of the head that stepped on:')
                    print(res['found'])


def main():
    if sys.argv[1] == 'find':
        find(int(sys.argv[2]))
        return
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
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
            rows.append(dict(game=r['game'], tm=tm, layout_key=r['layout_key'], replay=r['replay'], our_side=r['our_side']))
    rows.sort(key=lambda r: (r['layout_key'], r['tm'], r['game']))
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    classes = json.loads(Path(OUT + 'sp_tiles.json').read_text())['cls']
    geos, out, bad = {}, [], []
    for n, r in enumerate(rows):
        try:
            out.append(json.dumps(scan(r, geos, classes), separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 20 == 19:
            print(n + 1, len(rows), len(bad), flush=True)
    text = '\n'.join(out) + '\n'
    if shards > 6:
        Path(OUT + 'sp_ktest.jsonl').write_text(text)
    elif shard == 0:
        Path(OUT + 'sp_k-0.jsonl').write_text(text)
    elif shard == 1:
        Path(OUT + 'sp_k-1.jsonl').write_text(text)
    elif shard == 2:
        Path(OUT + 'sp_k-2.jsonl').write_text(text)
    elif shard == 3:
        Path(OUT + 'sp_k-3.jsonl').write_text(text)
    elif shard == 4:
        Path(OUT + 'sp_k-4.jsonl').write_text(text)
    else:
        Path(OUT + 'sp_k-5.jsonl').write_text(text)
    print('done', shard, len(out), 'bad', bad)


main()
