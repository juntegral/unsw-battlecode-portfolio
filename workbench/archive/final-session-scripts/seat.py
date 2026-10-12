"""Do we win less as team B? All game records on disk (ranked battles under live-one1, unranked sets under smoke), by seat."""
import json, glob, os, collections
os.chdir('~/01. Project/개인 프로젝트/unsw-swarm')
US = 1119
seen = set()
rows = []
for f in glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/*-old/game-*.json'):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if d.get('id') in seen or d.get('status') != 'completed' or d.get('winner') not in ('a', 'b'):
        continue
    seen.add(d['id'])
    if US not in (d.get('teamAId'), d.get('teamBId')):
        continue
    seat = 'A' if d['teamAId'] == US else 'B'
    win = (d['winner'] == 'a') == (seat == 'A')
    opp = d['teamBName'] if seat == 'A' else d['teamAName']
    oelo = d['teamBElo'] if seat == 'A' else d['teamAElo']
    rows.append((d.get('completedAt') or '', seat, win, opp, oelo or 0, bool(d.get('ranked')), d.get('mapName')))
rows.sort()
print('games', len(rows), 'from', rows[0][0][:16], 'to', rows[-1][0][:16])
def tab(name, sel):
    c = collections.Counter()
    for r in sel:
        c[(r[1], r[2])] += 1
    a, b = c[('A', True)] + c[('A', False)], c[('B', True)] + c[('B', False)]
    print('%-34s seat A %3d/%-3d %s   seat B %3d/%-3d %s' % (name, c[('A', True)], a, ('%.0f%%' % (100 * c[('A', True)] / a)) if a else '-',
                                                             c[('B', True)], b, ('%.0f%%' % (100 * c[('B', True)] / b)) if b else '-'))
tab('all', rows)
tab('ranked only', [r for r in rows if r[5]])
tab('unranked only', [r for r in rows if not r[5]])
tab('since 10-08 15:00Z, ranked', [r for r in rows if r[5] and r[0] >= '2026-10-08T15'])
for lo, hi in ((0, 1900), (1900, 2100), (2100, 2250), (2250, 9999)):
    tab('ranked, opp %d-%d' % (lo, hi), [r for r in rows if r[5] and lo <= r[4] < hi and r[0] >= '2026-10-08T15'])
print('per opponent with games in both seats (since 10-08 15:00Z):')
by = collections.defaultdict(list)
for r in rows:
    if r[0] >= '2026-10-08T15':
        by[r[3]].append(r)
for o, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    if {x[1] for x in rs} == {'A', 'B'}:
        tab('  ' + o[:30], rs)
print('ranked seat B by map (since 10-08 15:00Z):')
m = collections.Counter()
for r in rows:
    if r[5] and r[0] >= '2026-10-08T15':
        m[(r[6], r[1], r[2])] += 1
for mp in sorted({k[0] for k in m}):
    print('  %-18s A %d/%d   B %d/%d' % (mp, m[(mp, 'A', True)], m[(mp, 'A', True)] + m[(mp, 'A', False)], m[(mp, 'B', True)], m[(mp, 'B', True)] + m[(mp, 'B', False)]))
