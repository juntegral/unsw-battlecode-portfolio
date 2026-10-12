# 인계: meow 팀 작업 시작 (2026-10-03 새벽)

이전 세션(`unsw-arena` 폴더)에서 넘긴 현재 상태다. 오래 남길 사실은 메모리에도 있다(meow-team-repo, local-cleanup, team-change, qualifier-timeline, slay-queen-rules, claude-usage-budget).

## 지금까지
- **팀 이적(10-02):** "Teto, run!"(583)에서 **meow(1119)**로 옮겼다.
  - 팀원은 준싱(사용자), QWQ, Zhe다. QWQ는 봇 개발자로 보이고, 아마 C--다.
- **본 코드:** `battlecode` 폴더다. github.com/forrest-gan2005/battlecode 비공개 레포이고, 우리에게 쓰기 권한이 있다. 작업 규칙은 그 레포의 README를 따른다.
- **옛 레포:** UNSW, unsw-arena, unsw-heuristic는 GitHub 비공개 레포에 push한 뒤 로컬에서 지웠다.
  - 백업 위치: `juntegral/unsw-battlecode-2026`, `juntegral/unsw-heuristic`, `juntegral/unsw-swarm`.
  - 우리 도구는 `unsw-swarm`(374MB)에 남겼다.
- **연결:**
  - **GitHub:** `gh`가 juntegral 계정으로 로그인돼 있고, `gh auth setup-git`을 실행해 두었다.
  - **게임 서버 키:** `~/Downloads/api.txt`는 `unsw-swarm/docs/api.txt`(팀 1119 키)를 가리키는 링크다. 예: `node tools/online.js team`.
  - **디스코드 #meow:** unsw-swarm에서 `python3 tools/discord_sync.py`를 실행하면 새 메시지를 받아 온다.
    - 기록 파일은 `data/discord/900000000000000004.md`다.
    - `--wait N`을 주면 새 메시지가 올 때까지 기다린다.
    - 토큰은 `docs/discord.txt`에 있고, 도구만 읽는다.
- **Orca:** 이 세션은 Orca 터미널에서 돈다.
  - CLI는 `/Applications/Orca.app/Contents/Resources/bin/orca`를 쓴다. `/usr/local/bin/orca` 링크는 root 전용이라 실행되지 않는다.
  - `agent-context --json`으로 명령 스키마를 볼 수 있다.

## 현재 상태
- 새 코드 작업은 아직 시작하지 않았다. `battlecode/work`에 실행기 환경도 없다.
- **엔진 버전:** 서버 엔진은 1.2.7이다(PyPI 공개 10-02). README는 아직 1.2.3 기준이다. 1.2.4~1.2.7에서 바뀐 점은 확인하지 않았다.
- **래더:** 래더에는 v61이 올라가 있다. 업로드는 팀과 합의한 뒤에만 한다.
- **QWQ의 10-02 23:28 글:** 봇의 주요 문제 7개를 정리했고, 전문은 디스코드 기록에 있다.
  1. 큰 지도에서 여왕을 지키지 못함
  2. 지형 함정
  3. 후반 먹이기가 약함
  4. 복도형 지도에서 집을 떠나지 못함
  5. 작은 지도의 초반 사고사
  6. 로컬 시험이 래더와 다름
  7. 계산량 여유가 적음
- **퀄리파이어:** 제출 마감은 10-09 15:00 KST다. 전부 처음 보는 지도이고, 7판 4선승 단판 토너먼트다.

## 대기 중
- **디스코드 수신 시험:** 사용자가 #meow에 메시지를 올리면 sync로 받아지는지 확인한다.
- **`unsw-arena` 폴더 삭제:** 사용자가 이전 세션을 닫은 뒤 직접 지운다.

## 다음 작업 후보 (사용자 지시 전에는 시작하지 않는다)
1. 실행기 1.2.7 환경을 만들고, 1.2.4~1.2.7의 변경점을 확인한다.
2. C-- 코드를 점검한다. 1.2.3 이후의 몸 전이(BODYX 같은 버그)와 여왕 안전을 본다. QWQ의 문제 1, 5와 겹친다.
3. v1.8(`unsw-swarm/versions/v1.8`)에서 옮길 후보를 C-- 구조에 맞는지 판면으로 확인한다.
   - BODYX, BODYMEM2, Q2BOX
   - 여왕 번호 탐지
   - Q1 여왕 먹이기
4. 평가를 보완한다. 첫 갈림 인과 점검(`unsw-swarm/tools/firstdiv.js`)과 래더 기보의 사망 전수 조사를 쓴다. QWQ의 문제 6에 해당한다.
5. 팀과 디스코드에서 역할을 나눈다.

## 지킬 것
- 사용자에게는 한국어로 보고한다.
- 키와 토큰은 도구만 읽고, 화면과 로그에 출력하지 않는다.
- Claude 사용량을 아낀다. 넓은 작업은 Codex에 맡기고, Claude는 판정한다.
- 팀 레포에서는 팀 규칙을 따른다.
  - 새 동작은 기본으로 꺼진 토글 뒤에 넣는다.
  - 봇 코드에 주석을 달지 않고, 지도별 하드코딩을 하지 않는다.
  - 커밋 메시지는 영어로 쓴다.
- 팀 레포 push와 서버 업로드는 사용자와 합의한 뒤에 한다.
