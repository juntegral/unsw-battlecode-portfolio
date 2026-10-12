"""qexit-opus: deaths that came out of a one-way place: she had at most one free cell at her last turn start.
Split by how many free cells she had one turn earlier (2+ = she walked in by choice)."""
import sys, json
from collections import Counter
seen = set()
rows = []
for f in sys.argv[1].split(','):
    for l in open(f):
        try:
            d = json.loads(l)
        except Exception:
            continue
        if 'game' in d or (d['gid'], d['r']) in seen:
            continue
        seen.add((d['gid'], d['r']))
        rows.append(d)
c = Counter()
ex = {}
for d in rows:
    f1 = d.get('f1')
    if f1 is None or f1 > 1:
        continue
    if d.get('split1'):
        continue
    how = 'rammed by a foe after her forced step' if not d['own_turn'] else 'dies on her own move (wall, body or head)'
    if not d['own_turn'] and d['att'][0] != 'foe':
        continue
    f0 = d.get('f0')
    key = (how, 'free cells at last turn start %d' % f1, 'a turn earlier %s' % ('?' if f0 is None else '2+' if f0 >= 2 else str(f0)))
    c[key] += 1
    ex.setdefault(key, []).append('%s:r%d' % (d['gid'], d['r']))
print('one-way deaths:', sum(c.values()), 'of', len(rows))
for k, n in sorted(c.items(), key=lambda x: -x[1]):
    print('%3d  %s | %s | %s   e.g. %s' % (n, k[0], k[1], k[2], ' '.join(ex[k][:3])))
by = Counter()
for k, n in c.items():
    by[k[2]] += n
print(dict(by))
