"""Scratch (diag-aahsplit): look for the split rule in the turns of dragons of 4 or longer.
Usage: python3 as_rule.py <tag> <section>   sections: count hold box queen r0"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'
# row: 0 rnd 1 id 2 L 3 alive 4 isq 5 lng 6 fh 7 ft 8 ed 9 edt 10 pd 11 n3 12 oh 13 len_since 14 pearls_since 15 age 16 act 17 n 18 eats 19 died+1


def load(tag):
    return [json.loads(x) for x in Path(WORKREL + 'as_scan-' + tag + '.jsonl').read_text().splitlines() if x]


def pct(a, b):
    return '%5.1f' % (100.0 * a / b) if b else '    -'


def show(title, c, keys, cols):
    print(title)
    for k in keys:
        print('   %-10s' % str(k) + '  '.join('%s %s (%d)' % (cn, pct(c[k, cn, 's'], c[k, cn, 't']), c[k, cn, 't']) for cn in cols))


def main():
    tag, sec = sys.argv[1], sys.argv[2]
    games = load(tag)
    print('tag', tag, 'games', len(games))
    if sec == 'count':
        for name, gf in (('all boards', lambda g: True), ('cells <= 700', lambda g: g['w'] * g['h'] <= 700),
                         ('cells 701-1200', lambda g: 700 < g['w'] * g['h'] <= 1200), ('cells > 1200', lambda g: g['w'] * g['h'] > 1200)):
            c = Counter()
            ng = 0
            for g in games:
                if not gf(g):
                    continue
                ng += 1
                for r in g['rows']:
                    if r[4] or r[6] == 0:
                        continue
                    a = min(r[3], 63) // 4 * 4
                    Lc = 'L4' if r[2] == 4 else 'L5' if r[2] == 5 else 'L6-8' if r[2] <= 8 else 'L9+'
                    c[a, Lc, 't'] += 1
                    c[a, Lc, 's'] += int(r[16] >= 2)
            show('%s (%d games): splits per 100 turns, not queen, head free, by own dragons alive' % (name, ng), c, range(0, 64, 4), ('L4', 'L5', 'L6-8', 'L9+'))
        c = Counter()
        for g in games:
            for r in g['rows']:
                if r[4] or r[6] == 0 or r[3] < 36:
                    continue
                Lc = 'L4' if r[2] == 4 else 'L5' if r[2] == 5 else 'L6-8' if r[2] <= 8 else 'L9+'
                c[r[3], Lc, 't'] += 1
                c[r[3], Lc, 's'] += int(r[16] >= 2)
        show('exact count 36..64, all boards', c, range(36, 65), ('L4', 'L5', 'L6-8', 'L9+'))
        c = Counter()
        for g in games:
            for r in g['rows']:
                if r[4] or r[6] == 0:
                    continue
                b = 0 if r[0] <= 20 else 1 if r[0] <= 60 else 2 if r[0] <= 150 else 3 if r[0] <= 300 else 4
                a = 'under40' if r[3] < 40 else '40-47' if r[3] < 48 else '48-55' if r[3] < 56 else '56+'
                Lc = 'L4' if r[2] == 4 else 'L5' if r[2] == 5 else 'L6-8' if r[2] <= 8 else 'L9+'
                c[(b, a), Lc, 't'] += 1
                c[(b, a), Lc, 's'] += int(r[16] >= 2)
        show('round band x count', c, [(b, a) for b in range(5) for a in ('under40', '40-47', '48-55', '56+')], ('L4', 'L5', 'L6-8', 'L9+'))
    if sec == 'hold':
        lim = int(sys.argv[3]) if len(sys.argv) > 3 else 40
        R = [r for g in games for r in g['rows'] if not r[4] and r[6] > 0 and r[3] < lim]
        print('not queen, head free, alive <', lim, 'turns', len(R))
        for name, kf, keys in (
                ('length', lambda r: min(r[2], 9), range(4, 10)),
                ('turns at this length', lambda r: min(r[13], 6), range(7)),
                ('pearl steps (7 = none in 6)', lambda r: r[10], range(1, 8)),
                ('pearls within 3 steps', lambda r: min(r[11], 3), range(4)),
                ('free tiles at head', lambda r: r[6], range(1, 5)),
                ('free tiles at tail', lambda r: r[7], range(5)),
                ('enemy head to head', lambda r: r[8], range(1, 10)),
                ('enemy head to tail', lambda r: r[9], range(0, 10)),
                ('own heads within 3', lambda r: min(r[12], 4), range(5)),
                ('age in rounds', lambda r: min(r[15], 40) // 5 * 5, range(0, 45, 5)),
                ('round', lambda r: min(r[0], 300) // 25 * 25, range(0, 325, 25)),
                ('longest', lambda r: r[5], range(3))):
            c = Counter()
            for r in R:
                Lc = 'L4' if r[2] == 4 else 'L5+'
                c[kf(r), Lc, 't'] += 1
                c[kf(r), Lc, 's'] += int(r[16] >= 2)
            show(' by ' + name, c, keys, ('L4', 'L5+'))
        # what a 4-long that does not split does instead
        c = Counter()
        for r in R:
            if r[2] == 4:
                what = 'split' if r[16] >= 2 else 'eat' if r[18] else 'move1' if r[17] == 1 else 'move%d' % r[17]
                c[what, 'pearl beside' if r[10] == 1 else 'pearl 2-3' if r[10] <= 3 else 'no pearl near'] += 1
        for col in ('pearl beside', 'pearl 2-3', 'no pearl near'):
            t = sum(v for (w, cc), v in c.items() if cc == col)
            print('   4-long, %-14s n=%6d  ' % (col, t) + '  '.join('%s %s' % (w, pct(c[w, col], t)) for w in ('split', 'eat', 'move1', 'move2', 'move0')))
    if sec == 'box':
        S = [s for g in games for s in g['splits']]
        # split: 0 rnd 1 parent 2 Lb 3 child 4 after 5 alive 6 isq 7 lng 8 fh 9 ft 10 ed 11 edt 12 pd 13 n3 14 oh 15 len_since 16 pearls_since 17 age 18 keeps 19 tailhead 20 pdead3 21 cdead3
        for name, f in (('head boxed (no free tile)', lambda s: s[8] == 0), ('head free', lambda s: s[8] > 0)):
            sel = [s for s in S if f(s) and s[2] >= 5]
            c = Counter()
            for s in sel:
                kind = 'child2' if s[3] == 2 else 'keep2' if s[4] == 2 else 'other'
                c['L', min(s[2], 9), kind] += 1
                c['ft', s[9], kind] += 1
                c['al', min(s[5], 63) // 8 * 8, kind] += 1
                c['ed', min(s[10], 9), kind] += 1
                c['edt', min(s[11], 9), kind] += 1
                c['rb', 0 if s[0] <= 60 else 1 if s[0] <= 150 else 2 if s[0] <= 300 else 3, kind] += 1
                c['all', 0, kind] += 1
                c['pdead', kind, s[20]] += 1
                c['cdead', kind, s[21]] += 1
            print(name, 'splits of 5+:', len(sel))
            for key in ('all', 'L', 'ft', 'al', 'ed', 'edt', 'rb'):
                vals = sorted(set(k[1] for k in c if k[0] == key))
                print('  by', key, ' '.join('%s: c2 %d k2 %d o %d |' % (v, c[key, v, 'child2'], c[key, v, 'keep2'], c[key, v, 'other']) for v in vals))
            for kind in ('child2', 'keep2'):
                n = c['pdead', kind, 0] + c['pdead', kind, 1]
                print('  %s: parent dead within 3 rounds %s, child dead %s' % (kind, pct(c['pdead', kind, 1], n), pct(c['cdead', kind, 1], n)))
    if sec == 'queen':
        R = [r for g in games for r in g['rows'] if r[4]]
        print('queen turns at 4+:', len(R))
        c = Counter()
        for r in R:
            b = 0 if r[0] <= 20 else 1 if r[0] <= 60 else 2 if r[0] <= 150 else 3 if r[0] <= 300 else 4
            Lc = 'L4' if r[2] == 4 else 'L5' if r[2] == 5 else 'L6+'
            for key in (('band', b), ('fh', min(r[6], 2)), ('alive', min(r[3], 63) // 16 * 16), ('ed', 0 if r[8] <= 3 else 1 if r[8] <= 6 else 2), ('since', min(r[13], 4))):
                c[key, Lc, 't'] += 1
                c[key, Lc, 's'] += int(r[16] >= 2)
        show('queen: splits per 100 turns', c, sorted(set(k[0] for k in c)), ('L4', 'L5', 'L6+'))
        # queen length share of all her turns needs T; print the split shapes
        S = Counter((min(s[2], 8), s[3], s[4]) for g in games for s in g['splits'] if s[6])
        print(' queen split shapes (before, child, after):', sorted(S.items()))
    if sec == 'r0':
        c = Counter()
        for g in games:
            st = tuple(g['starters'])
            r0 = [s for s in g['splits'] if s[0] == 0]
            c[st, len(r0)] += 1
        for k, v in sorted(c.items()):
            print('  starters', k[0], 'round-0 splits', k[1], 'games', v)


main()
