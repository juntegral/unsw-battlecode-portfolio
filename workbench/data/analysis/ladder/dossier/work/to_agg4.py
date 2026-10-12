# Scratch (diag-topopen): tables from to_scan2-*.jsonl (pearl beside the head, births, children, portal sides, deaths).
# Usage: python3 to_agg4.py p1 <size|all> [maxround] | births <size|all> | kids <size|all> | gate <size|all> | dead <size|all> | ex <class>
import sys, json
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean, median

W = Path('data/analysis/ladder/dossier/work')
NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad', 91: 'SSS', 264: 'ftm', 842: 'horse', 1119: 'ours'}
LABS = ['aAah today', 'larp today', 'Cutlery today', 'chad today', 'top today', 'Cutlery old', 'SSS old', 'ftm old', 'horse old',
        'ours today', 'ours B7Q', 'ours vs top', 'ours ladder', 'our opp today', 'T3 opp', 'larp vs us', 'Cutlery vs us', 'aAah vs us', 'top vs us']
CLASSES = ('open', 'notail', 'tight', 'trapped', 'mate', 'enemy', 'portal')


def size(c):
    return 'S' if c <= 700 else 'M' if c <= 1200 else 'L'


def rows_all():
    out, seen = [], set()
    for f in sorted(W.glob('to_scan2-*.jsonl')):
        if 'test' in f.name:
            continue
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            g = json.loads(line)
            if 'error' in g or g['game'] in seen:
                continue
            seen.add(g['game'])
            src = g['src'][:2]
            for s in 'ut':
                d = g['sides'][s]
                team = d['team']
                labs = []
                if src == 'T3':
                    if team in NAMES and team != 1119:
                        labs += [NAMES[team] + ' today', 'top today']
                    else:
                        labs.append('T3 opp')
                elif src == 'T1':
                    labs.append((NAMES[team] + ' old') if s == 'u' and team in NAMES else 'T1 opp')
                elif src in ('OQ', 'OM', 'OB'):
                    if s == 'u':
                        labs.append('ours today')
                        if src == 'OQ':
                            labs.append('ours B7Q')
                    else:
                        labs.append('our opp today')
                elif src == 'OT':
                    labs.append('ours vs top' if s == 'u' else (NAMES.get(team, 'top') + ' vs us'))
                else:
                    labs.append('ours ladder' if s == 'u' else 'ladder opp')
                for lab in labs:
                    out.append(dict(lab=lab, g=g, d=d, s=s, size=size(g['cells'])))
    return out


def pct(a, b, nd=0):
    return '-' if not b else ('%.' + str(nd) + 'f') % (100.0 * a / b)


def pick(rows, l, sz):
    return [r for r in rows if r['lab'] == l and (sz == 'all' or r['size'] == sz)]


def p1(rows, sz, maxr):
    print('== pearl one step from the head at the turn start, dragons of length 4 or less, r0-%d, size %s' % (maxr, sz))
    print('   per game: turns; ate / moved elsewhere / split / died %; then per class: turns a game, moved elsewhere % of (ate + moved)')
    for l in LABS:
        rs = pick(rows, l, sz)
        if len(rs) < 3:
            continue
        n = len(rs)
        t = [p for r in rs for p in r['d']['p1'] if p[0] <= maxr and not p[3]]
        tq = [p for r in rs for p in r['d']['p1'] if p[0] <= maxr and p[3]]
        act = Counter(p[4] for p in t)
        line = []
        for c in CLASSES:
            x = [p for p in t if p[5] == c]
            e = sum(1 for p in x if p[4] == 'E')
            m = sum(1 for p in x if p[4] == 'M')
            line.append('%s %.1f:%s' % (c, len(x) / n, pct(m, e + m)))
        e = act['E']
        m = act['M']
        print('   %-14s n=%3d  %.1f turns; %s / %s / %s / %s | moved %s%% of ate+moved = %.1f a game | %s | queen: %.1f turns, moved %s%%' % (
            l, n, len(t) / n, pct(act['E'], len(t)), pct(act['M'], len(t)), pct(act['S'], len(t)), pct(act['D'], len(t)), pct(m, e + m, 1), m / n,
            '  '.join(line), len(tq) / n, pct(sum(1 for p in tq if p[4] == 'M'), sum(1 for p in tq if p[4] in 'EM'))))
        dec = [p for p in t if p[4] == 'M']
        if dec:
            later = Counter()
            for p in dec:
                if p[12] == 'n':
                    later['never by r100'] += 1
                elif p[12] == 's':
                    later['same dragon, %s' % ('next 2 rounds' if p[13] <= 2 else 'later')] += 1
                elif p[12] == 'm':
                    later['a mate, %s' % ('next 2 rounds' if p[13] <= 2 else 'later')] += 1
                else:
                    later['the enemy'] += 1
            print('        what became of the pearl it left: %s' % '; '.join('%s %s%%' % (k, pct(v, len(dec))) for k, v in later.most_common()))
            for c in CLASSES:
                x = [p for p in dec if p[5] == c]
                if len(x) >= 10:
                    lt = Counter('enemy' if p[12] == 'e' else 'never' if p[12] == 'n' else 'own side within 2' if p[13] <= 2 else 'own side later' for p in x)
                    print('          %-8s %.2f a game: %s' % (c, len(x) / n, '; '.join('%s %s%%' % (k, pct(v, len(x))) for k, v in lt.most_common())))
        for L in (2, 3, 4):
            x = [p for p in t if p[2] == L]
            e = sum(1 for p in x if p[4] == 'E')
            m = sum(1 for p in x if p[4] == 'M')
            sp = sum(1 for p in x if p[4] == 'S')
            print('        length %d: %.1f turns a game, moved elsewhere %s%% of ate+moved, split %s%%' % (L, len(x) / n, pct(m, e + m, 1), pct(sp, len(x), 1)))


def births(rows, sz):
    print('== natural pearls born r1-60 by path steps from the side nearest head at birth (bodies ignored), size', sz)
    print('   class: share of births %, eaten by this side within 10 rounds %, by r100 %, eaten by the other side by r100 %')
    bands = ((0, 1, '0-1'), (2, 3, '2-3'), (4, 7, '4-7'), (8, 12, '8-12'), (13, 99, '13+'))
    for l in LABS:
        rs = pick(rows, l, sz)
        if len(rs) < 3:
            continue
        cnt = defaultdict(lambda: [0, 0, 0, 0])
        tot = 0
        for r in rs:
            mine = r['s']
            for b in r['g']['births']:
                if b[0] > 60:
                    continue
                d = b[1] if mine == 'u' else b[2]
                band = next(nm for lo, hi, nm in bands if lo <= d <= hi)
                c = cnt[band]
                c[0] += 1
                tot += 1
                if b[3] == mine:
                    c[2] += 1
                    if b[4] - b[0] <= 10:
                        c[1] += 1
                elif b[3] != 'n':
                    c[3] += 1
        print('   %-14s n=%3d births %.0f a game | %s' % (l, len(rs), tot / len(rs), '  '.join(
            '%s: %s, %s, %s, %s' % (nm, pct(cnt[nm][0], tot), pct(cnt[nm][1], cnt[nm][0]), pct(cnt[nm][2], cnt[nm][0]), pct(cnt[nm][3], cnt[nm][0])) for lo, hi, nm in bands)))


def kids(rows, sz):
    print('== children born r1-40, size', sz)
    for l in LABS:
        rs = pick(rows, l, sz)
        if len(rs) < 3:
            continue
        ks = [k for r in rs for k in r['d']['kids'] if 1 <= k[0] <= 40]
        if not ks:
            continue
        n = len(ks)

        def fed(x, w):
            return sum(1 for k in x if k[5] is not None and k[5] - k[0] <= w)

        def dead(x, w):
            return sum(1 for k in x if k[6] is not None and k[6] - k[0] <= w)
        small = [k for k in ks if k[2] < 8]
        mid = [k for k in ks if 8 <= k[2] < 30]
        big = [k for k in ks if k[2] >= 30]
        near = [k for k in ks if k[4] <= 3]
        far = [k for k in ks if k[4] >= 9]
        boxed = sum(1 for k in ks if k[6] is not None and k[6] - k[0] <= 10 and k[7] and k[7].endswith('0'))
        print('   %-14s n=%3d %.1f a game | room under 8: %s%% (dead in 10: %s%%), 8-29: %s%% (%s%%), 30+: %s%% (%s%%) | pearl within 3 steps at birth %s%% (fed in 10: %s%%), none within 6: %s%% (fed in 10: %s%%, in 20: %s%%) | fed in 10 %s%%, dead in 10 %s%% (with no free tile %s%%)' % (
            l, len(rs), n / len(rs), pct(len(small), n), pct(dead(small, 10), len(small)), pct(len(mid), n), pct(dead(mid, 10), len(mid)), pct(len(big), n), pct(dead(big, 10), len(big)),
            pct(len(near), n), pct(fed(near, 10), len(near)), pct(len(far), n), pct(fed(far, 10), len(far)), pct(fed(far, 20), len(far)), pct(fed(ks, 10), n), pct(dead(ks, 10), n), pct(boxed, n)))


def gate(rows, sz):
    print('== turns that start beside a portal edge with no pearl beside the head: turns a game, stepped through %, size', sz)
    for l in LABS:
        rs = [r for r in pick(rows, l, sz) if r['g']['pairs'] > 0]
        if len(rs) < 3:
            continue
        tot = defaultdict(lambda: [0, 0])
        for r in rs:
            for k, v in r['d']['gate'].items():
                tot[k][0] += v[0]
                tot[k][1] += v[1]
        cells = []
        for kind in 'sql':
            for wdw in range(4):
                v = tot['%d|%s' % (wdw, kind)]
                cells.append('%s%s %.1f:%s' % (kind, ('r0-20', 'r21-40', 'r41-60', 'r61-100')[wdw], v[0] / len(rs), pct(v[1], v[0])))
        print('   %-14s n=%3d | %s' % (l, len(rs), '  '.join(cells)))


def dead(rows, sz):
    print('== deaths r0-60 a game, size', sz, ': on its own turn with no free tile beside the head / with a free tile (by cause) / not its turn')
    for l in LABS:
        rs = pick(rows, l, sz)
        if len(rs) < 3:
            continue
        n = len(rs)
        dl = [d for r in rs for d in r['d']['dead'] if d[0] <= 60]
        boxed = [d for d in dl if d[3] == 0]
        free = [d for d in dl if d[3] > 0]
        nott = [d for d in dl if d[3] < 0]
        fc = Counter(d[2] for d in free)
        young = sum(1 for d in boxed if d[5] and d[4] <= 3)
        print('   %-14s n=%3d all %.1f | boxed in %.1f (of them born 3 rounds or less before: %.1f) | with a free tile %.1f: %s | not its turn %.1f' % (
            l, n, len(dl) / n, len(boxed) / n, young / n, len(free) / n, ' '.join('%s %.1f' % (k, v / n) for k, v in fc.most_common()), len(nott) / n))


def ex(rows, cls, lab, sz):
    k = 0
    for r in rows:
        if r['lab'] != lab or (sz != 'all' and r['size'] != sz):
            continue
        for p in r['d']['p1']:
            if p[5] == cls and p[4] == 'M' and not p[3] and p[0] <= 60:
                print(r['g']['game'], r['g']['map'], 'round', p[0], 'id', p[1], 'len', p[2], 'head', (p[15], p[16]), 'pearl', (p[17], p[18]), 'room', p[6], 'tail', p[7], 'pearls beside', p[8], 'enemy', p[9], 'mate', p[10], 'later', p[12], p[13])
                k += 1
                if k >= 40:
                    return


def main():
    rows = rows_all()
    maps = [a[4:] for a in sys.argv if a.startswith('map=')]
    nomaps = [a[6:] for a in sys.argv if a.startswith('nomap=')]
    if maps:
        rows = [r for r in rows if any(r['g']['map'].startswith(m) for m in maps)]
    if nomaps:
        rows = [r for r in rows if not any(r['g']['map'].startswith(m) for m in nomaps)]
    sys.argv = [a for a in sys.argv if not a.startswith('map=') and not a.startswith('nomap=')]
    mode = sys.argv[1]
    if mode == 'ex':
        ex(rows, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'ours B7Q', sys.argv[4] if len(sys.argv) > 4 else 'all')
        return
    sz = sys.argv[2] if len(sys.argv) > 2 else 'all'
    if mode == 'p1':
        p1(rows, sz, int(sys.argv[3]) if len(sys.argv) > 3 else 60)
    elif mode == 'births':
        births(rows, sz)
    elif mode == 'kids':
        kids(rows, sz)
    elif mode == 'gate':
        gate(rows, sz)
    elif mode == 'dead':
        dead(rows, sz)


main()
