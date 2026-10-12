import sys
sys.dont_write_bytecode=True
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from summ import games
ex=[]
for label in sys.argv[1:]:
 for s in (0,1):
  C=Counter();ng=0
  for g in games(label):
   ng+=1
   for t in g['turns']:
    if t['side']!=s or t['queen'] or t['d1'] is None and not t['dead']:continue
    Lb='L2-3' if t['L']<=3 else 'L4+'
    d=t['d0']
    if d>3:continue
    ate=sum(t['eats'].values())>0;foe=any(z[1]!=s for z in t['near_heads']);mate=any(z[1]==s for z in t['near_heads'])
    for key in ((Lb,d,'all'),(Lb,d,'foe in view' if foe else 'mate only' if mate else 'alone')):
     C[key+('n',)]+=1;C[key+('ate',)]+=ate;C[key+('closer',)]+=ate or (t['d1'] is not None and t['d1']<d);C[key+('split',)]+=t['split'];C[key+('dead',)]+=t['dead']
    if s==0 and d==1 and not ate and not t['split'] and not foe and Lb=='L2-3' and len(ex)<12:ex.append((label,g['gid'],g['map'],t['r'],t['id'],t['h'],t['end'],mate))
  print('==',label,'side',s,'non-queen turns starting 1/2/3 steps from a pearl, per game')
  for Lb in ('L2-3','L4+'):
   for d in (1,2,3):
    print('  %s d=%d '%(Lb,d)+' | '.join('%s: n %.1f ate %2.0f%% closer %2.0f%% split %2.0f%% died %2.0f%%'%(w,C[(Lb,d,w,'n')]/ng,100*C[(Lb,d,w,'ate')]/max(1,C[(Lb,d,w,'n')]),100*C[(Lb,d,w,'closer')]/max(1,C[(Lb,d,w,'n')]),100*C[(Lb,d,w,'split')]/max(1,C[(Lb,d,w,'n')]),100*C[(Lb,d,w,'dead')]/max(1,C[(Lb,d,w,'n')])) for w in ('all','alone','mate only','foe in view')))
print('examples (ours, L2-3, pearl 1 step away, no foe in view, did not eat):')
for e in ex:print('  ',e)
