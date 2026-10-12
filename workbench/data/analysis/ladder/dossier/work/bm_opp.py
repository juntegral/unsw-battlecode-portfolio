"""Scratch (diag-bigmap): what each side does on big layouts (job 3): length mix, who feeds the long dragon and the
queen and from what, splits, where short heads stand, what surrounds the longest dragon, what happens to queens,
and what a short dragon does next to a long enemy head.
Usage: python3 data/analysis/ladder/dossier/work/bm_opp.py [O|L|R] [min cells] [max cells]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median, mean

WORK = Path('data/analysis/ladder/dossier/work')
EB = ((0, 2), (3, 5), (6, 7), (8, 9))          # bands of 50 rounds: 0-149, 150-299, 300-399, 400-499
EBN = ('r0-149', 'r150-299', 'r300-399', 'r400-499')
ORG = ('natural', 'own fed', 'own other dead', 'enemy dead')


def load(src, lo, hi):
    rows = []
    for p in sorted(WORK.glob('bm_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            if lo < g['cells'] <= hi:
                rows.append(g)
    rows.sort(key=lambda g: g['gid'])
    return rows


def eb(b):
    for k, (a, c) in enumerate(EB):
        if a <= b <= c:
            return k
    return 3


def klass(d):
    c = d['c']
    if c == 'head-on':
        if not d['cross']:
            return 'mate head-on'
        return 'rammed' if d['role'] == 'hit' else 'rammer'
    if c == 'other body':
        return 'body:' + d.get('hit', '?')
    if c == 'no action':
        return 'fed' if d.get('fed') else 'no action, boxed' if d.get('free') == 0 else 'no action, other'
    return c


def at(g, r):
    return g['snap'][min(r, g['last'])]


def report(name, gs):
    n = len(gs)
    if not n:
        return
    print()
    print('=====', name, 'games', n, 'won', sum(g['result'] == 'win' for g in gs))
    for s, nm in ((0, 'OURS'), (1, 'THEIRS')):
        print('--', nm)
        o = s * 4
        for r in (100, 150, 200, 300, 400, 499):
            v = [at(g, r) for g in gs]
            qa = [x[o + 3] for x in v if x[o + 3] > 0]
            print('  r%d: count median %g mean %.1f; total mean %.0f; longest median %g mean %.1f (q1 %g q3 %g); queen alive %d of %d, mean length alive %.1f, median %g' % (
                r, median(x[o] for x in v), mean(x[o] for x in v), mean(x[o + 1] for x in v), median(x[o + 2] for x in v), mean(x[o + 2] for x in v),
                sorted(x[o + 2] for x in v)[len(v) // 4], sorted(x[o + 2] for x in v)[(3 * len(v)) // 4], len(qa), n, mean(qa) if qa else 0, median(qa) if qa else 0))
        # first round the longest reaches 10 / 15 / 20 for good
        for L in (10, 15, 20, 30):
            fr = []
            for g in gs:
                r = g['last']
                while r >= 0 and g['snap'][r][o + 2] >= L:
                    r -= 1
                fr.append(r + 1 if r + 1 <= g['last'] else 999)
            print('  longest at least %d for good from round: median %g; never %d of %d' % (L, median(fr), sum(1 for x in fr if x == 999), n))
        # length mix
        for g0 in (150, 200, 300, 400):
            c = [0] * 6
            for g in gs:
                for row in g['hist']:
                    if row[0] == g0:
                        for k in range(6):
                            c[k] += row[1 + s][k]
            print('  length mix at r%d a game (2 / 3 / 4 / 5-7 / 8-14 / 15+): %s' % (g0, ' '.join('%.1f' % (x / n) for x in c)))
        # eats
        e = defaultdict(int)
        for g in gs:
            for b, sd, kind, top, origin, cnt in g['eats']:
                if sd == s:
                    cls = 'queen' if kind == 'q' else 'long 10+' if kind == 10 else 'mid 5-9' if kind == 5 else 'short 2-4'
                    e[(eb(b), cls, origin)] += cnt
                    if top and kind != 'q':
                        e[(eb(b), 'the longest (not queen)', origin)] += cnt
        for cls in ('queen', 'long 10+', 'the longest (not queen)', 'mid 5-9', 'short 2-4'):
            print('  pearls eaten a game by %s:' % cls)
            for k in range(4):
                print('     %s: %s | all %.1f' % (EBN[k], '; '.join('%s %.1f' % (ORG[og], e[(k, cls, og)] / n) for og in range(4)), sum(e[(k, cls, og)] for og in range(4)) / n))
        # which deaths feed the 10+ / longest
        fb = defaultdict(lambda: [0, 0, 0, 0])
        dc = defaultdict(lambda: [0, 0, 0, 0])
        dl = defaultdict(lambda: [0, 0, 0, 0])
        for g in gs:
            for d in g['deaths']:
                if d['s'] == s:
                    k = eb(d['r'] // 50)
                    fb[klass(d)][k] += d['eatB'][s]
                    dc[klass(d)][k] += 1
                    dl[klass(d)][k] += d['L']
        print('  own deaths a game by class and band %s: count / length / drops eaten by own 10+ or longest' % (EBN,))
        for k in sorted(dc, key=lambda k: -sum(dl[k])):
            print('     %-18s %s' % (k, ' | '.join('%.1f / %.1f / %.1f' % (dc[k][b] / n, dl[k][b] / n, fb[k][b] / n) for b in range(4))))
        # splits
        sp = defaultdict(int)
        for g in gs:
            for b, sd, L, child, cnt in g['splits']:
                if sd == s:
                    sp[(eb(b), 'at 4' if L == 4 else 'at 5-7' if L <= 7 else 'at 8+')] += cnt
        print('  splits a game:', ' | '.join('%s: %s' % (EBN[k], ' '.join('%s %.1f' % (c, sp[(k, c)] / n) for c in ('at 4', 'at 5-7', 'at 8+'))) for k in range(4)))
        # positions
        for r in (50, 100, 150, 200, 300, 400):
            c = [0] * 6
            m = 0
            for g in gs:
                for row in g['pos']:
                    if row[0] == r:
                        m += 1
                        for k in range(6):
                            c[k] += row[1 + s][k]
            if m:
                sh = sum(c[:3]) or 1
                lg = sum(c[3:]) or 1
                print('  heads at r%d a game: short (2-4) own third %.1f mid %.1f other third %.1f (share other third %.2f); 5+ own %.1f mid %.1f other %.1f (share %.2f)' % (
                    r, c[0] / m, c[1] / m, c[2] / m, c[2] / sh, c[3] / m, c[4] / m, c[5] / m, c[5] / lg))
        # leader surroundings
        for a, b in ((150, 290), (300, 390), (400, 499)):
            v = [row[1 + s] for g in gs for row in g['lead'] if a <= row[0] <= b and row[1 + s] is not None and row[1 + s][1] >= 10]
            if v:
                print('  the longest (10+) in r%d-%d, %d samples: mean length %.1f; zone from own start %.2f; own heads within 5: %.2f (none %.2f); enemy heads within 5: %.2f (none %.2f); enemy shorts within 8: %.2f; is the queen %.2f' % (
                    a, b, len(v), mean(x[1] for x in v), mean((x[2] if s == 0 else 1 - x[2]) for x in v), mean(x[3] for x in v), sum(x[3] == 0 for x in v) / len(v), mean(x[4] for x in v), sum(x[4] == 0 for x in v) / len(v), mean(x[6] for x in v), mean(x[7] for x in v)))
        # queen deaths
        qd = [d for g in gs for d in g['deaths'] if d['s'] == s and d['q']]
        c = Counter(klass(d) for d in qd)
        print('  queen deaths %d of %d games: %s; round median %g; by r100 %d, r101-200 %d, r201-300 %d, later %d; length at death 2: %d, 3: %d, 4-9: %d, 10+: %d' % (
            len(qd), n, dict(c), median(d['r'] for d in qd) if qd else 0, sum(d['r'] <= 100 for d in qd), sum(100 < d['r'] <= 200 for d in qd), sum(200 < d['r'] <= 300 for d in qd), sum(d['r'] > 300 for d in qd),
            sum(d['L'] == 2 for d in qd), sum(d['L'] == 3 for d in qd), sum(4 <= d['L'] <= 9 for d in qd), sum(d['L'] >= 10 for d in qd)))
        rq = [d for d in qd if klass(d) == 'rammed']
        if rq:
            print('     queen rammed: rammer length at turn start %s; steps %s; paid %s; own heads within 5 of her: mean %.2f' % (dict(Counter(d['m']['L0'] for d in rq)), dict(Counter(d['m']['steps'] for d in rq)), dict(Counter(d['m']['paid'] for d in rq)), mean(d['o5'] for d in rq)))
        # rams on long dragons of this side
        for lo_, hi_ in ((5, 7), (8, 14), (15, 999)):
            v = [d for g in gs for d in g['deaths'] if d['s'] == s and klass(d) == 'rammed' and lo_ <= d['L'] <= hi_]
            if v:
                print('  rammed at length %d-%d: %.1f a game, length %.1f a game; rammer length %.1f, steps %.2f, paid %.2f; by band %s; drops eaten by own %.2f by other %.2f' % (
                    lo_, hi_, len(v) / n, sum(d['L'] for d in v) / n, mean(d['m']['L0'] for d in v), mean(d['m']['steps'] for d in v), mean(d['m']['paid'] for d in v),
                    ' '.join('%.1f' % (sum(1 for d in v if eb(d['r'] // 50) == k) / n) for k in range(4)), sum(d['eat'][s] for d in v) / sum(d['drop'] for d in v), sum(d['eat'][1 - s] for d in v) / sum(d['drop'] for d in v)))
        # contact: short non-queen next to an enemy head
        ct = defaultdict(lambda: [0, 0, 0])
        for g in gs:
            for b, sd, L0, Lt, g0, edge, oc, q, cnt, hit in g['contact']:
                if sd == s and not q and L0 <= 4:
                    tk = 'target 10+' if Lt == 10 else 'target 5-9' if Lt == 5 else 'target 2-4'
                    for key in ((tk, 'd%d' % g0, 'edge' if edge else 'no edge'), (tk, 'all d', 'all')):
                        ct[key][0] += cnt
                        ct[key][1] += cnt if oc == 'R' else 0
                        ct[key][2] += hit
        print('  short (2-4, not queen) turns starting within 3 tiles of an enemy head, a game: turns, share that ram, share rammed before the next turn')
        for key in sorted(ct):
            x = ct[key]
            print('     %-34s %.1f  %.3f  %.3f' % (' '.join(key), x[0] / n, x[1] / x[0], x[2] / x[0]))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'O'
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
    rows = load(src, lo, hi)
    if src == 'O':
        for arm in ('MAIN', 'B7', 'B7Q'):
            report(arm, [g for g in rows if g['arm'] == arm])
        for opp in sorted(set(g['opp'] for g in rows)):
            report('all arms vs ' + opp, [g for g in rows if g['opp'] == opp])
    else:
        report('ALL', rows)


if __name__ == '__main__':
    main()
