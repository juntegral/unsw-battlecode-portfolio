import collections
c = collections.Counter()
tot = collections.Counter()
for l in open("~/01. Project/개인 프로젝트/unsw-swarm/data/online/live-one1/index.txt"):
    p = l.split()
    if len(p) < 6:
        continue
    day, hm, bid, kind, _, opp, res = p[0], p[1], p[2], p[3], p[4], p[5], p[6] if len(p) > 6 else ''
    c[(kind, res)] += 1
    tot[kind] += 1
    h = day + ' ' + hm[:2]
    c[(h, kind, res)] += 1
print(tot)
for k in sorted(k for k in c if len(k) == 2):
    print(k, c[k])
print('--- ranked by hour (download time)')
hours = sorted({k[0] for k in c if len(k) == 3})
for h in hours:
    print(h, 'ranked win', c[(h, 'ranked', 'win')], 'loss', c[(h, 'ranked', 'loss')], 'draw', c[(h, 'ranked', 'draw')])
