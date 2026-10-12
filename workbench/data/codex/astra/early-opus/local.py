"""Local arms: python3 -B data/codex/astra/early-opus/local.py <arm> [<arm> ...]  (arms under ~/meow-redteam/solo/runs/ea_<arm>)"""
import sys,json,re
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
import scan as S, summ
RUNS=Path.home()/'meow-redteam/solo/runs'
def rows(arm):
 cache=OUT/'local';cache.mkdir(exist_ok=True);out={}
 for folder in sorted((RUNS/('ea_'+arm)).glob('*-seed*-side*')):
  if not folder.is_dir() or not (folder/'result.txt').exists():continue
  f=cache/('%s__%s.json'%(arm,folder.name))
  if not f.exists():
   m=re.fullmatch(r'(.+)-seed(\d+)-side(\d)',folder.name);k=int(m[3])
   j=dict(id=0,teamAId=1119 if k==0 else 1,teamBId=1 if k==0 else 1119,mapName=m[1])
   g=S.scan(arm,None,j,folder/'game.replay');g['result']=(folder/'result.txt').read_text().strip();f.write_text(json.dumps(g,separators=(',',':')))
  out[folder.name]=json.loads(f.read_text())
 return out
if __name__=='__main__':
 arms={a:rows(a) for a in sys.argv[1:]}
 common=sorted(set.intersection(*[set(v) for v in arms.values()]))
 print('games in every arm:',len(common))
 print('%-40s '%'game'+' | '.join('%-34s'%a for a in arms))
 print('%-40s '%''+' | '.join('eat50 eat100 hd100 len100 dth q100 ' for a in arms))
 tot={a:Counter() for a in arms}
 for name in common:
  cells=[]
  for a in arms:
   m=summ.measure(arms[a][name],0)
   cells.append('%5d %6d %5d %6d %3d %4d '%(m['eat50'],m['eat100'],m['heads100'],m['len100'],m['deaths'],m['q100']))
   for k in ('eat50','eat100','nat100','heads100','len100','deaths','q100','splits100','hold4','deathmass'):tot[a][k]+=m[k]
   tot[a]['n']+=1
  print('%-40s '%name[:40]+' | '.join(cells))
 for a in arms:
  n=max(tot[a]['n'],1);print(a,'mean:',' '.join('%s %.1f'%(k,v/n) for k,v in tot[a].items() if k!='n'))
