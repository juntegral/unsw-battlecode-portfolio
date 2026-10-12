# Scratch (diag-feeding): (a) how the rammed leader was standing, from fd_ram-*.jsonl; (b) feeding our queen, split by
# whether their queen was alive when the feeder died, from fd_scan-*.jsonl and fd_games.jsonl. Prints only.
import json
from collections import Counter
from pathlib import Path
from statistics import median

R = [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_games.jsonl').open()]
BY = dict((r['game'], r) for r in R)
X = []
for k in range(2):
    p = Path('data/analysis/ladder/dossier/work/fd_ram-%d.jsonl' % k)
    if p.exists():
        X += [json.loads(l) for l in p.open() if l.strip()]
X = [x for x in X if x['r'] >= BY[x['game']]['S']]
print('== a. rammed leaders (hit, 8+, our longest, after S) ==', len(X), 'in games', len(set(x['game'] for x in X)))
if X:
    print(' rammer length', sorted(Counter(min(x['ram_L'], 10) for x in X).items()))
    print(' rammer started its turn this many tiles from the head', sorted(Counter(min(x['ram_from'], 8) for x in X).items()))
    print(' rammer steps this turn', sorted(Counter(x['ram_steps'] for x in X).items()), 'more than its free steps', sum(x['ram_steps'] > x['free'] for x in X))
    known = [x for x in X if x['seen'] is not None]
    print(' leader had a turn record', len(known), 'rammer in its 7x7 view at its last turn start', sum(x['seen'] for x in known),
          'distance then (tiles)', sorted(Counter(min(x['then_man'], 9) if x['then_man'] is not None else -1 for x in known).items()))
    print(' leader steps on its last turn', sorted(Counter(min(x['lead_steps'], 4) for x in known).items()), 'ate on it', sum(x['lead_ate'] > 0 for x in known))
    print(' enemy heads in view at its last turn', sorted(Counter(min(x['in_view'], 4) for x in known).items()))
    print(' ours within 5 tiles at its last turn', sorted(Counter(min(x['own5'], 4) for x in known).items()), 'at death', sorted(Counter(min(x['own5_now'], 4) for x in X).items()))
    print(' ours alive at that moment: median', median(x['n_us'] for x in X), '; with 20+ alive', sum(x['n_us'] >= 20 for x in X), 'of them with nobody within 5', sum(x['n_us'] >= 20 and x['own5_now'] == 0 for x in X))
    print(' a feeder died within 10 tiles in the last 10 rounds', sum(x['fed10'] > 0 for x in X), 'leader is our queen', sum(x['q'] for x in X))
    print(' leader length', sorted(Counter(min(x['L'] // 10 * 10, 50) for x in X).items()))

print('== b. feeding the queen ==')
G = []
for k in range(4):
    G += [json.loads(l) for l in Path('data/analysis/ladder/dossier/work/fd_scan-%d.jsonl' % k).open()]
tot = Counter()
games = {}
for g in G:
    if g['game'] not in BY:
        continue
    r0 = BY[g['game']]
    s = g['series']
    c = Counter()
    for d in g['feeders']:
        if d['tgt'] >= 0 and d['L'] * 2 <= d['tgt_len'] and not d['q'] and d['r'] >= r0['S'] and d['tgt_q']:
            key = 'theirs dead' if s[d['r']][8] == 0 else 'theirs alive'
            c[key] += 1
            c[key + ' np'] += d['np']
            c[key + ' eaten by queen'] += d['e_tgt']
    for k2, v in c.items():
        tot[k2] += v
    if c:
        games[g['game']] = c
print(' feeder deaths beside our queen:', dict(tot), 'games', len(games))


def wl(rs):
    return '%d-%d' % (sum(r['result'] == 'win' for r in rs), sum(r['result'] == 'loss' for r in rs))


dead = [BY[i] for i, c in games.items() if c['theirs dead'] >= 3]
alive = [BY[i] for i, c in games.items() if c['theirs alive'] >= 3 and c['theirs dead'] < 3]
print(' games with 3+ feeders to our queen while THEIR queen was dead:', len(dead), 'W-L', wl(dead), 'ended', sorted(Counter((r['ended_by'], r['result']) for r in dead).items()))
qd = [r for r in dead if r['Ue'][3] == 0]
print('   our queen dead at the end in', len(qd), 'W-L', wl(qd), '; alive in', len(dead) - len(qd), 'W-L', wl([r for r in dead if r['Ue'][3] > 0]))
for r in sorted(qd, key=lambda r: r['game']):
    c = games[r['game']]
    qdeath = [d for d in r['lead_deaths'] if d['q']]
    print('    ', r['game'], r['layout'], r['rating'], r['result'], r['ended_by'], 'S', r['S'], 'U', r['U'], 'T', r['T'], 'endU', r['Ue'], 'endT', r['Te'], 'fed to queen (their q dead)', c['theirs dead'],
          'pearls', c['theirs dead eaten by queen'], 'queen death', [(d['r'], d['L'], d['cause'], d['o_len']) for d in qdeath], 'queen ate', r['queen_ate'])
print(' games with 3+ feeders to our queen while their queen was alive (and not the above):', len(alive), 'W-L', wl(alive), 'ended', sorted(Counter((r['ended_by'], r['result']) for r in alive).items()))
# queen rule wins with both queens alive: was the growth needed
qw = [r for r in R if r['result'] == 'win' and r['ended_by'] == 'queen rule']
both = [r for r in qw if r['Te'][3] > 0]
print(' won on the queen rule', len(qw), 'their queen alive at the end', len(both), 'of those our queen at S not longer than their final queen', sum(r['U'][3] <= r['Te'][3] for r in both))
ql = [r for r in R if r['result'] == 'loss' and r['ended_by'] == 'queen rule']
print(' lost on the queen rule', len(ql), 'our queen alive at the end', sum(r['Ue'][3] > 0 for r in ql), 'our queen alive at S', sum(r['U'][3] > 0 for r in ql))
# position at S: only our queen alive
only = [r for r in R if r['U'][3] > 0 and r['T'][3] == 0]
print(' only our queen alive at S:', len(only), 'W-L', wl(only), 'queen dead at end', sum(r['Ue'][3] == 0 for r in only), 'W-L then', wl([r for r in only if r['Ue'][3] == 0]),
      'by kind', Counter(r['kind'] for r in only))
