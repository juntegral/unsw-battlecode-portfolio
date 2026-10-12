"""Scratch (diag-one1): paired table one3 against one2 on the same map and side. Usage: o1_localtab.py"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_local import rows, measures, snap
PAIRS = (('m9f3_vh', 'm8o2_vh'), ('m9f3_vb', 'm8o2_vb'))
keys = ['first', 'feeders201_300', 'nat151_200', 'nat201_300', 'nat301_350', 'T200', 'T300', 'T350', 'Tend', 'L300', 'L400', 'Lend', 'oLend', 'n5_9_r300', 'n10_r300', 'ram5_201_350', 'ramnet5_201_350', 'stopL201_350', 'stopnet201_350', 'ramsOn', 'ramsBy', 'uend', 'q']
tot = {a: {k: 0 for k in keys} for a in ('one3', 'one2')}
n = 0
wins = [0, 0]
longer = [0, 0, 0]
for a3, a2 in PAIRS:
    g3 = {g['folder']: g for g in rows(a3)}
    g2 = {g['folder']: g for g in rows(a2)}
    for f in sorted(set(g3) & set(g2)):
        m3, m2 = measures(g3[f]), measures(g2[f])
        cap = m2['u200'] >= 56
        print('%-42s %s | one3 %s %s, one2 %s %s%s' % (f[:42], a3[-2:], g3[f]['result'], g3[f]['how'], g2[f]['result'], g2[f]['how'], '' if cap else '  (not capped: %d dragons at r200)' % m2['u200']))
        if not cap:
            continue
        n += 1
        wins[0] += g3[f]['result'] == 'win'
        wins[1] += g2[f]['result'] == 'win'
        longer[0 if m3['Lend'] > m2['Lend'] else 1 if m3['Lend'] < m2['Lend'] else 2] += 1
        for k in keys:
            tot['one3'][k] += m3[k]
            tot['one2'][k] += m2[k]
        print('    one3: ' + ' '.join('%s %g' % (k, m3[k]) for k in keys) + ' lead ' + str(len(m3['lead'])))
        print('    one2: ' + ' '.join('%s %g' % (k, m2[k]) for k in keys) + ' lead ' + str(len(m2['lead'])))
print()
print('capped pairs', n, 'wins one3 %d one2 %d' % tuple(wins), '| end longest: one3 longer %d, shorter %d, equal %d' % tuple(longer))
if n:
    for k in keys:
        print('%-18s one3 %8.1f   one2 %8.1f' % (k, tot['one3'][k] / n, tot['one2'][k] / n))
