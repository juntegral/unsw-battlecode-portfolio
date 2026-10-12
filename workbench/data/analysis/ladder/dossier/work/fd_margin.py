# Scratch (diag-feeding): margins of games decided on longest dragon, and what an escort rule could reach. Prints only.
import json
from collections import Counter
from pathlib import Path

R = [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_games.jsonl').open()]
lw = [r for r in R if r['ended_by'] == 'longest dragon']
for res in ('win', 'loss'):
    ms = sorted(abs(r['Ue'][1] - r['Te'][1]) for r in lw if r['result'] == res)
    print(res, len(ms), 'margin <=2', sum(m <= 2 for m in ms), '<=3', sum(m <= 3 for m in ms), '<=5', sum(m <= 5 for m in ms), 'median', ms[len(ms) // 2])
    for kind in ('cap', 'q300', 'r400'):
        k = sorted(abs(r['Ue'][1] - r['Te'][1]) for r in lw if r['result'] == res and r['kind'] == kind)
        print('    ', kind, len(k), '<=3', sum(m <= 3 for m in k), '<=5', sum(m <= 5 for m in k))
# games in which a ram on our longest (15+) changed who held the longest dragon: before the ram ours > their final, after it the rest < their final
dec = []
for r in R:
    if r['result'] != 'loss':
        continue
    for d in r['lead_deaths']:
        if d['cause'] == 'headon' and d['o_side'] == 't' and not d['mover'] and d['L'] > r['Te'][1] and r['Ue'][1] <= r['Te'][1]:
            dec.append((r, d))
            break
print('lost games with a rammed leader that was longer than their final longest', len(dec), Counter(r['ended_by'] for r, d in dec), Counter(r['kind'] for r, d in dec))
print('   queen among them', sum(d['q'] for r, d in dec), 'rounds', sorted(d['r'] for r, d in dec))
allram = [(r, d) for r in R for d in r['lead_deaths'] if d['cause'] == 'headon' and d['o_side'] == 't' and not d['mover'] and d['L'] >= 10]
gl = set(r['game'] for r, d in allram)
print('games with our longest (10+) rammed after S', len(gl), 'W-L %d-%d' % (sum(r['result'] == 'win' for r in R if r['game'] in gl), sum(r['result'] == 'loss' for r in R if r['game'] in gl)),
      '| games without', len(R) - len(gl), 'W-L %d-%d' % (sum(r['result'] == 'win' for r in R if r['game'] not in gl), sum(r['result'] == 'loss' for r in R if r['game'] not in gl)))
fed = [r for r in R if r['n_feed'] > 0]
print('feeders per fed game: quartiles', sorted(r['n_feed'] for r in fed)[len(fed) // 4], sorted(r['n_feed'] for r in fed)[len(fed) // 2], sorted(r['n_feed'] for r in fed)[3 * len(fed) // 4],
      '| games with 6 or fewer feeders', sum(r['n_feed'] <= 6 for r in fed), 'W-L %d-%d' % (sum(r['result'] == 'win' for r in fed if r['n_feed'] <= 6), sum(r['result'] == 'loss' for r in fed if r['n_feed'] <= 6)))
few = [r for r in fed if r['n_feed'] <= 6 and r['result'] == 'win' and r['ended_by'] == 'longest dragon']
print('   won on longest with 6 or fewer feeders', len(few), 'margins', sorted(r['Ue'][1] - r['Te'][1] for r in few))
