#!/usr/bin/env python3
"""Run from ROOT: python3 -B data/codex/astra/feed-opus/tab.py"""
import sys, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from o1_scan import scan
RUNS = Path.home() / 'meow-redteam/solo/runs'
ARMS = ['fdL', 'fd400', 'fdNo', 'fd200', 'fdR4']


def view(folder, seat):
    m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
    j = dict(id=0, teamAId=1119 if seat == 0 else 1, teamBId=1 if seat == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
    return scan('fd', folder / 'game.replay', j)


def snap(g, r):
    r = min(r, g['last'])
    return g['snaps'].get(str(r), g['snaps'][str(g['last'])])


def row(g):
    qd = [d[0] for d in g['deaths'] if d[1] == 0 and d[6] == 1]
    oqd = [d[0] for d in g['deaths'] if d[1] == 1 and d[6] == 1]
    s3, s4, e = snap(g, 300), snap(g, 400), g['ends']
    st = [d for d in g['deaths'] if d[1] == 0 and d[4] == 'stop' and d[5] > 0]
    return dict(res=g['result'], how=g['how'], last=g['last'], qalive=int(e[0][3] > 0), q300=s3[0][3], q400=s4[0][3], qend=e[0][3],
                qdied=qd[0] if qd else 0, oqend=e[1][3], oqdied=oqd[0] if oqd else 0, T300=s3[0][1], T400=s4[0][1], Tend=e[0][1], oT400=s4[1][1], oTend=e[1][1],
                L400=s4[0][2], Lend=e[0][2], p100=snap(g, 100)[0][1], u100=snap(g, 100)[0][0],
                fed200=sum(1 for d in st if 200 < d[0] <= 300), fed300=sum(1 for d in st if 300 < d[0] <= 400), fed400=sum(1 for d in st if d[0] > 400))


games = {}
for arm in ARMS:
    for opp in ('mD17', 'm3base'):
        for folder in sorted((RUNS / f'fd_{arm}_{opp}').glob('*-seed*-side*')):
            if not (folder / 'result.txt').exists():
                continue
            m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
            k = int(m[3])
            games[(arm, opp, m[1], k)] = row(view(folder, k))
            if arm == 'fdL' and opp == 'mD17':
                games[(arm, opp, m[1], 1 - k)] = row(view(folder, 1 - k))
F = '%-6s %-5s %-9s q300/400/end %2d/%2d/%2d died %3d | them q end %2d died %3d | T300/400/end %3d/%3d/%3d them %3d/%3d | longest 400/end %2d/%2d | fed r201-300/301-400/401+ %2d/%2d/%2d | len r100 %3d units %2d | last %d'
keys = sorted({(o, m, k) for (a, o, m, k) in games})
for o, m, k in keys:
    print('== vs %s  %s  seat %d' % (o, m.replace('ladder_', ''), k))
    for a in ARMS:
        r = games.get((a, o, m, k))
        if r:
            print('  ' + F % (a, r['res'], r['how'], r['q300'], r['q400'], r['qend'], r['qdied'], r['oqend'], r['oqdied'], r['T300'], r['T400'], r['Tend'], r['oT400'], r['oTend'],
                              r['L400'], r['Lend'], r['fed200'], r['fed300'], r['fed400'], r['p100'], r['u100'], r['last']))
print()
print('per arm, on the pairs where both the arm and fdL have the game')
for a in ARMS[1:]:
    n = w = lw = qa = lqa = 0
    dq = dT = dend = 0
    better = worse = same = 0
    for o, m, k in keys:
        r, l = games.get((a, o, m, k)), games.get(('fdL', o, m, k))
        if not r or not l:
            continue
        n += 1; w += r['res'] == 'win'; lw += l['res'] == 'win'; qa += r['qalive']; lqa += l['qalive']
        dq += r['qend'] - l['qend']; dT += r['T400'] - l['T400']; dend += r['Tend'] - l['Tend']
        sc = lambda x: (x['res'] == 'win') - (x['res'] == 'loss')
        better += sc(r) > sc(l); worse += sc(r) < sc(l); same += sc(r) == sc(l)
    if n:
        print('%-6s pairs %2d | wins %d (live %d) | queen alive at end %d (live %d) | mean queen end %+.1f, total r400 %+.1f, total end %+.1f vs live | result better %d worse %d same %d' % (
            a, n, w, lw, qa, lqa, dq / n, dT / n, dend / n, better, worse, same))
