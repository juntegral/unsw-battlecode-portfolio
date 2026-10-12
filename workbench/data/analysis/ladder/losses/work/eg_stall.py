# Scratch (early-growth brief): how often the proposed stall test would be true, from replays.
# Stall (replay approximation of what the bot could measure): our dragon, length <= 4, round below the layout's centre-rule rounds,
# no pearl it has seen within 7 path steps (so the centre pull is on, main.cpp:5061-5065), and N or more rounds since it last grew
# or last set a new lowest wrap-around Manhattan distance to the centre tile. Prints only.
# With any argument: growth does not reset the clock (centre progress only).
import sys, json
from collections import Counter
from pathlib import Path

games = []
for n in range(4):
    for line in Path('data/analysis/ladder/losses/work/eg_rows-%d.jsonl' % n).read_text().splitlines():
        games.append(json.loads(line))


def pct(a, b):
    return '%5.1f%% (%d/%d)' % (100.0 * a / b, a, b) if b else '  n/a'


def rounds_rule(g):
    cells = g['w'] * g['h']
    long_map = g['w'] >= 2 * g['h']
    return (60 if long_map else 30) if (cells <= 1000 and (long_map or cells <= 700)) else 0


for key in sorted({g['map_key'] for g in games}):
    for grp in ('never_grew', 'grew', None):
        gs = [g for g in games if g['map_key'] == key and g['group'] == grp]
        if not gs or rounds_rule(gs[0]) == 0:
            continue
        R = rounds_rule(gs[0])
        tot, pull = 0, 0
        stalled = Counter()
        gstall = Counter()
        ate_next = Counter()
        for g in gs:
            mark, best = {}, {}
            hit = set()
            for t in g['turns']:
                if t[1] != 'u' or t[0] >= R:
                    continue
                i = t[2]
                if i not in mark:
                    mark[i], best[i] = t[0], t[7]
                if t[7] < best[i]:
                    best[i], mark[i] = t[7], t[0]
                if t[3] <= 4:
                    tot += 1
                    if t[10] is None or t[10] > 7:
                        pull += 1
                        for n in (8, 12, 16):
                            if t[0] - mark[i] >= n:
                                stalled[n] += 1
                                ate_next[n] += t[19]
                                hit.add(n)
                if t[19] > 0 and len(sys.argv) < 2:
                    mark[i] = t[0]
            for n in hit:
                gstall[n] += 1
        print('%-22s %-10s %2d games r<%d | our turns len<=4: %5d | pull on (no known pearl within 7): %s' % (key, grp, len(gs), R, tot, pct(pull, tot)))
        for n in (8, 12, 16):
            print('      stalled %2d+ rounds: %s of pull-on turns | %s of all short turns | games with any: %d of %d' % (
                n, pct(stalled[n], pull), pct(stalled[n], tot), gstall[n], len(gs)))
