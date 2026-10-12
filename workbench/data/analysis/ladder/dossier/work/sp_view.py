# Scratch (diag-spawn): text frames of the board around one tile, one frame per round start.
# Focal heads are capital letters (id mod 26), their bodies the same letter in lower case; opponent heads are
# digits (id mod 10), their bodies "+"; a pearl is "*"; the centre tile is bracketed in the header.
# Under each frame: what happened in that round inside the window (eat, split, death).
# Usage: python3 data/analysis/ladder/dossier/work/sp_view.py <game> <x> <y> <from> <to> [radius]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque

game, cx, cy, r0, r1 = (int(v) for v in sys.argv[1:6])
rad = int(sys.argv[6]) if len(sys.argv) > 6 else 3
row = None
for f in ('data/analysis/ladder/dossier/per-game.jsonl', 'data/analysis/ladder/dossier/target/per-game-top1.jsonl'):
    for line in open(f):
        if ('"game":%d,' % game) in line:
            r = json.loads(line)
            if r['relation'] == 'us':
                row = r
assert row, 'game not found'
root = replay.load(row['replay']).root()
text = root.text(0)
w, h = map(int, text.splitlines()[0].split()[1:3])
bodies, teams = {}, {}
for line in text.splitlines():
    q = line.split()
    if q and q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
        teams[i] = 'AB'[int(q[1])]
focal = row['our_side']
pearls = set()
notes = []
CAUSE = ('wall', 'own body', 'a body', 'head-on', 'no action')


def inside(p):
    dx = min(abs(p[0] - cx), w - abs(p[0] - cx))
    dy = min(abs(p[1] - cy), h - abs(p[1] - cy))
    return dx <= rad and dy <= rad


def frame(rnd):
    grid = {}
    for p in pearls:
        grid[p] = '*'
    for i, b in bodies.items():
        f = teams[i] == focal
        for n, c in enumerate(b):
            if f:
                grid[c] = chr(65 + i % 26) if n == 0 else chr(97 + i % 26)
            else:
                grid[c] = str(i % 10) if n == 0 else '+'
    print('round %d  (%s %s, layout %s, tile [%d,%d])' % (rnd, row['team'], row['result'], row['layout_key'], cx, cy))
    for dy in range(-rad, rad + 1):
        print('   ' + ' '.join(grid.get(((cx + dx) % w, (cy + dy) % h), '.') for dx in range(-rad, rad + 1)))
    ids = sorted(i for i, b in bodies.items() if inside(b[0]))
    print('   heads here: ' + ', '.join('%s%d(len %d)' % ('F' if teams[i] == focal else 'X', i, len(bodies[i])) for i in ids))


rnd, actor, shown = 0, None, False
for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        if shown:
            for n in notes:
                print('      ' + n)
        notes = []
        rnd, actor, shown = p.i32(0), None, False
        if rnd > r1:
            break
    elif k == 1:
        actor = p.i32(0)
        if not shown and r0 <= rnd <= r1:
            frame(rnd)
            shown = True
    elif k == 3:
        c = replay.point(p.pointer(0))
        if p.u32(0):
            pearls.add(c)
            if inside(c) and actor is None:
                notes.append('born at %d,%d' % c)
        else:
            pearls.discard(c)
            if inside(c):
                notes.append('%s%d eats at %d,%d' % ('F' if teams[actor] == focal else 'X', actor, c[0], c[1]))
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
        teams[c] = teams[a] = 'AB'[p.u16(8)]
        for zz, i in enumerate((a, c)):
            bodies[i] = deque(replay.point(x) for x in p.pointer(zz))
        if inside(bodies[a][0]) or inside(bodies[c][0]):
            notes.append('%s%d splits off %d (len %d and %d)' % ('F' if teams[a] == focal else 'X', a, c, len(bodies[a]), len(bodies[c])))
    elif k == 11:
        i = p.i32(0)
        if inside(bodies[i][0]):
            notes.append('%s%d dies (%s), len %d' % ('F' if teams[i] == focal else 'X', i, CAUSE[min(p.u16(4), 4)], len(bodies[i])))
        bodies.pop(i)
