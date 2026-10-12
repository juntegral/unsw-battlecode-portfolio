import sys,json
from collections import Counter
sys.path.insert(0,'data/codex/astra/early-opus')
from summ import games
for label in sys.argv[1:]:
 for s in (0,1):
  C=Counter();L=Counter();R=Counter();FE=Counter();M=Counter();mass=0;n=0;Q=0;mapc=Counter()
  for g in games(label):
   for d in g['deaths']:
    if d['side']!=s or d['r']>100:continue
    key=d['cause'] if d['cause'] in('wall','own body','illegal split','mate body','mate head') else 'fight'
    C[key]+=1
    if key in('wall','own body','illegal split'):
     n+=1;L[min(d['L'],6)]+=1;R[d['r']//25]+=1;FE[d['free_exits']]+=1;mass+=d['L'];mapc[g['map'][:10]]+=1
     hs=[t2 for t2 in g['turns'] if t2['id']==d['id'] and t2['r']==d['r']]
     if hs:M[min(hs[0]['heads'],60)//10*10]+=1;Q+=hs[0]['queen']
  print(label,'side',s,dict(C),'| self-kills',n,'mass',mass,'queen',Q,'L',sorted(L.items()),'round/25',sorted(R.items()),'free exits',sorted(FE.items()),'heads',sorted(M.items()));print('   maps',dict(mapc))
