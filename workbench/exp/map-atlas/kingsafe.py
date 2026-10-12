"""kingsafe.py — summarises cache/kingpath.jsonl (path-distance king safety) per map/layout for winners, losers and us.

King = the team's longest living dragon (>= 8) at the first turn of each round r300-499; distance = static path distance
(kelp, portals, wrap; bodies ignored) from its head to the nearest enemy head (31 = 31+ or unreachable).
Population: top games without a stalled team and with a winner (layout from raw.jsonl), our W0-W12 top-6 games.
Output: cache/kingsafe.json.
"""
import json, pathlib, collections
O = pathlib.Path(__file__).resolve().parent / 'cache'
WAVES = ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3'] + [f'cand-stack{i}-online' for i in range(1, 7)] + \
        ['cand-stack6-online-r2'] + [f'cand-stack{i}-online' for i in range(7, 12)]
meta = {}
for l in open(O / 'raw.jsonl'):
    r = json.loads(l)
    if r['src'] == 'local': continue
    meta[r['key']] = (r['map'] + '/' + r['layout'], r['src'], bool(r['stall']), r.get('set'), r.get('oppId'), r['winner'], r.get('us'))
acc = collections.defaultdict(lambda: {s: {'hist': [0] * 32, 'kd': [], 'games': 0} for s in 'WLU'})
mism = 0
for l in open(O / 'kingpath.jsonl'):
    k = json.loads(l); mism += k['mismatch']
    if k['key'] not in meta: continue
    lay, src, stall, st, opp, win, us = meta[k['key']]
    sides = []
    if src == 'top' and not stall and win: sides = [('W', win), ('L', 'B' if win == 'A' else 'A')]
    elif src == 'online' and st in WAVES and opp != 545: sides = [('U', us)]
    for s, t in sides:
        a = acc[lay][s]; a['games'] += 1
        for i, v in enumerate(k[t]['hist']): a['hist'][i] += v
        a['kd'] += k[t]['kd']
def summ(a):
    h = a['hist']; n = sum(h)
    if not n: return {'kingRounds': 0, 'games': a['games']}
    cum = lambda d: sum(h[:d + 1]) / n
    q = lambda p: next(i for i in range(32) if sum(h[:i + 1]) >= p * n)
    kd = a['kd']; late = len(kd)
    by = collections.Counter(x[2] for x in kd)
    dists = sorted(x[4] for x in kd if x[4] >= 0)
    kl = sorted(x[5] for x in kd if x[5] > 0)
    return {'games': a['games'], 'kingRounds': n, 'le2': cum(2), 'le3': cum(3), 'le4': cum(4), 'le6': cum(6), 'le8': cum(8), 'p10': q(0.10), 'p25': q(0.25), 'median': q(0.5),
            'kingDeaths': late, 'kingDeathsPerGame': late / a['games'] if a['games'] else None, 'deathReasons': dict(by),
            'deathDistMedian': dists[len(dists) // 2] if dists else None, 'deathDistLe3': (sum(d <= 3 for d in dists) / len(dists)) if dists else None,
            'deathDistLe6': (sum(d <= 6 for d in dists) / len(dists)) if dists else None, 'killerLenMedian': kl[len(kl) // 2] if kl else None, 'killerN': len(kl)}
out = {lay: {s: summ(a[s]) for s in 'WLU'} for lay, a in acc.items()}
out['_checks'] = {'mismatch': mism}
(O / 'kingsafe.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
f = lambda v, d=2: '–' if v is None else f'{v:.{d}f}'
print('reconstruction mismatch', mism)
for lay in sorted(k for k in out if not k.startswith('_')):
    x = out[lay]
    print(lay, ' | '.join(f"{s}: g{x[s].get('games')} kr{x[s].get('kingRounds')} <=3 {f(x[s].get('le3'))} <=6 {f(x[s].get('le6'))} p10 {x[s].get('p10')} med {x[s].get('median')} deaths/g {f(x[s].get('kingDeathsPerGame'))} dist@death med {x[s].get('deathDistMedian')} <=3 {f(x[s].get('deathDistLe3'))} killerL {x[s].get('killerLenMedian')}" for s in 'WLU'))
