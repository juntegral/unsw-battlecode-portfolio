"""late-opus tables from data.json. Usage: python3 -B data/codex/astra/late-opus/tab.py"""
import sys, json, os
sys.dont_write_bytecode = True
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from collections import Counter, defaultdict

D = json.load(open('data.json'))
G = D['games']
print('games', len(G), 'skip', D['skip'])
print('by version', sorted(Counter(g['ver'] for g in G).items()))
print('by src', sorted(Counter(('ranked' if g['src'] == 'ranked' else 'unranked') for g in G).items()))
print('wins', sum(g['win'] for g in G), 'winner values', Counter(g['winner'] for g in G))
print('last round', sorted(Counter(g['last'] for g in G).items())[-4:])


def lb(L):
    return '4-5' if L <= 5 else '6-9' if L <= 9 else '10-19' if L <= 19 else '20+'


def rb(r):
    return '0-99' if r < 100 else '100-299' if r < 300 else '300+'


def at(g, arr, r):
    i = r - (g['last'] - len(arr) + 1)
    return arr[i] if 0 <= i < len(arr) else None


def ws(t):
    return t['sp'] == 1 and t.get('mv') == 0 and t.get('La') == t['L'] - 2


# split kinds of our queen
kinds = Counter()
for g in G:
    for t in g['turns']:
        if t['sp']:
            kinds[('moved' if t.get('mv') else 'stood'), ('drop2' if t.get('La') == t['L'] - 2 else 'to2' if t.get('La') == 2 else 'other'),
                  ('parent' if t.get('qpar') else 'child')] += 1
print('\nqueen split turns by kind', sorted(kinds.items()))

print('\n== Count A: standing wait splits (head stays, length -2 by split)')
tab = Counter()
gw = defaultdict(int)
for g in G:
    for t in g['turns']:
        if ws(t):
            tab[lb(t['L']), rb(t['r']), min(t['f'], 2)] += 1
            tab[lb(t['L']), 'all', 'all'] += 1
            tab['all', rb(t['r']), 'all'] += 1
            tab['all', 'all', min(t['f'], 2)] += 1
            tab[lb(t['L']), 'all', min(t['f'], 2)] += 1
            tab[lb(t['L']), rb(t['r']), 'all'] += 1
            tab['all', 'all', 'all'] += 1
            gw[g['id']] += 1
print('turns', tab['all', 'all', 'all'], 'in games', len(gw), 'of', len(G))
print('per game count distribution', sorted(Counter(gw.values()).items()))
print('length band x round band')
print('%-6s %6s %8s %6s %6s' % ('L', '0-99', '100-299', '300+', 'all'))
for L in ('4-5', '6-9', '10-19', '20+', 'all'):
    print('%-6s %6d %8d %6d %6d' % (L, tab[L, '0-99', 'all'], tab[L, '100-299', 'all'], tab[L, '300+', 'all'], tab[L, 'all', 'all']))
print('length band x free cells beside head')
print('%-6s %6s %6s %6s' % ('L', 'f0', 'f1', 'f2+'))
for L in ('4-5', '6-9', '10-19', '20+', 'all'):
    print('%-6s %6d %6d %6d' % (L, tab[L, 'all', 0], tab[L, 'all', 1], tab[L, 'all', 2]))
print('by version (turns / games with any / games)')
for v in sorted({g['ver'] for g in G}):
    gs = [g for g in G if g['ver'] == v]
    print(' ', v, sum(gw.get(g['id'], 0) for g in gs), sum(1 for g in gs if g['id'] in gw), len(gs))

# runs
runs = []
for g in G:
    T = g['turns']
    i = 0
    while i < len(T):
        if ws(T[i]):
            j = i
            while j + 1 < len(T) and ws(T[j + 1]) and T[j + 1]['r'] == T[j]['r'] + 1:
                j += 1
            runs.append((g, i, j))
            i = j + 1
        else:
            i += 1
print('\nruns', len(runs), 'run length dist', sorted(Counter(j - i + 1 for g, i, j in runs).items()))
print('length lost per run dist', sorted(Counter(g['turns'][i]['L'] - g['turns'][j]['La'] for g, i, j in runs).items()))
for band in ('4-5', '6-9', '10-19', '20+'):
    rr = [(g, i, j) for g, i, j in runs if lb(g['turns'][i]['L']) == band]
    if rr:
        print('  start', band, 'runs', len(rr), 'turns', sum(j - i + 1 for g, i, j in rr), 'mean run', round(sum(j - i + 1 for g, i, j in rr) / len(rr), 2),
              'length lost total', sum(g['turns'][i]['L'] - g['turns'][j]['La'] for g, i, j in rr),
              'mean lost', round(sum(g['turns'][i]['L'] - g['turns'][j]['La'] for g, i, j in rr) / len(rr), 1))

print('\nruns starting at 10+ (each)')
print('%-8s %-5s %-9s %4s %3s %4s %4s %2s %4s %5s %5s %5s %4s %4s %3s' % ('game', 'ver', 'src', 'r0', 'n', 'L0', 'L1', 'f', 'eq', 'lead', 'd<=5', 'd<=20', 'dthR', 'qfin', 'win'))
opening = [(g, i, j) for g, i, j in runs if g['turns'][i]['L'] >= 10 and g['turns'][i]['r'] < 100]
print('opening runs from 10+ (r<100):', len(opening), 'games', len({g['id'] for g, i, j in opening}), 'turns', sum(j - i + 1 for g, i, j in opening),
      'run length dist', sorted(Counter(j - i + 1 for g, i, j in opening).items()), 'start round dist', sorted(Counter(g['turns'][i]['r'] for g, i, j in opening).items())[:6])
big = [(g, i, j) for g, i, j in runs if g['turns'][i]['L'] >= 10 and g['turns'][i]['r'] >= 100]
print('late runs from 10+ (r100+):', len(big), 'turns', sum(j - i + 1 for g, i, j in big), 'multi-turn runs', sum(1 for g, i, j in big if j > i),
      'lost in multi', sum(g['turns'][i]['L'] - g['turns'][j]['La'] for g, i, j in big if j > i),
      'free cells at start dist', sorted(Counter(min(g['turns'][i]['f'], 2) for g, i, j in big).items()),
      'nearest visible foe head gap at start', sorted(Counter(('none' if g['turns'][i]['ng'] < 0 else '<=3' if g['turns'][i]['ng'] <= 3 else '4-6' if g['turns'][i]['ng'] <= 6 else '7+') for g, i, j in big).items()))
agg = Counter()
games_big = set()
for g, i, j in big:
    T = g['turns']
    t0, t1 = T[i], T[j]
    dr = min((d['r'] for d in g['deaths'] if d['r'] >= t1['r']), default=None)
    lead = int(t0['L'] > t0['eq'])
    d5 = int(dr is not None and dr - t1['r'] <= 5)
    d20 = int(dr is not None and dr - t1['r'] <= 20)
    alive = int(g['qfin'] > 0)
    games_big.add(g['id'])
    agg['n'] += 1
    agg['lead'] += lead
    agg['d5'] += d5
    agg['d20'] += d20
    agg['alive'] += alive
    agg['win'] += g['win']
    agg['lost_len'] += t0['L'] - t1['La']
    agg['lead_win'] += lead and g['win']
    agg['lead_d20'] += lead and d20
    agg['lead_alive'] += lead and alive
    agg['lead_end'] += int(lead and t1['La'] > t0['eq'])
    agg['late'] += int(t0['r'] >= 300)
    agg['late_d20'] += int(t0['r'] >= 300 and d20)
    agg['late_win'] += int(t0['r'] >= 300 and g['win'])
    agg['f2'] += int(t0['f'] >= 2)
    print('%-8d %-5s %-9s %4d %3d %4d %4d %2d %4d %5d %5d %5d %4s %4d %3d' % (g['id'], g['ver'], g['src'][:9], t0['r'], j - i + 1, t0['L'], t1['La'], t0['f'], t0['eq'],
                                                                         lead, d5, d20, dr if dr is not None else '-', g['qfin'], g['win']))
print('totals', dict(agg), 'distinct games', len(games_big))
gb = [g for g in G if g['id'] in games_big]
print('games with a 10+ run: n', len(gb), 'wins', sum(g['win'] for g in gb), 'queen alive at end', sum(1 for g in gb if g['qfin'] > 0),
      'mean qfin', round(sum(g['qfin'] for g in gb) / max(1, len(gb)), 1))

def mx300(g):
    i0 = 300 - (g['last'] - len(g['ql']) + 1)
    return max(g['ql'][max(0, i0):], default=0) if i0 < len(g['ql']) else 0


def lead300(g):
    i0 = max(0, 300 - (g['last'] - len(g['ql']) + 1))
    return any(q >= 10 and q > e for q, e in zip(g['ql'][i0:], g['el'][i0:]))


print('\ncomparison (queen 10+ at some round start from 300 on): queen 10+ at round 300, by whether the game has a 10+ run at round 300+')
late_big = {g['id'] for g, i, j in big if g['turns'][i]['r'] >= 300}
for name, sel in (('no 10+ run at all', lambda g: g['id'] not in games_big), ('10+ run only before r300', lambda g: g['id'] in games_big and g['id'] not in late_big),
                  ('10+ run at r300+', lambda g: g['id'] in late_big)):
    gs = [g for g in G if sel(g) and mx300(g) >= 10]
    if gs:
        print('  %-26s n %3d alive at end %3d (%.0f%%) wins %3d (%.0f%%) mean qfin %.1f mean max ql r300+ %.1f' % (
            name, len(gs), sum(1 for g in gs if g['qfin'] > 0), 100 * sum(1 for g in gs if g['qfin'] > 0) / len(gs), sum(g['win'] for g in gs),
            100 * sum(g['win'] for g in gs) / len(gs), sum(g['qfin'] for g in gs) / len(gs), sum(mx300(g) for g in gs) / len(gs)))
print('same, restricted to queen 10+ and leading at round 300')
for name, sel in (('no 10+ run at r300+', lambda g: g['id'] not in late_big), ('10+ run at r300+', lambda g: g['id'] in late_big)):
    gs = [g for g in G if sel(g) and mx300(g) >= 10 and lead300(g)]
    if gs:
        print('  %-26s n %3d alive at end %3d wins %3d mean qfin %.1f' % (name, len(gs), sum(1 for g in gs if g['qfin'] > 0), sum(g['win'] for g in gs), sum(g['qfin'] for g in gs) / len(gs)))

print('\n== Count B: our queen deaths at round 350+')
print('%-8s %-5s %-9s %4s %3s %3s %4s %-10s %-22s %-9s %2s %2s %3s' % ('game', 'ver', 'src', 'r', 'L', 'eq', 'lead', 'cause', 'detail', 'last3', 'm5', 'nm', 'win'))
cb = Counter()
for g in G:
    for d in g['deaths']:
        if d['r'] < 350:
            continue
        lead = int(d['L'] > d['eq'])
        if d['cause'] == 'own':
            det = 'hit ' + ' '.join(str(x) for x in d.get('hit', ['?'])[:4]) + (' Q' if d.get('hit', [0, 0, 0, 0, 0])[-1] == 1 and len(d.get('hit', [])) == 5 else '')
        elif d['cause'].startswith('ram'):
            det = 'attL %d steps %d qview %d%s' % (d['attL'], d['att_steps'], d['qview'], ' Q' if d['att_is_q'] else '')
        else:
            det = 'reason %d' % d['reason']
        l3 = ''.join({1: 'T', -1: 'A', 0: '=', None: '.'}[t.get('tw')] if t['ng'] >= 0 else '.' for t in d['last3'])
        tw = sum(1 for t in d['last3'] if t.get('tw') == 1)
        aw = sum(1 for t in d['last3'] if t.get('tw') == -1)
        trend = 'toward' if tw > aw else 'away' if aw > tw else 'level' if any(t['ng'] >= 0 for t in d['last3']) else 'nofoe'
        cb['n'] += 1
        cb['cause', d['cause']] += 1
        cb['lead', lead] += 1
        cb['lead_cause', lead, d['cause']] += 1
        cb['trend', trend] += 1
        cb['lead_trend', lead, trend] += 1
        cb['m5', min(d['mates5'], 2)] += 1
        cb['win', g['win']] += 1
        cb['lead_win', lead, g['win']] += 1
        cb['wsplit3', int(any(t['sp'] and t.get('mv') == 0 for t in d['last3']))] += 1
        print('%-8d %-5s %-9s %4d %3d %3d %4d %-10s %-22s %-9s %2d %2d %3d' % (g['id'], g['ver'], g['src'][:9], d['r'], d['L'], d['eq'], lead, d['cause'], det[:22],
                                                                        l3 + ' ' + trend[:5], d['mates5'], d['n_mates'], g['win']))
print('totals')
for k in sorted(cb, key=str):
    print('  ', k, cb[k])

print('\n== Prize: state at round 350 against the result')
pz = Counter()
rows = []
for g in G:
    q, e = at(g, g['ql'], 350), at(g, g['el'], 350)
    if q is None:
        pz['game ended before r350'] += 1
        continue
    st = 'lead' if q > e else 'level' if q == e else 'behind'
    if q == 0:
        st = 'our queen dead' if e > 0 else 'both dead'
    pz[st, 'games'] += 1
    pz[st, 'win'] += g['win']
    if st == 'lead' and not g['win']:
        dl = [d for d in g['deaths'] if d['r'] >= 350]
        how = ('queen died r%d %s L%d' % (dl[0]['r'], dl[0]['cause'], dl[0]['L'])) if dl else ('alive, overtaken' if g['qfin'] <= g['efin'] else 'alive and longer?')
        pz['lead-loss', 'queen died' if dl else 'alive'] += 1
        if dl:
            pz['lead-loss cause', dl[0]['cause']] += 1
        rows.append((g['id'], g['ver'], g['src'], q, e, g['qfin'], g['efin'], how, g['winner'], g['last']))
for k in sorted(pz, key=str):
    print('  ', k, pz[k])
print('games lost from a queen lead at r350:')
print('%-8s %-5s %-9s %5s %5s %4s %4s  %s' % ('game', 'ver', 'src', 'q@350', 'e@350', 'qfin', 'efin', 'how'))
for r in rows:
    print('%-8d %-5s %-9s %5d %5d %4d %4d  %s (winner %s, last %d)' % r)
# same by version
print('lead at r350 by version: games / wins / losses with queen death')
for v in sorted({g['ver'] for g in G}):
    gs = [g for g in G if g['ver'] == v and (at(g, g['ql'], 350) or 0) > (at(g, g['el'], 350) or 0)]
    print('  ', v, len(gs), sum(g['win'] for g in gs), sum(1 for g in gs if not g['win'] and any(d['r'] >= 350 for d in g['deaths'])))
