# QSIGHT 분석 인계 — 게임 없는 BUILD

사전 기준은 `versions/v1.8/VERSION.md` §15다. 승패·총 길이로 채택하지 않는다. `Q2SIGHT_ON=false`가 제출 줄 기본값이며 on/off는 다른 기본값이 같다. `bot-base`는 작업 시작 원본이다. 분석 전에 아래 검사로 소스·지도·명세가 실행 시점에 바뀌지 않았는지 확인한다.

```sh
python3 exp/qsight/validate.py
```

## 조정자 실행

샌드박스 밖에서 실행한다. BUILD에서는 실행하지 않았다.

```sh
node exp/qsight/runq.js exp/qsight/spec.json --jobs 3 --cap 6
```

runq14 형식의 명세다. 기존 runq14는 경로 상대와 CPU를 지원하지 않으므로 제공한 runner를 쓴다(Q1c runner 사본, `tools/unswbc123` 고정, exit0만 재개 성공으로 인정). nice10·기계 전체6판·21GiB·재개 규칙은 유지한다. on/off 22지도 × 양편 × king/hunter × 시드1 =176판, 생성 M_07 8판, 동일성 Trophy/Australia/L_03 × 양편 × king의 두 빌드12판, 총196판이다. 22지도 세트의 스프린트7/번들5는 원 파일과 해시 대조했다. 동일성 Australia는 실제 `maps/sprint/`에서 읽는다. 시드2는 200판 제한 밖이다. `bot-compat`은 Q1c 동시 켬 합성 검사 전용이며 게임 명세에 없다.

## 원자료·완료·오류·CPU

```sh
UNSW_RULES=123 nice -n 10 node exp/qsight/analyze.js > exp/qsight/analysis.txt
```

`analysis.json`의 `summary.expectedGames=196`, loadedGames196, pairs92, identityKeys6, missing0을 확인한다. rows.jsonl의 키별 마지막 exit0/G있음/error·botProblem없음 줄만 결과로 쓴다. 실패 이력은 historyErrors에 따로 남는다. `checks`의 모든 값0, errors0을 요구한다. 재실행이 성공해도 오류 이력을 숨기지 않는다. `cpu`에는 양 팀이 함께 있으므로 우리 side의 max만 읽어 최대·80M 이상 경보·100M 이상 한도·누락 수를 지도/편/상대별로 낸다. 빈 CPU 줄은 통과가 아니라 미확인이다. 결과 파일의 won/G/longest를 채택 기준으로 쓰지 않는다.

## (a) 직접 목격·송신·여왕 수신·지연

`analyze.js`는 `tools/top_features.js`의 loader와 `tools/mass_ledger.js`의 `perGame(..., {rules:'123'})`를 쓴다. 실제 `sonarPing`과 다음 `turnStart`를 연결해 inbox를 복원한다. 여왕 id는 replay의 초기 팀별 최저 id로 구한다. 기존 `exp/q2/rammed.js`, `queendeath.js`는 A=id0을 가정하므로 id가 바뀐 판에는 그대로 쓰지 않는다.

- `qst<enemy>,<sighting-round>,<tile>,<reported-L>,<ray>,<queen-last-tile>`: 보내기로 한 보고. indicator는 행동 전이므로 실제 죽어 광선이0개인 기회도 분모에 남긴다.
- `qsn<received>,<accepted>`: 이번 여왕 inbox에서 유효한 보고 수와 엄격히 새 보고 채택 수.
- `qsr<enemy>,<sighting-round>,<tile>,<reported-L>,<sender>`: 여왕 cache의 모든 기록. 원 목격부터 나이≤3만 유지한다. 같은 라운드/오래된 보고로 TTL이 늘지 않는다. 현재 직접 보이는 적의 기록은 cache에 남아도 위협 가격에서 제외된다.
- `qsp<raw-reported-price-step1>,<raw-reported-price-step2>`: 선택 MOVE에 보고장이 부과한 순수 가격. SPLIT/경로 없는 RETURN은0이다. 이것만으로 후보의 총 점수·안전성을 주장하지 않는다.

`decode.js`가 새 패킷의 정확한 decoder다. whitening XOR `0x9E3779B97F4A7C15`, 상위→하위 magic6(0x21) / sender11 / enemy11 / round7 / x6 / y6 / len7 / team1 / reserved1(0) / CRC8 이다. shift58/47/36/29/23/17/10/9/8/0, CRC seed0x93·poly0x07·low checksum byte를 제외한 7bytes를 하위부터 처리한다. 기존 format2/Q1c와 별개이며 legacy decoder는 거부한다. 127라운드 wrap과 3라운드 만료를 검사한다.

`sets.on[key].signals`에서 실제 직접 보이는 머리/좌표/원 시각/송신자 일치를 점검한다. 실제 길이와 보고 길이를 별도로 보고해 partial-view의 과소/과대 추정 수를 센다. L≥9 미만 보고는 `queen-last-tile`까지 World가 알고 있던 간선 BFS의 거리≤M인지 원 관측을 복원해 확인한다. 초기 몸/포털/거울 간선 기억도 필요하다. ground truth 거리와 내부 관측 거리의 차이는 오류와 구분한다. 보고 우선순위는 `distance-M` 최소→길이 최대→id 최소다. 아군 여왕 머리의 소식은 headSeen≤20이다. 여왕 소식이 없으면 송신하지 않는다.

`signals.reports`의 실제 광선 hit와 `receipts`를 연결한다. 송신 기회/생존해 실제 발사/여왕 몸에 hit/수신/새 채택의 각 분모와 수를 적는다. 물리적으로 여왕에 도착한 모든 유효 보고는 다음 여왕 차례(지연1라운드 이내)에 읽히고 qsn/qsr에 맞아야 한다. 같은 라운드 또는 더 신선한 기존 증거 때문에 미채택된 것은 전달 실패와 구분한다. 신호가 아군 조각에 닿아도 재전송하지 않는다. 켈프·몸·미지 포털·자기 몸 굴절·송신자 사망을 실패 원인별로 분리한다. 기회0은 미확인이다.

## (b) 첫걸음 회피·실제 판면

raw reported field는 보고 원 위치에서 known-edge BFS로 `free=ceil(L/4)*(age+1)`, `reach=free+L-2`를 쓴다. d≤free이면45, free<d≤reach이면27, 그 밖0이다. 몸은 막지 않고 알려진 kelp는 막으며 미지 일반 간선은 열린 것으로 본다. 알려진 포털은 건너고 출구를 모르는 포털은 확장하지 않는다. direct visible enemy id는 제외한다. 여러 보고 및 기존 queenFirst와 max를 취한다. 기존 DFS의 매 걸음 항을 바꾸지 않았다. report 원 시점=현재이면 M이고, age>0은 무진주 다중턴 보수적 상한이다. 진주·분열 계보 사거리는 포함하지 않는다.

`sets.on[key].queenTurns`에서 (1) 수신 직후 선택이 달라진 판, (2) 선택 첫걸음이 보고 도달 밖인 판, (3) 보고 도달 안 선택/무대안/split 판, (4) 새 또는 조기 사망 판을 전수 목록으로 만든다. on/off는 금세 판면이 달라지므로 같은 key/round만으로 인과를 주장하지 않는다. 같은 관측 입력에 Q2SIGHT만 켜고 끈 Planner를 합성 호출해 후보/선택 차이를 확인한다(게임 추가 없음). 직접 보이는 적으로 보고장이 무시되는 경우도 따로 본다. 빌드의 `fixtures.cpp`는 같은 입력에서 queenFirst의 경계값27 대0 및 기존 직접 위협≥90의 max 보존을 확인한다. 실판에서 모든 대안이 도달 안이면 회피 실패와 구분하지만 성공 분모에는 넣지 않는다. 미관측 간선·자기 몸의 불확실성은 공개한다.

최소 두 가지 변화(송신→수신/회피)와 모든 안전 회귀의 실제 판면을 뽑는다. 예시 명령의 key/round/x/y는 analysis.json의 실제 값으로 대체한다.

```sh
UNSW_RULES=123 node exp/v16/board.js exp/qsight/on/games/bot-hunter_trophy_A_1/game.replay A 100 12 12 10 trophy a
UNSW_RULES=123 node exp/v16/board.js exp/qsight/off/games/bot-hunter_trophy_A_1/game.replay A 100 12 12 10 trophy a
```

이 도구는 라운드 시작 판면이며 켈프선을 그리지 않는다. 위험 행동 직전의 정확한 id순서 판면은 mass_ledger의 turn/action/death 훅으로 몸·머리·walls·portal 간선을 같이 출력한다. 마지막 여왕 차례 및 hunter 차례, 송신 전/후, 수신 전/후의 상태를 비교한다. 라운드 시작 사진만으로 순간 합법성·시야를 판정하지 않는다.

## (c) 시야 밖 사냥꾼 사망과 다른 사인

`pairs`는92짝(22지도88+생성4)이다. 주 집계는 원22지도의88짝이며 생성4는 별도 보고한다. `death.outsideHunter`는 rammed 사망에서 실제 rammer가 여왕의 마지막 자기 차례 snapshot에 있고 L≥9, torus Chebyshev>3일 때만 true다. rammer가 snapshot에 없으면 unknown으로 두며 시야 밖으로 임의 처리하지 않는다. 마지막 차례 snapshot 길이와 충돌 시 길이는 별도로 유지한다. 모든 rammed 수, 시야 밖 rammed 수, 그중 L≥9 수, 전체 rammed 중 몫을 off/on 및 지도/편/상대별로 내고 분모0은 null로 둔다. 몫만 낮아져도 전체 사망 증가로 인한 희석이면 목적 개선으로 보지 않는다.

다른 사망 원인별 합계·키별 새 사망·더 이른 사망을 보고하고 pairs의 newDeath/earlierDeath 전수 판면을 확인한다. 바깥 사냥꾼 감소와 함께 다른 원인 증가가0이어야 안전 기준을 충족한다. Autarky/PD/Slithery 시작 주머니의 early-death와 Around UNSW B r6도 따로 보고한다. 별도의 여왕 생존 count는 안전 보조 자료이며 승패 게이트는 없다. 신호만 발동하고 사망 감소 기회가 없으면 사망 기준은 미확인이다.

## off 동일성·CPU·BUILD 검증

```sh
UNSW_RULES=123 node tools/fingerprint.js exp/qsight/id-base/games/proxy4_king_trophy_A_1/game.replay exp/qsight/id-off/games/proxy4_king_trophy_A_1/game.replay
```

위처럼6키 모두 기존 기보의 hash를 비교한다. `--same`/`--run`은 새 게임을 시작하므로 쓰지 않는다. analyze의 identitySame6도 요구한다. fingerprint에는 sonarPing/message 이벤트가 포함된다. `compile-check.json`의 base/off SHA·WASM 바이트 동일을 확인하고 파일 자체를 `validate.py`로 재검산한다. CPU는 실판 rows의 우리 side 수치를 사용한다.

재현 가능한 BUILD 검사(게임0):

```sh
~/.aside/runtime/bin/python3 exp/qsight/build.py
python3 exp/qsight/check-fixtures.py
python3 exp/qsight/validate.py
```

compile과 합성 검사는 실판 지연·회피·사망·CPU 통과를 뜻하지 않는다. 분석 결과는 `exp/qsight/RESULT.md`에 실제 date 시각·각 분모·판면·원자료·미확인·위험을 적고, 스위치 채택 결정은 조정자에게 넘긴다.
