# Scratch (diag-stripes): the decision at a portal mouth, split by whether THIS dragon has already had the far side
# of the portal in its 7x7 view (so its program knows where the portal leads) or not (it would enter blind).
# A child is a new program with no memory, so its view starts at birth.
# Usage: python3 data/analysis/ladder/dossier/work/st_known.py <rows file> [maxround]
import sys, json
from collections import Counter

MAXR = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 6
games = [json.loads(line) for line in open(sys.argv[1])]
dec = Counter()
for g in games:
    w, h = g['w'], g['h']
    seen = {}
    wins = {}
    for t in g['turns']:
        if t['r'] > MAXR:
            break
        i = t['id']
        head = t['head']
        win = wins.get(head)
        if win is None:
            y, x = divmod(head, w)
            win = frozenset(((y + dy) % h) * w + (x + dx) % w for dy in range(-3, 4) for dx in range(-3, 4))
            wins[head] = win
        s = seen.setdefault(i, set())
        s |= win
        if t['hs'] < 48:
            continue
        fd = t['dirs'][0][0] if t['dirs'] else None
        for d, o in enumerate(t['opts']):
            if o is None or o[0] != 2 or o[2] >= 48 or o[6] != 0:
                continue
            k = ('loop%d' if o[3] else 'dead%d') % o[2]
            known = 'far side seen' if o[1] in s else 'far side never seen'
            pe = 'pearl on entry' if o[4] else ('pearl deeper' if o[5] > 0 else 'empty room')
            L = '2' if t['L'] <= 2 else '3' if t['L'] == 3 else '4+'
            for key in ((k, known, pe, L), (k, known, pe, 'all'), (k, known, 'any', 'all')):
                dec[key + (t['s'], int(fd == d))] += 1
print('took the portal step / chances (free step from the open area into a room under 48 tiles), all dragons')
ks = sorted({k[0] for k in dec})
for k in ks:
    for known in ('far side seen', 'far side never seen'):
        for pe in ('any', 'pearl on entry', 'pearl deeper', 'empty room'):
            for L in ('all', '2', '3', '4+'):
                if pe == 'any' and L != 'all':
                    continue
                u1, u0 = dec[k, known, pe, L, 'u', 1], dec[k, known, pe, L, 'u', 0]
                t1, t0 = dec[k, known, pe, L, 't', 1], dec[k, known, pe, L, 't', 0]
                if u1 + u0 + t1 + t0 == 0:
                    continue
                print('  %-6s %-19s %-14s L %-3s ours %5d / %5d (%s)  theirs %5d / %5d (%s)' % (
                    k, known, pe, L, u1, u1 + u0, '%.2f' % (u1 / (u1 + u0)) if u1 + u0 else '-',
                    t1, t1 + t0, '%.2f' % (t1 / (t1 + t0)) if t1 + t0 else '-'))
