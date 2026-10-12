# Scratch (diag-feeding): does company protect the longest dragon? For every turn of a side's longest dragon (10+)
# after our feeding began: nearest enemy head, own heads within 5 tiles, and whether it was rammed before its next turn.
# Usage: python3 .../fd_esc.py <shard> <shards>     then     python3 .../fd_esc.py sum
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


def scan(row, expo, dead):
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
    ours = teams[row['queen_us']]
    side = lambda i: 'u' if teams[i] == ours else 't'
    man = lambda a, c: torus(a % w, c % w, w) + torus(a // w, c // w, h)
    last = {}
    rnd, actor = 0, None
    S = row['S']
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            last.pop(actor, None)
            if rnd >= S:
                b = bodies[actor]
                s = side(actor)
                L = len(b)
                if L >= 10 and L >= max(len(bb) for i, bb in bodies.items() if side(i) == s):
                    hd = b[0]
                    e, o, es = 99, 0, 0
                    for i, bb in bodies.items():
                        if i == actor:
                            continue
                        d = man(hd, bb[0])
                        if side(i) == s:
                            o += int(d <= 5)
                        elif len(bb) <= 9:
                            e = min(e, d)
                            es += int(d <= 5)
                    n = sum(1 for i in bodies if side(i) == s)
                    key = '%s|%s|%s|%s' % (s, 'e<=3' if e <= 3 else 'e4-5' if e <= 5 else 'e6-8' if e <= 8 else 'e9+',
                                           'o0' if o == 0 else 'o1' if o == 1 else 'o2+', 'n<=10' if n <= 10 else 'n11-30' if n <= 30 else 'n31+')
                    expo[key] += 1
                    last[actor] = key
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
            last.pop(p.i32(0), None)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if reason == 3 and i != actor and i in last and side(actor) != side(i):
                dead[last[i]] += 1
            last.pop(i, None)
            bodies.pop(i)


def main():
    if sys.argv[1] == 'sum':
        expo, dead = Counter(), Counter()
        for k in range(4):
            d = json.loads(Path('data/analysis/ladder/dossier/work/fd_esc-%d.json' % k).read_text())
            expo.update(d['expo'])
            dead.update(d['dead'])
        for s in ('u', 't'):
            print('== longest dragon of', 'ours' if s == 'u' else 'theirs', '(10+), turns after our feeding began ==')
            for dims, name in (((1,), 'nearest enemy head (9 long or less)'), ((2,), 'own heads within 5'), ((1, 2), 'both'), ((2, 3), 'own within 5 x team size')):
                agg_e, agg_d = Counter(), Counter()
                for key, n in expo.items():
                    q = key.split('|')
                    if q[0] != s:
                        continue
                    kk = ' '.join(q[i] for i in dims)
                    agg_e[kk] += n
                    agg_d[kk] += dead.get(key, 0)
                print('  ', name)
                for kk in sorted(agg_e):
                    print('      %-14s turns %6d rammed %4d per 100 turns %.2f' % (kk, agg_e[kk], agg_d[kk], 100.0 * agg_d[kk] / agg_e[kk]))
        return
    shard, shards = int(sys.argv[1]), int(sys.argv[2])
    R = [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_games.jsonl').open()]
    rows = dict((r['game'], r) for r in R)
    for k in range(4):
        for l in Path('data/analysis/ladder/dossier/work/fd_scan-%d.jsonl' % k).open():
            g = json.loads(l)
            if g['game'] in rows:
                rows[g['game']]['queen_us'] = g['queen']['u']
    todo = sorted(R, key=lambda r: r['game'])
    todo = [r for n, r in enumerate(todo) if n % shards == shard]
    expo, dead = Counter(), Counter()
    for n, r in enumerate(todo):
        scan(r, expo, dead)
        if n % 20 == 19:
            print(n + 1, len(todo), flush=True)
    body = json.dumps(dict(expo=dict(expo), dead=dict(dead), games=len(todo)))
    if shard == 0:
        Path(OUT + 'fd_esc-0.json').write_text(body)
    elif shard == 1:
        Path(OUT + 'fd_esc-1.json').write_text(body)
    elif shard == 2:
        Path(OUT + 'fd_esc-2.json').write_text(body)
    else:
        Path(OUT + 'fd_esc-3.json').write_text(body)
    print('done', shard, len(todo))


main()
