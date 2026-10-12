"""qexit-opus: local on/off table. Usage (repo root): python3 -B data/codex/astra/qexit-opus/cmp.py <off arm> <on arm>"""
import sys, re, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
from pathlib import Path
from o1_scan import scan
import qdeath
RUNS = Path.home() / 'meow-redteam/solo/runs'


def game(arm, folder):
    m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
    k = int(m[3])
    j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
    g = scan(arm, folder / 'game.replay', j)
    q = qdeath.scan(folder / 'game.replay', k)

    def sn(r):
        r = min(r, g['last'])
        return g['snaps'].get(str(r), g['snaps'][str(g['last'])])
    row = dict(res=g['result'], how=g['how'], last=g['last'],
               q100=sn(100)[0][3], q200=sn(200)[0][3], qend=g['ends'][0][3], oqend=g['ends'][1][3],
               p100=sum(1 for e in g['eats'] if e[1] == 0 and e[0] <= 100), d100=sn(100)[0][0], t100=sn(100)[0][1],
               qd=q['deaths'])
    row['fires'] = q['stats'][2]
    row['c1'] = q['stats'][1]
    root = qdeath.replay.load(folder / 'game.replay').root()
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
            seq.append((rnd, actor, dirs))
    row['seq'] = seq
    row['queen'] = k if True else 0
    return row


def firstdiff(a, b):
    for x, y in zip(a['seq'], b['seq']):
        if x != y:
            return 'first different action r%d dragon %d: off %s on %s' % (x[0], x[1], x[2], y[2]) if x[:2] == y[:2] else 'order differs at r%d' % x[0]
    return 'identical games' if len(a['seq']) == len(b['seq']) else 'same until one ends'


def cls(d):
    f1 = d.get('f1')
    one = f1 is not None and f1 <= 1 and not d.get('split1')
    who = 'own move' if d['own_turn'] else 'rammed'
    return 'r%d L%d %s%s' % (d['r'], d['L'], who, ' ONE-WAY' if one else '')


off, on = sys.argv[1], sys.argv[2]
names = sorted(f.name for f in (RUNS / off).glob('*-seed*-side*') if f.is_dir() and (f / 'result.txt').exists() and (RUNS / on / f.name / 'result.txt').exists())
tot = {a: dict(n=0, win=0, qalive=0, qend=0, q100=0, q200=0, p100=0, d100=0, oneway=0, qdeaths=0, fires=0) for a in (off, on)}
print('%-34s | %-44s | %-44s' % ('map-seed-side', 'OFF res q100/200/end pearls100 dragons100', 'ON  res q100/200/end pearls100 dragons100 fires'))
for n in names:
    cells = []
    notes = []
    pair = []
    for a in (off, on):
        r = game(a, RUNS / a / n)
        pair.append(r)
        t = tot[a]
        t['n'] += 1
        t['win'] += r['res'] == 'win'
        t['qalive'] += r['qend'] > 0
        t['qend'] += r['qend']
        t['q100'] += r['q100']
        t['q200'] += r['q200']
        t['p100'] += r['p100']
        t['d100'] += r['d100']
        t['qdeaths'] += len(r['qd'])
        t['oneway'] += sum(1 for d in r['qd'] if 'ONE-WAY' in cls(d))
        t['fires'] += max(0, r['fires'])
        cells.append('%-5s %2d/%2d/%2d  p %3d  d %2d %s' % (r['res'], r['q100'], r['q200'], r['qend'], r['p100'], r['d100'], ('f %d' % r['fires']) if a == on else ''))
        notes.append(';'.join(cls(d) for d in r['qd']) or 'queen lives')
    print('%-34s | %-44s | %-44s' % (n[:34], cells[0], cells[1]))
    print('%-34s   off: %s | on: %s' % ('', notes[0], notes[1]))
    print('%-34s   %s; cond2 steps (true board) off %d on %d' % ('', firstdiff(pair[0], pair[1]), pair[0]['fires'], pair[1]['fires']))
for a in (off, on):
    t = tot[a]
    print(a, json.dumps(t))
