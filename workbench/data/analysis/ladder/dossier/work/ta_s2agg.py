"""Scratch (diag-topaah): tables from ta_s2-*.jsonl (steps per turn by length, what sprints are for, length mix)."""
import sys
import json
from collections import Counter
from pathlib import Path

WORK = 'data/analysis/ladder/dossier/work/'
TAGS = ('a', 'a0', 'l', 'cs', 'c1', 'g', 'q', 'm', 't')
CLS = (('2', (2,)), ('3', (3,)), ('4', (4,)), ('5', (5,)), ('6-8', (6, 7, 8)), ('9-12', (9, 10, 11, 12)), ('13+', (13, 14, 15)))
S = int(sys.argv[1]) if len(sys.argv) > 1 else 0


def main():
    for tag in TAGS:
        p = Path(WORK + 'ta_s2-' + tag + '.jsonl')
        if not p.exists():
            continue
        gs = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        print('==', tag, 'games', len(gs))
        for wn, ws in (('0-100', (0,)), ('101-300', (1,)), ('301+', (2,))):
            c = Counter()
            for g in gs:
                for w in ws:
                    c.update(g['T'][S][w])
            turns = c['turns']
            if not turns:
                continue
            sp = c['sp_eat'] + c['sp_ram'] + c['sp_die'] + c['sp_plain']
            print(' [%s] turns %d, at 60+ own dragons %.0f%%, sprint turns %.1f/1k (ends: eats %.0f%%, rams %.0f%%, dies otherwise %.0f%%, plain %.0f%%; straight %.0f%%), paid sprint turns %.2f/1k (eats %d, rams %d, dies %d, plain %d)' % (
                wn, turns, 100 * c['cap_turns'] / turns, 1000 * sp / turns, 100 * c['sp_eat'] / max(1, sp), 100 * c['sp_ram'] / max(1, sp),
                100 * c['sp_die'] / max(1, sp), 100 * c['sp_plain'] / max(1, sp), 100 * c['sp_straight'] / max(1, sp),
                1000 * c['sp_paid_turns'] / turns, c['paid_eat'], c['paid_ram'], c['paid_die'], c['paid_plain']))
            for name, ls in CLS:
                t = sum(c['t%d_%d' % (L, n)] for L in ls for n in range(5))
                if not t:
                    continue
                multi = sum(c['t%d_%d' % (L, n)] for L in ls for n in (2, 3, 4))
                three = sum(c['t%d_%d' % (L, n)] for L in ls for n in (3, 4))
                still = sum(c['t%d_0' % L] for L in ls)
                e0 = sum(c['e%d_0' % L] for L in ls)
                e1 = sum(c['e%d_1' % L] for L in ls)
                paid = sum(c['paid%d' % L] for L in ls)
                print('    len %-5s share of turns %5.1f%%  2+ steps %5.1f%%  3+ steps %4.1f%%  no step (split or none) %4.1f%%  pearls/100 turns: one step %5.1f, sprint %5.1f  segments paid/100 turns %.2f' % (
                    name, 100 * t / turns, 100 * multi / t, 100 * three / t, 100 * still / t, 100 * e0 / max(1, t - multi), 100 * e1 / max(1, multi), 100 * paid / t))
        rams = [x for g in gs for x in g['rams'] if x[1] == S]
        n = max(1, len(rams))
        print(' rams started %d (%.1f a game): sprinting %.0f%%, with a paid step %.0f%%, target the queen %.0f%%, target their longest %.0f%%, mover longer %.0f%%' % (
            len(rams), len(rams) / max(1, len(gs)), 100 * sum(1 for x in rams if x[4] > 1) / n, 100 * sum(1 for x in rams if x[5] > 0) / n,
            100 * sum(x[6] for x in rams) / n, 100 * sum(x[7] for x in rams) / n, 100 * sum(1 for x in rams if x[2] > x[3]) / n))
        for mark in ('100', '150', '200', '300'):
            hs = [g['hist'][mark][S] for g in gs if mark in g['hist']]
            if not hs:
                continue
            tot = Counter()
            for h in hs:
                for k, v in h.items():
                    tot[int(k)] += v
            line = '  '.join('%s: %.1f' % (name, sum(tot[L] for L in range(ls[0], 21) if (L in ls or (name == '13+' and L >= 13))) / len(hs)) for name, ls in CLS)
            print(' dragons by length at r%s (mean per game, %d games): %s' % (mark, len(hs), line))


main()
