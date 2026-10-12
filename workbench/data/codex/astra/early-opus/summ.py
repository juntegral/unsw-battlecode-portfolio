import sys,json,statistics as st
from pathlib import Path
from collections import Counter,defaultdict
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
def games(label):
 for mp in sorted((ROOT/'data/online/smoke'/(label+'-old')).glob('game-*.json')):
  j=json.loads(mp.read_text());f=OUT/('%d.json'%j['id'])
  if f.exists():yield json.loads(f.read_text())
def snap(g,r):
 ks=sorted(int(k) for k in g['snaps'] if 'q' in g['snaps'][k]);r=min(r,ks[-1]);return g['snaps'][str(r)]
def measure(g,s):
 m={}
 T=[t for t in g['turns'] if t['side']==s]
 for r in (25,50,75,100):
  m['eat%d'%r]=sum(1 for e in g['eats'] if e['side']==s and e['r']<=r)
  m['nat%d'%r]=sum(1 for e in g['eats'] if e['side']==s and e['r']<=r and e['origin']=='natural')
  sn=snap(g,r);m['heads%d'%r]=sn['heads'][s];m['len%d'%r]=sn['length'][s]
  m['q%d'%r]=sn['q'][s]
 for r in (25,50):
  sn=snap(g,r);hd=[x for x in sn['homed'][s] if x<99];m['home%d'%r]=sum(hd)/len(hd) if hd else None
  m['qhome%d'%r]=sn['qhome'][s]
  ls=sn['lens'][s];m['L2share%d'%r]=sum(1 for x in ls if x<=2)/len(ls) if ls else None;m['maxL%d'%r]=max(ls) if ls else 0
 S=[x for x in g['splits'] if x['side']==s]
 for r in (25,50,100):m['splits%d'%r]=sum(1 for x in S if x['r']<=r)
 m['split1']=min((x['r'] for x in S),default=None)
 m['splitL']=sum(x['L'] for x in S)/len(S) if S else None
 m['splitL4']=sum(1 for x in S if x['L']==4)/len(S) if S else None
 m['splitL5p']=sum(1 for x in S if x['L']>=5)
 m['child']=sum(x['parts'][1] for x in S)/len(S) if S else None
 # turns holding 4+ without splitting
 m['hold4']=sum(1 for t in T if t['L']>=4 and not t['split'])
 m['turns']=len(T)
 A=[t for t in T if t['d1'] is not None and t['d0']<99]
 m['stall']=sum(1 for t in A if sum(t['eats'].values())==0 and t['d1']>=t['d0'])/len(A) if A else None
 m['still']=sum(1 for t in T if not t['moves'] and not t['split'] and not t['dead'])/len(T) if T else None
 m['mate3']=sum(1 for t in T if t['mate']<=3)/len(T) if T else None
 m['mate1']=sum(1 for t in T if t['mate']<=1)/len(T) if T else None
 m['d0']=sum(min(t['d0'],40) for t in T)/len(T) if T else None
 m['far8']=sum(1 for t in T if t['d0']>8)/len(T) if T else None
 P=[t for t in T if t['paid']>0]
 m['paidturns']=len(P);m['paid']=sum(t['paid'] for t in P)
 m['paid_eat']=sum(1 for t in P if sum(t['eats'].values())>0)
 m['paid_kill']=sum(1 for t in P if t['kills']>0)
 m['paid_died']=sum(1 for t in P if t['dead'] and not t['kills'])
 m['paid_none']=sum(1 for t in P if not t['dead'] and not t['kills'] and not sum(t['eats'].values()))
 m['paid_eaten']=sum(sum(t['eats'].values()) for t in P)
 m['steps']=sum(len(t['moves']) for t in T)/len(T) if T else None
 m['qeat']=sum(sum(t['eats'].values()) for t in T if t['queen'])
 D=[d for d in g['deaths'] if d['side']==s and d['r']<=100]
 m['deaths']=len(D);m['deathmass']=sum(d['L'] for d in D)
 m['causes']=Counter(d['cause'] for d in D)
 m['dL2']=sum(1 for d in D if d['L']<=2)
 m['eat_per_turn']=100*m['eat100']/len(T) if T else None
 m['nat_per_turn']=100*m['nat100']/len(T) if T else None
 return m
KEYS=['eat25','eat50','eat75','eat100','nat25','nat50','nat100','heads25','heads50','heads75','heads100','len25','len50','len75','len100','splits25','splits50','splits100','split1','splitL','splitL4','splitL5p','child','hold4','turns','stall','still','mate3','mate1','d0','far8','steps','paidturns','paid','paid_eat','paid_kill','paid_died','paid_none','paid_eaten','home25','home50','L2share25','L2share50','maxL25','maxL50','q25','q50','q100','qhome25','qhome50','qeat','deaths','deathmass','dL2','eat_per_turn','nat_per_turn']
def mean(xs):
 xs=[x for x in xs if x is not None];return sum(xs)/len(xs) if xs else float('nan')
if __name__=='__main__':
 for label in sys.argv[1:]:
  rows=[]
  for g in games(label):
   u=measure(g,0);t=measure(g,1);rows.append((g,u,t))
  print('==',label,len(rows),'games   (us / them, mean per game; maps where us<them / us>them)')
  for k in KEYS:
   lo=sum(1 for g,u,t in rows if u[k] is not None and t[k] is not None and u[k]<t[k]);hi=sum(1 for g,u,t in rows if u[k] is not None and t[k] is not None and u[k]>t[k])
   print('  %-12s %8.2f / %8.2f   %2d<  %2d>'%(k,mean([u[k] for g,u,t in rows]),mean([t[k] for g,u,t in rows]),lo,hi))
  cu=Counter();ct=Counter()
  for g,u,t in rows:cu.update(u['causes']);ct.update(t['causes'])
  print('  death causes us',dict(cu));print('  death causes them',dict(ct))
  print('  per map: map | eat50 eat100 | heads50 heads100 | len100 | splits50 | stall%% | mate3%% | paid | deaths | q100   (us/them)')
  for g,u,t in rows:
   print('  %-16s %3d/%3d %3d/%3d | %2d/%2d %2d/%2d | %3d/%3d | %2d/%2d | %2.0f/%2.0f | %2.0f/%2.0f | %2d/%2d | %2d/%2d | %d/%d'%(g['map'][:16],u['eat50'],t['eat50'],u['eat100'],t['eat100'],u['heads50'],t['heads50'],u['heads100'],t['heads100'],u['len100'],t['len100'],u['splits50'],t['splits50'],100*(u['stall'] or 0),100*(t['stall'] or 0),100*(u['mate3'] or 0),100*(t['mate3'] or 0),u['paid'],t['paid'],u['deaths'],t['deaths'],u['q100'],t['q100']))
