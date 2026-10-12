import sys,json,gzip,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
import ladder_replay as lr
spec=importlib.util.spec_from_file_location('prior','data/codex/astra/sweep/0519/win1/analyze.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
OUT=Path('data/codex/astra/sweep/1055/loss16')
FILES=[Path('data/online/live-one1/b1501263/M1501265.replay'),Path('data/online/live-one1/b1501263/M1501267.replay'),Path('data/online/live-one1/b1502774/M1502775.replay')]
def main():
 for p in FILES:
  gid=int(p.stem[1:]);meta=json.loads((p.parent/f'game-{gid}.json').read_text());base=lr.scan(p,meta,str(p.parent),set());det=prior.detail(p);old=prior.o1_scan.scan('loss16',p,meta)
  own=int(base['ours']=='B');assert base['bots'][base['ours']]=='21330'
  score=lambda st:(int(st['count']>0),st['queen'],st['longest'],st['total'])
  notbehind=[int(r) for r,st in det['rounds'].items() if score(st[own])>=score(st[1-own])]
  det['permanent_behind']=max(notbehind)+1 if notbehind else min(det['rounds'])
  assert all(det['rounds'][base['last_round']][own][k]==base['final']['us'][v] for k,v in [('count','alive'),('queen','queen_length'),('longest','longest'),('total','total')])
  base.pop('intervals');base.pop('text')
  (OUT/f'{gid}.json.gz').write_bytes(gzip.compress(json.dumps(dict(base=base,detail=det,ledger=old),ensure_ascii=False).encode()))
  print(json.dumps(dict(gid=gid,map=meta['mapName'],end=base['last_round'],final=base['final'],behind=det['permanent_behind'],qdeath=[d for d in base['deaths'] if d['id'] in base['queens'].values()],eats=base['eats'],q_eats=base['q_eats'],q_splits=base['q_splits']),ensure_ascii=False))
if __name__=='__main__':main()
