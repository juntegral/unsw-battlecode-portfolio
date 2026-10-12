# 측정 정의와 한계

- 입력은 실행 시작 시 발견된 top1/* 및 팀 1119가 참가한 dl-*와 smoke/*의 game JSON / M replay 쌍이다. game id로 중복 제거한다. 수집 중 불완전하거나 바뀐 파일은 errors.json에 남기고 다음 실행에서 재시도한다. 네트워크를 사용하지 않는다.
- 수치는 실제 온라인 기보의 관측이다. 팀 버전·상대·지도·시간 분포를 통제한 인과 비교가 아니다. top1 표본에는 비랭크 경기도 포함되며, 우리 비교에는 요청대로 smoke 경기도 포함된다. 우리 래더만의 결과도 별도 요약한다.
- 버킷 r25는 r0–24 이벤트와 r25 시작 상태, 이후는 이전 경계 이상 / 현재 경계 미만이다. end는 마지막 경계부터 종료까지다. 정확히 경계에서 끝나면 end가 마지막 버킷을 복제한다. 종료 후 경계는 생성하지 않는다. 따라서 뒤 버킷은 생존 게임으로 조건화되며 end의 구간 길이는 게임마다 다르다. bucket_rounds를 함께 제공한다.
- 상태는 map의 DRAGON 순서와 매 단계 dragonUpdate head/tail, split 전체 몸, death에서 복원한다. 최종 units/total/longest와 모든 split 질량을 기보 기록과 대조하고 불일치 게임은 제외한다. 유료 질주의 길이 감소는 기록된 tail을 따르므로 ceil(L/4) 공짜 걸음을 별도 비용으로 잘못 빼지 않는다.
- cells_visited는 시작·분열 직후·이동 단계의 머리 칸 합집합이다. 시야나 지식 영역이 아니다. 모든 거리는 토러스 맨해튼 거리이며 장애물·포털 최단거리를 뜻하지 않는다.
- pearls_natural/corpse는 tileChange 제거로 센다. 사망 직후 연속 pearl 추가는 corpse, 나머지 추가는 natural로 분류한다. 기존 ledger와 같은 이벤트 순서 규약이다. 출처 없는 제거는 unknown이다. length_gained는 단계별 양의 길이 변화만으로, 유료 걸음에서 먹고 길이가 유지된 경우를 놓치므로 보조 지표다.
- splits 길이 클래스는 분열 직전 부모 길이, deaths는 죽기 직전 길이, headon_initiated는 충돌 직전 공격자 길이, sprints는 요청 시 길이다. 클래스는 le4 / 5_9 / 10plus. 사망 cause는 원본 enum 0–4를 wall/self/body/headon/other로 매핑한다. other에는 자살·무효 행동 등이 포함되며, suicides는 명시적 suicide 행동만 센다.
- feeding_near_longest는 자살 시점 팀 최장(동률 최소 id)이 다른 용이며 6칸 이내인 경우다. 실제 먹이 전달 성공 또는 의도를 증명하지 않는다. 자기 자신을 먹이 대상에 포함하지 않는다.
- headon_initiated는 현재 행동 주체와 다른 팀의 머리 사망 이벤트에서 행동당 한 번 센다. 아군끼리 충돌은 제외한다. sprints/mean_steps는 2걸음 이상 요청 수와 요청 걸음 평균이며, 죽어서 실행 못 한 후속 걸음도 포함한다. 0회 버킷의 평균은 NA다.
- portal_crossings는 실제 dragonUpdate가 있는 이동 단계의 출발 EDGE가 portal인 횟수다. 실패한 충돌 시도의 포털 사용은 제외한다. sonar_messages는 sonarPing 이벤트(방향별 ping) 수이며 sonar_nonzero_messages는 payload가 0이 아닌 ping 수다. 논리적 방송 수·수신 성공·내용 해석은 측정하지 않는다.
- queen은 팀 A/B를 가정하지 않고 DRAGON 순서 id 0/1의 진영으로 정한다. 사망 시 alive=0/length=0, 거리·주변 동료 수는 NA다. 적이 없으면 nearest_enemy_distance는 NA다.
- 종료 원인은 replay의 wipe-out 플래그를 우선하고, 라운드 소진이면 여왕 길이→최장→총 길이 규칙으로 추론해 recorded winner와 검증한다. 종료 세부 동점 규칙은 기보에 명시된 필드가 아니므로 추론이다. terminated 비트는 원문 그대로 보존하며 강제 중단으로 해석하지 않는다(정상 종료 기보도 true). 알 수 없는 종료 enum이나 승자 모순은 unknown이다.
- 팀 순위는 각 팀의 completedAt 기준 가장 최신 top1 game JSON의 ELO(동률 game id)를 취해 내림차순이다. 수집 시각은 없을 때만 대체한다. 현재 서버 실시간 순위가 아니다. 표본 20판 이상 팀을 top 팀 요약에 포함한다.
- 요약은 게임별 각 버킷 지표의 중앙값이며 빈 값은 제외한다. 표마다 N과 각 지표 유효 n을 표시한다. gap의 ratio=rank1/comparator; 둘 다 0이면 1, 비교군만 0이면 ∞, 한쪽 NA면 NA. 상대 격차=max(ratio,1/ratio)-1 (둘 중 하나만 0이면 ∞), 방향은 ratio로 읽는다. 공통점/특이점은 비교용이지 유의성 판정이 아니다.
- notable은 각 지도 크기×상대×승/패에서 큰 격차 게임을 먼저 뽑아 다양성을 확보한다. 승리 크기는 결정 지표 차이(전멸은 최종 총 길이 차이) / max(1, 양팀 지표 합)이다. 서로 다른 종료 유형의 격차를 절대 실력 차이로 읽지 않는다.
