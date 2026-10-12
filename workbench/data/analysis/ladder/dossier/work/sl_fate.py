# Scratch (diag-split): what becomes of a split. For every split of the focal side: the class of the parent's state
# on that turn (same classes as sl_agg.py), the child size, and for 20 rounds after it whether the child and the
# parent die (within 2, 5, 20 rounds; boxed in or not) and how many pearls each eats. -> sl_fate-<shard>.jsonl
# Usage: python3 data/analysis/ladder/dossier/work/sl_fate.py <shard> <shards> [games per layout per team]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LIMIT = 64
ROOM_CAP = 8
NEAR = 3
MARKS = (50, 100, 150, 200, 250, 300, 350, 400, 450, 500)
LAND = (100, 200, 300, 400)


def band(r):
    return 0 if r <= 100 else 1 if r <= 150 else 2 if r <= 200 else 3 if r <= 300 else 4 if r <= 400 else 5


def lb(n):
    return 0 if n == 2 else 1 if n == 3 else 2 if n == 4 else 3 if n <= 7 else 4


def elb(n):
    return 0 if n == 4 else 1 if n == 5 else 2 if n <= 7 else 3


def nb(n):
    return 0 if n < 32 else 1 if n < 56 else 2 if n < 60 else 3 if n < LIMIT else 4


def lifeb(n):
    return 0 if n <= 0 else 1 if n == 1 else 2 if n == 2 else 3 if n <= 5 else 4 if n <= 10 else 5 if n <= 20 else 6 if n <= 40 else 7 if n <= 80 else 8 if n <= 160 else 9


def durb(n):
    return 0 if n == 1 else 1 if n == 2 else 2 if n <= 5 else 3 if n <= 20 else 4


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.nbr = []
        self.portal = []
        for y in range(h):
            for x in range(w):
                row = []
                flag = 0
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = edges.get(e, (0, -1))
                    if kind == 1:
                        continue
                    if kind == 2:
                        flag = 1
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.append(dest)
                self.nbr.append(row)
                self.portal.append(flag)




def cls_of(k, big):
    bd, el, nk, role, rb, portal, enemy, free = k
    late = bd >= 2 if big else bd >= 4
    if role == 0 and bd >= 3:
        return 'queen>200'
    if role == 1 and late:
        return 'longest,late'
    if late and el > 0:
        return 'late,L>4'
    if nk == 4:
        return 'hard64'
    if nk == 3:
        return 'soft60-63'
    if rb == 0:
        return 'room0'
    if rb == 1:
        return 'room1-3'
    if portal:
        return 'portal'
    if not free:
        return 'headboxed'
    if enemy:
        return 'enemy<=3'
    return 'open,L4' if el == 0 else 'open,L5+'


def scan(row, geos):
    root = replay.load(row['replay']).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    cells = w * h
    big = cells > 1200
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
    g = geos[key]
    nbr = g.nbr
    focal = row['our_side']
    sd = {i: (0 if teams[i] == focal else 1) for i in bodies}
    queen = min(i for i in bodies if sd[i] == 0)
    cnt = [0] * cells
    for b in bodies.values():
        for c in b:
            cnt[c] += 1
    alive = sum(1 for i in bodies if sd[i] == 0)
    expected = deque()
    track = defaultdict(list)
    done = []

    def feat(i, bd):
        b = bodies[i]
        n = len(b)
        hd, tl = b[0], b[-1]
        hx, hy = hd % w, hd // w
        tx, ty = tl % w, tl // w
        mx = 0
        hit = 0
        for j, x in bodies.items():
            if sd[j] == 0:
                if len(x) > mx:
                    mx = len(x)
            elif not hit:
                e = x[0]
                ex, ey = e % w, e // w
                dx = abs(ex - hx)
                dy = abs(ey - hy)
                if min(dx, w - dx) + min(dy, h - dy) <= NEAR:
                    hit = 1
                else:
                    dx = abs(ex - tx)
                    dy = abs(ey - ty)
                    if min(dx, w - dx) + min(dy, h - dy) <= NEAR:
                        hit = 1
        role = 0 if i == queen else 1 if n >= mx else 2
        seen = {tl}
        frontier = [tl]
        rm = 0
        while frontier and rm < ROOM_CAP:
            nxt = []
            for u in frontier:
                for v in nbr[u]:
                    if v not in seen and cnt[v] == 0:
                        seen.add(v)
                        nxt.append(v)
                        rm += 1
            frontier = nxt
        rb = 0 if rm == 0 else 1 if rm < 4 else 2 if rm < ROOM_CAP else 3
        free = 0
        for v in nbr[hd]:
            if cnt[v] == 0:
                free = 1
                break
        return (bd, elb(n), nb(alive), role, rb, g.portal[tl], hit, free)

    rnd, actor = 0, None
    cur = None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            cur = None
            b = bodies.get(actor)
            if b is not None and sd[actor] == 0 and len(b) >= 4:
                cur = feat(actor, band(rnd))
        elif k == 3:
            t = replay.point(p.pointer(0))
            t = t[1] * w + t[0]
            if p.u32(0):
                if expected:
                    expected.popleft()
            elif actor in track:
                for tr in track[actor]:
                    if rnd - tr[2] <= 20:
                        tr[3] += 1
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                cnt[hd] += 1
            while len(b) > 1 and b[-1] != tl:
                cnt[b.pop()] -= 1
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            s = sd[a]
            for cell in bodies[a]:
                cnt[cell] -= 1
            sd[c] = s
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
                for cell in bodies[i]:
                    cnt[cell] += 1
            if s == 0:
                alive += 1
                if cur is not None and a == actor:
                    name = cls_of(cur, big) + '|' + ('c2' if len(bodies[c]) == 2 else 'c3+') + '|' + ('r0' if cur[0] == 0 else 'r1' if cur[0] <= 3 else 'r2')
                    name2 = 'vol%d|rm%d|L%d|N%d' % (cur[7], cur[4], cur[1], cur[2])
                    for role, i in ((0, c), (1, a)):
                        tr = [name, role, rnd, 0, -1, 0, name2]
                        track[i].append(tr)
                        done.append(tr)
                    cur = None
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            if sd[i] == 0:
                alive -= 1
                if i in track:
                    free = 0
                    for v in nbr[b[0]]:
                        if cnt[v] == 0:
                            free = 1
                            break
                    for tr in track[i]:
                        if tr[4] < 0 and rnd - tr[2] <= 20:
                            tr[4] = rnd - tr[2]
                            tr[5] = 1 if (reason != 3 and not free) else 2 if reason == 3 else 3
                    track.pop(i)
            for seg, cell in enumerate(b):
                cnt[cell] -= 1
                if seg % 2 == 0:
                    expected.append(cell)
            bodies.pop(i)
    out = {}
    for tr in done:
        for name in (tr[0], tr[6]):
            v = out.get(name)
            if v is None:
                v = out[name] = [0] * 20
            v[0] += tr[1] == 0
            if tr[2] > rnd - 20:
                continue
            o = 1 if tr[1] == 0 else 10
            v[o] += 1
            d = tr[4]
            if d >= 0:
                v[o + 1] += d <= 2
                v[o + 2] += d <= 5
                v[o + 3] += 1
                v[o + 4] += tr[5] == 1 and d <= 5
                v[o + 5] += tr[5] == 2 and d <= 5
            v[o + 6] += tr[3]
            v[o + 7] += tr[3] > 0
    return dict(game=row['game'], tm=row['tm'], layout=key, cells=cells, fate=out)


def main():
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
    geos, out, bad = {}, [], []
    for n, r in enumerate(rows):
        try:
            out.append(json.dumps(scan(r, geos), separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 20 == 19:
            print(n + 1, len(rows), len(bad), flush=True)
    text = '\n'.join(out) + '\n'
    if limit:
        Path(OUT + 'sl_fate-test.jsonl').write_text(text)
    elif shard == 0:
        Path(OUT + 'sl_fate-0.jsonl').write_text(text)
    elif shard == 1:
        Path(OUT + 'sl_fate-1.jsonl').write_text(text)
    elif shard == 2:
        Path(OUT + 'sl_fate-2.jsonl').write_text(text)
    else:
        Path(OUT + 'sl_fate-3.jsonl').write_text(text)
    print('done', shard, len(out), 'bad', bad)


main()
