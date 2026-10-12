"""waste.py <smoke folder> ...: our splits whose L2 child (or parent) dies in the same round as its own actor, per game. Run from ROOT."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from pathlib import Path
from ladder_replay import replay
from collections import deque
SM = Path('data/online/smoke')


def count(path, own):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    rnd, born, out = -1, {}, [[], []]
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
        elif k == 1:
            actor = p.i32(0)
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
            born[child] = (rnd, parent, born.get(parent, (-9,))[0] == rnd)
        elif k == 11:
            i = p.i32(0)
            s = 0 if teams[i] == own else 1
            if i in born and born[i][0] == rnd and i == actor and born[i][2] and len(bodies[i]) == 2:
                out[s].append(rnd)
            bodies.pop(i)
    return out, rnd


tot = [0, 0]
games = 0
for f in sys.argv[1:]:
    for mp in sorted((SM / f).glob('game-*.json')):
        j = json.loads(mp.read_text())
        rp = SM / f / ('M%d.replay' % j['id'])
        if not rp.exists() or 1119 not in (j['teamAId'], j['teamBId']):
            continue
        out, last = count(rp, 0 if j['teamAId'] == 1119 else 1)
        games += 1
        tot[0] += len(out[0])
        tot[1] += len(out[1])
        if out[0]:
            print('%s %d %-16s us %2d (r<=100: %d) rounds %s | opp %d' % (f[:10], j['id'], j.get('mapName', '?')[:16], len(out[0]), sum(1 for r in out[0] if r <= 100), out[0][:8], len(out[1])))
print('games', games, 'our events', tot[0], 'opp events', tot[1], '(event = a 2-long child of a same-round newborn dies on its own first move)')
