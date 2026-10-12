# Q1 백업 집결·적 여왕 목격 분석 절차

사전 기준은 `versions/v1.8/VERSION.md`의 Q1c BUILD 절이다. BUILD에서는 새 대전 0판이다. 아래는 조정자가 판을 실행한 뒤의 절차다. 모든 명령은 저장소 루트에서 실행한다.

## 1. 실행·누락·오류·CPU

```sh
node exp/q1c/runq.js exp/q1c/spec.json --jobs 3 --cap 6
UNSW_RULES=123 node exp/q1c/analyze.js > exp/q1c/analysis.txt
```

명세는 runq14 형식이고 `name`은 설명이다. 기존 `exp/v14/runq14.js`는 상대에 무조건 `bots/`를 붙이고 CPU 옵션을 읽지 않는다. 제공한 runner는 Q1 runner 사본으로 경로 상대·CPU를 지원한다. nice 10, 기계 전체 6판, 디스크 21GiB, 재개 규칙을 유지한다. 게임은 샌드박스 밖에서 실행한다. `spec.json`은 다음 196판이다.

| 묶음 | 판 수 | 구성 |
|---|---:|---|
| off / b / c / on | 각각44, 총176 | 11지도 × 양편 × king/hunter × 시드1 |
| id-off / id-base | 각각6, 총12 | 온라인 Trophy·스프린트 Around UNSW·생성 M_07 × 양편 × king |
| self | 8 | both 대 v1.8, big_empty·stronghold·M_07·L_03 × 양편 |

11지도는 번들5, Trauma, Australia, gen_M_07, gen_L_03, trauma_flip, australia_flip이다. `maps-flip`을 실제 경로로 사용한다. flip은 원 지도의 반대편과 거울이므로 독립 표본으로 합산하지 않고 여왕 id 확인용으로 별도 표를 낸다. 전체22지도·전 생성지도·시드2는 이번 cap 밖이다.

`analysis.json`은 exit0/G 있음/error·botProblem 없음인 키별 마지막 clean 줄을 읽는다. 오류 이력을 지우지 않는다. `missing=0`, 합계196판, identity6키가 있어야 완료다. 재구성 `checks`의 모든 항은0이어야 한다. CPU는 각 게임 `cpu`의 우리 team max를 모아 최댓값·80M 경보 수·100M 초과 수를 보고한다. CPU 줄이 없으면 미검증이다. timeout/no reply/비정상 종료는 깨짐이며 재실행 성공으로 이력을 숨기지 않는다.

## 2. (b) 백업으로 모으기와 여왕 주변 안전

`pairs`에서 `off/b`를 읽는다. off는 현재 Q1b2 기본값이고 b는 Q1B_BACKUP만 켠다. `bothQueenAlive430`인 **공통 키**에서 backupDelta r350/400/430의 중앙값, 양수/0/음수 수와 원 길이를 보고한다. r400/r430 증가가 주 기준이다. 종료로 관측이 없는 checkpoint는 null로 남기고0으로 채우지 않는다. 한쪽만 r430에 여왕이 산 키도 별도 공개한다.

`sets.b.*.gather`의 `qbk<targetId>,<queenTile>`은 실제 computeGoal의 목표 id와 여왕 회피 타일이다. −1은 목표/여왕 소식 없음이다. r300–339는 소식만 설정하고 집결 이동은 아직 안 한다. 예비 자신은 목표 −1이고 스스로 먹는다. 알려진 최장과의 길이·소식 선택 및 진짜 여왕 id(초기 팀 최저 id)를 표식과 판면에서 확인한다. 여왕이 최장일 때 목표가 여왕일 수 있다. v1.7의 신선도·길이차2/최신 소식 규칙이므로 replay의 실제 최장과 봇의 관측 최장을 구분한다.

`crowd`는 r340–480 매10라운드 여왕 차례의 2칸 안 아군 머리 수다. r340–429와 r430–480을 나눠 중앙값·머리2개 이상 몫·같은 키별 증가를 보고한다. `traps`는 r300 뒤 여왕 trap/a 전수다. 합계뿐 아니라 새 trap 키/라운드를 확인한다. 모으기 변경이 처음 생긴 차례, 길이가 증가한 차례, crowd 증가, 모든 새 trap의 전후2라운드 판면을 읽는다. 약한 잎 벌점은 강제6칸 장벽이 아니므로 거리6 안 진입을 모두 구현 위반으로 판정하지 않는다.

```sh
UNSW_RULES=123 node exp/v16/q1/qmech.js exp/q1c/off exp/q1c/b --list --out exp/q1c/backup-mechanism.md
UNSW_RULES=123 node exp/w7/tunnelpic.js exp/q1c/b/games/proxy4_king_trauma_flip_A_1/game.replay exp/v16/q1/maps-flip/trauma_flip.map A X,Y 398,399,400,401,429,430,431 --r 6
```

X,Y는 원자료의 여왕 머리 좌표로 바꾼다. `tunnelpic`은 라운드 시작 상태다. 실제 해당 드래곤 차례 중 몸/적 사망 순서는 mass_ledger의 turn/action/death 훅으로 별도 확인한다.

## 3. Q1c 관문·ground truth 정확도

독립 효과는 off/c, 상호작용은 b/on이다. `feeds`는 네 RETURN 경로(conv/sf/FE/cv2)의 표식과 타겟·slack·당시 실제 여왕 생존을 담는다. `mergeViolations`는 **0**이어야 한다. 판면에서는 donor가 실제로 목으로 들어가 떨어진 진주와 먹은 드래곤을 `qmech.js`로 확인한다. 표식만으로 성공한 합치기라고 쓰지 않는다.

`qc<belief>,<directRound>,<heardRound>,<ownDirectBit>`는 매 차례 early RETURN 뒤에도 붙는다. qc 마지막 항은 자기 목격 신호이며, 실제 sonar bit는 relay가 아니고 발사된 경우만 같다. 합치기에 쓰는 belief는 직접 또는 수신 믿음의 OR다. 수신만 한 조각에서는 belief=1/ownDirectBit=0이 정상이다.

`analyze.js`는 ML rules123의 실제 적 여왕 생존, 각 프로세스의 torus7×7 몸 목격, 다음 차례에 실제 전달된 sonar를 독립 재구성한다. 모든 `errors`를 전수 조사한다. `beliefMetrics`의 correct/turns가 >50%인지, precision=TP/(TP+FP), recall=TP/(TP+FN)를 전체·지도·편·상대·r0–299/300–429/430+로 보고한다. `sightTurns`가 원자료다. `signalMetrics`는 발사 ray 단위로 같은 ground truth를 대조하며 동일 송신자의 네 ray를 독립 목격으로 세지 않는다. `(r,id)`로 중복 제거한 송신 차례 표도 낸다. false가 많은 전체 정확도만으로 목격 기제를 입증하지 말고 true/relay/adoption의 분모를 같이 보여 준다. 종료 뒤 빈 라운드는 분모에 넣지 않는다.

적 여왕의 몸도 생존 목격이다. 적 팀 id0/1을 실제 PartObs로 봤을 때만 직접 갱신하고 소나의 적 메시지는 버린다. 사망 뒤 직접목격의 최대50라운드·수신의 최대100라운드 오차 창은 FP로 그대로 센다. 적 여왕 사망 뒤 여왕 feed가 있으면 해당 증거 나이와 판면을 보여 주며 관문위반(belief=false)과 stale=true를 구분한다. 우리 여왕 사망 뒤 최장 보존은 원 길이·먹이 대상·판면을 off와 비교하고 승패 숫자는 쓰지 않는다.

## 4. 소나 1비트·전파·감쇠

format2에서 whiten XOR 후 checksum byte의 bit7이 새 신호다. id/rnd/x/y/len/hx/hy/team/magic의 기존 비트는 모두 유지된다. new checksum7=(old checksum8 XOR 0x40)&127이다. 구 checksum8와 하위7비트가 다르므로 구 직접 메시지는 신호로 오독하지 않고 여전히 읽는다. 왕relay는 기존 메시지를 그대로 쓰고 bit를 싣지 않는다. 메시지 보고 나이 검사는 기존 mod128/age<64/direct≤3/relay≤60을 유지한다. `decode` 구현은 제공 분석 JS에 있다.

`propagation`은 bit=true이고 메시지 보고 round가 기존 직접/수신 증거보다 엄격히 새로워 실제 채택할 기회다. sender→hitId가 실제 같은 팀이고, 다음 receiver 차례까지 `delay<=N=1`, `set=true`여야 한다. 더 신선한 자기 목격 때문에 갱신할 필요가 없는 메시지는 분모에서 제외하고 수를 별도 낸다. 수신·표식 누락/신선도 위반은 `errors`에 남는다. 전파 기회0이면 통과 대신 미확인이다. self 묶음에서 true 목격·실제 전달·채택·늦은 feed가 각각 있는지 확인한다.

프로세스마다 마지막 직접 seen·채택 heard를 따라가기 때문에 stale/same-round/false/relay가 증거를 갱신하는지, 각 증거 age>50에서 belief=false인지 전 차례 검사된다. 수신만 가진 프로세스의 새 direct packet bit는0이어야 한다. 별도 송신 조각의 직접목격이 끊긴 뒤에도 보내던 true가 마지막 목격+50까지만 지속하는지 확인한다. 이로써 수신 믿음끼리 재전송해 영원히 유지되는 메아리가 없는지 점검한다. 새로운 true 직접 목격이 계속 있으면 믿음이 계속되는 것은 정상이다. 송신 진실 표는 sender 차례 시작의 ground truth와 대조하므로 그 행동 도중 적 여왕을 죽인 경우에는 death 훅으로 송신 시점도 별도 확인한다.

## 5. off 동일성·컴파일·인계

```sh
UNSW_RULES=123 node exp/v16/identity.js exp/q1c/id-off exp/q1c/id-base > exp/q1c/identity.txt
```

6/6 사건/소나 동일이며 analysis.identity도 전부same이어야 한다. 입력·현재v1.8이 빌드 이후 바뀌지 않았는지 먼저 `validate.py`로 확인한다. 바뀌었으면 coordinator가 id-base와 self의 상대를 작업 시작 스냅샷 bot-base로 바꾼 사실을 적고, 그대로 다른 기준과 섞지 않는다. c-on은 r0부터 소나/표식이 달라져 전체 사건 r300전 동일성을 요구할 수 없다. first physical action difference를 볼 때 소나·표식 제외임을 명시하며 초기 정보 공유로 인한 후속 행동 차이도 숨기지 않는다.

BUILD의 `build.py`는 공식 judge clang 컴파일만, `check-fixtures.py`는 합성 C++ 함수 검사만 수행한다. `compile-check.json`에서 base/off WASM 바이트 동일, fixtures에서 양편 id·direct/legacy message 필드·나이wrap·한단계 공유·freshness·목표r430 경계를 확인한다. 실판 CPU·사건·목격정확도·함정은 실행 전 미검증이다.

판정은 b와 c를 따로 쓴다. `RESULT.md`에 발동 → 질량/신호 전파 → 실제 판면 → ground truth → 안전/동일성/CPU → 부족한 표본 순서로 원자료 링크를 남긴다. Q1B/Q1C를 켤지는 조정자가 결정한다. 커밋·네트워크·게임 추가는 이 BUILD/분석 인계에 포함하지 않는다.
