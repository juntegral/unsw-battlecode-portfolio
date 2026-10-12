import json,statistics,collections
from pathlib import Path
O=Path('data/codex/astra/band');gs=list(map(json.loads,(O/'games.jsonl').read_text().splitlines()))
mean=lambda a:round(statistics.mean(a),2) if a else None
med=lambda a:statistics.median(a) if a else None

def snap(g,r,s=1,k=0):
 v=g['snapshots'].get(str(r));return None if v is None else v[('us','them')[s]][('alive','total','longest','queen_length')[k]]
def meansnap(G,r,s=1,k=0):return mean([v for g in G if (v:=snap(g,r,s,k)) is not None])
def summary(G):
 D=[d for g in G for d in g['deaths'] if d[1]==1]
 R=[d for g in G for d in g['deaths'] if d[1]==0 and d[4]=='rammed']
 feeds=[p for g in G for p in g['qfeeds']]
 E=[e for g in G for e in g['eats'] if e[1]==1 and e[2]=='q']
 turns=sum(g['turns'][1] for g in G)
 late=[d for d in D if d[0]>=350 and d[16]>=0 and d[16]<=3 and d[17]>=10]
 G350=[g for g in G if g['last']>=350]
 return dict(n=len(G),ranked=sum(g['ranked'] for g in G),ours=collections.Counter(g['result'] for g in G),bots=collections.Counter(g['bot'] for g in G),opponent_bots=collections.Counter(g['opponent_bot'] for g in G),
  split=med([min(z[0] for z in g['splits'] if z[1]==1) for g in G if any(z[1]==1 for z in g['splits'])]),
  split_n=sum(any(z[1]==1 for z in g['splits']) for g in G),h25=meansnap(G,25),h50=meansnap(G,50),
  pearls50=mean([sum(e[1]==1 and e[0]<=50 for e in g['eats']) for g in G if g['last']>=50]),
  natural50=mean([sum(e[1]==1 and e[0]<=50 and e[3]=='n' for e in g['eats']) for g in G if g['last']>=50]),
  turns=turns,rams=len(R),ram_rate=round(len(R)/turns*1000,2),ram24=sum(2<=d[18][0]<=4 for d in R),ram24_pct=round(sum(2<=d[18][0]<=4 for d in R)/len(R)*100,1) if R else None,
  paid_rams=sum(d[18][1]>(d[18][0]+3)//4 for d in R),paid_ram_pct=round(sum(d[18][1]>(d[18][0]+3)//4 for d in R)/len(R)*100,1) if R else None,actual_paid_rams=sum(d[18][2]>0 for d in R),
  paid_turns=sum(sum(p[1]==1 for p in g['paids']) for g in G),paid_turn_pct=round(sum(sum(p[1]==1 for p in g['paids']) for g in G)/turns*100,2),
  queen_rams=sum(d[6] for d in R),q_alive=sum(g['ends'][1][3]>0 for g in G),q300=meansnap(G,300,k=3),n300=sum(g['last']>=300 for g in G),qend=mean([g['ends'][1][3] for g in G]),
  qfood=collections.Counter(e[3] for e in E),qdonors=collections.Counter((p['drop_side']+':'+p['cause']+':'+str(p['other'])) for p in feeds),
  h350=meansnap(G,350),n350=len(G350),hend350=mean([g['ends'][1][0] for g in G350]),hend=mean([g['ends'][1][0] for g in G]),longest=mean([g['ends'][1][2] for g in G]),
  late_stop=sum(d[4]=='stop' for d in late),late_self=sum(d[4]=='own body' for d in late),late_wall=sum(d[4]=='wall' for d in late),late_matebody=sum(d[4]=='mate body' for d in late),
  walls=sum(d[4]=='wall' for d in D),deaths=len(D),wall_pct=round(sum(d[4]=='wall' for d in D)/len(D)*100,1),
  loss=collections.Counter(g['how'] for g in G if g['result']=='loss'),turn_med=med([g['turn_round'] for g in G if g['turn_round'] is not None]),
  turn_rounds=[[g['gid'],g['turn_round'],g['how']] for g in G if g['result']=='loss'],
  early_gaps=[[g['gid'],sum(e[0]<=50 and e[1]==0 for e in g['eats']),sum(e[0]<=50 and e[1]==1 for e in g['eats'])] for g in G],
  our_queen_death=collections.Counter(next((d['cause'] for d in g['queen_deaths'] if d['side']=='us'),'alive') for g in G),
  losses_our_queen_alive=sum(g['result']=='loss' and g['ends'][0][3]>0 for g in G),
  loss_early_behind=sum(g['result']=='loss' and sum(e[0]<=50 and e[1]==0 for e in g['eats'])<sum(e[0]<=50 and e[1]==1 for e in g['eats']) for g in G))
S={name:summary([g for g in gs if g['opp']==name]) for name in sorted({g['opp'] for g in gs})}
(O/'summary.json').write_text(json.dumps(S,ensure_ascii=False,indent=2))
for name,s in S.items():
 print(name,json.dumps({k:v for k,v in s.items() if k not in ('early_gaps','turn_rounds')},ensure_ascii=False))
print('SUBSETS')
for label in sorted({g['src'] for g in gs}):
 G=[g for g in gs if g['src']==label];print(label,len(G),G[0]['opp'],dict(collections.Counter(g['result'] for g in G)))
