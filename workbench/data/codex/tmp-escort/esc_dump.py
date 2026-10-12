"""esc_dump.py <arm> <game> <round> <dragon id> [radius] : the board around that dragon at the start of its turn in that round
(own side upper case: Q queen head, H head, o body; enemy lower case h head, x body; * pearl is not shown), then what it did."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/local')
from replay_format import load, point
from count_local import Geo
from pathlib import Path
from collections import deque

arm, game, R, who = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rad = int(sys.argv[5]) if len(sys.argv) > 5 else 4
side = int(game[-1])
root = load(Path('~/meow-redteam/solo/runs') / arm / game / 'game.replay').root()
bodies, teams, raw = {}, {}, []
for line in root.text(0).splitlines():
    q = line.split('#', 1)[0].split()
    if not q:
        continue
    if q[0] == 'MAP':
        w, h = map(int, q[1:3])
    elif q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
        teams[i] = 0 if int(q[1]) == side else 1
    elif q[0] == 'EDGE':
        raw.append(tuple(map(int, q[1:4])))
g = Geo(w, h, raw)
queen = min(i for i in bodies if teams[i] == 0)
tile = lambda p: p[1]*w+p[0]
rnd, actor, show = -1, None, False


def draw(c0):
    x0, y0 = c0 % w, c0 // w
    occ = {}
    for i, b in bodies.items():
        for k, c in enumerate(b):
            occ[c] = ('Q' if i == queen else 'H' if teams[i] == 0 else 'h') if k == 0 else ('o' if teams[i] == 0 else 'x')
    for dy in range(-rad, rad+1):
        row = ''
        for dx in range(-rad, rad+1):
            c = ((y0+dy) % h)*w+(x0+dx) % w
            row += ('@' if c == c0 else occ.get(c, '.'))
            row += '|' if g.moves[c][1][0] == 1 else ' '
        print('%3d  %s' % ((y0+dy) % h, row))
        row = '     '
        for dx in range(-rad, rad+1):
            c = ((y0+dy) % h)*w+(x0+dx) % w
            row += ('-' if g.moves[c][2][0] == 1 else ' ') + ' '
        if '-' in row:
            print(row)
    print('     x from %d; heads near:' % ((x0-rad) % w), ' '.join('#%d%s L%d (%d,%d)' % (i, 'ours' if teams[i] == 0 else 'theirs', len(b), b[0] % w, b[0] // w)
          for i, b in bodies.items() if abs((b[0] % w-x0+w//2) % w-w//2) <= rad and abs((b[0]//w-y0+h//2) % h-h//2) <= rad))


for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        rnd, actor = p.i32(0), None
        if rnd > R:
            break
    elif k == 1:
        if show:
            break
        actor = p.i32(0)
        if rnd == R and actor == who:
            show = True
            print('r%d #%d L%d at (%d,%d)' % (rnd, who, len(bodies[who]), bodies[who][0] % w, bodies[who][0] // w))
            draw(bodies[who][0])
    elif k == 9:
        i = p.i32(0)
        hd, tl = tile(point(p.pointer(0))), tile(point(p.pointer(1)))
        b = bodies[i]
        if show:
            print('  move #%d head to (%d,%d)' % (i, hd % w, hd // w))
        if b[0] != hd:
            b.appendleft(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif k == 10:
        parent, child = p.i32(0), p.i32(4)
        for z, i in enumerate((parent, child)):
            bodies[i] = deque(tile(point(c)) for c in p.pointer(z))
        teams[child] = teams[parent]
        if show:
            print('  split #%d child #%d' % (parent, child))
    elif k == 11:
        i, reason = p.i32(0), p.u16(4)
        if show:
            print('  death #%d reason %d' % (i, reason))
        bodies.pop(i)
