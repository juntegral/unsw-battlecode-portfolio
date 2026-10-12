# Scratch (diag-topopen): table from to_scan3-*.jsonl. Usage: python3 to_agg5.py [S|M|L|all] [nomap=Name]
import sys, json
from collections import defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad'}
LABS = ['aAah today', 'larp today', 'Cutlery today', 'chad today', 'top today', 'ours B7Q', 'ours main', 'ours B7', 'ours vs top', 'top vs us', 'our opp today', 'T3 opp']
BANDS = ('m0', 'm1', 'm2', 'm3', 'u1', 'none')


def size(c):
    return 'S' if c <= 700 else 'M' if c <= 1200 else 'L'


def main():
    nomaps = [a[6:] for a in sys.argv if a.startswith('nomap=')]
    args = [a for a in sys.argv[1:] if not a.startswith('nomap=')]
    sz = args[0] if args else 'all'
    acc = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    games = defaultdict(int)
    seen = set()
    for f in sorted(W.glob('to_scan3-*.jsonl')):
        if 'test' in f.name:
            continue
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            g = json.loads(line)
            if 'error' in g or g['game'] in seen or not g['pairs']:
                continue
            seen.add(g['game'])
            if sz != 'all' and size(g['cells']) != sz:
                continue
            if any(g['map'].startswith(m) for m in nomaps):
                continue
            src = g['src'][:2]
            for s in 'ut':
                d = g['sides'][s]
                labs = []
                if src == 'T3':
                    if d['team'] in NAMES:
                        labs += [NAMES[d['team']] + ' today', 'top today']
                    else:
                        labs.append('T3 opp')
                elif src in ('OQ', 'OM', 'OB'):
                    labs.append(dict(OQ='ours B7Q', OM='ours main', OB='ours B7')[src] if s == 'u' else 'our opp today')
                elif src == 'OT':
                    labs.append('ours vs top' if s == 'u' else 'top vs us')
                for l in labs:
                    games[l] += 1
                    for k, v in d['tally'].items():
                        a = acc[l][k]
                        for i in range(3):
                            a[i] += v[i]
    print('== non-queen dragons of length 4 or less, no pearl in view, layouts with portals, size', sz, 'without', nomaps)
    print('   per window (r0-20, r21-40, r41-60) and band: turns a game : ends nearer that mouth % : steps through a portal %')
    for l in LABS:
        n = games[l]
        if n < 3:
            continue
        print('## %s (%d games)' % (l, n))
        for wdw in range(3):
            tot = sum(acc[l]['%d|%s' % (wdw, b)][0] for b in BANDS)
            cells = []
            for b in BANDS:
                v = acc[l]['%d|%s' % (wdw, b)]
                cells.append('%s %.1f:%s:%s' % (b, v[0] / n, ('%.0f' % (100.0 * v[1] / v[0])) if v[0] and b[0] == 'm' else '-', ('%.0f' % (100.0 * v[2] / v[0])) if v[0] else '-'))
            print('   %s  all %.1f | %s' % (('r0-20 ', 'r21-40', 'r41-60')[wdw], tot / n, '  '.join(cells)))


main()
