# Counts for the no-action deaths (run 20261007-0300), from the h3n-shard files (own extraction, h3_noact.py).
import json
from collections import Counter
from statistics import median
D = 'data/analysis/ladder/'
rows = [json.loads(l) for l in open(D + 'rows.jsonl') if l.strip()]
X = dict()
for k in range(4):
    for l in open(D + 'work/h3n-shard%d.jsonl' % k):
        g = json.loads(l)
        X[g['game']] = g
print('games', len(X), 'errors', sum(1 for g in X.values() if 'error' in g))
SPLIT = '2026-10-06T14:48:15'
def band(r):
    e = r['opponent_rating']
    return 'a' if e < 1700 else 'b' if e < 1900 else 'c' if e < 2100 else 'd'
main = [r for r in rows if r['our_code'] == 'main']
v31 = [r for r in rows if r['our_code'] == 'v31']
def show(name, g):
    na = [n for r in g for n in X[r['game']]['noact']]
    if not na:
        print(name, 'no deaths'); return
    tot = sum(r['deaths'][w]['us']['other'] for r in g for w in r['deaths'])
    bad_drop = sum(1 for n in na if n[6] != (n[1] + 1) // 2)
    n8 = sum(1 for n in na if n[2] is not None and n[2] <= 8)
    n3 = sum(1 for n in na if n[2] is not None and n[2] <= 3)
    nobig = sum(1 for n in na if n[2] is None)
    dr = sum(n[6] for n in na); eu = sum(n[7] for n in na); et = sum(n[8] for n in na); eb = sum(n[9] for n in na)
    ln = sum(n[1] for n in na)
    print(name, 'games', len(g), 'deaths', len(na), '(rows say', tot, ') per game', round(len(na) / len(g), 1), '| drop count differs from ceil(L/2) in', bad_drop,
          '| near an own dragon 2x as long: within 3', round(n3 / len(na), 3), 'within 8', round(n8 / len(na), 3), 'no such dragon alive', round(nobig / len(na), 3),
          '| length given up', ln, 'pearls dropped', dr, 'eaten within 15 by us', eu, round(eu / dr, 3), 'by them', et, round(et / dr, 3), 'by an own dragon 2x as long', eb, round(eb / dr, 3))
    return na
for name, g in (('main all', main), ('main band b', [r for r in main if band(r) == 'b']), ('main band c', [r for r in main if band(r) == 'c']), ('main band d', [r for r in main if band(r) == 'd']),
                ('main half1', [r for r in main if r['time'] < SPLIT]), ('main half2', [r for r in main if r['time'] >= SPLIT]),
                ('main wins', [r for r in main if r['win']]), ('main losses', [r for r in main if not r['win']]),
                ('v31 all', v31), ('v31 band b', [r for r in v31 if band(r) == 'b']), ('v31 band c', [r for r in v31 if band(r) == 'c']), ('v31 band d', [r for r in v31 if band(r) == 'd'])):
    show(name, g)
na = [n for r in main for n in X[r['game']]['noact']]
far = [n for n in na if n[2] is None or n[2] > 8]
print('main far or no big dragon:', len(far), '| no big dragon', sum(1 for n in far if n[2] is None), '| lengths', Counter(min(n[1], 8) for n in far).most_common(8), '| rounds', sorted(Counter(n[0] // 100 * 100 for n in far).items()),
      '| drops', sum(n[6] for n in far), 'us', sum(n[7] for n in far), 'them', sum(n[8] for n in far), '| gap to nearest enemy head median', median([n[5] for n in far if n[5] is not None]),
      '| gap to our longest', Counter(min(n[4], 12) if n[4] is not None else -1 for n in far).most_common(6))
nobig = [n for n in na if n[2] is None]
print('main no own dragon 2x as long alive:', len(nobig), 'lengths', Counter(min(n[1], 12) for n in nobig).most_common(8), 'gap to our longest', Counter(min(n[4], 12) if n[4] is not None else -1 for n in nobig).most_common(6), 'drops', sum(n[6] for n in nobig), 'us', sum(n[7] for n in nobig), 'them', sum(n[8] for n in nobig))
near = [n for n in na if n[2] is not None and n[2] <= 8]
print('main near:', len(near), 'drops', sum(n[6] for n in near), 'us', sum(n[7] for n in near), 'them', sum(n[8] for n in near), 'big', sum(n[9] for n in near), '| gap', Counter(n[2] for n in near).most_common(9))
print('main: gap to nearest own 2x dragon, all', Counter(min(n[2], 13) if n[2] is not None else -1 for n in na).most_common(15))
# per game: feeding and the end
for name, g in (('main', main), ('v31', v31)):
    per = []
    for r in g:
        x = X[r['game']]['noact']
        per.append((len(x), sum(n[1] for n in x), sum(n[7] for n in x), sum(n[8] for n in x), r))
    fed = [p for p in per if p[0] >= 5]
    print(name, 'games with 5+ no-action deaths', len(fed), 'won', sum(p[4]['win'] for p in fed), '| games with none', sum(1 for p in per if p[0] == 0), 'won', sum(p[4]['win'] for p in per if p[0] == 0),
          '| median length given up in fed games', median([p[1] for p in fed]), 'median pearls got back', median([p[2] for p in fed]),
          '| games where they ate 10+ of our feeder pearls', sum(1 for p in fed if p[3] >= 10), 'won', sum(p[4]['win'] for p in fed if p[3] >= 10))
    # longest dragon endings
    ld = [p for p in fed if p[4]['ended_by'] == 'longest dragon']
    print('   fed games ending on longest dragon', len(ld), 'won', sum(p[4]['win'] for p in ld), '| median our longest', median([p[4]['final']['us']['longest'] for p in ld]) if ld else None, 'their longest', median([p[4]['final']['them']['longest'] for p in ld]) if ld else None)
    qr = [p for p in fed if p[4]['ended_by'] == 'queen rule']
    print('   fed games ending on queen rule', len(qr), 'won', sum(p[4]['win'] for p in qr), '| queens at end', Counter(p[4]['queens_at_end'] for p in qr).most_common())
    # their no-action deaths from rows
    print('   opponent no-action deaths per game (rows): median', median([sum(r['deaths_other'][w]['them']['no action'] for w in r['deaths_other']) for r in g]), '| games where they have 5+', sum(1 for r in g if sum(r['deaths_other'][w]['them']['no action'] for w in r['deaths_other']) >= 5))
