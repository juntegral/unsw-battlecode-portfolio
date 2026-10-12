# Scratch (diag-spawn): tables from sp_k-*.jsonl (spawn attempts seen through the mirror tile).
# O = meow as focal side "F" in its 500 games; R = rank-1 as focal side "F" in its 597 games; "X" = the opponents.
# Every line: pooled O, pooled R, equal-layout mean O, equal-layout mean R, layouts where R is higher / valid.
# Usage: python3 data/analysis/ladder/dossier/work/sp_tickagg.py [test]
import sys, json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
CG = {0: ('every', 'all'), 1: ('fast', 'all', 'not1'), 2: ('fast', 'all', 'not1'), 3: ('mid', 'all', 'not1'), 4: ('slow', 'all', 'not1'),
      5: ('rare', 'all', 'not1'), -1: ('rare', 'all', 'not1')}
LINES = []


def out(*a):
    LINES.append(' '.join(str(x) for x in a))


A = defaultdict(Counter)
games = Counter()
LAY = []
OUTS = ('born', 'pearl', 'Fh_empty', 'Fh_ate', 'Fb_empty', 'Fb_ate', 'Xh_empty', 'Xh_ate', 'Xb_empty', 'Xb_ate', 'body?', 'free_noborn')


def load(names):
    for name in names:
        for line in Path(OUT + name).read_text().splitlines():
            g = json.loads(line)
            a = A[(g['team'], g['layout'])]
            games[(g['team'], g['layout'])] += 1
            a[('games',)] += 1
            for k, v in g['A2'].items():
                z, c, out = k.split('|')
                for cg in CG[int(c)]:
                    for zz in (z, 'ab'):
                        a[('A', zz, cg, out)] += v
            for k, v in g['BM'].items():
                z, c, s, d1, res = k.split('|')
                for cg in CG[int(c)]:
                    for zz in (z, 'ab'):
                        a[('B', zz, cg, s, int(d1), res)] += v
            for k, v in g['B'].items():
                z, c, s, d1, res = k.split('|')
                for cg in CG[int(c)]:
                    for zz in (z, 'ab'):
                        a[('B0', zz, cg, s, int(d1), res)] += v
            for k, v in g['A'].items():
                z, c, o = k.split('|')
                for cg in CG[int(c)]:
                    for zz in (z, 'ab'):
                        a[('A0', zz, cg, o)] += v
            for k, v in g.get('B2', {}).items():
                z, c, s, d1, d0, who, wait = k.split('|')
                for cg in CG[int(c)]:
                    for zz in (z, 'ab'):
                        a[('B2', zz, cg, s, int(d1), int(d0), who, int(wait))] += v
            for k, v in g.get('BLM', {}).items():
                z, s, ln, res = k.split('|')
                for zz in (z, 'ab'):
                    a[('BL', zz, s, int(ln), res)] += v
            for k, v in g.get('CM', {}).items():
                z, c, s, d2, res = k.split('|')
                for cg in CG[int(c)]:
                    for zz in (z, 'ab'):
                        a[('C', zz, cg, s, int(d2), res)] += v


def val(team, lay, key):
    return A[(team, lay)].get(key, 0)


def cmp(label, num, den, scale=100.0, fmt='%6.1f'):
    nums = num if isinstance(num, list) else [num]
    dens = den if isinstance(den, list) else [den]
    pooled, per = {}, {}
    for tm in 'OR':
        n = sum(val(tm, l, k) for l in LAY for k in nums)
        d = sum(val(tm, l, k) for l in LAY for k in dens)
        pooled[tm] = (scale * n / d if d else None, n, d)
        per[tm] = {}
        for l in LAY:
            dd = sum(val(tm, l, k) for k in dens)
            if dd >= 20 or (dd and dens == [('games',)]):
                per[tm][l] = scale * sum(val(tm, l, k) for k in nums) / dd
    shared = [l for l in LAY if l in per['O'] and l in per['R']]
    mo = sum(per['O'][l] for l in shared) / len(shared) if shared else None
    mr = sum(per['R'][l] for l in shared) / len(shared) if shared else None
    hi = sum(1 for l in shared if per['R'][l] > per['O'][l])
    f = lambda v: (fmt % v) if v is not None else '    NA'
    out('%-64s O %s (%d/%d)  R %s (%d/%d) | layout mean O %s R %s | R higher %d/%d' % (
        label, f(pooled['O'][0]), pooled['O'][1], pooled['O'][2], f(pooled['R'][0]), pooled['R'][1], pooled['R'][2],
        f(mo), f(mr), hi, len(shared)))
    return per


def main():
    names = ['sp_ktest.jsonl'] if len(sys.argv) > 1 else ['sp_k-%d.jsonl' % n for n in range(6)]
    load(names)
    LAY.extend(sorted({l for (tm, l) in A}))
    out('games O %d R %d; layouts %d (layout means use layouts with 20 or more in the denominator for both teams)' % (
        sum(v for (tm, l), v in games.items() if tm == 'O'), sum(v for (tm, l), v in games.items() if tm == 'R'), len(LAY)))
    out('check: attempts where the mirror was born, the tile was free and nothing was born (must be 0):',
          sum(val(tm, l, ('A', 'ab', 'all', 'free_noborn')) for tm in 'OR' for l in LAY),
          '; body of unknown owner:', sum(val(tm, l, ('A', 'ab', 'all', 'body?')) for tm in 'OR' for l in LAY))
    for z in ('a', 'b', 'ab'):
        for cg in ('every', 'fast', 'mid', 'slow', 'rare', 'not1', 'all'):
            k = lambda out: ('A', z, cg, out)
            den = [k(o) for o in OUTS]
            out('\n-- what a spawn attempt met: window %s, class %s --' % (z, cg))
            cmp('attempts seen per game (mirror tile born)', den, ('games',), 1.0, '%6.1f')
            cmp('all pearls born per game', ('A0', z, cg, 'born'), ('games',), 1.0, '%6.1f')
            cmp('born %', k('born'), den)
            cmp('a pearl still lying %', k('pearl'), den)
            cmp('focal head that stepped onto the empty tile %', k('Fh_empty'), den)
            cmp('focal body, came over the empty tile %', k('Fb_empty'), den)
            cmp('focal head or body that ate there %', [k('Fh_ate'), k('Fb_ate')], den)
            cmp('opponent head that stepped onto the empty tile %', k('Xh_empty'), den)
            cmp('opponent body, came over the empty tile %', k('Xb_empty'), den)
            cmp('opponent head or body that ate there %', [k('Xh_ate'), k('Xb_ate')], den)
            cmp('killed by a focal empty step (head or body), per game', [k('Fh_empty'), k('Fb_empty')], ('games',), 1.0, '%6.2f')
            cmp('killed by an opponent empty step, per game', [k('Xh_empty'), k('Xb_empty')], ('games',), 1.0, '%6.2f')
            cmp('focal empty-step kills per 100 born', [k('Fh_empty'), k('Fb_empty')], k('born'))
            cmp('opponent empty-step kills per 100 born', [k('Xh_empty'), k('Xb_empty')], k('born'))
            for s in 'FX':
                for d1 in (1, 2, 3):
                    b = lambda res: ('B', z, cg, s, d1, res)
                    bd = [b(r) for r in ('on', 'other_on', 'born_d1', 'born_d2', 'born_d3')]
                    cmp('  side %s nearest head %d away, countdown 1, tile empty: steps on %%' % (s, d1), b('on'), bd)
                    cmp('     born with the head 1 step away %', b('born_d1'), bd)
                    cmp('     born with the head 2 steps away %', b('born_d2'), bd)
                    cmp('     born with the head 3 or more away %', b('born_d3'), bd)
    for z in ('a', 'b', 'ab'):
        for cg in ('all', 'not1', 'fast', 'mid', 'slow', 'rare'):
            out('\n-- two rounds ahead and afterwards: window %s, class %s --' % (z, cg))
            for s in 'FX':
                for d2 in (1, 2):
                    c = lambda res: ('C', z, cg, s, d2, res)
                    cd = [c(r) for r in ('on2', 'other_on2', 'on1', 'other_on1', 'born')]
                    cmp('side %s head %d away, countdown 2, tile empty: steps on now %%' % (s, d2), c('on2'), cd)
                    cmp('   steps on one round later (countdown 1) %', c('on1'), cd)
                    cmp('   born %', c('born'), cd)
                b = lambda d1, res: ('B0', z, cg, s, d1, res)
                e = lambda d1, d0, who, wt: ('B2', z, cg, s, d1, d0, who, wt)
                cmp('side %s beside at countdown 1, stayed 1 away: eats it in the birth round %%' % s, e(1, 1, 'self', 0), b(1, 'born_d1'))
                cmp('side %s beside at countdown 1, stepped back to 2: eats it one round after birth %%' % s, e(1, 2, 'self', 1), b(1, 'born_d2'))
                cmp('   eats it two rounds after birth %', e(1, 2, 'self', 2), b(1, 'born_d2'))
                cmp('   eats it later %', e(1, 2, 'self', 3), b(1, 'born_d2'))
                cmp('   the other side eats it %', [e(1, 2, 'other', q) for q in range(4)], b(1, 'born_d2'))
                cmp('side %s 2 away at countdown 1, moved beside: eats it in the birth round %%' % s, e(2, 1, 'self', 0), b(2, 'born_d1'))
        out('\n-- by length of the dragon beside the tile at countdown 1, window %s: steps on %% --' % z)
        for s in 'FX':
            for ln in (2, 3, 4, 5):
                cmp('side %s length %d%s' % (s, ln, '+' if ln == 5 else ''), ('BL', z, s, ln, 'on'), [('BL', z, s, ln, 'on'), ('BL', z, s, ln, 'off')])
    out('\n== per layout, all classes, rounds 0-300: tile empty, countdown 1, own head beside: steps on % (n) ==')
    for l in LAY:
        row = []
        for tm in 'OR':
            for s in 'FX':
                b = lambda res: val(tm, l, ('B', 'ab', 'all', s, 1, res))
                n = sum(b(r) for r in ('on', 'other_on', 'born_d1', 'born_d2', 'born_d3'))
                row.append('%s%s %5.1f (%4d)' % (tm, s, 100.0 * b('on') / n if n else -1, n))
            k = lambda out: val(tm, l, ('A', 'ab', 'all', out))
            gm = max(1, val(tm, l, ('games',)))
            row.append('kills/game F %.1f X %.1f born/game %.0f' % ((k('Fh_empty') + k('Fb_empty')) / gm, (k('Xh_empty') + k('Xb_empty')) / gm, k('born') / gm))
        out('  %-22s %s' % (l, ' | '.join(row)))


main()
if len(sys.argv) > 1:
    Path(OUT + 'sp_tickagg-test.txt').write_text('\n'.join(LINES) + '\n')
else:
    Path(OUT + 'sp_tickagg.txt').write_text('\n'.join(LINES) + '\n')
sys.stdout.write('lines %d\n' % len(LINES))
