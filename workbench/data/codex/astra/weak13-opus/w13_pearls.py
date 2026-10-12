"""Pearl ledger per 25 rounds: natural spawns, eaten by us / them (natural, own-corpse, foe-corpse), pearls lying at window end,
and where they lie (count nearer to one of our heads than to any of theirs, torus manhattan).
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_pearls.py <battle> <gid> [step]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from pathlib import Path

battle, gid = sys.argv[1], int(sys.argv[2])
step = int(sys.argv[3]) if len(sys.argv) > 3 else 25
folder = Path('data/online/live-one1') / battle if not battle.startswith('data/') else Path(battle)
j = json.loads((folder / ('game-%d.json' % gid)).read_text())
root = replay.load(folder / ('M%d.replay' % gid)).root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
bodies, teams = {}, {}
for line in lines:
    q = line.split()
    if q and q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
        teams[i] = int(q[1])
own = 0 if j['teamAId'] == 1119 else 1


def gap(a, b):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


present = {}
c = Counter()
rnd = -1
actor = None
expected = 0
last_side = None
print('%s %s %dx%d' % (gid, j['mapName'], W, H))
print('window  spawn | us: nat own foe | them: nat own foe | lying  nearer-us nearer-them')


def row(r):
    ours = [b[0] for i, b in bodies.items() if teams[i] == own]
    theirs = [b[0] for i, b in bodies.items() if teams[i] != own]
    nu = nt = 0
    for p in present:
        du = min((gap(p, h) for h in ours), default=999)
        dt = min((gap(p, h) for h in theirs), default=999)
        if du < dt:
            nu += 1
        elif dt < du:
            nt += 1
    print('r%-4d  %5d | %7d %3d %3d | %9d %3d %3d | %5d  %9d %11d' % (
        r, c['spawn'], c['us', 'n'], c['us', 'own'], c['us', 'foe'], c['them', 'n'], c['them', 'own'], c['them', 'foe'],
        len(present), nu, nt))


for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        if rnd >= 0 and (rnd + 1) % step == 0:
            row(rnd)
            c.clear()
        rnd = p.i32(0)
        actor = None
    elif k == 1:
        actor = p.i32(0)
    elif k == 3:
        xy = replay.point(p.pointer(0))
        if p.u32(0):
            if expected:
                present[xy] = last_side
                expected -= 1
            else:
                present[xy] = None
                c['spawn'] += 1
        else:
            src = present.pop(xy)
            s = 'us' if teams[actor] == own else 'them'
            o = 'n' if src is None else 'own' if src == teams[actor] else 'foe'
            c[s, o] += 1
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
    elif k == 11:
        i = p.i32(0)
        last_side = teams[i]
        expected = (len(bodies[i]) + 1) // 2
        bodies.pop(i)
row(rnd)
