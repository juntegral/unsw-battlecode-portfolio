# submit.js 업로드 검증 수정

작성 시각: 2026-10-05 21:02:40 KST (`date` 확인).

## 원인

외부 경로 자체가 아니라 **`.gitignore`를 다르게 취급한 두 비교식**이 원인이다. 실제 `~/meow-release/mybot2`에는 `.gitignore`와 `bot.toml`, `main.cpp`, `helper.hpp`, `sonar_codec.hpp`가 있다. 폴더 자체는 심볼릭 링크가 아니며, resolve한 경로도 같다.

수정 전 `tools/submit.js`의 근거:

- 45–54행 `files()`는 `.unswbc-build`, `build`, `.DS_Store`, `__pycache__`, `__MACOSX`만 제외한다. 따라서 `.gitignore`도 해시 목록에 들어간다.
- 95행 업로드 검증은 `Object.entries(want).every(([f, h]) => got[f] === h)`였다. 공식 ZIP에 없는 `.gitignore` 때문에 항상 false가 된다. 서버에만 있는 추가 파일은 검사하지 않는 문제도 있었다.
- 110행 `check`는 양쪽 파일명 합집합에서 `!path.basename(f).startsWith('.') && want[f] !== got[f]`만 차이로 센다. `.gitignore`는 제외되므로 같은 ZIP을 identical로 판정한다.

실제 `bot.toml`의 include는 `*.cpp`, `*.hpp`, `*.cc`, `*.hh`, `*.c`, `*.h`다. `.gitignore`는 업로드 대상이 아니다.

ZIP 생성은 이 JS가 아니라 설치된 공식 엔진에 맡긴다(`tools/submit.js` 현재 104행). `../battlecode/work/bc127/lib/python3.13/site-packages/unswbc/submit.py` 18–25행 `_zip()`은 `bot.toml`을 명시적으로 같은 이름으로 넣고, 각 source를 `archive.write(project.path / source, source)`로 넣는다. `project.py` 80–88행 `collect_sources()`는 `entry.relative_to(self.path)`로 source 이름을 만든다. 저장소 기준 상대 경로를 ZIP 항목 이름으로 쓰지 않는다. 화면에 보인 `../../../meow-release/mybot2`는 JS의 출력·로그용 `path.relative(ROOT, dir)`다.

따라서 오늘 두 업로드가 **외부 폴더라는 이유로** 동일한 네 파일을 가진 내부 폴더와 다른 소스나 `../` 항목을 포함할 수는 없다. ZIP의 타임스탬프 등 메타데이터와 압축 바이트는 달라질 수 있지만 파일 이름과 내용은 같다. 현재 설치된 공식 생성 함수로 내부·외부 임시 폴더의 항목과 내용을 같게 만드는 테스트가 통과했다. 실제 외부 폴더의 ZIP도 아래 네 항목만 담는다. 당시 두 서버 ZIP 자체는 다시 다운로드하지 않았으므로 역사적 원본까지 독립적으로 확정하지는 않았다.

## 변경

- `tools/submit.js` 57–75행: `compareZip()`과 `serverDiff()`를 만들었다. `upload`(111행)와 `check`(122행)가 같은 다운로드·해시 비교를 사용한다. 기존 `check`처럼 숨김 basename과 기존 캐시 제외 규칙을 유지하며, 나머지 파일의 변경·누락·추가를 모두 검사한다.
- 실제 차이가 없으면 성공하고, 차이가 있으면 기존처럼 종료 코드 1이다. 업로드 검증은 차이가 난 파일명도 출력한다. 기존 업로드 실패·사용법·대전 진행 중 거부의 종료 코드는 유지했다.
- HTTP 오류나 ZIP 추출 실패는 검증 오류로 명확히 실패한다. 이를 `DOES NOT match`로 잘못 출력하지 않는다. 검증할 수 없는 다운로드를 성공으로 처리하지 않는다. 임시 폴더는 `finally`에서 정리한다.
- 143–151행: 직접 실행할 때만 CLI를 시작하고 비교 함수를 export해, 테스트가 API 키나 서버를 사용하지 않고 함수를 호출할 수 있게 했다.
- `tools/test_submit_verify.py`: 오프라인 회귀 테스트 7개 추가.
- `tools/test_smoke.py`: 작업 중 별도로 변경된 `smoke.py`의 `subs.js list` 호출에 대해 기존 모의 응답을 두 줄 추가했다. 첫 전체 실행의 31개 실패는 모의 응답이 이 새 호출을 처리하지 못한 결과였다. `smoke.py`와 `pair_report.py`의 다른 변경은 이 작업에서 수정하지 않았다.

## 실행 결과

`node --check tools/submit.js`: 종료 코드 0, 출력 없음.

`tools/`에서 `python3 -m unittest -v test_submit_verify.py`:

```text
Ran 7 tests in 0.957s
OK
```

내부·외부 경로, 공백·한글 폴더명, `..` 상대 경로, 폴더 심볼릭 링크, 숨김 파일, 기존 캐시 제외, 중첩 파일, 내용 변경·파일 누락·서버 추가 파일, 잘못된 ZIP을 검사했다. 설치된 공식 `Project.collect_sources()`와 `_zip()`도 직접 호출했다(테스트 생략 없음).

실제 `~/meow-release/mybot2`에서도 공식 `_zip()`만 호출해 ZIP을 만들고 공유 비교 함수를 실행했다. 네 소스의 내용이나 해시는 출력하지 않았다:

```text
official ZIP entries: ["bot.toml", "helper.hpp", "main.cpp", "sonar_codec.hpp"]
{"legacyMissing":[".gitignore"],"sharedDiff":[]}
```

`tools/`에서 요청한 명령 `python3 -m unittest discover -p 'test_*.py'`:

```text
Ran 107 tests in 1.136s
OK
```

기존 `pair_report.py`의 unclosed file ResourceWarning은 남지만 테스트 실패는 없다. `git diff --check`도 통과했다.

## 확인하지 않은 부분

네트워크를 사용하지 않았다. `upload`, `activate`, `active`, `check` CLI 명령은 실행하지 않았고, 금지된 비밀 파일을 읽거나 출력하지 않았으며 커밋하지 않았다. 실제 서버의 제출 17594·17678 ZIP, 수정 후 온라인 업로드·활성화·다운로드, HTTP 오류 분기 자체는 서버를 통해 확인하지 않았다. 활성 제출을 이름으로 찾는 기존 절차는 유지했다. 같은 이름의 동시 제출이나 업로드 중 로컬 파일 변경의 일반적인 경쟁 가능성은 남지만, 이번 `.gitignore` 오판은 현재 실제 폴더로 서버 없이 재현·해결했다.
