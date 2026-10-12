"""sight-opus: arm beside the live bot, same map, seed and seat. Usage (repo root): python3 -B data/codex/astra/sight-opus/sg_cmp.py"""
import sys, re, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
from pathlib import Path
from collections import deque
from o1_scan import scan
import qdeath
replay = qdeath.replay
RUNS = Path.home() / 'meow-redteam/solo/runs'
CACHE = Path('data/codex/astra/sight-opus/cache')
CACHE.mkdir(exist_ok=True)
ARMS = ['f4', 'f8', 'e3', 'f8e3']


def last(folder, k):
    """Her death: round, length, killer id, killer's gap and seen or not at her last turn start."""
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
    rnd, actor, start, seq, death = -1, None, None, [], None
    for ev in root.pointer(3):
        kk = ev.u16(0)
        p = ev.pointer(0)
        if kk == 0:
            rnd = p.i32(0)
        elif kk == 1:
            actor = p.i32(0)
            if actor == Q and Q in bodies:
                h = bodies[Q][0]
                start = dict(r=rnd, L=len(bodies[Q]), foes={})
                for i, b in bodies.items():
                    if teams[i] != teams[Q]:
                        dx = abs(h[0] - b[0][0]); dx = min(dx, W - dx)
                        dy = abs(h[1] - b[0][1]); dy = min(dy, H - dy)
                        start['foes'][i] = (dx + dy, dx <= 3 and dy <= 3, len(b))
        elif kk == 4:
            a = p.pointer(0)
            dirs = tuple(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else ('other', a.u16(0) if a else -1)
            seq.append((rnd, actor, [str(x) for x in dirs]))
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
            i = p.i32(0)
            if i == Q and death is None:
                f = start['foes'].get(actor) if start else None
                death = dict(r=rnd, L=start['L'] if start else 0, own=actor == Q, killer=actor,
                             gap=f[0] if f else -1, seen=bool(f[1]) if f else False, kL=f[2] if f else 0)
            bodies.pop(i, None)
    return death, seq, Q


def game(folder, k):
    cp = CACHE / ('%s--%s--k%d.json' % (folder.parent.name, folder.name, k))
    if cp.exists():
        return json.loads(cp.read_text())
    m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
    j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
    g = scan('x', folder / 'game.replay', j)

    def sn(r):
        r = min(r, g['last'])
        return g['snaps'].get(str(r), g['snaps'][str(g['last'])])
    death, seq, Q = last(folder, k)
    row = dict(res=g['result'], last=g['last'], q200=sn(200)[0][3], q400=sn(400)[0][3], qend=g['ends'][0][3],
               p100=sum(1 for e in g['eats'] if e[1] == 0 and e[0] <= 100), d100=sn(100)[0][0], death=death, seq=seq, Q=Q)
    cp.write_text(json.dumps(row))
    return json.loads(cp.read_text())


def firstdiff(a, b):
    for x, y in zip(a['seq'], b['seq']):
        if x != y:
            who = 'QUEEN' if x[1] == a['Q'] else 'dragon %d' % x[1]
            return 'r%d %s' % (x[0], who) if x[:2] == y[:2] else 'order r%d' % x[0]
    return 'identical' if len(a['seq']) == len(b['seq']) else 'same until one ends'


def dtxt(r):
    d = r['death']
    if not d:
        return 'lives'
    if d['own']:
        return 'r%d L%d own turn' % (d['r'], d['L'])
    return 'r%d L%d rammed by L%d, %s' % (d['r'], d['L'], d['kL'], ('in view gap %d' % d['gap']) if d['seen'] else ('NOT in view gap %d' % d['gap']) if d['gap'] >= 0 else 'new dragon')


def line(tag, r, diff):
    return '  %-5s %-5s q200/400/end %2d/%2d/%2d  p100 %3d d100 %2d | %-38s | %s' % (tag, r['res'], r['q200'], r['q400'], r['qend'], r['p100'], r['d100'], dtxt(r), diff)


def done(f):
    return (f / 'result.txt').exists() and (f / 'game.replay').exists()


tot = {}
for opp in ('mD17', 'm3base'):
    base = RUNS / ('sg_L_%s' % opp)
    for bf in sorted(base.glob('*-seed*-side0')) if base.exists() else []:
        if not done(bf):
            continue
        for side in (0, 1):
            if opp == 'm3base' and side == 1:
                continue
            L = game(bf, side)
            rows = []
            for arm in ARMS:
                af = RUNS / ('sg_%s_%s' % (arm, opp)) / bf.name.replace('-side0', '-side%d' % side)
                if done(af):
                    rows.append((arm, game(af, side)))
            if not rows:
                continue
            print('%s seat %d vs %s' % (bf.name.replace('ladder_', '').replace('-side0', ''), side, opp))
            print(line('live', L, '-'))
            for arm, r in rows:
                d = firstdiff(L, r)
                print(line(arm, r, 'first differs: ' + d))
                t = tot.setdefault(arm, dict(pairs=0, identical=0, win=0, Lwin=0, ram=0, Lram=0, blind=0, Lblind=0, alive=0, Lalive=0, p100=0, Lp100=0, d100=0, Ld100=0, qend=0, Lqend=0, later=0, earlier=0))
                t['pairs'] += 1
                t['identical'] += d == 'identical'
                for key, x in (('', r), ('L', L)):
                    dd = x['death']
                    t[key + 'win'] += x['res'] == 'win'
                    t[key + 'ram'] += bool(dd and not dd['own'])
                    t[key + 'blind'] += bool(dd and not dd['own'] and not dd['seen'])
                    t[key + 'alive'] += not dd
                    t[key + 'p100'] += x['p100']
                    t[key + 'd100'] += x['d100']
                    t[key + 'qend'] += x['qend']
                ra = r['death']['r'] if r['death'] else 999
                rl = L['death']['r'] if L['death'] else 999
                t['later'] += ra > rl
                t['earlier'] += ra < rl
print()
print('totals per arm (arm / live on the same pairs)')
for arm, t in tot.items():
    print('%-5s pairs %2d identical %2d | wins %d/%d | queen rammed %d/%d, attacker not in view %d/%d, queen alive %d/%d, end length sum %d/%d | she dies later in %d, earlier in %d | p100 %d/%d d100 %d/%d' % (
        arm, t['pairs'], t['identical'], t['win'], t['Lwin'], t['ram'], t['Lram'], t['blind'], t['Lblind'], t['alive'], t['Lalive'], t['qend'], t['Lqend'], t['later'], t['earlier'], t['p100'], t['Lp100'], t['d100'], t['Ld100']))
