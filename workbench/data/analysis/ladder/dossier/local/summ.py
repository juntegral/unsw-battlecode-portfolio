#!/usr/bin/env python3
"""Compact view of rows.jsonl: per arm means and paired differences against base. summ.py [rows.jsonl] [map-substring]"""
import json, sys, collections, statistics as st
path = sys.argv[1] if len(sys.argv) > 1 else 'rows.jsonl'
flt = sys.argv[2] if len(sys.argv) > 2 else ''
rows = [json.loads(l) for l in open(path)]
rows = [r for r in rows if flt in r['map']]
key = lambda r: (r['map'], r['seed'], r['side'])
by = collections.defaultdict(dict)
for r in rows: by[r['arm']][key(r)] = r
O = lambda r, k: r['measures']['ours'][k]
T = lambda r, k: r['measures']['theirs'][k]
def mean(v): return sum(v) / len(v) if v else float('nan')
KEYS = ['alive_r150', 'alive_r200', 'alive_r300', 'alive_end', 'under56_share_151_400', 'pearls_151_200', 'splits_151_200',
        'skip_share_151_200', 'longest_r300', 'longest_end', 'total_end', 'meetings_started_101_300', 'chances_under59',
        'taken_under59', 'chances_ge59', 'taken_ge59', 'meeting_net_101_300']
arms = [a for a in ('base', 'fb', 'te', 'both') + tuple(sorted(set(by) - {'base', 'fb', 'te', 'both'})) if a in by]
print('arm    n  won | ' + ' '.join(k[:14].rjust(14) for k in KEYS))
for a in arms:
    g = list(by[a].values())
    print(f"{a:5} {len(g):2} {sum(r['result']=='win' for r in g):3}  | " + ' '.join(f"{mean([O(r,k) for r in g]):14.2f}" for k in KEYS))
    if a == 'base':
        print(f"{'(opp)':5} {len(g):2} {'':3}  | " + ' '.join(f"{mean([T(r,k) for r in g]):14.2f}" for k in KEYS))
for a in arms:
    g = by[a]; tu = sum(O(r, 'taken_under59') for r in g.values()); cu = sum(O(r, 'chances_under59') for r in g.values())
    tg = sum(O(r, 'taken_ge59') for r in g.values()); cg = sum(O(r, 'chances_ge59') for r in g.values())
    print(f"take rate {a:5}: under59 {tu}/{cu} = {tu/max(1,cu):.3f}   ge59 {tg}/{cg} = {tg/max(1,cg):.3f}")
print('\npaired against base (arm minus base), split by base under56_share_151_400 >= 0.2')
for a in arms:
    if a == 'base': continue
    for name, cond in (('all', lambda b: True), ('short', lambda b: O(b, 'under56_share_151_400') >= 0.2), ('full', lambda b: O(b, 'under56_share_151_400') < 0.2)):
        pr = [(by['base'][k], r) for k, r in by[a].items() if k in by['base'] and cond(by['base'][k])]
        if not pr: continue
        w = sum((r['result'] == 'win') - (b['result'] == 'win') for b, r in pr)
        fl = f"+{sum(r['result']=='win' and b['result']!='win' for b,r in pr)} -{sum(r['result']!='win' and b['result']=='win' for b,r in pr)}"
        d = lambda k: mean([O(r, k) - O(b, k) for b, r in pr])
        print(f"{a:5} {name:5} n={len(pr):2} wins {w:+d} ({fl}) | alive200 {d('alive_r200'):+.1f} alive300 {d('alive_r300'):+.1f} aliveEnd {d('alive_end'):+.1f} "
              f"pearls151 {d('pearls_151_200'):+.1f} splits151 {d('splits_151_200'):+.1f} skip151 {d('skip_share_151_200'):+.3f} "
              f"longest300 {d('longest_r300'):+.1f} longestEnd {d('longest_end'):+.1f} totalEnd {d('total_end'):+.1f} meet {d('meetings_started_101_300'):+.1f} net {d('meeting_net_101_300'):+.1f}")
if '-v' in sys.argv:
    for k in sorted(by['base']):
        b = by['base'][k]
        print(k[0][7:], k[2], f"base {b['result'][0]} a150 {O(b,'alive_r150')}/{T(b,'alive_r150')} a300 {O(b,'alive_r300')}/{T(b,'alive_r300')} u56 {O(b,'under56_share_151_400'):.2f} L {O(b,'longest_end')}/{T(b,'longest_end')} |",
              ' '.join(f"{a} {by[a][k]['result'][0]} L{O(by[a][k],'longest_end')} a300 {O(by[a][k],'alive_r300')}" for a in arms[1:] if k in by[a]))
