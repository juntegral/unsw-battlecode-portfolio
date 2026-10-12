# Scratch (diag-stripes): loop-room mouth decisions when the far side is known, split by how many dragons the side
# has at that turn (is the entering on the other portal layout a matter of crowding?) and by the length of the dragon.
# Usage: python3 data/analysis/ladder/dossier/work/st_crowd.py <rows file>
import sys, json
from collections import Counter

games = [json.loads(line) for line in open(sys.argv[1])]
dec = Counter()
for g in games:
    w, h = g['w'], g['h']
    seen = {}
    inside = {}
    wins = {}
    for t in g['turns']:
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
        n = t['nu'] if t['s'] == 'u' else t['nt']
        nb = '1-4' if n <= 4 else '5-8' if n <= 8 else '9-16' if n <= 16 else '17+'
        for d, o in enumerate(t['opts']):
            if o is None or o[0] != 2 or o[2] >= 48 or o[6] != 0 or not o[3]:
                continue
            if o[1] not in s:
                continue
            pe = 'pearl on entry' if o[4] else ('pearl deeper' if o[5] > 0 else 'empty room')
            L = '2' if t['L'] <= 2 else '3' if t['L'] == 3 else '4+'
            free = sum(1 for oo in t['opts'] if oo is not None and oo[0] == 0 and oo[6] == 0)
            for key in ((pe, L, nb), (pe, 'all', nb), (pe, L, 'all'), (pe, 'all', 'free%d' % min(free, 2))):
                dec[key + (t['s'], int(fd == d))] += 1
print('loop rooms, far side already seen by the dragon: took / chances, by own dragons alive (and by free ordinary steps: free0, free1, free2 = 2 or more)')
for pe in ('pearl on entry', 'pearl deeper', 'empty room'):
    for L in ('all', '2', '3', '4+'):
        for nb in ('all', '1-4', '5-8', '9-16', '17+', 'free0', 'free1', 'free2'):
            u1, u0 = dec[pe, L, nb, 'u', 1], dec[pe, L, nb, 'u', 0]
            t1, t0 = dec[pe, L, nb, 't', 1], dec[pe, L, nb, 't', 0]
            if u1 + u0 + t1 + t0 == 0:
                continue
            print('  %-14s L %-3s dragons %-5s ours %5d / %5d (%s)  theirs %5d / %5d (%s)' % (
                pe, L, nb, u1, u1 + u0, '%.2f' % (u1 / (u1 + u0)) if u1 + u0 else '-',
                t1, t1 + t0, '%.2f' % (t1 / (t1 + t0)) if t1 + t0 else '-'))
