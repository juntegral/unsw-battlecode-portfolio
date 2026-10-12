"""census.py <arm> ...: for every queen death in local games, what each living enemy dragon could have proved on its next
turn, and for every turn where a dragon lost sight of a LIVING enemy queen, whether a rule would have fired (false positive).
Both sides are witnesses of the other side's queen. Walls and portals are ignored (plain torus distance); pearl timers are
not in the replay, so spawned pearls can add false positives here that the bot's timer test removes.
Run from the repo root: python3 -B data/codex/astra/qdead-opus/census.py h2h_mNps_v13"""
import sys, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from pathlib import Path
RUNS = Path.home() / 'meow-redteam/solo/runs'
RULES = ('pearl', 'gone', 'vacate', 'pattern0', 'pattern1')


def game(path, tally, rowsout, name):
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
    queens = {t: min(i for i in bodies if teams[i] == t) for t in set(teams.values())}
    qteam = {v: k for k, v in queens.items()}
    pearls = set()
    sight, pending, dead = {}, {}, {}
    rnd = -1

    def gap(a, b):
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return min(dx, W - dx), min(dy, H - dy)

    def inview(h, c):
        dx, dy = gap(h, c)
        return dx <= 3 and dy <= 3

    def ball(c, r):
        return [((c[0] + dx) % W, (c[1] + dy) % H) for dx in range(-r, r + 1) for dy in range(-(r - abs(dx)), r - abs(dx) + 1)]

    def fired(w, h, prev):
        c, reach, L, parts, clear, whole = prev[1], prev[2], prev[3], prev[4], prev[5], prev[6]
        out = set()
        if not inview(h, c):
            return out
        if w > 1 and c in pearls:
            out.add('pearl')
            if any(x in pearls for x in parts if x != c):
                out.add('pattern0')
        if reach >= 0 and all(inview(h, x) for x in ball(c, reach)):
            out.add('gone')
        if whole and len(parts) == 2 and reach == 1:
            out.add('vacate')
        if c not in pearls and len(parts) >= 3 and any(x in pearls and inview(h, x) for x in parts if x != c) and \
                any(x in pearls and inview(h, x) for x in clear):
            out.add('pattern1')
        return out

    def turn(w):
        h = bodies[w][0]
        foe = [q for t, q in queens.items() if t != teams[w]][0]
        prev = sight.pop(w, None)
        live = prev is not None and prev[0] == rnd - 1
        if foe in bodies:
            b = bodies[foe]
            parts = [c for c in b if inview(h, c)]
            if live and not parts:
                tally['alive: lost sight turns'] += 1
                for r in fired(w, h, prev):
                    tally['alive: FALSE ' + r] += 1
                    rowsout.append('FALSE %s %s r%d w%d' % (r, name, rnd, w))
            if inview(h, b[0]):
                n = len(parts)
                whole = n == len(b) and all(max(gap(h, c)) < 3 for c in parts)
                reach = -1
                if 2 <= n <= 3 and whole:
                    base = n - 1
                    reach = base
                    while reach <= 2:
                        cells = ball(b[0], reach)
                        if not all(inview(h, c) for c in cells):
                            reach = -1
                            break
                        p = sum(1 for c in cells if c in pearls)
                        if base + p <= reach:
                            break
                        reach = base + p
                    if reach > 2:
                        reach = -1
                clear = [c for c in ball(b[0], 1) if c != b[0] and c not in pearls and c not in parts and inview(h, c)]
                sight[w] = (rnd, b[0], reach, len(b), parts, clear, whole)
        elif foe in dead and w in pending.get(foe, {}):
            pending[foe].pop(w)
            res = 'blind'
            if live:
                f = fired(w, h, prev)
                res = '+'.join(sorted(f)) if f else 'miss L%d %s %s' % (min(prev[3], 5), 'moved' if prev[1] != dead[foe][1] else 'same', 'cell-in-view' if inview(h, prev[1]) else 'cell-out')
            dead[foe][2].append(res)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
        elif k == 1:
            turn(p.i32(0))
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
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
        elif k == 11:
            i = p.i32(0)
            if i in qteam:
                dead[i] = [rnd, bodies[i][0], [], len(bodies[i])]
                pending[i] = {w: 1 for w in bodies if teams[w] != teams[i]}
            bodies.pop(i)
            sight.pop(i, None)
    for q, (r, c, res, L) in dead.items():
        got = set()
        for x in res:
            if not x.startswith('miss') and x != 'blind':
                got.update(x.split('+'))
        saw = any(x != 'blind' for x in res)
        tally['dead: queen deaths'] += 1
        tally['dead: a living witness had her head in view the turn before'] += 1 if saw else 0
        for rule in RULES:
            tally['dead: proved by ' + rule] += 1 if rule in got else 0
        tally['dead: proved by gone/vacate/pattern (no single pearl)'] += 1 if got - {'pearl'} else 0
        tally['dead: proved by any'] += 1 if got else 0
        if saw and not got:
            for x in set(res):
                if x.startswith('miss'):
                    tally['dead, unproved: ' + x] += 1
        rowsout.append('%s q%d r%d L%d %s' % (name, q, r, L, dict(Counter(res))))


for arm in sys.argv[1:]:
    tally, rowsout = Counter(), []
    n = 0
    for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
        if (folder / 'result.txt').exists() and (folder / 'game.replay').exists():
            game(folder / 'game.replay', tally, rowsout, folder.name)
            n += 1
    print('==', arm, n, 'games')
    for k in sorted(tally):
        print('  %-66s %d' % (k, tally[k]))
    open('data/codex/astra/qdead-opus/census-%s.txt' % arm, 'w').write('\n'.join(rowsout) + '\n')
