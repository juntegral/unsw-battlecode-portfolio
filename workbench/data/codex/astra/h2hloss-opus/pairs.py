"""Seat-paired results per map for each arm (side0, side1 from the newer version's view). Usage: pairs.py"""
import json, re
from collections import defaultdict, Counter
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
arms = ['h2h_mDone11_v8', 'h2h_mDone10_v8', 'h2h_mDone8_v5', 'h2h_mDone11_v5']
tab = defaultdict(dict)
tot = defaultdict(Counter)
for arm in arms:
    f = HERE / ('scan-%s.jsonl' % arm)
    if not f.exists():
        continue
    for l in f.read_text().splitlines():
        g = json.loads(l)
        m = re.fullmatch(r'gx_(.+)_\d+-seed1-side(\d)', g['folder'])
        r = {'win': 'W', 'loss': 'L', 'draw': 'D'}[g['result']] + {'elim': 'e', 'queen': 'q', 'longest': 'l', 'total': 't'}[g['how']]
        tab[m[1]].setdefault(arm, ['--', '--'])[int(m[2])] = r
        fam, size = m[1].split('_')
        tot[arm][(fam, r[0])] += 1
        tot[arm][(size, r[0])] += 1
        tot[arm][('side%s' % m[2], r[0])] += 1
        tot[arm][('all', r[0])] += 1
        tot[arm][('how ' + r, '')] += 1
print('%-18s' % 'map' + ''.join('%-18s' % a[5:] for a in arms))
for m in sorted(tab, key=lambda x: (x.split('_')[1], x)):
    print('%-18s' % m + ''.join('%-18s' % ' '.join(tab[m].get(a, ['--', '--'])) for a in arms))
for a in arms:
    print(a, 'W-L by key:', ' | '.join('%s %d-%d' % (k, tot[a][(k, 'W')], tot[a][(k, 'L')]) for k in ['all', 'side0', 'side1', '24x12', '64x16', '24x64', '64x64', 'open', 'rooms', 'corridors', 'islands', 'ring', 'rotation', 'poor', 'rich']))
    print('   decided:', {k[0]: v for k, v in tot[a].items() if k[0].startswith('how')})
    both = Counter()
    for m in tab:
        r = tab[m].get(a)
        if r and '--' not in r:
            both[r[0][0] + r[1][0]] += 1
    print('   seat pairs (side0 side1):', dict(both))
