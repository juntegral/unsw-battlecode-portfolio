# Scratch (diag-feeding): when does feeding start? Reads fd_scan-*.jsonl. Prints only.
import json
from collections import Counter
from pathlib import Path

G = []
for k in range(4):
    p = Path('data/analysis/ladder/dossier/work/fd_scan-%d.jsonl' % k)
    G += [json.loads(l) for l in p.open()]
print('games', len(G), 'reach r201/301/401', sum(g['last_round'] >= 201 for g in G), sum(g['last_round'] >= 301 for g in G),
      sum(g['last_round'] >= 401 for g in G))


def strict(d):
    return d['tgt'] >= 0 and d['L'] * 2 <= d['tgt_len'] and not d['q']


bins = Counter()
for g in G:
    for d in g['feeders']:
        kind = 'queen' if d['q'] else 'feeder' if strict(d) else 'near-not2x' if d['tgt'] >= 0 else 'alone'
        bins[(kind, min(d['r'], 499) // 50 * 50)] += 1
for kind in ('feeder', 'near-not2x', 'alone', 'queen'):
    print(kind, [(r, bins[(kind, r)]) for r in range(0, 500, 50)])
exact = Counter()
for g in G:
    for d in g['feeders']:
        if strict(d) and 195 <= d['r'] <= 205 or strict(d) and 295 <= d['r'] <= 305 or strict(d) and 395 <= d['r'] <= 405:
            exact[d['r']] += 1
print('strict feeder deaths by exact round near the three thresholds', sorted(exact.items()))

tab = Counter()
rows = []
for g in G:
    if g['last_round'] < 201:
        continue
    s = g['series']
    f = sorted(d['r'] for d in g['feeders'] if strict(d) and d['r'] > 150)
    first = f[0] if f else None
    cap = g['cap_rounds'][0] if g['cap_rounds'] else None
    q300 = len(s) > 301 and s[301][3] > 0
    q400 = len(s) > 401 and s[401][3] > 0
    cls = 'none' if first is None else '<=200' if first <= 200 else '201-300' if first <= 300 else '301-400' if first <= 400 else '401+'
    capc = 'nocap' if cap is None else 'cap<=300' if cap <= 300 else 'cap301-400'
    reach = 'end<301' if g['last_round'] < 301 else 'end<401' if g['last_round'] < 401 else 'full'
    tab[(reach, capc, 'Q300' if q300 else 'q-', cls)] += 1
    rows.append((g['game'], first, cap, q300, q400, g['last_round']))
for k in sorted(tab):
    print(k, tab[k])
# feeder deaths in 301-400 without the cap rule: was our count ever 56 that round?
odd = Counter()
for g in G:
    caps = set(g['cap_rounds'])
    s = g['series']
    for d in g['feeders']:
        if strict(d) and 200 < d['r'] <= 400:
            q = s[d['r']][3] > 0
            odd[('cap-round' if d['r'] in caps else 'not-cap', 'r201-300' if d['r'] <= 300 else 'r301-400', 'queen alive' if q else 'queen dead',
                 'target is queen' if d['tgt_q'] else 'target other')] += 1
for k in sorted(odd):
    print(k, odd[k])
late = Counter()
for g in G:
    s = g['series']
    for d in g['feeders']:
        if strict(d) and d['r'] > 400:
            q = s[d['r']][3] > 0
            late[('queen alive' if q else 'queen dead', 'target is queen' if d['tgt_q'] else 'target other', 'top' if d['tgt_top'] else 'not top')] += 1
print(sorted(late.items()))
