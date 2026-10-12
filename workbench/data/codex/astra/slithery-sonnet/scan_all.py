"""Scan every Slithery Fight / Portals game of ours (ranked since 2026-10-08T15:00Z + unranked smoke one11+) with o1_scan.scan."""
import sys, os, json, glob
sys.dont_write_bytecode = True
ROOT = '~/01. Project/개인 프로젝트/unsw-swarm/'
os.chdir(ROOT)
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from o1_scan import scan

MAPS = ('Slithery Fight', 'Portals')
OUT = ROOT + 'data/codex/astra/slithery-sonnet/scan.jsonl'
done = set()
if os.path.exists(OUT):
    for l in open(OUT):
        done.add(json.loads(l)['gid'])
todo = []
for f in sorted(glob.glob('data/online/live-one1/b*/game-*.json')):
    j = json.load(open(f))
    if j.get('completedAt', '') < sys.argv[1] or j['mapName'] not in MAPS:
        continue
    rp = Path(f).parent / ('M%d.replay' % j['id'])
    if rp.exists():
        todo.append(('ranked', rp, j))
for f in sorted(glob.glob('data/online/smoke/one1[1-9]-*-old/game-*.json')):
    j = json.load(open(f))
    if j['mapName'] not in MAPS or 1119 not in (j['teamAId'], j['teamBId']):
        continue
    rp = Path(f).parent / ('M%d.replay' % j['id'])
    if rp.exists():
        todo.append(('smoke:' + Path(f).parent.name, rp, j))
print(len(todo), 'games', flush=True)
with open(OUT, 'a') as out:
    for label, rp, j in todo:
        if j['id'] in done:
            continue
        try:
            g = scan(label, rp, j)
        except Exception as e:
            print('FAIL', j['id'], repr(e), flush=True)
            continue
        g['elo'] = [j['teamAElo'], j['teamBElo']]
        g['teamA'] = j['teamAId']
        g['winner_json'] = j['winner']
        g['completed'] = j['completedAt']
        out.write(json.dumps(g, separators=(',', ':')) + '\n')
        out.flush()
        print('ok', j['id'], g['map'], g['result'], flush=True)
print('DONE', flush=True)
