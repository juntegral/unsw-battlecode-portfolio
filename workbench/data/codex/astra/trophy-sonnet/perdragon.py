"""Per-dragon activity in a round window. Usage: perdragon.py <replay path> <ourteam index 0/1> r0 r1"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/tools')
from ladder_replay import replay
from collections import deque, defaultdict
path, own, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
root = replay.load(path).root()
lines = root.text(0).splitlines()
W, H = map(int, lines[0].split()[1:3])
bodies, teams = {}, {}
for line in lines:
    q = line.split()
    if q and q[0] == 'DRAGON':
        i = len(bodies)
        bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
        teams[i] = int(q[1])
birth = {i: 0 for i in bodies}
stat = defaultdict(lambda: dict(eats=0, moves=0, cells=set(), first=None, last=None, died=None, L0=None, L1=None, xing=0, born=None, hs=None))
rnd, actor = -1, None
for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
        if rnd > r1:
            break
    elif k == 1:
        actor = p.i32(0)
    elif k == 3:
        if not p.u32(0) and r0 <= rnd <= r1 and actor is not None and teams.get(actor) == own:
            stat[actor]['eats'] += 1
    elif k == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        b = bodies[i]
        if b[0] != hd:
            dx = abs(b[0][0] - hd[0]); dy = abs(b[0][1] - hd[1])
            x = min(dx, W - dx) + min(dy, H - dy) != 1
            b.appendleft(hd)
            if teams[i] == own and r0 <= rnd <= r1:
                s = stat[i]
                s['moves'] += 1
                s['cells'].add(hd)
                s['xing'] += x
                if s['first'] is None:
                    s['first'] = rnd; s['L0'] = len(b); s['hs'] = b[0]
                s['last'] = rnd; s['L1'] = len(b)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif k == 10:
        for z, i in enumerate((p.i32(0), p.i32(4))):
            bodies[i] = deque(replay.point(c) for c in p.pointer(z))
            teams[i] = p.u16(8)
            birth[i] = rnd
    elif k == 11:
        i = p.i32(0)
        if teams[i] == own:
            stat[i]['died'] = rnd
            stat[i]['dlen'] = len(bodies[i])
        bodies.pop(i)
print('id born first last died L0 L1 moves cells eats xing')
for i, s in sorted(stat.items()):
    print(i, birth.get(i), s['first'], s['last'], s['died'], s['L0'], s['L1'], s['moves'], len(s['cells']), s['eats'], s['xing'])
tot = sum(s['eats'] for s in stat.values())
print('total eats', tot, 'dragon-rounds', sum((s['last'] - s['first'] + 1) for s in stat.values() if s['first'] is not None))
