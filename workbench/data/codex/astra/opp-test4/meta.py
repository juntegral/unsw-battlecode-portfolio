import json, glob
from collections import defaultdict
rows = []
for f in glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/*-old/game-*.json'):
    try:
        j = json.load(open(f))
    except Exception:
        continue
    if 19 in (j.get('teamAId'), j.get('teamBId')) and 1119 in (j.get('teamAId'), j.get('teamBId')):
        own = 'a' if j['teamAId'] == 1119 else 'b'
        rows.append((j['id'], j['completedAt'][5:16], f.split('/')[-2], own.upper(), j['mapName'], 'W' if j['winner'] == own else 'L',
                     j['scoresA'] if own == 'a' else j['scoresB'], j['scoresB'] if own == 'a' else j['scoresA'], j['ranked'], j['teamAElo'], j['teamBElo'], j.get('eloChangeA')))
rows.sort()
for r in rows:
    print(*r)
g = defaultdict(lambda: [0, 0])
for r in rows:
    for k in ('set ' + r[2], 'map ' + r[4], 'seat ' + r[3] + (' ranked' if r[8] else ' unranked'), 'all'):
        g[k][0] += r[5] == 'W'
        g[k][1] += 1
for k in sorted(g):
    print(k, '%d/%d' % tuple(g[k]))
