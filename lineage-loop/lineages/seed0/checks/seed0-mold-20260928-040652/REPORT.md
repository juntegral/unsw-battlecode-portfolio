# seed0 거푸집 서버 확인 — 2026-09-28

- 제출: seed0-mold-20260928-040652, #9109 / v22. 서버 빌드 성공, 확인 시 active.
- 원본: ~/01. Project/개인 프로젝트/unsw-arena-seed/lineages/seed0/candidate
- 제출 ZIP: 28,004 bytes, 10 files. 서버에서 다시 받은 ZIP 및 각 파일 SHA256이 스냅숏과 일치.
- 이번 세션에서 제출 1회, 비랭크 경기 1판만 요청. 정식 채택/ready/로컬 bot 승격은 수행하지 않음.

## 요청한 1판

- 경기 #416934, Default, JJYA(A, #9109) vs risq-v(B, #8214). 요청 전 ELO 1510 / 1509.
- **승리**, 500라운드 종료. 비랭크라 이 경기 ELO 변화 0.

| 지표 | 거푸집 | risq-v |
|---|---:|---:|
| 최종 최장 길이 | 14 | 6 |
| 최종 생존 드래곤 | 6 | 37 |
| 최종 총 길이 | 29 | 128 |
| 분열 | 18 | 97 |
| 사망 | 16 | 64 |

- 거푸집 턴/행동: 2510/2510, instruction exceeded: 0.
- 거푸집 CPU points: 중앙값 10238348, p95 19919659, 최대 30829151.
- 서버 경기 log: null, hostFailures: 0, attempts: 1.
- 전체 총 길이는 상대가 컸지만 최장 드래곤 길이에서 앞서 승리. 한 지도·한 진영·한 상대의 1판으로 일반 성능 개선을 판단할 수 없음.

## 함께 발생한 별도 경기

확인 시 이 제출본 누적은 4승 0무 7패. 이 세션이 요청한 위 1판 외에 같은 계정 명의로 별도 랭크 시리즈 두 개가 요청되어 있음. 발생 주체나 자동화 경로는 확인하지 않음.

- #416897–416901: PoGang, 2승 3패.
- #416902–416906: Lon Co Kiri, 1승 4패.

## 근거

- manifest.json, source/, submission.zip, server-submission.zip
- upload.json, submissions-9109.json, battle-request.json
- battles-416934.json, battle-416934.replay, events-416934.jsonl.gz
- replay-result.json, summary.json
- battles-416897.json, battles-416902.json (별도 경기 조회만 수행)
