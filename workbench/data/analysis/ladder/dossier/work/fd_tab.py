# Scratch (diag-feeding): tables for jobs 1 to 4 from fd_games.jsonl. Prints only.
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median

R = [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_games.jsonl').open()]


def m(xs):
    xs = list(xs)
    return '%.1f' % mean(xs) if xs else '-'


def md(xs):
    xs = list(xs)
    return '%g' % median(xs) if xs else '-'


def wl(rs):
    return '%d-%d' % (sum(r['result'] == 'win' for r in rs), sum(r['result'] == 'loss' for r in rs))


print('== job 1: by start kind ==')
for kind in ('cap', 'q300', 'r400', 'all'):
    rs = [r for r in R if kind == 'all' or r['kind'] == kind]
    print(kind, 'n', len(rs), 'W-L', wl(rs), 'S median', md(r['S'] for r in rs),
          '| ours at S: dragons', m(r['U'][0] for r in rs), 'longest', m(r['U'][1] for r in rs), 'total', m(r['U'][2] for r in rs),
          '| end:', m(r['Ue'][0] for r in rs), m(r['Ue'][1] for r in rs), m(r['Ue'][2] for r in rs),
          '| theirs at S:', m(r['T'][0] for r in rs), m(r['T'][1] for r in rs), m(r['T'][2] for r in rs),
          '| end:', m(r['Te'][0] for r in rs), m(r['Te'][1] for r in rs), m(r['Te'][2] for r in rs))
    print('   medians ours S', md(r['U'][0] for r in rs), md(r['U'][1] for r in rs), md(r['U'][2] for r in rs), 'end', md(r['Ue'][0] for r in rs),
          md(r['Ue'][1] for r in rs), md(r['Ue'][2] for r in rs), '| theirs S', md(r['T'][0] for r in rs), md(r['T'][1] for r in rs), md(r['T'][2] for r in rs),
          'end', md(r['Te'][0] for r in rs), md(r['Te'][1] for r in rs), md(r['Te'][2] for r in rs))
    print('   ended', sorted(Counter((r['ended_by'], r['result']) for r in rs).items()))
    print('   fed games', sum(r['n_feed'] > 0 for r in rs), 'feeders/game', m(r['n_feed'] for r in rs))

print('== position at S (who would win if it stopped there) x result ==')
for kind in ('cap', 'q300', 'r400', 'all'):
    rs = [r for r in R if kind == 'all' or r['kind'] == kind]
    c = Counter((r['at'][1], r['at'][0], r['result']) for r in rs)
    print(kind, sorted(c.items()))
    c2 = Counter((r['at'][1], r['result']) for r in rs)
    print('   ', sorted(c2.items()))

print('== job 2: what feeding buys ==')
won_len = [r for r in R if r['result'] == 'win' and r['ended_by'] in ('longest dragon', 'total length')]
flip = [r for r in won_len if r['U'][1] < r['Te'][1]]
tie = [r for r in won_len if r['U'][1] == r['Te'][1]]
print('won on longest/total', len(won_len), 'our longest at S < their final longest', len(flip), 'equal', len(tie),
      'already longer', len(won_len) - len(flip) - len(tie))
print('  flips by kind', Counter(r['kind'] for r in flip), 'by layout', Counter(r['layout'] for r in flip).most_common())
print('  flips: fed?', Counter(r['n_feed'] > 0 for r in flip), 'median S longest', md(r['U'][1] for r in flip), 'their end', md(r['Te'][1] for r in flip),
      'our end', md(r['Ue'][1] for r in flip))
# of the flips: how many had our longest at S already above THEIR longest at S (they grew past it later)
print('  flips where we led on longest at S', sum(r['U'][1] > r['T'][1] for r in flip), 'behind at S', sum(r['U'][1] < r['T'][1] for r in flip))
# flips in which feeder pearls eaten by the top were needed: our end longest - feeder pearls eaten by top <= their end
need = [r for r in flip if r['Ue'][1] - r['e_top'] <= r['Te'][1]]
print('  flips that need the fed pearls (end longest minus fed pearls eaten by top <= their end longest)', len(need),
      'without them still longer', len(flip) - len(need))
allr = [r for r in R]
print('all games reaching S: our longest at S > their final longest', sum(r['U'][1] > r['Te'][1] for r in allr), 'of', len(allr),
      '; W-L among them', wl([r for r in allr if r['U'][1] > r['Te'][1]]))
alr = [r for r in allr if r['U'][1] > r['Te'][1]]
print('   those: ended', sorted(Counter((r['ended_by'], r['result']) for r in alr).items()))
print('   margin ratio our S longest / their end longest >= 1.5:', sum(r['U'][1] >= 1.5 * r['Te'][1] for r in alr), '>=2:', sum(r['U'][1] >= 2 * r['Te'][1] for r in alr))
# both queens dead at S and at end (pure longest games)
print('== job 3: costs ==')
ld = [r for r in R if r['lead_deaths']]
print('games with a leader death after S (longest of ours at the time, 8+ long, or the S-top/fed target)', len(ld), 'W-L', wl(ld))
first = [r['lead_deaths'][0] for r in ld]
print('  cause of first', Counter((d['cause'], d['o_side']) for d in first).most_common())
print('  length of first: median', md(d['L'] for d in first), 'round median', md(d['r'] for d in first))
alld = [d for r in ld for d in r['lead_deaths']]
print('  all leader deaths', len(alld), Counter((d['cause'], d['o_side']) for d in alld).most_common())
print('  lengths', Counter(min(d['L'] // 10 * 10, 50) for d in alld).most_common())
big = [r for r in R if any(d['L'] >= 15 and d['top'] for d in r['lead_deaths'])]
print('games where our longest (15+) died after S', len(big), 'W-L', wl(big), 'ended', sorted(Counter((r['ended_by'], r['result']) for r in big).items()))
wiped = [r for r in R if r['Ue'][0] == 0]
few = [r for r in R if 0 < r['Ue'][0] <= 3]
print('wiped after S', len(wiped), 'by kind', Counter(r['kind'] for r in wiped), '| ended with 1-3 dragons', len(few), 'W-L', wl(few))
print('  wiped: ours at S dragons', sorted(r['U'][0] for r in wiped), 'fed', [r['n_feed'] for r in wiped])
print('  few: ours at S dragons median', md(r['U'][0] for r in few), 'n_feed median', md(r['n_feed'] for r in few))
lostahead = [r for r in R if r['result'] == 'loss' and r['ahead_all']]
lostlead = [r for r in R if r['result'] == 'loss' and r['at'][1] == 'us']
print('lost though ahead on every rule at S', len(lostahead), 'of', sum(r['ahead_all'] for r in R), 'ahead-on-every-rule games; lost though ahead on the deciding rule', len(lostlead), 'of',
      sum(r['at'][1] == 'us' for r in R))
print('  the other way: won though behind on the deciding rule at S', sum(r['result'] == 'win' and r['at'][1] == 'them' for r in R), 'of', sum(r['at'][1] == 'them' for r in R))
print('  lostahead ended', Counter(r['ended_by'] for r in lostahead), 'kind', Counter(r['kind'] for r in lostahead), 'layout', Counter(r['layout'] for r in lostahead).most_common())
for r in sorted(lostahead, key=lambda r: r['game']):
    print('   ', r['game'], r['layout'], r['rating'], r['kind'], r['S'], 'U', r['U'], 'T', r['T'], 'end U', r['Ue'], 'T', r['Te'], r['ended_by'], 'feed', r['n_feed'], 'peak', r['peak'], r['peak_r'],
          'lead deaths', [(d['r'], d['L'], d['cause'], d['o_side'], d['o_len']) for d in r['lead_deaths']][:4])
print('== job 4: arrival ==')
fed = [r for r in R if r['n_feed'] > 0]
tot = Counter()
for r in fed:
    for k in ('n_feed', 'feed_L', 'feed_np', 'e_tgt', 'e_top', 'e_us', 'e_them'):
        tot[k] += r[k]
print('fed games', len(fed), dict(tot))
print('  per game: feeders', m(r['n_feed'] for r in fed), 'length given up', m(r['feed_L'] for r in fed), 'pearls dropped', m(r['feed_np'] for r in fed),
      'eaten by the dragon beside', m(r['e_tgt'] for r in fed), 'by our longest', m(r['e_top'] for r in fed), 'by any of ours', m(r['e_us'] for r in fed), 'by them', m(r['e_them'] for r in fed))
print('  leader gain S to end (our longest end - at S): mean', m(r['Ue'][1] - r['U'][1] for r in fed), 'median', md(r['Ue'][1] - r['U'][1] for r in fed),
      'peak - S', m(r['peak'] - r['U'][1] for r in fed), 'total length change', m(r['Ue'][2] - r['U'][2] for r in fed), 'dragons change', m(r['Ue'][0] - r['U'][0] for r in fed))
for kind in ('cap', 'q300', 'r400'):
    rs = [r for r in fed if r['kind'] == kind]
    print('  ', kind, len(rs), 'feeders', m(r['n_feed'] for r in rs), 'L', m(r['feed_L'] for r in rs), 'np', m(r['feed_np'] for r in rs), 'e_tgt', m(r['e_tgt'] for r in rs),
          'e_top', m(r['e_top'] for r in rs), 'e_us', m(r['e_us'] for r in rs), 'e_them', m(r['e_them'] for r in rs), '| longest S', m(r['U'][1] for r in rs), 'end', m(r['Ue'][1] for r in rs),
          'peak', m(r['peak'] for r in rs), '| total S', m(r['U'][2] for r in rs), 'end', m(r['Ue'][2] for r in rs), '| dragons', m(r['U'][0] for r in rs), m(r['Ue'][0] for r in rs),
          '| their dragons', m(r['T'][0] for r in rs), m(r['Te'][0] for r in rs), 'their total', m(r['T'][2] for r in rs), m(r['Te'][2] for r in rs))
ta = Counter()
for r in fed:
    for k, v in r['top_ate'].items():
        ta[k] += v
print('  what our longest ate after S, all fed games: natural', ta['n'], 'feeder drops', ta['f'], 'other own drops', ta['o'], 'their drops', ta['t'])
dc = Counter()
dl = Counter()
for r in R:
    for k, v in r['dc'].items():
        dc[k] += v
    for k, v in r['dl'].items():
        dl[k] += v
print('  our other deaths after S (count, length):', sorted((k, dc[k], dl[k]) for k in dc))
print('  feeder deaths', sum(r['n_feed'] for r in R), 'length', sum(r['feed_L'] for r in R))
