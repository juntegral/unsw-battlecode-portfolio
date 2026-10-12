"""Per-round trace of one side: every dragon (id, length, head, steps taken this round), plus eats, splits, deaths of both sides.
Usage: python3 -B data/codex/astra/h2hloss-opus/trace.py <arm> <folder> <r0> <r1> [side: new|old|both]"""
import sys, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from pathlib import Path
arm, folder, r0, r1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
show = sys.argv[5] if len(sys.argv) > 5 else 'new'
k = int(re.search(r'side(\d)$', folder)[1])
root = replay.load(Path.home() / 'meow-redteam/solo/runs' / arm / folder / 'game.replay').root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
bodies, teams = {}, {}
for line in lines:
    q = line.split()
    if q and q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * z]), int(q[4 + 2 * z])) for z in range(int(q[2])))
        teams[i] = int(q[1])
tm = sorted(set(teams.values()))
newteam = tm[k]
def nm(i):
    return ('N' if teams[i] == newteam else 'O') + str(i)
rnd, actor, moved, notes = -1, None, {}, []
def flush():
    if r0 <= rnd <= r1:
        out = []
        for i in sorted(bodies):
            isnew = teams[i] == newteam
            if show == 'both' or (show == 'new') == isnew:
                out.append('%s:%d@%d,%d%s' % (nm(i), len(bodies[i]), bodies[i][0][0], bodies[i][0][1], ('+%d' % moved.get(i, 0)) if moved.get(i, 0) != 1 else ''))
        print('r%d %s' % (rnd, ' '.join(out)))
        for n in notes:
            print('     ' + n)
for ev in root.pointer(3):
    kk = ev.u16(0)
    if kk not in (0, 1, 3, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if kk == 0:
        flush()
        rnd, moved, notes = p.i32(0), {}, []
        if rnd > r1:
            break
    elif kk == 1:
        actor = p.i32(0)
    elif kk == 3:
        if not p.u32(0):
            notes.append('%s eats %s' % (nm(actor), replay.point(p.pointer(0))))
    elif kk == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        b = bodies[i]
        if b[0] != hd:
            b.appendleft(hd)
            moved[i] = moved.get(i, 0) + 1
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif kk == 10:
        pa, ch = p.i32(0), p.i32(4)
        for z, i in enumerate((pa, ch)):
            bodies[i] = deque(replay.point(c) for c in p.pointer(z))
            teams[i] = p.u16(8)
        notes.append('%s splits -> %s:%d + %s:%d' % (nm(pa), nm(pa), len(bodies[pa]), nm(ch), len(bodies[ch])))
    elif kk == 11:
        i = p.i32(0)
        notes.append('%s dies (reason %d, len %d at %s) during turn of %s' % (nm(i), p.u16(4), len(bodies[i]), bodies[i][0], nm(actor)))
        bodies.pop(i)
flush()
