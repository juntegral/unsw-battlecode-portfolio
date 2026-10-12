"""Scratch (diag-bigmap): shared loader and the per-game timeline (job 1).
Usage: python3 data/analysis/ladder/dossier/work/bm_tl.py [O|L|R] [min cells]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from statistics import median, mean

WORK = Path('data/analysis/ladder/dossier/work')
CP = (50, 100, 150, 200, 300, 400, 500)
NAMES = ('queen', 'longest', 'total', 'elim')


def load(src, min_cells):
    rows = []
    for p in sorted(WORK.glob('bm_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            if g['cells'] > min_cells:
                rows.append(g)
    rows.sort(key=lambda g: g['gid'])
    return rows


def at(g, r):
    return g['snap'][min(r, g['last'])]


def decider(g):
    f = g['final']
    if f[0] == 0 or f[4] == 0:
        return 3
    if f[3] != f[7]:
        return 0
    if f[2] != f[6]:
        return 1
    return 2


def passed(g, q):
    """First end-of-round r from which the loser's quantity q stays below the winner's to the end (None for a draw)."""
    if g['result'] == 'draw':
        return None
    w = 0 if g['result'] == 'win' else 4
    l = 4 - w
    idx = (3, 2, 1, 2)[q]
    r = g['last']
    while r >= 0 and g['snap'][r][w + idx] > g['snap'][r][l + idx]:
        r -= 1
    return r + 1


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'O'
    mc = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
    rows = load(src, mc)
    print('games', len(rows))
    groups = {}
    for g in rows:
        groups.setdefault((g['arm'], g['opp'] if src == 'O' else 'all'), []).append(g)
    for key in sorted(groups):
        gs = groups[key]
        print()
        print(key, 'games', len(gs), 'won', sum(g['result'] == 'win' for g in gs))
        for g in gs:
            q = decider(g)
            cells = []
            for r in CP:
                s = at(g, r)
                cells.append('%d/%d/%d/%d:%d/%d/%d/%d' % (s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]))
            print('%d %-14s %dx%d %-4s %-7s pass r%s last %d | %s' % (g['gid'], g['map'][:14], g['W'], g['H'], g['result'], NAMES[q], passed(g, q), g['last'], ' | '.join(cells)))
        # medians by checkpoint
        for r in CP:
            v = [at(g, r) for g in gs]
            print('  r%d median ours n/total/longest/queen %s : theirs %s' % (r, '/'.join('%g' % median(x[k] for x in v) for k in range(4)), '/'.join('%g' % median(x[k] for x in v) for k in range(4, 8))))
        dec = [decider(g) for g in gs]
        print('  decided by', dict((NAMES[k], dec.count(k)) for k in range(4)))
        ps = [passed(g, decider(g)) for g in gs if g['result'] == 'loss']
        print('  losses: pass round median', median(ps) if ps else None, sorted(ps))


if __name__ == '__main__':
    main()
