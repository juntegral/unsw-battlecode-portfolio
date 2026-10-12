"""unB-opus health line per game and seat. Usage (ROOT): python3 -B data/codex/astra/unB-opus/health.py <arm> [filter] [trace]"""
import sys, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, defaultdict, Counter
from pathlib import Path
RUNS = Path.home() / 'meow-redteam/solo/runs'
KD = {0: 'wall', 1: 'own', 2: 'body', 3: 'head'}


def scan(path, trace=False):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    start = {i: b[0] for i, b in bodies.items()}
    queens = {t: min(i for i in teams if teams[i] == t) for t in (0, 1)}
    S = [dict(first=None, eats=Counter(), left={}, loop=0, dr=0, qd=None, snaps={}, deaths=Counter(), loopids=Counter()) for _ in (0, 1)]
    hist, lasteat = defaultdict(lambda: deque(maxlen=30)), {}
    rnd, actor = -1, None
    tr = []

    def snap():
        for s in (0, 1):
            ls = [len(b) for i, b in bodies.items() if teams[i] == s]
            S[s]['snaps'][rnd] = (len(ls), sum(ls), len(bodies.get(queens[s], ())))
        for i, b in bodies.items():
            s = teams[i]
            hist[i].append(b[0])
            S[s]['dr'] += 1
            if len(hist[i]) == 30 and len(set(hist[i])) <= 12 and rnd - lasteat.get(i, -99) >= 30:
                S[s]['loop'] += 1
                S[s]['loopids'][i] += 1
            if i in start and i not in S[s]['left'] and abs(b[0][0] - start[i][0]) + abs(b[0][1] - start[i][1]) >= 6:
                S[s]['left'][i] = rnd
        if trace and rnd <= 60:
            tr.append((rnd, {i: b[0] for i, b in bodies.items() if teams[i] == 0 and i in start}))

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            snap()
        elif k == 1:
            actor = p.i32(0)
        elif k == 3:
            if not p.u32(0):
                s = teams[actor]
                if S[s]['first'] is None:
                    S[s]['first'] = rnd
                S[s]['eats'][rnd] += 1
                lasteat[actor] = rnd
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
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = teams[i]
            kd = KD.get(reason, 'stop')
            if kd == 'head':
                kd = 'head-self' if i == actor else ('rammed' if teams[actor] != s else 'mate-head')
            if rnd < 100:
                S[s]['deaths'][kd] += 1
            if i == queens[s]:
                S[s]['qd'] = (rnd, kd, len(bodies[i]), int(i == actor))
            bodies.pop(i)
    last = rnd
    rnd += 1
    for s in (0, 1):
        ls = [len(b) for i, b in bodies.items() if teams[i] == s]
        S[s]['snaps'][rnd] = (len(ls), sum(ls), len(bodies.get(queens[s], ())))
    return S, last, tr


def line(S, last, s):
    d = S[s]

    def at(r):
        return d['snaps'][min(r, max(d['snaps']))]

    e = lambda r: sum(v for k, v in d['eats'].items() if k < r)
    left = sorted(d['left'].values())
    return 'first %s left %s eat %d/%d/%d drg %d/%d/%d loop %.0f%% q %s qL %d/%d/%d early-deaths %s' % (
        d['first'], left, e(25), e(50), e(100), at(25)[0], at(50)[0], at(100)[0], 100 * d['loop'] / max(1, d['dr']),
        d['qd'] or 'alive', at(100)[2], at(300)[2], at(10 ** 6)[2], dict(d['deaths']))


if __name__ == '__main__':
    arm = sys.argv[1]
    flt = sys.argv[2] if len(sys.argv) > 2 else ''
    for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
        if flt not in folder.name or not (folder / 'result.txt').exists():
            continue
        k = int(folder.name[-1])
        S, last, tr = scan(folder / 'game.replay', len(sys.argv) > 3)
        res = (folder / 'result.txt').read_text().strip().replace('\n', ' ')[:70]
        log = (folder / 'engine.log').read_text() if (folder / 'engine.log').exists() else ''
        bad = len(re.findall(r'(?i)crash|timeout|timed out|illegal|exception', log))
        print('%s last %d bad %d | %s' % (folder.name, last, bad, res))
        print('   US  ', line(S, last, k))
        print('   THEM', line(S, last, 1 - k))
        for r, hs in tr:
            print('    ', r, hs)
