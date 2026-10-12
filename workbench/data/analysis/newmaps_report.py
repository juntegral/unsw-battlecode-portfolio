#!/usr/bin/env python3
"""Generate the report, tables and draft cards from the full offline census."""
import json,csv,statistics,collections,datetime
from pathlib import Path
O=Path(__file__).resolve().parent
R=[json.loads(l) for l in (O/'newmaps-games.jsonl').read_text().splitlines()]
assert len(R)==100 and len({r['id'] for r in R})==100
assert not any(r['errors'] for r in R),[(r['id'],r['errors']) for r in R if r['errors']]
NAMES=['Australia','Tower Defense','Islands','Around UNSW','Stripes']
G=[(m,[r for r in R if r['map']==m]) for m in NAMES]+[('새 지도 5종',[r for r in R if r['group']=='new5']),('기존 10종',[r for r in R if r['group']=='old10']),('Maze·weakhold',[r for r in R if r['group']=='other'])]
def them(r):return 'B' if r['ours']=='A' else 'A'
def md(headers,rows):return '\n'.join(['| '+' | '.join(map(str,headers))+' |','| '+' | '.join('---' for _ in headers)+' |']+['| '+' | '.join(map(str,row))+' |' for row in rows])+'\n'
def avg(xs):return f'{statistics.mean(xs):.1f}' if xs else '—'
def pair(a,fn):return avg([fn(r,r['ours']) for r in a])+' / '+avg([fn(r,them(r)) for r in a])
def ids(a):return ', '.join(r['id'] for r in a)
def ds(a,our=True):return [d for r in a for d in r['deaths'] if d['team']==(r['ours'] if our else them(r))]
def terrain(d):return (d['pocket'] or d['dead_end']) and d['cause'] in ('wall','self','body') and not d['enemy']
for r in R:
 o=r['ours'];t=them(r);dd=[d for d in r['deaths'] if d['team']==o]
 r['flags']={
 'natural200_below_two_thirds':sum(r['natural'][o][:4])*3<sum(r['natural'][t][:4])*2,
 'terrain_recurrence_10':sum(terrain(d) for d in dd)>=10,
 'coverage100_below_half':'100' in r['snaps'] and r['snaps']['100'][o]['visited']*2<r['snaps']['100'][t]['visited'],
 'queen_rule_loss':not r['win'] and r['how']=='queen',
 'longest_loss_material_available':not r['win'] and r['how']=='longest' and r['snaps']['end'][o]['total']>r['snaps']['end'][t]['longest']}

def writecsv(name,headers,rows):
 with (O/name).open('w') as f:
  w=csv.writer(f);w.writerow(headers);w.writerows(rows)
writecsv('newmaps-curves.csv',['game','map','group','ours','round','present','team','role','longest','total','units','queen','visited'],[[r['id'],r['map'],r['group'],r['ours'],rd,int(rd in r['snaps']),t,'us' if t==r['ours'] else 'them',*[r['snaps'].get(rd,{}).get(t,{}).get(k,'') for k in ['longest','total','units','queen','visited']]] for r in R for rd in ['50','100','200','300','400','end'] for t in 'AB'])
writecsv('newmaps-economy.csv',['game','map','start_round','end_round_exclusive','team','role','pearls_all','pearls_natural'],[[r['id'],r['map'],i*50,(i+1)*50,t,'us' if t==r['ours'] else 'them',r['eats'][t][i],r['natural'][t][i]] for r in R for t in 'AB' for i in range(10)])
fields=['r','id','team','length','cause','raw_reason','actor','hit','collision_team','enemy','head','attempt','pocket','pocket_size','pocket_id','dead_end','corridor','near_portal','newborn','split_stub','explicit_suicide','dropped','eat_us','eat_them','eat_us_queen','eat_us_longest','uneaten']
writecsv('newmaps-deaths.csv',['game','map','ours']+fields,[[r['id'],r['map'],r['ours']]+[d.get(k) for k in fields] for r in R for d in r['deaths']])
writecsv('newmaps-game-summary.csv',['game','map','group','ours','opponent','win','decider','end_round','bot_id']+list(R[0]['flags']),[[r['id'],r['map'],r['group'],r['ours'],r['opponent'],r['win'],r['how'],r['round_end'],r['bot_ours'],*r['flags'].values()] for r in R])

S=[]
S.append('''새 지도 패배는 지도 크기 하나로 설명되지 않는다. 로컬에 실제 남아 있는 래더 기보 100판을 모두 재구성했다. 요청한 5종은 **35판 7승 28패(20.0%)**, 기존 10종은 **53판 31승 22패(58.5%)**다. Tower Defense에서는 r100 방문 칸이 48 대 169, r200 자연 진주 누적은 평균 6.1 대 110.4였다. Australia 두 판은 초반 탐색·자연 진주 섭취가 앞서도 작은 포털 방에서 소모되고 여왕 판정으로 졌다. Islands에서는 막다른 길의 6라운드 반복이 재현됐다. Around UNSW는 넓게 방문하고도 자연 진주 수확과 후반 승리 길이 보존에서 밀렸다. Stripes는 7판 모두 전멸 판정이어서 별도의 초기 경제·접촉 문제다.

**C2/C3 stay-home 수정은 v61에 없다.** `v61/main.cpp`는 `CENTER_PULL=40`, `NO_TAIL_ROOM=0`, `PENALTY_NO_TAIL=600`이다. C2의 `CENTER_PULL=0`, C3/NT6의 `NO_TAIL_ROOM=6`은 모두 꺼져 있다. `POCKET_CAP=48`과 `QUEEN_HOME_CLOSED=true`만 추가된 제출 기록과 일치한다. `CENTER_PATH`도 꺼져 있다. 따라서 해당 수정이 이미 들어갔다고 전제하면 안 된다. 다만 과거 C2/C3의 다른 지도 퇴행 기록 때문에 그대로 다시 켜자는 결론도 아니다.

**범위 제한:** 브리프의 “v61 893판” 원자료 전체는 이 작업공간에 없다. `battlecode/work/nr/`는 없고, `nr_*.txt`에는 기보 없는 과거 경기 767개가 남아 있다. 그중 요청 5종은 45판이다. 실제 다운로드된 100판(요청 5종 35판)은 표본 추출 없이 전부 분석했다. 893판 수치나 과거 45판의 행동을 재현했다고 주장하지 않는다. 다운로드 기보의 우리 bot ID는 모두 `15011`이지만, 서버 메타데이터의 submission ID가 null이며 ID→v61 라벨 대응 기록은 발견하지 못했다. **v61 설정 감사는 소스에 대해 확정이고, 100판의 버전 라벨은 브리프의 문맥에 의존한다.**

영향 규모는 아래 현상이 나타난 **패배 경기 수**다. 관측적 후보이며 고치면 뒤집힐 승수 추정이 아니다. 현상끼리 겹친다. 초반 자연 진주 열세 20판, 반복 지형 소모 17판, 심한 초기 탐색 정체 7판, 여왕 판정 패배 6판, 남은 총길이가 상대 최장보다 큰 최장 판정 패배 4판 순으로 검토할 가치가 있다. 기존 지도에서도 나타나는지와 반례를 함께 적었다.
''')
S.append('## 표: 범위와 승패\n')
inv=json.loads((O/'newmaps-inventory.json').read_text())
S.append(md(['자료','확인 결과','사용'],[
 ['battlecode/work/nr/','디렉터리 없음','기보 부재를 기록'],
 ['battlecode/work/nr_*.txt',f"{len({p for r in inv['games'] for p in r['lists']})}개 파일, 중복 제거 767개 과거 ID",'승패 목록·누락 인벤토리; 현재 100판과 합쳐 비율 계산하지 않음'],
 ['unsw-swarm/data/online/**','game JSON 100 + M replay 100; events-*.jsonl.gz 0','100판 전수 분석; 20개 series, 모두 ranked'],
 ['~/meow-loop-out/**','기보 387개, 래더 캐시·과거 분석 있음','387개는 로컬 harness/ident/기제/smoke 기보; 신규 래더 ID 없음'],
 ['전체 ID','867개 = 기보 100 + 목록만 767','newmaps-inventory.json에 모든 경로·ID'],
 ['기존 비교군','Autarky, Default, Devil, Portals, Prisoners Dilemma, Queen Of Spades, Schooltime, Slithery Fight, Trauma, Trophy','53판'],
 ['추가 새 지도','Maze 7판, weakhold 5판','기존 비교군에 섞지 않고 별도 보고'],
 ]))
S.append('목록만 남은 경기는 버전·ranked/unranked가 섞인 별도 이력이다. 행동 지표는 계산할 수 없지만 알려진 승패는 버리지 않고 아래에 보존했다. 893판 코호트와 같다는 증거가 없어 현재 100판과 합산하지 않는다.\n')
old_names={r['map'] for r in R if r['group']=='old10'}
hr=[]
for name in NAMES+['기존 10종','Maze·weakhold']:
 a=[r for r in inv['games'] if not r['replays'] and (r.get('list_map')==name or (name=='기존 10종' and r.get('list_map') in old_names) or (name=='Maze·weakhold' and r.get('list_map') in ['Maze','weakhold']))]
 hr.append([name,len(a),sum(r['list_result']=='W' for r in a),sum(r['list_result']=='L' for r in a),sum(r['list_result'] not in ['W','L'] for r in a),sum(r['list_ranked']=='R' for r in a),sum(r['list_ranked']=='U' for r in a)])
S.append(md(['기보 없는 과거 목록','n','W','L','기타','ranked','unranked'],hr))
rows=[]
for m in sorted({r['map'] for r in R}):
 a=[r for r in R if r['map']==m];c=collections.Counter(('W' if r['win'] else 'L',r['how']) for r in a)
 rows.append([m,len(a),sum(r['win'] for r in a),len(a)-sum(r['win'] for r in a),f"{100*sum(r['win'] for r in a)/len(a):.1f}%",*[f"{c['W',k]}/{c['L',k]}" for k in ['elimination','queen','longest','total']],sum(r['ours']=='A' for r in a),sum(r['ours']=='B' for r in a)])
S.append(md(['지도','n','W','L','승률','전멸 W/L','여왕 W/L','최장 W/L','총길이 W/L','A좌석 n','B좌석 n'],rows))
S.append('여왕은 각 팀의 최초 최저 ID다. 전멸을 먼저 분리하고, 시간 종료는 **여왕 길이 → 최장 → 총길이** 순서에서 최초로 다른 항목을 사용했다. 두 여왕이 모두 살아도 길이가 같으면 최장 판정이다. `ladq.py`의 여왕 생사만 비교하는 간이 분류를 그대로 쓰지 않았다. 판정 결과는 서버 winner와 100/100 일치한다.\n')
S.append('## 표: 길이·개체 수 곡선\n\n각 값은 **우리 / 상대 평균**, 해당 라운드 시작 상태. 종료된 게임을 후기 라운드에 이월하지 않았다. n을 반드시 함께 읽어야 한다. end는 모든 게임의 실제 종료 상태다. 모든 지도·게임의 수치는 `newmaps-curves.csv`에 있다.\n')
rows=[]
for name,a in G:
 for rd in ['50','100','200','300','400','end']:
  ar=[r for r in a if rd in r['snaps']]
  rows.append([name,rd,len(ar),*[pair(ar,lambda r,t,k=k:r['snaps'][rd][t][k]) for k in ['longest','total','units']]])
S.append(md(['지도군','round','n','최장','총길이','개체 수'],rows))
S.append('## 표: 방문 칸과 경제\n\n방문은 모든 아군 **머리가 실제 도달한 서로 다른 칸**의 합집합이다. 시작 머리·분열 자식 머리도 포함한다. 시야로만 본 칸, 현재 점유 면적, 영구 영토를 뜻하지 않는다. 진주는 `tileChange(false)`를 당시 행동자에 연결하며, 자연 생성과 사체 낙하를 구분한다. 유료 이동이 성장을 상쇄해도 섭취를 놓치지 않는다.\n')
rows=[]
for name,a in G:
 row=[name]
 for rd in ['100','200']:
  ar=[r for r in a if rd in r['snaps']];row.extend([len(ar),pair(ar,lambda r,t:r['snaps'][rd][t]['visited'])])
 row.extend([pair(a,lambda r,t:sum(r['natural'][t][:4])),pair(a,lambda r,t:sum(r['eats'][t][:4]))]);rows.append(row)
S.append(md(['지도군','r100 n','방문 r100','r200 n','방문 r200','자연 진주 r0–199','전체 진주 r0–199'],rows))
S.append('50라운드 구간별 **전체 섭취 / 자연 섭취를 별도 표**로 제공한다. 아래 각 셀의 구분자는 우리 : 상대이며 n은 고정된 해당 지도군 전체 게임 수다. 조기 종료 뒤 구간은 0이므로 생존 경기당 수확률로 해석하지 않는다. 이 처리의 영향은 경제 차이가 작은 게임에서 특히 주의한다.\n')
for key,label in [('eats','전체 진주(사체 포함)'),('natural','자연 진주')]:
 rows=[]
 for name,a in G:rows.append([name,len(a)]+[pair(a,lambda r,t:r[key][t][i]).replace(' / ',' : ') for i in range(10)])
 S.append('### '+label+'\n\n'+md(['지도군','n']+[f'{i*50}–{i*50+49}' for i in range(10)],rows))
S.append('## 표: 우리 사망 원인·시점·길이·지형\n\n`wall/self/body/head-on`은 엔진 사유다. enemy는 별도 축으로, 적 몸과 충돌하거나 적과 머리 충돌한 경우다. 아군 몸/머리와 구별했다. `suicide`는 실제 action=suicide가 선행한 경우만이며, wall/self를 의도적인 먹이기로 단정하지 않는다.\n')
rows=[]
for name,a in G:
 dd=ds(a);c=collections.Counter(d['cause'] for d in dd)
 rows.append([name,len(dd),*[c[k] for k in ['wall','self','body','head-on','suicide','invalid']],sum(d['cause']=='body' and d['enemy'] for d in dd),sum(d['cause']=='head-on' and d['enemy'] and d['actor']!=d['id'] for d in dd),sum(d['cause']=='head-on' and d['enemy'] and d['actor']==d['id'] for d in dd)])
S.append(md(['지도군','사망','wall','self','body','head-on','suicide','invalid','body 중 적 몸','적이 머리에 돌진','우리가 적 머리에 돌진'],rows))
rows=[]
for name,a in G:
 dd=ds(a);rows.append([name,*[sum(i*50<=d['r']<(i+1)*50 for d in dd) for i in range(10)]])
S.append(md(['지도군']+[f'r{i*50}–{i*50+49}' for i in range(10)],rows))
rows=[]
for name,a in G:
 dd=ds(a);rows.append([name,*[sum(lo<=d['length']<=hi for d in dd) for lo,hi in [(0,2),(3,4),(5,9),(10,19),(20,10000)]],sum(d['length'] for d in dd)])
S.append(md(['지도군','길이 ≤2','3–4','5–9','10–19','≥20','사망 당시 길이 합'],rows))
S.append('지형은 기보의 실제 벽·포털·wrap으로 만든 그래프에서 계산했다. pocket=포털을 제거한 연결 성분 ≤48칸, dead end=같은 그래프에서 차수 ≤1을 반복 제거한 가지, corridor=양쪽 반대 방향만 열린 폭 1 직선 칸, near portal=포털 인접 칸까지 열린 일반 간선 거리 ≤2. 막다른 가지와 포털 방은 겹칠 수 있다. 일반 큰 연결 성분 안의 넓은 단일입구 방까지 모두 포착하는 완전한 주머니 분류는 아니다. 위치는 **사망 직전 머리 좌표**이며 시도 목적지도 raw에 저장했다.\n')
rows=[]
for name,a in G:
 u=ds(a);t=ds(a,False);rows.append([name,*[f"{sum(d[k] for d in u)} / {sum(d[k] for d in t)}" for k in ['pocket','dead_end','corridor','near_portal']],f"{sum(terrain(d) for d in u)} / {sum(terrain(d) for d in t)}"])
S.append(md(['지도군','pocket 사망 우리/상대','dead end','corridor','near portal','pocket/가지의 비적대 wall/self/body'],rows))
S.append('## 표: 여왕의 운명\n\n요청 5종 35판 전부다. `생존 Lx`는 종료 생존 길이이며, 사망은 `r / 원인 / 당시 길이`다. 적이 먼저 들이받은 머리 충돌에는 `피격`을 붙였다. 나머지 65판도 `newmaps-games.jsonl`의 queen_death와 curves에 있다.\n')
def qfmt(r,t):
 d=r['queen_death'][t]
 if d is None:return '생존 L'+str(r['snaps']['end'][t]['queen'])
 return f"r{d['r']} / {d['cause']}{' 피격' if d['cause']=='head-on' and d['actor']!=d['id'] else ''} / L{d['length']}"
S.append(md(['game','지도','결과·판정','우리 여왕','상대 여왕'],[[r['id'],r['map'],('W ' if r['win'] else 'L ')+r['how'],qfmt(r,r['ours']),qfmt(r,them(r))] for r in R if r['group']=='new5']))
S.append('## 표: 자살과 먹이 회수\n\n엔진은 죽은 길이 L 중 ceil(L/2)개만 진주로 만든다. 아래 낙하량은 이 공식을 가정한 값이 아니라 실제 연속 tileChange(true)를 센 값이며 모든 사망에서 공식과 일치했다. 출처를 계속 보존해 끝까지 누가 먹었는지 추적했다. “우리 최장”은 섭취 직전 살아 있는 최장 개체(동률 최저 ID)이지 봇 내부 지정 leader나 최종 승자 계보가 아니다.\n')
rows=[]
for name,a in G:
 for own in [True,False]:
  dd=[d for d in ds(a,own) if d['explicit_suicide']]
  rows.append([name,'우리' if own else '상대',len(dd),sum(d['length'] for d in dd),sum(d['dropped'] for d in dd),sum(d['eat_us'] for d in dd),sum(d['eat_them'] for d in dd),sum(d['uneaten'] for d in dd),sum(d['eat_us_longest'] for d in dd),sum(d['eat_us_queen'] for d in dd)])
S.append(md(['지도군','자살 주체','횟수','원래 길이','실제 낙하','우리 섭취','상대 섭취','종료 미회수','우리 최장 섭취','우리 여왕 섭취'],rows))
S.append('의도 불명인 wall/self/아군 body 사망도 놓치지 않도록 별도로 집계했다. 이 수치를 전부 실수나 전부 먹이기라고 부르지 않는다.\n')
rows=[]
for name,a in G:
 dd=[d for d in ds(a) if d['cause'] in ('wall','self','body') and not d['enemy']];rows.append([name,len(dd),*[sum(d[k] for d in dd) for k in ['length','dropped','eat_us','eat_them','uneaten']]])
S.append(md(['지도군','횟수','길이','낙하','우리 회수','상대 회수','미회수'],rows))
S.append('## 표: v61 실제 설정\n')
S.append(md(['기능','v61 값','판정·근거'],[
 ['C2: center pull 제거','CENTER_PULL=40.0','OFF. C2에는 0 필요'],['C3: C2 + 방 크기 조건','CENTER_PULL=40.0; NO_TAIL_ROOM=0','OFF. C3에는 center 0 + room 6 필요'],['NT6','NO_TAIL_ROOM=0','OFF. 꼬리에 못 닿으면 room과 무관하게 penalty'],['기존 꼬리 미도달 벌점','PENALTY_NO_TAIL=600.0','ON'],['벽을 고려한 중심 거리','CENTER_PATH=false','OFF'],['원거리 탐색','FAR_GAIN=2','ON'],['주머니 길이 제한','POCKET_CAP=48; POCKET_DIV=2','ON. 미관측 간선이 있으면 크기를 cap으로 반환'],['포털 주머니 진입 금지','POCKET_PORTAL_BAN=false','OFF'],['닫힌 홈 여왕 모드','QUEEN_HOME_CLOSED=true','ON. 기존 조건의 최저 40칸·최대 전체의 1/2 등 적용'],['모든 실제 여왕 포털 금지','QUEEN_PORTAL_ALL=false','OFF'],['기존 여왕 크기 조건','QUEEN_MIN_CELLS=600','남아 있음; 권장 규칙이 아니라 현행 코드 사실']]))
S.append('`work/v60toggles.txt`의 중복 QUEEN_LEAD_BONUS는 마지막 값 1000을 적용해 고유 21개 항목을 전부 대조했으며 v61과 모두 일치했다. 소스 위치: `v61/main.cpp` 129–147, 222, 319–327, 410–411, 2412–2453, 3529–3530, 3585–3599. CENTER_PULL은 코드의 center_map·초반 round·길이 등의 조건부이며 매 턴 항상 40점이 적용된다는 뜻은 아니다.\n')
S.append('## 발견 사항: 영향 경기 수 순위\n')
keys=list(R[0]['flags']);titles=['자연 진주 수확 열세','반복되는 작은 방·막다른 가지 소모','초기 탐색 정체와 출구 평가','여왕 규칙과 역할 충돌','후반 승리 길이의 생존·집중 실패']
rows=[]
for i,(k,title) in enumerate(zip(keys,titles),1):
 new=[r for r in R if r['group']=='new5' and not r['win'] and r['flags'][k]];old=[r for r in R if r['group']=='old10' and not r['win'] and r['flags'][k]]
 rows.append([i,title,f'{len(new)}/28',', '.join(f'{m} {sum(r["map"]==m for r in new)}' for m in NAMES if any(r['map']==m for r in new)),f'{len(old)}/22'])
S.append(md(['순위','관측 현상','새 지도 패배 중','공유 지도','기존 지도 패배 중'],rows))
S.append('경기 수는 겹치며 더하면 안 된다. 문턱은 분석을 설명하기 위해 사후에 정한 기술 통계다: ① r0–199 자연 진주가 상대 ⅔ 미만(조기 종료면 실제 종료까지), ② pocket/가지에서 비적대 wall/self/body ≥10회, ③ r100까지 살아 있는 경기에서 방문 칸이 상대 절반 미만, ④ 실제 여왕 판정 패배, ⑤ 최장 판정 패배인데 종료 총길이는 상대 최장보다 큼. ②는 승리 7판 중 6판에도 나타나므로 패배의 충분조건이 아니다. ③은 ①의 일부와 중첩되지만 좁은 출구 평가라는 별도 수정 후보다. ⑤는 전체 총길이를 무손실 합칠 수 있다는 뜻이 아니다.\n')
for k,title in zip(keys,titles):
 a=[r for r in R if r['group']=='new5' and not r['win'] and r['flags'][k]];S.append(f'**{title}에 해당한 패배 ID:** {ids(a)}.\n')
S.append('''### 1. 이동 범위보다 지속 수확 지점 확보가 뒤진다 — 20패

새 지도 r0–199 자연 진주는 합계 **5,478 대 9,574**, 기존 10종은 **8,345 대 7,964**다. 20패의 ⅔ 미만 조건은 5개 지도 모두에 나타난다. 그러나 방문 칸 부족과 같은 현상은 아니다. Around UNSW는 r200 방문 2,111.6 대 2,009.6으로 앞서도 자연 진주가 게임당 283.6 대 502.9다. 990091은 r0–99 자연 157 대 240, r0–199 287 대 497; 993428은 136 대 249, 263 대 498이다. 이동한 칸 수만 키우는 목표로는 이 차이를 설명하거나 해결할 수 없다.

Stripes의 980565는 r0–99 자연 3 대 80, r155 전멸; 987226은 자연 1 대 51, r130 전멸. 초반 개체를 불릴 경제가 없어서 머리 교환 후 재생산이 안 되는 양상이다. 반대로 989284는 r100 자연 34 대 30으로 앞섰다가 r200 41 대 78로 뒤집혀 r221 전멸했다. “처음부터 탐색이 느렸다”로 모든 Stripes 패배를 묶을 수도 없다.

**일반 제안:** 관측한 진주 재생 간격·안전 경로·경쟁 상태로 예상 순수확이 높은 지역을 유지하고, 같은 경로의 중복 탐색을 줄인다. 지도의 면적·이름으로 켜지 않는다. **미확인:** 실제 fountain 점유 지속시간/의사결정 점수가 로그에 없으므로 '수확 지점 선택'은 원인 가설이다. 자연 진주 열세는 전투로 밀려난 결과일 수도 있다. 대조 사례는 988919·990120으로, 초반 자연 진주가 우세해도 패배했다. [카드 01](cards/01-sustained-natural-harvest.md).

### 2. 작은 방과 막다른 가지의 재순환은 고쳐지지 않았다 — 17패

Australia 988919에서 포털 없는 12칸 방 두 개에 우리 사망 **149회**, 990120은 **64회**, 993583은 **47회**다. 988919의 작은 방 진입은 23회 전부 L2–3이었다. 첫 진입은 r58, #14 L2, (35,24)→(56,40); r73 #20 L3가 뒤따른다. `POCKET_CAP=48, DIV=2`가 켜져도 12칸 방에서 grown≤6인 동안 벌점이 없고, 관측이 덜 된 경우에는 아예 크기 48을 반환한다. **소스상 사각지대와 실제 진입은 확인했지만, 각 턴 pocket_size 평가값은 기보에 없어서 발동 여부까지 단정하지 않는다.**

Islands 989283의 (40,12)에서는 r50,56,62,68,74,80,86,92,98,104,110,116,122,128,134,140,146,152에 L2가 6라운드마다 wall/self로 죽었다. 모두 직전 2라운드 내 분열한 부모 잔여체이며 각 낙하 진주 1개는 우리 편이 회수했다. 993189의 (15,12)도 r41,47,53,59,65,71,77,83에 같은 반복이 있다. **아군이 사체를 회수한다는 사실만으로 유익한 먹이기라 할 수 없다:** L2 중 1만 회수해 같은 가지에서 재순환하면 한 번마다 길이 1과 행동 기회가 사라진다.

일반 제안은 출구 수·몸이 돌아 나올 수 있는 공간·예상 성장·최근 같은 가지의 분열 사망 이력을 함께 보고 진입/분열을 억제하는 것이다. 과거 좌표나 지도명을 쓰지 않는다. 이 현상이 승리에도 존재하고 상대의 self-death가 더 많을 때도 있어 단순 사망 수 최소화는 적절한 목표가 아니다. 감소한 가지 체류/순손실이 외부 자연 진주 수확·생존으로 연결되는지 봐야 한다. [카드 02](cards/02-escape-safe-pocket-and-branch.md).

### 3. 좁은 출구를 빠져나가는 상태 평가가 필요하다 — 심한 정체 7패

r100 방문이 상대 절반 미만인 패배는 Tower Defense 5판과 Stripes 2판이다. Tower Defense는 전체 7판 r100 방문 평균 **48 대 169.4**, r200 생존 6판은 **79.3 대 328.8**이다. 983954는 r456 전멸까지 방문이 64 대 501, 990235는 r183 전멸까지 46 대 330이다. 7판의 r0–199 자연 진주는 43 대 773이다. 32×16에서도 발생하므로 큰 지도라는 조건은 원인이 아니다.

소스에서 꼬리 미도달 벌점 600과 벽을 고려하지 않는 중심 당김은 여전히 켜져 있다. 과거 디버그 기록은 이 항들이 출구 이동을 막았다고 했고 현 기보에서 정체가 재현됐다. 다만 이번 기보는 점수 항별 로그가 없으므로 동일한 턴별 원인까지 입증한 것은 아니다. Stripes의 정체를 같은 두 항 탓으로 확정하지도 않는다.

**일반 제안:** 통로 너머에 충분한 연결 공간이 있고 몸의 통과가 가능하면 꼬리에 즉시 돌아올 수 없다는 이유만으로 진입을 막지 않으며, 이동 불가능한 벽 너머 중심은 목표 가치에서 제외한다. 상대 도달 시간·충돌 위험은 따로 보존한다. 과거 C2/C3 전체 적용은 다른 지도에서 퇴행해 기각됐으므로 '전부 끄기' 대신 상태 조건을 검증한다. 반례 987053은 심한 경제 열세에도 여왕 생존으로 승리했고, 987230은 자기 방을 벗어났지만 여왕 자살로 졌다. [카드 03](cards/03-passable-corridor-exit.md).

### 4. 여왕 규칙과 먹이기 역할이 충돌한다 — 직접 판정 6패

새 지도 여왕은 35판 중 **34판 사망**했지만, 사망을 모두 패배 원인으로 세지 않았다. 상대 여왕도 죽거나 전멸 판정이 우선인 경우가 있기 때문이다. 직접 여왕 판정으로 진 것은 980156,983956,987230,988919,990120,990121의 6판이다. 같은 현상은 기존 지도 패배 22판 중 10판에도 있어 새 지도만의 문제가 아니다.

가장 명확한 역할 충돌은 **987230 r403, 실제 여왕 #1 L3의 명시적 자살**이다. 낙하 2개를 우리 #4가 r404/405에 모두 먹었다. 최종 우리 최장/총길이는 31/58, 상대는 여왕 혼자 L15였지만 졌다. 전달 자체는 성공했고 수신 대상과 승리 조건이 틀렸다. 990120은 여왕 r157 머리 피격 사망 뒤 최종 최장 45 대 24·총길이 287 대 167로 앞서고도 상대 여왕 L17 때문에 졌다. 990121도 r308 여왕 머리 피격, 최종 최장 49 대 29였지만 상대 여왕 L29가 이겼다.

**일반 제안:** 실제 여왕 정체성은 지형·지도 면적과 무관하게 유지하고 생존 여왕을 보통 feeder로 보내지 않는다. 여왕이 죽은 뒤에는 상대 여왕의 생사와 위치 관측에 따라 승리 목표를 재평가한다. 위 세 판에서 상대 여왕이 사라졌다면 고정된 종료 길이상 최장 우세지만, 실제 공격 성공·여왕 보존 후 길이가 그대로라는 보장은 없다. [카드 04](cards/04-queen-role-and-win-condition.md).

### 5. 후반에는 먹이를 더 버리기보다 키운 개체의 생존과 수신 대상을 확인해야 한다 — 4패

최장 판정 패배 8판 중 **4판**은 종료 총길이가 상대 최장보다 컸다: 990091(124 대 상대 최장65), 993189(49 대30), 993289(229 대50), 993428(173 대71). 나머지는 물량부터 부족하므로 '분산 길이만 합치면 된다'는 설명은 맞지 않는다. 네 판 중 세 판은 r400 우리 최장이 상대보다 컸다: 990091 34:25, 993189 52:22, 993289 17:16. 그러므로 과거 'r400부터 작은 최장이 문제'는 이번 전체 기보에서 유지되지 않는다.

보존 실패는 사건으로 보인다. **990091 r470 #777 L51**과 **993189 r412 #689 L59**가 적 머리에 피격되어 죽었다. 993289에서도 r371 L33, r395 L17, r399 L20을 잃었다. 반면 993428은 종료 총길이 173이 30개체에 나뉘고 최장은 66으로 상대 71에 못 미친다. 단순히 feeder 수만 늘리는 것보다, 살아남을 수신 개체와 실제 회수를 확인해야 한다.

새 지도 명시적 자살 812회, 원래 길이 2,157에서 진주 1,186이 떨어졌다. 우리 회수는 **1,046(88.2%)**, 상대 회수는 **91(7.7%)**, 미회수는 **49(4.1%)**다. 우리 최장이 먹은 것은 354(29.8% of drop), 우리 여왕은 0이다. 기존 10종은 우리 회수 1,094/1,194(91.6%), 우리 최장 558/1,194(46.7%), 여왕 159개다. '희생 대부분을 상대가 먹는다'는 가설은 기각된다. 최장 회수율은 상대적으로 낮지만 순간 최장과 내부 leader가 다를 수 있어 그 자체로 버그 확정은 아니다.

**일반 제안:** 여왕 동점/부재 등 최장이 실제 승리 기준인 상태에서, 관측 가능한 적의 다음 도달 범위와 수신 경로가 안전할 때만 집중 먹이기를 실행하고 키운 개체의 위험을 먼저 줄인다. 지도 이름·크기 문턱은 쓰지 않는다. [카드 05](cards/05-protect-and-feed-winning-length.md).
''')
S.append('## 이전 주장 검증과 해석 한계\n'+md(['이전 주장','이번 확인'],[
 ['Tower Defense stay-home','재현. C2/C3/NT6 미포함 확인. 평가항별 인과는 기존 디버그 기록이고 이번에는 행동·소스 대조'],
 ['Australia pocket deaths','3/3판 재현, 실제 포털 없는 12칸 방. PK48이 모든 진입을 막는다는 주장은 틀림'],
 ['Islands dead-end loop','좌표·분열 잔여체·6라운드 주기·아군 재섭취까지 재현'],
 ['queen deaths','새 지도 34/35 사망. 직접 여왕 판정 패배는 6/28로 분리'],
 ['r400 최장 3–15 대 상대18–75','이번 코호트의 보편 명제로는 기각. Australia·Around UNSW의 생존판 평균은 오히려 우리 최장이 큼'],
 ['상대가 희생 먹이를 대량 탈취','명시적 자살 낙하의 상대 회수 7.7%; 주된 손실이라는 주장 지지 안 됨'],
 ['큰 지도만 문제','32×16 정체와 24×12 전멸도 있어 단독 설명 불가'],
 ]))
S.append('''현 분석은 다운로드된 20개 시리즈의 관측 비교다. 상대 구성·좌석·지도별 경기 수가 다르고 Australia는 3판 모두 B라서 원인 효과의 크기나 개선 승률을 추정할 수 없다. 기존 지도 53판은 같은 100판 다운로드 코호트의 비교군이지만 지도별 상대 매칭까지 통제된 실험은 아니다. 자연 진주 열세는 나쁜 경로 선택의 원인일 수도, 전투 열세의 결과일 수도 있다. 사망·반복 소모·경제·여왕 현상은 겹친다.

원자료에 없는 경기·관측·평가 점수·버전 라벨을 보간하지 않았다. 로컬 893판 전수 검증은 불가능하며 누락 목록이 남아 있다. 추가 다운로드나 래더 요청 없이 현재 가진 100판을 모두 처리한 결과다.

## 사용 자료와 재현·검증

- `battlecode/replay.py`: `load`, `EVENT_NAMES`, `point`로 packed Cap’n Proto 이벤트를 전수 읽음. `work/bc.py`의 `load_map`과 body 재구성 방식을 재사용.
- `work/feedcheck.py`, `dtrace.py`, `bigdeath.py`, `bigdeaths.py`, `bigloc.py`, `lossan.py`, `leadfate.py`, `deathwin.py`, `howmap.py`, `ladq.py`, `eatcmp.py`를 읽고 지표 정의를 대조. 기존 `ladq`는 queen 생사만, `eatcmp`는 순길이 증가만 보는 제한이 있어 판정/경제는 보완했다.
- `work/plan.md` 약 600–646, `work/v60toggles.txt`, `v61/main.cpp`, `.github/ISSUE_TEMPLATE/idea.yml`. 과거 로컬 승패 숫자는 이번 판정 증거로 재사용하지 않음.
- `tune_runs/official127/*.map`의 동일 MAP_NAME 지도를 모든 기보와 비교. **98/100은 간선까지 정확히 일치. Schooltime 두 판은 같은 크기의 다른 간선 변형**이므로 실제 기보 지형을 사용. 숨겨진 TILE respawn 값은 기보의 자연 진주 출현 사건으로 대신 측정했으며 추정 spawn-rate를 진주 수에 섞지 않음.
- `unsw-swarm/data/online/dl-20261003/{game-*.json,M*.replay,index.json}` 전체. `~/meow-loop-out/ladder.json`, `card-0/attempt-1791068432/{analyse2.py,ladder.json,rows2.pkl}` 등은 발견 경로/이전 주장 대조에만 사용; 최종 수치는 기보에서 다시 계산. `events-*.jsonl.gz`는 index 설명에는 있으나 실제 파일 0개.
- `newmaps-inventory.json`: 지정 세 루트의 파일 전체 목록과 래더 ID별 자료 유무. 로컬 M0…M31 기보는 온라인 game metadata 없는 smoke 산출물로 제외. 과거 nr 목록만 있는 767판은 가용 승패를 보존했으나 현재 코호트와 섞지 않음.
- `newmaps_extract.py` → `newmaps-games.jsonl`, `newmaps-extract.log`; `newmaps_report.py` → 본 보고서, 5개 카드, CSV 4개. 실행은 `python3 data/analysis/newmaps_extract.py` 다음 `python3 data/analysis/newmaps_report.py`(unsw-swarm 루트 기준). 현재 로컬 절대경로를 사용한다.
- `newmaps-curves.csv`: 게임별 모든 체크포인트; `newmaps-economy.csv`: 모든 50라운드 진주 흐름; `newmaps-deaths.csv`: 모든 사망의 round·길이·좌표·원인·적대 여부·지형·낙하/회수; `newmaps-game-summary.csv`: 승패·판정·순위별 해당 여부. 상세 기보 JSONL에는 분열·포털 진입·개별 소비자 round/ID/좌표도 남김.

검증: 100개 고유 ID, 모든 메타데이터 winner 일치, 모든 게임 양측 종료 개체 수/최장/총길이 일치, 여왕→최장→총길이 판정 일치, 분열 길이 보존, 업데이트 tail 일치, **모든 실제 이동의 벽·포털·wrap 목적지 일치**, 모든 사망 낙하량 일치, 진주 출처 누락/중복 생성 0. 몸/머리 충돌의 팀 귀속 불명 0. 별도로 남아 있던 `card-0/attempt-1791068432/rows2.pkl`과도 100판 전체 양측 종료 상태 및 여왕 사망 round가 일치했다(같은 Python parser 계열이므로 완전히 독립적인 decoder 검증은 아님). 기존 JavaScript mass_ledger 독립 대조도 시도했으나 설치된 viewer VSIX 경로가 없어 실행되지 않았으므로 독립 검증이 됐다고 세지 않았다.

봇 소스·기존 도구·설정은 수정하지 않았다. 새 분석 파일만 작성했으며 래더 요청·커밋·GitHub 게시를 하지 않았다.
''')
(O/'newmaps-2026-10-04.md').write_text('\n'.join(S))

cards=[
('01-sustained-natural-harvest','[Idea] 관측한 재생 수익으로 수확 지역을 유지한다','economy',
'관측한 재생 간격, 안전 경로, 적·아군 경쟁으로 예상 순수확을 계산해 수확 지역을 유지한다. 중복 방문 자체의 보상보다 자연 진주의 지속 수확을 높인다. 발동은 관측 상태와 경로로만 정하고 지도 이름·크기 문턱은 사용하지 않는다.',
'새 지도 패배 28판 중 20판에서 r0–199 자연 진주가 상대의 ⅔ 미만. Around UNSW 990091 r100 자연 157:240, r200 287:497; 993428은 136:249, 263:498. Around UNSW 전체 r200 방문은 2111.6:2009.6으로 우리가 앞선다. Stripes 980565는 r100 자연 3:80, r155 전멸. 988919·990120은 초기 자연 수확 우세인데도 패배하므로 이 현상이 모든 패배 원인은 아니다.',
'관측한 수익 지점의 안전 체류와 r50 구간별 자연 섭취/생존 개체-turn이 늘고, 중복 탐색·헛이동이 줄어든다. 사체 재섭취를 자연 수확 증가로 세지 않는다.',
'수익 추정이 높은 경로를 선택해도 실제 자연 수확률이 늘지 않거나 충돌/여왕 사망이 증가한다. 경제 열세가 경로 결정 전 이미 전투에 의해 결정되어 개입 기회가 없다.',
'기본 OFF 스위치 설계. 새 관측의 타일별 자연 생성·도달 거리·경쟁·선택 이유를 기록. 회전/반사/포털 연결을 바꾼 미지 지형에서 동일 상태의 발동을 점검한다. 양좌석 로컬 재현은 수확 기제·CPU·부작용 확인용이며 승률 채택 근거로 사용하지 않는다. baseline/off 동일성과 기존 안전 규칙을 점검한다.'),
('02-escape-safe-pocket-and-branch','[Idea] 성장 후 탈출과 분열 재순환을 검사한다','terrain',
'좁은 입구·작은 연결 공간에 들어갈 때 현재 길이뿐 아니라 관측된 진주를 먹은 뒤의 몸과 돌아 나올 경로를 검사한다. 같은 가지에서 분열 잔여체 사망과 재진입이 반복되면 외부 경로를 우선한다. 알려지지 않은 공간은 안전으로 확정하지 않는다.',
'새 지도 패배 17/28에서 작은 방/막다른 가지의 비적대 wall/self/body가 ≥10회. Australia 988919의 12칸 방 사망149회, 진입23회 전부 L2–3(r58 #14, r73 #20 등). Islands 989283 (40,12), r50–152에 6라운드마다 L2 분열 잔여체가 사망하고 낙하1개를 아군이 회수. 993189 (15,12), r41–83 동일 반복. v61 POCKET_CAP48/DIV2는 grown≤6 또는 공간 미관측에 사각지대. 승리에도 반복이 있어 사망 감소만으로 유익함을 확정할 수 없다.',
'같은 가지에서의 6라운드 분열-사망 연쇄와 L−아군회수 순손실이 줄고, 빠져나온 개체의 외부 자연 수확이 증가한다. 유익한 수확/먹이기는 보존한다.',
'반복을 막아도 지역 순수확/외부 기회가 개선되지 않거나, 반복이 실제로 가장 유리한 자연 수확 경로였다. 성장 예측 때문에 안전한 지역까지 회피하며 전체 경제가 악화된다.',
'지도 좌표 없이 연결 성분·가지 입구·개체 몸·관측 성장으로 로그를 만든다. 작은 방, 단일입구 가지, 열린 회랑, 포털 출구를 생성해 회전/반사/관측 가림 변형을 양좌석으로 점검한다. 온라인 사례는 기제 기준으로만 사용. OFF 동일성·CPU·정상 분열 보존을 확인한다.'),
('03-passable-corridor-exit','[Idea] 통과 가능한 출구의 꼬리 미도달 벌점을 구분한다','terrain',
'폭이 좁아도 통로 너머 연결 공간과 몸의 통과 여유가 충분하면 즉시 꼬리에 돌아오지 못한다는 사실만으로 출구 이동을 배제하지 않는다. 목표의 거리 평가는 실제 열린 간선을 따르고, 충돌·적 도달 위험은 별도로 유지한다.',
'r100 방문이 상대 절반 미만인 새 지도 패배7판(Tower Defense5, Stripes2). Tower Defense 평균 방문 r100 48:169.4, r200 79.3:328.8. 983954 종료r456까지64:501, 990235 종료r183까지46:330. v61 CENTER_PULL40, NO_TAIL_ROOM0, PENALTY_NO_TAIL600, CENTER_PATH=false: C2/C3/NT6 미포함. 과거 C2/C3 전체 적용은 다른 지도에서 퇴행해 기각된 기록이 있다. 현 기보에는 항별 평가 로그가 없어 현상의 정확한 점수 원인은 아직 가설이다.',
'안전한 좁은 출구에서 내부 순환보다 외부 경로의 점수가 높아지고 최초 통과가 앞당겨진다. 실제 막힌 가지에서는 회피가 유지되며 자연 진주 접근 시간이 줄어든다.',
'출구 선택을 막던 항이 해당 벌점/거리 항이 아니거나, 출구를 빨리 지나도 적 도달 때문에 개체를 잃고 자연 수확이 늘지 않는다. 회랑 끝의 함정에 더 자주 들어간다.',
'먼저 baseline 출구 후보별 꼬리 도달·연결 공간·통과 여유·적 최단 도달·중심 거리 항을 기록한다. C2/C3 전역 토글 재활성화 대신 관측 상태 조건으로 실험한다. 회전·좌우반전·먼 출구·실제 막다른 길을 생성하고 양좌석에서 발동과 위양성을 확인. OFF 동일성·CPU 확인.'),
('04-queen-role-and-win-condition','[Idea] 실제 여왕의 역할을 승리 규칙에 고정한다','queen',
'실제 여왕이 살아 있으면 일반 feeder 자살 대상에서 제외하고, 승리 규칙상 여왕 길이가 우선임을 목표 선택에 유지한다. 여왕 부재가 확정되면 상대 여왕 상태를 우선 고려한다. 역할은 팀 최저 초기 ID와 생사로 정한다.',
'새 지도 여왕 판정 패배6판, 기존 지도10판. 987230 r403 실제 여왕#1 L3가 suicide, 낙하2개를 우리#4가 r404/405에 회수했지만 최장31:15로 앞서도 패배. 990120 여왕r157 피격 후 최장45:24·총287:167로 앞서며 여왕판정 패배. 990121 여왕r308 피격, 종료 최장49:29이나 패배. 새 지도 여왕사망34/35를 모두 구제 가능한 패배로 세지는 않는다.',
'실제 여왕이 생존 중 자살 feeder로 선택되는 사건0. 생존 여왕을 둔 상태의 수신 대상이 승리 조건과 맞고, 여왕 부재 시 무의미한 최장 우세에만 머무는 행동이 감소한다.',
'여왕 역할 보존이 독립 개체들의 안전/경제를 훼손하거나 자살이 실제 여왕이 아니라는 ID 반증이 나온다. 공격 전환이 관측되지 않은 상대 여왕을 추정해 무리한 공격만 늘린다. 단순 여왕 생존이 상대 여왕 길이를 이기지 못한다.',
'여왕 생존/사망/상대 미확인/둘 다 사망/동률을 교차한 상태 기반 fixture에서 역할 선택을 점검한다. 관측상 알 수 없는 적 여왕 사망을 oracle로 넣지 않는다. 987230형 수신자 옆 여왕도 일반 feeder가 되지 않는지 확인. OFF 동일성·CPU·실제 게임 규칙 판정을 검증하고 양좌석 미지 지형에서 기제를 확인.'),
('05-protect-and-feed-winning-length','[Idea] 살아남을 수신 개체에만 후반 길이를 집중한다','late-game',
'여왕 상태상 최장이 승리 기준인 때, 수신 개체의 적 도달 위험과 실제 회수 경로를 확인한 뒤 먹이기를 실행한다. 이미 키운 개체가 위협받으면 추가 희생보다 탈출·호위를 우선하고 안전한 수신 경로를 회복한다.',
'새 지도 최장판정 패배8판 중4판은 총길이가 상대 최장보다 큼: 990091,993189,993289,993428. 앞의3판은 r400 최장 우세였음. 990091 r470 L51, 993189 r412 L59 적 머리 피격 사망. 993289 r371 L33/r395 L17/r399 L20 사망. 전체 새 지도 자살 낙하1186 중 아군1046, 적91, 미회수49: 대량 탈취 가설은 지지 안 됨. 순간 최장 회수354/1186은 기존558/1194보다 낮으나 내부 leader와 동의어는 아님.',
'먹이기 직전 예측 수신자와 실제 수신자가 일치하고 위험한 순간의 큰 개체 피격이 감소한다. 최장이 승리 기준일 때 후기 최장 우세를 종료까지 보존한다. 자살 횟수 자체는 목표가 아니다.',
'보호 판단으로 먹이기만 늦어지거나 보호한 개체가 승리 계보가 아니어서 최종 길이가 개선되지 않는다. 먹이 회수는 이미 충분했고 보존 실패가 회피 불가능한 접촉이었다. 상대 최장을 이길 물량부터 없는데 집중만 강요한다.',
'수신자 ID·길이·예측 회수 시점·적의 합법 도달 범위·실제 소비자를 기록한다. 위협 없는 수신/위협 있는 수신/총량부족/여왕우선 상태를 분리해 생성한 미지 지형에서 양좌석 기제 확인. OFF 동일성·CPU·통로 봉쇄 부작용 검증. 로컬 승률은 채택 근거로 삼지 않는다.')]
for slug,title,area,claim,evidence,signal,falsifier,test in cards:
 text=f'# {title}\n\nStatus: draft / untested\n\nArea: {area}\n\n## Claim\n\n{claim}\n\n## Evidence\n\n{evidence}\n\n근거: [전수 분석](../newmaps-2026-10-04.md), [게임별 지표](../newmaps-game-summary.csv), [사망·회수 사건](../newmaps-deaths.csv). 경기 수는 중복 가능한 관측 현상이며 개선 승수 예측이 아니다.\n\n## Expected signal\n\n{signal}\n\n## What would show it\'s wrong\n\n{falsifier}\n\n## Test plan\n\n{test}\n\n이 카드는 제안 초안이다. 이번 작업에서는 봇 구현·대전 실행·온라인 요청을 하지 않았다.\n'
 (O/'cards'/f'{slug}.md').write_text(text)
print('report + 5 cards + 4 CSV files written')
