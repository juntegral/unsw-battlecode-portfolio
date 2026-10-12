# W10 전수 결투 연구

시작: 2026-10-01 18:00:57 KST. 쓰기 범위는 이 폴더와 `research/observations/duels.md`다. 네트워크, 대전, 업로드, 커밋을 하지 않는다.

`setup.js`는 읽을 기보를 게임 id로 중복 제거하고 `tables.json`을 먼저 만든다. `run.js`는 엄격 상위 10팀 대전을 먼저 추출해 `tables-strict.json`과 `tables.json`을 저장하고, 나머지 전수를 추출한 뒤 수집 목록을 한 번 갱신한다. `verify_raw.js`는 별도 머리·꼬리 재구성으로 **전수** 에피소드 id/끝/결과/공격자를 대조한다. `verify.py`는 압축 에피소드에서 표를 독립 재집계한다. `deep.js`는 전체 크기를 정한 뒤 분류별 중심에 가까운 서로 다른 세 경기의 판면을 만든다.

실행 순서:

```sh
nice -n 10 node exp/duel/setup.js
nice -n 10 node exp/duel/run.js
nice -n 10 node --max-old-space-size=1400 exp/duel/verify_raw.js
nice -n 10 node exp/duel/run_tactical.js
nice -n 10 node exp/duel/aggregate_tactical.js
nice -n 10 node exp/duel/aggregate.js full
nice -n 10 python3 exp/duel/verify.py
nice -n 10 node exp/duel/deep.js
nice -n 10 python3 exp/duel/draw.py
nice -n 10 python3 exp/duel/draw_micro.py
nice -n 10 python3 exp/duel/report.py
```

추출은 worker 2개, 원기보 독립 검증은 1개여서 함께 돌려도 worker 최대 3개다. 메모리/디스크는 10게임마다 검사하며 메모리 free 10% 미만 또는 디스크 21GiB 미만에서 중단한다. 프로그램은 실제 nice 값이 10 이상인지 확인한다. 현재 샌드박스에서 nice 변경 호출은 거부되지만 기본 실행 프로세스가 이미 nice=10을 상속한다(직접 `os.getPriority(0)` 확인). 모든 게임별 캐시는 gzip이며 중단 뒤 재개할 수 있다.

`tables.json`의 definitions가 조작적 정의다. episode outcome과 전 경기의 head-to-head contact 수는 다르다. 이미 제삼자가 가까운 접촉은 즉시 third_party이고, 실제 둘만 남은 결투 및 시작 d8 팀 머릿수가 같은 결투는 별도 표다. 질주의 중간 충돌은 action 후, 죽음 사건 전에 추적한다. 관측되는 행동을 미끼 의도로 단정하지 않는다. TRADE 문자열은 **선택한** 후보만 보이며, 생성됐으나 탈락한 kill path 수는 기보로 알 수 없다.

데이터 시점, 누락, stalled 제외, 실제 검증 차이와 가설의 적용 N=0을 최종 보고서에 밝힌다. `SUMMARY.txt`는 모든 확인과 보고서 작성이 끝난 뒤 마지막으로 생성한다.

고립 결투에서 빠지는 군집 싸움은 tactical.js로 직접 머리 충돌·적 몸 충돌·적 근접 벽/자기 사망을 별도로 전수 추출한다. contacts.jsonl.gz와 tactical-tables.json의 N은 episode N과 합하지 않는다. 여기의 head/pearl bait 조건은 마지막 차례의 적 관측·섭취 흔적으로 더 넓고, 의도나 실제 도달 보장을 뜻하지 않는다.

후착 자료 411판의 1무료걸음 모델 검사 오류를 전수 감사로 찾았다. calibrate.js가 ceil(L/4) 모델을 검증하고 해당 캐시만 원자료 독립 episode 재구성과 함께 보정한다. free-policies.json으로 재현하며 원 도구는 수정하지 않았다. 본선/우리 기보는 이 보정에 해당하지 않았다.

최종 재현에서는 cache 감사 뒤 calibrate.js를 실행하고, free-policies.json을 유지한 상태에서 verify_raw.js·aggregate.js·verify.py를 실행한다. custom_comparison.js와 verify_custom.py는 본선 승패별 프로필/능동접촉을 추가한다. report.py는 모든 검증이 0일 때만 보고서와 12줄 SUMMARY를 쓴다. 대표 판면 132개와 판단 시야 132개는 boards/, 직전 결정은 reads/에 있다.
