"""Scratch (diag-topaah): what a dragon does with a pearl beside its head after round 100, by situation (ta_s3-*.jsonl).
Classes (first that holds; "longest" = the side's longest dragon, our leader in our own games):
  queen | longest | feeder-like, pearl within 9 of the longest | feeder-like, pearl farther | pearl within 9 of the longest (8+ long) |
  enemy head within 2 of the pearl | trapped (room under L+2) | tight (under 3L+8) | open
feeder-like = round over 400 or (round over 200 and 56+ own dragons), not the queen, not the longest, 2 x length at most the longest's
length, within 15 tiles of the longest's head (agg8-bot/main.cpp 2332-2340, 4995-5005)."""
import sys
import json
from collections import Counter, defaultdict
from statistics import median
from pathlib import Path

WORK = 'data/analysis/ladder/dossier/work/'
TAGS = ('q', 'm', 't', 'a', 'l', 'c1', 'g')
NAMES = ('queen', 'longest', 'feeder, pearl in zone', 'feeder, pearl outside', 'zone pearl, not feeder', 'enemy head by pearl',
         'trapped', 'tight', 'open')


def klass(r):
    rnd, L, queen, isl, ll, dml, dpl, alive, origin, foe, room, act, cells, hunger = r
    grow = 300 if cells <= 1200 else 150
    feeding = rnd > 400 or (rnd > 200 and alive >= 56)
    if queen:
        return 0
    if isl and rnd > grow:
        return 1
    if feeding and L * 2 <= ll and dml <= 15:
        return 2 if dpl <= 9 else 3
    if rnd > grow and ll >= 8 and dpl <= 9:
        return 4
    if foe:
        return 5
    if room < L + 2:
        return 6
    if room < 3 * L + 8:
        return 7
    return 8


def main():
    for tag in TAGS:
        p = Path(WORK + 'ta_s3-' + tag + '.jsonl')
        if not p.exists():
            continue
        gs = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        print('==', tag, 'games', len(gs))
        for wn, lo, hi in (('101-300', 101, 300), ('301+', 301, 999)):
            tot = Counter()
            took = Counter()
            split = Counter()
            n = 0
            for g in gs:
                for r in g['rows']:
                    if lo <= r[0] <= hi:
                        k = klass(r)
                        tot[k] += 1
                        took[k] += r[11] == 0
                        split[k] += r[11] == 1
                        n += 1
            if not n:
                continue
            missed = n - sum(took.values())
            print(' [%s] turns with a pearl beside the head: %d (%.0f a game), taken %.1f%%, not taken %d (%.0f a game)' % (wn, n, n / len(gs), 100 * sum(took.values()) / n, missed, missed / len(gs)))
            for k, name in enumerate(NAMES):
                if tot[k]:
                    print('    %-26s share %5.1f%%  taken %5.1f%%  split instead %4.1f%%  not taken a game %6.1f  (share of all misses %4.1f%%)' % (
                        name, 100 * tot[k] / n, 100 * took[k] / tot[k], 100 * split[k] / tot[k], (tot[k] - took[k]) / len(gs), 100 * (tot[k] - took[k]) / max(1, missed)))
        fate = defaultdict(Counter)
        waits = defaultdict(list)
        for g in gs:
            for f in g['fates']:
                rnd, dpl, dml, ll, origin, feeder, ft, wait = f
                if rnd <= 100:
                    continue
                key = ('feeder' if feeder else 'other') + (', pearl within 9 of longest' if dpl <= 9 and ll >= 8 else ', pearl farther')
                fate[key][ft] += 1
                waits[key].append(wait)
        for key in sorted(fate):
            c = fate[key]
            n = sum(c.values())
            print(' declined pearls (%s): %d (%.1f a game); eaten later by the longest %.0f%%, the decliner %.0f%%, another mate %.0f%%, the enemy %.0f%%, nobody %.0f%%; median rounds until gone %s' % (
                key, n, n / len(gs), 100 * c[0] / n, 100 * c[1] / n, 100 * c[2] / n, 100 * c[3] / n, 100 * c[4] / n, median(waits[key])))


main()
