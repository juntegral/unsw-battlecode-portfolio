# Scratch (diag-drops): tables from dr_scan-*.jsonl. Actors: O ours, OO our opponents, R rank-1, RO rank-1's opponents.
# Every rate is formed inside a layout and then averaged over the 19 layouts with equal weight (as the scoreboard).
# Usage: python3 data/analysis/ladder/dossier/work/dr_agg.py <check|cls|bal|eat|all> [test] [lo hi]
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict, Counter

BASE = 'data/analysis/ladder/dossier/work/'
FILES = ['dr_scan-O0.jsonl', 'dr_scan-O1.jsonl', 'dr_scan-O2.jsonl', 'dr_scan-R0.jsonl', 'dr_scan-R1.jsonl', 'dr_scan-R2.jsonl']
ACTORS = ('O', 'OO', 'R', 'RO')


def games(test):
    for name in (['dr_scan-test.jsonl'] if test else FILES):
        with open(BASE + name) as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)


def actor(who, x):
    return who if x == 0 else who + 'O'


def cause(d, x):
    c, s, ps = d[5], d[2], d[6]
    own = s == x
    if c == 'H':
        return ('own, rammed by the other side' if own else 'theirs, rammed by us') if ps != s else ('own, same-team head-on' if own else 'theirs, same-team head-on')
    if c == 'M':
        return ('own, rammed one of theirs' if own else 'theirs, rammed one of ours') if ps != s else ('own, same-team head-on' if own else 'theirs, same-team head-on')
    if c == 'W':
        return 'own, wall' if own else 'theirs, wall'
    if c == 'O':
        return 'own, own body' if own else 'theirs, own body'
    if c == 'B':
        return ('own, another body' if own else 'theirs, another body')
    if c in ('N', 'I', 'U', 'Z'):
        return 'own, no valid action' if own else 'theirs, no valid action'
    return 'other'


def nd(v):
    return 0 if v <= 2 else 1 if v <= 5 else 2


def balance(pr, x):
    mine, theirs = pr[1 + x], pr[2 - x]
    return ('own head within 2', 'own head at 3-5', 'no own head within 5')[nd(mine)] + ' / ' + ('enemy within 2', 'enemy at 3-5', 'no enemy within 5')[nd(theirs)]


class Tab:
    # per actor and layout: class -> [pearls, eaten by the actor, eaten by the other side, nobody, sum wait when the actor eats]
    def __init__(self):
        self.c = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0, 0])))
        self.n = defaultdict(Counter)

    def add(self, a, lay, cls, pr, x):
        v = self.c[a][lay][cls]
        v[0] += 1
        self.n[a][lay] += 1
        if pr[7] == x:
            v[1] += 1
            v[4] += pr[8]
        elif pr[7] == 1 - x:
            v[2] += 1
        else:
            v[3] += 1

    def rows(self, a):
        lays = sorted(self.n[a])
        cl = sorted({k for l in lays for k in self.c[a][l]})
        out = {}
        for k in cl:
            w = sum(self.c[a][l][k][0] / self.n[a][l] for l in lays) / len(lays)
            e = sum(self.c[a][l][k][1] / self.n[a][l] for l in lays) / len(lays)
            o = sum(self.c[a][l][k][2] / self.n[a][l] for l in lays) / len(lays)
            n = sum(self.c[a][l][k][0] for l in lays)
            ate = sum(self.c[a][l][k][1] for l in lays)
            wait = sum(self.c[a][l][k][4] for l in lays)
            out[k] = (w, e, o, n, wait / ate if ate else 0.0)
        return out

    def show(self, title, pairs=(('O', 'R'), ('OO', 'RO'))):
        for a, b in pairs:
            ra, rb = self.rows(a), self.rows(b)
            ta, tb = sum(v[1] for v in ra.values()), sum(v[1] for v in rb.values())
            print()
            print('##', title, '|', a, 'against', b, '| share eaten: %.1f against %.1f, gap %+.1f' % (100 * ta, 100 * tb, 100 * (tb - ta)))
            print('class | %s: %% of drops, eats %%, other side %%, wait | %s: same | gap points = mix + rate' % (a, b))
            keys = sorted(set(ra) | set(rb), key=lambda k: -abs(rb.get(k, (0, 0))[1] - ra.get(k, (0, 0))[1]))
            for k in keys:
                wa, ea, oa, na, wta = ra.get(k, (0, 0, 0, 0, 0))
                wb, eb, ob, nb, wtb = rb.get(k, (0, 0, 0, 0, 0))
                sa = ea / wa if wa else 0.0
                sb = eb / wb if wb else 0.0
                mix = (wb - wa) * (sa + sb) / 2
                rate = (sb - sa) * (wa + wb) / 2
                print('%-58s | %5.1f %5.1f %5.1f %4.1f | %5.1f %5.1f %5.1f %4.1f | %+5.2f = %+5.2f %+5.2f | n %d %d' % (
                    k, 100 * wa, 100 * sa, 100 * (oa / wa if wa else 0), wta, 100 * wb, 100 * sb, 100 * (ob / wb if wb else 0), wtb,
                    100 * (eb - ea), 100 * mix, 100 * rate, na, nb))


def main():
    what = sys.argv[1]
    test = len(sys.argv) > 2 and sys.argv[2] == 'test'
    nums = [int(v) for v in sys.argv[2:] if v.isdigit()]
    lo, hi = (nums + [101, 300])[:2] if len(nums) >= 2 else (101, 300)
    t_cause, t_bal, t_cb, t_len = Tab(), Tab(), Tab(), Tab()
    ng = Counter()
    chk = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))
    eat = defaultdict(Counter)
    for gm in games(test):
        who, lay = gm['who'], gm['layout']
        ng[who] += 1
        for w in (0, 1):
            chk[who][lay][w * 2] += gm['chk'][w][0]
            chk[who][lay][w * 2 + 1] += gm['chk'][w][1]
        for d in gm['deaths']:
            if not (lo <= d[0] <= hi):
                continue
            for x in (0, 1):
                a = actor(who, x)
                cz = cause(d, x)
                own = d[2] == x
                for pr in d[12]:
                    t_cause.add(a, lay, cz, pr, x)
                    bl = balance(pr, x)
                    t_bal.add(a, lay, bl, pr, x)
                    t_cb.add(a, lay, ('own body: ' if own else 'their body: ') + bl, pr, x)
                    t_len.add(a, lay, ('own' if own else 'theirs') + ', length ' + ('2' if d[3] <= 2 else '3' if d[3] == 3 else '4' if d[3] == 4 else '5-9' if d[3] <= 9 else '10+'), pr, x)
                    if pr[7] == x:
                        eat[a]['n'] += 1
                        eat[a]['wait ' + ('0-1' if pr[8] <= 1 else '2-3' if pr[8] <= 3 else '4-10' if pr[8] <= 10 else '11+')] += 1
                        eat[a]['eater at death ' + ('1-2' if pr[10] <= 2 else '3-5' if pr[10] <= 5 else '6 or far or not yet born')] += 1
                        eat[a]['eater length ' + ('2' if pr[9] <= 2 else '3' if pr[9] == 3 else '4' if pr[9] == 4 else '5-9' if pr[9] <= 9 else '10+')] += 1
    print('games', dict(ng), 'window', lo, hi)
    if what in ('check', 'all'):
        for who in ('O', 'R'):
            lays = sorted(chk[who])
            for w, name in ((0, '0-100'), (1, '101-300')):
                vals = [chk[who][l][w * 2 + 1] / chk[who][l][w * 2] for l in lays if chk[who][l][w * 2]]
                print(who, name, 'neighbouring pearl not taken, layout mean %.2f%% over %d layouts; pooled %.2f%%' % (
                    100 * sum(vals) / len(vals), len(vals),
                    100 * sum(chk[who][l][w * 2 + 1] for l in lays) / max(1, sum(chk[who][l][w * 2] for l in lays))))
    if what in ('cls', 'all'):
        t_cause.show('whose body and how it died')
        t_len.show('length of the dead dragon')
    if what in ('bal', 'all'):
        t_bal.show('heads near the pearl at the death')
        t_cb.show('whose body x heads near')
    if what in ('eat', 'all'):
        for a in ACTORS:
            n = max(1, eat[a]['n'])
            print(a, ' '.join('%s %.1f%%' % (k, 100 * v / n) for k, v in sorted(eat[a].items()) if k != 'n'))


main()
