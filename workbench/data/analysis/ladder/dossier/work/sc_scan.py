# Scratch (diag-sacrifice): replays the 500 main ladder games of dossier/input-snapshot.json and writes one line
# per game: every death by "no valid action" and every head-on of both sides with where the dragon stood, its
# team mates, the nearest enemy head and who ate what it dropped; a compact row for every death up to round 300;
# standings every 25 rounds; turns, splits and pearls eaten by origin per window.
# Usage: python3 data/analysis/ladder/dossier/work/sc_scan.py <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAUSE = ('wall', 'own', 'body', 'headon', 'noact')
ROOM_CAP = 60


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
        n = w * h
        self.open = [[dest for kind, dest in self.moves[c] if kind != 1] for c in range(n)]
        self.deg = [len(set(self.open[c])) for c in range(n)]
        # dead-end cells: what is left outside the 2-core of the static graph (leaf pruning)
        deg = [len(set(self.open[c])) for c in range(n)]
        gone = [False] * n
        queue = deque(c for c in range(n) if deg[c] <= 1)
        while queue:
            c = queue.popleft()
            if gone[c]:
                continue
            gone[c] = True
            for z in set(self.open[c]):
                if not gone[z]:
                    deg[z] -= 1
                    if deg[z] <= 1:
                        queue.append(z)
        self.deadend = gone


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def window(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


def scan(row, geos):
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
    key = (row['map_key'], w, h)
    if key not in geos:
        geos[key] = Geo(w, h, raw)
    g = geos[key]
    ours = row['our_side']
    side = lambda i: 'u' if teams[i] == ours else 't'
    queen = dict(u=min(i for i in bodies if side(i) == 'u'), t=min(i for i in bodies if side(i) == 't'))
    born = {i: 0 for i in bodies}
    parent_of = {i: -1 for i in bodies}
    last_split = {}
    child_len = {}
    last_eat = {i: 0 for i in bodies}
    nturns = Counter()
    trail = {i: deque([b[0]], maxlen=7) for i, b in bodies.items()}
    series = {}
    turns = dict(u=[0, 0, 0, 0], t=[0, 0, 0, 0])
    splits = dict(u=[0, 0, 0, 0], t=[0, 0, 0, 0])
    eats = dict(u=[Counter() for _ in range(4)], t=[Counter() for _ in range(4)])
    q_eats = dict(u=[Counter() for _ in range(4)], t=[Counter() for _ in range(4)])
    top_eats = dict(u=[Counter() for _ in range(4)], t=[Counter() for _ in range(4)])
    events, compact = [], []
    present = {}
    expected = deque()
    turn_deaths = []
    rnd, actor, used, dirs, act = 0, None, 0, [], None

    def gap(a, c):
        return torus(a % w, c % w, w) + torus(a // w, c // w, h)

    def longest(s, skip=-1):
        best = 0
        for i, b in bodies.items():
            if i != skip and side(i) == s and len(b) > best:
                best = len(b)
        return best

    def stand():
        out = []
        for s in ('u', 't'):
            n = tot = big = 0
            for i, b in bodies.items():
                if side(i) == s:
                    n += 1
                    tot += len(b)
                    big = max(big, len(b))
            out += [n, big, tot, len(bodies.get(queen[s], ()))]
        return out

    def context(i):
        s = side(i)
        b = bodies[i]
        head = b[0]
        occ = {}
        for z, bb in bodies.items():
            for c in bb:
                occ[c] = z
        free = [c for c in set(g.open[head]) if c not in occ]
        seen = set(free)
        queue = deque(free)
        while queue and len(seen) < ROOM_CAP:
            c = queue.popleft()
            for z in g.open[c]:
                if z not in occ and z not in seen:
                    seen.add(z)
                    queue.append(z)
        adj = set()
        for c in set(g.open[head]):
            z = occ.get(c, i)
            if z != i:
                adj.add(z)
        mates = sorted((gap(head, bb[0]), z, len(bb)) for z, bb in bodies.items() if z != i and side(z) == s)[:4]
        foes = sorted((gap(head, bb[0]), z, len(bb)) for z, bb in bodies.items() if side(z) != s)[:2]
        rest = longest(s, i)
        tgt = (-1, 0, -1)
        for z, bb in bodies.items():
            if z != i and side(z) == s and gap(head, bb[0]) <= 10 and len(bb) > tgt[1]:
                tgt = (z, len(bb), gap(head, bb[0]))
        q = queen[s]
        old = trail[i][0]
        return dict(free=len(free), room=min(len(seen), ROOM_CAP), deg=g.deg[head], dead=int(g.deadend[head]),
                    adj_mate=[[z, len(bodies[z]), int(bodies[z][0] in g.open[head])] for z in adj if side(z) == s],
                    adj_foe=[[z, len(bodies[z])] for z in adj if side(z) != s],
                    mates=[[d, z, n, int(z == q), int(n >= rest)] for d, z, n in mates],
                    foes=[[d, z, n] for d, z, n in foes], rest=rest, tgt=list(tgt),
                    q_alive=int(q in bodies and q != i), q_len=len(bodies.get(q, ())) if q != i else 0,
                    q_dist=gap(head, bodies[q][0]) if q in bodies and q != i else -1,
                    pearl_adj=int(any(c in present for c in free)),
                    pearl_near=sum(1 for c in present if gap(head, c) <= 3),
                    n_side=sum(1 for z in bodies if side(z) == s) - 1,
                    n_foe=sum(1 for z in bodies if side(z) != s),
                    moved6=gap(old, head), tgt_was=gap(old, bodies[tgt[0]][0]) if tgt[0] >= 0 else -1)

    def finish_turn():
        hs = [d for d in turn_deaths if d['reason'] == 3]
        if len(hs) == 2:
            a, c = hs
            same = a['side'] == c['side']
            for own, other in ((a, c), (c, a)):
                own.update(o_side=other['side'], o_id=other['id'], o_len=other['L'], st=int(same),
                           o_q=other['q'], o_top=other['top'])
        turn_deaths.clear()

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            finish_turn()
        if k == 0:
            new = p.i32(0)
            if rnd % 25 == 0 and new != rnd:
                series[rnd] = stand()
            rnd, actor = new, None
        elif k == 1:
            actor = p.i32(0)
            dirs, used, act = [], 0, None
            turns[side(actor)][window(rnd)] += 1
            nturns[actor] += 1
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            fuel = p.pointer(1)
            act = ('timeout' if p.bit(32) or (fuel is not None and fuel.bit(64)) else
                   ('sprint', 'split', 'noact')[a.u16(0)] if a and a.u16(0) < 3 else 'noact')
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                if expected:
                    xy, rec = expected.popleft()
                    assert xy == c
                    present[c] = rec
                else:
                    present[c] = None
            else:
                rec = present.pop(c)
                s = side(actor)
                L = len(bodies[actor])
                is_top = int(L >= longest(s, actor))
                is_q = int(actor == queen[s])
                if rec is None:
                    origin = 'n'
                else:
                    d = rec
                    if d['side'] != s:
                        origin = 'e'
                    elif d['reason'] == 4:
                        origin = 's'
                    elif d['reason'] == 3 and d.get('st'):
                        origin = 'h'
                    else:
                        origin = 'o'
                    if 'p' in d:
                        d['p'].append([s, rnd - d['r'], actor, L, is_q, is_top])
                wn = window(rnd)
                eats[s][wn][origin] += 1
                if is_q:
                    q_eats[s][wn][origin] += 1
                if is_top:
                    top_eats[s][wn][origin] += 1
                last_eat[actor] = rnd
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                trail[i].append(hd)
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            par, kid = p.i32(0), p.i32(4)
            for z, i in enumerate((par, kid)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            splits[side(par)][window(rnd)] += 1
            born[kid] = rnd
            parent_of[kid] = par
            last_eat[kid] = rnd
            last_split[par] = rnd
            child_len[par] = len(bodies[kid])
            trail[kid] = deque([bodies[kid][0]], maxlen=7)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            b = bodies[i]
            L = len(b)
            head = b[0]
            cause = CAUSE[reason] if reason < 4 else (act or 'noact') if i == actor else 'noact'
            d = dict(r=rnd, id=i, L=L, cause=cause, reason=reason, side=s, x=head % w, y=head // w,
                     top=int(L >= longest(s, i)), q=int(i == queen[s]), mover=int(i == actor),
                     born=born[i], par=parent_of[i], split_r=last_split.get(i, -1), split_child=child_len.get(i, 0),
                     nturns=nturns[i], last_eat=last_eat[i], np=(L + 1) // 2)
            if rnd <= 300 or reason >= 3:
                d.update(context(i))
            if reason >= 3:
                d['p'] = []
                events.append(d)
            if rnd <= 300:
                compact.append([rnd, s, L, cause, d.get('free', -1), d.get('room', -1), d['q'], d['top'],
                                rnd - born[i], rnd - last_split[i] if i in last_split else -1, d.get('dead', -1),
                                nturns[i], d.get('n_side', -1)])
            turn_deaths.append(d)
            for seg, c in enumerate(b):
                if seg % 2 == 0:
                    expected.append((c, d))
            bodies.pop(i)
    finish_turn()
    final = stand()
    series[rnd] = final
    want = row['final']
    assert final == [want['us']['alive'], want['us']['longest'], want['us']['total'], want['us']['queen_length'],
                     want['them']['alive'], want['them']['longest'], want['them']['total'],
                     want['them']['queen_length']], (final, want)
    plain = lambda x: dict(u=[dict(c) for c in x['u']], t=[dict(c) for c in x['t']])
    return dict(game=row['game'], battle=row['battle'], layout=row['map_key'], w=w, h=h, cells=w * h,
                rating=row['opponent_rating'], opponent=row['opponent'], result=row['result'],
                ended_by=row['ended_by'], last_round=rnd, queen=queen, series=series, final=final,
                turns=turns, splits=splits, eats=plain(eats), q_eats=plain(q_eats), top_eats=plain(top_eats),
                events=events, compact=compact)


def main():
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    snap = json.loads(Path('data/analysis/ladder/dossier/input-snapshot.json').read_text())
    rows = sorted(snap['rows'], key=lambda r: r['game'])
    assert len(rows) == 500
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[:limit]
    geos, out, bad = {}, [], []
    for n, r in enumerate(rows):
        try:
            out.append(json.dumps(scan(r, geos), separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:300]))
        if n % 20 == 19:
            print(n + 1, len(rows), len(bad), flush=True)
    body = '\n'.join(out) + '\n'
    if limit:
        Path(OUT + 'sc_ev-test.jsonl').write_text(body)
    elif shard == 0:
        Path(OUT + 'sc_ev-0.jsonl').write_text(body)
    elif shard == 1:
        Path(OUT + 'sc_ev-1.jsonl').write_text(body)
    elif shard == 2:
        Path(OUT + 'sc_ev-2.jsonl').write_text(body)
    else:
        Path(OUT + 'sc_ev-3.jsonl').write_text(body)
    print('done', shard, len(out), 'bad', bad)


main()
