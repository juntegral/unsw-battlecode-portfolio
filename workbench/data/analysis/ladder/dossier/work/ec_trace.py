# Scratch (diag-economy): follows the followed side's dragons that go longest without a meal in one game and
# prints the path of the n-th longest such spell (rounds 30-300): head tile each round, pearls and team mates in the
# 7 by 7 view, how the spell ends. Also prints the game's ten longest spells.
# Usage: python3 data/analysis/ladder/dossier/work/ec_trace.py <O|R> <game> [n-th longest, default 1]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from pathlib import Path


def main():
    who, game = sys.argv[1], int(sys.argv[2])
    nth = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    row = [r for r in rows if r['who'] == who and r['game'] == game][0]
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    lines = text.splitlines()
    w, h = map(int, lines[0].split()[1:3])
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    focal = row['side']
    present = set()
    fed, path, spells = {i: 0 for i in bodies}, {i: [] for i in bodies}, []
    rnd, actor = 0, None

    def view(hd):
        n = m = 0
        for p in present:
            dx, dy = abs(p[0] - hd[0]), abs(p[1] - hd[1])
            if min(dx, w - dx) <= 3 and min(dy, h - dy) <= 3:
                n += 1
        for j, b in bodies.items():
            if teams[j] == focal:
                dx, dy = abs(b[0][0] - hd[0]), abs(b[0][1] - hd[1])
                if min(dx, w - dx) <= 3 and min(dy, h - dy) <= 3:
                    m += 1
        return n, m - 1

    def close(i, how):
        if path[i] and rnd - fed[i] >= 20:
            spells.append((rnd - fed[i], i, fed[i], rnd, how, path[i]))
        path[i] = []

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd > 300:
                break
        elif k == 1:
            actor = p.i32(0)
            b = bodies.get(actor)
            if b is not None and teams[actor] == focal and len(b) <= 3 and rnd >= 30:
                n, m = view(b[0])
                path[actor].append('%d,%d%s%s' % (b[0][0], b[0][1], '*' * min(n, 3), 'm' * min(m, 3)))
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
                present.discard(c)
                if teams[actor] == focal:
                    close(actor, 'ate')
                    fed[actor] = rnd
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            for z, i in enumerate((a, c)):
                bodies[i] = deque(replay.point(x) for x in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            fed[c] = rnd
            path[c] = []
        elif k == 11:
            i = p.i32(0)
            if teams[i] == focal:
                close(i, 'died (reason %d)' % p.u16(4))
            bodies.pop(i)
    for i in list(bodies):
        if teams[i] == focal:
            close(i, 'still hungry at round 300')
    spells.sort(reverse=True)
    print(row['layout'], 'spells of 20+ rounds without a meal:', len(spells), 'ten longest (rounds, dragon, from, to, end):',
          [(s[0], s[1], s[2], s[3], s[4]) for s in spells[:10]])
    if len(spells) >= nth:
        s = spells[nth - 1]
        print('dragon #%d, no meal from round %d to %d, %s. Head each turn (* pearls in view, m team mates in view):' % (s[1], s[2], s[3], s[4]))
        print(' '.join(s[5][:90]))


main()
