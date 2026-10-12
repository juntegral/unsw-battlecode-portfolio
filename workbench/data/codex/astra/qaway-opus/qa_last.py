"""qaway-opus: our queen's last turns. Usage (repo root): python3 -B data/codex/astra/qaway-opus/qa_last.py <run dir> <seat> [turns]"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
from pathlib import Path
from collections import deque
import qdeath
replay = qdeath.replay
folder, k = Path(sys.argv[1]), int(sys.argv[2])
N = int(sys.argv[3]) if len(sys.argv) > 3 else 6
root = replay.load(folder / 'game.replay').root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
bodies, teams = {}, {}
for line in lines:
    q = line.split()
    if q and q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * z]), int(q[4 + 2 * z])) for z in range(int(q[2])))
        teams[i] = int(q[1])
Q = min(i for i in bodies if teams[i] == k)
hist, rnd, actor = [], -1, None


def foes(h):
    out = []
    for i, b in bodies.items():
        if teams[i] == teams[Q]:
            continue
        dx = abs(h[0] - b[0][0]); dx = min(dx, W - dx)
        dy = abs(h[1] - b[0][1]); dy = min(dy, H - dy)
        if dx + dy <= 9:
            out.append('id%d L%d gap%d%s' % (i, len(b), dx + dy, '' if dx <= 3 and dy <= 3 else '(unseen)'))
    return out


for ev in root.pointer(3):
    kk = ev.u16(0)
    if kk not in (0, 1, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if kk == 0:
        rnd = p.i32(0)
    elif kk == 1:
        actor = p.i32(0)
        if actor == Q and Q in bodies:
            hist.append(dict(r=rnd, h=bodies[Q][0], L=len(bodies[Q]), foes=foes(bodies[Q][0]), steps=0, end=None))
    elif kk == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        b = bodies[i]
        if b[0] != hd:
            b.appendleft(hd)
            if i == Q and actor == Q and hist:
                hist[-1]['steps'] += 1
                hist[-1]['end'] = hd
                hist[-1]['endfoes'] = foes(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif kk == 10:
        parent, child = p.i32(0), p.i32(4)
        for z, i in enumerate((parent, child)):
            bodies[i] = deque(replay.point(c) for c in p.pointer(z))
            teams[i] = p.u16(8)
    elif kk == 11:
        i = p.i32(0)
        if i == Q:
            print('queen died r%d reason %d on the turn of dragon %s (L%d, team %s)' % (rnd, p.u16(4), actor, len(bodies.get(actor, [])), teams.get(actor)))
        bodies.pop(i, None)
for t in hist[-N:]:
    print('r%d L%d at %s steps %d -> %s | start: %s | end: %s' % (t['r'], t['L'], t['h'], t['steps'], t['end'], ', '.join(t['foes']) or '-', ', '.join(t.get('endfoes', [])) or '-'))
