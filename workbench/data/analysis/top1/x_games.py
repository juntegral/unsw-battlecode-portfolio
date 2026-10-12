#!/usr/bin/env python3
"""Build my own game list: every row of games.csv plus smoke-test games that are NOT in games.csv
(qh31b, qn23, safer-stride, ...), with the same fields. Output x_out/games.json."""
import csv, json, os, glob, collections
SMOKE = "~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke"
rows = list(csv.DictReader(open('games.csv')))
known = {r['game_id'] for r in rows}
out = []
for r in rows:
    out.append(dict(gid=int(r['game_id']), set=r['battle_id'], path=r['replay_path'], map=r['map'], cells=int(r['cells']),
                    w=int(r['width']), h=int(r['height']),
                    A=int(r['teamAId']), An=r['teamAName'], Ae=float(r['teamAElo'] or 0),
                    B=int(r['teamBId']), Bn=r['teamBName'], Be=float(r['teamBElo'] or 0),
                    winner=r['winner'], end_type=r['end_type'], rounds=int(r['rounds']), src='csv'))
extra = collections.Counter(); dup = collections.Counter()
for d in sorted(os.listdir(SMOKE)):
    p = os.path.join(SMOKE, d)
    if not os.path.isdir(p):
        continue
    for meta in sorted(glob.glob(os.path.join(p, 'game-*.json'))):
        m = json.load(open(meta))
        gid = str(m['id'])
        rep = os.path.join(p, 'M%s.replay' % gid)
        if not os.path.exists(rep):
            continue
        if gid in known:
            dup[d] += 1
            continue
        known.add(gid)
        extra[d] += 1
        out.append(dict(gid=int(gid), set=d, path=rep, map=m.get('mapName'), cells=None, w=None, h=None,
                        A=int(m['teamAId']), An=m.get('teamAName'), Ae=float(m.get('teamAElo') or 0),
                        B=int(m['teamBId']), Bn=m.get('teamBName'), Be=float(m.get('teamBElo') or 0),
                        winner=(m.get('winner') or '').upper() or None, end_type=None, rounds=None, src='smoke'))
json.dump(out, open('x_out/games.json', 'w'))
print('csv', len(rows), 'extra', sum(extra.values()), 'total', len(out))
print('extra by dir', dict(extra))
print('already in csv by dir', dict(dup))
