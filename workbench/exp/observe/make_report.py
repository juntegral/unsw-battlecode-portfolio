import json, statistics, datetime
from pathlib import Path

O=Path(__file__).parent
ROOT=O.parent.parent
T=json.loads((O/'tables.json').read_text())
R=[5,10,20,30,50,100,200]
CO=[('local-F','W1 F'),('local-S','W1 S'),('ours-W0-W12','우리 W0–W12'),('ours-v1','우리 v1-w1..3'),('elite-top10','상위권')]
def pct(v,d=1):return '—' if v is None else f'{100*v:.{d}f}%'
def num(v):return '—' if v is None else f'{v:,.1f}'
def cp(co,r):return T['globalCohorts'][co]['checkpoints'][str(r)]
def sup(co,r,m='global'):return T['supplement']['results'][m][co][str(r)]
def ratio(a,b):return a/b if b else None
def med(xs):return statistics.median(xs) if xs else None
lines=[]
def p(s=''):lines.append(s)
def table(head,rows):
 p('| '+' | '.join(head)+' |');p('| '+' | '.join(['---']*len(head))+' |')
 for row in rows:p('| '+' | '.join('—' if v is None else str(v) for v in row)+' |')
 p()

now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds')
p('# 처음 보는 지도의 관측 가능성 — W3 입력')
p(f'작성 시각: {now}. 원자료·분자·분모·분포는 [tables.json](../../exp/observe/tables.json), 고정 표본은 [population.json](../../exp/observe/population.json).')
p()
a,b=cp('ours-W0-W12',30),cp('elite-top10',30)
p(f"[사실] r30까지 팀 전체가 실제 본 칸의 평균은 우리 W0–W12 {pct(a['coverage']['mean'])}(N={a['N']} 팀·경기), 상위권 {pct(b['coverage']['mean'])}(N={b['N']}). 같은 시각 살아 있는 한 프로세스의 직접 관측 평균은 각각 {pct(a['process']['all']['own']['coverage']['mean'])}(N={a['process']['N']})와 {pct(b['process']['all']['own']['coverage']['mean'])}(N={b['process']['N']})다. 이 차이가 W3의 주된 제약이다.")
p()
p('[해석] W3는 관측한 칸·간선, 확정한 대칭, 확인한 포털 짝, 샘의 리셋 표본, 증명된 주머니를 각 프로세스가 누적하는 구조로 시작하는 편이 맞다. r10·r25·r50에 팀 합집합 전체가 한 프로세스에 있다고 가정하면 자료가 지지하는 범위를 넘는다. 신규 탐색·공유 정책을 실제 실행해 검증한 N=0이며, 아래 권고는 기존 경로를 고정한 관측 연구의 설계 입력이다.')
p()
p('## 방법과 N의 뜻')
p()
p('[사실] 원본 기보를 읽기만 했다. 새 대전·네트워크·업로드·커밋 N=0. 작업 경로는 `exp/observe/**`와 이 문서다. `tables.json`을 먼저 만들고 분석 결과를 채웠으며, `SUMMARY.txt`는 검증·문서 작성 후 마지막에 쓴다. 무거운 명령에 `nice -n 10`을 요청했으나 샌드박스가 우선순위 변경을 거부했다. 메모리 여유 10%·디스크 21 GiB 미만이면 계산을 멈추는 가드를 사용했고 분석 작업 프로세스는 최대 2개였다.')
p()
table(['자료','경기 N','선택한 팀·경기 N','범위'],[
 ['W1 로컬','240','240','F-H 40, F-K 80, S-H 40, S-K 80; 인식 끔'],
 ['우리 온라인','1,260','1,260','W0–W12 관련 15세트×70=1,050; v1 3세트×70=210'],
 ['data/top','960','1,323','15 지도·배치 층마다 SHA256 순서 64경기; 기록 순위≤10인 편'],
 ['전체','2,460','2,823','20 지도·배치; 상위권 한 경기 양편을 포함할 수 있음']])
p(f"[사실] top 인덱스 N={json.load(open(O/'population.json'))['topPoolN']:,}; 층별 적격 모집단 N은 JSON의 `population.selection.poolN`에 있다. 승패로 표본을 골라내지 않았다. 상위권은 번들 5지도에서 N=0이다. 로컬은 같은 지도·시드·경로 조건을 여러 엔진/상대/좌석으로 반복했으므로 독립 난수 조건은 N={T['population']['localSeedMapConditions']}뿐이다. 팀·경기 평균은 각 편에 같은 가중치, 칸별 정확도·P/R은 누적 분자·분모, 프로세스 분포는 살아 있는 프로세스에 같은 가중치다. 서로 다른 판/편/칸을 독립 표본처럼 취급한 CI는 제시하지 않는다.")
p()
p('[사실] r0부터 r까지 각 프로세스의 **행동 입력 직전 머리** 중심 7×7 창을 누적했다. 경계는 토러스이며, 벽이 창을 가리지 않고 포털 너머로 시야가 연장되지 않는다. r에는 그 라운드 입력을 포함한다. 분열 뒤 새 프로세스가 처음 받은 창부터 관측을 시작한다. 조기 종료한 판은 팀 누적 시야를 마지막 값으로 유지하고, 프로세스 분포에서는 사라진 프로세스를 제외한다. 종료 N은 각 checkpoint의 `endedBeforeRoundN`, 살아 있는 편 N은 `process.liveTeamGameN`에 저장했다. 빈 샘/주머니·정밀도 분모는 0% 대신 null/—로 쓴다.')
p()
p('[사실] 지도 파일은 정답 채점에만 썼다. 관측한 칸에 붙은 네 간선의 종류와 spawn 여부만 학습기에 공개하고, 양끝을 관측한 포털만 짝을 연결했다. 온라인 기보는 countdown·spawn gap을 삭제한다. 따라서 온라인의 관측 칸 spawn 여부는 지도 정답을 실제 시야에 투영한 값이며, 그 정보는 실제 입력 countdown≥0으로 확인할 수 있다. 온라인/상위권의 **실제 countdown으로 빨라지는 대칭 시각과 리셋 분류 정확도 N=0**이다. 상위권 이동은 기존 지도에서 나온 행동을 미지 지도 메모리 모델에 투영한 것으로, 실제 봇 메모리나 미지 지도 정책을 측정한 것은 아니다.')
p()
p('[사실] spawn은 시도 때마다 countdown이 리셋되며 몸이 있어도 리셋된다. 숨은 `min_gap`/`max_gap`으로 정답 평균 μ=(min+max)/2와 시도율 λ=1/μ를 정의했다. 샘은 μ≤12다. 실제 진주 생성·섭취율은 다른 값이며 이 연구에서 추정하지 않았다. `rules/ALL.md`의 Vision, Map symmetry, Spawn countdowns, Sonar와 `general-principles.md`의 “r30 아군 시야 합집합은 공유의 상한”을 적용했다.')
p()
p('## 1. 팀 누적 시야')
p()
p('[사실] 아래는 전체 칸/전체 spawn/정답 샘의 **관측 경험** 비율이다. 샘 열은 샘으로 분류했다는 뜻이 아니다. 샘이 없는 지도는 그 평균에서 제외하며 N을 별도로 적었다. 각 지도·배치와 요청한 7시점의 분포 및 미러 확장 값은 JSON에 모두 있다.')
p()
rows=[]
for co,label in CO:
 for r in R:
  c=cp(co,r);rows.append([label,r,c['N'],pct(c['coverage']['mean']),pct(c['spawnCoverage']['mean']),f"{pct(c['fountainCoverage']['mean'])} (N={c['fountainCoverage']['N']})"])
table(['집단','r','팀·경기 N','전체 칸','spawn 칸','샘 칸'],rows)
p('[사실] 지도·배치별 핵심 시점이다. 각 시점 셀은 **전체 칸 / spawn / 샘**이고 퍼센트다. 우리 온라인은 W0–W12와 v1를 함께 묶었다. 없는 집단은 행을 만들지 않았으며, 번들 지도 상위권 N=0이다. 샘 N은 샘이 있는 경우 팀·경기 N과 같고, 정답 샘이 0인 경우 N=0/—다.')
p()
rows=[]
for m,mm in T['maps'].items():
 for co,label in [('ours-online','우리'),('elite-top10','상위권'),('local-F','W1 F'),('local-S','W1 S')]:
  if co not in mm['cohorts']:continue
  c=mm['cohorts'][co];cells=[]
  for r in [10,25,50]:
   q=c['checkpoints'][str(r)];cells.append(' / '.join(pct(q[k]['mean']) for k in ['coverage','spawnCoverage','fountainCoverage']))
  rows.append([m,label,c['N'],*cells])
table(['지도/배치','집단','팀·경기 N','r10','r25','r50'],rows)
p('[해석] 상위권의 빠른 확장은 더 많은 자식과 이동 지역의 합집합에서 나온다. 이는 자식마다 완성된 지도를 갖는다는 증거가 아니다. 번들 소형 지도에서 사망 후 팀 시야가 멈춘 사례도 최종 관측 값으로 남겨 두었다. 각 집단·시점 N은 위 표에 있으며, 이 자료로 탐색 정책의 승패 효과를 판정한 N=0이다.')
p()
p('## 2. 한 프로세스의 지식과 실제 음파 접촉을 통한 공유')
p()
p('[사실] 게임은 새끼를 새 프로세스로 시작한다. 부모 메모리가 자동으로 복사되지 않는다. 현재 v1 계열 음파는 위치·길이·목표 등의 요약을 보내며 완전한 칸·간선 표를 보내지 않는다. 따라서 미지 지도에서 완전한 정적 칸 정보의 기본 모델은 **own**이다. 아래 `상속`은 부모와 모든 선조의 관측 표가 출생 때 완전히 복사된다는 반사실 상한이며, 실제 상속 구현 실험 N=0이다.')
p()
p('[사실] 음파는 행동 후 최대 네 방향에 같은 숫자 payload를 보내고, 벽/몸/포털/꼬리 굴절을 거친 실제 도착 경로를 사용했다. 높은 ID가 아직 행동하지 않았다면 같은 라운드, 이미 행동한 프로세스는 다음 입력에서 읽는다. 원래 메시지 수신자를 고정하고 다음 후보 필드를 대신 실었다. 송신 시점에 내용을 정해 실패·적/자기 수신도 송신 순서를 소모했다. 수신자의 미관측 칸을 보고 내용을 고르는 오라클은 쓰지 않았다. 상대는 같은 프로토콜에 참여하지 않는다고 두었으며, 아군 출처/형식 판별이 성공한다는 조건부 추정이다.')
p()
table(['모델','payload/스케줄','측정하는 지식'],[
 ['own','직접 7×7 창 누적','네 간선 종류+spawn 여부'],
 ['상속 상한','출생 때 부모 누적 표·리셋 표본 복사','현행 규칙에서 자동 제공되지 않음'],
 ['칸 패킷','아직 보내지 않은 칸 우선, 이후 순환; 1칸/송신','좌표+네 간선 종류+spawn; 포털 짝 ID 제외'],
 ['대칭 요약','생존 대칭 후보 3비트; 수신 후보와 교집합','직접 아는 칸을 확정 대칭으로 확장'],
 ['창 패킷','송신 직전 창을 고정; 10조각×2회; 전부 받아야 적용','112간선 종류+49 spawn 비트+중심'],
 ['spawn 비트맵','고정 창 49비트+중심; 2조각×2회','spawn 여부만, 완전한 지형 칸 아님'],
 ['리셋 요약','타일/표본 수/합; 미송신 우선 후 순환','더 많은 표본 요약으로 대체; 중복 합산 금지']])
p('[사실] 64비트는 PROTOCOL3를 요청한 뒤의 조건이다. 최초 루트 입력에서 교환 전에는 32비트 제약이 있으며 자식은 부모 프로토콜 버전을 잇는다. 제안 패킷은 PROTOCOL3·아군 형식 판별·현재 표본의 W,H≤64를 가정한다. 일반 미지 지도 구현은 좌표 크기와 ID를 동적으로 잡고 32비트 부트스트랩을 별도로 둬야 한다. r200까지 관측된 최대 프로세스 ID는 '+str(T['population']['maxProcessIdBy200'])+'(경기 N=2,460)다. 제한된 비트 폭으로 ID를 잘라 부모/발신자를 식별하는 설계는 별도 검증이 필요하다.')
p()
rows=[]
for co,label in CO:
 for r in [10,25,50,100,200]:
  q=cp(co,r)['process'];v=q['all'];d=v['own']['coverage'];rows.append([label,r,q['N'],pct(d['mean']),'/'.join(pct(d[k]) for k in ['p10','p50','p90']),pct(v['inherited']['coverage']['mean']),pct(v['patch']['coverage']['mean']),pct(v['summary']['mirroredCoverage']['mean']),pct(v['block']['coverage']['mean'])])
table(['집단','r','살아 있는 프로세스 N','own 평균','own p10/50/90','상속 상한 평균','칸 패킷 평균','대칭 요약+미러 평균','창 패킷 평균'],rows)
p('[사실] 뿌리/자식별 분포와 나이, 모든 요청 시점의 분포는 JSON `process.roots/children/all`에 있다. 위 평균은 프로세스 수로 가중하므로 다수 자식을 만든 편이 더 큰 비중을 갖는다. 편별 own 평균 분포는 `seatMeanOwnCoverage`에 따로 저장했다.')
p()
rows=[]
for co,label in [('ours-W0-W12','우리 W0–W12'),('ours-v1','우리 v1'),('elite-top10','상위권')]:
 for r in [10,25,50]:
  q=cp(co,r)['process'];v=q['all'];rows.append([label,r,q['N'],*(f"{100*v[k]['mean']:.2f}pp" for k in ['inheritanceGain','patchGain','summaryMirroringGain','blockGain']),pct(v['bitmap']['knownTileCoverage']['mean'])])
table(['집단','r','프로세스 N','상속−own','칸 패킷−own','대칭 요약−own 미러','창 패킷−own','비트맵 spawn 여부를 아는 전체 칸'],rows)
p('[해석] 같은 경로에서 작은 대칭 요약이 완전한 지형 패킷보다 효율적이었다. 연속 조각을 전부 모아야 하는 창 패킷은 접촉 단절에 취약하다. 부모 표 전체를 출생 때 제공하는 상한과 칸 패킷의 실제 접촉 성과 차이는 크다. 우선 전달 후보는 최초 출발 머리 좌표·계보/발신 식별·대칭 후보다. 포털의 두 끝 좌표와 리셋 표본 수/합/출처도 작고 재사용 가능하다. 최초 좌표/포털 짝 전용 패킷의 추가 커버리지 측정 N=0이며, 표의 이득을 그 필드의 검증값으로 대신 쓰지 않는다.')
p()
p('## 3. 대칭을 언제 확정하는가')
p()
p('[사실] 세 후보는 y축 반사(파일 `y`, x좌표 뒤집기), x축 반사(파일 `x`, y좌표 뒤집기), 180도 회전(`xy`)이다. 대칭으로 두 관측 칸을 대응시켜 간선 종류/spawn support가 다르면 후보를 제거한다. 포털 양끝 관측이 있는 경우 짝 관계도 검사한다. 로컬에서는 두 칸의 관측 countdown 만료 시각이 겹치는 구간에 일치해야 한다는 조건을 더했다. 하나만 남은 최초 r을 결정 시각으로 기록하고, 모르는 부분을 미러로 복사한다. 후보가 여러 개면 복사하지 않는다. 미러 확장은 겹침 때문에 정확히 두 배가 되지 않는다.')
p()
p('[사실] 초기 집계의 대칭축 진단 라벨을 역으로 읽은 오류를 정정했다(`axis-label-correction.json`). 좌표 변환·관측 마스크·경로·f-bin 예상 자체는 바뀌지 않았고 정답 후보 진단 및 리셋 orbit 중복 제거를 다시 계산했다. 정정 후 정답 대칭 제거/잘못 확정 진단은 전체 경기 N=2,460에서 0건이다. 이 표본에는 x축 반사 지도 N=0이므로 그 계열의 결정 속도에 관한 경험적 보장은 없다.')
p()
rows=[]
for co,label in CO:
 for r in [10,25,50,200]:
  s=sup(co,r)['fullSymmetry'];rows.append([label,r,f"{s['teamDecidedN']}/{s['teamN']}",f"{s['teamDynamicDecidedN']}/{s['teamDynamicN']}" if s['teamDynamicN'] else 'N=0',pct(s['teamMirroredCoverageMean']),pct(s['teamDynamicMirroredCoverageMean']),f"{s['own']['decidedN']}/{s['own']['N']}",pct(s['own']['mirroredCoverageMean'])])
table(['집단','r','팀 확정/팀 N(포털 포함)','countdown 포함 확정/N','팀 미러 커버리지','countdown 포함 미러','own 확정/프로세스 N','own 미러 커버리지'],rows)
p('[사실] 지도·배치별 r200 안에 결정한 편의 최초 시각 중앙값과 결정 비율이다. 최초 시각은 **결정한 편만의 조건부 중앙값**으로, 미결정을 200으로 넣지 않았다. `동적`은 로컬 countdown을 포함한다. 온라인의 동적 N=0이다. 자식 최초 시각은 자신의 출생 이후 관측 또는 가정한 상속에서 결정한 라운드이며, 사망한 프로세스가 현재 분포에 들어가지 않으므로 lifetime 결과도 JSON에 별도로 두었다.')
p()
rows=[]
for m,mm in T['maps'].items():
 for co,label in [('ours-online','우리'),('elite-top10','상위권'),('local-F','W1 F'),('local-S','W1 S')]:
  if co not in mm['cohorts']:continue
  s=sup(co,200,m)['fullSymmetry'];rows.append([m,label,mm['truth']['symmetry'],f"{s['teamDecidedN']}/{s['teamN']}",num(med(s['teamFirstRounds'])),f"{s['teamDynamicDecidedN']}/{s['teamDynamicN']}" if s['teamDynamicN'] else 'N=0',num(med(s['teamDynamicFirstRounds']))])
table(['지도/배치','집단','정답 대칭','정적 결정/팀 N','최초 r 중앙값(결정 N)','동적 결정/팀 N','동적 최초 r 중앙값(결정 N)'],rows)
p('[해석] 빈 지도/중복 대칭을 가진 지형은 정적 시야가 넓어져도 유형을 하나로 결정하지 못한다. 실제 countdown의 무작위 동기화가 이때 구별 정보를 제공할 수 있다. 미결정 중에는 남은 후보를 유지해야 하며, 가장 흔한 회전 후보를 고르는 것은 f-bin용 추정일 뿐 확정이 아니다. 시작점 집합이 특정 반사에 고정되는 경우에는 대칭 유형 결정 전에도 적 시작점이 같을 수 있으나, 그 추가 추론의 별도 성능 측정 N=0이다.')
p()
p('## 4. 샘 분류와 spawn 시도율')
p()
p('[사실] 마지막 관측이 r−1이고 그때 예상한 만료가 정확히 r이며, r에서 새 만료가 뒤로 이동할 때만 새 gap 한 개를 기록한다. 중간에 시야가 끊긴 만료 차이는 여러 gap의 합일 수 있어 표본에서 제외했다. 평균≤12 분류에 필요한 표본 gate를 1/2/4/8로 각각 채점했다. 정밀도=TP/(TP+FP), 재현율=TP/지도 전체 샘 수, 관측 샘 재현율은 TP/관측한 정답 샘 수다. 시도율 오차는 표본 수 gate를 통과한 타일에서 |추정λ/정답λ−1|의 평균이다. 빠른 샘만 먼저 gate를 통과하는 선택 편향이 있다.')
p()
rows=[]
for r in [5,10,20,25,30,50,100,200]:
 c=cp('local-v12',r)
 for gate in ['4','8']:
  v=c['rates'][gate];rows.append([r,gate,v['N'],f"{v['tp']}/{v['fp']}/{v['fn']}",pct(v['precision'],2),pct(v['recall']),pct(v['seenFountainRecall']),f"{pct(v['rateRelativeMAE'])} (타일·편 N={v['rateN']})",v['resetSamples']])
table(['r','최소 gap N','로컬 팀·경기 N','TP/FP/FN','정밀도','전체 샘 재현율','관측 샘 재현율','시도율 상대 MAE','중복 포함 리셋 표본 N'],rows)
p('[사실] 아래는 한 프로세스의 gap gate=4 결과다. 상속은 표본까지 완전히 상속한다는 상한, 리셋 패킷은 실제 송신/도착 경로에서 타일별 더 큰 표본 수의 요약으로 대체했다. 서로 겹칠 수 있는 요약을 더하지 않았다. 정답 샘 수는 프로세스별 전체 지도 샘 수를 분모로 합산한다.')
p()
rows=[]
for r in [10,25,50,100,200]:
 for mo,label in [('own','직접'),('inherited','상속 상한'),('packet','리셋 패킷'),('legacy','기존 max-gap 휴리스틱')]:
  v=sup('local-v12',r)['rates'][mo];rows.append([r,label,v['N'],f"{v['tp']}/{v['fp']}",pct(v['precision'],2),pct(v['recall']),pct(v['rateRelativeMAE'])])
table(['r','모델','프로세스 N','TP/FP','정밀도','전체 샘 재현율','시도율 상대 MAE'],rows)
p('[사실] 기존 max-gap 휴리스틱은 격리된 만료 차이도 gap으로 다루므로 위 표본 평균 분류와 같은 추정량이 아니다. 주머니 수확의 샘 판단을 그대로 지도 정답 평균≤12로 바꾸어 읽으면 안 된다. 로컬 지도별·집단별 결과, gate1/2, 미러 후 표본을 대칭 상대편에 전파한 결과는 JSON에 있다. 전파 시 같은 리셋을 두 번 세지 않고 더 많은 쪽의 요약을 택했다. 반복 시드·대칭 쌍·여러 관측자는 독립 표본이 아니다.')
p()
p('[해석] 발견과 분류를 분리하는 것이 맞다. spawn support는 첫 시야에서 알지만 샘/시도율은 연속 리셋 표본이 필요하다. gate4는 빠른 샘을 r10부터 일부 정확히 분류했고, 전체 샘 표의 완성을 뜻하지 않는다. μ가 12 경계에 가깝거나 gap 분산이 큰 타일은 표본 수/합을 유지하고 보류할 수 있어야 한다. r10 이후 느린 spawn이 새로 gate를 통과하면 평균 상대 오차가 증가할 수 있다. 새 미지 지도에서 같은 정밀도가 나온다는 검증 N=0이다.')
p()
p('## 5. 2-core와 주머니')
p()
p('[사실] 정답과 부분 그래프에서 서로 다른 이웃 수가 2 미만인 칸을 반복 제거하는 무방향 simple graph 2-core를 계산했다. 주머니 정답은 제거된 칸 전체로, 고립된 칸/나무도 포함한다. 몸 점유는 정적 그래프에서 제외한다. pessimistic은 모르는 간선을 벽으로, optimistic은 열린 간선으로 본다. 관측했으나 짝이 미확정인 포털은 optimistic에서 같은 방향의 가능한 모든 미관측 끝으로 연결해 보수적인 supergraph를 만든다. f-bin용 literal optimistic은 그 포털을 일반 열린 간선처럼 근사한다.')
p()
p('[사실] 단순 optimistic pruning만으로 주머니를 보증하지 않는다. 미관측 포털이 알려진 제거 성분에 붙는 문제를 막기 위해 **제거 성분의 모든 접한 간선이 관측되고 포털 짝도 모두 해결된 성분**만 certified 주머니로 공개한다. known-region P/R의 FN에는 아직 못 본 정답 주머니도 포함하므로 전체 지도에 대한 재현율이다. 표의 미러는 확정 대칭 때만 적용했고, certified에는 포털 짝 및 로컬 countdown을 포함한 확정값을 사용했다.')
p()
rows=[]
for co,label in [('ours-W0-W12','우리 W0–W12'),('elite-top10','상위권')]:
 for r in [10,25,50,100,200]:
  c=cp(co,r);s=sup(co,r)
  for mode,ml in [('optimistic','열림'),('pessimistic','벽'),('certified','닫힌 성분 인증')]:
   v=s['teamCertificates']['mirrored'] if mode=='certified' else c['pockets']['mirrored'][mode]
   rows.append([label,r,ml,v['N'],f"{v['tp']}/{v['fp']}/{v['fn']}",pct(v['precision']),pct(v['recall'])])
table(['집단','r','미지 간선 모델+미러','팀·경기 N','TP/FP/FN','정밀도','전체 주머니 재현율'],rows)
p('[사실] 아래 한 프로세스의 그래프는 매 편·시점에서 SHA256 순서 첫 살아 있는 프로세스 하나를 뽑고 그 편의 살아 있는 수로 가중했다. 한 시점당 표본 N과 대표하는 프로세스 수를 함께 적었다. 실제 전수 프로세스 그래프 P/R이 아니라 가중 표본 추정이다. 상속 모형/원시 그래프/모든 지도 결과는 JSON에 있다.')
p()
rows=[]
for co,label in [('ours-W0-W12','우리'),('elite-top10','상위권')]:
 for r in [10,25,50,200]:
  v=sup(co,r)['processGeometry']['own']['mirrored'];q=v['certified'];rows.append([label,r,q['sampleProcessN'],q['weightedProcessN'],pct(q['precision']),pct(q['recall']),pct(v['pessimistic']['precision']),pct(v['frontier']['accuracy'])])
table(['집단','r','표본 프로세스 N','가중 대표 수','인증 주머니 P','인증 주머니 R','벽 모델 주머니 P','같은 표본 f-bin 정확도'],rows)
p('[해석] 비관 그래프에서 남은 2-core는 이미 확인한 간선만으로 만든 순환 구조라는 양성 근거다. 반대로 비관 그래프에서 제거되었다고 주머니로 단정하면 표의 FP를 만든다. 인증된 제거 성분을 주머니 표에 올리고 나머지는 unknown으로 두는 편이 맞다. 수확 가능한 입구·왕복 경로·먹이 공급까지 검증한 N=0이므로 “non-core”를 곧바로 안전한 수확 주머니로 번역하지 않는다. 포털이 숨은 상태의 정답률 100%는 이 표본의 경험적 값과 인증 조건을 구분해야 한다.')
p()
p('## 6. frontier bins와 영토')
p()
p('[사실] 최초 아군 **머리** 집합을 BFS 출발점으로 삼고, 확정 대칭의 미러를 적 출발점으로 삼았다. 미결정 때는 남은 후보 중 회전, y축 반사, x축 반사 순서로 골랐다. f=dOwn/(dOwn+dEnemy), bin=min(4,floor(5f)); 양편 모두 도달 불가인 칸은 별도 bin5다. 미지 간선은 일반 열린 간선, 짝 미해결 포털은 일반 간선 근사이며, 확정 미러는 알려진 칸을 확장한다. 정확도 분모는 알려진/미러 추정된 칸의 칸·편 수다. 원래 몸 전체를 seed로 삼는 기존 표와의 비교는 `bodyReferenceAccuracy`, 정답 적 시작점을 준 상한은 `oracleEnemyAccuracy`다.')
p()
p('[사실] 아래 계산은 각 프로세스에 **최초 아군 머리 전체**가 알려졌다는 추가 가정을 쓴다. 팀 합집합에는 자연스러운 상한이나, 자식의 출생 위치를 최초 출발점으로 쓰면 이 가정이 성립하지 않는다. 단일 프로세스에 자기 계보의 최초 머리 하나만 주는 별도 오차도 JSON `processGeometry.*.rootOnlyFrontier`에 있다. 시작점 방송/전체 계보 census를 실제 구현한 N=0이다.')
p()
rows=[]
for co,label in CO:
 for r in [10,25,50,100,200]:
  c=cp(co,r);v=c['frontier']['mirrored'];rows.append([label,r,v['gameN'],v['N'],pct(c['frontier']['raw']['accuracy']),pct(v['accuracy']),f"{pct(v['spawnAccuracy'])} (N={v['spawnN']})",f"{pct(v['fountainAccuracy'])} (N={v['fountainN']})",pct(v['bodyReferenceAccuracy'])])
table(['집단','r','팀·경기 N','미러 포함 칸·편 N','원시 정확도','미러 정확도','spawn 정확도','샘 정확도','몸 seed 정답 표와 일치'],rows)
p('[사실] 지도·배치별 f-bin 미러 정확도다. 각 셀은 **정확도 (채점 칸·편 N)**이다. 팀·경기 N은 위 지도별 시야 표와 같고, 모르는 지역 자체의 정확도를 평가한 수치가 아니다.')
p()
rows=[]
for m,mm in T['maps'].items():
 for co,label in [('ours-online','우리'),('elite-top10','상위권'),('local-F','W1 F'),('local-S','W1 S')]:
  if co not in mm['cohorts']:continue
  cells=[]
  for r in [10,25,50]:
   v=mm['cohorts'][co]['checkpoints'][str(r)]['frontier']['mirrored'];cells.append(f"{pct(v['accuracy'])} (N={v['N']:,})")
  rows.append([m,label,mm['cohorts'][co]['N'],*cells])
table(['지도/배치','집단','팀·경기 N','r10','r25','r50'],rows)
p('[해석] 대칭·적 시작점만 맞아도 거리 표가 완성되는 것은 아니다. 아직 안 본 벽과 포털 짝이 경로 길이를 바꾸고, spawn/샘 위치의 bin 오차가 전체 칸보다 클 수 있다. 초기 영토/전선은 부드러운 추정으로 쓰고, 경계 부근·미해결 포털 근처에는 낮은 확신을 남겨야 한다. 거리 표의 갱신은 대칭 확정, 새 벽, 포털 짝 해결 때 필요하다. bin0–4 일치만으로 영역 공급량·가운데 배치 비율이 정확하다고 보증한 N=0이다.')
p()
p('## 7. W3 설계와 초기 탐색 권고')
p()
p('[해석] r10에는 관측 칸·간선·spawn support와 일부 대칭 확정, 매우 빠른 샘의 최소 표본, 이미 닫힌 주머니를 쓸 수 있다. r25에는 확정 대칭의 복사와 인증 주머니의 범위가 커진다. r50에도 프로세스별 전체 지도·느린 spawn 평균·전체 frontier 표가 모두 믿을 만하다는 결론은 나오지 않는다. 고정 라운드에 완성 플래그를 켜기보다 테이블별 증거 조건을 둔다. 관련 시점별 N과 정확도는 앞 표 및 마지막 표에 적었다.')
p()
p('[해석] 최초 머리 좌표/계보와 대칭 후보를 작은 음파 요약에 먼저 넣고, 그 다음 포털 짝 좌표와 리셋 표본 수·합·출처를 전달하는 순서를 권한다. 표본 요약끼리 겹치면 합산하지 말고 같은 origin의 더 많은 누적 표본으로 대체하거나 reset 사건 좌표·시각으로 중복을 제거한다. 단순 타일 패킷은 손실되어도 한 칸씩 복구할 수 있다. 창 전체의 다중 조각은 짧은 접촉에서 거의 완성되지 않았다. 이 순서의 실제 봇 성능 검증 N=0이고, 측정한 필드 이득은 2절의 조건부 패킷 표에 한정된다.')
p()
p('[사실] 토러스에서 인접 한 칸 이동으로 새 7×7 창이 추가할 수 있는 칸은 최대 7, 겹치지 않는 포털 이동/새끼 첫 창은 최대 49다(7×7 창의 기하 N=1 정의; 이 상한은 관측 전파 비용을 포함하지 않는다). 포털 시야가 너머로 이어지는 것은 아니다. 포털 양끝/ID를 봐야 정적 거리 그래프를 연결할 수 있다.')
p()
p('[해석] 첫 탐색은 이미 본 지역의 반복보다 서로 겹치지 않는 창을 얻는 짧은 경로에 가치를 주고, 대칭 후보끼리 예상이 다른 칸·미확정 포털의 반대 끝·주머니 목 주위 간선을 우선 후보로 삼는다. 샘 후보에 머무는 프로세스는 리셋 직전/직후 연속 창을 유지해야 gap을 얻는다. 지역마다 새끼를 내는 탐색은 팀 합집합을 넓히지만 지식을 새끼에게 전달할 연락 경로도 필요하다. 신규 탐색 경로를 실행한 N=0이며, 로컬 흉내 상대의 승패·길이를 채택 근거로 사용하지 않았다.')
p()
p('## 독립 재계산과 한계')
p()
rows=[]
for name,label in [('verification-heads.json','머리/창/상속/음파'),('verification-geometry.json','별도 그래프·2-core·BFS'),('verification-rates.json','별도 리셋 달력·표본 추정'),('verification-aggregate.json','전체 집계 재계산')]:
 f=O/name
 if f.exists():
  v=json.loads(f.read_text());n=v.get('games',v.get('counts',{}).get('games'));comparison=v.get('comparisonN',v.get('counts',{}));rows.append([f'[{label}](../../exp/observe/{name})',n,str(comparison),v['mismatchN']])
 else:raise RuntimeError('required verification missing: '+name)
table(['검증 파일','경기 N','비교 N/종류','불일치 N'],rows)
vr=json.loads((O/'verification-rates.json').read_text())
p(f"[사실] countdown 달력의 리셋 사건 N={vr['resetCalendarEventN']:,}에서 예상 만료와 사건 시각 불일치 N={vr['resetCalendarMismatchN']}. r200까지 우리 관측 리셋을 지도·시드·라운드·대칭 orbit으로 중복 제거한 수는 N={vr['uniqueOurObservedOrbitResetsAcrossRepeatedSeedRunsBy200']:,}, 독립 지도·시드 조건 N={vr['seedMapConditionN']}. 머리 검증은 mass-ledger/action 재현과 다른 replay dragonUpdate/split 경로를 썼고, 공식 파서로 음파를 대조한 경기 N=26이다. 그래프 검증은 source/map/기록 layout 층의 대표 N=40경기, 그래프 N=4,320이며 전 경기의 모든 그래프를 독립 재계산한 것은 아니다. 패킷 창·spawn 비트맵은 고정 실제 접촉에서 별도 재현했고, 보강된 포털 대칭/인증/리셋 패킷의 모든 세부 항목을 독립 파서로 전수 재구현한 N=0이다.")
p()
p('[해석] 관측 상한과 조건부 공유 가능성은 측정했지만, 그 지식을 가진 새 봇의 행동·CPU·승률을 검증하지 않았다(N=0). 미래의 미지 지도는 표본의 크기·대칭·gap 분포와 다를 수 있다. 따라서 다음 표의 라운드는 이 자료에서 관측된 사용 가능 시점이며, W3 공개 조건은 관측 증거로 판단한다.')
p()
p('[사실] 집계 전 JSON에 동결한 참고 기준은 전체 위치 coverage≥80%, 샘 P≥95%·전체 R≥80%, 주머니 P≥95%·전체 R≥80%, known-region f-bin 정확도≥90%다. 아래는 이 평균/누적 기준을 처음 통과한 측정 시점이며, 미래 지도에 대한 보장이나 각 편의 통과율이 아니다. —는 r200까지 측정 시점에서 통과하지 못했다는 뜻이다.')
p()
rows=[]
for co,label in CO:
 def first(fn):return next((r for r in [0,5,10,20,25,30,50,100,200] if fn(r)),None)
 cover=first(lambda r:cp(co,r)['coverage']['mean']>=.8)
 fountain=first(lambda r:(cp(co,r)['rates']['4']['precision'] or 0)>=.95 and (cp(co,r)['rates']['4']['recall'] or 0)>=.8)
 pocket=first(lambda r:(sup(co,r)['teamCertificates']['mirrored']['precision'] or 0)>=.95 and (sup(co,r)['teamCertificates']['mirrored']['recall'] or 0)>=.8)
 frontier=first(lambda r:cp(co,r)['frontier']['mirrored']['accuracy']>=.9)
 rows.append([label,T['globalCohorts'][co]['N'],cover,fountain if co.startswith('local') else 'N=0',pocket,frontier])
table(['집단','팀·경기 N','원시 위치 80% 최초 r','샘 P95/R80 최초 r','인증 주머니 P95/R80 최초 r','f-bin 90% 최초 r'],rows)
p()
p('## table → reliable from round … with accuracy … under assumption …')
p()
u10,u25,u50=(cp('ours-W0-W12',r) for r in [10,25,50])
s10,s25,s50=(sup('ours-W0-W12',r) for r in [10,25,50])
rate=cp('local-v12',50)['rates']['4'];pc=s50['teamCertificates']['mirrored']
table(['table','reliable from round','accuracy / N','under assumption'],[
 ['관측 타일·간선 / spawn support','첫 관측(r0 가능)', '그 칸은 입력의 정확한 정보; 머리/창 검증 경기 N=2,460, 불일치 0','unknown 표시 유지; 포털 너머 시야 없음; spawn gap과 구분'],
 ['팀 전체 관측 표','r10 / r25 / r50에서도 부분 표',f"커버리지 {pct(u10['coverage']['mean'])} / {pct(u25['coverage']['mean'])} / {pct(u50['coverage']['mean'])}; 각 N=1,050",'완전 공유 상한; 한 프로세스에 자동 전달되지 않음'],
 ['대칭 / 적 시작점','후보가 하나인 각자의 최초 r',f"팀 r10 {s10['fullSymmetry']['teamDecidedN']}/1,050, r25 {s25['fullSymmetry']['teamDecidedN']}/1,050, r50 {s50['fullSymmetry']['teamDecidedN']}/1,050 확정; 정답 제거 0",'간선/spawn/관측 포털 짝; 온라인 countdown 추가 속도 N=0; 최초 머리 전체 공유'],
 ['프로세스 정적 표','r50에서도 부분 표',f"own {pct(u50['process']['all']['own']['coverage']['mean'])}; own 미러 {pct(s50['fullSymmetry']['own']['mirroredCoverageMean'])}; 살아 있는 N={u50['process']['N']}",'직접 창만 누적; 부모 메모리 자동 상속 없음'],
 ['샘 후보 / spawn 시도율','연속 reset 4개 이후; 빠른 일부는 r10',f"로컬 r50 P={pct(rate['precision'],2)}, 전체 R={pct(rate['recall'])}, λ MAE={pct(rate['rateRelativeMAE'])}; 팀 N=240, rate 타일·편 N={rate['rateN']}",'μ≤12; 엄격한 연속 관측; 선택된 빠른 spawn; 온라인 실제 추정 N=0'],
 ['확인된 포털 짝','양끝의 대응 ID를 본 순간','새 포털 공유 프로토콜 추가 효과 측정 N=0; 지형 독립 검증 N=40경기','같은 ID 숫자를 대칭 정답 비교에 그대로 고정하지 않음; 미해결 짝 unknown'],
 ['2-core 양성 부분','확인된 간선만으로 순환이 생긴 순간','개념상 known subgraph의 core⊆true core; 독립 그래프 N=4,320/불일치 0','무방향 simple graph; 관측한 포털 짝만 연결; 전체 core recall 보장 없음'],
 ['인증 주머니','제거 성분의 모든 접한 간선·포털 짝 확인 후',f"우리 r50 미러 P={pct(pc['precision'])}, R={pct(pc['recall'])}; TP/FP/FN={pc['tp']}/{pc['fp']}/{pc['fn']}, N=1,050",'닫힌 성분 조건; non-core와 수확 가능한 주머니를 구분'],
 ['frontier / territory bins','r10부터 추정, r25/r50에도 보류 가능',f"우리 미러 정확도 r10 {pct(u10['frontier']['mirrored']['accuracy'])}, r25 {pct(u25['frontier']['mirrored']['accuracy'])}, r50 {pct(u50['frontier']['mirrored']['accuracy'])}; 팀 N=1,050; r50 칸·편 N={u50['frontier']['mirrored']['N']}",'최초 머리 전체·대칭 추정, 미지 간선 열림; 알려진 칸에서만 채점; 포털/새 벽 갱신'],
 ['spawn/샘 그룹의 전체 공급량','고정 r10/r25/r50 보장 없음','온라인 reset 정확도 N=0; 로컬 분류/속도 오차는 위 표','발견 coverage와 분류 confidence를 별도 저장; 미관측 공급량을 0으로 확정하지 않음']])
(ROOT/'research/observations/observability.md').write_text('\n'.join(lines),encoding='utf8')
print('report written',len(lines),'lines',len('\n'.join(lines).encode()),'bytes')
