import json, hashlib, sys
from pathlib import Path
from collections import deque
sys.dont_write_bytecode=True
sys.path.insert(0, 'tools')
import ladder_replay as lr

def home_checks(d, entry):
 w,h=d['size'];known=set();closed=False;history=[]
 raw=[tuple(map(int,p.split()[1:4])) for p in d['text'].splitlines() if p.startswith('EDGE ')]
 edges=lr.canonical_edges(w,h,raw)
 for t in d['qturns']:
  if t['id']!=d['queens']['us'] or t['r']>entry:continue
  x,y=t['head']
  for dy in range(-3,4):
   for dx in range(-3,4):
    for dr in range(4):known.add(lr.edge_id(w,h,(x+dx)%w,(y+dy)%h,dr))
  if not closed and t['r']<=200 and t['r']%2==0:
   seen={(x,y)};todo=deque([(x,y)]);n=None
   while todo and n is None:
    px,py=todo.popleft()
    for dr,(dx,dy) in enumerate(((0,-1),(1,0),(0,1),(-1,0))):
     ed=lr.edge_id(w,h,px,py,dr)
     if ed not in known:n=-1;break
     if edges.get(ed,(0,-1))[0]!=0:continue
     pt=((px+dx)%w,(py+dy)%h)
     if pt not in seen:
      if len(seen)>=w*h//2:n=-1;break
      seen.add(pt);todo.append(pt)
   n=len(seen) if n is None else n;closed=n>=40
   history.append([t['r'],n,closed])
 return history

OUT=Path(__file__).parent
ids=[1485181,1485182,1485486,1485489,1485490]
rows={g:json.loads((OUT/f'{g}.json').read_text()) for g in ids}
evidence={}
boards=['[M] 마지막 세 자기 턴의 시작 판면. r은 0부터, 좌표는 (x,y), 북쪽 위. 중앙 Q=우리 여왕, K=상대 여왕, A/a=우리 머리/몸, E/e=상대 머리/몸, *=진주, .=빈칸. 선=켈프, ~=포털. 각 판면은 토러스 7×7이며 바깥의 몸은 생략.\n']
board_table=['|[M] 경기·여왕|끝에서 세 번째 자기 턴|끝에서 두 번째|마지막|','|---|---|---|---|']
for g,d in rows.items():
 q=d['queens']['us']; eq=d['queens']['them'];ts=[t for t in d['qturns'] if t['id']==q];last=ts[-1];de=next(x for x in d['deaths'] if x['id']==q);w,h=d['size']
 def seen(pt,c):return all(min(abs(pt[i]-c[i]),(w,h)[i]-abs(pt[i]-c[i]))<=3 for i in (0,1))
 ev={'bot':d['bots'][d['ours']], 'queen_id':q, 'death':de, 'final':d['final'], 'last_nontailing_queen_round':max(int(r) for r,s in d['snapshots'].items() if s['us']['queen_length']>=s['them']['queen_length']), 'near_first':d['near_after_qdeath'][:1], 'near_unique_dragon_rounds':len({(x['id'],x['r']) for x in d['near_after_qdeath']}), 'enemy_queen_bounds':[[min(p[i] for p in d['enemy_q_positions_after']),max(p[i] for p in d['enemy_q_positions_after'])] for i in (0,1)], 'anomalies':d['anomalies']}
 if de['actor']!=q:
  a=next(x for x in last['nearby'] if x['id']==de['actor']);visible=sum(seen(p,last['head']) for p in a['body']);ghost=max([sum(seen(p,t['head']) for p in x['body']) for t in ts if last['r']-3<=t['r']<=last['r'] for x in t['nearby'] if x['id']==de['actor']],default=0)
  ev.update(attacker=a['id'],attacker_length=a['L'],visible_parts=visible,ghost_max_parts=ghost,attacker_turn=next(t for t in d['turns'] if t['r']==de['round'] and t['id']==a['id']))
 if g in [1485181,1485489]:
  entry=99 if g==1485181 else 111;t=next(t for t in ts if t['r']==entry);dest=t['steps'][0];ev['portal_entry']={'round':entry,'head':t['head'],'destination':dest,'prior_exit_sightings':sum(seen(dest,t['head']) for t in ts if t['r']<=entry), 'home_checks':home_checks(d,entry)}
 rp=Path(d['folder'])/f'M{g}.replay';ev['replay_sha256']=hashlib.sha256(rp.read_bytes()).hexdigest();evidence[g]=ev
 cells=[]; boards.append(f'## {g}, Q#{q}\n')
 for t in ts[-3:]:
  act='split' if t['split'] else ''.join('NESW'[v] for v in t['action']['dirs'])
  label=f"r{t['r']} {tuple(t['head'])} L{t['L']} → {act}"
  compact=[''.join(line[2+4*k] for k in range(7)) for line in t['board'].splitlines()[1::2]]
  assert len(compact)==7 and all(len(x)==7 for x in compact)
  cells.append(label+'<br><code>'+'<br>'.join(compact)+'</code>')
  boards.append(label+'\n\n```text\n'+t['board']+'\n```\n')
 board_table.append(f'|{g} Q#{q}|'+'|'.join(cells)+'|')
(OUT/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
(OUT/'boards.md').write_text('\n'.join(boards))
report='''[M/C/E] 최상위 원인: 시야에 잘린 적을 짧게 계산해 여왕 돌진 방어가 실패한 3/5판.
[E] 카드 A: 잘린 적의 길이 하한을 두 방어 경로에 함께 적용하고, 진주 포함 4걸음 끝점까지 검사한다.
[M/C/E] 사망·행동·길이 계수는 확실; 아래 코드 원인은 강한 추론이며 변경 후 생존·승리는 미검증.

[M] 2026-10-09 04:23:57 KST. 전부 **one8/21126**. 원기보 재집계에서 최종 상태와 서버 결과 일치, 재구성 이상 0. ★는 브리프가 지정한 레이팅 105 낮은 상대와의 랭크전이다. [M] r은 0–499. 최종은 **여왕/최장/총길이/생존수**, 우리→적. ‘전환’은 이후 여왕 열세가 다시 뒤집히지 않은 라운드이며, 수학적 승패 확정 시점은 아니다.

|[M] 경기·지도·우리편|최종 우리 → 적|판정·전환|패배 사건·수정 연결|
|---|---|---|---|
|1485181 Portals A|0/35/59/11 → 8/8/8/1|여왕, r105|Q#1 r99 미관측 출구 (12,15) 진입; r104 분열 5→3; r105 W 포털로 (18,2)의 **아군 #145 몸** 충돌. #145는 r104 S로 (18,3)에 이동해 그 칸에 꼬리를 남겼다. 적 공격 없음. 카드 B.|
|1485182 Slithery Fight A|0/15/114/29 → 16/31/163/18|여왕, r335|Q#0 r333 섭취 6→7, r334 S, r335 E→(23,2). #994 L6은 (25,4)에서 NNWW, 첫 칸 진주를 먹고 4번째에 충돌. 카드 A.|
|★1485486 Slithery Fight B|0/50/125/23 → 24/35/172/11|여왕, r409|Q#1 r407–408 섭취 46→48, r409 S→(41,13). #1458 L7은 (38,13)에서 EEE로 충돌. 성장 부족이 아니라 긴 여왕 노출. 카드 A.|
|★1485489 Portals B|0/14/62/14 → 6/6/10/2|여왕, r112; 사망 r113|Q#0 r111 E 포털→(27,13), r112 분열 4→2, r113 E 켈프 충돌. 출구의 N/E/S는 벽, W 귀환은 자기 목 (4,1). 적 공격 없음. 카드 B로 r111 진입 예방.|
|★1485490 Trauma B|0/4/7/2 → 23/23/78/8|여왕, r430|Q#1 r429 SE NEES(공백 제외) 6걸음, r430 WSS→(46,3). #235 L3이 (47,4)에서 NW 2걸음 충돌. 직전 Q길이는 23 대 8. 카드 A의 다중 이동 검사 수정.|

[C/E] 줄 번호는 [one8 main.cpp](../../../../../online/smoke/one8-bot/main.cpp). 실제 내부 점수·분기 로그는 없으므로 분기 선택을 재현했다고 주장하지 않는다.

|경기|LIVE 방어와 실패 조건 [C]; 기보 대조 [M/E]|
|---|---|
|1485182|`QUEEN_SAFETY:true`, `SMALL_SPRINT_THREAT:true`. 5278–5300: 보이는 #994는 1마디, 최근 3라운드 기억 최대도 1; `cut` 보정은 3마디, `full=2`, `reach=max(free,min(full,QS_PAY_REACH))=2`. 실제는 4걸음. `QS_PAY_REACH:3` 때문에 개발 중 `CUT_BODY_LEN:4`만으로도 부족.|
|1485486|동일 줄에서 #1458도 보임/기억 1/1→보정 3→도달 2. 실제 충돌은 3걸음. `CUT_BODY_LEN:4`의 직접 대상.|
|1485490|`STRIDE_SAFE_END:true`: 1707–1725,1748–1765의 별도 `stride_reach_map`은 경계 보정 없이 보임/기억 2/2→1걸음. 실제는 2걸음. 5320–5340의 일반 hit-map도 시작 몸의 (46,3), `enter_time=3`을 막지만 WSS 뒤에는 머리가 된다. 한 경로만 고치면 부족.|
|1485181,1485489|`QUEEN_NO_PORTAL:true`여도 4718–4720의 `is_queen()`은 `cells>600 || home_closed`에 의존; `QUEEN_PORTAL_ALL:false`. 관측 지형 재구성에서 진입 전 `home_closed=false`이므로 5080–5086의 보호 대상에서 빠진다. `POCKET_KEEP_OUT:true`도 701–735에서 미확인 출구의 `step` 실패 시 검사를 끝낸다. 두 진입 출구의 과거 자기 시야 관측은 모두 0회. r113에는 이미 합법 이동 없음.|

|[M] 우리 여왕 사망 뒤 상대 여왕에 ≤5걸음 접근?|상대 여왕 위치·추가 행동|
|---|---|
|1485181: 없음|상대 #0, 사망 라운드 끝 (1,12), 마지막 (2,10); 사후 범위 x0–7/y0–15.|
|1485182: 없음|상대 #1, (54,1)→(50,1); 범위 x50–61/y0–6.|
|1485486: 있음|최초 r467 #1536 L2, (17,24)→여왕 #0 (15,21), 지형거리 5. r493 #1666 L15는 (14,21)에서 여왕 (14,20)과 거리 1까지 접근했으나 SW 이동. `QUEEN_AVENGE:8`의 `length<=4`(2842–2844)가 이 긴 용은 제외한다.|
|1485489: 없음|상대 #1, (31,14)→(17,3); 범위 x16–31/y0–15.|
|1485490: 없음|상대 #0, (4,13)→(7,11); 범위 x4–10/y8–22.|

[M] 거리는 몸을 제외한 켈프·포털·토러스 최단 경로다. ≤5는 공격 가능성과 다르다. 다섯 판 모두 여왕이 죽었고 최장·총길이·전멸 판정은 없었다.

|순위·카드|분류·구체 규칙 [C/E]|위치·붙여넣을 상수|작동 계수 / 반증|
|---|---|---|---|
|1. A: 잘린 적 도달범위, 3판|**BEING BUILT** `CUT_BODY_LEN`의 필수 범위 보완; 기존 `QUEEN_SAFETY`는 **LIVE-BUT-FAILED**. 적 몸이 시야 경계에 닿으면 최소 L4로 보고, 현재 진주로 지불 가능한 4걸음까지 여왕 후보 끝점의 충돌 위험을 반영한다. 일반 이동과 다중 이동 둘 다 적용.|one8 5278–5300,5320–5350 **및 1748–1765**,1707–1725. 개발 카드 `CUT_BODY_LEN:4`; 기존 `QS_PAY_REACH:4`; one9의 `REACH_EATS:true` 유지. one8에는 후자 없음. 상수만 바꿔 완결되지 않음.|세 사망 턴의 실제 끝점을 위험으로 표시 3/3; 다른 안전 후보를 선택하고 다음 적 턴 생존해야 함. 1485182가 3걸음에서 잘리거나 1485490이 다중 이동 끝점까지 안전으로 남으면 반증. 승리 보장은 아님.|
|2. B: 미관측 포털 진입, 2판|**BEING BUILT** `QUEEN_PORTAL_ALL`; 새 카드 아님. 실제 여왕은 지도 크기와 관계없이 미관측 출구를 탐색하지 않는다.|one8 5080–5086,6815–6837. `QUEEN_PORTAL_ALL:true`. 1486–1511의 `!any_enterable` 비상 포털 경로는 별도로 금지를 우회하므로 적용 여부도 검사.|r99 #1 / r111 #0의 미관측 진입 2→0, 각각 r105/r113까지 여왕 생존. 비상 경로로 같은 진입을 출력하거나 이전에 다른 충돌로 죽으면 반증.|

[M] 마지막 세 자기 턴의 7×7은 아래와 같다. 중앙 Q=우리 여왕, K=상대 여왕, A/a=우리 머리/몸, E/e=적 머리/몸, *=진주, .=빈칸. 좌표는 중앙. **벽·포털까지 그린 원도는 [boards.md](boards.md)**.

'''
report=report.replace('SE NEES(공백 제외)','SENEES')
report+='\n'.join(board_table)+'\n\n[M/E] 재현: [analyze.py](analyze.py), [evidence.json](evidence.json), [재집계 로그](recheck.log). 측정은 원기보에서 재실행했다. 미검증: 변경 봇 실행·CPU·승률·상대 응수 변화·숨겨진 내부 점수. 네트워크·대전·봇 소스 수정은 하지 않았다.\n'
report=report.replace('cells>600 || home_closed', 'cells>600 &#124;&#124; home_closed')
(OUT/'report.md').write_text(report)
print('report outside-table words:',len(' '.join(line for line in report.splitlines() if not line.startswith('|')).split()))
print('boards:',sum(1 for _ in boards if '```text' in _),'games:',len(evidence))
