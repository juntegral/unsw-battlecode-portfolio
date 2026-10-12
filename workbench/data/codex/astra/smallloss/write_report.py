import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,csv
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parent))
from tabulate import table,loadall
from analyze import HERE
T=json.loads((HERE/'tables.json').read_text());gs=loadall()
alias={'sqheld_open_small_90012':'O','ladder_stripes_1':'S','sqheld_portals_small_90029':'P','sqheld_blobs_small_90028':'B'}
def short(folder):
 m=folder.split('-seed1-side')[0];return alias[m]+folder[-1]
def fmtact(a):return 'split '+str(a[1]) if a[0]==1 else ''.join('NESW'[d] for d in a[1]) if a[0]==0 else str(a)
loss=[]
for x in T['losses']:
 loss.append([x['game'].split('/')[0],short(x['game'].split('/')[1]),x['firstdiv_one5'],x['lastwin']+' r'+str(x['firstdiv_lastwin']),f'#{x["actor"]}: {fmtact(x["lastwin_action"])}→{fmtact(x["action"])}',x['permanent_behind'],x['elimination']])
early=[]
for x in T['early']:
 if x['panel']=='available' and x['side']==0:
  early.append([x['version'],x['games'],x['turns'],f'{x["natural"]}+{x["drops"]}',f'{100*x["all_per_turn"]:.2f}',f'{100*x["natural_per_turn"]:.2f}'])
report='''[M/E] 전멸은 수적 열세에서 교환 손실을 분열로 보충하지 못한 결과다. 확인한 회귀는 여왕 포털 차단과 WAR의 분열 생략이며, open 패배의 단일 원인은 미확정이다.  
[E] 변경안: 확인된 안전한 포털은 여왕에게 허용하고, 즉시 여왕 격살이 불가능하면 WAR가 일반 행동으로 돌아가게 한다. 그 전에는 `QUEEN_WAR=0`.  
[M/E] 확신: 기보 집계는 높음, 두 행동 회귀는 높음, 수정 후 전멸 방지 효과는 미검증.

[M] 39판·11패를 재계산했다. 전부 전멸이며 기존 집계기와 사망·분열·섭취·길이가 일치한다. r은 **0부터**, 표의 좌석은 후보 진영이다. O=`sqheld_open_small_90012`, S=`ladder_stripes_1`, P=`sqheld_portals_small_90029`, B=`sqheld_blobs_small_90028`. 버전 소스·라인은 [증거 색인](evidence.md) 참조. 이하 표 수치는 [M].

'''+table(['버전','판','one5와 첫 갈림','마지막 승리와 첫 갈림','그 행동','영구 수적 열세 r','전멸 r'],loss)+'''

[M] r0–100 실제 드래곤 차례 기준. 일찍 끝난 판은 종료까지이며 WAR에는 P1이 없다. 종료시각도 맞춘 공통 7판에서 자연진주/100차례는 9.57→9.75→8.68→8.77→8.77이다.

'''+table(['버전','판수','차례','자연+드롭 진주','전체/100차례','자연/100차례'],early)+'''

[M] one10 네 패배의 우리 사망 511건 중 들이받기 264, 들이받힘 214, 나머지 33이다. 적 여왕 격살은 **0회**다. L≤4 비여왕의 자연진주/100차례도 one9 8.03→one10 8.10이다. [E] 따라서 “새 버전일수록 짧은 조각이 모두 더 소심해졌다”나 “큰 여왕 사냥 자폭”으로 설명되지 않는다. 사냥 목표 변경의 간접 영향까지 배제한 것은 아니다.

[M/C] O0 r3 #0, O1 r8 #1은 적이 없는 동일 판면에서 이동→L4 분열이다. `QS_KEEP_MIN_UNITS`가 여왕 보유 하한을 풀었다(one5:1151–1154; one8:1862–1866). [E] 이는 확정된 최초 분기지만, 이후 패배까지 해당 스위치 하나가 일으켰다는 증명은 아니다.

'''+table(['카드 [E]','코드 [C]','결정 근거 [M]','반증 기준 [E]'],[
['1. 여왕 포털 금지는 미관측·위험 출구에 한정. 현재 관측된 빈 출구가 몸 전이·적 도달·다음 탈출 검사를 통과하면 이동/탐색 평가에 포함한다.','one5:3182,4155,5877; one10:4154,5147,6948. QUEEN_PORTAL_ALL은 기존 스위치이나 조건 변경 필요.','S0 r5·S1 r7 첫 행동 변경은 최초 적 목격 전. one9→one10 여왕 첫 섭취 r9→39/23, 포털 통과 1/4→0/0. S1 one10 r19에는 빈 포털 출구의 진주를 두고 떠남.','관측된 안전 출구가 전부 금지되는 횟수 0; r20 이전 섭취 회복. 포털 후 갇힘·충돌이 증가하면 기각. S0 one9 여왕은 r14 자충사하므로 무조건 허용 금지.'],
['2. WAR는 이번 차례 적 여왕 격살 경로가 확인될 때만 행동을 덮어쓴다. 그 외에는 정상 섭취·분열·안전 처리. 조건 수정 전 WAR=0.','one5:640 hunt_path 호출 주변; war8 main.cpp:1302,2903,3061,638. war_act가 먼저 반환하며 후처리도 건너뜀.','S1 r45 #6 동일 판면 L4: one10 분열, WAR 북진. WAR는 r44–66 L≥4 차례 21회·분열 0. O0 r67–93 분열 28→1, 들이받힘 11→19. S0 r166 이후에는 적 여왕이 이미 r125에 죽었음.','비격살 상황의 일반 분열 생략 0; 확인된 즉시 격살 기회는 유지. 복원 뒤 조각 사망·미회수 드롭 증가 또는 확정 격살 누락이면 기각.']])+'''

[M/C/E] OLD main은 수적 우위를 유지하며 교환한다. one10 O0/O1의 r0–100 차례는 우리 1478/1548, 상대 2228/2263이다. 상대도 동급 교환을 허용한다(m3base:2677–2730). [E] 여왕 생존·도달 안전만으로 재생산 공백을 막지 못한다.

[M] 각 패배의 10라운드 N/T/Q·양쪽 진주·모든 사망의 길이/직전 행동은 [증거 색인](evidence.md)에 있다. [E] 로그 없는 회피·wait-split 의도, 모든 스위치별 반사실 행동 변경 총수, 단일 스위치 인과, 수정 효과는 확인하지 못했다. 새 경기·네트워크·봇 수정은 수행하지 않았다.
'''
(HERE/'report.md').write_text(report)
now=datetime.now().astimezone().isoformat()
index=f'''[M] 작성 시각: {now}. 전용 폴더 밖 파일은 변경하지 않았다.

[M] 원자료는 `~/meow-redteam/solo/runs/<arm>/<map>-seed1-side<K>/game.replay`, `result.json`, `result.txt`. 매핑은 `sources.json`에 있다. one5/8/9/10의 로컬 main.cpp는 지정 smoke 소스와 바이트 단위로 일치한다. war8은 별도 소스이며 QUEEN_WAR와 사망 신호/탐색 구현이 함께 달라진다. 39판 모두 bot log 이벤트가 0개다.

[M] 실행: `python3 -B data/codex/astra/smallloss/analyze.py`, 이어서 `tabulate.py`, `suspects.py`, `write_report.py`. 기존 replay reader와 o1_scan 집계기를 import한다. 새 게임이나 봇 실행은 하지 않는다. nice -n 10 요청은 환경에서 setpriority 거절되었고 스크립트는 기본 우선순위로 실행됐다.

[M] 라운드는 replay roundStart의 0-based 번호다. “영구 열세”는 그 라운드 말부터 끝까지 우리 수 < 상대 수. 도중 동률이면 더 늦은 시점이다. 최초 분기는 sonar/log/CPU가 아닌 action·tileChange·dragonUpdate·split·death에서 비교한다. 최초 분기 직전 전체 몸/진주 상태가 동일함을 해시로 확인했다. 행동 의도가 아닌 결과 차이의 최초 시점이다. 결과 파일의 a/b 개체수·길이·여왕길이를 재구성과 대조했고, 기존 o1_scan으로 39판의 전체 사망·분열·진주·유료 비용 및 25라운드 스냅샷을 재확인했다.

[M] 파일:

- [검증 및 입력 해시](validation.csv)
- [패배별 첫 분기와 영구 열세](losses.csv)
- [10라운드 집계 CSV](timeline-10.csv)
- [모든 패배의 양쪽 사망 원장](deaths.csv)
- [자연/드롭 섭취·분열·사망 시기별 집계](windows.csv)
- [r0–100 비율 및 공통 표본/동일 시간창 보정](early-rates.csv)
- [L≤4 비여왕 식사·바로 옆 진주 미섭취](short-economy.csv)
- [스위치의 관측 가능한 외부 조건](observable-gates.csv)
- [직전 버전과 최초 분기 원자료](consecutive-divergences.json)
- [WAR 동일 시간창 비교](war-windows.json)
- [버전별 소스 해시 및 모든 상수](sources.json)

[M] 한 판마다 `<version>-<map>-seed1-side<K>.json`에 전체 차례, 양쪽 개체수/총길이/여왕길이, 실제 행동, 몸, 시야 내 머리, 인접 출구, 진주 기원, 실제 유료 손실, 분열 및 사망을 남겼다. `state` 해시는 글로벌 판면의 동일성을 확인하며 숨은 bot memory·sonar 상태가 같음을 보장하지 않는다.

'''
index+='\n'.join(f'- [전체 10라운드 표·개별 사망: {p.stem.removeprefix("timeline-")} ]({p.name})' for p in sorted(HERE.glob('timeline-*.md')))+'\n\n'
index+='''[M] 사망 원장 `activity` 해석: `ram-enemy-queen`은 해당 차례에 적 여왕과 충돌한 행동자, `child-before-first-turn`은 분열 뒤 자기 첫 차례 전에 사망, `after-split`은 마지막 자기 차례가 분열, `wait-split`은 이 중 여왕이다. `wait-split`은 QUEEN_WAIT 분기 실행의 증거가 아니다. `boxed-at-death`는 그 사망 이벤트 시점 빈 즉시 출구 0이다. head-on의 피격자가 먼저 제거되므로 행동자의 출구 수는 직전 차례보다 커질 수 있다. `last_free`를 함께 보존했다. `move/unresolved`에는 일반 이동·회피·진입·추격이 섞여 있고 로그가 없어 분리하지 않았다. 정면충돌 방향(들이받기/들이받힘)과 최종 사인은 확정 가능하다.

[E] 스위치별 “영향받을 수 있는 조건 횟수”와 “스위치가 실제 출력을 바꾼 횟수”는 다르다. 아래 U는 0이 아니라 이 데이터로 총수를 식별할 수 없다는 뜻이다. 첫 분기만 소스의 다른 변경 조건을 제거하여 귀속했고, 그 이후 출력 비교는 서로 달라진 상태를 비교하게 되므로 인과 계수로 세지 않았다.

'''
index+=table(['스위치','확정/관측된 계수 [M]','실제 변경 총수','코드/해석 [C/E]'],[
['QS_KEEP_MIN_UNITS','7개 패배의 마지막 승리 대비 첫 분기: O0 r3 ×4, O1 r8 ×3. 독립 표본 7개가 아닌 공유 계보.','U (확정 최초 분기 7개)','one5 1151–1154, one8 1862–1866, one10 1883–1887. 낮은 수의 L4 여왕에서 보유 3 제한 해제. 일반 분열이 확인되고 적도 없음.'],
['QUEEN_PORTAL_ALL','one9→10 S0 r5, S1 r7 최초 분기 2개. one10 S1 여왕의 포털 인접 차례 3개, 통과 0.','U (최초 분기 2개는 강한 귀속)','one10 5147–5148, 4154, 6948. 미관측만이 아니라 알려진 포털도 평가 제외. S0/S1 최초 적 머리 관측은 이후.'],
['CUT_BODY_LEN / QS_PAY_REACH','one9→10 O0 r39, O1 r101 최초 분기는 여왕. P1 r5 역시 여왕. O0 r39 one9는 1진주, one10은 0.','U (이 묶음 O 최초 분기 2개)','one10 5339–5349, 5389–5398, 3415–3428. O는 포털이 없고 boot는 미발동; 두 상수 개별 분리는 불가. P1은 포털 변경도 함께 후보.'],
['QUEEN_SURE_LEN / STEPS','one10 네 패배에서 적 여왕 격살 0; one8 O0 r104 #36 L4 격살 1.','U','one10 3533–3543, 3593–3638. 적 여왕을 새 타깃으로 삼아 다른 hunt를 밀어내는 부작용은 0격살로 배제 못 함.'],
['QUEEN_BOOT_LEN','one10/war 패배에서 r301 이후 살아 있는 우리 여왕 0; 무행동 사망 0.','U (여왕 분열 제한의 실제 적용은 0)','one10 5180–5181, 6642–6656. QUEEN_GAME_FEED_ROUND=300으로 조기 feeding 가능. 여왕은 모두 그 전에 사망; 마지막 O1 r301 이후 비여왕의 리더 믿음/먹이 자격 변경은 로그 없어 미확인.'],
['SPLIT_PORTAL_OK','one10 S1/P1에서 포털 인접 꼬리 L4 비여왕 분열 r≤100 각각 1회. O 패배는 0.','U','one10 1925–1942. 관측된 분열이 이 분기를 통과했는지 숨은 tail memory 없이 확정 못 함.'],
['SHORT_EVADE','one10 패배의 외부 후보 차례: O0 338, O1 465, S1 154, P1 116.','U','one10 787–865. 길이≤4·비여왕·비분열 이동·시야수 조건만. 공격 플래그/위험지도/대안 점수 제외. 실행 횟수가 아님.'],
['REACH_EATS','진주 및 실제 이동 경로는 차례별 원장에 보존.','U','one10 3425–3480, 5396–5468. 탐색 중 대체 경로·내부 enter_time·적 길이 기억 없어 최종 변경 수 불명.'],
['SMALL_SPRINT_THREAT','one8 O0 최초 분기는 적이 없는 r3 여왕 분열. 이 규칙으로 그 최초 분기를 설명 못 함.','U','one10 3422–3477. 이후 위협장 차이에 의한 변경 수는 로그 없음.'],
['MATE_UNPIN / POCKET_KEEP_OUT / TARGET_REACHABLE','UNPIN 등 이벤트 로그 39판 전체 0.','U','one10 1074–1268 / 668–773 / 3945–4059. 실행/취소된 후보 경로가 없으므로 실제 발동 0이라고 보고하지 않음.'],
['QUEEN_WAR 패키지','one10과 7짝 중 첫 행동 차이 5짝; B0/B1 사건 동일. S1 r45 분열→이동 1회 직접 확인.','U (패키지 최초 분기 5개)','war 1302–1304, 3061–3232 및 638–640. 사망 신호 변경도 포함. 재생산 생략이 코드와 일치하나 내부 war 상태 로그 없음.']])+'\n\n'
index+='''[M/C/E] 결정 근거 장면:

- O0 one8 vs one5 r3 #0: 같은 몸/진주 상태, 수 1:1, L4, 적 시야 0. one8 분열/one5 북진. one9 vs one8 O1 r8 #1: 수 2:3, L4, 적 시야 0, 분열/서진. 이후 영구 열세 O0 r18, O1 one9 r27. 이 시작 변화는 측정되었으나, 전멸의 충분조건이라는 증명은 없다.
- S1 one9 vs one10 r7 #1: 적을 아직 못 본 상태에서 남진/동진. one9는 r9 (10,11)→포털 (11,10)에서 진주를 먹고 r10 한 번 더 먹는다. one10 r19 (13,0)은 보이는 빈 포털 출구 (12,1)에 진주가 있지만 동진; 여왕 첫 섭취 r23. S0도 r5 분기 후 여왕 첫 섭취 r9→39. 반례: S0 one9 여왕은 r14 자충사, one10은 r166까지 생존. 식사 회복만으로 채택할 수 없는 이유다.
- O0 one10 vs one9 r39 #0: 적 #10은 실제 L3·관측 2칸, 머리 (16,2); CUT_BODY_LEN은 이를 최소 4로 취급한다. one9는 (19,2) 진주, one10은 (20,1) 빈칸. O1 r101 #1에서도 관측 1칸인 실제 L2 #43 앞에서 갈린다. P1 r5는 실제/관측 L3인 적 여왕 #0이 시야 경계에 닿아 최소4가 된다. 주의: '전신이 보임'은 원자료의 사실일 뿐 봇은 꼬리 표지가 없어 완전 관측을 확정하지 못한다.
- S1 war r45 #6: 수 1:4, L4, 보이는 적 0, 빈 출구 3. one10은 2+2 분열; war는 북진한다. r45–65에 L≥4인 21차례 동안 분열 0, r66 들이받혀 전멸. 안전 규칙이 너무 많다는 설명과 반대로, war는 기존 분열 및 SHORT_EVADE/UNPIN/POCKET 후처리를 건너뛴다.
- O0 war r67 #23 첫 차이: r66 우리 여왕 사망 뒤 동일 판면에서 남진/북진. r67–93 분열 one10 28/515차례, war 1/236; 피격사 11/19. war는 적 여왕 격살 0, r93 전멸.
- S0 war r166 #66 첫 차이: 실제 양쪽 여왕이 모두 죽은 뒤(상대 r125, 우리 r166) 같은 상태에서 서진/북진. r166–200 one10 분열24/667차례, war4/470; r200 개체수 23:0 대 11:2. war의 내부 적여왕 생사 믿음은 로그가 없어 확인 불가. '실제 적여왕 생존 시에만 영향'이라는 주장에는 반례다.

[M] OLD main 비교: one10 O0/O1 r0–100 차례 1478/1548 대 2228/2263, 자연진주 127/129 대 168/172. 자연진주를 차례로 나누면 우리 8.59/8.33, 상대 7.54/7.60이다. 적이 차례당 더 잘 먹어서가 아니라 더 많은 개체 차례를 확보했다. S1은 208차례·자연11 대 560차례·자연33, P1은 449·26 대 721·47이다. [C] m3base 2677–2730은 로컬 수 우세에서 같거나 긴 상대를 들이받는다. [E] 적의 재생산/출구 점유가 계속되는 동안 소모전을 버틸 개체를 유지해야 하며, 매차례 여왕 안전을 높이는 것만으로 해결되지 않는다.

[M] 짧은 비여왕 r0–100 자연진주/100차례: one5 9.008, one8 8.423, one9 8.032, one10 8.099, war 8.233. 바로 인접한 빈 진주 출구가 있고 이동 행동을 했으나 아무것도 먹지 않은 차례: 115/1124, 128/1169, 172/1086, 158/1062, 136/919. 이것은 안전한 진주를 거부한 횟수가 아니다. 적 도달/다음 탈출 조건이 포함되지 않았으므로 '겁쟁이' 빈도로 해석하지 않는다.

[E] 제한: 표본은 고정 seed1/4지도이고 로그·각 스위치 on/off의 같은 입력 출력이 없다. 실제 스위치별 변경 총수를 요구하는 부분은 현재 자료로 완결할 수 없다. 표의 U를 0 또는 인과 기여도로 읽으면 안 된다. 모델 전체 정책 메모리를 재실행하거나 새 단일 스위치 대조가 필요한데 브리프가 허용한 작업은 기보 읽기와 컴파일 확인뿐이라 수행하지 않았다. 두 카드는 다음 검증 대상으로 제안했으며 구현·컴파일·새 경기·온라인 확인은 없다.
'''
(HERE/'evidence.md').write_text(index)
# The newer brief asks <500; common asks <450. Count only prose, excluding tables.
prose='\n'.join(l for l in report.splitlines() if not l.startswith('|'))
print('report prose whitespace words',len(prose.split()),'tables',sum(l.startswith('|') for l in report.splitlines()))
