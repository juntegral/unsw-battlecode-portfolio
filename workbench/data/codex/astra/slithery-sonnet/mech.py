"""Mechanism tables for one map. Usage: python3 -I mech.py "Slithery Fight" [loss|all]"""
import sys, json, statistics as st
from collections import Counter, defaultdict
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/slithery-sonnet/')
import table
MAP = sys.argv[1]
SEL = sys.argv[2] if len(sys.argv) > 2 else 'loss'
rows = [r for r in table.rows if r['map'] == MAP and (SEL == 'all' or r['result'] == SEL)]
print(MAP, SEL, len(rows), 'games')
RS = [50, 100, 150, 200, 250, 300, 350, 400, 450, 499]


def snap(r, k):
    ks = sorted(int(x) for x in r['snaps'])
    kk = max([x for x in ks if x <= k] or [ks[0]])
    return r['snaps'][str(kk)]


def fmt(xs):
    return '%5.1f' % st.mean(xs) if xs else '  -  '


for name, col in (('queen length (dead = 0)', 3), ('longest dragon', 2), ('dragons', 0), ('total length', 1), ('dragons >=10 count', 8)):
    print('--', name, ' rounds', RS)
    for s, lab in ((0, 'us  '), (1, 'them')):
        print(lab, ' mean', ' '.join(fmt([snap(r, k)[s][col] for r in rows]) for k in RS))
        if col == 3:
            print(lab, ' alive', ' '.join('%5.2f' % (sum(1 for r in rows if snap(r, k)[s][3] > 0) / len(rows)) for k in RS))
            print(lab, ' median(alive)', ' '.join('%5s' % (st.median([snap(r, k)[s][3] for r in rows if snap(r, k)[s][3] > 0] or [0])) for k in RS))

# queen pearls: role q eats
print('-- queen eats (count per game) by round window: natural / own-corpse / foe-corpse')
for s, lab in ((0, 'us  '), (1, 'them')):
    for lo, hi in ((0, 100), (100, 200), (200, 300), (300, 400), (400, 500)):
        c = Counter()
        for r in rows:
            for e in r['eats']:
                if e[1] == s and e[2] == 'q' and lo <= e[0] < hi:
                    c[e[3]] += 1
        print(lab, '%3d-%3d' % (lo, hi), {k: round(v / len(rows), 1) for k, v in sorted(c.items())})
print('-- all-dragon eats per game (natural), by window')
for s, lab in ((0, 'us  '), (1, 'them')):
    out = []
    for lo, hi in ((0, 100), (100, 200), (200, 300), (300, 400), (400, 500)):
        c = Counter()
        for r in rows:
            for e in r['eats']:
                if e[1] == s and lo <= e[0] < hi:
                    c[e[3]] += 1
        out.append((lo, {k: round(v / len(rows)) for k, v in sorted(c.items())}))
    print(lab, out)

# queen splits (length given away)
print('-- queen splits per game (count; mean length kept) and rounds >=100')
for s, lab in ((0, 'us  '), (1, 'them')):
    n = [sum(1 for x in r['splits'] if x[1] == s and x[5]) for r in rows]
    late = [sum(1 for x in r['splits'] if x[1] == s and x[5] and x[0] >= 100) for r in rows]
    kept = [x[3] for r in rows for x in r['splits'] if x[1] == s and x[5]]
    print(lab, 'mean splits %.1f, after r100 %.1f, kept-length mean %.1f median %s' % (st.mean(n), st.mean(late), st.mean(kept) if kept else 0, st.median(kept) if kept else '-'))

# long dragon deaths
print('-- deaths of dragons with L>=8: by side, cause; rammed: attacker length bucket, steps vs free')
for s, lab in ((0, 'us  '), (1, 'them')):
    c = Counter()
    att = Counter()
    paid = Counter()
    n = 0
    for r in rows:
        for d in r['deaths']:
            if d[1] == s and d[2] >= 8:
                n += 1
                c[d[4]] += 1
                if d[4] == 'rammed' and d[18]:
                    L0, steps, _, gap, aq = d[18]
                    ab = '1-3' if L0 <= 3 else '4-7' if L0 <= 7 else '8-15' if L0 <= 15 else '16+'
                    att[ab] += 1
                    paid['free' if steps <= (L0 + 3) // 4 else 'paid'] += 1
    print(lab, 'long deaths %d (%.1f/game)' % (n, n / len(rows)), dict(c), 'rammed-by-attacker-len', dict(att), dict(paid))
print('-- long (>=8) deaths split by victim length >=16 only')
for s, lab in ((0, 'us  '), (1, 'them')):
    c = Counter(); att = Counter(); paid = Counter(); n = 0
    for r in rows:
        for d in r['deaths']:
            if d[1] == s and d[2] >= 16:
                n += 1; c[d[4]] += 1
                if d[4] == 'rammed' and d[18]:
                    L0, steps, _, gap, aq = d[18]
                    att['1-3' if L0 <= 3 else '4-7' if L0 <= 7 else '8-15' if L0 <= 15 else '16+'] += 1
                    paid['free' if steps <= (L0 + 3) // 4 else 'paid'] += 1
    print(lab, n, dict(c), dict(att), dict(paid))

# queen deaths
print('-- queen deaths: kind / length / round bucket')
for s, lab in ((0, 'us  '), (1, 'them')):
    ds = [d for r in rows for d in r['deaths'] if d[1] == s and d[6]]
    print(lab, len(ds), 'of', len(rows), dict(Counter(d[4] for d in ds)), 'len', dict(sorted(Counter(min(d[2], 12) for d in ds).items())),
          'round<100 %d, 100-299 %d, 300+ %d' % (sum(d[0] < 100 for d in ds), sum(100 <= d[0] < 300 for d in ds), sum(d[0] >= 300 for d in ds)))
    rm = [d for d in ds if d[4] == 'rammed' and d[18]]
    print('     rammed queens: attacker L0', sorted(d[18][0] for d in rm), 'steps vs free(ceil L0/4)', Counter('free' if d[18][1] <= (d[18][0] + 3) // 4 else 'paid' for d in rm))
