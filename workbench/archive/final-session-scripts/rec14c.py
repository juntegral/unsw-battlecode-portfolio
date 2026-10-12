"""Record the Codex restart and the plan until the deadline."""
import time
R = '~/01. Project/개인 프로젝트/unsw-swarm/'
t = time.strftime('%H:%M')
open(R + 'docs/SESSION-STATE.md', 'a').write(f'''- 10:46 **PR #61 병합됨**(jun). 팀 main = 솔로 소스(전부 꺼짐) + 프로필 one14. 순위 34위 2134(one14 첫 랭크전: Check Raise 3-2, kraken 3-2, Sponge 2-3 +25).
- **{t} Codex 재개**(jun이 리셋권 사용 → 실제로 풀린 건 둘째 계정 juntegral `~/.codex`; 첫 계정은 여전히 한도라 `.limit-until`을 5시간 뒤로 다시 써 둠). 띄운 것: ① sol `regress`(온라인 묶음 전체, 지도 × 버전 지표표로 조용한 퇴행 찾기; `data/codex/astra/regress/report.md`) ② Astra 빌더 `seen`(THREAT_SEEN_SIZE: 위협 크기를 보이는 마디가 아니라 기억한 크기로; `data/codex/build/seen/`) ③ Astra 빌더 `qsnear`(QS_HEAD_CLEAR 4: 적 머리가 가까우면 퀸이 분열 안 함 + 붙은 머리에서 떨어짐; `data/codex/build/qsnear/`) ④ `tools/sweep_loop.sh`(세대별 판 분석) 다시 켬. 빌더 기준 소스 = `src/solo/main.cpp`, 스위치 = tmp `one14.switches`.
- **마감까지 규칙**: 새 스위치는 (a) 끈 해시 = 92fb69564fbd (b) 로컬 맞대결 gx 48판 + 포털 지도 2개에서 one14(mNps)보다 나쁘지 않음 (c) 온라인 45판에서 지도별 r100 진주·퀸 사망이 one14보다 나쁘지 않음, 셋 다 13:30까지 채울 때만 라이브. 아니면 one14 유지. 14:30 활성 id 최종 확인. 지도별 버전 비교를 안 한 게 one12~13의 실수였음.
''')
print(t)
