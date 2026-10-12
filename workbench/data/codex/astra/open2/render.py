import json,sys,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
G=sorted([json.loads(p.read_text()) for p in P.glob('[0-9]*.json')],key=lambda g:g['gid'])
assert len(G)==45 and len({g['gid'] for g in G})==45
sets={'Cache': [g for g in G if '-c' in g['label']], 'Preyas':[g for g in G if g['label']=='one8-p1']}
CA=['wall','own body','mate body','foe body','mate head','rams','rammed','illegal split','other']
def snap(g,r):return g['snaps'].get(str(r),g['snaps'][str(max(map(int,g['snaps'])))])
def nums(gs,s,key,lo=0,hi=100):return sum(t[key] for g in gs for t in g['turns'] if t['side']==s and lo<=t['r']<=hi)
def evs(gs,s,kind,lo=0,hi=100):return [t for g in gs for t in g[kind] if t['side']==s and lo<=t['r']<=hi]

def ledger(gs):
 n=len(gs);a=['|구간|끝 머리|자연 섭취|사체 섭취|분열|사망|진주 3걸음 머리|진주 최단거리 몫 %|','|---|---|---|---|---|---|---|---|']
 for lo,hi in [(0,0)]+[(r-9,r) for r in range(10,101,10)]:
  values=[]
  for s in (0,1):
   es=evs(gs,s,'eats',lo,hi);v=[sum(snap(g,hi)['heads'][s] for g in gs)/n,sum(x['origin']=='natural' for x in es)/n,sum(x['origin']=='corpse' for x in es)/n,len(evs(gs,s,'splits',lo,hi))/n,len(evs(gs,s,'deaths',lo,hi))/n,sum(snap(g,hi)['near3'][s] for g in gs)/n,100*sum(snap(g,hi)['nearest'][s] for g in gs)/max(1,sum(snap(g,hi)['bearing'] for g in gs))];values.append(v)
  a.append('|%d–%d|'%(lo,hi)+'|'.join(f'{values[0][k]:.1f}/{values[1][k]:.1f}' for k in range(7))+'|')
 return '\n'.join(a)
def dtable(gs):
 a=['|구간|벽|자기 몸|아군 몸|적 몸|아군 머리|능동 램|피램|불법 분열|기타|','|---|---|---|---|---|---|---|---|---|---|']
 for lo,hi in [(0,0)]+[(r-9,r) for r in range(10,101,10)]:
  cs=[Counter(x['cause'] for x in evs(gs,s,'deaths',lo,hi)) for s in (0,1)]
  a.append('|%d–%d|'%(lo,hi)+'|'.join(f'{cs[0][k]}/{cs[1][k]}' for k in CA)+'|')
 return '\n'.join(a)
ld=['[M] 모든 값 우리/상대. 머리·섭취·분열·사망은 판당 평균; 사인표는 합계. r은 기보의 0 기반 라운드. r0 별도, 이후 10라운드 구간. 조기 종료판의 끝 상태는 r100까지 유지하고 새 사건은 더하지 않았다.','[M] 진주 칸=그 시점 실제 진주가 있는 칸(자연+사체). 거리=켈프와 포털을 반영한 정적 최단 걸음, 몸·시야·위협 제외. 최단거리 몫은 해당 진주 칸에서 단독으로 더 가까운 팀의 비율; 동률·양팀 도달불가 별도 제외 없이 분모에 포함. 생성 가능한 모든 칸의 영토 점유율과는 다르다.']
for label,gs in list(sets.items())+[(l,[g for g in G if g['label']==l]) for l in ('one8-c2','one10-c1')]:ld+=['\n[M] '+label+' '+str(len(gs))+'판',ledger(gs),'\n[M] 사인별 합계',dtable(gs)]
(P/'ledger.md').write_text('\n\n'.join(ld)+'\n')

# Each observed refusal gets an explicit uncertainty-preserving label.
gates=Counter(t['gate'] for g in G for t in g['turns'] if t['side']==0 and t['L']>=4 and not t['split'])
sg=['[M] L≥4 무분열 차례 전수. 아래는 우선순위를 정한 **관측 조건 분류**이며 실행된 return 문의 확정 집계가 아니다. [C] 두 소스의 DEBUG_LOG=false이고 [M] 대상 r0–100의 dragonLog는 0건이다.','|판정 가능한 조건/미확정|Cache|Preyas|코드 위치(one8 / one10)|','|---|---:|---:|---|']
locs={'QS_KEEP_LEN eligible (ring/early-return precedence unknown)':'1862 / 1883; 상수 150–153 / 153–156','child_spans_portal geometry (precedence unknown)':'1901 / 1922; 1941 / 1978','child_has_exit geometry (memory/precedence unknown)':'1897 / 1918; 1930 / 1967','CHILD_MIN_ROOM geometry (memory/precedence unknown)':'1897 / 1918; 실제 tail_room 2027 / 2064','portal-adjacent (exception/precedence unknown)':'1905 / 1926; one10 예외 1927','unresolved internal gate or earlier action':'act 1334–1568 / 1348–1579; harvesting_now 1884 / 1905'}
for k in gates:sg.append('|'+k+'|'+'|'.join(str(sum(t['gate']==k for g in gs for t in g['turns'] if t['side']==0 and t['L']>=4 and not t['split'])) for gs in sets.values())+'|'+locs[k]+'|')
sg+=['[C] one8: `QS_KEEP_MIN_UNITS:2`, 포털 예외 없음, `SHORT_EVADE:false`. one10: `QS_KEEP_MIN_UNITS:6`, `SPLIT_PORTAL_OK:true`, `SHORT_EVADE:true`. 따라서 one11 설정을 소급하지 않았다.','[C] 관문 순서(one10:1866–1945): safezone → queen guard → round/length/leader → QH → ring → QS_KEEP → grow round → unit cap → EAT_BEFORE_SPLIT → harvesting → can_split/queen_boot → tail unseen 허용 → child exit/room → child portal span → tail portal. [C] QG_SAFEZONE=false, QH는 QUEEN_AVENGE=8 때문에 qh_watch:2914–2922에서 꺼짐(one8:2877); EAT_BEFORE_SPLIT=false; grow_round는 150/300이고 LC_* 조기전환은 꺼짐. 이들 관문은 r0–100 원인이 아니다.','[E] QS_KEEP 조건은 값으로 확인되지만 그 앞의 ring 또는 hunt/ram 반환이 실제 원인일 수 있다. 나머지 기하 분류는 전체 판면이며 봇의 기억, enter_time, survey 및 사전 반환과 같다고 가정하지 않는다. tail_room 표값은 전체 상태에서 몸을 고정한 거리≤8 BFS이며 코드의 가중 미관측 공간값과 다르다.','|출전 집단·분열 전 길이|우리 횟수|상대 횟수|','|---|---:|---:|']
for label,gs in sets.items():
 cs=[Counter(x['L'] for x in evs(gs,s,'splits')) for s in (0,1)]
 for L in sorted(cs[0].keys()|cs[1].keys()):sg.append(f'|{label} L{L}|{cs[0][L]}|{cs[1][L]}|')
sg+=['|집단|L≥4 무분열 우리/상대|전체 분열 우리/상대|','|---|---|---|']
for label,gs in sets.items():sg.append('|'+label+'|'+'/'.join(str(sum(t['L']>=4 and not t['split'] for g in gs for t in g['turns'] if t['side']==s)) for s in (0,1))+'|'+'/'.join(str(len(evs(gs,s,'splits'))) for s in (0,1))+'|')
(P/'split-gates.md').write_text('\n\n'.join(sg[:1])+'\n\n'+'\n'.join(sg[1:])+'\n')
with (P/'split-turns.jsonl').open('w') as f:
 for g in G:
  for t in g['turns']:
   if t['side']==0 and t['L']>=4 and not t['split']:f.write(json.dumps({'gid':g['gid'],'bot':g['bots'][g['ours']],**t},separators=(',',':'))+'\n')

# Ten cases per observed cause, prefer diverse games and immediate geometry.
dsout=['[M] 우리 사망 1,178건에서 사인별 10건(7종, 총 70건). 각 사인 안에서는 빈 출구가 적고 이른 사건부터, 가능한 한 서로 다른 판을 먼저 선택했다. 빈 출구는 정적 빈 인접칸 수이며 꼬리 전이를 반영한 합법 행동 수가 아니다.','[C] one8/one10 기본 이동 제출은 1582/1596, hunt 선행 반환 1334/1348, ram 선행 반환 1404/1418, 탈출 분열 1950/1987, 일반 분열 1845/1866. [E] 로그가 없으므로 아래 코드 연결은 후보이며 단일 선택항의 인과 확정은 불가하다.','|사인 [M]|game:r #id|L|위치→충돌칸|행위자|빈 출구|직전 자기 차례|규칙 때문인가 [E/C]|','|---|---|---:|---|---:|---:|---|---|']
for cause in CA:
 ds=[(g,d) for g in G for d in g['deaths'] if d['side']==0 and d['cause']==cause]
 if not ds:continue
 ds.sort(key=lambda z:(z[1]['free_exits'],z[1]['r'],z[0]['gid'],z[1]['id']))
 selected=[];seen=set()
 for g,d in ds:
  if g['gid'] not in seen:selected.append((g,d));seen.add(g['gid'])
  if len(selected)==10:break
 if len(selected)<10:
  for x in ds:
   if x not in selected:selected.append(x)
   if len(selected)==10:break
 for g,d in selected:
  t=d['lastturn'];ver='one10' if g['label']=='one10-c1' else 'one8'
  last='없음(출생 후 미행동)' if t is None else f"r{t['r']} L{t['L']} "+('분열' if t['split'] else 'NESW 방향='+str(t['dirs']))
  why='상대가 진입; 직전 이동/분열의 점수항 미확정' if cause=='rammed' else '능동 머리 충돌; hunt/ram/기본 이동 중 미확정' if cause=='rams' else '동료의 진입' if cause=='mate head' and d['id']!=d['actor'] else '충돌 이동을 제출; 기본 이동/후처리 중 미확정'
  if cause in ('wall','own body') and d['L']==2 and d['free_exits']==0:why='L2·빈칸 0; 분열 불가(최소 총 L4), 막힘 시 기본 이동과 일치; 진입 원인 미확정'
  dsout.append(f"|{cause}|{g['gid']}:r{d['r']} #{d['id']} ({ver})|{d['L']}|{d['h']}→{d['target']}|{d['actor']}|{d['free_exits']}|{last}|{why}|")
(P/'death-cases.md').write_text('\n\n'.join(dsout[:2])+'\n\n'+'\n'.join(dsout[2:])+'\n')

M=defaultdict(list)
for g in G:M[g['map']].append(g)
top=sorted(M,key=lambda k:-sum(sum(e['side']==1 for e in g['eats'])-sum(e['side']==0 for e in g['eats']) for g in M[k])/len(M[k]))[:5]
op=['[M] 45판의 지도별 평균 r0–100 총 섭취 격차 상위 5개. 각 지도 3판 모두 r0–20의 시작 개체 경로를 나란히 기록. N/E/S/W=0/1/2/3; S=분열, †=죽음. 좌표는 기보 원좌표로 양쪽 대칭변환을 하지 않았다. 먹이는 (자연,사체); 길이는 행동 전.','|지도|평균 섭취 격차|game|r0–20 섭취 우리/상대|분열|2걸음 이상 이동 차례|유료 질주 소모|','|---|---:|---|---|---|---|---|']
for name in top:
 gap=sum(sum(e['side']==1 for e in g['eats'])-sum(e['side']==0 for e in g['eats']) for g in M[name])/len(M[name])
 for g in M[name]:
  ts=[[t for t in g['turns'] if t['r']<=20 and t['side']==s] for s in (0,1)]
  op.append(f'|{name}|{gap:.1f}|{g["gid"]}|'+ '/'.join(str(sum(sum(t['eats'].values()) for t in a)) for a in ts)+'|'+'/'.join(str(sum(t['split'] for t in a)) for a in ts)+'|'+'/'.join(str(sum(len(t['moves'])>1 for t in a)) for a in ts)+'|'+'/'.join(str(sum(t['paid'] for t in a)) for a in ts)+'|')
for name in top:
 for g in M[name]:
  op+=['\n[M] '+name+' game '+str(g['gid']),'|r|우리 시작 개체: #id L 머리→종점 행동 먹이|상대 시작 개체|','|---|---|---|']
  for r in range(21):
   sides=[]
   for s in (0,1):
    a=[t for t in g['turns'] if t['r']==r and t['side']==s and t['starter']]
    sides.append('; '.join(f"#{t['id']} L{t['L']} {t['h']}→{t['end']} "+('S' if t['split'] else ''.join('NESW'[d] for d in t['dirs']))+f" ({t['eats']['natural']},{t['eats']['corpse']})" for t in a))
   op.append(f'|{r}|'+ '|'.join(sides)+'|')
  op+=['\n[M] 같은 진주 칸을 두 머리 이상이 먹은 기록(원래 시작 개체와 자손 포함).','|팀|칸|섭취 r:#id:출처|','|---|---|---|']
  found=False
  for s in (0,1):
   tiles=defaultdict(list)
   for e in g['eats']:
    if e['side']==s and e['r']<=20:tiles[tuple(e['xy'])].append(e)
   for c,es in tiles.items():
    if len({e['id'] for e in es})>1:
     found=True;op.append('|'+('우리' if s==0 else '상대')+'|'+str(c)+'|'+'; '.join(f"r{e['r']}:#{e['id']}:{e['origin']}" for e in es)+'|')
  if not found:op.append('|양쪽|—|없음|')
(P/'openings.md').write_text('\n\n'.join(op[:1])+'\n\n'+'\n'.join(op[1:])+'\n')

manifest=[]
for g in G:
 rp=Path('data/online/smoke',g['label']+'-old',f'M{g["gid"]}.replay')
 assert g['bots'][g['ours']]==('21200' if g['label']=='one10-c1' else '21126')
 manifest.append({'gid':g['gid'],'label':g['label'],'bot':g['bots'][g['ours']],'ours':g['ours'],'map':g['map'],'last_scanned':max(map(int,g['snaps'])),'replay':str(rp),'sha256':hashlib.sha256(rp.read_bytes()).hexdigest()})
(P/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('top5',top,'files written')
