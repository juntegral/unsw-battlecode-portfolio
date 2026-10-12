"""Our non-queen dragons of 8 or longer that were rammed: how much of the attacker the victim could see at its last own turn start.
For each such death: victim length, attacker length, steps used, attacker parts inside the victim's 7 by 7 (centred on the victim's
head at its last turn start) at that moment, and the attacker's head distance to the victim's head after the victim moved.
Classes: unseen (0 parts in view), head-only/partial (fewer parts in view than the attacker has), full.
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_rammed.py [all]   (default: the two battles; all = plus the six one13 sets)"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from pathlib import Path

folders = [Path('data/online/live-one1/b1508960'), Path('data/online/live-one1/b1513119')]
if len(sys.argv) > 1:
    folders += [Path('data/online/smoke') / ('one13-%s-old' % s) for s in ('c1', 'k1', 'p1', 'c2', 'k2', 'p2')]
tot = Counter()
for folder in folders:
    for mp in sorted(folder.glob('game-*.json')):
        j = json.loads(mp.read_text())
        rp = folder / ('M%d.replay' % j['id'])
        if not rp.exists() or 1119 not in (j['teamAId'], j['teamBId']):
            continue
        root = replay.load(rp).root()
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
        queen = min(i for i in teams if teams[i] == own)

        def inview(c, h):
            return abs((c[0] - h[0] + W // 2) % W - W // 2) <= 3 and abs((c[1] - h[1] + H // 2) % H - H // 2) <= 3

        def gap(a, b):
            dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
            return min(dx, W - dx) + min(dy, H - dy)

        seen = {}      # our dragon -> {enemy id: (parts in view, enemy length)} at its last own turn start
        rnd, turn = -1, None
        for ev in root.pointer(3):
            k = ev.u16(0)
            if k not in (0, 1, 3, 9, 10, 11):
                continue
            p = ev.pointer(0)
            if k == 0:
                rnd = p.i32(0)
            elif k == 1:
                a = p.i32(0)
                turn = dict(i=a, L=len(bodies[a]), h=bodies[a][0], steps=0, e=0)
                if teams[a] == own and len(bodies[a]) >= 8:
                    h = bodies[a][0]
                    seen[a] = {z: (sum(1 for c in bb if inview(c, h)), len(bb)) for z, bb in bodies.items() if teams[z] != own and gap(h, bb[0]) <= 12}
            elif k == 3:
                if not p.u32(0) and turn:
                    turn['e'] += 1
            elif k == 9:
                i = p.i32(0)
                hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
                b = bodies[i]
                if b[0] != hd:
                    b.appendleft(hd)
                    if turn and i == turn['i']:
                        turn['steps'] += 1
                while len(b) > 1 and b[-1] != tl:
                    b.pop()
            elif k == 10:
                for z, i in enumerate((p.i32(0), p.i32(4))):
                    bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                    teams[i] = p.u16(8)
            elif k == 11:
                i, reason = p.i32(0), p.u16(4)
                L = len(bodies[i])
                if teams[i] == own and reason == 3 and turn['i'] != i and teams[turn['i']] != own and i != queen and L >= 8:
                    vis, aL = seen.get(i, {}).get(turn['i'], (0, turn['L']))
                    cls = 'unseen' if vis == 0 else 'partial' if vis < aL else 'full'
                    d = gap(turn['h'], bodies[i][0])
                    big = '15+' if L >= 15 else '8-14'
                    tot[big, cls] += 1
                    tot[big, 'all'] += 1
                    print('%s %d %-15s r%-3d victim #%d L%d | attacker #%d L%d, %d steps (free %d), ate %d, head distance %d | parts in view %d of %d -> %s' % (
                        folder.name, j['id'], j['mapName'], rnd, i, L, turn['i'], turn['L'], turn['steps'] + 1, -(-turn['L'] // 4), turn['e'], d, vis, aL, cls))
                bodies.pop(i)
                seen.pop(i, None)
print('totals:', sorted(tot.items()))
