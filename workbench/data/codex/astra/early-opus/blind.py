import sys
sys.dont_write_bytecode=True
from collections import Counter,defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summ import games
def heading(t,W,H):
 if len(t['moves'])!=1 or t['end'] is None:return None
 dx=(t['end'][0]-t['h'][0]+W//2)%W-W//2;dy=(t['end'][1]-t['h'][1]+H//2)%H-H//2
 return (dx,dy) if abs(dx)+abs(dy)==1 else None
for label in sys.argv[1:]:
 for s in (0,1):
  C=Counter();maps=defaultdict(Counter)
  for g in games(label):
   W,H=g['size'];prev={}
   for t in g['turns']:
    if t['side']!=s:continue
    hd=heading(t,W,H);p=prev.get(t['id']);prev[t['id']]=(t['r'],hd)
    if t['d1'] is None or t['d0']>=99 or t['L']>3 or t['queen']:continue
    ph='r0-11' if t['r']<12 else 'r12-50' if t['r']<=50 else 'r51-100'
    cls='sight' if t['d0']<=3 else 'near4-8' if t['d0']<=8 else 'far9+'
    for key in ((ph,cls),('all',cls)):
     C[key+('n',)]+=1
     ate=sum(t['eats'].values())>0
     C[key+('closer',)]+=ate or t['d1']<t['d0']
     C[key+('ate',)]+=ate
     if p and p[0]==t['r']-1 and p[1] and hd:
      C[key+('hn',)]+=1;C[key+('straight',)]+=p[1]==hd;C[key+('back',)]+=p[1]==(-hd[0],-hd[1])
    maps[g['map']][cls]+=1;maps[g['map']]['n']+=1
  print('==',label,'side',s,'(non-queen dragons of length 2-3)')
  for ph in ('r0-11','r12-50','r51-100','all'):
   tot=sum(C[(ph,c,'n')] for c in ('sight','near4-8','far9+'))
   print('  %-8s'%ph+' | '.join('%s: %4.1f%% of turns, closer %4.1f%%, ate %4.1f%%, straight %4.1f%%, reverse-ish %4.1f%%'%(c,100*C[(ph,c,'n')]/max(tot,1),100*C[(ph,c,'closer')]/max(C[(ph,c,'n')],1),100*C[(ph,c,'ate')]/max(C[(ph,c,'n')],1),100*C[(ph,c,'straight')]/max(C[(ph,c,'hn')],1),100*C[(ph,c,'back')]/max(C[(ph,c,'hn')],1)) for c in ('sight','near4-8','far9+')))
  print('  far9+ share per map:',' '.join('%s %.0f'%(m[:8],100*c['far9+']/c['n']) for m,c in maps.items()))
