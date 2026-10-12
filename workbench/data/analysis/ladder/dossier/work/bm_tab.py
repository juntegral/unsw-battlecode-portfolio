"""Scratch (diag-bigmap): prints the report's table 1 (one markdown row per arm and opponent, a game per line break)
and the recount of the headline cells straight from the scan rows.
Usage: python3 data/analysis/ladder/dossier/work/bm_tab.py [t1|check]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from statistics import median

WORK = Path('data/analysis/ladder/dossier/work')
CP = (50, 100, 150, 200, 300, 400, 499)
SHORT = {'Australia': 'Au', 'Islands': 'Is', 'Around UNSW': 'UN', 'Schooltime': 'Sc', 'Slithery Fight': 'SF'}


def load():
    rows = []
    for p in sorted(WORK.glob('bm_scan-O[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            if g['cells'] > 1200:
                rows.append(g)
    rows.sort(key=lambda g: g['gid'])
    return rows


def at(g, r):
    return g['snap'][min(r, g['last'])]


def decider(g):
    f = g['final']
    if f[0] == 0 or f[4] == 0:
        return 'E'
    if f[3] != f[7]:
        return 'Q'
    if f[2] != f[6]:
        return 'L'
    return 'T'


def passed(g):
    q = decider(g)
    w = 0 if g['result'] == 'win' else 4
    l = 4 - w
    idx = dict(Q=3, L=2, T=1, E=2)[q]
    r = g['last']
    while r >= 0 and g['snap'][r][w + idx] > g['snap'][r][l + idx]:
        r -= 1
    return r + 1


def t1(rows):
    for arm in ('MAIN', 'B7', 'B7Q'):
        for opp in ('Big Bobs Bots', 'WeHaveQuizzes'):
            gs = [g for g in rows if g['arm'] == arm and g['opp'] == opp]
            cells = []
            for g in gs:
                tl = ' '.join('%d/%d/%d/%d:%d/%d/%d/%d' % tuple(at(g, r)) for r in CP)
                cells.append('%d %s %s %s r%d; %s' % (g['gid'], SHORT.get(g['map'], g['map'][:2]), 'W' if g['result'] == 'win' else 'L', decider(g), passed(g), tl))
            ps = sorted(passed(g) for g in gs if g['result'] == 'loss')
            print('| %s / %s, %d of %d won; losses pass at median r%g | %s |' % (arm, opp, sum(g['result'] == 'win' for g in gs), len(gs), median(ps) if ps else 0, '<br>'.join(cells)))


def check(rows):
    for arm in ('MAIN', 'B7', 'B7Q'):
        gs = [g for g in rows if g['arm'] == arm]
        n = len(gs)
        rammed = sum(1 for g in gs for d in g['deaths'] if d['s'] == 0 and d['c'] == 'head-on' and d.get('cross') and d.get('role') == 'hit')
        ram = sum(1 for g in gs for d in g['deaths'] if d['s'] == 1 and d['c'] == 'head-on' and d.get('cross') and d.get('role') == 'hit')
        dec = [decider(g) for g in gs]
        print(arm, n, 'won', sum(g['result'] == 'win' for g in gs), 'rammed a game %.1f' % (rammed / n), 'we ram %.1f' % (ram / n), 'decided', dict((k, dec.count(k)) for k in 'QLTE'),
              'losses by Q %d L %d E %d' % (sum(1 for g in gs if g['result'] == 'loss' and decider(g) == 'Q'), sum(1 for g in gs if g['result'] == 'loss' and decider(g) == 'L'), sum(1 for g in gs if g['result'] == 'loss' and decider(g) == 'E')),
              'ours longest r300 median %g' % median(at(g, 300)[2] for g in gs), 'queen alive r150 %d ours %d theirs' % (sum(at(g, 150)[3] > 0 for g in gs), sum(at(g, 150)[7] > 0 for g in gs)),
              'queen alive end %d ours %d theirs' % (sum(g['final'][3] > 0 for g in gs), sum(g['final'][7] > 0 for g in gs)))
        ql = [g for g in gs if g['result'] == 'loss' and decider(g) == 'Q']
        print('   lost on the queen rule with our longest above theirs:', [g['gid'] for g in ql if g['final'][2] > g['final'][6]], 'and our queen dead in', sum(g['final'][3] == 0 for g in ql), 'of', len(ql))


rows = load()
if len(sys.argv) > 1 and sys.argv[1] == 'check':
    check(rows)
else:
    t1(rows)
