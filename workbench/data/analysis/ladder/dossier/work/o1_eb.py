"""Scratch (diag-one1, job D): EAT_BONUS check on local games, bonus arm against live on the same map and side.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_eb.py <bonus arm> <live arm[,fallback arm]>"""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from collections import deque, defaultdict, Counter
from ladder_replay import replay, edge_id, canonical_edges
from o1_scan import OUT, STEP
import o1_early
RUNS = Path.home() / 'meow-redteam/solo/runs'


def extra(path, own):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    side = lambda i: 0 if teams[i] == own else 1
    queen = min(i for i in bodies if side(i) == 0)
    starts = [b[0] for i, b in bodies.items() if side(i) == 0]

    def gap(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def free_sides(h):
        occ = set()
        for bb in bodies.values():
            occ.update(bb)
        n = 0
        for d in range(4):
            if edges.get(edge_id(W, H, h[0], h[1], d), (0, -1))[0] != 0:
                continue
            dx, dy = STEP[d]
            if ((h[0] + dx) % W, (h[1] + dy) % H) not in occ:
                n += 1
        return n

    c = Counter()
    lastmeal = {}
    near = {}            # tile -> [birth, eat round, side] for natural pearls born r<=30 within 6 tiles of one of our starts
    lay = []
    live = {}
    rnd, actor, expected = -1, None, 0
    qdeath = None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
        elif k == 1:
            actor = p.i32(0)
        elif k == 3:
            t = replay.point(p.pointer(0))
            if p.u32(0):
                if expected:
                    expected -= 1
                    live[t] = None
                else:
                    live[t] = rnd
            else:
                born = live.pop(t, None)
                s = side(actor)
                lastmeal[actor] = rnd
                if s == 0:
                    if rnd <= 30: c['meals30'] += 1
                    if rnd <= 100: c['meals100'] += 1
                    if actor == queen and rnd <= 100: c['queen meals100'] += 1
                    if born is not None and rnd <= 100: c['natural100'] += 1
                if born is not None and born <= 60 and min(gap(t, x) for x in starts) <= 6:
                    lay.append([t[0], t[1], max(born, 0), rnd, s])
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(x) for x in p.pointer(z))
                teams[i] = p.u16(8)
            if p.i32(0) in lastmeal:
                lastmeal[p.i32(4)] = lastmeal[p.i32(0)]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if side(i) == 0 and rnd <= 100:
                boxed = reason != 3 and free_sides(bodies[i][0]) == 0
                c['deaths100'] += 1
                c['boxed100'] += boxed
                c['rammed100'] += reason == 3 and i != actor
                if rnd - lastmeal.get(i, -99) <= 3:
                    c['dead within 3 of a meal'] += 1
                    c['.. boxed'] += boxed
                    c['.. head-on'] += reason == 3
            if i == queen:
                qdeath = [rnd, reason, len(bodies[i])]
            expected = (len(bodies[i]) + 1) // 2
            bodies.pop(i)
    return dict(c), lay, qdeath


def game(arm, folder):
    m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
    k = int(m[3])
    j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
    e = o1_early.scan(arm, folder / 'game.replay', j)
    C = Counter()
    for s, w, key, v in e['C']:
        if s == 0:
            C[key] += v
    ex, lay, qd = extra(folder / 'game.replay', k)
    return dict(map=m[1], side=k, C=dict(C), snaps=e['snaps'], ex=ex, lay=lay, qd=qd, result=(folder / 'result.txt').read_text().split('\n')[0][:80])


def rows(arm):
    cache_path = Path(OUT) / ('o1_eb-%s.json' % arm)
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
        if (folder / 'result.txt').exists() and folder.name not in cache:
            cache[folder.name] = game(arm, folder)
    cache_path.write_text(json.dumps(cache))
    return cache


if __name__ == '__main__':
    bonus = rows(sys.argv[1])
    live = {}
    for a in sys.argv[2].split(','):
        for f, g in rows(a).items():
            live.setdefault(f, g)
    T = [Counter(), Counter()]
    n = 0
    D1 = ('lower-id mate in view', 'only higher-id mates in view', 'no mate in view')
    for f in sorted(set(bonus) & set(live)):
        n += 1
        line = [f[:44]]
        for z, g in enumerate((bonus[f], live[f])):
            C = Counter(g['C'])
            taken = sum(C['D1 taken     | ' + x] for x in D1)
            nott = sum(C['D1 not taken | ' + x] for x in D1)
            mt = C['D1 taken     | ' + D1[0]] + C['D1 taken     | ' + D1[1]]
            mn = C['D1 not taken | ' + D1[0]] + C['D1 not taken | ' + D1[1]]
            u = lambda r: (g['snaps'].get(str(r)) or g['snaps'].get(r) or [[0, 0], [0, 0]])[0]
            ex = Counter(g['ex'])
            vals = dict(taken=taken, nott=nott, mtaken=mt, mnott=mn, ataken=C['D1 taken     | ' + D1[2]], anott=C['D1 not taken | ' + D1[2]],
                        meals30=ex['meals30'], meals100=ex['meals100'], u30=u(30)[0], u100=u(100)[0], T100=u(100)[1], dm=ex['dead within 3 of a meal'], dmb=ex['.. boxed'],
                        boxed=ex['boxed100'], deaths=ex['deaths100'], qmeals=ex['queen meals100'], qalive=int(g['qd'] is None or g['qd'][0] > 100), games=1,
                        win=int(('winner=%d' % g['side']) in g['result']))
            T[z].update(vals)
            line.append('%s: not taken %d/%d, meals r30/r100 %d/%d, dragons %d/%d, dead<=3 of meal %d (boxed %d), boxed %d, queen meals %d death %s | %s' % (
                'bonus' if z == 0 else 'live ', nott, taken + nott, ex['meals30'], ex['meals100'], u(30)[0], u(100)[0], ex['dead within 3 of a meal'], ex['.. boxed'], ex['boxed100'], ex['queen meals100'],
                ('r%d L%d' % (g['qd'][0], g['qd'][2])) if g['qd'] else 'alive', g['result'][:45]))
        print('\n   '.join(line))
        if 'australia' in f:
            for z, g in enumerate((bonus[f], live[f])):
                ours = sorted([l for l in g['lay'] if l[2] <= 30], key=lambda l: -(l[3] - l[2]))[:4]
                print('     %s near-start pearls that lay longest (tile, born, eaten, by side 0=ours): %s' % ('bonus' if z == 0 else 'live ', [((l[0], l[1]), l[2], l[3], l[4]) for l in ours]))
    print()
    print('pairs', n)
    for k in ('games', 'win', 'meals30', 'meals100', 'u30', 'u100', 'T100', 'dm', 'dmb', 'boxed', 'deaths', 'qmeals', 'qalive'):
        print('%-10s bonus %7.1f   live %7.1f' % (k, T[0][k] / max(1, n), T[1][k] / max(1, n)))
    for lab, a, b in (('all', 'nott', 'taken'), ('mate in view', 'mnott', 'mtaken'), ('no mate in view', 'anott', 'ataken')):
        print('one step away not taken, %-16s bonus %4.1f%% (%d of %d)   live %4.1f%% (%d of %d)' % (lab, 100 * T[0][a] / max(1, T[0][a] + T[0][b]), T[0][a], T[0][a] + T[0][b], 100 * T[1][a] / max(1, T[1][a] + T[1][b]), T[1][a], T[1][a] + T[1][b]))
