# W8 지도 생성기와 기제 점검 큐

Node 표준 라이브러리만 사용한다. 저장소 루트에서 실행한다. 커밋·온라인 신청·업로드는 하지 않는다.

```sh
node tools/mapgen/census.js
node tools/mapgen/validate.js --existing
node tools/mapgen/mapgen.js --seed 20261001
node tools/mapgen/validate.js
node tools/mapgen/check.js
node tools/mapgen/smoke.js
```

`census.json`을 먼저 쓰고 생성한다. `smoke.js`는 끝에서 manifest·연구 보고서·12줄 SUMMARY를 갱신한다. 게임 없이 보고서만 갱신하려면 `node tools/mapgen/report.js`를 쓴다. SUMMARY는 보고서 생성의 마지막 쓰기다. 재생성은 기존 게임과 같은 지도가 아닐 수 있으므로 seed와 mapSha256를 대조한다.

## 정적 검증

`validate.js`는 저장된 파일을 다시 파싱한다. MAP 선두·차원·정수·개수·중복·타일 gap·교대 변 행의 padding/범위·portal 두 endpoint와 방향/대칭 대응·몸 인접/겹침·양 팀 대칭을 검사한다. wrap의 동/남 별칭은 북/서 canonical 변으로 합친다. SYMMETRY 이름은 거울 축이다: x=상하, y=좌우, xy=180도.

기존 38개는 형식·대칭 검증을 모두 통과한다. 기존 지도는 연결성을 검사해 기록하되, 실제로 있는 분리 구역을 형식 오류로 간주하지 않는다. 생성 지도 기본 모드는 **전 칸 연결**을 강제한다. 현재 gen_X_04는 원본 Portals의 시작 주변을 보존하면서 4개 작은 성분이 남아 엄격 모드에서 실패한다. 양 팀의 모든 시작은 큰 성분에 있다. 이 예외를 정상 통과로 바꾸지 않았다.

인식 함정은 시작 머리마다 toroidal Manhattan 반경 6을 보존한다. TILE gap, 양 끝이 영역 안인 변, 원본 포털 쌍, 몸 접합 변, 시작 드래곤 순서를 유지한다. Autarky/Portals/PD 등은 이 보존 영역이 넓어 전체 40% 변경이 불가능하다. 기본값은 **가변 영역 변·생성 support 40% 이상 변경**이며 전체 비율도 manifest에 기록한다. 근처 보존과 Portals 전 칸 연결 조건 충돌은 보고서에 명시했다.

## 권장 smoke 실행기

```sh
node tools/mapgen/smoke.js
# 선택한 지도만 실행 (X이면 양 좌석, 나머지는 A)
node tools/mapgen/smoke.js --only gen_S_01,gen_M_02,gen_X_09
```

한 번에 한 판만 `nice -n 10 tools/unswbc run … --sandbox --seed 1 --no-logs --no-draw`로 실행한다. A는 versions/v1.6/bot, B는 bots/proxy4_king이며 X는 우리 B도 추가한다. 매 판 직전 pgrep로 기계 전체 `unswbc-clean.py run` 수 <6 및 statfs로 여유 ≥21GiB를 확인한다. pgrep 조회 실패를 0으로 간주하지 않고 중단한다. 게임 수/디스크 조건만 일시 부족하면 15초마다 재확인한다.

총 48판이다. 시작한 판은 오류가 있더라도 자동 재실행하지 않는다(지도당 한 판 요구). 미실행 blocked 행은 재개할 수 있다. `smoke.lock`은 실행기 중복을 막으며 정상 종료 때 지운다. 비정상 종료 후에는 소유 PID와 게임이 끝났는지 확인한 뒤 lock을 처리한다. 로그·replay·공식 runner 빌드 캐시는 `exp/mapgen/` 아래에 둔다. 상대 봇 소스는 직접 읽지 않는다.

`smoke.jsonl`에는 로딩·완료, 우리 오류/timeout, 팀별 CPU max, 양쪽 map 태그와 엔진, 우리 오인식 태그를 저장한다. 로컬 판 ID는 `mapgen:<지도>:<좌석>:1`이다. CPU의 M 표시는 runner가 0.1M 단위로 반올림한 값이며 없으면 null이다. 미실행 판의 관측값도 null이다. 승패·최종 길이 열이나 평가 표를 만들지 않는다. 원본 runner.log/replay는 진단을 위해 유지하며 runner 자체의 결과 문장이 로그에 있을 수 있다.

## 기존 큐를 수정하지 않고 연결하기

`exp/v14/runq14.js`는 spec의 `maps` 경로와 `only` 목록을 지원한다. 다음 spec을 **허용 경로에** 저장하면 기존 코드를 그대로 쓸 수 있다.

```json
[
  {
    "bot": "versions/v1.6/bot",
    "out": "exp/mapgen/future-mechanism",
    "maps": "maps/generated",
    "only": ["gen_S_01", "gen_M_02"],
    "opps": ["proxy4_king"],
    "sides": ["A", "B"],
    "seeds": [1]
  }
]
```

```sh
node exp/v14/runq14.js exp/mapgen/future-spec.json --jobs 1 --cap 6
```

`tools/eval.js`도 경로 옵션만 주면 된다.

```sh
node tools/eval.js --bot versions/v1.6/bot --label mapgen-future \
  --out exp/mapgen/future-eval --maps maps/generated \
  --opps proxy4_king --seeds 1 --jobs 1
```

두 기존 도구는 승패/길이 필드를 쓰므로 **이번 W8 smoke에는 사용하지 않는다**. 또 eval.js는 전체 판 수 gate가 없고 디스크 gate가 20GiB이므로, 자원 조건을 그대로 강제하려면 위 `smoke.js`를 쓴다. 기존 runq14도 pgrep 오류를 0으로 처리하므로 샌드박스 안에서는 사용하지 않는다. 이 명령들은 이후 별도로 승인된 기제 실험을 연결하는 방법이며 이번 smoke를 중복 실행하라는 뜻이 아니다.

판면 확인은 기존 도구를 그대로 쓴다.

```sh
node eval/board.js exp/mapgen/games/gen_M_02_A_1/game.replay gen_M_02 a A 0,25,50,100
```

## 지표와 한계

공급·2-core·중앙 정의는 `research/observations/general-principles.md` 및 `exp/spatial/lib.js`에서 가져왔다. 중앙은 시작 **몸 전체**로 BFS, 시작 팀 간 거리는 **머리**로 BFS다. 통로 폭은 수평/수직 열린 직선 구간의 작은 값이라는 기하 proxy로 정의했다. 포털은 일반 인접 변으로 세지 않고 실제 이동 목적지로 연결한다. 전체 파일의 상세 gap/너비 분포는 census와 manifest에 있다.

범위 판정은 고유 기존 지도의 지표별 min/max이며 분포 적합이나 joint envelope가 아니다. maze/thin·인식 함정 일부는 명시적으로 범위 밖이다. 생성 seed를 바꿔도 지도 가족·시작 설계는 그대로이므로 독립적인 organiser 표본으로 해석하지 않는다. 생성 지도가 로딩되고 게임이 끝났다는 사실만으로 runtime 규칙의 발동과 의도한 상태 변화를 증명하지 않는다.
