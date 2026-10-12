"""watch17-opus: queen trace over a round window. Usage (from ROOT): python3 -B .../trace.py <game json path> <r0> <r1>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque
from pathlib import Path

f, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
X = int(sys.argv[4]) if len(sys.argv) > 4 else -9
j = json.load(open(f))
rp = Path(f).parent / ('M%d.replay' % j['id'])
ours = 0 if j['teamAId'] == 1119 else 1
root = replay.load(rp).root()
G = geometry(root.text(0))
W, H = G['W'], G['H']
bodies = {i: deque(b) for i, b in G['bodies'].items()}
teams = dict(G['teams'])
Q = min(i for i in teams if teams[i] == ours)
N = replay.EVENT_NAMES
RS = {0: 'wall', 1: 'own', 2: 'body', 3: 'headon', 4: 'other'}


def gap(a, b):
    ax, ay, bx, by = a % W, a // W, b % W, b // W
    dx, dy = abs(ax - bx), abs(ay - by)
    return min(dx, W - dx) + min(dy, H - dy)


rnd = -1
actor = None
print(j['id'], j['mapName'], W, H, 'queen id', Q)
for ev in root.pointer(3):
    k = N[ev.u16(0)]
    p = ev.pointer(0)
    if k == 'roundStart':
        rnd = p.i32(0)
        actor = None
        if r0 <= rnd <= r1 and Q in bodies:
            h = bodies[Q][0]
            foes = sorted((gap(h, b[0]), len(b), i, (b[0] % W, b[0] // W)) for i, b in bodies.items() if teams[i] != ours)[:4]
            mates = sorted((gap(h, b[0]), len(b), i) for i, b in bodies.items() if teams[i] == ours and i != Q)[:3]
            print('r%d Q len %d head %s | foes %s | mates %s | alive us %d them %d' % (rnd, len(bodies[Q]), (h % W, h // W), foes, mates,
                  sum(1 for i in bodies if teams[i] == ours), sum(1 for i in bodies if teams[i] != ours)))
    elif k == 'turnStart':
        actor = p.i32(0)
    elif k == 'dragonAction':
        if r0 <= rnd <= r1 and p.i32(0) == Q:
            a = p.pointer(0)
            kind = a.u16(0) if a else 9
            dirs = list(a.pointer(0)) if a and kind == 0 and a.pointer(0) is not None else []
            print('   Q action kind %d dirs %s' % (kind, dirs))
    elif k == 'dragonUpdate':
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
        b = bodies[i]
        before = len(b)
        if b[0] != hd:
            b.appendleft(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
        if i == X and r0 <= rnd <= r1:
            print('      X%d update head %s len %d>%d' % (X, (hd % W, hd // W), before, len(b)))
        if i == Q and r0 <= rnd <= r1:
            print('   Q update (actor %s) head %s len %d>%d' % (actor, (hd % W, hd // W), before, len(b)))
    elif k == 'dragonSplit':
        par, ch = p.i32(0), p.i32(4)
        before = len(bodies[par]) if par in bodies else 0
        for z, i in enumerate((par, ch)):
            bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
            teams[i] = p.u16(8)
        if Q in (par, ch) and r0 <= rnd <= r1:
            print('   Q SPLIT parent %d (%d>%d) child %d len %d' % (par, before, len(bodies[par]), ch, len(bodies[ch])))
    elif k == 'dragonDeath':
        i = p.i32(0)
        if r0 <= rnd <= r1 and (i == Q or (Q in bodies and gap(bodies[Q][0], bodies[i][0]) <= 4)):
            print('   DEATH id %d team %s len %d reason %s (actor %s)%s' % (i, 'us' if teams[i] == ours else 'them', len(bodies[i]), RS.get(p.u16(4)), actor, '  <== QUEEN' if i == Q else ''))
        bodies.pop(i)
