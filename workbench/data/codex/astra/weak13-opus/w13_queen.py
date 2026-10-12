"""For one game: the round from which we are behind for good, and our queen's death with the attacker's turn.
Behind for good = first round r such that at the end of every round >= r the judgement tuple (alive>0, queen, longest, total)
of ours is lower than theirs. Attacker: id, length at turn start, head at turn start, steps, pearls eaten in the turn, length paid,
torus distance to the queen's head, whether its head was inside her 7 by 7 at her last own turn start and at its own turn start.
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_queen.py <battle> <gid>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from pathlib import Path

battle, gid = sys.argv[1], int(sys.argv[2])
folder = Path('data/online/live-one1') / battle
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
queen = {s: min(i for i in teams if (teams[i] == own) == (s == 0)) for s in (0, 1)}


def gap(a, b):
    dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
    return min(dx, W - dx) + min(dy, H - dy)


def inview(c, h):
    return abs((c[0] - h[0] + W // 2) % W - W // 2) <= 3 and abs((c[1] - h[1] + H // 2) % H - H // 2) <= 3


def tup(s):
    ls = [len(b) for i, b in bodies.items() if (teams[i] == own) == (s == 0)]
    return (1 if ls else 0, len(bodies.get(queen[s], ())), max(ls, default=0), sum(ls))


per = {}
rnd = -1
turn = None
qturns = []          # our queen's own turn starts: (round, head, length, enemy heads in view)
out = []
qdead = {}
for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 4, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        if rnd >= 0:
            per[rnd] = (tup(0), tup(1))
        rnd = p.i32(0)
    elif k == 1:
        a = p.i32(0)
        b = bodies[a]
        turn = dict(i=a, L=len(b), h=b[0], e=0, steps=0, act='none', team=teams[a], path=[b[0]])
        if a == queen[0]:
            foes = [(z, len(bb), bb[0]) for z, bb in bodies.items() if teams[z] != own and inview(bb[0], b[0])]
            qturns.append((rnd, b[0], len(b), foes))
        if queen[0] in bodies:
            turn['qh'] = bodies[queen[0]][0]
            turn['qL'] = len(bodies[queen[0]])
    elif k == 4:
        a = p.pointer(0)
        if a is not None and a.u16(0) == 0 and a.pointer(0) is not None:
            turn['act'] = ''.join('NESW'[x] for x in a.pointer(0))
    elif k == 3:
        if not p.u32(0):
            turn['e'] += 1
    elif k == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        b = bodies[i]
        if b[0] != hd:
            b.appendleft(hd)
            if turn and i == turn['i']:
                turn['steps'] += 1
                turn['path'].append(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif k == 10:
        par = p.i32(0)
        for z, i in enumerate((par, p.i32(4))):
            bodies[i] = deque(replay.point(c) for c in p.pointer(z))
            teams[i] = p.u16(8)
        if par == queen[0]:
            out.append('  our queen split r%d -> keeps %d, child #%d %d' % (rnd, len(bodies[par]), p.i32(4), len(bodies[p.i32(4)])))
    elif k == 11:
        i, reason = p.i32(0), p.u16(4)
        if i in (queen[0], queen[1]):
            s = 0 if i == queen[0] else 1
            qdead[s] = rnd
            L = len(bodies[i])
            line = '  %s queen #%d dies r%d L%d reason %s' % ('OUR' if s == 0 else 'their', i, rnd, L, ('wall', 'own body', 'body', 'head', 'stop')[reason])
            if s == 0:
                line += ' | their queen %s' % ('alive L%d' % len(bodies[queen[1]]) if queen[1] in bodies else 'dead since r%d' % qdead.get(1, -1))
                if turn['i'] != i:
                    a = turn
                    Lnow = len(bodies[a['i']]) if a['i'] in bodies else None
                    last = qturns[-1]
                    line += '\n    attacker #%d L%d from %s, order "%s", steps to hit %d (free steps ceil(L/4)=%d), pearls eaten on the way %d, path %s' % (
                        a['i'], a['L'], a['h'], a['act'], a['steps'] + 1, -(-a['L'] // 4), a['e'], a['path'])
                    line += '\n    distance to her head %d; inside her 7x7 at her last turn start (r%d, head %s): %s; inside at its own turn start: %s' % (
                        gap(a['h'], bodies[i][0]), last[0], last[1], any(z == a['i'] for z, _, _ in last[3]), inview(a['h'], bodies[i][0]))
                    line += '\n    enemy heads in her 7x7 at her last three turn starts: %s' % [(r, h, L_, [(z, l) for z, l, _ in f]) for r, h, L_, f in qturns[-3:]]
                else:
                    line += '\n    died on her own turn, order "%s", after %d steps from %s' % (turn['act'], turn['steps'], turn['h'])
            out.append(line)
        bodies.pop(i)
per[rnd] = (tup(0), tup(1))
last = max(per)
behind = None
for r in range(last, -1, -1):
    if r in per and per[r][0] < per[r][1]:
        behind = r
    elif r in per:
        break
print('%d %s: behind for good from r%s (end r%d); final us %s them %s (alive, queen, longest, total)' % (gid, j['mapName'], behind, last, per[last][0], per[last][1]))
if behind is not None and behind > 0:
    print('  round before: us %s them %s' % (per[behind - 1][0], per[behind - 1][1]))
for line in out[-8:]:
    print(line)
