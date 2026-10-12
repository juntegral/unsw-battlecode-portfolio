"""Scratch (diag-wipeout): where the two starters walk in rounds 0-20 on two-dragon starts (total length 6 or less,
1200 cells or fewer), both sides, by layout. Spawn tiles = every tile a natural pearl is born on during the game
(hindsight). Per side: torus distance from each starter to the nearest spawn tile at rounds 0, 5, 10, 15, 20; the
first round a pearl is inside a starter's 7 by 7 view; and of the steps taken with no pearl in view, the share that
end nearer the map centre (width/2, height/2, plain Manhattan as the bot measures it) and nearer a spawn tile.
Usage: python3 data/analysis/ladder/dossier/work/wo_far.py <O|L|R>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, defaultdict, Counter
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
LABELS = ('agg7-m1', 'agg7-m2', 'agg7-m3', 'sr51-bob1')
MARKS = (0, 5, 10, 15, 20)


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
                    out.append((rp, j, 1119))
    else:
        path = Path('data/analysis/ladder/dossier') / ('per-game.jsonl' if src == 'L' else 'target/per-game-top1.jsonl')
        team = 1119 if src == 'L' else 306
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['relation'] != 'us' or r['cells'] > 1200:
                continue
            st = r['all_starting_dragons']['us']
            if len(st) != 2 or sum(d['length'] for d in st) > 6:
                continue
            rp = Path(r['replay'])
            out.append((rp, json.loads((rp.parent / ('game-%d.json' % r['game'])).read_text()), team))
    return out


def scan(path, j, team):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    if W * H > 1200:
        return None
    own = 0 if j['teamAId'] == team else 1
    side = lambda i: 0 if teams[i] == own else 1
    if sum(1 for i in bodies if side(i) == 0) != 2 or sum(len(b) for i, b in bodies.items() if side(i) == 0) > 6:
        return None
    events = list(root.pointer(3))
    spawn = set()
    actor = None
    for ev in events:
        k = ev.u16(0)
        if k == 0:
            actor = None
        elif k == 1:
            actor = ev.pointer(0).i32(0)
        elif k == 3 and ev.pointer(0).u32(0) and actor is None:
            spawn.add(replay.point(ev.pointer(0).pointer(0)))
    starters = dict((i, side(i)) for i in bodies)
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def near(h):
        return min(gap(h, c) for c in spawn) if spawn else 0

    def centre(h):
        return abs(h[0] - W // 2) + abs(h[1] - H // 2)

    def inview(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3

    out = dict(dist=defaultdict(list), first_view=[None, None], steps=Counter(), W=W, H=H, map=j['mapName'], gid=j['id'],
               spawn_centre=sum(centre(c) for c in spawn) / max(len(spawn), 1), start_centre=[0, 0], nspawn=len(spawn))
    for s in (0, 1):
        out['start_centre'][s] = sum(centre(bodies[i][0]) for i in starters if starters[i] == s) / 2
    pearls = set()
    rnd, actor = -1, None
    pre = None
    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd in MARKS:
                for i, s in starters.items():
                    if i in bodies:
                        out['dist'][(rnd, s, 'q' if i in queens else 'o')].append(near(bodies[i][0]))
            if rnd > 20:
                break
        elif k == 1:
            actor = p.i32(0)
            pre = None
            if actor in starters and actor in bodies:
                h = bodies[actor][0]
                s = starters[actor]
                see = any(inview(h, c) for c in pearls)
                if see and out['first_view'][s] is None:
                    out['first_view'][s] = rnd
                if not see:
                    pre = (h, s, 'q' if actor in queens else 'o')
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pearls.add(c)
            else:
                pearls.discard(c)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                if pre is not None and i == actor:
                    h, s, rl = pre
                    out['steps'][(s, rl, 'n')] += 1
                    out['steps'][(s, rl, 'centre')] += centre(hd) < centre(h)
                    out['steps'][(s, rl, 'spawn')] += near(hd) < near(h)
                    out['steps'][(s, rl, 'spawn away')] += near(hd) > near(h)
                    pre = None
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
        elif k == 11:
            bodies.pop(p.i32(0))
    return out


def med(v):
    v = sorted(99 if x is None else x for x in v)
    return v[len(v) // 2] if v else None


def main():
    src = sys.argv[1]
    cls = {}
    for p in sorted(WORK.glob('wo_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            cls[g['gid']] = 'OUT' if g['final'][0] == 0 else 'KILL' if g['final'][4] == 0 else 'REST'
    by = defaultdict(list)
    for path, j, team in jobs(src):
        r = scan(path, j, team)
        if r is None:
            continue
        r['cls'] = cls[r['gid']]
        by[r['map']].append(r)
        by['ALL but Stripes' if r['map'] != 'Stripes' else 'Stripes only'].append(r)
        by['class ' + r['cls'] + (' Stripes' if r['map'] == 'Stripes' else '')].append(r)
    for name, a in sorted(by.items()):
        n = len(a)
        print('%s %s: games %d (%s) | spawn tiles %.0f, their mean centre distance %.1f, starters centre distance %.1f' % (
            src, name, n, dict(Counter(r['cls'] for r in a)), sum(r['nspawn'] for r in a) / n, sum(r['spawn_centre'] for r in a) / n, sum(r['start_centre'][0] for r in a) / n))
        print('   first round a pearl is in a starter view, median: us %s them %s' % (med([r['first_view'][0] for r in a]), med([r['first_view'][1] for r in a])))
        for s, nm in ((0, 'us'), (1, 'them')):
            for rl, rn in (('q', 'queen'), ('o', 'other')):
                ds = []
                for m in MARKS:
                    v = [x for r in a for x in r['dist'].get((m, s, rl), [])]
                    ds.append('r%d %.1f' % (m, sum(v) / max(len(v), 1)))
                st = Counter()
                for r in a:
                    for key in ('n', 'centre', 'spawn', 'spawn away'):
                        st[key] += r['steps'][(s, rl, key)]
                print('   %-4s %-5s distance to nearest spawn tile: %s | blind steps %d: nearer centre %.0f%%, nearer a spawn tile %.0f%%, farther from it %.0f%%' % (
                    nm, rn, ' '.join(ds), st['n'], 100 * st['centre'] / max(st['n'], 1), 100 * st['spawn'] / max(st['n'], 1), 100 * st['spawn away'] / max(st['n'], 1)))


main()
