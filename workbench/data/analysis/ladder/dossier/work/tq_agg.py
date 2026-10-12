"""Scratch (diag-theirqueen): tables from tq_scan-*.jsonl. Usage: python3 tq_agg.py online | ladder
Groups online: arm (MAIN m1+m2, B7 b1+b2, B7Q q1) x queen (ours all, ours vs Bob, ours vs Quiz, Bob's, Quiz's)."""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

W = Path('data/analysis/ladder/dossier/work')
F = dict(r=0, head=1, L=2, ds=3, o3=4, o5=5, e3m=6, e5m=7, ep3=8, ne=9, neL=10, nem=11, nom=12, kc=13, fx=14, pk=15, mn=16, inr=17, ob2=18,
         act=19, steps=20, La=21, ate=22, end=23, da=24, died=25, hit=26, ep3n=27, child=28, sep=29, db=30, ep5n=31, o3c=32)
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q'}
CAUSE = ('wall', 'own body', 'other body', 'head-on', 'other')


def load(tags):
    games = []
    for t in tags:
        p = W / ('tq_scan-%s.jsonl' % t)
        if p.exists():
            games += [json.loads(x) for x in p.read_text().splitlines() if x]
    return games


def groups_online(games):
    out = defaultdict(list)
    for g in games:
        arm = ARM[g['label']]
        opp = 'Bob' if g['opp'].startswith('Big') else 'Quiz'
        out[arm + ' ours'].append((g, 0))
        out[arm + ' ours/' + opp].append((g, 0))
        out[arm + ' ' + opp].append((g, 1))
        out[arm + ' theirs'].append((g, 1))
    order = [a + ' ' + q for a in ('MAIN', 'B7', 'B7Q') for q in ('ours', 'theirs', 'ours/Bob', 'Bob', 'ours/Quiz', 'Quiz')]
    return [(k, out[k]) for k in order if out[k]]


def groups_ladder(games):
    out = defaultdict(list)
    for g in games:
        if g['label'] == 'ladder':
            out['ours ladder'].append((g, 0))
            out['ladder opp'].append((g, 1))
        else:
            out['rank1'].append((g, 0))
            out['rank1 opp'].append((g, 1))
    return [(k, out[k]) for k in ('ours ladder', 'ladder opp', 'rank1', 'rank1 opp') if out[k]]


def pct(n, d):
    return '-' if not d else '%.0f%%' % (100.0 * n / d)


def f1(n, d):
    return '-' if not d else '%.1f' % (n / d)


def f2(n, d):
    return '-' if not d else '%.2f' % (n / d)


def qstate(g, s, cp):
    if cp == 'end' or g['last'] <= cp:
        return g['final'][s][0]
    return g['snaps'][str(cp)][s][0]


def table(groups):
    names = [k for k, _ in groups]
    rows = []

    def add(label, fn):
        rows.append([label] + [fn(v) for _, v in groups])

    add('games', lambda v: str(len(v)))
    add('focus-side wins', lambda v: str(sum(1 for g, s in v if g['win'] == 1)))
    for cp in (50, 100, 150, 300, 'end'):
        add('alive r%s' % cp, lambda v, cp=cp: '%d (%s)' % (sum(1 for g, s in v if qstate(g, s, cp) > 0), pct(sum(1 for g, s in v if qstate(g, s, cp) > 0), len(v))))
    for cp in (50, 100, 150, 300, 'end'):
        def ml(v, cp=cp):
            ls = [qstate(g, s, cp) for g, s in v]
            ls = [x for x in ls if x > 0]
            return f1(sum(ls), len(ls)) + '/' + (str(int(median(ls))) if ls else '-')
        add('len alive r%s mean/med' % cp, ml)

    def turns(v, lo=0, hi=9999):
        for g, s in v:
            for t in g['recs'][s]:
                if lo <= t[0] <= hi:
                    yield t

    add('queen turns', lambda v: str(sum(1 for _ in turns(v))))

    def lshare(v, lo, hi):
        c = Counter()
        for t in turns(v, lo, hi):
            L = t[F['L']]
            c['2' if L == 2 else '3' if L == 3 else '4' if L == 4 else '5-8' if L <= 8 else '9+'] += 1
        n = sum(c.values())
        return '/'.join(pct(c[k], n) for k in ('2', '3', '4', '5-8', '9+'))
    add('turn share L2/3/4/5-8/9+ r0-300', lambda v: lshare(v, 0, 300))
    add('turn share L2/3/4/5-8/9+ r0-100', lambda v: lshare(v, 0, 100))

    def spl(v):
        sp = [x for g, s in v for x in g['splits'][s]]
        if not sp:
            return '0'
        return '%s/g; r med %d; by r100 %s/g' % (f1(len(sp), len(v)), median(x[0] for x in sp), f1(sum(1 for x in sp if x[0] <= 100), len(v)))
    add('splits', spl)

    def splba(v):
        c = Counter()
        for g, s in v:
            for x in g['splits'][s]:
                if x[0] <= 300:
                    c['%d>%d' % (min(x[1], 9), min(x[2], 9))] += 1
        return ' '.join('%s:%d' % kv for kv in c.most_common(6))
    add('splits r0-300 before>after (9=9+)', splba)

    def dsat(v, cp):
        xs = []
        for g, s in v:
            for t in g['recs'][s]:
                if t[0] == cp:
                    xs.append((t[F['ds']], t[F['ds']] / (g['w'] // 2 + g['h'] // 2)))
        return '%s (%s)' % (f1(sum(x[0] for x in xs), len(xs)), f2(sum(x[1] for x in xs), len(xs)))
    for cp in (10, 25, 50, 100, 150, 300):
        add('dist from start r%d tiles (norm)' % cp, lambda v, cp=cp: dsat(v, cp))

    def area(v, lo, hi):
        xs = []
        for g, s in v:
            ts = [t for t in g['recs'][s] if lo <= t[0] < hi]
            if len(ts) >= hi - lo:
                xs.append(len(set(t[F['end']] for t in ts)))
        return '%s n%d' % (f1(sum(xs), len(xs)), len(xs))
    for lo in (0, 50, 100, 150, 250):
        add('distinct tiles r%d-%d' % (lo, lo + 49), lambda v, lo=lo: area(v, lo, lo + 50))

    def mean(v, key, lo=0, hi=9999, cond=None):
        n = d = 0
        for t in turns(v, lo, hi):
            if cond is None or cond(t):
                n += t[F[key]]
                d += 1
        return f2(n, d)

    def share(v, cond, lo=0, hi=9999, base=None):
        n = d = 0
        for t in turns(v, lo, hi):
            if base is None or base(t):
                d += 1
                n += 1 if cond(t) else 0
        return pct(n, d) + ' n%d' % d
    for lo, hi in ((0, 100), (101, 300)):
        add('own heads <=3 / <=5 r%d-%d' % (lo, hi), lambda v, lo=lo, hi=hi: mean(v, 'o3', lo, hi) + ' / ' + mean(v, 'o5', lo, hi))
        add('no own head <=5 r%d-%d' % (lo, hi), lambda v, lo=lo, hi=hi: share(v, lambda t: t[F['o5']] == 0, lo, hi))
        add('own body cells <=2 (any) r%d-%d' % (lo, hi), lambda v, lo=lo, hi=hi: share(v, lambda t: t[F['ob2']] > 0, lo, hi))
        add('mate nearer the nearest enemy (enemy <=8) r%d-%d' % (lo, hi), lambda v, lo=lo, hi=hi: share(v, lambda t: t[F['mn']] == 1, lo, hi, lambda t: t[F['mn']] >= 0))
        add('enemy head <=8 tiles, share of turns r%d-%d' % (lo, hi), lambda v, lo=lo, hi=hi: share(v, lambda t: t[F['mn']] >= 0, lo, hi))

    def per100(v, key, lo=0, hi=9999):
        n = d = 0
        for t in turns(v, lo, hi):
            n += t[F[key]]
            d += 1
        return f1(100.0 * n, d)
    for lo, hi in ((0, 9999), (0, 100), (101, 300)):
        add('enemy heads <=3 steps /100 turns r%d-%d' % (lo, hi), lambda v, lo=lo, hi=hi: per100(v, 'ep3n', lo, hi))
        add('turns with one <=3 steps r%d-%d' % (lo, hi), lambda v, lo=lo, hi=hi: share(v, lambda t: t[F['ep3n']] > 0, lo, hi))
        add('enemy heads <=5 steps /100 turns r%d-%d' % (lo, hi), lambda v, lo=lo, hi=hi: per100(v, 'ep5n', lo, hi))
        add('turns with her head in a head true reach r%d-%d' % (lo, hi), lambda v, lo=lo, hi=hi: share(v, lambda t: t[F['inr']] > 0, lo, hi))
    add('games with any turn <=3 steps', lambda v: '%d' % sum(1 for g, s in v if any(t[F['ep3n']] > 0 for t in g['recs'][s])))

    def respond(v):
        c = Counter()
        for t in turns(v):
            if t[F['ep3n']] <= 0:
                continue
            c['n'] += 1
            paid = t[F['act']] == 0 and t[F['La']] > 0 and t[F['L']] + t[F['ate']] - t[F['La']] > 0
            if t[F['died']]:
                c['died on her move'] += 1
            elif t[F['act']] == 1:
                c['split'] += 1
            elif t[F['act']] == 2:
                c['none'] += 1
            elif t[F['steps']] >= 2:
                c['sprint'] += 1
                c['sprint paid'] += 1 if paid else 0
                c['sprint away'] += 1 if t[F['da']] > t[F['db']] else 0
            elif t[F['da']] > t[F['db']]:
                c['step away'] += 1
            elif t[F['da']] == t[F['db']]:
                c['step level'] += 1
            else:
                c['step closer'] += 1
            c['hit after'] += t[F['hit']]
        n = c['n']
        return 'n%d: away %s level %s closer %s sprint %s (paid %d, away %d) split %s died %s | hit before next turn %s' % (
            n, pct(c['step away'], n), pct(c['step level'], n), pct(c['step closer'], n), pct(c['sprint'], n), c['sprint paid'], c['sprint away'],
            pct(c['split'], n), pct(c['died on her move'], n), pct(c['hit after'], n))
    add('on turns with a head <=3 steps', respond)

    def respond_len(v):
        out = []
        for name, lo, hi in (('L2', 2, 2), ('L3', 3, 3), ('L4+', 4, 999)):
            n = h = sp = 0
            for t in turns(v):
                if t[F['ep3n']] > 0 and lo <= t[F['L']] <= hi:
                    n += 1
                    h += t[F['hit']]
                    sp += 1 if t[F['steps']] >= 2 else 0
            out.append('%s n%d hit %s sprint %s' % (name, n, pct(h, n), pct(sp, n)))
        return '; '.join(out)
    add('same, by her length', respond_len)
    add('all turns: sprint (2+ steps)', lambda v: share(v, lambda t: t[F['steps']] >= 2))
    add('all turns: split', lambda v: share(v, lambda t: t[F['act']] == 1))
    add('all turns: head did not move', lambda v: share(v, lambda t: t[F['end']] == t[F['head']]))
    add('pearls eaten /100 turns r0-100; r101-300; all', lambda v: per100(v, 'ate', 0, 100) + '; ' + per100(v, 'ate', 101, 300) + '; ' + per100(v, 'ate'))
    add('pearls eaten per game', lambda v: f1(sum(t[F['ate']] for t in turns(v)), len(v)))
    add('turns in a one-entrance pocket (<=60 cells)', lambda v: share(v, lambda t: t[F['pk']] > 0))
    add('games: start tile in such a pocket', lambda v: '%d' % sum(1 for g, s in v if g['spocket'][s] > 0))
    add('games: start region closed (<half map)', lambda v: '%d' % sum(1 for g, s in v if g['scomp'][s] * 2 < g['cells']))
    add('turns on a tile with kelp on 2+ sides', lambda v: share(v, lambda t: t[F['kc']] >= 2))
    add('mean tiles within 3 steps (25 = open)', lambda v: mean(v, 'o3c'))
    add('mean free neighbour tiles', lambda v: mean(v, 'fx'))
    add('enemy head <=3 tiles but kelp between (of turns with one <=3 tiles)', lambda v: share(v, lambda t: t[F['sep']] > 0, 0, 9999, lambda t: t[F['e3m']] > 0))
    add('nearest enemy head, mean tiles r0-100; r101-300', lambda v: mean(v, 'nem', 0, 100) + '; ' + mean(v, 'nem', 101, 300))
    add('nearest own head, mean tiles r0-100; r101-300', lambda v: mean(v, 'nom', 0, 100) + '; ' + mean(v, 'nom', 101, 300))

    def fates(v):
        c = Counter()
        for g, s in v:
            f = g['fate'][s]
            if f is None:
                c['alive'] += 1
            elif f['own_move']:
                c['own: ' + CAUSE[min(f['reason'], 4)]] += 1
            else:
                c['rammed' if f['mside'] != s else 'own side'] += 1
        return ' '.join('%s:%d' % kv for kv in c.most_common())
    add('fate', fates)

    def rammed(v):
        fs = [g['fate'][s] for g, s in v if g['fate'][s] is not None and not g['fate'][s]['own_move'] and g['fate'][s]['mside'] != s]
        if not fs:
            return '0'
        cl = Counter(min(f['L'], 5) for f in fs)
        return 'n%d her L2:%d L3:%d L4:%d L5+:%d; r med %d; mover L mean %s; no own head <=5: %d; ds mean %s' % (
            len(fs), cl[2], cl[3], cl[4], cl[5], median(f['r'] for f in fs), f1(sum(f['mL'] for f in fs), len(fs)),
            sum(1 for f in fs if f['o5'] == 0), f1(sum(f['ds'] for f in fs), len(fs)))
    add('rammed queens', rammed)
    add('she rams an enemy head (times; victim queen)', lambda v: '%d; %d' % (sum(len(g['attacks'][s]) for g, s in v), sum(x[3] for g, s in v for x in g['attacks'][s])))
    add('enemy dies on her body', lambda v: '%d' % sum(len(g['bodykills'][s]) for g, s in v))

    def chance(v):
        # chances AT this queen: movers of the other side
        ch = [(g['game'], x) for g, s in v for x in g['chances'] if x[1] == 1 - s]
        short = [x for _, x in ch if x[2] <= 4]
        return 'turns %d games %d taken %d | short(<=4) %d/%d' % (len(ch), len(set(a for a, _ in ch)), sum(x[4] for _, x in ch), sum(x[4] for x in short), len(short))
    add('sure chances at her head (enemy mover, <=3 free steps)', chance)

    def nearq(v):
        n3 = sum(g['near'][1 - s][0] for g, s in v)
        n5 = sum(g['near'][1 - s][1] for g, s in v)
        qt = sum(len(g['recs'][s]) for g, s in v)
        return '%s / %s' % (f1(100.0 * n3, qt), f1(100.0 * n5, qt))
    add('enemy dragon-turns starting <=3 / <=5 tiles from her head, per 100 of her turns', nearq)
    width = max(len(r[0]) for r in rows)
    print(' | '.join(['measure'.ljust(width)] + names))
    for r in rows:
        print(' | '.join([r[0].ljust(width)] + r[1:]))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'online'
    if mode == 'online':
        games = load(('m1', 'm2', 'b1', 'b2', 'q1', 'q2', 'm3'))
        groups = groups_online(games)
    else:
        games = load(('L0', 'L1', 'T0', 'T1'))
        groups = groups_ladder(games)
    sel = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    if sel:
        groups = [(k, v) for k, v in groups if any(k == x or k.startswith(x + ' ') for x in sel)]
    table(groups)


main()
