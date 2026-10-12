기존 runner.py 부분 수정에 이어 task 카드 구현을 완료했습니다.
Task 양식과 전용 프롬프트를 추가하고, ready → building → tested 경로에서 불명확할 때만 질문하도록 했습니다.
최신 main 기준 구 10지도 × 2종자 × 양쪽의 40회 동일성 검사와 카드별 완료 검사를 독립 재실행합니다.
동일성 실패 시 ready로 돌아가 “this changes play; make it an idea card or fix it”을 기록합니다.
우선순위는 type:task > by:zhe > 다른 사람 > by:ai이며, 같은 그룹은 오래된 카드부터 처리합니다.
동일한 card/N → candidate → main 및 승인 흐름을 유지하고, 영문·중문 문서에 반영했습니다.
python3 -m unittest discover -s work/loop/tests: 43개 통과; git diff --check 통과.
커밋·푸시·실제 GitHub 호출은 하지 않았습니다. AI·게임·원격 작업은 모의 테스트로 검증했습니다.
