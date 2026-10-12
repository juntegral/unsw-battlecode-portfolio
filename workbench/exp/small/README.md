# 작은 지도 분석

보고서: [small-maps.md](../../research/observations/small-maps.md). 전수 타임라인 N=194는 [INDEX.md](INDEX.md)에 있다.

`tables.json`은 첫 산출물이다. 완료된 전체 표는 2026-10-01 13:25 KST에 처음 작성했고, 그 뒤 rank 누락과 미수집 elite 메타데이터를 확인해 갱신했다. 분석 모집단은 2,129판이다. `SUMMARY.txt`는 보고서·재집계·시각 QA를 마친 뒤 마지막에 작성한다.

기보 다운로드, 온라인 요청, 업로드, 새 로컬 경기, 봇 수정, 커밋은 하지 않았다. 쓰기는 이 디렉터리와 지정한 보고서 파일에만 했다. W7/DECISIONS는 사용자 지정 쓰기 범위 밖이므로 이 디렉터리에 실행 기록을 남겼다.

기존 동결 모집단으로 재현:

```sh
nice -n 10 node exp/small/extract.js
nice -n 10 node exp/small/aggregate.js
nice -n 10 python3 exp/small/verify.py
nice -n 10 node exp/small/key_recount.js
nice -n 10 python3 exp/small/key_compare.py
nice -n 10 node exp/small/support.js
nice -n 10 node exp/small/deep.js
nice -n 10 python3 exp/small/draw.py
nice -n 10 python3 exp/small/make_report.py
nice -n 10 python3 exp/small/finalize.py
```

`setup.js`는 현재 인덱스로 모집단을 다시 동결하고 census 표를 쓴다. 기존 결과를 재현할 때는 저장된 `population.json`을 사용한다. `rows.jsonl`은 append-only이며 key별 최신 schemaVersion=2를 읽는다. 부모가 worker 두 개를 띄우고, worker별 메모리 상한은 1,200 MB다. 재집계·정독은 순차 실행한다. 10% 메모리/21 GiB 디스크 gate는 `resource.jsonl`에 기록된다. 이 샌드박스에서 nice의 setpriority가 거절된 사실도 보고서에 명시했다.

재구성 두 가지:

- 주 집계: mass_ledger의 이동/돌진/분열/충돌/진주 원장. `turnStart`에서 상태를 읽는다.
- 독립 집계: replay의 `dragonUpdate` 머리/꼬리 및 `dragonSplit` 몸 목록을 따른다. d3/d8/시야/free와 사망/접촉을 따로 계산한다. `verify.py`가 이 증거를 별도 Python 코드로 재합산한다.

공유 binary decoder의 공식 viewer 비교 N=3판은 `decoder-qa.json`, 전체 수지와 대조는 `verification.json`, 우리 194판의 마지막 의사결정·머리/몸 구분을 새로 재구성한 대조는 `key-verification.json`, 자원/링크/표/타임라인 QA는 `qa.json`이다. 동일 팀·seed의 반복을 독립 실험으로 취급하지 않는다.

`ourGames`는 매 라운드 수/길이와 분열·사망·충돌 및 마지막 20라운드를 담는다. 마지막 20라운드 행동은 우리 팀만 표에 넣고, 상대 전체 행동은 `raw/*.json.gz`에 보존했다. 모든 99,839 머리 접촉의 개별 증거는 `headons.jsonl`이다. 큰 raw/row/head-on 캐시는 Git에서 제외했다.

그림은 `boards.json`에 적힌 `node eval/board.js <replay> <header map name> a <team> <rounds>`의 ASCII를 PNG로 렌더했다. 소형 번들의 header는 `Arena`, `Colosseum`, `Default Small`이며 파일 basename과 다를 수 있다. 세 PNG를 직접 열어 판면·글자·좌표를 확인했다.

가설은 관측에서 얻은 다음 실험의 후보다. 적용 실험 N=0이며, 원자료의 승자/패자 차이를 개선 효과로 바꾸지 않는다.
