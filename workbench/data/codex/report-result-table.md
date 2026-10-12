# 결과 메시지 표 변경

`tools/pair_report.py`의 Discord 메시지만 공백 정렬 코드 블록 표로 변경했다. 상대 이름은 18자로 제한하고, 단일 상대는 합계 행을 생략한다. 기준선이 없는 상대는 `-`로 표시하며, 얇은 기준선 안내와 1,900자 미만 제한을 적용했다. 기존 콘솔 출력·결과 파일·상대별 및 지도별 텍스트는 유지했다. 파일은 임시 파일에서 원자적으로 교체했다. 커밋과 네트워크 호출은 하지 않았다.

`tools/test_pair_report.py`에서 정렬, 단일 상대, 기준선 없음, 안내 문구, 이름 제한, 메시지 길이를 검증했다. 전체 100개 테스트가 통과했다. 샘플은 `--post` 없이 디스크의 기보로 계산했고 외부 명령 실행을 차단했다.

~~~~text
📊 #31 queen-hunt (on new main) online result, same teams + maps
```
opponent       wins new  wins live  our score    their score
all            10/30     4.0/30     54.3 → 65.1  167.8 → 166.8
test4          8/15      0.0/15     42.9 → 80.1  190.1 → 182.5
WeHaveQuizzes  2/15      4.0/15     65.6 → 50.1  145.5 → 151.1
```
live baseline 30 games (thin, under 45) · thin for test4, WeHaveQuizzes. about ±4 wins in 30 games is luck
~~~~

~~~~text
📊 #36 queen-dead-end online result, same teams + maps
```
opponent       wins new  wins live  our score    their score
all            4/30      4.0/30     54.3 → 67.5  167.8 → 166.9
test4          3/15      0.0/15     42.9 → 56.7  190.1 → 189.7
WeHaveQuizzes  1/15      4.0/15     65.6 → 78.3  145.5 → 144.0
```
live baseline 30 games (thin, under 45) · thin for test4, WeHaveQuizzes. about ±4 wins in 30 games is luck
~~~~

테스트 실행 마지막 4줄:

```text
----------------------------------------------------------------------
Ran 100 tests in 0.183s

OK
```
