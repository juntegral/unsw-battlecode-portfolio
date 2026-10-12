"""qaway-opus: local on/off table. Usage (repo root): python3 -B data/codex/astra/qaway-opus/qa_cmp.py <opp> <off arm> <on arm> [<on arm>]"""
import sys, re, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
from pathlib import Path
from o1_scan import scan
import qdeath
RUNS = Path.home() / 'meow-redteam/solo/runs'
CACHE = Path('data/codex/astra/qaway-opus/cache')
CACHE.mkdir(exist_ok=True)


def away(folder, k):
    """Our queen's turn starts with an enemy head in her 7 by 7 view: {round: torus manhattan gap to the nearest}."""
    from collections import deque
    replay = qdeath.replay
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
    out, outend, rnd, pend = {}, {}, -1, None

    def gapnow():
        h = bodies[Q][0]
        best = 99
        for i, b in bodies.items():
            if teams[i] == teams[Q]:
                continue
            dx = abs(h[0] - b[0][0]); dx = min(dx, W - dx)
            dy = abs(h[1] - b[0][1]); dy = min(dy, H - dy)
            if dx <= 3 and dy <= 3 and dx + dy < best:
                best = dx + dy
        return best
    for ev in root.pointer(3):
        kk = ev.u16(0)
        if kk not in (0, 1, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if kk in (0, 1) and pend is not None:
            if Q in bodies:
                outend.setdefault(pend, gapnow())
            pend = None
        if kk == 0:
            rnd = p.i32(0)
        elif kk == 1:
            if p.i32(0) == Q and Q in bodies:
                out.setdefault(rnd, gapnow())
                pend = rnd
        elif kk == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif kk == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
        elif kk == 11:
            bodies.pop(p.i32(0), None)
    return out, outend


def game(arm, folder):
    cp = CACHE / ('%s--%s.v4.json' % (folder.parent.name, folder.name))
    if cp.exists():
        return json.loads(cp.read_text())
    m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
    k = int(m[3])
    j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
    g = scan(arm, folder / 'game.replay', j)
    q = qdeath.scan(folder / 'game.replay', k)

    def sn(r):
        r = min(r, g['last'])
        return g['snaps'].get(str(r), g['snaps'][str(g['last'])])
    row = dict(res=g['result'], how=g['how'], last=g['last'],
               q100=sn(100)[0][3], q200=sn(200)[0][3], q350=sn(350)[0][3], q400=sn(400)[0][3], qend=g['ends'][0][3], oqend=g['ends'][1][3],
               p100=sum(1 for e in g['eats'] if e[1] == 0 and e[0] <= 100), d100=sn(100)[0][0], t100=sn(100)[0][1],
               qd=[dict(r=d['r'], L=d['L'], own=d['own_turn']) for d in q['deaths']])
    root = qdeath.replay.load(folder / 'game.replay').root()
    bodies = {}
    teams = {}
    for line in root.text(0).splitlines():
        p = line.split()
        if p and p[0] == 'DRAGON':
            teams[len(teams)] = int(p[1])
    Q = min(i for i in teams if teams[i] == k)
    seq, rnd, actor = [], -1, None
    for ev in root.pointer(3):
        kk = ev.u16(0)
        p = ev.pointer(0)
        if kk == 0:
            rnd = p.i32(0)
        elif kk == 1:
            actor = p.i32(0)
        elif kk == 4:
            a = p.pointer(0)
            dirs = tuple(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else ('other', a.u16(0) if a else -1)
            seq.append((rnd, actor, [str(x) for x in dirs]))
    row['seq'] = seq
    row['Q'] = Q
    row['away'], row['awayend'] = away(folder, k)
    cp.write_text(json.dumps(row))
    return json.loads(cp.read_text())


def firstdiff(a, b):
    for x, y in zip(a['seq'], b['seq']):
        if x != y:
            who = 'QUEEN' if x[1] == a['Q'] else 'dragon %d' % x[1]
            return 'r%d %s' % (x[0], who) if x[:2] == y[:2] else 'order r%d' % x[0]
    return 'identical' if len(a['seq']) == len(b['seq']) else 'same until one ends'


def qtxt(r):
    return ';'.join('r%d L%d %s' % (d['r'], d['L'], 'own' if d['own'] else 'rammed') for d in r['qd']) or 'lives'


def main():
    opp, arms = sys.argv[1], sys.argv[2:]
    dirs = ['%s_%s' % (a, opp) for a in arms]
    names = sorted(f.name for f in (RUNS / dirs[0]).glob('*-seed*-side*')
                   if f.is_dir() and all((RUNS / d / f.name / 'result.txt').exists() for d in dirs))
    tot = {a: dict(n=0, win=0, qalive=0, qend=0, q100=0, q200=0, p100=0, d100=0, near=0, nearsum=0, turns=0, deathsum=0) for a in arms}
    D = 7
    print('opponent %s; cell = res q100/q200/q350/q400/qend p100 d100 | queen turns with an enemy head in view / her turns (gap<=3) mean gap | queen' % opp)
    for n in names:
        pair = [game(a, RUNS / d / n) for a, d in zip(arms, dirs)]
        print(n[:40])
        for a, r in zip(arms, pair):
            aw = {int(x): y for x, y in r['away'].items()}
            near = [v for v in aw.values() if v < D]
            near3 = [v for v in near if v <= 3]
            end4 = sum(1 for v in r['awayend'].values() if v <= 4)
            t = tot[a]
            t['near3'] = t.get('near3', 0) + len(near3)
            t['n'] += 1
            t['win'] += r['res'] == 'win'
            t['qalive'] += r['qend'] > 0
            t['end4'] = t.get('end4', 0) + end4
            for key in ('q350', 'q400'):
                t[key] = t.get(key, 0) + r[key]
            for key in ('qend', 'q100', 'q200', 'p100', 'd100'):
                t[key] += r[key]
            t['near'] += len(near)
            t['nearsum'] += sum(near)
            t['turns'] += len(aw)
            t['deathsum'] += r['qd'][0]['r'] if r['qd'] else r['last']
            print('  %-5s %-5s %2d/%2d/%2d/%2d/%2d p %3d d %2d | seen %3d/%3d (<=3: %2d) mean %.2f end<=4: %3d | %s | vs %s: %s' % (
                a, r['res'], r['q100'], r['q200'], r['q350'], r['q400'], r['qend'], r['p100'], r['d100'], len(near), len(aw), len(near3),
                sum(near) / len(near) if near else 0, end4, qtxt(r), arms[0], firstdiff(pair[0], r) if a != arms[0] else '-'))
    for a in arms:
        t = tot[a]
        t['meanNear'] = round(t['nearsum'] / t['near'], 2) if t['near'] else 0
        print(a, json.dumps(t))


main()
