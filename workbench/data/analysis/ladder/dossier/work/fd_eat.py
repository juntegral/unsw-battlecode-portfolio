# Scratch (diag-feeding): who eats what our feeders drop. One line per game in fd_eat-<shard>.json (totals per shard).
# Feeder = our non-queen dragon that dies with no action after feeding began, with a team mate at least twice its length
# within 10 tiles (the longest such is "the dragon beside").
# Usage: python3 .../fd_eat.py <shard> <shards>     then     python3 .../fd_eat.py sum
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def scan(row, C):
    path = Path('data/online/ladder') / str(row['battle']) / ('M%d.replay' % row['game'])
    root = replay.load(path).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    qu = row['queen_us']
    ours = teams[qu]
    side = lambda i: 'u' if teams[i] == ours else 't'
    man = lambda a, c: torus(a % w, c % w, w) + torus(a // w, c // w, h)
    present = {}
    expected = deque()
    ate_fed = Counter()
    rnd, actor = 0, None
    S = row['S']
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present[c] = expected.popleft() if expected else None
            else:
                rec = present.pop(c)
                if rec is not None:
                    if side(actor) == 't':
                        C['them'] += 1
                    else:
                        L = len(bodies[actor])
                        best = max([len(b) for i, b in bodies.items() if i != actor and side(i) == 'u'], default=0)
                        if actor == rec['tgt']:
                            cls = 'beside'
                        elif L >= best:
                            cls = 'other-longest'
                        elif L >= 10:
                            cls = 'other-10+'
                        elif L >= 5:
                            cls = 'other-5-9'
                        else:
                            cls = 'other-2-4'
                        C[cls] += 1
                        if cls == 'beside' and L >= best:
                            C['beside-is-longest'] += 1
                        if cls in ('other-5-9', 'other-2-4'):
                            ate_fed[actor] += 1
                        C['wait-sum'] += rnd - rec['r']
                        C['wait-n'] += 1
                        if rnd - rec['r'] <= 3:
                            C['wait<=3'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            L, hd = len(b), b[0]
            rec = None
            if side(i) == 'u' and reason == 4 and i == actor and rnd >= S and i != qu:
                tgt, tl_ = -1, 0
                for z, bb in bodies.items():
                    if z != i and side(z) == 'u' and man(hd, bb[0]) <= 10 and len(bb) > tl_:
                        tgt, tl_ = z, len(bb)
                if tgt >= 0 and L * 2 <= tl_:
                    rec = dict(tgt=tgt, r=rnd)
                    C['feeders'] += 1
                    C['feeder-length'] += L
                    C['dropped'] += (L + 1) // 2
                    C['feeder-L%d' % min(L, 6)] += 1
                    if ate_fed.get(i):
                        C['feeder-had-eaten-feed'] += 1
                        C['refed-pearls'] += ate_fed[i]
            for seg, c in enumerate(b):
                if seg % 2 == 0:
                    expected.append(rec)
            bodies.pop(i)
    C['left'] += sum(1 for v in present.values() if v is not None)


def main():
    if sys.argv[1] == 'sum':
        C = Counter()
        for k in range(4):
            C.update(json.loads(Path('data/analysis/ladder/dossier/work/fd_eat-%d.json' % k).read_text()))
        d = C['dropped']
        print('feeders', C['feeders'], 'length', C['feeder-length'], 'dropped', d, 'by feeder length', [(n, C['feeder-L%d' % n]) for n in range(2, 7)])
        for k in ('beside', 'other-longest', 'other-10+', 'other-5-9', 'other-2-4', 'them', 'left'):
            print('  eaten by %-14s %6d  %.3f of dropped' % (k, C[k], C[k] / d))
        print('  beside and also our longest', C['beside-is-longest'])
        print('  eaten within 3 rounds', C['wait<=3'], 'of', C['wait-n'], 'mean wait %.1f' % (C['wait-sum'] / C['wait-n']))
        print('  feeders that had themselves eaten feeder pearls', C['feeder-had-eaten-feed'], 'pearls they had eaten', C['refed-pearls'])
        return
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    R = [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_games.jsonl').open()]
    rows = dict((r['game'], r) for r in R)
    for k in range(4):
        for l in Path('data/analysis/ladder/dossier/work/fd_scan-%d.jsonl' % k).open():
            g = json.loads(l)
            if g['game'] in rows:
                rows[g['game']]['queen_us'] = g['queen']['u']
    todo = sorted([r for r in R if r['n_feed'] > 0], key=lambda r: r['game'])
    todo = [r for n, r in enumerate(todo) if n % shards == shard]
    C = Counter()
    for n, r in enumerate(todo):
        scan(r, C)
        if n % 20 == 19:
            print(n + 1, len(todo), flush=True)
    body = json.dumps(dict(C))
    if shard == 0:
        Path(OUT + 'fd_eat-0.json').write_text(body)
    elif shard == 1:
        Path(OUT + 'fd_eat-1.json').write_text(body)
    elif shard == 2:
        Path(OUT + 'fd_eat-2.json').write_text(body)
    else:
        Path(OUT + 'fd_eat-3.json').write_text(body)
    print('done', shard, len(todo))


main()
