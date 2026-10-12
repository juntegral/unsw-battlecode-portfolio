import sys
sys.dont_write_bytecode=True
import json,html
from pathlib import Path
from collections import Counter
from datetime import datetime
O=Path(__file__).parent
xs=sorted([json.loads(p.read_text()) for p in O.glob('case*.json')],key=lambda x:(x['v'],x['gid']))
raws={int(p.stem[1:]):json.loads(p.read_text()) for p in O.glob('g*.json') if p.stem[1:].isdigit()}
portal={1483344:(65,'2+2 분열'),1485489:(111,'N'),1486054:(109,'N'),1493693:(90,'2+2 분열')}
long={1488845:'r34 #16 L4→5; r35 L5 분열, 여왕 r35 진입',1489844:'r320 #568 L3→4는 거리3/목적지 거리2; r321 L4 분열; #599 L5 몸도 서쪽 차단'}
unknown={1491740:'r283 #594 L3, 시야 밖 포털 (9,6)→(22,10)의 연결 기억 미확인; proposed.unknown이면 STRICT 반환'}
remote={1483997,1484442,1485181,1487486,1493890,1494966}
selfs={1483010,1483011,1484431,1484432,1485172,1487476,1489834,1491744,1492091,1493880,1493891,1494955}
classes={};details={}
for x in xs:
 gid=x['gid'];d=x['death'];raw=raws[gid];good=[c for c in x['closures'] if c['strict_certain']]
 if d['reason']==3:
  cls='N'
  note=f"정면충돌 actor#{d['actor']}; 마지막 두 차례 중 빈 출구≤1. 네 규칙의 구제 미입증"
  if gid==1483020:cls='D';note='r313 아군 #766 L4가 포털 출구 (22,6) 점유; 여왕 미관측, r314 여왕의 포털 정면충돌'
  elif gid==1492096:note='r117 적 #40 L2가 (10,9) 마지막 출구 점유; 아군 보호 규칙 불가'
  elif gid==1492104:cls='D';note='r186 포털 건너 아군 #104가 여왕과 충돌; 여왕 정지 분열 이후, 직접 여왕 관측 없음'
 elif good:
  cls='S';c=good[-1];place=c['remove_exits'];note=f"r{c['r']} 아군 #{c['id']} L{c['L']}, 출구 {place}; "+('이미 갇힌 뒤에도 몸을 유지. ' if c.get('already_boxed') else '마지막 출구 점유. ')+f"STRICT 대체/희생; KEEP의 생존 대안 한걸음 {c['live_alternatives'] or '없음'}"
 elif gid in portal:
  cls='P';r,act=portal[gid];note=f'r{r} 처음 보는 포털 방 진입 → LAST {act}; 뒤 자기 몸·분열로 봉쇄. POCKET은 미상 목적지 step 실패'
 elif gid in long:cls='L';note=long[gid]+'; STRICT 길이/거리·분열 관문 제외'
 elif gid in unknown:cls='U';note=unknown[gid]
 elif gid in remote:
  cls='D';c=raw['closures'][-1];note=f"r{c['r']} 아군 #{c['id']} L{c['L']}가 포털 출구 {c['before']} 점유; 머리→몸 봉쇄, 여왕 미관측. KEEP/STRICT 모두 제외; LAST는 여왕의 진입만 검사"
 elif gid in selfs:
  cls='Q';t=next((t for t in reversed(x['turns'][:-1]) if t['endbody'] and not t['endexits']),x['turns'][-2]);note=f"r{t['r']} 여왕 {''.join('NESW'[z] for z in t['dirs']) or '분열'} 뒤 자기 몸·벽 봉쇄; "
  if gid==1491744:note+='BOOT가 비상 분열까지 차단(5805); 네 출구 규칙은 성장 관문을 고치지 않음'
  elif gid in (1483011,1485172):note+='포털 방은 이미 관측됨: LAST 제외, 현재 대안 없음'
  elif gid==1484431:note+='POCKET 생존 대안은 포털 N뿐; choice.open/score 내부값 미확인'
  elif gid==1492091:note+='r126 EE의 끝은 출구1: POCKET 한 칸 검사 통과, r129는 양방향 모두 막힘'
  elif gid==1487476:note+='r195 N/S 모두 다른 몸 포함하면 다음 출구0: POCKET 대안 없음'
  else:note+='POCKET은 당장 출구0만 보고, 마지막 진입 때 생존 대안 없음; 분열은 점유를 남김'
 else:cls='N';note='적 #19 몸이 통로 반대쪽을 점유; r123 여왕이 진입. 네 보호 규칙으로 적 이동 변경 불가'
 classes[gid]=cls;details[gid]=note
non=[x for x in xs if x['death']['reason']!=3];cc=Counter(classes[x['gid']] for x in non)
assert len(xs)==85 and len(non)==45 and cc==Counter(S=19,P=4,Q=12,D=6,L=2,U=1,N=1),cc
old=json.loads((O.parent/'audit-threat/queen-deaths.json').read_text());oldids={d['gid'] for d in old['deaths'] if d['category']=='no_open_exit'};oldcov=oldids&{k for k,v in classes.items() if v in ('S','P')};assert len(oldids)==10 and len(oldcov)==6
stamp=datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
intro=f'''[M/C/E] one11의 행동 변경 범위: 기존 감사 **6/10**, 확대 비정면 사망 **23/45**(STRICT 19, PORTAL_LAST 4); 생존 구제 수는 미검증.
[M/E] 최대 미포괄군은 **여왕 자신의 통로·분열·기관측 포털 봉쇄 12건**; 아래 일반 규칙 후보는 그중 3건의 선택을 검출한다.
[M/C/E] 사건·조건 대조는 높음, 반사실 생존은 낮음. 원기보 184판(one8 124/one9 20/one10 40), one11 별도 6판; {stamp}.

[M] 비정면 사망은 모두 45건이다. 누락 방지를 위해 마지막 두 자기 차례 시작/끝에 빈 출구≤1이던 정면충돌 40건도 넓게 포함했다. 이는 ‘안전 출구 없음’과 다르며 45건 분모에 섞지 않았다. 기보 라운드는 0기반. 기본 목록은 06:10:49 KST 동결, one11은 06:22:21 KST에 한 판 추가했다. 120개 중복 경로를 제거하고 봇 ID를 확인했다. [전체 마지막 두 차례 7×7 판면](boards.md), [원자료 목록](inventory.json), [개별 판정](coverage.json).

[C] 줄은 모두 `data/online/smoke/one11-bot/main.cpp`. STRICT는 889–891·900–905·1010–1022의 길이/직접관측/거리/최종출구 관문, 1103–1126의 자기충돌을 대조했다. 이미 출구0이어도 적용된다. KEEP는 대안 실패 시 원행동을 남긴다(1044–1102). 미상 포털은 1021에서 반환한다. LAST는 1613–1617·1697–1720; POCKET은 689–701·742–791이며 최종 한 칸과 점수화된 대안만 본다. [E] 전 사건의 새 입력으로 봇을 실행한 결과는 아니다.

| 비정면 사망 분류 [M/C/E] | 건수 | 적용·실패 이유 |
|---|---:|---|
|S STRICT 포괄|19|직접 보이는 L2/3의 최종 점유를 바꿈; 이미 갇힌 뒤 구출도 포함|
|P 다른 live 규칙 포괄|4|미관측 포털 진입 대신 합법 분열/일반 이동|
|Q 자기 봉쇄|12|STRICT/KEEP는 여왕 제외; LAST는 기관측 목적지 제외; POCKET은 한 칸/후보 부족|
|D 비인접·앞선 차례|6|포털 반대편 아군이 여왕을 직접 못 봄|
|L 긴 차단자|2|결정적인 다음 차례 L4/5 또는 분열; 이전 이동은 거리 관문 밖|
|U 조건부|1|포털 연결 기억에 따라 STRICT 적용 여부가 달라짐|
|N 네 규칙 불가|1|적 몸과 여왕의 통로 진입; 전략적 구제 불가능이라는 뜻은 아님|

[E] **카드 하나:** L2/3 여왕의 이동 후보에 대해 관측된 지형·자기 몸·현재 진주로 연속 이동을 전개한다. 미관측 경계·순환·분열 가능한 길이에 도달하지 못하는 후보는, 도달 가능한 합법 일반 첫걸음이 있을 때 제외한다. [C] 삽입: POCKET의 `rejected`, 742–764, 후보 비교 771–791. 기존 상수로는 여러 차례 후 막힘을 검사하지 못한다. [M] 마지막 8차례 조사에서 1483010:r54 E→N, 1483011:r180 E→N, 1487476:r195 N→S, **3/12건**; [검출 자료](viability.json). [E] 다른 용의 이후 이동·새 진주 생성은 미모형화했다. 검출된 세 진입의 감소와 다음 10라운드 생존으로 시험하고, 대안도 봉쇄되거나 미래 먹이를 무시한 오거부가 생기면 기각한다. 전체 12건 해결 주장은 하지 않는다.

[M/E] one11(21269) 랭크 1496000–1496004·1496711: 로그0, 거리≤2에서 출구를 남기는 우회와 양립하는 행동 **13회**, 여왕 +10라운드 생존 **13/13**. 가까운 자기충돌 **1회**(1496003:r251 #414), +10 생존이지만 원래 출구가 2개여서 강제 희생 증거가 아니다. 확정 STRICT 발동 횟수는 **NA**이며 0으로 단정하지 않는다. KEEP·기존 점수와 구별할 개입 전 행동이 없다. [행동 목록](one11-observations.json). one11의 남은 봉쇄는 1496001:r81 자기 통로, 1496002:r451 자기 몸, 1496004:r126 포털 건너 아군 몸이다. 추가 1496711:r48 #36(L2)은 시야 밖 (18,8)에서 포털로 (13,5)에 와 마지막 출구를 막았고 r49 여왕이 죽었다. STRICT의 직접관측 조건이 live에서도 실패한 사례다. one11-c1/p1 완결 기보는 이 조사 시점에 없었다.

[E] 코드 기억·점수·새 정책 실행·CPU·장기 구제는 미검증. 네트워크·대전·봇 수정 없음.

| 경기 / 버전 [M] | 사망 r / L / 원인 [M] | 분류 [C/E] | 누가 무엇을 닫았고 one11은 무엇을 바꾸는가 [M/C/E] |
|---|---|---|---|
'''
causes={0:'벽',1:'자기몸',2:'다른몸',3:'정면',4:'무효'}
lines=[intro]
boards=['[M] 마지막 두 자기 차례 **시작** 판면. 중앙 Q=여왕, q=자기 몸, A/a=아군 머리/몸, E/e=적 머리/몸, *=진주, .=빈칸, ─/|=벽, P=포털. 상단이 북쪽이며 좌표는 토러스 (x,y). 각 그림은 7×7 칸과 경계선이다. 실제 기보의 시작 상태이며 새 정책 실행 결과가 아니다.\n']
for x in xs:
 gid=x['gid'];d=x['death'];lines.append(f"|[{gid} / one{x['v']}](boards.md#g{gid})|{d['r']} / {d['L']} / {causes[d['reason']]}|{classes[gid]}|{details[gid]}|\n")
 boards.append(f'\n<a id="g{gid}"></a>\n\n| {gid} one{x["v"]}: {x["map"]}; 사망 r{d["r"]}, L{d["L"]} [M] | 마지막 직전 차례 [M] | 마지막 차례 [M] |\n|---|---|---|\n')
 cells=[]
 for t in x['turns'][-2:]:
  act=''.join('NESW'[v] for v in t['dirs']) if t['dirs'] else f"SPLIT(child #{t['split']})"
  code=html.escape(t['board']).replace('|','&#124;').replace(' ','·').replace('\n','<br>')
  cells.append(f"r{t['r']} L{t['L']} Q{tuple(t['body'][0])} → {act}<br><code>{code}</code>")
 boards.append(f"|{details[gid]}|{'|'.join(cells)}|\n")
(O/'report.md').write_text(''.join(lines));(O/'boards.md').write_text(''.join(boards))
(O/'coverage.json').write_text(json.dumps(dict(time=stamp,non_head_counts=dict(cc),old_audit_ids=sorted(oldids),old_audit_covered=sorted(oldcov),classes=classes,details=details),ensure_ascii=False,indent=2))
obs=[]
for x in raws.values():
 if x['v']==11:
  for s in x['signals']:obs.append(dict(gid=x['gid'],**{k:s[k] for k in ('r','id','L','signal','queen_next10','before','endexits','body','dirs')},blocking_alternatives=s.get('blocking_alternatives',[])))
(O/'one11-observations.json').write_text(json.dumps(obs,ensure_ascii=False,indent=2))
print('classes',dict(cc),'old covered',sorted(oldcov),'boards',len(xs),'signals',len(obs))
print('prose whitespace words',sum(len(line.split()) for line in intro.splitlines() if not line.startswith('|')))
