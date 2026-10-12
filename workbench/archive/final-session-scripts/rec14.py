"""Record one14 in the session memo, the shared card list and the promise ledger."""
import time
R = '~/01. Project/개인 프로젝트/unsw-swarm/'
t = time.strftime('%H:%M')
open(R + 'docs/SESSION-STATE.md', 'a').write(f'''- 10:21 one13-q1(대 Quaker Qubits 15판): 7/15(108 대 92).
- **10:24 one14(제출 21497) 라이브 = one13에서 `PORTAL_SCOUT_MIN_LEN` 4 → 0 하나만.** 동결 뒤 변경이지만 "망가진 것"에 해당: weak13-opus의 중간 보고(Quaker Qubits 1-4 분석) → 내가 라벨 캐시로 따로 재계산해 확인. r100 우리 진주(지도별 온라인 3~4판 평균) one11 → one12 → one13: Portals 238 → 76 → 71, Trauma 41 → 8 → 4, Queen Of Spades 59 → 11 → 30, Australia 92 → 49 → 36, Default 58 → 22 → 32, Trophy 112 → 70 → 66; 긴 포털이 없는 지도(Maze, Slithery Fight, weakhold, Tower Defense)는 그대로. 원인: 짧은 용이 "아무도 건너편을 못 본 포털"을 피하는데, 아무도 안 건너니 영원히 못 봄 + 퀸도 금지 + 비퀸은 4에서 분열 → 팀 전체가 포털 없는 쪽에 갇힘. 로컬 맞대결에서는 안 보였음(mNps 대 one13 21-2-21; gx 지도엔 이런 포털이 적음). 봇 = 로컬 팔 `mNps`, 폴더 `data/online/smoke/one14-bot/`, one13과 소스 차이 1줄.
- 10:25 공지 `px-live-one14.txt` 게시 확인(디코에서 읽음). 대기열 one14-c1/p1/k1 시작. **PR #61에 둘째 커밋 2152c3f**(프로필 44줄, 헤더 one14; 프로필 적용 소스 = one14-bot diff 0줄), PR 제목·본문 one14로 수정.
- {t} 순위 42위 2101(one13의 마지막 랭크전: Team SKKU 1-4 −19, WeLikCoding 2-3 −6, Quaker Qubits 1-4 −33). 활성 21497 확인. 감시 둘 다시 띄움. weak13-opus는 나머지 네 판 분석 중.
- 남은 일: one14 세 묶음에서 여섯 포털 지도의 r100 진주가 one11 수준으로 돌아왔는지 확인(P72) → 안 돌아왔으면 원인 다시. 15:00 전 활성 id 재확인. P69, P70 마무리 글.
''')
p = R + 'data/codex/astra/CARDS.md'
s = open(p).read()
a = '## Live (one13, submission 21377, since 08:07 KST) = one12 with QS_KEEP_MIN_UNITS 2 instead of 6'
assert a in s
s = s.replace(a, '## Live (one14, submission 21497, since 10:24 KST) = one13 with PORTAL_SCOUT_MIN_LEN 0\n'
 '(PORTAL_SCOUT_MIN_LEN 4 kept the whole side out of unseen portals: our pearls by r100 on Portals fell 238 to 71, Trauma 41 to 4,\n'
 'Australia 92 to 36. Dropped. Read every mention of it below as OFF.)\n'
 '## Before that: one13 (submission 21377, 08:07 to 10:24 KST) = one12 with QS_KEEP_MIN_UNITS 2 instead of 6')
open(p, 'w').write(s)
open(R + 'docs/PROMISES.md', 'a').write('| P72 | 10-09 10:25 | meowbot notice (px-live-one14.txt): one14 plays the same three opponents and the pearls by r100 on the six portal maps should be back at one11\'s level; post whether they are | open |\n')
print(t)
