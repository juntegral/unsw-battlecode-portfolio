분석 기록: 2026-10-09T05:52:19+09:00

입력: one8-c2-old/M1493890.replay, M1493891.replay. 소스: data/online/smoke/one8-bot/main.cpp. 원본 불변.

판독: tools/ladder_replay.py의 scan, replay reader 재사용. tq2_chase.py의 Geo는 AST로 최상위 main 실행만 제외하고 import하여 사용.

기보 수치는 *-scan.json, 여왕 차례·전체 상태는 *-detail.json, 매 차례 행동은 *-turns.json. queen IDs는 각각 A0/B1과 A1/B0.

r302 MATE_UNPIN 재계산은 전체 시야 안에 몸이 있는 #150와 #1137을 원본 위험 함수의 이동/충돌 규칙으로 평가했다. 외부 상태 추정이나 봇 실행은 하지 않았다. 각 깊이의 출구는 unpin-check.json. 이 결과만으로 UNPIN이 최초 선택을 바꿨는지는 알 수 없다.

r302 진입 전 판면(queen center 54,11):

```text
+-+-+-+-+ + + +
 . . .|*|. . . 
+ + + + + + + +
 . a .|.|. . a 
+ + + + + + + +
 a a .|*|a a a 
+ + + + + + + +
 A a A Q . A a 
+ + + + + + + +
 . . a q . a aP
+ + + + + + +-+
 . . a q q .|*P
+ + + + + + + +
 . . A a . .|* 
+ + + + + + +-+
```

Portals 접근 계산은 이동/분열/사망 사건마다 실시; 방향성 지형 그래프의 역방향 BFS를 상대 여왕 머리에서 수행. 999999는 미도달 표식이다. 신체 무시라는 낙관적 조건에서도 도달 불가. Slithery는 두 여왕이 동시에 사후/생존인 구간이 없어 검사수가 0이다.
