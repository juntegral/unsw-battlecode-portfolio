"""Tables from turns-<arm>.jsonl: eat rates and declined pearls, new vs old, by role/phase/map class.
Usage: python3 -B data/codex/astra/h2hloss-opus/rates.py <arm> [small|big|all] [family]"""
import sys, json
from collections import defaultdict
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
arm = sys.argv[1]
cls = sys.argv[2] if len(sys.argv) > 2 else 'all'
fam = sys.argv[3] if len(sys.argv) > 3 else ''
gs = [json.loads(l) for l in (HERE / ('turns-%s.jsonl' % arm)).read_text().splitlines()]
gs = [g for g in gs if (cls == 'all' or (cls == 'small') == (g['W'] * g['H'] <= 300)) and fam in g['folder']]
print(arm, cls, fam, len(gs), 'games, new wins', sum(g['win'] for g in gs))
A = defaultdict(lambda: [0, 0, 0])
for g in gs:
    for k, v in g['T'].items():
        s, role, lc, ph, pd, foe = k.split('|')
        for key in ((s, role, ph, 'all', 'all'), (s, role, ph, 'p' + pd, 'all'), (s, role, ph, 'p' + pd, 'f' + foe), (s, role, ph, 'all', 'f' + foe),
                    (s, role + lc, ph, 'all', 'all'), (s, role + lc, ph, 'p' + pd, 'all'), (s, role + lc, ph, 'p1', 'f' + foe)):
            a = A[key]
            for z in range(3):
                a[z] += v[z]
def row(role, ph, pd, foe):
    out = []
    for s in '01':
        a = A[(s, role, ph, pd, foe)]
        out.append('%6d turns %5.1f%% ate' % (a[0], 100 * a[1] / a[0]) if a[0] else '     0 turns     -     ')
    return ' | '.join(out)
print('columns: NEW | old.  p1 = a pearl one free step away at turn start, p2 = two steps, p9 = none within two; f1 = enemy head in the 7x7, f2 = only enemy body, f0 = none')
for role in ('q', 'o', 'o2', 'o3', 'o4', 'o5', 'o10'):
    for ph in 'abcd':
        print('%-3s phase %s  all: %s' % (role, ph, row(role, ph, 'all', 'all')))
        for pd in ('p1', 'p2', 'p9'):
            print('      %s        %s' % (pd, row(role, ph, pd, 'all')))
        for foe in ('f0', 'f1', 'f2'):
            print('      p1 %s     %s' % (foe, row(role, ph, 'p1', foe)))
        if role in 'qo':
            for foe in ('f0', 'f1', 'f2'):
                print('      all %s    %s' % (foe, row(role, ph, 'all', foe)))
