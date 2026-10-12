"""Scratch (diag-whq): every cross-team ram seen from the victim's last own turn, and the turns that end inside reach.
Usage: python3 .../wq_ram.py [O|R]"""
import sys, json
from collections import Counter
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q', 'agg8-q2': 'B7Q'}


def load(prefix):
    rows = []
    for p in sorted(WORK.glob(prefix)):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    return rows


def klass(row):
    rnd, vs, Lv, vq, vtop, steps, mL0, mpaid, mate, c = row[:10]
    if c == 'new':
        return 'no own turn since birth'
    if c == 'long':
        return 'victim 5+ (not queen)'
    t1, tR, altR, ate, trader, moved, split = row[10:17]
    if c == 'unseen':
        return 'rammer not in view at its last turn'
    parts, Lz, dist, rt, altS, tS = row[17:23]
    if mate:
        return 'seen: rammer ate on the way'
    if dist > rt:
        return 'seen: outside reach then (bodies moved)'
    if ate:
        return 'seen: victim ate on that turn'
    if not altR:
        return 'seen: no free tile outside every reach'
    if dist <= 1:
        return 'seen: ended beside the head with a free tile outside reach'
    return 'seen: ended 2+ steps inside reach with a free tile outside reach'


def block(rows, title, vs):
    n = len(rows)
    if not n:
        return
    R = [r for g in rows for r in g['rams'] if r[1] == vs]
    print()
    print('==', title, '| games', n, '| rams on this side', len(R), '(%.1f a game)' % (len(R) / n))
    for nm, test in (('victim a queen', lambda r: r[3]), ('victim 4 or shorter, not queen', lambda r: r[2] <= 4 and not r[3]), ('victim 5+, not queen', lambda r: r[2] >= 5 and not r[3])):
        rs = [r for r in R if test(r)]
        if not rs:
            continue
        c = Counter(klass(r) for r in rs)
        print('  %s: %d (%.1f a game) | rammer steps 1: %d, 2: %d, 3+: %d | rammer length 2: %d, 3: %d, 4: %d, 5+: %d' % (
            nm, len(rs), len(rs) / n, sum(1 for r in rs if r[5] == 1), sum(1 for r in rs if r[5] == 2), sum(1 for r in rs if r[5] >= 3),
            sum(1 for r in rs if r[6] <= 2), sum(1 for r in rs if r[6] == 3), sum(1 for r in rs if r[6] == 4), sum(1 for r in rs if r[6] >= 5)))
        for k, v in c.most_common():
            print('      %s: %d (%.0f%%)' % (k, v, 100 * v / len(rs)))
        seen = [r for r in rs if r[9] == 'seen']
        if seen:
            tr = sum(1 for r in seen if r[14])
            print('      of %d seen: victim counted as a trader %d; inside parts-1 reach %d, with a free tile outside it %d, not trader and did not eat %d' % (
                len(seen), tr, sum(1 for r in seen if r[22]), sum(1 for r in seen if r[22] and r[21]), sum(1 for r in seen if r[22] and r[21] and not r[14] and not r[13])))
            two = [r for r in seen if r[5] >= 2]
            print('      of %d seen and rammed from 2+ steps: inside parts-1 reach %d, with a free tile outside it %d, not trader and did not eat %d' % (
                len(two), sum(1 for r in two if r[22]), sum(1 for r in two if r[22] and r[21]), sum(1 for r in two if r[22] and r[21] and not r[14] and not r[13])))
    e = Counter()
    for g in rows:
        for sd, kind, k, v in g['expo']:
            if sd == vs:
                e[(kind, k)] += v
    for kind, nm in (('S', 'dragons of 4 or less (not queen)'), ('Q', 'queen')):
        print('  %s, a game: ' % nm + '; '.join('%s %.1f' % (k[1], v / n) for k, v in sorted(e.items(), key=lambda t: -t[1]) if k[0] == kind))
        a, b = e[(kind, 'ends in true reach by choice')], e[(kind, 'by choice, rammed before the next turn')]
        a2, b2 = e[(kind, 'ends in parts-1 reach by choice')], e[(kind, 'parts-1 by choice, rammed before the next turn')]
        print('     by choice inside true reach: %d turns, rammed before the next turn %d (%.1f%%) | parts-1 reach by choice: %d, rammed %d (%.1f%%)' % (a, b, 100 * b / max(1, a), a2, b2, 100 * b2 / max(1, a2)))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'O'
    rows = load('wq_scan-%s[0-9].jsonl' % mode)
    if mode != 'O':
        block(rows, mode + ': side 0 is the victim', 0)
        block(rows, mode + ': side 1 is the victim', 1)
        return
    for opp in ('WeHaveQuizzes', 'Big Bobs Bots'):
        rs = [g for g in rows if g['opp'] == opp]
        for arm in ('MAIN', 'B7', 'B7Q'):
            block([g for g in rs if ARM[g['src']] == arm], '%s %s: ours rammed' % (opp, arm), 0)
        block(rs, '%s all arms: ours rammed' % opp, 0)
        block(rs, '%s all arms: theirs rammed by us' % opp, 1)


main()
