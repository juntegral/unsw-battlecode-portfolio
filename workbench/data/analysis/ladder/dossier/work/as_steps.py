"""Scratch (diag-aahsplit): steps per turn, what a two-step turn is for, pearls and deaths by length, timeline.
Usage: python3 as_steps.py <section> <tag> [<tag> ...]   sections: len use ram time"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'
BN = ('0-20', '21-60', '61-150', '151-300', '301+')
GN = ('2-3', '4', '5-8', '9-12', '13+')


def load(tag):
    return [json.loads(x) for x in Path(WORKREL + 'as_scan-' + tag + '.jsonl').read_text().splitlines() if x]


def grp(L):
    return 0 if L <= 3 else 1 if L == 4 else 2 if L <= 8 else 3 if L <= 12 else 4


def per(a, b, k=1000.0):
    return '%7.1f' % (k * a / b) if b else '      -'


def sec_len(tag, games, bands):
    T = Counter()
    for g in games:
        for key, v in g['T'].items():
            W, L, name = key.split('|')
            if int(W) in bands:
                T[grp(int(L)), name] += v
                T['L', int(L), name] += v
    tot = sum(T[z, 't'] for z in range(5))
    print('%s (%d games) bands %s: turns %d' % (tag, len(games), [BN[b] for b in bands], tot))
    print('   group  turns%%  2+steps%%  pearls/1k  eat2/1k  deaths/1k  rammed/1k  rams started/1k  boxed-in/1k  other deaths/1k  length lost/1k  enemy dies on its body/1k  splits/100  paid segs/1k')
    for z in range(5):
        t = T[z, 't']
        if not t:
            continue
        two = T[z, 'n2'] + T[z, 'n3'] + T[z, 'n4']
        oth = T[z, 'd'] - T[z, 'dv'] - T[z, 'da3e'] - T[z, 'dab']
        print('   %-5s %6.1f %s %s %s %s %s %s %s %s %s %s %s %s' % (GN[z], 100.0 * t / tot, per(two, t, 100.0), per(T[z, 'e'], t), per(T[z, 'e2'], t),
              per(T[z, 'd'], t), per(T[z, 'dv'], t), per(T[z, 'da3e'], t), per(T[z, 'dab'], t), per(oth, t), per(T[z, 'll'], t), per(T[z, 'kb'], t),
              per(T[z, 'sp'], t, 100.0), per(T[z, 'paid'], t)))
    print('   exact length: turns%, 2+steps%, pearls/1k, rammed/1k, rams started/1k, boxed/1k, all deaths/1k, length lost/1k')
    for L in range(2, 14):
        t = T['L', L, 't']
        if not t:
            continue
        two = T['L', L, 'n2'] + T['L', L, 'n3'] + T['L', L, 'n4']
        print('   L=%2d%s %6.2f %s %s %s %s %s %s %s' % (L, '+' if L == 13 else ' ', 100.0 * t / tot, per(two, t, 100.0), per(T['L', L, 'e'], t), per(T['L', L, 'dv'], t),
              per(T['L', L, 'da3e'], t), per(T['L', L, 'dab'], t), per(T['L', L, 'd'], t), per(T['L', L, 'll'], t)))


def sec_use(tag, games, bands):
    S = Counter()
    for g in games:
        for key, v in g['SP'].items():
            W, G, paid, name = key.split('|')
            if int(W) in bands:
                S[int(G), int(paid), name] += v
    print('%s (%d games) bands %s: turns of 2+ steps by length group and free/paid' % (tag, len(games), [BN[b] for b in bands]))
    cats = ('ram', 'die', 'eat2', 'endp', 'eatgo', 'esc', 'app', 'topearl', 'found', 'plain')
    print('   group paid      n   ' + ' '.join('%7s' % c for c in cats) + '   | ends on pearl  straight  enemy<=3: n, away, nearer')
    for G in range(5):
        for paid in (0, 1):
            n = S[G, paid, 'n']
            if not n:
                continue
            en = S[G, paid, 'ednear']
            print('   %-5s %d %8d   ' % (GN[G], paid, n) + ' '.join(per(S[G, paid, c], n, 100.0) for c in cats) + '   | %s %s  %s %s %s' % (
                per(S[G, paid, 'endpearl'], n, 100.0), per(S[G, paid, 'straight'], n, 100.0), per(en, n, 100.0), per(S[G, paid, 'edup'], en, 100.0), per(S[G, paid, 'eddown'], en, 100.0)))


def sec_ram(tag, games, bands):
    c = Counter()
    for g in games:
        for r in g['rams']:
            rnd, ms, ml, hl, n, paid, hq, mq = r
            b = 0 if rnd <= 20 else 1 if rnd <= 60 else 2 if rnd <= 150 else 3 if rnd <= 300 else 4
            if b not in bands:
                continue
            if ms == 1:   # the studied side is hit
                c['hit', min(hl, 9)] += 1
                c['hitml', min(hl, 9)] += ml
                c['hit_by2', min(hl, 9)] += int(ml <= 3)
                c['hit_n2', min(hl, 9)] += int(n >= 2)
            else:
                c['mov', min(ml, 9)] += 1
                c['movhl', min(ml, 9)] += hl
                c['mov_n2', min(ml, 9)] += int(n >= 2)
                c['mov_paid', min(ml, 9)] += int(paid > 0)
    print('%s (%d games) bands %s: cross-team head-ons' % (tag, len(games), [BN[b] for b in bands]))
    print('   studied side is HIT, by its length: n, mean rammer length, rammer 2-3 long %, rammer used 2+ steps %')
    for L in range(2, 10):
        n = c['hit', L]
        if n:
            print('   L=%d%s %6d  %5.2f  %s %s' % (L, '+' if L == 9 else ' ', n, c['hitml', L] / n, per(c['hit_by2', L], n, 100.0), per(c['hit_n2', L], n, 100.0)))
    print('   studied side RAMS, by its length: n, mean victim length, used 2+ steps %, paid %')
    for L in range(2, 10):
        n = c['mov', L]
        if n:
            print('   L=%d%s %6d  %5.2f  %s %s' % (L, '+' if L == 9 else ' ', n, c['movhl', L] / n, per(c['mov_n2', L], n, 100.0), per(c['mov_paid', L], n, 100.0)))


def size_class(g):
    cells = g['w'] * g['h']
    return 0 if cells <= 700 else 1 if cells <= 1200 else 2


def sec_time(tags):
    data = {t: load(t) for t in tags}
    ref = data[tags[0]]
    mix = Counter(g['map'] for g in ref)
    print('layout mix of', tags[0], dict(mix))
    marks = ('10', '20', '30', '40', '50', '60', '80', '100', '150', '200', '300')
    for tag in tags:
        games = data[tag]
        print('--', tag, len(games), 'games; layouts', len(set(g['map'] for g in games)), '; size classes (<=700, <=1200, >1200):', [sum(1 for g in games if size_class(g) == z) for z in range(3)])
        for mode in ('pooled', 'matched'):
            line_n, line_t, line_58, line_6, line_on, line_ot, line_k, line_g = [], [], [], [], [], [], [], []
            for m in marks:
                by = defaultdict(list)
                for g in games:
                    v = g['marks'].get(m)
                    if v is None:
                        continue
                    by[g['map']].append(v)
                if mode == 'pooled':
                    allv = [v for vs in by.values() for v in vs]
                    wts = [(1.0 / len(allv), v) for v in allv]
                    cov = 1.0
                else:
                    wts = []
                    cov = sum(mix[k] for k in by if k in mix) / float(sum(mix.values()))
                    tw = float(sum(mix[k] for k in by if k in mix))
                    for k, vs in by.items():
                        if k in mix:
                            for v in vs:
                                wts.append((mix[k] / tw / len(vs), v))
                f = lambda s, j: sum(wt * v[s][j] for wt, v in wts)
                line_n.append('%5.1f' % f(0, 0))
                line_t.append('%5.1f' % f(0, 1))
                line_58.append('%5.1f' % f(0, 2))
                line_6.append('%5.1f' % f(0, 3))
                line_on.append('%5.1f' % f(1, 0))
                line_ot.append('%5.1f' % f(1, 1))
                line_k.append('%5.2f' % cov)
                line_g.append('%5d' % sum(len(vs) for vs in by.values()))
            print('  %s  round      ' % mode + ' '.join('%5s' % m for m in marks))
            print('     dragons       ' + ' '.join(line_n))
            print('     total length  ' + ' '.join(line_t))
            print('     dragons 5-8   ' + ' '.join(line_58))
            print('     dragons 6+    ' + ' '.join(line_6))
            print('     opp dragons   ' + ' '.join(line_on))
            print('     opp total     ' + ' '.join(line_ot))
            print('     games reaching ' + ' '.join(line_g))
            if mode == 'matched':
                print('     layout cover  ' + ' '.join(line_k))
        for z in range(3):
            sel = [g for g in games if size_class(g) == z]
            if not sel:
                continue
            out = []
            for m in ('20', '40', '60', '100', '150', '200'):
                vs = [g['marks'][m] for g in sel if m in g['marks']]
                if vs:
                    out.append('%s: %.1f/%.1f (n=%d)' % (m, sum(v[0][0] for v in vs) / len(vs), sum(v[0][1] for v in vs) / len(vs), len(vs)))
            print('  size class %d (n=%d) dragons/total  ' % (z, len(sel)) + '  '.join(out))


def main():
    sec = sys.argv[1]
    tags = sys.argv[2:]
    if sec == 'time':
        sec_time(tags)
        return
    for tag in tags:
        games = load(tag)
        for bands in ((0, 1, 2, 3, 4), (0, 1), (2, 3)):
            if sec == 'len':
                sec_len(tag, games, bands)
            elif sec == 'use':
                sec_use(tag, games, bands)
            elif sec == 'ram':
                sec_ram(tag, games, bands)


main()
