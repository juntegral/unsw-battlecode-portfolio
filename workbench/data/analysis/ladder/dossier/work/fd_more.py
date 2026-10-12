# Scratch (diag-feeding): reach of the three candidate switches and a few table cells. Reads fd_games.jsonl. Prints only.
import json
from collections import Counter
from pathlib import Path
from statistics import median, mean

R = [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_games.jsonl').open()]


def wl(rs):
    return '%d-%d' % (sum(r['result'] == 'win' for r in rs), sum(r['result'] == 'loss' for r in rs))


print('layouts', len(set(r['layout'] for r in R)), 'games', len(R), wl(R))
print('== wins on longest/total by kind: needed growth after S ==')
for kind in ('cap', 'q300', 'r400'):
    w = [r for r in R if r['kind'] == kind and r['result'] == 'win' and r['ended_by'] in ('longest dragon', 'total length')]
    print(' ', kind, len(w), 'S longest < their final', sum(r['U'][1] < r['Te'][1] for r in w), 'equal', sum(r['U'][1] == r['Te'][1] for r in w),
          'need fed pearls', sum(r['U'][1] < r['Te'][1] and r['Ue'][1] - r['e_top'] <= r['Te'][1] for r in w))
late = [r for r in R if '401' in r['mid']]
w = [r for r in late if r['result'] == 'win' and r['ended_by'] in ('longest dragon', 'total length')]
print('reach r401', len(late), wl(late), '| won on longest/total', len(w), 'our r401 longest < their final', sum(r['mid']['401'][1] < r['Te'][1] for r in w),
      'equal', sum(r['mid']['401'][1] == r['Te'][1] for r in w), 'already longer', sum(r['mid']['401'][1] > r['Te'][1] for r in w))
print('== margin candidate: lost with our longest already above their final longest ==')
for tag, get in (('at S', lambda r: r['U'][1]), ('at r401', lambda r: r['mid']['401'][1] if '401' in r['mid'] else None)):
    rs = [r for r in R if get(r) is not None and get(r) > r['Te'][1]]
    ls = [r for r in rs if r['result'] == 'loss']
    print(' ', tag, 'games', len(rs), wl(rs), 'x1.5+', sum(get(r) >= 1.5 * r['Te'][1] for r in rs), wl([r for r in rs if get(r) >= 1.5 * r['Te'][1]]))
    for r in ls:
        print('     lost', r['game'], r['layout'], r['ended_by'], 'S', r['S'], 'ours then', get(r), 'end U', r['Ue'], 'T', r['Te'], 'feeders', r['n_feed'],
              [(d['r'], d['L'], d['cause'][:2], d['o_len']) for d in r['lead_deaths']][-2:])
print('== margin rule a dragon could apply: our longest >= k x their longest AT THAT MOMENT (r401), queens level ==')
for k in (1.5, 2, 3):
    rs = []
    for r in late:
        a = r['mid']['401']
        if a[3] == a[7] and a[5] > 0 and a[1] >= k * a[5]:
            rs.append(r)
    grow = [r for r in rs if r['mid']['401'][1] <= r['Te'][1]]
    print('  k', k, 'games', len(rs), wl(rs), '| their final longest reached our r401 longest in', len(grow), wl(grow),
          '| of those won only thanks to growth after r401', sum(r['result'] == 'win' and r['ended_by'] in ('longest dragon', 'total length') for r in grow))
print('== reserve candidate ==')
for lo in (10, 20):
    rs = [r for r in late if r['mid']['401'][0] >= lo and r['Ue'][0] <= 3]
    print('  ', lo, '+ dragons at r401 and 3 or fewer at the end:', len(rs), wl(rs), 'ended', sorted(Counter((r['ended_by'], r['result']) for r in rs).items()))
    for r in rs:
        if r['result'] == 'loss':
            print('      ', r['game'], r['layout'], r['ended_by'], 'r401', r['mid']['401'], 'end U', r['Ue'], 'T', r['Te'], 'feeders', r['n_feed'], 'other deaths', r['dc'])
el = [r for r in R if r['result'] == 'loss' and r['ended_by'] == 'elimination']
print('  lost by elimination after S', len(el), 'with 10+ feeders', sum(r['n_feed'] >= 10 for r in el), 'with 10+ dragons at S', sum(r['U'][0] >= 10 for r in el))
rs = [r for r in R if r['Ue'][0] <= 3]
print('  ended with 0-3 dragons', len(rs), wl(rs), 'ours at S: median', median(r['U'][0] for r in rs), '| of them with <= 10 at S', sum(r['U'][0] <= 10 for r in rs))
print('  dragons at the end, all games: median', median(r['Ue'][0] for r in R), 'theirs', median(r['Te'][0] for r in R))
print('== leader death candidate ==')
ld = [(r, d) for r in R for d in r['lead_deaths'] if d['top'] and d['L'] >= 15]
print('  deaths of our longest (15+) after S', len(ld), 'round median', median(d['r'] for r, d in ld), 'in the last 50 rounds', sum(d['r'] > 450 for r, d in ld),
      'next longest / dead one: median %.2f' % median(d['rest'] / d['L'] for r, d in ld), 'next longest under half', sum(d['rest'] * 2 < d['L'] for r, d in ld),
      'ours left median', median(d['n_left'] for r, d in ld))
gs = {}
for r, d in ld:
    gs.setdefault(r['game'], (r, []))[1].append(d)
print('  games', len(gs), wl([v[0] for v in gs.values()]))
half = [v[0] for v in gs.values() if any(d['rest'] * 2 < d['L'] for d in v[1])]
print('  games where the next longest was under half of the dead leader', len(half), wl(half))
print('== swarm spent: our deaths after S per game ==')
n = len(R)
tot = Counter()
totl = Counter()
for r in R:
    tot['feeder'] += r['n_feed']
    totl['feeder'] += r['feed_L']
    for k2, v in r['dc'].items():
        tot[k2] += v
    for k2, v in r['dl'].items():
        totl[k2] += v
for k2 in sorted(tot, key=lambda k: -tot[k]):
    print('   %-12s per game %.1f dragons, %.1f length' % (k2, tot[k2] / n, totl[k2] / n))
print('  splits after S per game', '%.1f' % mean(r['splits'] for r in R))
print('== arrival per fed game, by kind (means) ==')
for kind in ('cap', 'q300', 'r400', 'all'):
    rs = [r for r in R if r['n_feed'] > 0 and (kind == 'all' or r['kind'] == kind)]
    f = lambda k: mean(r[k] for r in rs)
    print('  %-5s n %3d feeders %.0f length %.0f dropped %.0f | eaten: dragon beside %.0f, our longest %.0f, any of ours %.0f, theirs %.1f | longest %.0f -> %.0f (peak %.0f)' % (
        kind, len(rs), f('n_feed'), f('feed_L'), f('feed_np'), f('e_tgt'), f('e_top'), f('e_us'), f('e_them'), mean(r['U'][1] for r in rs), mean(r['Ue'][1] for r in rs), mean(r['peak'] for r in rs)))
rs = [r for r in R if r['n_feed'] > 0]
print('  share of feeder length that reaches our longest: %.2f ; the dragon beside: %.2f ; lost at death (rule): %.2f' % (
    sum(r['e_top'] for r in rs) / sum(r['feed_L'] for r in rs), sum(r['e_tgt'] for r in rs) / sum(r['feed_L'] for r in rs), 1 - sum(r['feed_np'] for r in rs) / sum(r['feed_L'] for r in rs)))
print('  per game quartiles of (eaten by our longest / length given up):', [round(x, 2) for x in sorted(r['e_top'] / r['feed_L'] for r in rs)[len(rs) // 4::len(rs) // 4][:3]])
