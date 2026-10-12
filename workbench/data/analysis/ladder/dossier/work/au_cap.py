"""Scratch (diag-australia): the even-trade rule inside big layouts. Our code rams an equal head only at the
dragon cap (59+ of ours alive). Split 25-round bins of r100-299 by our count and compare. Reads au_ev-*.jsonl."""
import sys, json
from collections import defaultdict, Counter
from pathlib import Path

D = Path('data/analysis/ladder/dossier/work')
games = []
for n in range(4):
    with open(D / ('au_ev-%d.jsonl' % n)) as f:
        for line in f:
            games.append(json.loads(line))
BIG = [g for g in games if g['w'] * g['h'] > 1200]
print('big-layout games', len(BIG), Counter(g['layout'] for g in BIG))


def cls(a):
    return '59+' if a >= 59 else '50-58' if a >= 50 else '35-49' if a >= 35 else '<35'


def table(gs, title):
    acc = defaultdict(lambda: defaultdict(float))
    for g in gs:
        s = {x[0]: x for x in g['snaps']}
        evs = defaultdict(list)
        for e in g['hos']:
            if e['cross']:
                evs[e['r'] // 25].append(e)
        for b in range(4, 12):
            if b * 25 not in s or (b + 1) * 25 not in s:
                continue
            k = cls(min(s[b * 25][1][0], s[(b + 1) * 25][1][0]))
            a = acc[k]
            a['bins'] += 1
            a['games_' + str(g['game'])] = 1
            bu, bt = g['bins']['u'][b], g['bins']['t'][b]
            a['opp_u'] += bu['opp'][0]; a['took_u'] += bu['took'][0]
            a['opp_t'] += bt['opp'][0]; a['took_t'] += bt['took'][0]
            for e in evs[b]:
                if e['ms'] == 't':
                    a['they'] += 1
                    a['net_u'] += e['eat']['u'] - e['Lv']; a['net_t'] += e['eat']['t'] - e['Lm']
                else:
                    a['we'] += 1
                    a['net_u'] += e['eat']['u'] - e['Lm']; a['net_t'] += e['eat']['t'] - e['Lv']
                    a['we_vlen'] += e['Lv']; a['we_even'] += int(e['Lv'] < max(5, e['Lm'] + 2))
            a['nat_u'] += bu['en']; a['nat_t'] += bt['en']
            a['alive_t'] += s[b * 25][2][0]
    print('==', title)
    print('our dragons | 25-round bins (games) | they ram / we ram per bin | our share of rams | our adjacent chances per bin, taken | theirs, taken | net length from all meetings per bin: us / them | our rams on targets under the size rule | their dragons')
    for k in ('59+', '50-58', '35-49', '<35'):
        a = acc[k]
        n = a['bins']
        if not n:
            continue
        ng = sum(1 for z in a if z.startswith('games_'))
        print('%5s | %d (%d) | %.2f / %.2f | %.2f | %.2f, %.2f | %.2f, %.2f | %.1f / %.1f | %.2f | %.0f' % (
            k, n, ng, a['they'] / n, a['we'] / n, a['we'] / max(1, a['we'] + a['they']),
            a['opp_u'] / n, a['took_u'] / max(1, a['opp_u']), a['opp_t'] / n, a['took_t'] / max(1, a['opp_t']),
            a['net_u'] / n, a['net_t'] / n, a['we_even'] / max(1, a['we']), a['alive_t'] / n))


table(BIG, 'all layouts above 1200 cells, r100-299')
for lay in ('Australia #1', 'Around UNSW #1', 'Slithery Fight #1', 'Islands #1', 'Schooltime #2', 'Schooltime #1'):
    table([g for g in BIG if g['layout'] == lay], lay)

# reach by mover length (their rams, big layouts, r101-300)
print('== their rams on big layouts r101-300: steps to hit by mover length')
c = defaultdict(Counter)
for g in BIG:
    for e in g['hos']:
        if e['cross'] and e['ms'] == 't' and 101 <= e['r'] <= 300:
            c[min(e['Lm'], 6)][min(e['k'], 5)] += 1
for L in sorted(c):
    print('  mover len', L, dict(sorted(c[L].items())))
print('== our victims by length and the distance before their own last move (Australia, r101-300)')
c = defaultdict(Counter)
loc = Counter()
for g in BIG:
    if g['layout'] != 'Australia #1':
        continue
    for e in g['hos']:
        if e['cross'] and e['ms'] == 't' and 101 <= e['r'] <= 300 and e['dbefore'] is not None:
            c[min(e['Lv'], 6)][min(e['dbefore'], 6)] += 1
            reach = (e['Lv'] + 3) // 4 + e['Lv'] - 2
            can = e['Lv'] <= 4 and e['dbefore'] <= min(reach, 4) and e['Lm'] >= e['Lv']
            loc['all'] += 1
            loc['could reach first, equal or longer head'] += int(can)
            loc['same and not outnumbered nearby'] += int(can and e['near_v'] >= e['near_m'] + 1)
            loc['outnumbered nearby (their other heads within 5 > ours)'] += int(e['near_m'] > e['near_v'])
for L in sorted(c):
    print('  victim len', L, dict(sorted(c[L].items())))
print(dict(loc))
