"""Scratch (diag-attack): replay viewer. Prints, for rounds r0..r1 of one game, each turn of the dragons within 7 tiles
of a followed dragon: who moved where, lengths, deaths. Usage: python3 .../at_view.py <game> <dragon id> <r0> <r1>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from pathlib import Path


def torus(a, b, n):
    d = abs(a - b)
    return min(d, n - d)


def main():
    game, follow, r0, r1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    rows = json.loads(Path('data/analysis/ladder/dossier/input-snapshot.json').read_text())['rows']
    row = [r for r in rows if r['game'] == game][0]
    path = Path('data/online/ladder') / str(row['battle']) / ('M%d.replay' % row['game'])
    root = replay.load(path).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    print(game, row['map_key'], w, h, row['result'], 'vs', row['opponent_rating'], row['ended_by'])
    tile = lambda p: p[1] * w + p[0]
    bodies, teams = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    ours = row['our_side']
    side = lambda i: 'u' if teams[i] == ours else 't'
    man = lambda a, c: torus(a % w, c % w, w) + torus(a // w, c // w, h)
    xy = lambda c: '%d,%d' % (c % w, c // w)
    rnd, actor = 0, None
    spot = None
    start = None
    pearls = set()
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        show = r0 <= rnd <= r1
        if k == 0:
            rnd, actor = p.i32(0), None
            if follow in bodies:
                spot = bodies[follow][0]
            if r0 <= rnd <= r1 and spot is not None:
                nu = sum(1 for i in bodies if side(i) == 'u')
                nt = len(bodies) - nu
                near = sorted((man(spot, b[0]), side(i), i, len(b), xy(b[0])) for i, b in bodies.items() if man(spot, b[0]) <= 7)
                print('r%d ours %d theirs %d | pearls near: %s | %s' % (rnd, nu, nt, ' '.join(xy(c) for c in sorted(pearls) if man(spot, c) <= 4),
                                                                    '  '.join('%s#%d L%d @%s d%d' % (s, i, L, pos, d) for d, s, i, L, pos in near)))
        elif k == 1:
            actor = p.i32(0)
            start = (bodies[actor][0], len(bodies[actor]))
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                pearls.add(c)
            else:
                pearls.discard(c)
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
            if show and spot is not None and man(spot, bodies[p.i32(0)][0]) <= 7:
                print('      split %s#%d -> L%d and child #%d L%d' % (side(p.i32(0)), p.i32(0), len(bodies[p.i32(0)]), p.i32(4), len(bodies[p.i32(4)])))
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            if show and spot is not None and man(spot, b[0]) <= 9:
                print('      DEATH %s#%d L%d %s at %s%s' % (side(i), i, len(b), ('wall', 'own body', 'body', 'HEAD-ON', 'no action')[min(reason, 4)], xy(b[0]),
                                                          '' if i == actor else ' (mover %s#%d started at %s with L%d)' % (side(actor), actor, xy(start[0]), start[1])))
            bodies.pop(i)


main()
