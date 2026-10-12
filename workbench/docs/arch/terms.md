# 점수 항과 정적 크기: v1.3

기본 파일 경로는 `versions/v1.3/bot/`다. `v1.4/...`만 `versions/v1.4/bot/...`다. 아래 수치는 **공식에 값을 넣은 정적 계산**이며 관측 평균·기보 측정값이 아니다. 예시의 거리·길이·진주 확률을 함께 적었다. 코드의 진주 즉시 값은 `+p`, 확실한 진주는 **+1**이다. README의 “인접 진주 +50”은 개발 절차 예시이며 이 봇의 계수가 아니다(`plan.cpp:1599`, `params.hpp:8`, `docs/arch/README.md:26`).

## 점수 층과 적용 행

- `base`: 이번 action의 즉시 food/threat/portal/cost. `safety`: candidate 마지막 칸에서 한 번 flood fill. `cont`: 이후 한 걸음 DFS의 누적 값과 terminal leaf. `value=base+safety+cont`, trade/blind에는 cont 없음(`plan.cpp:1599`, `plan.cpp:1789`, `plan.cpp:1816`, `plan.cpp:1821`).
- DFS step의 할인 `g=GAMMA^(turns+1)`; terminal attract/explore/frontier도 `g`를 곱한다. goal penalty, kx penalty, 자유 출구 보너스는 **leaf에서 할인하지 않는다**(`plan.cpp:532`, `plan.cpp:536`, `plan.cpp:537`, `plan.cpp:564`).
- F0=MODE0 기본 FORTRESS(unknown/PD b/PD undecided), W=MODE1 Autarky/PD a, S=MODE2 SWARM 7가족, PT=MODE3 Portals. 정책 상세는 `policy.hpp:64`, `policy.hpp:130`, 인스턴스는 `plan.cpp:1302`다.
- S의 최종 `cv=value-kingFloorCost(end)`; v1.4 S는 추가로 `cv-=OP_STEP*clamp(opDist[end]-opDist[head],-1,1)`다. doom과 printed `v`는 raw value를 읽는다(`plan.cpp:1850`, `plan.cpp:1873`, `plan.cpp:2031`, `v1.4/plan.cpp:1843`).

예시에서 별도로 적지 않은 attraction은 wait≤distance, 추가 경합 없음으로 계산했다. 표의 “±”는 어느 차이를 측정하는지에 따라 다름을 뜻한다. 매개변수 셀의 숫자도 해당 줄에 있는 선언값이다. trade 공식의 enemyLen은 `max(minLen,2)`인 증명된 길이다. threat reach는 TG가 unseen floor5/옆 진주를 보충한 별도 길이이며, 둘을 같은 추정치로 대입하면 안 된다(`plan.cpp:102`, `plan.cpp:741`). `areaSafety`와 `threatCore`는 가상 길이 lenNow 대신 그 차례 `w_.myLen`을 사용한다(`plan.cpp:482`, `plan.cpp:217`).

## food: 즉시 섭취와 attraction source

| name / file:line / formula | parameters와 값 | 부호 | 적용 engine/rows | static scale estimate |
|---|---|---|---|---|
| `pearlValue`, `plan.cpp:1599`, `plan.cpp:565`: step `+pearlValue(t,p)`; future step `+p*g` | `p=pearlProb`; `GAMMA=.88` (`params.hpp:8`, `world.cpp:425`) | + | 모두; gh로 감소 가능 | 확실한 첫 진주 +1; 한 턴 뒤 +.88; 3턴 뒤 +.6815 |
| seen pearl survival, `world.cpp:437`, `world.cpp:441`: `p=.985^(r-pearlSeen)` | `PEARL_DECAY=.985` (`params.hpp:10`) | +의 입력 | 모두 | 10라운드 된 진주 p=.8597; 20라운드 .7391 |
| predicted spawn, `world.cpp:443`, `plan.cpp:563`: 확률 `.75*.985^age`; DFS `p<.05`이고 calendar가 arrival까지면 p=.75 | `SPAWN_CONF=.75`; fountain은 q≥.7 (`params.hpp:11`, `world.cpp:444`) | +의 입력 | 모두 | 예측 직후 +.75; fountain 오래됨 p 최소 .7(다른 p보다 큰 쪽) |
| unseen/mirror probability, `world.cpp:428`, `world.cpp:448`: prior 또는 mirror p×.8 | prior 초기 .05; 관측≥30 후 `(firstPearls+1)/(observed+20)` clamp .01..3 (`params.hpp:12`, `params.hpp:13`, `world.cpp:164`) | +의 입력 | 모두 | unknown tile 초기 +.05; mirror predicted spawn .75×.8=.6; mirror never-spawn은 0 |
| ordinary source, `plan.cpp:341`, `plan.cpp:428`: `s.v=p` if p≥.15; attraction `Σ v*.88^d*.97^max(0,wait-d)*contest` | `GAMMA=.88`, `GAMMA_WAIT=.97`, `ATTRACT_RADIUS=16`, `MAX_SOURCES=20` (`params.hpp:8`, `params.hpp:16`) | + | 모두 | 진주 1개 거리1 source .88; 거리7 .4087; 5개 거리3이면 5×.6815=3.4074(경합 없음, leaf 시간 할인 전) |
| future source, `plan.cpp:342`: `v=.9*SPAWN_CONF=.675`, wait=countdown | horizon120, wait gamma .97 (`params.hpp:9`, `params.hpp:18`) | + | 모두 | 거리3, wait10: .675×.88³×.97⁷=.3717; p≥.15면 이 branch 대신 ordinary p 사용 |
| fountain source floor, `plan.cpp:343`: free fountain `v=max(v,.9)` | `FOUNTAIN_VALUE=.9`; 관측 fountain 정의 samples≥2,maxSample≤12 또는 samples=1,maxSample≤3 (`params.hpp:15`, `world.hpp:168`) | + / max | 모두 | empty fountain 거리3, wait≤3이면 .9×.6815=.6133; 여러 fountain은 합산 |
| grab source, `plan.cpp:349`, `plan.cpp:353`: `v=max(v,1.5*p)`; enemy contest 생략 | `GRAB_VALUE=1.5`, reach6, drop age≤6, last seen gap2 (`params.hpp:196`) | + 강화 | F0/W/PT; S는 core2만; late king r450부터 꺼짐, PT는 재활성 | p=1 거리2:1.5×.7744=1.1616; ordinary .7744보다 .3872 큼. **즉시 pearl +1을 +1.5로 바꾸지 않음** |
| hunting source, `plan.cpp:383`: `v=min(.15*tradeValue,3)` | HUNT_MAX_LEN5, units≥2; W_KILL4 (`params.hpp:85`, `params.hpp:88`) | + | 모두 | tradeValue24이면 source cap3; 거리3이면 2.0444; L>5이면 source 없음 |
| ally hotspot source, `plan.cpp:386`: `v=.4` | msg age≤30, 고정 .4 (`plan.cpp:386`) | + | F0/W/PT; S claimSonar clears hotT | 거리3 .4×.6815=.2726; 거리7 .1635 |
| enemy contest, `plan.cpp:420`: source distance d에 `ef<d-1→.15`, `ef=d-1→.3`, `ef=d→.9`, 그 외1 | `CONTEST_ENEMY_CLOSER=.15`, `ONE_CLOSER=.3`, `EQUAL=.9` (`params.hpp:19`) | + 축소 | 모두; grab은 생략 | ordinary 거리3 .6815 → .1022 / .2044 / .6133 / .6815 |
| ally contest, `plan.cpp:427`: `af<d` 또는 `s.gh`이면 위 contest에 ×.15 | `CONTEST_ALLY_CLOSER=.15` (`params.hpp:20`) | + 축소 | 모두; cl의 af 변경·gh 적용 차이 | enemy closer도 겹치면 .15×.15=.0225; 거리3 한 진주 .0153 |
| cl source boost / sibling priority, `plan.cpp:409`, `plan.cpp:413`: `v=max(v,1.3*p)`; af를 sibling(≤4) 최단 Manhattan으로 교체 | `CLAIM_VALUE=1.3`, L≤4, reach6, TTL8, seen≤2 (`params.hpp:438`) | + 강화 / 양보 취소 | F0/PT/S, W는 K 제외 | p=1 거리3 .886; 긴 아군만 더 가까워도 .15 할인이 없어질 수 있음; source 강화 자체 +.2044 |
| ce floor, `plan.cpp:415`, `plan.cpp:426`: claimed + ef≥headDist−1이면 contest≥.9 | `CLAIM_ENEMY_ON=false`, `CONTEST_EQUAL=.9` (`params.hpp:439`, `params.hpp:19`) | + 강화 | 현재 전부 inactive | 켰을 때 거리3 enemy 1 closer .2044→.6133; +.4089 |
| cov floor, `plan.cpp:356`, `plan.cpp:425`: p<.15 spawn/fountain source contest≥.6 | `COV_ON=true`, maxL4, `COV_CONTEST=.6` (`params.hpp:329`); S own-side/core2 | + 강화 | F0/PT/S; W K 제외 | empty fountain 거리3 enemy closer:.9×.6815×.15=.092→×.6=.368; ally .15 할인은 여전히 적용 |
| gh drop ceding, `plan.cpp:351`, `plan.cpp:427`, `plan.cpp:1219`: grab 취소; attract contest×.15; **즉시/DFS pearlValue도 p×.15** | `GH_ON=true`, dropStart300, recipient R2, fresh drop6 (`params.hpp:568`, `params.hpp:570`) | + 축소 | F0/W/PT; S ghOn=false | 확실한 첫 drop +1→+.15. 거리3 source .6815→.1022; 큰 아군 곁 drop로 grab boost 없음 |

source trimming은 현재 head로부터의 할인값으로 상위20만 남긴다. grab/fountain floor는 trimming 전, cl boost와 contest는 trimming 후 적용한다. leaf의 `attract_[t]`는 source 총합이므로 “goal 0.4가 진주 1보다 작다”만으로 전체 경쟁을 설명할 수 없다(`plan.cpp:343`, `plan.cpp:353`, `plan.cpp:387`, `plan.cpp:409`, `plan.cpp:428`). DFS는 가상 섭취한 tile의 `SC.pnow`나 source를 삭제하지 않는다. 미래 각 step에도 현재 SC.pnow를 재사용하며, p<.05일 때 arrival까지 spawn이 예정된 경우만 .75로 보충한다. 재방문은 path로 막지만 terminal field에는 앞서 먹은 source가 남을 수 있다(`plan.cpp:472`, `plan.cpp:561`, `plan.cpp:563`, `plan.cpp:532`).

## goal와 탐색 leaf

| name / file:line / formula | parameters와 값 | 부호 | 적용 engine/rows | static scale estimate |
|---|---|---|---|---|
| F/sd/harvest approach pull, `plan.cpp:537`: `-W*max(0,min(goalDist,200)-2)` | `FG_HOLD=2`, `FG_W=.12` F/PT (`params.hpp:320`); `FG_W_FRONT=.4` S (`params.hpp:713`) | − 거리 | F0/PT F, S sd/HV 접근; W는 F 없음 | leaf d7: F −.6, S −2.0; d10: S −3.2; **한 칸 진전 차이는 .12/.4**, hold zone 안은 0 |
| gathering pull, `plan.cpp:538`: GH true면 `-.12*max(0,min(d,200)-3)`; false면 `-.12*min(d,200)` | GATHER_W .12, GH_HOLD3; GH true (`params.hpp:130`, `params.hpp:568`) | − 거리 | F0/W/PT; S 중앙 gathering 없음 | d7 −.48, d10 −.84; 한 칸 차 .12 |
| PT end gathering, `plan.cpp:592`: r≥430이면 위 weight .4(GH true branch) | PT_ENDGAME_ROUND430 / PT_END_GATHER_W .4 (`params.hpp:727`, `params.hpp:753`) | − 거리 | PT | d7 −1.6; d10 −2.8; `PT_ENDGAME_ON` 자체와 독립인 식 |
| exploration, `plan.cpp:234`, `plan.cpp:532`: `(unseen + staleRevealSum)*.35*prior*4*g` | EXPLORE_W .35, stale>60 후 `(age-60)/200` clamp1 (`params.hpp:21`) | + | 모두 leaf | 49칸 unseen, prior .05:3.43×g; depth3 leaf g=.88⁴=.5997 →2.057; prior .01이면 .4114 |
| free exits, `plan.cpp:534`, `plan.cpp:536`: `+.15*freeN` | nonreverse reachable next directions, literal .15 | + | 모두 leaf | freeN1/2/3 →+.15/.30/.45, 시간 할인 없음 |
| no-exit leaf, `plan.cpp:541`: `DEATH*.5*.88^turns` | DEATH=−1000 (`plan.cpp:24`) | − | 모두 leaf | depth3: −500×.88³=−340.736; depth7 −204.338 |
| no continuation, `plan.cpp:574`: `DEATH*.88^turns` | DEATH=−1000 | − | 모두 DFS | turns0 −1000; turns3 −681.472 |
| invalid candidate initial value, `plan.cpp:1806`: `DEATH*2` | −2000 | − sentinel | 모두; illegal candidate는 best 비교 제외 | −2000이며 합산 항이 아니라 미선택 sentinel |
| deterministic JITTER, `plan.cpp:1843`: `+.002*((mix32(id*7919+r*131+i*17+3)&1023)/1023)` | JITTER .002 (`params.hpp:589`) | + | 모든 legal candidate | 0..+.002; 일반 진주/goal보다 2–500배 작음; exact tie는 앞 candidate |

leaf goal penalty는 현재 head에서 target까지의 거리가 아니라 **탐색 끝 위치의 거리**다. 예컨대 현재 d7라도 모든 첫 수가 depth3..7 내 hold zone에 닿으면 goal 항 차이가 0일 수 있다. v1.4 문서에 이 실패가 기록되어 있다(`plan.cpp:537`, `versions/v1.4/VERSION.md:95`).

## safety / threat / portal

| name / file:line / formula | parameters와 값 | 부호 | 적용 engine/rows | static scale estimate |
|---|---|---|---|---|
| near threat, `plan.cpp:216`: `T[d]*badForThem*pseudo*king*endgame`; future step에 ×g | T1=30,T2=24,T3=15,T4=9; disadvantage .45(d1)/.2(d≥2), pseudo .5, king1.5, late ahead2 (`params.hpp:64`) | − | 모두; TG_ON=true | favorable enemy trade d1 −30, d2 −24; unfavorable d1 −13.5, d2 −4.8; king d1 −45; late ahead king −90 |
| ks2 long threat, `plan.cpp:198`: d5/6/7의 T×king1.5 | KS2_ON=false, T5/6/7=7/5/3, reach7 (`params.hpp:209`) | − | 현재 inactive | 켰을 때 king d5 −10.5,d6 −7.5,d7 −4.5; ENDGAME_THREAT_MULT는 이 함수에서 없음 |
| predicted head path, `plan.cpp:171`: softPenalty=max(old,1.5×{1,.6,.3}) | HEAD_PATH_PENALTY1.5, first3 tiles (`params.hpp:36`) | − | 모두 | 1/2/3칸 −1.5/−.9/−.45; 여러 머리가 같은 칸을 예측해도 합산 아님 |
| enemy echo line, `plan.cpp:179`: softPenalty=max(old,1.2×ageFactor×(1-.1*k)) | ECHO_LINE_RANGE6, fresh factor1 또는 .6 (`params.hpp:73`) | − | 모두 | fresh k1 −1.08,k6 −.48; aged k1 −.648; head-path와 max |
| next spawn block, `plan.cpp:1600`, `plan.cpp:567`: p<.5이고 spawn=arrival+1이면 −.5(DFS ×g) | BLOCK_SPAWN_PENALTY .5 (`params.hpp:22`) | − | 모두; regular 2-step 식에는 이 항 없음 | 첫 칸 −.5; future1 −.44 |
| sc body spawn block, `plan.cpp:2597`: own/neutral/**unknown-side** spawn r+2..r+min(L,8)일 때 softPenalty+=.5 | cfg.spawnClear=true S; SC_WIN8, head Manhattan R=DFS_DEPTH_MAX+2=9 (`params.hpp:665`, `policy.hpp:151`, `plan.cpp:2589`) | − | S만 | .5; head-path1.5와 겹치면 합2.0; enemy side=2만 제외하므로 unknown side도 가격 부과 |
| unknown edge, `plan.cpp:1599`, `plan.cpp:566`: −.3(DFS ×g) | UNKNOWN_EDGE_PENALTY .3 (`params.hpp:588`) | − | 모두 | 첫 crossing −.3; future1 −.264 |
| known portal stale / near head, `plan.cpp:251`: clean same-head probe면0; unseen exit `.5+1*min(age/20,1)+8*nearHead` | PORTAL_BLIND .5, STALE1, HEAD_NEAR8 (`params.hpp:39`) | − | 모두 | age10 −1; never seen −1.5; near head 추가하면 −9.5 |
| first portal extra, `plan.cpp:1583`: no probe→−4, dirty→−8, clean→0 | PORTAL_UNPROBED4 / DIRTY8 (`params.hpp:59`) | − | 모두 | unknown age + unprobed 합−5.5; dirty+near head 합−17.5; base portalPenalty와 **별개 합산** |
| px crowd/long override, `plan.cpp:272`, `plan.cpp:1588`: unseen fresh ally near exit 추가8(nearHead 중복 면제); long/r300 unprobed extra를8로 교체 | PX_ON=false; allyAge20,dist6,longL15 (`params.hpp:246`) | − / overwrite | 현재 inactive | 켰을 때 crowd8 추가; unprobed4→8은 추가4, 추가8이 아님 |
| px2 ally dirty override, `plan.cpp:1591`: portalExtra=max(extra,30) | PX2_ON=false, PX2_ALLY_PENALTY30 (`params.hpp:452`) | − / max | 현재 inactive | dirty8→30은 추가22; 기본 portalPenalty는 따로 남음 |
| area trap, `plan.cpp:512`: `-60*(1+.1*(L+2-count))` if count<L+2 | AREA_TRAP60 / MARGIN2 (`params.hpp:25`) | − | 모두; HV script는 탐색 안 함 | L8,count8 →−72; count5→−90 |
| area dead end / room, `plan.cpp:513`: count<cap에서 cycle0 AND roundsLeft>count이면−8*KS multiplier, 그 외−.5 | DEADEND8, ROOM.5; KS_ON=false, KS_DEADEND_MULT2 (`params.hpp:30`, `params.hpp:158`) | − | 모두 | 나무 지역 −8; 순환 room −.5; game가 region보다 빨리 끝나도 room branch −.5 |
| area fill shortage, `plan.cpp:516`: `-3*max(0,int(1.5*L)+4-count)` when count<cap | FILL3,ratio1.5,margin4 (`params.hpp:32`) | − | 모두 | L8,count10:over6 →−18; count16이면0 |
| area size bonus, `plan.cpp:519`: `+.04*min(count,cap)`; cap=max(2L+16,96) | AREA_BONUS.04,CAP_EXTRA16,CAP_MIN96 (`params.hpp:27`) | + | 모두 | L8 열린 cap96 →+3.84; L50 cap116 →+4.64; count10 →+.4 |
| tail reachable bonus, `plan.cpp:520`: tailReached→+1.5 | TAIL_REACH_BONUS1.5 (`params.hpp:35`) | + | 모두 | +1.5 once; 이동 후보 마지막 칸의 flood 결과 |
| blind candidate safety reference, `plan.cpp:1793`: safety=max ordinary safety; ordinary 없으면0 | 위 area 공식 | ± overwrite | 모두 blind candidate | 열린 ordinary가 +3.84면 blind도+3.84; 실제 exit flood 검사 아님 |
| unknown portal opportunity, `plan.cpp:294`: `frontierBase=4*(.25+.75*hunger)*timeF*unseenF` | hunger clamp((r-lastAte)/25),time clamp((left-30)/120),unseen min(1,2.5*share) (`params.hpp:46`) | + | 모두 | early hungry unseen≥40% →4; 막 먹음→1; r450 time1/6 →.667/.167 |
| frontier leaf field, `plan.cpp:455`, `plan.cpp:533`: `max(frontierBase*.88^d*allyFactor)*g` | nearest4 frontiers, radius16, ally closer .15 (`params.hpp:51`, `params.hpp:20`) | + | 모두 | hungry base4 거리3 →2.7259, depth3 leaf에서1.6347; frontier끼리 합산 안 함 |
| blind entry risk, `plan.cpp:322`, `plan.cpp:1568`, `plan.cpp:552`: `frontierValue-(.8+.05*L)`; DFS ×g | BLIND_RISK .8/PER_LEN .05, fv eligibility L≥3 (`params.hpp:53`) | ± | 모두 unknown portal | L4 fv4 →+3.0; L20→+2.2; L2 fv0이면−.9 |
| blind desperate price, `plan.cpp:1569`, `plan.cpp:1570`: voluntary가 아니면−25 | clean same-head probe + !late + !kingSafe + fv>0 필요; BLIND_DESPERATE25 (`params.hpp:57`) | − | 모두 첫 blind candidate | L4 fv4 dirty이면3−25=−22; 합 safety 별도 |
| blind commitment override, `plan.cpp:1837`: `value=max(old,bestOrd+blindBase-.5)` | FRONTIER_COMMIT_MARGIN .5 (`params.hpp:52`) | + / max | 모두 voluntary blind | L4 hungry clean base3이면 bestOrd보다 최소+2.5; PT의 blindBase에 module 벌점도 포함 |

공통 2-step sprint는 `p1+p2-1.6-threat(end)-soft(end)-portal1-portal2-extra-unknownEdge2`로 **single base를 그대로 더하지 않는다**. 따라서 single의 첫-step threat/soft/unknownEdge/next-spawn 가격이 같은 방식으로 누적되지 않는다(`plan.cpp:1625`). escape2/3도 별도 식이며 마지막-step soft/portal/unknown만 읽는다(`plan.cpp:1711`, `plan.cpp:1725`). 위협이 큰 첫 칸을 지나도 끝 칸이 안전하면 escape가 경쟁하는 이유다(`plan.cpp:1619`, `plan.cpp:1719`).

## splitting / conversion / combat

| name / file:line / formula | parameters와 값 | 부호 | 적용 engine/rows | static scale estimate |
|---|---|---|---|---|
| sprint movement cost, `plan.cpp:1625`, `plan.cpp:1725`: `-1.6*(steps-1)` | SPRINT_COST1.6 (`params.hpp:587`) | − | 모두 2/3-step/strike | 2-step−1.6,3-step−3.2,4-step−4.8; 두 진주 확정 2-step food+2−1.6=+.4, threat 등 별도 |
| trade up, `plan.cpp:745`: `4*(enemyLen-ownLen)` if diff≥3 AND ratio≥2 | W_KILL4,KILL_MIN_DIFF3,KILL_MIN_RATIO2 (`params.hpp:85`) | + terminal | 모두; units≥2, king L≥6는 기본 trade 금지 | L3 vs L6→+12; L4 vs L10→+24; trade에 area/DFS 없음 |
| remove leader, `plan.cpp:746`: max(previous, `4*(enemyLen-ownLen+2)`) if enemyLen>teamLongest | W_KILL4; fresh teamLongest (`world.cpp:451`) | + / max | 모두 | L4, enemy10, teamLongest8 →+32; 위 trade24에 더해서56이 아님 |
| late trade, `plan.cpp:747`: r≥495 AND enemy longer이면 max(prev,4*diff) | ENDGAME_ANY_TRADE_ROUND495 (`params.hpp:92`) | + / max | 모두 nonking | L4 vs L5→+4, 기본 diff/ratio gate 우회 |
| escort trade, `plan.cpp:749`: base≤0, enemy≥L−1, units≥3; allyL≥2L+4, near enemy≤4이면 max(v,.08*allyL) | W_ESCORT .08 (`params.hpp:90`) | + / max | 모두 | L3,allyL12→+.96; 여러 protector 길이 값 max |
| smallRam / lntRam override, `plan.cpp:641`, `plan.cpp:646`: max(base,12+4*(enemyLen-L)) | RAM_SMALL_VALUE12; RAM_SMALL_ON=false; LNT_RAM_ON=false (`params.hpp:147`, `params.hpp:154`, `params.hpp:514`) | + / max | 현재 inactive | 켰을 때 L4 vs L4→12; 이후 lnt veto가 0으로 만들 수 있음(lntRam 자체 true면 veto else 생략) |
| lntVeto, `plan.cpp:647`: positive trade→0 if disadvantage AND no kint | LNT_ON true; d3≤−1 F/PT/Slithery, d8≤−3 other S; kint enemy≥8, NEED_LONGEST=false; r<495 (`params.hpp:511`) | 제거 | 모두 | +24 trade가 legal=false(첫-step에서는 base DEATH=-1000)로 탈락; 단순 −24 감점 아님 |
| strike terminal, `plan.cpp:1767`: `tradeValue-(steps-1)*1.6` | STRIKE_MAX_STEPS4 (`params.hpp:91`) | +− | 모두 !late | tv24,4-step →19.2; 경로 진주/중간 threat/area/DFS 안 더함 |
| policy / sx / sr / HV / escape split, `plan.cpp:1987`, `plan.cpp:2530`: **additive split reward가 없다**; rule true+urgency면 선택 move를 SPLIT으로 교체 | caps/clocks/child-room은 [flow-swarm.md](flow-swarm.md), [flow-fortress.md](flow-fortress.md) | override | 모두; HV S only | 점수 크기 추정 대상 아님. urgency immediate p≥.5면 일반 split 전체 차단 (`plan.cpp:1993`); HV split은 별도 RETURN (`plan.cpp:2530`) |
| conversion sf / conv / gathering feed, `plan.cpp:1443`, `plan.cpp:1478`, `plan.cpp:1547`: **conversion reward가 없다**; gates로 neck MOVE 조기 반환 | CONV_MIN_UNITS3; SF_QUEUE_MAX2; clocks policy250..400, F300/340, late430 (`params.hpp:143`, `params.hpp:674`, `policy.hpp:75`) | override | sf S, conv/feed F0/W/PT | move 점수와 비교하지 않음 (`plan.cpp:1443`, `plan.cpp:1478`, `plan.cpp:1547`) |

`W_HUNT=.6`는 선언만 있고 실제 hunting source는 literal `.15`를 쓴다(`params.hpp:89`, `plan.cpp:383`). `CONV_START`와 같은 이름을 sf에서 읽는다고 가정하면 안 된다. sf main clock는 `cfg.convStart`, policy의 map row 값이다(`plan.cpp:1403`, `policy.hpp:150`).

## king / module-specific와 목표 후보 순위

| name / file:line / formula | parameters와 값 | 부호 | 적용 engine/rows | static scale estimate |
|---|---|---|---|---|
| kx leaf distance, `plan.cpp:540`: `-.4*max(0,7-kxDist[leaf])` | KX_ON true, r≥300, L≥8, kingFresh, KX_STALE3; map gate Schooltime/SF/Trauma/Autarky (`params.hpp:572`, `plan.cpp:1235`) | − | F0/W/PT 함수 존재; 현재 실제 정책에서는 Autarky W만 family gate 충족. S kxOff, PT map false | d3 −1.6,d6 −.4,d7→0; 미래 거리의 한 칸 차 .4 |
| king floor choice, `plan.cpp:2423`: d≤3 cost=20+10*(3-d); 3<d<6 cost=1*(6-d); 그 외0 | cfg.kingFloor true S, kingClass, enemy news≤3; KF values (`params.hpp:695`, `policy.hpp:153`) | − choice only | S | end d0/1/2/3/4/5/6:−50/−40/−30/−20/−2/−1/0. d3→d4 개선 **18**로 leaf pull .4보다 큼 |
| PT king DEAD, `ptmod.cpp:40`, `ptmod.cpp:56`, `plan.cpp:624`: first/each candidate step −40; DFS −40*g | PT_KING_SAFE_ON true / PT_KING_DEAD_PEN40 (`params.hpp:734`) | − | PT king L≥8 | first DEAD−40; future1−35.2; blind unknown uses static ptExit (`plan.cpp:607`) |
| PT pocket all-dragons, `ptmod.cpp:77`, `plan.cpp:625`: every action step −40; DFS −40*g | PT2_POCKET_ON true / PEN40 (`params.hpp:758`) | − | PT, all lengths | first pocket−40; king DEAD+POCKET−80; future1 overlap−70.4; HV script와 별도 |
| PT king unprobed crossing, `ptmod.cpp:58`: portal unseen AND head outside ROOM AND not clean same-head probe →−12 | PT_KING_BLIND_PEN12 (`params.hpp:736`) | − | PT king; candidate steps only | extra−12 + common unprobed4 + stale1.5 =−17.5 before DEAD/POCKET; DFS에는 crossing 추가 벌점 없음 |
| PT piece near king exit, `ptmod.cpp:62`, `ptmod.cpp:70`: unseen portal exit distance≤2+newsAge from longer king≥8 →−12 | PT_PIECE_PORTAL_ON true; news≤3, distance2, PEN12 (`params.hpp:739`) | − | PT nonking candidate steps only | king age2이면 radius4; hit→−12; ordinary portal costs 별도 |
| sd target group value, `plan.cpp:2323`: `sum core2 flow in Manhattan3/(1+fresh heads within3+claims within3)` | FG_GROUP_DIST3,GUARD3,SD_MIN_FLOW .004; mean gaps mapSpawnGap (`params.hpp:317`, `params.hpp:662`) | + ranking | S before max(convStart,430) | mean gap2 fountain3개 yield1.5; assigned2→.5. gap250 1개 alone .004(허용), assigned1→.002(배제). **move value에 더하지 않음** |
| frontier target deficit, `plan.cpp:2298`, `plan.cpp:2347`: positive `share*.01*(known+1)-have` first, then groupValue, then distance | cfg.frontShare r25/50/100/250 interpolation (`engcfg.hpp:39`, `policy.hpp:103`) | + lexicographic ranking | S FRONT_POLICY 모든 current row; side known 필요 | Schooltime a r100 bin2 share70%, known9/have4 →deficit3.0. 열세 veto면 deficit가 아무리 커도 후보 배제 |
| HV pocket ranking, `plan.cpp:2459`, `plan.cpp:2469`: count(p arrival≥.5), max food then min ETA | HV_MIN_FOOD2; ETA+depth+6 deadline (`params.hpp:771`, `params.hpp:774`) | + ranking | S Trauma/SF | 예상 food4는 food3보다 ETA가 길어도 먼저; all gates 통과 필요; **move bonus 없음** |
| HV food / depth selection, `plan.cpp:2511`, `plan.cpp:2548`: first BFS food; 없으면 deepest legal pocket step | food p≥.5, BFS depth cap16, HV_TRIGGER2 (`params.hpp:772`) | priority | S HV script | 일반 +1 대 −60 등의 비교를 생략하므로 deadend penalty로 꺾이지 않음 |
| v1.4 opening leaf, `v1.4/plan.cpp:538`: `-1.0*max(0,min(opDist,200)-0)`; opLeaf=true가 sd/gather term 생략 | OPENING_ON true, OP_W1/OP_HOLD0 (`v1.4/params.hpp:761`) | − distance / overwrite | v1.4 S scripted roles only; v1.3 absent | leaf d7→−7, 한 칸 진전 +1; 모든 후보가 waypoint 도달하면 차0 |
| v1.4 opening progress choice, `v1.4/plan.cpp:1843`: `-2*clamp(dEnd-dHead,-1,1)` | OP_STEP2 (`v1.4/params.hpp:764`) | ± choice only | v1.4 S opPull | closer+2,farther−2,unchanged0; 2칸 sprint closer도+2; 앞/뒤 후보 간 차4; raw doom/indicator 제외 |
| v1.4 hold group ranking, `v1.4/opmod.cpp:189`, `v1.4/opmod.cpp:206`: bin2 group yield/(1+assigned), sticky then max value/min distance | OP_HOLD_ON=false, ALL=false, END100; same sd .004 cutoff (`v1.4/params.hpp:774`) | + ranking / overwrite | 현재 v1.4 inactive; v1.3 absent | 활성화하면 enemy ETA와 ownership gate 대신 veto로 filter; move pull은 FG_W_FRONT .4 그대로 |

## 비교할 때 필요한 계산

위험이 없는 열린 지도에서 L8의 area 크기 보너스는 최대+3.84이고(tail 보너스 +1.5 별도), depth4에서 확실한 미래 진주 네 개를 먹는다면 step 합은 `.88+.88²+.88³+.88⁴=2.9356`이다. terminal source는 여기에 또 더해질 수 있다. 현재 진주 +1, source 여러 개의 합, leaf 목표 거리 차 .4, candidate 공간 차+1.5, 작은 threat조차−4.8은 서로 다른 층에서 경쟁한다(`plan.cpp:519`, `plan.cpp:565`, `plan.cpp:532`, `plan.cpp:537`, `plan.cpp:520`, `plan.cpp:224`).

trap 예: L8,count8,cycles0,roundsLeft>8,tail not reached이면 `−72−8−24+.32=−103.68`이다. 이것은 static area 하나이며 DFS death가 겹치면 훨씬 나빠진다. 반대로 적 인접 칸 −30이어도 나머지 후보가 trap/death라면 그 칸이 최선일 수 있다. “T1이 없어서 박혔다”와 “T1이 있어도 다른 수가 더 나빴다”를 분리해야 한다(`plan.cpp:512`, `plan.cpp:514`, `plan.cpp:516`, `plan.cpp:519`, `versions/v1.4/VERSION.md:252`).

### 위협 세기를 바꿀 때 (v1.7 W7a, 2026-10-01 17:05, `versions/v1.7/VERSION.md` 6.2·8.1)
- **정적 위협은 DFS의 모든 걸음에 다시 더해진다.**
  - 후보 값 = 첫걸음 `c.base`(−T) + 지역 안전 + 탐색 연속값이다. 연속값은 걸음마다 −T×g를 다시 더한다.
  - 그래서 위협을 판 전체에서 똑같이 키우면 모든 후보의 미래 걸음도 같이 무거워진다. 순위가 거의 바뀌지 않는다.
  - 예: W7a는 작은 판에서 "그들에게 나쁜 교환" 할인을 껐다. 안전한 대안이 있는데 적 도달 칸으로 간 이동이 1.4% → 1.4%로 그대로였다.
- **순위를 바꾸는 것은 첫걸음 항뿐이다.** W7a′는 첫걸음 끝 칸만 할인 없이 3배로 매겼고, 그 몫이 1.4% → 1.1%가 됐다.
  - 진단 빌드에서 첫걸음 위협 차이(예: 30 대 9)가 연속값 차이(약 27)에 지던 사례가 뒤집혔다.
  - 그래도 대안이 막다른 곳(s −93 ~ −113)이거나, 봇의 도달 추정이 실제보다 넓어 대안도 위협받는 경우는 남았다.
- **위협 세기를 고칠 때는 첫걸음 항과 탐색 항을 따로 다룬다.** 그리고 진단 빌드(`exp/w7/mkbuilds.py`의 `*-diag`: 후보마다 b/s/c/t를 지시 문자열에 씀)로 순위가 실제로 뒤집히는지 먼저 본다.

## 교차 확인 범위

`base`의 모든 대입/증감(`plan.cpp:1568`, `plan.cpp:1576`, `plan.cpp:1599`, `plan.cpp:1613`, `plan.cpp:1625`, `plan.cpp:1711`, `plan.cpp:1725`, `plan.cpp:1767`, `plan.cpp:1777`), `value/v2/cv`의 갱신(`plan.cpp:1807`, `plan.cpp:1821`, `plan.cpp:1837`, `plan.cpp:1843`, `plan.cpp:1850`), `dfs/dfsPt/areaSafety`의 v 증감(`plan.cpp:481`, `plan.cpp:526`, `plan.cpp:579`), source field 및 target rank(`plan.cpp:327`, `plan.cpp:2248`, `plan.cpp:2434`)를 모두 조회했다. split/feed 조건은 점수 항으로 꾸며 넣지 않았다. disabled 식은 disabled라고 표에 남겼다.

## v1.6 CONV2 항 (`versions/v1.6/bot`, v1.6g)

줄 번호는 `versions/v1.6/bot/`이다(`v1.6/` 표시). 아래 항은 conv2 행(`decideImpl<4>`, `dfs<2, true>`)에서 r ≥ cv2Start(그 행의 전환 시계)부터 쓴다. 요새 후반(`decideImpl<5>`)은 출시 빌드에서 꺼져 있다. 먹이(죽음)는 점수 항이 아니라 조기 RETURN이다(관문은 [flow-swarm.md](flow-swarm.md)의 CONV2 절).

| name / file:line / formula | parameters와 값 | 부호 | 적용 engine/rows | static scale estimate |
|---|---|---|---|---|
| CONV2 당김(잎), `v1.6/plan.cpp:541`: `v -= cvPullW_ * max(0, min(cvDist[t],200) - CV2_HOLD)`; cvDist는 K 머리에서의 BFS(알려진 변, 포털 제외, 몸 무시) | `CV2_PULL_W=.3`(조각·중간), `CV2_PULL_W_BIG=.6`(큰 것 8–12, r400+), `CV2_HOLD=3`; 반경 `CV2_R1/R2/R3=10/16/24`(+소식 나이), 소식 ≤ `CV2_PULL_FRESH=6` (`v1.6/params.hpp:818–821`, `:848`; `v1.6/conv2.cpp:153`, `:171`) | − (leaf, 할인 없음) | S의 conv2 행(v1.6g: 모든 떼 행); 다른 목표가 켜진 차례 제외 | 조각이 K에서 10칸: −.3×7=−2.1. 큰 것: −4.2. 거리 3 진주 다섯(3.4)과 비교하면 조각은 가까운 진주 무리를 먼저 먹고, 큰 것은 무리를 넘어 K로 간다. 위협 인접 −30보다 훨씬 작다 |
| K에게 남기기(gh 경로), `v1.6/conv2.cpp:84–97`, `:100–106`; 값 `v1.6/plan.cpp:1220`: `pearlValue=p*CONTEST_ALLY_CLOSER`; step `softPenalty += CV2_YIELD_PEN`; attraction `grab=false` (`v1.6/plan.cpp:350–351`) | `CV2_YIELD_R=4`(K 머리 맨해튼), `CV2_LEASE=12`라운드 임대, `CV2_YIELD_PEN=.5`, `CONTEST_ALLY_CLOSER=.15` (`v1.6/params.hpp:822`, `:829–830`, `:20`) | − | K가 다른 드래곤인 conv2 프로세스; K 머리 소식 ≤ 1라운드(임대 칸은 소식과 무관) | 남긴 확실한 진주를 밟으면 +1 → +.15−.5 = −.35. 4칸 넘게 뻗은 흔적의 먼 쪽은 남기지 않는다(v1.6h 측정: 당겨진 조각이 grab으로 먹음, VERSION.md §11.3) |
| K 다음 칸, `v1.6/conv2.cpp:108–112`: K 머리 이웃의 빈 칸 `softPenalty += CV2_FRONT_PEN` | `CV2_FRONT_PEN=2.0` (`v1.6/params.hpp:823`) | − | K 머리를 이번 라운드에 본 conv2 프로세스 | 그 칸에 진주가 있어도 +1−2 = −1. 머리 경로 벌점(`HEAD_PATH_PENALTY`)과 max가 아니라 더해진다 |
| 포털 조심, `v1.6/conv2.cpp:115–124`: 우리 머리에서 DFS_DEPTH_MAX+1 안의 포털 출구 중 시야 밖이고 K 머리에서 `CV2_PORTAL_NEAR + 소식 나이` 안인 칸 `softPenalty += CV2_PORTAL_PEN`; 당김 BFS도 포털을 지나지 않음(`v1.6/conv2.cpp:161`) | `CV2_PORTAL_NEAR=2`, `CV2_PORTAL_PEN=12.0` (`v1.6/params.hpp:838–839`) | − | 포털이 있는 지도의 conv2 프로세스(K 소식 ≤ 3라운드) | 건너기로 얻는 진주 1–3보다 훨씬 크다. Portals 모듈의 PT_PIECE_NEAR_KING_PEN 12와 같은 크기다 |
| 늦은 왕 grab, `v1.6/plan.cpp:1329`: conv2 행에서는 `grabOn_ = GRAB_ON`(늦은 왕 제외를 풀어 줌) | `CV2_KING_GRAB=true`, `GRAB_VALUE=1.5`, `GRAB_REACH=6` (`v1.6/params.hpp:831`, `:199–200`) | + | conv2 행의 늦은 왕 | 새 드롭 거리 2: 1.5×.7744 = 1.16(일반 .77보다 .39 큼) |
