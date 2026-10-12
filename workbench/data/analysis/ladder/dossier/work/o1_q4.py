"""Scratch (diag-one1, job H): our queen round by round: length at each of her turns, her splits, her death.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_q4.py <set> [<set> ...]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from ladder_replay import replay
from collections import deque, Counter
from o1_scan import jobs, OUT


def scan(path, j, team=1119):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    own = 0 if j['teamAId'] == team else 1
    queen = min(i for i in bodies if teams[i] == own)
    lens, splits, death = {}, [], None
    rnd, actor, eats = -1, None, []
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
        elif k == 1:
            actor = p.i32(0)
            if actor == queen:
                lens[rnd] = len(bodies[queen])
        elif k == 3:
            if not p.u32(0) and actor == queen:
                eats.append(rnd)
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
            before = len(bodies[parent])
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if parent == queen:
                splits.append([rnd, before, len(bodies[queen])])
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if i == queen:
                death = [rnd, ('wall', 'own body', 'body', 'rammed' if actor != queen else 'ran into a head', 'no action')[reason], len(bodies[i])]
            bodies.pop(i)
    return dict(lens=lens, splits=splits, death=death, eats=eats, last=rnd)


if __name__ == '__main__':
    for name in sys.argv[1:]:
        tot = Counter()
        print('==', name)
        for label, path, j in jobs(name):
            r = scan(path, j)
            won = (j['winner'] == 'a') == (j['teamAId'] == 1119)
            early = [s for s in r['splits'] if s[0] < 20 and s[2] == 2]
            L = r['lens']
            t2 = sum(1 for rd, l in L.items() if rd <= 300 and l == 2)
            tt = sum(1 for rd in L if rd <= 300)
            info = ''
            if early:
                s0 = early[0][0]
                back = next((rd for rd in sorted(L) if rd > s0 and L[rd] >= 3), None)
                end = back if back is not None else (r['death'][0] if r['death'] else r['last'])
                info = 'split 4>2 at r%s; at 2 for %d rounds until %s' % ([s[0] for s in early], end - s0, 'she was 3 again' if back is not None else ('she died' if r['death'] else 'the end'))
                tot['early'] += 1
                tot['early rounds at 2'] += end - s0
                tot['early never 3 again'] += back is None
                if r['death']:
                    tot['early died'] += 1
                    tot['early died ' + r['death'][1]] += 1
                    tot['early died at 2'] += r['death'][2] == 2
                    tot['early died by r100'] += r['death'][0] <= 100
                tot['early won'] += won
            else:
                tot['none'] += 1
                if r['death']:
                    tot['none died'] += 1
                    tot['none died ' + r['death'][1]] += 1
                    tot['none died at 2'] += r['death'][2] == 2
                    tot['none died by r100'] += r['death'][0] <= 100
                tot['none won'] += won
            tot['t2'] += t2; tot['tt'] += tt
            print('  %d %-15s %s | start %d | %s | queen turns at 2 in r0-300: %d of %d | pearls %d | death %s' % (j['id'], j['mapName'][:15], 'W' if won else 'L', L.get(0, 0), info or 'no early split', t2, tt, len(r['eats']), r['death'] or 'alive'))
        print('  ', dict(tot))
