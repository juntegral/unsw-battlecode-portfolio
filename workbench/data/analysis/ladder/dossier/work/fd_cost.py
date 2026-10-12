# Scratch (diag-feeding): the cost side. Reads fd_games.jsonl and fd_scan-*.jsonl. Prints only.
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median

R = [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_games.jsonl').open()]
BY = dict((r['game'], r) for r in R)
G = []
for k in range(4):
    G += [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_scan-%d.jsonl' % k).open()]
G = [g for g in G if g['game'] in BY]


def wl(rs):
    return '%d-%d' % (sum(r['result'] == 'win' for r in rs), sum(r['result'] == 'loss' for r in rs))


print('== 1. leader head-on deaths after S (our longest at the time, 8+) ==')
ho = [(r, d) for r in R for d in r['lead_deaths'] if d['cause'] == 'headon' and d['o_side'] == 't' and d['top']]
print('n', len(ho), 'our leader was the mover', sum(d['mover'] for r, d in ho), 'was hit', sum(1 - d['mover'] for r, d in ho))
print('  rammer length', sorted(Counter(min(d['o_len'], 10) for r, d in ho if not d['mover']).items()))
print('  leader length when hit: median', median(d['L'] for r, d in ho if not d['mover']), 'ratio leader/rammer median',
      median(d['L'] / d['o_len'] for r, d in ho if not d['mover']))
print('  round', sorted(Counter(d['r'] // 50 * 50 for r, d in ho).items()))
print('  ours left after it', sorted(Counter(min(d['n_left'] // 10 * 10, 50) for r, d in ho).items()))
print('  next longest of ours / dead leader: median', median(d['rest'] / d['L'] for r, d in ho))
print('== 2. hazard of the longest dragon (15+), deaths per 100 dragon-rounds ==')
for who, ai, li, ni in (('ours', 4, 1, 0), ('theirs', 9, 6, 5)):
    expo = Counter()
    dead = Counter()
    for g in G:
        r0 = BY[g['game']]
        s = g['series']
        for r in range(201, g['last_round'] + 1):
            a = s[r]
            if a[li] >= 15:
                n = a[ni]
                ph = 'r201-300' if r <= 300 else 'r301-400' if r <= 400 else 'r401-500'
                expo[ph] += 1
                expo['n' + ('<=5' if n <= 5 else '6-15' if n <= 15 else '16-35' if n <= 35 else '36+')] += 1
                expo['all'] += 1
        ds = (g['our_deaths'] + [d for d in g['feeders']]) if who == 'ours' else g['their_big']
        for d in ds:
            if d['r'] > 200 and d['top'] and d['L'] >= 15:
                n = d['n_side'] + 1
                ph = 'r201-300' if d['r'] <= 300 else 'r301-400' if d['r'] <= 400 else 'r401-500'
                dead[ph] += 1
                dead['n' + ('<=5' if n <= 5 else '6-15' if n <= 15 else '16-35' if n <= 35 else '36+')] += 1
                dead['all'] += 1
                dead['cause ' + d['cause'] + ' ' + str(d.get('o_side'))] += 1
    print(who, [(k, dead[k], expo[k], '%.2f' % (100.0 * dead[k] / expo[k])) for k in ('all', 'r201-300', 'r301-400', 'r401-500', 'n<=5', 'n6-15', 'n16-35', 'n36+') if expo[k]])
    print('   causes', sorted((k, v) for k, v in dead.items() if k.startswith('cause')))
print('== 3. games lost on longest dragon / total: did we ever hold a longer one than their final? ==')
ll = [r for r in R if r['result'] == 'loss' and r['ended_by'] in ('longest dragon', 'total length')]
had = [r for r in ll if r['peak'] > r['Te'][1]]
print('lost on longest/total', len(ll), 'our peak after S above their final longest', len(had), 'never', len(ll) - len(had))
print('  had: leader death present', sum(1 for r in had if r['lead_deaths']), 'kind', Counter(r['kind'] for r in had), 'last big death round',
      sorted(max([d['r'] for d in r['lead_deaths']], default=0) for r in had))
print('  never: our longest at S vs theirs at S ahead', sum(r['U'][1] > r['T'][1] for r in ll if r['peak'] <= r['Te'][1]), 'median our end', median(r['Ue'][1] for r in ll if r['peak'] <= r['Te'][1]),
      'their end', median(r['Te'][1] for r in ll if r['peak'] <= r['Te'][1]), 'our dragons at S', median(r['U'][0] for r in ll if r['peak'] <= r['Te'][1]),
      'theirs', median(r['T'][0] for r in ll if r['peak'] <= r['Te'][1]))
for r in sorted(had, key=lambda r: r['game']):
    print('    ', r['game'], r['layout'], r['rating'], r['kind'], 'S', r['S'], 'U', r['U'], 'T', r['T'], 'endU', r['Ue'], 'endT', r['Te'], 'peak', r['peak'], r['peak_r'], 'feed', r['n_feed'],
          [(d['r'], d['L'], d['cause'][:2], d['o_len'], d['mover'], d['n_left']) for d in r['lead_deaths']][-3:])
print('== 4. wiped after S and elimination ==')
for r in sorted([r for r in R if r['Ue'][0] == 0], key=lambda r: r['game']):
    print('    ', r['game'], r['layout'], r['rating'], r['kind'], 'S', r['S'], 'last', r['last'], 'U', r['U'], 'T', r['T'], 'endT', r['Te'], 'feed', r['n_feed'], r['feed_L'], 'peak', r['peak'], r['peak_r'],
          'deaths', r['dc'], [(d['r'], d['L'], d['cause'][:2], d['o_len'], d['mover'], d['n_left']) for d in r['lead_deaths']][-3:])
print('== 5. the last 100 rounds: position at r401 for every game that reaches it ==')
late = [r for r in R if r['last'] >= 401 and '401' in r['mid']]
tab = Counter()
for r in late:
    a = r['mid']['401']
    U, T = a[:4], a[4:]
    if U[3] != T[3]:
        pos = 'queen ' + ('us' if U[3] > T[3] else 'them')
    else:
        q = U[1] / T[1] if T[1] else 99
        pos = 'longest ' + ('us x2+' if q >= 2 else 'us x1.25-2' if q >= 1.25 else 'us <1.25' if q > 1 else 'level' if q == 1 else 'them <1.25' if q > 0.8 else 'them x1.25-2' if q > 0.5 else 'them x2+')
    tab[(pos, r['result'], r['ended_by'])] += 1
    tab[(pos, 'n')] += 1
    tab[(pos, r['result'])] += 1
for pos in ('queen us', 'queen them', 'longest us x2+', 'longest us x1.25-2', 'longest us <1.25', 'longest level', 'longest them <1.25', 'longest them x1.25-2', 'longest them x2+'):
    print('  ', pos, tab[(pos, 'n')], 'W-L %d-%d' % (tab[(pos, 'win')], tab[(pos, 'loss')]), sorted((k[1:], v) for k, v in tab.items() if k[0] == pos and len(k) == 3))
# games ahead on longest by 1.25+ at 401 with queens level: what feeding after 401 did
ah = []
for r in late:
    a = r['mid']['401']
    U, T = a[:4], a[4:]
    if U[3] == T[3] and T[1] and U[1] >= 1.25 * T[1]:
        ah.append((r, U, T))
print('  ahead x1.25+ on longest at r401, queens level:', len(ah), 'W-L', wl([x[0] for x in ah]))
print('     our r401 longest already above their FINAL longest', sum(U[1] > r['Te'][1] for r, U, T in ah), 'W-L', wl([r for r, U, T in ah if U[1] > r['Te'][1]]),
      '| not above', sum(U[1] <= r['Te'][1] for r, U, T in ah), 'W-L', wl([r for r, U, T in ah if U[1] <= r['Te'][1]]))
for r, U, T in ah:
    if r['result'] == 'loss':
        print('     lost', r['game'], r['layout'], r['rating'], 'r401 U', U, 'T', T, 'endU', r['Ue'], 'endT', r['Te'], r['ended_by'], 'feed', r['n_feed'], 'peak', r['peak'], r['peak_r'],
              [(d['r'], d['L'], d['cause'][:2], d['o_len'], d['mover'], d['n_left']) for d in r['lead_deaths'] if d['r'] > 400])
