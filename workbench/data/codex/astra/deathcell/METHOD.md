# 재현과 범위 [M]

[M] 분석자 deathcell. 시작 시 실제 시계 2026-10-09 01:38:16 KST, 결과 검증 시각 02:06:29 KST. ASTRA-COMMON과 지정 브리프를 따랐다. 산출은 이 폴더에만 썼다. 공용 DECISIONS/WORKQUEUE는 브리프의 쓰기 범위 때문에 수정하지 않았다.

[M] source inventory는 label_report.directory_inventory를 가져와 사용했다. 동일 game id는 한 번만 센다. one1–one5 라벨 폴더 150판과 그 밖의 실제 해당 제출 41판 = 191판. 각 제출: 20850/20880/20910/20941/20980. 20905는 REMOTE-LOG.md:1307의 c5455-w1 시험 제출이라 20판 별도 보고한다. 20835/20366 10판도 제외한다. 폴더가 아니라 기보 root의 bot id로 판정한다. inventory.json은 파일 목록, coverage.json은 제외 id 및 중복 목록이다. 새로운 수집 자료에 재실행하면 표본 수가 달라질 수 있다.

[M] scoreboard.load_replay와 기존 o1_scan.scan을 가져와 사용했다. 사망 원인/길이/분열/유료 걸음/섭취는 원래 계수기에 대조했고, 추가 스캔은 진입 사건과 현재 몸·개인 시야·벽/포털 거리를 붙였다. 모든 191판 양편에서 길이 장부와 최종 머릿수/길이/여왕이 일치했다. 행별 동등성 검사는 scan.py의 assert를 확인한다.

[M] 공격 거리 계산은 실제 이동 방향별 포털 착지와 벽을 포함한 그래프의 역방향 BFS이다. 몸과 길이별 질주 예산은 무시한다. 거리 3은 행동 횟수가 아니라 격자 이동 단계 수다. 맨해튼 거리 민감도는 summary.json에도 있다. 같은 좌표도 잠깐 막힌 몸 통로일 수 있으며, 성분 한 칸만이 즉시 지형적 외통의 명확한 부분집합이다.

[M] cells.csv/jsonl의 count, rounds, 각 dragon id/L/Q, last-step portal/pearl, 열린 변 성분 진입 portal/round, 진입 뒤 남은 성분 진주 수, 마지막 칸 진입 src/dest, 분열 나이를 모두 기록했다. near_enemy_companions는 동일 칸에서 죽었지만 적 거리 때문에 합계에서 제외한 드래곤이다. 이것으로 Stripes 여왕도 원인 자료에서 보존한다.

[E] ten-cells.md의 kernel은 선택 점수 로그가 아니다. 원래 C++의 room/known_room/pocket 알고리즘 일부를 Python으로 다시 계산했으며, 정확한 bot tail_index, home_closed, 타이머와 음파 상태는 복원하지 않았다. 이 재계산을 실제 변수 값이라고 인용하지 않는다. portal_dead/closed 누락 자체와 관련 상수는 코드 사실이고, 실제 선택에 그 분기가 우세했는지는 추정이다.

[M] audit.jsonl은 큰 후보군(관측된 출구가 모두 자기 몸에 막힌 진입), audit-narrow.jsonl은 그중 벽/새 목만인 확실한 외통, audit-card.jsonl은 다른 현재 합법 이동까지 존재하는 최종 카드의 집합이다. report.md 및 summary.json의 card는 최종 집합이다. 다른 이동의 적 위협까지 안전하다고 판정하지 않았으므로 후속 생존은 미검증이다. 유료 걸음 뒤 추가 외통을 완전 검출했다는 주장도 하지 않는다.

[M] 재현 순서(저장소 루트, 새 대전 없이 기보만 읽음):

```sh
python3 -B data/codex/astra/deathcell/scan.py
python3 -B data/codex/astra/deathcell/audit.py
python3 -B data/codex/astra/deathcell/narrow.py
python3 -B data/codex/astra/deathcell/alternatives.py
python3 -B data/codex/astra/deathcell/access.py
python3 -B data/codex/astra/deathcell/details.py
python3 -B data/codex/astra/deathcell/summarize.py
```

[M] 실제로는 nice -n 10으로 분석 실행을 요청했으나 샌드박스가 setpriority를 거부했다. 분석은 정상 실행됐다. 네트워크·게시·대전·업로드·실전 코드 변경·컴파일은 하지 않았다. 큰 JSONL은 분석 캐시이며 커밋하지 않았다.
