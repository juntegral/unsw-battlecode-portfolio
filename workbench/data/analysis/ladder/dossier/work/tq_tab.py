"""Scratch (diag-theirqueen): the report's tables as markdown, straight from tq_scan-*.jsonl.
Usage: python3 tq_tab.py A | B | C"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

W = Path('data/analysis/ladder/dossier/work')
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q'}
L, DS, O3, O5, ACT, STEPS, ATE, END, DA, DIED, HIT, EP3N, DB, EP5N, KC, PK, MN = 2, 3, 4, 5, 19, 20, 22, 23, 24, 25, 26, 27, 30, 31, 13, 15, 16


def load(tags):
    games = []
    for t in tags:
        p = W / ('tq_scan-%s.jsonl' % t)
        if p.exists():
            games += [json.loads(x) for x in p.read_text().splitlines() if x]
    return games


def pc(n, d):
    return '-' if not d else '%.0f%%' % (100.0 * n / d)


def f1(n, d):
    return '-' if not d else '%.1f' % (n / d)


def qlen(g, s, cp):
    if cp == 'end' or g['last'] <= cp:
        return g['final'][s][0]
    return g['snaps'][str(cp)][s][0]


def leash(g):
    return min(8, (g['w'] + g['h']) // 8)


def turns(v, lo=0, hi=9999):
    for g, s in v:
        for t in g['recs'][s]:
            if lo <= t[0] <= hi:
                yield t


def table_a(cols):
    rows = []

    def add(name, fn):
        rows.append('| ' + name + ' | ' + ' | '.join(fn(v) for _, v in cols) + ' |')
    print('| measure | ' + ' | '.join(k for k, _ in cols) + ' |')
    print('|---|' + '---|' * len(cols))
    add('games; won by that side', lambda v: '%d; %d' % (len(v), sum(1 for g, s in v if g['win'] is not None and (g['win'] == 1) == (s == 0))))
    add('queen alive at the end of r50; r100; r150; r300; game', lambda v: '; '.join(str(sum(1 for g, s in v if qlen(g, s, cp) > 0)) for cp in (50, 100, 150, 300, 'end')))

    def ml(v):
        out = []
        for cp in (100, 300, 'end'):
            ls = [qlen(g, s, cp) for g, s in v]
            ls = [x for x in ls if x > 0]
            out.append(f1(sum(ls), len(ls)))
        return '; '.join(out)
    add('her mean length when alive at r100; r300; end', ml)

    def ls(v):
        c = Counter()
        for t in turns(v, 0, 300):
            x = t[L]
            c[2 if x == 2 else 3 if x == 3 else 4 if x == 4 else 5 if x <= 8 else 9] += 1
        n = sum(c.values())
        return '/'.join('%.0f' % (100.0 * c[k] / n) for k in (2, 3, 4, 5, 9))
    add('share of her turns r0-300 at length 2/3/4/5-8/9+ (%)', ls)

    def sp(v):
        x = [z for g, s in v for z in g['splits'][s]]
        c = Counter('%d to %d' % (z[1], z[2]) for z in x if z[0] <= 300)
        return '%s; r%d; %s' % (f1(len(x), len(v)), median(z[0] for z in x), ', '.join('%s x%d' % kv for kv in c.most_common(2)))
    add('her splits per game; median round; commonest (length before to after, r0-300)', sp)

    def ds(v):
        out = []
        for cp in (25, 50, 100, 300):
            xs = [t[DS] for g, s in v for t in g['recs'][s] if t[0] == cp]
            out.append(f1(sum(xs), len(xs)))
        return '; '.join(out)
    add('tiles from her start tile at r25; r50; r100; r300 (mean, alive)', ds)

    def area(v):
        out = []
        for lo in (0, 50, 150):
            xs = []
            for g, s in v:
                ts = [t for t in g['recs'][s] if lo <= t[0] < lo + 50]
                if len(ts) >= 50:
                    xs.append(len(set(t[END] for t in ts)))
            out.append(f1(sum(xs), len(xs)))
        return '; '.join(out)
    add('distinct tiles she stands on in r0-49; r50-99; r150-199', area)

    def own(v):
        out = []
        for lo, hi in ((0, 100), (101, 300)):
            n = a = b = 0
            for t in turns(v, lo, hi):
                n += 1
                a += t[O3]
                b += t[O5]
            out.append('%.2f, %.2f' % (a / max(1, n), b / max(1, n)))
        return '; '.join(out)
    add('own heads within 3, within 5 tiles: r0-100; r101-300', own)

    def en(v):
        out = []
        for lo, hi in ((0, 100), (101, 300), (0, 9999)):
            n = a = 0
            for t in turns(v, lo, hi):
                n += 1
                a += t[EP3N]
            out.append(f1(100.0 * a, n))
        return '; '.join(out) + '; %d' % sum(1 for g, s in v if any(t[EP3N] > 0 for t in g['recs'][s]))
    add('enemy heads within 3 steps per 100 of her turns: r0-100; r101-300; all; games with any', en)

    def resp(v):
        c = Counter()
        for t in turns(v):
            if t[EP3N] <= 0:
                continue
            c['n'] += 1
            c['hit'] += t[HIT]
            if t[DIED]:
                c['died'] += 1
            elif t[ACT] == 1:
                c['split'] += 1
            elif t[ACT] == 2:
                c['none'] += 1
            elif t[STEPS] >= 2:
                c['sprint'] += 1
            elif t[DA] > t[DB]:
                c['away'] += 1
            elif t[DA] < t[DB]:
                c['closer'] += 1
            else:
                c['level'] += 1
        n = c['n']
        return '%d: %s/%s/%s/%s/%s; %s' % (n, pc(c['away'], n), pc(c['level'], n), pc(c['closer'], n), pc(c['sprint'], n), pc(c['split'], n), pc(c['hit'], n))
    add('such turns: she steps away/level/closer/sprints/splits; rammed before her next turn', resp)

    def pearls(v):
        out = []
        for lo, hi in ((0, 100), (101, 300)):
            n = a = 0
            for t in turns(v, lo, hi):
                n += 1
                a += t[ATE]
            out.append(f1(100.0 * a, n))
        return '; '.join(out) + '; ' + f1(sum(t[ATE] for t in turns(v)), len(v))
    add('pearls she eats per 100 turns r0-100; r101-300; per game', pearls)

    def place(v):
        n = pk = kc = 0
        for t in turns(v):
            n += 1
            pk += 1 if t[PK] > 0 else 0
            kc += 1 if t[KC] >= 2 else 0
        m = [t for t in turns(v, 101, 300) if t[MN] >= 0]
        return '%s; %s; %s' % (pc(pk, n), pc(kc, n), pc(sum(1 for t in m if t[MN] == 1), len(m)))
    add('turns in a one-entrance pocket; on a tile with kelp on 2+ sides; a mate nearer the nearest enemy head (r101-300)', place)
    add('she rams an enemy head; enemies die on her body', lambda v: '%d; %d' % (sum(len(g['attacks'][s]) for g, s in v), sum(len(g['bodykills'][s]) for g, s in v)))

    def fate(v):
        c = Counter()
        for g, s in v:
            f = g['fate'][s]
            if f is None:
                c['alive'] += 1
            elif f['own_move']:
                c['own%d' % min(f['reason'], 4)] += 1
            else:
                c['ram'] += 1
        return '%d; %d/%d/%d/%d; %d' % (c['ram'], c['own0'], c['own1'], c['own2'], c['own3'], c['alive'])
    add('fate: rammed; own move (wall/own body/other body/into a head); alive', fate)

    def chance(v):
        ch = [(g['game'], x) for g, s in v for x in g['chances'] if x[1] == 1 - s]
        n3 = sum(g['near'][1 - s][0] for g, s in v)
        qt = sum(len(g['recs'][s]) for g, s in v)
        return '%d, %d, %d; %s' % (len(ch), len(set(a for a, _ in ch)), sum(x[4] for _, x in ch), f1(100.0 * n3, qt))
    add('sure ways to her head (enemy mover, at most 3 steps): turns, games, taken; enemy dragon-turns starting within 3 tiles of her head per 100 of her turns', chance)
    for r in rows:
        print(r)


def band(g, t):
    x = t[DS] - leash(g)
    return 0 if x <= 0 else 1 if x <= 4 else 2


def exits(g, s):
    """class of her death: None alive, 'inside', 'walked', 'pushed'."""
    f = g['fate'][s]
    if f is None:
        return None
    R = leash(g)
    recs = g['recs'][s]
    if f['ds'] <= R + 2:
        return 'inside'
    last = max((n for n, t in enumerate(recs) if t[DS] <= R), default=None)
    if last is None:
        return 'walked'
    return 'pushed' if any(x[EP5N] > 0 for x in recs[max(0, last - 3):last + 1]) else 'walked'


def table_b(cols):
    print('| measure (open-start games) | ' + ' | '.join(k for k, _ in cols) + ' |')
    print('|---|' + '---|' * len(cols))
    rows = []

    def add(name, fn):
        rows.append('| ' + name + ' | ' + ' | '.join(fn([(g, s) for g, s in v if g['scomp'][s] * 2 >= g['cells']]) for _, v in cols) + ' |')

    def stat(v, lo, hi):
        c = [Counter(), Counter(), Counter()]
        for g, s in v:
            for t in g['recs'][s]:
                if lo <= t[0] <= hi:
                    b = c[band(g, t)]
                    b['n'] += 1
                    b['ram'] += t[HIT]
                    b['self'] += 1 if t[DIED] else 0
                    b['thr'] += 1 if t[EP3N] > 0 else 0
                    b['ate'] += t[ATE]
                    b['o5'] += t[O5]
                    b['kelp'] += 1 if t[KC] >= 2 else 0
                    b['pocket'] += 1 if t[PK] > 0 else 0
        return c
    add('games; her turns', lambda v: '%d; %d' % (len(v), sum(len(g['recs'][s]) for g, s in v)))

    def share(v):
        c = stat(v, 0, 9999)
        n = sum(b['n'] for b in c)
        return '/'.join('%.0f' % (100.0 * b['n'] / n) for b in c)
    add('share of her turns inside R / R+1 to R+4 / beyond R+4 (%)', share)

    def haz(v, lo, hi, key):
        c = stat(v, lo, hi)
        return ' / '.join('%s (%d)' % (f1(1000.0 * b[key], b['n']), b[key]) for b in c)
    add('rammed per 1000 turns there (count), all rounds', lambda v: haz(v, 0, 9999, 'ram'))
    add('same, r51-150', lambda v: haz(v, 51, 150, 'ram'))
    add('same, r151-300', lambda v: haz(v, 151, 300, 'ram'))
    add('died on her own move per 1000 turns there (count)', lambda v: haz(v, 0, 9999, 'self'))

    def per100(v, key):
        c = stat(v, 0, 9999)
        return ' / '.join(f1(100.0 * b[key], b['n']) for b in c)
    add('turns with an enemy head within 3 steps, per 100', lambda v: per100(v, 'thr'))
    add('pearls eaten per 100 turns there', lambda v: per100(v, 'ate'))

    def own5(v):
        c = stat(v, 0, 9999)
        return ' / '.join(f1(b['o5'], b['n']) for b in c)
    add('own heads within 5 tiles there', own5)

    def tight(v):
        c = stat(v, 0, 9999)
        n = sum(b['n'] for b in c)
        return '%s; %s' % (pc(sum(b['kelp'] for b in c), n), pc(sum(b['pocket'] for b in c), n))
    add('all her turns: tile with kelp on 2+ sides; in a one-entrance pocket', tight)

    def early(v):
        lay = defaultdict(list)
        for g, s in v:
            recs = g['recs'][s]
            at = next((t for t in recs if t[0] == 30), None)
            if at is None or any(t[EP5N] > 0 for t in recs if t[0] <= 30):
                continue
            f = g['fate'][s]
            lay[(g.get('layout') or g['map'], g['w'], g['h'], g.get('opp'))].append(
                (at[DS], f is not None and f['r'] <= 100, f is None, g['win'] is not None and (g['win'] == 1) == (s == 0), g['game']))
        lo, hi = [], []
        for x in lay.values():
            x = sorted(x, key=lambda r: (r[0], r[4]))
            if len(x) >= 4:
                lo += x[:len(x) // 2]
                hi += x[len(x) - len(x) // 2:]
        if not lo:
            return '-'
        n = len(lo)
        return '%d: %.1f v %.1f tiles; dead by r100 %d v %d; alive at end %d v %d; won %d v %d' % (
            n, sum(r[0] for r in lo) / n, sum(r[0] for r in hi) / n, sum(r[1] for r in lo), sum(r[1] for r in hi), sum(r[2] for r in lo),
            sum(r[2] for r in hi), sum(r[3] for r in lo), sum(r[3] for r in hi))
    add('within layout and opponent, no enemy head within 5 steps up to r30: nearer half v farther half at r30 (games each)', early)

    def deaths(v):
        c = Counter(exits(g, s) for g, s in v)
        return '%d: %d / %d / %d; %d' % (c['inside'] + c['walked'] + c['pushed'], c['inside'], c['walked'], c['pushed'], c[None])
    add('deaths: at most R+2 from start / after walking out of R / after being pushed out; alive at the end', deaths)

    def walked(v):
        gaps, lost, lostq = [], 0, 0
        for g, s in v:
            if exits(g, s) == 'walked':
                f = g['fate'][s]
                last = max((t[0] for t in g['recs'][s] if t[DS] <= leash(g)), default=0)
                gaps.append(f['r'] - last)
                bad = g['win'] is None or (g['win'] == 1) != (s == 0)
                lost += 1 if bad else 0
                lostq += 1 if bad and g['decided'] == 'queen' else 0
        return '-' if not gaps else '%d; %d; %d' % (median(gaps), lost, lostq)
    add('walked-out deaths: median rounds after she left R; games lost; lost on queen length', walked)
    for r in rows:
        print(r)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else 'A'
    if which in ('A', 'B'):
        games = load(('m1', 'm2', 'b1', 'b2', 'q1'))
        out = defaultdict(list)
        for g in games:
            arm = ARM[g['label']]
            opp = 'Bob' if g['opp'].startswith('Big') else 'Quiz'
            out[arm + ' ours'].append((g, 0))
            out[arm + ' ' + opp].append((g, 1))
            out['all ours'].append((g, 0))
            out['all ' + opp].append((g, 1))
        if which == 'A':
            table_a([(k, out[k]) for k in ('MAIN ours', 'MAIN Bob', 'MAIN Quiz', 'B7 ours', 'B7 Bob', 'B7 Quiz', 'B7Q ours', 'B7Q Bob', 'B7Q Quiz')])
        else:
            table_b([(k, out[k]) for k in ('MAIN ours', 'B7 ours', 'B7Q ours', 'all ours', 'all Bob', 'all Quiz')])
    else:
        games = load(('L0', 'T0'))
        out = defaultdict(list)
        for g in games:
            a, b = ('ours, ladder', 'our ladder opponents') if g['label'] == 'ladder' else ('rank-1', "rank-1's opponents")
            out[a].append((g, 0))
            out[b].append((g, 1))
        cols = [(k, out[k]) for k in ('ours, ladder', 'our ladder opponents', 'rank-1', "rank-1's opponents") if out[k]]
        table_a(cols)
        print()
        table_b(cols)


main()
