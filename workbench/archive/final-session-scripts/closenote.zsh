#!/bin/zsh
# Post the note that closes two open promises to Zhe, mark them in the ledger, record the final state.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
wc -c data/guide/px-zhe-close.txt
python3 tools/meowbot.py --announce-file data/guide/px-zhe-close.txt 2>&1 | tail -n 1 | cut -c1-100
python3 - <<'EOF'
import time, re
t = time.strftime('%H:%M')
p = 'docs/PROMISES.md'
s = open(p).read()
out = []
for line in s.split('\n'):
    if line.startswith('| P69 |') and line.rstrip().endswith('| open |'):
        line = line.rstrip()[:-len('| open |')] + '| done 10-09 %s KST: posted in px-zhe-close.txt (WAR_FEED_FIRST built, never tested: the revenge state never armed; cause found, the relay fix is not live) |' % t
    if line.startswith('| P70 |') and 'px-zhe-close' not in line:
        line = line.rstrip() + ' closed 10-09 %s KST in px-zhe-close.txt: a mate took her last free cell 2 times in 286 queen deaths (was 10 of 21). |' % t
    out.append(line)
open(p, 'w').write('\n'.join(out))
open('docs/SESSION-STATE.md', 'a').write('''- 13:34 **qaway-opus 2차(종료시킴): QUEEN_OUT_OF_REACH도 싣지 않음.** 겨냥한 Slithery 사례를 못 막음(r350 → r349 사망): 공격자(L5, 도달 5 = 무료 2 + 유료 3)를 간격 5에서야 처음 봄, 한 턴 전엔 간격 8로 시야 밖 → 한계는 걸음 규칙이 아니라 **시야**. Slithery 6쌍: 생존 2 → 3, 더 일찍 사망 3. 관찰(미추적): 먹인 퀸이 r344~346에 제자리에서 19 → 17 → 15 → 13으로 턴마다 2씩 줄어듦(어느 분기인지 미확인; 열린 문제). 소스 `src/w-qaway/main-on-current-base.cpp`, 표 `data/codex/astra/qaway-opus/`.
- 13:34 로컬 맞대결 최종(상대 mD16, 중단): mHl3 11-0-8, mHl6 5-0-11, mSh1 8-0-10, mSh7 10-0-8 → 싣지 않음. 로컬 판 전부 정지.
- **%s 최종 상태: 라이브 one17(제출 21693). 이후로는 망가진 게 확인될 때만 손댐(되돌릴 곳: one16 = 21651, `node tools/submit.js activate 21651 --confirm --purpose ...`).** 순위 36위 2131. 대기열 one17-c1 → s1 → p1(LIVE_ID 21693). Zhe에게 P69·P70 마무리 글 게시(`px-zhe-close.txt`). 서브에이전트 전부 종료. 남은 일: one17 온라인 묶음에서 이상 여부(지도별 r100, 퀸 탈피), 14:30 활성 id 최종 확인, jun에게 최종 보고, PR #62 병합은 jun·Zhe.
''' % t)
print(t)
EOF
tail -n 2 data/discord/900000000000000004.md | cut -c1-120
