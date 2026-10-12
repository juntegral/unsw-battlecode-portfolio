"""watch17-opus: per-set queen death reasons, wipes, and same-map rows across versions. Usage (from ROOT): python3 -B .../cmp.py [opp tag c1|s1|p1]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path
sys.dont_write_bytecode = True
C = json.loads(Path('data/codex/astra/watch17-opus/cache.json').read_text())
G = [g for g in C.values() if g.get('ver')]
RS = {0: 'wall', 1: 'own', 2: 'body', 3: 'headon', 4: 'other'}
by = defaultdict(list)
for g in G:
    by[(g['ver'], g['set'])].append(g)
print('set                 n win | queen deaths by reason                       | q death len>=10 | wiped(us) wiped(them) | med q death round | q split-by-2 from 10+ after r50')
for key in sorted(by):
    gs = by[key]
    qr = Counter(RS.get(g['qdead'][2]) for g in gs if g['qdead'])
    rr = sorted(g['qdead'][0] for g in gs if g['qdead'])
    print('%-8s %-9s %3d %3d | %-44s | %15d | %9d %11d | %17s | %d' % (
        key[0], key[1], len(gs), sum(1 for g in gs if g['win']), dict(qr), sum(1 for g in gs if g['qdead'] and g['qdead'][1] >= 10),
        sum(1 for g in gs if g['alive'][0] == 0), sum(1 for g in gs if g['alive'][1] == 0), rr[len(rr) // 2] if rr else '-',
        sum(1 for g in gs for s in g['qsplits'] if s['before'] >= 10 and s['before'] - s['after'] == 2 and s['r'] > 50)))
for tag in sys.argv[1:]:
    print()
    print('## same map, opponent set %s: result / queen (dNNN = died round NNN at len, aNN = alive len) / last round' % tag)
    rows = defaultdict(dict)
    for g in G:
        if g['set'].endswith('-' + tag):
            rows[g['map']][g['ver']] = g
    for m in sorted(rows):
        cells = []
        for v in ('one15', 'one16', 'one17'):
            g = rows[m].get(v)
            if not g:
                cells.append('%-28s' % '-')
                continue
            q = 'd%d@%d' % (g['qdead'][0], g['qdead'][1]) if g['qdead'] else 'a%d' % g['qfin']
            cells.append('%-28s' % ('%s %s eq%s r%d %s' % ('W' if g['win'] else 'L', q, g['eqfin'] or 'dead', g['last'], 'wipe' if 0 in g['alive'] else '')))
        print('%-16s %s' % (m[:16], ' | '.join(cells)))
