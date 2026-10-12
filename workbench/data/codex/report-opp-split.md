# 상대별 온라인 결과 분리

검증 시각: 2026-10-05 20:15:12 KST.

`tools/pair_report.py`는 기존 요약 뒤에 상대별 승수와 양 팀 평균 점수를 추가한다. 실행 상태의 상대 순서를 따르고, 순서가 없으면 이름순이다. 전체와 같은 지도별 pooled live 평균을 사용하며, 기준선 없는 키는 제외한다. 기존 기준선 없음 안내와 이번 실행만의 비교, 파일명, 지도별 표, 종료 동작은 유지했다.

Discord 문구는 복수 상대일 때 상대별 승수를 넣는다. 상대별 공유 키의 라이브 게임이 30판 미만이면 해당 상대에, 전체가 45판 미만이면 첫 문장에 `thin baseline` 안내를 넣는다. 1,900자 이상이면 뒤쪽 상대부터 통째로 빼고 `…`를 붙인다. 문구 생성 함수는 전송 없이 호출할 수 있다.

`tools/test_pair_report.py`에 9개 오프라인 테스트를 추가했다. `load`, `baseline`, `subprocess.run`은 모의 처리했다. 두 상대, 단일 상대, 상태 순서와 이름순, 기준선 없는 상대, 공유 키에 한정한 얇은 기준선, 키별 평균 가중치, 기존 이번 실행 비교, 게시 없는 실행, 긴 문구를 확인한다. 수정 파일은 임시 파일에서 컴파일 확인한 뒤 `os.replace`로 교체했다. 저장소 지침에 따라 결과를 `DECISIONS.md`에도 기록했다.

## 실제 출력

네트워크와 외부 프로세스 실행, 두 비밀 파일 접근을 차단하는 임시 Python 시작 가드를 사용했다. 두 명령 모두 `--post` 없이 저장된 게임 파일만 읽어 완료됐다. 스크립트의 기존 동작대로 `<label>-result.txt`는 기록된다. 변경 전 코드와 대조하여 추가된 `vs` 행을 제외한 출력 전체가 동일함을 확인했다.

### `python3 tools/pair_report.py qh31d-test` — 앞 8줄

```text
new bot 30 games | wins: new 10/30 vs live 4.0/30 (live baseline pooled over 30 games: 4/30)
our avg score 54.3 -> 65.1 | their avg score 167.8 -> 166.8
games where we scored 0: 9.0 -> 6
vs test4: wins new 8/15 vs live 0.0/15 | our avg score 42.9 -> 80.1 | their avg score 190.1 -> 182.5
vs WeHaveQuizzes: wins new 2/15 vs live 4.0/15 | our avg score 65.6 -> 50.1 | their avg score 145.5 -> 151.1
  Around UNSW        wins  0.0->1 | ours  270.0-> 472 | theirs  907.0-> 799
  Australia          wins  0.0->0 | ours  212.0->  59 | theirs  668.0-> 850
  Default            wins  1.0->0 | ours  181.0->  86 | theirs  210.0-> 242
```

보냈을 Discord 문구(문자열만 생성, 전송하지 않음):

```text
📊 qh31d-test online result (same teams + maps): wins: new 10/30 vs live 4.0/30 (live baseline pooled over 30 games: 4/30) (thin baseline: 30 live games). our avg score 54.3 -> 65.1 | their avg score 167.8 -> 166.8. by opponent: test4 8/15 (live 0.0) (thin baseline: 15 live games), WeHaveQuizzes 2/15 (live 4.0) (thin baseline: 15 live games). about ±4 wins in 30 games is luck
```

### `python3 tools/pair_report.py qd36-test` — 앞 8줄

```text
new bot 30 games | wins: new 4/30 vs live 4.0/30 (live baseline pooled over 30 games: 4/30)
our avg score 54.3 -> 67.5 | their avg score 167.8 -> 166.9
games where we scored 0: 9.0 -> 8
vs test4: wins new 3/15 vs live 0.0/15 | our avg score 42.9 -> 56.7 | their avg score 190.1 -> 189.7
vs WeHaveQuizzes: wins new 1/15 vs live 4.0/15 | our avg score 65.6 -> 78.3 | their avg score 145.5 -> 144.0
  Around UNSW        wins  0.0->0 | ours  270.0-> 498 | theirs  907.0-> 712
  Australia          wins  0.0->0 | ours  212.0-> 119 | theirs  668.0-> 763
  Default            wins  1.0->1 | ours  181.0-> 136 | theirs  210.0->  98
```

보냈을 Discord 문구(문자열만 생성, 전송하지 않음):

```text
📊 qd36-test online result (same teams + maps): wins: new 4/30 vs live 4.0/30 (live baseline pooled over 30 games: 4/30) (thin baseline: 30 live games). our avg score 54.3 -> 67.5 | their avg score 167.8 -> 166.9. by opponent: test4 3/15 (live 0.0) (thin baseline: 15 live games), WeHaveQuizzes 1/15 (live 4.0) (thin baseline: 15 live games). about ±4 wins in 30 games is luck
```

## 전체 테스트

`tools/`에서 `python3 -m unittest discover -p 'test_*.py'` 실행. 마지막 4줄:

```text
----------------------------------------------------------------------
Ran 99 tests in 0.193s

OK
```

`git diff --check` 통과. 네트워크, Discord 게시, 비밀 파일 읽기, 기존 프로세스 시작·종료·재시작, 커밋은 하지 않았다. 기존 `docs/PROMISES.md` 수정은 건드리지 않았다.

## 해석과 한계

단일 상대 판정은 새 게임 행에 등장한 상대 수로 한다. 일부 키에만 기준선이 있으면 그 키만 분리에 포함하고, 나머지 키의 기존 기준선 없음 안내는 그대로 남긴다.

상대를 전부 제외해도 카드 이름이나 pooled 실행 목록 자체가 너무 길면, 닫는 문장을 보존하고 앞부분을 말줄임하여 1,900자 미만을 보장한다. 일반적인 길이에서는 기존 첫 문장을 유지하며 얇은 기준선 안내만 덧붙인다. 이는 비정상적으로 긴 첫 문장과 길이 상한이 충돌할 때의 해석이다.

기존 코드의 파일 핸들 사용에서 `ResourceWarning`이 나타나지만 99개 테스트는 모두 통과했다. 이번 범위에서는 기존 파일 I/O를 변경하지 않았다.
