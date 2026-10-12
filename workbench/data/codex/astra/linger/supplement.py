import sys
sys.dont_write_bytecode=True
import json
from collections import defaultdict,Counter
from statistics import median,mean
from analyze import OUT
from summarize import G,opp,size,band,pct,rate
rows=[]
for label in sorted({g['label'] for g in G}):
 for z in ('≤1200','>1200'):
  gs=[g for g in G if g['label']==label and size(g)==z]
  for s in (0,1):
   bs=[b for g in gs for b in g['births'] if b['prev_s']==s]
   rows.append(dict(label=label,size=z,side=s,n=len(bs),near1=sum(b['near'][s]<=1 for b in bs),near3=sum(b['near'][s]<=3 for b in bs),same=sum(b['eat_i']==b['prev_i'] for b in bs),own=sum(b['eat_s']==s for b in bs),lost=sum(b['eat_s']==1-s for b in bs)))
(OUT/'by-version.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
lines=['[M] one5-d1 15판만의 재생 코호트. 우리 / 상대; 분모는 각 팀이 직전에 먹었던 칸의 재생 수.','', '|칸 수|생성 r|N|≤1%|≤3%|팀 회수%|','|---|---|---|---|---|---|']
for z in ('≤1200','>1200'):
 for br in ('0–50','51–150','151–300'):
  vs=[[b for g in G if g['label']=='one5-d1' and size(g)==z for b in g['births'] if b['prev_s']==s and band(b['r'])==br] for s in (0,1)]
  vals=[z,br,' / '.join(str(len(v)) for v in vs)]
  for d in (1,3):vals.append(' / '.join(rate(v,lambda b:b['near'][s]<=d) for s,v in enumerate(vs)))
  vals.append(' / '.join(rate(v,lambda b:b['eat_s']==s) for s,v in enumerate(vs)))
  lines.append('| '+' | '.join(vals)+' |')
lines+=['','[M] 강제 반경 3·최대 8라운드 체류의 기회비용 노출: 실제 재생 라운드 이전까지만(재생 없으면 8라운드) 원 용이 반경 밖 자연 진주를 먹었는가. 중복되는 식사 창이며, 팀의 확정 손실량이 아니다.','','|상대|칸 수|완전 식사 창|밖에서 먹은 창|비율%|밖에서 먹은 진주(중복 창)|','|---|---|---|---|---|---|']
for o in ('WHQ','dev1'):
 for z in ('≤1200','>1200'):
  ms=[(g,m) for g in G if opp(g)==o and size(g)==z for m in g['meals'] if m['s']==0 and m['r']+8<=g['rounds']]
  costs=[]
  for g,m in ms:
   until=min(m['r']+8,g['births'][m['birth']]['r']-1 if m['birth']>=0 else m['r']+8)
   costs.append(sum(e[2]>3 and e[0]<=until for e in m['elsewhere']))
  n=sum(x>0 for x in costs)
  lines.append(f'|{o}|{z}|{len(ms)}|{n}|{pct(n,len(ms))}|{sum(costs)}|')
lines+=['','[M] 거리 분포의 분모: 각 식사 후 라운드의 살아 있는 동일 ID만. 평균은 13에서 잘린 거리 평균.','','|상대|칸 수|팀|각 +1…+8 생존 식사 수|거리 평균 +1…+8|','|---|---|---|---|---|']
for o in ('WHQ','dev1'):
 for z in ('≤1200','>1200'):
  for s in (0,1):
   ms=[m for g in G if opp(g)==o and size(g)==z for m in g['meals'] if m['s']==s and m['r']+8<=g['rounds']]
   ds=[[m['d'][t] for m in ms if m['d'][t]>=0] for t in range(8)]
   lines.append('| '+' | '.join([o,z,str(s),'/'.join(str(len(d)) for d in ds),'/'.join(f'{mean(d):.2f}' for d in ds)])+' |')
(OUT/'supplement.md').write_text('\n'.join(lines)+'\n')
