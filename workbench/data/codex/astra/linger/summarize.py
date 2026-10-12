import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
from collections import defaultdict,Counter
from statistics import median,mean
from analyze import OUT
G=[json.loads(p.read_text()) for p in sorted(OUT.glob('g*.json'))]
C=[json.loads(p.read_text()) for p in sorted(OUT.glob('clear*.json'))]
def opp(g):return 'WHQ' if 'Quizzes' in g['opp'] else 'dev1'
def size(g):return '≤1200' if g['cells']<=1200 else '>1200'
def band(r):return '0–50' if r<=50 else '51–150' if r<=150 else '151–300'
def pct(n,d):return f'{100*n/d:.1f}' if d else 'NA'
def rate(v,p):return pct(sum(p(x) for x in v),len(v))
lines=[]
def table(header,rows):
 lines.append('| '+' | '.join(header)+' |');lines.append('|'+'|'.join(['---']*len(header))+'|')
 for row in rows:lines.append('| '+' | '.join(map(str,row))+' |')
 lines.append('')
bs=defaultdict(list);ms=defaultdict(list);cs=defaultdict(list)
for g in G:
 for b in g['births']:bs[opp(g),size(g),band(b['r']),b['prev_s']].append(b)
 for m in g['meals']:
  if m['r']+8<=g['rounds']:ms[opp(g),size(g),m['s']].append((g,m))
for g in C:
 for c in g['records']:cs[opp(g),size(g),c['s']].append(c)
lines.append('[M] 재생 진주: 각 칸의 직전 섭취 팀별 코호트. 셀은 우리 / 상대. 회수는 해당 코호트 팀 / 반대 팀 / 끝까지 미섭취 %. 거리: 생성 순간 몸을 통과하지 않는 벽·포털 경로.\n')
rows=[]
for o in ('WHQ','dev1'):
 for z in ('≤1200','>1200'):
  for band_ in ('0–50','51–150','151–300'):
   vs=[bs[o,z,band_,s] for s in (0,1)]
   rows.append([o,z,band_,' / '.join(str(len(v)) for v in vs),
    ' / '.join(rate(v,lambda b:b['near'][s]<=1) for s,v in enumerate(vs)),
    ' / '.join(rate(v,lambda b:b['near'][s]<=3) for s,v in enumerate(vs)),
    ' / '.join(','.join(rate(v,lambda b:b['eat_s']==t) for t in (s,1-s,-1)) for s,v in enumerate(vs))])
table(['상대','칸 수','생성 r','N 우리/상대','≤1 %','≤3 %','재섭취 자기,상대,미섭취 %'],rows)
lines.append('[M] 자연 진주 식사 후 동일 ID: r+1…r+8 종료 시 거리 중앙값(생존자; 벽·포털, 몸 무시, 13=13 이상/단절). 완전한 8라운드 관측 창만 포함; 죽음은 별도. 탐색=해당 용의 이후 시야가 팀이 아직 본 적 없는 칸을 공개.\n')
rows=[]
for k,gm in sorted(ms.items()):
 v=[m for g,m in gm];ds=[median(m['d'][i] for m in v if m['d'][i]>=0) if any(m['d'][i]>=0 for m in v) else -1 for i in range(8)]
 rows.append([*k,len(v),'/'.join(f'{x:g}' for x in ds),rate(v,lambda m:m['d'][7]<0),rate(v,lambda m:bool(m['splits'])),rate(v,lambda m:m['newtiles']>0),rate(v,lambda m:any(e[2]>3 for e in m['elsewhere'])),rate(v,lambda m:m['discover_far']>0)])
table(['상대','칸 수','팀 0=우리','식사 N','거리 +1…+8','8내 사망%','분열%','탐색%','3밖 다른 진주 먹음%','3밖 첫 발견 진주%'],rows)
lines.append('[M] 대칭 칸 생성으로 확인한 다음 라운드 생성 시도: 전 라운드 빈 칸에 1걸음 인접한 머리가 있었던 팀·칸·라운드. 회수는 진입하지 않고 실제 생성된 경우만; 생존 인접 후보의 거리.\n')
rows=[]
for k,v in sorted(cs.items()):
 off=[c for c in v if not c['entered']];born=[c for c in off if c['born']]
 rows.append([*k,len(v),rate(v,lambda c:c['entered']),len(off),rate(off,lambda c:c['candidate_d']<=3),len(born),rate(born,lambda c:c['eat_s']==c['s']),rate(born,lambda c:c['eat_s']==c['s'] and c['eat_r']<=c['r']+1),rate(born,lambda c:c['eat_s']==c['s'] and c['eat_i'] in c['ids'])])
table(['상대','칸 수','팀','기회 N','진입%','비진입 N','후보 ≤3%','비진입·생성 N','팀 회수%','생성+1내 회수%','원 후보 회수%'],rows)
(OUT/'tables.md').write_text('\n'.join(lines))

extra=[]
for g in G:
 for s in (0,1):
  v=[b for b in g['births'] if b['prev_s']==s]
  extra.append(dict(label=g['label'],gid=g['gid'],map=g['map'],size=size(g),side=s,n=len(v),near1=sum(b['near'][s]<=1 for b in v),near3=sum(b['near'][s]<=3 for b in v),own=sum(b['eat_s']==s for b in v),lost=sum(b['eat_s']==1-s for b in v)))
(OUT/'per-game.json').write_text(json.dumps(extra,ensure_ascii=False,indent=2))
print('GAMES',dict(Counter(g['label'] for g in G)),len(G),'CLEAR',len(C))
print('COUNTERS',sum(g['countdown_events'] for g in G),'MIRROR CHECKS',sum(g['checked'] for g in C),'BAD',sum(g['bad'] for g in C))
for o in ('WHQ','dev1'):
 for z in ('≤1200','>1200'):
  for s in (0,1):
   v=[b for g in G if opp(g)==o and size(g)==z for b in g['births'] if b['prev_s']==s]
   lost=[b for b in v if b['eat_s']==1-s]
   avail=[b for b in lost if b['eater_d']>=0 and b['gap']<=8]
   print('COHORT',o,z,s,'N',len(v),'near1/3',rate(v,lambda b:b['near'][s]<=1),rate(v,lambda b:b['near'][s]<=3),'own',rate(v,lambda b:b['eat_s']==s),'same',rate(v,lambda b:b['eat_i']==b['prev_i']),'lost',len(lost),'alive_gap8_lost',len(avail),'no-near recovered',rate([b for b in v if b['near'][s]>3],lambda b:b['eat_s']==s))
# Replay examples include return, replacement, loss while alive, and exploration.
examples=defaultdict(list)
for g in sorted(G,key=lambda g:(not g['label'].startswith('one5'),not g['label'].startswith('one4'),g['gid'])):
 for m in g['meals']:
  if m['s'] or m['birth']<0:continue
  b=g['births'][m['birth']]
  kinds=[]
  if b['eat_s']==0 and b['eat_i']==m['i'] and 2<=b['gap']<=8:kinds.append('same_return')
  if b['eat_s']==0 and b['eat_i']!=m['i'] and b['gap']<=8 and b['eater_d']>3:kinds.append('replacement')
  if b['eat_s']==1 and b['gap']<=8 and b['eater_d']>3:kinds.append('lost_alive')
  if m['newtiles'] and any(e[2]>3 for e in m['elsewhere']) and b['eat_s']==0:kinds.append('explore_paid')
  for kind in kinds:
   if len(examples[kind])<10 and not any(e['gid']==g['gid'] for e in examples[kind]):examples[kind].append(dict(gid=g['gid'],label=g['label'],map=g['map'],w=g['w'],meal=m,birth=b))
for g in sorted(C,key=lambda g:(not g['label'].startswith('one5'),g['gid'])):
 for c in g['records']:
  if c['s']:continue
  kind='clear_return' if not c['entered'] and c['born'] and c['eat_s']==0 and c['eat_i'] in c['ids'] else 'clear_lost' if not c['entered'] and c['born'] and c['eat_s']==1 else 'clear_enter' if c['entered'] else ''
  if kind and len(examples[kind])<10 and not any(e['gid']==g['gid'] for e in examples[kind]):examples[kind].append(dict(gid=g['gid'],label=g['label'],map=g['map'],w=g['w'],case=c))
(OUT/'examples.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2))
print('EXAMPLES written')
