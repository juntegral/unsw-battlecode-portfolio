"""Scratch (diag-bigmap): turns of dragons of 8 or more by how many steps they took, and how often the dragon is
rammed by an enemy head before its next own turn. Also whether an enemy head was in its 7 by 7 view when the turn
began, the pearls it ate on the turn, and how far the rammer's head was (straight tiles) when the turn began.
Usage: python3 data/analysis/ladder/dossier/work/bm_stride.py scan <O|L|R> | agg <O|L|R>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, defaultdict, Counter
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
WORK = Path('data/analysis/ladder/dossier/work')
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'agg7-b1', 'agg7-b2', 'agg8-q1', 'agg8-q2')


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
        path = Path('data/analysis/ladder/dossier') / ('per-game.jsonl' if src == 'L' else 'target/per-game-top1.jsonl')
        team = 1119 if src == 'L' else 306
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['relation'] != 'us':
                continue
            rp = Path(r['replay'])
            out.append((src, rp, json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text()), team))
        out.sort(key=lambda t: t[2]['id'])
    return out


def lbk(L):
    return 8 if L < 10 else 10 if L < 15 else 15 if L < 30 else 30


def scan(label, path, j, team):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    if W * H <= 1200:
        return None
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    own = 0 if j['teamAId'] == team else 1
    side = lambda i: 0 if teams[i] == own else 1

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(min(dx, W - dx), min(dy, H - dy))

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    turns = Counter()
    hits = Counter()
    far = Counter()
    last = {}
    rnd, actor, cur, used = -1, None, None, 0

    def close():
        nonlocal cur
        if cur is None:
            return
        i = cur['i']
        if i in bodies and not cur['split']:
            key = (cur['s'], rnd // 100, lbk(cur['L']), min(used, 3), int(cur['ate'] > 0), cur['seen'])
            turns[key] += 1
            last[i] = (key, cur['pos'])
        cur = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            rnd, actor = p.i32(0), None
        elif k == 1:
            close()
            actor = p.i32(0)
            used = 0
            b = bodies[actor]
            last.pop(actor, None)
            if len(b) >= 8:
                s = side(actor)
                h = b[0]
                pos = dict((z, bb[0]) for z, bb in bodies.items() if side(z) != s and gap(h, bb[0]) <= 12)
                cur = dict(i=actor, s=s, L=len(b), ate=0, split=False, seen=int(any(cheb(h, c) <= 3 for c in pos.values())), pos=pos, h=h)
            else:
                cur = None
        elif k == 3:
            if not p.u32(0) and cur is not None:
                cur['ate'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if cur is not None and parent == cur['i']:
                cur['split'] = True
            last.pop(child, None)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if reason == 3 and i != actor and side(i) != side(actor) and i in last:
                key, pos = last[i]
                hits[key] += 1
                if actor in pos:
                    far[(key[0], key[3], min(cheb(bodies[i][0], pos[actor]), 7))] += 1
                else:
                    far[(key[0], key[3], 9)] += 1
            bodies.pop(i)
            last.pop(i, None)
    close()
    arm = 'MAIN' if label.startswith('agg7-m') else 'B7' if label.startswith('agg7-b') else 'B7Q' if label.startswith('agg8-q') else label
    return dict(gid=j['id'], arm=arm, opp=j['team' + 'AB'[1 - own] + 'Name'], turns=[list(k) + [v, hits.get(k, 0)] for k, v in sorted(turns.items())], far=[list(k) + [v] for k, v in sorted(far.items())])


def do_scan():
    src = sys.argv[2]
    todo = jobs(src)
    name = 'bm_stride-O.jsonl'
    if src == 'L':
        name = 'bm_stride-L.jsonl'
    elif src == 'R':
        name = 'bm_stride-R.jsonl'
    n = 0
    with open(OUT + name, 'w') as f:
        for k, (label, path, j, team) in enumerate(todo):
            g = scan(label, path, j, team)
            if g is not None:
                f.write(json.dumps(g, separators=(',', ':')) + '\n')
                n += 1
            if k % 50 == 49:
                print(src, k + 1, len(todo), n, flush=True)
    print('done', src, len(todo), n)


def do_agg():
    src = sys.argv[2]
    rows = [json.loads(x) for x in (WORK / ('bm_stride-' + src + '.jsonl')).read_text().splitlines()]
    sets = [('ALL', rows)]
    if src == 'O':
        sets = [('MAIN', [g for g in rows if g['arm'] == 'MAIN']), ('B7+B7Q', [g for g in rows if g['arm'] != 'MAIN'])]
    for name, gs in sets:
        n = len(gs)
        print()
        print('=====', name, n, 'games; turns a game / rammed before the next own turn per 1000 turns')
        for s, nm in ((0, 'ours'), (1, 'theirs')):
            for lo in (8, 10, 15):
                for sel, snm in ((None, 'all rounds'), (2, 'r200-299'), (3, 'r300-399'), (4, 'r400-499')):
                    t = Counter()
                    h = Counter()
                    for g in gs:
                        for sd, band, L, st, ate, seen, cnt, hit in g['turns']:
                            if sd == s and L >= lo and (sel is None or band == sel):
                                for key in (('steps', st), ('steps, no enemy head in view at the start', st) if not seen else ('steps, enemy head in view', st), ('all', 0)):
                                    t[key] += cnt
                                    h[key] += hit
                    if not t[('all', 0)]:
                        continue
                    cells = []
                    for grp in ('steps', 'steps, no enemy head in view at the start', 'steps, enemy head in view'):
                        cells.append(grp + ': ' + ' '.join('%s=%.1f/%.2f (%d)' % ('0' if st == 0 else str(st) if st < 3 else '3+', t[(grp, st)] / n, 1000 * h[(grp, st)] / t[(grp, st)] if t[(grp, st)] else 0, h[(grp, st)]) for st in (0, 1, 2, 3)))
                    print('  %s %d+ %-9s all %.1f/%.2f (%d) | %s' % (nm, lo, snm, t[('all', 0)] / n, 1000 * h[('all', 0)] / t[('all', 0)], h[('all', 0)], ' | '.join(cells)))
            f = Counter()
            for g in gs:
                for sd, st, d, cnt in g['far']:
                    if sd == s:
                        f[(min(st, 2), 'in view (0-3)' if d <= 3 else 'out of view, 4-7' if d <= 7 else 'farther or new')] += cnt
            print('  %s rammed 8+: where the rammer head stood when the victim began its last turn (tiles, either axis): one step or none %s; two or more steps %s' % (nm, dict((k[1], v) for k, v in f.items() if k[0] <= 1), dict((k[1], v) for k, v in f.items() if k[0] == 2)))


if sys.argv[1] == 'scan':
    do_scan()
else:
    do_agg()
