"""Extra counts for the report: exact binomial tails, queen paid sprints, queen death rate by length, self-kills beside the queen (r<=300),
queen eat rate, late decisive rams. Usage: extra.py"""
import json
from math import comb
from collections import Counter
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
def tail(w, n):
    return sum(comb(n, k) for k in range(0, w + 1)) / 2 ** n
pool = {}
for arm in ('h2h_mDone11_v8', 'h2h_mDone10_v8', 'h2h_mDone8_v5', 'h2h_mDone11_v5'):
    S = [json.loads(l) for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines()]
    w = sum(g['result'] == 'win' for g in S); l = sum(g['result'] == 'loss' for g in S)
    print('%s: %d games, %d-%d, draws %d; P(wins <= %d of %d at 50%%) = %.3f' % (arm, len(S), w, l, len(S) - w - l, w, w + l, tail(w, w + l)))
    for s, nm in ((0, 'NEW'), (1, 'old')):
        qp = [p for g in S for p in g['paids'] if p[1] == s and p[6] and not p[5]]
        print('   %s queen paid moves (not a ram): %d, segments %d, from length 3: %d' % (nm, len(qp), sum(p[3] for p in qp), sum(1 for p in qp if p[2] == 3)))
    tf = HERE / ('turns-%s.jsonl' % arm)
    if not tf.exists():
        continue
    T = [json.loads(l) for l in tf.read_text().splitlines()]
    if 'dl' not in T[0]:
        continue
    print('   turns file: %d games' % len(T))
    for s, nm in ((0, 'NEW'), (1, 'old')):
        alive = sum(1 for g in T for L in g['qlen'][s][:301] if L)
        near = [x for g in T for x in g['dl'] if x[1] == s and not x[6] and x[0] <= 300 and x[5] and x[3] in (0, 1) and 0 <= x[4] <= 2]
        print('   %s r<=300: queen-alive rounds %d, non-queen self-kills (wall/own body) within 2 of the own queen %d (length %d) = %.2f per 100 queen rounds' % (nm, alive, len(near), sum(x[2] for x in near), 100 * len(near) / max(1, alive)))
        rounds = Counter(); deaths = Counter()
        for g in T:
            q = g['qlen'][s]
            for r in range(len(q) - 1):
                if q[r]:
                    rounds[min(q[r], 5)] += 1
                    if not q[r + 1]:
                        deaths[min(q[r], 5)] += 1
        print('   %s queen death rate per 100 rounds at length 2/3/4/5+: %s' % (nm, ' '.join('%.2f (%d/%d)' % (100 * deaths[L] / max(1, rounds[L]), deaths[L], rounds[L]) for L in (2, 3, 4, 5))))
        if arm.endswith('v8'):
            for L in (2, 3, 4, 5):
                pool.setdefault((nm, L), [0, 0]); pool[(nm, L)][0] += deaths[L]; pool[(nm, L)][1] += rounds[L]
        A = Counter()
        for g in T:
            for k, v in g['T'].items():
                sd, role, lc, ph, pd, foe = k.split('|')
                if int(sd) == s:
                    A[(role, ph, 't')] += v[0]; A[(role, ph, 'e')] += v[2]
                    if role == 'o' and lc in '234':
                        A[('small', ph, 't')] += v[0]; A[('small', ph, 'e')] += v[2]
        print('   %s pearls per 100 turns: queen r1-50 %.1f, r51-100 %.1f; non-queen of 2-4 r1-50 %.1f, r51-100 %.1f, r101-350 %.1f; all non-queen r101-350 %.1f' % (
            nm, 100 * A[('q', 'a', 'e')] / max(1, A[('q', 'a', 't')]), 100 * A[('q', 'b', 'e')] / max(1, A[('q', 'b', 't')]),
            100 * A[('small', 'a', 'e')] / max(1, A[('small', 'a', 't')]), 100 * A[('small', 'b', 'e')] / max(1, A[('small', 'b', 't')]),
            100 * A[('small', 'c', 'e')] / max(1, A[('small', 'c', 't')]), 100 * A[('o', 'c', 'e')] / max(1, A[('o', 'c', 't')])))
print('queen death rate pooled over the two arms against one8:', {k: '%.2f per 100 (%d/%d)' % (100 * v[0] / v[1], v[0], v[1]) for k, v in sorted(pool.items())})
