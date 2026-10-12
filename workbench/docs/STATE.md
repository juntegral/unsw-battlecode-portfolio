# 현재 상태 (2026-10-02 저녁, 새 팀 합류 전 정리)

지금 상태를 요약한 파일이다. 근거는 `DECISIONS.md`, `versions/v1.8/VERSION.md`, `research/observations/`에 있다.

## 1. 팀과 일정
- **팀 변경:**
  - 사용자는 기존 팀 "Teto, run!"(id 583)을 떠났다.
  - 10-02에 **C--**와 새 팀을 꾸리기로 했다. C--는 id 852의 C++ 솔로 팀이고, 옛 래더 ELO는 약 1,780–1,945였다.
  - API 키 파일과 C--의 주축 코드를 받을 예정이다.
- **팀 규칙:** 한 팀에 7일 넘게 있으면 떠날 수 없다.
- **퀄리파이어:** 제출 마감은 2026-10-09 15:00 KST다. 처음 보는 커스텀 지도에서 bo7 단일 탈락으로 치르고, 규칙은 1.2.3(여왕)이다.
- **워크플로우는 일시정지 상태다.** 10-02 14:14에 Claude 주간 사용량 때문에 멈췄고, 2시간 루프 cron은 지웠다. 재개는 사용자가 정한다.

## 2. 우리 봇 v1.8 (`versions/v1.8/bot`)
- **켠 것:**
  - 지도 인식 끔(QUAL_NO_MAPID).
  - 여왕 보호 묶음 Q2a–Q2j: 분열·탈출 제한, 안전한 첫 걸음, 사냥, 방, 상자 금지, 정지, 신중, 호위.
  - 여왕 번호 탐지. 진영과 무관하다.
  - Q1과 Q1b2: 여왕 먹이기와 막판 합류.
  - Q2BOX: 여왕의 마지막 출구를 막지 않는다.
  - BODYX: 다중 이동의 몸 전이를 1.2.3대로 계산한다.
  - BODYMEM2: 자기 몸 기억을 1.2.3대로 갱신하고, 미관측 진주에 기대는 유료 걸음은 거부한다.
  - FREECOST2: 유료 걸음에만 값을 매긴다.
- **시험 뒤 끈 것:**
  - Q1B_BACKUP, Q1C_SIGHT, Q2SIGHT.
  - BODYMEM: 아군 기억 부분이 해로웠다.
  - FREECOST: FREECOST2로 대체했다.
  - Q2D_FREESTEP, Q2DQ, Q2K_PACK.
- **업로드용 zip:** `bot/unsw-swarm-v1.8-8333e66-server-upload-nocomments.zip`. 주석을 지웠고, WASM이 원본과 같으며, 업로드 시험은 2/2를 통과했다. 아직 업로드하지 않았다.
- **위험:** FREECOST2 뒤 CPU 최대가 69M이다(이전 32M). 80M 경보 아래지만, 큰 미지 지도에서 확인해야 한다.
- **미해결:**
  - Around UNSW B에서 여왕이 r6에 죽는다.
  - 보이는 공격자에게 들이받힌다(29/38).
  - 지형에 갇힌다(28, 그중 16은 시작부터).
  - 초기에 관측하지 못한 몸을 기억하는 문제.
- **약점:** 미지 지도에서의 거시(탐색과 접근, 전환)가 약하다. 퍼지기와 개척지 기능이 지도 표에 기대고 있어서, 인식을 끄면 분열만 남는다.

## 3. 다른 봇에도 쓸 수 있는 도구
| 도구 | 하는 일 |
|---|---|
| `tools/firstdiv.js` | on/off 짝의 첫 갈림 인과 점검 |
| `tools/mass_ledger.js`, `tools/top_features.js` | 기보 재구성과 특징 추출. `UNSW_RULES=123`을 쓰고, 스프린트까지의 기보는 110 |
| `tools/replay2map.js` | 기보에서 지도 복원 |
| `exp/v1/smoke_upload.js` | 업로드 시험 2판 |
| `exp/<작업>/build.py` 형식 | 끈 빌드의 WASM 해시 동일성 확인 |
| `tools/codex/codex-build.sh`, `codex-analyze.sh` | Codex 개발·분석 실행기. 지시문은 `research/briefs/codex-build-template.md` |
| `tools/online.js` | 읽기 전용 API 명령. 키는 환경변수로만 넘긴다 |

## 4. 문서
- `docs/PHILOSOPHY.md`, `docs/PHILOSOPHY.en.md`: 방법론.
- `docs/pitch/what-i-bring.md`, `docs/pitch/sprint-notes.md`: 팀 합류용 영어 소개 문서.
- `docs/pitch/zitian-analysis.en.md`: zitian 스프린트 21판 분석(내부용).
- `research/observations/`: queen-mechanics, queen-early, queen-rammed, sprint-commentary, cutlery, duels, general-principles, observability 등.

## 5. 새 팀으로 재개할 때
1. **키:**
   - 새 팀 키 파일은 도구만 읽는다. 화면, 파일, 커밋, 로그에 남기지 않는다.
   - `tools/online.js`의 `OUR_TEAM = 583`을 새 팀 id로 바꾼다.
   - launchd 수집기 `com.jun.unsw-heuristic.collect-top`은 지금 401로 실패하고 있다. 새 키가 들어가면 자동으로 다시 수집한다.
2. **C-- 코드:** 별도 폴더에 원본 그대로 둔다. 변경은 스위치 규율로만 한다(기본 끔, 끈 빌드의 해시가 같아야 함). 가장 먼저 1.2.3 몸 전이(BODYX 사례)와 여왕 안전을 점검한다.
3. **v1.8에서 옮길 후보:** BODYX와 BODYMEM2(정확성 수정), Q2BOX, 여왕 번호 탐지, Q1 먹이기. 옮기기 전에 C-- 구조에 맞는지 판면으로 확인한다.
