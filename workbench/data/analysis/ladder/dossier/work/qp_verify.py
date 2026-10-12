import json
from pathlib import Path
D=Path('data/analysis/ladder/dossier');W=D/'work'
index={}
for who,f in [('O','per-game.jsonl'),('R','target/per-game-top1.jsonl')]:
 for line in (D/f).open():
  r=json.loads(line)
  if r['relation']=='us':index[who,r['game']]=r
rows=[json.loads(s) for f in W.glob('qp_games_*.jsonl') for s in f.open()];assert len(rows)==1097
checks=0
for g in rows:
 r=index[g['who'],g['game']];s=g['snaps'].get('100')
 if s and r['queen']['length']['100'] is not None:
  assert s.get('length',0)==r['queen']['length']['100'],(g['game'],s,r['queen']['length']);checks+=1
 assert g['snaps']['0']['path']==0 and g['snaps']['0']['nearer']==0
 for t,s in g['snaps'].items():
  if s['alive']:
   assert g['death'] is None or int(t)<g['death']['round'] or int(t)==0
   assert s['path'] is not None and 0<=s['centre']<=1
   p=s['prox'];assert p[0]<=p[1]<=p[2] and p[3]==int(p[1]==0)
print('games',len(rows),'queen lengths r100 matched',checks,'initial/snapshot invariants passed')
