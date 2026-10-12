"""Extra cuts: shed rounds, tighter comparison, game-end effect."""
import json
from collections import defaultdict
D = json.load(open('data/codex/astra/shed-sonnet/data.json'))
G = D['games']
print('last round hist', sorted(set(g['last'] for g in G))[:5], '...', sorted(set(g['last'] for g in G))[-5:])
S = [dict(s, g=g) for g in G for s in g['sheds']]
rb = defaultdict(int)
for s in S:
    rb[(s['r'] // 50) * 50] += 1
print('shed round hist (len 4+)', dict(sorted(rb.items())))
rb = defaultdict(int)
for s in S:
    if s['before'] >= 10:
        rb[(s['r'] // 50) * 50] += 1
print('shed round hist (len 10+)', dict(sorted(rb.items())))
print('queen length before, 4-5 sheds: 4 =', sum(1 for s in S if s['before'] == 4), '5 =', sum(1 for s in S if s['before'] == 5))


def bucket(L):
    return '4-5' if L <= 5 else ('6-9' if L <= 9 else '10+')


def oc(g, r):
    d = g['qdead']
    return (d is not None and d - r <= 3, d is not None and d - r <= 20, d is None)


def tab(rows, label):
    n = len(rows)
    if not n:
        print('  ', label, 'N=0')
        return
    print('  %-46s N=%-5d dead<=3 %2.0f%%  dead<=20 %2.0f%%  alive-end %2.0f%%' % (label, n, 100 * sum(r[0] for r in rows) / n, 100 * sum(r[1] for r in rows) / n, 100 * sum(r[2] for r in rows) / n))


print('\nOnly turns >=25 rounds before the last round (kills the game-end artefact)')
for b in ('4-5', '10+'):
    tab([oc(s['g'], s['r']) for s in S if bucket(s['before']) == b and s['r'] <= s['g']['last'] - 25], 'sheds len ' + b)
    for nd in (3, 2):
        tab([oc(g, t['r']) for g in G for t in g['turns'] if bucket(t['ql']) == b and t['nd'] <= nd and not t['split'] and t['r'] <= g['last'] - 25],
            'no-split nd<=%d len %s' % (nd, b))
print('\nShed vs no-split, same nearest-enemy distance (len 4+)')
for nd in (1, 2, 3, 4, 5, 6):
    a = [oc(s['g'], s['r']) for s in S if s['nd'] == nd and s['r'] <= s['g']['last'] - 25]
    c = [oc(g, t['r']) for g in G for t in g['turns'] if t['ql'] >= 4 and t['nd'] == nd and not t['split'] and t['r'] <= g['last'] - 25]
    tab(a, 'shed nd==%d' % nd)
    tab(c, 'no-split nd==%d' % nd)
print('\nSame, len 10+ only')
for nd in (1, 2, 3, 4, 5, 6):
    a = [oc(s['g'], s['r']) for s in S if s['nd'] == nd and s['before'] >= 10]
    c = [oc(g, t['r']) for g in G for t in g['turns'] if t['ql'] >= 10 and t['nd'] == nd and not t['split']]
    tab(a, 'shed nd==%d len10+' % nd)
    tab(c, 'no-split nd==%d len10+' % nd)
print('\nSame, nearest-enemy length >=4 (a real threat)')
a = [oc(s['g'], s['r']) for s in S if s['nd'] <= 6 and s['nl'] >= 4]
c = [oc(g, t['r']) for g in G for t in g['turns'] if t['ql'] >= 4 and t['nd'] <= 3 and t['nl'] >= 4 and not t['split']]
tab(a, 'shed nearest<=6 nl>=4')
tab(c, 'no-split nearest<=3 nl>=4')
# queen outcome 10+ in no-split nd<=3 compare end length
print('\nQueen final length after shed 10+ vs queens 10+ that were within 3 of an enemy head at some turn without a shed (per game)')
gl = []
for g in G:
    if any(t['ql'] >= 10 and t['nd'] <= 3 and not t['split'] for t in g['turns']) and not any(s['before'] >= 10 for s in g['sheds']):
        gl.append(g)
print('  games %d wins %d queen alive at end %d' % (len(gl), sum(g['win'] for g in gl), sum(1 for g in gl if g['qdead'] is None)))
gs = [g for g in G if any(s['before'] >= 10 for s in g['sheds'])]
print('  shed10+ games %d wins %d queen alive at end %d' % (len(gs), sum(g['win'] for g in gs), sum(1 for g in gs if g['qdead'] is None)))
# 10+ games by enemy queen status at shed
print('\nshed 10+: enemy queen at shed: dead (EQ=0) %d, alive %d' % (sum(1 for s in S if s['before'] >= 10 and s['eq'] == 0), sum(1 for s in S if s['before'] >= 10 and s['eq'] > 0)))
for s in S:
    if s['before'] >= 10:
        print('   g%d r%d Q%d EQ%d  Qlen vs EQ: %s' % (s['g']['id'], s['r'], s['before'], s['eq'], 'ahead' if s['before'] > s['eq'] else 'behind/tie'))
