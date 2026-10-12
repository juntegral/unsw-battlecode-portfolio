# unsw-heuristic

UNSW Battlecode(심해 드래곤 게임) 봇을 **사용자의 가설·아이디어에서 출발해** 사람과 Claude가 함께 개선하는 휴리스틱 연구 저장소다. 무인 웨이브 루프(`../unsw-arena`)와 분리되어 있다. 여기서 더 완성된 봇이 나오면, 루프는 그 봇에서 출발해 연장하는 데 쓴다. 루프는 2026-09-29부터 일시정지 상태다.

## 작업 방식
1. **관측:** 로그를 수집하고 분석한다. 온라인 대전 기록(상위권 상대 포함), 로컬 평가 리플레이, 로컬 상대의 행동이 대상이다. 특히 우리가 진 경기에서 상대에게 배운다("당하고 배우기").
2. **가설:** 사용자의 아이디어(`research/`)와 관측 사실에서 가설을 세운다.
3. **검증:** 같은 시드로 짝지어 비교하고, 채택은 새 시드 확인으로 판정한다. 판별 한계는 `research/MEASUREMENT.md`에 있다.
4. **기록:** 관측 사실과 실험 결과를 `research/`에 남긴다. 사실과 해석을 구분해서 쓴다.

## 규칙
- **로컬 상대(`bots/`):** 실행과 분석을 모두 허용한다. 리플레이, 행동, 음파 메시지 해독을 포함한다.
- **원격 작업은 전면 허용한다.** API 키(`~/Downloads/api.txt`) 사용, 제출 업로드, 대전 신청, 기록 다운로드가 모두 가능하다.
  - 키는 화면 출력, 파일, 커밋, 로그에 남기지 않는다. 필요한 자식 프로세스에 환경변수로만 넘긴다.
- **대전 티켓은 아낀다.** 대전을 신청할 때는 승패와 관계없이 리더보드 최상위권 팀을 우선 상대로 고른다.
  - 모든 원격 작업(업로드, 대전 신청, 다운로드)은 `data/online/REMOTE-LOG.md`에 날짜, 대상, 목적, 사용 티켓을 기록한다.
- **로컬 경기:** 동시 6판까지 돌린다. 판정 엔진이 CPU 점수로 재기 때문에 부하가 결과를 바꾸지 않는다. 디스크 여유가 20GB 미만이면 새 경기를 시작하지 않는다.

## 구조
| 경로 | 내용 |
|---|---|
| `bot/` | 현재 최선. g4-r4(제출 10365)에 세 가지를 더한 것이다: 긴 드래곤 탈출 질주(`cand-avoid6`), 포털 활용(`cand-portal1`), 10마리 판본 Prisoners Dilemma의 막다른 칸 먼저 먹기(`cand-pd10e`). 2026-09-30 06:40 채택, 제출 12142. 이력은 `research/experiments/online-tests.md`에 있다. |
| `exp/` | 후보 봇과 평가 결과. `exp/eval-r1/`은 현재 최선의 기준 평가 160판이다. |
| `bots/` | 로컬 상대 4종(소스): replay_rules_v8, archetype_swarm, archetype_hunter, h2. |
| `maps/` | 온라인 지도 10개(`online-20260927`, a판)와 번들 지도. `variants/`는 서버에서 관측된 두 번째 판본이다: Devil·Queen Of Spades·Schooltime·Slithery Fight의 b판과 Prisoners Dilemma 10마리판. 서버는 이 다섯 지도를 반반 낸다. `server-b/`는 b판 평가 묶음이다(로컬 평가는 시드 1을 a판, 시드 2를 b판으로 돌린다). |
| `rules/` | 공식 규칙서 저장본. |
| `tools/` | `unswbc`(공식 1.1.0 판정, 해시 기반 깨끗한 빌드), `eval.js`(표준 벤치마크), `viewer.js`(리플레이 파서), `export_replay.js`. |
| `data/online/` | 온라인 대전 기록(2026-09-27 연습 경기 273판, 우리 팀 id 583). git에는 넣지 않는다. |
| `data/top/` | 레이팅 1900 이상 팀끼리의 대전 리플레이(`<대전>/<경기>.replay.gz`, 목록 `index.jsonl`). launchd가 5분마다 `tools/collect_top.js`로 모은다(설정 사본 `docs/launchd/`, 로그 `data/top/collect.log`). |
| `research/` | 연구 의제, 측정 한계, 관측 기록, 실험 기록. |
| `docs/` | 온라인 API 사용법 등 운영 문서. |

## 명령
- 표준 벤치마크 160판: `node tools/eval.js --bot <봇 폴더> --label <이름> --seeds 1,2 --jobs 6` (결과는 `exp/<이름>/`).
- 한 판: `tools/unswbc run maps/online-20260927/<지도>.map <봇A> <봇B> --sandbox --seed 1 -o game.replay`
- 리플레이 읽기: `require('./tools/replay.js').load(<.replay 또는 .replay.gz 파일>)`는 사건 목록(`events`)과 결과(`result`)를 준다. 음파 사건에는 실제 64비트 메시지(`value64`)와 멈춘 곳(`hitKind`)이 붙는다.
  - `tools/viewer.js`의 `load(<폴더>)`는 옛 형식으로 읽어서 음파 값이 모두 0이다. 평가 도구용으로만 남겨 둔다.
- 상위권 경기 특징: `node tools/top_features.js`가 `data/top/features.jsonl`에 경기당 한 줄을 덧붙인다(스키마 `docs/top_features.md`).
- 상위권 대전 수집(수동 실행): `node tools/collect_top.js --min-elo 1900` 또는 `--top 20`. 티켓을 쓰지 않는다.
- 온라인 조회·다운로드·대전 신청: `node tools/online.js <명령>`(사용법 `docs/online.md`). 신청은 `--confirm --expect-active <제출 id>`가 없으면 계획과 비용만 출력한다.
- 온라인 웨이브(한 시간 창의 시험 세트)와 그 피드백: `node tools/online_wave.js <봇 폴더|active:<제출 id>> <이름> "<설명>" <세트> --vs <지난 세트>`. 올리기, 상위 6팀과 DEV 팀 상대 70판, 받기, 적용 확인 보고서(`research/experiments/mech-<이름>.md`)까지 한다.
- 기보 선별(가장 크게 진 판, 극상위권을 이긴 판, 부류별 최악): `node tools/wave_triage.js <세트> --out <파일.md>`. 동작 지문(동작이 같아야 하는 변경 확인): `node tools/fingerprint.js --same <봇A> <봇B>`. 올린 봇 기록: `research/experiments/VERSIONS.md`.
- 구현 적용 확인(2026-09-30부터 온라인 피드백): `node tools/mech_check.js <세트>[+<세트>] [--vs <세트>] --out <파일.md>`. 봇의 INDICATOR 표식으로 기능마다 발동, 상황, 의도한 결과, 실패 사례를 센다. 승률은 판정에 쓰지 않는다(`research/OVERNIGHT-2026-09-29.md`의 "구현 적용 확인" 절). 새 기능에는 반드시 고유 표식을 단다.
