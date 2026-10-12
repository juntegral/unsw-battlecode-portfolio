import sys,json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
sys.dont_write_bytecode=True
from analyze import wrapped,OUT
if __name__=='__main__':
 inv=json.loads((OUT/'inventory.json').read_text());seen={x['gid'] for x in inv['selected']};jobs=[]
 for v in json.loads((OUT/'final-inventory-check.json').read_text())['new_metadata']:
  mp=Path(v);m=json.loads(mp.read_text());gid=m['id'];j=dict(path=str(mp.with_name(f'M{gid}.replay')),meta=str(mp),src='ours',gid=gid,teams=[m['teamAId'],m['teamBId']],time=m.get('completedAt'))
  if gid not in seen:jobs.append(j);inv['selected'].append(j)
 inv['late_update']='2026-10-09 05:06:03 KST';(OUT/'inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2));errors=[]
 with (OUT/'games.jsonl').open('a') as out,ProcessPoolExecutor(max_workers=3) as pool:
  for f in as_completed([pool.submit(wrapped,j) for j in jobs]):
   g,e=f.result()
   if e:errors.append(e);print('ERROR',e,flush=True)
   if g:out.write(json.dumps(g,separators=(',',':'))+'\n');out.flush();print('added',g['gid'],'version',g['version'],flush=True)
 (OUT/'late-errors.json').write_text(json.dumps(errors,indent=2))
