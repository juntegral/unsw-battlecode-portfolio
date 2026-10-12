import json, sys
from collections import defaultdict, Counter
from statistics import median, mean
from math import comb
R = json.load(open('data/codex/astra/skku-opus/rows.json'))
def wr(rs): return f"{sum(r['result']=='win' for r in rs)}/{len(rs)}"
def med(xs):
    xs = [x for x in xs if x is not None]
    return round(median(xs), 1) if xs else None
def avg(xs):
    xs = [x for x in xs if x is not None]
    return round(mean(xs), 1) if xs else None
print('TABLE gid when(UTC) ver seat map cells result how lastR | ourQ(end) theirQ(end) | ourQdeath theirQdeath | p100 us/them | n100 us/them')
for r in R:
    e = r['ends']
    print(r['gid'], r['when'][5:16], r['ver'], r['seat'], r['map'], r['cells'], r['result'], r['how'], r['last'], '|', e[0][3], e[1][3], '|', r['qd'][0], r['qd'][1], '|',
          f"{r['p100'][0]}/{r['p100'][1]}", '|', f"{r['n100'][0]}/{r['n100'][1]}", '| ids', r['ourq_id'], r['theirq_id'])
print()
for key in ('seat', 'ver', 'map'):
    g = defaultdict(list)
    for r in R: g[r[key]].append(r)
    print('BY', key, {k: wr(v) for k, v in sorted(g.items())})
g = defaultdict(list)
for r in R: g[(r['ver'], r['seat'])].append(r)
print('BY ver,seat', {k: wr(v) for k, v in sorted(g.items())})
g = defaultdict(list)
for r in R: g[(r['map'], r['seat'])].append(r)
print('BY map,seat (>=3)', {k: wr(v) for k, v in sorted(g.items()) if len(v) >= 3})
print('BY map,seat all', {k: wr(v) for k, v in sorted(g.items())})
# matched-map expectation: apply seat-A per-map win rate to the seat-B draw
A = defaultdict(list)
for r in R:
    if r['seat'] == 'A': A[r['map']].append(r['result'] == 'win')
B = [r for r in R if r['seat'] == 'B']
exp = sum(mean(A[r['map']]) for r in B if r['map'] in A); nB = sum(1 for r in B if r['map'] in A)
print('seat-B games on maps also played from seat A:', nB, 'expected wins at seat-A per-map rates', round(exp, 2), 'actual', sum(r['result'] == 'win' for r in B if r['map'] in A))
# same for version: restrict to one14+one15
for v in ('one14', 'one15'):
    a = [r for r in R if r['ver'] == v and r['seat'] == 'A']; b = [r for r in R if r['ver'] == v and r['seat'] == 'B']
    Am = defaultdict(list)
    for r in a: Am[r['map']].append(r['result'] == 'win')
    print(v, 'A', wr(a), 'B', wr(b), 'B-maps:', [(r['map'], r['result'], 'A same ver:', Am.get(r['map'])) for r in b])
# fisher exact
def fisher(a, b, c, d):
    n = a + b + c + d; r1 = a + b; c1 = a + c
    def p(x): return comb(r1, x) * comb(n - r1, c1 - x) / comb(n, c1)
    p0 = p(a)
    return sum(p(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if p(x) <= p0 + 1e-12)
a = [r for r in R if r['seat'] == 'A']; b = [r for r in R if r['seat'] == 'B']
wa = sum(r['result'] == 'win' for r in a); wb = sum(r['result'] == 'win' for r in b)
print('fisher two-sided seat', round(fisher(wa, len(a) - wa, wb, len(b) - wb), 4))
a2 = [r for r in a if r['ver'] in ('one14', 'one15')]; b2 = [r for r in b if r['ver'] in ('one14', 'one15')]
wa2 = sum(r['result'] == 'win' for r in a2); wb2 = sum(r['result'] == 'win' for r in b2)
print('one14+15 only: A', wr(a2), 'B', wr(b2), 'fisher', round(fisher(wa2, len(a2) - wa2, wb2, len(b2) - wb2), 4))
print()
def block(name, rs):
    print('==', name, 'n', len(rs), 'wins', wr(rs))
    oq = [r['qd'][0] for r in rs]; tq = [r['qd'][1] for r in rs]
    print(' our queen died', sum(x is not None for x in oq), 'median r', med(oq), '| their queen died', sum(x is not None for x in tq), 'median r', med(tq))
    fk = Counter()
    for r in rs:
        o, t = r['qd']
        fk['none' if o is None and t is None else 'ours first' if (t is None or (o is not None and o < t)) else 'theirs first' if (o is None or t < o) else 'same round'] += 1
    print(' whose queen dies first', dict(fk))
    print(' our queen dead by r100', sum(x is not None and x <= 100 for x in oq), 'theirs', sum(x is not None and x <= 100 for x in tq))
    print(' first eat us/them', med([r['first_eat'][0] for r in rs]), med([r['first_eat'][1] for r in rs]), ' first split us/them', med([r['first_split'][0] for r in rs]), med([r['first_split'][1] for r in rs]))
    for k in ('n50', 'n100', 'p50', 'p100'):
        print(' ', k, 'us/them mean', avg([r[k][0] for r in rs]), avg([r[k][1] for r in rs]), 'median', med([r[k][0] for r in rs]), med([r[k][1] for r in rs]))
    print('  queen home dist median (<=r100) us/them', med([r['home100'][0] for r in rs]), med([r['home100'][1] for r in rs]), 'whole game', med([r['home'][0] for r in rs]), med([r['home'][1] for r in rs]))
    print('  queen L at r50 us/them', med([r['qL50'][0] for r in rs]), med([r['qL50'][1] for r in rs]))
    for s, nm in ((0, 'OUR queen death'), (1, 'THEIR queen death')):
        at = [r['atk'][s] for r in rs if r['atk'][s]]
        ram = [x for x in at if not x['self'] and x['actor_side'] is not None and x['actor_side'] != s]
        selfd = [x for x in at if x['self']]
        print(' ', nm, 'n', len(at), 'rammed by enemy', len(ram), 'own move', len(selfd), 'other', len(at) - len(ram) - len(selfd))
        if ram:
            print('    rammer L', dict(sorted(Counter(x['aL'] for x in ram).items())), 'dist', dict(sorted(Counter(x['dist'] for x in ram).items())), 'paid', dict(sorted(Counter(x['paid'] for x in ram).items())),
                  'steps', dict(sorted(Counter(x['steps'] for x in ram).items())), 'portal', sum(x['portal'] for x in ram), 'seen last turn', sum(bool(x['seen']) for x in ram), 'foe queen already dead', sum(not x['foe_q_alive'] for x in ram),
                  'queen L', dict(sorted(Counter(x['qL'] for x in ram).items())))
        if selfd:
            print('    own-move deaths: reason', dict(Counter(x['reason'] for x in selfd)), 'queen L', dict(sorted(Counter(x['qL'] for x in selfd).items())), 'foe queen already dead', sum(not x['foe_q_alive'] for x in selfd))
block('seat A', a); block('seat B', b)
block('seat A wins', [r for r in a if r['result'] == 'win']); block('seat A losses', [r for r in a if r['result'] != 'win'])
block('seat B wins', [r for r in b if r['result'] == 'win']); block('seat B losses', [r for r in b if r['result'] != 'win'])
block('all wins', [r for r in R if r['result'] == 'win']); block('all losses', [r for r in R if r['result'] != 'win'])
print()
print('queen death detail (ours):')
for r in R:
    x = r['atk'][0]
    if x: print(' ', r['gid'], r['seat'], r['map'], r['result'], x)
print('queen death detail (theirs):')
for r in R:
    x = r['atk'][1]
    if x: print(' ', r['gid'], r['seat'], r['map'], r['result'], x)
