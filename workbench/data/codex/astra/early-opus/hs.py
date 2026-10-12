"""On/off table for a split or explore arm, our side, r0-100.  python3 -B hs.py <off arm> <on arm>"""
import sys
sys.dont_write_bytecode=True
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import local,summ
from mech import mech
def row(g):
 m=summ.measure(g,0);c=mech(g,0)
 S=[x for x in g['splits'] if x['side']==0 and x['r']<=100];D=[d for d in g['deaths'] if d['side']==0]
 near=0
 for x in S:
  near+=any(d['id'] in (x['id'],x['child']) and 0<=d['r']-x['r']<=3 for d in D)
 q=min(t['id'] for t in g['turns'] if t['side']==0)
 qs=sum(1 for x in S if x['id']==q)
 causes=Counter(('L%d '%min(d['L'],4))+d['cause'] for d in D if d['r']<=100)
 qdead=next((d['r'] for d in D if d['id']==q),None)
 return dict(e50=m['eat50'],e100=m['eat100'],h100=m['heads100'],len100=m['len100'],q100=m['q100'],qhome50=m['qhome50'],d100=m['deaths'],splits=len(S),near=near,qs=qs,hold=c['hold'],first=100*c['split0']/max(c['split'],1),causes=causes,qdead=qdead,res=g['result'].split()[0])
if __name__=='__main__':
 off,on=sys.argv[1:3];A=local.rows(off);B=local.rows(on);common=sorted(set(A)&set(B))
 print('%-28s | %s (off) | %s (on)   columns: pearls r50, r100, dragons r100, total length r100, queen length r100, deaths r100, splits, deaths within 3 rounds of a split, queen splits, 4+ hold turns, first-turn split %%, queen died at, result'%('map',off,on))
 T=[Counter(),Counter()];CA=[Counter(),Counter()]
 for n in common:
  ra,rb=row(A[n]),row(B[n])
  f=lambda r:'%3d %3d %2d %3d %d %2d %2d %2d %d %2d %3.0f%% %s %s'%(r['e50'],r['e100'],r['h100'],r['len100'],r['q100'],r['d100'],r['splits'],r['near'],r['qs'],r['hold'],r['first'],r['qdead'],r['res'][-1])
  print('%-28s | %s | %s'%(n[:28],f(ra),f(rb)))
  for k,r in enumerate((ra,rb)):
   for key in ('e50','e100','h100','len100','q100','d100','splits','near','qs','hold'):T[k][key]+=r[key]
   CA[k].update(r['causes'])
 n=max(len(common),1)
 for k,name in enumerate((off,on)):
  print(name,'mean:',' '.join('%s %.1f'%(key,T[k][key]/n) for key in ('e50','e100','h100','len100','q100','d100','splits','near','qs','hold')),'| deaths within 3 rounds per 100 splits %.0f'%(100*T[k]['near']/max(T[k]['splits'],1)))
  print('   deaths r0-100 by length and cause (all maps):',', '.join('%s %d'%(c,v) for c,v in CA[k].most_common(12)))
