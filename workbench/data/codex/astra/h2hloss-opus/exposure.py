"""After each own move of a non-queen dragon of 10+ : is its head inside the true sprint reach (L-1 steps, Manhattan, walls ignored)
of an enemy of 2-4? Counted per side (0 = newer), by own class (10-14, 15+), enemy length, distance, and whether the enemy body
is fully inside the mover's 7x7 (visible parts == true length). One row per arm. Usage: exposure.py <arm> ..."""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from pathlib import Path
RUNS = Path.home() / 'meow-redteam/solo/runs'
HERE = Path('data/codex/astra/h2hloss-opus')


def one(path, k, C):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * z]), int(q[4 + 2 * z])) for z in range(int(q[2])))
            teams[i] = int(q[1])
    new = sorted(set(teams.values()))[k]
    side = lambda i: 0 if teams[i] == new else 1
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    rnd, actor = -1, None

    def close():
        if actor is None or actor not in bodies or actor in queens:
            return
        b = bodies[actor]
        L = len(b)
        if L < 10:
            return
        s = side(actor)
        cls = '15+' if L >= 15 else '10-14'
        ph = 'r<=350' if rnd <= 350 else 'r>350'
        C[(s, cls, ph, 'turns')] += 1
        h = b[0]
        worst = None
        for z, bb in bodies.items():
            if teams[z] == teams[actor] or len(bb) > 4:
                continue
            e = bb[0]
            dx = abs(e[0] - h[0]); dx = min(dx, W - dx)
            dy = abs(e[1] - h[1]); dy = min(dy, H - dy)
            if dx > 3 or dy > 3:
                continue
            d = dx + dy
            Le = len(bb)
            if d <= Le - 1:
                vis = 0
                for c in bb:
                    ax = abs(c[0] - h[0]); ax = min(ax, W - ax)
                    ay = abs(c[1] - h[1]); ay = min(ay, H - ay)
                    if ax <= 3 and ay <= 3:
                        vis += 1
                key = (Le, d, 'full' if vis == Le else 'cut')
                if worst is None or key[1] < worst[1]:
                    worst = key
        if worst is not None:
            C[(s, cls, ph, 'in reach')] += 1
            C[(s, cls, ph, 'in reach: enemy %d at distance %d' % worst[:2])] += 1
            C[(s, cls, ph, 'in reach: body ' + worst[2])] += 1
    for ev in root.pointer(3):
        kk = ev.u16(0)
        if kk not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if kk == 0:
            close()
            actor = None
            rnd = p.i32(0)
        elif kk == 1:
            close()
            actor = p.i32(0)
        elif kk == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif kk == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
        elif kk == 11:
            bodies.pop(p.i32(0))


for arm in sys.argv[1:]:
    C = Counter()
    n = 0
    for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
        if not (folder / 'result.txt').exists():
            continue
        one(folder / 'game.replay', int(folder.name[-1]), C)
        n += 1
    (HERE / ('exposure-%s.json' % arm)).write_text(json.dumps({'games': n, 'C': {'|'.join(map(str, k)): v for k, v in C.items()}}))
    print('==', arm, n, 'games')
    for cls in ('10-14', '15+'):
        for ph in ('r<=350', 'r>350'):
            for s, nm in ((0, 'NEW'), (1, 'old')):
                t = C[(s, cls, ph, 'turns')]
                r = C[(s, cls, ph, 'in reach')]
                det = {k[3][10:]: v for k, v in sorted(C.items()) if k[:3] == (s, cls, ph) and k[3].startswith('in reach: ')}
                print('  own %-5s %-6s %s: %6d turns, ended inside a small enemy\'s reach %4d (%.2f%%) %s' % (cls, ph, nm, t, r, 100 * r / max(1, t), det))
