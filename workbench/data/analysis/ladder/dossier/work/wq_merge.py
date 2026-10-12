"""Scratch (diag-whq): the merge situation. For every turn after round 200 of a dragon that is not its side's queen:
the nearest team mate at least twice its length and 4 or more long (torus tiles from head to head: beside, 2-3, 4-6, 7-15,
farther or none), whether an enemy head is within 4 tiles, and whether the dragon stops on that turn (dies with no order
while a free tile is beside it). Also whether it splits on that turn.
Usage: python3 data/analysis/ladder/dossier/work/wq_merge.py <O|R> <shard> <shards> [limit]   |   ... agg <O|R>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
WORK = Path('data/analysis/ladder/dossier/work')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'agg7-b1', 'agg7-b2', 'agg8-q1', 'agg8-q2')
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q', 'agg8-q2': 'B7Q'}


def jobs(src):
    out = []
    if src == 'O':
        for label in LABELS:
            folder = Path('data/online/smoke') / (label + '-new')
            if not folder.is_dir():
                continue
            for mp in sorted(folder.glob('game-*.json')):
                j = json.loads(mp.read_text())
                rp = folder / ('M%d.replay' % j['id'])
                if rp.exists():
                    out.append((label, rp, j, 1119))
    else:
        path = Path('data/analysis/ladder/dossier/target/per-game-top1.jsonl')
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            rp = Path(r['replay'])
            j = json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text())
            out.append((src, rp, j, 306))
        out.sort(key=lambda t: t[2]['id'])
    return out


def scan(label, path, j, team):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
    own = 0 if j['teamAId'] == team else 1

    def side(i):
        return 0 if teams[i] == own else 1

    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def dest(h, d):
        x, y = h
        e = edge_id(W, H, x, y, d)
        kind, pid = edges.get(e, (0, -1))
        if kind == 2:
            partner = [z for z in portals[pid] if z != e][0]
            prow, px = divmod(partner, W + 1)
            py = prow // 2
            return ((px - (d == 3)) % W, (py - (d == 0)) % H)
        dx, dy = STEP[d]
        return ((x + dx) % W, (y + dy) % H)

    def free_sides(h):
        occ = set()
        for bb in bodies.values():
            occ.update(bb)
        n = 0
        for d in range(4):
            if edges.get(edge_id(W, H, h[0], h[1], d), (0, -1))[0] == 1:
                continue
            if dest(h, d) not in occ:
                n += 1
        return n

    C = Counter()
    rnd, actor = -1, None
    cur = None

    def close():
        nonlocal cur
        if cur is not None:
            C[cur + ('turns',)] += 1
            cur = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            rnd, actor = p.i32(0), None
        elif k == 1:
            close()
            actor = p.i32(0)
            s = side(actor)
            if rnd > 200 and actor != queens[s]:
                b = bodies[actor]
                L = len(b)
                h = b[0]
                best = 99
                e4 = 0
                n = 0
                for z, bb in bodies.items():
                    if z == actor:
                        continue
                    g = gap(h, bb[0])
                    if side(z) == s:
                        n += 1
                        if len(bb) >= 2 * L and len(bb) >= 4 and g < best:
                            best = g
                    elif g <= 4:
                        e4 = 1
                bucket = 0 if best <= 1 else 1 if best <= 3 else 2 if best <= 6 else 3 if best <= 15 else 4
                w = 0 if rnd <= 300 else 1 if rnd <= 400 else 2
                lc = 0 if L <= 2 else 1 if L == 3 else 2 if L == 4 else 3 if L <= 9 else 4
                cur = (w, s, lc, bucket, e4, 1 if n + 1 >= 56 else 0)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if cur is not None and parent == actor:
                C[cur + ('splits',)] += 1
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if cur is not None and i == actor and reason == 4 and free_sides(bodies[i][0]) > 0:
                C[cur + ('stops',)] += 1
            bodies.pop(i)
    close()
    fin = root.pointer(4)
    winner = fin.u16(6) if fin.u16(4) == 1 else None
    return dict(src=label, gid=j['id'], map=j['mapName'], cells=W * H, opp=j['team' + 'AB'[1 - own] + 'Name'],
                result='draw' if winner is None else 'win' if winner == own else 'loss', last=rnd,
                C=[list(key) + [n] for key, n in sorted(C.items())])


def do_scan():
    src, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else None
    todo = [t for n, t in enumerate(jobs(src)) if n % shards == shard]
    name = 'wq_merge-test.jsonl'
    if limit is None:
        if src == 'O' and shard == 0:
            name = 'wq_merge-O0.jsonl'
        elif src == 'O':
            name = 'wq_merge-O1.jsonl'
        elif shard == 0:
            name = 'wq_merge-R0.jsonl'
        else:
            name = 'wq_merge-R1.jsonl'
    else:
        todo = todo[:limit]
    with open(OUT + name, 'w') as f:
        for n, (label, path, j, team) in enumerate(todo):
            f.write(json.dumps(scan(label, path, j, team), separators=(',', ':')) + '\n')
            f.flush()
    print('done', src, shard, len(todo))


def show(rows, title):
    n = len(rows)
    if not n:
        return
    print()
    print('==', title, '| games', n)
    BN = ('beside', '2-3 tiles', '4-6', '7-15', 'farther or none')
    WN = ('201-300', '301-400', '401+')
    for s, nm in ((0, 'side0'), (1, 'side1')):
        A = Counter()
        for g in rows:
            for w, sd, lc, bucket, e4, full, kind, v in g['C']:
                if sd == s:
                    A[(w, bucket, e4, kind)] += v
                    A[(w, 'all', kind)] += v
                    A[(w, bucket, 'L', lc, kind)] += v
                    if w < 2:
                        A[(w, bucket, 'full', full, kind)] += v
        for w in range(3):
            tot = A[(w, 'all', 'turns')]
            if not tot:
                continue
            out = []
            for bk in range(5):
                t0, s0 = A[(w, bk, 0, 'turns')], A[(w, bk, 0, 'stops')]
                t1, s1 = A[(w, bk, 1, 'turns')], A[(w, bk, 1, 'stops')]
                out.append('%s: %.0f turns a game (%.0f%%), stops %.1f a game = %.1f%% of turns with no enemy head within 4 (%.1f%% with one)' % (
                    BN[bk], (t0 + t1) / n, 100 * (t0 + t1) / tot, (s0 + s1) / n, 100 * s0 / max(1, t0), 100 * s1 / max(1, t1)))
            print('  %s r%s: turns a game %.0f, stops %.1f, splits %.1f | a mate twice its length and 4+: %s' % (nm, WN[w], tot / n, A[(w, 'all', 'stops')] / n, A[(w, 'all', 'splits')] / n, ' | '.join(out)))
            for bk in (0, 1):
                print('      %s by own length 2; 3; 4; 5-9; 10+: turns a game %s; stop rate %s' % (BN[bk],
                      '; '.join('%.0f' % (A[(w, bk, 'L', lc, 'turns')] / n) for lc in range(5)),
                      '; '.join('%.1f%%' % (100 * A[(w, bk, 'L', lc, 'stops')] / max(1, A[(w, bk, 'L', lc, 'turns')])) for lc in range(5))))
            if w < 2:
                print('      beside or 2-3 tiles, by own count: under 56: turns a game %.0f, stop rate %.1f%%; 56 or more: %.0f, %.1f%%' % (
                    sum(A[(w, bk, 'full', 0, 'turns')] for bk in (0, 1)) / n, 100 * sum(A[(w, bk, 'full', 0, 'stops')] for bk in (0, 1)) / max(1, sum(A[(w, bk, 'full', 0, 'turns')] for bk in (0, 1))),
                    sum(A[(w, bk, 'full', 1, 'turns')] for bk in (0, 1)) / n, 100 * sum(A[(w, bk, 'full', 1, 'stops')] for bk in (0, 1)) / max(1, sum(A[(w, bk, 'full', 1, 'turns')] for bk in (0, 1)))))


def do_agg():
    src = sys.argv[2]
    rows = []
    for p in sorted(WORK.glob('wq_merge-%s[0-9].jsonl' % src)):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    if src != 'O':
        show(rows, 'rank-1 (side0) all')
        show([g for g in rows if g['cells'] > 1200], 'rank-1 (side0) above 1200 cells')
        return
    for opp in ('WeHaveQuizzes', 'Big Bobs Bots'):
        rs = [g for g in rows if g['opp'] == opp]
        show([g for g in rs if ARM[g['src']] == 'MAIN'], opp + ' MAIN all boards')
        show([g for g in rs if ARM[g['src']] != 'MAIN'], opp + ' B7 and B7Q all boards')
        show([g for g in rs if ARM[g['src']] != 'MAIN' and g['cells'] > 1200], opp + ' B7 and B7Q above 1200 cells')
        show([g for g in rs if ARM[g['src']] != 'MAIN' and g['cells'] <= 1200], opp + ' B7 and B7Q 1200 cells or fewer')


if sys.argv[1] == 'agg':
    do_agg()
else:
    do_scan()
