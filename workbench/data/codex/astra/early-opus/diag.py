import sys
sys.dont_write_bytecode=True
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import local
WHY={0:'?',1:'safezone',2:'queen rule',3:'round/len/leader',4:'qh scout',5:'ring wary',6:'QS_KEEP',7:'grow round',8:'soft limit',9:'eat before split',10:'harvesting',11:'cannot split/queen boot',12:'child exit/room',13:'child spans portal',14:'tail at portal'}
for name,g in local.rows('diag').items():
 C=Counter();n=0;room=Counter();Lc=Counter()
 for t in g['turns']:
  if t['side']!=0 or t['L']<4 or t['split']:continue
  n+=1;logs=[l for l in t['logs'] if 'NOSPLIT' in l]
  if not logs:C['no log: act() returned before the split check (queen='+str(int(t['queen']))+')']+=1;continue
  q=logs[0].split();why=int(q[-3]);C[WHY[why]+(' q' if t['queen'] else '')]+=1
  if why==12:room[q[-1][:4]]+=1;Lc[t['L']]+=1
 print(name,'L>=4 turns without a split:',n)
 for k,v in C.most_common():print('   %4d %s'%(v,k))
 print('   child exit/room: tail_room values',room.most_common(8),'lengths',sorted(Lc.items()))
 print('   sample log',next((l for t in g['turns'] for l in t['logs'] if 'NOSPLIT' in l),None))
