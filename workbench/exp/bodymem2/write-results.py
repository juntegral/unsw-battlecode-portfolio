from pathlib import Path
import json, collections, subprocess, re
root = Path(__file__).resolve().parents[2]
task = root / 'exp/bodymem2'
A = json.loads((task / 'analysis.json').read_text())
F = json.loads((task / 'firstdiv.json').read_text())
U = json.loads((task / 'audit-summary.json').read_text())
I = json.loads((task / 'audit-input-check.json').read_text())
V = json.loads((task / 'validation.json').read_text())
R = json.loads((task / 'review-analysis.json').read_text())
stamp = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z'], text=True).strip()
assert A['expectedGames'] == 192 and len(A['pairs']) == 84 and len(A['identity']) == 12
assert not A['missing'] and not A['historyErrors']
assert all(i['same'] for i in A['identity'])
assert all(not any(x['checks'].values()) and not x['oracleDrift'] and not x['stepDrift'] and x['cpuMaxM'] is not None and x['cpuMaxM'] < 80 for s in A['sets'].values() for x in s.values())
assert F['summary']['status'] == {'matched':5, 'no_divergence':79}
assert not any(F['summary'][k] for k in ['errors','stateMismatches','firstTurnMismatches','priorInfoDifferences'])
assert not I['totals']['unknownSpawningCountdown'] and not I['totals']['ambiguousFacing']
stats = {}
for arm in ['on','off']:
    rows = list(A['sets'][arm].values())
    stats[arm] = {k:sum(x[k] for x in rows) for k in ['multi','completed','predicted','unknownInput','unseenPearls','rejected','oversprint']}
    stats[arm].update({k:sum(len(x[k]) for x in rows) for k in ['startBodyDrift','endBodyDrift','missingTags','oracleDrift','stepDrift']})
    for field in ['reasons','causes']:
        stats[arm][field] = dict(sum((collections.Counter(x[field]) for x in rows), collections.Counter()))
    stats[arm]['queenCensored'] = sum(x['queenCensored'] for x in rows)
maxcpu = max(x['cpuMaxM'] for s in A['sets'].values() for x in s.values())
table = F['summary']['tables']
assert table['changed']['3']['harm'] <= table['changed']['3']['help']
assert table['queen']['50']['harm'] <= table['queen']['50']['help']
assert not stats['on']['oversprint'] and not stats['on']['causes'].get('sprintDeath',0)
assert stats['on']['startBodyDrift'] < stats['off']['startBodyDrift']
summary = {
    'time':stamp, 'proposal':'ON', 'criterion1':{'fixtures':'PASS','purposeDirection':'PASS','strictFullArrayZero':'FAIL','residualCause':'legacy own portal-chain reconstruction, same-input on/off both drift'},
    'criterion2':'PASS','criterion3':'PASS','criterion4':'PASS','stats':stats,'CPUmaxM':maxcpu,
    'identityN':12,'pairsN':84,'gamesN':192,'changedN':5,'noDivergenceN':79,
    'partialRule':'purpose improves; no new harm at preregistered horizons; identity/CPU/errors pass; strict legacy array counterexample retained'
}
(task / 'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
criteria = '''| 사전 등록 항목 | 값 / N | 판정 |
|---|---|---|
| 1 합성 exact123 전이·제거·다음 LENGTH | ON drift 0/2133, OFF 1802/2133; 지급 2138검사, 가격 변경 0 | PASS |
| 1 단일/분열·아군 범위 보존 | 단일 no-op/원격 경로 fixture 통과; 아군 direct/relay/occupancy/fresh 4/4 동일; 분열 분기·소나·관측/캐시 소스 보존 | PASS(분열은 소스 확인) |
| 1 공통 bodyx 시작 drift 감소 | ON 114/3552(3.209%), OFF 121/3513(3.444%); 84키/arm | PASS(방향) |
| 1 완전 추적 가능한 시작 뒤 다음 관측 전체 배열 drift 0 | 같은 이력 양 World의 공통 exact 시작 다중 이동→다음 관측 621건: ON 1, OFF 3 | **FAIL(엄격한 0)**; ON 1건은 OFF도 같은 입력에서 실패하는 기존 포털 연결 |
| 2 첫 변경 용 k=3 harm <= help | 0 <= 1; N=5; both 2/neither 2/censored 0 | PASS |
| 2 여왕 k=50 harm <= help | 0 <= 0; N=5; both 4/neither 1/censored 0; 갈림 전 양쪽 사망 3, 생존 분모 2 | PASS(위해 게이트; 개선 기회 0) |
| 2 모든 harm 설명·동일 물리 입력 | harm 0/5; 첫 차례/시작/geometry/facing 불일치 0/5, 직전 소나 차이 0/5; 누락/오류 0/84 | PASS; harm 판면/원인 요구 N=0 |
| 3 지급 사망·오류·의도한 실제 변화 | 지급 사망/oversprint ON 0/84, OFF 1/84; 오류/no reply/timeout 0/192; L8/3걸음 L14/미관측 성장·무료/유료 판면과 배열 확인 | PASS |
| 4 OFF/base 동일성 | WASM 530752 bytes·SHA 동일(1/1); 사건·이동·분열·사망·진주·메시지/소나 12/12 동일 | PASS |
| 4 CPU·누락·탐색 | 192/192 CPU 있음, 최대 32.4M <80M; missing/error 0/192; 공통 round:id 깊이 lower/same/higher 40/469491/26, N=469557 | PASS; 갈림 뒤 깊이 차이는 순수 CPU 효과 아님 |
'''
text = f'''# BODYMEM2 ANALYSIS — {stamp}

부분 적용 제안 **ON**. 목적 방향은 개선했고 새 위해·identity/CPU/오류 게이트는 통과했다. 엄격한 전체 배열 drift0 항목은 기존 포털 반례 1건 때문에 FAIL로 그대로 남긴다. 이 제안은 모든 몸 기억 문제가 해결됐다는 판정이 아니다. 스위치/봇/params는 변경하지 않았다.

## 발동·지급·실제 판면

이번 default A/hunter #14 r188의 같은 몸 `[775,774]`에서 ON `N`은 `[891,775]`로 완주, OFF `NW`는 첫 미관측 진주가 없어 두 번째 선지급에서 A 사망한다. 양 원본 이력 및 기존 BODYX 실패 이력의 강제 재생에서 같은 ON/OFF 선택과 즉시 oracle 결과를 확인했다. ON `bodymem2r` 거절 합 70은 발동 하한 문맥이며 채택 게이트가 아니다. raw A 전수는 ON 0건, OFF 이 1건뿐이다; invalid split/무출력/timeout 사인은 0이다. trade/조기 반환은 태그 누락으로 공개하고 독립 ledger의 지급 검사에서 새 A 사망이 없음을 확인했다.

![L8 무료 두 걸음, r146→147](board-free.png)

big_empty A/king #48: r146 EE, L8→8, 실제 배열 `[997,1061,1060,1059,995,996,932,933]`→`[999,998,997,1061,1060,1059,995,996]`; 정상 꼬리가 2칸 전진했다. 라운드 시작 그림의 문자 a가 #48이다.

![포털 다중 이동 뒤 자기 몸 복원, r474→475](board-restore.png)

schooltime B/hunter #355: r474 SSW, L12 무료 한도3, 실제/ON 다음 배열 `[1401,1402,925,865,864,863,923,922,982,981,1041,1040]`. 같은 과거 행동의 OFF는 `[1401,1402,865,864,863,923,922,982,981,1041,1040,1039]`로 원격 중간 머리925를 놓친다. 그림의 b가 #355다. r477의 같은 첫 변경 차례에서 이 기억 차이가 S→E 선택으로 이어지고 두 선택 모두 즉시 완주/k3 생존한다.

추가 실제 판면: [L14 전](board-L14-before.txt)·[후](board-L14-after.txt), [미관측 성장 전](board-growth-before.txt)·[후](board-growth-after.txt), [default 지급 관문](board-payment.txt). L14의 ceil(14/4) 무료 **한도는4**이며 사전 등록의 ‘무료3’은 이번 NNN의 사용 걸음3으로 읽었다: big_empty #115 r306→307, 길이14 유지/꼬리3칸 전진. Portals A/king #27 r412 WS는 미관측 진주2개로 L12→14; ON 직후 보수 예측12는 다음 실제 LENGTH에서 `[306,274,173,174,206,238,270,302,303,335,367,399,398,397]` 전체14칸으로 복원된다. 시작·매 걸음 head/tail·끝 배열은 독립123 oracle와 검산했다. 처음 보는 bundled/generated 및 인식 끈 online/sprint의 대표 무료·유료·완주 배열은 [review-analysis.json](review-analysis.json), 같은 이력 양 World의 시작/직후/다음 배열은 [audit-summary.json](audit-summary.json)·audit/*.snapshots.json에 있다.

## 공통 태그·전체 배열·판정

{criteria}

| 양 arm 공통 측정 | ON (84키) | OFF (84키) |
|---|---:|---:|
| 다중 시도(사망 포함) | 3677 | 3638 |
| 완주 | 3548 | 3504 |
| 시작 bodyx 태그 있음 | 3552 | 3513 |
| 태그 누락(trade/조기 반환; 성공으로 세지 않음) | 125 | 125 |
| 시작 hash drift | 114 | 121 |
| 끝 예측 drift / 완주 | 98/3548 | 104/3504 |
| 끝 drift 중 시작부터 틀림 / 시작 정확·미관측 경로 | 97 / 1 | 103 / 1 |
| unknown 시작 슬롯 태그 / 미관측 경로 태그 | 32 / 17 | 33 / 23 |
| 독립 전체 전이 / 매 걸음 head-tail 검산 불일치 | 0 / 0 | 0 / 0 |

hash만으로 배열 동일을 확정하지 않았다. 모든 drift 키, 부분 시야 성장/포털 및 네 지도군 대표를 양 원본 arm에서 같은 관측·소나·echo·과거 행동으로 강제 재생했다(48키×양 이력=96 replay, 47874 실제 차례; 두 World에 각각 입력). [drift-review.json](drift-review.json)의 114/121 시작 drift 전부 native 배열 hash가 production 태그와 일치했고 실제 전체 배열은 다르다. ON 102/114, OFF 106/121은 첫 관측부터 native 몸이 틀린 id에서 발생했다(초기 긴 몸/직선 추정/unknown과 중첩). 현 차례 unknown 슬롯이 있는 drift는 32/33이며 초기 틀림과 중복되는 범주다.

공통 exact 시작 뒤 다음 관측 621건 중 실제 ON 이력306건은 ON/OFF drift0/1, 실제 OFF 이력315건은1/2다. 두 원본에서 같은 전이를 중복 점검한 진단 분모이며 독립 표본621개로 주장하지 않는다. 남은 1건: OFF Colosseum B/hunter #81 r370 ENN→r371. 두 모델의 시작은 정확하고 ON 직후 몸도 실제17칸과 같으나, 다음 ingest의 기존 자기 관측 chain이 포털 뒤 `[199,215,214,213,229,245,...]`로 재정렬한다. OFF도 같은 입력에서 같은 순서 오류를 낸다. `ingestDragons`의 기존 geo.stepIdx 연결과 `updateOwnBody`의 chain 우선 병합 경로가 보존되어 있어 새 전이 직후 정답을 다시 덮는다. [전 판면](board-legacy-before.txt)·[후 판면](board-legacy-after.txt)와 audit-summary의 전수 배열을 남겼다. 이 반례를 지워 엄격한 drift0을 PASS로 만들지 않았다.

보수적 미관측 섭취 때문에 ON 직후 실제 끝과 다른 5/621건도 남겼다(Portals #27 양 이력, Australia #235 양 이력, OFF #159의 ES). 다섯 건 모두 다음 LENGTH의 전체 배열은 복원된다. 이것은 ON 전용 태그가 아닌 같은 입력 두 World 배열 점검이다. 합성 fixture의2133 전이/2138 지급 검사는 [fixture-check.json](fixture-check.json), 단일 no-op 및 아군4개 동일 snapshot·단일/분열·소나/캐시 소스 보존은 [validation.json](validation.json)에 있다. validation의 `unmeasured`/`realGameCausalGateMeasured:false`는 BUILD 시점 메타데이터이며 이번 실제 측정은 analysis/firstdiv/이 보고서다.

## 첫 변경 결정·즉시 oracle·위해

firstdiv matched5/84, no_divergence79/84. 시작 geometry/몸/진주/facing·첫 실제 차례 모두5/5 동일; 앞선 소나 차이0, start/first-turn mismatch0, 오류/누락0. k=3과 k=50 harm 모두0이므로 harm별 판면·한 줄 원인 요구 대상 N=0(의도적 먹이기 harm도0). k=1과 k=10 용도 harm0/help1이다. 첫 용5개와 같은 R의 추가 용1개를 빠짐없이 아래에 공개한다. k=3은 R+3 시작, k=50은 R+50 시작이며 censored를 생존으로 바꾸지 않는다. 여왕50은 이후 정책 전체 효과다.

| 키 (seed1) | R/id | ON / OFF 선택 | 같은 실제 차례 | ON 즉시 / OFF 즉시 oracle | k1/k3 ON : OFF | 선택 경로 |
|---|---|---|---|---|---|---|
| hunter Colosseum A | 224/#81 | N / NW | 동일 | 둘 다 첫걸음 O(#80 아군 몸) | dead:dead / dead:dead | `bodymem2r3` 지급 관문; 첫 N은 같아 새 사망이 아님 |
| hunter Colosseum B | 106/#25 | E / EN | 동일 | 둘 다 첫걸음 O(#49 아군 몸) | dead:dead / dead:dead | `bodymem2r1` 지급 관문; 첫 E는 같아 새 사망이 아님 |
| hunter default A | 188/#14 | N / NW | 동일 | ON 완주 / OFF 두 번째 지급 A, 남은 `[891,775]` | alive:dead / alive:dead | `bodymem2r3`; 보지 못한 첫 진주에 의존한 지급 제거 |
| hunter schooltime B | 477/#355 | E / S | 동일 | 둘 다 완주 | alive:alive / alive:alive | r474 SSW 원격 중간 머리925 기억 복원 |
| king australia B | 350/#159 | N / ES | 동일 | 둘 다 완주; 실제 ES 첫 원격 진주는 있음 | alive:alive / alive:alive | `bodymem2r1`; 관측 밖 진주에 의존한 후보의 보수 거절 |
| king australia B (추가) | 350/#332 | S / N | **불일치** | 각 실제 판면에서는 둘 다 완주 | alive:alive / alive:alive | #159 뒤 같은 R의 정책/기억 변화; 최초 동일 입력 게이트 분모에 넣지 않음 |

old/new 표식·모든 실제 차례의 몸/진주·완주 몸/사망 걸음·사인 및 k1/k3 fate는 [review-analysis.json](review-analysis.json)의12행(6용×양 이력), raw death/상대 행동/아군 몸은 [firstdiv.json](firstdiv.json)에 있다. 첫 용5개의 선택은 양 원본 이력 각각에 두 native 모델을 적용했을 때20/20 재현된다. 추가 #332는 양 실제 차례가 이미 다르고 native 재현도2/4뿐이므로 같은 입력의 선택 이유는 미확인이다. 첫 즉시 사망2건은 OFF도 동일 첫걸음에서 동일 아군 몸에 O 사망; feeding 표식은 없다. 이 둘을 새 위해로 세거나 생존으로 숨기지 않았다.

## 원시 사망·여왕 수명: 문맥만

| 원시 사인 (84키/arm) | ON | OFF |
|---|---:|---:|
| S | 1597 | 1591 |
| W | 5434 | 5421 |
| O | 1352 | 1349 |
| H | 715 | 717 |
| A | 0 | 1 |

| 기제 사인 (84키/arm) | ON | OFF |
|---|---:|---:|
| sac | 1599 | 1592 |
| trap | 6776 | 6758 |
| rammed | 299 | 301 |
| ram | 270 | 268 |
| allyHead | 146 | 148 |
| enemyBody | 8 | 11 |
| sprintDeath | 0 | 1 |
| fault | 0 | 0 |

여왕 수명 ON longer/shorter/same=0/0/84, 차이 합/최소/최대=0/0/0. 양쪽 사망69/84, 관측 종료 생존15/84; 생존은 마지막 round+1의 관측 하한이다. raw 사망 증가나 이후 조기 사망·수명/승패/총길이를 채택 게이트로 쓰지 않았다. 모든84키의 raw/기제 사인과 양쪽 여왕 수명·censoring은 [keywise.tsv](keywise.tsv)에 있다. 아래 수명은 양 방향 전수 문맥이며 `*`는 관측 종료 생존이다.

| 키 | ON 여왕 수명 | OFF 여왕 수명 | 방향 |
|---|---:|---:|---|
'''
for p in A['pairs']:
    text += f"| {p['key']} | {p['queenLifeOn']}{'*' if p['queenCensoredOn'] else ''} | {p['queenLifeOff']}{'*' if p['queenCensoredOff'] else ''} | same |\n"
text += f'''
## 동일성·CPU·오류

OFF/base WASM SHA-256 `{V['compile']['base']['sha256']}`와530752 bytes 동일; Trophy/Around UNSW/M_07 × A/B × king/hunter 사건·소나12/12 동일. 명세192/192의 마지막 clean row 및 기보 있음, 실행 실패 이력/중복/누락/오류0. 독립 ledger10항 모두0(192기보). 우리 팀 CPU192/192 측정·최대{maxcpu}M, 한도80M 경보/100M 미만. 실제 같은 round:id 깊이 lower/same/higher=40/469491/26(N469557), 갈림 이후 비교는 순수 비용 효과로 해석하지 않았다.

같은 관측·강제 과거 action의 native 깊이는 lower/same/higher=0/47324/0(N47324), 태그 없는550차례는 분모 밖이다. native clock/벽시계를 judge points로 쓰지 않았고 같은 입력 production points는 미측정이다. native 입력의 raw `missingCountdown`1154769는 [audit-input-check.json](audit-input-check.json)에서 전부 spawn maxGap0인 정상 `-1`로 대조됐다; 실제 spawning countdown 누락/모호한 facing0. bot·params·spec 동결 source 해시 보존, 게임 실행/커밋/네트워크0. 분석 및 보드에는 UNSW_RULES=123을 적용했다. nice10은 setpriority 거부로 미적용됐다.

**제안: ON — 부분 적용 규칙.** 양 arm 공통 태그 시작 drift 감소와 같은 입력의 지급 실패 회피/원격 머리 복원이 의도한 방향으로 움직였다. 동일성·CPU·오류 통과, 첫 동일 판면에서 용k3 harm0<=help1 및 여왕k50 harm0<=help0이고 새 즉시 사망이 없다. 엄격한 배열0 FAIL은 두 코드 모두 같은 입력에서 실패하는 기존 포털 반례이며 숨기지 않는다. 스위치 채택/변경은 조정자가 한다.
'''
(task / 'RESULT.md').write_text(text)
brief = [
    f'BODYMEM2 ANALYSIS {stamp}; 기존192/192판,84 ON/OFF짝,identity12키; 게임/봇·params 변경/커밋/네트워크0.',
    '기준1 합성 PASS: 배열/LENGTH ON0·OFF1802 drift /2133; 지급2138검사,가격변경0; 단일 no-op·원격 경로/아군4개 동일·분열 소스 보존.',
    '기준1 방향 PASS: 시작 drift ON114/3552·OFF121/3513; 전체 배열0 FAIL: 같은 입력 다음 관측 ON1·OFF3/N621,ON1은 양쪽 기존 포털 오류; multi3677/3638,완주3548/3504,누락태그125/125.',
    '기준2 PASS: firstdiv 용k3 harm/help0/1,N5; 여왕k50 0/0,N5(갈림 때 생존2); harm0,시작/첫차례·직전소나 불일치0; 무변경79/84; 추가용1은 이후 판면 불일치 문맥만.',
    '기준3 PASS: 지급 사망/oversprint ON0·OFF1/N84; 첫 즉시 새 사망0(양쪽 동일 O 사망2); 새 완주/기존 지급 A1; 판면2장 board-free.png·board-restore.png.',
    '기준4 PASS: WASM byte 동일1/1·사건/소나12/12; CPU192/192,max32.4M<80M; 오류/누락/no reply/timeout0; 깊이lower/same/higher40/469491/26,N469557(갈림 뒤 비용 인과 주장 없음).',
    '문맥만: raw S/W/O/H/A ON1597/5434/1352/715/0·OFF1591/5421/1349/717/1; 여왕longer/shorter/same0/0/84,censored15/15,delta0;84키 양방향 keywise.tsv·RESULT.md.',
    '제안: switch ON — 부분 적용: 목적 방향 개선·identity/CPU/오류 통과·새 harm 없음; 엄격한 배열0의 기존 양쪽 포털 반례1은 FAIL로 유지.'
]
assert len(brief) == 8
(task / 'RESULT.txt').write_text('\n'.join(brief)+'\n')
version = root / 'versions/v1.8/VERSION.md'
old = version.read_text()
assert 'BODYMEM2 ANALYSIS 결과 (' not in old
section = max(map(int,re.findall(r'^## (\d+)\.',old,re.M))) + 1
addition = f'''
## {section}. BODYMEM2 ANALYSIS 결과 ({stamp}; 기존 기보만)

**부분 적용 제안 ON.** 지급 실패 OFF1→ON0, 공통 시작 drift121/3513→114/3552와 원격 머리 복원이 의도한 방향으로 움직였다. identity/CPU/오류와 사전 등록 firstdiv 위해 게이트가 통과했다. 엄격한 전체 배열0은 기존 양쪽 포털 반례1건 때문에 FAIL로 유지한다; 봇·params·스위치는 수정하지 않았다.

{criteria}

- **분모/정직성:** ON/OFF multi3677/3638, completed3548/3504, bodyx 시작 태그3552/3513, 누락125/125, unknown 슬롯32/33, 미관측 경로17/23. 끝 drift98/104 중 시작부터 틀림97/103, 시작 정확·미관측 경로1/1. ON 전용 거절70은 하한 문맥이다. 독립 oracle/매 걸음 검산0, ledger10항0(192판); tag 없는 trade를 성공으로 세지 않았다.
- **같은 이력 배열:** 모든 drift 키·부분 시야/포털·네 지도군 대표의96 replay/47874차례를 양 World로 강제 재생했다. 실제 ON 이력306 exact 다중→다음 관측의 drift는 ON/OFF0/1, OFF 이력315는1/2. 남은 ON1은 OFF Colosseum B/hunter #81 r370 ENN→371에서 기존 자기 관측 chain이 정상 직후 몸을 포털 순서로 다시 덮는 양쪽 오류다. 같은 전이의 양 원본 재검사는 독립 표본으로 주장하지 않는다.
- **첫 갈림:** matched5/84·무변경79, 첫 변경5용의 동일 물리 차례 및 직전 소나 검산 통과, 양 실제 이력 native 선택20/20 재현. Colosseum A/#81 N vs NW와 B/#25 E vs EN는 양쪽 같은 첫걸음 아군 몸 O 사망(새 죽음 아님). default A/#14 r188 N 완주 vs NW 두 번째 지급 A; schooltime B/#355 r477은 r474 SSW의 원격 머리925 복원으로 S→E, 양쪽 완주/k3 생존; australia B/king #159 r350 N vs ES는 지급 관문이며 실제 ES도 원격 진주로 완주/k3 생존. 같은 R의 추가 #332는 차례 판면이 이미 다르고 native 재현2/4여서 문맥만 공개했다. harm0이므로 harm 판면/원인 요구 N0, 먹이기 harm0이다. queen k50은 이후 정책 전체 효과다.
- **실제 판면 2장:** [L8 무료2](../../exp/bodymem2/board-free.png), [schooltime 다중/원격 머리 복원](../../exp/bodymem2/board-restore.png). L14 NNN은 사용3걸음/무료한도4(ceil14/4), 실제 길이14·꼬리3 전진이며 ASCII도 남겼다. Portals #27 r412 WS의 미관측 성장 L12→14는 다음 LENGTH 전체 배열로 복원된다. 실제 차례·매 걸음·다음 관측 배열/추가 판면은 [RESULT.md](../../exp/bodymem2/RESULT.md)에 연결했다.
- **양방향 문맥(게이트 아님):** raw S/W/O/H/A ON1597/5434/1352/715/0, OFF1591/5421/1349/717/1. 기제 sac/trap/rammed/ram/allyHead/enemyBody/sprintDeath ON1599/6776/299/270/146/8/0, OFF1592/6758/301/268/148/11/1. 여왕 수명 longer/shorter/same0/0/84, delta합/최소/최대0, 양쪽 관측 종료 생존15/84. 모든84키 양쪽 수명·censoring·사인 전수는 [keywise.tsv](../../exp/bodymem2/keywise.tsv)·RESULT.md다.
- **CPU/입력 한계:** 같은 관측 native 깊이0/47324/0(lower/same/higher), 태그 없음550; production 같은 입력 points는 미측정이며 native clock을 judge clock으로 주장하지 않는다. raw countdown 경고1154769는 모두 spawn maxGap0의 정상-1로 원지도와 대조했고 실제 누락/facing 모호함0. validation의 미측정 표식은 BUILD 메타데이터다. source/지도/spec 보존, 게임/네트워크/커밋0; nice10은 환경 거부로 미적용.

근거: [analysis.json](../../exp/bodymem2/analysis.json), [firstdiv.json](../../exp/bodymem2/firstdiv.json), [audit-summary.json](../../exp/bodymem2/audit-summary.json), [drift-review.json](../../exp/bodymem2/drift-review.json), [RESULT.txt(8줄)](../../exp/bodymem2/RESULT.txt). 엄격한 기존 배열 반례를 숨기지 않고, 목적 개선과 새 위해 없음으로 부분 적용 ON을 제안한다.
'''
version.write_text(old+addition)
print(stamp)
print('VERSION section',section,'RESULT.txt lines',len(brief),'proposal ON')
