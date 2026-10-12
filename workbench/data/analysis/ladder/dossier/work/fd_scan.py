# Scratch (diag-feeding): replays every main ladder game in rows.jsonl and writes one line per game:
# per-round standings of both sides, every death of ours after round 200 (cause, length, who was hit),
# every "no action" death of ours with the long team mate beside it and who ate what it dropped,
# and what our longest dragon ate, by where the pearl came from.
# Usage: python3 data/analysis/ladder/dossier/work/fd_scan.py <shard> <shards>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
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


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


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
    top = dict(u=-1, t=-1)
    series = []
    cap_rounds = []
    our_deaths, their_big, feeders = [], [], []
    their_small = Counter()
    top_eat, queen_eat = {}, {}
    eat_bins = dict(u={}, t={})
    split_bins = dict(u=Counter(), t=Counter())
    fed_ids = set()
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
            if top[s] not in bodies or len(bodies[top[s]]) != big:
                cand = [i for i, b in bodies.items() if side(i) == s and len(b) == big]
                top[s] = min(cand) if cand else -1
            out += [n, big, tot, len(bodies.get(queen[s], ())), top[s]]
        return out

    def finish_turn():
        hs = [d for d in turn_deaths if d['reason'] == 3]
        if len(hs) == 2:
            a, c = hs
            for own, other in ((a, c), (c, a)):
                own.update(o_side=other['side'], o_id=other['id'], o_len=other['L'])
        turn_deaths.clear()

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            finish_turn()
        if k == 0:
            rnd, actor = p.i32(0), None
            while len(series) < rnd:
                series.append(None)
            series.append(stand())
        elif k == 1:
            actor = p.i32(0)
            dirs, used, act = [], 0, None
            if rnd > 200 and side(actor) == 'u':
                n = sum(1 for i in bodies if side(i) == 'u')
                if n >= 56 and (not cap_rounds or cap_rounds[-1] != rnd):
                    cap_rounds.append(rnd)
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
                origin = 'n' if rec is None else rec['code']
                if rnd > 150:
                    b = eat_bins[s].setdefault((rnd - 1) // 25, dict(n=0, f=0, o=0, t=0))
                    b[origin] += 1
                if s == 'u':
                    is_top = L >= longest('u', actor)
                    if rec is not None and rec['code'] == 'f':
                        d = rec['d']
                        d['e_us'] += 1
                        d['e_tgt'] += int(actor == d['tgt'])
                        d['e_top'] += int(is_top)
                    if rnd > 150:
                        if is_top:
                            top_eat.setdefault(rnd, dict(n=0, f=0, o=0, t=0))[origin] += 1
                        if actor == queen['u']:
                            queen_eat.setdefault(rnd, dict(n=0, f=0, o=0, t=0))[origin] += 1
                elif rec is not None and rec['code'] == 'f':
                    rec['d']['e_them'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            if rnd > 150:
                split_bins[side(p.i32(0))][(rnd - 1) // 25] += 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            b = bodies[i]
            L = len(b)
            head = b[0]
            cause = CAUSE[reason] if reason < 4 else (act or 'noact') if i == actor else 'noact'
            d = dict(r=rnd, id=i, L=L, cause=cause, reason=reason, side=s, x=head % w, y=head // w,
                     top=int(L >= longest(s, i)), q=int(i == queen[s]), mover=int(i == actor),
                     o_side=None, o_id=None, o_len=None, rest=longest(s, i),
                     n_side=sum(1 for z in bodies if side(z) == s) - 1)
            if reason == 2 and i == actor and used < len(dirs):
                dest = g.moves[head][dirs[used]][1]
                owners = [z for z, bb in bodies.items() if z != i and dest in bb]
                if owners:
                    d.update(o_side=side(owners[0]), o_id=owners[0], o_len=len(bodies[owners[0]]))
            code = 't' if s == 't' else 'o'
            rec = dict(code=code)
            if s == 'u' and cause == 'noact' and i == actor:
                tgt, tl_, dist = -1, 0, -1
                for z, bb in bodies.items():
                    if z != i and side(z) == 'u' and gap(head, bb[0]) <= 10 and len(bb) > tl_:
                        tgt, tl_, dist = z, len(bb), gap(head, bb[0])
                enemy = min([gap(head, bb[0]) for z, bb in bodies.items() if side(z) == 't'], default=99)
                d.update(tgt=tgt, tgt_len=tl_, tgt_q=int(tgt == queen['u']), tgt_top=int(tl_ >= longest('u', i) and tgt >= 0),
                         dist=dist, enemy=enemy, np=(L + 1) // 2, e_us=0, e_tgt=0, e_top=0, e_them=0)
                rec = dict(code='f', d=d)
                feeders.append(d)
                if tgt >= 0:
                    fed_ids.add(tgt)
            elif s == 'u':
                if rnd > 200:
                    our_deaths.append(d)
            elif rnd > 200:
                if L >= 6 or d['top']:
                    their_big.append(d)
                else:
                    their_small[cause + '|' + str((rnd - 1) // 50)] += 1
            turn_deaths.append(d)
            for seg, c in enumerate(b):
                if seg % 2 == 0:
                    expected.append((c, rec))
            bodies.pop(i)
    finish_turn()
    final = stand()
    for d in our_deaths:
        d['fed'] = int(d['id'] in fed_ids)
    return dict(game=row['game'], battle=row['battle'], layout=row['map_key'], w=w, h=h, cells=w * h,
                rating=row['opponent_rating'], opponent=row['opponent'], result=row['result'],
                ended_by=row['ended_by'], queens_at_end=row['queens_at_end'], last_round=rnd, time=row['time'],
                queen=queen, series=series, final=final, cap_rounds=cap_rounds, our_deaths=our_deaths,
                their_big=their_big, their_small=dict(their_small), feeders=feeders,
                top_eat=top_eat, queen_eat=queen_eat, eat_bins=eat_bins,
                split_bins=dict(u=dict(split_bins['u']), t=dict(split_bins['t'])))


def main():
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rows = [json.loads(l) for l in open('data/analysis/ladder/rows.jsonl')]
    rows = sorted([r for r in rows if r['our_code'] == 'main'], key=lambda r: r['game'])
    rows = [r for n, r in enumerate(rows) if n % shards == shard]
    if limit:
        rows = rows[:limit]
    geos, out, bad = {}, [], []
    for n, r in enumerate(rows):
        try:
            rec = scan(r, geos)
            f = rec['final']
            want = r['final']
            assert [f[0], f[1], f[2], f[5], f[6], f[7]] == [want['us']['alive'], want['us']['longest'], want['us']['total'],
                                                           want['them']['alive'], want['them']['longest'], want['them']['total']], (f, want)
            out.append(json.dumps(rec, separators=(',', ':')))
        except Exception as e:
            bad.append((r['game'], repr(e)[:200]))
        if n % 20 == 19:
            print(n + 1, len(rows), len(bad), flush=True)
    body = '\n'.join(out) + '\n'
    if shard == 0:
        Path(OUT + 'fd_scan-0.jsonl').write_text(body)
    elif shard == 1:
        Path(OUT + 'fd_scan-1.jsonl').write_text(body)
    elif shard == 2:
        Path(OUT + 'fd_scan-2.jsonl').write_text(body)
    elif shard == 3:
        Path(OUT + 'fd_scan-3.jsonl').write_text(body)
    else:
        Path(OUT + 'fd_scan-4.jsonl').write_text(body)
    print('done', shard, len(out), 'bad', bad)


main()
