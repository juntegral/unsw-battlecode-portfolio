import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'data/analysis/ladder/dossier/online')
import label_report as lr
OUT=Path('data/codex/astra/queenfeed')
refs={}
for p in Path('data/analysis/ladder/dossier/online').glob('label-one*-old.json'):
 for col in json.loads(p.read_text())['columns']:
  for r in col['games']:refs[r['game']]=r
checks=0;prov=[]
for f in sorted(OUT.glob('one*.jsonl')):
 rows=[json.loads(x) for x in f.read_text().splitlines()];assert len(rows)==15
 for g in rows:
  r=refs[g['game']]
  assert g['queen_pearls']==r['details']['queen_counts']['pearls']
  assert g['feeder_eat']==r['extra']['counts']['feeder_eat']
  assert (g['death'] or {}).get('round')==(r['extra']['queen_death'] or {}).get('round')
  for key in ('herd_alone','herd_turns'):assert g['queen_counts'].get(key,0)==r['details']['queen_counts'].get(key,0)
  for cp in ('100','300'):
   for side in (0,1):
    for key in ('alive','total','queen_length','pearls'):assert g['snaps'][cp]['sides'][side][key]==r['details']['checkpoints'][cp][side][key]
  path=Path('data/online/smoke')/(g['label']+'-old')/('M'+str(g['game'])+'.replay')
  text=lr.agg.sb.load_replay(path).root().text(0)
  normalized=[' '.join([p[0],'TEAM',*p[2:]]) if p[0]=='DRAGON' else ' '.join(p) for line in text.splitlines() if (p:=line.split())]
  prov.append(dict(label=g['label'],map=g['map'],game=g['game'],queen_id=g['queen_id'],queen_start=g['start'][str(g['queen_id'])][0],
                   geometry_and_starts_hash=hashlib.sha256('\n'.join(normalized).encode()).hexdigest(),replay_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
  checks+=1
OUT.joinpath('validation.json').write_text(json.dumps(dict(verified_games=checks,provenance=prov),ensure_ascii=False,indent=2))
print('verified games',checks)
for s in ('w1','d1'):
 a={x['map']:x for x in prov if x['label']=='one3-'+s}
 for v in '45':
  b={x['map']:x for x in prov if x['label']=='one'+v+'-'+s}
  print(s,'one3 vs one'+v,'same geometry',sum(a[m]['geometry_and_starts_hash']==b[m]['geometry_and_starts_hash'] for m in a),'changed queen starter',sum(a[m]['queen_id']!=b[m]['queen_id'] for m in a))
