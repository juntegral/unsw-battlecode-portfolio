"""stuck-opus: loop classes (dragon-rounds in the 30th+ round of a no-eat loop on <=12 cells, by what the nearest reachable pearl is).
Usage (ROOT): python3 -B data/codex/astra/stuck-opus/cls.py online|local [by=ver|map|fam|size|phase] [filter substring]"""
import sys, json, re
sys.dont_write_bytecode = True
from pathlib import Path
from collections import defaultdict
HERE = Path('data/codex/astra/stuck-opus')
CATS = ('deadend', 'free', 'mate', 'enemy', 'idle')
kind = sys.argv[1]
by = sys.argv[2] if len(sys.argv) > 2 else 'ver'
flt = sys.argv[3] if len(sys.argv) > 3 else ''
gs = []
for p in sorted(HERE.glob('rows-*.jsonl')):
    local = not p.name.startswith('rows-one')
    if local != (kind == 'local'):
        continue
    gs += [json.loads(l) for l in p.read_text().splitlines()]
gs = [g for g in gs if flt in g['key']]


def fam(g):
    m = re.match(r'gx_([a-z]+)_(\d+)x(\d+)', g['map'])
    return m[1] if m else g['map'].replace('ladder_', 'L:')


def key(g):
    if by == 'ver':
        return g['ver']
    if by == 'map':
        return '%s %s' % (g['ver'], g['map'])
    if by == 'fam':
        return '%s %s' % (g['ver'], fam(g))
    if by == 'size':
        return '%s %05d cells' % (g['ver'], g['cells'])
    if by == 'set':
        return g['set']
    return g['ver']


acc = defaultdict(lambda: dict(n=0, alive=[[0, 0, 0], [0, 0, 0]], lc=[[defaultdict(int) for _ in range(3)] for _ in range(2)]))
for g in gs:
    a = acc[key(g)]
    a['n'] += 1
    for s in (0, 1):
        for ph in range(3):
            a['alive'][s][ph] += sum(g['cnt'][s][ro][ph]['n'] for ro in range(2))
            for c, v in g['lc'][s][ph].items():
                a['lc'][s][ph][c] += v
phs = [(0, 1, 2)] if by != 'phase' else [(0,), (1,), (2,)]
print('%d games. Cells: looping dragon-rounds as %% of that side\'s alive dragon-rounds, us | them. Columns: %s, total; then our looping dragon-rounds per game' % (len(gs), ', '.join(CATS)))
for k in sorted(acc):
    a = acc[k]
    for ph in phs:
        al = [sum(a['alive'][s][p] for p in ph) for s in (0, 1)]
        line = '%-30s n=%-3d %s ' % (k[:30], a['n'], '' if len(phs) == 1 else 'phase%d' % ph[0])
        tot = [0, 0]
        for c in CATS:
            v = [sum(a['lc'][s][p][c] for p in ph) for s in (0, 1)]
            tot[0] += v[0]
            tot[1] += v[1]
            line += ' %4.1f|%4.1f' % (100 * v[0] / max(al[0], 1), 100 * v[1] / max(al[1], 1))
        line += '  tot %4.1f|%4.1f  %6.0f/game' % (100 * tot[0] / max(al[0], 1), 100 * tot[1] / max(al[1], 1), tot[0] / a['n'])
        print(line)
if by == 'ex':
    for g in gs:
        for e in g['lex']:
            print(g['key'], g['map'], e)
