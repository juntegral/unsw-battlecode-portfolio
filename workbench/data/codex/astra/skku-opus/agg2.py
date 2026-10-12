import json
from collections import defaultdict, Counter
from statistics import median, mean
R = json.load(open('data/codex/astra/skku-opus/rows.json'))
def wr(rs): return f"{sum(r['result']=='win' for r in rs)}/{len(rs)}"
g = defaultdict(list)
for r in R: g[('ourQid', r['ourq_id'])].append(r); g[('seat,ourQid', r['seat'], r['ourq_id'])].append(r)
print({k: wr(v) for k, v in sorted(g.items())})
# small / large maps by seat
g = defaultdict(list)
for r in R: g[(r['seat'], 'small<=625' if r['cells'] <= 625 else 'mid' if r['cells'] <= 1701 else 'big')].append(r)
print({k: wr(v) for k, v in sorted(g.items())})
# matched maps: per map, mean of metric by seat, then mean over maps present in both
def matched(name, f):
    m = defaultdict(lambda: defaultdict(list))
    for r in R:
        v = f(r)
        if v is not None: m[r['map']][r['seat']].append(v)
    both = [k for k in m if m[k]['A'] and m[k]['B']]
    a = mean(mean(m[k]['A']) for k in both); b = mean(mean(m[k]['B']) for k in both)
    print(f'matched {len(both)} maps  {name}: seatA {a:.1f}  seatB {b:.1f}')
matched('win', lambda r: 100 * (r['result'] == 'win'))
matched('our p100', lambda r: r['p100'][0]); matched('their p100', lambda r: r['p100'][1])
matched('our n100', lambda r: r['n100'][0]); matched('their n100', lambda r: r['n100'][1])
matched('our n50', lambda r: r['n50'][0]); matched('their n50', lambda r: r['n50'][1])
matched('their queen home<=r100', lambda r: r['home100'][1]); matched('our queen home<=r100', lambda r: r['home100'][0])
matched('our queen died %', lambda r: 100 * (r['qd'][0] is not None)); matched('their queen died %', lambda r: 100 * (r['qd'][1] is not None))
matched('our queen dead by r100 %', lambda r: 100 * (r['qd'][0] is not None and r['qd'][0] <= 100)); matched('their queen dead by r100 %', lambda r: 100 * (r['qd'][1] is not None and r['qd'][1] <= 100))
matched('our first eat', lambda r: r['first_eat'][0]); matched('their first eat', lambda r: r['first_eat'][1])
# games that ended early (n100 0/0) and our losses: queen state when ours died
print('losses: our queen death r, L, units at death, foe q alive, rammer')
for r in R:
    if r['result'] != 'win':
        x = r['atk'][0]
        print(' ', r['gid'], r['seat'], r['ver'], r['map'], r['how'], 'ends', r['ends'], '|', None if not x else (x['r'], 'qL', x['qL'], 'units', x['units'], 'foeQalive', x['foe_q_alive'], 'self' if x['self'] else ('ram L', x['aL'], 'dist', x['dist'], 'paid', x['paid'], 'seen', x['seen'])), 'theirQd', r['qd'][1], 'home', r['home100'])
print('wins: their queen death')
for r in R:
    if r['result'] == 'win':
        x = r['atk'][1]
        print(' ', r['gid'], r['seat'], r['ver'], r['map'], r['how'], '|', None if not x else (x['r'], 'qL', x['qL'], 'units', x['units'], 'ourQalive', x['foe_q_alive'], 'self r%d' % x['reason'] if x['self'] else ('ram L', x['aL'], 'dist', x['dist'], 'paid', x['paid'], 'seen', x['seen'])), 'ourQd', r['qd'][0])
# units their queen had around when it died vs ours
for s, nm in ((0, 'our'), (1, 'their')):
    xs = [r['atk'][s] for r in R if r['atk'][s]]
    print(nm, 'queen death: side units at death', dict(sorted(Counter(min(x['units'], 10) if x['units'] is not None else -1 for x in xs).items())), 'round<=60', sum(x['r'] <= 60 for x in xs), '61-150', sum(60 < x['r'] <= 150 for x in xs), '>150', sum(x['r'] > 150 for x in xs))
