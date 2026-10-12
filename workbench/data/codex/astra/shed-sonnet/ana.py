"""Reads data.json; prints the report tables."""
import json, sys
from collections import defaultdict
D = json.load(open('data/codex/astra/shed-sonnet/data.json'))
G = D['games']
print('games', len(G), 'ranked', sum(g['ranked'] for g in G), 'unranked', sum(not g['ranked'] for g in G), 'wins', sum(g['win'] for g in G))


def bucket(L):
    return '4-5' if L <= 5 else ('6-9' if L <= 9 else '10+')


def outcome(g, r):
    d = g['qdead']
    return (d is not None and d - r <= 3, d is not None and d - r <= 20, d is None)


S = []
for g in G:
    for s in g['sheds']:
        s = dict(s)
        s['g'] = g
        S.append(s)
print('sheds', len(S), 'games with shed', sum(1 for g in G if g['sheds']))

print('\n1. sheds per game / by bucket / by version')
cnt = defaultdict(int)
for g in G:
    cnt[len(g['sheds'])] += 1
print('sheds-per-game histogram', dict(sorted(cnt.items())))
bk = defaultdict(lambda: [0, set()])
for s in S:
    b = bucket(s['before'])
    bk[b][0] += 1
    bk[b][1].add(s['g']['id'])
for b in ('4-5', '6-9', '10+'):
    print(' len', b, 'sheds', bk[b][0], 'games', len(bk[b][1]))
vs = defaultdict(lambda: [0, 0, 0, 0])
for g in G:
    v = vs[g['ver']]
    v[0] += 1
    v[1] += len(g['sheds'])
    v[2] += 1 if g['sheds'] else 0
    v[3] += sum(1 for s in g['sheds'] if s['before'] >= 10)
for v in sorted(vs):
    print(' ', v, 'games', vs[v][0], 'sheds', vs[v][1], 'games-with-shed', vs[v][2], 'sheds10+', vs[v][3], 'per-game %.2f' % (vs[v][1] / vs[v][0]))


def tab(rows, label):
    n = len(rows)
    if not n:
        print(' ', label, 'N=0')
        return
    a = sum(1 for r in rows if r[0])
    b = sum(1 for r in rows if r[1])
    c = sum(1 for r in rows if r[2])
    print('  %-34s N=%-6d dead<=3: %d (%.0f%%)  dead<=20: %d (%.0f%%)  alive at end: %d (%.0f%%)' % (label, n, a, 100 * a / n, b, 100 * b / n, c, 100 * c / n))


print('\n2. after a shed (first-found: every shed)')
shedrows = [outcome(s['g'], s['r']) for s in S]
tab(shedrows, 'all sheds')
for b in ('4-5', '6-9', '10+'):
    tab([outcome(s['g'], s['r']) for s in S if bucket(s['before']) == b], 'sheds len ' + b)
# a shed right after a previous shed in the same game is rare; also first shed per game only
first = {}
for s in S:
    if s['g']['id'] not in first:
        first[s['g']['id']] = s
tab([outcome(s['g'], s['r']) for s in first.values()], 'first shed per game')

# comparison: turns with queen >=4, nearest enemy head within 3, no queen split that round
print('  comparison turns: queen len>=4, enemy head within 3 (Manhattan torus), no queen split that round')
for lim in (3, 6):
    for b in ('4-5', '6-9', '10+', 'all'):
        rows = []
        gset = set()
        for g in G:
            for t in g['turns']:
                if t['ql'] >= 4 and t['nd'] <= lim and not t['split'] and (b == 'all' or bucket(t['ql']) == b):
                    rows.append(outcome(g, t['r']))
                    gset.add(g['id'])
        tab(rows, 'no-split within %d, len %s (%d games)' % (lim, b, len(gset)))
# shed turns by same-condition: what are shed turns' nd
nds = defaultdict(int)
for s in S:
    nds[s['nd']] += 1
print('  shed nearest-enemy distance histogram', dict(sorted(nds.items())))
n3 = sum(1 for s in S if s['nd'] <= 3)
print('  sheds with nearest enemy <=3:', n3, 'of', len(S))
tab([outcome(s['g'], s['r']) for s in S if s['nd'] <= 3], 'sheds with nearest <=3')
# split turns at all (queen splits that do not leave her at 2), within 3
oth = 0
for g in G:
    for t in g['turns']:
        if t['split']:
            oth += 1
print('  rounds with any queen split (all lengths):', oth)

# matched comparison: same distribution of queen length bucket and enemy-nearest-length
print('  comparison matched on nearest-enemy length>=2 & within 3 & ql>=4:')
for b in ('4-5', '6-9', '10+'):
    rows = [outcome(g, t['r']) for g in G for t in g['turns'] if t['ql'] >= 4 and t['nd'] <= 3 and t['nl'] >= 2 and not t['split'] and bucket(t['ql']) == b]
    tab(rows, 'no-split within 3, nl>=2, len ' + b)
    rows = [outcome(s['g'], s['r']) for s in S if s['nd'] <= 6 and s['nl'] >= 2 and bucket(s['before']) == b]
    tab(rows, 'shed (nearest<=6, nl>=2) len ' + b)

print('\n  final queen outcome')
fin = [s['g']['qfin'] for s in S]
alive = [s['g']['qfin'] for s in S if s['g']['qdead'] is None]
print('  sheds: final queen length when alive: n=%d mean=%.1f median=%s' % (len(alive), sum(alive) / max(1, len(alive)), sorted(alive)[len(alive) // 2] if alive else None))
print('  child alive at end: %d of %d; mean child final (alive) %.1f; mean child len at shed %.1f' % (
    sum(1 for s in S if s['child_final'] > 0), len(S), sum(s['child_final'] for s in S if s['child_final'] > 0) / max(1, sum(1 for s in S if s['child_final'] > 0)),
    sum(s['child_len'] for s in S) / len(S)))
# queen-final after shed vs queen length before
for b in ('4-5', '6-9', '10+'):
    ss = [s for s in S if bucket(s['before']) == b]
    if ss:
        print('   len %s: n=%d, queen end length mean %.1f; child end alive %d, child final mean-over-alive %.1f' % (
            b, len(ss), sum(s['g']['qfin'] for s in ss) / len(ss), sum(1 for s in ss if s['child_final'] > 0),
            sum(s['child_final'] for s in ss if s['child_final'] > 0) / max(1, sum(1 for s in ss if s['child_final'] > 0))))

print('\n3. games with shed vs without')


def wr(gs, label):
    n = len(gs)
    if not n:
        print(' ', label, 'N=0')
        return
    w = sum(g['win'] for g in gs)
    qa = sum(1 for g in gs if g['qdead'] is None)
    print('  %-28s N=%-4d wins %d (%.0f%%)  our queen alive at end %d (%.0f%%)' % (label, n, w, 100 * w / n, qa, 100 * qa / n))


wr([g for g in G if g['sheds']], 'with shed')
wr([g for g in G if not g['sheds']], 'without shed')
wr([g for g in G if any(s['before'] >= 10 for s in g['sheds'])], 'with shed from 10+')
wr([g for g in G if g['sheds'] and not any(s['before'] >= 10 for s in g['sheds'])], 'shed only <10')
for rk in (True, False):
    wr([g for g in G if g['sheds'] and g['ranked'] == rk], 'with shed ranked=%s' % rk)
    wr([g for g in G if not g['sheds'] and g['ranked'] == rk], 'without shed ranked=%s' % rk)
# confounder: queen reached length >=4 in game at all
q4 = [g for g in G if any(t['ql'] >= 4 for t in g['turns'])]
wr([g for g in q4 if g['sheds']], 'with shed (queen reached 4+)')
wr([g for g in q4 if not g['sheds']], 'without shed (queen reached 4+)')
# enemy queen alive state
print('  shed games: enemy queen alive at end', sum(1 for g in G if g['sheds'] and g['eqdead'] is None), 'of', sum(1 for g in G if g['sheds']))
print('  no-shed games: enemy queen alive at end', sum(1 for g in G if not g['sheds'] and g['eqdead'] is None), 'of', sum(1 for g in G if not g['sheds']))

print('\n4. sheds from 10+')
for s in S:
    if s['before'] >= 10:
        g = s['g']
        print(' g%d %s r%d  Q %d->2 child %d  nearest %s(len %s) n<=6=%d foes6=%s  EQ=%d  Qdead=%s Qfin=%d childfin=%d  %s' % (
            g['id'], g['ver'], s['r'], s['before'], s['child_len'], s['nd'], s['nl'], s['n6'], s['foes6'], s['eq'], g['qdead'], g['qfin'], s['child_final'], 'WIN' if g['win'] else 'LOSS'))
