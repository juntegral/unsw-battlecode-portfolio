import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime
sys.path.insert(0,'data/analysis/ladder/dossier/online')
import label_report as lr
VERS={'20980':'one5','21086':'one7','21126':'one8','21165':'one9','21200':'one10'}
OUT=Path('data/codex/astra/audit-hunt')
def inventory():
 pats=[f'data/online/smoke/one{n}-{s}-old' for n in (5,7,8,9,10) for s in ('w1','c1','k1')]+['data/online/live-one1/b*']
 inv=lr.directory_inventory('audit-hunt',','.join(pats)); rows=[];other={}
 for rp,j in inv['jobs']:
  print('read',j['id'],rp.stat().st_size,flush=True)
  root=lr.agg.sb.load_replay(rp).root();own=int(j['teamAId']!=1119);bot=root.text(1+own)
  if bot in VERS:rows.append(dict(gid=j['id'],version=VERS[bot],bot=bot,path=str(rp),meta=j))
  else:other[bot]=other.get(bot,0)+1
 result=dict(time=datetime.now().astimezone().isoformat(),rows=rows,other=other,duplicates=inv['duplicate_ids'],notes=inv['notes'])
 (OUT/'inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print({v:sum(x['version']==v for x in rows) for v in VERS.values()},flush=True)
if __name__=='__main__':inventory()
