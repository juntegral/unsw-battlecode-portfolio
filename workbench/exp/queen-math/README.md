# 여왕 규칙 수학 — 오프라인 재현

규칙 원문: `rules/`, unswbc 1.2.3. 공식 엔진을 가져오거나 실행하지 않는다.
네트워크·봇·대전·멀티프로세싱 없이 Python 표준 라이브러리로만 계산한다.
작은 방은 실제 지도 안에 kelp로 둘러싸인 부분 그래프로 해석한다.

```sh
nice -n 10 python3 exp/queen-math/analyze.py
nice -n 10 python3 exp/queen-math/verify.py
```

두 명령은 순서대로 실행한다. 분석기는 표와 열거 결과를 다시 쓰며,
보고서와 `SUMMARY.txt`를 쓰지 않는다. 현재 샌드박스는 `nice`의 우선순위
변경을 거부하지만 명령 자체는 실행한다. 스크립트는 자식 프로세스를 만들지 않는다.

| 파일 | 내용 |
|---|---|
| `model.py` | 규칙 텍스트의 충돌·지불·먹기·죽음·분열·id 순서 모델 |
| `analyze.py` | 표 생성, 유한 상태 열거, 모든 구성적 증인 검증 |
| `verify.py` | 모델을 import하지 않는 별도 구현으로 원자료 재검산 |
| `render_tables.py` | 보고서의 표시된 이동/드롭 표만 CSV에서 갱신 |
| `source-manifest.json` | 읽은 규칙 파일의 SHA-256; 검산 시 변경 여부 확인 |
| `reach.csv` | L2–40 무료·유료 이동·한 턴/두 턴 사거리·직접 머리/분열 계보의 안전 거리 |
| `reach-envelopes.json` | 모든 L의 맨해튼 외피; 특정 몸 배치의 정확한 집합이 아님 |
| `reach-union-over-bodies.json` | 초기 몸/방향 전체에 대한 정확한 합집합, 무료 이동 집합도 포함 |
| `reach-exact-small.json`, `reach-pictures.txt` | 동쪽을 향한 직선 몸 L2–8의 정확한 도달 집합 |
| `drops.csv`, `L3-stream.csv` | L2–40 드롭 효율, L3 한 마리의 3걸음 수확 모델 |
| `fixtures.json` | 분열, 진주, 먹이기, 과속, 포털, L4–40의 한/두 라운드 분열 암살 경계 증인 |
| `rooms-3x3.json`, `rooms-pictures.txt` | 연결된 3×3 부분방과 모든 몸 상태; 안전 반복 동작·그림 |
| `rectangles.json`, `cycle.csv` | 1–4변 직사각형 최대 순환, L2–40 최소 순환 |
| `rectangle-constructions.json` | 일반 구성법으로 만든 2–10변 81개 순환과 두 바퀴 검증 |
| `vault-phases.csv`, `vault-witnesses.json` | C4–50, Q2–40의 몸통 입구 차단 상태 열거 |
| `vault-pictures.txt` | 안전한 72개 순환/길이의 실제 2×n 방 그림과 동작 |
| `vault-minimal.csv`, `vault-verification.json` | 최소 순환의 금고 가능 여부와 실제 2×5/Q9 검증 |
| `vault-growth-counterexample.json` | 빈 칸의 진주 하나로 기존 금고가 자기 충돌하는 반례 |
| `assassination.json` | 열린 공간·복도·방 입구의 여왕 선택과 사냥꾼 대응 증인 |
| `backup-EV.csv`, `backup-model.json` | 조건부 승률을 가정한 일반 기대값 모델 |
| `backup-concrete.csv`, `backup-concrete.json` | 실제 길이·세 타이브레이크를 모두 열거한 작은 기대값 모델 |
| `backup-feed-everything.csv`, `backup-feed-everything.json` | 여왕만 남기는 정책의 조기 전멸까지 포함한 비교 |
| `verification.json`, `independent-verification.json` | 분석 assertion 결과와 독립 구현 검산 결과 |
| `run.log`, `verify.log` | 실행 로그 |
| `SUMMARY.txt` | 전체 검증 뒤 마지막에 작성하는 12줄 요약 |

최종 해설은 `research/observations/queen-mechanics.md`다. **자기 충돌 없는
순환**, **몸 배치에서 살아남을 수 있는 상태**, **외부 공격에도 안전한 금고**는
서로 다른 성질이다. `rooms`의 safe는 첫 두 성질에 관한 것이며,
외부 공격까지 막는 성질은 `vault`의 명시된 불변식에만 붙인다.

모델 범위: sonar 전파·진주 난수·500라운드 경기는 실행하지 않는다.
Sonar와 시야의 설계 제약은 보고서에서 원문으로 도출한다. 모델의 포털은
주어진 방향 간선의 목적지를 바꾸는 작은 증인만 다루며, 지도 파일을 해석하지 않는다.
게임 종료는 `score()`의 r500 비교와 보고서의 조기 전멸 설명으로 구분한다.
