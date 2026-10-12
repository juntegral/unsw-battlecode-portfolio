"""opp-uncancel: list every game on disk against team 899."""
import json, glob, os, sys
sys.dont_write_bytecode = True
OPP = 899
rows = []
for f in glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/*/game-*.json'):
    try:
        j = json.load(open(f))
    except Exception:
        continue
    if OPP in (j.get('teamAId'), j.get('teamBId')) and 1119 in (j.get('teamAId'), j.get('teamBId')):
        rp = os.path.join(os.path.dirname(f), 'M%d.replay' % j['id'])
        rows.append((j.get('completedAt') or '', j['id'], f, os.path.exists(rp), j))
seen = set()
for c, gid, f, has, j in sorted(rows):
    if gid in seen:
        continue
    seen.add(gid)
    own = 0 if j['teamAId'] == 1119 else 1
    print(gid, c[5:16], 'AB'[own], j['mapName'], 'winner', j.get('winner'), 'ranked', j.get('ranked'), 'replay', has, os.path.dirname(f).split('/')[-1],
          j.get('teamAElo'), j.get('teamBElo'), j.get('teamAName'), '|', j.get('teamBName'))
print(len(seen), 'games')
