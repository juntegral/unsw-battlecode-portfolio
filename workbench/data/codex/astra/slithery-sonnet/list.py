import json,glob,sys
ROOT='~/01. Project/개인 프로젝트/unsw-swarm/'
rows=[]
for f in glob.glob(ROOT+'data/online/live-one1/b*/game-*.json'):
    j=json.load(open(f))
    if j.get('completedAt','')<'2026-10-08T15:00': continue
    if j['mapName'] in ('Slithery Fight','Portals'):
        us='a' if j['teamAId']==1119 else 'b'
        opp=j['teamBElo'] if us=='a' else j['teamAElo']
        me=j['teamAElo'] if us=='a' else j['teamBElo']
        rows.append((j['mapName'],j['completedAt'],j['id'],us,j['winner'],me,opp,f.split('/')[-2]))
for r in sorted(rows): print(*r)
print(len(rows))
