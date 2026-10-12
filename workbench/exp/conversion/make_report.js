'use strict';
const fs=require('fs'),path=require('path');
const OUT=__dirname,ROOT=path.resolve(OUT,'../..');
const T=JSON.parse(fs.readFileSync(path.join(OUT,'tables.json'))),V=JSON.parse(fs.readFileSync(path.join(OUT,'verification.json'))),P=JSON.parse(fs.readFileSync(path.join(OUT,'population.json'))),D=JSON.parse(fs.readFileSync(path.join(OUT,'deep-reads.json'))),AUDIT=JSON.parse(fs.readFileSync(path.join(OUT,'audit.json')));
const MAPS=['Slithery Fight/a','Slithery Fight/b','Schooltime/a','Trauma/a','Autarky/a'];
const labels={'Slithery Fight/a':'Slithery a','Slithery Fight/b':'Slithery b','Schooltime/a':'Schooltime a','Trauma/a':'Trauma','Autarky/a':'Autarky'};
const roles=[['eliteWinner','엘리트 승'],['eliteLoser','엘리트 패'],['ours:W0-W12:top6','W0–W12'],['ours:bench-s11:top6','최근 stack11'],['ours:v1:top6','v1']];
const f=(x,d=2)=>x==null||!Number.isFinite(x)?'—':Number(x).toFixed(d),pct=(x,d=1)=>x==null||!Number.isFinite(x)?'—':f(x*100,d)+'%',num=x=>Number(x||0).toLocaleString('en-US'),g=(m,r,s='r500')=>T.groups[m+'|'+r+'|'+s],avg=(x,N)=>N?x/N:null;
const out=[],add=s=>out.push(s.trim()+'\n');
function table(headers,rows){add('| '+headers.join(' | ')+' |\n| '+headers.map(()=> '---').join(' | ')+' |\n'+rows.map(r=>'| '+r.join(' | ')+' |').join('\n'));}
function coreRows(fn,selected=roles){return MAPS.flatMap(m=>selected.flatMap(([r,l])=>{const a=g(m,r);return a?[fn(m,r,l,a)]:[];}));}
const primaryRoles=[roles[0],roles[1],roles[4]];
add(`# 500라운드 맵의 군집 질량 → 최종 왕: 전환 프로토콜

작성: 2026-10-01 KST. 전수표 최초 저장 ${new Date(T.firstWrittenAt).toLocaleString('sv-SE',{timeZone:'Asia/Seoul',hour12:false})} KST. Top 모집단 동결 ${new Date(P.frozenAt).toLocaleString('sv-SE',{timeZone:'Asia/Seoul',hour12:false})} KST. 온라인 목록 최종 확인 ${new Date(P.onlineRefreshedAt).toLocaleString('sv-SE',{timeZone:'Asia/Seoul',hour12:false})} KST. [online-status.json](../../exp/conversion/online-status.json)에 존재하는 모든 우리 세트와 미도착 목록을 남겼다.

[사실] 요청된 로컬 기보 **N=${num(T.coverage.requested)}게임**을 모두 재구성했다. Top stalled **N=${T.coverage.excludedStall}게임**을 제외했고, 독립 원시 이벤트 검산 **N=${num(V.N)}게임에서 불일치 0건**이다. v1의 Slithery 최종 왕은 **25.78 대 상대 58.72 (N=18, a 6/b 12게임)**로 brief의 25.8/58.7을 재현한다.

[해석] 전환의 핵심은 **작은 조각의 지속적인 지역 재활용 → 가까운 수령자 성장 → 마지막 왕에게 예약된 급식**이다. Slithery에서 v1은 최종 왕을 수령자로 만드는 연결이 약하다. Trauma는 왕에게 보낼 재료량과 초기 수령자 성장부터 부족하다. Autarky는 v1의 기존 요새형 왕 성장을 보존하는 처방이 맞다. 아래 프로토콜은 기보에 근거한 구현 제안이며 새 봇 실험 N=0이다.`);
add(`## 1. 모집단과 세 단계 방법

### 1단계: 전수 스크립트

[사실] \`data/top/index.jsonl\` **N=${num(P.topIndexLines)}행**에서 대상 네 맵의 모든 top-vs-top **N=8,466게임**을 선택했다. 우리 온라인은 W0–W12의 15세트, 이전 9세트, v1-w1..3 및 bench-s11-1..3, 기본 **30세트 × 대상 맵 28게임 = N=840**에 초기 \`r1-online\` **N=76**, \`r1-autoscrim\` **N=2**를 확인했다. 두 세트는 게임 587111/587113을 공유하므로 **78인덱스 행 중 고유 76게임**을 추가해 **${P.sets.length}세트, 고유 N=${T.coverage.source.online}게임**이다. 최초 저장표의 초기 세트 누락은 마감 목록 대조에서 보완했고, 동일 원본 SHA-256을 확인해 전체 모집단에서는 중복을 한 번만 센다. 개별 세트의 membership은 alias로 보존한다. W0–W12/v1의 비교 모집단과 키 수치는 변하지 않았다. 인덱스가 있는 온라인 디렉터리 33개 중 \`top-sample\`은 우리 팀이 없는 Portals 1게임이므로 우리 대상 모집단에서 제외한다. Top에서 round≥100이고 한 팀의 sonar=0, split≤3인 stalled **N=108**은 이전 연구와 같은 기준으로 제외한다. 양 팀 결과는 같은 게임에서 나온 짝이며, 게임/조각/진주 관측을 독립 표본으로 취급하지 않는다.

[사실] 보존된 전체 레이아웃은 다음과 같다. 조기 종료도 \`scope=all\`에 포함한다. 본문의 r250–500 성장·기하 비교는 **실제 500라운드에 도달한 \`scope=r500\`**이며, 완주 선택에 따른 생존 편향이 있다. Autarky의 top 조기 종료가 특히 많으므로 완주 표를 전체 승률의 대용으로 쓰지 않는다.`);
table(['맵/레이아웃','stalled 제외 후 게임 N','본문 여부'],Object.entries(T.coverage.layouts).map(([m,N])=>[m,num(N),MAPS.includes(m)?'주 분석':'별도 JSON 부록']));
table(['맵','엘리트 승/패 각각 N 전체/완주','W0–W12 top6 N 전체/완주','최근 stack11 top6 N 전체/완주','v1 top6 N 전체/완주'],MAPS.map(m=>[labels[m],...['eliteWinner','ours:W0-W12:top6','ours:bench-s11:top6','ours:v1:top6'].map(r=>`${g(m,r,'all')?.N||0}/${g(m,r)?.N||0}`)]));
add(`[사실] 레이아웃 구분은 자연 생성 진주의 a/b spawn support와 기존 layout assignment를 재사용한다. **Slithery 미확정 N=${T.coverage.layouts['Slithery Fight/?']||0}게임**을 a/b로 강제 배정하지 않았다. Schooltime b **N=${num(T.coverage.layouts['Schooltime/b'])}게임**도 전수 추출해 JSON에 보존하지만 요청한 a 프로토콜의 근거에 섞지 않았다. 우리 비교의 주 층은 상대 ID 306/70/20/801/264/46인 **top6**이다. DEV545, all7, 기타 상대 층 및 우리 세트별 결과는 모두 \`tables.groups\`에 따로 있다.

[사실] v12-w*·v13-w* 온라인 기보는 확인 시점에 **N=0세트/0게임**이다. v1/v12/v13 로컬 실험 디렉터리는 기보 경로의 존재만 확인했으나 원시 replay가 없는 요약 행을 전수 기보 분석으로 세지 않았다. 이후 도착한 기보는 \`refresh_online.js\` → \`extract.js\` → \`aggregate.js\` → \`targets.js\` → \`verify.js\` 순서로 갱신할 수 있다. Top 동결 모집단은 유지한다.

[사실] [extract.js](../../exp/conversion/extract.js)는 \`exp/spatial\`의 모집단·기하 코드, [mass_ledger.js](../../tools/mass_ledger.js)의 이동/섭취/계보 회계, \`legacy/exp/intake-gap/rawload.js\`의 빠른 디코더를 재사용한다. \`turn\`은 **이동 전 turnStart**이다. 섭취자는 다음 turn의 현재 조각으로 추정하지 않고 실제 \`eat\` 이벤트와 이동 시뮬레이션으로 정한다. [targets.js](../../exp/conversion/targets.js)는 \`legacy/exp/endgame-king/extract.js\`의 표시문 파서를 사용한다. 보드 렌더러는 \`exp/pocket\`의 방법을 재사용했다.

### 2단계: 크기가 있는 클래스

[사실] r250 이후 **모든 희생 이벤트**에 기증자 길이·계보·실제 사망 위치·각 드롭 좌표·섭취자 ID/라운드·경로 거리·회수 지연을 저장했다. [tables.json](../../exp/conversion/tables.json)의 \`eventFiles\`가 N=${num(T.coverage.processed)}개의 압축 per-game 파일을 가리킨다. 그 파일의 \`deaths\`에서 \`cause=0\`이 본 연구의 희생이다. 실패 이벤트도 분류에 포함한다. 성공한 예만 골라 전수 결과를 만들지 않았다.

[사실] 공간 클래스는 여섯 가지다. 왕 계보가 ≥1개를 먹었을 때 기증자→당시 왕 머리 거리 ≤3이면 \`direct\`, 4–8이면 \`localPickup\`, ≥9이면 \`fieldTour\`다. 왕 섭취가 없으면 enemy>ally는 \`enemyTheft\`, 그 외 ally>0은 \`otherAlly\`, 나머지는 \`uncollected\`다. 따라서 \`enemyTheft\`는 패킷 전체를 적이 먹었다는 뜻이 아니다. 릴레이 이력은 이 공간 분류와 겹치는 별도 축이다.

### 3단계: 클래스 안의 정독

[사실] 성공 2진주 이상, r300 이후, 완주 엘리트 승리라는 조건의 클래스 크기를 먼저 계산한 뒤 가장 큰 **성공 클래스 direct**의 길이/거리/왕 섭취량/평균 지연 중앙값에 가까운 예를 맵마다 1개 선택했다. 전수에서 가장 큰 클래스는 \`otherAlly\`이며 성공 subset의 direct와 구별한다. 추가로 큰 후반 급식 3개, 우리 실패·지연 3개, 엘리트 왕 사망 1개, 원거리 회수 1개를 읽었다. **총 정독 N=13게임/13이벤트**이고 전수 수치에는 선택 가중치를 주지 않는다. ID·라운드·선택 클래스 N은 8절에 공개한다.`);
add(`## 2. 정의: 무엇을 왕에게 전환했다고 세는가

[사실] 최종 왕은 종료 시 가장 긴 생존 조각이며 동률이면 작은 ID다. 그 조각의 split 부모를 역추적하되, **자식이 태어난 순간부터 최종 경로는 그 자식으로 넘어간다**. 이후 부모가 먹은 진주를 계속 왕 섭취로 세지 않는다. r250/300/... 값은 라운드 시작의 해당 경로 조각 길이, r500은 마지막 r499 행동 후 길이다. 조기 종료 게임의 \`all.curve[500]\`은 실제 종료 상태이며 r500에 살아 있었다는 뜻이 아니다. 왕 계보가 전무하면 길이 곡선은 null이고 최종 점수만 0이다.

[사실] 희생은 ledger의 \`sac\` 운영 정의다. 이동 전 빈 이웃이 있었고 자기 충돌·벽 충돌·아군 몸 충돌·유효 행동 없음 등으로 죽은 경우다. 의도까지 증명하는 분류가 아니며 TLE, 지불 못한 다중 이동, 적과의 전투 사망은 분리한다. 죽음 드롭은 규칙대로 **ceil(L/2)**개이며 머리부터 몸의 짝수 인덱스에 생긴다. 실제 \`tileChange\` 좌표를 보존했다.

[사실] **line share**의 분모는 지정 구간에 *생성한* 자기 팀 희생 드롭 전부이고, 분자는 게임 종료 전 활성 최종 계보가 먹은 수다. ally는 같은 팀의 다른 활성 경로, enemy는 상대, none은 끝까지 미섭취다. 반면 **line sacrifice pearls r300–499**는 그 구간에 *먹은* 진주이며 r250–299에 만든 드롭도 포함한다. 따라서 두 분자가 다를 수 있다. 진주 share는 게임별 share의 단순 평균이 아니라 전체 분자/분모다.

[사실] 거리는 kelp·portal·wrap을 반영한 정적 최단 경로다. 기증자 머리 거리는 기증자→사망 순간 왕 머리, 드롭 거리는 그 왕 머리→각 드롭이다. 임시 용 몸통은 무시하므로 실제 안전한 이동 경로보다 짧을 수 있다. null은 왕 부재/도달 불가다. 지연은 섭취 round−사망 round, first turns는 사망 이후 최초 회수까지 활성 계보가 실행한 턴 수다. 같은 라운드에 부모/자식이 모두 행동하면 계보 턴 수가 라운드 수보다 많을 수 있다.

[사실] donor ID가 split ancestry에 속하는지와, 희생 순간 **활성** 최종 경로인지도 나눈다. 부모가 왕 자식을 만든 뒤 희생하는 경우 ancestry에는 속하지만 활성 경로에는 속하지 않는다. 활성 최종 경로의 희생 N=0은 정의상 자연스럽다. 활성 경로가 죽으면 살아 있는 최종 왕까지 이어질 수 없다. 현재 최장 L≥8 조각의 사망은 별도 \`kingDeaths\`로 측정하며, 이를 ‘최종 왕이 죽었다’고 표현하지 않는다.`);
add(`## 3. 독립 검산: line share와 왕 곡선 양쪽 수치

[사실] [verify.js](../../exp/conversion/verify.js)는 mass ledger와 본 extractor를 호출하지 않는다. 원시 \`dragonUpdate\`의 머리/꼬리, split, death, \`tileChange\`를 독자적으로 복원하고 빈 이웃 및 사망 이유를 다시 분류한다. 공유한 것은 빠른 decoder와 동결된 layout assignment다. **N=${num(V.N)}게임**, 최종 점수·생존 수·팀 총길이 검사 오류 0, per-game 최종 길이/6개 곡선/희생 수/드롭 수/네 수령자 분할/r300 섭취량 불일치 0이다. 추가 [audit.js](../../exp/conversion/audit.js)는 **N=${num(AUDIT.groupsN)}집계 그룹** 전부를 독립 합계와 대조했고 일치했다. ${V.canonicalReconciliation?`이번 실행은 처음 N=${num(V.recountedInputFiles)}개 원본 파일을 전수 재계산한 뒤, 초기 세트 사이의 바이트 동일 기보 2쌍을 정규화했다. 해당 고유 2게임은 독립 스크립트로 한 번 더 재계산했고, 세트 membership을 보존한 N=${num(Object.keys(T.groups).length)}그룹의 합계/곡선이 정규화 전 독립 결과와 전부 같음을 확인했다. 따라서 최종 고유 게임 검산 N=${num(V.N)}이며, 단순히 반복 파일을 별도 게임으로 세지 않는다. [canonical_reconcile.js](../../exp/conversion/canonical_reconcile.js)에 이 증명을 보존했다.`:''} 계보·거리 계산 전체를 독립 검증했다고 확대하지 않는다.

[사실] 아래는 r300–499에 생성한 희생 드롭의 line 분자/전체 분모다. ‘원본’은 주 스크립트, ‘독립’은 별도 원시 이벤트 스크립트이며 두 값 모두 제시한다. 모든 W0–W12와 세트별 층의 검산은 [verification.json](../../exp/conversion/verification.json)에 있다.`);
table(['맵','역할','게임 N','원본 line/드롭','독립 line/드롭','원본/독립 share'],coreRows((m,r,l,a)=>{const v=V.groups[m+'|'+r+'|r500'];return [labels[m],l,a.N,`${num(a.line300)}/${num(a.drops300)}`,`${num(v.independent.line300)}/${num(v.independent.drops300)}`,`${pct(a.shares300.line,2)} / ${pct(v.independent.line300/v.independent.drops300,2)}`];},primaryRoles));
add(`[사실] 곡선은 아래 **길이 합계 벡터 [250,300,350,400,450,500]**로도 양쪽 수치를 제시한다. 행의 N은 각 지점의 유효 계보 N이다. Autarky 엘리트 패는 완주 게임 N=928 중 최종 생존 계보가 없는 1게임이 있어 곡선 N=927이다. 최종 점수 평균은 그 0점까지 포함해 **21,839/928=23.53**이고, 아래 r500 계보 평균 23.56은 생존 계보 N=927의 값이다.`);
table(['맵','역할','지점별 N','원본 길이 합계 벡터','독립 길이 합계 벡터'],coreRows((m,r,l,a)=>{const b=V.groups[m+'|'+r+'|r500'];return [labels[m],l,[250,300,350,400,450,500].map(q=>a.curve[q].N).join('/'),[250,300,350,400,450,500].map(q=>num(a.curve[q].sum)).join(', '),[250,300,350,400,450,500].map(q=>num(b.curve[q]?.independent)).join(', ')];},primaryRoles));
add(`## 4. 왕 성장: 어느 연결에서 멈추는가

[사실] 다음은 활성 최종 왕 경로의 평균 길이다. 열의 N은 앞의 검산 정의를 따른다. W0–W12는 과거 15세트를 묶은 기술통계이며 최근 stack11은 \`bench-s11-1..3\`이다. 과거 W12와 최근 benchmark를 섞지 않았다.`);
table(['맵','역할','완주 게임 N','r250','r300','r350','r400','r450','r500'],coreRows((m,r,l,a)=>[labels[m],l,a.N,...[250,300,350,400,450,500].map(q=>a.curve[q].N===a.N?f(a.curve[q].mean):`${f(a.curve[q].mean)} (N=${a.curve[q].N})`)]));
add(`[사실] r300–499의 유입/유출 회계도 분리했다. \`L500=L300+전체 섭취−sprint 비용−off-path split−path-transfer split 비용\`이 정확히 닫힌다. 표 값은 게임당 평균이며 괄호의 N은 시작 r300 계보가 있는 게임 수다. 희생 진주만으로 최종 성장을 설명하지 않는다.`);
table(['맵','역할','회계 N','희생 섭취/게임','자연 진주 섭취/게임','전체 섭취/게임','sprint+split 손실/게임','현재 최장 L≥8 사망 N (게임당)','L500−L300/게임'],coreRows((m,r,l,a)=>{const b=a.balance300;return [labels[m],l,b.N,f(a.lineSacEat300.mean),f(a.lineNatural300.mean),f(avg(b.eat,b.N)),f(avg(b.sprint+b.splitOff+b.splitPath,b.N)),`${num(a.kingDeaths)} (${f(a.kingDeaths/a.N)})`,f(avg(b.final-b.L300,b.N))];},primaryRoles));
add(`[해석] Slithery a의 v1(N=6)은 자연 진주를 왕에게 **24.67/게임** 공급하지만 희생 유입은 **9.00**, 엘리트 승(N=988)은 각각 **10.92/36.55**다. 즉 자연 섭취 증가가 마지막 전환 부족을 가린다. b의 v1(N=12)은 r300→400이 **7.42→10.50**에서 멈춘다. Schooltime a v1(N=8)은 r250→300 **13.88→12.38**로 내려간 뒤 성장하지만, 희생 유입 **6.13**과 손실 **15.75**가 엘리트 승(N=1,055)의 **28.18/9.41**에 못 미친다.

[해석] Trauma v1(N=17)은 r300 왕 **3.12**에서 r450 **6.59**로만 자란다. r300 이후 팀 희생 드롭 총량 자체가 **7.06/게임**으로 엘리트 승(N=1,918)의 **64.26**보다 적다. 단순 recipient 교체로 19.48을 만들 수 없다. Autarky v1(N=18)은 왕 r250 **21.94**, 최종 **61.11**, 후반 손실 **0.72**, 희생 드롭 적 섭취 **0/417**이다. 요새의 기존 큰 왕과 자연 섭취를 깨지 않는 처방이 필요하다.

### W0–W12와 v1 각 wave

[사실] 아래 각 셀은 **N전체/완주; 완주 최종 왕; 완주 r300–499 line 희생 섭취**다. 조기 종료의 0점은 전체 N에 포함하되 완주 평균에는 들어가지 않는다. complete N=0이면 평균은 표시하지 않는다. line share 및 여섯 지점 곡선은 각 \`ours:set:*:top6\` 그룹에 모두 있다. W0의 merge2 세 세트만 같은 family로 묶었다.`);
const waves=[['W0 (merge2 3세트)','ours:merge2:top6'],...Array.from({length:6},(_,i)=>['W'+(i+1),'ours:set:cand-stack'+(i+1)+'-online:top6']),['W7 (stack6 r2)','ours:set:cand-stack6-online-r2:top6'],...Array.from({length:5},(_,i)=>['W'+(i+8),'ours:set:cand-stack'+(i+7)+'-online:top6'])];
function waveCell(m,r){const a=g(m,r,'all'),b=g(m,r);return `${a?.N||0}/${b?.N||0}; ${b?f(b.final.mean,1):'—'}; ${b?f(b.lineSacEat300.mean,1):'—'}`;}
table(['wave',...MAPS.map(m=>labels[m])],waves.map(([l,r])=>[l,...MAPS.map(m=>waveCell(m,r))]));
table(['온라인 세트',...MAPS.map(m=>labels[m])],['v1-w1','v1-w2','v1-w3','bench-s11-1','bench-s11-2','bench-s11-3'].map(s=>[s,...MAPS.map(m=>waveCell(m,'ours:set:'+s+':top6'))]));
add(`[사실] 팀 안에 쌓인 큰 조각 질량과 수령자 승격도 직접 측정했다. 다음 heads/mass는 r250 팀 전체, 최장 일치 N은 해당 시점 최장 ID가 활성 최종 경로와 같은 게임 수다. r450 큰 아군 질량은 왕 밖의 L≥8 조각 길이 합계/게임이다. Slithery에서는 같은 head 수로 출발해도 최종 경로의 성장과 공급 연결이 갈린다.`);
table(['맵','역할/게임 N','r250 heads / 팀 질량 평균','r300 최장=최종 경로 N/유효 N','r450 최장=최종 경로 N/유효 N','r450 왕 밖 L≥8 질량/게임'],coreRows((m,r,l,a)=>{const c=a.curveMoments;return [labels[m],`${l}/${a.N}`,`${f(c[250].heads/c[250].N)} / ${f(c[250].mass/c[250].N)}`,`${c[300].lineIsMax}/${c[300].N}`,`${c[450].lineIsMax}/${c[450].N}`,f(c[450].otherBigMass/c[450].N)];},primaryRoles));
add(`[사실] r250 이후 만들어진 희생 패킷의 왕 총 회수량으로 게임도 분류했다. 아래 N은 게임 수이며 각 행 합계는 완주 게임 N이다. ‘0’이 표시문에서 왕을 한 번도 선언하지 않았다는 뜻은 아니다.`);
table(['맵','역할/게임 N','생존 왕 없음 N','왕 회수 0 N','1–9 N','10–24 N','≥25 N'],coreRows((m,r,l,a)=>[labels[m],`${l}/${a.N}`,...['noSurvivingKing','zeroLineFeed','lineFeed1-9','lineFeed10-24','lineFeed25+'].map(k=>num(a.gameClasses[k]))],primaryRoles));
add(`[사실] 이번 맵/시간/완주 층에서 v1 Slithery의 r300–499 희생 섭취는 **146/18=8.11**, 생성 line share는 **142/880=16.14%**다. brief의 혼합 모집단 수치 6.8과 22%를 이 분모에 그대로 대입하지 않았다. 같은 상대 세트의 평균 점수 25.78/58.72는 재현했다. 최근 benchmark Slithery는 전체 N=18, 완주 N=16이며 레이아웃 구성도 v1(a6/b12)과 다르므로 수치 차이를 처치 효과로 해석하지 않는다.`);
add(`## 5. 희생 기하와 수령자

### 길이, 계보, 거리, 회수 시간

[사실] 다음 표의 희생은 r250–499 전부다. 길이는 평균 및 p50/p90, 거리·지연은 p50/p90다. ‘머리 거리 N’은 유효 정적 거리의 이벤트 수, ‘왕 드롭 N’은 왕이 실제로 먹은 드롭 수, ‘first N’은 왕 섭취가 한 번이라도 있었던 패킷 수다. 마지막 열의 ancestry는 기증자 ID가 split ancestry에 속하는 수다.`);
table(['맵','역할/게임 N','희생 N','기증 L 평균; p50/p90','머리 거리 p50/p90 (N)','왕 드롭 거리 p50/p90 (N)','왕 회수 지연 p50/p90 (드롭 N)','첫 회수 왕 턴 p50/p90 (패킷 N)','ancestry 기증 N / 희생 N'],coreRows((m,r,l,a)=>[labels[m],`${l} / ${a.N}`,num(a.sacN),`${f(a.feederLength.mean)}; ${a.feederLength.p50}/${a.feederLength.p90}`,`${a.feederDistance.p50}/${a.feederDistance.p90} (${num(a.feederDistance.N)})`,`${a.lineDropDistance.p50}/${a.lineDropDistance.p90} (${num(a.lineDropDistance.N)})`,`${a.delay.p50}/${a.delay.p90} (${num(a.delay.N)})`,`${a.kingTurnsToFirst.p50}/${a.kingTurnsToFirst.p90} (${num(a.kingTurnsToFirst.N)})`,`${num(a.feederGenealogy.ancestorN)}/${num(a.sacN)}`],primaryRoles));
add(`[사실] 엘리트 승의 전체 기증자 머리 거리는 Slithery a/b **23/20**, Schooltime a **24**, Trauma **23**칸 중앙값이지만 왕이 먹은 드롭의 당시 거리 중앙값은 전부 **3**이다(각 N은 표). Autarky는 기증자 머리도 **4**칸 중앙값으로 가깝다. 활성 최종 경로 자체의 희생은 위 15개 그룹 **N=0**; ancestry 부모의 사후 급식은 존재한다.

[해석] ‘왕 주변에서만 모두 희생한다’는 전체 군집 설명은 맞지 않는다. 대부분의 지역 죽음/섭취는 왕 밖의 아군 사이에 일어나고, **왕으로 들어오는 마지막 연결이 가깝다**. 최종 왕 ancestry에 속한 조각만 feeder로 제한할 이유도 없다.

### 드롭 전체의 행선지

[사실] 아래는 r300–499 생성 드롭의 네 행선지다. 게임별 평균을 표에 넣되 share는 전체 진주 가중 비율이다. ‘생성 N’은 드롭 분모, ‘희생 N’은 패킷 수다. r250–299까지 포함한 동일 값은 \`shares250\`/\`drops\`/\`toLine\` 등에 있다.`);
table(['맵','역할/게임 N','희생 N','생성 드롭 N (게임당)','왕 계보','다른 아군','적','미회수','r300–499 왕 희생 섭취/게임'],coreRows((m,r,l,a)=>[labels[m],`${l}/${a.N}`,num(a.sac300N),`${num(a.drops300)} (${f(a.drops300/a.N)})`,pct(a.shares300.line),pct(a.shares300.ally),pct(a.shares300.enemy),pct(a.shares300.none),f(a.lineSacEat300.mean)]));
add(`[사실] r250–499 드롭 분모로도 왕/아군/적/미회수를 확인할 수 있다.`);
table(['맵','역할/게임 N','생성 드롭 N','왕/아군/적/미회수 N','왕/아군/적/미회수 %'],coreRows((m,r,l,a)=>[labels[m],`${l}/${a.N}`,num(a.drops),[a.toLine,a.toAlly,a.toEnemy,a.none].map(num).join('/'),[a.shares250.line,a.shares250.ally,a.shares250.enemy,a.shares250.none].map(x=>pct(x)).join('/')],primaryRoles));
add(`[해석] share 하나만 올리는 것은 목표에 충분하지 않다. Trauma v1의 생성 line share **43.33%(N=120드롭/17게임)**는 엘리트 승의 **29.55%(N=${num(g('Trauma/a','eliteWinner').drops300)}드롭/1,918게임)**보다 높지만 절대 공급은 **3.06 대 19.48**이다. 반대로 Slithery v1에서는 적보다 **다른 아군**에게 들어가는 비중이 훨씬 크다. 적 도난만 해결해서는 마지막 왕의 점수가 복구되지 않는다.`);
add(`## 6. 급식 토폴로지와 왕의 이동

### 모든 패킷 클래스의 크기

[사실] 아래 여섯 클래스의 N 합계는 희생 N과 같다. 각 셀은 이벤트 수이며 성공/실패를 같이 보여준다. 마지막 열의 direct/local/far 비율은 실제 왕 섭취 진주 수를 분모로 한다.`);
table(['맵','역할/게임 N','희생 N','direct','local 4–8','far ≥9','다른 아군','적 우세','미회수','왕 진주 direct/local/far %'],coreRows((m,r,l,a)=>[labels[m],`${l}/${a.N}`,num(a.sacN),...['direct','localPickup','fieldTour','otherAlly','enemyTheft','uncollected'].map(k=>num(a.classes[k])),['direct','localPickup','fieldTour'].map(k=>pct((a.topologyPearls[k]?.line||0)/a.toLine)).join('/')],primaryRoles));
add(`[사실] 기증자 머리 거리별로 **실패를 포함한 모든 드롭**의 왕 회수율을 다시 조건화했다. 아래 셀은 \`기증 희생 N; 왕 섭취/생성 드롭\`이다. 이 표는 성공 direct만 고른 것과 달리 배달 성공 확률의 관측 분모를 갖는다.`);
function geoCell(a,dc){const z={N:0,drops:0,line:0};for(const [k,v]of Object.entries(a.geometryCells))if(k.endsWith('|'+dc))for(const q of Object.keys(z))z[q]+=v[q];return `${num(z.N)}; ${num(z.line)}/${num(z.drops)} (${pct(z.line/z.drops)})`;}
table(['맵','역할/게임 N','near 0–3','local 4–8','far ≥9'],coreRows((m,r,l,a)=>[labels[m],`${l}/${a.N}`,...['near0-3','local4-8','far9+'].map(d=>geoCell(a,d))],primaryRoles));
add(`[사실] 엘리트 승의 왕 섭취 진주 중 direct는 **73.3–80.7%**, 먼 fieldTour는 **1.6–3.3%**다(5개 맵, 각 게임/진주 N은 위 표). 먼 지역 패킷의 왕 회수율은 **0.76–2.02%**에 그친다. ‘왕이 넓게 흩어진 드롭만 순회해서 만든다’는 설명은 이 마지막 연결의 주 형태가 아니다.

### 릴레이: 작은 조각 → 수령자 → 왕

[사실] 릴레이의 측정 조건은 **왕 밖의 같은 ID가 이전 희생을 먹고, 나중에 자신도 희생해서 왕에게 ≥1개를 공급**하는 것이다. split 자손으로 넘어간 릴레이는 따라가지 않았고, r250 이전 첫 다리도 포함하지 않았다. ‘두 번째 패킷의 왕 진주’는 그 패킷 전체에서 왕이 먹은 수다. 최초 진주가 성장·split·사망을 거쳐 보존됐다는 토큰 추적 결과가 아니다. 따라서 아래 비율은 *릴레이 이력이 있는 패킷의 기여*, 개별 진주의 재변환율이 아니다.`);
table(['맵','역할/게임 N','첫 다리 진주 N','두 번째 희생 패킷 N','그 패킷 왕 진주/전체 왕 희생 진주','첫 다리 수령자 L p50/평균 (진주 N)'],coreRows((m,r,l,a)=>[labels[m],`${l}/${a.N}`,num(a.relay.candidateFirstLegPearls),num(a.relay.chains),`${num(a.relay.secondLegLinePearls)}/${num(a.toLine)} (${pct(a.relay.secondLegLinePearls/a.toLine)})`,`${a.relay.midLengths.p50}/${f(a.relay.midLengths.mean)} (${num(a.relay.midLengths.N)})`],primaryRoles));
add(`[해석] 엘리트 승에서 왕 진주의 **39.5–50.6%**는 이 보수적인 same-ID 릴레이 이력이 있는 패킷에서 온다. 그러나 첫 수령자 길이 중앙값은 **3–4**다. 중간 수령자를 ‘처음부터 L≥8인 중형’으로만 제한하면 지역 성장의 초기 연결을 놓친다. 가까운 직접 급식과 릴레이는 대안 관계가 아니다. 릴레이의 마지막 죽음이 왕 가까이 일어날 수 있다.

### 왕이 걷는 양과 기다림

[사실] r300–499 활성 계보의 성공 이동 칸수를 드롭 섭취 수로 나눴다. ‘죽음 전체’에는 양 팀의 희생/전투/고립 드롭이 모두 있고, ‘자기 희생’은 앞의 lineSacEat300과 같다. 모든 왕 턴은 이동 또는 split 행동이며 규칙에 합법적인 wait가 없다. zero-step과 split 수가 아래 모든 행에서 일치했다.`);
table(['맵','역할/게임 N','왕 행동 턴 N','성공 이동 칸 N','죽음 드롭 섭취 N; 칸/진주','자기 희생 섭취 N; 칸/진주','중복 head 관측 %','거리≤8 아군 머리 없는 턴 N (%)','zero-step N / split N','20턴≤8고유칸 윈도 N/전체 N'],coreRows((m,r,l,a)=>{const p=a.path;return [labels[m],`${l}/${a.N}`,num(p.turns),num(p.steps),`${num(p.dropEaten)}; ${f(p.tilesPerDrop)}`,`${num(p.sacEaten)}; ${f(p.tilesPerSac)}`,pct(p.revisit/p.turns),`${num(p.nearZero)} (${pct(p.nearZero/p.turns)})`,`${num(p.zeroSteps)}/${num(p.splitActions)}`,`${num(p.localWindowUnique8)}/${num(p.localWindowN)}`];},primaryRoles));
add(`[사실] 엘리트 승의 자기 희생 진주당 이동은 Slithery a/b **5.48/5.32**, Schooltime a **7.11**, Trauma **10.26**, Autarky **9.08**칸이다. v1은 각각 **22.22/26.21/33.35/65.33/14.08**칸(각 N은 표). 왕 head 위치 재방문율이 더 높은 v1에서도 희생 섭취 효율이 낮다.

[해석] 가까운 급식 장을 유지하면서 안전한 넓은 경로를 걷는 것이 목표다. ‘왕을 정지시켜 feeder가 모이게 한다’는 구현은 규칙에 맞지 않는다. 긴 몸이 들어갈 수 있는 순환 경로를 쓰되 작은 반복 회전으로 길이 이상의 몸을 밀어 넣지 않는다. 스프린트는 회수 속도를 올리는 대신 길이를 잃으므로 위험 탈출 또는 순이익이 확인되는 회수에만 쓴다.`);
add(`## 7. 타이밍: r250의 단계와 작은 조각의 순서

[사실] 값은 **희생 이벤트 / 살아 있는 팀-round 노출**이다. 완주 그룹이라 각 10라운드 구간의 노출은 게임 N×10이며 셀에 이벤트 N을 같이 적었다. r0–249는 10라운드 ledger 집계, r250–499는 정확한 이벤트 라운드를 보존한다. 다음 표의 240→250 비교는 bin 경계에 맞는다.`);
table(['맵','역할/게임 N','구간별 team-round N','r240–249 rate (희생 N)','r250–259','r260–269','r350–359','r400–409','r450–459'],coreRows((m,r,l,a)=>[labels[m],`${l}/${a.N}`,a.N*10,...[240,250,260,350,400,450].map(q=>{const x=a.sacTiming10.find(x=>x.from===q);return `${f(x.rate,3)} (${num(x.N)})`;})],primaryRoles));
add(`[사실] 엘리트 승의 r240–249→250–259 비율은 Slithery a **0.114→0.506 (N=988게임)**, b **0.117→0.458 (N=1,051)**, Schooltime a **0.070→0.265 (N=1,055)**, Trauma **0.043→0.172 (N=1,918)**다. Autarky **0.015→0.047 (N=928)**도 증가하지만 큰 재활용 파동은 r350–450에 늦게 온다.

[사실] 첫 25라운드와 r400–424의 기증자 순서를 비교했다. ‘near/local/far’는 모든 기증자에서의 분포이며, no-line 이벤트가 있으면 별도로 표시한다. 수치가 없는 v1 phase도 **N=0**으로 남긴다.`);
table(['맵','역할/게임 N','희생 구간','기증 이벤트 N','L평균','작음 L≤4 %','큰 L≥8 %','near≤3/local4–8/far≥9 %','거리 평균 (유효 N)','왕 부재/거리없음 N'],coreRows((m,r,l,a)=>[m,r,l,a], [roles[0],roles[4]]).flatMap(([m,r,l,a])=>[250,400].map(q=>{const p=a.phaseLen[q]||{N:0,distanceN:0};return [labels[m],`${l}/${a.N}`,`${q}–${q+24}`,num(p.N),f(avg(p.len,p.N)),pct(avg(p.small4,p.N)),pct(avg(p.big8,p.N)),[p.near3,p.local8,p.far9].map(n=>pct(avg(n,p.N))).join('/'),`${f(avg(p.distance,p.distanceN))} (${num(p.distanceN)})`,num(p.noLine)];})));
add(`[사실] 엘리트 승 r250–274의 작은 L≤4 비율은 Slithery a/b **93.5/94.2% (희생 N=10,939/10,857)**, Schooltime a **86.2%(N=7,209)**, Trauma **98.5%(N=7,726)**, Autarky **97.5%(N=1,052)**다. 후반 L≥8 기증은 늘지만 r400–424에도 이벤트 대부분은 작은 조각이다. 거리와 near 비율은 시간이 지나며 일괄 수렴하지 않는다.

[해석] r250은 작은 지역 재활용을 시작하는 스위치로 읽을 수 있다. 왕 선정을 끝내고 모든 작은 조각을 한 번에 죽이는 시계로 읽으면 공급망이 끝난다. 생산자는 계속 수확·split하면서 필요한 지역 relay를 만들고, r350 이후 큰 수령자도 마지막 왕에게 연결해야 한다.

### v1의 정체 구간 진단

[사실] 다음은 v1의 비증가 구간 L(q+50)≤L(q)이다. ‘근처 드롭’은 기증자 머리→왕 거리 ≤8의 희생 드롭이며, ‘아군 없음’은 왕 머리에서 거리 ≤8에 다른 아군 **머리**가 없는 행동 턴이다. 머리가 있다는 사실이 기증 가능 길이/예약/경로 확보를 뜻하지 않는다. ‘왕 사망’은 현재 최장 L≥8 조각의 사망이다.`);
table(['맵','구간','비증가 게임 N/유효 게임 N','평균 성장','비증가 구간 왕 턴 N','그중 아군 머리 없음 N','근처 드롭 N → 왕/아군/적 N','현재 왕 사망 N'],MAPS.flatMap(m=>{const a=g(m,'ours:v1:top6');return [250,300,350,400,450].map(q=>{const s=a.stalls[q];return [labels[m],`${q}–${q+50}`,`${s.stallN}/${s.N}`,f(s.growth.mean),num(s.stallTurns),num(s.stallNoFeederTurns),`${num(s.stallNearDropN)} → ${num(s.stallNearToLine)}/${num(s.stallNearToAlly)}/${num(s.stallNearToEnemy)}`,num(s.stallKingDeaths)];});}));
add(`[해석] **Slithery a:** v1(N=6)은 r250–274에 88회(14.67/게임) 희생하지만 near≤3은 6/88뿐이다. r300에는 최종 경로가 현재 최장인 게임이 **0/6**, 다른 L≥8 조각에 **80.83/게임** 길이가 있다. r450에도 다른 큰 조각의 길이 **70.67/게임**이 남는다. ‘왕이 될 조각을 전혀 못 키웠다’보다 여러 수령자에 쌓은 뒤 마지막 연결을 못 만든 설명이 맞는다. r350–374 희생은 **20/6=3.33/게임**으로 엘리트 승의 지속 공급보다 작아진다.

[해석] **Slithery b:** v1의 r300–350 비증가 **9/12게임**에서 아군 머리 부재는 **1/456턴**뿐인데 가까운 드롭은 **11개**, 왕 2/아군 7/적 2다. r350–400 비증가 **8/12게임**에는 가까운 희생 드롭 **0개**다. 아군이 왕 주변에 있어도 feeder로 전환되지 않는 구간이다. 왕 사망도 각각 N=1/2여서 일부 실패의 추가 원인이다.

[해석] **Schooltime a:** v1(N=8)은 r250–300 비증가 **7/8게임**, 그 구간 현재 왕 사망 **N=5**, 가까운 드롭 **N=0**이다. r250 heads **24.50** 대 엘리트 승 **59.13(N=1,055)**, r450 다른 큰 조각 질량 **32.63** 대 **122.36**이다. 이 맵은 최종 수령자 지정뿐 아니라 분산 생산량과 왕의 split/충돌 손실도 같이 봐야 한다.

[해석] **Trauma:** v1(N=17) r350–400 비증가 **10/17게임**, r400–450 **8/17게임**에서 가까운 희생 드롭 **각 N=0**, 현재 왕 사망 **각 N=0**이다. 전체 r250 이후 희생 **75회 중 54회**가 마지막 r475–499에 몰린다. r400–424에는 희생 **N=0**. 초기 recipient를 키우는 연결이 막힌 상태에서 재료도 적고 clock의 실질 행동이 늦다. 적의 도난은 후반 생성 **7/120**이므로 이것만을 주원인으로 삼지 않는다.

[해석] **Autarky:** v1(N=18) r350–400/400–450/450–500 비증가 **각 0/18게임**, 성장 **10.72/10.50/10.11**이다. fort 내부 king route와 자연 섭취를 유지하면서 남은 큰 동료의 예정 급식만 추가하는 것이 목표다. SE의 r250 대량 전환 시간을 이 맵에 그대로 옮길 이유가 없다.`);
add(`## 8. 정독: 클래스 크기 → 게임 ID와 라운드

[사실] 아래 후보 N은 사전 조건에 맞는 이벤트 수다. 기본 5개는 r300 이후, 완주 엘리트 승, 왕 섭취 ≥2인 성공 subset이며 full direct N은 6절의 전수 direct 크기다. 후반 큰 급식은 r≥375, L≥8, 왕 섭취≥3의 subset다. 게임 1개 예는 해당 클래스를 설명할 뿐 빈도를 다시 추정하지 않는다.`);
table(['맵','선택 종류','후보 N / 선택 클래스 N','전수 클래스 N','게임 ID / team / r','기증자 L; 거리 → 당시 왕 ID','왕/아군/적/미회수 진주','왕 섭취 라운드','최종 왕 ID / L'],D.map(d=>{const p=d.pick;return [labels[p.map],'',p.classCandidateN?`${num(p.candidateN)} / ${num(p.classCandidateN)}`:num(p.candidateN),p.fullClassN?num(p.fullClassN):'조건부 subset',`${p.gameId}/${p.team}/r${p.round}`,`#${p.id} L${p.len}; d${p.distance} → #${p.lineId}`,`${d.target.toLine}/${d.target.toAlly}/${d.target.toEnemy}/${d.target.none}`,d.target.drops.filter(x=>x.recipient==='line').map(x=>x.eat.r).sort((a,b)=>a-b).join(', ')||'없음',`#${d.final.id}/L${d.final.len}`];}).map((row,i)=>{const p=D[i].pick;row[1]=p.studyClass|| (p.selection.startsWith('late')?'후반 L≥8':'중앙값 direct');return row;}));
add(`[사실] 기본 예의 upstream도 확인했다(N=5선택 게임). Slithery a **598432 B r491 #1496 L4→#1267**은 **r488 #1728 L2의 1진주**를 먼저 받았다. Slithery b **588756 A r385 #1149 L4→#1123**, Schooltime a **586373 B r404 #639 L4→#636**에는 이 정의의 same-ID 이전 희생 섭취가 없다. Trauma **583552 B r427 #329 L3→#378**은 **r394 #106 L2의 1진주**를, Autarky **587776 A r446 #234 L4→#48**은 **r374 #219 L3의 1진주**를 받았다. 다섯 예 모두 가까운 최종 급식이며 일부는 relay 이력도 가진다.

### 보드 1: Slithery a의 큰 급식과 한 진주의 도난

[사실] **게임 583445, B, r438 (선택 N=1; 같은 큰 후반 급식 후보 N=1,154)**. #968 L12가 당시 왕 #751 L36의 머리 거리 2에서 죽었다. 6드롭 중 왕 5, 적 #991이 1개를 먹었다. 왕 회수는 **r440/444/455/457/461**, 지연 **2/6/17/19/23**. 적은 머리 쪽 드롭을 **r460(22라운드 뒤)** 회수했다. 그림은 사망 직전, 2라운드 뒤, 마지막 왕 회수 다음 라운드다. 파란색은 활성 왕, 주황은 기증자, 붉은색은 적, 금색 테두리는 해당 드롭 위치다. 흰 진주는 다른 출처다.

![Slithery a 583445 r438–462 실제 급식 보드](../../exp/conversion/board-Slithery_Fight_a.png)

[해석] 머리 거리 2만 확인하면 긴 기증자의 휘어진 몸이 만드는 6개 드롭과 늦게 오는 적을 놓친다. 첫 진주를 빨리 먹었다는 것과 패킷 전체를 빨리 회수했다는 것은 다르다.

### 보드 2: Trauma의 작은 조각 → L9 → 왕

[사실] **게임 581297, A, r377 (선택 N=1; 후보 N=473)**. #240은 **r302 #246 L2, r308 #215 L3, r348 #274 L2**의 희생에서 각 1개, 총 **3개**를 받아 성장했다. r377 L9에서 왕 #69 L18의 머리 거리 2에서 죽고 5개 모두 왕이 **r379/381/383/385/391**에 먹었다. 가장 긴 지연은 14라운드다. 직접에 속하면서 관측 가능한 relay 이력을 가진 예다. L9의 나머지 질량이나 최종 드롭 5개를 최초 3진주에 귀속하지 않았다.

![Trauma 581297 r377–392 실제 릴레이 최종 급식 보드](../../exp/conversion/board-Trauma_a.png)

[해석] Trauma의 중간 recipient는 작은 희생을 차곡차곡 받아 L9가 된 뒤 왕의 바깥 경로에 몸을 배치했다. 포켓 안의 왕에게 모든 조각을 밀어 넣는 형태로 읽을 필요가 없다.

### 보드 3: Autarky의 요새 경로에 놓인 L8

[사실] **게임 576775, A, r434 (선택 N=1; 후보 N=457)**. #304 L8이 #298 L14 머리의 한 칸 앞에서 죽었다. 왕은 4드롭을 **r435/437/439/441**, 즉 **1/3/5/7라운드** 뒤 모두 먹었다. 적 #362가 주변에 있지만 이 패킷의 적 섭취는 **0/4**였다. 이 한 사례의 무도난을 전체 요새의 안전 보장으로 확대하지 않는다.

![Autarky 576775 r434–442 실제 급식 보드](../../exp/conversion/board-Autarky_a.png)

[해석] 왕이 이미 따라가는 넓은 경로에 feeder의 몸을 직렬로 놓으면 회수 순서가 짧고 예측 가능하다. 요새에서는 머리 거리보다 왕이 앞으로 먹을 공간의 예약이 유용하다.

### 실패와 예외도 같은 절차로 읽기

[사실] **Slithery b v1, 게임 753184 A r465 (선택 N=1; 최종까지 L≥8로 생존하는 다른 수령자에게 ≥2진주가 간 후보 N=54)**. #596 L4, 왕 #282에서 거리 33. 두 드롭은 #598이 r465/r467에 먹고 그 조각은 최종 **L18**로 살아 남았다. 왕 L43 외에 L25/19/18/18/17 등 별도 질량이 남는다. 왕에게 직접 회수된 진주 **N=0**이며 적도 **N=0**이다.

[사실] **Schooltime a v1, 게임 744677 A r483 (선택 N=1; 같은 실패 후보 N=26)**. #505 L5의 3개는 #497이 r485/r487에 2개, #344가 r488에 1개를 먹었다. #344도 r489 L8에서 죽었지만 이 첫 패킷은 왕 #499 직접 섭취 **N=0**이다. #497은 최종 **L26**으로 남고 최종 왕은 **L86**. 높은 왕 점수 게임에도 마감 연결을 못 만든 지역 stock이 존재한다. #344의 다음 패킷 전체를 최초 1진주의 재전달이라고 세지 않는다.

[사실] **Trauma v1, 게임 744640 A r489 (선택 N=1; r475 이후 왕 섭취가 있는 후보 N=19)**. #265 L3가 거리 4에서 죽었다. r492 #299 왕이 1개, #52가 1개를 먹었다. #52는 r493 L3에서 다시 죽었다. 최종 왕 L10. 재활용이 없는 봇은 아니지만 대부분의 공급을 마감 11라운드 전에 시작한 사례다.

[사실] **엘리트 패 Slithery b, 게임 674922 A r392 (선택 N=1; r350 이후 L≥15 현재 왕의 피격 사망 후보 N=227)**. 당시 최장 #960 L35가 적 head 충돌로 죽고 18드롭을 아군이 전부 회수했다. 최종 계보의 당시 #1361 및 최종 #1768 L37은 그 18개를 직접 먹은 수 **N=0**이다. 팀 안으로 회수했다는 사실만으로 원래 왕을 보존한 것은 아니다. 이 이벤트는 희생이 아니라 \`rammed\`다.

[사실] **원거리 회수 Slithery a, 게임 588760 A r405 (선택 N=1; 성공 ≥2진주 far 후보 N=236; 전수 far 성공 N=763)**. #1471 L4, 왕 #896에서 거리 13. 두 진주를 왕이 r420/r426, 지연 15/21에 먹었다. 이 형태는 존재하지만 왕 진주의 1.6–3.3%라는 전수 규모와 함께 읽어야 한다.`);
add(`## 9. k8과 r250 clock이 놓친 것

### k8이 닫는 초기 연결

[사실] ‘당시 왕이 L≥max(own+4,8)’ 조건을 가까운 거리≤8 희생에 사후 적용했다. 표의 실패 진주는 **실제 관측에서 왕이 성공적으로 먹었지만 이 길이 gate는 통과하지 못했을 수**인 진주다. 다른 판단 조건/메시지/코드가 그 행동을 허용했을 수 있으므로 현 봇이 k8을 위반했다고 판정하지 않는다. 신규 gate 실험 N=0이다.`);
table(['맵','역할/게임 N','가까운 희생 N','k8 통과/실패 이벤트 N','실패 드롭 N','실패 조건에서도 왕이 먹은 N / 전체 왕 희생 N'],coreRows((m,r,l,a)=>{const k=a.nearK8Gate;return [labels[m],`${l}/${a.N}`,num(k.N),`${num(k.passes)}/${num(k.N-k.passes)}`,num(k.failsDrops),`${num(k.failsToLine)}/${num(a.toLine)} (${pct(k.failsToLine/a.toLine)})`];},[roles[0],roles[4]]));
add(`[해석] Trauma 엘리트 승은 k8이 막았을 연결에서 왕 진주 **6,442/42,146=15.3%(N=1,918게임)**를 얻었다. v1 관측은 **22/52=42.3%(N=17게임)**. 작은 recipient를 L8까지 기다리면 bootstrap이 늦을 수 있다. Slithery에서는 해당 비중이 작으므로 gate 숫자만 낮추는 것으로 전체 전환 문제를 해결한다고 기대하지 않는다.

### 큰 아군을 선택했어도 마지막 왕을 선택하지 않은 경우

[사실] 우리 \`feed/conv\` 표시문에서 실제 선언 대상 ID를 읽었다. 다음은 **r250 이후 완주 v1**의 라벨이 있는 희생들이다. N은 희생 이벤트이며 Trauma/Autarky의 unlabeled 이벤트는 제외되므로 전수 희생 N과 다를 수 있다. 별도 \`targets.json\`에 모든 라벨 이벤트가 있다.`);
table(['맵','게임 N / 라벨 희생 N','선언 대상=활성 최종 계보 N (%)','대상이 왕인 드롭: 왕/아군/적/미회수 N','대상이 왕 밖인 드롭: 왕/전체 N'],MAPS.map(m=>{const a=g(m,'ours:v1:top6'),v=T.declaredTargets.groups[m+'|ours:v1:top6|r500'];return [labels[m],`${a.N}/${v.N}`,`${v.targetIsLineN} (${pct(v.targetIsLineN/v.N)})`,[v.targetLine.line,v.targetLine.ally,v.targetLine.enemy,v.targetLine.none].join('/'),`${v.targetOffLine.line}/${v.targetOffLine.drops} (${pct(v.targetOffLine.line/v.targetOffLine.drops)})`];}));
add(`[해석] Slithery a/b v1의 선언 대상이 최종 왕 경로인 것은 **45/350=12.9%, 95/421=22.6%**다. 왕을 대상으로 선언한 패킷은 실제로 **51/72=70.8%, 99/174=56.9%**를 왕이 먹는다. 반대로 다른 대상으로 선언한 패킷의 왕 직접 회수는 **10/546=1.8%, 9/565=1.6%**다. ‘주변의 더 큰 아군에게 준다’에는 지역 성장 이후 그 recipient를 최종 왕으로 넘기는 규칙이 없다. 왕 대상으로 선언된 패킷도 다른 아군이 **21/72, 61/174**를 먹으므로 마지막 구간의 양보/예약이 필요하다.

[해석] r250 clock은 첫 지역 재활용 시작과 왕의 최종 선정을 한 사건으로 취급하기 쉽다. 엘리트 승의 최종 경로가 당시 최장인 비율은 r300 Slithery a/b **453/988=45.9%, 551/1,051=52.4%**, Schooltime a **306/1,055=29.0%**뿐이고 r450에는 **901/988=91.2%, 976/1,051=92.9%, 861/1,055=81.6%**다. r250에 고정한 임의의 큰 아군은 후반 왕과 다를 수 있다. local relay를 유지한 뒤 공급량과 생존 경로가 있는 왕을 지속적인 ID로 연결해야 한다.`);
add(`## 10. 구현 공통 규약 [해석]

다음 수치·상태 전이는 **제안이며 구현/자가대전 N=0**이다. 근거 N은 앞의 전수 표와 마지막 맵별 표에 있다. 과거 [supply-chain](../../legacy/research/observations/supply-chain.md)의 전원 집결 실패와 [pocket-harvest](pocket-harvest.md)의 생산자/출구 병목을 고려해 지역 생산과 급식 예약을 분리한다.

1. **역할과 두 시계.** 상태를 HARVEST → LOCAL_RELAY → KING_FEEDER로 둔다. SE는 r250부터 L2–4의 지역 재활용을 허용하고 생산적인 수확자를 전부 없애지 않는다. 초기 local recipient는 L3–7도 허용하되 donor보다 길고, 빈 길과 예정 드롭을 실제로 회수할 수 있어야 한다. r350에는 안전한 recipient를 잠정 왕 후보로 승격하고 r400 전후에는 최종 급식 ID를 안정화한다. Bootstrap은 \`recipient>donor\`, 마지막 peer 병합은 \`elected king≥donor\`를 출발 gate로 쓴다. k8의 own+4/8 바닥은 모든 지역 연결의 필수 조건으로 쓰지 않는다.
2. **알 수 있는 왕만 연결.** 봇은 미래 최종 왕을 모른다. 최근 관측/sonar의 ID·길이·head·안전 경로·주변 급식 재고로 후보를 정하고 동률은 full ID로 푼다. 4라운드 TTL, 기존 후보를 잦게 바꾸지 않는 hysteresis, 사망/경로 소실 때만 재선정을 둔다. 전체 합의나 전역 메모리를 가정하지 않는다. TTL 안의 왕 정보를 못 받은 지역은 local relay를 계속 운영한다. split으로 왕 자식에게 넘기면 새 ID로 명시적 승계 메시지를 보내고 이전 ID의 offer는 취소한다.
3. **소나는 살아 있을 때 교환.** \`KING\` → \`OFFER\` → \`ACK(slot round, donor ID, first-drop waypoint)\`를 사망 전 턴에 교환한다. sonar는 행동 후 살아 있을 때만 나가므로 희생 턴의 출하 공지는 전달되지 않는다. full ID를 8bit로 축약하지 않는다. 64bit 메시지 예: type3+round9+ID32+x6+y6+length8=64; KING은 king ID, OFFER/ACK은 donor ID를 싣고, ACK은 유효한 KING/offer 상태와 묶는다. 길이는 field 범위를 넘으면 포화/별도 패킷으로 처리한다. 한 방향에 두 개를 보내면 마지막 것만 남으므로 종류를 턴마다 나눠 보낸다. 발신자·팀 정보가 없는 메시지를 맹신하지 않고 시야의 아군 ID/기존 handshake와 확인한다. ID 순서에 따른 같은 round/다음 round 수신 차이를 slot round에 반영한다.
4. **드롭 몸 전체 예약.** donor가 자신의 몸 좌표를 행동 이력으로 확실히 복원했을 때만 body[0], body[2], ...의 드롭을 계산한다. 새 split child/재시작처럼 tail이 불명확하면 작은 확인 가능한 급식만 하거나 몸을 복원할 때까지 수확을 계속한다. 첫 드롭을 왕 예정 경로의 **1–3칸 앞**에 둔다. 큰 L≥8은 head만 맞추지 말고 다음 10–30턴 회수할 드롭 경로도 제시한다. OFFER가 예고한 희생 round를 키로 FOOTPRINT 청크를 보낸다(예: type3+round9+chunk4+4좌표쌍48=64bit). full donor ID를 가진 OFFER에 청크를 묶고 왕은 한 번에 pending donor 1개만 유지한다. 송신 중 TTL은 살아 있는 갱신 메시지로 유지하고 donor는 예고한 이동을 지킨다. 새 진주/장애물 때문에 미래 몸 좌표 예측이 바뀌면 offer를 취소하고 다시 계산한다. 왕이 ACK한 패킷을 1개씩 직렬 처리하고, 다음 donor는 현재 패킷 회수가 끝나거나 겹치지 않는 slot일 때만 죽는다.
5. **마지막 확인과 죽는 방법.** 희생 턴에 왕 ID/위치·빈 이동 대안·drop footprint·slot/적 위험을 다시 확인한다. 조건이 깨지면 donor는 안전 이동/수확을 계속하고 offer를 갱신한다. 유효한 자기 목 역진입은 몸을 이동시키기 전에 사망하므로 검증된 footprint를 유지할 수 있다. portal/heading 때문에 역방향의 실제 도착지가 목인지 확인한다. 아군 head로 충돌해서 왕을 함께 죽이는 급식을 쓰지 않는다. donor ID가 왕보다 작으면 같은 round 섭취가 가능하고, 크면 왕은 죽음 확인 다음 round부터 그 공간에 들어간다.
6. **왕의 움직임.** 기본 1칸 이동으로 예약 waypoint와 뒤의 짝수 body 드롭을 따라간다. 왕 route에 다른 아군이 새로 들어오면 회수보다 안전한 우회가 먼저다. route의 길이는 최소 현재 몸+예상 growth+여유칸을 수용해야 한다(초기 설계값 L+4는 검증 시작점). own tail도 아직 점유된 칸이므로 즉시 진입 불가다. 긴 왕을 작은 4칸 회전에 묶지 않는다. split은 최종 통합 단계에서 기본 금지하고 생존 탈출 예외만 두어 길이 누수를 막는다.
7. **도난과 아군 분산 회수 방지.** 예약된 드롭 구역은 비수령 아군이 양보하고 head/body로 왕 경로를 막지 않는다. 진주가 탐나도 lease TTL 동안 별도 수확 경로를 걷는다. 적 접근 예상이 왕보다 2라운드 이상 늦는 패킷만 승인한다는 설계 gate를 두되 **7×7 시야 밖 적을 없다고 가정하지 않는다**. 최신 입구 파수/sonar와 실제 통로 차단으로 보호된 구역을 우선한다. 긴 스프린트가 가능한 적의 ETA를 단일 보행 거리로 계산하지 않는다. 정보가 없거나 ingress가 열려 있으면 큰 패킷은 거절하고 작은 가까운 packet만 고려한다.
8. **마감.** 새 큰 급식은 원칙 r460 이전에 만들고, 남은 라운드가 footprint 회수 예상+안전 여유보다 적으면 만들지 않는다. 작은 L2–4는 1–3턴 첫 회수가 보장되는 slot에서만 r475 이후 허용한다. feeder가 왕에게 이동하는 동안 split/스프린트로 배달 길이를 잃는 비용도 제안 예산에 넣는다. 왕의 마지막 생존 길이를 늘리지 못하는 사망은 전환 성공으로 세지 않는다.

[해석] 출시 전 비교할 최소 지표는 선언 왕 일치율, near 예약 패킷의 왕/아군/적 share, r300 이후 왕 희생 섭취 절대량, r350–450 왕 성장, 왕 split 손실/사망, 생산자 자연 섭취다. 왕 일치율이 올라가도 Trauma 총 드롭이 유지되면 예상 상한부터 달라져야 한다. Autarky에서는 line 수만 늘리고 기존 자연 섭취/최종 길이가 낮아지는 변경을 채택하지 않는다.`);
add(`## 11. 산출물·한계·재현

[사실] [tables.json](../../exp/conversion/tables.json)은 보고서보다 먼저 저장했고, 현재 N=${num(Object.keys(T.groups).length)}집계 그룹과 N=${num(T.coverage.processed)}압축 이벤트 파일 mapping, declared target, 검산 참조를 담는다. [population.json](../../exp/conversion/population.json)은 동결된 게임 목록이다. [deep-selection.json](../../exp/conversion/deep-selection.json)/[deep-reads.json](../../exp/conversion/deep-reads.json)과 13개 \`deep-*.json.gz\`에 정독의 선택 분모·행동·섭취·복사된 보드 snapshot을 보존했다. 마지막에는 15줄 [SUMMARY.txt](../../exp/conversion/SUMMARY.txt)를 쓴다.

[사실] 재현 순서는 기존 population에서 \`node exp/conversion/extract.js\`, \`node exp/conversion/aggregate.js\`, \`node exp/conversion/targets.js\`, \`node exp/conversion/verify.js\`, \`node exp/conversion/audit.js\`, \`node exp/conversion/deep.js\`, \`PYTHONPATH=/opt/homebrew/lib/python3.13/site-packages python3 exp/conversion/draw_boards.py\`, \`node exp/conversion/make_report.js\`다. 추출/검산 worker는 각 최대 2개이며 두 파이프라인을 동시에 돌리지 않는다. 메모리 free<10%, 디스크 free<21GiB면 중단/일시 정지한다. 검산 후 자원 확인은 free memory ${AUDIT.resource.memory}%, disk ${f(AUDIT.resource.diskGiB)}GiB였다. 대형 캐시는 gzip만 유지했고 원시 replay의 uncompressed 복제는 만들지 않았다.

[사실] 추가 관측 연구의 한계는 다음과 같다. 승/패는 최종 점수로 정의해 selection을 포함하고, 여러 게임은 같은 battle·상대·봇 버전을 공유한다. 임시 몸을 무시한 정적 거리, 운영 정의의 희생, same-ID/r250 이후에만 잡히는 relay, partial vision과 전역 기보 정보의 차이를 구별했다. 상대 소스의 의도를 추론해 사실로 쓰지 않았다. 정확한 원 진주 질량이 relay를 지나 재전달됐는지, 새 protocol의 성능/CI, 아직 오지 않은 v12-w* 결과는 이 연구에서 측정하지 않았다(N=0). 키 숫자의 독립 검산은 완료했고 이 미측정 부분을 누락된 전수 게임으로 세지 않는다.

[사실] 참조한 이전 관측은 [map-atlas](map-atlas.md), [spatial-occupancy](spatial-occupancy.md), [pocket-harvest](pocket-harvest.md), [endgame-king](../../legacy/research/observations/endgame-king.md), [conversion-chain](../../legacy/research/observations/conversion-chain.md), [supply-chain](../../legacy/research/observations/supply-chain.md), 규칙 [ALL.md](../../rules/ALL.md)다. bot/versions/eval/다른 exp/legacy/data/.cache를 수정하지 않았고 네트워크·업로드·commit을 하지 않았다.

## 12. 맵별 구현 프로토콜 [해석] — 보고서 마지막 표

**예상 line pearls는 새 봇 측정값이 아닌 조건부 배달 예산**이다. 공통 계산은 r300–499에 지정 feeder가 희생한 \`ceil(L/2)\` 드롭 수 × 예약 회수율이다. SE의 60–75%, 요새의 70–90%는 설계 가정이며 실험 N=0. 현재 관측과 필요한 공급량을 함께 적는다. 거리/시각은 제안값이고 엘리트가 그 상수를 사용했다는 뜻이 아니다.`);
table(['맵 / 관측 근거 N','누가 → 누구, 시점','희생 위치·왕 경로','도난/병목 방지','조건부 r300–499 line 진주 예산 / 관측값'],[
 ['Slithery a / 엘리트 승 988, v1 6, 최근 stack11 9','r250 L2–4 지역 수확자 → L3–7 relay; r350 잠정 왕, r400–450 relay L5–12 → 안정된 왕 ID. 생산 pocket의 수확자는 남긴다.','아군 생산 구역 바깥의 넓은 2-core 경로. 첫 드롭은 왕 1–3칸 앞; 모든 짝수 body 좌표를 lease. 왕은 1칸으로 패킷 순회, 큰 패킷은 r460 전에 출하.','왕 밖 큰 아군에 쌓은 stock을 두 번째 급식으로 잇는다. 입구 파수+최근 메시지로 보호된 lane만 사용; 적 정보가 없으면 큰 packet 거절. 비수령 아군은 예약 진주 양보.','12×L3(24드롭)+2×L8(8)=32, ×60–75% → **19–24**. v1 9.00, 엘리트 36.55. 현재 생성 56.00/게임 안에 재료는 있으나 공간적 배달은 검증 N=0.'],
 ['Slithery b / 엘리트 승 1,051, v1 12, 최근 stack11 7','a와 같은 두 단계. r250 전원 전환을 줄이고 fountain/pocket 생산자를 유지. r375–450에서 준비된 relay를 왕 ID에 연결.','분산 생산 출구 → 보호된 넓은 왕 route. 먼 packet을 왕이 찾으러 가기보다 살아 있는 feeder가 local slot까지 이동. first drop 1–3칸, 단일 패킷 직렬 회수.','r350–400 근처 드롭 0인 정체를 줄인다. 보호되지 않은 교차로에서 긴 몸을 풀지 않는다. ACK 후 death 확인, near packet의 아군 선점 제한.','같은 32드롭 ×60–75% → **19–24**. v1 7.67, 엘리트 37.63; 현재 생성 45.33/게임. 부족한 공급량/생존 경로가 먼저 확보돼야 한다.'],
 ['Schooltime a / 엘리트 승 1,055, v1 8, 최근 stack11 8','r250 분산 생산대의 작은 조각 → 지역 relay; r350 후보 왕, r400–450 선택 relay → 왕. fountain pocket 집결 가정은 쓰지 않는다.','생산대에 relay anchor를 여러 개 두고 왕은 가까운 준비 packet 사이의 넓은 안전 경로를 걷는다. remote donor를 r250부터 왕에게 장거리 이동시키지 않는다.','분산 자연 수확량을 보존하고 왕 split 손실 제한. 학교 통로의 병목/적 접근은 파수 최신성으로 승인. 긴 footprint 회수 중 다른 아군이 가로채지 않도록 lease.','8×L3(16)+2×L8(8)=24드롭 ×60–75% → **14–18**. v1 6.13, 엘리트 28.18, 현재 생성 31.63/게임. 생산 감소를 동반하면 예산을 다시 계산.'],
 ['Trauma / 엘리트 승 1,918, v1 17, 최근 stack11 18','r250부터 L3–7 외부 relay bootstrap(8 바닥 제거); pocket 수확의 reversed child를 출구로 내보내 작은 공급을 반복. 준비된 L8–12는 r375–450 왕으로.','긴 왕을 깊은 막다른 pocket 안에 두지 않는다. 출구 바깥 넓은 길에 왕 1–3칸 앞 slot, relay의 몸을 왕 경로에 배치. r475 일괄 사망을 앞당겨 분산.','가까운 머리 존재만으로 feed 처리하지 않는다. 수확 → export → relay 준비량을 먼저 늘리고 파수로 출구 보호. drop footprint가 출구를 막으면 예약 거절.','4×L3(8)+1×L8(4)=12드롭 ×60–75% → **7–9**(재료 증가 조건). 현재 7.06드롭을 유지하면 **4.2–5.3**가 이 회수율의 상한. v1 3.06, 엘리트 19.48; clock만으로 엘리트 절대량을 기대하지 않는다.'],
 ['Autarky / 엘리트 승 928, v1 18, 최근 stack11 18','r250에 이미 큰 v1 왕을 유지. r350–450 요새 생산자/남은 L5–12 → 같은 왕 ID. 모든 guard를 희생시키지 않고 마지막 입구 수비 유지.','요새 안 왕의 기존 넓은 순환/자연 진주 route에 first drop 1–3칸 앞. L8–12 몸을 route와 나란히 정렬. 긴 packet은 마감 여유 10–30턴 확보.','wall/몸통으로 보호되는 lane, 살아 있는 guard의 최신 ingress 정보를 사용. 기존 왕 자연 섭취·생존 우선. SE의 r250 head 파동을 강제하지 않는다.','4×L3(8)+2×L12(12)=20드롭 ×70–90% → **14–18**. v1 14.22, 엘리트 22.02. v1 자연 섭취 21.94/게임, 최종 61.11을 보존하며 평가.']
]);
fs.writeFileSync(path.join(ROOT,'research/observations/conversion-protocol.md'),out.join('\n'));
console.log(JSON.stringify({report:'research/observations/conversion-protocol.md',bytes:Buffer.byteLength(out.join('\n')),tableGroups:Object.keys(T.groups).length,deepN:D.length}));
